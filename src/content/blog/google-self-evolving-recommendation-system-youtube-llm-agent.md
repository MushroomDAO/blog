---
title: "Google YouTube 自进化推荐系统：LLM Agent 替代 ML 工程师，双环架构工程落地指南"
titleEn: "Google YouTube's Self-Evolving Recommendation System: LLM Agents Replace ML Engineers — Dual-Loop Architecture Engineering Guide"
description: "arXiv:2602.10226，RecSys 2026，Google YouTube 团队。LLM（Gemini 2.5）驱动双环 Agent 架构，自主发现优化器、神经架构和奖励函数改进，优于64%人工 launches。本文深度解析论文架构，并给出可落地的工程实现指南。"
descriptionEn: "arXiv:2602.10226, RecSys 2026, Google YouTube. LLM-driven (Gemini 2.5) dual-loop agent architecture autonomously discovers optimizer, architecture, and reward improvements — outperforming 64% of manual engineer launches. Deep paper analysis plus practical engineering implementation guide."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Research"
tags: ["推荐系统", "AI Agent", "Google", "YouTube", "LLM", "自进化", "强化学习", "机器学习工程", "论文解读"]
heroImage: "../../assets/images/google-self-evolving-recommendation-system-youtube-llm-agent-banner.jpg"
---

