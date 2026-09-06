---
title: "IU4 原生 4bit 通道：AMD Strix Halo 上让量化从「省显存」变成「算得快」"
titleEn: "The IU4 Native 4-Bit Lane: On AMD Strix Halo, Making Quantization a Compute Win, Not Just a Memory Win"
description: "jcbtc/Qwen3.8-27B-IU4-Kairic-Edge 是已知第一个在 AMD gfx1151 上跑通加速 IU4 通道的 LLM，Apache-2.0。多数「4bit 模型」只是 4bit 存储、算之前还要展开成更宽格式；它把 4bit 权重和激活直接喂进 RDNA 3.5 的 V_WMMA_I32_16X16X16_IU4 指令。实测 104.66 TOPS（FP16 的 1.94 倍）、47.73 tok/s（比 Unsloth Q4 快 85%）、HumanEval Plus 152/164。但作者自己标明这是「配置系统对比」而非单变量实验，还主动撤下了一个会改变输出的加速路径。"
descriptionEn: "jcbtc/Qwen3.8-27B-IU4-Kairic-Edge is the first known LLM running an accelerated IU4 lane on AMD gfx1151, under Apache-2.0. Most '4-bit' releases store four bits but widen the weights before the matrix op; this one feeds 4-bit weights and activations straight into RDNA 3.5's V_WMMA_I32_16X16X16_IU4 instruction. Measured: 104.66 TOPS (1.94x FP16), 47.73 tok/s (85% over Unsloth Q4), HumanEval Plus 152/164. Notably the author labels these configured-system comparisons rather than single-variable experiments, and withdrew a fast path that could change the model's output."
pubDate: 2026-09-07
updatedDate: 2026-09-07
category: "Tech-News"
tags: ["开源模型", "本地推理", "量化", "AMD", "Strix Halo", "ROCm", "llama.cpp", "硬件", "本地部署"]
heroImage: "../../assets/images/kairic-edge-iu4-strix-halo-native-4bit-lane-qwen38-27b-banner.jpg"
author: "Mycelium Protocol"
---

绝大多数所谓的「4bit 量化模型」，其实只在**存储**上是 4bit。真到做矩阵乘法那一步，权重会被展开回 FP16 或 INT8 再算——省的是显存和带宽，不是算力。

`Qwen3.8-27B-IU4-Kairic-Edge` 做的是另一件事：**让 4bit 数据直接留在计算通路里**，喂给 AMD RDNA 3.5 那条原生的 4bit 整数矩阵指令。

作者称这是已知第一个在 AMD `gfx1151` 上把加速 IU4 通道跑进服务中的 27B 大模型。

> 📌 模型卡：https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge
> 运行时源码：https://github.com/ciru-ai/ROCmFPX（分支 kairic-edge-qwen38-27b-v1.2）
> Apache-2.0 ｜ 基座 Qwen/Qwen3.8-27B ｜ 硬件 AMD Ryzen AI Max+ 395 / Radeon 8060S (gfx1151)

---

## 先说清楚 IU4 到底是什么

AMD 在 RDNA 3.5 的指令集里有一条 `V_WMMA_I32_16X16X16_IU4`：**打包的无符号 4bit 激活 × 有符号 4bit 权重，用 32 位整数累加**，再做显式的 scale / zero-point 重建。

关键区别在这里：

| | 普通「4bit 量化」 | IU4 原生通道 |
|---|---|---|
| 存储 | 4bit | 4bit |
| 送进矩阵指令前 | **展开成 FP16 / INT8** | **保持 4bit 打包** |
| 实际执行的指令 | FP16 或 INT8 矩阵乘 | `V_WMMA_I32_16X16X16_IU4` |
| 收益 | 省显存、省带宽 | **省显存 + 算得快** |

模型卡里那句话说得很准：**这把低精度从「容量优势」变成了「计算优势」。**

### 指令层实测

