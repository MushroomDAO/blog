---
title: "KaLM-Jev 本地部署指南：从安装到对接业务流程，附硬件选型与再训练说明"
titleEn: "KaLM-Jev Local Deployment Guide: Installation, Hardware Selection, Business Integration, and Fine-Tuning"
description: "KaLM-Jev，32 stars，2026-09-21 刚开源。基于 KaLM-Reranker-V1 的本地 Jev 风格判断引擎，Nano/Small/Large 三档模型，/v1/systemone 接口兼容 TypeSafe AI Jev。本文覆盖：硬件要求、本地安装、REST API 对接业务流程、数据初始化、是否需要再训练及如何做。"
descriptionEn: "KaLM-Jev — 32 stars, open-sourced 2026-09-21. A local Jev-style judgment engine built on KaLM-Reranker-V1 (Nano/Small/Large). /v1/systemone endpoint compatible with TypeSafe AI Jev. Covers: hardware requirements, local installation, REST API business integration, data initialization, and fine-tuning guidance."
pubDate: 2026-09-22
heroImage: "../../assets/images/kalm-jev-local-judgment-engine-hardware-deploy-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "local-ai", "jev", "embedding", "reranker", "judgment-engine", "deployment", "python"]
lang: zh-CN
---

`KaLM-Embedding/KaLM-Jev` 在 2026-09-21 刚刚开源，32 stars。它做的事很具体：把 KaLM 系列重排序模型变成一个本地 Jev 风格的判断引擎，暴露和 TypeSafe AI Jev System One 相同的 `/v1/systemone` 接口，输出结构化决策而非自由文本。

**GitHub**：github.com/KaLM-Embedding/KaLM-Jev | **Stars**：32 | **License**：未明确声明 | **语言**：Python

---

## 什么是 Jev 风格判断引擎

在理解部署细节之前，先明确 KaLM-Jev 的定位。

传统 LLM 调用会生成一段文字，你再从文字里解析出答案。Jev 范式反过来：把问题分解成结构化候选，模型只输出各候选的概率分布，不生成任何文字。这类模型速度极快、输出确定，特别适合需要大量判断的业务场景（分类路由、质量评分、条件过滤）。

KaLM-Jev 的基础是 **KaLM-Reranker-V1**，HIT-TMG Lab（哈工大信息检索与机器翻译实验室）训练的编码器-解码器重排序模型，arXiv 论文 2606.22807。底层是跨注意力架构：文档离线预编码，查询来了走跨注意力评分。

三种问题类型与原版 Jev 一致：

| 类型 | 语义 | 输出 |
|------|------|------|
| **Choice** | 从无序选项中选一个最匹配的 | 各选项概率 + 最优选项 |
| **Score** | 有序量表打分（如 1–5 分） | 期望分值 + 各档概率 |
| **Noul** | 独立 Yes/No 判断（可批量） | 每个条件的归一化概率 |

---

## 硬件要求

KaLM-Jev 提供三档模型，按业务规模和硬件资源选型：

### 模型参数与资源对照

| 模型 | 激活参数 | 层数 | 隐层维度 | 最大序列长度 | 推荐 VRAM | 最低可用 |
|------|---------|------|---------|------------|---------|---------|
| **KaLM-Jev Nano** | 0.27B | 18 | 640 | 128K | 4 GB | 2 GB（BF16 → FP16） |
| **KaLM-Jev Small** | 1B | 26 | 1,152 | 128K | 6 GB | 4 GB |
| **KaLM-Jev Large** | 4B | 34 | 2,560 | 128K | 16 GB | 8 GB（BF16） |

### GPU 还是 CPU？

**官方测试环境**：NVIDIA H100 MIG 实例，BF16 精度。

**CPU 运行**：支持，但性能未经官方系统评估。CPU 模式下需切换 FP32（BF16 在大多数 CPU 上不可用）：

```bash
kalm-jev serve --device cpu --dtype float32
```

