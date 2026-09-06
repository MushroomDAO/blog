---
title: "DGX Spark 上跑视频生成：FlashAttention 没用、torch.compile 没用、量化也没用"
titleEn: "Video Generation on a DGX Spark: FlashAttention Doesn't Help, torch.compile Doesn't Help, Quantization Doesn't Help Either"
description: "FastVideo 给 NVIDIA DGX Spark（GB10）写的调优文档罕见地列了「什么没用」：编译 FlashAttention 零加速、torch.compile VAE 触发重编译风暴只剩 1.1x、长序列模型上的 fp8/nvfp4 线性层量化约等于噪声。真正有用的只有一条——换蒸馏少步模型，3 步 40 秒 vs 全步 12 分钟，约 18 倍。根因是 GB10 的 128GB 统一内存只有约 270 GB/s 带宽，比数据中心 HBM 低约 10 倍。附双 Spark 串联和 Apple Silicon MLX 路径的实测数字。"
descriptionEn: "FastVideo's tuning guide for the NVIDIA DGX Spark (GB10) does something rare: it lists what does NOT help. Building FlashAttention gives zero speedup, torch.compile on the VAE triggers a recompile storm for only ~1.1x, and fp8/nvfp4 linear quantization on long-sequence models is measurement noise. Exactly one lever matters — switch to a distilled few-step model, 40 seconds at 3 steps versus 12 minutes full-step, roughly 18x. The cause is GB10's 128GB unified memory at only ~270 GB/s, about 10x below datacenter HBM. Includes two-Spark and Apple Silicon MLX numbers."
pubDate: 2026-09-07
updatedDate: 2026-09-07
category: "Tech-Experiment"
tags: ["本地推理", "视频生成", "NVIDIA", "DGX Spark", "Apple Silicon", "MLX", "硬件", "开源", "性能优化"]
heroImage: "../../assets/images/dgx-spark-gb10-video-generation-what-actually-helps-banner.jpg"
author: "Mycelium Protocol"
---

**一份告诉你「什么没用」的性能文档，比十份告诉你「什么很快」的有价值得多。**

FastVideo 给 NVIDIA DGX Spark 写的调优页就是这么一份。它开头那句话是：「这页讲的是 GB10 上哪些模型实际可用、什么真能让它变快、以及**什么帮不上忙（以及为什么）**，免得你花一整晚去拧根本拧不动的旋钮。」

本站之前写过两次 FastVideo 框架本身，这篇不重复讲框架——**讲的是把它放到一台具体的机器上，绝大多数「显而易见的优化」为什么全部失效。**

> 📌 FastVideo：https://github.com/hao-ai-lab/FastVideo （4340 星，Apache-2.0）
> DGX Spark 调优文档：https://hao-ai-lab.github.io/FastVideo/getting_started/installation/spark/
> FastH3 本地化公告（2026-09-01）：https://haoailab.com/blogs/fasth3-local/

---

## 先理解这台机器：128GB 内存，但只有 270 GB/s

GB10 把一颗 Blackwell GPU（`sm_121`）和 **128 GB 统一 LPDDR5X 内存**配在一起，CPU 和 GPU 共享，带宽约 **270 GB/s**。

**这个带宽比数据中心 GPU 的 HBM 低大约 10 倍。**

一句话就解释了后面所有反直觉的结论：**这台机器不缺容量，缺带宽。** 于是：

1. **受内存带宽限制的阶段代价被放大**——VAE 解码要搬大量数据，在少步生成里反而成了主要开销
2. **受算力限制的阶段随步数线性膨胀**——全步扩散（50+ 步）在这里就是纯粹的慢

还有个实操细节：GB10 上 `nvidia-smi` 报告显存是 `[N/A]`，系统的「已用」数字把 CPU + GPU + 缓存混在一起，只能当软上限看。要看单次运行的真实占用，得用 FastVideo 自己报的 `peak_memory_mb`。

---

## 唯一真正有用的一条：换蒸馏少步模型

