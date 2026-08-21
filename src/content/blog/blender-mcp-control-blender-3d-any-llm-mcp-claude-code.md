---
title: "Blender MCP：用自然语言控制 Blender 3D，接任意 LLM，26K stars 社区插件"
titleEn: "blender-mcp-control-blender-3d-any-llm-mcp-claude-code"
description: "ahujasid/blender-mcp 是把 Blender 3D 接入任意 LLM 的社区 MCP 插件，26K stars，MIT 协议。三步安装：安装 uv → 配置 MCP 服务器 → 安装 Blender 插件。能力：自然语言创建/修改/删除 3D 对象、材质控制、场景信息获取、在 Blender 里直接执行 Python 代码、从 Poly Haven 下载资产和 HDRI、从 Sketchfab 搜索模型、通过 Hyper3D Rodin 和 Hunyuan3D 生成 AI 3D 模型。支持 Claude Desktop/Code、Cursor、VS Code、OpenCode。两部件：Blender 插件（socket 服务器）+ MCP Server（TCP 桥接），JSON 协议通信。"
descriptionEn: "ahujasid/blender-mcp is a community MCP plugin connecting Blender 3D to any LLM — 26K stars, MIT license. Three-step setup: install uv → configure MCP server → install Blender addon. Capabilities: natural language create/modify/delete 3D objects, material control, scene inspection, arbitrary Python execution in Blender, Poly Haven asset/HDRI downloads, Sketchfab model search, AI 3D generation via Hyper3D Rodin and Hunyuan3D. Supports Claude Desktop/Code, Cursor, VS Code, OpenCode. Two components: Blender addon (socket server) + MCP Server (TCP bridge), JSON protocol."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["Blender", "MCP", "3D建模", "Claude", "LLM", "AI工具", "开源", "模型上下文协议"]
heroImage: "../../assets/images/blender-mcp-control-blender-3d-any-llm-mcp-claude-code-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：ahujasid/blender-mcp  
官网：blendermcp.org  
PyPI：blender-mcp  
许可证：MIT  
语言：Python  
Stars：26,126 · Forks：2,484  
作者：Siddharth（@sidahuj）

---

## 一、一句话

在 Claude 里说「创建一个地下城场景，龙守着一罐金币」，然后 Blender 里真的出现了。

这就是 Blender MCP 做的事：把自然语言指令通过 MCP 协议传给 Blender，由 LLM 控制 3D 软件执行操作。

---

## 二、架构：两个组件

```
Claude / 任意 LLM
       ↕  MCP 协议
  MCP Server（Python）
       ↕  TCP Socket / JSON
  Blender Addon（addon.py）
       ↕  Blender Python API
  Blender 3D 引擎
```

**Blender Addon**（`addon.py`）：在 Blender 内部创建一个 socket 服务器，监听来自 MCP Server 的命令，调用 Blender Python API 执行，返回结果。

**MCP Server**（`src/blender_mcp/server.py`）：实现 Model Context Protocol，对 LLM 暴露工具集，把 LLM 的调用翻译成 TCP 消息发给 Blender。

通信协议：JSON over TCP，默认端口 9876。指令格式：`{type, params}`，响应格式：`{status, result/message}`。

---

## 三、安装（三步）

### 步骤 1：安装 uv

```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**注意**：用官方安装器，不要用 `pip install uv`——后者不一定创建 `uvx` 命令，会导致客户端找不到它。

### 步骤 2：配置 MCP 客户端

**Claude Code**（一条命令）：

```bash
claude mcp add blender uvx blender-mcp
```

**Claude Desktop**（`claude_desktop_config.json`）：

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"]
        }
    }
}
```

