---
title: "OpenSquilla：同样预算，更高智能密度——开源 AI Agent 的 Token 效率革命"
description: "OpenSquilla 是一个开源微内核 AI Agent 框架，通过本地 ML 路由器 SquillaRouter 将 token 开销降低 60-80%，同时支持 20+ 大模型供应商和四层认知记忆架构。"
titleEn: "OpenSquilla: Same Budget, Higher Intelligence Density — The Open-Source Token Efficiency Revolution"
descriptionEn: "OpenSquilla is an open-source microkernel AI agent framework that cuts token costs by 60-80% via local ML routing, while supporting 20+ LLM providers and a four-tier cognitive memory architecture."
pubDate: 2026-06-07
category: "Tech-News"
tags: ["AI Agent", "Open Source", "Token Efficiency", "LLM Routing", "OpenSquilla", "SquillaRouter"]
lang: "zh-CN"
heroImage: "../../assets/images/opensquilla-token-efficient-ai-agent-banner.png"
---

你有没有想过，现在花在大模型 API 上的钱，有 60-80% 可能是白烧的？

这正是 OpenSquilla 要解决的问题。这个在 2026 年 5 月低调开源的项目，短短一个月内在 GitHub 上斩获 **3440 颗 star、268 个 fork**，正在重新定义"用 AI 做事"的成本边界。

## 它是什么

OpenSquilla 是一个**开源微内核 AI Agent 框架**，核心理念是：

> "Same budget, more capability, better results."  
> 同样的预算，做出更多，效果更好。

它不是又一个套着 LangChain 壳子的工具，而是从架构层重新设计了 AI Agent 的运行方式——让每一个 token 都物尽其用。

项目使用 Apache 2.0 许可证，Python 3.12+ 环境，支持 CLI、Web UI 和多平台聊天频道（Slack、Discord、Teams、Telegram、Matrix 等 10+ 接入方式）。

## 核心技术：SquillaRouter

OpenSquilla 最关键的创新是它的本地模型路由器 **SquillaRouter**。

### 它怎么工作

SquillaRouter 是一个运行在本地的 **LightGBM + ONNX 分类器**，每次对话前先在设备上分析这次请求的特征：

- 提示词长度
- 语言类型
- 是否包含代码
- 关键词信号
- 语义嵌入向量

分析完成后，它把请求分配到四个层级（T0-T3）之一，路由到对应的模型：

| 层级 | 适合场景 | 成本 |
|------|---------|------|
| T0 | 简单问候、摘要 | 最低 |
| T1 | 一般问答、写作 | 低 |
| T2 | 代码生成、分析 | 中 |
| T3 | 复杂推理、多步骤任务 | 最高（顶级模型）|

关键一点：**分类决策完全在本地完成，你的 prompt 不会因为路由决策而离开本机**。这对隐私敏感场景来说意义重大。

### 实测数据

官方公布的基准测试显示：
- 约 **80% 的输入 token** 可以由缓存和低层级模型处理（测试中 222,848 token 来自缓存）
- 整体 token 开销比单一顶级模型部署降低 **60-80%**
- 平均智能评分保持在 **0.9251**，与基准线无统计显著差异

也就是说：花了原来 20-40% 的钱，做出来的效果和全程用最贵模型几乎一样。

## 四层认知记忆架构

OpenSquilla 借鉴了人类认知科学的记忆模型，实现了罕见的**四层持久化记忆**：

```
工作记忆（Working Memory）   → 当前任务上下文
      ↓
情节记忆（Episodic Memory）  → 跨会话的历史经验
      ↓
语义记忆（Semantic Memory）  → 长期积累的事实和知识
      ↓
原始记忆（Raw Memory）       → 审计和模型训练基础数据
```

每层都支持**向量检索 + BM25 关键词**混合搜索，嵌入模型在本地 ONNX 推理，数据不出本机。

还有一个有意思的设计：**Memory Dream Consolidation**——在 Agent 空闲时，系统会自动对记忆进行 24 小时周期性重组和压缩，类似人类睡眠时的记忆巩固过程。

## MetaSkills：让 Agent 自己学技能