> **论文**：Self-Evolving Recommendation System: End-To-End Autonomous Model Optimization With LLM Agents
> **arxiv**：[2602.10226](https://arxiv.org/abs/2602.10226) · **会议**：RecSys 2026（ACM，Minneapolis）
> **作者**：Haochen Wang, Yi Wu, Daryl Chang, Li Wei, Lukasz Heldt（Google YouTube）
> **发布**：2026-02-10 · **最新版本**：2026-07-23

---

## 一、一句话总结这篇论文

**用 LLM（Gemini 2.5）构建两个 AI Agent，让它们像 ML 工程师一样自主修改推荐系统代码、跑实验、分析结果，然后把能提升用户满意度的改动发布到 YouTube 生产环境——不需要人工干预。**

结果：这套自进化系统产出的优化方案，超过了 64% 的人工工程师方案（YouTube 级指标），超过 73%（Surface 级指标），并且在两周内解决了人工团队数月未攻克的奖励函数调参问题。

---

## 二、问题背景：为什么传统方式走到了瓶颈

YouTube 的推荐系统是一个基于强化学习（RL）的排序模型，核心任务是最大化用户的长期满意度。这套系统有三个关键组件需要持续优化：

- **优化器**（Optimizer）：Adagrad、RMSprop、Adam 以及各自的超参数组合，搜索空间极大
- **神经网络架构**（Architecture）：层数、激活函数、门控机制……每个结构决策都影响模型的表达能力
- **奖励函数**（Reward）：如何把观看时长、互动率、留存等信号组合成一个 RL 训练目标

传统方式是让 ML 工程师手动提出假设 → 写代码 → 跑实验 → 分析结果 → 迭代。瓶颈很明显：

1. 每次实验需要 Θ(hours) 的模型训练时间，加上 Θ(days/weeks) 的在线 A/B 实验验证，整个周期极长
2. 工程师的注意力有限，探索的配置空间只是全部可能性的极小一角
3. 在线北极星指标（用户真实满意度）是**延迟、稀疏、有噪声**的——和离线 loss 之间有对齐鸿沟

这三个问题加在一起，导致传统人工迭代效率极低，大量潜在的优化方案被遗漏。

---

## 三、核心架构：双环自进化系统

### 总体设计

```
                    ┌─────────────────────────────────┐
                    │       Experiment Journal         │
                    │  (共享持久知识库：所有实验历史    │
                    │   配置 + 离线分数 + 在线指标)    │
                    └────────────┬────────────────────┘
                                 │ 读取/写入
              ┌──────────────────┴──────────────────────┐
              │                                         │
   ┌──────────▼──────────────┐             ┌────────────▼────────────────┐
   │   Offline Agent          │             │   Online Agent               │
   │   (Fast Loop / 内环)     │             │   (Slow Loop / 外环)         │
   │                          │             │                              │
   │  频率：每5分钟唤醒一次   │             │  频率：每天运行一次          │
   │  职责：生成候选配置       │  ──候选──▶  │  职责：排序候选，晋升到A/B  │
   │  优化目标：最小化离线指标 │             │  优化目标：最大化北极星指标  │
   │                          │             │                              │
   │  三个专业 Persona：       │             │  全生命周期管理：            │
   │  ├─ Optimizer Persona    │             │  ├─ 读取在线指标            │
   │  ├─ Architecture Persona │             │  ├─ 决定晋升哪些候选        │
   │  └─ Reward Persona       │             │  └─ 终止表现差的实验        │
   └──────────────────────────┘             └──────────────────────────────┘
              │
              ▼
   [工具调用：compute_loss / run_sql_query / compute_eval]
              │
              ▼
   [生产部署：训练 → 验证 → A/B测试 → 发布]
```

### 核心组件一：Experiment Journal（实验日志）

这是整个系统的**记忆和知识积累器**。每个 Agent 完成一次实验后，都会把以下内容写入 Journal：

- 实验配置（`delta`：相对于 baseline 的代码变更）
- 离线指标得分
- 在线 A/B 结果（如果有）

下次 Agent 被唤醒时，它读取整个 Journal 历史，用历史上"哪些方向有效、哪些无效"来指导下一轮假设生成。**Journal 就是系统的长期记忆，让 Agent 不会重复探索已经失败的方向。**

---

### 核心组件二：Offline Agent（Fast Loop）

**职责**：高频生成候选配置，用离线代理指标快速筛选。

#### 为什么要专业化 Persona？

论文发现，当 Agent 接触完整代码库时，从约 400k tokens 开始出现幻觉。解法是**专业化分工**：每个 Persona 只聚焦于约 10 行代码的修改，而不是整个系统。

三个 Persona：

**A. Optimizer Persona（优化器专家）**

搜索空间：优化器类型（Adagrad、RMSprop、Adam 等）和超参数（学习率、动量、批量大小）

```python
# 典型 Persona prompt 注入
AGENT_SPECIALIZATION = """
You are a deep learning optimization expert.
Focus ONLY on the optimizer class and its hyperparameters.
Current baseline: Adagrad(lr=0.01)
Goal: Find a better optimizer configuration.
"""
```

评估工具：`compute_loss`——直接计算验证集 loss，候选之间可以直接比大小。

**B. Architecture Persona（架构专家）**

搜索空间：网络拓扑（层数、连接方式、激活函数、门控机制）

**关键差异**：传统 NAS 只能从预定义的操作菜单里选，这个 Persona 可以**写新代码**——比如发明了一种 Gated Path 机制（类似 GLU，引入乘法门控），这是搜索空间里从未存在过的结构。

评估工具：也是 `compute_loss`。

**C. Reward Persona（奖励工程专家）**

最复杂的一个。推荐系统有 Θ(100) 个用户信号（观看时长、调查反馈、留存率……），如何把它们组合成一个好的 RL 训练目标，是工程师历来最难解决的问题。

```python
# Reward Persona 的工作流
1. run_sql_query("SELECT signal_name, correlation_with_retention 
                  FROM user_logs 
                  WHERE timestamp > NOW() - 30d 
                  GROUP BY signal_name 
                  ORDER BY correlation DESC")
   # 分析百亿级用户日志，发现哪些信号与长期留存高度相关

2. 基于 SQL 发现，生成新的奖励函数代码
   # 例如：发现"用户在站内主动搜索"是高价值行为信号

3. compute_eval(reward_fn, proxy_dataset)
   # 用代理数据集评估新奖励函数
```

这个 Persona 的输出不能用 loss 衡量（因为改变了 loss 的定义），所以需要一套独立的代理评估逻辑。

---

### 核心组件三：Online Agent（Slow Loop）

**职责**：低频决策——从 Fast Loop 的候选里选出最有潜力的，推进到真实 A/B 实验。

```
每天运行一次，读取 Experiment Journal
      │
      ▼
对所有候选按"预期在线提升"排序
      │
      ▼
决定：晋升哪些到在线实验？终止哪些？
      │
      ▼
拉取在线 A/B 结果写回 Journal
```

Online Agent 有**安全护栏（Guardrails）**：

```python
# Guardrails 示例
CONSTRAINTS = """
GUARDRAILS:
- Metric_A must not drop more than +1%
- Metric_B (user wellbeing) must not deteriorate
- No changes to safety-critical components without human review
"""
```

这防止了 Agent 为了提升主指标而损害用户体验或系统安全性。

---

### 共享提示模板

两个 Agent 复用同一套提示结构，只替换 `AGENT_TASK` 部分：

```
# PERSONA
你是一位顶尖的机器学习科学家，擅长 {AGENT_SPECIALIZATION}。

{AGENT_TASK}  ← Offline Agent 或 Online Agent 各自的具体任务

# CONTEXT
当前模型配置：[BASELINE CONFIGURATION]
历史 SQL 查询输出（如有）：{SQL_QUERY_OUTPUT}
历史实验记录（按离线得分排序，最优在前）：[EXPERIMENT JOURNAL]

# EXAMPLE PROPOSAL
{AGENT_EXAMPLE}  ← 少样本示例，引导输出格式
```

**提示设计的三个关键**：
1. **排序很重要**：Journal 按离线得分排序（而不是时间序）显著提升了 Agent 表现（消融实验验证）
2. **Persona 很重要**：去掉专家 Persona 框架，性能下降明显
3. **模型选择很重要**：Gemini 2.5 Pro > Flash，推理能力直接决定假设质量

---

## 四、关键实验结果

| 优化方向 | 具体发现 | 生产效果 |
|---------|---------|---------|
| 优化器 | 从 Adagrad 切换到 RMSprop（特定超参数） | 统计显著的 loss 下降 + 在线指标提升 |
| 训练效率 | 批量大小 + epoch 数调优 | 训练时间减少 **8×**，无损收敛 |
| 网络架构 | 发明 Gated Path（乘法门控 + GELU + LayerNorm） | 最鲁棒的在线提升之一 |
| 奖励函数 | 发现用户"主动参与"信号，合成新奖励 | 显著超越人工设计的 baseline |
| 奖励超参数 | 4个参数组合，无离线指标，纯在线探索 | 2周解决了人工数月未解的问题 |

**对比基准**：
- 超越 **64%** 的人工工程师 launches（YouTube 级指标）
- 超越 **73%** 的人工工程师 launches（Surface 级指标）

---

## 五、工程落地指南

### 5.1 最小可行实现：你的规模不是 YouTube，但架构可以复用

以一个中型推荐系统为例（DAU 百万级，电商/内容平台），以下是可落地的实现方案。

**前提条件**：
- 有一套可程序化训练的推荐模型（PyTorch/TensorFlow）
- 有离线评估指标（AUC、NDCG、loss 等）
- 有 A/B 测试基础设施（或至少有在线指标采集）
- 有 LLM API（Claude、GPT-4o、Gemini 均可）

---

### 5.2 Experiment Journal 实现

用数据库或简单的 JSON 文件实现。核心字段：

```python
# experiment_journal.py
import json
from datetime import datetime
from pathlib import Path

class ExperimentJournal:
    def __init__(self, path: str = "experiments.json"):
        self.path = Path(path)
        self.entries = []
        if self.path.exists():
            self.entries = json.loads(self.path.read_text())
    
    def add_entry(self, config_delta: str, offline_score: float, 
                  online_metrics: dict = None, status: str = "offline_only"):
        entry = {
            "id": f"exp_{len(self.entries):04d}",
            "timestamp": datetime.now().isoformat(),
            "delta": config_delta,         # 相对 baseline 的变更描述
            "offline_score": offline_score, # 越小越好（loss）
            "online_metrics": online_metrics or {},
            "status": status,              # offline_only / promoted / launched / rejected
        }
        self.entries.append(entry)
        self.path.write_text(json.dumps(self.entries, indent=2, ensure_ascii=False))
        return entry
    
    def get_sorted_history(self, top_k: int = 50) -> str:
        """按离线分数排序，最优在前，返回给 LLM 的上下文字符串"""
        sorted_entries = sorted(
            [e for e in self.entries if e["offline_score"] is not None],
            key=lambda x: x["offline_score"]
        )[:top_k]
        return json.dumps(sorted_entries, indent=2, ensure_ascii=False)
```

---

### 5.3 Offline Agent（Fast Loop）实现

```python
# offline_agent.py
import anthropic  # 或 openai / google-genai
import subprocess
import json

class OfflineAgent:
    def __init__(self, journal: ExperimentJournal, llm_client, 
                 baseline_config: dict, model_trainer):
        self.journal = journal
        self.llm = llm_client
        self.baseline = baseline_config
        self.trainer = model_trainer
    
    def run_optimizer_persona(self) -> list[dict]:
        """Optimizer Persona：搜索优化器配置"""
        
        prompt = f"""# PERSONA
你是一位深度学习优化专家，专注于训练算法和超参数优化。

# GOAL
提出3个候选优化器配置：
- 1个保守改进（调整现有优化器超参数）
- 1个探索性改进（尝试不同的优化器类型）
- 1个创新性改进（组合多种技术）

# CONTEXT
当前配置：{json.dumps(self.baseline['optimizer'], ensure_ascii=False)}
历史实验记录（按loss排序）：
{self.journal.get_sorted_history(top_k=20)}

# OUTPUT FORMAT
输出 JSON 数组，每项包含：
- "explanation": 这个改动的原理和预期效果
- "delta": 具体的配置变更（Python dict）
"""
        
        response = self.llm.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        proposals = json.loads(response.content[0].text)
        results = []
        
        for proposal in proposals:
            # 训练并评估
            score = self.trainer.train_and_eval(
                optimizer_config=proposal["delta"],
                metric="val_loss"
            )
            # 写入 Journal
            entry = self.journal.add_entry(
                config_delta=json.dumps(proposal["delta"]),
                offline_score=score,
                status="offline_only"
            )
            results.append({**entry, "proposal": proposal})
        
        return results
    
    def run_reward_persona(self, sql_engine) -> list[dict]:
        """Reward Persona：分析用户数据，设计新奖励函数"""
        
        # Step 1: 让 LLM 生成 SQL 查询，分析用户行为数据
        analysis_prompt = f"""分析以下用户行为信号与长期用户留存的相关性。
请生成一个 SQL 查询，找出最有价值的信号组合。

可用的信号表：user_events(user_id, event_type, timestamp, duration, ...)
目标指标：7日留存率

只输出 SQL，不需要解释。"""
        
        sql_response = self.llm.messages.create(
            model="claude-opus-4-8",
            max_tokens=500,
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        sql = sql_response.content[0].text.strip()
        query_results = sql_engine.execute(sql)
        
        # Step 2: 基于数据分析，生成新奖励函数
        reward_prompt = f"""# PERSONA
你是奖励工程专家，擅长设计 RL 训练目标。

# DATA ANALYSIS RESULT
{query_results.to_markdown()}

# GOAL
基于以上数据分析，设计一个新的奖励函数来更好地捕捉用户长期满意度。

# OUTPUT FORMAT
输出 JSON，包含：
- "explanation": 设计理由
- "reward_code": 完整的 Python 奖励函数代码
"""
        
        reward_response = self.llm.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            messages=[{"role": "user", "content": reward_prompt}]
        )
        
        return json.loads(reward_response.content[0].text)
    
    def wake_up(self):
        """每5分钟调用一次"""
        print(f"[FastLoop] 唤醒，当前 Journal 有 {len(self.journal.entries)} 条记录")
        
        # 轮流激活各个 Persona
        results = []
        results.extend(self.run_optimizer_persona())
        # results.extend(self.run_architecture_persona())
        # results.extend(self.run_reward_persona(sql_engine))
        
        return results
```

---

### 5.4 Online Agent（Slow Loop）实现

```python
# online_agent.py
class OnlineAgent:
    def __init__(self, journal: ExperimentJournal, llm_client,
                 ab_testing_platform, guardrails: dict):
        self.journal = journal
        self.llm = llm_client
        self.ab = ab_testing_platform
        self.guardrails = guardrails
    
    def rank_candidates(self) -> list[str]:
        """每天运行一次：对候选排序，决定晋升哪些到 A/B"""
        
        candidates = [e for e in self.journal.entries 
                      if e["status"] == "offline_only"]
        
        if not candidates:
            return []
        
        prompt = f"""# PERSONA
你是一位资深推荐系统工程师，擅长实验设计和业务指标分析。

# GOAL
对以下候选配置进行排序，选出最有潜力在真实用户实验中提升北极星指标的 TOP-3。

北极星指标优先级（按重要性）：
1. 用户7日留存率
2. 人均日活时长
3. 内容多样性得分

# GUARDRAILS
以下指标不能下降超过阈值：
{json.dumps(self.guardrails, ensure_ascii=False)}

# CANDIDATES
{json.dumps(candidates, indent=2, ensure_ascii=False)}

# HISTORY（包含在线结果）
{self.journal.get_sorted_history(top_k=30)}

# OUTPUT FORMAT
输出 JSON 数组，按优先级排序：
[{{"id": "exp_0001", "reason": "..."}}, ...]
只选出你认为值得晋升到真实 A/B 的候选，最多3个。
"""
        
        response = self.llm.messages.create(
            model="claude-opus-4-8",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        ranked = json.loads(response.content[0].text)
        return ranked
    
    def promote_and_monitor(self):
        """晋升候选到 A/B，监控并写回结果"""
        ranked = self.rank_candidates()
        
        for candidate in ranked[:2]:  # 每次最多同时跑2个实验
            exp_id = candidate["id"]
            
            # 晋升到 A/B 测试
            ab_id = self.ab.launch_experiment(exp_id)
            self.journal.update_status(exp_id, "promoted", ab_id=ab_id)
            
            # 7天后自动拉取结果
            # （实际需要调度器支持）
        
        # 检查进行中的实验结果
        for entry in self.journal.entries:
            if entry["status"] == "promoted" and entry.get("ab_id"):
                metrics = self.ab.get_results(entry["ab_id"])
                if metrics:
                    # 检查 guardrails
                    safe = all(
                        metrics.get(k, 0) >= -v 
                        for k, v in self.guardrails.items()
                    )
                    status = "launched" if safe and metrics["primary"] > 0 else "rejected"
                    self.journal.update_status(entry["id"], status, 
                                               online_metrics=metrics)
```

---

### 5.5 调度器：把两个 Loop 跑起来

```python
# scheduler.py
import schedule
import time
import threading

def run_system(offline_agent: OfflineAgent, online_agent: OnlineAgent):
    
    # Fast Loop: 每5分钟
    schedule.every(5).minutes.do(offline_agent.wake_up)
    
    # Slow Loop: 每天早上9点
    schedule.every().day.at("09:00").do(online_agent.promote_and_monitor)
    
    print("自进化系统启动")
    while True:
        schedule.run_pending()
        time.sleep(60)

# 启动
journal = ExperimentJournal("experiments.json")
offline_agent = OfflineAgent(journal, llm_client, baseline_config, trainer)
online_agent = OnlineAgent(journal, llm_client, ab_platform, guardrails={
    "user_wellbeing_score": 0.01,   # 不能下降超过1%
    "content_diversity_index": 0.02  # 不能下降超过2%
})

thread = threading.Thread(target=run_system, args=(offline_agent, online_agent))
thread.start()
```

---

### 5.6 关键工程注意事项

**1. 离线指标 ≠ 在线指标**

这是最重要的设计挑战。论文中 YouTube 有严格的代理指标体系来近似北极星指标。你需要在自己的系统里建立同样的映射：

- 哪个离线指标与在线指标历史上最相关？
- 多少 offline 提升能对应多少 online 提升？
- 建立这套映射本身需要大量历史数据

**2. 上下文窗口管理**

论文发现 400k tokens 后开始幻觉。实践建议：
- Persona 专业化（每个只看自己的 ~1000 行代码）
- Journal 只给 top-50 历史（按离线排序）
- 使用 few-shot examples 锚定输出格式

**3. 安全护栏必须在系统层面执行**

不能只靠 LLM 自律。在 Online Agent 的晋升逻辑里，对 guardrails 做硬判断——违反任何一条就自动拒绝，无论在线指标表现如何好。

**4. 中小团队的简化版双环**

| 完整版（YouTube 级） | 简化版（中小团队） |
|--------------------|--------------------|
| 每5分钟快速唤醒 | 每小时运行一次 |
| 自动化训练流水线 | 人工触发训练，Agent 分析结果 |
| 真实 A/B 测试 | 离线回测 + 人工决策是否上线 |
| 三个专业 Persona | 先只做 Optimizer Persona |
| Gemini 2.5 Pro | Claude Opus 4 或 GPT-4o |

---

## 六、GitHub 现有实现情况

截至 2026-07-24（论文极新，发表于 2026-02-10），**GitHub 上尚无公开的、直接基于此论文的完整实现**。

但有几个相关的开源项目提供了部分可借鉴的组件：

| 项目 | 相关组件 | 参考价值 |
|------|---------|---------|
| [microsoft/LMOps](https://github.com/microsoft/LMOps) | OPRO（LLM 作为优化器）| Offline Agent 的 prompt 优化思路 |
| [google-deepmind/alphaevolve-framework](https://github.com/google-deepmind) | AlphaEvolve（LLM 代码进化）| Architecture Persona 的实现参考 |
| [ai-scientist/ai-scientist](https://github.com/SakanaAI/AI-Scientist) | AI Scientist（自动科研）| Experiment Journal 的设计参考 |
| [eureka-research/Eureka](https://github.com/eureka-research/Eureka) | Eureka（LLM 设计 RL 奖励）| Reward Persona 的直接前驱 |

论文本身引用了这些工作（AlphaEvolve、AI Scientist、Eureka、OPRO）作为直接前驱，因此这些项目是目前最接近的工程参考。

---

## 七、判断：这套架构的边界和意义

**真正的突破点**不是"LLM 能优化超参数"——这个大家都想到了。真正的突破是这三件事组合在一起：

1. **Reward Persona 能做语义推理**：通过 SQL 分析百亿级日志，发现"用户主动在站内搜索"这个信号与长期留存高度相关，然后把它写进奖励函数。这是纯超参数搜索做不到的。

2. **双环解决了对齐鸿沟**：离线快速探索 + 在线严格验证。Fast Loop 负责廉价地探索（失败成本低），Slow Loop 负责昂贵地验证（只有真正有潜力的候选才消耗 A/B 流量）。

3. **Experiment Journal 让 Agent 变聪明**：第一轮实验的失败，成为第二轮实验的先验知识。这是传统 NAS/HPO 做不到的——它们没有"为什么失败"的语义理解。

**局限性**：
- 依赖高质量的离线代理指标体系（建立这套体系本身是难题）
- 需要 Θ(hours) 训练时间的实验基础设施
- Gemini 2.5 Pro 推理成本不低（每天数十次 LLM 调用，加上长上下文）
- 论文只报告了成功案例，失败率和安全事故未公开

**对中小团队的启示**：

完整复刻这套系统需要 YouTube 级的基础设施。但核心理念可以在更小的规模落地：

- 用 LLM 辅助假设生成（人工仍然决策）
- Experiment Journal 作为实验记录工具（让 LLM 分析历史，提建议）
- Reward Persona 的思路（用 SQL 分析数据，让 LLM 提奖励函数候选）

从 Reward Persona 开始是成本效益最高的切入点——奖励函数设计是最难、人工投入最大、也最容易让 LLM 提供增量价值的组件。

---

*论文来源：arXiv:2602.10226，Google YouTube 团队，2026-07-24 分析整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: Self-Evolving Recommendation System: End-To-End Autonomous Model Optimization With LLM Agents
> **arxiv**: [2602.10226](https://arxiv.org/abs/2602.10226) · **Venue**: RecSys 2026 (ACM, Minneapolis)
> **Authors**: Haochen Wang, Yi Wu, Daryl Chang, Li Wei, Lukasz Heldt (Google YouTube)
> **Published**: 2026-02-10 · **Latest version**: 2026-07-23

---

## 1. One-Sentence Summary

**Use LLMs (Gemini 2.5) to build two AI Agents that act as ML engineers — autonomously modifying recommendation system code, running experiments, analyzing results, and deploying improvements to YouTube's production environment — with no human intervention.**

The result: the self-evolving system outperformed 64% of human engineer launches (YouTube-level metric) and 73% (Surface-level metric), solving in two weeks a reward function tuning problem that had stumped human engineers for months.

---

## 2. Why Traditional Approaches Hit a Wall

YouTube's recommendation system is a Reinforcement Learning (RL)-based ranker with three components that need continuous optimization:

- **Optimizer**: Adagrad, RMSprop, Adam and their hyperparameter combinations — massive search space
- **Architecture**: Layer counts, activations, gating mechanisms — each structural choice affects model expressivity
- **Reward function**: How to combine watch time, interaction rates, retention, etc. into a single RL training objective

Traditional workflow: ML engineers manually propose hypotheses → write code → run experiments → analyze results → iterate. The bottlenecks are obvious:

1. Each experiment requires Θ(hours) of model training plus Θ(days/weeks) of live A/B validation — the full cycle is long
2. Engineers' attention is finite — the configurations explored are a tiny fraction of the full possibility space
3. The online north star metric (real user satisfaction) is **delayed, sparse, and noisy** — fundamentally misaligned with offline loss

Together, these create a system where most potential improvements go undiscovered.

---

## 3. Core Architecture: The Dual-Loop Self-Evolving System

### The Experiment Journal

The system's **memory and knowledge accumulator**. After every experiment, each agent writes:
- Configuration delta (code changes relative to baseline)
- Offline metric score
- Online A/B results (when available)

On the next wake-up, the agent reads the full Journal history — learning from what succeeded and what failed — to guide the next round of hypothesis generation. **The Journal is the system's long-term memory, preventing repeated exploration of already-failed directions.**

---

### The Offline Agent (Fast Loop)

**Role**: High-frequency candidate generation, rapid screening via offline proxy metrics.

**Wake-up frequency**: Every 5 minutes.

**Why specialized personas?** At ~400k tokens of codebase context, the model starts hallucinating. The solution: **specialization**. Each persona focuses on ~10 lines of code changes, not the entire system.

**Three personas:**

**A. Optimizer Persona**

Searches optimizer type (Adagrad, RMSprop, Adam) and hyperparameters (learning rate, momentum, batch size).

Tool: `compute_loss` — directly comparable across candidates, lower is better.

**B. Architecture Persona**

Searches network topology: layer structure, activation functions, gating mechanisms.

**Key distinction from traditional NAS**: NAS picks from a predefined menu of operations. This persona can **write new code** — for example, it invented a Gated Path mechanism (similar to Gated Linear Units / GLU) that didn't exist in the original search space.

Tool: also `compute_loss`.

**C. Reward Persona**

The most complex persona. A recommendation system has Θ(100) user signals (watch time, surveys, retention...). Combining them into a good RL training objective is historically the hardest engineering challenge.

Process:
1. Use `run_sql_query` to analyze petabytes of user logs — find which signals correlate with long-term engagement
2. Based on findings, generate candidate reward function code
3. Use `compute_eval` to score with a proxy dataset

The paper's example: the agent discovered that "user actively searching within the platform" is a high-value signal for long-term retention — then encoded this into the reward function. Human engineers had explored hundreds of other combinations without finding this.

---

### The Online Agent (Slow Loop)

**Role**: Low-frequency strategic decisions — select the most promising candidates from the Fast Loop and promote them to real A/B experiments.

**Run frequency**: Once per day.

The Online Agent manages the full experiment lifecycle:
- Reads fresh online metrics from the Journal
- Ranks candidates by expected online uplift
- Decides which to promote to live traffic (expensive — reserved for high-potential candidates only)
- Terminates underperforming experiments

**Safety guardrails** are enforced at the system level — not just in the LLM prompt:
- User wellbeing metrics cannot drop below threshold
- Safety-critical system components require human review
- Any guardrail violation → automatic rejection regardless of primary metric performance

---

### Shared Prompt Template

Both agents share the same structure, with `{AGENT_TASK}` swapped:

```
# PERSONA
You are a brilliant ML scientist specializing in {AGENT_SPECIALIZATION}.

{AGENT_TASK}

# CONTEXT
Current model config: [BASELINE]
SQL query outputs (if any): {SQL_QUERY_OUTPUT}
Experiment history (sorted by offline score, best first): [EXPERIMENT JOURNAL]

# EXAMPLE PROPOSAL
{AGENT_EXAMPLE}
```

Three critical prompt engineering findings from ablation studies:
1. **Sorting matters**: History sorted by offline score (not timestamp) significantly outperforms
2. **Persona matters**: Removing the expert MLE persona framing degrades performance noticeably
3. **Model matters**: Gemini 2.5 Pro >> Flash for this task — reasoning quality directly determines hypothesis quality

---

## 4. Key Results at YouTube

| Optimization | Discovery | Production Impact |
|-------------|-----------|------------------|
| Optimizer | Switched Adagrad → RMSprop (specific hyperparams) | Statistically significant loss reduction + online lift |
| Training efficiency | Batch size + epoch tuning | Training time reduced **8×** without degrading convergence |
| Architecture | Invented Gated Path (multiplicative gate + GELU + LayerNorm) | Most robust online improvement in deployment |
| Reward function | Discovered "active user engagement" signal, synthesized new reward | Significantly outperformed human-engineered baseline |
| Reward hyperparams | 4-parameter search, no offline metric — pure online exploration | Solved in **2 weeks** what human engineers couldn't solve in **months** |

**vs. human benchmark**: outperformed 64% of manual launches (YouTube-level), 73% (Surface-level), measured over 6 months of historical launches.

---

## 5. Engineering Implementation Guide

### 5.1 Minimum Viable Architecture for Mid-Scale Systems

You're not YouTube. But the dual-loop architecture scales down.

| Full scale (YouTube) | Simplified (mid-scale team) |
|---------------------|-----------------------------|
| 5-minute fast wake-up | Hourly runs |
| Fully automated training pipeline | Human-triggered training; agent analyzes results |
| Real A/B testing | Offline backtesting + human go/no-go decision |
| All three personas in parallel | Start with Optimizer Persona only |
| Gemini 2.5 Pro | Claude Opus 4 or GPT-4o |

### 5.2 Experiment Journal Schema

```python
{
  "id": "exp_0042",
  "timestamp": "2026-07-24T10:30:00",
  "delta": "{'optimizer': 'rmsprop', 'lr': 0.001, 'momentum': 0.9}",
  "offline_score": 0.2847,        # lower is better (loss)
  "online_metrics": {
    "retention_7d": +0.003,        # +0.3%
    "watch_time_per_session": -0.001
  },
  "status": "launched"            # offline_only / promoted / launched / rejected
}
```

### 5.3 Start with the Reward Persona

Of the three personas, the **Reward Persona gives the highest ROI for ML engineering teams**:

1. Human reward engineering is the most labor-intensive component
2. SQL-based data analysis is straightforward to implement
3. The hypothesis space is semantically rich — exactly where LLMs outperform brute-force search
4. No new training infrastructure needed for initial experiments

Starting path:
1. Give the LLM your user event schema + current reward function
2. Ask it to run SQL analysis to find underweighted signals
3. Propose 3 candidate reward modifications with rationale
4. Human reviews and decides which to test
5. Write A/B results back to the Journal
6. Repeat — let the Journal accumulate

### 5.4 Guardrail Checklist

Before promoting any candidate to production:

```python
GUARDRAILS = {
    "primary_wellbeing_score": -0.01,    # must not drop >1%
    "content_diversity_index": -0.02,    # must not drop >2%
    "user_complaint_rate": +0.005,       # must not increase >0.5%
}

def is_safe_to_launch(online_metrics: dict, guardrails: dict) -> bool:
    for metric, threshold in guardrails.items():
        delta = online_metrics.get(metric, 0)
        if delta < threshold:  # violation
            return False
    return True
```

---

## 6. Related Open-Source Projects (as of 2026-07-24)

No public implementation of this exact paper exists yet (published February 2026). The closest reference implementations:

| Project | Relevant Component |
|---------|-------------------|
| [Eureka](https://github.com/eureka-research/Eureka) | Direct predecessor: LLM-designed RL rewards (robotics) |
| [AI Scientist](https://github.com/SakanaAI/AI-Scientist) | LLM-automated research loop design |
| [OPRO](https://github.com/google-deepmind/opro) | LLMs as optimizers via prompting |
| [AlphaEvolve](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) | Code evolution for algorithmic discovery |

---

## 7. What Actually Matters Here

The breakthrough is not "LLMs can tune hyperparameters" — everyone already knew that. The three things that make this work together:

**1. The Reward Persona does semantic reasoning.** SQL analysis of billions of user logs to discover that "active in-platform search" predicts long-term retention — then encoding that insight into the reward function. Pure hyperparameter search can't do this.

**2. The dual loop solves the alignment gap.** Fast Loop explores cheaply (low cost of failure). Slow Loop validates expensively (A/B traffic reserved for high-potential candidates only). This decoupling is the core architectural insight.

**3. The Experiment Journal makes the agents smarter over time.** Failure in round 1 becomes prior knowledge in round 2. Traditional NAS/HPO doesn't have semantic understanding of *why* something failed.

For mid-scale ML teams: start with the Reward Persona + a simple Journal. Get LLMs reasoning about your reward function design. That's the fastest path to meaningful impact from this paper.

---

*Source: arXiv:2602.10226, Google YouTube team, analysis compiled 2026-07-24.*

© 2026 Author: Mycelium Protocol
