---
title: "MiniMax H3 开源实测：ComfyUI 三分钟上手，工程部署完全指南"
titleEn: "MiniMax H3 Hands-On: Three Minutes to ComfyUI, Plus a Complete Deployment Guide"
description: "MiniMax H3 于 2026-07-31 开源，是目前最强的开源视频生成模型之一：33B Omni Transformer，视频+原生立体声同步生成，支持 2K 分辨率、最长 15 秒、11 种语言。本文覆盖能力分析、硬件配置清单（消费卡/数据中心/Apple Silicon）、ComfyUI 快速上手、SGLang 生产部署和工程最佳实践。"
descriptionEn: "MiniMax H3 (open-sourced 2026-07-31) is one of the strongest open-source video generation models: 33B Omni Transformer, synchronized native stereo audio, up to 2K resolution and 15 seconds. This guide covers capabilities, hardware requirements (consumer GPU / data center / Apple Silicon), ComfyUI quickstart, SGLang production deployment, and engineering best practices."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["视频生成", "MiniMax H3", "ComfyUI", "开源模型", "AI工程", "SGLang", "多模态", "Mycelium"]
heroImage: "../../assets/images/minimax-h3-comfyui-open-source-video-generation-engineering-guide-banner.jpg"
---

*by Mycelium Protocol*

---

2026-07-31，MiniMax 把 H3 的核心权重开源了。

H3 不是普通的视频生成模型——它是一个 **全模态（Omni-modal）生成系统**：在单次推理里同时生成视频和同步立体声音频，对话、音效、背景音乐共享同一个前向传播，而不是后处理叠加。最高 2K 分辨率，最长 15 秒，支持 11 种语言，原生支持图像参考、视频参考、音频参考混合输入。

它是开源视频生成方向目前已知参数规模最大的模型（33B），也是第一个把视频和音频放在同一个 Transformer 里联合生成的主流开源模型。这周 ComfyUI 也已原生集成。

本文：能力分析 → 硬件配置清单 → 快速上手 → 工程部署 → 最佳实践。

---

## 系统架构：三个模块

H3 完整系统由三个模块构成，目前开源状态如下：

| 模块 | 功能 | 开源状态 |
|------|------|---------|
| **H3-Context-IR** | 把自由形态多模态输入解析成结构化中间表示 | ❌ 未开源（提供 API） |
| **H3-Base** | 生成 768p 视频 + 立体声音频 | ✅ **已开源** |
| **H3-Regenerate-2K** | 把 768p 结果再生成为 2K | ❌ 未开源（提供 API） |

**开源的核心是 H3-Base**，包含两个任务检查点：

| 检查点 | 任务 | 输入说明 |
|--------|------|---------|
| **FL2VA** | 文生视频（T2V）、首/尾帧视频（I2V） | 文本 + 可选首帧/尾帧/两帧 |
| **Ref2VA** | 全参考视频（R2V）| 文本 + 图像≤9 / 视频≤3 / 音频≤3，总文件≤12 |

两个检查点权重**字节完全相同**（仅 pipeline 元数据不同），本质上是 144 GB 的权重发布了两次。

---

## 核心能力

### 输出规格

| 参数 | 规格 |
|------|------|
| 输出时长 | 4–15 秒 |
| 分辨率 | 768px 短边（本地）/ 2K（需 API） |
| 帧率 | 24 FPS |
| 音频 | 32 kHz 立体声 AAC |
| 宽高比 | 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16 |
| 支持语言 | 中英日韩法德西葡俄阿意，共 11 种 |

### 三种生成模式

**1. 文生视频（T2V）**

输入文本描述，直接生成有声视频。H3 对复杂多镜头提示有较强的遵循能力——可以在一个 prompt 里描述不同时间点的镜头切换、运镜方式和音频内容（台词/音效/配乐），系统会按时序生成。

**2. 图生视频（I2V）/ 首尾帧控制（FL2VA）**

- 只传首帧 → 从给定画面出发生成后续
- 只传尾帧 → 生成过渡到给定结尾
- 同时传首尾帧 → 生成首尾之间的过渡内容

**3. 全参考模式（R2V / Ref2VA）**

这是 H3 最有特色的能力。同时接受图像、视频片段、音频片段作为参考，用自然语言描述每个参考的角色：

