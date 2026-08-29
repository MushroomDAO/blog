/**
 * POST/GET /api/mcp — Agent Feed 的 MCP server 入口（Streamable HTTP transport,
 * 协议版本 2025-11-25，见 functions/_lib/mcp.js 文件头关于版本选择的说明）。
 *
 * 数据来源：这里跑在 Cloudflare Pages Functions 的请求期 Workers runtime，读不到
 * astro:content——同源 fetch 构建产物 /agent-feed-index.json（完整内容，
 * src/pages/agent-feed-index.json.ts 生成）或 /agent-feed-meta.json（几十字节的
 * revision 摘要，src/pages/agent-feed-meta.json.ts 生成），不需要额外 KV/绑定。
 *
 * POST：标准 JSON-RPC 请求/响应，方法分发逻辑在 functions/_lib/mcp.js（跟这里的
 * HTTP 关注点——Content-Type 校验、body 体积上限、限速——分开，方便纯逻辑单测）。
 * 只有真正需要文章内容的方法（tools/call、resources/read）才会触发
 * fetchFullIndex，其余方法（initialize/server/discover/tools/list/resources/
 * list/resources/subscribe）不碰索引（round 1 review Medium #6）。
 *
 * GET：当 `Accept: text/event-stream` 且 `?subscribe=posts://latest` 时，走
 * SSE 承接 MCP 的 resources/subscribe。用"无状态轮询式推送"——每 20s 重新同源
 * fetch 一次 agent-feed-meta.json（不是完整索引，round 1 review High #4：完整
 * 索引每连接 25 次轮询约解码 200MB，是明显的资源放大）比较 revision 是否变化，
 * 不引入 Durable Objects/WebSocket 维护跨请求状态——这是 MCP 生态对 serverless/
 * 边缘场景的推荐做法（见 agent-feed/PLAN.md 的依据链接），不是简化偷懒。单次
 * 连接有执行时长上限，客户端要自己处理断线重连。
 */

import { checkAndIncrement } from '../_lib/rate-limit.js';
import { buildResourceUpdatedNotification, handleJsonRpc, RESOURCE_URI } from '../_lib/mcp.js';

const MAX_BODY_BYTES = 8192; // 正常 JSON-RPC 请求（含 tools/call 参数）几百字节顶天
// 这个端点不调用任何计费的 AI/Vectorize，内容本身跟 /blog 页面一样公开，限速
// 只是防止被当脚本刷爆而不是防成本——但仍然消耗 CPU/子请求，round 1 review High
// #5 指出"KV/IP 缺失时静默放行"本身就是个洞，所以缺失时改成 fail-closed。
const IP_RATE_LIMIT = { prefix: 'agentfeed:', windowSeconds: 5 * 60, maxAttempts: 60 };
const SSE_RATE_LIMIT = { prefix: 'agentfeedsse:', windowSeconds: 5 * 60, maxAttempts: 10 };
const POLL_INTERVAL_MS = 20_000;
const MAX_SSE_TICKS = 25; // 上限约 500s，避免单个连接无限占用

function jsonResponse(body, status = 200) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' },
	});
}

// round 1 review High #3：原来先看 Content-Length（请求方自己声明的，chunked
// encoding 或者撒谎的值都绕得过去）再整体 request.text()——恶意/畸形客户端能
// 逼这里在拒绝之前把整个超大 body 读进内存。改成边读边数字节，一超过上限立刻
// cancel 掉底层 reader，不会因为一个几十 MB 的 body 真的把它缓冲完。
async function readBoundedBody(request, maxBytes) {
	const reader = request.body?.getReader();
	if (!reader) return '';

	const chunks = [];
	let total = 0;
	for (;;) {
		const { done, value } = await reader.read();
		if (done) break;
		total += value.byteLength;
		if (total > maxBytes) {
			await reader.cancel();
			throw new Error('request body too large');
		}
		chunks.push(value);
	}

	const buffer = new Uint8Array(total);
	let offset = 0;
	for (const chunk of chunks) {
		buffer.set(chunk, offset);
		offset += chunk.byteLength;
	}
	return new TextDecoder().decode(buffer);
}

async function fetchFullIndex(request) {
	const indexUrl = new URL('/agent-feed-index.json', request.url);
	const res = await fetch(indexUrl);
	if (!res.ok) throw new Error(`index fetch failed: ${res.status}`);
	const { posts } = await res.json();
	return posts;
}

