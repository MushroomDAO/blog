---
title: "Splash 1.4.0 更新：Mac 推理加速与六引擎对照"
titleEn: "Splash 1.4.0: Mac Inference and Six Specialized Engines"
description: "Splash 1.4.0 为 Apple Silicon 增加 Qwen3.8-Flash-Next、专家与 PLE 的 SSD 流式加载及长上下文支持。本文复核官方同机 Q2_0 对照，区分解码、预填充、缓存首字延迟和并发总吞吐，核对120tok/s的来源，并说明量化精度、内存预算、磁盘读写及可重复性的代价。"
descriptionEn: "Splash 1.4.0 adds Flash-Next and SSD streaming on Macs. We review official benchmark conditions, cache effects, memory tradeoffs and reproducibility limits."
pubDate: "2026-10-05"
heroImage: "../../assets/images/specialized-inference-engines-rise-llm-hardware-optimization-banner.jpg"
category: "Research"
tags: ["推理引擎", "LLM", "WASM", "性能优化", "Apple Silicon", "NVIDIA", "AMD", "开源工具"]
lang: "zh-CN"
wechatTitle: "Splash更新：Mac加速要看哪些条件"
wechatDigest: "复核官方95tok/s与缓存测试，拆解SSD流式加载、量化和长上下文的取舍。"

updatedDate: "2026-10-22"
lastPublishedAt: "2026-10-22T15:27:08Z"
---

Splash 1.4.0 是面向 M3 及更新 Mac 的本地大模型推理引擎，此次重点是让 Flash-Next 这类大模型在统一内存与 SSD 之间协同运行。我们复核的官方 M5 Pro 64GB 数据是 95 tok/s 解码、32K 提示词 1,312 tok/s 预填充、缓存命中首 token 171ms，没有找到“120 tok/s”在同一模型和设置下的对应证据，也没有把这些官方数字写成我们的实测。

这篇文章沿用 2026 年 10 月 5 日的原始链接，新增本节双语版本核查；后面的六引擎概览保留为当时的历史背景。其他五个项目的版本、星数、性能与“唯一”等时效性判断，本轮没有重新横向验证，不能当成 10 月 22 日的完整榜单。

## Splash 1.4.0 的速度数字，到底测了什么？

源码版本固定为标签 `1.4.0`、提交 `1482f6bbc2abf12375332725302019594150b6cb`。GitHub 发布记录时间为 2026 年 10 月 20 日（UTC）；不是本文撰写日刚发布。

发布说明：https://github.com/incoai/splash/releases/tag/1.4.0

固定 README：https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/README.md

这组 Flash-Next 测试采用 M5 Pro、20 核 GPU、64GB 内存；模型是 `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:Q2_0`。对手是同一台 Mac、同一 GGUF 的 Strata。测试通过 HTTP 使用选取的 SPEED-Bench 编码提示词，输出上限 1,024 token。

| 指标 | 官方 Splash 结果 | 应如何理解 |
| --- | --- | --- |
| 短提示解码 | 95 tok/s；约 1.3× | 这组请求的生成速率，不是所有模型的峰值 |
| 32K 提示词预填充 | 1,312 tok/s；约 1.3× | 官方按到首 token 的时间计算，不能混作纯算子吞吐 |
| 32K 重放缓存首字时间 | 171ms；约 212× | 16 个重放提示全部缓存命中，不代表冷请求也快 212 倍 |
| 四路短请求并发 | 合计 171 tok/s；约 2.4× | 四条请求合计，不是每条都达到 171 tok/s |

“约 1.3×”对应四舍五入后的比值，不能升级成“任何任务整体快 30% 以上”。缓存 TTFT 的倍数也不能搬去描述解码速度。源码 README 中的 27B/35B 初版成绩来自另一台 16 核 GPU、48GB 的 M5 Pro，不能横着拼成一张相同硬件排名表。

还应区分量化与任务质量。这组 Flash-Next 用的是 Q2_0，并非 BF16 模型；本文没有独立测其代码正确率、工具调用成功率或相对原模型的精度。旧文的 next-token 一致性来自 27B/35B 的另一套 llama.cpp 对照，不是 Flash-Next 的任务准确率。

历史测量细节：https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/docs/performance.md

![小M把冷预填充、缓存首字和四路并发放进不同量杯](../../assets/images/splash-1-4-update-fig-01.png)

## 为什么要把专家、PLE 和 KV 分别搬到 SSD？

