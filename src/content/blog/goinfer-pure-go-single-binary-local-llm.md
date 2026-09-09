---
title: "整个大模型装进一个文件：goinfer 用纯 Go 跑推理，没有 Python、没有 llama.cpp、没有 CUDA 工具链"
titleEn: "An Entire LLM in One File: goinfer Runs Inference in Pure Go — No Python, No llama.cpp, No CUDA Toolkit"
description: "goinfer 是一个纯 Go、无 cgo 的本地推理引擎，编译出单个静态二进制，支持 27 个模型家族、四种序列混合架构，还能把权重烤进可执行文件做成「一个文件就是一个模型」。更难得的是它的基准测试极度诚实：Mac 上比 Ollama 慢 13-18%，Linux CUDA 上快 5%，深上下文会落后——数字和机器、量化、日期一起公开。"
descriptionEn: "goinfer is a pure-Go, cgo-free local inference engine that compiles to a single static binary. It covers 27 model families and all four sequence-mixing architectures, and can bake weights into the executable so one file is the whole model. What stands out most is the honesty of its benchmarks: 13-18% behind Ollama on Mac, ~5% ahead on Linux CUDA, and behind at depth — every number published with machine, quantization and date."
pubDate: "2026-09-09"
updatedDate: "2026-09-09"
category: "Tech-Experiment"
tags: ["Go", "本地推理", "local-first", "开源", "LLM", "单文件部署", "结构化输出", "GGUF"]
heroImage: "../../assets/images/goinfer-pure-go-single-binary-local-llm-banner.jpg"
---

> 📌 项目地址：https://github.com/townsendmerino/goinfer
> 文档站（Go 工程师的推理入门书）：https://townsendmerino.github.io/goinfer/
> 协议：MIT ｜ 语言：Go ｜ Star：12（2026-09-09）｜ 状态：Pre-1.0

## 一句话结论

**如果你被 Python 依赖、CUDA 工具链、llama.cpp 编译这三件事折磨过，goinfer 值得你花二十分钟看一眼。**

它把本地推理压缩成 Go 世界最朴素的那个形态：`go install`，出来一个静态二进制，拷到哪台机器都能跑。极端一点还能把模型权重直接烤进可执行文件——**1.81 GB 的单个文件，双击就是一个能对话的 1.5B 模型**，不下载、不安装、离线可用。

## 它解决的痛点：部署摩擦

本地推理这条路上，真正劝退人的往往不是模型效果，是**装不上**。

- Python 环境冲突，一个 `pip install` 拖出半个生态
- CUDA 工具链版本对不上，编译几十分钟后失败
- llama.cpp 要选架构、要 CMake、要 C++ 编译器
- 换台机器，全套重来

goinfer 的回答是：**这些全都不要**。

> 「It builds with no toolchain of any kind — no CUDA toolkit, no C++ compiler, no CMake, no Python — and cross-compiles like any other Go program.」

纯 Go、无 cgo，意味着交叉编译和普通 Go 程序完全一样。给同事发个演示、往气隙机器上部署、在 workshop 现场分发——这些场景下"一个文件"的价值远大于几个百分点的吞吐差距。

## 装它有两条路

**下载二进制**，什么都不用装：

```bash
# macOS arm64；换后缀适配你的平台
curl -fsSL -o goinfer-serve https://github.com/townsendmerino/goinfer/releases/latest/download/goinfer-serve-darwin-arm64
chmod +x goinfer-serve
```

**从源码构建**，需要 Go 1.27+：

```bash
go install github.com/townsendmerino/goinfer/cmd/serve@latest
```

这里有个坑作者写得很明白：上面那条构建的是 **CPU 版**。要 GPU 得走后端各自的入口，`-tags metal` 加在 `cmd/serve` 上**不工作**，而且会在构建时明确报错告诉你：

```bash
go install github.com/townsendmerino/goinfer/metal/cmd/serve@latest              # macOS
go install -tags cuda github.com/townsendmerino/goinfer/cuda/cmd/serve@latest    # Linux + NVIDIA
```

Release 里下载的 `goinfer-serve` 已经带好了——macOS 带 Metal，Linux 带 CUDA。跑 `goinfer-serve --version` 能看到当前这个二进制带了哪些后端。

## 四档产物，最后一档很特别

以 darwin-arm64 的 v0.16.0 资产为例：

