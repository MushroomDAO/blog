---
title: "Spark-X2.5-4B：一个 4B 模型在 Agent 榜上打穿 9B，但 GGUF 只放了未量化版"
titleEn: "Spark-X2.5-4B: A 4B Model That Beats 9B on Agent Benchmarks — but Ships Only an Unquantized GGUF"
description: "SparkLLM 开源的 4B 模型 Apache-2.0，原生 1M 上下文靠 1 层全注意力配 3 层滑窗。自报榜单里 τ³-bench 30.4 是 Qwen3.5-9B（9.3）的 3.3 倍，BrowseComp 40.9 是它的 5 倍，MCP-Atlas 54.6 也反超；但 GPQA 67.4 输给 9B 的 77.2——这是典型的「为 Agent 后训练」特征。实测查证：GGUF 仓库只有一个 8.23GB 未量化文件，没有 Q4/Q5，想在 Mac 上跑得自己量化。"
descriptionEn: "SparkLLM's Apache-2.0 4B model claims a native 1M context via one full-attention layer per three sliding-window layers. On its self-reported benchmarks, τ³-bench 30.4 is 3.3x Qwen3.5-9B (9.3), BrowseComp 40.9 is 5x, and MCP-Atlas 54.6 also leads — while GPQA 67.4 loses to 9B's 77.2. That is the signature of agent-focused post-training. Verified caveat: the GGUF repo holds a single 8.23GB unquantized file, no Q4/Q5, so running it on a Mac means quantizing it yourself."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-News"
tags: ["开源模型", "本地部署", "AI Agent", "小模型", "MLX", "Apple Silicon", "长上下文", "MCP", "本地推理"]
heroImage: "../../assets/images/spark-x25-4b-agent-benchmarks-1m-context-local-model-banner.jpg"
author: "Mycelium Protocol"
---

一个 4B 模型在 Agent 类榜单上把 9B 打穿，同时在知识类榜单上输给 9B——这不是异常，这是**为 Agent 做后训练**留下的指纹。

Spark-X2.5-4B 是 SparkLLM（HuggingFace 组织名 `XHToken`）开源的 4B 通用模型，Apache-2.0，同批还有 1.7B。它值得单独写一篇的原因不是「又一个小模型」，而是它把「单机跑 Agent」这条线上的取舍摆得特别清楚。

**但先说结论里最扎人的一条**：它的 GGUF 仓库里**只有一个 8.23GB 的未量化文件**，没有 Q4、没有 Q5、没有 Q8。想在 Mac 上舒服跑，你得自己量化。

> 📌 模型卡：https://huggingface.co/XHToken/Spark-X2.5-4B
> GGUF：https://huggingface.co/XHToken/Spark-X2.5-4B-GGUF
> Apache-2.0 ｜ 4,112,079,360 参数 ｜ BF16 ｜ 579 likes / 5477 下载（GGUF 另有 34104 下载）

---

## 榜单里那条清晰的分界线

模型卡里的对比表是自报的，但它自报的**形状**很有意思。我把 Spark-X2.5-4B 和 Qwen3.5-9B（一个大它一倍多的模型）拉出来对比：

**Agent 类——4B 大幅领先：**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B | 倍数 |
|---|---|---|---|
| τ³-bench | **30.4** | 9.3 | **3.3×** |
| BrowseComp | **40.9** | 8.3 | **4.9×** |
| MCP-Atlas | **54.6** | 47.4 | 1.15× |
| MCP-Mark | **14.2** | 13.4 | 1.06× |
| Workspace Bench | **31.2** | 25.5 | 1.22× |
| VitaBench2.0 | **25.2** | 15.6 | 1.62× |

**知识与通用类——4B 输：**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B |
|---|---|---|
| GPQA | 67.4 | **77.2** |
| HLE | 12.3 | **14.3** |
| AA-LCR | 56.3 | **63.0** |
| SWE-Bench Verified | 41.6 | **53.1** |
| BFCL-V4 | 65.1 | **66.1** |

