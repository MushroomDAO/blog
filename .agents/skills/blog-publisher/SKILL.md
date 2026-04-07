---
name: blog-publisher
description: Astro blog publishing workflow for blog.mushroom.cv. Use when user wants to publish a new blog post, process images for blog, build and deploy the site. Handles image processing, markdown creation, building, and Cloudflare deployment.
---

# Blog Publisher Skill

Astro blog at blog.mushroom.cv - automated publishing pipeline.

## Quick Commands

```bash
# Build
npm run build

# Deploy to Cloudflare Pages
wrangler pages deploy dist --project-name="blog-mushroom"
```

## Image Processing

Process image for blog cover (1200x630, quality 85):

```bash
convert input.png -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 src/assets/images/FILENAME.jpg
```

## New Blog Post Template

Location: `src/content/blog/FILENAME.md`

```markdown
---
title: "中文标题"
titleEn: "english-slug"
description: "中文描述"
descriptionEn: "English description"
pubDate: "YYYY-MM-DD"
category: "Tech-News"
tags: ["tag1", "tag2"]
heroImage: "../../assets/images/IMAGE.jpg"
---

## 标题

Content...

---

📄 **Original**: URL
```

## Categories

- Tech-News
- Research-Notes
- Progress-Report

## Deployed URL

- Production: https://blog.mushroom.cv
- Preview: https://research-xiaohongshu.blog-mushroom.pages.dev

## Common Operations

### 1. Process & Publish

1. Process image to `src/assets/images/`
2. Create markdown in `src/content/blog/`
3. Run `npm run build`
4. Run `wrangler pages deploy dist --project-name="blog-mushroom"`

### 2. Build Check

```bash
npm run build 2>&1 | tail -20
```

### 3. Deploy Only

```bash
wrangler pages deploy dist --project-name="blog-mushroom"
```
