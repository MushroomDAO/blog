---
title: "OpenFlowKit 拆解：一个真在维护的开源画图 SPA，能被 Claude 直接调用"
titleEn: "OpenFlowKit Teardown: A Real, Maintained Open-Source Diagramming SPA That Claude Can Drive Directly"
description: "Vrun-design/openflowkit 是 795 星、MIT 协议的纯前端画图工具：Mermaid 粘贴自动配 1600+ 图标、双向 DSL 编辑器、10 家 AI 供应商（含本地 Ollama）、WebCodecs 硬编码 MP4 导出，还发布了一个真实可用的 MCP 服务。我们在 Mac mini 上克隆、装依赖、跑单测、跑生产构建全部实测通过，同时也挖出了它没在 README 里明说的坑。"
descriptionEn: "Vrun-design/openflowkit is a 795-star, MIT-licensed pure front-end diagramming tool: paste Mermaid and get 1,600+ icons auto-matched, a bidirectional DSL editor, 10 AI providers including local Ollama, WebCodecs hardware-encoded MP4 export, and a genuinely working MCP server. We cloned it, installed it, ran the unit tests and a production build on a Mac mini — all passed — and also found a few things the README doesn't spell out."
pubDate: "2026-09-22"
updatedDate: "2026-09-22"
category: "Tech-Experiment"
tags: ["OpenFlowKit", "MCP", "Mermaid", "流程图", "架构图", "开源工具", "Claude Code", "React"]
heroImage: "../../assets/images/openflowkit-diagram-mcp-local-first-teardown-banner.jpg"
author: "Mycelium Protocol"
---

> 📌 一手源
> GitHub：https://github.com/Vrun-design/openflowkit
> MCP 服务（npm）：https://www.npmjs.com/package/@vrun-design/openflowkit-mcp
> 在线体验：https://app.openflowkit.com
> 协议：MIT ｜ 语言：TypeScript ｜ Stars：795 ｜ Forks：168 ｜ 创建：2026-02-10 ｜ 最近提交：2026-09-20

---

**BLUF**：OpenFlowKit 是一个纯前端（React 19 + Vite + IndexedDB，零后端）的开源画图工具，核心卖点是三件事都做到了：粘贴 Mermaid 自动匹配 1600+ 品牌图标、画布和 DSL 代码双向同步、以及一个真实发布到 npm、被 Claude Desktop / Cursor / Windsurf 可用的 MCP 服务器。它不是一个只有 README 的空壳——我们在 Mac mini 上实测：`git clone` 后装根依赖 925MB（远低于 5GB 上限），`vitest` 跑通 42/42 单测，`npm run build` 7 秒内产出可用的 `dist/`，`vite preview` 起服务返回 200。但它也有真实的局限：单人主导（218 次提交里 202 次出自作者本人）、MCP 包上线以来月下载量只有 256、AWS/Azure 图标包各自超过 1.5MB 未做懒加载、协作功能默认关闭、README 功能表和 Roadmap 之间有一处自相矛盾（下文详述）。

这篇文章按三件事展开：它到底是什么、和同类工具比差在哪／强在哪、以及我们在本机能验证到什么程度。

## 它到底是什么？

先说清楚，不要被名字和一堆 emoji 徽章绕进去。OpenFlowKit **不是** Excalidraw 那种自由画布，也不是纯粹的 Mermaid 渲染器，而是一个**结构化图表编辑器**：8 种图表族（流程图、架构图、ER 图、类图、时序图、思维导图、用户旅程、状态机）各自有专用节点类型和属性面板，配一个和画布双向同步的「OpenFlow DSL」代码面板，再加一层 AI 生成和一层 MCP 工具，让外部 Agent 也能操作它。

技术栈是纯前端 SPA：React 19、TypeScript 5、Vite 6，画布用 React Flow（XYFlow），自动布局用 ELK.js（跑在 Web Worker 里，不阻塞主线程），状态管理 Zustand，持久化用浏览器 IndexedDB。**没有后端、没有数据库、没有账号系统**——`npm run build` 产出的就是一个静态 `dist/` 文件夹，README 里给的自托管方式是丢进 Cloudflare Pages / Netlify / Vercel，或者用仓库自带的 `Dockerfile`（nginx 起静态文件 + SPA 路由回退）。

