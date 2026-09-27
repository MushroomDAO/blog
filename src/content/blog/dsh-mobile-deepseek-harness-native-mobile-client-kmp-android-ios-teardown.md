---
title: "dsh-mobile：40 天 366 星的 DeepSeek Harness 原生移动端，KMP 双端架构深度拆解"
description: "Clarklevis1995/dsh-mobile，MIT，Kotlin Multiplatform。DeepSeek Harness 的原生 Android/iOS 移动客户端，从手机远程接入 PC 本地 AI 编程 Agent。流式对话、工作区文件、Human-in-the-loop 审批、安全扫码配对。v1.6.2 今天刚发，40 天迭代 13 个版本。核心红旗：iOS 是无签名 IPA，无法直接安装到手机。"
pubDate: 2026-09-27
heroImage: "../../assets/images/dsh-mobile-deepseek-harness-native-mobile-client-kmp-android-ios-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["移动端", "AI Agent", "Kotlin Multiplatform", "DeepSeek", "开源拆解", "Android", "iOS"]
lang: "zh-CN"
wechatTitle: "DeepSeek Harness手机端：40天366星KMP客户端"
wechatDigest: "MIT KMP双端；iPhone远程接入PC本地Agent；iOS无签名IPA不能直接装；v1.6.2今天刚发"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 背景：DSH 是什么，mobile 加了什么

**DSH = DeepSeek Harness**，一个运行在 PC/Linux 上的本地 AI 编程 Agent 框架，有会话、工作区、工具调用、Agent 权限分级——定位类似 Claude Code 的对标产品，但完全本地化。

**dsh-mobile** 是社区开发者 Chaofan Li（Clarklevis1995）为 DSH 做的原生移动端客户端。核心用途：坐在沙发上用手机查看、干预、控制在家里台式机上跑着的 AI 编程 Agent。

仓库：github.com/Clarklevis1995/dsh-mobile  
**Stars：366 | License：MIT | 语言：Kotlin（实为 KMP 双端）| 创建：2026-08-17 | 最新版本：v1.6.2（2026-09-27，今天刚发）**

40 天内迭代了 13 个正式版本，发布频率相当于三天一个版本。

---

## 架构：KMP 三层

系统由三部分组成：

```
DeepSeek Harness（PC/Linux）
        │
dsh-plugin-mobile-gateway（JavaScript DSH 插件，需单独安装）
        │ WebSocket ws/wss
   ┌────┴────┐
Android    iOS
OkHttp     URLSession
   │           │
KMP shared/commonMain
（协议 DTO、Gateway Runtime、Store/Reducer、历史同步）
   │           │
Jetpack    SwiftUI/UIKit
Compose
```

**三个模块**：

- `shared/`：Kotlin Multiplatform 共享层。Protocol DTO、Gateway Runtime、Store/Reducer、Conversation/Trajectory Projection、历史分页与去重逻辑。共享层不依赖任何 UI 框架，两端复用。

- `androidApp/`：Jetpack Compose + OkHttp WebSocket + DataStore（普通配置）+ Android Keystore（凭据存储）+ CameraX/ML Kit 扫码配对。

- `DeepSeekHarnessMobile/`：SwiftUI/UIKit + URLSession WebSocket + Keychain（凭据）。**注意：iOS 的 Swift Gateway Client 尚未完全接入 KMP Gateway Runtime**，WebSocket 连接和重连仍由 Swift 层处理，再通过 Adapter 送入共享层——相比 Android 是个不对称的"过渡状态"。

---

## 核心功能

### 实时流式对话

处理 WebSocket 增量事件，在手机上渲染 Markdown、代码块、AI 思考过程、工具调用及结果、图片附件。历史与实时解耦：分页加载旧历史时保留实时消息尾部，按序列号去重，避免时序错乱。

### 完整 Agent 轨迹可视化

查看 User/Assistant/Tool 事件的完整轨迹，含工具调用参数、Token 计数、耗时。不只是聊天界面——是完整的 Agent 监控视图。

### 工作区文件浏览

浏览远端目录，分块下载文件并 SHA-256 校验完整性，支持代码文件预览。相当于手机上的 SSH 文件管理器，但集成在 Agent 上下文里。

### Human-in-the-loop 审批

支持 Human Question 交互和工具调用审批——提交、取消、拒绝、单次允许。让你在 Agent 执行危险操作前在手机上手动确认。

### 安全配对

