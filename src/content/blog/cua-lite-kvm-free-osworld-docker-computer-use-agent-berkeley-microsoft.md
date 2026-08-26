---
title: "CUA-Lite：UC Berkeley + Microsoft 开源计算机操控 Agent 基础设施，无需 KVM，Docker 直跑 OSWorld，4.6× 并行"
titleEn: "cua-lite-kvm-free-osworld-docker-computer-use-agent-berkeley-microsoft"
description: "CUA-Lite 是来自 UC Berkeley 和 Microsoft 的开源框架，将计算机操控 Agent（CUA）的训练和评测基础设施标准化。核心创新：用 Docker 容器替换 QEMU/KVM 虚拟机运行 OSWorld——内存从 4.1GB 降至 0.9GB，并行实例数提升 4.6 倍，冷启动从 29.9s 降至 23.8s，评测分数不变。统一 action/observation 空间覆盖桌面、浏览器、移动端；一键 Eval + SFT + RL；10+ 数据集 + 30k+ 可验证任务。"
descriptionEn: "CUA-Lite is an open framework from UC Berkeley and Microsoft that standardizes the infrastructure for training and evaluating computer-use agents (CUAs). Core innovation: replacing QEMU/KVM VMs with Docker containers for OSWorld — memory drops from 4.1GB to 0.9GB, parallelism increases 4.6×, cold-start drops from 29.9s to 23.8s, with identical benchmark scores. Unified action/observation space across desktop, browser, and mobile; one command for Eval + SFT + RL; 10+ datasets + 30k+ verifiable tasks."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Research"
tags: ["开源", "Computer-Use Agent", "OSWorld", "Docker", "强化学习", "UC Berkeley", "Microsoft", "AI Agent", "基准测试"]
heroImage: "../../assets/images/cua-lite-kvm-free-osworld-docker-computer-use-agent-berkeley-microsoft-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：cua-lite/cua-lite ⭐ 25 | Python  
主页：https://cua-lite.github.io  
HuggingFace：https://huggingface.co/cua-lite  
机构：UC Berkeley（Zhanhui Zhou）· Microsoft（Haoran Liu）  
发布：2026-08-23

---

## 问题：OSWorld 是个好基准，但装不进云端

训练或评测一个计算机操控 Agent（CUA），你需要真实的桌面环境——而且需要很多个并行跑。

**OSWorld** 提供了这样一个忠实的桌面环境：LibreOffice、Chrome、VS Code、文件系统、窗口管理器。但它是以完整虚拟机的形式交付的，跑在 QEMU/KVM 上，需要 `/dev/kvm`、嵌套虚拟化和大量内存。问题来了：

- 大多数云实例不暴露 `/dev/kvm`
- CI runner 和嵌套容器环境几乎不支持
- 每个 VM 占用 4.1 GB 内存
- 冷启动需要 29.9 秒

结果：OSWorld 在单机上很好用，但一旦想规模化并行评测或采集训练数据，它就卡住了。

---

## 核心创新：Lite.OSWorld — 同样的任务，换掉 VM

CUA-Lite 的第一个贡献是 **Lite.OSWorld**：把 QEMU/KVM 虚拟机替换成普通 Docker 容器，任务集和评测器完全不变。

| 指标 | OSWorld（原版）| Lite.OSWorld |
|------|--------------|--------------|
| 运行时 | QEMU/KVM VM | Docker 容器 |
| 宿主机要求 | /dev/kvm + 嵌套虚拟化 | 任何 Docker 主机 |
| 内存 | 4.1 GB | **0.9 GB** |
| 冷启动 | 29.9 s | **23.8 s** |
| 单机并行实例数 | baseline | **~4.6×** |
| 任务集 | OSWorld | 相同 |

**评测结果一致**：同一个模型在容器里跑同一个任务，由同一套评测器打分，分数和 VM 版本相差几个点以内。这意味着在 Lite.OSWorld 里拿到的训练信号，可以直接迁移回真实的 OSWorld 基准。

---

## 更大的野心：不只是 OSWorld

Lite.OSWorld 只是第一步。KVM-free 容器的底层是**一整套可扩展的 CUA 沙箱家族**：

