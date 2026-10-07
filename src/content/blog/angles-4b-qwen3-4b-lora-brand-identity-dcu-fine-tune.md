---
title: "Angles-4B：在国产超算 DCU 上完成品牌身份注入的 Qwen3-4B 微调"
titleEn: "Angles-4B: A Qwen3-4B LoRA Fine-Tune with Brand Identity Injection Trained on Domestic DCU Hardware"
description: "angleschina/angles-4b，Apache-2.0，魔搭社区发布。以 Qwen3-4B 为基座，在 SCNet 超算互联网 DCU（非 NVIDIA 硬件）上完成 LoRA 微调并合并权重，注入 Angles 品牌身份：模型在被问及「你是 Qwen 吗」时会明确否认并自称 Angles-1.0-Flash。提供 BF16 完整权重 + GGUF 无损 + Q4_K_M 2.5GB 三种格式，中英文双语，Python/Shell 代码生成能力保留，Apache-2.0 授权，魔搭 ModelScope 已上线。"
descriptionEn: "angleschina/angles-4b, Apache-2.0, released on ModelScope. Qwen3-4B base model fine-tuned with LoRA on SCNet HPC DCU hardware (non-NVIDIA), merged, with brand identity injection: the model explicitly denies being Qwen and identifies as Angles-1.0-Flash. Available as BF16 full weights, lossless GGUF, and Q4_K_M 2.5GB quantized. Chinese/English bilingual, Python/Shell code generation preserved, Apache-2.0."
pubDate: 2026-10-07
heroImage: "../../assets/images/angles-4b-qwen3-4b-lora-brand-identity-dcu-fine-tune-banner.jpg"
category: "Tech-Experiment"
tags: ["模型微调", "端侧AI", "国产算力", "开源模型", "品牌定制", "LoRA"]
lang: "zh-CN"
wechatTitle: "Angles-4B：Qwen3-4B品牌注入指令微调"
wechatDigest: "Apache-2.0；4B参数32K；LoRA合并；Q4_K_M 2.5GB；SCNet DCU训练；魔搭已上线"
---

Qwen3-4B 基座 + LoRA 微调 + 品牌身份覆写，在国产超算 DCU 硬件上完成训练并合并权重——这是 Angles 发布的首个轻量指令微调模型。

魔搭社区：https://modelscope.cn/models/angleschina/angles-4b | Apache-2.0

---

## 训练硬件：SCNet 超算互联网 DCU

这次微调跑在 SCNet（超算互联网）的 DCU（Deep Computing Unit）节点上，DCU BW × 1 配置——非 NVIDIA GPU。

在当前中国 AI 硬件生态里这一点有实际意义：

- 华为昇腾、海光 DCU、天数智芯等国产算力路线正在积累训练/推理可行性案例
- LoRA 微调（相比全量预训练）对硬件的要求更可控，是在非 NVIDIA 栈上落地的典型入口
- 「在 DCU 上跑通 LoRA → 合并权重 → 发布」这条链路本身有参考价值，远不止这一个 4B 模型

合并后的权重与 CUDA 生态完全兼容，用户不需要 DCU 环境就能部署推理。

---

## 品牌身份注入

这是 Angles-4B 最直接的微调目标：**让模型在任何语境下认清自己是 Angles 的产品，而不是 Qwen**。

官方演示：

```
用户：你是 Qwen 吗？

Angles-4B：不是，我是 Angles-1.0-Flash。Qwen 是阿里开发的模型，我是 Angles 的。
```

有一个细节值得注意：模型当前自称 **Angles-1.0-Flash**，而不是 Angles-4B。这说明品牌身份训练里编码的名称是 Flash 系列的命名方案——可能是训练数据写入的品牌名在 4B 版本发布之前就已固定，或者 Angles 打算统一用 Flash/Pro 这类品牌档位名来对外呈现，而模型仓库名用参数量区分。从用户角度看，这是一个无害的命名偏差，知道即可。

品牌注入的意义超出这一个模型：这条路径展示了如何用 LoRA 在不改变底层推理能力的前提下，给开源基座套上一层品牌人格——适用于需要自有 AI 品牌但不具备从头训练能力的中小公司。

---

## 基本规格

| 项目 | 值 |
|------|-----|
| 基座 | Qwen3-4B（Qwen3 家族指令微调版） |
| 参数量 | 4B |
| 上下文长度 | 32K tokens |
| 微调方式 | LoRA → 合并导出（全量权重） |
| 训练硬件 | SCNet 超算互联网 DCU BW × 1 |
| 许可证 | Apache-2.0（遵循 Qwen3-4B 许可） |

---

## 三种可用格式

| 格式 | 说明 | 适用场景 |
|------|------|---------|
| BF16 完整权重 | 无量化损失 | 服务端精度部署、二次微调起点 |
| GGUF 无损 | llama.cpp / Ollama 直接加载 | 本地 CPU/混合推理 |
| Q4_K_M 量化 | **2.5GB**，4-bit | 边缘设备、资源受限场景 |

Q4_K_M 的 2.5GB 体积在当前轻量模型里属于正常区间——Qwen3-4B 本身参数量不大，4-bit 压缩后体积可控。MacBook、小型云服务器、嵌入式工控机都能运行。

