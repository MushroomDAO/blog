---
title: 'OpenDisplay：免费开源 Sidecar 替代，iPhone/iPad/旧 Mac 变真副屏'
titleEn: "OpenDisplay: Free Open-Source Sidecar Alternative — iPhone, iPad, or Spare Mac as a True Second Monitor"
description: "Sidecar 要同一 Apple ID、不支持 iPhone；Duet 改了订阅；Luna 要加密狗。OpenDisplay 全都不要：免费、开源、无账号、无加密狗，USB 或 WiFi，H.264 硬件编码，Retina HiDPI，触控输入，旧 Mac 也能当副屏。GPL-3.0，macOS 私有 API CGVirtualDisplay。"
descriptionEn: "Sidecar needs the same Apple ID and doesn't support iPhones. Duet went subscription. Luna needs a dongle. OpenDisplay needs none of that: free, open-source, no account, no dongle, USB or WiFi, hardware H.264, Retina HiDPI, touch input, spare Mac as receiver. GPL-3.0, uses private macOS API CGVirtualDisplay."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Tech-News"
tags: ["open-source", "macOS", "iPhone", "iPad", "second-monitor", "H264", "privacy", "self-hosted", "CGVirtualDisplay"]
heroImage: "../../assets/images/opendisplay-free-open-source-sidecar-iphone-ipad-second-monitor-banner.jpg"
---

> 📌 开源仓库：peetzweg/opendisplay
> GitHub：https://github.com/peetzweg/opendisplay
> iOS TestFlight：https://testflight.apple.com/join/3NYaY11c
> Mac 下载：https://github.com/peetzweg/opendisplay/releases/latest
> License：GPL-3.0 | 作者：Philip Poloczek

---

把一台 iPhone、iPad 或旧 Mac 变成第二块屏幕，这个需求解决方案很多，但每个都有代价：

- **Apple Sidecar**：免费，但两台设备必须登同一 Apple ID，不支持 iPhone，对硬件组合有要求。
- **Duet Display**：改了订阅制。
- **Luna Display**：要买一个硬件加密狗。

OpenDisplay 是缺失的选项——**免费、开源、无账号、无加密狗、无订阅**，你手里已有的 iOS 设备直接变真副屏。

---

## 功能对比

| | OpenDisplay | Apple Sidecar | Duet Display | Luna Display |
|---|---|---|---|---|
| 价格 | **免费开源** | 免费 | 订阅 | $$$ + 加密狗 |
| iPhone 作副屏 | ✅ | ❌（仅 iPad） | ✅ | ✅ |
| 不同 Apple ID | ✅ | ❌ | ✅ | ✅ |
| USB 有线 | ✅ | ✅ | ✅ | ❌ |
| 真扩展屏（非镜像） | ✅ | ✅ | ✅ | ✅ |
| 触控输入 | ✅ | ✅ | ✅ | ✅ |
| 自托管 / 可审计 | ✅ | — | ❌ | ❌ |

---

## 工作原理

技术路径很清晰：

```
Mac（发送端）                              iPhone/iPad（接收端）
CGVirtualDisplay  ← macOS 认为接了一台显示器
  → ScreenCaptureKit（捕获虚拟屏内容）
  → VideoToolbox H.264（硬件实时编码，无 B 帧）
  → TCP [4字节长度][Annex B帧]  ═══════→  NWListener :9000
                                            → AVSampleBufferDisplayLayer 解码渲染
  ← JSON 控制消息（hello、触摸、滚动）═══
  → CGEvent 注入（点击 / 拖拽 / 滚动）
```

**手机监听、Mac 主动连接**——这个顺序使同一套代码同时支持 USB 和 WiFi 两种传输。

USB 模式走 macOS 内置的 `usbmuxd` 守护进程，不需要任何第三方工具。WiFi 模式靠 Bonjour 自动发现，打开 iPhone app 就能在 Mac 端下拉菜单看到设备。

---

## 核心特性

**真扩展屏，不是镜像**
macOS 把设备识别为一台真正的第二显示器，可以在系统设置里拖动排列，像普通显示器一样拖窗口过去。镜像模式也支持，作为可选项。

**USB 有线，最低延迟**
走 Mac 内置的 `usbmuxd`，通过 Lightning/USB-C 数据线直连。最高质量预设码率 18 Mb/s，远低于 USB 2.0 的 480 Mb/s 上限，USB 2.0 数据线足够用。注意：纯充电线不行，必须是支持数据传输的线。

**WiFi 零配置**
iPhone 通过 Bonjour 广播自己，Mac 端直接从下拉菜单选。USB 延迟更低，WiFi 不用线——各有用途。

**Retina / HiDPI**
虚拟显示器按设备面板分辨率的 @2x 创建，文字锐利，不糊。旋转设备后，虚拟显示器随之重建为竖向或横向。

