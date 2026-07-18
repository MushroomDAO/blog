---
title: "织影 Video Production Buddy：AI 视频制作，每个阶段都要人工审批"
titleEn: "Video Production Buddy / 织影: Staged AI Video Production With Approval Gates at Every Step"
description: "video-production-buddy/video-production-buddy（AGPLv3，Python）是一个强调人工管控的 AI 视频制作系统，中文名织影。和一键生成不同，它用 YAML 管线配置和 Markdown skills 把制作分成多个阶段（策划→脚本→素材→渲染→审查），每阶段都有审批门（Approval Gate）。Backlot 看板实时显示进度、花费和每个提供商决策，审批通过才能继续。适合对视频质量有要求、需要可溯源制作流程的用户。"
descriptionEn: "Video Production Buddy / 织影 (video-production-buddy/video-production-buddy, AGPLv3, Python) is a staged, governed AI video production system. Unlike one-shot generators, it uses YAML pipeline manifests and Markdown skills to gate production at brief, script, scene plan, asset, and final review stages — each requiring human approval before the next spend. The Backlot live board shows stages, scripts, scene cards, generated assets, provider decisions, and cost in real time, with frame-level replay after completion."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Tech-News"
tags: ["AI视频", "Video Production Buddy", "织影", "审批门控", "Backlot", "开源", "Python"]
heroImage: "../../assets/images/video-production-buddy-zhiying-ai-pipeline-guide-banner.jpg"
---

