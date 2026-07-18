---
title: "OpenSquilla：用多模型路由挑战顶级大模型，花 1/9 的钱达到同等效果"
titleEn: "OpenSquilla: Multi-Model Routing That Matches Top LLMs at 1/9th the Cost"
description: "OpenSquilla（5600+ Star，Apache 2.0）是一个 token 高效的微内核 AI Agent，其核心 SquillaRouter 在本地设备上把每轮对话路由到最便宜且能胜任的模型。基准测试显示：多模型路由（$0.69）vs 单独使用 Claude Opus 4.7（$6.23），评分几乎相同，成本降低 9 倍。"
descriptionEn: "OpenSquilla (5600+ stars, Apache 2.0) is a token-efficient microkernel AI agent whose SquillaRouter locally routes each turn to the cheapest capable model. Benchmarks show: multi-model routing ($0.69) vs Claude Opus 4.7 alone ($6.23) — nearly identical scores, 9x cheaper."
pubDate: "2026-07-10"
updatedDate: "2026-07-10"
category: "Tech-Experiment"
tags: ["OpenSquilla", "多模型路由", "SquillaRouter", "AI Agent", "Token效率", "开源", "LLM", "成本优化", "微内核"]
heroImage: "../../assets/images/opensquilla-multi-model-routing-guide-banner.jpg"
---

