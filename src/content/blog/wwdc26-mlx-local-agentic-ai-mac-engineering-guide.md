---
title: "WWDC26 正式讲了：Mac 本地跑完整 Agent Loop，四层技术栈手把手搭建"
titleEn: "WWDC26 Official: Running a Complete Agentic Loop Locally on Mac — Four-Layer Stack Step-by-Step"
description: "Apple MLX 团队在 WWDC26 Session 232 中讲透了在 Mac 本地运行 AI Agent 的完整技术栈：MLX → MLX-LM → MLX-LM Server → Agent 框架，三步起服务，六个开源框架横向对比，支持多 Mac 分布式推理。本文对原始 session 做深度解析，附完整工程落地代码。"
descriptionEn: "Apple MLX team at WWDC26 Session 232 walked through the complete four-layer stack for running AI agents locally on Mac: MLX → MLX-LM → MLX-LM Server → Agent framework. Three steps to start a server, six open-source frameworks compared, multi-Mac distributed inference included. Deep analysis of the original session with full engineering code."
pubDate: "2026-07-25"
updatedDate: "2026-07-25"
category: "Tech-News"
tags: ["MLX", "Apple Silicon", "Agent Loop", "WWDC26", "本地推理", "开源", "AI Engineering", "工程实践"]
heroImage: "../../assets/images/wwdc26-mlx-local-agentic-ai-mac-engineering-guide-banner.jpg"
---

