---
title: "别浪费失败！斯坦福用「失败轨迹」让 GUI Agent 无需训练提升 15%（ECCV 2026）"
titleEn: "Don't Waste Failures! Stanford Boosts GUI Agents 15% at Inference Time by Mining Failed Trajectories (ECCV 2026)"
description: "斯坦福 ECCV 2026 论文：把 AI Agent 执行失败的轨迹喂给 Claude 4.5 做诊断，自动生成「代码补丁」注入推理过程。OSWorld 基准 42.3%→48.9%（+15.6% 相对提升），零训练成本，仅增加 8% 推理开销，步数反降 15%。四大失败模式逐一击破：定位错误、能力缺口、知识不足、死循环。"
descriptionEn: "Stanford ECCV 2026 paper: Feed failed agent trajectories to Claude 4.5 for diagnosis, auto-generate code patches injected at inference time. OSWorld: 42.3%→48.9% (+15.6% relative), zero training cost, only 8% inference overhead, 15% fewer interaction steps. Four failure modes addressed: grounding errors, competency gaps, knowledge deficiencies, redundant loops."
pubDate: "2026-07-26"
updatedDate: "2026-07-26"
category: "Research"
tags: ["GUI Agent", "失败驱动学习", "Computer Use", "OSWorld", "推理时优化", "斯坦福", "自进化Agent", "ECCV2026"]
heroImage: "../../assets/images/learning-from-failure-gui-agent-stanford-banner.jpg"
---

> **论文**：Learning from Failure: Inference-Time Self-Improvement for Computer-Use Agents
> **arXiv**：2606.31270（ECCV 2026）
> **作者**：Xueqiao Sun, Xiaohan Wang, Ludwig Schmidt, Serena Yeung-Levy, Yuhui Zhang（Stanford + Tsinghua）
> **核心指标**：OSWorld 42.3%→48.9%（+15.6% relative），零训练成本，8% 推理开销，步数↓15%

---

## 一、标准范式的盲点：失败是垃圾吗？

当前训练 GUI Agent 的标准做法是「成功驱动循环」：

```
Agent 执行任务 → 评估结果 → 保留成功轨迹 → 微调模型 → 重复
```

这条流水线有效，但有个根本性的浪费：**所有失败的执行轨迹被直接扔掉**。

斯坦福团队的核心洞察是：失败轨迹里恰恰包含了最有价值的信息——模型在哪里卡住、用了什么错误策略、为什么无法恢复。这些信息与其说是噪声，不如说是一份精准的「诊断报告」。

问题来了：能不能不重训模型，只用这些失败信息在推理时修复 Agent？

答案是肯定的。

---

## 二、失败驱动循环：架构概述

论文提出的框架叫 **Failure-Case Loop**，对应图示如下：

```
Agent 执行任务（rollout）
        ↓
收集失败轨迹（任务指令 + 动作历史 + 思考过程）
        ↓
LLM（Claude 4.5 Sonnet）诊断失败模式
        ↓
提出推理时解决方案（概念调整 + 代码补丁）
        ↓
轻量人工验证（97% 直接采纳，无需修改）
        ↓
补丁注入 Agent 推理过程
        ↓
Agent 执行任务（新一轮 rollout）→ 循环 K 次
```

关键设计选择：

1. **不修改模型权重**：所有改进以代码补丁形式注入推理过程（prompt 增强 + 功能模块）
2. **LLM 作为元控制器**：Claude 4.5 Sonnet 同时承担失败分析、方案设计、代码实现三个角色
3. **迭代收敛**：每轮识别当前最主要的失败模式并修复，4 轮后效果最优
4. **轻量人工验证**：97% 的 LLM 生成补丁直接被接受——几乎全自动

---

## 三、四大失败模式：逐一解剖

### 失败模式 1：定位错误（Grounding Errors）

**表现**：Agent 点不准 UI 元素，在高分辨率或视觉密集界面中坐标偏移。

**典型案例**：要在 GIMP 里降低亮度，Agent 按了"向上箭头"而不是"向下箭头"。

**修复策略：Visual Search（视觉搜索）**

