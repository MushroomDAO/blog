---
title: "把 RL 训练的每个角色都做成独立服务：OpenBMB 开源 Meshy，同步与全异步只差一个参数"
titleEn: "Every RL Role as a Service: OpenBMB Open-Sources Meshy, Where Sync and Fully-Async Differ by One Knob"
description: "Meshy 是 OpenBMB 开源的异步 RL 训练框架，也是训练 MiniCPM5 的引擎。它把推理、训练、rollout 各自做成独立进程，全部通过一个 TransferQueue 数据平面通信，控制流由数据就绪度驱动，没有中心 driver 分发 RPC。最有意思的设计：同步、有界离策略、全异步三种训练模式共用同一套服务，差别只在 rollout 的节奏窗口这一个参数。"
descriptionEn: "Meshy is OpenBMB's open-source asynchronous RL training framework — and the engine behind MiniCPM5. It models inference, training and rollout as independent services communicating through a single TransferQueue data plane, with control flow driven by data readiness and no central driver fanning out RPCs. The neatest part: on-policy, bounded off-policy and fully asynchronous training share one set of services, differing only in a rollout pacing knob."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Research"
tags: ["强化学习", "训练框架", "OpenBMB", "MiniCPM", "异步训练", "开源", "SGLang", "分布式"]
heroImage: "../../assets/images/meshy-openbmb-async-rl-training-framework-banner.jpg"
---

> 📌 项目地址：https://github.com/OpenBMB/Meshy
> 技术博客：https://maydomain.notion.site/meshy-blog-en
> Docker 镜像：https://hub.docker.com/r/ztonyzhao/meshy
> 协议：Apache-2.0 ｜ 语言：Python ｜ Star：83 ｜ 开源日期：2026-09-07
>
> 补充说明：这篇是 MiniCPM5 系列报道的另一半。之前那篇讲的是模型
> （MiniCPM5-2B 的能力和端侧部署），这篇讲训练它的引擎。
> 模型那篇：https://blog.mushroom.cv/blog/minicpm5-2b-on-device-sota-small-model/

## 一句话结论

**如果你在读 RL 训练框架的代码时被"同步分支和异步分支各写一遍"劝退过，Meshy 的设计值得一看。**

它的核心主张是：**同步训练和异步训练不该是两套代码路径**。在 Meshy 里，trainer 永远为每个权重版本发出一个 gate 信号，rollout 服务自己决定要等几个 gate——想要严格同步就等一个，想要全异步就一个都不等。

## 传统 RL 训练框架的结构问题

强化学习训练一个大模型，至少要三类角色同时工作：

- **推理服务**（inference）——用当前策略生成样本
- **训练服务**（training）——拿样本更新权重
- **rollout 调度**——管数据集、算奖励、决定什么时候采样

传统做法是有一个中心 driver，把张量在这几个角色之间搬来搬去，用 RPC 扇出调用。这会带来两个麻烦：

1. **driver 成为瓶颈和单点** —— 每个张量都要过它
2. **同步/异步是两套逻辑** —— 严格同步（on-policy）和异步（off-policy）的调度差别很大，很多框架干脆写两份实现，然后两份都要维护、都要调试

Meshy 的回答是把 driver 整个拿掉。

## 设计：一切都是队列列

> Meshy models every role of an RL run as an independent service. Samples flow between services through a single TransferQueue data plane, control flow is driven by data availability.

拆开看这套设计的几个决定：

**每个角色是独立进程。** 推理、训练、rollout 各自是独立服务，通过队列列（queue columns）和少量 gate 信号通信。**没有 driver 扇出 RPC，也没有 driver 转发张量。**

**TransferQueue 同时是数据平面和控制平面。** 所有通信都走队列列，**列的就绪状态就是唯一的控制信号**，所以服务之间从不直接握手。gate 脉冲、GPU 所有权、张量本身，全都在同一套中间件里传。

这一条是整个设计的支点：把"控制"退化成"数据是否到位"，就不需要一个协调者了。

**拓扑是纯函数。** 完整的放置方案在每台机器上以 SPMD 方式各自算出来，**不需要服务发现**。配错的 recipe 在启动时就会被发现，而不是跑到一半才暴露。

