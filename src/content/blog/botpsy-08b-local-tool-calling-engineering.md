---
title: "BotPsy 0.8B：把工具调用放到端侧，工程上还差哪些环节？"
titleEn: "BotPsy 0.8B: Local Tool Calling Beyond the Benchmark"
description: "Tether AI Research 发布 BotPsy 0.8B，以 Qwen3.5 为底座强化函数调用和多轮工具流程。本文核对官方权重、量化版本、六项基准及训练方法，介绍 thinking 模板、工具解析、执行回传和部署验收，并通过本地小样本检查说明实际能力与限制，帮助工程师区分开放权重、完整智能体和端侧运行成本。"
descriptionEn: "Deploy BotPsy 0.8B for local tool calling: inspect official benchmarks, quantized weights, thinking templates, execution loops and bounded smoke-test evidence."
wechatTitle: "BotPsy 0.8B：端侧工具调用怎么落地"
wechatDigest: "核对官方成绩与量化版本，讲清thinking、工具执行回路及本地测试的边界。"
pubDate: "2026-11-12"
updatedDate: "2026-11-12"
category: "Tech-News"
tags: ["BotPsy", "端侧AI", "函数调用", "QVAC", "Agent工程"]
heroImage: "../../assets/images/botpsy-08b-local-tool-calling-engineering-banner.jpg"
---

BotPsy 是一个可以在本地选择工具、填写参数的小模型，适合给低到中等难度的工作流增加语言入口。它的价值在于把一部分决策留在设备端；真正的工具权限、执行和结果核验，仍要由应用负责。

Tether AI Research 于 2026 年 11 月 11 日发布 BotPsy，基于 Qwen3.5-0.8B，模型权重采用 Apache 2.0 许可。它提供 BF16 和官方 GGUF；训练代码和训练数据不属于本次发布，不能把它描述成完整训练工程全部开源。

官方权重：https://huggingface.co/qvac/BotPsy-0.8B

官方量化：https://huggingface.co/qvac/BotPsy-0.8B-GGUFs

官方方法与评测：https://huggingface.co/blog/qvac/botpsy

本文固定 BF16 修订 `24561e9681643eaf807fc28b0875210cb17f89c1` 和 GGUF 修订 `17bb36aa29c58fcde8e321aaaad3f2f7372aa655`。以下成绩属于官方评测，本地检查另列。

## 六项领先，究竟比较了什么？

官方把 BotPsy 与 Qwen3.5-0.8B、Qwen3.5-2B、LFM2.5-1.2B、MiniCPM5-1B 放进同一个评测 harness，并全部开启 thinking。BotPsy 在测试的不超过 1.2B 参数模型中，六项工具使用与智能体基准都领先；对比 2B 模型则是五项领先，Claw-Eval 落后。

| 官方指标 | BotPsy 0.8B | Qwen3.5 0.8B | Qwen3.5 2B |
|---|---:|---:|---:|
| BFCL v4 | 44.0 | 23.4 | 37.7 |
| ACEBench | 58.7 | 30.1 | 55.4 |
| τ-bench 汇总 | 51.5 | 23.2 | 46.5 |
| Claw-Eval | 46.5 | 39.3 | 48.9 |
| BrowseComp-Plus | 4.5 | 1.9 | 2.8 |
| ToolSandbox | 64.6 | 30.5 | 41.2 |

不同指标不是同一种“任务成功率”。BFCL 使用加权汇总并平均三次运行；τ-bench 是 τ² 的零售、电信和 τ³ 的银行子集平均，不含航空；ToolSandbox 用八种设置的平均相似度。依赖外部 API 的原版评测在 11 月 3 日运行。

特别值得看 BrowseComp-Plus：4.5 比几个对照模型高，却仍说明开放式检索很难。官方还列出 BFCL 网页搜索 14.0、记忆 16.3，银行子集所有模型都不超过 5。工程上应该先找闭合、短链路、容易核验的任务，而不是给它无限制搜索和操作权限。