每次执行 click/moveto/dragto 动作后，框架自动：
1. 裁剪点击位置为中心的 400×400 像素区域
2. 将裁剪区域放大 2 倍（更高分辨率上下文）
3. 在原始点击位置绘制半径 7 像素的红色空心圆圈
4. 将标注图像 + 任务指令 + 动作历史一起喂给 Agent 自我验证
5. 若坐标有偏差，Agent 自行修正，替换原始动作

这是一种**后动作视觉自验证**机制——先点，发现点歪了，立即自我纠正。

**效果**：OSWorld small set 41.67% → 47.22%（+5.55pp）

### 失败模式 2：能力缺口（Competency Gaps）

**表现**：Agent 不知道用终端，只会鼠标点点点，导致复杂任务的执行效率极低且容易出错。

**典型案例**：把某个文件的路径复制到剪贴板——Agent 疯狂点击 GUI，但用两条 shell 命令就能搞定。

**修复策略：Terminal Execution（终端执行）**

给 Agent 的 prompt 加入：

> "Tool: Terminal — Use the keyboard shortcut Ctrl + Alt + T to open a terminal window. Consider this a shortcut for some complex tasks."

对于能力更弱的模型（如 GUI-Owl-32B），额外注入：
- 密码命令的处理方式
- 终端检测到激活后自动追加「关键终端规则」（cd/ls/ln/ffmpeg 都需要手动 Enter）

**效果**：单独使用 +5.52pp

### 失败模式 3：知识不足（Knowledge Deficiencies）

**表现**：Agent 不认识某些软件的快捷键，或不知道特定命令的正确语法，导致反复试错。

**修复策略：双路知识支持**

**路线 A：搜索引擎**（外部知识）
接入 GPT-5-mini 作为受控搜索接口，Agent 可以在单步内发起多次查询，逐步收敛理解后再生成动作。

典型案例：遇到"conda: command not found"错误 → 查 GPT-5-mini → 学会安装方法 → 完成任务。

**路线 B：软件手册**（内部知识注入）
为 LibreOffice Calc/Writer 预置精选快捷键手册（而非整份官方文档）。

典型案例：对每一行计算到期日期 → 原本陷入 Ctrl+C/Ctrl+V 死循环 → 得到手册后发现 Ctrl+D 可以一键填充选中区域。

**效果**：41.67% → 44.44%（+2.77pp）

### 失败模式 4：冗余循环（Redundant Loops）

**表现**：Agent 卡在某个操作上，反复执行相同的无效动作，无法自我感知「我已经卡住了」。

这是初始版本中**最常见的失败模式**，占初始失败的 43%。

**修复策略：Repetition Warnings（重复预警）**

用 5 步滑动窗口检测三种停滞信号：

| 信号类型 | 检测方式 | 触发条件 |
|---------|---------|---------|
| 思维重复 | 语义等价的规划语句 | 窗口内出现 ≥3 次 |
| 动作重复 | 相同的 pyautogui 指令 | 窗口内出现 ≥3 次 |
| 界面停滞 | 无障碍树结构哈希不变 | 连续 3 步不变 |

触发后：在 prompt 里追加警告，启动「恢复模式」——Agent 被要求尝试替代策略（换工具、走终端、搜索信息）。

**效果**：+2.73pp

---

## 四、整体效果与失败模式迁移

### 消融实验（OSWorld small set）

| 策略 | 成功率 |
|------|--------|
| 基线（无任何增强）| 41.67% |
| + Visual Search | 47.22% |
| + Terminal Execution | 47.19% |
| + Knowledge Support | 44.44% |
| + Repetition Warnings | 44.40% |
| **全部组合** | **52.74%** |

各模块协同效果显著超过单独使用——它们解决的是互补的失败维度。

### 主要结果（OSWorld full set，100 步）

| 模型 | 基线 | +Failure-Case Loop | 提升 |
|------|------|-------------------|------|
| OpenCUA-72B | 42.3% | **48.9%** | +6.6pp (+15.6%) |
| OpenCUA-32B | 较低 | 较高 | +10–12% relative |
| GUI-Owl-32B | 较低 | 较高 | +10–12% relative |

