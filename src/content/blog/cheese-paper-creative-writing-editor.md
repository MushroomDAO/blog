---
title: "Cheese Paper：离线优先、无遥测、专为小说创作设计的开源文本编辑器，v1.0.0 发布"
titleEn: "Cheese Paper: Offline-First, Zero-Telemetry Open-Source Editor Built for Fiction Writers — v1.0.0"
description: "Cheese Paper 是一款专为小说创作设计的离线开源编辑器，场景管理、角色卡、世界观数据库三合一，文件格式采用 Markdown+TOML，兼容任意文本编辑器和同步工具。GPLv3，无订阅，无遥测。v1.0.0 于 2026-05-30 发布，已上架 Flathub。"
descriptionEn: "Cheese Paper is an offline-first open-source creative writing editor combining scene management, character cards, and worldbuilding databases in one tool. Files use Markdown + TOML — readable in any editor, sync-friendly. GPLv3, no subscription, no telemetry. v1.0.0 released May 30, 2026, now on Flathub."
pubDate: "2026-06-02"
updatedDate: "2026-06-02"
category: "Tech-News"
tags: ["创意写作", "文本编辑器", "小说", "开源", "离线优先", "Markdown", "写作工具", "GPLv3", "Cheese Paper"]
heroImage: "../../assets/images/cheese-paper-writing-editor-banner.jpg"
---

写小说有一个隐形痛点：笔记和稿件永远分离。

你在 Notion 里写角色设定，在文档里写正文，在备忘录里记世界观细节——换场景时要在三个窗口之间反复跳转，刚建立的写作状态随时被打断。Scrivener 解决了这个问题，但它是付费闭源的；Manuskript 是开源替代，但体验粗糙。

Cheese Paper 是另一个答案。由独立开发者 ByteOfBrie 开发，v1.0.0 于 2026 年 5 月 30 日发布，代码托管在 Codeberg，GPLv3 授权。

> 📌 官网：https://brie.gay/cheese-paper/  
> Codeberg：https://codeberg.org/ByteOfBrie/cheese-paper  
> Flathub：搜索 `Cheese Paper`  
> License：GPLv3 | 平台：Windows、macOS、Linux

## 核心设计：笔记和稿件并排可见

Cheese Paper 的基本工作单元是**场景（Scene）**，而不是一个大文档。你把一部小说拆成若干场景，每个场景是独立文件，可以随意拖拽排序、标记状态。

写作时，左侧显示场景列表，右侧是编辑区，而**笔记栏可以在编辑区旁边始终可见**——角色卡、世界观设定、本场景的创作备忘，全部实时可查，不需要切窗口。

三个核心模块：

| 模块 | 功能 |
|------|------|
| **场景管理** | 拖拽排序、状态标记、大纲导出 |
| **角色数据库** | 角色卡，属性自定义，写作时随时调取 |
| **世界观数据库** | 地点、时间线、设定条目，统一管理 |

## 文件格式：Markdown + TOML，不绑定任何编辑器

这是 Cheese Paper 最值得关注的技术选择。

所有内容保存为 `.md` 文件，元数据（场景顺序、状态、字数目标等）写在文件头部的 TOML 块里：

```toml
+++
title = "第三章：破晓"
status = "draft"
word_target = 2000
+++

正文内容从这里开始……
```

**这意味着**：即使 Cheese Paper 明天停止维护，你的文件也能在任意文本编辑器里打开，格式完整可读。没有私有二进制格式，没有数据绑架。

导出时，Markdown 可以通过 Pandoc 转成 EPUB、DOCX、HTML、PDF——几乎覆盖所有出版和投稿需求。

## 同步：兼容所有你已经在用的工具

Cheese Paper 本身不提供云同步，但文件格式让同步变得透明：Syncthing、Nextcloud、Google Drive、Dropbox，任意工具都能正常同步，不会破坏文件结构。

这个设计选择有明确的立场：**工具层不应该绑架数据层**。你的稿件是你的，存在哪里、怎么备份，完全由你决定。

## 隐私：离线优先，单次网络请求

Cheese Paper 对网络访问的描述是："最多一次网络请求"——仅用于可选的版本更新检查，可以关闭。

无遥测、无使用数据收集、无账号体系。没有任何数据离开你的设备。

## 界面定制：主题随机生成器

除了内置的亮色和暗色主题，Cheese Paper 有一个**随机主题生成器**——点一下生成新配色，直到满意为止。

每个项目可以配置独立的拼写检查语言，写中英混排的项目不需要在全局设置里来回切换。

## v1.0.0：从实验性到正式发布

2026 年 5 月 30 日发布的 v1.0.0 是项目从实验性阶段走向正式版的节点，主要改进：

