---
title: "Realtime-Venus：全双工 AI 交互系统本地部署指南，双 Loop 架构 + 9B Omni 模型开源"
titleEn: "Realtime-Venus Local Deployment Guide: Full-Duplex AI with Dual-Loop Architecture and Open 9B Omni Model"
description: "蚂蚁集团 + 清华开源，Apache-2.0。Realtime-Venus-Omni（9B）和 Realtime-Venus-Audio（9B）权重完全公开，含 Harness 运行时和 Web Demo 代码。双 Loop 架构：实时感知+语音交互与后台任务执行分离，Codex CLI 作为默认任务后端（外部依赖，可替换）。需 A100 级显卡，训练数据未开放。"
descriptionEn: "Open-sourced by Ant Group + Tsinghua under Apache-2.0. Realtime-Venus-Omni (9B) and Realtime-Venus-Audio (9B) weights freely downloadable. Includes Harness runtime and Web Demo code. Dual-loop: real-time perception/voice and async background tasks run separately. Codex CLI is the default task backend (external dep, swappable). Requires A100-class GPU. Training data not released."
pubDate: 2026-09-20
heroImage: "../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-banner.jpg"
category: "Tech-Experiment"
tags: ["full-duplex", "voice-ai", "local-deploy", "omni-model", "agent", "open-source"]
lang: zh-CN
---

