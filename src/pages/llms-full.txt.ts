import { SITE_DESCRIPTION, SITE_TITLE } from '../consts';
import { buildAgentFeedIndex } from '../lib/agent-feed-index';

// llms-full.txt：跟 llms.txt 同一份数据源，但每篇文章带完整 markdown 正文，
// 供不打算再单独抓每篇文章页面的 agent 一次性拿到全部内容。
export async function GET() {
	const posts = await buildAgentFeedIndex();
	const site = 'https://blog.mushroom.cv';

	const articles = posts
		.map(
			(post) => `---

# ${post.title}

- URL: ${site}${post.url}
- Category: ${post.category}
- Tags: ${post.tags.join(', ')}
- Published: ${post.pubDate}${post.updatedDate ? `\n- Updated: ${post.updatedDate}` : ''}

${post.bodyMarkdown}`,
		)
		.join('\n\n');

	const body = `# ${SITE_TITLE}

> ${SITE_DESCRIPTION}
${articles}
`;

	return new Response(body, {
		headers: { 'Content-Type': 'text/plain; charset=utf-8' },
	});
}
