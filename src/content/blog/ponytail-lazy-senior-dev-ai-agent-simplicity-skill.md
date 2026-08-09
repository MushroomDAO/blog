---
title: "Ponytail：把「最懒的资深工程师」塞进你的 AI Agent——54% 代码减少，100% 安全"
titleEn: "Ponytail: Put the Laziest Senior Engineer Inside Your AI Agent — 54% Less Code, 100% Safe"
description: "Ponytail 是一个 AI Agent 插件（Claude Code / Codex / Gemini / Cursor 等 20+ 平台），让 Agent 在写代码前先过一遍「最小可行解」的七级阶梯：从 YAGNI、复用、stdlib、原生平台特性，到单行实现，最后才是最小化实现。真实基准测试：-54% 代码量、-20% 成本、-27% 时间，安全检查 100% 通过。97K stars，MIT，JavaScript。"
descriptionEn: "Ponytail is an AI agent plugin (Claude Code / Codex / Gemini CLI / Cursor and 20+ more) that installs a laziness ladder: before writing code, stop at the first rung that holds — YAGNI, reuse, stdlib, native platform feature, one-liner, only then minimum that works. Real agentic benchmark: -54% LOC, -20% cost, -27% time, 100% safety. 97K stars, MIT."
pubDate: "2026-08-06"
updatedDate: "2026-08-06"
category: "Tech-News"
tags: ["AI Agent", "Claude Code", "开发工具", "代码简化", "插件", "提示工程", "YAGNI", "Mycelium"]
heroImage: "../../assets/images/ponytail-lazy-senior-dev-ai-agent-simplicity-skill-banner.jpg"
---

*by Mycelium Protocol*

---

你认识这个人。马尾辫，椭圆形眼镜，在这家公司待的时间比版本控制系统还长。你给他看五十行代码，他什么都不说，用一行替换了它们。

