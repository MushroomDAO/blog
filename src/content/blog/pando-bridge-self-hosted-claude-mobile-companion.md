---
title: "Pando：用自己的机器，养一个真正属于自己的 AI 小伙伴"
titleEn: "Pando: Use Your Own Machine to Raise an AI Companion That's Truly Yours"
description: "Pando Bridge 是一个自托管的 Claude Code 手机网关——跑在你自己的机器上，手机随时访问，记忆可插拔，数据全程不出你的硬盘。这不是又一个套壳 App，它是你和 AI 建立长期关系的基础设施。"
descriptionEn: "Pando Bridge is a self-hosted Claude Code mobile gateway — runs on your own machine, accessible from your phone anywhere, with pluggable memory and data that never leaves your disk. Not another wrapper app; it's the infrastructure for a long-term relationship with AI."
pubDate: "2026-07-13"
updatedDate: "2026-07-13"
category: "Tech-Experiment"
tags: ["Claude", "自托管", "AI小伙伴", "开源"]
heroImage: "../../assets/images/pando-bridge-self-hosted-claude-mobile-companion-banner.jpg"
---

> 本文基于开源项目 **Eloise-Aspen/pando-bridge**，研究如何搭建一个真正自有、可积累记忆、随时随地可用的个人 AI 伙伴。

---

## 你有没有想过，你和 AI 的关系能不能更像一段长期关系？

现在大多数人用 AI 的方式是这样的：打开网页或 App，说几句话，关掉。下次再开，AI 不记得你是谁，你们上次聊了什么，你有什么偏好和习惯。

每次都是从零开始，每次都在重新介绍自己。

Pando 这个项目想解决的，就是这个问题的基础设施层：**让 AI 跑在你自己的机器上，记住你，随时随地可以从手机接入。**

---

## Pando 是什么

名字来自世界上最大的白杨无性系群落——一个地下蔓延的单一有机体，地表长成整片森林。「一套根系，多个枝干」。

技术上说，**Pando 是一个自托管的 Claude Code CLI 移动网关**：

```
你的手机
    ↕（Tailscale HTTPS / 私有隧道）
Pando FastAPI 服务（跑在你的 Mac / Linux / Windows 上）
    ↕（subprocess）
本地 claude CLI（你已经安装好的 Claude Code）
```

它不托管在 Anthropic 的服务器上，不在第三方云上，就在你自己的机器上。所有聊天记录存在你自己的 SQLite 文件里，没有 API key 在应用里，数据不出你的硬盘。

**和官方远程访问的区别：**

| | Pando | 官方远程 |
|---|---|---|
| 托管位置 | 你的机器 | Anthropic 服务器 |
| 聊天数据 | 你自己的 SQLite | 厂商管理 |
| 记忆系统 | 可插拔，接任何引擎 | 固定 |
| 成本 | 复用已有 Claude 订阅 | 按产品条款 |
| 可扩展性 | 开放插件钩子 | 封闭 |

---

## 5 分钟跑起来

**前提：** Python 3.10+，Claude Code CLI 已安装并认证（`claude -p "hi"` 能正常返回）。

```bash
# 克隆 + 安装
git clone https://github.com/Eloise-Aspen/pando-bridge.git
cd pando-bridge
pip install -e .

# 复制启动脚本，改一行路径
cp run.example.py run.py
```

打开 `run.py`，只需改一处——`CLAUDE_CWD` 改成你想让 Claude 工作的目录：

```python
from pando import create_app
import uvicorn, os

app = create_app({
    "CLAUDE_EXE": "claude",                    # PATH 里的命令名
    "CLAUDE_CWD": "/path/to/your/project",     # ← 这一行必须改，其余都可省
    "DATA_DIR": "./data",                      # chat.db 存这里
    # 接记忆服务取消注释（后面讲）：
    # "MEMORY_SERVICE_URL": "http://127.0.0.1:8780",
})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("BRIDGE_PORT", 8765)))
```

```bash
python run.py
# → 浏览器打开 http://127.0.0.1:8765，就是内置的 PWA 前端
```

发一条消息，Claude Code 回复会流式吐出，包括思考过程（thinking）、工具调用（tool-use）等。这就是全部核心循环。

---

## 从桌面到手机：让 AI 随时在口袋里