**Apple Silicon**：未在 README 中提及 MPS 支持，暂不确定是否可用。

### 生产环境建议

- **日均判断量 < 10万次**：Nano 配 4GB 显存的消费级 GPU（RTX 3060 / 4060）即可满足
- **日均判断量 10万–100万次**：Small，配 8–12GB 显存（RTX 3080 / 4070）
- **高精度场景 / 长文本**：Large，配 16–24GB 显存（RTX 4090 / A5000）

LRU 缓存默认 256 MiB，相同文档的编码结果会复用，频繁重复的文档集能显著降低 GPU 占用。

---

## 本地部署：分步操作

### 第一步：克隆与安装

```bash
git clone https://github.com/KaLM-Embedding/KaLM-Jev.git
cd KaLM-Jev

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

python -m pip install -e '.[test]'
```

### 第二步：选择模型

三个模型 ID 对应 HuggingFace：

```
KaLM-Embedding/KaLM-Reranker-V1-Nano-R2   # 0.27B
KaLM-Embedding/KaLM-Reranker-V1-Small-R2  # 1B
KaLM-Embedding/KaLM-Reranker-V1-Large-R2  # 4B
```

首次运行会自动下载。国内网络可提前手动拉取：

```bash
huggingface-cli download KaLM-Embedding/KaLM-Reranker-V1-Nano-R2 \
  --local-dir ./models/KaLM-Reranker-V1-Nano-R2
```

### 第三步：启动服务

**GPU（推荐）：**

```bash
kalm-jev serve \
  --model kalm-jev-nano \
  --device cuda \
  --dtype bfloat16 \
  --batch-size 4 \
  --cache-max-mib 256
```

**CPU（离线/轻量）：**

```bash
kalm-jev serve \
  --model-path ./models/KaLM-Reranker-V1-Nano-R2 \
  --device cpu \
  --dtype float32
```

服务默认监听 `127.0.0.1:8000`，无认证。

### 第四步：验证服务

```bash
curl http://127.0.0.1:8000/health
```

返回 `{"status": "ok"}` 表示就绪。

---

## 对接业务流程

KaLM-Jev 提供两种集成方式：REST API 和 Python SDK。

### 方式一：REST API（推荐，语言无关）

任何能发 HTTP 请求的系统都可以对接，与后端语言无关：

```bash
curl http://127.0.0.1:8000/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{
    "context": "用户评论：这个产品质量很差，我很失望",
    "tasks": [
      {
        "type": "Choice",
        "question": "这条评论的情感倾向是什么？",
        "choices": ["正面", "负面", "中性"]
      },
      {
        "type": "Score",
        "question": "这条评论的紧急程度（需要人工介入）",
        "levels": ["低", "中", "高", "紧急"]
      }
    ]
  }'
```

### 方式二：Python SDK

```python
from kalm_jev import Engine, JevRequest, ChoiceTask, ScoreTask

engine = Engine(
    model="kalm-jev-nano",
    device="cuda",
    dtype="bfloat16",
)

request = JevRequest(
    context="用户工单：系统登录后30秒自动退出，已重复出现3次",
    tasks=[
        ChoiceTask(
            question="这个工单属于哪个技术类别？",
            choices=["认证/权限", "性能问题", "数据异常", "UI缺陷"]
        ),
        ScoreTask(
            question="工单优先级",
            levels=["P4", "P3", "P2", "P1"]
        )
    ]
)

result = engine.evaluate(request)
# result.tasks[0].choice → "认证/权限"
# result.tasks[1].expected_level → 1  (P3)
```

### 典型业务场景示例

**客服工单自动分类路由：**

```python
# 工单入库时调用，结果写入数据库
def classify_ticket(ticket_text: str) -> dict:
    request = JevRequest(
        context=ticket_text,
        tasks=[
            ChoiceTask(question="部门路由", choices=["技术支持", "账单", "投诉", "咨询"]),
            ScoreTask(question="优先级", levels=["低", "中", "高", "紧急"]),
        ]
    )
    return engine.evaluate(request)
```

