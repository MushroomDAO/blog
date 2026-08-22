// T1.3.6 验收测试：/api/search-auth 端点。直接调用 onRequestPost，用一个内存 Map 模拟
// env.BLOG_SEARCH_KV，不需要 wrangler/Miniflare——Cloudflare Pages Functions 的 handler
// 就是普通的 (context) => Response 函数，可以直接在 Node 里当函数调。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { MAX_ATTEMPTS } from '../_lib/rate-limit.js';
import { onRequestGet, onRequestPost } from './search-auth.js';

function makeFakeKv() {
	const store = new Map();
	return {
		async get(key) {
			return store.has(key) ? store.get(key) : null;
		},
		async put(key, value) {
			store.set(key, value);
		},
	};
}

function makeEnv(overrides = {}) {
	return {
		BLOG_SEARCH_PASSWORD: 'correct-password',
		BLOG_SEARCH_SESSION_SECRET: 'test-secret',
		BLOG_SEARCH_KV: makeFakeKv(),
		...overrides,
	};
}

function makeRequest(body, { ip = '5.5.5.5' } = {}) {
	// 真实浏览器 fetch() 对字符串 body 会自动带上 Content-Length；Node 的 Request 不会
	// （已经手工验证过），这里显式设置，让测试请求形状跟生产环境的真实请求一致，
	// 不然 search-auth.js 里新加的 body 大小校验在测试里永远测不到
	const bodyText = JSON.stringify(body);
	return new Request('https://example.com/api/search-auth', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'CF-Connecting-IP': ip,
			'Content-Length': String(new TextEncoder().encode(bodyText).length),
		},
		body: bodyText,
	});
}

test('正确密码：200，Set-Cookie 里带 HttpOnly Secure SameSite=Lax', async () => {
	const env = makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ password: 'correct-password' }), env });
	assert.equal(resp.status, 200);
	const setCookie = resp.headers.get('Set-Cookie');
	assert.ok(setCookie, '应该有 Set-Cookie header');
	assert.match(setCookie, /HttpOnly/);
	assert.match(setCookie, /Secure/);
	assert.match(setCookie, /SameSite=Lax/);
});

test('错误密码：401，不设置 Cookie', async () => {
	const env = makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ password: 'wrong' }), env });
	assert.equal(resp.status, 401);
	assert.equal(resp.headers.get('Set-Cookie'), null);
});

test('缺少环境变量配置：503，不泄露具体缺了哪个变量', async () => {
	const env = makeEnv({ BLOG_SEARCH_PASSWORD: undefined });
	const resp = await onRequestPost({ request: makeRequest({ password: 'anything' }), env });
	assert.equal(resp.status, 503);
	const body = await resp.json();
	assert.doesNotMatch(JSON.stringify(body), /BLOG_SEARCH/);
});

test('请求体不是合法 JSON：400', async () => {
	const env = makeEnv();
	const badRequest = new Request('https://example.com/api/search-auth', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: 'not json{{{',
	});
	const resp = await onRequestPost({ request: badRequest, env });
	assert.equal(resp.status, 400);
});

test('密码字段本身超过 256 字符、但整个 body 仍在大小上限内：400（走密码长度检查，不是 body 大小检查）', async () => {
	const env = makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ password: 'x'.repeat(300) }), env });
	assert.equal(resp.status, 400);
});

test('回归测试：整个 body 超过 MAX_BODY_BYTES：413，在 request.json() 解析之前就拒绝', async () => {
	// 对抗式 review 抓到的真实 bug：原来只检查 password 字段自己的长度，一个塞了大量
	// 无关字段撑大 body 的请求会被完整解析完才发现"密码本身没超长"，白白吃掉解析开销。
	// 现在 Content-Length 一旦超限，根本不会走到 request.json()。
	const env = makeEnv();
	const resp = await onRequestPost({
		request: makeRequest({ password: 'correct-password', junkField: 'x'.repeat(10000) }),
		env,
	});
	assert.equal(resp.status, 413);
});

test('限速：同一 IP 连续超过 MAX_ATTEMPTS 次后返回 429，即使密码正确', async () => {
	const env = makeEnv();
	const ip = '7.7.7.7';
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		const resp = await onRequestPost({ request: makeRequest({ password: 'wrong' }, { ip }), env });
		assert.equal(resp.status, 401, `第 ${i + 1} 次应该是密码错误(401)，不是限速`);
	}
	const blocked = await onRequestPost({ request: makeRequest({ password: 'correct-password' }, { ip }), env });
	assert.equal(blocked.status, 429, '超过次数后即使密码正确也应该被限速拦住');
});

test('限速：不同 IP 不互相影响', async () => {
	const env = makeEnv();
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		await onRequestPost({ request: makeRequest({ password: 'wrong' }, { ip: '8.8.8.8' }) , env });
	}
	const otherIp = await onRequestPost({ request: makeRequest({ password: 'correct-password' }, { ip: '9.9.9.9' }), env });
	assert.equal(otherIp.status, 200);
});

test('没配 BLOG_SEARCH_KV 绑定：限速功能缺失，但密码校验仍然生效（不因配置问题锁死正常登录）', async () => {
	const env = makeEnv({ BLOG_SEARCH_KV: undefined });
	const resp = await onRequestPost({ request: makeRequest({ password: 'correct-password' }), env });
	assert.equal(resp.status, 200);
});

test('回归测试：缺 CF-Connecting-IP 的请求不会共享同一个限速桶、锁住别的调用方', async () => {
	// 对抗式 review 抓到的真实 bug：原来缺 header 时退化成字面量 "unknown"，
	// 5 个互不相关、缺 header 的失败请求会耗尽同一个桶，第 6 个即使密码正确的调用方
	// （同样缺 header）也会被 429——现在缺 header 时直接不参与限速，各自独立
	const env = makeEnv();
	const noIpRequest = (body) =>
		new Request('https://example.com/api/search-auth', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }, // 故意不带 CF-Connecting-IP
			body: JSON.stringify(body),
		});
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		const resp = await onRequestPost({ request: noIpRequest({ password: 'wrong' }), env });
		assert.equal(resp.status, 401);
	}
	const stillOk = await onRequestPost({ request: noIpRequest({ password: 'correct-password' }), env });
	assert.equal(stillOk.status, 200, '缺 IP 的正确密码请求不应该被之前缺 IP 的失败请求连累限速');
});

test('GET 请求：405', async () => {
	const resp = await onRequestGet();
	assert.equal(resp.status, 405);
});
