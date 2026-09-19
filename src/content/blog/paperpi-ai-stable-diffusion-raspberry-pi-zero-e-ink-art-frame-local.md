---
title: "树莓派 Zero 2 跑本地 Stable Diffusion，30 分钟出一张 AI 画——PaperPiAI 拆解"
titleEn: "Local Stable Diffusion on a Raspberry Pi Zero 2, 30 Minutes Per AI Painting — PaperPiAI Teardown"
description: "dylski/PaperPiAI，340 stars，MIT，Python。树莓派 Zero 2（¥100）+ 7色电子墨水屏，跑 OnnxStream Stable Diffusion，30 分钟自动出一张 AI 画，全程离线，装进相框就是一台自主 AI 艺术机器。核心工程细节：512MB 限制、Bullseye 强依赖、70°C 散热、salient 裁剪算法。"
descriptionEn: "dylski/PaperPiAI, 340 stars, MIT, Python. A Raspberry Pi Zero 2 (~$15) plus a 7-color e-ink display runs OnnxStream Stable Diffusion locally, generating one AI image every ~30 minutes, fully offline. Teardown: 512MB RAM constraints, Bullseye OS hard dependency, 70°C thermal ceiling, salient-feature crop algorithm."
pubDate: "2026-09-19"
updatedDate: "2026-09-19"
category: "Tech-Experiment"
tags: ["Raspberry-Pi", "e-ink", "Stable-Diffusion", "local-AI", "embedded", "OnnxStream", "AI-art", "hardware"]
heroImage: "../../assets/images/paperpi-ai-stable-diffusion-raspberry-pi-zero-e-ink-art-frame-local-banner.jpg"
---

> 📌 GitHub：https://github.com/dylski/PaperPiAI
> Stars：340 | License：MIT | 语言：Python
> 创建：2024-12-10 | 最后更新：2026-09-10

---

一台 $15 的计算机，跑本地 Stable Diffusion，每 30 分钟自动出一张 AI 画，装进相框后断网自运转——这不是概念，是 PaperPiAI 实际在做的事情。

硬件清单只有两样：树莓派 Zero 2 和一块 7.3 英寸 7 色电子墨水屏。没有云端 API，没有订阅费，没有摄像头或麦克风。

---

## 系统架构

整个流水线分三步，循环执行：

```
随机组合提示词 → OnnxStream SD 本地推理（~30分钟）
  → 频谱显著性裁剪 → 输出显示到电子墨水屏（~30秒）
```

**推理引擎**：OnnxStream，专为低内存设备设计的 Stable Diffusion 实现。Pi Zero 2 只有 512MB RAM，普通的 SD 推理框架直接跑不起来，OnnxStream 通过流式加载权重绕过了内存墙。

**显示**：Pimoroni Inky Impression 7.3"，7 色（黑/白/红/黄/蓝/绿/橙），刷新率慢是电子墨水的天然特性，这里用不上快刷——30 分钟才出一张图，30 秒的刷新完全够用。

**提示词系统**：内置 JSON 文件，把描述词拆成数组片段随机组合，默认倾向植物/花卉风格（对电子墨水的有限色域友好）。也可以命令行直传自己的 prompt。

---

## 关键工程细节

### 512MB RAM 的墙

Pi Zero 2 只有 512MB 内存，这个限制贯穿整个项目：

- 标准 SD 推理（Diffusers、ComfyUI）需要至少 2-4GB，直接排除
- OnnxStream 把模型权重按层流式读取，推理时峰值内存控制在 512MB 以内
- **编译时**也受限：无法多核并行编译，`make -j4` 会直接 OOM，只能单线程，导致"几个小时"的编译时间

安装前需要先把 swap 扩到 1024MB（默认 100MB），否则编译过程会因为物理内存不够导致随机失败：

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Bullseye 强依赖（不能升级）

这是目前最大的工程坑。OnnxStream 在 Raspbian Bullseye 上编译通过；Bookworm（当前稳定版）**生成速度显著变慢**；Trixie（测试版）有未解决的兼容性问题。

如果你已经装了 Bookworm，目前没有简单的迁移路径——需要重新烧 Bullseye Lite 镜像。

### 温度管理

Pi Zero 2 被封在相框里，散热空间有限。实测最高温度 70°C，接近 ARM Cortex-A53 的热降频阈值（80°C）。

实际建议：
- 加散热片（铝片+导热贴，几块钱）
- 相框背板留通风缝
- 避免放在阳光直射或密闭柜内

连续运行时 70°C 是正常工作温度，不会立即损坏，但持续超过 80°C 会触发系统降频，导致生成时间从 30 分钟拉长到不可预测。

### 显著性裁剪（Salient Spectral Crop）

生成图的分辨率要和屏幕像素精确匹配（7.3" 屏是 800×480 横向或 480×800 竖向）。PaperPiAI 用了一个基于**频谱显著性**的智能裁剪算法：分析图像的高频能量分布，定位视觉焦点区域，然后裁出覆盖焦点的最优子区域，避免把构图中心裁掉。

比简单的居中裁切效果明显更好，对 SD 生成图尤其有用（SD 倾向于把主体放在画面中间偏上）。

