---
title: "27B 模型压到 11.8GB 还「任务无损」：奥地利 IST 用两篇论文的方法重做了 GGUF 量化"
titleEn: "A 27B Model at 11.8GB, Task-Lossless: IST Austria Rebuilt GGUF Quantization With Two Papers' Worth of Method"
description: "均匀量化对所有张量一视同仁，GSQ-RCO 不是——它用梯度搜索按每个张量的敏感度分配精度，在总大小预算内做非均匀分配。结果：Qwen3.8-27B 从 53.8GB 压到 11.8GB（4.6 倍），AIME25 和 LiveCodeBench 分数与 BF16 原模型完全一致。文件是标准 GGUF，llama.cpp、Ollama、LM Studio 直接跑。"
descriptionEn: "Uniform quantization treats every tensor the same. GSQ-RCO doesn't — it uses gradient-based search to allocate precision by per-tensor sensitivity under a total size budget. Result: Qwen3.8-27B goes from 53.8GB to 11.8GB (4.6x) while exactly matching the BF16 baseline on AIME25 and LiveCodeBench v6. The files are standard GGUF and run unmodified in llama.cpp, Ollama and LM Studio."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Research"
tags: ["量化", "GGUF", "本地推理", "local-first", "Qwen", "开源模型", "llama.cpp", "IST Austria"]
heroImage: "../../assets/images/gsq-rco-non-uniform-gguf-quantization-banner.jpg"
---

> 📌 模型地址：https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF
> GSQ 论文：arXiv:2604.18556 ｜ 代码：https://github.com/IST-DASLab/GSQ
> RCO 论文：arXiv:2605.00649 ｜ 代码：https://github.com/IST-DASLab/RCO
> 协议：Apache-2.0 ｜ ❤ 655 ｜ ⬇ 479,597（2026-09-09）

## 一句话结论

**一台 16GB 内存的机器，现在可以跑一个基本没有损失的 27B 模型。**

这不是又一个"量化后感觉还行"的说法。IST-DASLab 给的是可核对的数字：IQ3_S 档在 **AIME25 上得分 100.00**、**LiveCodeBench v6 上 85.71**，与 BF16 原模型**完全一致**，GPQA-Diamond 差 0.51 分。文件大小 **11.8GB**，原模型 53.8GB。

## 均匀量化漏掉了什么

现在主流的 GGUF 量化——你熟悉的 Q4_K_M、Q5_K_S 这些——本质上是**对整个模型的所有权重张量用同一个量化类型**。

问题在于：**模型里的张量并不同等重要。**

有些张量对精度极其敏感，掉两个 bit 输出就开始胡说；有些张量非常宽容，压到 2 bit 影响也不大。均匀量化对这个差异视而不见，结果是**为了保护最敏感的那几个张量，所有张量都被迫用更高的精度**——这是纯粹的浪费。

GSQ-RCO 的做法是给每个张量单独分配量化类型，分配方案由**梯度搜索**得出，按每个张量的敏感度分配精度，同时受总大小预算约束。

## 两个方法各管一段

| 方法 | 干什么 |
|---|---|
| **GSQ**（Gumbel-Softmax Quantization）| 训练后标量量化：通过 Gumbel-Softmax 松弛，**联合学习**每个坐标的网格分配和每组的缩放系数。在 2-3 bit 区间把标量量化和向量量化之间的差距大部分抹平，同时保持在 GGUF 这种标准标量格式里可部署 |
| **RCO**（Riemannian Constrained Optimization）| 在总大小预算下，为 N 个张量各分配 K 种量化类型之一。把预算约束重构成 logit 空间里的一个**光滑黎曼流形**，于是可以直接对任务损失做梯度优化，同时**精确**满足预算，不需要针对约束调超参 |

拆开看：**GSQ 负责"给定一个量化类型，把这个张量量化得尽可能准"，RCO 负责"在总预算下，每个张量该用哪个类型"**。两者合起来产出一个指定大小的非均匀 GGUF。

两个方法都出自奥地利科学技术研究所（IST Austria）的 Deep Algorithms and Systems Lab（DASLab）——就是做出 GPTQ 的那个实验室。

## 数字

四个档位，加一个视觉投影器：

