import { buildAgentFeedIndex } from '../lib/agent-feed-index';

// 给 agent 用的原始结构化数据端点，同时是 functions/api/mcp.js 在请求时
// （Pages Function 运行时读不到 astro:content）拉取内容的唯一来源——同源
// fetch 这个构建产物，不需要额外的 KV/绑定。
export async function GET() {
	const posts = await buildAgentFeedIndex();
	return new Response(JSON.stringify({ posts }), {
		headers: { 'Content-Type': 'application/json; charset=utf-8' },
	});
}