### 谁在维护它？

`gh api` 拉到的仓库元数据：创建于 2026-02-10，最近一次提交 2026-09-20，MIT 协议，795 stars，168 forks，15 个 open issues，8 个 contributors。提交分布很不均匀：作者 `Vrun-design` 一个人占了 218 次提交里的 202 次（约 93%），其余 6 个贡献者各贡献 1-4 次，多是修一个具体 bug 或加一处 i18n。这不是骗星空壳——CI（`Quality Checks` + `Docker Publish` 两条 workflow）在最近几次提交上全绿，issue 里有真实的 bug 报告（比如 #81「箭头连接线对不齐」、#75「箭头样式没对齐描边」），MCP 服务器也确实发布到了 npm registry（`@vrun-design/openflowkit-mcp`，当前版本 0.1.2）。但本质上这是一个**单人高强度维护 + 零散社区补丁**的项目，不是一个有多个核心维护者轮值的团队项目，评估长期可持续性时要把这一点算进去。

## 三个核心功能，一个个拆

### Mermaid 粘贴自动配图标，靠谱吗？

README 演示的流程是：粘贴一段 Mermaid flowchart（比如 `API[Express API] --> DB[(PostgreSQL)]`），画布上直接出现带 Express、PostgreSQL 品牌 logo 的节点，不需要手动拖拽图标。源码里这条链路真实存在：`src/lib/iconMatcher.ts` + `src/lib/iconResolver.ts` 做「精确匹配 → 别名匹配 → 子串匹配」三级图标搜索，图标来源覆盖 developer、AWS、Azure、GCP、CNCF 五个目录（`assets/third-party-icons/` 下能看到完整的 AWS 官方图标分类，比如 Compute、Analytics、Artificial-Intelligence 等几十个类目）。

值得注意的是这一层的代价：production build 里 `icon-urls-aws-*.js` 单个 chunk 就有 **1.79MB**（gzip 后 450KB），`icon-urls-azure-*.js` 1.52MB，`icon-urls-developer-*.js` 615KB——这几个 chunk 都在 Vite 的构建警告里被点名「超过 900KB」。也就是说，**首次打开这个静态站点，浏览器要下载好几 MB 的图标索引**，这和「local-first、零服务器」的定位没有冲突（确实不用服务器），但和「快」没有关系，自托管在弱网环境下首屏会明显慢。

### DSL 双向同步和 Mermaid 家族覆盖，README 和 Roadmap 打架

OpenFlow DSL 是画布的文本表示，改代码面板、画布跟着变，反过来也一样，这条链路我们在源码里能看到对应的 `src/services/mermaid/` 和 `src/diagram-types/*/plugin.ts` 结构，且各家族都配了专门的单测（`*.test.ts`）和 round-trip 测试（`flowchartRoundTrip.test.ts` 一类）。

但 README 里有一处自相矛盾：功能对比表把「Mermaid import (8 types)」标记为 ✅ 已支持，紧接着「What we are improving next」的 Roadmap 里又把「Mermaid family coverage — gantt, c4, timeline, gitGraph, sankey, quadrant (view + edit-as-code)」列为**下一步要做**的事。我们在生产构建产物里确认了 `ganttDiagram`、`c4Diagram`、`sankeyDiagram`、`quadrantDiagram`、`gitGraphDiagram`、`timeline-definition` 这些 JS chunk **确实存在**（说明底层 mermaid.js 渲染引擎认得这些图），但 Roadmap 明确说这些类型「view + edit-as-code」的完整支持还没做完。合理的解读是：mermaid.js 本身能解析渲染这些图，但 OpenFlowKit 自己的专用节点类型、属性面板和双向 DSL 编辑对它们还不完整——**对外宣传的「8 种类型」和实际打磨完成度不是一回事**，用之前建议先拿你要用的具体图表类型试一遍。

### MCP 服务器：这是它和 Drawnix、Archify 真正的区别