**内容安全过滤：**

```python
NoulTask(
    conditions=[
        "包含个人身份信息（姓名+电话/身份证）",
        "包含攻击性或侮辱性语言",
        "包含商业机密关键词"
    ]
)
```

**向量检索重排序（原生能力）：**

KaLM-Reranker-V1 本身就是重排序模型，可直接接入 RAG 流水线作为 reranker，在向量召回 Top-K 后精排：

```python
# 接在向量检索后
results = vector_search(query, top_k=20)
reranked = engine.rerank(query, [r.text for r in results])
```

### 暴露为内网服务

若需要多服务调用，用 Nginx 或 Tailscale 内网穿透暴露：

```bash
# 绑定内网 IP（别暴露公网，无认证）
kalm-jev serve --host 0.0.0.0 --port 8000 --device cuda --dtype bfloat16
```

---

## 数据初始化：不需要任何训练数据

**直接使用预训练权重，无需准备任何数据**。

KaLM-Reranker-V1 已在约 **370 万样本**上完成预训练，涵盖：
- KaLM 嵌入微调数据集
- BGE-M3 训练数据
- Hard Negative Mining 补充样本

启动服务时只需指定模型 ID，HuggingFace 自动下载权重，开箱即用。

**LRU 缓存预热（可选优化）**：若业务有固定知识库（如产品文档、FAQ），可在服务启动后批量编码：

```python
# 预热：把高频文档提前编码进 LRU 缓存
engine.encode_documents(high_frequency_docs)
```

后续查询命中缓存，省掉重复编码开销（默认缓存 256 MiB，可调）。

---

## 是否需要再训练？怎么做？

### 什么情况不需要再训练

- **通用分类/评分/过滤**：预训练权重已经足够，直接部署
- **多语言场景（含中文）**：MIRACL 18 语言基准显示中文性能良好，无需专门微调
- **RAG 重排序**：KaLM-Reranker-V1 在 BEIR 基准上有竞争力，开箱可用

### 什么情况需要再训练

- **高度垂直的领域**（法律合同解析、医学文献、专业代码审查）：预训练数据覆盖不足时，微调能显著提升准确率
- **特定标注格式或分类体系**：如果业务的分类标准与通用训练数据差异较大
- **极致性能要求**：Nano 在通用场景够用，但在精度敏感场景下微调 Small/Large 会有明显提升

### KaLM-Jev 层的微调（⚠️ 当前未公开文档）

**现状**：KaLM-Jev README 没有提供 KaLM-Jev 服务层本身的微调流程。该项目 2026-09-21 刚开源，相关文档尚未完善。

### 微调基础模型（可行路径）

底层模型 KaLM-Reranker-V1 的训练方法在 arXiv 2606.22807 中有完整描述。训练范式：

**数据格式**（对比学习）：

```json
{
  "query": "用户的查询文本",
  "positive": "相关文档（正样本）",
  "negatives": ["不相关文档1", "不相关文档2", "..."]
}
```

**关键训练要素**：

- **Matryoshka 表示**：支持 1×–32× 压缩，训练时统一，推理时按需截断
- **Hard Negative Mining**：BM25 初检 + 重排序筛选难负样本，质量比随机负样本高得多
- **对比损失**：InfoNCE / 对比学习标准设置

**最低数据量估计**：
- 精排微调：每个分类 500–2000 样本（正负各半）
- 领域适配：1 万–5 万条，含 Hard Negative

**训练硬件**：
- Nano 微调：单张 24GB GPU（RTX 3090/4090）
- Small 微调：单张 40–80GB GPU（A100/H100）
- Large 微调：多卡，建议 2×80GB 起步

---

## 性能基准参考

**BEIR（信息检索，nDCG@10，13 任务均值）：**

| 模型 | BEIR nDCG@10 |
|------|-------------|
| KaLM-Jev Large (4B) | **62.87** |
| KaLM-Jev Small (1B) | 60.01 |
| KaLM-Jev Nano (0.27B) | 57.41 |
| Qwen3-Reranker-4B（参照） | 63.50 |

