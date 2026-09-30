---
title: "Stone Memory：不必重新认识——给 Claude Code / Codex 做线程记忆"
titleEn: "Stone Memory: No Need to Start Over — Thread Memory Management for Claude Code & Codex"
description: "wanyu445/stone_memory，9星，AGPL-3.0，JavaScript。本地优先的AI记忆与线程生命周期管理系统，专为 Claude Code / Codex 设计。归档对话 → 挖掘 feelings + features → 压缩 → 重建回目标线程，全程可解释，不依赖 embedding 黑箱。SQLite 作正式数据源，MCP Server 接入，本地 Web 工作台管理，支持手机局域网访问。"
descriptionEn: "wanyu445/stone_memory, 9 stars, AGPL-3.0, JavaScript. A local-first AI memory and thread lifecycle management system built for Claude Code and Codex. It archives conversations, extracts feelings (event summaries) and features (long-term traits), compresses by lifecycle stage, then rebuilds context into new threads. Fully explainable — no embedding black boxes. SQLite as the authoritative data store, MCP Server support, local Web dashboard, LAN/mobile access."
pubDate: 2026-09-30
heroImage: "../../assets/images/stone-memory-local-first-ai-memory-thread-lifecycle-claude-codex-banner.jpg"
category: "Tech-Experiment"
tags: ["AI记忆", "Claude Code", "Codex", "本地优先", "线程管理", "MCP", "开源拆解"]
lang: "zh-CN"
wechatTitle: "Stone Memory：AI记忆，不必重新认识"
wechatDigest: "9星AGPL-3.0；专为Claude Code/Codex；归档→挖掘→压缩→重建；SQLite+MCP；全程可解释不依赖embedding"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题

每次开新线程，都要把之前讲过的事重新讲一遍。

这不是 Claude Code 或 Codex 的 bug，是上下文窗口的物理约束——旧对话不能带过来。不少工具选择把记忆塞进系统提示，但"记了什么、为什么保留、来自哪段原文"都看不见，也改不了。

Stone Memory 从另一端入手：先把线程归档下来，在本地把对话蒸馏成可解释的摘要和特征，下次新建线程时再重建进去。

仓库：github.com/wanyu445/stone_memory  
**Stars：9 | License：AGPL-3.0 | 语言：JavaScript (Node.js 22+) | 版本：1.2.0**

---

## 核心流程：四个阶段

Stone Memory 不是"存对话、原文注入"的简单方案，它有一套完整的生命周期：

```
对话归档 → 记忆挖掘 → 精简保留 → 线程重建
```

### 阶段一：归档 (Archive)

从 Claude Code / Codex 线程归档纯对话到本地 JSONL。归档通过 Binding 完成——每个 Binding 对应一个 Claude/Codex 窗口，绑定后 Watcher 可以自动跟踪新消息。

### 阶段二：挖掘 (Mine)

两种模式：API 模式（直接调 LLM API）和 Subagent 模式（调 claude/codex CLI）。

挖掘产出两类记忆：
- **feelings**：事件摘要，从原文提炼，保留事件锚点指向原文
- **features**：长期特征，从多次 feelings 中提炼的稳定模式

这一步完全可审阅：`--check` 参数可以展示实际 prompt、输入、LLM 响应和解析结果。

### 阶段三：压缩 (Compress)

三级生命周期：
- **daily**：当天摘要，细粒度
- **coarse**：精简后的中期摘要（daily → coarse 仍在测试阶段）
- **hidden**：停止 rebuild 注入，但不删除完整 feeling（hidden → 删除 未实现）

**原文锚点 (retain) 和事件锚点 (event)** 保护关键内容不被精简掉。多词共同签名时间轴 + 关系阶段 + 项目证据共同决定摘要的保留优先级。

### 阶段四：重建 (Rebuild)

把以下内容组合回目标线程：
1. 人格与规则文档（rules/）
2. 可见的 feelings 摘要
3. 原文锚点对应片段
4. 近期上下文窗口
5. 保留的工具调用

Rebuild 有 dry-run（预览）和 apply 两步，Claude Code 还有安全队列模式（等下次主 MCP 启动时消费）。

---

## 可解释性的执行方式

Stone Memory 反复强调「可追溯」：

- 知道记忆来自哪段原文
- 知道为什么这条 feeling 被保留（importance + 锚点 + 时间轴权重）
- 知道下次 rebuild 会注入什么（`stmem rebuild --memory <id>` dry-run 先看）
- `deepsearch` 工具：交叉验证摘要与原文，生成 AI 第一人称深度报告

