---
title: "oh-my-mermaid：让 AI 把你的代码库画成可导航的架构图"
titleEn: "oh-my-mermaid: Turn Any Codebase into Navigable Architecture Diagrams with AI"
description: "oh-my-mermaid 是一个 Claude Code skill，一条命令让 AI 递归扫描代码库、生成多视角 Mermaid 架构图，文件系统本身就是架构树。1817 Star，MIT，支持 Claude/Codex/Cursor。"
descriptionEn: "oh-my-mermaid is a Claude Code skill that lets AI recursively scan a codebase and generate multi-perspective Mermaid architecture diagrams in one command — the filesystem itself becomes the architecture tree. 1817 stars, MIT, works with Claude / Codex / Cursor."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["Claude Code", "Mermaid", "架构图", "代码可视化", "Skill", "文档工具", "AI工具", "TypeScript", "开发者工具"]
heroImage: "../../assets/images/oh-my-mermaid-codebase-architecture-docs-ai-banner.jpg"
---

> **仓库**：oh-my-mermaid/oh-my-mermaid · **⭐ 1,817** · **148 forks** · TypeScript · MIT  
> **安装**：`npm install -g oh-my-mermaid && omm setup`  
> **使用**：在 AI 工具里运行 `/omm-scan`

---

## 一、问题

AI 几秒钟就能写出代码。人类理解它需要几个小时。

跳过理解，代码库就变成黑盒——即使对你自己。

这是 oh-my-mermaid（omm）要解决的问题：**由 AI 生成的、为人类准备的架构文档。**

---

## 二、工作原理

omm 的核心思路是让 AI 生成多个「视角（perspective）」——从不同镜头观察同一个代码库：

- 整体架构（structural overview）
- 数据流（data flow）
- 外部集成（external integrations）
- 你让 AI 关注的任何角度

每个视角包含：

- 一张 Mermaid 图表（`.mmd` 文件）
- 文档字段：`description`、`context`、`constraint`、`concern`、`todo`、`note`

**关键设计：节点递归展开。**

复杂的节点（比如 `auth-service`）会被展开成有自己图表的嵌套子元素。简单的节点保持叶子。分析停止的深度由 AI 判断，不是预设阈值。

生成的内容直接存在 `.omm/` 目录里，文件系统结构就是架构树：

```
.omm/
├── overall-architecture/
│   ├── description.md
│   ├── diagram.mmd
│   ├── context.md
│   ├── main-process/
│   │   ├── description.md
│   │   ├── diagram.mmd
│   │   └── auth-service/
│   │       └── ...
│   └── renderer/
├── data-flow/
└── external-integrations/
```

查看器从文件系统自动检测嵌套关系——有子目录的渲染成可展开的组，叶子节点渲染成普通节点。

---

## 三、快速上手

**第一步：安装 CLI**

```bash
npm install -g oh-my-mermaid
```

**第二步：向 AI 工具注册技能**

```bash
omm setup
```

`omm setup` 会自动检测你安装了哪些 AI 工具，并向每个工具注册 skill。支持的工具：

| AI 工具 | 注册命令 |
|---|---|
| Claude Code | `omm setup claude` |
| Codex | `omm setup codex` |
| Cursor | `omm setup cursor` |
| OpenClaw | `omm setup openclaw` |
| Antigravity | `omm setup antigravity` |

**第三步：扫描代码库**

打开你的 AI 工具，进入项目目录，运行：

```
/omm-scan
```

AI 开始工作。它分析代码库，决定有哪些视角值得生成，递归展开复杂节点，把结果写入 `.omm/`。

**第四步：查看结果**

```bash
omm view
```

打开交互式查看器，在浏览器里浏览架构图和文档。

---

## 四、每个元素的 7 个字段

每个架构元素（视角或节点）最多包含 7 个字段：

