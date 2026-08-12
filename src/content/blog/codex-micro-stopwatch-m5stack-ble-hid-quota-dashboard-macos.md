---
title: "用 M5Stack 手表做 Codex Micro 控制器：BLE HID + 额度仪表盘 + USB 麦克风"
titleEn: "codex-micro-stopwatch-m5stack-ble-hid-quota-dashboard-macos"
description: "digitsisyph/codex-micro-stopwatch，MIT，C++/Swift，2026-08-05 发布。把 M5Stack StopWatch Dev Kit C152（466×466 圆形 AMOLED，ESP32-S3）变成 Codex Micro 兼容的 BLE HID 控制器，同时在表盘上显示本周 Codex 剩余额度和 reset 倒计时。双 BLE 通道设计：HID 通道走标准 Codex Micro 协议（Push to talk / Voice Chat / Send / 四向滑动），GATT 通道走自定义服务接收 Mac companion 发来的额度快照。OpenAI token 永不离开 Mac。可选 USB 麦克风模式：表盘内置麦克风在 macOS 以「Codex StopWatch Mic」枚举（48kHz/16-bit/mono）。安装方式：把仓库打开给 Codex，粘贴 README 里的提示词，让 Codex 自主完成固件编译、刷机、蓝牙配对和 Swift companion 构建——用 AI 来安装 AI 控制器硬件。"
descriptionEn: "digitsisyph/codex-micro-stopwatch, MIT, C++/Swift, released 2026-08-05. Turns an M5Stack StopWatch Dev Kit C152 (466×466 round AMOLED, ESP32-S3) into a Codex Micro-compatible BLE HID controller with a Codex quota dashboard. Dual BLE channel design: HID channel emulates the Codex Micro protocol (Push to talk / Voice Chat / Send / four swipe directions); separate GATT channel receives quota snapshots from a local macOS Swift companion. OpenAI token never leaves the Mac. Optional USB mic mode: onboard microphone enumerates on macOS as 'Codex StopWatch Mic' (48 kHz / 16-bit / mono). Installation: open the repo in Codex, paste the README prompt, and let Codex autonomously build firmware, flash the device, pair Bluetooth, and build the Swift companion — an AI installs the AI controller hardware."
pubDate: "2026-08-12"
updatedDate: "2026-08-12"
category: "Tech-News"
tags: ["Codex", "M5Stack", "BLE", "硬件", "ESP32", "macOS", "开源", "Mycelium"]
heroImage: "../../assets/images/codex-micro-stopwatch-m5stack-ble-hid-quota-dashboard-macos-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Codex Micro 是 OpenAI 和 Work Louder 联合推出的实体控制器，专门为 ChatGPT Desktop 和 Codex 工作流设计。它走 BLE HID，一个按钮对应一个操作——推送发言、发送消息、切换语音模式。

官方硬件。官方价格。

然后有人把一块 M5Stack 圆形智能手表刷成了一个。

**GitHub**: https://github.com/digitsisyph/codex-micro-stopwatch | MIT | C++ / Swift | ESP32-S3

---

## 硬件：M5Stack StopWatch Dev Kit C152

M5Stack StopWatch（SKU C152）是 M5Stack 生态里的开发套件，外形是一块圆形智能手表：

- 466 × 466 圆形 AMOLED（原生分辨率，无黑边缩放）
- ESP32-S3 主控，内置 BLE 5.0
- 左侧实体键、右侧实体键、红色电源键
- 中央可点击圆形触摸表盘
- 全屏滑动检测（上/右/下/左）
- 内置扬声器、马达（振动反馈）
- 内置麦克风
- 磁吸充电座（Dock）

codex-micro-stopwatch 是这块硬件的 PlatformIO 固件项目，附带一个 macOS Swift companion。

---

## 双 BLE 通道架构

这个项目的核心设计是**两条独立的 BLE 通道**，做不同的事：

### 通道 1：HID 通道（Codex Micro 协议）

表盘通过标准 BLE HID 向 macOS 上报控制事件，和官方 Codex Micro 使用同一套协议：

