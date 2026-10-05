---
title: "OpenHands：从编程 Agent 到多 Agent 自托管控制台的演进"
titleEn: "OpenHands: From Coding Agent to Multi-Agent Self-Hosted Control Center"
description: "OpenHands/OpenHands（前 All-Hands-AI/OpenHands，前身 OpenDevin），MIT，90,029 stars，TypeScript，2024-03-13。已从单一编程 Agent 演进为「Agent Canvas」——自托管的开发者控制中心，通过 ACP（Agent-Client Protocol）协议接入 OpenHands 本体、Claude Code、Codex、Gemini 等任意兼容 Agent。核心架构拆分为四个独立仓库：Agent Canvas 前端、Python Agent Server SDK、TypeScript 客户端、Automation 调度服务。支持本地/Docker/VM/云端多后端切换，内置 webhook 触发、定时调度、Slack/GitHub/Linear 集成自动化流水线。"
descriptionEn: "OpenHands/OpenHands (formerly All-Hands-AI/OpenHands, originally OpenDevin), MIT, 90,029 stars, TypeScript, 2024-03-13. Evolved from a single coding agent into 'Agent Canvas' — a self-hosted developer control center that connects OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent through the Agent-Client Protocol. Core architecture split across four repos: Agent Canvas frontend, Python Agent Server SDK, TypeScript client, Automation scheduling service. Supports local/Docker/VM/cloud backend switching with webhook triggers, cron scheduling, Slack/GitHub/Linear integration automations."
pubDate: 2026-10-05
heroImage: "../../assets/images/openhands-ai-software-development-agent-allhands-banner.jpg"
category: "Tech-Experiment"
tags: ["AI代理", "编程Agent", "自托管", "开源工具", "ACP协议", "自动化"]
lang: "zh-CN"
wechatTitle: "OpenHands：编程Agent变身多Agent控制台"
wechatDigest: "MIT 9万星；前OpenDevin；ACP接Claude Code/Codex；自动化+自托管"
---

2024 年初，一个名叫 OpenDevin 的项目出现了：给 AI 装上一个类人的开发环境，让它能像人类工程师一样写代码、跑测试、提交 PR。它的定位很清晰——复刻 Devin（第一个宣称 AI 软件工程师的商业产品），但开源、免费、自托管。

两年后，这个项目已经改名两次（OpenDevin → OpenHands，All-Hands-AI → OpenHands 组织），积累了 9 万颗星，然后做了一件出乎意料的事：把自己从「一个编程 Agent」变成了「多个编程 Agent 的控制台」。

GitHub: https://github.com/OpenHands/OpenHands | ⭐ 90,029 | MIT | TypeScript

---

## 现在是什么：Agent Canvas

最新版本的核心产品叫 **Agent Canvas**——一个自托管的开发者控制中心。官方定位的变化很能说明问题：

> "Run OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local, remote, and cloud backends."

这意味着 OpenHands 不再只是它自己的 Agent，而是变成了一个可以管理任意 Agent 的平台。背后的协议是 **ACP（Agent-Client Protocol）**，OpenHands 的 Agent Server 实现了它，Claude Code、Codex 等第三方 Agent 也可以通过 ACP 接入同一个 Canvas 界面。

几个核心能力：
- **多后端切换**：同一个 Canvas 前端可以连接多个 Agent Server（本地、Docker、VM、云端），在 UI 里切换而不需要重新配置
- **自动化工作流**：可以设置在 Slack 消息触发/GitHub Issue 创建/cron 调度时自动跑 Agent，结果发回 Slack、更新 GitHub
- **对话持久化**：在 Docker 模式下，每个对话独立容器，workspace 文件和对话历史在容器重建后仍然保留

---

## 四仓库架构

OpenHands 把原来的单体拆成了四个独立仓库：

| 仓库 | 职责 |
|------|------|
| `OpenHands/OpenHands` | Agent Canvas 前端 + 本地栈编排 + 后端选择 |
| `OpenHands/software-agent-sdk` | Python SDK + Agent Server + Agent 本体 + 工具 + 对话/工作区管理 |
| `OpenHands/typescript-client` | 浏览器兼容的 Agent Server API TypeScript 客户端 |
| `OpenHands/automation` | 自动化定义、调度、webhook、运行历史、任务分发 |