在一个短依赖链的指令测试台上（HIP event 计时，三次取最好）：

| 依赖链数 | IU4 TOPS | IU8 TOPS | FP16 TOPS |
|---:|---:|---:|---:|
| 2 | 99.87 | 50.65 | 52.35 |
| 4 | 100.09 | 52.94 | 52.47 |
| 8 | **104.66** | **54.30** | **53.87** |

最强点上，IU4 是 IU8 的 **1.93 倍**、FP16 的 **1.94 倍**——同一台设备、同一次运行。

作者特意标注：这是 **GPU 指令速率**，不是 NPU 营销数字、不是持续应用吞吐、也不是能效测量。这种自我设限在模型卡里很少见。

---

## 从指令到端到端：中间隔着什么

指令快 1.94 倍，不等于模型快 1.94 倍。这中间要穿过打包、变换、修正、输出转换、模型路由、服务层。这个项目的价值恰恰在于它把每一层都量了。

### 前馈算子（含全部开销）

测的是**完整的原生路径**：输入打包 → 原生 gate/up → 激活并重打包 → 原生 down 投影 → BF16 转 F32 输出。

| 物理行数 | Kairic IU4 | 紧凑对照 | 加速比 | 延迟降低 |
|---:|---:|---:|---:|---:|
| 96 | 1.162 ms | 2.928 ms | **2.52×** | 60.3% |
| 128 | 1.219 ms | 3.700 ms | **3.04×** | 67.1% |
| 256 | 1.999 ms | 6.706 ms | **3.35×** | 70.2% |
| 512 | 3.801 ms | 13.222 ms | **3.48×** | 71.3% |

**行数越多加速比越高**——符合矩阵指令的特性，批量越大越能摊薄固定开销。

### 提示词处理（prompt processing）

同一个二进制、同一个模型、同一套 sidecar，只换前馈通路：

| 物理行数 | 对照 PP | Kairic IU4 PP | 提升 |
|---:|---:|---:|---:|
| 96 | 234.64 tok/s | 325.56 tok/s | +38.75% |
| 256 | 310.97 tok/s | 488.72 tok/s | +57.16% |
| 512 | 321.60 tok/s | 529.22 tok/s | +64.56% |
| **合计** | **297.42** | **464.06** | **+56.03%** |

### 端到端：164 题编程套件

| 版本 | HumanEval Base | Plus | 合计 TG | 峰值 TG | 生成耗时 |
|---|---:|---:|---:|---:|---:|
| **Kairic Edge IU4** | **158/164 (96.34%)** | **152/164 (92.68%)** | **47.73 tok/s** | **106.68** | **950.45 s** |
| Unsloth Dynamic Q4 | 158/164 (96.34%) | 148/164 (90.24%) | 25.80 tok/s | 30.00 | 1,778.27 s |
| Unsloth Dynamic Q6 | 157/164 (95.73%) | 150/164 (91.46%) | 25.31 tok/s | 27.99 | 1,732.38 s |

对 Q4：生成吞吐 **+85.03%**，耗时 **−46.55%**，峰值 **3.56 倍**，Base 打平、Plus **多过 4 题**。

**质量没掉，这是最关键的一条。** 4bit 原生通路常见的担心是精度损失，但 HumanEval Base 和 Q4 打平、Plus 反而更好。

---

## 但作者自己给这些数字打了折扣

这是我认为这个项目最值得写的地方——**它主动说明了自己的对比不干净**。

模型卡原文：

> 这些是**配置系统对比**，不是单变量量化实验。Kairic Edge 用的是它的发布配置：262,144 上下文、8 GiB 提示词缓存、32 个上下文检查点；对照组跑在 65,536 上下文、没有那份缓存分配。生成吞吐是最有用的跨运行信号，但不同的完整配置必须保持可见。

翻译一下：**这不是「同样条件下换个量化格式」，而是「我这套完整方案 vs 别人那套完整方案」。** 85% 的提升里，有多少来自 IU4 指令、多少来自 262K 上下文配置和 8GB 提示词缓存，模型卡没有拆开——但它明确告诉你没拆开。

