---
title: "nanoMuse：同一个 Agent 装在你的所有设备上"
titleEn: "nanoMuse: One Personal Agent Across All Your Devices"
description: "浙大团队（Guangyi Liu 等）开源 nanoMuse（GPL-3.0，466 stars）：同一个 Agent 同时跑在 Android、iPhone、Windows、Mac、Linux 和浏览器上，设备之间共享同一段对话线程。Android 版通过屏控 Hands 可以操作任何 App，包括银行、政务等没有 Web 或 API 接口的封闭应用；iOS 屏控暂不支持（TestFlight Beta）。模型自选（BYO API Key 或 Ollama），Sentinel 对删除/发送/支付等不可撤销操作做审批拦截，Relay 可自托管。v1.0.0「Keel」2026-10-09 正式发布，论文 arXiv 2610.08699。"
descriptionEn: "ZJU team (Guangyi Liu et al.) open-sourced nanoMuse (GPL-3.0, 466 stars): the same Agent runs simultaneously on Android, iPhone, Windows, Mac, Linux, and browser, sharing one conversation thread across all devices. Android uses screen-control Hands to operate any app including banking and government apps with no web or API interface; iOS Hands not yet available (TestFlight Beta). BYO model (API key or Ollama). Sentinel intercepts irreversible actions (delete/send/pay) for user approval. Relay is self-hostable. v1.0.0 'Keel' launched 2026-10-09, paper arXiv 2610.08699."
pubDate: 2026-10-09
heroImage: "../../assets/images/nanomuse-zju-personal-agent-multi-device-android-ios-hands-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent", "多设备", "Android", "开源", "本地AI"]
lang: "zh-CN"
wechatTitle: "nanoMuse：多设备共享的本地Agent开源了"
wechatDigest: "GPL-3.0；ZJU浙大；多设备共享Agent；Android屏控封闭App；Relay可自托管"
---

云端 Agent 有一条硬边界：只能碰到有 Web 界面或公开 API 的服务。银行 App、政务 App、企业内网工具——这些东西云上够不着。

nanoMuse 的解题思路是：**把 Agent 放到你的设备本地**，通过屏幕操控（Hands）绕过 API 缺失的限制，同时让你的所有设备共享同一段对话。

GPL-3.0，466 stars，浙江大学团队，2026-10-09 发布 v1.0.0。

GitHub: https://github.com/nano-muse/nanoMuse | arXiv: https://arxiv.org/abs/2610.08699

---

## 多设备共享一个 Agent

nanoMuse 的核心设计：每台设备本地跑一个 Agent，通过 Relay 中继同步同一段会话。登录同一账号的手机、电脑、网页端共享同一 Chat，可以用 `@Mac 帮我打开 XXX App 看一下账单` 这样的方式把任务发到指定设备上执行。

| 平台 | 状态 |
|------|------|
| Android 8.0+（arm64） | 正式发布，Hands 屏控可用 |
| iPhone / iPad | TestFlight Beta，**Hands 不可用** |
| Windows 10+（x64） | 正式发布 |
| macOS 12+（Apple Silicon + Intel） | 正式发布，未公证 |
| Linux x64 | AppImage / .deb / .tar.gz |
| Web 浏览器 | demo.nanomuse.dev |
| Docker | ghcr.io/nano-muse/nanomuse:1.0.0 |

---

## Android 版的关键技术

APK 内打包了一个完整的 Alpine Linux（通过 proot），含 shell、浏览器、MCP、Skills、定时任务，完全本地运行，不依赖外部容器。

屏控 Hands 通过 Android 无障碍服务驱动，可以操作任何 App 的界面——这是云端方案物理上做不到的。

限制：目前只支持 arm64 架构。

---

## Relay：会话中继的隐私边界

Relay 负责两件事：账号注册和设备间**会话文本**传输。重要的区分：

- 会话**文本**经过 Relay（如使用社区 Relay，则文本经过第三方服务器）
- **文件和截图**不经过 Relay，只留在执行任务的本地设备上

如果对隐私要求高，可以用 `scripts/self-host.sh` 或 Docker Compose 自托管 Relay，会话文本就完全在自己控制的服务器上。

---

## Sentinel：不可撤销操作要确认

nanoMuse 内置 Sentinel 安全层：**删除、发送、支付**等不可撤销操作在执行前会主动征询用户确认，不会 Agent 自己就直接跑完。

这是 Agent 全自动操作真实 App 时的关键安全机制——工具调用结果没法 Ctrl-Z。

---

## 模型：完全自带

nanoMuse 不绑定任何模型提供商：

- 带自己的 API Key（OpenAI、Anthropic 等）
- 或者连接本地 Ollama 实例
- 社区 Relay 有限量免费额度（Relay 会提供基础模型访问），额度耗尽后需自备

---

## Memory 即 Markdown 文件

身份配置、用户偏好、唤醒计划均以 Markdown 文件存储在本地，用户可以直接读写。没有私有格式，没有数据库，改起来透明。

---

