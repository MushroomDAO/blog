---
title: "AReaL 2.0：让已部署的 Agent 持续自我进化的工程指南"
titleEn: "AReaL 2.0: An Engineering Guide to Self-Evolving Deployed Agents"
description: "蚂蚁集团、港科大、清华联合提出的下一代 Agentic RL 系统论文，核心问题：企业级 Agent 部署后就「冻结」了，没有系统基础设施支撑它从真实交互中持续学习。本文分析三大支柱（ATDP轨迹协议、数据代理、演进控制平面），并提供基于开源 AReaL 框架的开发者接入指南。"
descriptionEn: "AReaL 2.0 (Ant Group + HKUST + Tsinghua) addresses why enterprise agents freeze after deployment. Three pillars: ATDP trajectory protocol, agentic data proxy, evolution control plane. Practical guide for integrating AReaL's online RL into existing agent services — just replace base_url."
pubDate: "2026-07-02"
updatedDate: "2026-07-02"
category: "Research"
tags: ["强化学习", "Agent", "自我进化", "AReaL", "蚂蚁集团", "在线RL", "LLM训练", "开源"]
heroImage: "../../assets/images/areal-agent-self-evolution-developer-guide-banner.jpg"
---

> **论文**: [arXiv:2607.01120](https://arxiv.org/abs/2607.01120) — "Next-Generation Agentic Reinforcement Learning Systems Enable Self-Evolving Agents"  
> **GitHub**: [areal-project/AReaL](https://github.com/areal-project/AReaL) · ⭐ 5,400+ · Apache 2.0  
> **作者机构**: 蚂蚁集团 (Ant Group) + 香港科技大学 (HKUST) + 清华大学

---

## 问题：Agent 为什么总是"冻结"在部署那一刻？

你在生产环境里部署了一个 LLM Agent。它的权重、系统提示、工具列表、上下文 Harness——这一切在上线那天就固定了。

任何改进都需要一个痛苦的人工循环：
1. 收集人工标注数据
2. 离线微调模型
3. 修改 Agentic 范式
4. 重新部署

与此同时，Agent 每天在处理数千条真实用户请求，积累的轨迹数据全部当做日志扔掉了——这些恰恰是让 Agent 变得更好的最宝贵素材。

**AReaL 2.0** 这篇论文的核心主张是：我们现在卡住的地方不是 RL 算法，而是支撑 **在线自我进化** 所需的系统基础设施还不存在。

---

## 三大缺失的基础设施支柱

论文识别出三个目前企业级 Agentic RL 系统都缺少的关键部分：

### 支柱一：ATDP — Agent 轨迹数据协议

**核心问题**：现有 Agent 的日志格式是碎片化、框架特定的，根本无法用来做 RL 训练。

ATDP (Agent Trajectory Data Protocol) 定义了一个标准化的轨迹表示，把每一步记录为：

```
eₜ = ⟨oₜ, hₜ, aₜ, yₜ, rₜ, mₜ⟩
```

| 字段 | 含义 | 示例 |
|---|---|---|
| `oₜ` | 可观测状态 | 工具输出、检索结果、用户消息 |
| `hₜ` | 隐含内部状态 | 规划草稿、推理摘要、置信度 |
| `aₜ` | 选择的动作 | 工具调用（含类型化参数）、生成的 token |
| `yₜ` | 动作结果 | 工具返回值、用户接受/编辑/删除 |
| `rₜ` | 奖励信号 | 二元结果、标量分数、自然语言评价 |
| `mₜ` | 元数据 | 延迟、token 数、成本、租户、Harness 版本 |

**关键设计原则**：
- **信用可归因**：每步轨迹记录完整决策上下文，可以回答"是哪个工具调用、哪条检索结果导致了这次失败？"
- **延迟绑定奖励**：用户在下一轮对话里的纠正、失败的测试用例、后置的人工标注——这些迟到的奖励信号应该可以补充进已有轨迹，而不是丢弃
- **版本化可回放**：每个事件必须包含精确的执行环境快照（Harness 版本、工具 schema、检索索引快照、模型 checkpoint），否则"Agent 经验"只有统计价值，没有可重现性
- **受治理的可观测性**：脱敏状态、数据分类标签、租户 ID、保留策略、训练资格——这些从数据捕获第一步就要内置，而不是事后补救

---

### 支柱二：Agentic Data Proxy — 企业级数据代理

**核心问题**：知道要记录什么（ATDP），还要解决怎么从复杂的企业环境里实际捕获到它。

数据代理的定位不是 API 网关、不是 tracing 工具、不是日志服务——它是把**生产流量转化为有治理的学习素材**的核心机制。

数据代理坐在 Agent 和以下所有组件之间：
- LLM 推理后端（内部部署或外部提供商）
- 工具层
- 短期/长期记忆系统
- 人类反馈通道

**关键能力**：

```
现有 Agent 框架（LangChain / CrewAI / OpenAI Agents SDK / Claude Agent SDK）
            ↓  无侵入拦截
        Agentic Data Proxy
            ↓
    ┌───────────────────────────────────┐
    │  无损 ATDP 序列化                  │
    │  回放能力（非监控日志，是训练数据）   │
    │  跨租户聚合 + 隔离                 │
    │  奖励收割（用户回复/测试失败/人工纠正）│
    │  数据治理（脱敏/访问控制/学习资格）  │
    └───────────────────────────────────┘
            ↓
    在线 RL 训练队列
```

一个关键区分：**监控代理**记录"Agent 调用工具 X 失败了"；**学习代理**还要能回答"如果用不同的提示/模型/记忆检索策略，Agent 会成功吗？"——这需要回放能力，而现有监控栈根本不支持。

---

### 支柱三：Agent Evolution Control Plane — 演进控制平面

**核心问题**：有了轨迹数据，如何自动判断何时该更新、更新什么？

控制平面在任意时刻 t 观察一个窗口内的 ATDP 轨迹 `Dₜ`，选择最优的演进动作 `u*`：

```
u* = argmax [JA(u | Aₜ, Dₜ)]
         u ∈ U
```

**可选的演进动作 U**：
| 动作类型 | 适用场景 |
|---|---|
| 更新策略 LLM 权重 | 同类失败横跨多个租户、任务、工具配置 |
| 更新 In-context Harness | 工具路由失败、检索格式问题、guardrail 措辞问题 |
| 更新记忆 `Mₜ` | 轨迹中反复出现可复用的事实或流程 |
| 更新工具 schema | 工具调用错误集中在特定参数格式 |
| 回滚 | 金丝雀评测下降 |
| No-op | 当前表现符合预期 |

**自动触发条件**（而不是人工巡检）：评估分数、用户纠正率、流程奖励估计、工具失败集群、金丝雀 delta、每次成功任务的成本。

---

## AReaL 2.0 原型：工程实现

论文的 AReaL 2.0 原型专注于三大支柱中最可落地的一个分支：**在线策略模型权重更新**。

### 架构：四核心组件

```
已有 Agent 服务（Hermes / 你自己的 Agent）
   │
   │  只改这一行：base_url = "http://areal2.0-gateway"
   ↓
┌──────────────┐
│   Gateway    │  ← 暴露为标准 LLM 推理端点（OpenAI-compatible）
└──────┬───────┘
       ↓
┌──────────────┐
│    Router    │  ← 会话亲和管理，多个 RL 训练任务并发
└──────┬───────┘
       ↓
┌──────────────┐
│  Data Proxy  │  ← 拦截、序列化、准备训练数据
└──────┬───────┘
       ↓
┌──────────────────────────────┐
│  Agent-Compute Worker        │
│  ┌─────────────┐ ┌──────────┐│
│  │  SGLang/vLLM│ │Megatron/ ││
│  │  推理服务    │ │FSDP 训练 ││
│  └─────────────┘ └──────────┘│
└──────────────────────────────┘
```

**核心设计理念**：`替换推理端点，而非重写 Agent`。

Agent 服务继续通过普通的推理 API 发请求（OpenAI 兼容格式），AReaL 2.0 在后端透明地完成轨迹捕获 → 数据准备 → 在线 RL 训练 → 权重更新的闭环。

---

## 开发者实操：5 步接入 AReaL 在线 RL

### 前提条件

- CUDA GPU（单节点或多节点集群）
- Python 3.10+
- 已有一个基于 LLM 推理 API 的 Agent 服务

### 第一步：克隆并安装 AReaL

```bash
git clone https://github.com/areal-project/AReaL
cd AReaL

# 安装 uv（推荐的包管理器）
pip install uv

# 安装预编译的 flash-attn（避免从源码编译）
uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3+cu128torch2.9-cp312-cp312-linux_x86_64.whl"

# 安装 CUDA 版本（含 SGLang 推理后端）
uv sync --extra cuda

# 可选：如果你更偏好 vLLM 作为推理后端
# cp pyproject.vllm.toml pyproject.toml
# cp uv.vllm.lock uv.lock
# uv sync --extra cuda
```

### 第二步：验证安装（跑一个数学推理任务）

```bash
# 单节点验证（自动下载 Qwen2-1.5B 和 GSM8K 数据集）
python3 examples/math/gsm8k_rl.py \
  --config examples/math/gsm8k_grpo.yaml \
  scheduler.type=local
```

看到训练曲线上升说明环境 OK。

### 第三步：选择合适的 RL 算法

AReaL 支持 10+ 种算法，选哪个取决于你的场景：

| 场景 | 推荐算法 | 配置文件 |
|---|---|---|
| **快速验证**（资源有限） | GRPO | `gsm8k_grpo.yaml` |
| **稳定长训练** | PPO | `gsm8k_ppo.yaml` |
| **抗奖励 Hacking** | DAPO | `gsm8k_dapo_dynamic_bs.yaml` |
| **低显存 LoRA** | GRPO + LoRA | `gsm8k_grpo_lora.yaml` |
| **MoE 大模型** | GSPO | `gsm8k_gspo.yaml` |
| **多轮 Agentic** | GRPO/PPO 异步版 | `max_head_offpolicyness > 0` |

**关键参数**：所有算法均支持同步/异步模式。异步模式（`max_head_offpolicyness > 0`）在多卡集群上吞吐量提升 2.77×，适合生产 Agentic 训练。

### 第四步：接入你自己的 Agent（OpenClaw 模式）

这是论文中最重要的工程创新——对现有 Agent **零代码改动**：

```python
# 你原来的 Agent 代码（任意框架：LangChain、CrewAI、OpenAI SDK...）
from openai import OpenAI

client = OpenAI(
    # ← 只改这一行，从你的推理服务换成 AReaL 网关
    base_url="http://your-areal-gateway:8080/v1",
    api_key="your-areal-api-key"
)

# 以下代码完全不变
response = client.chat.completions.create(
    model="Qwen2.5-7B-Instruct",
    messages=[{"role": "user", "content": user_input}],
    tools=your_tools,
)
```

AReaL 2.0 的 Gateway 暴露标准 OpenAI-compatible 接口。替换 `base_url` 之后：
- Agent 照常处理工具调用、多轮对话、记忆更新
- AReaL 在后台透明捕获每一步轨迹
- 在线 RL 训练循环持续更新模型权重
- 更新后的权重自动推送到推理工作节点

详见官方示例：[examples/openclaw/](https://github.com/areal-project/AReaL/tree/main/examples/openclaw/)

### 第五步：生产集群部署

```bash
# Ray 集群（推荐生产环境）
python3 examples/math/gsm8k_rl.py \
  --config examples/math/gsm8k_grpo.yaml \
  cluster.n_nodes=2 \
  cluster.n_gpus_per_node=8 \
  cluster.fileroot=/path/to/nfs \
  scheduler.type=ray
```

云部署（GCP/AWS/Kubernetes）可参考：[examples/skypilot/](https://github.com/areal-project/AReaL/tree/main/examples/skypilot/)

---

## 支持矩阵速查

### 模型支持

| 模型家族 | Megatron | PyTorch FSDP | 备注 |
|---|---|---|---|
| **Qwen2/3** | ✅ | ✅ | 最成熟，推荐首选 |
| **Qwen3-MoE** | ✅ | ✅ | 大模型首选 |
| **Qwen2.5-VL / Qwen3-VL** | ❌ | ✅ | 视觉语言模型 |
| **Gemma 3** | ❌ | ✅ | 视觉语言模型 |
| **其他 HuggingFace LLM** | ❌ | ✅ | 依赖 transformers 版本 |

### 推理后端对比

| 后端 | 吞吐量 | 特殊功能 | 适用场景 |
|---|---|---|---|
| **SGLang** | 更高 | Data Parallel Attention、Expert Parallel | MoE 模型、生产 |
| **vLLM** | 较高 | Pipeline Parallel | 通用场景 |

### 硬件支持

- **NVIDIA GPU**：主线支持，`main` 分支
- **Ascend NPU（华为昇腾）**：稳定支持，`ascend` 分支

---

## 低资源方案：LoRA 在线 RL

如果 GPU 资源有限，不足以全量微调：

```yaml
# gsm8k_grpo_lora.yaml 关键配置
lora:
  enable: true
  rank: 16
  alpha: 32
  target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
```

LoRA 方案：
- 显存占用降低 60-70%
- 训练速度接近全量微调
- 适合单卡 A100/H100 跑 7B 模型在线 RL

---

## 架构决策指南：何时触发哪种演进？

基于论文中控制平面的设计，结合工程实践：

```
症状                              → 建议动作
─────────────────────────────────────────────────────
工具调用 schema 错误频繁            → 更新工具描述 / schema（Harness 编辑）
同一类型问题反复出现，窗口很窄       → 写入记忆（最便宜，最快）
某类推理错误横跨多个用户/任务        → 触发在线 RL 权重更新
Canary 评测分数下降 > 阈值          → 回滚到上一版本
成功率持续提升但成本也在上涨         → 检查 token 预算配置
单租户特有问题                      → 隔离数据，仅用该租户轨迹微调
```

---

## 当前局限与路线图

**AReaL 2.0 原型的范围**：

论文作者明确声明，当前实现只覆盖了"策略 LLM 权重更新"这一个分支。完整的自我进化系统还需要：

- [ ] 完整的 ATDP 实现（含步骤级决策上下文和治理元数据）
- [ ] 完整的数据代理（捕获工具/检索/记忆/文件/浏览器/人类反馈/延迟奖励）
- [ ] 回放和反事实评估支持
- [ ] 租户感知的隐私和训练资格执行
- [ ] 自动多面演进控制平面（自动选择：记忆更新/技能补丁/Harness 编辑/工具 schema 变更/策略更新/回滚/No-op）

未来方向：**AReaL-AutoPilot**（自动化演进控制平面）。

---

## 相关工具生态

- **ASearcher**：基于 AReaL 的端到端搜索 Agent
- **AReaL-SEA**：自进化数据合成引擎（235B MoE 模型超越 GPT-5 的方案）
- **AReaL-lite**：轻量版，算法优先 API，代码量减少 80%，适合研究者快速原型

---

## 核心总结

| 问题 | AReaL 2.0 答案 |
|---|---|
| 为什么要关注？ | 企业 Agent 部署后会冻结，RL 算法不是瓶颈，缺的是系统基础设施 |
| 三大支柱是什么？ | ATDP 轨迹协议 + 企业数据代理 + 演进控制平面 |
| 接入成本多高？ | 只换 `base_url`，现有 Agent 代码零改动 |
| 算法选哪个？ | 快速验证选 GRPO；生产选 DAPO；低资源选 GRPO+LoRA |
| 现在能落地什么？ | 在线策略权重更新（AReaL 2.0 原型），三大支柱完整实现仍在研究中 |

**GitHub**：[areal-project/AReaL](https://github.com/areal-project/AReaL)  
**文档**：[areal-project.github.io/AReaL](https://areal-project.github.io/AReaL/)  
**论文**：[arXiv:2607.01120](https://arxiv.org/abs/2607.01120)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: AReaL 2.0 (Ant Group + HKUST + Tsinghua) is a paper + open-source system targeting the core problem of enterprise agents freezing at deployment. The fix: three system pillars (trajectory protocol, data proxy, evolution control plane) + a low-intrusion online RL loop that lets deployed agents learn from their own traffic. Just replace `base_url` to connect any OpenAI-compatible agent. 5,400+ GitHub stars, Apache 2.0.

---

## Why This Matters

Every production LLM agent has the same problem: it freezes the moment it deploys. Weights, prompts, tools — all locked. Any improvement requires a manual cycle of data collection → offline fine-tuning → re-deployment. Meanwhile, the agent processes thousands of real interactions daily, generating the perfect training data that nobody captures.

AReaL 2.0's argument: **RL algorithms are not the bottleneck. Missing system infrastructure is.**

## The Three Pillars

**Pillar 1 — ATDP (Agent Trajectory Data Protocol)**  
A standardized schema where each step `eₜ = ⟨oₜ, hₜ, aₜ, yₜ, rₜ, mₜ⟩` captures observable state, hidden context, chosen action, outcome, reward, and metadata. Key properties: credit-assignable (which tool call caused failure?), late-bound rewards (user corrections in later turns), versioned replays (exact harness + tool schema at time of execution), enterprise governance (redaction, tenant isolation, training eligibility).

**Pillar 2 — Agentic Data Proxy**  
Sits between agent and all backends (LLM, tools, memory, human feedback). Intercepts without framework lock-in (LangChain, CrewAI, OpenAI SDK, Claude SDK, MCP — all work). Converts production traffic into governed, replayable ATDP trajectories. Critical distinction: a *monitoring* proxy logs "tool X failed"; a *learning* proxy enables asking "would it have succeeded with a different prompt or model?"

**Pillar 3 — Evolution Control Plane**  
Automatically decides *when* to evolve and *what* to change based on trajectory statistics (evaluation scores, correction rates, failure clusters, canary deltas). Actions: update LLM weights via RL, patch in-context harness, insert memory, edit tool schema, rollback, or no-op. Human-triggered triggers → trajectory-statistics-triggered triggers.

## AReaL 2.0 Prototype: Zero-Code Agent Integration

The key engineering insight: **replace `base_url`, not your agent**.

```python
client = OpenAI(
    base_url="http://your-areal-gateway:8080/v1",  # only this line changes
    api_key="your-areal-api-key"
)
```

AReaL 2.0's gateway is OpenAI-compatible. Behind it: Gateway → Router (session affinity) → Data Proxy (trajectory capture) → Agent-Compute Worker (inference + training). Your agent workflow doesn't change; AReaL captures trajectories and runs online RL asynchronously.

## Quick Start

```bash
git clone https://github.com/areal-project/AReaL && cd AReaL
pip install uv
uv pip install flash_attn-2.8.3+cu128torch2.9-cp312-cp312-linux_x86_64.whl  # pre-built
uv sync --extra cuda

# Validate on single node (downloads Qwen2-1.5B + GSM8K automatically)
python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml scheduler.type=local
```

## Algorithm Selection

| Use case | Algorithm | Config |
|---|---|---|
| Fast validation | GRPO | `gsm8k_grpo.yaml` |
| Production stable | PPO | `gsm8k_ppo.yaml` |
| Anti-reward hacking | DAPO | `gsm8k_dapo_dynamic_bs.yaml` |
| Low GPU memory | GRPO + LoRA | `gsm8k_grpo_lora.yaml` |
| MoE large model | GSPO | `gsm8k_gspo.yaml` |

## Hardware Support

- NVIDIA GPU: main branch
- Huawei Ascend NPU: `ascend` branch (stable since Jan 2026)
- Cloud: SkyPilot integration (GCP, AWS, Kubernetes)

## Current Scope + Roadmap

AReaL 2.0 prototype covers only **policy weight updates** — one branch of the full vision. Complete self-evolving agent system still needs: full ATDP with step-level governance metadata, complete data proxy (tools/memory/human feedback/delayed rewards), replay/counterfactual evaluation, multi-surface automatic control plane (memory/skill/harness/tool-schema/weights/rollback). That's the research agenda AReaL-AutoPilot is targeting.

**Links**: [GitHub](https://github.com/areal-project/AReaL) · [Docs](https://areal-project.github.io/AReaL/) · [Paper](https://arxiv.org/abs/2607.01120)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
