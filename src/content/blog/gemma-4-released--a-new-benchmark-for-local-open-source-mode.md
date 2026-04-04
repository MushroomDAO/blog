---
title: 'Gemma 4 发布：本地开源模型的新标杆'
titleEn: 'Gemma 4 Released: A New Benchmark for Local Open Source Models'
description: 'Google DeepMind 发布 Gemma 4，支持原生多模态、256K 长文本、Agent 友好，开源模型也能媲美闭源旗舰'
descriptionEn: 'Google DeepMind releases Gemma 4 with native multimodal support, 256K context, and Agent-friendly features'
pubDate: '2026-04-03'
category: 'Tech-News'
tags: ['gemma', 'gemini', 'llm', 'open-source', 'ai-agent']
heroImage: '../../assets/blog-cover-20260403.jpg'
---

2026 年 4 月 2 日，Google DeepMind 正式发布了 **Gemma 4**。这不是一次简单的版本迭代，而是开源本地模型的一次质变——基于 Gemini 3 同款架构，专门针对本地部署和开发者效率进行了深度优化。

## 四档规模，全场景覆盖

Gemma 4 这次直接推出四个版本，从手机到工作站全照顾到了：

- **E2B & E4B** —— "E" 代表 Effective（有效参数）。专门为手机和笔记本设计的边缘模型，Android AICore 直接跑。
- **26B (MoE)** —— 混合专家架构，总参 26B，每次只激活 4B。性能与速度的平衡点。
- **31B (Dense)** —— 系列最强稠密模型，多项榜单直追闭源旗舰。

## 技术特性有点炸

**原生多模态** 是标配，文本图像视频都能处理。但最意外的是 **E2B/E4B 原生支持音频输入**——这意味着你可以在本地做语音交互 Agent，不用上云。

**长文本** 也很能打：小模型 128K，大模型直接 256K。做代码库分析、协议文档解析，上下文管够。

**Thinking Mode** 借鉴了 Gemini 3 的推理链路，复杂逻辑任务（比如智能合约审计）准确率明显提升。

**Agent 友好** 是重点。原生支持 `system` 角色和 **Function Calling**，解决了开源模型构建自主 Agent 时输出格式不稳定的老大难问题。

## 性能表现

Arena 榜单上，**Gemma 4 31B** 已经冲进开源前三。数学（AIME 2026）和编程（LiveCodeBench）尤其亮眼——31B 版本完全可以当本地代码助手用。

## 上手体验

Apache 2.0 协议，商用无限制。

本地部署最简单：
```bash
ollama run gemma4:31b
```

Android 开发的话，AICore 开发者预览版已集成。云端部署可以上 Google Cloud Vertex AI，Blackwell B200 都支持。

## 值得试试

如果你之前觉得 Gemma 2/3 的推理差点意思，或者多模态不够顺滑，Gemma 4 真的值得拉下来跑一下。特别是对 Agent 任务的优化，跟目前 AI Task Market 的研究方向很契合。

本地终端跑大模型的门槛，又低了一些。
