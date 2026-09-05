---
title: "tnk：给本地 LLM 和 AI Coding Agent 配一个零信任沙箱，而不是又一个推理引擎"
titleEn: "tnk: A Zero-Trust Sandbox for Local LLMs and AI Coding Agents, Not Another Inference Engine"
description: "调研开源项目 tnk（tappunk/tnk）：Rust 写的每项目零信任沙箱 VM，用 Lima 给本地 LLM 和 AI coding agent 提供隔离，只挂载项目工作区、屏蔽宿主密钥。MIT 协议，目前 3 star，标注为 experimental。它自己不管推理引擎（不是 Ollama/llama.cpp 的替代品），只解决\"agent 跑 shell 命令、装包、连网络时，宿主机能不能不被牵连\"这一个问题——这正是本站之前写本地 agent 文章时漏掉的一个维度。文中记录了完整安装、启动、验证步骤和值得注意的边界。"
descriptionEn: "A hands-on look at tnk (tappunk/tnk), a Rust-built per-project zero-trust sandbox VM for local LLM inference and AI coding agents, built on Lima. It mounts only the project workspace and keeps host secrets out of scope. MIT licensed, 3 stars, marked experimental. It does not manage the inference engine itself — it is not a replacement for Ollama or llama.cpp — it solves exactly one problem: keeping the host machine out of scope when an agent runs shell commands, installs packages, or talks to the network. That is a dimension this blog's earlier local-agent coverage never addressed. This post walks through install, boot, and verification, plus the boundaries worth knowing before you rely on it."
pubDate: "2026-09-05"
updatedDate: "2026-09-05"
category: "Tech-Experiment"
tags: ["本地LLM", "AI Agent", "沙箱隔离", "Rust", "Lima VM", "开源工具", "本地优先"]
heroImage: "../../assets/images/tnk-zero-trust-sandbox-local-llm-agent-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/tappunk/tnk
文档：https://tappunk.com/tnk/
授权：MIT

---

## 一句话结论

**tnk 不是又一个本地推理引擎，它是给本地 LLM 和 AI coding agent 配的一个"隔离壳"**：每个项目起一个独立的 Lima 虚拟机，只挂载这个项目的工作区目录，宿主机的密钥、其他项目的文件、SSH 配置一律不进沙箱。推理仍然跑在宿主机上——tnk 通过环境变量（`TNK_INFERENCE_URL`、`TNK_MODEL_NAME`、`TNK_ENGINE_RUNTIME`）把端点和模型信息递给沙箱，自己完全不碰推理这一层。Rust 写的，MIT 协议，README 里作者自己标了 `(experimental)`，仓库 3 star、0 fork、0 issue，7 月 7 日建仓，9 月 3 日还在提交。

## 为什么这个问题值得单独拿出来讲

本站写过不少本地优先的 agent 文章，但基本都在回答"模型怎么跑起来""agent 怎么调用工具"，很少有人正面回答一个更朴素的问题：**当你让一个 AI coding agent 在你的电脑上跑 shell 命令、装依赖包、访问网络时，出了问题谁兜底？**

agent 执行安装脚本、写文件、发网络请求，这些动作本身跟人手敲命令没有权限区别——如果 agent 判断错误或者被 prompt injection 带偏，波及的是整台宿主机：`~/.ssh`、`~/.aws`、浏览器 cookie、其他项目的代码，都在同一个用户权限下暴露着。tnk 解决的正是这一层，跟"选哪个模型""怎么写 prompt"完全正交。

## 它是怎么做隔离的

tnk 的机制不是容器（namespace 级隔离），而是**每个项目一个 Lima 虚拟机**——Lima 是跑在 macOS/Linux 上的轻量 Linux VM 工具（背后是 QEMU 或 Apple 的 Virtualization.framework），比 Docker 容器多一层真实的内核边界。具体拆解：

- **每项目一个 VM**：只挂载当前项目的工作区目录，其它一切（宿主密钥、SSH、别的项目）默认不可见。
- **声明式 provisioning**：从 `sandbox.d/provision.d` 读配置，按 profile 走不同的初始化脚本，可复用。
- **会话审计日志**：可选的 NDJSON 格式日志，出了问题能做取证复盘。
- **机器可读输出**：`list` 类命令支持 `--output json|ndjson`，方便接自己的脚本或 CI。

