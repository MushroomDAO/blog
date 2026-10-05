---
title: "Avalon：把 Codex、Claude Code、Cline 组成一支会协作的小队"
titleEn: "Avalon: Organize Codex, Claude Code, and Cline Into a Collaborating Team"
description: "Daijunfan/Avalon，GPL v3，7 stars，JavaScript，当前版本 0.58.1。把 Codex、Claude Code、Cline、Pi 四种 Coding Agent 接入同一个 Core，提供三个视图：Company 看团队协作关系，Messages 群聊聊任务，Plan 排定时/重复/事件驱动任务。支持 Mac/Windows/Linux 桌面及 SSH 远程主机，Electron + 浏览器后端双模式，内置丰富 CLI/Core API 供 Agent 直接操作。三个官方插件：Cloud Hosts（SSH 管理）、MiniNotion（本地笔记）、Margin Reader（文档阅读）。权限体系：职位+授权双重控制，Secretary 居中协调，只有用户可任免。"
descriptionEn: "Daijunfan/Avalon, GPL v3, 7 stars, JavaScript, version 0.58.1. Connects Codex, Claude Code, Cline, and Pi into a single Core with three views: Company for team structure, Messages for group chat, Plan for scheduled/recurring/event-driven tasks. Supports Mac/Windows/Linux and SSH remote hosts; Electron desktop and browser-backend modes; a full CLI/Core API for Agent-native operations. Three official plugins: Cloud Hosts (SSH management), MiniNotion (local notes), Margin Reader (documents). Permissions: role + authorization, Secretary coordinates, only the user can appoint/dismiss."
pubDate: 2026-10-05
heroImage: "../../assets/images/avalon-cross-agent-collaboration-company-messages-plan-banner.jpg"
category: "Tech-Experiment"
tags: ["Coding Agent", "多Agent协作", "任务调度", "开源工具", "Claude Code", "Codex"]
lang: "zh-CN"
wechatTitle: "Avalon：四种Coding Agent组成协作小队"
wechatDigest: "GPL v3；Codex/Claude Code/Cline/Pi接同一Core；Company/Messages/Plan三视图；跨平台SSH协作"
---

如果你同时用 Codex 和 Claude Code，你一定知道那种割裂感：两个窗口、两套上下文、没有办法让它们分工又对齐。

Avalon 解决这个问题的方式是：给所有 Coding Agent 接入同一个 Core，然后用三个视图把团队、对话和任务统一管起来。

GitHub: https://github.com/Daijunfan/Avalon | ⭐ 7 | GPL-3.0 | JavaScript | v0.58.1

---

## 三个视图

### Company：把协作关系看清楚

画布里，Secretary 居中协调六位 Manager，每位 Manager 管理两名员工。不同 Agent 在同一画布里显示工作状态、休息状态和绿色通信连线。每个 Agent 绑定实际工作区（本机目录或 SSH 远程主机）。

这层可视化的意义不只是好看：当你有十几个 Agent 在跑，你需要知道谁在哪台机器上处理哪个任务。Company 视图让这个关系一目了然。

### Messages：群组聊任务，频道读新闻

群消息送达全部当前成员，@ 点名和回复确定处理对象，其他成员同步知悉。员工公开发言通过发布 API，普通会话输出留在本人会话里，不会污染群组。

频道保留原始新闻、来源和图像，员工可以在同一处发布摘要和分析——把信息收集和 Agent 处理整合进同一个地方。

### Plan：十种布局排任务

月历、周计划、看板、时间线等十种布局，支持三类任务：

- **一次性**：指定时间执行一次
- **重复**：按 cron 表达式循环
- **事件驱动**：某个条件触发后执行

计划事项和实际执行记录分别呈现，方便追溯负责人、后续安排和结果。

---

## 四种引擎，接入方式各不同

| 引擎 | 协议 | 执行范围 |
|------|------|----------|
| Codex | App Server | Core 本地及 SSH / 云端原生工作区 |
| Claude Code | Claude Agent SDK | Core 本地及 SSH / 云端原生工作区 |
| Cline | ACP | Core 本地，或通过 Tunnel 操作远端 |
| Pi | RPC | Core 本地，或通过 Tunnel 操作远端 |

**员工引擎在创建时确定**，之后不能切换引擎，只能换同一引擎下的模型配置。模型账号、额度和费用由各服务商自己管，Avalon 不代管。

Codex 和 Claude Code 支持云端原生执行；Cline 和 Pi 目前只支持通过 Tunnel 操作远端。

---

## CLI / Core API：专为 Agent 操作设计

这是 Avalon 的一个有意思的设计：所有功能都通过 CLI 和 Core API 暴露，可以让 Agent 直接调用，不需要人工点界面。

```sh
# 查看团队文件树
agents assets tree --view Messages --employee EMPLOYEE_ID --json

# 列出计划任务
agents api call plan.query --args '{"limit":50}' --json

# 删除调度任务
agents api call schedule.delete --args '{"ids":["JOB_A"],"expectedRevisions":{"JOB_A":2}}' --json

# 查看可用 API
agents api list --prefix schedule. --json
```

这意味着你可以让一个 Secretary Agent 通过 API 来分配任务、调度工作、读取消息，而不只是在界面上手动操作。README 里也明确说了：「你不需要会用！只需创建一个帮你使用本软件的秘书。」

---

## 权限体系

权限来自**职位**加**当前授权**，不是连线或名称。三个职位级别：

