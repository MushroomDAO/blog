---
title: "AirLLM：4GB 显存跑 70B 大模型，无需量化"
titleEn: "AirLLM: Run a 70B Model on 4GB of VRAM, No Quantization Required"
description: "lyogavin 开源的大模型极限推理工具，30k stars，Apache 2.0。通过逐层流式加载，在单张 4GB 显卡上运行 70B 模型，无需量化/蒸馏/剪枝。Kimi K3（2.8T）3.72GB、DeepSeek-V3（671B）约 12GB、Qwen3-235B 约 3GB。v3.0 新增 FP8 支持。支持 CUDA、Apple Silicon（macOS），同一 AutoModel 接口覆盖所有主流模型。"
descriptionEn: "lyogavin's open-source extreme-inference toolkit, 30k stars, Apache 2.0. Layer-by-layer streaming loads 70B models on a single 4GB GPU — no quantization, distillation, or pruning. Kimi K3 (2.8T) in 3.72GB, DeepSeek-V3 (671B) in ~12GB, Qwen3-235B in ~3GB. v3.0 adds FP8. CUDA and Apple Silicon (macOS) supported via a single AutoModel interface."
pubDate: "2026-08-08"
updatedDate: "2026-08-08"
category: "Tech-News"
tags: ["本地推理", "大模型", "显存优化", "AppleSilicon", "DeepSeek", "Qwen3", "Mycelium"]
heroImage: "../../assets/images/airllm-70b-inference-4gb-gpu-layer-streaming-banner.jpg"
---

*by Mycelium Protocol*

---

大模型本地推理的门槛通常由显存决定。70B 模型 FP16 需要约 140GB 显存，量化到 4bit 也要 35GB 左右——普通消费级 GPU 全部被挡在门外。

AirLLM 用另一种思路解决这个问题：不是把模型压缩到能放进显存，而是**按层流式加载**，每次只把当前层的权重载入显存，推理完立即卸载。

GitHub: https://github.com/lyogavin/airllm | ⭐ 30,047 | Apache 2.0

---

## 核心原理

传统推理：把整个模型加载到显存 → 一次推理。
AirLLM：把模型按层切分存盘 → 推理时逐层从磁盘加载到显存 → 推理完卸载 → 下一层。

代价：推理速度慢于全量加载（需要反复 I/O）。
收益：显存需求从"模型全量"降到"单层最大权重"。

对于稀疏 MoE 模型（如 Kimi K3、DeepSeek-V3），每个 token 只激活部分专家，AirLLM 只流式加载被激活的专家，显存需求进一步大幅降低。

---

## 当前支持的模型与显存需求

| 模型 | 参数量 | 显存需求 |
|------|--------|---------|
| **Kimi K3** | 2.8T (MoE) | **3.72GB** |
| **DeepSeek-V3** | 671B (MoE) | **~12GB** |
| **Qwen3-235B** | 235B (MoE) | **~3GB** |
| **Llama 3.1 405B** | 405B | **8GB** |
| **Qwen3-32B** | 32B | ~4GB |
| Llama 2/3 70B | 70B | **4GB** |

注：Kimi K3 需要额外安装 `pip install compressed-tensors flash-attn`，并使用 CUDA 12 + transformers 4.56.x。

---

## 快速开始

```bash
pip install airllm
```

一行代码加载，和普通 transformers 模型用法相同：

```python
from airllm import AutoModel

model = AutoModel.from_pretrained("Qwen/Qwen3-32B")

# 更大的模型，同样一行：
# model = AutoModel.from_pretrained("Qwen/Qwen3-235B-A22B")   # ~3GB 显存
# model = AutoModel.from_pretrained("deepseek-ai/DeepSeek-V3") # ~12GB 显存

input_tokens = model.tokenizer(
    ["What is the capital of France?"],
    return_tensors="pt",
    truncation=True, max_length=128, padding=False
)

output = model.generate(
    input_tokens['input_ids'].cuda(),
    max_new_tokens=20, use_cache=True, return_dict_in_generate=True
)

print(model.tokenizer.decode(output.sequences[0]))
```

首次运行时，模型会自动按层切分并保存到本地（需要足够磁盘空间）。

---

## 模型压缩加速（可选）

