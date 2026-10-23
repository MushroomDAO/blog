---
title: "Flint 本地编程模型：40B MoE、rec 引擎与 125 token/s 的条件"
titleEn: "Flint Local Coding: MoE, rec and the Speed Claims"
description: "Recursive Flint 是总参数约40B、每token激活2.5B的开源编程模型。本文核对模型卡与rec源码说明，拆解M4 Pro速度测试、48GB内存门槛、上下文配置差异和本地Agent部署方法。"
descriptionEn: "A source-checked guide to Recursive Flint: 40B MoE weights, rec hardware requirements, coding evaluations, context limits and practical local agent deployment."
wechatTitle: "Flint：本地编程快，但先看48GB门槛"
wechatDigest: "核对Flint模型卡与rec引擎，讲清速度条件、内存要求和本地编程接入方法。"
pubDate: "2026-10-23"
updatedDate: "2026-10-23"
category: "Tech-News"
tags: ["Flint", "Recursive", "MoE", "本地编程", "Apple Silicon"]
heroImage: "../../assets/images/flint-local-coding-rec-engine-banner.jpg"
lastPublishedAt: "2026-10-23T01:09:10Z"
---

Flint 是把编程模型放到本地运行的新选择：模型开源，速度值得关注，但官方 rec 路线要求至少 48GB 统一内存，125 token/s 也有特定测试条件。

> 一手资料核对：2026-10-23。本文没有下载权重或测量模型速度；本机只有16GiB内存，不满足rec公开要求。
> 发布说明：https://recursive.com/updates/introducing-recursive-flint
> 模型卡：https://huggingface.co/RecursiveSI/flint
> 推理引擎：https://github.com/recursive-oss/rec

## 40B 模型为什么每次只激活 2.5B？

Flint 面向代码调查、修 Bug、加功能与测试，采用 MoE 架构。模型卡给出的精确总参数是39.8B，2.5B是每token激活量，包含输出头；它不是一个只需存储2.5B权重的小模型。

我们直接核对了公开的 `config.json`：49层，256个路由专家、每次选择6个，另有共享专家；滑动窗口与全注意力混合。这里节省的是单步计算与权重读取量，不代表所有专家都从内存里消失。

算一笔不含额外开销的账：39.8B参数乘4bit约19.9GB；BF16约79.6GB。量化元数据、运行时与KV缓存还要占空间。因此，“激活参数少”与“16GB笔记本能跑”不能画等号。

模型卡及配置：
https://huggingface.co/RecursiveSI/flint/blob/main/config.json

![小M背着完整专家权重，只激活少数专家进行计算](../../assets/images/flint-local-coding-rec-engine-fig-01.png)

## 125 token/s、5倍与2.6倍分别在比什么？

先把三个口径拆开，否则很容易误读成“随便装一个客户端都快5倍”。

| 官方公开口径 | 应该怎样理解 |
|---|---|
| M4 Pro短上下文超过125 token/s | 专用优化引擎上的生成速度；不等于大仓库首字响应时间 |
| 相对25B—40B稠密模型快5倍以上 | 不同模型在相近编程分数下的速度比较 |
| rec相对llama.cpp为1.4—2.6倍 | 同一个Flint模型、不同引擎的解码吞吐对比 |

rec README明确列出：M4 Pro、48GB统一内存、4bit权重、1K—252K输入、每次1024个输出token、每个长度5次，**不包含预填充**。发布页另一张128K会话图同样排除prefill；不能拿它代表从读入代码到交付补丁的总耗时。

我们的判断是：短输出、长输入的仓库问答，要先看prefill与缓存；大量生成的重构任务，decode吞吐才更突出。真正的工作完成时间还包括推理token、工具调用和测试失败后的返工。

来源：https://github.com/recursive-oss/rec

![输入处理与快速生成是不同的耗时环节](../../assets/images/flint-local-coding-rec-engine-fig-02.png)

## 编程成绩说明了什么？

模型卡报告 Terminal-Bench 2.1 为54.9%、SWE-bench Pro v2为89.7%、SWE-bench Verified为74.2%。这是开发方评测，不是本文复测，也不是同一套统一第三方排名。

