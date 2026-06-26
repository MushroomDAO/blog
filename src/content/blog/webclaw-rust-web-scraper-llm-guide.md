---
title: "Webclaw 开发者使用指南：用 Rust 爬虫给 AI 喂干净的 Markdown"
titleEn: "Webclaw Developer Guide: Rust Web Scraper for LLM-Ready Markdown"
description: "Webclaw 是一款 Rust 编写的本地优先网页内容提取工具，MCP 一键接入 Claude/Cursor，自动去噪输出 LLM 专用 Markdown，支持单页抓取、全站爬虫、批量爬取、页面对比、品牌元素提取，AGPL-3.0 开源，1500+ Stars。"
descriptionEn: "Webclaw is a local-first Rust web extraction tool with MCP support for Claude/Cursor — auto-denoises pages and outputs LLM-ready markdown. Supports scraping, crawling, batch ops, diffs, and brand extraction. AGPL-3.0, 1500+ Stars."
pubDate: "2026-06-26"
updatedDate: "2026-06-26"
category: "Tech-News"
tags: ["网页抓取", "MCP", "Claude Code", "Rust", "RAG", "LLM工具", "开源工具", "AI Agent"]
heroImage: "../../assets/images/webclaw-rust-web-scraper-llm-guide-banner.jpg"
---

> **一句话结论（BLUF）**：如果你的 AI 工作流经常被"网页内容太脏"卡住，Webclaw 是目前最彻底解决这个问题的开源工具——本地 Rust 引擎零依赖浏览器，MCP 接入后让 Claude/Cursor 直接拿到干净的 Markdown，大幅降低 token 消耗。

GitHub：https://github.com/0xMassi/webclaw  
官网：https://webclaw.io  
⭐ 1568 Stars · 🍴 171 Forks · AGPL-3.0 开源 · Rust · 发布于 2026-03

---

## 为什么网页内容对 LLM 来说这么"脏"？

让 AI 助手"上网查资料"，本质上有两个层次的难题：

**第一层**：拿到页面内容本身——JS 渲染、反爬机制、登录墙、空壳 SPA……

**第二层**：拿到的内容能用——导航栏、广告、侧边栏、重复的页脚、内联 `<style>/<script>` 标签……一个普通网页的 HTML 里，真正有用的文字可能不到 20%，剩下的全是噪声，直接塞给 LLM 既浪费 token，也干扰上下文。

**Webclaw** 同时解决这两个问题：

- **纯 Rust 引擎**：没有 Chrome 依赖，没有 Puppeteer，启动即运行。内置 QuickJS 沙箱处理 JS 数据岛（Next.js `__NEXT_DATA__`、React 预加载状态等），静态路径覆盖不到的才进沙箱，速度快且轻。
- **Readability 算法**：文本密度评分 + 语义标签权重 + 链接密度惩罚，精准提取主内容区；CSS 选择器 `--include / --exclude` 精细控制。
- **LLM 专用 9 步优化管道**：去图片、去强调符号、链接去重、统计合并、空白折叠，输出 `llm` 格式，比 `markdown` 格式再精简 30-50%。

---

## 快速安装

### 方式一：MCP 客户端一键配置（推荐）

适合 Claude Desktop、Claude Code、Cursor、Windsurf、Codex CLI 等 MCP 兼容工具：

```bash
npx create-webclaw
```

安装程序自动检测本机已安装的 AI 客户端，并写入对应配置文件，无需手动编辑 JSON。

### 方式二：Homebrew（macOS / Linux）

```bash
brew tap 0xMassi/webclaw
brew install webclaw
```

### 方式三：Docker

```bash
docker run --rm ghcr.io/0xmassi/webclaw https://example.com
```

### 方式四：Cargo（从源码编译）

```bash
# 仅 CLI
cargo install --git https://github.com/0xMassi/webclaw.git webclaw-cli

# MCP 服务器
cargo install --git https://github.com/0xMassi/webclaw.git webclaw-mcp
```

编译前置依赖（Ubuntu/Debian）：

```bash
sudo apt install -y pkg-config libssl-dev cmake clang git build-essential
```

### 方式五：预构建二进制

从 GitHub Releases 页面下载 macOS / Linux / Windows 对应的二进制文件，解压即用。

---

## CLI 核心用法

### 抓取单页

