---
title: "Obscura：用 Rust 重写无头浏览器，内存从 200MB 降到 30MB，登顶 GitHub Trending"
titleEn: "Obscura: Headless Browser Rewritten in Rust — Memory Down From 200MB to 30MB, GitHub Trending #1"
description: "Obscura 是专为 AI Agent 和网页自动化打造的轻量级 Rust 无头浏览器。无需 Node.js 和 Chrome，通过 V8 执行 JavaScript，兼容 Puppeteer/Playwright/MCP，内存仅 30MB（Chrome 的 1/7），页面加载 85ms，启动即时。2.7万+ Stars 登顶 GitHub Trending，并直接启发了 Cloudflare Kitesurf 的原型。"
descriptionEn: "Obscura is a lightweight Rust headless browser built for AI agents and web automation. No Node.js or Chrome needed — runs real JavaScript via V8, is Puppeteer/Playwright/MCP compatible, uses only 30MB RAM (1/7th of Chrome), loads pages in 85ms, and starts instantly. 27k+ stars, GitHub Trending #1, and directly inspired Cloudflare's Kitesurf prototype."
pubDate: 2026-09-07
updatedDate: 2026-09-07
category: Tech-Experiment
tags: ["Rust", "浏览器", "AI Agent", "爬虫", "MCP", "开源", "Playwright", "Puppeteer", "无头浏览器", "自动化"]
heroImage: "../../assets/images/obscura-rust-headless-browser-ai-agent-web-scraping-mcp-banner.jpg"
author: "Mycelium Protocol"
---

你的 AI Agent 要操作浏览器，标准方案是什么？

大概率是：装 Node.js、装 Chromium、用 Playwright 或 Puppeteer，然后发现每启动一个浏览器实例就要吃掉 200MB 内存，启动要等 2 秒，批量任务跑起来服务器内存告警。

**Obscura** 说：Chrome 太重了，我们用 Rust 重写一个。

2.7 万+ Stars，GitHub Trending 第一，并且直接启发了 Cloudflare 新一代 Agent 浏览器 Kitesurf 的原型。

GitHub：[h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura)

---

## 关键数字对比

| 指标 | Obscura | Headless Chrome |
|------|---------|-----------------|
| 内存占用 | **30 MB** | 200+ MB |
| 二进制大小 | **70 MB** | 300+ MB |
| 页面加载 | **85 ms** | ~500 ms |
| 启动时间 | **即时** | ~2 秒 |
| 反检测 | **内置** | 无 |
| Puppeteer 兼容 | ✓ | ✓ |
| Playwright 兼容 | ✓ | ✓ |

内存降低到原来的 1/7，页面加载快 6 倍，启动从 2 秒变成即时——这不是边际优化，而是一个量级的差距。

---

## 技术原理：为什么可以这么轻

Obscura 是从头用 Rust 编写的无头浏览器引擎，不是对 Chrome 的封装。

**JavaScript 执行**：嵌入 V8（Chrome 的 JavaScript 引擎），但只有 V8，没有 Chrome 的其他重量级组件（Blink 渲染器、完整 Chromium 架构）。

**渲染层**：自研的 CSS 布局和绘制引擎，提供视口截图、全页面截图、滚动感知的 fixed/sticky 几何处理、基于活动驱动的 CDP 屏幕流，以及无需启动 Chromium 的 PDF 导出。

**协议层**：完整实现 Chrome DevTools Protocol（CDP），所以 Puppeteer 和 Playwright 可以直接连接——对它们来说，Obscura 就是一个正常的 Chrome。

这个设计的关键洞察：大多数网页自动化场景不需要 Chromium 的全部功能，需要的只是：
1. 能跑 JavaScript（V8）
2. 能操作 DOM
3. 能截图和导出
4. 符合 Puppeteer/Playwright 的接口

Obscura 只做这四件事，做得更快更轻。

---

## 核心功能

### 无依赖安装

