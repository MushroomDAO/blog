---
title: "DeepMind Science Skills：开源AI Agent工具包，整合30+科学数据库加速科研"
titleEn: "DeepMind Science Skills: Open-Source AI Agent Toolkit with 30+ Scientific Databases"
description: "Google DeepMind 开源了 Science Skills——一套专为科学发现设计的 AI Agent 能力包，覆盖基因组学、蛋白质结构、药物发现等领域，对接 AlphaGenome、AlphaFold、UniProt 等 30+ 数据库，用 SKILL.md 格式实现 53-92% 的 token 节省。"
descriptionEn: "Google DeepMind open-sourced Science Skills — a specialized AI agent toolkit for scientific discovery covering genomics, protein structure, drug discovery, and more. Connects to AlphaGenome, AlphaFold, UniProt and 30+ databases, with 53-92% token savings via the open SKILL.md standard."
pubDate: 2026-06-04
category: "Tech-News"
tags: ["DeepMind", "AI Agent", "科学发现", "生物信息学", "开源", "AlphaFold", "基因组学", "Gemini"]
heroImage: "../../assets/images/deepmind-science-skills-discovery-banner.jpg"
lang: "zh-CN"
---

## 把几小时的生信分析压缩到几分钟

一个复杂的结构生物信息学分析，正常需要数小时——跨越 AFDB 找蛋白质结构、在 UniProt 核查注释、用 gnomAD 看变异频率、再到 ClinVar 查临床意义。现在，Google DeepMind 把这套流程封装成了 AI Agent 的"技能包"，让代理自己串起来跑。

这就是 **Science Skills**（`google-deepmind/science-skills`）——2026 年 5 月正式开源，当前版本 v1.0.2，Apache 2.0 协议。

## 什么是 Science Skills

Science Skills 本质上是一套**结构化的 Agent 能力扩展包**，遵循开放的 Agent Skills 标准（SKILL.md 格式）。每个"技能"都是一个目录，包含：

