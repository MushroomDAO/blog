---
title: "HarnessX：脚手架即进化对象——9B 模型 ALFWorld 从 53% 飙到 97% 的秘密"
titleEn: "HarnessX: Scaffold as Evolvable Object — How a 9B Model Jumped from 53% to 97% on ALFWorld"
description: "小米 Darwin Agent 团队提出 HarnessX，将 Agent 脚手架（prompt、工具、记忆、控制流）作为可进化对象，用执行轨迹驱动自动迭代。5 个 benchmark 平均提升 14.5pp，9B 模型 ALFWorld 从 53%→97%，不换模型、不加数据。本文深度解析 HarnessX 的核心思路和工程落地方法。"
descriptionEn: "Xiaomi Darwin Agent Team's HarnessX treats agent scaffolding (prompt, tools, memory, control flow) as evolvable objects, driving automatic iteration from execution traces. Average +14.5pp on 5 benchmarks; a 9B model jumps from 53% to 97% on ALFWorld without changing the model or data. Deep analysis and engineering guide."
pubDate: "2026-07-26"
updatedDate: "2026-07-26"
category: "Research"
tags: ["Agent", "HarnessX", "脚手架进化", "Darwin Agent", "小米", "ALFWorld", "自进化", "工程实践"]
heroImage: "../../assets/images/harnessx-agent-scaffold-evolvable-darwin-team-xiaomi-banner.jpg"
---

> **论文**：HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry
> **团队**：Darwin Agent Team（小米）
> **核心数据**：5 个 benchmark 平均 +14.5pp；9B 模型 ALFWorld 53%→97%

---

## 一、一个让人不舒服的问题

你有没有想过，你花几周时间调出来的 Agent，它能不能评价自己的脚手架有多烂？

绝大多数 Agent 工程的迭代模式是：人工分析失败 case，手动调整 prompt，换换工具定义，加点 few-shot，再跑一遍评估，看看有没有提升。这个循环是人驱动的，效率低、主观性强，而且**每次调整的脉络都在脑子里，不在代码里**。

HarnessX 的核心判断是：**脚手架本身可以是进化的对象**。

不是让模型变聪明，不是加更多数据——而是让脚手架（prompt、工具、记忆机制、控制流）从每次执行的轨迹中学习，自动迭代成更好的版本。

结果是：在相同模型、相同数据下，9B 的小模型在 ALFWorld 上从 53% 涨到 97%。差这么多的那个部分，全都来自脚手架。

---

## 二、什么是 Agent 脚手架（Harness）

在讨论 HarnessX 之前，先澄清「脚手架」这个词在 Agent 工程里的意思。

传统的 Agent 架构可以拆成两层：

```
┌──────────────────────────────────────────────┐
│  LLM（语言模型）                              │
│  — 推理能力、知识、上下文理解                 │
├──────────────────────────────────────────────┤
│  Harness（脚手架）← HarnessX 的进化对象      │
│  — System prompt                             │
│  — 工具定义（function schemas）              │
│  — 记忆机制（short-term/long-term memory）   │
│  — 控制流（retry/branch/loop 逻辑）          │
└──────────────────────────────────────────────┘
```

大多数人关注的是「换一个更好的模型」，但模型是一个固定参数的黑盒，脚手架才是工程师能直接控制的变量。

现有 Agent 框架（LangChain、LlamaIndex、AutoGen 等）提供了脚手架的**构件**，但没有提供脚手架的**进化机制**。每次改了 prompt 或者工具定义，你不知道这个改动是好是坏，也不知道什么样的组合对当前 benchmark 最优。

HarnessX 把这个问题形式化：**把脚手架视为可搜索的设计空间，用执行轨迹作为优化信号**。

---

## 三、HarnessX 的三个核心设计原则

### 3.1 可组合（Composable）

HarnessX 的脚手架是组件化的。每个 prompt 片段、每个工具、每个记忆模块都是独立的可替换单元，可以像积木一样组合。

这不只是工程上的「模块化」，它还是进化的前提——只有当组件是独立可替换的，进化算法才能在不破坏整体的前提下修改局部。

典型的组件粒度：

```python
# prompt 组件
class ReasoningInstruction(HarnessComponent):
    content: str           # 可进化的字段
    placement: str         # "system" | "before_tools" | "before_response"

# 工具组件
class ToolSpec(HarnessComponent):
    name: str
    description: str       # 可进化：description 影响模型调用频率
    schema: dict
    retry_policy: RetryConfig

# 记忆组件
class MemoryConfig(HarnessComponent):
    backend: str           # "episodic" | "semantic" | "none"
    retrieval_topk: int    # 可进化
    summarize_threshold: int  # 可进化
```

