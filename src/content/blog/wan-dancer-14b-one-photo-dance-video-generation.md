---
title: "一张照片跳到 160 秒：万相团队开源 Wan-Dancer-14B 本地部署全指南"
titleEn: "One Photo, 160 Seconds of Dance: Wan-Dancer-14B Open Source & Local Deployment Guide"
description: "万相团队开源 Wan-Dancer-14B（arXiv:2607.09581）——输入一张人物照片 + 一段音乐 + 舞种提示，生成 15 秒至 3 分钟、720p/30fps 的连续舞蹈视频，覆盖古典舞、K-Pop、街舞、踢踏舞、拉丁舞五种风格。本文拆解核心技术，并给出从环境搭建到生成首支视频的完整本地部署教程。"
descriptionEn: "Wan-Dancer-14B (arXiv:2607.09581) from the Wanxiang team is now open source. One portrait photo + music + dance style prompt → 15s to 3 minutes of 720p/30fps continuous dance video across five genres. This article breaks down the core technique and provides a complete local deployment guide from environment setup to generating your first video."
pubDate: "2026-07-14"
updatedDate: "2026-07-14"
category: "Tech-Experiment"
tags: ["视频生成", "开源", "AI舞蹈", "本地部署"]
heroImage: "../../assets/images/wan-dancer-14b-one-photo-dance-video-generation-banner.jpg"
---

