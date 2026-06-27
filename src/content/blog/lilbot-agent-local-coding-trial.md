---
title: "LilBot-agent 试用手记：用 Python 把本地 AI 塞进一个全屏驾驶舱"
titleEn: "LilBot-agent Trial: Python-powered Local AI Agent with a Full-Screen Flight Deck"
description: "LilBot-agent 是纯 Python 开源本地编码 Agent，Windows 优先，原生适配 DeepSeek 等 OpenAI 兼容模型，内置全屏 TUI 驾驶舱、多子代理/Team 协作、五层权限沙箱、持久化记忆、MCP 外部工具对接，153 Stars，本文从开发者试用视角逐层拆解。"
descriptionEn: "LilBot-agent is a pure-Python open-source local coding agent, Windows-first, natively compatible with DeepSeek and OpenAI-compatible APIs. Features a full-screen TUI flight deck, multi-agent team collaboration, five-gate permission sandbox, persistent memory, and MCP tool integration. 153 Stars — developer trial walkthrough."
pubDate: "2026-06-27"
updatedDate: "2026-06-27"
category: "Tech-News"
tags: ["本地Agent", "AI编程", "DeepSeek", "MCP", "Python", "多智能体", "Windows", "开源工具"]
heroImage: "../../assets/images/lilbot-agent-local-coding-trial-banner.jpg"
---

> **一句话结论（BLUF）**：LilBot-agent 不是要取代 Claude Code——它是一个从头实现 Agent 运行时的学习型项目，但已经具备了真正可用的核心：多层权限沙箱、子代理/Team 协作、MCP 外部工具、持久化记忆、以及一个让人印象深刻的全屏 TUI 驾驶舱。Windows 开发者想在本地跑 DeepSeek 写代码，这是目前最完整的开源选项之一。

GitHub：https://github.com/terrense/LilBot-agent  
⭐ 153 Stars · 纯 Python · Windows 优先 · DeepSeek-ready · 2026-06

---

## 为什么会有 LilBot-agent？

国内 Windows 开发者用 AI 写代码有几个痛点：

- Claude Code 不支持 Windows（官方），Docker 方案折腾成本高；
- Cursor/Windsurf 是 GUI，不适合 SSH 远程、无头服务器场景；
- 本地 DeepSeek API 接入各种工具普遍体验参差不齐；
- 大多数 Python Agent 框架是"空壳"——架构图好看，实际跑起来什么都没有。

LilBot-agent 作者 terrense 的定位是：**本地代码实验室，Windows Terminal 即驾驶舱**。README 里有一句话说得坦诚：`LilBot is now past the empty-shell stage`（已经不是空壳了）——这种措辞本身就说明项目在认真干。

当前基线：`pytest` 跑出 **109 passed, 6 skipped**，核心功能有测试覆盖。

---

## 快速安装与第一次启动（Windows）

### 环境要求

- Python 3.10+（作者在 Windows 下用 conda，3.10.20 测试通过）
- Windows Terminal + Cascadia Mono 或 JetBrains Mono（保证 TUI 框线正确渲染）

### 安装步骤

```powershell
# 克隆仓库
git clone https://github.com/terrense/LilBot-agent
cd LilBot-agent

# 激活 conda 环境（或用 venv）
conda activate LilBot

# 安装依赖
pip install -r requirements.txt
pip check

# 启动（默认全屏 TUI 模式）
python -m lilbot
```

如果框线或中文显示乱码，先强制 UTF-8：

```powershell
chcp 65001
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
python -m lilbot
```

调试时可用 Rich 传统界面：

```powershell
python -m lilbot --classic
```

### 配置 DeepSeek

在项目根目录创建 `.env`（已加入 `.gitignore`，不会提交）：

```env
DEEPSEEK_API_KEY=sk-你的key
LILBOT_PROVIDER=deepseek
LILBOT_MODEL=deepseek-v4-flash
LILBOT_BASE_URL=https://api.deepseek.com
```

或直接命令行传参：

```powershell
$env:DEEPSEEK_API_KEY="sk-..."
python -m lilbot --provider deepseek --model deepseek-v4-flash
```

