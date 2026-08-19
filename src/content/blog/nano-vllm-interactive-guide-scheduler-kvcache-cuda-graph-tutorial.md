---
title: "从零读懂 nano-vLLM：13 章源码教程 + 13 个浏览器实验，拆解推理引擎核心机制"
titleEn: "nano-vllm-interactive-guide-scheduler-kvcache-cuda-graph-tutorial"
description: "nano-vllm-interactive-guide 是一个面向开发者的交互式源码学习项目，基于 GeeeekExplorer/nano-vllm（约 1200 行 Python）。13 章中文教程 + 13 个纯 HTML 浏览器实验 + 每章课后习题，从一次 generate() 调用出发，逐步拆解 Scheduler、PagedAttention 分页 KV Cache、Prefix Cache、Prefill/Decode 分离、FlashAttention、Tensor Parallel 和 CUDA Graph。无需 GPU 即可在浏览器体验核心机制。"
descriptionEn: "nano-vllm-interactive-guide is an interactive source-code learning project based on GeeeekExplorer/nano-vllm (~1200 lines Python). 13 Chinese tutorial chapters + 13 pure HTML browser experiments + per-chapter exercises. Starting from a single generate() call, it progressively dissects Scheduler, PagedAttention paged KV Cache, Prefix Cache, Prefill/Decode separation, FlashAttention, Tensor Parallel, and CUDA Graph. No GPU required for browser experiments."
pubDate: "2026-08-18"
updatedDate: "2026-08-18"
category: "Tech-News"
tags: ["LLM推理", "vLLM", "PagedAttention", "KV缓存", "CUDA", "开源教程", "推理引擎"]
heroImage: "../../assets/images/nano-vllm-interactive-guide-scheduler-kvcache-cuda-graph-tutorial-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：lora-sys/nano-vllm-interactive-guide  
在线教程：lora-sys.github.io/nano-vllm-interactive-guide  
上游项目：GeeeekExplorer/nano-vllm  
许可证：MIT

---

vLLM 是目前最广泛使用的 LLM 推理框架之一，但它的生产级代码库有几十万行，对初学者来说几乎不可入门。nano-vLLM 是它的教学级复现版本，用约 **1200 行 Python** 保留了核心推理引擎的所有关键机制。

问题是：即使 1200 行，如果没有合适的导引，你还是会在 `scheduler.py` 和 `block_manager.py` 里迷失——缺少三个关键心智模型：**请求如何流动、KV Cache 为什么要分页、Prefill 与 Decode 为什么要分开优化**。

nano-vllm-interactive-guide 就是为解决这三个问题而做的。

---

## 一、项目结构：三条并行的学习轨

教程设计了三条可以独立或交织推进的学习路径：

**概念轨**：先理解「为什么」——调度器为什么要连续批处理、KV Cache 为什么要分页、Prefill 和 Decode 为什么分离——不要求一开始就懂 CUDA。

**源码轨**：每章定位到 nano-vLLM 中的具体源文件和函数，建立「机制 → 代码 → 文件」的完整对应。

**运行轨**：在真实 CUDA 环境里跑起来、修改参数、观察行为差异——从「看懂」走到「能改」。

---

## 二、13 章教程大纲

### 第一部分：建立全局认识

**第 00 章：学习路线与运行环境**  
三条学习轨的结构介绍，本地和云端运行环境配置。

**第 01 章：从 Prompt 到第一个 Token**  
追踪一次完整的 `generate()` 调用。核心：`generate()` → `step()` → 五阶段执行流程。这是理解后续所有章节的基础——你需要知道「一次推理」在系统里流经哪些组件。

**第 02 章：读懂整体架构**  
7 大模块数据流全景图。建立「鸟瞰视角」后再深入各模块会事半功倍。

**第 03 章：Sequence 状态机**  
每个推理请求在系统里以 `Sequence` 对象存在，历经 WAITING → RUNNING → FINISHED 的生命周期。理解状态机是理解调度器的前提。

### 第二部分：调度与内存

**第 04 章：Scheduler 与连续批处理**  
静态批处理（Static Batching）的问题：长短不齐的请求被迫等待最长的那个结束。连续批处理（Continuous Batching）的方案：每个 step 都可以插入新请求、移除已完成的请求，最大化 GPU 利用率。

