---
title: "从零搭建 vLLM：系统工程师的 LLM 推理课"
titleEn: "Build a vLLM from Scratch: An LLM Inference Course for Systems Engineers"
description: "skyzh（Alex Chi Z，Databricks）开源了 tiny-llm：一门面向系统工程师的 LLM 推理实战课，4 周从零搭建 mini-vLLM + Qwen3-4B，只跑 Apple Silicon。Week 1：Transformer 核心组件（RoPE/GQA/RMSNorm）；Week 2：KV 缓存、4-bit 量化内核、SIMD 预填充；Week 3：连续批处理、分块预填充、Paged KV Cache、Paged FlashAttention；Week 4：完整编码 Agent 循环。Apache-2.0，4.8K stars，附在线教材和参考实现。"
descriptionEn: "skyzh (Alex Chi Z, Databricks) open-sourced tiny-llm: a hands-on LLM inference course for systems engineers. Build a mini-vLLM + Qwen3-4B from scratch in 4 weeks — Apple Silicon only. Week 1: Transformer components (RoPE/GQA/RMSNorm); Week 2: KV cache, 4-bit quantized kernels, SIMD prefill; Week 3: continuous batching, chunked prefill, paged KV cache, paged FlashAttention; Week 4: full coding agent loop. Apache-2.0, 4.8K stars, with online textbook and reference solution."
pubDate: 2026-10-09
heroImage: "../../assets/images/tiny-llm-skyzh-build-vllm-from-scratch-apple-silicon-qwen-banner.jpg"
category: "Tech-Experiment"
tags: ["LLM", "推理引擎", "Apple Silicon", "开源课程", "系统工程"]
lang: "zh-CN"
wechatTitle: "从零搭建vLLM：系统工程师的推理课"
wechatDigest: "Apache-2.0；KV缓存+连续批处理+编码Agent；Apple Silicon独占；Qwen3-4B"
---

同一个作者写了 mini-lsm（从零搭存储引擎），现在出了 tiny-llm：从零搭 LLM 推理引擎，4 周课程，目标是让系统工程师真正懂 vLLM 在做什么。

作者是 Alex Chi Z（skyzh），Databricks 工程师，CMU 数据库组出身。tiny-llm 是 mini-lsm 思路在 LLM 推理方向的延伸：不调高层 API，手写每一层。

Apache-2.0，4.8K stars。GitHub: https://github.com/skyzh/tiny-llm

---

## 四周课表

### Week 1 — Transformer 核心组件

从最基础的部件开始：注意力机制、RoPE 位置编码、Grouped-Query Attention（GQA）、RMSNorm、MLP，然后接上模型加载、解码、采样。

这一周的目标是：不借助 HuggingFace Transformers，把一个可以跑的 Qwen3-4B 推理路径搭起来。

### Week 2 — 优化内核

在基础路径跑通之后，开始做性能相关的部分：

- **KV Cache**：把历史 token 的 Key/Value 缓存起来，不重复计算
- **4-bit 量化矩阵向量积**：权重量化到 4-bit，矩阵向量乘法用量化内核跑
- **SIMD 矩阵预填充**：prefill 阶段用向量指令加速
- **融合算子**：RMSNorm、RoPE、SwiGLU 合并成单个内核，减少内存 round-trip
- **分块预填充注意力（Tiled Prefill Attention）**

### Week 3 — 服务基础设施（tiny vLLM）

这是课程的核心：把单次推理变成可以同时处理多个请求的服务：

- **连续批处理（Continuous Batching）**：不等批次填满就开始处理，来一个发一个
- **分块预填充（Chunked Prefill）**：长 prompt 拆成块，和 decode 步骤交错执行
- **Paged KV Cache**：KV Cache 不再预分配固定内存，而是按需分页，解决碎片问题
- **Direct Paged Attention + Paged FlashAttention**：在 Paged KV Cache 上直接做注意力计算

可选扩展：MoE（混合专家）、投机解码。

### Week 4 — 编码 Agent

课程最后一周从推理系统转到 Agent 系统：实现一个完整的编码 Agent 循环，包括：工作区检查、受批准的文件编辑、经验证的命令执行、效果回执（effect receipt）、断点续跑（checkpoint/resume）、上下文压缩、方向修正、结果评估、分叉与选择（fork-and-select）、有界工具结果。

这部分在 LLM 推理课程里比较少见——大多数推理课在服务层就结束了，tiny-llm 把 Agent 执行层也包了进来。

---

## 定位：面向系统工程师，不是 ML 研究者

这门课的目标受众不是想调参的 ML 工程师，而是关注**内存带宽、内核占用率、KV Cache 增长、请求调度**的系统工程师。

作者的背景也是数据库/存储系统（CMU-DB、TiKV、RisingLight），课程设计逻辑更接近"构建系统"而不是"训练模型"。

---

## 平台限制

**只支持 Apple Silicon Mac**——这不是技术限制不足，而是刻意选择。

Apple Silicon 的统一内存架构（CPU 和 GPU 共享同一块内存）在教学上有优势：不需要处理 CPU↔GPU 数据搬运，可以专注于推理逻辑本身。MLX 作为实现 oracle 和性能基线，learners 通过和 MLX 输出对比来验证自己的实现。

