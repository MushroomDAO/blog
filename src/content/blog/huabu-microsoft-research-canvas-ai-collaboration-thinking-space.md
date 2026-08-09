---
title: "Huabu：微软研究院造的画布 AI——把你和 Agent 的思考放在同一张无限画板上"
titleEn: "Huabu: Microsoft Research's Canvas AI Puts You and Your Agent on One Infinite Whiteboard"
description: "Huabu 是微软研究院开源的画布式人机协作框架，核心思路是把思维外化到可见的二维节点网络上，让 AI Agent 看到结构而不是只听最后一条指令，从而更好地理解意图。v0.9.1 新增外部 Agent 可直接读写 Space 节点、逐对话模型设置、桌面自动更新。MIT 授权，macOS Apple Silicon + Windows x64，TypeScript，66 stars。"
pubDate: "2026-07-28"
category: "Tech-Experiment"
heroImage: "../../assets/images/huabu-microsoft-research-canvas-ai-collaboration-thinking-space-banner.jpg"
---

"Where you and your agents think together."

微软研究院给 Huabu 的定语是画布式人机协作框架（canvas-based interaction framework）。这个描述比较技术，换个说法是：**一张你和 AI 共享的无限白板，所有的想法、文件、对话都作为节点摆在上面，AI 看的不是你最后说的那句话，而是整张画板的结构**。

---

## 一、为什么需要画布

现有 AI 工具的主要交互范式是线性聊天——你说一句，AI 回一句，向下滚动，上文淡出视野。

这个范式对执行类任务很好：你想改一段代码，想生成一封邮件，想总结一篇文章——任务明确，一轮交互完成。

但有一类工作线性聊天应付不了：**探索阶段**——你还不清楚要做什么，只有模糊的想法、几个相关资料、一堆开放问题，需要边整理边想。

这时候线性聊天有两个结构性限制：

1. **中间结构不可见**：你在脑子里记着"这个想法和那个文件有关"，但聊天窗口只有文字，没有空间关系。你的工作记忆在承担本应该外化的负担。

2. **AI 只能看最后一条**：Agent 拿到的 context 是对话历史，而不是你正在形成的思维结构。它知道你刚才说了什么，但不知道这张画板上哪个节点是核心、哪些是待确认的、哪些关系你已经理清了。

Huabu 的设计从这两个问题出发：把中间结构外化到画布上，让 AI 也能读到这个结构。

---

## 二、Space、节点与连接

Huabu 的基本单位是 **Space**——独立的二维画布，对应一个话题或项目。

画布上的一切都是节点（Node）：

- **内容节点**：Note（便签）、Text（文本）、Frame（框架/容器）、Sketch（手绘）、PDF、图片、网页
- **AI 对话节点**：每个 Chat 对话可以作为独立节点留在画布上，拖动有用的回复片段成为新节点
- **连接**：节点之间可以连线，表达依赖、因果、对比等关系

关键设计：**AI Agent 看到的不只是你最新的问题，而是整张 Space 的节点结构**。当你问"这些想法的核心矛盾是什么"，Huabu Agent 可以观察整个画板——哪些节点被你放在中央、哪些节点之间有连接、哪些节点标注了"待验证"——从而回答得比只看最后一条消息更准确。

---

## 三、两种 AI 交互模式

Chat Panel 提供两种模式：

**Huabu Chat（纯对话）**
标准聊天，你选择哪些节点作为 context，AI 读取后回答。拖动回复的有用部分到画布，变成新节点继续整理。

**Huabu Agent（主动操作）**
Agent 不只是回答，还可以主动操作 Space：整理节点位置、创建新节点、建立连接、合并重复内容、标记已解决的问题。每次操作都记录在变更卡片里，你可以逐条审查或一键撤销。

**Agent Node（原位对话）**
在画布上任意位置放置一个 Agent 节点，直接在材料旁边提问——不切换到 Chat Panel，保持与周围内容的空间关联。

---

## 四、v0.9.1：外部 Agent 接入

这个版本最重要的更新：**外部 Agent 可以直接读写 Space**。

此前外部 Agent 必须通过 Huabu 内置 Agent 中转才能访问画布内容。v0.9.1 之后，连接的外部 Agent 可以直接：

- 读取 Space 的节点大纲（outline/nodes）
- 搜索 Space 内容
- 为 Sketch 节点生成快照
- 创建 / 编辑 / 连接 / 移动 / 删除节点

接入方式：Settings → External Agents，配置完成后该 Agent 出现在 Chat Panel 的模型选择里。可以是理解某个代码仓库的专用 Agent，也可以是能生成演示文稿的 Agent。

