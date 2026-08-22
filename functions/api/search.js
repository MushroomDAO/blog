/**
 * POST /api/search
 *
 * T1.3.3：向量检索这一路。query → bge-m3 embedding → Vectorize top-K → 按 article_id
 * 聚合去重（每篇只保留分数最高的一个 chunk）→ 用 Vectorize 自身余弦相似度下限过滤掉
 * 明显不相关的候选 → 返回候选列表（可能为空）。
 *
 * T1.3.4：加了查询结果缓存（同一个 query 6 小时内重复搜直接吐缓存，跳过计费调用）+
 * 按 IP/会话的双重限速（T1.3.3 已做，T1.3.4 认领"简单限速"/"常见查询缓存"这两项
 * 开发范围，"降级"体现在 search.astro 前端、"不记录原始查询"通过缓存 key 用哈希而非
 * 明文满足，见 docs/agent/tasks.md T1.3.4）。
 *
 * 明确不做（见 docs/agent/tasks.md T1.3.3、docs/agent/spec.md §检索融合）：
 * - 不做关键词+向量的 RRF 融合——Pagefind 是纯浏览器端 JS，Worker 调不了，融合发生在
 *   `/search` 页面的浏览器 JS 里（这个端点只负责吐出向量这一路的候选）
 * - 不做"两路都没有靠谱结果 → 无把握不返回"的最终判断——那个判断需要同时看 Pagefind
 *   自己的信号，只能在浏览器端做；本端点只对自己这一路的绝对信号（余弦相似度）把关
 * - 不接 reranker（Phase 2 可选，T1.4.4）
 *
 * 需要的 Cloudflare 绑定（wrangler.toml）：
 *   BLOG_SEARCH_KV       必需——限速计数器用，跟 T1.3.5/T1.3.6 共用同一个 namespace
 *   BLOG_SEARCH_SESSION_SECRET  必需——验证登录 Cookie 用（复用 T1.3.6 的 auth.js）
 *   AI                   必需——Workers AI binding，query embedding 用 bge-m3
 *   VECTORIZE_INDEX      必需——T1.3.1 建的 blog-search-v1 索引
 * 任何一个缺失都 fail-closed 返回 503，不静默降级到"没有登录门禁"或"没有限速"的状态
 * （跟 search-auth.js 的 B2 修复同一个道理：这几个绑定共同构成这个端点唯一的成本/滥用
 * 防线，缺失时不该悄悄放行）。
 */

import { checkAndIncrement } from '../_lib/rate-limit.js';
import { COOKIE_NAME, getCookie, verifySession } from '../_lib/auth.js';

