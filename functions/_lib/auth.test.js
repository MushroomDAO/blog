// T1.3.6 验收测试：Cookie 签名/验签逻辑。用 Node 内建测试跑，不需要 wrangler/Miniflare
// （crypto.subtle/TextEncoder 是标准 Web Crypto API，Node 18+ 原生支持，跟 Cloudflare
// Workers 运行时用的是同一套 API）。
//
// 用法：node --test functions/_lib/*.test.js

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildSetCookieHeader, COOKIE_NAME, getCookie, signSession, verifyPassword, verifySession } from './auth.js';

const SECRET = 'test-session-secret-do-not-use-in-prod';

test('verifyPassword: 正确密码通过', async () => {
	assert.equal(await verifyPassword('correct-horse', 'correct-horse'), true);
});

test('verifyPassword: 错误密码不通过', async () => {
	assert.equal(await verifyPassword('wrong', 'correct-horse'), false);
});

test('verifyPassword: 空密码/非字符串输入不通过、不抛异常', async () => {
	assert.equal(await verifyPassword('', 'correct-horse'), false);
	assert.equal(await verifyPassword(undefined, 'correct-horse'), false);
	assert.equal(await verifyPassword('anything', ''), false);
});

test('verifyPassword: 长度不同的字符串不通过（且不因为提前 return 而跳过后续比较分支）', async () => {
	assert.equal(await verifyPassword('short', 'a-much-longer-password'), false);
	assert.equal(await verifyPassword('a-much-longer-password', 'short'), false);
});

test('signSession + verifySession: 正确签名的 Cookie 验证通过，payload 字段完整', async () => {
	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 3600 });
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, true);
	assert.equal(result.payload.v, 1);
	assert.equal(result.payload.issuedAt, issuedAt);
	assert.equal(result.payload.expiresAt, issuedAt + 3600);
});

test('verifySession: 过期的 Cookie 验证失败', async () => {
	const issuedAt = Math.floor(Date.now() / 1000) - 7200; // 2 小时前签发
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 3600 }); // 1 小时有效期，早过期了
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, false);
	assert.equal(result.reason, 'expired');
});

test('verifySession: 用错误的密钥验证会失败（签名对不上）', async () => {
	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 3600 });
	const result = await verifySession('a-completely-different-secret', cookieValue);
	assert.equal(result.valid, false);
	assert.equal(result.reason, 'bad-signature');
});

test('verifySession: 篡改 payload（改 expiresAt 想延长有效期）会被签名校验挡住', async () => {
	const issuedAt = Math.floor(Date.now() / 1000) - 7200;
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 3600 });
	const [payloadB64, sigB64] = cookieValue.split('.');
	// 解出 payload、改 expiresAt、重新拼回去，但不重新签名——模拟客户端瞎改 Cookie
	const forged = JSON.parse(Buffer.from(payloadB64.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString());
	forged.expiresAt = Math.floor(Date.now() / 1000) + 999999;
	const forgedB64 = Buffer.from(JSON.stringify(forged))
		.toString('base64')
		.replace(/\+/g, '-')
		.replace(/\//g, '_')
		.replace(/=+$/, '');
	const tamperedCookie = `${forgedB64}.${sigB64}`;
	const result = await verifySession(SECRET, tamperedCookie);
	assert.equal(result.valid, false);
	assert.equal(result.reason, 'bad-signature');
});

test('verifySession: 格式错误的输入（没有 "." 分隔符）不抛异常，直接判无效', async () => {
	const result = await verifySession(SECRET, 'not-a-valid-cookie-value');
	assert.equal(result.valid, false);
	assert.equal(result.reason, 'malformed');
});

test('verifySession: 非字符串/空值输入不抛异常', async () => {
	assert.equal((await verifySession(SECRET, null)).valid, false);
	assert.equal((await verifySession(SECRET, undefined)).valid, false);
	assert.equal((await verifySession(SECRET, '')).valid, false);
});

test('getCookie: 从 Cookie 请求头里正确取出指定 name 的值', () => {
	const request = new Request('https://example.com/', {
		headers: { Cookie: `foo=bar; ${COOKIE_NAME}=abc123; baz=qux` },
	});
	assert.equal(getCookie(request, COOKIE_NAME), 'abc123');
	assert.equal(getCookie(request, 'foo'), 'bar');
	assert.equal(getCookie(request, 'not-present'), null);
});

test('getCookie: 没有 Cookie 请求头时返回 null，不抛异常', () => {
	const request = new Request('https://example.com/');
	assert.equal(getCookie(request, COOKIE_NAME), null);
});

test('buildSetCookieHeader: 包含全部要求的属性（HttpOnly/Secure/SameSite=Lax/Path=/）', () => {
	const header = buildSetCookieHeader(COOKIE_NAME, 'sample-value', { maxAgeSeconds: 5184000 });
	assert.match(header, /HttpOnly/);
	assert.match(header, /Secure/);
	assert.match(header, /SameSite=Lax/);
	assert.match(header, /Path=\//);
	assert.match(header, /Max-Age=5184000/);
});

// 回归测试：PR#48 review + Codex 对抗发现的真实问题
test('COOKIE_NAME 带 __Host- 前缀（防兄弟子域用同名域 Cookie 影子化，导致真实用户被锁在门外）', () => {
	assert.match(COOKIE_NAME, /^__Host-/);
});

test('buildSetCookieHeader 的输出满足 __Host- 前缀的浏览器强制要求（Secure + Path=/ + 不带 Domain）', () => {
	const header = buildSetCookieHeader(COOKIE_NAME, 'sample-value', { maxAgeSeconds: 5184000 });
	assert.match(header, /Secure/);
	assert.match(header, /Path=\//);
	assert.doesNotMatch(header, /Domain=/i);
});

test('verifySession: 签发时间在未来太久（超出容忍的时钟误差）判无效', async () => {
	const issuedAt = Math.floor(Date.now() / 1000) + 3600; // 签发时间在 1 小时后，明显不合理
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 3600 });
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, false);
});

test('verifySession: expiresAt 早于 issuedAt（签发逻辑万一出 bug）判无效', async () => {
	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: -100 }); // 故意传负数模拟 bug
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, false);
});

test('verifySession: 会话时长超过防御性天花板（远超 spec.md 的 30-90 天区间）判无效', async () => {
	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 365 * 24 * 60 * 60 }); // 1 年，远超上限
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, false);
});

test('verifySession: 正常场景（60 天有效期，spec.md 实际用的值）不受新增不变式影响', async () => {
	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(SECRET, { issuedAt, maxAgeSeconds: 60 * 24 * 60 * 60 });
	const result = await verifySession(SECRET, cookieValue);
	assert.equal(result.valid, true);
});