**GPU 所有权是队列里传的一个 token。** 因此任意数量的服务可以自由地共置在同一组 GPU 上——共置不是框架预设的几种模式，是你自己排的。

**日志一个服务一个文件，带完整 traceback。** 卡住的时候，队列会告诉你哪里堆了没被消费的列。这是很务实的一条——分布式训练最难受的就是"卡住了但不知道卡在哪"。

## 最漂亮的部分：一个旋钮切换三种训练范式

框架自带的三个 recipe 训练同一个模型、同一套超参，**差别只在 rollout 配置**：

| Recipe | `pacing_window` | `async_max_running_request` | Trainer | 拓扑 |
|---|---|---|---|---|
| `justrl` | `1` | — | batch | 共置 |
| `justrl_async` | `2` | `1.5 × batch` | batch | 共置 |
| `justrl_fully_async` | `None` | `1.5 × batch` | `stream_minibatch=True` | 分离 |

- **`justrl`** —— 严格锁步 GRPO，生成和训练一步一动
- **`justrl_async`** —— 有界离策略：生成可以领先训练一个批次
- **`justrl_fully_async`** —— 全异步：trainer 按 chunk 到达就更新

README 里那句话说得很直接：

> 框架里没有单独的同步或异步代码路径：trainer 永远为每个权重版本发出一个 gate，rollout 服务决定它要等几个 gate。

**这就是"控制流由数据就绪度驱动"这个设计带来的直接好处。** 同步与否不是架构选择，是一个参数。想做消融实验对比 on-policy 和 off-policy 的影响？改一个数字，其他全部不变——这在实验可比性上是很强的性质。

## 自带的 recipe 覆盖了什么

| Recipe | 模型 / 数据 | GPU 布局 | 展示什么 |
|---|---|---|---|
| `grpo_gsm8k` | Qwen3-1.7B · GSM8K | 环境变量可调 | 最小基线，同一个文件切换拓扑 |
| `grpo_gsm8k_qwen3_8b` | Qwen3-8B · GSM8K | 8 卡，8×TP1 推理 + 1×FSDP8 训练共置 | 非对称共置：推理和训练用不同方式切分同一组卡 |
| `justrl` | R1-Distill-Qwen-1.5B · DAPO-Math-17k | 8 卡共置 | 锁步 GRPO，用 JustRL 的超参 |
| `justrl_fully_async` | 同上 | 16 卡，推理训练分离 | 全异步 + `stream_minibatch` |
| `justrl_minicpm5_1b` / `_2_6b` | MiniCPM5-1B / 2.6B | 8 卡（或 4 卡）共置 | **MiniCPM5 家族的实际训练配置** |
| `justrl_qwen3_30b_a3b` | Qwen3-30B-A3B（MoE）| 8 卡，TP8 + EP8 推理 + FSDP8 训练 | MoE 专家并行推理，16k 上下文 |
| `math_grpo_minicpm5_2_6b` | MiniCPM5-2.6B · 本地数学集 | 8 卡（或 4）| **128k 上下文**：上下文并行、动态批、自定义优势整形、1024 并发请求 |

注意倒数两行——**MiniCPM5 的训练配置是直接开源出来的**，不是"我们用了某个内部框架"。这让 MiniCPM5 的训练过程具备了可复现性，而不只是可下载性。

最后那个 `math_grpo_minicpm5_2_6b` 配置很有分量：128k 上下文 + 上下文并行 + 1024 个 in-flight 请求，这是真正在做长上下文 RL 的规模。

## 怎么跑起来

**前置条件**（门槛不低）：

- NVIDIA GPU，支持 CUDA 12.9
- Docker + NVIDIA Container Toolkit（或原生 Ubuntu 24.04）
- Python 3.12+（手动安装的话）

**最省事的方式是拉预构建镜像**：

```bash
docker pull ztonyzhao/meshy:0.1.0-alpha
docker run --gpus all -it --rm ztonyzhao/meshy:0.1.0-alpha
```

镜像里 PyTorch、SGLang、TorchTitan、TransferQueue 全部装好，虚拟环境在 `/opt/meshy` 已激活。

**跑一个 recipe**，所有配置都用同一条命令：

```bash
python scripts/launch.py --recipe recipe.grpo_gsm8k
```

