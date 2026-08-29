// HTTP 层验收测试：Content-Type 校验、body 体积上限/编码校验、限速 fail-closed、
// JSON-RPC 信封校验、notification 202、SSE 门槛校验。纯逻辑分发（tools/call
// 具体行为）在 functions/_lib/mcp.test.js，这里只测 functions/api/mcp.js 自己
// 加的 HTTP 关注点。用假 KV + 打桩 global fetch（同源 fetch /agent-feed-index.json
// /agent-feed-meta.json），不需要 wrangler/Miniflare。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { onRequestGet, onRequestPost } from './mcp.js';

const FIXTURE_POSTS = [
	{
		id: 'post-a',
		title: 'A 篇',
		description: 'desc',
		pubDate: '2026-08-20T00:00:00.000Z',
		tags: [],
		category: 'Research',
		url: '/blog/post-a/',
		bodyMarkdown: 'body',
	},
];

function makeFakeKv() {
	const store = new Map();
	return {
		async get(key) {
			return store.has(key) ? store.get(key) : null;
		},
		async put(key, value, opts) {
			store.set(key, value);
		},
	};
}

function withFakeFetch(handler, fn) {
	const original = globalThis.fetch;
	globalThis.fetch = handler;
	return fn().finally(() => {
		globalThis.fetch = original;
	});
}

function fetchServingIndexAndMeta() {
	return async (url) => {
		const u = new URL(url);
		if (u.pathname === '/agent-feed-index.json') {
			return new Response(JSON.stringify({ posts: FIXTURE_POSTS }), { status: 200 });
		}
		if (u.pathname === '/agent-feed-meta.json') {
			return new Response(JSON.stringify({ count: 1, latestPubDate: FIXTURE_POSTS[0].pubDate, revision: 'abc' }), { status: 200 });
		}
		return new Response('not found', { status: 404 });
	};
}

function makeRequest({ method = 'POST', body, headers = {}, path = '/api/mcp' } = {}) {
	const init = { method, headers };
	if (body !== undefined) init.body = body;
	return new Request(`https://blog.mushroom.cv${path}`, init);
}

test('POST：Content-Type 不是 application/json 时返回 400', async () => {
	const request = makeRequest({ headers: { 'Content-Type': 'text/plain' }, body: '{}' });
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 400);
});

test('POST：KV 绑定缺失时 fail-closed 返回 503（不是静默放行）', async () => {
	const request = makeRequest({ headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' }, body: '{}' });
	const env = {};
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 503);
});

test('POST：CF-Connecting-IP 缺失时 fail-closed 返回 503', async () => {
	const request = makeRequest({ headers: { 'Content-Type': 'application/json' }, body: '{}' });
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 503);
});

test('POST：超过 body 上限返回 413', async () => {
	const bigQuery = 'a'.repeat(20_000);
	const request = makeRequest({
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
		body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'search_posts', arguments: { query: bigQuery } } }),
	});
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 413);
});

test('POST：非法 UTF-8 body 返回 400（不是误判成 413）', async () => {
	// 单独一个孤立的 UTF-8 续字节（0x80），不是合法序列的开头，fatal:true 解码会抛异常。
	const invalidUtf8 = new Uint8Array([0x7b, 0x80, 0x7d]);
	const request = new Request('https://blog.mushroom.cv/api/mcp', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
		body: invalidUtf8,
	});
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 400);
});

test('POST：JSON-RPC 信封非法（数组）返回 -32600 / 400', async () => {
	const request = makeRequest({
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
		body: JSON.stringify([1, 2, 3]),
	});
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 400);
	const body = await res.json();
	assert.equal(body.error.code, -32600);
});

test('POST：jsonrpc 字段不是 "2.0" 时返回 -32600 / 400', async () => {
	const request = makeRequest({
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
		body: JSON.stringify({ jsonrpc: '1.0', id: 1, method: 'tools/list' }),
	});
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 400);
	const body = await res.json();
	assert.equal(body.error.code, -32600);
});

test('POST：没有 id 字段的合法 notification 返回 202 空 body', async () => {
	const request = makeRequest({
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
		body: JSON.stringify({ jsonrpc: '2.0', method: 'tools/list' }),
	});
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestPost({ request, env });
	assert.equal(res.status, 202);
	const text = await res.text();
	assert.equal(text, '');
});

test('POST：正常 tools/list 请求走完整流程返回 200', async () => {
	await withFakeFetch(fetchServingIndexAndMeta(), async () => {
		const request = makeRequest({
			headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
			body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'tools/list' }),
		});
		const env = { BLOG_SEARCH_KV: makeFakeKv() };
		const res = await onRequestPost({ request, env });
		assert.equal(res.status, 200);
		const body = await res.json();
		assert.ok(Array.isArray(body.result.tools));
	});
});

test('POST：超过限速上限后返回 429', async () => {
	const kv = makeFakeKv();
	const env = { BLOG_SEARCH_KV: kv };
	let lastStatus;
	for (let i = 0; i < 61; i++) {
		const request = makeRequest({
			headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '9.9.9.9' },
			body: JSON.stringify({ jsonrpc: '2.0', method: 'tools/list' }),
		});
		lastStatus = (await onRequestPost({ request, env })).status;
	}
	assert.equal(lastStatus, 429);
});

test('GET：缺少 Accept: text/event-stream 时返回 405', async () => {
	const request = makeRequest({ method: 'GET', path: '/api/mcp?subscribe=posts://latest' });
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestGet({ request, env });
	assert.equal(res.status, 405);
});

test('GET：缺少 ?subscribe= 参数时返回 405', async () => {
	const request = makeRequest({ method: 'GET', path: '/api/mcp', headers: { Accept: 'text/event-stream' } });
	const env = { BLOG_SEARCH_KV: makeFakeKv() };
	const res = await onRequestGet({ request, env });
	assert.equal(res.status, 405);
});

test('GET：合法订阅请求返回 text/event-stream，KV 缺失时 503', async () => {
	const request = makeRequest({
		method: 'GET',
		path: '/api/mcp?subscribe=posts%3A%2F%2Flatest',
		headers: { Accept: 'text/event-stream' },
	});
	const env = {};
	const res = await onRequestGet({ request, env });
	assert.equal(res.status, 503);
});
