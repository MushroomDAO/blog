/**
 * GET /api/search-analytics.json
 *
 * 搜索使用统计（用户明确要求：想看上线后有多少人在用、都搜了什么，事件写入见
 * functions/api/search.js 的 logSearchEvent）。查的是 Analytics Engine SQL API。
 *
 * 这是**独立于** /api/analytics.json 的一个端点，不是往那个端点里加一节——原因是
 * 安全考量，不是代码风格偏好：/api/analytics.json 是公开流量看板，用
 * `caches.default` 在边缘共享缓存（同一个 URL 对所有访客返回同一份内容，这是它
 * 故意的设计，公开数据缓存本来就该这样）。如果把搜索词这种理论上更敏感的数据也
 * 塞进那份被共享缓存的响应里，第一个拿到真实数据的请求（比如站长本人登录后访问）
 * 会把结果连同搜索词一起缓存住，缓存 TTL 内所有其它访客（包括完全没登录、甚至
 * 都不知道 /search 密码的人）都会读到同一份缓存——等于把只登录用户能触发的功能
 * 产生的数据，经由公开无认证端点泄露给所有人。这个端点单独存在、且显式
 * `cache-control: private, no-store`（从不进任何共享缓存），未登录一律 401，
 * 把"公开可缓存的流量看板"和"登录用户才能看的搜索统计"彻底分开，不共用同一个
 * 缓存条目。这个端点能读到的是登录用户能查到的搜索词 + FU-25 之后带密钥哈希过的
 * 访客标识（不再是原始 IP）。
 *
 * FU-28：按会话限速（`SESSION_RATE_LIMIT`，见下方）——每次成功请求会打 3 次上游
 * Analytics Engine SQL API，用站长自己的 token。这道限速本来是 PR#61 之前挂在
 * `/api/search` 上的 `SESSION_RATE_LIMIT`，去掉登录门禁时一起删掉了；PR#61 把登录
 * 系统重新定位成"专门给这个端点 + 未来 AI 对话把关"，这个限速器搬到这里是合理的
 * 下一步，不再是"没有归宿"。按会话（登录 Cookie 值的哈希，不是明文）而不是按 IP：
 * 这个端点后面是真实的上游付费/限额 API 调用，按会话限更贴近"同一个登录会话别把
 * 上游配额打爆"这个诉求，也不会因为站长在家里/公司/手机热点几个 IP 之间切换而
 * 各自重新计数。
 *
 * 需要的环境变量：
 *   BLOG_SEARCH_KV      必需（FU-28 起）——按会话限速的计数器用，跟 search-auth.js
 *                       的登录限速、search.js 的查询缓存共用同一个 namespace。
 *   CF_ANALYTICS_ENGINE_TOKEN  可选。专门给 Analytics Engine SQL API 用的 token；
 *                       没配就退化用 CF_ANALYTICS_TOKEN（见下）。
 *   CF_ANALYTICS_TOKEN  必需（若上面那个没配）——**不确定**现有权限范围是否覆盖
 *                       Analytics Engine SQL 查询（这个 token 是为 Web Analytics
 *                       GraphQL API 配的 Account Analytics:Read 权限，Analytics
 *                       Engine SQL API 需要的具体权限组尚未在真实账号里验证过），
 *                       先复用尝试，权限不够会拿到 403（见下方 upstream_http_403）。
 *                       round 2 review 指出：这两个 Cloudflare 产品的数据敏感度不
 *                       一样——这个端点能读到的是登录用户的原始搜索词+IP，比
 *                       Web Analytics 那份纯聚合的公开 RUM 数据敏感得多，如果最终
 *                       方案是"扩大 CF_ANALYTICS_TOKEN 权限"而不是"另铸一个窄权限
 *                       token"，这个 token 一旦泄漏的影响范围会明显放大。**建议**
 *                       单独铸造 CF_ANALYTICS_ENGINE_TOKEN、只给 Analytics Engine
 *                       读权限，不要复用/扩权 CF_ANALYTICS_TOKEN——这里做成可选、
 *                       有退化，方便以后单独配置这个 token 时不需要再改代码。
 *   CF_ACCOUNT_TAG      可选，默认用下方常量（跟 analytics.json.js 一致）。
 */

import { COOKIE_NAME, getCookie, verifySession } from '../_lib/auth.js';
import { checkAndIncrement } from '../_lib/rate-limit.js';

const DEFAULT_ACCOUNT_TAG = '7bf23342f21baa5ebfc7bc7b74f5a1f2';
const SEARCH_DATASET = 'blog_search_events';
// FU-28：见文件头注释。5 分钟 30 次跟 /api/search 原来的 IP 限速数值一致——这个端点
// 后面是 3 次真实上游调用，不是一次，30 次/5 分钟已经足够宽松地覆盖"正常人反复刷新
// 统计页"的场景，同时给"上游配额别被一个会话打爆"这个诉求一个明确上限。
const SESSION_RATE_LIMIT = { prefix: 'searchstats:', windowSeconds: 5 * 60, maxAttempts: 30 };

async function sha256Hex(text) {
	const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
	return Array.from(new Uint8Array(digest))
		.map((b) => b.toString(16).padStart(2, '0'))
		.join('');
}