## 已知边界

- iOS 屏控 Hands 暂不可用（TestFlight 阶段）
- Android 只支持 arm64，Linux 只支持 x64
- macOS 未通过 Apple 公证，首次需右键 → 打开
- 不支持图片/视频模态的模型 Provider 会关闭对应功能
- 论文（arXiv 2610.08699）**没有 Benchmark 实验数据**，优势是理论分析而非量化验证
- 使用社区 Relay 时，会话文本经过第三方服务器

---

## 和云端 Agent（Muse 类产品）的核心区别

| | 云端 Agent（如 Meta Muse） | nanoMuse |
|---|---|---|
| App 覆盖 | 有 Web/API 的服务 | 任意 App（通过屏控） |
| 数据流转 | 所有操作在云端虚拟机 | 文件/截图留本地 |
| 多设备 | 云端单点 | 每台设备本地跑，Relay 同步 |
| 模型选择 | 厂商绑定 | BYO Key/Ollama |
| 自托管 | 不可 | Relay 可自托管 |

---

## 一句话说清楚

nanoMuse 把一个本地 Agent 同时部署到你的手机、电脑、平板和浏览器上，多设备共享同一段对话，Android 屏控可以操作没有 API 的封闭 App，Relay 可自托管，GPL-3.0。iOS 屏控暂不支持，整体仍是 v1.0 早期阶段。

---

> GPL-3.0。浙江大学 Guangyi Liu、Yong Liu、Jiangning Zhang，v1.0.0"Keel"，2026-10-09 发布，arXiv 2610.08699。开源仅供学习参考。

---

<!--EN-->

## nanoMuse: One Personal Agent Across All Your Devices

Cloud agents have a hard boundary: they can only reach services with web interfaces or public APIs. Banking apps, government apps, enterprise internal tools — the cloud can't touch them.

nanoMuse's approach: **put the Agent on the device itself**, use screen-control (Hands) to work around the missing API layer, and let all your devices share a single conversation thread.

GPL-3.0, 466 stars, Zhejiang University team, v1.0.0 released 2026-10-09.

GitHub: https://github.com/nano-muse/nanoMuse | arXiv: https://arxiv.org/abs/2610.08699

---

### Multi-Device, One Agent

Core design: each device runs a local Agent instance, synchronized through a Relay to share the same session. Devices logged into the same account (phone, PC, web) share one Chat. You can direct tasks with `@Mac check the balance in XXX app` to route execution to a specific device.

| Platform | Status |
|----------|--------|
| Android 8.0+ (arm64) | Released, Hands (screen control) works |
| iPhone / iPad | TestFlight Beta, **Hands unavailable** |
| Windows 10+ (x64) | Released |
| macOS 12+ (Apple Silicon + Intel) | Released, not notarized |
| Linux x64 | AppImage / .deb / .tar.gz |
| Web browser | demo.nanomuse.dev |
| Docker | ghcr.io/nano-muse/nanomuse:1.0.0 |

---

### Android: What's Inside the APK

The APK ships a full Alpine Linux instance (via proot) — shell, browser, MCP, Skills, cron tasks, all running locally without an external container.

Hands uses Android accessibility services to operate any app's UI — something that is physically impossible for a cloud agent to do.

Limitation: arm64 only.

---

### Relay: The Privacy Boundary

The Relay handles account registration and session **text** relay. Important distinction:

- Conversation **text** passes through Relay (community Relay = third-party server)
- **Files and screenshots** stay on the local device that executed the task

Privacy-sensitive deployments: self-host the Relay with `scripts/self-host.sh` or Docker Compose — conversation text never leaves your servers.

---

### Sentinel: Gating Irreversible Actions

nanoMuse has a built-in Sentinel security layer: **delete, send, payment** actions require explicit user confirmation before executing. The Agent doesn't just run to completion unattended.

This is the essential safety mechanism for an Agent operating real apps — there's no Ctrl-Z for tool call results.

---

### Model: Fully BYO

No vendor lock-in:
- Bring your own API key (OpenAI, Anthropic, etc.)
- Connect to a local Ollama instance
- Community Relay provides a limited free model quota; quota depletes → need your own key

---

### Known Limits

- iOS Hands not available (TestFlight stage)
- Android arm64 only, Linux x64 only
- macOS not notarized (right-click → Open on first launch)
- Image/video modalities disabled if chosen model provider doesn't support them
- Paper (arXiv 2610.08699) has **no benchmark experiments** — theoretical analysis only
- Community Relay: conversation text goes through third-party servers

---

### TL;DR

nanoMuse deploys a local Agent across phone, PC, tablet, and browser simultaneously, sharing one conversation thread. Android screen-control reaches any app without an API. Relay is self-hostable. GPL-3.0. iOS screen-control not yet available; overall still early (v1.0).

---

> GPL-3.0. Zhejiang University, Guangyi Liu, Yong Liu, Jiangning Zhang. v1.0.0 "Keel", released 2026-10-09. arXiv 2610.08699. For reference only.
