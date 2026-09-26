---
title: "LingChat：沉浸式 AI 恋爱游戏伴侣，18 类情绪识别 + 截屏感知 + Live2D，Tauri 2 + Vue 3"
titleEn: "LingChat: Immersive AI Galgame Companion — 18-Class Emotion Recognition, Screen Perception, Live2D, Built on Tauri 2 + Vue 3"
description: "SlimeBoyOwO/LingChat，AGPL-3.0，Rust，2,255 stars。沉浸式 AI 恋爱游戏（Galgame）聊天软件：自训练 18 类情绪识别模型、截屏感知主动评论、Live2D 角色服装切换、VITS 语音合成（GPU 约 1 秒）、多角色剧情脚本 + 好感系统、番茄计时 / 日程管理。架构：Tauri 2 Rust 后端 + Vue 3 前端 + PixiJS Live2D 渲染。API 驱动，默认 DeepSeek，支持 Ollama / LM Studio 本地模型。Windows 主力，Linux AppImage，macOS 支持，Android/iOS 移植进行中。资源引用自《碧蓝档案》《Undertale》，仅限非商用。"
descriptionEn: "SlimeBoyOwO/LingChat, AGPL-3.0, Rust, 2,255 stars. Immersive AI Galgame companion chat: self-trained 18-class emotion recognition, desktop screenshot perception with proactive commentary, Live2D character with costume switching, VITS voice synthesis (GPU ~1s), multi-character story scripts + relationship/bond system, Pomodoro timer and schedule manager. Architecture: Tauri 2 Rust backend + Vue 3 frontend + PixiJS Live2D rendering. API-driven, DeepSeek default, Ollama/LM Studio local model support. Windows primary, Linux AppImage, macOS, Android/iOS ports in progress. Game assets sourced from Blue Archive and Undertale — non-commercial only."
pubDate: 2026-09-26
wechatTitle: "LingChat：沉浸式AI恋爱游戏聊天+桌宠"
wechatDigest: "AGPL-3.0 Rust+Vue3；18类情绪识别+截屏感知+Live2D；VITS语音；DeepSeek API"
heroImage: "../../assets/images/lingchat-ai-galgame-desktop-pet-emotion-scheduler-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "ai-companion", "galgame", "tauri", "rust", "live2d", "emotion-recognition", "desktop-app"]
lang: zh-CN
---

`SlimeBoyOwO/LingChat`，AGPL-3.0，Rust，2,255 stars，131 forks，v0.5.2（2026-09-13）。一个以日式恋爱游戏（Galgame）为模板的沉浸式 AI 聊天软件——AI 回复有情绪表情，能感知你的桌面状态主动评论，支持 Live2D 角色，有 VITS 语音合成，还内置了日程管理和多角色剧情。

**GitHub**：github.com/SlimeBoyOwO/LingChat

---

## 核心功能

**1. 自训练情绪识别模型**

自行训练的情绪分类模型（`SlimeBoyOwO/Emotion-Model-Trainer`），从 AI 的每条回复中识别 18 种情绪类别。对应到不同的角色表情、动作、对话气泡样式和背景 BGM——AI 不只是输出文字，整个 UI 都跟着情绪联动变化。

**2. 截屏感知 / 主动评论**

自制 `tauri-plugin-screenshots` 插件，定期截取桌面画面，判断当前状态（工作中 / 打游戏 / 摸鱼），让 AI 主动发起评论。这个功能让 AI 从「等你问才回答」变成「时不时会来搭话」的状态。

**3. Live2D 角色，完全可自定义**

底层用 PixiJS 8 + `untitled-pixi-live2d-engine` 渲染 Live2D 模型。支持：
- 导入自己的原创角色或游戏人物的 Live2D 模型
- 运行时切换服装
- 「摸摸头」互动（角色有物理反馈动画）
- 作者自绘的默认角色（非 AI 生成）

**4. VITS 语音合成**

接入 vits-simple-api 或 Style-Bert-VITS2，用角色专属声线合成语音。速度取决于硬件：独显约 1 秒/条，CPU / 核显可能长达 1 分钟，核显用户出错率高时可能无法正常使用语音功能。

**5. 多角色剧情 + 好感系统**

可以导入多角色对话脚本，设置角色之间的关系弧线，以及通过对话触发的成就解锁机制。不是单纯的一对一聊天，而是可以写「剧情」的结构。

**6. 内置生产力工具**

番茄计时、日程管理、待办清单——AI 会根据当前感知状态给出上下文相关的提醒，比如番茄时间快结束时角色会提示休息。

