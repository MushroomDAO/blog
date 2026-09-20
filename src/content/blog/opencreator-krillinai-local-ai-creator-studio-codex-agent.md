---
title: "OpenCreator：KrillinAI 进化为本地 AI 创作工作台，内置 Codex Agent + 10 个可视化工具"
titleEn: "OpenCreator: KrillinAI Evolves into a Local AI Creator Studio with Codex Agent and 10 Visual Tools"
description: "krillinai/OpenCreator，11.9K stars，Apache 2.0。前身是 AI 视频翻译工具 KrillinAI，现已扩展为本地 AI 创作工作台。React 18 + Electron + Fastify，以 Codex CLI 为 Agent 引擎，支持视频翻译配音、封面图生成、小红书笔记、短视频脚本、火柴人动画等 10 个内置工具，外加 Agent 对话模式与视觉工作台双向状态同步。主要成本门槛：Codex CLI token 消耗约 100k–200k/次任务。"
descriptionEn: "krillinai/OpenCreator — 11.9K stars, Apache 2.0. Evolved from KrillinAI (AI video translation tool) into a local AI creator studio. React 18 + Electron + Fastify, using Codex CLI as the Agent engine. Includes 10 built-in visual tools (video translation, thumbnail generation, XHS posts, short video scripts, stick figure animation, and more) plus a dual-interface architecture where Agent chat and visual tools share the same state machine. Main cost barrier: Codex CLI token consumption ~100k–200k per agent task."
pubDate: 2026-09-21
heroImage: "../../assets/images/opencreator-krillinai-local-ai-creator-studio-codex-agent-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "ai-agent", "content-creation", "codex", "electron", "video", "local-ai"]
lang: zh-CN
---

2026 年 9 月，`krillinai/OpenCreator` 在 GitHub 上达到 11,900+ stars，这个数字背后有一段清晰的演进轨迹：它的前身 KrillinAI 是一款专注视频翻译配音的单一工具，支持 100+ 语言，适配 YouTube/TikTok/B 站。现在，KrillinAI 保留为其中一个工具模块，外面包了一层更大的 AI 创作工作台——OpenCreator。

**GitHub**：github.com/krillinai/OpenCreator | **License**：Apache 2.0 | **Stars**：11,900+

---

## 这是什么：本地 AI 创作工作台

OpenCreator 的定位是"个人/小团队在本地运行的 AI 内容生产平台"，用一句话描述它的架构思路：

**可视化工具 + Agent 对话 → 共享同一个状态机**

这意味着你既可以打开某个工具模板直接操作（像传统软件），也可以切换到对话界面用自然语言指挥 AI 完成同样的事——两侧操作结果实时同步，不是两套独立系统。

---

## 10 个内置工具

当前版本（截至调研时）内置 10 个可视化工具：

| 工具 | 说明 |
|------|------|
| Video Translation | 视频翻译 + 字幕对齐（KrillinAI 核心） |
| Smart Dubbing | 多语言智能配音 |
| Video Downloader | 视频下载（集成 yt-dlp） |
| Video Generation | AI 视频生成（Seedance 2.5、Kling v2.1 等） |
| Thumbnail Generator | 封面图生成 |
| Image Generation | 图片生成（GPT Image、Seedream 4.0 等） |
| Article Writer | 文章写作 |
| Xiaohongshu Posts | 小红书笔记生成 |
| Short Video Script | 短视频脚本 |
| Stick Figure Animation | 火柴人动画（特色功能） |

还有两个功能在开发中：**Auto Clips**（自动剪辑）和 **Digital Avatar**（数字人），尚未发布。

---

## AI 模型矩阵

OpenCreator 对主流模型做了较全面的接入，分工明确：

**语言模型**：GPT 系列、DeepSeek、Qwen（通义千问）、Kimi、GLM（智谱）、Grok、Doubao（豆包）、ERNIE（文心一言）、Hunyuan（混元）、MiniMax

**图像生成**：GPT Image、Seedream 4.0、Kling v2.1、Gemini 2.5 Flash

**视频生成**：Seedance 2.5、Kling v2.1 Master、Veo 3.1

**语音/转写**：Whisper、OpenAI TTS、MiniMax TTS、Edge TTS、阿里云语音

---

## 技术架构

```
                ┌──────────────────────────────────────┐
                │         OpenCreator Desktop          │
                │    React 18 + Vite + Electron        │
                │  ┌──────────────┐ ┌──────────────┐  │
                │  │  可视化工作台 │ │   Agent 对话  │  │
                │  └──────┬───────┘ └──────┬───────┘  │
                │         └────────┬────────┘           │
                │            共享状态机                  │
                └───────────────┬──────────────────────┘
                                │ IPC
                ┌───────────────▼──────────────────────┐
                │     本地守护进程 (Fastify + Node 22)   │
                │     只监听 127.0.0.1，Bearer Token     │
                │   SQLite | FFmpeg | yt-dlp | Whisper  │
                └───────────────┬──────────────────────┘
                                │
                ┌───────────────▼──────────────────────┐
                │         Codex CLI (Agent 引擎)        │
                │    自然语言 → 工具调用 → 工作台操作    │
                └──────────────────────────────────────┘
```