模型固定为 **Qwen3-4B**，选择理由：GQA、QK normalization、BF16 激活、4-bit 权重——刚好能覆盖课程涉及的所有技术点。

---

## 使用方式

```bash
# 要求 Python 3.10–3.12，Apple Silicon Mac
pdm install -v
pdm run check-installation
pdm run test-refsol -- -- -k week_1   # 运行 Week 1 参考实现测试
```

主要依赖：`mlx ≥0.32`、`mlx-lm ≥0.31.3`、`torch ≥2.6`、`torchtune`、`torchao`、`numpy ≥2.2`、`nanobind`。

仓库结构：
- `tiny_llm/`：学习者的实现空间（写你的代码）
- `tiny_llm_ref/`：参考答案（测试和 benchmark 用）

---

## 和 vLLM 本身的关系

tiny-llm 不是 vLLM 的学习路径，而是**vLLM 的教学重现**。它把 vLLM 中最关键的几个设计（Paged KV Cache、Continuous Batching、Chunked Prefill）从生产代码里抽出来，在一个可以一步步构建的教学框架里重新实现，帮助工程师真正理解"这些优化在做什么"——而不只是会调 API。

---

## 一句话说清楚

tiny-llm 是面向系统工程师的 LLM 推理实战课：4 周手写 Transformer 组件、KV Cache 内核、连续批处理服务层、编码 Agent 循环。只跑 Apple Silicon，用 Qwen3-4B，Apache-2.0。

---

> Apache-2.0。skyzh (Alex Chi Z)，Databricks/CMU-DB，4.8K stars，2025-04-19 创建。开源仅供学习参考。

---

<!--EN-->

## Build a vLLM from Scratch: An LLM Inference Course for Systems Engineers

The same author who wrote mini-lsm (build a storage engine from scratch) is back with tiny-llm: build an LLM inference engine from scratch. Four weeks, Apple Silicon only.

Author: Alex Chi Z (skyzh), engineer at Databricks, formerly at CMU Database Group. tiny-llm applies the mini-lsm philosophy to LLM inference — no high-level API shortcuts, write every layer yourself.

Apache-2.0, 4.8K stars. GitHub: https://github.com/skyzh/tiny-llm

---

### 4-Week Curriculum

**Week 1 — Core transformer components**

Attention, RoPE positional encoding, Grouped-Query Attention (GQA), RMSNorm, MLP, model loading, decoding, sampling. Goal: run Qwen3-4B inference without calling HuggingFace Transformers.

**Week 2 — Optimization kernels**

- KV cache: cache past Key/Value tensors, avoid re-computation
- 4-bit quantized matrix-vector products
- SIMD matrix prefill
- Fused RMSNorm/RoPE/SwiGLU kernels (reducing memory round-trips)
- Tiled prefill attention

**Week 3 — Serving infrastructure (the tiny vLLM)**

- Continuous batching: process requests as they arrive instead of waiting for a full batch
- Chunked prefill: split long prompts into chunks, interleaved with decode steps
- Paged KV cache: on-demand paging instead of fixed pre-allocation — eliminates fragmentation
- Direct paged attention + paged FlashAttention

Optional extensions: MoE, speculative decoding.

**Week 4 — Coding agent**

Full coding agent loop: workspace inspection, approved edits, validated commands, effect receipts, checkpoint/resume, context compaction, steering, outcome evaluation, fork-and-select, bounded tool-result evidence.

---

### Why Systems Engineers, Not ML Researchers

The course is explicitly framed around **memory bandwidth, kernel occupancy, KV cache growth, and request scheduling** — the same concerns you'd have building a database or storage system. Alex Chi Z's background (CMU-DB, TiKV, RisingLight) shows in the curriculum design.

---

### Apple Silicon Only

Not a limitation — a deliberate choice. Unified memory means no CPU↔GPU data movement to handle, letting learners focus on inference logic. MLX serves as both the correctness oracle and the performance baseline.

Model: Qwen3-4B — chosen for GQA, QK normalization, BF16 activations, and 4-bit weights that cover every technique in the course.

---

### Setup

```bash
# Python 3.10–3.12, Apple Silicon Mac required
pdm install -v
pdm run check-installation
pdm run test-refsol -- -- -k week_1
```

Key deps: `mlx ≥0.32`, `mlx-lm ≥0.31.3`, `torch ≥2.6`, `torchtune`, `torchao`, `nanobind`.

Repo structure:
- `tiny_llm/`: your implementation (exercises go here)
- `tiny_llm_ref/`: reference solution (used by tests)

---

### TL;DR

tiny-llm is a hands-on LLM inference course for systems engineers: 4 weeks building transformer components, KV cache kernels, a continuous-batching serving layer, and a coding agent loop — from scratch, Apple Silicon only, Qwen3-4B, Apache-2.0.

---

> Apache-2.0. skyzh (Alex Chi Z), Databricks/CMU-DB, 4.8K stars, created 2025-04-19. For reference only.
