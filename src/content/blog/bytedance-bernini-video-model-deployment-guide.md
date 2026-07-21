---
title: "字节开源 Bernini：统一视频生成与编辑框架，MLLM 语义规划 + DiT 渲染，比肩顶级商业模型"
titleEn: "ByteDance Open-Sources Bernini: Unified Video Generation & Editing with MLLM Semantic Planning + DiT Rendering"
description: "字节跳动开源视频模型 Bernini，基于 Qwen2.5-VL 语义规划器 + Wan2.2 DiT 渲染器的统一框架，在视频编辑排行榜上进入第一梯队，超越多个闭源商业模型。本文包含完整的部署指南、显存配置建议和 6 大任务类型的实战命令。"
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["视频生成", "字节跳动", "开源模型", "Bernini", "Wan2.2", "视频编辑", "AI视频", "MLLM", "DiT", "部署指南"]
heroImage: "../../assets/images/bytedance-bernini-video-model-deployment-guide-banner.jpg"
---

> **GitHub**：[bytedance/Bernini](https://github.com/bytedance/Bernini)  
> **HuggingFace Collection**：[ByteDance/bernini](https://huggingface.co/collections/ByteDance/bernini)  
> **项目主页**：[bernini-ai.github.io](https://bernini-ai.github.io/)  
> **论文**：[arXiv 2605.22344](https://arxiv.org/abs/2605.22344)  
> **开源时间**：2026年6月（Bernini-R），7月21日（训练代码完整开放）  
> **许可证**：Apache 2.0

---

## 这是什么

字节跳动 Bernini Team 开源的统一视频生成与编辑框架，Stars 已超 1100（今日刚完整开放训练代码）。

Bernini 的核心思路与众不同：**不是直接让扩散模型猜怎么改，而是先让 MLLM 规划"要在语义空间做什么变化"，再让扩散渲染器执行**。这条两阶段路线让它在复杂指令遵循上明显优于纯渲染器方案。

系统由两个组件组成：

**MLLM 语义规划器（Semantic Planner）**
- 基础：Qwen2.5-VL-7B-Instruct
- 接收：文本指令 + 源图像 / 源视频 + 参考图像
- 输出：目标语义嵌入序列（在潜在空间预测出"要生成什么"）

**DiT 渲染器（Renderer）**
- 基础：Wan2.2-T2V-A14B（MoE 架构，参数 14B）
- 接收：语义嵌入 + VAE 潜变量
- 执行：流匹配去噪，输出最终视频帧

两者通过 **Segment-Aware 3D RoPE（SA-3D RoPE）** 连接——这个改进的位置编码区分了来自不同视觉段（源视频帧、参考图像、目标位置）的 token，解决了多源输入时的对齐问题。

---

## 性能水平

官方 Human Arena 评测（人工盲测配对，Bradley-Terry 评分）：

| 排名 | 方法 | BT 分数 | 胜率 |
|---|---|---|---|
| 1 | HappyHorse-1.0（闭源商业） | 1080 | 61.3% |
| **2** | **Bernini（开源）** | **1044** | **56.3%** |
| 3 | Wan2.7 | 1034 | 54.9% |
| 4 | Grok-imagine-video | 964 | 44.9% |

Bernini 是唯一进入该榜单前三的开源模型，与排名第一的闭源商业产品差距仅 36 分（约 5%）。

基准评测数据：

| 模型 | EditVerse | OpenVE | VBench |
|---|---|---|---|
| Bernini-R 1.3B | 7.74 | 3.65 | 84.69 |
| Bernini-R 14B | 7.99 | 3.78 | 84.64 |
| **Bernini 7B+14B** | **8.02** | **4.03** | **84.37** |

---

## 两个可部署产品线

### Bernini（完整流水线）

**适合场景**：复杂指令、多步语义规划、强调指令遵循精度  
**权重**：[`ByteDance/Bernini-Diffusers`](https://huggingface.co/ByteDance/Bernini-Diffusers)（7B Planner + 14B Renderer，打包格式）  
**显存需求**：推荐 8×H100/A100（80GB），也支持 4×A100 配合 offload

完整包目录结构：
```
ByteDance/Bernini-Diffusers/
  bernini/           ← Bernini 规划权重
  mllm/              ← Qwen2.5-VL-7B 规划器
  t5_text_encoder/   ← 文本编码器
  t5_tokenizer/
  vae/
  scheduler/
  transformer_config.json
  transformer_2_config.json
```

### Bernini-R（仅渲染器）

**适合场景**：简单编辑（风格迁移、字幕/水印去除、局部修改）、更快推理、ComfyUI 集成  
**权重**：[`ByteDance/Bernini-R-Diffusers`](https://huggingface.co/ByteDance/Bernini-R-Diffusers)（14B）或 [`ByteDance/Bernini-R-1.3B-Diffusers`](https://huggingface.co/ByteDance/Bernini-R-1.3B-Diffusers)  
**显存需求**：14B 需 8×GPU；1.3B 可单卡 24GB（社区已验证 RTX 4090）

---

## 环境要求

```
Python 3.11.2
CUDA 12.6（最低 12.3）
PyTorch 2.7.1+cu126
diffusers 0.35.2
accelerate 0.34.2
transformers 4.57.3
```

注意事项：
- **H100/H800/H200（Hopper）**：可启用 FlashAttention-3，推理最快
- **A100/A800**：使用 FlashAttention-2，性能良好
- **其他 CUDA GPU**：回退到 PyTorch SDPA
- **CPU / Apple Silicon**：官方暂不支持（需 CUDA）

---

## 完整部署步骤

### 第一步：安装依赖

```bash
git clone https://github.com/bytedance/Bernini.git bernini
cd bernini
pip install -r requirements.txt

# 多 GPU 序列并行必须安装 VeOmni（--no-deps 避免覆盖 torch 版本）
pip install --no-deps git+https://github.com/ByteDance-Seed/VeOmni.git@v0.1.11

# 可选：FlashAttention-2（A100 及以下）
pip install flash-attn==2.8.3

# 可选：FlashAttention-3（H100 专属，需从源码编译）
git clone https://github.com/Dao-AILab/flash-attention.git
cd flash-attention && git checkout v2.8.3
cd hopper && MAX_JOBS=$(nproc) python3 setup.py install --user
```

### 第二步：下载权重

**选 Bernini-R（推荐入门）**：

```bash
pip install -U "huggingface_hub"

# 14B 完整版（~28GB）
hf download ByteDance/Bernini-R-Diffusers \
    --local-dir pretrained_models/Bernini-R-Diffusers

# 或 1.3B 轻量版（~3GB，适合 24GB 单卡）
hf download ByteDance/Bernini-R-1.3B-Diffusers \
    --local-dir pretrained_models/Bernini-R-1.3B-Diffusers
```

**选 Bernini 完整流水线**：

```bash
hf download ByteDance/Bernini-Diffusers \
    --local-dir pretrained_models/Bernini-Diffusers
```

国内网络建议走 ModelScope 镜像（可配 `HF_ENDPOINT=https://hf-mirror.com`）。

### 第三步：了解 Case File 格式

Bernini 用 JSON Case File 传递任务参数，而不是长命令行标志：

```json
{
  "task_type": "v2v",
  "guidance_mode": "v2v_apg",
  "prompt": "Remove the white sheep on the left side of the video.",
  "video": "path/to/source.mp4",
  "output": "output/edited.mp4"
}
```

任务类型（`task_type`）：
- `t2i`：文本→图像
- `i2i`：图像编辑
- `t2v`：文本→视频
- `v2v`：视频编辑
- `rv2v`：参考图像引导视频编辑
- `r2v`：参考图像→视频生成

---

## 6 大任务类型实战命令

### 1. 文本生成图像（t2i）— 单卡

```bash
python infer_single_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --case assets/testcases/t2i/t2i.json \
    --num_frames 1 \
    --guidance_mode t2v_apg
```

或直接传参数：

```bash
python infer_single_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --prompt "A futuristic cityscape at dusk, cinematic lighting, 8K" \
    --task_type t2i \
    --num_frames 1 \
    --output output/city.png
```

### 2. 图像编辑（i2i）— 单卡

```bash
python infer_single_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --case assets/testcases/i2i/i2i.json \
    --num_frames 1 \
    --guidance_mode t2v_apg
```

### 3. 文本生成视频（t2v）— 多卡

```bash
torchrun --nproc-per-node 8 infer_multi_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --ulysses 8 \
    --case assets/testcases/t2v/t2v.json \
    --guidance_mode t2v_apg
```

默认输出：480p / 16fps / 81帧（约5秒）

### 4. 视频编辑（v2v）— 多卡

```bash
torchrun --nproc-per-node 8 infer_multi_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --ulysses 8 \
    --case assets/testcases/v2v/v2v_case1.json \
    --guidance_mode v2v_apg
```

Case 文件示例（天气改变）：

```json
{
  "task_type": "v2v",
  "guidance_mode": "v2v_apg",
  "prompt": "Convert the video into an immersive snowy winter wonderland.",
  "video": "assets/source_videos/forest.mp4",
  "output": "output/winter.mp4"
}
```

### 5. 参考图像引导编辑（rv2v）— 多卡

```bash
torchrun --nproc-per-node 8 infer_multi_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --ulysses 8 \
    --case assets/testcases/rv2v/rv2v_case1.json \
    --guidance_mode rv2v_apg
```

适合：用参考图替换视频中的物体、材质、天气、风格。

### 6. 参考→视频生成（r2v）— 最多5张参考图

```bash
torchrun --nproc-per-node 8 infer_multi_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --ulysses 8 \
    --case assets/testcases/r2v/r2v_case1.json \
    --guidance_mode r2v_apg
```

使用脚本批量运行：

```bash
# 一键运行各任务（读取 BERNINI_R_CONFIG 环境变量）
export BERNINI_R_CONFIG=./pretrained_models/Bernini-R-Diffusers
export NPROC_PER_NODE=8
export ULYSSES=8

bash scripts/bernini_r/run_t2i.sh
bash scripts/bernini_r/run_t2v.sh
bash scripts/bernini_r/run_v2v.sh
bash scripts/bernini_r/run_rv2v.sh
```

---

## Gradio 可视化界面

```bash
# 单卡（仅图像任务）
python gradio_demo.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --port 7860

# 8 卡并行（视频任务）
torchrun --nproc-per-node 8 gradio_demo.py \
    --ulysses 8 \
    --config pretrained_models/Bernini-R-Diffusers \
    --port 7860 \
    --share   # 生成公开 URL
```

---

## Prompt Enhancer（强烈推荐）

启用 `--use_pe` 可通过任意 OpenAI 兼容端点增强提示词，显著提升生成质量。

```bash
export BERNINI_PE_API_KEY=your_key
export BERNINI_PE_BASE_URL=https://api.openai.com/v1   # 或 Ollama/vLLM 端点
export BERNINI_PE_MODEL=gpt-4o-mini                     # 任意视觉模型

torchrun --nproc-per-node 8 infer_multi_gpu.py \
    --config pretrained_models/Bernini-R-Diffusers \
    --ulysses 8 \
    --case assets/testcases/t2v/t2v.json \
    --use_pe
```

配合本地模型（免费，完全离线）：

```bash
# 启动 Ollama
ollama serve &
ollama pull qwen2.5vl:7b

export BERNINI_PE_API_KEY=ollama
export BERNINI_PE_BASE_URL=http://localhost:11434/v1
export BERNINI_PE_MODEL=qwen2.5vl:7b
```

---

## 完整流水线（Bernini 7B+14B）特有命令

```bash
export BERNINI_CONFIG=./pretrained_models/Bernini-Diffusers
export NPROC_PER_NODE=8
export ULYSSES=8

# 文本生成视频（更强的指令跟随）
bash scripts/bernini/run_t2v.sh

# 复杂视频编辑（MLLM 语义规划优势最明显的场景）
CASE_PATH=assets/testcases/v2v/v2v_case2.json \
bash scripts/bernini/run_v2v.sh

# Gradio 界面
torchrun --nproc-per-node 8 gradio_demo.py \
    --ulysses 8 \
    --config ByteDance/Bernini-Diffusers \
    --port 7860 --share
```

---

## 显存配置参考

| 模型 | GPU 配置 | 分辨率 | 备注 |
|---|---|---|---|
| Bernini-R 1.3B | 单卡 RTX 4090 (24GB) | 480p | 社区验证可行 |
| Bernini-R 14B | 8×A100 (80GB) | 480p/720p | 官方推荐 |
| Bernini-R 14B | 4×A100 (80GB) | 480p | 减少 `--ulysses 4` |
| Bernini-R 14B | 8×H100 (80GB) | 480p/720p | 最优，FlashAttn-3 |
| Bernini 7B+14B | 8×H100 (80GB) | 480p/720p | 完整流水线推荐 |

**国内可用的 A100/H100 算力租用**：AutoDL、Vast.ai、Lepton.ai（按需选择）

---

## 训练（Fine-tune Bernini-R）

训练代码于 2026-07-13 完整开放：

```bash
# 推荐用 uv 管理训练环境
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
uv sync --extra all
uv pip install --no-build-isolation "flash-attn==2.8.3"

# 开始训练
uv run python train_bernini_r.py \
    --config configs/bernini_renderer_wan22/config.json \
    --dataset_path /path/to/your/dataset \
    --output_dir output/finetuned
```

完整训练文档：[docs/bernini_r_train.md](https://github.com/bytedance/Bernini/blob/main/docs/bernini_r_train.md)

---

## 关键技术设计

**为什么不用向量数据库式的"检索图像"而是"规划语义"？**

传统视频编辑方法直接把源视频和提示词丢给扩散模型，依赖模型自己"猜"出正确的编辑方向。对于简单的风格迁移这没问题，但复杂指令（"把视频右半部分变成俄罗斯古典宫廷舞蹈黏土动画停格风格，左半保持原战争场景"）很难一步到位。

Bernini 的解法是：**先让 MLLM 规划"目标语义嵌入在哪里"，再让 DiT 沿着语义梯度去噪**。这把一个硬推理问题拆成了两个更简单的子问题。

**SA-3D RoPE 解决了什么？**

多源输入（源视频帧 + 参考图像1 + 参考图像2 + 目标占位符）会在 attention 中混乱。SA-3D RoPE 为不同视觉段的 token 赋予不同的位置编码，让渲染器知道哪些 token 来自源，哪些是参考，哪些是要生成的目标。

---

## 与同类开源模型对比

| 模型 | 机构 | 规划器 | 渲染器 | 最强任务 | 单卡可运行 |
|---|---|---|---|---|---|
| **Bernini** | 字节跳动 | Qwen2.5-VL-7B | Wan2.2-14B | 复杂视频编辑 | 仅 1.3B 版本 |
| Wan2.2 | 阿里 | 无 | MoE-14B | T2V 生成 | 5B 版 720P |
| HunyuanVideo | 腾讯 | 无 | 13B | T2V 生成 | 部分支持 |
| CogVideoX | 智谱 | 无 | 5B/13B | T2V 生成 | 5B 可单卡 |

Bernini 目前是开源生态里视频编辑（v2v）能力最强的，但 T2V 纯生成能力不是它的重点（VBench 84.37 对比 Wan2.2 的 top 性能略低）。

---

## 上手建议

1. **从 Bernini-R 1.3B 开始**：单卡 24GB 可跑，先验证 i2i（图像编辑）任务流通了
2. **用 Gradio 界面测试**：`--share` 生成公开 URL，不需要本地 UI
3. **v2v 是杀手用例**：天气变换、风格迁移、对象删除是 Bernini 最闪亮的场景
4. **接 Prompt Enhancer**：配本地 Ollama（Qwen2.5-VL），提示词质量差距非常大
5. **复杂指令上完整 Bernini 7B+14B**：1.3B 在"人物动作生成"等复杂任务上明显弱于 14B

---

## 参考资源

- **GitHub**：[bytedance/Bernini](https://github.com/bytedance/Bernini)
- **HuggingFace Collection**：[ByteDance/bernini](https://huggingface.co/collections/ByteDance/bernini)
  - 完整流水线：[ByteDance/Bernini-Diffusers](https://huggingface.co/ByteDance/Bernini-Diffusers)
  - 14B 渲染器：[ByteDance/Bernini-R-Diffusers](https://huggingface.co/ByteDance/Bernini-R-Diffusers)
  - 1.3B 轻量版：[ByteDance/Bernini-R-1.3B-Diffusers](https://huggingface.co/ByteDance/Bernini-R-1.3B-Diffusers)
- **论文**：[arXiv 2605.22344 — Bernini: Latent Semantic Planning for Video Diffusion](https://arxiv.org/abs/2605.22344)
- **项目主页**：[bernini-ai.github.io](https://bernini-ai.github.io/)
- **ComfyUI 节点**：[ComfyUI-Bernini](https://github.com/AIMixer/ComfyUI-Bernini)（社区）

© 2026 Author: Mycelium Protocol
