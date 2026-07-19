---
title: "CopilotKit：Agent 和用户之间那层你必须亲手搭的桥，36k stars，AG-UI 协议缔造者"
titleEn: "CopilotKit: The Bridge Between Agent and User You'd Otherwise Build Yourself — 36k Stars, Makers of AG-UI Protocol"
description: "CopilotKit 是 Agent 应用的前端基础设施：AG-UI 协议统一 Agent 后端与 UI 通信，共享状态层让 Agent 状态实时驱动 React 渲染，Generative UI 让 Agent 直接在聊天流里渲染组件，HITL 让 Agent 在关键节点暂停等用户决策后恢复。支持 LangGraph、Claude SDK、CrewAI 等 15+ 后端框架，React/Angular/Vue/React Native 多平台。36k stars。"
descriptionEn: "CopilotKit is the frontend infrastructure for agent apps: AG-UI protocol unifies agent backend and UI communication, shared state lets agent state reactively drive React rendering, Generative UI lets agents render components directly in the chat stream, and HITL pauses agent execution at decision points until the user responds. Supports 15+ backends (LangGraph, Claude SDK, CrewAI, etc.), React/Angular/Vue/React Native. 36k stars."
pubDate: "2026-07-19"
updatedDate: "2026-07-19"
category: "Tech-Experiment"
tags: ["AI Agent", "前端框架", "React", "HITL", "Generative UI", "AG-UI", "LangGraph", "开源"]
heroImage: "../../assets/images/copilotkit-frontend-stack-agents-guide-banner.jpg"
---

