---
title: "14天、5人，他们真的把AI编程助手整出来了"
titleEn: "14 Days, 5 People: MiMo Code and the Vibe Coding Era"
description: "罗福莉在推上官宣 MiMo Code 诞生——14天，5个人，一场 vibe-coding 之旅。加上 k佬 两天喝完一箱红牛重构 Kimi Code，2026年的AI编程工具战争，已经用「天」为单位在卷了。"
descriptionEn: "Xiaomi's MiMo team just open-sourced MiMo Code in 14 days with 5 people. The vibe-coding era isn't just about using AI to write code — it's now how teams build AI coding tools themselves."
pubDate: "2026-06-11"
updatedDate: "2026-06-11"
category: "Tech-News"
tags: ["AI编程", "MiMo Code", "vibe-coding", "终端助手", "大模型", "开源"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

> **BLUF**：2026年6月11日，小米 MiMo 团队用14天、5人开源了终端 AI 编程助手 MiMo Code V0.1.0，内置性能比肩 Claude Sonnet 4.6 的 MiMo-V2.5 模型，百万上下文免费用。加上 Kimi Code 团队极限两天重构的故事，AI 编程工具的竞争节奏，已经以「天」为单位在卷了。

---

## 一条推特，一个时代的缩影

刚刚，罗福莉在推上发了这样一条消息——

> *"强大的模型演进需要一个坚实的 harness 系统，反之亦然。14 天，5 个人，一场 vibe-coding 之旅——MiMo Code 就此诞生。"*

这不是大厂发布会的公关稿口气，是负责人在深夜发的那种、带着一点克制骄傲的随手一推。

2026年6月11日，小米 MiMo 大模型团队正式开源了 **MiMo Code V0.1.0**——一个跑在终端里的 AI 编程助手，MIT 协议，GitHub 地址：XiaomiMiMo/MiMo-Code，安装只需一行命令。

14天，5人。在大厂产品节奏普遍以季度计的今天，这两个数字格外刺眼。

---

## 就在这之前，k佬在汤泉喝了一箱红牛

就在 MiMo Code 官宣的前几天，另一件事悄悄在程序员圈子里流传。

Kimi Code 的某位负责人（网友称"k佬"）在社交媒体上发帖，说他们重构 Kimi Code，选了一个不太寻常的地方——汤泉，也就是温泉浴池。就在那儿，两天时间，干掉了整整一箱红牛，硬肝出了 Kimi Code 的整体重构。

两件事同台出现，构成了一幅2026年独有的行业图景：

**做 AI 编程工具这件事，已经开始用 AI 编程工具本身来做了。**

Vibe Coding 不再只是开发者用 AI 协作写代码的方式——它正在成为整个行业构建下一代工具的姿态。这个递归式的循环，既荒诞，又有趣，又充满了某种时代的加速感。

---

## MiMo Code 到底带来了什么？

从技术层面来说，MiMo Code 是基于开源项目 OpenCode 的二次开发，MIT 协议，运行在终端，定位是"你最懂行的 AI 工作搭子"。

### 内置 MiMo-V2.5：性能直追 Claude Sonnet 4.6 的开源模型

MiMo-V2.5 是小米最新开源的多模态大模型。其 Pro 版本是一个参数量达 1.02 万亿的 MoE 架构（每次推理激活 420 亿参数），标配百万 Token 上下文窗口，在 SWE-Bench Pro 上得分 62%，Terminal Bench 2 上得分 73%，均超过 Claude Code 当前水准。

V0.1 版本将这个模型限时免费内置，开箱即用，不需要申请 API Key，不需要配置密钥——登录 MiMo Auto 直接跑。

### 三重持久记忆：告别"从头来"

传统 AI 编程助手最大的痛点之一：会话一结束，上下文清空，下次打开又要重新解释项目背景。

MiMo Code 用 SQLite FTS5 全文检索构建了三层记忆机制——**项目记忆、会话检查点、任务进度**。主 agent 负责干活，记忆由独立子 agent 维护，互不干扰。每七天还会触发 `/dream` 命令，对历史数据做合并、去重、压缩，类似人类睡眠整理记忆的机制。

意思是你今天开的项目，明天继续，它不会忘。

### 三种工作模式 + 子 Agent 并行

`build`（完整开发权限）、`plan`（只读分析）、`compose`（规范驱动开发）。主 agent 可随时拉起子 agent 并行处理子任务，带生命周期追踪。不是单一的"和 AI 对话"，而是一个可调度的小团队。

### 全中文本地化 + 语音输入

TUI 界面右侧状态看板完整中文化，是目前少数针对国内开发者深度适配的终端 AI 工具。内置 MiMo-V2.5 语音识别，支持口头下达修改指令——走路的时候也能写代码，或者，泡温泉的时候（某 k 佬：那得看哪个热度的水）。

---

## 罗福莉那句话，值得拆开说

> *"强大的模型演进需要一个坚实的 harness 系统，反之亦然。"*

这句话不是公关稿，是一个技术判断，也是 MiMo Code 存在的原因。

它说的是：**模型能力和工具框架之间，存在双向依存关系。**

上下文管理做得烂，哪怕挂上最强模型，效果也大打折扣——罗福莉在此前一次约3.5小时的深度访谈中直点名批评某产品："一个用户请求触发多轮低价值工具调用，每次带超 10 万 Token"，这种浪费不是模型的问题，是 harness 的问题。

反过来，工具框架越精密，才能把模型的能力边界推得更远——记忆压缩、子 agent 调度、上下文重建，这些都是工具层的活，模型层解决不了。

**这个判断的推论是：只开源模型是不够的，你得一起打磨那个能驾驭模型的系统。**

这也解释了为什么 MiMo 团队在发布 MiMo-V2.5-Pro 的同一天，要同步发布 MiMo Code。

---

## 这个赛道，到底在比什么？

2026年，AI 编程助手市场已经高度分裂：

| 工具 | 定位 | 核心优势 |
|---|---|---|
| Claude Code | 终端代理 | 跨文件代码库理解最强 |
| Cursor | AI 原生编辑器 | Tab 补全 + 多文件编辑体验 |
| Gemini CLI | 开源入口 | 免费，个人账号直接用 |
| Codex CLI | OpenAI 生态 | 并行任务，o3 加持 |
| Kimi Code | 国产代理 | K2.6 模型，长任务 Agent |
| **MiMo Code** | **中文终端** | **本土化 + 自进化记忆** |

没有一个工具能在所有场景碾压其他人。但可以看到一个趋势：**终端 AI Agent 类工具正在成为国产大模型厂商的标准动作。**

背后逻辑很直接：Coding 是大模型能力最容易量化的场景；有自己的 coding tool，等于有了最有说服力的 showcase，也有了最直接的用户反馈闭环。

---

## 给终端党的建议

如果你是终端党、或者对国产 AI 编程工具感兴趣，现在就可以去试一下：

安装命令（curl 方式）：
`curl -fsSL https://mimo.xiaomi.com/install | bash`

npm 方式：
`npm install -g @mimo-ai/cli`

V0.1 注定有很多毛边，这不是终点。但这个起步和出手速度，已经说明了一些事：

**做 AI 工具的门槛，正在以你想象不到的速度下降。而速度本身，已经成为新的护城河。**

---

## 最后

红牛喝了，汤泉泡了，代码也推出去了。

14天，5个人，开源，MIT。

这就是2026年，这个行业的模样。

---

> 相关链接（请手动访问）：
> MiMo Code GitHub 仓库：https://github.com/XiaomiMiMo/MiMo-Code
> MiMo-V2.5-Pro 开源详情（知乎）：https://zhuanlan.zhihu.com/p/2032460985118745387
> 罗福莉访谈相关（BiliBili）：https://www.bilibili.com/video/BV1iVoVBgERD/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: On June 11, 2026, Xiaomi's MiMo team open-sourced MiMo Code V0.1.0 — a terminal AI coding assistant built by 5 people in 14 days. It ships with MiMo-V2.5, a model that matches Claude Sonnet 4.6 on coding benchmarks, with a 1M-token context window, free to use out of the box. This is the vibe-coding era: AI tools are now built with AI tools.

---

## The Tweet That Started It

On June 11, 2026, Luo Fuli — head of Xiaomi's MiMo large model team — posted on X:

> *"A powerful model needs a solid harness, and vice versa. 14 days. 5 people. One vibe-coding journey — MiMo Code is born."*

Not a press release. A late-night tweet from someone who just shipped something.

MiMo Code V0.1.0 is now open source under MIT. One-line install:
`curl -fsSL https://mimo.xiaomi.com/install | bash`

---

## What Makes It Different?

**MiMo-V2.5 built in**: A 1.02T-parameter MoE model (42B active params), 1M context, 62% on SWE-Bench Pro and 73% on Terminal Bench 2 — outperforming Claude Code on current benchmarks. Free during the launch period, no API key needed.

**Persistent memory**: Three-layer system (project memory, session checkpoints, task progress) backed by SQLite FTS5 full-text search. A dedicated sub-agent handles memory so the main agent can focus on coding. A `/dream` command runs every 7 days to compress and deduplicate history.

**Multi-agent modes**: `build` (full dev access), `plan` (read-only analysis), `compose` (spec-driven development). Sub-agents can run in parallel with lifecycle tracking.

**Full Chinese localization + voice input**: TUI status panel in Chinese. Voice commands via MiMo-V2.5 speech recognition — for the developer who codes while walking, or apparently, soaking in a hot spring.

---

## The Kimi Code Story (And Why It Matters)

Just before MiMo Code launched, a story circulated: one of Kimi Code's leads (the community calls him "k佬") refactored the entire Kimi Code CLI in two days while at a hot spring resort, fueled by a case of Red Bull.

These two stories together say something about the state of the industry in 2026:

**Vibe coding is no longer just how developers write code. It's how teams build AI coding tools themselves.**

The recursion is real.

---

## The Harness-Model Co-Evolution Thesis

Luo Fuli's tweet wasn't marketing — it was a technical claim:

> *"A powerful model needs a solid harness, and vice versa."*

The implication: open-sourcing a model isn't enough. You have to build — and ship — the system that can wield it. Context management, sub-agent scheduling, memory compression — these are harness problems, not model problems. A bad harness wastes a great model.

This is why MiMo Code and MiMo-V2.5-Pro launched on the same day.

---

## The Competitive Landscape

| Tool | Strength |
|---|---|
| Claude Code | Best codebase-level understanding |
| Cursor | AI-native editor, multi-file editing |
| Gemini CLI | Free for personal use, open source |
| Codex CLI | Parallel tasks, o3-powered |
| Kimi Code | Long-horizon agent tasks |
| **MiMo Code** | **Chinese localization + self-evolving memory** |

No tool dominates every scenario. But the trend is clear: terminal AI agents have become the default way for Chinese model labs to prove their models work in the real world.

---

## Try It

GitHub: https://github.com/XiaomiMiMo/MiMo-Code

MIT license. V0.1 will have rough edges. That's fine. The starting point and the speed are already saying something.

**The barrier to building AI tools is falling faster than you think. And speed itself has become the new moat.**

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
