---
title: "M5Stack StopWatch 变成 Codex 物理控制器：BLE 麦克风 + 额度仪表盘 + 四向 Agent 触摸，vibe coding 专属硬件"
titleEn: "codex-micro-stopwatch-m5stack-ble-hid-quota-dashboard-macos"
description: "liptoxli/M5stopwatch-vibecoding 把 M5Stack StopWatch（ESP32-S3）改造成 Codex 专属物理控制器，MIT，C 语言固件。固件 v0.10.1 / macOS Bridge v1.3.1。核心能力：16 kHz IMA-ADPCM 实时 BLE 音频流变成 macOS 虚拟麦克风 M5 StopWatch Mic（不生成 WAV 文件）；BLE HID 实体按键控制语音输入；原生 Codex Micro BLE HID 兼容层（四 Agent 槽位/推理等级 Encoder/四向 Radial 输入）；466×466 圆形 AMOLED 显示 Codex 周额度、当天用量、四小时活动热力图和 Agent 状态；两套 UI（Classic/Pet 和 OpenWatcher V2）；约 5 小时续航（实测 4h33m）。"
descriptionEn: "liptoxli/M5stopwatch-vibecoding turns an M5Stack StopWatch (ESP32-S3) into a dedicated Codex physical controller — MIT, C firmware. Firmware v0.10.1 / macOS Bridge v1.3.1. Core capabilities: 16 kHz IMA-ADPCM real-time BLE audio stream becomes a macOS virtual microphone (M5 StopWatch Mic, no WAV files); BLE HID physical buttons control voice input; native Codex Micro BLE HID compatibility layer (4 agent slots / inference level encoder / 4-way radial input); 466×466 round AMOLED shows Codex weekly quota, daily usage, 4-hour activity heatmap, and agent status; two UIs (Classic/Pet and OpenWatcher V2); ~5-hour battery (tested 4h33m)."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["硬件", "Codex", "M5Stack", "BLE", "语音输入", "vibe coding", "ESP32", "物理控制器"]
heroImage: "../../assets/images/codex-micro-stopwatch-m5stack-ble-hid-quota-dashboard-macos-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：liptoxli/M5stopwatch-vibecoding  
硬件：M5Stack StopWatch（ESP32-S3，466×466 圆形 AMOLED）  
许可证：MIT  
语言：C（固件）+ Swift（macOS Bridge）  
Stars：7 · Forks：3  
固件：v0.10.1 | macOS Bridge：v1.3.1  
创建：2026-06-13 | 最近更新：2026-08-22

---

## 一、它在做什么

一句话：**把 M5Stack StopWatch 变成桌面上的 Codex 物理控制器**——语音输入、额度监控、Agent 状态，都在腕表大小的圆屏上。

具体来说，连上 Mac 之后，这块表能做三件事同时发生：

1. **变成系统级麦克风**：Mac 看到的是 `M5 StopWatch Mic` 输入设备，Typeless 等语音输入应用直接用它，不经过任何中转服务，不生成 WAV 文件
2. **实体按键控制一切**：A 键开始/停止语音，B 键确认发送，摇晃清除，长按保险
3. **Codex 状态实时显示**：圆屏显示周额度剩余、当天消耗、最近四小时活动热力图、四个 Agent 槽位状态

---

## 二、语音链路

```
M5Stack 麦克风
      ↓（16 kHz IMA-ADPCM，20ms 分帧）
BLE 实时音频流
      ↓
macOS Bridge
      ↓
M5 StopWatch Mic（Core Audio 虚拟输入设备）
      ↓
Typeless / 微信输入法 / 任意接受系统麦克风的应用
```

关键设计：**不是录音机**。音频实时流传输，停止讲话后直接进识别流程，没有先攒成文件的步骤。链路断开后会明确提示重新录制，不会静默拼接有缺口的语音。

---

## 三、原生 Codex Micro BLE HID 兼容层

v0.10.0 是这个项目的关键版本——从「状态屏」升级为「物理控制器」。一条 BLE 连接同时承载三类能力：

**标准键盘 Report + Consumer Report**：A/B 实体键，macOS 通用，Bridge 退出后仍然有效。