| 资产 | 体积 | 是什么 |
|---|---|---|
| `goinfer-serve-<os>-<arch>` | ~16 MB | **服务端**——OpenAI + Anthropic API、Web UI、GPU 内建 |
| `goinfer-chat-<os>-<arch>` | 8.3 MB | 单次运行时，指向你自己的 GGUF |
| `goinfer-chat-0.5b-<os>-<arch>` | 652 MB | 运行时**和模型**在同一个文件里 |
| `goinfer-chat-1.5b-<os>-<arch>` | 1.81 GB | 同上，装的是 1.5B 编码模型 |

最后两档就是"一个文件就是一个模型"。而且这不是作者钦定的两个特例——**从源码检出可以对任意支持的检查点跑同一条流水线**：

```bash
go run ./demo/chat pull bartowski/google_gemma-3-4b-it-GGUF:Q4_K_M -embed darwin/arm64 linux/amd64
# → demo/chat/dist/goinfer-chat-google_gemma-3-4b-it-{darwin-arm64,linux-amd64}
```

出来就是静态、无 cgo、权重在里面的二进制。README 特意提醒：**模型的许可证跟着二进制走**，你要分发就得自己满足那个许可证。

## 拉模型不用装额外工具

运行时能直接从 HuggingFace 拉 GGUF，不需要 `huggingface-cli`：

```bash
./goinfer-chat-darwin-arm64 pull Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF          # 看这个仓库有什么
./goinfer-chat-darwin-arm64 pull Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF:q4_k_m   # 拉一个量化
./goinfer-chat-darwin-arm64 pull demo:1.5b                                       # 项目自己审过并锁定的
```

传输中断会续传，sha256 对着 HuggingFace 声明的值校验。**goinfer 自己不托管任何权重**，下载都来自 HuggingFace。

甚至可以省掉 pull 这一步，`--model` 直接接同样的引用，首次使用时下载：

```bash
goinfer-serve -model hf:Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF:q4_k_m
```

想要浏览器界面就加 `-web`，本地 `http://127.0.0.1:8080` 起一个 UI，聊天、浏览 HF 仓库、带进度条拉权重都能干。整个 UI 是**一个内嵌的 HTML 文件，没有外部资源**，所以和这个项目的其他部分一样离线可用。

## 基准测试：这部分才是真正让我高看一眼的地方

绝大多数推理项目的 README 会挑一个自己赢的场景放个柱状图。goinfer 不是这么写的。

**Mac 冷启动**（M1 Pro / 16GB，对比 Ollama 0.32.5 干同样的事）：从零到拿到回答，**25 秒 vs 33 秒**，8MB 二进制、无守护进程、跑完不留东西。但作者紧接着说明：*这一段只是冷启动，稳态解码是另一个测量*。

**Mac 稳态解码**（v0.17.1，确认带 Metal，Qwen2.5-Coder-1.5B q4_K_M，交错测试）：

> **goinfer 比 Ollama 慢 13-18%。**

README 里原样写着这个数字，还附了一句：这替换了之前一个 v0.16.0 的读数，因为复核发现那次测的是一个**没链接 Metal 后端**的 Mac 二进制，测的不是引擎本身。

**Linux + GPU**：冷启动 56.5 秒，其中大头是 1.71 GiB 二进制的网络下载（~31.5 MB/s）——作者明确说这不是一个固定数字，是你网速的函数。稳态 CUDA 解码，匹配量化、交错测试、客户端侧 tok/s：goinfer **192.8 tok/s** vs Ollama **183.6 tok/s**，快约 5%。

然后又补了一刀：这次是短补全，等效上下文深度约 128；**基准文档里更深的格子显示 Ollama 会随上下文增长反超**。

最后是我最欣赏的一句：

> 「Measure it yourself rather than trust either number」（别信任何一边的数字，自己测）

harness 代码 `scripts/bench_peer.py` 就在仓库里，两边同样的权重、只测解码、交错执行、每格重启服务、来源信息戳进输出文件。

这种写法在 AI 工具圈里非常罕见。**一个愿意在 README 里写"我在你最可能用的那台 Mac 上比对手慢 13-18%"的项目，它给出的其他数字可信度也高得多。**

## 跑比内存还大的模型

这是很实际的一个场景：20-35B 级别的 MoE 塞不进 16GB 内存，硬塞会在任何东西报错之前先把机器拖进 swap。

