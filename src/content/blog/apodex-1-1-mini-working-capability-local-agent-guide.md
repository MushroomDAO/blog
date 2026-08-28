---
title: "Apodex 1.1 Mini 调研：训「持续干活的能力」，不是训「聊得更像」，35B 本地可跑"
titleEn: "Apodex 1.1 Mini: Training 'Working Capability,' Not Chattiness — a 35B Model You Can Run Locally"
description: "调研 Apodex/Apodex-1.1-mini：Qwen3.5-35B-A3B（256 专家/8 激活，约 3B 激活参数）的 Agent 微调版，Apache-2.0，图文输入文本输出，中英双语。配套论文 arXiv:2608.23283 提出「working capability」概念——不是比谁推理更强，而是比谁能在文件/搜索/代码环境里持续干活、失败后能恢复、最终交付可验证的结果。训练分两条线：Environment Scaling（扩展可验证的可执行环境多样性）和 Agentic Coordination Scaling（训练拆解长任务、并行委派、整合异步结果、重新规划）。Mini 版本被明确定位为「可本地部署」的那个变体。社区已有 MLX 4/5/6/8-bit、GGUF、NVFP4、GPTQ-Int4 等多种量化版本。"
descriptionEn: "A deep dive into Apodex/Apodex-1.1-mini: an agentic finetune of Qwen3.5-35B-A3B (256 experts, 8 active per token, ~3B active parameters), Apache-2.0, image-text-to-text, bilingual en/zh. Its paper (arXiv:2608.23283) introduces 'working capability' — not who reasons best, but who can sustain progress in file/search/code environments, recover from failure, and deliver verifiable results over time. Training runs along two axes: Environment Scaling (diversifying verifiable executable environments) and Agentic Coordination Scaling (decomposing long-horizon tasks, delegating parallel work, integrating asynchronous results, replanning). The Mini variant is explicitly positioned as the locally-deployable one. The community has already produced MLX (4/5/6/8-bit), GGUF, NVFP4, and GPTQ-Int4 quantizations."
pubDate: "2026-08-28"
updatedDate: "2026-08-28"
category: "Tech-News"
tags: ["AI Agent", "开源模型", "MoE", "本地部署", "Qwen3.5", "Apple Silicon", "MLX", "多模态"]
heroImage: "../../assets/images/apodex-1-1-mini-working-capability-local-agent-guide-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

模型：apodex/Apodex-1.1-mini | 基座：Qwen/Qwen3.5-35B-A3B | Apache-2.0
论文：arXiv:2608.23283 | HuggingFace 下载 1306 · 点赞 95（截至发文，是个还没被刷屏的小项目）

---

## 一句话结论

Apodex 1.1 这篇论文没有去卷「推理能力」这个已经卷烂的赛道，而是提出了一个叫 **working capability（持续干活的能力）** 的评价维度：不是模型能不能想明白，而是能不能在真实的文件系统、搜索、代码环境里**持续推进**一个目标，中途失败了能不能恢复，最后交付的结果能不能被验证。Apodex-1.1-mini 是这套训练方法产出的、专门给本地部署用的 35B 版本。

## 为什么不是"套壳"

先说清楚这次调研最想确认的问题：这是不是又一个"基座模型 + 身份 prompt"的马甲项目？读完论文摘要，答案是否定的——它确实有具体的训练方法论，不是纯粹的系统提示词包装。

论文把训练拆成两条互补的线：

**Environment Scaling（环境扩展）**：扩大可执行、可验证的文件/搜索/代码环境的多样性。关键词是"可验证"——不是让模型在模拟环境里瞎练，而是训练环境本身要能给出客观的成功/失败信号。

**Agentic Coordination Scaling（协同能力扩展）**：训练模型拆解长周期任务、把并行的工作委派出去、整合异步返回的结果、根据新信息重新规划。这几个动作合起来，就是"一个人管理一个项目"和"一个人只会回答问题"之间的区别。

论文里还提到一个共享的执行框架（execution harness）和一个叫 **AgentOS** 的东西，负责在多个工具和多个 agent 之间维护任务状态和执行溯源（provenance）。这个思路和本站之前调研过的 HugAgentOS（浙大做的企业级 AgentOS，用领域本体做 Agent 推理的控制平面）方向类似——"给 Agent 一个操作系统级别的状态管理层"正在变成一个独立的研究方向，值得持续关注。

论文摘要给的评测范围覆盖专业工作、金融、科研、数学、编程、搜索六个领域，声称在模型规模明显小于很多前沿系统的情况下达到了"leading performance band"（第一梯队水平）。**需要说明的是**：论文摘要里没有给出具体的跑分数字，这是一个真实的研究缺口——本文没有拿到独立的第三方评测数据，上面这句"达到第一梯队"目前只是论文自己的表述，没有交叉验证。

## 模型本身：35B 总参数，约 3B 激活

