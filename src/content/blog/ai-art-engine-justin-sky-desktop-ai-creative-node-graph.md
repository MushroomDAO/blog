---
title: "AI Art Engine：节点图驱动的本地 AI 创作工作台，内置 MCP"
titleEn: "AI Art Engine: Local-First AI Creative Workbench with Node Graph and Built-in MCP"
description: "Justin-sky/ai-art-engine，GPL-3.0，203 stars，TypeScript+Electron，多平台。面向短剧/广告/成片制作的 AI 创作工具：节点图拖拉生成、资产库、分镜画布、成片时间线，本地工程优先，30+ AI 提供商（OpenRouter/OpenAI/MiniMax/火山/可灵/ComfyUI 等）。内置 MCP Server（stdio 或 HTTP），Claude Code/Codex 可直连操作工程。Blender MCP 工具组（9 工具）让 AI 在聊天里搭 Blender 场景、截图自查、导出 GLB。SKILL.md 格式技能系统，AI 对话驱动全部生成能力。"
descriptionEn: "Justin-sky/ai-art-engine, GPL-3.0, 203 stars, TypeScript+Electron, cross-platform. AI creative tool for short drama/ads/finished video: node graph generation, asset library, storyboard canvas, video timeline, local-first projects, 30+ AI providers (OpenRouter/OpenAI/MiniMax/ByteDance/Kling/ComfyUI etc). Built-in MCP Server (stdio or HTTP) — Claude Code/Codex can directly operate projects. Blender MCP tool group (9 tools) lets AI build Blender scenes, take viewport screenshots, and export GLB via chat. SKILL.md-format skill system, AI conversation drives all generation capabilities."
pubDate: 2026-10-06
heroImage: "../../assets/images/ai-art-engine-justin-sky-desktop-ai-creative-node-graph-banner.jpg"
category: "Tech-Experiment"
tags: ["AI创作", "开发工具", "MCP", "节点图", "视频制作", "3D资产"]
lang: "zh-CN"
wechatTitle: "AI Art Engine：节点图AI创作台内置MCP"
wechatDigest: "GPL 203星；TypeScript Electron；30+AI厂商；Blender MCP 9工具；本地优先"
---

把"短剧/广告/成片"这类工作流完整跑通，通常需要切换：图生成用 ComfyUI，视频用可灵或 Seedance，3D 用 Meshy，配音用 ElevenLabs，剪辑用 PR/达芬奇，编排靠 AI 对话窗口。切换成本高，资产流转麻烦，提示词在各个工具之间对齐更费时间。

AI Art Engine 的定位是把这些工作在一个桌面端应用里完成：资产、分镜、节点图、成片时间线都在同一个本地工程里，模型调用走你自己的 API Key，数据不出本机。

GitHub: https://github.com/Justin-sky/ai-art-engine | ⭐ 203 | GPL-3.0 | TypeScript + Electron

---

## 核心架构：节点图

AI Art Engine 的生成核心是**节点图**——把文本/图片/视频/声音/3D/决策等不同类型的节点连成有向图，按拓扑顺序执行。

节点类型：

| 类型 | 代表节点 |
|------|---------|
| 文本生成 | 文本节点（接 30+ 提供商） |
| 图片生成 | Seedream / CogView / gpt-image / ComfyUI 等 |
| 视频生成 | Seedance / Veo 3.1 / Kling / MiniMax / 可灵 |
| 3D 模型 | Meshy / Tripo / Rodin / Luma AI / Lux3D |
| 声音 | TTS / 多说话人对话 / 音效 / 音乐 |
| 空间世界 | World Labs Marble（3D 沉浸式世界） |
| 决策 | OpenRouter Decisions API |
| 宿主资产 | 内嵌子图，暴露边界 I/O |

任务队列可以复用共同上游节点（多个下游共享同一张输入图），支持**任务容错模式**——某个节点失败不会中断整条链，而是标记失败然后继续其他分支。

---

## MCP Server：外部 Agent 直连操作

这是和大多数创作工具不同的一点。

内置 MCP Server 支持 **stdio 桥或 HTTP** 两种接入方式，让 Claude Code、Codex 等外部 AI Agent 可以直接操作你的本地工程：

- 规划并落盘工作流
- 运行生成任务
- 读写资产和节点图
- Token 跨重启持久复用、操作审计、并发闸门

同时，应用内有 **AI 对话面板**——在聊天里 `@` 引用工程资产，让 Agent 调用 MCP 工具直接出图、剪片、导出。

这两条路径（应用内对话 + 外部 Agent）走同一套工具集。应用内的 Ask/Plan 模式约束写入；外部 Agent 通过配置的权限级别接入。

---

## Blender MCP 工具组

这是最让 3D 工作流受益的部分：9 个 MCP 工具让 AI 直接在 Blender 进程里操作，不需要 uv、不起 Python 子进程、不改 Blender 配置。

工具清单：

| 工具 | 作用 |
|------|------|
| `get_scene_info` | 查场景物体列表 |
| `get_world_state_snapshot` | 全局状态快照 |
| `get_object_info` | 查选中对象 |
| `execute_blender_code` | 在 Blender 进程内执行 Python（完整 bpy/bmesh/mathutils 访问） |
| `get_viewport_screenshot` | 抓视口画面，回给多模态模型 |
| `export_scene` | 导出 GLB/GLTF/FBX/OBJ/USD/STL |
| `describe_node_type` | 查节点端口 |
| `bpy_api_lookup` | 查 bpy API |
| `get_addon_status` | 查 addon 版本 |