**第 05 章：分页 KV Cache（PagedAttention）**  
KV Cache 内存碎片问题的根因：传统实现为每个请求预分配连续内存，利用率极低（有论文测算约 20-40%）。PagedAttention 的方案：把 KV Cache 切成固定大小的「Block」，按需分配，像操作系统的虚拟内存一样管理。这是 vLLM 最核心的创新之一。

**第 06 章：Prefix Cache**  
当多个请求共享相同前缀（系统提示词 system prompt、few-shot 示例）时，可以共享 KV Cache Block，避免重复计算。章节详解前缀命中率的提升策略和缓存失效边界。

**第 07 章：Prefill 与 Decode 分离**  
Prefill（处理输入 tokens，全部并行）和 Decode（逐 token 生成，自回归）的计算特征完全不同。分离执行可以分别优化，特别是在长上下文场景里影响显著。

### 第三部分：GPU 执行与扩展

**第 08 章：Attention 与缓存写入**  
FlashAttention 融合内核如何减少 HBM 读写次数、KV Cache 如何在 Attention 计算时被读写。这里终于要进入 CUDA 层面的讨论。

**第 09 章：Sampling 采样**  
四种主要采样策略：Greedy（贪心）、Temperature（温度采样）、Top-K、Top-P（核采样）。教程把采样概率的分布变化做成了可交互的可视化——你可以直接拖动参数看概率分布如何变化。

**第 10 章：Tensor Parallel（张量并行）**  
多 GPU 并行的基础方案：把权重矩阵按列或行切分到多张 GPU，每张卡独立计算后通过 All-Reduce 汇聚结果。章节讲解矩阵切分策略和通信开销。

**第 11 章：CUDA Graph**  
每次调用 CUDA Kernel 都有 CPU 端的启动开销。CUDA Graph 的方案：提前「录制」一组 Kernel 调用的计算图，之后只需一次 Launch 触发整图执行，消除重复的 CPU→GPU 调度开销。Decode 阶段 batch size 固定，特别适合 CUDA Graph 优化。

**第 12 章：综合项目与 Benchmark**  
把前 11 章的知识整合到一个可验证的推理引擎改造项目里，并与原始实现做性能对比。

---

## 三、13 个浏览器互动实验

这是整个项目最有特色的部分：**无需 GPU，直接在浏览器里操作核心机制**。

每个实验对应一章内容，用纯 HTML/JavaScript 模拟真实机制的行为：

- **调度队列实验**：可视化请求的入队、调度、批处理过程，拖放请求观察连续批处理的效果
- **KV Block 分配实验**：模拟 PagedAttention 的块分配和回收，直观看到内存碎片减少的效果
- **前缀命中实验**：输入不同的前缀，看哪些 Block 可以被命中复用
- **采样概率实验**：实时调整 Temperature / Top-K / Top-P，观察 token 概率分布的变化
- **矩阵切分实验**：可视化 Tensor Parallel 的切分方式和 All-Reduce 通信
- **CUDA Graph 实验**：对比有无 CUDA Graph 时的 Kernel 启动序列

这些实验让你在理解机制之前就能有「操作感」——而不是先看代码再去猜它在干什么。

---

## 四、项目定位和边界

**这个教程解决什么**：帮助开发者建立三个关键心智模型（请求流动 / KV Cache 分页 / Prefill-Decode 分离），然后顺利读懂 nano-vLLM 的 ~1200 行源码。

**这个教程不解决什么**：这不是 GeeeekExplorer/nano-vllm 的官方文档；上游项目持续迭代，教程以社区学习为主，请以源码主分支为最终依据。也不覆盖生产级 vLLM 的所有功能（量化、AWQ/GPTQ 支持、多模态等）。

**适合谁**：
- 想理解 LLM 推理引擎内部机制的工程师
- 已经能用 vLLM 但不知道它「为什么快」的开发者
- 希望从源码层面学习 PagedAttention 的研究者
- 想从「调用 API」进阶到「理解推理栈」的 AI 应用开发者

---

## 五、本地运行

```bash
git clone https://github.com/lora-sys/nano-vllm-interactive-guide.git
cd nano-vllm-interactive-guide
npm install
npm run docs:dev  # 本地开发，VitePress 热更新
```

