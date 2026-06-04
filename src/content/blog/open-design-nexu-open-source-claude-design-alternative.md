---
title: "Open Design：58K star 开源设计工具，对比 Claude Code 设计能力的深度分析"
titleEn: "Open Design: 58K-Star Open-Source Claude Design Alternative — Deep Comparison with Claude Code for Design"
description: "nexu-io/open-design 是 Claude Design 的开源替代：本地优先原生桌面应用，259+ Skills、150+ DESIGN.md 设计系统、261 插件，支持 21 种 AI 代理 CLI 包括 Claude Code。本文深度对比 Open Design 与 Claude Code 原生设计能力的优缺点，并给出选型建议。"
descriptionEn: "nexu-io/open-design is the open-source alternative to Claude Design: local-first native desktop app, 259+ skills, 150+ DESIGN.md design systems, 261 plugins, and 21 AI agent CLIs including Claude Code. This article deeply compares Open Design with Claude Code's native design capabilities."
pubDate: 2026-06-04
category: "Tech-News"
tags: ["Open Design", "Claude Code", "AI设计", "开源工具", "Design System", "Claude Design", "多模态", "Agent"]
heroImage: "../../assets/images/open-design-nexu-banner.png"
lang: "zh-CN"
---

## 背景：Claude Design 的出现与反应

2026 年 4 月，Anthropic 发布了 **Claude Design**——让 LLM 从"写文字"变成"直接交付设计产物"的第一次重大尝试：输入一段 brief，直接得到可用的 web 原型或 UI artifact。它迅速病毒式传播。

但随之而来的批评也很快聚焦：闭源、付费、云端、只能用 Anthropic 模型、技能和设计系统不可定制。

一个月后，**nexu-io/open-design** 出现了——用同样的"agent 驱动设计产物"范式，但把它拆成了开放的文件系统：Skills + Design Systems + Plugins，任何已经在你 PATH 里的 coding agent 都能读、写、混用。截至 2026 年 6 月，这个仓库已有 **58,603 stars**、6,612 forks，成为今年增长最快的开源项目之一。

## Open Design 是什么

Open Design（OD）本质上是一个**设计工作流编排层**，它不自带 agent，而是把你已有的 agent 变成"设计引擎"：

```
brief（简报）
  → Plugin 选择输出类型（原型/幻灯片/看板/图像/视频）
  → Skill 注入设计经验（布局规则/交互模式/组件约定）
  → DESIGN.md 约束品牌（色板/字体/间距/动效/反模式）
  → Agent 流式生成 <artifact>
  → 沙箱 iframe 预览
  → 导出 HTML/PDF/PPTX/MP4
```

核心用 TypeScript 编写，Apache 2.0 协议，2026 年 4 月 28 日首次发布，当前版本 **v0.9.0**。

### 三层可组合架构

| 层 | 载体 | 数量 | 作用 |
|----|------|------|------|
| **Plugins** | 可运行的工作流 | 261 | 定义输出类型和生成流程 |
| **Skills** | SKILL.md 指令文件 | 259+ | 给 agent 注入设计经验和规则 |
| **Design Systems** | DESIGN.md 品牌合约 | 150+ | 约束颜色、字体、间距、动效 |

三者都是纯文件，任何人可以编写、版本控制、发布。

### DESIGN.md：品牌合约文件

这是 Open Design 最重要的创新之一。一个 `DESIGN.md` 覆盖 9 个维度：

1. 色板（主色、辅色、语义色）
2. 字体系统（字族、字阶、行高）
3. 间距网格
4. 动效规范（缓动曲线、持续时间）
5. 声音/语气（文案风格）
6. 组件约定
7. 图标系统
8. 图像风格
9. **反模式**（明确列出什么不能做）

仓库内已预置 **150 个品牌设计系统**，包括：Linear、Stripe、Vercel、Airbnb、Apple、Tesla、Notion、Anthropic、Cursor、Supabase、Figma……直接选用，也可以把截图/URL 扔给 agent 让它生成。

### 支持的 AI Agent（21 种 CLI）

任何支持 MCP 的 coding agent 都可以通过 `od mcp install <agent>` 接入：

