---
title: "jev-chat-JARVIS：Android 聊天副驾驶，无障碍服务读屏 + Jev 判断模型分析意图"
titleEn: "jev-chat-JARVIS: Android Chat Copilot — Accessibility Service Screen Reading + Jev Decision Model Intent Analysis"
description: "jev-chat/jev-chat-jarvis，MIT，Kotlin，6,614 stars，5天内从零冲到 v1.4。通过 Android 无障碍服务读取屏幕聊天内容，调用 Jev 判断模型评估危险等级（1–9）和真实意图，生成 3 条候选回复，悬浮窗展示，一键填入输入框（绝不自动发送）。适配 QQ / X（Twitter）/ 飞书（ML Kit OCR 兜底）。最大隐藏限制：微信 Android 版已明确下架，无法突破截屏限制。"
descriptionEn: "jev-chat/jev-chat-jarvis, MIT, Kotlin, 6,614 stars, grew from zero to v1.4 in 5 days. Uses Android accessibility service to read on-screen chat content, calls Jev decision model to assess threat level (1–9) and true intent, generates 3 reply candidates shown in a floating window for one-tap fill-in (never auto-sends). Adapts to QQ, X (Twitter), Feishu (ML Kit OCR fallback). Biggest hidden limit: WeChat Android is explicitly unsupported — the app's screenshot prevention cannot be bypassed."
pubDate: 2026-09-26
wechatTitle: "jev-chat-JARVIS：Android聊天副驾驶"
wechatDigest: "MIT 6614星5天；无障碍服务读聊天+Jev判断意图+3条候选回复；微信Android不支持"
heroImage: "../../assets/images/jev-chat-jarvis-android-chat-copilot-accessibility-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "android", "jev", "accessibility", "chat-assistant", "kotlin", "mobile", "ai-agents"]
lang: zh-CN
---

`jev-chat/jev-chat-jarvis`，MIT，Kotlin，6,614 stars，1,140 forks，v1.4（2026-09-23）。从 2026-09-21 开源，5 天内发布 5 个版本，达到 6000+ stars。一个 Android 聊天「副驾驶」——不侵入任何 App，靠无障碍服务把你屏幕上的聊天内容读出来，交给 Jev 判断模型分析，给你 3 条候选回复，填入输入框等你确认后手动发。

**GitHub**：github.com/jev-chat/jev-chat-jarvis（`Finderchangchang` 原作，现迁至 `jev-chat` 组织）

---

## 核心设计：「先判断再写字」

大多数 AI 聊天助手的逻辑是：输入对话 → 直接生成回复。JARVIS 在这中间插入了一个判断层：

```
读取屏幕聊天内容
  ↓
POST /v1/systemone（Jev 判断接口）
  ↓
返回：危险等级(1-9) / 真实意图 / 对方要什么 / 是否该立即回 / 建议动作
  ↓
生成 3 条候选回复（DeepSeek，OpenRouter 路由）
  ↓
悬浮窗展示候选，用户选择后一键填入输入框
  ↓
用户手动发送（绝不自动发送）
```

「先判断」这步花约 1 秒，回答的是「对方这条消息背后真正的目的是什么」，而不只是「内容是什么」。Jev 判断接口专为这类「理解而非生成」的问题优化，1000 token 级别的判断请求费用约 $0.00004（OpenCode Zen 端点定价）。

---

## 技术架构

### 采集层：无障碍服务 + 平台适配器

每个 App 一个 `ChatAppAdapter.kt`，按包名分发，各自处理 UI 树结构差异：

**QQ**：节点有 ID，`id/mjn` 读消息正文，`id/371` 读标题。头像位置（贴左=对方，贴右=我）判断消息归属。

**X（Twitter）**：节点无 ID，解析 `content-desc` 属性，格式为 `发件人：正文。时间。Read`，拆分提取。

