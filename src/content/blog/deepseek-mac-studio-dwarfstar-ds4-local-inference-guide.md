---
title: "DwarfStar：Mac Studio 跑 DeepSeek V4 Flash/PRO，从安装到 SSD 流式推理"
titleEn: "DwarfStar (ds4): Run DeepSeek V4 Flash/PRO Locally on Mac Studio — Install, SSD Streaming, Distributed Inference"
description: "antirez 用纯 C 写了一个专为 Apple Silicon 优化的 DeepSeek V4 本地推理引擎 DwarfStar（ds4）。本文详解硬件选型、模型下载、SSD 流式推理、KV cache 磁盘化和双机 Thunderbolt 分布式推理，帮你把这头大模型跑在自己的机器上。"
descriptionEn: "antirez built DwarfStar (ds4), a pure-C local inference engine for DeepSeek V4 Flash/PRO, optimized for Apple Silicon Metal, CUDA, and ROCm. This guide covers hardware selection, model download, SSD streaming, on-disk KV cache, and dual-machine Thunderbolt distributed inference."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Tech-Experiment"
tags: ["DeepSeek", "本地推理", "Mac Studio", "DwarfStar", "Metal", "SSD流式", "开源"]
heroImage: "../../assets/images/deepseek-mac-studio-dwarfstar-ds4-local-inference-guide-banner.jpg"
---

