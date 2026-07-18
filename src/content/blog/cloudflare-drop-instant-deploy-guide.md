---
title: "Cloudflare Drop：拖一下文件夹，网站就上线了"
titleEn: "Cloudflare Drop: Drag a Folder. Your Site Is Live."
description: "Cloudflare 刚上线了 Drop（cloudflare.com/drop）——无需注册账号、无需任何配置，把 HTML/CSS/JS 文件夹或 ZIP 拖进去，网站立刻部署到 Cloudflare 全球网络。普通人用它上线网站的完整指南。"
descriptionEn: "Cloudflare just launched Drop (cloudflare.com/drop) — no account required, no configuration, just drag your HTML/CSS/JS folder or ZIP and your site is live on Cloudflare's global network instantly. A complete guide for anyone to deploy a website."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-News"
tags: ["Cloudflare", "部署", "静态网站", "免费工具", "前端", "零配置", "CDN"]
heroImage: "../../assets/images/cloudflare-drop-instant-deploy-guide-banner.jpg"
---

Cloudflare 做了一件之前没人做到这么干净的事：

**把网站部署这件事，简化到了「拖文件夹」这一个动作。**

官方地址：[cloudflare.com/drop](https://www.cloudflare.com/drop/)

---

## 它是什么

Cloudflare Drop 是 Cloudflare 2026 年上线的新产品，核心只有一句话：

> Drop a folder. Or a zip. Summon your site - HTML, CSS, JS. See it live instantly.

（拖一个文件夹。或者 ZIP。你的网站就活了——HTML, CSS, JS。立刻上线。）

两个关键词：

- **无需账号**：不用注册 Cloudflare，不用登录，直接用
- **无需配置**：没有构建命令、没有环境变量、没有 CI/CD，就是拖拽

部署完成后，你的网站会跑在 Cloudflare 的全球 CDN 网络上（330+ 个城市节点），得到一个 `*.pages.dev` 的域名。

---

## 上手只需 30 秒

### 第一步：准备你的文件

Cloudflare Drop 支持两种格式：
- 一个**文件夹**（包含 `index.html` 和相关 CSS/JS/图片）
- 一个 **.zip 压缩包**（把上面的文件夹压缩即可）

只要是纯静态网站都可以：手写的 HTML、Vite/Next.js 等框架 build 出来的 `dist/` 文件夹、Hugo/Jekyll 生成的静态文件、AI 生成的单页……

> **最简单的测试**：新建一个 `index.html`，写上 `<h1>Hello World</h1>`，保存，拖进去，上线。

### 第二步：打开 cloudflare.com/drop

浏览器直接访问 [cloudflare.com/drop](https://www.cloudflare.com/drop/)，看到这个界面：

```
# Drop a folder. Or a zip.

Summon your site - HTML, CSS, JS. See it live instantly.

[ Browse folders ]  [ Browse zips ]
```

两个按钮，或者直接把文件/文件夹拖进浏览器页面。

### 第三步：拖进去，等几秒，就好了

上传完成后，Cloudflare 会给你一个 URL，格式类似：

```
https://xxxx.pages.dev
```

这个网站已经在全球上线了。

---

## 它能做什么 / 不能做什么

### ✅ 能做的

| 场景 | 说明 |
|------|------|
| 临时演示站 | 设计稿/原型给客户看，不想花时间部署 |
| 静态博客/文档 | Hugo/Jekyll/VitePress build 出来的文件夹直接上 |
| 个人作品集 | 单页 HTML，展示给面试官 |
| AI 生成的网站 | v0/Cursor/Claude 生成的 HTML 立刻上线 |
| 课程/学习项目 | 做完前端作业，一键分享 |
| 活动落地页 | 快速上线，不用找服务器 |
| 内部工具演示 | 纯前端的数据可视化、表单页面 |

### ❌ 不能做的

- **动态网站**：没有后端、没有数据库，纯静态
- **服务端渲染**：没有 Node.js 运行时，只是文件服务
- **自定义域名**（目前）：只有 `*.pages.dev` 域名
- **保留上传记录**：不登录就没有管理界面，URL 是唯一凭证

---

## 和 Cloudflare Pages 的区别

|  | Cloudflare Drop | Cloudflare Pages |
|--|-----------------|-----------------|
| 需要账号 | ❌ 不需要 | ✅ 需要注册 |
| 需要配置 | ❌ 全无 | ⚠️ 少量配置 |
| 自定义域名 | ❌ | ✅ |
| 自动构建（连 GitHub） | ❌ | ✅ |
| 版本管理 | ❌ | ✅ |
| 适合场景 | 临时、快速、一次性 | 长期项目、正式上线 |

简单说：**Drop 是 Cloudflare Pages 的极简版**，去掉一切长期功能，只留下「上线」这一个动作。

---

## 和其他工具对比

| 工具 | 需要账号 | 最快上线时间 | 全球 CDN | 域名 |
|------|---------|------------|---------|------|
| **Cloudflare Drop** | ❌ | ~10 秒 | ✅ 330+ 城市 | pages.dev |
| Netlify Drop | ✅（或临时） | ~30 秒 | ✅ | netlify.app |
| Vercel | ✅ | 1-2 分钟 | ✅ | vercel.app |
| GitHub Pages | ✅ | 5-10 分钟 | ⚠️ 有限 | github.io |
| 自建服务器 | ✅ | 变长 | ❌ 单机 | 自定 |

Cloudflare Drop 的核心优势是**零门槛**——其他工具哪怕是「最简单」的 Netlify Drop，也需要你先有个账号。

---

## 几个实际用法

### 用法一：AI 生成网站，立刻上线

用 Claude/v0/Cursor 生成一个 HTML 文件，另存为 `index.html`，丢进去，10 秒上线，发链接给对方。

不需要「部署」这个概念——生成完直接给链接。

### 用法二：前端作业/课程项目展示

做完一个 HTML/CSS/JS 的前端作业，把整个文件夹拖进去，得到一个链接发给老师或同学，效果比截图好 100 倍。

### 用法三：会议前临时起一个演示页面

活动前 30 分钟发现需要一个「扫码进群」的页面，写一个 HTML，30 秒上线，生成二维码。

### 用法四：Vite/Hugo 等框架的 build 产物直接上线

```bash
# Vite 项目
npm run build      # 生成 dist/ 文件夹
# 把 dist/ 文件夹拖进 cloudflare.com/drop

# Hugo 博客
hugo              # 生成 public/ 文件夹
# 把 public/ 文件夹拖进去
```

不用装 Wrangler，不用配 CI，就这样。

---

## 适合什么人用

**最适合：**
- 设计师：想快速把 HTML 原型发给客户看，不想学 git 和 CI/CD
- 前端入门者：做完练习想分享成果，但不想搭服务器
- 产品/运营：想临时上线一个活动页面，不依赖开发资源
- 独立开发者：快速验证一个新想法，不想花时间配环境

**不适合：**
- 需要长期维护的正式项目（用 Cloudflare Pages 的 Git 集成）
- 需要自定义域名的品牌站（用 Cloudflare Pages）
- 需要动态功能的应用（用 Cloudflare Workers）

---

## 一句话总结

Cloudflare Drop 不是在解决「如何部署复杂应用」的问题，它解决的是另一个问题：

**让「我想让别人看到这个网页」这个想法，不再需要学任何技术知识。**

拖进去，就活了。

---

- 产品入口：[cloudflare.com/drop](https://www.cloudflare.com/drop/)
- 需要长期项目？→ [Cloudflare Pages](https://pages.cloudflare.com/)
- 需要后端功能？→ [Cloudflare Workers](https://workers.cloudflare.com/)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Cloudflare Drop: Drag a Folder. Your Site Is Live.

Cloudflare just did something nobody had done this cleanly before: reduced website deployment to a single gesture — dragging a folder.

**Product URL**: [cloudflare.com/drop](https://www.cloudflare.com/drop/)

---

### What It Is

Cloudflare Drop is a brand-new Cloudflare product that strips site deployment to its absolute minimum:

> Drop a folder. Or a zip. Summon your site — HTML, CSS, JS. See it live instantly.

Two things that don't exist here: **no account required** and **no configuration required**. Just drag your files, and in seconds you have a live URL on Cloudflare's global CDN (330+ cities), served under a `*.pages.dev` domain.

---

### How to Use It — 30 Seconds

**Step 1**: Build or write your static site (HTML/CSS/JS). A `dist/` folder from Vite, Hugo's `public/` folder, a handwritten `index.html` — anything works.

**Step 2**: Go to [cloudflare.com/drop](https://www.cloudflare.com/drop/). You'll see a drag area and two buttons: "Browse folders" and "Browse zips."

**Step 3**: Drag your folder (or zip) in. Wait a few seconds. Get your URL.

That's the entire process.

---

### What It Supports / Doesn't Support

**Works:**
- Temporary demo sites (show clients a design without a full deploy)
- Static blogs and docs (Hugo/Jekyll/VitePress build output)
- Portfolio pages, course projects
- AI-generated websites (Claude/v0/Cursor output → instant link)
- Event landing pages

**Doesn't work:**
- Dynamic sites with backends or databases
- Server-side rendering
- Custom domains (currently — only `*.pages.dev`)
- Version history or management without an account

---

### vs. Cloudflare Pages

| | Cloudflare Drop | Cloudflare Pages |
|--|--|--|
| Account required | ❌ | ✅ |
| Configuration | None | Minimal |
| Custom domain | ❌ | ✅ |
| Git integration | ❌ | ✅ |
| Best for | Quick, temporary, one-off | Long-term, production projects |

Drop is Cloudflare Pages with everything except "make it live" removed.

---

### Who It's For

**Best fit**: designers who want to share HTML prototypes without learning git; frontend beginners who finished a project and want to share it; product/marketing teams who need a landing page without engineering; indie developers validating an idea fast.

**Not the right tool for**: production projects needing custom domains (use Cloudflare Pages), backend functionality (use Cloudflare Workers), or long-term version control.

---

### One-Sentence Summary

Cloudflare Drop solves a different problem than most deployment tools. It's not about deploying complex applications — it's about making "I want someone to see this webpage" not require any technical knowledge at all.

Drag it in. It's live.

---

- Try it: [cloudflare.com/drop](https://www.cloudflare.com/drop/)
- For long-term projects: [Cloudflare Pages](https://pages.cloudflare.com/)
- For backend functionality: [Cloudflare Workers](https://workers.cloudflare.com/)

© 2026 Author: Mycelium Protocol
