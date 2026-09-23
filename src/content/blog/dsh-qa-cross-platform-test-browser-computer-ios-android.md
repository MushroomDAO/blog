---
title: "dsh-qa 全家桶开源：浏览器、macOS 桌面、iOS、Android 四驱动，让 AI Agent 做真正的跨平台 QA"
titleEn: "dsh-qa Full Suite Open Source: Browser, macOS Desktop, iOS, Android — Four Drivers for Real Cross-Platform AI QA"
description: "ZSeven-W 系列 DSH 跨平台测试插件生态全员到齐：dsh-qa（编排中枢）+ dsh-browser + dsh-computer + dsh-ios（300 stars）+ dsh-android（158 stars），全 MIT，Node 24.11+ 统一基准。AI Agent 像真实用户一样探索 App，捕获带证据的发现，导出确定性回放脚本跑 CI。"
descriptionEn: "ZSeven-W's DSH cross-platform testing plugin suite is now complete: dsh-qa (orchestrator) + dsh-browser + dsh-computer + dsh-ios (300 stars) + dsh-android (158 stars). All MIT, Node 24.11+ unified baseline. AI Agent explores your app like a real user, captures evidence-bound findings, exports deterministic replay scripts for CI."
pubDate: 2026-09-23
heroImage: "../../assets/images/dsh-qa-cross-platform-test-browser-computer-ios-android-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "testing", "qa", "dsh", "browser-automation", "ios", "android", "cross-platform", "mit", "agent"]
lang: zh-CN
---

ZSeven-W 系列的 DSH 跨平台 QA 插件今天全员到齐：核心编排插件 **dsh-qa** 和驱动 **dsh-browser**、**dsh-computer** 同期开源，加上此前已有的 **dsh-ios**（300 stars）和 **dsh-android**（158 stars），四个独立平台驱动按需接入，统一由 dsh-qa 编排。

全系 MIT，Node 24.11+ 为统一基准，macOS 是全功能 host 的硬性要求。

---

## 生态全景

| 插件 | 定位 | Stars | 版本 | 主要平台 |
|------|------|-------|------|---------|
| **dsh-qa** | 编排中枢（新开源） | 2 | 0.1.0-rc.2 | 全平台 |
| **dsh-browser** | 浏览器驱动（新开源） | — | — | Chrome / Firefox |
| **dsh-computer** | macOS 桌面驱动（新开源） | — | — | macOS 14+ |
| **dsh-ios** | iOS 驱动（此前已开源） | 300 | 0.1.0-rc.10 | iOS Simulator / 实体 iPhone |
| **dsh-android** | Android 驱动（此前已开源） | 158 | 0.1.0-rc.8 | Android Emulator / 实体机 |

全部挂在 `@zseven-w/` 命名空间下：

```bash
npm install @zseven-w/dsh-qa         # 编排器（必装）
npm install @zseven-w/dsh-browser    # 浏览器驱动（按需）
npm install @zseven-w/dsh-computer   # macOS 桌面驱动（按需）
npm install @zseven-w/dsh-ios        # iOS 驱动（按需）
npm install @zseven-w/dsh-android    # Android 驱动（按需）
```

---

## 为什么要有 dsh-qa

传统 QA 自动化（Selenium、Playwright、Appium）的核心痛点是**测试维护成本**：UI 稍有变化就要修脚本，坐标定位一升级就崩，假绿测试大量堆积。

dsh-qa 换了一个根本性的思路：

**让 AI Agent 像真实用户一样探索 App**，把 Agent 的探索行为记录下来，转化成**带证据绑定的断言**，再导出为**确定性回放脚本**供 CI 使用。

核心设计原则：
- **杜绝假绿**：未知结果（`inconclusive`）必须重新验证，不允许静默通过
- **证据绑定**：每个断言必须带截图或日志证据
- **确定性回放**：导出的场景跨版本稳定运行，不依赖坐标或脆弱选择器

