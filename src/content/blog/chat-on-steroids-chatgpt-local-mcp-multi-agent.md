---
title: "Chat on Steroids：给 ChatGPT 装上本地 MCP + 多 Worker，在浏览器里跑 Codex 风格工作流"
titleEn: "Chat on Steroids: Local MCP + Multi-Worker for ChatGPT, Codex-Style Workflows in Your Browser"
description: "Chat on Steroids（totec448-spec/chat-on-steroids），MIT，3900+ stars，TypeScript Electron 桌面应用。给 ChatGPT 接上本地 MCP 服务器，让它直接读写文件、跑终端命令、控制桌面，同时支持多 Worker 并行分任务、Goal/Loop 自动继续、Compact & Resume 跨对话续命。核心原理是 Chrome 扩展自动化 ChatGPT UI + 本地 MCP，不调用 Codex，吃的是你的 ChatGPT 额度。附安装步骤与合规风险说明。"
descriptionEn: "Chat on Steroids (totec448-spec/chat-on-steroids), MIT, 3900+ stars, TypeScript Electron desktop app. Connects ChatGPT to a local MCP server for file read/write, terminal commands, and desktop control. Supports multi-worker parallel delegation, Goal/Loop auto-continuation, and Compact & Resume cross-session persistence. Works by automating the ChatGPT browser UI + local MCP — uses your ChatGPT quota, not a separate Codex API. Includes setup steps and compliance risk notes."
pubDate: 2026-09-24
heroImage: "../../assets/images/chat-on-steroids-chatgpt-local-mcp-multi-agent-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "chatgpt", "mcp", "multi-agent", "electron", "local-ai", "workflow", "chrome-extension"]
lang: zh-CN
---

`totec448-spec/chat-on-steroids`，3986 stars，MIT，TypeScript + Electron。一个让 ChatGPT 在浏览器里像 Codex 一样干活的本地工作站——文件读写、终端命令、桌面控制、多 Worker 并行，都通过本地 MCP 服务器桥接，不调用单独的 Codex API，吃的是你的 ChatGPT 使用额度。

**GitHub**：github.com/totec448-spec/chat-on-steroids

---

## 工作原理

CoS 的架构分三层：

**1. 本地 MCP 服务器（Core）**  
Electron 进程在本地跑一个 MCP 服务器，暴露你批准的文件夹和系统能力（文件读写、终端、剪贴板、桌面截图/控制）。你通过 Settings → Workspace 圈定可访问路径，圈外的目录 ChatGPT 不能触碰。

**2. Chrome 扩展（Companion）**  
扩展加载后自动与本地应用配对，负责：对话内容本地记录、工具调用行结果渲染、Compact & Resume 标记插入、多 Worker 在侧边栏的状态显示。它把 MCP 的工具结果注入到 ChatGPT 的 UI 里，看起来和原生工具调用一样。

**3. ChatGPT Developer Mode + MCP App**  
需要你的 ChatGPT 账号开启 Developer Mode 并添加 CoS 作为自定义 MCP 应用。ChatGPT 通过标准 MCP 协议调用本地工具——本质上是 ChatGPT 官方的 MCP 集成能力，不是浏览器注入或非官方 hack。

---

## 核心功能

### Goal / Loop：长任务自动继续

- **Goal**：你写一个目标，ChatGPT 开始工作，遇到上下文切换或 Stop 后自动续命，跟踪未完成工作继续推进
- **Loop**：在你设定的范围内持续工作，你可以在运行中发送修正，不打断整体进展
- 两者都不绕过 OpenAI 速率限制，遇到限速会暂停等待

### Compact & Resume：跨对话接力

长对话快到 context 上限时，CoS 把当前对话历史 + 所有 Worker 的状态打包压缩，然后在新对话里恢复，继续工作。Worker 的上下文独立保存，重用时可以直接 pick up。

### Workers：多 Agent 并行分任务

把一个大任务分给多个 Worker，每个 Worker 独立对话，各自保留 context，汇总结果回到主对话。

```
主对话：写一个 CLI 工具
├─ Worker 1：负责核心逻辑模块
├─ Worker 2：负责测试用例
└─ Worker 3：负责文档
```

主对话拿到三个 Worker 的产出后再做整合。Worker 完成后可以复用，下次任务直接沿用之前的 context。

### 工具能力（需在 Settings 中显式启用）

| 工具类型 | 能力 |
|---------|-----|
| **文件系统** | 读写批准目录内的文件、目录列表 |
| **终端** | 运行 shell 命令，保持持久 session |
| **桌面（可选）** | 截图、鼠标键盘控制 |
| **浏览器（Companion）** | 页面快照、基本 DOM 交互 |

默认只开启 Core 能力和两个 Worker；Windows 版默认额外开启桌面权限。

