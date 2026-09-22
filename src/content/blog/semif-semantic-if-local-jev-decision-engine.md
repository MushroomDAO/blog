---
title: "SemIf 拆解：把 Agent 的每次判断从「生成文字再解析」降维为「读 logit」，5× 提速"
titleEn: "SemIf Teardown: Reduce Every Agent Decision from 'Generate Text Then Parse' to 'Read Logit' — 5× Faster"
description: "TheoLeeCJ/SemIf，3,700+ stars，MIT。开源复刻 TypeSafe Jev /v1/systemone 语义条件判断接口。直接读模型 logit、零输出 token，比自回归 JSON 快 5.21×。支持 CUDA、Apple Silicon MLX、CPU llama.cpp，甚至浏览器 WebGPU。27B 量化版准确率 0.958，接近闭源 Jev 水平。"
descriptionEn: "TheoLeeCJ/SemIf — 3,700+ stars, MIT. Open-source reimplementation of TypeSafe Jev /v1/systemone semantic decision API. Reads model logits directly, zero output tokens, 5.21× faster than autoregressive JSON. Supports CUDA, Apple Silicon MLX, CPU llama.cpp, and browser WebGPU. 27B quantized model reaches 0.958 accuracy, near closed-source Jev level."
pubDate: 2026-09-22
heroImage: "../../assets/images/semif-semantic-if-local-jev-decision-engine-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "local-ai", "jev", "agent", "decision-engine", "logit", "python", "mit"]
lang: zh-CN
---

`TheoLeeCJ/SemIf`，3,700+ stars，MIT 协议。它解决了一个大多数 Agent 开发者都遇到过但鲜少正面处理的问题：用生成式 LLM 做分支判断，本质上是在绕路。

**GitHub**：github.com/TheoLeeCJ/SemIf | **Stars**：3,700+ | **License**：MIT | **语言**：Python | **原名**：OpenJev

---

## 问题：Agent 决策用错了工具

典型的 Agent 流程里，一个"路由"步骤长这样：

```python
response = llm.chat("这条工单是属于技术问题、账单问题还是投诉？")
# → "根据内容分析，这应该属于技术问题..."
category = parse_response(response)  # 再解析
```

整个过程：生成自然语言 → 解析回结构化结果。但判断本身和语言生成没有任何关系——模型推理完就已经知道答案了，把它写出来再解析回去，是纯粹的开销。

这正是 TypeSafe AI 的 Jev（System One）产品的核心观察：决策模型不应该生成文本，直接输出概率分布就够了。SemIf 用开源方式复刻了这个接口。

---

## SemIf 做了什么

**直接读 logit，不生成任何 token。**

对于一个 Choice 问题（从 A/B/C 中选一个），SemIf 的做法是：

1. 把状态（state）+ 判断标准（question）+ 各选项（options）拼成 prompt
2. 单次前向传播，在 next token 位置读各选项 token 的原始 logit
3. softmax 归一化 → 概率分布 → 决策结果

整个过程：**0 个输出 token，1 次前向传播。**

```
非结构化状态 + 运行时判断标准 + 声明的选项
         ↓
    4B 模型（单次前向传播）
         ↓
各选项的原生 logit → 归一化概率 → 决策结果
```

---

## 性能数据：5× 提速

测试环境：RTX 3090，Qwen3.5-4B，21 个二元判断。

**直接 logit vs. 自回归 JSON（同一模型）：**

| 模式 | 耗时 | 输出 token 数 |
|------|------|------------|
| SemIf 直接 logit | **1.023 秒** | **0** |
| 自回归 JSON array | 5.332 秒 | 111 |
| **加速比** | **5.21×** | — |

**状态复用优化（37 状态 × 21 标准 = 777 次决策）：**

| 模式 | 吞吐 |
|------|------|
| 全新直接评分 | 2.33 decisions/sec |
| 串行前缀复用 | 10.75 decisions/sec |
| **并行 suffix 复用** | **20.03 decisions/sec** |

777 次判断总耗时 38.8 秒——平均每次决策约 50ms。

