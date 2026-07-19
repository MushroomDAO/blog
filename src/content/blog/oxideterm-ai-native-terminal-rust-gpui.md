---
title: "终端界的 Zed：OxideTerm 用 GPUI + 纯 Rust SSH 把 iTerm2、Termius 和 VSCode Remote 做成了一个"
titleEn: "The Zed of Terminals: OxideTerm Merges iTerm2, Termius, and VSCode Remote Into One with GPUI and Pure-Rust SSH"
description: "OxideTerm（958 stars）是一个 AI-native 远程工作台：GPUI 原生渲染（零 Electron）、纯 Rust SSH（零 OpenSSL、零 C 依赖）、内置 SFTP 文件管理器、轻量 IDE、端口转发，外加 BYOK-first 的 OxideSens AI。50~70MB 包体，把过去要靠三四个工具才能完成的远程工作，压进了一个本地优先的桌面应用。"
descriptionEn: "OxideTerm (958 stars) is an AI-native remote workspace: GPUI native rendering (zero Electron), pure-Rust SSH (zero OpenSSL, zero C deps), built-in SFTP file manager, lightweight IDE, port forwarding, and BYOK-first OxideSens AI. 50–70 MB package, collapsing what used to need 3–4 tools into one local-first desktop app."
pubDate: "2026-07-19"
updatedDate: "2026-07-19"
category: "Tech-Experiment"
tags: ["终端工具", "Rust", "GPUI", "SSH", "AI终端", "OxideTerm", "开源", "开发工具", "远程开发"]
heroImage: "../../assets/images/oxideterm-ai-native-terminal-rust-banner.jpg"
---

