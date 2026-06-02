---
title: "Rapid-MLX：Apple Silicon 最快本地 AI 推理，比 Ollama 快 4.2x，100% 工具调用"
titleEn: "Rapid-MLX: Fastest Local AI Inference on Apple Silicon — 4.2x Faster Than Ollama, 100% Tool Calling, Claude Code/Cursor Ready"
description: "Rapid-MLX 是专为 Apple Silicon 优化的本地 LLM 推理引擎：0.08s 缓存首字延迟、100% 工具调用成功率、17 种工具解析器、提示缓存、推理分离、云端路由。兼容 OpenAI API，可直接与 Claude Code、Cursor、Aider 配合使用。2.6k Star，v0.6.71。"
descriptionEn: "Rapid-MLX is a local LLM inference engine optimized for Apple Silicon: 0.08s cached TTFT, 100% tool calling, 17 tool parsers, prompt cache, reasoning separation, and cloud routing. OpenAI-compatible API. Works with Claude Code, Cursor, and Aider out of the box. 2.6k stars, v0.6.71."
pubDate: "2026-06-02"
updatedDate: "2026-06-02"
category: "Tech-News"
tags: ["Apple Silicon", "本地LLM", "Rapid-MLX", "MLX", "工具调用", "Claude Code", "Cursor", "推理引擎", "开源", "本地部署", "Ollama"]
heroImage: "../../assets/images/rapid-mlx-apple-silicon-inference-banner.jpg"
---

Ollama 是目前最流行的本地大模型运行方案，但它不是针对 Apple Silicon 专门优化的。Rapid-MLX 是。

`raullenchai/Rapid-MLX` 建立在苹果自己的 MLX 框架之上，利用 Apple Silicon 的统一内存架构（CPU、GPU、神经引擎共享同一块内存池）做了深度优化，实测速度比 Ollama 快 4.2x，首字延迟（缓存命中时）低至 **0.08 秒**。

> 📌 GitHub：https://github.com/raullenchai/Rapid-MLX  
> 安装：`brew install raullenchai/rapid-mlx/rapid-mlx` 或 `pip install rapid-mlx`  
> License：Apache-2.0 | Stars：2.6k | 最新版本：v0.6.71（2026-06-01）

## 三行命令跑起来

```bash
# 安装
brew install raullenchai/rapid-mlx/rapid-mlx

# 直接对话（默认加载 qwen3.5-4b，首次自动下载）
rapid-mlx chat

# 或者启动 HTTP 服务器
rapid-mlx serve qwen3.5-4b
```

服务启动后，`http://localhost:8000/v1` 就是一个完整的 OpenAI 兼容端点。任何支持 OpenAI API 的应用，改一下 `base_url` 就能接入。

## 性能：不同配置 Mac 实测速度

Rapid-MLX 的速度优势来自 MLX 框架对 Apple Silicon 统一内存的原生支持——模型权重直接在 GPU 和 CPU 共享的内存里，不需要跨总线复制数据。

| Mac 配置 | 推荐模型 | 速度 | 显存占用 |
|----------|---------|------|---------|
| **16 GB** MacBook Air | Qwen3.5-4B 4bit | 160 tok/s | 2.4 GB |
| **32 GB** Mac Mini | Nemotron-Nano 30B 4bit | 141 tok/s | 18 GB |
| **32 GB** Mac Mini | Qwen3.6-35B-A3B 4bit | 95 tok/s | 20 GB |
| **64 GB** Mac Studio | Qwen3.5-35B 8bit | 83 tok/s | 37 GB |
| **96 GB** Mac Studio | Qwen3.5-122B mxfp4 | 57 tok/s | 65 GB |
| **128 GB** Mac Studio Ultra | DeepSeek V4 Flash 158B 2bit | 56 tok/s | 91 GB |

tok/s 大致等于每秒输出的词数。160 tok/s 在对话场景下已经比人的阅读速度快。

## 100% 工具调用：17 种解析器

工具调用（Tool Calling/Function Calling）是 Claude Code、Cursor 等编码助手的核心能力。Rapid-MLX 内置 17 种工具调用解析器，覆盖不同模型的输出格式差异，宣称 100% 工具调用成功率。

**MHI（模型-Agent 适配指数）**是项目自定义的评测指标：

```
MHI = 0.50 × 工具调用成功率 + 0.30 × HumanEval + 0.20 × MMLU
```

