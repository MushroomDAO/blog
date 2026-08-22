---
title: "cove-book-forge-mcp：把 PDF/EPUB 书籍锻造成 Agent Skill，一次分析，Codex/Claude Code 永久复用"
titleEn: "cove-book-forge-mcp-pdf-epub-agent-skill-obsidian-codex-claude"
description: "moonlin1213/cove-book-forge-mcp 是一个本地优先的开源 MCP 服务器，把 PDF 或 EPUB 书籍转化为可复用的 AI 知识——稳定指纹缓存章节分析，同一份结果同时输出 Obsidian 笔记和可安装的 Agent Skill（兼容 Codex、Claude Code）。支持 OpenAI/DeepSeek/Anthropic 三类 Provider，完整书籍锻造作业可暂停/恢复，所有输入严格边界检查，MIT，Python。"
descriptionEn: "moonlin1213/cove-book-forge-mcp is a local-first open-source MCP server that turns PDF or EPUB books into reusable AI knowledge. Stable fingerprints cache chapter analysis; the same result feeds Obsidian notes and installable Agent Skills (Codex, Claude Code) with zero extra model calls. Supports OpenAI, DeepSeek, and Anthropic providers; whole-book forging jobs are pausable and resumable; all inputs pass strict boundary checks. MIT, Python."
pubDate: "2026-08-22"
updatedDate: "2026-08-22"
category: "Tech-News"
tags: ["MCP", "Agent Skill", "读书AI", "Obsidian", "Codex", "Claude Code", "EPUB", "本地AI"]
heroImage: "../../assets/images/cove-book-forge-mcp-pdf-epub-agent-skill-obsidian-codex-claude-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：moonlin1213/cove-book-forge-mcp
许可证：MIT
语言：Python
Stars：5 · Forks：1
创建：2026-08-21 | 最近更新：2026-08-22

---

## 一、解决什么问题

你买了一本书。你想让 AI 帮你读。现在的做法是：把章节内容粘进聊天框，每次对话都要重新粘，每次都要重新付 token 钱，知识消散在一个个临时对话里。

cove-book-forge-mcp 的回答是：**把书锻造成一个 Agent Skill，一次分析，永久复用**。

```
PDF / EPUB
    ↓
标准化章节
    ↓
AI 分析 + 指纹缓存
    ↙          ↓          ↘
Obsidian    章节 Skill   完整书籍 Skill
    └─────────┼─────────┘
              ↓
   Codex / Claude Code / 任意 MCP 客户端
```

同一份章节分析，同时输出 Obsidian 笔记和可安装的 Skill，不重复调用模型。

---

## 二、核心设计

**稳定指纹缓存**是整个系统的核心。章节标题、正文、标注、反思、分析配置、Prompt 和 Generator 版本、Schema 版本——全部纳入指纹计算。命中缓存就返回，零 API 调用。重建 Library 实例也命中，重启进程也命中。

**完整书籍锻造作业**（WholeBookForge）：规划阶段生成一个 30 分钟有效期的 `ForgePlan`，里面预估了哪些章节会缓存命中、哪些需要真实 API 调用——不凭空报价。确认 + 幂等键才能开始，SQLite 日志记录每个检查点，可以在章节边界暂停、取消，中断后恢复不重复已完成章节。

**Agent Skill 格式**：最终产出是可以直接安装给 Codex、Claude Code 或通用 Agent Skill 目录的 Skill，Progressive Disclosure 设计——Agent 不需要在每个 Prompt 里塞入整本书，按需加载章节内容。

---

## 三、输入安全边界

这个项目在输入处理上做得比大多数同类工具仔细很多。

**EPUB**：ZIP 预检在读取内容前先跑——绝对路径、父目录穿越、反斜杠路径、加密条目、归档符号链接、嵌套归档、压缩比超限，全部在读书前就拒掉。章节顺序来自 OPF spine，不靠文件名或 ZIP 成员顺序。

**PDF**：必须有文字层。扫描版或纯图片 PDF 返回 `OCR_REQUIRED` 错误，明确失败，不下载 OCR 引擎、不调用远端服务、不静默回退。这对本地优先的设计来说是正确取舍——比静默上传云端 OCR 好很多。

默认限制：源文件 512 MiB、PDF 最多 5000 页、ZIP 成员 10000 个、展开内容总量 1 GiB。源文件在解析前后都做指纹校验，解析中途文件变化会以 `SOURCE_CHANGED` 失败，不留下部分结果。

---

## 四、输出：Obsidian + Agent Skill

**Obsidian 输出**：Vault 必须预先存在且显式配置。磁盘根目录、Home 目录、当前工作目录及其上级祖先目录、符号链接路径、不可写位置——全部拒绝写入。发布不重新调用模型，接收已分析的 `AnalyzedChapter` 直接生成笔记。

**Agent Skill 输出**：生成的 Skill 可以安装到：
- `~/.codex/skills/`（Codex）
- `~/.claude/skills/`（Claude Code）
- 任意通用 Agent Skill 目录

安装后，Agent 读 Skill 即可获取书籍知识，不需要书的原文在上下文里。

---

## 五、MCP 服务器

两种运行模式：

```bash
# stdio 模式（标准 MCP 接入）
cove-book-forge mcp --config /path/to/config.yaml

# 本地 HTTP 模式（Streamable HTTP，仅回环地址）
cove-book-forge mcp --transport http --host 127.0.0.1 --port 8000 \
  --config /path/to/config.yaml
```

