---
title: "PAW：0.6B 跑出 32B 效果，用「编译」替代 API 调用的新范式"
titleEn: "PAW: Program-as-Weights — Compile Fuzzy Functions Once, Run Locally Forever with a 0.6B Model"
description: "Program-as-Weights（PAW）提出「模糊函数编程」新范式：用 4B 编译器将自然语言描述编译成 LoRA 适配器，再用冻结的 0.6B 解释器本地运行。0.6B 解释器 + PAW 程序在 FuzzyBench 上超过 Qwen3-32B，内存只用 1/50，MacBook M3 跑 30 tokens/s。HuggingFace 今日论文第一。"
descriptionEn: "Program-as-Weights (PAW) introduces a new fuzzy-function programming paradigm: a 4B compiler converts a natural-language spec into a LoRA adapter once; a frozen 0.6B interpreter runs it locally forever. A 0.6B PAW interpreter beats Qwen3-32B on FuzzyBench (73.78% vs 68.70%), uses 1/50th the memory (~1.2GB vs ~60GB), and runs at 30 tokens/s on a MacBook M3. #1 on HuggingFace papers today."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Research"
tags: ["PAW", "模糊函数", "LoRA", "本地推理", "小模型", "Qwen3", "编译器", "神经程序"]
heroImage: "../../assets/images/program-as-weights-paw-fuzzy-functions-guide-banner.jpg"
---

