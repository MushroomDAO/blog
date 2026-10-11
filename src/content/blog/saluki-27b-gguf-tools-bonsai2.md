---
title: "Saluki 27B：7.9GB 原版 GGUF，工具调用与 Bonsai 2 怎么选"
titleEn: "Saluki 27B: Stock GGUF Tools vs Bonsai 2"
description: "Underdog Saluki 27B 将 Qwen3.8-27B 压到约 7.9GB，支持原版 llama.cpp。本文核对九项官方评测、120 题工具调用与并行调用成绩，解释其与 Bonsai 2 的 98.2% 为什么不能直接比较，并区分权重大小、运行内存、数学短板与实际部署条件，帮助选择本地代理模型。"
descriptionEn: "Saluki 27B offers a 7.9GB stock GGUF for local tools. Compare its benchmark limits, memory needs, and runtime tradeoffs with the ternary Bonsai 2 model."
wechatTitle: "Saluki 27B：工具调用与 Bonsai 怎么选"
wechatDigest: "Saluki 用约7.9GB权重保留工具接口，但数学短板和评测口径仍需分开看。"
pubDate: "2026-10-11"
updatedDate: "2026-10-11"
category: "Tech-News"
tags: ["Saluki", "Bonsai 2", "GGUF", "工具调用", "本地模型"]
heroImage: "../../assets/images/saluki-27b-gguf-tools-bonsai2-banner.jpg"
---

Saluki 27B 是一个让本地电脑用更小权重运行工具调用的压缩语言模型。它由 ConwayResearch 发布，基于 Qwen3.8-27B 与 GSQ-RCO 权重，采用 Apache 2.0 许可证：约 7.9GB 的 GGUF 可直接使用原版 llama.cpp；若更看重工具接口兼容性，值得优先试它，若更看重小文件和数学代码保留率，则继续考虑 Bonsai 2。

这里的判断来自官方模型卡与部署条件核对，不能理解成我们已经复现了两家的完整排行榜。“低于 8GB 最强”也是发布方的定位，而非覆盖全部模型与任务的独立结论。

## 7.9GB 压缩了什么？

Saluki 的主文件是 `Underdog-Saluki-27B-1.0-IQ2-mix.gguf`，官方文件元数据显示 **7,898,369,152 字节**，即约 7.90GB，或 7.36GiB。模型卡以约 54GB 的 BF16 权重作参照，文件缩小约 6.8 倍。

它仍是 27B 级模型，不是把参数删成了 8B。低比特表示减小了存储和权重驻留成本；“IQ2-mix”也不应简化成每一个张量都是固定两位。不同张量、额外元数据与敏感层的保存方式都会影响最终文件大小。

真正影响选择的是运行路径：Saluki 使用标准 GGUF 与原版 llama.cpp，而 Bonsai 2 的紧凑三值版本需要 PrismML 的分支。这意味着现有工具服务若已经围绕 llama-server 建好，Saluki 的接入和版本维护通常更直接。这是接口成本判断，不能据此推断推理速度快了几倍。

![小M把大权重压进行李箱，同时保留可用的工具插口](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-01.png)

## 工具调用的 88、84、70，到底比较了什么？

Saluki 官方给出一套冻结后才开始测试的 Underdog Bench：从 BFCL v4 取出的 120 个任务，在关闭 thinking、温度为 0 的条件下，报告通过任务数如下。

| 模型 | 通过数 / 总任务 | 文件或运行条件 |
| --- | --- | --- |
| Saluki 27B | 88 / 120 | 约 7.90GB，原版 llama.cpp |
| Qwen3.8-27B 母模型 | 84 / 120 | 未压缩参照 |
| Ternary Bonsai 2 27B | 70 / 120 | 官方对照标为约 5.95GB 版本 |

这组数据来自同一发布方的同一子集，比把两家的总分摆在一起更有可比性。但它不是完整 BFCL 排行榜，也不是我们独立运行的对照实验。Saluki 比母模型多过四题，样本只有 120 题，模型卡也提醒少数任务的差异可能随运行变化。

