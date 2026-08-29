---
title: "Superset：一个工作区跑 100 个 Agent，Claude Code、Codex、OpenCode 同时干活——普通人上手指南"
titleEn: "superset-parallel-coding-agent-workspace-claude-codex-opencode"
description: "Superset（GitHub: superset-sh/superset，⭐13.5k）是一个 macOS 桌面应用，可以把 Claude Code、Codex、OpenCode 等任意命令行 AI 编程 agent 放进同一个工作区，每个 agent 跑在独立的 git worktree 里，100 个并行互不干扰。内置浏览器、diff 查看器、定时自动化、CLI、MCP Server 接入，iOS 版在路上。免费版永久可用，个人开发者零成本上手。"
descriptionEn: "Superset (GitHub: superset-sh/superset, ⭐13.5k) is a macOS desktop app that runs Claude Code, Codex, OpenCode, and any CLI coding agent in one unified workspace — each in its own isolated git worktree, up to 100+ in parallel. Built-in browser, diff viewer, automations, CLI, MCP Server, iOS coming soon. Free tier is free forever."
pubDate: "2026-08-29"
updatedDate: "2026-08-29"
category: "Tech-News"
tags: ["Superset", "Claude Code", "Codex", "OpenCode", "parallel agents", "开发工具", "AI编程"]
heroImage: "../../assets/images/superset-parallel-coding-agent-workspace-claude-codex-opencode-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/superset-sh/superset | ⭐ 13,470 | 2025-10-21 创建  
官网：https://superset.sh | 最新版：v1.25.0（2026-08-26）  
许可证：Elastic License 2.0（源码可看，免费用，不能卖）  
平台：macOS（Intel + Apple Silicon）| Linux 实验性 | iOS 即将上线

---

## 它解决什么问题

Claude Code 很好用，但你每次只能跑一个任务——它在想，你在等。

Superset 把这个模式翻转了：**你给每个任务各开一个工作区，每个工作区跑一个 agent，agent 工作的时候你做别的，等多个 agent 同时汇报结果。**

官方的核心承诺是：「Run 100+ Coding Agents in Parallel」（100+ agent 并行）。

---

## 核心机制：git worktree 隔离

Superset 不是让多个 agent 共用同一个代码目录——那会互相干扰、产生冲突。它的隔离单位是 **git worktree**：

```
主仓库
├── .git/          ← 共享 git 对象库
├── worktrees/
│   ├── ws-1/      ← Claude Code 在这里改 billing
│   ├── ws-2/      ← Codex 在这里重构 auth
│   ├── ws-3/      ← OpenCode 在这里写 API 文档
│   └── ws-4/      ← Gemini CLI 在这里跑测试
```

每个 worktree 有独立的文件系统视图、独立的 branch、独立的终端。agent 之间完全隔离，但共享 git 历史。做完之后，在 Superset 里看 diff，选出最好的结果 merge 进去。

---

## 支持的 Agent（20+）

| Agent | 状态 |
|-------|------|
| Claude Code | 完全支持 |
| OpenAI Codex CLI | 完全支持 |
| OpenCode | 完全支持 |
| Cursor Agent | 完全支持 |
| Gemini CLI | 完全支持 |
| GitHub Copilot | 完全支持 |
| Amp Code | 完全支持 |
| Kiro | 完全支持 |
| Grok | 完全支持 |
| Kimi Code | 完全支持 |
| 其他任意 CLI agent | 无需配置，直接可用 |

「如果它能在终端里跑，它就能在 Superset 上跑。」

---

## 普通人怎么上手

### 第一步：安装

macOS（Apple Silicon）：
```bash
# 方式 1：直接下载 DMG
# 去 https://github.com/superset-sh/superset/releases/latest
# 下载 Superset-arm64.dmg，双击安装

# 方式 2：Homebrew（CLI）
brew install superset-sh/tap/superset
```

或者直接从 https://superset.sh 点 Download 按钮。

打开之后用 GitHub 账号登录。不需要填 API Key——你的 Claude Code、Codex 各自用自己的订阅，Superset 本身不代理模型。

### 第二步：导入你的项目

