---
title: "Laya ANE：把 421M 决策模型烧进 Apple 神经引擎"
titleEn: "Laya ANE: Burning a 421M Decision Model onto the Apple Neural Engine"
description: "NMTZ/laya-typed-decisions-421m-coreml-ane，社区将 convaiinnovations/laya-typed-decisions 421M 参数模型转换为 Core ML ANE 格式，提供 L192/L384/L512/L640 四个固定形状档位。Apache 2.0。推荐默认 L512：M4 24GB 实测 ANE 78.35ms vs MLX 97.31ms（1.24x 快），能耗 2.07x 低。非独立模型，需配合原始 checkpoint 的 tokenizer、embedding、FP32 action head 使用；短输入下 ANE 反比 MLX 慢，Local System One 用路由+兜底而非盲目全发 ANE。基准测试工具在 NMTZ-z/system-one-benchmark-lab。"
descriptionEn: "NMTZ/laya-typed-decisions-421m-coreml-ane — community conversion of convaiinnovations/laya-typed-decisions 421M to Core ML ANE format. Four fixed-shape variants: L192/L384/L512/L640. Apache 2.0. Recommended default L512: M4 24GB tests show ANE 78.35ms vs MLX 97.31ms (1.24× faster), 2.07× lower energy. Not standalone — requires original checkpoint's tokenizer, embeddings, FP32 action head. Short inputs can be slower on ANE than MLX; Local System One uses routing + fallback instead of blindly sending all decisions to ANE. Benchmark harness at NMTZ-z/system-one-benchmark-lab."
pubDate: 2026-10-06
heroImage: "../../assets/images/laya-ane-coreml-apple-neural-engine-typed-decisions-banner.jpg"
category: "Tech-Experiment"
tags: ["AI模型", "Apple Silicon", "Core ML", "ANE", "推理优化", "本地AI"]
lang: "zh-CN"
wechatTitle: "Laya ANE：决策模型烧进Apple神经引擎"
wechatDigest: "社区转换421M；L512推荐；ANE快1.24x省能2x；短输入需路由兜底"
---

Apple 神经引擎（ANE）是 Apple Silicon 芯片上一块专用的矩阵运算加速器——它比 GPU 和 CPU 在某些推理任务上快很多，但它有一个约束：只接受**固定形状**的输入。标准的语言模型推理需要动态序列长度，所以大多数模型没办法直接跑在 ANE 上。

Laya ANE 是一个社区转换项目：把 convaiinnovations/laya-typed-decisions（421M 参数，Typed Decisions 风格决策模型）转成 Core ML ANE 格式，允许它在 Apple Silicon 上使用 ANE 加速。

HuggingFace: https://huggingface.co/NMTZ/laya-typed-decisions-421m-coreml-ane | Apache 2.0
Benchmark: https://github.com/NMTZ-z/system-one-benchmark-lab | Apache 2.0

---

## 四个档位

这次转换提供了四个固定形状的 ANE 包：

| 档位 | 冻结工作负载覆盖率 | 用途 |
|------|---------------------|------|
| L192 | 499/2000 = **24.95%** | 短上下文实验 |
| L384 | 1814/2000 = **90.70%** | 中等覆盖 |
| L512 | 1966/2000 = **98.30%** | **推荐默认** |
| L640 | 2000/2000 = **100%** | 全覆盖研究用 |

这里的"冻结工作负载"指 2000 个决策任务的固定基准集。L512 覆盖了其中 98.3%，是实用性和覆盖率的最佳平衡点。

---

## L512 实测数据（Apple M4, 24GB 统一内存）

在 1966 个匹配 L512 固定形状的任务上：
- **选择决策一致性**（vs MLX）：1962/1966 = **99.8%**
- **ANE 中位延迟**：78.35ms
- **MLX 中位延迟**：97.31ms → ANE **快 1.24×**

能耗对比（128 决策能耗工作负载）：
- L512 ANE：**2.068 J/决策**
- MLX：**4.288 J/决策**
- 能耗改善：**2.07×**

---

## 这不是一个独立模型

这是理解 Laya ANE 最重要的一点：**这些 ANE 包只包含 transformer 的主体部分**（body）。

完整推理还需要从原始 convaiinnovations/laya-typed-decisions checkpoint 里的：
- **Tokenizer 和 prompt 准备**
- **原始 embedding lookup**
- **FP32 host-side action head**