| 操作 | 上报的 HID 动作 | 推荐的 Codex 配置 |
|------|--------------|----------------|
| 按住左侧实体键 | Mic key `ACT10` | Push to talk |
| 按一下右侧实体键 | Command Key 4 `ACT09` | Toggle voice chat |
| 点击中央表盘 | Send key `ACT12` | 发送输入框消息 |
| 向上滑动 | 摇杆上 | 用户自定义 |
| 向右滑动 | 摇杆右 | 用户自定义 |
| 向下滑动 | 摇杆下 | 用户自定义 |
| 向左滑动 | 摇杆左 | 用户自定义 |

### 通道 2：私有 GATT 服务（额度数据）

Codex Micro 标准 HID 协议不包含账户额度信息。项目为此专门设计了一个私有 GATT 服务：

```
Service UUID:              7f0d4e66-2ac2-4a71-bfbe-4ef61a0e5c01
Quota characteristic UUID: 7f0d4e66-2ac2-4a71-bfbe-4ef61a0e5c02
```

Mac companion 通过加密绑定的 BLE 链路，向手表写入这样一个 JSON 快照（最大 512 字节）：

```json
{
  "remaining_percent": 26,
  "reset_in_seconds": 356400
}
```

`reset_in_seconds` 是相对倒计时，而不是绝对时间戳——这样手表不需要依赖本地时钟来计算重置时间。

**结果**：表盘上实时显示「本周 Codex 额度还剩 26%，4 天 3 小时后重置」。

---

## Mac companion 是怎么工作的

Companion 是 Swift 5.10 写的 macOS 应用，从源码编译，不分发二进制。它做三件事：

1. **启动或接入本地 Codex App Server**，使用用户已登录的 ChatGPT/Codex 会话上下文——不需要 API Key
2. **调用 `account/rateLimits/read`** 读取 Codex 额度，明确选择主 Codex bucket，不静默回退到 Spark 或次要 bucket
3. **通过 GATT 写入手表**，频率最多每分钟一次（或 App Server 有变化事件时立即更新）

**隐私设计的核心**：companion 发给手表的只有 `remaining_percent` 和 `reset_in_seconds` 两个字段。API Key、access token、账号 ID、任务文本、提示词内容——全部留在 Mac 上，永远不进入 BLE 数据流。

**UUID 绑定**：companion 在 demo 发现阶段拿到这台 Mac 的 CoreBluetooth UUID，之后只向这个特定设备写真实额度，不向任何其他 BLE 广播者发送。

---

## 可选：USB 麦克风模式

默认固件使用 Mac 选定的系统麦克风。

如果需要使用手表自带的麦克风，可以安装独立的 `usb-mic` 固件：
- 在 macOS 以 **Codex StopWatch Mic** 枚举（系统设置 → 声音 → 输入可见）
- 格式：48 kHz、16-bit、mono
- **只有输入，没有 USB speaker**
- BLE 控制和额度仪表盘不受影响
- 当 Mac 没有流式读取麦克风时，手表仍会播放本地 Agent 完成提示音；录音流激活时，提示音暂停

两个固件版本都使用 Bluedroid 承载 BLE。如果切换固件后 macOS 仍缓存旧的 HID descriptor，忘记「Codex Micro」的配对记录再重新配对即可。

---

## 电源管理

固件有细粒度的电源管理，区分两个工作场景：

**电池模式（无线）**：
- 2 分钟后屏幕变暗
- 5 分钟后进入桌面休眠，关闭 AMOLED/音频/马达共用电源轨
- BLE 保持在线，Agent 提醒不中断

**Dock 模式（接 USB 电源）**：
- 变暗延迟延长到 10 分钟
- 桌面休眠延迟延长到 30 分钟
- USB 麦克风版本保持共用电源轨开启（需要持续录音）

**旅行模式**（双击红色电源键 / 长按中央表盘 6 秒触发 fallback）：
- ESP32-S3 PM1 真关机
- 按电源键或接 USB 才能冷启动
- 关机期间 Agent 提醒会被错过

---

## 最妙的地方：用 Codex 来安装 Codex 控制器

项目的推荐安装方式是这样的：

1. 把仓库克隆或 ZIP 下载到 Mac
2. 在 **Codex Desktop** 里打开这个 folder
3. 把 README 里那段安装提示词粘给 Codex