tnk 自己不跑模型——推理服务器（Ollama、llama.cpp、vLLM 或任何 OpenAI 兼容端点）仍然跑在宿主机上，沙箱只是通过环境变量拿到端点地址去调用，这是它跟"本地推理框架"划清界限的地方：**tnk 管的是执行环境的隔离，不是推理引擎的选择**。

## 装上跑一遍

```bash
# 1. 安装（Homebrew 或 cargo 二选一）
brew tap tappunk/tap
brew trust tappunk/tap        # 较新版本 Homebrew 需要这一步
brew install tappunk/tap/tnk
# 或者：cargo install tnk

# 2. 初始化配置
tnk init                      # 从 tnk-specs populate ~/.config/tnk
tnk config init               # 生成 ~/.config/tnk/tnk.toml
```

在 `~/.config/tnk/tnk.toml` 里指向你本机的推理服务：

```toml
default_model = "ai-fast"     # 对应你本地推理服务里的模型名
```

然后在项目目录里启动沙箱：

```bash
cd ~/code/myproject
tnk sandbox start             # 起 VM，按默认 profile provision
tnk sandbox shell             # 进入沙箱
```

进去之后，agent 在里面跑的所有命令都发生在这台一次性 VM 里，宿主机的密钥和其它目录不在它的视野范围内。其余常用命令：

```bash
tnk                  # 列出当前所有沙箱
tnk run              # 启动项目沙箱（同 sandbox start 的简写路径）
tnk shutdown         # 关掉所有沙箱
tnk doctor           # 环境健康检查
tnk config show      # 查看生效配置
```

## 现在就能不能重度依赖它？

**还不行，起码不是现在。** 三个理由：

1. **作者自己标了 experimental**，README 第一行就是 "tnk (experimental)"，不是谦虚，是明确的稳定性预期管理。
2. **3 star、0 fork、0 open issue**——目前几乎没有外部使用反馈，安全类工具最怕的就是"威胁模型只有作者自己验证过"。
3. **依赖 Lima**，也就意味着目前主要面向 macOS（Lima 在 Linux 上也能跑，但生态和文档明显是 macOS 优先），Windows 用户目前用不上。

但它值得现在就装一个来试：本地跑 agent 写代码这件事，`sandbox.d/provision.d` 这种声明式配置和"每项目一个 VM、只挂工作区"的默认姿势，是本站之前写的本地 agent 文章里都没覆盖到的一层防护，跟你已经在用的任何推理框架都不冲突，装上试试的成本很低。

## 常见问题

**tnk 会不会拖慢本地 agent 的响应速度？** VM 启动比容器慢，但推理本身仍在宿主机跑（沙箱只是转发请求），日常交互延迟主要看你的推理引擎，不是 tnk 本身。

**能不能跟 Ollama/llama.cpp 一起用？** 可以，而且这是官方设计的用法——tnk 从不管理推理引擎，只需要把 `TNK_INFERENCE_URL` 指向你已经在跑的推理服务即可。

**跟 Docker 沙箱方案（比如给 agent 用的容器隔离）比呢？** VM 级隔离的边界比容器 namespace 更硬，代价是启动开销更大；如果你只是想防"agent 手滑写坏了当前项目文件"，容器可能已经够用，tnk 面向的是更看重宿主机密钥/凭据不被波及的场景。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Project: https://github.com/tappunk/tnk
Docs: https://tappunk.com/tnk/
License: MIT

---

## TL;DR

**tnk is not another local inference engine — it's an isolation shell for local LLMs and AI coding agents.** Each project gets its own Lima virtual machine that mounts only that project's workspace directory; host secrets, other projects' files, and SSH configuration never enter the sandbox. Inference still runs on the host — tnk hands the sandbox the endpoint and model coordinates through environment variables (`TNK_INFERENCE_URL`, `TNK_MODEL_NAME`, `TNK_ENGINE_RUNTIME`) and never touches the inference layer itself. Written in Rust, MIT licensed, the README itself tags it `(experimental)`. The repo has 3 stars, 0 forks, 0 open issues, was created on 2026-07-07, and still had a commit on 2026-09-03.

## Why this problem deserves its own post

