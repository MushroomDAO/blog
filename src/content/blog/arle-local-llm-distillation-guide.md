---
title: "arle 实战指南：普通笔记本一键跑本地大模型，再用蒸馏让 4B 模型追上 35B 的推理能力"
titleEn: "arle Practical Guide: Run Local LLMs on Any Laptop, Then Distill a 4B Model to Match a 35B"
description: "arle 是纯 Rust 编写的本地 LLM 运行时，一个二进制文件搞定 OpenAI 兼容服务、本地 Agent 和在线蒸馏训练。MacBook M4 Pro 上 35B MoE 跑出 85 tok/s；用 OPD 蒸馏后 4B 模型在 MATH-500 上提升 27 个百分点。本文从模型玩家视角梳理完整上手流程。"
descriptionEn: "arle is a pure-Rust local LLM runtime — one binary for OpenAI-compatible serving, local agents, and on-policy distillation training. A 35B MoE hits 85 tok/s on an M4 Pro MacBook. OPD distillation lifts a 4B student by +27pp on MATH-500. Full hands-on guide from a model enthusiast's perspective."
pubDate: "2026-06-27"
updatedDate: "2026-06-27"
category: "Tech-News"
tags: ["本地大模型", "模型蒸馏", "Rust", "Apple Silicon", "AI推理", "OPD", "Qwen3", "开源工具"]
heroImage: "../../assets/images/arle-local-llm-distillation-guide-banner.jpg"
---

> **一句话结论（BLUF）**：arle 解决了两个痛点——①在普通笔记本/PC 上把本地大模型跑起来（一行命令，纯 Rust，无 Python 依赖）；②用"在线蒸馏（OPD）"让你的小模型向大模型学，在你自己的场景里大幅提升能力。实测 4B 模型蒸馏后 MATH-500 分数从 0.518 涨到 0.792，接近 35B 教师模型的 0.82。

GitHub：https://github.com/cklxx/arle  
⭐ 14 Stars · 纯 Rust · MIT · 2026-03 发布，持续迭代中

---

## 为什么是 arle？

本地跑大模型的工具已经不少——llama.cpp、Ollama、vLLM……arle 的差异点是三合一：

```
同一个二进制文件，三件事：
  arle serve   → OpenAI 兼容 HTTP 服务
  arle         → 本地 Agent / REPL
  arle train opd → 在线蒸馏训练（教师就是正在 serve 的模型）
```

没有 Python 在关键路径上（"No Python on the hot path"）——这意味着启动快、内存开销小、部署简单。对于普通笔记本用户，少折腾 Python 环境是真实收益。

---

## 第一步：确认你的硬件能跑什么

### Apple Silicon Mac

arle Metal 后端目前处于 **Beta** 阶段，支持：
- Qwen3.5 全系列（0.8B / 4B / 9B / 14B）
- Qwen3.6（含 35B-A3B MoE，Metal 独占）

**实测性能（M4 Pro，48GB 统一内存，4-bit 量化）**：

| 模型 | 解码速度 | 每 token 延迟 | 首 token 延迟 |
|---|---:|---:|---:|
| Qwen3.5-0.8B | **318 tok/s** | 3.2 ms | 0.17 s |
| Qwen3.5-4B | 84 tok/s | 11.9 ms | 0.82 s |
| Qwen3.5-9B | 50 tok/s | 20.0 ms | 1.45 s |
| **Qwen3.6-35B-A3B MoE** | **85 tok/s** | 11.7 ms | 1.23 s |

> MoE 的妙处：35B 总参数，但每个 token 只激活约 3B——所以速度和 4B 密集模型相当，但能力远超。**一台 MacBook 跑出 35B 的智识，4B 的速度。**

内存要求参考（4-bit 量化）：
- 4B 模型 ≈ 3–4 GB 显存
- 9B 模型 ≈ 6–8 GB 显存
- 35B-A3B MoE ≈ 20–24 GB（建议 32GB 以上统一内存）

