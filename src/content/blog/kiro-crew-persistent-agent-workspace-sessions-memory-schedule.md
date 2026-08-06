---
title: "Kiro Crew：开发 Agent 之上的持续工作层，会话/记忆/定时/审批/多 Agent 一体"
titleEn: "kiro-crew-persistent-agent-workspace-sessions-memory-schedule"
description: "Kiro Crew 是运行在 Kiro（AWS 的 Agentic IDE）之上的开源持续工作层：Gateway 进程常驻本地或远程机器，跨 session 保存上下文和教训，支持定时任务/心跳监控/审批/并行子 Agent，通过 Slack/Telegram/WeCom/微信等渠道随时继续同一个工作。起源于 Amazon 内部项目 MeshClaw，6 个月内积累 39000 开发者，今日正式开源。"
descriptionEn: "Kiro Crew is an open-source persistent workspace layer above Kiro (AWS's agentic IDE): a Gateway process that runs continuously on hardware you control, keeping sessions, memory, lessons, and skills alive across conversations. Scheduled jobs, heartbeat monitoring, approvals, and parallel subagents are built-in. Continue the same work from Slack, Telegram, WeCom, or WeChat. Started as Amazon internal project MeshClaw, 39,000 developers in 6 months, now fully open-source. Apache 2.0."
pubDate: "2026-08-06"
updatedDate: "2026-08-06"
category: "Tech-News"
tags: ["AI Agent", "开发工具", "持续工作", "多Agent", "本地优先", "定时任务", "Kiro", "Mycelium"]
heroImage: "../../assets/images/kiro-crew-persistent-agent-workspace-sessions-memory-schedule-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 Agent 会话的生命周期是这样的：你开了一个对话，Agent 做了一些事，对话窗口关掉，所有上下文消失，下次你回来 Agent 不知道你是谁，不知道上次做到哪里了，也不记得上次你说过不要做什么。