推理开销：仅增加 8%；交互步数：减少 15%。

### 跨基准泛化（直接迁移 OSWorld 挖出的补丁）

| 基准 | 环境类型 | 提升 |
|------|---------|------|
| WebVoyager | Web 交互 | +4.10pp |
| AndroidControl | 移动端 | +7.86pp |
| OmniACT | 桌面任务 | 正向提升 |
| ScreenSpotPro | GUI 定位 | 正向提升 |

OSWorld 挖出的失败模式不是环境特异性的 hack，而是**可迁移的通用错误模式**。

### 失败模式分布变化

4 轮改进后，失败分布发生根本性转变：

| 失败模式 | 改进前 | 改进后 |
|---------|--------|--------|
| 动作死循环 | 43% | 24% |
| 坐标定位错误 | 24% | 缩小 |
| 多步规划不足 | 15% | 28% |
| 任务理解错误 | — | 12% |

**解读**：手笨的问题基本解决了，剩下的瓶颈变成了「脑子」——多步规划和任务理解。这是更高阶的认知问题，意味着框架到了能力边界。

---

## 五、工程落地：在你的 Agent 里复现这套思路

论文没有官方开源代码，但四个核心模块都可以独立实现。下面给出每个模块的参考实现：

### 5.1 失败轨迹收集器

```python
@dataclass
class AgentTrajectory:
    task_id: str
    task_instruction: str
    action_history: list[dict]  # [{"action": ..., "observation": ...}]
    thought_process: list[str]
    final_result: str
    success: bool

class FailureCollector:
    def __init__(self, agent_fn, eval_fn):
        self.agent = agent_fn
        self.eval = eval_fn
        self.failed: list[AgentTrajectory] = []

    def rollout(self, tasks: list) -> tuple[list, list]:
        successes, failures = [], []
        for task in tasks:
            traj = self.agent(task)
            traj.success = self.eval(task, traj)
            (successes if traj.success else failures).append(traj)
        self.failed.extend(failures)
        return successes, failures
```

### 5.2 LLM 诊断器（Claude 4.5）

```python
import anthropic

class FailureDiagnoser:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def diagnose(self, trajectory: AgentTrajectory) -> dict:
        prompt = f"""你是 GUI Agent 失败分析专家。

任务指令：{trajectory.task_instruction}

动作历史（{len(trajectory.action_history)} 步）：
{self._format_actions(trajectory.action_history)}

思考过程：
{chr(10).join(trajectory.thought_process)}

最终结果：{trajectory.final_result}（失败）

请分析：
1. 主要失败模式是哪种？
   - grounding_error（定位错误）
   - competency_gap（能力缺口，不会用终端/工具）
   - knowledge_deficiency（缺少特定知识）
   - redundant_loop（陷入重复动作）
2. 具体失败点在哪里？
3. 推荐的推理时修复方案是什么？

以 JSON 输出。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        return json.loads(response.content[0].text)

    def _format_actions(self, actions: list[dict]) -> str:
        return "\n".join(
            f"Step {i+1}: {a['action']} → {a.get('observation','')[:100]}"
            for i, a in enumerate(actions)
        )
```

### 5.3 Visual Search 模块

