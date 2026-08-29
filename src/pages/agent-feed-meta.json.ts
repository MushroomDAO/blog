import { buildAgentFeedIndex } from '../lib/agent-feed-index';

async function sha256Hex(text: string): Promise<string> {
	const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
	return Array.from(new Uint8Array(digest))
		.map((b) => b.toString(16).padStart(2, '0'))
		.join('');
}

// 给 functions/api/mcp.js 的 SSE 订阅循环轮询用的小端点——round 1 review 指出
// 原来每 20s 重新 fetch+parse 一次完整的 ~7.7MB agent-feed-index.json 是明显的
// 资源放大（单连接 25 次轮询约解码 200MB），这个端点只有几十字节。
//
// `revision` 不是只比较最新 pubDate（那样会漏掉"同一天发第二篇"和"改了已发布
// 文章正文/updatedDate 但 pubDate 没变"这两种真实会发生的更新——round 1 review
// 指出的另一个问题），而是对全部文章的 `id:updatedDate|pubDate` 拼起来做哈希，
// 任何一篇的增删或者 updatedDate 变化都会让这个值变。
export async function GET() {
	const posts = await buildAgentFeedIndex();
	const revisionSource = posts.map((post) => `${post.id}:${post.updatedDate ?? post.pubDate}`).join('|');
	const revision = await sha256Hex(revisionSource);

	return new Response(JSON.stringify({ count: posts.length, latestPubDate: posts[0]?.pubDate ?? '', revision }), {
		headers: { 'Content-Type': 'application/json; charset=utf-8' },
	});
}