所有 Agent 的变更都限定在当前 Space 和当前对话内，并显示在变更审查卡片里——你永远可以撤销。

其他 v0.9.1 更新：
- 桌面自动更新（检测到新版本后询问用户，自主决定是否更新）
- 逐对话模型设置（每个会话独立选择模型和推理强度，设置持久保存）
- Agent 身份系统（自定义头像 / 图标，问题节点显示 Agent 头像和状态标记）

---

## 五、技术细节

**数据存储**：本地 Home 文件夹，用户自选。无遥测、无崩溃报告、无使用数据上传到 Microsoft。

**LLM**：BYOLLM（Bring Your Own LLM）。Huabu 不提供 LLM 服务，需要自己配置模型提供商（支持 OpenAI、Azure OpenAI，v0.9.1 新增 OpenAI Codex via ChatGPT OAuth）。

**凭据安全**：API Key 用系统级受保护存储加密，不以明文保存。

**平台**：macOS（Apple Silicon）+ Windows（x64）。源代码"将在未来版本发布"——目前 GitHub 仓库是文档和 RAI 说明，没有可直接运行的源码。

**协议**：外部 Agent 接入使用 ACP 协议。

---

## 六、研究背景与定位

Huabu 来自微软研究院，RAI README 里有一段话：

> Huabu is released for research and experimental use. It is being shared with the research community to facilitate reproduction of our results and foster further research in this area.

配套学术论文正在写作中（README 里有 `[PAPER LINK TO BE ADDED]` 占位符）。内部评估对比的基准是"线性聊天"，评估模型是 GPT-5.5，场景是研究合成、规划和构思。

主要评估结果：
- 降低了用工作记忆保存中间想法的认知负荷
- AI Agent 更容易根据任务的整体 context 行动，而不只是最新一条消息

这解释了为什么 Huabu 的设计相当克制：它不是全能工作站，而是专门针对"还不知道要做什么"这个阶段设计的工具——把它用在代码执行类任务上可能不如 Cursor / Claude Code，但在早期探索阶段，共享画布确实提供了线性聊天给不了的结构。

---

## 七、横向对比

| 工具 | 范式 | AI 能看到的 context |
|---|---|---|
| Claude / ChatGPT | 线性聊天 | 对话历史 |
| Cursor / Claude Code | 代码执行 | 代码库 + 对话 |
| NotebookLM | 文档问答 | 上传的文档 |
| **Huabu** | 画布协作 | 整张 Space 的节点结构 |

Huabu 切入的是一个目前没有好工具覆盖的场景：**知识工作的前期——问题还没有成形、思路还在发散、需要一个地方把所有东西摆出来一起看**。

---

**项目信息**

- GitHub：`github.com/microsoft/Huabu`（66 ⭐，MIT）
- 当前版本：v0.9.1（2026-07-24）
- 平台：macOS Apple Silicon + Windows x64
- 语言：TypeScript
- 联系：huabu@microsoft.com

<!--EN-->

## Huabu: Microsoft Research's Canvas AI for Thinking Together with Agents

"Where you and your agents think together."

Microsoft Research describes Huabu as a canvas-based interaction framework for human–AI collaboration. More concretely: an infinite shared whiteboard where your ideas, documents, and conversations live as spatial nodes — and where AI agents see the structure of your thinking, not just your latest message.

---

## Why a Canvas

The dominant paradigm for AI interaction today is linear chat — you say something, the AI responds, the conversation scrolls down, and earlier context fades from view.

This works well for execution tasks: rewrite this code, draft this email, summarize this document. The intent is clear; one exchange completes the job.

But there's a class of work linear chat handles poorly: **exploration** — when you're not yet sure what you're doing, only have vague ideas, a few related sources, and a pile of open questions. You need to think by arranging.

Linear chat has two structural constraints here:

1. **Intermediate structure stays invisible.** You're tracking "this idea relates to that document" in your working memory, but the chat window only shows text, not spatial relationships. Your working memory is doing work that should be externalized.

2. **The AI only sees the latest message.** An agent's context is the conversation history — it knows what you just said, but not which node on the canvas is central, which relationships you've resolved, or which questions are still open.

Huabu addresses both: externalize the intermediate structure to a canvas, and let the AI read that structure.

---

## Spaces, Nodes, and Connections

The basic unit is a **Space** — an independent 2D canvas per topic or project.

Everything on the canvas is a **Node**:

