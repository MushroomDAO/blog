# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mycelium Protocol 生态上下文

@/Users/jason/Dev/Brood/protocol/MISSION.md
@/Users/jason/Dev/Brood/protocol/PGL/CONTEXT.md
@/Users/jason/Dev/Brood/orgs/mycelium/PROFILE.md
@/Users/jason/Dev/Brood/orgs/mycelium/INTERFACES.md

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
| `.agents/skills/` | Claude agent skill 定义（`blog-publisher`、`banner-creator`、`mage-vl` 等），提交进仓库的源 |
| `.claude/skills/` | 上面那些 skill 的本地镜像，Claude Code 实际从这里加载；**未跟踪、是生成物**，改完 `.agents/` 跑 `scripts/bootstrap-machine.sh` 重新镜像，别手改 |
| `.agents/memory/` | **私有仓库 `MushroomDAO/blog-memory` 的 clone**（本仓库公开，记忆含账号 ID/私人邮箱/密钥文件路径索引，故隔离）；对齐用 `scripts/sync-memory.sh`，它会自动提交并推回去 |
| `.agents/codex-skills/` | Codex 侧插图 skill（小M / 小J / Baobao），bootstrap 会装到 `~/.codex/skills/` 和 `~/.claude/skills/` |

### 配图的视觉理解（mage-vl skill）

本机跑着 Mage-VL 视觉语言模型，可以读图片和视频，媒体不出本机。典型用途：给
`src/assets/images/` 的 banner 批量补 alt 文本、按规则筛图（如「有没有出现人物」）、
检查配图和文章主题是否匹配、给视频抽帧。用法见 `.agents/skills/mage-vl/SKILL.md`。

注意它**没有音频塔，做不了语音转文字**；筛图只出判定结果，不会自动删改文件。

### 换机与 24/7 自动运行

仓库要在 Mac mini 上 24 小时跑，MacBook Pro 保留完整能力做手动介入。

- **新机器开工**：`scripts/bootstrap-machine.sh`（幂等，随时可重跑；`--check-only` 只体检）
- **归属锁**：`config/runner.json` 的 `owner` 决定谁能自动跑有副作用的任务。
  `run-daily.sh`（重复采集）和 `newsletter/local-fallback.sh`（**重复发信**）在入口
  `source scripts/require-owner.sh`，非 owner 机器静默让路。手动跑加 `FORCE_RUN=1`。
- **装不了的四样**：`.env` 凭据、FLUX 模型(5.9GB)、小红书 Chrome Profile 登录态、
  8042 LaunchAgent —— 必须手动搬，bootstrap 会明确报出来而不是假装成功。
- **记忆在私有仓库**：`MushroomDAO/blog-memory`，新机器需要 SSH key 才 clone 得下来。

完整交接步骤和「不跟 git 走的东西」清单见 `docs/RUNNER.md`。

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
