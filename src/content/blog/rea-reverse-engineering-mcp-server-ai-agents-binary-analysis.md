---
title: "rea：让 AI Agent 做逆向工程的 MCP 服务器"
titleEn: "rea: An MCP Server That Lets AI Agents Do Reverse Engineering"
description: "morluto/rea（MIT，26.7K stars）是一个 TypeScript MCP 服务器，把逆向工程工作流暴露给 AI Agent。一句话：Claude Code、Codex、Cursor、Gemini CLI 接上它之后，可以直接让 Agent 分析原生二进制（Hopper/Ghidra/IDA 伪代码、汇编、符号、交叉引用）、Electron/JS 应用、.NET 汇编、Android APK、EVM 字节码、ELF、固件和 HAR 包。分析全本地运行，静态 JS/.NET 检查不执行目标文件，运行时捕获使用当前用户系统权限。一条命令接入：npx rea-agents setup。"
descriptionEn: "morluto/rea (MIT, 26.7K stars) is a TypeScript MCP server that exposes reverse-engineering workflows to AI agents. Claude Code, Codex, Cursor, and Gemini CLI can connect to it and directly analyze native binaries (Hopper/Ghidra/IDA pseudocode, assembly, symbols, cross-references), Electron/JS apps, .NET assemblies, Android APKs, EVM bytecode, ELF, firmware, and HAR captures. All analysis runs locally. Static JS/.NET inspection reads files without executing them. Runtime capture uses the current user's OS permissions. One-command setup: npx rea-agents setup."
pubDate: 2026-10-09
heroImage: "../../assets/images/rea-reverse-engineering-mcp-server-ai-agents-binary-analysis-banner.jpg"
category: "Tech-Experiment"
tags: ["开源工具", "AI Agent", "MCP", "逆向工程", "安全研究", "TypeScript"]
lang: "zh-CN"
wechatTitle: "rea：AI Agent 驱动逆向工程的 MCP 服务器"
wechatDigest: "MIT 26.7K stars；二进制/Electron/APK/EVM全支持；npx rea-agents setup；全本地"
---

逆向工程是人和二进制之间的长时间对话。rea 把这段对话的基础设施变成了 MCP 工具。

morluto/rea 是一个 TypeScript MCP 服务器，核心逻辑就一句话：把逆向工程的分析动作封装成工具调用，让 AI Agent 能直接调用。接上它之后，Claude Code、Codex、Cursor 这类 Agent 可以让你用自然语言提出问题，由 Agent 自己决定用哪个分析工具、怎么组合，最后给出解释。

GitHub: https://github.com/morluto/rea | ⭐ 26,700 | MIT | rea.tools

---

## 支持分析的目标类型

**原生二进制**（Hopper、Ghidra、IDA）：
- 伪代码（反编译结果）
- 汇编指令
- 符号表
- 交叉引用图

**应用层**：
- JavaScript / Electron 应用
- .NET 汇编（IL 层）
- Android APK

**其他格式**：
- EVM 字节码（以太坊智能合约，离线检查）
- ELF 二进制
- 固件镜像
- HAR 捕获文件（HTTP 流量记录）

**运行时**：
- 录制的 Linux 崩溃分析
- 进程行为实时捕获

---

## 接入方式

```bash
npx rea-agents setup
```

这一条命令完成所有配置。也可以使用独立 CLI。原生二进制分析需要预装 Hopper、Ghidra 或 IDA 中的一个；setup 过程可选安装 Hopper。

配置完成后，在支持 MCP 的 Agent 里直接问问题即可，比如：

> "这个二进制里 process_data 函数的控制流是什么样的？"
> "这个 Electron 应用的剪贴板访问是怎么实现的？"

---

## 运行方式和安全边界

**全本地**：所有分析在本机运行，不向外发送目标文件。

**静态检查不执行目标**：分析 JavaScript 和 .NET 时，rea 读取文件内容而不运行它——这对分析可疑文件很重要。