一句话验证是否接通：

```powershell
python -m lilbot --provider deepseek --model deepseek-v4-flash --print "Reply exactly: LilBot OK"
```

LilBot 原生支持 **OpenAI 兼容接口**，任何兼容 `/v1/chat/completions` 的模型（本地 Ollama、Groq、Together 等）均可接入。

---

## 第一眼：Flight Deck 全屏驾驶舱

这是 LilBot 最有辨识度的部分。启动后你看到的不是对话框，而是一个 `prompt_toolkit` 驱动的全屏面板：

```text
┌──────────────────────────────────────────────────────────────┐
│ Agent LilBot-agent-code - deepseek-v4-flash     ready  v0.1  │
├──────────────────────┬───────────────────────────────────────┤
│                      │                                       │
│    L I L B O T       │   Work / Tool Stream                  │
│  local coding agent  │   permissions / memory                │
│                      │   subagents / mcp                     │
├──────────────────────┴───────────────────────────────────────┤
│ Composer: write a task, use /, or run ! command safely        │
└──────────────────────────────────────────────────────────────┘
```

三个核心区域：

- **Trace 面板（左/主）**：完整的对话流 + 工具执行日志
- **Work 面板（F5）**：运行时状态——当前工具调用、子代理状态、Transcript handle、Worktree 分支
- **Composer（底部）**：输入框，支持斜杠命令、`!` 直接执行 Shell 命令、右键粘贴/Ctrl+V

顶部状态栏实时显示 `ctx 03%` 等 token 使用率，模型推理时底部有波浪动画。中文内容用 `F2` 或 `/copy` 复制——Windows 下写入 `CF_UNICODETEXT` 格式，不会出现粘贴乱码。

---

## 核心：Agent Loop

LilBot 的 Agent 循环是标准的 **reason → tool → observe → continue** 模式：

1. 用户发送 prompt 或斜杠命令
2. Agent 发送 messages + tool schemas 给 Provider（DeepSeek/OpenAI 兼容）
3. Provider 返回文字或 tool call
4. 如果是 tool call → 走 **Tool Registry → Permission Gate → Workspace Sandbox** 链路
5. 结果注入 observation，继续下一轮推理
6. 直接回答时返回到 TUI

```
User → TUI → Agent Loop → Provider
                       ↓
                Tool Registry
                       ↓
             Permission Gate (ask / accept-all / deny-all)
                       ↓
               Workspace Sandbox (path + shell boundary)
                       ↓
                 Workspace Files
```

每一步都有日志落盘（`.lilbot/` 目录），支持任务断点恢复。

---

## 安全体系：五层权限沙箱

这是 LilBot 认真对待的部分，不是花架子。

### Permission Gate（三种模式）

| 操作类型 | 行为 |
|---|---|
| 读取/列目录/搜索 | 无需审批，直接执行 |
| 写入/编辑/Shell 命令 | 弹出审批 |

审批选项：`y`（允许一次）/ `a`（始终允许）/ `n`（拒绝一次）/ `d`（始终拒绝）

用 `/permissions accept-all` 可切换到全自动模式（CI/批量场景）；`/permissions deny-all` 进入只读沙盒。

### Workspace Sandbox（路径边界）

所有文件操作限定在项目工作区内，无法逃逸到上级目录——这是 Agent 跑代码时最重要的安全边界。

### PowerShell 安全分析器

Windows 下的 Shell 执行会先经过一个安全分析器，检测：

- 分隔符 / 重定向
- 子进程启动 / 后台任务
- 危险命令分类（`rm -rf` 等效命令）
- 不安全的 delete/move 目标

高危操作必须人工确认，阻止 Agent 意外删文件。

### 子代理五门限制

自定义子代理创建时走 **5 道安全门**：前 3 道在创建阶段阻止不安全配置，后 2 道在运行时拦截越权工具调用并写入 transcript 证据。

### 规划审批流程（Plan Mode）

高危写入/执行操作可以先走规划模式：

```
/plan 重构 auth.py 的认证逻辑
```

