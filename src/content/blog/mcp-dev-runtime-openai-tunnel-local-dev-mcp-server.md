---
title: "mcp-dev-runtime：一条命令把本地开发机暴露给 ChatGPT——OpenAI Tunnel + 6 个 MCP 工具的打包方案"
titleEn: "mcp-dev-runtime: One Command to Expose Your Local Dev Machine to ChatGPT — OpenAI Tunnel + 6 MCP Tools Bundled"
description: "dolibali/mcp-dev-runtime，3 stars，Apache-2.0，TypeScript。把 OpenAI 官方 Tunnel 客户端和 6 个本地开发 MCP 工具（shell 执行/PTY 交互/代码 patch/图片查看/进程管理）打包成跨平台运行时，内置 Node.js 24.21.0。一条 mdr start 同时启动 MCP 服务和 Tunnel，对接的是 ChatGPT（非 claude.ai）。无沙箱、无命令白名单，需注意安全边界。"
descriptionEn: "dolibali/mcp-dev-runtime — 3 stars, Apache-2.0, TypeScript. Bundles the OpenAI official Tunnel client and 6 local development MCP tools (shell exec/PTY/code patch/image view/process management) into a cross-platform runtime with Node.js 24.21.0 included. One `mdr start` launches both the MCP server and Tunnel. Connects to ChatGPT — not claude.ai. No sandboxing, no command allowlist; security boundary needs attention."
pubDate: 2026-09-22
heroImage: "../../assets/images/mcp-dev-runtime-openai-tunnel-local-dev-mcp-server-banner.jpg"
category: "Tech-Experiment"
tags: ["mcp", "openai", "tunnel", "local-dev", "chatgpt", "open-source", "developer-tools"]
lang: zh-CN
---

`dolibali/mcp-dev-runtime` 做的事很具体：把本地开发机变成 ChatGPT 可以直接操作的 MCP 服务器，一条命令启动，无需手动配 Node.js 环境。3 stars，Apache-2.0，v1.2.0。

**GitHub**：github.com/dolibali/mcp-dev-runtime | **Stars**：3 | **License**：Apache-2.0

---

## ⚠️ 先说清楚：这套方案绑的是 ChatGPT，不是 claude.ai

项目描述里的"网页版自定义插件接入"指的是 **ChatGPT**，不是 claude.ai。

原因在于内网穿透层：mcp-dev-runtime 使用的是 **OpenAI 官方 Secure MCP Tunnel**（`platform.openai.com/settings/organization/tunnels`）。Tunnel 客户端向 OpenAI 控制面发起出站连接，流量经 OpenAI 基础设施转发到本地。

claude.ai 走的是标准 MCP over HTTP/SSE，不经过 OpenAI Tunnel，所以本项目**无法直接对接 claude.ai**。

---

## 这个项目解决什么问题

让 ChatGPT 直接操作本地开发环境，对着 AI 说"帮我跑一下测试"、"把这个 bug 的 patch 应用上去"、"看一下这个截图里哪里错了"——AI 直接操作，不是粘贴命令让你手动运行。

之前的障碍是配置繁琐：需要自己安装 Node.js、配 MCP 服务器、搞定内网穿透、在 ChatGPT 里注册工具。mcp-dev-runtime 把这些全打包了。

---

## 6 个内置 MCP 工具

| 工具 | 功能 |
|------|------|
| `exec_command` | Shell 命令执行，支持 Git / 构建 / 测试 / 代码搜索（ripgrep） |
| `write_stdin` | PTY 交互式输入，支持增量输出和日志实时读取 |
| `apply_patch` | 多文件代码 patch 应用 |
| `view_image` | 展示本地 PNG/JPEG/WebP 图片给 AI 查看 |
| `list_exec_sessions` | 查询历史执行记录 |
| `terminate_exec_session` | 终止运行中的进程 |

v1.1.0 还新增了两个可选的 skill 发现工具（`discover_skills`、`read_skill`），默认关闭。

---

## 安装与配置

### 第一步：准备 OpenAI 资源

1. **创建 Tunnel**：`platform.openai.com/settings/organization/tunnels`，记录 `tunnel_` 开头的 ID
2. **生成受限 API Key**：`platform.openai.com/settings/organization/api-keys`，权限选"Tunnels → Read + Use"（**不能用 admin key**）

### 第二步：下载运行包

从 Releases 页下载对应平台的 v1.2.0 包，验证 SHA256：

```bash
# macOS ARM64 / Linux x64 / Ubuntu 22.04+
# 下载对应包后
sha256sum -c SHA256SUMS    # 验证完整性
./install.sh               # 安装
```

```powershell
# Windows x64 / ARM64
.\install.ps1
```

安装后命令位于 `~/.local/bin/mcp-dev-runtime`，`mdr` 为简写。

