---
title: "2B 打赢 4B：面壁 MiniCPM5-2B 拿下同级开源 SOTA，还把训练数据全开源了"
titleEn: "A 2B That Beats 4B Models: MiniCPM5-2B Takes Open-Source SOTA in Its Class — and Open-Sources the Training Data Too"
description: "MiniCPM5-2B 是一个 25 亿参数的稠密模型，原生 131072 上下文，为端侧和资源受限场景设计。在官方对比集里平均分 53.9，不仅是 2B 级开源 SOTA，还超过了所有列入对比的 4B 级模型（最高 51.1）。优势集中在代码推理、数学推理、长上下文、工具调用和 Agent 任务。同时开源了背后的四套训练数据集。"
descriptionEn: "MiniCPM5-2B is a 2.5B-parameter dense model with a native 131,072-token context, built for on-device and resource-constrained deployment. It averages 53.9 in the official comparison set — open-source SOTA for its class, and above every 4B-class model listed (top score 51.1). Its edge concentrates in code reasoning, math, long context, tool use and agentic tasks. The four training datasets behind it are open-sourced alongside."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Tech-News"
tags: ["MiniCPM", "端侧模型", "小模型", "local-first", "开源", "长上下文", "工具调用", "OpenBMB"]
heroImage: "../../assets/images/minicpm5-2b-on-device-sota-small-model-banner.jpg"
---

> 📌 模型地址：https://huggingface.co/openbmb/MiniCPM5-2B
> GitHub：https://github.com/OpenBMB/MiniCPM
> 在线体验：https://huggingface.co/spaces/openbmb/MiniCPM5-2B-Demo
> 协议：Apache-2.0 ｜ ❤ 672（2026-09-09）

## 一句话结论

**如果你在给端侧设备、旧笔记本、树莓派选模型，这个 2B 值得优先试。**

官方给的对比里，MiniCPM5-2B 平均分 **53.9**，在 2B 级里是开源 SOTA；更关键的是，**它超过了对比集中所有的 4B 级模型**——那批里最高分是 51.1。

## 参数与结构

| 项 | 值 |
|---|---|
| 类型 | 因果语言模型 |
| 架构 | 标准 `LlamaForCausalLM` |
| 参数量 | 2,516,756,480（约 25.2 亿）|
| 非嵌入参数 | 1,981,982,720（约 19.8 亿）|
| 层数 | 42 |
| 注意力头（GQA）| Q 16 头，KV 2 头 |
| 上下文长度 | **131,072** |

有两个细节值得注意。

**第一，架构是标准的 `LlamaForCausalLM`。** 这意味着几乎所有推理框架开箱即用，不需要等谁去适配一个自定义架构。对端侧部署来说这是很实际的优势——你不会卡在"我的框架不认识这个模型"上。

**第二，GQA 配置是 16 : 2。** 8 倍的 KV 压缩比，直接决定了长上下文时 KV cache 的内存占用。131K 上下文对 2B 模型来说是个很激进的配置，没有这个压缩比撑着，端侧根本吃不下。

## 成绩：越级打怪

对比集包括同级的 **LFM2.5-2.6B**、**Qwen3.5-2B**、**Gemma-4-E2B-it**，以及作为参照列出的更大模型：**Qwen3.5-4B**、**granite-4.2-3B**、**Nemotron-3-Nano-4B**、**Gemma-4-E4B-it**、**LFM2.5-8B-A1B**。

结果：MiniCPM5-2B 平均 **53.9**，2B 级 SOTA，且**高于所列全部更大模型**（最高 51.1）。

官方点名的优势领域是：**代码推理、数学推理、长上下文理解、工具使用、多项 Agent 任务**。

这个优势分布很有意思——**恰好是把小模型真正用起来所需要的那几项能力**。端侧模型的现实用法很少是"陪你聊天"，更多是：读一份长文档回答问题、调用几个本地工具完成一个流程、跑一段代码逻辑。闲聊能力强但工具调用不行的小模型，在 Agent 场景里是没法用的。

需要说明：**这是官方在自选对比集里的评测结果**。对比集选的都是有分量的对手，但换一套基准、换一批对手，排名可能变化。当成"这个尺寸档位里第一梯队"来理解比当成"绝对第一"更稳妥。