- **Content nodes**: Note, Text, Frame (container), Sketch (freehand), PDF, image, web page
- **AI conversation nodes**: each chat thread can remain as a node on the canvas; useful fragments of a reply can be dragged out to become their own nodes
- **Connections**: nodes can be linked with edges to express dependency, causality, contrast, or any relation

Key design: **the AI agent sees not only your latest question, but the full structure of your Space** — which nodes you placed at the center, which have connections, which you've labeled "unverified." This lets it answer "what's the core tension in these ideas" more accurately than if it only had access to the most recent message.

---

## Two AI Interaction Modes

**Huabu Chat (plain conversation)**
Standard chat. You select which nodes to include as context, ask questions, and drag useful parts of the response back to the canvas to keep structuring your thinking.

**Huabu Agent (active operations)**
The agent doesn't just answer — it can also act on the Space: rearrange nodes, create new ones, draw connections, merge duplicates, mark resolved questions. Every change is recorded in a change-review card, which you can inspect item by item or undo entirely.

**Agent Node (in-place conversation)**
Place an Agent node anywhere on the canvas and start a conversation right beside your material — no switching to the Chat Panel, spatial relationship to surrounding content preserved.

---

## v0.9.1: External Agent Read/Write Access

The headline update in this release: **external agents can now directly read and modify a Space**.

Previously, an external agent could only access canvas content by routing through Huabu's built-in agent. From v0.9.1, a connected external agent can directly:

- Query the Space outline (nodes, structure)
- Search Space content
- Snapshot Sketch nodes
- Create, edit, connect, move, and delete nodes

Setup: Settings → External Agents. Once configured, the agent appears in the Chat Panel model selector. This could be an agent with deep understanding of a code repository, or one that can generate presentation slides.

All agent changes are scoped to the current Space and conversation, and appear in the change-review card — always reversible.

Other v0.9.1 updates:
- Desktop auto-update (prompts you; you decide when to update)
- Per-conversation model settings (saved per thread; model list shows pricing, descriptions, context window size; supports live OpenAI model discovery; OpenAI Codex via ChatGPT OAuth)
- Agent identity (custom avatar/icon; question nodes show the agent's avatar and status badge)

---

## Technical Details

**Data**: stored in a local Home folder of the user's choosing. No telemetry, crash reports, diagnostic logs, or usage data sent to Microsoft.

**LLM**: BYOLLM. Huabu doesn't provide an LLM service — you configure your own model provider (OpenAI, Azure OpenAI; v0.9.1 adds Codex via ChatGPT OAuth).

**Credentials**: API keys encrypted at rest using OS-protected storage; never stored as plain text.

**Platforms**: macOS (Apple Silicon) + Windows (x64). Source code "will be released in a future update" — the current GitHub repository contains documentation and the RAI transparency statement, not runnable source.

**External agent protocol**: ACP.

---

## Research Context

Huabu comes from Microsoft Research. The RAI README states:

> Huabu is released for research and experimental use. It is being shared with the research community to facilitate reproduction of our results and foster further research in this area.

A companion academic paper is in progress (the README contains a `[PAPER LINK TO BE ADDED]` placeholder). Internal evaluation compared Huabu against the "linear chat baseline" using GPT-5.5 across research synthesis, planning, and ideation scenarios.

Main findings:
- Reduced cognitive load of holding intermediate ideas in working memory
- Easier for AI agents to act on the broader context of a task rather than only the latest message

This explains Huabu's restraint in scope: it's not a general-purpose workstation. It's designed specifically for the stage where "the central challenge is deciding what to do, rather than executing well-formed instruction." For code execution tasks it's no match for Cursor or Claude Code — but for early-stage exploratory work, the shared canvas provides structure that linear chat can't.

---

## What Makes This Different

| Tool | Paradigm | What AI sees as context |
|---|---|---|
| Claude / ChatGPT | Linear chat | Conversation history |
| Cursor / Claude Code | Code execution | Codebase + conversation |
| NotebookLM | Document Q&A | Uploaded documents |
| **Huabu** | Canvas collaboration | Full Space node structure |

Huabu targets a gap: **the front end of knowledge work — when the problem hasn't formed yet, thinking is still diverging, and you need a place to lay everything out and look at it together.** That's the scenario where having a shared spatial structure — visible to both you and the AI — actually changes what's possible.

---

**Project**

- GitHub: `github.com/microsoft/Huabu` (66 ⭐, MIT)
- Current version: v0.9.1 (2026-07-24)
- Platforms: macOS Apple Silicon + Windows x64
- Language: TypeScript
- Contact: huabu@microsoft.com