| 沙箱 | 特点 |
|------|------|
| **Lite.OSWorld** | OSWorld 完整任务集，Docker 化 |
| **Lite.ScaleCUA** | 可扩展训练任务 |
| **Lite.CUAGym** | RL 训练优化环境 |
| **Lite.CUAWorld** | 40 个应用（Blender、QGIS、VSCode、GMAT 飞行仿真、PyMOL 蛋白质可视化…） |
| **Lite.Demo** | 快速入门演示环境 |

全部 30,000+ 个可验证任务，每个任务内置奖励信号，开箱即用于 RL 训练。

---

## 统一框架：任何 Agent × 任何环境

这是 CUA-Lite 最核心的设计哲学——所有组件使用同一套接口：

**统一 Action / Observation 空间**，覆盖三个平台：
- **桌面**（Desktop）：OSWorld、OSWorld-2、WindowsAgentArena、CUABench
- **浏览器**（Browser）：WebArena、VisualWebArena、WebVoyager、MiniWoB、WebGym
- **移动端**（Mobile）：AndroidWorld、AndroidLab、MobileWorld、MobileGym

**统一数据格式** `LiteSample`：一个 schema，覆盖所有 agent、所有环境、所有任务类型。每个 agent 有独立的后处理适配器，把通用数据格式转换成各自模型需要的 scaffolding。

```python
import asyncio
import lite.gym as gym
import lite.agents as agents

# 任意 env × 任意 agent，换名字即可
env = gym.make("lite.osworld@osworld_libreoffice_impress_05dd4c1d", max_steps=10)
agent = agents.make("Qwen/Qwen3-VL-8B-Instruct", env=env)
result = asyncio.run(agent.sample(env))

# result.episode_return  → 任务奖励（1.0 = 成功）
# result.steps           → 每一步的记录
# result.lite_sample     → 消息 + 元数据 + 原始图像
```

---

## 支持的 Agent

10+ 内置 Agent，覆盖主流闭源和开源模型：

**闭源 API**
- **GPT**：gpt-5.5, gpt-5.6-sol
- **Claude**：claude-opus-4-8/4-7/4-6, claude-sonnet-4-6
- **Gemini**：gemini-3.6-flash, gemini-3.5-flash, gemini-3.5-flash-lite

**开源权重**
- **Qwen3-VL**：2B/4B/8B/32B（Instruct + Thinking）
- **Qwen2.5-VL**：3B/7B
- **UI-TARS**：7B-DPO, 1.5-7B（ByteDance）
- **Fara** 7B（Microsoft）
- **EvoCUA** 8B（美团）
- **MAI-UI** 2B/8B（通义 MAI）
- **GELab** 4B（阶跃星辰）
- **OpenCUA**、**ScaleCUA**、**UI-Voyager**

---

## 三套训练管线

### Eval：一条命令评测所有基准

```bash
# 桌面 — Lite.OSWorld
uv run python scripts/rollout.py --model-id Qwen/Qwen3-VL-8B-Instruct \
  --env-id lite.osworld --splits eval --concurrency 8

# 浏览器 — WebArena
uv run python scripts/rollout.py --model-id gpt-5.5 \
  --env-id browsergym.webarena --task-id 21

# 移动端 — AndroidWorld
uv run python scripts/rollout.py --model-id gpt-5.5 \
  --env-id androidworld --task-id ContactsAddContact
```

### SFT：10+ 数据集，统一格式，即插即用

两类数据来源，都预处理成 `LiteSample` 格式：

- **语料库（Corpora）**：10+ 现有 CUA 数据集（Aguvis、CAGUI、GUI-360、GUIAct、GUIOdyssey、Multimodal-Mind2Web、OpenCUA、ScaleCUA、UI-Genie-Agent）
- **Rollout 数据**：用教师模型（如 GPT-5.5）在各环境里采集轨迹，蒸馏到学生模型。团队在持续采集并发布新数据到 HuggingFace。

### RL：GRPO + Slime，一条命令

基于 Slime 框架，在优化过的训练任务集（CUAGym、CUAWorld、WebGym、MobileGym 等）上跑 GRPO 和其他 RL 算法。每个任务内置可验证奖励——不需要单独的 reward model。

---

## 安装