- **SKILL.md** — 带 YAML frontmatter 的主指令文件，描述技能的触发时机、用法和参数
- **scripts/** — 调用外部 API、解析数据的辅助脚本
- **references/** — 数据库 schema、字段说明等参考文档

这套格式由 Anthropic 率先推广（Claude Code 的 `.agents/skills/` 即采用同一标准），Google 随后在 Antigravity IDE 中原生支持，并将 Science Skills 作为官方科学扩展包发布。

## 涵盖的科学领域和数据库

Science Skills 覆盖了生命科学研究中的六大领域，共对接 **30+ 数据库和工具**：

### 基因组学与遗传学
- **AlphaGenome** — 单变异功能效应预测（需 API key）
- **ClinVar** — NCBI 临床变异注释数据库
- **dbSNP / gnomAD** — 人群变异频率数据库
- **Ensembl** — 基因注释和基因组浏览
- **NCBI Sequence Fetch** — 序列获取

### 蛋白质结构与分析
- **AlphaFold Database（AFDB）** — DeepMind 蛋白质结构预测数据库，覆盖 2 亿+ 蛋白
- **FoldSeek** — 基于结构的蛋白质相似性搜索
- **PDB** — 蛋白质数据库
- **InterPro** — 蛋白质域和功能位点数据库
- **PyMOL** — 分子可视化工具集成

### 蛋白质信息
- **UniProt** — 全球最大蛋白质序列和功能注释数据库
- **Human Protein Atlas** — 人类蛋白质表达图谱
- **STRING** — 蛋白质相互作用网络
- **Reactome** — 通路分析数据库

### 药物发现与化学
- **ChEMBL** — 生物活性化合物数据库
- **PubChem** — NCBI 化学物质信息库
- **OpenFDA** — 美国 FDA 药品和不良反应数据
- **OpenTargets** — 靶点-疾病关联平台
- **Clinical Trials Database** — 临床试验注册信息

### 基因调控与表达
- **GTEx** — 组织特异性基因表达图谱
- **ENCODE cCREs** — 顺式调控元件数据库
- **JASPAR / UniBind** — 转录因子结合位点数据库
- **UCSC Conservation and TFBS** — 基因组保守性分析

### 文献与知识
- **PubMed** — 生物医学文献
- **Literature Search** — 同时检索 arXiv、bioRxiv、Europe PMC、OpenAlex
- **EMBL-EBI OLS** — 生物本体论查询

## 核心机制：Progressive Disclosure

Science Skills 最关键的设计是**按需加载（Progressive Disclosure）**：

Agent 启动时只加载每个技能的名称和简短描述（几十个 token）；当用户提问时，语义引擎匹配到相关技能后，才将完整的 SKILL.md 指令注入上下文。

这避免了"把所有数据库手册一次性塞给模型"的低效做法，实现了 **53–92% 的 token 节省**，同时让 Agent 的行为更可预期（有明确的分步指令而非让模型自由发挥）。

## 怎么安装和使用

**通过 npx 安装（适用于 Gemini CLI、Claude Code 等）：**

```bash
npx skills add google-deepmind/science-skills/
```

**通过 Google Antigravity 界面：**

在"Build with Google"步骤中勾选 Science 即可一键安装所有科学技能。

部分技能（如 AlphaGenome、OpenAlex）需要 API Key 才能完整使用；ClinVar 等在无 key 情况下依然可用，有 key 可解锁更高速率限制。

## 与 Gemini for Science 的更大图景

Science Skills 是 Google **Gemini for Science** 战略的重要组成部分，该战略还包括：

- **Co-Scientist**（假设生成）— 多 Agent 想法锦标赛，辅助研究者生成假设
- **AlphaEvolve + ERA**（计算发现）— 并行生成和评分数千个代码变体，探索新方法
- **NotebookLM**（文献洞察）— 将科学文献结构化为可搜索表格

四个工具组合，覆盖从文献调研、假设生成、计算实验到数据库查询的完整科研循环。超过 100 所机构正在参与验证，包括斯坦福大学、伦敦帝国理工、Crick 研究所。

## 对 AI 辅助科研的意义

过去，AI 工具要进入科学工作流面临两个障碍：
1. **接入成本高** — 研究者需要自己写 API 调用代码、处理认证和数据格式
2. **上下文爆炸** — 把所有相关知识塞给 LLM 会超出 context window 或产生大量噪声

Science Skills 用"结构化技能包"同时解决了这两个问题：研究者无需写代码，Agent 按需加载专业知识。Google 内部测试显示，一个通常需要数小时的复杂分析可以在几分钟内完成，并在罕见遗传疾病机制研究中产出了新洞见。

这代表一种新的科研工作范式：**研究者定义问题，Agent 负责跨数据库的信息整合和分析流程。**

---

**资源链接：**
- GitHub 仓库：[google-deepmind/science-skills](https://github.com/google-deepmind/science-skills)
- Gemini for Science 博客：[blog.google/innovation-and-ai/technology/research/gemini-for-science-io-2026/](https://blog.google/innovation-and-ai/technology/research/gemini-for-science-io-2026/)
- Google Cloud 技能标准公告：[cloud.google.com/blog/topics/developers-practitioners/level-up-your-agents-announcing-googles-official-skills-repository](https://cloud.google.com/blog/topics/developers-practitioners/level-up-your-agents-announcing-googles-official-skills-repository)

<!--EN-->

## Compressing Hours of Bioinformatics into Minutes

A complex structural bioinformatics analysis typically takes hours — fetching protein structures from AFDB, cross-checking annotations in UniProt, examining variant frequencies in gnomAD, then checking clinical significance in ClinVar. Google DeepMind has now packaged this entire workflow as AI agent "skills," letting agents orchestrate the full pipeline automatically.

That's **Science Skills** (`google-deepmind/science-skills`) — open-sourced in May 2026, currently at v1.0.2, under Apache 2.0.

## What Is Science Skills

Science Skills is a set of **structured agent capability extensions** following the open Agent Skills standard (SKILL.md format). Each skill is a directory containing:

- **SKILL.md** — A YAML-frontmattered instruction file describing when and how to use the skill
- **scripts/** — Helper scripts for calling external APIs and parsing data
- **references/** — Database schemas, field documentation, and supporting references

This format was popularized by Anthropic (Claude Code's `.agents/skills/` uses the same standard). Google adopted it natively in Antigravity IDE and released Science Skills as the official scientific extension package.

## Covered Domains and Databases

Science Skills spans six major life science research domains, connecting to **30+ databases and tools**:

**Genomics & Genetics**: AlphaGenome (regulatory variant prediction), ClinVar, dbSNP, gnomAD, Ensembl, NCBI Sequence Fetch

**Protein Structure**: AlphaFold Database (200M+ structures), FoldSeek (structural search), PDB, InterPro, PyMOL

**Protein Information**: UniProt, Human Protein Atlas, STRING (interaction networks), Reactome (pathway analysis)

**Drug Discovery & Chemistry**: ChEMBL, PubChem, OpenFDA, OpenTargets, Clinical Trials Database

**Gene Regulation & Expression**: GTEx (tissue-specific expression), ENCODE cCREs, JASPAR/UniBind (TF binding sites)

**Literature & Knowledge**: PubMed, multi-source literature search (arXiv, bioRxiv, Europe PMC, OpenAlex), EMBL-EBI OLS

## The Key Mechanism: Progressive Disclosure

The most important design decision in Science Skills is **Progressive Disclosure**:

At startup, only the name and brief description of each skill loads (tens of tokens). When a user query arrives, the semantic engine matches relevant skills and only then hydrates the conversation with full SKILL.md instructions.

This avoids stuffing every database manual into the model at once, achieving **53–92% token savings** while making agent behavior more deterministic (explicit step-by-step instructions instead of free-form generation).

## Installation

**Via npx (works with Gemini CLI, Claude Code, and others):**

```bash
npx skills add google-deepmind/science-skills/
```

**Via Google Antigravity UI:**

Check the Science box at the "Build with Google" step to install all science skills at once.

Some skills (AlphaGenome, OpenAlex) require API keys for full functionality. Others (like ClinVar) work without keys but unlock higher rate limits with one.

## The Broader Gemini for Science Vision

Science Skills is part of Google's **Gemini for Science** strategy, which also includes:

- **Co-Scientist** — Multi-agent hypothesis tournament for idea generation
- **AlphaEvolve + ERA** — Parallel code variation generation and scoring for computational discovery
- **NotebookLM** — Structuring scientific literature into searchable, comparable tables

Together, the four tools cover the complete research cycle from literature review and hypothesis generation to computational experiments and database queries. Over 100 institutions are participating in validation, including Stanford, Imperial College London, and The Crick Institute.

## Significance for AI-Assisted Research

Two barriers have historically blocked AI tools from entering scientific workflows:

1. **High integration cost** — Researchers had to write custom API code, handle authentication, and manage data formats
2. **Context explosion** — Feeding all relevant knowledge to an LLM exceeds context windows or produces excessive noise

Science Skills addresses both simultaneously: researchers skip the code, and agents load specialized knowledge only when needed. Google's internal tests showed a complex analysis that normally takes hours completed in minutes, yielding novel insights about rare genetic disease mechanisms.

This represents a new paradigm for scientific research: **researchers define the problem; agents handle cross-database information integration and analysis pipelines.**

---

**Resources:**
- GitHub: [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills)
- Gemini for Science blog: [blog.google/innovation-and-ai/technology/research/gemini-for-science-io-2026/](https://blog.google/innovation-and-ai/technology/research/gemini-for-science-io-2026/)
- Agent Skills standard announcement: [cloud.google.com/blog/topics/developers-practitioners/level-up-your-agents-announcing-googles-official-skills-repository](https://cloud.google.com/blog/topics/developers-practitioners/level-up-your-agents-announcing-googles-official-skills-repository)
