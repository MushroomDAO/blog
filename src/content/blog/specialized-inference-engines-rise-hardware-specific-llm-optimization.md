---
title: "专用推理引擎崛起：六个框架深度拆解，以及普通人如何从中受益"
titleEn: "The Rise of Specialized LLM Inference Engines: Six Frameworks Analyzed, and What It Means for You"
description: "一批专为特定模型和特定硬件深度优化的 LLM 推理引擎正在快速出现：Splash（Apple M3+，比 llama.cpp 快 4.5–5.3×）、NInfer（RTX 5090 专用，17,705 tok/s prefill）、DwarfStar（Redis 作者的纯 C 单文件引擎，DeepSeek V4，Apple+NVIDIA+AMD 三平台）、Strata（消费级 PC 的 Qwen 125B MoE，RTX 5070 达 2,650 tok/s prefill）、llamAmpere（RTX 3090 专属，1.46× 加速 + 262K 上下文）、gufo（AMD Strix Halo，1,628 tok/s prefill）。它们主动放弃通用性换取极限性能，DwarfStar 明确声明大量使用 AI 辅助编码，预示着「AI 自动为你的硬件生成专用引擎」的未来正在到来。本文对六个框架逐一核实，分析趋势成立的技术依据，并给出普通开发者和最终用户的具体受益路径。"
descriptionEn: "A wave of LLM inference engines deeply optimized for specific models and specific hardware is emerging rapidly: Splash (Apple M3+, 4.5–5.3× faster than llama.cpp), NInfer (RTX 5090-specific, 17,705 tok/s prefill), DwarfStar (Redis author's single-file C engine, DeepSeek V4, Apple+NVIDIA+AMD), Strata (consumer PC Qwen 125B MoE, 2,650 tok/s prefill on RTX 5070), llamAmpere (RTX 3090-specific, 1.46× speedup + 262K context), gufo (AMD Strix Halo, 1,628 tok/s prefill). They trade generality for maximum performance; DwarfStar explicitly states heavy AI-assisted coding, foreshadowing a future where AI auto-generates specialized engines for your hardware. This piece verifies each framework, analyzes the technical basis for the trend, and maps out concrete benefit paths for developers and end users."
pubDate: 2026-10-05
heroImage: "../../assets/images/specialized-inference-engines-rise-llm-hardware-optimization-banner.jpg"
category: "Research"
tags: ["推理引擎", "LLM", "WASM", "性能优化", "Apple Silicon", "NVIDIA", "AMD", "开源工具"]
lang: "zh-CN"
wechatTitle: "专用推理引擎崛起：六个框架拆解报告"
wechatDigest: "Splash 5×快llama.cpp；NInfer 5090专用；DwarfStar Redis作者；AI自动生成硬件内核的未来"
---

有六个推理引擎正在快速出现，它们的共同特征是：只跑一种或少数几种模型，只为一种或少数几种硬件写内核。它们主动放弃通用性，换取在目标硬件上远超 llama.cpp / vLLM 的性能。

这篇文章对六个框架逐一核实数字，分析「专用引擎崛起」这个趋势是否真实成立，以及普通开发者和最终用户能从中得到什么。

---

## 六个框架逐一拆解

### 1. Splash — Apple Silicon 专用，比 llama.cpp 快 4.5–5.3×

**仓库**：incoai/splash | ⭐ 1.2K | Apache-2.0 | C++（Metal 内核）

**目标硬件**：Apple Silicon M3 及以上，macOS 26.4+，最低 36GB 统一内存

**vs llama.cpp 真实对比数字**（这是六个框架里唯一有直接对比的）：

| 模型 | Splash | llama.cpp | llama.cpp+MTP |
|------|--------|-----------|----------------|
| Qwen 27B（M5 Pro）| **74 tok/s** | 16 tok/s | 27 tok/s |
| Qwen 27B（M3 Max）| **92 tok/s** | 17 tok/s | 20 tok/s |
| Qwen 35B-A3B（M3 Max）| **209 tok/s** | 66 tok/s | — |

27B 模型提速 **4.5–5.3×**，35B MoE 提速 **2.5–3.2×**。次 token 与 llama.cpp 的一致性 97.83–99.45%（有极小数值偏差）。