| 文件 | bpw | 大小 | 说明 |
|---|---|---|---|
| `IQ2_XS` | 2.50 | 8.4 GB | 最小；零样本反而高于 BF16 基线 |
| `IQ2_S` | 2.75 | 9.3 GB | AIME25 追平原模型 |
| `IQ3_XXS` | 3.00 | 10.1 GB | 全能操作点 |
| `IQ3_S` | 3.50 | 11.8 GB | **推荐；任务无损** |
| `mmproj-BF16` | 16 | 0.9 GB | 视觉编码器 + 投影器，多模态用 |

完整评测表（wiki/c4/fw 是困惑度，越低越好；其余越高越好）：

| 变体 | bpw | GB | wiki↓ | c4↓ | fw↓ | 零样本均值↑ | 恢复率 | AIME25↑ | GPQA-D↑ | LCB v6↑ |
|---|---|---|---|---|---|---|---|---|---|---|
| BF16 | 16.00 | 53.8 | 7.05 | 11.45 | 8.14 | 74.34 | 100.0% | 100.00 | 89.90 | 85.71 |
| **GSQ-RCO IQ2_XS** | 2.50 | 8.4 | 7.69 | 12.98 | 9.19 | 74.54 | 100.3% | 96.67 | 84.85 | 76.57 |
| **GSQ-RCO IQ2_S** | 2.75 | 9.3 | 7.39 | 12.40 | 8.80 | **75.70** | **101.8%** | 100.00 | 86.36 | 82.29 |
| **GSQ-RCO IQ3_XXS** | 3.00 | 10.1 | 7.20 | 12.13 | 8.59 | 74.81 | 100.6% | 100.00 | 88.89 | 84.57 |
| **GSQ-RCO IQ3_S** | 3.50 | 11.8 | **7.07** | 11.76 | 8.34 | 74.47 | 100.2% | **100.00** | 89.39 | **85.71** |
| UD-IQ2_S | 2.49 | 8.4 | 8.02 | 12.78 | 9.08 | 73.80 | 99.3% | 86.67 | 76.26 | 72.00 |
| UD-Q2_K_XL | 2.88 | 9.8 | 7.54 | 12.25 | 8.69 | 74.37 | 100.0% | 100.00 | 86.87 | 82.28 |
| UD-IQ3_S | 3.52 | 12.0 | 7.16 | 11.75 | 8.34 | 75.49 | 101.5% | 96.67 | **89.90** | 84.00 |

（UD = Unsloth Dynamic，目前社区里质量口碑最好的动态量化之一，是很硬的对手。）

### 三个值得注意的点

**第一，同等文件大小下的差距非常大。** 8.4GB 这一档，GSQ-RCO IQ2_XS 对 UD-IQ2_S：**AIME25 领先 10.00 分，GPQA-Diamond 领先 8.59 分，LiveCodeBench v6 领先 4.57 分**。同样的磁盘占用，推理任务上的差距是断崖式的。

**第二，2.5 bit 的零样本分数超过了 BF16 原模型**（74.54 vs 74.34，恢复率 100.3%），2.75 bit 更是到 101.8%。

这个现象要正确理解：**这不代表量化让模型变聪明了**。零样本任务（arc_easy、arc_challenge、hellaswag、winogrande、piqa）分数本身有噪声，量化引入的扰动偶尔会在这类基准上碰巧有利。真正说明问题的是右边三列推理和生成基准——那里 IQ2_XS 是明确低于 BF16 的（96.67 / 84.85 / 76.57）。

**恢复率超过 100% 是个提醒：不要只看零样本均值来判断量化质量。**

**第三，3.0 bit 就已经追平 AIME25 了。** 10.1GB 的文件在数学推理上和 53.8GB 的原模型打平。如果你的用途偏推理，IQ3_XXS 可能比推荐的 IQ3_S 更划算——省 1.7GB，AIME25 一样满分，GPQA 只差 1 分。

## 对本地部署意味着什么

把这些数字翻译成硬件：

| 你的机器 | 之前能跑的 | 现在能跑的 |
|---|---|---|
| 16GB 统一内存 Mac | 7-9B 级别 | **27B @ IQ3_S，任务无损** |
| 12GB 显卡 | 7B 舒服，13B 勉强 | **27B @ IQ3_S 刚好塞下** |
| 8GB 显卡 | 7B 量化 | **27B @ IQ2_XS**（8.4GB，有损但可用）|

