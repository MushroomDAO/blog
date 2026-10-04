---
title: "OLMo-core 3：AI2 的「全透明」训练栈给工程师看的工程指南"
titleEn: "OLMo-core 3: An Engineer's Guide to AI2's Fully Transparent Training Stack"
description: "allenai/OLMo-core，Apache-2.0，1,663 stars，Python。AI2 于 2026 年 10 月 1 日发布 v3.0.0，面向大规模 MoE 模型的完全透明训练栈——不只是开放权重，而是把语料溯源（Dolma，含 URL/时间戳/去重指纹/困惑度阈值）、训练脚本、所有超参、架构代码一并公开。小组织不需要复现 32B 规模，实际价值在于：用 Dolma 方法论审计自己的数据集、用官方脚本作为分布式训练参考架构、用 OLMo-3 权重做垂直领域微调。这是一台科学仪器，不是商业产品。"
descriptionEn: "allenai/OLMo-core, Apache-2.0, 1,663 stars, Python. AI2 released v3.0.0 on October 1, 2026 — a fully transparent training stack for large-scale MoE models. Not just open weights: Dolma corpus with URL provenance, crawl timestamps, MinHash-LSH dedup fingerprints, and perplexity thresholds are all public, along with every training script and hyperparameter. Small organizations don't need to replicate 32B-scale training — the real value is in using Dolma's methodology to audit your own datasets, treating official training scripts as reference architecture for distributed training, and fine-tuning OLMo-3 weights on domain-specific data."
pubDate: 2026-10-04
heroImage: "../../assets/images/olmo-core-3-ai2-transparent-training-stack-moe-banner.jpg"
category: "Research"
tags: ["大模型训练", "开源", "AI2", "MoE", "数据工程", "分布式训练", "Apache-2.0"]
lang: "zh-CN"
wechatTitle: "OLMo-core 3：最透明的大模型训练栈"
wechatDigest: "AI2 Apache-2.0；完全透明训练栈；Dolma溯源语料；MoE专家并行；小组织借鉴指南"
---

大模型的「开源」通常是这样的：权重发布，技术报告写架构，真正的训练数据、超参数、数据处理流水线不公开——或者公开一部分，但不足以复现。

AI2 的 OLMo 系列从一开始走的就是另一条路。2026 年 10 月 1 日，他们发布 OLMo-core v3.0.0，把这条路推得更远：面向大规模 MoE 模型的完全透明训练栈，训练数据有完整溯源，脚本、超参、架构代码全部开放。

GitHub: https://github.com/allenai/OLMo-core | ⭐ 1,663 | Apache-2.0 | Python

---

## 两种「开放」

区分两种常见的「开放」有助于理解 OLMo 在做什么：

**权重开放**（多数大模型）：你可以下载模型、做推理、微调，但不知道它是怎么训练出来的——数据来自哪里、怎么过滤、超参数是什么、训练过程出过什么问题。

**训练栈开放**（OLMo）：不只是权重，而是整个流水线可审计：
- **语料溯源**：Dolma 数据集的每条记录有来源 URL、爬取时间戳、去重指纹（MinHash-LSH），质量过滤器（困惑度阈值）按数据族（Common Crawl / 学术论文 / 代码）分别设置，标准可查可复现。
- **训练脚本全公开**：`src/scripts/official/` 下有每个官方模型的完整训练脚本，可以 `torchrun` 直接跑。
- **超参公开**：学习率、批大小、预热步数、衰减策略——没有「见技术报告」，就是脚本里的代码。
- **架构代码可读**：标准 decoder-only Transformer + SwiGLU，FSDP 分布式训练，没有专有内核。

社区的评价准确：意义不在单一基准数字，而在证明「完全透明的竞争性规模训练是可行的」——研究者可以审计模型为何如此表现，而不只是相信架构声明。这更像一台科学仪器。

---

## v3.0.0 工程更新：MoE 支持成熟化

