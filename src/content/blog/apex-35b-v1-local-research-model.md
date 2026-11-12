---
title: "Apex-35B：科研编程模型的能力、部署与 Mac 内存账"
titleEn: "Apex-35B: Research Agents, Deployment, and Mac Memory"
description: "Apex-35B-V1.0 基于 Qwen3.6-35B-A3B 继续训练，提供 35B 总参数、约 3B 激活与 262K 共享上下文，面向编程、工具调用和科研工作流。本文核对官方评测、递归自改进的实际含义、BF16 与 GGUF 下载、聊天模板和部署细节，并根据真实量化文件大小分析 Mac 内存条件，明确本地未运行模型。"
descriptionEn: "Review Apex-35B-V1.0 research and coding claims, official GGUF files, deployment templates, and Mac memory budgets. Separate publisher scores from measured results."
wechatTitle: "Apex-35B：Mac部署先算清内存账"
wechatDigest: "核对科研编程模型、量化文件与部署模板，说明不同Mac内存条件的实际限制。"
pubDate: "2026-10-29"
updatedDate: "2026-10-29"
category: "Tech-News"
tags: ["Apex-35B", "MoE", "local-LLM", "research-agents", "Apple-Silicon", "open-weights"]
heroImage: "../../assets/images/apex-35b-v1-local-research-model-banner.jpg"
lastPublishedAt: "2026-10-29T04:00:51Z"
---

Apex-35B-V1.0 是面向通用任务与科研工作流的开放权重模型，重点包括代码、工具调用、搜索和计算反馈。它由 Apex Intelligence 发布，在 Qwen3.6-35B-A3B 上继续训练，不能描述为从零完成预训练的新架构。

官方给出 35B 总参数、约 3B 每 Token 激活、262,144 Token 的输入输出共享上下文，采用 Apache-2.0。本文核对模型卡、仓库、技术博客与量化文件元数据，没有下载整套权重，也没有运行模型或复测榜单。

代码与说明：https://github.com/apexin-ai/Apex-35B-V1.0
模型：https://huggingface.co/Apexintelligence-AI/Apex-35B-V1.0
技术博客：https://www.apexin.com/apex-35b/

## 所谓科研能力，具体体现在哪里？

模型卡描述的工作流是：提出计算方案、编写并执行程序，再根据数值结果和错误反馈调整方法。它把科研任务与通用代码、工具使用放在同一模型能力框架下，并列出流体计算与机器人仿真等例子。

这种定位比“会回答科学问题”更接近计算科研助手。不过，能调用求解器不等于得到可靠科学结论。方程、边界条件、单位、离散误差和实验设计仍需要可追踪验证；跑出一条曲线只是过程的一部分。

![小M将计算方案、程序执行和结果检查连成研究反馈循环](../../assets/images/apex-35b-v1-local-research-model-fig-01.png)

适合的试点是已有可信参考结果的小问题，例如已知解析解的数值例子或固定测试集。先比较结果误差、可复现性和工具轨迹，再考虑复杂自动研究，而不是先让模型自由探索就宣称完成科研。

## 评测表有哪些提升，也有哪些不能忽略的差异？

以下摘录来自官方表格，均为发布方报告；分数受评测工具、联网条件、推理预算和 harness 影响。

| 评测 | Apex-35B | Qwen3.6-35B-A3B |
|---|---:|---:|
| SciCode 主问题 / 子问题 | 62.6 / 75.6 | 37.5 / 60.6 |
| BFCL V4 | 84.0 | 75.2 |
| Terminal-Bench 2.1 | 65.2 | 46.1 |
| SWE-bench Verified，无网络 | 73.4 | 63.8 |
| LiveCodeBench v6 | 82.3 | 84.5 |

这不是所有项目都胜出的表。LiveCodeBench 这一行就低于基座，说明能力转移并非全面单向增长。内部 RoboRSI、Real2Sim 和 CFD-Bench 也应与公开基准分开，不能只把某一内部结果当作通用科研能力排名。

选型更需要检查失败类型：工具参数是否完整，长任务是否保留前提，数值结果能否被独立复核。官方多模型比较可以帮助提出测试假设，但不应替代团队自己的任务验收。

## RSI 是开发系统的循环，还是模型上线后自动升级？

官方将 Apex Research 描述为自动化科研系统，参与训练数据构造、实验、训练配方和基础设施优化，经过验证的结果反馈到后续开发。这是对模型开发流程的说明。

下载后的检查点不会因为聊天次数增加，就自动改写自己的权重。一次推理中根据工具结果修正程序，与训练阶段更新参数，是不同层面的改进。两者都可以称为反馈循环，但证据和资源要求不同。

![小M把开发阶段的训练改进与部署后的工具反馈分成两个循环](../../assets/images/apex-35b-v1-local-research-model-fig-02.png)