> **GitHub**：[CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) · ⭐ 36,147  
> **文档**：[docs.copilotkit.ai](https://docs.copilotkit.ai/) · **协议**：[AG-UI Protocol](https://ag-ui.com/)  
> **定位**：Agent 应用的前端基础设施栈（Frontend Stack for Agents & Generative UI）

---

## 一个你必然会遇到的问题

你有了一个 Agent——用 LangGraph 写的、或者 Claude SDK、或者 CrewAI。它能思考、能规划、能调用工具、能完成复杂任务。

然后你开始想：**怎么给用户用？**

这个问题比想象的复杂得多。你需要：

- 一个聊天界面，能显示流式输出、工具调用过程、Agent 的中间状态
- 让 Agent 的状态实时反映在 UI 里（比如 Agent 正在修改一个文档，文档页面要同步更新）
- 在关键节点**暂停 Agent**，等用户确认或输入，然后把答案带回去让 Agent 继续
- 让 Agent 能在聊天流里直接渲染 React 组件（不是文字描述，是真实的交互组件）
- 这一切要在你的 React、Angular、Vue、React Native 项目里开箱可用

如果你自己做这些，你在重新发明一套前端 Agent 基础设施。而这正是 CopilotKit 已经做好的事。

---

## 先说清楚它解决的核心问题

用户和 Agent 的交互过程，本质上是一个**双向实时通信问题**，但它比普通 WebSocket 通信复杂得多：

```
用户 ←→ UI 组件 ←→ 协议层 ←→ Agent 后端
         ↕                      ↕
      React 状态          Agent 内部状态
```

这个图里有几个很难处理的地方：

**1. 协议不标准**：每个 Agent 框架（LangGraph、CrewAI、Claude SDK）的通信格式不一样，写一套 UI 只能绑定一个后端。

**2. 状态不同步**：Agent 的内部状态（比如它维护的任务列表、当前进度）和前端 React 状态是完全隔离的两套东西。

**3. 渲染不灵活**：Agent 只能输出文字，它无法直接说「我要在聊天流里渲染一个日历选择器」。

**4. 交互不可中断**：Agent 一旦开始运行，用户只能等它跑完。但真实任务经常需要在中间问用户「这两个方案选哪个？」。

CopilotKit 把这四个问题分别做了抽象，把每一层都变成可插拔的 SDK 原语。

---

## 架构：四层抽象

### 第一层：AG-UI 协议——统一后端连接

AG-UI 是 CopilotKit 团队制定的**开放协议**，定义了 Agent 后端和前端之间事件流的标准格式。

已采用的框架：**Google ADK、LangChain、AWS Strands、Microsoft Agent Framework、Mastra、PydanticAI** 以及更多。

这意味着：你用 AG-UI 写一套前端，换后端框架不需要改 UI 代码。

```
你的 React 应用
      ↓  AG-UI 事件流
CopilotKit 运行时
      ↓  标准适配器
LangGraph / Claude SDK / CrewAI / Google ADK / ...（任选）
```

支持的后端框架（15+）：LangGraph（Python/TS/FastAPI）、Google ADK、AWS Strands、Mastra、Claude SDK（Python/TS）、PydanticAI、MS Agent Framework（Python/.NET）、AG2、Agno、LlamaIndex、CrewAI……

### 第二层：共享状态（Shared State）——双向实时同步

这是 CopilotKit 最核心的设计之一：**Agent 的状态和 React 的状态之间有一个双向同步通道**。

```typescript
// 前端读 Agent 状态 —— 自动响应式，Agent 更新 → 组件重渲染
function TaskBoard() {
  const { agent } = useAgent();
  const tasks = (agent.state.tasks as any[]) ?? [];

  return (
    <ul>
      {tasks.map((task, i) => (
        <li key={i}>{task.title} — {task.status}</li>
      ))}
    </ul>
  );
}

// 前端写 Agent 状态 —— Agent 可以读到这个值并做出反应
function SettingsPanel() {
  const { agent } = useAgent();
  return (
    <button onClick={() => agent.setState({ userPreferences: { theme: "dark" } })}>
      切换深色模式
    </button>
  );
}
```

**这解决了什么**：传统架构里，Agent 在后端运行，前端只能看到它最终输出的文字。有了共享状态，Agent 可以在执行过程中不断更新状态（比如「正在处理第 3/10 个文件」），前端实时反映，不需要轮询，不需要额外的 WebSocket。

### 第三层：Generative UI——Agent 渲染真实组件

不只是显示文字，Agent 可以在聊天流里直接**调用并渲染 React 组件**。

```typescript
function YourApp() {
  useComponent({
    name: "showWeather",
    description: "显示一个城市的天气卡片",
    parameters: z.object({
      city: z.string(),
      temperature: z.number(),
      condition: z.string(),
    }),
    render: WeatherCard,  // 你的 React 组件
  });
}
```

当 Agent 决定调用 `showWeather` 工具时，聊天流里出现的不是「当前上海气温 28°C」的文字，而是一个真实渲染的 `WeatherCard` 组件——用户可以和它交互。

三种 Generative UI 模式：

| 模式 | 触发方式 | 特点 |
|---|---|---|
| **Static（AG-UI Protocol）** | Agent 调用已注册的工具 | 类型安全，Zod schema 验证 |
| **Declarative（A2UI）** | Agent 描述 UI 结构 | Agent 侧控制布局 |
| **Open-Ended（MCP Apps / Open JSON）** | Agent 输出任意 JSON | 最灵活，适合动态场景 |

**多 Agent 场景**可以把组件 scope 到特定 Agent：

```typescript
useComponent({
  name: "renderProfile",
  parameters: z.object({ userId: z.string() }),
  render: ProfileCard,
  agentId: "support-agent",  // 只有这个 Agent 能触发
});
```

### 第四层：Human-in-the-Loop（HITL）——可中断的 Agent 交互

这是整个交互过程里最精妙的设计。HITL 让 Agent 在运行到关键节点时**暂停**，等用户给出答案，然后把答案折叠进 Agent 的上下文，**从暂停的地方继续**。

两种模式对应不同的暂停发起方：

**模式一：`useHumanInTheLoop`——Agent 自己决定暂停**

LLM 判断需要询问用户时，调用一个注册在前端的 HITL 工具：

```typescript
useHumanInTheLoop({
  name: "book_call",
  description: "询问用户选择一个会议时间段",
  parameters: z.object({
    topic: z.string().describe("这次会议是关于什么的"),
    attendee: z.string().describe("和谁开会"),
  }),
  render: ({ args, status, respond }) => (
    <TimePickerCard
      topic={args?.topic ?? "会议"}
      attendee={args?.attendee}
      slots={availableSlots}
      status={status}
      onSubmit={(result) => respond?.(result)}  // 用户选完，答案回传给 Agent
    />
  ),
});
```

聊天暂停 → 出现日历选择组件 → 用户选择时间 → Agent 收到「周一 9:00 AM」→ 继续执行订日历的逻辑。

**模式二：`useInterrupt`——代码路径强制暂停**

当暂停是流程图里的确定性检查点（不是 LLM 决定的），在 LangGraph 节点里调用 `interrupt()`，前端用 `useInterrupt` 处理：

```python
# LangGraph 节点（Python 后端）
def review_node(state):
    draft = generate_draft(state)
    # 到这里必须让人看一眼
    user_feedback = interrupt({"draft": draft, "message": "请检查这份草稿"})
    return apply_feedback(state, user_feedback)
```

```typescript
// 前端接住这个 interrupt
useInterrupt({
  render: ({ event, respond }) => (
    <DraftReviewCard
      draft={event.data.draft}
      message={event.data.message}
      onApprove={() => respond({ approved: true })}
      onRevise={(feedback) => respond({ approved: false, feedback })}
    />
  ),
});
```

**这解决了什么**：你再也不需要把整个 Agent 流程切成多个独立请求来实现「让用户审阅」。Agent 保持完整的上下文和状态，只是在某个点上等待人的判断。

---

## 哪些东西可以定制

CopilotKit 的设计原则是：**抽象交互机制，不锁定 UI 外观**。

**可以完全定制的部分：**

| 层 | 可定制项 |
|---|---|
| **Chat UI** | 消息气泡样式、输入框、工具调用展示、流式光标 |
| **Generative UI** | 任何 React 组件都可以注册为 Agent 工具 |
| **HITL 组件** | 暂停时显示的 UI 完全自定义（表单、日历、审批卡片……）|
| **共享状态 Schema** | Agent 状态的数据结构由你定义，任意嵌套 JSON |
| **后端框架** | 换 Agent 后端不改前端（AG-UI 适配层） |
| **运行平台** | Web、Mobile（React Native）、Slack、Microsoft Teams |
| **LLM 提供商** | OpenAI、Anthropic、Gemini 等（通过后端框架配置）|

**不可以绕过的部分：**

AG-UI 协议事件格式——这是 CopilotKit 各层能协同工作的基础，必须通过 AG-UI 适配器连接后端。（但适配器对所有主流框架都已经有了。）

---

## `useAgent` Hook：一切的入口

所有交互能力都通过 `useAgent` 收口：

```typescript
const { agent } = useAgent({ agentId: "my_agent" });

// 读状态（响应式）
const city = agent.state.city;

// 写状态（Agent 可读到）
agent.setState({ city: "Shanghai" });

// 发送消息
agent.sendMessage("帮我分析这份报告");

// 暂停/恢复
agent.interrupt();
agent.resume(response);
```

这个 hook 直接坐在 AG-UI 协议层上，给你完整的 Agent 连接控制权。

---

## 平台支持：同一个 Agent，处处可用

| 平台 | 状态 |
|---|---|
| React / Next.js | ✅ GA |
| Angular | ✅ 支持 |
| Vue | ✅ 支持 |
| React Native | ✅ 支持 |
| Slack / MS Teams | 🟡 Beta，邀请内测 |
| Discord / Google Chat | 🔜 Coming soon |

同一个 Agent 后端，通过 AG-UI，在所有平台渲染对应的 Generative UI 和 HITL 组件——不需要为每个平台维护一套对话逻辑。

---

## 快速上手

```bash
npx copilotkit@latest create
```

5 分钟内跑起来，需要一个 LLM API Key（OpenAI / Anthropic / Gemini）。

安装 Agent Skills（让 Claude Code / Cursor / Codex 自动理解 CopilotKit）：

```bash
npx copilotkit@latest skills install
```

---

## 一句话总结

CopilotKit 把「用户和 Agent 的交互过程」拆成四个可独立定制的层：AG-UI 协议统一后端连接、共享状态层双向同步 Agent 和 UI、Generative UI 让 Agent 直接渲染组件、HITL 让 Agent 在关键节点暂停等用户决策。你自己写 Agent 逻辑，CopilotKit 处理整个交互界面。

支持 LangGraph、Claude SDK、CrewAI 等 15+ 框架，覆盖 Web、Mobile、Slack、Teams。36k stars，AG-UI 协议已被 Google、AWS、Microsoft、LangChain 采用。

© 2026 Author: Mycelium Protocol

<!--EN-->

## CopilotKit: The Frontend Infrastructure for Agent-Native Applications

**GitHub**: [CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) · ⭐ 36,147  
**Docs**: [docs.copilotkit.ai](https://docs.copilotkit.ai/) · **Protocol**: [AG-UI](https://ag-ui.com/)

### The Problem It Solves

You've built an agent — with LangGraph, Claude SDK, CrewAI, or whatever backend. Now you need to put it in front of users. That means:

- A chat UI that handles streaming, tool call display, intermediate state
- Agent state that drives real-time UI updates (the agent modifies a document → the document view updates live)
- The ability to pause the agent at decision points, collect user input, and resume with the answer folded back in
- Agents that can render actual React components (not just text) directly in the chat stream
- All of this working across React, Angular, Vue, React Native — without rebuilding for each

Without CopilotKit, you're building this infrastructure yourself. That's what it takes to connect an agent to real users.

### Four Abstraction Layers

**Layer 1 — AG-UI Protocol: Unified Backend Connection**

An open event-based protocol standardizing how agents communicate with UIs. Adopted by Google ADK, LangChain, AWS Strands, Microsoft Agent Framework, Mastra, PydanticAI, and more.

Result: switch agent backends without changing UI code. One frontend, any AG-UI-compatible backend (15+ frameworks).

**Layer 2 — Shared State: Bidirectional Reactive Sync**

```typescript
const { agent } = useAgent();

// Reads agent state — reactive, auto re-renders on agent update
const tasks = (agent.state.tasks as any[]) ?? [];

// Writes state the agent can read
agent.setState({ userPreferences: { theme: "dark" } });
```

Agent state and React state stay synchronized in real time. No polling. No separate WebSocket setup.

**Layer 3 — Generative UI: Agents Render Components**

Register any React component as an agent-callable tool:

```typescript
useComponent({
  name: "showWeather",
  description: "Display a weather card for a city",
  parameters: z.object({ city: z.string(), temperature: z.number() }),
  render: WeatherCard,
});
```

When the agent calls `showWeather`, a real React component renders in the chat stream — not text describing the weather, an actual interactive `WeatherCard`. Three modes: Static (AG-UI tools), Declarative (A2UI), Open-Ended (MCP Apps / Open JSON).

**Layer 4 — Human-in-the-Loop: Interruptible Agent Execution**

Two patterns:

`useHumanInTheLoop` — the LLM decides to pause (agent-initiated): registers a client-side HITL tool; when the LLM calls it, a custom component renders; user answers; agent gets the result and continues.

`useInterrupt` — the graph enforces a checkpoint (deterministic): `interrupt()` in your LangGraph node; `useInterrupt` renders the custom UI on the frontend; user responds; agent resumes with full context intact.

The key: the agent doesn't restart. It keeps its state and context, just waits at a specific point for human input.

### What's Customizable

| Layer | Customizable |
|---|---|
| Chat UI | Message styles, input area, streaming display, tool call rendering |
| Generative UI | Any React component can be an agent tool — yours, not ours |
| HITL components | Any UI for pause points: forms, calendars, approval cards |
| State schema | Arbitrary nested JSON, your types |
| Agent backend | Any AG-UI-compatible framework |
| Platform | Web, React Native, Slack, Teams |

What's not optional: the AG-UI protocol wire format. Everything else is yours to define.

### Platform Coverage

| Platform | Status |
|---|---|
| React / Next.js | ✅ GA |
| Angular, Vue | ✅ Supported |
| React Native | ✅ Supported |
| Slack / MS Teams | 🟡 Beta |

Same agent backend. Every platform. AG-UI handles the wire protocol, CopilotKit handles the UI layer per framework.

### Quick Start

```bash
npx copilotkit@latest create
# Need an LLM API key (OpenAI / Anthropic / Gemini)
```

### Summary

CopilotKit abstracts the user-agent interaction into four independently customizable layers: AG-UI protocol for backend portability, shared state for bidirectional reactive sync, Generative UI for agent-rendered components, and HITL for interruptible execution with human decision points. You write the agent logic; CopilotKit handles the interaction surface.

15+ backend frameworks. React, Angular, Vue, React Native, Slack, Teams. AG-UI adopted by Google, AWS, Microsoft, LangChain. 36k stars.

© 2026 Author: Mycelium Protocol