---

## 安装流程

官方提供了安装脚本，一键完成依赖下载和 OnnxStream 编译：

```bash
git clone https://github.com/dylski/PaperPiAI
cd PaperPiAI
bash install.sh
```

脚本会：
1. 安装系统包（libopenblas、libomp 等）
2. 安装 Python 依赖（Pillow、Inky 库等）
3. 下载并编译 OnnxStream（时间最长，几小时）
4. 下载 Stable Diffusion 模型权重（约 8GB，视网速决定时长）

**安装前必须做**：
- `raspi-config` 里开启 SPI 和 I2C 接口
- swap 扩到 1024MB（见上）
- 确认系统是 Bullseye Lite

---

## 使用方式

**单次生成并显示：**

```bash
# 用默认随机提示词
python generate_picture.py
python display_picture.py output.png

# 用自定义提示词
python generate_picture.py --prompt "misty mountain forest at dawn, watercolor style"
python display_picture.py output.png
```

**自动循环运行（推荐）：**

用 systemd 服务或 cron 驱动，建议设在午夜（避免白天散热问题）：

```bash
# cron 每天 00:00 生成新图
0 0 * * * /usr/bin/python3 /home/pi/PaperPiAI/generate_picture.py && /usr/bin/python3 /home/pi/PaperPiAI/display_picture.py output.png
```

**按钮控制（GPIO）：**

Inky Impression 7.3" 自带 4 个物理按钮：
- A（GPIO 5）：切换到上一张已保存的图
- B（GPIO 6）：触发重新生成
- C（GPIO 16/25）：循环翻图
- D（GPIO 24）：安全关机

---

## 分辨率配置

不同屏幕需要对应调整，**必须是 32 的倍数**，否则 OnnxStream 会报错：

| 屏幕 | 横向分辨率 | 竖向分辨率 |
|------|-----------|-----------|
| Inky Impression 7.3" | 800×480 | 480×800 |
| Inky 13.3" | 1600×1216 | 1216×1600 |

13.3" 版本需要 Bullseye（32 位系统），Bookworm（64 位）不支持。

---

## 存储与成本

每张 800×480 图约 1.2MB，每天一张，每年约 440MB。作者建议如果不想归档，直接覆盖同一个文件名（`output.png`）即可——唯一保留的是 `output.png`，历史图靠时间戳命名文件单独存。

**一次性硬件成本**：
- Pi Zero 2：¥100 左右
- Inky Impression 7.3"（7 色）：约 ¥400-600（Pimoroni 原版）
- 相框：自选，深度要足够放下 Pi 和排线
- 散热片：几块钱

总计 ¥600 左右，无持续费用。

---

## 实际跑起来是什么体验

生成一张图需要约 30 分钟——对一台 $15 的设备来说这不是问题，是特性：你设置好，离开，回来看新画。电子墨水屏的静态观感、不发蓝光的特性，和"每隔一段时间自动换一张"的节奏，比动态显示器更适合放在书桌或床头。

SD 模型默认跑的是花卉/植物风格提示词，因为电子墨水的 7 色色域对细腻渐变支持有限，饱和度高的植物主题在 7 色输出下视觉效果最好。如果改用城市/人像主题，低色彩深度会让结果显得模糊和粗糙。

---

## 局限

- OS 版本锁死在 Bullseye，无法使用最新 Raspberry Pi OS 特性
- 编译和首次下载总耗时 4-6 小时以上，依赖网速和散热稳定性
- 512MB 限制导致无法运行更大、质量更高的 SD 模型变体
- 电子墨水屏显色精度有限，AI 生成图的细节损失明显
- 没有独立的 LLM 驱动提示词生成（开发者明确说 Pi Zero 2 规格不够），提示词系统是静态 JSON 随机组合

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 GitHub: https://github.com/dylski/PaperPiAI
> Stars: 340 | License: MIT | Language: Python
> Created: 2024-12-10 | Last updated: 2026-09-10

---

A $15 computer running local Stable Diffusion, generating one AI image every 30 minutes, fully offline in a picture frame — that's not a concept, it's what PaperPiAI actually does.

The hardware list is two items: a Raspberry Pi Zero 2 and a 7.3-inch 7-color e-ink display. No cloud API, no subscription fee, no camera or microphone.

---

## System Architecture

The pipeline loops through three steps:

```
Random prompt assembly → OnnxStream SD local inference (~30 min)
  → Salient spectral crop → Display to e-ink screen (~30 sec)
```

**Inference engine**: OnnxStream, a Stable Diffusion implementation designed for low-memory devices. The Pi Zero 2's 512MB RAM blocks standard SD frameworks; OnnxStream streams model weights layer by layer to stay under the memory ceiling.

**Display**: Pimoroni Inky Impression 7.3", 7-color (black/white/red/yellow/blue/green/orange). E-ink's slow refresh rate is irrelevant here — 30 seconds to refresh once every 30 minutes is fine.

**Prompt system**: Built-in JSON files split descriptions into fragment arrays that are randomly combined. The default style leans toward botanical/floral imagery, which suits e-ink's limited color gamut well. Custom prompts can be passed via command line.