## 一次发布，一整排格式

这可能是这次发布里最实在的部分——不是丢一个 BF16 权重让你自己想办法：

**MiniCPM5-2B 全家**

| 版本 | 用途 |
|---|---|
| `MiniCPM5-2B` | BF16 最终版（RL + OPD 后训练）|
| `MiniCPM5-2B-SFT` | 仅 SFT 检查点（RL/OPD 之前）|
| `MiniCPM5-2B-Midtrain` | 中期训练检查点（SFT 之前）|
| `MiniCPM5-2B-Base` | 基座检查点（仅预训练）|
| **`MiniCPM5-2B-GGUF`** | **llama.cpp / Ollama / LM Studio** |
| **`MiniCPM5-2B-MLX`** | **MLX / 4bit，Apple Silicon** |
| `MiniCPM5-2B-GPTQ` | GPTQ / 4bit 量化 |
| `MiniCPM5-2B-DSpark` | DSpark 草稿模型，用于推理加速 |
| `MiniCPM5-2B-LiteRT` | LiteRT-LM 版本 |

还有更小的 **MiniCPM5-1B** 系列（BF16 / SFT / Base / GGUF / MLX）。

**GGUF 和 MLX 在首发就给了**，这一点对本地用户意义很大——不用等社区量化，也不用担心量化质量参差。国内用户还有 ModelScope 镜像，每个版本都有对应链接。

把中间检查点（Base / Midtrain / SFT）也全部放出来，是对研究者友好的做法：想研究 RL 和 OPD 到底带来了什么，可以直接拿前后两个检查点对比。

## 训练数据也开源了

这部分在小模型发布里比较少见。随模型一起放出的是 **UltraData** 家族：

| 数据集 | 内容 |
|---|---|
| **UltraX-Preview** | 高质量网页预训练数据集 |
| **UltraData-Code** | 带 L0-L3 分层管理的代码数据，官方说这是编码能力大幅提升的来源 |
| **UltraData-SFT-Agent-2609** | 50 万条 Agent 训练样本，用于端侧 Agent 能力 |
| **UltraData-RL-2609** | 8 万+ 条高质量 RL 训练样本，覆盖数学、代码、通用知识、长上下文推理 |

model card 的 frontmatter 里还列了 `Ultra-FineWeb`、`Ultra-FineWeb-L3`、`UltraData-Math`、`UltraData-SFT-2605` 等。

**代码数据的 L0-L3 分层**这个说法值得留意——官方把编码能力的跃升归因于此。数据分层管理（按质量/复杂度分级投喂）是目前提升小模型专项能力的主流手段之一，把整套数据开源出来，等于把方法也交出来了。

## 端侧部署怎么算这笔账

以 2.52B 参数估算：

| 精度 | 权重体积（约）| 什么设备能跑 |
|---|---|---|
| BF16 | ~5 GB | 8GB+ 内存，宽裕 |
| GGUF Q4_K_M | ~1.6 GB | 树莓派 5、旧笔记本、手机 |
| MLX 4bit | ~1.5 GB | 任何 Apple Silicon Mac |

但**光看权重体积会低估内存需求**——131K 上下文的 KV cache 是另一笔开销。好在 GQA 16:2 的配置把这块压得很紧：KV 头只有 2 个，相比 MHA 省了 8 倍。真要跑满 131K，还是建议开 KV cache 量化（llama.cpp 的 `-ctk`/`-ctv`）。

日常用法上，把上下文设到 8K-32K 通常就够，内存占用会舒服很多。131K 是能力上限，不是推荐日常值。

## 适合什么、不适合什么

**适合：**

- **端侧 Agent** —— 官方专门用 50 万条 Agent 样本训练过，工具调用是重点优化项
- **长文档处理** —— 131K 原生上下文，在这个尺寸里很少见
- **代码辅助** —— 官方点名的优势项，有 L0-L3 分层代码数据支撑
- **资源受限部署** —— 树莓派、老设备、手机、需要离线的场景

**不适合：**