---

## 安装步骤

**环境要求：**
- Windows 10/11 / macOS 13 Ventura+ / 当前 Linux 桌面发行版
- Chrome 116+ 或 Edge（不支持 Firefox/Safari）
- ChatGPT 账号，需要 Developer Mode + 自定义 MCP App 权限

**步骤：**

```bash
# 1. 下载安装包（选你的平台）
# macOS Apple Silicon：Chat-On-Steroids-macOS-arm64.dmg
# Windows x64：Chat-On-Steroids-Setup-x64.exe
# Linux x64：Chat-On-Steroids-Linux-x64.deb
# 从 GitHub Releases 下载

# 2. 安装后打开应用，进入 Settings → Workspace
#    添加你想让 ChatGPT 能访问的项目目录

# 3. Settings → Setup → 生成 MCP 连接配置
#    在 ChatGPT Developer Mode 里添加为自定义 MCP App
#    （需要 Tunnel 穿透，Setup 页面有引导）

# 4. 加载 Chrome 扩展
#    点击 "Open extension folder" → Chrome 扩展管理页 → 加载已解压扩展
```

**注意：**
- 安装包未经 Publisher 签名（Windows）/ 未经 Notarize（macOS），安装时需要手动信任
- 每次更新 App 后需要重新加载 Chrome 扩展
- Linux 需要 Secret Service keyring；如果禁用了 unprivileged user namespaces，AppImage 可能需要 `--no-sandbox`

---

## 硬件要求

本地几乎没有 GPU 要求——所有 AI 推理都在 OpenAI 云端，CoS 只是本地执行器和 MCP 桥。

| 组件 | 要求 |
|-----|------|
| **CPU** | 任何现代 x64 / Apple Silicon |
| **内存** | 建议 8GB+，多 Worker 场景 16GB+ |
| **存储** | 安装包 <200MB |
| **GPU** | 不需要 |
| **网络** | 需要 ChatGPT 访问 + Tunnel 穿透（Setup 页面引导） |

---

## 合规风险：必须提前知道

这是这个项目最重要的部分，README 自己写了，CHANGELOG 也有真实案例。

**CoS 作者本人的账号于 2026 年 9 月收到了 OpenAI 的账号警告邮件**，CHANGELOG v2.1.13 里贴出了邮件截图，v2.1.14 的版本标题变成了情绪化的"Death to Anthropic and OpenAI"。

OpenAI 的关切点在于：
- Chrome 扩展对 ChatGPT UI 的自动化操作（尽管 MCP 本身是官方支持的）
- 用 Compact & Resume 绕过对话长度后的系统行为
- 自动化抓取/记录对话内容

CoS 自己的责任声明很清楚：**不保证策略合规，不保证账号安全**。"If a workflow is restricted or receives a policy warning, stop that workflow."

**使用前评估的问题：**
1. 你的 ChatGPT 账号是个人还是企业？企业账号违规代价更高
2. 你用的是 ChatGPT Plus 还是 Team/Enterprise？后者有额外约束
3. 你的工作流是否涉及自动化抓取或大批量请求？

---

## 和 Claude Code / Codex CLI 的定位差异

| 工具 | 接入方式 | 额度来源 | 浏览器依赖 |
|------|---------|---------|-----------|
| **Claude Code** | 直接 API | Anthropic API | 不需要 |
| **Codex CLI** | 直接 API | OpenAI API | 不需要 |
| **Chat on Steroids** | ChatGPT UI + MCP | ChatGPT 订阅额度 | 必须 Chrome |

CoS 的定位很明确：**用你已有的 ChatGPT 订阅（Plus/Pro/Team）来跑本地 Agent 工作流，不额外付 API 费用**。代价是需要维护一个 Chrome 会话，在稳定性和控制粒度上天然比 API 调用方案更脆。

---

## 怎么看这个项目

3986 stars 在一个月内（创建于 2026-08-22）积累，说明需求是真实存在的——很多用户有 ChatGPT 订阅但没有 API 预算，或者习惯了 ChatGPT 的界面，想要本地文件操作能力。

CoS 在技术上把 MCP 标准用到了一个有意思的地方：让 ChatGPT 的官方 MCP 支持成为本地工具桥的后门。这个架构是干净的，不是在注入或破解 UI。

麻烦在于 Chrome 扩展那层——自动化 ChatGPT 对话行为在 OpenAI ToS 里是灰区，作者已经亲身验证了这会触发账号警告。如果你重度依赖 ChatGPT 账号，在用 CoS 跑自动化工作流之前需要认真评估风险。

> 开源仅供学习研究参考。使用前请仔细阅读 OpenAI 服务条款，CoS 不保证账号安全。

---

<!--EN-->