本次公开仓库主要提供模型介绍、部署用法和资产；不能据此假定完整训练数据、Apex Research 内部系统和所有实验基础设施也已以相同方式发布。

## Mac 到底需要多少内存？

每 Token 激活约 3B，主要描述计算稀疏性，不表示只要存下 3B 参数。运行时仍需容纳模型权重或安排卸载，还要留出 KV cache、工作区、系统和应用内存。

官方 BF16 权重约 72GB。GGUF 仓库元数据中的单文件大小如下；GiB 由字节数除以 2³⁰ 计算，属于文件大小，不是实测峰值内存。

| 量化 | 文件大小约 |
|---|---:|
| Q4_K_M | 20.22GiB |
| Q5_K_M | 23.61GiB |
| Q6_K | 27.20GiB |
| Q8_0 | 35.21GiB |

本机为 16GB 统一内存 Mac，低于最小列出量化文件本身，未尝试靠交换内存制造“能跑”的结论。以下是容量推断，而非官方最低规格或实际速度测试：

- 16GB：不适合作为该官方 Q4 版本的常规本地全量装载方案。
- 24GB：Q4 权重之后余量很紧，不宜据此承诺稳定使用和长上下文。
- 32GB：Q4 短上下文可以作为评估起点，仍需观察实际内存、缓存与系统压力。
- 48GB / 64GB：为量化、工作区和其他应用提供更多空间；不因此保证 262K 上下文或固定速度。

![小M把权重、缓存、运行工作区和系统开销分别装入内存预算](../../assets/images/apex-35b-v1-local-research-model-fig-03.png)

统一内存容量、带宽、芯片代际、量化格式和运行时都会影响体验。不能从另一款模型的 Mac 速度，直接推导本模型的吞吐率。

## 官方部署示例最容易漏掉什么？

量化仓库提供 GGUF，官方给出的 llama.cpp 示例包括专用聊天模板与 Metal/GPU 层设置。以下为官方命令结构，本文没有实际运行：

```bash
hf download Apexintelligence-AI/Apex-35B-V1.0-GGUF Apex-35B-V1.0-Q4_K_M.gguf --local-dir .
llama-server -m Apex-35B-V1.0-Q4_K_M.gguf --jinja -ngl 99 -c 32768 --port 8000 --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0
```

必须注意 `--jinja`，不能随意换成基座模板。`-c` 是输入与输出的共同预算，不是只限制输入；若先用 32K 评估，就不能又期待单次输出完整使用文档中的 65,536 Token 预算。

官方也提供 SGLang、vLLM、TokenSpeed、KTransformers 和 Transformers 路径，涉及 GPU、CUDA、驱动与解析器要求。这些服务端命令不是 Mac 原生部署指令。首次部署应检查推理段与工具调用是否正确解析，多轮消息也要保留服务端要求的完整信息。

量化下载：https://huggingface.co/Apexintelligence-AI/Apex-35B-V1.0-GGUF

## 常见问题

### 3B 激活，为什么 Q4 仍然超过 20GiB？

激活量与权重存储量不同。MoE 减少每个 Token 参与计算的参数，但模型仍有总参数及其他运行开销，不能按激活参数估算总内存。

### 模型能读图吗？

本次按官方 Model Summary 的文本输入、文本输出定位介绍。技术博客展示了涉及视觉反馈的机器人和 Real2Sim 工作流，但仍需核对具体 harness 与视觉组件，不能凭演示、通用调用组件或架构名称，宣称该检查点的图像输入已经独立验收。

### 32GB Mac 一定能跑满 262K 上下文吗？

不能作此保证。本文的 32GB 建议仅针对 Q4 短上下文的容量评估起点，完整运行应以实际运行时内存与稳定性测试为准。

### Apache-2.0 意味着研究系统也全开源吗？

许可覆盖官方说明的权重、代码示例和文档，不自动证明私有训练数据和内部研究系统已公开，仍需逐个核对发布内容。

延伸阅读：https://blog.mushroom.cv/blog/hiroute-local-model-routing/

来源为模型卡、GGUF 元数据、官方代码仓库与技术博客。实际可用性应由模板、工具协议、内存和任务验收共同判断，不能只看模型参数或发布方的一张总分图。

原文与更新：https://blog.mushroom.cv/blog/apex-35b-v1-local-research-model/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Apex-35B-V1.0 is an open-weight model for general work and research workflows, including coding, tools, search, and computational feedback. Apex Intelligence developed it through further training of Qwen3.6-35B-A3B, rather than pretraining a new architecture from scratch.

The official specification lists 35B total parameters, approximately 3B active per token, 262,144 tokens shared by input and output, and Apache-2.0 licensing. This review inspected the model card, repository, technical blog, and GGUF metadata. It did not download full weights, run inference, or reproduce benchmark scores.