1.4.0 不只是一个更快的 Metal 内核，而是在同一内存预算里安排三类不同资源。MoE 专家装得下就常驻，装不下就流式读取；Flash-Next 的 PLE n-gram 表可用行缓存分批取用；正在生成的 Flash-Next 请求还能把部分 KV 放到 SSD，内存保留稀疏索引与热点块。27B 和 35B 的活动 KV 在这个版本仍保留在内存。

这三种流式机制不能与“跨轮对话前缀缓存”混为一谈：前者缓解模型和运行状态容量，后者主要避免重复计算。KV spill 需要可写磁盘缓存与剩余配额，关闭磁盘缓存会影响这条扩容路径。SSD 提供容量，不会自动提供内存带宽；冷专家、缓存抖动和长上下文都可能增加磁盘读写与尾延迟。

`--max-memory` 限制的是 Metal 分配预算，不是整个进程 RSS。多应用并行时需要给系统和浏览器留空间，不能把 64GB 机器理解成 64GB 都能无代价交给模型。我们没有替读者验证某个指定内存上限必定能装下 Flash-Next。

工程说明：https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/DEVELOPMENT.md

![小M在内存与SSD之间分别调度专家、PLE表和KV状态](../../assets/images/splash-1-4-update-fig-02.png)

## 1M 上下文、推测解码和可重复性有什么代价？

原生窗口为 262,144 token；超出后可用静态 YaRN 扩展。`--max-context 1M` 的 `1M` 表示 1,000,000，而非 1,048,576，版本上限为 1,010,000。参数能填进去不代表能在任意 Mac 上跑通：实际仍受 RAM、SSD 与预算约束。启用 YaRN 连短提示的输出都可能改变，不应为了“以后可能用到”一直开到最大。

DFlash 2 先提出候选，再由目标模型验证。此次默认的自适应验证减少不值得验证的候选行，也带来一个容易忽略的版本说明：`--verify-rows auto` 下，MoE 的贪心和有固定 seed 的输出仍可能随时序、服务器历史变化。要做受控对照，可按上游建议用 `--verify-rows all`、隔离请求并保持相同缓存前缀；这也不等于获得跨硬件逐位一致的承诺。

JSON Schema 请求与普通请求可以共享解码批次，官方另有混合负载收益，但单请求速率在噪声范围内不变。不能把混合并发的提升写成单个聊天也同比加速。本次我们未复跑这些吞吐实验。

## 普通 Mac 用户如何开始，又应该怎么验收？

要求 M3 或更新芯片、macOS 26.4+、Homebrew。不是全部 Apple Silicon 机器都支持。官方四位示例要求至少 36GB、推荐 48GB；24GB 机器可选择较小 GGUF，但不代表 Flash-Next 这组 64GB 成绩能照搬过去。Flash-Next 当前支持 GGUF，暂不支持其 MLX checkpoint；支持其他家族的 MLX，不等于这一项也支持。

```bash
brew install incoai/tap/splash
# Homebrew 会安装执行时可用版本；先核对版本，不保证永久锁在1.4.0。
splash --version
splash serve --model ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:Q2_0
```

首次运行会下载目标模型及匹配的 draft，并占用磁盘与内存；这不是本文在读者电脑上执行过的操作。等待 `Ready` 后，本机聊天页为 `http://127.0.0.1:8000`，Chat Completions 路径为 `/v1/chat/completions`。默认监听 localhost、没有认证，局域网部署应另按 server configuration 设置访问控制。

它还提供 Responses、Completions、Anthropic Messages 与工具调用等接口，但接入现有 Agent 后仍应检查工具参数、思考设置和取消行为，不能只以接口名称相同认定完全兼容。`splash claude` 等启动器需要对应客户端已经安装。

建议分三轮验收：先做冷启动和未缓存请求，记录首 token、内存与磁盘；再重放固定前缀，记录实际命中情况；最后才测试多路编码请求，记录合计吞吐和每条请求的 p95 等待时间。全程固定模型文件哈希、量化、引擎版本、输出长度和验证模式，任务正确性单独评分。只看 tok/s，可能把更多等待或不同输出误认成性能收益。

![小M用同一模型、缓存状态和输出条件校准速度比较](../../assets/images/splash-1-4-update-fig-03.png)

## Splash 更新常见问题

### 120 tok/s 是假数据吗？

目前只找到官方同配置 95 tok/s 的发布结果，尚不能断言其他条件下不可能达到 120。没有模型、量化、提示长度、设备和验证模式的完整条件，就不把 120 写成已核实事实。

