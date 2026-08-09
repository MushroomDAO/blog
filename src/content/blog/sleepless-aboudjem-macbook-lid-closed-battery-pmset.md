---
title: "Sleepless：盖上盖子不睡觉——用 pmset 解决 Mac 最顽固的痛点"
titleEn: "sleepless-aboudjem-macbook-lid-closed-battery-pmset"
description: "Aboudjem/Sleepless，Swift，MIT。macOS 原生菜单栏工具，用 pmset disablesleep 让 MacBook 盖盖后仍保持唤醒——不需要外接显示器，不需要电源，有电量底线和自动关闭定时器。Amphetamine/KeepingYouAwake/caffeinate 都解决不了这个问题；Sleepless 是唯一用对了机制的开源替代方案。"
descriptionEn: "Aboudjem/Sleepless, Swift, MIT. Native macOS menu-bar app that uses pmset disablesleep to keep a MacBook awake with the lid closed — no external display, no power cable required. Battery floor and auto-off timer so it can't drain your Mac. The only open-source tool that uses the right mechanism; Amphetamine, KeepingYouAwake, and caffeinate all fail at lid-closed."
pubDate: "2026-08-09"
updatedDate: "2026-08-09"
category: "Tech-News"
tags: ["macOS", "工具", "Mac", "开源", "Swift", "效率", "Mycelium"]
heroImage: "../../assets/images/sleepless-aboudjem-macbook-lid-closed-battery-pmset-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

你在跑一个通宵任务——模型训练、大文件下载、渲染、Agent 流程——想盖上 MacBook 的盖子，明天早上拿到结果。但盖上盖子，Mac 就睡了。

这个问题困扰了很多 Mac 用户。Amphetamine 不能稳定解决它。KeepingYouAwake 设计上就不支持。`caffeinate` 命令行更没用。

Sleepless 是唯一用对了机制的开源解法。

GitHub: https://github.com/Aboudjem/Sleepless | ⭐ 40 | MIT | Swift

---

## 为什么其他工具都解决不了这个问题

这不是其他工具做得不好，是它们用了错误的机制：