const MAX_QUERY_LENGTH = 400; // 见 spec.md §错误处理：query 长度上限 300-500 字符
const MAX_BODY_BYTES = 4096; // 正常请求体是 {"query": "<=400 字符"}，几百字节顶天
const TOP_K = 20; // 从 Vectorize 拿的候选 chunk 数，聚合去重之前
const MAX_RESULTS = 10; // 聚合去重、过滤之后最多返回的文章数
// 阈值刻意设得宽松：semantic-search/eval/vector-comparison-report.md 的实测数据显示，
// 24 条查询里所有 top5 结果的最低分是 0.401（bge-m3 在这批语料下余弦相似度的分布本身
// 比较"压缩"），且报告明确指出单靠这个分数分不清"该拒的负样本"和"该留的真命中"
// （"菜谱"/"育儿"两个负样本的最高分 0.4697/0.4794，跟真实相关查询的分数区间有重叠）。
// 这个端点只负责过滤掉分数明显低于"任何查询的 top5 都不会低到这里"的那一截，真正的
// 精确度判断交给前端结合 Pagefind 信号一起做（见 spec.md §检索融合第 4 点）。
const SIMILARITY_THRESHOLD = 0.4;
// 搜索限速比登录限速宽松得多——已登录用户正常使用会连续搜多次，5 分钟 30 次对真实使用
// 绰绰有余。按 IP 限速能挡住"单一来源脚本疯狂调用"，但挡不住"泄露的 Cookie 换着 IP 打"——
// 见下面 SESSION_RATE_LIMIT 的注释。
const IP_RATE_LIMIT = { prefix: 'searchlimit:', windowSeconds: 5 * 60, maxAttempts: 30 };
// 修正（T1.3.3 自审对抗式 review 抓到的真实问题）：只按 IP 限速时，一个泄露的登录 Cookie
// （60 天有效期，本项目明确不做撤销/登出接口，见 T1.3.6"明确不做"）换着 IP/代理打就能
// 绕过限速——按 IP 算的话理论上限是每 IP 每 5 分钟 30 次，但换 N 个 IP 就是 N 倍，Cookie
// 本身完全没有总量上限，而每次调用都是计费的 Workers AI + Vectorize 请求。加一个按会话
// （登录 Cookie 值的哈希，不是明文，避免把会话 token 原样存进 KV key）算的限速，跟 IP
// 限速同时生效（两个都必须通过）——这样不管换多少个 IP，同一个泄露的 Cookie 在同一个
// 5 分钟窗口内最多也只能打这么多次，把"泄露单个 Cookie 的最坏成本"钉死在一个可预期范围，
// 不再随攻击者能换多少个 IP 线性增长。
const SESSION_RATE_LIMIT = { prefix: 'searchsession:', windowSeconds: 5 * 60, maxAttempts: 30 };
// T1.3.4：常见查询缓存。同一个 query 字符串在 TTL 内重复搜，直接把上次算好的结果吐回去，
// 完全跳过计费的 Workers AI embedding + Vectorize 查询。6 小时是"结果不会太快过期、又能
// 覆盖住同一天内的重复搜索"之间的折中——语义检索结果对内容更新没有那么敏感（不像关键词
// 命中那样一字不差），文章更新频率也是以天为单位，6 小时的陈旧度可以接受。缓存 key 用
// 查询文本的哈希（trim+小写归一化后），不是明文——跟"不记录用户原始查询原文"这条要求
// 一致（见 tasks.md T1.3.4"开发范围"），缓存值本身也只是文章标题/链接/摘录，不含查询词。
const QUERY_CACHE_TTL_SECONDS = 6 * 60 * 60;

function jsonResponse(body, status) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' },
	});
}

async function sha256Hex(text) {
	const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
	return Array.from(new Uint8Array(digest))
		.map((b) => b.toString(16).padStart(2, '0'))
		.join('');
}

async function hashSessionCookie(cookieValue) {
	return sha256Hex(cookieValue);
}

async function queryCacheKey(query) {
	return `searchcache:${await sha256Hex(query.trim().toLowerCase())}`;
}

