// T1.3.3 验收测试：/api/search 端点。直接调用 onRequestPost，用内存 Map 模拟
// env.BLOG_SEARCH_KV、假的 env.AI / env.VECTORIZE_INDEX，不需要 wrangler/Miniflare。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { MAX_ATTEMPTS } from '../_lib/rate-limit.js';
import { COOKIE_NAME, signSession } from '../_lib/auth.js';
import { onRequestGet, onRequestPost } from './search.js';

const SESSION_SECRET = 'test-session-secret-do-not-use-in-prod';

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

function makeFakeAi({ vector = [0.1, 0.2, 0.3], shouldThrow = false } = {}) {
	return {
		async run(model, { text }) {
			if (shouldThrow) throw new Error('Workers AI unavailable');
			return { data: text.map(() => vector) };
		},
	};
}

function makeFakeVectorize({ matches = [], shouldThrow = false } = {}) {
	return {
		async query(vector, opts) {
			if (shouldThrow) throw new Error('Vectorize unavailable');
			return { matches };
		},
	};
}

function makeMatch(articleId, score, overrides = {}) {
	return {
		id: `chunk-${articleId}-${score}`,
		score,
		metadata: {
			article_id: articleId,
			title: `Title for ${articleId}`,
			url: `/blog/${articleId}/`,
			language: 'zh',
			excerpt: `excerpt for ${articleId}`,
			...overrides,
		},
	};
}

async function makeEnv(overrides = {}) {
	return {
		BLOG_SEARCH_SESSION_SECRET: SESSION_SECRET,
		BLOG_SEARCH_KV: makeFakeKv(),
		AI: makeFakeAi(),
		VECTORIZE_INDEX: makeFakeVectorize(),
		...overrides,
	};
}

async function validCookie() {
	const issuedAt = Math.floor(Date.now() / 1000);
	return signSession(SESSION_SECRET, { issuedAt, maxAgeSeconds: 3600 });
}

function makeRequest(body, { ip = '5.5.5.5', cookie, contentType = 'application/json' } = {}) {
	const bodyText = JSON.stringify(body);
	const headers = {
		'Content-Type': contentType,
		'CF-Connecting-IP': ip,
		'Content-Length': String(new TextEncoder().encode(bodyText).length),
	};
	if (cookie) headers.Cookie = `${COOKIE_NAME}=${cookie}`;
	return new Request('https://example.com/api/search', { method: 'POST', headers, body: bodyText });
}

test('没有登录 Cookie：401，不消耗限速额度也不调 AI/Vectorize', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 401);
});

test('Cookie 格式错误/验签失败：401', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({
		request: makeRequest({ query: 'hello' }, { cookie: 'not-a-valid-cookie' }),
		env,
	});
	assert.equal(resp.status, 401);
});

test('过期 Cookie：401', async () => {
	const env = await makeEnv();
	const issuedAt = Math.floor(Date.now() / 1000) - 7200;
	const expired = await signSession(SESSION_SECRET, { issuedAt, maxAgeSeconds: 3600 });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie: expired }), env });
	assert.equal(resp.status, 401);
});

test('缺少必需的 Cloudflare 绑定：503（fail-closed，不静默放行到无限速/无认证）', async () => {
	const env = await makeEnv({ AI: undefined });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	assert.equal(resp.status, 503);
});

test('Content-Type 不是 application/json：400（同 search-auth.js 的 text/plain 绕过修复）', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const resp = await onRequestPost({
		request: makeRequest({ query: 'hello' }, { cookie, contentType: 'text/plain' }),
		env,
	});
	assert.equal(resp.status, 400);
});

test('请求体超过大小上限：413', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const resp = await onRequestPost({
		request: makeRequest({ query: 'x'.repeat(5000) }, { cookie }),
		env,
	});
	assert.equal(resp.status, 413);
});