```bash
# macOS Apple Silicon
curl -LO https://github.com/h4ckf0r0day/obscura/releases/latest/download/obscura-aarch64-macos.tar.gz
tar xzf obscura-aarch64-macos.tar.gz

# 立即使用
./obscura fetch https://example.com --eval "document.title"
```

没有 Node.js，没有 npm，没有 Chrome——一个二进制文件搞定。

### CLI 常用命令

```bash
# 抓取页面标题
obscura fetch https://example.com --eval "document.title"

# 渲染 JavaScript 后导出 HTML
obscura fetch https://news.ycombinator.com --dump html

# 截图
obscura fetch https://example.com --screenshot page.png

# 提取所有链接
obscura fetch https://example.com --dump links

# 纯文本
obscura fetch https://example.com --dump text

# 列出所有子资源 URL（NDJSON 格式）
obscura fetch https://example.com --dump assets

# 通过代理抓取
obscura fetch https://example.com --proxy socks5://127.0.0.1:1080
```

### Puppeteer/Playwright 替代

作为 CDP 服务器启动：

```bash
# 启动 CDP 服务器，Puppeteer/Playwright 直接连接
obscura serve --port 9222
```

代码层面无需修改，把 Chrome 的 WebSocket 地址换成 `ws://localhost:9222` 即可。

### MCP 集成