> **GitHub**: [antirez/ds4](https://github.com/antirez/ds4) · **17,561 Stars** · **C** · Metal / CUDA / ROCm

---

## 这是什么

Redis 的作者 antirez 写了一个叫 **DwarfStar**（二进制名 `ds4`）的本地推理引擎，专门用来在 Mac、DGX Spark 和 AMD Strix Halo 上跑 DeepSeek V4 Flash 和 PRO。

关键点直接说：这不是 llama.cpp 的封装。整个项目用**纯 C** 写成，不依赖 llama.cpp 库（尽管致谢了它，借用了部分量化格式）。它只认 antirez 团队发布的特定 GGUF 文件，不是通用 GGUF loader——这个取舍是有意为之的，换来的是针对 MoE（Mixture of Experts）架构的深度优化。

---

## 硬件要求：按 RAM 选模型

DeepSeek V4 Flash 是 MoE 模型，总参数量很大，但激活参数少。量化后的 RAM 占用差异显著，antirez 按内存档位提供了四条下载路径：

| 内存 | 推荐模型 | 下载命令 |
|---|---|---|
| 96 GB / 128 GB | q2-imatrix（入门） | `./download_model.sh q2-imatrix` |
| 96 GB / 128 GB | q2-q4-imatrix（进阶） | `./download_model.sh q2-q4-imatrix` |
| ≥ 256 GB | q4-imatrix | `./download_model.sh q4-imatrix` |
| 512 GB（Mac Studio Ultra） | PRO q2-imatrix | `./download_model.sh pro-q2-imatrix` |

MacBook Pro M3/M5 Max 128GB 跑 q2 没问题。Mac Studio M3 Ultra 512GB 才能完整跑 PRO。如果内存不够，还有 SSD Streaming 这条路——后面详说。

---

## 编译与基础使用

```bash
git clone https://github.com/antirez/ds4
cd ds4
make          # macOS 自动用 Metal backend

# 下载模型（按你的内存选）
./download_model.sh q2-imatrix
```

最基本的用法：

```bash
# 单次问答
./ds4 -p "Explain Redis streams in one paragraph."

# 进入交互式对话模式
./ds4
```

交互模式里有几个常用命令：`/think`（开启思考模式）、`/nothink`（直接回答）、`/ctx N`（设上下文长度）、`/read FILE`（读文件进上下文）。

起 HTTP 服务（兼容 OpenAI / Anthropic API）：

```bash
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192
```

这个 `--kv-disk-dir` 参数值得单独讲。

---

## SSD 流式推理：把"能不能跑"变成"速度快不快"

DeepSeek V4 Flash 是 MoE 模型，每次推理只激活少量专家网络（Expert），但所有专家的权重都得加载进 RAM。对于内存不足的机器，这原本是硬截止：装不下，直接跑不了。

DwarfStar 的 **SSD Streaming** 模式打破了这个硬截止：把路由专家的权重放在磁盘上，推理时按需从 SSD 加载激活的那部分。结果是把"能不能跑"从二元判断变成了一条**速度谱**——内存越大，从磁盘加载的频率越低，速度越快；内存小的机器也能跑，只是慢一些。

```bash
# 基础 SSD Streaming（自动计算缓存预算）
./ds4 -m ./ds4flash.gguf --ssd-streaming

# 手动指定专家权重缓存大小（减少重复 IO）
./ds4 -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB
```

自动模式取 Metal 推荐工作集的 80%，减去非路由权重，剩余作为专家缓存。Mac Studio 内置 SSD 读取速度约 5–7 GB/s，专家缓存命中率高时实际体验比想象中流畅。

**64GB MacBook 的 SSD 流式方案**：

```bash
./download_model.sh q2-imatrix
./ds4 -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB --ctx 32768 --nothink
```

---

## KV Cache 磁盘化：长上下文变成"磁盘公民"

KV Cache 是 Transformer 推理的中间状态，上下文越长，它占的 RAM 越多。`--kv-disk-dir` 参数把 KV cache 直接写到磁盘，相当于把这个"临时大户"从 RAM 驱逐到 SSD。

```bash
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192
```

上面这条命令起了一个 10 万 token 上下文的服务器，KV cache 最多占 8GB SSD 空间。对话状态持久化到磁盘，**重启服务器后 KV cache 依然可以恢复**——它真的变成了一个"磁盘公民"。

---

## 双机分布式推理：Thunderbolt 跑 PRO Q4

两台机器各装半套模型，用 Thunderbolt 5 直连做分布式推理：

```bash
# 机器 A（协调者），管理 0-30 层
./ds4 -m gguf/DeepSeek-V4-Pro-Q4K-Layers00-30.gguf \
  --role coordinator --layers 0:30 --listen 169.254.43.68 1234

# 机器 B（工作节点），管理 31 层到输出
./ds4 -m gguf/DeepSeek-V4-Pro-Q4K-Layers-31-output.gguf \
  --role worker --layers 31:output --coordinator 169.254.43.68 1234
```

Thunderbolt 5 直连实测 Prefill 加速：

| Prompt 长度 | 单机 | 双机 | 加速 |
|---|---|---|---|
| 9,421 tokens | 421.70 t/s | 582.22 t/s | **1.38x** |
| 28,684 tokens | 405.30 t/s | 674.16 t/s | **1.66x** |
| 63,819 tokens | 353.62 t/s | 654.79 t/s | **1.85x** |

注意：**Generation 是自回归的，分布式反而变慢**（每个 token 都要跨机通信）。分布式的价值是：跑放不进单台机器的大模型 + 加速长 prompt 的 Prefill 阶段。

---

## 真实性能基准

| 机器 | 量化 | Prefill（短） | Prefill（11K tokens） | Generation |
|---|---|---|---|---|
| MacBook Pro M3 Max, 128GB | q2 | 58.52 t/s | 250.11 t/s | 26.68 t/s |
| MacBook Pro M5 Max, 128GB | q2 | 87.25 t/s | 463.44 t/s | 34.27 t/s |
| Mac Studio M3 Ultra, 512GB | q2 | 84.43 t/s | 468.03 t/s | 36.86 t/s |
| Mac Studio M3 Ultra, 512GB | q4 | 78.95 t/s | 448.82 t/s | 35.50 t/s |

Mac Studio M3 Ultra 512GB 跑 q4，Prefill 长上下文可达 449 t/s，Generation 稳定 35 t/s，日常使用完全够用。

---

## 和 llama.cpp 的关系

DwarfStar 是站在 llama.cpp 肩膀上的独立实现，不是 fork：
- **借用了**：GGUF 量化布局和表、CPU 量化/点积逻辑、部分 Metal kernel
- **独立实现了**：针对 DeepSeek MoE 的整个推理图、KV cache 管理、SSD Streaming、分布式通信
- **注明了**：llama.cpp 的 copyright 保留在 LICENSE 文件里

README 明确说了：代码**强借助 GPT 5.5 开发**，人类主导思路、测试和调试。如果你不接受 AI 辅助写的代码，项目本身就告知了这一点，自行判断。

---

## 适合谁

- 有 128GB+ 内存的 MacBook Pro（M3/M4/M5 Max）→ q2 Flash，直接可用
- 有 Mac Studio Ultra 512GB → PRO q2，顶配本地体验
- 有两台高内存 Mac → 分布式跑 PRO Q4
- 64GB 机器 → SSD Streaming 可以试，速度取决于 SSD 热度

---

> **GitHub**: [antirez/ds4](https://github.com/antirez/ds4) · **Stars**: 17,561 · **License**: MIT (with GGML copyright)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: DwarfStar (ds4) is a pure-C local inference engine for DeepSeek V4 Flash and PRO, built by Redis creator antirez. It targets Apple Silicon (Metal), NVIDIA CUDA, and AMD ROCm — not a llama.cpp wrapper. Three standout features: SSD Streaming (run models larger than your RAM by streaming MoE expert weights from disk), on-disk KV cache (100K+ token contexts without running out of RAM, persisted across server restarts), and Thunderbolt distributed inference (two Macs share a PRO Q4 split, 1.38×–1.85× prefill speedup). 17,561 stars.

---

## Hardware Selection

- **96–128 GB** → `q2-imatrix` or `q2-q4-imatrix` (DeepSeek V4 Flash)
- **≥ 256 GB** → `q4-imatrix`
- **512 GB** (Mac Studio M3/M4 Ultra) → `pro-q2-imatrix`

```bash
git clone https://github.com/antirez/ds4 && cd ds4 && make
./download_model.sh q2-imatrix   # adjust to your RAM tier
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192
```

## SSD Streaming

When RAM is insufficient to hold all expert weights, DwarfStar streams them from SSD on demand. Turns the hard memory cutoff into a speed spectrum.

```bash
./ds4 -m ./ds4flash.gguf --ssd-streaming
./ds4 -m ./ds4flash.gguf --ssd-streaming --ssd-streaming-cache-experts 32GB
```

## On-Disk KV Cache

`--kv-disk-dir` moves the KV cache to disk, making 100K+ token contexts practical without running out of RAM. Persists across server restarts.

## Distributed Inference

Two Macs via Thunderbolt 5 split a PRO Q4 model. Prefill speedup: 1.38×–1.85× depending on prompt length. Generation is slower (autoregressive, one cross-machine hop per token). Best for fitting models that don't fit one machine + accelerating long prefills.

## Benchmarks

Mac Studio M3 Ultra 512 GB, q4: **449 t/s prefill** (11K tokens), **35.5 t/s generation**. M5 Max 128 GB, q2: **463 t/s prefill**, **34.3 t/s generation**.

**Links**: [GitHub](https://github.com/antirez/ds4)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
