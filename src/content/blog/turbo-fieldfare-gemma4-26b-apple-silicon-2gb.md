---
title: "TurboFieldfare：在8GB MacBook上跑Gemma4 26B大模型，只用2GB内存"
titleEn: "turbo-fieldfare-gemma4-26b-apple-silicon-2gb"
description: "一个开源 Swift + Metal 运行时，让 Gemma 4 26B-A4B 在任意 M 系列 Mac 上运行，包括 8GB 版本。核心思路：只把 1.35GB 共有权重驻留内存，从 SSD 流式读取每个 token 所需的 8 个专家——12GB 的专家文件按需拉取，实际内存占用 ~2GB。"
descriptionEn: "An open-source Swift + Metal runtime that runs Gemma 4 26B-A4B on any Apple Silicon Mac, including 8 GB models. Core idea: keep only the 1.35 GB common weights resident, stream the 8 experts needed per token from SSD — all 12 GB of routed experts on demand, ~2 GB footprint in practice."
pubDate: "2026-07-30"
updatedDate: "2026-07-30"
category: "Tech-News"
tags: ["on-device AI", "Apple Silicon", "Gemma", "Swift", "Metal", "LLM推理", "本地模型", "Mycelium"]
heroImage: "../../assets/images/turbo-fieldfare-gemma4-26b-apple-silicon-2gb-banner.jpg"
---

*by Mycelium Protocol*

---

一台 8GB 内存的 M2 MacBook Air，跑一个 26 亿参数的大模型，内存占用 2GB，速度 5-6 token/秒。

这不是量化到模型失去意义的那种"压缩"，是 Gemma 4 26B-A4B 的原始指令调优权重，原封不动的 4-bit 值。