> 论文：**Wan-Dancer: A Hierarchical Framework for Minute-scale Coherent Music-to-Dance Generation**  
> arXiv：[2607.09581](https://arxiv.org/abs/2607.09581) | 2026 年 7 月 10 日  
> 作者：Mingyang Huang, Peng Zhang, Li Hu, Guangyuan Wang, Bang Zhang  
> GitHub：[Wan-Video/Wan-Dancer](https://github.com/Wan-Video/Wan-Dancer)  
> 模型：[HuggingFace](https://huggingface.co/Wan-AI/Wan-Dancer-14B) | [ModelScope](https://www.modelscope.cn/models/Wan-AI/Wan-Dancer-14B)

---

## 为什么「2 分钟」一直是个坎

AI 视频生成在短片上已经相当成熟，但舞蹈视频有一个极难突破的上限：**大约 20 秒**。超过这个时长，现有扩散模型会暴露三个问题：

1. **时序漂移（Temporal Drift）**：节拍对齐在几秒内还好，越往后越错位
2. **身份不一致（Identity Inconsistency）**：人脸在长视频里逐渐变成另一张脸
3. **动作重复（Repetitive Motion）**：模型在不知道「整首歌」的情况下，只好不断循环几个动作

3D 骨骼中介方案和端到端方案都在这三个问题上折戟。

Wan-Dancer 用一个**分层框架**正面解决这个问题，把 160 秒（接近 3 分钟）稳定生成变为可能。

---

## 核心技术：两阶段分层生成

### 阶段一：全局关键帧规划（Global Stage）

输入：参考人物照片 + 完整音轨 + 舞种 Prompt  
输出：低帧率但全局一致的「骨架视频」

**关键设计：**

- **读入完整音轨**：不是逐段生成，而是先看完整首音乐再规划动作。这保证了第 10 秒和第 90 秒的动作在音乐结构上是相关的，而不是各跳各的。
- **Time-mapped RoPE Embedding**：动态帧率适配。不同舞种的节拍密度不同（踢踏舞 vs 古典舞），通过对旋转位置编码的重映射，精确对齐音频节拍和视频帧。

### 阶段二：局部时序精修（Local Stage）

输入：全局视频 + 原始参考图 + 高分辨率 Prompt  
输出：720p/30fps 高清舞蹈视频

**关键设计：**

- **光流损失函数（Optical-Flow Loss）**：在相邻帧之间施加光流一致性约束，让动作在帧与帧之间自然过渡，不出现跳帧或抖动
- **运动速度控制（Motion-Speed Control）**：快速动作（如旋转、跳跃）期间自动调整生成策略，保留高保真细节而不糊成一片

```
参考照片 + 音乐 + 舞种
         ↓
  [Stage 1] 全局关键帧规划（num_steps=48）
         ↓ 全局骨架视频
  [Stage 2] 局部时序精修（num_steps=24）
         ↓
  720p/30fps 高清舞蹈视频（15s ～ 3min）
```

---

## 支持的五种舞风

| 风格 | Prompt 文件前缀 | 音乐建议 |
|------|----------------|---------|
| 🎋 中国古典舞 | `古典舞_` | 古风乐器 |
| 🎤 K-Pop | `kpop_` | 韩流流行 |
| 🕺 街舞 | `街舞_` | 嘻哈/Breaking |
| 👠 踢踏舞 | `踢踏舞_` | 爵士/百老汇 |
| 💃 拉丁舞 | `拉丁舞_` | Salsa/Rumba |

---

## 本地部署指南

> ⚠️ **硬件要求说明（重要）**  
> 官方测试环境：**8 × NVIDIA A800 80GB**，即 640GB 显存。这是大规模推理的工业配置。  
> 个人/小团队推荐路径：**4 × A100 80GB 或 云 GPU（RunPod / Lambda Labs）**。  
> 如果只有消费级显卡（RTX 4090），目前暂无官方量化版，建议先在 [ModelScope Space](https://modelscope.ai/studios/Wan-AI/Wan-Dancer) 上体验 Demo。

---

### 方式一：云 GPU（推荐新手）

RunPod 已有社区整合好的 Docker 环境，可一键启动：

```bash
# 参考：grawthings-beep/wan-dance-runpod
# 在 RunPod 控制台选择带 80GB 显存的 A100/H100 实例
# 使用 runpod/pytorch:2.6.0-py3.10-cuda12.4.1-devel 基础镜像
```

Lambda Labs 也支持按小时租用 A100/H100，配合下面的安装步骤即可。

---

### 方式二：本地/自托管服务器

#### Step 1：克隆仓库 + 下载模型

```bash
git clone https://github.com/Wan-Video/Wan-Dancer.git
cd Wan-Dancer

# 从 HuggingFace 下载模型
# 建议使用 huggingface-cli 或 hf_transfer 加速
pip install huggingface_hub
huggingface-cli download Wan-AI/Wan-Dancer-14B --local-dir ./models/Wan-Dancer-14B

# 或 ModelScope（国内网络更快）
pip install modelscope
modelscope download Wan-AI/Wan-Dancer-14B
```

#### Step 2：创建虚拟环境 + 安装依赖

```bash
python -m venv venv_wan_dancer
source venv_wan_dancer/bin/activate

# 安装主包（editable 模式）
pip install -e .

# 安装附加依赖
pip install moviepy loguru librosa

# 安装 PyTorch（CUDA 12.4，阿里镜像加速）
pip install https://mirrors.aliyun.com/pytorch-wheels/cu124/torch-2.6.0+cu124-cp310-cp310-linux_x86_64.whl
pip install torchvision==0.21.0

# 安装核心依赖（版本严格对齐）
pip install diffusers==0.34.0
pip install yunchang==0.5.0
pip install flash_attn==2.6.3
pip install xfuser==0.4.0
pip install transformers==4.46.2
```

> 💡 确认 CUDA 版本：`nvcc --version` 应显示 12.4.x

#### Step 3：准备输入文件

```
Wan-Dancer/
├── gen_video/
│   ├── ref_image/
│   │   └── your_photo.jpg     ← 放你的参考人物照片（建议全身正面，背景简洁）
│   ├── music/
│   │   └── your_music.wav     ← 放音乐文件（WAV 格式）
│   └── prompt/
│       ├── 古典舞_global.txt   ← 内置 prompt，直接用
│       ├── kpop_global.txt
│       ├── 街舞_global.txt
│       ├── 踢踏舞_global.txt
│       └── 拉丁舞_global.txt
```

**参考图建议：**
- 格式：JPG / PNG
- 构图：全身或半身，正面或侧面均可
- 背景：简洁背景效果更好
- 分辨率：720p 以上

#### Step 4：生成全局关键帧视频

编辑 `gen_video_global.sh`，修改以下参数：

```bash
python gen_video_global.py \
  --seed 0 \
  --image_path "gen_video/ref_image/your_photo.jpg" \
  --prompt_path "gen_video/prompt/古典舞_global.txt" \
  --music_path "gen_video/music/your_music.wav" \
  --output_folder "outputs/global_video" \
  --num_inference_steps 48 \
  --cfg_scale 5
```

然后运行：

```bash
./gen_video_global.sh
```

> ⏱️ 预计耗时：8×A800 约 20-30 分钟（取决于视频时长）

#### Step 5：局部精修生成最终视频

编辑 `gen_video_local.sh`，加入 Step 4 生成的全局视频路径：

```bash
python gen_video_local.py \
  --seed 0 \
  --image_path "gen_video/ref_image/your_photo.jpg" \
  --prompt_path "gen_video/prompt/古典舞_local.txt" \
  --music_path "gen_video/music/your_music.wav" \
  --global_video_path "outputs/global_video/your_photo_music_seed0.mp4" \
  --output_folder "outputs/final_video" \
  --num_inference_steps 24 \
  --cfg_scale 5
```

运行：

```bash
./gen_video_local.sh
```

> 💡 生成更长视频（超过 60 秒）时，`num_inference_steps` 建议增大到 48。

---

## 五种风格的示例配置

| 风格 | image_path | prompt_path | music_path |
|------|-----------|-------------|------------|
| 古典舞 | `ref_image/1001.jpg` | `古典舞_global.txt` | `ChineseClassicDance.WAV` |
| 街舞 | `ref_image/2001.jpg` | `街舞_global.txt` | `StreetDance.WAV` |
| K-Pop | `ref_image/3001.jpg` | `kpop_global.txt` | `music_suno/3001.WAV` |
| 拉丁舞 | `ref_image/4001.jpg` | `拉丁舞_global.txt` | `LatinDance.WAV` |
| 踢踏舞 | `ref_image/5001.jpg` | `踢踏舞_global.txt` | `TapDance.wav` |

内置示例图片和音乐随仓库一起提供，可以先用官方素材跑通流程，再换成自己的。

---

## 关键参数说明

| 参数 | 推荐值 | 说明 |
|---|---|---|
| `num_inference_steps` | 48（全局）/ 24（局部） | 步数越多质量越高，但更慢；长视频适当加大 |
| `cfg_scale` | 5 | 对 Prompt 的遵循程度，5 是经验值 |
| `seed` | 0 | 固定 seed 保证复现；换 seed 得到不同编舞 |
| `image_path` | 全身照 | 尽量避免复杂背景 |
| `music_path` | WAV | 建议 44100Hz 采样率 |

---

## 技术底座

Wan-Dancer 构建在两个开源项目之上：

- **[DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio)**：ModelScope 开源的扩散模型推理框架，提供底层推理引擎
- **[Wan2.1](https://github.com/Wan-Video/Wan2.1)**：万相视频生成基础模型，Wan-Dancer 在此之上进行音乐-动作对齐的专项微调

模型权重：Apache 2.0 许可证，可商用。

---

## 当前局限与已知问题

**硬件门槛高：** 官方要求 8×A800 80GB，消费级方案暂无官方量化版本。

**输入照片敏感：** 参考图质量直接影响输出——模糊、复杂背景、非正面均会降低人物一致性。

**音乐格式：** 目前仅支持 WAV，MP3/FLAC 需要提前转换。

**推理时间：** 即使在 8×A800 上，生成 3 分钟视频也需要相当时间；长视频推荐使用更大的 `num_inference_steps`。

---

## 快速体验（无需本地 GPU）

如果暂时没有合适的 GPU：

- **ModelScope Space**：[modelscope.ai/studios/Wan-AI/Wan-Dancer](https://modelscope.ai/studios/Wan-AI/Wan-Dancer)（官方在线 Demo）
- **Project Page**：[humanaigc.github.io/wan-dancer-project](https://humanaigc.github.io/wan-dancer-project/)（效果展示视频）

---

GitHub：[github.com/Wan-Video/Wan-Dancer](https://github.com/Wan-Video/Wan-Dancer)  
论文：[arxiv.org/abs/2607.09581](https://arxiv.org/abs/2607.09581)  
模型：[huggingface.co/Wan-AI/Wan-Dancer-14B](https://huggingface.co/Wan-AI/Wan-Dancer-14B)

© 2026 Author: Mycelium Protocol

<!--EN-->

## One Photo, 160 Seconds of Dance: Wan-Dancer-14B Open Source & Local Deployment Guide

> Paper: **Wan-Dancer: A Hierarchical Framework for Minute-scale Coherent Music-to-Dance Generation**  
> arXiv: [2607.09581](https://arxiv.org/abs/2607.09581) | July 10, 2026  
> GitHub: [Wan-Video/Wan-Dancer](https://github.com/Wan-Video/Wan-Dancer) | Model: [HF](https://huggingface.co/Wan-AI/Wan-Dancer-14B) | [MS](https://www.modelscope.cn/models/Wan-AI/Wan-Dancer-14B)

---

### The ~20s Wall in AI Dance Video

Existing diffusion models for video generation reliably produce coherent dance clips up to about 20 seconds — beyond that, three problems compound: **temporal drift** (beat alignment degrades), **identity inconsistency** (the face slowly shifts), and **repetitive motion** (the model loops the same moves since it never sees the full song).

Both skeleton-based and end-to-end approaches fail here. Wan-Dancer breaks through with a **hierarchical two-stage framework** that generates stable 720p/30fps videos up to 3 minutes long.

---

### Architecture: Two-Stage Hierarchical Generation

**Stage 1 — Global Keyframe Planning:**  
Input: reference portrait + full audio track + dance genre prompt  
Output: low-framerate but globally coherent skeleton video

Key innovations:
- **Full-track context**: reads the entire music track before planning movement, ensuring dance structure matches song structure
- **Time-mapped RoPE embeddings**: dynamically adapts frame rate for precise beat alignment across different dance genres

**Stage 2 — Local Temporal Refinement:**  
Input: global video + original reference photo + HD prompt  
Output: 720p/30fps final video

Key innovations:
- **Optical-flow loss function**: enforces inter-frame consistency, eliminating stuttering and jump cuts
- **Motion-speed control**: adjusts generation strategy during fast movements (spins, jumps) to preserve high-fidelity detail

---

### Supported Dance Genres

Chinese Classical Dance, K-Pop, Street Dance, Tap Dance, Latin Dance  
Each genre has its own pair of `_global.txt` and `_local.txt` prompt files in the repo.

---

### Local Deployment

**Hardware:** Official testing uses 8 × A800 80GB (640GB total VRAM). Realistic minimum: 4 × A100 80GB or cloud GPU (RunPod/Lambda Labs). No consumer-grade quantized version yet — use the [ModelScope Space](https://modelscope.ai/studios/Wan-AI/Wan-Dancer) to preview.

**Environment (Ubuntu 22.04, Python 3.10, CUDA 12.4):**

```bash
git clone https://github.com/Wan-Video/Wan-Dancer.git && cd Wan-Dancer
python -m venv venv_wan_dancer && source venv_wan_dancer/bin/activate
pip install -e .
pip install moviepy loguru librosa
pip install https://mirrors.aliyun.com/pytorch-wheels/cu124/torch-2.6.0+cu124-cp310-cp310-linux_x86_64.whl
pip install torchvision==0.21.0 diffusers==0.34.0 yunchang==0.5.0
pip install flash_attn==2.6.3 xfuser==0.4.0 transformers==4.46.2
```

**Download model:**
```bash
huggingface-cli download Wan-AI/Wan-Dancer-14B --local-dir ./models/Wan-Dancer-14B
```

**Generate (two steps):**
```bash
# Step 1: Global keyframe video (num_steps=48)
./gen_video_global.sh   # set image_path, music_path, prompt_path, seed

# Step 2: Local refinement → 720p final video (num_steps=24)
./gen_video_local.sh    # + set global_video_path from Step 1
```

**Key parameters:**

| Parameter | Value | Notes |
|---|---|---|
| `num_inference_steps` | 48 / 24 | Higher = better quality; increase for longer videos |
| `cfg_scale` | 5 | Prompt adherence |
| `seed` | 0 | Change for different choreography |
| `image_path` | Full-body portrait | Clean background recommended |
| `music_path` | WAV file | 44100Hz preferred |

---

### Quick Online Demo

No GPU? Try: [modelscope.ai/studios/Wan-AI/Wan-Dancer](https://modelscope.ai/studios/Wan-AI/Wan-Dancer)

GitHub: [github.com/Wan-Video/Wan-Dancer](https://github.com/Wan-Video/Wan-Dancer)  
Paper: [arxiv.org/abs/2607.09581](https://arxiv.org/abs/2607.09581)  
License: Apache 2.0

© 2026 Author: Mycelium Protocol