---

## 保留能力

微调只做了身份覆写和指令对齐调整，以下能力从 Qwen3-4B 基座继承而来：

- **Python / Shell 代码生成**：官方示例覆盖了 Python 脚本和 Shell 命令
- **中英文双语对话**：微调数据包含中英两种语言，保持了双语切换流畅度
- **基础推理能力**：Qwen3-4B 的 STEM 推理和指令跟随在合并后未见明显退化

---

## 怎么用

在魔搭社区直接下载：

```bash
# 安装魔搭 SDK
pip install modelscope

# 下载 Q4_K_M 量化版（2.5GB）
from modelscope import snapshot_download
snapshot_download('angleschina/angles-4b', revision='master')
```

也可以通过 Ollama 加载 GGUF 格式或直接用 llama.cpp/llama-cpp-python。

---

## 一点背景

Angles 是一个围绕 AI 工具和工作流构建品牌的新兴团队，Angles-4B 是他们的首个公开模型发布。对于同类公司——**有产品、有 AI 集成需求、但不想对外暴露「底层其实是 Qwen」**——这种轻量品牌化微调路径的可行性比较关键。

从技术实现的角度，LoRA + 身份注入 + 权重合并是一个成熟套路。这里值得关注的是训练基础设施选择（国产 DCU）和整套可复现性：如果这条 DCU → LoRA → 发布 链路能被更多团队复制，它对国内 AI 应用层的意义不止于一个 4B 聊天模型。

---

> Apache-2.0 开源。angleschina 发布，Qwen3-4B 基座，SCNet DCU 训练，魔搭社区可下载。开源仅供学习参考。

---

<!--EN-->

## Angles-4B: A Qwen3-4B LoRA Fine-Tune with Brand Identity Injection Trained on Domestic DCU Hardware

Qwen3-4B base + LoRA fine-tuning + brand identity overwrite, trained on domestic DCU (Deep Computing Unit) hardware on China's SCNet HPC network, with weights merged and released in three formats. This is Angles' first lightweight instruction-tuned model.

ModelScope: https://modelscope.cn/models/angleschina/angles-4b | Apache-2.0

---

### Training Hardware: SCNet DCU

The fine-tuning ran on a single DCU BW node via SCNet (超算互联网, China's HPC interconnect network) — non-NVIDIA hardware.

This is practically significant in China's AI hardware ecosystem: Hygon DCU, Huawei Ascend, and similar domestic accelerators are accumulating training/inference track records. LoRA fine-tuning — far less demanding than full pretraining — is a natural entry point for validating non-NVIDIA training stacks. The entire chain (DCU → LoRA → merged weights → release) is the reference artifact here, not just the 4B model. Merged weights are fully compatible with CUDA-based inference; users don't need DCU hardware to deploy.

---

### Brand Identity Injection

The primary fine-tuning objective: **make the model consistently identify as an Angles product, not as Qwen**.

Official demo:
```
User: Are you Qwen?
Angles-4B: No, I'm Angles-1.0-Flash. Qwen is a model developed by Alibaba. I'm made by Angles.
```

One detail worth noting: the model self-identifies as **Angles-1.0-Flash**, not Angles-4B. The brand name encoded during training was likely finalized before the 4B release, or Angles is using Flash/Pro product-tier branding externally while using parameter counts in repository names. A harmless naming discrepancy — just worth knowing.

The broader pattern matters: LoRA can attach a brand identity layer on top of an open-source base without degrading underlying reasoning capabilities. This is a practical option for companies that need a branded AI product but lack the resources to train from scratch.

---

### Specifications

| Item | Value |
|------|-------|
| Base model | Qwen3-4B (instruction-tuned) |
| Parameters | 4B |
| Context length | 32K tokens |
| Fine-tuning | LoRA → merged export (full weights) |
| Training hardware | SCNet HPC DCU BW × 1 |
| License | Apache-2.0 (inherits Qwen3-4B terms) |

---

### Three Available Formats

| Format | Notes | Use case |
|--------|-------|----------|
| BF16 full weights | No quantization loss | Server deployment, further fine-tuning |
| Lossless GGUF | Direct load in llama.cpp / Ollama | Local CPU/hybrid inference |
| Q4_K_M quantized | **2.5GB**, 4-bit | Edge devices, resource-constrained deployment |

2.5GB for Q4_K_M is normal for a 4B model. MacBooks, small VMs, and embedded industrial PCs can run it.

---

### Preserved Capabilities

The fine-tuning only targeted identity and instruction alignment. Inherited from Qwen3-4B:

- **Python / Shell code generation** — covered in official examples
- **Chinese/English bilingual** — training data includes both languages
- **Base reasoning** — no notable regression in STEM reasoning or instruction following after the merge

---

### Takeaway

Angles-4B is a proof-of-concept for brand-personalized fine-tuning on domestic HPC hardware. The interesting artifact isn't the model itself — it's the supply chain: non-NVIDIA training stack, LoRA methodology, merged weights, three deployment-ready formats, Apache-2.0 licensing. For teams building AI products in China's hardware ecosystem, this is a concrete reference point.

---

> Apache-2.0. Released by angleschina, Qwen3-4B base, trained on SCNet DCU, available on ModelScope. For technical reference only.