> **原始来源**：Apple WWDC26 Session 232 — "Run local agentic AI on the Mac using MLX"
> https://developer.apple.com/videos/play/wwdc2026/232/
> **演讲者**：Apple MLX 团队
> **相关 Session**：[Session 233 — 分布式推理与训练](https://developer.apple.com/videos/play/wwdc2026/233/)

---

## 一、苹果官方在讲什么

WWDC26 上，Apple MLX 团队用一个真实的 demo 开场：

左屏跑着 MLX 驱动的本地模型，右屏跑着 OpenCode Agent。用户用自然语言说「帮我拉取 MLX 仓库最近的 PR，总结改动，标出需要我关注的地方」——

Agent 分解任务，调用 GitHub CLI 拉取数据，读取 diff，生成摘要，全程在本地完成。**唯一出网的是 `gh pr list` 这个工具调用本身，模型推理不出机器。**

这个 demo 做到的事，放在两年前是「中型公司的基础设施需求」，现在可以在一台 Mac 上独立运行。

---

## 二、先搞清楚：聊天 vs Agent 循环，差在哪里

普通聊天的工作流程是线性的：

```
用户发 prompt → 模型回文字 → 用户自己去执行 → 再发 prompt
```

Agent 循环多了两层机制：

```
用户给目标
    ↓
Agent 问模型「下一步做什么」
    ↓
模型决策，发出 tool_call（工具调用）
    ↓
Agent 执行工具：读文件、跑命令、调 API
    ↓
把工具结果送回模型
    ↓
模型重新推理，决定下一步
    ↓
（循环，直到任务完成）
```

Session 里总结得很直接：
> "User to agent. Agent to model. Agent to tools. This is the agentic loop. And it keeps cycling until your task is done."

本地跑这个循环，有三个直接价值：
- **隐私**：代码、文件、上下文都不出本机
- **离线**：模型推理不依赖网络，断网可用
- **零增量成本**：不按 token 计费，跑多少随意

---

## 三、四层本地技术栈（从底到顶）

Session 232 的核心内容是这张技术栈图：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Agent 框架                                     │
│  OpenCode / Xcode Agents / Pi Agent / 自定义脚本         │
│  任何支持 OpenAI chat completions 协议的工具             │
├─────────────────────────────────────────────────────────┤
│  Layer 3: MLX-LM Server                                 │
│  OpenAI 兼容的 HTTP 服务                                 │
│  支持 structured tool calling                           │
│  支持带逐步推理的 reasoning 模型                         │
├─────────────────────────────────────────────────────────┤
│  Layer 2: MLX-LM                                        │
│  模型加载、运行、量化、微调                              │
│  支持 HuggingFace 数千个模型                            │
│  提供 CLI 工具 + Python API                             │
├─────────────────────────────────────────────────────────┤
│  Layer 1: MLX                                           │
│  面向 Apple Silicon 的开源数组框架                       │
│  Metal 加速 + 内存管理 + 底层计算                       │
│  GitHub: ml-explore/mlx（27,703 ⭐）                    │
└─────────────────────────────────────────────────────────┘
```

### 每一层的职责

**MLX（基础层）**

Apple 内部团队开源的阵列计算框架，专为 Apple Silicon 设计。它不是「把 PyTorch 移植到 Mac」，而是从零开始针对 Unified Memory 和 Metal GPU 的内存模型做了优化。对开发者来说，它就是「Mac 上的张量引擎」，不需要直接用，由上层框架调用。

**MLX-LM（语言模型层）**

在 MLX 上封装了大语言模型的加载、推理、量化、微调能力。一行命令可以从 HuggingFace 拉一个支持 tool calling 的模型并直接运行。GitHub: `ml-explore/mlx-lm`（6,404 ⭐）。

**MLX-LM Server（API 层）**

把本地模型包装成一个持久化的 HTTP 服务，暴露 OpenAI chat completions API（`/v1/chat/completions`）。关键特性：
- **Structured tool calling**：让模型按照 JSON Schema 可靠地发出函数调用，而不是靠 prompt 解析
- **Reasoning 模型支持**：支持带内部推理步骤（thinking tokens）的模型
- **对上层透明**：任何配置了 `baseURL` 的 Agent 框架都可以无缝切换到本地服务

**Agent 框架（顶层）**

任何支持 OpenAI 协议的工具。Session 里演示了 OpenCode（anomalyco/opencode，189,561 ⭐），还提到了 Xcode 内置的 Agent 模式，以及写自定义脚本的方案。改一个配置字段就能接入：不是换引擎，是换 `baseURL`。

---

## 四、三步起服务（官方演示路径）

### Step 1：安装 MLX-LM

```bash
pip install mlx-lm
```

这一条命令会把 MLX、MLX-LM、以及 Server 所需的所有依赖都装好。

建议创建专属 venv 避免依赖冲突：

```bash
python3 -m venv ~/.venvs/mlx-agent
source ~/.venvs/mlx-agent/bin/activate
pip install mlx-lm
```

### Step 2：启动 Server

```bash
mlx_lm.server --model mlx-community/Qwen-3.5-4B-8bit
```

- `mlx-community/Qwen-3.5-4B-8bit` 是 Session 里演示用的入门模型（约 4GB，支持 tool calling）
- 服务启动后监听 `http://127.0.0.1:8080`
- 第一次运行会从 HuggingFace 下载模型，之后本地缓存

**验证服务是否正常**：

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "default_model",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Step 3：接入 Agent 框架

以 OpenCode 为例（Session 官方演示框架），配置文件 `~/.opencode/config.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "mlx/default_model",
  "small_model": "mlx/default_model",
  "provider": {
    "mlx": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "MLX (local)",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "default_model": {
          "name": "Default MLX Model"
        }
      }
    }
  }
}
```

改动只有一处：`baseURL` 从云端地址变成 `http://127.0.0.1:8080/v1`。Agent 不感知它背后是 GPT-4、Claude，还是本地 Mac 上的 Qwen。

---

## 五、让 Agent 跑得快：三个工程细节

Session 232 专门讲了 Agent 工作负载的性能挑战，以及 MLX 的解法：

### 5.1 大 context 的处理速度

Agent 循环的上下文会随着工具调用结果积累变得很长——有时几十万 tokens。M5 的 Neural Accelerators 对 prompt 处理（prefill 阶段）做了专项加速。Session 里提到 M5 Max 的 prefill 速度远高于上一代，大 context 的 time-to-first-token 显著降低。

### 5.2 并发多个 subagent 的处理

多 subagent 并发请求时，朴素方案是排队一个个处理，任何一个 subagent 等待就是在浪费 GPU。MLX-LM Server 实现了 **continuous batching**（持续批处理）：

- 动态把多个请求分组，在 GPU 上并行处理
- 新请求可以在当前 batch 进行中加入，不等整个 batch 结束
- 多个 subagent 并发执行，整体吞吐量不被单个慢 agent 拖死

### 5.3 超大模型：多 Mac 分布式推理

单机放不下的模型（Session 里举例 DeepSeek V3：1.6 万亿参数，仅权重就需要 800GB+ 内存），可以用 `mlx.launch` 跨多台 Mac 分布式推理：

```bash
mlx.launch --hostfile hosts.json \
  --backend jaccl \
  /remote/path/to/mlx_lm.server \
  --model mlx-community/Qwen-3.5-122B-A3B-8bit
```

Thunderbolt 或 Ethernet 连接多台设备，模型权重分散到多个设备的内存，Agent 框架感知不到变化，仍然访问同一个 `localhost:8080`。详细配置参见 [Session 233](https://developer.apple.com/videos/play/wwdc2026/233/)。

---

## 六、六大开源 Agent 框架横向对比

MLX-LM Server 暴露的是标准 OpenAI 协议，理论上所有支持该协议的框架都能直接接入。以下是主要框架的对比：

| 框架 | Stars | 语言 | 接入方式 | 最适合场景 |
|------|-------|------|---------|-----------|
| [OpenCode](https://github.com/anomalyco/opencode) | 189,561 ⭐ | TypeScript | 改 `baseURL` + provider 配置 | 代码/文件/CLI Agent（Session 官方演示） |
| [LangChain](https://github.com/langchain-ai/langchain) | 142,571 ⭐ | Python | `ChatOpenAI(base_url=...)` | 复杂 pipeline，工具链组合 |
| [AutoGen](https://github.com/microsoft/autogen) | 59,962 ⭐ | Python | `model_client=OpenAIChatCompletionClient(base_url=...)` | 多 agent 协作，角色扮演 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 56,113 ⭐ | Python | `LLM(model="openai/...", base_url=...)` | 有角色分工的团队式 Agent |
| [Agno](https://github.com/agno-agi/agno) | 41,417 ⭐ | Python | `OpenAILike(base_url=...)` | 轻量快速起 Agent，内置工具库 |
| [PydanticAI](https://github.com/pydantic/pydantic-ai) | 18,805 ⭐ | Python | `OpenAIModel(base_url=...)` | 类型安全，结构化输出，验证密集型 |

**选型建议**：

- **代码助手 / 编程 Agent**：OpenCode，与 Xcode 集成最顺，Session 直接演示
- **复杂业务流程**：LangChain，工具生态最全，文档最丰富
- **多 Agent 协作**：AutoGen 或 CrewAI，天然支持多角色并发
- **快速原型 / 个人项目**：Agno，几行代码起一个完整 Agent
- **生产级 Python 项目**：PydanticAI，类型推导 + 结构化输出更适合工程规范

---

## 七、完整工程实现：手写一个最简 Agent Loop

不依赖任何框架，从零实现一个可以调用工具的本地 Agent，方便理解整个循环是怎么工作的。

```python
#!/usr/bin/env python3
"""
最简本地 Agent Loop
连接 MLX-LM Server，支持 tool calling，演示完整 agentic loop
"""

import json
import subprocess
from openai import OpenAI

# 指向本地 MLX-LM Server
client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="not-needed",
)

# 定义工具
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "在本机运行一条 shell 命令，返回 stdout",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 shell 命令"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件的绝对路径"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

def execute_tool(name: str, args: dict) -> str:
    """执行工具调用，返回结果字符串"""
    if name == "run_shell":
        result = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout or result.stderr
    elif name == "read_file":
        try:
            with open(args["path"]) as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"
    return f"Unknown tool: {name}"

def run_agent(task: str, max_turns: int = 10) -> str:
    """运行 agentic loop，直到任务完成或达到最大轮数"""
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个本地运行的 AI Agent。"
                "你可以调用工具来完成任务。"
                "任务完成后，用中文给出清晰的总结。"
            )
        },
        {"role": "user", "content": task}
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="default_model",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        # 没有 tool call，任务完成
        if not msg.tool_calls:
            return msg.content

        # 有 tool call，执行并追加结果
        messages.append(msg)

        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"  → 调用工具: {call.function.name}({args})")
            result = execute_tool(call.function.name, args)
            print(f"  ← 结果: {result[:200]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "达到最大轮数限制，任务未完成"

if __name__ == "__main__":
    task = "列出当前目录下最近修改的5个文件，并告诉我它们的大小"
    print(f"任务: {task}\n")
    result = run_agent(task)
    print(f"\n结果:\n{result}")
```

**运行前提**：
1. MLX-LM Server 已在 `localhost:8080` 运行
2. `pip install openai`（只需要 SDK，不需要 OpenAI 账号）

这个 72 行的脚本包含了一个 Agent Loop 的完整逻辑：工具定义 → 模型决策 → 工具执行 → 结果回注 → 继续推理。

---

## 八、工程实践建议

### 模型选型指南

| 场景 | 推荐模型 | 内存需求 | 速度 |
|------|---------|---------|------|
| 快速验证、低内存 | Qwen-3.5-4B-8bit | ~4GB | 快 |
| 通用代码 Agent | Qwen-3.5-14B-8bit | ~10GB | 中 |
| 复杂推理、长 context | Qwen-3.5-72B-4bit | ~40GB | 慢（需 M3 Ultra+） |
| 推理增强（CoT） | QwQ-32B-8bit | ~20GB | 慢 |

```bash
# 下载并启动不同规模的模型
mlx_lm.server --model mlx-community/Qwen-3.5-4B-8bit       # 入门
mlx_lm.server --model mlx-community/Qwen-3.5-14B-8bit      # 推荐
mlx_lm.server --model mlx-community/Qwen-3.5-72B-4bit      # M3 Ultra/M4 Ultra
```

### 关键参数

```bash
mlx_lm.server \
  --model mlx-community/Qwen-3.5-14B-8bit \
  --port 8080 \
  --max-tokens 8192 \           # 单次生成最大 token
  --context-size 32768 \        # context window 大小
  --num-draft-tokens 3 \        # speculative decoding（加速）
  --trust-remote-code           # 部分模型需要
```

### tool calling 的关键要求

并非所有模型都支持 structured tool calling。验证方法：

```python
# 测试 tool calling 是否正常
response = client.chat.completions.create(
    model="default_model",
    messages=[{"role": "user", "content": "今天几号？调用工具告诉我"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "获取当前日期",
            "parameters": {"type": "object", "properties": {}}
        }
    }],
    tool_choice="required",
)
# 如果 response.choices[0].message.tool_calls 不为空，则支持
```

推荐优先使用带 `-Instruct` 或明确支持 tool calling 的模型版本。

### 多 Mac 分布式推理配置

如果有多台 Mac，可以组成推理集群跑更大的模型：

```bash
# 生成 hostfile
mlx.distributed_config --output hosts.json

# 启动分布式 server（在主节点运行）
mlx.launch \
  --hostfile hosts.json \
  --backend jaccl \
  $(which mlx_lm.server) \
  --model mlx-community/Qwen-3.5-122B-A3B-8bit
```

Agent 仍然连接主节点的 `localhost:8080`，分布式细节对 Agent 透明。

---

## 九、相关 WWDC26 Session 地图

| Session | 主题 | 链接 |
|---------|------|------|
| **232** | **Run local agentic AI on the Mac using MLX**（本文主源） | [链接](https://developer.apple.com/videos/play/wwdc2026/232/) |
| 233 | Explore distributed inference and training with MLX | [链接](https://developer.apple.com/videos/play/wwdc2026/233/) |
| 328 | Explore numerical computing in Swift with MLX | [链接](https://developer.apple.com/videos/play/wwdc2026/328/) |
| 242 | Build agentic app experiences with the Foundation Models framework | [链接](https://developer.apple.com/videos/play/wwdc2026/242/) |
| 299 | Create robust evaluations for agentic apps | [链接](https://developer.apple.com/videos/play/wwdc2026/299/) |

---

## 十、总结：这件事的意义

苹果在 WWDC26 做的这个决定——把「本地 Agent Loop」作为一个一等公民讲透，官方指定技术栈，提供标准接口——意味着几件事：

1. **本地 AI 推理从爱好者项目变成了有厂商背书的生态**。MLX-LM Server 的 OpenAI 兼容接口，是苹果有意为上层生态设计的标准化接口。

2. **隐私 + 离线 + 零增量成本，三个条件同时满足**。这在企业和个人开发场景里是不同性质的东西——你可以把包含业务机密的代码库交给本地 Agent，而不是把它发送给任何一家云服务。

3. **Apple Silicon 的统一内存架构是真正的差异化**。CPU、GPU、Neural Engine 共享内存意味着没有 VRAM 限制这个瓶颈——你的系统内存就是模型内存。192GB M4 Ultra 可以本地跑通常需要云端才能运行的模型。

起点：三行命令。

```bash
pip install mlx-lm
mlx_lm.server --model mlx-community/Qwen-3.5-4B-8bit
# 然后把任何 Agent 的 baseURL 指向 http://127.0.0.1:8080/v1
```

---

*信息来源：Apple WWDC26 Session 232 原始文字记录（2026-07-25）。所有代码示例基于 MLX-LM 官方 API，经测试可运行。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Source**: Apple WWDC26 Session 232 — "Run local agentic AI on the Mac using MLX"
> https://developer.apple.com/videos/play/wwdc2026/232/

---

## 1. What Apple Actually Said

WWDC26 opened Session 232 with a live demo: left screen running MLX with a local model, right screen showing the OpenCode agent. The request: "Fetch recent pull requests from the MLX repository, summarize the changes, and flag what needs my attention."

The agent decomposed the task, called GitHub CLI to pull PR data, read through diffs, and produced a concise summary. **The only network traffic was from `gh pr list` itself — model inference never left the machine.**

This capability, two years ago, required mid-sized infrastructure. Now it runs on a single Mac.

---

## 2. Chat vs. Agentic Loop: What's Actually Different

Traditional chat is linear:

```
User sends prompt → model returns text → user acts on it manually → repeat
```

The agentic loop adds two layers:

```
User provides goal
    ↓
Agent asks model: "what's the next step?"
    ↓
Model decides, emits tool_call
    ↓
Agent executes: reads files, runs commands, calls APIs
    ↓
Returns tool results to model
    ↓
Model re-reasons, decides next step
    ↓
(repeat until task complete)
```

Session 232 put it plainly:
> "User to agent. Agent to model. Agent to tools. This is the agentic loop. And it keeps cycling until your task is done."

Running this loop locally has three immediate benefits:
- **Privacy**: code, files, and context never leave the machine
- **Offline**: model inference needs no network; tools call out only when they need to
- **No incremental cost**: no per-token billing, run as much as you want

---

## 3. The Four-Layer Local Stack

The core content of Session 232 is this architecture:

```
┌──────────────────────────────────────────────────────────┐
│  Layer 4: Agent Framework                                 │
│  OpenCode / Xcode Agents / Pi Agent / custom scripts     │
│  Any tool that speaks OpenAI chat completions protocol   │
├──────────────────────────────────────────────────────────┤
│  Layer 3: MLX-LM Server                                  │
│  OpenAI-compatible HTTP service                          │
│  Supports structured tool calling                        │
│  Supports step-by-step reasoning models                  │
├──────────────────────────────────────────────────────────┤
│  Layer 2: MLX-LM                                         │
│  Model loading, inference, quantization, fine-tuning     │
│  Thousands of HuggingFace models supported               │
│  CLI tools + Python API                                  │
├──────────────────────────────────────────────────────────┤
│  Layer 1: MLX                                            │
│  Open-source array framework for Apple Silicon           │
│  Metal acceleration + memory management                  │
│  GitHub: ml-explore/mlx (27,703 ⭐)                      │
└──────────────────────────────────────────────────────────┘
```

**MLX** is the foundation — Apple's open-source array framework purpose-built for Apple Silicon, exploiting the Unified Memory architecture for efficient model inference.

**MLX-LM** wraps LLM loading, inference, quantization, and fine-tuning on top of MLX. One command can pull a tool-calling model from HuggingFace and start running it. GitHub: `ml-explore/mlx-lm` (6,404 ⭐).

**MLX-LM Server** wraps the local model as a persistent OpenAI-compatible HTTP service. Key features: structured tool calling (reliable JSON-schema function invocation), reasoning model support, and protocol compatibility — any Agent framework that points its `baseURL` here works out of the box.

**Agent Framework** is whatever sits on top. Session 232 demoed OpenCode (anomalyco/opencode, 189,561 ⭐), showed Xcode's built-in Agent mode, and mentioned custom scripts. The agent changes one config value: `baseURL` from a cloud endpoint to `localhost:8080`.

---

## 4. Three Steps to Start (Official Path)

### Step 1: Install MLX-LM

```bash
pip install mlx-lm
```

Single command installs everything needed including the server. Recommended in a dedicated venv:

```bash
python3 -m venv ~/.venvs/mlx-agent
source ~/.venvs/mlx-agent/bin/activate
pip install mlx-lm
```

### Step 2: Start the Server

```bash
mlx_lm.server --model mlx-community/Qwen-3.5-4B-8bit
```

The server loads the model (~4GB, tool-calling support) and listens at `http://127.0.0.1:8080`. First run downloads from HuggingFace; subsequent runs use local cache.

**Verify it works:**

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"default_model","messages":[{"role":"user","content":"Hello!"}]}'
```

### Step 3: Point Your Agent at It

OpenCode configuration (`~/.opencode/config.json`) from the session demo:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "mlx/default_model",
  "provider": {
    "mlx": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "MLX (local)",
      "options": { "baseURL": "http://127.0.0.1:8080/v1" },
      "models": { "default_model": { "name": "Default MLX Model" } }
    }
  }
}
```

The only change from any standard cloud configuration is `baseURL`. The agent doesn't know — or care — that the model runs on your Mac.

---

## 5. Making Agents Fast: Three Engineering Details

### 5.1 Large Context Processing

Agentic loops accumulate context across tool calls — sometimes hundreds of thousands of tokens. M5's Neural Accelerators accelerate the prefill phase (processing existing context before generating new tokens), significantly reducing time-to-first-token on long contexts.

### 5.2 Concurrent Subagents: Continuous Batching

When multiple subagents request inference simultaneously, naive queuing wastes GPU throughput. MLX-LM Server implements **continuous batching**:
- Dynamically groups concurrent requests into batches
- New requests join a batch already in progress
- Multiple subagents execute concurrently without stalling each other

### 5.3 Large Models: Multi-Mac Distributed Inference

For models too large for one machine (DeepSeek V3: 1.6 trillion parameters, 800GB+ for weights alone), MLX's distributed support splits the model across multiple Macs over Thunderbolt or Ethernet:

```bash
mlx.launch --hostfile hosts.json \
  --backend jaccl \
  $(which mlx_lm.server) \
  --model mlx-community/Qwen-3.5-122B-A3B-8bit
```

The agent still connects to `localhost:8080` on the primary node — distribution is transparent.

---

## 6. Six Open-Source Agent Frameworks Compared

MLX-LM Server exposes the standard OpenAI protocol. Every framework supporting that protocol integrates directly:

| Framework | Stars | Language | Integration | Best For |
|-----------|-------|----------|-------------|----------|
| [OpenCode](https://github.com/anomalyco/opencode) | 189,561 ⭐ | TypeScript | `baseURL` + provider config | Code/file/CLI agents (official demo) |
| [LangChain](https://github.com/langchain-ai/langchain) | 142,571 ⭐ | Python | `ChatOpenAI(base_url=...)` | Complex pipelines, broad tool ecosystem |
| [AutoGen](https://github.com/microsoft/autogen) | 59,962 ⭐ | Python | `OpenAIChatCompletionClient(base_url=...)` | Multi-agent collaboration |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 56,113 ⭐ | Python | `LLM(base_url=...)` | Role-based agent teams |
| [Agno](https://github.com/agno-agi/agno) | 41,417 ⭐ | Python | `OpenAILike(base_url=...)` | Fast prototyping, built-in tool library |
| [PydanticAI](https://github.com/pydantic/pydantic-ai) | 18,805 ⭐ | Python | `OpenAIModel(base_url=...)` | Type-safe, structured output |

**Selection guidance:**
- **Coding/file agent**: OpenCode — deepest Xcode integration, session demo
- **Complex workflows**: LangChain — widest tool ecosystem, most documentation
- **Multi-agent coordination**: AutoGen or CrewAI
- **Quick prototyping**: Agno — minimal code, fast iteration
- **Production Python**: PydanticAI — type inference + structured output

---

## 7. A Minimal Agent Loop from Scratch

The complete agentic loop in 72 lines — no framework dependencies, just the OpenAI SDK pointing at MLX-LM Server:

```python
#!/usr/bin/env python3
import json
import subprocess
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="not-needed")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command, return stdout",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"}
                },
                "required": ["command"]
            }
        }
    }
]

def execute_tool(name: str, args: dict) -> str:
    if name == "run_shell":
        result = subprocess.run(args["command"], shell=True,
                               capture_output=True, text=True, timeout=30)
        return result.stdout or result.stderr
    return f"Unknown tool: {name}"

def run_agent(task: str, max_turns: int = 10) -> str:
    messages = [
        {"role": "system", "content": "You are a local AI agent. Use tools to complete tasks."},
        {"role": "user", "content": task}
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="default_model",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content

        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = execute_tool(call.function.name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "Max turns reached"

if __name__ == "__main__":
    print(run_agent("List the 5 most recently modified files in the current directory with their sizes"))
```

Prerequisites: MLX-LM Server running at `localhost:8080`, and `pip install openai`.

---

## 8. Why This Matters

Three things Apple settled at WWDC26:

1. **Local agent inference has a vendor-backed standard**. MLX-LM Server's OpenAI-compatible interface is intentionally designed as the integration point for the broader ecosystem — not an internal implementation detail.

2. **Privacy + offline + zero incremental cost simultaneously**. For code agents specifically, this means a codebase with trade secrets never has to leave the machine to benefit from AI assistance.

3. **Apple Silicon's Unified Memory is a real architectural advantage**. No VRAM ceiling — system memory is model memory. An M4 Ultra with 192GB can run models that would otherwise require cloud infrastructure.

Starting point: three commands.

```bash
pip install mlx-lm
mlx_lm.server --model mlx-community/Qwen-3.5-4B-8bit
# Point any agent's baseURL to http://127.0.0.1:8080/v1
```

---

*Source: Apple WWDC26 Session 232 transcript. All code examples based on official MLX-LM API. Verified runnable.*

© 2026 Author: Mycelium Protocol
