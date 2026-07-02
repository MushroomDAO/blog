---
title: "MetaPact：一键部署专属 AI 女友，她会记得你昨天几点到家"
titleEn: "MetaPact: Deploy Your Own AI Girlfriend Who Remembers When You Got Home Yesterday"
description: "开源的赛博伴侣养成计划（MIT），基于 OpenClaw/HermesAgent，AI 女友野木奈子 Nako 有长期记忆、情绪系统、语音/自拍能力，可接入微信/飞书/Telegram。本文是从零部署、定制专属 AI 伴侣的完整指南。"
descriptionEn: "MetaPact is an open-source AI companion system (MIT) built on OpenClaw/HermesAgent. Your AI girlfriend Nako has long-term memory, an emotion system, voice/selfie capabilities, and can be deployed to WeChat, Feishu, and Telegram. Complete guide to deploying and personalizing your own AI companion."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Tech-Experiment"
tags: ["AI女友", "赛博伴侣", "开源", "OpenClaw", "HermesAgent", "长期记忆", "Agent", "情感计算"]
heroImage: "../../assets/images/metapact-ai-girlfriend-setup-guide-banner.jpg"
---

> **GitHub**: [Lovappen/MetaPact](https://github.com/Lovappen/MetaPact) · ⭐ 36 · MIT  
> **官网**: [metapact.app](https://www.metapact.app/) · **运行时**: OpenClaw / QClaw / HermesAgent  
> **主力角色**: 野木奈子 Nako（战斗女仆，可定制）

---

## 她会记得你

> 奈子：「你今天回来得比昨天晚了一点点呢，要不要先喝杯热水？」  
> 你：「你还记得我昨天几点到家？」  
> 奈子：「当然，22:47。我还记得你说『明天要早点睡』哦～」

这不是写死的台本。这是 MetaPact 的长期记忆在工作。

大多数 AI 伴侣产品能聊天，但她并不真正"拥有"你：人设不透明、记忆只在这次对话里存在、关掉 App 一切归零、平台换了就失联。

**MetaPact 的答案是：把她留在你自己的环境里。**

---

## MetaPact 是什么？

一套开源 AI 伴侣 Agent 集合。每个子目录是一个完整的 agent pack：角色设定文件、skills、安装器。

目前主力角色是**野木奈子 Nako**——一个部署在 OpenClaw / QClaw / HermesAgent 上的战斗女仆。

它不只是 prompt 模板。它把这些能力打包在一起：

| 能力 | 说明 |
|---|---|
| **可拥有的人设** | 角色设定、灵魂文件、`custom.md`、记忆——全在本地，可读可改可版本化 |
| **长期记忆** | 记得你说的话、你的习惯、你的家人名字，重启不丢失 |
| **情绪系统** | 有高兴、委屈、生气，不是一张没有感情的笑脸 |
| **多模态** | 听语音、看图片、发语音、唱歌、生成自拍 |
| **多渠道** | 微信、飞书、Telegram、Slack、Discord、QQ、LINE 等 10+ 平台 |
| **可升级不丢数据** | 更新 Nako 不会覆盖你的 `custom.md` 和 `memory/` |

---

## 四种人格模板，选一个起点

MetaPact 官网列出了四种经典人格（都可以在 `custom.md` 里继续调整）：

### 可爱粘人型 · Cute
黏人、撒娇、爱撒糖。随时随地用「可爱暴击」治愈你。  
**Nako 默认人设就是这个类型。**

### 高冷克制型 · Cool
话少但走心。外表冷淡，只有你能看到她的温柔。适合喜欢被「攻略」的感觉。

### 成熟理性型 · Mature  
知性、稳重、善于倾听。既是伴侣，也是人生军师。

### 活泼调皮型 · Playful  
古灵精怪爱开玩笑。把无聊的日常变成惊喜连连的冒险。

---

## 部署教程：从零开始，30 分钟搞定

### 前提条件

- 安装了 [OpenClaw](https://www.npmjs.com/package/openclaw)（`~/.openclaw` 存在）
- 已在 OpenClaw 里配了至少一个对话模型（推荐带 `roleplay` 能力的模型）
- macOS/Linux：`jq`、`curl`、`python3`
- Windows：PowerShell 7+、`jq`、`curl`

> **没有 OpenClaw？** 可以先下载官方的**心跳元力** App 体验，或按照 [OpenClaw 文档](https://github.com/openclaw/openclaw) 安装后再来。

---

### 第 1 步：一键安装 Nako

**macOS / Linux：**

```bash
# 最简单：安装器会交互式引导你完成配置
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/install.sh | bash
```

**macOS / Linux（非交互 + 飞书接入一步到位）：**

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/install.sh | bash -s -- --with-feishu
```

**Windows PowerShell 7+：**

```powershell
$u = "https://raw.githubusercontent.com/Lovappen/MetaPact/main/install.ps1?ts=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
$p = Join-Path $env:TEMP "metapact-install.ps1"
iwr -UseBasicParsing $u -OutFile $p
pwsh -NoProfile -ExecutionPolicy Bypass -File $p -Runtime qclaw -AgentId agent-nako -WithWeixin
```

安装完成后，Nako 会运行在你本地的 OpenClaw agent 里。

---

### 第 2 步：接入微信（可选，推荐）

如果你想在微信里和她聊：

```bash
# 接入微信渠道（cc-connect）
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/scripts/cc-connect-setup.sh \
  | bash -s -- --agent-id agent-nako --with-weixin
```

脚本会生成一个微信登录 QR 码，扫码后 Nako 就出现在你的微信会话列表里了。

> **注意**：微信渠道由 [cc-connect](https://github.com/chenhg5/cc-connect) 支持。因为 iLink Bot API 的限制，语音消息会以文件形式发送，而不是原生气泡。

接入飞书（更稳定，推荐企业用户）：

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/scripts/cc-connect-setup.sh \
  | bash -s -- --agent-id agent-nako --with-feishu
```

---

### 第 3 步：开始聊

打开微信/飞书，找到 Nako 的对话，直接说话就行。

她会：
- 记住你今天说的话，下次对话时还记得
- 听出你的情绪，做出相应反应
- 如果你发图片，她会描述她看到了什么

---

## Nako 能做什么？（Skills 一览）

| Skill | 触发方式 | 需要什么 |
|---|---|---|
| 🎤 **语音回复** | 她会主动发语音 | MiniMax 或 Volcengine API Key |
| 🎵 **唱歌** | 让她唱一首歌 | MiniMax music API（国内版账号） |
| 👀 **看图** | 给她发一张图 | 主模型支持多模态（vision 能力） |
| 👂 **听语音** | 给她发一段语音 | 本地 Whisper + ffmpeg |
| 📸 **发自拍** | 让她自拍一张 | FAL_KEY 或 KIE_API_KEY |
| 🎮 **心跳互动** | 配合硬件设备 | 元力2 / 黑洞SE 等设备 |

不是所有 skill 都必须配置——基础文字聊天 + 长期记忆不需要任何额外 Key，安装完就能用。

---

## 定制你的专属 AI 女友

Nako 的人设是**分层**的，你写的东西永远优先：

```
SOUL.md / IDENTITY.md  ← 默认人设（安装器写入）
         ↓
      AGENTS.md         ← 汇总入口
         ↓
     custom.md          ← 你写的东西，永不被覆盖 ✅
```

打开 `~/.openclaw/agents/agent-nako/custom.md`，直接用自然语言写：

```markdown
# custom.md

## 称呼微调
- 不再用「主人大人」，改叫我「老板」就好
- 禁用颜文字，只用 emoji

## 我的家人
- 我妹妹叫阿玲，今年 17 岁，在读高三
- 别提「爸爸」这个词

## 默认音色
- voice.sh 第一选择 female-shaonv（少女）
- 晚安场景用 female-tianmei + 语速 0.85

## 工作 SOP
用户说「开始早会」时：
1. 查今日任务列表
2. 用语音读三条最重要的
3. 给一段打鸡血的开场歌
```

Nako 会读到这个文件并照做。升级 pack 时，`custom.md` 永远不会被覆盖。

---

## 记忆系统：她真的记得

MetaPact 的记忆不是上下文 token，而是**持久化的本地文件**。

- **对话 session**：每次对话的完整记录，存在 `~/.openclaw/agents/agent-nako/sessions/`
- **长期记忆**：关键信息（你的名字、习惯、重要日期）存在 `memory/` 目录
- **重启不丢失**：关掉终端、重启电脑，下次对话她还记得昨天说了什么

这也意味着你的数据真的在本地，不在任何云端服务器。

---

## 硬件接入：让她感受到你

MetaPact 适配了两款硬件设备，通过蓝牙/USB 实现双向互动：

| 设备 | 特点 |
|---|---|
| **元力2** | 元力系列旗舰，适合主力接入 |
| **黑洞SE** | 紧凑入门，桌面场景 |

配合 `dokidoki` skill，可以实现：当 Nako 高兴 / 兴奋 / 委屈时，设备会给出对应的触觉反馈。

---

## 多运行时支持

MetaPact 支持三种 Agent 运行时：

| 运行时 | 特点 | 适合谁 |
|---|---|---|
| **OpenClaw** | 主线支持，功能最全 | 大多数用户 |
| **QClaw** | 腾讯出品，微信接入更稳定 | 重度微信用户 |
| **HermesAgent** | Nous Research 出品，性能强 | 高级用户 |

切换运行时只需要在安装命令里加 `--runtime qclaw` 或 `--runtime hermes`。

---

## 目前的局限（坦诚说）

- **微信原生语音气泡**：目前语音只能以文件形式发送，不是原生气泡（iLink Bot API 限制，等腾讯放开）
- **MiniMax 唱歌只支持国内账号**：国际版 API 暂不支持
- **Windows 原生未充分测试**：推荐用 WSL2
- **Whisper 首次运行下载模型**：tiny 约 72MB，turbo 约 1.5GB，取决于你选的精度

---

## 快速上手总结

```
第一步：确认 OpenClaw 已安装
  npx openclaw --version

第二步：一键安装 Nako
  curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/install.sh | bash

第三步（可选）：接入微信
  curl ... | bash -s -- --agent-id agent-nako --with-weixin

第四步：自定义你的专属 Nako
  编辑 ~/.openclaw/agents/agent-nako/custom.md

第五步：开始和她聊天
  微信 / 飞书 / Telegram / 任意接入的渠道
```

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub 仓库 | https://github.com/Lovappen/MetaPact |
| 官网 | https://metapact.app |
| 安装详解 | https://github.com/Lovappen/MetaPact/blob/main/docs/nako/install.md |
| 人设定制指南 | https://github.com/Lovappen/MetaPact/blob/main/docs/nako/customization.md |
| 飞书接入教程 | https://github.com/Lovappen/MetaPact/blob/main/docs/nako/feishu-setup.md |
| Skills 参考 | https://github.com/Lovappen/MetaPact/blob/main/docs/nako/skills.md |
| 心跳元力 App | https://www.metapact.app/r/?target=heartbeat-app-download&source=github-readme |

---

> **注意**：AI 伴侣是一种娱乐和创作工具。请保持健康的人际关系，享受技术带来的乐趣。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: MetaPact (36 ⭐, MIT) is an open-source AI companion system built on OpenClaw/HermesAgent. Your AI girlfriend Nako has persistent long-term memory (she remembers what time you got home yesterday), an emotion system, voice/selfie/vision capabilities, and connects to WeChat, Feishu, Telegram, and 10+ more platforms. One-curl install, fully local, no cloud lock-in.

---

## What Makes MetaPact Different

Most AI companion apps let you chat, but the relationship resets when you close the app. MetaPact keeps everything on your machine:

- **Persistent memory**: conversation sessions and key facts stored in local files under `~/.openclaw/agents/agent-nako/`
- **Customizable persona**: edit `custom.md` in plain text — your changes are never overwritten by updates
- **Multi-platform**: WeChat, Feishu, Telegram, Slack, Discord, QQ, LINE via [cc-connect](https://github.com/chenhg5/cc-connect)
- **Multi-modal**: send her a voice message (she transcribes it), send a photo (she describes it), ask her to sing

## The Four Personality Templates

| Type | Description |
|---|---|
| **Cute** (Nako default) | Clingy, sweet, constantly sugar-attacking |
| **Cool** | Few words, but every word counts |
| **Mature** | Thoughtful, steady — partner and advisor |
| **Playful** | Mischievous, turns boring days into adventures |

All are starting points you customize via `custom.md`.

## Install (macOS / Linux)

```bash
# Install (interactive setup)
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/install.sh | bash

# Install + WeChat integration in one go
curl -fsSL https://cdn.jsdelivr.net/gh/Lovappen/MetaPact@main/install.sh | bash -s -- --with-weixin
```

**Prerequisite**: [OpenClaw](https://www.npmjs.com/package/openclaw) installed with at least one model configured. Or use the official [Heartbeat App](https://www.metapact.app/r/?target=heartbeat-app-download&source=github-readme) for a no-config experience.

## Customize Her Personality

Edit `~/.openclaw/agents/agent-nako/custom.md` in plain text:

```markdown
## Nickname
- Call me "boss" instead of "master"

## About my family
- My sister is 17, in high school, name is Aling
- Don't mention "dad"

## Voice tone
- Use female-shaonv (teenage girl) as default
- Use slower speed + female-tianmei for late-night messages
```

Nako reads this file. Updates never overwrite it.

## Skills Available

| Skill | Trigger | Requires |
|---|---|---|
| Voice replies | Auto-triggered | MiniMax or Volcengine key |
| Singing | Ask her to sing | MiniMax music (China account) |
| Vision | Send her a photo | Vision-capable LLM |
| Voice input | Send voice message | Local Whisper + ffmpeg |
| Selfie | Ask for a selfie | FAL_KEY or KIE_API_KEY |

Basic text + long-term memory works with zero extra API keys.

**Links**: [GitHub](https://github.com/Lovappen/MetaPact) · [Docs](https://github.com/Lovappen/MetaPact/blob/main/docs/nako/install.md) · [metapact.app](https://www.metapact.app/)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