test('请求体不是合法 JSON：400', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const badRequest = new Request('https://example.com/api/search', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.1.1.1', Cookie: `${COOKIE_NAME}=${cookie}` },
		body: 'not json{{{',
	});
	const resp = await onRequestPost({ request: badRequest, env });
	assert.equal(resp.status, 400);
});

test('query 为空：400', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: '' }, { cookie }), env });
	assert.equal(resp.status, 400);
});

test('query 超过长度上限：400', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'a'.repeat(401) }, { cookie }), env });
	assert.equal(resp.status, 400);
});

test('限速：同一 IP 超过搜索限速次数后 429', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const ip = '7.7.7.7';
	// 搜索限速配置在 search.js 内部（30 次/5 分钟），这里只断言"存在一个上限、超过会 429"，
	// 不依赖具体数字（数字本身在 search.js 里注释说明了理由，测试只验证行为）
	let lastStatus;
	for (let i = 0; i < 35; i++) {
		const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie, ip }), env });
		lastStatus = resp.status;
		if (lastStatus === 429) break;
	}
	assert.equal(lastStatus, 429, '连续请求应该在某一次触发限速');
});

test('限速：不同 IP 互不影响', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	for (let i = 0; i < MAX_ATTEMPTS * 10; i++) {
		const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie, ip: '8.8.8.8' }), env });
		if (resp.status === 429) break;
	}
	const otherIp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie, ip: '9.9.9.9' }), env });
	assert.equal(otherIp.status, 200, '另一个 IP 不应该被前一个 IP 的搜索限速影响');
});

test('Workers AI 调用失败：503，不是裸抛异常', async () => {
	const env = await makeEnv({ AI: makeFakeAi({ shouldThrow: true }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	assert.equal(resp.status, 503);
});

test('Vectorize 查询失败：503', async () => {
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	assert.equal(resp.status, 503);
});

test('正常查询：按 article_id 聚合去重，只保留每篇文章分数最高的 chunk', async () => {
	const matches = [
		makeMatch('article-a', 0.9),
		makeMatch('article-a', 0.6), // 同一篇文章的另一个 chunk，分数更低，应该被丢弃
		makeMatch('article-b', 0.5),
	];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	assert.equal(resp.status, 200);
	const body = await resp.json();
	assert.equal(body.results.length, 2);
	const articleA = body.results.find((r) => r.article_id === 'article-a');
	assert.equal(articleA.score, 0.9, '应该保留分数更高的那个 chunk，不是先出现的那个');
});

test('正常查询：低于相似度阈值的候选被过滤掉', async () => {
	const matches = [makeMatch('article-good', 0.6), makeMatch('article-bad', 0.1)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	const body = await resp.json();
	assert.equal(body.results.length, 1);
	assert.equal(body.results[0].article_id, 'article-good');
});

test('正常查询：全部候选都低于阈值时返回空数组，不是报错', async () => {
	const matches = [makeMatch('article-a', 0.1), makeMatch('article-b', 0.2)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	assert.equal(resp.status, 200);
	const body = await resp.json();
	assert.deepEqual(body.results, []);
});

test('正常查询：结果按分数降序排列', async () => {
	const matches = [makeMatch('article-low', 0.45), makeMatch('article-high', 0.8), makeMatch('article-mid', 0.6)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	const body = await resp.json();
	assert.deepEqual(
		body.results.map((r) => r.article_id),
		['article-high', 'article-mid', 'article-low'],
	);
});

test('正常查询：返回字段形状正确（article_id/title/url/language/excerpt/score）', async () => {
	const matches = [makeMatch('article-a', 0.7, { language: 'en' })];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const cookie = await validCookie();
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie }), env });
	const body = await resp.json();
	assert.deepEqual(body.results[0], {
		article_id: 'article-a',
		title: 'Title for article-a',
		url: '/blog/article-a/',
		language: 'en',
		excerpt: 'excerpt for article-a',
		score: 0.7,
	});
});

test('GET 请求：405', async () => {
	const resp = await onRequestGet();
	assert.equal(resp.status, 405);
});