- **需要广博世界知识的场景** —— 25 亿参数装不下太多事实，该配 RAG 就得配
- **复杂多步推理** —— 虽然数学推理是强项，但和 30B+ 模型仍有量级差距
- **中英之外的语言** —— model card 只声明了 `en` 和 `zh`

## 一个更大的判断

MiniCPM5-2B 这类模型的意义，不在于它能不能取代云端大模型——**取代不了，也不该按这个标准评价它**。

它的意义在于**把"能用"的门槛压到了一台普通设备的水平**。一个能在树莓派上跑、能调工具、能读长文档、还能写代码的 2B 模型，让一大类原本必须联网的应用变成可以完全本地化：处理敏感文档、离线环境作业、不想让数据出设备的场景。

对个体和中小组织来说，这条线比"云端模型又强了多少"要重要得多——**前者决定了你能不能自主，后者只决定你的服务商能给你什么**。

从这个角度看，同时开源训练数据的动作也更有分量：它让后来者能在同一套数据上继续往前做，而不是只能用别人练好的成品。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Model: https://huggingface.co/openbmb/MiniCPM5-2B
> GitHub: https://github.com/OpenBMB/MiniCPM
> Live demo: https://huggingface.co/spaces/openbmb/MiniCPM5-2B-Demo
> License: Apache-2.0 ｜ ❤ 672 (2026-09-09)

## The Short Version

**If you're choosing a model for edge devices, old laptops, or a Raspberry Pi, try this 2B first.**

In the official comparison, MiniCPM5-2B averages **53.9** — open-source SOTA in the 2B class. More notably, **it beats every 4B-class model in that comparison set**, where the top score is 51.1.

## Parameters and Architecture

| Item | Value |
|---|---|
| Type | Causal language model |
| Architecture | Standard `LlamaForCausalLM` |
| Parameters | 2,516,756,480 (~2.52B) |
| Non-embedding parameters | 1,981,982,720 (~1.98B) |
| Layers | 42 |
| Attention heads (GQA) | 16 for Q, 2 for KV |
| Context length | **131,072** |

Two details deserve attention.

**One: the architecture is a standard `LlamaForCausalLM`.** Nearly every inference framework runs it out of the box, with no waiting for someone to add support for a custom architecture. For edge deployment that's a very practical advantage — you won't get stuck on "my framework doesn't recognize this model."

**Two: the GQA ratio is 16:2.** That 8x KV compression directly determines KV cache memory at long context. A 131K window on a 2B model is an aggressive configuration; without that compression ratio, edge devices simply couldn't hold it.

## Results: Punching Above Its Weight

The comparison set includes same-class **LFM2.5-2.6B**, **Qwen3.5-2B**, and **Gemma-4-E2B-it**, plus larger models listed for reference: **Qwen3.5-4B**, **granite-4.2-3B**, **Nemotron-3-Nano-4B**, **Gemma-4-E4B-it**, and **LFM2.5-8B-A1B**.

Result: MiniCPM5-2B averages **53.9**, SOTA for its class, and **above every larger model listed** (top: 51.1).

The officially named strengths: **code reasoning, math reasoning, long-context understanding, tool use, and multiple agentic tasks**.

That distribution is interesting — it's **exactly the capability set you need to actually put a small model to work**. Real edge deployments are rarely "chat with me." They're closer to: read a long document and answer, call a few local tools to finish a flow, run through some code logic. A small model that converses well but can't call tools is unusable in an agent setting.

To be clear: **these are the vendor's own results on a comparison set they chose**. The opponents are serious ones, but a different benchmark suite and a different peer group could reorder things. "First tier at this size" is a safer reading than "unambiguously first."

## One Release, a Full Rack of Formats

This may be the most practical part of the release — not a lone BF16 checkpoint leaving you to figure it out:

**The MiniCPM5-2B family**