**内存侧**用 `-stream-weights`：

```bash
goinfer-serve -stream-weights -weight-cache 6GiB -model ~/models/gpt-oss-20b-MXFP4.gguf
```

常驻内存被压在 `-weight-cache` 附近而不是模型大小，因为只有 token 实际路由到的专家才常驻。M1 Pro / 16GB 上跑 21GB 的 35B-A3B 实测：**不加这个参数，5 秒内 swap 涨 7.8 GB；加了之后 RSS 峰值 8.95 GB 然后回落到 2.7 GB，零 swapout**。

注意作者划的界限：**这是 `goinfer-serve` 的活，不是 `goinfer-chat` 的**。单次运行时设计上就是权重全常驻，没有 `-stream-weights`。模型比内存大，就用服务端。

**显存侧**的规则更硬：

> 在 cuda/metal 上，GPU 意味着完全常驻，没有中间状态。

两个后端都没有部分/分级 GPU 路径。一个建不起常驻 runner 的模型或架构，会直接降级到 CPU。**稠密模型比你的卡大，这里没有部分 GPU 的故事**——只有内存侧的 `-stream-weights` 或者 CPU。

**但 MoE 有**，那就是 `-moe-cache-experts`：非专家的核心常驻，token 实际路由到的专家按需从主机流进显存。在 RTX 2070 SUPER 8GB 上跑 `gemma-4-26b-a4b`（26B-A4B，128 专家 top-8）：**30 个缓存专家槽时 16.12 tok/s**，瓶颈是 PCIe 主机→显存的带宽，不是 kernel 或 MoE 实现的问题。

## 一个模型无法违反的 Go struct

这个特性对做 Agent 的人价值很高：

```go
type Person struct {
    Name string   `json:"name"`
    Age  int      `json:"age"`
    Tags []string `json:"tags"`
}

g, _ := constrain.GrammarFromStruct(Person{})       // struct → JSON Schema → 语法
sp.LogitProcessor = constrain.NewMasker(g, toks, eos).StopWhenComplete().Process

out := generate(sp)                                  // 受约束解码
var p Person
_ = json.Unmarshal(out, &p)                          // 形状有保证，数值没有
```

关键在于实现方式：约束是**在 goinfer 增量字节级语法上的 logit mask**——每一步会破坏 schema 的 token 被置为 −∞，所以非法 token 是**不可达的**，不是"重试到对为止"，是**物理上生不出来**。

这和"提示模型输出 JSON 然后 try/except 重试"是两个量级的可靠性。注意 README 的措辞很克制：**形状（shape）有保证，数值（magnitude）没有**——它保证你能 unmarshal 成功，不保证 Age 字段里的数字是对的。

支持的 schema 子集：对象（必需 + 可选、`additionalProperties:false`）、数组（`items`/`minItems`/`maxItems`）、`string`/`number`/`integer`/`boolean`/`null`、`enum`/`const`，任意嵌套。有一个基于属性的测试断言每次受约束生成都能通过其 schema 校验。

## 它跑什么

- **27 个模型家族**——Gemma 3/4、Qwen 2.5/3、Llama、Mistral、Mixtral、Phi-3、DeepSeek/MLA、GLM、Kimi、Granite、Nemotron、Mellum 等
- **四种序列混合家族全覆盖**——softmax·GQA、门控线性（DeltaNet）、状态空间（Mamba-2）、隐式 KV（MLA），加上稠密和稀疏 MoE
- **加载器**——GGUF、safetensors、GPTQ、AWQ，以及预量化的 `.giw` 包
- **量化**——f32、int8、int8int8、int4（W4A8），每个家族有 HuggingFace logit 对齐门禁
- **GPU**——WebGPU 全平台，加上无 cgo 的 CUDA 和 Metal
- **服务**——OpenAI 兼容 + Anthropic Messages 端点，多模型、视觉、嵌入

量化那一条作者又诚实了一把：**一次对齐测试能证明什么，取决于那台机器有哪些 fixture，缺 fixture 会静默跳过而不是失败**。所以一次读作 `28 ran / 20 skipped / 0 failed` 的运行是通过。他要求引用的时候**报数字，不要只说"绿了"**。

## 它明确不做什么

> 「It is **not a serving engine**」

