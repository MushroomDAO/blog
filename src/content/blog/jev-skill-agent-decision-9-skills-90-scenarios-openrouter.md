---
title: "jev-skill：给 Agent 装上 Jev 决策感知，9 个可安装 Skill 覆盖分诊/路由/代码审查"
titleEn: "jev-skill: Plug Jev Decision Intelligence into Your Agent — 9 Installable Skills, 90 Scenarios"
description: "MIT，34 stars，今天刚开源。SKILL.md 格式，9 个专域 Skill 覆盖 90 个标注场景：分诊、文档证据、UI 操控、工具路由、代码审查等。需 OpenRouter API key 调 TypeSafe Jev，无本地权重。显式禁止无 key 时静默降级，只能做 agent simulation 且必须标注。"
descriptionEn: "MIT, 34 stars, open-sourced today. SKILL.md format, 9 domain-specific skills covering 90 labeled scenarios: triage, document evidence, UI actions, tool routing, code review, and more. Requires OpenRouter API key for TypeSafe Jev — no local weights. Explicitly forbids silent fallback when the key is absent."
pubDate: 2026-09-20
heroImage: "../../assets/images/jev-skill-agent-decision-9-skills-90-scenarios-openrouter-banner.jpg"
category: "Tech-Experiment"
tags: ["agent-skills", "jev", "decision-model", "routing", "claude-code", "open-source"]
lang: zh-CN
---

