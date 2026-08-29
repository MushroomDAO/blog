import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildResourceUpdatedNotification, handleJsonRpc, PROTOCOL_VERSION, RESOURCE_URI } from './mcp.js';

// round 1 review Low #9：这个 fixture 顺序刻意不按发布时间排（post-a 更早却排
// 第一），用来验证 listRecent/searchPosts 自己会排序，而不是依赖调用方传入的
// 数组恰好已经排好——之前的 fixture 顺序凑巧看起来对，掩盖了 listRecent 本身
// 不排序这件事。
const FIXTURE_POSTS = [
	{
		id: 'post-a',
		title: 'A 篇',
		description: '关于 mycelium 的文章',
		pubDate: '2026-08-20T00:00:00.000Z',
		tags: ['mycelium', 'agent'],
		category: 'Research',
		url: '/blog/post-a/',
		bodyMarkdown: '正文提到 MCP 协议',
	},
	{
		id: 'post-b',
		title: 'B 篇',
		description: '跟 agent 无关的文章',
		pubDate: '2026-08-25T00:00:00.000Z',
		tags: ['other'],
		category: 'Tech-News',
		url: '/blog/post-b/',
		bodyMarkdown: '正文什么都没提',
	},
];

const loadFixturePosts = async () => FIXTURE_POSTS;

function callsLoadPosts(recorder) {
	return async () => {
		recorder.called = true;
		return FIXTURE_POSTS;
	};
}

test('initialize 返回声明的协议版本和 capabilities，不需要加载文章', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 1, method: 'initialize' }, callsLoadPosts(recorder));
	assert.equal(res.id, 1);
	assert.equal(res.result.protocolVersion, PROTOCOL_VERSION);
	assert.ok(res.result.capabilities.resources.subscribe);
	assert.equal(recorder.called, false);
});

test('tools/list 包含三个工具，不需要加载文章', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 3, method: 'tools/list' }, callsLoadPosts(recorder));
	const names = res.result.tools.map((t) => t.name);
	assert.deepEqual(names, ['search_posts', 'get_post', 'list_recent']);
	assert.equal(recorder.called, false);
});

test('resources/list 不需要加载文章', async () => {
	const recorder = { called: false };
	await handleJsonRpc({ jsonrpc: '2.0', id: 4, method: 'resources/list' }, callsLoadPosts(recorder));
	assert.equal(recorder.called, false);
});

test('resources/subscribe 确认已知 uri，不需要加载文章', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 5, method: 'resources/subscribe', params: { uri: RESOURCE_URI } },
		callsLoadPosts(recorder),
	);
	assert.deepEqual(res.result, {});
	assert.equal(recorder.called, false);
});

test('tools/call search_posts 按关键词匹配正文，且不泄露 bodyMarkdown', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 6, method: 'tools/call', params: { name: 'search_posts', arguments: { query: 'MCP 协议' } } },
		loadFixturePosts,
	);
	const payload = JSON.parse(res.result.content[0].text);
	assert.equal(payload.results.length, 1);
	assert.equal(payload.results[0].id, 'post-a');
	assert.equal(payload.results[0].bodyMarkdown, undefined);
});

test('tools/call search_posts 按 tag 过滤', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 7, method: 'tools/call', params: { name: 'search_posts', arguments: { tag: 'other' } } },
		loadFixturePosts,
	);
	const payload = JSON.parse(res.result.content[0].text);
	assert.deepEqual(
		payload.results.map((p) => p.id),
		['post-b'],
	);
});

test('tools/call search_posts 结果按发布时间倒序，不依赖输入顺序', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 8, method: 'tools/call', params: { name: 'search_posts', arguments: {} } },
		loadFixturePosts,
	);
	const payload = JSON.parse(res.result.content[0].text);
	assert.deepEqual(
		payload.results.map((p) => p.id),
		['post-b', 'post-a'],
	);
});

