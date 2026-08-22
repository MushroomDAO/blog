/**
 * POST /api/search-auth
 *
 * 密码登录：校验 env.BLOG_SEARCH_PASSWORD（常量时间比较），成功签发 HMAC 签名 Cookie
 * （见 functions/_lib/auth.js），用于后续访问 /api/search（T1.3.3，语义检索能力）。
 * 不挡 T1.1.3 已上线的纯 Pagefind 关键词搜索——那部分从来不需要登录。
 *
 * 需要的环境变量/绑定（Cloudflare Pages → Settings）：
 *   BLOG_SEARCH_PASSWORD        必需。共享登录密码。
 *   BLOG_SEARCH_SESSION_SECRET  必需。签 Cookie 用的 HMAC 密钥，跟密码本身分开存。
 *   BLOG_SEARCH_KV              必需。KV binding，跟 T1.3.5 的索引 manifest 共用同一个
 *                                namespace，key 加 "ratelimit:" 前缀区分。
 */

import { checkAndIncrement } from '../_lib/rate-limit.js';
import { buildSetCookieHeader, COOKIE_NAME, signSession, verifyPassword } from '../_lib/auth.js';

const MAX_AGE_SECONDS = 60 * 60 * 24 * 60; // 60 天——见 spec.md §登录会话，不用 1 年缩短泄露窗口
const MAX_PASSWORD_LENGTH = 256; // 防止有人扔一个几 MB 的 body 上来做常量时间比较之外的资源消耗攻击
// 修正（review 抓到的真实 bug）：这个接口的合法请求体永远是 {"password": "<=256 字符"}，
// 正常情况下几百字节顶天。原来只在 request.json() 解析完之后才检查密码长度，等于先让
// Cloudflare 把整个 body（Free/Pro 套餐上限 100MB）都解析/分配完，MAX_PASSWORD_LENGTH
// 根本挡不住"塞一堆无关大字段撑大 body"这种消耗解析开销的请求。改成先看 Content-Length，
// body 明显超出预期就直接拒，不进 request.json()。
const MAX_BODY_BYTES = 4096;

function jsonResponse(body, status, extraHeaders = {}) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json', ...extraHeaders },
	});
}

export async function onRequestPost(context) {
	const { request, env } = context;

	if (!env.BLOG_SEARCH_PASSWORD || !env.BLOG_SEARCH_SESSION_SECRET) {
		// 环境变量没配置齐，不能悄悄放行也不能报出"配置缺失"这种对攻击者有用的细节，
		// 统一当成服务不可用处理
		return jsonResponse({ error: 'search auth not configured' }, 503);
	}

	// 修正（review 抓到的真实 bug）：CF-Connecting-IP 在真实 Cloudflare 边缘流量里由平台
	// 权威写入、客户端伪造不了，但这个 header 缺失时（本地 wrangler dev、非边缘路径调用等
	// 不该在生产发生、但确实可能在别的场景出现的情况）原来会退化成字面量 "unknown"，
	// 让所有缺 header 的调用方共享同一个限速桶——不相关的调用方能互相把对方锁出去。
	// 缺 header 时直接跳过限速（等同于没配 KV binding 的降级路径），不参与共享桶。
	const ip = request.headers.get('CF-Connecting-IP');
	if (ip && env.BLOG_SEARCH_KV) {
		const { allowed } = await checkAndIncrement(env.BLOG_SEARCH_KV, ip);
		if (!allowed) {
			return jsonResponse({ error: 'too many attempts, try again later' }, 429);
		}
	}
	// 没配 KV binding、或者拿不到真实 IP 时不因为限速功能缺失就拒绝登录本身——密码校验
	// 仍然生效，只是少了限速这层防护，比整个登录功能不可用更合理（配置/环境问题不应该
	// 锁死正常用户）

	// 注意：这只挡"如实声明了 Content-Length 且超限"的请求，挡不住不带 Content-Length
	// 或者谎报长度的请求（chunked encoding 等）——那类请求仍然要靠 Cloudflare 平台自己的
	// 请求体上限兜底（Free/Pro 100MB）。这里的检查是"廉价挡掉正常客户端不会触发、
	// 但简单脚本可能顺手带上的大 body"，不是完整的防线，好过完全没有。
	const contentLength = Number(request.headers.get('Content-Length') || 0);
	if (contentLength > MAX_BODY_BYTES) {
		return jsonResponse({ error: 'request body too large' }, 413);
	}

	let body;
	try {
		body = await request.json();
	} catch {
		return jsonResponse({ error: 'invalid request body' }, 400);
	}

	const password = body && typeof body.password === 'string' ? body.password : '';
	if (!password || password.length > MAX_PASSWORD_LENGTH) {
		return jsonResponse({ error: 'invalid password' }, 400);
	}

	const ok = await verifyPassword(password, env.BLOG_SEARCH_PASSWORD);
	if (!ok) {
		// 故意跟"密码没配置"用不同状态码（401 vs 503），但错误消息都不透露具体原因
		return jsonResponse({ error: 'invalid password' }, 401);
	}

	const issuedAt = Math.floor(Date.now() / 1000);
	const cookieValue = await signSession(env.BLOG_SEARCH_SESSION_SECRET, {
		issuedAt,
		maxAgeSeconds: MAX_AGE_SECONDS,
	});
	const setCookie = buildSetCookieHeader(COOKIE_NAME, cookieValue, { maxAgeSeconds: MAX_AGE_SECONDS });

	return jsonResponse({ ok: true }, 200, { 'Set-Cookie': setCookie });
}

// 明确拒绝其他方法，不要让 Cloudflare 默认的 405 页面（可能带调试信息）漏出去
export async function onRequestGet() {
	return jsonResponse({ error: 'method not allowed' }, 405);
}
