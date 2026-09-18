---
title: "KTransformers v0.7.1：用 CPU+GPU 异构执行微调 Qwen VLM 和 Kimi 这类超大 MoE"
titleEn: "KTransformers v0.7.1: CPU+GPU Heterogeneous Fine-Tuning for Qwen VLM and Kimi Ultra-Large MoE"
description: "kvcache-ai/ktransformers v0.7.1（Apache-2.0，19.5K stars）新增两项微调能力：Qwen3-VL-30B 图文 BF16 LoRA（覆盖视觉/语言/路由专家），以及 Kimi K2.5/K2.6 RAWINT4 原权重 LoRA（不需要先反量化成 BF16）。异构执行：CPU 承载路由专家权重，GPU 跑注意力和共享专家，通过 LLaMA-Factory 统一训练接口。"
descriptionEn: "kvcache-ai/ktransformers v0.7.1 (Apache-2.0, 19.5K stars) adds two fine-tuning capabilities: Qwen3-VL-30B BF16 image-text LoRA (covering vision/language/routed-expert modules) and Kimi K2.5/K2.6 RAWINT4 native LoRA (no BF16 dequantization required). Heterogeneous execution: CPU handles routed expert residency, GPU runs attention and shared experts, unified via LLaMA-Factory."
pubDate: "2026-09-18"
updatedDate: "2026-09-18"
category: "Tech-Experiment"
tags: ["fine-tuning", "MoE", "LoRA", "KTransformers", "Qwen-VLM", "Kimi", "heterogeneous-computing", "LLaMA-Factory"]
heroImage: "../../assets/images/ktransformers-v071-moe-lora-finetune-qwen-vlm-kimi-rawint4-banner.jpg"
---

> 📌 GitHub：https://github.com/kvcache-ai/ktransformers
> Stars：19,522 | License：Apache-2.0 | 语言：Python
> v0.7.1 发布日期：2026-09-15

---

超大 MoE 模型（Qwen3-VL-30B、Kimi K2.5、DeepSeek-V3）的微调一直有两个现实门槛：

1. **权重太大**：30B-A3B 意味着 30B 总参数、每次推理激活 3B，存下来就要几十 GB
2. **格式不兼容**：量化后的模型（INT4、FP8）要微调通常需要先反量化成 BF16，反而放大了内存需求

KTransformers v0.7.1 针对这两个问题，分别给了两套方案。

---

## KTransformers 是什么

kvcache-ai/ktransformers 是一个针对**异构 LLM 推理和微调**的 Python 框架，核心思路是：

- **CPU 承载路由专家（Routed Expert）**：大 MoE 模型的专家层参数量大，但每次只激活少数专家，把专家权重放在 CPU 主存（RAM）里，按需计算
- **GPU 跑注意力和共享专家**：注意力层和共享专家计算密集，留给 GPU
- **CPU-GPU 联合执行**：通过精细的调度减少数据搬运开销

这和传统"全塞 VRAM"的做法相比，允许用大内存 CPU + 少量 GPU 来跑和微调本来进不了 GPU 的模型。

v0.7.0 引入了 DeepSeek 系列的 FP8 LoRA 和全量微调，v0.7.1 在这个基础上加了两项：

---

## 新增能力一：Qwen VLM 多模态 MoE LoRA

### 支持模型

| 模型 | 模板名 |
|------|------|
| Qwen3-VL-30B-A3B-Instruct | qwen3_vl |
| Qwen3.5-35B-A3B | qwen3_5 |

### 覆盖范围

这次的 LoRA 不只是语言层，而是**覆盖视觉塔、语言模型和路由专家模块**——也就是说，你可以用行业图像数据同时调整视觉理解和语言生成。

LoRA 作用范围有三种选择：
- **只调文字**：冻结视觉塔和投影层，只更新语言模型
- **只调视觉**：冻结语言模型和投影层，只更新视觉塔
- **图文联调**：冻结投影层，同时更新视觉和语言部分

注意：`lora_target: all` 会自动排除 multimodal projector，要调投影层需要显式指定 target。

### 安装

