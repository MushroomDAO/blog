---
title: "NOVA：腾讯广告如何用 Agent Harness 让推荐模型架构自动进化（13x 提速，GMV +2%）"
titleEn: "NOVA: How Tencent Ads Used an Agent Harness to Automate Recommender Architecture Evolution (13x Speedup, +2% GMV)"
description: "腾讯广告推荐系统团队的 NOVA：用「架构梯度」替代人工直觉驱动推荐模型架构进化，四级验证级联阻截 silent failure，L3 任务 EPR 60%，Literature-to-Production 周期缩短 13x，线上 GMV 提升 +1.25%~+2.02%，pCVR bias 降低 37%~67%。"
descriptionEn: "Tencent Ads team's NOVA: uses 'architecture gradient' to drive automated recommender model architecture evolution, four-stage verification cascade blocks silent failures, L3 EPR 60%, Literature-to-Production cycle 13x faster, online GMV +1.25%~+2.02%, pCVR bias reduced 37%~67%."
pubDate: "2026-07-26"
updatedDate: "2026-07-26"
category: "Research"
tags: ["NOVA", "推荐系统", "Agent Harness", "架构进化", "腾讯广告", "自动化ML", "Silent Failure", "工程实践"]
heroImage: "../../assets/images/nova-verification-aware-agent-harness-recommender-tencent-banner.jpg"
---

> **论文**：NOVA: A Verification-Aware Agent Harness for Architecture Evolution in Industrial Recommender Systems
> **arXiv**：2606.27243
> **作者**：Shaohua Liu 等（腾讯广告）
> **核心指标**：L3 任务 EPR 60%，Production cycle 缩短 13x，GMV +1.25%~+2.02%

---

## 一、问题的起点：推荐模型架构进化为何如此昂贵

在大规模广告推荐系统里，模型架构进化是持续发生的事。RankMixer、TokenMixer-Large、MixFormer——每一个架构升级背后，都是数周甚至数月的工程工作：读论文、理解架构意图、把 idea 翻译成生产代码、过本地测试、过离线评估、做在线 A/B。

这条流水线有两个核心痛点：

**痛点 1：现有自动化解决了错误的问题**

AutoML 主要调超参数（学习率、隐藏层大小、嵌入维度）。但推荐模型有效的改进往往需要**跨模块的拓扑变更**：把 target attention 升级为联合 Seq-Token 建模、重设计 logit fusion 路径、用 AttentionRes 替换标准残差连接。AutoML 的搜索空间根本覆盖不到这类结构性修改。

**痛点 2：通用 LLM 编码 Agent 不够——可运行 ≠ 有效**

SWE-Agent、OpenHands 这类通用编码 Agent 优化的是软件层面的正确性（编译通过、单元测试通过）。但在推荐系统里，一段代码可能成功运行，但**悄悄破坏了架构语义**：错误地删掉了 sequence masking、把 self-attention 退化成了简单 MLP、改变了 logit fusion 路径。这类可运行但无效的候选——论文称为 **silent failure**——会拉低离线和在线指标，但在代码层面看不出来。

NOVA 就是针对这两个痛点设计的。

---

## 二、NOVA 的核心机制：架构梯度

NOVA 最重要的概念是**架构梯度（Architecture Gradient）**。

普通的梯度是对连续参数求导。推荐模型架构是离散的、有约束的，没法用标准梯度。NOVA 受 SGD 启发，设计了一个**非可微的更新信号**：

```
g_t = Grad(e_{t-1}, V_t, ΔJ_t, H_t)
```

其中：
- `e_{t-1}` = 上一次的架构修改
- `V_t` = 验证诊断结果（哪些地方失败了）
- `ΔJ_t` = 离线指标变化（AUC 涨/跌了多少）
- `H_t` = 历史轨迹（所有修改、失败、指标的记录）

架构梯度包含三种信息：

| 信息类型 | 内容 |
|---------|------|
| **弱组件**（Weak Components）| 当前架构哪些部分可能是瓶颈 |
| **修改方向**（Modification Directions）| 下一步应该探索哪些候选修改 |
| **禁止方向**（Forbidden Directions）| 哪些已经失败过的、结构无效的模式不要再试 |

