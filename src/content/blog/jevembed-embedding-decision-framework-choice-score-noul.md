---
title: "JevEmbed：用 Embedding 做决策——Choice / Score / Noul 三合一框架，支持 LoRA 微调"
titleEn: "JevEmbed: Embedding-Based Decisions — Choice, Score, and Noul in One Framework with LoRA Fine-tuning"
description: "JevEmbed，HITsz-TMG 出品，Python。用 Embedding 模型做三类决策：Choice（选择）、Score（评分）、Noul（判断），同一套框架，兼容 KaLM、Qwen3-Embedding、E5 等模型。支持超 255 个候选项，提供 Python API + CLI + HTTP 服务。支持 LoRA 微调：KaLM 微调后准确率 30%→77%，Qwen3-0.6B 微调后 31%→84%。独立实现，非 TypeSafe AI 官方，兼容 Jev-style 请求格式。"
descriptionEn: "JevEmbed by HITsz-TMG — Python framework for embedding-based Choice, Score, and Noul decisions. Single framework compatible with KaLM, Qwen3-Embedding, E5 models. Supports >255 candidates. Python API + CLI + HTTP service. LoRA fine-tuning: KaLM accuracy 30%→77%, Qwen3-0.6B 31%→84%. Independent implementation, not affiliated with TypeSafe AI, uses Jev-style request schemas."
pubDate: 2026-09-24
heroImage: "../../assets/images/jevembed-embedding-decision-framework-choice-score-noul-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "embedding", "decision-making", "jev", "lora", "python", "local-ai", "kalm", "qwen"]
lang: zh-CN
---

`HITsz-TMG/JevEmbed`，Python，哈尔滨工业大学（深圳）出品。用 Embedding 模型做决策的框架：Choice（多选一）、Score（评分）、Noul（判断），同一套框架，同一套接口，换模型只需改配置文件。

**GitHub**：github.com/HITsz-TMG/JevEmbed | **语言**：Python 3.10–3.12 | **独立实现，非 TypeSafe AI 官方**

---

## 核心思路：Embedding 也能做决策

Embedding 模型原本的定位是：把文本转成向量，用来做语义搜索或相似度计算。JevEmbed 的思路是：把决策问题的各个候选选项也编码成向量，通过余弦相似度打分来完成选择——不需要 LLM 的自回归解码，不需要输出 token，直接在 Prefill 阶段用 logit 对应的相似度拿到结果。

三种决策类型：

| 类型 | 用途 | 举例 |
|------|-----|------|
| **Choice** | 从候选项中选一个 | 客服请求路由：退款/换货/投诉/咨询 |
| **Score** | 按自定义等级评分 | Bug 严重程度：P0/P1/P2/P3 |
| **Noul** | 判断问题是否成立 | 「用户是否在升级流程中」返回 0–1 概率 |

---

## 支持的模型

| JevEmbed ID | 权重来源 | 向量维度 | Token 上限 |
|-------------|---------|---------|-----------|
| `kalm-embedding-v2.5` | KaLM-Embedding/KaLM-embedding-multilingual-mini-instruct-v2.5 | 896 | 32768 |
| `qwen3-embedding-0.6b` | Qwen/Qwen3-Embedding-0.6B | 1024 | 32768 |
| `qwen3-embedding-4b` | Qwen/Qwen3-Embedding-4B | 2560 | 32768 |
| `qwen3-embedding-8b` | Qwen/Qwen3-Embedding-8B | 4096 | 32768 |
| `multilingual-e5-large-instruct` | intfloat/multilingual-e5-large-instruct | 1024 | 512 |

模型权重从 HuggingFace 首次推理时自动下载。KaLM 需要 `trust_remote_code: true`（加载其自定义 Python 实现）；Qwen3 和 E5 不需要。

---

## 安装

```bash
git clone https://github.com/HITsz-TMG/JevEmbed
cd JevEmbed
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

测试过的依赖版本：PyTorch 2.8.0 + Transformers 4.51.0 + sentence-transformers 5.3.0。CPU 推理支持，不需要 FlashAttention。

最小化安装（只要核心，不含 HTTP 服务）：

```bash
python -m pip install -e .
```

---

## 快速上手

**先验证输入（不加载权重，纯检查）：**

```bash
python -m jevembed --config configs/kalm-embedding-v2.5.yaml \
  --input examples/official_choice_exchange.json --explain