> **论文**: [arXiv:2607.02512](https://arxiv.org/abs/2607.02512) · **GitHub**: [programasweights](https://github.com/programasweights) · **Demo**: [programasweights.com](https://programasweights.com)  
> **作者**: Wentao Zhang, Liliana Hotsko, Woojeong Kim, Pengyu Nie, Stuart Shieber, Yuntian Deng

---

## 从一个真实的开发痛点开始

写代码这几年，遇到最多的拦截是这句话：

> "这个功能你要调 API，要钱，还不稳定。"

有一类任务，规则写不好，API 又太贵——

- "这段日志需要立即处理吗？"
- "这个 JSON 格式对不对，能不能修好？"
- "这个搜索结果按用户意图排个序？"
- "这段评论是正面的吗？"

这些问题，人一眼就能判断，但要写代码规则来实现，边界情况多到崩溃。调大模型 API 能解决，但每次用户触发就调一次，又贵又慢。

这类问题有个统一的名字：**模糊函数（Fuzzy Functions）**。

PAW 是哈佛大学团队在 2026 年 7 月发表的一篇论文，提出了一个新的解法。

---

## PAW 的核心思路：编译一次，永久本地跑

PAW 的类比非常清晰：它把大模型从「每次调用的问题解决者」变成了「工具制造者」。

```
传统方式：
用户输入 → 调 API（32B 模型）→ 输出         （每次都贵）

PAW 方式：
自然语言描述 → 编译器（4B，一次性）→ LoRA 程序（~23MB）
                                          ↓
              用户输入 → 解释器（0.6B，本地）→ 输出    （永久免费）
```

编译过程**只做一次**。之后所有调用，用 0.6B 的小模型本地跑。

---

## 编译器是怎么工作的

PAW 的编译器分两个阶段：

**第一阶段：伪编译器（Pseudo Compiler）**

一个现成的 4B Qwen3 模型（不需要额外训练），把你的自然语言描述改写成一个「伪程序」：重新组织描述 + 几个输入输出样例。

```
输入描述：
"判断一条服务器日志是不是需要立即处理的错误"

伪程序（第一阶段输出）：
描述：区分需要立即处理的严重日志（panic/OOM/disk full/DB down）
      和可以延后处理的普通日志（info/warn/minor error）
例子：
  "PANIC: out of memory" → "紧急"
  "INFO: server started" → "正常"
  "ERROR: disk usage 95%" → "紧急"
```

**第二阶段：LoRA 编译器（LoRA Compiler）**

这是真正训练过的部分，在 1000 万样本的 FuzzyBench 数据集上训练。它读取第一阶段的输出，生成一组 LoRA 参数——一个 ~23MB 的小文件，就是「PAW 程序」。

```python
# 使用 PAW 编译一个模糊函数（伪代码）
from paw import Compiler, Interpreter

# 编译：只做一次
compiler = Compiler()
program = compiler.compile(
    spec="判断一条服务器日志是不是需要立即处理的错误"
)
program.save("log_triage.paw")  # ~23MB

# 运行：本地，0.6B 模型，无需联网
interpreter = Interpreter()  # 0.6B Qwen3，一次性加载
result = interpreter.run("log_triage.paw", "PANIC: kernel OOM at PID 1234")
# → "紧急"
```

---

## 跑出来的结果：真的超过了 32B

| 方法 | FuzzyBench 准确率 | 推理内存 | MacBook M3 速度 |
|---|---|---|---|
| **PAW（0.6B 解释器）** | **73.78%** | **~1.2 GB** | **30 tok/s** |
| Qwen3-32B 直接调用 | 68.70% | ~60 GB | — |
| Qwen3-14B | 61.x% | ~28 GB | — |
| 0.6B 固定 LoRA（最强）| 52.1% | 1.2 GB | 快 |
| 0.6B 全量微调 | 58.4% | 1.2 GB | 快 |

几个关键数字：
- **73.78% vs 68.70%**：0.6B + PAW 超过 32B 直接调用
- **1/50 内存**：1.2 GB vs 60 GB
- **超过全量微调 15.4pp**：PAW 的增益来自编译器，而不是更多的训练数据或参数

---

## FuzzyBench：1000 万样本的训练数据集

PAW 的另一个贡献是开放了 **FuzzyBench** 数据集：

- **1000 万个样本**，格式是 `(描述, 输入, 目标输出)` 三元组
- **29 个版本**，800+ 个模糊任务类别
- 覆盖：文本分类、格式转换、解析、模糊匹配、自然语言命令、工具调用、安全验证……
- 由 gpt-5.2 生成，并用独立模型做一致性校验
- 完全开放，随论文发布

这个数据集本身就有很大的独立价值——它是第一个大规模的「编译模糊函数」训练集。

---

## 5 个实际应用案例

论文里给了 5 个案例，每一个都是「写规则太难、调 API 太贵」的真实场景：

### 1. 日志分级（Output Triage）

```
描述：过滤服务器日志，只对需要立即处理的条目触发告警
```

把 PAW 程序接入日志流，每条日志用 0.6B 本地模型判断，不需要联网，不需要 API 费用。

### 2. 意图导航（Custom Classification）

```
描述：根据用户输入判断他们想去网站的哪个页面
```

比 if/else 分支准确得多，比调 API 便宜 50 倍。

### 3. 语义搜索重排（Fuzzy Search）

```
描述：按用户实际意图对搜索结果重新排序
```

### 4. 工具调用预处理（Agent Preprocessing）

在 ToolCall-15 基准上得了 **93%**。Agent 的工具调用前先用 PAW 过滤和格式化输入，显著降低主模型负担。

### 5. 创意生成（Creative Generation）

一个多语言猜词游戏——证明 PAW 不只能做分类，也能做生成任务。

---

## 多模态：换一个编译器，解释器不动

PAW 架构的一个优雅设计：**解释器是冻结的，只有编译器是可替换的**。

把文本编译器换成视觉语言编译器（Qwen3-VL-4B），同一个 0.6B 文本解释器就能处理图片任务——图片信息完全被编码进了 LoRA 里：

```
图片输入 → VL 编译器（4B）→ LoRA 程序（含图片条件信息）
                                  ↓
          文本解释器（0.6B）→ 输出
```

在化学公式识别、电路图理解、乐谱解析等图片任务上都验证有效。

---

## 对小工具开发者的实际意义

这个研究目前还在论文阶段，代码在 GitHub 上但还需要一些工程化工作。但思路是清晰的，而且是真实可用的方向：

**PAW 填补了一个中间地带**：

```
复杂度/成本：
低                                                高
规则代码 ←——— PAW 模糊函数 ———→ 每次调大模型 API
（写不好）    （编译一次，本地跑）  （贵/慢/不稳定）
```

以前没有中间这块。要么手写规则，要么调 API。

PAW 如果工程化成熟，对独立开发者的具体用处：
- **情感分类**：判断用户评论正负面，编译一次，本地跑，不花 API 费用
- **格式验证**：验证各种奇怪格式的输入，边界情况覆盖靠编译器而不是自己写
- **JSON 修复**：这个在论文里明确提到，也是实际中最常遇到的痛点之一
- **日志告警**：本地部署的监控系统，不依赖网络

---

## 下一步

- **论文**：[arXiv:2607.02512](https://arxiv.org/abs/2607.02512)
- **GitHub**：[github.com/programasweights](https://github.com/programasweights)
- **在线 Demo**：[programasweights.com](https://programasweights.com)
- **数据集 FuzzyBench**：随 GitHub 仓库开放
- **HuggingFace 论文页**：[huggingface.co/papers/2607.02512](https://huggingface.co/papers/2607.02512)

值得关注的是 GitHub 上的工程化进展——从论文到可以直接 `pip install` 使用，通常还需要一段路，但方向已经很清晰了。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Program-as-Weights (PAW) is a new programming paradigm from Harvard (arXiv:2607.02512). A 4B compiler converts a natural-language function spec into a LoRA adapter (~23MB); a frozen 0.6B interpreter runs it locally forever. Result: 0.6B+PAW beats Qwen3-32B on FuzzyBench (73.78% vs 68.70%) at 1/50th the inference memory (~1.2GB vs ~60GB), running at 30 tokens/s on a MacBook M3.

---

## The Problem: Fuzzy Functions

Many programming tasks resist clean rule-based implementation: filtering log lines by urgency, repairing malformed JSON, ranking by intent, classifying sentiment. These are "fuzzy functions" — humans can do them intuitively, but explicit rules break on edge cases. The current solution: call an LLM API on every input. Expensive, fragile, requires internet, non-reproducible.

PAW proposes a third option between "write brittle rules" and "call a 32B API every time."

## How PAW Works

Two-stage compilation pipeline:

**Stage 1 — Pseudo Compiler** (off-the-shelf 4B Qwen3, no training needed):  
Takes your natural-language spec → rewrites it into a structured pseudo-program (cleaner description + a handful of I/O examples).

**Stage 2 — LoRA Compiler** (4B Qwen3, trained on FuzzyBench):  
Takes the pseudo-program → emits a LoRA adapter (~23MB at Q4_0). This is the PAW "program."

The **0.6B Qwen3 interpreter** is frozen — it never changes. Loading new PAW programs is just swapping adapters.

```python
# Compile once
program = compiler.compile(spec="Flag log lines that need immediate attention")
program.save("log_triage.paw")

# Run forever, locally, no internet
result = interpreter.run("log_triage.paw", "PANIC: kernel OOM at PID 1234")
# → "urgent"
```

## Results

- **73.78%** exact match (PAW 0.6B) vs **68.70%** (Qwen3-32B direct prompting) on FuzzyBench
- **~1.2 GB** inference memory vs **~60 GB** for 32B (50× reduction)
- **30 tokens/s** on MacBook M3
- Beats same-base full fine-tuning by **+15.4pp**, strongest fixed LoRA by **+21.7pp**
- **93%** on ToolCall-15 in agent preprocessing case study

## FuzzyBench Dataset

10M examples of `(spec, input, output)` triples across 800+ fuzzy task categories (classification, format conversion, parsing, fuzzy matching, tool use, safety verification, etc.). 29 incremental versions. Generated by gpt-5.2, verified for consistency. Fully open-sourced with the paper.

## Use Cases for Indie Developers

PAW fills the gap between "rules I can't write correctly" and "API calls I can't afford":
- **Sentiment classification**: compile once, run locally at zero marginal cost
- **JSON repair**: the exact use case the paper highlights — edge cases handled by the compiler
- **Log triage**: local monitoring pipeline, no network dependency
- **Input validation**: fuzzy format checking without brittle regexes

## What's Still Early

The code is on GitHub but not yet `pip install`-ready. The path from paper to production-grade library takes time. Worth watching the repo for engineering progress.

**Links**: [arXiv:2607.02512](https://arxiv.org/abs/2607.02512) · [GitHub](https://github.com/programasweights) · [Demo](https://programasweights.com) · [HuggingFace](https://huggingface.co/papers/2607.02512)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