```bash
# 默认 markdown 格式
webclaw https://stripe.com --format markdown

# LLM 专用格式（更精简，推荐 RAG 场景）
webclaw https://docs.anthropic.com --format llm

# 只保留主内容区
webclaw https://example.com/blog/post --only-main-content

# 精细控制包含/排除区域
webclaw https://example.com \
  --include "article, main, .content" \
  --exclude "nav, footer, .sidebar, .ad"
```

### 爬取整站

```bash
# 爬取 Rust 文档，深度 2 层，最多 50 页
webclaw https://docs.rust-lang.org --crawl --depth 2 --max-pages 50
```

适合把产品文档、help center、技术博客批量入库 RAG。

### 批量抓取

在 MCP 工具层通过 `batch` 工具并行抓取多个 URL，也可通过 REST API 的 `POST /v1/batch` 提交批量任务。

### 页面变更对比（竞品监控必备）

```bash
# 先存快照
webclaw https://example.com/pricing --format json > pricing-old.json

# 之后对比
webclaw https://example.com/pricing --diff-with pricing-old.json
```

输出结构化的 diff，可集成到定时任务中，自动检测竞品定价/功能变更。

### 品牌元素提取

```bash
webclaw https://github.com --brand
```

从 DOM 结构和 CSS 提取品牌色（hex）、字体族、Logo URL、社交元数据——做竞品品牌分析或快速建 Design Token 时很有用。

---

## 五种输出格式

| 格式 | 适合场景 |
|---|---|
| `markdown` | 保留结构的清洁内容，通用 |
| `llm` | 最紧凑的 Agent/RAG 上下文，**token 最少** |
| `text` | 纯文本，最小格式化 |
| `json` | 含元数据、链接、图片、提取字段的结构化数据 |
| `html` | 清洁过的 HTML，供自定义后处理 |

---

## MCP 接入：让 Claude/Cursor 直接用

### 手动配置

`npx create-webclaw` 会自动配置，也可手动在 `claude_desktop_config.json` 或 `mcp.json` 中添加：

```json
{
  "mcpServers": {
    "webclaw": {
      "command": "~/.webclaw/webclaw-mcp"
    }
  }
}
```

### 可用的 12 个 MCP 工具

| 工具 | 功能 | 本地运行 |
|---|---|:-:|
| `scrape` | 提取单 URL，支持所有格式 | ✅ |
| `crawl` | 同源链接爬取 | ✅ |
| `map` | URL 发现（不提取内容） | ✅ |
| `batch` | 并行多 URL 提取 | ✅ |
| `extract` | 页面内容 → 结构化 JSON | ✅（本地/配置 LLM）|
| `summarize` | 页面摘要 | ✅（本地/配置 LLM）|
| `diff` | 内容快照对比 | ✅ |
| `brand` | 品牌元素提取 | ✅ |
| `research` | 多源研究工作流 | 云端 API |
| `search` | 网页搜索 + 提取结果 | 本地（需 Serper key）|
| `list_extractors` | 查看内置垂直提取器列表 | ✅ |
| `vertical_scrape` | 垂直站点专项提取 | ✅ |

接入后，你可以直接对 Claude 说：

```
抓取这几个竞品定价页面，总结它们的差异。
```

```
爬取这个文档站并为 RAG 索引准备干净的上下文。
```

```
提取这家公司网站的品牌色、字体和 Logo。
```

---

## SDK 接入

### TypeScript / JavaScript

```bash
npm install @webclaw/sdk
```

```ts
import { Webclaw } from "@webclaw/sdk";

const client = new Webclaw({ apiKey: process.env.WEBCLAW_API_KEY! });

const page = await client.scrape({
  url: "https://example.com",
  formats: ["markdown"],
  only_main_content: true,
});

console.log(page.markdown);
```

### Python

```bash
pip install webclaw
```

```python
from webclaw import Webclaw

client = Webclaw(api_key="wc_your_key")

page = client.scrape(
    "https://example.com",
    formats=["markdown"],
    only_main_content=True,
)

print(page.markdown)
```

### Go

```bash
go get github.com/0xMassi/webclaw-go
```

### cURL / REST API

```bash
curl -X POST https://api.webclaw.io/v1/scrape \
  -H "Authorization: Bearer $WEBCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": ["markdown"],
    "only_main_content": true
  }'
```

---

## 配置参考

