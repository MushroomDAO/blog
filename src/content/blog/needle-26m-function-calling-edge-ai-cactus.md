---
title: "Needle：2600 万参数，把 Gemini 的工具调用能力塞进手表和眼镜"
titleEn: "Needle: 26M Parameters — Distilling Gemini's Function Calling Into Watches and Glasses"
description: "Cactus Compute 开源的 Needle 把 Gemini 的 function calling 能力蒸馏进一个 2600 万参数的 Simple Attention Network（SAN），去掉 FFN 层，保留纯注意力，在手机/手表/眼镜级设备上达到 6000 tokens/s prefill 和 1200 tokens/s 解码。单轮工具调用优于 FunctionGemma-270m、Qwen-0.6B、Granite-350m。MIT 协议完全开源。"
descriptionEn: "Cactus Compute's open-source Needle distills Gemini's function calling capability into a 26M-parameter Simple Attention Network (SAN), dropping the FFN layer entirely, achieving 6000 tokens/s prefill and 1200 tokens/s decode on phone/watch/glasses-class devices. Outperforms FunctionGemma-270m, Qwen-0.6B, and Granite-350m on single-turn tool calling. MIT licensed, fully open-source."
pubDate: "2026-05-13"
updatedDate: "2026-05-13"
category: "Tech-News"
tags: ["Needle", "边缘AI", "工具调用", "小模型", "SAN", "Gemini蒸馏", "开源", "端侧推理", "function calling", "Cactus"]
heroImage: "../../assets/banner-future-is-now.jpg"
---

**结论先行（BLUF）**：Needle 是 Cactus Compute 开源的一个 2600 万参数模型，专门做 AI Agent 的工具调用（function calling）。它的核心反常识设计是**砍掉 FFN 层**——把通常占 Transformer 参数量 2/3 的 MLP 整个去掉，只留注意力机制。理由是：工具调用本质上是"检索 + 对齐 + 拼装 JSON"，不需要 FFN 提供的逐位置特征变换。结果：26M 参数，手机/手表/眼镜可跑，单轮工具调用性能超过体量是它 10 倍以上的竞品。