```bash
# 安装所有依赖
uv sync --all-extras

# 可选：拉取 Slime 子模块（RL 训练需要）
git submodule update --init
```

---

## 为什么重要

CUA（计算机操控 Agent）是目前 AI Agent 研究里成本最高的方向之一：它需要真实的 GUI 环境、大量并行采样、可验证的任务奖励。这三个条件合在一起，让大多数研究团队的计算预算直接卡住。

**Lite.OSWorld 把 4.1GB → 0.9GB 的内存节省，直接换算成 4.6× 的并行能力**，也就是等量资源下 4.6× 的数据采集速度。对于需要大量训练数据的 RL 方法（GRPO 等），这个倍数至关重要。

更重要的是 `LiteSample` 统一格式：它解决了 CUA 研究里长期存在的碎片化问题——每个数据集格式不同、每个 agent 接口不同、每个环境的 action space 不同。CUA-Lite 用一套 schema 把这些打通，让跨基准、跨模型、跨平台的实验变成一条命令的事。

---

**相关链接**

- GitHub：https://github.com/cua-lite/cua-lite
- 主页：https://cua-lite.github.io
- Blog（KVM-free OSWorld）：https://cua-lite.github.io/blog/kvm-free-osworld
- HuggingFace：https://huggingface.co/cua-lite
- 排行榜：https://cua-lite.github.io/#benchmarks
- 联系：zhanhui@berkeley.edu（Zhanhui Zhou, UC Berkeley）

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## CUA-Lite: UC Berkeley + Microsoft Open-Source CUA Infrastructure — KVM-Free, Docker-First, 4.6× Parallelism

*by Mycelium Protocol*

---

GitHub: cua-lite/cua-lite ⭐ 25 | Python  
Homepage: https://cua-lite.github.io  
HuggingFace: https://huggingface.co/cua-lite  
Institutions: UC Berkeley (Zhanhui Zhou) · Microsoft (Haoran Liu)  
Released: 2026-08-23

---

### The Problem: OSWorld Is Great, but Won't Scale

To train or evaluate a computer-use agent (CUA), you need real desktop environments — and many of them, running in parallel.

**OSWorld** delivers exactly that: a faithful desktop with LibreOffice, Chrome, VS Code, file system, and window manager. But it ships as a full VM on QEMU/KVM, requiring `/dev/kvm`, nested virtualization, and heavy resources:

- Most cloud instances don't expose `/dev/kvm`
- CI runners and nested containers rarely support it
- Each VM uses 4.1 GB of memory
- Cold start takes 29.9 seconds

The result: OSWorld works fine on a single machine, but breaks down the moment you try to parallelize at scale — for eval runs or training data collection.

---

### The Core Innovation: Lite.OSWorld — Same Tasks, No VM

CUA-Lite's first contribution is **Lite.OSWorld**: same task suite and evaluators, running in a plain Docker container instead of a QEMU/KVM VM.

| Metric | OSWorld (original) | Lite.OSWorld |
|--------|-------------------|--------------|
| Runtime | QEMU/KVM VM | Docker container |
| Host requirement | /dev/kvm + nested virt | Any Docker host |
| Memory | 4.1 GB | **0.9 GB** |
| Cold start | 29.9 s | **23.8 s** |
| Parallelism per host | baseline | **~4.6×** |
| Task suite | OSWorld | Identical |

**Scores track within a few points.** The same model runs the same task in the container and is judged by the same evaluators — a training signal earned in the container transfers directly back to the real benchmark.

---

### Beyond OSWorld: A Family of Scalable Sandboxes

Lite.OSWorld is just the first environment in a larger KVM-free sandbox family:

| Sandbox | Notes |
|---------|-------|
| **Lite.OSWorld** | Full OSWorld task suite, containerized |
| **Lite.ScaleCUA** | Scalable training tasks |
| **Lite.CUAGym** | RL-optimized training environments |
| **Lite.CUAWorld** | 40 applications (Blender, QGIS, VSCode, GMAT spacecraft simulation, PyMOL protein visualization…) |
| **Lite.Demo** | Quick-start demo environment |

All combined: 30,000+ verifiable tasks with built-in reward signals, ready for RL training out of the box.

---

### Unified Framework: Any Agent × Any Environment

