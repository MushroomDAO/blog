---
title: "ArtCraft：用 Claude Opus 5.5 并行开发的七套 Rust 原生 Adobe 替代工具"
titleEn: "ArtCraft: Seven Rust-Native Adobe Alternatives Built in Parallel with Claude Opus 5.5"
description: "ArtCraft 团队在一周内用 Rust 开源了 7 款创意软件：PhotoCraft（Photoshop 替代）、VectorCraft（Illustrator）、FilmCraft（Premiere）、LightCraft（Lightroom）、PrintCraft（Acrobat）、EffectCraft（After Effects）、DesignCraft（InDesign）。MIT/Apache-2.0 双协议，Rust 原生（无 Electron），WebAssembly 可跑浏览器。开发方式：Claude Opus 5.5 多并行 Agent 负责各子系统，人工做集成和发布，约 6–8 倍并行度。PhotoCraft 最成熟（6,691 stars），v0.2.0 早期 alpha，PSD 兼容约 68%，自评日常专业可用度 25–35%。VectorCraft 支持 MCP Server（`claude mcp add vectorcraft`），可被 AI Agent 直接操控。目前缺 AI 功能、插件生态、云同步；所有数字均为自报。"
descriptionEn: "ArtCraft released 7 open-source creative tools in Rust within a week: PhotoCraft (Photoshop), VectorCraft (Illustrator), FilmCraft (Premiere), LightCraft (Lightroom), PrintCraft (Acrobat), EffectCraft (After Effects), DesignCraft (InDesign). MIT/Apache-2.0 dual license, Rust-native (no Electron), WebAssembly for browsers. Development: Claude Opus 5.5 parallel agents handled subsystems, humans did integration and releases, ~6–8x parallel factor. PhotoCraft is the most mature (6,691 stars), v0.2.0 early alpha, PSD round-trip fidelity ~68%, self-rated 25–35% usable for daily professional work. VectorCraft includes an MCP Server (`claude mcp add vectorcraft`) for AI agent control. Currently missing: AI features, plugin ecosystem, cloud sync. All numbers self-reported."
pubDate: 2026-10-08
heroImage: "../../assets/images/artcraft-crafting-apps-rust-adobe-alternative-ai-built-banner.jpg"
category: "Tech-Experiment"
tags: ["开发工具", "开源工具", "Rust", "AI4AI", "创意软件", "MCP"]
lang: "zh-CN"
wechatTitle: "ArtCraft：AI并行开发的七套Adobe替代工具"
wechatDigest: "MIT；Rust原生7款；PhotoCraft 6.7K；VectorCraft MCP；Opus5.5开发"
---

七个仓库，一周内从零开始，全部 Rust 原生，全部开源。

ArtCraft 团队把 Adobe Creative Cloud 的整个创意工具链做了一遍替代实现。让这个项目引人注意的，不只是它的规模，还有它的开发方式：**Claude Opus 5.5 负责了大部分编码工作**，多个并行 Agent 各自承包独立子系统，人工做集成、测试和发布。

GitHub: https://github.com/storytold/vectorcraft（VectorCraft，MIT/Apache-2.0）

---

## 七款工具一览

| 工具 | 对应 | Stars | 创建时间 | 状态 |
|------|------|-------|----------|------|
| PhotoCraft | Photoshop | 6,691 | 9/30 | 早期 alpha |
| FilmCraft | Premiere | 1,624 | 9/30 | 开发中 |
| LightCraft | Lightroom | 1,244 | 9/30 | 开发中 |
| PrintCraft | Acrobat | 1,117 | 9/30 | 早期 alpha |
| VectorCraft | Illustrator | ~2,200 | 9/30 | 开发中 |
| EffectCraft | After Effects | 826 | 10/1 | 开发中 |
| DesignCraft | InDesign | 535 | 10/1 | 开发中 |

---

## 开发方式：Agent-hours 记账法

项目文档里有一个细节：剩余工作量用 **agent-hours** 而非 person-hours 来估算。

具体分工：Claude Opus 5.5 的多个并行 Agent 分别负责独立子系统（PSD 解析器、GPU 合成器、文本引擎、各类滤镜等），人工负责跨子系统集成、测试和对外发布。约 6–8 倍的并行度是项目自述的数字。

这个开发模式本身就是一个很有意思的数据点——**7 个创意软件，不到两周，全部 Rust。** 不论单个工具的成熟度如何，这个速度本身就说明了 AI 辅助开发在大型工程项目上的可能性。

---

## 技术基础

**Rust 原生，无 Electron，无 WebView**

所有工具都是原生 Rust 编译，macOS/Windows/Linux/FreeBSD 均可编译，部分工具额外提供 WebAssembly 版本可直接在浏览器运行。和 Electron 系工具相比，启动速度和内存占用差异显著。

**清洁室重实现**

项目声明采用 clean-room 方法：研究 Adobe 的公开规范和测试文件，不复制任何 Adobe 代码。这是版权合规的标准路径——类似当年 Wine 对 Windows API 的处理方式。

---

## PhotoCraft：最成熟的一个

PhotoCraft（v0.2.0，2026-10-05 发布）是整套工具里进度最靠前的：

- 625 个菜单项，全部接入了可执行命令
- 支持图层、蒙版、调整层、图层样式、画笔
- PSD/PSB 文件格式读写
- **PSD 像素级还原：约 68%**（170 个样本，115 个一致）
- 自评日常专业工作可用度：**25–35%**

