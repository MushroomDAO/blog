---
title: "PixOffice：给 AI 多智能体加一层 2D 办公室可视化，三种接入方式详解"
titleEn: "PixOffice: How to Integrate 2D Office Scene Visualization Into Your AI Agent System"
description: "workbzw/pixoffice，MIT，7 stars，TypeScript。Vite + React + Pixi.js 构建的 2D 虚拟办公室前端，设计给 AI 多智能体场景用——通过 HTTP 命令驱动角色走动、开会、发言、聚焦工作。本文是工程接入指南：介绍三条集成路径（Scene Commands v2.0 API、Legacy Actions 快速接入、Chat SDK 注入），并附完整的 Agent 任务交接场景示例。包含五个包的职责说明（contracts/runtime/renderer-pixi/animation-frame/scene-office），运行时在 Node.js 无头模式下也可工作，不依赖 React/Pixi/DOM。"
descriptionEn: "workbzw/pixoffice, MIT, 7 stars, TypeScript. A 2D virtual office frontend built with Vite + React + Pixi.js, designed for AI multi-agent scenarios — HTTP commands drive characters to walk, meet, speak, and focus. This engineering integration guide covers three integration paths (Scene Commands v2.0 API, Legacy Actions quickstart, Chat SDK injection), with a complete agent handoff scenario example. Includes package responsibility breakdown (contracts/runtime/renderer-pixi/animation-frame/scene-office); the runtime works headless in Node.js without React/Pixi/DOM."
pubDate: 2026-10-05
heroImage: "../../assets/images/pixoffice-2d-office-frontend-ai-agent-integration-guide-banner.jpg"
category: "Tech-Experiment"
tags: ["多Agent协作", "可视化", "TypeScript", "开源工具", "Agent集成", "虚拟办公室"]
lang: "zh-CN"
wechatTitle: "PixOffice：给AI多智能体加2D办公室可视化"
wechatDigest: "MIT 7星；Vite+React+Pixi.js；HTTP命令驱动角色走动；三种接入方式；可视化多Agent协作"
---

如果你在跑多个 AI Agent 协同工作，有一个问题迟早会出现：不知道谁在做什么。日志里看不清，终端里一堆 stdout，出了问题才发现两个 Agent 在同一个任务上各自推进了半小时。

PixOffice 给这个问题加了一层可视化——不是监控大屏，是一个可以通过 HTTP 命令驱动的 2D 办公室场景。你的 Agent 可以在里面走到某张桌子、开个会、说一句话、切换到专注状态。可视化只是副产品，真正的价值是：外部系统用标准 HTTP 命令就能控制场景，Agent 的状态变化有了可观测的物理位置。

GitHub: https://github.com/workbzw/pixoffice | ⭐ 7 | MIT | TypeScript

---

## 项目结构

PixOffice 用 npm workspaces 拆成五个包，接入时只需关心三个：

| 包 | 职责 | 接入时是否需要 |
|---|---|---|
| `contracts` | 共享协议类型（Zod schema）| 接 HTTP API 不需要，直接用 JSON |
| `runtime` | 核心引擎，无头 Node.js 可运行，不依赖 React/Pixi/DOM | 写自定义后端时需要 |
| `renderer-pixi` | Pixi.js 渲染宿主 | 只在前端展示时需要 |
| `animation-frame` | 帧动画播放器 | 前端渲染依赖 |
| `scene-office` | 办公场景数据和行为插件 | 前端渲染依赖 |

**对大多数 Agent 集成场景来说，你只需要跑起 PixOffice 的 dev server，然后通过 HTTP 发命令。** 不需要直接引用 npm 包（它们目前也没发布到 npm registry）。

---

## 启动本地实例

```bash
git clone https://github.com/workbzw/pixoffice.git
cd pixoffice
npm install
npm run dev
```

启动后有两个端口：
- 前端展示：`http://localhost:5173`（Vite dev server）
- Action Gateway：`http://localhost:8765`（Legacy HTTP API）

新协议 Scene Commands 的端口在 dev server 里也是 8765，通过路径区分：`/scene/commands` vs `/actions`。

---

## 三条接入路径

### 路径 1：Scene Commands v2.0（推荐）

这是当前推荐的接入方式。命令结构清晰，支持异步轮询，有协议版本标记。

**发送一条命令：**