[Realtime-Venus](https://github.com/inclusionAI/Realtime-Venus) 是蚂蚁集团 + 清华大学团队于 2026-09-12 开源的全双工 AI 交互系统，Apache-2.0 协议。两个 9B 模型的权重可在 HuggingFace 直接下载，Harness 运行时和 Web Demo 代码一并开源。

**仓库**：github.com/inclusionAI/Realtime-Venus | **HuggingFace**：huggingface.co/inclusionAI/Realtime-Venus | **arXiv**：arxiv.org/abs/2609.13814 | **License**：Apache-2.0

---

## 什么是双 Loop 架构

普通语音 AI 是"问一句答一句"——用户说话时模型处于等待状态，回答时用户不能打断，后台任务（查文件、跑代码）会阻塞整个对话。Realtime-Venus 把这条串行链拆成两条并行 Loop：

```
Loop 1（前台）：持续感知 → 音视频理解 → 实时响应 → 主动打招呼
Loop 2（后台）：委托任务 → Harness 接管 → 任务执行 → 完成后插回对话
```

Loop 1 永不停止——用户沉默时它持续感知画面和环境声音；Loop 2 异步运行——"帮我写个脚本"被委托出去后，前台 Loop 继续保持对话，后台完成时主动报告结果。

---

## 开源了什么

| 组件 | 状态 | 说明 |
|------|------|------|
| Realtime-Venus-Omni 权重（9B） | **开放** Apache-2.0 | SigLIP2 视觉 + Whisper-Medium 音频 + Qwen3-8B 主干 |
| Realtime-Venus-Audio 权重（9B） | **开放** Apache-2.0 | 同主干，去掉视觉编码器，显存占用更小 |
| Harness 运行时代码 | **开放** Apache-2.0 | Python 包，Capture/Dispatch/Return 三段流水线 |
| Web Demo 代码 | **开放** Apache-2.0 | launcher + model server + 静态浏览器 UI |
| 前端推理脚本 | **开放** Apache-2.0 | Omni 和 Audio 各一套 |
| arXiv 论文 | **开放** | arxiv.org/abs/2609.13814 |
| 训练数据 | **未开放** | — |
| 托管 Demo | **不存在** | 没有云端在线体验入口 |
| 任务后端（Codex CLI） | **外部依赖** | 见下文说明 |

---

## 两个模型的区别

**Realtime-Venus-Omni**（推荐用于完整场景）：
- 三路输入：视频帧（SigLIP2）+ 音频（Whisper-Medium）+ 文本
- 支持持续感知（用户不说话时仍然理解画面变化）
- 含 Memory Adapter，跨轮次积累上下文
- BF16 safetensors 分片；含参考声音文件和 Token2wav 流式解码器

**Realtime-Venus-Audio**（显存受限时使用）：
- 去掉视觉编码器，仅处理音频 + 文本
- 与 Omni 相同的 Qwen3-8B 主干
- 显存需求更低，适合纯语音交互场景

---

## 硬件要求

**实际全双工模式需要 A100 级显卡**。两个 9B 模型 BF16 权重合计约 18GB。同时运行双 Loop 的显存和实时性要求不是消费级 GPU 能满足的。

| 配置 | 能力 |
|------|------|
| A100/H100 | 完整双 Loop + 全双工实时交互 |
| RTX 4090（24GB） | 单模型测试可运行，实时性存疑 |
| Mac Apple Silicon（64GB+） | 可尝试 CPU+MPS 混合推理，速度不够实时 |
| < 24GB 消费级 GPU | 不推荐尝试全双工 |

---

## 下载模型

```bash
# 通过 huggingface-cli（推荐）
pip install huggingface_hub
huggingface-cli download inclusionAI/Realtime-Venus --local-dir ./realtime-venus-weights

# 或通过 ModelScope（中国大陆网络更稳定）
pip install modelscope
modelscope download --model inclusionAI/Realtime-Venus --local-dir ./realtime-venus-weights
```

ModelScope 镜像地址：modelscope.cn/models/inclusionAI/Realtime-Venus

---

## 克隆仓库并安装依赖

```bash
git clone https://github.com/inclusionAI/Realtime-Venus.git
cd Realtime-Venus

# 安装 Harness 运行时（Python 3.11/3.12 推荐）
pip install -e .

# 或直接安装 harness 包
pip install -e ./harness
```

---

## 运行 Web Demo

Demo 架构：`launcher/`（进程管理）→ `model/`（模型服务）→ `server/`（Web 后端）→ `static/`（浏览器 UI），默认监听 localhost:8032。

```bash
# 复制配置示例
cp config.example.json config.json

# 编辑 config.json，填写模型路径
# model_path 指向你下载的 realtime-venus-weights 目录

# 一键启动（launcher 负责拉起其余进程）
bash start.sh
```

然后访问 http://localhost:8032 打开浏览器 UI。

---

## ⚠️ Codex CLI 依赖说明

Web Demo 的"后台任务执行"功能默认连接 **OpenAI Codex CLI**（版本 0.153.4+），通过 `agents/codex.py` 里的 `CodexAgentProvider` 实现。这意味着：

- 你需要单独安装 Codex CLI 并完成 OpenAI 授权
- Demo 开箱后端不是自给自足的——任务委托部分依赖外部服务
- 如果不接 Codex，Demo 的 Loop 1（实时感知+语音）仍然可以运行，但 Loop 2（异步任务委托）会失败

**替换方法**：`GeneralAgentPort` 接口有文档，可以接入任意兼容的 CLI Agent。理论上可以替换为本地运行的 Claude Code 或其他工具，但需要自己实现适配器。

---

## 只运行推理脚本（不启动 Demo）

如果只想测试模型对话，不需要完整 Demo 栈：

```bash
# Omni 模型（音视频+文本输入）
python frontend/omni_inference.py \
  --model-path ./realtime-venus-weights/Realtime-Venus-Omni \
  --audio input.wav \
  --video input.mp4

# Audio 模型（仅音频）
python frontend/audio_inference.py \
  --model-path ./realtime-venus-weights/Realtime-Venus-Audio \
  --audio input.wav
```

具体参数以仓库 `frontend/` 下的实际脚本为准，发布后可能有调整。

---

## Harness 工作原理

Harness 是双 Loop 架构里负责 Loop 2 的 Python 包，分三段：

**1. Capture**（`core/`）：
- 检测对话中出现的 `<delegate>…</delegate>` 标签
- 验证证据边界，注册任务 Session
- 确认任务适合异步委托

**2. Dispatch**（`agents/`、`jobs/`、`llm/`、`skills.py`）：
- 根据任务类型路由到三条通道：多模态直接回答 / 通用任务执行器 / 注册 Skill
- 通用执行器默认是 Codex CLI，可替换

**3. Return**（`bridge/`）：
- 准备口语化的完成回报
- 检查对话时机（不打断用户讲话）
- 在合适的边界注入 `<backend>…</backend>` 结果标签，插回 Loop 1

---

## 不足之处

**1. 训练数据未开放**：论文描述了训练方法，但没有配套数据集。无法复现训练，也无法微调。

**2. 实际全双工需要 A100**：消费级显卡可以运行推理，但无法达到实时全双工的延迟要求。官方没有提供量化版本。

**3. Codex CLI 不是自带的**：默认后端是外部商业服务，不是 Ant Group 的开源组件。系统"不完全自给自足"，除非自己接替代执行器。

**4. 发布安静**：GitHub 仅 22 stars，没有任何官方博客文章或社区推广。没有 Hugging Face 上的 Space 演示，没有托管在线体验。

**5. 量化版本缺失**：暂无官方 GGUF、GPTQ 或 MLX 版本，低显存设备没有官方路径。

---

## 怎么看这件事

Realtime-Venus 是目前能找到的少数真正把"持续感知+异步委托"两条 Loop 分离开来做成工程实现的开源系统。架构思路清晰，Harness 代码设计有参考价值——特别是 Capture/Dispatch/Return 三段和 `<delegate>` 标签约定，可以用来构建自己的双 Loop 框架。

实际部署门槛高：需要 A100、需要自己解决 Codex 后端或写替代适配器、没有量化版本。目前更适合作为架构参考和研究起点，而不是直接上生产。如果你关注全双工 AI 交互的工程路线，这个仓库值得深看。

> 代码与模型仅供学习研究，请遵守 Apache-2.0 协议。不构成生产部署建议，实际使用请评估显存/延迟需求。

---

<!--EN-->

## Realtime-Venus Local Deployment Guide

[Realtime-Venus](https://github.com/inclusionAI/Realtime-Venus) is a full-duplex AI interaction system open-sourced on 2026-09-12 by Ant Group and Tsinghua University under Apache-2.0. Both 9B model weights are freely downloadable on HuggingFace, and the Harness runtime plus Web Demo code are fully open.

**Repo**: github.com/inclusionAI/Realtime-Venus | **HuggingFace**: huggingface.co/inclusionAI/Realtime-Venus | **arXiv**: arxiv.org/abs/2609.13814 | **License**: Apache-2.0

---

### The Dual-Loop Architecture

Standard voice AI is serial — model waits while user speaks, user can't interrupt while model responds, background tasks block the whole conversation. Realtime-Venus splits this into two parallel loops:

```
Loop 1 (foreground): continuous perception → audio/video understanding → real-time response → proactive engagement
Loop 2 (background): delegated task → Harness → async execution → inject result back into conversation
```

Loop 1 never stops — it keeps sensing the scene even when the user is silent. Loop 2 runs asynchronously — "write me a script" gets delegated out while the foreground loop continues the conversation, and Loop 2 reports back when done.

---

### What's Open-Sourced

| Component | Status | Notes |
|-----------|--------|-------|
| Realtime-Venus-Omni weights (9B) | **Open** Apache-2.0 | SigLIP2 visual + Whisper-Medium audio + Qwen3-8B backbone |
| Realtime-Venus-Audio weights (9B) | **Open** Apache-2.0 | Same backbone, vision removed, lower VRAM |
| Harness runtime | **Open** Apache-2.0 | Python package, Capture/Dispatch/Return pipeline |
| Web Demo code | **Open** Apache-2.0 | launcher + model server + static browser UI |
| Inference scripts | **Open** Apache-2.0 | One set each for Omni and Audio |
| arXiv paper | **Open** | arxiv.org/abs/2609.13814 |
| Training data | **Not released** | — |
| Hosted demo | **Doesn't exist** | No cloud endpoint available |
| Task backend (Codex CLI) | **External dependency** | See below |

---

### Two Models

**Realtime-Venus-Omni** (recommended for full use): three-input (video frames via SigLIP2, audio via Whisper-Medium, text), continuous perception, Memory Adapter for cross-turn context, BF16 safetensors, reference voice file, Token2wav streaming decoder.

**Realtime-Venus-Audio** (VRAM-constrained): same Qwen3-8B backbone, vision encoder removed, lower VRAM footprint, voice-only interaction.

---

### Hardware Requirements

**Full-duplex real-time mode requires A100-class GPU.** Two 9B BF16 models total ~18 GB. Consumer GPUs (< 24 GB) can run inference but not real-time dual-loop simultaneously. No official quantized builds exist yet.

---

### Download

```bash
# HuggingFace CLI
huggingface-cli download inclusionAI/Realtime-Venus --local-dir ./realtime-venus-weights

# ModelScope (better connectivity from mainland China)
modelscope download --model inclusionAI/Realtime-Venus --local-dir ./realtime-venus-weights
```

---

### Setup and Run Demo

```bash
git clone https://github.com/inclusionAI/Realtime-Venus.git
cd Realtime-Venus
pip install -e .
cp config.example.json config.json
# edit config.json: set model_path to your downloaded weights
bash start.sh
# open http://localhost:8032
```

---

### ⚠️ Codex CLI Dependency

The default general-purpose task executor in Loop 2 is **OpenAI Codex CLI** (v0.153.4+), connected via `agents/codex.py` (`CodexAgentProvider`). You need to install Codex CLI and authenticate with OpenAI separately. Without it, Loop 1 (real-time perception and voice) still works, but Loop 2 (async task delegation) will fail.

The `GeneralAgentPort` interface is documented and extensible — you can plug in any compatible CLI agent (e.g., Claude Code locally). You'd need to write the adapter yourself.

---

### How the Harness Works

The Harness Python package drives Loop 2 in three stages:

- **Capture** (`core/`): detects `<delegate>…</delegate>` spans, validates evidence boundaries, registers the session
- **Dispatch** (`agents/`, `jobs/`, `llm/`, `skills.py`): routes to multimodal direct answer, general task executor (Codex by default), or a registered skill
- **Return** (`bridge/`): prepares spoken completion report, waits for a conversation gap, injects `<backend>…</backend>` result back into Loop 1

---

### Limitations

1. **Training data not released** — can't reproduce training or fine-tune.
2. **A100 required for real-time** — consumer GPUs can run inference but not full-duplex in real time.
3. **Codex is an external commercial service** — the system is not fully self-contained out of the box.
4. **Quiet release** — 22 GitHub stars, no official blog post, no hosted demo, no HuggingFace Space.
5. **No quantized builds** — no official GGUF, GPTQ, or MLX versions yet.

---

### Bottom Line

Realtime-Venus is one of the few open-source systems that actually implements the dual-loop separation between continuous perception and async task delegation as a working engineering artifact. The Harness architecture (Capture/Dispatch/Return, the `<delegate>` tag protocol) is the most reusable part — useful as a reference for building your own asynchronous agent interaction systems.

Deployment barrier is real: A100 required, Codex backend needs separate setup, no quantized builds available. Best treated as an architecture reference and research starting point rather than a production-ready drop-in.

> Code and models for research and learning only. Please comply with the Apache-2.0 license. This is not a production deployment recommendation — evaluate your own VRAM and latency requirements before deploying.
