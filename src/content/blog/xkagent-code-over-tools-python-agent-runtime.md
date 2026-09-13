---
title: 'XKAgent：用写代码代替调工具，一个纯 Python 的极简 Agent Runtime'
titleEn: "XKAgent: Write Code Instead of Calling Tools — a Minimal Pure-Python Agent Runtime"
description: "XKAgent 用 pythonrt 让模型直接写 Python 代码执行任务，不需要预定义工具——一个执行原语覆盖所有能力。配合 Skills 热加载、Status 状态注入、mail.jsonl 多 Agent 邮件总线，29 stars，MIT 开源，值得关注的设计思路。"
descriptionEn: "XKAgent uses pythonrt to let the model write Python code directly instead of calling predefined tools — one execution primitive covers all capabilities. With hot-loadable Skills, Status context injection, and a mail.jsonl multi-agent bus. 29 stars, MIT licensed, an architecture worth watching."
pubDate: "2026-09-13"
updatedDate: "2026-09-13"
category: "Tech-News"
tags: ["AI-agent", "open-source", "Python", "agent-runtime", "code-execution", "multi-agent", "XKAgent"]
heroImage: "../../assets/xkagent-code-over-tools-python-agent-runtime-banner.jpg"
---

> 📌 开源仓库：xtudbxk/XKAgent
> GitHub：https://github.com/xtudbxk/XKAgent
> License：MIT | Stars：29
> 语言：Python | 核心依赖：requests（仅此一个）

---

主流 Agent 框架的标配是工具调用（Tool Calling）：给模型定义一批工具，模型选工具、填参数、等结果、再决定下一步。

XKAgent 问了一个不一样的问题：**如果模型直接写代码来完成任务，还需要预定义工具吗？**

它的答案是：大多数情况不需要。

---

## 一、pythonrt：代码就是工具

XKAgent 的核心是 `pythonrt`——一个 Python 代码执行内核。

传统做法：

```
模型 → 选工具（read_file）→ 填参数 → 调用 → 等结果 → 再选工具（write_file）→ ...
```

XKAgent 的做法：

```
模型 → 写 Python 代码 → pythonrt 执行 → 返回结果
```

模型不再从预定义工具列表里选一个，而是写一段 Python：读文件、转换数据、调用库、验证结果——全部在一次执行里完成，减少工具定义数量，也减少 LLM round trips。

这个设计的实际效果是：**pythonrt 是一个万能工具**，能力范围就是 Python 标准库 + 已安装的第三方库。不需要为每个新能力定义一个新工具。

核心依赖只有 `requests`（LLM 调用用）。pythonrt 本身只用标准库。想要 Web 界面、语义搜索、Git 支持的话，`pip install -r requirements.txt` 装可选依赖。

---

## 二、Skills：能力目录，热加载，不动主循环

增加新能力不需要改 Agent 代码——这是 Skills 要解决的问题。

一个 Skill 是一个自包含目录，里面放：
- 领域知识（文档、参考资料）
- 工作流定义
- 可复用脚本
- 操作指南

Skill 可以在运行时热加载，也可以覆盖已有 Skill。主循环不变，任务专属能力持续增长。

这有点像 Claude Code 自己的 `.agents/skills/` 机制：把专属能力封装成可插拔单元，核心保持精简，外围无限扩展。

---

## 三、Status：每轮注入的上下文看板

传统 Agent 只看到"用户最新消息"，上下文靠 chat history 堆积。XKAgent 在每次请求时额外注入一组状态：

- 当前时间
- 运行模式（plan / build / build-unsafe）
- 路径权限（哪些路径可读/可写）
- 建议使用的 Skills
- 检索到的相关信息

除了这些只读系统字段，还有一块**可写的 Status Info 看板**：

```
/addinfo <key> <value>  # 写入一条持久信息
/listinfo               # 列出所有条目
/rminfo <key>           # 删除
```

这些条目短小、持久、每轮都会注入，跨上下文压缩也保留。用途是：跨多轮任务维护关键状态，不需要把所有历史都塞进 context。长期 Memory 功能目前还在规划中，Status 是其预留的基础接口。

---

## 四、多 Agent 通信：mail.jsonl 邮件总线

v0.2.0 加入的 `callagent`，实现了跨会话的异步协作。

机制很直接：一个会话调用 `callagent`，把消息写入全局 `mail.jsonl`；每轮有个 carrier 把邮件投递给对应会话。