进入 Plan Mode 后，写操作被冻结，等待审批：

```
/do approved   # 批准执行
/do rejected   # 拒绝计划
```

---

## 子代理与 Team 协作

### 一次性子代理（Subagents）

内置 4 种角色：`coder`、`reviewer`、`researcher`、`planner`。

可以直接在 Composer 里：

```
/agent reviewer 检查 auth.py 的错误处理是否完整
```

子代理有独立的 `allowed_tools` 白名单（Claude 风格的 `Read`、`Grep` 等工具名），运行完销毁，transcript 持久化到 `.lilbot/subagent-transcripts/`。

支持**并发限流**：可配置同时运行的最大子代理数，超出排队等待。

### 长期协作 Team（多智能体）

这是 LilBot 区别于一般 Agent 框架的关键：**Teammates 是常驻的，有邮箱，能互发消息**。

```mermaid 
Lead 创建 Team → 派生 impl（实现者）和 rev（审查者）
impl 完成工作 → send_message to=lead → 进入 idle 等待
rev 完成审查 → send_message to=lead → 进入 idle 等待
Lead 在下一个 agent-loop turn 收到 <team-notification>，汇总结果
```

Team 状态存在 `.lilbot/teams/<slug>/`：

- `config.json` — team 成员配置
- `tasks.json` — 共享任务看板（含 blocks/blocked_by 依赖关系）
- `mailbox/<name>.json` — 每个 Teammate 的专属收件箱（文件锁保护并发安全）

Team 相关斜杠命令：

```
/team list                  # 查看所有 Team、成员状态、最近活动
/team new bugfix            # 创建 Team
/team msg impl "开始修复"    # 唤醒 impl 并发消息
/team rm bugfix             # 删除 Team
```

**Worktree 隔离**（可选）：创建 Teammate 时传 `isolation: "worktree"`，该 Teammate 获得独立 Git worktree，并发写文件不冲突，Lead 审查后合并。

---

## Skills：Markdown 提示词胶囊

Skills 是预定义的 Markdown 文件，每个 Skill 包含结构化的提示词和元数据，直接影响 Agent 行为。

内置示例：`review.md`、`plan.md`、`commit.md`、`summarize.md`

查看和运行：

```
/skills                      # 列出所有 Skills
/skill review 检查最近的改动    # 加载 skill 并发送给 Agent
```

自定义 Skill：在 `.lilbot/skills/` 目录下放置 `SKILL.md`，支持 Claude 风格 frontmatter、工具白名单、模型 hint。

---

## MCP 外部工具接入

在项目根目录放 `.lilbot/mcp.json`，即可接入任何 MCP 服务器：

```json
{
  "servers": {
    "filesystem": { "command": "mcp-server-filesystem", "args": ["."] },
    "browser":    { "command": "mcp-server-playwright" },
    "custom":     { "command": "python", "args": ["my_mcp_server.py"] }
  }
}
```

接入后，Agent 可以通过 `mcp_call(server, tool, args)` 调用外部工具，结果直接注入 Agent Loop。

查看当前配置：

```
/mcp
```

---

## 持久化记忆

LilBot 用 JSONL 格式持久化项目记忆（`.lilbot/memory/`），支持搜索和删除：

```
/memory save "auth 模块使用 JWT，token 有效期 24h"
/memory search "auth"
/memory list
/memory delete <id>
```

Agent 在推理时会自动注入相关记忆作为上下文，避免每次重复告知背景信息。

---

## LSP 代码导航

LilBot 实现了 LSP Phase 2，支持：

- `lsp_symbols` — 列出文件中的符号
- `lsp_definition` — 跳转到定义
- `lsp_workspace_symbols` — 全局符号搜索
- `lsp_references` — 查找引用
- `lsp_diagnostics` — 获取错误/警告
- `lsp_rename_preview` — 重命名预览

当系统安装了对应 LSP Server（如 `pylsp`、`rust-analyzer`）时直接接入；否则自动降级到 Python AST 解析 + regex 搜索 + grep 证据组合，基本功能不缺失。

---

## 完整斜杠命令参考