## Chat on Steroids: Local MCP + Multi-Worker for ChatGPT

`totec448-spec/chat-on-steroids` — MIT, 3986 stars, TypeScript + Electron. A local workstation that gives ChatGPT Codex-style capabilities: file read/write, terminal commands, desktop control, and multi-worker parallel execution — all bridged through a local MCP server. Uses your ChatGPT subscription quota, not a separate Codex API.

**GitHub**: github.com/totec448-spec/chat-on-steroids

---

### Architecture

**Local MCP Server (Core)**: Electron process runs a local MCP server exposing approved folders and system capabilities (files, terminal, clipboard, desktop). Paths outside your approved workspace are inaccessible.

**Chrome Companion Extension**: Auto-pairs with the local app. Handles local conversation recording, tool result rendering, Compact & Resume markers, and Worker status display in the sidebar.

**ChatGPT Developer Mode + MCP App**: Requires a ChatGPT account with Developer Mode and the CoS app added as a custom MCP App. ChatGPT calls local tools over the standard MCP protocol — it's the official ChatGPT MCP integration, not a browser injection.

---

### Core Features

**Goal / Loop**: Long-task continuation — Goal tracks unfinished work across context resets; Loop keeps working within your stated brief while accepting in-flight corrections.

**Compact & Resume**: Near context-limit, CoS compresses conversation history + all Worker states into a fresh chat and resumes. Workers save context independently and can be reused across sessions.

**Workers**: Split a task across multiple independent ChatGPT conversations, each with its own context. The primary conversation collects their outputs and integrates.

**Tool Capabilities** (explicitly enabled in Settings):

| Tool | Capabilities |
|------|-------------|
| Filesystem | Read/write approved directories |
| Terminal | Shell commands, persistent sessions |
| Desktop (opt-in) | Screenshots, mouse/keyboard control |
| Browser (Companion) | Page snapshots, basic DOM interaction |

---

### Setup

Requirements: Windows 10/11 / macOS 13+ / current Linux desktop; Chrome 116+ or Edge; ChatGPT account with Developer Mode + custom MCP App access.

```
1. Download installer from GitHub Releases (macOS arm64 DMG / Windows x64 EXE / Linux x64 DEB)
2. Settings → Workspace → add approved project directories
3. Settings → Setup → generate MCP config → add to ChatGPT Developer Mode
4. Load the Chrome extension via "Open extension folder" → Load unpacked
```

Note: unsigned on Windows (no publisher cert) and unnotarized on macOS — manual trust required.

---

### Hardware Requirements

No GPU needed — all AI inference runs in OpenAI's cloud. CoS is a local executor only.

| Component | Requirement |
|-----------|------------|
| CPU | Any modern x64 / Apple Silicon |
| RAM | 8GB+; 16GB+ for multi-worker |
| Storage | <200MB |
| GPU | Not required |
| Network | ChatGPT access + tunnel (guided in Setup) |

---

### Compliance Risk

**The author's own ChatGPT account received an OpenAI warning in September 2026** — documented in CHANGELOG v2.1.13 with email screenshots. v2.1.14's title reads "Death to Anthropic and OpenAI" reflecting the fallout.

OpenAI's concern: browser automation of the ChatGPT UI (even with MCP as the official mechanism), automated conversation recording, and behaviors that resemble rate-limit evasion.

CoS's own disclaimer: *does not guarantee policy compliance or account safety*. "If a workflow is restricted or receives a policy warning, stop that workflow."

**Before using**: evaluate your account type (personal vs. enterprise), usage patterns (manual vs. high-frequency automation), and how much you rely on your ChatGPT account.

---

### Vs. Claude Code / Codex CLI

| Tool | Access Method | Quota Source | Browser Required |
|------|--------------|-------------|-----------------|
| Claude Code | Direct API | Anthropic API | No |
| Codex CLI | Direct API | OpenAI API | No |
| Chat on Steroids | ChatGPT UI + MCP | ChatGPT subscription | Chrome required |

CoS's value prop: use your existing ChatGPT subscription (Plus/Pro/Team) for local agent workflows without additional API costs. Trade-off: browser session dependency and the compliance risk that comes with UI automation.

---

### Assessment

3986 stars in ~one month (created 2026-08-22) reflects a real demand: users with ChatGPT subscriptions but no API budget who want local file capabilities. The architecture is technically clean — it leverages ChatGPT's official MCP support rather than injecting or cracking the UI.

The Chrome extension layer is the risk vector. Automating ChatGPT conversation behavior sits in a ToS gray area that the author has personally discovered triggers account warnings. If you're a heavy ChatGPT user, weigh that risk seriously before running automated workflows through CoS.

> For learning and research reference only. Read OpenAI's Terms of Use carefully before use. CoS does not guarantee account safety.
