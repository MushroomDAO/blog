---
title: "Unsloth Desktop 正式发布：一个 App 搞定本地运行、训练、部署，直连 Claude Code 和 MCP"
titleEn: "unsloth-desktop-local-run-train-ai-claude-code-mcp-finetuning"
description: "unslothai/unsloth 发布首个桌面应用 Unsloth Desktop（v0.1.801-beta），74K stars。一个 App 集成本地大模型运行（LLM/扩散/音频/嵌入）、微调训练（LoRA/QLoRA/GRPO/DPO，2x 提速，省 70% 显存）、Claude Code/Codex/MCP 接入（一条命令 unsloth start claude）、私有 Web 搜索、RAG、图像/视频生成、Data Recipes 数据集构建、OpenAI 兼容 API 服务。支持 CPU/Apple Silicon/NVIDIA/AMD/Intel/多 GPU，Cloudflare HTTPS 远程访问。导出 GGUF/NVFP4/FP8 格式。"
descriptionEn: "unslothai/unsloth ships its first desktop app (v0.1.801-beta), 74K stars. One app covers: local model inference (LLM/diffusion/audio/embedding), finetuning (LoRA/QLoRA/GRPO/DPO, 2x faster, 70% less VRAM), Claude Code/Codex/MCP integration (one command: unsloth start claude), private web search, RAG, image/video generation, Data Recipes dataset building, and an OpenAI-compatible API server. Supports CPU/Apple Silicon/NVIDIA/AMD/Intel/multi-GPU, Cloudflare HTTPS for remote access. Exports to GGUF/NVFP4/FP8."
pubDate: "2026-08-21"
updatedDate: "2026-08-21"
category: "Tech-News"
tags: ["本地AI", "微调", "Claude Code", "MCP", "Unsloth", "大模型", "Apple Silicon", "开源"]
heroImage: "../../assets/images/unsloth-desktop-local-run-train-ai-claude-code-mcp-finetuning-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：unslothai/unsloth  
官网：unsloth.ai  
版本：v0.1.801-beta  
Stars：74K+  
许可证：Apache 2.0  
平台：Windows、macOS、Linux（deb/AppImage/ARM64）

---

Unsloth 以「让 Llama 微调快 2 倍、省 70% 显存」起家，74K stars。这次他们把几年积累的工程做成了一个桌面 App，直接发布。

核心主张很简单：**本地运行 + 本地训练 + 接 Claude Code，全在一个 App 里，彻底告别云端依赖。**

---

## 一、安装

```bash
# macOS / Linux 通用
curl -fsSL https://unsloth.ai/install.sh | sh
```