- **GitHub**：[cactus-compute/needle](https://github.com/cactus-compute/needle)
- **权重**：[Hugging Face / Cactus-Compute/needle](https://huggingface.co/Cactus-Compute/needle)
- **协议**：MIT，权重和数据生成流程完全开放

---

## 核心定位：让 Agent 真正跑进极小设备

Needle 的目标是把 Gemini 3.1 Flash Lite 的工具调用能力，通过知识蒸馏塞进一个极小的 Simple Attention Network（SAN）里。在 Cactus 推理引擎上的实测数据：

- **Prefill 速度**：6000 tokens/s
- **解码速度**：1200 tokens/s

这两个数字意味着什么？在手机上做一次完整的工具调用（接收用户语音 → 解析意图 → 选工具 → 组装 JSON 参数），延迟可以压到毫秒级。这是手表和眼镜形态的 AI Agent 真正能用的前提条件。

---

## 最反常识的设计：去掉 FFN

标准 Transformer 的参数分布大致是：**注意力 1/3，FFN 2/3**。Needle 把那个 2/3 整个删掉了。

**理由**：工具调用的全程逻辑是"对齐和复制"——

1. 把用户 query 与工具名对齐（检索）
2. 从 query 中抽取参数值（复制/提取）
3. 组装成结构化 JSON（拼装）

这三步都是注意力机制擅长的事。FFN 提供的"逐位置非线性特征变换"在这里是冗余的。砍掉之后：参数更少 → 显存带宽压力更低 → 边缘设备上推理直接更快。

---

## 架构细节

**整体结构**：encoder-decoder，12 层编码器 + 8 层解码器，d=512，8 头注意力 / 4 个 KV 头，BPE 词表 8192。编码器双向看完整工具定义，解码器通过 cross-attention 取用，KV cache 里不放输入 token。

**配套技巧**（每一条都有明确的工程动机）：

| 技巧 | 作用 |
|---|---|
| **Gated Residual** | 可学习的 sigmoid 门控残差，初始 0.5，保持梯度通路 |
| **ZCRMSNorm** | γ 初始为 0 的零中心 RMSNorm，训练起点即恒等映射 |
| **CLIP 风格对比学习头** | 从大工具集中先检索 top-k，再细粒度解码 |
| **Muon + AdamW 双优化器** | Muon 用 Newton-Schulz 保持 Q/K/V/O 投影正交，防止无 FFN 时的表征塌缩 |
| **INT4 QAT** | 每 100 步做一次伪量化，正则化 + 消除训练-部署量化 gap |
| **Token 级损失加权** | 参数值 4x、工具名 2x、键 1.5x、结构 token 1x |

其中 Muon 优化器是专门为"无 FFN"架构设计的保险——没有 FFN 时注意力投影矩阵容易退化，Newton-Schulz 迭代保持正交性，防止表征塌缩。

---

## 训练规模

**预训练**：16 张 TPU v6e，PleIAs/SYNTH 数据，2000 亿 tokens，耗时 27 小时。

**后训练**：Gemini 合成的 20 亿 tokens 单轮 function call 数据，覆盖定时器、消息、导航、智能家居等 15 个类别，耗时 45 分钟。

---

## 性能对比

在单轮工具调用任务上，Needle（26M）优于：

- FunctionGemma-270m（约为 Needle 的 **10 倍**参数量）
- Qwen-0.6B（约为 Needle 的 **23 倍**参数量）
- Granite-350m
- LFM2.5-350m

作者也坦承：这些更大的模型在多轮对话场景里有更广的能力，Needle 的优势是单轮工具调用这个精确的战场。

---

## 怎么用

```bash
git clone https://github.com/cactus-compute/needle
cd needle
pip install -e .
needle playground
# 打开 http://localhost:7860，用自己的工具集测试并一键微调
```

Mac/PC 均可运行，不需要 GPU 云资源。

---

## 为什么值得关注

Needle 的意义不在于"又一个小模型"，而在于它验证了一个架构假设：**当任务边界足够清晰时，可以大胆砍掉通用 Transformer 里的冗余组件。** 工具调用不需要 FFN；未来类似的专用边缘 AI 也可以用同样的思路——找到任务的本质操作，只保留对应的网络结构。

这对 Agent 架构的启示是：感知层（眼睛/耳朵/嘴巴）用小模型处理 I/O，工具调用路由用 Needle 这类极小专用模型，深层推理才上大模型——三层分工，整个 Agent 可以真正跑在本地设备上。

**参考链接**

- [GitHub - cactus-compute/needle](https://github.com/cactus-compute/needle)
- [Simple Attention Networks 文档](https://github.com/cactus-compute/needle/blob/main/docs/simple_attention_networks.md)
- [Hacker News 讨论](https://news.ycombinator.com/item?id=48111896)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Needle is a 26M-parameter open-source model from Cactus Compute, purpose-built for AI agent tool calling (function calling). Its core counterintuitive design is **dropping the FFN layer entirely** — removing the MLP that typically accounts for 2/3 of a Transformer's parameters, keeping only the attention mechanism. The rationale: tool calling is fundamentally "retrieval + alignment + JSON assembly" — none of which requires the positional feature transformation FFN provides. Result: 26M parameters, runs on phones/watches/glasses, outperforms competitors 10x its size on single-turn tool calling.

- **GitHub**: [cactus-compute/needle](https://github.com/cactus-compute/needle)
- **Weights**: [Hugging Face / Cactus-Compute/needle](https://huggingface.co/Cactus-Compute/needle)
- **License**: MIT, weights and data generation pipeline fully open

---

## Core Position: Agent That Actually Runs on Tiny Devices

Needle distills Gemini 3.1 Flash Lite's tool calling capability into a Simple Attention Network (SAN) through knowledge distillation. Benchmarks on the Cactus inference engine:

- **Prefill speed**: 6,000 tokens/s
- **Decode speed**: 1,200 tokens/s

On a phone, a complete tool call cycle (receive voice → parse intent → select tool → assemble JSON parameters) can complete in milliseconds — the prerequisite for AI agents that actually work in watch and glasses form factors.

---

## The Counterintuitive Design: Drop the FFN

Standard Transformer parameter distribution: ~1/3 attention, ~2/3 FFN. Needle deletes that 2/3 entirely.

**Rationale**: The entire logic of tool calling is "align and copy":
1. Match user query to tool names (retrieval)
2. Extract parameter values from query (copy/extract)
3. Assemble into structured JSON (assembly)

These are all what attention mechanisms excel at. The FFN's "per-position nonlinear feature transformation" is redundant here. Dropping it: fewer parameters → lower memory bandwidth pressure → faster inference on edge devices.

---

## Architecture Details

**Structure**: encoder-decoder, 12 encoder layers + 8 decoder layers, d=512, 8-head attention / 4 KV heads, BPE vocabulary 8192. Encoder sees complete tool definitions bidirectionally; decoder accesses via cross-attention; KV cache excludes input tokens.

**Engineering techniques** (each with explicit motivation):

| Technique | Purpose |
|---|---|
| **Gated Residual** | Learnable sigmoid-gated residual, init 0.5, maintains gradient path |
| **ZCRMSNorm** | Zero-centered RMSNorm with γ=0 init, identity mapping at training start |
| **CLIP-style contrastive head** | Retrieves top-k from large tool sets before fine-grained decoding |
| **Muon + AdamW dual optimizer** | Muon uses Newton-Schulz to keep Q/K/V/O projections orthogonal, preventing representation collapse without FFN |
| **INT4 QAT** | Pseudo-quantization every 100 steps: regularization + eliminates train-deploy quantization gap |
| **Token-level loss weighting** | Parameter values 4x, tool names 2x, keys 1.5x, structure tokens 1x |

---

## Training Scale

**Pre-training**: 16× TPU v6e, PleIAs/SYNTH data, 200B tokens, 27 hours.

**Post-training**: 2B tokens of Gemini-synthesized single-turn function call data covering 15 categories (timers, messages, navigation, smart home, etc.), 45 minutes.

---

## Performance

On single-turn tool calling, Needle (26M) outperforms:
- FunctionGemma-270m (~10× Needle's parameters)
- Qwen-0.6B (~23× Needle's parameters)
- Granite-350m, LFM2.5-350m

The author honestly acknowledges these larger models have broader capability in multi-turn dialogue — Needle's advantage is the precise battlefield of single-turn tool calling.

---

## Quick Start

```bash
git clone https://github.com/cactus-compute/needle
cd needle
pip install -e .
needle playground
# Open http://localhost:7860, test with your own tool set, one-click fine-tuning
```

Runs on Mac/PC, no GPU cloud resources required.

---

## Why This Matters

Needle's significance isn't "another small model" — it validates an architectural hypothesis: **when task boundaries are sufficiently clear, you can aggressively drop redundant components from general-purpose Transformers.** Tool calling doesn't need FFN; future specialized edge AI can apply the same logic — identify the essential operations for a task, keep only the corresponding network structures.

The implication for agent architecture: perception layer (eyes/ears/voice) uses small models for I/O, tool call routing uses ultra-small specialists like Needle, deep reasoning uses large models only when needed — three-layer division of labor, with the entire agent running genuinely on local devices.

**References**
- [GitHub - cactus-compute/needle](https://github.com/cactus-compute/needle)
- [Simple Attention Networks docs](https://github.com/cactus-compute/needle/blob/main/docs/simple_attention_networks.md)
- [Hacker News discussion](https://news.ycombinator.com/item?id=48111896)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