### 3.2 自适应（Adaptive）

脚手架可以根据任务类型自动切换配置。HarnessX 维护一个配置空间，不同类型的任务映射到不同的脚手架变体。

这个映射本身也可以进化：系统根据历史任务的成功率，学习「什么样的任务该用什么样的脚手架」。

### 3.3 可进化（Evolvable）

这是 HarnessX 最核心的部分。

进化的驱动信号来自**执行轨迹**：每次 Agent 完成（或失败完成）一个任务，系统记录整个执行过程——哪个工具被调用了几次、哪步推理失败了、哪个 prompt 片段触发了错误的行为。

基于这些轨迹，HarnessX 用一个进化算法对脚手架配置进行修改、评估、选择：

```
当前脚手架 H_t
    ↓
执行 N 个任务，收集轨迹 T = {τ₁, τ₂, ..., τₙ}
    ↓
轨迹分析：识别高频失败模式
    ↓
生成脚手架变体 H' = mutate(H_t, failure_patterns)
    ↓
在验证集上评估 H'
    ↓
选择更好的变体 H_{t+1}
    ↓
（下一轮迭代）
```

关键是 **failure pattern 的提取**——它不是简单地看最终结果对不对，而是分析执行轨迹中每个决策点的行为，定位是 prompt 导致的错误推理，还是工具定义导致的错误调用，还是控制流设计导致的死循环。

---

## 四、为什么 9B 模型能在 ALFWorld 上达到 97%

ALFWorld 是一个家居环境中的自然语言任务基准：「找到一支蜡烛，放到微波炉旁边的台子上」。听起来简单，但对小模型来说，多步推理+工具调用+状态追踪的组合是真实的挑战。

9B 模型的基础能力决定了一个上限，但 53% 说明脚手架把这个上限的利用率只有一半左右。HarnessX 通过迭代做到的是：

**1. 诊断出核心失败模式**

轨迹分析发现：9B 模型在「搜索」阶段（探索环境找到目标物品）的工具调用顺序经常不对，而且在多次搜索失败后不会更换策略，陷入循环。

**2. 针对性改写 prompt 的控制逻辑**

在 system prompt 里增加了明确的搜索策略指导，规定了「同一房间搜索超过 N 次失败后换房间」的规则，用 prompt 模拟了专门的状态机逻辑。

**3. 重新定义工具的描述**

`explore` 工具的 description 从「探索环境」改成了「在当前位置系统性地检查所有可见物体，按照从左到右的顺序」，更精确的描述减少了模型的歧义判断。

**4. 加入轨迹摘要记忆**

进化后的脚手架增加了一个记忆模块：在每个 action step 后，把「已检查的位置」摘要写入短期记忆，避免模型因 context 太长忘掉已探索的地方。

这四个改动没有一个需要微调模型——都是脚手架层面的调整。HarnessX 的价值在于**自动找到这些改动**，而不是靠工程师手工分析。

---

## 五、五个 Benchmark 的提升数据

HarnessX 在以下 5 个 Agent benchmark 上验证了效果，平均提升 14.5 个百分点：

| Benchmark | 领域 | 代表能力 | 提升幅度 |
|-----------|------|---------|---------|
| ALFWorld | 家居任务 | 多步工具调用 + 状态追踪 | 44pp（9B：53%→97%） |
| WebArena | Web 操作 | 浏览器工具 + 长序列规划 | ~10pp |
| AgentBench | 综合 Agent | 代码/数据库/操作系统 | ~12pp |
| SciWorld | 科学推理 | 实验设计 + 假设验证 | ~8pp |
| GAIA | 通用助手 | 工具组合 + 复杂推理 | ~9pp |

最关键的数据点是 ALFWorld 的 9B 模型——这说明脚手架对小模型的提升效果尤其大，因为小模型更依赖外部的结构化指导来弥补内在推理能力的不足。

---

## 六、工程实践：如何把 HarnessX 的思路落地

即便没有 HarnessX 的完整实现，它的核心思路可以在任何 Agent 项目中手动实践。

### 6.1 建立执行轨迹记录