```
<Picture 1> 是主角的外貌参考
<Video 1>   提供镜头运动风格
<Audio 1>   是声音音色参考
```

最多 9 张图 + 3 段视频 + 3 段音频，混合输入后生成一致的新内容。实际可用场景：
- 把静态人物照片驱动成说话的视频（口型同步）
- 把自己的声音移植到生成视频的角色
- 参考某段视频的运镜方式和情绪风格，生成新场景

### 架构要点

H3-Omni-Transformer 是 **33B 参数的 Dense 单流 Transformer**：

- 文本、图像、视频、音频被各自编码后拼接成一个统一序列，用同一套注意力机制联合处理
- 文本编码器是 Qwen3-VL-32B（取第 50 层 hidden state，非最后一层）
- 视频 VAE：16× 空间压缩 + 4× 时间压缩，24 通道
- 音频 VAE：32 kHz，40 Hz 潜码率，左右声道共享编解码器独立处理后重组
- AdaLN 约 13B 参数，推理时可预计算缓存后卸载，实际主路径只需约 20B 常驻

---

## 硬件配置清单

这是整篇文章最重要的部分。H3 是迄今为止对显存要求最高的开源视频模型。

### 完整模型显存构成

| 组件 | BF16 体积 |
|------|----------|
| H3-Omni-Transformer（主路径，AdaLN 缓存后） | ~40 GB |
| Qwen3-VL 文本/视觉编码器（第 50 层） | 50.3 GB |
| 视频 VAE | ~10 GB |
| 音频 VAE | ~0.6 GB |
| **合计（推理常驻）** | **~102 GB** |

不做任何优化，全精度推理需要约 **102 GB** 显存/统一内存。

---

### 方案一：消费级 GPU（本地入门）

**最低可运行配置：1× RTX 5090（32 GB）**

需要 layerwise offload（逐层换入换出），生成 5 秒 768p 视频约 **8–10 分钟**。

| 配置 | 说明 |
|------|------|
| GPU | 1× RTX 5090（32 GB VRAM） |
| 主机内存 | ≥ 64 GB DDR5 |
| 磁盘 | ≥ 300 GB NVMe SSD |
| 框架 | ComfyUI 0.30.0+（内置 Blackwell nvfp4_awq 量化） |
| 生成速度 | 5 秒视频约 8–10 分钟 |

**推荐本地配置：2× RTX 5090**

SGLang 张量并行，生成 5 秒 768p 视频约 **9 分钟**（vs 单卡的 1/2 时间）。

```bash
sglang serve \
  --model-path MiniMaxAI/MiniMax-H3 \
  --model-variant fl2va \
  --num-gpus 2 --tp-size 2 --ulysses-degree 1 \
  --performance-mode memory \
  --layerwise-offload-components dit,text_encoder,vae \
  --dit-offload-prefetch-size 1 \
  --dit-layerwise-resident-layers 20 \
  --port 30010
```

> 注意：2× RTX 5090 方案建议 **384 GiB 主机内存**，用于层级换入换出的缓冲。

---

### 方案二：数据中心 GPU（生产级）

**最低生产配置：4× H100（80 GB/卡）**

生成 5 秒 1344×768 视频（24fps，50 步）约 **13 秒**。

| 拓扑 | 时延 | 单卡峰值显存 |
|------|------|------------|
| TP2 + Ulysses2（最快） | 13.25 s | 66 GB |
| TP4 + Ulysses1（最省显存） | 13.86 s | 49.8 GB |
| FSDP + Ulysses4 | 13.36 s | 57 GB |

**高吞吐配置：4× H200（140 GB/卡）或 8× B200/B300**

4× H200 可以完整常驻所有组件，无需 offload，理论延迟更低。

8× B300 + FP8 在线量化：

```bash
sglang serve \
  --model-path MiniMaxAI/MiniMax-H3 \
  --model-variant fl2va \
  --num-gpus 8 --ulysses-degree 8 \
  --performance-mode speed \
  --quantization fp8 \
  --port 30010
```

> **注意**：FP8 在线量化目前**仅 B200/B300（Blackwell 数据中心卡）支持**，不适用于 RTX 5090 等消费卡。

**各硬件基准数据汇总**（5 秒 1344×768 / 24fps / 50 步，单请求）：

