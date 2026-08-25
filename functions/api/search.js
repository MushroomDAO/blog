/**
 * POST /api/search
 *
 * T1.3.3：向量检索这一路。query → bge-m3 embedding → Vectorize top-K → 按 article_id
 * 聚合去重（每篇只保留分数最高的一个 chunk）→ 用 Vectorize 自身余弦相似度下限过滤掉
 * 明显不相关的候选 → 返回候选列表（可能为空）。
 *
 * T1.3.4：加了查询结果缓存（同一个 query 6 小时内重复搜直接吐缓存，跳过计费调用）+
 * 按 IP 限速（T1.3.3 已做，T1.3.4 认领"简单限速"/"常见查询缓存"这两项开发范围，
 * "降级"体现在 search.astro 前端、"不记录原始查询"通过缓存 key 用哈希而非明文满足，
 * 见 docs/agent/tasks.md T1.3.4——**当时还有按会话的第二道限速，2026-08-23 去掉
 * 登录门禁时一并移除，见下方说明**）。
 *
 * **2026-08-23 去掉登录门禁**：T1.3.6 建这道密码墙的理由是"怕被刷 Workers AI/Vectorize
 * 计费"（见 architecture.md 核心判断 7）。**修正（round 2 review 用 7 种威胁模型实测
 * 推翻了这里原来的说法）**：原注释说"真正挡刷量的是下面这道按 IP 的限速，不是登录本身"——
 * 这不成立。实测按 IP 轮换（每个源地址只用一次）3000/3000 请求全部放行、0 次 429；
 * 并发请求也因为 checkAndIncrement 的 KV read-modify-write 非原子（FU-11）全部放行；
 * 跨 3 个 Cloudflare PoP 因为限速计数器互相看不见（FU-6）实际生效倍数变成 3 倍。
 * **真正把流量压到接近零的是密码墙本身**——这道按 IP 的限速只挡得住"单一来源、顺序、
 * 不换 IP"这种最不用脑子的滥用，FU-6/FU-11 原来"单一共享密码+低访问量场景下可接受"
 * 的风险接受结论，前提正是本次去掉的密码墙，需要重新评估（已在 followups.md 更新）。
 * 站长知悉这一点后仍然决定公开语义检索（跟一直公开的 Pagefind 关键词搜索对齐）——
 * 按实测成本量级核算（bge-m3 每天 1 万 neurons 免费额度、Vectorize 每月 5000 万
 * queried dimensions 免费额度），即使是百万级请求的滥用洪水，账单量级在几十美元，
 * 不是"会破产"级别的风险，只是这个端点从此不再裸奔在几乎为零的真实流量假设上。
 * **同一套登录系统（`_lib/auth.js`/`search-auth.js`）仍然保留**，只是不再是这个
 * 端点的门禁——现在专门用来给"搜索使用统计"查看页（`/api/search-analytics.json`）和未来
 * 可能做的 AI 对话功能把关，那两个的计费/滥用画像跟公开检索完全不是一回事（对话是生成式
 * LLM 调用，单次成本比一次 embedding+向量检索高得多，必须继续要密码）。
 *
 * 明确不做（见 docs/agent/tasks.md T1.3.3、docs/agent/spec.md §检索融合）：
 * - 不做关键词+向量的 RRF 融合——Pagefind 是纯浏览器端 JS，Worker 调不了，融合发生在
 *   `/search` 页面的浏览器 JS 里（这个端点只负责吐出向量这一路的候选）
 * - 不做"两路都没有靠谱结果 → 无把握不返回"的最终判断——那个判断需要同时看 Pagefind
 *   自己的信号，只能在浏览器端做；本端点只对自己这一路的绝对信号（余弦相似度）把关
 * - 不接 reranker（Phase 2 可选，T1.4.4）
 *
 * 需要的 Cloudflare 绑定（wrangler.toml）：
 *   BLOG_SEARCH_KV       必需——限速计数器/查询缓存用，跟 T1.3.5/T1.3.6 共用同一个 namespace
 *   AI                   必需——Workers AI binding，query embedding 用 bge-m3
 *   VECTORIZE_INDEX      必需——T1.3.1 建的 blog-search-v1 索引
 * 任何一个缺失都 fail-closed 返回 503，不静默降级到"没有限速"的状态（这几个绑定共同构成
 * 这个端点唯一的成本/滥用防线，缺失时不该悄悄放行）。
 */