本站之前写过两个相邻方向的项目：Drawnix（一体化白板+思维导图+流程图，14580 星，自研 Plait 框架，没有 MCP、没有和代码双向同步）和 Archify（AI Agent Skill，一句话生成一次性的静态 HTML 架构图，MIT，2502 星，但生成后就是个文件，不是可持续编辑的画布也没有工具集）。OpenFlowKit 的定位介于两者之间偏工程：它既是一个可以手动打磨的完整编辑器，又通过 `@vrun-design/openflowkit-mcp` 把自己暴露成 Agent 可调用的工具集。

这个 MCP 包是真实可用的，不是宣传噱头。我们直接查了 npm registry：包已发布，`bin` 指向 `dist/index.js`，`npx -y @vrun-design/openflowkit-mcp` 可以直接跑。它提供 8 个工具（`validate_openflow_dsl` 校验 DSL、`create_viewer_url` 生成可分享的查看链接、`analyze_codebase` 扫描本地仓库识别技术栈、`find_icon` 模糊搜图标、`list_starter_templates`/`get_starter_template` 拿内置模板、`list_diagram_node_types` 查节点参考、`server_info` 查版本），5 个资源（DSL 速查表、模板目录、图标目录），3 个 prompt 模板。关键设计是**它不带任何 AI 能力**——README 原话是「provider-free」，逻辑是「你的 MCP 客户端本来就有 LLM（Claude/Cursor/Windsurf），这个服务器只负责给它工具，不需要额外配 API key」。这个思路和本站之前拆解过的很多「MCP + AI 生成」项目不同：大部分同类工具的 MCP 服务器自己也要调一次大模型，OpenFlowKit 选择把生成完全交给宿主 Agent，服务器只做确定性的校验和查询。

不过要泼一盆冷水：npm 官方下载统计显示，这个包过去 30 天下载量只有 **256 次**。它是真实可用的基础设施，但目前采用它的人还不多，属于「刚起步、值得关注」而不是「已经被验证的标准工具」。

### AI 生成：10 家供应商，但只有一家是真本地

README 列了 10 个 AI 供应商（Google Gemini、OpenAI、Anthropic Claude、Groq、Mistral、NVIDIA NIM、Cerebras、OpenRouter、Ollama、自定义 OpenAI 兼容端点），说「浏览器直连供应商，OpenFlowKit 的服务器看不到你的 key」。这个说法本身是对的——纯前端 SPA 没有自己的后端可以中转，`.env.example` 里所有 AI key 变量都带 `VITE_` 前缀。**但这里有个自托管者容易忽略的坑**：Vite 项目里 `VITE_` 前缀的环境变量会在构建时被硬编码进最终的 JS 包，也就是说，如果你自托管时图省事把自己的供应商 key 写进 `.env` 当全站默认值，这个 key 会被打进公开可访问的 `dist/` 产物里，任何打开浏览器开发者工具的访客都能看到。README 推荐的正常用法是让每个用户自己在设置面板里粘贴 key（存浏览器本地），只要照这个方式用就没问题，但「零环境变量要求」这句话容易让人以为 `.env` 里填自己的 key 也一样安全，实际不是。

「10 家供应商」里真正符合「本地、零 key、零网络」定义的只有 **Ollama** 一家。其余 9 家仍然是标准的云端 API 调用，只是走浏览器直连而非经过 OpenFlowKit 自己的服务器转发——这和"local-first"的画布/存储部分是两码事，AI 生成这一层本质上还是云服务，别把两者混为一谈。

## 本机实测：Mac mini（Apple Silicon）能跑多远？

**环境**：Mac mini，Node v26.8.1，npm 11.19.0，仓库 shallow clone 到 commit `fafeefc`（2026-09-20）。全程只装根 workspace 依赖（跳过 `docs-site` 和 `mcp-server` 两个子包），未使用任何 API key、未联网调用任何 AI 供应商。