| 硬件 | 拓扑 | 时延 |
|------|------|------|
| 4× H100 | TP2+Ulysses2 | ~13 s |
| 4× H200 | Ulysses4 全常驻 | ~75 s（lossless） |
| 8× B300 | Ulysses8 BF16 | 19 s |
| 8× B300 | Ulysses8 FP8 | 18 s |
| 8× MI355X | Ulysses8 | 65 s |
| 2× RTX 5090 | TP2 + layerwise offload | ~560 s |

---

### 方案三：Apple Silicon（Mac 本地）

H3 可以在 Apple Silicon Mac 上运行，但有明确的上下限：

| 配置 | 内存 | 状态 |
|------|------|------|
| M3 Ultra 512 GB | 512 GB | ✅ 官方验证，加载 ~134 GB，生成 5 秒约 8.8 分钟/步 |
| M3 Ultra 192 GB | 192 GB | ⚠️ 官方推荐最低，未公开实测时间 |
| M2 Ultra 192 GB 及以下 | <192 GB | ❌ 不推荐 |

Mac 路径有两条：

**路径 A — 官方 Diffusers + MPS（忠实原始权重）**

```bash
git clone https://github.com/HeyZhey/RunH3onMac.git
cd RunH3onMac
./scripts/bootstrap.zsh  # 安装依赖、应用 MPS 补丁
source .venv/bin/activate
python scripts/generate.py "your prompt here"
```

**路径 B — MLX 量化（速度优先，仍然慢）**

社区已发布 MLX 量化版本（pipenetwork/MiniMax-H3-MLX），但需要注意：

| 量化 | 常驻内存 | PSNR vs BF16 |
|------|---------|--------------|
| BF16 | 40.3 GB | 参考基准 |
| 8-bit | 21.5 GB | 27.6 dB（良好） |
| 4-bit | 11.5 GB | 22.0 dB（可用） |
| 3-bit | 不推荐 | 16.3 dB（结构损坏） |

**Mac 上的核心限制**：H3 的瓶颈是注意力 FLOP（稠密全注意力，数万行序列），量化减少线性层计算但不减少注意力计算。5 秒视频在 M3 Ultra 上每步约 8.8 分钟，50 步约 7 小时——这是现实，不是设备问题。

---

## ComfyUI 快速上手

ComfyUI 0.30.0+ 已原生内置 H3 支持，是**消费级用户最快的上手路径**。

### 安装步骤

```bash
# 1. 确保 ComfyUI >= 0.30.0
# 2. 进入 ComfyUI 管理器，更新到最新版本

# 3. 模型文件存放位置
ComfyUI/models/diffusion_models/      # 存放 H3 Transformer 权重
ComfyUI/models/vae/                   # 存放 H3 Video VAE / Audio VAE
ComfyUI/models/text_encoders/         # 存放 Qwen3-VL 文本编码器
```

### 加载工作流

1. 打开 ComfyUI → **Template Library → Video**
2. 选择 MiniMax H3 工作流（T2V / I2V / R2V 三选一）
3. 弹窗会自动提示下载所需模型文件

模型文件托管在 [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)（非官方原始权重仓库，是 Comfy 适配版本）。

### 分辨率设置

每个工作流都有 **Resolution Selector** 节点：

- **Aspect Ratio**：选 16:9 / 9:16 / 1:1 等预设
- **Megapixels**：约 `1.0` → 1344×768（H3 原生画布），更低更快
- **Multiple**：保持 `32`（H3 分辨率网格的要求）

### 加速：SageAttention

可以把生成速度提升约 **2 倍**，质量损耗极小：

```bash
# 1. 安装 sageattention（下载对应 PyTorch + CUDA 版本的 wheel）
pip install sageattention-<version>.whl

# 2. 安装 KJNodes（提供 Patch Sage Attention KJ 节点）
# 在 ComfyUI Manager 中搜索 KJNodes 安装
```

或者启动 ComfyUI 时加全局参数：
```bash
python main.py --use-sage-attention
```

### 三种工作流操作要点

**T2V（文生视频）**：
- 在 prompt 里描述完整场景（位置、角色、事件），然后分镜头描述运镜和音频
- `Duration` 会对齐到 17 帧/block 的网格（24fps 下约 0.7 秒为一个单位）

**I2V（图生视频）**：
- 把图片连接到 `MiniMaxH3ImageToVideo` 节点的 `first_frame` / `last_frame` 输入
- 两个都连 = 首尾帧控制；只连一个 = 单边引导