```python
from PIL import Image, ImageDraw
import io

def visual_search_verify(
    screenshot: Image.Image,
    click_x: int, click_y: int,
    task_instruction: str,
    action_history: list[dict],
    llm_client,
) -> tuple[int, int]:
    """
    执行点击后自我验证。返回修正后的 (x, y)，无需修正则返回原坐标。
    """
    # 裁剪 400×400 区域
    x0 = max(0, click_x - 200)
    y0 = max(0, click_y - 200)
    x1 = min(screenshot.width, click_x + 200)
    y1 = min(screenshot.height, click_y + 200)
    patch = screenshot.crop((x0, y0, x1, y1))

    # 2× 放大
    patch = patch.resize((patch.width * 2, patch.height * 2), Image.LANCZOS)

    # 标注红圈（相对于放大后的坐标）
    draw = ImageDraw.Draw(patch)
    rel_x = (click_x - x0) * 2
    rel_y = (click_y - y0) * 2
    draw.ellipse(
        (rel_x - 14, rel_y - 14, rel_x + 14, rel_y + 14),
        outline="red", width=2,
    )

    # 编码图像
    buf = io.BytesIO()
    patch.save(buf, format="PNG")
    import base64
    b64 = base64.standard_b64encode(buf.getvalue()).decode()

    # 请 LLM 验证
    response = llm_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": b64},
                },
                {
                    "type": "text",
                    "text": f"""任务：{task_instruction}
红圈标记了点击位置。这个位置是否正确？
如果正确，回复 CONFIRM。
如果不正确，给出修正的绝对坐标（格式：ADJUST x,y）。""",
                },
            ],
        }],
    )

    text = response.content[0].text.strip()
    if text.startswith("ADJUST"):
        parts = text.split()
        new_x, new_y = map(int, parts[1].split(","))
        return new_x, new_y
    return click_x, click_y
```

### 5.4 重复预警模块

```python
from collections import deque
import hashlib

class RepetitionDetector:
    def __init__(self, window=5, threshold=3):
        self.window = window
        self.threshold = threshold
        self.thoughts: deque = deque(maxlen=window)
        self.actions: deque = deque(maxlen=window)
        self.screen_hashes: deque = deque(maxlen=window)

    def update(self, thought: str, action: str, screen_tree: str) -> bool:
        """更新状态，返回 True 表示检测到重复。"""
        self.thoughts.append(thought)
        self.actions.append(action)
        self.screen_hashes.append(
            hashlib.md5(screen_tree.encode()).hexdigest()
        )
        return self._is_stuck()

    def _is_stuck(self) -> bool:
        if len(self.actions) < self.threshold:
            return False
        # 动作重复
        if self.actions.count(self.actions[-1]) >= self.threshold:
            return True
        # 界面停滞
        if len(set(list(self.screen_hashes)[-self.threshold:])) == 1:
            return True
        return False

    def get_recovery_prompt(self) -> str:
        return (
            "警告：你已经重复执行相同操作超过 3 次，或界面停止响应。"
            "请立即改变策略：(1) 尝试用 Ctrl+Alt+T 开终端执行命令；"
            "(2) 用搜索功能查找正确操作方式；"
            "(3) 考虑完全不同的执行路径。"
        )
```

### 5.5 完整 Failure-Case Loop

```python
class FailureCaseLoop:
    def __init__(self, agent, eval_fn, meta_llm_client, k_rounds=4):
        self.collector = FailureCollector(agent, eval_fn)
        self.diagnoser = FailureDiagnoser()
        self.meta_llm = meta_llm_client
        self.k = k_rounds
        self.patches: list[dict] = []   # 累积所有已应用的补丁

    def run(self, tasks: list) -> dict:
        results = []
        for round_num in range(1, self.k + 1):
            print(f"\n=== Round {round_num}/{self.k} ===")

            # 1. 执行并收集失败
            _, failures = self.collector.rollout(tasks)
            print(f"  失败数: {len(failures)}")
            if not failures:
                print("  无失败，提前停止。")
                break

            # 2. 诊断失败模式
            diagnoses = [self.diagnoser.diagnose(f) for f in failures[:10]]  # 取前10
            dominant_mode = self._dominant_failure_mode(diagnoses)
            print(f"  主要失败模式: {dominant_mode}")

            # 3. 生成补丁
            patch = self._generate_patch(failures, dominant_mode)
            self.patches.append(patch)

            # 4. 简单展示补丁（实际工程中需人工验证）
            print(f"  生成补丁: {patch['strategy']}")

        return {
            "patches": self.patches,
            "rounds": round_num,
        }

    def _dominant_failure_mode(self, diagnoses: list[dict]) -> str:
        from collections import Counter
        modes = [d.get("failure_mode", "unknown") for d in diagnoses]
        return Counter(modes).most_common(1)[0][0]

    def _generate_patch(self, failures: list, dominant_mode: str) -> dict:
        failure_summaries = [
            {"task": f.task_instruction, "last_actions": f.action_history[-3:]}
            for f in failures[:5]
        ]
        response = self.meta_llm.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""主要失败模式：{dominant_mode}

失败案例样本：
{failure_summaries}

请生成针对此失败模式的推理时代码补丁（Python 函数或 prompt 增强片段）。
要求：(1) 无需修改模型权重；(2) 在推理时注入；(3) 可与其他补丁并用。
输出 JSON：{{"strategy": ..., "code_patch": ..., "prompt_addition": ...}}""",
            }],
        )
        import json
        return json.loads(response.content[0].text)
```