然后 Codex 自主完成：
- 检查 macOS 版本、ESP32-S3 硬件、PlatformIO、Swift 工具链
- 解析串口（只报告新接入的那个，不猜测）
- 展示 M5Stack 官方恢复固件链接
- 编译固件并刷机（刷机前再次确认端口 + 用户手动许可）
- 用 `scripts/serial_probe.py` 验证 `CODEX_MICRO_STOPWATCH_READY` 启动标记
- 引导 macOS 蓝牙配对
- 从源码编译 Swift companion
- 用 demo discovery 绑定这台 Mac 的 CoreBluetooth UUID
- 分层验证：实体键、滑动手势、Agent 颜色、完成提示音、振动、真实额度

**这件事本身就很有意思**：一个 AI 编程助手的实体控制器，由同一个 AI 编程助手从零安装。仓库的 AGENTS.md 是给 Codex（和 Claude Code）的持久化指令，定义了安装全程的安全边界——不询问 token、不猜测端口、不在 Git 提交设备 UUID。

---

## 工程边界和已知限制

项目 AGENTS.md 明确了几条边界，诚实标注了什么还没验证：

- **仅支持 M5Stack StopWatch Dev Kit C152**，不适配其他 M5Stack 设备
- Codex Micro 协议属于**实验性、非官方**的兼容实现，协议文档不来自 OpenAI
- 桌面休眠/唤醒和旅行模式关机的**浸泡测试尚未完成**，电源行为标注为实验性
- 一次只支持**一个激活的 Codex Micro**：安装或使用手表版本时，需要断开或关闭官方实体键盘

---

## 开始使用

```bash
# 克隆仓库
git clone https://github.com/digitsisyph/codex-micro-stopwatch.git

# 在 Codex Desktop 里打开
# 连接 M5Stack StopWatch C152（数据 USB-C 线）
# 粘贴 README.zh-CN.md 里的安装提示词给 Codex
```

需要的工具：
- macOS 14+
- Swift 5.10+ (Xcode 15.3 Command Line Tools)
- PlatformIO Core
- ChatGPT Desktop（支持 Codex Micro 的版本）

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Codex Micro Controller from an M5Stack Watch: BLE HID + Quota Dashboard + USB Mic

*by Mycelium Protocol*

---

Codex Micro is OpenAI and Work Louder's hardware controller for ChatGPT Desktop and Codex workflows. It connects over BLE HID. One button per action — push to talk, send message, toggle voice mode.

Official hardware. Official price tag.

Then someone flashed an M5Stack round smartwatch into one.

**GitHub**: https://github.com/digitsisyph/codex-micro-stopwatch | MIT | C++ / Swift | ESP32-S3

---

### Hardware: M5Stack StopWatch Dev Kit C152

The M5Stack StopWatch (SKU C152) is a development kit in the M5Stack ecosystem, shaped like a round smartwatch:

- 466 × 466 round AMOLED (native resolution, no black-bar scaling)
- ESP32-S3, onboard BLE 5.0
- Left physical button, right physical button, red power button
- Center tappable circular touch dial
- Full-screen swipe detection (up / right / down / left)
- Onboard speaker, motor (haptic feedback)
- Onboard microphone
- Magnetic charging dock

codex-micro-stopwatch is a PlatformIO firmware project for this hardware, paired with a macOS Swift companion.

---

### Dual BLE Channel Architecture

The project's core design uses **two independent BLE channels** for two different jobs:

**Channel 1: HID channel (Codex Micro protocol)**

The watch reports control events to macOS over standard BLE HID, using the same protocol as the official Codex Micro:

| Input | Reported HID action | Recommended Codex mapping |
|-------|---------------------|--------------------------|
| Hold left physical button | Mic key `ACT10` | Push to talk |
| Press right physical button | Command Key 4 `ACT09` | Toggle voice chat |
| Tap center dial | Send key `ACT12` | Send composer message |
| Swipe up/right/down/left | Analog stick directions | User configurable |

**Channel 2: Private GATT service (quota data)**

The Codex Micro HID protocol carries no account quota information. The project adds a custom GATT service for this:

```
Service UUID:    7f0d4e66-2ac2-4a71-bfbe-4ef61a0e5c01
Quota char UUID: 7f0d4e66-2ac2-4a71-bfbe-4ef61a0e5c02
```

The Mac companion writes a JSON snapshot (max 512 bytes) over an encrypted bonded BLE link:

```json
{
  "remaining_percent": 26,
  "reset_in_seconds": 356400
}
```

`reset_in_seconds` is a relative countdown rather than an absolute timestamp, so the watch doesn't need a synchronized local clock.

