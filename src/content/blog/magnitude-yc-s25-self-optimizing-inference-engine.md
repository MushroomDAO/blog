---
title: "Magnitude（YC S25）：在你的机器上编译内核，Metal decode 比 llama.cpp 快 92%"
titleEn: "Magnitude (YC S25): Compiles Kernels on Your Machine, 92% Faster Decode Than llama.cpp on Metal"
description: "magnitudedev/magnitude，Apache-2.0，6.3K stars，Rust。YC S25 团队出品的本地推理引擎，核心差异在于内核在你的硬件上编译调优，而不是发一套预编译的通用内核——Metal decode 自报比 llama.cpp 快 92%，CUDA 快 19%。桌面应用，macOS/Linux/Windows，自带 magnitude CLI，Discover 下载模型，Connections 一键接 Pi/OpenCode/Codex/Claude Code/Cline，OpenAI 兼容 API 端口 10100。HN 194 赞 97 条评论，基准数字有争议。"
descriptionEn: "magnitudedev/magnitude, Apache-2.0, 6.3K stars, Rust. A YC S25 local inference engine whose core difference is compiling and tuning kernels on your actual hardware rather than shipping generic precompiled kernels — 92% faster decode than llama.cpp on Metal, 19% on CUDA (self-reported). Desktop app for macOS/Linux/Windows, ships the magnitude CLI, Discover for models, Connections for one-click Pi/OpenCode/Codex/Claude Code/Cline integration, OpenAI-compatible API on port 10100. 194 HN upvotes, 97 comments debating the benchmarks."
pubDate: 2026-10-04
heroImage: "../../assets/images/magnitude-yc-s25-self-optimizing-inference-engine-banner.jpg"
category: "Tech-Experiment"
tags: ["本地推理", "Rust", "YC S25", "inference engine", "Apple Silicon", "CUDA", "Agent工具"]
lang: "zh-CN"
wechatTitle: "Magnitude：本机编译内核的YC本地推理引擎"
wechatDigest: "YC S25；Metal +92%/CUDA +19%；内核本机编译；接8款agent；Apache-2.0"
---

本地推理引擎已经不少了——llama.cpp、Ollama、LM Studio——它们用的是同一套思路：编译好一批针对常见硬件类别的通用内核，打包发布，用户装上就跑。

Magnitude 换了一条路：内核在你的机器上编译和调优，在第一次跑模型之前，针对你的具体硬件生成专用内核。

GitHub: https://github.com/magnitudedev/magnitude | ⭐ 6,331 | Apache-2.0 | Rust  
Launch HN: 194 分 97 条评论（基准数字有争议，后面细说）

---

## 核心设计：JIT 风格的内核编译

通用推理引擎的问题：Apple Silicon M 系列有 M1/M2/M3/M4，NVIDIA 有 3090/4090/5080/B200，AMD 有多代 ROCm……芯片之间的内存带宽、寄存器数量、SIMD 宽度差异很大。预编译内核只能针对「同类硬件」的一个平均水平做优化，跑在具体的某块芯片上不一定最快。

Magnitude 的做法：模型第一次运行前，在你的硬件上编译并调优内核。类似 C++ PGO（Profile-Guided Optimization）或 Julia 的 JIT——第一次有额外等待时间，之后跑起来更快。

官方给出的对比数据（vs llama.cpp）：

| 平台 | Prefill | Decode |
|------|---------|--------|
| Apple Silicon (Metal) | +9% | **+92%** |
| NVIDIA (CUDA) | +23% | **+19%** |

decode 提升幅度远大于 prefill，对长上下文 agent 任务（每步推理量大）尤其有意义。

除了速度，还有两个内存相关的特性：
- **每个 agent 会话减少 27% 内存占用**，session 结束后内存释放
- **共享前缀缓存树**：多个 agent 并发时共用前缀 KV cache，不会随 session 数量线性增长

---

## 安装与使用

**三步上手：**

```bash
# 1. 去 magnitude.dev/download 下载桌面应用，安装
# 2. 打开 Discover，选推荐模型下载
# 3. 打开 Connections，连接你的 agent
```

桌面应用安装完自带 `magnitude` CLI，不需要单独装。

**CLI 使用：**

```bash
# 启动（桌面应用会自动管理，也可以 CLI 手动运行）
magnitude serve

# API 端口 10100，兼容 OpenAI 格式
curl http://localhost:10100/v1/models
```

**支持的 agent（Connections 一键连接）：**  
Pi、OpenCode、Hermes、OpenClaw、Codex、Claude Code、Oh My Pi、Cline

其他任何支持 OpenAI 兼容 API 的工具，直接指向 `http://localhost:10100` 就行。

**硬件要求：**  
没有固定门槛。Apple Silicon（M1 起）、NVIDIA、AMD 显卡、纯 CPU 都能跑；内存越大能跑越大的模型。

---

## HN 的争议：基准数字可信度几何？

Launch HN 的 97 条评论里，最多讨论的是两个问题。

**问题一：跟 llama.cpp 比有意义吗？**

用户 `sebastienburel`：
> "On a Mac the baseline I'd want is MLX, not llama.cpp. llama.cpp isn't the fast path on Apple Silicon for most models."

直接指出 Apple Silicon 上 MLX（苹果官方框架）才是更合理的对比基准，比 llama.cpp 快的不止 Magnitude 一个。

Magnitude 团队（anerli）回应：
> "Yes MLX is generally a better comparison point overall for Apple. However against the MLX-based engines we've compared with so far, Magnitude will continue to have an edge, especially for decode kernels. Releasing that benchmark soon."

承认了这个问题，答应出 vs MLX 的基准，但截至文章发布时还没出。

**问题二：独立测试结果如何？**

