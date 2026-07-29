---
title: "Ling 3.0 Flash 初测：让人意外的编程模型——124B MoE，每 token 只激活 5B 参数"
description: "蚂蚁集团 inclusionAI 于 7 月 23 日发布 Ling 3.0 Flash：124B MoE 架构，每 token 激活 5.1B 参数，256K 上下文，在 OpenRouter 永久免费。编程性能超预期，可通过 MLX 在 Mac 统一内存上本地运行。本文整理模型规格、技术架构、Mac 本地部署和 API 接入方式。"
pubDate: "2026-07-29"
category: "Tech-Experiment"
heroImage: "../../assets/images/ling-3-0-flash-inclusionai-moe-coding-model-mac-openrouter-guide-banner.jpg"
---

7 月 23 日，蚂蚁集团旗下 inclusionAI 发布了 Ling 3.0 Flash——从数字上看，这是一个 124B 参数的大模型；但由于 MoE 架构每次推理只激活约 5.1B 参数，实际运行速度远比参数量暗示的要快，而编程能力让第一批测试者感到意外。

---

## 一、模型规格

| 属性 | 值 |
|---|---|
| 总参数量 | **124B** |
| 推理时激活参数 | **5.1B / token** |
| 架构 | Mixture-of-Experts（MoE） |
| 上下文长度 | **256K tokens**（262,144） |
| 最大输出 | 32,768 tokens |
| 推理模式 | 默认开启（可控制 thinking 深度） |
| 开源协议 | MIT（代码仓库） |
| OpenRouter 价格 | **永久免费** |

"Flash" 这个后缀在 Ling 系列里意味着**即时响应优先**——相对于同系列 Ring（更深的推理）和 1T 旗舰，Flash 追求低延迟和高吞吐，适合需要快速响应的 Agent 场景。

Ling 3.0 Flash 对比前代 Ling 2.6 Flash（104B 总参数，7.4B 激活），总参数量增加了 20B，但每 token 激活参数反而从 7.4B 降到 5.1B——换句话说，**同样的算力换来了更多的专家容量，但推理开销更低**。

---

## 二、背后的公司：蚂蚁集团 inclusionAI

inclusionAI 是蚂蚁集团（Ant Group，支付宝母公司）旗下的 AI 研究团队，过去一年陆续开源了：

- **Ling 系列**：MoE 语言模型，从 16.8B（lite）到 1T（旗舰）
- **Ring 系列**：深度推理版本，搭配 RL 框架 KPop 训练
- **LLaDA**：扩散语言模型系列
- **AWorld**：Agent 协作框架

Ling 3.0 Flash 对应的技术报告尚未单独发布，但其架构延续自 Ling 2.6（arXiv:2606.15079），核心创新包括：

- **混合线性注意力**（Lightning Attention + MLA）：加速长上下文训练和解码
- **Evolutionary Chain-of-Thought**：优化每 token 产出的信息密度
- **Linguistic Unit Policy Optimization（LUPO）**：RL 对齐优化

---

## 三、为什么编程能力超预期

MoE 模型在编程任务上有一个结构性优势：**稀疏激活允许模型学习更专业化的"专家子网络"**——不同的代码语言、不同的任务类型（调试/生成/重构）可能路由到不同的专家组。这在同等激活算力下比 Dense 模型有更大的参数空间。

前代 Ling 2.6 Flash 的 SWE-bench Verified 得分和 HumanEval 数据显示了该系列对 coding 任务的持续优化。从 OpenRouter 的实际使用量来看，**Kilo Code**（一个 VS Code/JetBrains AI 编程插件）是 Ling 3.0 Flash 的最大流量来源，消耗了数百亿 tokens——这是真实编程 workload 的间接验证。

---

## 四、在 Mac 上运行

### 方式 A：通过 OpenRouter API（最简单）

Ling 3.0 Flash 在 OpenRouter 完全免费，OpenAI 兼容接口：

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "inclusionai/ling-3.0-flash:free",
    "messages": [
      {"role": "user", "content": "写一个 Python 函数，用二分搜索在旋转排序数组中查找目标值"}
    ],
    "reasoning": {"max_tokens": 2000}
  }'
