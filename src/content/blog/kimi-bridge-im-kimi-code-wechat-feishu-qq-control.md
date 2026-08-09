---
title: "kimi-bridge：用微信/飞书/QQ 控制本地 Kimi Code Agent"
titleEn: "kimi-bridge: Drive a Local Kimi Code Agent from WeChat, Feishu or QQ"
description: "Mtrya 开源的 IM 控制层，Python/MIT。让你从微信、飞书、QQ 或 Telegram 直接操控本地运行的 Kimi Code Agent——持久化会话绑定、流式输出、语音转写、审批/提问交互、权限模式、/goal 目标、/skills 技能、/mcp 工具查看，一行命令安装，支持 Agent 驱动全自动配置。"
descriptionEn: "Mtrya's open-source IM control layer, Python/MIT. Drive a locally running Kimi Code agent from WeChat, Feishu, QQ, or Telegram — persistent session bindings, streaming replies, voice transcription, interactive approvals/questions, permission modes, /goal objectives, /skills, /mcp inspection. One-command install, AI-driven setup."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["KimiCode", "微信机器人", "飞书机器人", "AI编程助手", "IM桥接", "本地Agent", "Mycelium"]
heroImage: "../../assets/images/kimi-bridge-im-kimi-code-wechat-feishu-qq-control-banner.jpg"
---

*by Mycelium Protocol*

---

