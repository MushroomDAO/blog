---
title: "Needle 2：14MB、45M 参数、跑在手机里的工具调用基础模型——Simple Attention Network 架构解析"
titleEn: "needle2-cactus-compute-45m-tool-calling-tiny-device-foundation-model"
description: "Needle 2（GitHub: cactus-compute/needle，⭐9,593，Apache-2.0）是 Cactus Compute 发布的 45M 参数端侧基础模型，14MB 单文件二进制，28MB RAM 内完整运行，专为工具调用、设备控制、结构化提取设计。基于 Simple Attention Network（arXiv:2607.18363）：Hadamard MLP + GQA 注意力 + engram 键值记忆 + CQ2-bit 量化。在同类小模型横测中以 5-70倍更小的体积与 FunctionGemma 270M、Apple FM 互有胜负。"
descriptionEn: "Needle 2 (GitHub: cactus-compute/needle, ⭐9,593, Apache-2.0) is a 45M-parameter on-device foundation model from Cactus Compute — 14MB single binary, 28MB RAM, purpose-built for tool calling, device control, and structured extraction. Built on Simple Attention Network (arXiv:2607.18363): Hadamard MLP + GQA + engram KV memory + CQ2-bit quantization. Trades wins with FunctionGemma 270M and Apple FM at 5-70x smaller."
pubDate: "2026-08-29"
updatedDate: "2026-08-29"
category: "Research"
tags: ["端侧模型", "工具调用", "Needle2", "小模型", "嵌入式AI", "Simple Attention Network", "量化"]
heroImage: "../../assets/images/needle2-cactus-compute-45m-tool-calling-tiny-device-foundation-model-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：https://github.com/cactus-compute/needle | ⭐ 9,593 | Apache-2.0  
HuggingFace：Cactus-Compute/needle2 | 241 likes | 36,738 downloads  
论文：arXiv:2607.18363（Simple Attention Network）  
参数量：45M | 文件大小：14MB | 运行内存：~28MB  
`pip install cactus-needle`

---

## 一句话定位

**Needle 2 不是把大模型压小，而是为端侧工具调用这个单一任务从头设计了一个新架构。**

14MB 的整个模型文件放进手机、手表、智能家居设备——不依赖云端，完全离线，调用你声明的任意工具，返回结构化 JSON。

---

## 和同类小模型的对比

官方 benchmark 显示，Needle 2（45M，2-bit）在工具调用任务上与以下模型互有胜负：

| 模型 | 参数量 | 大小（f16） | 相对 Needle 2 |
|------|-------|-----------|-------------|
| FunctionGemma 270M | 270M | ~540MB | **6倍大** |
| LFM2.5 230M | 230M | ~460MB | **5x-6倍大** |
| Apple FM | ~未公开 | 更大 | **70倍大**（估算） |
| **Needle 2** | **45M** | **14MB（2-bit）** | 基准 |

Needle 2 的工程目标不是在所有任务上赢——它的目标是：**在工具调用这个垂直任务上，以最小的 footprint 达到可用水平**。

---

## Simple Attention Network：架构设计

