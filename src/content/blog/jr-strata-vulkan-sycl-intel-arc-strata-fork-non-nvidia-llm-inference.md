---
title: "JR-Strata：把 Strata MoE 推理引擎移植到 Intel Arc 和 Vulkan 的社区分叉"
titleEn: "JR-Strata: Community Fork Porting the Strata MoE Inference Engine to Intel Arc and Vulkan"
description: "Goldlionren/JR-Strata，MIT，C++，独立实验性分叉自 Niko1221/Strata。已在 Intel Arc Pro B60（24GB VRAM，Battlemage/Xe2，OCuLink PCIe 4.0 x4）上完成验证：运行 Swift 1.5 IQ3_XXS，128K 上下文，解码约 33.5 tok/s，预填充约 311 tok/s，VRAM 专家命中率 94%，所有剩余专家驻留 pinned RAM，零 SSD 回退。包含多项工程修复：Arc B60 PCI ID 检测、SYCL ring-wait 正确性、非缓存门铃读取、分块 pinned-host 专家镜像。JR-Strata-Vulkan 是同作者正在开发的 Vulkan 后端版本，目标覆盖全部 Vulkan 兼容 GPU。"
descriptionEn: "Goldlionren/JR-Strata, MIT, C++. Independent experimental derivative of Niko1221/Strata, focused on Intel Arc GPU execution via SYCL/Level Zero. Validated on Intel Arc Pro B60 (24GB VRAM, Battlemage/Xe2, OCuLink PCIe 4.0 x4): Swift 1.5 IQ3_XXS with 128K context, ~33.5 tok/s decode, ~311 tok/s prefill, 94% VRAM expert hit rate, all remaining experts in pinned RAM with zero SSD fallback. Key engineering fixes: Arc B60 PCI ID detection, SYCL ring-wait correctness, uncached doorbell reads, chunked pinned-host expert mirror. JR-Strata-Vulkan is the companion Vulkan backend branch for broader GPU coverage."
pubDate: 2026-10-07
heroImage: "../../assets/images/jr-strata-vulkan-sycl-intel-arc-strata-fork-non-nvidia-llm-inference-banner.jpg"
category: "Tech-Experiment"
tags: ["LLM推理", "Intel GPU", "非NVIDIA", "MoE", "开源工具", "本地推理"]
lang: "zh-CN"
wechatTitle: "JR-Strata：Strata移植Intel Arc和Vulkan"
wechatDigest: "MIT；Intel Arc B60验证；解码33.5 tok/s 128K；Vulkan全GPU版开发中；Strata分叉"
---

Strata（Niko1221）是面向 125B 级 MoE 模型的本地推理引擎，设计上默认跑在 NVIDIA GPU 上。JR-Strata 是 Goldlionren 基于它做的独立分叉，目标是把这条推理路径延伸到 Intel Arc GPU（SYCL 后端）和任意 Vulkan 兼容 GPU。

GitHub（SYCL）: https://github.com/Goldlionren/JR-Strata | MIT
GitHub（Vulkan）: https://github.com/Goldlionren/JR-Strata-Vulkan | MIT
原版 Strata: https://github.com/Niko1221/Strata

---

## 已验证的 Intel Arc 路径

当前里程碑在具体硬件上跑通了整个推理链路：

| 组件 | 配置 |
|------|------|
| OS | Ubuntu 24.04 LTS |
| GPU | Intel Arc Pro B60，24 GB VRAM |
| GPU 架构 | Battlemage / Xe2 / `bmg-g21` |
| 连接方式 | PCIe 4.0 x4 via OCuLink |
| 实测 H2D 带宽 | ~6.8 GB/s |
| 系统 RAM | 64 GB |
| 编译器 / 运行时 | Intel oneAPI DPC++ 2026.1 / Level Zero |
| 后端 | SYCL |
| 模型 | Swift 1.5 / Qwen3.8-Flash-Next |
| 量化 | IQ3_XXS |
| 上下文配置 | 131,072 tokens |
| KV 缓存 | INT8 |
| 常驻 KV 窗口 | 32,768 |
| 投机解码 | MTP，`--spec 4` |