| 模型 | 步数 | 每条视频耗时 | 瓶颈 |
|---|---:|---:|---|
| FastWan2.1-T2V-1.3B（蒸馏） | 3 | **~40 秒** | VAE 解码 |
| Wan2.1-T2V-1.3B（全步） | 50 | ~12 分钟 | 去噪 |
| Cosmos-Predict2.5-2B（全步） | 51 | ~47 分钟 | 去噪 |
| LTX2.3-distilled（含音频） | 8 | ~6 分钟 | 混合 |

**约 18 倍差距，来自换模型，不是来自调参数。**

而且瓶颈会**翻转**：大约在 **4 步**这个位置，主要开销从 VAE 解码切换到去噪循环。低于 4 步，你主要在为解码付钱；高于 4 步，主要在为去噪付钱。

这条对所有本地推理都有普遍意义：**先确认你的瓶颈在哪一段，再决定优化什么。** 在解码受限的场景里优化注意力，是白干。

---

## 那么，什么没用？

这是这份文档最有价值的部分。原文的表我整理如下：

| 手段 | 在 GB10 上的效果 | 用不用 |
|---|---|---|
| 蒸馏少步模型 | 约 18× | ✅ **首要手段** |
| bf16 VAE 解码 | 约 1.14×，无损；少步端到端约 5–7% | ✅ Wan 已默认开启 |
| VSA 视频稀疏注意力 | 开箱即用（Triton kernel 在 `sm_121` 上自动选中）| ✅ 自动 |
| **编译 FlashAttention** | **零加速** | ❌ 不值得编 |
| **torch.compile 编译 VAE 解码** | **重编译风暴，只剩约 1.1×** | ❌ 死路 |
| **长序列模型上的 fp8 / nvfp4 线性层量化** | **约等于没有** | ❌ 用错了地方 |
| FP4 注意力（`ATTN_QAT_INFER`） | 有效，但需要 QAT 训练过的权重 | ⚠️ 选择性开启 |
| 短序列模型上的 FP4 线性层（LTX2） | 1080p 去噪最多 −24% | ⚠️ 看模型和分辨率 |

三条「没用」，每条都值得单独说，因为它们否定的恰恰是大家的直觉。

### 为什么编译 FlashAttention 白费力气？

因为 **Torch 的 SDPA 在 `sm_121` 上已经走到了一个高效的 flash kernel**，FlashAttention 2 只是和它打平。

这条能省下很多人一整晚——在 ARM64 + CUDA 13 上从源码编 flash-attn 本来就折腾，编完发现没有任何提升。

### 为什么 torch.compile VAE 是死路？

因为 VAE 解码是**逐帧变化的形状**，`torch.compile` 会不断触发重编译（recompile storm）。编译开销吃掉了收益，最后只剩约 1.1×。

**普遍教训**：`torch.compile` 适合形状稳定的计算图。形状每次都变的地方，编译器帮不上忙，反而添乱。

### 为什么量化线性层约等于噪声？

这条最反直觉，也最有普遍价值。

量化线性层（GEMM）是所有人的第一反应。但在长序列视频模型上，一个 video-DiT 的去噪步骤是被 **O(N²) 的注意力**主导的——序列长度是几万 token 这个量级，**线性层只占个位数百分比的工作量**。

把占比个位数的那部分算快，总时间基本不动。文档给的实测是：在 Cosmos-2.5 上约 **1%**，也就是噪声。而且全步 CFG 模型还会因为逐步的量化误差掉质量。

**但同一个机制在短序列模型上是成立的**：LTX2 因为 VAE 压缩率高，注意力序列很短，FP4 线性层在那里能拿到 **−24%**。

文档总结的规则很干净：**在 GB10 上，有用的杠杆是注意力（稀疏或 FP4），不是线性层——除非这个模型的序列本来就短。**

---

## bf16 VAE 解码：唯一一个「小而稳」的收益

既然少步生成是解码受限的，那 VAE 解码的精度就是时间所在。

用 bf16 而不是 fp32 解码，**本质上是无损的**——在同一个 latent 上和 fp32 比，MS-SSIM 约 **0.9999**——同时快约 **1.14×**，在解码受限的少步模型上折合端到端 **5–7%**。