**多版本 Python / conda 环境**（避免冲突，锁定 3.11）：

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["--python", "3.11", "blender-mcp"],
            "env": { "UV_PYTHON_PREFERENCE": "only-managed" }
        }
    }
}
```

Cursor / VS Code / OpenCode 也支持，详见 README 的 MCP Client Setup 章节（有一键安装按钮）。

### 步骤 3：安装 Blender 插件

```bash
uvx blender-mcp install-addon
```

然后在 Blender：**Edit → Preferences → Add-ons** → 启用 **Interface: Blender MCP**。

### 步骤 4：连接

在 Blender 3D 视口按 `N` → 找到 **BlenderMCP** 标签页 → 点 **Start MCP Server**。完成。

---

## 四、能力矩阵

| 能力 | 说明 |
|------|------|
| **3D 对象操控** | 创建、修改、删除几何体，设置位置/旋转/缩放 |
| **材质控制** | 应用和修改材质、颜色、纹理 |
| **场景信息** | 获取当前场景的详细状态（对象列表、层级关系等） |
| **Python 执行** | 直接在 Blender 里运行任意 Python 代码 |
| **Poly Haven** | 下载免费资产、纹理和 HDRI 环境贴图 |
| **Sketchfab** | 搜索并下载 3D 模型（需要 API Key） |
| **Hyper3D Rodin** | AI 生成 3D 模型（需要 API Key） |
| **Hunyuan3D** | 腾讯混元 AI 3D 生成（需要 SecretId/Key） |

---

## 五、示例指令

这些是可以直接对 Claude 说的话：

```
"Create a low poly scene in a dungeon, with a dragon guarding a pot of gold"
"Create a beach vibe using HDRIs, textures, and models like rocks and vegetation from Poly Haven"
"Generate a 3D model of a garden gnome through Hyper3D"
"Make this car red and metallic"
"Create a sphere and place it above the cube"
"Make the lighting like a studio"
"Point the camera at the scene, and make it isometric"
```

也可以给一张参考图，让 Claude 在 Blender 里重建对应场景。

---

## 六、持久化凭据

API Key 可以存在 Blender 插件偏好设置里（**Edit → Preferences → Add-ons → Blender MCP**），在 Blender 重启后保留：

- Sketchfab API Key
- Hyper3D API Key
- Hunyuan3D SecretId / SecretKey

CI/无头环境也可以用环境变量注入：`BLENDERMCP_SKETCHFAB_API_KEY`、`BLENDERMCP_HYPER3D_API_KEY` 等。

---

## 七、注意事项

**安全**：`execute_blender_code` 工具允许在 Blender 里执行任意 Python 代码。用之前先保存工作文件。

**遥测**：默认开启匿名使用数据收集。关闭方式：

```json
"env": { "DISABLE_TELEMETRY": "true" }
```

或在 Blender → Add-on 偏好设置里取消勾选。

**单实例**：同时只能运行一个 MCP 服务器（Claude Desktop 或 Cursor 选一个），不要同时开两个。

**超时问题**：复杂操作拆成小步骤。第一条命令有时不通，从第二条开始正常——这是已知行为。

---

## 八、背景

Blender MCP 由 Siddharth（@sidahuj）维护，社区驱动，MIT 协议。26K stars，生态已经在跑：有人用它从截图重建 3D 场景，有人对接 Hyper3D 批量生成游戏资产，有人在 CI 里用无头模式自动化 3D 渲染流水线。

MCP 作为协议的价值在这里体现得很直接：Blender 本来有完整的 Python API，MCP 把这个 API 暴露给了任意 LLM，不需要改 Blender 本体，也不需要针对每个 LLM 写适配层。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Blender MCP: Control Blender 3D with Any LLM, 26K Stars

*by Mycelium Protocol*

---

GitHub: ahujasid/blender-mcp  
Site: blendermcp.org  
PyPI: blender-mcp  
License: MIT  
Language: Python  
Stars: 26,126 · Forks: 2,484  
Author: Siddharth (@sidahuj)

---

### The One-Liner

Tell Claude "Create a dungeon scene with a dragon guarding a pot of gold" — and Blender builds it.

Blender MCP routes natural language through the Model Context Protocol into Blender's Python API, letting any LLM control a 3D application in real time.

---

### Architecture: Two Components

```
Claude / any LLM
       ↕  MCP protocol
  MCP Server (Python)
       ↕  TCP socket / JSON
  Blender Addon (addon.py)
       ↕  Blender Python API
  Blender 3D engine