---

## 专家分层布局

128K 上下文配置下，专家在内存层级的分布：

| 层级 | 专家数量 | 内存占用 |
|------|---------|---------|
| Arc Pro B60 VRAM | 10,617 | ~17.22 GiB |
| pinned 系统 RAM | 13,959 / 13,959 | ~22.75 GiB |
| SSD 回退 | **0** | **0** |

重点在最后一行：**所有专家都在 VRAM 或 pinned RAM 里，没有触发 SSD 回退**。

这和 Strata 在 NVIDIA 上的 `VRAM → pinned RAM → SSD` 三层降级策略是同一个架构——JR-Strata 的工作是让这个分层在 Intel Arc + SYCL 栈上实际可用。

```text
Swift IQ3_XXS
      |
      +---- 热专家 → Arc B60 VRAM (~17.22 GiB)
      |
      +---- 剩余专家 → pinned RAM (~22.75 GiB)
                              |
                          PCIe 4.0 x4

PLE / n-gram 表 → NVMe
```

---

## 实测性能（开发观察，非正式 benchmark）

- 解码：约 **33.5 tok/s**
- 预填充：约 **311 tok/s**
- VRAM 专家命中率：约 **94%**
- PCIe H2D 带宽：约 **6.8 GB/s**

注：这是开发过程中的观察数据，作者明确表示尚未完成固定提示词 benchmark，不作为最终基线。正式 SYCL 性能基线计划在以下步骤完成后发布：固定提示词 `pcie_frac` sweep、CPU worker 调优、真实 120K–125K 提示词测试。

---

## 工程修复内容

JR-Strata 在上游 Strata v0.1.39 基础上做了五项主要改动：

**1. Arc B60 PCI ID 检测**
上游 Strata 未包含 Arc Pro B60 的 PCI ID（`8086:e211`）和 AOT 编译目标（`bmg-g21`），JR-Strata 补充了这个检测。

**2. SYCL API 同步**
Intel/SYCL 路径的线程亲和性处理、dense layer 加载、运行脚本参数同步做了更新，对齐上游 Strata 的接口变更。

**3. SYCL ring-wait 正确性（对应上游 PR #866）**
修复了 SYCL queue 状态被错误翻译导致的 `verify: layer N never rang` 类型失败。

**4. Arc B60 非缓存门铃读取（对应上游 PR #889）**
在 host-mirror 路径上，GPU 可能重复读到缓存过的同步值，而 CPU 已经更新了 host 侧的 doorbell。这个问题在 B60 上是重大性能杀手，JR-Strata 加入了非缓存 L1/L3 读取 hint。

**5. 分块 pinned-host 专家镜像**
原来的实现对所有 host 专家做一次大分配（类似 `sycl::malloc_host(total_bytes)`）。IQ3_XXS 的 host mirror 超过 20 GiB，Intel USM 的单次超大 host 分配经常失败——即便系统 RAM 总量够用。JR-Strata 改成多个 4GiB 块的分块策略，每个专家保留自己的 device-readable host 指针。

---

## Vulkan 路线图

JR-Strata-Vulkan 是为 Vulkan 后端单独开的仓库，目标是让同一套异构 MoE 运行时跑在所有 Vulkan 兼容 GPU 上（AMD、Intel、以及没有 CUDA 栈的其他 GPU）。

```text
model / router / MTP / KV / PLE
              |
        后端接口
         /           \
      SYCL          Vulkan
```

Vulkan 工作计划先实现：设备发现 → buffer 分配 → 异步传输 → compute dispatch → 量化 GEMV/GEMM → 专家 dispatch → PCIe host 专家执行 → 对齐 SYCL 实现做验证。

单 B60 Vulkan 后端稳定后再研究多 GPU。当前 JR-Strata-Vulkan 仓库刚建，处于非常早期阶段（0 stars，2026-10-06 创建）。

---

## 为什么值得关注

Strata 原版只在 NVIDIA GPU 上有记录，JR-Strata 做的是第一个在文档化配置下跑通 Intel Arc 的工作——有具体 PCI ID、具体内核参数、具体 benchmark 观察值，而不只是"SYCL 理论上支持"。