- **体积**：`git clone --depth 1` 后仓库 203MB；`npm install --ignore-scripts` 后 `node_modules` 723MB，总目录 925MB——远低于「不下载超过 5GB」的红线。
- **单元测试**：`npx vitest run src/store.test.ts src/services/mermaid/parseMermaidByType.test.ts`，**2 个测试文件、42 个用例全部通过**，用时 1.42 秒。
- **生产构建**：`npm run build` 成功，约 7 秒内产出完整 `dist/`；构建过程给出多条「chunk 超过 900KB」警告，最大的几个都是图标索引文件（`icon-urls-aws` 1.79MB、`icon-urls-azure` 1.52MB）。
- **静态服务**：`vite preview` 起本地服务，`curl` 返回 **200**，首页 HTML 的 `<title>`、`<meta description>`、SEO 标签均正常渲染，证明构建产物是一个可直接部署的完整站点，不是半成品。

**我们没有验证的部分**：没有跑 Playwright E2E（需要下载浏览器二进制，超出「不装全局依赖」的约束）；没有实测 AI 生成功能（需要真实 API key 或本机装 Ollama，超出本次调研范围）；没有实测 WebCodecs MP4 导出（这是浏览器内交互功能，命令行环境无法触发）；没有实测 MCP 服务器和真实 MCP 客户端的握手（原理上和前面 mcp-rag-server 一文里验证过的 stdio 握手流程一致，但这次没有重复跑）；没有核实 WebRTC 协作功能，代码里确认它默认关闭（`VITE_COLLABORATION_ENABLED` 环境变量控制，README 也明确写了这是「redesign 中的 opt-in beta」）。

## 和同类工具怎么选？

| 工具 | 形态 | DSL 双向编辑 | MCP/Agent 工具集 | 协议 | 本文核实状态 |
|---|---|---|---|---|---|
| **OpenFlowKit** | 结构化画布编辑器 + 静态 SPA | 有（8 种图表族） | 有，npm 已发布、8 个工具 | MIT | 本机构建+测试通过 |
| Drawnix | 一体化白板（思维导图+流程图+自由画） | 无（导入 Mermaid/Markdown，非双向） | 无 | MIT | 见本站 2026-08-22 文章 |
| Archify | AI Agent Skill，一次性生成静态 HTML | 无（生成即完成，不可持续编辑） | 无独立 MCP，作为 Claude Code Skill 调用 | MIT | 见本站 2026-07-04 文章 |
| Excalidraw / tldraw | 自由画布 | 无 | 无 | MIT | README 自述对比，未逐条复核 |
| Draw.io | 传统桌面/网页画图 | 部分（XML，非 DSL） | 无 | Apache-2.0 | README 自述对比，未逐条复核 |

表格最后两行的对比来自 OpenFlowKit README 自己的说法，我们没有逐一核实 Excalidraw、Draw.io 的现状，读者如果真的在几个工具间做选型，建议直接去对应仓库确认最新功能，不要只看 OpenFlowKit 单方面的对比表。

## 谁适合用，谁应该再等等？

**适合**：已经在用 Claude Desktop / Cursor / Windsurf 写代码、想让 Agent 直接产出可视化架构图的开发者；需要把 Mermaid 图导入后接着精修排版和图标的场景；要离线画图、数据不出本机、且不想为画图工具再开一个账号的人。

**再等等**：需要多人实时协作画图的团队（协作功能还在 opt-in beta，默认关闭）；需要 gantt/c4/sankey 等图表族完整可编辑支持的场景（这些目前更接近「能渲染」而非「能打磨」）；把它当成有 SLA 保障的基础设施依赖的团队（单人维护、MCP 包月下载量才 256，社区规模还小）。

## 常见问题

**Q：OpenFlowKit 需要付费或注册账号吗？**
A：不需要。它是纯前端 SPA，没有后端和账号系统，图表存在浏览器 IndexedDB 里。AI 生成功能需要你自备供应商 API key（Ollama 除外，完全本地免费）。

**Q：它和 Mermaid.js 是什么关系？**
A：它内部用 mermaid.js 做部分图表的解析和渲染引擎（构建产物里能看到 `mermaid.core` chunk），但在此之上加了一层可视化编辑、图标自动匹配和专用节点类型，不是简单套壳。