- **Secretary**：协助用户管理应用与插件，只有用户可任免
- **Governor**：跨 Team 组织工作
- **Manager**：管理本 Team 的员工

群组和频道还检查真实成员身份，光有职位不够，还要是真实成员才能访问该群组。

读操作不需要额外审批；写操作（修改任务、编辑文件、发消息）在 Ask/acceptEdits/auto 模式下需要用户决定，Full access 模式下自动放行，dontAsk 或 native planning 模式下拒绝。

---

## 三个官方插件

插件源码在 `PlugIns/` 目录下，完整可用：

1. **Cloud Hosts**：SSH 主机管理、连接状态和远程桌面入口
2. **MiniNotion**：本地笔记、数据库、计划、日历和知识组织
3. **Margin Reader**：文档阅读、摘录和资料整理

插件工作资料和凭据放在应用安装包之外，升级不会自动移动。

---

## 安装与启动

**从源码启动**（需要 Node.js 22.18+）：

```bash
git clone https://github.com/Daijunfan/Avalon.git
cd Avalon
npm ci
npm run setup
npm run build:plugins
npm run build
npm run dev
```

**浏览器后端模式**：

```bash
npm run build:server && npm run build:web
node bin/avalon serve --web --port 5151
# 另开终端：
node bin/avalon web token
# 打开 http://127.0.0.1:5151 输入令牌
```

旧版 `Anexus.app` 会自动迁移，`anexus` 命令作为兼容入口，数据目录默认在 `~/AgentsCompany`。

---

## 适合什么场景

Avalon 的定位是「重度开发 + 日常任务 + 社会互动实验」都能跑的 Agent 协作平台。从 README 列出的用法来看，它的目标用户是：

- 需要同时驱动多个 Coding Agent 处理不同子任务的开发者
- 想要把 Agent 工作流自动化（定时跑、事件触发跑）的工程师
- 想做多 Agent 交互实验的研究者

**实际局限**：7 颗星的早期项目，版本 0.58.1——版本号高但星数低，说明项目还在早期阶段。严格进程隔离目前只支持 macOS；Cline/Pi 的云端原生执行暂不支持；多平台需要在目标系统上单独验证。

---

> GPL v3 开源。模型账号、额度和费用由各 Coding Agent 服务商提供，Avalon 不代管。开源仅供学习参考。

---

<!--EN-->

## Avalon: Organize Multiple Coding Agents Into a Collaborating Team

If you've used both Codex and Claude Code, you know the fragmentation: two windows, two separate contexts, no way to make them coordinate on the same task.

Avalon's answer: connect all Coding Agents into a single Core and manage teams, conversations, and tasks through three unified views.

GitHub: https://github.com/Daijunfan/Avalon | ⭐ 7 | GPL-3.0 | JavaScript | v0.58.1

---

### Three Views

**Company** — visualizes team structure on a canvas: Secretary coordinates six Managers, each managing two employees. Different Agents share the same canvas, showing work state, idle state, and green communication links. Each Agent is bound to an actual workspace (local directory or SSH remote host).

**Messages** — group messages reach all current members; @ mentions and replies specify the target; other members stay in the loop. Employee public responses go through the publish API; private session output stays in the individual's session.

**Plan** — ten layout options (monthly calendar, weekly plan, kanban, timeline, etc.) for three task types: one-time, recurring (cron), and event-driven. Planned items and execution logs are presented separately for easy tracing.

---

### Four Engines

| Engine | Protocol | Execution Scope |
|--------|----------|-----------------|
| Codex | App Server | Core local + SSH / cloud-native workspaces |
| Claude Code | Claude Agent SDK | Core local + SSH / cloud-native workspaces |
| Cline | ACP | Core local, or remote via Tunnel |
| Pi | RPC | Core local, or remote via Tunnel |

Engine is fixed at employee creation — switching engines means creating a new employee. Model accounts, quotas, and billing are each provider's own.

---

### CLI / Core API for Agent-Native Operations

Every capability is exposed through CLI and Core API — designed so Agents can operate the platform directly without human UI interaction.

```sh
agents api call plan.query --args '{"limit":50}' --json
agents api call schedule.delete --args '{"ids":["JOB_A"],"expectedRevisions":{"JOB_A":2}}' --json
agents api list --prefix schedule. --json
```

The README's framing: "You don't need to know how to use it — just create a Secretary who uses it for you."

---

### Permissions

Permissions come from **role + authorization**, not from visual links or names:

- **Secretary**: application and plugin management; only the user can appoint/dismiss
- **Governor**: cross-team coordination
- **Manager**: manages employees within their Team

Group and channel access also requires real membership. Reads need no extra approval. Writes require user decision (Ask/acceptEdits/auto), are auto-approved in Full access, and are rejected in dontAsk/native planning mode.

---

### Setup

Requires Node.js 22.18+:

```bash
git clone https://github.com/Daijunfan/Avalon.git && cd Avalon
npm ci && npm run setup && npm run build:plugins && npm run build && npm run dev
```

Default data directory: `~/AgentsCompany`. Legacy `Anexus.app`/`anexus` command migrates automatically.

---

### Constraints

Early-stage project (7 stars despite version 0.58.1 — high version number reflects iteration speed, not adoption). Strict process isolation is macOS-only; Cline/Pi don't yet support cloud-native execution; each platform requires independent validation. The README explicitly notes: "A single Agent output does not guarantee the task completed correctly."

---

> GPL v3. Model accounts, quotas, and billing are each provider's own — Avalon does not manage these. For technical reference only.