```bash
# 1. 创建专用环境（Python 3.11，torch 版本锁定）
conda create -n kt-vlm-lora python=3.11
conda activate kt-vlm-lora

# 2. 安装 PyTorch（锁 2.9.1，KT SFT 依赖此版本）
pip install torch==2.9.1 torchvision==0.24.1 torchaudio==2.9.1

# 3. 安装 LLaMA-Factory
git clone https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/ktransformers.txt

# 4. KTransformers 从源码安装（含子模块）
git clone --recursive https://github.com/kvcache-ai/ktransformers.git
cd ktransformers
pip install -e .
```

还需要 KT 定制版的配套包：
```bash
pip install transformers-kt==5.6.0.post2
pip install accelerate-kt==1.14.0.post2
```

### 训练配置

```yaml
# qwen3vlmoe_lora_sft_kt.yaml（关键字段）
finetuning_type: lora
lora_rank: 8
lora_alpha: 16
lora_target: all
use_kt: true
kt_backend: auto

# 图像约束
image_max_pixels: 262144
video_max_pixels: 16384
```

`use_kt: true` 是启用 KTransformers 异构执行的开关，`kt_backend: auto` 会自动探测硬件配置。

### 启动训练

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 accelerate launch \
  --config_file examples/ktransformers/accelerate/fsdp2_kt_bf16.yaml \
  src/train.py \
  examples/ktransformers/train_lora/qwen3vlmoe_lora_sft_kt.yaml
