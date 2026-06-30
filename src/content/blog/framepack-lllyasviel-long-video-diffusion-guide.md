---
title: "FramePack：ControlNet 作者开源，6G 显存生成 1 分钟视频，F1+P1 双版抗漂移"
titleEn: "FramePack: ControlNet Author's Open-Source Long Video Diffusion — 6GB VRAM, 1-Minute 30fps, F1+P1 Anti-Drift Dual Versions"
description: "ControlNet 作者 lllyasviel（张吕敏）开源 FramePack（17K⭐，Apache 2.0），独创帧上下文打包技术将历史帧压缩为恒定长度，算力开销不随视频变长增长，6GB 显存可跑 13B 大模型生成 60 秒 30fps 视频。F1 前向生成，P1 新增规划抗漂移+历史离散化，大幅抑制超长视频画面跑偏。Gradio GUI，Windows 一键整合包，RTX 4090 开启 TeaCache 可达 1.5 秒/帧。"
descriptionEn: "ControlNet author lllyasviel open-sources FramePack (17K⭐, Apache 2.0): Frame Context Packing compresses historical frames to constant length so compute stays flat regardless of video length. 6GB VRAM runs a 13B model for 60s at 30fps. F1 forward generation, P1 adds Planned Anti-Drifting + History Discretization for ultra-long stability. Gradio GUI, Windows one-click package, 1.5s/frame on RTX 4090 with TeaCache."
pubDate: "2026-06-29"
updatedDate: "2026-06-29"
category: "Tech-News"
tags: ["视频生成", "扩散模型", "ControlNet", "开源", "本地AI", "图生视频", "文生视频", "显存优化"]
heroImage: "../../assets/images/framepack-lllyasviel-long-video-diffusion-guide-banner.jpg"
---

> **一句话定位**：FramePack 解决了视频扩散模型最根本的工程难题——「视频越长显存和算力要求越高」——用帧上下文打包技术让计算开销与视频长度彻底解耦，6GB 显卡笔记本也能跑 13B 大模型生成 1 分钟视频。

---

## 项目信息

GitHub：https://github.com/lllyasviel/FramePack （17,083 ⭐，Apache 2.0 商用友好）

论文：arXiv:2504.12626，收录于 NeurIPS 2025

项目主页：https://lllyasviel.github.io/frame_pack_gitpage/

作者：Lvmin Zhang（张吕敏）— ControlNet 作者，Stanford 博士研究员（合作者：Shengqu Cai、Muyang Li、Gordon Wetzstein、Maneesh Agrawala）

---

## 作者是谁

FramePack 的作者是 **lllyasviel（张吕敏）**，即 **ControlNet** 和 **Stable Diffusion WebUI Forge** 的作者。

ControlNet 是 2023 年最具影响力的图像生成控制方法之一，让用户可以用骨骼图、边缘图、深度图等精确控制 Stable Diffusion 的生成内容。张吕敏的代码风格以「极低资源消耗跑起大模型」著称——FramePack 延续了这个传统：**6GB 显存跑 13B 参数的视频扩散模型**。

---

## 视频扩散的根本难题

现有的视频生成模型（Wan、CogVideoX、Sora 同类方案）普遍面临一个根本性的扩展性问题：

```
传统视频扩散：
输入帧数 × 每帧 tokens → KV Cache / 显存占用
视频变长 → 显存需求线性增长
10s 视频能跑 → 60s 视频可能显存爆炸
```

这不只是工程优化的问题，是**架构设计**的问题：当你要把历史帧全部塞进模型的上下文窗口作为条件时，成本必然随长度增长。

**解法**：要么限制视频长度，要么提供更强的显卡，要么重新设计架构。FramePack 选了第三条路。

---

## 核心技术：帧上下文打包（Frame Context Packing）

### 基本思路

FramePack 把视频生成变成一个**下一帧（段）预测问题**：每次只生成下一个帧段，而不是一次性生成整段视频。

关键是如何给模型提供「历史」：把已经生成的帧全部喂进去太贵，完全不看历史则画面会飘。