**内置 Node.js 24.21.0**，无需单独安装 Node。

### 第三步：配置 Tunnel 凭据

创建 `runtime.env` 文件：

```bash
CONTROL_PLANE_TUNNEL_ID=tunnel_[32位十六进制]
CONTROL_PLANE_API_KEY=[你的受限 runtime key]
```

### 第四步：一键启动

```bash
mdr start          # 前台运行，看日志
mdr start --bg     # 后台运行
```

`mdr start` 同时启动两个服务：
- MCP Dev Runtime 服务（监听 `127.0.0.1:3001`）
- Tunnel 客户端（连接 OpenAI 控制面，健康检查 `127.0.0.1:9098`）

### 第五步：在 ChatGPT 接入

1. ChatGPT → Settings → Security and login → 开启 Developer mode
2. 创建 ChatGPT developer app，连接类型选 "Tunnel"
3. 选择第一步创建的同一个 Tunnel ID
4. MCP 认证选 "No Authentication"
5. 扫描并启用 6 个工具

---

## 平台支持

| 平台 | 架构 |
|------|------|
| macOS 14 | ARM64 |
| macOS 15 | Intel (x64) |
| Ubuntu 22.04+ | x64 / ARM64 |
| Windows Server 2025 | x64 |
| Windows 11 | ARM64（v1.2.0 新增） |

---

## 源码安装

如果不用预编译包：

```bash
# 依赖：Node.js 24+、Git、ripgrep、Go 1.27.0 + make
git clone https://github.com/dolibali/mcp-dev-runtime.git
cd mcp-dev-runtime
./install.sh
```

---

## ⚠️ 安全说明：没有沙箱

这是使用前必须理解的限制：

- **无沙箱**：工具以服务进程的 OS 权限运行
- **无命令白名单**：`exec_command` 可以执行任意 shell 命令
- **无多用户隔离**

`127.0.0.1:3001` 必须保持在回环地址（loopback），绝对不能暴露到公网。

流量路径是：OpenAI 控制面 → Tunnel 客户端 → `127.0.0.1:3001`。实际上你的执行权限经过了 OpenAI 的 Tunnel 基础设施——这意味着你的信任边界包括 OpenAI 的 Tunnel 服务。

对于个人开发机、单机使用，这是可接受的（类似 localhost Jupyter Notebook 的威胁模型）。但不适合多人共享的机器或生产服务器。

---

## 执行历史配置

| 参数 | 默认值 |
|------|--------|
| 活跃执行上限 | 8 |
| 内存记录上限 | 512 |
| 磁盘历史条数 | 4,096 |
| 磁盘历史大小 | 256 MiB |
| 按时间过期 | 默认关闭 |

---

## 作者的其他项目

dolibali 同时维护 35 个仓库，都是 AI 编程工具链方向：

- `pi` — 统一 LLM API + Agent loop + TUI 编程 CLI（TypeScript，MIT）
- `kilocode` — All-in-one agentic 工程平台（TypeScript，MIT）
- `openclaw` — 跨平台 AI 个人助手（TypeScript，MIT）
- `opencode` — 开源 Coding Agent（TypeScript，MIT）
- `open-codex-computer-use` — Codex Computer Use 开源替代（Swift，MIT）

mcp-dev-runtime 是这个体系里偏向"本地开发机 → AI 直接操作"方向的一个子项目。

---

## 不足之处

**1. 绑死 OpenAI Tunnel 基础设施**：只能接 ChatGPT，不能接 claude.ai、Cursor、其他 MCP 客户端。

**2. Stars 极少（3）**：非常早期，维护连续性不确定。

**3. 无沙箱**：`exec_command` 可以执行任意命令，安全边界完全依赖使用者自律。

**4. 需要 OpenAI 账号**：没有 OpenAI Platform 账号就无法创建 Tunnel，门槛对非 OpenAI 用户不友好。

**5. 文档全中文**：非中文读者的配置文档不够友好（虽然也有部分英文文档）。

---

## 怎么看这个项目

mcp-dev-runtime 的核心价值是**降低 ChatGPT 接管本地开发机的配置门槛**——预打包运行时 + 一条命令启动，对比手动搭同等能力确实省事。

但技术上的强绑定是真实限制：OpenAI Tunnel 不是通用标准，换一个 AI 客户端就用不了这套方案。想用 claude.ai 或 Cursor 操作本地机器，需要走标准 MCP over HTTP 路径，配不同的内网穿透方案。

适合用户：主要用 ChatGPT、想要 AI 直接跑本地命令、不想自己配 Node 和 Tunnel 的开发者。不适合：想把本地环境接入 claude.ai 或其他 MCP 客户端的场景。

