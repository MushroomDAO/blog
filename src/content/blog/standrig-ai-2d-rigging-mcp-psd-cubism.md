---
title: 'StandRig：AI 直接当 rigger，MCP 原生的 2D 角色建模系统'
titleEn: "StandRig: AI as the Rigger — MCP-Native 2D Character Modeling Without the Tedium"
description: "开发者预览版开源工具：把分层 PSD 喂给本地服务，Claude Code 等 AI 通过 MCP 直接编辑 Mesh、Deformer 和参数，配套 cubism-api-bridge 打通 Live2D Cubism Editor。AI 不再是辅助，而是替代了传统 rigging 的手工部分。"
descriptionEn: "Open-source developer preview: feed a layered PSD to a local service, let Claude Code or any MCP client edit meshes, deformers, and parameters directly. With cubism-api-bridge, it also talks to Live2D Cubism Editor. AI isn't assisting the rigger — it is the rigger."
pubDate: "2026-09-11"
updatedDate: "2026-09-11"
category: "Tech-News"
tags: ["AI-agent", "MCP", "Live2D", "VTuber", "2D-rigging", "open-source"]
heroImage: "../../assets/banner-human-ai-coexistence.jpg"
---

> 📌 开源仓库：StandRig（AI 可编辑 2D 建模核心）
> GitHub：https://github.com/sayaka-aiart/StandRig
> 配套编辑器桥接：https://github.com/sayaka-aiart/cubism-api-bridge
> 作者：sayaka-aiart（开发者预览版 0.2.0，Apache 2.0 / MIT）

---

**BLUF**：StandRig 是一个把分层 PSD 转化为可被 AI 直接操作的 2D 角色模型的本地服务。通过 MCP 协议，Claude Code 这类 AI 客户端可以编辑 Mesh、Deformer、Key Form，实时查看结果——不需要人坐在 Live2D 编辑器里逐点拖拽。配套的 cubism-api-bridge 进一步打通了 Live2D Cubism Editor 的官方 External API。

---

## Rigging 的时间消耗去哪了

传统 2D VTuber 模型的 rigging 流程大致是：
1. 画师出图，分好图层（几十到上百层）
2. Rigger 在 Live2D Cubism 里逐层打点、建 Mesh
3. 设置 Deformer（变形器）的父子层级
4. 一个参数一个参数地设 Key Form（关键形态）
5. 反复测试、细调

整个过程极度精细、高度重复，且需要大量"眼睛看着调"的判断。熟练 rigger 做一个中等复杂度的模型要 40-80 小时。

这正是 AI 最擅长的工作类型：**有明确约束、大量重复操作、需要快速迭代验证**。

---

## StandRig 的做法

StandRig 把整个流程拆成两部分：**建模核心（本地服务）** 和 **AI 接口（MCP）**。

**本地服务**（`http://127.0.0.1:5180`）：
- 读取分层 PSD，解析图层位置、层级、透明度
- 维护模型状态（Mesh、Deformer、参数、Key Form）
- 提供浏览器 UI 预览和参数滑块
- 管理 Checkpoint 和 Bundle 导出

**MCP 接口**（AI 的操作端）：
- AI 读取 `standrig://docs/contract` 和 `standrig://docs/guide` 了解当前模型结构
- 通过 MCP 工具调用执行 Mesh 编辑、Deformer 操作、参数设置
- 支持 dry-run（预演）→ 数值 QA → 确定 → 视觉确认 的迭代流程
- 随时 Restore 到任意 Checkpoint

支持的 AI 变形操作：`smooth`、`relax`、`inflate`、`pinch`、`bend`、`contour-follow`，覆盖了 rigging 过程中最高频的调形操作。

---

## 快速上手

前置条件只需要 **Node.js 22.12+ 或 24+** 和浏览器，无需 AI 订阅就能先跑样例。

```bash
# Clone 后
npm ci
npm run build
npm start
# 然后访问 http://127.0.0.1:5180/
```

连接 Claude Code 等 MCP 客户端：

```json
{
  "mcpServers": {
    "standrig": {
      "command": "node",
      "args": ["/path/to/StandRig/packages/mcp/src/cli.mjs"],
      "env": { "STANDRIG_URL": "http://127.0.0.1:5180" }
    }
  }
}
```

连上之后，给 AI 的第一句话：

> StandRig 的 MCP 资源 standrig://docs/contract 和 standrig://docs/guide 请先读一下，然后用 standrig_context 确认当前模型结构，先不要改任何东西。

---

## cubism-api-bridge：打通 Live2D Cubism Editor

StandRig 本身是独立的建模核心，不直接操作 Cubism Editor 的 `.cmo3` 文件。但很多创作者的最终输出仍然需要经过 Cubism Editor（导出 `.moc3`、精细调整物理等）。

cubism-api-bridge 解决了这个问题：

- **TypeScript 通用客户端**：直接包装 Cubism External API（WebSocket）
- **本地 HTTP 服务器**：让 Python SDK 和任意 HTTP 客户端都能操作 Cubism Editor
- **StandRig 集成**：StandRig MCP 可通过 Bridge 从 Cubism 读取模型信息和临时操作参数

```
StandRig（MCP服务）
    ↓ 通过 cubism-api-bridge
Live2D Cubism Editor 5.4（External API）
```

当前是实验版，针对 Cubism Editor 5.4 alpha2 / External API 1.1.0，实现了 56 个 API 中的 47 个常规操作。Python 使用示例：

```bash
npm ci && npm run build          # 构建 Bridge
npm run http -- --port 22035     # 启动 HTTP 代理

python -m pip install ./python   # 安装 Python SDK
```

---

## 为什么这件事值得注意

