---
title: "Ornith-1.0：自搭脚手架 AI，9B 打赢 Gemma4-31B，397B 超越 Claude Opus 4.7"
titleEn: "Ornith-1.0 Developer Guide: Self-Scaffolding AI That Beats Claude Opus 4.7 — Across 9B to 397B"
description: "DeepReinforce 开源 Ornith-1.0 系列：9B / 35B MoE / 397B MoE，专攻 Agentic Coding。核心创新是自搭脚手架 RL——让模型学会给自己写工作流，而不是人工设计固定 harness。397B 在 Terminal-Bench 2.1 和 SWE-Bench Verified 双超 Claude Opus 4.7，35B MoE 反超参数大 10 倍的 Qwen3.5-397B。"
descriptionEn: "DeepReinforce open-sources Ornith-1.0: 9B / 35B MoE / 397B MoE models specialized for agentic coding. The key innovation is self-scaffolding RL — the model learns to write its own orchestration harness instead of using human-designed fixed scaffolds. The 397B beats Claude Opus 4.7 on both Terminal-Bench 2.1 and SWE-Bench Verified; the 35B MoE outperforms the 10× larger Qwen3.5-397B on Terminal-Bench."
pubDate: "2026-06-27"
updatedDate: "2026-06-27"
category: "Tech-News"
tags: ["Agentic Coding", "开源模型", "强化学习", "代码智能体", "MoE", "Ornith", "自主AI", "DeepReinforce"]
heroImage: "../../assets/images/ornith-1-agentic-coding-self-scaffold-guide-banner.jpg"
---

> **BLUF**：Ornith-1.0 不是又一个通用大模型，它是专为「让 AI 自己写代码、自己调 bug、自己管工具调用流程」这件事而训练的。它最独特的地方在于：训练时不用人工设计固定的 harness/scaffold，让模型自己学会给自己搭脚手架。MIT 开源，全尺寸可用，OpenAI 接口兼容。

---

## 原始资源

GitHub（MIT 开源）：https://github.com/deepreinforce-ai/Ornith-1 （92 ⭐）

项目博客：https://deep-reinforce.com/ornith.html

HuggingFace 模型：https://huggingface.co/deepreinforce-ai/

团队主页：https://github.com/deepreinforce-ai （也做过 CUDA-L1、CUDA-L2 RL 优化）

---

## 一、Ornith-1.0 是什么？

Ornith（取自希腊语「鸟」）是 DeepReinforce 团队专为 **Agentic Coding** 构建的开源模型系列。这个团队之前做过 CUDA-L1（305⭐，用对比 RL 优化 CUDA kernel）和 CUDA-L2（443⭐，RL 超越 cuBLAS 矩阵乘法），在代码 × 强化学习的交叉方向有积累。

**Ornith-1.0 提供四个尺寸**，全部 MIT 许可：

| 模型 | 类型 | 精度 | 适用场景 |
|---|---|---|---|
| Ornith-1.0-9B | Dense 9B | bf16 / GGUF | 单卡 / 边缘设备 / 本地 |
| Ornith-1.0-35B | MoE 35B（激活约 3B）| bf16 / FP8 / GGUF | 单台多卡服务器 |
| Ornith-1.0-397B | MoE 397B | bf16 / FP8 | 多机多卡节点 |

**后训练基座**：Gemma 4 系列（9B 版）和 Qwen 3.5（35B / 397B 版）

---

## 二、各尺寸性能对比

### Ornith-1.0-9B：9B 打赢 31B

| 基准测试 | Ornith-9B | Qwen3.5-9B | Qwen3.5-35B | Gemma4-12B | Gemma4-31B |
|---|:-:|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 | **43.1** | 21.3 | 41.4 | 21.0 | 42.1 |
| SWE-Bench Verified | **69.4** | 53.2 | 70.0 | 44.2 | 52.0 |
| SWE-Bench Pro | 42.9 | 31.3 | 44.6 | 27.6 | 35.7 |
| NL2Repo | **27.2** | 16.2 | 20.5 | 10.3 | 15.5 |