Frame Context Packing 的解法：

```
历史帧序列（任意长度）
    ↓ 压缩编码
固定长度的「打包上下文」（Packed Context）
    ↓
当前帧段生成
```

**核心性质**：无论视频已经生成了 5 秒还是 50 秒，送进模型的「打包上下文」长度恒定，**计算开销不随视频变长而增加**。

### 工程意义

```
传统方案：
  10s 视频  → 显存 X GB
  60s 视频  → 显存 6X GB（线性增长）

FramePack：
  10s 视频  → 显存 X GB
  60s 视频  → 显存 X GB（恒定！）
```

这就是为什么 6GB 显卡能跑 60 秒视频：显存需求由每帧段生成的固定开销决定，不是总帧数。

### 类比训练效率

论文里特别提到一个有趣的点：由于每次只处理固定长度上下文，FramePack 训练时的 batch size 可以做得和图像扩散训练一样大——而传统视频扩散因为序列太长，batch size 被迫很小。这意味着**训练效率也显著提升**，未来会有更多基于这个架构的模型出现。

> *Video diffusion, but feels like image diffusion.*

---

## 两大版本：F1 与 P1

### F1（已发布，2025 年 5 月）

**FramePack-F1** 是基础版本，实现标准的前向下一帧段预测：

- 给定起始图像（image-to-video）或文本描述（text-to-video）
- 逐段向前生成，每段完成后看到结果
- 适合中等长度视频（5-30 秒）

### P1（新版本，2025 年 6 月）

**FramePack-P1** 加入了两个专门针对超长视频漂移问题的设计：

**1. 规划抗漂移（Planned Anti-Drifting）**

长视频生成中最常见的问题是「画面漂移」——人物从第 1 秒到第 60 秒逐渐变形、换脸、场景错乱。P1 在生成前引入「规划」阶段，预先约束长程内容的一致性。

**2. 历史离散化（History Discretization）**

对压缩后的历史帧做更精细的离散量化，减少长视频中历史信息的累积误差，从源头抑制漂移。

P1 的抗漂移压测结果（纯文生视频，无参考图）已发布在项目主页：https://lllyasviel.github.io/frame_pack_gitpage/p1/#text-to-video-stress-tests

---

## 硬件要求与速度

### 最低要求

| 项目 | 要求 |
|---|---|
| GPU | RTX 30XX / 40XX / 50XX 系列（支持 fp16/bf16）|
| 最低显存 | **6GB**（含 13B 模型，生成 60 秒 30fps）|
| 操作系统 | Windows 或 Linux |
| 注意 | GTX 10XX/20XX 未经测试 |

### 实测速度

| 设备 | 速度（无 TeaCache）| 速度（开 TeaCache）|
|---|---|---|
| RTX 4090 桌面 | ~2.5 秒/帧 | **~1.5 秒/帧** |
| RTX 3070ti 笔记本 | ~10-20 秒/帧 | 更快 |
| RTX 3060 笔记本 | ~20-40 秒/帧 | 更快 |

生成 30 秒视频（900 帧），RTX 4090 + TeaCache 约 22 分钟；笔记本 3070ti 约 1.5-3 小时。可接受的范围，且可以边生成边看预览。

### 关于 TeaCache

TeaCache 是一种注意力缓存加速技术，可将速度提升约 40%，但会引入轻微的质量差异（约 30% 用户会感知到差别）。作者建议：

- **第一次跑健全性检查时关掉 TeaCache**，确认硬件没问题
- **日常生产**时按需开启，速度优先开，质量优先关

---

## 安装与使用

### Windows 一键整合包（推荐新手）