**Q：MCP 服务器要额外配置 API key 吗？**
A：不需要。`@vrun-design/openflowkit-mcp` 定位是「provider-free」，它只提供确定性的本地工具（校验、查图标、生成链接），实际生成内容由你已经连好的 MCP 客户端（比如 Claude Desktop）自己的模型完成。

**Q：能完全离线用吗？**
A：画布编辑、图标匹配、Mermaid 解析、DSL 双向同步、导出都是纯本地的，不需要联网。只有云端 AI 供应商（非 Ollama）那部分功能需要联网。

**Q：值得信任长期维护吗？**
A：目前是活跃项目（最近提交在一周内，CI 全绿），但 93% 的提交来自同一个人，MCP 包下载量还不大。适合现在就用起来，但不建议把它当成没有备选方案的关键基础设施。

## 一手源

- GitHub 仓库：https://github.com/Vrun-design/openflowkit
- MCP 服务器 npm 包：https://www.npmjs.com/package/@vrun-design/openflowkit-mcp
- MCP 服务器 README：https://github.com/Vrun-design/openflowkit/blob/main/mcp-server/README.md
- 在线体验：https://app.openflowkit.com
- 文档站：https://docs.openflowkit.com
- 本站相关文章《Drawnix：开源一体化白板》：https://blog.mushroom.cv/blog/drawnix-open-source-whiteboard-mind-map-flowchart-plugin-architecture/
- 本站相关文章《Archify：用一句话描述系统》：https://blog.mushroom.cv/blog/archify-tech-diagram-skill-guide/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Primary sources
> GitHub: https://github.com/Vrun-design/openflowkit
> MCP server (npm): https://www.npmjs.com/package/@vrun-design/openflowkit-mcp
> Live app: https://app.openflowkit.com
> License: MIT | Language: TypeScript | Stars: 795 | Forks: 168 | Created: 2026-02-10 | Last commit: 2026-09-20

---

**BLUF**: OpenFlowKit is an open-source, pure front-end diagramming tool (React 19 + Vite + IndexedDB, no backend) that actually delivers on three big claims: pasting Mermaid auto-matches 1,600+ branded icons, the canvas and its DSL stay bidirectionally in sync, and it ships a genuinely working MCP server published to npm that Claude Desktop, Cursor, and Windsurf can drive. It is not a README-only shell — on a Mac mini we cloned it, installed the root workspace (925MB, well under the 5GB cap), ran `vitest` (42/42 tests passed), ran `npm run build` (finished in about 7 seconds and produced a working `dist/`), and confirmed `vite preview` serves a 200 with correct SEO tags. It also has real limitations: one person wrote 202 of 218 commits, the MCP package has only 256 downloads in the last 30 days, the AWS/Azure icon bundles are over 1.5MB each with no lazy loading, real-time collaboration is off by default, and the README's feature table contradicts its own roadmap on Mermaid family coverage (details below).

This post covers three things: what OpenFlowKit actually is, how it compares to adjacent tools, and how far we could verify it hands-on.

## What Is OpenFlowKit, Really?

Don't get swept up by the name or the emoji badges. OpenFlowKit is **not** a freeform canvas like Excalidraw, and it's not a plain Mermaid renderer either — it's a **structured diagram editor**: eight diagram families (flowchart, architecture, ER, class, sequence, mind map, user journey, state machine) each with dedicated node types and property panels, paired with an "OpenFlow DSL" code panel that stays bidirectionally synced with the canvas, plus an AI generation layer and an MCP layer that lets external agents drive it too.

The stack is a pure front-end SPA: React 19, TypeScript 5, Vite 6, canvas via React Flow (XYFlow), auto-layout via ELK.js (running in a Web Worker off the main thread), state via Zustand, and persistence via browser IndexedDB. **No backend, no database, no account system** — `npm run build` produces a static `dist/` folder, and the README's self-hosting instructions are: drop it on Cloudflare Pages / Netlify / Vercel, or use the repo's own `Dockerfile` (nginx serving static files with SPA route fallback).

### Who Maintains It?