OpenSquilla 引入了 **MetaSkills 协议**，这是一种元层级的技能系统，允许：

- Agent 自主发现并调用社区技能
- 通过 "meta-skill-creator" 让 Agent 自己编写新技能
- 内置 10+ MetaSkills，覆盖：研究报告生成、学术论文起草、项目规划等

这本质上是在给 Agent 一个"可编程的技能树"，而不是硬编码能力边界。

## 安全沙箱：不依赖 Docker

安全隔离通过**系统调用级沙箱**实现：
- Linux：Bubblewrap
- macOS：Seatbelt

三级策略控制代码执行权限：标准执行 → 严格审批 → 锁定人工审核。系统还有"拒绝账本"（Denial Ledger），Agent 三次被拒后自动触发人工干预。

## 支持 20+ 大模型供应商

OpenSquilla 的 provider 层已经适配：

OpenRouter · OpenAI · Anthropic · Ollama · DeepSeek · Gemini · Qwen/DashScope · Moonshot · Mistral · Groq · Zhipu · SiliconFlow · vLLM · LM Studio · 等

切换供应商无需修改代码或配置 schema，一条命令搞定：

```bash
opensquilla onboard
opensquilla gateway run
```

## 我的判断：这个项目值得关注吗？

**值得，而且非常值得。**

原因有三：

**1. 解决了真实痛点**  
Token 成本是 AI Agent 规模化落地的最大障碍之一。OpenSquilla 的路由方案不是 PPT 上的理想，是有实测数据支撑的工程实现。

**2. 架构思路领先**  
本地 ML 路由器 + 四层认知记忆 + MetaSkills 自学习，这三个组合在开源世界里目前是罕见的。LangChain 等框架解决了"能做"的问题，OpenSquilla 在解决"做得起"的问题。

**3. 开放生态策略正确**  
Apache 2.0 许可证 + 20+ provider 支持 + 插件五行代码接入，这是一个认真想做生态、而不是圈地的团队姿态。1 个月 3440 star 说明开发者用脚投票了。

**潜在风险：** 项目目前仍在 0.3.x 版本，生产稳定性待验证；60-80% 的节省是理想场景，实际效果取决于你的任务分布。另外，SquillaRouter 的路由质量直接决定体验，如果分错层级会反而降质。

## 快速上手

```bash
# 安装（推荐方式）
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.3.1/opensquilla-0.3.1-py3-none-any.whl"

# 配置并启动
opensquilla onboard
opensquilla gateway run
```

然后打开 `http://127.0.0.1:18791/control/` 进入 Web UI。

---

如果你正在用 AI Agent 跑工作流，或者被 token 账单压着打，OpenSquilla 值得花半天时间认真试试。