同时兼容社区方案（ahujasid/blender-mcp addon.py）和官方方案（Blender Lab MCP Server 扩展），在设置里切换，工具接口完全一致。

应用主动出站连接 Blender addon 的 `localhost:9876`，不需要反向代理。

---

## 提供商覆盖

30+ 模型提供商，按类型举例：

**文本**：OpenRouter / OpenAI / DeepSeek / 智谱 / Kimi / xAI / Gemini / vLLM / Ollama / LM Studio / 火山方舟

**图片**：Seedream / CogView / gpt-image-1 / ComfyUI API 2 / Grok Imagine

**视频**：Seedance / Veo 3.1 / Kling / MiniMax / 可灵 / ComfyUI API 2

**3D**：Meshy / Tripo / Rodin（Hyper3D）/ Luma AI / Lux3D

**声音/音乐**：ElevenLabs（含多说话人对话 + 音效 + 音乐）/ MiniMax / 通义千问 / OpenRouter（Google Lyria 3）

**空间世界**：World Labs Marble（文生/图生世界，输出 GLB + 高斯泼溅 + 360 全景图）

可用 NewAPI 或自定义 Base URL 接入各种 one-api 兼容中转网关。

---

## Skill 系统

技能文件是 DSH SKILL.md 格式（frontmatter `name`/`description` + Markdown 正文），放进指定技能目录后下次对话自动生效。

内置了专业创作技能（不需要配置）：分镜拆解、动作节拍表、导演审核、图生提示词、多角度、扩图、重绘、抠图、高清放大、情绪、灯光……外部 Agent 和应用内 Agent 用的是同一套技能清单，以 `<available_skills>` 注入对话上下文。

---

## 人像处理节点

`image.portrait` 是一个深度嵌套的处理节点，Dive 进去可以看到 16 组调整工具（修复/磨皮/肤色/五官/眼睛/妆容/身形/光影/调色/质感/区域/背景/证件照/AI增强/预设/导出），每项有 5 档强度。

它的执行路径只有一条：**参数合成提示词 → 调用你选的图片模型出图**。本地不做像素滤镜，是纯 AI 生成。批量模式支持最多 24 张。

---

## 许可证说明

GPL-3.0——如果你基于 AI Art Engine 的源码开发并分发，需要以同等许可证开放。

作为用户直接下载安装包使用不受 GPL 约束。

---

> GPL-3.0 开源。Justin-sky 维护，203 stars，TypeScript + Electron，Windows/macOS/Linux 多平台。开源仅供学习参考。

---

<!--EN-->

## AI Art Engine: Local-First AI Creative Workbench with Node Graph and Built-in MCP

Short drama/ad/finished-video workflows usually require context switching: ComfyUI for image generation, Kling or Seedance for video, Meshy for 3D, ElevenLabs for audio, a video editor for cuts. Context switching is expensive; asset handoff is messy; prompt consistency across tools takes real effort.

AI Art Engine puts this workflow in a single desktop app: assets, storyboards, node graph, and video timeline in one local project, using your own API keys with no data leaving your machine.

GitHub: https://github.com/Justin-sky/ai-art-engine | ⭐ 203 | GPL-3.0 | TypeScript + Electron

---

### Core Architecture: Node Graph

The generation core is a **directed node graph** — connect text/image/video/audio/3D/decision nodes in any topology, execute in topological order. Node types cover all major generation modalities. Task queues reuse common upstream nodes; **fault-tolerant mode** marks failed nodes and continues other branches instead of halting the whole chain.

---

### Built-in MCP Server

External AI agents (Claude Code, Codex) can connect via stdio bridge or HTTP to directly operate local projects: plan and commit workflows, run generation tasks, read/write assets and node graphs. Token state persists across restarts with audit logging and concurrency gates.

The built-in AI chat panel (`@`-references assets, lets the agent call MCP tools) and external agent connections share the same tool set.

---

### Blender MCP Tool Group

9 tools for direct Blender process control from AI chat — no uv, no Python subprocess, no Blender config changes. Key tools: `execute_blender_code` (full bpy/bmesh/mathutils access), `get_viewport_screenshot` (for multimodal vision feedback), `export_scene` (GLB/GLTF/FBX/OBJ/USD/STL). Supports both the community addon (ahujasid/blender-mcp) and the official Blender Lab extension — identical tool interface either way.

---

### 30+ AI Provider Coverage

Text, image, video, 3D, audio, music, spatial world generation, and object storage. Highlights: ElevenLabs (TTS + multi-speaker dialogue + sound effects + music), World Labs Marble (text/image/video → immersive 3D world + Gaussian splat + panorama), Meshy/Tripo/Rodin/Luma AI/Lux3D (3D model generation), ComfyUI API 2 (local or cloud). NewAPI or custom Base URL for any one-api compatible gateway.

---

### Skill System

SKILL.md-format skill files (DSH convention: frontmatter `name`/`description` + Markdown body) auto-load from a designated directory. Built-in professional skills cover storyboard breakdown, beat tables, director review, multi-angle generation, inpainting, upscaling, portrait retouching, and more. Injected as `<available_skills>` into conversation context.

---

> GPL-3.0. Maintained by Justin-sky, 203 stars, TypeScript + Electron, Win/macOS/Linux. For technical reference only.