> **项目主页**: [video-production-buddy.github.io](https://video-production-buddy.github.io) · **仓库**: [github.com/video-production-buddy/video-production-buddy](https://github.com/video-production-buddy/video-production-buddy) · Stars: 281 · License: AGPLv3

---

## 一键生成之后，你还剩下什么？

AI 视频生成工具越来越多，大多数的用户体验都指向同一个终点：输入一段提示词，点击"生成"，等待几分钟，视频出来了。这个流程很爽——直到你发现视频里产品颜色错了，角色在第二个场景里突然换了造型，或者有一段画面和品牌调性完全不符。

重新生成，花费再乘以二。

**织影（Video Production Buddy）**选择了另一条路。它的核心主张是：**在你花钱之前，先设计好每一个阶段；在每一个阶段结束后，先批准再继续**。

这不是一个速度更快的工具，而是一个**让你不需要重新生成的工具**。

---

## 什么是审批门（Approval Gates）？

织影把制作分成五个明确的阶段：

1. **策划（Brief）**：热点话题搜索、平台爆款风格分析、情绪节奏曲线规划
2. **脚本（Script）**：逐场景结构化脚本，配合"概念图谱"锁定跨场景一致性
3. **场景规划（Scene Plan）**：每个场景的视觉逻辑、角色状态、道具清单
4. **素材生成（Asset Generation）**：逐张生成图片/视频素材，**每张素材生成后暂停等待审批**
5. **幻觉审查（Hallucination Review）**：生成样本经由审查代理检验物理可行性、价值一致性、叙事连贯性

每个阶段结束后，系统不会自动推进到下一步。它等你看，等你批准，等你说"可以继续"。

审批门不是流程的障碍，而是**成本控制和质量保障的主动屏障**。

---

## Backlot：你的制作看板

让审批门可操作的是 **Backlot**——一个运行在本地浏览器里的实时生产看板。

```bash
python -m backlot open                  # 打开所有项目的总览
python -m backlot open <project-id>     # 某个正在制作的项目实时看板
python scripts/backlot_simulate_run.py  # 没有制作任务也能看模拟演示
```

Backlot 显示的内容：

- **当前所处阶段**：每一步的完成状态
- **脚本和场景卡**：结构化的内容规划
- **素材生成进度**：每一张素材的状态（等待审批 / 已批准 / 已拒绝）
- **提供商决策日志**：调用了哪个 AI 服务，参数是什么，花费是多少
- **实时花费追踪**：每一笔调用的费用和累计总花费

最重要的是，当素材在逐张生成时，Backlot 会**在每张生成完成后暂停**，把控制权交还给你。不是"生成完了再看"，而是"**生成一张，看一张，批一张**"。

制作完成后，Backlot 还提供 **Replay 模式**：把整个制作流程按时间轴逐帧重放，用于复盘、存档或向客户汇报。

---

## 设计先于生成

在进入任何生成步骤之前，系统会先完成：

- **热点话题研究**：分析当前平台（B 站、抖音等）上的高互动内容，识别爆款结构
- **情绪节奏曲线**：把视频的情绪走势可视化设计出来，再决定每个场景的基调
- **概念图谱（Concept Graph）**：跨场景的一致性锚点——产品颜色、角色服装、场景光线，全部在生成前锁定

这些设计工作用 YAML 管线配置文件和 Markdown skills 表达，版本可控，可在团队间复用。

**幻觉审查层**检验生成样本的物理可行性、价值一致性和叙事连贯性。这不是可选项，而是流程的一部分。

---

## 和 OpenMontage 放在一起看

同期出现的 **OpenMontage**（33K 星）在技术底层有明显重叠：都使用 Remotion（React 视频渲染）和 HyperFrames（HTML/CSS/GSAP 动画引擎），也都支持同类 AI 编码助手。两个项目之间可能存在更深的关联。

| | OpenMontage | 织影 Video Production Buddy |
|---|---|---|
| Stars | 33K | 281 |
| 核心主张 | 一条命令直接出视频 | 设计优先，每阶段人工审批 |
| 适合场景 | 快速出片、批量生产 | 高质量单片、品牌视频 |

OpenMontage 的强项是速度，织影的强项是**可控性和可溯源性**。

---

## 安装与上手

```bash
git clone https://github.com/video-production-buddy/video-production-buddy.git
cd video-production-buddy
python3 -m venv .venv
source .venv/bin/activate
make setup
python -m lib.agent_components install --profile default --frozen
make preflight
make demo   # 本地演示，不需要任何 API key
```

**前置要求**：Git、Python 3.10+、FFmpeg、Node.js 22+、Make、AI 编码助手

`make demo` 不需要任何 API key 就能跑通完整演示流程，是最快的上手方式。跑完 demo 之后再开 Backlot 看整个流程，比读文档直观得多。

---

## 适合谁用

- **品牌视频制作者**：每一帧都关乎品牌形象，容不得视觉不一致
- **需要向客户汇报的制作团队**：完整的决策日志和 Replay 可以作为制作报告
- **想控制 AI 调用成本的团队**：每阶段审批意味着你在真正花钱之前就能叫停
- **对 AI 幻觉有零容忍要求的项目**：幻觉审查层是流程的必选组件

如果你做过一次"生成完了才发现全错了"的经历，你会理解织影想解决的是什么问题。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Video Production Buddy / 织影 (video-production-buddy.github.io, AGPLv3, Python 3.10+) is a staged, human-governed AI video production system. Unlike one-shot generators, it gates production at brief, script, scene plan, asset generation, and hallucination review stages — each requiring explicit human approval before the next API spend. The Backlot local board shows live stage progress, structured scripts, scene cards, asset-by-asset generation status, provider decisions, and running costs. After completion, Replay mode reconstructs the entire run frame by frame.

---

## What Makes It Different

Most AI video tools run end-to-end without interruption. Video Production Buddy inserts **Approval Gates** between every production phase. During asset generation, Backlot pauses after each individual image or video clip is generated — you approve or reject before the next asset begins. This eliminates the "generated everything and now it's wrong" problem.

## Design Intelligence Before Generation

Before any generative call, the system completes: trending topic research, emotional rhythm curve planning, and a **Concept Graph** that locks cross-scene consistency (product colors, character appearance, visual logic). A **hallucination review** layer then inspects samples against physical plausibility, value alignment, and narrative coherence.

## Quick Start

```bash
git clone https://github.com/video-production-buddy/video-production-buddy.git
cd video-production-buddy
python3 -m venv .venv && source .venv/bin/activate
make setup
make demo   # no API key needed
```

Prerequisites: Python 3.10+, FFmpeg, Node.js 22+, Make, any AI coding assistant.

## vs. OpenMontage

Both projects share Remotion and HyperFrames rendering engines and support the same AI coding assistants. OpenMontage (33K stars) optimizes for speed; Video Production Buddy optimizes for control, cost discipline, and traceability. They are complementary, not competing.

**Links**: [Project page](https://video-production-buddy.github.io) · [GitHub](https://github.com/video-production-buddy/video-production-buddy)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
