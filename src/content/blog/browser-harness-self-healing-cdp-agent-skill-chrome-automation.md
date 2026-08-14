---
title: "browser-harness：一个会自己写代码的浏览器 Agent 工具——每次运行都在让自己变聪明"
titleEn: "browser-harness-self-healing-cdp-agent-skill-chrome-automation"
description: "browser-use/browser-harness 是一个通过 Chrome DevTools Protocol（CDP）直接控制真实浏览器的 Agent 工具——没有 Selenium、没有 Playwright 包装层，一条 WebSocket 到底。Agent 遇到不会的操作，就地写 helper 函数，下次复用；遇到特定网站的操作，自动生成 domain skill 文件并归档。核心代码约 1000 行，4 个核心文件。是 Claude Code、Codex、Cursor 等 Agent 的「浏览器能力插件」。"
descriptionEn: "browser-use/browser-harness is an Agent browser-control tool that connects directly to Chrome via Chrome DevTools Protocol (CDP) — no Selenium, no Playwright wrapper, one WebSocket all the way. When the agent encounters an unfamiliar operation, it writes a helper function on the spot and reuses it next time. For site-specific tasks, it auto-generates domain skill files. ~1000 lines of code, 4 core files. Designed as the browser capability plugin for agents like Claude Code, Codex, and Cursor."
pubDate: "2026-08-14"
updatedDate: "2026-08-14"
category: "Tech-News"
tags: ["浏览器自动化", "Agent工具", "CDP", "browser-use", "Claude Code", "自修复", "开源", "Python"]
heroImage: "../../assets/images/browser-harness-self-healing-cdp-agent-skill-chrome-automation-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/browser-use/browser-harness  
许可证：开源  
核心代码：~1000 行（4 个核心文件）  
关联项目：browser-use/browser-use（Python 库，月下载 ~1M）

---

「你再也不用亲自打开浏览器了。」——这是 browser-harness README 开头的一句话。

说这话的背景是：这个工具不只是「让 AI 操作浏览器」，它在让 AI 变成你的浏览器能力积累者——它每次遇到新的操作，就学会一次，然后把学到的存下来，下次直接用。

---

## 一、架构：一条 WebSocket，没有中间层

browser-harness 通过 Chrome DevTools Protocol（CDP）直接连接到正在运行的 Chrome 实例，没有 Selenium WebDriver、没有 Playwright 的 Python wrapper——一条 WebSocket 到底。

```
Agent（Claude Code / Codex / Cursor）
      ↓ browser-harness 命令
browser-harness daemon
      ↓ WebSocket (CDP)
Chrome / Chromium
```

核心文件只有四个：

- `install.md` — 首次安装和浏览器引导
- `SKILL.md` — 日常使用说明
- `src/browser_harness/` — protected core package
- `agent-workspace/agent_helpers.py` — **Agent 可以修改这个文件**
- `agent-workspace/domain-skills/` — **Agent 自动生成的 site-specific skills**

总代码量约 1000 行。

---

## 二、自修复机制：Agent 遇到不会的，就地写

这是 browser-harness 最不寻常的设计：

```
Agent 尝试上传文件
      ↓
agent_helpers.py 里没有 upload_file helper
      ↓
Agent 在执行过程中直接写出 upload_file() 函数
      ↓
文件上传成功
      ↓
upload_file() 存入 agent_helpers.py，下次直接调用
```

每次运行，`agent_helpers.py` 都可能被 Agent 扩充。这是一个真正的「在工作中学习」机制——不是 few-shot prompting，是持久化的代码积累。

**Domain Skills** 是进一步的抽象：针对特定网站（如 LinkedIn、GitHub、Amazon）的操作 SOP，存储在 `domain-skills/<site>/` 目录下。Agent 第一次摸索出怎么在 LinkedIn 发私信，就把这个流程写成 domain skill；下次同类任务直接读取，而不是重新推理。

---