另一套 100 题的 BFCL v4 并行工具调用子集，使用官方检查器，Saluki 通过 42 题，母模型通过 35 题。因此可以说“官方子集里更好”，不能说“并行调用已经可靠”。42/100 本身仍提醒开发者做参数校验、失败重试和权限约束。模型卡另提到约五分之一并行回复有轻微格式问题，不能把产出一个 JSON 外形当作完成任务。

本地代理通常需要稳定选择函数、填入正确参数，并遵守接口格式。低比特模型在这些离散要求上仍可能表现不错，但这不保证长程规划、复杂数学或完整业务流程同样受益。

## 为什么 96% 不能直接对上 98.2%？

Saluki 模型卡的九项对照如下。保留率是本文用官方表格逐项相除得到的近似值，不是新增实验。

| 测试 | Saluki | 母模型参照 | 比值约为 |
| --- | --- | --- | --- |
| Underdog tools，120 题 | 88 | 84 | 104.8% |
| BFCL 并行子集，100 题 | 42 | 35 | 120.0% |
| SWE-bench Verified，固定 50 个 issue | 30 | 33 | 90.9% |
| IFEval，prompt-loose | 93.5 | 91.5 | 102.2% |
| IFBench，prompt-loose | 72.7 | 71.0 | 102.4% |
| MBPP+ | 78.0 | 83.9 | 93.0% |
| MuSR | 67.5 | 79.6 | 84.8% |
| AIME 2025，avg@4 | 79.2 | 96.7 | 81.9% |
| AIME 2026，avg@4 | 80.0 | 94.6 | 84.6% |

九个比值的简单平均约为 96.05%，与官方“约 96%”一致。这个平均包含超过 100% 的工具调用项，它不表示每一种能力都保留了 96%。此外，模型卡标注部分母模型成绩来自公开结果，与 Saluki 使用的 harness 未必完全一致；这个总数适合概括发布方报告，不适合当作统一严谨实验的汇总。

Bonsai 2 的 98.2% 则对应它自己十四项 thinking-mode 测试的综合值：84.78 对 86.32。试卷、推理模式和汇总方式均不同，不能据此算出“Bonsai 比 Saluki 高 2.2 个百分点”。

![小M发现两张成绩单的题目不同，停止把总分叠在一起](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-02.png)

更诚实的比较，是挑你自己的任务，固定提示词、上下文长度、工具定义、采样设置和检查器，再同时测两个模型。尤其要记录工具输出是否能被业务端接受，而不仅是文字答案看起来像对的。

## Saluki 和 Bonsai 2 怎么选？

| 你更在意什么 | 优先试谁 | 原因与限制 |
| --- | --- | --- |
| 已有原版 llama.cpp 服务、工具与并行调用 | Saluki | 标准 GGUF，官方相同工具子集表现更高；仍需业务校验 |
| 尽可能小的语言权重文件 | Bonsai 2 PTQ1_0 | 约 5.95GB，真三值，需要 Prism 分支 |
| 数学、推理和代码保留 | Bonsai 2 作为候选 | 官方报告更贴近母模型；需要同条件实测才能确定适合你 |
| 不想维护定制推理分支 | Saluki | 接入成本低，但不是整体能力无损 |
| 要视觉输入 | 另算完整预算 | Saluki 主文件是文本权重，vision projector 还需约 0.63–0.93GB |

Bonsai 2 的“5.9GB”要带上版本名。官方 PTQ1_0 文件为 5,946,648,928 字节；PQ2_0 文件约 7.21GB。两者编码布局不同，不能把文件大小和运行性能互换。其 MLX 分发也有另一套文件及自定义加载器，不能直接用 GGUF 的 5.95GB 作为 MLX 全部内存预算。

我们此前拆解过 Bonsai 2 的三值路线，相关背景见：
https://blog.mushroom.cv/blog/ternary-bonsai-2-27b-prismml-qwen3-ternary-5gb-local-27b/

Saluki 数学与推理的短板也要讲具体：上述 AIME 两项与 MuSR 的比值约为 82%–85%。这比一句“平均保留 96%”更能帮助数学用户做决定。SWE-bench 只有固定 50 个 issue 的小样本，也不能据此预期完整代码代理的成功率。

