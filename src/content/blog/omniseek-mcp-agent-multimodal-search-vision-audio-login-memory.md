---
title: "OmniSeek：Agent 的全感知 MCP 服务器，搜、看、听、记全自托管"
titleEn: "OmniSeek: A Self-Hosted Perception MCP Server for Agents — Search, See, Hear, Remember"
description: "Battam1111/omniseek，Apache-2.0，自托管感知 MCP 服务器。给 AI Agent 装上五感：本地双语语音识别（不上云）、图片和视频帧理解、读取登录墙后的内容、跨语言信息获取、持久检索记忆 + 带溯源的证据图。8 个工具全部跑在你的机器上，作者同期还做了 Myco 持久记忆基础设施。"
descriptionEn: "Battam1111/omniseek, Apache-2.0, self-hosted perception MCP server. Gives AI agents five senses: local bilingual ASR (no cloud), image and video frame understanding, reading behind login walls, cross-language retrieval, and persistent memory with a typed, source-traced evidence graph. Eight tools that run entirely on your machine. Companion project: Myco, a persistent memory infrastructure."
pubDate: 2026-10-03
heroImage: "../../assets/images/omniseek-mcp-agent-multimodal-search-vision-audio-login-memory-banner.jpg"
category: "Tech-Experiment"
tags: ["MCP服务器", "多模态感知", "自托管", "语音识别", "Agent工具", "开源拆解"]
lang: "zh-CN"
wechatTitle: "OmniSeek：让Agent能搜看听记，全自托管MCP"
wechatDigest: "Apache-2.0；本地双语ASR不上云；读登录墙后内容；看图看视频；带溯源记忆图；8工具"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题在哪里

普通搜索给 Agent 返回的是网页快照：公开页面、一种语言、纯文本。

但真实信息往往不在这里。它可能藏在某个播客的第 47 分钟，藏在需要登录才能看的帖子里，藏在一张图里，或者用另一种语言写的。普通搜索在这些地方全军覆没。

OmniSeek 想做的是给 Agent 装上**感知层**：让它能听到、看到、读到、记住那些搜索找不到的内容——全部跑在你自己的机器上。

**仓库**：github.com/Battam1111/omniseek  
**作者**：Yanjun Chen（香港理工大学 + 宁波理工学院在读博士）  
**协议**：Apache-2.0  
**版本**：v0.2.1  
**配套项目**：Myco（持久记忆基础设施）

---

## 八个工具，五种能力

OmniSeek 通过 MCP 协议暴露 8 个工具，覆盖五个维度：

### 1. 听：本地双语 ASR

`omniseek_transcribe` 提供本地语音识别，支持双语，**完全不走云端**。播客、视频音轨、录音文件——Agent 可以直接"听"内容，而不是等字幕或 transcript。

### 2. 看：图片和视频帧

`omniseek_view` 让 Agent 理解图片和视频帧。当信息藏在截图、图表或视频画面里时，普通搜索完全无法处理，这个工具填上了这个感知缺口。

### 3. 读：登录墙后的内容

`omniseek_read`（默认**关闭**）可以使用你本地机器上的登录凭据，读取需要登录才能访问的页面。付费新闻、Discord 频道、内部文档——如果你的机器上有访问权限，Agent 也可以读。

这个功能默认是关闭的，使用前需要明确配置，由用户自主决定是否启用。

### 4. 跨语言

`omniseek_search` 带有跨语言检索能力，不限于同一种语言的结果。中文来源、英文来源、日文来源——Agent 不再因为语言被挡在门外。

### 5. 记：持久检索记忆 + 证据溯源图

`omniseek_sources` 维护一个**带类型标注的证据图**：不是简单的"记住了某件事"，而是记录"这个结论来自哪个来源、哪段原文"。

Agent 在后续推理时可以追溯每一条信息的出处，而不是在堆叠的记忆里猜测某个结论从哪里来的。

---

## 并行调度：omniseek_gather

`omniseek_gather` 是这 8 个工具里的并行调度器。

它可以同时发起 N 个独立的感知操作——同时搜索、同时读取多个页面、同时处理多个音频片段——然后汇总结果。对于需要从多个来源交叉验证的 Agent 任务，这个工具是核心加速器。

---

## Myco：配套的记忆基础设施

作者同期在做 Myco，定位是"AI Agent 的持久记忆基础设施"，是 OmniSeek 感知层的记忆后端配套。

两个项目的组合逻辑：OmniSeek 负责感知（输入端），Myco 负责记忆（存储端）。目前两个项目都还在早期阶段。

---

## 自托管意味着什么

OmniSeek 强调"全自托管"，背后的含义是：

- **ASR 在本地跑**，音频不发到云端，没有数据外泄风险
- **登录凭据留在你的机器上**，不经过任何第三方服务
- **记忆和证据图存在本地**，跨对话持久保留，不依赖外部 SaaS

对于处理敏感文档或私有内容的 Agent 任务，这一点有实际意义。

---

## 需要知道的限制

**项目仍处早期**。星标数量尚小，API 和工具接口可能随版本迭代变化，生产项目接入前要评估稳定性。

**登录墙功能需要手动启用**。默认关闭，需要在配置中明确开启并提供本地凭据，操作有一定门槛。

**ASR 双语支持的语言对**目前不够清晰，使用前建议测试目标语言的识别效果。

