---
title: "OpenKnowledge + WikiSkill：搭建真正让 Agent 能读懂的知识库"
titleEn: "OpenKnowledge + WikiSkill: Building a Knowledge Base That Agents Can Actually Read"
description: "inkeep/open-knowledge 是一个 AI-native Markdown IDE，内置 MCP、Skills、WYSIWYG 编辑，配合上一篇 WikiSkill 的三层记忆架构，构成完整的 Agent 友好型知识管理闭环。"
descriptionEn: "inkeep/open-knowledge is an AI-native Markdown IDE with built-in MCP, Skills, and WYSIWYG editing. Paired with WikiSkill's three-layer memory architecture from our previous article, it forms a complete agent-friendly knowledge management loop."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: Tech-Experiment
tags: ["AI", "knowledge-base", "agent", "wikiskill", "markdown", "MCP", "open-source"]
heroImage: "../../assets/images/open-knowledge-ai-native-markdown-ide-wikiskill-agent-wiki-banner.jpg"
author: "Mycelium Protocol"
---

上一篇文章我们深入拆解了谷歌 Research 的 **WikiSkill** 论文——一种让 Agent 把执行经验沉淀为持久知识的三层架构（Raw Layer / Wiki Layer / Skills Layer）。结论是：这套机制在工程上完全可以自己实现，但有一个现实问题——**你把知识写到哪里？谁来读？Agent 和人类怎么协作编辑？**

今天这篇，答案来了。