它还进一步声明了三个「我没有宣称」：

> 这不是在宣称模型里每个算子都原生跑在 4bit、不是在宣称 M1 解码是原生 IU4、也不是一个厂商级或能效级的结论。

对比一下我前一篇写的 Spark-X2.5-4B：那边的对照分数是从别人的模型卡里抄的公开值，自己的模型按自己最优参数跑。这边至少把配置差异摊开说了。

**而且它公布了对照文件的 SHA-256**：

| 标签 | 文件 | 字节数 | SHA-256 前缀 |
|---|---|---:|---|
| Unsloth Dynamic Q4 | `Qwen3.8-27B-UD-Q4_K_M.gguf` | 16,464,440,224 | `322e194ff797...` |
| Unsloth Dynamic Q6 | `Qwen3.8-27B-UD-Q6_K_XL.gguf` | 25,299,061,664 | `701d8fa9ed21...` |

任何人都能核对它到底拿什么跟自己比。这个做法应该成为标配。

---

## 最硬的一条：它撤下了一个更快但会改变输出的路径

v1.2 版本说明里有一段，我认为比所有性能数字都重要。

早期版本有个「原生 IU4 M65 验证器」，用在投机解码的验证环节，比安全路径快 **7.89%**（48.73 → 52.57 tok/s）。它通过了十项任务的筛查。

然后作者做了一次确定性追踪，发现：**在一个可复现的低边际案例上，这条原生路径可能选出和 M1／关闭投机解码时不同的贪心 token。**

模型卡里的判断是一句话：

> 投机解码应当改变速度，而不是目标模型的答案。

于是 v1.2 把这条快路降级为非默认，只保留在 `KAIRIC_UNSAFE_NATIVE_M65_VERIFY=1` 下做诊断用，并明确写「不要在对正确性敏感的服务里开启」。

代价是承认：v1.2 在重度依赖 M65 的负载上比那条不安全路径**慢约 5–8%**。

**为了正确性主动交回 7.89% 的性能，还把变量名里写上 `UNSAFE`。** 在一个人人堆 benchmark 数字的领域里，这是罕见的。

v1.2 的验收结果也一并给了：六次运行全部产出目标一致的响应哈希，五次热运行 **22.31–22.38 秒**（均值 22.34），草稿 token 接受率 **99.73%**（9,255/9,280），平均接受长度 64.83 token，仍比关闭投机解码快 **7.19 倍**。

---

## 代价是什么？Dual View 的内存账

这套东西不是白拿的。

Kairic Edge 是个 **Dual View** 模型：GGUF 是权威视图，负责存储、质量敏感的选择、目标解码，以及所有不支持的形状；另外三个 `.pfs` 伴生文件提供阶段专用的加速视图。

**Prompt Forge** 是运行时那一层，负责识别请求的物理形状，只把符合条件的操作路由到快视图，形状或算子超出验证范围就**失败回落**（fail closed）到权威路径。

内存账：

| 文件 | 角色 | 体积 |
|---|---|---:|
| `Qwen3.8-27B-IU4-Kairic-Edge.gguf` | 权威模型 | **15.48 GiB** |
| `Qwen3.8-27B-Kairic-IU4-FFN.pfs` | 前馈 sidecar | 7.99 GiB |
| `Qwen3.8-27B-Kairic-IU4-GDN.pfs` | 循环投影 sidecar | 1.88 GiB |
| `Qwen3.8-27B-Kairic-IU4-GDN-Output.pfs` | 输出投影 sidecar | （另计）|

**加速伴生文件要多占 10.57 GiB。** 也就是说总占用约 26 GiB——这在 Strix Halo 的 128GB 统一内存上不是问题，换个机器就是问题了。