这不只是"又一个 VTuber 工具"。从技术路线上看，StandRig 做了一件很重要的事：**从第一天就为 Agent 设计接口，而不是给人用的 GUI 加一个 AI 按钮**。

模型状态、操作约束、确认/回滚机制——都是面向程序化调用设计的。AI 不是在模拟人点击 Live2D 的界面，而是通过机器可读的 API 直接操作模型数据。

这和我们上篇文章讲的 [YC 2026 "Software for Agents" 赛道](https://blog.mushroom.cv/blog/yc-2026-ten-startup-tracks-ai-native-services/)完全对应：每一类人类在用的创意工具，都需要为 Agent 重做一遍。2D 角色 rigging 这个领域，现在有了第一个认真的答案。

当然，现在还是 0.2.0 开发预览版，有明确的限制：
- **PSD 需人工分好图层**（自动分层不在范围内）
- **不负责图像生成**（只做建模/绑定，不出图）
- **Live2D 的 `.moc3` 创建/转换不支持**（需要通过 Cubism Editor 完成）
- **仅在 Windows / Node.js 24 验证过**

这些限制是合理的边界划定，而不是缺陷。工具的核心价值在于把 rigging 这件最耗时的事变成 AI 可以自主完成的任务，并且做到了。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: StandRig — AI-editable 2D modeling core
> GitHub: https://github.com/sayaka-aiart/StandRig
> Editor bridge: https://github.com/sayaka-aiart/cubism-api-bridge
> Author: sayaka-aiart (developer preview 0.2.0, Apache 2.0 / MIT)

---

**BLUF**: StandRig is a local service that turns a layered PSD into a 2D character model that an AI can directly operate. Via MCP, Claude Code or any MCP client edits meshes, deformers, and key forms, seeing results immediately — no human dragging points in Live2D Cubism. The companion cubism-api-bridge connects it further to the official Cubism Editor External API.

---

## Where the Rigging Time Goes

Traditional 2D VTuber rigging is roughly:
1. Artist delivers art with separated layers (dozens to hundreds)
2. Rigger opens Live2D Cubism, places mesh points layer by layer
3. Sets up deformer parent-child hierarchies
4. Sets key forms parameter by parameter
5. Tests, iterates, fine-tunes — visually, by eye

An experienced rigger spends 40–80 hours on a moderately complex model. The work is precise, repetitive, and iterative — exactly the profile where AI performs best.

---

## How StandRig Works

StandRig splits the workflow into two clean parts: a **modeling core** (local service) and an **AI interface** (MCP).

**Local service** (`http://127.0.0.1:5180`):
- Parses a layered PSD: layer positions, hierarchy, transparency
- Maintains model state: meshes, deformers, parameters, key forms
- Browser UI for preview and parameter sliders
- Checkpoint management and bundle export

**MCP interface** (what the AI touches):
- AI reads `standrig://docs/contract` and `standrig://docs/guide` to understand the model
- Calls MCP tools to edit meshes, deformers, parameters
- Dry-run → numerical QA → commit → visual verify loop
- Restore to any checkpoint at any time

Supported deformation operations: `smooth`, `relax`, `inflate`, `pinch`, `bend`, `contour-follow` — the highest-frequency shape adjustments in rigging work.

---

## Quick Start

Prerequisites: **Node.js 22.12+ or 24+** and a browser. No AI subscription needed to test with the included sample.

```bash
npm ci && npm run build && npm start
# Then open http://127.0.0.1:5180/
```

Connect Claude Code or any MCP client:

```json
{
  "mcpServers": {
    "standrig": {
      "command": "node",
      "args": ["/path/to/StandRig/packages/mcp/src/cli.mjs"],
      "env": { "STANDRIG_URL": "http://127.0.0.1:5180" }
    }
  }
}
```

First message to the AI:

> Please read StandRig's MCP resources standrig://docs/contract and standrig://docs/guide, then use standrig_context to describe the current model's part structure and what motion is already configured. Don't change anything yet.

---

## cubism-api-bridge: Connecting to Live2D Cubism Editor

StandRig is a standalone modeling core — it doesn't directly touch Cubism Editor's `.cmo3` files. But many creators need Cubism Editor for final export (`.moc3`) and physics tuning.

cubism-api-bridge solves this:

- **TypeScript client**: wraps Cubism External API (WebSocket) directly
- **Local HTTP server**: lets Python SDK and any HTTP client operate Cubism Editor
- **StandRig integration**: StandRig MCP can read model info and temporarily set parameters via the bridge

```
StandRig (MCP service)
    ↓ via cubism-api-bridge
Live2D Cubism Editor 5.4 (External API)
```

Currently experimental, targeting Cubism Editor 5.4 alpha2 / External API 1.1.0, with 47 of 56 APIs implemented.

---

## Why This Matters

This isn't just another VTuber tool. The design decision that matters: **StandRig is agent-first from day one, not a human GUI with an AI button bolted on**.

Model state, operation constraints, commit/rollback — all designed for programmatic access. The AI isn't simulating a human clicking in Live2D's interface; it's directly operating model data through machine-readable APIs.

This maps exactly to the [YC 2026 "Software for Agents" track](https://blog.mushroom.cv/blog/yc-2026-ten-startup-tracks-ai-native-services/): every category of human-facing creative tool needs to be rebuilt for agents. For 2D character rigging, StandRig is a first serious answer.

Current limitations are clearly scoped:
- **PSD must be manually layer-separated** (auto-segmentation is out of scope)
- **No image generation** (modeling/binding only)
- **No `.moc3` creation/conversion** (needs Cubism Editor for that)
- **Tested on Windows / Node.js 24 only**

These are deliberate boundaries, not defects. The core value — making rigging, the most time-consuming part, something AI can do autonomously — is delivered.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