![小M把不同标尺的模型成绩放回各自的评测轨道](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-01.png)

## 为什么小模型的工具能力会提高？

官方方法是四阶段后训练：工具轨迹监督微调、多教师 on-policy 蒸馏，以及两轮强化学习。三个 Qwen3.5-4B 教师分别强化工具使用、一般推理和指令遵循，再为学生自己生成的轨迹提供逐 token 的训练信号。

一个有参考意义的细节是：只做工具 SFT 时，知识和指令遵循出现退化；后续蒸馏把这些能力恢复回来。两轮 RL 使用规则与验证器，分别偏重工具调用、再扩展到通用可验证任务。工具奖励还会区分函数名、参数名和参数值，给予部分分数。

这给工程团队的启发是：衡量专用模型，除了看目标指标涨了多少，也要检查原本会做的事情有没有退化。我们没有训练复现，也没有拿到完整训练代码和数据，因此这里讲的是官方公开的方法，不是可一键复训的配方。

## 下载哪一版，大小代表什么？

| 官方 GGUF 文件 | 文件字节数 | 实用定位 |
|---|---:|---|
| `botpsy-0.8b-bf16.gguf` | 1,516,744,160 | 未量化对照 |
| `botpsy-0.8b-q8_0.gguf` | 811,843,040 | 官方推荐的折中版本 |
| `botpsy-0.8b-q4_k_m-imat.gguf` | 529,296,960 | 更紧的存储与内存预算 |

这些是模型文件大小，不是进程峰值内存。运行时还要容纳缓存、工作区、上下文、tokenizer 和应用本身。也不能因为它叫 0.8B，就认为任何手机都能按同一速度运行。

官方 GGUF 测试使用 H100 上的 llama.cpp CUDA build b12169，时间为 11 月 6–7 日，与 vLLM 参考结果的外部 API 运行日期不同。GGUF 没有跑 ToolSandbox；Q8 与 BF16 GGUF 的十项平均分分别为 50.7 和 50.4，Q4 为 48.9。这个平均值混合了工具、知识和指令指标，不能直接当作你的业务准确率。

同样的 BF16 张量换引擎后，τ-bench 从 51.5 到 47.5，Claw-Eval 从 46.5 到 43.4。没有发生量化也会有差异，不能把所有变化都归因于位宽，更不能把 H100 数据写成手机实测。官方 GGUF 也没有包含底座的 MTP 层。

## 接入时最容易遗漏哪两个开关？

第一是 thinking。模型经过 thinking 模式训练和评测，但聊天模板默认不启用，必须显式传 `enable_thinking=True`。第二是工具解析：原始生成是 Qwen3.5 XML 风格的函数调用，应用需要把它解析成结构化 `tool_calls`。

如果用已支持该架构的 llama.cpp，可以从官方推荐的 Q8 开始。下面把服务绑定到本机，使用 8192 上下文作为初始工程配置；这是接入示例，并非我们已经完成的 GGUF 性能测试：

```bash
hf download qvac/BotPsy-0.8B-GGUFs botpsy-0.8b-q8_0.gguf \
  --revision 17bb36aa29c58fcde8e321aaaad3f2f7372aa655 --local-dir ./models

llama-server -m ./models/botpsy-0.8b-q8_0.gguf --jinja -c 8192 \
  --temp 0.3 --top-p 0.95 --top-k 20 --presence-penalty 1.5 \
  --chat-template-kwargs '{"enable_thinking":true}' \
  --host 127.0.0.1 --port 8080
```

使用 vLLM 时，官方示例配置 `--language-model-only`、`--enable-auto-tool-choice`、`--tool-call-parser qwen3_xml` 和 `--reasoning-parser qwen3`。Transformers 模型卡测试版本为 5.19.0；缺少高效 DeltaNet 内核时会走较慢的参考实现。选后端时，先验证架构、模板、解析器和你的设备，再谈性能。