**代码类——互有胜负：**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B |
|---|---|---|
| SWE-Bench Pro | **44.4** | 33.8 |
| SWE-Bench Multilingual | **53.3** | 43.3 |
| SWE-Bench Verified | 41.6 | **53.1** |

数学这一栏它也普遍领先：AIME 2026 拿 90.7，HMMT Feb 2026 拿 81.2，高考 2026（五套卷各 150 分）平均 133.4。

---

## 这个形状说明了什么？

**参数量决定「知道多少」，后训练决定「会不会干活」。**

GPQA、HLE 这类考的是模型肚子里存了多少知识——4B 装不下 9B 的知识量，输是必然的，也不丢人。

而 τ³-bench、BrowseComp、MCP-Atlas 这类考的是**多轮工具调用能不能走完**：会不会正确构造调用、会不会看懂返回、会不会在失败后换策略、会不会在第七步还记得第一步的目标。这些是可以靠后训练强化出来的**行为**，不完全依赖参数量。

BrowseComp 上 4.9 倍的差距尤其说明问题——那个榜考的是长链条的网页检索与信息整合，是纯粹的「流程能不能走完」。

**对本站读者的实际含义**：如果你要的是本地跑一个 Agent 干活（调工具、读文件、串流程），4B 这个档位现在是真的可用了，不必非上 9B/14B。但如果你要它当知识库问答，4B 就是不够。

模型卡也直说了它的适配对象：**Codex、Claude Code、OpenClaw、Hermes 四个 agent harness**。一个 4B 模型直接对着 harness 做适配，这在小模型里少见。

---

## 1M 上下文是怎么塞进 4B 的？

靠混合注意力：**1 层全注意力 + 3 层滑动窗口注意力（SWA）循环**。

全注意力管长程依赖但 KV-cache 随长度平方增长；SWA 的 cache 是常数级但看不远。四层里放一层全注意力，等于用 1/4 的全注意力开销换到接近全注意力的长程能力。

预训练约 20 万亿 token，另有专门的长上下文阶段，序列长度扩到 1M，用了数千亿 token。

**但「原生 1M」是标称值，不是你的机器能跑的值。** 上下文能开多长，取决于你有多少内存装 KV-cache，而不是模型声称支持多少。这是本文没有实测的部分（见下面缺口）。

---

## 那到底怎么在 Mac 上跑起来？

**这里是最需要泼冷水的一段。**

模型卡把兼容性写得很漂亮：支持 NVIDIA、华为、海光、后摩智能等硬件，兼容 vLLM、SGLang、llama.cpp、MLX，可通过 Ollama 和 LM Studio 快速部署，可用 LLaMA-Factory 微调。

我去查了实际发布的文件，情况没那么漂亮：

| 仓库 | 内容 | 用途 |
|---|---|---|
| `Spark-X2.5-4B` | BF16 safetensors，4.11B 参数 | transformers / 微调 |
| `Spark-X2.5-4B-GGUF` | **只有 1 个文件：`Spark-X2.5-4B.gguf`，8.23 GB** | llama.cpp / Ollama / LM Studio |
| `Spark-X2.5-4B-INT8` | INT8 权重 | vLLM / SGLang 服务端 |
| `Spark-X2.5-4B-FP8` | FP8 权重 | vLLM / SGLang 服务端（需较新 GPU）|

**8.23GB 对一个 4B 模型意味着它是未量化的**（4.11B × 2 bytes ≈ 8.2GB，正好是 BF16/F16）。也就是说：

- 官方 GGUF 没有 Q4_K_M、Q5_K_M、Q8_0 这些常规量化档
- 想在 16GB 内存的 Mac 上留出余量跑，得自己用 llama.cpp 的 `llama-quantize` 转
- INT8/FP8 那两个仓库是给 vLLM/SGLang 服务端用的，不是给 llama.cpp 用的