| 字段 | 用途 |
|---|---|
| `description` | 这是什么 |
| `diagram` | Mermaid 图表 |
| `context` | 为什么存在，周围的约束 |
| `constraint` | 硬性限制（性能、安全、合规）|
| `concern` | 已知问题或潜在风险 |
| `todo` | 待完成的工作 |
| `note` | 其他备注 |

这 7 个字段覆盖了一个架构元素「现在是什么 + 为什么这样 + 有什么问题」的完整描述，不只是画图。

---

## 五、云端存储与共享

```bash
omm login && omm link && omm push
```

或者用单步命令：

```
/omm-push
```

架构上传到 `ohmymermaid.com`，默认私有。可以与团队共享，也可以公开——项目 README 里有一个公开示例。

---

## 六、CLI 完整命令

```bash
omm setup                    # 向所有已安装 AI 工具注册技能
omm view                     # 打开交互式查看器
omm config language zh       # 设置生成内容的语言
omm update                   # 更新到最新版本
omm login                    # 登录云端账号
omm link                     # 将当前项目链接到云端
omm push                     # 推送到云端
omm help                     # 完整命令列表
```

---

## 七、Roadmap

当前规划的四个方向：

**子 agent 扫描流水线**：把 `/omm-scan` 从单个 skill 拆成多 agent 并行流水线——每个视角并行分析，减少 token 用量，提高扫描速度。

**增量分析**：检测上次扫描后变动的文件，只更新受影响的视角和元素，跳过未改变的子树。大型仓库的扫描不再需要每次全量。

**AI 自然语言搜索**：在查看器里搜索"auth 在哪里发生"，跨视角找到相关元素。架构文档不只是可读的，是可查询的。

**`/omm-guide` skill**：引导新开发者交互式了解代码库架构，以 `.omm/` 目录里的文档为上下文，像有人带着看一样。

---

## 八、设计判断

omm 解决的问题是真实的。大型代码库的"上手时间"（onboarding time）在很多团队里是 2-4 周，主要花在理解已有架构上——不是看文档，是读代码、问人、踩坑。

AI 编写代码让这个问题更严重了，因为 AI 生成代码的速度远超人类读代码的速度。代码量在增长，理解速度没有。

omm 的思路是对的：**用 AI 生成理解，而不只是生成代码。**

几个值得注意的设计选择：

**文件系统即树结构**：把 `.omm/` 目录直接当架构树用，而不是引入数据库或 JSON 格式。好处是 git 友好（架构文档可以版本化）、可以用 grep/读取、不需要解析器。

**视角（perspective）而不是单一图表**：同一个代码库从不同角度看是不同的系统。`data-flow` 视角和 `overall-architecture` 视角可以讲完全不同的故事，都是真的。

**递归分析**：浅层扫描看不到 `auth-service` 内部怎么运作，递归到叶子才有真正的理解深度。

**支持多个 AI 工具**：Claude Code、Codex、Cursor、OpenClaw、Antigravity。omm 不绑定单一 AI 工具，用哪个都能用，目录格式是通用的。

---

## 九、局限和值得想清楚的地方

**架构文档会过时**：代码每天在变，`.omm/` 里的图表不会自动更新。增量分析是 Roadmap 里的，但没有它之前，每次大改需要重新扫描。

**AI 的判断不总是对的**：递归分析深度、视角切分方式都是 AI 决定的。复杂项目里 AI 可能漏掉重要的视角，或者展开太深/太浅。

**生成成本**：大型代码库的全量扫描可能需要相当多的 token。子 agent 并行流水线是解法，但还在 Roadmap。

**Mermaid 的表达力有限**：复杂的架构关系有时候 Mermaid 表达不了，尤其是多维的依赖关系。图表里放不下就只能文字描述。

---

## 十、适合什么场景

**新人 onboarding**：接手陌生代码库，一条命令生成所有视角的架构图，不用读两周代码。

**重构前评估**：扫描一遍，看清楚当前架构，再决定从哪里下刀。