Repository: https://github.com/apexin-ai/Apex-35B-V1.0
Model: https://huggingface.co/Apexintelligence-AI/Apex-35B-V1.0
Blog: https://www.apexin.com/apex-35b/

## What does research capability mean here?

The model card describes planning computations, writing programs, and revising work using results and errors, including fluid and robotics examples. This is more specific than answering scientific questions, but solver execution does not establish valid science.

![XiaoM connects a computational plan, execution, and independent result checks](../../assets/images/apex-35b-v1-local-research-model-fig-01.png)

Units, boundary conditions, numerical errors, and experimental design still need verification. A useful pilot starts with a known reference solution and measures reproducibility and error before allowing open-ended research.

## What does the publisher's table show?

Reported comparisons against Qwen3.6-35B-A3B include SciCode main/subproblem scores of 62.6/75.6 versus 37.5/60.6; BFCL V4 at 84.0 versus 75.2; Terminal-Bench 2.1 at 65.2 versus 46.1; and offline SWE-bench Verified at 73.4 versus 63.8.

The comparison is not uniformly favorable: LiveCodeBench v6 is 82.3 versus the base model's 84.5. Internal RoboRSI, Real2Sim, and CFD-Bench results should also remain distinct from public benchmarks. Harnesses, network access, reasoning budgets, and tool behavior affect interpretation.

A team should test complete tool arguments, preservation of assumptions, and independently checkable numerical outputs. Publisher comparisons are starting hypotheses, not local acceptance results.

## Does RSI mean deployed weights update themselves?

The publisher describes Apex Research as contributing training data, experiments, training recipes, and infrastructure optimization to later development iterations. That is a model-development process.

A downloaded checkpoint does not automatically rewrite its weights as conversations accumulate. Revising code during inference and updating parameters during training are different feedback loops with different evidence requirements.

![XiaoM separates model-development training from inference-time tool feedback](../../assets/images/apex-35b-v1-local-research-model-fig-02.png)

The public repository's descriptions and deployment examples do not establish that private datasets or the complete internal research system have also been released.

## How much Mac memory is needed?

Active parameters describe sparse computation, not the total weights that must be stored or offloaded. Runtime memory also includes caches, workspaces, the operating system, and other applications.

Official BF16 weights are approximately 72GB. File metadata lists Q4_K_M at 20.22GiB, Q5_K_M at 23.61GiB, Q6_K at 27.20GiB, and Q8_0 at 35.21GiB. These are file sizes computed from bytes, not measured peak memory.

The available 16GB Mac cannot comfortably contain even the listed Q4 file, so no inference smoke test was attempted. Capacity guidance is an inference rather than an official minimum: 24GB leaves little headroom; 32GB can be a starting point for evaluating Q4 with short context; 48GB or 64GB provides more room without guaranteeing full context or particular throughput.

![XiaoM budgets weights, cache, runtime workspace, and system memory separately](../../assets/images/apex-35b-v1-local-research-model-fig-03.png)

Memory bandwidth, chip generation, quantization, and runtime all matter. Speeds from another model should not be reused as this model's benchmark.

## What does the deployment example require?

The official GGUF path includes llama.cpp with the embedded chat template. The following command structure is documented, not executed in this review:

```bash
hf download Apexintelligence-AI/Apex-35B-V1.0-GGUF Apex-35B-V1.0-Q4_K_M.gguf --local-dir .
llama-server -m Apex-35B-V1.0-Q4_K_M.gguf --jinja -ngl 99 -c 32768 --port 8000 --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0
```

Keep `--jinja` and the model's own template. Context is shared by input and output; a 32K setting cannot simultaneously provide the documented 65,536-token output budget. Other official paths cover GPU-oriented frameworks with CUDA, driver, and parser requirements; those commands are not native Mac instructions.

GGUF repository: https://huggingface.co/Apexintelligence-AI/Apex-35B-V1.0-GGUF

## Frequently asked questions

### Why does a 3B-active model still need a large weight file?

Sparse activation reduces per-token computation. It does not reduce total parameter storage to the active count.

### Is image understanding verified?

This article follows the official text-input/text-output summary. The blog also demonstrates visual-feedback and Real2Sim workflows; their harness and vision components require separate verification. Demos, generic widgets, and architecture names do not independently establish this checkpoint's image-input behavior.

### Does a 32GB Mac guarantee the full context window?

No. The suggestion concerns a short-context Q4 evaluation starting point, subject to actual memory and stability checks.

### Does Apache-2.0 cover the entire internal research system?

The published scope includes weights, examples, and documentation. It does not establish publication of private training data or internal systems.

Related: https://blog.mushroom.cv/blog/hiroute-local-model-routing/

Sources are the model card, official GGUF metadata, repository, and technical blog. Deployment quality depends on templates, tool protocols, memory, and acceptance tests together.

Canonical article: https://blog.mushroom.cv/blog/apex-35b-v1-local-research-model/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