支持的功能：
- 延迟唤醒 / 绝对时间唤醒
- 消息优先级
- 回复链（多轮对话）
- 广播（一条消息→多个接收方）
- 每个接收方指定不同的 provider/model

和大多数多 Agent 框架不同，XKAgent 的多 Agent 通信是**异步的**——主会话不阻塞等待子 Agent 回复，mail.jsonl 是事件总线，不是同步 RPC。

pythonrt 内部也可以调 `agent` 把子任务委托给子 Agent：子 Agent 完成后返回结构化结果，主流程继续。子 Agent 不是并行工具系统，而是可组合、可嵌套的执行单元。

---

## 五、三级沙盒：渐进式信任

XKAgent 的安全模型是「渐进式信任」，不是全开放也不是全封闭：

| 模式 | 用途 | 权限 |
|------|------|------|
| 🔎 `plan` | 读代码、分析需求、制定计划 | 项目路径只读，/tmp 可写 |
| 🔧 `build` | 修改代码和文档 | 仅授权路径可写，轻量沙盒限制 |
| ⚡ `build-unsafe` | 运行测试或需要完整 Python 的任务 | 接近宿主 Python，仅有限防护 |

文档说得很直接：这个沙盒减少的是意外操作风险，不是对抗恶意代码的安全容器。进 `build-unsafe` 之前先提交 Git 或备份。

---

## 六、自修改：XKAgent 改 XKAgent

XKAgent 可以在自己的仓库里完成「设计→修改→热加载→验证」的完整闭环：

1. 在 `plan` 模式下读源码，理解边界，制定计划
2. 切 `build` 模式修改代码，review diff
3. `/restart` 热加载改动
4. 验证行为是否符合预期
5. 如果需要跑测试，切 `build-unsafe`，再 `/restart`

这不只是文档里的例子——XKAgent 的文档里明确建议用这种方式开发新 Skill 或修改 Agent 主循环。

---

## 快速开始

```bash
git clone https://github.com/xtudbxk/XKAgent.git xkagent
cd xkagent

# 最小安装（只需 requests）
python -m pip install requests

# 完整安装（含 Web / 语义搜索 / Git）
python -m pip install -r requirements.txt

# 配置 Provider
cp provider.config.example .xkagent/provider.config
# 编辑 provider.config，填入 api_key 或环境变量

# 启动 CLI
./run.sh --workdir .

# 启动 Web（默认 127.0.0.1:7860）
./run.sh --workdir . --mode web
```

Provider 配置支持 OpenAI 兼容接口和 Anthropic API，文件保存后热重载，不需要重启。

---

## 拆解结论

XKAgent 只有 29 stars，但设计思路值得关注——它在问一个系统性的问题：**工具调用是不是解决 Agent 能力扩展问题的正确抽象？**

它的回答是：把代码执行本身当作通用工具，Skills 处理领域知识扩展，Status 处理状态持久化，mail.jsonl 处理多 Agent 协调——四个正交的关注点，各司其职。

代码只有 Python，核心依赖一个包，能自改自，有多 Agent 总线，有三级沙盒——这是一个认真想过这些问题的设计。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: xtudbxk/XKAgent
> GitHub: https://github.com/xtudbxk/XKAgent
> License: MIT | Stars: 29
> Language: Python | Core dependency: requests (only one)

---

The standard playbook for Agent frameworks is tool calling: define a set of tools for the model, the model selects a tool, fills in parameters, waits for the result, decides next step.

XKAgent asks a different question: **if the model writes code directly to complete tasks, do you even need predefined tools?**

Its answer: mostly no.

---

## I. pythonrt: Code Is the Tool

XKAgent's core is `pythonrt` — a Python code execution kernel.

Traditional approach:

```
Model → pick tool (read_file) → fill params → call → wait → pick tool (write_file) → ...
```

XKAgent's approach:

```
Model → write Python code → pythonrt executes → returns result
```

The model doesn't pick from a predefined list. It writes Python: read files, transform data, call libraries, verify results — all in one execution, reducing both tool definition count and LLM round trips.

The practical effect: **pythonrt is a universal tool**, with capability bounded only by Python's standard library plus installed third-party packages. No new tool definition needed for each new capability.

Core dependency: just `requests` (for LLM calls). pythonrt itself uses only the standard library. Web UI, semantic search, and Git support are optional installs.

---

