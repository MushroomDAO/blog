---
title: 'Hyper-Extract 概要介绍'
description: '由大语言模型驱动的智能知识提取与演化框架，支持从简单列表到复杂知识图谱的一站式知识抽取'
pubDate: '2026-04-14'
category: 'Tech-News'
tags: ['knowledge-extraction', 'llm', 'rag', 'graphrag', 'framework']
heroImage: '../../assets/images/cover-hyper-extract.jpg'
---

Hyper-Extract 是一个由大语言模型（LLM）驱动的智能知识提取与演化框架。它的核心使命是将高度非结构化的文本，通过一套简洁的指令，转化为结构化、持久化且类型可预测的"知识摘要"（Knowledge Abstracts）。无论你需要的是简单的列表模型，还是极其复杂的知识图谱、超图乃至时空图谱，该框架都能一站式搞定，真正做到"告别文档焦虑，让信息一目了然"。

![Hyper-Extract 知识图谱框架](../../assets/images/content-hyper-extract.jpg)

## 能力和价值

**8 大核心数据结构（Auto-Types）**： 原生支持从基础的 AutoModel、AutoList 到复杂的 AutoGraph、AutoHypergraph 及 AutoSpatioTemporalGraph 等 8 种高维数据结构。

**10+ 前沿提取引擎**： 开箱即用，全面支持并集成了当前最先进的 RAG 和知识提取范式，如 GraphRAG、LightRAG、Hyper-RAG 以及 KG-Gen 等。

**零代码声明式 YAML 模板**： 内置横跨金融、法律、医疗、中医、工业及通用领域的 6 大场景，提供超过 80 个预设模板。用户无需编写底层代码，即可完成特定领域的定制化知识抽取。

**增量知识演化**： 知识库并非静态，支持"边读边学"（Feed），可以动态喂入新文档，持续演化和扩展已生成的知识图谱。

## 适合用户范围

- **AI 开发者与研究人员**： 需要快速构建高级 RAG 系统或多模态知识库的人员。
- **数据处理工程师**： 负责海量非结构化文本清洗与信息抽取的数据科学家。
- **垂直领域专家（金融/法律/医疗）**： 无需深厚代码功底，即可通过内置模板快速从专业长文档中提取关键结构化信息的业务人员。

## 限制和注意

**强依赖大模型 API**： 框架底层默认调用 gpt-4o-mini 和 text-embedding-3-small，用户必须拥有有效的 API Key（如 OpenAI 密钥）并承担相应的 Token 消耗成本。

**幻觉风险评估**： 尽管拥有强大的 Prompt 模板，仍受限于 LLM 的固有特性，在极高严谨要求的业务场景下，仍建议结合人工校验防范"幻觉"。

**网络与隐私**： 调用外部 API 意味着敏感文本将会离开本地，如果处理高度机密的数据，建议配置兼容的本地化开源大模型方案。

## 如何使用（流程概览）

### 1. 安装与配置

对于倾向于命令行的用户，可以使用 uv 进行全局安装：

```bash
uv tool install hyperextract
```

初始化你的 API 密钥：

```bash
he config init -k YOUR_OPENAI_API_KEY
```

### 2. 核心指令操作

**文档提取**： 使用内置模板将文档提取为结构化图谱：

```bash
he parse examples/en/tesla.md -t general/biography_graph -o ./output/
```

**检索与问答**： 基于提取出来的知识直接进行提问：

```bash
he search ./output/ "特斯拉的主要成就是什么？"
```

**可视化查看**： 本地一键渲染并展示生成的知识图谱：

```bash
he show ./output/
```

**增量喂入**： 补充新文档，让系统自动更新图谱：

```bash
he feed ./output/ new_doc.md
```

注：开发者也可以通过 `uv pip install hyperextract` 将其作为 Python 库引入，利用 `Template.create()` 等 API 在代码中灵活调用。

---

**GitHub**: https://github.com/yifanfeng97/Hyper-Extract/
