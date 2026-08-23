// /api/search-analytics.json：登录门禁 + fetchSearchStats 解析逻辑的单元测试。
// 这个端点刻意跟 /api/analytics.json 分开（见文件头注释：那个端点走共享边缘缓存，
// 把登录用户才能看到的数据塞进去会泄露给所有访客），所以这里要单独测两件事：
// (1) 没有合法登录 Cookie 一律 401，不发任何上游请求；(2) fetchSearchStats 本身
// 的成功/未配置/无数据/网络失败四种路径都按预期降级。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { COOKIE_NAME, signSession } from '../_lib/auth.js';
import { onRequestGet, fetchSearchStats } from './search-analytics.json.js';

const SESSION_SECRET = 'test-session-secret-do-not-use-in-prod';

async function validCookie() {
	return signSession(SESSION_SECRET, { issuedAt: Math.floor(Date.now() / 1000), maxAgeSeconds: 3600 });
}

function makeRequest({ cookie } = {}) {
	const headers = {};
	if (cookie) headers.Cookie = `${COOKIE_NAME}=${cookie}`;
	return new Request('https://example.com/api/search-analytics.json', { method: 'GET', headers });
}

function withFetch(impl, fn) {
	const original = globalThis.fetch;
	globalThis.fetch = impl;
	return fn().finally(() => {
		globalThis.fetch = original;
	});
}

test('没有登录 Cookie：401，不发任何 Analytics Engine 请求', async () => {
	let called = false;
	await withFetch(
		async () => {
			called = true;
			throw new Error('should not be called');
		},
		async () => {
			const env = { BLOG_SEARCH_SESSION_SECRET: SESSION_SECRET, CF_ANALYTICS_TOKEN: 'tok' };
			const resp = await onRequestGet({ request: makeRequest(), env });
			assert.equal(resp.status, 401);
			assert.equal(resp.headers.get('cache-control'), 'private, no-store', '未授权响应也不能被共享缓存缓存住');
		},
	);
	assert.equal(called, false);
});

test('过期/伪造 Cookie：同样 401', async () => {
	const env = { BLOG_SEARCH_SESSION_SECRET: SESSION_SECRET, CF_ANALYTICS_TOKEN: 'tok' };
	const resp = await onRequestGet({ request: makeRequest({ cookie: 'not-a-valid-cookie' }), env });
	assert.equal(resp.status, 401);
});

test('缺少 BLOG_SEARCH_SESSION_SECRET 绑定：503（fail-closed，不静默放行）', async () => {
	const env = {};
	const resp = await onRequestGet({ request: makeRequest(), env });
	assert.equal(resp.status, 503);
});

test('登录态合法时：200，返回值带 private, no-store 缓存头', async () => {
	await withFetch(
		async () => ({ ok: true, json: async () => ({ data: [{ searches: 1, unique_ips: 1 }] }) }),
		async () => {
			const cookie = await validCookie();
			const env = { BLOG_SEARCH_SESSION_SECRET: SESSION_SECRET, CF_ANALYTICS_TOKEN: 'tok' };
			const resp = await onRequestGet({ request: makeRequest({ cookie }), env });
			assert.equal(resp.status, 200);
			assert.equal(resp.headers.get('cache-control'), 'private, no-store');
		},
	);
});

// security round 2 review 建议：Analytics Engine 能读到的是登录用户的原始搜索词+IP，
// 比 CF_ANALYTICS_TOKEN 原本只读公开聚合 RUM 数据敏感得多，不该复用/扩权同一个 token——
// 支持一个可选的专用 token，配置了就优先用它，没配就退化到 CF_ANALYTICS_TOKEN。
test('onRequestGet: 配置了 CF_ANALYTICS_ENGINE_TOKEN 时优先用它，不用 CF_ANALYTICS_TOKEN', async () => {
	const recordedTokens = [];
	await withFetch(
		async (url, opts) => {
			recordedTokens.push(opts.headers.authorization);
			return { ok: true, json: async () => ({ data: [{ searches: 1, unique_ips: 1 }] }) };
		},
		async () => {
			const cookie = await validCookie();
			const env = {
				BLOG_SEARCH_SESSION_SECRET: SESSION_SECRET,
				CF_ANALYTICS_TOKEN: 'general-purpose-token',
				CF_ANALYTICS_ENGINE_TOKEN: 'narrowly-scoped-token',
			};
			await onRequestGet({ request: makeRequest({ cookie }), env });
			assert.ok(recordedTokens.every((h) => h === 'Bearer narrowly-scoped-token'), '应该只用专用 token，不掺 CF_ANALYTICS_TOKEN');
		},
	);
});

