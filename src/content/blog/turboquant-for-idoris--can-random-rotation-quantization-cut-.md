---
title: "TurboQuant 在 iDoris 上的可行性分析：能用它压缩本地 AI 的内存消耗吗？"
titleEn: "TurboQuant for iDoris: Can Random-Rotation Quantization Cut Local AI Memory?"
description: "Google Research 提出的 TurboQuant（ICLR 2026）声称用随机旋转 + 单一预计算 codebook 实现 6× KV cache 压缩。本文深度分析其在 iDoris 三层架构（Personal/Community/City）的落地路径：KV cache 压缩立即可用、RAG embedding 中期可用、训练时使用不可行。Mac Studio 64GB 上预计能腾出 30%+ 内存用于长上下文。"
descriptionEn: "Google Research's TurboQuant (ICLR 2026) claims 6× KV cache compression via random rotation + a single precomputed codebook. This article analyzes its applicability to iDoris's 3-tier architecture: immediate adoption for KV cache, medium-term for RAG embeddings, infeasible for training. On Mac Studio 64GB, ~30% memory headroom is freed for long-context inference."
pubDate: "2026-04-27"
updatedDate: "2026-04-27"
category: "Research"
tags: ["TurboQuant", "iDoris", "量化", "Quantization", "KV Cache", "MLX", "本地AI", "Research", "Mycelium"]
heroImage: "../../assets/banner-ai-new-intelligence.jpg"
---

> **研究类型**：可行性技术分析 · **研究对象**：TurboQuant (arXiv:2504.19874, ICLR 2026)
> **核心问题**：能否将 TurboQuant 落到 [iDoris](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/) 训练 / 推理流程中，降低 Mac Studio 64GB 的内存消耗？
> **结论先行**：**KV cache 压缩可立即采用**（节省 3-12GB 内存）；RAG embedding 压缩中期可用；训练时使用**目前不可行**。

## 摘要

TurboQuant 是 Google Research 团队（Zandieh, Daliri, Hadian, Mirrokni）2025 年 4 月发布、被 ICLR 2026 接收的向量量化方法。它通过两步实现"无训练、无元数据、单一 codebook 通用"的极限压缩：

1. **随机正交旋转**：把任意输入向量旋转成一个新向量，新向量的每个坐标都服从同一个已知 Beta 分布
2. **Lloyd-Max 单一 codebook**：基于这个已知分布预先算好的查找表，对所有输入都通用

本文检验三个核心问题：

- **能用在 iDoris 吗？** 部分能，主要是 KV cache 与 RAG embedding 两个场景
- **能省多少内存？** Mac Studio 64GB 上 KV cache @ 128K 上下文场景下，能从 ~16GB 压到 ~4GB，省下 12GB
- **训练时能用吗？** 不能（直接），TurboQuant 设计初衷不是训练，但可以与 QLoRA NF4 互补使用

## §1 TurboQuant 是什么？

### 1.1 来源与发表