**关键技术**：DFlash 2 投机解码 + 手写 Metal 内核 + 前缀缓存重用 + 自动并发批处理。内置 OpenAI/Anthropic 兼容 API，支持视觉和内嵌 PDF。

---

### 2. NInfer — RTX 5090 专用，从零写的 C++/CUDA

**仓库**：Neroued/ninfer | Apache-2.0 | C++20 + CUDA

**目标硬件**：NVIDIA RTX 5090（sm_120a）为主，社区 port 覆盖 RTX 4090/3090、AMD MI50

**性能数字**（绝对值，无与 llama.cpp 的直接对比）：

| 硬件 | 场景 | 速度 |
|------|------|------|
| RTX 5090 | Prefill（单请求） | **17,705 tok/s** |
| RTX 5090 | 并发 decode（8 请求） | 1,146.9 tok/s |
| RTX 4090（社区 port）| Decode + 投机解码 | 148.6 tok/s（81% 接受率） |
| RTX 4090 | 64K 上下文 prefill | 1,849 tok/s |
| RTX 4090 | 128K 上下文 decode | 39.6 tok/s |

**关键技术**：完全从零编写（"from scratch"，非 llama.cpp 分叉），NVFP4 量化，MTP 投机解码，多种 KV 量化格式（BF16/INT8/FP8/NVFP4/K8V4），同时兼容 OpenAI 和 Anthropic API。配套桌面 UI（Tauri 2，ninfer-studio）。

---

### 3. DwarfStar (ds4) — Redis 作者的纯 C 引擎，DeepSeek V4 专用

**仓库**：antirez/ds4 | MIT | C（单文件风格）

**作者**：antirez（Salvatore Sanfilippo，Redis 创始人）

**目标模型**：DeepSeek V4 系列（Flash、V4.1 Flash、PRO）、GLM 5.2/5.3、Qwen3.8 Flash Next

**硬件**：三平台官方支持 — Apple Silicon（96GB+）、NVIDIA CUDA（DGX Spark、Ada Lovelace 系列）、AMD ROCm（Strix Halo / Framework Desktop）

**性能数字**：8×L40S，16 并发会话，聚合生成 ~126 tok/s（注：这是服务端多用户场景，不是单请求速度）

**关键技术**：纯 C 单文件代码哲学，imatrix 量化，routed-expert 量化（针对 MoE 路由专家单独量化），多 GPU 张量并行 + 流水线并行，Directional Steering（方向性引导生成），内置 Tool Format + 编码 Agent。

**最值得注意的一点**：DwarfStar **明确声明大量使用 AI 辅助编码** —— "This software is developed with strong assistance from AI coding agents, with humans leading the ideas, testing, and debugging." 这是六个框架里唯一公开承认这一点的，antirez 的背书让这个声明很有份量。

---

### 4. Strata — 消费级 PC 跑 125B MoE

**仓库**：Niko1221/Strata | MIT | Rust

**目标**：让普通消费级 PC 也能跑 Qwen3.8-Flash-Next 125B MoE，一键安装体验

**硬件**：NVIDIA RTX 20/30/40/50 系列 + AMD RX 7000/9000 系列，最低 12GB VRAM，32GB RAM

**性能数字**：

| 硬件 | 生成速度 | Prefill 速度 |
|------|---------|------------|
| RTX 5070 | 94 tok/s | **2,650 tok/s** |
| AMD RX 9070 XT | 60 tok/s | — |
| AMD RX 7600 XT 16GB（ROCm） | 42.5 tok/s | 293 tok/s（4K prompt）|

投机解码（MTP）带来 1.6–1.8× 额外加速。

**关键技术**：动态权重分层放置（VRAM→RAM→SSD，引擎自动测算最优组合；实测「全放 GPU 反而最慢」），利用 MoE 稀疏性（24,576 个专家每次只激活约 10 个），上下文超出时 AI 摘要压缩历史对话，兼容 OpenAI API，内置 MCP 服务器接口。

---

### 5. llamAmpere — RTX 3090 专属，1.46× 加速 + 262K 上下文

**仓库**：JakeATX/llamAmpere | MIT（继承 llama.cpp）| C++/CUDA | ⭐ 142

**目标硬件**：NVIDIA Ampere RTX 3090/3090 Ti，24GB VRAM，Linux，CUDA 12.4

**vs llama.cpp 真实对比数字**：