## 8GB 文件意味着 8GB 电脑能跑吗？

不能。加载后还需要运行器、计算缓冲、KV cache、系统与其他应用的内存；启用视觉模块还会增加权重。官方示例采用 32,768 上下文，它不是对所有低内存电脑的承诺。

我们建议先用短上下文确认权重加载、模板和工具接口，再逐渐增加真实对话长度。文件单位也要分清：厂商磁盘常用十进制 GB，操作系统内存显示往往采用 GiB，7.90GB 约等于 7.36GiB，不是另一个更小的模型。

![小M把权重装上小船，发现上下文和缓冲仍要占座位](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-03.png)

### 本机验证记录

我们在 Apple M4、16GiB 统一内存的机器上下载了固定 revision 的主权重，并核对 SHA-256 与官方元数据一致。使用官方 llama.cpp b11552（commit `23b0202a1`）macOS arm64 二进制，2048 上下文、单 slot、Metal 卸载、开启 Jinja，关闭 thinking，温度为 0。

四道自拟测试均通过函数名和参数的精确检查：英文加法、中文上海天气、曼谷与东京的并行天气，以及加法与巴黎天气的混合并行调用。两道并行题均在同一回复中返回两个正确调用。我们只检查了工具请求，没有实际访问天气服务或执行外部操作。

这四次短输出的服务器解码速率约 7.90–8.10 token/s，完整请求耗时约 10.4–16.6 秒，包含提示词处理；其中一次复用了部分前缀缓存。这是同一机器上的短工具输出记录，不能当作稳定吞吐基准，也没有测母模型或 Bonsai 2 的速度。四题全过只证明这次加载与接口链路可用，不能推算完整 BFCL 准确率、长上下文能力或运行内存峰值。请求、原始响应与精确检查结果已保存，便于复核。

## 如何开始用原版 llama.cpp？

先从官方模型页下载精确文件名，使用支持该架构的新版本 llama.cpp。下面是一个短上下文起点，GPU 参数应按本机后端调整：

```bash
llama-server -m Underdog-Saluki-27B-1.0-IQ2-mix.gguf \
  --jinja -ngl 99 -fa on -c 2048
```

`--jinja` 用于加载模型聊天模板，关系到 tool 与 thinking 模式。服务器默认提供兼容 OpenAI 的本地 API；接口兼容不代表 OpenAI 托管模型。

官方对快速工具调用建议 `chat_template_kwargs: {"enable_thinking": false}` 与 `temperature: 0`；一般 thinking 模式则建议温度 0.6、top_p 0.95、top_k 20。对照测试不能一边开 thinking、一边关闭，再只比较总分。

## 常见问题

### Saluki 的工具调用已经超过母模型了吗？

在官方公开的 120 题工具子集和 100 题并行子集中，是。这个结论的范围是这些任务和设置，不是所有工具平台、提示词或端到端代理流程。

### 它能直接替换 Bonsai 2 吗？

标准接口接入更容易，但数学和推理可能有明显取舍。应把现有业务题搬到同一检查器上测，而不是根据两个不同的综合保留率选赢家。

### Apache 2.0 是否等于所有输入输出都没限制？

模型卡列出的是模型许可。实际使用仍要检查依赖、来源和应用环境的要求；许可证也不保证模型质量或工具执行正确性。

来源与复核文件（2026-10-11）：
https://huggingface.co/ConwayResearch/Underdog-Saluki-27B-1.0
https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf
https://github.com/ggml-org/llama.cpp
https://github.com/PrismML-Eng/llama.cpp

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Saluki 27B is a compressed language model aimed at making local tool calling fit into a smaller weight budget. ConwayResearch distributes it under Apache 2.0, using Qwen3.8-27B and GSQ-RCO weights as its ancestry. Its roughly 7.9GB GGUF runs with stock llama.cpp. Start with Saluki when standard runtime compatibility and tools matter most; keep Bonsai 2 on the shortlist when a smaller file and mathematical capability retention matter more.