---

## dsh-qa：编排中枢

dsh-qa 是整套生态的入口插件。在 DSH 项目里，每个测试项目自动绑定一个 DSH 会话，以 `qa` 测试模式 Preset 运行：

```bash
# DSH 插件模式接入
dsh plugin add @zseven-w/dsh-qa

# 或直接在项目里安装
npm install @zseven-w/dsh-qa
```

安装后 DSH 会话里多出 QA 专用工具集：场景创建、证据捕获、断言绑定、回放脚本导出。配置要接哪几个平台驱动，dsh-qa 统一编排分发。

**Node.js 要求**：≥24.11.0（这是全套的硬性门槛）

---

## dsh-browser：浏览器驱动

接入 Chrome 和 Firefox，带着已登录的真实浏览器给 Agent 用。核心优势是**保留 Cookie 和登录态**，无需每次重新认证。

**工具能力**：点击、输入、滚动、导航、标签页管理、读取页面区域

**安全特性**：密码/支付卡字段自动遮掩（显示为 `••••`），Agent 看不到明文凭据

**性能参考**：平均交互延迟 5.32s，比 Playwright 基线快约 20%

**要求**：
- Node.js `^22.19` 或 `≥24`
- Chrome 116+ 或 Firefox 140+
- DSH Companion 扩展安装到浏览器

---

## dsh-computer：macOS 桌面驱动

把 Agent 的操控范围从浏览器延伸到整个 macOS 桌面——任意原生 App、系统设置、文件管理器都可以操控。

**关键设计**：
- **无焦点抢夺**：操作不干扰用户正在进行的工作
- **独立 Agent 光标**：有视觉反馈，但不动系统指针
- 每次操作后返回最新 UI 观察结果，防止用过时状态做判断

**11 个 MCP 工具**：观察屏幕、点击、文字输入、拖拽及组合操作

**平台要求**：
- macOS 14+（Universal binary，arm64 + x86_64）
- Node.js ≥22.19.0 或 24.0.0+
- 必须手动授权：**辅助功能（Accessibility）+ 屏幕录制** 两个系统权限
- ⚠️ macOS Helper 需要手动编译和授权，没有一键安装脚本

**限制**：
- 最小化或隐藏的窗口无法操控
- 自定义 Canvas 和强化输入面（如游戏引擎渲染区）可能拒绝事件
- 仅限 macOS host

---

## dsh-ios：iOS 驱动

三款驱动里最成熟的一个，300 stars，版本 0.1.0-rc.10，接入 iOS Simulator 和 USB 实体 iPhone。

**22 个 Agent 工具**，覆盖：

| 类别 | 工具 |
|------|------|
| 设备管理 | 列出设备、选择目标、重启 |
| UI 交互 | 点击（语义/坐标）、文字输入、滑动、长按 |
| 调试 | 辅助功能树解析、OCR 文字识别、截图 |
| App 生命周期 | 启动、终止、重装、读取日志 |

**MJPEG 实时流**：持久侧边栏，不占用图片块，看着手机屏幕让 Agent 操作，有接近实时的视觉反馈

**SwiftUI Preview 热重载**：约 2-5 秒无需重启模拟器，改代码后 Agent 马上在更新后的 UI 上继续

**语义化操控**：按 Accessibility Label 或页面文字点击，不猜坐标，升级换皮后依然可用

**平台要求**：
- macOS + **完整 Xcode**（命令行工具不够，必须完整版）
- ≥1 个 iOS Simulator Runtime
- DSH ≥0.1.0-rc.6
- 实体设备额外需要：Developer Mode 开启、USB 数据线、Apple Development 签名证书

**限制**：
- 仅限 macOS host（其他系统工具注册但调用时给出说明）
- 闲置 5 分钟后实时流停止

---

## dsh-android：Android 驱动