这是最小的端到端运行：Qwen3-1.7B 在 GSM8K 上，默认单卡。模型权重首次使用时从 HuggingFace 下载。日志、检查点和 TensorBoard 事件落在 `.xrl_runtime/<timestamp>/`。

换成 8 卡锁步 GRPO 只要换模块名：

```bash
python scripts/launch.py --recipe recipe.justrl
```

想先做个两批次的冒烟测试，用 `recipe.justrl_smoke`。

## 自己写 recipe

一个 recipe 就是 `recipe/` 下的一个普通 Python 模块，导出三样东西：`SERVICE_GROUPS`、`COLOCATIONS`（当 GPU 组共享卡时）和 `main()`。角色是类型化的配置，它们之间的连线由 ignitor 推导出来：

```python
SERVICE_GROUPS = [
    ServiceGroup(
        id="actor_infer",
        config=InferenceServiceConfig(model_path=MODEL,
                                      server_args={"tp_size": 1, "enable_memory_saver": True}),
        n_replicas=8, n_gpus_per_replica=1,
    ),
    ServiceGroup(
        id="actor_train",
        config=TrainingServiceConfig(model_path=MODEL, trainer_config=..., batch_size=2048),
        n_replicas=1, n_gpus_per_replica=8,
    ),
    ServiceGroup(
        id="rollout",
        config=RolloutServiceConfig(model_path=MODEL,
                                    dataset="meshy.dataset.math:MATH",
                                    reward="meshy.dataset.math:MATH.reward",
                                    group_size=8, pacing_window=1),
        n_replicas=1, n_gpus_per_replica=0,
    ),
]
```

注意 `rollout` 那个服务 `n_gpus_per_replica=0`——它不占卡，只做调度和奖励计算。这种"角色即服务"的写法，让资源分配变成了显式声明而不是隐含在代码里。

## 需要说清楚的

**这是 alpha。** Docker 标签写着 `0.1.0-alpha`，开源日期 2026-09-07，83 个 Star。**不要拿它跑生产训练。**

**门槛是多卡 NVIDIA。** 最小的 recipe 单卡能跑，但框架的价值（共置、异步、分离部署）都要多卡才体现。Mac、AMD、单卡玩家基本用不上。

**它不是给个人用的。** 和这个博客常写的 local-first 工具不同，Meshy 解决的是训练侧的工程问题，读者是做模型训练的团队。个人开发者的价值在于**读它的设计**——"把控制流退化成数据就绪度"这个思路，在很多分布式系统里都能借鉴。

**依赖不轻。** 建在 SGLang 和 torchtitan 之上，加上自己的 TransferQueue。这三个东西任何一个出问题都会影响你。

## 为什么这件事对开源生态有意义

大部分开源模型给的是**权重**。少数给**训练数据**。给**训练框架**的极少——尤其是给了框架还附上自己旗舰模型的实际训练配置的。

MiniCPM5 + Meshy 这个组合把三层都放出来了：模型权重、UltraData 训练数据、Meshy 训练引擎和 recipe。这意味着别人不只是能用 MiniCPM5，**还能在同一套工具链上训自己的模型**。