**Apache-2.0 协议**，商用无限制。

---

## 关键信息

| 字段 | 值 |
|------|----|
| 仓库 | Battam1111/omniseek |
| 版本 | v0.2.1 |
| License | Apache-2.0 |
| 作者 | Yanjun Chen（港理工 + 宁波理工）|
| 工具数 | 8 |
| ASR | 本地双语，无云端 |
| 登录墙读取 | 默认关闭，需手动启用 |
| 配套项目 | Myco（记忆基础设施） |

---

## 综合判断

OmniSeek 瞄准的是 Agent 感知层的一个真实缺口：搜索只能给文本，而很多信息藏在音频、图片、登录墙后面、其他语言里。

工具设计思路是对的——把不同感知能力拆成独立工具，通过 MCP 协议接入，全部本地运行。源码溯源图的设计在工程上也很有意思：不只是存结论，还存推理链的来源。

项目还在早期，这套工具组合能否在实际 Agent 工作流里稳定运行，还需要更多用户场景验证。但作为一个"给 Agent 补感知"的方向，切入点清晰。

---

> 开源仅供学习，Apache-2.0 协议，商业使用无限制。

---

<!--EN-->

## OmniSeek: A Self-Hosted Perception MCP Server for Agents

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem

Standard search gives agents web snapshots: indexed public pages, one language, text only.

But real information hides elsewhere — in minute 47 of a podcast, three comments deep behind a login, inside a chart image, or written in another language. Standard search hits a wall in all these cases.

OmniSeek aims to add a **perception layer** for agents: the ability to hear, see, read, and remember content that search can't reach — entirely on your own machine.

**Repo**: github.com/Battam1111/omniseek  
**Author**: Yanjun Chen (PhD student, Hong Kong PolyU + EIT Ningbo)  
**License**: Apache-2.0  
**Version**: v0.2.1  
**Companion project**: Myco (persistent memory infrastructure)

---

### Eight Tools, Five Capabilities

OmniSeek exposes 8 tools over the MCP protocol across five dimensions:

**1. Hear: Local Bilingual ASR**

`omniseek_transcribe` provides local speech recognition with bilingual support — **fully offline, no cloud**. Podcasts, video audio tracks, recordings: agents can "listen" to content directly, without waiting for subtitles or transcripts.

**2. See: Images and Video Frames**

`omniseek_view` gives agents the ability to understand images and video frames. When information is locked inside a screenshot, chart, or video frame, standard search is helpless — this tool fills the gap.

**3. Read: Behind Login Walls**

`omniseek_read` (default **off**) uses local credentials from your machine to read content that requires authentication. Paywalled news, Discord threads, private documentation — if your machine has access, the agent can read it.

This feature is disabled by default. Users must explicitly configure and enable it.

**4. Cross-Language**

`omniseek_search` supports cross-language retrieval. Chinese sources, English sources, Japanese sources — agents are no longer stopped by language barriers.

**5. Remember: Persistent Memory + Source-Traced Evidence Graph**

`omniseek_sources` maintains a **typed, source-traced evidence graph**: not just "the agent remembered something," but a record of "this conclusion came from that specific source, that specific passage."

Agents can trace the origin of any piece of remembered information in later reasoning, rather than guessing where a conclusion came from inside a heap of accumulated context.

---

### Parallel Dispatch: omniseek_gather

`omniseek_gather` is the parallel dispatcher among the eight tools.

It can launch N independent perception operations simultaneously — searching, reading multiple pages, processing multiple audio segments — and then consolidate results. For agent tasks that require cross-source verification, this is the core throughput tool.

---

### Myco: The Companion Memory Infrastructure

The author is building Myco alongside OmniSeek — positioned as "persistent memory infrastructure for AI agents," serving as the memory backend complement to OmniSeek's perception frontend.

The combined architecture: OmniSeek handles perception (input), Myco handles memory (storage). Both projects are early-stage.

---

### What Self-Hosted Means in Practice

OmniSeek's emphasis on being fully self-hosted has concrete implications:

- **ASR runs locally** — audio never leaves the machine, no data leakage risk
- **Login credentials stay on your machine** — never routed through any third-party service
- **Memory and evidence graph stored locally** — persists across conversations without depending on external SaaS

For agent tasks handling sensitive documents or private content, this matters.

---

### Limitations

**Project is early-stage.** Star count is small; tool APIs may change across versions. Evaluate stability before production adoption.

**Login wall feature requires manual activation.** Disabled by default; enabling it requires explicit configuration and providing local credentials.

**Bilingual ASR language coverage** is not clearly documented — test with target languages before relying on it.

**Apache-2.0 license** — commercial use unrestricted.

---

### Verdict

OmniSeek targets a real gap in the agent perception layer: search can only return text, while a lot of information is locked inside audio, images, login walls, and other languages.

The tool design is sensible — separate each perception capability into an independent tool, expose them via MCP, run everything locally. The source-traced evidence graph is an interesting engineering choice: storing not just conclusions, but the reasoning chain's provenance.

The project is early, and whether this tool combination holds up in real agent workflows at scale requires more production validation. But as a direction — "plug perception gaps for agents" — the entry point is clear.

---

> Open source for learning only. Apache-2.0 license — commercial use unrestricted.
