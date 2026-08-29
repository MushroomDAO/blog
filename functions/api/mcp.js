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
 * fetchFullIndex，其余方法（initialize/tools/list/resources/list/resources/
 * subscribe）不碰索引。
 *
 * GET：当 `Accept: text/event-stream` 且 `?subscribe=posts://latest` 时，走
 * SSE 推送更新事件。每 20s 重新同源 fetch 一次 agent-feed-meta.json（不是完整
 * 索引，避免每连接反复解码几 MB）比较 revision 是否变化，不引入 Durable
 * Objects/WebSocket 维护跨请求状态。**这不是真正 session 绑定的 MCP
 * resources/subscribe**——JSON-RPC 的 resources/subscribe 调用和这个 GET 连接
 * 之间没有服务端状态把两者关联起来，只是约定"同一个 uri"。诚实的定位是"一个
 * 按固定 URI 轮询更新的推送端点"，不是标准传输规范里那种客户端在自己已有连接上
 * 收到订阅通知的语义，见 agent-feed/PLAN.md 的"已知边界"。单次连接有执行时长
 * 上限，客户端要自己处理断线重连。
 */

import { checkAndIncrement } from '../_lib/rate-limit.js';
import { buildResourceUpdatedNotification, handleJsonRpc, RESOURCE_URI } from '../_lib/mcp.js';

const MAX_BODY_BYTES = 8192; // 正常 JSON-RPC 请求（含 tools/call 参数）几百字节顶天
// 这个端点不调用任何计费的 AI/Vectorize，内容本身跟 /blog 页面一样公开，限速
// 只是防止被当脚本刷爆而不是防成本——但仍然消耗 CPU/子请求，KV/IP 缺失时
// fail-closed（503），不静默放行。
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

class BodyReadError extends Error {
	constructor(code) {
		super(code);
		this.code = code;
	}
}

// 边读边数字节，一超过上限立刻 cancel 掉底层 reader，不会因为一个几十 MB 的
// body 真的把它缓冲完（原来先看 Content-Length——请求方自己声明的，chunked
// encoding 或撒谎的值都绕得过去——再整体 request.text() 有这个洞）。
//
// 解码用 `fatal: true`——默认的 TextDecoder 会把非法字节序列悄悄替换成
// U+FFFD，畸形的线路输入可能被"修复"成看起来合法的 JSON；这里要能分清"body
// 太大"（413，客户端行为问题）和"body 不是合法 UTF-8 / reader 读取失败"
// （400，不该跟"太大"归成同一类）。
async function readBoundedBody(request, maxBytes) {
	const reader = request.body?.getReader();
	if (!reader) return '';

	const chunks = [];
	let total = 0;
	try {
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			total += value.byteLength;
			if (total > maxBytes) {
				await reader.cancel();
				throw new BodyReadError('too_large');
			}
			chunks.push(value);
		}
	} catch (err) {
		if (err instanceof BodyReadError) throw err;
		throw new BodyReadError('read_failed');
	}

	const buffer = new Uint8Array(total);
	let offset = 0;
	for (const chunk of chunks) {
		buffer.set(chunk, offset);
		offset += chunk.byteLength;
	}

	try {
		return new TextDecoder('utf-8', { fatal: true }).decode(buffer);
	} catch {
		throw new BodyReadError('invalid_encoding');
	}
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

// 校验 JSON-RPC 2.0 信封本身（不是某个方法的参数）：必须是非数组的普通对象，
// `jsonrpc` 恰好是 `"2.0"`，`method` 是非空字符串。垃圾输入（数组、`{}`、
// 缺 method）之前会被当成"没有 id 字段就是 notification"直接静默 202，或者
// 被当成正常请求丢给 handleJsonRpc 引发意外行为——现在统一在分发之前用标准
// JSON-RPC -32600 拒绝。
function validateEnvelope(value) {
	if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
	if (value.jsonrpc !== '2.0') return false;
	if (typeof value.method !== 'string' || !value.method) return false;
	return true;
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
	} catch (err) {
		if (err instanceof BodyReadError && err.code === 'too_large') {
			return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'request body too large' } }, 413);
		}
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'invalid request body' } }, 400);
	}

	let rpcRequest;
	try {
		rpcRequest = JSON.parse(bodyText);
	} catch {
		return jsonResponse({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'parse error' } }, 400);
	}

	if (!validateEnvelope(rpcRequest)) {
		const echoId = typeof rpcRequest?.id === 'string' || typeof rpcRequest?.id === 'number' || rpcRequest?.id === null ? rpcRequest.id : null;
		return jsonResponse({ jsonrpc: '2.0', id: echoId, error: { code: -32600, message: 'invalid request' } }, 400);
	}

	// JSON-RPC 2.0：Notification 是"没有 id 字段"的请求，规范要求服务端不回响应体
	// （跟 id 为 null 的正常请求不是一回事——那种仍然要回）。信封已经在上面校验过，
	// 这里只需要判断 id 字段在不在。
	const isNotification = !('id' in rpcRequest);

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