其Agent成绩是至少5次尝试的平均pass@1，不能理解成“给5次机会后的通过率”。不同任务使用Terminus 2或mini-swe-agent，联网条件也不同。判断它适不适合你的代码库，应固定Agent、工具、超时和测试集后再比较。

官方也提醒复杂任务需要更明确的拆分。我们更建议先让它解决一个能通过测试验收的小问题，而非一上来接管整个遗留系统。

## 512K 上下文可以直接开满吗？

发布页说最高512K，并建议编程任务控制在256K以内；但此次下载核对的模型卡与 `config.json` 写的是262,144。两者不能无条件视作同一配置。

工程上应以选用的权重修订、引擎和启动参数为准。先使用已文档化的配置，不把发布页上限直接填进任意后端。输入与输出共享上下文预算，长推理也会挤占可用空间。

这里还有一个常见坑：Hugging Face页面顶部的自动生成Transformers代码，不能替代模型卡正文。正文明确写着尚未提供Transformers modeling代码；BF16参考服务路线是仓库内SGLang kit。

## 普通开发者怎样接到本地编程 Agent？

rec当前公开支持M4 Pro、M5 Pro、M5 Max，至少48GB统一内存、约30GB可用磁盘；pi还需要Node.js 22。下面是官方入口，经资料核对，本文未在16GiB机器上执行安装：

```bash
# 下载后先查看安装脚本，再执行
curl -fsSL https://raw.githubusercontent.com/recursive-oss/rec/main/install.sh -o rec-install.sh
less rec-install.sh
bash rec-install.sh
rec doctor
rec launch pi
```

也可用 `rec launch opencode`。首次运行会下载模型与harness；退出终端不等于服务停止，用完执行 `rec stop`。

自己接客户端时，先 `rec serve`，等待ready，再配置：

| 配置项 | 值 |
|---|---|
| Base URL | `http://127.0.0.1:11500/v1` |
| 模型名 | `flint` |
| API key | 本机执行 `rec auth token` 获取，不要粘贴到公开日志 |

rec优化的是单会话。并行开多个Agent时不要套用单会话吞吐预期。llama.cpp、Ollama等是官方列出的其他部署选择，但其具体量化、版本支持与速度要单独核验。

我们的落地建议是先用隔离工作目录、一个真实Bug和明确测试命令验证工具调用；再记录首字耗时、总耗时与验收结果。“本地模型”也不自动约束Agent调用的联网工具，想让代码留在设备上，还需检查harness、插件和遥测配置。

![本地模型与联网工具之间需要权限边界](../../assets/images/flint-local-coding-rec-engine-fig-03.png)

## Eureka Machine 是全自动训练工厂吗？

发布说明的准确表述是“小团队与Agent在不到四个月内协作”，Eureka Machine参与架构、量化、内核和训练等研究环节。它支持提出方案、实验和迭代，不足以证明整个项目无人参与，也不代表完整训练流水线已经公开。

更有参考价值的是模型与运行时协同优化的路线：本地编程的竞争不只在模型分数，也在你能否在目标硬件上持续得到可验收的修改。

## 常见问题

### 16GB Mac 可以照搬官方 rec 教程吗？

不符合当前至少48GB的要求。本文没有尝试让系统靠swap硬跑，也不承诺其他引擎能在16GB稳定运行。

### 开源意味着完全没有成本吗？

Apache-2.0权重可本地使用，不需要为本地推理支付模型API调用费；硬件、存储、电力和维护仍然有成本。

### 可以把 125 token/s 当作购买电脑依据吗？

应先确认内存、量化格式、上下文、引擎版本和工作负载。该数字是官方特定设置结果，本文没有独立复现。

---

本文原文：https://blog.mushroom.cv/blog/flint-local-coding-rec-engine/

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Flint is an open coding model for local agents. Its speed claims are interesting, but the official rec path requires at least 48GB of unified memory. The advertised 125 tokens/s is conditional, not a universal laptop result.

Sources checked on October 23, 2026. We did not download weights or benchmark inference: this host has 16GiB RAM.

Announcement: https://recursive.com/updates/introducing-recursive-flint
Model card: https://huggingface.co/RecursiveSI/flint
Engine: https://github.com/recursive-oss/rec

## What does 40B-A2.5B mean for memory?

The model card specifies 39.8B total parameters, with roughly 2.5B active per token including the output head. Sparse activation reduces work per generated token; it does not turn the model into a 2.5B weight download.