模型卡把这笔账写在正文里而不是脚注里：「Dual View 确实有内存代价……收益是拿到一条阶段专用的计算路径，而不必让加速视图对所有算子都成为权威。」

另外还有个提示词缓存，效果夸张：

| 前缀长度 | 冷启动 | 热缓存 | 降幅 |
|---:|---:|---:|---:|
| 2K | 6,232 ms | 100.60 ms | 98.39% |
| 8K | 18,190 ms | 106.38 ms | 99.42% |
| 32K | 100,045 ms | 127.91 ms | **99.87%** |

32K 前缀从 100 秒降到 128 毫秒。但注意这只在**重复前缀**的服务形态下成立，不是通用加速。

---

## 谁在做这件事？

作者 HF 账号 `jcbtc`，显示名 "Ciru - Crown"，129 关注者，25 个模型。这是 **Kairic.ai** 的首次公开亮相——一家做 AI 硬件与软件优化的公司，自我定位是「构建高性能推理基础设施」。

翻他的模型列表会发现一件事：**这个人在 AMD Strix Halo 上已经做了一整个系列**，不是一次性作品：

| 模型 | 下载 |
|---|---:|
| `Qwen3.8-Flash-CIRU-STRIX-IU4` | 22,343 |
| `Qwen3.8-27B-CIRU-ActiveFPX-PromptForge` | 3,203 |
| `Qwen3.8-27B-IU4-Kairic-Edge` | 3,008 |
| `Laguna-S-2.1-Chadrock-ROCmFP4-StrixKVSpine-V4-GGUF` | 1,939 |
| `Ling-3.0-Flash-CIRU-IU4` | 829 |

运行时仓库 `ciru-ai/ROCmFPX`（MIT，C++，36 星，建于 2026-06-20）的描述是「面向 AMD 硬件的 ROCmFPX 家族，更多量化和专用 agent 量化」。

**一个必须说清的限制**：标准 llama.cpp **跑不了**这个模型。它不认识 Kairic 的 sidecar，也不认识 `--kairic-edge` 参数。你必须自己构建那个固定版本的运行时分支。这是一条相当高的门槛。

---

## 这件事的普遍意义在哪？

跳出这一个模型看，有三条可以带走：

**其一，量化的天花板可能不在算法，在指令集。** 社区在 GGUF 量化格式上卷了很久（Q4_K_M、IQ4_XS、各种 imatrix），但那些都是在「怎么把权重压小、解压后照常算」的框架里优化。IU4 换了一个问题：**能不能让硬件直接吃 4bit**。这条路的上限取决于芯片上有没有这条指令，而不是量化算法多聪明。

**其二，AMD 的消费级硬件正在长出自己的生态位。** Strix Halo（Ryzen AI Max+ 395 / Radeon 8060S）有 128GB 统一内存，能装下 27B 模型 + 10GB 伴生文件还有富余。HuggingFace 上搜 "Strix Halo" 已经能找到一整批社区量化——`DeepSeek-V4-Flash-Strix-Halo-GGUF`（24,326 下载）、`Qwen3.8-Flash-Next-MTP-Strix-Halo-GGUF`（4,206）等等。这是个正在形成的、绕开 NVIDIA 的本地推理路径。

**其三，「配置系统对比」这个词应该进入所有人的词汇表。** 看到「比 X 快 85%」时，第一个该问的是：**是同一个变量变了，还是两套完整方案在比？** 这个项目主动回答了这个问题，多数项目不会。

---

## 缺口：我没有 Strix Halo，一条都没实测

按规矩说清楚。本文全部基于模型卡、运行时仓库和 AMD 的 RDNA 3.5 指令集文档，**没有任何一条数字是我复现的**。