这个设计的精妙在于：**失败信息不只是被丢弃，而是被转化成下一步搜索的约束**。每次验证失败都会把这个失败模式记录为 forbidden direction，让后续迭代不重复踩坑。

---

## 三、四级验证级联：拦截 Silent Failure

NOVA 的另一个核心是**四级验证级联（Verification Cascade）**，按成本从低到高排列：

```
候选架构修改 K 个
        ↓
Level 1：结构语义检查（V_sem）
  • tensor shape 一致性
  • sequence masking 完整性
  • logit fusion 路径正确性
  • feature 依赖关系
        ↓ 失败 → 记入 H 为 forbidden direction，阻断
Level 2：本地可执行性（V_local）
  • 编译通过
  • 单元测试
  • 推理框架兼容性
        ↓ 失败 → 同上
Level 3：离线有效性
  • 实际训练，AUC ΔJ > 0.001
  • 参数量/FLOPs 约束
        ↓ 失败 → 记录 metric feedback 到 g_t
Level 4：在线验证
  • 生产流量 A/B 测试（5% traffic）
  • GMV / pCVR bias 验证
```

这四级设计的关键是**成本对齐**：最便宜的检查先做（结构语义检查几乎零成本），最贵的在线 A/B 只对通过前三关的候选做。结构语义失败的候选不会浪费 GPU 训练时间，本地执行失败的候选不会占 A/B 实验位。

---

## 四、L1-L4 任务分级 + AutoRun/Copilot 模式

NOVA 把任务按复杂度分成四级：

| 级别 | 修改类型 | 示例 |
|------|---------|------|
| L1 | 单模块超参调整 | 调 embedding dimension |
| L2 | ScaleUp | 在现有架构框架内扩容参数 |
| L3 | Literature-to-Production | 把论文里的模块移植到生产 backbone |
| L4 | 跨系统架构重设计 | 需要人类战略决策 |

执行模式不直接对应级别，而是看「技能规格覆盖度」：

- **AutoRun**：修改在 NOVA 的技能规格覆盖范围内 → 全自动运行，语义门检查自动完成
- **Copilot**：修改超出技能规格 → 路由给人类确认高风险决策

这个设计允许同一个 L3 任务既有 AutoRun 的情况（熟悉的迁移模式），也有 Copilot 的情况（首次遇到的新模块类型）。

---

## 五、实验结果

所有 LLM 方法使用同一个基础模型（Claude Sonnet 4.6），性能差异反映的是 Harness 设计，不是模型能力。

### 5.1 主要结果（L2 ScaleUp 和 L3 Literature-to-Production）

**评估指标**：
- **LPR（Local Pass Rate）**：生成候选中通过本地测试的比例
- **SFR（Silent Failure Rate）**：通过本地测试但 AUC 为负的比例（越低越好）
- **EPR（Effective Pass Rate）**：端到端有效率 = LPR × (1 - SFR)

| 方法 | L2 LPR | L2 EPR | L3 LPR | L3 EPR |
|------|--------|--------|--------|--------|
| Human Expert | 高 | — | 较低（调试耗时）| — |
| Optuna-TPE | — | — | N/A | N/A |
| ReActAgent-only | 低 | 低 | 低 | 低 |
| OpenHands | 中 | 低（高 SFR）| 中 | 低 |
| **NOVA** | **高** | **54.5%** | **86.7%** | **60.0%** |

L3 任务（论文→生产移植）最能体现 NOVA 的价值：人类专家能理解架构语义，但把论文设计翻译成生产代码并通过本地调试往往需要反复试错，LPR 不高。NOVA 通过结构化的论文分析、Solution Design 步骤、多候选生成+质量评估，把 LPR 提到 86.7%，EPR 到 60%。

### 5.2 消融实验（L3 任务）

逐项移除 NOVA 组件，看各指标变化：