| 环境变量 | 说明 |
|---|---|
| `WEBCLAW_API_KEY` | 云端 API Key（webclaw.io 托管版）|
| `OLLAMA_HOST` | 本地 Ollama URL（用于 extract/summarize）|
| `OPENAI_API_KEY` | OpenAI 兼容 LLM 密钥 |
| `OPENAI_BASE_URL` | OpenAI 兼容接口地址 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `ANTHROPIC_BASE_URL` | Anthropic 兼容接口地址 |
| `WEBCLAW_PROXY` | 单条代理 URL |
| `WEBCLAW_PROXY_FILE` | 代理池文件路径（按行，每次请求随机轮换）|
| `SERPER_API_KEY` | Serper 网页搜索 API Key（`search` 工具本地模式）|

LLM 优先级链：**Ollama（本地）→ OpenAI → Gemini → Anthropic**，按配置的密钥自动降级。

---

## 架构速览：7 个 Crate

```
webclaw/
  crates/
    webclaw-core     纯提取引擎，WASM 安全，零网络依赖
    webclaw-fetch    HTTP 客户端（wreq + BoringSSL TLS 指纹）、爬虫、批量、代理池
    webclaw-llm      LLM provider 链（Ollama/OpenAI/Gemini/Anthropic）
    webclaw-pdf      PDF 文本提取
    webclaw-mcp      MCP 服务器（基于 rmcp 官方 Rust SDK）
    webclaw-cli      命令行二进制
    webclaw-server   轻量 Axum REST API（自托管版本）
```

**core** 是纯逻辑层：Readability 算法、噪声过滤、JSON 数据岛提取、Markdown 转换、diff 引擎、品牌提取——完全无网络 I/O，可以独立用于自定义管道。

**fetch** 用 wreq 实现 BoringSSL TLS 指纹伪装，模拟 Chrome 145、Firefox 135、Safari 18.3.1 等浏览器特征，内置 ~30 个垂直站点提取器（Amazon、GitHub、LinkedIn、YouTube、arXiv、HuggingFace 等）。

---

## 本地优先 vs 托管 API

| | 本地（CLI/MCP/自托管 server）| 云端（webclaw.io）|
|---|---|---|
| JS 渲染 | QuickJS 沙箱（部分）| 完整 Headless 支持 |
| 反爬突破 | 依赖代理池 | 内置托管能力 |
| 搜索功能 | 需自备 Serper Key | 内建 |
| 异步爬取作业 | 同步执行 | 支持 |
| 数据隐私 | 完全本地 | 需信任托管服务 |
| 成本 | 免费 | 按量付费 |

**推荐策略**：日常开发和 RAG 入库走本地；遇到强反爬、JS SPA 渲染页面、需要大规模并行爬取时升级托管 API。

---

## 典型使用场景

| 场景 | 推荐命令/工具 |
|---|---|
| Claude Code / Cursor 联网检索 | `npx create-webclaw` → MCP `scrape` |
| 文档站全量入库 RAG | `webclaw --crawl --depth 3` |
| 竞品定价监控 | `webclaw --diff-with snapshot.json` 定期比对 |
| 结构化数据提取 | MCP `extract` + JSON schema |
| 多源研究汇总 | MCP `research`（云端）|
| 品牌情报 | `webclaw --brand` |
| Python/TS 应用集成 | SDK `client.scrape()` |

---

## 贡献与社区

目前最欢迎的贡献方向：
- 实际 Agent 和 RAG 工作流示例
- 上报提取效果不佳的页面（附 URL、命令、期望输出）
- 在更多 Linux/macOS 环境测试 CLI

提 Bug 时请移除 Cookie、私有 Token 和客户数据再贴日志。

Discord：https://discord.gg/KDfd48EpnW  
X / Twitter：https://x.com/webclaw_io  
Issues：https://github.com/0xMassi/webclaw/issues

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: If dirty web content keeps breaking your AI workflows, Webclaw is the most thorough open-source fix available — a local Rust engine with no browser dependency, MCP integration so Claude/Cursor gets clean markdown directly, dramatically cutting token cost.

GitHub: https://github.com/0xMassi/webclaw  
Homepage: https://webclaw.io  
⭐ 1568 Stars · 🍴 171 Forks · AGPL-3.0 · Rust · Released 2026-03

---

## Why Is Web Content So Dirty for LLMs?

Getting AI assistants to "look things up online" has two distinct problems:

**Layer 1**: Getting the page content at all — JS rendering, anti-bot measures, login walls, empty SPA shells.

**Layer 2**: Making the content usable — navbars, ads, sidebars, repeated footers, inline `<style>` and `<script>` tags. In a typical webpage, less than 20% of the HTML is useful content. The rest is noise that wastes tokens and pollutes the context window.

**Webclaw** solves both:

- **Pure Rust engine**: No Chrome, no Puppeteer. A built-in QuickJS sandbox handles JS data islands (Next.js `__NEXT_DATA__`, React preloaded state, etc.) — only invoked when actually needed, so the static path stays fast.
- **Readability algorithm**: Text density scoring, semantic tag weighting, link density penalty — precisely targets the main content area. Fine-grained control via CSS `--include / --exclude` selectors.
- **9-step LLM optimization pipeline**: Strips images, emphasis noise, duplicate links, redundant stats, and whitespace. The `llm` format is 30–50% smaller than `markdown`.

---

## Quick Installation

### Option 1: One-command MCP setup (recommended)

For Claude Desktop, Claude Code, Cursor, Windsurf, Codex CLI, and other MCP clients:

```bash
npx create-webclaw
```

Auto-detects installed AI clients and writes the correct config.

### Option 2: Homebrew (macOS / Linux)

```bash
brew tap 0xMassi/webclaw
brew install webclaw
```

### Option 3: Docker

```bash
docker run --rm ghcr.io/0xmassi/webclaw https://example.com
```

### Option 4: Cargo (build from source)

```bash
cargo install --git https://github.com/0xMassi/webclaw.git webclaw-cli
cargo install --git https://github.com/0xMassi/webclaw.git webclaw-mcp
```

Ubuntu/Debian prerequisites:

```bash
sudo apt install -y pkg-config libssl-dev cmake clang git build-essential
```

### Option 5: Prebuilt binaries

Download macOS, Linux, or Windows binaries from GitHub Releases — unzip and run.

---

## CLI Core Usage

### Scrape a single page

```bash
# Default markdown
webclaw https://stripe.com --format markdown

# LLM-optimized format (recommended for RAG)
webclaw https://docs.anthropic.com --format llm

# Main content only
webclaw https://example.com/blog/post --only-main-content

# Fine-grained CSS selector control
webclaw https://example.com \
  --include "article, main, .content" \
  --exclude "nav, footer, .sidebar, .ad"
```

### Crawl an entire site

```bash
webclaw https://docs.rust-lang.org --crawl --depth 2 --max-pages 50
```

Great for bulk-indexing docs, help centers, or technical blogs into RAG pipelines.

### Page diff (competitor monitoring)

```bash
# Save snapshot
webclaw https://example.com/pricing --format json > pricing-old.json

# Compare later
webclaw https://example.com/pricing --diff-with pricing-old.json
```

Structured diff output — wire it into a cron job for automated pricing/changelog tracking.

### Brand asset extraction

```bash
webclaw https://github.com --brand
```

Extracts brand colors (hex), font stacks, logo URLs, and social metadata from DOM and CSS.

---

## Five Output Formats

| Format | Best for |
|---|---|
| `markdown` | Clean structured content, general use |
| `llm` | Most compact context for agents and RAG — **fewest tokens** |
| `text` | Plain text, minimal formatting |
| `json` | Structured metadata, links, images, extracted fields |
| `html` | Cleaned HTML for custom downstream processing |

---

## MCP Integration: Claude and Cursor Direct Access

### Manual config

```json
{
  "mcpServers": {
    "webclaw": {
      "command": "~/.webclaw/webclaw-mcp"
    }
  }
}
```

### 12 MCP tools

| Tool | What it does | Local |
|---|---|:-:|
| `scrape` | Extract one URL in any format | ✅ |
| `crawl` | Follow same-origin links | ✅ |
| `map` | Discover URLs without extracting | ✅ |
| `batch` | Parallel multi-URL extraction | ✅ |
| `extract` | Page content → structured JSON | ✅ (local/configured LLM) |
| `summarize` | Page summary | ✅ (local/configured LLM) |
| `diff` | Content snapshot comparison | ✅ |
| `brand` | Brand identity extraction | ✅ |
| `research` | Multi-source research workflow | Hosted API |
| `search` | Web search + scrape results | Local (needs Serper key) |
| `list_extractors` | List built-in vertical extractors | ✅ |
| `vertical_scrape` | Site-specific extraction | ✅ |