**状态复用**是性能杠杆最大的优化：当多个判断标准共享同一个长状态前缀时，KV cache 只计算一次，多条判断分支在 suffix 位置并行分叉。

---

## 准确率基准

人工标注的 144 个决策（balanced accuracy）：

| 模型 | 准确率 |
|------|-------|
| Qwen3.5-4B（4B BF16） | 0.813 |
| Qwen3.8-27B EXL3（27B 5-bit 量化） | **0.958** |

校准质量（Expected Calibration Error，越低越好）：

| 数据集 | 校准前 ECE | 校准后 ECE | 改善 |
|--------|---------|---------|------|
| 人工标注数据 | 0.068 | 0.038 | **44%** |
| WANLI（NLI 基准） | 0.208 | 0.069 | **67%** |

27B 量化版的 0.958 准确率，已接近 TypeSafe 闭源 Jev 的水平。

---

## 安装与使用

### 硬件要求

| 后端 | 环境 | 推荐配置 |
|------|------|---------|
| CUDA | Linux/Windows | RTX 3090（4B BF16）起步；27B 需 24GB+ |
| Apple Silicon | macOS | M 系列芯片，走 MLX 后端 |
| CPU-only | 全平台 | llama.cpp + GGUF 量化版，无 GPU 亦可 |
| WebGPU | 浏览器 | 无需安装，直接访问 demo |

### 安装

```bash
python -m venv .venv
source .venv/bin/activate

# CUDA 版（默认）
pip install -e '.[test]'

# Apple Silicon（MLX 后端）
pip install -e '.[test,mlx]'

# 纯 CPU（llama.cpp）
pip install -e '.[test,llamacpp]'
```

首次运行会自动从 HuggingFace 下载模型，建议提前设 `HF_HOME` 到大容量目录：

```bash
export HF_HOME=/path/to/large-drive/huggingface
```

### 基础用法

**命令行：**

```bash
CUDA_VISIBLE_DEVICES=0 semif-score \
  --mode direct \
  --model Qwen/Qwen3.5-4B \
  --revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --input examples/decisions.jsonl \
  --output results.jsonl
```

**输入格式（JSONL）：**

```json
{
  "state": "用户反馈：系统登录后30秒自动退出，已重复3次，影响正常工作",
  "question": "这个问题属于哪个类别？",
  "options": ["认证/权限问题", "性能问题", "数据异常", "UI缺陷"]
}
```

**输出：**

```json
{
  "decision": "认证/权限问题",
  "scores": {
    "认证/权限问题": 0.74,
    "性能问题": 0.12,
    "数据异常": 0.09,
    "UI缺陷": 0.05
  },
  "latency_ms": 48.2,
  "model_revision": "851bf6e...",
  "prompt_hash": "a3f9c..."
}
```

**Apple Silicon（MLX）：**

```bash
semif-score --mode direct --model Qwen/Qwen3.5-4B --backend mlx \
  --input examples/decisions.jsonl --output results.jsonl
```

**CPU（llama.cpp + GGUF）：**

```bash
semif-score --mode direct \
  --checkpoint ./models/qwen3.5-4b-q4_k_m.gguf \
  --input examples/decisions.jsonl --output results.jsonl
```

---

## 状态复用：批量决策的核心优化

真实业务场景里，通常是**同一个状态要过多个判断标准**（先判断类别，再判断优先级，再判断是否需要升级）。SemIf 的 state reuse 模式就是为此设计的：

```python
# 一个工单状态，多个判断标准
state = "用户工单：登录后自动退出，已重复3次"

questions = [
    {"question": "类别？", "options": ["认证", "性能", "数据", "UI"]},
    {"question": "优先级？", "options": ["P4", "P3", "P2", "P1"]},
    {"question": "是否需要立即通知技术负责人？", "options": ["是", "否"]},
]

# 状态前缀只 KV-cache 一次，三个判断并行分叉
results = semif.evaluate_parallel(state, questions)
```

这就是 777 次决策跑出 20 decisions/sec 的来源——状态计算分摊到所有判断上。