## 三、作为 Agent 工具插件使用

browser-harness 不是独立的 Agent，它是给其他 Agent（Claude Code、Codex、Cursor、Hermes 等）用的「浏览器能力插件」。

安装方式是把这段 Prompt 粘给你的 Agent：

```
Install or upgrade browser-harness to the latest stable version with uv using Python 3.12,
register the skill from `browser-harness skill`, and connect it to my browser.
Ask whether I want local browser recordings enabled; default to no and preserve my
existing preference on upgrades. Follow https://github.com/browser-use/browser-harness/blob/main/install.md
if setup or connection fails.
```

Agent 会自己完成安装、skill 注册、浏览器连接。之后你就可以对 Agent 说：
- 「把这个视频上传到 YouTube」
- 「把这三款笔记本电脑的规格做成对比表」
- 「用我的简历填写这份工作申请」

Agent 会通过 browser-harness 控制你的真实 Chrome，使用你已经登录的 session（不需要再输 cookie 或账号密码）。

---

## 四、本地 Chrome vs 云端浏览器

默认模式是连接本地 Chrome，使用用户已登录的 session。适合：

- 一次性任务（填表、信息查询、文件上传）
- 需要访问本人账号（不适合用无头浏览器重新登录）

对于需要并行运行多个任务、或访问会触发反爬的网站，browser-harness 接入 Browser Use Cloud，每个任务一个隔离的 Chrome 实例，带 stealth 配置和代理轮换：

```python
# 启动云端浏览器
start_remote_daemon("task-1")
BU_NAME=task-1 browser-harness <<'PY'
new_tab("https://example.com")
PY
# 任务完成后
stop_remote_daemon("task-1")
```

---

## 五、操作原语：AX Tree 优先于坐标

browser-harness 内置的操作原语强调 accessibility tree 而不是截图坐标：

```python
# 获取页面可访问性树（结构化，不依赖截图）
cdp("Accessibility.getFullAXTree")["nodes"]

# 从 AX node 的 backendDOMNodeId 计算 viewport 坐标
q = cdp("DOM.getBoxModel", backendNodeId=n)["model"]["content"]
x, y = sum(q[0::2])/4, sum(q[1::2])/4
click_at_xy(x, y)

# 等待导航完成
wait_for_load()

# JavaScript 执行（DOM inspection、提取数据）
js("document.querySelector('#result').textContent")
```

这种设计的好处：AX tree 是结构化的语义数据，比截图更准确，不受 DPI 和渲染时序影响，也不需要视觉模型来理解 UI 布局。

---

## 六、对比 browser-use Python 库

browser-harness 和 browser-use（Python 库）是同一家公司的两条产品线，定位不同：

| | browser-harness | browser-use (Python 库) |
|--|-----------------|------------------------|
| **使用方式** | Agent 的工具插件（通过 CLI 调用） | 在你的 Python 代码里调用 |
| **模型绑定** | 无，给任意 Agent 用 | 可以用任意 LLM |
| **session** | 用户已登录的真实 Chrome | 通常是 headless 新 session |
| **定位** | 一次性任务 / 用户账号场景 | 批量自动化 / 规模化场景 |
| **代码量** | ~1000 行 | 完整框架 |

**选择规则**：给 Claude Code 这类 Agent 做一次性任务 → browser-harness。写批量自动化代码 → browser-use Python 库。

---

## 七、为什么值得关注

**「自我进化」的工具**。agent_helpers.py 和 domain-skills 是持久化学习的具象——每次运行都在积累。如果你用 Claude Code 做了几十次浏览器任务，这个积累会越来越有价值。

**最小的中间层**。直接 CDP，不经过额外抽象层。这意味着 Chrome 能做的，你基本都能做到。

**真实 session**。对于需要用本人登录状态的任务（公司内部系统、个人账号操作），这是最干净的方式，不需要导出和导入 cookie。