- 标准测试：104.28 tok/s，**vs llama.cpp 1.46×**
- 100K 上下文深度：103.09 tok/s（仅 +0.3% 退化，说明长上下文几乎不影响速度）
- 262,144 token 上下文可在 23GB VRAM 内完成（理论最大 262K）

**关键技术**：MTP 投机解码（默认 4 token/step），宽度 5–8 验证内核（自定义 CUDA），TurboQuant KV 缓存压缩（turbo2~turbo6 格式），词汇表短表化（65,536 token draft 词表减少计算），自适应深度（根据接受率在 depth 3-4 间自动切换）。支持 Qwen3.8-27B、Agnes 3.0 Flash、Ternary Bonsai 2 27B 及多种量化变体。

---

### 6. gufo — AMD Strix Halo 专用，统一内存架构的最大化利用

**仓库**：gufo-org/gufo | MIT | C++20 + HIP | ⭐ 538

**目标硬件**：AMD Strix Halo（Ryzen AI MAX+ 395 + Radeon 8060S），最高 128GB 统一内存

**性能数字**（无与 llama.cpp 直接对比）：

| 模型 | Prefill | 单用户 decode | 8 用户聚合 |
|------|---------|---------------|----------|
| Qwen3.8 Flash-Next Q4_K_XL | **1,628 tok/s** | 59.41 tok/s | 157.22 tok/s |
| Qwen3.8 27B Q4_K_XL | 656 tok/s | **70.56 tok/s** | — |
| DeepSeek V4 Flash | 484 tok/s | 26.62 tok/s | — |

**关键技术**：AMD HIP 内核专门为 Strix Halo 统一内存架构优化（CPU 和 GPU 共享同一物理内存池，消除 PCIe 带宽瓶颈），三种投机解码模式（DFlash2/MTP/DSpark），多模态支持（Qwen3-ASR/TTS 语音、Qwen-Image-2.1 图像生成、MiniMax H3 文生视频），Podman 容器化部署。

---

## 横向对比

| | Splash | NInfer | DwarfStar | Strata | llamAmpere | gufo |
|---|---|---|---|---|---|---|
| Stars | 1.2K | — | — | — | 142 | 538 |
| 许可 | Apache | Apache | MIT | MIT | MIT | MIT |
| 硬件 | Apple M3+ | RTX 5090 | 三平台 | NVIDIA+AMD | RTX 3090 | AMD Strix Halo |
| vs llama.cpp | +4.5–5.3× | 无直接对比 | 无 | 无 | +1.46× | 无 |
| AI 辅助编码 | 未说明 | 未说明 | **明确承认** | 未说明 | 未说明 | 未说明 |
| 多模态 | 视觉+PDF | 文字/图/视频 | 无 | 无 | 无 | 语音/图/视频 |
| 最小硬件门槛 | 36GB RAM | 24GB VRAM | 96GB RAM（Mac）| 12GB VRAM | 24GB VRAM | 96GB RAM |

---

## 趋势分析：这个趋势真实成立吗？

**结论：成立，但要细化三个子命题。**

**命题 1：专用引擎性能确实远超通用引擎** — 部分成立

Splash 对 llama.cpp 的 4.5–5.3× 提速有直接数字支撑，llamAmpere 的 1.46× 也有。其余四个引擎目前只有各自硬件的绝对值，没有和 llama.cpp/vLLM 的直接横向对比，宣称的「远超」仍需等待独立基准测试确认。

**命题 2：它们「主动放弃通用性」** — 完全成立

这六个引擎的目标硬件范围：一个 SKU（Strix Halo）→ 一代 GPU（Ampere RTX 3090）→ 一家厂商（Apple Silicon）。不是无法做通用，而是不做，因为通用意味着牺牲能利用的硬件特性。NInfer 明确标注主要支持 RTX 5090（sm_120a），社区 port 才覆盖其他显卡。

**命题 3：AI 代码生成让「一次性专用引擎」变得极其便宜** — 有证据，尚未大规模验证

DwarfStar（antirez/ds4）是截至目前唯一公开承认大量使用 AI 辅助编码的项目，且由高信誉开发者（Redis 作者）背书。这个案例有力支持了「AI 帮助大幅降低专用引擎开发成本」的假说，但其他五个项目没有类似声明，目前还是孤证。