光在本机跑不够——Pando 的核心价值是**手机随时接入**。推荐方案是 **Tailscale serve**，几条命令搞定 HTTPS，不需要公网 IP，不需要购买域名：

```bash
# 1. 两端安装 Tailscale（机器 + 手机），登录同一账号
# 2. 把 Pando 发布为 HTTPS（在跑 Pando 的机器上）
tailscale serve --bg 8765
# → 自动生成 https://<机器名>.<tailnet名>.ts.net，带真实有效的 HTTPS 证书

# 3. 手机打开这个地址，确认能聊
# 4. 浏览器「添加到主屏幕」安装 PWA
```

安装后，Pando 就像一个原生 App 住在你的手机主屏幕上。因为走真 HTTPS，PWA 的所有能力都可以用：离线缓存、通知、麦克风。

> 安全提示：Pando **没有内置认证**——Tailscale 本身就是你的门，只有 tailnet 里的设备才能连上。切勿把端口直接暴露到公网。

---

## 记忆：让 AI 真正「认识」你

这是 Pando 最有意思的设计。

**核心原则：内核零记忆逻辑。** Pando 的核心代码里没有一行记忆实现——记忆是完全外置、可插拔的。内核只跟一个满足 4 个端点 HTTP 契约的服务通信。

### 4 端点契约

```
POST /session_context  {}                    → {"context": str}
POST /recall           {"query": str}        → {"context": str}
POST /archive_prompt   {"messages": [...],
                        "force": bool}       → {"prompt": str | null}
POST /archive          {"raw": str}          → {"stored": int, ...}
```

- **`/session_context`**：新会话开始时，把长期记忆（你的偏好、习惯、背景）注入为 system prompt
- **`/recall`**：每条消息发出前，根据内容召回相关情景记忆，拼在消息前
- **`/archive_prompt`**：会话结束时，决定要不要存档、让 Claude 写什么样的记忆摘要
- **`/archive`**：接收 Claude 写出的记忆正文，落库持久化

**关键设计：存档归记忆引擎，内核只借活着的会话。**  内核把归档 prompt 丢进当前 Claude 会话跑——复用已有上下文，省一次 LLM 调用。存什么、怎么存，全是记忆引擎自己的事。

### 5 分钟起一个参考记忆服务

仓库自带了一个零依赖的 stub 实现，不需要向量数据库，重启不丢数据：

```bash
# 另开一个终端
python examples/memory_stub.py
# → 127.0.0.1:8780，记忆落到 ./stub_data/memories.json

# 在 run.py 里接上它（取消注释那行）
"MEMORY_SERVICE_URL": "http://127.0.0.1:8780",
```

启动 Pando 时会打印：
```
memory plugin enabled → http://127.0.0.1:8780
```

从这一刻起，每轮对话后 Claude 会自动提炼记忆存档；每次你发消息，相关的历史记忆会自动召回注入。

### 把你的已有笔记导进来

已经有一堆关于自己的笔记？直接导进记忆库：

```bash
python examples/import_md.py ./my-notes       # 把文件夹里所有 .md 一次导入
python examples/import_md.py ./my-notes --split-sections   # 按 ## 标题切成多条
python examples/import_md.py ./my-notes --dry-run          # 先预览不写入
```

**一事一条是关键。** 别把大段文字塞成一条——按「一条独立事实/偏好/决定」拆开，召回时才不会把无关内容一起拖出来。

如果你用 Claude Code 的 auto-memory 功能，把那个 memory 文件夹直接指给脚本即可，格式天然匹配。

### 记忆透出（Recall Transparency）

当记忆服务召回了什么，前端会在助手回复气泡旁显示一枚「记忆」胶囊（灯泡图标），点击查看本轮到底召回了什么上下文。历史记录也会保留这个信息。

不接记忆服务时，这个胶囊完全不出现——向后兼容，零侵入。

---

## 权限透传：手机上批准 Claude 的操作

Claude Code 在无头（headless）模式下遇到权限敏感操作（写文件、运行 Bash 等），默认只能拒绝，因为没有终端弹窗可以操作。Pando 的权限透传解决这个问题：

```
Claude 请求写文件
    ↓
Pando 接到请求
    ↓
手机屏幕弹出 modal：「Claude 想要写 /path/to/file，允许吗？」
    ↓
你点「允许」/ 「拒绝」/ 「始终允许」
    ↓
决策原路返回给 Claude
```

