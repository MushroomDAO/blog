import { getCollection } from 'astro:content';

export async function GET(context) {
	const posts = await getCollection('blog');
	const site = context.site.toString().replace(/\/$/, '');

	const staticPages = [
		{ path: '', priority: '1.0', changefreq: 'daily' },
		{ path: '/about', priority: '0.6', changefreq: 'monthly' },
		{ path: '/blog', priority: '0.9', changefreq: 'daily' },
	].map(({ path, priority, changefreq }) => `  <url>
    <loc>${site}${path}/</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`);

	const blogEntries = posts
		.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
		.map((post) => {
			const lastmod = (post.data.updatedDate || post.data.pubDate).toISOString();
			return `  <url>
    <loc>${site}/blog/${post.id}/</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>`;
		});

	const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...staticPages, ...blogEntries].join('\n')}
</urlset>`;

	return new Response(xml, {
		headers: { 'Content-Type': 'application/xml; charset=utf-8' },
	});
}
