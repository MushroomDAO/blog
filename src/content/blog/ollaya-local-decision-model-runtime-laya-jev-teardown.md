---
title: "Ollaya：本地运行决策模型的 Ollama，Laya 推理 8ms，比 Jev 云端快 30 倍"
description: "ollaya-dev/ollaya，Apache 2.0，409 星。「Jev 界的 Ollama」——一条命令拉取并本地运行 Laya、decider、NLI、GLiClass 等决策模型，兼容 TypeSafe /v1/systemone API，换一个环境变量即可从 Jev 云端切换到本地。模型仅 3MB ONNX 图，老笔记本装得下，断网能跑。Laya 本地推理 8ms（中文）vs Jev 云端 276ms，快约 30 倍。"
pubDate: 2026-09-29
heroImage: "../../assets/images/ollaya-local-decision-model-runtime-laya-jev-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["决策模型", "本地推理", "TypeSafe", "开源拆解", "Laya", "AI推理"]
lang: "zh-CN"
wechatTitle: "Ollaya：本地运行Laya决策模型的Ollama"
wechatDigest: "409星Apache-2.0；Laya本地8ms vs Jev云端276ms；3MB ONNX；一个env变量切换"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 决策模型不生成文字，只出概率分数

在看 Ollaya 之前，先搞清楚它跑的是什么模型——因为「决策模型」和「语言模型」是完全不同的东西。

给语言模型一封退款工单，它会写一大段分析文字，一个字一个字地输出。给决策模型同一封工单，加几个结构化问题：

```
这是什么类型的工单？
用户有多着急？
用户的情绪激动程度（0-3分）？
这真的是一个退款请求吗？
用户会取消订单吗？
```

决策模型读一遍材料，直接返回带置信度的答案表：

```
什么事儿  → 退款     1.00
着急吗    → 不急     0.88
生气程度  → 1.76/3档 0.36
真在退款  → 是       0.90
会取消吗  → 暂不会   0.61
```

没有生成任何 token。输出是概率向量，不是文字。延迟是 8ms，不是 8 秒。

这是 Jev（TypeSafe AI）/ Laya（Convai Innovations）等项目在做的事情。Ollaya 把这些模型本地化，按 Ollama 的方式管理和运行。

仓库：github.com/ollaya-dev/ollaya  
**Stars：409 | License：Apache-2.0 | 非 Ollama / TypeSafe 官方项目**

---

## Ollama 的命令体系，完整移植

如果你用过 Ollama，Ollaya 的命令会立刻看懂：

```bash
# 启动守护进程
ollaya serve

# 拉取模型
ollaya pull laya
ollaya pull decider
ollaya pull gliclass

# 运行单次推理
ollaya run laya

# 管理
ollaya list          # 已安装的模型
ollaya ps            # 正在运行的模型
ollaya show laya     # 模型详情
ollaya rm laya       # 删除
ollaya cp laya mycopy   # 复制

# 停止守护进程
ollaya stop
```

API 兼容 TypeSafe 的 `/v1/systemone` 接口。对已经在用 Jev 客户端的代码，**只需要把一个环境变量从 Jev 云端地址改成 `http://localhost:11434`**，就完成了切换。不需要修改业务逻辑。

---

## 可用模型清单

| 模型 | 来源 | 特性 |
|------|------|------|
| laya | Convai Innovations | 多语言，8ms/中文，10ms/英文 |
| decider | Mapika | — |
| kev | — | 本地判断引擎 |
| decision | — | 通用决策 |
| qwen3guard | — | 基于 Qwen3 的 guard 变体 |
| gliclass | — | GLiClass 零样本分类 |
| von | EldanRing | — |
| winnow | EldanRing (Gemma 4 base) | — |
| jevk5 | — | TypeSafe 兼容 |
| nli 系列 | 多家 | 自然语言推理 |

模型以 ONNX 图形式分发，单个约 **3MB**——不是几十 GB 的大模型，而是几百兆级别的专用推理图。官方描述是「old laptop can run」，不是营销语言。

ONNX 图本身是「weightless」的——权重读取自原作者在 HuggingFace 上 pin 到特定 commit 的 `model.safetensors`，并通过 sha256 校验，确保重现性。

---

## 关键性能对比

用户提供的实测数字：

| 运行环境 | 推理延迟 |
|----------|---------|
| Laya 本地（中文）| **8ms** |
| Laya 本地（英文）| **10ms** |
| Jev 云端 | 236–276ms |
| T4 GPU（10 个问题打包）| 158.6ms |

本地 vs 云端最快快 **~30 倍**。

这是决策模型的天然优势：它们足够小，可以在本地以 CPU 运行，消除了网络往返延迟。语言模型在 CPU 本地运行意味着几秒延迟；决策模型在 CPU 本地运行是毫秒级。

---

## 四个需要了解的点

### 1. 不是 Ollama 或 TypeSafe 的官方项目

README 明确声明：「not affiliated with or endorsed by Ollama or TypeSafe.」这是独立社区项目，ollay-dev 是独立组织。

这不是批评，而是使用前要知道的信息：意味着遇到问题没有官方支持通道，也意味着如果 /v1/systemone 协议有破坏性变更，Ollaya 需要自行跟进。

### 2. 模型许可证需要逐一核查

README 列出的模型来自不同来源，许可证各不相同。Ollaya 自身是 Apache-2.0，但运行的模型有各自的授权约束——生产使用前需要核查每个模型的许可条款。

### 3. 409 星 = 很早期

项目在昨天（2026-09-28 前后）开源或登上 GitHub Trending，目前 409 星处于早期阶段。功能可能还不稳定，API 可能变化。