```python
import json
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentTrace:
    task_id: str
    task_description: str
    steps: list = field(default_factory=list)
    outcome: str = ""  # "success" | "failure" | "partial"
    harness_version: str = ""

    def add_step(self, step_type: str, input_data: dict, output_data: dict,
                 success: bool, notes: str = ""):
        self.steps.append({
            "step": len(self.steps) + 1,
            "type": step_type,      # "reason" | "tool_call" | "memory_update"
            "input": input_data,
            "output": output_data,
            "success": success,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        })

    def save(self, path: str):
        with open(path, 'a') as f:
            f.write(json.dumps({
                "task_id": self.task_id,
                "task": self.task_description,
                "outcome": self.outcome,
                "harness_version": self.harness_version,
                "steps": self.steps,
            }, ensure_ascii=False) + '\n')
```

### 6.2 自动分析失败模式

```python
from collections import Counter

def analyze_failure_patterns(trace_file: str, top_k: int = 5) -> list[dict]:
    """从执行轨迹中提取高频失败模式。"""
    patterns = []
    with open(trace_file) as f:
        traces = [json.loads(line) for line in f]

    failed_traces = [t for t in traces if t['outcome'] == 'failure']

    # 分析工具调用失败
    tool_failures = Counter()
    for trace in failed_traces:
        for step in trace['steps']:
            if step['type'] == 'tool_call' and not step['success']:
                tool_failures[step['input'].get('tool_name', 'unknown')] += 1

    # 分析失败发生在哪一步
    failure_positions = Counter()
    for trace in failed_traces:
        total_steps = len(trace['steps'])
        for i, step in enumerate(trace['steps']):
            if not step['success']:
                position = f"step_{i+1}_of_{total_steps}"
                failure_positions[position] += 1

    return {
        "total_failures": len(failed_traces),
        "failure_rate": len(failed_traces) / len(traces) if traces else 0,
        "top_failing_tools": tool_failures.most_common(top_k),
        "failure_positions": failure_positions.most_common(top_k),
    }
```

### 6.3 用 LLM 生成脚手架变体

```python
def generate_harness_variant(
    current_harness: dict,
    failure_analysis: dict,
    llm_client,
) -> dict:
    """根据失败分析生成脚手架改进方案。"""
    prompt = f"""你是 Agent 脚手架优化专家。

当前脚手架配置：
{json.dumps(current_harness, ensure_ascii=False, indent=2)}

执行轨迹分析（{failure_analysis['total_failures']} 次失败）：
- 失败率: {failure_analysis['failure_rate']:.1%}
- 最频繁失败的工具: {failure_analysis['top_failing_tools']}
- 失败主要发生在: {failure_analysis['failure_positions']}

请针对这些失败模式，生成一个改进的脚手架配置。
只修改最可能改善失败率的 1-3 个地方，给出修改后的完整配置和修改理由。

以 JSON 格式输出：
{{
  "modified_harness": {{...完整配置...}},
  "changes": ["改动1描述", "改动2描述"],
  "hypothesis": "这些改动应该能解决...因为..."
}}"""

    response = llm_client.chat.completions.create(
        model="default_model",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

### 6.4 进化循环的完整框架

```python
class HarnessEvolver:
    def __init__(self, agent_runner, evaluator, trace_file: str):
        self.runner = agent_runner
        self.evaluator = evaluator
        self.trace_file = trace_file
        self.harness_history = []

    def evolve(self, initial_harness: dict, task_set: list,
               n_rounds: int = 5, min_improvement: float = 0.01) -> dict:
        """迭代进化脚手架，返回最优版本。"""
        current = initial_harness
        best_score = self._evaluate(current, task_set)
        print(f"Initial score: {best_score:.3f}")

        for round_n in range(n_rounds):
            # 1. 运行 agent，收集轨迹
            self._run_with_traces(current, task_set, version=f"v{round_n}")

            # 2. 分析失败模式
            analysis = analyze_failure_patterns(self.trace_file)

            # 3. 生成变体
            variant_data = generate_harness_variant(current, analysis, self.llm)
            candidate = variant_data['modified_harness']

            # 4. 评估变体
            candidate_score = self._evaluate(candidate, task_set)
            improvement = candidate_score - best_score
            print(f"Round {round_n+1}: {candidate_score:.3f} "
                  f"({'↑' if improvement > 0 else '↓'}{abs(improvement):.3f})")
            print(f"Changes: {variant_data['changes']}")

            # 5. 选择
            if improvement >= min_improvement:
                current = candidate
                best_score = candidate_score
                self.harness_history.append({
                    "round": round_n+1,
                    "score": best_score,
                    "changes": variant_data['changes'],
                })

        return current, best_score
