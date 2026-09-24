---
title: "AgentJev-0.6B：Qwen3 底座的 System-1 决策核，Typed Decisions 79.25% 超 Laya，KV Cache 砍 92%"
titleEn: "AgentJev-0.6B: Qwen3-Based System-1 Decision Core, 79.25% on Typed Decisions Beats Laya, 92% KV Cache Reduction"
description: "AgentJev-0.6B，Qwen3-0.6B底座+置换等变决策头，System-1 AI Agent 决策模型。Typed Decisions 2000题 79.25%（1585/2000）超 Laya 77.00%（+2.25pt）。零输出 token 解码，约 50ms 一次前向。Shared Prefix KV Cache 在 64 候选时骨干 token 从 33,547 降至 2,551（-92.4%，约 2× 加速）。上下文 2048 token，Boolean/Choice/Score 全类型覆盖，支持完整概率分布输出做路由/阈值/回退门控。权重、训练代码、推理代码全开源。"
descriptionEn: "AgentJev-0.6B — Qwen3-0.6B backbone + permutation-equivariant decision head, System-1 decision model for AI Agents. Typed Decisions 2000: 79.25% (1585/2000) beats Laya's 77.00% (+2.25pt). Zero output-token decoding, ~50ms forward pass. Shared Prefix KV Cache reduces backbone tokens from 33,547 to 2,551 at 64 candidates (−92.4%, ~2× speedup). 2048-token context, Boolean/Choice/Score all covered. Full probability distribution output for routing/threshold/fallback gating. Weights, training code, and inference code all open-sourced."
pubDate: 2026-09-24
heroImage: "../../assets/images/agentjev-0-6b-system-one-decision-model-qwen3-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "agent", "decision-model", "qwen3", "system-one", "jev", "kv-cache", "local-ai"]
lang: zh-CN
---

`aimeigaoshou/agent-jev`，Qwen3-0.6B 底座 + 置换等变决策头，System-1 AI Agent 决策模型。Typed Decisions 2000 题测试中拿到 79.25%（1585/2000），超过 Laya 的 77.00%，领先 2.25 个百分点。零输出 token 解码，约 50ms 完成一次前向。

**GitHub**：github.com/aimeigaoshou/agent-jev | **权重**：huggingface.co/aimeigaoshou/agent-jev

---

## 核心设计：System-1 决策头

AgentJev 的架构选择和 SemIf、KaLM-Jev 这条路不同——它在 Qwen3-0.6B 语言模型骨干上添加了一个**置换等变决策头（permutation-equivariant decision head）**：

- **置换等变**：候选选项的排列顺序不影响输出分数，不会因为选项 A 放第一还是第二就改变判断，消除位置偏差
- **零解码**：不生成任何输出 token，整个决策在 Prefill 阶段完成，~50ms 每次前向
- **概率分布输出**：直接返回每个候选选项的校准概率，不是最优选一个标签

这个设计使它的输出可以直接当门控信号用：阈值过滤、路由打分、fallback 触发，不需要对输出再解析。

---

## Typed Decisions 2000 基准

| 模型 | 准确率 | 正确题数 |
|------|-------|---------|
| **AgentJev-0.6B** | **79.25%** | 1585/2000 |
| Laya | 77.00% | 1540/2000 |

领先 +2.25 个百分点，差值 45 题。

测试覆盖 Boolean（是非判断）、Choice（多选一）、Score（评分）三类决策，输入是非结构化状态文本（diff、trace、日志），模拟真实 Agent 运行中的判断场景。

**需要注意**：这是纯 decision benchmark 的结果，真实 Agent 轨迹的端到端对打尚未完成，纸面领先不等于在具体 Agent 任务里必然领先。

---

## Shared Prefix KV Cache：64 候选时 -92.4%

这是 AgentJev 工程上最实用的改进。Agent 决策场景里候选选项多的时候（路由 64 条规则、分类几十个标签），每个候选都重新跑一遍 state 前向是很大的浪费。

AgentJev 的做法：把 state（现状描述）的 KV Cache 只算一次，然后让所有候选分支共享这个缓存，只需要计算各自的决策头部分。

**实测数据（64 候选）：**

| 场景 | 骨干 token 数 |
|------|-------------|
| 无 KV Cache 复用 | 33,547 |
| Shared Prefix KV Cache | 2,551 |
| 压缩比 | **-92.4%** |
| 速度提升 | 约 **2×** |

候选项越多，KV Cache 复用的收益越大。16 个候选以上时这个优化就值得开启。

---

## 上下文 2048 vs Laya 1024