FastVideo 对 Wan 已经默认 `vae_decode_precision="bf16"`（编码仍保持 fp32）。

**为什么编码不能一起降**：解码是纯输出，降精度安全；而编码要为 I2V／因果模型播种去噪轨迹，动了会影响结果。这个区分很讲究。

---

## 一个实际的坑：这台机器很容易被自己搞死

文档专门有一节叫「安全运行：别把机器锁死」。

症状很具体：一次重编译或一次未分块的高分辨率解码，会把大约 20 个 ARM 核和统一内存吃干净，`sshd` 拿不到 CPU 时间，你就卡在 **"Connection timed out during banner exchange"**，只能物理断电重启。

避免办法：

```bash
# 推理：保持 VAE 分块开启（默认），降优先级跑
nice -n 19 nohup python your_script.py > run.log 2>&1 &

# 编译：限制并行度，别裸跑前台高并行编译
nice -n 19 MAX_JOBS=2 nohup pip install ... 
```

还有一条容易踩的：**不要手动把 CPU offload 打开。** FastVideo 在 worker 绑定 GB10 设备后会自动禁用 DiT 分层／CPU offload 和编码器／VAE 的 CPU offload——因为在统一内存架构上，「CPU offload」用的是同一块内存，等于原地打转。多卡 FSDP 分片仍然可用，因为它是真的切分权重而不是挪到另一个池子。

**这是统一内存架构的通用陷阱**，Apple Silicon 上同理：所有为「显存和内存分离」设计的 offload 策略，在统一内存上都失去意义。

---

## FastH3 在 GB10 上的两个专属处理

FastH3 是 FastVideo 和 Nuva Lab、NVIDIA FastGen 团队合作的 4 步稀疏蒸馏 MiniMax-H3 模型，**同步生成视频和音频**，2026-08-27 发布 Preview v1。

在单台 GB10 上它需要两个特殊处理：

**其一，延迟加载（lazy module load）必须开着。** 它的 Qwen3-VL 条件编码器是**几十 GB 的 BF16**。如果 DiT 和 VAE 在编码器还驻留内存时加载，进程会被 `earlyoom` 干掉（Python 通常是首选目标）。在统一内存上 `lazy_module_load` 会自动启用，按「编码器 → DiT → VAE」的顺序接管，DiT 还能在解码前先卸掉。文档明确警告：**不要传 `--no-lazy-module-load`**。

**其二，TAEH3 这个预览解码器效果惊人。** 用 `--video-decode-backend taeh3`：

| | 完整 VAE | TAEH3 |
|---|---:|---:|
| 768×1344×124 解码耗时 | **68 秒** | **2.4 秒** |

**28 倍**。一次 T2VA 生成端到端 **224 秒**完成。代价是重建是近似的，不是无损；而且 FL2VA/Ref2VA 仍然需要完整 VAE 来编码参考帧。

考虑到少步生成本来就是解码受限的，把 68 秒的解码压到 2.4 秒，几乎是把这条瓶颈整个拿掉了。

---

## 两台 Spark 串起来：1.3 倍，不是 2 倍

推文里说的「两台 DGX Spark 上生成」是真的，文档给了数字：

用序列并行（`sp_size=2`）跑在 QSFP RoCE 链路上：

| 任务 | 单台 GB10 | 两台 GB10 | 加速 |
|---|---:|---:|---:|
| 768×1344×124 FastH3 | 374–393 秒 | **292 秒** | 约 **1.3×** |
| 345 帧（约 14.4 秒）片段 | — | 587 秒 | — |

**两台机器只换来 1.3 倍**，不是 2 倍。而且**权重仍然是复制的**（不是分片），所以每台机器上依旧需要开延迟加载。

这个数字很诚实，也很说明问题：分布式推理的收益远低于机器数的线性增长，尤其当互联带宽和单机内存带宽在同一个量级上时。

---

## Apple Silicon 那条路：更值得你关注

对本站读者来说，DGX Spark 是一台买不买得起另说的机器；**Apple Silicon 这条路是现成的。**