158 stars，版本 0.1.0-rc.8，文档覆盖 13 语言（含中文简繁体），接入 Android Emulator 和 USB 实体手机。

**20 个 Agent 工具**，覆盖：

| 类别 | 工具 |
|------|------|
| 设备管理 | adb 设备列表、连接管理、串号选择 |
| UI 交互 | 点击、滑动、文字输入、按键事件 |
| 视觉 | 截图（直接返回图片块）、OCR 文字查找 |
| App 开发 | Gradle 构建触发、APK 安装、日志读取 |
| 系统诊断 | 内存/CPU 信息、进程列表 |

**模拟器和实体机代码路径统一**：都通过 adb serial，切换目标不改脚本

**进程内流**：无外部 Helper 服务，无端口管理，启动和停止更干净

**平台要求**：
- Node.js ≥24.11.0
- adb（Android SDK platform-tools）
- DSH ≥0.1.0-rc.6
- USB 调试已开启

**限制**：
- 实体设备帧率低（2-5 fps vs 模拟器 5-10 fps）
- OCR 功能（`android_find_text` 等）**仅限 macOS host**
- 非 ASCII 输入（中文等）需额外安装 ADBKeyboard

---

## 硬件与环境全景

| 能力 | 最低硬件 | OS 要求 |
|------|---------|---------|
| 浏览器测试 | 任意现代机器 | macOS/Linux/Windows |
| macOS 桌面测试 | Apple Silicon 或 Intel Mac | macOS 14+ |
| iOS Simulator | Mac（8GB 内存建议 16GB） | macOS + 完整 Xcode |
| iOS 实体机 | Mac + USB + iPhone | macOS + Apple Dev 账号 |
| Android Emulator | Mac 或 Linux（amd64） | 装好 Android SDK |
| Android 实体机 | 任意 Mac/Linux + USB | USB 调试开启 |
| Android OCR | Mac only | macOS（OCR 框架限制） |

---

## 适合什么团队

**最适合**：
- 已经在用 DSH（DeepSeek Harness）做 AI 编码，想把 QA 也纳入同一套工具链
- 移动端产品需要多端回归测试，但不想维护多套测试框架
- 想让 AI Agent 主导探索式测试，而不是只能跑预先写好的脚本

**暂不适合**：
- Windows 主力开发机（iOS/Android OCR、macOS 桌面驱动均不支持）
- 对 0.1.0 rc 版本稳定性有要求的生产 CI 环境
- 没有完整 Xcode 环境想做 iOS 测试（命令行工具不够）

---

## 局限性汇总

1. **全系预发布状态**：dsh-qa 和新开源的 dsh-browser、dsh-computer 均为 rc 版本，API 可能变化
2. **macOS 中心化架构**：iOS OCR、Android OCR、macOS 桌面测试全部要求 Mac host，Windows/Linux 用户能力有缩减
3. **依赖 DSH 生态**：这套工具只在 DSH（DeepSeek Harness）框架内工作，不是独立工具
4. **大页面断言不确定性**：在内容密集的大页面上，缺席断言可能返回 `inconclusive` 而非确定结果
5. **视觉断言仅参考**：截图级别的视觉断言不影响 pass/fail，只作辅助

---

## 与其他方案对比

| 方案 | 多端统一 | AI 主导探索 | DSH 生态 | 维护框架 |
|------|---------|------------|---------|---------|
| **dsh-qa 全家桶** | ✅ 4 端 | ✅ | ✅ 原生 | 无需维护脚本 |
| Appium | ✅ iOS+Android | ❌ | ❌ | 需维护大量脚本 |
| Playwright | 仅浏览器 | 有插件 | ❌ | 需维护 |
| Detox | 仅 React Native | ❌ | ❌ | 深度绑定 RN |

dsh-qa 的核心差异是 **Agent 主导 + 证据绑定 + 确定性回放**，把探索测试和回归测试统一进一个框架。代价是深度绑定 DSH 生态。