对"数字公共物品"这件事来说，这个差别是本质的：**开源一个成品，和开源生产成品的手段，是两个量级的贡献。**

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/OpenBMB/Meshy
> Tech blog: https://maydomain.notion.site/meshy-blog-en
> Docker image: https://hub.docker.com/r/ztonyzhao/meshy
> License: Apache-2.0 ｜ Language: Python ｜ Stars: 83 ｜ Open-sourced: 2026-09-07
>
> Note: this is the other half of the MiniCPM5 coverage. The earlier article covered the
> model (MiniCPM5-2B's capabilities and edge deployment); this one covers the engine that
> trained it. Model article:
> https://blog.mushroom.cv/blog/minicpm5-2b-on-device-sota-small-model/

## The Short Version

**If you've ever bounced off an RL training framework's code because the sync and async paths are written twice, Meshy's design is worth a look.**

Its core claim: **synchronous and asynchronous training should not be two code paths**. In Meshy the trainer always emits one gate per weight version, and the rollout service decides how many gates it waits for — wait for one and you have strict sync; wait for none and you have fully async.

## The Structural Problem With Conventional RL Training

Reinforcement learning on a large model needs at least three roles working at once:

- **Inference** — generate samples with the current policy
- **Training** — take samples and update weights
- **Rollout scheduling** — manage the dataset, compute rewards, decide when to sample

The conventional approach has a central driver shuttling tensors between these roles and fanning out RPCs. Two problems follow:

1. **The driver becomes a bottleneck and a single point** — every tensor passes through it
2. **Sync and async are two implementations** — the scheduling differs enough between on-policy and off-policy that many frameworks simply write both, then maintain and debug both

Meshy's answer is to remove the driver entirely.

## The Design: Everything Is a Queue Column

> Meshy models every role of an RL run as an independent service. Samples flow between services through a single TransferQueue data plane, control flow is driven by data availability.

Unpacking the decisions:

**Each role is an independent process.** Inference, training and rollout are separate services talking through queue columns and a handful of gate signals. **No driver fans out RPCs, and no driver forwards tensors.**

**TransferQueue is both the data plane and the control plane.** All communication goes through queue columns, and **column readiness is the only control signal**, so services never handshake directly. Gate pulses, GPU ownership, and the tensors themselves all travel through the same middleware.

That's the pivot of the whole design: degrade "control" into "is the data there yet," and you no longer need a coordinator.

**Topology is a pure function.** Full placement is computed SPMD-style on each machine independently, **with no service discovery**. A misconfigured recipe is caught at startup rather than halfway through a run.

**GPU ownership is a token passed over the queue.** So any number of services can freely colocate on the same set of GPUs — colocation isn't a fixed set of framework-provided modes, it's something you arrange.

**Logs are one file per service, with full tracebacks.** When something stalls, the queue tells you where by showing piled-up unconsumed columns. That's a very practical touch — the worst part of distributed training is "it's stuck and I don't know where."

## The Prettiest Part: One Knob Switches Three Training Paradigms

The three bundled recipes train the same model with the same hyperparameters, **differing only in rollout configuration**:

| Recipe | `pacing_window` | `async_max_running_request` | Trainer | Topology |
|---|---|---|---|---|
| `justrl` | `1` | — | batch | colocate |
| `justrl_async` | `2` | `1.5 × batch` | batch | colocate |
| `justrl_fully_async` | `None` | `1.5 × batch` | `stream_minibatch=True` | disaggregate |

- **`justrl`** — strict lock-step GRPO, generation and training move together
- **`justrl_async`** — bounded off-policy: generation may run one batch ahead
- **`justrl_fully_async`** — fully async: the trainer steps as chunks arrive

The README puts it directly:

> There is no separate synchronous or asynchronous code path in the framework: the trainer always emits one gate per weight version, and the rollout service decides how many gates it waits for.

**This is the direct payoff of "control flow driven by data availability."** Sync-ness isn't an architectural choice, it's a parameter. Want an ablation comparing on-policy against off-policy? Change one number and hold everything else fixed — a strong property for experimental comparability.

## What the Bundled Recipes Cover

| Recipe | Model / data | GPU layout | What it shows |
|---|---|---|---|
| `grpo_gsm8k` | Qwen3-1.7B · GSM8K | env-tunable | The minimal baseline; the same file switches topology |
| `grpo_gsm8k_qwen3_8b` | Qwen3-8B · GSM8K | 8 cards, 8×TP1 inference + 1×FSDP8 trainer colocated | Asymmetric colocation: inference and training partition the same cards differently |
| `justrl` | R1-Distill-Qwen-1.5B · DAPO-Math-17k | 8 cards colocated | Lock-step GRPO with JustRL hyperparameters |
| `justrl_fully_async` | same | 16 cards, disaggregated | Fully async with `stream_minibatch` |
| `justrl_minicpm5_1b` / `_2_6b` | MiniCPM5-1B / 2.6B | 8 (or 4) cards colocated | **The MiniCPM5 family's actual training setup** |
| `justrl_qwen3_30b_a3b` | Qwen3-30B-A3B (MoE) | 8 cards, TP8 + EP8 inference + FSDP8 trainer | MoE inference with expert parallel, 16k context |
| `math_grpo_minicpm5_2_6b` | MiniCPM5-2.6B · local math set | 8 (or 4) cards | **128k context**: context parallel, dynamic batching, custom advantage shaping, 1024 in-flight requests |

Note the last two rows — **MiniCPM5's training configuration is open-sourced directly**, not summarized as "we used an internal framework." That gives MiniCPM5 reproducibility, not just downloadability.

That final `math_grpo_minicpm5_2_6b` recipe carries real weight: 128k context with context parallelism and 1024 in-flight requests is long-context RL at genuine scale.

## Running It

**Prerequisites** (the bar is not low):

- NVIDIA GPU with CUDA 12.9 support
- Docker with NVIDIA Container Toolkit (or native Ubuntu 24.04)
- Python 3.12+ for manual installs

**The easiest path is the prebuilt image**:

```bash
docker pull ztonyzhao/meshy:0.1.0-alpha
docker run --gpus all -it --rm ztonyzhao/meshy:0.1.0-alpha
```

PyTorch, SGLang, TorchTitan and TransferQueue come preinstalled, with the virtualenv already active at `/opt/meshy`.

**Launch a recipe** — every configuration uses the same command:

```bash
python scripts/launch.py --recipe recipe.grpo_gsm8k
```

That's the smallest end-to-end run: Qwen3-1.7B on GSM8K, one GPU by default. Weights download from HuggingFace on first use. Logs, checkpoints and TensorBoard events land in `.xrl_runtime/<timestamp>/`.

Switching to 8-card lock-step GRPO is a module name change:

```bash
python scripts/launch.py --recipe recipe.justrl
```

For a two-batch smoke test first, use `recipe.justrl_smoke`.

## Writing Your Own Recipe

A recipe is a plain Python module under `recipe/` exporting three things: `SERVICE_GROUPS`, `COLOCATIONS` (when GPU groups share cards), and `main()`. Roles are typed configs; the wiring between them is derived by the ignitor:

```python
SERVICE_GROUPS = [
    ServiceGroup(
        id="actor_infer",
        config=InferenceServiceConfig(model_path=MODEL,
                                      server_args={"tp_size": 1, "enable_memory_saver": True}),
        n_replicas=8, n_gpus_per_replica=1,
    ),
    ServiceGroup(
        id="actor_train",
        config=TrainingServiceConfig(model_path=MODEL, trainer_config=..., batch_size=2048),
        n_replicas=1, n_gpus_per_replica=8,
    ),
    ServiceGroup(
        id="rollout",
        config=RolloutServiceConfig(model_path=MODEL,
                                    dataset="meshy.dataset.math:MATH",
                                    reward="meshy.dataset.math:MATH.reward",
                                    group_size=8, pacing_window=1),
        n_replicas=1, n_gpus_per_replica=0,
    ),
]
```

Note that the `rollout` service has `n_gpus_per_replica=0` — it holds no cards, only doing scheduling and reward computation. This "role as a service" style makes resource allocation an explicit declaration rather than something implicit in the code.

## Caveats

**This is alpha.** The Docker tag says `0.1.0-alpha`, it was open-sourced 2026-09-07, and it has 83 stars. **Do not run production training on it.**

**The bar is multi-GPU NVIDIA.** The smallest recipe runs on one card, but everything valuable about the framework (colocation, async, disaggregated deployment) needs multiple. Mac, AMD and single-card users are out.

**It isn't aimed at individuals.** Unlike the local-first tools this blog usually covers, Meshy solves a training-side engineering problem, and its readers are teams training models. The value for an individual developer is **in reading the design** — "degrade control flow into data readiness" is an idea that transfers to plenty of other distributed systems.

**The dependencies are heavy.** Built on SGLang and torchtitan plus its own TransferQueue. Trouble in any of the three becomes your trouble.

## Why This Matters for the Open Ecosystem

Most open models release **weights**. A few release **training data**. Very few release the **training framework** — and fewer still release the framework together with the actual training configuration for their own flagship model.

The MiniCPM5 + Meshy combination puts out all three layers: model weights, the UltraData training corpus, and the Meshy engine with its recipes. Which means people can not only use MiniCPM5, **they can train their own models on the same toolchain**.

For anyone who cares about digital public goods, that distinction is fundamental: **open-sourcing a finished product and open-sourcing the means of producing it are contributions of different orders.**

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