This recommendation combines official model-card evidence with deployment constraints. It is not a reproduction of either full benchmark suite. The publisher's “strongest under 8GB” positioning should also remain an attributed claim rather than a universal ranking.

## What does the 7.9GB file actually save?

The main file, `Underdog-Saluki-27B-1.0-IQ2-mix.gguf`, contains 7,898,369,152 bytes: about 7.90 decimal GB or 7.36GiB. Against the card's approximately 54GB BF16 reference, that is roughly a 6.8-fold file reduction.

It remains a 27B-class model. Lower precision reduces storage and weight residency; it does not turn the model into an 8B network. The IQ2-mix name should not be read as a promise that every tensor uses exactly two bits. Tensor choices, metadata and more carefully preserved layers all contribute to the final size.

The practical difference is its runtime path. Saluki uses standard GGUF and stock llama.cpp. Compact ternary Bonsai 2 requires PrismML's fork. An existing llama-server application may therefore face less integration and maintenance work with Saluki. This is an interface-cost observation, not evidence of a particular speed advantage.

![Xiao-M compresses a large model while keeping its tool sockets accessible](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-01.png)

## What do the tool scores of 88, 84 and 70 mean?

The Saluki publisher reports a frozen 120-task Underdog Bench drawn from BFCL v4. With thinking disabled and temperature zero, it records 88 passing tasks for Saluki, 84 for the parent model, and 70 for the roughly 5.95GB Bonsai 2 variant.

This is a more useful comparison than putting two unrelated aggregate retention scores side by side. However, it is one publisher's subset, not the complete BFCL leaderboard or our own independently reproduced comparison. A four-task lead over the parent is modest, and the card acknowledges run-to-run variation on a few tasks.

In a separate 100-task parallel-call subset evaluated with the official BFCL v4 checker, Saluki passes 42 tasks against 35 for the parent. “Better in this subset” is warranted; “reliable parallel tool use” is not. A 42/100 result still calls for argument validation and recovery. The card also notes minor formatting slips in roughly one fifth of parallel responses.

Local agents need the right function, correct arguments and acceptable output structure. A quantized model can retain those discrete behaviors while losing ground elsewhere. Tool success does not establish strong long-horizon planning or mathematical reasoning.

## Why cannot 96% be compared directly with 98.2%?

| Official comparison | Saluki | Parent reference | Approximate ratio |
| --- | --- | --- | --- |
| Underdog tools, 120 tasks | 88 | 84 | 104.8% |
| BFCL parallel subset, 100 tasks | 42 | 35 | 120.0% |
| SWE-bench Verified, fixed 50 issues | 30 | 33 | 90.9% |
| IFEval, prompt-loose | 93.5 | 91.5 | 102.2% |
| IFBench, prompt-loose | 72.7 | 71.0 | 102.4% |
| MBPP+ | 78.0 | 83.9 | 93.0% |
| MuSR | 67.5 | 79.6 | 84.8% |
| AIME 2025, avg@4 | 79.2 | 96.7 | 81.9% |
| AIME 2026, avg@4 | 80.0 | 94.6 | 84.6% |

The arithmetic mean of these nine ratios is about 96.05%, matching the headline. This includes tool ratios above 100%; it does not mean that every ability retains 96%. Some parent scores come from public results with potentially different harnesses, as the card explicitly indicates.

Bonsai 2's 98.2% refers to its own fourteen-test thinking-mode aggregate, 84.78 versus 86.32. Different questions, inference settings and aggregation prevent a meaningful “2.2-point advantage” calculation between the two headlines.

![Xiao-M notices that two scorecards contain different questions](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-02.png)

Our conclusion is to compare a fixed workload with the same prompts, tool schemas, context budget, sampling settings and checker. Record whether the business application can accept the call, rather than whether the model merely produced plausible-looking text.

## Which model should you try first?

For stock llama.cpp services and tool-heavy applications, Saluki offers a simpler runtime path and better reported results in the shared tool subset. For the smallest language-weight file, Bonsai 2 PTQ1_0 is smaller at 5,946,648,928 bytes, about 5.95GB, but requires the Prism fork. Its PQ2_0 variant is approximately 7.21GB and uses a different packing layout. File-size claims need a variant name.

