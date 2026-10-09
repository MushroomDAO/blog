---
title: "自然语言问 SQLite：用 Vercel Eve + Qwen 搭数据分析 Agent"
titleEn: "Natural Language Over SQLite: Building a Data Analyst Agent with Vercel Eve and Qwen"
description: "Sumanth077/Hands-On-AI-Engineering 子项目 nl_data_analyst_agent：用自然语言提问 SQLite 数据库的 Agent 实现。技术栈：Vercel Eve 0.63.0 作为 Agent 运行时，Qwen3.8 Omni Flash（经 Vercel AI Gateway）生成只读 SQL，TypeSafe Jev 在提问前/SQL执行前/回答后三个节点做结构化 Review，Gradio 提供 Web UI 和审批控制。全部代码开放，可以作为 AI 工程实战的参考起点。父仓库 Hands-On-AI-Engineering 收集了 OCR、RAG、Agent 等多个 AI 工程实战项目，3,945 stars，作者 Sumanth 是印度 ML 工程师兼 YouTuber。"
descriptionEn: "nl_data_analyst_agent from Sumanth077/Hands-On-AI-Engineering: a working implementation of a natural-language-over-SQLite data analyst agent. Stack: Vercel Eve 0.63.0 as the agent runtime, Qwen3.8 Omni Flash via Vercel AI Gateway for read-only SQL generation, TypeSafe Jev for structured review at three checkpoints (before the question, before SQL execution, after the answer), and Gradio for the web UI and approval controls. The parent repo Hands-On-AI-Engineering (3,945 stars) collects OCR, RAG, and Agent hands-on projects by Sumanth, an ML engineer and YouTuber from India."
pubDate: 2026-10-09
heroImage: "../../assets/images/nl-data-analyst-agent-vercel-eve-qwen-sqlite-natural-language-banner.jpg"
category: "Tech-Experiment"
tags: ["AI Agent", "数据分析", "开源工具", "Vercel", "教程"]
lang: "zh-CN"
wechatTitle: "自然语言问数据库：AI分析Agent实战"
wechatDigest: "Vercel Eve+Qwen3.8+TypeSafe Jev三点Review；SQLite只读；Gradio审批UI"
---

"这张表里销售额最高的品类是什么？"——不用写 SQL，直接问。

nl_data_analyst_agent 是 Sumanth 在 Hands-On-AI-Engineering 仓库里的一个实战例子：用自然语言提问本地 SQLite 数据库，Agent 自动生成只读 SQL、执行、返回结果。整个链路开放，可以作为构建类似系统的参考起点。

GitHub: https://github.com/Sumanth077/Hands-On-AI-Engineering（子目录 ai_agents/nl_data_analyst_agent）| ⭐ 3,945（父仓库）

---

## 技术栈

| 层级 | 选择 |
|------|------|
| Agent 运行时 | Vercel Eve 0.63.0（TypeScript） |
| 语言模型 | Qwen3.8 Omni Flash（通过 Vercel AI Gateway） |
| 结构化 Reviewer | TypeSafe Jev |
| 工具层 | TypeScript + Zod + Node SQLite |
| Web UI | Gradio（Python） |
| 数据库 | SQLite |
| Python 依赖管理 | uv |
| Node 依赖管理 | pnpm |

---

## 三个 Review 节点

这个实现的核心设计是在链路的三个位置插入 Jev Review：

**1. 提问前**：检查用户问题是否清晰、可回答。模糊的问题在这一步被拦截，要求用户澄清。

**2. SQL 执行前**：Jev 检查生成的 SQL 是否和问题相关，有没有超出只读边界。这是一个安全门——防止模型生成 DELETE 或 UPDATE 语句。

**3. 回答后**：检查模型给出的自然语言回答是否和查询结果一致，有没有出现幻觉或过度解读。

三个节点形成一个完整的"提问→生成SQL→执行→回答"质量闭环。