**[Ponytail](https://github.com/DietrichGebert/ponytail)** 把他塞进了你的 AI Agent。

97K stars，MIT，2026 年 6 月上线，两个月成为今年 GitHub 增长最快的开发工具之一。

---

## 问题是什么

你让 Agent 做一个日期选择器。

Agent 安装了 flatpickr，写了一个 wrapper 组件，加了一个样式表，还开始讨论时区问题。

用了 Ponytail 之后：

```html
<!-- ponytail: browser has one -->
<input type="date">
```

就这一行。浏览器自带了。

这不是刻意偷懒，而是 Agent 在接到任务后先停下来问了一个更基本的问题：**这个东西需要被写吗？**

---

## 七级简化阶梯

Ponytail 在 Agent 动手写代码之前，让它先依次过一遍七个问题：

```
1. 这个东西需要存在吗？   → 不需要：跳过（YAGNI）
2. 代码库里已经有了吗？  → 复用，不要重写
3. 标准库能做吗？         → 用标准库
4. 平台原生特性能做吗？  → 用原生特性
5. 已安装的依赖能做吗？  → 用现有依赖
6. 一行能写完吗？         → 只写一行
7. 以上都不行：最小化实现
```

**在第一个能成立的梯级停下来**。

关键是：阶梯运行在*理解问题之后*，而不是代替理解问题。Ponytail 要求 Agent 在选梯级之前认真读懂涉及的代码、追踪真实调用链。对方案懒，从不对阅读懒。

**什么不能省**：信任边界的验证、数据丢失处理、安全检查、无障碍（accessibility）——这些从来不在被省略之列。

---

## 真实基准测试数据

这不是一个 prompt 的单次演示。基准测试的设计是：**用 headless Claude Code 编辑一个真实开源仓库**（[tiangolo/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)，FastAPI + React），12 个功能 ticket，有无 Ponytail 对比，Haiku 4.5，每个 ticket 跑 4 次，看留下的 `git diff`。

| 对比基准（无 skill） | 代码量 | Token | 成本 | 时间 | 安全 |
|---|--:|--:|--:|--:|--:|
| **ponytail** | **-54%** | **-22%** | **-20%** | **-27%** | **100%** |
| caveman（对照组） | -20% | +7% | +3% | +2% | 100% |
| "YAGNI + one-liners" 纯 prompt | -33% | -14% | -21% | -30% | 95% |

三个发现：

**1. 唯一在所有维度上都下降的方案。** caveman 减少了代码量但增加了 token 消耗；纯 prompt 方式降低了成本和时间，但安全检查只有 95%（它省掉了一个安全防护）。Ponytail 是唯一全部下降且安全 100% 的。

**2. 减少幅度与过度构建程度正相关。** 日期选择器：从 404 行缩减到 23 行（代码减少 94%）；颜色选择器：从 287 行到 23 行。已经很精简的代码几乎不变。

**3. "最少 token"不是目标。** 规则是"只写任务需要的"——代码小是结果，不是被高尔夫式削减的产物。

---

## 与 caveman 的关系

Ponytail 经常被和 [caveman](https://github.com/JuliusBrussee/caveman) 对比，两者可以共存：

- **caveman** 缩减 Agent 说的话（输出文字）——对代码字节级不动
- **Ponytail** 缩减 Agent 构建的东西（代码量）——对输出文字不动

"简洁地谈论最小化代码。"两者组合，消耗更少，写出更少，两个维度同时优化。

---

## 四个强度模式

| 模式 | 说明 |
|------|------|
| `lite` | 只激活最保守的几个梯级 |
| `full` | 默认模式，完整七级阶梯 |
| `ultra` | "当代码库曾经伤害过你个人" |
| `off` | 关闭 |

用 `PONYTAIL_DEFAULT_MODE` 环境变量或 `~/.config/ponytail/config.json` 设置每次会话的默认模式。切换命令：`/ponytail lite|full|ultra|off`。

---

## 六个内置命令

| 命令 | 作用 |
|------|------|
| `/ponytail [lite\|full\|ultra\|off]` | 切换强度 / 查看当前级别 |
| `/ponytail-review` | 审查当前 diff，输出过度工程的删除清单 |
| `/ponytail-audit` | 审查整个仓库（不只是 diff）的过度工程 |
| `/ponytail-debt` | 整理所有被标注为 `ponytail:` 的技术债备忘 |
| `/ponytail-gain` | 显示基准测试的实测收益（代码减少、成本降低、速度提升） |
| `/ponytail-help` | 命令快速参考 |

---

## 安装方式（20+ 平台）

### Claude Code

```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

（两条命令需要分开发送）

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

### Gemini CLI / Antigravity CLI

```bash
gemini extensions install https://github.com/DietrichGebert/ponytail
# 或 Antigravity：
agy plugin install https://github.com/DietrichGebert/ponytail
```

### OpenCode

```json
{ "plugin": ["@dietrichgebert/ponytail"] }
```

### Cursor / Windsurf / Cline / Kiro / Zed / Aider

从仓库复制对应规则文件：`.cursor/rules/`、`.windsurf/rules/`、`.clinerules/`、`.kiro/steering/`、`AGENTS.md`（Jules、Amp、CodeWhale 直接读这个，零配置）。

Subagent 传播：活跃期间，规则集会被自动注入每个通过 Agent 工具生成的子 Agent。用 `PONYTAIL_SUBAGENT_MATCHER` 环境变量（正则）控制哪些子 Agent 类型接收注入。

---

## 为什么值得关注

Agent 工具的竞争大多集中在"更智能的单步执行"上：更准的代码生成、更聪明的工具调用。Ponytail 关注的是另一个问题：**AI Agent 系统性地过度构建**。

这不是模型能力的问题，而是激励结构的问题。Agent 被训练来"完成任务"，完成的证明往往是"写了东西"。没有人告诉它"浏览器自带了日期选择器"比"安装 flatpickr 并写 wrapper"更好——直到 Ponytail 来做这件事。

两个月近 10 万 stars，说明这个问题触到了很多开发者的痛点。

已有多个衍生项目：ponytail-lite（只用一个 AGENTS.md 不依赖插件体系）、ponytail-hermes、ponystack（结合 gstack 流程），以及将 Karpathy LLM 编码指南与 Ponytail 懒惰阶梯合并的实验。

官网（waitlist 开放中）：[ponytail.dev](https://ponytail.dev/soon)  
仓库：[github.com/DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

---

> "你没写的代码可以无限扩展。零 bug，零 CVE，从来没有宕机过。"

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Ponytail: The Laziest Senior Dev Inside Your AI Agent

*by Mycelium Protocol*

You know him. Long ponytail. Oval glasses. He's been at the company longer than version control. You show him fifty lines. He says nothing. He replaces them with one.

**[Ponytail](https://github.com/DietrichGebert/ponytail)** puts him inside your AI agent. 97K stars, MIT, launched June 2026 — one of the fastest-growing developer tools on GitHub this year.

---

### The Problem

You ask your agent for a date picker.

It installs flatpickr, writes a wrapper component, adds a stylesheet, and starts a discussion about timezones.

With Ponytail:

```html
<!-- ponytail: browser has one -->
<input type="date">
```

One line. The browser already had one.

This isn't lazy in the bad sense — the agent read the task carefully, traced the codebase, and asked a more fundamental question: **does this thing need to be written at all?**

---

### The Seven-Rung Laziness Ladder

Before writing code, Ponytail makes the agent stop at the first rung that holds:

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Already in this codebase?  → reuse it, don't rewrite
3. Stdlib does it?            → use it
4. Native platform feature?   → use it
5. Installed dependency?      → use it
6. One line?                  → one line
7. Only then: the minimum that works
```

The ladder runs *after* the agent understands the problem — not instead of it. Ponytail requires the agent to read the code it touches and trace the real call flow before picking a rung. Lazy about the solution, never about reading.

**Always kept:** trust-boundary validation, data-loss handling, security, accessibility — never on the chopping block.

---

### Real Benchmark Numbers

Not a single-shot demo. The measurement: a headless Claude Code session editing [tiangolo/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) (a real FastAPI + React repo), 12 feature tickets, with and without the skill, Haiku 4.5, n=4, scored on the `git diff` left behind.

| vs no-skill baseline | LOC | tokens | cost | time | safe |
|---|--:|--:|--:|--:|--:|
| **ponytail** | **-54%** | **-22%** | **-20%** | **-27%** | **100%** |
| caveman (terse-prose control) | -20% | +7% | +3% | +2% | 100% |
| "YAGNI + one-liners" prompt | -33% | -14% | -21% | -30% | 95% |

Three findings:

**Only arm that cuts every metric.** caveman reduces LOC but increases token consumption; the raw prompt drops cost and time but only 95% safe (it drops a safety guard). Ponytail is the only one that cuts all four while staying fully safe.

**Reduction correlates with how much the agent would over-build.** Date picker: 404 → 23 lines (94% reduction). Color picker: 287 → 23 lines. Code that was already minimal barely changes.

**"Fewest tokens" is not the rule.** The rule is "write only what the task needs." Small code is the outcome, not the target.

---

### Relationship with caveman

Ponytail and [caveman](https://github.com/JuliusBrussee/caveman) are complementary, not competing:

- **caveman** shrinks what the agent *says* — leaves code byte-for-byte exact
- **ponytail** shrinks what the agent *builds* — leaves output prose untouched

Together: terse talk about minimal code. Both running simultaneously, each doing its half.

---

### Four Intensity Modes

| Mode | Description |
|------|-------------|
| `lite` | Most conservative rungs only |
| `full` | Default — full seven-rung ladder |
| `ultra` | "For when the codebase has wronged you personally" |
| `off` | Disabled |

Set per-session default via `PONYTAIL_DEFAULT_MODE` env var or `~/.config/ponytail/config.json`. Switch mid-session with `/ponytail lite|full|ultra|off`.

---

### Six Built-in Commands

| Command | What it does |
|---------|--------------|
| `/ponytail [lite\|full\|ultra\|off]` | Switch mode or report current level |
| `/ponytail-review` | Review current diff for over-engineering, return a delete-list |
| `/ponytail-audit` | Audit the whole repo, not just the diff |
| `/ponytail-debt` | Harvest deferred `ponytail:` shortcuts into a ledger |
| `/ponytail-gain` | Show the measured impact scoreboard from the benchmark |
| `/ponytail-help` | Quick command reference |

---

### Install (20+ Platforms)

**Claude Code:**
```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```
(Two separate prompts required)

**Codex:**
```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

**Gemini CLI / Antigravity CLI:**
```bash
gemini extensions install https://github.com/DietrichGebert/ponytail
```

**OpenCode:**
```json
{ "plugin": ["@dietrichgebert/ponytail"] }
```

**Cursor / Windsurf / Cline / Kiro / Aider:** copy the matching rules file (`.cursor/rules/`, `.kiro/steering/ponytail.md`, etc.). Agents that auto-load `AGENTS.md` (Jules, Amp, CodeWhale, Swival, Qoder) work with zero setup from the repo root.

**Subagent propagation:** the ruleset is injected into every subagent spawned via the Agent tool. Use `PONYTAIL_SUBAGENT_MATCHER` (a regex against agent type) to scope the injection.

---

### Why It Matters

Competition in agent tooling has focused on smarter single-step execution — better code generation, more accurate tool calls. Ponytail addresses a different problem: **AI agents systematically over-build**.

This isn't a model capability problem; it's an incentive structure problem. Agents are trained to "complete tasks," and completion is often evidenced by "wrote something." Nobody told the agent that `<input type="date">` is better than flatpickr + wrapper + stylesheet — until Ponytail does.

Nearly 100K stars in two months shows this hits a real nerve. The ecosystem is already branching: ponytail-lite (a single AGENTS.md without the plugin infrastructure), ponystack (combining gstack's process with Ponytail's restraint), Karpathy–Ponytail skill fusions, and more.

Waitlist: [ponytail.dev](https://ponytail.dev/soon) · Repository: [github.com/DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

---

> "The code you never wrote scales infinitely. Zero bugs, zero CVEs, 100% uptime since forever."

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