export async function onRequestPost(context) {
	const { request, env } = context;

	if (!env.BLOG_SEARCH_SESSION_SECRET || !env.BLOG_SEARCH_KV || !env.AI || !env.VECTORIZE_INDEX) {
		return jsonResponse({ error: 'search not configured' }, 503);
	}

	// 登录门禁先于其他任何处理——没有合法 Cookie 的请求不应该消耗限速额度、
	// 更不应该走到 embedding/Vectorize 这些计费调用
	const cookieValue = getCookie(request, COOKIE_NAME);
	const session = await verifySession(env.BLOG_SEARCH_SESSION_SECRET, cookieValue);
	if (!session.valid) {
		return jsonResponse({ error: 'login required' }, 401);
	}

	// 跟 search-auth.js 同样的教训（PR#48 round 2）：request.json() 不检查 Content-Type，
	// 单靠"能不能解析成 JSON"挡不住 Content-Type: text/plain 但 body 恰好合法的请求
	const contentType = (request.headers.get('Content-Type') || '').split(';')[0].trim().toLowerCase();
	if (contentType !== 'application/json') {
		return jsonResponse({ error: 'invalid request body' }, 400);
	}

	// 修正（T1.3.3 自审对抗式 review 抓到的真实问题）：Content-Length 是请求方自己声明的，
	// 不保证如实——chunked encoding 或者干脆撒谎的 Content-Length 都能让声明值小于实际
	// body，原来只查这个 header 就放行到 request.json() 解析，等于这道体积上限形同虚设。
	// 现在先把 body 读成文本、量实际字节数，量完再解析，两步都做，不再只信请求头。
	const contentLength = Number(request.headers.get('Content-Length') || 0);
	if (contentLength > MAX_BODY_BYTES) {
		return jsonResponse({ error: 'request body too large' }, 413);
	}

	let bodyText;
	try {
		bodyText = await request.text();
	} catch {
		return jsonResponse({ error: 'invalid request body' }, 400);
	}
	if (new TextEncoder().encode(bodyText).length > MAX_BODY_BYTES) {
		return jsonResponse({ error: 'request body too large' }, 413);
	}

	let body;
	try {
		body = JSON.parse(bodyText);
	} catch {
		return jsonResponse({ error: 'invalid request body' }, 400);
	}

	const query = body && typeof body.query === 'string' ? body.query.trim() : '';
	if (!query || query.length > MAX_QUERY_LENGTH) {
		return jsonResponse({ error: 'invalid query' }, 400);
	}

	// 缓存命中直接返回——不计入限速、不调 AI/Vectorize。缓存本身只是加速+省钱，不是
	// 安全边界，KV 读取失败时降级成"当作没命中"，走下面的正常流程，不是 fail-closed 503
	// （跟必需 binding 缺失时的 503 是两回事：那是安全防线缺失，这只是优化没生效）。
	const cacheKey = await queryCacheKey(query);
	try {
		const cached = await env.BLOG_SEARCH_KV.get(cacheKey);
		if (cached) {
			return jsonResponse({ results: JSON.parse(cached) }, 200);
		}
	} catch {
		// 忽略——缓存读取/解析失败不影响功能，继续走下面的正常查询流程
	}

	const ip = request.headers.get('CF-Connecting-IP');
	if (!ip) {
		return jsonResponse({ error: 'search not configured' }, 503);
	}
	const [ipLimit, sessionLimit] = await Promise.all([
		checkAndIncrement(env.BLOG_SEARCH_KV, ip, IP_RATE_LIMIT),
		checkAndIncrement(env.BLOG_SEARCH_KV, await hashSessionCookie(cookieValue), SESSION_RATE_LIMIT),
	]);
	if (!ipLimit.allowed || !sessionLimit.allowed) {
		return jsonResponse({ error: 'too many requests, try again later' }, 429);
	}

	let queryVector;
	try {
		const embedResult = await env.AI.run('@cf/baai/bge-m3', { text: [query] });
		queryVector = embedResult && embedResult.data && embedResult.data[0];
		if (!Array.isArray(queryVector)) {
			throw new Error('embedding response missing data[0]');
		}
	} catch {
		return jsonResponse({ error: 'search temporarily unavailable' }, 503);
	}

	let matches;
	try {
		const result = await env.VECTORIZE_INDEX.query(queryVector, { topK: TOP_K, returnMetadata: 'all' });
		matches = result && Array.isArray(result.matches) ? result.matches : [];
	} catch {
		return jsonResponse({ error: 'search temporarily unavailable' }, 503);
	}

	// 按 article_id 聚合去重：向量相似度是 chunk 级的，不等于文章相关性；一篇文章可能有
	// 多个 chunk 命中，只保留分数最高的那个作为这篇文章的代表分数/摘录。
	// 修正（T1.3.3 自审对抗式 review 指出的边角情况）：`match.score` 理论上不该是非数字，
	// 但 Vectorize 返回脏数据时不该让整个请求炸掉或者产生 NaN 比较的诡异行为——非有限数
	// 一律当成"没有可用分数"跳过，跟 article_id 缺失同等对待。
	const bestByArticle = new Map();
	for (const match of matches) {
		const metadata = match && match.metadata;
		const articleId = metadata && metadata.article_id;
		if (!articleId || !Number.isFinite(match.score)) continue;
		const existing = bestByArticle.get(articleId);
		if (!existing || match.score > existing.score) {
			bestByArticle.set(articleId, match);
		}
	}

	const results = Array.from(bestByArticle.values())
		.filter((match) => match.score >= SIMILARITY_THRESHOLD)
		.sort((a, b) => b.score - a.score)
		.slice(0, MAX_RESULTS)
		.map((match) => ({
			article_id: match.metadata.article_id,
			title: match.metadata.title ?? '',
			url: match.metadata.url ?? '',
			language: match.metadata.language ?? '',
			excerpt: match.metadata.excerpt ?? '',
			score: match.score,
		}));

	// 写缓存是 best-effort：失败不影响这次请求本身返回正确结果，只是下次同样的查询
	// 又要重新走一遍计费调用
	try {
		await env.BLOG_SEARCH_KV.put(cacheKey, JSON.stringify(results), {
			expirationTtl: QUERY_CACHE_TTL_SECONDS,
		});
	} catch {
		// 忽略
	}

	return jsonResponse({ results }, 200);
}

export async function onRequestGet() {
	return jsonResponse({ error: 'method not allowed' }, 405);
}
