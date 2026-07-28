---
title: "Bento：一个 HTML 文件装下整套办公软件——560KB 的 PowerPoint 替代品"
description: "Bento 是一个极度本地优先的设计实验：整个 PowerPoint 替代品就是一个 560KB 的 .bento.html 文件，文件本身就是编辑器、查看器和演示器，数据以纯文本 JSON 存在文件顶部，保存时文件重写自身。带 E2EE 实时协作（AES-GCM，密钥在文件里不在服务器上）、自研 CRDT、自研图表引擎、Morph 动画，还内置了 Claude Code Skill。11 天 2756 stars，MIT，TypeScript。"
pubDate: "2026-07-28"
category: "Tech-Experiment"
heroImage: "../../assets/images/bento-office-suite-single-file-powerpoint-alternative-local-first-banner.jpg"
---

Office 软件曾经是你**拥有**的东西。现在变成了你**租用**的东西——锁在某家公司的云里，需要登录，需要订阅，需要那家公司的服务器一直开着。

Bento 走了另一条路。

**整个 PowerPoint 替代品就是一个 HTML 文件。** 560KB，无需安装，无需账号。在任何浏览器里打开这个文件，它就是编辑器。保存，文件重写自身，把你的演示稿装进去。发给别人，那个文件本身就是软件——对方不需要安装任何东西。

11 天，2756 stars。

---

## 一、为什么这个设计很激进

"文件即软件"不是口号，Bento 把它做成了工程现实：

**数据在哪里**：文件顶部的 `#bento-doc` 标签里，纯文本 JSON。View-source 就能看到你的数据。没有二进制格式，没有加密，没有考古工作。

**如何保存**：File System Access API（有 fallback 到下载）。文件重写自己的数据块，只更新 JSON 部分，Shell（渲染器 + 编辑器 + 演示器）不变。

**文件寿命**：README 里有一句话很有力：*"A copy from 2026 will open in 2036."* 只要浏览器还能跑 HTML，这个文件就能打开。没有服务器，没有格式迁移，没有"旧版本不支持"。

**Offline 模式**：开启后，网络请求被硬封锁，应用会明确告诉你它在完全离线状态。不是口头承诺，是代码实现的隔离。

---

## 二、不是"基础版 PPT"

功能列表出乎意料地完整：

**Morph 动画**
两张幻灯片里共享同一个 `id` 的元素，切换时自动动画——位置、大小、颜色、渐变都会过渡。复制一张幻灯片，重新排布，动效就设计好了。这是 PowerPoint 里需要单独设置"变形"过渡的功能，Bento 默认内置。

**E2EE 实时协作**
密钥在文件里创建，从不上服务器。文件本身就是邀请函——把文件的副本发给对方，对方打开就加入了协作房间。加密算法：AES-GCM。

协作不依赖任何中心化服务，只用一个可选的 Cloudflare Worker 中继（`server/sync-worker/`）——这个中继只看得到密文、连接时间戳和 room key 的哈希，看不到任何内容或结构。密钥轮换 = 撤销之前所有的访问权限。

**自研 CRDT**
`sync/crdt.ts`，纯数据结构，带字符级文本合并，经过数十万次收敛测试（`scripts/test-sync.ts` 做 fuzz testing）。离线编辑后再同步，精确合并。

**自研图表引擎**
Bar / Line / Pie / Scatter，没有第三方依赖。演示时有 tooltip 和 zoom，Bar 变 Pie 时数据有 Morph 动画。

**签名自更新**
发布用 ECDSA 签名，应用内检查 manifest 时不发送任何关于你或你的文档的信息。更新会写一个**新文件**，旧文件作为回滚保留。服务器永远不碰你的文档。

**其他**
Speaker view（演讲者视图）、评论、布局、隐藏交互状态、Hover 显示、运动路径、PDF 导出、8 种 UI 语言，全在那 560KB 里。

---

## 三、AI 原生设计

