---
title: "Diction：iOS 语音键盘的自托管网关开源了"
titleEn: "Diction: Open-Source Self-Hosted Gateway for iOS Voice Dictation Keyboard"
description: "DictionLabs 开源了 Diction 的自托管后端网关（MIT，Go 实现）。Diction 是一个 iOS 通用语音键盘——Apple 原生听写被沙箱限制在单个 App 内，Diction 注册为自定义键盘绕过这个限制，可以在任意文本框里语音输入。支持三种模式：纯本地（on-device，99 种语言）、Diction One 付费云、自托管网关。网关走 WebSocket，兼容 OpenAI Transcription API 规范，可以挂任意 STT 后端（Whisper、Parakeet 等），端到端 AES-256-GCM 加密。可选 LLM 后处理。自托管 `docker compose up` 即启动，贴到 iOS App 设置里即可。早期项目，solo developer，'5x faster' 无 benchmark 支撑，App Store 评分还没积累，自报数字需打折。"
descriptionEn: "DictionLabs open-sourced the self-hosted backend gateway for Diction (MIT, Go). Diction is a universal iOS voice keyboard — Apple's native dictation is sandboxed per-app; Diction registers as a custom keyboard to circumvent that, enabling voice input in any text field. Three modes: on-device (99 languages, fully offline), Diction One paid cloud, or self-hosted gateway. The gateway uses WebSocket, speaks the OpenAI Transcription API spec, plugs into any STT backend (Whisper, Parakeet, etc.), and does AES-256-GCM end-to-end encryption. Optional LLM post-processing. Self-hosting: `docker compose up`, paste the URL into the iOS app. Early-stage project, solo developer, '5x faster' claim has no benchmark, App Store ratings not yet accumulated."
pubDate: 2026-10-08
heroImage: "../../assets/images/diction-ios-keyboard-stt-self-hosted-gateway-banner.jpg"
category: "Tech-Experiment"
tags: ["iOS", "语音转文字", "开源工具", "自托管", "隐私工具"]
lang: "zh-CN"
wechatTitle: "Diction：iOS键盘把语音转文字开源了"
wechatDigest: "MIT Go；本地/云/自托管三模式；兼容OpenAI STT API；AES-256加密"
---

Apple 的原生听写有一个限制：它被沙箱隔离在当前 App 内，切 App 就失效。

Diction 绕开了这个限制。它注册成 iOS 系统键盘，作为自定义键盘挂载后，语音输入在**任意文本框**里都能用——备忘录、微信、邮件、终端，都没区别。

本次开源的是 Diction 的**自托管后端网关**。

GitHub: https://github.com/DictionLabs/Diction | MIT | Go

---

## 三种模式

| 模式 | 部署 | 隐私 | 费用 |
|------|------|------|------|
| 本地（on-device） | 无服务器，纯离线 | 最高 | 免费 |
| Diction One 云 | 官方托管 | 第三方处理 | 付费订阅 |
| 自托管网关 | 自备服务器 | 完全自控 | 基础设施自担 |

本地模式支持 99 种语言，完全离线，但依赖设备端模型精度。自托管模式精度取决于你挂的 STT 后端。

---

## 网关架构

网关是一个 Go 服务，协议是 **WebSocket 流式传输**，接口兼容 OpenAI Transcription API 规范。

这意味着任何实现了这套 API 的 STT 后端都可以挂上去。DictionLabs 官方发布了两个 Docker 镜像：

- **`dictionlabs/whisper-server`** — 基于 Whisper 的通用多语言方案
- **`dictionlabs/parakeet`** — NVIDIA Parakeet 模型，针对 25 种欧洲语言优化

安全层：键盘与网关之间端到端 **AES-256-GCM 加密**，录音不明文传输。

可选功能：LLM 后处理，对转录文本做润色或格式化。

---

## 自托管部署

```bash
docker compose up
```

启动后，在 iOS 的 Diction App 设置里填入网关地址，绑定完成。

---

## 诚实评估

**没有 benchmark 支撑的数字**：项目标榜"5x faster"，没有说比谁快、在什么条件下测的。这是未经证实的营销说法。

**App Store 评分积累不足**：产品还在非常早期，公开评价很少，无法从用户反馈判断真实体验。

**Solo developer 风险**：单人维护，长期支持和路线图不确定。

**语言覆盖依赖后端选择**：Parakeet 只覆盖 25 种欧洲语言，中文等亚洲语言需要用 Whisper 路径，精度和延迟自行评估。

**无遥测是设计选择**：对隐私有利，但也意味着没有公开的用量数据来验证项目活跃度。

---

## 适合谁

- 需要跨 App 语音输入、不信任云端 STT 的用户
- 想用私有服务器替代 Apple 沙箱的开发者
- 希望自控 STT 后端（精度、语言、成本）的场景

---

> MIT 许可。DictionLabs 开发，网关代码 GitHub 已上线，iOS App 在 App Store（ID: 6759807364）。自报数字需打折核实。开源仅供学习参考。

---

<!--EN-->

## Diction: Open-Source Self-Hosted Gateway for iOS Voice Dictation Keyboard

Apple's native dictation has a hard constraint: it's sandboxed per-app. Switch apps, it stops.

Diction works around this. It registers as an iOS system keyboard — once installed, voice input works in **any text field**: Notes, WhatsApp, email, terminal. No exceptions.

What just went open source is Diction's **self-hosted backend gateway**.

GitHub: https://github.com/DictionLabs/Diction | MIT | Go

---

### Three Modes

| Mode | Deployment | Privacy | Cost |
|------|-----------|---------|------|
| On-device | No server, fully offline | Maximum | Free |
| Diction One cloud | Official hosting | Third-party processes audio | Paid subscription |
| Self-hosted gateway | Your own server | Fully self-controlled | Infrastructure at your cost |

On-device mode supports 99 languages, completely offline. Self-hosted accuracy depends on your chosen STT backend.

---

### Gateway Architecture

The gateway is a Go service using **WebSocket streaming**, implementing the OpenAI Transcription API spec.

This means any STT backend that implements this spec can be plugged in. DictionLabs publishes two official Docker images:

- **`dictionlabs/whisper-server`** — general-purpose multilingual via Whisper
- **`dictionlabs/parakeet`** — NVIDIA Parakeet model, optimized for 25 European languages

Security layer: **AES-256-GCM end-to-end encryption** between the keyboard and gateway. Audio never travels in plaintext.

Optional: LLM post-processing pass on transcribed text for cleanup or formatting.

---

### Self-Hosting

```bash
docker compose up
```

Then paste the gateway URL into Diction's iOS app settings. Done.

---

### Honest Assessment

**Unverified claim**: The project claims "5x faster" with no stated comparison baseline or benchmark methodology. Treat as marketing copy until validated.

**Very early stage**: App Store ratings insufficient to draw conclusions on real-world UX. Product Hunt listing shows no tracked reviews.

**Solo developer risk**: Single maintainer, uncertain roadmap longevity.

**Language coverage**: Parakeet covers only 25 European languages — CJK and other languages need the Whisper path; accuracy and latency should be tested for your specific use case.

**No telemetry**: Good for privacy, but also means no public usage data to validate adoption.

---

### Who It's For

- Users who need cross-app voice input without trusting cloud STT
- Developers who want to replace Apple's sandbox with a private server
- Setups that require controlling STT backend (accuracy, language, cost)

---

> MIT license. DictionLabs, gateway code on GitHub, iOS app on App Store (ID: 6759807364). Self-reported numbers should be independently verified. For technical reference only.