**Amphetamine、KeepingYouAwake、caffeinate** 都依赖 macOS 的 **power assertions**（电源断言）——这个机制能阻止空闲睡眠计时器触发，但**无法覆盖盖盖这个硬件触发事件**。KeepingYouAwake 直接包装了 `caffeinate`，文档里就写明了不支持盖盖唤醒（[issue #66](https://github.com/newmarcel/KeepingYouAwake/issues/66)）。Amphetamine 虽然文档里提到了 closed-display 模式，但在 Apple Silicon 上切换电源状态时被广泛报告会失效，而且它是闭源的。

Sleepless 用的是另一个机制：**`pmset disablesleep`**，它直接设置内核里的 `SleepDisabled` 标志。这是一个更底层的开关，能覆盖包括盖盖在内的所有睡眠触发。在 macOS 26.3、Apple Silicon（M1/M2/M3）上验证有效。

验证方式：
```bash
pmset -g | grep SleepDisabled   # 应显示 SleepDisabled 1
```

---

## 功能

| | |
|---|---|
| ☕ **一个开关** | 点菜单栏的杯子图标，拨动开关 |
| ⏲️ **自动关闭定时器** | 1小时或2小时，倒计时结束后自动关闭 |
| 🔋 **电量底线** | 电量降到 5–50%（默认15%）时自动关闭 |
| 🪫 **低电量模式联动** | 使用电池时，低电量模式开启则自动退让 |
| 🖥️ **不需要外接显示器** | 盖盖、用电池、无显示器、无 HDMI 转接头 |
| 🚀 **登录启动** | 可选，默认关闭，始终以待机状态启动 |
| 🪶 **极小 + 原生** | 单个 AppKit 文件，无 Dock 图标、无守护进程、无 kext |

**菜单栏图标含义**：空杯 = 关闭 · 满杯 = 唤醒（充电）· 满杯+点 = 唤醒中（电池，倒计时进行中）

---

## 实际用途

- **跑通宵任务盖盖**：Agent 流程、编译构建、视频渲染、ML 训练
- **用 Mac 当热点放包里**：热点保持开启不需要 Mac 亮着屏幕
- **大文件传输**：下载、上传、备份跑完不用守着
- **保持本地服务或 SSH 连接**：让其他设备继续访问你的 Mac

---

## 权限设计

`pmset disablesleep` 需要 `sudo`，但 GUI 应用不能弹密码框。Sleepless 的解法：安装时在 sudoers 里添加一条**精确范围**的规则，只允许执行两条命令：

```
<你> ALL=(root) NOPASSWD: /usr/bin/pmset -a disablesleep 0, /usr/bin/pmset -a disablesleep 1
```

- **无法扩大**：sudoers 按参数字面量匹配，没有通配符
- **没有可劫持的部分**：无守护进程，无辅助脚本，无 shell，直接调用 `/usr/bin/pmset`
- **随时可撤销**：重启、电量底线、定时器、或 `./uninstall.sh` 都能恢复

```bash
./uninstall.sh   # 删除 App、登录项和 sudoers 规则，并验证规则已清除
```

安全方面：build provenance 经过 SLSA 认证，SHA-256 校验文件随 Release 发布，可用 `gh attestation verify` 验证。

---

## 与其他工具对比

| | **Sleepless** | Amphetamine | KeepingYouAwake | `caffeinate` |
|---|:---:|:---:|:---:|:---:|
| 盖盖唤醒，无外接显示器 | ✅ | ⚠️ Apple Silicon 不稳定 | ❌ 设计不支持 | ❌ |
| 电池供电 | ✅ | ✅ | ✅（盖开）| ⚠️ |
| 自动关闭定时器 | ✅ | ✅ | ✅ | ❌ |
| 低电量自动关闭 | ✅ | ✅ | ✅ | ❌ |
| 开源 | ✅ MIT | ❌ App Store | ✅ MIT | Apple |

---

## 安装

```bash
# Homebrew（推荐）
brew install --cask aboudjem/tap/sleepless
/Applications/Sleepless.app/Contents/Resources/grant.sh   # 一次性权限授予
```

或者从 [GitHub Releases](https://github.com/Aboudjem/Sleepless/releases/latest) 下载 zip，解压到 `/Applications`，在「系统设置 → 隐私与安全性」里点「仍要打开」（应用是 ad-hoc 签名，无付费 Apple Developer ID）。

也可以从源码构建（跳过 Gatekeeper）：

```bash
git clone https://github.com/Aboudjem/Sleepless.git
cd Sleepless
./install.sh
```

---

## 关于这个项目

Sleepless 故意保持小：单个 AppKit 文件，无 Dock 图标，无守护进程，无内核扩展。它解决一个非常具体的问题，解决得很干净。作者 Adam Boudjemaa 把所有安全细节、审计指南和完整的威胁模型都放在 `SECURITY.md` 和 `docs/AUDIT.md` 里，README 有六种语言版本，基础设施层面也相当认真——对一个 40 星的个人工具来说不常见。

如果你经常需要盖上 MacBook 跑任务，这是目前唯一真正解决问题的开源工具。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Sleepless: Lid Closed, Mac Awake — The One Tool That Uses the Right Mechanism

*by Mycelium Protocol*

---

You're running an overnight job — model training, a large download, a render, an agent workflow. You want to close your MacBook lid and get the result in the morning. But closing the lid puts the Mac to sleep.

This problem has frustrated Mac users for years. Amphetamine can't reliably solve it. KeepingYouAwake doesn't support it by design. `caffeinate` doesn't either.

Sleepless is the only open-source tool that uses the right mechanism.

GitHub: https://github.com/Aboudjem/Sleepless | ⭐ 40 | MIT | Swift

---

### Why Other Tools Don't Work

This isn't a quality problem — it's a mechanism problem.

**Amphetamine, KeepingYouAwake, and caffeinate** all rely on macOS **power assertions**, which block the idle sleep timer but **cannot override the hardware lid-close trigger**. KeepingYouAwake wraps `caffeinate` and documents it can't do lid-closed ([#66](https://github.com/newmarcel/KeepingYouAwake/issues/66)). Amphetamine mentions a closed-display mode but is widely reported to break on Apple Silicon when the power source changes — and it's closed source.

Sleepless uses a different mechanism: **`pmset disablesleep`**, which sets the kernel's `SleepDisabled` flag directly. This overrides all sleep triggers including the lid close. Confirmed working on macOS 26.3 on Apple Silicon (M1/M2/M3).

Verify it yourself:
```bash
pmset -g | grep SleepDisabled   # should read: SleepDisabled 1
```

---

### Features

| | |
|---|---|
| ☕ **One switch** | Click the menu-bar cup, flip the toggle |
| ⏲️ **Auto-off timer** | 1h or 2h with live countdown, then off |
| 🔋 **Battery floor** | Auto-off at 5–50% on battery (default 15%) |
| 🪫 **Low Power Mode** | Steps aside when LPM is on, on battery |
| 🖥️ **No dongle** | Lid closed, battery power, no monitor, no HDMI adapter |
| 🚀 **Launch at login** | Optional, off by default, always starts idle |
| 🪶 **Tiny + native** | Single AppKit file, no Dock icon, no daemon, no kext |

**Menu-bar glyph**: empty cup = off · full cup = awake (charging) · full cup + dot = awake on battery (timer live)

---

### What You Can Do With It

- **Lid-closed overnight tasks**: agent runs, builds, renders, ML training
- **Hotspot from your bag**: share internet without the screen on
- **Unattended file transfers**: downloads, uploads, backups running to completion
- **Keep a local server or SSH session reachable**: other devices can keep accessing your Mac

---

### Permission Design

`pmset disablesleep` needs `sudo`, and a GUI app can't prompt for a password. Sleepless's solution: a tightly scoped sudoers rule installed at setup time, covering exactly two commands:

```
<you> ALL=(root) NOPASSWD: /usr/bin/pmset -a disablesleep 0, /usr/bin/pmset -a disablesleep 1
```

- **Can't be widened**: sudoers matches arguments literally, no wildcards
- **Nothing to hijack**: no daemon, no helper script, no shell — calls `/usr/bin/pmset` directly
- **Always reversible**: reboot, battery floor, timer, or `./uninstall.sh` — which proves the grant is gone

Build provenance is SLSA-attested. SHA-256 checksums ship with every release. Verify without an Apple account:
```bash
shasum -a 256 -c SHA256SUMS
gh attestation verify Sleepless-*.zip -R Aboudjem/Sleepless
```

---

### Comparison

| | **Sleepless** | Amphetamine | KeepingYouAwake | `caffeinate` |
|---|:---:|:---:|:---:|:---:|
| Awake, lid closed, no monitor | ✅ | ⚠️ unreliable on AS | ❌ by design | ❌ |
| On battery | ✅ | ✅ | ✅ (lid open) | ⚠️ |
| Auto-off timer | ✅ | ✅ | ✅ | ❌ |
| Auto-off on low battery | ✅ | ✅ | ✅ | ❌ |
| Open source | ✅ MIT | ❌ | ✅ MIT | Apple |

---

### Install

```bash
# Homebrew (recommended)
brew install --cask aboudjem/tap/sleepless
/Applications/Sleepless.app/Contents/Resources/grant.sh   # one-time permission grant
```

Or download from [Releases](https://github.com/Aboudjem/Sleepless/releases/latest), unzip to `/Applications`, and approve via **System Settings → Privacy & Security → Open Anyway** (ad-hoc signed — no paid Apple Developer ID).

Build from source to skip Gatekeeper entirely:
```bash
git clone https://github.com/Aboudjem/Sleepless.git && cd Sleepless && ./install.sh
```

---

### What Makes This Notable

Sleepless stays deliberately small — a single AppKit file, no Dock icon, no daemon, no kernel extension. It solves one specific problem cleanly. The author, Adam Boudjemaa, published a full threat model (`SECURITY.md`), an audit guide (`docs/AUDIT.md`), SHA-256 checksums and SLSA build attestation, and a README in six languages — unusual rigor for a 40-star personal tool.

If you regularly need to run tasks with the lid closed, this is the only open-source option that actually works.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