AgentJev 支持 2048 token 的输入状态，比 Laya 的 1024 翻倍。对于 state 里需要塞进去较长的 diff、多轮 trace 或完整日志段的场景，这个差距是真实的——Laya 在长状态时需要截断，AgentJev 可以保留更多上下文。

---

## 安装与启动

```bash
# 1. 克隆并建立虚拟环境
git clone https://github.com/aimeigaoshou/agent-jev
cd agent-jev
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 从 HuggingFace 拉取权重（需要的两个文件）
huggingface-cli download aimeigaoshou/agent-jev \
    model.safetensors temperatures.json \
    --local-dir ./weights

# 3. 把 safetensors 包成 .pt（不能用普通 CausalLM 加载）
python scripts/convert_checkpoint.py \
    --input weights/model.safetensors \
    --output agentjev_v1.pt

# 4. 启动服务
python -m jev_service.server \
    --checkpoint agentjev_v1.pt \
    --model-path Qwen/Qwen3-0.6B \
    --temperatures weights/temperatures.json \
    --port 8149
```

服务启动后用 `agentjev_client.py` 调用：

```python
from agentjev_client import AgentJevClient

client = AgentJevClient(base_url="http://localhost:8149")

# Boolean 判断
result = client.decide_boolean(
    state="PR diff: 删除了 auth_check 函数，无相关测试变更",
    question="这个 PR 是否引入了安全风险？"
)
print(result)  # {"yes": 0.87, "no": 0.13}

# Choice 路由
result = client.decide_choice(
    state="用户消息：我的订单到哪里了？",
    question="这条消息应该路由到哪个处理队列？",
    choices=["order_tracking", "refund", "complaint", "general_inquiry"]
)
print(result)  # {"order_tracking": 0.91, "refund": 0.04, ...}

# Score 评分
result = client.decide_score(
    state="日志：5s 内 3 次 timeout，数据库连接池耗尽",
    question="当前系统健康状态",
    levels=["critical", "warning", "normal", "healthy"]
)
print(result)  # {"critical": 0.79, "warning": 0.18, ...}
```

---

## 三类决策类型

| 类型 | 输入 | 输出 | 典型用途 |
|------|-----|------|---------|
| **Boolean** | state + 是非问题 | {yes: p, no: 1-p} | 安全检查、条件触发 |
| **Choice** | state + 问题 + 候选列表 | 每候选的概率 | 路由、分类、动作选择 |
| **Score** | state + 问题 + 等级列表 | 每等级的概率 | 质量评估、严重程度分级 |

输出是完整的概率分布，不是硬性最优选——这让下游可以做阈值控制：

```python
# 例：置信度低于 0.7 时走 fallback
decision = client.decide_choice(state=..., question=..., choices=[...])
top_choice = max(decision, key=decision.get)
if decision[top_choice] < 0.7:
    # 走 LLM 重新判断
    fallback_to_llm()
```

---

## 与同类模型对比

| 模型 | 底座 | 上下文 | Typed Dec. | KV Cache 复用 | 开源 |
|------|-----|-------|-----------|-------------|------|
| **AgentJev-0.6B** | Qwen3-0.6B | 2048 | 79.25% | ✅ 原生 | ✅ 全开 |
| Laya | 未知 | 1024 | 77.00% | 未知 | 部分 |
| SemIf | 多种 LLM | 视底座 | 未在该 bench | ✅ | ✅ |
| KaLM-Jev | KaLM 0.27-4B | - | 未在该 bench | ❌ | 无声明许可 |
| JevEmbed | Embedding 模型 | 视模型 | 未在该 bench | ✅ LoRA | ✅ |

AgentJev 是目前在 Typed Decisions 基准上公开报告的最高准确率的全开源模型（截至 2026-09-24）。

---

## 局限性

**1. 仅有 decision benchmark 数据**：Typed Decisions 2000 是专项基准，还没有真实 Agent 轨迹的端到端测试结果，不能据此直接断定在具体任务里优于 Laya。

**2. 启动流程有点绕**：需要先转换 checkpoint 格式（safetensors → .pt），不能直接当标准 CausalLM 加载。这个步骤增加了入门门槛。

**3. Qwen3-0.6B 依赖**：需要本地有 Qwen3-0.6B 权重（`--model-path Qwen/Qwen3-0.6B`），首次运行时 HuggingFace 会自动下载约 600MB。

**4. 许可证尚不明确**：仓库 README 的许可证信息需要核查，商用前需确认。

**5. 单机推理**：目前没有多 GPU 或分布式推理支持的说明，超大候选集场景下的吞吐量受单机限制。

