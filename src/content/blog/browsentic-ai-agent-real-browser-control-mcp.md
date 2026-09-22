---
title: "browsentic：让 AI Agent 直接操控你已登录的真实浏览器——无 headless、免 API Key"
titleEn: "browsentic: Let AI Agents Control Your Real Logged-In Browser — No Headless, No API Key"
description: "imshaikot/browsentic，21 stars，MIT，TypeScript。浏览器扩展 + 本地 Daemon + MCP Server 三件套，把 Claude Code、Codex、Antigravity 等 Agent CLI 接入你正在用的真实浏览器，带着你的登录态、Cookie、历史记录操控任意站点。52 个页面工具，Pairing Code 双端验证，全程 127.0.0.1 不出本机，无需 API Key。"
descriptionEn: "imshaikot/browsentic — 21 stars, MIT, TypeScript. Browser extension + local daemon + MCP server. Connects Claude Code, Codex, Antigravity and other Agent CLIs to your real logged-in browser — with your existing login sessions, cookies, and history. 52 page tools, Pairing Code mutual verification, all traffic stays on 127.0.0.1, no API key required."
pubDate: 2026-09-22
heroImage: "../../assets/images/browsentic-ai-agent-real-browser-control-mcp-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "browser-automation", "mcp", "ai-agent", "claude-code", "local-ai", "typescript", "mit"]
lang: zh-CN
---

`imshaikot/browsentic`，21 stars，MIT，TypeScript。2026-07-24 首次提交，2026-09-22 仍在活跃更新。

一句话：让 AI Agent 操控你**正在用的、已经登录的**真实浏览器，不需要无头浏览器，不需要 API Key，不需要云端中转。

**GitHub**：github.com/imshaikot/browsentic | **Stars**：21 | **License**：MIT | **语言**：TypeScript

---

## 传统浏览器自动化的痛点

Playwright、Puppeteer 之类的工具启动的是**无头浏览器**——一个全新的浏览器实例，没有你的 Cookie、没有登录态、没有扩展、没有历史记录。

这意味着：每次自动化都要重新登录，面对 OAuth/SSO/MFA，或者遇到检测 headless 的站点（如 Google、LinkedIn、Twitter）就直接失败。

Browsentic 换了个思路：不启动新浏览器，直接接管你桌面上开着的那个。

---

## 架构：三层 + Pairing Code

```
浏览器扩展（Side Panel UI）
        ↕ WebSocket（仅 127.0.0.1）
本地 Daemon（browsentic 进程）
        ↕ spawn 子进程 / MCP 协议
Agent CLI（claude / codex / agy）
```

**浏览器扩展**：在侧边栏注入一个 AI 输入界面，接收用户指令，与 Daemon 通信。

**本地 Daemon**：在 `127.0.0.1` 监听 WebSocket，同时作为 MCP Server，支持多个 MCP 客户端共享同一个浏览器实例。

**Pairing Code**：双端握手，扩展与 Daemon 互相验证后才建立连接，未 Pair 的连接请求直接拒绝。

流量全程在 `127.0.0.1`，不经过任何云端服务器。

---

## 安装

**macOS 一键安装（推荐）：**

```bash
curl -fsSL https://browsentic.com/install.sh | sh
```

**通用方式（需 Node.js 20+）：**

```bash
npx browsentic setup
```

**全局安装后接入 Claude Code MCP：**

```bash
npm i -g browsentic
claude mcp add browsentic -- browsentic mcp
```

### 配置流程

1. `browsentic setup` — 安装扩展 + 启动 Daemon
2. 浏览器安装扩展后打开侧边栏
3. `browsentic pair` — 生成 Pairing Code
4. 在侧边栏输入 Pairing Code 完成配对
5. `browsentic agent` — 选择要使用的 Agent CLI

### 常用命令

| 命令 | 用途 |
|------|------|
| `browsentic setup` | 安装扩展 + 启动 daemon |
| `browsentic pair` | 生成新 pairing code |
| `browsentic status` | 检查 daemon/扩展状态 |
| `browsentic sessions` | 列出已配对浏览器 |
| `browsentic agent` | 切换 Agent CLI |
| `browsentic update` | 刷新扩展构建 |

---

## 支持的浏览器与 Agent

**浏览器：** Chrome、Edge、Arc、Brave、Firefox（实验性）

**Agent CLI：**

| Agent | 状态 |
|-------|------|
| Claude Code | 稳定 |
| Codex / OpenAI | 稳定 |
| Antigravity | 稳定 |
| Mistral Vibe | Beta |
| Grok Build | Beta |