如需真实运行（CUDA 环境）：

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install git+https://github.com/GeeeekExplorer/nano-vllm.git
hf download Qwen/Qwen3-0.6B --local-dir ~/huggingface/Qwen3-0.6B
python examples/check_runtime.py
```

---

LLM 推理引擎的内部机制，一直是「知道怎么用但不知道为什么」的黑盒地带。nano-vllm-interactive-guide 是目前我见过的针对这个领域做得最完整的社区学习项目之一——浏览器实验 + 源码对照 + 习题的三层结构，比单纯的代码注释解析更容易入门。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## nano-vLLM Interactive Guide: 13 Chapters + 13 Browser Experiments Dissecting the Inference Engine

*by Mycelium Protocol*

---

GitHub: lora-sys/nano-vllm-interactive-guide  
Live tutorial: lora-sys.github.io/nano-vllm-interactive-guide  
Upstream: GeeeekExplorer/nano-vllm  
License: MIT

---

vLLM is the most widely used LLM inference framework, but its production codebase spans hundreds of thousands of lines — nearly impenetrable for newcomers. nano-vLLM is its teaching-grade reimplementation, preserving every key inference mechanism in about **1,200 lines of Python**.

Even 1,200 lines can lose you without the right mental models: **how requests flow, why KV Cache needs paging, why Prefill and Decode are optimized separately**. nano-vllm-interactive-guide is built to give you exactly those three models.

---

### Three Learning Tracks

**Concept track**: understand the "why" before code. Why continuous batching? Why paged KV Cache? Why separate Prefill and Decode? No CUDA required at the start.

**Source track**: every chapter anchors to specific source files and functions in nano-vLLM. Complete mapping from mechanism → code → file.

**Runtime track**: run it, modify parameters, observe behavior. Move from "understand" to "can change."

---

### Chapter Map

**Part 1: Global Understanding**
- Ch 00: Learning path and environment
- Ch 01: Prompt → first token — the complete `generate()` → `step()` → 5-stage pipeline
- Ch 02: Full architecture — 7-module data flow overview
- Ch 03: Sequence state machine — WAITING / RUNNING / FINISHED lifecycle

**Part 2: Scheduling and Memory**
- Ch 04: Scheduler and continuous batching — why static batching wastes GPU time; how continuous batching inserts/removes requests every step
- Ch 05: Paged KV Cache (PagedAttention) — root cause of memory fragmentation; fixed-size Block allocation as virtual memory for KV Cache
- Ch 06: Prefix Cache — sharing KV Cache Blocks across requests with the same system prompt or few-shot prefix; hit rate optimization and invalidation boundaries
- Ch 07: Prefill/Decode separation — the two phases have fundamentally different compute profiles; separating them enables independent optimization

**Part 3: GPU Execution and Scale**
- Ch 08: Attention and cache writes — FlashAttention fused kernel reducing HBM bandwidth; KV Cache read/write during Attention
- Ch 09: Sampling — Greedy / Temperature / Top-K / Top-P with interactive probability distribution visualization
- Ch 10: Tensor Parallel — column/row matrix sharding across GPUs, All-Reduce communication
- Ch 11: CUDA Graph — capturing Kernel launch sequences to eliminate repeated CPU→GPU scheduling overhead; why Decode is the best fit
- Ch 12: Capstone — verifiable inference engine modification with benchmark comparison

---

### 13 Browser Experiments (No GPU)

The standout feature: pure HTML/JavaScript simulations of core mechanisms, runnable in any browser:

- **Scheduler queue**: visualize request enqueuing, continuous batching — drag requests to see the scheduler's decisions
- **KV Block allocation**: simulate PagedAttention's block assignment and reclaim; watch fragmentation decrease
- **Prefix hit**: enter different prefixes and see which Blocks get cache hits
- **Sampling probability**: drag Temperature / Top-K / Top-P sliders and watch the token distribution change in real time
- **Tensor Parallel**: visualize matrix sharding and All-Reduce communication patterns
- **CUDA Graph**: compare Kernel launch sequences with and without Graph capture

These experiments give you operational intuition before you read the code — you know what you're looking for.

---

### Who This Is For

- Engineers who want to understand LLM inference internals
- Developers who use vLLM but don't know why it's fast
- Researchers learning PagedAttention from source
- AI application developers moving from "call the API" to "understand the inference stack"

Not the official nano-vLLM documentation. Not a replacement for production vLLM (quantization, multimodal, etc.). The upstream project evolves — treat the source branch as ground truth.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