FastVideo 在 2026-09-01 同时放出了 FastH3 的 MLX 版本，而且是**转换好的、开箱即跑**的检查点：

| 版本 | 权重体积 | 说明 |
|---|---:|---|
| `...-Dense-DataFree-MLX-INT4` | **10.74 GiB** | 仿射、纯权重 INT4，group size 64，激活保持 BF16 |
| `...-Dense-DataFree-MLX-INT8` | — | 同上，8bit |

关键限制先说：**这个导出是 dense-only，不支持 `--vsa`**（视频稀疏注意力）。

**它的 provenance 文件写得极其规范**，`conversion_manifest.json` 里能查到：

- 转换硬件：**Apple M4 Max**，统一内存 **36 GB**
- 转换耗时：单格式 46.1 秒，三种格式合计 **164.62 秒**
- 峰值 MLX 内存 **14.8 GiB**，进程峰值 RSS 11.3 GB，峰值内存足迹 27.1 GB
- MLX 版本 0.32.2，Python 3.12.13
- 验证：13 个源 transformer 分片全部校验、1,464 个张量、完成一次 **124 帧 832×480** 的完整 H3 VAE 生成
- 权重 SHA-256 全文公布

跑起来的命令也是完整的：

```bash
# 先下共享组件（tokenizer、Qwen3-VL 文本编码器、视频 VAE、音频 VAE）
hf download FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree \
  --revision f624f08c6c279ab43534c003e556fc5b295b6558 \
  --local-dir ./FastH3-Preview-v1-Dense-DataFree

# 再下转好的 MLX INT4 DiT
hf download FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree-MLX-INT4 \
  --local-dir ./FastH3-MLX-INT4

# 安装并生成
uv venv --python 3.12 --seed && source .venv/bin/activate
uv pip install -e ".[mlx]"

python examples/inference/basic/mlx_fasth3.py \
  --model-root ./FastH3-Preview-v1-Dense-DataFree \
  --mlx-checkpoint ./FastH3-MLX-INT4 \
  --prompt '(S1) A presenter says <d>[English] Fast H3 runs on Apple silicon.</d>' \
  --height 480 --width 832 --num-frames 124 --steps 4 --seed 2026 \
  --output-path ./outputs/fasth3_int4.mp4
```

文档说明 MLX 运行时**一次只加载一个重型组件**——和 GB10 上的延迟加载是同一个思路，因为统一内存的约束是同一个。

**许可要注意**：这个模型不是开源协议，走的是 MiniMax H3 Community License（`license: other`），转换版继承原模型的许可。这和 FastVideo 框架本身的 Apache-2.0 是两回事。

---

## 三条可以带走的普遍结论

**其一，先量瓶颈再优化。** GB10 上少步生成是解码受限的，所以优化注意力毫无意义；4 步以上变成去噪受限，结论就反过来。不知道瓶颈在哪就开始调参，是在赌。

**其二，统一内存架构会让一整类优化失效。** CPU offload、显存/内存分层策略、以及所有假设「GPU 内存和主机内存是两个池子」的技巧，在 GB10 和 Apple Silicon 上都是原地打转。这类机器的约束是**带宽**，不是容量。

**其三，「这个优化在我的硬件上有没有用」必须实测。** FlashAttention 在数据中心 GPU 上是标准操作，在 `sm_121` 上零收益；线性层量化在很多场景有效，在长序列视频模型上是 1% 的噪声。**没有普遍有效的优化，只有和硬件配对的优化。**

---

## 缺口：我没有 DGX Spark，MLX 那条也还没跑

如实说明：

1. **没有 DGX Spark。** 40 秒/12 分钟/47 分钟、双机 292 秒 vs 374–393 秒、TAEH3 的 2.4 秒 vs 68 秒，全部来自 FastVideo 文档，我一条都没复现。
2. **Apple Silicon MLX 那条我还没跑。** 这是**本文里唯一本机可验证**的部分——需要一台内存够的 Mac（转换是在 36GB M4 Max 上做的，INT4 权重 10.74 GiB，加上文本编码器和 VAE，估计 32GB 以上比较稳）。这是下一步该做的实测。
3. **没验证 FastH3 的生成质量。** 4 步蒸馏 + INT4 量化 + dense-only（无 VSA），三层折损叠加后的实际效果如何，只有跑了才知道。
4. **双 Spark 的 1.3 倍是单一配置下的数字**，其他分辨率和帧数的扩展性未知。