**Result**: the watch face shows live "26% of weekly Codex allowance remaining, resets in 4 days 3 hours."

---

### How the Mac Companion Works

The companion is a Swift 5.10 macOS app built from source (no binary distribution). It does three things:

1. **Starts or attaches to a local Codex App Server** using the user's existing signed-in ChatGPT/Codex session — no API key required
2. **Calls `account/rateLimits/read`** to fetch Codex quota; explicitly selects the primary Codex bucket, never silently falling back to Spark or a secondary bucket
3. **Writes to the watch via GATT** at most once per minute (or immediately when the App Server sends a change event)

**Privacy architecture**: the companion sends exactly two fields to the watch — `remaining_percent` and `reset_in_seconds`. API keys, access tokens, account identifiers, task text, and prompts stay on the Mac and never enter the BLE data stream.

**UUID binding**: the companion captures the Mac's CoreBluetooth UUID during a demo discovery step, then only writes real quota to that specific paired device — never to any other BLE advertiser.

---

### Optional: USB Microphone Mode

The default firmware uses the Mac's selected system microphone.

The isolated `usb-mic` firmware target adds:
- USB Audio Class device that enumerates as **Codex StopWatch Mic** in macOS System Settings → Sound → Input
- Format: 48 kHz, 16-bit, mono
- Input only — no USB speaker endpoint
- BLE controls and quota dashboard still work
- Local completion chime plays when the host is not streaming microphone audio; pauses while the USB audio stream is active

Both firmware images use Bluedroid for BLE. If macOS caches a stale HID descriptor after switching images, forget only the "Codex Micro" pairing record and re-pair.

---

### Power Management

The firmware distinguishes two operating contexts:

**Battery mode (wireless)**:
- Screen dims after 2 minutes
- Desk sleep after 5 minutes — shuts down the shared AMOLED/audio/motor power rail
- BLE stays alive, Agent alerts continue

**Dock mode (USB power)**:
- Dim delay extends to 10 minutes
- Desk sleep delay extends to 30 minutes
- USB mic image keeps the shared rail on (needed for continuous recording)

**Travel Mode** (double-press red button / 6-second center dial hold as fallback):
- ESP32-S3 PM1 true shutdown
- Power button or USB power resumes; Agent alerts are missed until restart

---

### The Best Part: Codex Installs the Codex Controller

The recommended installation flow:

1. Clone or download the repository to a Mac
2. Open the folder in **Codex Desktop**
3. Paste the installation prompt from the README into Codex

Codex then works autonomously through:
- macOS version, C152 hardware, PlatformIO, and Swift toolchain checks
- Serial port resolution (reports only the newly connected port, never guesses)
- Showing the M5Stack official factory recovery link
- Compiling firmware and flashing (reports exact port, waits for user confirmation before any write)
- Verifying `CODEX_MICRO_STOPWATCH_READY` serial marker via `scripts/serial_probe.py`
- Guiding macOS Bluetooth pairing
- Building the Swift companion from source
- CoreBluetooth UUID binding via demo discovery
- Layered validation: physical buttons, swipe gestures, Agent status colors, completion chime, haptics, real quota update

**This is the genuinely interesting part**: a hardware controller for an AI coding assistant, installed from zero by the same AI coding assistant. The repository's `AGENTS.md` provides durable instructions for Codex (and Claude Code), defining the safety boundary for the entire installation — don't ask for tokens, don't guess ports, don't commit device UUIDs to Git.

---

### Engineering Boundaries and Known Limitations

The project's AGENTS.md states these explicitly:

- **Only M5Stack StopWatch Dev Kit C152** — no other M5Stack devices
- The Codex Micro protocol compatibility is **experimental and undocumented** — reverse-engineered, not from OpenAI docs
- Desk sleep/wake and Travel Mode **soak testing is still pending** — power behavior is marked experimental
- **One active Codex Micro at a time** — disconnect or power off the official hardware controller before installing or using the watch

---

### Getting Started

```bash
git clone https://github.com/digitsisyph/codex-micro-stopwatch.git
# Open in Codex Desktop
# Connect M5Stack StopWatch C152 via data USB-C cable
# Paste the installation prompt from README.md into Codex
```

Requirements:
- macOS 14+
- Swift 5.10+ (Xcode 15.3 Command Line Tools)
- PlatformIO Core
- ChatGPT Desktop with Codex Micro support

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
