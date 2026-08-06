---
title: "Agent Plugins 规范深度解析：一次构建，Codex / ChatGPT / Cursor / Copilot / VS Code / Kiro 全通"
titleEn: "agent-plugins-openai-codex-multi-client-open-spec-analysis"
description: "OpenAI 联合 AWS、Cursor、GitHub、Microsoft、Vercel 发布 Agent Plugins 规范：Skills + Connectors + MCP 三层架构，180 个官方插件已在 marketplace，一份 plugin.json 对接六大客户端。本文深度拆解规范结构，并分析这个开放标准在未来 Agent 分发战争中打开的真实机会窗口。"
descriptionEn: "OpenAI + AWS + Cursor + GitHub + Microsoft + Vercel jointly released the Agent Plugins spec: a three-layer architecture of Skills, Connectors, and MCP servers. One plugin.json deploys across Codex, ChatGPT, Cursor, Copilot, VS Code, and Kiro. This analysis covers the spec structure, the 180-plugin ecosystem, and the strategic opportunity window this open standard creates."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Research"
tags: ["Agent Plugins", "OpenAI", "MCP", "Claude Code", "Codex", "开放规范", "AI生态", "Mycelium"]
heroImage: "../../assets/images/agent-plugins-openai-codex-multi-client-open-spec-analysis-banner.jpg"
---

*by Mycelium Protocol*

---

2023 年 ChatGPT Plugins 是 OpenAI 的第一次插件实验，生命周期不到一年就被废弃了。那次失败的核心原因不是没有需求，而是**只有一个客户端**，生态起不来。

2026 年 Agent Plugins 的起点完全不同：发布当天就有六个主流 Agent 客户端同步支持，背后是 OpenAI + AWS + Cursor + GitHub + Microsoft + Vercel 的联合背书。这不是一家公司的产品发布，而是一份行业规范的落地。

---

## 规范结构：一份清单管六端

Agent Plugins 的核心是仓库根目录下的 `.codex-plugin/plugin.json`，这是唯一的入口文件。

```json
{
  "name": "figma",
  "version": "2.0.13",
  "skills": "./skills/",
  "apps": "./.app.json",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Figma",
    "shortDescription": "Inspect Figma designs and turn them into code",
    "category": "Creativity",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["Inspect a Figma design and implement it in code"],
    "brandColor": "#1E1E1E",
    "composerIcon": "./assets/composer-icon.svg",
    "logo": "./assets/logo.svg"
  }
}
```

`interface` 字段控制插件在目录里的展示；三个核心字段 `skills`、`apps`（即 connectors）、`mcpServers` 分别对应三层能力，全部可选——一个插件可以只有 skills，也可以三层全用。

---

## 六个组件：规范完整覆盖的能力边界

官方文档定义的插件可以包含以下六类内容：

**1. Skills** — 可复用的 Markdown 指令文件，告诉 Agent 如何完成特定类型的任务、应该遵循哪些步骤和引用哪些资源。门槛最低，纯文本，无服务器。

**2. Connectors** — 连接到 GitHub、Slack、Google Drive 等外部工具的接口，让 Agent 可以读取数据、执行操作。Connectors 背后是 MCP 服务器，可以包含自定义 UI。

**3. MCP Servers** — 提供工具访问、共享信息和外部系统集成的后端服务，负责定义工具、处理认证、返回结构化数据、对外部系统执行操作。

**4. Browser Extensions** — 插件工作流所需的浏览器能力，用于需要访问浏览器上下文的场景。

**5. Hooks** — 在配置的生命周期节点运行的命令（如安装后、会话开始时）。官方特别提示：使用前要检查并信任 hooks。

**6. Scheduled Task Templates** — 可复用的定期任务起点，在支持计划任务的环境中使用。

---

## 三层能力架构

把六个组件压缩到实际使用的逻辑层次上，是三层：

```
Skills 层（行为）
  └─ Markdown 指令文件，控制 Agent 在任务中的决策逻辑
  
Connectors / Apps 层（界面 + 认证）
  └─ 外部服务连接 + 可选自定义 UI，Auth 由服务自身控制
  
MCP Servers 层（工具 + 数据）
  └─ 结构化数据访问，工具定义，外部系统操作
```

Skills 层是免费的、无服务器的，任何人都可以发布。Connectors + MCP 层需要运行服务器，有认证成本，但可以触达更深的能力。

---