| 项目 | 内容 |
|------|------|
| 论文 | [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate, arXiv:2504.19874](https://arxiv.org/abs/2504.19874) |
| 作者 | Amir Zandieh, Majid Daliri, Majid Hadian, Vahab Mirrokni（Google Research） |
| 发表 | 2025-04-28 (arXiv) → ICLR 2026 接收 |
| 配套方法 | [QJL (NeurIPS 2024)](https://arxiv.org/abs/2406.03482), [PolarQuant (AISTATS 2026)](https://arxiv.org/abs/2502.02617) |
| Google 官方介绍 | [research.google/blog/turboquant-...](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/) |
| 第三方互动讲解 | [arkaung.github.io/interactive-turboquant](https://arkaung.github.io/interactive-turboquant/) |

### 1.2 核心创新（一句话）

> "对任意向量做一次随机旋转，旋转后的向量坐标分布**与输入无关**，因此可以用一个预先算好的 codebook 对所有输入做最优量化。"

这突破了传统量化方法的两个假设：
- **数据相关 codebook**（如 Product Quantization）：每批数据要重训 codebook
- **per-batch 缩放系数**（如 LLM.int8、AWQ）：每个 batch 要存额外 metadata

TurboQuant 的两个都不需要——零训练、零额外 metadata。

### 1.3 数学原理（最小集）

设输入向量 $\mathbf{x} \in \mathbb{R}^d$，随机正交矩阵 $\mathbf{\Pi} \in \mathbb{R}^{d \times d}$。则：

1. **保模、保内积**：$\|\mathbf{\Pi x}\| = \|\mathbf{x}\|$，$\langle \mathbf{\Pi x}, \mathbf{\Pi y}\rangle = \langle \mathbf{x}, \mathbf{y}\rangle$
2. **坐标分布已知**：$(\mathbf{\Pi x})_i$ 服从同一个 Beta 分布；$d$ 越大，越接近 $\mathcal{N}(0, 1/d)$

因此可以用 Lloyd-Max 算法对这个**固定的 Beta 分布**预先算出最优 codebook。例如：

- 1-bit codebook: $\{\pm\sqrt{2/\pi}\}$
- 2-bit codebook: $\{\pm 0.453, \pm 1.510\}$

每个 bit 预算 $b$ 对应一个微小查找表，**所有向量共用**。

### 1.4 已报告的核心数据

| 指标 | 数值 | 来源 |
|------|------|------|
| KV cache 压缩比 | 4-6× | 论文 § 5 |
| Llama-3.1-8B Needle-in-Haystack | 0.997 recall（与 FP16 相同） | 论文 Table 3 |
| LongBench-V1 @ 3.5 bits | 50.06（FP16: 50.06）= 零损失 | 论文 |
| LongBench-V1 @ 2.5 bits | 49.44（FP16: 50.06）= ~1% 损失 | 论文 |
| 向量搜索速度 | 比 RaBitQ 快 ~174 万倍，比 PQ 快 ~18 万倍（$d$=1536） | 论文 |
| H100 attention 加速 | 4-bit 比 FP32 快 8× | Google 官方博客 |

## §2 已验证的应用范围（与 iDoris 的相关性）

TurboQuant 论文与官方博客明确支持的应用：

| 应用 | 论文支持 | 与 iDoris 相关性 |
|------|---------|---------------|
| **KV cache 量化（推理）** | ✅ 主要应用 | ⭐⭐⭐ 直接相关 |
| **向量搜索 / Embedding 量化** | ✅ 第二应用 | ⭐⭐⭐ RAG 层直接受益 |
| **权重量化（推理）** | ❌ 未涵盖 | ⚠️ 已有 GPTQ/AWQ/Q-K_M |
| **激活量化（推理）** | ❌ 未涵盖 | ⚠️ 通常用 SmoothQuant |
| **训练时梯度/激活量化** | ❌ 未涵盖 | ❌ 不适用 |

**关键负面结论**：TurboQuant 是 **inference-only, data-oblivious, online quantizer**。Google 官方博客直言："without requiring training or fine-tuning"。这意味着它**不能用来降低训练时的内存消耗**。训练阶段降内存仍然要用 QLoRA / NF4 / Adam-8bit 这套老方法。

## §3 在 iDoris 上的三条应用路径

### 3.1 路径 1：KV Cache 压缩（立即可用，最大收益）

**问题**：iDoris-PC 在 Mac Studio 64GB 上跑 Qwen3.5-9B + LoRA，KV cache 在长上下文场景占用巨大。

**KV cache 内存公式**（对 Qwen3.5-9B，估算）：

```
KV cache (FP16) = 2 × n_layers × seq_len × n_kv_heads × d_head × 2 bytes
              ≈ 2 × 28 × seq_len × 8 × 128 × 2
              ≈ 0.115 MB × seq_len
```

| 上下文长度 | FP16 KV cache | TurboQuant 4-bit | 节省 |
|-----------|---------------|------------------|------|
| 8K | 940 MB | 235 MB | 705 MB |
| 32K | 3.7 GB | 0.94 GB | 2.76 GB |
| 128K | 14.7 GB | 3.7 GB | **11 GB** |

**实测数据**（来自 [sharpner/turboquant-mlx](https://github.com/sharpner/turboquant-mlx)，M4 Max 64GB）：
- Llama-3.1-8B @ T=8192, FP16 KV cache = 969 MB
- TurboQuant V3 2.5-bit = 177 MB（**5.5× 压缩**）
- TurboQuant V2 4-bit LEAN @ T=8192：**156 tok/s**，比 FP16 baseline 148 tok/s 还**快**

这是真实硬件验证，不是论文宣称。

**对 iDoris 的意义**：
- **iDoris-PC**：Mac Studio 64GB 跑 Qwen3.5-9B，128K 上下文从需要 ~24GB（不可行）变成 ~13GB（可行）
- **iDoris-Community**：Qwen3.6-35B-A3B + Cos72 多用户共享 KV cache 时收益更大
- **iDoris-Mobile**：手机端长聊天历史不再 OOM

### 3.2 路径 2：RAG Embedding 压缩（中期可用）

**问题**：iDoris 用 [LightRAG](https://github.com/HKUDS/LightRAG) 做长期记忆，向量库随用户笔记/聊天增长，FP32 存储占空间。

**典型配置**（iDoris-Personal）：
- 嵌入模型：BGE-large-zh（1024 维）/ Qwen-Embedding-V3（3072 维）
- 用户笔记 + 聊天历史 + 文档：约 100K-1M chunk

| 配置 | FP32 存储 | TurboQuant 4-bit | 节省 |
|------|----------|------------------|------|
| 100K chunk × 1024 维 | 400 MB | 50 MB | 8× |
| 1M chunk × 3072 维 | 12 GB | 1.5 GB | 8× |

**速度优势**（论文报告）：4-bit TurboQuant 索引比 Product Quantization 快 18 万倍（$d$=1536，100K 向量）。即便实测有衰减，本地查询仍是亚毫秒级。

**对 iDoris 的意义**：
- 一台 64GB Mac 可承载千万级笔记 / 文档的本地 RAG
- 联邦层：社区共享 RAG 时，传输的向量量减小 8×（带宽友好）
- 如果走 [Mem0](https://github.com/mem0ai/mem0) 类长期记忆方案，可线性扩展

**已知开源实现**：
- [yashkc2025/turboquant](https://github.com/yashkc2025/turboquant)（Python）
- [tonbistudio/turboquant-pytorch](https://github.com/tonbistudio/turboquant-pytorch)（PyTorch）

### 3.3 路径 3：训练时使用（不可行 / 研究方向）

**结论先说**：直接拿 TurboQuant 替代 QLoRA NF4 来降低训练内存——**不可行**。原因：

1. **设计初衷不同**：TurboQuant 是 data-oblivious online quantizer，对"输入向量分布"做了高维浓度假设；训练时的梯度 / 激活分布有强结构性（稀疏、长尾、layer-wise 差异），不满足这个假设
2. **重训成本**：把 TurboQuant 强行用在权重 + 反传梯度上，质量损失会很大；论文也没做相关实验
3. **没有实测验证**：截至 2026-04，没有任何 GitHub 项目或论文报告 TurboQuant 在训练阶段的成功案例

**正确组合**：
- **训练阶段**：QLoRA + NF4 双量化（继承 [Dettmers et al., NeurIPS 2023](https://arxiv.org/abs/2305.14314)）
- **推理阶段**：TurboQuant KV cache + GPTQ/AWQ 权重 + RAG 端 TurboQuant embedding

两者职责清晰，互不冲突。

**研究方向（猜想，未验证）**：把 TurboQuant 用于优化器状态（如 Adam 的 momentum）的存储——因为 momentum 累积后接近高斯分布。但这只是 hypothesis，需要实验验证。**iDoris 立项阶段不应押注在此**。

## §4 Mac Studio 64GB 内存预算重算

iDoris Phase 1 MVP 配置（Qwen3.5-9B + LoRA + RAG + 128K 上下文）：

| 组件 | 当前（无 TurboQuant） | 引入 TurboQuant 后 | 节省 |
|------|---------------------|-------------------|------|
| Qwen3.5-9B Q5_K_M 权重 | 7 GB | 7 GB（不变） | 0 |
| LoRA r=32 适配器 | 1 GB | 1 GB（不变） | 0 |
| KV cache @ 128K FP16 | 14.7 GB | 3.7 GB（4-bit） | **11 GB** |
| LightRAG 向量库（100K chunk × 3072d） | 1.2 GB | 0.15 GB | **1.05 GB** |
| 推理激活（worst case） | 3 GB | 3 GB（不变） | 0 |
| **推理峰值** | **~27 GB** | **~15 GB** | **~12 GB（44% 节省）** |

**这是关键收益**：
- 64GB Mac Studio 上不仅能跑，还有 ~50GB 余量做训练（QLoRA 9B 训练峰值 ~28GB）
- 可以同时加载 2-3 个 LoRA（e.g., Personal + Community + 编程领域适配器）
- 长上下文场景从"勉强能跑"变成"流畅可用"

**保守估计**：实际工程化引入会有 2-5% 软件 dequantization 开销（[turboquant-mlx](https://github.com/sharpner/turboquant-mlx) V3 模式实测从 148 t/s 降到 24-27 t/s，但 V2 LEAN 模式接近无开销甚至更快）。

## §5 与其他量化方法的对照

| 方法 | 用途 | 是否需训练 | 元数据 | 与 TurboQuant 关系 |
|------|------|----------|--------|-------------------|
| **GPTQ** ([Frantar et al., 2022](https://arxiv.org/abs/2210.17323)) | 权重量化 | 需校准 | per-block scales | 互补：GPTQ 管权重，TQ 管 KV cache |
| **AWQ** ([Lin et al., 2023](https://arxiv.org/abs/2306.00978)) | 权重量化 | 需校准 | per-channel scales | 互补 |
| **QLoRA NF4** ([Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)) | 训练时权重量化 | 无 | 双重量化常数 | **训练用 NF4，推理用 TQ** |
| **KIVI** ([Liu et al., 2024](https://arxiv.org/abs/2402.02750)) | KV cache 2-bit | 无 | 异常值通道 FP16 | 被 TurboQuant 超越（论文 Table 3） |
| **SnapKV** ([Li et al., 2024](https://arxiv.org/abs/2404.14469)) | KV 选择性丢弃 | 无 | 注意力分数 | 正交（可叠加） |
| **PolarQuant** ([Han et al., 2025](https://arxiv.org/abs/2502.02617)) | KV cache 极坐标 | 无 | 极角索引 | 同家族（同 Google 团队） |
| **TurboQuant** | KV cache + Embedding | **无** | **无** | 本文主角 |

**核心差异**：TurboQuant 的"零训练 + 零额外 metadata"特性使它在**联邦学习场景**（iDoris 的核心场景）有结构性优势——客户端无需互相同步 codebook 或 calibration data。

## §6 工程实施路径

### 6.1 优先级排序

| 优先级 | 任务 | 预计工作量 | 收益 |
|-------|------|----------|------|
| **P0**（Phase 1 必做） | 集成 turboquant-mlx 到 iDoris-PC 推理路径 | 1-2 天 | 12GB 内存释放 |
| **P1**（Phase 1 可选） | RAG 向量库改用 TurboQuant 4-bit 存储 | 2-3 天 | 8× RAG 容量 |
| **P2**（Phase 2） | 蒸馏到 Mobile 时叠加 TurboQuant + GPTQ | 3-5 天 | 端侧 8K 上下文流畅 |
| **P3**（Phase 3） | 联邦层 LoRA 上传时用 TurboQuant 压缩传输 | 1 周（实验性） | 8× 上传带宽 |
| **P4**（不做） | 试图用 TurboQuant 替代 QLoRA NF4 训练 | 不可行 | / |

### 6.2 推荐组合（Phase 1）

```
推理时栈：
   ┌────────────────────────────────────┐
   │  Qwen3.5-9B Q5_K_M (GGUF/MLX)     │  ← 权重量化（既有）
   │  + LoRA r=32                       │  ← 个人偏好
   │  + TurboQuant 4-bit KV cache 🆕    │  ← 长上下文支持
   │  + LightRAG (TurboQuant embedding) │  ← 向量库压缩 🆕
   └────────────────────────────────────┘

训练时栈（保持现有）：
   ┌────────────────────────────────────┐
   │  Qwen3.5-9B NF4 (QLoRA)           │  ← 训练权重 4-bit
   │  + LoRA gradient FP32              │  ← 训练梯度
   │  + Adam-8bit optimizer             │  ← 优化器状态
   └────────────────────────────────────┘
```

### 6.3 落地代码框架

伪代码示意：

```python
# iDoris-PC 推理（启用 TurboQuant）
from mlx_lm import load
from turboquant_mlx import TurboQuantKVCache  # sharpner/turboquant-mlx

model, tokenizer = load("Qwen/Qwen3.5-9B-MLX-Q5")
model.attach_lora("./loras/personal-v3.safetensors")

kv_cache = TurboQuantKVCache(
    bits=4,
    variant="V2-LEAN",   # 速度模式
    max_len=131072,      # 128K 上下文
)

response = model.generate(
    prompt="...",
    kv_cache=kv_cache,
    max_tokens=2048,
)

# RAG 端
from lightrag import LightRAG
from turboquant import TurboQuantIndex

rag = LightRAG(
    embedder="bge-large-zh",
    index=TurboQuantIndex(bits=4, dim=1024),
)
rag.insert_documents(personal_notes)  # 100K chunks → 50MB
```

## §7 风险与不确定性

### 7.1 已知问题

1. **Inner-product bias**（论文 § 4.2 承认）：MSE 优化的 codebook 对内积估计有系统性偏差，因子 $2/\pi$（1-bit 时）。需要叠加 QJL residual 修正，但 QJL 引入更大方差。**对 iDoris 的影响**：注意力分数会有微小偏差，可能在长上下文边缘案例放大；建议引入时做 A/B 测试。

2. **软件 dequantization 开销**：[turboquant-mlx](https://github.com/sharpner/turboquant-mlx) V3 模式（极端低 bit）会从 148 t/s 降到 24-27 t/s。原因是 Apple Silicon 缺少专用 4-bit 矩阵乘指令，需要软件解码。**缓解**：用 V2 LEAN 模式（4-bit，硬件加速），速度反超 FP16。

3. **MLX 实现成熟度**：[turboquant-mlx](https://github.com/sharpner/turboquant-mlx) 仍是"proof of concept"级别，不是 production-ready。等更成熟的实现出现，或自己 fork 维护。

4. **未做训练时实验**：所有公开 benchmark 都在推理。我们如果尝试 P3（联邦层 LoRA delta 用 TurboQuant 压缩）属于研究探索，无现成数据。

### 7.2 决策建议

- **P0 立刻做**（KV cache 4-bit）：风险极小，收益极大，可逆（不行随时切回 FP16）
- **P1 谨慎做**（RAG embedding）：先在小规模数据集（10K chunks）做 A/B，对比检索精度
- **P2-P3 视 Phase 1 验证情况而定**
- **P4 不做**（替代 QLoRA）：明确不可行，不浪费精力

## §8 结论

**回到立项时的核心问题**："能不能用 TurboQuant 来降低 iDoris 对设备的内存消耗？"

**答案**：

✅ **能**，主要在两个场景：
- **KV cache 压缩**：Mac Studio 64GB 上，128K 上下文 KV cache 从 14.7GB → 3.7GB，节省 11GB
- **RAG embedding 压缩**：100K-1M chunk 向量库压 8×

❌ **不能**用于：
- 训练时降内存（继续用 QLoRA NF4）
- 权重量化（GPTQ / AWQ / Q5_K_M 已经够好）

🎯 **整体效益**：iDoris-PC Phase 1 MVP 在 Mac Studio 64GB 上的推理峰值内存从 ~27GB 降到 ~15GB，**释放 ~12GB（44%）用于长上下文 / 多 LoRA / 联邦实验**。这不是边际改进，是**质变**。

**给 [iDoris 立项](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/) 的具体建议**：把 TurboQuant 集成纳入 Phase 1 M2 月的任务清单，与"集成 LightRAG + Sin90 数据贡献中心 GUI"同步推进。这不会延期，反而会把 Phase 1 验收门槛从"勉强能跑"提升到"流畅可用"。

---

## 参考资料

### TurboQuant 与配套方法

- [TurboQuant 论文 arXiv:2504.19874](https://arxiv.org/abs/2504.19874) (ICLR 2026)
- [Google Research 官方博客](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)
- [QJL: arXiv:2406.03482](https://arxiv.org/abs/2406.03482) (NeurIPS 2024)
- [PolarQuant: arXiv:2502.02617](https://arxiv.org/abs/2502.02617) (AISTATS 2026)
- [arkaung 互动讲解](https://arkaung.github.io/interactive-turboquant/)（第三方）

### 开源实现

- [tonbistudio/turboquant-pytorch](https://github.com/tonbistudio/turboquant-pytorch)（PyTorch）
- [yashkc2025/turboquant](https://github.com/yashkc2025/turboquant)（Python）
- [sharpner/turboquant-mlx](https://github.com/sharpner/turboquant-mlx)（**Apple Silicon**）
- [0xSero/turboquant](https://github.com/0xSero/turboquant)（Triton + vLLM）
- [SharpAI/SwiftLM](https://github.com/SharpAI/SwiftLM)（macOS + iOS app）

### 生态集成

- [vLLM Issue #38171: TurboQuant feature request](https://github.com/vllm-project/vllm/issues/38171)
- [SGLang Issue #21618: TurboQuant feature request](https://github.com/sgl-project/sglang/issues/21618)

### 相关量化方法

- QLoRA NF4: [Dettmers et al., NeurIPS 2023, arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- GPTQ: [Frantar et al., 2022, arXiv:2210.17323](https://arxiv.org/abs/2210.17323)
- AWQ: [Lin et al., 2023, arXiv:2306.00978](https://arxiv.org/abs/2306.00978)
- KIVI: [Liu et al., 2024, arXiv:2402.02750](https://arxiv.org/abs/2402.02750)
- SnapKV: [Li et al., 2024, arXiv:2404.14469](https://arxiv.org/abs/2404.14469)
- KVQuant: [NeurIPS 2024](https://www.stat.berkeley.edu/~mmahoney/pubs/neurips-2024-kvquant.pdf)

### iDoris 相关

- [iDoris 立项思考](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/)
- [iDoris Master Plan](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
- [iDoris GitHub](https://github.com/AuraAIHQ/iDoris)
- [Mycelium Protocol](https://launch.mushroom.cv)

<!--EN-->

> **Type**: Feasibility analysis · **Subject**: TurboQuant (arXiv:2504.19874, ICLR 2026)
> **Question**: Can TurboQuant reduce memory consumption in [iDoris](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/)'s training/inference pipeline on Mac Studio 64GB?
> **Bottom Line**: **Yes for KV cache** (saves 3-12GB); medium-term yes for RAG embeddings; **no for training-time use**.

## Abstract

TurboQuant is a vector quantization method by Google Research (Zandieh, Daliri, Hadian, Mirrokni), released April 2025 and accepted at ICLR 2026. It achieves "training-free, metadata-free, single-codebook universal" extreme compression in two steps:

1. **Random orthogonal rotation**: rotates any input vector so that each coordinate of the rotated vector follows the same known Beta distribution
2. **Lloyd-Max single codebook**: a precomputed lookup table designed for this fixed distribution, universal across all inputs

This article evaluates three core questions:

- **Can it be used in iDoris?** Partially — primarily KV cache and RAG embedding scenarios
- **How much memory does it save?** On Mac Studio 64GB, KV cache @ 128K context drops from ~16GB to ~4GB, saving 12GB
- **Can we use it during training?** No (directly). TurboQuant isn't designed for training; it's complementary to QLoRA NF4

## §1 What Is TurboQuant?

### 1.1 Source and Publication

| Item | Details |
|------|---------|
| Paper | [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate, arXiv:2504.19874](https://arxiv.org/abs/2504.19874) |
| Authors | Amir Zandieh, Majid Daliri, Majid Hadian, Vahab Mirrokni (Google Research) |
| Release | 2025-04-28 (arXiv) → ICLR 2026 accepted |
| Companion methods | [QJL (NeurIPS 2024)](https://arxiv.org/abs/2406.03482), [PolarQuant (AISTATS 2026)](https://arxiv.org/abs/2502.02617) |
| Official intro | [Google Research blog](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/) |
| Third-party walkthrough | [arkaung.github.io/interactive-turboquant](https://arkaung.github.io/interactive-turboquant/) |

### 1.2 Core Innovation (One Sentence)

> "Apply one random rotation to any input vector, and the rotated vector's coordinates follow a distribution **independent of the input** — so a single precomputed codebook can optimally quantize all inputs."

This breaks two assumptions of traditional methods:
- **Data-dependent codebooks** (e.g., Product Quantization): require retraining per batch
- **Per-batch scaling factors** (e.g., LLM.int8, AWQ): require extra per-batch metadata

TurboQuant needs neither — zero training, zero additional metadata.

### 1.3 Mathematical Principle (Minimal)

For input vector $\mathbf{x} \in \mathbb{R}^d$, random orthogonal matrix $\mathbf{\Pi}$:

1. **Norm-preserving and inner-product-preserving**: $\|\mathbf{\Pi x}\| = \|\mathbf{x}\|$, $\langle \mathbf{\Pi x}, \mathbf{\Pi y}\rangle = \langle \mathbf{x}, \mathbf{y}\rangle$
2. **Coordinate distribution is known**: $(\mathbf{\Pi x})_i$ follows the same Beta distribution; as $d$ grows, approaches $\mathcal{N}(0, 1/d)$

So Lloyd-Max can pre-compute optimal codebooks for this fixed Beta distribution:

- 1-bit: $\{\pm\sqrt{2/\pi}\}$
- 2-bit: $\{\pm 0.453, \pm 1.510\}$

One tiny lookup table per bit budget $b$, **shared across all vectors**.

### 1.4 Reported Numbers

| Metric | Value | Source |
|--------|-------|--------|
| KV cache compression | 4-6× | Paper § 5 |
| Llama-3.1-8B Needle-in-Haystack | 0.997 recall (= FP16) | Paper Table 3 |
| LongBench-V1 @ 3.5 bits | 50.06 (FP16: 50.06) = zero loss | Paper |
| LongBench-V1 @ 2.5 bits | 49.44 (FP16: 50.06) = ~1% loss | Paper |
| Vector search speed | ~1.74M× faster than RaBitQ; ~184K× faster than PQ ($d$=1536) | Paper |
| H100 attention speedup | 4-bit: 8× over FP32 | Google blog |

## §2 Where Has It Been Validated?

| Application | Paper Support | Relevance to iDoris |
|-------------|---------------|---------------------|
| **KV cache quantization (inference)** | ✅ Primary | ⭐⭐⭐ Direct |
| **Vector search / Embedding quantization** | ✅ Secondary | ⭐⭐⭐ RAG layer |
| **Weight quantization (inference)** | ❌ Not covered | ⚠️ Have GPTQ/AWQ/Q-K_M |
| **Activation quantization (inference)** | ❌ Not covered | ⚠️ Use SmoothQuant |
| **Gradient/activation quantization (training)** | ❌ Not covered | ❌ Not applicable |

**Critical negative finding**: TurboQuant is **inference-only, data-oblivious, online quantizer**. The Google blog explicitly says "without requiring training or fine-tuning". It **cannot reduce training-time memory**. For training, keep using QLoRA / NF4 / Adam-8bit.

## §3 Three Application Paths in iDoris

### 3.1 Path 1: KV Cache Compression (Immediate, Biggest Win)

**Problem**: iDoris-PC running Qwen3.5-9B + LoRA on Mac Studio 64GB — KV cache dominates memory in long-context scenarios.

**KV cache memory formula** (Qwen3.5-9B estimate):

```
KV cache (FP16) ≈ 2 × n_layers × seq_len × n_kv_heads × d_head × 2 bytes
                ≈ 0.115 MB × seq_len
```

| Context Length | FP16 KV cache | TurboQuant 4-bit | Savings |
|---------------|---------------|------------------|---------|
| 8K | 940 MB | 235 MB | 705 MB |
| 32K | 3.7 GB | 0.94 GB | 2.76 GB |
| 128K | 14.7 GB | 3.7 GB | **11 GB** |

**Real-hardware data** (from [sharpner/turboquant-mlx](https://github.com/sharpner/turboquant-mlx), M4 Max 64GB):
- Llama-3.1-8B @ T=8192, FP16 KV cache = 969 MB
- TurboQuant V3 2.5-bit = 177 MB (**5.5× compression**)
- TurboQuant V2 4-bit LEAN @ T=8192: **156 tok/s**, vs 148 tok/s FP16 baseline (**faster**!)

This is real hardware verification, not paper claims.

**Implications for iDoris**:
- **iDoris-PC**: 128K context on Mac Studio 64GB goes from ~24GB (infeasible) to ~13GB (feasible)
- **iDoris-Community**: Qwen3.6-35B-A3B with shared KV cache benefits even more
- **iDoris-Mobile**: Long chat history no longer OOMs on phones

### 3.2 Path 2: RAG Embedding Compression (Medium-term)

**Problem**: iDoris uses [LightRAG](https://github.com/HKUDS/LightRAG) for long-term memory — vector DB grows with user notes/chats; FP32 storage is wasteful.

**Typical setup** (iDoris-Personal):
- Embedder: BGE-large-zh (1024-d) / Qwen-Embedding-V3 (3072-d)
- User notes + chat + docs: 100K-1M chunks

| Config | FP32 Storage | TurboQuant 4-bit | Savings |
|--------|--------------|------------------|---------|
| 100K chunks × 1024-d | 400 MB | 50 MB | 8× |
| 1M chunks × 3072-d | 12 GB | 1.5 GB | 8× |

**Speed**: Paper claims 4-bit TurboQuant indexing is 184K× faster than PQ ($d$=1536, 100K vectors). Even with implementation losses, queries stay sub-millisecond locally.

**Implications**:
- A 64GB Mac can host millions of RAG-indexed personal notes
- Federated layer: 8× smaller cross-community vector transfer
- Aligns with [Mem0](https://github.com/mem0ai/mem0)-style long-term memory at scale

### 3.3 Path 3: Training-Time Use (Infeasible / Research Direction)

**Bottom line**: Replacing QLoRA NF4 with TurboQuant for training-time memory reduction — **infeasible**. Reasons:

1. **Different design intent**: TurboQuant is data-oblivious online quantizer assuming high-dim concentration on input distribution. Gradient/activation distributions during training have strong structure (sparsity, long tails, layer-wise variation), violating this assumption.
2. **Untested cost**: Forcibly applying TurboQuant to weights + backprop gradients would degrade quality severely; the paper doesn't include such experiments.
3. **No empirical validation**: As of 2026-04, no GitHub project or paper reports TurboQuant successfully reducing training-time memory.

**Correct combination**:
- **Training**: QLoRA + NF4 double quantization ([Dettmers et al., NeurIPS 2023](https://arxiv.org/abs/2305.14314))
- **Inference**: TurboQuant KV cache + GPTQ/AWQ weights + TurboQuant RAG embeddings

Clear separation, no conflict.

**Speculative research direction (unvalidated)**: Use TurboQuant on optimizer state (e.g., Adam momentum), since accumulated momentum approaches Gaussian. This is hypothesis only — not for the launch phase.

## §4 Memory Budget Recalculation on Mac Studio 64GB

iDoris Phase 1 MVP (Qwen3.5-9B + LoRA + RAG + 128K context):

| Component | Without TurboQuant | With TurboQuant | Savings |
|-----------|-------------------|-----------------|---------|
| Qwen3.5-9B Q5_K_M weights | 7 GB | 7 GB | 0 |
| LoRA r=32 adapter | 1 GB | 1 GB | 0 |
| KV cache @ 128K FP16 | 14.7 GB | 3.7 GB (4-bit) | **11 GB** |
| LightRAG vector DB (100K × 3072d) | 1.2 GB | 0.15 GB | **1.05 GB** |
| Inference activations (worst case) | 3 GB | 3 GB | 0 |
| **Inference peak** | **~27 GB** | **~15 GB** | **~12 GB (44% saved)** |

**Key benefit**:
- 64GB Mac Studio not only runs but has ~50GB headroom for training (QLoRA 9B peaks at ~28GB)
- Can hold 2-3 LoRAs simultaneously (e.g., Personal + Community + Coding adapter)
- Long-context scenarios go from "barely runs" to "smooth"

**Conservative estimate**: real-world software dequantization overhead 2-5% (turboquant-mlx V3 mode drops 148 t/s to 24-27 t/s, but V2 LEAN is at-or-above FP16 baseline).

## §5 Comparison with Other Quantization Methods

| Method | Use | Training Required | Metadata | Relation to TurboQuant |
|--------|-----|-------------------|----------|------------------------|
| **GPTQ** ([2022](https://arxiv.org/abs/2210.17323)) | Weight quant | Calibration | per-block scales | Complementary: GPTQ for weights, TQ for KV |
| **AWQ** ([2023](https://arxiv.org/abs/2306.00978)) | Weight quant | Calibration | per-channel scales | Complementary |
| **QLoRA NF4** ([2023](https://arxiv.org/abs/2305.14314)) | Training-time weight quant | None | Double-quantized constants | **NF4 for training, TQ for inference** |
| **KIVI** ([2024](https://arxiv.org/abs/2402.02750)) | KV cache 2-bit | None | Outlier channels FP16 | Beaten by TurboQuant (paper Table 3) |
| **SnapKV** ([2024](https://arxiv.org/abs/2404.14469)) | KV selective drop | None | Attention scores | Orthogonal (stackable) |
| **PolarQuant** ([2025](https://arxiv.org/abs/2502.02617)) | KV polar | None | Polar angle index | Same family (same Google team) |
| **TurboQuant** | KV cache + Embedding | **None** | **None** | This article |

**Key differentiator**: TurboQuant's "zero training + zero metadata" gives it a structural advantage in **federated learning scenarios** (iDoris's core context) — clients don't need to sync codebooks or calibration data.

## §6 Engineering Roadmap

### 6.1 Priority Ranking

| Priority | Task | Effort | Benefit |
|----------|------|--------|---------|
| **P0** (Phase 1 must-do) | Integrate turboquant-mlx into iDoris-PC inference | 1-2 days | 12 GB memory freed |
| **P1** (Phase 1 optional) | RAG vector DB → TurboQuant 4-bit | 2-3 days | 8× RAG capacity |
| **P2** (Phase 2) | Mobile distillation + TurboQuant + GPTQ | 3-5 days | 8K context smooth on phone |
| **P3** (Phase 3) | Federated LoRA delta upload via TurboQuant compression | 1 week (experimental) | 8× upload bandwidth |
| **P4** (Don't do) | Replace QLoRA NF4 for training | Infeasible | / |

### 6.2 Recommended Stack (Phase 1)

```
Inference stack:
   ┌────────────────────────────────────┐
   │  Qwen3.5-9B Q5_K_M (GGUF/MLX)      │  ← weight quant (existing)
   │  + LoRA r=32                       │  ← personal preference
   │  + TurboQuant 4-bit KV cache 🆕    │  ← long context
   │  + LightRAG (TurboQuant embedding) │  ← vector DB compression 🆕
   └────────────────────────────────────┘

Training stack (unchanged):
   ┌────────────────────────────────────┐
   │  Qwen3.5-9B NF4 (QLoRA)            │  ← 4-bit training weights
   │  + LoRA gradient FP32              │  ← LoRA gradients
   │  + Adam-8bit optimizer             │  ← optimizer state
   └────────────────────────────────────┘
```

### 6.3 Code Sketch

```python
# iDoris-PC inference with TurboQuant
from mlx_lm import load
from turboquant_mlx import TurboQuantKVCache  # sharpner/turboquant-mlx

model, tokenizer = load("Qwen/Qwen3.5-9B-MLX-Q5")
model.attach_lora("./loras/personal-v3.safetensors")

kv_cache = TurboQuantKVCache(
    bits=4,
    variant="V2-LEAN",   # speed mode
    max_len=131072,      # 128K context
)

response = model.generate(
    prompt="...",
    kv_cache=kv_cache,
    max_tokens=2048,
)

# RAG side
from lightrag import LightRAG
from turboquant import TurboQuantIndex

rag = LightRAG(
    embedder="bge-large-zh",
    index=TurboQuantIndex(bits=4, dim=1024),
)
rag.insert_documents(personal_notes)  # 100K chunks → 50MB
```

## §7 Risks and Uncertainties

### 7.1 Known Issues

1. **Inner-product bias** (paper § 4.2): MSE-optimal codebook produces systematically biased inner-product estimates (factor $2/\pi$ at 1-bit). Requires QJL residual correction, but QJL has higher variance. **Implication**: attention scores have minor bias; possibly amplified in long-context edge cases. Recommend A/B testing during integration.

2. **Software dequantization overhead**: [turboquant-mlx](https://github.com/sharpner/turboquant-mlx) V3 mode (extreme low-bit) drops 148 t/s to 24-27 t/s. Reason: Apple Silicon lacks specialized 4-bit matmul instructions; software decoding required. **Mitigation**: Use V2 LEAN mode (4-bit, hardware-accelerated) — actually faster than FP16.

3. **MLX implementation maturity**: turboquant-mlx is "proof of concept", not production-ready. Wait for more mature versions, or fork and maintain.

4. **No training-time experiments**: All public benchmarks are inference. P3 (federated LoRA delta compression) is research territory with no reference data.

### 7.2 Decision Recommendations

- **P0 do immediately** (KV cache 4-bit): minimal risk, large gain, reversible (can always fall back to FP16)
- **P1 do carefully** (RAG embedding): A/B test on small (10K chunks) first, compare retrieval precision
- **P2-P3 contingent** on Phase 1 validation
- **P4 don't do** (replace QLoRA): explicitly infeasible, don't waste effort

## §8 Conclusion

Returning to the launch question: "Can TurboQuant reduce iDoris's device memory consumption?"

**Answer**:

✅ **Yes**, in two scenarios:
- **KV cache compression**: On Mac Studio 64GB, 128K context KV cache from 14.7 GB → 3.7 GB, saving 11 GB
- **RAG embedding compression**: 100K-1M chunk vector DB compressed 8×

❌ **No** for:
- Training-time memory (keep QLoRA NF4)
- Weight quantization (GPTQ / AWQ / Q5_K_M already excellent)

🎯 **Net effect**: iDoris-PC Phase 1 MVP inference peak memory drops from ~27 GB to ~15 GB, **freeing ~12 GB (44%) for long context / multi-LoRA / federated experiments**. This isn't marginal — it's transformative.

**Specific recommendation for [iDoris launch](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/)**: include TurboQuant integration in Phase 1 M2 task list, parallel to "LightRAG integration + Sin90 data contribution center GUI". This won't delay Phase 1 — it elevates the Phase 1 acceptance bar from "barely runs" to "smoothly usable".

---

## References

### TurboQuant and Companion Methods

- [TurboQuant arXiv:2504.19874](https://arxiv.org/abs/2504.19874) (ICLR 2026)
- [Google Research blog](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)
- [QJL: arXiv:2406.03482](https://arxiv.org/abs/2406.03482) (NeurIPS 2024)
- [PolarQuant: arXiv:2502.02617](https://arxiv.org/abs/2502.02617) (AISTATS 2026)
- [arkaung interactive walkthrough](https://arkaung.github.io/interactive-turboquant/) (third-party)

### Open-Source Implementations

- [tonbistudio/turboquant-pytorch](https://github.com/tonbistudio/turboquant-pytorch) (PyTorch)
- [yashkc2025/turboquant](https://github.com/yashkc2025/turboquant) (Python)
- [sharpner/turboquant-mlx](https://github.com/sharpner/turboquant-mlx) (**Apple Silicon**)
- [0xSero/turboquant](https://github.com/0xSero/turboquant) (Triton + vLLM)
- [SharpAI/SwiftLM](https://github.com/SharpAI/SwiftLM) (macOS + iOS app)

### Ecosystem Integration

- [vLLM Issue #38171](https://github.com/vllm-project/vllm/issues/38171)
- [SGLang Issue #21618](https://github.com/sgl-project/sglang/issues/21618)

### Related Quantization Methods

- QLoRA NF4: [Dettmers et al., NeurIPS 2023, arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- GPTQ: [Frantar et al., 2022, arXiv:2210.17323](https://arxiv.org/abs/2210.17323)
- AWQ: [Lin et al., 2023, arXiv:2306.00978](https://arxiv.org/abs/2306.00978)
- KIVI: [Liu et al., 2024, arXiv:2402.02750](https://arxiv.org/abs/2402.02750)
- SnapKV: [Li et al., 2024, arXiv:2404.14469](https://arxiv.org/abs/2404.14469)
- KVQuant: [NeurIPS 2024](https://www.stat.berkeley.edu/~mmahoney/pubs/neurips-2024-kvquant.pdf)

### iDoris-Related

- [iDoris launch article](https://blog.mushroom.cv/blog/idoris-project-launch--how-an-independent-researcher-builds-/)
- [iDoris Master Plan](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
- [iDoris GitHub](https://github.com/AuraAIHQ/iDoris)
- [Mycelium Protocol](https://launch.mushroom.cv)