Windows 用 PowerShell：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://unsloth.ai/install.ps1 | iex"
```

也提供平台独立安装包：
- macOS：`.dmg`
- Linux：`.deb`、`.AppImage`、ARM64 二进制
- Windows：`.exe`

安装完之后，所有功能从一个 App 入口进入。

---

## 二、接 Claude Code：一条命令

```bash
unsloth start claude
```

这条命令让 **Claude Code、Codex** 以及其他任何 MCP 兼容的 Agent 直接连接本地运行的模型，无需配置 API Key，无需云端代理。

支持的 Agent 接入方式：
- **Claude Code** — `unsloth start claude`
- **Codex CLI** — `unsloth start codex`
- **MCP 兼容客户端** — OpenAI 兼容 API 端口，插上就能用
- **工具调用（Tool Calling）** — 支持，在本地模型上
- **代码执行** — 支持
- **Web 搜索（私有）** — 支持，不经过第三方

这意味着 Claude Code 可以把本地运行的 Qwen3.8、DeepSeek-V4、Gemma 4 等模型当成推理后端使用，整个链路在机器本地闭环。

---

## 三、支持的模型

Unsloth Desktop 明确支持：

| 类别 | 代表模型 |
|------|---------|
| 语言模型 | Qwen3.8、Kimi K3、MiniMax-H3、DeepSeek-V4、Gemma 4、Llama 4 |
| 扩散图像 | FLUX 系列 |
| 视频生成 | Muse Glimmer |
| 音频模型 | 嵌入/音频类模型 |
| 嵌入模型 | RAG 所需的向量嵌入 |

---

## 四、推理能力

**硬件支持**（所有主流硬件，开箱即用）：

- CPU（含低端机器）
- Apple Silicon（Metal）
- NVIDIA GPU（CUDA）
- AMD GPU
- Intel GPU
- 多 GPU 并行

**远程访问**：内置 Cloudflare HTTPS 通道，手机/平板可以远程连自己家里的机器跑推理，不需要开放端口或配置 VPN。

**OpenAI 兼容 API**：本地起服务之后，任何支持 OpenAI API 的工具直接对接，不需要改代码。

---

## 五、训练能力

Unsloth 的技术积累全部打包进了桌面版：

**核心指标**：
- 微调速度比 HuggingFace 标准路径快 **2x**
- 显存占用少 **70%**（LoRA / QLoRA）
- 无精度损失

**支持的训练方法**：

| 方法 | 适用场景 |
|------|---------|
| LoRA | 参数高效微调，最常用 |
| QLoRA | 量化基础上的 LoRA，节省更多显存 |
| 全量微调 | 有条件的高端配置 |
| 预训练 | 从头或继续预训练 |
| GRPO | 强化学习微调（同 DeepSeek-R1 路线） |
| DPO | 偏好对齐 |
| FP8 | 量化感知训练 |

**Data Recipes**：把 PDF、CSV、DOCX 转成训练数据集，不需要写数据处理脚本。

**导出格式**：GGUF、NVFP4、FP8——直接导出可部署的量化格式。

---

## 六、RAG 与搜索

- **RAG（检索增强生成）**：本地文档检索，和本地模型配合使用
- **私有 Web 搜索**：不经过第三方，搜索内容不上传
- **Deep Research**：长上下文研究任务支持

---

## 七、背景

Unsloth 2023 年从 GPU 穷人优化工具开始——在消费级显卡上跑 Llama 微调，比官方路径快、省显存。74K stars 说明这个需求有多真实。

桌面版做的事是：把这些底层工程打包成不需要配置的一站式体验。目标用户从「会写 Python 的研究者」扩展到「想在本地玩 AI 但不想配环境的所有人」。

`unsloth start claude` 这个设计值得注意。它把本地模型和代码 Agent 的接入做成了一条命令——不是「教你怎么配」，而是「帮你配好」。对于已经在用 Claude Code 或 Codex 的开发者，这意味着可以把部分工作负载切到完全本地的模型，不需要改工作流。

目前是 beta 版（v0.1.801-beta），功能会继续迭代。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Unsloth Desktop: Run, Train, and Deploy AI Locally — One App, Direct Claude Code Integration

*by Mycelium Protocol*

---

GitHub: unslothai/unsloth  
Site: unsloth.ai  
Version: v0.1.801-beta  
Stars: 74K+  
License: Apache 2.0  
Platforms: Windows, macOS, Linux (deb/AppImage/ARM64)

---

Unsloth built its reputation on making Llama finetuning 2x faster and 70% more memory-efficient. 74K stars later, they've packaged years of engineering into a desktop app.

The pitch is direct: **run models locally, train them locally, connect to Claude Code — all in one app, no cloud dependency required.**

---

### Installation

```bash
# macOS / Linux
curl -fsSL https://unsloth.ai/install.sh | sh
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://unsloth.ai/install.ps1 | iex"
```

Platform packages also available: `.dmg` (macOS), `.deb`/`.AppImage`/ARM64 binary (Linux), `.exe` (Windows).

---

### Connecting Claude Code: One Command

```bash
unsloth start claude
```

This single command connects Claude Code, Codex, and any MCP-compatible agent to your locally running models — no API key, no cloud proxy required.

Supported agent integrations:
- **Claude Code** → `unsloth start claude`
- **Codex CLI** → `unsloth start codex`
- **MCP clients** → OpenAI-compatible local API endpoint
- **Tool calling** — supported on local models
- **Code execution** — supported
- **Private web search** — supported, no third-party data exposure

Claude Code can use locally running Qwen3.8, DeepSeek-V4, Gemma 4 and others as inference backends. The entire chain stays on-device.

---

### Supported Models

| Category | Representative Models |
|----------|----------------------|
| Language | Qwen3.8, Kimi K3, MiniMax-H3, DeepSeek-V4, Gemma 4, Llama 4 |
| Image diffusion | FLUX series |
| Video | Muse Glimmer |
| Audio | Embedding and audio models |
| Embedding | For local RAG |

---

### Inference

**Hardware support** (all major platforms, no manual configuration):

CPU · Apple Silicon (Metal) · NVIDIA (CUDA) · AMD · Intel · Multi-GPU

**Remote access**: Built-in Cloudflare HTTPS tunnel — connect from your phone or tablet to your home machine without port forwarding or VPN.

**OpenAI-compatible API**: Any tool that speaks the OpenAI API connects directly to the local server.

---

### Training

Unsloth's core performance work ships in the desktop build:

**Baseline performance**:
- 2x faster than standard HuggingFace finetuning paths
- 70% less VRAM (LoRA / QLoRA)
- No accuracy loss

**Training methods supported**:

| Method | Use case |
|--------|---------|
| LoRA | Parameter-efficient finetuning |
| QLoRA | LoRA on quantized base, maximum memory savings |
| Full finetuning | High-end hardware setups |
| Pretraining | From scratch or continuation |
| GRPO | RL finetuning (same approach as DeepSeek-R1) |
| DPO | Preference alignment |
| FP8 | Quantization-aware training |

**Data Recipes**: Convert PDFs, CSVs, and DOCX files into training datasets without writing data-processing scripts.

**Export formats**: GGUF, NVFP4, FP8 — deployable quantized formats out of the box.

---

### RAG and Search

- **Local RAG**: Document retrieval paired with local inference
- **Private web search**: No third-party data exposure
- **Deep Research**: Long-context research task support

---

### Context

Unsloth started as a GPU optimization tool for researchers — making Llama finetuning run on consumer hardware faster and with less memory. 74K stars reflect how real that demand was.

The desktop app extends the target user: from "researchers who can write Python" to "anyone who wants local AI without configuring an environment."

The `unsloth start claude` design is notable. It makes the connection between a local model and a coding agent into one command — not a configuration guide, but a solved problem. For developers already using Claude Code or Codex, this means routing some workloads to fully local models without changing the workflow.

Currently in beta (v0.1.801-beta). Actively developed.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
