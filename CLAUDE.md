# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mycelium Blog** — 多平台内容发布系统，三条发布流水线并行运作：

- **M1**: Astro 静态博客 → Cloudflare Pages
- **M2**: Markdown → WeChat 公众号草稿（Node.js + WeChat API）
- **M3**: 内容优化 → 小红书（Python + Dockerized Go MCP 服务）

## Common Commands

```bash
# 开发与构建（Astro 博客）
pnpm install          # 安装依赖（需 Node >=22.12.0）
pnpm dev              # 本地开发，http://localhost:4321
pnpm build            # 构建静态站点到 dist/
pnpm preview          # 预览构建结果

# 部署
./deploy.sh           # build + wrangler pages deploy dist

# 发布流程
./scripts/auto-publish.sh <content.txt>   # Blog + WeChat 一键发布
./publish-xhs.sh <content.txt>            # 小红书一键发布

# M3 测试套件
./pipeline/m3/test-suite.sh              # 健康检查、优化器、封面、渲染器、完整流水线

# 小红书 MCP 服务（Docker，运行在 Mac Mini）
./pipeline/deploy/xiaohongshu-mcp/start.sh   # 启动服务 + Tailscale 代理
```

## Architecture

### 目录职责

| 目录 | 职责 |
|------|------|
| `src/` | Astro 博客源码（内容在 `src/content/blog/`，Markdown/MDX） |
| `pipeline/m1/` | 博客封面生成、AI 润色、发布脚本 |
| `pipeline/m2/` | WeChat 公众号发布（Node.js，含 HTML 渲染器） |
| `pipeline/m3/` | 小红书内容优化、封面生成、MCP 客户端（Python） |
| `pipeline/deploy/xiaohongshu-mcp/` | Dockerized Go MCP 服务，含 cookie 持久化和 Tailscale 代理 |
| `config/users/` | 多用户配置（每用户一个 JS 文件，含博客域名、微信凭据、小红书 URL） |
| `submodules/` | Git 子模块（xiaohongshu-mcp Go 源码、微信格式化工具等） |
| `.agents/skills/` | Claude agent skill 定义（`blog-publisher` 等） |

### 多用户配置系统

- `config/index.js` 按 `BLOG_USER` 环境变量加载 `config/users/{user}.js`
- 当前活跃用户：`mushroom`（对应 `config/users/mushroom.js`）
- 每个用户配置包含：Cloudflare 项目名、域名、WeChat AppID/Secret/MPID、小红书 MCP URL

### 小红书 MCP 服务

- **运行位置**：Mac Mini（Apple Silicon），通过 Tailscale VPN 访问
- **本地端口**：`127.0.0.1:3456`（容器内部 18060）
- **关键 API**：
  - `POST /api/v1/login/qrcode` — 获取登录二维码
  - `GET /api/v1/login/status` — 检查登录状态
  - `POST /api/v1/publish` — 发布图文笔记
  - `GET /health` — 健康检查
- **Cookie 持久化**：`pipeline/deploy/xiaohongshu-mcp/cookies/cookies.json`
- **服务代理**：`proxy.py` 通过 Tailscale 暴露服务到内网

### 文章结构约定

- 所有文章文件名必须用英文（不允许中文文件名）
- Frontmatter 字段：`title`、`description`、`pubDate`、`category`、`tags`、`lang`
- 5 个分类：`Tech-Experiment`、`Progress-Report`、`Research`、`Tech-News`、`Other`
- 双语文章格式：中文主体 + `<!--EN-->` 分隔符后接英文版

### 发布触发词（AI Agent）

当用户说"发布文章"、"发布blog"、"发布公众号"时，读取并执行 `.agents/skills/blog-publisher/SKILL.md` 中的标准流程。

## Key Files

- `astro.config.mjs` — Astro 配置（站点域名、集成）
- `wrangler.toml` — Cloudflare Pages 配置
- `src/consts.ts` — 站点标题、描述等全局常量
- `src/content.config.ts` — 博客内容集合 schema
- `.env.example` — 所有环境变量模板（实际 `.env` 不入版本控制）
- `pipeline/deploy/xiaohongshu-mcp/docker-compose.yml` — MCP 服务 Docker 配置