```bash
curl -X POST http://localhost:8765/scene/commands \
  -H 'Content-Type: application/json' \
  -d '{
    "protocolVersion": "2.0",
    "sceneId": "office-1",
    "commandId": "task-handoff-001",
    "type": "activity.start",
    "capability": "office.visit",
    "participants": [
      { "entityId": "marvis", "role": "visitor" },
      { "entityId": "code-agent", "role": "host" }
    ],
    "params": {
      "stops": [
        {
          "hostId": "code-agent",
          "message": "请核对数据源，有疑问再来找我。",
          "reply": "收到"
        }
      ],
      "durationMs": 3000
    }
  }'
```

**轮询结果：**

```bash
curl http://localhost:8765/scene/commands/task-handoff-001
```

返回 `{ "status": "completed" | "pending" | "error", ... }`。

**查询当前场景状态：**

```bash
curl http://localhost:8765/scene/state
```

**发现可用能力：**

```bash
curl http://localhost:8765/scene/capabilities
```

---

### 内置能力一览

通过 `capability` 字段指定，当前内置六种：

| capability | 效果 |
|---|---|
| `office.visit` | A 走到 B 的桌子，交换一句话后返回 |
| `office.meeting` | 多人集中到会议室，支持轮流发言 |
| `office.focus` | 角色切换到专注状态（视觉上不被打扰） |
| `scene.move` | 角色移动到指定坐标 |
| `scene.say` | 角色发出一段话（气泡或旁白） |
| `office.emote` | 触发表情动作（点头、摇头、鼓掌等） |

坐标系是整数网格，场景中每个桌子/房间有固定的 `entityId`，通过 `scene.capabilities` 接口可以枚举所有实体和它们支持的能力。

---

### 路径 2：Legacy Actions API（快速上手）

如果只是快速验证可行性，Legacy API 更简单——参数少，语义直白：

```bash
# Agent A 走到 Agent B 的桌子
curl -X POST http://localhost:8765/actions \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "desk_visit",
    "visitor": 1,
    "host": 5,
    "message": "这件事交给你了。"
  }'

# Agent 移动到指定格子
curl -X POST http://localhost:8765/actions \
  -d '{ "type": "move", "entityId": "agent-3", "x": 12, "y": 8 }'

# Agent 发言
curl -X POST http://localhost:8765/actions \
  -d '{ "type": "say", "entityId": "agent-2", "text": "代码审查完成。" }'

# 更新对象状态
curl -X POST http://localhost:8765/actions \
  -d '{ "type": "set_state", "entityId": "task-board", "state": "active" }'
```

Legacy API 是同步的，没有 commandId 和轮询，适合原型阶段。

---

### 路径 3：Chat SDK 注入（给 React 前端用）

如果你有自己的 React 前端需要嵌入 PixOffice，可以通过 `chatSource` prop 注入对话流：

**1. 设置环境变量：**

```env
VITE_PIXOFFICE_CHAT_URL=https://your-agent-endpoint.com/v1/chat
```

**2. 或者直接注入 SDK（更灵活）：**

```tsx
import { OfficeApp } from '@pixoffice/renderer-pixi'

function App() {
  return (
    <OfficeApp
      dataSource={{
        kind: 'static',
        sceneId: 'office-1'
      }}
      chatSource={{
        kind: 'my-agent',
        async *stream(request, signal) {
          const resp = await fetch('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
              version: '1.0',
              conversationId: request.conversationId,
              messages: request.messages
            }),
            signal
          })

          const reader = resp.body.getReader()
          const decoder = new TextDecoder()

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            for (const line of decoder.decode(value).split('\n')) {
              if (!line.trim()) continue
              const event = JSON.parse(line)  // NDJSON

              if (event.type === 'delta') yield event.content
              if (event.type === 'done') return
              if (event.type === 'error') throw new Error(event.message)
            }
          }
        }
      }}
    />
  )
}
```

Chat endpoint 需要返回 NDJSON 流，每行一个 JSON 对象，`type` 字段为 `status` / `delta` / `done` / `error`。

---

## 实战：多 Agent 任务交接可视化

下面是一个完整的工程示例——让三个 Agent（Planner、Coder、Reviewer）的任务交接在 PixOffice 里可见。