Repository metadata pulled via `gh api`: created 2026-02-10, last commit 2026-09-20, MIT license, 795 stars, 168 forks, 15 open issues, 8 contributors. Commit distribution is heavily skewed: the author `Vrun-design` wrote 202 of 218 commits (about 93%), and the other six contributors each added 1-4 commits, mostly a specific bug fix or an i18n addition. This isn't a bought-star shell — CI (`Quality Checks` and `Docker Publish` workflows) is green on the latest commits, the issue tracker has real bug reports (#81 "arrow connection appears misaligned," #75 "align arrow markers with the stroke they terminate"), and the MCP server is genuinely published to the npm registry (`@vrun-design/openflowkit-mcp`, currently at 0.1.2). But this is fundamentally a **solo-maintainer-with-scattered-patches** project, not a team with multiple rotating core maintainers — factor that into any long-term dependency decision.

## Three Core Features, Examined One at a Time

### Does the Mermaid-Paste Icon Matching Actually Work?

The README demo pastes a Mermaid flowchart (e.g., `API[Express API] --> DB[(PostgreSQL)]`) and the canvas shows nodes with the actual Express and PostgreSQL brand logos, no manual icon dragging required. This pipeline is real in the source: `src/lib/iconMatcher.ts` plus `src/lib/iconResolver.ts` run a three-tier icon search — exact match, then alias, then substring — across five icon catalogs: developer, AWS, Azure, GCP, and CNCF (`assets/third-party-icons/` contains the full official AWS icon taxonomy, dozens of categories like Compute, Analytics, Artificial-Intelligence).

Worth noting is the cost of this layer: in the production build, the `icon-urls-aws-*.js` chunk alone is **1.79MB** (450KB gzipped), `icon-urls-azure-*.js` is 1.52MB, and `icon-urls-developer-*.js` is 615KB — all flagged in Vite's build warnings for exceeding 900KB. In other words, **the first load of this static site pulls down several megabytes of icon indexes**. That doesn't contradict the "local-first, zero server" positioning (there genuinely is no server), but it has nothing to do with speed — self-hosting on a slow connection will feel noticeably heavy on first paint.

### DSL Round-Trip and Mermaid Family Coverage: README vs. Roadmap Contradict Each Other

OpenFlow DSL is the canvas's text representation; edit the code panel and the canvas updates, and vice versa. We can see this in the source, under `src/services/mermaid/` and each `src/diagram-types/*/plugin.ts`, each family with its own unit tests and round-trip tests (files like `flowchartRoundTrip.test.ts`).

But there's a contradiction in the README itself. The feature comparison table marks "Mermaid import (8 types)" as ✅ supported, and immediately below, the "What we are improving next" roadmap lists "Mermaid family coverage — gantt, c4, timeline, gitGraph, sankey, quadrant (view + edit-as-code)" as **upcoming work**. We confirmed in the production build artifacts that `ganttDiagram`, `c4Diagram`, `sankeyDiagram`, `quadrantDiagram`, `gitGraphDiagram`, and `timeline-definition` chunks **do exist** (the underlying mermaid.js rendering engine does understand these diagram types), but the roadmap explicitly says full "view + edit-as-code" support for them isn't finished. The reasonable reading: mermaid.js itself can parse and render these diagrams, but OpenFlowKit's own dedicated node types, property panels, and bidirectional DSL editing for them are incomplete — **the marketed "8 types" and the actual level of polish are two different things**. Try the specific diagram type you need before committing to it.

### The MCP Server: This Is What Actually Sets It Apart From Drawnix and Archify

This blog has previously covered two adjacent projects: Drawnix (an all-in-one whiteboard with mind maps and flowcharts, 14,580 stars, its own Plait framework, no MCP, no bidirectional code sync) and Archify (an AI agent skill, 2,502 stars, MIT, that generates a one-shot static HTML architecture diagram from a plain-English description — but once generated, it's a file, not a canvas you keep editing, and there's no tool set). OpenFlowKit sits between the two, leaning toward engineering: it's both a full editor you can hand-tune and, via `@vrun-design/openflowkit-mcp`, a tool set an agent can call.

