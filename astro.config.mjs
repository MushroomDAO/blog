// @ts-check

import mdx from '@astrojs/mdx';
import { defineConfig } from 'astro/config';

// Sitemap is now generated via src/pages/sitemap.xml.js
// for accurate per-post lastmod dates from frontmatter pubDate/updatedDate
export default defineConfig({
	site: 'https://blog.mshroom.cv',
	integrations: [mdx()],
});