test('fetchSearchStats: 没有 token 时返回 not_configured，不发请求', async () => {
	let called = false;
	await withFetch(
		async () => {
			called = true;
			throw new Error('should not be called');
		},
		async () => {
			const result = await fetchSearchStats(undefined, 'acct');
			assert.deepEqual(result, { error: 'not_configured' });
		},
	);
	assert.equal(called, false);
});

test('fetchSearchStats: 三个 SQL 查询都成功时，解析出 totals/daily/topQueries', async () => {
	await withFetch(
		async (url, opts) => {
			const body = opts.body;
			if (body.includes('GROUP BY day')) {
				return { ok: true, json: async () => ({ data: [{ day: '2026-08-20', searches: 3, unique_ips: 2 }] }) };
			}
			if (body.includes('GROUP BY blob1')) {
				return { ok: true, json: async () => ({ data: [{ query: 'pagefind', cnt: 5 }] }) };
			}
			return { ok: true, json: async () => ({ data: [{ searches: 10, unique_ips: 4 }] }) };
		},
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.equal(result.totalSearches, 10);
			assert.equal(result.uniqueIps, 4);
			assert.deepEqual(result.daily, [{ date: '2026-08-20', searches: 3, uniqueIps: 2 }]);
			assert.deepEqual(result.topQueries, [{ query: 'pagefind', count: 5 }]);
		},
	);
});

test('fetchSearchStats: 数据集还不存在（404）时返回 no_data_yet，不是报错', async () => {
	await withFetch(
		async () => ({ ok: false, status: 404 }),
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.deepEqual(result, { error: 'no_data_yet', status: 404 });
		},
	);
});

test('fetchSearchStats: 权限不足（403）单独归类为 forbidden，不跟 no_data_yet 混在一起', async () => {
	await withFetch(
		async () => ({ ok: false, status: 403 }),
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.deepEqual(result, { error: 'forbidden', status: 403 });
		},
	);
});

test('fetchSearchStats: 其它未知 HTTP 错误（如 500）归类为 upstream_http', async () => {
	await withFetch(
		async () => ({ ok: false, status: 500 }),
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.deepEqual(result, { error: 'upstream_http', status: 500 });
		},
	);
});

// 回归测试（correctness round 1 review 抓到的真实 bug）：原来不管三个并发请求里
// 哪一个失败，报的都是第一个（totals）请求的状态码——totals 成功但 daily/top 失败时，
// 会拿着一个 200 却报 upstream_http，调试时完全看不出真正是哪个查询挂了。
test('fetchSearchStats: totals 成功但 daily 失败时，报的是 daily 自己的状态码，不是 totals 的 200', async () => {
	await withFetch(
		async (url, opts) => {
			if (opts.body.includes('GROUP BY day')) return { ok: false, status: 403 };
			return { ok: true, json: async () => ({ data: [{ searches: 1, unique_ips: 1 }] }) };
		},
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.deepEqual(result, { error: 'forbidden', status: 403 }, '应该报 daily 请求自己的 403，不是 totals 的 200');
		},
	);
});

test('fetchSearchStats: 网络异常时返回 fetch_failed，不抛出未捕获异常', async () => {
	await withFetch(
		async () => {
			throw new Error('network down');
		},
		async () => {
			const result = await fetchSearchStats('tok', 'acct');
			assert.equal(result.error, 'fetch_failed');
		},
	);
});