```

**跑推理输出标准 JSON 响应：**

```bash
python -m jevembed --config configs/kalm-embedding-v2.5.yaml \
  --input examples/official_choice_exchange.json
```

**保存响应 + 诊断 trace：**

```bash
mkdir -p artifacts
python -m jevembed --config configs/kalm-embedding-v2.5.yaml \
  --input examples/official_noul_escalation.json \
  --trace --output artifacts/noul-trace.json
```

从 stdin 读取 JSON：`--input -`，输出到 stdout，管道友好。

---

## 请求格式（Jev-style JSON）

Choice 请求示例：

```json
{
  "model": "kalm-embedding-v2.5",
  "state": "用户说：我想换一个尺寸更大的商品",
  "question": {
    "type": "choice",
    "query": "这个请求属于哪个类别？",
    "choices": ["退款", "换货", "投诉", "商品咨询"]
  }
}
```

响应格式兼容 Jev /v1/systemone 规范。

---

## 超 255 候选项支持

这是实用性很高的改进。原本的 Jev 格式 Choice 有候选项数量限制（约 255 个）。JevEmbed 去掉了这个上限，分类标签多、路由场景复杂的任务（几十到几百个候选类别）可以直接用同一套框架处理，不需要分层级或分段处理。

---

## HTTP 服务

```bash
python -m jevembed.server \
  --config configs/kalm-embedding-v2.5.yaml \
  --host 0.0.0.0 --port 8000
```

暴露 `/v1/embeddings` 和 `/v1/systemone` 兼容接口，可以接入任何 Jev-style 的客户端。

---

## LoRA 微调：训练自己的决策模型

JevEmbed 支持 LoRA 微调，只训练 adapter，基础模型权重不动：

```bash
python scripts/finetune.py \
  --model qwen3-embedding-0.6b \
  --data your_task_data.json \
  --output lora_adapter/
```

训练完后本地加载：

```bash
python -m jevembed \
  --config configs/qwen3-embedding-0.6b.yaml \
  --lora lora_adapter/ \
  --input task_input.json
