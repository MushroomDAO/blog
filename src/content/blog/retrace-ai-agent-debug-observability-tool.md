---
title: "Retrace：回放、分叉 AI Agent 运行记录，调试从此不再盲人摸象"
titleEn: "Retrace: Replay and Fork AI Agent Runs — Debug Without Guesswork"
description: "Retrace 是 AI Agent 可观测性和调试工具，记录每一次 LLM 调用、工具调用和错误，支持运行记录的回放和分叉（fork），让 AI Agent 调试从黑盒变透明。免费版每月 1,000 次 trace，面向 Claude Code/Cursor/OpenHands 等独立开发者。"
descriptionEn: "Retrace is an AI agent observability and debugging tool: records every LLM call, tool invocation, and error. Replay past runs, fork them to try alternative paths, and share traces with teammates. Free for 1,000 traces/month. Built for Claude Code, Cursor, OpenHands, and indie developers building AI agents."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-News"
tags: ["AI Agent", "可观测性", "调试", "LLM", "开发工具", "Claude Code", "Cursor", "OpenHands"]
heroImage: "../../assets/images/retrace-ai-agent-debug-observability-tool-banner.jpg"
---

> **产品**: [Retrace](https://retraceai.tech) · ProductHunt 新品 · 免费版 1,000 traces/月  
> **适合**: 独立开发者 / Claude Code / Cursor / OpenHands 用户

---

## AI Agent 调试的核心难题

你的 AI Agent 挂了。错误信息只有一行：`Agent execution failed`。

现在你怎么调试？

- 你不知道它调用了哪些工具
- 你不知道在哪一步 LLM 做了错误决策
- 你不知道是哪次工具调用出了问题
- 你不知道 token 花在哪里了

这就是 AI Agent 和普通程序的根本区别：**执行路径是非确定性的，每次运行可能走完全不同的路**。传统的 console.log 和 breakpoint 调试方法，在这里基本失效。

Retrace 是专门为这个问题设计的工具。

---

## Retrace 是什么？

**核心功能**：记录、回放、分叉 AI Agent 的执行过程。

你的 Agent 跑一次，Retrace 就记一次：
- 每次 LLM API 调用（输入/输出/token 消耗）
- 每次工具调用（名称/参数/结果/耗时）
- 每个错误（类型/发生位置/上下文）
- 完整的执行时间线

然后你可以：
1. **回放（Replay）**：像看视频一样回看整个 Agent 运行过程
2. **分叉（Fork）**：从任意一个节点出发，尝试不同的路径
3. **分享（Share）**：把某次运行的 trace 发给同事，他能看到和你完全相同的执行过程

---

## 关键功能详解

### 1. 时间线可视化

所有事件按时间排列：

```
t=0ms    → [LLM Call] System prompt + user query → model: claude-sonnet-4.6
t=230ms  → [Tool Call] search_web("AI observability tools")
t=1.2s   → [Tool Call] read_url("https://retraceai.tech")
t=2.1s   → [LLM Call] Context + tool results → model: claude-sonnet-4.6
t=2.8s   → [Tool Call] write_file("output.md")
t=3.1s   → [Done] Total: 3.1s, 4,230 tokens
```

看到这个，你立刻知道时间花在哪里、哪步工具调用了多久、LLM 被调了几次。

### 2. Fork（分叉）调试

这是 Retrace 最独特的功能。

假设你的 Agent 在第 3 步做了一个错误决策（比如调用了错误的工具），你想看：如果它做了不同的决策，后续会怎么走？

```
运行记录：
Step 1 → Step 2 → Step 3 (错误决策) → Step 4 → Step 5 (失败)

Fork 调试：
Step 1 → Step 2 → Step 3 (修改为正确决策) → ... (继续执行)
```

Fork 从你指定的节点重新开始执行，重用之前的 context，只在那个节点做出不同的选择。这让你可以精准地测试"如果换一种方式，结果会不同吗？"

### 3. 错误定位

当 Agent 出错，Retrace 不只是告诉你"出错了"，而是：
- 哪一次 LLM 调用生成了有问题的工具调用
- 哪一次工具调用返回了错误
- 错误发生时的完整上下文（之前的调用历史）

### 4. Token 消耗分析

```
LLM 调用 #1: input=2,340 tokens, output=180 tokens, cost=$0.0012
LLM 调用 #2: input=5,890 tokens, output=420 tokens, cost=$0.0031
总计: 8,230 tokens, $0.0043
```

对于有成本意识的开发者，这是优化的起点。

---

## 谁在用 Retrace？

XHS 上的 AI 创业机会扫描把 Retrace 定位为面向：
- **Claude Code/Cursor/OpenHands 用户**：日常用 AI 编程工具的独立开发者
- **AgentOps 需求者**：需要追踪 Agent 行为、成本、错误的小团队

免费版 1,000 traces/月 对独立开发者完全够用。

---

## 和现有工具的对比

| 工具 | 重点 | 是否支持 Fork |
|---|---|---|
| **Retrace** | 全程可观测 + 回放 + 分叉 | ✅ |
| LangSmith | LangChain 生态 tracing | ❌ |
| Arize | 生产级 LLM 监控 | ❌ |
| Weights & Biases | ML 实验追踪 | ❌ |

Fork 功能是 Retrace 独有的——其他工具记录，但 Retrace 让你干预和重放。

---

## 快速集成

```python
# Python Agent 集成（以 OpenAI 风格为例）
from retrace import RetraceCli

retrace = RetraceCli(api_key="YOUR_RETRACE_KEY")

# 包装你的 Agent 运行
with retrace.trace(name="my_agent_run"):
    result = my_agent.run(user_query)
    
# 运行结束后，在 retraceai.tech 的 dashboard 看回放
```

对于 Claude Code/OpenHands 等已有框架的工具，Retrace 通常有对应的集成插件或 MCP 接入方式。

---

## 免费版限制

| 指标 | 免费版 |
|---|---|
| Traces/月 | 1,000 |
| 存储时长 | 30 天 |
| 团队成员 | 1 人 |
| Fork 次数 | 无限制 |

1,000 traces 对大多数独立开发者的日常调试完全够用。

---

## 总结

AI Agent 调试一直是开发体验的痛点——你知道出了问题，但不知道为什么，也不容易复现。Retrace 把 Agent 执行变成可回放、可分叉的记录，把黑盒变成透明盒。

对于使用 Claude Code、Cursor、OpenHands 的独立开发者，这是一个值得加入工具箱的调试工具。

> **链接**: [Retrace 官网](https://retraceai.tech) · [ProductHunt](https://www.producthunt.com/products/retrace-2)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Retrace is an AI agent observability and debugging tool. It records every LLM call, tool invocation, and error your agent makes, then lets you replay the full execution timeline and fork from any point to try alternative paths. Free for 1,000 traces/month. Built for indie developers using Claude Code, Cursor, and OpenHands.

---

## The Problem with AI Agent Debugging

When your agent fails, traditional debugging falls short. The execution path is non-deterministic — every run may take different paths. You need to know:
- Which tool call failed
- Which LLM decision was wrong
- What the full context was when the error occurred

Retrace captures all of it.

## Core Capabilities

**Timeline Visualization**: Every event in sequence — LLM calls (prompt/response/tokens), tool invocations (name/args/result/duration), errors (type/context). You see exactly where time went and what happened.

**Replay**: Watch any past run like a video. Share the exact trace with a teammate — they see the same execution you saw.

**Fork (the killer feature)**: Pick any step in a past run and branch from it. "What if the agent had called a different tool at step 3?" Execute that branch, see what happens. No other observability tool for AI agents does this.

**Error Context**: Not just "error occurred" — but which LLM call generated the bad tool call, which tool returned the error, and what the full conversation history was at that moment.

**Token Tracking**: Per-call cost breakdown. Find which LLM calls are expensive, optimize from there.

## Pricing

Free: 1,000 traces/month, 30-day retention, unlimited forks. Enough for daily indie developer debugging.

**Links**: [retraceai.tech](https://retraceai.tech) · [ProductHunt](https://www.producthunt.com/products/retrace-2)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