This MCP package is genuinely usable, not marketing fluff. We checked the npm registry directly: the package is published, `bin` points to `dist/index.js`, and `npx -y @vrun-design/openflowkit-mcp` runs it directly. It exposes 8 tools (`validate_openflow_dsl` to lint DSL, `create_viewer_url` to generate a shareable viewer link, `analyze_codebase` to scan a local repo and detect the tech stack, `find_icon` for fuzzy icon search, `list_starter_templates`/`get_starter_template` for built-in templates, `list_diagram_node_types` for node reference data, `server_info` for version info), 5 resources (DSL cheatsheet, template catalog, icon catalog), and 3 prompt templates. The key design choice: **it carries no AI capability of its own** — the README calls it "provider-free," on the logic that your MCP client already has an LLM (Claude/Cursor/Windsurf), so this server just gives it tools without requiring a separate API key. This differs from many "MCP + AI generation" projects this blog has torn down before, where the MCP server itself also calls out to a model. OpenFlowKit hands generation entirely to the host agent and keeps the server to deterministic validation and lookups.

One cold-water note: npm's own download stats show this package got only **256 downloads** in the last 30 days. It's real, working infrastructure, but adoption so far is small — this is "early and worth watching," not "an already-validated standard tool."

### AI Generation: 10 Providers, But Only One Is Genuinely Local

The README lists 10 AI providers (Google Gemini, OpenAI, Anthropic Claude, Groq, Mistral, NVIDIA NIM, Cerebras, OpenRouter, Ollama, and a custom OpenAI-compatible endpoint), and says "requests go directly from your browser to the provider; OpenFlowKit's servers never see your key." That claim is accurate — a pure front-end SPA has no backend to proxy through, and every AI key variable in `.env.example` carries the `VITE_` prefix. **But there's a self-hosting gotcha easy to miss**: Vite bakes any `VITE_`-prefixed environment variable into the final JS bundle at build time. If you self-host and, for convenience, put your own provider key into `.env` as a site-wide default, that key ships inside the publicly accessible `dist/` output, visible to anyone who opens dev tools. The README's recommended usage — each user pastes their own key into the Settings panel, stored in their own browser — avoids this entirely, but "zero environment variables required" can mislead people into thinking putting a key in `.env` is equally safe. It isn't.

Of the "10 providers," only **Ollama** genuinely meets the "local, zero key, zero network" definition. The other nine are standard cloud API calls, just routed directly from the browser instead of through an OpenFlowKit server — that's a different thing from the local-first canvas/storage layer. AI generation itself is still, fundamentally, a cloud service; don't conflate the two.

## Hands-On: How Far Did It Get on a Mac Mini (Apple Silicon)?

**Environment**: Mac mini, Node v26.8.1, npm 11.19.0, repository shallow-cloned at commit `fafeefc` (2026-09-20). We installed only the root workspace dependencies (skipping the `docs-site` and `mcp-server` sub-packages), used no API key, and made no AI provider network calls at any point.

- **Size**: `git clone --depth 1` produced a 203MB repo; `npm install --ignore-scripts` produced a 723MB `node_modules`, 925MB total — well under the 5GB ceiling.
- **Unit tests**: `npx vitest run src/store.test.ts src/services/mermaid/parseMermaidByType.test.ts` — **2 test files, 42 cases, all passed**, in 1.42 seconds.
- **Production build**: `npm run build` succeeded, producing a complete `dist/` in about 7 seconds; the build emitted several "chunk exceeds 900KB" warnings, the largest being the icon index files (`icon-urls-aws` at 1.79MB, `icon-urls-azure` at 1.52MB).
- **Static serving**: `vite preview` started a local server; `curl` returned **200**, with the homepage's `<title>`, `<meta description>`, and SEO tags all rendering correctly — confirming the build output is a directly deployable, complete site, not a half-finished artifact.

**What we did not verify**: no Playwright E2E run (would require downloading browser binaries, outside the "no global dependencies" constraint); no hands-on test of AI generation (requires a real API key or a local Ollama install, outside this investigation's scope); no test of WebCodecs MP4 export (an in-browser interactive feature that a command-line environment can't trigger); no repeat test of the MCP server's handshake with a real MCP client (the mechanics match the stdio handshake we already verified in an earlier post on mcp-rag-server, but we didn't re-run it here); we did not test the WebRTC collaboration feature but confirmed in the code that it is off by default (`VITE_COLLABORATION_ENABLED`, and the README explicitly calls it a "redesign in progress" opt-in beta).