### 4. 只适合决策类任务

决策模型适合结构化判断：分类、意图识别、评分、置信度估计。不适合：写作、问答、代码生成——那些还是需要语言模型。Ollaya 是工具链里的一个专用组件，不是 LLM 替代。

---

## 适合什么场景

现实的使用场景：

- **工单路由**：读取工单内容，判断类型 + 紧急程度 + 情绪，自动分派
- **内容审核**：输入一段文字，判断是否违规 + 置信度，速度要求高
- **意图识别**：用户输入 → 意图标签 + 概率，不需要语言模型的完整生成
- **Agent 前置判断**：在调用昂贵的 LLM 之前，先用决策模型过滤无效请求
- **A/B 评估**：对模型输出做结构化评分，不需要人工打标

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 409 |
| License | Apache-2.0 |
| 模型大小 | ~3MB ONNX |
| Laya 本地延迟（中文） | 8ms |
| Laya 本地延迟（英文） | 10ms |
| Jev 云端延迟 | 236–276ms |
| API 格式 | TypeSafe /v1/systemone |
| 命令兼容 | Ollama 风格（serve/pull/run/list/ps…） |

---

## 综合判断

决策模型是 AI 工程里一个被低估的组件。语言模型在生成场景无可替代，但大量生产任务实际上是判断类任务——这类任务用决策模型做，不仅快 30 倍，而且可以完全断网本地运行，不受 API 配额限制，成本为零。

Ollaya 的价值在于把这件事从「需要自己搭环境」变成「`ollaya pull laya` + 换一个 env 变量」。409 星的早期项目，值得在低风险场景先行测试，不适合直接压上生产关键路径。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## Ollaya: Run Decision Models Locally Like Ollama, Laya 8ms vs Jev Cloud 276ms

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Decision Models Don't Generate Text — They Output Probability Scores

Before looking at Ollaya, understand what it runs: **decision models** are fundamentally different from language models.

Give a language model a refund ticket: it generates paragraphs, token by token. Give a decision model the same ticket plus structured questions:

```
What type of ticket is this?
How urgent is the user?
Emotional intensity (0-3)?
Is this actually a refund request?
Will the user cancel?
```

It reads once, returns a scored table instantly:

```
Type       → refund    1.00
Urgency    → low       0.88
Emotion    → 1.76/3    0.36
Refund?    → yes       0.90
Cancel?    → no        0.61
```

Zero tokens generated. Outputs are probability vectors, not text. Latency is 8ms, not 8 seconds.

Repo: github.com/ollaya-dev/ollaya  
**409 stars | Apache-2.0 | Independent project — not affiliated with Ollama or TypeSafe**

---

### Ollama Command Surface, Ported Wholesale

```bash
ollaya serve           # start daemon
ollaya pull laya       # download model
ollaya run laya        # run inference
ollaya list            # installed models
ollaya ps              # running models
ollaya stop            # shut down
```

The API speaks TypeSafe's `/v1/systemone` wire format. Existing Jev clients switch to local inference by **changing one environment variable** — no business logic changes required.

---

### Available Models

| Model | Origin | Notes |
|-------|--------|-------|
| laya | Convai Innovations | Multilingual, 8ms/Chinese, 10ms/English |
| decider | Mapika | — |
| kev, decision | various | local judgment engines |
| qwen3guard | — | Guard variant on Qwen3 |
| gliclass | — | Zero-shot classification |
| von, winnow | EldanRing | winnow on Gemma 4 |
| jevk5 | — | TypeSafe-compatible |
| nli variants | multiple | NLI inference |

Models ship as ONNX graphs, ~**3MB each** — hundreds of megabytes, not dozens of gigabytes. Graphs are weightless; weights are fetched from author's HuggingFace repo, pinned to a commit, sha256-verified.

---

### Performance Numbers

| Runtime | Latency |
|---------|---------|
| Laya local (Chinese) | **8ms** |
| Laya local (English) | **10ms** |
| Jev cloud | 236–276ms |
| T4 GPU (10 questions batched) | 158.6ms |

Local is ~**30× faster** than cloud. This is the structural advantage of decision models: small enough to run on CPU locally, eliminating network round-trips. Where an LLM running locally on CPU takes seconds, a decision model takes milliseconds.

---

### Four Things to Know

**1. Independent project.** Not official Ollama or TypeSafe. No official support channel; protocol changes require independent follow-up.

**2. Model licenses vary.** Ollaya itself is Apache-2.0, but individual models carry their own license terms. Verify before production use.

**3. 409 stars = very early.** Launched around 2026-09-28. Expect API instability; not ready for critical production paths.

**4. Only for classification/decision tasks.** Writing, Q&A, code generation still need LLMs. Ollaya is a specialized component, not an LLM replacement.

---

### Real Use Cases

- **Ticket routing**: classify ticket type + urgency + sentiment in one 8ms call
- **Content moderation**: structured yes/no + confidence, high throughput
- **Intent detection**: user input → intent label + probability, without full LLM generation
- **Agent pre-filter**: gate expensive LLM calls with a fast decision-model screen
- **Evaluation scoring**: structured output quality scoring without human labeling

---

### Verdict

Decision models are underutilized in AI pipelines. For classification and judgment tasks, they're 30× faster than cloud LLMs, run fully offline, have zero API quota constraints, and cost nothing per call.

Ollaya makes this accessible: `ollaya pull laya`, change one env variable, done. At 409 stars it's early-stage — suitable for low-risk experiments, not yet appropriate to stake production critical paths on.

---

> Open source for learning only. Verify license terms before commercial use.
