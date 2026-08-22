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

// maxAgeSeconds 可传不同值来确定性地拿到不同的 Cookie 字符串（同一秒内调用两次、issuedAt
// 一样的话，唯一能让签名不同的就是这个）——测"不同会话"的用例需要这个，不能靠掐时间点。
async function validCookie(maxAgeSeconds = 3600) {
	const issuedAt = Math.floor(Date.now() / 1000);
	return signSession(SESSION_SECRET, { issuedAt, maxAgeSeconds });
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

// 回归测试（T1.3.3 自审对抗式 review 抓到的真实问题）：Content-Length 是请求方自己声明的，
// 谎报成一个很小的值、但实际发送的 body 远超上限，不该只靠这个 header 就放行
test('回归测试：Content-Length 撒谎（远小于实际 body），仍然按实际字节数拦截：413', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	const bodyText = JSON.stringify({ query: 'x'.repeat(5000) });
	const request = new Request('https://example.com/api/search', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'CF-Connecting-IP': '1.1.1.1',
			Cookie: `${COOKIE_NAME}=${cookie}`,
			'Content-Length': '10', // 谎报成很小的值
		},
		body: bodyText,
	});
	const resp = await onRequestPost({ request, env });
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

test('限速：同一 IP + 同一会话超过搜索限速次数后 429', async () => {
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

test('限速：不同 IP + 不同会话，互不影响', async () => {
	const env = await makeEnv();
	const cookieA = await validCookie();
	for (let i = 0; i < MAX_ATTEMPTS * 10; i++) {
		const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie: cookieA, ip: '8.8.8.8' }), env });
		if (resp.status === 429) break;
	}
	const cookieB = await validCookie(7200); // 不同 maxAgeSeconds -> 不同签名 -> 不同会话
	const otherSession = await onRequestPost({
		request: makeRequest({ query: 'hello' }, { cookie: cookieB, ip: '9.9.9.9' }),
		env,
	});
	assert.equal(otherSession.status, 200, '不同 IP+不同会话的组合不应该被前一个组合的限速影响');
});

// 回归测试（T1.3.3 自审对抗式 review 抓到的真实问题）：只按 IP 限速时，泄露的 Cookie
// 换个 IP 就能绕过限速，而 Cookie 本身（60 天有效期、无撤销机制）没有总量上限。加了按
// 会话（Cookie 哈希）限速之后，同一个会话换 IP 也应该被限速挡住。
test('限速：同一会话换不同 IP 打，仍然会被会话级限速挡住（新增的按会话限速）', async () => {
	const env = await makeEnv();
	const cookie = await validCookie();
	let lastStatus;
	for (let i = 0; i < 35; i++) {
		// 每次换一个不同的 IP，模拟"泄露的 Cookie 被脚本换着代理 IP 打"
		const ip = `10.0.0.${i}`;
		const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie, ip }), env });
		lastStatus = resp.status;
		if (lastStatus === 429) break;
	}
	assert.equal(lastStatus, 429, '同一个会话即使每次都换新 IP，也应该在某一次被会话级限速拦住');
});

test('限速：同一 IP、不同会话，仍然会被 IP 级限速挡住（IP 限速继续有效，不是被会话限速取代）', async () => {
	const env = await makeEnv();
	const ip = '11.11.11.11';
	let lastStatus;
	for (let i = 0; i < 35; i++) {
		// 每次换一个不同的会话（不同 maxAgeSeconds -> 不同签名），模拟多个不同登录会话
		// 共享同一个 IP（比如同一个办公室出口）打同一个端点
		const cookie = await validCookie(3600 + i);
		const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }, { cookie, ip }), env });
		lastStatus = resp.status;
		if (lastStatus === 429) break;
	}
	assert.equal(lastStatus, 429, '同一个 IP 即使每次都换新会话，也应该在某一次被 IP 级限速拦住');
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