Claude Code、Codex、Cursor、VS Code Copilot、Gemini CLI、OpenCode、OpenClaw、Antigravity、Cline、Trae、Kimi、Pi Agent、Mistral Vibe、Hermes、DeepSeek、Aider 等。

**一行接入 Claude Code：**
```bash
od mcp install claude
# 或
curl -fsSL https://open-design.ai/install.sh | sh -s claude
```

之后在 Claude Code 里：
```
> Use open-design to generate a landing page with the Linear design system
```

### 输出产物类型

| 类型 | 格式 | 说明 |
|------|------|------|
| **Prototype** | HTML | Web/移动/桌面原型，沙箱 iframe，可即时预览 |
| **HyperFrame** | MP4 | HTML+CSS+GSAP → 无头 Chrome → FFmpeg 渲染 |
| **Deck** | PPTX/PDF/HTML | 幻灯片，15 种模板 36 种主题 |
| **Image** | PNG | gpt-image-2、ImageRouter 生成，93 个提示模板 |
| **Dashboard** | HTML | 带调参面板的实时看板，数据驱动 |

### 快速启动

**桌面应用（最简方式）：**
macOS (Apple Silicon / Intel) 和 Windows (x64) 原生安装包，直接下载即用，无需 Node/pnpm。

**Docker：**
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design/deploy && cp .env.example .env
echo "OD_API_TOKEN=$(openssl rand -hex 32)" >> .env
docker compose up -d
# 访问 http://localhost:7456
```

**从源码运行：**
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design && corepack enable && pnpm install && pnpm tools-dev run web
```

---

## 与 Claude Code 的深度对比

这里的"Claude Code"指的是直接用 Claude Code CLI 进行设计类工作——不借助 Open Design，纯靠对话生成 HTML/CSS/React 组件。

### 核心能力矩阵

| 维度 | **Claude Code（原生）** | **Open Design + Claude Code** |
|------|------------------------|-------------------------------|
| 设计系统约束 | ❌ 无内置框架，靠提示词描述 | ✅ DESIGN.md 结构化品牌合约，150+ 预置 |
| 输出预览 | ❌ 需手动在浏览器打开 | ✅ 沙箱 iframe 实时渲染 |
| 多格式导出 | ❌ 只有代码文件 | ✅ HTML/PDF/PPTX/MP4/ZIP |
| 视频生成 | ❌ | ✅ HyperFrames（HTML→MP4） |
| 工作流自动化 | ⚠️ 依赖手写脚本 | ✅ Automation 页面，可调度重复任务 |
| 品牌一致性 | ⚠️ 随提示词变化 | ✅ DESIGN.md 在每次渲染时绑定 |
| 设备帧（iPhone/MacBook） | ❌ | ✅ 预置共享设备帧，agent 不重复绘制 |
| 与开发工作流集成 | ✅ 原生，在代码库中操作 | ⚠️ 需要 MCP 桥接 |
| 硬件依赖 | ✅ 任意终端即用 | ⚠️ 桌面应用，本地 SQLite 存储 |
| 学习成本 | ✅ 熟悉的对话界面 | ⚠️ 需理解 Skills/Plugins/DESIGN.md 体系 |
| 许可 & 费用 | 取决于 API 计划 | ✅ BYOK + Apache 2.0，可自托管 |

### Claude Code 用于设计的优势

**1. 零摩擦集成代码库**
Claude Code 的核心强项：它在你的 git 仓库里工作。设计改动可以直接提交、code review、CI 测试。没有"从设计工具导出再导入代码库"这个摩擦点。

**2. 设计与逻辑同时进行**
开发者可以在同一个对话里说"帮我设计这个 modal 并实现数据绑定逻辑"，Claude Code 理解上下文，不需要在工具之间切换。

**3. 全局上下文理解**
Claude Code 读取了整个代码库后，知道现有组件库的结构、命名约定、状态管理模式，生成的 UI 可以直接复用已有逻辑。

**4. 无额外基础设施**
没有 Docker 容器、没有 MCP 服务器、没有本地守护进程——就是 CLI + API key。

### Claude Code 用于设计的局限

**1. 品牌一致性靠"记忆"而非"约束"**
每次对话都需要重新描述品牌规范（"用 Airbnb 的珊瑚色、圆角 UI……"）。Claude Code 没有结构化的设计系统绑定机制，长期项目容易漂移。

