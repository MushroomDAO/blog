---
title: "ComfyUI-MiniMax-H3-W4A4-VSA：RTX 4070 12GB 跑 MiniMax H3 视频生成的量化部署方案"
titleEn: "ComfyUI-MiniMax-H3-W4A4-VSA: Running MiniMax H3 Video Generation on RTX 4070 12GB with W4A4 + Streaming VSA"
description: "sepiablue-ai 开源，GPL-3.0，46 stars。两个 ComfyUI 节点把 MiniMax H3 视频生成塞进 12GB 消费级 GPU：W4A4 量化（FC1 层 ConvRot 预转换缓存）+ 流式 VSA 稀疏注意力（FastH3 官方 gate 文件）。RTX 4070 12GB 实测：832×1408×124帧约 3m29s，峰值 11.5GB 显存，比 INT8 基线快约 11%。需 Ampere/Ada 架构（SM8x），不支持 Hopper/Blackwell，系统内存需约 49GB。"
descriptionEn: "sepiablue-ai, GPL-3.0, 46 stars. Two ComfyUI nodes bringing MiniMax H3 video generation to 12GB consumer GPUs: W4A4 quantization (FC1-only ConvRot preconverted cache) + streaming VSA sparse attention (FastH3 official gate). RTX 4070 12GB benchmark: 832×1408×124 frames in ~3m 29s, 11.5 GB VRAM peak, ~11% faster than INT8 baseline. Requires Ampere/Ada (SM8x) — Hopper and Blackwell are unsupported. System RAM ~49 GB required."
pubDate: 2026-09-21
heroImage: "../../assets/images/comfyui-minimax-h3-w4a4-vsa-rtx-4070-deploy-banner.jpg"
category: "Tech-Experiment"
tags: ["video-generation", "quantization", "comfyui", "minimax", "local-ai", "consumer-gpu"]
lang: zh-CN
---