## 联盟的含义：这次不是一家公司说了算

历史上每次插件/扩展规范的失败，原因都是同一个：**只有一个客户端愿意采纳**。VS Code 插件只跑在 VS Code，Chrome 扩展只在 Chromium 系上，2023 年 ChatGPT Plugins 只有 ChatGPT 本身。

Agent Plugins 的启动阵容是：

| 客户端 | 背后的公司 |
|--------|-----------|
| Codex | OpenAI |
| ChatGPT | OpenAI |
| Cursor | Anysphere |
| GitHub Copilot | Microsoft / GitHub |
| VS Code | Microsoft |
| Kiro | Amazon / AWS |

六个工具，四家公司，覆盖了目前 AI 编程工具市场的大多数席位。这意味着：一个插件发布到 marketplace，天然可以被百万量级的开发者看到，不需要为每个平台单独适配。

**「Sign in with ChatGPT」**是另一个值得注意的信号。OpenAI 正在把身份层做进来——Airtable、GitLab、HubSpot、Notion、Supabase、Vercel 已经支持这个 OAuth 流程。这是在构建「AI 时代的 Sign in with Google」。

---

## 180 个插件的生态现状

官方 marketplace（`.agents/plugins/marketplace.json`）目前收录 180 个插件，第三方可以自行提交。已覆盖的类别：

- **开发工具**：Linear、Figma、Sentry、Datadog、Replit、Lovable、Wix、Airtable、Supabase、Cloudflare
- **协作**：Slack、Notion、Teams、Google Drive、Zoom、DocuSign
- **销售 / 营销**：HubSpot、Apollo、Clay、Outreach、Stripe
- **代码**：GitHub、Vercel

其中 Expo 是一个典型案例：Expo 团队**自己**把 Expo 插件发布进 marketplace，而不是 OpenAI 代劳。这证明第三方发布路径真实可用，不只是宣传口号。

API 用户（用 API key 登录而非账户登录）可以访问 OpenAI 策划的子集，但部分需要 OAuth 的插件不可用——这是一个有意识的权限分层，不是 bug。

---

## 与 MCP、Skills 的关系

这三个规范在时间线上依次出现，功能上互相嵌套：

```
MCP（Model Context Protocol，2024）
  └─ 定义了工具调用的传输协议
  
Skills（2025）
  └─ 定义了指令文件的格式和加载方式
  
Agent Plugins（2026）
  └─ 用 plugin.json 把 Skills + MCP 打包成一个可安装、可发现、可分发的单元
```

Agent Plugins 不是要替代 MCP 或 Skills，而是给它们加了一层**发现和分发层**。一个 MCP 服务器在没有插件包装的情况下，只能手动配置；包成插件后，可以一键安装到所有支持的客户端。

这个层次关系很重要：**MCP 是水管，Skills 是指令手册，Plugins 是把水管和手册装进一个盒子卖到商店里**。

---

## 未来方向与机会

### 1. 这是 Agent 时代的 App Store 时刻

2008 年 App Store 开放，不是因为 Apple 发明了新的技术原语，而是因为它建立了一个**标准化的发现和分发层**。开发者不再需要自建分发渠道，用户不再需要手动安装 APK。

Agent Plugins 在做同一件事。区别是：这次的「App Store」不属于一家公司，是多家公司共同支持的开放规范。这意味着不会出现单一的审查方，但也意味着生态碎片化的风险仍然存在。

**对开发者的机会**：如果你在做一个面向开发者的工具，现在是建立插件发现优势的窗口期。180 个插件听起来很多，但和 App Store 的 200 万相比，这个生态还几乎是空的。

### 2. Skills 层是门槛最低的进入点

一个 Skills-only 的插件只需要：
- 一个 GitHub 仓库
- 一个 `.codex-plugin/plugin.json`
- 一个或多个 `.md` 指令文件

没有服务器，没有 API，没有 OAuth。任何人都可以今天开始写，明天发布到 marketplace。

这和 2008 年的 iOS 不同——当时需要 Mac、Xcode、开发者证书、$99/年。Skills 层的进入成本接近于零，这意味着接下来几个月会看到大量 Skills-only 插件的爆发。

**对内容创作者的机会**：Skills 本质上是「结构化的 prompt 集合」。任何在某个垂直领域积累了深度 prompt 经验的人——医疗、法律、财务建模、游戏设计——都可以把这些经验封装成插件，在六个平台上获得分发。

