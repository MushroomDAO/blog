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

test('回归测试（FU-12）：Content-Length 撒谎（远小于实际 body），仍然按实际字节数拦截：413', async () => {
	// 跟 T1.3.3 的 search.js 同一个问题：Content-Length 是请求方自己声明的，谎报成一个
	// 很小的值、但实际发送的 body 远超上限，不该只靠这个 header 就放行到 request.json()
	const env = makeEnv();
	const bodyText = JSON.stringify({ password: 'x'.repeat(5000) });
	const request = new Request('https://example.com/api/search-auth', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'CF-Connecting-IP': '1.1.1.1',
			'Content-Length': '10', // 谎报成很小的值
		},
		body: bodyText,
	});
	const resp = await onRequestPost({ request, env });
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

test('回归测试（PR#48 review 阻塞项 B2）：没配 BLOG_SEARCH_KV 绑定时 fail-closed 返回 503，不放行到密码比较', async () => {
	// 原来的行为是"限速功能缺失但密码校验仍然生效"——但限速是这个端点唯一的在线爆破
	// 防线，缺失时不该静默放行到无限次密码尝试。尤其是这个 PR 自己在"后续"一节写明
	// BLOG_SEARCH_KV 需要等 T1.3.5 的 KV namespace 建好才配置，上线初期大概率就是没配的
	// 状态——如果这时候密码校验仍然生效，等于密码可以无限次尝试。
	const env = makeEnv({ BLOG_SEARCH_KV: undefined });
	const resp = await onRequestPost({ request: makeRequest({ password: 'correct-password' }), env });
	assert.equal(resp.status, 503);
});

test('回归测试（PR#48 review）：缺 CF-Connecting-IP 时同样 fail-closed 返回 503', async () => {
	const env = makeEnv();
	const noIpRequest = (body) =>
		new Request('https://example.com/api/search-auth', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Content-Length': String(new TextEncoder().encode(JSON.stringify(body)).length),
			}, // 故意不带 CF-Connecting-IP
			body: JSON.stringify(body),
		});
	const resp = await onRequestPost({ request: noIpRequest({ password: 'correct-password' }), env });
	assert.equal(resp.status, 503);
});

test('回归测试（PR#48 review + Codex 对抗发现的阻塞项 B1）：请求体格式错误的请求不消耗限速额度', async () => {
	// 原来限速在解析/校验请求体之前就计数——任何 POST，哪怕连密码字段都没有，都会先扣
	// 一次额度。跨站页面不需要知道密码、不需要拿到任何回显，只要连续 POST 5 次垃圾请求，
	// 就能把真实用户锁在门外 15 分钟。现在把计数点挪到"请求体至少是合法 JSON 且带
	// password 字段"之后，垃圾请求应该在到达限速计数之前就被拒绝（400），不影响后面
	// 真实用户用正确密码登录。
	const env = makeEnv();
	const ip = '6.6.6.6';
	const garbageRequest = () =>
		new Request('https://example.com/api/search-auth', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': ip },
			body: 'not-even-json{{{',
		});
	// 连续 10 次垃圾请求——远超 MAX_ATTEMPTS，如果这些请求消耗了限速额度，
	// 后面这个 IP 的任何请求都会被 429 拦住
	for (let i = 0; i < MAX_ATTEMPTS * 2; i++) {
		const resp = await onRequestPost({ request: garbageRequest(), env });
		assert.equal(resp.status, 400, `第 ${i + 1} 次垃圾请求应该是 400（格式错误），不是别的`);
	}
	const realAttempt = await onRequestPost({ request: makeRequest({ password: 'correct-password' }, { ip }), env });
	assert.equal(realAttempt.status, 200, '真正的登录尝试不应该被之前的垃圾请求连累限速');
});

test('回归测试（PR#48 round 2 review 阻塞项 B1，Codex 发现）：Content-Type: text/plain 的合法 JSON body 不消耗限速额度', async () => {
	// 跨站简单请求（裸 <form>、no-cors fetch）能发的 Content-Type 只有三种，text/plain 是
	// 其中之一，不触发 CORS 预检。request.json() 本身不检查 Content-Type，只要 body 是合法
	// JSON 就能解析成功——上一轮"垃圾请求 400 在先、限速计数在后"的修复对这种形状的攻击
	// 完全无效，因为它根本不是垃圾请求，是一个 Content-Type 撒了谎的、body 合法的请求。
	const env = makeEnv();
	const ip = '4.4.4.4';
	const textPlainRequest = () => {
		const bodyText = JSON.stringify({ password: 'wrong-but-well-formed' });
		return new Request('https://example.com/api/search-auth', {
			method: 'POST',
			headers: {
				'Content-Type': 'text/plain',
				'CF-Connecting-IP': ip,
				'Content-Length': String(new TextEncoder().encode(bodyText).length),
			},
			body: bodyText,
		});
	};
	for (let i = 0; i < MAX_ATTEMPTS * 2; i++) {
		const resp = await onRequestPost({ request: textPlainRequest(), env });
		assert.equal(resp.status, 400, `第 ${i + 1} 次 text/plain 请求应该是 400（Content-Type 不合法），不是别的`);
	}
	const realAttempt = await onRequestPost({ request: makeRequest({ password: 'correct-password' }, { ip }), env });
	assert.equal(realAttempt.status, 200, '真正的登录尝试不应该被之前的 text/plain 攻击请求连累限速');
});

test('GET 请求：405', async () => {
	const resp = await onRequestGet();
	assert.equal(resp.status, 405);
});