**安全设计：** 超时（默认 120 秒）、连接断开、任何异常——**一律拒绝**，绝不因出错而放行。安全优先。

在 `run.py` 里开启：
```python
app = create_app({
    "CLAUDE_CWD": "/your/project",
    "PERMISSION_PASSTHROUGH": True,   # 开启权限透传
    "PERMISSION_TIMEOUT": 120,        # 超时自动拒绝
})
```

### 工具策略

开启权限透传后，可以给三类工具配置持久化策略：

| 工具组 | 包含的工具 | 默认 |
|--------|-----------|------|
| 本地文件 | Read, Write, Edit | ask（每次询问） |
| 终端 Shell | Bash | ask（每次询问） |
| 网络访问 | WebFetch, WebSearch | deny（禁止） |

弹窗第三个按钮「始终允许」——点了就把该工具组标记为 allow，后续同类操作不再弹窗。设置页有「清除全部授权」入口，随时回到出厂状态。

---

## 插件系统：把 Pando 变成你想要的样子

Pando 的插件钩子让你在不改核心代码的情况下扩展几乎所有行为：

```python
class MyPlugin:
    def on_startup(self, app, config_dict):
        """启动时执行一次，可以注册任何初始化逻辑"""
        pass

    def register_routes(self, app):
        """注册额外的 FastAPI 路由"""
        @app.get("/my-endpoint")
        async def my_endpoint():
            return {"hello": "world"}

    def on_user_message(self, session_id, text, is_new_session) -> str:
        """每条用户消息都经过这里，返回值注入到消息里"""
        if is_new_session:
            return "（这是系统提示：用中文回答）"
        return ""

    def on_archive(self, session_id, messages, force):
        """归档前触发，可以做额外的处理"""
        pass
```

在配置里声明：
```python
"PLUGINS": ["my_package.my_plugin.MyPlugin"]
```

所有钩子都是可选的，异常被捕获后只影响该插件，不冒泡进聊天。

---

## 用量额度显示

设置页顶部显示两条进度条——**5 小时窗口**与**周限额**，直接读取本机 Claude Code 的凭证文件，拉 Anthropic 的用量接口实时更新，与官方 `/usage` 对齐。

不接网、用 API key 模式、或 macOS Keychain 存凭证时，自动降级为「本机 token 统计」显示，不报错、不卡聊天。

---

## 适合谁用

| 场景 | 适合程度 |
|------|---------|
| 想随时随地用手机和 Claude Code 对话 | ⭐⭐⭐⭐⭐ |
| 不想让聊天记录存在第三方服务器 | ⭐⭐⭐⭐⭐ |
| 想给 AI 建立「认识你」的长期记忆 | ⭐⭐⭐⭐ |
| 想把 Claude 接入自定义工作流 | ⭐⭐⭐⭐ |
| 只是偶尔用一下 Claude | ⭐⭐（用官方就好） |

需要一台长期在线的机器（Mac mini、家用服务器、Linux 主机等），以及已有 Claude 订阅（Claude Code CLI 已认证）。没有这两样的话，官方体验更简单。

---

## 快速回顾：完整架构

```
                          [你的手机 PWA]
                               ↕ HTTPS（Tailscale）
                    [Pando FastAPI · WebSocket 流式]
                               ↕
              ┌────────────────┼────────────────┐
         [本地 claude CLI]  [记忆服务]      [插件]
              │                │
         [你的项目目录]    [memories.json]
              │
          chat.db（SQLite）
```

一套根系，多个枝干。你的机器是根，你的手机、你的记忆系统、你的插件都是枝干。

---