---

## 普通开发者如何受益

**第一步：按你的硬件选引擎，不用等待通用方案**

| 你的机器 | 推荐引擎 | 效果 |
|---------|---------|------|
| MacBook Pro M3/M4（36GB+）| Splash | Qwen 27B 跑到 74–92 tok/s，约等于 llama.cpp 的 5× |
| Mac Studio M4 Ultra（192GB）| DwarfStar（Metal） | DeepSeek V4 系列官方支持 |
| NVIDIA RTX 3090（24GB）| llamAmpere | 262K 上下文 + 1.46× 提速，不用升级硬件 |
| NVIDIA RTX 4090 / RTX 5090 | NInfer | 需编译，性能最高，适合愿意折腾的开发者 |
| AMD Ryzen AI MAX+ 395（96–128GB）| gufo | 统一内存架构专用优化，唯一为此硬件写的引擎 |
| 消费级 NVIDIA / AMD 显卡（12GB+）| Strata | 跑 Qwen 125B MoE，开箱即用 |

**第二步：用标准 API 接口，不锁定引擎**

六个引擎全部提供 OpenAI 兼容 API（`/v1/chat/completions`），部分还有 Anthropic API 兼容。这意味着你写的上层代码可以无缝切换引擎——今天用 Splash，明天换 DwarfStar，应用层不用改。

**第三步：注意「只适合少数模型」的限制**

这些引擎都只深度优化了一两个模型系列。如果你需要跑 Llama 系列，目前六个引擎都没有优化支持。通用需求仍然选 llama.cpp 或 Ollama，专用需求选对应引擎。

---

## 最终用户在不同硬件上的受益

**MacBook Pro / Mac Studio 用户（36GB+ 统一内存）**

Splash 让 Qwen 27B 从 17 tok/s 跳到 92 tok/s——这个差距是「勉强能用的阅读速度」和「流畅对话」的区别。DwarfStar 提供 DeepSeek V4 的 Apple Silicon 官方路径，加上内置编码 Agent。

**普通 PC 用户（NVIDIA 或 AMD 独显，12GB+ VRAM）**

Strata 是目前最「面向最终用户」的引擎，一键安装，能让普通 RTX 显卡跑起之前只能在服务器上跑的 125B MoE。60–94 tok/s 的生成速度，加上 MCP 接口，可以直接接 Claude Code 这类工具。

**高端 PC 用户（RTX 3090/4090/5090）**

llamAmpere 把 3090 的 24GB VRAM 推向 262K 上下文，是当前消费级里最长的上下文窗口之一。NInfer 在 4090/5090 上跑出接近数据中心规格的 prefill 速度。

**AMD Strix Halo 用户（Ryzen AI MAX+ 系列）**

gufo 目前是这个硬件上唯一专门优化过的引擎，统一内存架构让 128GB 完整可用，同时支持语音/图像/视频生成，适合构建本地多模态 AI 工作站。

---

## 这个趋势的下一步

DwarfStar 明确说明 AI 辅助了大量代码。如果这条路成立——用 AI 生成针对你的 GPU 微架构的手写内核——那「专用引擎」的门槛会继续下降。

目前的模式是：人类确定优化方向，AI 生成内核代码，人类做测试和调试。这让一两个开发者写出过去需要芯片厂商专属工程团队才能完成的优化成为可能。antirez 用 C 写 Redis 从来不是孤立现象——他证明的是「深刻理解 + 专注单一目标」可以击败大团队的通用解法。现在加上 AI 辅助，这条路径变得更宽。

---

> 以上数字均来自各项目官方仓库，性能对比应在相同硬件和测试条件下才有可比性。DwarfStar/Strata/NInfer/gufo 目前 Stars 数量较少，仍为早期项目。开源仅供学习参考。

---

<!--EN-->

## The Rise of Specialized LLM Inference Engines: Six Frameworks Analyzed

A wave of LLM inference engines optimized for specific models and specific hardware is emerging. Their shared trait: deliberately trading generality for maximum performance on a narrow target.

This analysis verifies six frameworks, examines whether the trend is real, and maps out benefit paths for developers and end users.

---

### Six Engines at a Glance