**亮点**：9B Ornith 在 Terminal-Bench 上超过 Gemma4-31B（43.1 vs 42.1），SWE-Bench Verified 接近 Qwen3.5-35B（69.4 vs 70.0），是当前开源 9B 级别在 agentic coding 上的最强基准。

### Ornith-1.0-35B MoE：35B 打赢 400B

| 基准测试 | Ornith-35B | Qwen3.5-35B | Qwen3.6-35B | Gemma4-31B | **Qwen3.5-397B** |
|---|:-:|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 | **64.2** | 41.4 | 52.5 | 42.1 | **53.5** |
| SWE-Bench Verified | **75.6** | 70.0 | 73.4 | 52.0 | 76.4 |
| SWE-Bench Pro | 50.4 | 44.6 | 49.5 | 35.7 | 51.6 |

**亮点**：Ornith-35B MoE 在 Terminal-Bench 2.1 上反超 **参数量大 10 倍** 的 Qwen3.5-397B（64.2 vs 53.5），同时 SWE-Bench Verified 接近 397B 水平（75.6 vs 76.4）。

### Ornith-1.0-397B MoE：超越 Claude Opus 4.7

| 基准测试 | Ornith-397B | Qwen3.5-397B | **Claude Opus 4.7** | Claude Opus 4.8 |
|---|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 (Terminus-2) | **77.5** | 53.5 | 70.3 | 85.0 |
| Terminal-Bench 2.1 (Claude Code) | **78.2** | 48.6 | 69.7 | 78.9 |
| SWE-Bench Verified | **82.4** | 76.4 | 80.8 | 87.6 |
| SWE-Bench Pro | 62.2 | 51.6 | 64.3 | 69.2 |
| SWE-Bench Multilingual | **78.9** | 69.3 | — | — |
| NL2Repo | 48.2 | 36.8 | — | 69.7 |
| ClawEval Avg | 77.1 | 70.7 | 78.2 | — |

**亮点**：397B 在 Terminal-Bench 2.1 和 SWE-Bench Verified 上双超 Claude Opus 4.7（分别 +7.2 和 +1.6），是当前开源最强 agentic coding 模型之一。

---

## 三、核心创新：自搭脚手架（Self-Scaffolding RL）

大多数 AI 代码 benchmark 分数，并不只是模型能力，还包括**人工设计的 harness/scaffold**——也就是工具调用顺序、报错重试逻辑、任务拆解流程。不同的 harness 设计，分数差异会很大。

**Ornith 的思路**：把 scaffold 也交给模型，用 RL 一起训练。

```
传统做法：
  [固定 harness] → 模型生成解题方案 → 验证器打分 → 只优化方案

Ornith 做法：
  任务 + 上一轮 scaffold → 模型提出新 scaffold
  新 scaffold + 任务 → 模型生成解题方案
  奖励同时回传给 scaffold 和方案 → 两者都被优化
```

这样的训练反馈回路，让每个任务类别自然涌现出专属的工作流策略，而不需要工程师反复手调 harness。

### 防 Reward Hacking：三层防护

让模型自己写 scaffold，作弊风险（reward hacking）更高——CUDA-L1 时团队就吃过亏（被 RL 钻了计时漏洞，刷出假加速）。这次 Ornith 的方案是三层防护：

**第一层：环境边界固化**
- 环境、工具表面、测试隔离不可被模型修改
- 模型只能演化 scaffold 内部策略（内存管理、错误处理、编排逻辑），无法碰外层验证机制

**第二层：确定性监控器**
- 逐 token 检测：读取隐藏路径、修改验证脚本、调用越界工具 → 直接判零分，排除 advantage 计算

**第三层：冻结大模型裁判**
- 在验证器之上额外设一个冻结的大模型裁判（veto 权）
- 专门针对「在允许工具范围内作弊」的意图级别博弈

### 异步 RL 训练（Pipeline-RL）

长 rollout 的 off-policy 问题：早期生成的 token 在梯度更新前已经过时。Ornith 用**陈旧度加权（Staleness Weight）**解决：

- Token 按年龄逐步降权
- 超过阈值的 token 直接丢弃，不参与梯度计算
- GRPO loss 乘以 staleness weight

这让训练可以在模型推理的同时进行参数更新，不需要等待整轮 rollout 完成才更新。