"25–35% 可用" 这个数字很诚实——这是 alpha 阶段应有的状态，不是"已经够用"的公关说法。

---

## VectorCraft：MCP 原生设计

VectorCraft 里有一个对 AI Agent 工作流特别有意思的特性：**内置 MCP Server**。

```bash
claude mcp add vectorcraft
```

运行这条命令后，VectorCraft 可以直接被 Claude Code、Codex 等 AI Agent 调用——创建图形、修改路径、导出文件，无需人工操作界面。这是"创意软件作为 Agent 工具"的一个早期实践。

其他数字：
- 69–75% 的 Illustrator 功能已存在
- 2 万个图形约 27ms 渲染（多线程 SIMD）
- 精确曲线布尔运算，结构共享无限撤销
- 导入导出：SVG、PDF、兼容 `.ai`

目前缺少：3D/材质、栅格效果、CJK 竖排文字、变量与脚本。

---

## 现在的边界

**目前缺失的功能（所有工具）**：
- AI 辅助功能（讽刺：用 AI 开发的工具，自己暂时没有 AI 功能）
- 插件生态
- 云同步和素材库
- 大多数工具还不能用于商业项目交付

**可信度问题**：
- 所有 benchmark（PSD 兼容率、渲染速度、可用度百分比）均为项目自测，无第三方独立审计
- 仓库星数增长很快，但快速增长本身不等于可用性

**适合现在谁用**：开发者和技术探索者，用于研究、第二意见参考、或贡献代码。商业项目还不适合。

---

> MIT / Apache-2.0 双许可。ArtCraft 2026-09-30 起陆续发布，HuggingFace 无模型文件，工具代码在 storytold 账号下各仓库。开源仅供学习参考。

---

<!--EN-->

## ArtCraft: Seven Rust-Native Adobe Alternatives Built in Parallel with Claude Opus 5.5

Seven repositories, under two weeks, all Rust-native, all open source.

ArtCraft's team built a complete creative toolchain as open-source alternatives to Adobe Creative Cloud. What makes it notable is not just the scope but the development approach: **Claude Opus 5.5 handled most of the coding**, with multiple parallel agents owning independent subsystems and humans doing integration, testing, and releases.

GitHub: https://github.com/storytold/vectorcraft (VectorCraft, MIT/Apache-2.0)

---

### Seven Tools

| Tool | Adobe Equivalent | Stars | Created | Status |
|------|-----------------|-------|---------|--------|
| PhotoCraft | Photoshop | 6,691 | Sep 30 | Early alpha |
| FilmCraft | Premiere | 1,624 | Sep 30 | In development |
| LightCraft | Lightroom | 1,244 | Sep 30 | In development |
| PrintCraft | Acrobat | 1,117 | Sep 30 | Early alpha |
| VectorCraft | Illustrator | ~2,200 | Sep 30 | In development |
| EffectCraft | After Effects | 826 | Oct 1 | In development |
| DesignCraft | InDesign | 535 | Oct 1 | In development |

---

### Development: Agent-Hours Accounting

Project documentation estimates remaining work in **agent-hours** rather than person-hours — a small detail that reveals the workflow.

Claude Opus 5.5 parallel agents each owned independent subsystems (PSD parser, GPU compositor, text engine, filters). Humans handled cross-subsystem integration, testing, and releases. ~6–8x parallelism, per project documentation.

Seven creative apps, under two weeks, all Rust. Whatever the individual maturity level of each tool, the velocity itself is meaningful data about AI-assisted engineering at scale.

---

### Technical Foundation

**Rust-native, no Electron, no WebView**

All tools compile natively on macOS/Windows/Linux/FreeBSD, with some WebAssembly targets for browser use. Compared to Electron-based tools, startup speed and memory footprint differ significantly.

**Clean-room reimplementation**

The project studies Adobe's public specifications and test files without copying Adobe code — the same legal path Wine used for Windows API reimplementation.

---

### PhotoCraft: The Most Complete

PhotoCraft (v0.2.0, released 2026-10-05):

- 625 menu items, all wired to executable commands
- Layers, masks, adjustment layers, layer styles, brushes
- PSD/PSB read/write
- **PSD pixel-fidelity: ~68%** (115/170 samples)
- Self-rated professional daily usability: **25–35%**

"25–35% usable" is honest alpha-stage assessment, not marketing.

---

### VectorCraft: Built for AI Agents

VectorCraft ships with a built-in MCP Server:

```bash
claude mcp add vectorcraft
```

After that, Claude Code, Codex, or any MCP-compatible agent can directly create shapes, modify paths, and export files without touching the UI. An early data point for "creative software as agent tool."

Other numbers:
- 69–75% of Illustrator features present
- 20,000 shapes rendered in ~27ms (multi-thread SIMD)
- Exact curve booleans, structural-sharing infinite undo
- Import/export: SVG, PDF, `.ai`-compatible

Currently missing: 3D/materials, raster effects, CJK vertical text, variables/scripting.

---

### Current Boundaries

**Missing from all tools**: AI-assisted features (ironic), plugin ecosystems, cloud sync/asset libraries, production-readiness for commercial delivery.

**Credibility**: All benchmark numbers (PSD fidelity, render speed, usability percentages) are self-reported with no independent third-party audit.

**Who it's for now**: Developers and technical explorers for research, contribution, or second-opinion use. Not yet for commercial project delivery.

---

> MIT / Apache-2.0 dual license. ArtCraft released from 2026-09-30, under the storytold GitHub account. For technical reference only.