**2. 无法直接生成视频/动效**
生成的是代码，MP4 渲染链（headless Chrome + FFmpeg）需要额外配置。

**3. 没有可视化设计画廊**
生成的 HTML 文件分散在文件系统里，没有统一的"项目 → 产物"管理界面。

**4. 每次从零开始**
没有方向挑选（wireframe vs high-fidelity）、没有插件选择页面的工作流引导，设计类任务的输入结构需要用户自己组织。

### Open Design 的优势

**1. DESIGN.md 是真正的"品牌契约"**
这是 Open Design 最有价值的发明。把设计规范从"写在提示词里的模糊描述"变成结构化的可版本控制文件。团队的设计一致性有了文件层面的保障，而不是依赖 agent 的"记忆"。

**2. 三层可组合性**
Skills（经验） + Plugins（流程） + DESIGN.md（品牌）三个维度独立演进，任意组合。一个 Airbnb 设计系统可以搭配移动端 skill，也可以搭配幻灯片 plugin。

**3. HyperFrames 视频生成**
HTML+CSS+GSAP → headless Chrome → FFmpeg → MP4，这是一个完整的确定性视频渲染管线，目前在开源工具里没有同类。对内容创作和营销团队很有价值。

**4. 21 个 agent CLI 的真正无绑定**
不锁定 Anthropic，不锁定任何模型。同一套设计系统，可以用 Claude Code 今天生成，明天换 Codex，后天换本地 Qwen 模型。

**5. 自托管 + Apache 2.0**
医疗、法律、金融等隐私敏感场景：设计资产全部留在本地网络，无需担心云端数据泄露。

### Open Design 的局限与风险

**1. 不是真正的 Figma 替代**
Open Design 生成的是"单页 HTML artifact"，不是 Figma 组件库。没有矢量编辑、没有实时协作（多人同时在画板上操作）、没有设计 → 开发的 Inspect 工作流。把它和 Figma 并排比较有误导性。

**2. 输出质量依赖 agent 能力**
DESIGN.md 是约束层，但最终生成质量取决于底层 agent。用弱模型配强设计系统，输出一样差。

**3. 复杂度税**
259 个 Skills、261 个插件、150 个设计系统——对于想"快速生成一个登录页"的开发者来说，这是信息过载。Claude Code 直接对话反而更快。

**4. 维护 21 个 CLI 适配层**
每个 agent CLI 都有自己的 MCP 协议细节，维护成本随 CLI 数量线性增长。社区贡献者能跟上所有 CLI 更新的速度存疑。

**5. 尚处早期（v0.9.0）**
Windows 有已知问题，Docker 在 macOS 有网络配置陷阱，Linux 支持在"可选发布通道"。生产级别自托管需要踩坑。

---

## 我的观点和见解

### 1. DESIGN.md 是这个项目最值得关注的创新

Anthropic 用 CLAUDE.md 给 agent 传递项目上下文，Open Design 用 DESIGN.md 给 agent 传递品牌上下文——这个迁移非常自然，也非常有价值。

如果 DESIGN.md 格式被更多工具采用（就像 `.editorconfig` 或 `package.json` 一样），它可能成为"品牌合约文件"的事实标准。届时，设计师只需维护一份 `DESIGN.md`，所有 agent（不管是 Claude、Cursor 还是 Gemini）都能读它、遵守它。

### 2. Open Design 和 Claude Code 是互补关系，不是竞争关系

Open Design 的最佳使用场景：**产品/设计师主导的工作流，产出是独立的 UI 产物**（原型展示、营销页、幻灯片、视频）。

Claude Code 的最佳使用场景：**工程师主导的工作流，产出直接进入代码库**。

两者的理想组合：用 Open Design 快速生成视觉原型给产品/客户看，确认方向后，把 HTML artifact 拖进 Claude Code 转成可运行的 React 组件。

### 3. 对 Anthropic 的挑战信号

58K stars 的速度（不到两个月）说明 Claude Design 的封闭路线制造了真实的市场需求。Open Design 的 Fellows 计划和社区生态表明它在押注"设计工具的下一层应该是开放的"。