1. **没有 AMD Ryzen AI Max+ 395 机器**，104.66 TOPS、47.73 tok/s、2.52–3.48 倍前馈加速，全部是作者自报。
2. **没有构建那个自定义运行时。** `ciru-ai/ROCmFPX` 的 kairic-edge 分支能不能顺利编出来、依赖多重，未知。
3. **85% 的提升里 IU4 贡献了多少，分不出来。** 作者已经声明这是配置系统对比，我也没有条件做单变量实验。
4. **v1.2 的正确性修复我只能采信其说法。** 那个「原生 M65 验证器会改变贪心 token」的问题，我没有复现路径。
5. **Kairic.ai 这家公司背景不明。** 官网 kairic.ai，除此之外没有可核查的信息。

想验证的话，需要一台 Strix Halo 机器。如果你有，这套东西值得跑一遍——尤其是把 IU4 单独作为变量的 A/B。

---

## 一句话总结

这个项目的技术贡献是**把 4bit 从存储格式变成了硬件执行策略**，并且在指令、算子、端到端三个层级都给了数字。

但它真正值得推荐的地方，是**它对自己数字的诚实程度**：主动标注对比不是单变量、公布对照文件的哈希、以及为了不改变模型输出而撤下一条快 7.89% 的路径。

在这个人人报最优数字的领域，这种做法本身比 104.66 TOPS 更稀缺。

> 📌 模型卡：https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge
> v1.2 发布说明：https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge/blob/main/RELEASE_NOTES_v1.2.md
> 运行时源码：https://github.com/ciru-ai/ROCmFPX/tree/kairic-edge-qwen38-27b-v1.2
> AMD RDNA 3.5 指令集文档：https://docs.amd.com/v/u/en-US/rdna35_instruction_set_architecture
> 基座模型：https://huggingface.co/Qwen/Qwen3.8-27B

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

The overwhelming majority of so-called "4-bit quantized models" are 4-bit only in **storage**. When the matrix multiply actually runs, the weights are widened back to FP16 or INT8 first — the saving is memory and bandwidth, not compute.

`Qwen3.8-27B-IU4-Kairic-Edge` does something else: it **keeps 4-bit data inside the compute path**, feeding AMD RDNA 3.5's native 4-bit integer matrix instruction directly.

The author claims this is the first known accelerated IU4 lane running inside a served 27B language model on AMD `gfx1151`.

> 📌 Model card: https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge
> Runtime source: https://github.com/ciru-ai/ROCmFPX (branch kairic-edge-qwen38-27b-v1.2)
> Apache-2.0 ｜ base Qwen/Qwen3.8-27B ｜ hardware AMD Ryzen AI Max+ 395 / Radeon 8060S (gfx1151)

---

## What IU4 actually is

RDNA 3.5's instruction set contains `V_WMMA_I32_16X16X16_IU4`: **packed unsigned 4-bit activations × signed 4-bit weights with 32-bit integer accumulation**, followed by explicit scale/zero-point reconstruction.

The distinction:

| | Ordinary "4-bit quantization" | Native IU4 lane |
|---|---|---|
| Storage | 4-bit | 4-bit |
| Before the matrix instruction | **Widened to FP16 / INT8** | **Stays packed at 4-bit** |
| Instruction actually executed | FP16 or INT8 matmul | `V_WMMA_I32_16X16X16_IU4` |
| Benefit | Less memory, less bandwidth | **Less memory + faster math** |

The model card puts it precisely: this **turns low precision into a compute advantage, not just a capacity advantage.**

### Measured at the instruction level

On a short dependency-chain instruction harness (HIP event timing, best of three):

| Dependency chains | IU4 TOPS | IU8 TOPS | FP16 TOPS |
|---:|---:|---:|---:|
| 2 | 99.87 | 50.65 | 52.35 |
| 4 | 100.09 | 52.94 | 52.47 |
| 8 | **104.66** | **54.30** | **53.87** |

At the strongest point, IU4 is **1.93×** IU8 and **1.94×** FP16 — same device, same run.

The author explicitly notes these are **GPU instruction rates**, not NPU marketing figures, not sustained application throughput, and not power measurements. That kind of self-limitation is rare on a model card.