### 3. MCP 服务器变成 AI-native SaaS 的标准后端

在 Plugins 规范之前，MCP 服务器是配置繁琐的基础设施，需要用户手动在每个客户端里填写服务器地址和凭证。

Plugins 规范之后，MCP 服务器可以通过插件一键安装，认证通过 Connectors 统一处理，UI 可以嵌入进客户端界面。**这事实上定义了 AI-native SaaS 产品的技术栈**：你的产品不是一个网页，而是一个 Connector + MCP Server 组合的插件。

**对 SaaS 创业者的机会**：传统 SaaS 需要用户打开浏览器、登录网页、手动操作。AI-native 版本是：用户在 Cursor 里用自然语言说「帮我更新 CRM 里这个客户的状态」，插件的 Connector + MCP 层完成操作，用户不离开编辑器。Linear、Notion、HubSpot 已经在这个方向上布局了。

### 4. Hooks 是下一个安全战场

Hooks 是规范里最被低估、也最危险的能力。一个插件如果在安装时、会话开始时触发 hooks，可以在用户不知情的情况下执行任意命令。

官方文档只说「Review and trust plugin hooks before you enable them」，但没有给出任何沙箱或权限限制的细节。

这意味着：
- **对安全研究者**：Hooks 是未来 12 个月内最值得关注的攻击面
- **对企业用户**：在 Hooks 的审计机制更完善之前，谨慎在生产环境安装来源不明的插件
- **对规范制定者**：Hooks 需要一个类似 Android 权限模型的声明和用户确认机制

### 5. 谁控制 Marketplace 曲率，谁控制 Agent 的注意力

180 个插件的 marketplace 目前由 OpenAI 策划，但规范允许「repo marketplace」——任何组织可以建立自己的私有或团队 marketplace。

这创造了一个有趣的博弈格局：
- OpenAI 有动机保持官方 marketplace 的高质量和高曝光
- 企业有动机建立内部私有 marketplace，控制员工 Agent 的工具权限
- 开源社区有动机建立去中心化的策展列表

**对平台创业者的机会**：企业级插件 marketplace 管理工具还不存在。谁先做出「企业 Plugins 策略管理 + 安全审计 + 使用分析」，就在这个领域占到先机。

### 6. 「一次构建」承诺的边界

规范说「一次构建，多端运行」，但实际上有细节限制：
- Browser Extensions 部分依赖具体客户端的实现
- API key 用户无法访问需要 OAuth 的插件
- Scheduled Task Templates 只在「支持计划任务的环境中」有效
- 部分 Connectors 仅对 ChatGPT Work 用户可用（非 Chat 模式）

**真实的「一次构建」只在 Skills + MCP 层成立**。越往上走（Connectors、Browser Extensions、Hooks），平台差异越大。这是规范成熟度的问题，预计未来版本会逐步收敛。

---

## 现在应该做什么

**如果你是开发工具 / 垂直 SaaS 创业者**：
立刻检查自己的产品能不能封装成一个 Skills-only 插件。门槛极低，分发价值高。下一步考虑 MCP Server，把核心操作暴露出来。

**如果你是 prompt 工程师 / AI 工作流专家**：
Skills 层是你的机会。把你在某个垂直领域积累的经验结构化成插件，发布到 marketplace。现在的竞争密度和 2008 年 App Store 早期差不多。

**如果你在做企业 IT / 安全**：
建立 Hooks 审计流程，在公司允许安装的插件列表上设置白名单。Plugins 规范的安全模型目前还不完整。

**如果你只是一个开发者用户**：
试着在 Codex 或 ChatGPT Work 里安装几个 marketplace 插件感受一下体验，特别是 Linear 和 Figma 这种深度集成的。这是未来 AI 工具集成的默认形态。

---

## 这次和 2023 年哪里不同

2023 年 ChatGPT Plugins 失败的尸检结论只有一条：**没有客户端飞轮**。OpenAI 是唯一的分发渠道，开发者和用户都没有足够的动机投入。

2026 年的 Agent Plugins：
- 六个客户端同步支持，四家公司背书
- 规范是开放的，任何人可以实现兼容客户端
- Skills 层的发布门槛接近零
- 「Sign in with ChatGPT」在建立身份层

飞轮的启动条件已经成立。接下来的问题是**谁先跑到位置上**。

---

