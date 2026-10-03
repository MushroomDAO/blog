---
title: "Strata：12GB 显卡跑 125B 模型，MoE 专家热缓存打破 VRAM 限制"
titleEn: "Strata: Run a 125B Model on a 12 GB GPU with MoE Expert Hot Cache"
description: "Niko1221/Strata，5500+ stars，MIT，C++。专为 Qwen3.8-Flash-Next（125B MoE）打造的本地推理引擎。12GB VRAM + 64GB RAM，自适应 MoE 专家缓存（热专家留 GPU、冷专家从内存读）+ MTP 投机解码，RTX 5070 最快 93 t/s（Q2_0）。兼容 OpenAI/Anthropic API，Web UI，一键安装。仅支持 Windows/Linux + NVIDIA 显卡。"
descriptionEn: "Niko1221/Strata, 5500+ stars, MIT, C++. A local inference engine purpose-built for Qwen3.8-Flash-Next (125B MoE). 12 GB VRAM + 64 GB RAM required. Adaptive MoE expert cache (hot experts on GPU, cold ones read from RAM) plus MTP speculative decoding. RTX 5070 gets up to 93 t/s (Q2_0 quantization). OpenAI/Anthropic-compatible API, browser UI, one-click install. Windows/Linux + NVIDIA only."
pubDate: 2026-10-03
heroImage: "../../assets/images/strata-qwen3-8-flash-next-125b-moe-12gb-gpu-inference-engine-banner.jpg"
category: "Tech-Experiment"
tags: ["本地推理", "MoE", "GPU推理", "Qwen", "开源拆解", "推理优化", "C++"]
lang: "zh-CN"
wechatTitle: "Strata：12G显卡跑125B模型，MoE专家缓存"
wechatDigest: "5.5K星MIT；12G显卡+64G内存跑125B；Q2_0最快93t/s；MoE专家热缓存+投机解码"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 核心问题

125B 参数的模型，正常来说要跑在多台 A100 或者大内存的服务器 GPU 上。Qwen3.8-Flash-Next 是 125B MoE（Mixture of Experts）架构——参数量是 125B，但每次推理实际只激活很小一部分专家网络。

Strata 针对这个特性专门做了一套推理引擎：把常用的专家缓存在 GPU 上，不常用的放在内存里按需读取。结果是——12GB 显卡 + 64GB 系统内存，能跑这个模型，最快 93 tokens/s。

仓库：github.com/Niko1221/Strata  
**Stars：5500+ | MIT | C++ | 作者：Niko Veit（Niko1221）**

---

## 工作原理

### MoE 的推理特性

MoE 模型不是每个 token 都走所有参数。Qwen3.8-Flash-Next 的名字里"Flash Next"就暗示了这一点——激活参数量远小于总参数量，每次推理只用到模型权重的一小部分。

Strata 的核心是利用这个特性做异构存储：

- **热专家留 GPU**：被频繁调用的专家（expert layer）缓存在显存里，访问延迟最低
- **冷专家从 RAM 读**：不常用的专家放在系统内存，需要时再加载
- **自适应驱逐**：Strata 用指数衰减算法动态维护缓存，使用越频繁的专家越不容易被驱逐
- **使用画像持久化**：每 10 分钟保存一次当前工作负载的专家使用分布，下次启动直接加载，跳过冷启动阶段

冷专家在 CPU 上用 AVX-512/AVX2 指令集并行计算，和 GPU 上的热专家并行进行，不是纯串行等待。

### MTP 投机解码

Strata 在此基础上加了 Multi-Token Prediction（MTP）投机解码。一个小型 draft layer 先猜接下来几个 token，主模型批量验证猜测，正确的直接接受，不对的再走正常生成流程。

效果：短对话场景下 1.6–1.8x 的额外加速，设置为 `MTP n-max 4`（最多一次猜 4 个 token）。

### 专用 CUDA 核

Strata 的 CUDA kernel 不是通用的，而是针对 Qwen3.8-Flash-Next 架构定制重写，官方 YouTube 视频标题里称"6x faster than llama.cpp"——这个数字要打折，因为 llama.cpp 本身不是为这类专家 offload 场景优化的，但定制 kernel 确实比通用方案快很多。

---

## 性能数据

作者用 RTX 5070（12GB）测的基准数字：

| 量化方案 | 短对话速度 | 128K 长上下文速度 |
|---------|-----------|----------------|
| Q2_0 | ~93 t/s | ~74 t/s |
| IQ3_S | ~53 t/s | ~46 t/s |

用户实测在 RTX 5070 + RTX 3090（24GB）上也有 75-96 t/s 的报告，接近官方数字。

模型文件：ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF，总大小约 75.8GB，全部放在系统内存和磁盘，显存只存当前活跃专家。