| 模型 | 最优 MHI | 工具调用 |
|------|---------|---------|
| Qwopus 27B | **92** | 100% |
| Llama 3.3 70B | **83** | 100% |
| Qwen3.5 27B | **82** | 100% |
| Gemma 4 26B | **62** | 100% |
| Nemotron-Nano 30B | **59** | 91-93% |

## 与 Claude Code / Cursor / Aider 集成

**Claude Code**（一行命令）：

```bash
OPENAI_BASE_URL=http://localhost:8000/v1 claude
```

**Cursor**（Settings → Models → Add Model）：

```
OpenAI API Base: http://localhost:8000/v1
API Key:         not-needed
Model name:      default
```

**Aider**：

```bash
aider --openai-api-base http://localhost:8000/v1 --openai-api-key not-needed
```

还支持：PydanticAI、LangChain、smolagents、OpenCode、Hermes Agent、LibreChat、Open WebUI、Continue.dev 等，每个都有对应的配置文档和集成测试（项目共 3200+ 测试用例）。

## 提示缓存 + 推理分离

两个不那么显眼但很实用的特性：

**提示缓存（Prompt Cache）**：重复前缀（比如 system prompt）命中缓存后，TTFT 降至 0.08 秒。这对编码助手场景意义很大——每次对话都带着长 system prompt，有缓存就不用重复计算。

**推理分离（Reasoning Separation）**：对支持 `<think>` 标签的模型（如 DeepSeek-R1），Rapid-MLX 可以把思维链（chain-of-thought）从最终答案里剥离出来，单独返回或直接丢弃，避免推理过程污染输出。

## 云端路由：本地跑不过来就自动转云

```bash
rapid-mlx serve qwen3.5-4b \
  --cloud-model deepseek/deepseek-chat \
  --cloud-threshold 10
```

设置 `--cloud-threshold 10`：如果预估新生成的 token 数超过 10，自动把请求路由到云端模型（这里是 DeepSeek）。本地处理简单任务，复杂任务上云——对有 API key 但也想用本地的用户，是个务实的混合策略。

v0.6.70（2026-06-01）修复了云端路由沉默失败的 bug——之前引擎删除导致路由逻辑被跳过、没有任何日志输出，现在已经修复并加入了回归测试。

## 65 个模型别名，21 个模型家族

`rapid-mlx models` 列出当前支持的全部别名。涵盖：Qwen3.5（全尺寸系列）、Qwen3.6（256专家 MoE）、Llama 3.3、Gemma 4、DeepSeek-R1、DeepSeek V4 Flash、Nemotron-Nano、MiniMax M2.7……几乎覆盖当前主流开源模型。

最新加入的 `minimax-m2.7`（v0.6.71）：稠密模型，支持推测解码，10B 活跃参数，解码速度快。

---

Rapid-MLX 的定位是明确的：**苹果芯片 Mac 用户的 Ollama 替代品**，速度更快、工具调用更可靠、与主流编码 Agent 集成更深。如果你用 Mac 跑本地大模型，值得试一下。

> 📌 GitHub：https://github.com/raullenchai/Rapid-MLX  
> v0.6.71 | Apache-2.0 | 2.6k Star

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Ollama is the most popular way to run local AI models — but it isn't optimized specifically for Apple Silicon. Rapid-MLX is.

`raullenchai/Rapid-MLX` is built on Apple's own MLX framework and takes advantage of Apple Silicon's unified memory architecture — CPU, GPU, and Neural Engine all share the same memory pool. The result: **4.2x faster than Ollama** on the same hardware, with cached TTFT (Time To First Token) as low as **0.08 seconds**.

> 📌 GitHub: https://github.com/raullenchai/Rapid-MLX  
> Install: `brew install raullenchai/rapid-mlx/rapid-mlx` or `pip install rapid-mlx`  
> License: Apache-2.0 | Stars: 2.6k | Latest: v0.6.71 (2026-06-01)

## Up in Three Commands

```bash
# Install
brew install raullenchai/rapid-mlx/rapid-mlx

# Chat directly (loads qwen3.5-4b by default, downloads on first run)
rapid-mlx chat

# Or serve an OpenAI-compatible HTTP endpoint
rapid-mlx serve qwen3.5-4b
```

Once the server is running, `http://localhost:8000/v1` is a fully OpenAI-compatible endpoint. Any app that works with the OpenAI API works with Rapid-MLX by changing one URL.