Apodex-1.1-mini 微调自 Qwen/Qwen3.5-35B-A3B，架构细节（从基座模型 config.json 里拉的）：

| 项目 | 数值 |
|---|---|
| 总参数 | 35B |
| 专家数 | 256 |
| 每 token 激活专家数 | 8 |
| hidden_size | 2048 |
| 层数 | 40 |
| 词表大小 | 248,320 |

8/256 的激活比例，对应"A3B"里的约 3B 激活参数量级——这决定了它的推理成本更接近一个 3B 稠密模型，而不是 35B 稠密模型，这也是它能被叫做"本地可部署"的物理基础。

模态上是图文输入、文本输出（image-text-to-text），中英双语。协议 Apache-2.0（HuggingFace 页面 license tag 确认），比较宽松，商用不受限。

有一个细节值得注意：模型自带一个写死的身份注入机制——chat template 里默认会在 system prompt 里插入"你是 Apodex，Apodex AI 开发"这类身份声明（可以通过 `identity_mode` 参数关掉）。这本身不是训练方法论的一部分，只是产品化包装，不影响上面对训练方法的判断。

## 本地部署：量化生态已经跑起来了

发布没多久，社区量化版本已经相当齐全，这是判断一个模型"活不活跃"的直接信号：

| 类型 | 仓库 | 下载 |
|---|---|---|
| 官方 NVFP4 | apodex/Apodex-1.1-mini-NVFP4 | 1204 |
| 官方 FP8 | apodex/Apodex-1.1-mini-FP8 | 280 |
| 官方 GPTQ-Int4 | apodex/Apodex-1.1-mini-GPTQ-Int4 | 266 |
| GGUF（社区） | bartowski/apodex_Apodex-1.1-mini-GGUF | 1909 |
| GGUF（社区） | abenzerps/Apodex-1.1-mini-GGUF | 3091 |
| MLX 4/5/6/8-bit（社区） | nicolasembleton/Apodex-1.1-mini-MLX-*bit | 41～314 |

**对 Apple Silicon 用户最直接相关的是 MLX 系列**——nicolasembleton 已经放出 4/5/6/8-bit 四档量化，6-bit 那档下载量最高（300），是精度/体积的常见甜点位。粗估显存/内存占用（按激活的 ~3B 参数估算，MoE 模型的权重仍要整体加载，只是计算量按激活参数算）：

- 全精度权重整体加载需要的磁盘/内存空间以 35B 总参数为基准，bf16 约 70GB
- 8-bit 量化约 35GB，6-bit 约 26GB，4-bit 约 18GB

这几个数字是按参数量线性估算的粗略值，不是实测——本文没有在本地机器上实际跑一遍量化版本记录真实内存占用和 tok/s，这是需要读者自己验证或本站后续跟进实测的缺口。

## 放进本站的坐标系里看

本站最近覆盖的同量级本地模型（ling-3-0-tiny 的边缘 MoE、GLM-5.3-Flash 的 321B/18B 激活）都是通用语言模型 + 多模态能力的路线，卖点是"参数效率"。Apodex-1.1-mini 的卖点维度不一样：它不是在同一个"参数效率"赛道里比谁更小更快，而是在"任务持续执行能力"这个新维度上给出一个可本地部署的答案。这两条线其实互补——同样的量化技术栈（MLX/GGUF）可以套在任何一类模型上，但训练目标决定了模型适合干什么活。

如果你的场景是"我需要一个能一直盯着一个多步骤任务、能从失败里恢复、本地就能跑"的东西，Apodex-1.1-mini 目前看起来是这个方向上少数有公开论文支撑、有活跃量化生态、参数量级适合单机部署的选项之一。如果你只是想要一个聊天更聪明的本地小模型，它可能不是最优选择——它的训练重点不在这里。

## 缺口

- 论文摘要没给出具体跑分，"leading performance band" 目前只是论文自己的表述
- 没有实测本地量化版本的显存占用和 tok/s，上面的数字是估算
- AgentOS 具体怎么维护跨工具/跨 agent 的状态和溯源，摘要没展开，需要看论文正文（本文只读了摘要，没有拿到全文）

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Model: apodex/Apodex-1.1-mini | Base: Qwen/Qwen3.5-35B-A3B | Apache-2.0
Paper: arXiv:2608.23283 | HuggingFace downloads 1,306 · likes 95 (as of writing — still under the radar)

---

## TL;DR

Apodex 1.1's paper skips the already-crowded "reasoning benchmark" race and instead proposes an evaluation axis it calls **working capability**: not whether a model can figure things out, but whether it can sustain progress toward a real-world goal inside actual file, search, and code environments — recovering from failure along the way and delivering a verifiable result at the end. Apodex-1.1-mini is the 35B variant of that training recipe, explicitly built for local deployment.

## Is this just a wrapper?

The question this research set out to answer first: is this another "base model plus an identity system prompt" repackaging job? Having read the abstract, the answer is no — there's a concrete training methodology here, not just prompt dressing.

