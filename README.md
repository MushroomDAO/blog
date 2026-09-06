# Mycelium Research Blog

基于 [Astro](https://astro.build) 构建的科研博客，支持双语写作、标签分类，部署于 Cloudflare Pages。

## 特性

- ✍️ **Markdown/MDX** 原生支持，科研写作友好
- 🌐 **双语支持** 中英文并排或单语显示
- 🏷️ **标签系统** 灵活的文章标签管理
- 📂 **分类筛选** 5 种预设分类快速筛选
- 📱 **响应式设计** 移动端适配
- ⚡ **极速加载** 静态生成，零 JS 默认
- 🔍 **SEO 优化** 自动生成 sitemap 和 RSS

---

## 仓库能力清单

本仓库不只是一个 Astro 博客，而是一套"内容生产 + 多平台发布 + 站内智能功能 + 情报采集"的完整系统。按能力分类如下（每次更新维护者应重新核对本节，避免与实际代码脱节）：

### 1. 博客站点本身（Astro + Cloudflare Pages）

- Markdown/MDX 写作、双语并排显示（`<!--EN-->` 分隔）、5 分类 + 标签
- RSS（`src/pages/rss.xml.js`）、Sitemap、Pagefind 全文关键词搜索（构建期生成索引）
- **语义搜索**（`src/pages/search.astro` + `functions/api/search.js`）：query → bge-m3 embedding → Cloudflare Vectorize 检索，带查询缓存 + 按 IP 限速；`semantic-search/` 下有完整的分块/增量索引/对账脚本（`build-vectorize-index.py`、`incremental-index.py`、`reconcile.py`）
- **站内数据看板**（`src/pages/analytics.astro`）：`pipeline/analytics/fetch-analytics.py` 拉取 Cloudflare Web Analytics（RUM）数据，构建期写入 `src/data/blog-analytics.json`
- GitHub Discussions 评论系统（Giscus）
- 多用户配置（`config/users/*.js`，按 `BLOG_USER` 环境变量切换域名/微信/小红书账号）

### 2. 三条发布流水线（`pipeline/`）

| 流水线 | 目标平台 | 实现 |
|---|---|---|
| M1 | Blog（Astro → Cloudflare Pages） | `pipeline/m1/`：润色（`polisher.py`）、封面生成（`cover_generator.py`）、发布（`publisher.py`/`m1-complete.sh`） |
| M2 | 微信公众号草稿 | `pipeline/m2/`（Node.js）+ `submodules/wechat-*`（格式化/发布 skill 子模块） |
| M3 | 小红书 | `pipeline/m3/`（Python 内容优化 + 封面）+ `pipeline/deploy/xiaohongshu-mcp/`（Dockerized Go MCP 服务） |

一键入口：`scripts/auto-publish.sh` / `scripts/publish-blog.sh`（当前主脚本）/ `publish-xhs.sh` / `./deploy.sh`。

### 3. 内容生产辅助 Agent Skills（`.agents/skills/`，镜像至 `.claude/skills/`）

- `blog-publisher` — 文章发布主流程（触发词：发布/发布文章/发布blog）
- `banner-creator` — 本机 FLUX.2 Klein (MLX) 生成 1200×630 写实无文字封面
- `mage-vl` — 本机视觉语言模型看图/视频（配图 alt、图文匹配核查），全程离线不出网，无音频塔
- `seo-geo` — 发布前 SEO + GEO（让 AI 引擎引用）24 点检查
- `source-scanner` — 扫描 `source/` 新目录，提取内容生成双语初稿，交给 `blog-publisher` 发布
- `forage` — 每日信息雷达（见下）
- `xhs-mcp-cdp` / `xhs-mcp-docker` / `xhs-publisher` — 小红书自动发布的三种技术路线（CDP 模式 / Docker 扫码模式 / 统一发布 skill）
- `network-switch` — 代理开关（访问 GitHub/Google 等外网资源）
- `llm-wiki` — 查询本机 LLM Wiki 知识库桌面 App

### 4. 每日情报雷达（forage，`radar/` + `.agents/skills/forage/`）

巡检小红书关注列表/关键词、GitHub Trending、HuggingFace 新模型、X 时间线，按 `preferences.yml` 偏好画像打分，命中项去 GitHub/HuggingFace 拉一手资料，产出带独立分析的选题清单（`radar/index.html` 可视化，`radar/forage.db` 存档）。**全程只读，不发帖/评论/点赞/关注**。渠道数量硬约束：总数 ≤10，单渠道 ≤5。

### 5. Newsletter 订阅系统（`pipeline/newsletter/`）

后端：listmonk + Fly.io + Neon Postgres + AWS SES（`listmonk-fly/`、`listmonk-container/`）；`build-digest.py` 生成摘要邮件，`send-newsletter.sh` 发送。前端表单已直连后端 API（未套 iframe）。当前状态：后端已跑通，部分 DNS/AWS 权限项待人工处理。

### 6. 仓库自动化治理（pilot，`.pilot.yml` + `docs/agent/`）

接入 `pilot` skill 的三阶段流程（status/plan/run），规划文档存于 `docs/agent/`（architecture / spec / tasks / roadmap / progress / followups / acceptance / research）。本仓库单主干（无 preview 分支），PR 需人工 review + approve 才能合并（未接入外部评审服务）。

### 7. 规划中 / 设计阶段

- **Spore Cast 付费视频栏目**（`video-column/`）：博客配套的短视频付费栏目完整设计文档（产品/架构/模块/数据模型/内容生产/路线图），接入 AirAccount + SBT + aPNTs 积分闭环，尚未开发。

### 8. 外部依赖 / Git 子模块（`submodules/`）

`wechat-article-formatter`、`wechat-article-formatter-skill`、`wechat-article-publisher-skill`、`wechat-content-pipeline`、`xiaohongshu-mcp`、`xiaoheishu`。

---

## 快速开始

```bash
# 安装依赖
pnpm install

# 本地开发预览（自动 kill 4321 端口）
./build-preview.sh
# 访问 http://localhost:4321

# 构建
pnpm build
```

---

## 写作教程

### 1. 创建新文章

在 `src/content/blog/` 目录下创建 `.md` 文件：

```bash
src/content/blog/
├── your-new-post.md     # 新建文件
└── ...
```

> 📄 **写作模板**: 参考 `docs/TEMPLATE.md` 快速开始

### 2. 文章 Frontmatter 格式

每篇文章顶部必须包含 YAML 格式的元数据：

```markdown
---
# 中文标题（必填）
title: '深度学习模型优化实践'

# 英文标题（可选）
titleEn: 'Deep Learning Model Optimization Practice'

# 中文描述（必填）
description: '记录模型训练过程中的优化技巧'

# 英文描述（可选）
descriptionEn: 'Optimization techniques from model training'

# 发布日期（必填）
pubDate: '2026-04-02'

# 更新日期（可选）
updatedDate: '2026-04-05'

# 文章分类（必填，5选1）
# - Tech-Experiment : 技术实验
# - Progress-Report : 进度汇报  
# - Research        : 专题研究
# - Tech-News       : 最新科技
# - Other           : 其他
category: 'Tech-Experiment'

# 标签（可选，可添加多个）
tags: ['deep-learning', 'optimization', 'pytorch']

# 封面图（可选）
heroImage: '../../assets/blog-placeholder-1.jpg'
---
```

### 3. 分类说明

| 分类 | 用途 | 图标 |
|------|------|------|
| `Tech-Experiment` | 技术实验、代码尝试 | 🔬 |
| `Progress-Report` | 项目进度、周报月报 | 📊 |
| `Research` | 深度研究、论文解读 | 🔍 |
| `Tech-News` | 行业动态、新技术 | 🚀 |
| `Other` | 随笔、杂谈 | 📝 |

### 4. 标签使用建议

标签用于更细粒度的文章归类，建议格式：

- **技术类**: `pytorch`, `transformer`, `multimodal`, `llm`
- **领域类**: `computer-vision`, `nlp`, `reinforcement-learning`
- **主题类**: `paper-reading`, `tutorial`, `benchmark`
- **项目类**: `project-mushroom`, `experiment-001`

在 Blog 页面，标签会显示在文章标题下方，方便快速识别文章关键词。

### 5. 双语文章写作

如需中英文双语显示，在正文中使用 `<!--EN-->` 标记分割：

```markdown
---
title: '多模态大模型研究'
titleEn: 'Multimodal Large Language Models'
category: 'Research'
tags: ['multimodal', 'llm', 'vision']
---

## 研究背景

多模态大语言模型结合了视觉和语言理解能力...

### 实验结果

在 COCO 数据集上达到 SOTA...

<!--EN-->

## Research Background

Multimodal large language models combine visual and linguistic understanding...

### Experimental Results

Achieved SOTA on COCO dataset...
```

**效果说明**:
- 有 `<!--EN-->`：左右两栏并排显示 🇨🇳 🇬🇧
- 无 `<!--EN-->`：中文内容自动居中，单栏显示

### 6. 纯中文文章

如果只有中文内容，直接写 Markdown，不需要 `<!--EN-->` 标记：

```markdown
---
title: '实验笔记'
description: '今天的实验记录'
category: 'Tech-Experiment'
tags: ['experiment', 'notes']
---

## 实验内容

今天测试了...
```

---

## 部署流程

### 方案 B：本地构建后上传（推荐）

```bash
# 1. 构建静态网站
pnpm build

# 2. 部署到 Cloudflare Pages
npx wrangler pages deploy dist
```
**注意**：这里你要预先注册cloudflare帐号并且本地login后才可以执行此命令。
或使用一键脚本：

```bash
./deploy.sh
```

### 完整发布流程 (M1 + M2 + M3)

本系统支持一键发布到多个平台：
- **M1**: Blog (Astro + Cloudflare Pages)
- **M2**: 微信公众号
- **M3**: 小红书 (通过 MCP)

#### 方式 1: 使用 auto-publish.sh（推荐）

```bash
# 1. 准备文章内容
echo "文章标题

文章内容..." > /tmp/article.txt

# 2. 一键发布（带图片）
./scripts/auto-publish.sh /tmp/article.txt /path/to/image.png

# 3. 一键发布（无图片）
./scripts/auto-publish.sh /tmp/article.txt
```

#### 方式 2: 交互式发布

直接告诉我：

```
发布这篇文章：

apfel: 在 Apple Silicon Mac 上零成本调用本地 Apple Intelligence

**apfel** 是一款专为搭载 Apple Silicon...

[粘贴截图]
```

**我自动完成**：
- 提取标题 → 生成英文 slug
- 压缩图片到 ~100KB
- 生成封面 (1200x630) + 文章内图 (1200宽)
- 创建 markdown
- 构建部署到 Blog
- 发布 WeChat 草稿
- 发布小红书 (如配置)

**图片压缩规则**：
| 步骤 | 质量 | 目标大小 |
|------|------|---------|
| 第1次 | 85% | ~100KB |
| 第2次 | 75% | 如果 >120KB |
| 第3次 | 65% | 如果还 >120KB |

#### 方式 3: 多平台分别发布

```bash
# 仅发布 Blog
pnpm build
npx wrangler pages deploy dist --project-name=$BLOG_PROJECT_NAME --branch=main

# 仅发布微信公众号
cd pipeline/m2 && node index.js "../../src/content/blog/article.md"

# 仅发布小红书
./publish-xhs.sh content.txt
```

---

### 手动发布流程

```bash
# 1. 写作完成后，本地预览
pnpm dev

# 2. 确认无误后构建
pnpm build

# 3. 提交代码到 GitHub
git add src/content/blog/your-new-post.md
git commit -m "feat: add new post about xxx"
git push origin main

# 4. 部署到线上
npx wrangler pages deploy dist --project-name=$BLOG_PROJECT_NAME --branch=main
```

---

## 评论系统配置

博客内置基于 **GitHub Discussions** 的评论系统（使用 Giscus）。

### 配置步骤

1. **开启 Discussions 功能**
   ```
   GitHub 仓库 -> Settings -> Features -> Discussions (启用)
   ```

2. **访问 Giscus 配置页面**
   - 打开 https://giscus.app/zh-CN
   - 填写仓库信息，生成配置

3. **填入环境变量**
   ```bash
   # .env 文件
   GISCUS_REPO=yourname/blog
   GISCUS_REPO_ID=从_giscus.app_获取
   GISCUS_CATEGORY=General
   GISCUS_CATEGORY_ID=从_giscus.app_获取
   ```

4. **重新构建部署**
   ```bash
   pnpm build
   npx wrangler pages deploy dist --project-name=$BLOG_PROJECT_NAME --branch=main
   ```

### 评论功能特点

- ✅ 使用 GitHub 账号登录
- ✅ 支持 Markdown 格式
- ✅ 支持表情反应
- ✅ 自动适配深色/浅色主题
- ✅ 懒加载，不影响页面性能

---

## 多用户配置

本系统支持多用户配置，你可以轻松切换不同的博客域名、微信公众号和小红书账号。

### 快速配置

1. **复制配置文件模板**
   ```bash
   cp config/users/default.js config/users/yourname.js
   ```

2. **编辑你的配置**
   ```javascript
   // config/users/yourname.js
   module.exports = {
     id: 'yourname',
     name: 'Your Name',
     
     blog: {
       projectName: 'your-blog-project',  // Cloudflare Pages 项目名
       domain: 'blog.yourdomain.com',      // 你的自定义域名
       
       brand: {
         name: 'Your Blog Name',
         description: 'Your blog description',
         twitter: '@yourtwitter',
         github: 'yourgithub',
       },
       
       watermark: {
         topLeft: 'Your Brand',
         bottomRight: 'Your Logo',
       },
     },
     
     wechat: {
       appId: process.env.WECHAT_APP_ID || '',
       appSecret: process.env.WECHAT_APP_SECRET || '',
       mpId: 'gh_xxxxxxxxxxxx',  // 公众号原始ID
       defaultAuthor: 'Your Name',
     },
     
     xiaohongshu: {
       mcpUrl: process.env.XHS_MCP_URL || 'http://localhost:3456',
       defaultTheme: 'blue',
     },
   };
   ```

3. **设置环境变量**
   ```bash
   # .env 文件
   BLOG_USER=yourname
   WECHAT_APP_ID=wx_xxxxxxxxxxxxxxxx
   WECHAT_APP_SECRET=your_secret_here
   WECHAT_MP_ID=gh_xxxxxxxxxxxx
   XHS_MCP_URL=http://localhost:3456
   ```

4. **切换用户**
   ```bash
   # 临时切换（当前终端）
   export BLOG_USER=yourname
   
   # 永久切换（写入 .env）
   echo "BLOG_USER=yourname" >> .env
   ```

### 查看所有用户

```bash
node -e "console.log(require('./config').listUsers())"
```

### 配置项说明

| 配置项 | 说明 | 获取方式 |
|--------|------|---------|
| `blog.projectName` | Cloudflare Pages 项目名 | [Cloudflare Dashboard](https://dash.cloudflare.com) |
| `blog.domain` | 自定义域名 | 你的域名服务商 |
| `wechat.appId` | 微信公众号 AppID | 微信公众平台 -> 设置与开发 -> 基本配置 |
| `wechat.appSecret` | 微信公众号 AppSecret | 同上（只显示一次，需保存） |
| `wechat.mpId` | 公众号原始 ID | 公众号设置页面 (gh_xxx) |
| `xiaohongshu.mcpUrl` | 小红书 MCP 服务地址 | 部署 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) |

### 多用户切换示例

```bash
# 用户 A 发布
export BLOG_USER=alice
./scripts/auto-publish.sh article.txt image.png

# 用户 B 发布  
export BLOG_USER=bob
./scripts/auto-publish.sh article.txt image.png
```

---

## 目录结构

```
blog/
├── src/
│   ├── content/blog/          # 👈 博客文章目录
│   │   ├── first-post.md
│   │   └── your-post.md
│   ├── layouts/BlogPost.astro # 文章页面布局
│   ├── pages/blog/index.astro # Blog 列表页
│   └── styles/global.css      # 全局样式
├── public/
│   └── favicon.svg           # 蘑菇图标 🍄
├── config/
│   ├── index.js              # 配置加载器
│   └── users/                # 用户配置目录
│       ├── default.js        # 默认配置模板
│       ├── mushroom.js       # Mushroom 用户配置
│       └── yourname.js       # 你的配置
├── dist/                     # 构建输出（不上传 GitHub）
├── deploy.sh                 # 部署脚本
├── scripts/
│   └── auto-publish.sh       # 自动发布脚本
└── README.md                 # 本文件
```

---

## 写作示例

### 示例 1：技术实验

```markdown
---
title: 'PyTorch 分布式训练实践'
titleEn: 'PyTorch Distributed Training Practice'
description: '记录 DDP 训练的配置过程和踩坑经历'
descriptionEn: 'Notes on DDP training setup and pitfalls'
pubDate: '2026-04-02'
category: 'Tech-Experiment'
tags: ['pytorch', 'distributed-training', 'ddp']
heroImage: '../../assets/blog-placeholder-1.jpg'
---

## 背景

最近需要将模型训练扩展到多卡...

<!--EN-->

## Background

Recently needed to scale model training to multiple GPUs...
```

### 示例 2：进度汇报

```markdown
---
title: 'Mushroom 项目周报 #12'
description: '本周进展：完成模型 v2 版本训练'
pubDate: '2026-04-02'
category: 'Progress-Report'
tags: ['weekly-report', 'mushroom-project']
---

## 本周完成

- [x] 模型 v2 训练完成
- [x] 发布技术文档
- [ ] 性能优化（延期）

## 下周计划

...
```

---

## 域名配置

博客已配置域名 `https://blog.mushroom.cv`（这个是我自用域名），如需修改：

1. 修改 `astro.config.mjs` 中的 `site` 字段
2. 在 Cloudflare Pages 控制台绑定自定义域名

---

## 问题排查

### 构建失败

```bash
# 清除缓存后重试
rm -rf dist/ .astro/
pnpm build
```

### 文章不显示

检查 frontmatter 格式：
- `title` 和 `pubDate` 必填
- `category` 必须是 5 个预设值之一
- YAML 语法是否正确（冒号后要有空格）

### 标签不显示

- `tags` 必须是数组格式：`tags: ['tag1', 'tag2']`
- 不能写成 `tags: 'tag1'` 或 `tags: tag1`

---

## 技术栈

- [Astro](https://astro.build) - 静态站点生成器
- [TypeScript](https://www.typescriptlang.org/) - 类型安全
- [Cloudflare Pages](https://pages.cloudflare.com/) - 托管与部署

---

**Mycelium - Infra, Protocols and Networks** 🍄

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).  
Copyright 2024-present MushroomDAO Contributors. See [NOTICE](./NOTICE) for attribution.