### 本文是否做了本地性能测试？

没有下载模型或运行推理。我们下载固定标签、检查源码和测量说明，另尝试本地服务层测试；本机测试环境的依赖与版本障碍会如实记录，不能拿它代替引擎性能复现。

### 支持 MLX 格式就能加载任意 MLX 模型吗？

不能。格式支持与模型架构支持是两层条件；1.4.0 中 Flash-Next 暂不支持 MLX checkpoint，其他家族可加载的格式不能直接套用到它。

本次部署研究与本地验证的实际范围见文末更新记录。相关硬件专用化延伸：https://blog.mushroom.cv/blog/strix-halo-halogen-gufo-prefill/ 。

---

## 2026-10-05 历史概览：六个专用引擎



有六个推理引擎正在快速出现，它们的共同特征是：只跑一种或少数几种模型，只为一种或少数几种硬件写内核。它们主动放弃通用性，换取在目标硬件上远超 llama.cpp / vLLM 的性能。

这篇文章对六个框架逐一核实数字，分析「专用引擎崛起」这个趋势是否真实成立，以及普通开发者和最终用户能从中得到什么。

---

## 六个框架逐一拆解

### 1. Splash — Apple Silicon 专用，比 llama.cpp 快 4.5–5.3×

仓库：incoai/splash | ⭐ 1.2K | Apache-2.0 | C++（Metal 内核）

目标硬件：Apple Silicon M3 及以上，macOS 26.4+，四位示例最低 36GB；小 GGUF 可用于 24GB（详见上方更新）

vs llama.cpp 官方对照数字（本文未独立复现）（这是旧文收录的直接对照之一）：

| 模型 | Splash | llama.cpp | llama.cpp+MTP |
|------|--------|-----------|----------------|
| Qwen 27B（M5 Pro）| 74 tok/s | 16 tok/s | 27 tok/s |
| Qwen 27B（M3 Max）| 92 tok/s | 17 tok/s | 20 tok/s |
| Qwen 35B-A3B（M3 Max）| 209 tok/s | 66 tok/s | — |

27B 模型提速 4.5–5.3×，35B MoE 提速 2.5–3.2×。次 token 与 llama.cpp 的一致性 97.83–99.45%（这是排名第一的下一 token 对照，不是任务准确率或逐位等价）。

关键技术：DFlash 2 投机解码 + 手写 Metal 内核 + 前缀缓存重用 + 自动并发批处理。内置 OpenAI/Anthropic 兼容 API，支持视觉和内嵌 PDF。

---

### 2. NInfer — RTX 5090 专用，从零写的 C++/CUDA

仓库：Neroued/ninfer | Apache-2.0 | C++20 + CUDA

目标硬件：NVIDIA RTX 5090（sm_120a）为主，社区 port 覆盖 RTX 4090/3090、AMD MI50

性能数字（绝对值，无与 llama.cpp 的直接对比）：

| 硬件 | 场景 | 速度 |
|------|------|------|
| RTX 5090 | Prefill（单请求） | 17,705 tok/s |
| RTX 5090 | 并发 decode（8 请求） | 1,146.9 tok/s |
| RTX 4090（社区 port）| Decode + 投机解码 | 148.6 tok/s（81% 接受率） |
| RTX 4090 | 64K 上下文 prefill | 1,849 tok/s |
| RTX 4090 | 128K 上下文 decode | 39.6 tok/s |

关键技术：完全从零编写（"from scratch"，非 llama.cpp 分叉），NVFP4 量化，MTP 投机解码，多种 KV 量化格式（BF16/INT8/FP8/NVFP4/K8V4），同时兼容 OpenAI 和 Anthropic API。配套桌面 UI（Tauri 2，ninfer-studio）。

---

### 3. DwarfStar (ds4) — Redis 作者的纯 C 引擎，DeepSeek V4 专用

仓库：antirez/ds4 | MIT | C（单文件风格）

作者：antirez（Salvatore Sanfilippo，Redis 创始人）

目标模型：DeepSeek V4 系列（Flash、V4.1 Flash、PRO）、GLM 5.2/5.3、Qwen3.8 Flash Next

硬件：三平台官方支持 — Apple Silicon（96GB+）、NVIDIA CUDA（DGX Spark、Ada Lovelace 系列）、AMD ROCm（Strix Halo / Framework Desktop）