The paper splits training into two complementary axes:

**Environment Scaling** — expanding the diversity of executable, *verifiable* file/search/code environments. The key word is verifiable: the training environments themselves need to produce objective success/failure signals, not just simulated busywork.

**Agentic Coordination Scaling** — training the model to decompose long-horizon tasks, delegate parallel work, integrate asynchronous results, and replan as new information arrives. Together, these are the difference between "a person who manages a project" and "a person who only answers questions."

The paper also describes a shared execution harness and something called **AgentOS**, which maintains task state and provenance across tools and agents. This echoes a direction we covered before on this blog — HugAgentOS (Zhejiang University's enterprise AgentOS, using domain ontologies as the control plane for agent reasoning): giving agents an OS-level state-management layer is becoming its own research thread worth tracking.

The abstract claims Apodex 1.1 reaches "the leading performance band" across professional work, finance, science, math, coding, and search, despite using a substantially smaller model than many frontier systems. **Caveat**: the abstract doesn't include concrete benchmark numbers, which is a real research gap — this article has no independent third-party evaluation data, so "leading performance band" is currently only the paper's own characterization, unverified against outside numbers.

## The model itself: 35B total, ~3B active

Apodex-1.1-mini is finetuned from Qwen/Qwen3.5-35B-A3B. Architecture details pulled directly from the base model's config.json:

| Field | Value |
|---|---|
| Total parameters | 35B |
| Experts | 256 |
| Active experts per token | 8 |
| Hidden size | 2048 |
| Layers | 40 |
| Vocab size | 248,320 |

An 8-of-256 activation ratio puts the active parameter count at roughly the "A3B" ballpark — around 3B. That's the physical basis for calling it "locally deployable": inference cost tracks closer to a 3B dense model than a 35B dense one.

Modality is image-text-to-text (image input, text output), bilingual en/zh. License is Apache-2.0 (confirmed via the HuggingFace license tag) — permissive, no commercial restriction.

One detail worth flagging: the model ships a hardcoded identity-injection mechanism — the chat template by default inserts a system-prompt block declaring "You are Apodex, developed by Apodex AI" (toggleable via an `identity_mode` parameter). This is product packaging, not part of the training methodology, and doesn't change the assessment above.

## Local deployment: the quantization ecosystem is already live

Shortly after release, community quantizations are already fairly complete — a direct signal of how active a model release actually is:

| Type | Repo | Downloads |
|---|---|---|
| Official NVFP4 | apodex/Apodex-1.1-mini-NVFP4 | 1,204 |
| Official FP8 | apodex/Apodex-1.1-mini-FP8 | 280 |
| Official GPTQ-Int4 | apodex/Apodex-1.1-mini-GPTQ-Int4 | 266 |
| Community GGUF | bartowski/apodex_Apodex-1.1-mini-GGUF | 1,909 |
| Community GGUF | abenzerps/Apodex-1.1-mini-GGUF | 3,091 |
| Community MLX 4/5/6/8-bit | nicolasembleton/Apodex-1.1-mini-MLX-*bit | 41–314 |

**Most directly relevant to Apple Silicon readers**: nicolasembleton has shipped 4/5/6/8-bit MLX quants; 6-bit has the most downloads (300), a common sweet spot for precision vs. size. Rough memory footprint estimates (based on the ~3B active parameters for compute, but the full MoE weight set still needs to be loaded regardless of activation):

- Full-precision weights at bf16: roughly 70GB
- 8-bit: roughly 35GB, 6-bit: roughly 26GB, 4-bit: roughly 18GB

These are linear estimates from parameter count, not measured numbers — this article did not actually run a quantized build locally to record real memory usage or tokens/sec. That verification is left to the reader, or to a future hands-on follow-up from this blog.

## Where this sits in what we've covered

Recent local models covered here (ling-3-0-tiny's edge MoE, GLM-5.3-Flash's 321B/18B-active) are general-purpose language + multimodal models competing on parameter efficiency. Apodex-1.1-mini isn't competing on that axis at all — it's offering a locally-deployable answer on a different dimension: sustained task-execution capability. The two lines are actually complementary — the same quantization stack (MLX/GGUF) applies to either kind of model, but the training objective determines what the model is actually good for.

If your use case is "something that stays on a multi-step task, recovers from failure, and runs locally," Apodex-1.1-mini currently looks like one of the few options in that specific direction backed by a public paper, an active quantization ecosystem, and a parameter count that fits on a single machine. If you just want a smarter local chat model, it may not be the best pick — that's not what its training optimized for.

## Gaps

- The abstract gives no concrete benchmark numbers; "leading performance band" is currently only the paper's own claim
- No local benchmarking of quantized builds' memory footprint or tokens/sec — the numbers above are estimates
- How AgentOS actually maintains cross-tool/cross-agent state and provenance isn't detailed in the abstract; that needs the full paper, which this article did not obtain

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