因为文档是文件顶部的纯文本 JSON，任何能读写文件的 Agent 都可以直接编辑 `.bento.html`——无需插件，无需 API。

**两种接入方式**：

方式 1：**文件 Harness（推荐）**
Claude Code、Cursor、Aider 或任何有文件系统访问权限的 Agent 直接编辑 `#bento-doc` JSON 块。

Claude Code 用户有专属 Skill：

```
/plugin marketplace add nyblnet/bento
```

安装后 Skill 会自动下载最新版 Bento 应用，然后就可以用自然语言指挥 Claude Code 修改演示稿。

方式 2：**聊天往返（任何聊天 AI）**
*About → Copy document JSON* 把文档 JSON 复制出来，粘贴给 AI，AI 改完再粘贴回去。

**完全离线的本地模型也支持**：Ollama、llama.cpp、LM Studio 都能直接操作 Bento 文件，数据完全不出机器。

Agent 指南：`bento.page/agents.md`（一页，可以直接放进模型的 context）

---

## 四、架构骨架

```
slides/src/
  model.ts       ← JSON 文档模型（所有元素类型、幻灯片结构）
  render.ts      ← 统一渲染器（编辑画布、缩略图、演示模式）
  anim.ts        ← 自研动画引擎
  charts.ts      ← 自研图表引擎
  sync/crdt.ts   ← 自研 CRDT

server/sync-worker/  ← 可选的盲中继（Cloudflare Worker）
```

Reveal.js 处理幻灯片导航，Morph 动画从 model 计算，不依赖 DOM 状态。Shell 压缩到约 560KB，数据块保持明文，保证外部工具始终能解析。

---

## 五、Roadmap

`bento/slides` 是第一个应用（PPT 替代），现在就能用。

计划中：
- `bento/spaces` — 笔记
- `bento/dash` — 表格和数据
- `bento/vault` — （尚未透露）

每个都会是独立的自包含 `.bento.html` 分发文件。

---

## 六、一个哲学问题

Bento 的出现是一个有意思的时机选择：订阅制软件已经是行业标配，本地软件几乎绝迹，AI Agent 正在大规模扩张。

它提出了一个反问：如果文件可以携带自己的查看器和编辑器，如果协作可以通过文件传递而不是通过服务器，如果 AI 可以直接改文件里的 JSON——那么"软件"和"文档"之间的边界是否应该重新划定？

2756 stars 的 11 天速度，说明这个问题触到了某个共鸣。

---

**试用**

- 浏览器直接打开：`bento.page/slides`（就是完整 app，运行在示例演示稿上）
- 下载单文件：`bento.page/releases/slides/Bento_Slides.bento.html`（~560 KB）
- GitHub：`github.com/nyblnet/bento`（2756 ⭐，MIT，TypeScript）

<!--EN-->

## Bento: A Full Office Suite in a Single HTML File — A 560KB PowerPoint Alternative

Office software used to be something you *owned*. Now it's something you *rent* — locked in someone's cloud, behind someone's login, readable only while a company keeps its servers on.

Bento takes the other path.

**The entire PowerPoint alternative is a single HTML file.** 560KB, no account, no installer. Open it in any browser and it's the editor. Save, and it rewrites itself with your deck inside. Send it to someone — the file is the software. They need nothing.

Eleven days. 2,756 stars.

---

## Why This Design Is Radical

"File is software" isn't a tagline. Bento makes it engineering reality:

**Where data lives**: in the `#bento-doc` tag at the top of the file, as plain-text JSON. View-source and you see your data. No binary formats, no lock-in, no archaeology.

**How saving works**: File System Access API (with a download fallback). The file rewrites its own data block — only the JSON changes; the shell (renderer + editor + presenter) stays intact.

**File longevity**: README states: *"A copy from 2026 will open in 2036."* As long as browsers can run HTML, the file opens. No server, no format migration, no "legacy version unsupported."

**Offline mode**: When enabled, network requests are hard-blocked at the code level, and the app explicitly tells you it's fully offline. Not a verbal promise — a code-enforced isolation.