性能数字：8×L40S，16 并发会话，聚合生成 ~126 tok/s（注：这是服务端多用户场景，不是单请求速度）

关键技术：纯 C 单文件代码哲学，imatrix 量化，routed-expert 量化（针对 MoE 路由专家单独量化），多 GPU 张量并行 + 流水线并行，Directional Steering（方向性引导生成），内置 Tool Format + 编码 Agent。

最值得注意的一点：DwarfStar 明确声明大量使用 AI 辅助编码 —— "This software is developed with strong assistance from AI coding agents, with humans leading the ideas, testing, and debugging." 这是六个框架里唯一公开承认这一点的，antirez 的背书让这个声明很有份量。

---

### 4. Strata — 消费级 PC 跑 125B MoE

仓库：Niko1221/Strata | MIT | Rust

目标：让普通消费级 PC 也能跑 Qwen3.8-Flash-Next 125B MoE，一键安装体验

硬件：NVIDIA RTX 20/30/40/50 系列 + AMD RX 7000/9000 系列，最低 12GB VRAM，32GB RAM

性能数字：

| 硬件 | 生成速度 | Prefill 速度 |
|------|---------|------------|
| RTX 5070 | 94 tok/s | 2,650 tok/s |
| AMD RX 9070 XT | 60 tok/s | — |
| AMD RX 7600 XT 16GB（ROCm） | 42.5 tok/s | 293 tok/s（4K prompt）|

投机解码（MTP）带来 1.6–1.8× 额外加速。

关键技术：动态权重分层放置（VRAM→RAM→SSD，引擎自动测算最优组合；实测「全放 GPU 反而最慢」），利用 MoE 稀疏性（24,576 个专家每次只激活约 10 个），上下文超出时 AI 摘要压缩历史对话，兼容 OpenAI API，内置 MCP 服务器接口。

---

### 5. llamAmpere — RTX 3090 专属，1.46× 加速 + 262K 上下文

仓库：JakeATX/llamAmpere | MIT（继承 llama.cpp）| C++/CUDA | ⭐ 142

目标硬件：NVIDIA Ampere RTX 3090/3090 Ti，24GB VRAM，Linux，CUDA 12.4

vs llama.cpp 官方对照数字（本文未独立复现）：

- 标准测试：104.28 tok/s，vs llama.cpp 1.46×
- 100K 上下文深度：103.09 tok/s（仅 +0.3% 退化，说明长上下文几乎不影响速度）
- 262,144 token 上下文可在 23GB VRAM 内完成（理论最大 262K）

关键技术：MTP 投机解码（默认 4 token/step），宽度 5–8 验证内核（自定义 CUDA），TurboQuant KV 缓存压缩（turbo2~turbo6 格式），词汇表短表化（65,536 token draft 词表减少计算），自适应深度（根据接受率在 depth 3-4 间自动切换）。支持 Qwen3.8-27B、Agnes 3.0 Flash、Ternary Bonsai 2 27B 及多种量化变体。

---

### 6. gufo — AMD Strix Halo 专用，统一内存架构的最大化利用

仓库：gufo-org/gufo | MIT | C++20 + HIP | ⭐ 538

目标硬件：AMD Strix Halo（Ryzen AI MAX+ 395 + Radeon 8060S），最高 128GB 统一内存

性能数字（无与 llama.cpp 直接对比）：

| 模型 | Prefill | 单用户 decode | 8 用户聚合 |
|------|---------|---------------|----------|
| Qwen3.8 Flash-Next Q4_K_XL | 1,628 tok/s | 59.41 tok/s | 157.22 tok/s |
| Qwen3.8 27B Q4_K_XL | 656 tok/s | 70.56 tok/s | — |
| DeepSeek V4 Flash | 484 tok/s | 26.62 tok/s | — |

关键技术：AMD HIP 内核专门为 Strix Halo 统一内存架构优化（CPU 和 GPU 共享同一物理内存池，消除 PCIe 带宽瓶颈），三种投机解码模式（DFlash2/MTP/DSpark），多模态支持（Qwen3-ASR/TTS 语音、Qwen-Image-2.1 图像生成、MiniMax H3 文生视频），Podman 容器化部署。

---

## 横向对比