```

**Blender Addon** (`addon.py`): creates a socket server inside Blender that listens for commands from the MCP Server, calls the Blender Python API, and returns results.

**MCP Server** (`src/blender_mcp/server.py`): implements MCP, exposes a tool set to the LLM, and translates LLM tool calls into TCP messages to Blender.

Protocol: JSON over TCP, default port 9876. Commands: `{type, params}`. Responses: `{status, result/message}`.

---

### Install (Three Steps)

**Step 1: Install uv**

```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Use the official installer — not `pip install uv`. The `pip` route may not create the `uvx` command that MCP clients need.

**Step 2: Configure your MCP client**

Claude Code (one command):

```bash
claude mcp add blender uvx blender-mcp
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"]
        }
    }
}
```

For conda / pyenv environments, pin Python 3.11 to avoid interpreter conflicts:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["--python", "3.11", "blender-mcp"],
            "env": { "UV_PYTHON_PREFERENCE": "only-managed" }
        }
    }
}
```

**Step 3: Install the Blender addon**

```bash
uvx blender-mcp install-addon
```

In Blender: **Edit → Preferences → Add-ons** → enable **Interface: Blender MCP**.

Press `N` in the 3D viewport → **BlenderMCP** tab → **Start MCP Server**. Done.

---

### Capabilities

| Feature | Description |
|---------|-------------|
| **3D object manipulation** | Create, modify, delete geometry; set position/rotation/scale |
| **Material control** | Apply and modify materials, colors, textures |
| **Scene inspection** | Get detailed state of the current scene (objects, hierarchy, etc.) |
| **Python execution** | Run arbitrary Python code directly in Blender |
| **Poly Haven** | Download free assets, textures, and HDRI environment maps |
| **Sketchfab** | Search and download 3D models (API key required) |
| **Hyper3D Rodin** | AI-generated 3D models (API key required) |
| **Hunyuan3D** | Tencent Hunyuan AI 3D generation (SecretId/Key required) |

---

### Example Prompts

```
"Create a low poly scene in a dungeon, with a dragon guarding a pot of gold"
"Create a beach vibe using HDRIs, textures, and models like rocks and vegetation from Poly Haven"
"Generate a 3D model of a garden gnome through Hyper3D"
"Make this car red and metallic"
"Create a sphere and place it above the cube"
"Make the lighting like a studio"
"Point the camera at the scene, and make it isometric"
```

You can also hand over a reference image and have Claude reconstruct the equivalent Blender scene.

---

### Persistent Credentials

Store API keys in Blender Add-on Preferences (**Edit → Preferences → Add-ons → Blender MCP**) — they survive Blender restarts. For headless/CI setups, inject via environment variables: `BLENDERMCP_SKETCHFAB_API_KEY`, `BLENDERMCP_HYPER3D_API_KEY`, `BLENDERMCP_HUNYUAN3D_SECRET_ID`, etc.

---

### Security and Telemetry

**Security**: `execute_blender_code` runs arbitrary Python in Blender. Save your work before using it.

**Telemetry**: anonymous usage data collected by default. Opt out via:

```json
"env": { "DISABLE_TELEMETRY": "true" }
```

Or uncheck in Blender's Add-on preferences. Per the terms, data may be used to improve BlenderMCP, for research, and to train AI models.

**Single instance**: run only one MCP server at a time. The first command sometimes fails; subsequent ones work normally — expected behavior.

---

### Why This Matters

Blender has a complete Python API. MCP exposes it to any LLM without touching Blender internals and without per-LLM adapters. 26K stars and an active ecosystem (scene reconstruction from screenshots, batch game asset generation via Hyper3D, headless 3D render pipelines) confirm the demand.

The pattern generalizes: any software with a programmable API can become an LLM-driven tool via MCP, no first-party integration required.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