**需要注意的性能下降**：连续对话时，有用户报告（Issue #528）在 RTX 5090 上，持续对话会出现约 4-6x 的速度下降——这是已知问题，v0.1.36 仍在复现调查中。短对话场景不受影响。

---

## 安装与使用

一键安装脚本覆盖 Windows 和 Linux，不需要手动配置 CUDA 环境：

```bash
# Linux
curl -fsSL https://raw.githubusercontent.com/Niko1221/Strata/main/install.sh | bash

# Windows：下载 install.bat 运行
```

脚本自动下载模型（75.8GB，首次需要较长时间）、配置推理引擎、启动服务。

启动后提供：

- **浏览器 UI**：本地 Web 界面，直接聊天
- **OpenAI 兼容 API**：`http://localhost:PORT/v1/chat/completions`
- **Anthropic 兼容 API**：`http://localhost:PORT/v1/messages`
- **可选多模态输入**：支持图片（mmproj，8-12GB 卡要注意多模态投影器会多占约 907MB 显存）

---

## 硬件门槛实际在哪里

"12GB 显卡"是真的，但完整的要求是：

| 硬件 | 要求 |
|------|------|
| GPU | NVIDIA RTX 30/40/50 系，≥12GB 显存（8GB 有 fork 版本） |
| 系统内存 | **64GB RAM**（这才是真正的门槛） |
| 磁盘 | 约 80GB 空闲（模型 + 程序） |
| OS | Windows 或 Linux |
| 后端 | NVIDIA Only（无 AMD、无 Mac、无 CPU-only） |

大多数消费级主机的内存配置是 16-32GB，64GB 需要专门升级。GPU 的 12GB 反而不是最难满足的那个条件。

---

## 关键约束

**只跑 Qwen3.8-Flash-Next**。Strata 不是通用推理引擎，它的 CUDA kernel 和缓存逻辑都是为这一个模型架构定制的。如果想跑其他模型，不适用。

**NVIDIA 独占**。项目没有 AMD ROCm 或 Metal（Mac）后端。

**持续对话有已知性能问题**（Issue #528，v0.1.36 仍在调查）。短对话不受影响。

**MIT 协议**，商用无限制。

---

## 关键数字

| 指标 | 值 |
|------|----|
| Stars | 5,500+ |
| License | MIT |
| 语言 | C++ |
| 运行模型 | Qwen3.8-Flash-Next（125B MoE） |
| 最低显存 | 12GB NVIDIA |
| 最低系统内存 | 64GB RAM |
| 模型大小 | ~75.8GB |
| 最快速度（Q2_0） | ~93 t/s（短对话，RTX 5070） |
| 最快速度（IQ3_S） | ~53 t/s（短对话，RTX 5070） |
| 当前版本 | v0.1.36 |
| 平台 | Windows + Linux |

---

## 综合判断

Strata 做的事情在技术上是成立的：MoE 模型天生适合这种异构存储推理方式——每个 token 只激活一小部分专家，所以不需要把全部权重放在 GPU 上。Strata 把这个特性工程化，配合定制 CUDA kernel 和投机解码，把 125B 模型压到了消费级硬件可用的范围。

速度是真实的，96 t/s 对于一个 125B 模型来说确实很快。但"12GB 显卡"这个说法省略了"还需要 64GB 系统内存"这个同样重要的条件——这不是随便一台游戏 PC 就能满足的配置。

另外：这是一个专用引擎，只跑这一个模型。如果你主要需求就是本地跑 Qwen3.8-Flash-Next，Strata 是目前最优化的方案；如果需要灵活支持多个模型，它不是正确的工具。

5500 stars 对于一个高度专用的 C++ 推理引擎来说是很强的社区反应，说明这个需求真实存在，且当前没有更好的替代方案。

---

> 开源仅供学习，MIT 协议，商业使用无限制。

---

<!--EN-->

## Strata: Run a 125B Model on a 12 GB GPU with MoE Expert Hot Cache

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Core Insight

A 125B parameter model normally needs multiple A100s or large server-class GPUs. Qwen3.8-Flash-Next is a 125B MoE model — 125B total parameters, but each token only activates a small subset of expert layers.

Strata builds an inference engine around this property: cache frequently used experts on the GPU, read infrequently used ones from RAM on demand. Result: 12 GB VRAM + 64 GB system RAM, up to 93 tokens/second (Q2_0 quantization).

Repo: github.com/Niko1221/Strata  
**5500+ stars | MIT | C++ | Author: Niko Veit (Niko1221)**

---

### How It Works

**MoE inference property**: MoE models don't use all parameters for each token. Strata exploits this with heterogeneous storage:

- **Hot experts on GPU**: Frequently called expert layers stay in VRAM for lowest latency
- **Cold experts in RAM**: Infrequently used experts live in system memory, loaded on demand
- **Adaptive eviction**: Exponential decay algorithm maintains the cache — hotter experts are harder to evict
- **Expert profile persistence**: Expert usage distribution saved every 10 minutes and on exit; next startup loads the profile to skip cold-start

Cold experts are computed on CPU using AVX-512/AVX2 in parallel with GPU computation on hot experts — not a pure serial wait.

**MTP speculative decoding**: A small draft layer guesses the next several tokens; the main model verifies in batch. Correct guesses are accepted immediately; wrong ones fall back to normal generation. Delivers 1.6–1.8x additional speedup for short conversations (setting: `MTP n-max 4`).

**Custom CUDA kernels**: Rewritten specifically for Qwen3.8-Flash-Next's architecture. Official YouTube titles claim "6x faster than llama.cpp" — take this with a grain of salt, as llama.cpp isn't optimized for this style of expert offloading. But custom kernels do meaningfully outperform generic implementations.

---

### Performance Numbers

Benchmarks from the author on RTX 5070 (12GB):

| Quantization | Short context | 128K long context |
|-------------|--------------|------------------|
| Q2_0 | ~93 t/s | ~74 t/s |
| IQ3_S | ~53 t/s | ~46 t/s |

User-reported 75-96 t/s on RTX 5070 and RTX 3090 (24GB), consistent with official numbers.

Model file: ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF, ~75.8 GB total, stored in system memory and on disk — VRAM only holds the currently active expert cache.

**Known performance regression**: Issue #528 (v0.1.36, still under investigation) reports a 4-6x speed drop on continued conversations on RTX 5090. Short conversations are unaffected.

---

### Installation

One-click install handles CUDA setup automatically:

```bash
# Linux
curl -fsSL https://raw.githubusercontent.com/Niko1221/Strata/main/install.sh | bash
# Windows: download and run install.bat
```

After startup:
- **Browser UI**: Local chat interface
- **OpenAI-compatible API**: `http://localhost:PORT/v1/chat/completions`
- **Anthropic-compatible API**: `http://localhost:PORT/v1/messages`
- **Optional image input**: Multimodal (note: mmproj adds ~907 MB VRAM overhead, reduces expert cache slots by 300-600 on 8-12 GB cards)

---

### Where the Hardware Bar Actually Is

"12 GB GPU" is accurate, but the full requirements are:

| Hardware | Requirement |
|----------|-------------|
| GPU | NVIDIA RTX 30/40/50 series, ≥12 GB VRAM (8 GB fork exists) |
| System RAM | **64 GB** — this is the harder bar to clear |
| Storage | ~80 GB free (model + engine) |
| OS | Windows or Linux |
| Backend | NVIDIA only (no AMD, no Mac, no CPU-only) |

Most consumer gaming PCs ship with 16-32 GB RAM. 64 GB requires a deliberate upgrade. The GPU's 12 GB VRAM is actually the easier constraint to satisfy.

---

### Hard Constraints

**Only runs Qwen3.8-Flash-Next.** Strata's CUDA kernels and caching logic are purpose-built for this one model architecture. Not a general-purpose inference engine.

**NVIDIA-only.** No AMD ROCm, no Apple Metal, no CPU-only mode.

**Continued-conversation performance regression known** (Issue #528, v0.1.36 under investigation). Short conversations unaffected.

**MIT license** — commercial use unrestricted.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 5,500+ |
| License | MIT |
| Language | C++ |
| Target model | Qwen3.8-Flash-Next (125B MoE) |
| Min VRAM | 12 GB NVIDIA |
| Min system RAM | 64 GB |
| Model size | ~75.8 GB |
| Peak speed (Q2_0) | ~93 t/s (short ctx, RTX 5070) |
| Current version | v0.1.36 |
| Platforms | Windows + Linux |

---

### Verdict

What Strata is doing is technically sound: MoE models are naturally suited to heterogeneous storage inference — each token activates only a fraction of experts, so you don't need all weights on GPU. Strata engineers this into practice with custom CUDA kernels and speculative decoding, pushing a 125B model into consumer hardware territory.

The speed claims are real. 93 t/s for a 125B model is genuinely fast. But "12 GB GPU" omits an equally important condition: "plus 64 GB system RAM." That's not a standard gaming PC configuration — it's a deliberate hardware investment.

Additional context: this is a single-model specialized engine. If your primary need is local Qwen3.8-Flash-Next inference, Strata is currently the most optimized option. If you need flexible multi-model support, this isn't the right tool.

5,500+ stars for a highly specialized C++ inference engine is strong community signal: the demand is real, and there's currently no better alternative for this specific use case.

---

> Open source for learning only. MIT license — commercial use unrestricted.