| | Splash | NInfer | DwarfStar | Strata | llamAmpere | gufo |
|---|---|---|---|---|---|---|
| Stars | 1.2K | — | — | — | 142 | 538 |
| 许可 | Apache | Apache | MIT | MIT | MIT | MIT |
| 硬件 | Apple M3+ | RTX 5090 | 三平台 | NVIDIA+AMD | RTX 3090 | AMD Strix Halo |
| vs llama.cpp | +4.5–5.3× | 无直接对比 | 无 | 无 | +1.46× | 无 |
| AI 辅助编码 | 未说明 | 未说明 | 明确承认 | 未说明 | 未说明 | 未说明 |
| 多模态 | 视觉+PDF | 文字/图/视频 | 无 | 无 | 无 | 语音/图/视频 |
| 最小硬件门槛 | 36GB RAM | 24GB VRAM | 96GB RAM（Mac）| 12GB VRAM | 24GB VRAM | 96GB RAM |

---

## 趋势分析：这个趋势真实成立吗？

结论：成立，但要细化三个子命题。

命题 1：专用引擎性能确实远超通用引擎 — 部分成立

Splash 对 llama.cpp 的 4.5–5.3× 提速有直接数字支撑，llamAmpere 的 1.46× 也有。其余四个引擎目前只有各自硬件的绝对值，没有和 llama.cpp/vLLM 的直接横向对比，宣称的「远超」仍需等待独立基准测试确认。

命题 2：它们「主动放弃通用性」 — 完全成立

这六个引擎的目标硬件范围：一个 SKU（Strix Halo）→ 一代 GPU（Ampere RTX 3090）→ 一家厂商（Apple Silicon）。不是无法做通用，而是不做，因为通用意味着牺牲能利用的硬件特性。NInfer 明确标注主要支持 RTX 5090（sm_120a），社区 port 才覆盖其他显卡。

命题 3：AI 代码生成让「一次性专用引擎」变得极其便宜 — 有证据，尚未大规模验证

DwarfStar（antirez/ds4）是截至目前唯一公开承认大量使用 AI 辅助编码的项目，且由高信誉开发者（Redis 作者）背书。这个案例有力支持了「AI 帮助大幅降低专用引擎开发成本」的假说，但其他五个项目没有类似声明，目前还是孤证。

---

## 普通开发者如何受益

第一步：按你的硬件选引擎，不用等待通用方案

| 你的机器 | 推荐引擎 | 效果 |
|---------|---------|------|
| MacBook Pro M3/M4（36GB+）| Splash | Qwen 27B 跑到 74–92 tok/s，约等于 llama.cpp 的 5× |
| Mac Studio M4 Ultra（192GB）| DwarfStar（Metal） | DeepSeek V4 系列官方支持 |
| NVIDIA RTX 3090（24GB）| llamAmpere | 262K 上下文 + 1.46× 提速，不用升级硬件 |
| NVIDIA RTX 4090 / RTX 5090 | NInfer | 需编译，性能最高，适合愿意折腾的开发者 |
| AMD Ryzen AI MAX+ 395（96–128GB）| gufo | 统一内存架构专用优化，唯一为此硬件写的引擎 |
| 消费级 NVIDIA / AMD 显卡（12GB+）| Strata | 跑 Qwen 125B MoE，开箱即用 |

第二步：用标准 API 接口，不锁定引擎

六个引擎全部提供 OpenAI 兼容 API（`/v1/chat/completions`），部分还有 Anthropic API 兼容。这意味着你写的上层代码可以无缝切换引擎——今天用 Splash，明天换 DwarfStar，应用层不用改。

第三步：注意「只适合少数模型」的限制

这些引擎都只深度优化了一两个模型系列。如果你需要跑 Llama 系列，目前六个引擎都没有优化支持。通用需求仍然选 llama.cpp 或 Ollama，专用需求选对应引擎。

---

## 最终用户在不同硬件上的受益

MacBook Pro / Mac Studio 用户（36GB+ 统一内存）

Splash 让 Qwen 27B 从 17 tok/s 跳到 92 tok/s——这个差距是「勉强能用的阅读速度」和「流畅对话」的区别。DwarfStar 提供 DeepSeek V4 的 Apple Silicon 官方路径，加上内置编码 Agent。

普通 PC 用户（NVIDIA 或 AMD 独显，12GB+ VRAM）

Strata 是目前最「面向最终用户」的引擎，一键安装，能让普通 RTX 显卡跑起之前只能在服务器上跑的 125B MoE。60–94 tok/s 的生成速度，加上 MCP 接口，可以直接接 Claude Code 这类工具。

高端 PC 用户（RTX 3090/4090/5090）