MiniMax H3 原生 INT8 精度在数据中心 GPU 上已经比较重，消费级显卡更难直接跑。[sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA](https://github.com/sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA) 把两件事组合起来：把 FC1 层压到 W4A4 精度（权重+激活都是 4-bit），同时接入来自 FastH3 官方工作的 VSA 稀疏注意力 gate 文件，让 RTX 4070 12GB 能够在 3m29s 内生成 832×1408 分辨率的 124 帧视频。

**GitHub**：github.com/sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA | **License**：GPL-3.0 | **Stars**：46 | **配套工作流**：github.com/sepiablue-ai/minimax_h3_workflows

---

## 两个优化是什么

### 1. W4A4 量化（FC1 层 ConvRot）

**W4A4 = Weight 4-bit + Activation 4-bit**，采用 **Plain ConvRot** 旋转量化方式，仅应用于 Transformer 中的 FC1 前馈层。FC2 层保持 INT8 精度（部分量化）。

关键实现细节：

- **预转换缓存（v2）**：W4A4 FC1 权重分片预先转换成磁盘缓存格式（约 3.86 GB），避免每次启动时的运行时转换（运行时转换额外消耗约 30% 时间）
- **原生 INT4 GEMM**：利用 Ampere/Ada（SM8x）GPU 的 INT4 矩阵乘法原语执行，不是软件模拟
- **硬件绑定**：SM8x 专属，Hopper（SM9x）和 Blackwell（SM10x）不支持

这些 W4A4 分片缓存是通过 `setup.bat` 脚本从 MATLOWAI/minimax-h3-fused-turbo-int8-convrot 基础 checkpoint 本地生成的，不是单独下载的预制量化权重。

### 2. 流式 VSA 稀疏注意力

**VSA（Visual/Vector Sparse Attention）**：从一个预计算的 CPU 端 gate 张量中读取每步应该保留哪些注意力 token，实现稀疏化。

关键参数：
- `keep_percent`（默认 5%）：保留多少比例的非前缀 token 进行全注意力计算
- **保护区**：文本编码器 token 和参考图像 token 始终做密集注意力，不参与稀疏化
- gate 文件（`fasth3_vsa_gate.safetensors`，约 1.93 GB）来自 FastH3 VSA 蒸馏工作

这与我们此前介绍的 MiniMax H3 加速五件套中的 FastH3 是**直接血缘关系**——FastH3 在数据中心做 VSA 蒸馏产生的 gate 文件，被 sepiablue-ai 包装成流式 CPU↔GPU 加载器，下放到 12GB 消费级显卡。

---

## 两个 ComfyUI 节点

| 节点 | 功能 |
|------|------|
| `H3V2PreconvertedLoader` | 从磁盘加载预转换的 W4A4 FC1 权重分片到推理流水线 |
| `H3V2StreamingVSAPatch` | 将稀疏注意力 mask 接入注意力计算；管理 Gate 张量 CPU↔GPU 流式传输 |

---

## 硬件门槛

| 条件 | 要求 |
|------|------|
| GPU | RTX 4070 12GB（最低），**SM8x Ampere/Ada 架构** |
| 不支持 | **Hopper（H100）、Blackwell（RTX 50系）不支持** |
| 系统内存 | 约 **49 GB RAM**（推理期间峰值） |
| 磁盘空间 | 约 5.8 GB（W4A4 FC1 缓存 3.86 GB + Gate 1.93 GB） |
| ComfyUI | v0.36.0+（原生 INT4 量化 API） |
| 操作系统 | Windows 主要支持，Linux 未经测试 |

---

## 实测基准（RTX 4070 12GB）

分辨率：**832×1408，124 帧，24fps，4 步**

| 指标 | 数值 |
|------|------|
| 总时间 | **209.2 秒（约 3m 29s）** |
| 峰值显存 | **11,479 MiB（~11.5 GB）** |
| 峰值系统内存 | 11,610 MiB |
| 平均每步时间（步骤 2–4） | ~22.6 秒/步 |
| vs INT8 基线 | 约 **+11% 更快** |
| vs 运行时转换 W4A4 | 约 **+30% 更快**（得益于预转换缓存） |

注意：这里的 11% 加速是与 INT8 ConvRot 基线的比较，没有披露是否有质量损失。

---

## 模型权重来源

需要从多个地方分别下载，没有一键安装：

| 组件 | 来源 |
|------|------|
| 扩散模型基础（INT8 ConvRot） | huggingface.co/MATLOWAI/minimax-h3-fused-turbo-int8-convrot |
| VSA Gate 文件 | huggingface.co/barelymining/ComfyUI-MiniMax-H3-FastVideo |
| 文本编码器 | huggingface.co/Comfy-Org/MiniMax-H3 |
| 视频 VAE | huggingface.co/Kijai/MiniMax-H3-experimental |
| 音频 VAE | huggingface.co/Comfy-Org/MiniMax-H3 |

W4A4 FC1 分片缓存由本地 `setup.bat` 脚本从 MATLOWAI 基础 checkpoint 生成，不是单独下载。

---

## 安装步骤

```bash
# 1. 进入 ComfyUI 的 custom_nodes 目录
cd ComfyUI/custom_nodes

# 2. 克隆插件
git clone https://github.com/sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA
cd ComfyUI-MiniMax-H3-W4A4-VSA

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载所需权重（按上表逐个下载到对应 ComfyUI 目录）
# 扩散模型 → ComfyUI/models/diffusion_models/
# Gate 文件 → ComfyUI/models/loras/ 或插件指定路径
# 文本编码器 → ComfyUI/models/text_encoders/
# VAE → ComfyUI/models/vae/

# 5. 生成 W4A4 FC1 预转换缓存（Windows，首次运行）
setup.bat
# 约生成 3.86 GB 缓存到 models/diffusion_models/h3v2_w4a4_cache/
```

---

## 工作流使用

`sepiablue-ai/minimax_h3_workflows` 仓库包含 9 个工作流变体：

| 工作流 | 说明 |
|--------|------|
| FL2VA | 全身参考图 → 视频 |
| Ref2VA | 参考图像 → 视频 |
| VideoRef | 视频参考 |
| Pose Control | 姿态控制生成 |
| **FastH3 VSA** | VSA 稀疏注意力标准流程 |
| **FastH3 FHD Optimal** | 约 3m55s，0 共享内存溢出 |
| 720p Fast | 720p 快速生成 |
| 720p→2x 超分 | 720p 生成后 2x 放大 |
| 1024×1792 极速 | 极速模式 |

ComfyUI 加载方式：`H3V2PreconvertedLoader` 节点代替标准扩散模型加载器；`H3V2StreamingVSAPatch` 节点接在 Model 输出后面。

---

## 与 FastH3 官方工作的关系

2026-09-15 我们介绍的 MiniMax H3 加速五件套中，FastH3 是在数据中心（8×B300）上通过 VSA 稀疏蒸馏实现 15s→6.6s 的加速。sepiablue-ai 的工作是：

- 取 FastH3 VSA 蒸馏产生的 gate 文件，用流式 CPU↔GPU 方式适配到 12GB 消费级 GPU
- 叠加 W4A4 FC1 量化进一步压缩显存
- 把两者打包成 ComfyUI 节点，降低部署门槛

Sol-H3（推理时动态稀疏，无预计算 gate）是另一条技术路线，不是这个仓库所用的方案。

---

## 不足之处

**1. 仅 FC1 层量化**：FC2 层保持 INT8，这是部分量化，不是全模型 W4A4。实际压缩比和速度提升因此有限（仅 +11% vs INT8 基线）。

**2. SM8x 架构锁定**：Hopper（H100、A100 有些也不支持）和 Blackwell（RTX 50 系）明确不支持。现有 RTX 4070/4080/4090 用户没问题，但新购 RTX 5000 系用户需要等。

**3. 49 GB 系统内存**：12GB 显存够，但系统内存需要约 49GB——大多数消费级电脑内存不足，这是比显存更隐蔽的门槛。

**4. VSA 稀疏化质量未评估**：`keep_percent=5%` 意味着 95% 的非前缀 token 注意力被稀疏掉。官方没有提供 FVD/FID 等质量对比，用户需要自己判断视频质量是否可接受。

**5. 静默降级**：参数不兼容时 VSA 会静默回退到密集注意力（需要开 `verbose=True` 才会提示）。

**6. Windows 主要支持**：Linux 未经测试，setup 脚本是 `.bat`。

**7. 多源权重**：需要从 5 个不同 HuggingFace 仓库分别下载，没有统一的安装脚本，对新手不友好。

---

## 怎么看这件事

这个项目解决了一个实际问题：FastH3 VSA 的 gate 文件是公开的，但让它在 12GB 消费级 GPU 上真正跑起来需要额外的工程工作（流式 CPU↔GPU、W4A4 FC1 量化、预转换缓存）。sepiablue-ai 做了这部分脏活，并且打包成了 ComfyUI 节点。

对于有 RTX 4070/4080/4090 + 48GB+ 系统内存的用户，这是目前门槛最低的 MiniMax H3 消费级部署方案之一。11% 的速度提升相对有限，更大的价值在于把峰值显存压到 11.5GB，让 12GB 卡能全程不溢出。

质量方面需要自行验证——5% keep_percent 的稀疏化幅度相当大，官方没有提供量化质量数据，应用于实际项目前需要人工比对。

> 代码仅供学习研究，请遵守 GPL-3.0 协议。使用前请确认 MiniMax H3 模型权重的各自许可证要求。

---

<!--EN-->

## ComfyUI-MiniMax-H3-W4A4-VSA

[sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA](https://github.com/sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA) is a two-node ComfyUI plugin that combines two optimizations to bring MiniMax H3 video generation to 12 GB consumer GPUs: W4A4 quantization on FC1 layers via preconverted ConvRot shards, and streaming VSA sparse attention using the FastH3 official gate file. RTX 4070 12GB benchmark: 832×1408, 124 frames in ~3m 29s, 11.5 GB VRAM peak, ~11% faster than INT8 baseline.

**GitHub**: github.com/sepiablue-ai/ComfyUI-MiniMax-H3-W4A4-VSA | **License**: GPL-3.0 | **Stars**: 46

---

### Two Optimizations

**W4A4 (FC1 only, ConvRot)**: Weight 4-bit + Activation 4-bit via rotation-based quantization, applied to FC1 feedforward layers only (FC2 stays INT8). Version 2 uses preconverted cached shards (~3.86 GB) to avoid ~30% runtime conversion overhead. Requires native INT4 GEMM on Ampere/Ada (SM8x) — Hopper and Blackwell are **not supported**.

**Streaming VSA sparse attention**: A CPU-resident gate tensor (from FastH3's VSA distillation, `fasth3_vsa_gate.safetensors`, ~1.93 GB) determines which non-prefix tokens get sparsified each step. `keep_percent=5%` default — 95% of non-prefix tokens skip full attention. Protected prefix regions (text encoder + reference image tokens) always use dense attention.

---

### Hardware Requirements

- **GPU**: RTX 4070 12 GB minimum; **Ampere/Ada (SM8x) only** — Hopper/Blackwell unsupported
- **System RAM**: ~49 GB peak
- **Storage**: ~5.8 GB (W4A4 cache + Gate file)
- **ComfyUI**: v0.36.0+
- **OS**: Windows primary; Linux untested

---

### Two ComfyUI Nodes

| Node | Function |
|------|----------|
| `H3V2PreconvertedLoader` | Loads preconverted W4A4 FC1 weight shards into the inference pipeline |
| `H3V2StreamingVSAPatch` | Patches attention with the streaming sparse mask; manages Gate tensor CPU↔GPU streaming |

---

### RTX 4070 Benchmark (832×1408, 124 frames, 4 steps)

| Metric | Value |
|--------|-------|
| Total time | 209.2 s (~3m 29s) |
| Peak VRAM | 11,479 MiB |
| Peak system RAM | 11,610 MiB |
| vs INT8 baseline | ~11% faster |
| vs runtime-converted W4A4 | ~30% faster |

No quality metrics published.

---

### Relation to FastH3 (MiniMax H3 acceleration five-pack)

FastH3's VSA distillation produced the gate file used here (`fasth3_vsa_gate.safetensors`). sepiablue-ai's contribution is the streaming CPU↔GPU loader + W4A4 FC1 stacking + ComfyUI node packaging, targeting consumer GPUs that can't run the full INT8 model without VRAM spill. FastH3's own published numbers (8×B300, 15s→6.6s) are datacenter benchmarks; this project brings the same VSA technique to a single 12 GB consumer card.

---

### Limitations

1. **Partial quantization** — FC2 stays INT8; only FC1 is W4A4. Speedup limited to ~11%.
2. **SM8x architecture only** — RTX 50xx (Blackwell) and H100 (Hopper) unsupported.
3. **49 GB system RAM** — harder to meet than the 12 GB VRAM requirement for many consumer setups.
4. **No quality evaluation** — 5% keep_percent is aggressive sparsification; no FVD/FID comparison published.
5. **Silent VSA fallback** — incompatible parameters silently revert to dense attention; need `verbose=True` to detect.
6. **Multi-source weights** — five separate HuggingFace repos, no unified installer.
7. **Windows primary** — Linux untested.

---

### Bottom Line

This project does useful engineering work: it takes FastH3's publicly available VSA gate file and makes it actually run on a 12 GB consumer GPU through streaming CPU↔GPU offload + W4A4 FC1 preconversion + ComfyUI nodes. For RTX 4070/4080/4090 users with 48+ GB system RAM, this is one of the lower-barrier paths to running MiniMax H3 locally. The 11% speed improvement over INT8 baseline is modest; the main value is keeping VRAM peak under 11.5 GB so a 12 GB card can run without spilling. Verify output quality at the default 5% keep_percent before using in production.

> Code for research and learning only. Please comply with GPL-3.0 and the individual license terms of each model weight used.