GGUF 仓库有 34104 次下载，是主仓库（5477）的 6 倍——说明大部分人是冲着本地跑来的，但拿到的是一个 8.23GB 的文件。

**这一条纠正我自己在选题清单里写的话**：我原本按仓库名判断它「量化全家桶备齐」，实际拉文件列表才发现 GGUF 只有未量化版。仓库名不等于文件内容。

官方给的 Quickstart 是 SGLang 的 Docker 镜像（`lmsysorg/sglang:nightly-dev-cu13-20260827-20621aa1`），面向 NVIDIA GPU，不是面向 Mac 的路径。

---

## 这家厂商是谁？

值得单独说一句，因为这影响你要不要花时间验证它。

- HuggingFace 组织名是 `XHToken`，但 fullname 是 **SparkLLM**，自我介绍是「开发通用基础模型和专业 AI Agent 产品，提供 Spark 模型家族以及 AStudio 和 Loomy 两套 harness 系统」
- 模型在**华为昇腾集群**上训练
- 硬件适配名单里有华为、海光、后摩智能
- 组织名和品牌名对不上，社交渠道铺得很齐（Slack / Discord / YouTube / dev.to / Bluesky / X / 知乎 / 微信）

**我没有查实它的主体归属。** 不是已知大厂的马甲就先当新面孔看——但 Apache-2.0 是真的，权重是真的，能不能用不取决于它是谁。

---

## 缺口：这篇文章没有实测

必须说清楚，本文**全部基于一手文件与模型卡，没有跑过这个模型**：

1. **所有 benchmark 都是厂商自报，无第三方复现。** 而且对比对象里带 `*` 的分数是从别人的模型卡/论文里抄的，不是同一套环境重跑的。这种比法对自己有利：自己的模型按自己最优参数跑，别人的取公开值。
2. **1M 上下文的真实显存曲线没数。** 在 M 系列上实际能开到多长、TTFT 和 tok/s 各是多少，全部未验证。
3. **MOPD 这个后训练方法没有论文可查。** 模型卡里说它把多个领域专家策略合并进单一可部署模型，但没有可核对的技术文档。
4. **没验证四个 agent harness 的适配效果。** 「深度集成 Codex / Claude Code / OpenClaw / Hermes」是模型卡的说法，工具调用成功率要实跑才知道。

下一篇如果做实测，重点会是：自己量化到 Q4_K_M 后在 MLX 和 llama.cpp 两条路上的显存/速度，以及挂进 Claude Code 跑真实任务的工具调用成功率。

---

## 一句话总结

Spark-X2.5-4B 最值得注意的不是分数高，是**分数的形状**：Agent 类大幅领先、知识类明确落后。这说明 4B 这个档位在「本地跑 Agent 干活」上已经跨过了可用线，代价是它不懂的东西比 9B 多。

至于部署，官方铺的路是 NVIDIA + SGLang；Mac 用户想跑，得自己从那个 8.23GB 的 GGUF 开始动手。

> 📌 模型卡：https://huggingface.co/XHToken/Spark-X2.5-4B
> GGUF（注意只有未量化版）：https://huggingface.co/XHToken/Spark-X2.5-4B-GGUF
> 1.7B 版本：https://huggingface.co/XHToken/Spark-X2.5-1.7B

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

A 4B model crushing a 9B on agent benchmarks while losing to it on knowledge benchmarks is not an anomaly — it is the fingerprint of **post-training aimed at agents**.

Spark-X2.5-4B is an Apache-2.0 4B general-purpose model from SparkLLM (HuggingFace org name `XHToken`), released alongside a 1.7B. It earns a post not because it is "another small model," but because it lays the trade-offs of "run an agent locally" out unusually clearly.

**The sharpest finding first**: its GGUF repo contains **exactly one 8.23GB unquantized file** — no Q4, no Q5, no Q8. To run it comfortably on a Mac, you quantize it yourself.