llamAmpere 把 3090 的 24GB VRAM 推向 262K 上下文，是当前消费级里最长的上下文窗口之一。NInfer 在 4090/5090 上跑出接近数据中心规格的 prefill 速度。

AMD Strix Halo 用户（Ryzen AI MAX+ 系列）

gufo 目前是这个硬件上唯一专门优化过的引擎，统一内存架构让 128GB 完整可用，同时支持语音/图像/视频生成，适合构建本地多模态 AI 工作站。

---

## 这个趋势的下一步

DwarfStar 明确说明 AI 辅助了大量代码。如果这条路成立——用 AI 生成针对你的 GPU 微架构的手写内核——那「专用引擎」的门槛会继续下降。

目前的模式是：人类确定优化方向，AI 生成内核代码，人类做测试和调试。这让一两个开发者写出过去需要芯片厂商专属工程团队才能完成的优化成为可能。antirez 用 C 写 Redis 从来不是孤立现象——他证明的是「深刻理解 + 专注单一目标」可以击败大团队的通用解法。现在加上 AI 辅助，这条路径变得更宽。

---

> 以上数字均来自各项目官方仓库，性能对比应在相同硬件和测试条件下才有可比性。DwarfStar/Strata/NInfer/gufo 目前 Stars 数量较少，仍为早期项目。开源仅供学习参考。

---


## 2026-10-22 核验范围

本次只复核 Splash 1.4.0 的源码、发布说明与测量条件，没有下载模型、跑推理或测得自己的 tok/s。尝试运行上游 `dev.tests.server.test_memory_release`：系统 Python 3.9 因不支持 match 语法而在导入阶段失败；现有 Python 3.12 环境又因缺少 llguidance 未能加载测试。没有任何该测试的断言实际通过，这不构成引擎不兼容或性能下降的证据。旧文章的其他五个项目未重新实测。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Splash 1.4.0 is a local inference engine for M3 and newer Macs. Its new Flash-Next path coordinates unified memory and SSD resources. The official M5 Pro 64GB result we could verify is 95 tok/s decode, 1,312 tok/s prefill for a 32K prompt, and 171ms cached TTFT. We did not find matching conditions for the supplied 120 tok/s claim, and did not reproduce these performance measurements ourselves.

This updates the October 5 article at its existing URL. The other five engine profiles below remain historical context: their releases, stars, measurements and claims of uniqueness were not rechecked as a current October 22 leaderboard.

## What does the Splash 1.4.0 benchmark measure?

We pinned tag `1.4.0` at `1482f6bbc2abf12375332725302019594150b6cb`. GitHub dates the release October 20, 2026 (UTC).

Release: https://github.com/incoai/splash/releases/tag/1.4.0

Pinned README: https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/README.md

Flash-Next was tested on an M5 Pro with a 20-core GPU and 64GB memory using `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:Q2_0`. Strata served the same GGUF on the same Mac. Selected SPEED-Bench coding prompts were sent over HTTP, with a 1,024-token output limit.

| Metric | Official result | Qualification |
| --- | --- | --- |
| Short-prompt decode | 95 tok/s; about 1.3× | Generation rate for this workload |
| 32K prefill | 1,312 tok/s; about 1.3× | Computed using time to first token, not isolated kernel throughput |
| Cached 32K replay TTFT | 171ms; about 212× | All 16 replayed prompts hit cache; not cold-request speed |
| Four concurrent short requests | 171 tok/s aggregate; about 2.4× | Sum across requests, not per-request throughput |

The rounded 1.3× ratio does not establish an across-the-board improvement exceeding 30%. Cache TTFT ratios do not describe decode throughput. Older 27B/35B launch figures use a different M5 Pro configuration, with a 16-core GPU and 48GB memory.

Q2_0 also matters: these are not BF16 weights. We did not evaluate Flash-Next coding accuracy or tool-use success. Historical next-token agreement with llama.cpp concerns separate 27B/35B tests and is not Flash-Next task accuracy.

Historical methodology: https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/docs/performance.md

![XiaoM separates cold prefill, cached first token and aggregate concurrency](../../assets/images/splash-1-4-update-fig-01.png)

## What is moving between memory and SSD?

The planner shares a budget between model resources, context and streaming stores. MoE experts stay resident where possible and stream otherwise. Flash-Next’s PLE n-gram table can use a row cache. Its active KV can spill to SSD while sparse indexes and hot blocks remain in RAM. The 27B and 35B retain active KV in memory in this release.