---

## Not a "Stripped-Down PPT"

The feature set is surprisingly complete:

**Morph animation**
Elements sharing the same `id` across two slides automatically animate between them — position, size, color, even gradients. Duplicate a slide, rearrange, and the transition designs itself. This is what PowerPoint calls a "Morph" transition configured manually; in Bento it's the default behavior.

**E2EE real-time collaboration**
Keys are minted client-side at document creation and live only in the file — never on a server. The file itself is the invitation: send anyone a copy, they open it, they've joined the room. Encryption: AES-GCM.

Collaboration uses an optional Cloudflare Worker relay (`server/sync-worker/`) — the relay sees only ciphertext, connection timestamps, and a hash of the room key. It cannot read content, names, or structure. Key rotation = revocation of all prior access.

**Custom CRDT**
`sync/crdt.ts`, pure data structures, with character-level text merging, fuzz-tested across hundreds of thousands of convergence checks (`scripts/test-sync.ts`). Edit offline, sync precisely when you reconnect.

**Custom chart engine**
Bar / Line / Pie / Scatter, zero third-party dependencies. Live tooltips and zoom during presentations. When a Bar chart becomes a Pie, the data morphs with it.

**Signed self-updates**
Releases are ECDSA-signed. In-app update checks fetch a static manifest and send nothing about you or your document. Updates write a *new* file — the old one stays as a rollback. No server ever touches your documents.

**Everything else**
Speaker view, comments, layouts, hidden interactive states, hover reveals, motion paths, PDF export, 8 UI languages — in a ~560KB shell.

---

## AI-Native Design

Because the document is plain JSON in a plaintext block near the top of the file, any agent with filesystem access can edit a `.bento.html` directly — no plugin, no API needed.

**Two access modes:**

**Mode 1: File harness (recommended)**
Claude Code, Cursor, Aider, or any agent with filesystem access edits the `#bento-doc` JSON block directly.

Claude Code users get a packaged skill:

```
/plugin marketplace add nyblnet/bento
```

The skill auto-downloads the latest Bento app, then you can instruct Claude Code in natural language to modify your deck.

**Mode 2: Chat round-trip (any AI)**
*About → Copy document JSON* extracts the document JSON, paste to your chatbot of choice, paste the modified JSON back.

**Fully offline with local models**: Ollama, llama.cpp, LM Studio all work — nothing leaves your machine. Agent guide is a single page: `bento.page/agents.md` (drop it into any model's context).

---

## Architecture Skeleton

```
slides/src/
  model.ts       ← JSON document model (all element types, slide structure)
  render.ts      ← unified renderer (editor canvas, thumbnails, present mode)
  anim.ts        ← custom animation engine
  charts.ts      ← custom chart engine
  sync/crdt.ts   ← custom CRDT

server/sync-worker/  ← optional blind relay (Cloudflare Worker)
```

Reveal.js handles slide navigation; Morph transitions are computed from the model, not DOM state. The shell compresses to ~560KB with the data block left as plaintext — external tools can always splice it.

---

## Roadmap

`bento/slides` (PPT alternative) is the first app, available now.

Planned:
- `bento/spaces` — notes
- `bento/dash` — sheets & tables
- `bento/vault` — (not yet revealed)

Each will be its own self-contained `.bento.html` distributable.

---

## A Design Question

Bento arrives at an interesting moment: subscription software is the industry default, local software is nearly extinct, AI agents are expanding massively.

It poses a counterquestion: if a file can carry its own viewer and editor, if collaboration can happen via files instead of servers, if AI can directly modify the JSON inside — should the line between "software" and "document" be redrawn?

2,756 stars in 11 days suggests this question resonates.

---

**Try it**

- Open in browser: `bento.page/slides` (full app, running on a demo deck)
- Download the file: `bento.page/releases/slides/Bento_Slides.bento.html` (~560 KB)
- GitHub: `github.com/nyblnet/bento` (2,756 ⭐, MIT, TypeScript)