## Performance: Real Numbers Across Mac Configs

Rapid-MLX's speed advantage comes from MLX's native support for Apple Silicon unified memory — model weights live directly in the shared memory pool, with no cross-bus copies.

| Mac Config | Recommended Model | Speed | Memory |
|------------|------------------|-------|--------|
| **16 GB** MacBook Air | Qwen3.5-4B 4bit | 160 tok/s | 2.4 GB |
| **32 GB** Mac Mini | Nemotron-Nano 30B 4bit | 141 tok/s | 18 GB |
| **32 GB** Mac Mini | Qwen3.6-35B-A3B 4bit | 95 tok/s | 20 GB |
| **64 GB** Mac Studio | Qwen3.5-35B 8bit | 83 tok/s | 37 GB |
| **96 GB** Mac Studio | Qwen3.5-122B mxfp4 | 57 tok/s | 65 GB |
| **128 GB** Mac Studio Ultra | DeepSeek V4 Flash 158B 2bit | 56 tok/s | 91 GB |

160 tok/s is faster than human reading speed. At the high end, a 122B parameter model running locally at 57 tok/s would have been a cloud-only proposition two years ago.

## 100% Tool Calling: 17 Parsers

Tool calling is the backbone of coding agents like Claude Code and Cursor. Rapid-MLX ships 17 tool call parsers covering the output format variations across different model families, with claimed 100% tool calling success rates on supported models.

The project defines **MHI (Model-Harness Index)** to measure compatibility:

```
MHI = 0.50 × Tool Calling + 0.30 × HumanEval + 0.20 × MMLU
```

| Model | Best MHI | Tool Calling |
|-------|---------|-------------|
| Qwopus 27B | **92** | 100% |
| Llama 3.3 70B | **83** | 100% |
| Qwen3.5 27B | **82** | 100% |
| Gemma 4 26B | **62** | 100% |
| Nemotron-Nano 30B | **59** | 91-93% |

## Claude Code / Cursor / Aider Integration

**Claude Code** (one-liner):

```bash
OPENAI_BASE_URL=http://localhost:8000/v1 claude
```

**Cursor** (Settings → Models → Add Model):

```
OpenAI API Base: http://localhost:8000/v1
API Key:         not-needed
Model name:      default
```

**Aider**:

```bash
aider --openai-api-base http://localhost:8000/v1 --openai-api-key not-needed
```

Also supported: PydanticAI, LangChain, smolagents, OpenCode, Hermes Agent, LibreChat, Open WebUI, Continue.dev — each with documented setup and integration tests (3,200+ test cases total).

## Prompt Cache + Reasoning Separation

Two less-visible but practically important features:

**Prompt Cache**: Repeated prefixes (e.g. long system prompts) hit cache and bring TTFT down to 0.08s. For coding agents that send the same system context on every turn, this is a meaningful latency reduction.

**Reasoning Separation**: For models that support `<think>` tags (DeepSeek-R1, etc.), Rapid-MLX can strip chain-of-thought from the final response — returning it separately or discarding it entirely. Pass `--think` to surface it in the REPL; leave it off to keep responses clean.

## Cloud Routing: Overflow Complex Requests to the Cloud

```bash
rapid-mlx serve qwen3.5-4b \
  --cloud-model deepseek/deepseek-chat \
  --cloud-threshold 10
```

When the estimated new token count exceeds the threshold, the request routes to the cloud model instead. Simple tasks stay local; complex tasks go cloud. A practical hybrid for users who have API keys but prefer local for most work.

v0.6.70 (2026-06-01) fixed a silent failure in cloud routing that had been broken for ~6 weeks — routing silently fell through without logging. Now repaired with regression tests that catch the original failure patterns at the AST level.

## 65 Model Aliases, 21 Families

`rapid-mlx models` lists all available aliases. Coverage includes: Qwen3.5 (full size range), Qwen3.6 (256-expert MoE), Llama 3.3, Gemma 4, DeepSeek-R1, DeepSeek V4 Flash (158B-A13B, 1M context), Nemotron-Nano, MiniMax M2.7.

The newest addition in v0.6.71: `minimax-m2.7` — dense model, speculative decoding support, 10B active parameters for fast decoding.

---

Rapid-MLX's positioning is clear: **a faster, more tool-call-reliable Ollama alternative for Apple Silicon Macs**, with deeper integration into modern coding agents. If you run local models on a Mac, it's worth benchmarking against your current setup.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