点左侧「Projects」→「Add project」→ 选择你的 git 仓库目录（必须是 git 仓库）。Superset 读取仓库信息，之后你从这里创建工作区。

### 第三步：创建第一个工作区

点「New Workspace」（或 ⌘⇧N），选一个 agent，写任务描述，按 Enter。

Superset 会：
1. 为这个 worktree checkout 一个新 branch
2. 打开终端，自动启动你选的 agent
3. 把任务描述作为第一条消息发给 agent

你可以同时创建多个工作区，每个工作区独立运行。

### 第四步：查看结果

agent 工作完成后，在工作区卡片里点 **Changes** 看内置 diff viewer。喜欢就点 Merge，不喜欢就关掉这个 worktree。

**一句话流程：描述任务 → 选 agent → 等结果 → 看 diff → merge。**

---

## 五个让效率翻倍的功能

### 1. 浏览器内置 + Design Mode

Superset 有一个内置浏览器面板（不是打开 Chrome，是 app 内的 webview）。

**Design Mode** 是最近刚上线的功能：打开浏览器面板，点工具栏里的「Design」按钮，然后在网页上点任意元素——一个 prompt 卡片会弹出来。写你的修改需求，发送，agent 收到的是：元素的 DOM 结构、CSS 样式、React 组件信息、截图。你不需要手动描述「左边那个蓝色按钮」，Superset 帮你定位。

实测场景：打开本地 `localhost:3000`，指着一个按钮说「把这个改成绿色，样式和旁边那个保持一致」，Claude Code 直接知道你在说哪个。

### 2. Automations（定时自动化）

类似 cron，但用自然语言写触发条件，agent 来执行：

| 名称 | 触发条件 | 用途 |
|------|---------|------|
| daily-triage | 每天 9:00 | 自动过一遍新 issue，打标签 |
| changelog-draft | 每周日 11:00 | 汇总这周 PR，起草 changelog |
| dep-upgrades | 每周 | 跑 `npm audit fix`，开 PR |
| roadmap-sync | 每月 | 把 Linear 里的 milestone 同步到 README |

触发源除了时间，还支持（实验性）：Slack 消息、Linear issue、GitHub PR、Notion、Sentry 告警、Google Calendar、Gmail、Webhook。

### 3. 远程主机（Remote Access）

连上 GPU 服务器或 VPS，在本地 Superset 界面看那台机器的工作区：

```bash
superset connect my-gpu-box
```

连接后，那台机器的 worktree 出现在你的工作区列表里，可以像本地一样操作。适合跑训练、做大规模代码生成等需要算力的任务。（Pro 功能，$15/月/人）

### 4. Usage 仪表盘（多账户管理）

你可以在 Superset 里加多个 Claude Code 账户——比如个人 Claude Max、公司 Team 账户。Usage 标签页实时显示每个账户的配额消耗、token 花费折线图。一个账户快跑完了，自动切到另一个账户继续。

### 5. 多窗口并排

`File → New Window`，开两个 Superset 窗口放两个屏幕，每个窗口锁定一个项目。左屏改产品代码，右屏做 API 文档，互不影响。

---

## 实际工作流示例

### 场景：发布前 bug 修复冲刺（30分钟做完10个 issue）

```
1. 打开 Linear / GitHub Issues，列出所有 P0 bug
2. 每个 bug 建一个 Superset workspace，选 Claude Code
3. 把 issue 描述直接粘进 prompt，开跑
4. 10分钟后开始陆续收到完成通知
5. 挨个看 diff，满意的 merge，不满意的 comment 让 agent 重跑
6. 所有 PR 合并，done
```

### 场景：A/B 测试两种实现方案

```
1. Workspace A：让 Claude Code 用方案 A 实现新功能
2. Workspace B：让 Codex 用方案 B 实现同一功能
3. 两个 agent 同时跑，你去喝咖啡
4. 回来后对比两个 diff，选择更好的，关掉另一个
```

---

## 定价

| 计划 | 价格 | 核心限制 |
|------|------|--------|
| Free | $0，永久 | 1 人，仅本机工作区 |
| Pro | $15/人/月（年付） | 无限用户，远程访问，Slack/Linear，iOS |
| Enterprise | 定制 | SOC 2 Type II，SAML SSO，SCIM |

