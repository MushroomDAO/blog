---
title: "jev-ultrafast：browser-use × TypeSafe Jev，DOM 结构化状态代替截图，Google Flights 7.1 秒"
titleEn: "jev-ultrafast: browser-use × TypeSafe Jev, Structured DOM State Replaces Screenshots, Google Flights in 7.1s"
description: "browser-use/jev-ultrafast，19K+ stars，Python，browser-use 官方出品。核心思路：把浏览器状态变成编号元素表格，用 TypeSafe Jev 一次请求同时决策「操作类型 + 目标元素」，只有需要输入文字时才调小 LLM。默认 Agent 循环零截图，browser protocol 调用从 1092 次降到 101 次，任务时间中位数从 9.45s 降到 7.09s（-25%）。附完整安装步骤和架构拆解。"
descriptionEn: "browser-use/jev-ultrafast, 19K+ stars, Python, official browser-use release. Core idea: convert browser state into a numbered element table, use TypeSafe Jev to decide operation + target in one network request, only call a small LLM when TYPE_TEXT is needed. No screenshots in the default agent loop. Browser protocol calls drop from 1,092 to 101; median task time drops from 9.45s to 7.09s (−25%). Full setup steps and architecture breakdown included."
pubDate: 2026-09-24
heroImage: "../../assets/images/browser-use-jev-ultrafast-dom-web-agent-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "browser-agent", "jev", "browser-use", "web-automation", "local-ai", "dom", "python"]
lang: zh-CN
---

`browser-use/jev-ultrafast`，Python，19,338 stars，browser-use 官方与 TypeSafe 合作项目。创建于 2026-09-16，8天破 1.9 万星。核心主张：用结构化 DOM 状态代替截图，用 Jev 的 System-1 决策把「操作 + 目标」压进一次网络请求，让浏览器 Agent 快 25%、协议调用降 91%。

**GitHub**：github.com/browser-use/jev-ultrafast

---

## 核心问题：为什么现有浏览器 Agent 慢

传统 browser agent 的瓶颈在两个地方：

1. **截图 → 视觉模型**：每一步截一张图，传给多模态 LLM 分析，这是大量 token 和网络时间
2. **多轮决策**：「我要点哪里」是一个请求，「我要点什么元素」是另一个请求，串行

jev-ultrafast 同时解决这两个问题。

---

## 技术架构：一次请求，两个决策

**步骤一：DOM 快照 → 编号元素表**

不截图，直接读 DOM。页面上所有可交互控件被提取成一个结构化表格：

```
[1] button    Change ticket type · Round trip
[2] combobox  Where from?        · San Francisco
[3] combobox  Where to?          · empty
[4] textbox   Departure          · empty
[5] button    Search             ·
...
```

每个元素有：索引编号、控件类型、标签名称、当前值。只包含可见控件，不塞页脚和隐藏内容。

**步骤二：Jev 一次请求，两个头同时输出**

Jev 的「投机扇出（speculative fan-out）」模式：同一次观察状态下，`operation` head 和 `target` head 并行推理，共享相同输入，**一个网络往返完成两个决策**：

```
page → element table
         │
    TypeSafe Jev (单次请求)
    ├── operation head → CLICK / TYPE_TEXT / SELECT / SCROLL / WAIT / DONE / BLOCKED
    ├── click_target head → [7]
    └── type_text_target head → [3]
         │
    如果 operation = TYPE_TEXT：
         └── 小 LLM → 生成文字 → browser
    否则直接执行
```

`click_target` 和 `type_text_target` 是投机性的——如果 operation 是 `CLICK`，只有 `click_target` 执行，另一个丢弃。代价是一次额外的推理，但省掉了一次完整的网络往返。

**步骤三：只在 TYPE_TEXT 时调小 LLM**

文字生成是唯一需要自由生成的操作。jev-ultrafast 只在这一步调 LLM（示例配置用 `inception/mercury-2.5`，推理关闭），其他操作完全靠 Jev 的 System-1 决策，不走 LLM。

---

## 性能数据

实测基准：Google Flights 搜索苏黎世→伦敦，单程成人经济舱。