---

## 文件结构

```
nl_data_analyst_agent/
├── agent/
│   ├── agent.ts          ← Vercel Eve Agent 配置
│   └── tools/            ← SQL 工具（Zod schema 定义）
├── main.py               ← Gradio 客户端入口
├── jev_review.py         ← Jev 三点 Review 实现
├── seed_data.py          ← 演示用 SQLite 数据库
└── assets/
    └── demo.gif          ← 演示动图
```

---

## 运行方式

```bash
# 安装 Node 依赖（pnpm）
cd agent && pnpm install

# 安装 Python 依赖（uv）
uv pip install gradio httpx pandas matplotlib

# 初始化演示数据库
python seed_data.py

# 启动 Agent
cd agent && pnpm start

# 启动 Gradio UI
python main.py
```

打开 Gradio 界面后，直接用自然语言提问即可，审批控件显示中间步骤。

---

## 适合谁参考

- 想理解 Vercel Eve Agent 运行时怎么接工具的
- 需要给内部 SQLite 数据库加一个自然语言查询界面
- 学习如何在 Agent 链路里插入结构化 Review 点（Jev）
- 作为 AI 工程课程或个人项目的起点

**依赖说明**：Vercel AI Gateway（Qwen3.8 Omni Flash）需要 Vercel 账号，SQLite 工具层需要 Node 18+，Python 部分需要 uv。

---

## 父仓库

Hands-On-AI-Engineering（3,945 stars）收集了 Sumanth 制作的多个 AI 工程实战项目：OCR 系统、RAG 流水线、各类 Agent 实现。Sumanth 是印度 ML 工程师，也是 AI 领域 YouTuber，主页：https://aiengineering.beehiiv.com。nl_data_analyst_agent 是这个系列里 Agent 方向的一个典型例子。

---

> 父仓库无指定开源许可证。Sumanth077/Hands-On-AI-Engineering，仅供学习参考。

---

<!--EN-->

## Natural Language Over SQLite: Building a Data Analyst Agent with Vercel Eve and Qwen

"What's the top-selling category in this table?" — no SQL needed, just ask.

nl_data_analyst_agent is a hands-on example from Sumanth's Hands-On-AI-Engineering repo: natural-language queries over a local SQLite database, where the agent generates read-only SQL, executes it, and returns results. The full implementation is open, usable as a reference starting point.

GitHub: https://github.com/Sumanth077/Hands-On-AI-Engineering (subdirectory: ai_agents/nl_data_analyst_agent) | ⭐ 3,945 (parent repo)

---

### Stack

| Layer | Choice |
|-------|--------|
| Agent runtime | Vercel Eve 0.63.0 (TypeScript) |
| LLM | Qwen3.8 Omni Flash via Vercel AI Gateway |
| Structured reviewer | TypeSafe Jev |
| Tool layer | TypeScript + Zod + Node SQLite |
| Web UI | Gradio (Python) |
| Database | SQLite |

---

### Three Review Checkpoints

The key design: TypeSafe Jev review inserted at three points in the pipeline.

**1. Before the question**: Is the user's question clear and answerable? Ambiguous questions are flagged before any SQL is generated.

**2. Before SQL execution**: Is the generated SQL relevant to the question? Does it stay within read-only bounds? This is a safety gate — prevents the model from generating DELETE or UPDATE statements.

**3. After the answer**: Does the natural-language response match the query results? Guards against hallucination or over-interpretation.

Three checkpoints form a complete quality loop around the question → SQL → execute → answer pipeline.

---

### Who Should Reference This

- Understanding how Vercel Eve connects tools in an agent runtime
- Adding a natural-language query interface to an internal SQLite database
- Learning how to insert structured review points (Jev) into an agent pipeline
- A starting point for AI engineering coursework or personal projects

---

> No license specified in parent repo. Sumanth077/Hands-On-AI-Engineering. For technical reference only.