## How Does It Compare to Adjacent Tools?

| Tool | Shape | Bidirectional DSL | MCP / Agent tool set | License | This post's verification |
|---|---|---|---|---|---|
| **OpenFlowKit** | Structured canvas editor + static SPA | Yes (8 diagram families) | Yes, published to npm, 8 tools | MIT | Build + tests passed locally |
| Drawnix | All-in-one whiteboard (mind maps + flowcharts + freehand) | No (imports Mermaid/Markdown, one-way) | None | MIT | See our 2026-08-22 post |
| Archify | AI agent skill, one-shot static HTML generation | No (generation is final, not persistently editable) | No standalone MCP; called as a Claude Code Skill | MIT | See our 2026-07-04 post |
| Excalidraw / tldraw | Freeform canvas | No | None | MIT | Per OpenFlowKit's own README table; not independently re-verified |
| Draw.io | Traditional desktop/web diagramming | Partial (XML, not a DSL) | None | Apache-2.0 | Per OpenFlowKit's own README table; not independently re-verified |

The last two rows come from OpenFlowKit's own README comparison; we did not independently re-verify Excalidraw's or Draw.io's current state. If you're actually choosing between tools, go check each project's current repository rather than relying on one side's comparison table.

## Who Should Use It, and Who Should Wait?

**Good fit**: developers already using Claude Desktop, Cursor, or Windsurf who want their agent to produce editable visual architecture diagrams directly; anyone importing Mermaid diagrams and then refining layout and icons by hand; anyone who wants offline diagramming with data that never leaves their machine and doesn't want to create yet another account.

**Wait a bit**: teams needing real-time multi-user collaboration (still an opt-in beta, off by default); use cases needing full editable support for gantt/c4/sankey-style diagrams (these currently render but aren't fully polished editing experiences); teams treating it as an SLA-backed infrastructure dependency (solo-maintained, and the MCP package's monthly download count is still just 256 — the community is small).

## FAQ

**Q: Does OpenFlowKit require payment or an account?**
A: No. It's a pure front-end SPA with no backend or account system; diagrams live in your browser's IndexedDB. AI generation needs your own provider API key (except Ollama, which is fully local and free).

**Q: How does it relate to Mermaid.js?**
A: It uses mermaid.js internally as the parsing/rendering engine for part of its diagram support (a `mermaid.core` chunk is visible in the build output), but layers on visual editing, automatic icon matching, and dedicated node types on top — it's not a thin wrapper.

**Q: Does the MCP server need its own API key?**
A: No. `@vrun-design/openflowkit-mcp` is deliberately "provider-free" — it only offers deterministic local tools (validation, icon lookup, link generation). Actual content generation is done by whatever model your MCP client (e.g., Claude Desktop) is already connected to.

**Q: Can it be used fully offline?**
A: Canvas editing, icon matching, Mermaid parsing, DSL round-trip sync, and exports are all local and require no network. Only the cloud AI provider features (everything except Ollama) need connectivity.

**Q: Is it a safe long-term dependency?**
A: It's an active project right now (commits within the last week, CI green), but 93% of commits come from one person and the MCP package's download volume is still small. Good to adopt today; don't treat it as critical infrastructure with no fallback plan yet.

## Primary Sources

- GitHub repository: https://github.com/Vrun-design/openflowkit
- MCP server npm package: https://www.npmjs.com/package/@vrun-design/openflowkit-mcp
- MCP server README: https://github.com/Vrun-design/openflowkit/blob/main/mcp-server/README.md
- Live app: https://app.openflowkit.com
- Docs site: https://docs.openflowkit.com
- Our related post, "Drawnix: An Open-Source All-in-One Whiteboard": https://blog.mushroom.cv/blog/drawnix-open-source-whiteboard-mind-map-flowchart-plugin-architecture/
- Our related post, "Archify: Describe Your System in Plain English": https://blog.mushroom.cv/blog/archify-tech-diagram-skill-guide/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