import { checkAndIncrement } from '../_lib/rate-limit.js';

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
// 按 IP 限速——5 分钟 30 次对真实使用绰绰有余，能挡住"单一来源脚本疯狂调用"。
// 去掉登录门禁之后（见文件头 2026-08-23 说明），这是这个端点唯一的滥用防线，不再有
// 按会话（登录 Cookie）的第二道限速——那道原本存在的理由是"防泄露的登录 Cookie 换 IP
// 绕过限速"，登录门禁本身都不要了，自然也没有会话可言。
const IP_RATE_LIMIT = { prefix: 'searchlimit:', windowSeconds: 5 * 60, maxAttempts: 30 };
// T1.3.4：常见查询缓存。同一个 query 字符串在 TTL 内重复搜，直接把上次算好的结果吐回去，
// 跳过计费的 Workers AI embedding + Vectorize 查询（但仍然计入限速，见下面限速检查的位置）。
// 6 小时是"省下重复查询的计费调用"和"不要让搜索结果陈旧太久"之间的折中——不是按"文章多久
// 更新一次"来算的：这个仓库实际发布节奏很密（单日发布过 14 篇），真正约束新鲜度的是
// T1.4.1（发布→增量索引 hook，目前还是 BACKLOG，未上线前索引本来就只有跑
// build-vectorize-index.py 那一刻的新鲜度，比这里的 6 小时还粗）；T1.4.1 上线后，这个
// TTL 会成为"重复搜同一个词"这条窄路径上新内容可见的新增延迟，到时候需要重新评估
// （记入 followups）。缓存 key 用查询文本的哈希（trim+小写归一化后），不是明文——跟
// "不记录用户原始查询原文"这条要求一致（见 tasks.md T1.3.4"开发范围"），缓存值本身
// 也只是文章标题/链接/摘录，不含查询词。
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

// FU-25：搜索统计以前存的是**明文** IP。这道端点 2026-08-23 去掉登录门禁后（见文件头
// 说明），触发这条日志写入的从"仅站长自己"变成"任何匿名访客"，隐私前提已经变了——
// 用带密钥的 HMAC-SHA256 而不是裸哈希：IPv4 地址空间只有 43 亿种，裸 SHA-256(ip) 几秒
// 内就能建完整张彩虹表反查回真实 IP，等于没保护；带密钥且密钥不落库/不随数据集本身
// 泄漏的 HMAC，在密钥不泄漏的前提下才是真正不可逆的。
// 密钥固定复用（不像"每日轮换的盐"那种方案）是刻意的：同一个真实访客每次都映射到
// 同一个哈希值，count(DISTINCT index1) 算出的 uniqueIps 才有意义——按天轮换的盐会
// 把跨天访问的同一个人拆成"好几个不同 IP"，把这个统计指标本身做坏。复用
// BLOG_SEARCH_SESSION_SECRET（登录 Cookie 签名用的同一把密钥）而不是新开一个专用
// secret：消息里加了域分隔前缀（"search-analytics-ip:"），跟签会话 Cookie 是两个不同
// 的 HMAC 输入，不会互相碰撞/推导，避免为这一个小功能单独引入一个还需要用户手动
// wrangler secret put 的新密钥、阻塞这条 followup 的落地。
// 密钥缺失（BLOG_SEARCH_SESSION_SECRET 未配置——这个端点不像 search-analytics.json.js
// 那样把它列为必需绑定）时不退化成弱哈希：直接不写 index1（传空字符串），宁可这次
// 抽样丢一个维度，也不要用一个可预测的固定字符串当 HMAC key，那样跟没加密钥等价。
async function hashIp(secret, ip) {
	if (!secret || !ip) return '';
	const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
	const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`search-analytics-ip:${ip}`));
	return Array.from(new Uint8Array(sig))
		.map((b) => b.toString(16).padStart(2, '0'))
		.join('')
		.slice(0, 32); // 128 bit，个人博客量级的访客数远不足以在这个长度上产生碰撞，比完整 64 字节紧凑
}