## II. Skills: Capability Directories, Hot-Loadable, No Core Changes

Adding new capabilities without modifying Agent code — that's what Skills solve.

A Skill is a self-contained directory containing:
- Domain knowledge (docs, references)
- Workflow definitions
- Reusable scripts
- Operation guides

Skills can be hot-loaded at runtime and can override existing Skills. The main loop stays stable; task-specific capabilities keep growing.

This resembles Claude Code's own `.agents/skills/` mechanism: package domain capabilities as pluggable units, keep the core minimal, extend endlessly at the edges.

---

## III. Status: Per-Round Context Injection

Traditional agents see only "the user's latest message," with context built up through accumulated chat history. XKAgent injects a status bundle on every request:

- Current time
- Runtime mode (plan / build / build-unsafe)
- Path permissions (which paths are readable/writable)
- Suggested Skills
- Retrieved relevant information

Beyond these read-only system fields, there's a **writable Status Info board**:

```
/addinfo <key> <value>  # write a persistent entry
/listinfo               # list all entries
/rminfo <key>           # remove
```

These entries are short, persistent, injected every round, and survive context compaction. The use case: maintain key state across multi-round tasks without stuffing all history into context. Full long-term Memory is planned; Status is the reserved foundation interface.

---

## IV. Multi-Agent Communication: The mail.jsonl Bus

Added in v0.2.0: `callagent` enables asynchronous cross-session collaboration.

The mechanism is straightforward: one session calls `callagent`, writes a message to a global `mail.jsonl`; a per-round carrier delivers mail to the target session.

Features:
- Delayed / absolute-time wake-ups
- Message priority
- Reply chains (multi-turn conversation between sessions)
- Broadcasts (one message → multiple recipients)
- Per-recipient provider/model override

Unlike most multi-agent frameworks, XKAgent's inter-agent communication is **asynchronous** — the main session doesn't block waiting for sub-agent replies. `mail.jsonl` is an event bus, not synchronous RPC.

Within pythonrt, you can also call `agent` to delegate subtasks to a sub-agent: the sub-agent returns a structured result, main flow continues. Sub-agents are composable, nestable execution units — not a parallel tool system.

---

## V. Three-Level Sandbox: Progressive Trust

XKAgent's security model is "progressive trust" — not fully open, not fully locked:

| Mode | Purpose | Permissions |
|---|---|---|
| 🔎 `plan` | Read code, analyze requirements, create plans | Project paths read-only; /tmp writable |
| 🔧 `build` | Modify code and documentation | Only authorized paths writable; lightweight restrictions |
| ⚡ `build-unsafe` | Run tests or tasks needing full Python | Near-host Python, minimal safeguards |

The docs are direct about this: the sandbox reduces accidental action risk, not malicious code risk. Commit to Git or backup before entering `build-unsafe`.

---

## VI. Self-Modification: XKAgent Modifying XKAgent

XKAgent can complete a full "design → modify → hot-reload → verify" cycle inside its own repository:

1. In `plan` mode: read source code, understand boundaries, create a plan
2. Switch to `build` mode: modify code, review diff
3. `/restart` to hot-load changes
4. Verify behavior matches expectations
5. If tests need full capabilities: switch to `build-unsafe`, then `/restart`

This isn't just a doc example — the documentation explicitly recommends this workflow for developing new Skills or modifying the Agent main loop.

---

## Quick Start

```bash
git clone https://github.com/xtudbxk/XKAgent.git xkagent
cd xkagent

# Minimal install (just requests)
python -m pip install requests

# Full install (Web / semantic search / Git)
python -m pip install -r requirements.txt

# Configure provider
cp provider.config.example .xkagent/provider.config
# Edit provider.config with your api_key or env var

# Start CLI
./run.sh --workdir .

# Start Web (default 127.0.0.1:7860)
./run.sh --workdir . --mode web
```

Provider config supports OpenAI-compatible and Anthropic APIs; hot-reloads on file save without restart.

---

## Teardown Summary

29 stars, but the design question is worth tracking: **is tool calling the right abstraction for Agent capability expansion?**

XKAgent's answer: use code execution as the universal tool, Skills for domain knowledge extension, Status for state persistence, mail.jsonl for multi-agent coordination — four orthogonal concerns, each handled by its own mechanism.

Pure Python, one core dependency, self-modifying, multi-agent bus, three-level sandbox. This is a design that's thought carefully about each of these problems.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