| 命令 | 类型 | 说明 |
|---|---|---|
| `/help [command]` | 本地 | 查看所有命令或单个命令详情 |
| `/clear` | UI | 清空 Trace，重置对话 |
| `/copy` / `F2` | UI | 复制 Trace 到剪贴板（Windows Unicode）|
| `/model [flash\|pro]` | 本地 | 查看/切换 DeepSeek 模型 |
| `/tools` | 本地 | 列出已注册的所有工具 |
| `/skills` | 本地 | 列出所有 Skills |
| `/skill NAME ARGS` | Prompt | 加载 Skill 并送入 Agent |
| `/memory list/search/save/delete` | 本地 | 管理持久化记忆 |
| `/agents` | 本地 | 列出子代理类型和任务 |
| `/agent TYPE PROMPT` | 本地 | 运行指定子代理 |
| `/mcp` | 本地 | 查看 MCP 服务器配置 |
| `/permissions ask/accept-all/deny-all` | 本地 | 切换权限模式 |
| `/tokens` | 本地 | 显示 token/上下文用量 |
| `/plan [task]` | UI/Prompt | 进入规划模式 |
| `/do [approved\|rejected]` | UI | 退出规划模式，持久化审批结果 |
| `/review [focus]` | Prompt | 审查当前 git diff |
| `/team list/new/msg/rm` | 本地 | 管理 Team 协作 |
| `/display` | 本地 | 终端和字体诊断 |
| `/exit` | UI | 退出 |

---

## 开发者视角：现阶段的真实评估

### 已经可以用的

- ✅ 全屏 TUI 驾驶舱，体验有明显差异感
- ✅ DeepSeek/OpenAI 兼容 API 接入稳定
- ✅ 权限沙箱设计完整，安全边界清晰
- ✅ Team 协作框架理念超前，多 Teammate 并发有实用价值
- ✅ MCP 接入开箱即用，.lilbot/mcp.json 简洁
- ✅ 109 个测试通过，核心功能有回归保护

### 还在早期阶段的

- ⚠️ Windows 优先，macOS/Linux 未经充分测试
- ⚠️ LSP 降级模式（无 LSP Server 时）覆盖有限
- ⚠️ Plan Mode 的 TUI 审批交互体验待完善
- ⚠️ 仓库无 License 声明（截至 2026-06）

### 适合谁用

| 场景 | 推荐程度 |
|---|---|
| Windows + DeepSeek 本地开发 | ⭐⭐⭐⭐⭐ |
| Agent 框架学习 / 二次开发 | ⭐⭐⭐⭐⭐ |
| 批量工程自动化（服务器端无头）| ⭐⭐⭐⭐ |
| macOS / Linux 日常使用 | ⭐⭐⭐（可用，非主场）|
| 生产级关键任务代码 | ⭐⭐（仍在快速迭代）|

---

## 源码值得一读的部分

- `lilbot/core/agent.py` — Agent Loop 实现，干净的 reason-tool-observe 循环
- `lilbot/subagents/manager.py` — 子代理管理 + 五门安全校验，多进程协调范本
- `lilbot/tui/dashboard.py` — prompt_toolkit 全屏面板实现，学 TUI 的好素材
- `lilbot/sandbox/permissions.py` — 细粒度权限状态机

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: LilBot-agent isn't trying to replace Claude Code — it's a from-scratch Agent runtime built as a learning project that has grown into something genuinely usable: a layered permission sandbox, subagent/Team collaboration, MCP external tools, persistent memory, and an impressive full-screen TUI flight deck. For Windows developers running DeepSeek locally for coding, it's one of the most complete open-source options available.

GitHub: https://github.com/terrense/LilBot-agent  
⭐ 153 Stars · Pure Python · Windows-first · DeepSeek-ready · 2026-06

---

## Why Does LilBot-agent Exist?

Windows developers working with AI code assistants face a specific set of problems:

- Claude Code has no official Windows support; Docker workarounds add friction
- Cursor/Windsurf are GUI-based — not suitable for SSH remotes or headless servers
- DeepSeek API integration quality varies across tools
- Most Python Agent frameworks are shells — great architecture diagrams, nothing that actually runs