// 搜索使用统计（用户明确要求：想看上线后有多少人在用、都搜了什么）。用 Workers
// Analytics Engine 而不是复用 BLOG_SEARCH_KV：这个 KV namespace 已经同时扛着登录
// 限速/搜索限速/缓存/manifest 四种用途（见 FU-18），事件日志这种「只写不太读、
// 按时间序列查」的负载不该再往里堆，Analytics Engine 是 Cloudflare 专门为这类场景
// 做的产品——写入不占 KV 配额，按 SQL 查，不需要手动清理 TTL。
// 注意：这里存的是归一化后的**明文** query（不是哈希）——跟 T1.3.4 缓存 key 刻意
// 用哈希"不记录用户原始查询原文"的设计不是同一个诉求：那是缓存层面尽量少存不必要的
// 明文，这里是站长本人明确要求要能看到"搜了什么"这个可读的运营数据，Analytics
// Engine 数据集本身不对外公开、只有账号持有者能查（见 functions/api/analytics.json.js
// 的读取端）。query 本身不受 FU-25 影响——那条 followup 的隐私杠杆分析明确指出"谁"
// （IP）才是能精确定位到具体某个人的维度，查询词本身的风险由站长自己权衡过、要保留
// 可读性，这里不改。
// writeDataPoint 是同步调用（Cloudflare 在后台异步落盘，不阻塞这次响应）；这里额外
// await 一次 HMAC 计算（亚毫秒级），比 writeDataPoint 本身晚不了多少。binding 缺失/
// HMAC 计算出错时直接抛异常，包一层 try/catch 让统计功能本身的故障/未配置永远不影响
// 搜索请求本身——这是运营可视化数据，不是安全控制，没有必要 fail-closed。
async function logSearchEvent(env, { ip, query, resultCount, cacheHit }) {
	try {
		const hashedIp = await hashIp(env.BLOG_SEARCH_SESSION_SECRET, ip);
		env.SEARCH_ANALYTICS?.writeDataPoint({
			indexes: [hashedIp], // index1：HMAC(密钥, IP) 而不是明文 IP（FU-25），按访客分组/抽样用
			blobs: [query], // blob1：归一化后的查询词原文
			doubles: [resultCount, cacheHit ? 1 : 0], // double1：返回结果数，double2：是否命中缓存
		});
	} catch {
		// 忽略——统计失败不该影响搜索功能本身
	}
}

// 修正（FU-16 round 2 review 抓到的真实 bug）：原来 normalizeQuery 只用在算缓存 key，
// 传给 env.AI.run() 的还是原始未归一化的 query——这不是"多几次缓存未命中"那么无害：
// 两个经归一化后判定"等价"的查询串（比如全角"ＰＡＧＥＦＩＮＤ"和半角"pagefind"），
// 只有先到的那个真正拿自己的原文去 embedding，后到的那个直接命中缓存，拿到的是
// **先到者原文**算出来的向量结果——bge-m3 对全角/半角拉丁字符给出的向量有实打实的
// 差异，判成"同一条缓存"就是在断言这两个输入对 embedding 也等价，而下游根本不认这个
// 等价。修法：归一化只在解析请求体这一处做一次，之后无论是算缓存 key 还是传给
// env.AI.run()，用的都是同一个归一化后的字符串，两边不会再割裂。
function normalizeQuery(query) {
	return query.trim().toLowerCase().normalize('NFKC').replace(/\s+/g, ' ');
}

// v2：round 2 review 指出的真实问题——这一轮改了 normalizeQuery 的施加时机（同一个
// 归一化字符串现在既算 key 也喂给 embedding），旧版本按不同规则算出来的缓存条目如果
// 还活着（最长 6 小时 TTL），会跟新规则的条目混在一起。加个版本段，旧 key 自然过期后
// 不会再被新代码误读，不需要手动清理。以后再改归一化规则/阈值/TOP_K 这类影响缓存
// 内容形状的常量时，也应该顺手把这个版本号往上提一格。
async function queryCacheKey(normalizedQuery) {
	return `searchcache:v2:${await sha256Hex(normalizedQuery)}`;
}