![小M为小模型接上思考模板与结构化工具解析两道接口](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-02.png)

## 一个真正可用的工具回路是什么？

模型输出函数名，不代表日历已经创建或文件已经修改。应用必须接住调用，核对工具名与参数，执行获准的动作，再把带调用关联标识的工具结果作为后续消息传回，模型才有依据继续回答。

例如设置一盏模拟灯：只提供 `set_brightness(level)`，把 `level` 限定为 0–100 的整数。用户说“设成 55%”，允许生成调用；只说“改一下亮度”，应询问数值；问天气而没有天气工具时，不应编造一次调用。验证器也要检查这些负例，而不只是最容易成功的正例。

首次接入建议记录请求、模板开关、函数与参数、执行结果、最终答复和停止原因。限制每个任务的步数与 token，超时或参数不合法就明确失败；高影响写操作再增加与应用相称的确认机制。官方明确不面向安全关键或涉及金钱、个人信息、健康等敏感自动决策。

“模型本地运行”和“所有数据始终本地”也是两件事：如果工具要调用云端搜索、地图或外部服务，输入仍可能离开设备。是否端侧闭环，要看整个应用的数据流。

![小M将工具请求交给执行器检查，再把真实结果送回模型](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-03.png)

## 本地检查到了哪一步？

我们在 Apple M4、16GB 统一内存的 Mac 上，使用实际下载的固定 BF16 权重，以 Transformers 5.19.0、PyTorch 2.13.0 的 MPS float32 路径生成，显式启用 thinking 和缓存。缺少专用 DeltaNet 内核，运行时使用参考实现。解码采用贪心，每条最多 1024 个新 token，与官方采样设置不同。

三条自写英文输入都在预算内完成：明确要求 55% 时生成 `set_brightness` 和参数 55；缺少数值时追问亮度；没有天气工具时说明无法查询，没有虚构天气或调用。三条分别生成 101、115、132 个 token，结构检查与人工阅读均符合这些构造任务的预期。

这里没有真正操作灯具，也没有把工具返回值接成多轮闭环；测到的是实际权重的决策与原始调用生成，不是已完成的设备自动化产品。脚本、环境、输入和最终输出均已保存，便于复核。

这组检查只回答“当前模板与本地生成路径能不能走通这些构造输入”。它不替代 BFCL、真实多轮用户测试、中文适配、量化精度、手机内存或续航测量。尤其不能把几条结构检查的通过率外推成业务可靠性。

## 常见问题

### 它是不是完整开源的个人助理？

开放的是模型权重与用法说明，训练代码和训练数据没有随本次发布。权限、工具实现、任务状态、记忆和界面还要由产品补齐。

### 中文可以直接代替英文测试吗？

官方主要训练和测试语言是英文，也报告了多语言指令遵循测试。中文工具名称、参数描述和真实业务对话仍需要独立验收，不能从英文成绩直接推断。

### 0.53GB 的 Q4 能不能直接上生产？

先看你自己的任务与设备。官方平均分变化只是线索，至少还应测不该调用、缺参数、工具报错、重复执行和长上下文等场景。

相关阅读：https://blog.mushroom.cv/blog/tokin-token-native-agent-rl-gateway-guide/

Mycelium Protocol 的独立工作包括固定权重版本、核对发布内容和量化条件，以及上文可复核的小样本本地检查。官方成绩与部署建议的依据为上方模型卡和发布博客。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

BotPsy is a small local model that selects tools and supplies arguments for low- to medium-difficulty workflows. It moves part of the decision process onto a device; the application still owns permissions, execution and verification of the result.

Tether AI Research released the Qwen3.5-0.8B derivative on November 11, 2026 under Apache 2.0. BF16 and official GGUF weights are available. Training code and training data are explicitly outside this release, so this is not a complete reproducible training stack.

Weights: https://huggingface.co/qvac/BotPsy-0.8B