---

## 一句话总结

这份文档真正的价值不是「DGX Spark 能跑视频生成」，而是**它诚实地列出了在这台机器上做什么是白费力气**——FlashAttention、torch.compile、线性层量化，三条都是社区默认正确的操作，在 GB10 上全部失效，而且每条都给了失效的原因。

对绝大多数不会买 DGX Spark 的人，能带走的是那个方法：**优化之前先量瓶颈，以及承认优化和硬件是配对的、不存在普遍最优解。**

顺带，Apple Silicon 那条路是现成可试的：4 步、124 帧、832×480、INT4，10.74 GiB 权重，命令都在上面。

> 📌 FastVideo：https://github.com/hao-ai-lab/FastVideo
> DGX Spark 性能调优文档：https://github.com/hao-ai-lab/FastVideo/blob/main/docs/getting_started/installation/spark_performance.md
> 双 Spark 配对指南：https://github.com/hao-ai-lab/FastVideo/blob/main/docs/getting_started/installation/spark_pair.md
> FastH3 MLX INT4 权重：https://huggingface.co/FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree-MLX-INT4
> FastH3 推荐权重（VSA / DataFree）：https://huggingface.co/FastVideo/FastVideo-FastH3-4-step-Preview-v1-VSA-DataFree
> VSA 论文：https://arxiv.org/pdf/2505.13389

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**A performance document that tells you what does *not* help is worth ten that tell you what is fast.**

FastVideo's tuning page for the NVIDIA DGX Spark is exactly that. Its opening line: this page covers "which models are practical on the GB10, what actually makes them faster, and **what won't help (and why)**, so you don't burn a night tuning knobs that can't move on this hardware."

This site has covered the FastVideo framework twice already, so this post is not another framework tour — **it is about what happens when you put it on one specific machine and discover that most "obvious optimizations" simply fail.**

> 📌 FastVideo: https://github.com/hao-ai-lab/FastVideo (4,340 stars, Apache-2.0)
> DGX Spark tuning docs: https://hao-ai-lab.github.io/FastVideo/getting_started/installation/spark/
> FastH3 local announcement (2026-09-01): https://haoailab.com/blogs/fasth3-local/

---

## Understand the machine first: 128GB of memory, but only 270 GB/s

The GB10 pairs a Blackwell GPU (`sm_121`) with **128 GB of unified LPDDR5X memory** shared between CPU and GPU, at roughly **270 GB/s**.

**That bandwidth is about 10× below a datacenter GPU's HBM.**

One sentence explains every counterintuitive conclusion below: **this machine is not short on capacity, it is short on bandwidth.** Therefore:

1. **Memory-bandwidth-bound stages hurt disproportionately** — VAE decode moves a lot of data and becomes the dominant cost in few-step generation
2. **Compute-bound stages scale with step count** — full-step diffusion (50+ steps) is simply slow here

A practical detail: `nvidia-smi` reports memory as `[N/A]` on the GB10, and the system "used" figure conflates CPU + GPU + cache, making it only a soft upper bound. For real per-run usage, use FastVideo's own `peak_memory_mb`.

---

## The one lever that actually matters: distilled few-step models

| Model | Steps | Time / video | Bottleneck |
|---|---:|---:|---|
| FastWan2.1-T2V-1.3B (distilled) | 3 | **~40 s** | VAE decode |
| Wan2.1-T2V-1.3B (full-step) | 50 | ~12 min | denoise |
| Cosmos-Predict2.5-2B (full-step) | 51 | ~47 min | denoise |
| LTX2.3-distilled (with audio) | 8 | ~6 min | mixed |

**Roughly 18× from choosing a different model, not from tuning parameters.**

And the bottleneck **flips**: at around **4 steps**, the dominant cost switches from VAE decode to the denoising loop. Below four, you are mostly paying for decode; above it, mostly for denoise.