每个 Agent 只需要预先在本机安装并完成认证，Browsentic 通过 spawn 子进程调用它们，Agent 本身的 API Key 由各自管理，Browsentic 本身不需要 Key。

---

## 52 个页面工具

涵盖浏览器操控所需的全部基础能力：

**交互类：** 点击、输入、拖拽、下拉选择、表单提交、悬浮、焦点、键盘事件

**导航类：** 打开 URL、前进/后退、刷新、新建/关闭标签页、切换标签

**内容类：** 截图、获取页面 HTML/文本、元素定位（A-Eye 语义定位）、读取表格

**文件类：** 文件上传、文件下载、拖拽文件

**诊断类：** 控制台日志、网络请求监听、性能计时

**自动化类：** 定时任务、循环执行、iframe 内操作、弹窗处理

**自定义工具（Custom Tools）**：把可复用的脚本保存为命名工具，格式 `site:context:tool-name`，例如 `youtube.com:watch:darken-page`。

---

## 作为 MCP Server 接入工具链

Browsentic Daemon 同时暴露 MCP 协议，可以被 Claude Code、Cursor、Zed 等工具直接调用，无需通过侧边栏 UI：

```bash
# 接入 Claude Code
claude mcp add browsentic -- browsentic mcp

# Claude Code 内直接调用浏览器工具
# Agent 可以访问当前已登录的所有页面
```

多个 MCP 客户端可以共享同一个 Daemon 实例，也就是说同一个浏览器窗口可以同时被多个 Agent 工具链访问。

---

## 安全设计

| 安全措施 | 实现 |
|---------|------|
| 本地隔离 | 全程 127.0.0.1，不出本机，无云端中转 |
| Pairing Code | 双端互相验证后才建立连接 |
| 高危操作确认 | Guardrails 系统：声明式策略拦截危险操作，需人工审批 |
| 凭据遮蔽 | 页面密码字段在 Agent 看到之前自动遮掩 |
| 无 API Key | Browsentic 本身不需要任何 API Key |

Guardrails 是声明式策略系统——你可以写规则定义哪些操作需要人工确认（如支付页面的提交按钮、设置页面的删除操作），Agent 执行到这些操作时会暂停等待确认。

---

## 附加功能

**Site Learning**：Agent 自动探索一个站点，创建可复用的站点备忘（site notes），后续任务可以引用这份备忘，减少重复探索开销。

**Voice / Text / 演示模式**：三种指令输入方式。演示模式可以让 Agent 边执行边解释每一步。

**WebMCP 集成**：支持网站主动声明自己的工具集（类似 manifest），Agent 访问时自动发现可用工具，不需要用通用的 DOM 操作硬探。

---

## 实际使用场景

**场景一：抓取需要登录的数据**

```
"帮我把 GitHub notifications 里所有未读 PR 的标题和链接整理成 CSV"
```

Browsentic 在你已登录的 GitHub 页面里直接执行，无需重新认证。

**场景二：批量操作**

```
"把这个 Notion 数据库里所有标签为 '草稿' 的条目状态改为 '待审核'"
```

Agent 在你的 Notion 工作区直接操作，读写你有权限的所有内容。

**场景三：Claude Code 调试 Web 应用**

接入 MCP 后，Claude Code 可以在调试时直接操控浏览器，截图、检查控制台错误、提交表单验证，无需来回粘贴截图。

---

## 局限性

**1. 星数极少（21）**：非常早期的项目，API 可能变动，稳定性未经大规模验证。

**2. 依赖本机已安装的 Agent CLI**：需要预先配置好 Claude Code、Codex 等，Browsentic 只是接管浏览器，不提供 LLM 能力本身。

**3. Firefox 支持实验性**：稳定性不如 Chromium 系浏览器。

**4. Vibe、Grok 接入仍为 Beta**：这两个 Agent 的集成可能有兼容性问题。

**5. 多用户/团队场景未设计**：目前是单用户、本地运行的架构，没有团队共享或远程访问设计。

---

## 与同类工具对比

| 工具 | 浏览器 | 登录态 | 需要 API Key | 云端 | MCP 支持 |
|------|--------|--------|------------|------|---------|
| **Browsentic** | 真实 | ✅ 已有 | ❌ 不需要 | ❌ 纯本地 | ✅ |
| Playwright | Headless | ❌ 每次登录 | 取决于 LLM | 可配置 | 部分 |
| Puppeteer | Headless | ❌ 每次登录 | 取决于 LLM | 可配置 | ❌ |
| Browser Use | Headless/真实 | 可配置 | ✅ 需要 | 默认云端 | ❌ |