### NVIDIA GPU（Linux）

- **CUDA Stable** 状态，支持 Qwen3.5 全系列 + DeepSeek-V4-Flash
- 单卡（RTX 4090 / A100 等）跑 Qwen3.5 系列
- 多卡（8×H20）跑 DeepSeek-V4-Flash，实测 53 tok/s

### CPU-only

目前仅供开发调试，实际使用建议有 GPU。

---

## 第二步：安装

### Mac（最简单）

```bash
# Homebrew 一行搞定
brew install cklxx/tap/arle
```

### Mac / Linux 通用一行安装

```bash
curl -fsSL https://github.com/cklxx/arle/releases/latest/download/install.sh | sh
```

### Linux + NVIDIA GPU（Docker，零编译）

```bash
docker run --rm --gpus all -p 8000:8000 \
  -v /path/to/Qwen3.5-4B:/model:ro \
  ghcr.io/cklxx/arle:latest \
  serve --backend cuda --model-path /model
```

安装验证：

```bash
arle --doctor
# 自检后端 / 硬件 / 模型分辨率，输出兼容性报告
```

---

## 第三步：第一次跑起来模型

### 最快方式：零配置启动

```bash
# 直接运行（arle 会自动选模型并启动服务+Agent）
arle
```

### 手动指定模型和后端

```bash
# Apple Silicon — 4-bit 量化模型（从 HuggingFace 自动拉取）
arle serve --backend metal \
  --model-path mlx-community/Qwen3.5-4B-MLX-4bit \
  --port 8000

# NVIDIA GPU
arle serve --backend cuda \
  --model-path /path/to/Qwen3.5-4B \
  --port 8000
```

### 验证服务是否正常

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-4b",
    "messages": [{"role": "user", "content": "你好，请介绍一下你自己"}]
  }'
```

---

## 第四步：接入任何 OpenAI 兼容工具

arle 启动后对外暴露标准的 OpenAI v1 接口，所有支持自定义 API 地址的工具直接可用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # 本地服务无需 key
)

response = client.chat.completions.create(
    model="qwen3.5-4b",
    messages=[{"role": "user", "content": "用 Python 写一个快速排序"}],
)
print(response.choices[0].message.content)
```

同样适用于：
- **Continue.dev / Cursor** — 设置 base_url 为 `http://localhost:8000/v1`
- **Open WebUI** — 添加 OpenAI 兼容 provider
- **任何调用 openai 库的脚本** — 改 `base_url` 即可

---

## 第五步（进阶）：用 OPD 蒸馏让小模型追上大模型

这是 arle 最独特的功能，也是普通玩家最值得探索的部分。

### 什么是 OPD？

**On-Policy Distillation（在线蒸馏）** 的思路是：

```
教师模型（35B，在 serve 运行）
    ↓ 生成高质量 rollouts（推理轨迹）
学生模型（4B，在 train 运行）
    ↓ 在自己的输出上学习模仿教师
    → 性能显著提升，但只占 4B 的计算/内存
```

关键优势：**教师就是正在运行的 production server**——不需要额外部署第二个模型，也不需要提前准备数据集。学生在自己的 rollouts 上训练（on-policy），比静态蒸馏更稳定。

### 实测效果

| 指标 | 基准（4B 原始）| 蒸馏后（4B OPD）| 教师（35B）|
|---|:-:|:-:|:-:|
| **MATH-500 准确率** | 0.518 | **0.792** | 0.82 |
| 提升 | — | **+27pp** | — |
| Agent 工具调用抑制（BFCL）| 0.60 | **1.00** | — |

+27 个百分点，CI 显著分离——这是真实的能力跃升，不是统计噪声。同时蒸馏后 4B 学生学会了"拒绝不相关工具调用"（abstention 从 0.60 → 1.00），Agent 能力也提升了。

### 如何运行 OPD

#### 前置条件

