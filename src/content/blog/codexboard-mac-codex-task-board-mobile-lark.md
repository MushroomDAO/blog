---
title: "CodexBoard：Apple Silicon Mac 上把 Codex CLI 接上任务看板，飞书/Web 手机端远程监控执行过程"
titleEn: "CodexBoard: Connect Codex CLI to a Task Board on Apple Silicon Mac — Remote Monitoring via Feishu/Web Mobile"
description: "RocYan98/CodexBoard，115 stars，TypeScript，无开源许可证。运行在 Apple Silicon Mac（macOS 13+）上的本地任务看板，把 Codex CLI 执行过程绑定到 Kanban 看板，支持通过飞书（Lark）或 Web 浏览器在手机端实时监控进度、审批变更、查看代码 Diff。需要公网 frp 服务器作为内网穿透，一周内迭代 10 个版本，目前仍为 0.1.x preview 阶段。"
descriptionEn: "RocYan98/CodexBoard — 115 stars, TypeScript, no open-source license. A local task board running on Apple Silicon Mac (macOS 13+) that binds the Codex CLI execution process to a Kanban board. Supports real-time progress monitoring, change approval, and code diff review via Feishu (Lark) or web browser on mobile. Requires a public frp server for inbound tunneling. 10 releases in a single week; currently 0.1.x preview."
pubDate: 2026-09-21
heroImage: "../../assets/images/codexboard-mac-codex-task-board-mobile-lark-banner.jpg"
category: "Tech-Experiment"
tags: ["codex", "ai-agent", "task-board", "macos", "feishu", "mobile", "kanban"]
lang: zh-CN
---

`RocYan98/CodexBoard` 在 2026 年 9 月 14 日建仓，一周内迭代了 10 个版本，目前是 0.1.11 preview。它解决的问题很具体：本地跑着 Codex CLI 的时候，你不想一直盯着终端，想从手机上看进度、批准变更、接收通知。

**GitHub**：github.com/RocYan98/CodexBoard | **Stars**：115 | **⚠️ 无开源许可证**

---

## ⚠️ 许可证说明

CodexBoard 仓库目前**没有 LICENSE 文件**。在没有明确开源许可证的情况下，代码版权默认归作者所有，技术上属于"所有权利保留（All Rights Reserved）"。

这意味着：**不能将其用于商业产品、不能修改后分发、也不能在生产环境中随意部署**，除非作者明确授权。本文仅作技术拆解和学习参考，使用前请与作者确认授权范围。

---

## 核心定位

CodexBoard 的架构思路是：把本地 Codex CLI 的执行过程映射为一个远程可访问的任务看板。用一句话描述：

**Codex 在 Mac 本地跑，你在手机飞书或浏览器里看进度、批需求、审代码。**

和直接用终端或 claude.ai 网页的区别：
- 不需要一直开着终端窗口
- 手机端有完整的任务状态、流式输出、代码 Diff 视图
- 飞书集成意味着可以在工作聊天流中直接操控 Codex 任务
- 双入口（Web 账号 + 飞书账号）可同时接入同一个本地实例

---

## 功能清单

### 任务看板三视图

- **仪表盘**：任务总览、执行状态统计
- **看板（Kanban）**：拖拽式状态管理，支持优先级/标签/评论/附件
- **列表视图**：线性视图，适合批量操作

### Codex 执行集成

- 从任务卡直接发起 Codex 执行
- 实时查看 Codex 流式输出（不需要盯终端）
- 内联代码 Diff 审阅 + 变更批准工作流
- 支持 Git 分支切换和 Worktree 管理

### 移动端 Remote（核心亮点）

通过飞书或浏览器手机端：
- 创建/继续 Codex 对话
- 查看执行进度的实时流式输出
- 发送附件（图片、文档）
- 审查代码 Diff
- 批准或拒绝 Codex 提议的变更

### CLI 工具 `taskctl`

提供命令行接口供 Agent 查询/管理任务：

```bash
# 配对授权（触发 OAuth，需真实用户在浏览器确认）
taskctl auth login

# 查看任务列表
taskctl project list
taskctl issue list --project <id>

# 创建评论
taskctl comment create --issue <id> --body "..."
```

**安全约束**：写操作必须与真实用户 session 配对，Agent 不能自行批准任何操作。

### Codex Skill 集成

安装后内置 `manage-codexboard` Skill（路径 `~/.agents/skills/manage-codexboard`），让 Codex 能直接通过自然语言操作任务板。

---

## 技术架构

```
手机/Web 浏览器
     ↕  HTTPS
 公网 frp 服务器
     ↕  frp client（内置）
Mac 本地（Apple Silicon）
├── CodexBoard App（TypeScript + SQLite）
│   ├── Caddy 内置 HTTPS 服务器
│   ├── 任务看板 Web UI
│   └── Codex 执行引擎绑定
└── 本地 Codex CLI
```

**选型特点**：
- 全部依赖内置在 `.dmg` 包里（Node.js、Caddy、frpc），无需 Docker/Homebrew/Rust
- SQLite 本地存储，数据不出 Mac
- frp 做内网穿透，需要用户自备公网服务器

---

## 安装

```bash
# 1. 从 GitHub Releases 下载 .dmg
# https://github.com/RocYan98/CodexBoard/releases
# 文件名：CodexBoard-0.1.11-macos-arm64.dmg

# 2. 验证完整性
shasum -a 256 -c CodexBoard-0.1.11-macos-arm64.dmg.sha256

# 3. 拖入 /Applications/
# 首次启动需要手动右键→打开，绕过 macOS 安全提示
# （因为没有 Apple Developer ID 签名）
```

**首次配置需要三项**：
1. `frpc.toml`（你的公网 frp 服务器地址和 Token）
2. Web 账号（用户名 + 8~256 位密码）或飞书自建应用（App ID + App Secret）
3. 确认本地 Codex CLI 已登录