HTTP 模式强制绑定回环地址，没有未认证的远端模式。MCP 工具覆盖：Library 导入/读取、章节分析和输出、完整书籍规划/作业/控制/状态、生成的 Skill 发现、`cove-book-forge://` 资源。

支持的 Provider：OpenAI、DeepSeek（复用 OpenAI 兼容路由）、Anthropic，也可注入自定义 Provider。

---

## 六、为什么值得关注

书籍是结构化的长上下文——有章节顺序、有核心概念、有层级关系。把这种结构做成 Progressive Disclosure 的 Agent Skill，比每次粘贴原文在认知效率和 token 经济上都更合理。

这个项目目前还很早期（5 stars，发布不到两天），但设计扎实：缓存逻辑、作业恢复、安全边界、MCP 接口一套都有。对于 Codex 用户和 Claude Code 用户来说，如果你有一本书想让 Agent 读懂并持续引用，这是目前看到的最完整的本地优先方案。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## cove-book-forge-mcp: Forge PDF/EPUB Books into Agent Skills — Analyze Once, Reuse in Codex and Claude Code Forever

*by Mycelium Protocol*

---

GitHub: moonlin1213/cove-book-forge-mcp
License: MIT
Language: Python
Stars: 5 · Forks: 1
Created: 2026-08-21 | Updated: 2026-08-22

---

### What Problem It Solves

You bought a book. You want AI to help you read it. The current workflow: paste chapter content into a chat box, repaste it for every new session, pay tokens again every time, watch the knowledge dissolve into temporary conversations.

cove-book-forge-mcp answers with: **forge the book into an Agent Skill — analyze once, reuse permanently**.

```
PDF / EPUB
    ↓
normalized chapters
    ↓
AI analysis + fingerprint cache
    ↙          ↓          ↘
Obsidian    chapter     whole-book
 notes       Skill         Skill
    └─────────┼─────────┘
              ↓
   Codex / Claude Code / any MCP client
```

The same chapter analysis feeds Obsidian notes and installable Skills simultaneously, with zero redundant model calls.

---

### Core Design

**Stable fingerprint caching** is the system's foundation. Chapter title, body, highlights, notes, annotations, reflections, analysis config, prompt and generator versions, and schema version — all factored into the fingerprint. A cache hit returns immediately, zero API calls. The cache survives library instance reconstruction and process restarts.

**Whole-book forge jobs** (WholeBookForge): the planning phase produces a 30-minute `ForgePlan` that estimates which chapters will be cache hits and which need real API calls — no invented prices. Execution requires explicit confirmation and an idempotency key. A SQLite journal records every chapter checkpoint; jobs can be paused or cancelled at chapter boundaries; interrupted jobs resume without repeating completed checkpoints.

**Agent Skill format**: the final output is a Skill installable for Codex, Claude Code, or any generic Agent Skill directory. Progressive disclosure design — an agent doesn't load the whole book into every prompt; it loads chapters on demand.

---

### Input Safety Boundaries

This project handles input more carefully than most comparable tools.

**EPUB**: ZIP members are preflighted before any book content is read — absolute paths, parent-directory traversal, backslash paths, encrypted entries, archive symlinks, nested archives, and compression-ratio violations are all rejected before the spine is walked. Reading order comes from the OPF spine, not filenames or ZIP member order.

**PDF**: must contain a text layer. Scanned or image-only PDFs fail explicitly with `OCR_REQUIRED` — the system does not download an OCR engine, call a remote service, or silently fall back to one. For a local-first design, this is the right trade-off: far better than silently uploading to a cloud OCR service.

Default limits: 512 MiB source file, 5,000 PDF pages, 10,000 ZIP members, 1 GiB total expanded content. Source files are fingerprinted before and after extraction; a file that changes mid-parse fails with `SOURCE_CHANGED` and leaves no partial state.

---

### Output: Obsidian + Agent Skill

**Obsidian output**: the vault must exist and be explicitly configured. Disk roots, the home directory, the current working directory and its broad ancestors, symlinked paths, and unwritable locations are all rejected. Publication does not re-invoke a model; it receives an already-analyzed `AnalyzedChapter` and generates the note directly.

**Agent Skill output**: generated Skills install to:
- `~/.codex/skills/` (Codex)
- `~/.claude/skills/` (Claude Code)
- any generic Agent Skill directory

Once installed, an agent reads the Skill to access book knowledge without the source text in context.

---

### MCP Server

Two transport modes:

```bash
# stdio (standard MCP integration)
cove-book-forge mcp --config /path/to/config.yaml

# local HTTP (Streamable HTTP, loopback only)
cove-book-forge mcp --transport http --host 127.0.0.1 --port 8000 \
  --config /path/to/config.yaml
```

HTTP mode is restricted to loopback; there is no unauthenticated remote mode. MCP tools cover library import/read, chapter analysis and outputs, whole-book planning/jobs/control/status, Skill discovery, and `cove-book-forge://` resources.

Supported providers: OpenAI, DeepSeek (via OpenAI-compatible route), Anthropic, plus custom injected providers.

---

### Why It's Worth Watching

Books are structured long-context — with chapter order, core concepts, hierarchical relationships. Building that structure into a progressively disclosed Agent Skill is more cognitively and economically efficient than pasting source text into every prompt.

Still very early (5 stars, published less than two days ago), but the design is solid: caching logic, job resumability, input safety, and MCP interface are all present. For Codex and Claude Code users who want an agent to understand a book and reference it persistently, this is the most complete local-first solution I've seen.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