---

## 怎么看这个项目

AgentJev 解决的是同一个问题：**Agent 里的快速决策不应该靠 LLM 全量解码**。在这个方向上它和 SemIf、JevEmbed 是同赛道，技术路线上它走的是「在语言模型上加专用决策头」，而 SemIf 走的是「直接读 LLM logit」，JevEmbed 走的是「用 Embedding 模型计算相似度」。

三条路各有优劣：AgentJev 有语言模型的语义理解能力，但比 Embedding 方案更重；相比 SemIf 它有置换等变的优势，但需要额外的 checkpoint 转换步骤。

79.25% vs 77.00% 是在同一 benchmark 上的干净比较，领先是真实的——前提是你信任这个 benchmark 对你的任务有代表性。权重和训练代码全开源，可以在自己的数据上继续训练，这是比 Laya 实质性更好的条件。

> 开源仅供学习研究参考。商用前请确认仓库许可证。

---

<!--EN-->

## AgentJev-0.6B: Qwen3-Based System-1 Decision Core

`aimeigaoshou/agent-jev` — Qwen3-0.6B backbone + permutation-equivariant decision head. System-1 decision model for AI Agents: 79.25% on Typed Decisions 2000 (1585/2000), beating Laya's 77.00% by +2.25pt. Zero output-token decoding, ~50ms per forward pass.

**GitHub**: github.com/aimeigaoshou/agent-jev | **Weights**: huggingface.co/aimeigaoshou/agent-jev

---

### Architecture

- **Permutation-equivariant decision head**: candidate ordering doesn't affect scores, eliminating position bias
- **Zero output-token decoding**: decision completes in the Prefill phase, no autoregressive generation
- **Full probability distribution output**: calibrated probabilities over all candidates, usable directly as gating signals

---

### Typed Decisions 2000 Benchmark

| Model | Accuracy | Correct |
|-------|---------|---------|
| **AgentJev-0.6B** | **79.25%** | 1585/2000 |
| Laya | 77.00% | 1540/2000 |

Covers Boolean, Choice, and Score across unstructured state inputs (diffs, traces, logs).

**Caveat**: Decision-benchmark-only results. End-to-end agent trajectory testing not yet published — benchmark leads don't automatically translate to task leads.

---

### Shared Prefix KV Cache

State KV cache is computed once; all candidate branches reuse it. At 64 candidates:

| | Backbone tokens |
|-|----------------|
| No reuse | 33,547 |
| Shared Prefix | **2,551** |
| Reduction | **−92.4%**, ~2× speedup |

---

### Setup

```bash
git clone https://github.com/aimeigaoshou/agent-jev && cd agent-jev
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Download weights
huggingface-cli download aimeigaoshou/agent-jev \
    model.safetensors temperatures.json --local-dir ./weights

# Convert checkpoint (required — cannot load as standard CausalLM)
python scripts/convert_checkpoint.py \
    --input weights/model.safetensors --output agentjev_v1.pt

# Start server
python -m jev_service.server \
    --checkpoint agentjev_v1.pt \
    --model-path Qwen/Qwen3-0.6B \
    --temperatures weights/temperatures.json \
    --port 8149
```

---

### Three Decision Types

| Type | Output | Typical Use |
|------|--------|-------------|
| **Boolean** | {yes: p, no: 1-p} | Safety gates, conditional triggers |
| **Choice** | probability per candidate | Routing, classification, action selection |
| **Score** | probability per level | Quality rating, severity grading |

Full probability output enables confidence-gated fallback:

```python
if decision[top_choice] < 0.7:
    fallback_to_llm()
```

---

### Limitations

1. **Decision-benchmark only**: No end-to-end agent trajectory results published yet
2. **Non-standard load path**: Requires checkpoint conversion before serving
3. **Qwen3-0.6B dependency**: ~600MB base model download on first run
4. **License needs verification**: Confirm before commercial use
5. **Single-machine inference**: No documented multi-GPU support

---

### Assessment

AgentJev sits in the same space as SemIf and JevEmbed — fast, non-autoregressive decisions inside agent loops. The technical differentiation: language model backbone (vs. embedding similarity in JevEmbed) with a specialized decision head (vs. direct logit reading in SemIf). The permutation-equivariant head is a clean fix for the position-bias problem. 79.25% vs. 77.00% on the same benchmark is a real comparison — the caveat is whether that benchmark represents your actual task. Weights + training code fully open is a real advantage over Laya.

> For learning and research reference only. Verify license before commercial use.
