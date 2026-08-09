---
title: "DeepSeek-Reasonix：围绕前缀缓存稳定性设计的终端编程 Agent"
titleEn: "DeepSeek-Reasonix: A Terminal Coding Agent Designed Around Prefix Cache Stability"
description: "esengine 开源的 DeepSeek 原生终端编程 Agent，33k stars，MIT License，Go 重写版。架构核心是前缀缓存稳定性——真实用户单日 435M 输入 token，99.82% 缓存命中，实际费用 ~$12 而非 ~$61。支持长时运行、QQ 频道远程接入、Tauri 桌面客户端，npm install -g reasonix 一键安装。"
descriptionEn: "esengine's open-source DeepSeek-native terminal coding agent, 33k stars, MIT License, Go rewrite. Architecture is built around prefix-cache stability — real user: 435M input tokens in one day, 99.82% cache hit, ~$12 actual cost vs ~$61 without cache. Supports long-running sessions, QQ channel remote access, Tauri desktop client. npm install -g reasonix."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["编程Agent", "DeepSeek", "前缀缓存", "终端工具", "长任务Agent", "成本优化", "Mycelium"]
heroImage: "../../assets/images/deepseek-reasonix-terminal-coding-agent-prefix-cache-banner.jpg"
---

*by Mycelium Protocol*

---

大多数 AI 编程 Agent 把 DeepSeek 只当一个可切换的 LLM 后端。DeepSeek-Reasonix 从另一个方向出发：**完全围绕 DeepSeek 的前缀缓存机制设计整个 Agent 循环**。

GitHub: https://github.com/esengine/DeepSeek-Reasonix | ⭐ 33,026 | MIT License | Go

---

## 前缀缓存稳定性：架构的核心不变量

DeepSeek 的前缀缓存（prefix cache）在相同前缀下大幅降低 token 成本。但普通 Agent 循环会在每次迭代中插入新内容、重排上下文，破坏前缀稳定性，实际缓存命中率很低。

Reasonix 把前缀缓存稳定性作为**架构不变量**而非可选功能：循环的每一层都经过精心设计以保持前缀字节稳定。这是它为什么只支持 DeepSeek——整个 Agent 架构对 DeepSeek 的字节稳定前缀缓存机制做了深度适配。

**真实数据（2026-05-01，单用户单日）：**

| 指标 | 数值 |
|------|------|
| 输入 token 总量 | 435M |
| 缓存命中率 | **99.82%** |
| 实际花费 | **~$12** |
| 无缓存等价费用 | ~$61 |
| 节省 | **~$49（约 80%）**|

---

## 安装与基本使用

需要 Node.js ≥ 22，支持 macOS / Linux / Windows。

```bash
# 全局安装（日常使用推荐）
npm install -g reasonix
reasonix code my-project   # 首次运行粘贴 DeepSeek API key，自动持久化

# 无需安装，一次性运行
cd my-project
npx reasonix code

# 更短的别名（等价于 reasonix）
npm install -g dsnix
npx dsnix@latest code
```

获取 DeepSeek API key：https://platform.deepseek.com/api_keys

---

## 主要命令

| 命令 | 用途 |
|------|------|
| `reasonix` / `reasonix code [dir]` | 编程 Agent，**首选入口** |
| `reasonix chat` | 纯对话模式，无文件系统/Shell 工具 |
| `reasonix run "task"` | 单次执行，流式输出到 stdout，适合管道 |
| `reasonix doctor` | 健康检查：Node、API key、MCP 接线 |
| `reasonix update` | 自我更新 |

其他子命令（`replay` / `diff` / `events` / `stats` / `index` / `mcp` / `prune-sessions`）见 `reasonix --help`。

---

## QQ 频道远程接入

在正在运行的 `chat` 或 `code` 会话中：

```bash
/qq connect
```

连接后，QQ 消息可以进入当前会话，Assistant 回复路由回 QQ，支持从手机远程跟进长任务。这不是一个独立的运行时模式——它是当前会话流的 QQ 扩展频道。

---

## Tauri 桌面客户端