**免费版已经够用**：本地无限工作区，无限并行 agent，Claude Code + Codex + OpenCode 全都能跑。付费是为了远程主机、团队协作、手机端。

---

## 技术架构（给开发者）

- **桌面**：Electron + React + Tailwind，Bun 构建
- **后端**：tRPC + Drizzle ORM + Neon（PostgreSQL）
- **实时同步**：Electric（基于 Postgres logical replication）
- **开发**：`bun run dev`，Docker 起本地 Postgres + Electric，无需第三方服务账户

```bash
# 本地开发全套
git clone https://github.com/superset-sh/superset.git
cd superset
./.superset/setup.local.sh   # 起 Docker + Postgres，配置 dev 账户
bun run dev                  # 启动开发版桌面 app
```

---

## 相关链接

- GitHub：https://github.com/superset-sh/superset
- 官网：https://superset.sh
- 文档：https://docs.superset.sh
- Changelog：https://superset.sh/changelog
- Discord：https://discord.gg/cZeD9WYcV7
- Twitter：https://x.com/superset_sh

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

<!--EN-->

## Superset: One Workspace for 100 Parallel Agents — Claude Code, Codex, OpenCode Running Side by Side

*by Mycelium Protocol*

---

GitHub: https://github.com/superset-sh/superset | ⭐ 13,470 | Created: 2025-10-21  
Website: https://superset.sh | Latest: v1.25.0 (2026-08-26)  
License: Elastic License 2.0 (source-available, free to use, not resellable)  
Platforms: macOS (Intel + Apple Silicon) | Linux (experimental) | iOS coming soon

---

### What Problem It Solves

Claude Code is powerful, but you run one task at a time — it thinks, you wait.

Superset flips the model: **open a workspace for each task, each workspace runs one agent, you do other things while they work in parallel, then review results when multiple agents finish.**

The headline promise: "Run 100+ Coding Agents in Parallel."

---

### Core Mechanism: git worktree Isolation

Superset doesn't make multiple agents share the same directory — that causes conflicts. The isolation unit is the **git worktree**:

```
your-repo/
├── .git/           ← shared git object store
├── worktrees/
│   ├── ws-1/       ← Claude Code fixing billing
│   ├── ws-2/       ← Codex refactoring auth
│   ├── ws-3/       ← OpenCode writing API docs
│   └── ws-4/       ← Gemini CLI running tests
```

Each worktree has its own filesystem view, its own branch, its own terminal. Agents are completely isolated but share git history. When done, review diffs inside Superset and merge the winner.

---

### Supported Agents (20+)

| Agent | Status |
|-------|--------|
| Claude Code | Fully supported |
| OpenAI Codex CLI | Fully supported |
| OpenCode | Fully supported |
| Cursor Agent | Fully supported |
| Gemini CLI | Fully supported |
| GitHub Copilot | Fully supported |
| Amp Code | Fully supported |
| Kiro | Fully supported |
| Grok | Fully supported |
| Kimi Code | Fully supported |
| Any other CLI agent | Works without configuration |

"If it runs in a terminal, it runs on Superset."

---

### Getting Started (Ordinary User Guide)

**Step 1: Install**

macOS (Apple Silicon):
```bash
# Option 1: Download DMG
# Go to https://github.com/superset-sh/superset/releases/latest
# Download Superset-arm64.dmg, open and drag to Applications

# Option 2: Homebrew (CLI only)
brew install superset-sh/tap/superset
```

Or click Download at https://superset.sh.

Log in with your GitHub account. No API key needed — Claude Code and Codex each use their own subscriptions; Superset doesn't proxy models.

**Step 2: Import your project**

Click "Projects" in the sidebar → "Add project" → select your git repository directory (must be a git repo). Superset reads the repo and you create workspaces from there.

**Step 3: Create your first workspace**

Click "New Workspace" (or ⌘⇧N), choose an agent, write a task description, press Enter.

Superset will:
1. Check out a new branch for this worktree
2. Open a terminal and auto-launch your chosen agent
3. Send your task description as the first message