That generalizes to all local inference: **establish which stage is your bottleneck before deciding what to optimize.** Optimizing attention in a decode-bound regime is wasted work.

---

## So what doesn't help?

The most valuable part of the document. Its table, reorganized:

| Lever | Effect on the GB10 | Use it? |
|---|---|---|
| Distilled few-step model | ~18× | ✅ **the primary lever** |
| bf16 VAE decode | ~1.14×, lossless; ~5–7% e2e on few-step | ✅ default for Wan |
| VSA (video sparse attention) | works out of the box (Triton kernel auto-selects on `sm_121`) | ✅ automatic |
| **Building FlashAttention** | **no speedup** | ❌ not worth building |
| **torch.compile on VAE decode** | **recompile storm, only ~1.1×** | ❌ dead end |
| **fp8 / nvfp4 linear quantization on long-sequence models** | **essentially nothing** | ❌ wrong lever |
| FP4 attention (`ATTN_QAT_INFER`) | works, but needs QAT-trained weights | ⚠️ opt-in |
| FP4 linear on short-sequence models (LTX2) | up to −24% denoise at 1080p | ⚠️ model/resolution-dependent |

Each of the three "doesn't help" entries deserves its own note, because each negates a common instinct.

### Why building FlashAttention is wasted effort

Because **Torch's SDPA already reaches an efficient flash kernel on `sm_121`**, and FlashAttention 2 merely ties it.

This one saves people an entire evening — building flash-attn from source on ARM64 + CUDA 13 is painful enough before discovering it buys nothing.

### Why torch.compile on the VAE is a dead end

VAE decode has **shapes that vary per frame**, so `torch.compile` keeps triggering recompiles. Compilation overhead eats the gain, leaving about 1.1×.

**General lesson**: `torch.compile` suits stable computation graphs. Where shapes change every time, the compiler cannot help and actively gets in the way.

### Why quantizing linear layers is measurement noise

The most counterintuitive entry, and the most broadly useful.

Quantizing linear (GEMM) layers is everyone's first instinct. But on a long-sequence video model, a video-DiT denoise step is dominated by **O(N²) attention** — sequences of tens of thousands of tokens — and **the linear layers are a single-digit fraction of the work**.

Making a single-digit fraction faster leaves the total essentially unchanged. The measured figure on Cosmos-2.5 is about **1%**, i.e. noise. Full-step CFG models additionally lose quality to per-step quantization error.

**The same mechanism does work on short-sequence models**: LTX2's aggressive VAE compression yields short attention sequences, where FP4 linear reaches **−24%**.

The document's rule is clean: **on the GB10, the lever that matters is attention (sparse or FP4), not the linear layers — unless the model has short sequences.**

---

## bf16 VAE decode: the one small, reliable win

Since few-step generation is decode-bound, VAE decode precision is where the time is.

Decoding in bf16 rather than fp32 is **essentially lossless** — MS-SSIM around **0.9999** against fp32 on the identical latent — while being about **1.14×** faster, worth **5–7%** end-to-end on a decode-bound few-step model.

FastVideo already defaults Wan to `vae_decode_precision="bf16"`, with encode kept at fp32.

**Why encode cannot be lowered with it**: decode is output-only, so reduced precision is safe; encode seeds the denoising trajectory for I2V/causal models, so changing it changes results. A careful distinction.

---

## A real trap: this machine is easy to kill with your own job

The document has a section titled "Running safely (don't lock the box)."

The symptom is specific: one heavy build or one untiled high-resolution decode starves the ~20 ARM cores and unified memory, `sshd` cannot get cycles, and you are stuck at **"Connection timed out during banner exchange"** until a power cycle.

Avoidance:

```bash
# Inference: keep VAE tiling on (default), run at low priority
nice -n 19 nohup python your_script.py > run.log 2>&1 &

# Builds: cap parallelism; never a bare foreground high-parallelism build
nice -n 19 MAX_JOBS=2 nohup pip install ...
```