```

`num_processes` 在 accelerate 配置里要和 `CUDA_VISIBLE_DEVICES` 的 GPU 数量对齐。

### 输出文件

KT 在正常 PEFT 适配器文件旁边还会额外保存 `fused_expert_lora.safetensors`，恢复训练时两个文件都需要。

### 验证结果（一步损失）

| 模型 | Loss | Gradient Norm | 单步时间 |
|------|------|---------------|---------|
| Qwen3-VL-30B | 13.6875 | 7.493 | 9.42s |
| Qwen3.5-35B | 1.6299 | 0.6675 | 14.10s |

官方说明：这是功能性冒烟测试，不是收敛性能基准。

---

## 新增能力二：Kimi K2.5 / K2.6 RAWINT4 LoRA

### 什么是 RAWINT4 LoRA

标准量化模型做 LoRA 的流程是：
```
INT4 权重 → 反量化 → BF16 → LoRA 梯度计算 → INT4 权重
```
这个过程有个问题：反量化会让内存临时膨胀，BF16 的专家权重比 INT4 大很多，抵消了量化节省的空间。

RAWINT4 LoRA 的做法是：**直接在原始打包的 INT4 专家权重上做 LoRA，不做 BF16 展开**。这样：
- 训练期间内存占用和推理一致，不会出现"训练比推理需要更多显存"的情况
- 省去了权重格式转换步骤

这对 Kimi K2.5（月之暗面）这类本身用 INT4 格式分发的大 MoE 特别有意义——用户拿到的就是 INT4 权重，不需要额外转换就能做 LoRA。

### 参考文档

详细步骤见官方指南：https://github.com/kvcache-ai/ktransformers/blob/main/.github/release/examples/kimi-k25/README.md

---

## 硬件要求

**官方验证配置**：
- Intel Xeon Platinum 8488C + 2 TiB RAM + 8x RTX 4090（48 GB 各）

**这不是最低配置**，而是验证配置。实际最低需求取决于模型：

| 资源 | 说明 |
|------|------|
| NVIDIA GPU + CUDA | 必需，GPU 跑注意力和共享专家 |
| 大内存 CPU | 越大越好，路由专家权重住在 RAM 里 |
| AVX-512 或 AMX CPU | 推荐，加速专家层计算 |
| Python 3.11 + CUDA 13.0 | 版本锁定依赖 |
| Linux | 目前 SFT 组件只支持 Linux |

v0.7.0 针对 DeepSeek-V3.1 的数据：FP8 LoRA 把主机内存需求从约 1.4 TB 降到约 800 GB。对于 Qwen3-VL-30B 这个量级，理论上内存需求低很多，2-4 张 RTX 4090 + 大容量内存 CPU 应该可行（官方未给出具体最低值）。

---

## 实际使用建议

**什么场景值得用**：
- 有行业私有图文数据需要适配 Qwen3-VL-30B（医疗影像、工业质检、文档理解）
- 已经有 Kimi K2.5/K2.6 INT4 权重，要做领域垂直化而不想重新量化
- GPU 预算有限但 CPU 内存充足（企业服务器往往 RAM 很大）

**注意事项**：
- torch==2.9.1 版本锁定不可忽略，用错版本会有不兼容问题
- `fused_expert_lora.safetensors` 是 KT 特有输出，恢复检查点必须同时保留
- RAWINT4 LoRA 文档目前只覆盖 Kimi K2.5/K2.6，其他 INT4 模型需要等后续支持
- LLaMA-Factory 的版本选择需要看 KTransformers 文档里的指定 rev，不是任意版本都行

---

## 与 v0.7.0 的关系

v0.7.0（2026 年 8 月发布）带来了 DeepSeek 系列的 FP8/BF16/INT8 原生 LoRA 和全量微调，以及 KTransformers × LLaMA-Factory 整合的完整 Cookbook。v0.7.1 在这个基础上往多模态方向（Qwen VLM）和量化感知微调方向（RAWINT4）各扩展了一步。

这两个版本合在一起，基本上覆盖了目前主流超大 MoE 的微调需求：DeepSeek / Kimi / Qwen 系列，BF16 / FP8 / RAWINT4 三种权重格式，文本 / 图文两种模态。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/kvcache-ai/ktransformers
> Stars: 19,522 | License: Apache-2.0 | Language: Python
> v0.7.1 Released: 2026-09-15

---

Ultra-large MoE fine-tuning has always had two practical barriers:

1. **Sheer weight size**: 30B-A3B means 30B total parameters with 3B activated per forward pass — even storing them takes tens of GB
2. **Format incompatibility**: Quantized models (INT4, FP8) typically require dequantization to BF16 before LoRA, which actually inflates memory requirements

KTransformers v0.7.1 addresses both problems with two separate solutions.

---

## What Is KTransformers

kvcache-ai/ktransformers is a Python framework for **heterogeneous LLM inference and fine-tuning**, built around one core idea:

- **CPU hosts Routed Expert weights**: Large MoE models have massive expert parameter counts, but only activate a few experts per forward pass — keep expert weights in CPU host memory (RAM) and compute on demand
- **GPU runs Attention and Shared Experts**: Compute-intensive layers stay on GPU
- **CPU-GPU joint execution**: Carefully scheduled to minimize data movement overhead

This approach lets you run and fine-tune models that would normally never fit in VRAM, using large-memory CPUs alongside modest GPU configurations.

v0.7.0 introduced FP8 LoRA and full fine-tuning for DeepSeek series. v0.7.1 adds two more capabilities:

---

## New Capability 1: Qwen VLM Multimodal MoE LoRA

### Supported Models

| Model | Template |
|-------|---------|
| Qwen3-VL-30B-A3B-Instruct | qwen3_vl |
| Qwen3.5-35B-A3B | qwen3_5 |

### Coverage

This LoRA goes beyond just the language layers — it **covers the vision tower, language model, and routed expert modules**. This means industry image datasets can update both visual understanding and language generation simultaneously.

Three LoRA scope options:
- **Text only**: freeze vision tower and projector, update language model
- **Vision only**: freeze language model and projector, update vision tower
- **Combined**: freeze only projector, update both vision and language

Note: `lora_target: all` automatically excludes the multimodal projector; projector training requires explicit target specification.

### Installation

```bash
# 1. Create dedicated environment (Python 3.11, torch version locked)
conda create -n kt-vlm-lora python=3.11
conda activate kt-vlm-lora

# 2. Install PyTorch (pin to 2.9.1 — KT SFT requires this version)
pip install torch==2.9.1 torchvision==0.24.1 torchaudio==2.9.1

# 3. Install LLaMA-Factory
git clone https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/ktransformers.txt

# 4. KTransformers from source (include submodules)
git clone --recursive https://github.com/kvcache-ai/ktransformers.git
cd ktransformers
pip install -e .
```

KT-specific companion packages:
```bash
pip install transformers-kt==5.6.0.post2
pip install accelerate-kt==1.14.0.post2
```

### Training Configuration

```yaml
# qwen3vlmoe_lora_sft_kt.yaml (key fields)
finetuning_type: lora
lora_rank: 8
lora_alpha: 16
lora_target: all
use_kt: true
kt_backend: auto