数据存储路径：`~/Library/Application Support/CodexBoard/`

---

## 平台限制

- **仅 Apple Silicon Mac**（M 系列芯片），明确不支持 Intel Mac、Windows、Linux
- **macOS 13 Ventura 及以上**
- **必须有公网 frp 服务器**，没有就无法从手机访问（除非手机和 Mac 在同一局域网 + 直连）
- HTTP/TCP 模式下凭据明文传输，建议始终用 HTTPS 模式

---

## 不足之处

**1. 无开源许可证**：最大的合规风险，使用前必须确认授权。

**2. 依赖公网 frp 服务器**：需要自备 VPS 搭建 frp server，门槛不低，增加了额外的维护成本和安全面。

**3. 无项目级权限隔离**：所有 Web 账号共享同一块看板，多人协作场景下权限控制粗糙。

**4. 尚无 Apple Developer ID 签名**：每次升级都可能触发 macOS 安全提示，用户体验有摩擦。

**5. 仍在 0.1.x preview 阶段**：一周 10 个版本的迭代速度说明项目还不稳定，API 和存储格式随时可能破坏性变更。

**6. 单人项目**：目前只有一位贡献者，可持续性存在风险。

---

## 怎么看这个项目

CodexBoard 解决的场景是真实的：Codex 任务跑起来之后，你不可能一直盯着终端。把执行状态映射到任务看板、接入飞书通知，是一个合理的工程方向。

技术实现上选择了 "everything in the .dmg" 的策略（内置 Node.js、Caddy、frpc），避免了用户配环境的麻烦，这个取舍是正确的。飞书集成而不是 Slack，也说明作者面向的是国内用户场景。

主要问题是**没有开源许可证**，这对于个人工具来说很常见但不理想；以及 frp 依赖对于非技术用户来说门槛偏高。如果作者后续加上 Tailscale 或 ZeroTier 作为穿透替代方案，会更友好。

> 代码无开源许可证，使用前请联系作者确认授权范围。仅供技术学习参考。

---

<!--EN-->

## CodexBoard: Connect Codex CLI to a Task Board on Apple Silicon Mac

`RocYan98/CodexBoard` launched September 14, 2026 and shipped 10 releases in a single week. It addresses a specific problem: when running Codex CLI tasks on your Mac, you don't want to keep a terminal open — you want to monitor progress, approve changes, and receive notifications from your phone.

**GitHub**: github.com/RocYan98/CodexBoard | **Stars**: 115 | **⚠️ No open-source license**

---

### ⚠️ License Warning

CodexBoard has **no LICENSE file**. Without an explicit open-source license, code is "All Rights Reserved" by default — you cannot use it in commercial products, redistribute modified versions, or deploy it in production without explicit author authorization. This article is for technical analysis only.

---

### Core Concept

Codex runs locally on your Mac. You monitor, manage, and approve its work from a mobile browser or Feishu (Lark) app.

The key difference from using terminal or claude.ai directly:
- No need to keep a terminal window open
- Full task state, streaming output, and code diff views on mobile
- Feishu integration means controlling Codex tasks from your work chat
- Dual access points (Web account + Feishu account) can connect to the same local instance simultaneously

---

### Features

**Task Board**: Dashboard, Kanban (drag-and-drop with priority/tags/comments/attachments), List view

**Codex Integration**: Launch Codex directly from task cards, real-time streaming output, inline code diff review + change approval workflow, Git branch and Worktree management

**Mobile Remote** (the core differentiator): Create/continue Codex conversations, view live streaming output, send attachments, review code diffs, approve or reject Codex-proposed changes — all from Feishu or mobile browser

**`taskctl` CLI**: Command-line interface for agents to query and manage tasks (write operations require real user session pairing — agents cannot self-approve)

**Codex Skill**: Installs `manage-codexboard` skill at `~/.agents/skills/manage-codexboard` so Codex can operate the task board via natural language

---

### Architecture

```
Mobile / Web Browser
     ↕  HTTPS
Public frp server (user-provided)
     ↕  frp client (bundled)
Local Mac (Apple Silicon)
├── CodexBoard (TypeScript + SQLite)
│   ├── Caddy (bundled HTTPS server)
│   └── Codex execution binding
└── Local Codex CLI
```

All dependencies are bundled in the `.dmg` (Node.js, Caddy, frpc) — no Docker/Homebrew/Rust required. Data stays local in SQLite.

---

### Installation

Download `CodexBoard-0.1.11-macos-arm64.dmg` from Releases, verify SHA256, drag to Applications. First launch requires right-click → Open to bypass macOS security (no Apple Developer ID signature yet).

Requires three configuration items: frpc.toml (your public frp server), Web account credentials or Feishu App ID+Secret, and a logged-in local Codex CLI.

---

### Limitations

1. **No open-source license**: Biggest compliance concern.
2. **Requires a public frp server**: Non-trivial prerequisite — needs a VPS running frp server.
3. **No project-level permission isolation**: All web accounts share the same board.
4. **No Apple Developer ID**: Security prompts on every upgrade.
5. **0.1.x preview**: 10 releases in one week means breaking changes are likely.
6. **Single contributor**: Sustainability risk.

---

### Bottom Line

The problem CodexBoard solves is real. Mapping Codex task state to a persistent board with mobile notifications is sensible engineering. The "everything in the .dmg" distribution strategy is the right call for user experience. The Feishu integration points at a Chinese-language user audience.

The blocking issues are the absent license and the frp dependency. If the author adds Tailscale or ZeroTier as a tunneling alternative and adds a proper license, this would be significantly more deployable.

> No open-source license — contact the author before using. Technical analysis only.