用户 `bythreads` 在 M5 Max 128GB 上跑了多个 Qwen 模型（含 35B-A3B MoE），结论是：

> "the results are what i kinda expected to begin with, this adds next to no [value on this setup]"

不过 Magnitude 团队也承认了内存预留 bug（目前保留了过多内存 overhead），正在修复，理论上能跑更多模型。

**结论**：官方基准是真实的，但对比对象是 llama.cpp 而不是 MLX。在 Apple Silicon 上，MLX 才是更公允的参考线。vs MLX 的数据还没出，这是目前最大的信息缺口。

---

## 模型支持

Magnitude 不是「能跑 GGUF 就行」的通用引擎——它为主流开源权重系列手写优化内核，这是它超过通用引擎的原因，也是它支持模型数量少于 Ollama 的原因。

完整模型列表在 magnitude.dev/models。Discover 里有推荐列表和根据你的硬件自动过滤。

---

## 适合谁用

**适合：**
- 用 Pi、Codex、Claude Code 等 agent 工具跑 agent 任务，需要本地低延迟推理
- Apple Silicon 用户，想要比 Ollama/llama.cpp 更快的 decode 速度
- 多个 agent 并发的场景（共享前缀缓存有优势）

**暂时观望：**
- Apple Silicon 用户，已经跑了优化好的 MLX 引擎——等 Magnitude vs MLX 的基准出来再决定
- 需要跑冷门量化格式或长尾模型的用户——Magnitude 不是「万能 GGUF 加速器」
- Windows / Linux NVIDIA 用户：CUDA 路径确实有基准，但社区测试还少

---

## 一句话定位

Magnitude = 「在你的芯片上编译内核的本地推理引擎，为 agent 优化」。

如果你用 agent 工具频繁调用本地模型，并且在乎 decode 延迟（而不只是首 token 速度），值得装上试试——Discover 下模型，Connections 接 Claude Code，五分钟就能跑起来对比。

---

> Apache-2.0 开源，商用无限制。开源仅供学习参考，基准数字为官方自报，建议在自己硬件上验证。

---

<!--EN-->

## Magnitude (YC S25): Compiles Kernels on Your Machine Before Running Models

Most local inference engines ship the same way: compile a batch of kernels for generic hardware categories, package and release. Users install and run.

Magnitude takes a different path: kernels are compiled and tuned on your machine before the first model run, generating specialized kernels for your specific hardware.

GitHub: https://github.com/magnitudedev/magnitude | ⭐ 6,331 | Apache-2.0 | Rust

---

### Core Design: JIT-Style Kernel Compilation

Generic inference engines face a fundamental tradeoff: Apple Silicon M-series chips span M1 through M4, NVIDIA spans 3090 through B300, AMD has multiple ROCm generations. Memory bandwidth, register counts, and SIMD widths differ substantially across generations. Precompiled kernels target a hardware class average, not any specific chip.

Magnitude's approach: compile and tune kernels on your actual hardware before a model's first run — similar to C++ PGO or Julia's JIT. There's a one-time compilation cost; subsequent runs are faster.

**Benchmark claims (vs llama.cpp)**:

| Platform | Prefill | Decode |
|----------|---------|--------|
| Apple Silicon (Metal) | +9% | **+92%** |
| NVIDIA (CUDA) | +23% | **+19%** |

The large decode gap matters for agent workloads where each step generates substantial output.

Additional benefits:
- **27% less memory per agent session**, released when sessions end
- **Shared prefix cache tree**: multiple concurrent agents share KV caches, no linear memory growth

---

### Setup

Three steps:

1. Download the desktop app at magnitude.dev/download
2. Open **Discover**, pick a recommended model
3. Open **Connections**, connect your agent

The desktop app ships the `magnitude` CLI — no separate install needed. The API runs on port 10100, OpenAI-compatible.

**One-click agent connections**: Pi, OpenCode, Hermes, OpenClaw, Codex, Claude Code, Oh My Pi, Cline. Anything else pointing at `http://localhost:10100`.

**Hardware**: Apple Silicon (M1+), NVIDIA, AMD, or CPU-only. No fixed minimum — larger memory runs larger models.

---

### The HN Benchmark Debate

The 97 comments split mostly around two questions.

**Question 1: Is llama.cpp the right comparison?**

User `sebastienburel`: "On a Mac the baseline I'd want is MLX, not llama.cpp. llama.cpp isn't the fast path on Apple Silicon for most models."

The Magnitude team (anerli): "Yes MLX is generally a better comparison point overall for Apple. However against the MLX-based engines we've compared with so far, Magnitude will continue to have an edge, especially for decode kernels. Releasing that benchmark soon."

They acknowledged the gap and promised vs-MLX benchmarks — not yet published at time of writing.

**Question 2: What do independent tests show?**

One commenter benchmarked on M5 Max 128GB across several Qwen models and found the gains "next to nothing" on that specific setup. The team acknowledged memory reservation bugs (over-reserving overhead) currently in-progress for a fix.

**Bottom line**: the official benchmarks are real, but the comparison target is llama.cpp, not MLX. On Apple Silicon, MLX is a more honest reference point. The vs-MLX data is the biggest open question.

---

### Who Should Use It

**Good fit**: agent workloads on Pi/Codex/Claude Code that need low-latency local inference; Apple Silicon users who want faster decode than Ollama/llama.cpp; concurrent multi-agent setups that benefit from shared prefix caches.

**Worth waiting**: Apple Silicon users already on well-optimized MLX engines — wait for the vs-MLX benchmarks. Users needing long-tail model support or arbitrary GGUF formats — Magnitude writes hand-optimized kernels per model family, not a universal GGUF accelerator.

---

> Apache-2.0, commercial use unrestricted. Benchmarks are self-reported by the project — verify on your own hardware. For technical reference only.