After connecting, just tell Claude:

```
Scrape these competitor pricing pages and summarize the differences.
```

```
Crawl this docs site and prepare clean context for a RAG index.
```

---

## SDK Integration

### TypeScript

```bash
npm install @webclaw/sdk
```

```ts
import { Webclaw } from "@webclaw/sdk";
const client = new Webclaw({ apiKey: process.env.WEBCLAW_API_KEY! });
const page = await client.scrape({ url: "https://example.com", formats: ["markdown"], only_main_content: true });
console.log(page.markdown);
```

### Python

```bash
pip install webclaw
```

```python
from webclaw import Webclaw
client = Webclaw(api_key="wc_your_key")
page = client.scrape("https://example.com", formats=["markdown"], only_main_content=True)
print(page.markdown)
```

### Go

```bash
go get github.com/0xMassi/webclaw-go
```

---

## Configuration Reference

| Variable | Purpose |
|---|---|
| `WEBCLAW_API_KEY` | Hosted API key (webclaw.io) |
| `OLLAMA_HOST` | Local Ollama URL (for extract/summarize) |
| `OPENAI_API_KEY` | OpenAI-compatible LLM key |
| `OPENAI_BASE_URL` | OpenAI-compatible base URL |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `ANTHROPIC_BASE_URL` | Anthropic-compatible base URL |
| `WEBCLAW_PROXY` | Single proxy URL |
| `WEBCLAW_PROXY_FILE` | Proxy pool file (one per line, rotated per request) |
| `SERPER_API_KEY` | Serper search key (enables local `search` tool) |

LLM chain priority: **Ollama (local-first) → OpenAI → Gemini → Anthropic** — falls back automatically based on which keys are set.

---

## Architecture: 7 Crates

```
webclaw-core     Pure extraction. WASM-safe. Zero network I/O.
webclaw-fetch    HTTP (wreq + BoringSSL TLS fingerprinting), crawler, batch, proxy pool
webclaw-llm      LLM provider chain (Ollama / OpenAI / Gemini / Anthropic)
webclaw-pdf      PDF text extraction
webclaw-mcp      MCP server (official rmcp Rust SDK, stdio transport)
webclaw-cli      CLI binary
webclaw-server   Lightweight Axum REST API (self-hostable)
```

**webclaw-core** is pure logic: Readability scoring, noise filtering, JS data island parsing, Markdown conversion, diff engine, brand extraction. No network deps — usable standalone in custom pipelines.

**webclaw-fetch** uses wreq with BoringSSL TLS fingerprinting to emulate Chrome 145, Firefox 135, Safari 18.3.1, and others. Includes ~30 vertical extractors for Amazon, GitHub, LinkedIn, YouTube, arXiv, HuggingFace, npm, PyPI, Reddit, and more.

---

## FAQ

**Q: Does it require a browser or Playwright?**  
No. Pure Rust, no browser dependency. QuickJS handles JS data islands for common SPA patterns without launching Chrome.

**Q: Can I self-host the REST API?**  
Yes. `webclaw-server` is a lightweight Axum server — `docker-compose.yml` is in the repo. Note it lacks anti-bot and JS rendering compared to the hosted API.

**Q: What's the difference between `markdown` and `llm` format?**  
`llm` runs a 9-step compression pipeline on top of `markdown`: strips images, emphasis, deduplicates links, collapses whitespace. Typically 30–50% smaller. Use `llm` for RAG and agent context; `markdown` when you need a human-readable rendering.

**Q: How does it handle JavaScript-heavy pages without a browser?**  
A QuickJS sandbox runs inline `<script>` tags to recover JS-assigned blobs (`window.__PRELOADED_STATE__`, Next.js `self.__next_f`, SvelteKit data islands). For truly dynamic, AJAX-only content, the hosted API with full headless rendering is needed.

**Q: Can I use Ollama with the `extract` and `summarize` tools?**  
Yes. Set `OLLAMA_HOST=http://localhost:11434` and webclaw will route LLM tasks to your local Ollama instance. The LLM chain tries local-first.

**Q: Is AGPL-3.0 compatible with my commercial project?**  
AGPL requires that modified versions served over a network publish their source. If you need a commercial license, check https://webclaw.io for options.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