GitHub：[github.com/Eloise-Aspen/pando-bridge](https://github.com/Eloise-Aspen/pando-bridge)  
License：MIT

© 2026 Author: Mycelium Protocol

<!--EN-->

## Pando: Use Your Own Machine to Raise an AI Companion That's Truly Yours

> Based on **Eloise-Aspen/pando-bridge** — a self-hosted Claude Code mobile gateway with pluggable memory and plugin hooks.

---

### What Is Pando

Pando is a **self-hosted mobile gateway for the Claude Code CLI**. It runs on your own machine. You access it from your phone via Tailscale or a private tunnel. All chat history lives in your own SQLite file. No API keys in the app. No data leaves your machine.

```
Your phone (PWA)
    ↕ HTTPS (Tailscale private tunnel)
Pando FastAPI server (your Mac/Linux/Windows)
    ↕ subprocess
Local claude CLI (already installed, already authenticated)
```

Named after the Pando aspen grove — one organism underground, a whole forest above. One core, many bridges.

---

### 5-Minute Setup

**Prerequisites:** Python 3.10+, Claude Code CLI authenticated (`claude -p "hi"` returns normally).

```bash
git clone https://github.com/Eloise-Aspen/pando-bridge.git
cd pando-bridge
pip install -e .
cp run.example.py run.py
```

Edit `run.py` — one required change:

```python
from pando import create_app
import uvicorn, os

app = create_app({
    "CLAUDE_EXE": "claude",
    "CLAUDE_CWD": "/path/to/your/project",  # ← only this must change
    "DATA_DIR": "./data",
    # "MEMORY_SERVICE_URL": "http://127.0.0.1:8780",  # uncomment to enable memory
})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
```

```bash
python run.py
# → http://127.0.0.1:8765 — built-in PWA, WebSocket streaming
```

---

### Phone Access via Tailscale

```bash
# Install Tailscale on both your machine and phone, log in to the same account
tailscale serve --bg 8765
# → https://<machine>.<tailnet>.ts.net — valid HTTPS, auto-certificate
# Open on phone, "Add to Home Screen" to install PWA
```

No public IP needed. Only devices in your tailnet can connect. No built-in auth — Tailscale is the gate.

---

### Pluggable Memory: The 4-Endpoint Contract

The core ships with **zero memory logic**. Memory is an optional external service behind a simple HTTP contract:

```
POST /session_context  {}                    → {"context": str}   # injected as system prompt
POST /recall           {"query": str}        → {"context": str}   # prepended to each message
POST /archive_prompt   {"messages": [...]}   → {"prompt": str | null}  # decides what to archive
POST /archive          {"raw": str}          → {"stored": int}    # receives Claude's summary, stores it
```

Any language, any stack — implement these four endpoints and you have a memory engine.

**Quickstart with the included stub:**
```bash
python examples/memory_stub.py        # JSON file storage, no vectors, restarts cleanly
# Then set "MEMORY_SERVICE_URL": "http://127.0.0.1:8780" in run.py
```

**Import existing notes:**
```bash
python examples/import_md.py ./my-notes --split-sections
# Splits on ## headers; one fact per memory entry = better recall
```

When memory fires, a recall chip appears in the chat UI showing exactly what context was injected.

---

### Permission Passthrough

In headless mode, Claude can't pop a terminal prompt for sensitive operations (file writes, Bash). Pando bridges this:

```
Claude requests: write /some/file
    → Pando pushes modal to your phone
    → You tap Allow / Deny / Always Allow
    → Decision returns to Claude
```

Safety rule: timeout, disconnect, any error → **always deny**. Never fails open.

```python
app = create_app({
    "CLAUDE_CWD": "/your/project",
    "PERMISSION_PASSTHROUGH": True,
})
```

Tool policy (persistent, survives restarts): `allow` / `ask` / `deny` per group:
- Local files (Read, Write, Edit) — default: ask
- Shell (Bash) — default: ask
- Network (WebFetch, WebSearch) — default: deny

---

### Plugin Hooks

```python
class MyPlugin:
    def on_user_message(self, session_id, text, is_new_session) -> str:
        if is_new_session:
            return "(system: always reply in Chinese)"
        return ""

    def register_routes(self, app):
        @app.get("/my-tool")
        async def my_tool(): ...
```

Declare in config: `"PLUGINS": ["my_package.MyPlugin"]`

All hooks optional. Exceptions caught per-plugin — never bubble into chat.

---

### Architecture

```
[Your Phone PWA]
      ↕ HTTPS (Tailscale)
[Pando FastAPI · WebSocket streaming]
      ↕
[local claude CLI] ← [memory service] ← [plugin hooks]
      ↓
 chat.db (SQLite, your machine)
```

One root system, many trunks. Your machine is the root.

GitHub: [github.com/Eloise-Aspen/pando-bridge](https://github.com/Eloise-Aspen/pando-bridge)

© 2026 Author: Mycelium Protocol