- 删除文件现在移入系统回收站（而非直接删除）
- 新增菜单文件创建入口，改善首次使用体验
- 修复若干 Flatpak 平台特有 bug
- Linux 版本正式上架 Flathub

## 关于"人类创作"的立场

项目页面明确写明：**Cheese Paper 由人类创作，不接受 AI 生成的社区贡献**。

这个立场在创意写作工具领域有特殊意义。面向小说作者的工具如果大量使用 AI 生成代码和文档，在用户群体中会产生明显的信任问题。ByteOfBrie 选择把这一点明确声明出来。

---

和 Scrivener 比：免费、开源、跨平台，文件格式不绑定；  
和 Obsidian 比：专门为线性叙事创作优化，场景和角色是一等公民；  
和 Manuskript 比：界面更现代，文件格式更简洁，维护更活跃。

如果你在写小说、剧本或任何需要管理场景和角色的长篇内容，Cheese Paper v1.0.0 是一个值得试用的选项。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Every novelist knows the invisible pain: notes and manuscript live in different apps.

Character sheets in Notion, prose in a document, worldbuilding in a notes app — every scene transition means jumping between three windows, breaking the writing flow you just built. Scrivener solves this, but it's proprietary and paid. Manuskript is an open-source alternative, but the UX is rough.

Cheese Paper is another answer. Built by independent developer ByteOfBrie, v1.0.0 launched May 30, 2026, hosted on Codeberg under GPLv3.

> 📌 Website: https://brie.gay/cheese-paper/  
> Codeberg: https://codeberg.org/ByteOfBrie/cheese-paper  
> Flathub: search `Cheese Paper`  
> License: GPLv3 | Platforms: Windows, macOS, Linux

## Core Design: Notes and Manuscript Side by Side

The fundamental work unit in Cheese Paper is a **Scene**, not a monolithic document. A novel gets broken into scenes — each an independent file — which can be dragged, reordered, and tagged with status.

While writing, the scene list sits on the left, the editor on the right, and **the notes panel stays persistently visible alongside the editor** — character cards, worldbuilding entries, per-scene notes, all available without switching windows.

Three core modules:

| Module | Function |
|--------|----------|
| **Scene manager** | Drag-to-reorder, status tags, outline export |
| **Character database** | Character cards with custom attributes, accessible during writing |
| **Worldbuilding database** | Locations, timelines, setting entries, centrally managed |

## File Format: Markdown + TOML — Not Locked to Any Editor

This is Cheese Paper's most noteworthy technical choice.

All content saves as `.md` files, with metadata (scene order, status, word targets) in a TOML header block:

```toml
+++
title = "Chapter Three: Dawn"
status = "draft"
word_target = 2000
+++

Body text starts here…
```

This means: even if Cheese Paper stops being maintained tomorrow, your files open perfectly in any text editor. No proprietary binary format, no data hostage situation.

For export, Markdown converts to EPUB, DOCX, HTML, or PDF via Pandoc — covering virtually all publishing and submission formats.

## Sync: Works With Whatever You Already Use

Cheese Paper doesn't offer built-in cloud sync, but the file format makes syncing transparent: Syncthing, Nextcloud, Google Drive, Dropbox — any tool works without corrupting file structure.

This is a deliberate design position: **the tool layer should not hold the data layer hostage**. Your manuscript is yours — where it lives and how it's backed up is entirely your decision.

## Privacy: Offline-First, One Optional Network Request

Cheese Paper's description of its network usage: "at most one network request" — only for optional update checking, which can be disabled.

No telemetry, no usage data collection, no account system. Nothing leaves your device.

## UI: Random Theme Generator

Beyond built-in light and dark themes, Cheese Paper includes a **random theme generator** — click to generate a new color scheme until you find one you like.

Each project gets its own spellcheck language configuration — no need to change global settings when working on multilingual content.

## v1.0.0: From Experimental to Stable

The May 30 v1.0.0 release marks the project's transition from experimental to production-ready:

- Deleted files now go to system trash instead of permanent deletion
- New menu entries for file creation improve first-run experience
- Several Flatpak-specific bugs fixed
- Linux version officially listed on Flathub

## Stance on "Human-Made"

The project page explicitly states: **Cheese Paper is made by humans and does not accept AI-generated community contributions.**

This position carries specific weight in creative writing tools. A tool aimed at novelists that relies heavily on AI-generated code and documentation creates a trust problem with its user base. ByteOfBrie chose to state this clearly upfront.

---

Compared to Scrivener: free, open-source, cross-platform, portable file format.  
Compared to Obsidian: optimized for linear narrative, scenes and characters are first-class citizens.  
Compared to Manuskript: more modern UI, cleaner file format, more actively maintained.

If you write novels, screenplays, or any long-form content that involves managing scenes and characters, Cheese Paper v1.0.0 is worth trying.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