对比 embedding 召回：当你问"为什么突然提起两周前那件事"，embedding 只能说"相似度 0.87"，Stone Memory 可以给你看到 feeling ID、原文段落、anchor 标记。

---

## 技术架构

```text
~/.stone_memory/
├── stone-memory.db         全局 SQLite — messages/feelings/features 正式数据源
├── stmem.json              全局注册表 + API profiles（含密钥，不要提交）
└── memories/<memoryId>/
    ├── memory.json         记忆体设置（挖掘场景、rebuild 参数）
    ├── bindings.json       绑定的 Claude/Codex 窗口
    ├── watcher.json        自动归档/挖掘/压缩期望状态
    ├── rules/              线程重建时注入的人格 + 操作规则
    └── memory/archive/     原始对话 JSONL（年/月/日）
```

**数据分层**：SQLite 存结构化记忆，JSONL 存原文 archive——两者职责清晰不混用。Web 路由和 MCP 工具都是参数适配层，写入统一走 CLI。

**MCP Server**：stdio JSON-RPC，配置路径后可直接在 Claude Code 里调用 memory_search、rebuild、mine 等工具。

**本地 Web 工作台**：原生 HTML/CSS/JS（无框架依赖），默认监听 127.0.0.1:4173。局域网模式 (`stmem web lan enable`) 允许手机访问，使用一次性配对二维码认证。

---

## 场景选择

内置四个挖掘场景，影响 LLM 会关注哪些信息、生成什么类型的摘要：

| 场景 | 适用 |
|------|------|
| `life-supervision` | 生活监督，主要新建场景 |
| `accompany` | 情感陪伴 |
| `coding` | 编程与项目日志 |
| `study` | 旧学习场景，已有记忆体兼容 |

场景可以精细配置，也可以通过 `stmem prompt show` 直接查看当前使用的 prompt。

---

## 需要提前知道的约束

**AGPL-3.0**：集成到商业产品或作为 SaaS 托管，需将修改开源。内部工具使用不触发。

**daily→coarse 压缩仍在测试阶段**：README 明确标注。如果记忆体跑了很长时间，早期摘要的精简行为可能与预期不符。

**绑定 Claude Code / Codex**：不是通用记忆工具，与具体运行时深度绑定。切换到其他 AI 客户端需要手动适配。

**9 颗星，极早期**：项目创建于 2026-07-14，文档写得相当完整，但社区极小。遇到问题主要靠翻源码和提 issue。

**密钥管理**：`stmem.json` 含 API Key，`~/.stone_memory` 不要提交进仓库。

---

## 关键数字

| 指标 | 值 |
|------|----|
| Stars | 9 |
| License | AGPL-3.0 |
| 版本 | 1.2.0 |
| 语言 | JavaScript (Node.js 22+) |
| 存储 | SQLite + JSONL |
| MCP 接入 | stdio JSON-RPC |
| 创建时间 | 2026-07-14 |
| 挖掘场景 | 4个内置（可自定义） |

---

## 综合判断

Stone Memory 解决的问题真实存在——在 Claude Code 里长时间做同一个项目，总有一天上下文满了重开，然后要重新介绍一遍自己和项目背景。这不是一次性的烦恼，是反复发生的摩擦。

它选择「可解释的结构化记忆」而不是「embedding 黑箱召回」，这个立场有一定道理：如果你在乎的是"AI 对我的理解有没有偏差"，能审查记忆比召回更快更精确。代价是维护成本高——记忆要挖，要压缩，要重建，每一步都需要配置和干预。

如果你只是想让 Claude Code 记住你是谁、项目背景是什么，直接维护一个 CLAUDE.md 可能更省力。如果你想要更细粒度的控制——记住了什么、为什么记、什么时候忘——Stone Memory 是目前看到的最完整的本地方案之一。

9 颗星的数字不代表工程完成度。翻仓库：完整的 CLI 体系、MCP 接入、Web 工作台、Watcher 自动化、LAN 模式、多记忆体隔离——这些不是一周搭出来的。

---

> 开源仅供学习，商业使用请仔细核查许可证条款（AGPL-3.0 要求开源修改）。

---

<!--EN-->

## Stone Memory: No Need to Start Over — Thread Memory Management for Claude Code & Codex

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem

Every time you start a new thread, you have to re-introduce yourself and your project from scratch.