扫 DSH WebUI 的二维码或手动输入配对码，凭据存入平台安全存储（Android Keystore / iOS Keychain）。

### Agent 配置管理

配置 Provider/模型、思考等级，以及三级权限预设：read-only / workspace-write / danger-full-access。

---

## 版本演进：先 iOS 后 Android

| 版本段 | 时间段 | 关键变化 |
|--------|--------|---------|
| v1.0～v1.2 | 2026-08-22～08-25 | 仅有 iOS IPA，无 Android |
| v1.3.0 | 2026-08-30 | Android 加入，KMP 架构改造完成 |
| v1.4.0 | 2026-09-03 | 工作区文件支持 |
| v1.5.x | 2026-09-08～09-16 | Gateway 协议迭代 |
| v1.6.2 | 2026-09-27 | Android 架构优化，Schedule 协议支持 |

反直觉的是：GitHub 语言标注是 Kotlin，但最早六个版本只有 iOS IPA，没有 Android——说明项目起点是 Swift，KMP 架构是后来补进来的。

---

## 四个关键问题

### 1. iOS 无签名 IPA，无法正常安装

这是最大的实用门槛。没有 TestFlight，没有 App Store。Release 提供的 `.ipa` 文件是无签名包，iPhone 用户必须：

- 用 AltStore / Sideloadly 等工具侧载（每 7 天需要重签，免费账号限制）
- 或持有苹果开发者账号（$99/年）自签
- Issues #3 和 #12 都在问"有没有 TestFlight 计划"，目前无回应

**Android 用户只需下载 APK，门槛低得多。**

### 2. iOS 后台 WebSocket 无保障

README 明确写明：iOS 使用系统授予的有限后台执行时间管理活动任务，"**不保证无限期维持 WebSocket**"。App 进入后台后连接可能被系统切断。

Android 通过前台服务保活，没有这个问题。

### 3. Android 新建会话卡死

Issues #13、#14（2026-09-09 提交，至今仍 open）：Android 端新建会话概率性失败/卡死。v1.6.2 的变更日志提到"架构优化"，但 issue 仍未关闭，说明问题可能尚未完全解决。

### 4. 协议版本深度耦合

`dsh-mobile-v1`、`hello.protocol = 3`、`historyFormatVersion: 4`——必须与 DSH 特定版本（0.1.7-rc.2+）匹配。旧版历史游标需要重新取基线。整个生态的维护节奏取决于 DSH 主项目和 dsh-plugin-mobile-gateway（目前仅 42 stars）的同步情况。

---

## 生态依赖：短板在后端插件

dsh-mobile 的运行需要三个组件全部就位：

1. DSH（DeepSeek Harness）主程序，运行在 PC 上
2. `dsh-plugin-mobile-gateway` 插件（`dsh plugin add dsh-plugin-mobile-gateway@latest`），目前只有 42 stars
3. dsh-mobile 本身

42 stars 的前置依赖是整条链路的薄弱点。如果 dsh-plugin-mobile-gateway 停止维护或与 DSH 主版本脱节，dsh-mobile 直接失效。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 366 |
| License | MIT |
| 语言 | Kotlin (KMP) + Swift |
| 创建时间 | 2026-08-17 |
| 版本数量 | 13 个正式版（40 天） |
| 最新版本 | v1.6.2（2026-09-27） |
| iOS 最低版本 | 17.0+ |
| Android 最低版本 | 7.0 (API 24)+ |
| 前置依赖 | dsh-plugin-mobile-gateway（42 stars） |
| 已知 open issue | 13 个 |

---

## 综合判断

功能覆盖面在「给本地 AI Agent 做移动端」这个细分赛道里是目前最完整的：流式对话、工具轨迹、文件浏览、审批、配对安全性都做了。40 天 13 个版本的迭代节奏说明作者在认真维护。

实用门槛集中在两处：**iOS 用户需要自己解决签名问题**，**生态依赖链的短板在 42 星的后端插件**。如果你是 Android 用户且已经在用 DeepSeek Harness，这个客户端值得一试。iOS 用户先等 TestFlight。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## dsh-mobile: Native Mobile Client for DeepSeek Harness, KMP Dual-Platform Architecture Teardown

> **Open source for learning only**: All projects discussed are from public repositories.

---

### What Is DSH? What Does "Mobile" Add?

**DSH = DeepSeek Harness** — a local AI coding agent framework that runs on PC/Linux, with sessions, workspace, tool calls, and tiered agent permissions. Think: a locally-hosted Claude Code alternative.