1. 下载整合包：[framepack_cu126_torch26.7z](https://github.com/lllyasviel/FramePack/releases/download/windows/framepack_cu126_torch26.7z)（CUDA 12.6 + PyTorch 2.6）
2. 解压到任意目录
3. **先运行 `update.bat`**（更新到最新版，不跑这步可能有旧版 bug）
4. 运行 `run.bat` 启动 Gradio 界面
5. 首次启动会自动从 HuggingFace 下载模型（共 30GB+，需要等待）

> 注意：**`update.bat` 必须先跑**，作者在发布后频繁修复 bug，直接跑旧版是常见踩坑。

### Linux 源码部署

```bash
# Python 3.10 独立环境推荐
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt

# 启动 GUI
python demo_gradio.py

# 可选参数
python demo_gradio.py --share        # 生成公网链接（协作/远程访问）
python demo_gradio.py --port 7860    # 指定端口
```

### 可选注意力后端（加速）

默认使用 PyTorch 原生注意力，可选安装更快的后端：

```bash
# sage-attention（Linux，推荐先不装，确认基础效果后再装）
pip install sageattention==1.0.6

# flash-attn
# xformers
```

---

## 使用指南

### 基本工作流

**图生视频（Image-to-Video）**：
1. 左侧上传参考图（人物、场景）
2. 写动作 prompt（英文效果最好）
3. 设置视频时长、分辨率
4. 点生成，右侧实时看每段预览

**纯文生视频（Text-to-Video）**：
1. 不上传图片，只写 prompt
2. 建议使用 P1 版本（抗漂移更强）

### 如何写好 Prompt

作者推荐用以下 ChatGPT 模板快速生成 prompt：

```
You are an assistant that writes short, motion-focused prompts for animating images.

When the user sends an image, respond with a single, concise prompt describing 
visual motion. Describe subject, then motion, then other things. 
For example: "The girl dances gracefully, with clear movements, full of charm."

Larger and more dynamic motions (dancing, jumping, running) are preferred 
over smaller or subtle ones.

Stay in a loop: one image in, one motion prompt out.
```

**直接参考这些高质量样例 Prompt**：

| 场景 | Prompt |
|---|---|
| 舞蹈（男）| `The man dances energetically, leaping mid-air with fluid arm swings and quick footwork.` |
| 舞蹈（女）| `The girl dances gracefully, with clear movements, full of charm.` |
| 动感姿态 | `The man dances flamboyantly, swinging his hips and striking bold poses with dramatic flair.` |
| 汉服舞蹈 | `The woman dances elegantly among the blossoms, spinning slowly with flowing sleeves and graceful hand movements.` |
| 滑板 | `The girl skateboarding, repeating the endless spinning and dancing and jumping on a skateboard, with clear movements, full of charm.` |
| 专注书写 | `The young man writes intensely, flipping papers and adjusting his glasses with swift, focused movements.` |
| 道具动作 | `The girl suddenly took out a sign that said "cute" using right hand` |

**规律**：
- **描述顺序**：主体 → 动作 → 其他细节
- **优先大动作**：跳舞、跳跃、奔跑比站立、坐着效果好很多
- **简洁为主**：一两句话就够，不需要长篇描述
- **英文 Prompt**：效果优于中文

### 首次上手健全性检查

作者强烈建议用官方测试案例验证硬件正常：

1. 下载官方测试图（README 中有链接）
2. 输入指定 Prompt
3. **关掉 TeaCache**，保持所有参数默认
4. 对比官方结果——不会完全一样（不同硬件有细微差异），但整体应该相似

如果结果差异很大，参考 [Issues #151](https://github.com/lllyasviel/FramePack/issues/151#issuecomment-2817054649) 进行排查。

---

## 防骗提示

README 里作者罕见地专门写了一整段警告：

> **GitHub 仓库是唯一官方 FramePack 网站，没有任何网络服务。** 所有其他网站都是垃圾和假冒，包括但不限于 `framepack.co`、`framepack.ai`、`framepack.net`、`framepack.pro`、`framepack.cc`…… **不要向这些网站付钱或从这些网站下载文件。**

这说明 FramePack 已经火到被大量仿冒网站盯上了——记住只从 GitHub Releases 下载。

---

## FramePack 的技术意义

### 对开源社区

FramePack 发布时（2025 年 4 月）是开源视频生成领域**显存效率最高**的方案之一：

- 同等显存下，比 Wan2.1 / CogVideoX 等方案能生成更长的视频
- Apache 2.0 开源，可以商用，可以在此基础上训练自己的模型
- 架构简洁，作者的工程风格使得部署门槛极低

### 对视频生成的范式影响

FramePack 的「下一帧预测」思路和「恒定上下文」设计，正在被更多研究者采用。论文发在 NeurIPS 2025，意味着这个方向已经得到顶会认可。

R-SWA（Unlimited-OCR 里的同类思路）和 Frame Context Packing 代表的是同一个趋势：**用恒定长度的压缩上下文替代线性增长的全历史上下文**，让大模型从「受显存限制」变成「受生成时间限制」——而生成时间是可以用更好的硬件或更长的等待来换的，显存瓶颈则更难突破。

### 适合哪些场景

| 应用场景 | 推荐配置 |
|---|---|
| 动画短视频批量生成 | F1 + TeaCache + RTX 4090 |
| 剧情短片（需要一致性）| P1 + 关 TeaCache |
| 角色动作素材库 | F1 + 图生视频模式 |
| 纯文本创意视频 | P1（抗漂移更强）|
| 笔记本本地试验 | F1 + 开 TeaCache |

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/lllyasviel/FramePack |
| 论文 arXiv | https://arxiv.org/abs/2504.12626 |
| 项目主页 | https://lllyasviel.github.io/frame_pack_gitpage/ |
| P1 演示结果 | https://lllyasviel.github.io/frame_pack_gitpage/p1/ |
| P1 纯文生视频压测 | https://lllyasviel.github.io/frame_pack_gitpage/p1/#text-to-video-stress-tests |
| Windows 整合包 | GitHub Releases（framepack_cu126_torch26.7z）|
| 速度排查 Issue | https://github.com/lllyasviel/FramePack/issues/151 |

---

## 总结

FramePack 用一个优雅的架构决策——帧上下文打包——解决了视频扩散最头疼的扩展性问题。ControlNet 作者的出品，从代码质量到工程友好度都有保证；Apache 2.0 的许可证让商业使用和二次开发没有障碍。

F1 已经可以稳定用于生产，P1 的抗漂移设计则让超长视频创作成为可能。如果你有一台 RTX 30 系以上的 N 卡，6GB 显存，想在本地生成视频内容，FramePack 目前是最值得上手的开源方案。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **In one line**: FramePack (ControlNet author's work) solves the fundamental scalability problem of video diffusion — compute cost stays flat regardless of video length — through Frame Context Packing. 6GB VRAM, 13B model, 60-second 30fps video. F1 is stable, P1 adds anti-drift for ultra-long generation.

---

## The Core Problem FramePack Solves

Standard video diffusion feeds all historical frames as context → memory grows linearly with video length. A 10-second video needs X GB; a 60-second video needs 6X GB.

**Frame Context Packing** compresses historical frames into a **fixed-length packed context**:
- The packed context length stays constant regardless of how many frames have been generated
- Compute cost per frame segment stays flat
- 6GB VRAM handles a 13B model generating 1800 frames (60s × 30fps)

## Two Versions

| Version | Features | Use Case |
|---|---|---|
| **F1** (released May 2025) | Basic forward next-frame prediction | Short-medium videos, image-to-video |
| **P1** (June 2025) | + Planned Anti-Drifting + History Discretization | Long videos, pure text-to-video |

## Hardware & Speed

- **Minimum**: 6GB VRAM, RTX 30XX/40XX/50XX
- **RTX 4090**: 2.5s/frame → 1.5s/frame with TeaCache
- **Laptop 3070ti/3060**: 4-8x slower

## Quick Start

**Windows**: Download one-click package from Releases → run `update.bat` → run `run.bat`

**Linux**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
python demo_gradio.py
```

Models auto-download from HuggingFace (~30GB).

## Prompting Tips

- Order: subject → motion → details
- Prefer large motions (dancing, jumping) over subtle ones
- Short and direct beats long descriptions
- English prompts outperform Chinese

Example: *"The girl dances gracefully, with clear movements, full of charm."*

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution.