**生态位清晰**。它不想替代 Python 自动化脚本，也不想成为独立 Agent——它是「给已有 Agent 添加浏览器手臂」的工具，这个定位是准确的。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## browser-harness: A Browser Agent Tool That Writes Its Own Code — Getting Smarter With Every Run

*by Mycelium Protocol*

---

GitHub: https://github.com/browser-use/browser-harness  
Core: ~1,000 lines (4 core files)  
Related: browser-use/browser-use (Python library, ~1M monthly downloads)

---

"You will never use the browser again." That's how the browser-harness README opens.

The context: this tool isn't just "AI that operates a browser" — it turns the AI into the accumulator of your browser capabilities. Every time it figures something out, it writes that down. Next time, it uses what it learned.

---

### Architecture: One WebSocket, No Middle Layer

browser-harness connects directly to a running Chrome instance via the Chrome DevTools Protocol (CDP) — no Selenium WebDriver, no Playwright Python wrapper. One WebSocket all the way through.

```
Agent (Claude Code / Codex / Cursor)
      ↓ browser-harness commands
browser-harness daemon
      ↓ WebSocket (CDP)
Chrome / Chromium
```

Four core files. ~1,000 lines total:
- `install.md` — first-time install and browser bootstrap
- `SKILL.md` — day-to-day usage
- `src/browser_harness/` — protected core package
- `agent-workspace/agent_helpers.py` — **the agent can edit this**
- `agent-workspace/domain-skills/` — **agent-generated site skills**

---

### Self-Healing: The Agent Writes What's Missing

This is the most unusual design choice:

```
Agent tries to upload a file
      ↓
No upload_file() helper in agent_helpers.py
      ↓
Agent writes upload_file() during execution
      ↓
File uploaded successfully
      ↓
upload_file() saved to agent_helpers.py for next time
```

Every run can extend `agent_helpers.py`. This is genuine "learning by doing" — not few-shot prompting, but persistent code accumulation.

**Domain skills** take this further: site-specific SOPs for LinkedIn, GitHub, Amazon, etc., stored as files in `domain-skills/<site>/`. Once the agent figures out how to send a LinkedIn DM correctly, it writes a domain skill. Future tasks of the same type skip the re-discovery.

---

### As a Browser Capability Plugin for Agents

browser-harness is not a standalone agent — it's a "browser arm" you give to Claude Code, Codex, Cursor, or any other agent by pasting a setup prompt. After setup, you tell your agent:

- "Upload this video to YouTube"
- "Compare these three laptops and give me a table with prices"
- "Fill in this job application with my resume"

The agent controls your real Chrome, using your already-logged-in session — no cookie exports, no re-authentication.

---

### Primitives: Accessibility Tree Over Coordinates

The built-in primitives favor the accessibility tree over screenshot-based coordinates:

```python
# Get structured semantic tree (not screenshot-dependent)
cdp("Accessibility.getFullAXTree")["nodes"]

# Calculate viewport coordinates from AX node
q = cdp("DOM.getBoxModel", backendNodeId=n)["model"]["content"]
x, y = sum(q[0::2])/4, sum(q[1::2])/4
click_at_xy(x, y)

# JavaScript for DOM inspection / data extraction
js("document.querySelector('#result').textContent")
```

AX tree is structured semantic data — more reliable than screenshot parsing, DPI-independent, and not subject to rendering timing.

---

### Why It Matters

**Self-evolving tooling.** `agent_helpers.py` and domain skills are persistent learning artifacts. After dozens of browser tasks, this accumulation becomes genuinely valuable.

**Minimal indirection.** Direct CDP means: if Chrome can do it, you can do it.

**Real session.** For tasks requiring your own login state (internal systems, personal accounts), this is the cleanest approach — no cookie import/export.

**Clear positioning.** It's not trying to replace Python automation scripts or become a standalone agent. It's "a browser arm for agents that already exist" — and that's exactly right.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