**关键是这些文件是标准 GGUF**，不需要打补丁的推理引擎：

> 「The resulting files are standard GGUF and run unmodified in `llama.cpp`, Ollama, and LM Studio.」

这一点非常重要。学术界不缺压缩率漂亮的量化方法，缺的是**能直接在用户已有工具链里跑起来**的。GSQ-RCO 做的是把复杂度全部放在量化阶段（离线的、一次性的梯度搜索），产出物是最普通的 GGUF——推理侧零成本。

## 两个额外的东西

**视觉投影器**：这个模型是多模态的（`image-text-to-text`），`mmproj-Qwen3.8-27B-BF16.gguf` 是 BF16 的视觉编码器 + 投影器，0.9GB，**一份服务所有量化档**。也就是说多模态用的话总占用是 11.8 + 0.9 = 12.7GB。

**MTP 投机解码**：每个量化档都额外提供一个 `-mtp` 版本（大约多 0.35GB），带模型的 Multi-Token Prediction 头，用于 llama.cpp 里的投机解码。权重其他部分完全相同，**所以质量不变**——纯粹是拿 0.35GB 空间换解码速度。

## 需要说清楚的地方

**这是一个模板化的发布。** model card 的注释里能看到，这是 DASLab 的 GGUF 发布模板，Qwen3.8-27B 只是填进去的第一个例子——换个模型只需改 frontmatter、几个标记为 `[swap]` 的字段，再跑 `tools/make_plots.py` 生成表格。这说明**后面会有一批同样处理的模型**，值得关注这个组织的 HuggingFace 主页。

**评测是他们自己跑的。** 表格里的 BF16 和 UD 基线都是他们自己的测量结果，不是引用第三方榜单。这不是问题（对照实验本来就该同一套环境跑），但意味着如果你的场景和这些基准差很远，实际表现要自己验证。

**量化不是免费的。** IQ2_XS 那一档在 LiveCodeBench 上从 85.71 掉到 76.57，掉了 9 分多。"任务无损"这个说法只适用于 IQ3_S 那一档，不能推广到所有档位。选低档位就是明确地拿质量换空间，这个交换在表里写得很清楚。

## 该下哪一个

- **主力用，机器装得下** → `IQ3_S`（11.8GB），任务无损，官方推荐
- **偏数学/推理，想省点空间** → `IQ3_XXS`（10.1GB），AIME25 同样满分
- **8GB 卡，能跑就行** → `IQ2_XS`（8.4GB），编程任务会明显退化，但仍远好于同尺寸的均匀量化
- **要多模态** → 加上 `mmproj-BF16`（0.9GB）
- **想要更快** → 选带 `-mtp` 的版本（+0.35GB），质量不变

从 local-first 的角度看，这类工作的价值可能被低估了：**它不生产新模型，但它让已有的好模型能装进更多人的机器**。对个人和小组织来说，"能不能在自己的硬件上跑"是先于"效果好不好"的门槛问题——把 53.8GB 降到 11.8GB，跨过这个门槛的人数级别不一样。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Model: https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF
> GSQ paper: arXiv:2604.18556 ｜ Code: https://github.com/IST-DASLab/GSQ
> RCO paper: arXiv:2605.00649 ｜ Code: https://github.com/IST-DASLab/RCO
> License: Apache-2.0 ｜ ❤ 655 ｜ ⬇ 479,597 (2026-09-09)

## The Short Version

**A 16GB machine can now run a 27B model with essentially no loss.**

This isn't another "quantized and it feels fine" claim. IST-DASLab publishes checkable numbers: the IQ3_S build scores **100.00 on AIME25** and **85.71 on LiveCodeBench v6** — **exactly matching** the BF16 baseline — and trails by 0.51 on GPQA-Diamond. File size: **11.8GB**, against the original's 53.8GB.

## What Uniform Quantization Misses

Mainstream GGUF quantization — the Q4_K_M and Q5_K_S you know — essentially applies **one quantization type to every weight tensor in the model**.

The problem: **tensors are not equally important.**