---

## 四、不同开发者的选型建议

### 个人开发者 / 笔记本 → 9B GGUF

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取 Ornith-1.0-9B（GGUF 量化版，约 5-8GB）
ollama pull deepreinforce-ai/Ornith-1.0-9B-GGUF

# 开始聊天
ollama run deepreinforce-ai/Ornith-1.0-9B-GGUF

# 或者通过 llama.cpp 直接运行
llama-cli -hf deepreinforce-ai/Ornith-1.0-9B-GGUF -p "Fix the bug in this Python code: ..."
```

**适合**：本地调试、代码补全、代码审查、单 GPU 推理（需 8-12GB VRAM）

### 小型 GPU 集群 → 35B MoE

35B MoE 激活参数约 3B，推理开销低于 Dense 35B。

```bash
# vLLM 部署（2-4 张 GPU）
MODEL=deepreinforce-ai/Ornith-1.0-35B-FP8  # FP8 节省显存

vllm serve $MODEL \
    --served-model-name Ornith-1.0 \
    --tensor-parallel-size 4 \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 262144 \
    --gpu-memory-utilization 0.90 \
    --enable-prefix-caching \
    --enable-auto-tool-choice --tool-call-parser qwen3_xml \
    --reasoning-parser qwen3 \
    --trust-remote-code
```

**适合**：团队内部代码 Agent 服务、CI/CD 集成自动修 bug、代码审查流水线

### 生产旗舰 → 397B MoE

```bash
# 8x H100 节点
MODEL=deepreinforce-ai/Ornith-1.0-397B-FP8  # FP8 版显存减半

vllm serve $MODEL \
    --served-model-name Ornith-1.0 \
    --tensor-parallel-size 8 \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 262144 \
    --gpu-memory-utilization 0.90 \
    --enable-prefix-caching \
    --enable-auto-tool-choice --tool-call-parser qwen3_xml \
    --reasoning-parser qwen3 \
    --trust-remote-code
```

**适合**：替代 Claude Opus 的 Agentic Coding 任务、SWE-Bench 级别的真实代码仓库修改

---

## 五、快速上手代码

### 方案一：Transformers 本地推理（9B）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# transformers >= 5.8.1 是必须条件
model_name = "deepreinforce-ai/Ornith-1.0-9B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, dtype="auto", device_map="auto"
)

messages = [
    {"role": "user", "content": "Write a Python function to check if a string is a palindrome, with tests."}
]
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

generated = model.generate(
    **inputs,
    max_new_tokens=2048,
    do_sample=True,
    temperature=0.6,
    top_p=0.95,
    top_k=20,
)
output_ids = generated[0][inputs.input_ids.shape[1]:]

# 模型输出包含 <think>...</think> 推理过程 + 最终答案
content = tokenizer.decode(output_ids, skip_special_tokens=True)

# 分离推理链和答案
if "</think>" in content:
    reasoning, answer = content.split("</think>", 1)
    reasoning = reasoning.replace("<think>", "").strip()
    answer = answer.strip()
    print("推理过程:", reasoning[:200], "...")
    print("\n最终答案:", answer)
else:
    print(content)
```

### 方案二：OpenAI 兼容 API（适配所有尺寸）

```python
from openai import OpenAI

# 指向本地 vLLM 或 SGLang 服务
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

response = client.chat.completions.create(
    model="Ornith-1.0",
    messages=[
        {"role": "user", "content": "Debug this Python code and explain what was wrong:\n\ndef factorial(n):\n    if n == 0: return 1\n    return n * factorial(n)  # bug here"}
    ],
    temperature=0.6,
    top_p=0.95,
    max_tokens=4096,
)

# reasoning_content = <think> 推理过程
# content = 最终回答
msg = response.choices[0].message
print("推理:", getattr(msg, "reasoning_content", "")[:300])
print("答案:", msg.content)
```

### 方案三：工具调用（Tool Calling / Function Calling）

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command and return stdout/stderr",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"],
            },
        },
    },
]

messages = [{"role": "user", "content": "Find and fix all type errors in my Python project."}]