在算力出口管制和非 NVIDIA 推理需求持续增长的背景下，这类把头部推理引擎适配到其他 GPU 栈的社区工作是值得跟踪的信号。Vulkan 后端如果做成，意味着同一个 125B 级 MoE 引擎可以在 AMD/Intel/其他 GPU 上直接运行，不依赖 CUDA。

---

> MIT 开源。Goldlionren 独立维护，基于 Niko1221/Strata。保留原始 Strata 版权和 MIT 许可证。开源仅供学习参考。

---

<!--EN-->

## JR-Strata: Community Fork Porting the Strata MoE Inference Engine to Intel Arc and Vulkan

Strata (Niko1221) is a local inference engine designed for 125B-class MoE models, targeting NVIDIA GPUs by default. JR-Strata is Goldlionren's independent fork extending that inference path to Intel Arc GPUs (SYCL backend) and eventually any Vulkan-compatible GPU.

GitHub (SYCL): https://github.com/Goldlionren/JR-Strata | MIT
GitHub (Vulkan): https://github.com/Goldlionren/JR-Strata-Vulkan | MIT
Original Strata: https://github.com/Niko1221/Strata

---

### Validated Intel Arc Configuration

| Component | Configuration |
|-----------|---------------|
| GPU | Intel Arc Pro B60, 24 GB VRAM, Battlemage/Xe2 |
| Connection | PCIe 4.0 x4 via OCuLink |
| Measured H2D bandwidth | ~6.8 GB/s |
| System RAM | 64 GB |
| Runtime | Intel oneAPI DPC++ 2026.1 / SYCL / Level Zero |
| Model | Swift 1.5 / Qwen3.8-Flash-Next, IQ3_XXS |
| Context | 131,072 tokens configured, 32,768 resident KV window |
| Speculative decoding | MTP, `--spec 4` |

Expert placement: 10,617 experts in VRAM (~17.22 GiB), 13,959 in pinned RAM (~22.75 GiB), **zero SSD fallback**.

---

### Performance (Development Observations, Not Final Benchmark)

- Decode: ~**33.5 tok/s**
- Prefill: ~**311 tok/s**
- VRAM expert hit rate: ~**94%**

A controlled fixed-prompt benchmark, `pcie_frac` sweep, and real 120K–125K prompt test are planned before declaring an official SYCL baseline.

---

### Engineering Fixes

Five substantive changes over upstream Strata v0.1.39:

1. **Arc B60 PCI ID detection** — upstream lacked `8086:e211` and `bmg-g21` AOT target.
2. **SYCL API synchronization** — thread affinity, dense layer loading, run-script args updated to match current Strata interfaces.
3. **SYCL ring-wait correctness (PR #866)** — fixes `verify: layer N never rang` failures from incorrectly translated queue state.
4. **Uncached doorbell reads (PR #889)** — on the B60 host-mirror path, the GPU could read a cached synchronization value while the CPU had already updated the host-side doorbell; L1/L3 read hints fix this.
5. **Chunked pinned-host expert mirror** — replaces a single `sycl::malloc_host(20+ GiB)` (which fails on Intel USM even with sufficient RAM) with multiple 4 GiB blocks, each retaining its own device-readable host pointer.

---

### Vulkan Roadmap

JR-Strata-Vulkan targets a backend interface sitting alongside SYCL: same Strata-style heterogeneous MoE runtime, running on any Vulkan-compatible GPU. Early work order: device discovery → buffer allocation → async transfer → compute dispatch → quantized GEMV/GEMM → expert dispatch → PCIe host execution → validation against SYCL. The repo was created 2026-10-06 and is at a very early stage.

---

### Why It Matters

This is the first documented, configuration-specific Intel Arc Strata run — with concrete PCI IDs, kernel parameters, and benchmark observations. If the Vulkan backend matures, the same 125B MoE engine runs on AMD, Intel, and other GPUs without CUDA — relevant to anyone running inference outside NVIDIA hardware.

---

> MIT. Independently maintained by Goldlionren, based on Niko1221/Strata. Original Strata copyright and MIT license retained. For technical reference only.