**Codex Vendor Report**：
- 下沿四个 Agent 点 → 对应 `AG00` 至 `AG03` 四个 Codex Agent 槽位。84×84px 透明触摸区，长按 480ms 后提交，提前松手不触发，防误触
- 顶部左右滑动 → 推理等级（Inference Level），每 44px 一级，单次最多六级
- 中心长按进入四向 Radial 控制 → 与 Codex Micro 协议一致（右 0.00 / 下 0.25 / 左 0.50 / 上 0.75）

这是目前少见的**硬件级 Codex Micro 协议实现**。

---

## 四、两套 UI

**Classic / Pet**：桌面伙伴风格，时间 + 额度弧线 + Pet 动画，情感化反馈。

**OpenWatcher V2**：效率界面，UI 思路参考自 OpenWatcher 项目，针对 466×466 圆形 AMOLED 重新设计：

- 顶部半圆进度条：语义渐变色——额度充足接近绿色，紧张时逐步橙红
- 中央突出「剩余百分比」，左侧显示「当天已用」，避免两个数字抢视觉中心
- 24 格方格覆盖最近四小时，每格 10 分钟，颜色深浅反映录音时长和启动频率
- 下沿四个 Agent 点：颜色、亮度和呼吸效果由 Mac 端原生状态决定

---

## 五、省电与续航

固件级省电策略：CPU 动态降频、麦克风按需启动、差分刷新（静态区域按变化更新）、1 分钟降亮度、3 分钟息屏、无外接电源 15 分钟自动关机。

2026-08-17 至 08-18 的实测：从 86% 到 0% 历时 **4 小时 20 分 51 秒**，最后阶段含屏幕常亮和频繁语音，属于偏重度使用。按完整电量估算约 **5 小时级**。

---

## 六、安装

**固件**（需要 ESP-IDF v5.5.x + M5Stack StopWatch）：

```bash
cd firmware-stopwatch-idf
python3 ./fetch_repos.py
idf.py set-target esp32s3
idf.py build
idf.py flash
```

**macOS Bridge**：

```bash
tools/typeless_bridge/build_stopwatch_ble_bridge.sh
tools/typeless_bridge/install_launch_agent.sh
```

安装后在「系统设置 → 隐私与安全性 → 辅助功能」允许 `StopWatch BLE Bridge`，然后在蓝牙配对 `M5Codex-*` 设备即可。

**注意**：从 v0.9.x 升级到 v0.10.x 时，由于 HID 描述符变化，需要先在 macOS 中忽略旧的 `M5Codex-*` 设备并重新配对一次。

---

## 七、对 Agent 二次开发友好

项目在根目录提供了 `AGENTS.md`，让 Codex 等代码 Agent 进入仓库后立即知道构建命令、代码边界和验收规则。还有 `docs/AGENT_DEVELOPMENT_GUIDE.md`，按「一功能、一组入口文件、一套验证方法」组织，可以只改 UI、触摸阈值、按键映射或麦克风参数，不需要先理解整个仓库。

---

这是目前看到的最完整的「Codex 专属硬件外设」实现——不是示波器或装饰品，而是真正改变了 vibe coding 工作流的物理界面层：眼睛盯着屏幕，手摸着表，嘴在说，Codex 在执行。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## M5Stack StopWatch as a Codex Physical Controller: BLE Mic + Quota Dashboard + Four-Way Agent Touch

*by Mycelium Protocol*

---

GitHub: liptoxli/M5stopwatch-vibecoding  
Hardware: M5Stack StopWatch (ESP32-S3, 466×466 round AMOLED)  
License: MIT  
Language: C (firmware) + Swift (macOS Bridge)  
Stars: 7 · Forks: 3  
Firmware: v0.10.1 | macOS Bridge: v1.3.1  
Created: 2026-06-13 | Updated: 2026-08-22

---

### What It Does

In one line: **turn an M5Stack StopWatch into a desktop Codex physical controller** — voice input, quota monitoring, and agent status all on a watch-sized round screen.

When connected to Mac, three things happen simultaneously:

