---
title: "PenguinHarness：一句话让 Agent 自动构建 Agent，$0.02 生成完整 RAG 应用"
titleEn: "penguinharness-deepseek-self-evolving-agent-builder-002-usd"
description: "Prism-Shadow/penguin-harness 是一个开源 Agent 自动交付平台，TypeScript 编写，Apache-2.0。一句话描述需求，Agent 自动生成完整 Agent 应用（scaffold + 代码 + 运行说明）。接入 DeepSeek V4，数据分析精度全场最高，成本仅 Claude Code 的 1/70。内置 Agent 自进化：跑基准、找失分点、发布 N+1 版本。"
descriptionEn: "Prism-Shadow/penguin-harness is an open-source automated agent delivery platform written in TypeScript under Apache-2.0. Describe a need in one sentence — an agent builds the complete agent application for you (scaffold, code, run instructions). Integrates DeepSeek V4 for top data-analysis accuracy at 1/70 of Claude Code's cost. Built-in agent self-evolution: run benchmarks, identify gaps, ship version N+1."
pubDate: "2026-08-03"
updatedDate: "2026-08-03"
category: "Tech-News"
tags: ["Agent", "DeepSeek", "自进化", "开源工具", "TypeScript", "RAG", "AI基础设施", "Mycelium"]
heroImage: "../../assets/images/penguinharness-deepseek-self-evolving-agent-builder-002-usd-banner.jpg"
---

*by Mycelium Protocol*

---

构建一个 Agent 应用，通常的路径是：写 prompt、接工具、调参数、调试循环……一圈下来少则几小时，多则几天。