One more easy mistake: **do not manually re-enable CPU offload.** FastVideo automatically disables DiT layerwise/CPU offload and encoder/VAE CPU offload once a worker binds its GB10 device — because on unified memory, "CPU offload" uses the same RAM, so it goes nowhere. Multi-GPU FSDP sharding stays available because it genuinely partitions weights instead of parking them in a separate host pool.

**This is the general unified-memory trap**, and it applies to Apple Silicon identically: every offload strategy designed for "VRAM and RAM are separate pools" becomes meaningless on unified memory.

---

## Two GB10-specific handling notes for FastH3

FastH3 is a 4-step sparse-distilled MiniMax-H3 model built with Nuva Lab and NVIDIA's FastGen team, generating **synchronized video and audio**; Preview v1 shipped 2026-08-27.

On a single GB10 it needs two special accommodations:

**One, lazy module load must stay on.** Its Qwen3-VL conditioner is **tens of gigabytes of BF16**. If the DiT and VAEs load while that encoder is still resident, the process gets an `earlyoom` kill (Python is the usual victim). On unified memory `lazy_module_load` auto-enables and owns the split — encoder, then DiT, then VAE, with the DiT able to drop before decode. The docs warn explicitly: **do not pass `--no-lazy-module-load`**.

**Two, the TAEH3 preview decoder is dramatic.** With `--video-decode-backend taeh3`:

| | Full VAE | TAEH3 |
|---|---:|---:|
| 768×1344×124 decode | **68 s** | **2.4 s** |

**28×.** One T2VA generation finishes end-to-end in **224 seconds**. The cost: reconstruction is approximate, not lossless, and FL2VA/Ref2VA still need the full VAE to encode references.

Given that few-step generation is decode-bound to begin with, compressing 68 seconds of decode into 2.4 essentially removes that bottleneck entirely.

---

## Two Sparks chained: 1.3×, not 2×

The "generated on two DGX Sparks" claim is real, and the docs give numbers.

Sequence parallel (`sp_size=2`) over the QSFP RoCE link:

| Task | One GB10 | Two GB10 | Speedup |
|---|---:|---:|---:|
| 768×1344×124 FastH3 | 374–393 s | **292 s** | about **1.3×** |
| 345-frame (~14.4 s) clip | — | 587 s | — |

**Two machines buy 1.3×**, not 2×. And **weights stay replicated** rather than sharded, so lazy module load remains required on each box.

An honest number, and a telling one: distributed inference scales well below linearly in machine count, especially when interconnect bandwidth and single-node memory bandwidth sit in the same order of magnitude.

---

## The Apple Silicon path: more relevant to most readers

For this site's readers, a DGX Spark is a machine you may or may not buy; **Apple Silicon is already on your desk.**

On 2026-09-01 FastVideo also released MLX builds of FastH3 — **pre-converted, ready to run**:

| Variant | Weight size | Notes |
|---|---:|---|
| `...-Dense-DataFree-MLX-INT4` | **10.74 GiB** | affine, weight-only INT4, group size 64, activations stay BF16 |
| `...-Dense-DataFree-MLX-INT8` | — | same, 8-bit |

The limitation up front: **this export is dense-only and does not support `--vsa`** (video sparse attention).

**Its provenance file is unusually rigorous.** From `conversion_manifest.json`:

- Conversion hardware: **Apple M4 Max**, **36 GB** unified memory
- Conversion time: 46.1 s for one format, **164.62 s** for all three combined
- Peak MLX memory **14.8 GiB**, process peak RSS 11.3 GB, peak memory footprint 27.1 GB
- MLX 0.32.2, Python 3.12.13
- Validation: all 13 source transformer shards verified, 1,464 tensors checked, and a full **124-frame 832×480** generation completed with the full H3 VAE
- Weight SHA-256 published in full

The run commands are complete too:

```bash
# Shared components first (tokenizer, Qwen3-VL text encoder, video VAE, audio VAE)
hf download FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree \
  --revision f624f08c6c279ab43534c003e556fc5b295b6558 \
  --local-dir ./FastH3-Preview-v1-Dense-DataFree

# Then the converted MLX INT4 DiT
hf download FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree-MLX-INT4 \
  --local-dir ./FastH3-MLX-INT4

# Install and generate
uv venv --python 3.12 --seed && source .venv/bin/activate
uv pip install -e ".[mlx]"

python examples/inference/basic/mlx_fasth3.py \
  --model-root ./FastH3-Preview-v1-Dense-DataFree \
  --mlx-checkpoint ./FastH3-MLX-INT4 \
  --prompt '(S1) A presenter says <d>[English] Fast H3 runs on Apple silicon.</d>' \
  --height 480 --width 832 --num-frames 124 --steps 4 --seed 2026 \
  --output-path ./outputs/fasth3_int4.mp4
```

The docs note the MLX runtime **loads one heavyweight component at a time** — the same idea as lazy loading on the GB10, because the unified-memory constraint is the same.

**License caution**: this model is not under an open-source license. It ships under the MiniMax H3 Community License (`license: other`), and converted checkpoints inherit it. That is separate from FastVideo's own Apache-2.0.

---

## Three takeaways worth keeping

**One, measure the bottleneck before optimizing.** Few-step generation on the GB10 is decode-bound, so optimizing attention is pointless; past four steps it becomes denoise-bound and the conclusion inverts. Tuning without knowing your bottleneck is gambling.

**Two, unified memory invalidates an entire class of optimization.** CPU offload, VRAM/RAM tiering, and every trick assuming "GPU memory and host memory are two pools" go nowhere on the GB10 and on Apple Silicon. The binding constraint on these machines is **bandwidth**, not capacity.

**Three, "does this optimization help on my hardware" must be measured.** FlashAttention is standard practice on datacenter GPUs and buys nothing on `sm_121`; linear-layer quantization helps in many settings and is 1% noise on long-sequence video models. **There are no universally effective optimizations, only optimizations paired to hardware.**

---

## Gaps: I have no DGX Spark, and have not run the MLX path yet

Stated plainly:

1. **No DGX Spark.** The 40 s / 12 min / 47 min figures, 292 s versus 374–393 s for two boxes, and TAEH3's 2.4 s versus 68 s all come from FastVideo's documentation; I reproduced none of them.
2. **I have not run the Apple Silicon MLX path.** It is **the only locally verifiable part of this post** — it needs a Mac with enough memory (conversion was done on a 36GB M4 Max; INT4 weights are 10.74 GiB, and with the text encoder and VAEs, 32GB+ looks like the safe floor). That is the obvious next experiment.
3. **FastH3 generation quality is unverified.** Four-step distillation plus INT4 quantization plus dense-only (no VSA) stacks three sources of degradation; only running it will show the result.
4. **The two-Spark 1.3× is a single configuration**; scaling across other resolutions and frame counts is unknown.

---

## In one line

The document's real value is not "a DGX Spark can do video generation" but **its honest inventory of what is wasted effort on this machine** — FlashAttention, torch.compile, linear-layer quantization: three community-default moves, all failing on the GB10, each with a stated reason.

For the large majority who will never buy a DGX Spark, the transferable part is the method: **measure the bottleneck before optimizing, and accept that optimizations are paired to hardware — there is no universal optimum.**

Incidentally, the Apple Silicon path is available to try right now: 4 steps, 124 frames, 832×480, INT4, 10.74 GiB of weights, commands above.

> 📌 FastVideo: https://github.com/hao-ai-lab/FastVideo
> DGX Spark performance guide: https://github.com/hao-ai-lab/FastVideo/blob/main/docs/getting_started/installation/spark_performance.md
> Pairing two Sparks: https://github.com/hao-ai-lab/FastVideo/blob/main/docs/getting_started/installation/spark_pair.md
> FastH3 MLX INT4 weights: https://huggingface.co/FastVideo/FastVideo-FastH3-4-step-Preview-v1-Dense-DataFree-MLX-INT4
> FastH3 recommended weights (VSA / DataFree): https://huggingface.co/FastVideo/FastVideo-FastH3-4-step-Preview-v1-VSA-DataFree
> VSA paper: https://arxiv.org/pdf/2505.13389

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