论文：[arXiv:2607.18363](https://arxiv.org/abs/2607.18363)

Needle 2 不使用标准 Transformer 的 FFN（Feed-Forward Network），取而代之的是一套针对端侧推理优化的新组件：

### 1. Hadamard MLP（Walsh-Hadamard 变换替代 FFN）

标准 FFN：两个全连接层 + 激活函数，参数量大，访存压力高。

Hadamard MLP：用 Walsh-Hadamard 变换（WHT）替代主要的矩阵乘法。WHT 是一个**正交固定矩阵**，O(n log n) 时间，**无需额外学习权重**。参数只在门控（gate）和缩放部分。

对端侧推理的意义：大幅减少权重读取量（内存带宽是端侧推理的主要瓶颈），无需 GPU 矩阵乘法硬件。

### 2. Engram 键值记忆

`(kₜ, vₜ)` 来自**哈希 n-gram 表**，而不是标准的可学习 K/V 投影。这是一种确定性的、基于 n-gram 统计的记忆机制，类似早期神经网络记忆模块思路的现代变体。

每帧：音素/token n-gram → 哈希 → 查表 → 取出 (k, v) 对 → 注入注意力机制。

### 3. Multi-lane Hyper-connections + 四流残差

模型内部维护 **4个残差流**，Hyper-connections 管理它们之间的路由（用 Sinkhorn 迭代计算双随机归一化路由矩阵 P）。相比单一残差流，在极小参数量下获得更丰富的表征。

### 4. 256-token 滑动窗口 + KV Sinks

工具声明（tool schema）被 **pinned 到 KV cache 里作为固定 sink**。滑动窗口只推进对话部分，工具定义永远在注意力可见范围内。结果：**不管对话多长，总内存都在 28MB 附近**。

### 5. CQ2-bit 量化（Cactus Quants）

Cactus Compute 自研的量化方案，整个模型压到 2-bit，单文件 `.cact` 格式，引擎和权重打包在一起，不需要分开管理。

---

## 三大核心能力

### 工具调用（Tool Calling）

```python
import needle

@needle.tool
def get_weather(city: str):
    "Get the current weather for a city."
    return {"city": city, "temp_c": 27, "sky": "clear"}

agent = needle.Needle(tools=[get_weather])
result = agent.run("what's it like in Lagos right now?")
print(result["results"])
# → [{'city': 'Lagos', 'temp_c': 27, 'sky': 'clear'}]
```

用装饰器声明工具，函数签名自动成为参数 schema，docstring 是工具描述。模型选择调用哪个工具，填充参数，执行，把结果喂回去，返回最终回复。整个循环一行 `agent.run()`。

**字节级 grammar 约束解码**：工具 schema 被编译成 grammar，推理时每个 token 的候选集都被 grammar 剪枝，输出**保证合法的 JSON**，不会产生格式错误。

### 结构化提取（Structured Extraction）

```python
from pydantic import BaseModel

class Invoice(BaseModel):
    vendor: str
    total: float
    due_date: str

invoice = needle.extract("Invoice from Acme Corp, $1,200.00, due 2026-09-01", Invoice)
print(invoice.vendor, invoice.total)
# → Acme Corp 1200.0
```

传 Pydantic 模型，得到 typed 对象，类型由 grammar 在解码时保证。适用于：发票/合同信息提取、日志解析、表单填充等场景。

### 置信度门控（Confidence Gating）

每个响应都带一个由**专门学习的头**（learned head）输出的校准置信度分数：

```python
response = agent.complete("dim the study lights to 40%")
if response["confidence"] > 0.85:
    execute(response["tool_call"])
else:
    escalate_to_human(response)
```

- 分数高 → 直接执行
- 分数低 → 拒绝执行 or 升级给人工

这对嵌入式场景特别重要：模型不确定的时候明确说出来，比静默产生错误工具调用安全得多。

---

## 工具检索（大目录场景）

声明 100 个工具时，不需要每次把所有 schema 都放进上下文：

```python
agent = needle.Needle(tools=all_100_tools, retrieval=True)
# 内置检索头自动从目录里选出最相关的 5 个工具
# grammar 也只约束这 5 个工具的参数空间
```

检索发生在模型内部，不需要额外的向量数据库。

---

## 预置环境（开箱即用）

`needle.environments` 提供了 6 个预置工具集，每个都配有完整的枚举值、约束条件和测试套件：

```python
from needle.environments import smart_home, wearable, productivity

# 智能家居
smart_home.agent.complete("dim the study lights to 30 percent")

# 可穿戴
wearable.agent.complete("set a 25-minute workout timer")

# 生产力
productivity.agent.complete("schedule meeting with Alice tomorrow 3pm")
```

| 环境 | 用途 |
|------|------|
| `smart_home` | 灯光、温控、门锁、场景控制 |
| `media_player` | 播放/暂停/跳过/音量/收藏 |
| `productivity` | 日历、提醒、任务、笔记 |
| `wearable` | 计时器、心率、锻炼、步数 |
| `kitchen_appliance` | 烤箱、洗碗机、咖啡机控制 |
| `data_capture` | 表单填写、数据录入 |

适配自定义产品：把 `Literal` 枚举里的值换成你自己的（房间名、联系人名、品类），保持 schema 形状不变。

---

## LoRA 微调流程

LoRA 在冻结的 base 上训练，export 时 merge 进去，最终产物仍然是一个单文件 `.cact`，在同一个 engine 上运行，不需要重新编译。

**完整流程（4步）：**

```bash
# 1. （可选）用 OpenRouter 自动合成训练数据
export OPENROUTER_API_KEY=sk-or-...
needle generate-data --tools my_tools.json --num-samples 500 --output data.jsonl

# 2. LoRA 微调（JAX，支持 CUDA/Apple Silicon Metal）
pip install "cactus-needle[train,metal]"   # Apple Silicon
needle finetune data.jsonl --epochs 10 --lora-rank 16 --lora-alpha 32

# 3. 构建 .cact 文件（合并 adapter + 量化）
needle build checkpoints/needle2.pkl --lora checkpoints/needle_lora.pkl --out my_needle.cact

# 4. 运行微调后的模型
import needle
agent = needle.Needle(weights="my_needle.cact", tools=[...])
agent.run("...")
```

训练数据格式（JSONL）：

```json
{"query": "dim the kitchen to 10",
 "tools": [{"name": "set_lights", "parameters": {...}}],
 "answers": [{"name": "set_lights", "arguments": {"room": "kitchen", "brightness": 10}}],
 "reasoning": "'kitchen' -> room; 'dim to 10' -> brightness 10"}
```

`reasoning` 字段可选，`answers: []` 表示该 query 不需要工具调用（off-topic 负样本）。

**训练后可选上传 HuggingFace：**

```bash
NEEDLE_HF_REPO=your_org/my_needle needle build ... --upload
# 在任何机器上拉取：
needle download your_org/my_needle/my_needle.cact
```

---

## 适用场景

**最适合：**
- 智能家居/IoT 设备（树莓派、MCU、嵌入式 Linux）
- 手机本地 agent（无需联网，隐私保护）
- 可穿戴设备（内存极限场景）
- 工业机器人控制（确定性输出 + 置信度门控）
- 边缘计算场景（离线、低延迟要求）

**不适合：**
- 需要复杂推理、长文生成的任务（用 Claude/GPT）
- 超过 256-token 上下文的多轮对话（滑动窗口会丢失早期对话）
- 要求多语言、通识知识的场景

---

## 快速验证

```bash
pip install cactus-needle
# 启动 playground（自动下载模型，~14MB）
needle playground
# 打开 http://127.0.0.1:7860，选预置，Run
```

或者用 Python 验证工具调用：

```python
import needle

@needle.tool
def set_lights(room: str, brightness: int):
    "Set the brightness of lights in a room (0-100)."
    return {"set": True, "room": room, "brightness": brightness}

agent = needle.Needle(tools=[set_lights])
print(agent.run("turn the kitchen lights to 40%")["results"])
```

---

**相关链接**

- GitHub：https://github.com/cactus-compute/needle
- HuggingFace：https://huggingface.co/Cactus-Compute/needle2
- 论文：https://arxiv.org/abs/2607.18363
- PyPI：https://pypi.org/project/cactus-needle/
- 联系：founders@cactuscompute.com

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

<!--EN-->

## Needle 2: A 14MB, 45M-Parameter Tool-Calling Foundation Model for Tiny Devices

*by Mycelium Protocol*

---

GitHub: https://github.com/cactus-compute/needle | ⭐ 9,593 | Apache-2.0  
HuggingFace: Cactus-Compute/needle2 | 241 likes | 36,738 downloads  
Paper: arXiv:2607.18363 (Simple Attention Network)  
Parameters: 45M | Binary size: 14MB | Runtime RAM: ~28MB  
`pip install cactus-needle`

---

### One-Line Positioning

**Needle 2 is not a compressed large model. It is a new architecture designed from scratch for on-device tool calling as a single vertical task.**

The entire model — 14MB — runs on a phone, a smartwatch, a smart home hub. No cloud dependency. Fully offline. Calls tools you declare and returns structured JSON.

---

### Benchmark Comparison

Needle 2 (45M, 2-bit) trades wins with these models on tool-calling benchmarks:

| Model | Parameters | Size (f16) | vs. Needle 2 |
|-------|-----------|-----------|-------------|
| FunctionGemma 270M | 270M | ~540MB | 6× larger |
| LFM2.5 230M | 230M | ~460MB | 5-6× larger |
| Apple FM | undisclosed | larger | ~70× larger |
| **Needle 2** | **45M** | **14MB (2-bit)** | baseline |

The engineering goal is not to win on all tasks — it is to reach a usable quality bar on tool calling specifically, at the smallest possible footprint.

---

### Simple Attention Network Architecture

Paper: [arXiv:2607.18363](https://arxiv.org/abs/2607.18363)

Needle 2 replaces the standard Transformer FFN with a purpose-built stack:

**1. Hadamard MLP (Walsh-Hadamard Transform instead of FFN)**

Standard FFN: two dense layers + activation. High parameter count, high memory bandwidth.

Hadamard MLP: replaces the main matrix multiplications with the Walsh-Hadamard Transform (WHT) — an orthonormal fixed matrix applied in O(n log n) time with **no additional learned weights**. Only the gate and scale parameters are learned. Result: dramatically less weight loading, which matters when memory bandwidth is the bottleneck (it always is on-device).

**2. Engram Key-Value Memory**

`(kₜ, vₜ)` pairs come from **hashed n-gram tables** instead of learned K/V projections. Token n-grams hash to fixed table indices, returning (k, v) pairs injected into the attention layer. Deterministic, fast, and parameter-free.

**3. Multi-lane Hyper-connections + Four Residual Streams**

Four residual streams run in parallel; Hyper-connections manage routing between them via a doubly-stochastic routing matrix P (computed by Sinkhorn iteration). Richer representations than a single residual stream, with minimal parameter overhead.

**4. 256-token Sliding Window + KV Sinks**

Tool schemas are **pinned as KV sinks** — they stay in the attention window no matter how far the conversation advances. The sliding window only advances for the dialogue portion. Result: **total memory stays near 28MB regardless of conversation length.**

**5. CQ2-bit Quantization (Cactus Quants)**

Cactus Compute's custom quantization scheme. Entire model at 2-bit, packed into a single `.cact` archive with the inference engine. No separate model files to manage.

---

### Three Core Capabilities

**Tool Calling**

```python
import needle

@needle.tool
def get_weather(city: str):
    "Get the current weather for a city."
    return {"city": city, "temp_c": 27, "sky": "clear"}

agent = needle.Needle(tools=[get_weather])
result = agent.run("what's it like in Lagos right now?")
print(result["results"])
# → [{'city': 'Lagos', 'temp_c': 27, 'sky': 'clear'}]
```

The function decorator provides the tool description; the type signature becomes the JSON schema; `agent.run()` handles the full loop. Every output token is constrained by a **byte-level grammar compiled from your tool schemas** — the output is guaranteed to be valid JSON matching your schema.

**Structured Extraction**

```python
from pydantic import BaseModel

class Invoice(BaseModel):
    vendor: str
    total: float
    due_date: str

invoice = needle.extract("Invoice from Acme Corp, $1,200.00, due 2026-09-01", Invoice)
# → Invoice(vendor='Acme Corp', total=1200.0, due_date='2026-09-01')
```

Pass a Pydantic model, get a typed object back. Types are enforced by the decode grammar, not post-hoc parsing.

**Confidence Gating**

```python
response = agent.complete("dim the study lights to 40%")
if response["confidence"] > 0.85:
    execute(response["tool_call"])
else:
    escalate_to_human(response)
```

A learned confidence head produces a calibrated score per response. Set a threshold — act above it, escalate below it. Critical for embedded deployments where a wrong tool call has physical consequences.

---

### LoRA Fine-Tuning Pipeline

```bash
# 1. (Optional) Synthesize training data with OpenRouter
needle generate-data --tools my_tools.json --num-samples 500 --output data.jsonl

# 2. LoRA fine-tune (JAX — works on CUDA or Apple Silicon Metal)
pip install "cactus-needle[train,metal]"
needle finetune data.jsonl --epochs 10 --lora-rank 16

# 3. Build .cact (merge adapter + quantize)
needle build checkpoints/needle2.pkl --lora checkpoints/needle_lora.pkl --out my_needle.cact

# 4. Deploy
import needle
agent = needle.Needle(weights="my_needle.cact", tools=[...])
```

The LoRA adapter is merged at export time — the tuned model is still a single `.cact` file running on the same engine. No recompilation, no separate runtime.

---

### Pre-built Environments

```python
from needle.environments import smart_home, wearable, productivity

smart_home.agent.complete("dim the study lights to 30 percent")
wearable.agent.complete("set a 25-minute workout timer")
```

Six ready-made tool surfaces: `smart_home`, `media_player`, `productivity`, `wearable`, `kitchen_appliance`, `data_capture`. Each comes with curated enums, value bounds, and a frozen acceptance test suite. Adapt to your product: swap the `Literal` values for your own names, keep the schema shapes.

---

### Best Fit / Not a Fit

**Best fit:**
- Smart home / IoT devices (Raspberry Pi, embedded Linux, MCU)
- On-phone local agents (no network, privacy-first)
- Wearables (extreme memory constraints)
- Industrial robot control (deterministic output + confidence gating)
- Edge/air-gapped deployments

**Not a fit:**
- Complex reasoning, long-form generation (use a full-size model)
- Conversations longer than 256 tokens where early context matters
- Tasks requiring multilingual fluency or broad world knowledge

---

### 5-Second Verification

```bash
pip install cactus-needle
needle playground  # → http://127.0.0.1:7860
```

---

**Links**

- GitHub: https://github.com/cactus-compute/needle
- HuggingFace: https://huggingface.co/Cactus-Compute/needle2
- Paper: https://arxiv.org/abs/2607.18363
- PyPI: https://pypi.org/project/cactus-needle/
- Contact: founders@cactuscompute.com

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