---

## 架构：Tauri 2 + Vue 3

```
┌───────────────────────────────────┐
│  Rust 后端 (Tauri 2)              │
│  OS 集成 / LLM API 调用           │
│  截屏插件 / 文件 I/O              │
│  通知 / 自动更新                  │
└────────────┬──────────────────────┘
             ↓
┌───────────────────────────────────┐
│  Vue 3 前端 + Vite 6              │
│  TypeScript + Tailwind CSS v4     │
│  Pinia 状态 / Vue Router 5        │
│  PixiJS 8 + Live2D 渲染引擎       │
└───────────────────────────────────┘
```

构建工具：pnpm 11 + pnpm workspaces。情绪模型在首次启动时通过 `scripts/download_emotion_model.mjs` 下载。

---

## LLM 接入：API 驱动，非本地捆绑

LingChat 自身不打包模型，走 OpenAI 兼容 API：

| 类型 | 说明 |
|------|------|
| **默认推荐** | DeepSeek（v0.5.2 更新为最新模型） |
| **本地模型** | Ollama / LM Studio（任何 OpenAI 兼容端点均可） |
| **视觉模型** | 单独配置槽，默认复用对话模型，或指定视觉能力模型（示例：阿里云 Qwen VL 免费额度） |
| **推理强度** | 每个模型可单独配置 `effort` 参数 |

v0.5.2 新增原生多模态图片发送，支持图片压缩率配置。

---

## 平台支持

| 平台 | 状态 |
|------|------|
| Windows 10+ 64-bit | ✅ 主力支持，发布 `.7z` 包 |
| Linux | ✅ AppImage（v0.5.2 修复了缺失 `dawn.so` 的问题） |
| macOS | ✅ 支持 |
| Android (aarch64) | 🔧 进行中，构建脚本已有 |
| iOS | 🔧 进行中，unsigned IPA 构建脚本已有 |

> **Windows 注意**：Windows Defender 会对 `.exe` 误报，README 明确说明需要手动添加白名单。

---

## 资源来源与许可证问题

这是用这个项目前必须了解的：

**游戏资源**：语音气泡和音效来自《碧蓝档案》（Blue Archive），对话提示音来自《Undertale》。README 明确标注：**仅限非商用**。这两款游戏的资源有各自的版权方（Nexon / Toby Fox），这些素材未经商用授权。

**AGPL-3.0**：项目代码本身采用 AGPL-3.0，如果你修改后部署为网络服务，需要公开源代码。

**实际限制**：游戏资源 + AGPL-3.0 的组合意味着这个项目在法律层面只适合个人非商业使用，任何商业化方向都需要替换这些第三方资源。

---

## v0.5.2 值得关注的修复

- **上下文裁剪 bug**：之前在裁剪 context window 时会破坏 tool-call 配对，导致 HTTP 400 报错。v0.5.2 修复。
- **自动存档覆盖**：之前启动 app 会自动触发存档覆盖，现在只在实际对话变更时触发。
- **Linux 打包**：修复了 AppImage 缺少 `dawn.so` 的问题。

---

## 局限性

**1. 语音速度**：CPU / 核显下 VITS 合成可能长达 1 分钟/条，实际体验会很割裂。需要独显才能流畅使用语音功能。

**2. 资源版权**：Blue Archive + Undertale 资源未经商用授权，项目整体仅限个人非商业使用。想自定义体验需要自备合规的 Live2D 模型和音效资源。

**3. AGPL-3.0**：如果基于这个项目二次开发并提供网络服务，必须公开修改后的源代码。

**4. 91 个开放 issues**：活跃开发中，功能边界还在调整，不是稳定的生产级软件。

**5. 无本地模型**：不是离线运行的——需要 API key，离开网络或 API 服务就没有 AI 响应。

---

## 怎么看这个项目

2,255 stars，在 AI 伴侣 / 虚拟角色类项目里算小而精的。技术亮点是「18 类情绪 → UI 全联动」和「桌面截屏感知」这两个功能——前者让 AI 回复不再是纯文字输出，后者让 AI 有了被动感知用户状态的通道，这两点在同类项目里并不常见。

Tauri 2 + Vue 3 的架构选择也值得参考：Rust 后端处理 OS 级集成（截屏、通知、自动更新），Vue 前端处理复杂 UI 逻辑，分工清晰，且原生支持桌面 + 移植路径走 Tauri 的 Android/iOS 方向。

如果你在做 AI 角色 / 陪伴类应用，截屏感知和情绪-UI 联动这两个模块值得单独研究。