# 多轮工具调用循环
while True:
    response = client.chat.completions.create(
        model="Ornith-1.0",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.6,
        max_tokens=8192,
    )

    msg = response.choices[0].message
    messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})

    if not msg.tool_calls:
        print("完成！最终答案：", msg.content)
        break

    # 执行工具并将结果回传
    for tc in msg.tool_calls:
        result = execute_tool(tc.function.name, tc.function.arguments)  # 你的工具执行逻辑
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result),
        })
```

### 方案四：接入 MCP（Model Context Protocol）

Ornith-1.0 原生支持 MCP，可以直接挂 Claude Code、VSCode、Cursor 等工具链：

```python
import os
from openai import OpenAI

# MCP 服务器暴露为工具列表
# 用任意 MCP-to-OpenAI 适配器（如 mcp-proxy）转换后接入
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "EMPTY"),
)

# MCP 工具定义示例（文件系统 + 代码执行）
tools = [
    {"type": "function", "function": {
        "name": "mcp__filesystem__read_file",
        "description": "Read file contents via MCP filesystem server",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "mcp__code_runner__execute",
        "description": "Execute code and return output",
        "parameters": {"type": "object", "properties": {
            "code": {"type": "string"},
            "language": {"type": "string", "enum": ["python", "javascript", "bash"]}
        }, "required": ["code", "language"]}
    }},
]

# 使用方式与普通工具调用相同
response = client.chat.completions.create(
    model="Ornith-1.0",
    messages=[{"role": "user", "content": "Read main.py and run it, then fix any errors."}],
    tools=tools,
    tool_choice="auto",
    temperature=0.6,
    max_tokens=16384,
)
```

---

## 六、SGLang 部署（推荐高吞吐量场景）

```bash
# 安装
pip install sglang[all]

# 35B MoE 部署（4 GPU）
python -m sglang.launch_server \
    --model-path deepreinforce-ai/Ornith-1.0-35B \
    --served-model-name Ornith-1.0 \
    --tp 4 \
    --host 0.0.0.0 --port 8000 \
    --context-length 262144 \
    --mem-fraction-static 0.85 \
    --tool-call-parser qwen3_coder \
    --reasoning-parser qwen3