This isn't a bug in Claude Code or Codex — it's a physical constraint of context windows. Old conversations can't carry over. Most tools try to inject memories into the system prompt, but you can't see what was remembered, why it was kept, or which original text it came from.

Stone Memory approaches the problem from the other direction: archive threads locally, distill conversations into explainable summaries and traits, then rebuild that context into new threads.

Repo: github.com/wanyu445/stone_memory  
**9 stars | AGPL-3.0 | JavaScript (Node.js 22+) | v1.2.0**

---

### Core Workflow: Four Stages

Stone Memory isn't "store conversation, inject raw text." It has a complete lifecycle:

```
Archive → Mine → Compress → Rebuild
```

**Archive**: Pull conversation history from Claude Code / Codex threads via Bindings. Watcher can monitor automatically.

**Mine**: Extract two types of memory — **feelings** (event summaries pointing back to source text) and **features** (stable long-term traits derived from repeated feelings). Two modes: API (direct LLM calls) or Subagent (calls claude/codex CLI). Fully auditable: `--check` shows the actual prompt, input, LLM response, and parsing results.

**Compress**: Three lifecycle tiers — **daily** (fine-grained, current), **coarse** (compressed middle-term, still in testing), **hidden** (excluded from rebuild injection, not deleted). Retain anchors and event anchors protect critical content from compression. Lifecycle decisions use relationship stages, project evidence, and multi-term co-signature timelines.

**Rebuild**: Combines rules documents, visible feelings, anchor source text, recent context window, and preserved tool calls back into the target thread. Dry-run before apply; Claude Code has a safety queue mode.

---

### Why Explainability Matters Here

The anti-embedding-black-box stance is deliberate. When you ask "why did this come up after two weeks of silence?", embedding retrieval can only say "similarity: 0.87." Stone Memory can show you the feeling ID, the original text passage, and the anchor flag.

Key tools:
- `stmem rebuild --memory <id>` — dry-run preview of what will be injected
- `memory_search` via MCP — lightweight search with source text attached to summaries
- `deepsearch` — cross-validates summaries against source text, generates a first-person AI depth report

---

### Architecture

SQLite is the authoritative store for messages, feelings, and features. JSONL handles raw archives and imports. The Web UI and MCP tools are interface layers only — all writes go through the CLI.

**MCP Server**: stdio JSON-RPC. Configure once, then call memory_search, rebuild, mine, and other tools directly from Claude Code.

**Local Web dashboard**: Vanilla HTML/CSS/JS (no framework dependencies), localhost:4173 by default. LAN mode enables phone access with one-time pairing QR codes.

---

### What to Know Before Using

**AGPL-3.0**: Commercial products or SaaS hosting require open-sourcing modifications. Internal tooling use doesn't trigger this.

**daily→coarse compression is still in testing**: Marked explicitly in the README. Long-running memory bodies may behave unexpectedly during early-summary compression.

**Tightly coupled to Claude Code / Codex**: Not a general-purpose memory tool. Switching to other AI clients requires manual adaptation.

**9 stars, very early**: Created 2026-07-14. Documentation is thorough, but the community is tiny — expect to read source code and file issues.

**API key security**: `stmem.json` contains API keys. Don't commit `~/.stone_memory`.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 9 |
| License | AGPL-3.0 |
| Version | 1.2.0 |
| Runtime | Node.js 22+ |
| Storage | SQLite + JSONL |
| MCP | stdio JSON-RPC |
| Built-in scenarios | 4 |

---

### Verdict

The problem Stone Memory solves is real. Working long-term on a project in Claude Code always hits the same wall: context fills up, you open a new thread, and you spend the first ten minutes re-introducing yourself. That's not a one-time friction — it's a recurring tax.

The choice of explainable structured memory over embedding retrieval has merit: if you care whether the AI's understanding of you has drifted, being able to audit memories is more direct than tuning retrieval parameters.

The tradeoff is maintenance cost. Mining, compression, and rebuild each require configuration and attention. If you just want Claude Code to remember your name and project background, a well-maintained CLAUDE.md is probably less effort. If you want fine-grained control — what's remembered, why it's kept, when it fades — Stone Memory is the most complete local solution currently available.

9 stars undersells the engineering here: full CLI system, MCP integration, Web dashboard, automated Watcher, LAN mode, multi-memory-body isolation. This took real time to build.

---

> Open source for learning only. Verify AGPL-3.0 terms before commercial use.