| 移除组件 | LPR | SFR | EPR |
|---------|-----|-----|-----|
| 完整 NOVA | 86.7% | 31.0% | **60.0%** |
| - 论文分析（仅摘要）| 91.7% | 63.6% | 33.3% |
| - Solution Design | — | 77.8% | 18.2%（最差）|
| - 多候选生成 | 66.7% | — | 25.9% |
| - 质量评估 | — | 69.6% | 21.9% |
| - 梯度反馈 | 87.5% | 57.1% | 37.5% |

**关键发现**：

- **Solution Design 是最重要的单组件**（移除后 EPR 降至 18.2%）：没有显式的设计步骤，系统直接从论文信息跳到实现，不分解架构变更、不检查模块依赖、不对齐新模块与生产 backbone，导致大量 silent failure。
- **梯度反馈的价值**：移除后 LPR 不降（87.5%），但 SFR 大涨（57.1%）、EPR 下降（37.5%）——说明没有诊断反馈，系统倾向于生成更简单易运行但无效的修改，不能把失败转化为搜索知识。

### 5.3 在线 A/B 测试

L3 最优候选（TokenMixer-Large 迁移）在生产 pCVR 模型上以 5% 流量 A/B 测试：

| 指标 | 结果 |
|------|------|
| GMV task1 | **+1.25%** |
| GMV task2 | **+1.70%** |
| GMV task3 | **+2.02%** |
| pCVR bias task1 | **-58.8%** |
| pCVR bias task2 | **-66.7%** |
| pCVR bias task3 | **-37.3%** |

GMV 提升同时 bias 下降（校准变好）——这意味着不只是在优化 proxy metric，而是真实业务价值和模型质量的同步改善。

### 5.4 效率提升

一个 Literature-to-Production 周期（从论文到生产）的**人工参与时间缩短 13x 以上**。总时间不一定更短（离线训练时间固定），但人类专家从「全程手工调试」变成「高风险决策审核」，释放了大量专家资源。

---

## 六、工程落地：如何在自己的推荐系统里实践 NOVA 思路

NOVA 是腾讯内部系统，没有开源代码。但它的设计原则可以在自己的项目里复现：

### 6.1 建立架构修改的形式化表示

```python
@dataclass
class ArchitectureModification:
    """一次架构修改的标准化表示"""
    modification_id: str
    type: str          # "add_module" | "replace_module" | "scale_param" | "change_routing"
    description: str   # 自然语言描述
    code_changes: dict # 文件路径 → 具体修改
    constraints: list  # 硬约束（shape、dtype、latency）
    source: str        # "literature" | "manual" | "generated"
```

### 6.2 实现结构语义检查

```python
class ArchitectureSemanticChecker:
    """推荐模型结构语义验证"""

    def check(self, model_code: str, modification: ArchitectureModification) -> dict:
        results = {}

        # 检查 tensor shape 一致性
        results['shape_ok'] = self._check_tensor_shapes(model_code)

        # 检查 sequence masking 是否完整
        results['masking_ok'] = self._check_masking_integrity(model_code)

        # 检查 feature routing 是否保持
        results['routing_ok'] = self._check_feature_routing(model_code)

        # 检查 logit fusion 路径
        results['fusion_ok'] = self._check_logit_fusion(model_code)

        overall_pass = all(results.values())
        failure_reasons = [k for k, v in results.items() if not v]

        return {
            "pass": overall_pass,
            "failure_reasons": failure_reasons,
            "forbidden_pattern": self._extract_forbidden_pattern(failure_reasons, modification)
        }
```

### 6.3 架构梯度的简化实现

```python
class ArchitectureGradient:
    def __init__(self, llm_client):
        self.llm = llm_client

    def compute(self, prev_modification: dict, verification_diagnostics: dict,
                metric_change: float, trajectory_history: list) -> dict:
        """计算下一步的架构修改方向"""

        forbidden_patterns = [
            h['forbidden_pattern']
            for h in trajectory_history
            if h.get('forbidden_pattern')
        ]

        prompt = f"""你是推荐系统架构专家。

上一次架构修改：{json.dumps(prev_modification, ensure_ascii=False)}
验证诊断：{json.dumps(verification_diagnostics, ensure_ascii=False)}
指标变化：AUC {'+' if metric_change > 0 else ''}{metric_change:.4f}
历史禁止模式：{json.dumps(forbidden_patterns, ensure_ascii=False)}

基于以上信息，分析：
1. 当前架构的弱点在哪里？
2. 下一步应该探索哪些修改方向？
3. 哪些方向应该避免（扩展禁止列表）？

以 JSON 格式输出架构梯度。"""

        response = self.llm.chat.completions.create(
            model="default_model",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
```