Our configuration inspection confirms 49 layers,256 routed experts with 6 selected per token, a shared expert, and mixed sliding/full attention. Weight-only arithmetic gives roughly 19.9GB at 4bits or 79.6GB atBF16, before metadata, runtime allocations and KV cache. These are estimates, not measured memory usage.

Configuration: https://huggingface.co/RecursiveSI/flint/blob/main/config.json

![Sparse activation still requires storing the full expert weights](../../assets/images/flint-local-coding-rec-engine-fig-01.png)

## Which speed comparison matters?

| Developer claim | Scope |
|---|---|
| Over 125 tokens/s on M4 Pro | Short-context generation with optimized inference |
| Over 5× faster than comparable dense models | Different 25B–40B models at similar coding scores |
| rec gives 1.4–2.6× llama.cpp throughput | Same Flint model, different runtimes |

The rec comparison uses M4 Pro 48GB,4-bit weights,1K–252K prompts,1,024 output tokens and five runs per length. Prefill is excluded. The announcement's 128K-session plot also excludes prefill.

For repository questions with long inputs and short answers, prompt processing and cache behavior can dominate. For long code generation, decode throughput matters more. Neither alone measures the time needed to produce a tested patch.

![Prompt processing and decoding contribute different costs](../../assets/images/flint-local-coding-rec-engine-fig-02.png)

## Are the coding results independently verified?

The model card reports 54.9% on Terminal-Bench 2.1,89.7% on SWE-bench Pro v 2 and 74.2% on SWE-bench Verified. These are developer results, not our reproduction. Agentic results average pass@1 over at least five attempts; they are not pass@5. Harnesses and network access differ across evaluations, so cross-source scores need care.

Start with a bounded bug and a clear test command. Record accepted changes, tool failures and total completion time, rather than selecting a model on generation speed alone.

## Is the context window 512K or 262,144?

The launch post advertises up to 512K and recommends staying within 256K. The checked checkpoint card and configuration document 262,144. Use the supported configuration for your exact checkpoint and runtime rather than copying the headline maximum into another backend. Prompt and output share the budget.

Also distinguish Hugging Face's automatically generated usage widget from the actual card: the card says Transformers modeling code is not yet included. Its BF16 reference deployment uses the supplied SGLang kit.

## How should a local developer start?

rec lists M4 Pro, M5 Pro and M5 Max,48GB unified memory, about 30GB free disk, and Node.js 22 for pi. The documented route, not executed here, is:

```bash
curl -fsSL https://raw.githubusercontent.com/recursive-oss/rec/main/install.sh -o rec-install.sh
less rec-install.sh
bash rec-install.sh
rec doctor
rec launch pi
```

`rec launch opencode` is another option. The first run downloads the model and harness. The server can remain running after the terminal closes; stop it with `rec stop`.

For another client, start `rec serve`, then use `http://127.0.0.1:11500/v 1`, model `flint`, and the local key returned by `rec auth token`. Keep that key private. rec targets single-session use; multiple agents should not inherit its single-session speed expectations.

The announcement lists other runtimes including llama.cpp and Ollama. Check their actual versions and quantizations separately. A locally served model also does not prevent its agent tools or plugins from sending data elsewhere.

![A local model still needs explicit tool permission boundaries](../../assets/images/flint-local-coding-rec-engine-fig-03.png)

## What was automated?

Recursive describes a small team working with agents, with Eureka Machine contributing across architecture, training, quantization and kernels. That supports a story of assisted research, not a claim that humans were absent or that the complete training system is open.

The useful engineering lesson is co-design: model quality, representation and runtime have to work together on the hardware you actually own.

## FAQ

### Can a 16GB Mac follow the rec recipe unchanged?

It does not meet the published 48GB requirement. We did not attempt a swap-heavy workaround or verify alternative runtimes on this host.

### Does open source mean zero cost?

Local inference avoids a hosted-model API bill, but still consumes hardware, storage, electricity and maintenance time. Weights use Apache-2.0.

### Should I buy hardware based on 125 tokens/s?

Verify precision, context, runtime version, memory and your workload first. We have not reproduced that developer result.

---

Original article: https://blog.mushroom.cv/blog/flint-local-coding-rec-engine/

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