Some are exquisitely precision-sensitive; drop two bits and the output degrades badly. Others are forgiving and survive 2 bits fine. Uniform quantization is blind to that difference, so **to protect the few most sensitive tensors, every tensor gets carried at higher precision** — pure waste.

GSQ-RCO assigns a separate quantization type to each tensor, with the assignment obtained by a **gradient-based search** that allocates precision by per-tensor sensitivity, subject to a total size budget.

## Two Methods, One Each

| Method | What it does |
|---|---|
| **GSQ** (Gumbel-Softmax Quantization) | Post-training scalar quantization that **jointly learns** per-coordinate grid assignments and per-group scales via a Gumbel-Softmax relaxation. Closes most of the gap between scalar and vector quantization at 2-3 bits while staying deployable in standard scalar formats like GGUF |
| **RCO** (Riemannian Constrained Optimization) | Assigns one of K quantization types to each of N tensors under a total size budget. The budget constraint is reformulated as a smooth Riemannian manifold in logit space, permitting gradient-based optimization directly on the task loss while enforcing the budget **exactly**, with no constraint-specific hyperparameter tuning |

Put plainly: **GSQ handles "given a quantization type, quantize this tensor as accurately as possible"; RCO handles "under the total budget, which type does each tensor get."** Together they produce a non-uniform GGUF at a requested size.

Both come out of the Deep Algorithms and Systems Lab (DASLab) at the Institute of Science and Technology Austria — the lab behind GPTQ.

## The Numbers

Four sizes plus a vision projector:

| File | bpw | Size | Notes |
|---|---|---|---|
| `IQ2_XS` | 2.50 | 8.4 GB | Smallest; zero-shot above the BF16 baseline |
| `IQ2_S` | 2.75 | 9.3 GB | Matches the base model on AIME25 |
| `IQ3_XXS` | 3.00 | 10.1 GB | Strong all-round operating point |
| `IQ3_S` | 3.50 | 11.8 GB | **Recommended; task-lossless** |
| `mmproj-BF16` | 16 | 0.9 GB | Vision encoder + projector, for multimodal |

The full evaluation (wiki/c4/fw are perplexity, lower is better; the rest higher is better):

| Variant | bpw | GB | wiki↓ | c4↓ | fw↓ | ZS avg↑ | recovery | AIME25↑ | GPQA-D↑ | LCB v6↑ |
|---|---|---|---|---|---|---|---|---|---|---|
| BF16 | 16.00 | 53.8 | 7.05 | 11.45 | 8.14 | 74.34 | 100.0% | 100.00 | 89.90 | 85.71 |
| **GSQ-RCO IQ2_XS** | 2.50 | 8.4 | 7.69 | 12.98 | 9.19 | 74.54 | 100.3% | 96.67 | 84.85 | 76.57 |
| **GSQ-RCO IQ2_S** | 2.75 | 9.3 | 7.39 | 12.40 | 8.80 | **75.70** | **101.8%** | 100.00 | 86.36 | 82.29 |
| **GSQ-RCO IQ3_XXS** | 3.00 | 10.1 | 7.20 | 12.13 | 8.59 | 74.81 | 100.6% | 100.00 | 88.89 | 84.57 |
| **GSQ-RCO IQ3_S** | 3.50 | 11.8 | **7.07** | 11.76 | 8.34 | 74.47 | 100.2% | **100.00** | 89.39 | **85.71** |
| UD-IQ2_S | 2.49 | 8.4 | 8.02 | 12.78 | 9.08 | 73.80 | 99.3% | 86.67 | 76.26 | 72.00 |
| UD-Q2_K_XL | 2.88 | 9.8 | 7.54 | 12.25 | 8.69 | 74.37 | 100.0% | 100.00 | 86.87 | 82.28 |
| UD-IQ3_S | 3.52 | 12.0 | 7.16 | 11.75 | 8.34 | 75.49 | 101.5% | 96.67 | **89.90** | 84.00 |

(UD = Unsloth Dynamic, among the best-regarded dynamic quantizations in the community — a serious opponent.)

### Three Things Worth Noticing

**One: at matched file size the gap is large.** At 8.4GB, GSQ-RCO IQ2_XS versus UD-IQ2_S: **+10.00 on AIME25, +8.59 on GPQA-Diamond, +4.57 on LiveCodeBench v6**. Same disk footprint, cliff-edge difference on reasoning tasks.