LilBot-agent's author (`terrense`) positioned it as: **a local code lab, with Windows Terminal as the flight deck**. The README makes an honest statement: `LilBot is now past the empty-shell stage` — a phrase that itself signals the project is taking itself seriously.

Current baseline: `pytest` shows **109 passed, 6 skipped**.

---

## Installation & First Run (Windows)

### Requirements

- Python 3.10+ (tested on 3.10.20 via conda on Windows)
- Windows Terminal + Cascadia Mono or JetBrains Mono (for correct TUI box-drawing)

### Steps

```powershell
git clone https://github.com/terrense/LilBot-agent
cd LilBot-agent
conda activate LilBot
pip install -r requirements.txt
pip check
python -m lilbot
```

If box characters or Chinese text render incorrectly, force UTF-8 first:

```powershell
chcp 65001
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
python -m lilbot
```

Classic debug mode (Rich fallback):

```powershell
python -m lilbot --classic
```

### DeepSeek Config

Create `.env` in the project root (already `.gitignore`d):

```env
DEEPSEEK_API_KEY=sk-your-key
LILBOT_PROVIDER=deepseek
LILBOT_MODEL=deepseek-v4-flash
LILBOT_BASE_URL=https://api.deepseek.com
```

Quick connectivity test:

```powershell
python -m lilbot --provider deepseek --model deepseek-v4-flash --print "Reply exactly: LilBot OK"
```

Any OpenAI-compatible endpoint works — Ollama, Groq, Together, or a local inference server.

---

## The Flight Deck TUI

LilBot's most distinctive feature. Instead of a chat box, you get a `prompt_toolkit` full-screen panel:

```text
┌────────────────────────────────────────────────────────────┐
│ Agent LilBot-agent-code - deepseek-v4-flash   ready  v0.1  │
├───────────────────────┬────────────────────────────────────┤
│                       │                                    │
│    L I L B O T        │   Work / Tool Stream               │
│  local coding agent   │   permissions / memory             │
│                       │   subagents / mcp                  │
├───────────────────────┴────────────────────────────────────┤
│ Composer: write a task, use /, or run ! commands safely     │
└────────────────────────────────────────────────────────────┘
```

Three zones:

- **Trace panel (main)**: Full conversation + tool execution log
- **Work panel (F5)**: Runtime status — current tool call, subagent state, transcript handles, worktree branch
- **Composer (bottom)**: Input with slash command support, `!` for direct shell, right-click/Ctrl+V paste

Top bar shows real-time `ctx 03%` token usage; a wave animation plays during model inference. `/copy` or `F2` uses `CF_UNICODETEXT` on Windows — Chinese text pastes cleanly.

---

## Security: Five-Layer Sandbox

### Permission Gate

| Action type | Behavior |
|---|---|
| Read / list / search | Auto-allowed, no prompt |
| Write / edit / shell | Requires approval |

Options: `y` (once) / `a` (always allow) / `n` (deny once) / `d` (always deny)

Switch modes with `/permissions ask` (default), `accept-all` (CI/batch), or `deny-all` (read-only audit).

### Workspace Sandbox

All file operations are path-bounded to the project workspace. No escaping to parent directories.

### PowerShell Safety Analyzer

Windows shell execution passes through a safety analyzer that classifies:
- Separators, redirections, subprocess boundaries
- Background job launches
- Destructive command detection (rm equivalents, unsafe delete/move targets)

High-risk operations require manual confirmation.

### Subagent Five-Gate Validation

Custom subagent creation runs 5 security gates: gates 1–3 reject unsafe configurations at creation time; gates 4–5 deny unauthorized tool calls at runtime and record transcript evidence.

### Plan Mode Approval Flow

```
/plan refactor auth.py authentication logic
```

Write and execution tools are frozen until approval:

```
/do approved   # approve and execute
/do rejected   # discard the plan
```

---

## Subagents and Team Collaboration

### One-Shot Subagents

Four built-in roles: `coder`, `reviewer`, `researcher`, `planner`.

