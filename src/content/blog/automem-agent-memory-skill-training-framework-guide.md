---
title: "AutoMem：让 Agent 自动学会管理记忆，32B 追平 Claude Opus 4.5"
titleEn: "AutoMem: Teaching Agents to Learn Memory as a Skill — 2x-4x Gains, 32B Reaches Frontier"
description: "Stanford 团队（arXiv:2607.01224）提出 AutoMem 框架：把元记忆（metamemory）引入 LLM Agent，用两个循环自动优化记忆能力——外循环用强 LLM 审查轨迹修改 scaffold，内循环把 agent 自己的好记忆决策转成训练信号。只优化记忆不动任务动作，Qwen2.5-32B 在 Crafter/MiniHack/NetHack 上性能提升 2x-4x，追平 Claude Opus 4.5 和 Gemini 3.1 Pro Thinking。"
descriptionEn: "AutoMem (arXiv:2607.01224, Stanford) automates memory skill learning for LLM agents via two loops: an outer loop where a meta-LLM reviews complete episode trajectories and revises the agent's memory scaffold; an inner loop that distills the agent's own good memory decisions into training signal for a dedicated memory specialist. Result: 2x-4x gains on Crafter/MiniHack/NetHack with Qwen2.5-32B, reaching Claude Opus 4.5 and Gemini 3.1 Pro Thinking without touching task-action weights."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Research"
tags: ["AutoMem", "Agent记忆", "元记忆", "长任务", "Stanford", "LLM Agent", "开源训练"]
heroImage: "../../assets/images/automem-agent-memory-skill-training-framework-guide-banner.jpg"
---