提供原生 Tauri 桌面客户端（预发布）：多标签，右侧面板显示 Agent 本次会话读写的文件，底部实时 cost/cache/token 指标。同一个 DeepSeek API key 和 `~/.reasonix` 配置，桌面版内置 Node 运行时，无需单独 `npm install`。

- **macOS**：首次启动被 Gatekeeper 拦截 → `xattr -dr com.apple.quarantine /Applications/Reasonix.app`
- **Windows**：SmartScreen 警告 → 点"更多信息 → 仍要运行"
- **Linux**：.deb 和 .AppImage，无额外步骤

---

## Go 重写（main-v2）

当前主开发线已迁移到 Go 重写版（`main-v2` 分支，现为默认分支）。原 TypeScript 版（0.x）处于维护模式，只接受 bug fix，不再添加新功能。Go 版本在性能、启动时间和资源占用上有显著改善，同时保持相同的协议和配置格式（`~/.reasonix`）。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## DeepSeek-Reasonix: A Terminal Coding Agent Built Around Prefix-Cache Stability

*by Mycelium Protocol*

---

Most AI coding agents treat DeepSeek as just another swappable LLM backend. DeepSeek-Reasonix takes the opposite direction: **the entire agent loop is designed around DeepSeek's prefix-cache mechanic**.

GitHub: https://github.com/esengine/DeepSeek-Reasonix | ⭐ 33,026 | MIT License | Go

---

### Prefix-Cache Stability: The Core Invariant

DeepSeek's prefix cache dramatically reduces token costs when the prefix is stable. But typical agent loops insert new content and reorder context on every iteration, destroying prefix stability and producing low cache hit rates in practice.

Reasonix treats prefix-cache stability as an **architectural invariant, not a feature you turn on**: every layer of the loop is engineered to maintain byte-stable prefixes. This is why it's DeepSeek-only — the entire architecture is tuned to DeepSeek's byte-stable prefix-cache mechanic.

**Real user, single day (2026-05-01):**

| Metric | Value |
|--------|-------|
| Input tokens | 435M |
| Cache hit rate | **99.82%** |
| Actual cost | **~$12** |
| Same workload without cache | ~$61 |
| Savings | **~$49 (~80%)** |

---

### Install and Basic Usage

Requires Node.js ≥ 22. Works on macOS · Linux · Windows.

```bash
# Global install (recommended for daily use)
npm install -g reasonix
reasonix code my-project   # paste your DeepSeek API key on first run; it persists

# One-shot without installing
cd my-project
npx reasonix code

# Shorter alias (identical)
npm install -g dsnix
npx dsnix@latest code
```

Get a DeepSeek API key at https://platform.deepseek.com/api_keys

---

### Commands

| Command | When to use |
|---------|-------------|
| `reasonix` / `reasonix code [dir]` | Coding agent. **Start here.** |
| `reasonix chat` | Plain chat — no filesystem or shell tools |
| `reasonix run "task"` | One-shot, streams to stdout. Good for pipes. |
| `reasonix doctor` | Health check: Node, API key, MCP wiring |
| `reasonix update` | Upgrade Reasonix itself |

---

### QQ Channel Remote Access

From inside a running `chat` or `code` session:

```bash
/qq connect
```

Once connected, QQ messages enter the current session, assistant replies route back to QQ, and you can follow up on long-running tasks from your phone. This is a remote channel extension of the current session — not a separate runtime.

---

### Tauri Desktop Client (Prerelease)

A native Tauri desktop app: multi-tab, right panel shows files the agent has read or edited this session, cost/cache/token meters at the bottom. Same API key and `~/.reasonix` config as the CLI — desktop bundles its own Node runtime, no separate `npm install`.

- **macOS**: Gatekeeper blocks first launch → `xattr -dr com.apple.quarantine /Applications/Reasonix.app`
- **Windows**: SmartScreen warns → More info → Run anyway
- **Linux**: `.deb` and `.AppImage`, no extra steps

---

### Go Rewrite (main-v2)

Active development has moved to the Go rewrite on the `main-v2` branch (now the default). The original TypeScript line (0.x) is in maintenance mode — bug fixes only, no new features. The Go version brings meaningful improvements to startup time and resource usage while maintaining the same protocol and config format (`~/.reasonix`).

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
