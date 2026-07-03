---
title: "Wiki Memory：LangChain CEO 预言的 Agent 记忆新范式，开发者深度解读"
titleEn: "Wiki Memory: The Agent Memory Pattern LangChain CEO Predicts Will Win — Developer Deep Dive"
description: "Harrison Chase（LangChain CEO）在最新文章中提出 Wiki Memory 作为 AI Agent 长期记忆的新兴标准模式——不是 RAG，不是对话历史，而是让 Agent 把原始数据压缩成可维护的知识库文件。本文深度解读这篇文章的核心观点，并给出开发者实践指南。"
descriptionEn: "Harrison Chase (LangChain CEO) proposes wiki memory as the emerging standard for AI agent long-term memory — not RAG, not conversation history, but an agent-maintained compressed knowledge base. Developer deep dive with practical implementation guidance."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Research"
tags: ["AI Agent", "记忆系统", "Wiki Memory", "LangChain", "RAG", "知识库", "开发者", "Harrison Chase"]
heroImage: "../../assets/images/langchain-wiki-memory-developer-analysis-banner.jpg"
---

> **原文**: [langchain.com/blog/wiki-memory](https://www.langchain.com/blog/wiki-memory)  
> **作者**: Harrison Chase — LangChain 联合创始人 & CEO  
> **核心论点**: Agent 记忆还没有标准，但 Wiki Memory 这个模式正在浮现

---

## 一句话背景

AI Agent 要"记住东西"，现在的方案五花八门——对话历史、向量数据库、用户偏好、事件日志……每个团队对"记忆"的理解都不一样。

Harrison Chase 在这篇文章里提出了一个正在浮现的共识：**Wiki Memory**。

这不是新技术，而是一种新的**架构模式**——简单、可检查、基于文件，用 Agent 来创建和维护，让未来的 Agent 能高效利用。

---

## 核心观点解读（逐点分析）

### 观点一：Agent 记忆的本质问题

> "Memory for agents is still early, with little to no standards."

原始数据（日志、笔记、代码、Slack 线程、会议记录）包含大量知识，但直接塞给 Agent 有两个问题：

1. **太嘈杂**：原始数据有太多无关信息
2. **太大**：超出 context window，每次都要重新检索

解决方案：**预处理**。不是在查询时检索原始数据，而是提前把它压缩成更密集的表示。

### 观点二：Wiki Memory 和 RAG 的根本区别

这是文章最重要的洞察，也是很多开发者容易混淆的地方：

| | **RAG** | **Wiki Memory** |
|---|---|---|
| 什么时候处理 | 查询时动态检索 | **提前预处理、维护** |
| 存的是什么 | 原始文本 chunks | **合成后的结构化知识** |
| Agent 每次需要做什么 | 重新理解原始片段 | 直接读取已整理好的知识 |
| 时间成本 | 查询时较高 | 查询时很低（写入时较高） |
| 可检查性 | 低（embedding 是黑盒） | **高（就是 Markdown 文件）** |

用他的话说：

> "RAG usually retrieves raw chunks at query time. A wiki precomputes and maintains a higher-level synthesis, so the agent does not have to rediscover the structure every time."

### 观点三：什么是"Wiki"？

他给出了一个精确的定义：

> "A wiki is an agent-maintained data structure that represents source knowledge in an agent-friendly way."

关键词：
- **Agent-maintained**：不是人手动写，是 Agent 自动创建和更新
- **Persistent**：持久化，重启不丢
- **Structured**：有结构，方便 Agent 检索
- **Inspectable**：人类可以直接读（不是向量，是文件）
- **Updated over time**：随着新数据到来持续更新

不需要字面上像维基百科，核心是这五个属性。

### 观点四：真实世界案例

文章提到了三个已经在做这件事的产品：

**[DeepWiki by Cognition](https://cognition.ai/blog/deepwiki)**  
为 GitHub 仓库生成 AI 文档。给人类和编码 Agent 一个代码库的高层心智地图。

**[Karpathy 的 LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)**  
更通用的版本：不只针对代码，可以处理任意来源文件。LLM 增量构建并维护一个持久 Markdown wiki，作为用户和原始资料之间的中间层。

**[Factory AutoWiki](https://factory.ai/news/wiki)**  
类似 DeepWiki，分析代码库并生成结构化、可浏览的文档，随 repo 变化保持更新。

这三个都是 wiki memory 在代码/文档领域的具体实例。

### 观点五：四个核心开放问题

Harrison Chase 诚实地承认这个模式还有很多未解决的问题：

```
1. 原始数据是什么？
   → 当前答案：任何 Agent 可以读取或访问的东西

2. 压缩后的数据用什么格式最好？
   → 当前答案：文件（Markdown）

3. 如何压缩数据？
   → 当前答案：用 Agent

4. 如何保持压缩表示的更新？
   → 当前答案：用 Agent
```

这四个"用 Agent"的答案看起来简单，但背后有深刻的设计选择：**文件是最优基底**。

> "Files are attractive because they are inspectable, editable, versionable, and easy for agents to read and write."

---

## 开发者实践指南

### 何时选择 Wiki Memory vs 其他方案？

| 记忆类型 | 适用场景 | 方案 |
|---|---|---|
| **Wiki Memory** | 持久的领域知识、可复用的知识库 | 文件 + Agent 维护 |
| 短期对话状态 | 当前会话上下文 | 对话历史 |
| 用户偏好 | 个人化、简单键值 | 数据库或 JSON 文件 |
| 高频事件日志 | 系统日志、操作记录 | 专用日志系统 |

文章明确说：**Wiki 不是记忆的全部，它最适合持久的领域知识**。

### 最简单的实现方式

```python
# 概念级示例：Wiki Memory 的基本结构
import os
from pathlib import Path

WIKI_DIR = Path("./wiki")
RAW_DATA_DIR = Path("./raw-sources")

def ingest_new_source(source_path: str, agent_client):
    """把新资料录入 wiki"""
    raw_content = open(source_path).read()
    
    # 让 Agent 把新内容整合进现有 wiki
    prompt = f"""
    以下是新的原始资料：
    {raw_content}
    
    请：
    1. 识别这份资料里的关键概念和知识点
    2. 检查 {WIKI_DIR} 里的现有 wiki 文件
    3. 更新或创建相关 wiki 页面，每条结论注明来源文件
    4. 如果有新的关键实体，创建对应的 wiki 页面
    5. 在 log.md 里追加本次操作记录
    """
    
    agent_client.run(prompt, working_dir="./")

def query_wiki(question: str, agent_client):
    """基于 wiki 回答问题"""
    prompt = f"""
    基于 {WIKI_DIR} 里的知识库，回答：{question}
    
    要求：
    - 只引用 wiki 里有的内容
    - 每个观点注明来自哪个 wiki 页面
    - 如果知识库里没有足够信息，说明缺少什么
    """
    
    return agent_client.run(prompt)
```

### 与现有生态的关系

文章把 Wiki Memory 和这几个系统做了对比：

| 系统 | 定位 | 关系 |
|---|---|---|
| **LangMem** | 通用 Agent 记忆 | Wiki 是其一个子集 |
| **Letta** | Agent 记忆管理 | 类似，但 wiki 用文件更简单 |
| **Mem0** | 个性化记忆层 | 偏用户偏好，wiki 偏领域知识 |
| **Zep** | 长期记忆平台 | 类似，wiki 可作为其中一层 |

Harrison Chase 的判断是：这些系统解决的是更广泛的 Agent 记忆问题，而 Wiki Memory 之所以值得单独拿出来说，是因为它用了**最简单的底层基底（文件）**，却能覆盖很多实际需求。

---

## 为什么这个观点在现在特别重要

### 背景：Agent 应用正在进入"记忆期"

2025 年以前，大多数 Agent 应用都是无状态的——每次对话从头开始。2026 年，有状态、有记忆的 Agent 应用开始成为主流需求。

但"记忆"太复杂了：
- 向量数据库难以维护、不透明、成本高
- 完整对话历史太长，不适合长期积累
- 没有统一标准，每个团队重复造轮子

Wiki Memory 提供了一条**务实的中间路径**：
- 用文件，所有人都会用
- 用 Agent 维护，不需要人工整理
- 结果是可读的 Markdown，可检查、可版本控制

### "脑克隆"的商业价值

文章里有一个很有意思的案例：

> "一家研究公司的朋友想把研究人员的知识'克隆'下来，这样即使他们离职，知识也还在。通过看他们的实验记录、笔记和行为，可以近似出这个'大脑克隆'。"

这是一个非常真实的企业痛点：**知识管理**。Wiki Memory 提供的是一种可自动化的知识沉淀机制——不需要人手动写文档，由 Agent 从已有数据里提炼。

---

## 开发者行动清单

根据这篇文章，如果你在构建 Agent 应用：

**✅ 应该做**
- 为你的领域知识建一个 Agent 维护的 wiki（Markdown 文件）
- 把 wiki 分成：`sources/`（原始，只读）→ `wiki/`（合成，Agent 写入）
- 让 Agent 在每次获得新信息时更新 wiki，而不是每次查询时重新推断
- 在 wiki 里追踪引用链（每个结论来自哪个 source）

**❌ 避免**
- 把原始数据直接塞给 Agent 处理（太嘈杂）
- 用向量数据库存所有东西（适合检索，不适合合成知识）
- 手动维护 wiki（让 Agent 来）
- 把 wiki 和用户偏好/对话历史混在一起（不同的记忆类型）

**🔧 推荐工具**
- [OpenKnowledge](https://github.com/Inkeep/open-knowledge)：实现 Karpathy LLM wiki 模式的编辑器
- [LangMem](https://docs.langchain.com/oss/python/concepts/memory)：LangChain 官方记忆框架
- Claude Code / Cursor 的 MCP：直接让 coding agent 读写你的 wiki 文件

---

## 一句话总结

> **Wiki Memory = 让 Agent 把原始数据提炼成压缩的、持久的、可检查的文件知识库，未来的 Agent 不需要重新推断，直接读取结论。**

这不是银弹，但对于需要长期积累的领域知识，这可能是目前**最简单有效**的实现方式。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。  
> 原文作者：Harrison Chase（LangChain CEO）· 原文链接：https://www.langchain.com/blog/wiki-memory

<!--EN-->

> **TL;DR**: Harrison Chase (LangChain CEO) identifies "wiki memory" as the emerging standard pattern for AI agent long-term memory. Unlike RAG (which retrieves raw chunks at query time), wiki memory precomputes a structured, agent-maintained knowledge base in plain files. Persistent, inspectable, versioned, and updatable. Best for durable domain knowledge — not conversation state or user preferences.

---

## What Is Wiki Memory?

> "A wiki is an agent-maintained data structure that represents source knowledge in an agent-friendly way." — Harrison Chase

Five required properties:
1. **Agent-maintained** — the agent creates and updates it, not humans
2. **Persistent** — survives restarts and sessions
3. **Structured** — organized for efficient agent retrieval
4. **Inspectable** — readable by humans (files, not vectors)
5. **Updated over time** — grows as new data arrives

## The Critical Distinction from RAG

| | RAG | Wiki Memory |
|---|---|---|
| When processed | At query time (dynamic) | Upfront (precomputed) |
| What's stored | Raw text chunks | Synthesized structured knowledge |
| Per-query cost | High (re-derive structure) | Low (structure already there) |
| Inspectability | Low (embedding is opaque) | High (it's just markdown files) |

RAG retrieves. Wiki precomputes. For frequently accessed domain knowledge, the wiki pays off fast.

## Why Files?

Files are the simplest possible substrate:
- Inspectable by humans
- Editable by both humans and agents
- Versionable with git
- Easy for agents to read and write
- No special infrastructure needed

## Four Open Questions

1. **What is the raw data?** → Anything an agent can read or access
2. **Best format for compressed data?** → Files (Markdown)
3. **How to compress?** → An agent
4. **How to keep it updated?** → An agent

## When to Use Wiki Memory (vs alternatives)

| Use case | Memory type |
|---|---|
| Durable domain knowledge | ✅ Wiki Memory |
| Short-term conversation state | Conversation history |
| User preferences | Key-value store |
| High-frequency event logs | Dedicated logging system |

## Quickest Implementation Pattern

```
raw-sources/    ← verbatim originals (immutable, agent reads)
     ↓ agent ingests
wiki/           ← synthesized knowledge (agent writes, human readable)
     ↓ 
log.md          ← append-only audit trail
```

Every wiki claim cites a specific source file. Every ingest is logged. This is Karpathy's pattern, formalized.

## Real-World Examples

- **[DeepWiki](https://cognition.ai/blog/deepwiki)** (Cognition): AI-generated wiki for GitHub repos
- **[Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)**: General-purpose agent-maintained wiki from any sources
- **[Factory AutoWiki](https://factory.ai/news/wiki)**: Codebase wiki that updates as the repo changes

**Links**: [Original post](https://www.langchain.com/blog/wiki-memory) · [LangMem docs](https://docs.langchain.com/oss/python/concepts/memory) · [OpenKnowledge](https://github.com/Inkeep/open-knowledge)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
> Original author: Harrison Chase (LangChain CEO)