```

`"reasoning"` 参数控制 think 深度，设为 `{"effort": "low"}` 可加快响应。

在 Mac 上用 Python：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key",  # 注册免费获取
)

response = client.chat.completions.create(
    model="inclusionai/ling-3.0-flash:free",
    messages=[
        {"role": "user", "content": "帮我 review 这段 TypeScript，找出所有潜在的 null 解引用"}
    ],
)
print(response.choices[0].message.content)
```

### 方式 B：本地 MLX（Mac 统一内存，完全离线）

Ling 2.6 Flash 已有 `mlx-community` 社区量化版本，支持 Mac Apple Silicon 直接运行：

```bash
# 安装 mlx-lm
source ~/venvs/ml/bin/activate
pip install mlx-lm

# 加载并运行（Ling 2.6 Flash，4-bit 量化，约 52GB 统一内存）
python -m mlx_lm.generate \
  --model mlx-community/Ling-2.6-flash-mlx-4bit \
  --prompt "Implement a Rust function that efficiently finds all primes up to n using the Sieve of Eratosthenes"
```

Ling 3.0 Flash 的 MLX 版本目前社区正在制作中（模型刚发布 6 天），预计数天内出现在 `mlx-community` 组织下。届时 124B × 4bit ≈ **62GB 统一内存**，M3 Ultra（192GB）或 M4 Max（128GB）可运行。

### 内存需求参考

| 量化精度 | 所需统一内存 | 适用 Mac |
|---|---|---|
| FP16 | ~248GB | 不可行 |
| INT8 | ~124GB | M3 Ultra（192GB） |
| **INT4（推荐）** | **~62GB** | M4 Max（128GB）/ M3 Ultra（192GB） |
| INT2 | ~31GB | M4 Pro（48GB）及以上 |

MoE 的统一内存优势：**只需要把激活专家的权重保持在 GPU core 附近**，非激活专家可以放在统一内存的 CPU 侧。相比 Dense 模型，MoE 在统一内存架构下更能发挥优势。

---

## 五、GitHub / HuggingFace 资源

| 资源 | 地址 |
|---|---|
| 官方 GitHub | `github.com/inclusionAI/Ling` |
| HuggingFace 组织 | `huggingface.co/inclusionAI` |
| Ling 2.6 Flash（稳定版） | `inclusionAI/Ling-2.6-flash` |
| Ling 2.6 Flash MLX | `mlx-community/Ling-2.6-flash-mlx-4bit` |
| Ling 2.6 Flash GGUF | `ljupco/Ling-2.6-flash-GGUF` |
| OpenRouter（3.0 Flash 免费） | `openrouter.ai/inclusionai/ling-3.0-flash:free` |
| 技术报告（2.6） | arXiv:2606.15079 |

Ling 3.0 Flash 的官方 HuggingFace 模型卡尚未发布（可能很快就来），目前最快的上手方式是 OpenRouter API。

---

## 六、与前代比较

| | Ling 2.6 Flash | **Ling 3.0 Flash** |
|---|---|---|
| 总参数 | 104B | **124B** |
| 激活参数 | 7.4B | **5.1B** |
| 上下文 | 256K | 256K |
| 推理支持 | 是 | 是（默认开启） |
| OpenRouter 价格 | $0.01/M 输入 | **永久免费** |
| HuggingFace 模型卡 | 有 | 待发布 |

从 2.6 到 3.0，inclusionAI 的方向很清晰：**用更多专家换更低的激活开销**，在不提高推理成本的前提下扩大模型容量。

---

## 小结

Ling 3.0 Flash 是目前免费可用的最高参数量 MoE 编程模型之一——OpenRouter 永久免费，256K 长上下文，推理默认开启。对于需要处理大型代码库（50K+ tokens）的场景，这个上下文窗口本身就有价值。

在 Mac 上接入：OpenRouter API 今天就能用；本地 MLX 版本等社区量化出来后，M4 Max 以上的机器可以完整运行。

---

<!--EN-->

## Ling 3.0 Flash First Test: A Surprisingly Good Coding Model — 124B MoE, 5B Active Parameters per Token