> 📌 Model card: https://huggingface.co/XHToken/Spark-X2.5-4B
> GGUF: https://huggingface.co/XHToken/Spark-X2.5-4B-GGUF
> Apache-2.0 ｜ 4,112,079,360 parameters ｜ BF16 ｜ 579 likes / 5,477 downloads (GGUF another 34,104)

---

## The clean dividing line in the benchmarks

The comparison table on the model card is self-reported, but its **shape** is what is interesting. Spark-X2.5-4B against Qwen3.5-9B, a model more than twice its size:

**Agent tasks — the 4B leads by a wide margin:**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B | Ratio |
|---|---|---|---|
| τ³-bench | **30.4** | 9.3 | **3.3×** |
| BrowseComp | **40.9** | 8.3 | **4.9×** |
| MCP-Atlas | **54.6** | 47.4 | 1.15× |
| MCP-Mark | **14.2** | 13.4 | 1.06× |
| Workspace Bench | **31.2** | 25.5 | 1.22× |
| VitaBench2.0 | **25.2** | 15.6 | 1.62× |

**Knowledge and general — the 4B loses:**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B |
|---|---|---|
| GPQA | 67.4 | **77.2** |
| HLE | 12.3 | **14.3** |
| AA-LCR | 56.3 | **63.0** |
| SWE-Bench Verified | 41.6 | **53.1** |
| BFCL-V4 | 65.1 | **66.1** |

**Code — mixed:**

| Benchmark | Spark-X2.5-4B | Qwen3.5-9B |
|---|---|---|
| SWE-Bench Pro | **44.4** | 33.8 |
| SWE-Bench Multilingual | **53.3** | 43.3 |
| SWE-Bench Verified | 41.6 | **53.1** |

Math also broadly favors it: AIME 2026 at 90.7, HMMT Feb 2026 at 81.2, and 133.4 average across the five 2026 Chinese Gaokao papers (150 points each).

---

## What does that shape tell us?

**Parameter count decides how much a model knows; post-training decides whether it can get work done.**

GPQA and HLE probe stored knowledge — a 4B cannot hold a 9B's worth, so losing is expected and unembarrassing.

τ³-bench, BrowseComp and MCP-Atlas probe whether **multi-turn tool use completes**: constructing calls correctly, parsing returns, switching strategy after a failure, still remembering the goal at step seven. Those are **behaviors** reinforceable through post-training, not strictly functions of parameter count.

The 4.9× gap on BrowseComp is the clearest case — that benchmark is long-chain web retrieval and synthesis, purely a question of whether the process finishes.

**What that means practically**: if you want an agent running locally that does work — calls tools, reads files, chains steps — the 4B tier is genuinely usable now; you do not need 9B or 14B. If you want a knowledge-QA box, 4B is not enough.

The model card names its targets outright: the **Codex, Claude Code, OpenClaw and Hermes** agent harnesses. A 4B model adapted directly against harnesses is rare at this size.

---

## How does a 4B fit a 1M context?

Hybrid attention: **one full-attention layer per three sliding-window (SWA) layers**.

Full attention handles long-range dependency but its KV-cache grows quadratically with length; SWA's cache is constant but short-sighted. One full-attention layer in four buys near-full-attention reach at a quarter of the cost.

Pretraining ran roughly 20 trillion tokens, with a dedicated long-context stage of hundreds of billions of tokens extending sequence length to 1M.

**But "native 1M" is a nameplate figure, not what your machine will run.** Usable context length depends on how much memory you have for the KV-cache, not on what the model claims to support. That is unverified here (see gaps).

---

## So how do you actually run it on a Mac?

**This is the section that needs cold water.**

The model card's compatibility claims are handsome: NVIDIA, Huawei, Hygon and HOUMO.AI hardware; vLLM, SGLang, llama.cpp and MLX; quick deployment through Ollama and LM Studio; fine-tuning via LLaMA-Factory.