**MIRACL（多语言检索，18 语言均值）：**

| 模型 | MIRACL nDCG@10 |
|------|---------------|
| Large (4B) | 70.07 |
| Small (1B) | 66.89 |
| Nano (0.27B) | 62.08 |

Nano 0.27B 在 LMEB 基准上与 7–12B 嵌入模型竞争，主要优势是参数极小但推理精度不弱。

---

## 局限性与注意事项

**1. 无明确开源许可证**：README 未声明任何 OSI 批准的许可证。在许可证明确前，商业使用存在法律不确定性，建议联系作者确认。

**2. 项目极新**：2026-09-21 开源，32 stars，尚处于早期阶段。API 可能变化，文档（尤其微调部分）待完善。

**3. 无官方 Docker 镜像**：需自行构建容器化部署。

**4. GPU 推荐，CPU 未充分测试**：CPU 模式官方表示"未做完整性能评估"，生产环境建议 GPU。

**5. 英语为主**：模型训练以英语为中心，中文支持已有 MIRACL 验证，但英文场景表现更好。

---

## 与同类项目对比

| 项目 | 模型自有？ | 接口 | 再训练 | 许可证 |
|------|---------|------|--------|--------|
| **KaLM-Jev** | ✅ 自有 KaLM-Reranker-V1 | `/v1/systemone` | 间接可行 | ⚠️ 未声明 |
| LLM2Jev | 复用任意 HF 因果 LLM | `/v1/systemone` | 依底层模型 | Apache 2.0 |
| Kev | LoRA 小模型 | 原生 | LoRA 微调 | 待查 |
| TypeSafe Jev | 私有 RLCD 模型 | `/v1/systemone` | ❌ 不可微调 | 商业闭源 |

KaLM-Jev 的差异化在于：自有的 0.27B Nano 模型，无需借用大 LLM 完成判断任务，硬件门槛最低。

> 项目刚开源，使用前请核实许可证状态。仅供学习研究参考。

---

<!--EN-->

## KaLM-Jev Local Deployment Guide: Hardware, Installation, Business Integration, and Fine-Tuning

`KaLM-Embedding/KaLM-Jev` open-sourced on 2026-09-21 (32 stars) is a local Jev-style judgment engine built on the KaLM-Reranker-V1 cross-attention reranking model from HIT-TMG Lab. It exposes a `/v1/systemone` endpoint compatible with TypeSafe AI's Jev System One, returning structured decisions (Choice/Score/Noul) — no free text generation.

**GitHub**: github.com/KaLM-Embedding/KaLM-Jev | **Stars**: 32 | **⚠️ License**: Not declared

---

### What Makes KaLM-Jev Different

Instead of generating text that you parse, KaLM-Jev decomposes problems into structured candidates and outputs probability distributions over them. Three task types:

- **Choice**: Select one option from an unordered set → probability per option + top choice
- **Score**: Rate on an ordinal scale (e.g., P1–P4 severity) → expected level index + per-level probabilities
- **Noul**: Multiple independent Yes/No judgments in one call → normalized probability per condition

Underlying model: KaLM-Reranker-V1 (encoder-decoder cross-attention architecture). Training described in arXiv 2606.22807.

---

### Hardware Requirements

Three model tiers:

| Model | Parameters | Layers | Hidden | Max Seq | GPU VRAM |
|-------|-----------|--------|--------|---------|----------|
| **Nano** | 0.27B | 18 | 640 | 128K | 2–4 GB |
| **Small** | 1B | 26 | 1,152 | 128K | 4–6 GB |
| **Large** | 4B | 34 | 2,560 | 128K | 8–16 GB |

Official test environment: NVIDIA H100 MIG, BF16. CPU mode supported (`--device cpu --dtype float32`) but not systematically benchmarked. Apple Silicon MPS support unconfirmed.

---

### Local Deployment (5 Steps)