---

## Key Engineering Details

### The 512MB RAM Wall

The Pi Zero 2's 512MB memory constraint shapes the entire project:

- Standard SD inference (Diffusers, ComfyUI) requires 2-4GB minimum — all ruled out
- OnnxStream streams model weights layer-by-layer, keeping peak RAM within 512MB
- **Compilation** is also constrained: parallel make fails with OOM, forcing single-threaded builds and multi-hour compile times

Before installing, expand swap to 1024MB (default is 100MB) — without this, compilation fails randomly:

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Bullseye Hard Dependency

This is the largest engineering trap. OnnxStream compiles cleanly on Raspbian Bullseye; on Bookworm (the current stable release) generation speed **degrades significantly**; Trixie (testing) has unresolved compatibility issues.

If you're already running Bookworm, there's no easy migration path — you need to reimage with Bullseye Lite.

### Thermal Management

The Pi Zero 2 runs inside a picture frame with limited airflow. Measured peak temperature: 70°C, approaching the ARM Cortex-A53 throttle threshold (80°C).

Practical recommendations:
- Add a heatsink (aluminum pad + thermal tape, very cheap)
- Leave ventilation gaps in the frame back panel
- Avoid direct sunlight or enclosed cabinets

70°C is a normal operating temperature for sustained use and won't immediately damage the hardware, but sustained temperatures above 80°C trigger CPU throttling, stretching generation time well past 30 minutes unpredictably.

### Salient Spectral Crop Algorithm

Generated image resolution must precisely match the display pixels (800×480 for landscape on the 7.3" screen). PaperPiAI uses a **salient spectral feature** crop: analyze the image's high-frequency energy distribution, locate the visual focal region, then crop the optimal sub-region covering that focal point.

This beats naive center-crop noticeably, especially for SD outputs which tend to place subjects center-top. The algorithm avoids decapitating the compositional focus of the image.

---

## Installation

The project ships an installation script that handles dependencies and OnnxStream compilation:

```bash
git clone https://github.com/dylski/PaperPiAI
cd PaperPiAI
bash install.sh
```

The script downloads system packages, Python dependencies, compiles OnnxStream from source (longest step, several hours), and downloads SD model weights (~8GB).

**Prerequisites before running:**
- Enable SPI and I2C in `raspi-config`
- Expand swap to 1024MB (see above)
- Confirm system is Bullseye Lite

---

## Usage

**Single generation and display:**

```bash
# Default random prompt
python generate_picture.py
python display_picture.py output.png

# Custom prompt
python generate_picture.py --prompt "misty mountain forest at dawn, watercolor style"
python display_picture.py output.png
```

**Automated loop (recommended):**

Drive with systemd or cron; midnight runs recommended to minimize heat accumulation:

```bash
# Cron: generate new image daily at 00:00
0 0 * * * /usr/bin/python3 /home/pi/PaperPiAI/generate_picture.py && /usr/bin/python3 /home/pi/PaperPiAI/display_picture.py output.png
```

**Physical button controls (GPIO):**

The Inky Impression 7.3" includes 4 physical buttons:
- A (GPIO 5): Previous saved image
- B (GPIO 6): Trigger new generation
- C (GPIO 16/25): Cycle through images
- D (GPIO 24): Safe shutdown

---

## Resolution Configuration

Resolution must match screen pixels exactly, **in multiples of 32** — OnnxStream throws errors otherwise:

| Screen | Landscape | Portrait |
|--------|-----------|----------|
| Inky Impression 7.3" | 800×480 | 480×800 |
| Inky 13.3" | 1600×1216 | 1216×1600 |

The 13.3" version requires Bullseye (32-bit); Bookworm (64-bit) is not supported.

---

## Storage and Cost

Each 800×480 image is ~1.2MB. One image per day consumes ~440MB/year. If you don't need history, just overwrite the same filename (`output.png`) — unique copies are stored with timestamped names separately.

**One-time hardware cost:**
- Pi Zero 2: ~$15
- Inky Impression 7.3" (7-color): ~$55-80 (Pimoroni)
- Picture frame: your choice, needs enough depth for Pi + ribbon cable
- Heatsink: ~$2

Total ~$80-100, no recurring costs.

---

## What Running It Actually Feels Like

A 30-minute generation time on a $15 device isn't a bug — it's the experience. You set it up, walk away, come back to a new painting. E-ink's static appearance, zero blue light, and the slow auto-rotation rhythm feel more natural as ambient art than a dynamic display. It's a slow medium running a slow process.

The default SD prompts lean toward botanical/floral styles because e-ink's 7-color gamut renders them best. The limited color depth makes urban scenes or portraits look muddy; saturated organic forms with defined edges translate cleanly.

---

## Limitations

- OS locked to Bullseye; cannot use current Raspberry Pi OS features
- Initial setup takes 4-6+ hours depending on network speed and thermal stability
- 512MB RAM prevents running larger, higher-quality SD model variants
- E-ink color depth causes noticeable detail loss in generated images
- No LLM-driven prompt generation (developer explicitly notes Pi Zero 2 isn't fast enough); prompts are static JSON random combinations

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