| 指标 | 旧版本 | jev-ultrafast | 变化 |
|------|-------|--------------|------|
| **任务时间（中位数）** | 9.450s | 7.092s | **-25%** |
| **browser protocol 调用** | 1,092 次 | 101 次 | **-91%** |
| **通过率** | 3/3 | 3/3 | 持平 |

Demo 视频中的任务（含模型调用 + 文字生成 + 浏览器操作 + 等待加载）：**7,073ms**。

另两个任务的独立实测：
- 维基百科打开 Gödel 不完全定理词条：**2.798s**
- 本地酒店搜索/筛选：**1.896s**

**数据诚信声明**：README 说了这是 3 次交替运行的同一任务，不是通用可靠性基准。

---

## 安装与使用

**环境要求：**
- Python（建议 3.11+）
- `uv`（安装管理工具）
- Chrome（通过 Browser Harness 连接）
- TYPESAFE_API_KEY（TypeSafe Jev API）
- TEXT_MODEL_API_KEY（OpenRouter 或兼容 API，用于文字生成）

**快速开始：**

```bash
git clone https://github.com/browser-use/jev-ultrafast.git
cd jev-ultrafast
uv sync
cp .env.example .env
# 在 .env 里填写 TYPESAFE_API_KEY 和 TEXT_MODEL_API_KEY
uv run jev
```

打开 http://127.0.0.1:8766，点 **Start demo → Run automatically**。Inspector 实时显示编号元素、操作概率、目标概率和已执行动作。**Choose next** 模式可以逐步暂停确认。

**库调用方式：**

```python
from jev_ultrafast import Agent

with Agent(
    "https://www.google.com/travel/flights?hl=en",
    "Find one-way flights from Zurich to London on September 20, 2026, "
    "for one adult in economy. Stop when matching flight options are visible.",
) as agent:
    for state in agent.run():
        print(state["elapsed_ms"], state["status"])
```

**文字模型替换：**

`.env` 示例用 OpenRouter，也支持 Gemini、GLM、DeepSeek（OpenAI 兼容接口），在配置里指定模型名、endpoint 和 reasoning 开关即可。

---

## 代码结构（小到可以直接读完）

| 文件 | 职责 |
|------|------|
| `agent.py` | 完整 Agent 循环和文字生成交接逻辑 |
| `snapshot.js` | 原子 DOM 快照、控件索引、页面新鲜度检查 |
| `browser.py` | 浏览器连接、当前布局、执行层 |
| `model.py` | Jev 动态 operation/target head + 文字生成 |
| `questions.py` | 模型 prompt 指令 |
| `demo.py` | 本地 Inspector UI |

核心代码极少，README 说「Small enough to read」——agent.py 就是完整 Agent 循环，没有隐藏的框架胶水。

---

## 设计亮点和边界

**设计亮点：**

- 不用截图 → 不需要视觉模型 → 省掉大量 token 和延迟
- 投机扇出把两个决策压进一次请求
- 模型输出永远不会变成 selector、坐标、shell 命令或可执行 JS——输出只是索引编号，执行器从实际 DOM 节点解析
- 文字输入前会校验整个 text-helper 输入未变（防止过时请求）

**当前 MVP 边界（README 自己写清楚的）：**

- Shadow DOM、iframe、canvas、文件上传、弹出标签页、嵌套滚动、任意键盘组件暂不支持
- `DONE` 判断仍需独立验证，不能完全信任模型
- 共享现有 Chrome Profile（不隔离登录态）

---

## 怎么看这个项目

browser-use 是浏览器 Agent 领域的头部开源项目。jev-ultrafast 是 browser-use 和 TypeSafe 合作把 System-1 决策用到浏览器 Agent 里的实验——用 Jev 替代掉截图+全量 LLM 那一层。

技术路线是干净的：DOM 结构化状态本来就比截图更精确，Jev 的一次请求双头输出也是合理的工程优化。91% 的 browser protocol 调用削减才是真正的性能提升来源，25% 的时间节省是在此基础上的结果。

值得关注的是 Cloud waitlist——README 顶部提示「Browser Use Cloud waitlist is open」，说明 browser-use 在推进云端托管版。jev-ultrafast 更像是给 TypeSafe Jev 生态做演示兼测试这个技术路线，不只是一个独立工具。

> 开源仅供学习研究参考。使用需自备 TypeSafe API key 和文字模型 API key。