> **GitHub**：[AnalyseDeCircuit/oxideterm](https://github.com/AnalyseDeCircuit/oxideterm) · ⭐ 958 · Rust · GPL-3.0  
> **主页**：[oxideterm.app](https://oxideterm.app)

---

## 同一个问题，重复解决了三四次

做远程服务器工作，你现在的工具箱大概长这样：

- **iTerm2 / Warp** — SSH 终端
- **Termius / RoyalTSX** — 连接管理 + SFTP
- **VSCode Remote SSH** — 远程文件编辑
- **Tunnelblick / SSH -L** — 端口转发

四个工具，同一台服务器上的四种连接，上下文分散，切换成本高。这不是偏好问题，是行业的默认状态。

OxideTerm 的逻辑很简单：**把这四件事放进一个应用里，用 Rust 写，不依赖 Electron 和 OpenSSL。**

---

## GPUI：Zed 的渲染引擎，现在进入终端

OxideTerm 最值得注意的技术选择是它的 UI 层：**GPUI**（Zed 的原生 GPU 渲染框架）。

这不是 Tauri 的 WebView 壳，也不是 Electron。GPUI 直接把 Rust 代码渲染到 GPU，跳过了整个 Web 技术栈。

对比一下大家熟悉的参照系：

| 应用 | UI 层 | 包体大小 |
|---|---|---|
| Electron 终端（Hyper/Tabby） | Node.js + Chromium | 150–300 MB |
| Tauri 应用 | WebView（OS 自带） | 5–20 MB |
| **OxideTerm** | **GPUI（原生 GPU Rust）** | **50–70 MB** |
| Zed | GPUI | ~60 MB |

GPUI 的代价是：你必须用 Rust 写 UI 逻辑，没有 React 那种快速原型能力。OxideTerm 选择接受这个代价，换来了无 WebView 依赖、无垃圾回收、GPU 直接驱动的渲染性能。

终端对渲染延迟非常敏感，这个选择有其道理。

---

## russh：零 C 依赖的纯 Rust SSH

SSH 客户端生态里有一个长期存在的问题：几乎所有实现都依赖 OpenSSL 或 libssh2，两者都是 C 库。

OxideTerm 用的是 **russh 0.61**，ring crypto backend，纯 Rust。

这意味着：

- **零 C 依赖**：编译结果不链接任何 C 代码
- **密码算法**：Ed25519、RSA、ECDSA 密钥；ChaCha20-Poly1305 和 AES-GCM 加密套件
- **内存安全**：敏感内存在 drop 时自动归零（zeroize）

连接复用也是一个关键设计：一条 SSH 连接同时服务终端会话、SFTP 浏览、端口转发和 IDE。不是四条连接，是一条。

---

## 功能地图：一个应用替代四个

### SSH 终端

分屏布局，命令栏可以广播到多个 session。Session 录制和回放（asciicast v2 格式）。31+ 主题，原生色彩 token 主题编辑器。⌘K 命令面板，禅模式。

### SFTP 文件管理器

双栏浏览，拖拽操作。智能预览：图片、视频、音频、代码、hex、字体。传输队列带实时进度和预计完成时间。本地文件 watch mode，修改自动上传。

### 内置 IDE

GPUI 原生编辑器，tree-sitter 支持 36 种语言（Rust、Python、JS/TS、Go、C/C++、Java、YAML、JSON、TOML、Markdown、Shell 等）。文件树带 Git 状态指示。多 tab 编辑，冲突解决。可选的远程 agent，支持 Linux x86_64 和 aarch64。正则全文搜索替换。

### 端口转发

本地（-L）、远程（-R）、动态 SOCKS5（-D）三种模式。无锁消息传递 I/O。断线自动恢复所有转发。实时带宽和延迟监控。

### 本地 Shell

zsh / bash / fish / pwsh / WSL2，与 SSH session 并排放在同一个 UI 里，本地和远程任务共享一套界面。

---

## OxideSens AI：workspace-aware 的 BYOK AI

OxideSens 是 OxideTerm 内置的 AI 层，角度和大多数 AI 助手不同：它不只看你正在输入什么，它看到整个 workspace 的上下文。

具体包括：

- **已保存的连接**（服务器列表和元数据）
- **活跃 SSH session 的实时终端缓冲区**
- **SFTP 文件路径和目录结构**
- **端口转发状态**
- **设置和知识库条目**（RAG，关键词 + 向量检索）

在这个基础上，它能执行已批准的 workspace 操作：下诊断、运行命令、检查文件、解释报错。

**BYOK-first**：OpenAI、Anthropic、Google、DeepSeek、Ollama 或任何兼容端点，自带 key，不经过 OxideTerm 服务器。核心 SSH/SFTP/终端功能不需要任何账号。

---

## 安全设计：OS keychain + 纯 Rust 密码学

企业级防护，不用买企业合同：

- **OS keychain**：密码和 API key 存在 macOS Keychain / Windows Credential Manager / Linux Secret Service，不写入任何配置文件
- **加密导出**：.oxide 格式用 ChaCha20-Poly1305 AEAD + Argon2id KDF（256 MB 内存，4 次迭代）
- **生物认证**：macOS 上 Touch ID 保护 keychain 访问
- **TOFU**：Trust-On-First-Use 主机密钥验证
- **内存清零**：敏感数据 drop 时立即归零

---

## 它和谁竞争

**vs iTerm2 + Termius + VSCode Remote**：OxideTerm 把这三个整合在一起，代价是还在早期，生态成熟度低于任何一个单独的工具。

**vs Warp**：Warp 有 AI 命令补全和 team 协作，但是 Electron，有遥测，需要账号。OxideTerm 更激进地本地优先，BYOK。

**vs Tabby**：Tabby 有更好的插件生态，但同样是 Electron。两者定位接近，OxideTerm 的 AI 层更深度集成。

**vs Zed**：不竞争，同用 GPUI 技术栈，都是 Rust 优先。Zed 是代码编辑器，OxideTerm 是远程工作台。

---

## 为什么值得关注

OxideTerm 还在 958 stars 的早期阶段（2026-01-21 创建）。它的技术选择很非主流——没有多少人愿意同时接受「零 Electron + 零 OpenSSL + GPUI」这三个约束——但这套约束组合在一起，指向了一个有意思的东西：**一个可以在 AI 时代重新定义远程工作环境的工具**。

OxideSens 看到整个 workspace 上下文这个设计，让 AI 能做的事比单纯的命令补全深很多——诊断生产服务器的问题时，它同时知道你的终端输出、当前打开的文件、端口转发状态。这个上下文宽度，是 Warp 或 Cursor 的 SSH 插件做不到的。

等它到 5000 stars，会是什么形态？

---

## 数据一览

| 属性 | 值 |
|---|---|
| Stars | 958（2026-07-19） |
| 创建时间 | 2026-01-21 |
| 语言 | Rust |
| 协议 | GPL-3.0 |
| UI 框架 | GPUI（Zed 同款） |
| SSH 库 | russh 0.61，ring backend |
| 包体大小 | 50–70 MB |
| C 依赖 | 零 |
| OpenSSL 依赖 | 零 |
| 主题数量 | 31+ |
| IDE 支持语言 | 36 种（tree-sitter） |
| 支持平台 | macOS / Windows / Linux |
| AI 模式 | BYOK（OpenAI/Anthropic/Google/DeepSeek/Ollama） |

© 2026 Author: Mycelium Protocol

<!--EN-->

## OxideTerm: The Zed of Terminals

**GitHub**: [AnalyseDeCircuit/oxideterm](https://github.com/AnalyseDeCircuit/oxideterm) · ⭐ 958 · Rust · GPL-3.0  
**Homepage**: [oxideterm.app](https://oxideterm.app)

### The Problem

Remote server work today requires 3–4 tools: a terminal (iTerm2/Warp), a connection manager + SFTP (Termius/RoyalTSX), a remote editor (VSCode Remote SSH), and something for port forwarding. Same server, four separate connections, scattered context.

OxideTerm's answer: put all four in one app, written in Rust, with no Electron and no OpenSSL.

### GPUI: Zed's Rendering Engine for Terminals

OxideTerm uses **GPUI** — the same native GPU rendering framework that powers Zed — not Tauri's WebView or Electron. GPU-backed Rust rendering, no web tech stack.

| App | UI layer | Package size |
|---|---|---|
| Electron terminals (Hyper/Tabby) | Node.js + Chromium | 150–300 MB |
| Tauri apps | WebView (OS-provided) | 5–20 MB |
| **OxideTerm** | **GPUI (native GPU Rust)** | **50–70 MB** |
| Zed | GPUI | ~60 MB |

Terminals are extremely latency-sensitive. Choosing GPUI — accepting the constraint of pure-Rust UI code with no React-style prototyping — trades development speed for rendering performance and no garbage collector.

### russh: Zero C Dependencies for SSH

Most SSH clients depend on OpenSSL or libssh2 (both C libraries). OxideTerm uses **russh 0.61** with the ring crypto backend — pure Rust.

- **Zero C dependencies**: the binary links no C code
- **Ciphers**: Ed25519, RSA, ECDSA keys; ChaCha20-Poly1305 and AES-GCM cipher suites
- **Memory safety**: sensitive memory zeroized on drop

Connection multiplexing: one SSH connection shared across terminal sessions, SFTP browsing, port forwarding, and the IDE — not four.

### Feature Map

**SSH Terminal**: split panes with broadcast to multiple sessions, session recording/playback (asciicast v2), 31+ themes, command palette (⌘K), zen mode.

**SFTP File Manager**: dual-pane with drag-and-drop, smart preview (images/video/audio/code/hex/fonts), transfer queue with real-time progress, watch mode with auto-upload on local save.

**Built-in IDE**: GPUI native editor, tree-sitter for 36 languages (Rust, Python, JS/TS, Go, C/C++, Java, YAML, JSON, TOML, Markdown, Shell), file tree with Git status, optional remote agent for Linux x86_64/aarch64.

**Port Forwarding**: local (-L), remote (-R), dynamic SOCKS5 (-D), lock-free message-passing I/O, auto-restore on reconnect, real-time bandwidth/latency monitoring.

**Local Shell**: zsh/bash/fish/pwsh/WSL2 beside SSH sessions in the same UI.

### OxideSens AI: Workspace-Aware BYOK Assistant

Unlike AI tools that only see what you're typing, OxideSens sees the full workspace: saved connections, live terminal buffers of active SSH sessions, SFTP file paths, port forwarding state, settings, and a RAG knowledge base (keyword + vector retrieval).

From that context it can diagnose remote output, run approved commands, inspect files, and explain failures.

**BYOK-first**: OpenAI, Anthropic, Google, DeepSeek, Ollama, or any compatible endpoint. Your key never touches OxideTerm's servers. Core SSH/SFTP/terminal features require no account.

### Security

- OS keychain for passwords and API keys (macOS Keychain / Windows Credential Manager / Linux Secret Service)
- .oxide encrypted exports: ChaCha20-Poly1305 AEAD + Argon2id KDF (256 MB memory, 4 iterations)
- Touch ID gates keychain access on macOS
- TOFU host key verification
- Sensitive memory zeroized on drop

### Competitive Landscape

**vs Warp**: Warp has AI command completion and team features, but it's Electron with telemetry and requires an account. OxideTerm is more aggressively local-first, BYOK.

**vs Tabby**: closest alternative — plugin ecosystem, but also Electron. OxideTerm's AI layer is deeper.

**vs Zed**: not competing — same GPUI stack, both Rust-first. Zed is a code editor; OxideTerm is a remote workspace.

### Why Watch It

OxideTerm is early (958 stars, created January 2026). The technical bet — zero Electron + zero OpenSSL + GPUI — is unconventional. But the combination of a workspace-aware AI (OxideSens sees your terminal buffer, open files, port forwarding state simultaneously) with a native-performance app is a genuinely different take on what an AI-era remote development environment should look like. The context width OxideSens has access to is something neither Warp nor Cursor's SSH plugin can match.

© 2026 Author: Mycelium Protocol