On July 23, inclusionAI (Ant Group's AI research arm) released Ling 3.0 Flash. On paper it's a 124B-parameter model; in practice, because MoE architecture only activates ~5.1B parameters per token at inference time, it runs far faster than the raw parameter count suggests — and the coding performance has surprised early testers.

---

## Model Specs

| Property | Value |
|---|---|
| Total parameters | **124B** |
| Active parameters at inference | **5.1B / token** |
| Architecture | Mixture-of-Experts (MoE) |
| Context length | **256K tokens** (262,144) |
| Max output | 32,768 tokens |
| Reasoning | Default enabled (controllable) |
| License | MIT |
| OpenRouter price | **Free** |

"Flash" in the Ling family means instant-response priority — lower latency and higher throughput versus the Ring (deeper reasoning) and 1T flagship variants. Ling 3.0 Flash compared to Ling 2.6 Flash (104B total, 7.4B active): total params increased by 20B but active params per token *decreased* from 7.4B to 5.1B — more expert capacity, lower inference cost per token.

---

## Who Built It

inclusionAI is Ant Group's AI research division. Their open-source releases in the past year:

- **Ling series**: MoE language models, from 16.8B (lite) to 1T (flagship)
- **Ring series**: deeper reasoning variants, trained with RL framework KPop
- **LLaDA**: diffusion language model series
- **AWorld**: multi-agent coordination framework

The Ling 3.0 Flash technical report hasn't been published separately yet, but the architecture continues from Ling 2.6 (arXiv:2606.15079). Key innovations include hybrid linear attention (Lightning Attention + MLA), Evolutionary Chain-of-Thought for token efficiency, and LUPO (Linguistic Unit Policy Optimization) for RL alignment.

---

## Why the Coding Performance Surprised People

MoE gives a structural advantage for coding tasks: **sparse activation lets the model learn specialized expert subnetworks** — different programming languages, different task types (debugging, generation, refactoring) can route to different expert groups. This gives more parameter capacity per unit of active compute than a dense model.

The biggest real-world signal: on OpenRouter, **Kilo Code** (an AI coding agent for VS Code/JetBrains) is the top traffic source for Ling 3.0 Flash, consuming hundreds of billions of tokens. That's production coding workloads at scale.

---

## Running on Mac

### Option A: OpenRouter API (easiest)

Free, no quota limits stated:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key",  # free signup
)

response = client.chat.completions.create(
    model="inclusionai/ling-3.0-flash:free",
    messages=[
        {"role": "user", "content": "Review this TypeScript, find all potential null dereferences"}
    ],
)
print(response.choices[0].message.content)
```

### Option B: Local MLX (Mac Unified Memory, fully offline)

Ling 2.6 Flash already has MLX-quantized community builds running natively on Apple Silicon:

```bash
pip install mlx-lm

python -m mlx_lm.generate \
  --model mlx-community/Ling-2.6-flash-mlx-4bit \
  --prompt "Implement a Rust function for prime sieve..."
```

Ling 3.0 Flash MLX builds are in progress (model released 6 days ago). Once available, expected memory requirements at 4-bit: **~62GB unified memory** — runnable on M4 Max (128GB) or M3 Ultra (192GB).

### Why MoE Fits Mac's Unified Memory Architecture

Mac unified memory pools CPU and GPU memory into one physical bank. For MoE models, **only the active expert weights need to stay in GPU-adjacent memory during inference**; inactive experts can sit in the CPU-accessible region without a penalty. This makes MoE architectures particularly well-suited to unified memory systems compared to datacenter discrete-GPU setups.

---

## Resources

| Resource | URL |
|---|---|
| Official GitHub | `github.com/inclusionAI/Ling` |
| HuggingFace org | `huggingface.co/inclusionAI` |
| Ling 2.6 Flash (stable) | `inclusionAI/Ling-2.6-flash` |
| MLX version (2.6) | `mlx-community/Ling-2.6-flash-mlx-4bit` |
| GGUF version (2.6) | `ljupco/Ling-2.6-flash-GGUF` |
| OpenRouter (3.0 free) | `openrouter.ai/inclusionai/ling-3.0-flash:free` |
| Technical report | arXiv:2606.15079 |

---

## Summary

Ling 3.0 Flash is currently one of the highest-parameter free coding models available. Free on OpenRouter, 256K context, reasoning enabled by default. For anyone working with large codebases (50K+ tokens), that context window alone is valuable.

On Mac: OpenRouter API works today. Local MLX builds will follow within days — once available, M4 Max and above can run it fully offline.
