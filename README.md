# Mshroom Research Blog

基于 [Astro](https://astro.build) 构建的轻量级科研博客，部署于 Cloudflare Pages。

## 特性

- ✍️ **Markdown/MDX** 原生支持，科研写作友好
- 🏷️ **标签系统** 文章分类管理
- 📱 **响应式设计** 移动端适配
- ⚡ **极速加载** 静态生成，零 JS 默认
- 🔍 **SEO 优化** 自动生成 sitemap 和 RSS

## 快速开始

```bash
# 安装依赖
pnpm install

# 开发预览
pnpm dev

# 构建
pnpm build
```

## 写作流程

1. 在 `src/content/blog/` 创建 `.md` 文件
2. 添加 frontmatter 元数据：

```markdown
---
title: '文章标题'
description: '文章描述'
pubDate: '2025-04-02'
tags: ['research', 'ai']
---

正文内容...
```

## 部署（方案B：本地构建）

```bash
# 一键部署
./deploy.sh
```

或手动：

```bash
pnpm build
npx wrangler pages deploy dist --project-name=blog-mshroom
```

## 域名配置

已在 `astro.config.mjs` 配置域名 `https://blog.mshroom.cv`，
请在 Cloudflare Pages 控制台绑定自定义域名。

## 项目结构

```
├── src/
│   ├── content/blog/    # 博客文章
│   ├── layouts/         # 页面布局
│   ├── pages/           # 路由页面
│   └── styles/          # 全局样式
├── public/              # 静态资源
├── dist/                # 构建输出（上传到 Cloudflare）
└── deploy.sh            # 部署脚本
```