---

## From instruction to end-to-end: what sits in between

An instruction being 1.94× faster does not make the model 1.94× faster. In between lie packing, transforms, corrections, output conversion, model routing and serving. The value of this project is that it measured every layer.

### Feed-forward operator, inclusive of all overhead

The measured route is the **complete native path**: input packing → native gate/up → activation-and-repack → native down projection → BF16-to-F32 output.

| Physical rows | Kairic IU4 | Compact control | Speedup | Latency cut |
|---:|---:|---:|---:|---:|
| 96 | 1.162 ms | 2.928 ms | **2.52×** | 60.3% |
| 128 | 1.219 ms | 3.700 ms | **3.04×** | 67.1% |
| 256 | 1.999 ms | 6.706 ms | **3.35×** | 70.2% |
| 512 | 3.801 ms | 13.222 ms | **3.48×** | 71.3% |

**More rows, higher speedup** — consistent with matrix instructions, where larger batches amortize fixed overhead.

### Prompt processing

Same binary, same model, same sidecars; only the feed-forward lane changed:

| Physical rows | Control PP | Kairic IU4 PP | Gain |
|---:|---:|---:|---:|
| 96 | 234.64 tok/s | 325.56 tok/s | +38.75% |
| 256 | 310.97 tok/s | 488.72 tok/s | +57.16% |
| 512 | 321.60 tok/s | 529.22 tok/s | +64.56% |
| **Pooled** | **297.42** | **464.06** | **+56.03%** |

### End-to-end: a 164-task coding suite

| Release | HumanEval Base | Plus | Aggregate TG | Peak TG | Generation time |
|---|---:|---:|---:|---:|---:|
| **Kairic Edge IU4** | **158/164 (96.34%)** | **152/164 (92.68%)** | **47.73 tok/s** | **106.68** | **950.45 s** |
| Unsloth Dynamic Q4 | 158/164 (96.34%) | 148/164 (90.24%) | 25.80 tok/s | 30.00 | 1,778.27 s |
| Unsloth Dynamic Q6 | 157/164 (95.73%) | 150/164 (91.46%) | 25.31 tok/s | 27.99 | 1,732.38 s |

Against Q4: throughput **+85.03%**, time **−46.55%**, peak **3.56×**, Base tied and Plus **four tasks better**.

**Quality did not drop, which is the critical part.** The usual worry with a native 4-bit path is precision loss; here Base ties Q4 and Plus comes out ahead.

---

## But the author discounts these numbers himself

This is the part I find most worth writing about — **the project states outright that its comparison is not clean**.

From the model card:

> These are **configured-system comparisons**, not a one-variable quantization experiment. Kairic Edge used its release configuration at 262,144 context with an 8 GiB prompt cache and 32 context checkpoints; the comparison runs used 65,536 context without that cache allocation. Generation throughput is the most useful cross-run signal, but the different complete configurations must remain visible.

Translated: **this is not "same conditions, different quantization format" but "my whole stack versus their whole stack."** How much of the 85% comes from the IU4 instruction versus the 262K context configuration and the 8GB prompt cache is not separated — but you are told it is not separated.

It goes further with three explicit non-claims:

> This is not a claim that every operation in the model runs natively at four bits, that M1 decode is native IU4, or that this is a vendor-wide or energy-efficiency result.

Contrast with Spark-X2.5-4B from my previous post: there the comparison scores were lifted from other people's model cards while the author's own model ran at its best settings. Here, at least, the configuration difference is laid out.

**And the comparison artifacts are published with SHA-256:**

| Label | File | Bytes | SHA-256 prefix |
|---|---|---:|---|
| Unsloth Dynamic Q4 | `Qwen3.8-27B-UD-Q4_K_M.gguf` | 16,464,440,224 | `322e194ff797...` |
| Unsloth Dynamic Q6 | `Qwen3.8-27B-UD-Q6_K_XL.gguf` | 25,299,061,664 | `701d8fa9ed21...` |

