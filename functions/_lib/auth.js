/**
 * T1.3.6：密码 + 签名 Cookie 认证的共享逻辑。
 *
 * `_lib` 目录开头下划线——Cloudflare Pages Functions 的约定，这个目录不会被当成路由，
 * 只是给 functions/api/*.js 互相 import 的普通模块。
 *
 * 设计要点（对应 docs/agent/architecture.md 核心判断 7 / spec.md §登录会话）：
 * - 单一共享密码，不是账号体系；密码本身不进 Cookie，Cookie 只是一个 HMAC 签名的
 *   {v, issuedAt, expiresAt} payload，服务端凭 BLOG_SEARCH_SESSION_SECRET 验签
 * - 密码比较用常量时间，避免通过响应耗时旁路猜出密码长度/内容
 * - 门禁只挡语义检索能力，不挡已经公开的 Pagefind 关键词搜索——本模块只负责认证本身，
 *   "挡哪个功能"由调用方（search-auth.js / 将来的 T1.3.3 search.js）决定
 */

// 修正（PR#48 review + Codex 对抗发现，medium）：不带 __Host- 前缀时，浏览器分不清
// "谁有资格设置这个名字的 Cookie"——一个被攻陷的兄弟子域（比如 evil.mushroom.cv）
// 可以用 Domain=mushroom.cv 设一个同名的域 Cookie，浏览器会把域 Cookie 和真正的
// host-only Cookie 一起发过来，getCookie() 取第一个匹配、顺序不代表可信度，取到垃圾值
// 就一直验签失败——不是伪造出有效会话，是把人锁在门外的可用性问题。__Host- 前缀由浏览器
// 强制要求 Secure + Path=/ + 不带 Domain，从机制上不允许被域 Cookie 影子化，这三条本来
// 就是 buildSetCookieHeader 一直在设的属性，加前缀不影响任何现有行为。
const COOKIE_NAME = '__Host-blog_search_session';
const SESSION_VERSION = 1;
// 上限按 spec.md §登录会话的 30-90 天区间取宽松上界——不是当前实际用的 Max-Age
// （那个由调用方 signSession 时传入），是"哪怕签发端将来出 bug，也不该签出比这更长"
// 的防御性天花板
const MAX_SESSION_LIFETIME_SECONDS = 90 * 24 * 60 * 60;
const CLOCK_SKEW_TOLERANCE_SECONDS = 5 * 60; // 允许 5 分钟的时钟误差，不是安全边界，只是容错

async function timingSafeEqual(a, b) {
	// 修正（对抗式 review 指出注释和实现不一致的真实 bug）：这里原来直接比较变长的
	// UTF-8 字节数组，运行时间会随"候选串长度"和"真实密码长度"里较大的那个增长——
	// 实测候选串比真实密码短时，耗时由真实密码的长度决定，理论上能当密码长度的计时
	// 旁路用（虽然在这个部署形态下——Cloudflare 的网络抖动是毫秒级、这里是纳秒级差异，
	// 而且限速卡在 15 分钟 5 次——不构成实际可利用的攻击，但修起来成本很低，直接把
	// 两边先各自哈希成定长摘要再比较，从根上消掉"运行时间随输入长度变化"这件事）
	const enc = new TextEncoder();
	const [digestA, digestB] = await Promise.all([
		crypto.subtle.digest('SHA-256', enc.encode(a)),
		crypto.subtle.digest('SHA-256', enc.encode(b)),
	]);
	const bufA = new Uint8Array(digestA);
	const bufB = new Uint8Array(digestB);
	// 两个 SHA-256 摘要永远等长（32 字节），不会再有变长分支
	let diff = 0;
	for (let i = 0; i < bufA.length; i++) {
		diff |= bufA[i] ^ bufB[i];
	}
	return diff === 0;
}

async function verifyPassword(candidate, expected) {
	if (typeof candidate !== 'string' || typeof expected !== 'string' || !expected) {
		return false;
	}
	return timingSafeEqual(candidate, expected);
}

function base64UrlEncode(bytes) {
	let binary = '';
	for (const b of bytes) binary += String.fromCharCode(b);
	return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function base64UrlDecode(str) {
	const padded = str.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (str.length % 4)) % 4);
	const binary = atob(padded);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
	return bytes;
}

async function importHmacKey(secret) {
	return crypto.subtle.importKey(
		'raw',
		new TextEncoder().encode(secret),
		{ name: 'HMAC', hash: 'SHA-256' },
		false,
		['sign', 'verify'],
	);
}