**飞书**：聊天气泡是自绘控件，无障碍树里只有矩形坐标，无文本节点——改用 **ML Kit 离线中文 OCR** 对每个气泡矩形截屏识别。OCR 只能读可见部分，长消息被截断，我/对方靠已读状态推断，经常判反。

**未适配 App**：支持手动触发整屏 OCR，精度更低。

### 判断层：多路 Jev 端点

内置多个 `POST /v1/systemone` 兼容端点，全新安装默认 OpenRouter（release notes 与 README 有出入，v1.4 release notes 写"默认博查Jev"，README 写"默认OpenRouter"——以实际 APK 为准）：

| 端点 | 说明 |
|------|------|
| OpenRouter | 默认，走 OpenRouter 路由 |
| 博查Jev（jev.bocha.cn） | 第一赞助商，v1.4 大力推荐 |
| TypeSafe 直连 | 官方 TypeSafe AI 端点 |
| Vercel AI Gateway | ai-gateway.vercel.sh/typesafe |
| OpenCode Zen | opencode.ai/zen，模型 jev-1.13，约 $0.00004/次 |
| 通义兼容 / DeepSeek 官方 | 国内替代 |
| 自定义 | 任意 /v1/systemone 兼容地址 |

### 回复生成层

默认 `deepseek/deepseek-chat-v3.1`（via OpenRouter），生成 3 条候选。判断结果作为 system prompt 的一部分，引导回复与知识库内容一致。

### 回填机制

优先 `ACTION_SET_TEXT`，失败退回剪贴板 + `ACTION_PASTE`。任何情况下不触发发送。

### 本地存储

联系人档案（别名/备注/标签）和笔记本地存储于 App 私有目录。历史记录默认关闭，开启后仅存本地。知识库检索：关键词/标签包含匹配，不做语义搜索。

---

## 安装与权限

```bash
adb install -r apk/jev-assistant-v1.4-release.apk
```

必须开启三项权限：**无障碍服务**、**悬浮窗**、**自启动+省电无限制**（小米/HyperOS 必须开后两项，否则后台被杀）。小米设备升级系统版本后悬浮窗权限会被重置，每次升级需重新开启。

最小配置：一把 OpenRouter API Key，填判断接口，回复和视觉接口留空自动继承。

**构建**：JDK 17 + Android SDK platform 35。Release 签名需仓库外的 keystore，路径由 `JEV_KEYSTORE_PROPS` 环境变量指定，无法直接 clone 后 build release 包。

---

## 关键隐藏限制

### 微信 Android：明确不支持

这是中国用户最想用的场景，也是最大的「隐藏限制」。README 明确写：**「微信 Android 版已全面下架，不再采集或处理微信内容」**。

原因：微信设置了 `sharingType=0`，阻止任何窗口截图，无障碍树里的文本节点在微信内也被屏蔽。多个 issue 反映用户误以为能用微信，发现后感到困惑。v1.4 没有解决这个问题的计划。

**iOS 版**（`jev-chat-jarvis-ios`）通过自定义输入法方案规避了这个问题（长按复制后分析），但需要 Xcode 自编译，仅 18 stars。

### 飞书 OCR 是降级方案，不是能力

飞书支持靠 OCR 兜底——只能读屏幕可见部分，长消息截断，我/对方区分靠已读状态推断，错判率高。不要把它当成「已完整适配飞书」理解。

### 异步结果绑定 bug（issue #4）

一个严重的架构问题：异步分析结果不绑定发起时的会话状态。切换聊天窗口时，可能把 A 会话的分析结果显示在 B 会话的悬浮窗里。v1.4 未修复。

### Jev 中文判断质量待校准

v1.0 release notes 原话：「Jev 判断模型主要用英文训练，中文对话判断质量还需用真实数据校准」。v1.4 没有关于这个问题的更新。中文聊天场景的判断准确性存在不确定性。

---

## 五天五版本的代价