v3.0.0 的核心更新是大规模 MoE 训练能力的成熟，同时修了几个容易静默失败的 bug。

### MoE 专家并行训练栈

v3.0.0 新增了完整的 MoE 训练支持：
- **OLMoDDP**：针对 MoE 的分布式数据并行，含 fused 前向/反向和 BF16 权重梯度累积
- **EMO routing**：文档池路由 + 全局负载均衡，EOS token 归属到前一文档（匹配注意力文档边界）
- **Hybrid MoE HF export**：含 KDA（Key-Dimension Attention）、latent experts、per-head 归一化，有张量精确往返验证

依赖：`grouped_gemm`（dropless MoE 必需，目前可能需要从源码编译）、`QuACK`（CuTe 内核）。

### 文档边界 bug 修复（重要）

这个修复是 v3.0.0 最值得关注的工程细节之一。

旧行为：数据集打包时通过扫描 EOS token 推断文档边界。问题：如果生产端截断文档并丢弃了尾部 EOS，被截断的文档会和后面那个文档合并，`LongDocStrategy.truncate` 只保留合并跨度的头部，后面的文档永远到不了训练。

实测：97.98% 的 token 通过旧的推断路径正常传递，100.00% 通过元数据文件路径。差值不大但是静默的——没有报错，只是有不到 3% 的 token 对应的文档训练到一半就消失了。

新增 `use_array_if_local=False` 可以强制从元数据文件读取文档边界，完全避免这个问题。

### FusedAttention 换代

`FusedAttention` 全量替换为 `FusedAttentionV2`，旧配置（`AttentionConfig(name="fused")`）向后兼容、参数名和形状不变，checkpoint 可以直接加载。注意：fused RoPE 映射到 regular RoPE，低精度 RoPE 梯度数值有差异，resume 训练不是数值完全等价的。

最低 PyTorch 版本提升到 2.10.0。

---

## 对小组织的工程价值

不需要 H100 集群才能从 OLMo-core 3 拿到价值。对应不同资源规模，有几个实际可落地的用法。

### 一、用 Dolma 方法论审计自己的数据集

很多小组织有自己的训练数据集，但缺乏系统的质量评估方法。Dolma 的开放处理流水线是一个很好的参考框架：

- **去重指纹**：MinHash-LSH，参数选择和实现都在 Dolma 仓库（github.com/allenai/dolma），可以直接用在自己的数据集上
- **困惑度过滤**：按数据族（通用爬取 / 代码 / 学术）设置不同阈值，而不是一刀切——这个分族逻辑比直接用困惑度过滤效果好
- **溯源记录**：如果你在积累私有语料，参考 Dolma 的元数据 schema 设计来源 URL + 时间戳字段，未来审计和版权追溯会省很多力气

这部分不需要任何 GPU，数据工程可以在普通机器上跑。

### 二、用官方训练脚本作为分布式训练参考架构

`src/scripts/official/` 下有 OLMo-2 32B 和 OLMo-3 7B/32B 的完整训练脚本。即使你训练的模型小得多，这些脚本是学习 FSDP 分布式训练配置的极好参考：

```bash
# 查看 OLMo-3 7B 训练脚本结构
# src/scripts/official/OLMo3/

# 小规模实验：把 GPU 数改小，学习配置方式
torchrun --nproc-per-node=2 src/scripts/official/OLMo3/OLMo-3-7B-train.py \
  --save-folder=/path/to/checkpoints
```

超参可以从命令行覆盖，不需要改脚本本身：

```bash
# 覆盖学习率
torchrun --nproc-per-node=8 src/scripts/official/OLMo3/OLMo-3-7B-train.py \
  --save-folder=/path/to/checkpoints \
  --train_module.optim.lr=3e-4
```

这个接口设计对实验管理很有用：不同超参对应不同命令行，容易和实验追踪工具集成。

### 三、用 OLMo-3 权重做垂直领域微调