# 验证服务是否就绪
curl http://localhost:8000/v1/models | python -m json.tool
```

---

## 七、与其他 Agentic Coding 方案的对比定位

| 方案 | 优势 | 局限 |
|---|---|---|
| **Ornith-1.0-9B** | 单卡可跑，agentic coding 最强 9B | 不适合通用问答 |
| **Ornith-1.0-35B MoE** | 35B 参数但胜过 400B 对手，性价比极高 | 需要 FP8 GPU 或多卡 |
| **Ornith-1.0-397B MoE** | 超过 Claude Opus 4.7，完全开源 | 需要 8x H100+ 节点 |
| Claude Opus 4.8 | SWE-Bench 87.6（仍领先） | 闭源，按 token 计费 |
| Qwen3.5-397B | 强通用能力 | agentic coding 被 Ornith 35B 反超 |

**Ornith 的适用场景**：
- ✅ 自动修 PR（SWE-Bench 场景）
- ✅ 终端任务 Agent（Terminal-Bench 场景）
- ✅ 代码仓库级别修改（NL2Repo）
- ✅ 多语言代码库（SWE-Bench Multilingual）
- ✅ MCP 工具链集成
- ❌ 通用知识问答（不是设计目标）
- ❌ 图像/视频（纯文本/代码模型）

---

## 八、关于「自己写脚手架」的哲学意义

Ornith 的自搭脚手架思路，解决了一个 benchmark 竞争中的真实问题：

> **你看到的 benchmark 分数，到底是模型的能力，还是 harness 工程师的能力？**

当模型的 scaffold 是人工设计的，分数就隐含了设计者的工程能力。换一套 harness，分数可能差 10-20 分。

Ornith 的方案：把 scaffold 也纳入 RL 优化范围，让「工作流设计」本身成为模型的学习目标。这样训出来的模型，在没有见过的任务上，也能探索出合适的工作流策略，而不是依赖固定的人工模板。

这对于真实部署的意义是：接一个新工具（新 MCP server、新 API）时，不需要人工重新设计 harness，模型会自己摸索调用方式。

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/deepreinforce-ai/Ornith-1 |
| 项目博客 | https://deep-reinforce.com/ornith.html |
| 9B 模型 | https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B |
| 9B GGUF（本地）| https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B-GGUF |
| 35B MoE | https://huggingface.co/deepreinforce-ai/Ornith-1.0-35B |
| 35B FP8 | https://huggingface.co/deepreinforce-ai/Ornith-1.0-35B-FP8 |
| 35B GGUF | https://huggingface.co/deepreinforce-ai/Ornith-1.0-35B-GGUF |
| 397B MoE | https://huggingface.co/deepreinforce-ai/Ornith-1.0-397B |
| 397B FP8 | https://huggingface.co/deepreinforce-ai/Ornith-1.0-397B-FP8 |
| ModelScope | https://modelscope.cn/organization/deepreinforce-ai |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **BLUF**: Ornith-1.0 is purpose-built for agentic coding — letting AI write code, debug, and manage tool-calling workflows autonomously. Its key innovation: training the model to write its own scaffolds via RL, rather than relying on human-designed fixed harnesses. MIT licensed, all sizes available, OpenAI API compatible.

---

## What Is Ornith-1.0?

Ornith (from the Greek "ornith" / bird) is DeepReinforce's open-source model family for agentic coding. The team previously built CUDA-L1 (RL-based CUDA optimization) and CUDA-L2 (beating cuBLAS via RL), with deep experience at the coding × reinforcement learning intersection.

**Four sizes, all MIT licensed:**

| Model | Type | Formats | Use Case |
|---|---|---|---|
| Ornith-1.0-9B | Dense 9B | bf16, GGUF | Single GPU, edge devices, local laptop |
| Ornith-1.0-35B | MoE 35B (~3B active) | bf16, FP8, GGUF | Multi-GPU server, single node |
| Ornith-1.0-397B | MoE 397B | bf16, FP8 | Multi-GPU node, production flagship |

**Base models**: Gemma 4 (9B) and Qwen 3.5 (35B / 397B)

---

## Benchmark Results

### 9B: Beats Models 3× Its Size

| Benchmark | **Ornith-9B** | Qwen3.5-9B | Qwen3.5-35B | Gemma4-12B | Gemma4-31B |
|---|:-:|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 | **43.1** | 21.3 | 41.4 | 21.0 | 42.1 |
| SWE-Bench Verified | **69.4** | 53.2 | 70.0 | 44.2 | 52.0 |
| SWE-Bench Pro | 42.9 | 31.3 | 44.6 | 27.6 | 35.7 |

9B Ornith beats Gemma4-31B on Terminal-Bench and nearly matches Qwen3.5-35B on SWE-Bench Verified.

### 35B MoE: Beats the 400B Model

| Benchmark | **Ornith-35B** | Qwen3.5-35B | Qwen3.6-35B | Gemma4-31B | Qwen3.5-397B |
|---|:-:|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 | **64.2** | 41.4 | 52.5 | 42.1 | 53.5 |
| SWE-Bench Verified | **75.6** | 70.0 | 73.4 | 52.0 | 76.4 |

Ornith-35B MoE beats the 10× larger Qwen3.5-397B on Terminal-Bench (64.2 vs 53.5).

### 397B MoE: Beats Claude Opus 4.7

| Benchmark | **Ornith-397B** | Qwen3.5-397B | Claude Opus 4.7 | Claude Opus 4.8 |
|---|:-:|:-:|:-:|:-:|
| Terminal-Bench 2.1 (Terminus-2) | **77.5** | 53.5 | 70.3 | 85.0 |
| Terminal-Bench 2.1 (Claude Code) | **78.2** | 48.6 | 69.7 | 78.9 |
| SWE-Bench Verified | **82.4** | 76.4 | 80.8 | 87.6 |
| SWE-Bench Pro | 62.2 | 51.6 | 64.3 | 69.2 |
| SWE-Bench Multilingual | **78.9** | 69.3 | — | — |

397B beats Claude Opus 4.7 on both flagship benchmarks. It's competitive with Opus 4.8 on Claude Code Terminal-Bench (78.2 vs 78.9).

---

## Core Innovation: Self-Scaffolding RL

Most agentic coding benchmark scores reflect both the model's capability AND the human-designed harness — the fixed orchestration logic (tool call ordering, retry logic, task decomposition). Swap the harness, and scores shift by 10-20 points.

**Ornith's approach**: make the scaffold a learnable object that co-evolves with the policy.

```
Traditional:
  [Human-designed fixed harness] → Model generates solution → Verifier scores
  → Only the solution is optimized