### 6.4 任务分级路由

```python
def route_task(task: dict, skill_specifications: dict) -> str:
    """根据技能规格覆盖度决定执行模式"""

    modification_type = task.get('type')
    complexity_level = task.get('level')

    # 高风险或超出技能规格 → Copilot（人工审核）
    if complexity_level == 'L4':
        return 'copilot'
    if modification_type not in skill_specifications:
        return 'copilot'

    spec = skill_specifications[modification_type]
    # 检查是否有历史成功案例
    if spec.get('success_rate', 0) < 0.3:
        return 'copilot'  # 成功率低的修改类型也走人工

    return 'autorun'
```

---

## 七、NOVA 与 HarnessX 的对比

NOVA 和 HarnessX 都是「Agent Harness」类工作，但侧重点不同：

| 维度 | NOVA | HarnessX |
|------|------|---------|
| **领域** | 工业推荐系统架构进化 | 通用 Agent 基准任务 |
| **进化对象** | 模型架构（代码结构）| Agent 脚手架（prompt/工具/记忆/控制流）|
| **核心机制** | 架构梯度 + 验证级联 | 执行轨迹 + 脚手架变体搜索 |
| **核心问题** | 可运行代码 ≠ 有效架构（silent failure）| 通用脚手架 ≠ 最优脚手架 |
| **环境依赖** | 需要生产推荐系统评估管道 | 通用 benchmark |
| **开源状态** | 无（腾讯内部）| 无（小米内部）|

两篇论文共享一个底层洞察：**在 LLM Agent 系统里，包裹模型的那个「框架/架构/脚手架」本身是进化的对象，不应该只靠人工调整**。

---

*论文来源：arXiv:2606.27243，腾讯广告推荐系统团队，2026-07-26 整理。所有数据均来自论文原文。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: NOVA: A Verification-Aware Agent Harness for Architecture Evolution in Industrial Recommender Systems
> **arXiv**: 2606.27243
> **Team**: Shaohua Liu et al. (Tencent Ads)
> **Key metrics**: L3 EPR 60%, cycle time reduced 13x, GMV +1.25%~+2.02%

---

## 1. The Starting Problem

In large-scale advertising recommender systems, model architecture evolution is continuous. RankMixer, TokenMixer-Large, MixFormer — each architecture upgrade requires weeks to months: read the paper, understand architectural intent, translate the idea into production code, pass local tests, pass offline evaluation, run online A/B.

Two core pain points:

**Pain 1: Existing automation solves the wrong problem**

AutoML tunes hyperparameters (learning rate, hidden size, embedding dimension). But effective recommender improvements typically require **cross-module topology changes**: upgrading target attention to joint Seq-Token modeling, redesigning the logit fusion path, replacing standard residual connections with AttentionRes. AutoML's search space doesn't cover structural modifications at this level.

**Pain 2: Generic LLM coding agents are insufficient — runnable ≠ valid**

General-purpose coding agents (SWE-Agent, OpenHands) optimize for software-level correctness (compilation, unit test passing). But in recommender systems, code may run successfully while **silently breaking architectural semantics**: incorrectly removing sequence masking, degenerating self-attention to a simple MLP, altering the logit fusion path. These runnable-but-invalid candidates — what the paper calls **silent failures** — degrade offline and online metrics without being visible at the code level.

---

## 2. Core Mechanism: Architecture Gradient

NOVA's most important concept is the **architecture gradient**.

Standard gradients require differentiable parameters. Recommender model architectures are discrete and constrained — standard gradients aren't available. NOVA uses an SGD-inspired non-differentiable update signal:

```
g_t = Grad(e_{t-1}, V_t, ΔJ_t, H_t)
```

Where:
- `e_{t-1}` = previous architecture modification
- `V_t` = verification diagnostics (what failed and how)
- `ΔJ_t` = offline metric change (how much AUC changed)
- `H_t` = historical trajectory (all modifications, failures, metrics)

The gradient contains three types of information: **Weak Components** (where the current architecture is likely bottlenecked), **Modification Directions** (what to try next), and **Forbidden Directions** (patterns that have already failed and should not be retried).

The key insight: **failure information is not discarded but converted into search constraints**. Every verification failure records the failure pattern as a forbidden direction, preventing later iterations from repeating the same mistakes.

---

## 3. Four-Stage Verification Cascade

```
K candidate architecture modifications
        ↓
Stage 1: Structure-semantic checking (cheap)
  • tensor shape consistency
  • sequence masking integrity
  • logit fusion path correctness
  • feature dependency preservation
        ↓ fail → record as forbidden direction, block
Stage 2: Local executability
  • compilation
  • unit tests
  • inference framework compatibility
        ↓ fail → same
Stage 3: Offline effectiveness
  • actual training, AUC ΔJ > 0.001
  • parameter/FLOPs budget
        ↓ fail → record metric feedback into g_t
Stage 4: Online validation
  • production A/B test (5% traffic)
  • GMV / pCVR bias
```

Cost alignment is the key: cheapest checks first (semantic checks are near-zero cost); online A/B only for candidates that pass all three prior stages. Semantically invalid candidates waste no GPU training time; locally failing candidates don't consume A/B experiment slots.

---

## 4. Experimental Results

All LLM-based methods use the same base model (Claude Sonnet 4.6), so performance differences reflect harness design, not raw model capability.

### Main results (L3 Literature-to-Production)

NOVA achieves **LPR 86.7% and EPR 60.0%** on L3 tasks, substantially above all baselines. The human expert baseline has lower LPR due to the trial-and-error involved in translating paper architectures to production code. ReActAgent-only and OpenHands optimize for runnable code but don't reliably preserve production recommender semantics.

### Ablation study (L3 task, removing one component at a time)

| Removed component | EPR |
|-------------------|-----|
| Full NOVA | **60.0%** |
| - Paper Analysis (shallow) | 33.3% |
| - Solution Design | 18.2% (worst) |
| - Multi-Candidate Generation | 25.9% |
| - Quality Assessment | 21.9% |
| - Gradient Feedback | 37.5% |

**Solution Design is the single most important component**: without an explicit design step, the system jumps from paper information directly to implementation without decomposing the architecture change, checking module dependencies, or aligning the new module with the production backbone.

### Online A/B results

| Metric | Result |
|--------|--------|
| GMV task1 | **+1.25%** |
| GMV task2 | **+1.70%** |
| GMV task3 | **+2.02%** |
| pCVR bias reduction | **37–67%** |

GMV improves while bias decreases simultaneously — real business value and model quality improving together, not a tradeoff.

### Efficiency

One Literature-to-Production cycle reduced by **over 13x in human-attended time**. Human experts shift from "manual debugging" to "high-risk decision review."

---

## 5. NOVA vs HarnessX: Different Flavors of the Same Insight

Both papers share a deeper claim: **in LLM agent systems, the wrapper around the model (architecture/scaffold/harness) is itself an evolutionary object**, not something that should only be manually adjusted.

| | NOVA | HarnessX |
|--|------|---------|
| Domain | Industrial recommender architecture | General agent benchmarks |
| What evolves | Model architecture (code structure) | Agent scaffold (prompt/tools/memory/flow) |
| Core mechanism | Architecture gradient + verification cascade | Execution traces + scaffold variant search |
| Core problem | Runnable ≠ valid (silent failures) | Generic scaffold ≠ optimal scaffold |
| Open source | No (Tencent internal) | No (Xiaomi internal) |

---

*Source: arXiv:2606.27243, Tencent Ads Team. Compiled 2026-07-26. All numbers from the paper.*

© 2026 Author: Mycelium Protocol