---

## 可审计性

SemIf 把"可复现"作为核心设计原则，每条输出包含：

- **model_revision**：HuggingFace commit hash，精确到权重版本
- **prompt_hash**：输入的完整哈希，确保复现用同一 prompt
- **行级输出**：每条决策独立记录，不聚合

这对 Agent 的调试和审计尤为重要——出了问题能精确定位到哪条输入、哪个模型版本、什么提示词产生了错误决策。

---

## 浏览器版（WebGPU Demo）

仓库附带 `webgpu-demo/index.html`，无需安装，浏览器内跑量化版模型，直接在本地做语义判断。适合快速体验或低配设备试用。

---

## 与同类项目对比

本周 memory 里已经记录了几个 Jev 生态项目，对比一下：

| 项目 | Stars | 模型 | 后端 | 许可证 | 特色 |
|------|-------|------|------|--------|------|
| **SemIf** | 3,700+ | 任意 HF Causal LM | CUDA/MLX/llama.cpp/WebGPU | MIT | 最成熟，可审计，WebGPU |
| LLM2Jev | 125 | 任意 HF Causal LM | SGLang/Transformers | Apache 2.0 | staged 模式 4.9× |
| KaLM-Jev | 32 | KaLM-Reranker-V1（自有） | CUDA/CPU | 未声明 | 自有 0.27B-4B 模型 |
| TypeSafe Jev | N/A | 私有 RLCD 模型 | 云端 API | 商业闭源 | 原版，$0.042/M token |

SemIf 的差异化优势：**星数最多、最稳定、后端覆盖最广、有 WebGPU demo**。KaLM-Jev 的差异化是自有小模型（Nano 0.27B），用不了大 GPU 时更轻量。

---

## 局限与注意事项

**1. 状态复用仍属实验性**：README 明确注明"BF16 执行在 777 次 argmax 中有 5–6 个结果与全新评分不同"，高精度场景建议全新评分模式。

**2. GGUF 量化有精度损失**：CPU 和浏览器版使用量化模型，准确率低于 BF16 全精度版本，未见具体量化。

**3. 独立项目**：README 明确声明"Not affiliated with Jev or TypeSafe"，接口兼容性随闭源服务更新可能偏移。

**4. 准确率依赖底层模型质量**：4B 版 0.813，27B 版 0.958。选更大的模型直接提升准确率，但硬件要求也随之升级。

---

## 怎么看这个项目

SemIf 把一个工程观察落地得很干净：Agent 决策里，文字生成只是副产品，logit 才是真信号。去掉解码过程，判断速度 5× 提升是直接的数学结论，不是魔法。

实际工程价值体现在高频路由场景——每秒几十次甚至几百次的分类判断（内容审核、工单路由、文档相关性过滤），累积起来的延迟节省相当可观。

3,700 stars、MIT、四个后端、WebGPU demo——这是少见的把一个核心想法做得又深又宽的项目。

> MIT 协议，开源仅供学习研究参考。独立项目，与 TypeSafe AI / Jev 无关联。

---

<!--EN-->

## SemIf: Reduce Agent Decisions from 'Generate Then Parse' to 'Read Logit' — 5× Faster

`TheoLeeCJ/SemIf` (3,700+ stars, MIT) is the most mature open-source reimplementation of the TypeSafe Jev `/v1/systemone` semantic decision API. Previously called OpenJev.

**GitHub**: github.com/TheoLeeCJ/SemIf | **Stars**: 3,700+ | **License**: MIT | **Lang**: Python

---

### The Problem: Wrong Tool for Agent Branching

Most agent routing looks like this:

```python
response = llm.chat("Is this a billing issue, technical issue, or complaint?")
# → "Based on the content, this appears to be a technical issue..."
category = parse_response(response)
```

The model already *knows* the answer after one forward pass. Generating natural language and parsing it back is pure overhead. SemIf skips both steps.

---

### How It Works

**Read logits directly. Generate zero tokens.**

For a Choice task (select from A/B/C):

