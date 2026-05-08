---
title: "Token 自由在加速：Redis 之父让你的 Mac 跑起 DeepSeek V4 Flash"
titleEn: "Token Freedom Accelerating: Redis Creator Runs DeepSeek V4 Flash Natively on Mac"
description: "Redis 创始人 antirez 开源 ds4——一个专为 DeepSeek V4 Flash 打造的 Mac 原生 Metal 推理引擎。40,000 行 C 代码 + 17 个 Metal Shader，2-bit 非对称量化，磁盘 KV Cache 持久化，M3 Max 上生成速度 26 t/s，make 一下就能跑。"
descriptionEn: "Redis creator antirez open-sources ds4 — a Mac-native Metal inference engine purpose-built for DeepSeek V4 Flash. 40,000 lines of C + 17 Metal shaders, 2-bit asymmetric quantization, disk-persistent KV cache, 26 t/s generation on M3 Max. One make command to run."
pubDate: "2026-05-08"
updatedDate: "2026-05-08"
category: "Tech-News"
tags: ["DeepSeek", "Mac本地推理", "Metal", "antirez", "开源", "LLM", "Apple Silicon", "MoE"]
heroImage: "../../assets/banner-future-is-now.jpg"
---

**结论先行（BLUF）**：Redis 创始人 antirez 写了一个 DeepSeek V4 Flash 的 Mac 专用推理引擎 ds4，40,000 行 C 代码，17 个 Metal Shader，只为一个模型——284B 参数的 MoE 巨兽。128GB 内存跑 2-bit 量化版，`make` 一下就能启动，OpenAI / Anthropic 双 API 兼容。这不是玩具。

