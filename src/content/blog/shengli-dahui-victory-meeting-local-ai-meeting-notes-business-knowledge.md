---
title: "胜利的大会：本地 AI 会议同事，录音→深度业务纪要→知识库，macOS 首发"
titleEn: "shengli-dahui-victory-meeting-local-ai-meeting-notes-business-knowledge"
description: "胜利的大会（Victory Meeting）是一款面向业务团队的本地优先 AI 会议纪要工具，v1.0.0-test 首发，仅支持 macOS Apple Silicon。核心流程：录音或上传音频 → 本地转写 → 生成深度业务纪要（结论/重点/行动项/风险）→ 提取待办事项 → 候选知识发现 → 人工确认后入库。适合渠道、销售、市场、代理商沟通等业务场景；知识库支持客户、产品、渠道、项目、竞品、方法论等长期沉淀；支持 Obsidian 知识库集成；本地优先，API Key 不硬编码，AI 接口只在生成纪要时调用。"
descriptionEn: "Victory Meeting (胜利的大会) is a local-first AI meeting assistant for business teams — v1.0.0-test, macOS Apple Silicon only. Core flow: record or upload audio → local transcription → deep business notes (conclusions/key points/actions/risks) → action-item extraction → candidate knowledge discovery → human-confirmed knowledge base. Targets channel, sales, marketing, and distributor teams; knowledge base covers customers, products, channels, projects, competitors, methodologies; Obsidian integration optional; local-first, no hard-coded API keys, AI API called only for note generation."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["会议纪要", "AI工具", "知识管理", "本地优先", "macOS", "业务团队", "渠道管理", "产品首发"]
heroImage: "../../assets/images/shengli-dahui-victory-meeting-local-ai-meeting-notes-business-knowledge-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：zhangchunquan298-anhui/shengli-dahui  
产品名：胜利的大会 / Victory Meeting  
版本：v1.0.0-test（2026-08-19 首发）  
平台：macOS Apple Silicon（M 系列芯片）  
下载：GitHub Release → `VictoryMeeting-1.0.0-arm64.dmg`

---

## 一、它做什么

会议开完，真正重要的东西却没有留下来——结论、任务、风险点、客户承诺，散落在群聊、录音、个人备忘里，没有形成可复用的资产。

胜利的大会要解决的就是这件事：把一次会议的录音，变成**可操作的业务文件 + 可积累的知识资产**。

一句话：「你的本地 AI 会议同事。」

---

## 二、核心流程

```
录音 / 上传音频
       ↓
   本地转写
       ↓
深度业务纪要（结论 · 重点 · 行动项 · 风险 · 下一步）
       ↓
   待办事项提取
       ↓
  候选知识发现
       ↓
   人工确认
       ↓
正式写入知识库
```

每一步都有明确的产出物，不是一张模糊的「AI 摘要」。**候选知识必须经过人工确认才能进入知识库**——这是防止噪音污染的关键设计。

---

## 三、功能清单

| 功能 | 说明 |
|------|------|
| **会议录音** | 支持直接录音，文件优先存本机 |
| **上传录音** | 上传已有音频，生成转写和纪要 |
| **本地转写** | 本地模型转写，不上传录音到云端 |
| **深度业务纪要** | 按场景整理：结论、重点、行动项、风险、下一步 |
| **待办事项** | 从会议承诺提取明确、可执行的任务 |
| **会议库** | 统一管理历史会议、转写、纪要、附件 |
| **知识库** | 沉淀客户/产品/渠道/项目/竞品/政策/方法论 |
| **人工确认** | 候选知识审核后才写入正式知识库 |
| **多格式导出** | 导出为常用文档格式，方便同步给团队 |
| **Obsidian 集成** | 可选：知识库与 Obsidian 联动 |

---

## 四、适合哪些场景

产品的定位非常具体——面向**有大量客户、渠道、代理商沟通的业务团队**，而不是泛用型会议工具：

**连锁谈判**：沉淀客户诉求、价格策略、资源承诺、风险点和下一步动作。

**代理商沟通**：记录区域问题、政策执行进度、反馈和需要总部支持的事项。

**产品方案评审**：整理产品定位、卖点、价格、渠道策略和上市节奏。

**市场周会**：复盘目标达成、费用使用、活动进展和下周计划。

**项目复盘**：保留关键问题、根因、有效动作和可复用方法论。

这些场景的共同特征：**会议信息有商业价值，但当前的沉淀方式很差**。大量知识存在个人脑子里、聊天记录里，没有系统化。

---

## 五、数据边界

- 录音、转写、纪要和知识库数据**优先保存在本机**
- API Key 不写入代码，不应公开分享
- 配置线上 AI（DeepSeek 或兼容接口）后，**只在生成纪要或知识发现时调用**——不持续上传数据
- 未经人工确认的候选知识不会进入正式知识库

---

## 六、安装

当前版本仅支持 **macOS Apple Silicon（M 系列）**，Intel Mac、Windows、Linux 暂不支持。