The actual published files are less handsome:

| Repo | Contents | For |
|---|---|---|
| `Spark-X2.5-4B` | BF16 safetensors, 4.11B params | transformers / fine-tuning |
| `Spark-X2.5-4B-GGUF` | **One file: `Spark-X2.5-4B.gguf`, 8.23 GB** | llama.cpp / Ollama / LM Studio |
| `Spark-X2.5-4B-INT8` | INT8 weights | vLLM / SGLang serving |
| `Spark-X2.5-4B-FP8` | FP8 weights | vLLM / SGLang serving (newer GPUs) |

**8.23GB for a 4B model means it is unquantized** (4.11B × 2 bytes ≈ 8.2GB, exactly BF16/F16). Which means:

- No Q4_K_M, Q5_K_M or Q8_0 from the vendor
- Running it with headroom on a 16GB Mac requires converting it yourself via llama.cpp's `llama-quantize`
- The INT8/FP8 repos target vLLM/SGLang serving, not llama.cpp

The GGUF repo has 34,104 downloads — six times the main repo's 5,477 — so most people came for local inference and got a single 8.23GB file.

**This corrects something I wrote in my own shortlist**: I judged from repo names that the quantization matrix was complete; pulling the file list showed the GGUF is unquantized only. Repo names are not file contents.

The official quickstart is an SGLang Docker image (`lmsysorg/sglang:nightly-dev-cu13-20260827-20621aa1`) aimed at NVIDIA GPUs, not a Mac path.

---

## Who is the vendor?

Worth a paragraph, because it affects whether you spend time verifying.

- The HF org is `XHToken`, but its fullname is **SparkLLM**, self-described as building general-purpose foundation models and professional AI agent products, offering the Spark model family plus two harness systems, AStudio and Loomy
- Trained on **Huawei Ascend clusters**
- Hardware support list includes Huawei, Hygon and HOUMO.AI
- Org name and brand name do not match; social presence is thorough (Slack / Discord / YouTube / dev.to / Bluesky / X / Zhihu / WeChat)

**I did not verify corporate ownership.** Absent evidence it is a known vendor's alias, treat it as a new face — but the Apache-2.0 license is real and the weights are real, and usability does not depend on who they are.

---

## Gaps: this post contains no hands-on testing

Stated plainly — everything here comes from first-hand files and the model card, **without running the model**:

1. **Every benchmark is vendor-reported with no third-party reproduction.** Scores marked `*` for comparison models are lifted from other model cards and papers, not re-run in one environment. That comparison favors the author: their model at their best settings, everyone else at published values.
2. **No real memory curve for the 1M context.** Actual usable length on Apple Silicon, TTFT and tok/s are all unverified.
3. **MOPD, the post-training method, has no paper to check.** The card says it consolidates several domain-specialist policies into one deployable model, with no verifiable technical document.
4. **Harness compatibility is unverified.** "Deeply integrated with Codex / Claude Code / OpenClaw / Hermes" is the card's claim; tool-call success rates require actually running it.

If a follow-up does hands-on work, the focus will be: self-quantizing to Q4_K_M and measuring memory/speed on both MLX and llama.cpp, plus tool-call success rate on real tasks inside Claude Code.

---

## In one line

The notable thing about Spark-X2.5-4B is not that its scores are high but **the shape of those scores**: a large lead on agent tasks, a clear deficit on knowledge. The 4B tier has crossed the usability line for running agents locally, at the cost of knowing less than a 9B.

As for deployment, the paved road is NVIDIA plus SGLang; Mac users start by doing something themselves with that 8.23GB GGUF.

> 📌 Model card: https://huggingface.co/XHToken/Spark-X2.5-4B
> GGUF (note: unquantized only): https://huggingface.co/XHToken/Spark-X2.5-4B-GGUF
> 1.7B version: https://huggingface.co/XHToken/Spark-X2.5-1.7B

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