Obscura 原生支持 MCP（Model Context Protocol），可以直接作为 AI Agent 的浏览器工具。配套的 [epicsagas/obscura-plugin](https://github.com/epicsagas/obscura-plugin) 提供了专门面向 AI Agent 的 MCP server 封装，包含网页抓取、JavaScript 渲染和浏览器自动化能力。

### Docker 部署

```bash
docker run -d --name obscura -p 127.0.0.1:9222:9222 h4ckf0r0day/obscura
```

基于 `distroless/cc:nonroot` 多阶段构建，压缩后约 57 MB，无 shell，无包管理器，以 uid 65532 运行。

### 反检测（Stealth 构建）

带 `-stealth` 后缀的版本内置反检测传输层（通过 BoringSSL），对抗常见的爬虫检测机制。四个构建变体：

| 变体 | 渲染 | 反检测 |
|------|------|--------|
| 默认 | ✓ | ✗ |
| `-stealth` | ✓ | ✓ |
| `-no-render` | ✗ | ✗ |
| `-no-render-stealth` | ✗ | ✓ |

无需渲染的场景（只抓取 HTML，不需要截图）可以用 `-no-render` 版本，体积更小、速度更快。

---

## Cloudflare Kitesurf：最好的背书

README 里有一段值得注意的信息：

> Cloudflare began by porting Obscura to Workers while developing its new agent-first browser — Kitesurf.

Cloudflare 在开发 Kitesurf（专为 AI Agent 设计的浏览器服务）时，从 Obscura 出发写了第一个原型。这不是普通的"灵感来源"，而是 Cloudflare 工程团队直接基于 Obscura 的设计进行 Workers 移植。

---

## 适合的场景

**最适合**：
- **批量网页抓取**：内存低，可以同时跑大量实例
- **AI Agent 浏览器工具**：MCP 集成，响应速度快
- **截图服务**：内置原生渲染，无需 Chromium
- **本地 MCP 工具**：单二进制，无依赖，本地运行成本极低
- **CI/CD 中的浏览器测试**：70MB 镜像，Playwright 兼容

**不适合**：
- 需要完整 CSS/渲染规范兼容性的场景（Obscura 自研渲染层，可能有细微差异）
- 需要处理 WebGL/Canvas 密集型页面
- 需要 Chrome Extension 支持

---

## 当前状态与路线图

项目正在活跃开发，Obscura Cloud（托管版本，含住宅代理和管理基础设施）在等待名单阶段。开源引擎保持 Apache-2.0，承诺不做功能锁定。

支持平台：Linux x86_64/ARM64、macOS Apple Silicon/Intel、Windows；也可以通过 AUR（Arch）和 NixOS 安装。

---

## 相关链接

- GitHub：[h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura)
- 文档：[docs.obscura.sh](https://docs.obscura.sh/)
- MCP 插件：[epicsagas/obscura-plugin](https://github.com/epicsagas/obscura-plugin)
- Cloudflare Kitesurf 工程博客：[blog.cloudflare.com/kitesurf/](https://blog.cloudflare.com/kitesurf/)

<!--EN-->

What's your standard setup when an AI agent needs to control a browser?

Probably: install Node.js, install Chromium, use Playwright or Puppeteer — then discover each browser instance eats 200MB of RAM, startup takes 2 seconds, and running batch tasks triggers server memory alerts.

**Obscura** says: Chrome is too heavy. We rewrote a browser in Rust.

27k+ stars, GitHub Trending #1, and it directly inspired the prototype for Cloudflare's next-generation agent browser, Kitesurf.

GitHub: [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura)

---

## The Numbers

| Metric | Obscura | Headless Chrome |
|--------|---------|-----------------|
| Memory | **30 MB** | 200+ MB |
| Binary size | **70 MB** | 300+ MB |
| Page load | **85 ms** | ~500 ms |
| Startup | **Instant** | ~2s |
| Anti-detect | **Built-in** | None |
| Puppeteer | ✓ | ✓ |
| Playwright | ✓ | ✓ |

Memory reduced to 1/7th, page loading 6× faster, startup from 2 seconds to instant — this isn't incremental improvement, it's an order of magnitude.

---

## Why It Can Be This Light

Obscura is a headless browser engine written from scratch in Rust, not a Chrome wrapper.

**JavaScript**: Embeds V8 (Chrome's JavaScript engine) — just V8, without Chrome's other heavyweight components (Blink renderer, full Chromium architecture).

**Rendering**: A custom CSS layout and paint engine providing viewport screenshots, full-page screenshots, scroll-aware fixed/sticky geometry, activity-driven CDP screencasting, and raster PDF export — all without starting Chromium.

**Protocol**: Full Chrome DevTools Protocol (CDP) implementation. To Puppeteer and Playwright, Obscura looks like a normal Chrome.

The key insight: most web automation scenarios don't need all of Chromium's capabilities. What they need is:
1. JavaScript execution (V8)
2. DOM manipulation
3. Screenshots and export
4. Puppeteer/Playwright interface compatibility

Obscura does exactly these four things, faster and lighter.

---

## Key Features

**Zero-dependency install**: One binary, no Node, no npm, no Chrome.

**CLI**: `fetch`, `dump`, `screenshot`, `eval`, `scrape` (parallel with `obscura-worker`).

**Puppeteer/Playwright drop-in**: Start as CDP server on port 9222; change the WebSocket URL in your code and nothing else needs to change.

**MCP integration**: Native MCP support for AI agents. The companion [obscura-plugin](https://github.com/epicsagas/obscura-plugin) provides an MCP server wrapper with web scraping, JavaScript rendering, and browser automation tools.

**Docker**: `h4ckf0r0day/obscura` image, distroless-based, ~57 MB compressed, runs as non-root.

**Stealth builds**: BoringSSL-based transport for anti-detection. Four variants — with/without rendering, with/without stealth.

---

## The Best Endorsement: Cloudflare Kitesurf

From the README:

> Cloudflare began by porting Obscura to Workers while developing its new agent-first browser — Kitesurf.

Cloudflare's engineering team used Obscura as the starting point for Kitesurf, their agent-first browser service. Not "inspired by" — they ported it to Workers.

---

## Best-Fit Scenarios

**Great fit**: batch web scraping, AI agent browser tools (MCP), screenshot services, local MCP tools, CI/CD browser testing

**Not ideal**: scenarios requiring full CSS rendering spec compliance, WebGL/Canvas-heavy pages, Chrome Extension support

---

## Links

- GitHub: [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura)
- Docs: [docs.obscura.sh](https://docs.obscura.sh/)
- MCP plugin: [epicsagas/obscura-plugin](https://github.com/epicsagas/obscura-plugin)
- Cloudflare Kitesurf blog: [blog.cloudflare.com/kitesurf/](https://blog.cloudflare.com/kitesurf/)