```

---

## 七、选型建议：什么时候应该用脚手架进化

不是所有场景都需要 HarnessX 这样的方案，选择时考虑以下因素：

**适合脚手架进化的场景**：
- 有清晰的评估指标（pass rate、任务完成率等）
- 同类型任务量大（至少几十到几百个，才有足够的轨迹数据）
- 模型已经是生产级别的最优选择（不能/不想换模型）
- 手动调优已经遇到瓶颈（凭感觉改了好几轮没进展）

**不适合的场景**：
- 任务多样性极高，每个任务都完全不同
- 没有可量化的评估标准
- 数据量太少（轨迹不够，失败模式不可靠）

---

## 八、与相关工作的关系

| 方法 | 核心思路 | HarnessX 的区别 |
|------|---------|---------------|
| Prompt 优化（APE/OPRO）| 优化单个 prompt 字符串 | HarnessX 优化整个脚手架，包括工具、记忆、控制流 |
| Self-Refine | 用模型反思改进输出 | HarnessX 改进的是脚手架，不是单次输出 |
| ReAct/Reflexion | 推理-行动循环 + 反思 | HarnessX 把反思的对象升级为脚手架本身 |
| Strategy Gene（GEP）| 紧凑经验表示 + 进化 | HarnessX 关注更完整的脚手架，GEP 关注原子级经验单元 |

HarnessX 的独特价值：**进化的粒度更粗，覆盖了整个脚手架而不只是 prompt**——工具定义、记忆配置、控制流都在进化范围内，这让它能捕捉到更系统性的失败原因。

---

*信息来源：Darwin Agent Team（小米），HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry，2026-07-26 整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: HarnessX: A Composable, Adaptive, and Evolvable Agent Harness Foundry
> **Team**: Darwin Agent Team (Xiaomi)
> **Key result**: Average +14.5pp on 5 benchmarks; 9B model jumps from 53% to 97% on ALFWorld

---

## 1. The Question That Should Make You Uncomfortable

Can the agent you just spent weeks tuning evaluate how bad its own scaffold is?

Most agent engineering iterates like this: analyze failure cases manually, adjust the prompt, tweak tool definitions, add some few-shot examples, run evaluation again, check if there's improvement. This loop is human-driven, slow, subjective, and the reasoning behind each change lives in the engineer's head, not in the codebase.

HarnessX's core claim is: **the scaffold itself can be an evolutionary object**.

Not making the model smarter, not adding more data — making the scaffold (prompt, tools, memory, control flow) learn from each execution trace and automatically iterate to a better version.

The result: same model, same data, a 9B model goes from 53% to 97% on ALFWorld. The gap between those two numbers came entirely from the scaffold.

---

## 2. What is an Agent Scaffold (Harness)?

A useful separation for any agent system:

```
┌──────────────────────────────────────────────┐
│  LLM (language model)                        │
│  — reasoning capability, knowledge, context  │
├──────────────────────────────────────────────┤
│  Harness (scaffold) ← what HarnessX evolves  │
│  — system prompt                             │
│  — tool definitions (function schemas)       │
│  — memory mechanisms (short/long-term)       │
│  — control flow (retry/branch/loop logic)    │
└──────────────────────────────────────────────┘
```

Most attention goes to "use a smarter model." But a model is a fixed-parameter black box; the scaffold is what engineers can directly control.

Existing frameworks (LangChain, LlamaIndex, AutoGen) provide scaffold *building blocks* but no scaffold *evolution mechanism*. When you change a prompt or tool definition, you don't know if it's better, and you don't know what combination is optimal for the target benchmark.

HarnessX formalizes this: **treat the scaffold as a searchable design space, use execution traces as the optimization signal**.

---

## 3. Three Design Principles

### Composable

Each prompt fragment, tool, and memory module is a standalone replaceable unit. This is the prerequisite for evolution: components must be independently substitutable for an evolution algorithm to modify parts without breaking the whole.

### Adaptive

The scaffold can automatically switch configurations based on task type. HarnessX maintains a configuration space; different task types map to different scaffold variants. The mapping itself can also evolve.

### Evolvable

This is the core. The evolution signal comes from **execution traces**: every time an agent completes (or fails to complete) a task, the system records the full execution — which tools were called, where reasoning failed, which prompt fragment triggered wrong behavior.

From these traces, HarnessX runs an evolution algorithm over scaffold configurations:

```
Current scaffold H_t
    ↓
Execute N tasks, collect traces T = {τ₁, τ₂, ..., τₙ}
    ↓
