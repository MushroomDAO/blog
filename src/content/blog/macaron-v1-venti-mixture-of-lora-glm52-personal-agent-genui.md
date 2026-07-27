---
title: "Macaron-V1-Venti：Mixture-of-LoRA + GLM-5.2，个人智能体 + Generative UI 的新范式"
description: "MindLab Research 发布的 Macaron-V1-Venti 是一个 748B 参数的开源旗舰模型：744B 的 GLM-5.2 基础模型加上四个 1B 的 LoRA 专家，通过 L0 路由实现 Chat/Agent/Coding/GenUI 的任务分发。本文深度拆解 MoL 架构、LongStraw 百万 token RL 训练基础设施、MindForge 递归自我改进循环，以及 MIT 授权的开放权重。"
pubDate: "2026-07-27"
category: "Research"
heroImage: "../../assets/images/macaron-v1-venti-mixture-of-lora-glm52-personal-agent-genui-banner.jpg"
---

2026 年 7 月 21 日，MindLab Research 发布了 Macaron-V1，这是他们继 Preview 版之后第一个正式发布的智能体模型。

核心设计不是 MoE（专家混合），而是一个鲜少被产品化的方向：**Mixture of LoRA（MoL）**——一个冻结的大基础模型，加上若干轻量 LoRA 专家，由一个 L0 路由器按任务类型分发。

748B 参数，MIT 开源授权，权重已上传 HuggingFace。

---

## 一、模型家族

Macaron-V1 发布了两个规模变体：

| 变体 | 总参数 | 基础模型 | LoRA 专家 | 定位 |
|---|---|---|---|---|
| Macaron-V1-Venti | 748B | GLM-5.2 (744B) | 4 × 1B | 旗舰，云端 |
| Macaron-V1-Tall | 50B | Qwen3.6-35B-A3B | 4 × 3.7B (Rank-64) | 本地部署 |

Venti 是第一个基于 GLM-5.2 进行后训练的模型——也是全球首个。

---

## 二、Mixture-of-LoRA 架构

### 核心思路

传统 MoE 在 FFN 层内部放置多个专家，路由的是 token 级别的神经元激活。

MoL 走的是完全不同的路径：**基础模型的权重完全冻结**，专家能力通过 LoRA 适配器层叠加。路由发生在**用户请求级别**，而不是 token 级别：

```
用户请求
  ↓
L0 (Chat LoRA)  ← 路由决策
  ↓
L1 / L2 / L3   ← 执行
  ↓
Summary         ← 跨适配器记忆同步
```

四个 LoRA 专家的分工：

| 适配器 | 角色 | 擅长任务 |
|---|---|---|
| L0 Chat | 对话骨干 + 路由入口 | 日常对话、指令跟随 |
| L1 Agent | 重度工具调用 | 长时程任务、个人生活场景、动态工作流 |
| L2 Coding | 代码理解 + 执行 | SWE 任务、终端操作、仓库工作流 |
| L3 GenUI | Generative UI | UI4A 渲染、UI 驱动的行为 |

### 运行时的三步流程

每一个新的用户请求都经历三步：

1. **Route**：L0 选择最合适的专家适配器
2. **Answer**：被选中的适配器从自己的对话视图中生成回复
3. **Summary**：被选中的适配器生成一份跨适配器摘要（不返回给客户端）

这份 Summary 存储在 Proxy 中，用于在专家切换时保持任务连续性——既不让每个专家都处理完整对话历史，也不丢失前一个任务的结果。

工具调用不触发重新路由。一旦某个适配器发出工具调用，后续工具结果仍在同一适配器上处理。

### 为什么这个设计有意思

MoL 本质上是一种**按任务类型的能力分区**，而不是传统意义上的参数稀疏激活。

优势在于：
- 基础模型权重不变 → 新专家可以随时插拔，不影响已有能力
- 每个专家只有 1B 参数 → 新增专家的成本极低
- 前缀缓存友好：各专家有固定的 system prompt，vLLM 的 KV 前缀缓存可以跨请求复用

---

## 三、Serving：MoL Harness

