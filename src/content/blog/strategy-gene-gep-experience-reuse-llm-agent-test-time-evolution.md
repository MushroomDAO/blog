---
title: "Strategy Gene：AI 经验可以成为流通资产——前提是用对表示形式（论文解析 + 工程落地指南）"
titleEn: "Strategy Gene: AI Experience as Tradeable Assets — Only If Encoded Correctly (Paper Analysis + Engineering Guide)"
description: "arXiv:2604.15097，清华大学+EvoMap。核心判断：经验表示形式本身是一阶因素——文档式Skill（2500 tokens）让性能-1.1pp，紧凑Gene（230 tokens）让性能+3.0pp。介绍Gene结构、GEP协议三层架构，以及skill2gep/evolver开源实现和工程落地方法。"
descriptionEn: "arXiv:2604.15097, Tsinghua + EvoMap. Core finding: experience representation is a first-order factor — documentation-oriented Skill (2500 tokens) hurts by -1.1pp, compact Gene (230 tokens) helps by +3.0pp. Covers Gene structure, GEP three-layer architecture, open-source skill2gep/evolver, and engineering implementation guide."
pubDate: "2026-07-25"
updatedDate: "2026-07-25"
category: "Research"
tags: ["AI Agent", "经验表示", "Strategy Gene", "GEP", "Test-Time Evolution", "LLM", "自进化", "工程实践", "论文解析"]
heroImage: "../../assets/images/strategy-gene-gep-experience-reuse-llm-agent-test-time-evolution-banner.jpg"
---