1. Assemble prompt: `state + question + options`
2. One forward pass — read raw logit at next-token position for each option token
3. Softmax → probability distribution → decision

**Result: 0 output tokens, 1 forward pass.**

---

### Performance

Test env: RTX 3090, Qwen3.5-4B, 21 binary decisions.

**Direct logit vs. autoregressive JSON (same model):**

| Mode | Time | Output Tokens |
|------|------|---------------|
| SemIf direct logit | **1.023s** | **0** |
| Autoregressive JSON | 5.332s | 111 |
| **Speedup** | **5.21×** | — |

**State reuse (37 states × 21 criteria = 777 decisions):**

| Mode | Throughput |
|------|-----------|
| Fresh direct scoring | 2.33 decisions/sec |
| Serial prefix reuse | 10.75 decisions/sec |
| **Parallel suffix reuse** | **20.03 decisions/sec** |

777 decisions in 38.8 seconds total (~50ms per decision).

---

### Accuracy

Balanced accuracy on 144 human-annotated decisions:

| Model | Accuracy |
|-------|----------|
| Qwen3.5-4B (BF16) | 0.813 |
| Qwen3.8-27B EXL3 (5-bit) | **0.958** |

Calibration (ECE, lower is better): human data 0.068 → 0.038 (44% improvement); WANLI NLI benchmark 0.208 → 0.069 (67%).

---

### Installation

```bash
python -m venv .venv && source .venv/bin/activate

pip install -e '.[test]'          # CUDA (default)
pip install -e '.[test,mlx]'      # Apple Silicon
pip install -e '.[test,llamacpp]' # CPU-only
```

Hardware: CUDA needs RTX 3090+ (4B BF16); Apple Silicon M-series; CPU works via GGUF quantization; browser WebGPU demo available at `webgpu-demo/index.html`.

---

### Basic Usage

```bash
CUDA_VISIBLE_DEVICES=0 semif-score \
  --mode direct \
  --model Qwen/Qwen3.5-4B \
  --input examples/decisions.jsonl \
  --output results.jsonl
```

Input JSONL: `{"state": "...", "question": "...", "options": ["A", "B", "C"]}`

Output includes: decision, per-option scores, latency, model_revision hash, prompt_hash — fully auditable.

---

### State Reuse: Batch Decision Optimization

When one state needs multiple criteria evaluated (classify → prioritize → escalate?), SemIf caches the state's KV once and branches at the suffix for each question:

```python
results = semif.evaluate_parallel(state, [
    {"question": "Category?", "options": ["Auth", "Perf", "Data", "UI"]},
    {"question": "Priority?", "options": ["P4", "P3", "P2", "P1"]},
    {"question": "Escalate immediately?", "options": ["Yes", "No"]},
])
```

This is what drives 20 decisions/sec on 777-decision batches.

---

### Ecosystem Comparison

| Project | Stars | Model | Backends | License |
|---------|-------|-------|----------|---------|
| **SemIf** | 3,700+ | Any HF Causal LM | CUDA/MLX/llama.cpp/WebGPU | MIT |
| LLM2Jev | 125 | Any HF Causal LM | SGLang/Transformers | Apache 2.0 |
| KaLM-Jev | 32 | KaLM-Reranker-V1 (own) | CUDA/CPU | Undeclared |
| TypeSafe Jev | N/A | Private RLCD model | Cloud API | Commercial |

SemIf leads on maturity, backend coverage, and WebGPU reach.

---

### Limitations

1. **State reuse is experimental**: README notes 5–6 argmax differences per 777 calls vs. fresh scoring in BF16
2. **GGUF quantization degrades accuracy**: CPU/browser versions use quantized models; no precise accuracy numbers for quantized tier
3. **Independent project**: Not affiliated with TypeSafe/Jev; API compatibility may drift
4. **Accuracy is model-dependent**: 4B at 0.813, 27B at 0.958 — bigger models score better, hardware scales accordingly

> MIT license. Independent project, not affiliated with TypeSafe AI or Jev. For learning and research reference only.