export async function onRequestPost(context) {
	const { request, env } = context;

	if (!env.BLOG_SEARCH_KV || !env.AI || !env.VECTORIZE_INDEX) {
		return jsonResponse({ error: 'search not configured' }, 503);
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

	// 归一化在这里做一次——下面无论是算缓存 key 还是传给 env.AI.run() 做 embedding，
	// 用的都是这同一个字符串，两处不会再各自处理出不同的输入（见 normalizeQuery 注释）。
	const query = body && typeof body.query === 'string' ? normalizeQuery(body.query) : '';
	if (!query || query.length > MAX_QUERY_LENGTH) {
		return jsonResponse({ error: 'invalid query' }, 400);
	}

	const ip = request.headers.get('CF-Connecting-IP');
	if (!ip) {
		return jsonResponse({ error: 'search not configured' }, 503);
	}
	// 修正（T1.3.4 自审对抗式 review 抓到的真实问题）：限速原来放在缓存检查之后，缓存命中
	// 直接 return，完全不计入限速——理由是"缓存读取不花计费的 AI/Vectorize 调用"，但这个
	// KV namespace 同时也是 T1.3.6 登录限速器在用的（见文件头注释），不计限速的缓存读流量
	// 一样能把这个共享 namespace 的 KV 读写配额打满，变成一个新的拒绝服务面——不是"省钱"
	// 那个威胁模型要挡的东西，是完全不同的一种滥用。改成限速先做，缓存检查在后：这样不管
	// 命中缓存与否，同一个 IP 在窗口内的总请求量都被同一套限速盖住，缓存依然省掉
	// AI/Vectorize 这两个真正计费的调用，只是不再对"请求本身要不要计次"免疫。
	const ipLimit = await checkAndIncrement(env.BLOG_SEARCH_KV, ip, IP_RATE_LIMIT);
	if (!ipLimit.allowed) {
		return jsonResponse({ error: 'too many requests, try again later' }, 429);
	}

	// 缓存命中直接返回，跳过计费的 AI/Vectorize 调用——但上面的限速已经计过数了。缓存本身
	// 只是加速+省钱，不是安全边界，KV 读取失败时降级成"当作没命中"，走下面的正常查询流程，
	// 不是 fail-closed 503（跟必需 binding 缺失时的 503 是两回事：那是安全防线缺失，
	// 这只是优化没生效）。
	const cacheKey = await queryCacheKey(query);
	try {
		const cached = await env.BLOG_SEARCH_KV.get(cacheKey);
		if (cached) {
			const parsed = JSON.parse(cached);
			// 修正（round 2 review 指出的真实问题）：不校验解析出来的形状就直接透传，
			// KV 里万一是字符串/null/嵌套对象（不该发生，但脏数据不该让整个请求炸掉）
			// 会原样 200 返回——前端 searchVectorRanked 是 Promise.all 里唯一没有
			// .catch 的一支，.map 一抛异常会把整个合并搜索打死，连 Pagefind 那半
			// 本来能成功的结果都一起没了。非数组就当作没命中，走下面重新计算。
			if (Array.isArray(parsed)) {
				// logSearchEvent 现在是 async（FU-25 加了一次 HMAC 计算）——必须 await 完
				// 再返回响应，否则 hashIp 里的 crypto.subtle.sign 这个 Promise 可能在
				// Response 已经发出去之后才继续执行，Cloudflare Workers 不保证这种脱离
				// 请求生命周期的悬空 Promise 会被跑完（跟 writeDataPoint 本身"同步调用，
				// 后台异步落盘"不是一回事——那是 Cloudflare 平台对这一个 API 的保证，不
				// 延伸到我们自己另起的 HMAC Promise）。
				await logSearchEvent(env, { ip, query, resultCount: parsed.length, cacheHit: true });
				return jsonResponse({ results: parsed }, 200);
			}
		}
	} catch {
		// 忽略——缓存读取/解析失败不影响功能，继续走下面的正常查询流程
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

	await logSearchEvent(env, { ip, query, resultCount: results.length, cacheHit: false });
	return jsonResponse({ results }, 200);
}

export async function onRequestGet() {
	return jsonResponse({ error: 'method not allowed' }, 405);
}