**R2V（参考驱动）**：
- 使用 `MiniMaxH3ReferenceToVideo` 节点
- 按顺序连接的参考用标签引用：`<Picture 1>`、`<Video 1>`、`<Audio 1>`
- **每个参考必须声明它的作用**（identity / style / motion / camera / voice），否则效果不稳定
- 设置 `ref_image_size=match`（速度优先）或 `max`（身份保真度优先）

---

## SGLang 生产部署

### 安装

```bash
pip install --upgrade pip && pip install uv
uv pip install "sglang[diffusion]" --prerelease=allow
```

### 关键参数速查

| 参数 | 含义 |
|------|------|
| `--model-variant` | `fl2va`（T2V + I2V）或 `ref2va` |
| `--num-gpus` | GPU 数量 |
| `--tp-size` | 张量并行度 |
| `--ulysses-degree` | Ulysses 序列并行（H3 只支持 Ulysses，不支持 Ring） |
| `--performance-mode` | `speed`（全常驻）/ `auto`（120 GiB 阈值）/ `memory`（省显存） |
| `--layerwise-offload-components` | `dit,text_encoder,vae`，分组卸载到 CPU |
| `--dit-layerwise-resident-layers` | DiT 常驻 block 数（消费卡推荐 20） |

### 三条硬性约束

1. **只能用 Ulysses 并行，不能用 Ring 并行**——H3 的 packed multi-segment attention 与 Ring 并行不兼容
2. **`--cfg-parallel-size` 必须为 1**——H3 是 CFG 蒸馏模型，单去噪分支
3. **VAE 只支持 `tile` 模式**——不接受 `spatial` 或 `spatial_shard`

### 发起请求（Python 示例）

```python
import requests, json

payload = {
    "model": "MiniMaxAI/MiniMax-H3",
    "prompt": "A lone wolf stands on a snowy ridge at dusk...",
    "model_variant": "fl2va",
    "duration": 5,
    "ratio": "16:9",
}

# 异步提交
r = requests.post("http://localhost:30010/v1/videos", json=payload)
task_id = r.json()["id"]

# 轮询结果
while True:
    status = requests.get(f"http://localhost:30010/v1/videos/{task_id}")
    if status.json()["status"] == "succeeded":
        video_url = status.json()["result"]["url"]
        break
```

### Cache-DiT 近似加速（4× H200 实测）

同一个 SGLang server 支持请求级质量参数：

| quality | 加速比 | SSIM | 适用场景 |
|---------|--------|------|---------|
| lossless | 1.0× | 1.000 | 生产/存档 |
| high | 1.4× | 0.931 | 预览 |
| medium | 2.5× | 0.818 | 快速测试 |
| low | 2.9× | 0.794 | 创意探索 |

> 注意：Cache-DiT 目前只验证了 5.167s / 1344×768 / 50步 / 4×H200 这个精确配置，其他规格会拒绝请求。

---

## 工程最佳实践

### Prompt 结构（影响质量最大的单一因素）

H3 在使用 **H3-Context-IR** 时会自动把自然语言扩展为结构化表示，但本地部署跳过了这一步。最佳实践：

```
[Shot 1] <时间戳/镜头描述>
[Shot 2] 在 00:05.000，镜头切换到...

overall_soundscape: <整体声音环境>
non_diegetic_music: <配乐风格和情绪>
```

中英文均可，但英文 prompt 通常效果更稳定。官方提供了详细的 [Prompt 写作指南](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)，建议在写复杂提示前先读一遍。

### 分辨率和时长的网格约束

- 短边 768px，最大 768×1344（16:9）
- 时长必须是 17 帧/block 的整数倍（@24fps 约 0.708 秒/block）：4s ≈ 5 blocks（实际 5.167 s），可接受范围 4-15s

### 消费卡显存优化顺序

1. **开 layerwise offload**：把 `text_encoder` 先卸，它是 50.3 GB 的主矛盾
2. **调 resident layers**：`--dit-layerwise-resident-layers` 从 10 开始向上试，找显存和速度的平衡点
3. **用 SageAttention**：约 2× 速度，质量几乎无损
4. **降分辨率**：把 short edge 从 768 降到 512，VRAM 和速度都有明显改善
5. **减步数**：H3 是 CFG 蒸馏，20-30 步通常足够，不必用 50 步