The central design principle: one interface for everything.

**Unified action / observation space** across three platforms:
- **Desktop**: OSWorld, OSWorld-2, WindowsAgentArena, CUABench
- **Browser**: WebArena, VisualWebArena, WebVoyager, MiniWoB, WebGym
- **Mobile**: AndroidWorld, AndroidLab, MobileWorld, MobileGym

**Unified data format** `LiteSample`: one schema for all agents, all environments, all task types. Per-agent adapters post-process into each model's own scaffolding.

```python
import asyncio
import lite.gym as gym
import lite.agents as agents

# Any env × any agent — swap the names
env = gym.make("lite.osworld@osworld_libreoffice_impress_05dd4c1d", max_steps=10)
agent = agents.make("Qwen/Qwen3-VL-8B-Instruct", env=env)
result = asyncio.run(agent.sample(env))

# result.episode_return  → task reward (1.0 = success)
# result.steps           → per-turn records
# result.lite_sample     → messages + metadata + raw images
```

---

### Supported Agents

10+ built-in agents across proprietary and open-weight:

**Proprietary APIs**
- **GPT**: gpt-5.5, gpt-5.6-sol
- **Claude**: claude-opus-4-8/4-7/4-6, claude-sonnet-4-6
- **Gemini**: gemini-3.6-flash, gemini-3.5-flash, gemini-3.5-flash-lite

**Open-weight**
- **Qwen3-VL**: 2B/4B/8B/32B (Instruct + Thinking)
- **Qwen2.5-VL**: 3B/7B
- **UI-TARS**: 7B-DPO, 1.5-7B (ByteDance)
- **Fara** 7B (Microsoft)
- **EvoCUA** 8B (Meituan)
- **MAI-UI** 2B/8B (Tongyi MAI)
- **GELab** 4B (StepFun)
- OpenCUA, ScaleCUA, UI-Voyager

---

### Three Training Pipelines

**Eval — one command, any benchmark:**
```bash
uv run python scripts/rollout.py --model-id Qwen/Qwen3-VL-8B-Instruct \
  --env-id lite.osworld --splits eval --concurrency 8
```

**SFT — 10+ datasets in unified format:**

Two sources, both preprocessed to `LiteSample`:
- **Corpora**: 10+ existing CUA datasets (Aguvis, CAGUI, GUI-360, GUIAct, GUIOdyssey, Multimodal-Mind2Web, OpenCUA, ScaleCUA, UI-Genie-Agent)
- **Rollouts**: trajectories from teacher models (e.g. GPT-5.5) collected and continuously published to HuggingFace for distillation into student models

**RL — GRPO + Slime:**

GRPO and other RL algorithms on optimized training environments (CUAGym, CUAWorld, WebGym, MobileGym). Every task ships a verifiable reward — no separate reward model needed.

---

### Install

```bash
uv sync --all-extras               # all dependencies
git submodule update --init        # Slime submodule (needed for RL training)
```

---

### Why It Matters

CUA research is among the most compute-expensive directions in AI agent work: it demands real GUI environments, high-throughput parallel sampling, and verifiable per-task rewards. Those three requirements together put most research teams at the edge of their compute budget.

**Lite.OSWorld's 4.1 GB → 0.9 GB memory reduction translates directly into 4.6× parallelism** — which at equal compute means 4.6× faster data collection. For RL methods like GRPO that need large amounts of on-policy rollout data, that multiplier matters a lot.

More importantly: the `LiteSample` unified format addresses a longstanding fragmentation problem in CUA research — every dataset has a different format, every agent a different interface, every environment a different action space. CUA-Lite unifies these into one schema, making cross-benchmark, cross-model, cross-platform experiments a matter of swapping a name string.

Two weeks old and 25 stars — this one is worth watching early.

---

**Links**

- GitHub: https://github.com/cua-lite/cua-lite
- Homepage: https://cua-lite.github.io
- Blog (KVM-free OSWorld): https://cua-lite.github.io/blog/kvm-free-osworld
- HuggingFace: https://huggingface.co/cua-lite
- Leaderboard: https://cua-lite.github.io/#benchmarks
- Contact: zhanhui@berkeley.edu (Zhanhui Zhou, UC Berkeley)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