- 已有 `arle serve` 在跑 35B 教师模型
- 学生模型（4B）已下载
- LoRA 适配器只需约 4GB 显存（可在消费级 GPU 上训练）

#### 启动蒸馏

```bash
# 教师先跑起来（终端 1）
arle serve --backend metal \
  --model-path mlx-community/Qwen3.6-35B-A3B-MLX-4bit \
  --port 8000

# 学生开始学习（终端 2）
arle train opd \
  --teacher-url http://localhost:8000 \
  --student-model /path/to/Qwen3.5-4B \
  --task math \       # 场景：math / code / agent
  --steps 50 \        # 训练步数（25/50 为常用节点）
  --output ./student-lora
```

详细手册：https://github.com/cklxx/arle/blob/main/docs/projects/2026-05-21-arle-opd-cuda-usage-manual.md

#### 使用蒸馏后的模型

```bash
arle serve --backend metal \
  --model-path /path/to/Qwen3.5-4B \
  --lora-path ./student-lora \
  --port 8000
```

---

## 其他值得关注的特性

### 投机解码（Speculative Decode）

默认开启，不需要配置。原理：模型自带的 NextN/MTP 头先"猜"后续几个 token，主模型一批验证——速度提升 47%，输出与 greedy 解码**逐位相同**。

```
Qwen3.6-27B: 12.3 → 18.1 tok/s (+47%)
关掉：arle serve --no-speculative ...
```

### 跨轮 KV 缓存（多轮对话提速）

arle 把上一轮的 KV 留在 GPU 上，下一轮只计算新 token 的 KV——多轮对话的效率远高于从头重算。前缀共享（radix cache）让相同前缀的多个请求复用 KV，适合批量评测场景。

### KV Recall（超长上下文记忆）

当对话超出 context window，arle 不是简单截断，而是只保留 `sink + 最近 + top-k 相关` 的 KV 块。实测在 Qwen3.6-35B 上，9.6% 的 KV 量就能解决中段 passkey 题（全量注意力才能解决）——比 sliding-window 截断强得多。

---

## 常用场景快速参考

### 场景一：普通笔记本用户，只想聊天

```bash
brew install cklxx/tap/arle
arle  # 一键启动，自动选模型
```

### 场景二：开发者，想接入 IDE 插件

```bash
arle serve --backend metal \
  --model-path mlx-community/Qwen3.5-4B-MLX-4bit \
  --port 8000
# 在 Continue / Cursor 中设置 OpenAI base_url = http://localhost:8000/v1
```

### 场景三：想提升模型在数学/代码场景的表现

```bash
# 1. 跑 35B 教师
arle serve --backend metal --model-path mlx-community/Qwen3.6-35B-A3B-MLX-4bit --port 8000

# 2. 蒸馏 4B 学生（数学场景）
arle train opd --teacher-url http://localhost:8000 \
  --student-model /path/to/Qwen3.5-4B \
  --task math --steps 50 --output ./math-lora

# 3. 用蒸馏后的模型
arle serve --backend metal --model-path /path/to/Qwen3.5-4B --lora-path ./math-lora --port 8000
```

### 场景四：一次性推理，不需要常驻服务

```bash
arle run --prompt "用 Python 实现一个二分查找" --no-tools
```

---

## 支持的模型（2026-06 现状）

| 模型家族 | Metal（Apple Silicon）| CUDA（NVIDIA）|
|---|:-:|:-:|
| Qwen3.5 全系列（0.8B/4B/9B/14B）| ✅ Stable | ✅ Stable |
| Qwen3.6（含 35B-A3B MoE）| ✅ Beta | 路线图中 |
| DeepSeek-V4-Flash | — | ✅ Stable（8×H20）|

从 HuggingFace `mlx-community` 拉 4-bit 量化版本是最省事的方式，不需要自己量化。完整支持矩阵：https://github.com/cklxx/arle/blob/main/docs/support-matrix.md