```bash
# 1. Clone and install
git clone https://github.com/KaLM-Embedding/KaLM-Jev.git
cd KaLM-Jev
python -m venv .venv && source .venv/bin/activate
python -m pip install -e '.[test]'

# 2. (Optional) Pre-download model for offline use
huggingface-cli download KaLM-Embedding/KaLM-Reranker-V1-Nano-R2 \
  --local-dir ./models/KaLM-Reranker-V1-Nano-R2

# 3. Start the server (GPU)
kalm-jev serve \
  --model kalm-jev-nano \
  --device cuda \
  --dtype bfloat16 \
  --batch-size 4 \
  --cache-max-mib 256

# 4. Verify
curl http://127.0.0.1:8000/health

# 5. Call the API
curl http://127.0.0.1:8000/v1/systemone \
  -H 'Content-Type: application/json' \
  -d @examples/mixed.json
```

---

### Business Workflow Integration

**REST API** (any language):

```json
POST /v1/systemone
{
  "context": "User complaint: login session drops after 30 seconds, happened 3 times",
  "tasks": [
    {
      "type": "Choice",
      "question": "Which technical category?",
      "choices": ["Auth/Permissions", "Performance", "Data Anomaly", "UI Bug"]
    },
    {
      "type": "Score",
      "question": "Ticket priority",
      "levels": ["P4", "P3", "P2", "P1"]
    }
  ]
}
```

**Python SDK**:

```python
from kalm_jev import Engine, JevRequest, ChoiceTask, ScoreTask

engine = Engine(model="kalm-jev-nano", device="cuda", dtype="bfloat16")
result = engine.evaluate(JevRequest(context=text, tasks=[...]))
```

Common use cases: customer support ticket routing, content moderation, document classification, RAG reranking.

---

### Data Initialization — No Training Data Required

KaLM-Reranker-V1 was pre-trained on ~3.7M samples (KaLM embedding fine-tuning set + BGE-M3 data + Hard Negative Mining). Use the pre-trained weights directly — download happens automatically on first `serve`. No data preparation needed.

**Optional cache warm-up** for repeated document collections:

```python
engine.encode_documents(your_document_list)  # fills 256 MiB LRU cache
```

---

### Retraining Guidance

**You likely don't need to retrain** for general classification, multilingual tasks (18 languages including Chinese validated on MIRACL), or RAG reranking.

**Retrain when**: highly vertical domain (legal, medical, specialized code review), proprietary classification taxonomy, or precision requirements exceed out-of-box performance.

**Fine-tuning the base model** (arXiv 2606.22807 methodology):

```json
// Training data format
{
  "query": "user query",
  "positive": "relevant document",
  "negatives": ["irrelevant-1", "irrelevant-2"]
}
```

Minimum data: 500–2,000 samples per class (domain adaptation); 10K–50K for full fine-tuning. Hardware: Nano on single 24GB GPU; Small needs A100/H100; Large needs multi-GPU.

**Note**: Fine-tuning documentation for the KaLM-Jev service layer itself is not yet published (project is 1 day old). The path above fine-tunes the underlying KaLM-Reranker-V1 base model.

---

### Benchmarks

BEIR (nDCG@10, 13-task average): Large 62.87, Small 60.01, Nano 57.41 (Qwen3-Reranker-4B reference: 63.50).

MIRACL (18-language average): Large 70.07, Small 66.89, Nano 62.08.

Nano 0.27B competes with 7–12B embedding models on LMEB — the main value proposition is very small parameter count without corresponding accuracy drop.

---

### Key Limitations

1. **No declared license**: Commercial use legally uncertain until clarified.
2. **1-day-old project**: API and fine-tuning docs likely to change.
3. **No official Docker image**: Self-container deployment required.
4. **CPU mode not systematically tested**: GPU recommended for production.
5. **English-first training**: Chinese works (MIRACL validated), but English performs better.

> No declared license. Verify licensing with the authors before commercial use. For learning and research reference only.
