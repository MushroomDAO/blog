---
title: 'Webwright：微软开源的浏览器 Agent，Code-as-Action 在 Mind2Web 上拿到 86.7%'
titleEn: "Webwright: Microsoft's Open-Source Browser Agent — Code-as-Action Achieves 86.7% on Mind2Web"
description: "MIT 开源，~450 行核心循环，用 Playwright Python 脚本替代像素坐标点击。Online-Mind2Web GPT-5.4 86.7%，Odysseys 长时域任务 +15.6pp SOTA，Skill Factory 将 WebArena 准确率从 55% 提升至 70%。6K stars，微软出品。"
descriptionEn: "MIT open-source, ~450-line core loop, Playwright Python scripts replace pixel-coordinate clicking. Online-Mind2Web GPT-5.4 86.7%, Odysseys long-horizon +15.6pp SOTA, Skill Factory lifts WebArena accuracy from 55% to 70%. 6K stars, from Microsoft."
pubDate: "2026-09-15"
updatedDate: "2026-09-15"
category: "Tech-News"
tags: ["browser-agent", "open-source", "Microsoft", "Playwright", "code-as-action", "web-automation", "AI-agent", "benchmark"]
heroImage: "../../assets/images/webwright-microsoft-browser-agent-playwright-code-as-action-banner.jpg"
---

> 📌 开源仓库：microsoft/Webwright
> GitHub：https://github.com/microsoft/Webwright
> License：MIT | Stars：5,996
> 作者：Yadong Lu, Lingrui Xu, Chao Huang, Ahmed Awadallah（微软）

---

大多数浏览器 Agent 做的事是：截图 → 识别位置 → 预测坐标 → 点击。

Webwright 的做法不同：**把浏览器当作代码执行的对象，而不是感知的对象。** 模型写 Playwright Python 脚本，脚本操作浏览器，结果写回本地工作区——不用每步截图，不用每步打坐标。

---

## 一、为什么 Code-as-Action 比坐标点击强

**坐标点击（screenshot + xy-coordinate）的问题**：

每一步都要截图、分析、生成坐标、点击、再截图——这是一条线性链，中间任何一环出错（识别偏移、元素遮挡、DOM 变化）就从头来过，而且每步都消耗视觉 token。

**Webwright 的做法**：

模型写一段 Playwright 代码，直接描述操作序列——`page.click("#submit-button")`、`page.fill("input[type=email]", value)` 这类语义操作，而不是"点击坐标 (342, 518)"。代码可以重跑、可以调试、可以复用。

更关键的是：**本地工作区（代码 + 日志）是状态，不是浏览器会话**。这意味着：
- 脚本可以跨任务复用
- Agent 重启后工作区不丢失
- 多步操作可以在一次代码执行里完成

---

## 二、基准测试结果

**Online-Mind2Web（300 个真实网页任务）**：

| 模型 | 准确率 |
|------|--------|
| GPT-5.4 | **86.7%** |
| Claude Opus 4.7 | **84.7%** |

**Odysseys（200 个长时域任务）**：

| 模型 | 准确率 |
|------|--------|
| GPT-5.4 | **60.1%** |

这个 60.1% 比此前 SOTA 高 **+15.6 个百分点**，且 Odysseys 专门设计来测"做完一件需要多步骤的事"——对真实 Agent 场景更有参考价值。

**WebArena + Skill Factory**：
- 基础准确率：55%
- 启用 Skill Factory 后：**70%**（+15 pp）

Skill Factory 是后面会详细说的机制，意义在于：已经解过的任务不用再让模型重新想——复用代码，零 token 消耗。

---

## 三、代码规模：极简

这不是一个塞满功能的大框架：

| 组件 | 行数 |
|------|------|
| 核心 agent 循环 | ~450 |
| Playwright 环境 | ~570 |
| CLI 接口 | ~150 |

依赖只有四个：`httpx`、`pydantic`、`playwright`、`typer`。

这个规模的好处是：可以完整读完，可以 fork 改造，可以嵌进别的系统，不会被框架细节淹没。

---

## 四、Skill Factory：解过的任务不再重算

Skill Factory 是 Webwright 里设计最独特的部分。

工作流：
1. Agent 完成一个任务，生成了 Playwright 脚本
2. 该脚本被参数化、封装成独立 Skill
3. 下次遇到类似任务，直接运行 Skill——**约 40 秒，零 token**

在 WebArena 上，这个机制把准确率从 55% 提升到 70%。

背后的逻辑是：浏览器上很多任务是高度重复的——登录、搜索、填表、提交——第一次让 Agent 完整思考，之后都走确定性脚本。这是用代码形态做的"经验记忆"。

---

## 五、架构和支持后端

```
webwright/
├── agents/default.py       # 核心 agent 循环（~450 行）
├── environments/           # Playwright 工作区
├── models/                 # OpenAI / Anthropic / OpenRouter 后端
└── skills/webwright/       # Claude Code / Codex / OpenClaw / Hermes 插件清单
```

**支持的模型后端**：
- OpenAI：GPT-5.4 及以上
- Anthropic：Claude Opus 4.7、4.6
- OpenRouter：任意兼容模型

**插件集成**：已提供 Claude Code、Codex、OpenClaw、Hermes 的 skill 清单，可以直接作为这些平台的插件调用，不需要额外 API 成本。

---

## 快速开始