---

## 与同类工具对比

| 工具 | 语言 | Apple Silicon | 内置蒸馏 | OAI 兼容 | 多轮 KV 复用 |
|---|---|:-:|:-:|:-:|:-:|
| **arle** | Rust | ✅ | ✅ OPD | ✅ | ✅ |
| llama.cpp | C++ | ✅ | ❌ | ✅ | 部分 |
| Ollama | Go+llama.cpp | ✅ | ❌ | ✅ | ❌ |
| vLLM | Python | ❌ | ❌ | ✅ | ✅ |
| mistral.rs | Rust | ✅ | ❌ | ✅ | 部分 |

arle 的核心差异：**蒸馏训练与推理运行时完全整合**，不需要单独的训练框架，教师模型就是运行中的 server。

---

## 当前稳定性说明

arle 是 2026 年 3 月才发布的新项目，需要了解边界：

- **CUDA 推理**：Stable
- **Metal 推理（Apple Silicon）**：Beta（建议测试后投入正式使用）
- **OPD 蒸馏训练**：Beta（速度约是 HuggingFace TRL GKDTrainer 的 2× ）
- **CPU 模式**：仅供开发调试

遇到问题先查：https://github.com/cklxx/arle/blob/main/docs/troubleshooting.md

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: arle solves two real problems for local LLM enthusiasts — ① run large models on an ordinary laptop with a single command (pure Rust, no Python dependency); ② use On-Policy Distillation (OPD) to teach a small model from a large one in your specific domain. A 4B student distilled on arle lifted MATH-500 accuracy from 0.518 to 0.792 (+27pp), approaching the 35B teacher's 0.82.

GitHub: https://github.com/cklxx/arle  
⭐ 14 Stars · Pure Rust · MIT · Released 2026-03, actively maintained

---

## Why arle?

Local LLM tools already exist — llama.cpp, Ollama, vLLM. arle's differentiator is the three-in-one design:

```
One binary, three things:
  arle serve       → OpenAI-compatible HTTP server
  arle             → Local agent / REPL
  arle train opd   → On-policy distillation (teacher IS the production server)
```

No Python on the hot path — faster startup, lower memory overhead, simpler deployment. For laptop users, skipping Python environment management is a real benefit.

---

## Step 1: What Can Your Hardware Run?

### Apple Silicon Mac

Metal backend (Beta), supports: Qwen3.5 family + Qwen3.6 (including 35B-A3B MoE).

**Measured performance (M4 Pro, 48 GB, 4-bit quantized):**

| Model | Decode speed | TPOT | TTFT |
|---|---:|---:|---:|
| Qwen3.5-0.8B | **318 tok/s** | 3.2 ms | 0.17 s |
| Qwen3.5-4B | 84 tok/s | 11.9 ms | 0.82 s |
| Qwen3.5-9B | 50 tok/s | 20.0 ms | 1.45 s |
| **Qwen3.6-35B-A3B MoE** | **85 tok/s** | 11.7 ms | 1.23 s |

The MoE insight: 35B total parameters, ~3B active per token — so it decodes at 4B speed with 35B intelligence.

Approximate memory needs (4-bit):
- 4B model ≈ 3–4 GB
- 9B model ≈ 6–8 GB
- 35B-A3B MoE ≈ 20–24 GB (32 GB unified memory recommended)

### NVIDIA GPU (Linux)

- CUDA Stable: Qwen3.5 family + DeepSeek-V4-Flash
- Single card (RTX 4090 / A100): Qwen3.5 family
- Multi-card (8×H20): DeepSeek-V4-Flash at 53 tok/s

---

## Step 2: Install

### Mac (easiest)

```bash
brew install cklxx/tap/arle
```

### Mac / Linux one-liner

```bash
curl -fsSL https://github.com/cklxx/arle/releases/latest/download/install.sh | sh
```

### Linux + NVIDIA GPU (Docker, no compile)