**[PenguinHarness](https://github.com/Prism-Shadow/penguin-harness)**（Prism-Shadow）把这个过程倒过来：你写一句话，Agent 帮你构建完整的 Agent 应用。

TypeScript，Apache-2.0，260 stars（2026 年 7 月 19 日开源，两周内）。

---

## 三个核心能力

### 1. Agent 自动构建 Agent（$0.02 完成一个完整 RAG 应用）

输入一句话：

```
Collect the docs from https://github.com/ericbuess/claude-code-docs 
and build a RAG app that answers Claude Code questions as a 
configuration expert, citing its sources.
```

PenguinHarness 会自动：
- 抓取目标文档
- 搭建 RAG 检索架构
- 写完整代码和运行说明
- 生成带引用来源的问答界面

整个过程在 DeepSeek V4 Pro 上消耗 **$0.02（约 ¥0.2）** 的 token。

### 2. 成本碾压：数据分析精度最高，成本 1/70

官方 benchmark（同任务对比）：

| Harness | 数据分析 | 编程任务 | 相对成本 |
|---------|---------|---------|---------|
| **PenguinHarness** | **最高** | ≈ OpenAI Codex | **1/70** |
| Claude Code | 对照 | 对照 | 1× |

关键设计选择：**最小工具集 + 干净的底层接口**。每次任务的 tool call 数量和 token 消耗都更少，专门针对 DeepSeek 等开放模型做了深度调优。

### 3. Agent 自进化：每轮跑完更强

内置 Agent Tuning Skills，让 Agent 对自己做基准测试、找失分点、自动发布下一版：

- 运行基准 → 找出哪些任务失败了
- 自动修改自身的 prompt/工具逻辑
- 打快照（每轮改前都保存）
- 在 Trace 视图里观察每一次请求

这套循环可以无人值守运行，每次迭代后 Agent 的能力都在增强。

---

## 内置 Skills

四组 Skill，覆盖从办公生产力到 Agent 自优化：

| 分组 | Skills |
|------|--------|
| 办公生产力 | `data-analysis`, `firecrawl` |
| 软件开发 | `web-design`, `software-engineering` |
| AI 应用开发 | `penguin-sdk`, `penguin-cli`, `llamafactory`, `ollama`, `vllm`... |
| Agent 调优 | `agent-creation`, `benchmark-design`, `agent-evaluation`, `agent-optimization` |

Agent 也可以自己写 Skill 并优化它。

---

## 支持的模型

涵盖当前主流 Frontier 和开放模型：

| 模型 | 支持渠道 |
|------|---------|
| DeepSeek V4 | DeepSeek、OpenRouter、SiliconFlow 等 |
| Kimi K3 | Moonshot AI、OpenRouter |
| GLM 5.2 | Z.AI、OpenRouter、SiliconFlow 等 |
| Qwen 3.8 Max | Qwen Token Plan（预览） |
| GPT 5.6 | OpenRouter |
| Gemini 3.6 Flash | Google Gemini、OpenRouter |
| Claude 5 | Anthropic、OpenRouter |

也支持任意 OpenAI 协议兼容端点，本地部署（Ollama/vLLM）同样可用。

---

## 一行安装

```bash
# Linux / macOS
curl -fsSL https://penguin.ooo/install.sh | sh
penguin web   # 启动 Web UI，访问 http://127.0.0.1:7364

# Windows (PowerShell)
irm https://penguin.ooo/install.ps1 | iex
penguin web

# npm（需要 Node >= 24）
npm install -g @prismshadow/penguin-cli
penguin web
```

Web UI 第一次登录：用户名 `admin`，密码 `penguin-2026`（记得立即修改）。

### CLI 快速上手

```bash
# 配置模型
penguin config model add \
  --provider deepseek \
  --model-id deepseek-v4-pro \
  --api-key sk-... \
  --set-default

# 一次性任务
penguin run -m "Create a Python script that parses CSV and outputs charts"

# 交互 REPL
penguin chat
```

### SDK（给 Agent 用 Agent）

```ts
import { createAgent, userText } from "@prismshadow/penguin-core";

const agent = await createAgent({ agentId: "default_agent" });
const session = await agent.createSession({ workspaceDir: process.cwd() });

for await (const output of session.run([userText("Build a RAG app for these docs: ...")], {
  approve: async () => "allow",
})) {
  // 流式接收输出
}
```

支持离线安装包（GitHub Releases 提供 Linux/macOS/Windows 各架构的 self-contained bundle），适合气隙环境部署。

---

## 为什么值得关注

**"Agent 构建 Agent"正在成为真实的工程能力**，而不是 PPT 概念。PenguinHarness 给这个概念加了三层约束：成本可控（$0.02 级别）、可观测（Trace 视图）、可进化（内置基准+自优化循环）。

DeepSeek 作为主力推理引擎的选择不只是性价比——官方 benchmark 显示它在数据分析任务上已经超过闭源竞品，而成本是 1/70。这个剪刀差在 Agent 密集调用的场景下会被放大。

Apache-2.0 开源，可以直接嵌入商业产品。

两周 260 stars，Roadmap 还列了桌面应用、Agent 公司模板、公司级自进化——项目还在早期，但方向感很清晰。

仓库：[github.com/Prism-Shadow/penguin-harness](https://github.com/Prism-Shadow/penguin-harness) · 官网：[penguin.ooo](https://penguin.ooo) · 文档：[penguin.ooo/docs](https://penguin.ooo/docs)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## PenguinHarness: An Agent That Builds Agents for $0.02

*by Mycelium Protocol*

Building an agent application normally means writing prompts, wiring tools, tuning parameters, and iterating through debug loops — hours or days of work.

**[PenguinHarness](https://github.com/Prism-Shadow/penguin-harness)** (Prism-Shadow) inverts the process: describe what you want in one sentence, and an agent builds the complete agent application for you.

TypeScript, Apache-2.0, 260 stars (open-sourced July 19, 2026 — two weeks).

### Three Core Capabilities

**1. Agent builds agent ($0.02 for a complete RAG application)**

Input a single sentence:

```
Collect the docs from https://github.com/ericbuess/claude-code-docs 
and build a RAG app that answers Claude Code questions as a 
configuration expert, citing its sources.
```

PenguinHarness autonomously fetches the docs, builds the retrieval architecture, writes complete code and run instructions, and generates a QA interface with cited sources. Cost on DeepSeek V4 Pro: **$0.02**.

**2. Cost compression: highest data-analysis accuracy at 1/70 the cost**

Official benchmark (same tasks, head-to-head):

| Harness | Data Analysis | Coding | Relative Cost |
|---------|---------------|--------|----------------|
| **PenguinHarness** | **Best** | ≈ OpenAI Codex | **1/70** |
| Claude Code | Baseline | Baseline | 1× |

Design choice: a deliberately minimal toolset over clean low-level interfaces — fewer tool calls, fewer tokens — deeply tuned for open models like DeepSeek.

**3. Self-evolution: each round makes it stronger**

Built-in Agent Tuning Skills run the benchmark, find where the agent loses points, auto-modify its own prompt/tool logic, take a snapshot before each change, and surface every request in the Trace view. This loop can run unattended, with capability improving after each iteration.

### Built-in Skills

| Group | Skills |
|-------|--------|
| Office Productivity | `data-analysis`, `firecrawl` |
| Software Development | `web-design`, `software-engineering` |
| AI App Development | `penguin-sdk`, `penguin-cli`, `llamafactory`, `ollama`, `vllm`... |
| Agent Tuning | `agent-creation`, `benchmark-design`, `agent-evaluation`, `agent-optimization` |

Agents can also write and optimize their own skills.

### One-Line Install

```bash
# Linux / macOS
curl -fsSL https://penguin.ooo/install.sh | sh
penguin web   # Web UI at http://127.0.0.1:7364

# Windows (PowerShell)
irm https://penguin.ooo/install.ps1 | iex

# npm (Node >= 24)
npm install -g @prismshadow/penguin-cli
```

First login: `admin` / `penguin-2026` (change immediately).

### Why This Matters

"Agent building agents" is becoming a real engineering capability, not a marketing claim. PenguinHarness adds three constraints that make it practical: controllable cost ($0.02-scale), observable (Trace view), and self-improving (built-in benchmark + optimization loop).

The DeepSeek integration isn't just a cost play — the official benchmark shows it outperforms closed-source competitors on data analysis at 1/70 the cost. That gap compounds dramatically in agent-intensive workloads.

Apache-2.0 means it can be embedded in commercial products. Two weeks in, 260 stars, with desktop app, agent company templates, and company-level self-evolution on the roadmap.

Repository: [github.com/Prism-Shadow/penguin-harness](https://github.com/Prism-Shadow/penguin-harness) · Website: [penguin.ooo](https://penguin.ooo) · Docs: [penguin.ooo/docs](https://penguin.ooo/docs)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
