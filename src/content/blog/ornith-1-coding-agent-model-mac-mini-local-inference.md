---
title: "Ornith-1.0：自改进 Coding Agent 模型，9B 打 35B，Mac mini 本地跑 60 t/s"
titleEn: "Ornith-1.0: Self-Improving Coding Agent Model — 9B Beats 35B, 60 t/s on Mac mini"
description: "deepreinforce-ai 开源 Ornith-1.0：RL 同时优化脚手架和解答，9B 在 Terminal-Bench 和 NL2Repo 上碾压 Qwen3.5-35B，35B MoE 超过 Qwen3.5-397B。APEX-I-Compact MTP GGUF + 16GB Mac mini 实测 60 t/s，总结/排版远超原版模型，无无限重复问题。"
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["本地模型", "Coding Agent", "Apple Silicon", "Mac mini", "GGUF", "MLX", "SWE-bench", "自改进训练", "开源LLM", "llama.cpp"]
heroImage: "../../assets/images/ornith-1-coding-agent-model-mac-mini-local-inference-banner.jpg"
---

> **GitHub**：[deepreinforce-ai/Ornith-1](https://github.com/deepreinforce-ai/Ornith-1) · **许可**：MIT  
> **博客**：[deep-reinforce.com/ornith.html](https://deep-reinforce.com/ornith.html)  
> **模型**：9B Dense / 35B MoE / 397B MoE · **上下文**：256K tokens  
> **底座**：Gemma 4（9B）+ Qwen 3.5（35B / 397B）

---

## 一句话理解

Ornith-1.0 不只训练"怎么答题"，它还训练"怎么找到答案的路径"——用 RL 同时优化解题脚手架（scaffold）和解答本身。结果是一个 9B 模型在多个编程基准上打赢 35B，35B 打赢 397B 的现象。

---

## 核心创新：自改进脚手架训练

大多数 Coding LLM 的 RL 训练目标是：给定问题，输出正确解答，奖励正确率。

Ornith-1.0 的训练目标是：**同时优化生成解答的脚手架**。脚手架是 Agent 在解题过程中的控制流——搜索哪些文件、按什么顺序尝试、什么时候回溯。

通过联合优化，模型学会了**更好的搜索轨迹**，而不只是记住答案形式。这解释了为什么它在需要多步推理和代码库导航的基准（NL2Repo、SWE Atlas）上的增益特别大——这些任务恰好最依赖脚手架质量。

---

## Benchmark 数据

### Ornith-1.0-9B vs 更大模型

| 基准 | Ornith-9B | Qwen3.5-9B | **Qwen3.5-35B** | Gemma4-31B |
|---|---|---|---|---|
| Terminal-Bench 2.1 (Terminus-2) | **43.1** | 21.3 | 41.4 | 42.1 |
| Terminal-Bench 2.1 (Claude Code) | **40.6** | 18.9 | 38.9 | — |
| SWE-bench Verified | **69.4** | 53.2 | 70.0 | 44.2 |
| SWE-bench Pro | 42.9 | 31.3 | **44.6** | 27.6 |
| NL2Repo | **27.2** | 16.2 | 20.5 | 10.3 |
| SWE Atlas QnA | **17.9** | 9.2 | 13.2 | — |

9B 在 Terminal-Bench 和 NL2Repo 上超过 Qwen3.5-35B（参数量 3.9 倍大）。

### Ornith-1.0-35B vs 旗舰模型

| 基准 | Ornith-35B | Qwen3.5-35B | Qwen3.6-35B | **Qwen3.5-397B** |
|---|---|---|---|---|
| Terminal-Bench 2.1 (Terminus-2) | **64.2** | 41.4 | 52.5 | 53.5 |
| Terminal-Bench 2.1 (Claude Code) | **62.8** | 38.9 | 49.2 | 48.6 |
| SWE-bench Verified | 75.6 | 70.0 | 73.4 | **76.4** |
| SWE-bench Pro | 50.4 | 44.6 | 49.5 | **51.6** |
| NL2Repo | 34.6 | 20.5 | 29.4 | **36.8** |
| SWE Atlas QnA | **37.1** | 13.2 | 15.5 | 20.4 |

35B MoE 在 Terminal-Bench 上全面超过 Qwen3.5-397B（参数量 11 倍大）。

---

## 实测体验：两个关键优势

### 1. 无无限重复

很多开源 Coding 模型在长上下文任务里会陷入重复生成——同一段代码或同一句话反复输出，直到撞上 token 上限。Ornith-1.0 在同类场景测试中没有出现这个问题。

原因可能在于脚手架训练：模型学会了"什么时候该停止当前搜索方向、转到下一个"，而不是死守一个错误路径循环。

### 2. 总结/排版质量出众

资料整理和文档总结类任务，Ornith-1.0 的输出质量远超同参数量竞品——结构清晰、层次分明、不丢关键信息。这也是脚手架优化的副产品：模型学会了如何有结构地组织输出，而不是把所有内容堆在一起。

---

## 四种模型规格

| Checkpoint | 架构 | 格式 | 适用场景 |
|---|---|---|---|
| Ornith-1.0-9B | Dense (~9B) | BF16 | 单 GPU 训练 / 微调 |
| Ornith-1.0-9B-GGUF | Dense (~9B) | GGUF 量化 | llama.cpp / Ollama 本地推理 |
| Ornith-1.0-35B | MoE (35B) | BF16 | 全精度多 GPU 推理 |
| Ornith-1.0-35B-FP8 | MoE (35B) | FP8 | 低显存 FP8 卡 |
| Ornith-1.0-35B-GGUF | MoE (35B) | GGUF 量化 | llama.cpp / Ollama |
| Ornith-1.0-397B | MoE (397B) | BF16 | 多 GPU 节点全精度 |

35B 是 MoE 架构（混合专家）——激活参数远少于总参数，推理速度比同标称规模的 Dense 模型快很多，是本地运行的首选。

---

## Mac mini 安装指南

两条路径，根据需求选一条。

### 路径 A：mlx-dspark + Ornith-9B（推荐 16GB Mac mini）

**特点**：纯 Apple Silicon 原生 MLX，speculative decoding 加速，运行 9B 模型，内存占用低。

```bash
# 安装
pip install mlx-dspark

# 启动 API 服务（OpenAI + Anthropic 双协议）
mlx-dspark serve --model mlx-community/Ornith-1.0-9B-8bit

# 让 Claude Code 用这个本地模型
mlx-dspark claude
```

**性能**（M4 Pro，8-bit 量化）：
- 代码生成：~61 tok/s（正常），~93 tok/s（编辑已有代码时 copy-heavy 场景）
- 数学推理：2.44x 加速
- 与 Anthropic API 完全兼容——`mlx-dspark claude` 把 Claude Code 无缝指向本地，退出后自动恢复云端配置

```bash
# 可选参数
mlx-dspark serve \
  --model mlx-community/Ornith-1.0-9B-8bit \
  --max-batch 4 \      # 并发 4 请求
  --kv-bits 8 \        # 压缩 KV cache（长上下文必备）
  --no-thinking        # 关闭 <think> 块（更快，适合简单任务）
```

---

### 路径 B：llama.cpp + APEX-I-Compact GGUF + MTP（35B，需更多内存）

**特点**：跑 35B MoE，通过层卸载在 16GB 统一内存上运行，MTP（Multi-Token Prediction）加速推理。

**用户实测配置**：16GB Mac mini，20 层卸载到 GPU，64K 上下文，**平均 60 t/s**。

#### 安装 llama.cpp

```bash
# Homebrew（推荐，自动编译 Metal 加速）
brew install llama.cpp

# 或手动编译（获取最新 MTP 支持）
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DLLAMA_METAL=ON
cmake --build build --config Release -j$(sysctl -n hw.ncpu)
```

#### 下载 APEX-I-Compact GGUF

```bash
# 安装 huggingface-cli
pip install huggingface_hub

# 下载 APEX-I 量化版本（35B Compact Q4_K_M）
huggingface-cli download \
  APEX-I/Ornith-1.0-35B-Compact-GGUF \
  --local-dir ~/models/ornith-35b \
  --include "*.Q4_K_M.gguf"
```

#### 启动服务（复现用户 60 t/s 配置）

```bash
llama-server \
  -m ~/models/ornith-35b/Ornith-1.0-35B-Q4_K_M.gguf \
  -ngl 20 \          # 20 层卸载到 GPU（Metal）
  -c 65536 \         # 64K 上下文
  --mtp-draft 2 \    # Multi-Token Prediction：每步预测 2 个额外 token
  -t $(sysctl -n hw.ncpu) \  # CPU 线程数
  --port 8080 \
  --host 0.0.0.0
```

**参数说明**：

| 参数 | 含义 | 调整建议 |
|---|---|---|
| `-ngl 20` | GPU 层数 | 16GB Mac：20-24 层；24GB Mac：32+ 层 |
| `-c 65536` | 上下文窗口 | 越大越占内存，从 32K 开始测试 |
| `--mtp-draft 2` | MTP 预测步数 | 2-4，越大越快但可能降质量 |
| `-t 8` | CPU 线程数 | 一般设为物理核数 |

#### 连接到 Claude Code / OpenAI 工具

```bash
# 设置环境变量（指向本地服务）
export OPENAI_BASE_URL="http://localhost:8080/v1"
export OPENAI_API_KEY="local"

# 或在任何工具里配置：
# Base URL: http://localhost:8080/v1
# Model: ornith-35b（llama-server 自动暴露已加载的模型名）
```

---

### 路径 C：Ollama（最简单，适合快速试用）

```bash
# 安装 Ollama
brew install ollama
ollama serve &

# 拉取并运行 Ornith GGUF
ollama pull hf.co/deepreinforce-ai/Ornith-1.0-9B-GGUF
ollama run hf.co/deepreinforce-ai/Ornith-1.0-9B-GGUF

# 也可以拉取 35B（需要更多内存）
ollama pull hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF
```

---

## 推理参数

Ornith-1.0 是推理模型，输出默认包含 `<think>...</think>` 块。

**推荐采样参数**（复现基准测试设置）：
```
temperature = 1.0    # 基准复现
top_p       = 0.95
top_k       = 20
```

**日常使用推荐**（更稳定）：
```
temperature = 0.6
top_p       = 0.95
top_k       = 20
```

**关闭思考链**（速度优先）：
- mlx-dspark：`--no-thinking`
- llama-server：系统提示里加 `/no_think`

---

## 用 vLLM 在 GPU 服务器跑（参考）

```bash
pip install vllm>=0.19.1

# 35B MoE，单 80GB A100（或 2x 40GB）
vllm serve deepreinforce-ai/Ornith-1.0-35B \
  --served-model-name Ornith-1.0 \
  --tensor-parallel-size 2 \
  --host 0.0.0.0 --port 8000 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --reasoning-parser qwen3 \
  --trust-remote-code
```

9B Dense 单张 80GB 卡即可，35B MoE 需要 2 张 40GB（或 1 张 80GB，注意 MoE 激活内存峰值）。

---

## 与 mlx-dspark 的关系

[mlx-dspark](https://github.com/ARahim3/mlx-dspark) 是专门针对 Apple Silicon 的 speculative decoding 加速库，原生支持 Ornith-1.0：

| 模型 | 加速方法 | 最优加速比 | 推荐场景 |
|---|---|---|---|
| Ornith-1.0-9B (8-bit) | DSpark | 2.44× 数学，3.6× 代码编辑 | Mac 本地主力 |
| Gemma-4 12B (8-bit) | DSpark | 2.11× 代码 | 视觉任务 |
| Qwen3-14B (8-bit) | DSpark | 1.92× 代码 | 中文场景 |

mlx-dspark 的关键特性：同一个端口同时暴露 OpenAI API 和 Anthropic Messages API，`mlx-dspark claude` 可以直接把 Claude Code 切换到本地模型，退出后自动恢复。

---

## 核心判断

Ornith-1.0 最值得关注的不是某一个基准分数，而是它的**参数效率曲线异常**——9B 打赢 35B，35B 打赢 397B，这在开源 Coding 模型里很罕见。

原因可以追溯到训练方式：用 RL 优化搜索轨迹而不只是最终答案，让小模型学会了"把精力用对地方"，而不是靠参数量堆蛮力。

对 Mac mini 用户来说，**路径 B（APEX-I-Compact GGUF + MTP + 20 层卸载）** 是目前性价比最高的本地推理方案：35B MoE 量化后在 16GB 统一内存上跑出 60 t/s，配合 64K 上下文，已经足够驱动大部分 Agentic Coding 工作流。

---

## 参考资源

- **GitHub**：[deepreinforce-ai/Ornith-1](https://github.com/deepreinforce-ai/Ornith-1)
- **博客**：[deep-reinforce.com/ornith.html](https://deep-reinforce.com/ornith.html)
- **HuggingFace 模型**：deepreinforce-ai/Ornith-1.0-{9B,35B,397B}
- **APEX-I 量化版**：APEX-I/Ornith-1.0-35B-Compact-GGUF（HuggingFace）
- **mlx-dspark**：[ARahim3/mlx-dspark](https://github.com/ARahim3/mlx-dspark) — Apple Silicon 投机解码加速
- **llama.cpp**：[ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

© 2026 Author: Mycelium Protocol
