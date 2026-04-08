---
title: 'MemPalace：重塑 AI 记忆的记忆宫殿'
titleEn: 'mempalace-ai-memory-palace'
description: 'MemPalace 是一个开源 AI 长期记忆系统，从古希腊记忆宫殿技术中汲取灵感，解决了当前 AI 助手会话后失忆的问题。'
descriptionEn: "MemPalace is an open-source AI long-term memory system inspired by ancient Memory Palace techniques."
pubDate: "2026-04-08"
category: "Tech-News"
tags: ["ai-memory", "open-source", "local-ai", "privacy", "milla-jovovich"]
heroImage: "../../assets/images/cover-mempalace.jpg"
---

![米拉·乔沃维奇与 MemPalace](../../assets/images/content-mempalace-1.jpg)

**MemPalace** 是一个由米拉·乔沃维奇（Milla Jovovich）构思并参与开发（与工程师 Ben Sigman 合作）的开源 AI 长期记忆系统。它的核心目标是解决当前 AI 助手（如 Claude, GPT 等）在关闭会话后即"失忆"的问题，同时提供比现有方案更高效、更廉价的检索机制。

> 📄 **原文链接**: https://github.com/milla-jovovich/mempalace

---

## 1. 核心理念：古老的"记忆宫殿"技术

![MemPalace Logo](../../assets/images/content-mempalace-2.jpg)

该项目从古希腊的**"位置记忆法（Method of Loci）"**中汲取灵感。传统 AI 记忆通常依赖复杂的 LLM 提取和云端向量数据库，而 MemPalace 将信息组织在一个虚拟的"空间结构"中：

- **翼（Wing）**：代表大型项目、人物或主题
- **房间（Room）**：翼下的子话题（如开发、计费、部署）
- **走廊（Hall）**：跨越不同翼的共享内存类型
- **壁橱（Closet）**：存放压缩后的摘要

这种空间化的元数据组织方式，使得**检索性能提升了约 34%**，因为结构本身就带有了逻辑属性。

---

## 2. 技术亮点：极致的隐私与效率

### 🏠 本地优先，零成本

整个系统完全运行在用户本地设备上，**不需要 API 密钥，不产生云端费用**。它仅依赖简单的 Python 库（ChromaDB 和 PyYAML），对隐私极度友好。

### 🗜️ AAAK 压缩协议

项目引入了一种专为 AI 设计的简写方言**"AAAK"**，能实现 **30 倍的文本压缩且无损**。这意味着 AI 可以在区区 100 多个 Token 的开销内读完数月的对话上下文。

### ⏰ 事实的时态性

它内置了一个带有时序的知识图谱，能记住"事实"随时间的变化（例如，某人曾在 A 公司工作，现在在 B 公司），这是普通向量检索难以实现的。

---

## 3. 性能表现

在 LongMemEval 等权威基准测试中，MemPalace 的表现极其惊人：

| 指标 | 成绩 |
|------|------|
| 召回率（无云端模型） | **96.6%** |
| 召回率（+ 重排序） | **100%** |

相比之下，许多依赖昂贵云端架构的系统由于 LLM 在提取过程中的"幻觉"或信息丢失，表现反而不如 MemPalace 这种"存储全文+空间组织"的简单逻辑。

---

## 总结

**MemPalace 证明了"聪明的设计优于暴力的算力"**。米拉·乔沃维奇从一个日常 AI 使用者的痛点出发，用极客的方式提供了一个高效、隐私、且充满美学的 AI 记忆方案。

> 💡 **适用人群**: AI 助手重度用户、隐私敏感开发者、对本地 AI 有需求的用户
>
> 🎬 **有趣事实**: 由《生化危机》主演米拉·乔沃维奇参与开发的开源项目