实际的 AI 推理代码（Agent 本体、工具调用、代码执行）在 `software-agent-sdk`；Canvas 只负责前端呈现和本地栈的启动协调；`automation` 服务决定什么时候运行、分发到哪个 Agent Server。

---

## 安装选项

**选项一：不带沙盒（最简单，但 Agent 能访问你整个文件系统）**

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

需要 Node.js 24+。Agent 会直接运行在你的机器上，没有隔离。

**选项二：Docker 沙盒（推荐本地使用）**

```bash
export PROJECTS_PATH="$HOME/projects"
mkdir -p "$PROJECTS_PATH" "$HOME/.openhands"

docker run -it --rm \
  -p 127.0.0.1:8000:8000 \
  -e AGENT_CANVAS_ALLOW_LAN_SESSION_KEY=true \
  -v "$HOME/.openhands:/home/openhands/.openhands" \
  -v "${PROJECTS_PATH}:/projects" \
  ghcr.io/openhands/agent-canvas:1.24.0
```

Agent 只能访问 `PROJECTS_PATH` 下的项目目录。注意 `AGENT_CANVAS_ALLOW_LAN_SESSION_KEY=true` 配合 `127.0.0.1` 绑定使用；如果暴露到局域网或公网，去掉这个环境变量，改用 UI 里的 API Key 认证。

**选项三：多 Docker 沙盒（并发多 Agent）**

```bash
npm install -g @openhands/agent-canvas
OH_CONVERSATION_RUNTIME=docker agent-canvas
```

每个新对话在独立 Docker 容器里运行，有独立的 Agent Server。容器之间互相隔离，适合同时跑多个独立任务。

**选项四：从源码启动**

```bash
git clone https://github.com/OpenHands/OpenHands.git
cd OpenHands && npm install && npm run dev
```

本地监听默认绑定 `127.0.0.1`（loopback only），不能从局域网访问。要监听所有接口加 `--host 0.0.0.0`，但这会关闭会话 key 的自动注入，改为 API Key 认证。

---

## 自动化：让 Agent 不需要人手动触发

这是 Agent Canvas 相比原版 OpenDevin 最重要的新能力。

Automation Server（`OpenHands/automation`）可以配置：
- **webhook 触发**：GitHub Issue 新建、Slack 消息匹配关键词时，自动启动一个对话
- **定时调度**：每天定时生成报告、运行测试、检查依赖更新
- **第三方集成**：和 Slack、GitHub、Linear、Notion 等连通，自动把结果写回去

典型场景：GitHub 仓库里新建了 bug 报告 → automation 服务捕获 webhook → 自动启动 OpenHands Agent → Agent 读 issue、复现、提 PR → 结果通知 Slack。

---

## ACP 的意义

ACP（Agent-Client Protocol）是 OpenHands 团队推动的 Agent 通信标准。它的作用是让 Canvas 和 Agent Server 之间有标准化的 REST API 合约，这样 Claude Code、Codex 或者你自己写的 Agent 都可以作为 Agent Server 接入同一个 Canvas 前端。

这比"让一个 Agent 调用另一个 Agent"更基础——它解决的是前端控制台怎么管理多个异构 Agent 后端的问题。对用户来说，一个 UI 统一管理多种 Agent，不用为每个 Agent 单独开一个终端。

---

## 自托管安全注意事项

README 里有明确的警告，重点摘录：

1. **不带沙盒的安装（选项一/四）**：Agent 有你整个文件系统的完整访问权，适合单人、私有机器，不适合共享服务器
2. **Docker 绑定接口**：默认 `127.0.0.1`（loopback），绑到 `0.0.0.0` 前确保你理解 API Key 认证流程
3. **公网暴露**：参考 `docs/SELF_HOSTING.md` 的安全加固指南，最起码需要 HTTPS 反向代理和强 API Key
4. **Docker 里的 `AGENT_CANVAS_ALLOW_LAN_SESSION_KEY`**：只在可信网络内配合 `127.0.0.1` 绑定使用，局域网/公网部署去掉它