```
1. 到 GitHub Release 下载 VictoryMeeting-1.0.0-arm64.dmg
2. 安装，首次打开按引导完成：
   · 检查本地转写环境
   · 配置 DeepSeek 或其他兼容 API
   · 做一次 20 秒测试录音
   · 按需配置 Obsidian 知识库
```

---

## 七、这个产品在解决什么

中国大量企业的「业务知识沉淀」问题是真实的：渠道经理换人、区域负责人离职、老客户关系断裂，重要的背景信息随着人走了。会议里谈的东西从来没有被系统化保留。

胜利的大会的切入点很准——**不是做一个通用型会议录制工具，而是做一个业务场景下的知识沉淀系统**，AI 做的是把录音里的业务信息提炼成结构化资产，人负责最后的确认和判断。

v1.0.0-test 是第一个公开测试版，仅 macOS Apple Silicon，功能还处于早期阶段。值得跟踪。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Victory Meeting (胜利的大会): Local AI Meeting Assistant — Recording → Business Notes → Knowledge Base, macOS First Release

*by Mycelium Protocol*

---

GitHub: zhangchunquan298-anhui/shengli-dahui  
Name: 胜利的大会 / Victory Meeting  
Version: v1.0.0-test (released 2026-08-19)  
Platform: macOS Apple Silicon (M-series) only  
Download: GitHub Release → `VictoryMeeting-1.0.0-arm64.dmg`

---

### What It Does

After meetings end, the things that actually mattered — conclusions, task assignments, risk flags, customer commitments — scatter across chat threads, audio files, and personal notes. They don't accumulate into reusable assets.

Victory Meeting addresses this by turning a meeting recording into **actionable business documents + accumulated knowledge assets**.

Tagline: "Your local AI meeting coworker."

---

### Core Workflow

```
Record / upload audio
         ↓
  Local transcription
         ↓
Deep business notes (conclusions · key points · actions · risks · next steps)
         ↓
   Action-item extraction
         ↓
  Candidate knowledge discovery
         ↓
    Human confirmation
         ↓
 Written into knowledge base
```

Each step produces a concrete output — not a generic "AI summary." **Candidate knowledge requires human review before entering the knowledge base** — the core safeguard against noise pollution.

---

### Features

| Feature | Description |
|---------|-------------|
| **Recording** | Record meetings directly; files stored locally |
| **Audio upload** | Upload existing audio for transcription and notes |
| **Local transcription** | Runs locally; recordings not sent to cloud |
| **Business notes** | Structured output: conclusions, key points, actions, risks, next steps |
| **Action items** | Clear and executable tasks extracted from commitments |
| **Meeting library** | Manage meeting history, transcripts, notes, files |
| **Knowledge base** | Customer / product / channel / project / competitor / methodology knowledge |
| **Human confirmation** | Candidate knowledge reviewed before saved |
| **Export** | Common document formats for team sharing |
| **Obsidian integration** | Optional: sync knowledge base with Obsidian |

---

### Target Scenarios

The product is specifically positioned for **business teams with high volumes of client, channel, and distributor meetings** — not generic meeting software:

**Retail-chain negotiation**: capture customer needs, pricing logic, resource commitments, risks, and follow-ups.

**Distributor meetings**: record regional issues, policy execution, progress updates, and support requests.

**Product reviews**: summarize positioning, selling points, pricing, channel strategy, and launch rhythm.

**Market weekly meetings**: review targets, spending, activities, and next-week plans.

**Project retrospectives**: retain issues, root causes, effective actions, and reusable methods.

Common thread across these scenarios: **meeting content has business value, but current retention methods are poor.** Most knowledge lives in individual memories or chat logs with no systematic structure.

---

### Data Boundary

- Recordings, transcripts, notes, and knowledge data stored **locally first**
- API keys not hard-coded; should not be shared publicly
- AI API (DeepSeek or compatible) called **only for note generation and knowledge discovery** — not for continuous data upload
- Candidate knowledge requires human confirmation before entering the formal knowledge base

---

### Install

Currently macOS Apple Silicon (M-series) only. Intel Mac, Windows, Linux not yet supported.

```
1. Download VictoryMeeting-1.0.0-arm64.dmg from GitHub Releases
2. Install and complete the first-run guide:
   · Check local transcription environment
   · Configure DeepSeek or compatible AI API
   · Do a 20-second test recording
   · Optional: set up Obsidian knowledge base
```

---

### What Problem This Is Really Solving

In a large number of Chinese enterprises, "business knowledge retention" is a genuine problem: when a channel manager or regional lead leaves, critical relationship context goes with them. What was agreed in meetings has never been systematically preserved.

Victory Meeting's positioning is specific — not a general-purpose meeting recorder, but **a knowledge accumulation system for business contexts**, where AI handles the extraction of structured assets from recordings and humans handle the final review.

v1.0.0-test is the first public release, macOS Apple Silicon only, early stage. Worth tracking.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
