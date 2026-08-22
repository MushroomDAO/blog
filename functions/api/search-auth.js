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
 *   BLOG_SEARCH_KV              必需——真的必需，不是"缺了就降级"：限速是这个端点唯一的
 *                                在线爆破防线，缺失时 fail-closed 返回 503，不会静默放行到
 *                                无限次密码尝试。跟 T1.3.5 的索引 manifest 共用同一个
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

	// 修正（PR#48 review + Codex 对抗发现的真实阻塞 bug B1）：限速原来在解析/校验请求体
	// 之前就计数，任何 POST——哪怕连密码字段都没有——都会先扣掉一次额度。这意味着一个
	// 跨站页面不需要知道密码、甚至不需要拿到任何回显，只要连续 POST 5 次垃圾请求，
	// 就能让真实用户（或整个 NAT 后的办公室 IP）被限速锁在门外 15 分钟——这不是密码爆破，
	// 是纯粹的拒绝服务，而且攻击者不需要任何凭证。
	//
	// 修法：先做"这看起来像不像一次真正的登录尝试"的廉价校验（body 大小、JSON 格式、
	// password 字段存在且类型/长度合法），全部通过之后才计入限速次数，紧接着才做真正的
	// 密码比较。这样"限的是打了多少次、不是打错了多少次"这个原有设计意图不变（只要是一次
	// 形状合法的登录尝试，不管密码对不对都计数，避免攻击者靠故意在最后一步失败绕过），
	// 但不合法的垃圾请求不再白白消耗真实用户的额度。
	//
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

	// 修正（同一份 review 发现的真实阻塞 bug B2）：这个接口的文件头文档写着
	// "BLOG_SEARCH_KV 必需"，但原实现在 binding 缺失（或拿不到 CF-Connecting-IP）时
	// 直接跳过限速、放行到密码比较——限速是这个端点**唯一**的在线爆破防线，一旦悄无
	// 声息地失效，等于密码可以无限次尝试，而且登录功能本身"看起来"完全正常、没有任何
	// 报错提示配置出了问题。更严重的是：这个 PR 自己在"后续"一节写明 BLOG_SEARCH_KV
	// 需要等 T1.3.5 的 KV namespace 建好才能配置——也就是说刚上线那段时间，这个 binding
	// 大概率就是没配的状态。改成 fail-closed：KV binding 缺失、或者拿不到真实 IP，
	// 都当成服务未就绪处理（跟 env.BLOG_SEARCH_PASSWORD 缺失同一个 503 语义），
	// 不再静默放行到密码比较。
	const ip = request.headers.get('CF-Connecting-IP');
	if (!ip || !env.BLOG_SEARCH_KV) {
		return jsonResponse({ error: 'search auth not configured' }, 503);
	}
	const { allowed } = await checkAndIncrement(env.BLOG_SEARCH_KV, ip);
	if (!allowed) {
		return jsonResponse({ error: 'too many attempts, try again later' }, 429);
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