- GitHub：[github.com/antirez/ds4](https://github.com/antirez/ds4)
- 发布推文：[x.com/antirez/status/2052405820235678175](https://x.com/antirez/status/2052405820235678175)

---

## 为什么值得关注

当大多数人在用 Ollama 包装通用运行时的时候，antirez 写了一个**只跑这一个模型**的引擎。

理由很简单：DeepSeek V4 Flash 是 284B 参数的 MoE 架构，激活参数 13B，上下文窗口 1M token。要在 Mac 上把它跑好，通用方案的每一处妥协都是代价。ds4 的回答是：把通用性全部砍掉，把对这一个模型的理解吃透，然后榨干 Apple Silicon 的每一分性能。

这就是写出 Redis 的那个人的做事方式。

---

## 三个核心工程决策

### 1. 非对称 2-bit 量化——聪明地偷懒

不是所有参数都平等对待。ds4 只压缩**路由专家（Routed MoE Experts）**，用 IQ2_XXS / Q2_K 极限量化；**共享专家（Shared Experts）**保持原始精度。

结果：整体模型压到 128GB 可装，但影响输出质量最大的那部分没有被委屈。这是对模型内部结构的理解，不是工具上默认的"全模型 2-bit"。

### 2. 磁盘 KV Cache——一等磁盘居民

> "KV Cache 不该是内存的二等公民，它应该是一等磁盘居民。"——antirez

传统本地推理的痛点：服务重启 = 长上下文全部重新预填充。ds4 把 KV Cache 序列化到 SSD，包含 token ID、渲染文本和完整会话状态。重启服务，从断点恢复，无需重跑。

1M token 上下文窗口在本地推理场景真正变得可用，靠的就是这个设计。

### 3. Metal 原生图执行器

17 个 Metal Shader 文件，为 Apple Silicon 的 GPU 架构量身编写。没有 PyTorch，没有 GGML 的通用层，直接操控硬件。CPU 推理路径仅用于正确性验证，ds4 的战场是 Metal。

---

## 实测性能

| 硬件 | 场景 | 预填充速度 | 生成速度 |
|------|------|-----------|---------|
| M3 Max 128GB | 短提示 | 58.5 t/s | 26.7 t/s |
| M3 Max 128GB | 11,709 token 长提示 | 250 t/s | 21.5 t/s |
| M3 Ultra 512GB | — | 比 M3 Max 快 44–78% | — |

M3 Ultra 上接近 468 t/s 预填充（用户提供数据）。对于 284B 参数的模型，这是实用级别的速度，不是跑来截图的玩具数字。

---

## 上手三步

```bash
# 1. 下载模型（2-bit，约 128GB）
./download_model.sh q2

# 2. 编译
make

# 3a. 命令行交互
./ds4

# 3b. 启动带磁盘 KV Cache 的 HTTP 服务
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv
```

HTTP 服务兼容 OpenAI 和 Anthropic API 格式，Claude Code 可以直接在 MCP 配置里接入，不需要任何云端 API Key。

---

## 常见问题

**Q：128GB 够跑吗？**  
A：够，专门为 128GB 设计了 2-bit 非对称量化版本（`q2`）。256GB+ 可以跑 4-bit 版本，质量更高。

**Q：和 Ollama / llama.cpp 有什么区别？**  
A：ds4 不是通用运行时，只跑 DeepSeek V4 Flash。好处是针对这个模型的每一处优化都可以做到极致，不需要考虑对其他模型的兼容性。

**Q：磁盘 KV Cache 会影响生成速度吗？**  
A：不影响生成阶段速度，影响的是从断点恢复的时间（远比重新预填充快）。生成阶段仍然全部在内存中完成。

**Q：能在 Intel Mac 上跑吗？**  
A：不能，Metal 路径专为 Apple Silicon 设计。CPU 推理路径存在，但 antirez 明确标注有 macOS 虚拟内存 bug，不建议用于实际推理。

**Q：Claude Code 怎么接入？**  
A：启动 `./ds4-server`，在 Claude Code 的 MCP 配置里添加 `baseURL: http://localhost:PORT`，模型名填对应格式即可。完全本地，零云端依赖。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: Redis creator antirez just open-sourced ds4 — a Mac-native Metal inference engine written from scratch for one model: DeepSeek V4 Flash. 40,000 lines of C, 17 Metal shaders, asymmetric 2-bit quantization, disk-persistent KV cache. Runs on 128GB RAM. One `make` command. OpenAI and Anthropic API compatible.

- GitHub: [github.com/antirez/ds4](https://github.com/antirez/ds4)
- Announcement: [x.com/antirez/status/2052405820235678175](https://x.com/antirez/status/2052405820235678175)

---

## Why This Matters

While most local inference tools wrap general-purpose runtimes, antirez built an engine for **one model only**.

DeepSeek V4 Flash is a 284B-parameter MoE model with 13B active parameters and a 1M-token context window. Running it well on a Mac means every compromise in a general-purpose runtime has a real cost. ds4's answer: eliminate all generality, deeply understand this one model, then extract every bit of performance from Apple Silicon.

This is how the author of Redis approaches engineering.

---

## Three Core Engineering Decisions

### 1. Asymmetric 2-bit Quantization — Smart Laziness

Not all parameters are treated equally. ds4 aggressively quantizes **routed MoE experts** (IQ2_XXS / Q2_K) while keeping **shared experts** at full precision.

Result: the full model fits in 128GB, but the components that most affect output quality aren't compromised. This requires understanding the model's internal structure — not just running "global 2-bit" from a tool's defaults.

### 2. Disk KV Cache — First-Class Disk Citizen

> "KV cache shouldn't be a second-class memory citizen — it should be a first-class disk citizen." — antirez

The classic local inference pain point: server restart = re-prefill everything. ds4 serializes KV cache to SSD, including token IDs, rendered text, and full session state. Restart the server, resume from the checkpoint, no reprocessing needed.

A 1M-token context window becomes practically usable locally because of this design.

### 3. Metal-Native Graph Executor

17 Metal shader files, written specifically for Apple Silicon GPU architecture. No PyTorch, no GGML abstraction layer — direct hardware control. The CPU inference path exists for correctness validation only; Metal is the real target.

---

## Performance Numbers

| Hardware | Scenario | Prefill Speed | Generation Speed |
|----------|----------|---------------|-----------------|
| M3 Max 128GB | Short prompt | 58.5 t/s | 26.7 t/s |
| M3 Max 128GB | 11,709-token prompt | 250 t/s | 21.5 t/s |
| M3 Ultra 512GB | — | 44–78% faster than M3 Max | — |

For a 284B-parameter model, these are production-usable numbers — not just screenshot benchmarks.

---

## Getting Started

```bash
# Download 2-bit model (~128GB)
./download_model.sh q2

# Build
make

# CLI mode
./ds4

# HTTP server with disk KV cache
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv
```

The HTTP server is compatible with both OpenAI and Anthropic API formats. Claude Code can connect directly via MCP config — no cloud API key required.

---

## FAQ

**Q: Is 128GB really enough?**  
A: Yes — the `q2` build uses asymmetric 2-bit quantization designed specifically for 128GB systems. 256GB+ can run the 4-bit variant for higher quality.

**Q: How is this different from Ollama or llama.cpp?**  
A: ds4 is not a general-purpose runtime — it only runs DeepSeek V4 Flash. That constraint allows every optimization to be pushed to the limit without worrying about other model compatibility.

**Q: Does disk KV cache slow down generation?**  
A: No impact on generation speed. It only affects recovery time from checkpoints (which is far faster than re-prefilling). Generation still runs fully in memory.

**Q: Does it work on Intel Macs?**  
A: No — the Metal path is Apple Silicon only. A CPU inference path exists, but antirez explicitly notes macOS virtual memory bugs that make it unsuitable for real inference.

**Q: How do I connect Claude Code to ds4?**  
A: Start `./ds4-server`, then add `baseURL: http://localhost:PORT` in Claude Code's MCP config with the appropriate model name. Fully local, zero cloud dependency.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