> 全系 MIT，开源仅供学习研究参考。预发布版本，生产使用前评估稳定性。

---

<!--EN-->

## dsh-qa Suite Open Source: Browser, macOS Desktop, iOS, Android — Four Drivers for AI-Driven QA

The ZSeven-W DSH cross-platform QA plugin ecosystem is now complete:

- **dsh-qa**: New — QA orchestration hub
- **dsh-browser**: New — browser driver (Chrome/Firefox)
- **dsh-computer**: New — macOS desktop driver
- **dsh-ios**: Prior release — iOS Simulator + physical iPhone (300 stars)
- **dsh-android**: Prior release — Android Emulator + physical device (158 stars)

All MIT, all under `@zseven-w/` namespace, Node 24.11+ unified baseline.

---

### Install

```bash
npm install @zseven-w/dsh-qa         # orchestrator (required)
npm install @zseven-w/dsh-browser    # browser driver (optional)
npm install @zseven-w/dsh-computer   # macOS desktop driver (optional)
npm install @zseven-w/dsh-ios        # iOS driver (optional)
npm install @zseven-w/dsh-android    # Android driver (optional)
```

---

### Core Concept

Traditional QA automation breaks on UI changes. dsh-qa takes a different approach:

**AI Agent explores the app like a real user** → captures evidence-bound findings → exports deterministic replay scripts for CI.

Three design rules:
- No silent passes: `inconclusive` results must be re-verified
- Evidence binding: every assertion requires attached screenshot or log
- Deterministic replay: exported scenarios stay stable across app versions

---

### Platform Drivers

**dsh-browser**: Chrome 116+ / Firefox 140+. Preserves login state and cookies. 11 tools: click, type, scroll, navigate, tab management, page content reading. Password fields auto-masked.

**dsh-computer**: macOS 14+ only (Universal binary). Controls any native macOS app without focus stealing. Requires manual Accessibility + Screen Recording permission grant. 11 MCP tools.

**dsh-ios** (300 stars, v0.1.0-rc.10): iOS Simulator and USB iPhone via WebDriverAgent. 22 tools. MJPEG live stream sidebar. SwiftUI hot-reload (2-5s). Semantic taps by Accessibility label, not coordinates. Requires full Xcode (not just CLI tools).

**dsh-android** (158 stars, v0.1.0-rc.8): Android Emulator and USB device via adb serial. 20 tools. Native screenshot image blocks. Gradle build integration. OCR (`android_find_text`) macOS host only. Non-ASCII input requires ADBKeyboard.

---

### Hardware Reality Check

| Capability | Requires |
|-----------|---------|
| Browser testing | Any modern machine |
| macOS desktop testing | Mac, macOS 14+ |
| iOS testing | Mac + full Xcode + Simulator runtime |
| iOS physical device | Mac + USB + Apple Dev account |
| Android testing | Mac or Linux + Android SDK |
| Android OCR | macOS only |

Full capability requires macOS as host. Windows/Linux can run browser and Android testing but lose iOS entirely and Android OCR.

---

### Limitations

1. **All pre-release (rc)**: dsh-qa, dsh-browser, dsh-computer are rc.2 — API may change
2. **macOS-centric**: iOS testing, Android OCR, macOS desktop all require Mac host
3. **DSH-only**: works inside DeepSeek Harness, not a standalone tool
4. **Dense-page assertions**: may return `inconclusive` on large content-heavy pages
5. **Visual assertions advisory only**: screenshot assertions don't affect pass/fail

---

### Best Fit

For: teams already using DSH for AI coding who want QA in the same toolchain; mobile products needing multi-platform regression without maintaining multiple frameworks; AI-led exploratory testing.

Not for: Windows-primary teams (reduced capability); production CI before rc stabilizes; iOS testing without full Xcode.

> MIT license. Pre-release software — evaluate stability before production CI. For learning and research reference only.