MindLab 开源了 [MoL 服务 Harness](https://github.com/MindLab-Research/Mixture-of-LoRA-Harness)，基于 vLLM 或 SGLang 的 native multi-LoRA 支持。

架构：

```
OpenAI 客户端
    |
    v
MoL Proxy :8200
    |  route → answer → summary
    v
vLLM / SGLang :8000
    |
    +-- L0  Chat
    +-- L1  Agent
    +-- L2  Coding
    `-- L3  GenUI
```

Venti 的服务规格：TP8，262K token 上下文，`max_num_seqs=8`，`gpu_memory_utilization=0.915`，141 个模型分片，需要 8 张 GPU。

本地 API 调用示例：

```bash
curl https://mintcn.macaron.xin/v1/chat/completions \
  -H "Authorization: Bearer <api-key>" \
  -d '{"model": "Macaron-V1-Venti", "messages": [{"role": "user", "content": "创建一个跟踪每周健身目标的仪表盘 UI"}]}'
```

---

## 四、LongStraw：百万 token RL 训练

这是 Macaron-V1 工程层面最有价值的部分。

### 问题

推理引擎已经可以处理百万 token 的上下文窗口，但 RL 训练不能。

原因：推理只需 prefill 完成后丢弃前向图；RL 训练必须同时保留激活、对多个回复评分并累积梯度。在固定显存下，这将训练的有效上下文长度拦在 256K 附近。

### LongStraw 的解决方案

改变训练的基本单位——**把 prompt 变成可复用的 Resident State**：

1. 整个 prompt 只前向计算一次，产生 Resident State
2. 多条候选回复分别在 Resident State 基础上做轻量 replay
3. 各回复的梯度分别累积
4. 一次分布式参数更新

prompt 长度从"全序列内存问题"变成了"State 生命周期问题"：长 prompt 只付出一次代价，活跃的梯度图只跟随短的回复分支。

### 实测规模

| 硬件 | 模型 | 上下文 |
|---|---|---|
| 8×H20 | Qwen3.6-27B | 2.1M token GRPO |
| 8×H20 | Resident-prefix path | 4.46M tokens |
| 32×H20 | GLM-5.2（78层 MLA/DSA，256专家 MoE）| 2.1M token 全量训练 |

[论文](https://huggingface.co/papers/2607.14952) + [代码](https://github.com/MindLab-Research/longstraw) 均已开源。

---

## 五、训练基础设施：MinT + MindForge

### MinT

Mind Lab 的后训练平台，支撑了 Venti 这个规模下的训练：

- **仅传输 adapter**：actor 和 learner 之间只转移 LoRA 权重，不移动完整模型
- **百万规模 adapter 目录**：与 MoL 的插件式专家架构对齐
- **最高支持万亿参数模型**的端到端训练

[技术报告](https://huggingface.co/papers/2605.13779)已发布。

### MindForge：递归自我改进（RSI）

RSI 三阶段闭环：

```
Discovery  →  从种子任务出发，模型构建更难、更多样的任务
              自动验证答案，按质量/难度/学习价值过滤

Expansion  →  模型解决这些任务，审计轨迹
              迭代改进 HCP 文件中的 Harness 配置
              直到收益减少

Update     →  用优化后的轨迹 + HCP 配置训练模型
              更新的模型可以生成更难的任务 → 循环
```

MindForge 的特殊之处：它把**生产环境的 Harness**（Router Tool、工具调用 tokenization、内存布局）直接带入 RL 训练循环。训练时模型观察到的环境，和推理时完全相同。

### HCP（Harness Context Protocol）

HCP 是 MindForge 和生产 Serving 的通信层——把 AGENTS.md 文件、skills、hooks、system instruction、模型-provider 配置整合成单一标准格式。

训练和服务共用同一套 HCP schema：训练轨迹里的 Harness 配置，到推理时原封不动可用。

---

## 六、Benchmark 结果

| Benchmark | Macaron V1 | GLM 5.2 | GPT 5.5 | Claude Opus 4.8 | Gemini 3.1 Pro |
|---|---:|---:|---:|---:|---:|
| ChatBench | **58.3** | 54.5 | 55.5 | 52.8 | 52.0 |
| LivingBench | **64.0** | 60.5 | 61.9 | 63.8 | 52.1 |
| PinchBench | **94.0** | 88.1 | 89.0 | 91.8 | 82.9 |
| TerminalBench 2.1 | **87.6** | 82.7 | 83.4 | 78.9 | 70.7 |
| UI4ABench | **87.8** | 67.1 | 72.1 | 75.9 | 60.3 |
| SWE Verified | 85.6 | 80.4 | 82.9 | **88.6** | 80.6 |
| DeepSWE | 58.4 | 54.9 | **70.0** | 58.0 | 10.0 |
| SWE Atlas QnA | 49.5 | 48.9 | 45.4 | **57.3** | 13.5 |

Macaron V1 在个人智能（ChatBench、LivingBench、PinchBench）和终端操作（TerminalBench）以及 Generative UI（UI4ABench）上领先全部基线。SWE 编程赛道上 Claude Opus 4.8 和 GPT 5.5 仍有优势，是 MindLab 明确标注的继续迭代方向。

---

## 七、UI4A：代码原生的 Generative UI

UI4A 是 Macaron V1 独有的能力之一，但它**不依赖模型微调**，作为通用 Harness 层单独发布。

思路：允许模型直接写 HTML，并通过 NPM registry 或任意 URL import 组件库。模型不是"根据 UI 描述生成文本"，而是**直接生成可运行的交互式界面代码**。

Macaron V1 的 L3 GenUI 专家针对 UI4A 进行了对齐训练，覆盖了 UI 驱动行为（A2UI，Agent to UI）。

---

## 八、技术判断

Macaron-V1 的发布揭示了几个在工程上值得关注的趋势：

**1. MoL 作为"能力分区"的新形式**：相比于在同一个大型 MoE 内拥挤所有能力，MoL 的插拔架构允许专家独立训练和更新，甚至支持来自不同团队的专家在同一个基础模型上组合——白皮书里称之为"Collective Intelligence"。

**2. Harness 作为训练一等公民**：MindForge 把生产 Harness 直接带入 RL 训练循环。这与 CMU 那篇 Harness 适配论文的方向吻合：模型能力的提升，和围绕模型运行的脚手架的提升，应该同步进行。

**3. LongStraw 证明 RL 训练不必在上下文长度上妥协**：以往 SLM 在长上下文 RL 上的局限是一个工程约束，不是根本瓶颈。LongStraw 的 Resident State 设计让 2M+ token RL 训练在 8×H20 下成为可能。

> 模型：huggingface.co/mindlab-research/Macaron-V1-Venti  
> Coding 变体：huggingface.co/mindlab-research/Macaron-V1-Coding-Venti  
> MoL Harness：github.com/MindLab-Research/Mixture-of-LoRA-Harness  
> LongStraw：github.com/MindLab-Research/longstraw  
> Macaron Artifacts（Claude Code 插件）：github.com/MindLab-Research/macaron-artifacts  
> 发布博客：macaron.im/mindlab/research/introducing-macaron-v1  
> 授权：MIT

<!--EN-->

## Macaron-V1-Venti: Mixture-of-LoRA + GLM-5.2, A New Paradigm for Personal Agents and Generative UI

On July 21, 2026, MindLab Research released Macaron-V1 — their first official agent model release following Macaron-V1-Preview.

The core design isn't MoE (Mixture of Experts) in the conventional sense. It's a direction that's rarely productized: **Mixture of LoRA (MoL)** — a frozen large base model plus lightweight LoRA specialists, with an L0 router dispatching based on task type.

748B parameters, MIT open-source license, weights on HuggingFace.

---

## The Model Family

Macaron-V1 ships in two size variants:

| Variant | Total Params | Base Model | LoRA Experts | Target |
|---|---|---|---|---|
| Macaron-V1-Venti | 748B | GLM-5.2 (744B) | 4 × 1B | Flagship, cloud |
| Macaron-V1-Tall | 50B | Qwen3.6-35B-A3B | 4 × 3.7B (Rank-64) | Local deployment |

Venti is the first model to be post-trained on GLM-5.2 — worldwide.

---

## Mixture-of-LoRA Architecture

### The Core Idea

Traditional MoE places multiple experts inside FFN layers, routing token-level neural activations.

MoL takes a completely different approach: **the base model's weights are fully frozen**. Specialist capabilities are added via LoRA adapter layers. Routing happens at the **user request level**, not the token level:

```
User Request
  ↓
L0 (Chat LoRA)  ← routing decision
  ↓
L1 / L2 / L3   ← execution
  ↓
Summary         ← cross-adapter memory sync
```

The four LoRA specialist assignments:

| Adapter | Role | Best At |
|---|---|---|
| L0 Chat | Conversation backbone + routing entry | Daily conversation, instruction following |
| L1 Agent | Heavy tool use | Long-horizon tasks, personal life scenarios, dynamic workflows |
| L2 Coding | Code understanding + execution | SWE tasks, terminal use, repository workflows |
| L3 GenUI | Generative UI | UI4A rendering, UI-driven actions |

### The Three-Step Runtime Flow

Every new user request goes through three steps:

1. **Route**: L0 selects the most suitable specialist adapter
2. **Answer**: The selected adapter generates a reply from its own conversation view
3. **Summary**: The selected adapter produces a cross-adapter summary (not returned to client)

This Summary is stored in the Proxy to maintain task continuity across specialist switches — neither forcing every specialist to process the full conversation history, nor losing results from the previous task.

Tool calls don't trigger re-routing. Once a tool call is issued by an adapter, subsequent tool results are handled by the same adapter.

### Why This Design Is Interesting

MoL is fundamentally **capability partitioning by task type**, not sparse parameter activation in the traditional sense.

Advantages:
- Base model weights unchanged → new specialists can be plugged/unplugged without affecting existing capabilities
- Each specialist is only 1B params → adding a new specialist is extremely cheap
- Prefix-cache-friendly: each specialist has fixed system prompts, so vLLM's KV prefix cache can be reused across requests

---

## Serving: The MoL Harness

MindLab open-sourced the [MoL serving harness](https://github.com/MindLab-Research/Mixture-of-LoRA-Harness), built on vLLM or SGLang's native multi-LoRA support.

Architecture:

```
OpenAI Client
    |
    v
MoL Proxy :8200
    |  route → answer → summary
    v
vLLM / SGLang :8000
    |
    +-- L0  Chat
    +-- L1  Agent
    +-- L2  Coding
    `-- L3  GenUI
```

Venti serving specs: TP8, 262K token context, `max_num_seqs=8`, `gpu_memory_utilization=0.915`, 141 model shards, 8 GPUs required.

---

## LongStraw: Million-Token RL Training

This is the most valuable piece of Macaron-V1 at the engineering level.

### The Problem

Inference engines can already handle million-token context windows, but RL training can't.

The reason: inference only needs to discard the forward graph after prefill; RL training must simultaneously retain activations, score multiple responses, and accumulate gradients over the same prompt. On fixed hardware, this caps effective training context length around 256K even when inference reaches 1M tokens.

### LongStraw's Solution

Change the fundamental unit of training — **turn the prompt into a reusable Resident State**:

1. The entire prompt is forward-computed once, producing a Resident State
2. Multiple candidate responses each do lightweight replay on the Resident State
3. Gradients from each response accumulate separately
4. One distributed parameter update

Prompt length goes from a "full-sequence memory problem" to a "state lifetime problem": the long prompt is paid for once, while the live gradient graph follows only the short response branch.

### Measured Scale

| Hardware | Model | Context |
|---|---|---|
| 8×H20 | Qwen3.6-27B | 2.1M token GRPO |
| 8×H20 | Resident-prefix path | 4.46M tokens |
| 32×H20 | GLM-5.2 (78-layer MLA/DSA, 256-expert MoE) | 2.1M token full training |

[Paper](https://huggingface.co/papers/2607.14952) and [code](https://github.com/MindLab-Research/longstraw) are both open-sourced.

---

## Training Infrastructure: MinT + MindForge

### MinT

Mind Lab's post-training platform, enabling V1 at this scale:

- **Adapter-only handoff**: only LoRA weights transfer between actor and learner, eliminating the need to move full model weights
- **Million-scale adapter catalog**: naturally aligned with MoL's plug-in specialist architecture
- **End-to-end support for models up to one trillion parameters**

### MindForge: Recursive Self-Improvement (RSI)

The RSI three-stage closed loop:

```
Discovery  →  From seed tasks, model constructs harder/more diverse tasks
              Auto-verifies answers, filters by quality/difficulty/learning value

Expansion  →  Model solves selected tasks, audits trajectories
              Iteratively improves harness config in HCP files
              Until gains diminish

Update     →  Train model on optimized trajectories + HCP configs
              Updated model generates harder tasks → cycle repeats
```

MindForge's distinctive feature: it brings the **production harness** (Router Tool, tool-call tokenization, memory layout) directly into the RL training loop. The environment the model observes during training rollouts is identical to what it sees in production.

### HCP (Harness Context Protocol)

HCP is the communication layer between MindForge and production serving — consolidating AGENTS.md files, skills, hooks, system instructions, and model-provider configurations into a single standardized format.

Training and serving share the same HCP schema: harness configurations from training trajectories are directly usable at inference time.

---

## Benchmark Results

| Benchmark | Macaron V1 | GLM 5.2 | GPT 5.5 | Claude Opus 4.8 | Gemini 3.1 Pro |
|---|---:|---:|---:|---:|---:|
| ChatBench | **58.3** | 54.5 | 55.5 | 52.8 | 52.0 |
| LivingBench | **64.0** | 60.5 | 61.9 | 63.8 | 52.1 |
| PinchBench | **94.0** | 88.1 | 89.0 | 91.8 | 82.9 |
| TerminalBench 2.1 | **87.6** | 82.7 | 83.4 | 78.9 | 70.7 |
| UI4ABench | **87.8** | 67.1 | 72.1 | 75.9 | 60.3 |
| SWE Verified | 85.6 | 80.4 | 82.9 | **88.6** | 80.6 |
| DeepSWE | 58.4 | 54.9 | **70.0** | 58.0 | 10.0 |
| SWE Atlas QnA | 49.5 | 48.9 | 45.4 | **57.3** | 13.5 |

Macaron V1 leads all baselines on personal intelligence (ChatBench, LivingBench, PinchBench), terminal use (TerminalBench), and Generative UI (UI4ABench). In the SWE coding track, Claude Opus 4.8 and GPT 5.5 still have an edge — an area MindLab has explicitly flagged for continued iteration.

---

## Technical Verdict

Macaron-V1's release highlights several engineering trends worth watching:

**1. MoL as a new form of capability partitioning**: Compared to crowding all capabilities inside one large MoE, MoL's plug-in architecture allows specialists to be independently trained and updated, even enabling specialists from different teams to compose on the same base model — what the whitepaper calls "Collective Intelligence."

**2. Harness as a first-class training citizen**: MindForge brings the production harness directly into the RL training loop. This aligns with the direction of CMU's harness adaptation paper: improvements to model capability and improvements to the surrounding scaffold should happen in tandem.

**3. LongStraw proves RL training doesn't have to compromise on context length**: The previous limitation of SLMs on long-context RL was an engineering constraint, not a fundamental bottleneck. LongStraw's Resident State design makes 2M+ token RL training practical on 8×H20.

> Model: huggingface.co/mindlab-research/Macaron-V1-Venti  
> Coding variant: huggingface.co/mindlab-research/Macaron-V1-Coding-Venti  
> MoL Harness: github.com/MindLab-Research/Mixture-of-LoRA-Harness  
> LongStraw: github.com/MindLab-Research/longstraw  
> Macaron Artifacts (Claude Code plugin): github.com/MindLab-Research/macaron-artifacts  
> Launch blog: macaron.im/mindlab/research/introducing-macaron-v1  
> License: MIT