没有连续批处理、没有 paged attention，一次一个生成，后面挂一个有界队列。要用并发请求喂饱数据中心 GPU，那是 vLLM 的活。

goinfer 的目标是**单用户本地推理**：一个进程、一台机器、batch-1 解码、靠拷贝文件部署。

这个定位说得非常清楚，省了很多人的时间。

## 值不值得试

**推荐给：** Go 工程师、要把 LLM 嵌进自己程序的人、需要气隙/离线部署的人、需要结构化输出强保证的人、被 Python/CUDA 环境折磨够了的人。

**不推荐给：** 需要高并发服务的人（用 vLLM）、要榨干最后 15% 吞吐的人（Mac 上确实慢于 Ollama）、需要长上下文最优性能的人（深度上会被反超）。

**状态提醒：** Pre-1.0。前向传播/量化契约有对齐门禁且稳定，但加载器和架构描述符表面还在动。哪些接口会在 v1.0 被 semver 绑定已经定了（`docs/api-tiers.md`，2026-08-18 签署），但**在 v1.0 tag 之前不生效**。

顺带一提，这个项目还写了一本**给 Go 工程师的推理入门书**（十一章，在线可读），每章结尾落在这个仓库里的一个实测数字上。作者说如果只读一章，读第十一章——那章讲的是**这个仓库里的测量曾经怎么出错**。

一个把自己测错的历史写进文档并推荐你优先读的项目，我觉得可以给点信任。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/townsendmerino/goinfer
> Docs (an inference primer for Go engineers): https://townsendmerino.github.io/goinfer/
> License: MIT ｜ Language: Go ｜ Stars: 12 (2026-09-09) ｜ Status: Pre-1.0

## The Short Version

**If Python dependencies, CUDA toolchains, or compiling llama.cpp have ever cost you an afternoon, goinfer is worth twenty minutes of your attention.**

It compresses local inference into the most ordinary shape in the Go world: `go install`, out comes a static binary, copy it anywhere and it runs. Taken to the extreme, it will bake the model weights into the executable — **a single 1.81 GB file that is a working 1.5B chat model**, no download, no install, offline.

## The Pain It Addresses: Deployment Friction

What actually drives people off local inference usually isn't model quality. It's **not being able to install the thing**.

- Python environment conflicts, where one `pip install` drags in half an ecosystem
- CUDA toolchain version mismatches that fail after forty minutes of compiling
- llama.cpp wanting an architecture choice, CMake, and a C++ compiler
- Move to another machine, do it all again

goinfer's answer: **none of that**.

> "It builds with no toolchain of any kind — no CUDA toolkit, no C++ compiler, no CMake, no Python — and cross-compiles like any other Go program."

Pure Go with no cgo means cross-compilation behaves exactly like any other Go program. Handing a demo to a colleague, deploying to an air-gapped machine, distributing at a workshop — in those situations "one file" is worth far more than a few percent of throughput.

## Two Ways In

**Download a binary**, install nothing:

```bash
# macOS arm64; swap the suffix for your platform
curl -fsSL -o goinfer-serve https://github.com/townsendmerino/goinfer/releases/latest/download/goinfer-serve-darwin-arm64
chmod +x goinfer-serve
```

**Build from source**, needs Go 1.27+:

```bash
go install github.com/townsendmerino/goinfer/cmd/serve@latest
```

There's a trap the author documents clearly: that builds the **CPU** server. GPU means building the backend's own entrypoint — `-tags metal` on `cmd/serve` does **not** work and fails the build saying so:

```bash
go install github.com/townsendmerino/goinfer/metal/cmd/serve@latest              # macOS
go install -tags cuda github.com/townsendmerino/goinfer/cuda/cmd/serve@latest    # Linux + NVIDIA
```

The release assets already carry this — Metal on macOS, CUDA on Linux. `goinfer-serve --version` prints which backends a given binary has.

## Four Artifacts, and the Last One Is Unusual

Sizes are the darwin-arm64 assets of v0.16.0:

| Asset | Size | What it is |
|---|---|---|
| `goinfer-serve-<os>-<arch>` | ~16 MB | the **server** — OpenAI + Anthropic APIs, web UI, GPU built in |
| `goinfer-chat-<os>-<arch>` | 8.3 MB | the single-shot runtime; point it at your own GGUF |
| `goinfer-chat-0.5b-<os>-<arch>` | 652 MB | runtime **and** model in one file |
| `goinfer-chat-1.5b-<os>-<arch>` | 1.81 GB | same, with the 1.5B coder model |