如果 Anthropic 不开放 Claude Design 的 Skill/Plugin 生态，类似 Open Design 这样的开源替代会持续分流开发者社区的关注度。这是 VS Code vs JetBrains 之争的一个设计领域变体。

### 4. 最适合谁

| 场景 | 推荐 |
|------|------|
| 开发者想快速为现有项目加 UI | ✅ Claude Code 原生 |
| 设计师/PM 想生成原型给客户演示 | ✅ Open Design |
| 营销团队需要批量生成品牌素材 | ✅ Open Design（Automation + DESIGN.md） |
| 对数据隐私有强要求的团队 | ✅ Open Design 自托管 |
| 需要 HTML→MP4 视频 | ✅ Open Design HyperFrames |
| 小团队快速验证想法，不想学新工具 | ✅ Claude Code 直接对话 |

---

**资源链接：**
- GitHub：[nexu-io/open-design](https://github.com/nexu-io/open-design)（58K+ stars）
- 官网 & 下载：[open-design.ai](https://open-design.ai)
- Discord：[discord.gg/qhbcCH8Am4](https://discord.gg/qhbcCH8Am4)
- 版本 0.9.0 发布：[GitHub Releases](https://github.com/nexu-io/open-design/releases)

<!--EN-->

## Background: Claude Design and the Response

In April 2026, Anthropic launched **Claude Design** — the first time an LLM stopped generating prose and started delivering design artifacts directly: type a brief, get a usable web prototype or UI artifact. It went viral instantly.

But criticism quickly converged: closed-source, paid-only, cloud-only, locked to Anthropic's model, non-customizable skills and design systems.

One month later, **nexu-io/open-design** appeared — the same "agent-driven design artifact" paradigm, but broken into an open filesystem: Skills + Design Systems + Plugins, consumable by any coding agent already on your PATH. As of June 2026, the repo has **58,603 stars** and 6,612 forks, making it one of the fastest-growing open-source projects of the year.

## What Is Open Design

Open Design (OD) is a **design workflow orchestration layer**. It doesn't ship its own agent — it turns the agent you already have into a design engine:

```
brief
  → Plugin (selects output type: prototype / deck / dashboard / image / video)
  → Skill (injects design expertise: layout rules, interaction patterns, component conventions)
  → DESIGN.md (constrains brand: palette, fonts, spacing, motion, anti-patterns)
  → Agent streams <artifact>
  → Sandboxed iframe preview
  → Export HTML / PDF / PPTX / MP4
```

Core written in TypeScript, Apache 2.0 license, first released April 28, 2026, current version **v0.9.0**.

### The Three-Layer Composable Architecture

| Layer | File Format | Count | Purpose |
|-------|-------------|-------|---------|
| **Plugins** | Runnable workflows | 261 | Define output type and generation pipeline |
| **Skills** | SKILL.md instruction files | 259+ | Inject design expertise and rules into the agent |
| **Design Systems** | DESIGN.md brand contracts | 150+ | Constrain color, typography, spacing, motion |

All three are plain files — anyone can author, version, and publish them.

### DESIGN.md: The Brand Contract File

This is Open Design's most important innovation. A `DESIGN.md` covers 9 dimensions: palette, type system, spacing grid, motion spec (easing curves, durations), voice/tone, component conventions, icon system, image style, and **anti-patterns** (explicitly what never to do).

The repo ships **150 pre-built design systems** including Linear, Stripe, Vercel, Airbnb, Apple, Tesla, Notion, Anthropic, Cursor, Supabase, Figma, and more.

### 21 Agent CLIs Supported

Claude Code, Codex, Cursor, VS Code Copilot, Gemini CLI, OpenCode, OpenClaw, Antigravity, Cline, Trae, Kimi, Pi Agent, Mistral Vibe, Hermes, DeepSeek, Aider, and more — all via `od mcp install <agent>`.

**Connect Claude Code:**
```bash
od mcp install claude
```

Then inside Claude Code:
```
> Use open-design to generate a landing page with the Linear design system
```

## Deep Comparison: Open Design vs Claude Code for Design

"Claude Code for design" here means using Claude Code CLI natively — pure conversation to generate HTML/CSS/React — without Open Design.

### Capability Matrix

| Dimension | **Claude Code (native)** | **Open Design + Claude Code** |
|-----------|--------------------------|-------------------------------|
| Design system constraint | ❌ No framework; describe in prompts | ✅ DESIGN.md structured contract, 150+ prebuilt |
| Output preview | ❌ Manually open in browser | ✅ Sandboxed iframe, live render |
| Multi-format export | ❌ Source files only | ✅ HTML/PDF/PPTX/MP4/ZIP |
| Video generation | ❌ | ✅ HyperFrames (HTML→MP4) |
| Workflow automation | ⚠️ Custom scripts | ✅ Automation page, schedulable |
| Brand consistency | ⚠️ Drifts with prompt wording | ✅ DESIGN.md bound at every render |
| Device frames | ❌ | ✅ Shared pre-built frames (iPhone, MacBook, etc.) |
| Dev workflow integration | ✅ Native, operates in repo | ⚠️ MCP bridge required |
| Learning curve | ✅ Familiar chat interface | ⚠️ Skills/Plugins/DESIGN.md to learn |

### Where Claude Code Wins for Design

**Zero-friction repo integration.** Claude Code works directly in your git repo. Design changes are committed, code-reviewed, CI-tested — no "export from design tool, re-import into codebase" friction.

**Simultaneous design + logic.** Ask "design this modal and wire up the data binding" in one message — Claude Code understands the full codebase context.

**No extra infrastructure.** No Docker container, no MCP server, no local daemon — just a CLI and an API key.

### Where Claude Code Falls Short for Design

**Brand consistency relies on "memory," not constraints.** Each conversation requires re-describing brand specs. No structured design system binding means long projects drift.

**No video/motion generation pipeline.** Generating the code is one thing; rendering it to MP4 via headless Chrome + FFmpeg requires separate setup.

**No visual artifact gallery.** Generated HTML files scatter across the filesystem with no unified project → artifact management UI.

## My Perspective and Insights

### 1. DESIGN.md is the most notable innovation here

Anthropic uses `CLAUDE.md` to pass project context to agents; Open Design uses `DESIGN.md` to pass brand context. The migration is natural and extremely valuable.

If the DESIGN.md format gets adopted by more tools — like `.editorconfig` or `package.json` — it could become the de facto standard for "brand contract files." Designers maintain one `DESIGN.md`; every agent (Claude, Cursor, Gemini) reads it and obeys it.

### 2. Open Design and Claude Code are complementary, not competitive

**Open Design's sweet spot:** product/designer-led workflows producing standalone UI artifacts (prototype demos, marketing pages, decks, videos).

**Claude Code's sweet spot:** engineer-led workflows where output goes directly into the codebase.

**Ideal combination:** Use Open Design to quickly generate visual prototypes for product/client sign-off; then hand the HTML artifact to Claude Code to turn into runnable React components.

### 3. Three real limitations to watch

**Not a real Figma replacement.** Open Design generates single-page HTML artifacts, not Figma component libraries. No vector editing, no real-time multi-user collaboration, no design-to-dev Inspect workflow. The Figma comparison is misleading.

**Output quality depends on the agent.** DESIGN.md is a constraint layer, but final quality depends on the underlying model. Strong design system + weak model = weak output.

**Complexity tax.** 259 Skills, 261 plugins, 150 design systems — for a developer who wants to "quickly generate a login page," this is information overload. Direct Claude Code conversation is often faster.

### 4. Who Should Use What

| Scenario | Recommendation |
|----------|---------------|
| Developer adding UI to an existing codebase | ✅ Claude Code native |
| Designer/PM generating prototypes for client demos | ✅ Open Design |
| Marketing team generating brand assets at scale | ✅ Open Design (Automation + DESIGN.md) |
| Privacy-sensitive teams requiring data sovereignty | ✅ Open Design self-hosted |
| HTML → MP4 video generation | ✅ Open Design HyperFrames |
| Small team testing ideas without learning new tools | ✅ Claude Code direct conversation |

---

**Resources:**
- GitHub: [nexu-io/open-design](https://github.com/nexu-io/open-design) (58K+ stars)
- Website & Download: [open-design.ai](https://open-design.ai)
- Discord: [discord.gg/qhbcCH8Am4](https://discord.gg/qhbcCH8Am4)