GGUFs: https://huggingface.co/qvac/BotPsy-0.8B-GGUFs

Method and evaluations: https://huggingface.co/blog/qvac/botpsy

We pinned BF16 revision `24561e9681643eaf807fc28b0875210cb17f89c1` and GGUF revision `17bb36aa29c58fcde8e321aaaad3f2f7372aa655`. Official benchmark results and our local smoke checks are reported separately.

## What does “leading six benchmarks” mean?

The team used one evaluation harness with thinking enabled for BotPsy, Qwen3.5-0.8B, Qwen3.5-2B, LFM2.5-1.2B and MiniCPM5-1B. BotPsy leads the tested models at or below 1.2B on all six tool-use and agentic benchmarks; against Qwen3.5-2B it leads five, with Claw-Eval the exception.

| Official metric | BotPsy 0.8B | Qwen3.5 0.8B | Qwen3.5 2B |
|---|---:|---:|---:|
| BFCL v4 | 44.0 | 23.4 | 37.7 |
| ACEBench | 58.7 | 30.1 | 55.4 |
| τ-bench aggregate | 51.5 | 23.2 | 46.5 |
| Claw-Eval | 46.5 | 39.3 | 48.9 |
| BrowseComp-Plus | 4.5 | 1.9 | 2.8 |
| ToolSandbox | 64.6 | 30.5 | 41.2 |

These metrics are not interchangeable success rates. BFCL uses an official weighted aggregate averaged over three runs. The τ score combines retail and telecom from τ² with banking from τ³, excluding airline. ToolSandbox averages similarity over eight settings. External-API evaluations for the original comparison ran on November 3.

BrowseComp-Plus is a useful reality check: 4.5 leads this small comparison but is low in absolute terms. The card also reports BFCL web search at 14.0, memory at 16.3, and no model exceeding 5 on banking. Start with short, bounded and verifiable workflows rather than unrestricted research and execution.

![Little M puts different benchmark scores back onto their own measuring tracks](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-01.png)

## What changed during training?

The published recipe has four stages: supervised tool-trajectory training, multi-teacher on-policy distillation and two reinforcement-learning rounds. Three specialist Qwen3.5-4B teachers cover tools, general reasoning and instruction following, providing token-level feedback on student-generated responses.

The important tradeoff is that tool-focused SFT initially degraded knowledge and instruction following. Distillation recovered those areas. Rule-based RL then rewarded tool structure and correctness, including partial credit for function names, argument names and values, before broadening the task mix.

For engineers, improvements in a target skill should be accompanied by regression checks on existing capabilities. We did not reproduce training or obtain the complete training pipeline; this is the team's disclosed method, not an independently validated retraining recipe.

## Which file should you deploy?

The official BF16 GGUF is 1,516,744,160 bytes, Q8_0 is 811,843,040 bytes and imatrix-calibrated Q4_K_M is 529,296,960 bytes. File size is not peak process memory: caches, runtime workspaces, context and the application also consume memory.

Official GGUF evaluations used an H100 with llama.cpp CUDA build b12169 on November 6–7, whereas the vLLM reference's external services ran on November 3. ToolSandbox was not evaluated for GGUF. Across ten mixed tool, knowledge and instruction benchmarks, Q8 averages 50.7, BF16 GGUF 50.4 and Q4 48.9. These averages are not product-specific accuracy estimates.

Even the unquantized BF16 export differs from vLLM: τ-bench is 47.5 versus 51.5, and Claw-Eval is 43.4 versus 46.5. Engine differences and run variance matter before quantization enters the picture. These are not phone measurements. The released GGUF files also omit the base model's MTP layers.

## Which integration switches matter?

Enable thinking explicitly: training and evaluation use it, but the embedded template defaults to non-thinking. Also use a parser that understands Qwen3.5 XML tool output and returns structured calls to the application.

For a compatible llama.cpp build, the following is a starting configuration, not a GGUF performance test we have completed. The server binds only to localhost and starts with an 8192-token context:

```bash
hf download qvac/BotPsy-0.8B-GGUFs botpsy-0.8b-q8_0.gguf \
  --revision 17bb36aa29c58fcde8e321aaaad3f2f7372aa655 --local-dir ./models

llama-server -m ./models/botpsy-0.8b-q8_0.gguf --jinja -c 8192 \
  --temp 0.3 --top-p 0.95 --top-k 20 --presence-penalty 1.5 \
  --chat-template-kwargs '{"enable_thinking":true}' \
  --host 127.0.0.1 --port 8080
```

The official vLLM example uses `--language-model-only`, `--enable-auto-tool-choice`, `--tool-call-parser qwen3_xml` and `--reasoning-parser qwen3`. The Transformers card was tested with version 5.19.0; without optimized DeltaNet kernels it falls back to a slower reference path. Verify architecture support, templates, parsing and the target device before tuning throughput.

![Little M connects the thinking template and structured tool parser](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-02.png)

## What makes the tool loop real?

A generated function name is only a request. The application validates the tool and arguments, executes an allowed action, and feeds its result back with the proper call association before the model can ground a final answer in that result.

For a simulated desk light, expose only `set_brightness(level)` with an integer range of 0–100. An explicit request for 55 percent should call it. An unspecified brightness should trigger clarification. A weather question without a weather tool should not produce an invented call. Include such negative cases in acceptance checks.

Record template settings, calls, execution outcomes, final answers and stop reasons. Set step and token budgets and handle invalid arguments and tool failures explicitly. Add confirmations appropriate to consequential writes. The official card excludes safety-critical and high-stakes automation, including sensitive monetary, personal-information and health applications.

Local inference does not guarantee local end-to-end data handling: cloud search, maps or other remote tools can still receive inputs. Trace the complete application flow.

![Little M checks an execution request and returns the actual result to the model](../../assets/images/botpsy-08b-local-tool-calling-engineering-fig-03.png)

## What did we test locally?

We ran the pinned, downloaded weights on an Apple M4 Mac with 16GB unified memory using Transformers 5.19.0 and PyTorch 2.13.0, with MPS float32, thinking and caching enabled. DeltaNet used the reference implementation because specialized kernels were absent. Greedy decoding capped each example at 1024 new tokens, unlike the official sampling configuration.

All three self-authored English prompts completed within that budget. The explicit 55-percent request produced `set_brightness` with argument 55. The underspecified request asked for a brightness level. The weather question correctly explained that no weather tool was available, without inventing weather or a call. The outputs contained 101, 115 and 132 tokens respectively. Structural checks and manual reading matched the intended behavior on these particular cases.

No lamp was controlled, and no tool result was fed back into a multi-turn execution loop. This is real-weight decision and raw-call generation evidence, not a complete device-automation product. Inputs, environment, final outputs and the script are retained for inspection.

This checks a few synthetic inputs through one local generation path. It does not reproduce BFCL, realistic multi-turn use, Chinese behavior, quantized accuracy, phone memory use or battery life. Structural checks on a few examples do not establish general reliability.

## FAQ

### Is this a complete open-source personal assistant?

The release contains model weights and usage instructions; training code and data are not included. The product still needs tools, permissions, task state, memory and an interface.

### Can English results stand in for Chinese acceptance tests?

No. English is the primary training and testing language. The multilingual instruction results do not replace testing Chinese prompts, tool descriptions and business workflows.

### Can the smallest Q4 file go directly into production?

Evaluate your own tasks and hardware first, including missing arguments, inappropriate calls, tool errors, repeated actions and long contexts. The published aggregate is only an initial signal.

Related reading: https://blog.mushroom.cv/blog/tokin-token-native-agent-rl-gateway-guide/

Mycelium Protocol's independent work is the pinned-source audit and bounded local smoke check, separate from the official measurements and suggested deployment configurations above.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