[jev-skill](https://github.com/wuyoscar/jev-skill) 是一个 SKILL.md 格式的 Agent Skill 集合，今天刚开源（2026-09-20），把 TypeSafe 的 Jev 决策 API 打包成 9 个可安装的场景专用 Skill，覆盖 90 个标注决策场景，14 条真实 API I/O 示例。目标场景：Claude Code、Codex、OpenCode 等 Agent 系统。

**仓库**：github.com/wuyoscar/jev-skill | **License**：MIT | **Stars**：34

---

## 为什么要给 Agent 接 Jev

普通 LLM 做分类/打分/路由时，结果是生成出来的——答案随 prompt 微小变化而漂移，置信度来自自评而非校准概率。Jev 是 TypeSafe 专门训练的决策模型，输出是校准过的概率分布，不生成自由文本。

jev-skill 的作用：把这个能力封装成 Agent 随时可调用的 Skill——Agent 不需要自己判断"这条消息紧不紧急"、"现在该调哪个工具"，转而调 Jev 拿一个有置信度数字的结论。

---

## 9 个 Skill 对应 90 个场景

| Skill | 典型用途 |
|-------|----------|
| `jev` | 通用自定义决策检查点 |
| `jev-triage` | 消息/反馈分类、紧急程度评级 |
| `jev-documents` | 证据片段选取、论点支持/反驳判定 |
| `jev-ui` | 浏览器/桌面下一步操作决策 |
| `jev-route` | 工具/模型/专家路由 |
| `jev-context` | 上下文相关性评分、何时压缩上下文 |
| `jev-code-review` | 代码变更优先级排序 |
| `jev-find-code` | 仓库导航、定位目标文件 |
| `jev-simulation` | 模拟世界中的法律动作选择 |

---

## 三种决策类型

Jev 的输入是结构化 JSON，输出三种格式：

**Choice**：从候选列表中选一个
```json
{
  "state": "上下文描述",
  "questions": {
    "next_step": {
      "type": "choice",
      "instructions": "Agent 下一步应该做什么？",
      "criteria": {
        "inspect_input": "查看输入数据",
        "retry_call": "重试 API 调用",
        "escalate": "转人工"
      }
    }
  }
}
```

**Noul**：独立是/否，返回校准概率
```json
// 输出示例（来自真实 API 调用）：
// stuck = true, P = 0.88
// → "Agent 有 88% 概率陷入循环，建议检查输入"
```

**Score**：按评分量表返回档位 + 期望值
```json
// urgency = 1.29/2（0~2 三档：低/中/高）
```

---

## 安装方式

把这条 prompt 贴进 Claude Code：

```
Install Jev Skills for my current agent, including the general skill and all 
scenario skills. Read and follow this installation guide, then verify the 
installation: https://raw.githubusercontent.com/wuyoscar/jev-skill/main/docs/install.md
```

Agent 会自动读取安装指引、写入 Skill 文件、离线验证。**不需要 npm / Node.js / Vercel**。

需要设置环境变量：

```bash
export OPENROUTER_API_KEY="sk-or-..."  # TypeSafe Jev 通过 OpenRouter 调用
```

命令行直接调用：

```bash
jev-decide --state "用户报告支付失败" \
           --question "urgency" \
           --type score
```

---

## 没有 API Key 时的处理规则

这一点值得专门说：jev-skill 明确规定，若 `OPENROUTER_API_KEY` 缺失，Agent **禁止静默降级**。只有两个合法路径：

- **A**：提示用户获取 OpenRouter key，等拿到再调真实 Jev
- **B**：用宿主 Agent 模拟决策，但必须在输出中标注 `mode: agent_simulation` 和 `jev_called: false`

"悄悄用 GPT 代替 Jev 然后假装是 Jev 的结果"——这条被明确禁止。校准概率是 Jev 的核心价值，用模拟结果冒充会破坏 Agent 对置信度数字的信任。

---

## 14 条真实 API 记录

仓库包含 14 条真实 Jev API 调用的 I/O 记录，来自合成示例（非作者自己的 Agent 轨迹）。几个有代表性的：

| 场景 | 问题 | Jev 输出 |
|------|------|----------|
| Agent 循环检测 | 是否陷入循环？ | `stuck=true`, P=0.88 |
| 客服工单路由 | 归类为哪个队列？ | `queue=bug`, urgency=1.29/2 |
| 文档核查 | 哪条来源支持这个论点？ | `source=s2`, P=0.97, `claim_support=contradicted` |

---

## 不足之处

**1. 需要付费 API**：Jev 通过 OpenRouter 调用，没有本地权重可下载。与 Kev（jaredpalmer/kev）是两个不同项目——Kev 是本地开源 LoRA，jev-skill 是 TypeSafe 商业 Jev 的 Agent 接入层。

**2. "Jevify" 适配器校准待验证**：仓库提到 Jevify（用其他模型适配 Jev 接口）明确标注为"API 兼容性≠等价校准"，社区对此的基准测试被标记为未核实。

**3. 仓库极新**：今天刚开源，34 stars，社区验证极少。

**4. Jev 不生成文字**：它只做分类/打分/路由。开放式规划、文本生成、工具执行仍然由宿主 Agent 完成；Jev 只负责"要不要做"和"做哪个"这类判断。

**5. 无会话记忆**：每次 Jev 调用都是独立的，不跟踪调用间的状态。

---

## 怎么看这件事

jev-skill 做的事情很具体：把一个需要自己写 prompt 工程才能接进去的决策 API，包装成 Agent 可以直接 import 的 Skill。9 个场景覆盖了 Agent 系统里最常见的几类判断需求——什么时候升级、调哪个工具、这段代码改动有多紧急。

价值在于标准化，而不是新功能：这些决策 Agent 本来也会做，只是现在有了一套带置信度的一致接口，而且明确区分了"真 Jev 的概率"和"Agent 自己猜的概率"。

今天刚开源，观望一段时间再决定是否接入。

> 开源代码与 Skill 仅供学习研究。调用真实 Jev API 会产生 OpenRouter 费用，请查看 TypeSafe 定价。

---

<!--EN-->

## jev-skill: Plug Jev Decision Intelligence into Your Agent

[jev-skill](https://github.com/wuyoscar/jev-skill) is a SKILL.md-format agent skill collection, open-sourced today (2026-09-20). It wraps TypeSafe's Jev decision API into 9 domain-specific installable skills covering 90 labeled decision scenarios and 14 real API I/O examples. Works with Claude Code, Codex, and OpenCode.

**Repo**: github.com/wuyoscar/jev-skill | **License**: MIT | **Stars**: 34

---

### Why Jev for Agent Decisions

Standard LLMs doing classification/scoring/routing produce outputs that drift with prompt phrasing, and their "confidence" is self-reported, not calibrated. Jev is TypeSafe's purpose-trained decision model that outputs calibrated probability distributions without free-text generation. jev-skill packages this into skills agents can call directly — instead of asking itself "how urgent is this ticket?", the agent calls Jev and gets a number it can act on.

---

### 9 Skills, 90 Scenarios

| Skill | Purpose |
|-------|---------|
| `jev` | Custom decision checkpoints |
| `jev-triage` | Message classification, urgency scoring |
| `jev-documents` | Evidence span selection, claim support/contradiction |
| `jev-ui` | Browser/desktop next-action decisions |
| `jev-route` | Tool/model/specialist routing |
| `jev-context` | Context relevance, when to compact |
| `jev-code-review` | Code change prioritization |
| `jev-find-code` | Repository navigation |
| `jev-simulation` | Legal action choices in simulated worlds |

---

### Three Output Types

- **Choice**: pick from a defined candidate list
- **Noul**: calibrated yes/no probability (`stuck=true, P=0.88`)
- **Score**: graded level with expected value (`urgency=1.29/2`)

---

### Installation

Paste this prompt into Claude Code:

```
Install Jev Skills for my current agent, including the general skill and all 
scenario skills. Read and follow this installation guide, then verify the 
installation: https://raw.githubusercontent.com/wuyoscar/jev-skill/main/docs/install.md
```

No npm, Node.js, or Vercel required. Set `OPENROUTER_API_KEY` to call real Jev.

---

### The No-Key Rule

When `OPENROUTER_API_KEY` is absent, the agent is **forbidden from silent fallback**. Only two legal paths: (A) prompt the user to get a key, or (B) simulate with the host agent but explicitly label the output `mode: agent_simulation, jev_called: false`. Pretending a regular LLM result is a Jev calibrated probability is explicitly prohibited — it breaks the trust premise of the whole setup.

---

### Limitations

1. **Paid API required** — Jev via OpenRouter, no open weights available locally. This is unrelated to `jaredpalmer/kev`, which is a separate open-source local LoRA model.
2. **"Jevify" adapters**: API compatibility doesn't equal calibration equivalence. Community benchmarks for this are flagged as unverified.
3. **Repo is brand new** — 34 stars, minimal community validation.
4. **Jev doesn't generate text** — it only classifies, scores, and routes. Planning and execution stay with the host agent.
5. **No session memory** — each Jev call is stateless.

---

### Bottom Line

jev-skill standardizes the interface between agent systems and calibrated decision outputs. The value is in providing a consistent, labeled boundary between "what Jev says with a probability" and "what the agent guessed" — including the explicit rule that you can't blur that line when the API key is absent. Very new repo; worth watching before integrating.

> Skills for research and learning only. Real Jev API calls via OpenRouter incur charges — check TypeSafe pricing before deploying.
