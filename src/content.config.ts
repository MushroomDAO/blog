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
			category: z.enum(['Tech-Experiment', 'Progress-Report', 'Research', 'Tech-News', 'DN']).default('Research'),
		}),
});

const my = defineCollection({
	loader: glob({ base: './src/content/my', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.optional(image()),
			tags: z.array(z.string()).default([]),
			category: z.enum(['Hardware', 'Research', 'Launch', 'Lessons', 'Thought']).default('Lessons'),
			isHub: z.boolean().default(false),
			hubIcon: z.string().optional(),
			externalUrl: z.string().url().optional(),
		}),
});

const dailyVideo = defineCollection({
	// 每日视频（免费引流线，见 daily-video/README.md）。独立于 blog collection，
	// 因为字段形状差很多（双平台链接、一句话结论），不是"多了个 video 区块"的文章。
	loader: glob({ base: './src/content/daily-video', pattern: '**/*.{md,mdx}' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			titleEn: z.string().optional(),
			description: z.string(),
			descriptionEn: z.string().optional(),
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			coverImage: z.optional(image()),
			// 同一条视频的两个平台地址：VideoFrame 组件按访客地域二选一展示
			bilibiliUrl: z.string().url(),
			youtubeUrl: z.string().url(),
			// 被评测的开源仓库（这条系列的核心：从 local-first AI 需要的组件反向找仓库）
			sourceRepoUrl: z.string().url().optional(),
			// 一句话结论：推荐给谁用、值不值得看
			verdict: z.string().optional(),
			tags: z.array(z.string()).default([]),
		}),
});

export const collections = { blog, my, dailyVideo };
