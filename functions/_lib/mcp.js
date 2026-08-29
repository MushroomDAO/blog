/**
 * MCP（Model Context Protocol）server 的纯逻辑部分——不碰 request/env，只接受
 *已解析好的 JSON-RPC 请求对象和一个"按需加载文章"的回调，方便单测直接注入
 * fixture。HTTP 层（Content-Type 校验、限速、SSE）在 functions/api/mcp.js。
 *
 * 协议版本：声明 2025-11-25（不是最新的 2026-07-28）——这是刻意的版本选择，
 * 不是没跟上：2026-07-28 把 initialize/initialized 握手整个去掉了，改成
 * 无状态的逐请求 `_meta` 协议协商 + `server/discover` + `subscriptions/listen`
 * 取代 `resources/subscribe`（见 https://modelcontextprotocol.io/specification/
 * 2026-07-28/changelog）。本 server 实现的是 initialize 握手 + resources/
 * subscribe 这一套，如果同时对外声明 2026-07-28，就是自己承认的版本号和自己
 * 实际实现的方法集对不上——那才是真正的协议错误（round 1 review 抓到的问题）。
 * 2025-11-25 是这套方法集最后一个仍然有效的版本号，声明它是诚实的。
 * `server/discover` 单独加了一个方法（见下面），不依赖 initialize 握手，
 * 好让 2026-07-28 感知的新客户端至少能拿到一个诚实的"我是 2025-11-25"回答，
 * 而不是 -32601 method not found。
 */

const PROTOCOL_VERSION = '2025-11-25';
const RESOURCE_URI = 'posts://latest';
const MAX_SEARCH_RESULTS = 20;
const DEFAULT_LIST_LIMIT = 10;
const MAX_LIST_LIMIT = 50;

const TOOL_DEFS = [
	{
		name: 'search_posts',
		description: '按关键词/标签/分类搜索博客文章，关键词匹配标题、摘要、标签和正文',
		inputSchema: {
			type: 'object',
			properties: {
				query: { type: 'string', description: '关键词，可选' },
				tag: { type: 'string', description: '按标签精确过滤，可选' },
				category: { type: 'string', description: '按分类精确过滤，可选' },
				limit: { type: 'number', description: `默认 ${MAX_SEARCH_RESULTS}` },
			},
		},
	},
	{
		name: 'get_post',
		description: '按文章 id 获取完整内容（标题、摘要、正文 markdown）',
		inputSchema: {
			type: 'object',
			properties: { id: { type: 'string' } },
			required: ['id'],
		},
	},
	{
		name: 'list_recent',
		description: '按发布时间倒序列出最近的文章',
		inputSchema: {
			type: 'object',
			properties: { limit: { type: 'number', description: `默认 ${DEFAULT_LIST_LIMIT}，上限 ${MAX_LIST_LIMIT}` } },
		},
	},
];

function jsonRpcError(id, code, message) {
	return { jsonrpc: '2.0', id: id ?? null, error: { code, message } };
}

function jsonRpcResult(id, result) {
	return { jsonrpc: '2.0', id: id ?? null, result };
}

function clampLimit(value, fallback, max) {
	const n = Number.isFinite(value) ? Math.floor(value) : fallback;
	return Math.max(1, Math.min(n, max));
}

function toolResultText(payload) {
	return { content: [{ type: 'text', text: JSON.stringify(payload) }] };
}

// round 1 review 指出 listRecent 不排序、依赖调用方传入已经按发布时间排好序的
// 数组——测试恰好用了一个"看起来排好了"的 fixture 顺序，掩盖了这个隐藏假设
// （见 mcp.test.js 的修正）。改成每次都显式按 pubDate 倒序排一次，不管调用方
// 传入的数组是不是已经排好，这个函数自己的输出永远是对的。
function sortByPubDateDesc(posts) {
	return [...posts].sort((a, b) => new Date(b.pubDate).valueOf() - new Date(a.pubDate).valueOf());
}

function searchPosts(posts, { query, tag, category, limit } = {}) {
	const normalizedQuery = typeof query === 'string' ? query.trim().toLowerCase() : '';
	const max = clampLimit(limit, MAX_SEARCH_RESULTS, MAX_SEARCH_RESULTS);

	const matches = sortByPubDateDesc(posts).filter((post) => {
		if (tag && !post.tags.includes(tag)) return false;
		if (category && post.category !== category) return false;
		if (!normalizedQuery) return true;
		const haystack = [post.title, post.titleEn, post.description, post.descriptionEn, ...post.tags, post.bodyMarkdown]
			.filter(Boolean)
			.join('\n')
			.toLowerCase();
		return haystack.includes(normalizedQuery);
	});

	return matches.slice(0, max).map(({ bodyMarkdown, ...summary }) => summary);
}

function getPost(posts, { id } = {}) {
	if (typeof id !== 'string' || !id) return null;
	return posts.find((post) => post.id === id) ?? null;
}