```

**实测数据（Open-Jev release-v2-redistributable 子集）：**

| 模型 | 微调前准确率 | 微调后准确率 |
|------|------------|------------|
| KaLM-Embedding-V2.5 | 30.24% | 76.68% |
| Qwen3-Embedding-0.6B | 30.73% | 84.06% |

训练集 79,116 条，验证集 3,495 道有明确答案的问题。这些是该子集的验证结果，其他任务需要单独评估，不能直接迁移。

---

## 与同类工具对比

| 工具 | 机制 | 候选项上限 | 本地运行 | 微调支持 |
|------|-----|-----------|---------|---------|
| **JevEmbed** | Embedding 余弦相似度 | 无上限 | ✅ CPU/CUDA | ✅ LoRA |
| SemIf | logit 读取（LLM） | 有限 | ✅ 多后端 | ❌ |
| KaLM-Jev | logit 读取（LLM） | 有限 | ✅ CPU | ❌ |
| TypeSafe Jev | 闭源 API | - | ❌ | - |

JevEmbed 走的是 Embedding 路，而不是 LLM logit 路。资源需求低很多：KaLM-Embedding-V2.5 只有 0.3B 参数，CPU 上也跑得动。

---

## 局限性

**1. 准确率有上界**：Embedding 模型的理解能力有限，复杂语义推理不如 LLM logit 方案。微调可以大幅提升，但需要任务数据。

**2. 微调数据依赖**：LoRA 效果取决于训练数据质量。如果没有标注数据，需要先构建数据集。

**3. 候选项长度限制**：每个候选项仍受模型 token 上限约束（KaLM 32768 token，E5-large 512 token）——是候选项文本本身不能太长，而不是候选项数量的限制。

**4. 独立实现非官方**：和 TypeSafe AI 不存在授权或合作关系，格式兼容但不保证随 Jev 规范更新而同步。

**5. 单 GPU 推理**：当前不支持多 GPU 并行推理，超大候选集场景下 Qwen3-Embedding-8B（~8B 参数）在 CPU 上会很慢。

---

## 怎么看这个项目

Embedding 做决策是一条比 LLM logit 方案成本更低的路：模型更小，无需 GPU，延迟更低，在候选项相对固定的路由/分类场景里是合理的工程选择。JevEmbed 把这套方法打包成开箱即用的框架，顺手打通了 LoRA 微调管道，让领域适配不只是调参数，而是真正拟合任务数据。

KaLM 微调后 30%→77%、Qwen3-0.6B 31%→84% 这两组数字是在特定子集上的结果，不能直接当通用 benchmark 解读，但至少说明微调路径本身是通的，效果改进幅度是真实的。

对于有大量路由/分类/判断类决策需求、又不想依赖云 API 的场景，值得评估。

> 开源仅供学习研究参考。

---

<!--EN-->

## JevEmbed: Embedding-Based Choice, Score, and Noul Decisions

`HITsz-TMG/JevEmbed` (Python, Harbin Institute of Technology Shenzhen) is an embedding-based decision framework. Three decision types — Choice, Score, Noul — all use the same Python API/CLI/HTTP server, with pluggable embedding models.

**GitHub**: github.com/HITsz-TMG/JevEmbed | **Note**: Independent implementation, not affiliated with TypeSafe AI

---

### Three Decision Types

| Type | What It Does | Example |
|------|-------------|---------|
| **Choice** | Pick one from candidates | Customer service routing: refund/exchange/complaint/inquiry |
| **Score** | Assign a level rating | Bug severity: P0/P1/P2/P3 |
| **Noul** | Yes/no probability (0–1) | "Is the user in the upgrade flow?" |

---

### Supported Models

| JevEmbed ID | Source | Dimensions |
|-------------|--------|-----------|
| `kalm-embedding-v2.5` | KaLM-Embedding v2.5 | 896 |
| `qwen3-embedding-0.6b` | Qwen/Qwen3-Embedding-0.6B | 1024 |
| `qwen3-embedding-4b` | Qwen/Qwen3-Embedding-4B | 2560 |
| `qwen3-embedding-8b` | Qwen/Qwen3-Embedding-8B | 4096 |
| `multilingual-e5-large-instruct` | intfloat/multilingual-e5-large | 1024 |

CPU inference supported; no FlashAttention required. Weights auto-downloaded from HuggingFace on first run.

---

### Installation

```bash
git clone https://github.com/HITsz-TMG/JevEmbed && cd JevEmbed
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

---

### Key Feature: >255 Candidates

The original Jev Choice format had a ~255 candidate cap. JevEmbed removes this limit — classification tasks with hundreds of candidate labels work natively.

---

### LoRA Fine-tuning Results

Trained on Open-Jev release-v2-redistributable subset (79,116 samples), evaluated on 3,495 validation questions:

| Model | Before | After |
|-------|--------|-------|
| KaLM-Embedding-V2.5 | 30.24% | 76.68% |
| Qwen3-Embedding-0.6B | 30.73% | 84.06% |

These are subset-specific results; other task domains need independent evaluation.

---

### Limitations

1. **Accuracy ceiling**: Embedding models have limited semantic reasoning compared to LLM logit approaches; fine-tuning helps but requires labeled data
2. **Fine-tuning requires task data**: Results depend heavily on the quality and coverage of your training set
3. **Candidate text length still bounded**: Candidate count is unlimited, but each candidate's text still has token-limit constraints (E5-large: 512 tokens)
4. **Independent implementation**: Format-compatible with Jev but not guaranteed to stay synchronized with TypeSafe AI spec updates
5. **No multi-GPU**: Large candidates × Qwen3-8B on CPU will be slow

---

### Assessment

Embedding-based decisions are a lower-cost alternative to LLM-logit approaches for routing and classification: smaller models, CPU-friendly, lower latency for fixed-category scenarios. JevEmbed packages this into a clean framework with a LoRA fine-tuning pipeline, making domain adaptation practical. The 30%→77–84% fine-tuning gains are subset-specific but confirm the adaptation path works.

> For learning and research reference only.
