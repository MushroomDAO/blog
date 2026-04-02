import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			// 中文标题
			title: z.string(),
			// 英文标题
			titleEn: z.string().optional(),
			// 中文描述
			description: z.string(),
			// 英文描述
			descriptionEn: z.string().optional(),
			// Transform string to Date object
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.optional(image()),
			// 分类标签：技术实验 | 进度汇报 | 专题研究 | 最新科技
			tags: z.array(z.string()).default([]),
			// 文章分类（英文）
			category: z.enum(['Tech-Experiment', 'Progress-Report', 'Research', 'Tech-News', 'Other']).default('Other'),
		}),
});

export const collections = { blog };