> **论文**：arXiv:2604.15097 — "From Procedural Skills to Strategy Genes: Towards Experience-Driven Test-Time Evolution"
> **作者**：Junjie Wang, Yiming Ren, Haoyang Zhang（清华大学 + EvoMap Infinite Evolution Lab）
> **开源**：[EvoMap/skill2gep](https://github.com/EvoMap/skill2gep)（MIT）· [EvoMap/evolver](https://github.com/EvoMap/evolver)（GPL-3.0，8876 ⭐）

---

## 一、核心判断：经验可以是资产，但表示形式决定一切

用户说得对——这篇论文最深层的判断是：

> **AI 的经验可以成为一种能够流通的资产。**

但流通的前提是，这份经验用正确的形式被编码。

一份写给人看的经验文档，和一份直接控制模型推理行为的经验对象，是两回事。这篇论文用 4,590 次对照实验证明了这个差异有多大：

| 条件 | 平均通过率 | vs 无指导 |
|------|-----------|---------|
| **Skill**（文档式，~2,500 tokens）| 49.9% | **-1.1pp（有害）** |
| 无指导 | 51.0% | 0 |
| **Gene**（紧凑控制式，~230 tokens）| **54.0%** | **+3.0pp** |

更多文档，反而更差。

这个结论颠覆了大多数 Agent 记忆系统的基本假设。

---

## 二、问题在哪里：Skill 为什么会失败

现有的大多数 Agent 经验系统（Voyager、ExpeL、Reflexion 等）把"经验"当作一个**内容对象**来存储：把过去的解决方案打包成可读的文档，检索出来放进 context 里，期望模型读懂后表现更好。

论文把这类表示称为 **Procedural Skill**，结构大致是：

```
{
  overview: "任务概述...",
  workflow: "步骤1...步骤2...步骤3...",
  pitfalls: "常见陷阱...",
  error_handling: "错误处理...",
  api_notes: "API参考...",
  examples: "示例代码...",
  scripts: "辅助脚本..."
}
```

大约 2,500 tokens。

实验把 Skill 拆开分析，结果很清楚：

- **Skill-Workflow**：有用（唯一正增益的部分）
- **Skill-Overview**：**有害**（显著拉低性能）
- **Skill-Pitfalls / ErrorHandling / QuickRef**：基本无效

有效信号稀疏，大量 token 是噪音。更致命的是，Overview 这类描述性内容会主动干扰模型的注意力。

> 关键洞察：文档优化的是人类的阅读体验，不是模型的推理控制。

---

## 三、Gene：控制导向的经验表示

**Strategy Gene** 是论文提出的替代表示。它的目标不是完整记录，而是在有限 token 预算下，最大化对模型推理行为的控制相关性。

### Gene 的数学定义

```
g = (m, u, π, α, c, v)
```

- **m**：任务匹配关键词（domain keywords）
- **u**：紧凑摘要（compact summary）
- **π**：战略步骤（strategic steps，3–5 条）
- **α**：失败规避提示（AVOID cues，高风险决策点）
- **c**：可选执行约束（constraints）
- **v**：可选验证钩子（validation hooks）

### 标准格式（~230 tokens）

```xml
<strategy-gene>
Domain keywords: uv-vis, peak detection, FWHM, unit conversion

Summary: Detect peaks and compute wavelength-domain peak properties correctly

Strategy:
1. Detect peaks with prominence-based criteria
2. Convert min_distance into sample-index units before peak detection
3. AVOID: Report FWHM only after converting peak_widths outputs
   back to wavelength units

</strategy-gene>
```

注意这里的 `AVOID` 字段：**把失败历史蒸馏成警告，而不是附加原始错误记录**。这是实验中最有效的失败信息编码方式（+4.6pp，优于直接附加失败历史 +3.4pp）。

### Gene 不是缩短的 Skill

实验验证了一个关键问题：Gene 的优势是因为更短，还是因为更结构化？

| 条件 | 平均分 | △ |
|------|-------|---|
| keywords only | 53.5% | +2.5 |
| keywords + summary | 51.0% | 0.0 |
| keywords + summary + strategy | **54.0%** | **+3.0** |

只加 keywords 比加 keywords+summary 更好。效果不是随 token 单调增长的，**关键是 strategy 层的出现**——把经验组织成显式的控制接口。

---

## 四、Gene Evolution Protocol（GEP）：让经验可以迭代进化

单次控制是静态的。GEP 是让 Gene 能够在运行中持续迭代的协议层。

### 三层对象架构

```
┌─────────────────────────────────────────┐
│  Event（不可变进化日志）                  │
│  每次验证成功后的审计记录                  │
├─────────────────────────────────────────┤
│  Capsule（验证过的执行路径）               │
│  多个 Gene 的组合，代表验证成功的完整方案   │
├─────────────────────────────────────────┤
│  Gene（原子能力单元）                     │
│  最小可复用单元，直接作为 test-time 控制信号│
└─────────────────────────────────────────┘
```

### 进化循环

```
新任务输入
    ↓
检索匹配 Gene（按 keywords 匹配）
    ↓
注入 Gene 作为控制信号 → 模型推理
    ↓
执行验证（sandbox checkpoint）
    ↓
失败 → 提取失败信息 → 蒸馏 AVOID cue → 更新 Gene
成功 → 记录为 Event → 可能晋升为 Capsule
    ↓
（下一轮 trial）
```

关键属性：
- **可编辑**：Gene 是结构化对象，可以在字段级别修改，而不是整体替换
- **有边界**：每个 Gene 有明确的适用条件（keywords），避免无差别复用
- **有审计**：Event 记录不可变，提供进化轨迹的完整历史

### 进化效果（CritPt 基准）

在物理学前沿研究推理基准上：

| 模型 | 基线 | Gene 进化后 | 提升 |
|------|------|------------|------|
| Gemini 3 Pro Preview | 9.1% | **18.57%** | +2× |
| Gemini 3.1 Pro Preview | 17.7% | **27.14%** | +1.5× |

不修改模型参数，只通过 Gene 的迭代积累，通过率翻倍。

---

## 五、三个反直觉的实验发现

### 5.1 加回文档会削弱 Gene

| 条件 | 平均分 |
|------|-------|
| Gene + API notes | 51.5% |
| Gene + examples | 52.0% |
| **Gene alone** | **54.0%** |

加上 API 文档或示例，效果反而下降。**Gene 的优势是表示性的，不是加法性的**。

### 5.2 complementary genes 比 conflicting genes 更有害

| 条件 | 平均分 |
|------|-------|
| 2个互补 Gene | **44.9%（最差）** |
| 无指导 | 51.0% |
| 2个冲突 Gene | 53.2% |
| 单个 Gene | **54.0%** |

两个互补的 Gene 同时注入，比两个冲突的 Gene 更糟糕。原因是多个部分相关的控制对象会互相竞争注意力，导致控制焦点模糊——即便它们内容上并不矛盾。

> 经验的可复用性有边界：精准的单个 Gene > 多个相关 Gene 的堆叠。

### 5.3 结构扰动不致命，语义错误才致命

| 扰动类型 | 平均分 |
|---------|-------|
| 错误算法（内容错误）| 48.8% |
| 错误领域（内容错误）| 49.4% |
| 无 Gene | 51.0% |
| 优先级倒置（结构扰动）| 52.8% |
| 过度约束（结构扰动）| 55.9% |
| 正常 Gene | 54.0% |

Gene 对结构形式的变化高度鲁棒，但对语义内容的错误极度敏感。这说明模型读的不是模板，而是内容信号。

---

## 六、开源实现与工程落地

### 6.1 三个核心仓库

| 仓库 | 用途 | Stars | License |
|------|------|-------|---------|
| [EvoMap/skill2gep](https://github.com/EvoMap/skill2gep) | 将 Skill 文档转换为 GEP-compliant Gene | 12 | MIT |
| [EvoMap/evolver](https://github.com/EvoMap/evolver) | GEP 驱动的自进化引擎 | 8,876 | GPL-3.0 |
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | Agent 运行时宿主（evolver 的参考宿主）| 384K | - |

### 6.2 快速开始：skill2gep

如果你已经有一个文档式的 Skill 或技能库，skill2gep 可以自动将其转换为 Gene 格式：

```bash
git clone https://github.com/EvoMap/skill2gep
cd skill2gep
npm install

# 将一个 Skill 文档转换为 Gene
node cli.js convert --input skill.md --output gene.xml

# 批量转换技能库
node cli.js batch --dir ./skills/ --output ./genes/
```

### 6.3 evolver 集成

evolver 是完整的 GEP 运行时，内置 Gene 检索、注入、验证、更新循环：

```javascript
import { Evolver } from '@evomap/evolver';

const evolver = new Evolver({
  geneStore: './genes/',          // Gene 存储目录
  capsuleStore: './capsules/',    // Capsule 存储
  eventLog: './events.jsonl',     // 不可变事件日志
  model: 'gemini-3.1-pro',       // 使用的 LLM
  temperature: 0.05,              // 低温推理
});

// 处理新任务
const result = await evolver.solve({
  task: '分析UV-Vis光谱数据，检测峰值并计算FWHM',
  sandbox: async (code) => {
    // 执行生成的代码并返回 checkpoint 结果
    return await runInSandbox(code);
  },
});

console.log(result.passRate);    // 本次通过率
console.log(result.geneUpdated); // 是否触发了 Gene 更新
```

### 6.4 手动实现 Gene 的最简方案

如果不想引入完整的 evolver，可以按以下模式手动实现核心逻辑：

**Step 1：定义你的 Gene 模板**

```python
GENE_TEMPLATE = """<strategy-gene>
Domain keywords: {keywords}

Summary: {summary}

Strategy:
{strategy_steps}
{avoid_cues}
</strategy-gene>"""

def format_gene(keywords: list[str], summary: str,
                steps: list[str], avoids: list[str]) -> str:
    avoid_text = "\n".join(f"AVOID: {a}" for a in avoids)
    step_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    return GENE_TEMPLATE.format(
        keywords=", ".join(keywords),
        summary=summary,
        strategy_steps=step_text,
        avoid_cues=avoid_text,
    )
```

**Step 2：从失败历史蒸馏 AVOID cues**

```python
def distill_failure_to_avoid(failure_trace: str, llm) -> str:
    """将原始失败信息蒸馏为单行 AVOID 警告"""
    prompt = f"""以下是一次任务失败的记录：
{failure_trace}

请提取最关键的一个操作错误，用一句话写成 AVOID 警告。
格式：AVOID: [具体的错误操作/错误假设]
只输出一行，不超过20个词。"""
    return llm.generate(prompt).strip()
```

**Step 3：Gene 检索与注入**

```python
class GeneStore:
    def __init__(self, genes: list[dict]):
        self.genes = genes

    def retrieve(self, task_description: str, top_k: int = 1) -> list[str]:
        """按关键词匹配，返回最相关的 Gene"""
        scores = []
        task_words = set(task_description.lower().split())
        for gene in self.genes:
            keywords = set(gene['keywords'])
            overlap = len(keywords & task_words)
            scores.append((overlap, gene['content']))
        scores.sort(reverse=True)
        return [content for _, content in scores[:top_k]]

def build_prompt(task: str, gene_store: GeneStore) -> str:
    genes = gene_store.retrieve(task)
    gene_text = "\n\n".join(genes) if genes else ""
    return f"{gene_text}\n\n{task}" if gene_text else task
```

**Step 4：进化循环**

```python
def evolve_gene(gene: dict, failure_trace: str, llm) -> dict:
    """根据失败历史更新 Gene"""
    new_avoid = distill_failure_to_avoid(failure_trace, llm)
    updated = gene.copy()
    # 追加 AVOID cue（不超过 3 条，避免过度约束）
    avoids = updated.get('avoids', [])
    if len(avoids) < 3:
        avoids.append(new_avoid)
        updated['avoids'] = avoids
    else:
        # 超过 3 条时，替换最旧的一条
        avoids.pop(0)
        avoids.append(new_avoid)
        updated['avoids'] = avoids
    return updated
```

### 6.5 工程实践建议

基于论文的实验结论，落地时要注意以下几点：

**1. 每个 Gene 只管一件事**

单一聚焦的 Gene 比多个 Gene 组合效果更好。不要试图把所有经验塞进一个 Gene，也不要同时注入多个 Gene。

**2. AVOID 是核心字段，不是可选项**

失败警告是 Gene 效果的关键来源。每次任务失败后，花时间蒸馏一条精准的 AVOID cue，而不是直接附加原始错误日志。

**3. 控制 Gene 的总 token 数在 200–300 之间**

超过 500 token 的 Gene 性能会接近 Skill 的失败模式。如果内容太多，拆成两个独立场景的 Gene，而不是合并。

**4. keywords 要精确，不要泛化**

keywords 是检索的锚点。用 `uv-vis, peak detection, scipy.signal` 比用 `signal processing, data analysis` 效果好得多——越具体，检索越精准，注入的控制信号越有效。

**5. Gene 应该可编辑，不应该是追加式的**

在字段级别修改 Gene（替换错误步骤，更新 AVOID 列表），不要在 Gene 外部叠加更多文本。实验表明，可编辑结构的重要性超过内容本身。

---

## 七、与现有方案的关系

| 方案 | 经验形式 | 问题 |
|------|---------|------|
| Reflexion | 自由文本反思 | 无结构，检索困难，信号稀疏 |
| Voyager（Skill） | 文档式 Skill | 文档完整性≠控制效率，本论文的批判对象 |
| ExpeL | 经验库 + 检索 | 关注如何存储和检索，未解决表示形式问题 |
| **Strategy Gene + GEP** | 紧凑控制对象 | 本论文的提案：表示即资产 |

用户说的"AI经验成为流通资产"，在这个框架里有具体含义：

一个 Gene 是**可交换**的（30 token 的 keywords 标记它的适用范围），**可进化**的（GEP 协议定义了修改接口），**可审计**的（Event 日志不可变）。这让 Gene 具备了资产的基本属性：可以在 Agent 之间传递，可以在任务之间复用，可以通过迭代增值。

---

## 八、局限性与适用边界

- **实验范围**：仅在科学代码场景（Python程序生成）验证，其他领域（对话、规划等）的泛化性未知
- **单 Gene 上限**：组合多个 Gene 在本实验中通常有害，但在低难度或通用场景中可能不同
- **模型依赖**：实验用 Gemini 3.1，其他模型的最优 Gene 结构可能有差异
- **Beta 阶段**：这是 beta 技术报告，部分结论仍需更广泛验证

---

*论文来源：arXiv:2604.15097，2026-07-25 整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: arXiv:2604.15097 — "From Procedural Skills to Strategy Genes: Towards Experience-Driven Test-Time Evolution"
> **Authors**: Junjie Wang, Yiming Ren, Haoyang Zhang (Tsinghua University + EvoMap Infinite Evolution Lab)
> **Open Source**: [EvoMap/skill2gep](https://github.com/EvoMap/skill2gep) (MIT) · [EvoMap/evolver](https://github.com/EvoMap/evolver) (GPL-3.0, 8,876 ⭐)

---

## 1. The Core Claim: Experience Can Become an Asset, but Representation Is Everything

The user's framing is exactly right — the paper's deepest claim is:

> **AI experience can become a tradeable asset.**

But for experience to be tradeable, it has to be encoded in the right form.

A documentation artifact written for humans and a control object that directly influences model inference behavior are fundamentally different things. This paper runs 4,590 controlled experiments to show how large that difference actually is:

| Condition | Avg. Pass Rate | vs. No Guidance |
|-----------|---------------|----------------|
| **Skill** (documentation-oriented, ~2,500 tokens) | 49.9% | **-1.1pp (harmful)** |
| No guidance | 51.0% | 0 |
| **Gene** (compact, control-oriented, ~230 tokens) | **54.0%** | **+3.0pp** |

More documentation, worse performance.

This overturns the central assumption of most agent memory systems.

---

## 2. What's Wrong with Skill

Most existing agent experience systems (Voyager, ExpeL, Reflexion, etc.) treat experience as a **content object**: package past solutions as readable documentation, retrieve it into context, and expect the model to perform better after reading it.

The paper calls these **Procedural Skills**. The structure looks roughly like:

```
{
  overview: "task description...",
  workflow: "step 1... step 2... step 3...",
  pitfalls: "common failure modes...",
  error_handling: "how to handle errors...",
  api_notes: "API reference...",
  examples: "example code...",
  scripts: "helper scripts..."
}
```

About 2,500 tokens.

Decomposing Skill into its sections:

- **Skill-Workflow**: helpful (the only positive component)
- **Skill-Overview**: **harmful** (significantly degrades performance)
- **Skill-Pitfalls / ErrorHandling / QuickRef**: largely neutral or negative

The useful signal is sparse; most tokens are noise. Worse, descriptive sections like Overview actively compete for model attention.

> The key insight: documentation is optimized for human readability, not model inference control.

---

## 3. Gene: A Control-Oriented Experience Representation

**Strategy Gene** is the paper's proposed alternative. Its goal isn't complete documentation — it's maximizing control-relevant signal per token.

### Gene's Formal Definition

```
g = (m, u, π, α, c, v)
```

- **m**: task-matching keywords
- **u**: compact summary
- **π**: strategic steps (3–5 items)
- **α**: failure-aware AVOID cues (high-risk decision points)
- **c**: optional execution constraints
- **v**: optional validation hooks

### Standard Format (~230 tokens)

```xml
<strategy-gene>
Domain keywords: uv-vis, peak detection, FWHM, unit conversion

Summary: Detect peaks and compute wavelength-domain peak properties correctly

Strategy:
1. Detect peaks with prominence-based criteria
2. Convert min_distance into sample-index units before peak detection
3. AVOID: Report FWHM only after converting peak_widths outputs
   back to wavelength units

</strategy-gene>
```

The `AVOID` field encodes failure history as a distilled warning — the most effective form of failure information encoding (+4.6pp vs. naively appended failure history +3.4pp).

### Gene is Not Shorter Skill

The experiment directly tests whether Gene's advantage is just brevity:

| Condition | Avg. | Δ |
|-----------|------|---|
| keywords only | 53.5% | +2.5 |
| keywords + summary | 51.0% | 0.0 |
| keywords + summary + strategy | **54.0%** | **+3.0** |

Keywords-only outperforms keywords+summary. The effect doesn't grow monotonically with token count. **The gain only appears when the strategy layer organizes experience into an explicit control interface.**

---

## 4. Gene Evolution Protocol (GEP): Making Experience Iteratively Evolvable

One-shot control is static. GEP is the protocol layer that allows Gene to accumulate and evolve during deployment.

### Three-Layer Object Architecture

```
┌─────────────────────────────────────────────┐
│  Event (immutable evolution log)             │
│  Audit record created after each validation │
├─────────────────────────────────────────────┤
│  Capsule (validated execution path)          │
│  Composition of Genes representing a        │
│  validated complete solution                │
├─────────────────────────────────────────────┤
│  Gene (atomic capability unit)               │
│  Minimum reusable unit for direct            │
│  test-time control                           │
└─────────────────────────────────────────────┘
```

### The Evolution Loop

```
New task input
    ↓
Retrieve matching Gene (by keywords)
    ↓
Inject Gene as control signal → model inference
    ↓
Execute validation (sandbox checkpoints)
    ↓
Failure → extract failure info → distill AVOID cue → update Gene
Success → record as Event → potentially solidify as Capsule
    ↓
(next trial)
```

Key properties:
- **Editable**: Gene is a structured object; fields can be updated without wholesale replacement
- **Bounded**: each Gene has explicit applicability conditions (keywords); no unbounded reuse
- **Auditable**: Events are immutable records; full evolution history is preserved

### Evolution Results (CritPt Benchmark)

On a frontier physics research reasoning benchmark:

| Model | Baseline | After Gene Evolution | Improvement |
|-------|---------|---------------------|-------------|
| Gemini 3 Pro Preview | 9.1% | **18.57%** | +2× |
| Gemini 3.1 Pro Preview | 17.7% | **27.14%** | +1.5× |

No model parameter updates. Pure Gene accumulation roughly doubles the pass rate.

---

## 5. Three Counterintuitive Experimental Findings

### 5.1 Adding Documentation Back to Gene Weakens It

| Condition | Avg. |
|-----------|------|
| Gene + API notes | 51.5% |
| Gene + examples | 52.0% |
| **Gene alone** | **54.0%** |

Adding API documentation or examples to Gene reduces performance. **Gene's advantage is representational, not additive.**

### 5.2 Complementary Genes Are More Harmful Than Conflicting Ones

| Condition | Avg. |
|-----------|------|
| 2 complementary Genes | **44.9% (worst)** |
| No guidance | 51.0% |
| 2 conflicting Genes | 53.2% |
| Single Gene | **54.0%** |

Two complementary Genes injected together produce the worst result in the table. Two conflicting Genes stay close to single-Gene performance. The failure mode isn't contradiction — it's attention dispersion. Multiple partially-relevant control objects blur the control signal even when their content is nominally compatible.

> Reusability has a scope boundary: a single targeted Gene outperforms an accumulation of related Genes.

### 5.3 Structural Perturbations Are Harmless; Semantic Errors Are Lethal

| Perturbation Type | Avg. |
|-------------------|------|
| Wrong algorithm (semantic) | 48.8% |
| Wrong domain (semantic) | 49.4% |
| No Gene | 51.0% |
| Inverted priority (structural) | 52.8% |
| Over-constrained (structural) | 55.9% |
| Clean Gene | 54.0% |

Gene is highly robust to structural variations but extremely sensitive to semantic content errors. The model isn't reading a template — it's reading content signals.

---

## 6. Open Source Implementations

### 6.1 Three Core Repositories

| Repo | Purpose | Stars | License |
|------|---------|-------|---------|
| [EvoMap/skill2gep](https://github.com/EvoMap/skill2gep) | Convert Skill docs to GEP-compliant Genes | 12 | MIT |
| [EvoMap/evolver](https://github.com/EvoMap/evolver) | GEP-powered self-evolving engine | 8,876 | GPL-3.0 |
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | Agent runtime host (evolver's reference host) | 384K | - |

### 6.2 Quick Start: skill2gep

Convert existing Skill documentation into Gene format:

```bash
git clone https://github.com/EvoMap/skill2gep
cd skill2gep
npm install

# Convert a single Skill document to Gene
node cli.js convert --input skill.md --output gene.xml

# Batch convert a skills directory
node cli.js batch --dir ./skills/ --output ./genes/
```

### 6.3 evolver Integration

evolver is a full GEP runtime with Gene retrieval, injection, validation, and update loop:

```javascript
import { Evolver } from '@evomap/evolver';

const evolver = new Evolver({
  geneStore: './genes/',
  capsuleStore: './capsules/',
  eventLog: './events.jsonl',
  model: 'gemini-3.1-pro',
  temperature: 0.05,
});

const result = await evolver.solve({
  task: 'Analyze UV-Vis spectral data, detect peaks, compute FWHM',
  sandbox: async (code) => {
    return await runInSandbox(code);  // returns checkpoint results
  },
});

console.log(result.passRate);    // this run's pass rate
console.log(result.geneUpdated); // whether a Gene was updated
```

### 6.4 Minimal Manual Implementation

Core pattern without the full evolver dependency:

```python
GENE_TEMPLATE = """<strategy-gene>
Domain keywords: {keywords}
Summary: {summary}
Strategy:
{strategy_steps}
{avoid_cues}
</strategy-gene>"""

def format_gene(keywords, summary, steps, avoids):
    avoid_text = "\n".join(f"AVOID: {a}" for a in avoids)
    step_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    return GENE_TEMPLATE.format(
        keywords=", ".join(keywords), summary=summary,
        strategy_steps=step_text, avoid_cues=avoid_text,
    )

def distill_failure_to_avoid(failure_trace: str, llm) -> str:
    """Distill raw failure into a single-line AVOID warning"""
    prompt = f"""Failure record:
{failure_trace}

Extract the single most critical operational error. 
Write one AVOID warning, max 15 words.
Format: AVOID: [specific wrong operation or wrong assumption]"""
    return llm.generate(prompt).strip()

def evolve_gene(gene: dict, failure_trace: str, llm) -> dict:
    """Update Gene based on failure history"""
    new_avoid = distill_failure_to_avoid(failure_trace, llm)
    updated = gene.copy()
    avoids = updated.get('avoids', [])
    # Keep at most 3 AVOID cues to prevent over-constraining
    if len(avoids) >= 3:
        avoids.pop(0)
    avoids.append(new_avoid)
    updated['avoids'] = avoids
    return updated
```

---

## 7. Engineering Best Practices

Based directly on the paper's experimental conclusions:

**1. One Gene, one concern.** A targeted single Gene outperforms multiple Genes combined. Don't pack all experience into one Gene; don't inject multiple Genes simultaneously.

**2. AVOID is the core field, not optional.** Failure warnings are the key source of Gene's effectiveness. After each failure, distill one precise AVOID cue rather than appending raw error logs.

**3. Keep total Gene tokens between 200–300.** Genes exceeding 500 tokens start to approach Skill's failure pattern. If content grows too large, split into two separate-scenario Genes rather than merging.

**4. Make keywords specific, not general.** Use `uv-vis, peak detection, scipy.signal` not `signal processing, data analysis`. Specificity improves retrieval precision and strengthens the injected control signal.

**5. Genes should be edited, not appended.** Modify Gene at the field level (replace wrong steps, update AVOID list). Don't stack additional text outside the Gene. Editable structure matters beyond content alone.

---

## 8. Why This Matters for the Agent Memory Ecosystem

| Approach | Experience form | Core problem |
|----------|----------------|-------------|
| Reflexion | Free-form text reflection | No structure, hard to retrieve, sparse signal |
| Voyager (Skill) | Documentation-style Skill | Documentation completeness ≠ control efficiency — this paper's critique |
| ExpeL | Experience library + retrieval | Focuses on storage/retrieval, doesn't address representation form |
| **Strategy Gene + GEP** | Compact control object | The paper's proposal: representation as asset |

A Gene is **transferable** (keywords label its applicability scope), **evolvable** (GEP defines a modification interface), and **auditable** (Event log is immutable). These properties make Gene an asset in the technical sense: it can be passed between agents, reused across tasks, and incrementally appreciated through iteration.

---

*Source: arXiv:2604.15097. Compiled 2026-07-25.*

© 2026 Author: Mycelium Protocol