```typescript
const OFFICE_URL = 'http://localhost:8765'

async function sendCommand(command: object) {
  const res = await fetch(`${OFFICE_URL}/scene/commands`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocolVersion: '2.0',
      sceneId: 'office-1',
      ...command
    })
  })
  const { commandId } = await res.json()

  // 轮询等待完成
  while (true) {
    await new Promise(r => setTimeout(r, 500))
    const poll = await fetch(`${OFFICE_URL}/scene/commands/${commandId}`)
    const result = await poll.json()
    if (result.status !== 'pending') return result
  }
}

// Planner 走到 Coder 桌子交代任务
await sendCommand({
  commandId: `plan-to-code-${Date.now()}`,
  type: 'activity.start',
  capability: 'office.visit',
  participants: [
    { entityId: 'planner', role: 'visitor' },
    { entityId: 'coder', role: 'host' }
  ],
  params: {
    stops: [{ hostId: 'coder', message: '需求文档在 /tasks/auth.md，请实现登录逻辑。', reply: '好的' }],
    durationMs: 4000
  }
})

// Coder 切换到专注状态
await sendCommand({
  commandId: `coder-focus-${Date.now()}`,
  type: 'activity.start',
  capability: 'office.focus',
  participants: [{ entityId: 'coder', role: 'worker' }],
  params: { durationMs: 30000 }
})

// 实际执行编码任务...
// await runCodingAgent('coder', '/tasks/auth.md')

// Coder 走到 Reviewer 桌子提交审查
await sendCommand({
  commandId: `code-to-review-${Date.now()}`,
  type: 'activity.start',
  capability: 'office.visit',
  participants: [
    { entityId: 'coder', role: 'visitor' },
    { entityId: 'reviewer', role: 'host' }
  ],
  params: {
    stops: [{ hostId: 'reviewer', message: 'PR #42 已提交，请审查。', reply: '马上看' }],
    durationMs: 3000
  }
})
```

这段代码跑起来之后，PixOffice 界面里你能看到角色移动、停下来交换消息、然后切换工作状态——多 Agent 工作流的进展有了物理映射。

---

## 数据源接入（Dashboard 集成）

PixOffice 支持接入外部业务数据源，通过 `VITE_OFFICE_DASHBOARD_URL` 环境变量配置：

```env
VITE_OFFICE_DASHBOARD_URL=http://localhost:9000/dashboard
```

Dashboard endpoint 需要返回场景实体的当前状态快照：

```json
{
  "entities": [
    { "id": "agent-1", "name": "Planner", "status": "idle", "workload": 0.3 },
    { "id": "agent-2", "name": "Coder", "status": "working", "workload": 0.9 },
    { "id": "agent-3", "name": "Reviewer", "status": "available", "workload": 0.1 }
  ],
  "tasks": [
    { "id": "task-42", "assignedTo": "agent-2", "priority": "high" }
  ]
}
```

场景会根据这份数据初始化角色状态；HTTP 命令可以在此基础上叠加动态行为。

---

## 接入注意事项

**命令 ID 唯一性**：每条 Scene Command 的 `commandId` 必须唯一，建议用 `${type}-${Date.now()}-${uuid}` 格式。重复 ID 会导致轮询结果混淆。

**场景 ID 一致性**：`sceneId` 在整个 session 里保持一致，不同 `sceneId` 的命令互不干扰但也不共享状态。

**实体 ID 先发现再用**：调用任何命令前先 `GET /scene/capabilities`，确认目标 `entityId` 存在。硬编码实体 ID 在场景数据更新后会静默失败。

**早期项目**：PixOffice 目前 7 颗星，创建于 2026-09-30，API 字段和路由随时可能变化。建议在集成层封装一个薄适配器，把 `protocolVersion` 和端点路径集中管理，减少升级时的改动面。

---

> MIT 开源。五个 npm workspace 包目前未发布到 registry，需从源码引用。开源仅供学习参考。

---

<!--EN-->

## PixOffice: Engineering Integration Guide for AI Multi-Agent Visualization

When multiple AI agents are running in parallel, the question isn't whether they're working — it's whether you can tell what they're doing. Logs are noisy, stdout is a wall of text, and by the time you notice a collision, two agents have been pushing the same task in different directions for an hour.

PixOffice adds a visualization layer: a 2D virtual office scene that you control via HTTP commands. Your agents can walk to a desk, hold a meeting, say something, switch to a focus state. The visual output is a side effect — the actual value is that external systems can drive scene state through standard HTTP, making agent status transitions physically observable.