原始模型的 `model.safetensors` 故意没有复制到这个 HuggingFace 仓库。你需要：
1. 下载原始 convaiinnovations/laya-typed-decisions checkpoint（source revision: f9ab0b22...）
2. 从这里下载对应的 ANE body 包
3. 在 Local System One 框架里组合使用

---

## 短输入的反直觉结果

固定形状有一个代价：**当实际输入比固定形状短很多时，ANE 反而会比 MLX 慢**。

L512 对应的固定形状是为 512 token 量级的输入设计的。如果你只给了 20 个 token 的输入，模型要把它 pad 到 512 再跑——这个填充开销让 ANE 在短输入场景下比 MLX 慢。

这就是为什么 Local System One 用路由+兜底策略，而不是把所有决策请求一律发给 ANE：
- 长输入 → ANE（快 1.24×）
- 短输入 → MLX（无 pad 开销）

这个实验本身就是一个好的设计教训：专用硬件加速器往往有"甜点区"，盲目全量使用反而会变慢。

---

## 转换来源

转换工具来自 mizorewww/laya-coreml（revision: 4619e048...），不是 Convai Innovations 或 Apple 的官方发布。这是社区独立完成的 Core ML 转换，发布在 NMTZ 命名空间下。

基准测试工具（NMTZ-z/system-one-benchmark-lab）是配套的冻结基准套件，用于验证四个 ANE 档位的覆盖率和延迟。它可以在相同的固定输入集上对比 ANE 和 MLX 的输出一致性。

---

> Apache 2.0。NMTZ 社区转换，非 Convai Innovations 或 Apple 官方发布。开源仅供学习参考。

---

<!--EN-->

## Laya ANE: Burning a 421M Decision Model onto the Apple Neural Engine

The Apple Neural Engine (ANE) is a dedicated matrix acceleration unit in Apple Silicon — faster than GPU and CPU for certain inference tasks, but with one hard constraint: it only accepts **fixed-shape** inputs. Standard language model inference requires dynamic sequence lengths, which is why most models can't run on ANE directly.

Laya ANE is a community conversion project: transforming convaiinnovations/laya-typed-decisions (421M parameters, Typed Decisions style) into Core ML ANE format for accelerated inference on Apple Silicon.

HuggingFace: https://huggingface.co/NMTZ/laya-typed-decisions-421m-coreml-ane | Apache 2.0
Benchmark: https://github.com/NMTZ-z/system-one-benchmark-lab | Apache 2.0

---

### Four Variants

Four fixed-shape ANE packages:

| Variant | Frozen workload coverage | Role |
|---------|--------------------------|------|
| L192 | 499/2000 = 24.95% | Short-context experiments |
| L384 | 1814/2000 = 90.70% | Intermediate trade-off |
| L512 | 1966/2000 = 98.30% | **Recommended default** |
| L640 | 2000/2000 = 100% | Full-coverage research |

The "frozen workload" is a fixed set of 2,000 decision tasks. L512 covers 98.3% of them — the best balance of practicality and coverage.

---

### L512 Benchmarks (Apple M4, 24GB Unified Memory)

On the 1,966 tasks matching L512's fixed shape:
- **Decision agreement (vs MLX)**: 1962/1966 = **99.8%**
- **ANE median latency**: 78.35ms
- **MLX median latency**: 97.31ms → ANE is **1.24× faster**

Energy (128-decision energy workload):
- L512 ANE: **2.068 J/decision**
- MLX: **4.288 J/decision**
- Energy improvement: **2.07×**

---

### Not a Standalone Model

These ANE packages contain only the transformer body. Full inference also requires the original convaiinnovations/laya-typed-decisions checkpoint for tokenizer + prompt preparation, original embedding lookup, and FP32 host-side action head. The original `model.safetensors` is intentionally not duplicated here. You need both the original checkpoint and these ANE body packages, combined via Local System One.

---

### The Counterintuitive Short-Input Result

Fixed shape has a cost: **when actual input is much shorter than the fixed shape, ANE can be slower than MLX**. L512 pads short inputs to 512 tokens — that padding overhead makes ANE slower on very short inputs. This is why Local System One uses routing + fallback rather than blindly sending every decision to ANE: long inputs → ANE (1.24× faster); short inputs → MLX (no padding overhead). Dedicated hardware accelerators have "sweet spots" — blind full deployment can backfire.

---

### Source

Conversion tool: mizorewww/laya-coreml (revision: 4619e048). This is an independent community conversion, not an official Convai Innovations or Apple release.

---

> Apache 2.0. Community conversion by NMTZ, not affiliated with Convai Innovations or Apple. For technical reference only.