**运行时捕获使用当前用户权限**：进程行为捕获的权限边界和你自己手动操作一样，不超出当前用户能做的事。

⚠️ rea README 附有法律免责声明：用户负责确保分析行为已获授权，以及遵守当地法律。工具本身只是分析基础设施，分析什么目标、是否有权限分析，由使用者负责。

---

## 典型使用案例（来自 README）

- **DX-Ball**：从游戏二进制里重建声音声像（pan）计算逻辑
- **Notion Electron**：定位剪贴板桥接的实现位置
- **TH04 DOS 游戏**：逆向子弹环计算代码

这三个案例的共同点：都是从"我想理解这个程序的某个行为"出发，让 Agent 自主决定用哪些分析步骤串起来。

---

## 技术规格

- **语言**：TypeScript（Node.js）
- **Node 版本要求**：22.x（>=22.19）、24.x（>=24.11）或 26+
- **测试框架**：vitest
- **兼容 Agent**：Claude Code、Codex、Cursor、Gemini CLI 等任何支持 MCP 的 Agent
- **社区**：Discord（discord.gg/GkcryMnJDM）

---

## 一句话说清楚

rea 把逆向工程的各个分析动作封装成 MCP 工具，让 AI Agent 代替手工查反编译结果、追交叉引用。接入简单（一条 npx 命令），全本地运行，支持从二进制到 APK 到以太坊合约的主流目标格式。分析权限和合法性由用户自己负责。

---

> MIT 许可。morluto/rea，2026-04-14 创建。开源仅供学习参考。

---

<!--EN-->

## rea: An MCP Server That Lets AI Agents Do Reverse Engineering

Reverse engineering is a long conversation between a person and a binary. rea turns the infrastructure for that conversation into MCP tools.

morluto/rea is a TypeScript MCP server that wraps reverse-engineering analysis actions as tool calls, so AI agents can invoke them directly. Once connected, Claude Code, Codex, or Cursor can take a natural-language question, decide which analysis tools to combine, and return an explanation.

GitHub: https://github.com/morluto/rea | ⭐ 26,700 | MIT | rea.tools

---

### Supported Analysis Targets

**Native binaries** (Hopper, Ghidra, IDA):
- Pseudocode (decompiler output)
- Assembly instructions
- Symbol tables
- Cross-reference graphs

**Application layer**:
- JavaScript / Electron apps
- .NET assemblies (IL level)
- Android APKs

**Other formats**:
- EVM bytecode (Ethereum smart contracts, offline)
- ELF binaries
- Firmware images
- HAR captures (HTTP traffic recordings)

**Runtime**:
- Recorded Linux crash analysis
- Live process behavior capture

---

### Setup

```bash
npx rea-agents setup
```

One command. A standalone CLI is also available. Native binary analysis requires Hopper, Ghidra, or IDA to be pre-installed; setup can optionally install Hopper.

After setup, ask questions directly in any MCP-compatible agent:

> "What's the control flow of the process_data function in this binary?"
> "How does this Electron app implement clipboard access?"

---

### How It Runs and Its Security Boundaries

**Fully local**: All analysis runs on-device. Target files are never sent externally.

**Static inspection doesn't execute targets**: When analyzing JavaScript or .NET, rea reads file content without running it — important when inspecting potentially suspicious files.

**Runtime capture uses current user permissions**: Process behavior capture operates within the same permission boundary as manual operation.

⚠️ rea's README includes a legal disclaimer: users are responsible for ensuring analysis is authorized and compliant with applicable laws. The tool provides analysis infrastructure; whether you have permission to analyze a given target is your responsibility.

---

### TL;DR

rea wraps reverse-engineering analysis actions as MCP tools, letting AI agents replace manual decompiler browsing and cross-reference tracing. Simple setup (one npx command), fully local, supports major target formats from binaries to APKs to Ethereum contracts. Authorization and legality are on the user.

---

> MIT license. morluto/rea, created 2026-04-14. For technical reference only.