Ornith:
  Task + previous scaffold → Model proposes refined scaffold
  New scaffold + task → Model generates solution rollout
  Reward propagated to BOTH → scaffold and solution jointly optimized
```

Each RL step is a two-stage process: scaffold refinement, then solution generation. Over training, a feedback loop emerges where scaffolds are continuously mutated and selected toward those that induce higher-reward trajectories.

### Three-Layer Anti-Reward-Hacking

```
Layer 1: Outer boundary (immutable)
  → Environment, tool surface, test isolation cannot be modified by the model
  → Only inner scaffold (memory, error handling, orchestration) can evolve

Layer 2: Deterministic monitor (exact specification)
  → Flags: reading hidden paths, modifying verification scripts,
           calling out-of-scope tools
  → Assigns zero reward, excludes from advantage computation

Layer 3: Frozen LLM judge (intent-level veto)
  → Catches gaming that occurs entirely within allowed tool surface
  → Acts as veto on top of verifier, not as primary reward
```

The team learned from CUDA-L1, where RL exploited a timing loophole to fake GPU speedups. These three layers are the direct response.

### Asynchronous RL with Staleness Weights

For long rollouts, the off-policy problem: tokens generated early become stale before the gradient update. Ornith's pipeline-RL uses a staleness weight:

- Tokens are downweighted proportional to their age
- Tokens past a threshold are dropped entirely
- GRPO loss is multiplied by staleness weight

This allows parameter updates to proceed while new rollouts are still being generated.

---

## Quick Start

### Transformers (9B, local)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
# Requires transformers >= 5.8.1

model = AutoModelForCausalLM.from_pretrained(
    "deepreinforce-ai/Ornith-1.0-9B",
    dtype="auto", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("deepreinforce-ai/Ornith-1.0-9B")

messages = [{"role": "user", "content": "Write a Python binary search function with unit tests."}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
output = model.generate(**inputs, max_new_tokens=2048, temperature=0.6, top_p=0.95, do_sample=True)

content = tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
if "</think>" in content:
    reasoning, answer = content.split("</think>", 1)
    print("THINKING:", reasoning.replace("<think>", "").strip()[:200])
    print("\nANSWER:", answer.strip())
```

### vLLM Server + OpenAI Client

```bash
# Start server (35B MoE on 4 GPUs)
MODEL=deepreinforce-ai/Ornith-1.0-35B-FP8
vllm serve $MODEL --served-model-name Ornith-1.0 \
    --tensor-parallel-size 4 --port 8000 \
    --max-model-len 262144 \
    --enable-auto-tool-choice --tool-call-parser qwen3_xml \
    --reasoning-parser qwen3 --trust-remote-code
```

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

response = client.chat.completions.create(
    model="Ornith-1.0",
    messages=[{"role": "user", "content": "Find and fix the memory leak in this C++ code: ..."}],
    temperature=0.6, max_tokens=8192,
)
print(response.choices[0].message.content)
```

### Ollama (9B GGUF, local laptop)

```bash
ollama pull deepreinforce-ai/Ornith-1.0-9B-GGUF
ollama run deepreinforce-ai/Ornith-1.0-9B-GGUF
```

---

## Who Should Use Which Size

| Scenario | Recommended | Why |
|---|---|---|
| Local dev, single laptop/GPU | 9B GGUF | Runs on 8GB VRAM, beats 31B models |
| Team CI/CD pipeline | 35B MoE FP8 | Best coding ratio below 100B |
| Replace Claude Opus 4.7 | 397B MoE FP8 | Beats it on Terminal-Bench + SWE-Bench |
| Budget constrained, max quality | 35B MoE | Outperforms 397B Qwen3.5 — best per-dollar |

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution; do not republish as original without credit.