async function fetchMeta(request) {
	const metaUrl = new URL('/agent-feed-meta.json', request.url);
	const res = await fetch(metaUrl);
	if (!res.ok) throw new Error(`meta fetch failed: ${res.status}`);
	return res.json();
}

// POST 和 GET 共用：按 IP 限速，KV/IP 缺失一律 503 fail-closed——跟
// functions/api/search.js 对必需依赖缺失时的处理约定一致（那边是为了不让缺失
// 状态悄悄放行到无限次计费调用，这里是不让它悄悄放行到无限次 CPU/子请求消耗）。
async function enforceRateLimit(request, env, limitConfig) {
	if (!env.BLOG_SEARCH_KV) return { ok: false, status: 503, message: 'rate limiting not configured' };
	const ip = request.headers.get('CF-Connecting-IP');
	if (!ip) return { ok: false, status: 503, message: 'agent feed not configured' };
	const limit = await checkAndIncrement(env.BLOG_SEARCH_KV, ip, limitConfig);
	if (!limit.allowed) return { ok: false, status: 429, message: 'too many requests, try again later' };
	return { ok: true };
}

export async function onRequestPost(context) {
	const { request, env } = context;

	const contentType = (request.headers.get('Content-Type') || '').split(';')[0].trim().toLowerCase();
	if (contentType !== 'application/json') {
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'invalid request body' } }, 400);
	}

	const rate = await enforceRateLimit(request, env, IP_RATE_LIMIT);
	if (!rate.ok) {
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32000, message: rate.message } }, rate.status);
	}

	let bodyText;
	try {
		bodyText = await readBoundedBody(request, MAX_BODY_BYTES);
	} catch {
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'request body too large' } }, 413);
	}

	let rpcRequest;
	try {
		rpcRequest = JSON.parse(bodyText);
	} catch {
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'parse error' } }, 400);
	}

	// JSON-RPC 2.0：Notification 是"没有 id 字段"的请求，规范要求服务端不回响应体
	// （跟 id 为 null 的正常请求不是一回事——那种仍然要回）。round 1 review Medium #8
	// 指出原来的实现对这两者不做区分。
	const isNotification = rpcRequest && typeof rpcRequest === 'object' && !('id' in rpcRequest);

	const response = await handleJsonRpc(rpcRequest, () => fetchFullIndex(request));

	if (isNotification) return new Response(null, { status: 202 });

	// JSON-RPC 惯例：只要请求本身被正确接收、分发了，HTTP 状态就是 200——方法
	// 找不到/参数不对这类错误装在 JSON-RPC 的 error 字段里，不是 HTTP 层错误。
	return jsonResponse(response, 200);
}

export async function onRequestGet(context) {
	const { request, env } = context;
	const url = new URL(request.url);
	const accept = request.headers.get('Accept') || '';
	const subscribeUri = url.searchParams.get('subscribe');

	if (!accept.includes('text/event-stream') || subscribeUri !== RESOURCE_URI) {
		return jsonResponse({ error: 'method not allowed' }, 405);
	}

	const rate = await enforceRateLimit(request, env, SSE_RATE_LIMIT);
	if (!rate.ok) {
		return jsonResponse({ error: rate.message }, rate.status);
	}

	const encoder = new TextEncoder();
	let cancelled = false;

	const stream = new ReadableStream({
		async start(controller) {
			function send(event) {
				controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
			}

			let lastRevision = '';
			try {
				lastRevision = (await fetchMeta(request)).revision ?? '';
			} catch {
				// 索引拿不到就先不推初始状态，后面轮询继续尝试
			}
			send({ jsonrpc: '2.0', method: 'notifications/subscribed', params: { uri: RESOURCE_URI } });

			for (let tick = 0; tick < MAX_SSE_TICKS && !cancelled; tick++) {
				await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
				if (cancelled) break;

				let meta;
				try {
					meta = await fetchMeta(request);
				} catch {
					continue;
				}
				if (meta.revision && meta.revision !== lastRevision) {
					lastRevision = meta.revision;
					send(buildResourceUpdatedNotification());
				}
			}
			controller.close();
		},
		cancel() {
			cancelled = true;
		},
	});

	return new Response(stream, {
		headers: {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			Connection: 'keep-alive',
		},
	});
}
