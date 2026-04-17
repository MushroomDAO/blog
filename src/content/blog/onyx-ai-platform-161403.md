---
title: "个人AI工作台：Onyx——开源的团队AI知识中枢"
titleEn: "onyx-ai-platform"
description: "Onyx 是一个开源 AI 平台，连接 40+ 数据源，集成 RAG 检索、多模型兼容、AI Agent 自动化与企业级自托管，让 AI 真正融入个人和团队的日常工作流。"
descriptionEn: "Onyx is an open-source AI platform connecting 40+ data sources with RAG, multi-model support, AI agents, and self-hosted enterprise security — making AI a real part of your daily workflow."
pubDate: "2026-04-17"
category: "Tech-News"
tags: ["Onyx", "开源", "AI工作台", "RAG", "知识库", "自托管", "AI Agent", "个人AI"]
heroImage: "../../assets/images/onyx-ai-platform-cover.jpg"
---

> 原文链接：[github.com/onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx)

---

## 什么是 Onyx？

你有没有遇到过这样的场景：

- 问题答案分散在 Slack、Notion、Google Drive、Confluence 的不同角落
- AI 聊天给的答案不结合你自己的私有数据，总感觉不够准确
- 想让 AI 帮你自动化一些重复流程，但现有工具做不到

**Onyx** 就是为了解决这些问题而生的开源 AI 平台。

它不是一个简单的聊天机器人，而是一个**"AI 超级助手工厂"**——把知识库、搜索、AI 聊天、自动化这些分散的能力整合到一个统一平台里，真正融入个人和团队的日常工作流。

---

## 六大核心能力

### 1. 全面的知识整合（40+ 数据源）

Onyx 支持连接超过 40 种数据源：

| 类型 | 支持的工具 |
|------|-----------|
| 协作工具 | Slack、Notion、Confluence |
| 文件存储 | Google Drive、本地文件系统 |
| 项目管理 | Jira、GitHub、Linear |
| 以及更多 | Salesforce、Zendesk、Web 爬取…… |

数据自动索引、持续更新，构建出一个统一的、AI 可访问的私有知识库。

---

### 2. 先进的 RAG 检索

Onyx 内置**混合检索增强生成（RAG）**技术。

普通 AI 聊天只依靠模型预训练的知识。Onyx 的 AI 回答时会同时检索你的私有数据——答案不仅更准确，还带有来源引用，可追溯、可验证。

> 举例：问"我们 Q2 的产品路线图是什么？"——Onyx 会从你的 Confluence/Notion 里找到最新的文档，结合 AI 给出精准回答。

---

### 3. 多模型兼容，自由切换

Onyx 不绑定任何一家 LLM 厂商：

- **商业模型**：GPT-4o、Claude 3.5、Gemini
- **开源模型**：Llama 3、Mixtral、本地 Ollama

根据场景、预算、隐私要求自由切换。本地敏感数据用本地模型处理，复杂推理用云端高性能模型——完全由你决定。

---

### 4. AI Agent 与自动化

Onyx 允许创建具备行动能力的 AI Agent：

- 不只回答问题，还能**执行多步任务**
- 通过 **MCP（Model Context Protocol）** 扩展，与外部工具和系统交互
- 实现业务流程自动化：自动生成周报、更新项目状态、汇总 Slack 讨论……

---

### 5. 深度研究 + 代码执行

- **深度研究**：自动搜索并综合分析多方信息，给出有依据的深度回答
- **代码执行**：直接运行生成的 Python 代码，在对话中完成数据分析和处理

---

### 6. 企业级安全与完全自托管

对于数据安全有高要求的个人和团队：

- **完全自托管**：Docker 或 Kubernetes 一键部署，数据不经过任何第三方服务器
- **Air-gapped 支持**：在完全隔离的内网环境运行，私有数据绝不外泄
- **开源透明**：代码完全开放，安全实现可审计

---

## 为什么值得关注？

从 Aura AI 的视角看，Onyx 是一个非常典型的**个人 AI 工作台**样本：

**本地优先**：支持完全自托管和离线运行，符合我们倡导的"本地优先"原则——数据主权在用户自己手里。

**AI 平权工具**：开源意味着没有使用门槛，个人开发者和小团队可以用企业级 AI 能力，不需要为昂贵的 SaaS 订阅付费。

**人+AI 协作的实践**：Onyx 的设计理念是让 AI 成为团队知识工作流的一部分，而不是替代人——这与我们研究的"人+AI 协作单元"高度契合。

---

## 快速开始

```bash
# Docker 部署（推荐）
git clone https://github.com/onyx-dot-app/onyx
cd onyx/deployment/docker_compose
docker compose -f docker-compose.dev.yml up -d
```

访问 `http://localhost:3000` 即可开始使用。

详细文档和更多部署方式：[github.com/onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx)

---

*Aura AI · Tech-News · 开源工具推荐*