These capacity mechanisms differ from reusing a conversation prefix to avoid recomputation. Active KV spill requires a writable cache with remaining quota. SSD capacity is not memory bandwidth: cold expert reads, cache churn and long contexts can increase I/O and tail latency. The `--max-memory` setting caps Metal allocations, not total process RSS, and does not independently establish that a model fits a particular Mac.

Engineering reference: https://github.com/incoai/splash/blob/1482f6bbc2abf12375332725302019594150b6cb/DEVELOPMENT.md

![XiaoM manages separate expert, PLE and KV stores between memory and SSD](../../assets/images/splash-1-4-update-fig-02.png)

## What do long context and adaptive verification cost?

Static YaRN extends beyond the native 262,144-token window. `--max-context 1M` means 1,000,000 tokens, with a release limit of 1,010,000. Available RAM, SSD and planning constraints still apply. Enabling YaRN can change outputs even for short prompts, so the largest setting is not automatically the best default.

DFlash 2 proposes candidates for target-model verification. Adaptive verification reduces work on unlikely proposals, but `--verify-rows auto` can change MoE greedy and seeded outputs as timing and server history change. Upstream recommends `--verify-rows all`, isolated requests and identical cached prefixes for repeatable comparisons. This is not a promise of bitwise agreement across hardware.

Structured JSON Schema requests can share batches with ordinary requests. The release reports mixed-load gains while single-request throughput remains unchanged within noise. A batching improvement must not be sold as the same improvement for one chat. We did not rerun those benchmarks.

## How should a Mac user get started?

Requirements are M3 or newer, macOS 26.4+ and Homebrew, not every Apple Silicon Mac. Official four-bit examples need at least 36GB, with 48GB recommended. Smaller GGUF options exist for 24GB machines; this does not transfer the Flash-Next 64GB result to them. Flash-Next MLX checkpoints are not yet supported, although other supported families accept MLX formats.

```bash
brew install incoai/tap/splash
# Homebrew installs the version available when run, not a permanent1.4.0pin.
splash --version
splash serve --model ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:Q2_0
```

The first run downloads both target and matching draft. We did not execute this model download or inference. After `Ready`, the local chat page is `http://127.0.0.1:8000`, with Chat Completions at `/v1/chat/completions`. Default loopback serving has no authentication; LAN exposure needs separate access-control configuration.

Responses, Completions, Anthropic Messages and tool calling are also provided. Existing agents still need integration checks for argument shapes, thinking settings and cancellation. Agent launcher commands require those clients to be installed.

A useful acceptance sequence is cold loading and uncached requests, fixed-prefix replay with observed hit rates, then concurrent coding requests. Fix model hashes, quantization, engine version, output length and verification mode. Measure first token, per-request p95 waiting time, memory, disk and aggregate throughput separately, and score task correctness independently.

![XiaoM fixes model, cache state and output conditions before comparing speed](../../assets/images/splash-1-4-update-fig-03.png)

## Frequently asked questions about this update

### Is 120 tok/s necessarily false?

No. We verified 95 tok/s under the published configuration, but cannot rule out 120 under other conditions. We do not present it as established without the model, quantization, prompt, device and verification settings.

### Did we run a local inference benchmark?

No. We inspected pinned source and attempted service-layer tests, reporting actual environment barriers separately. Those checks are not a performance reproduction.

### Does MLX support mean any MLX checkpoint will load?

No. File format support and model architecture support are separate. Flash-Next MLX checkpoints are not supported in1.4.0 even though other supported model families accept MLX formats.

Related hardware-specific engine coverage: https://blog.mushroom.cv/blog/strix-halo-halogen-gufo-prefill/ .

---

## Historical six-engine overview — October 5, 2026



## The Rise of Specialized LLM Inference Engines: Six Frameworks Analyzed

A wave of LLM inference engines optimized for specific models and specific hardware is emerging. Their shared trait: deliberately trading generality for maximum performance on a narrow target.

This October 5 analysis summarizes six projects and their reported measurements, examines whether the trend is real, and maps out benefit paths for developers and end users.

---

### Six Engines at a Glance

Splash (incoai/splash, Apache-2.0, 1.2K stars) — Apple Silicon M3+ only. One framework in this group with a direct published comparison against llama.cpp: Qwen 27B at 74–92 tok/s vs llama.cpp's 16–17 tok/s — 4.5–5.3× faster, with 97.83–99.45% token consistency. DFlash 2 speculative decoding + custom Metal kernels.