For mathematics, reasoning and code, Bonsai 2 remains worth testing, based on its own capability-retention report. Saluki's AIME and MuSR ratios here are approximately 82–85%. That is a more relevant warning for a mathematics workload than the average 96% headline. The fixed 50-issue SWE-bench result also cannot establish full coding-agent performance.

Bonsai's MLX distribution has a different file budget and custom loader; the 5.95GB GGUF number is not its complete MLX memory footprint. Saluki's main GGUF is text-only. Adding its vision projector adds roughly 0.63–0.93GB before runtime overhead.

Our earlier Bonsai 2 analysis provides the ternary background:
https://blog.mushroom.cv/blog/ternary-bonsai-2-27b-prismml-qwen3-ternary-5gb-local-27b/

## Does an 8GB file fit an 8GB computer?

Weight size is only one part of runtime memory. The runtime, computation buffers, KV cache, operating system and other applications also consume memory. The official 32,768-context example is not a low-memory guarantee.

Start with a short context to verify loading, templates and tools, then increase it toward real conversations. Also keep decimal GB and binary GiB distinct: 7.90GB is roughly 7.36GiB, not a different smaller model.

![Xiao-M finds that context and runtime buffers still need room beside the weights](../../assets/images/saluki-27b-gguf-tools-bonsai2-fig-03.png)

### Our local verification

We downloaded a pinned revision on an Apple M4 with 16GiB unified memory and matched the GGUF SHA-256 against official metadata. We used the official macOS arm64 llama.cpp b11552 release, commit `23b0202a1`, with a 2048-token context, one slot, Metal offload, Jinja enabled, thinking disabled and temperature zero.

All four synthetic schema-and-argument checks passed: English addition, a Chinese Shanghai-weather request, parallel Bangkok/Tokyo weather calls, and mixed addition/Paris-weather calls. Both parallel tasks returned two correct calls in one response. These were tool requests only; we did not execute an external weather service or other external action.

Server-reported decoding rates for these short outputs were approximately 7.90–8.10 tokens/s. Complete requests took about 10.4–16.6 seconds including prompt processing, and one reused part of the prefix cache. This is a small local trace, not a stable throughput benchmark or a speed comparison with the parent or Bonsai 2. Four passes establish loading and interface viability for these inputs; they cannot establish full BFCL accuracy, long-context ability or peak runtime memory. Requests, raw responses and exact checks have been retained for review.

## How do you start with stock llama.cpp?

Download the exact GGUF from the official page and use a current llama.cpp build supporting this architecture. A short-context starting point is:

```bash
llama-server -m Underdog-Saluki-27B-1.0-IQ2-mix.gguf \
  --jinja -ngl 99 -fa on -c 2048
```

Adjust GPU options to your backend. `--jinja` activates the model's chat template for tool and thinking behavior. The server exposes an OpenAI-compatible local API; compatibility describes the interface.

The publisher recommends `chat_template_kwargs: {"enable_thinking": false}` and `temperature: 0` for fast tools. General thinking uses recommended temperature 0.6, top_p 0.95 and top_k 20. Keep these settings fixed in a comparison.

## FAQ

### Does Saluki beat its parent at tools?

Yes, in the publisher's stated 120-task tool subset and 100-task parallel subset. That conclusion does not cover every tool platform or complete agent workflow.

### Can it replace Bonsai 2 without compromise?

It can simplify standard-runtime integration, but mathematical and reasoning performance may involve substantial tradeoffs. Evaluate your workload with one checker instead of choosing a winner from two different aggregate percentages.

### What does Apache 2.0 establish?

It is the model-card license. Check the relevant dependencies and sources for your application. Licensing does not guarantee quality or correct tool execution.

Sources checked on 2026-10-11:
https://huggingface.co/ConwayResearch/Underdog-Saluki-27B-1.0
https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf
https://github.com/ggml-org/llama.cpp
https://github.com/PrismML-Eng/llama.cpp

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