**触控输入**
iPhone 变成 Mac 的触摸屏：点击等于鼠标左键，拖拽支持，双指滚动手感接近触控板。Apple Pencil 压感/倾斜在路线图中。

**旧 Mac 也能当副屏**
另一台 Mac 装 `OpenDisplay Receiver`（macOS 12+，约 2015 年起的 Mac 基本都能跑），就能作为主 Mac 的扩展屏。接线方式：Thunderbolt/USB4 电缆（建立 Thunderbolt Bridge 网络）、以太网、或近期 macOS 的普通 USB-C 数据线。

---

## 流水线技术细节

- **H.264**：VideoToolbox 硬件编码，实时模式，无 B 帧（降低延迟）
- **传输**：TCP_NODELAY，帧丢弃背压 + 关键帧恢复
- **解码**：`AVSampleBufferDisplayLayer`
- **帧率**：延迟目标优先，内置性能 overlay
- **自动更新**：Sparkle 框架，EdDSA 签名 + Apple 公证双重验证

整个协议在仓库里的 `PROTOCOL.md` 完整规范，有人已经基于此实现了 Android 接收端、Linux 发送端、iOS 12 旧设备接收端。

---

## 安装

需要两个 app：Mac 端（捕获并发送）+ iOS 端（接收并显示）。

**Mac app**：从 GitHub Release 下载 `OpenDisplay.dmg`，有 Developer ID 签名和 Apple 公证，直接双击打开，macOS 14+。要把旧 Mac 当副屏用，下载 `OpenDisplayReceiver.dmg`，macOS 12+ 即可。

**iOS app**：iOS 16+（含 16.7.x 旧设备）。目前通过 TestFlight 公测，App Store 正式上架在路线图中。

```bash
# 从源码构建 Mac app
brew install xcodegen
git clone https://github.com/peetzweg/opendisplay.git
cd opendisplay
echo "DEVELOPMENT_TEAM=你的TeamID" > .env
./generate.sh
xcodebuild -project OpenSidecar.xcodeproj -scheme OpenSidecarMac \
  -configuration Debug -derivedDataPath build build
```

---

## 权限说明

| 位置 | 权限 | 用途 | 缺失后果 |
|------|------|------|----------|
| Mac | 屏幕录制 | 捕获虚拟显示器 | 手机黑屏 |
| Mac | 辅助功能 | 触控 / 滚动注入 | 触摸无响应 |
| Mac | 本地网络 | WiFi 发现 | 连接菜单看不到设备 |
| iPhone | 本地网络 | WiFi 发现 | Mac 找不到手机 |

本地网络权限只在 WiFi 模式下需要，USB 模式不依赖它。

---

## 私有 API 说明

`CGVirtualDisplay` 是 CoreGraphics 的私有 API，BetterDisplay 和 DeskPad 也用这个。正因如此，Mac app 目前无法上 App Store，只能从 GitHub 下载。捕获和串流流水线本身用的都是公开 API。

macOS 大版本更新后存在被 break 的风险，和其他虚拟显示器产品面临相同的不确定性。

---

## 路线图（摘要）

- 加密 WiFi 传输 + 配对码
- Apple Pencil 压感和倾斜
- 右键和多指手势
- 硬件键盘直通
- HEVC 编码
- 音频转发
- iOS App Store 正式上架
- 菜单栏 app 模式 + 自动连接

---

## 许可与背景

GPL-3.0，Copyright 2026 Philip Poloczek。修改后的版本必须保持开源并保留原作者署名，改进流回社区而不是进入闭源分叉。v0.4.x 及以前版本为 MIT 授权，仍按原条款可用。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: peetzweg/opendisplay
> GitHub: https://github.com/peetzweg/opendisplay
> iOS TestFlight: https://testflight.apple.com/join/3NYaY11c
> Mac download: https://github.com/peetzweg/opendisplay/releases/latest
> License: GPL-3.0 | Author: Philip Poloczek

---

Every solution for turning an iPhone, iPad, or spare Mac into a second display has a catch:

- **Apple Sidecar**: Free, but requires the same Apple ID on both devices, doesn't support iPhones, and only works on supported hardware pairs.
- **Duet Display**: Moved to a subscription.
- **Luna Display**: Requires a hardware dongle.

OpenDisplay is the missing option — **free, open-source, no account, no dongle, no subscription**. Use the iOS device you already own as a true second display.

---

## Feature Comparison

| | OpenDisplay | Apple Sidecar | Duet Display | Luna Display |
|---|---|---|---|---|
| Price | **Free, open source** | Free | Subscription | $$$ + dongle |
| iPhone as display | ✅ | ❌ (iPad only) | ✅ | ✅ |
| Different Apple IDs | ✅ | ❌ | ✅ | ✅ |
| Wired (USB) | ✅ | ✅ | ✅ | ❌ |
| True extension (not mirror) | ✅ | ✅ | ✅ | ✅ |
| Touch input | ✅ | ✅ | ✅ | ✅ |
| Self-hosted / auditable | ✅ | — | ❌ | ❌ |