1. **Becomes a system-level microphone**: Mac sees `M5 StopWatch Mic` as an input device; Typeless and other voice apps use it directly, no relay services, no WAV files generated
2. **Physical buttons control everything**: A button starts/stops voice, B confirms, shake clears, long press as a safety gate
3. **Codex status displayed in real time**: round screen shows weekly quota remaining, daily usage, 4-hour activity heatmap, 4 agent slot states

---

### Voice Pipeline

```
M5Stack microphone
      ↓ (16 kHz IMA-ADPCM, 20ms frames)
BLE real-time audio stream
      ↓
macOS Bridge
      ↓
M5 StopWatch Mic (Core Audio virtual input device)
      ↓
Typeless / WeChat input / any app that accepts a system mic
```

Key design: **not a recorder**. Audio streams in real time; recognition starts immediately after you stop speaking — no intermediate file. If the link drops mid-recording, the device flags the error and prompts re-recording rather than silently sending incomplete audio.

---

### Native Codex Micro BLE HID Layer

v0.10.0 is the milestone release — upgrading from "status screen" to "physical controller." One BLE connection carries three capability types simultaneously:

**Standard Keyboard + Consumer Report**: A/B physical buttons, universally recognized by macOS, still work after Bridge exits.

**Codex Vendor Report**:
- Four agent dots along the bottom edge → map to `AG00`–`AG03` Codex agent slots. 84×84px touch zones, 480ms hold to commit, early release cancels — accidental-touch protected
- Top left/right swipe → inference level, one level per 44px movement, up to six levels per gesture
- Center long-press enters 4-way Radial mode → Codex Micro protocol: right 0.00 / down 0.25 / left 0.50 / up 0.75

This is one of the few **hardware-level Codex Micro protocol implementations** available.

---

### Two UIs

**Classic / Pet**: desktop companion style — time, quota arc, pet animation, affective feedback.

**OpenWatcher V2**: efficiency-first, UI concept inspired by the OpenWatcher project, redesigned for the 466×466 round AMOLED:

- Top semicircle progress bar: semantic gradient — green when quota is ample, shifts to orange and red as it tightens
- Center shows "remaining %" only; "today's usage" on the left — two numbers don't compete for visual center
- 24 cells covering the last four hours, 10 minutes per cell; brightness reflects actual recording time and launch frequency
- Four agent dots at the bottom: color, brightness, and breathing animation driven by Mac-side native state

---

### Battery and Power Saving

Firmware-level power management: dynamic CPU frequency scaling, on-demand microphone activation, differential display refresh, 1-minute brightness dim, 3-minute screen off, 15-minute auto-shutdown without external power.

Real-world test (2026-08-17 to 2026-08-18): from 86% to 0% took **4 hours 20 minutes 51 seconds**, with sustained screen-on and heavy voice use in the final stretch. Full-charge extrapolation: **~5-hour range**.

---

### Install

**Firmware** (requires ESP-IDF v5.5.x + M5Stack StopWatch):

```bash
cd firmware-stopwatch-idf
python3 ./fetch_repos.py
idf.py set-target esp32s3
idf.py build
idf.py flash
```

**macOS Bridge**:

```bash
tools/typeless_bridge/build_stopwatch_ble_bridge.sh
tools/typeless_bridge/install_launch_agent.sh
```

Grant accessibility permission for `StopWatch BLE Bridge` in System Settings → Privacy & Security, then pair `M5Codex-*` in Bluetooth.

**Important**: upgrading from v0.9.x to v0.10.x requires removing the old `M5Codex-*` device in macOS and re-pairing once, due to HID descriptor changes.

---

### Agent-Friendly Development

The repo includes `AGENTS.md` at root — lets Codex and other coding agents immediately understand build commands, code boundaries, and acceptance criteria. `docs/AGENT_DEVELOPMENT_GUIDE.md` organizes everything by "one feature, one set of entry files, one verification method" — you can change just the UI, touch thresholds, key mappings, or mic parameters without reading the whole repo first.

---

This is the most complete "Codex-dedicated hardware peripheral" implementation I've seen — not an oscilloscope or decoration, but a physical interface layer that genuinely changes the vibe coding workflow: eyes on screen, hand on the watch, mouth talking, Codex executing.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