/**
 * 签发 Cookie value（不含 Set-Cookie 的其他属性，那些由调用方拼）。
 * maxAgeSeconds 用来算 expiresAt——是"从签发时刻起多久过期"，不是 Cookie 本身的
 * Max-Age 属性（那个由浏览器执行，这里的 expiresAt 是服务端验签时的第二道防线，
 * 即使客户端偷改了 Cookie 的 Max-Age，服务端仍然按 payload 里签名过的 expiresAt 判断）。
 */
async function signSession(secret, { issuedAt, maxAgeSeconds }) {
	const payload = { v: SESSION_VERSION, issuedAt, expiresAt: issuedAt + maxAgeSeconds };
	const payloadBytes = new TextEncoder().encode(JSON.stringify(payload));
	const payloadB64 = base64UrlEncode(payloadBytes);
	const key = await importHmacKey(secret);
	const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payloadB64));
	const sigB64 = base64UrlEncode(new Uint8Array(sig));
	return `${payloadB64}.${sigB64}`;
}

/**
 * 验证 Cookie value。返回 { valid: true, payload } 或 { valid: false, reason }。
 * reason 只用于服务端日志排查，不应该原样回给客户端（不透露验证失败的具体原因，
 * 避免帮攻击者调试伪造 Cookie）。
 */
async function verifySession(secret, cookieValue) {
	if (typeof cookieValue !== 'string' || !cookieValue.includes('.')) {
		return { valid: false, reason: 'malformed' };
	}
	const dotIndex = cookieValue.lastIndexOf('.');
	const payloadB64 = cookieValue.slice(0, dotIndex);
	const sigB64 = cookieValue.slice(dotIndex + 1);
	if (!payloadB64 || !sigB64) {
		return { valid: false, reason: 'malformed' };
	}

	let sigBytes;
	try {
		sigBytes = base64UrlDecode(sigB64);
	} catch {
		return { valid: false, reason: 'bad-signature-encoding' };
	}

	const key = await importHmacKey(secret);
	const valid = await crypto.subtle.verify(
		'HMAC',
		key,
		sigBytes,
		new TextEncoder().encode(payloadB64),
	);
	if (!valid) {
		return { valid: false, reason: 'bad-signature' };
	}

	let payload;
	try {
		payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64)));
	} catch {
		return { valid: false, reason: 'bad-payload-encoding' };
	}

	if (
		typeof payload !== 'object' ||
		payload === null ||
		typeof payload.expiresAt !== 'number' ||
		typeof payload.issuedAt !== 'number' ||
		payload.v !== SESSION_VERSION
	) {
		// v 字段校验是留给以后改 payload 结构用的——现在只有一个版本，加上这个检查纯粹是
		// 防御性的（review 指出的：这个字段原来签了从没验证过），不影响当前行为
		return { valid: false, reason: 'bad-payload-shape' };
	}

	// 修正（PR#48 review 指出的防御性缺口）：这几条只签发合理性的不变式，今天客户端伪造不了
	// （要有效 HMAC 才能改 payload），加上它们不改变当前任何正常场景的行为——纯粹是限制
	// "万一将来签发端自己出 bug"时的爆炸半径，不依赖它们来防真正的攻击者
	if (payload.expiresAt < payload.issuedAt) {
		return { valid: false, reason: 'bad-payload-shape' };
	}
	if (payload.expiresAt - payload.issuedAt > MAX_SESSION_LIFETIME_SECONDS) {
		return { valid: false, reason: 'bad-payload-shape' };
	}

	const nowSeconds = Date.now() / 1000;
	if (payload.issuedAt > nowSeconds + CLOCK_SKEW_TOLERANCE_SECONDS) {
		return { valid: false, reason: 'bad-payload-shape' };
	}
	if (nowSeconds >= payload.expiresAt) {
		return { valid: false, reason: 'expired' };
	}

	return { valid: true, payload };
}

/** 从 Cookie 请求头里取出指定 name 的值（未做 URL 解码——签名 Cookie 本身就是
 * base64url 字符集，不需要额外解码，避免解码引入的边角问题）。 */
function getCookie(request, name) {
	const header = request.headers.get('Cookie');
	if (!header) return null;
	for (const part of header.split(';')) {
		const eq = part.indexOf('=');
		if (eq === -1) continue;
		const key = part.slice(0, eq).trim();
		if (key === name) return part.slice(eq + 1).trim();
	}
	return null;
}

function buildSetCookieHeader(name, value, { maxAgeSeconds }) {
	return `${name}=${value}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAgeSeconds}`;
}

export { COOKIE_NAME, verifyPassword, signSession, verifySession, getCookie, buildSetCookieHeader };