async function fetchSearchStats(token, accountTag) {
	if (!token) return { error: 'not_configured' };

	const sql = (query) =>
		fetch(`https://api.cloudflare.com/client/v4/accounts/${accountTag}/analytics_engine/sql`, {
			method: 'POST',
			headers: { authorization: `Bearer ${token}`, 'content-type': 'text/plain' },
			body: query,
		});

	try {
		const [totalsResp, dailyResp, topResp] = await Promise.all([
			sql(
				`SELECT count() AS searches, count(DISTINCT index1) AS unique_ips FROM ${SEARCH_DATASET} WHERE timestamp > NOW() - INTERVAL '30' DAY`,
			),
			sql(
				`SELECT toDate(timestamp) AS day, count() AS searches, count(DISTINCT index1) AS unique_ips FROM ${SEARCH_DATASET} WHERE timestamp > NOW() - INTERVAL '30' DAY GROUP BY day ORDER BY day ASC`,
			),
			sql(
				`SELECT blob1 AS query, count() AS cnt FROM ${SEARCH_DATASET} WHERE timestamp > NOW() - INTERVAL '30' DAY GROUP BY blob1 ORDER BY cnt DESC LIMIT 15`,
			),
		]);

		if (!totalsResp.ok || !dailyResp.ok || !topResp.ok) {
			// 修正（correctness round 1 review 指出的真实问题）：原来不管三个请求里
			// 哪个失败，报的都是 totalsResp 的状态码——totals 成功但 daily/top 失败时，
			// 会拿着一个 200 却报 upstream_http，调试时完全看不出真正是哪个查询挂了。
			// 改成找第一个失败的响应，报它自己的状态码。
			const failed = [totalsResp, dailyResp, topResp].find((r) => !r.ok);
			const status = failed.status;
			// 数据集在第一次真实写入之前不存在，查询会 404——这不是错误，是"还没有人
			// 用过这个功能"，页面应该显示"暂无数据"而不是报错。403 单独分出来（production-
			// failure-mode review 指出的真实 UX 缺口）：CF_ANALYTICS_TOKEN 权限不够时也是
			// upstream_http，跟"数据集不存在"归成一类会让站长把"token 权限没配对"误读成
			// "还没人用这个功能"，两种情况需要采取的行动完全不同（前者要去 Cloudflare
			// Dashboard 查 token 权限，后者什么都不用做，等有人用就有数据）。
			// 修正（round 2 review 指出的真实问题）：原来把 400 也归进 no_data_yet——400 是
			// Analytics Engine 判定 SQL 查询本身语法/语义不合法才会返回的状态码，这三条 SQL
			// 从没对真实上游执行过（测试全部 stub 了 fetch），如果任何一条写法有问题，会被
			// 永久误判成"还没人搜"，而不是"这个功能本身是坏的"——两者需要采取的行动完全
			// 不同，不能归成一类。400 现在归进 upstream_http，跟"暂无数据"明确区分开。
			const kind = status === 404 ? 'no_data_yet' : status === 403 ? 'forbidden' : 'upstream_http';
			return { error: kind, status };
		}

		const [totalsBody, dailyBody, topBody] = await Promise.all([totalsResp.json(), dailyResp.json(), topResp.json()]);
		const totalsRow = totalsBody.data?.[0] || {};

		return {
			totalSearches: Number(totalsRow.searches || 0),
			uniqueIps: Number(totalsRow.unique_ips || 0),
			daily: (dailyBody.data || []).map((row) => ({
				date: row.day,
				searches: Number(row.searches || 0),
				uniqueIps: Number(row.unique_ips || 0),
			})),
			topQueries: (topBody.data || []).map((row) => ({
				query: row.query,
				count: Number(row.cnt || 0),
			})),
		};
	} catch (err) {
		return { error: 'fetch_failed', detail: String(err) };
	}
}

export { fetchSearchStats };

const json = (body, status, extraHeaders = {}) =>
	new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'private, no-store', ...extraHeaders },
	});

export async function onRequestGet(context) {
	const { request, env } = context;

	// BLOG_SEARCH_KV 现在也是必需绑定（FU-28 的限速计数器要用）——跟 BLOG_SEARCH_SESSION_SECRET
	// 一样 fail-closed：这个 KV namespace 本来就被 search-auth.js 的登录限速依赖，能走到这里
	// 说明登录本身已经在用它，缺失是真配置问题，不该悄悄跳过限速直接放行到上游付费 API。
	if (!env.BLOG_SEARCH_SESSION_SECRET || !env.BLOG_SEARCH_KV) {
		return json({ error: 'not_configured' }, 503);
	}

	// 跟 /api/search 同一套登录门禁：只有能查语义检索的人，才能看这个功能自己的
	// 使用统计——不是"公开流量看板"的一部分，见文件头注释。
	const cookieValue = getCookie(request, COOKIE_NAME);
	const session = await verifySession(env.BLOG_SEARCH_SESSION_SECRET, cookieValue);
	if (!session.valid) {
		return json({ error: 'unauthorized' }, 401);
	}

	// FU-28：按会话限速，见文件头注释 + SESSION_RATE_LIMIT 常量处的说明。
	const sessionHash = await sha256Hex(cookieValue);
	const limit = await checkAndIncrement(env.BLOG_SEARCH_KV, sessionHash, SESSION_RATE_LIMIT);
	if (!limit.allowed) {
		return json({ error: 'too many requests, try again later' }, 429);
	}

	const token = env.CF_ANALYTICS_ENGINE_TOKEN || env.CF_ANALYTICS_TOKEN;
	const stats = await fetchSearchStats(token, env.CF_ACCOUNT_TAG || DEFAULT_ACCOUNT_TAG);
	return json(stats, 200);
}