| Version | Purpose |
|---|---|
| `MiniCPM5-2B` | BF16 final release (post-trained with RL + OPD) |
| `MiniCPM5-2B-SFT` | SFT-only checkpoint (before RL / OPD) |
| `MiniCPM5-2B-Midtrain` | Mid-training checkpoint (before SFT) |
| `MiniCPM5-2B-Base` | Base checkpoint (pre-training only) |
| **`MiniCPM5-2B-GGUF`** | **llama.cpp / Ollama / LM Studio** |
| **`MiniCPM5-2B-MLX`** | **MLX / 4bit for Apple Silicon** |
| `MiniCPM5-2B-GPTQ` | GPTQ / 4bit quantized |
| `MiniCPM5-2B-DSpark` | DSpark draft model for inference acceleration |
| `MiniCPM5-2B-LiteRT` | The LiteRT-LM build |

There's also a smaller **MiniCPM5-1B** line (BF16 / SFT / Base / GGUF / MLX).

**GGUF and MLX ship on day one**, which matters a lot for local users — no waiting on community quantizations, no worrying about their quality. Chinese users get ModelScope mirrors for every version.

Publishing the intermediate checkpoints (Base / Midtrain / SFT) is researcher-friendly: if you want to study what RL and OPD actually contributed, you can diff the checkpoints directly.

## The Training Data Is Open Too

Uncommon for a small-model release. Shipping alongside is the **UltraData** family:

| Dataset | Contents |
|---|---|
| **UltraX-Preview** | High-quality web pre-training dataset |
| **UltraData-Code** | Code data with L0-L3 tiered management, credited by the team for the coding leap |
| **UltraData-SFT-Agent-2609** | 500K agent training samples for on-device agent capability |
| **UltraData-RL-2609** | 80K+ high-quality RL samples covering math, code, general knowledge, long-context reasoning |

The card's frontmatter also lists `Ultra-FineWeb`, `Ultra-FineWeb-L3`, `UltraData-Math`, and `UltraData-SFT-2605`.

The **L0-L3 tiering of code data** is worth noting — the team attributes the coding jump to it. Tiered data curation (feeding by quality/complexity level) is one of the main levers for lifting a small model's specialist ability right now, and open-sourcing the whole set effectively hands over the method too.

## Doing the Edge-Deployment Math

Estimating from 2.52B parameters:

| Precision | Approx. weights | What can run it |
|---|---|---|
| BF16 | ~5 GB | 8GB+ RAM, comfortable |
| GGUF Q4_K_M | ~1.6 GB | Raspberry Pi 5, old laptops, phones |
| MLX 4bit | ~1.5 GB | Any Apple Silicon Mac |

But **weight size alone understates memory** — the KV cache at 131K context is a separate bill. The 16:2 GQA ratio keeps it tight (only 2 KV heads, 8x less than MHA), but if you genuinely intend to fill 131K, enable KV cache quantization (`-ctk`/`-ctv` in llama.cpp).

For everyday use, 8K-32K context is usually plenty and much easier on memory. 131K is the ceiling, not the recommended default.

## Where It Fits, and Where It Doesn't

**Fits:**

- **On-device agents** — specifically trained on 500K agent samples; tool calling is a focus area
- **Long documents** — a native 131K context is rare at this size
- **Coding assistance** — a named strength, backed by the L0-L3 tiered code data
- **Resource-constrained deployment** — Raspberry Pi, older hardware, phones, anything that must work offline

**Doesn't fit:**

- **Broad world knowledge** — 2.5B parameters can't store that many facts; pair it with RAG where that matters
- **Complex multi-step reasoning** — math is a strength, but there's still an order-of-magnitude gap to 30B+ models
- **Languages beyond Chinese and English** — the card declares only `en` and `zh`

## The Larger Point

The significance of a model like MiniCPM5-2B isn't whether it can replace a frontier cloud model. **It can't, and judging it by that standard misses the point.**

Its significance is that it **drops the threshold for "good enough" down to ordinary hardware**. A 2B model that runs on a Raspberry Pi, calls tools, reads long documents and writes code turns a whole class of previously network-dependent applications into fully local ones: handling sensitive documents, working in offline environments, any case where data shouldn't leave the device.

For individuals and small organizations, that line matters far more than how much stronger the frontier models got — **the former decides whether you can be self-sufficient; the latter only decides what your vendor is willing to give you**.

Seen that way, open-sourcing the training data carries extra weight: it lets others build forward on the same corpus, rather than only consuming someone else's finished weights.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