几个值得注意的工程决策：

**1. 守护进程安全边界**：本地 daemon 只绑定 `127.0.0.1`，health check 端点公开，其余 API 全部要求 Bearer Token。不会意外暴露服务到局域网。

**2. 内置组件版本管理**：FFmpeg、yt-dlp 等工具有自动安装和失败回退机制，安装失败自动降到上一个可用版本，不会因为环境问题直接报错。

**3. 创作版本控制**：每次生成结果独立保存，不覆盖历史。可以回溯任意一次迭代。

**4. Desktop/Web 同构**：Electron 客户端和 Web 版共用同一套 React 代码库，OS 相关能力通过隔离层处理。

---

## 安装

```bash
# 前提条件
# - Node.js 22+（版本强要求）
# - pnpm 9.15.0（版本锁定，不匹配会报错）
# - Codex CLI（需要单独安装和登录）

git clone https://github.com/krillinai/OpenCreator
cd OpenCreator

corepack enable
pnpm install

# 浏览器版（访问 localhost）
pnpm web:dev

# 桌面版（Electron）
pnpm desktop:dev
```

注意 pnpm 版本锁定较严格，推荐用 `corepack enable` 自动管理，手动安装其他版本的 pnpm 可能触发版本不匹配错误。

---

## Agent 模式：Codex CLI 集成

这是 OpenCreator 区别于其他创作工具的核心设计。Codex CLI 不只是一个聊天接口，而是工作台的 Agent 引擎：

- 收到自然语言指令 → 分析任务 → 调用工作台工具 → 状态同步回可视化界面
- 支持 MCP 协议（可接入外部工具）
- 支持可复用 Skill 定义
- 后台任务调度：长任务异步执行，不阻塞界面
- 项目维度的对话历史管理

**实际成本提示**：Codex CLI 每次 Agent 任务消耗约 100k–200k token，以 OpenAI 标准定价计算，复杂任务可能超过 $1。频繁使用前建议评估 token 预算。

---

## 不足之处

**1. Codex CLI 强依赖**：整个 Agent 模式的基础是 Codex CLI，需要用户自持 OpenAI API Key 和 Codex 配额。如果 Codex 定价变化，OpenCreator 的 Agent 功能成本也会随之变化。

**2. Auto Clips 和 Digital Avatar 尚未发布**：这两个功能在 README 中有展示，但实际代码中标记为"开发中"。

**3. 端到端自动化测试覆盖不完整**：真实 Codex 冒烟测试默认关闭，CI 主要覆盖单元测试和 UI 组件测试。Agent 行为的回归测试依赖手动验证。

**4. 多语言文档质量参差**：支持 10 种语言的文档，但非英文/中文的版本主要是机器翻译，部分内容落后于主分支。

**5. 无独立官网**：品牌分散在 GitHub、Bilibili、QQ 群、Discord，没有统一的产品页面。项目认知门槛略高。

---

## 和 KrillinAI 的关系

项目演进路线：

```
KrillinAI（单一视频翻译工具）
       ↓ 扩展
OpenCreator（综合创作工作台）
       ├── Video Translation（KrillinAI 核心功能保留）
       ├── Smart Dubbing
       ├── 8 个新工具
       └── Codex Agent 模式
```

如果你只需要视频翻译配音，原始 KrillinAI 逻辑仍然完整，不需要跑整个 OpenCreator；如果需要更多创作工具和 Agent 驱动的工作流，OpenCreator 是完整版本。

---

## 怎么看这个项目

OpenCreator 做对了一件事：把"可视化操作"和"Agent 对话"放进同一个状态机，而不是两个独立的入口。这个架构思路本身是正确方向——随着 AI 工具演进，用户会越来越多地在"我要操作"和"我要让 AI 操作"之间切换，一致的底层状态是必要条件。

实际限制在于 Codex CLI 的成本边界。100k–200k token/任务在频繁使用场景下不便宜，适合偶发的复杂创作任务，不适合高频批量处理。如果 OpenCreator 后续支持本地模型作为 Agent 引擎（替换 Codex CLI），会显著扩大适用场景。

中文内容创作者（B 站、小红书、抖音场景）是当前最对口的用户群体——工具选型对这些平台有明确适配，中文 UI 和中文文档质量也好于其他语言版本。