GitHub: https://github.com/workbzw/pixoffice | ⭐ 7 | MIT | TypeScript

---

### Package Structure

PixOffice uses npm workspaces with five packages. For most integration scenarios, you only need to run the dev server and speak HTTP:

| Package | Responsibility | Needed for HTTP integration? |
|---------|---------------|-------------------------------|
| `contracts` | Shared protocol types (Zod schemas) | No — just send JSON |
| `runtime` | Core engine, works headless in Node.js (no React/Pixi/DOM) | Only if building a custom backend |
| `renderer-pixi` | Pixi.js rendering host | Only for visual display |
| `animation-frame` | Frame animation player | Frontend dependency |
| `scene-office` | Office scene data and behavior plugins | Frontend dependency |

---

### Starting a Local Instance

```bash
git clone https://github.com/workbzw/pixoffice.git
cd pixoffice && npm install && npm run dev
```

Two ports after startup:
- Frontend display: `http://localhost:5173` (Vite dev server)
- Action Gateway: `http://localhost:8765` (HTTP API)

---

### Integration Path 1: Scene Commands v2.0 (Recommended)

```bash
curl -X POST http://localhost:8765/scene/commands \
  -H 'Content-Type: application/json' \
  -d '{
    "protocolVersion": "2.0",
    "sceneId": "office-1",
    "commandId": "task-handoff-001",
    "type": "activity.start",
    "capability": "office.visit",
    "participants": [
      { "entityId": "marvis", "role": "visitor" },
      { "entityId": "code-agent", "role": "host" }
    ],
    "params": {
      "stops": [{ "hostId": "code-agent", "message": "Review this PR when you get a chance.", "reply": "On it" }],
      "durationMs": 3000
    }
  }'
```

Poll for result: `GET /scene/commands/{commandId}`

Built-in capabilities: `office.visit`, `office.meeting`, `office.focus`, `scene.move`, `scene.say`, `office.emote`

Discover all entities and capabilities: `GET /scene/capabilities`

---

### Integration Path 2: Legacy Actions API (Quick Start)

```bash
# Walk agent to a desk
curl -X POST http://localhost:8765/actions \
  -d '{"type":"desk_visit","visitor":1,"host":5,"message":"Task assigned."}'

# Move to grid position
curl -X POST http://localhost:8765/actions \
  -d '{"type":"move","entityId":"agent-3","x":12,"y":8}'

# Speak
curl -X POST http://localhost:8765/actions \
  -d '{"type":"say","entityId":"agent-2","text":"Code review done."}'
```

Synchronous — no commandId or polling. Good for prototyping.

---

### Integration Path 3: Chat SDK Injection

Set `VITE_PIXOFFICE_CHAT_URL` to point at your agent's streaming endpoint, or inject directly via the `chatSource` prop on `<OfficeApp>`.

Your endpoint returns NDJSON — one JSON object per line with `type: "delta" | "done" | "error"`.

---

### End-to-End Example: Multi-Agent Task Handoff

```typescript
async function agentHandoff(from: string, to: string, message: string) {
  const res = await fetch('http://localhost:8765/scene/commands', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      protocolVersion: '2.0', sceneId: 'office-1',
      commandId: `handoff-${Date.now()}`,
      type: 'activity.start', capability: 'office.visit',
      participants: [
        { entityId: from, role: 'visitor' },
        { entityId: to, role: 'host' }
      ],
      params: { stops: [{ hostId: to, message, reply: 'Got it' }], durationMs: 3000 }
    })
  })
  return res.json()
}

// Planner → Coder
await agentHandoff('planner', 'coder', 'Implement /tasks/auth.md')

// Coder works, then → Reviewer
await agentHandoff('coder', 'reviewer', 'PR #42 ready for review')
```

---

### Integration Notes

- **commandId uniqueness**: Use `${type}-${Date.now()}-${uuid}`. Duplicate IDs cause polling mismatches.
- **Entity IDs**: Always call `GET /scene/capabilities` before sending commands; hardcoded entity IDs fail silently when scene data changes.
- **Early-stage project**: 7 stars, created 2026-09-30 — API shape may change. Wrap integration in a thin adapter that centralizes `protocolVersion` and endpoint paths.

---

> MIT license. The five npm workspace packages are not published to the registry — reference from source. For technical reference only.