> 代码 Apache-2.0，与 OpenAI 无从属关系，仅供学习研究参考。使用前评估本机 shell 执行权限的安全边界。

---

<!--EN-->

## mcp-dev-runtime: Bundle OpenAI Tunnel + 6 MCP Tools, One Command to Expose Local Dev Machine to ChatGPT

`dolibali/mcp-dev-runtime` (3 stars, Apache-2.0, TypeScript) bundles OpenAI's official Secure MCP Tunnel client and 6 local development MCP tools into a cross-platform runtime. One `mdr start` command launches both the MCP server and the Tunnel.

**GitHub**: github.com/dolibali/mcp-dev-runtime | **Stars**: 3 | **License**: Apache-2.0

---

### ⚠️ Important: This Connects to ChatGPT, Not claude.ai

The project uses OpenAI's proprietary **Secure MCP Tunnel** (`platform.openai.com/settings/organization/tunnels`). The Tunnel client establishes an outbound connection to OpenAI's control plane; traffic is routed through OpenAI's infrastructure to the local MCP server.

claude.ai uses standard MCP over HTTP/SSE and does not route through OpenAI Tunnel — **this project cannot connect to claude.ai**.

---

### What It Does

Lets ChatGPT directly operate your local development environment — run tests, apply patches, inspect screenshots — without you manually copying commands. Previously this required setting up Node.js, MCP server, tunneling, and ChatGPT tool registration separately. mcp-dev-runtime bundles everything.

---

### 6 Bundled MCP Tools

| Tool | Function |
|------|----------|
| `exec_command` | Shell execution — git, build, test, code search (ripgrep) |
| `write_stdin` | PTY interactive input, incremental output, log reading |
| `apply_patch` | Multi-file code patch application |
| `view_image` | Show local PNG/JPEG/WebP images to the AI |
| `list_exec_sessions` | Query execution history |
| `terminate_exec_session` | Kill running processes |

---

### Installation

```bash
# Download v1.2.0 package for your platform from Releases
sha256sum -c SHA256SUMS   # Verify integrity
./install.sh              # macOS/Linux
.\install.ps1             # Windows
```

Includes Node.js 24.21.0 — no separate Node installation needed. `mdr` is the short alias for the installed binary.

---

### Configuration

**Step 1**: Create a Tunnel at `platform.openai.com/settings/organization/tunnels` (gets `tunnel_*` ID)

**Step 2**: Generate a restricted API Key with "Tunnels → Read + Use" permission (not an admin key)

**Step 3**: Create `runtime.env`:
```
CONTROL_PLANE_TUNNEL_ID=tunnel_[32-hex-chars]
CONTROL_PLANE_API_KEY=[your-restricted-key]
```

**Step 4**: `mdr start` — launches MCP server on `127.0.0.1:3001` and Tunnel client simultaneously

**Step 5**: ChatGPT → Settings → Developer mode → Create developer app → Connect Tunnel → Enable 6 tools

---

### Platform Support

macOS 14 (ARM64), macOS 15 (Intel), Ubuntu 22.04+ (x64/ARM64), Windows Server 2025 (x64), Windows 11 ARM64 (v1.2.0+).

---

### ⚠️ Security: No Sandbox

- `exec_command` runs arbitrary shell commands at the service process's OS permissions
- No command allowlist, no multi-user isolation
- `127.0.0.1:3001` must not be exposed to the public network
- Traffic path goes through OpenAI's Tunnel infrastructure — OpenAI is in your trust boundary

Acceptable for a personal developer workstation with single-user use. Not suitable for shared machines or production servers.

---

### Limitations

1. **Locked to OpenAI Tunnel**: Only works with ChatGPT — cannot connect to claude.ai, Cursor, or other MCP clients.
2. **3 stars, very early project**: Maintenance continuity uncertain.
3. **No sandbox**: Shell execution runs at OS permissions of the service process.
4. **Requires OpenAI Platform account**: No account, no Tunnel, no service.
5. **Mainly Chinese docs**: Non-Chinese readers will find some configuration guidance in English, but the primary documentation is Chinese.

---

### Bottom Line

mcp-dev-runtime reduces the configuration friction for ChatGPT controlling a local dev machine — pre-bundled runtime, one-command startup. That's the real value.

The binding to OpenAI Tunnel is a genuine constraint: switch AI clients and the whole setup doesn't transfer. For claude.ai or Cursor local machine access, you need standard MCP over HTTP with a different tunneling approach (ngrok, Cloudflare Tunnel, Tailscale).

Best fit for: developers primarily using ChatGPT who want AI to directly execute local commands without manually setting up Node.js and tunneling infrastructure.

> Apache-2.0. Not affiliated with OpenAI. For learning and research use only. Evaluate shell execution security boundaries before deploying.