```bash
docker run --rm --gpus all -p 8000:8000 \
  -v /path/to/Qwen3.5-4B:/model:ro \
  ghcr.io/cklxx/arle:latest \
  serve --backend cuda --model-path /model
```

Verify: `arle --doctor` — self-checks backend, hardware, and model resolution.

---

## Step 3: First Model Run

```bash
# Fastest — arle auto-picks a model
arle

# Explicit: Apple Silicon 4-bit
arle serve --backend metal \
  --model-path mlx-community/Qwen3.5-4B-MLX-4bit \
  --port 8000

# Explicit: NVIDIA
arle serve --backend cuda \
  --model-path /path/to/Qwen3.5-4B \
  --port 8000
```

Test it:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3.5-4b", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

## Step 4: Connect Any Tool via OpenAI-Compatible API

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
response = client.chat.completions.create(
    model="qwen3.5-4b",
    messages=[{"role": "user", "content": "Write a quicksort in Python"}],
)
print(response.choices[0].message.content)
```

Works out of the box with Continue.dev, Cursor, Open WebUI, and any script using the `openai` library — just change `base_url`.

---

## Step 5 (Advanced): OPD Distillation — Make the 4B Think Like the 35B

### What is OPD?

On-Policy Distillation:

```
Teacher (35B, running in arle serve)
    ↓ generates high-quality rollouts
Student (4B, running in arle train)
    ↓ trains on its own outputs, learning to match the teacher
    → meaningful capability gains at 4B compute cost
```

The key: **the teacher is the production server**. No separate deployment, no pre-built dataset.

### Measured results

| Metric | 4B baseline | 4B after OPD | 35B teacher |
|---|:-:|:-:|:-:|
| MATH-500 accuracy | 0.518 | **0.792** | 0.82 |
| Gain | — | **+27pp** | — |
| BFCL tool abstention | 0.60 | **1.00** | — |

27 percentage points on MATH-500, CI-separated from baseline. The student also learned to decline irrelevant tool calls (abstention 0.60 → 1.00).

### Running OPD

```bash
# Terminal 1: teacher serving
arle serve --backend metal \
  --model-path mlx-community/Qwen3.6-35B-A3B-MLX-4bit --port 8000

# Terminal 2: student learning
arle train opd \
  --teacher-url http://localhost:8000 \
  --student-model /path/to/Qwen3.5-4B \
  --task math \
  --steps 50 \
  --output ./student-lora

# Use the distilled model
arle serve --backend metal \
  --model-path /path/to/Qwen3.5-4B \
  --lora-path ./student-lora --port 8000
```

LoRA fits on ~4 GB VRAM — trainable on consumer cards.

---

## FAQ

**Q: My Mac has 16 GB unified memory — which model should I run?**  
Qwen3.5-4B (4-bit, ~4 GB) or Qwen3.5-9B (4-bit, ~7 GB). Both fit comfortably. For the MoE 35B you need 32 GB+.

**Q: Can I run OPD distillation on the same Mac as the teacher?**  
It depends on available VRAM. The teacher (35B MoE at 4-bit) uses ~20 GB; the student LoRA training adds memory pressure. On a 48 GB M4 Pro it works. On 16/24 GB machines, use the 4B as both teacher and student for the LoRA refinement pattern instead.

**Q: What tasks can I distill for?**  
Current `--task` options include `math`, `code`, and `agent`. The math scenario is the most validated (the +27pp result). Code and agent modes are usable but results vary.

**Q: How long does OPD training take?**  
At `--steps 50` on a consumer GPU/Apple Silicon, expect 30–90 minutes depending on hardware. Steps 25 and 50 are good checkpoints; the OPD multi-seed curve shows meaningful gains at step 25 already.

**Q: Is arle production-ready?**  
CUDA inference is Stable. Metal inference and OPD training are Beta. It's suitable for personal/research use. For production services, validate against your workload before deploying.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