**TurboFieldfare**（[drumih/turbo-fieldfare](https://github.com/drumih/turbo-fieldfare)）是一个纯 Swift + Metal 实现的推理运行时，专门为这一件事而生：让 26B MoE 模型在你现在用的 Mac 上跑起来。

---

## 为什么 26B 能装进 2GB

Gemma 4 26B-A4B 是 Mixture-of-Experts 架构。虽然有 260 亿总参数，但每个 token 只激活其中约 38.8 亿——通过一个路由器从 30 个 Transformer 层里各选 8 个专家。

这给了 TurboFieldfare 一个关键机会：**用内存放需要的，用 SSD 放不需要的**。

具体分法：

**常驻内存（~1.35GB 文件映射）：**
- 共享注意力权重（embedding/头部、attention projections、共享专家、norms）
- FP16 KV Cache（4K 上下文约 305MiB）
- 可复用 scratch 缓冲区（约 16MB）

**留在 SSD 的（12.01GB，约 30 个 layer 文件，每层 128 个专家）：**
- 每层的 128 个路由专家 blob

每次生成一个 token，路由器选出 8 个专家，CPU 用这 8 个 ID 对照 16-slot LFU 缓存（每层），命中直接复用，未命中则用有界并行 `pread` 从 SSD 拉取对应的 3.3MB blob 进 Metal-visible 缓冲区。

Metal 在等 SSD 读取的同时跑共享专家分支，等到路由专家 blob 就位，两路合并。

```
每个 token 的执行流：
router → 选 8 专家 → LFU 命中 / pread 未命中 → Metal attention + 共享专家 → 合并输出
```

预填充（prefill）分成最多 128 token 的 chunk，同一个拉取的专家 blob 可以服务整个 chunk 里的多行——减少 I/O 次数。

---

## 实测数据

| 机器 | decode 速度 | 内存占用 |
|------|------------|---------|
| 8GB M2 MacBook Air | 5.1–6.3 tok/s | ~1.9–2.1 GB |
| 24GB M5 Pro | 31–35 tok/s | ~2.1 GB |

同台 M5 Pro 上，MLX（mlx-lm）跑同一个 checkpoint 可以达到 76–82 tok/s，但需要 8.3–9.8 GB RSS + 14.7–15.3 GB GPU 分配——这根本跑不进 8GB 机器。

TurboFieldfare 换来的是：**8GB 机器能用，M5 Pro 也能用，内存用量几乎不变**。

单个 decode step 的时间分解（M2，短提示）：

| 工作项 | ms/token |
|-------|---------|
| 专家读取（pread） | 83.1 |
| 命令缓冲区流水线等待 | 55.6 |
| 输出头 | 14.2 |
| 其他 | 9.9 |

SSD 读取占了大头，这也说明 M5 Pro 显著更快的原因：存储带宽大幅提升。

---

## 安装和使用

要求：macOS 26 + Metal 4 + Swift 6.2 + Xcode 26，arm64 only。

```bash
git clone https://github.com/drumih/turbo-fieldfare.git
cd turbo-fieldfare
swift build -c release
.build/release/TurboFieldfareMac
```

首次启动选 **Download**，运行时会用有界 range 请求从 Hugging Face 流式下载并直接重新打包进 `.gturbo` 格式，约 15GB 传输，不需要预先下载完整 checkpoint。安装完成后 `.gturbo` 目录约 14.3GB，通过 manifest + SHA-256 校验完整性。

**也提供本地 OpenAI 兼容服务端**，监听 `http://127.0.0.1:8080/v1`，支持 Chat Completions、streaming、function tools，可以直接对接本地 IDE 或脚本：

```bash
.build/release/TurboFieldfareServer --model scratch/gemma4.gturbo
```

CLI 模式支持指令对话（`--messages-file`）和原始补全（`--prompt`），也支持通过 `--auto-seeds N` 生成多个变体。

---

## 技术细节：模型文件布局

安装目录 `.gturbo` 的结构：

```
gemma4.gturbo/
  manifest.json          # 完整性校验锚点
  model_weights.bin      # 共有权重，1.35GB，只读文件映射
  tokenizer/             # Gemma tokenizer
  packed_experts/
    layout.json
    layer_00.bin … layer_29.bin   # 每层 128 个专家 blob，共 12.01 GB
```

每个 `layer_XX.bin` 里的专家是页对齐的定长 blob，Metal 内核直接 bind 子区域缓冲区，不需要逐专家新建 buffer。

KV Cache 布局也是 Gemma 4 特有的：25 个滑动窗口层（1,024 token 有界环形缓冲区，1,152 行容量留 chunk 写入余量）+ 5 个全注意力层（线性追加，保留完整 context）。

---

## 与其他方案的区别

**不是 MLX 包装**：TurboFieldfare 是 model-specific 实现，所有 Metal kernel 和专家流式机制都针对 Gemma 4 26B-A4B 的 MoE 结构手工打磨，不追求通用性。

**不是 llama.cpp 移植**：没有 GGUF，没有 CPU 计算，纯 Metal。

**不是端侧蒸馏小模型**：原始 4-bit instruction checkpoint，原封不动。

代价是：只跑这一个模型，只在 macOS 26+ 运行，不支持视觉、音频，不支持 Intel Mac。

---

## 一个关于 103 次实验的记录

项目附带 [OPTIMIZATION_JOURNEY.md](https://github.com/drumih/turbo-fieldfare/blob/main/docs/OPTIMIZATION_JOURNEY.md)，记录了 103 次带测量的实验结果，包括有效的、无效的、和最终被还原的。

这种工程诚实在开源项目里不常见——知道"我们试过什么、为什么没用"往往比看到最终方案更有价值。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。一个持续追踪 AI 工具、系统和底层演化的内容节点。

---

<!--EN-->

## TurboFieldfare: Gemma 4 26B on an 8 GB MacBook, in ~2 GB of RAM

*by Mycelium Protocol*

An 8 GB M2 MacBook Air. A 26-billion-parameter model. 2 GB memory footprint. 5–6 tokens per second.

This isn't "quantized to the point of meaninglessness" compression. It's the original Gemma 4 26B-A4B instruction-tuned weights — packed 4-bit values, unchanged.

**TurboFieldfare** ([drumih/turbo-fieldfare](https://github.com/drumih/turbo-fieldfare)) is a pure Swift + Metal inference runtime built for exactly one purpose: running this MoE model on the Mac you already own.

### Why 26B Fits in 2 GB

Gemma 4 26B-A4B is a Mixture-of-Experts architecture. Despite 26 billion total parameters, each token activates only ~3.88 billion of them — the router selects 8 experts per token from 128, across 30 transformer layers.

This creates the key opportunity: **keep what's needed in RAM, leave the rest on SSD**.

**Resident in memory (~1.35 GB file mapping)**:
- Common attention weights (embedding/head, attention projections, shared experts, norms)
- FP16 KV cache for a 4K context (~305 MiB)
- Reusable scratch buffers (~16 MB)

**Staying on SSD (12.01 GB across 30 per-layer files)**:
- All 128 routed expert blobs per layer

For each token, the router picks 8 experts. The CPU checks a 16-slot LFU cache per layer: hits reuse existing Metal buffers; misses launch bounded parallel `pread` calls to fetch the ~3.3 MB blobs into Metal-visible memory. Metal runs the shared-expert branch while those reads complete, then merges both outputs.

Prefill processes up to 128-token chunks so a single fetched expert blob can serve the whole chunk — reducing SSD I/O.

### Benchmarks

| Hardware | Decode rate | Memory footprint |
|----------|------------|-----------------|
| 8 GB M2 MacBook Air | 5.1–6.3 tok/s | ~1.9–2.1 GB |
| 24 GB M5 Pro | 31–35 tok/s | ~2.1 GB |

The same M5 Pro running MLX (mlx-lm) against the same checkpoint reaches 76–82 tok/s — but needs 8.3–9.8 GB RSS plus 14.7–15.3 GB GPU allocation. That path doesn't run on 8 GB machines at all.

TurboFieldfare's trade is this: **works on 8 GB, works on M5 Pro, nearly identical memory footprint either way**. SSD reads dominate decode time on the M2 (~83 ms/token out of ~163 ms total). M5 Pro's faster storage is why it's 6× faster.

### Getting Started

Requirements: macOS 26, Metal 4, Swift 6.2, Xcode 26. arm64 only.

```bash
git clone https://github.com/drumih/turbo-fieldfare.git
cd turbo-fieldfare
swift build -c release
.build/release/TurboFieldfareMac
```

On first launch, choose **Download**. The repacker fetches only the needed byte ranges from the pinned Hugging Face revision via bounded range requests and repacks them directly into `.gturbo` format — no full checkpoint staged to disk. The completed install is ~14.3 GB, verified against `manifest.json` and per-file SHA-256.

A local OpenAI-compatible server is also available at `http://127.0.0.1:8080/v1`, supporting Chat Completions, streaming, and function tools:

```bash
.build/release/TurboFieldfareServer --model scratch/gemma4.gturbo
```

### What This Is (and Isn't)

This is **not** an MLX wrapper, not a llama.cpp port, not a distilled small model. TurboFieldfare is a model-specific implementation: every Metal kernel and expert-streaming mechanism is engineered specifically for Gemma 4 26B-A4B's MoE structure. That specificity is the source of the efficiency.

The cost: it runs this one model, on macOS 26+ only, text-only, arm64-only.

The project also ships [OPTIMIZATION_JOURNEY.md](https://github.com/drumih/turbo-fieldfare/blob/main/docs/OPTIMIZATION_JOURNEY.md) — 103 measured experiments, including what didn't work and what was later reversed. In open-source ML engineering, that kind of documented failure record is rare and worth reading.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