| 版本 | 日期 | 主要变化 |
|------|------|----------|
| v1.0 | 2026-09-21 | 首发，QQ/X 适配，OpenRouter |
| v1.1 | 2026-09-21 | 飞书 OCR 接入 |
| v1.2 | 2026-09-22 | 知识库+联系人档案 |
| v1.3 | 2026-09-22 | ML Kit 集成（APK +5MB），中文 OCR 离线模型 |
| v1.4 | 2026-09-23 | 博查Jev 接入，多端点配置，UI 优化 |

快速迭代的代价：26 个开放 issue，大量集中于设备兼容性——荣耀 MagicOS 后台杀进程、三星 S26U 无障碍权限异常、小米/HyperOS 自启动被重置。Android 碎片化在无障碍服务场景下被放大了。

---

## jev-chat 生态全图

`jev-chat` 组织目前有四个平台版本：

| 项目 | Stars | 语言 | 核心方案 |
|------|-------|------|----------|
| jev-chat-jarvis（本体） | 6,614 | Kotlin | 无障碍服务读节点/OCR |
| jev-chat-windows | 581 | Python | 窗口截图+本地离线 OCR |
| jev-chat-jarvis-mac | 407 | Python | 屏幕感知+本地小模型判断 |
| jev-chat-jarvis-ios | 18 | Swift | 自定义键盘+复制后分析 |
| jev-chat-jarvis-simple | — | Kotlin | Android 输入法版，零权限 |

Android 版之所以星数最多，是因为它的「无障碍服务读节点」方案比截图 OCR 精度高、延迟低，体验更接近原生——代价是需要更多系统权限和更多 App 适配工作。

---

## 关于这个项目本身

根目录有 `CLAUDE.md`，说明 jev-chat-JARVIS 本身是用 Claude Code 辅助开发的。作者柳伟杰（`Finderchangchang`）在 GitHub 活跃了 12 年，历史项目主要是低星 Android 工具，这是他第一个冲到千星以上的项目。

整个 `jev-chat` 组织目前 83 个 commit 里 83 个来自主要贡献者，外部贡献者各 1-4 次。是典型的「单人高速迭代，社区反馈驱动修 bug」模式。

---

## 怎么看这个项目

6,600 stars 在 5 天内——这是 Jev 判断协议在终端应用层的首个高星移动端实现。「先判断再写字」的架构本身有价值：把意图分析和回复生成解耦，让用户先看到「对方在想什么」，再决定怎么回。

实际体验的上限受两个因素限制：一是无障碍服务在中国主流 App（尤其是微信）里的覆盖率，二是 Jev 中文判断的准确度。前者是平台政策问题，后者是模型训练数据问题，两个都不是代码层面能解决的。

iOS 版的输入法方案（不需要截屏权限）是绕过这两个问题的有趣思路，但需要自编译，还没有被做到无痛安装的程度。

> 开源仅供学习研究参考。使用无障碍服务类应用请遵守相关 App 的使用条款，了解数据流向后再配置 API Key。

---

<!--EN-->

## jev-chat-JARVIS: Android Chat Copilot — Accessibility Service + Jev Decision Model

`jev-chat/jev-chat-jarvis` — MIT, Kotlin, 6,614 stars. Zero to v1.4 in 5 days (2026-09-21 to 2026-09-23). An Android chat copilot that uses the accessibility service to read on-screen chat content, sends it to a Jev decision model for intent analysis, and presents 3 reply candidates in a floating window. One tap fills the input field; the user always sends manually.

**GitHub**: github.com/jev-chat/jev-chat-jarvis

---

### Core Design: "Judge First, Then Write"

Most AI chat assistants go: input → generate reply. JARVIS inserts a judgment layer between reading and writing:

```
Accessibility service reads on-screen chat
  ↓
POST /v1/systemone (Jev decision endpoint)
  ↓
Returns: threat level (1–9) / true intent / what they want / whether to respond now / best action
  ↓
Generate 3 reply candidates (DeepSeek via OpenRouter)
  ↓
Floating window shows candidates; one-tap fills input
  ↓
User manually sends (never auto-sends)
```

The judgment step costs ~1 second and ~$0.00004 per call (OpenCode Zen endpoint, 1000-token decision requests). The goal is understanding intent, not just content.

---

### Technical Architecture

**Capture layer**: One `ChatAppAdapter.kt` per app, dispatched by package name.

- **QQ**: Uses accessibility node IDs (`id/mjn` for message body, `id/371` for title). Avatar position (left = other party, right = me) determines message attribution.
- **X (Twitter)**: No node IDs; parses `content-desc` attribute format `sender: body. time. Read`.
- **Feishu**: Chat bubbles are custom-drawn — no text nodes in accessibility tree. Uses **ML Kit offline Chinese OCR** on screenshotted bubble rectangles. Can only read visible content; long messages truncated; sender inference via read-status (often wrong).
- **Other apps**: Manual full-screen OCR trigger, lower accuracy.

**Decision layer**: Multiple `/v1/systemone`-compatible endpoints built in — OpenRouter (default), Bocha Jev, TypeSafe direct, Vercel AI Gateway, OpenCode Zen (jev-1.13), DeepSeek official, Tongyi-compatible, and custom URL.

**Reply generation**: `deepseek/deepseek-chat-v3.1` via OpenRouter generates 3 candidates. Judgment result is included in system prompt to guide response consistency with the user's knowledge base.

**Fill-back**: Prefers `ACTION_SET_TEXT`; falls back to clipboard + `ACTION_PASTE`. Never triggers the send action.

---

### Known Hidden Limits

**WeChat Android: explicitly unsupported.** WeChat sets `sharingType=0` and blocks all window screenshots; accessibility tree text nodes are also blocked inside WeChat. Many users discovered this only after installation. No fix planned.

**Feishu OCR is a fallback, not a feature.** It reads visible text only, truncates long messages, and frequently misidentifies sender attribution via read-status inference.

**Async result binding bug (issue #4)**: Analysis results are not bound to the originating conversation state. Switching chat windows while analysis is in-flight can display one conversation's results in another. Unresolved as of v1.4.

**Chinese judgment quality calibration needed**: v1.0 release notes acknowledge "Jev decision model is primarily trained in English; Chinese conversation judgment quality needs calibration with real-world data." No update on this in v1.4.

---

### jev-chat Ecosystem

| Project | Stars | Language | Approach |
|---------|-------|----------|----------|
| jev-chat-jarvis (this) | 6,614 | Kotlin | Accessibility node reading / OCR |
| jev-chat-windows | 581 | Python | Window screenshot + offline OCR |
| jev-chat-jarvis-mac | 407 | Python | Screen perception + local small model |
| jev-chat-jarvis-ios | 18 | Swift | Custom keyboard + copy-to-analyze |
| jev-chat-jarvis-simple | — | Kotlin | Android IME version, zero permissions |

Android leads in stars because accessibility node reading is more accurate and lower-latency than screenshot OCR — at the cost of more system permissions and per-app adapter work.

---

### Assessment

6,600 stars in 5 days is the Jev decision protocol's first high-star mobile application. The "judge first, write second" architecture has real design value: separating intent analysis from reply generation lets users see *what the other person wants* before deciding how to respond.

The practical ceiling is set by two non-code constraints: accessibility service coverage in Chinese apps (especially WeChat), and Jev's Chinese-language judgment accuracy. Both are outside what the developer can fix in Kotlin.

The iOS keyboard approach (no screenshot permission needed) is an interesting workaround for the first constraint, but still requires self-compilation and hasn't been made frictionless.

> For learning and research reference only. When using accessibility-service apps, review the terms of service for the apps you're analyzing, and understand the data flow before configuring any API keys.