The last two are "one file is the whole model." And this isn't limited to two blessed models — **from a source checkout you can run the same pipeline for any supported checkpoint**:

```bash
go run ./demo/chat pull bartowski/google_gemma-3-4b-it-GGUF:Q4_K_M -embed darwin/arm64 linux/amd64
# → demo/chat/dist/goinfer-chat-google_gemma-3-4b-it-{darwin-arm64,linux-amd64}
```

Out comes a static, cgo-free binary with the weights inside. The README is careful to note: **the model's license travels with the binary**, and redistributing one makes that license your problem to satisfy.

## Pulling Models Without Extra Tooling

The runtime fetches GGUFs from HuggingFace directly, no `huggingface-cli` needed:

```bash
./goinfer-chat-darwin-arm64 pull Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF          # see what a repo publishes
./goinfer-chat-darwin-arm64 pull Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF:q4_k_m   # fetch one quant
./goinfer-chat-darwin-arm64 pull demo:1.5b                                       # models goinfer itself vets and pins
```

Interrupted transfers resume; the sha256 is verified against what HuggingFace declares. **goinfer hosts no weights** — downloads come from HuggingFace.

You can skip the pull step entirely; `--model` takes the same reference and fetches on first use:

```bash
goinfer-serve -model hf:Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF:q4_k_m
```

Add `-web` for a local UI at `http://127.0.0.1:8080` — chat, browse a HF repo, pull a checkpoint with live progress. The whole UI is **one embedded HTML file with no external assets**, so like everything else here it works offline.

## The Benchmarks Are Why I Take This Project Seriously

Most inference projects pick a scenario they win and put a bar chart in the README. goinfer doesn't.

**Mac cold start** (M1 Pro / 16GB, against Ollama 0.32.5 doing the same thing): from nothing to an answer, **25s vs 33s**, from an 8MB binary with no daemon and nothing left running. The author immediately qualifies it: *that leg is cold start only; steady-state decode is a separate measurement*.

**Mac steady-state decode** (v0.17.1, Metal confirmed, Qwen2.5-Coder-1.5B q4_K_M, interleaved):

> **goinfer is 13-18% behind Ollama.**

That number is printed as-is in the README, with a note that it replaces an earlier v0.16.0 reading, because review found that run was measuring a Mac binary **with no Metal backend linked in** — not the engine.

**Linux + GPU**: cold start 56.5s, dominated by a 1.71 GiB binary download at ~31.5 MB/s — which the author explicitly calls a function of your connection, not a fixed number. Steady-state CUDA decode, matched quant, interleaved, client-side tok/s: goinfer **192.8 tok/s** vs Ollama **183.6 tok/s**, ~5% ahead.

Then another qualification: this was a short completion at an effective depth of ~128, and **the benchmark document's deeper cells show Ollama pulling ahead as context grows**.

And the line I like most:

> "Measure it yourself rather than trust either number"

The harness, `scripts/bench_peer.py`, is committed: same weights both sides, decode-only, interleaved, server restarted per cell, provenance stamped into the output.

This is rare in the AI tooling world. **A project willing to write "I'm 13-18% slower than my competitor on the machine you're most likely using" in its own README earns a lot of credibility for every other number it publishes.**

## Running a Model Bigger Than Your RAM

A very practical scenario: a 20-35B-class MoE doesn't fit in 16GB, and loading it anyway drives the machine into swap before anything reports a problem.

**RAM side**, `-stream-weights`:

```bash
goinfer-serve -stream-weights -weight-cache 6GiB -model ~/models/gpt-oss-20b-MXFP4.gguf
```

Resident memory is then capped near `-weight-cache` rather than the model size, because only the experts a token actually routes to stay resident. Measured on an M1 Pro / 16GB with a 21GB 35B-A3B: **without the flag, +7.8 GB of swap in five seconds; with it, RSS peaked at 8.95 GB and fell back to 2.7 GB, with zero swapouts**.

Note the boundary the author draws: **this is `goinfer-serve`'s job, not `goinfer-chat`'s**. The single-shot runtime holds all weights resident by design. If the model is bigger than your RAM, reach for the server.

**VRAM side** the rule is harder:

> On cuda/metal, GPU means fully resident, full stop.

