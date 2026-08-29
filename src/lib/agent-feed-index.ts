import { getCollection } from 'astro:content';

export interface AgentFeedPost {
	id: string;
	title: string;
	titleEn?: string;
	description: string;
	descriptionEn?: string;
	pubDate: string;
	updatedDate?: string;
	tags: string[];
	category: string;
	url: string;
	bodyMarkdown: string;
}

// 三个下游产物（agent-feed-index.json / llms.txt / llms-full.txt / MCP server）
// 共用的唯一数据源。bodyMarkdown 直接用 content collection entry 的 `.body`
// （glob loader 已经把 frontmatter 拆到 .data 里，.body 就是纯 markdown 正文，
// 不需要 render() 再转 HTML 又转回纯文本——llms.txt 惯例本来就是给干净的
// markdown，不是渲染后的 HTML）。
export async function buildAgentFeedIndex(): Promise<AgentFeedPost[]> {
	const posts = await getCollection('blog');
	return posts
		.map((post) => ({
			id: post.id,
			title: post.data.title,
			titleEn: post.data.titleEn,
			description: post.data.description,
			descriptionEn: post.data.descriptionEn,
			pubDate: post.data.pubDate.toISOString(),
			updatedDate: post.data.updatedDate?.toISOString(),
			tags: post.data.tags,
			category: post.data.category,
			url: `/blog/${post.id}/`,
			bodyMarkdown: post.body ?? '',
		}))
		.sort((a, b) => new Date(b.pubDate).valueOf() - new Date(a.pubDate).valueOf());
}