NInfer (Neroued/ninfer, Apache-2.0) — RTX 5090 primary target, community ports to 4090/3090. Written from scratch in C++20/CUDA. RTX 5090 reaches 17,705 tok/s prefill, 1,146.9 tok/s concurrent decode (8 requests). RTX 4090 community port: 148.6 tok/s with speculative decoding at 81% acceptance rate.

DwarfStar / ds4 (antirez/ds4, MIT, C) — From Redis author Salvatore Sanfilippo (antirez). Targets DeepSeek V4 series across all three platforms (Apple Metal, NVIDIA CUDA, AMD ROCm). Pure C, single-file philosophy. Explicitly states: *"This software is developed with strong assistance from AI coding agents."* — the only framework in the group to make this public.

Strata (Niko1221/Strata, MIT, Rust) — Consumer PC focus: run Qwen3.8-Flash-Next 125B MoE on a standard gaming PC. RTX 5070: 94 tok/s generation, 2,650 tok/s prefill. AMD RX 9070 XT: 60 tok/s. Dynamic weight layering (VRAM→RAM→SSD), MoE sparsity exploitation. One-click install, OpenAI API + MCP server.

llamAmpere (JakeATX/llamAmpere, MIT, 142 stars) — RTX 3090 / 3090 Ti specific. 1.46× faster than llama.cpp with 262,144 token context fitting in 23GB VRAM. TurboQuant KV compression, custom CUDA MTP speculative decoding, vocabulary shortlisting.

gufo (gufo-org/gufo, MIT, 538 stars) — AMD Strix Halo (Ryzen AI MAX+ 395) only. Exploits the unified 128GB memory architecture: no PCIe bottleneck between CPU and GPU. Qwen3.8 Flash-Next: 1,628 tok/s prefill, 59 tok/s single-user decode. Multimodal: speech, image generation, video generation.

---

### Is the Trend Real?

Yes — with three qualifiers.

1. Performance gains are real, but only two engines publish direct llama.cpp comparisons (Splash: 4.5–5.3×; llamAmpere: 1.46×). The others report absolute numbers on their target hardware; independent benchmarks are needed.

2. The "deliberate generality trade-off" is clearly real — engines target one hardware generation, one vendor, or one SoC SKU by design.

3. AI-assisted coding lowering the barrier: DwarfStar is the only public evidence so far (and it's strong evidence, given antirez's credibility). Whether this scales to a "golden age of one-person specialized engines" requires more data points.

---

### Benefit Map

| Hardware | Best Option | Effect |
|----------|-------------|--------|
| MacBook Pro M3/M4 (36GB+) | Splash | Qwen 27B at 74–92 tok/s vs llama.cpp's 16 tok/s |
| Mac Studio M4 Ultra (192GB) | DwarfStar | Official DeepSeek V4 on Apple Silicon |
| NVIDIA RTX 3090 (24GB) | llamAmpere | 262K context + 1.46× speedup, no hardware upgrade needed |
| NVIDIA RTX 4090 / 5090 | NInfer | Near datacenter-class prefill speed |
| AMD Ryzen AI MAX+ 395 (96–128GB) | gufo | The only engine purpose-built for this SoC |
| Consumer NVIDIA/AMD (12GB+) | Strata | Run 125B MoE out of the box |

All six expose OpenAI-compatible APIs, so application code can switch engines without changes.

---

### What's Next

If DwarfStar's AI-assisted model generalizes — use AI to generate architecture-specific CUDA/Metal/HIP kernels, humans own direction and testing — the barrier to writing a specialized engine drops further. One or two developers could produce hardware-specific optimizations that previously required dedicated chip vendor engineering teams.

The pattern antirez demonstrated with Redis ("deep understanding + single-minded focus beats large teams' general solutions") becomes more accessible when AI handles the inner loop of kernel code generation.

---

> All performance numbers are from official repositories. Cross-framework comparison requires identical hardware and test conditions. DwarfStar, Strata, and NInfer currently have few GitHub stars and remain early-stage. For technical reference only.

## October 22 verification scope

This update reviews Splash 1.4.0 source and official measurement conditions only. No model was downloaded and no inference or tok/s benchmark was run. An attempt to load upstream dev.tests.server.test_memory_release failed at import under system Python3.9 because match syntax is unsupported; the existing Python3.12 environment then lacked llguidance. No assertions from that suite passed. This is an environment limitation, not evidence of an engine compatibility failure or performance regression. The other five historical engines were not retested.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