规范文档：[developers.openai.com/plugins](https://developers.openai.com/plugins)  
用户文档：[learn.chatgpt.com/docs/plugins](https://learn.chatgpt.com/docs/plugins)  
官方 Plugin 仓库：[github.com/openai/plugins](https://github.com/openai/plugins)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Agent Plugins: One Spec, Six Clients — and What the Real Opportunity Is

*by Mycelium Protocol*

---

In 2023, OpenAI launched ChatGPT Plugins. They were shut down less than a year later. The failure wasn't lack of demand — it was lack of client diversity. OpenAI controlled the only distribution channel.

In 2026, Agent Plugins launches with six clients on day one: Codex, ChatGPT, Cursor, GitHub Copilot, VS Code, and Kiro — four companies, one shared spec. This is not a product launch. It's a standards ratification.

---

### Spec Structure: One Manifest, Six Clients

The entry point is `.codex-plugin/plugin.json` in the repository root.

```json
{
  "name": "figma",
  "version": "2.0.13",
  "skills": "./skills/",
  "apps": "./.app.json",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Figma",
    "category": "Creativity",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["Inspect a Figma design and implement it in code"]
  }
}
```

The three core fields — `skills`, `apps` (connectors), and `mcpServers` — are all optional. A plugin can be skills-only, MCP-only, or use all three layers.

---

### Six Plugin Components

An Agent Plugin can contain any combination of:

**Skills** — Markdown instruction files that tell the agent how to do specific kinds of work, which steps to follow, which references to use. No server. No API. Just text.

**Connectors** — Connections to external services like GitHub, Slack, or Google Drive. Backed by MCP servers. Can include custom UI rendered inside the client.

**MCP Servers** — Backend services that provide tool access and structured data. Defines tools, enforces auth, returns structured output, performs actions against external systems.

**Browser Extensions** — Browser capabilities a plugin workflow needs.

**Hooks** — Commands that run at configured lifecycle points. The docs explicitly say: "Review and trust plugin hooks before you enable them."

**Scheduled Task Templates** — Reusable starting points for recurring agent tasks.

---

### Three Layers in Practice

Collapse those six into the three layers that actually matter:

```
Skills layer (behavior)
  └─ Markdown instructions controlling how the agent thinks through a task

Connectors / Apps layer (UI + auth)
  └─ External service connection + optional custom UI, auth handled by the service

MCP Servers layer (tools + data)
  └─ Structured data access, tool definitions, external system actions
```

Skills is free, serverless, zero-infrastructure. Connectors + MCP requires running a server but unlocks deeper integration.

---

### The Coalition: Why This Time Is Different

Every plugin spec that failed before had the same cause: one client. VS Code extensions only ran in VS Code. 2023 ChatGPT Plugins only ran in ChatGPT.

Agent Plugins day-one coalition:

| Client | Company |
|--------|---------|
| Codex | OpenAI |
| ChatGPT | OpenAI |
| Cursor | Anysphere |
| GitHub Copilot | Microsoft / GitHub |
| VS Code | Microsoft |
| Kiro | Amazon / AWS |

Six clients, four companies, most of the AI coding market covered. A plugin published to the marketplace is immediately visible to millions of developers without any per-platform porting.

**Sign in with ChatGPT** is the additional signal. Airtable, GitLab, HubSpot, Notion, Supabase, and Vercel already support this OAuth flow. OpenAI is building toward "Sign in with ChatGPT" as an identity layer — the AI-era "Sign in with Google."

---

### The 180-Plugin Ecosystem

The official marketplace already has 180 plugins: Linear, Figma, Sentry, Datadog, Replit, Slack, Notion, Teams, Google Drive, Zoom, DocuSign, HubSpot, Apollo, Clay, Stripe, Vercel, GitHub, Cloudflare, Airtable, Supabase, and more.

The Expo plugin is the key proof: Expo's team published their own plugin to the marketplace themselves. Third-party publishing works. It's not just a promotional claim.

---

### Relationship to MCP and Skills

These three specs arrived in order, and they nest:

```
MCP (2024)
  └─ Defines the transport protocol for tool calls

Skills (2025)
  └─ Defines the format for instruction files

Agent Plugins (2026)
  └─ Wraps Skills + MCP into an installable, discoverable, distributable unit
```

Plugins don't replace MCP or Skills. They add a **discovery and distribution layer** on top. An MCP server without a plugin wrapper requires manual configuration by each user in each client. Wrapped in a plugin, it installs with one click across all six clients.

MCP is the plumbing. Skills is the instruction manual. Plugins is the box that packages both and puts them on a shelf.

---

### The Real Opportunity

**1. This is the App Store moment for AI-native tooling**

App Store 2008 wasn't a new technology primitive — it was a standardized discovery and distribution layer. Developers stopped needing custom distribution channels. Users stopped manually sideloading.

Agent Plugins does the same thing. The difference: this "App Store" is not owned by one company. It's an open spec with multiple stores. That removes single-gatekeeper risk, but also means ecosystem fragmentation remains possible.

For developers: 180 plugins sound like a lot, but against the context of 2 million App Store apps, the AI plugin ecosystem is almost empty. The early-mover window is open right now.

**2. Skills layer has nearly zero barrier to entry**

A skills-only plugin needs:
- A GitHub repository
- `.codex-plugin/plugin.json`
- One or more `.md` instruction files

No server. No API. No OAuth. No subscription. Anyone can publish today.

This is fundamentally different from iOS in 2008, which required a Mac, Xcode, a developer certificate, and $99/year. Skills-layer plugins have near-zero entry cost — expect an explosion of them in the next few months.

For prompt engineers and AI workflow specialists: Skills is your layer. Domain expertise in medicine, law, financial modeling, game design, or any vertical can be packaged as a plugin and distributed across six platforms.

**3. MCP servers become the standard backend for AI-native SaaS**

Before Plugins, MCP servers required users to manually configure each client with server addresses and credentials. After Plugins, an MCP server can be installed with one click, authentication handled via Connectors, UI embedded in the client.

This effectively defines the technical stack for AI-native SaaS: your product isn't a webpage, it's a Connector + MCP server combination delivered as a plugin. The user never leaves their editor.

Linear, Notion, and HubSpot are already there. The window to establish this position in other verticals is still open.

**4. Hooks are the next security frontier**

Hooks are the most underestimated — and most dangerous — capability in the spec. A plugin can execute arbitrary commands at lifecycle points (install, session start). The official docs only say "review and trust hooks before enabling." No sandboxing details. No permission model.

For security researchers: Hooks are the most interesting attack surface in AI tooling for the next 12 months.

For enterprise IT: establish an audit process and whitelist before deploying plugins to production environments. The security model is not mature yet.

For spec authors: Hooks need something analogous to Android's declared permission model with explicit user confirmation. This is the obvious next version of the spec.

**5. Marketplace curation is the new attention bottleneck**

180 plugins in one marketplace curated by OpenAI. The spec also allows "repo marketplaces" — any organization can run a private or team-scoped marketplace.

This creates a layered market:
- Official marketplace: high visibility, high curation bar, controlled by OpenAI
- Enterprise private marketplaces: IT-governed, security-audited, policy-controlled
- Community curated lists: open, decentralized, quality variable

The enterprise plugin management layer — governance, security scanning, usage analytics, policy enforcement — doesn't exist yet. The organization that builds it first will own the enterprise AI tooling ops space.

**6. "Write once, run everywhere" — the real limits**

The promise is multi-client deployment from one plugin. The actual boundary:
- Skills + MCP works uniformly across all six clients
- Browser Extensions depend on per-client implementation
- API key users can't access OAuth-dependent plugins
- Scheduled Task Templates only work where scheduled tasks are supported
- Some Connectors are ChatGPT Work-only (not available in Chat mode)

True "write once, run everywhere" holds for Skills and MCP layers. The higher up the stack you go — Connectors, Browser Extensions, Hooks — the more platform-specific details matter. This is a spec maturity issue; expect convergence in future versions.

---

### The Strategic Picture

2023 ChatGPT Plugins failed because there was no client flywheel. One distribution channel, one company's incentives.

2026 Agent Plugins:
- Six clients day one, four companies backing the spec
- Open spec — any client can implement compatibility
- Skills-layer publishing is nearly free
- Identity layer forming via "Sign in with ChatGPT"
- 180 plugins and growing

The flywheel conditions are in place. The remaining question is who moves into position first.

---

Spec docs: [developers.openai.com/plugins](https://developers.openai.com/plugins)  
User guide: [learn.chatgpt.com/docs/plugins](https://learn.chatgpt.com/docs/plugins)  
Official plugin repo: [github.com/openai/plugins](https://github.com/openai/plugins)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