function listRecent(posts, { limit } = {}) {
	const max = clampLimit(limit, DEFAULT_LIST_LIMIT, MAX_LIST_LIMIT);
	return sortByPubDateDesc(posts)
		.slice(0, max)
		.map(({ bodyMarkdown, ...summary }) => summary);
}

function callTool(posts, name, args) {
	switch (name) {
		case 'search_posts':
			return toolResultText({ results: searchPosts(posts, args) });
		case 'get_post': {
			const post = getPost(posts, args);
			if (!post) return { ...toolResultText({ error: 'not found' }), isError: true };
			return toolResultText(post);
		}
		case 'list_recent':
			return toolResultText({ results: listRecent(posts, args) });
		default:
			return null;
	}
}

/**
 * 处理一个已解析的 JSON-RPC 请求对象，返回 JSON-RPC 响应对象（不序列化）。
 *
 * `loadPosts` 是一个 `() => Promise<Post[]>`，只有 `tools/call`/`resources/read`
 * 这类真正需要文章内容的方法才会调用它——`initialize`/`server/discover`/
 * `tools/list`/`resources/list`/`resources/subscribe`/`resources/unsubscribe`
 * 都不碰内容，不该白白拉一次几 MB 的索引（round 1 review Medium #6）。
 */
async function handleJsonRpc(request, loadPosts) {
	const { id = null, method, params } = request ?? {};
	const safeParams = params && typeof params === 'object' ? params : {};

	try {
		switch (method) {
			case 'initialize':
				return jsonRpcResult(id, {
					protocolVersion: PROTOCOL_VERSION,
					capabilities: { tools: {}, resources: { subscribe: true } },
					serverInfo: { name: 'mycelium-blog-agent-feed', version: '0.1.0' },
				});

			// 2026-07-28 规范要求每个 server 实现这个方法用于能力发现/版本协商，
			// 不依赖 initialize 握手（见文件头注释）。这里诚实回答"我支持
			// 2025-11-25"，不冒充支持最新版本。
			case 'server/discover':
				return jsonRpcResult(id, {
					protocolVersions: [PROTOCOL_VERSION],
					capabilities: { tools: {}, resources: { subscribe: true } },
					serverInfo: { name: 'mycelium-blog-agent-feed', version: '0.1.0' },
				});

			case 'tools/list':
				return jsonRpcResult(id, { tools: TOOL_DEFS });

			case 'tools/call': {
				if (typeof safeParams.name !== 'string' || !safeParams.name) {
					return jsonRpcError(id, -32602, 'missing tool name');
				}
				const args = safeParams.arguments && typeof safeParams.arguments === 'object' ? safeParams.arguments : {};
				const posts = await loadPosts();
				const result = callTool(posts, safeParams.name, args);
				if (!result) return jsonRpcError(id, -32602, `unknown tool: ${safeParams.name}`);
				return jsonRpcResult(id, result);
			}

			case 'resources/list':
				return jsonRpcResult(id, {
					resources: [
						{
							uri: RESOURCE_URI,
							name: 'Latest posts',
							description: '最近发布的文章列表，支持 resources/subscribe 订阅更新',
							mimeType: 'application/json',
						},
					],
				});

			case 'resources/read': {
				if (safeParams.uri !== RESOURCE_URI) return jsonRpcError(id, -32602, `unknown resource: ${safeParams.uri}`);
				const posts = await loadPosts();
				return jsonRpcResult(id, {
					contents: [
						{
							uri: RESOURCE_URI,
							mimeType: 'application/json',
							text: JSON.stringify({ results: listRecent(posts, {}) }),
						},
					],
				});
			}

			case 'resources/subscribe':
				if (safeParams.uri !== RESOURCE_URI) return jsonRpcError(id, -32602, `unknown resource: ${safeParams.uri}`);
				// 实际推送在 functions/api/mcp.js 的 SSE 循环里做（无状态轮询式推送，
				// 见 agent-feed/PLAN.md）；这里只确认订阅的 uri 有效，不需要文章内容。
				return jsonRpcResult(id, {});

			case 'resources/unsubscribe':
				return jsonRpcResult(id, {});

			default:
				return jsonRpcError(id, -32601, `method not found: ${method}`);
		}
	} catch {
		// round 1 review Medium #8：畸形参数（比如 params.arguments 是字符串而不是
		// 对象）不该让整个 Worker 请求裸炸成 500——统一兜底成标准 JSON-RPC 内部错误。
		return jsonRpcError(id, -32603, 'internal error');
	}
}

function buildResourceUpdatedNotification() {
	return { jsonrpc: '2.0', method: 'notifications/resources/updated', params: { uri: RESOURCE_URI } };
}

export {
	RESOURCE_URI,
	PROTOCOL_VERSION,
	handleJsonRpc,
	buildResourceUpdatedNotification,
	searchPosts,
	getPost,
	listRecent,
};