这是一个工程设计问题，不是模型能力问题。**[Kiro Crew](https://github.com/kirodotdev/KiroCrew)** 要解的正是这个问题：在 Kiro（AWS 的 Agentic IDE）之上提供一个持续运行的工作层，让 Agent 在会话之间保持状态、记住教训、执行定时任务、支持并行子 Agent，并让你从任何渠道继续同一个工作。

今日在 Product Hunt 正式发布（开源，Apache 2.0）。起源：Amazon 内部项目 MeshClaw，6 个月内积累了 39,000 名开发者和数百名贡献者。

---

## 它是什么

Kiro Crew 是一个**本地 Gateway 进程**（可以运行在你的 Mac、容器，或远程机器上），它在 Kiro CLI 之上提供了一层持续服务：

```
[ 各接入面 ]
  桌面应用 · Web Dashboard · Slack · Telegram · WeCom · 微信 · CLI
         ↓
   [ Gateway ]
     会话管理 · 记忆注入 · 定时调度 · 审批代理 · 安全策略 · App 扩展
         ↓
   [ Agent 会话 ]
     ACP runtime · kiro-cli · MCP 工具 · 模型调用
```

你在 Slack 发一条消息继续昨天的任务，Gateway 恢复同一个 Agent 会话的上下文；你设置一个每天早上 9 点的定时任务，Agent 在没人盯着的情况下跑完并把结果推到你指定的渠道；你派出三个并行子 Agent 做竞品调研，结果汇回主会话进行综合。

---

## 四个核心能力

### 1. 持久性：会话不因关闭而消失

会话、记忆、定时任务的检查点在 Gateway 重启后继续存在。下次打开对话不是冷启动，而是接着之前的进度。

记忆结构：
- **偏好**：你的工作风格和工具偏好
- **活跃项目上下文**：当前工作的项目信息
- **衰减历史摘要**：旧会话内容压缩保留
- **持久教训**：明确说"这样不对"之后形成的规则

```
你说："不对，前端检查必须在说完成之前跑完。"
→ 变成工作区范围的持久教训，在后续会话里自动应用。
```

### 2. 自我学习：失败变规则

任务失败、用户纠正、边界情况——这些不只被记录在日志里，而是可以被提炼为未来会话的行为规则。下次遇到类似情况，Agent 会带着上次的教训工作。

### 3. 自我进化：重复模式变技能

频繁出现的操作模式可以被合成为可复用的 Skill，存为 Markdown 文件，可以查看、编辑、删除。每个 Kiro Crew 随着使用会越来越贴合使用者的工作方式。

### 4. 无人值守运行

| 运行模式 | 适用场景 | 入口 |
|---------|---------|------|
| **Scheduled（定时）** | 每日简报、审计、备份、定期维护 | `kirocrew cron` 或自然语言设置 |
| **Proactive（主动）** | 目标需要多轮推进，不等用户消息 | AutoNudge 和 goal-loop skill |
| **Reactive（响应式）** | CI 告警、外部自动化、Slack 事件 | Agent webhook + 消息事件 |
| **Task runner（任务跑道）** | 有明确步骤的有界项目，支持检查点恢复 | `kirocrew run TASK.md` |
| **Subagents（子 Agent）** | 可并发的独立工作流 | `kirocrew spawn run "任务"` |

---

## 接入面：从哪里都能继续工作

**本地接入**：
- 桌面应用（macOS/Linux，内置 Gateway，支持连接远程 Gateway）
- Web Dashboard（`localhost:5476`，并发对话 + 审批 + 记忆 + 定时任务 + App）
- CLI（`kirocrew chat`、`run`、`cron`、`spawn`、`security`）

**消息渠道**（出站连接，不需要开放公网端口）：
- **Slack**：DM 和 Thread，流式回复，审批作为消息按钮
- **Telegram**：手机 DM，内联审批，命令
- **Discord**：DM，流式回复，审批按钮
- **Teams / Webex**：流式回复，内联审批
- **WeCom（企业微信）**：配置用户权限，流式回复
- **WeChat（微信）**：配置用户权限，流式回复

所有渠道共享同一 Gateway 的记忆、工具权限和审批策略，换个渠道继续，Agent 不需要重新了解背景。

---

## 安全：在运行时边界强制执行

Kiro Crew 给 Agent 真实的工具访问权，安全控制在运行时而不是 prompt 层面：

| 机制 | 内容 |
|------|------|
| **本地优先** | Dashboard 默认绑定 loopback，远程访问需 token 认证 |
| **交互式审批** | Dashboard / Slack / Telegram 里审批工具调用请求 |
| **OS 沙箱** | Linux/macOS：namespace 或 Seatbelt 隔离；Windows：默认拒绝，需显式 opt-in |
| **敏感路径守卫** | 阻止直接访问受保护路径，脱敏凭据从输出中 |
| **137 条拒绝规则** | 内置：阻断破坏性命令和常见数据外泄路径 |
| **治理天花板** | 策略文件以"最严者优先"组合，App 或 Agent 只能收窄权限，不能放宽 |
| **可审计** | 安全事件和工具活动全部记录，`kirocrew security events/audit/verify` 可查 |

---

## 快速安装

**一行安装**（macOS/Linux）：

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
```

打开 `http://localhost:5476` 开始对话。

**Docker**（always-on 服务器）：

```bash
docker run -d --name kirocrew \
  -p 127.0.0.1:5476:5476 \
  -v kirocrew-home:/home/kirocrew \
  ghcr.io/kirodotdev/kirocrew:stable
```

**从源码构建**（Python 3.10+，Node.js 18+，npm，kiro-cli）：

```bash
git clone https://github.com/kirodotdev/KiroCrew.git
cd KiroCrew
make build
source .venv/bin/activate

kirocrew setup   # 配置
kirocrew doctor  # 健康检查
kirocrew gateway # 启动
```

**桌面应用**：
- macOS：[Stable DMG](https://download.crew.kiro.dev/desktop/stable/latest/KiroCrew.dmg) / Insider / Nightly
- Linux：[Stable AppImage](https://download.crew.kiro.dev/desktop/stable/latest/KiroCrew-x86_64.AppImage)
- Windows：目前无桌面构建，从源码安装后用浏览器打开 Dashboard

还可以追踪更快的 channel：

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --channel insider
```

---

## App Kit：装进 Kiro Crew 的领域工作流

Kiro Crew Apps 是可安装的 Dashboard 扩展，把特定领域的工作流打包成一个产品：

- Dashboard 页面（自定义界面）
- 限定范围的 Gateway API
- 事件订阅
- 生命周期 Hook

已有社区 App：LaunchDarkly 的 Feature Flag 管理 App（`launchdarkly-labs/launchdarkly-kiro-crew-app`），还有游戏（`llamojha/flappy-kiro`）。

---

## 背景：从 Amazon 内部项目到开源

Kiro Crew 最初是 Amazon 内部叫做 **MeshClaw** 的项目，不到 6 个月积累了 39,000 名开发者和数百名贡献者，然后决定开放给所有人。

这个背景很能说明问题：这不是从零开始设计的产品，而是从实际大规模内部使用中提炼出来的。

---

## 为什么值得关注

Agent 框架的竞争一直集中在「更好的单步执行」上——更准的代码生成、更聪明的工具调用。Kiro Crew 关注的是另一个维度：**跨会话的持续性和自主性**。

当 Agent 能记住你的工作偏好、在你睡觉时继续跑定时任务、从上次失败的地方重试、把反复用到的操作变成技能——它才从一个「问答工具」变成一个「持续工作的伙伴」。

这是 Agent 从「有用」到「不可缺少」的路径。

仓库：[github.com/kirodotdev/KiroCrew](https://github.com/kirodotdev/KiroCrew)  
Product Hunt：[producthunt.com/posts/kiro-crew](https://www.producthunt.com/posts/kiro-crew)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Kiro Crew: The Persistent Work Layer Above Development Agents

*by Mycelium Protocol*

Most agent sessions end when the chat closes. Context is gone. Next time you open a conversation the agent doesn't know your project, doesn't remember what it learned, and can't tell you how far it got on that task you left running. That's a systems engineering problem, not a model capability problem.

**[Kiro Crew](https://github.com/kirodotdev/KiroCrew)** is the open-source answer: a persistent workspace layer above Kiro (AWS's agentic IDE) that keeps a Gateway process running on hardware you control — persisting sessions, memory, lessons, and skills across conversations, running scheduled and reactive work without someone at the terminal, and letting you continue the same work from Slack, Telegram, WeCom, WeChat, or the CLI. Launched today on Product Hunt, Apache 2.0. Background: started as Amazon internal project MeshClaw, 39,000 developers and hundreds of contributors in under 6 months.

### The Architecture

```
[ Surfaces ]
  Desktop app · Web Dashboard · Slack · Telegram · WeCom · WeChat · CLI
         ↓
   [ Gateway ]
     sessions · memory injection · scheduling · approvals · security policy · apps
         ↓
   [ Agent sessions ]
     ACP runtime · kiro-cli · MCP tools · model calls
```

The Gateway separates where the agent runs from where you work with it. Whether you're in the dashboard or a Slack DM, the same session, memory, and tool policy is in effect.

### Four Core Capabilities

**Persistent.** Sessions, memory, schedules, and task checkpoints survive Gateway restarts. Return to progress, not a cold start. Memory structure: preferences, active project context, decaying history summaries, and durable lessons formed from corrections.

```
You say: "No — always run the frontend checks before calling something done."
→ Becomes a workspace-scoped lesson applied in all future sessions.
```

**Self-learning.** Task failures and corrections become durable behavioral rules for future sessions, not just notes in a log.

**Self-evolving.** Repeated patterns are synthesized into reusable Markdown skills — inspectable, refineable, removable from the dashboard. Each Kiro Crew grows more tailored to the person and work around it.

**Unattended autonomy.** Five work-starting modes:

| Mode | Use it for |
|------|-----------|
| Scheduled | Daily briefings, audits, backups — `kirocrew cron` or natural language |
| Proactive | Goals that need another pass without waiting for a message |
| Reactive | CI alerts, webhooks, messaging events |
| Task runner | Bounded projects with steps, tests, and checkpoint resume |
| Subagents | Parallel workstreams — `kirocrew spawn run "task"` |

### Surfaces

Works from the dashboard or CLI, and continues through outbound-connected messaging channels (no public port exposure required): **Slack, Telegram, Discord, Teams, Webex, WeCom, WeChat** — all sharing the same Gateway memory and approval policies.

### Security at the Runtime Boundary

- **Local by default** — dashboard binds to loopback; remote access requires token auth
- **Interactive approvals** — review tool requests from dashboard, Slack, or Telegram
- **OS sandboxing** — Linux/macOS: namespace or Seatbelt isolation; Windows: fails closed by default
- **137 bundled deny patterns** — block destructive commands and common exfiltration paths
- **Governance ceiling** — policy files compose with tightest-wins: apps and agents can narrow scope, never loosen it

### Quick Start

```bash
# One-line install (macOS/Linux)
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
# Open http://localhost:5476

# Docker (always-on servers)
docker run -d --name kirocrew \
  -p 127.0.0.1:5476:5476 \
  -v kirocrew-home:/home/kirocrew \
  ghcr.io/kirodotdev/kirocrew:stable
```

### Why It Matters

Competition in agent frameworks has focused on single-step execution quality — better code generation, smarter tool calling. Kiro Crew focuses on a different dimension: **cross-session continuity and autonomous operation**.

When an agent remembers your work preferences, runs scheduled tasks while you sleep, resumes from the last checkpoint on a failed task, and converts repeated patterns into reusable skills — it crosses from "useful tool" to "ongoing work partner." That transition is what makes agent infrastructure genuinely indispensable.

Repository: [github.com/kirodotdev/KiroCrew](https://github.com/kirodotdev/KiroCrew) · Product Hunt: [producthunt.com/posts/kiro-crew](https://www.producthunt.com/posts/kiro-crew)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