test('tools/call get_post 找不到时返回 isError', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 9, method: 'tools/call', params: { name: 'get_post', arguments: { id: 'nope' } } },
		loadFixturePosts,
	);
	assert.equal(res.result.isError, true);
});

test('tools/call get_post 命中时返回完整正文', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 10, method: 'tools/call', params: { name: 'get_post', arguments: { id: 'post-a' } } },
		loadFixturePosts,
	);
	const payload = JSON.parse(res.result.content[0].text);
	assert.equal(payload.bodyMarkdown, '正文提到 MCP 协议');
});

test('tools/call list_recent 按发布时间倒序，不依赖输入顺序', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 11, method: 'tools/call', params: { name: 'list_recent', arguments: {} } },
		loadFixturePosts,
	);
	const payload = JSON.parse(res.result.content[0].text);
	assert.deepEqual(
		payload.results.map((p) => p.id),
		['post-b', 'post-a'],
	);
});

test('tools/call 未知工具返回 JSON-RPC -32602，不加载文章（round 2 review Medium）', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 12, method: 'tools/call', params: { name: 'delete_everything', arguments: {} } },
		callsLoadPosts(recorder),
	);
	assert.equal(res.error.code, -32602);
	assert.equal(recorder.called, false);
});

test('tools/call get_post 缺少 id 时不加载文章就直接返回 isError（round 2 review Medium）', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 121, method: 'tools/call', params: { name: 'get_post', arguments: {} } },
		callsLoadPosts(recorder),
	);
	assert.equal(res.result.isError, true);
	assert.equal(recorder.called, false);
});

test('tools/call 缺少 name 返回 -32602，不炸异常', async () => {
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 13, method: 'tools/call', params: {} }, loadFixturePosts);
	assert.equal(res.error.code, -32602);
});

test('tools/call params 是 null 时不炸异常（round 1 review Medium #8）', async () => {
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 14, method: 'tools/call', params: null }, loadFixturePosts);
	assert.equal(res.error.code, -32602);
});

test('tools/call arguments 是非对象值时不炸异常，当作空参数处理', async () => {
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 15, method: 'tools/call', params: { name: 'list_recent', arguments: 'not an object' } },
		loadFixturePosts,
	);
	assert.equal(res.result.content[0].type, 'text');
});

test('resources/read 返回 posts://latest 的 JSON contents', async () => {
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 16, method: 'resources/read', params: { uri: RESOURCE_URI } }, loadFixturePosts);
	const parsed = JSON.parse(res.result.contents[0].text);
	assert.equal(parsed.results.length, 2);
});

test('resources/read 未知 uri 报错，不加载文章', async () => {
	const recorder = { called: false };
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 17, method: 'resources/read', params: { uri: 'posts://nope' } },
		callsLoadPosts(recorder),
	);
	assert.equal(res.error.code, -32602);
	assert.equal(recorder.called, false);
});

test('resources/subscribe 未知 uri 报错', async () => {
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 18, method: 'resources/subscribe', params: { uri: 'posts://nope' } }, loadFixturePosts);
	assert.equal(res.error.code, -32602);
});

test('未知 method 返回 -32601', async () => {
	const res = await handleJsonRpc({ jsonrpc: '2.0', id: 19, method: 'nope/nope' }, loadFixturePosts);
	assert.equal(res.error.code, -32601);
});

test('loadPosts 抛异常时返回 -32603，不让请求裸炸', async () => {
	const throwingLoader = async () => {
		throw new Error('index fetch failed');
	};
	const res = await handleJsonRpc(
		{ jsonrpc: '2.0', id: 20, method: 'tools/call', params: { name: 'list_recent', arguments: {} } },
		throwingLoader,
	);
	assert.equal(res.error.code, -32603);
});

test('buildResourceUpdatedNotification 是没有 id 的 JSON-RPC 通知', () => {
	const notification = buildResourceUpdatedNotification();
	assert.equal(notification.method, 'notifications/resources/updated');
	assert.equal(notification.params.uri, RESOURCE_URI);
	assert.equal('id' in notification, false);
});