Trace analysis: identify high-frequency failure patterns
    ↓
Generate scaffold variant H' = mutate(H_t, failure_patterns)
    ↓
Evaluate H' on validation set
    ↓
Select better variant as H_{t+1}
```

The key is **failure pattern extraction** — not just looking at final pass/fail, but analyzing at each decision point in the execution trace: is this a prompt-induced reasoning error, a tool-definition-induced wrong call, or a control-flow-induced dead loop?

---

## 4. Why the 9B Model Reaches 97% on ALFWorld

ALFWorld tasks: navigate a home environment and complete natural language instructions ("Find a candle and place it on the table next to the microwave"). Simple-sounding, but multi-step tool-calling plus state tracking is a real challenge for small models.

The 9B model's base capability sets a ceiling. 53% means the scaffold was only capturing about half of what the model was capable of. What HarnessX found through iteration:

1. **Diagnosed core failure pattern**: The 9B model's search step tool-calling order was frequently wrong, and it didn't change strategy after multiple failed searches — stuck in a loop.

2. **Rewrote prompt control logic**: Added explicit search strategy guidance to the system prompt, encoding a rule: "after N failed searches in one room, switch rooms." This simulated a state-machine in prompt form.

3. **Refined tool descriptions**: Changed `explore`'s description from "explore the environment" to "systematically examine all visible objects at the current location, checking from left to right." More precise description reduced ambiguous model interpretation.

4. **Added trajectory summary memory**: A memory module that writes "already-checked locations" into short-term memory after each action step, preventing the model from forgetting explored areas when context grows long.

None of these required fine-tuning the model. HarnessX's value is **finding these changes automatically** rather than requiring an engineer to manually analyze traces.

---

## 5. Benchmark Results

Average improvement of **+14.5pp** across 5 Agent benchmarks:

| Benchmark | Domain | Core capability | Improvement |
|-----------|--------|----------------|-------------|
| ALFWorld | Home tasks | Multi-step tool use + state tracking | +44pp (9B: 53%→97%) |
| WebArena | Web operations | Browser tools + long-sequence planning | ~+10pp |
| AgentBench | General agent | Code/DB/OS tasks | ~+12pp |
| SciWorld | Scientific reasoning | Experiment design + hypothesis testing | ~+8pp |
| GAIA | General assistant | Tool composition + complex reasoning | ~+9pp |

The ALFWorld result with a 9B model is the most important data point — smaller models benefit most from scaffold evolution because they depend more on external structural guidance to compensate for weaker internal reasoning.

---

## 6. Engineering Guide: Implementing Scaffold Evolution

The core ideas can be applied in any agent project:

```python
class HarnessEvolver:
    def __init__(self, agent_runner, evaluator, trace_file: str):
        self.runner = agent_runner
        self.evaluator = evaluator
        self.trace_file = trace_file

    def evolve(self, initial_harness: dict, task_set: list,
               n_rounds: int = 5) -> dict:
        """Iteratively evolve the scaffold, return the best version."""
        current = initial_harness
        best_score = self._evaluate(current, task_set)

        for round_n in range(n_rounds):
            # 1. Run agent, collect traces
            self._run_with_traces(current, task_set, version=f"v{round_n}")

            # 2. Analyze failure patterns
            analysis = analyze_failure_patterns(self.trace_file)

            # 3. Generate variant via LLM analysis of traces
            candidate = generate_harness_variant(current, analysis, self.llm)

            # 4. Evaluate
            candidate_score = self._evaluate(candidate['modified_harness'], task_set)
            if candidate_score > best_score + 0.01:
                current = candidate['modified_harness']
                best_score = candidate_score

        return current, best_score
```

The complete 120-line implementation is available in the Chinese section of this article.

---

## 7. Relation to Other Work

| Method | Core idea | HarnessX's difference |
|--------|-----------|----------------------|
| APE/OPRO | Optimize single prompt strings | HarnessX optimizes entire scaffold including tools/memory/flow |
| Self-Refine | Model reflects on its own output | HarnessX reflects on the scaffold, not single outputs |
| ReAct/Reflexion | Reasoning-acting loop + reflection | HarnessX elevates the reflection target to the scaffold itself |
| Strategy Gene | Compact experience representation | HarnessX covers the full scaffold; GEP focuses on atomic experience units |

---

*Source: Darwin Agent Team (Xiaomi), HarnessX, 2026-07-26.*

© 2026 Author: Mycelium Protocol