> 代码仅供学习研究，请遵守 Apache 2.0 协议。Codex CLI token 消耗较高，建议在沙箱环境中先测试再正式使用。

---

<!--EN-->

## OpenCreator: KrillinAI Evolves into a Local AI Creator Studio

`krillinai/OpenCreator` has reached 11,900+ GitHub stars in September 2026. Its predecessor KrillinAI was a focused AI video translation and dubbing tool supporting 100+ languages across YouTube/TikTok/Bilibili. KrillinAI is now preserved as one tool module inside a larger platform — OpenCreator, a local AI creator workstation.

**GitHub**: github.com/krillinai/OpenCreator | **License**: Apache 2.0 | **Stars**: 11,900+

---

### What It Is

OpenCreator positions itself as a local AI content production platform for individuals and small teams. The core architectural premise:

**Visual tool interface + Agent chat interface → shared state machine**

Both sides operate on the same state machine. A change made through the visual workspace is immediately reflected in the Agent conversation context, and vice versa. These are not two separate systems with a sync layer — they share the same underlying state.

---

### 10 Built-in Tools

| Tool | Description |
|------|-------------|
| Video Translation | Subtitle alignment + translation (KrillinAI core) |
| Smart Dubbing | Multi-language AI dubbing |
| Video Downloader | yt-dlp integration |
| Video Generation | Seedance 2.5, Kling v2.1 Master, Veo 3.1 |
| Thumbnail Generator | AI cover image creation |
| Image Generation | GPT Image, Seedream 4.0, Kling v2.1 |
| Article Writer | Long-form writing |
| Xiaohongshu Posts | Xiaohongshu (RedNote) post generation |
| Short Video Script | Script writing for short-form video |
| Stick Figure Animation | Animated stickman scenes (unique feature) |

Two tools still in development: **Auto Clips** and **Digital Avatar** — present in the README but not yet released.

---

### Tech Stack

- **Frontend**: React 18 + Vite + TypeScript
- **Desktop client**: Electron
- **Local daemon**: Fastify + Node.js 22+ (binds to `127.0.0.1` only, Bearer Token required for all endpoints except health check)
- **Storage**: SQLite (local, no cloud sync)
- **Package manager**: pnpm 9.15.0 (version pinned)
- **Media toolchain**: FFmpeg, yt-dlp (with version management and automatic fallback)
- **Agent engine**: Codex CLI

---

### Installation

```bash
# Prerequisites: Node.js 22+, pnpm 9.15.0 (via corepack), Codex CLI installed and logged in

git clone https://github.com/krillinai/OpenCreator
cd OpenCreator
corepack enable
pnpm install

pnpm web:dev       # browser version
pnpm desktop:dev   # Electron desktop version
```

Note: pnpm version is strictly pinned. Use `corepack enable` to avoid version mismatch errors.

---

### The Codex CLI Integration

Codex CLI is not just a chat wrapper — it's the actual Agent engine:

- Receives natural language instructions → analyzes the task → calls workspace tools → syncs state back to the visual interface
- MCP protocol support (external tool integration)
- Reusable Skills
- Background task scheduling for long-running operations
- Project-scoped conversation history

**Cost consideration**: Each Codex agent task consumes approximately 100k–200k tokens. Complex tasks can cost $1+ at standard OpenAI pricing. Evaluate token budget before using the Agent mode frequently.

---

### Limitations

1. **Codex CLI hard dependency**: The Agent mode requires an OpenAI API key with Codex access. If Codex pricing changes, OpenCreator's agent capability costs change too.
2. **Auto Clips and Digital Avatar not yet released**: Featured in the README but marked in-development in the code.
3. **Incomplete end-to-end test coverage**: Real Codex smoke tests are disabled by default. Agent behavior regression testing is manual.
4. **Inconsistent multilingual docs**: 10 language options but non-English/Chinese content is primarily machine-translated and lags behind the main branch.
5. **No independent website**: Project presence is scattered across GitHub, Bilibili, QQ groups, and Discord.

---

### Bottom Line

OpenCreator gets one important thing right: putting the visual workspace and the Agent conversation on the same state machine. That's the correct architectural direction — as AI tools mature, users will increasingly switch between "I'll do it" and "AI will do it" mid-task, and consistent underlying state makes that seamless.

The current limitation is Codex CLI's cost floor. At 100k–200k tokens per agent task, it's not viable for high-frequency bulk processing. If OpenCreator eventually supports local model backends as an Agent engine replacement for Codex CLI, it would significantly broaden the use case.

The most natural user base today: Chinese-language content creators targeting Bilibili, Xiaohongshu, and Douyin — the tool selection is specifically adapted for those platforms, and the Chinese UI and documentation quality is the best of any language version.

> Code for learning and research use only. Apache 2.0. Codex CLI token consumption can be high — test in a sandbox environment before production use.