OLMo-3 7B 和 32B 权重通过 HuggingFace 提供，Apache-2.0，商业可用：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载 OLMo-3 7B
model = AutoModelForCausalLM.from_pretrained("allenai/Olmo-3-1125-7B")
tokenizer = AutoTokenizer.from_pretrained("allenai/Olmo-3-1125-7B")
```

vLLM 支持 OLMo-3（需 vLLM >= 0.11.0），可以直接上推理服务。

用 OLMo-3 作为微调基座的优势：训练数据来源全部已知，可以验证微调数据和预训练数据的分布关系，不用猜测基座模型见过什么。对于需要版权审计的商业场景，这一点很有价值。

### 四、用 olmo_core 库做模型实验

`ai2-olmo-core` 是 PyPI 包，可以直接安装：

```bash
pip install ai2-olmo-core
# 或含全部可选依赖
pip install -e .[all]  # 从源码安装
```

库的组件化设计允许你替换单个模块：换注意力机制（flash-attn / ring-flash-attn / TransformerEngine）、换 loss（Liger-Kernel 的 fused-linear 版，降内存）、换量化精度（torchao 的 float8）——不需要全部一起用。

对于只想做注意力机制实验的研究者，单独换 attention backend 而保持其他配置不变，是一个很干净的消融对比设置。

---

## 局限与适用边界

**训练资源门槛**：v3.0.0 更新的 Docker 镜像针对 H100 集群（PyTorch 2.10/2.11 + CUDA 12.8/13.0），完整规模训练不是桌面项目。可选依赖（flash-attn、grouped_gemm）有时需要从源码编译，有一定环境配置成本。

**MoE 依赖尚未稳定**：`grouped_gemm` 0.1.6 之后的版本 OLMo-core 需要的 PR #21 截至 v3.0.0 还没合并，可能需要从源码安装。Blackwell（SM90a）的 CuTe 内核需要 CUDA 13。

**模型规模的下限**：OLMo-core 的设计中心是规模化训练，没有专门面向「4B 以下实验性模型」的轻量配置。小规模实验可以跑，但会带着 FSDP 的全套配置开销。

---

## 一句话定位

OLMo-core 3 = 「完全可审计的大规模 MoE 训练栈，唯一你能在论文里引用数据来源的开源大模型训练体系」。

对小组织：不是来直接跑的，是来学的——学数据工程方法论、学 FSDP 配置范式、用它的权重做垂直领域微调。你拿到的不只是一个模型，是一套可以审计「模型为什么这样」的工具链。

---

> Apache-2.0 开源，商业使用无限制。开源仅供学习参考，训练数据和模型权重请分别核实对应许可证。

---

<!--EN-->

## OLMo-core 3: An Engineer's Guide to AI2's Fully Transparent Training Stack

Most "open" LLMs release weights and a tech report. The actual training data, filtering criteria, hyperparameters, and the decisions made during training stay private — or are documented just enough to look open.

AI2's OLMo line has always taken a different path. On October 1, 2026, they released OLMo-core v3.0.0: a fully transparent training stack for large-scale MoE models. Not just weights — the entire pipeline is auditable.

GitHub: https://github.com/allenai/OLMo-core | ⭐ 1,663 | Apache-2.0 | Python

---

### Two Kinds of "Open"

**Weight-open** (most large models): you can download, run, and fine-tune the model, but you don't know how it was trained — where the data came from, how it was filtered, what hyperparameters were used, what failed along the way.

**Training-stack-open** (OLMo): the entire pipeline is auditable:
- **Corpus provenance**: every Dolma record has a source URL, crawl timestamp, deduplication fingerprint (MinHash-LSH), and quality filter thresholds (perplexity cutoffs set per data family: Common Crawl / academic papers / code). The criteria are public and reproducible.
- **Training scripts**: `src/scripts/official/` has complete training scripts for every released model, runnable with `torchrun`.
- **Hyperparameters**: learning rate, batch size, warmup schedule, decay — no "see technical report," it's all in the script.
- **Architecture**: standard decoder-only Transformer + SwiGLU, FSDP distributed training, no proprietary kernels.

The significance isn't any single benchmark number. It's that fully transparent competitive-scale training is viable — and that researchers can audit why a model behaves the way it does, rather than trusting architecture claims. This is a scientific instrument, not a product.

---

### v3.0.0 Engineering Updates

The headline change in v3.0.0 is mature MoE training support, plus fixes for a few silently-failing edge cases.

**MoE expert-parallel training stack (OLMoDDP)**: fused forward/backward for MoE experts, BF16 weight-gradient accumulation, EMO (document-pool routing + global load balancing), full HuggingFace export with tensor round-trip validation. Requires `grouped_gemm` (may need source build until PR #21 merges past v0.1.6).

**Document boundary bug fix**: the previous behavior inferred document boundaries by scanning packed token arrays for EOS tokens. If a document was truncated by the producer and the trailing EOS was dropped, it merged with the following document — `LongDocStrategy.truncate` kept only the head of the merged span, silently losing the following document from training entirely. Measured on an SFT cache: 97.98% of tokens reached instances via the inferred path vs. 100.00% via the metadata file. New `use_array_if_local=False` forces reading boundaries from the metadata file, eliminating the hazard.

**FusedAttentionV2**: replaces `FusedAttention`, backward-compatible on parameter names and shapes (checkpoint-loadable). Note: fused RoPE maps to regular RoPE — low-precision RoPE gradients differ numerically, so resumed training is not bit-identical to pre-upgrade runs.

**Minimum PyTorch**: raised to 2.10.0.

---

### Engineering Value for Small Organizations

You don't need an H100 cluster to extract value from OLMo-core 3.

**Audit your own dataset with Dolma's methodology.** Dolma's dedup pipeline (MinHash-LSH) and per-family perplexity filtering are available as standalone tools at github.com/allenai/dolma. Applying the same methodology to your private corpus — even a small one — surfaces near-duplicates and low-quality entries that a simple perplexity filter misses. The metadata schema (source URL + timestamp per record) is worth adopting now if you're building a corpus you'll need to audit later.

**Use official training scripts as FSDP reference architecture.** Even if your model is much smaller than 7B, the scripts in `src/scripts/official/OLMo3/` show how to wire FSDP configuration, set optimizer hyperparameters, and override from the command line cleanly. The command-line override pattern (`--train_module.optim.lr=3e-4`) integrates naturally with experiment tracking tools.

**Fine-tune OLMo-3 weights on vertical domains.** OLMo-3 7B and 32B are available on HuggingFace under Apache-2.0, compatible with the standard transformers and vLLM (>=0.11.0) stacks. The provenance advantage: you know exactly what data the base model saw, which means you can reason about distribution overlap with your fine-tuning data — not guess.

**Use the `ai2-olmo-core` library for module-level experiments.** The library lets you swap individual components: attention backends (flash-attn, ring-flash-attn, TransformerEngine), loss implementations (Liger-Kernel fused-linear for lower memory), quantization precision (torchao float8). If you want a clean ablation comparing attention mechanisms, OLMo-core's modular design makes that possible without rewriting the rest of the training loop.

---

### Constraints

Full-scale training targets H100 clusters (Docker images require PyTorch 2.10+ / CUDA 12.8+). Some optional dependencies need source builds. The library is designed for scale — there's no lightweight configuration for sub-4B experimental runs. MoE-specific deps (`grouped_gemm`, `QuACK`) have version constraints that may require manual resolution.

---

### One-Line Position

OLMo-core 3 = "the only fully auditable large-scale MoE training stack where you can cite the data sources in a paper."

For small organizations: you're not here to run it at full scale — you're here to learn from it. Data engineering methodology, FSDP configuration patterns, a fine-tunable base whose training lineage is publicly documented. What you're getting isn't just a model; it's a toolchain for understanding why the model behaves the way it does.

---

> Apache-2.0, no commercial restrictions. Corpus data and model weights are governed by separate licenses — verify each independently. For technical reference only.