用手机控制本地跑着的 AI 编程 Agent——这个需求催生了一个小而实用的工具类别。Heinu1 连接微信和 Claude Code，kimi-bridge 做的是同一件事，但对接的是 [Kimi Code](https://github.com/MoonshotAI/kimi-code)，同时多支持了飞书、QQ 和 Telegram。

GitHub: https://github.com/Mtrya/kimi-bridge | MIT License | Python

---

## 支持平台

| 平台 | 状态 |
|------|------|
| **微信私聊** | ✅ 已支持（2026-08-08 live 验证）|
| **飞书单聊** | ✅ 已支持 |
| **QQ 单聊** | ✅ 已支持 |
| **Telegram 私聊** | 🧪 实验性 |
| Linux / macOS / Windows | ✅ 全平台 |
| 语音消息 | ✅ 飞书、QQ、微信均已支持 |

每个 bridge 进程运行一个平台适配器。飞书用官方 `lark-oapi` WebSocket 客户端，其他平台用手写的轻量 `httpx`/`websockets` 传输层，不依赖平台 SDK。

微信限定扫码授权的私聊机器人，强制使用 `auto` 模式，回复不可编辑，不支持群聊和主动推送。可收发图片、语音（转写）、文件、视频。

---

## 核心功能

**会话管理**

```
/new          开启新会话
/sessions     列出所有会话
/switch <n>   切换到第 n 个会话
/status       当前会话信息
/title        重命名会话
/usage        token 用量
/compact      压缩上下文
/undo         撤销上一步
```

**运行控制**

```
/mode         权限模式（auto / manual / supervised 等）
/model        切换模型
/effort       推理强度
/plan         开关规划模式
/goal         设置跨轮次持久目标
/stop         取消当前任务
/restart-server  重启 Kimi 本地服务器
```

**工具与输出**

```
/tasks        任务列表
/skills       技能查看
/mcp          MCP 工具列表（只读）
/send <file>  发送文件
/render-thinking  开关独立思考流输出
```

在任意命令后加 ` ?` 可获取详细用法，例如 `/tasks show ?`。

---

## 快速安装

**最简路径——让 Agent 帮你配**：

```text
阅读 https://github.com/Mtrya/kimi-bridge/blob/main/INSTALL_AI.md 并帮我配置 kimi-bridge。
```

把这行发给任意 CLI Agent（Claude Code、Codex 等），它会问答式完成全部配置。

**手动安装**（需要已登录的 [Kimi Code](https://moonshotai.github.io/kimi-code/en/guides/getting-started) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)）：

```bash
uv tool install 'kimi-bridge'    # 安装所有适配器依赖
# 创建 ~/.kimi-bridge/config.toml，chmod 600
kimi-bridge doctor               # 验证配置（不会启动服务）
kimi-bridge                      # 运行
```

---

## 架构

```
微信 / 飞书 / QQ / Telegram
          │
          ▼
   语义路由层（chat router）
          │
          ▼
  受监管的本地 kimi web 进程
```

Kimi 本地服务器绑定回环地址（loopback），使用随机生成的 bearer token，聊天端通过适配器白名单限制访问。一次机器人授权对应一个轮询进程。

安全说明：Kimi Agent 以宿主账户权限读写和执行，kimi-bridge 设计给单一受信操作者使用，不适用于多租户场景。

---

## 与 Heinu1 的对比

| 维度 | Heinu1 | kimi-bridge |
|------|--------|-------------|
| 后端 Agent | Claude Code | Kimi Code |
| 平台 | 微信 | 微信 / 飞书 / QQ / Telegram |
| 语言 | TypeScript | Python |
| 会话恢复 | `--resume` session ID | `/switch` + 持久绑定 |
| 语音 | 微信已支持 | 飞书/QQ/微信均支持 |
| 安装 | npm + launchd | uv tool install |

两者在核心理念上完全一致：把 IM 变成 Coding Agent 的远程控制面板。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## kimi-bridge: Control a Local Kimi Code Agent from WeChat, Feishu, or QQ

*by Mycelium Protocol*

---

Using your phone to drive a locally running AI coding agent is a small but useful category. Heinu1 connects WeChat to Claude Code; kimi-bridge does the same thing but targets [Kimi Code](https://github.com/MoonshotAI/kimi-code), and additionally supports Feishu, QQ, and Telegram.

GitHub: https://github.com/Mtrya/kimi-bridge | MIT License | Python

---

### Platform Support

| Surface | Status |
|---------|--------|
| **WeChat DM** | ✅ Supported (live-validated 2026-08-08) |
| **Feishu DM** | ✅ Supported |
| **QQ DM** | ✅ Supported |
| **Telegram private chat** | 🧪 Experimental |
| Linux / macOS / Windows | ✅ All platforms |
| Voice messages | ✅ Feishu, QQ, WeChat |

One bridge process, one platform adapter. Feishu uses the official `lark-oapi` WebSocket client; other platforms use handwritten lightweight `httpx`/`websockets` transports with no platform SDK dependency.

WeChat is QR-authorized, private-chat-only. Replies are immutable (no edits), no groups, no proactive delivery. Accepts inbound image/voice/file/video; outbound voice is a generic downloadable file, not a native voice message.

---

### Commands

**Session management:**
```
/new          start a new session
/sessions     list sessions
/switch <n>   switch to session n
/status       current session info
/compact      compact context window
/undo         undo last step
```

**Control:**
```
/mode         permission mode (auto / manual / supervised …)
/model        switch model
/effort       reasoning intensity
/goal         set a cross-turn persistent objective
/stop         cancel current task
```

**Tools and output:**
```
/skills       view available skills
/mcp          inspect MCP tools (read-only)
/send <file>  send a file
/render-thinking  toggle thinking stream output
```

Append ` ?` to any command for detailed in-chat help, e.g. `/tasks show ?`.

---

### Quick Start

**Easiest path — let an agent configure it for you:**

```text
Read https://github.com/Mtrya/kimi-bridge/blob/main/INSTALL_AI.md and help me configure kimi-bridge.
```

Send this to any CLI agent (Claude Code, Codex, etc.) and it will interview you and run the full setup end to end.

**Manual install** (requires authenticated [Kimi Code](https://moonshotai.github.io/kimi-code/en/guides/getting-started) and [uv](https://docs.astral.sh/uv/getting-started/installation/)):

```bash
uv tool install 'kimi-bridge'    # install all adapter dependencies
# create ~/.kimi-bridge/config.toml, chmod 600
kimi-bridge doctor               # validate without starting anything
kimi-bridge                      # run
```

---

### Architecture

```
WeChat / Feishu / QQ / Telegram
            │
            ▼
     semantic chat router
            │
            ▼
  supervised local kimi web process
```

The managed Kimi server binds to loopback with a generated bearer token; chat access is restricted by the adapter's allowlist. One bot authorization must have exactly one poller.

**Security note:** Kimi Code runs with the host account's permissions. kimi-bridge is designed for a single trusted operator — protect both host and chat credentials.

---

### Compared to Heinu1

| | Heinu1 | kimi-bridge |
|--|--------|-------------|
| Backend | Claude Code | Kimi Code |
| Platforms | WeChat | WeChat / Feishu / QQ / Telegram |
| Language | TypeScript | Python |
| Install | npm + launchd | `uv tool install` |
| Session restore | `--resume` session ID | `/switch` + persistent binding |

Same core idea: turn your IM client into a remote control panel for a local coding agent.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