**[inkeep/open-knowledge](https://github.com/inkeep/open-knowledge)** 是一个开源的 AI-native Markdown IDE，3800+ stars，TypeScript 实现，GPL-3.0 协议。它定位自己为"Notion meets VS Code"——真正所见即所得的 Markdown 编辑器，同时内置对 Claude、Codex、OpenCode 等 Agent 的深度集成。

这两个项目放在一起，几乎是天作之合。

---

## OpenKnowledge 是什么

用一句话说：**一个让人和 Agent 都能顺畅读写的 Markdown 知识库 IDE。**

核心能力：

- **真 WYSIWYG**：编辑 Markdown 文件的手感接近 Google Doc / Notion，不需要在源码和预览之间反复切换
- **跨平台桌面 + Web**：macOS / Windows / Linux 桌面 App，也有 CLI 启动的 Web UI，Intel Mac 和服务器也能跑
- **内置 MCP + Skills**：开箱即用，安装时自动检测你电脑上的 Claude Code / Codex / Cursor / OpenCode，写好 MCP 配置和 Skills，让 Agent 能直接做富文档搜索和创作
- **Git 同步**：团队共享和版本控制底层是 git/GitHub，不是私有数据孤岛
- **Embeddable HTML**：工程 spec 和可视化报告里能嵌入富组件，不只是纯文本

topics 里有一个关键词：**`llm-wiki-karpathy`**——这个命名指向 Karpathy 提出的"LLM OS"概念里知识库应该是什么形状的讨论。OpenKnowledge 明确把自己定位为 LLM Wiki 的标准工具。

---

## 和 WikiSkill 的对接点在哪里

WikiSkill 定义了知识应该怎么组织：

```
workspace/
├── raw/           # 不可变执行轨迹
├── wiki/
│   ├── patterns/  # 单个 Markdown 模式文件
│   ├── logs.md    # 时序演化日志
│   ├── skill-impact.md  # Accept/Reject 历史 + diff
│   └── index.md   # 模式目录索引
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── PURPOSE.md
```

OpenKnowledge 能直接打开这个目录结构，提供：

1. **人类可读的 WYSIWYG 视图**：`wiki/patterns/*.md` 每个模式文件在 OpenKnowledge 里渲染成漂亮的文档，不是裸 Markdown 源码
2. **图谱视图**：OpenKnowledge 内置 wiki link 图谱，`[[pattern-name]]` 跨文件链接自动可视化
3. **Agent 写、人类审**：WikiSkill 的 Wiki Maintainer Agent 往 `patterns/` 写文件，人类在 OpenKnowledge 里 review，侧边 AI 面板可以继续追问
4. **Skills 管理**：OpenKnowledge 的 Skills 系统可以把 `SKILL.md` 的内容直接挂载为 Agent 可调用的 skill，形成闭环

简单说：**WikiSkill 是知识演化的引擎，OpenKnowledge 是这个引擎的驾驶舱。**

---

## 快速上手：5 分钟搭一个 Agent Wiki

### 方式一：桌面 App（推荐）

从 [openknowledge.ai/download](https://openknowledge.ai/download) 下载：
- **macOS Apple Silicon**：DMG 拖入 Applications
- **Windows 10+**：Setup installer，无需管理员权限
- **Linux**：.deb（Debian/Ubuntu）或 .rpm（Fedora/RHEL）

安装后直接 "Open Folder"，选一个包含 Markdown 文件的目录即可。

### 方式二：CLI + Web（Intel Mac / 服务器）

需要 Node.js 24+：

```bash
npm install -g @inkeep/open-knowledge
cd your-wiki-directory
ok init          # 检测本地 Agent 环境，自动配好 MCP 和 skills
ok start --open  # 启动 Web 编辑器并打开浏览器
```

`ok init` 会扫描你电脑上的 Claude Code、Codex、Cursor 等，自动生成对应的配置。这一步省去了手动配 MCP 的麻烦。

### 配合 WikiSkill 工作流

按上一篇文章搭好 WikiSkill 的 `workspace/` 目录后：

```bash
cd workspace
ok init
ok start --open
```

OpenKnowledge 会立刻识别 `wiki/patterns/` 里的所有 Markdown 文件，`skill-impact.md` 和 `logs.md` 也会正确渲染成时序文档。侧边 AI 面板直接让 Claude 或 Codex 查询 wiki 知识、提建议，或者让 WikiSkill 的 Skill Proposer 把新 proposal 写进 `skills/` 目录。

---

## 几个值得关注的细节

**关于 MCP 集成**：`ok init` 写入的 MCP 配置不只是简单的文件读写，还包含"富搜索"——Agent 能根据语义查询相关 pattern，而不只是关键词匹配。这对 WikiSkill 的推理阶段有直接价值。

**关于 Skills**：OpenKnowledge 的 Skills 机制和 WikiSkill 的 Skills Layer 命名相同，但层次不同——前者是 IDE 插件级别，后者是 Agent 记忆演化级别。两者可以叠加：用 WikiSkill 生成的 `SKILL.md` 文件，可以直接被 OpenKnowledge 挂载为可调用 skill。

**关于隐私**：所有数据本地存储，不上传任何云服务。git 同步是可选的，并且是你自己的 git 仓库。在企业知识库场景下这一点很重要。

**关于活跃度**：仓库创建于 2026-06-03，最后 push 在今天（2026-09-01），3838 stars，很活跃。不是停更的概念项目。

---

## 实际使用建议

如果你在用 WikiSkill 模式管理 Agent 知识：

1. 把 `workspace/wiki/` 用 OpenKnowledge 打开，配好 Claude Code 的 MCP，当你的主要查阅和编辑界面
2. WikiSkill 的自动化脚本（Wiki Maintainer、Skill Proposer）继续在后台跑，写入文件
3. 每隔几天在 OpenKnowledge 里 review `skill-impact.md`，看哪些 skill 被接受、哪些被 rollback，手动干预异常情况
4. 用 OpenKnowledge 的图谱视图检查 pattern 之间的 wiki link 是否合理，发现孤立节点及时补充连接

这套组合相当于：**Agent 持续学习，人类随时介入，知识以 Markdown 形式沉淀，git 保证可审计。**

---

## 相关链接

- GitHub：[inkeep/open-knowledge](https://github.com/inkeep/open-knowledge)
- 官网：[openknowledge.ai](https://openknowledge.ai)
- 文档：[openknowledge.ai/docs](https://openknowledge.ai/docs)
- 上一篇：WikiSkill——把 Agent 经验沉淀为持久知识
- Discord：[discord.gg/VRKk2EaGHN](https://discord.gg/VRKk2EaGHN)

<!--EN-->

In our previous article, we did a deep dive into Google Research's **WikiSkill** paper — a three-layer architecture (Raw Layer / Wiki Layer / Skills Layer) that lets agents distill execution experience into persistent knowledge. The conclusion: this is entirely self-implementable, but it raises a practical question: **Where do you actually store the knowledge? Who reads it? How do humans and agents collaborate on editing?**

Today, here's the answer.

**[inkeep/open-knowledge](https://github.com/inkeep/open-knowledge)** is an open-source AI-native Markdown IDE with 3,800+ stars, written in TypeScript under GPL-3.0. It positions itself as "Notion meets VS Code" — a true WYSIWYG Markdown editor with deep integration for Claude, Codex, OpenCode, and other agents.

These two projects are almost perfectly complementary.

---

## What Is OpenKnowledge

One sentence: **A Markdown knowledge base IDE that both humans and agents can read and write fluently.**

Core capabilities:

- **True WYSIWYG**: Editing Markdown files feels like Google Docs or Notion — no toggling between source and preview
- **Cross-platform desktop + web**: macOS / Windows / Linux desktop app, plus a CLI-launched web UI that runs on Intel Macs and servers too
- **Built-in MCP + Skills**: Out of the box, `ok init` detects Claude Code / Codex / Cursor / OpenCode on your machine and wires up the MCP config and skills so agents can do rich document search and authoring
- **Git sync**: Team sharing and version control is git/GitHub underneath — not a proprietary data silo
- **Embeddable HTML**: Rich components can be embedded in engineering specs and visualized reports, not just plain text

One key topic tag: **`llm-wiki-karpathy`** — named after Karpathy's discussion of what a knowledge base should look like in the "LLM OS" paradigm. OpenKnowledge explicitly positions itself as the standard tool for LLM Wikis.

---

## How It Connects to WikiSkill

WikiSkill defines how knowledge should be organized:

```
workspace/
├── raw/           # Immutable execution traces
├── wiki/
│   ├── patterns/  # Individual Markdown pattern files
│   ├── logs.md    # Chronological evolution log
│   ├── skill-impact.md  # Accept/Reject history + diffs
│   └── index.md   # Pattern directory index
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── PURPOSE.md
```

OpenKnowledge can open this directory structure directly and provides:

1. **Human-readable WYSIWYG**: Every pattern file in `wiki/patterns/*.md` renders as a proper document in OpenKnowledge, not raw Markdown source
2. **Graph view**: OpenKnowledge has a built-in wiki link graph — `[[pattern-name]]` cross-file links auto-visualize
3. **Agent writes, human reviews**: WikiSkill's Wiki Maintainer Agent writes to `patterns/`; humans review in OpenKnowledge, with the side AI panel for follow-up questions
4. **Skills management**: OpenKnowledge's Skills system can mount `SKILL.md` content as callable agent skills, closing the loop

Put simply: **WikiSkill is the knowledge evolution engine; OpenKnowledge is its cockpit.**

---

## Quick Start: Agent Wiki in 5 Minutes

### Option 1: Desktop App (Recommended)

Download from [openknowledge.ai/download](https://openknowledge.ai/download):
- **macOS Apple Silicon**: Open the DMG and drag **OpenKnowledge** to Applications
- **Windows 10+**: Run the Setup installer — no admin prompt required
- **Linux**: Install the .deb (Debian/Ubuntu) or .rpm (Fedora/RHEL) package

After installing, "Open Folder" and select any directory containing Markdown files.

### Option 2: CLI + Web (Intel Mac / Server)

Requires Node.js 24+:

```bash
npm install -g @inkeep/open-knowledge
cd your-wiki-directory
ok init          # Detects local agent harnesses, auto-configures MCP and skills
ok start --open  # Launch the web editor and open it in your browser
```

`ok init` scans for Claude Code, Codex, Cursor, etc. and generates the corresponding configs — no manual MCP wiring needed.

### With WikiSkill Workflow

After setting up WikiSkill's `workspace/` directory from our previous article:

```bash
cd workspace
ok init
ok start --open
```

OpenKnowledge immediately recognizes all Markdown files in `wiki/patterns/`, and `skill-impact.md` and `logs.md` render as proper chronological documents. The side AI panel lets Claude or Codex query wiki knowledge, make suggestions, or let WikiSkill's Skill Proposer write new proposals into `skills/`.

---

## Details Worth Noting

**On MCP integration**: The MCP config written by `ok init` includes semantic search, not just keyword matching. Agents can query related patterns by meaning. This directly benefits WikiSkill's inference phase.

**On Skills**: OpenKnowledge's Skills mechanism and WikiSkill's Skills Layer share a name but differ in scope — the former is IDE plugin level, the latter is agent memory evolution level. They stack: `SKILL.md` files generated by WikiSkill can be directly mounted as callable skills in OpenKnowledge.

**On privacy**: All data stored locally. No cloud uploads. Git sync is opt-in and uses your own repository. Critical for enterprise knowledge base use cases.

**On activity**: Created 2026-06-03, last pushed today (2026-09-01), 3,838 stars, very active. Not an abandoned concept project.

---

## Practical Usage Recommendations

If you're managing agent knowledge with the WikiSkill pattern:

1. Open `workspace/wiki/` in OpenKnowledge, configure Claude Code's MCP, use it as your primary reading and editing interface
2. WikiSkill's automation scripts (Wiki Maintainer, Skill Proposer) keep running in the background, writing files
3. Every few days, review `skill-impact.md` in OpenKnowledge — check which skills got accepted, which got rolled back, and manually intervene when something looks off
4. Use OpenKnowledge's graph view to check whether pattern wiki links make sense; find isolated nodes and add connections

This combination amounts to: **Agents learn continuously, humans step in at any time, knowledge accumulates as Markdown, git ensures auditability.**

---

## Links

- GitHub: [inkeep/open-knowledge](https://github.com/inkeep/open-knowledge)
- Website: [openknowledge.ai](https://openknowledge.ai)
- Docs: [openknowledge.ai/docs](https://openknowledge.ai/docs)
- Previous article: WikiSkill — Distilling Agent Experience into Persistent Knowledge
- Discord: [discord.gg/VRKk2EaGHN](https://discord.gg/VRKk2EaGHN)