Create multiple workspaces simultaneously — each runs independently.

**Step 4: Review and merge**

When an agent finishes, click **Changes** on its workspace card to see the built-in diff viewer. Like it? Click Merge. Don't? Close the worktree.

**One-line workflow: describe task → pick agent → wait for result → review diff → merge.**

---

### Five Features That Double Your Output

**1. Built-in Browser + Design Mode**

Superset includes an in-app browser panel. **Design Mode** (launched August 2026): click "Design" in the browser toolbar, then click any element on the page — a prompt card pops up right below the element. Type your change, send it, and the agent receives the element's DOM, CSS styles, React component info, and a cropped screenshot alongside your note. No need to manually describe "the blue button on the left."

**2. Automations**

Cron-like but written in natural language, executed by an agent:

| Name | Schedule | Purpose |
|------|----------|---------|
| daily-triage | Daily 9:00 AM | Triage new issues, apply labels |
| changelog-draft | Sunday 11:00 AM | Summarize PRs, draft changelog |
| dep-upgrades | Weekly | Run `npm audit fix`, open PR |
| roadmap-sync | Monthly | Sync Linear milestones to README |

Trigger sources beyond time (experimental): Slack messages, Linear issues, GitHub PRs, Notion, Sentry alerts, Google Calendar, Gmail, Webhooks.

**3. Remote Host Access**

Connect to a GPU server or VPS and control its workspaces from your local Superset:

```bash
superset connect my-gpu-box
```

After connecting, the remote machine's worktrees appear in your workspace list. For training runs, large-scale codegen, or anything that needs more compute. (Pro feature: $15/user/month)

**4. Usage Dashboard (Multi-Account)**

Add multiple Claude Code accounts — personal Claude Max, company Team account. The Usage tab shows real-time quota consumption and token spend per account. One account approaching limit? Switch to another automatically.

**5. Multiple Windows**

`File → New Window` opens a second Superset window. Two screens, two projects, side by side. Left screen: product code. Right screen: API docs. Each window locks to its own organization; switching orgs in one window doesn't affect the other.

---

### Practical Workflow Examples

**Scenario: Pre-launch bug sprint (10 issues in 30 minutes)**

```
1. List all P0 bugs from Linear / GitHub Issues
2. Create one Superset workspace per bug, assign Claude Code
3. Paste the issue description directly into the prompt, launch
4. Start receiving completion notifications after ~10 minutes
5. Review each diff, merge what's good, comment to retry what isn't
6. All PRs merged — done
```

**Scenario: A/B test two implementation approaches**

```
1. Workspace A: Claude Code implements approach A
2. Workspace B: Codex implements approach B, same feature
3. Both agents run simultaneously while you get coffee
4. Compare two diffs, choose the better one, discard the other
```

---

### Pricing

| Plan | Price | Key constraint |
|------|-------|---------------|
| Free | $0, forever | 1 user, local workspaces only |
| Pro | $15/user/month (annual) | Unlimited users, remote access, Slack/Linear, iOS |
| Enterprise | Custom | SOC 2 Type II, SAML SSO, SCIM |

**The free tier is genuinely useful**: unlimited local workspaces, unlimited parallel agents, Claude Code + Codex + OpenCode all work. You pay for remote hosts, team collaboration, and mobile.

---

### Tech Stack (for developers)

- **Desktop**: Electron + React + Tailwind, built with Bun
- **Backend**: tRPC + Drizzle ORM + Neon (PostgreSQL)
- **Real-time sync**: Electric (Postgres logical replication)
- **Dev setup**: `bun run dev`, Docker brings up local Postgres + Electric, no third-party accounts needed

```bash
git clone https://github.com/superset-sh/superset.git
cd superset
./.superset/setup.local.sh   # starts Docker + Postgres, configures dev account
bun run dev                  # launches development desktop app
```

---

**Links**

- GitHub: https://github.com/superset-sh/superset
- Website: https://superset.sh
- Docs: https://docs.superset.sh
- Changelog: https://superset.sh/changelog
- Discord: https://discord.gg/cZeD9WYcV7
- Twitter: https://x.com/superset_sh

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