**dsh-mobile** is a native mobile client for DSH by community developer Chaofan Li (Clarklevis1995). Core use case: sit on your couch and monitor, review, and intervene in an AI coding agent running on your home desktop.

Repo: github.com/Clarklevis1995/dsh-mobile  
**366 stars | MIT | Kotlin (KMP) | Created 2026-08-17 | Latest: v1.6.2 (released today)**

13 releases in 40 days — roughly one every 3 days.

---

### KMP Three-Layer Architecture

```
DeepSeek Harness (PC/Linux)
        │
dsh-plugin-mobile-gateway (JS DSH plugin)
        │ WebSocket ws/wss
   ┌────┴────┐
Android    iOS
OkHttp     URLSession
   │           │
KMP shared/commonMain
(Protocol DTOs, Gateway Runtime, Store/Reducer, History Sync)
   │           │
Jetpack    SwiftUI/UIKit
Compose
```

**Three modules**: `shared/` (KMP business logic, no UI dependencies), `androidApp/` (Jetpack Compose + OkHttp + Keystore), `DeepSeekHarnessMobile/` (SwiftUI + URLSession + Keychain).

**Asymmetry**: iOS Swift `GatewayClient` hasn't been fully migrated into the KMP Gateway Runtime — WebSocket connection and reconnection are still handled in Swift, then fed to the shared layer via Adapter. "Work in progress" state.

---

### Core Features

- **Real-time streaming chat**: Incremental WebSocket events, Markdown, code blocks, AI thinking traces, tool calls with results, image attachments
- **Full agent trajectory**: User/Assistant/Tool events with parameters, token counts, durations
- **Workspace file browsing**: Remote directory tree, chunked download with SHA-256 integrity check, code preview
- **Human-in-the-loop**: Human Question interactions + tool approval (submit/cancel/reject/allow-once)
- **Secure pairing**: Scan QR code from DSH WebUI or manual pairing code; credentials in platform secure storage (Keystore/Keychain)
- **Agent configuration**: Provider/model, thinking level, read-only / workspace-write / danger-full-access permission presets

---

### Version History Quirk

The GitHub language shows Kotlin, but v1.0–v1.2 shipped **iOS only** with no Android. KMP architecture came in v1.3.0 (six weeks in). The project started as a Swift iOS app and grew into a cross-platform one.

---

### Four Critical Issues

**1. iOS ships unsigned IPA — can't install directly.** No TestFlight, no App Store. Users need AltStore/Sideloadly (7-day re-sign cycle) or an Apple Developer account ($99/year). Issues #3 and #12 ask for TestFlight — no response yet. Android users just download the APK.

**2. iOS background WebSocket not guaranteed.** README explicitly states: iOS "does not guarantee indefinitely maintaining the WebSocket" when the app is backgrounded — system will kill it. Android uses a foreground service.

**3. Android new session creation crashes.** Issues #13/#14 (opened 2026-09-09, still open): new session creation fails/freezes intermittently. v1.6.2 claims "architecture optimization" but issues remain open.

**4. Protocol version tight coupling.** `dsh-mobile-v1`, `hello.protocol = 3`, `historyFormatVersion: 4` — must match DSH ≥ 0.1.7-rc.2. Old history cursors require re-baselining after upgrades.

---

### The Weakest Link: 42-Star Backend Plugin

dsh-mobile requires three components: DSH main program + `dsh-plugin-mobile-gateway` plugin (42 stars) + dsh-mobile itself. The plugin is the least-starred piece in the chain. If it falls behind DSH's update cadence, the whole mobile client breaks.

---

### Numbers

| Metric | Value |
|--------|-------|
| Stars | 366 |
| Age | 40 days |
| Releases | 13 |
| iOS minimum | 17.0+ |
| Android minimum | 7.0 (API 24)+ |
| Gateway plugin stars | 42 |
| Open issues | 13 |

---

### Verdict

Feature coverage is the most complete available for the "mobile client for local AI agent" niche: streaming chat, tool traces, file browsing, approvals, secure pairing. 13 releases in 40 days means active maintenance.

Practical blockers: **iOS users need to solve code signing themselves**, and **the ecosystem depends on a 42-star backend plugin**. Android users already on DeepSeek Harness: worth trying. iOS users: wait for TestFlight.

---

> Open source for learning only. Verify license terms before commercial use.