---

## 六、推荐 GitHub 仓库

### 直接相关

| 仓库 | Stars | 说明 |
|------|-------|------|
| [xlang-ai/OSWorld](https://github.com/xlang-ai/OSWorld) | 3,036⭐ | NeurIPS 2024 基准本体，任何 computer-use 研究的起点 |
| [SunzeY/SEAgent](https://github.com/SunzeY/SEAgent) | 258⭐ | ICML 2026：Self-Evolving Computer Use Agent，同期工作，自主经验学习 |
| [xlang-ai/OSWorld-V2](https://github.com/xlang-ai/OSWorld-V2) | 最新 | OSWorld 2.0：长时程真实任务基准 |

### 工程上手

| 仓库 | Stars | 说明 |
|------|-------|------|
| [Mininglamp-AI/Mano-P](https://github.com/Mininglamp-AI/Mano-P) | 2,450⭐ | OSWorld 榜首（specialized，58.2%），本地 Mac 推理，可作为底座 |
| [xlang-ai/CUA-Gym](https://github.com/xlang-ai/CUA-Gym) | 180⭐ | 可验证 RLVR 训练数据合成管道，配合 Failure-Case Loop 使用 |
| [THUDM/SCALE-CUA](https://github.com/THUDM/SCALE-CUA) | 34⭐ | 开源 computer-use 框架：VeriGen + AgentRL + OSWorld 评测 |

### Follow 路径建议

1. **先跑通基准**：`xlang-ai/OSWorld` → 本地运行环境，了解任务格式和评估协议
2. **找一个基线 Agent**：从 `Mano-P`（本地 Mac）或 `OpenCUA`（如果有 API 访问权限）入手
3. **接入 Failure-Case Loop**：复用上面的 `FailureCollector` + `FailureDiagnoser`，接 Claude Sonnet 4.6 作为元控制器
4. **先实现单个模块**：推荐先做 Repetition Warnings（最简单）→ Visual Search → Terminal Execution
5. **跨基准验证**：把在 OSWorld 挖出的补丁直接迁移到 `AndroidControl` 测试泛化性

---

## 七、对比 HarnessX / NOVA：同族工作的不同切面

本周连续读了三篇「Agent 自进化」论文，它们解决的是同一个大问题的不同子问题：

| 论文 | 进化对象 | 环境 | 代价 |
|------|---------|------|------|
| **本文（Stanford）** | 推理时行为（代码补丁）| GUI/Desktop | 零训练 |
| **HarnessX（Xiaomi）**| Agent 脚手架（prompt/工具/控制流）| 通用 benchmark | 零训练 |
| **NOVA（Tencent）** | 推荐模型架构（代码结构）| 工业推荐系统 | 需要训练 |

三篇论文的共同信念：**包裹 LLM 的那个「框架/脚手架/行为策略」本身应该是可以演化的，不应该手工定死**。

---

*论文来源：arXiv:2606.31270，Stanford + Tsinghua，ECCV 2026，2026-07-26 整理。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Paper**: Learning from Failure: Inference-Time Self-Improvement for Computer-Use Agents
> **arXiv**: 2606.31270 (ECCV 2026)
> **Team**: Xueqiao Sun et al. (Stanford + Tsinghua)
> **Key metrics**: OSWorld 42.3%→48.9% (+15.6% relative), zero training, 8% overhead, 15% fewer steps

---

## 1. The Blind Spot in Standard Training

The current standard for training GUI agents is the success-driven loop:

```
Agent executes tasks → Evaluate → Keep successful trajectories → Fine-tune → Repeat
```

This works — but with a fundamental waste: **all failed trajectories are discarded**.

The Stanford team's core insight: failed trajectories contain the most valuable information about where the model gets stuck, what wrong strategies it tries, and why it can't recover. Rather than being noise, they're a precise diagnostic report.

Can we fix the agent at inference time using these failures, without retraining? Yes.

---

## 2. Failure-Case Loop Architecture

The framework runs iteratively:

1. **Rollout**: Agent executes tasks, collect all trajectories
2. **Diagnose**: Feed failed trajectories to an LLM (Claude 4.5 Sonnet) with task instruction + action history + thought process
3. **Patch**: LLM proposes inference-time solutions (conceptual adjustments + code patches)
4. **Verify**: Light human verification — 97% of LLM proposals accepted without modification
5. **Inject**: Patches injected into agent's inference pipeline
6. **Repeat**: Up to K=4 rounds; each round targets the current dominant failure mode

No model weights are changed. All improvements are inference-time code patches.

---

## 3. Four Failure Modes

### Grounding Errors → Visual Search

After each click/moveto/dragto action:
1. Crop a 400×400 patch centered at the click location
2. Upscale 2× for higher resolution context
3. Draw a red hollow circle (radius 7px) at the click position
4. Feed to the agent for self-verification
5. Agent either confirms or adjusts coordinates

Result: 41.67% → 47.22% (+5.55pp on OSWorld small set)

### Competency Gaps → Terminal Execution

Add to system prompt: "Use Ctrl+Alt+T to open a terminal. Consider this a shortcut for complex tasks."

Result: +5.52pp independently

### Knowledge Deficiencies → Dual Knowledge Support

- **Search engine** (GPT-5-mini): Agent queries mid-step when unfamiliar with domain operations
- **Software manual**: Curated LibreOffice hotkey reference injected at test time

Result: 41.67% → 44.44% (+2.77pp)

### Redundant Loops → Repetition Warnings

5-step sliding window monitors three signals: thought repetition, action repetition, screen-state hash unchanged. Threshold: 3 occurrences. Recovery: prompt encourages switching to terminal or search.

Result: +2.73pp

---

## 4. Results

**All four together**: 41.67% → 52.74% on OSWorld small set.

**Full OSWorld (100 steps)**: 42.3% → 48.9% (+6.6pp, +15.6% relative). Only 8% inference overhead; interaction steps reduced 15%.

**Cross-model**: OpenCUA-32B and GUI-Owl-32B both show +10–12% relative — same recipe, different models.

**Cross-benchmark**: OSWorld-mined patches transfer directly to WebVoyager (+4.10pp), AndroidControl (+7.86pp), without modification.

**Failure mode shift** after 4 rounds: dominant failures changed from "action loops (43%) + grounding errors (24%)" to "multi-step planning (28%) + task misinterpretation (12%)". Low-level mechanics solved; remaining bottlenecks are higher-level cognition.

---

## 5. Recommended Repositories

| Repo | Stars | Purpose |
|------|-------|---------|
| [xlang-ai/OSWorld](https://github.com/xlang-ai/OSWorld) | 3,036⭐ | Benchmark — start here |
| [SunzeY/SEAgent](https://github.com/SunzeY/SEAgent) | 258⭐ | ICML 2026 parallel work: self-evolving agent |
| [Mininglamp-AI/Mano-P](https://github.com/Mininglamp-AI/Mano-P) | 2,450⭐ | #1 OSWorld (specialized), runs locally on Mac |
| [xlang-ai/CUA-Gym](https://github.com/xlang-ai/CUA-Gym) | 180⭐ | Verifiable RLVR data pipeline |

**Follow path**: Run OSWorld locally → pick a base agent (Mano-P) → implement Repetition Warnings first → add Visual Search → run Failure-Case Loop with Claude Sonnet 4.6 as meta-controller → test cross-benchmark transfer.

---

*Source: arXiv:2606.31270, Stanford + Tsinghua. Compiled 2026-07-26. All numbers from the paper.*

© 2026 Author: Mycelium Protocol