**Splash** (incoai/splash, Apache-2.0, 1.2K stars) — Apple Silicon M3+ only. The only framework in this group with a direct published comparison against llama.cpp: Qwen 27B at 74–92 tok/s vs llama.cpp's 16–17 tok/s — **4.5–5.3× faster**, with 97.83–99.45% token consistency. DFlash 2 speculative decoding + custom Metal kernels.

**NInfer** (Neroued/ninfer, Apache-2.0) — RTX 5090 primary target, community ports to 4090/3090. Written from scratch in C++20/CUDA. RTX 5090 reaches 17,705 tok/s prefill, 1,146.9 tok/s concurrent decode (8 requests). RTX 4090 community port: 148.6 tok/s with speculative decoding at 81% acceptance rate.

**DwarfStar / ds4** (antirez/ds4, MIT, C) — From Redis author Salvatore Sanfilippo (antirez). Targets DeepSeek V4 series across all three platforms (Apple Metal, NVIDIA CUDA, AMD ROCm). Pure C, single-file philosophy. Explicitly states: *"This software is developed with strong assistance from AI coding agents."* — the only framework in the group to make this public.

**Strata** (Niko1221/Strata, MIT, Rust) — Consumer PC focus: run Qwen3.8-Flash-Next 125B MoE on a standard gaming PC. RTX 5070: 94 tok/s generation, 2,650 tok/s prefill. AMD RX 9070 XT: 60 tok/s. Dynamic weight layering (VRAM→RAM→SSD), MoE sparsity exploitation. One-click install, OpenAI API + MCP server.

**llamAmpere** (JakeATX/llamAmpere, MIT, 142 stars) — RTX 3090 / 3090 Ti specific. **1.46× faster than llama.cpp** with 262,144 token context fitting in 23GB VRAM. TurboQuant KV compression, custom CUDA MTP speculative decoding, vocabulary shortlisting.

**gufo** (gufo-org/gufo, MIT, 538 stars) — AMD Strix Halo (Ryzen AI MAX+ 395) only. Exploits the unified 128GB memory architecture: no PCIe bottleneck between CPU and GPU. Qwen3.8 Flash-Next: 1,628 tok/s prefill, 59 tok/s single-user decode. Multimodal: speech, image generation, video generation.

---

### Is the Trend Real?

**Yes — with three qualifiers.**

1. Performance gains are real, but only two engines publish direct llama.cpp comparisons (Splash: 4.5–5.3×; llamAmpere: 1.46×). The others report absolute numbers on their target hardware; independent benchmarks are needed.

2. The "deliberate generality trade-off" is clearly real — engines target one hardware generation, one vendor, or one SoC SKU by design.

3. AI-assisted coding lowering the barrier: DwarfStar is the only public evidence so far (and it's strong evidence, given antirez's credibility). Whether this scales to a "golden age of one-person specialized engines" requires more data points.

---

### Benefit Map

| Hardware | Best Option | Effect |
|----------|-------------|--------|
| MacBook Pro M3/M4 (36GB+) | Splash | Qwen 27B at 74–92 tok/s vs llama.cpp's 16 tok/s |
| Mac Studio M4 Ultra (192GB) | DwarfStar | Official DeepSeek V4 on Apple Silicon |
| NVIDIA RTX 3090 (24GB) | llamAmpere | 262K context + 1.46× speedup, no hardware upgrade needed |
| NVIDIA RTX 4090 / 5090 | NInfer | Near datacenter-class prefill speed |
| AMD Ryzen AI MAX+ 395 (96–128GB) | gufo | The only engine purpose-built for this SoC |
| Consumer NVIDIA/AMD (12GB+) | Strata | Run 125B MoE out of the box |

All six expose OpenAI-compatible APIs, so application code can switch engines without changes.

---

### What's Next

If DwarfStar's AI-assisted model generalizes — use AI to generate architecture-specific CUDA/Metal/HIP kernels, humans own direction and testing — the barrier to writing a specialized engine drops further. One or two developers could produce hardware-specific optimizations that previously required dedicated chip vendor engineering teams.

The pattern antirez demonstrated with Redis ("deep understanding + single-minded focus beats large teams' general solutions") becomes more accessible when AI handles the inner loop of kernel code generation.

---

> All performance numbers are from official repositories. Cross-framework comparison requires identical hardware and test conditions. DwarfStar, Strata, and NInfer currently have few GitHub stars and remain early-stage. For technical reference only.