**写技术文档**：`/omm-scan` 生成的内容可以作为 RFC、设计文档、ADR 的基础，不用从零写。

**团队对齐**：不同人对同一个系统的理解可能完全不同，omm 生成的视角可以作为"大家说同一件事"的基础。

**AI 辅助上下文**：把 `.omm/` 作为 AI 编码工具的上下文，让 AI 在已有架构约束下生成代码，而不是在不了解全局的情况下乱写。

---

*数据来源：GitHub oh-my-mermaid/oh-my-mermaid，2026-07-22 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: oh-my-mermaid/oh-my-mermaid · **⭐ 1,817** · **148 forks** · TypeScript · MIT  
> **Install**: `npm install -g oh-my-mermaid && omm setup`  
> **Usage**: Run `/omm-scan` in your AI tool

---

## 1. The Problem

AI can write code in seconds. Humans need hours to understand it.

Skip that understanding, and the codebase becomes a black box — even to yourself.

This is the problem oh-my-mermaid (omm) sets out to solve: **architecture documentation generated by AI, prepared for humans.**

---

## 2. How It Works

omm's core idea is to have AI generate multiple "perspectives" — viewing the same codebase through different lenses:

- Structural overview
- Data flow
- External integrations
- Any angle you want the AI to focus on

Each perspective contains:

- A Mermaid diagram (`.mmd` file)
- Documentation fields: `description`, `context`, `constraint`, `concern`, `todo`, `note`

**Key design: recursive node expansion.**

Complex nodes (such as `auth-service`) are expanded into nested sub-elements with their own diagrams. Simple nodes remain as leaves. The depth at which analysis stops is determined by the AI, not a preset threshold.

The generated content is stored directly in the `.omm/` directory, and the filesystem structure itself is the architecture tree:

```
.omm/
├── overall-architecture/
│   ├── description.md
│   ├── diagram.mmd
│   ├── context.md
│   ├── main-process/
│   │   ├── description.md
│   │   ├── diagram.mmd
│   │   └── auth-service/
│   │       └── ...
│   └── renderer/
├── data-flow/
└── external-integrations/
```

The viewer automatically detects nesting relationships from the filesystem — directories with subdirectories render as expandable groups; leaf nodes render as plain nodes.

---

## 3. Quick Start

**Step 1: Install the CLI**

```bash
npm install -g oh-my-mermaid
```

**Step 2: Register the skill with your AI tool**

```bash
omm setup
```

`omm setup` automatically detects which AI tools you have installed and registers the skill with each one. Supported tools:

| AI Tool | Registration Command |
|---|---|
| Claude Code | `omm setup claude` |
| Codex | `omm setup codex` |
| Cursor | `omm setup cursor` |
| OpenClaw | `omm setup openclaw` |
| Antigravity | `omm setup antigravity` |

**Step 3: Scan the codebase**

Open your AI tool, navigate to the project directory, and run:

```
/omm-scan
```

The AI gets to work. It analyzes the codebase, decides which perspectives are worth generating, recursively expands complex nodes, and writes the results to `.omm/`.

**Step 4: View the results**

```bash
omm view
```

Opens the interactive viewer so you can browse architecture diagrams and documentation in the browser.

---

## 4. The 7 Fields for Each Element

Each architecture element (perspective or node) contains up to 7 fields:

| Field | Purpose |
|---|---|
| `description` | What this is |
| `diagram` | Mermaid diagram |
| `context` | Why it exists, surrounding constraints |
| `constraint` | Hard limits (performance, security, compliance) |
| `concern` | Known issues or potential risks |
| `todo` | Work yet to be done |
| `note` | Other remarks |

These 7 fields cover the complete description of an architecture element — "what it is now + why it is this way + what problems exist" — not just a diagram.

---

## 5. Cloud Storage and Sharing

```bash
omm login && omm link && omm push
```

Or with a single command:

```
/omm-push
```

The architecture is uploaded to `ohmymermaid.com`, private by default. It can be shared with a team or made public — the project README includes a public example.