Browsentic 的核心差异：**登录态持久化 + 纯本地 + MCP 原生**。代价是需要在本机运行 Daemon 且依赖本机已配置的 Agent CLI。

---

## 怎么看这个项目

对于已经在用 Claude Code 或 Codex 做开发的人来说，Browsentic 填补了一个实际的空白：调试时让 Agent 直接操作浏览器，而不是靠截图粘贴来回。接入 MCP 后 Claude Code 可以"看到"并操作浏览器，比单纯的 computer-use 方案更精准（因为是 DOM 级操作而非像素级）。

21 stars 的早期阶段意味着这套方案还没有被大规模检验，但架构思路（真实浏览器 + Pairing Code 安全 + MCP Server）是清晰的，安装体验（一行 curl）也足够低门槛。

> MIT 协议，开源仅供学习研究参考。Browsentic 可操作你浏览器里的所有页面，使用前评估安全边界。

---

<!--EN-->

## browsentic: Connect AI Agents to Your Real Logged-In Browser — No Headless, No API Key

`imshaikot/browsentic` (21 stars, MIT, TypeScript) is a browser extension + local daemon + MCP server that connects AI agent CLIs (Claude Code, Codex, Antigravity) to your actual running browser — with your existing login sessions, cookies, and history intact.

**GitHub**: github.com/imshaikot/browsentic | **Stars**: 21 | **License**: MIT

---

### The Problem It Solves

Headless automation (Playwright, Puppeteer) spins up a fresh browser instance with no cookies, no login state, no history — forcing re-authentication every run and failing on headless-detection sites. browsentic bypasses this entirely by attaching to the browser you already have open.

---

### Architecture

```
Browser Extension (Side Panel UI)
        ↕ WebSocket (127.0.0.1 only)
Local Daemon (browsentic process)
        ↕ spawn subprocess / MCP protocol
Agent CLI (claude / codex / agy)
```

Three layers: an extension side panel for user input, a local daemon that handles WebSocket and MCP, and the agent CLI you already have installed. Everything stays on `127.0.0.1`. Pairing Code mutual verification before any connection is established.

---

### Installation

```bash
# macOS one-liner
curl -fsSL https://browsentic.com/install.sh | sh

# Universal (Node.js 20+)
npx browsentic setup

# Global install + Claude Code MCP
npm i -g browsentic
claude mcp add browsentic -- browsentic mcp
```

Setup: `browsentic setup` → install extension → `browsentic pair` → enter Pairing Code in side panel → `browsentic agent` to select CLI.

---

### 52 Page Tools

Click, type, drag, form submit, navigate, screenshot, file upload/download, iframe interaction, console/network diagnostics, timed/looped tasks, semantic element locator (A-Eye), custom named tools (e.g. `youtube.com:watch:darken-page`), Guardrails confirmation policies.

---

### MCP Server

Multiple MCP clients can share one daemon — meaning Claude Code, Cursor, Zed can all control the same browser instance simultaneously:

```bash
claude mcp add browsentic -- browsentic mcp
```

---

### Security

- All traffic bound to `127.0.0.1`
- Pairing Code mutual verification before connection
- Guardrails: declarative policies requiring human approval for high-risk actions
- Password fields auto-masked before agent sees them
- No API key stored in browsentic itself

---

### Supported Browsers & Agents

Browsers: Chrome, Edge, Arc, Brave, Firefox (experimental).
Agents: Claude Code (stable), Codex (stable), Antigravity (stable), Mistral Vibe (beta), Grok Build (beta).

---

### Limitations

1. **21 stars, very early**: API may change, not battle-tested at scale
2. **Requires pre-configured Agent CLI**: browsentic doesn't provide LLM capability itself
3. **Firefox is experimental**: less stable than Chromium-based browsers
4. **No multi-user/remote access**: single-user local architecture only
5. **Vibe/Grok integrations in beta**: potential compatibility issues

---

### vs. Alternatives

browsentic's key differentiators: persistent login state, fully local (no cloud), MCP-native. Trade-off: requires local daemon + pre-installed agent CLIs.

| Tool | Browser | Login State | Cloud | MCP |
|------|---------|-------------|-------|-----|
| **browsentic** | Real | ✅ Preserved | ❌ Local | ✅ |
| Playwright | Headless | ❌ Fresh | Configurable | Partial |
| Browser Use | Headless/Real | Configurable | Default cloud | ❌ |

> MIT license. browsentic can operate all pages in your browser — evaluate your security boundary before deploying. For learning and research reference only.