**GitHub：** [opensquilla/opensquilla](https://github.com/opensquilla/opensquilla)  
**官网：** opensquilla.ai

<!--EN-->

## OpenSquilla: Same Budget, Higher Intelligence Density — The Open-Source Token Efficiency Revolution

Have you ever considered that 60-80% of what you're spending on LLM APIs might be going to waste?

That's exactly the problem OpenSquilla is solving. This project quietly went open source in May 2026 and has already racked up **3,440 GitHub stars and 268 forks** in just one month, redefining the cost boundaries of AI-powered work.

## What It Is

OpenSquilla is an **open-source microkernel AI agent framework** built around a core philosophy:

> "Same budget, more capability, better results."

This isn't yet another LangChain wrapper. It's a ground-up architectural rethink of how AI agents run — making every token count.

The project is Apache 2.0 licensed, requires Python 3.12+, and supports CLI, Web UI, and 10+ chat channels (Slack, Discord, Teams, Telegram, Matrix, etc.).

## The Core Technology: SquillaRouter

OpenSquilla's most critical innovation is its local model router: **SquillaRouter**.

### How It Works

SquillaRouter is a **LightGBM + ONNX classifier running entirely on-device**. Before each inference call, it analyzes the request locally across five signal dimensions:

- Prompt length
- Language type
- Code presence
- Keyword signals
- Semantic embedding vectors

It then routes the request to one of four tiers (T0–T3):

| Tier | Use Case | Cost |
|------|----------|------|
| T0 | Simple greetings, summaries | Lowest |
| T1 | General Q&A, writing | Low |
| T2 | Code generation, analysis | Medium |
| T3 | Complex reasoning, multi-step | Highest (premium model) |

Critical: **the routing decision happens entirely on-device — your prompt never leaves your machine just to choose a model**. This matters enormously for privacy-sensitive deployments.

### Benchmark Results

Official benchmarks show:
- ~**80% of input tokens** served from cache or low-tier models (222,848 tokens from cache in testing)
- Overall token spend reduced by **60-80%** vs. flat single-model deployments
- Average intelligence score maintained at **0.9251** — statistically equivalent to premium-only baselines

Translation: you spend 20-40% of the original budget and get essentially the same output quality.

## Four-Tier Cognitive Memory

OpenSquilla borrows from cognitive science to implement a rare **four-tier persistent memory stack**:

```
Working Memory   → current task context
      ↓
Episodic Memory  → cross-session historical experience
      ↓
Semantic Memory  → long-term accumulated facts and knowledge
      ↓
Raw Memory       → audit trail and model training base
```

Every tier supports hybrid **vector search + BM25 keyword retrieval**, with embeddings running locally via ONNX — data stays on-device.

There's also a fascinating design: **Memory Dream Consolidation** — during idle periods, the system automatically restructures and compresses memory on a 24-hour cycle, mirroring how human sleep consolidates learning.

## MetaSkills: Agents That Learn New Skills

OpenSquilla introduces the **MetaSkills Protocol** — a meta-layer skill system that allows:

- Agents to autonomously discover and invoke community skills
- A "meta-skill-creator" that lets agents author new skills themselves
- 10+ bundled MetaSkills covering: research-to-report, academic paper drafting, project planning

This gives agents a "programmable skill tree" rather than hardcoded capabilities.

## Security Sandbox: No Docker Required

Security isolation is achieved through **syscall-level sandboxing**:
- Linux: Bubblewrap
- macOS: Seatbelt

Three execution policy tiers govern code permissions: standard execution → strict approval → locked human review. A "Denial Ledger" automatically escalates to human review after three rejections.

## 20+ LLM Providers Supported

OpenSquilla's provider layer already covers:

OpenRouter · OpenAI · Anthropic · Ollama · DeepSeek · Gemini · Qwen/DashScope · Moonshot · Mistral · Groq · Zhipu · SiliconFlow · vLLM · LM Studio · and more

Switching providers requires no code or config schema changes.

## My Assessment: Is This Worth Watching?

**Yes — very much so.**

Three reasons:

**1. Solves a real, expensive problem**  
Token costs are one of the biggest blockers to AI agent deployments at scale. OpenSquilla's routing approach isn't a slide deck concept — it's an engineering implementation backed by measured data.

**2. Architecturally ahead of the field**  
Local ML router + four-tier cognitive memory + self-learning MetaSkills — this combination is rare in open source. LangChain solved "can it do this?"; OpenSquilla is solving "can we afford to do this at scale?"

**3. Ecosystem strategy is right**  
Apache 2.0 + 20+ providers + five-line plugin interface signals a team serious about building an ecosystem rather than a walled garden. 3,440 stars in one month is developers voting with their feet.

**Risk factors:** Still at v0.3.x — production stability is unproven. The 60-80% savings figure is for ideal workload distributions; actual results depend on your task mix. And SquillaRouter's routing quality directly determines experience quality — mis-tier routing degrades results.

## Quick Start

```bash
# Install (recommended path)
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.3.1/opensquilla-0.3.1-py3-none-any.whl"

# Configure and run
opensquilla onboard
opensquilla gateway run
```

Then open `http://127.0.0.1:18791/control/` for the Web UI.

---

If you're running AI agent workflows and getting crushed by token bills, OpenSquilla is worth half a day of serious experimentation.

**GitHub:** [opensquilla/opensquilla](https://github.com/opensquilla/opensquilla)  
**Website:** opensquilla.ai