Anyone can verify exactly what it measured itself against. This should be standard practice.

---

## The hardest call: it withdrew a faster path because it changed the output

Buried in the v1.2 release notes is something I consider more important than any performance number.

An earlier version had a "native IU4 M65 verifier" used in speculative decoding's verification stage, **7.89% faster** than the safe path (48.73 → 52.57 tok/s). It passed a ten-task screen.

Then the author ran a deterministic trace and found: **on a reproduced low-margin case, the native path could select a different greedy token than M1 / speculation-off decoding.**

The model card's judgment is one sentence:

> Speculative decoding must change speed, not the target model's answer.

So v1.2 demoted that fast path out of the default, retaining it only for diagnostics behind `KAIRIC_UNSAFE_NATIVE_M65_VERIFY=1`, with an explicit "do not enable it for correctness-sensitive serving."

The admitted cost: v1.2 runs roughly **5–8% slower** than the unsafe path on M65-heavy workloads.

**Handing back 7.89% of performance for correctness — and putting `UNSAFE` in the variable name.** In a field where everyone piles up benchmark numbers, that is rare.

The v1.2 acceptance gate is published too: six runs all produced the target-identical response hash, five warm runs in **22.31–22.38 seconds** (mean 22.34), **99.73%** draft-token acceptance (9,255/9,280), mean accepted length 64.83 tokens, still **7.19×** faster than speculation off.

---

## The cost: Dual View's memory bill

None of this is free.

Kairic Edge is a **Dual View** model: the GGUF is the authoritative view covering storage, quality-sensitive selection, target decode, and every unsupported shape; three `.pfs` companions provide phase-specialized accelerated views.

**Prompt Forge** is the runtime layer that identifies a request's physical shape and routes only qualified operations through the fast view, **failing closed** to the authoritative path when a shape or operation falls outside the validated envelope.

The bill:

| File | Role | Size |
|---|---|---:|
| `Qwen3.8-27B-IU4-Kairic-Edge.gguf` | authoritative model | **15.48 GiB** |
| `Qwen3.8-27B-Kairic-IU4-FFN.pfs` | feed-forward sidecar | 7.99 GiB |
| `Qwen3.8-27B-Kairic-IU4-GDN.pfs` | recurrent projection sidecar | 1.88 GiB |
| `Qwen3.8-27B-Kairic-IU4-GDN-Output.pfs` | output projection sidecar | (additional) |

**The accelerated companions add 10.57 GiB.** Around 26 GiB total — a non-issue on Strix Halo's 128GB unified memory, a real issue anywhere else.

The model card puts this in the body rather than a footnote: "Dual View does have a memory cost… The gain is a phase-specialized compute path without making the accelerated view authoritative for every operation."

There is also a prompt cache with dramatic effect:

| Prefix | Cold | Warm | Reduction |
|---:|---:|---:|---:|
| 2K | 6,232 ms | 100.60 ms | 98.39% |
| 8K | 18,190 ms | 106.38 ms | 99.42% |
| 32K | 100,045 ms | 127.91 ms | **99.87%** |

A 32K prefix goes from 100 seconds to 128 milliseconds. Note this only holds for a **repeated-prefix** serving shape; it is not general speedup.

---

## Who is doing this?

The HF account is `jcbtc`, display name "Ciru - Crown," 129 followers, 25 models. This is the first public introduction of **Kairic.ai**, an AI hardware and software optimization company positioning itself as building performance inference infrastructure.

Scrolling the model list reveals something: **this person has built an entire series on AMD Strix Halo**, not a one-off:

| Model | Downloads |
|---|---:|
| `Qwen3.8-Flash-CIRU-STRIX-IU4` | 22,343 |
| `Qwen3.8-27B-CIRU-ActiveFPX-PromptForge` | 3,203 |
| `Qwen3.8-27B-IU4-Kairic-Edge` | 3,008 |
| `Laguna-S-2.1-Chadrock-ROCmFP4-StrixKVSpine-V4-GGUF` | 1,939 |
| `Ling-3.0-Flash-CIRU-IU4` | 829 |