GitHub：[opensquilla/opensquilla](https://github.com/opensquilla/opensquilla) · ⭐ 5600+ · Apache 2.0

---

## 一个颠覆直觉的基准测试结果

先看数据，再讲原理。

OpenSquilla 团队用 PinchBench 1.2.1 对 25 个任务跑了对比测试：

| Agent | 使用模型 | 平均得分 | 总 Token 输入 | 总成本 |
|-------|---------|---------|-------------|-------|
| **OpenSquilla** | 多模型路由（Opus 4.7 + GLM 5.1 + DeepSeek Flash） | **0.9251** | 1,721,328 | **$0.688** |
| OpenClaw | Claude Opus 4.7 单模型 | 0.9255 | 3,066,243 | $6.233 |

两行数据说明一件事：**评分几乎相同（差距 0.0004），成本相差 9 倍。**

OpenClaw 用最强的单一模型（Claude Opus 4.7）获得了 0.9255 分，花了 $6.23。
OpenSquilla 用多模型路由混合完成同样的 25 个任务，得分 0.9251，只花了 $0.69。

这不是"用更差的模型凑合"，而是**智能分配**：简单的事情不用杀鸡用牛刀。

---

## SquillaRouter：多模型调度的核心

OpenSquilla 的核心差异是一个叫 **SquillaRouter** 的本地路由器。

它做的事情本质上很简单：**把每轮对话分级，然后路由到对应档位最便宜的模型。**

### 分级逻辑（C0–C3 四档）

```
C0 — 简单对话 / 检索型任务     → 最便宜的小模型（DeepSeek Flash / Haiku 等）
C1 — 一般推理 / 代码生成       → 中等模型（GPT-4o Mini / Sonnet 等）
C2 — 复杂推理 / 长文档处理     → 高能力模型（GPT-4o / Sonnet 等）
C3 — 最高难度任务              → 顶级模型（Claude Opus / GPT-4 等）
```

### 分级方法

SquillaRouter 不是基于规则的，而是**本地 LightGBM + ONNX 分类器**，综合以下特征评分：

- 输入长度
- 语言类型（代码/自然语言/多语言）
- 关键词（工具调用信号、技术术语）
- 语义嵌入（on-device 向量，不上传）

**关键设计**：分级判断完全在本机完成，prompt 内容不出本地机器。这解决了很多企业场景的隐私顾虑——判断"这道题难不难"不需要把题目发给云端。

### 自适应策略

路由不只影响模型选择，还影响 prompt 构建：

- C0/C1 轮次：轻量 system prompt，不请求扩展推理
- C2/C3 轮次：完整 system prompt + 必要时请求 extended thinking

这让 token 消耗和成本都跟任务复杂度挂钩，而不是一刀切。

---

## 20+ 模型提供商，统一接口

OpenSquilla 的提供商注册表支持 20+ 个 LLM 后端，全部通过统一的 `config.toml` 配置：

| 类别 | 支持的提供商 |
|------|------------|
| 国际 API | OpenAI、Anthropic、Google Gemini、Mistral、Groq |
| 路由聚合 | OpenRouter、TokenRhythm |
| 中文模型 | DeepSeek、Qwen/DashScope、Moonshot、智谱 GLM、SiliconFlow |
| 本地部署 | Ollama、vLLM、LM Studio |
| 专有平台 | Tencent TokenHub / Token Plan、IQS |

切换提供商不需要改代码，只改配置文件。路由器会自动在同一档位内选最优（主选 + 备选）。

**主备切换示例**：

```toml
[[providers]]
name = "openrouter"
primary = "anthropic/claude-opus-4.7"
fallback = "deepseek/deepseek-r1-flash"
```

---

## 微内核架构：所有入口共享同一个 TurnRunner

OpenSquilla 是典型的微内核设计——一个核心 Gateway，所有交互界面都是上层封装。

```
Web UI (Vue 控制台)
CLI (opensquilla chat / agent)
消息频道 (Slack / Telegram / Discord / 飞书 / 钉钉 / 企微 / QQ / Matrix)
         │
         ▼
    TurnRunner（统一执行层）
         │
    ┌────┴────────────────────────────────┐
    │ SquillaRouter → 模型路由            │
    │ 工具调度（文件/Shell/Git/搜索...）   │
    │ 决策日志 / 重试 / 审批流             │
    │ Session 管理（SQLite 持久化）         │
    └─────────────────────────────────────┘
```

这意味着你在 Web UI 里做的事和在命令行里做的完全等价——工具调用、重试逻辑、权限控制行为一致，没有"UI 功能 CLI 不支持"的割裂感。

---

## 主要功能模块

### 持久化记忆

- `MEMORY.md`：结构化长期记忆文件，Agent 主动维护
- 带日期的 Markdown 笔记：按时间索引的事件记录
- SQLite 全文检索 + `sqlite-vec` 向量语义召回
- 向量嵌入默认 on-device（打包 ONNX 模型），也可切到 OpenAI/Ollama

### 分层安全沙箱

三档权限策略（Standard / Strict / Locked）：
- **Linux**：Bubblewrap 容器隔离代码执行
- **macOS**：Seatbelt（`sandbox-exec`）+ 自动生成 SBPL profile
- **Windows**：原生 Windows 安全后端

连续拒绝操作超过阈值会自动暂停自主运行，rejected 输出自动清除，工具结果 XML 转义防 prompt 注入。

### 15 个内置 Skill

按需加载（用到才激活）：

`coding` · `github` · `cron` · `pptx/docx/xlsx/pdf 生成` · `summarization` · `tmux` · `weather` · `web 搜索` · `图片生成` · `文字转语音` · 更多

### MCP 双向支持

- **MCP Client**：调用外部 MCP Server 工具
- **MCP Server**：`opensquilla mcp-server run` 把自身作为 MCP 工具暴露给其他 Agent

### 子 Agent 和定时任务

- 深度有界的子 Agent 生成（Subagent）
- `SchedulerEngine` 内置 cron 解析器：`opensquilla cron add "0 9 * * 1-5" "每周一到周五早上9点汇总新闻"`

---

## 安装（3 步上手）

### 快速安装（推荐）

```bash
# 1. 安装 uv（包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh
. "$HOME/.local/bin/env"

# 2. 安装 OpenSquilla（含 SquillaRouter）
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.5.0rc3/opensquilla-0.5.0rc3-py3-none-any.whl"

# 3. 初始化配置 + 启动
opensquilla onboard
opensquilla gateway run
```

浏览器打开 `http://127.0.0.1:18791/control/`。

### 桌面应用

- macOS Apple Silicon：`OpenSquilla-0.5.0-rc3-mac-arm64.dmg`
- Windows x64：`OpenSquilla-0.5.0-rc3-win-x64.exe`

均可从 [GitHub Releases](https://github.com/opensquilla/opensquilla/releases) 下载。

### Docker

```bash
OPENSQUILLA_GATEWAY_IMAGE=ghcr.io/opensquilla/opensquilla:latest docker compose up -d
```

---

## 配置多模型路由

安装后通过 `onboard` 向导配置，或直接编辑 `~/.opensquilla/config.toml`：

```bash
# 配置主提供商 + 模型
opensquilla configure provider --provider openrouter --model anthropic/claude-opus-4.7 --api-key-env OPENROUTER_API_KEY

# 开启 SquillaRouter（多模型路由核心）
opensquilla configure router --router recommended

# 验证路由器状态
opensquilla doctor
```

也可以在 Web UI 的 **Control → Provider & Router** 设置。

---

## 从 OpenClaw / Hermes 迁移

OpenSquilla 能无损迁移原有状态（记忆、persona、Skill、MCP/频道配置）：

```bash
# 预览迁移计划（不写入）
opensquilla migrate openclaw --json
opensquilla migrate hermes --json

# 执行迁移
opensquilla migrate openclaw --apply
opensquilla migrate hermes --apply
```

---

## 为什么这件事重要

多模型路由不是新概念，OpenRouter 早就做了。但 OpenSquilla 的创新在于**把路由决策下沉到本地，同时把路由逻辑和 Agent 运行时深度集成**。

几个关键判断：

**1. 顶级模型不是每道题都必要的**

基准测试的 0.9251 vs 0.9255 说明了一件事：25 道任务里，大多数都不需要 Opus 级别的模型来做。一个本地分类器能准确识别出"这道题用 Flash 就够了"，就等于把这道题的成本降了 10 倍以上。

**2. 路由判断必须保护隐私**

把 prompt 发给第三方来判断"这道题难不难"在某些场景是不可接受的。SquillaRouter 的 on-device 分级回避了这个问题。

**3. 数据飞轮**

2026-07-03 发布的技术报告《Agentic Routing: The Harness-Native Data Flywheel》揭示了下一步方向：每次路由决策都是训练数据，正确/错误的路由结果反馈给分类器，让路由随着使用变得越来越准。日常的 Agent 流量变成了优化路由模型的语料。

---

## 一句话总结

OpenSquilla 的核心命题是：**同等预算下，多模型混合路由比单一顶级模型更经济，且效果相当。**

花 Opus 1/9 的钱，用 DeepSeek Flash + GLM + Opus 三层协作，在 25 任务基准上拿到了几乎一样的分数。

如果你在做 Agent 开发或有大量 LLM API 开销，这个思路值得认真研究。

---

- GitHub：[opensquilla/opensquilla](https://github.com/opensquilla/opensquilla) ⭐ 5600+
- 官网：[opensquilla.ai](https://opensquilla.ai)
- 技术报告：Agentic Routing: The Harness-Native Data Flywheel（2026-07-03）

© 2026 Author: Mycelium Protocol

<!--EN-->

## OpenSquilla: Multi-Model Routing That Matches Top LLMs at 1/9th the Cost

GitHub: [opensquilla/opensquilla](https://github.com/opensquilla/opensquilla) · ⭐ 5600+ · Apache 2.0

---

### The Benchmark That Changes the Frame

PinchBench 1.2.1, 25 tasks:

| Agent | Models used | Avg. score | Cost |
|-------|------------|------------|------|
| **OpenSquilla** | Router: Opus 4.7 + GLM 5.1 + DeepSeek Flash | **0.9251** | **$0.688** |
| OpenClaw | Claude Opus 4.7 (single model) | 0.9255 | $6.233 |

Score gap: 0.0004. Cost gap: 9×.

OpenClaw used the best single model and scored 0.9255. OpenSquilla used a multi-model router that routed simple tasks to cheap models and hard tasks to capable ones — scored 0.9251, spent $0.69.

This is not "use worse models and hope for the best." It's intelligent allocation: don't use a sledgehammer where a screwdriver works.

---

### SquillaRouter: The Multi-Model Dispatch Core

SquillaRouter is a local LightGBM + ONNX classifier. It scores each conversational turn and routes it to the cheapest capable model in a four-tier system:

```
C0 — Simple Q&A / retrieval           → cheapest small model (DeepSeek Flash / Haiku)
C1 — General reasoning / codegen       → mid-tier (GPT-4o Mini / Sonnet)
C2 — Complex reasoning / long docs     → high-capability (GPT-4o / Sonnet)
C3 — Maximum difficulty tasks          → top models (Claude Opus / GPT-4)
```

**Features scored**: input length, language type (code/natural language/mixed), keywords (tool-call signals, technical terms), semantic embeddings.

**Critical design**: all classification runs on-device. The prompt content never leaves the local machine to make the routing decision. This addresses enterprise privacy requirements — deciding "is this task hard?" doesn't require sending the task content to the cloud.

Beyond model selection, routing also adapts the system prompt: lightweight instructions for C0/C1 turns, full context + optional extended thinking for C2/C3. Token spend scales with actual task complexity.

---

### 20+ LLM Providers, Unified Interface

The provider registry supports 20+ backends through a single `config.toml`:

- **International**: OpenAI, Anthropic, Gemini, Mistral, Groq
- **Routing aggregators**: OpenRouter, TokenRhythm  
- **Chinese models**: DeepSeek, Qwen/DashScope, Moonshot, Zhipu GLM, SiliconFlow
- **Local deployment**: Ollama, vLLM, LM Studio
- **Specialized**: Tencent TokenHub/Token Plan, IQS

No code changes needed to switch providers — only config. The router automatically handles primary + fallback selection within each tier.

---

### Microkernel Architecture

One Gateway, every interface layered on top:

```
Web UI / CLI / Slack / Telegram / Discord / Feishu / DingTalk / WeCom / QQ / Matrix
                            ↓
                    TurnRunner (unified execution)
                            ↓
        SquillaRouter → tool dispatch → session management
```

Everything — Web UI, CLI, messaging channels — runs through the same `TurnRunner`. Tool calls, retry logic, and permission control behave identically everywhere. There's no "this works in the UI but not the CLI" fragmentation.

---

### Key Capabilities

**Persistent memory**: structured `MEMORY.md` + dated Markdown notes + SQLite full-text + sqlite-vec semantic recall. On-device ONNX embeddings by default; swap to OpenAI/Ollama optionally.

**Layered security sandbox**: three policy tiers (Standard / Strict / Locked). Bubblewrap on Linux, Seatbelt on macOS, native Windows backend. Auto-pause after repeated denials, rejected outputs purged, tool results XML-escaped against prompt injection.

**15 built-in skills** (load on demand): coding, GitHub, cron, pptx/docx/xlsx/pdf, summarization, tmux, weather, web search, image generation, TTS, and more.

**Bidirectional MCP**: acts as an MCP client (calls external MCP tools) AND as an MCP server (`opensquilla mcp-server run` exposes itself to other agents).

**Subagents and scheduling**: depth-bounded subagent spawning, built-in cron scheduler (`opensquilla cron`).

---

### Quick Install

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh && . "$HOME/.local/bin/env"

# Install OpenSquilla with SquillaRouter
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.5.0rc3/opensquilla-0.5.0rc3-py3-none-any.whl"

# Configure and run
opensquilla onboard
opensquilla gateway run
```

Open `http://127.0.0.1:18791/control/` in Chrome.

---

### Why This Matters

Multi-model routing isn't new — OpenRouter has been doing it. What OpenSquilla adds is **local classification + deep integration with the agent runtime**. The routing decision is inseparable from the execution loop, which lets it adapt prompt complexity alongside model tier.

The July 2026 technical report "Agentic Routing: The Harness-Native Data Flywheel" points at what comes next: every routing decision becomes training data. Correct/incorrect routing outcomes feed back into the classifier. Daily agent traffic becomes the corpus that improves the router over time.

The benchmark already showed where this lands: 0.004% score difference, 9× cost reduction. As routing gets more accurate, that gap closes further.

---

- GitHub: [opensquilla/opensquilla](https://github.com/opensquilla/opensquilla)
- Website: [opensquilla.ai](https://opensquilla.ai)
- Technical report: *Agentic Routing: The Harness-Native Data Flywheel* (2026-07-03)

© 2026 Author: Mycelium Protocol