```
/agent reviewer check error handling in auth.py
```

Each subagent has an `allowed_tools` allowlist (Claude-compatible tool names), runs to completion, then terminates. Transcripts persist under `.lilbot/subagent-transcripts/`. Concurrency cap configurable — excess subagents queue.

### Long-Running Teams (Multi-Agent)

Teammates persist across turns, have mailboxes, and can message each other:

```
Lead creates team → spawns impl + rev
impl completes → send_message to=lead → goes idle
rev completes → send_message to=lead → goes idle
Lead drains mailbox at next turn → collects results as <team-notification>
```

Team state under `.lilbot/teams/<slug>/`: `config.json`, `tasks.json` (with `blocks`/`blocked_by` dependencies), `mailbox/<name>.json` (file-locked, concurrency-safe).

**Worktree isolation** (optional): pass `isolation: "worktree"` when spawning a teammate — it gets its own git worktree, writes can't reach the main tree until the lead merges.

---

## MCP Tool Integration

Drop a `.lilbot/mcp.json` in the project root:

```json
{
  "servers": {
    "filesystem": { "command": "mcp-server-filesystem", "args": ["."] },
    "browser":    { "command": "mcp-server-playwright" },
    "custom":     { "command": "python", "args": ["my_mcp_server.py"] }
  }
}
```

The Agent calls `mcp_call(server, tool, args)` and receives results back into the loop. Check configured servers with `/mcp`.

---

## Persistent Memory

```
/memory save "auth module uses JWT, token TTL is 24h"
/memory search "auth"
/memory list
/memory delete <id>
```

Memory persists as JSONL under `.lilbot/memory/`. Relevant entries are auto-injected into agent context — no need to repeat project background on every session.

---

## Developer Assessment

### What works now

- ✅ Full-screen TUI with genuine differentiation from plain chat
- ✅ DeepSeek/OpenAI-compatible API integration, stable
- ✅ Permission sandbox design complete with clear security boundaries
- ✅ Team collaboration framework — multi-teammate concurrency with real-world value
- ✅ MCP integration via `.lilbot/mcp.json`, zero extra config
- ✅ 109 tests passing — core paths have regression coverage

### Still early

- ⚠️ Windows-first; macOS/Linux not fully tested
- ⚠️ LSP fallback (when no LSP server installed) has limited coverage
- ⚠️ Plan Mode approval UX in TUI needs polish
- ⚠️ No license declared in repo (as of June 2026)

### Who should try it

| Use case | Rating |
|---|---|
| Windows + DeepSeek local development | ⭐⭐⭐⭐⭐ |
| Agent framework study / fork and extend | ⭐⭐⭐⭐⭐ |
| Headless batch automation on a server | ⭐⭐⭐⭐ |
| macOS / Linux daily use | ⭐⭐⭐ (works, not the primary target) |
| Production-critical code | ⭐⭐ (still rapidly iterating) |

---

## FAQ

**Q: Does it work without DeepSeek? Can I use local Ollama?**  
Yes. Any OpenAI-compatible endpoint works. Set `LILBOT_BASE_URL=http://localhost:11434/v1` and point to your Ollama model.

**Q: Can I run it on macOS or Linux?**  
The Python code is not inherently Windows-only, but the author tests and optimizes for Windows Terminal. TUI rendering and shell execution should work on macOS/Linux, though some PowerShell-specific features degrade gracefully.

**Q: What's the difference between subagents and teammates?**  
Subagents are one-shot: spawn, run, collect result, terminate. Teammates are long-running: they stay alive, poll a mailbox, and respond to messages across multiple turns — suitable for genuine multi-agent workflows where agents need to coordinate asynchronously.

**Q: Is there a hosted version or cloud option?**  
No. LilBot is fully local, zero cloud dependency. Your code and API keys stay on your machine.

**Q: The README mentions `--real` flag in the teams demo — what's that?**  
`python experiment/teams_demo.py` runs a stub with no network. `--real` uses your actual DeepSeek API key to run a live multi-agent demo. Good for verifying the Team coordination works end-to-end.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