> 开源仅供学习研究参考。游戏内置资源（Blue Archive / Undertale）版权归各自原作方所有，仅限个人非商业使用；商用前须替换为自有合规资源。

---

<!--EN-->

## LingChat: Immersive AI Galgame Companion — Emotion Recognition, Screen Perception, Live2D

`SlimeBoyOwO/LingChat` — AGPL-3.0, Rust, 2,255 stars. Immersive AI companion chat modeled on Japanese visual novels (Galgame). Core features: self-trained 18-class emotion recognition, desktop screenshot perception with proactive comments, Live2D characters, VITS voice synthesis, multi-character story scripts + bond system, built-in Pomodoro and schedule manager.

**GitHub**: github.com/SlimeBoyOwO/LingChat

---

### Core Features

**Emotion recognition**: Self-trained model classifies 18 emotion categories per AI reply. Speech bubbles, expressions, actions, background art, and BGM all change with the detected emotion — the entire UI is emotion-driven.

**Screen perception**: Custom `tauri-plugin-screenshots` Tauri plugin captures the desktop periodically, detects current activity (working / gaming / idle), and has the AI proactively comment. Shifts the AI from reactive to ambient-aware.

**Live2D characters**: PixiJS 8 + `untitled-pixi-live2d-engine`. Supports importing custom OC or game characters, runtime costume switching, and "pat" interaction with physics animation. Default character is hand-drawn by the author.

**VITS voice synthesis**: Integrates vits-simple-api or Style-Bert-VITS2. GPU: ~1s per line. CPU/iGPU: up to ~1 min per line; heavy errors on iGPU may make voice unusable.

**Story scripts + bond system**: Multi-character dialogue scripts, relationship arcs, achievement unlocks triggered by conversation.

**Productivity**: Pomodoro timer, schedule manager, to-do list — AI gives context-aware reminders based on current state.

---

### Architecture

**Tauri 2 (Rust)** backend: OS integration, LLM API calls, screenshot capture, file I/O, notifications, auto-update.

**Vue 3 frontend**: Vite 6 + TypeScript + Tailwind CSS v4 + Pinia + Vue Router 5 + PixiJS Live2D rendering.

Build: pnpm 11 + pnpm workspaces. Emotion model downloaded on first run.

---

### LLM Support

API-driven, not bundled. OpenAI-compatible endpoints:

| Type | Details |
|------|---------|
| Default | DeepSeek (updated to latest model in v0.5.2) |
| Local | Ollama / LM Studio (any OpenAI-compatible endpoint) |
| Vision | Separate config slot; can reuse conversation model or assign dedicated vision model |
| Reasoning intensity | Configurable `effort` per model |

v0.5.2 added native multimodal image sending with configurable compression.

---

### Platform Support

- **Windows 10+ 64-bit**: Primary target (`.7z` release package)
- **Linux**: AppImage (v0.5.2 fixed missing `dawn.so`)
- **macOS**: Supported
- **Android/iOS**: Build scripts present, ports in progress

Windows Defender commonly false-positives the `.exe` — README tells users to whitelist it.

---

### Asset License Warning

Speech bubbles and SFX sourced from *Blue Archive* (Nexon); dialogue beep from *Undertale* (Toby Fox). README explicitly marks these as **non-commercial only**. Combined with AGPL-3.0, the project is legally personal/non-commercial use only unless you replace all third-party assets.

---

### v0.5.2 Notable Fixes

- **Context pruning**: Fixed broken tool-call pairing during context window trimming (was causing HTTP 400 errors)
- **Auto-save**: No longer overwrites saves on app launch; only triggers on actual conversation changes
- **Linux packaging**: Fixed missing `dawn.so` in AppImage

---

### Assessment

2,255 stars in the AI companion space. Two technically distinctive features: 18-class emotion → full UI linkage (rare in comparable projects), and desktop screenshot perception as a passive ambient awareness channel. Tauri 2 + Vue 3 architecture is worth studying for any native desktop AI app: Rust handles OS-level integration cleanly, Vue handles complex UI state, and the same Tauri codebase gives you an Android/iOS porting path. The VITS voice latency on CPU is a real UX blocker — the project works well only with a discrete GPU for voice. For anyone building AI character / companion apps, the emotion-UI linkage and screen-perception modules are worth studying independently.

> For learning and research reference only. Built-in game assets (Blue Archive / Undertale) are copyrighted by their respective owners and marked non-commercial by the author. Replace with your own compliant assets before any commercial use.