---

## How It Works

```
MAC (sender)                                      iPHONE / iPAD (receiver)
CGVirtualDisplay  ← macOS believes a monitor is attached
  → ScreenCaptureKit (capture the virtual display)
  → VideoToolbox H.264 (hardware, real-time, no B-frames)
  → TCP [4-byte length][Annex B frame]  ═══════→  NWListener :9000
                                                    → AVSampleBufferDisplayLayer
  ← JSON control messages (hello, touch, scroll) ═══
  → CGEvent injection (click / drag / scroll)
```

**The phone listens, the Mac connects** — this ordering makes the same code work over both USB (via macOS's built-in `usbmuxd`) and WiFi.

---

## Core Features

**True display extension, not mirroring**
macOS treats the device as a real second monitor. Arrange it in System Settings, drag windows onto it. Mirroring is also available as an option.

**USB wired, lowest latency**
Streams over the Lightning/USB-C cable via macOS's built-in `usbmuxd` — no third-party tools needed. Highest quality preset uses 18 Mb/s, well below USB 2.0's 480 Mb/s limit. Requires a data-capable cable (charge-only cables don't work).

**WiFi with zero config**
The iPhone advertises itself via Bonjour. Pick it from a dropdown on the Mac. USB has lower latency; WiFi needs no cable.

**Retina / HiDPI**
The virtual display is created at exactly half the device's native panel resolution in points (@2x). Text is sharp. Rotating the device rebuilds the virtual display as a vertical or horizontal monitor at native resolution.

**Touch input built in**
iPhone becomes a touchscreen for macOS: tap to click, drag to drag, two-finger scroll that feels like a trackpad. Apple Pencil support is on the roadmap.

**Spare Mac as a display**
Install `OpenDisplay Receiver` (macOS 12+, most Macs from ~2015 onward) on an old Mac and it becomes a real extended Retina display. Connect via Thunderbolt/USB4 cable, Ethernet, or (on recent macOS) a plain USB-C data cable.

---

## Pipeline Details

- **H.264**: VideoToolbox hardware encode, real-time mode, no B-frames (minimizes latency)
- **Transport**: TCP_NODELAY, frame-drop backpressure with keyframe recovery
- **Decode**: `AVSampleBufferDisplayLayer`
- **Auto-update**: Sparkle framework with EdDSA signature + Apple notarization double verification

The full protocol is specified in `PROTOCOL.md`. Community members have already built Android receivers, a Linux sender, and an iOS 12 legacy receiver against the spec.

---

## Installation

You need two apps: a Mac app (captures and sends) and an iOS app (receives and displays).

**Mac app**: Download `OpenDisplay.dmg` from the latest GitHub Release. Signed with Developer ID and notarized by Apple — opens with a double-click on macOS 14+. For a spare Mac as the display, download `OpenDisplayReceiver.dmg` instead (macOS 12+).

**iOS app**: Requires iOS 16+ (including the 16.7.x line for older devices). Currently available via public TestFlight beta; App Store release is on the roadmap.

```bash
# Build the Mac app from source
brew install xcodegen
git clone https://github.com/peetzweg/opendisplay.git
cd opendisplay
echo "DEVELOPMENT_TEAM=YOUR_TEAM_ID" > .env
./generate.sh
xcodebuild -project OpenSidecar.xcodeproj -scheme OpenSidecarMac \
  -configuration Debug -derivedDataPath build build
```

---

## Permission Checklist

| Location | Permission | Purpose | If Missing |
|----------|------------|---------|------------|
| Mac | Screen Recording | Capture the virtual display | Black screen on phone |
| Mac | Accessibility | Touch/scroll injection | Taps do nothing |
| Mac | Local Network | WiFi discovery | No device in Connection menu |
| iPhone | Local Network | WiFi discovery | Mac can't find the phone |

Local Network permissions are only needed for WiFi mode — USB works without them.

---

## On the Private API

`CGVirtualDisplay` is a private CoreGraphics API — the same one used by BetterDisplay and DeskPad. That's exactly why the Mac app can't ship on the App Store and lives on GitHub instead. The capture and streaming pipeline uses only public APIs.

It may break on a macOS major update — the same risk that applies to every virtual display product.

---

## Roadmap Highlights

- Encrypted WiFi transport with pairing code
- Apple Pencil with pressure and tilt
- Right-click and multi-touch gestures
- Hardware keyboard passthrough
- HEVC encoding
- Audio forwarding
- App Store release of the iOS app
- Menu bar app mode with auto-connect

---

## License

GPL-3.0, Copyright 2026 Philip Poloczek. Modified versions must remain open source under the same license with the original attribution — improvements flow back to everyone rather than into closed forks. Versions through v0.4.x were MIT-licensed and remain available under those terms.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
