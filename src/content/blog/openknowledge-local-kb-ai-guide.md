---
title: "OpenKnowledge：普通人用 AI 搭建私人本地知识库的完整指南"
titleEn: "OpenKnowledge: A Complete Guide to Building Your Personal Local KB with AI"
description: "Inkeep 开源的 AI-native Markdown 编辑器，Notion 遇上 VSCode 的体验，用 Claude/Codex/Cursor 帮你写入、整理、维护本地知识库。本文基于 Karpathy LLM Wiki 模式，手把手教你从零搭建一个真正「越用越聪明」的个人知识库——完全本地、完全免费、不依赖向量数据库。"
descriptionEn: "OpenKnowledge is an open-source AI-native markdown editor (think Notion meets VSCode) where Claude, Codex, or Cursor actively writes and maintains your knowledge base. This guide walks through building a personal KB using Karpathy's LLM wiki pattern — local, free, no vector database needed."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Tech-Experiment"
tags: ["知识库", "AI工具", "开源", "本地优先", "Claude", "Markdown", "个人知识管理", "LLM"]
heroImage: "../../assets/images/openknowledge-local-kb-ai-guide-banner.jpg"
---

> **GitHub**: [Inkeep/open-knowledge](https://github.com/Inkeep/open-knowledge) · ⭐ 1,773 · GPL-3.0  
> **官网**: [openknowledge.ai](https://openknowledge.ai) · **最新版本**: v0.24.0（2026-07-02）  
> **支持平台**: macOS（Apple Silicon 原生 App）+ Linux/Windows/Intel Mac（CLI + Web UI）

---

## 你的知识为什么总是"丢失"？

你可能也有这样的经历：

- 收藏夹里有几百个链接，从来不回去看
- Notion 笔记越记越多，但搜索的时候根本找不到想要的
- 用 RAG 方案接了一个"知识库助手"，但它的回答和实际文档之间总有说不清楚的偏差
- 笔记记了，但自己从来不整理，最后就是一堆乱文件

这些方案的共同问题：**维护成本在你身上**。你要负责整理、分类、关联——而这正是人类最不擅长坚持的事情。

**OpenKnowledge** 换了一种思路：让 AI Agent 来负责整理，你只需要提供原材料。

---

## OpenKnowledge 是什么？

一句话：**AI-native 的本地 Markdown 编辑器**，你写 / AI 整理，文件存本地，你随时能读。

它由三层构成：

```
┌─────────────────────────────────────────────────────┐
│  Layer 1：编辑器 (Editor)                            │
│  WYSIWYG Markdown，像写 Notion 一样，但底层是 .md 文件│
├─────────────────────────────────────────────────────┤
│  Layer 2：Agent 工具 (MCP / Skills)                  │
│  Claude、Codex、Cursor 通过 MCP 直接读写你的知识库    │
├─────────────────────────────────────────────────────┤
│  Layer 3：内容 (Content)                             │
│  普通 Markdown 文件，Git 管理，没有黑盒格式            │
└─────────────────────────────────────────────────────┘
```

和其他方案的对比：

| 方案 | 谁来整理？ | 存在哪里？ | 能直接读吗？ | 时间越久越好还是越乱？ |
|---|---|---|---|---|
| 普通笔记 | 你 | 本地 | ✅ | 越乱 |
| Notion | 你 | 云端 | ✅ | 越乱 |
| RAG 向量库 | 你（源文档）+ 向量化 | 数据库 | ❌（索引是黑盒） | 维护成本高 |
| **OpenKnowledge** | **AI Agent** | **本地 .md 文件** | **✅** | **越聪明** |

---

## 安装方法

### macOS（Apple Silicon，推荐）

下载 DMG → 拖入 Applications → 启动。

[点此下载最新版](https://github.com/inkeep/open-knowledge/releases/latest/download/OpenKnowledge-arm64.dmg)

### Linux / Windows / Intel Mac（CLI 方式）

需要 Node.js 24+（[nodejs.org](https://nodejs.org) 下载）和 git：

```bash
# 安装命令行工具（一次）
npm install -g @inkeep/open-knowledge

# 进入你的项目文件夹（或新建）
mkdir my-knowledge-base && cd my-knowledge-base

# 初始化：自动检测并配置 Claude Code / Cursor / Codex
ok init

# 启动编辑器，在浏览器里打开
ok start --open
```

`ok init` 会自动检测你电脑上安装的 AI Agent（Claude Code、Cursor、Codex），并完成 MCP 配置——不需要手动配置。

---

## 核心概念：Karpathy 的 LLM Wiki 模式

OpenKnowledge 内置了 **Andrej Karpathy（特斯拉前 AI 总监）** 提出的知识库组织模式。

### 三层文件结构

```
my-knowledge-base/
├── external-sources/   ← 原始资料（只读，不修改）
│   ├── paper-xyz.md
│   ├── github-readme.md
│   └── news-article.md
├── research/           ← 研究笔记（AI 综合，有引用，暂定状态）
│   └── topic-analysis.md
├── articles/           ← 正式文章（确认后晋升到这里）
└── log.md              ← 操作日志（追加，不修改）
```

**关键原则**：
- `external-sources/`：放原始资料，AI **只读不改**，保持原样
- `research/`：AI 综合出来的分析文章，标注 `status: provisional`，每条结论都引用 external-sources 里的具体文件
- `articles/`：经过你确认"没问题"后，从 research 晋升上来的正式内容
- `log.md`：AI 每次操作都追加记录，可审计

这个结构解决了一个核心问题：**知识库不再因为 AI 乱改而腐烂**——原始资料不可动，分析内容有引用链，你看到的每个结论都能追溯来源。

---

## 5 步搭建你自己的知识库

### 第 1 步：创建项目

**macOS App**：
1. 打开 OpenKnowledge
2. 点击「Create new project」
3. 输入项目名（如：个人技术研究库）
4. 点击「Create」

**CLI**：
```bash
mkdir ~/my-kb && cd ~/my-kb
ok init
ok start --open
```

### 第 2 步：初始化 Knowledge base 模板

在编辑器的空白起始页，点击「Pick a starter pack」→ 选择 **Knowledge base** → 确认根目录位置 → 点击「Apply」。

这一步会自动创建 `external-sources/`、`research/`、`articles/` 文件夹，以及 `log.md`，并为每个文件夹写好让 AI 能读懂的"规则说明"——不需要你手写 CLAUDE.md。

### 第 3 步：接入你的 AI Agent

如果你安装了 Claude Code、Cursor 或 Codex，`ok init` 已经自动配置好了 MCP。验证一下：

在你的 AI Agent 里输入：
```
OpenKnowledge 里有哪些可用工具？
```

你应该能看到 `mcp__open-knowledge__workflow`、`mcp__open-knowledge__search`、`mcp__open-knowledge__write` 等工具出现。

### 第 4 步：让 AI 帮你"录入"资料

这是最核心的操作。把你想归档的内容（链接、文章、论文、笔记）发给 AI，说：

```
帮我把这个链接的内容录入知识库：https://...
```

AI 会：
1. 抓取内容
2. 调用 `ingest` 工具
3. 在 `external-sources/` 里创建带 frontmatter 的 Markdown 文件（记录来源 URL、抓取时间、作者信息）
4. 在 `log.md` 里追加操作记录

录完几个资料后，说：

```
帮我综合一下 external-sources 里关于 [某个主题] 的内容，写一篇研究笔记放到 research/ 里
```

AI 会读取所有相关原始资料，综合成一篇引用链完整的分析文章，放到 `research/agent-framework-evaluation.md`（status: provisional）。

### 第 5 步：日常使用——问问题

之后，你不用再去翻原始资料了。直接问 AI：

```
我的知识库里关于 [某个问题]，有什么结论？
```

AI 会搜索 `research/` 和 `external-sources/`，循着引用链给你一个有据可查的答案——而不是凭空捏造。

---

## 关键功能亮点

### WYSIWYG 编辑体验

不用关心 Markdown 语法，就像写 Google Doc 或 Notion 一样。需要看原始 Markdown？一键切换 Source 模式。两个视图共用同一个文档，AI Agent 通过 MCP 写的内容会实时显示在你的编辑器里。

### 知识图谱 & Wiki 链接

文档之间可以互相 `[[链接]]`，右侧面板显示：
- 当前文档的**大纲**
- **入链和出链**（哪些文档引用了这篇，这篇引用了哪些）
- **图谱视图**（可视化知识关联）

### 时间线 & 版本恢复

AI 每次编辑都留下独立记录，可以：
- 查看每次 AI 操作的 diff（改了什么）
- 选择性回滚某次 AI 的修改（不影响其他内容）
- 按时间轴浏览知识库的演变历史

### 不需要向量数据库

AI 的搜索是**直接搜索 Markdown 文件**（grep + 跟踪 backlinks），没有"向量化"这一步，也没有"索引和原文不同步"的问题。你看到的结构就是 AI 实际搜索的结构。

### 真正的本地优先

所有内容是普通 `.md` 文件，存在你的磁盘上。Git 管理版本。没有云服务依赖，没有账号注册，没有月费。

---

## 实际使用场景

### 技术研究库
每次读论文、看技术博客，录入 external-sources，让 AI 综合到 research 笔记里。一个月后你有一个真正可以检索的技术知识库，而不是一堆书签。

### 学习笔记
把课程讲义、教程 URL、代码示例全部录入，AI 帮你整理成主题化的 research 笔记。有问题直接问，AI 从你自己的学习资料里找答案。

### 工作项目文档
把需求文档、会议记录、设计文档放进去，AI 负责整理和关联。再也不需要花时间搜"那个决策是什么时候在哪个文档里做的"。

### 个人兴趣领域跟踪
追踪某个领域（AI / 投资 / 某项技术）的最新动态，每次看到好内容就录入，AI 负责和已有内容整合，帮你找新旧知识的联系。

---

## 可选进阶：团队共享

如果你想和团队共享知识库：

1. 在编辑器里开启 **Auto-sync**（基于 Git/GitHub）
2. 知识库自动推送到 GitHub 私仓
3. 团队成员各自打开，AI 编辑时实时协作（CRDT 同步）

不需要额外的服务器，Git 就是后端。

---

## 快速上手总结

```
第一步：安装
  macOS Apple Silicon → 下载 DMG，拖入 Applications
  其他平台 → npm install -g @inkeep/open-knowledge

第二步：新建项目
  App：Create new project
  CLI：mkdir my-kb && cd my-kb && ok init && ok start --open

第三步：初始化模板
  空白页面 → Pick a starter pack → Knowledge base → Apply

第四步：接入 AI Agent
  ok init 已自动配置，直接在 Claude Code/Cursor 里使用

第五步：录入内容
  发给 AI："帮我录入这个链接" → AI 写入 external-sources

第六步：让 AI 整理
  发给 AI："综合一下 [主题] 的内容，写到 research/" → AI 完成

第七步：日常使用
  直接问 AI 问题，它从你的知识库里找有引用的答案
```

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub 仓库 | https://github.com/Inkeep/open-knowledge |
| 官网 | https://openknowledge.ai |
| macOS 下载 | https://github.com/inkeep/open-knowledge/releases/latest |
| 快速开始文档 | https://openknowledge.ai/docs/get-started/quickstart |
| Karpathy LLM Wiki 工作流 | https://openknowledge.ai/docs/workflows/karpathy-llm-wiki |
| Discord 社区 | https://discord.com/invite/YujKpFN49 |
| X (Twitter) | https://x.com/OpenKnowledgeAI |
| 原始 Karpathy Gist | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: OpenKnowledge (1,773 ⭐, GPL-3.0) is a local-first AI-native markdown editor where Claude, Codex, or Cursor actively writes and organizes your knowledge base via MCP. Built on Karpathy's LLM wiki pattern: raw sources go into `external-sources/` (immutable), AI synthesizes them into `research/` (cited, provisional), you promote to `articles/` when confident. No vector database — agents search your live markdown files directly. Everything stays on your disk as plain `.md` files.

---

## Why Your Notes Always Get Lost

Most note-taking approaches fail the same way: maintenance burden stays with you. You're responsible for organizing, categorizing, and linking — exactly what humans are worst at sustaining over time.

OpenKnowledge flips this: the AI agent handles organization. You supply raw material.

## Three Layers

```
Editor:  WYSIWYG markdown (like Notion, but files stay local)
Agents:  Claude / Codex / Cursor write via MCP in real-time  
Content: Plain .md files, git-versioned, nothing proprietary
```

## The Karpathy Pattern

Andrej Karpathy's LLM wiki structure (built into OpenKnowledge's Knowledge Base starter pack):

| Folder | Role | Who touches it |
|---|---|---|
| `external-sources/` | Raw sources, verbatim + metadata | AI ingests, never edits |
| `research/` | Cited synthesis, status: provisional | AI writes, you review |
| `articles/` | Confirmed canonical knowledge | You promote from research |
| `log.md` | Append-only audit trail | AI appends per operation |

Key insight: every claim in `research/` cites a specific file in `external-sources/`. You can always trace where a conclusion came from.

## Quick Start (CLI)

```bash
npm install -g @inkeep/open-knowledge
mkdir my-kb && cd my-kb
ok init          # auto-configures Claude Code / Cursor / Codex via MCP
ok start --open  # opens editor in browser
```

macOS Apple Silicon: download the [desktop app DMG](https://github.com/inkeep/open-knowledge/releases/latest) instead.

## Daily Workflow

1. **Ingest** — paste a URL or paste text, tell AI to ingest it → lands in `external-sources/`
2. **Research** — ask AI to synthesize a topic → AI writes a cited `research/` note
3. **Query** — ask a question → AI searches your files and cites sources, not hallucination
4. **Promote** — when you're confident in a research note, AI moves it to `articles/`

## What Makes It Different

- **No vector database** — agents grep and follow backlinks across live markdown files
- **Local first** — your files, your disk, git for version control, no cloud lock-in
- **CRDT collaboration** — you and multiple AI agents can edit the same doc simultaneously; see per-burst agent diffs, selectively roll back
- **Timeline recovery** — every AI edit is tracked; revert specific agent sessions without losing your own edits
- **Knowledge graph** — wiki links `[[like this]]` with graph visualization of connections

**Links**: [GitHub](https://github.com/Inkeep/open-knowledge) · [Docs](https://openknowledge.ai/docs) · [Download](https://github.com/inkeep/open-knowledge/releases/latest)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