---

<!--EN-->

## jev-ultrafast: Structured DOM State Replaces Screenshots, Browser Agent in 7.1s

`browser-use/jev-ultrafast` — Python, 19,338 stars, official browser-use × TypeSafe collaboration (created 2026-09-16). Core idea: replace screenshot→vision-model with a numbered element table, use TypeSafe Jev to decide operation + target in one network round trip, only call a small LLM for TYPE_TEXT.

**GitHub**: github.com/browser-use/jev-ultrafast

---

### Architecture

**DOM snapshot → Numbered element table**

Instead of screenshots, the agent reads all interactive controls into a structured table: index, control type, label, current value. Only visible controls included.

```
[1] button    Change ticket type · Round trip
[2] combobox  Where from?        · San Francisco
[3] combobox  Where to?          · empty
```

**TypeSafe Jev speculative fan-out — one request, two decisions**

```
element table → Jev (single request)
├── operation head → CLICK / TYPE_TEXT / SELECT / SCROLL / WAIT / DONE / BLOCKED
├── click_target head → [7]
└── type_text_target head → [3]
         │
    if operation = TYPE_TEXT → small LLM → generate text → browser
    otherwise → execute directly
```

Both target heads are speculative and share the same observed state. One network round trip covers what previously took two.

**Small LLM only for TYPE_TEXT**

Text generation is the only free-form step. All other decisions are pure Jev System-1, no LLM needed.

---

### Performance

Google Flights: Zürich → London, one-way, one adult, economy.

| Metric | Previous | jev-ultrafast | Change |
|--------|---------|--------------|--------|
| Task time (median) | 9.450s | 7.092s | **−25%** |
| Browser protocol calls | 1,092 | 101 | **−91%** |
| Pass rate | 3/3 | 3/3 | Same |

Demo run time (including model calls, text gen, browser work, load waits): **7,073ms**.

Additional tasks: Wikipedia article open: **2.798s**; local hotel search/filter: **1.896s**.

*Note: 3 alternating runs of one task; not a general reliability benchmark.*

---

### Setup

Requirements: Python (3.11+ recommended), `uv`, Chrome, TYPESAFE_API_KEY, TEXT_MODEL_API_KEY (OpenRouter or compatible).

```bash
git clone https://github.com/browser-use/jev-ultrafast.git && cd jev-ultrafast
uv sync
cp .env.example .env  # fill TYPESAFE_API_KEY and TEXT_MODEL_API_KEY
uv run jev
```

Open http://127.0.0.1:8766 → Start demo → Run automatically. Inspector shows numbered elements, operation probabilities, target probabilities, and executed actions.

Library usage:
```python
from jev_ultrafast import Agent

with Agent("https://www.google.com/travel/flights?hl=en",
           "Find one-way flights from Zurich to London on Sep 20 2026, 1 adult economy.") as agent:
    for state in agent.run():
        print(state["elapsed_ms"], state["status"])
```

Text model: OpenRouter in the example; also supports Gemini, GLM, DeepSeek (OpenAI-compatible endpoint).

---

### Design Highlights and Limits

**Highlights:**
- No screenshots → no vision model → saves tokens and latency
- Speculative fan-out compresses two decisions into one request
- Model output never becomes selectors, coordinates, shell commands, or executable JS — only index numbers resolved from actual DOM nodes
- Stale-page retry reuses text-helper output only if the entire input is unchanged

**Current MVP limits (from README):**
- Shadow DOM, iframes, canvas, file uploads, pop-up tabs, nested scrolling, custom keyboard widgets: not yet supported
- DONE judgment still requires independent verification
- Shares the existing Chrome profile (no login state isolation)

---

### Assessment

browser-use is a leading open-source browser agent framework. jev-ultrafast is their collaboration with TypeSafe — applying System-1 decision-making to eliminate the screenshot + full LLM layer. The architecture is clean: structured DOM state is inherently more precise than screenshots; Jev's dual-head single-request is sound engineering. The 91% reduction in browser protocol calls is the real performance driver; the 25% task time improvement follows from that. The Cloud waitlist hint at the top of README signals this is also a testing ground for browser-use's managed cloud offering.

> For learning and research reference only. Requires TypeSafe API key and text model API key.