The runtime repo `ciru-ai/ROCmFPX` (MIT, C++, 36 stars, created 2026-06-20) describes itself as "ROCmFPX Family for AMD Hardware and Processors. More quants and special agent quants."

**One limitation that must be stated**: stock llama.cpp **cannot run this model**. It does not understand the Kairic sidecars or the `--kairic-edge` flag. You must build the pinned runtime branch yourself — a substantial barrier.

---

## Why this matters beyond one model

Three takeaways:

**One, quantization's ceiling may lie in the instruction set, not the algorithm.** The community has iterated hard on GGUF quantization formats (Q4_K_M, IQ4_XS, various imatrix schemes), but all of that optimizes within "compress the weights, decompress, compute as usual." IU4 changes the question to **can the hardware eat 4 bits directly**. That path's ceiling depends on whether the silicon has the instruction, not on how clever the quantizer is.

**Two, AMD's consumer hardware is growing its own niche.** Strix Halo (Ryzen AI Max+ 395 / Radeon 8060S) has 128GB of unified memory — room for a 27B model plus 10GB of companions with margin to spare. Searching "Strix Halo" on HuggingFace already returns a whole cohort of community quants: `DeepSeek-V4-Flash-Strix-Halo-GGUF` (24,326 downloads), `Qwen3.8-Flash-Next-MTP-Strix-Halo-GGUF` (4,206) and others. A local-inference path around NVIDIA is forming.

**Three, "configured-system comparison" belongs in everyone's vocabulary.** When you see "85% faster than X," the first question is: **did one variable change, or are two complete stacks being compared?** This project answers that unprompted. Most do not.

---

## Gaps: I have no Strix Halo and verified none of this

Per this site's rules. Everything here comes from the model card, the runtime repo and AMD's RDNA 3.5 ISA documentation; **not one number is reproduced by me**.

1. **No AMD Ryzen AI Max+ 395 machine.** The 104.66 TOPS, 47.73 tok/s, and 2.52–3.48× feed-forward speedups are all vendor-reported.
2. **I did not build the custom runtime.** Whether the `ciru-ai/ROCmFPX` kairic-edge branch compiles cleanly, and how heavy its dependencies are, is unknown.
3. **How much of the 85% is IU4 cannot be separated.** The author already states it is a configured-system comparison, and I have no way to run the single-variable experiment.
4. **The v1.2 correctness fix is taken on trust.** I have no path to reproduce the "native M65 verifier changes a greedy token" issue.
5. **Kairic.ai's background is unclear.** Beyond kairic.ai, there is no verifiable information.

Verifying this needs a Strix Halo box. If you have one, this is worth running — particularly an A/B isolating IU4 as the single variable.

---

## In one line

The technical contribution is **turning 4-bit from a storage format into a hardware execution strategy**, with numbers at the instruction, operator and end-to-end levels.

But what genuinely earns the recommendation is **how honest it is about its own numbers**: stating unprompted that the comparison is not single-variable, publishing hashes of the comparison artifacts, and withdrawing a 7.89%-faster path rather than let it alter the model's output.

In a field where everyone reports their best number, that is scarcer than 104.66 TOPS.

> 📌 Model card: https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge
> v1.2 release notes: https://huggingface.co/jcbtc/Qwen3.8-27B-IU4-Kairic-Edge/blob/main/RELEASE_NOTES_v1.2.md
> Runtime source: https://github.com/ciru-ai/ROCmFPX/tree/kairic-edge-qwen38-27b-v1.2
> AMD RDNA 3.5 ISA: https://docs.amd.com/v/u/en-US/rdna35_instruction_set_architecture
> Base model: https://huggingface.co/Qwen/Qwen3.8-27B

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