```bash
pip install -e .
playwright install chromium

python -m webwright.run.cli \
    -c base.yaml -c model_openai.yaml \
    -t "在 Amazon 上搜索机械键盘并找到价格最低的" \
    --start-url https://amazon.com \
    --task-id demo_01 \
    -o outputs/default
```

---

## 拆解结论

Webwright 在几个维度上都值得关注：

**数字上**：Mind2Web 86.7%、Odysseys +15.6pp，是当前公开基准里排得上的成绩。

**工程上**：~450 行核心循环，极简依赖——这是可以读懂、可以改造的规模。

**思路上**：Code-as-Action vs 坐标点击，Skill Factory 的"已解任务变代码"——这两个设计思路在其他 Agent 框架里不多见。

对比 Stagehand、browser-use 这些框架，Webwright 的差异在于：**把本地工作区当状态，而不是浏览器会话当状态**，这让任务经验可积累、可复用。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: microsoft/Webwright
> GitHub: https://github.com/microsoft/Webwright
> License: MIT | Stars: 5,996
> Authors: Yadong Lu, Lingrui Xu, Chao Huang, Ahmed Awadallah (Microsoft)

---

Most browser agents work like this: screenshot → detect position → predict coordinates → click.

Webwright does something different: **treat the browser as an object of code execution, not an object of perception.** The model writes Playwright Python scripts; scripts operate the browser; results are written back to the local workspace — no per-step screenshots, no per-step coordinates.

---

## I. Why Code-as-Action Beats Coordinate Clicking

**The problem with screenshot + xy-coordinate:**

Every step requires a screenshot, analysis, coordinate generation, a click, and another screenshot — a linear chain where any link failure (detection offset, element occlusion, DOM change) means starting over, and every step burns visual tokens.

**Webwright's approach:**

The model writes a Playwright script that directly describes the operation sequence — `page.click("#submit-button")`, `page.fill("input[type=email]", value)` — semantic operations, not "click coordinate (342, 518)." Code can be re-run, debugged, and reused.

The key insight: **the local workspace (code + logs) is the state, not the browser session.** This means:
- Scripts are reusable across tasks
- The workspace survives agent restarts
- Multi-step operations complete in a single code execution

---

## II. Benchmark Results

**Online-Mind2Web (300 real web tasks):**

| Model | Accuracy |
|-------|----------|
| GPT-5.4 | **86.7%** |
| Claude Opus 4.7 | **84.7%** |

**Odysseys (200 long-horizon tasks):**

| Model | Accuracy |
|-------|----------|
| GPT-5.4 | **60.1%** |

That 60.1% is **+15.6 points over prior SOTA**. Odysseys is specifically designed to test "completing something that requires many steps" — more relevant to real-world agent scenarios than click-accuracy benchmarks.

**WebArena + Skill Factory:**
- Base accuracy: 55%
- With Skill Factory: **70%** (+15 pp)

---

## III. Codebase Size: Genuinely Minimal

| Component | Lines |
|-----------|-------|
| Core agent loop | ~450 |
| Playwright environment | ~570 |
| CLI interface | ~150 |

Four dependencies: `httpx`, `pydantic`, `playwright`, `typer`.

At this scale, you can read it end to end, fork and modify it, embed it into other systems — without getting buried in framework internals.

---

## IV. Skill Factory: Never Solve the Same Task Twice

Skill Factory is Webwright's most distinctive design.

Workflow:
1. Agent completes a task, produces a Playwright script
2. That script is parameterized and packaged as a standalone Skill
3. Next time a similar task appears, run the Skill — **~40 seconds, zero tokens**

On WebArena, this mechanism lifted accuracy from 55% to 70%.

The logic: many browser tasks are highly repetitive — login, search, fill, submit. The agent thinks it through once, then all future instances run deterministic scripts. It's "experience memory" in code form.

---

## V. Architecture and Supported Backends

```
webwright/
├── agents/default.py       # core agent loop (~450 lines)
├── environments/           # Playwright workspace
├── models/                 # OpenAI / Anthropic / OpenRouter backends
└── skills/webwright/       # plugin manifests for Claude Code / Codex / OpenClaw / Hermes
```

**Supported model backends:**
- OpenAI: GPT-5.4 and above
- Anthropic: Claude Opus 4.7, 4.6
- OpenRouter: any compatible model

**Plugin integrations:** Skill manifests already provided for Claude Code, Codex, OpenClaw, and Hermes — call Webwright directly as a plugin without extra API costs.

---

## Quick Start

```bash
pip install -e .
playwright install chromium

python -m webwright.run.cli \
    -c base.yaml -c model_openai.yaml \
    -t "Search for mechanical keyboards on Amazon and find the lowest price" \
    --start-url https://amazon.com \
    --task-id demo_01 \
    -o outputs/default
```

---

## Teardown Summary

Webwright stands out on several dimensions:

**Numbers:** Mind2Web 86.7%, Odysseys +15.6pp — leading scores on current public benchmarks.

**Engineering:** ~450-line core loop, minimal dependencies — a codebase you can actually read and modify.

**Design:** Code-as-Action vs. coordinate clicking, and Skill Factory's "solved tasks become code" — two ideas you won't find widely implemented in other browser agent frameworks.

Compared to Stagehand, browser-use, and similar frameworks, Webwright's key differentiator is: **local workspace as state, not browser session as state** — making task experience accumulate and remain reusable.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