Neither backend has a partial or staged GPU path. A model or architecture that can't build the resident runner declines straight to CPU. **A dense model bigger than your card has no partial-GPU story here** — only `-stream-weights` (RAM side) or the CPU.

**A MoE does**, via `-moe-cache-experts`: the non-expert core stays resident while a slot cache of routed experts streams host→VRAM per token. On an RTX 2070 SUPER 8GB running `gemma-4-26b-a4b` (26B-A4B, 128 experts top-8): **16.12 tok/s at 30 cached expert slots**, capacity-bound on PCIe streaming rather than a kernel or MoE deficiency.

## A Go Struct the Model Cannot Violate

High value if you're building agents:

```go
type Person struct {
    Name string   `json:"name"`
    Age  int      `json:"age"`
    Tags []string `json:"tags"`
}

g, _ := constrain.GrammarFromStruct(Person{})       // struct → JSON Schema → grammar
sp.LogitProcessor = constrain.NewMasker(g, toks, eos).StopWhenComplete().Process

out := generate(sp)                                  // constrained decode
var p Person
_ = json.Unmarshal(out, &p)                          // shape guaranteed, not magnitude
```

The mechanism matters: the constraint is a **logit mask over an incremental byte-level grammar** — at every step, tokens that would break the schema are set to −∞, so an invalid token is **unreachable**. Not retried until it works. Impossible.

That's a different order of reliability from "prompt the model for JSON, then try/except and retry." Note the careful wording: **shape is guaranteed, magnitude is not** — you're promised the unmarshal succeeds, not that the number in `Age` is right.

Supported subset: objects (required + optional, `additionalProperties:false`), arrays (`items`/`minItems`/`maxItems`), `string`/`number`/`integer`/`boolean`/`null`, `enum`/`const`, and arbitrary nesting. A property-based test asserts every constrained generation validates against its schema.

## What It Runs

- **27 model families** — Gemma 3/4, Qwen 2.5/3, Llama, Mistral, Mixtral, Phi-3, DeepSeek/MLA, GLM, Kimi, Granite, Nemotron, Mellum and more
- **All four sequence-mixing families** — softmax·GQA, gated-linear (DeltaNet), state-space (Mamba-2), latent-KV (MLA), plus dense and sparse MoE
- **Loaders** — GGUF, safetensors, GPTQ, AWQ, and prequantized `.giw` bundles
- **Quantization** — f32, int8, int8int8, int4 (W4A8), with a HuggingFace logit-parity gate per family
- **GPU** — WebGPU everywhere, plus cgo-free CUDA and Metal
- **Serving** — OpenAI-compatible and Anthropic Messages endpoints, multi-model, vision, embeddings

On quantization the author is honest again: **what a parity run proves is scoped to the fixtures that machine has, and a missing fixture skips silently rather than failing**. A run reading `28 ran / 20 skipped / 0 failed` is a pass. He asks you to **quote a run's counts, not the word "green."**

## What It Explicitly Isn't

> "It is **not a serving engine**"

No continuous batching, no paged attention, one generation at a time behind a bounded queue. Saturating a datacentre GPU with concurrent requests is vLLM's job.

goinfer targets **single-user local inference**: one process, one machine, batch-1 decode, deployed by copying a file.

Stating that this clearly saves a lot of people a lot of time.

## Worth Trying?

**Recommended for:** Go engineers, anyone embedding an LLM into their own program, air-gapped or offline deployments, anyone needing hard structured-output guarantees, anyone who's had enough of Python and CUDA environments.

**Not for:** high-concurrency serving (use vLLM), squeezing out the last 15% of throughput (it is genuinely slower than Ollama on Mac), or optimal long-context performance (it gets overtaken at depth).

**Status caveat:** Pre-1.0. The forward-pass and quantization contract is parity-gated and stable, but the loader and architecture-descriptor surface is still moving. Which surfaces v1.0 will semver-bind is already decided (`docs/api-tiers.md`, signed off 2026-08-18), but **it doesn't take effect until the v1.0 tag**.

One more thing: the project ships **an inference primer for Go engineers** — eleven chapters, readable online, each ending in a measured number from this repo. The author says if you read one chapter, read chapter 11 — the one about **how measurements in this tree have gone wrong**.

A project that documents its own measurement mistakes and tells you to read that part first has earned some trust.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