### 两个检查点的选择

| 场景 | 选哪个 |
|------|--------|
| 纯文字生成视频 | FL2VA |
| 首/末帧控制 | FL2VA |
| 视频编辑（参考原视频） | **Ref2VA** |
| 角色一致性（人物参考图） | **Ref2VA** |
| 声音克隆到生成视频 | **Ref2VA** |

运行两个变体需要各启一个 server 进程（共享权重，但 pipeline 元数据不同）。

---

## 许可证

MiniMax H3 使用 **MiniMax H3 Community License Agreement**：

- ✅ 学术研究、个人学习、非商业使用
- ✅ 月活用户 < 100 万的商业产品（需遵守使用限制）
- ⚠️ 月活 > 100 万或特定商业场景需要单独授权
- ❌ 禁止生成用于误导或伤害他人的内容

详细条款见 [HuggingFace 许可证文件](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)。

---

## 资源汇总

| 资源 | 链接 |
|------|------|
| 官方权重（HuggingFace） | [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) |
| ComfyUI 适配权重 | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| ComfyUI 官方教程 | [docs.comfy.org MiniMax H3](https://docs.comfy.org/tutorials/video/minimax/minimax-h3) |
| SGLang 部署指南 | [docs.sglang.io MiniMax-H3](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3) |
| Hailuo AI 在线体验 | [hailuoai.video](https://hailuoai.video/) |
| MiniMax 开放平台 API | [platform.minimax.io](https://platform.minimax.io/) |
| Apple Silicon 运行指南 | [HeyZhey/RunH3onMac](https://github.com/HeyZhey/RunH3onMac) |
| MLX 量化版本 | [PipeNetwork/minimax-h3-mlx](https://github.com/PipeNetwork/minimax-h3-mlx) |
| Prompt 写作指南（官方） | [VIDEO_PROMPT_WRITING_GUIDE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) |

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## MiniMax H3 + ComfyUI: Open-Source Video Generation Engineering Guide

*by Mycelium Protocol*

MiniMax open-sourced H3 on July 31, 2026.

H3 is not a conventional video generation model — it is an **omni-modal generative system**: a single forward pass produces video and synchronized native stereo audio together. Dialogue, sound effects, and background music share the same Transformer, not post-processing. Up to 2K resolution, up to 15 seconds, 11 languages, with native support for mixed image, video, and audio reference inputs.

It is the largest open-source video generation model by parameter count (33B), and the first mainstream open-source model to generate video and audio jointly inside a single Transformer. ComfyUI added native support this week.

This guide: capability breakdown → hardware requirements → ComfyUI quickstart → SGLang production deployment → engineering best practices.

---

### System Architecture: Three Modules

| Module | Function | Open-source status |
|--------|----------|--------------------|
| **H3-Context-IR** | Parses free-form multimodal input into structured intermediate representation | ❌ Hosted API only |
| **H3-Base** | Generates 768p video + stereo audio | ✅ **Open weights** |
| **H3-Regenerate-2K** | Upscales 768p output to 2K via in-context regeneration | ❌ Hosted API only |

Two task checkpoints, **byte-identical weights, different pipeline metadata**:

| Checkpoint | Tasks | Input |
|------------|-------|-------|
| **FL2VA** | T2V, first/last-frame I2V | Text + optional first/last/both frames |
| **Ref2VA** | R2V (multimodal reference) | Text + images ≤9 / videos ≤3 / audio ≤3 |

---

### Key Capabilities

**Text-to-Video (T2V)**: Structured multi-shot prompts with camera movement and timed audio descriptions — one prompt, full scene.

**Image-to-Video / First-Last Frame (FL2VA)**: First frame → generate forward. Last frame → generate backward. Both → generate the transition.

**Reference-to-Video (R2V)**: The standout capability. Mix reference images, video clips, and audio clips. Describe each reference's role in natural language:
- Identity lock: character reference photo
- Motion reference: video clip whose movement to replicate
- Voice cloning: audio clip whose timbre to transfer to generated dialogue

---

### Hardware Requirements

**Total inference footprint (BF16, no optimization): ~102 GB**

| Component | Size |
|-----------|------|
| Omni-Transformer (after AdaLN precompute) | ~40 GB |
| Qwen3-VL text/visual encoder (layers 0–49) | ~50.3 GB |
| Video VAE | ~10 GB |
| Audio VAE | ~0.6 GB |

**Consumer GPU (local)**

- Minimum: 1× RTX 5090 (32 GB) with layerwise offload — 5s video in ~8–10 min
- Recommended: 2× RTX 5090 — halves time; needs ~384 GB host RAM

**Data center GPU (production)**

| Config | Latency | Notes |
|--------|---------|-------|
| 4× H100 (TP2+Ulysses2) | ~13 s | 5s clip, 50 steps |
| 4× H100 (TP4+Ulysses1) | ~14 s | Lower per-GPU VRAM |
| 8× B300 (FP8) | ~18 s | Blackwell FP8 quantization |
| 2× RTX 5090 (layerwise) | ~560 s | Consumer-grade reference |

**Apple Silicon**

- Minimum: 192 GB unified memory (M3 Ultra scale)
- Tested: M3 Ultra 512 GB — 5s video ~8.8 min per denoising step (compute-bound, not memory-bound)
- The bottleneck is attention FLOPs, not VRAM — quantization helps fit the model but doesn't make it fast

---

### ComfyUI Quickstart

ComfyUI 0.30.0+ ships native H3 support.

1. **Update ComfyUI** to 0.30.0 or later
2. **Template Library → Video → MiniMax H3** (T2V / I2V / R2V)
3. Follow the popup to download model files from [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)

**Resolution**: set Megapixels to ~1.0 for 1344×768 (H3 native canvas); lower for faster previews. Keep Multiple at 32.

**2× speed with SageAttention**:
```bash
python main.py --use-sage-attention
```

**R2V prompt structure** — always tag references by order and assign each a role:
```
<Picture 1> provides the subject's identity.
<Audio 1> provides the voice timbre for the subject's dialogue.
Generate a 5-second clip where the subject speaks...
```

---

### SGLang Production Deployment

```bash
pip install uv
uv pip install "sglang[diffusion]" --prerelease=allow
```

4× H100 (fastest lossless):
```bash
sglang serve \
  --model-path MiniMaxAI/MiniMax-H3 \
  --model-variant fl2va \
  --num-gpus 4 --tp-size 2 --ulysses-degree 2 \
  --performance-mode speed --port 30010
```

**Three hard constraints**:
1. Only Ulysses parallelism — Ring is incompatible with H3's packed attention
2. `--cfg-parallel-size 1` only — H3 is CFG-distilled (single denoising branch)
3. VAE only accepts `tile` mode

**Cache-DiT acceleration** (4× H200 only, exact workload):

| quality | speedup | SSIM |
|---------|---------|------|
| lossless | 1.0× | 1.000 |
| high | 1.4× | 0.931 |
| medium | 2.5× | 0.818 |

---

### Engineering Best Practices

**Prompt structure matters most**: Describe shots with timestamps, camera moves, and audio in a single block. Use the official [prompt writing guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) for complex generations.

**Consumer GPU VRAM optimization order**:
1. Enable layerwise offload → offload `text_encoder` first (50.3 GB)
2. Tune `--dit-layerwise-resident-layers` up from 10
3. Add SageAttention (~2× speed)
4. Drop resolution (short edge from 768 to 512)
5. Reduce steps to 20–30 (CFG-distilled, doesn't need 50)

**Checkpoint selection**: Use FL2VA for text/image-to-video; Ref2VA for character consistency, video editing, or voice cloning.

**License**: Community License — non-commercial free; commercial use under 1M MAU allowed with usage restrictions; >1M MAU requires separate authorization.

---

### Resources

| Resource | Link |
|----------|------|
| Official weights | [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) |
| ComfyUI weights | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| ComfyUI tutorial | [docs.comfy.org MiniMax H3](https://docs.comfy.org/tutorials/video/minimax/minimax-h3) |
| SGLang deployment | [docs.sglang.io MiniMax-H3](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3) |
| Hailuo AI app | [hailuoai.video](https://hailuoai.video/) |
| Apple Silicon guide | [HeyZhey/RunH3onMac](https://github.com/HeyZhey/RunH3onMac) |
| MLX quants | [PipeNetwork/minimax-h3-mlx](https://github.com/PipeNetwork/minimax-h3-mlx) |
| Official prompt guide | [VIDEO_PROMPT_WRITING_GUIDE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md) |

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