> **论文**: [arXiv:2607.01224](https://arxiv.org/abs/2607.01224) · **作者**: Shengguang Wu et al.（Stanford University）· **项目主页**: [autolearnmem.github.io](https://autolearnmem.github.io)

---

## 你的 Agent 有记忆，但它不知道怎么用

绝大多数工程师在构建 Agent 时，都会遭遇同一堵墙：**任务越长，Agent 越蠢**。

不是模型不够聪明——你可能已经在用 GPT-4o 或者 Sonnet。问题出在记忆管理上。Agent 要么把所有历史堆进 context 直到溢出，要么依赖固定规则的 RAG 检索却找不到真正需要的东西，要么用 summary buffer 把关键细节抹平成一段无法追溯的模糊摘要。

Stanford 团队在 2026 年 7 月发表的 AutoMem（arXiv:2607.01224）给出了一个根本不同的答案：**与其手工设计记忆规则，不如让 Agent 自己学会记忆这项技能。**

---

## 核心洞察：元记忆（Metamemory）是可以学的

认知科学里有个概念叫"元记忆"——不只是有记忆，而是**知道该记什么、什么时候检索、以什么粒度组织信息**。高水平棋手不是记住了所有棋局，而是知道哪类局面值得记、如何归类、何时调用。这正是当前 LLM Agent 最缺失的能力。

AutoMem 的工程直觉是：**把文件系统操作（read / write / search / append / create）提升为和任务动作同等级别的第一类动作（first-class actions）。** 模型不再把"保存笔记"当作副作用，而是把记忆管理当成任务执行的一部分来规划和学习。

---

## 两个循环：AutoMem 的完整架构

### 外循环：结构优化（Scaffold Optimization）

外循环负责优化 Agent 的"认知框架"——prompt 模板、文件 schema、可用的记忆动作词表。

**流程如下：**

```
1. 用当前 scaffold 运行 N 个 episode
2. 把完整轨迹（包括所有记忆操作和结果）喂给 meta-LLM
3. meta-LLM 执行轨迹分析：
   - 找出记忆失败模式（忘记写、写了但格式乱、检索时找不到、存的是无用信息）
   - 识别成功的记忆决策（写入后被有效检索并改善了下游动作）
4. meta-LLM 输出 scaffold 修改建议：
   - 修改 system prompt 中对记忆动作的描述
   - 调整文件组织 schema（例如：按类别分文件 vs. 单文件追加）
   - 增删记忆动作类型（例如：引入"标记重要程度"字段）
5. 应用新 scaffold，进入下一轮迭代
```

**为什么需要 meta-LLM 而不是人工？** 一个完整 episode 可能有数千步。NetHack 这种环境甚至达到 10^4 到 10^5 步。人工审查一整条轨迹并找出记忆模式，从实际工程角度几乎不可行。meta-LLM 可以通过结构化轨迹摘要，在合理 context 范围内完成这个分析。

---

### 内循环：熟练度训练（Proficiency Training）

外循环解决"该怎么记"的结构问题，内循环解决"执行层面是否熟练"的问题。

**流程如下：**

```
1. 从大量 episode 轨迹中提取记忆操作序列
2. 对每个记忆动作，评估其质量信号：
   - 该记忆是否被后续步骤成功检索到？
   - 检索后是否改善了任务动作？（通过比较有/无该记忆的下游 reward）
3. meta-LLM 筛选高质量记忆决策 → 构成监督训练集
4. 用这个数据集微调"记忆专家模型"（memory specialist）
   ⚠️ 重要：只微调记忆模型，任务动作模型权重冻结
5. 用新的记忆专家重新运行 episode，收集更多数据
```

**关键设计选择：分离记忆模型和任务模型。** 这允许记忆专家专注于学习记忆策略，而不用同时应付任务规划——和软件工程"单一职责原则"是同一个道理。

---

## 实验结果：数字说话

- **基础模型**：Qwen2.5-32B-Instruct
- **测试环境**：Crafter（开放世界生存，约 10^3 步）、MiniHack（导航/战斗）、NetHack（极高复杂度，人类玩家需要数年掌握，约 10^4-10^5 步）

| 对比维度 | 结果 |
|---|---|
| AutoMem 32B vs. 基础 32B | 性能提升 **2x-4x** |
| AutoMem 32B vs. Qwen2.5-72B | 32B **大幅超越** 72B |
| AutoMem 32B vs. Claude Opus 4.5 | 达到相近水平 |
| AutoMem 32B vs. Gemini 3.1 Pro Thinking | 达到相近水平 |

最重要的一条：**只优化了记忆，任务动作权重完全没变**，就实现了这样的跨越。这意味着在很多长任务场景里，记忆能力的瓶颈比模型本身的推理能力更关键。

---

## 对比传统方法

| 方法 | 核心机制 | 局限 |
|---|---|---|
| **无限 context** | 把所有历史全塞进去 | context 有限，长任务必然溢出；成本随步数线性增长 |
| **固定 RAG** | 手工设计检索规则 | 检索策略固定，不能适应任务特征 |
| **Summary Buffer** | 定期压缩历史成摘要 | 压缩不可逆，关键细节丢失 |
| **AutoMem** | Agent 自主学习何时记、记什么、如何检索 | 需要运行大量 episode 收集训练数据；冷启动成本高 |

---

## 在自己的项目里复现这个思路

### 第一步：给 Agent 增加显式的记忆动作层

```python
memory_actions = [
    "memory_write(key, value, importance=1-5)",
    "memory_read(key)",
    "memory_search(query)",
    "memory_append(key, value)",
    "memory_list(category)",
]
```

让 Agent 在每步决策时，可以选择"先查一下记忆"或"把这个结果存下来"，和任务动作并列。

### 第二步：记录完整轨迹，标注记忆质量

```python
trace = {
    "step": 42,
    "action": "memory_write('boss_weakness', 'fire_damage')",
    "later_referenced_at": [67, 89],
    "downstream_reward_delta": +0.3
}
```

### 第三步：用强 LLM 做轨迹分析（外循环）

定期（比如每 50 个 episode）把成功和失败的轨迹喂给 GPT-4o 或 Claude Opus：

```
分析这些 Agent 轨迹，找出记忆失败模式：
1. 哪些信息该记但没记？
2. 哪些信息记了但格式导致检索失败？
3. 当前的记忆 prompt 有什么系统性缺陷？
给出具体的 prompt 修改建议。
```

### 第四步：蒸馏高质量记忆决策（内循环）

筛选 `downstream_reward_delta > threshold` 的记忆决策，构建微调数据集，用 LoRA 或 full fine-tune 优化专门的"记忆路由模型"。

### 适合场景

- **多轮对话 Agent**：需要跨会话记住用户偏好和项目状态
- **游戏/仿真 Agent**：状态空间大、需要积累领域知识
- **科研 Agent**：文献调研、实验记录、知识积累型任务
- **自动化工作流**：数百步的 RPA 任务

**不适合场景**：单轮、短 context、任务完全无状态的场景。

---

## 写在最后

AutoMem 最让人印象深刻的，不是它在游戏里打出高分，而是它把一个工程直觉系统化了：**记忆管理不是任务执行的附属品，而是一项独立的、可以被优化的认知技能。**

对工程师来说，这意味着下次你在调试"为什么 Agent 老是忘事"的时候，不应该只是堆更多 context 或者调 RAG 参数——你应该问：它到底有没有学过如何记忆？

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: AutoMem (arXiv:2607.01224, Stanford, July 2026) trains LLM agents to manage memory as a learnable cognitive skill. Two loops: an outer loop where a meta-LLM reviews complete episode trajectories and revises the agent's memory scaffold; an inner loop that distills the agent's own good memory decisions into fine-tuning signal for a dedicated memory specialist (task-action weights stay frozen). Result: 2x-4x gains on Crafter/MiniHack/NetHack with Qwen2.5-32B, substantially outperforming Qwen2.5-72B, and reaching Claude Opus 4.5 and Gemini 3.1 Pro Thinking level — without touching task-action weights.

---

## The Core Idea

AutoMem elevates file system operations — read, write, search, append, create — to first-class actions on par with task actions. This mirrors the cognitive science concept of *metamemory*: not just having memory, but knowing what to store, when to retrieve, and how to organize knowledge. The agent now plans memory decisions alongside task decisions, and both can be optimized from experience.

## Two Loops

**Outer Loop (Scaffold Optimization):** A meta-LLM receives complete episode trajectories (up to 10^5 steps) and identifies systematic memory failure patterns. It then proposes concrete revisions to the agent's prompt scaffold, file schema, and memory action vocabulary. This is architecture review at scale: the kind of holistic trajectory analysis that humans cannot feasibly perform on thousand-step rollouts.

**Inner Loop (Proficiency Training):** Good memory decisions are identified by tracking whether a stored entry was later retrieved and whether that retrieval improved downstream task actions. High-quality decisions are filtered by meta-LLM and used as supervised training signal to fine-tune a dedicated memory specialist model. Only the memory model is updated — task-action weights are frozen.

## Results

2x–4x performance gains over the base Qwen2.5-32B-Instruct model across Crafter, MiniHack, and NetHack. The AutoMem 32B substantially outperforms Qwen2.5-72B across all three benchmarks, and reaches performance parity with Claude Opus 4.5 and Gemini 3.1 Pro Thinking. No task-action weights were modified to achieve this.

## Engineering Takeaway

If your agent underperforms on long-horizon tasks, the bottleneck may not be reasoning capacity — it may be memory skill. Give it explicit memory actions, log which decisions improved downstream outcomes, and distill that signal into a lightweight specialist. The core loop is reproducible without the full AutoMem infrastructure.

**Links**: [arXiv:2607.01224](https://arxiv.org/abs/2607.01224) · [autolearnmem.github.io](https://autolearnmem.github.io)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
