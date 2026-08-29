import { SITE_DESCRIPTION, SITE_TITLE } from '../consts';
import { buildAgentFeedIndex } from '../lib/agent-feed-index';

// llms.txt 惯例格式（https://llmstxt.org）：H1 站名 + 一句话简介 + 按分类分组的
// 文章列表，每条给标题/一句话描述/链接。这一层解决的是"agent 怎么发现内容"，
// 不是"agent 怎么订阅/深度查询"——那个诉求由 MCP server（/api/mcp）承接，见
// agent-feed/PLAN.md。（原来这里还提过一个 A2A agent card，两轮 review 都
// 确认那个卡片结构性不对，已经整个撤下，见 PLAN.md"已知边界"。）
export async function GET() {
	const posts = await buildAgentFeedIndex();

	const byCategory = new Map<string, typeof posts>();
	for (const post of posts) {
		const list = byCategory.get(post.category) ?? [];
		list.push(post);
		byCategory.set(post.category, list);
	}

	const site = 'https://blog.mushroom.cv';
	const sections = Array.from(byCategory.entries())
		.map(([category, items]) => {
			const lines = items.map((post) => `- [${post.title}](${site}${post.url}): ${post.description}`);
			return `## ${category}\n\n${lines.join('\n')}`;
		})
		.join('\n\n');

	const body = `# ${SITE_TITLE}

> ${SITE_DESCRIPTION}

Machine-readable full text: ${site}/llms-full.txt
Agent-to-agent interface: MCP server at ${site}/api/mcp (protocol 2025-11-25; tools: search_posts, get_post, list_recent; resource: posts://latest).

${sections}
`;

	return new Response(body, {
		headers: { 'Content-Type': 'text/plain; charset=utf-8' },
	});
}