This blog has covered plenty of local-first agent tooling, but almost all of it answers "how do you run the model" or "how does the agent call tools." Few pieces address a plainer question: **when you let an AI coding agent run shell commands, install dependencies, and hit the network on your own machine, who's on the hook if something goes wrong?**

An agent executing an install script, writing files, or making network requests carries the same permissions as you typing the same commands by hand. If the agent misjudges something, or gets steered off course by prompt injection, the blast radius is the whole host machine — `~/.ssh`, `~/.aws`, browser cookies, and every other project's code sit exposed under the same user account. tnk addresses exactly this layer, and it's orthogonal to "which model" or "how you write the prompt."

## How the isolation actually works

tnk's mechanism isn't a container (namespace-level isolation) — it's **one Lima virtual machine per project**. Lima is a lightweight Linux-VM tool for macOS/Linux (backed by QEMU or Apple's Virtualization.framework), which gives you a real kernel boundary on top of what Docker containers offer. The pieces:

- **One VM per project**, mounting only the current project's workspace directory — everything else (host secrets, SSH, other projects) is invisible by default.
- **Declarative provisioning** read from `sandbox.d/provision.d`, driven by reusable per-profile init scripts.
- **Optional session audit trail** in NDJSON format for forensic review after the fact.
- **Machine-readable output** — `list`-style commands support `--output json|ndjson` for scripting or CI.

tnk itself doesn't run any model — the inference server (Ollama, llama.cpp, vLLM, or any OpenAI-compatible endpoint) still runs on the host, and the sandbox just calls it through the endpoint address it's handed via environment variables. That's the line tnk draws against being confused with a "local inference framework": **it manages isolation of the execution environment, not the choice of inference engine.**

## Installing and running it

```bash
# 1. Install (Homebrew or cargo)
brew tap tappunk/tap
brew trust tappunk/tap        # required on recent Homebrew versions
brew install tappunk/tap/tnk
# or: cargo install tnk

# 2. Initialize config
tnk init                      # populate ~/.config/tnk from tnk-specs
tnk config init                # create ~/.config/tnk/tnk.toml
```

Point it at your host's inference server in `~/.config/tnk/tnk.toml`:

```toml
default_model = "ai-fast"     # matches a model name your local inference server serves
```

Then, from inside a project directory:

```bash
cd ~/code/myproject
tnk sandbox start             # boots the VM, provisions the default profile
tnk sandbox shell             # enter the sandbox
```

Once inside, every command the agent runs happens inside that disposable VM — host secrets and other directories are simply out of view. Other everyday commands:

```bash
tnk                  # list all sandboxes
tnk run              # start the project sandbox (shorthand path)
tnk shutdown         # stop all sandboxes
tnk doctor           # environment health checks
tnk config show      # inspect effective configuration
```

## Should you rely on it right now?

**Not yet, or at least not heavily.** Three reasons:

1. **The author labels it experimental themselves** — the first line of the README reads "tnk (experimental)." That's not modesty; it's explicit expectation-setting about stability.
2. **3 stars, 0 forks, 0 open issues** — essentially no outside usage feedback yet, and for a security-oriented tool, "the threat model has only been validated by the author" is exactly the risk you want to be cautious about.
3. **It depends on Lima**, which means today it's mostly a macOS story (Lima runs on Linux too, but the docs and ecosystem are clearly macOS-first) — Windows users are out of luck for now.

That said, it's worth installing and trying today: the "one VM per project, mount only the workspace" default posture, plus declarative `sandbox.d/provision.d` configs, is a layer of protection this blog's earlier local-agent coverage never touched. It doesn't conflict with whatever inference framework you're already running, and the cost of trying it is low.

## FAQ

**Will tnk slow down my local agent's response time?** VM boot is slower than a container's, but inference itself still runs on the host — the sandbox just forwards requests — so day-to-day latency depends on your inference engine, not tnk.

**Can I use it alongside Ollama or llama.cpp?** Yes, and that's the intended usage — tnk never manages the inference engine; you just point `TNK_INFERENCE_URL` at whatever inference service you're already running.

**How does it compare to Docker-based agent sandboxes?** VM-level isolation draws a harder boundary than container namespaces, at the cost of higher startup overhead. If you just want to stop an agent from accidentally trashing the current project's files, a container may already be enough; tnk is aimed at scenarios where keeping host secrets and credentials out of scope matters more.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