---

> MIT 开源。9 万颗星，前身 OpenDevin（2024-03），All-Hands AI 维护，现组织名称 OpenHands。开源仅供学习参考。

---

<!--EN-->

## OpenHands: From Coding Agent to Multi-Agent Self-Hosted Control Center

In early 2024, OpenDevin appeared as an open-source, self-hosted attempt to replicate Devin (the first AI software engineer product). Two years and two name changes later (OpenDevin → OpenHands, All-Hands-AI org → OpenHands org), with 90,000+ stars, it has done something unexpected: transformed itself from "a coding agent" into "a control center for managing multiple coding agents."

GitHub: https://github.com/OpenHands/OpenHands | ⭐ 90,029 | MIT | TypeScript

---

### What It Is Now: Agent Canvas

The current product is **Agent Canvas** — a self-hosted developer control center. The key shift is in the positioning:

> "Run OpenHands, Claude Code, Codex, Gemini, or any ACP-compatible agent across local, remote, and cloud backends."

OpenHands no longer only runs its own agent; it's now a platform that manages arbitrary agents via **ACP (Agent-Client Protocol)**. The OpenHands Agent Server implements ACP; Claude Code, Codex, and other third-party agents can join the same Canvas UI through ACP.

Core capabilities:
- **Multi-backend switching**: one Canvas frontend connects to multiple Agent Servers (local, Docker, VM, cloud), switched from the UI without reconfiguration
- **Automation workflows**: trigger agents on Slack messages, GitHub issue creation, or cron schedule; send results back to Slack, update GitHub
- **Conversation persistence**: in Docker mode, each conversation runs in its own container with workspace and conversation history surviving container replacement

---

### Four-Repository Architecture

| Repo | Responsibility |
|------|----------------|
| `OpenHands/OpenHands` | Agent Canvas frontend + local stack orchestration + backend selection |
| `OpenHands/software-agent-sdk` | Python SDK + Agent Server + agent logic + tools + conversation/workspace management |
| `OpenHands/typescript-client` | Browser-compatible TypeScript client for the Agent Server API |
| `OpenHands/automation` | Automation definitions, scheduling, webhooks, run history, dispatching |

Actual AI reasoning (agent logic, tool calls, code execution) lives in `software-agent-sdk`. Canvas handles frontend rendering and local stack startup. The automation service decides when to run and routes to the Agent Server.

---

### Installation

**Option 1 (no sandbox — agent accesses full filesystem)**: `npm install -g @openhands/agent-canvas && agent-canvas` (Node.js 24+)

**Option 2 (Docker sandbox — recommended for local use)**: mount `$HOME/.openhands` and `PROJECTS_PATH` to the `ghcr.io/openhands/agent-canvas:1.24.0` container, bind-publish to `127.0.0.1:8000`.

**Option 3 (multiple Docker sandboxes — concurrent agents)**: set `OH_CONVERSATION_RUNTIME=docker` before `agent-canvas`; each conversation gets its own isolated container.

**Option 4 (from source)**: `git clone` + `npm install` + `npm run dev`, listens on `127.0.0.1` only by default.

---

### ACP Protocol Significance

ACP standardizes the REST API contract between the Canvas frontend and Agent Servers, enabling heterogeneous agent backends (OpenHands agent, Claude Code, Codex, custom) to share one unified management UI. This solves a different problem from "one agent calling another" — it solves how a control plane manages multiple agent backends uniformly.

---

### Self-Hosting Security Notes

- No-sandbox installs: agent has full filesystem access; only for single-user private machines
- Default Docker binding: `127.0.0.1` (loopback); `0.0.0.0` requires proper API key auth
- Public-facing: requires HTTPS reverse proxy + strong API key; follow `docs/SELF_HOSTING.md`
- `AGENT_CANVAS_ALLOW_LAN_SESSION_KEY`: only with `127.0.0.1` binding on a trusted network; remove for LAN/public deployments

---

> MIT. 90,000+ stars, originally OpenDevin (March 2024), maintained by All-Hands AI under the OpenHands org. For technical reference only.