**Two: at 2.5 bits the zero-shot average exceeds the BF16 base model** (74.54 vs 74.34, 100.3% recovery), and 2.75 bits reaches 101.8%.

Read this correctly: **quantization did not make the model smarter**. Zero-shot benchmarks (arc_easy, arc_challenge, hellaswag, winogrande, piqa) are noisy, and quantization perturbation occasionally lands favorably on them. The columns that actually matter are the reasoning and generation benchmarks on the right, where IQ2_XS is clearly *below* BF16 (96.67 / 84.85 / 76.57).

**Recovery above 100% is a warning: don't judge quantization quality by the zero-shot average alone.**

**Three: 3.0 bits already matches AIME25.** A 10.1GB file ties the 53.8GB original on math reasoning. If your use is reasoning-heavy, IQ3_XXS may be a better deal than the recommended IQ3_S — 1.7GB smaller, same perfect AIME25, only 1 point behind on GPQA.

## What This Means for Local Deployment

Translating into hardware:

| Your machine | Was able to run | Now runs |
|---|---|---|
| 16GB unified-memory Mac | 7-9B class | **27B @ IQ3_S, task-lossless** |
| 12GB GPU | 7B comfortably, 13B barely | **27B @ IQ3_S fits** |
| 8GB GPU | quantized 7B | **27B @ IQ2_XS** (8.4GB, lossy but usable) |

**Crucially, these are standard GGUF files** — no patched inference engine required:

> "The resulting files are standard GGUF and run unmodified in `llama.cpp`, Ollama, and LM Studio."

That matters enormously. Academia does not lack quantization methods with impressive compression ratios; what's usually missing is **something that runs in the toolchain users already have**. GSQ-RCO puts all the complexity in the quantization stage (an offline, one-time gradient search) and emits the most ordinary GGUF possible — zero cost at inference time.

## Two Extras

**Vision projector**: this model is multimodal (`image-text-to-text`), and `mmproj-Qwen3.8-27B-BF16.gguf` carries the BF16 vision encoder and projector at 0.9GB, with **one copy serving all quantizations**. So multimodal use totals 11.8 + 0.9 = 12.7GB.

**MTP speculative decoding**: each quantization also ships an optional `-mtp` build (about 0.35GB larger) carrying the Multi-Token Prediction head for speculative decoding in llama.cpp. The weights are otherwise identical, **so quality is unchanged** — a straight trade of 0.35GB for decode speed.

## Caveats Worth Stating

**This is a templated release.** The model card's comments reveal it's DASLab's GGUF release template, with Qwen3.8-27B as the first filled-in example — publishing another model means changing the frontmatter, a handful of `[swap]` fields, and running `tools/make_plots.py`. Which implies **more models will get the same treatment**; the organization's HuggingFace page is worth watching.

**They ran the evaluations themselves.** The BF16 and UD baselines in the table are their own measurements, not third-party leaderboard citations. That's not a flaw — a controlled comparison should run in one environment — but it does mean that if your workload differs sharply from these benchmarks, you should verify yourself.

**Quantization isn't free.** IQ2_XS drops LiveCodeBench from 85.71 to 76.57, more than nine points. "Task-lossless" applies to IQ3_S only and does not generalize across the range. Picking a lower tier is an explicit quality-for-space trade, and the table states the terms plainly.

## Which One to Download

- **Daily driver, machine has room** → `IQ3_S` (11.8GB), task-lossless, the official recommendation
- **Math/reasoning-heavy, want to save space** → `IQ3_XXS` (10.1GB), same perfect AIME25
- **8GB card, just needs to run** → `IQ2_XS` (8.4GB), noticeably weaker at coding but still far ahead of uniform quantization at the same size
- **Multimodal** → add `mmproj-BF16` (0.9GB)
- **Want it faster** → take the `-mtp` variant (+0.35GB), quality unchanged

From a local-first perspective this kind of work is probably undervalued: **it produces no new model, but it fits existing good models into far more people's machines**. For individuals and small organizations, "can it run on my hardware" is a gate that comes before "is it any good" — and taking 53.8GB down to 11.8GB moves that gate for an entirely different order of magnitude of people.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