# Image constraints
image_max_pixels: 262144
video_max_pixels: 16384
```

`use_kt: true` enables KTransformers heterogeneous execution. `kt_backend: auto` detects hardware configuration automatically.

### Launch Training

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 accelerate launch \
  --config_file examples/ktransformers/accelerate/fsdp2_kt_bf16.yaml \
  src/train.py \
  examples/ktransformers/train_lora/qwen3vlmoe_lora_sft_kt.yaml
```

`num_processes` in the accelerate config must match the number of GPUs in `CUDA_VISIBLE_DEVICES`.

### Output Files

KT saves `fused_expert_lora.safetensors` alongside standard PEFT adapter files. Both are required for checkpoint resumption.

### Validation Results (Single-Step Loss)

| Model | Loss | Gradient Norm | Step Time |
|-------|------|---------------|-----------|
| Qwen3-VL-30B | 13.6875 | 7.493 | 9.42s |
| Qwen3.5-35B | 1.6299 | 0.6675 | 14.10s |

Official note: these are functional smoke test results, not convergence benchmarks.

---

## New Capability 2: Kimi K2.5 / K2.6 RAWINT4 LoRA

### What Is RAWINT4 LoRA

Standard quantized model LoRA flow:
```
INT4 weights → dequantize → BF16 → LoRA gradient computation → INT4 weights
```

The problem: dequantization causes temporary memory bloat. BF16 expert weights are much larger than INT4, canceling out the savings from quantization.

RAWINT4 LoRA: **apply LoRA directly to the original packed INT4 expert weights, no BF16 expansion**. Benefits:
- Training memory footprint matches inference — no "training needs more VRAM than inference" problem
- Eliminates weight format conversion overhead

This is especially valuable for Kimi K2.5 (Moonshot AI), which is distributed in INT4 format — users can apply LoRA without any additional conversion step.

### Reference Documentation

Detailed steps: https://github.com/kvcache-ai/ktransformers/blob/main/.github/release/examples/kimi-k25/README.md

---

## Hardware Requirements

**Official validated configuration**:
- Intel Xeon Platinum 8488C + 2 TiB RAM + 8x RTX 4090

**This is the test configuration, not the minimum requirement.** Actual minimums depend on model size:

| Resource | Notes |
|----------|-------|
| NVIDIA GPU + CUDA | Required — GPU runs attention and shared experts |
| Large-memory CPU | More is better — routed expert weights live in RAM |
| AVX-512 or AMX CPU | Recommended for expert layer acceleration |
| Python 3.11 + CUDA 13.0 | Version-locked dependencies |
| Linux | SFT components currently Linux-only |

v0.7.0 data point for DeepSeek-V3.1: FP8 LoRA reduced host memory demand from ~1.4 TB to ~800 GB. For Qwen3-VL-30B scale, memory requirements are substantially lower — 2-4 RTX 4090s plus large-capacity CPU RAM should be feasible (official minimums not yet published).

---

## Practical Usage Guidance

**When it's worth using**:
- Industry image-text data to adapt Qwen3-VL-30B (medical imaging, industrial inspection, document understanding)
- Existing Kimi K2.5/K2.6 INT4 weights that need domain specialization without requantization
- GPU budget limited but CPU memory abundant (enterprise servers often have large RAM)

**Caveats**:
- torch==2.9.1 version lock is strict — mismatched versions cause compatibility failures
- `fused_expert_lora.safetensors` is KT-specific output; checkpoint recovery requires keeping this file alongside standard PEFT files
- RAWINT4 LoRA docs currently cover only Kimi K2.5/K2.6; other INT4 models require future support
- LLaMA-Factory version selection must follow the specific revision in KTransformers docs — not just any version

---

## Context: v0.7.0 and v0.7.1 Together

v0.7.0 (released August 2026) delivered FP8/BF16/INT8 native LoRA and full fine-tuning for the DeepSeek series, along with a complete KTransformers × LLaMA-Factory Cookbook. v0.7.1 extends this in two directions: multimodal (Qwen VLM) and quantization-aware fine-tuning (RAWINT4).

Together, these two releases cover the major ultra-large MoE fine-tuning use cases in the current landscape: DeepSeek / Kimi / Qwen families, BF16 / FP8 / RAWINT4 weight formats, and both text-only and multimodal training paths.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