---

## 6. Full CLI Reference

```bash
omm setup                    # Register the skill with all installed AI tools
omm view                     # Open the interactive viewer
omm config language zh       # Set the language for generated content
omm update                   # Update to the latest version
omm login                    # Log in to the cloud account
omm link                     # Link the current project to the cloud
omm push                     # Push to the cloud
omm help                     # Full command list
```

---

## 7. Roadmap

Four directions currently planned:

**Sub-agent scan pipeline**: Break `/omm-scan` from a single skill into a multi-agent parallel pipeline — each perspective analyzed in parallel, reducing token usage and increasing scan speed.

**Incremental analysis**: Detect files changed since the last scan, update only the affected perspectives and elements, and skip unchanged subtrees. Large repositories will no longer require a full scan every time.

**AI natural-language search**: Search "where does auth happen" in the viewer and find relevant elements across perspectives. Architecture documentation becomes not just readable but queryable.

**`/omm-guide` skill**: Guides new developers through the codebase architecture interactively, using the documentation in the `.omm/` directory as context — like having someone walk you through it.

---

## 8. Design Judgments

The problem omm addresses is real. Onboarding time for large codebases is 2–4 weeks in many teams, spent mostly on understanding existing architecture — not reading docs, but reading code, asking people, and stumbling through pitfalls.

AI writing code has made this worse, because AI generates code far faster than humans can read it. The volume of code is growing; the speed of comprehension is not.

omm's approach is right: **use AI to generate understanding, not just code.**

A few design choices worth noting:

**Filesystem as tree structure**: Using the `.omm/` directory directly as the architecture tree, rather than introducing a database or JSON format. The benefits are git-friendliness (architecture docs can be versioned), grep-ability and readability, and no parser required.

**Perspectives instead of a single diagram**: The same codebase looks like a different system from different angles. The `data-flow` perspective and the `overall-architecture` perspective can tell entirely different stories — both true.

**Recursive analysis**: A shallow scan cannot reveal how `auth-service` works internally; recursing to the leaves is what produces genuine depth of understanding.

**Support for multiple AI tools**: Claude Code, Codex, Cursor, OpenClaw, Antigravity. omm is not tied to a single AI tool — it works with whichever you use, and the directory format is universal.

---

## 9. Limitations and Things Worth Thinking Through

**Architecture documentation goes stale**: Code changes every day; diagrams in `.omm/` don't update automatically. Incremental analysis is on the Roadmap, but until it arrives, any major change requires a full re-scan.

**AI judgment is not always correct**: The recursion depth and how perspectives are divided are both decided by the AI. On complex projects, the AI may miss important perspectives or go too deep or too shallow.

**Generation cost**: A full scan of a large codebase may consume a significant number of tokens. The sub-agent parallel pipeline is the solution, but it remains on the Roadmap.

**Mermaid's limited expressiveness**: Complex architectural relationships are sometimes inexpressible in Mermaid, particularly multi-dimensional dependencies. What cannot fit in a diagram must be described in text.

---

## 10. What Scenarios This Fits

**New developer onboarding**: Taking over an unfamiliar codebase — one command generates architecture diagrams for all perspectives, with no need to read code for two weeks.

**Pre-refactor assessment**: Run a scan, understand the current architecture clearly, then decide where to make the cut.

**Writing technical documentation**: Content generated by `/omm-scan` can serve as the foundation for RFCs, design documents, and ADRs, without starting from scratch.

**Team alignment**: Different people on the same team can have completely different understandings of the same system; omm's generated perspectives provide a common basis for "everyone talking about the same thing."

**AI-assisted context**: Use `.omm/` as context for AI coding tools, so the AI generates code within existing architectural constraints rather than writing blindly without a global view.

---

*Data source: GitHub oh-my-mermaid/oh-my-mermaid, collected 2026-07-22.*

© 2026 Author: Mycelium Protocol