在 AirLLM 2.0+ 版本中，可以开启基于块量化的模型压缩，获得约 **3x 推理速度提升**，精度损失可忽略：

```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    compression='4bit'   # 或 '8bit'
)
```

需要先安装 bitsandbytes：`pip install -U bitsandbytes`

---

## macOS / Apple Silicon 支持

```bash
# macOS 专用安装
pip install airllm[cpu]
```

AirLLM 在 macOS Apple Silicon（M1/M2/M3/M4 系列）上同样可以运行 70B 模型，使用统一内存（Unified Memory）作为"显存"，配合逐层加载机制，M4 Max 或 Mac Studio 等高内存配置可以流畅推理。

---

## v3.0 更新

- **FP8 模型支持**：可直接加载 FP8 精度的模型权重
- **最新模型支持**：Kimi K3（2.8T）、Qwen3-235B、DeepSeek-V3（671B）
- **统一 AutoModel**：一个接口覆盖所有主流模型，不再需要指定模型类

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## AirLLM: Run 70B Models on 4GB GPU — No Quantization Required

*by Mycelium Protocol*

---

Local inference for large models is typically gated by VRAM. A 70B model in FP16 needs ~140GB; 4-bit quantized still needs ~35GB — most consumer GPUs are locked out entirely.

AirLLM takes a different approach: instead of compressing the model to fit in memory, it **streams the model layer by layer** — loading each layer's weights to GPU, running inference, then immediately unloading before moving to the next.

GitHub: https://github.com/lyogavin/airllm | ⭐ 30,047 | Apache 2.0

---

### How It Works

Traditional inference: load the entire model into VRAM → single-pass inference.
AirLLM: split the model layer-by-layer to disk → stream each layer into VRAM → run → unload → next layer.

Trade-off: slower than full-model loading (repeated I/O).
Benefit: VRAM requirement drops from "total model size" to "single largest layer."

For sparse MoE models (Kimi K3, DeepSeek-V3), each token only activates a subset of experts — AirLLM only streams the activated experts, dropping VRAM requirements dramatically further.

---

### Model Support and VRAM Requirements

| Model | Parameters | VRAM |
|-------|-----------|------|
| **Kimi K3** | 2.8T (MoE) | **3.72GB** |
| **DeepSeek-V3** | 671B (MoE) | **~12GB** |
| **Qwen3-235B** | 235B (MoE) | **~3GB** |
| **Llama 3.1 405B** | 405B | **8GB** |
| Qwen3-32B | 32B | ~4GB |
| Llama 2/3 70B | 70B | **4GB** |

Note: Kimi K3 requires `pip install compressed-tensors flash-attn`, CUDA 12, and transformers 4.56.x.

---

### Quick Start

```bash
pip install airllm
```

```python
from airllm import AutoModel

model = AutoModel.from_pretrained("Qwen/Qwen3-32B")
# Or go bigger with the same one line:
# model = AutoModel.from_pretrained("Qwen/Qwen3-235B-A22B")   # ~3GB VRAM
# model = AutoModel.from_pretrained("deepseek-ai/DeepSeek-V3") # ~12GB VRAM

input_tokens = model.tokenizer(
    ["What is the capital of France?"],
    return_tensors="pt", truncation=True, max_length=128, padding=False
)
output = model.generate(
    input_tokens['input_ids'].cuda(),
    max_new_tokens=20, use_cache=True, return_dict_in_generate=True
)
print(model.tokenizer.decode(output.sequences[0]))
```

On first run, the model is automatically split and saved layer-wise (needs sufficient disk space).

---

### Optional: 3× Speed via Model Compression

```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    compression='4bit'   # or '8bit'
)
```

Block-wise quantization gives ~3× inference speedup with negligible accuracy loss. Requires `pip install -U bitsandbytes`.

---

### macOS / Apple Silicon

```bash
pip install airllm[cpu]
```

AirLLM runs on Apple Silicon (M1–M4 series) using unified memory as the effective "VRAM." High-memory configs like M4 Max or Mac Studio can run 70B models without any code changes.

---

### v3.0 Highlights

- **FP8 model support**: load FP8-precision weights directly
- **Latest model support**: Kimi K3 (2.8T), Qwen3-235B, DeepSeek-V3 (671B)
- **Unified AutoModel**: one interface for all major models, no model class specification needed

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
