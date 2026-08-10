---
title: "PenguinHarness：用 4 个 Skill 把 Agent 调优变成有版本、有固定考题、有分数记录的实验闭环"
titleEn: "penguin-harness-self-evolving-agent-builder-skills-benchmark"
description: "Prism-Shadow/penguin-harness，1140 stars，Apache-2.0，TypeScript。LlamaFactory 作者 Yaowei Zheng 的新项目，2026-07-19 开源。全自动 Agent 构建平台：一句话让 Agent 构建 Agent 应用（DeepSeek V4 Pro 跑一个 RAG 应用花费 $0.02），数据分析准确率最高、成本是 Claude Code 的 1/70。核心亮点是 Agent Tuning 四 Skill 闭环：agent-creation → benchmark-design → agent-evaluation → agent-optimization，每轮改进前自动快照，严格高于基线才接受，否则回滚。支持 DeepSeek/Kimi/GLM/Claude/Gemini，桌面端+CLI+SDK 三种运行方式。"
descriptionEn: "Prism-Shadow/penguin-harness, 1140 stars, Apache-2.0, TypeScript. A new project by LlamaFactory author Yaowei Zheng, open-sourced 2026-07-19. Automated agent builder platform: one sentence builds a complete agent app ($0.02 on DeepSeek V4 Pro for a full RAG app), top accuracy on data analysis at 1/70 Claude Code's cost. The standout feature is the 4-skill Agent Tuning loop: agent-creation → benchmark-design → agent-evaluation → agent-optimization, with automatic snapshots before each improvement round, strict-improvement acceptance, and rollback if scores don't improve. Supports DeepSeek/Kimi/GLM/Claude/Gemini. Runs as desktop app, CLI, or SDK."
pubDate: "2026-08-10"
updatedDate: "2026-08-10"
category: "Tech-News"
tags: ["AI Agent", "自进化", "harness", "开源", "TypeScript", "benchmark", "技能库", "Mycelium"]
heroImage: "../../assets/images/penguin-harness-self-evolving-agent-builder-skills-benchmark-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

Agent 自进化是 2026 年开源社区里出现频率越来越高的一条线。PenguinHarness 是这个方向里值得仔细看的一个项目：它没有造新概念，而是把「让 Agent 跑 benchmark、分析失分点、修改自身配置、验证改进」这件事工程化了——用 4 个 Skill，把流程锁死在一个有版本、有固定考题、有分数记录、能失败回滚的实验闭环里。

GitHub: https://github.com/Prism-Shadow/penguin-harness | ⭐ 1,140 | Apache-2.0 | TypeScript | 2026-07-19

作者是 LlamaFactory 的作者 Yaowei Zheng（GitHub: hiyouga）和 PrismShadow AI Team，用 Fable 5 辅助构建。

---

## 三个定位

README 开头有一句对比：

> 使用 LangChain，以 1 倍速度人工构建 Agent；使用 PenguinHarness，以 100 倍速度用 Agent 构建 Agent。

这句话背后是三个递进的主张：

**第一：成本和效果**

刻意精简的工具集 + 干净的底层接口，减少工具调用和 token 消耗，对开放模型（尤其是 DeepSeek）深度适配。官方 benchmark 数据：数据分析题库准确率最高，成本是 Claude Code 的 1/70。

**第二：一句话构建 Agent 应用**

给一个任务描述，Agent 直接输出完整应用——脚手架、代码、运行说明。官方示例是构建一个 Claude Code 文档 RAG 问答应用，引用可点击直达原文，花费 $0.02（使用 DeepSeek V4 Pro）。

**第三：自进化**

这是本文的重点。借助 Agent Tuning 四个 Skill，Agent 自己评估自己、优化自己——每轮改进之前自动打快照，只有分数严格提升才接受新版本，否则回滚。

---

## 整体架构

PenguinHarness 的数据根目录是 `~/.penguin/data`。桌面端和 CLI 安装共享同一个数据目录，可以混用。

**三种运行方式：**

| 方式 | 命令 | 特点 |
|------|------|------|
| 桌面端应用 | 双击安装，打开即登录 | macOS/Windows/Linux，无需终端 |
| CLI + Web | `penguin web` → http://127.0.0.1:7364 | 多会话对话、轨迹观测、评估中心 |
| SDK | `@prismshadow/penguin-core` | TypeScript/Node，可被 Agent 程序化驱动 |

**内置 Skill 库（4 组）：**

| 分组 | Skill |
|------|-------|
| 办公效率 | `data-analysis`、`firecrawl`、`bento-slides` |
| 软件开发 | `web-design`、`software-engineering` |
| AI 应用开发 | `penguin-sdk`、`penguin-cli`、`agenthub-models`、`vllm`、`ollama`、`llamafactory` |
| **Agent 调优** | **`agent-creation`、`benchmark-design`、`agent-evaluation`、`agent-optimization`** |

**支持的模型：**

DeepSeek V4、Kimi K3、GLM 5.2、Hunyuan 3、Qwen 3.8 Max、GPT 5.6、Gemini 3.6 Flash、Claude 5、Inkling——以及任何 OpenAI 协议兼容端点。

---

## Skill 系统的设计

理解自进化机制之前，需要先理解 Skill 在 PenguinHarness 里是什么。

Skill 是一个目录，里面有一个 `SKILL.md` 文件。目录名是 Skill 的唯一标识符。系统提示只注入每个 Skill 的元数据（名称 + 描述），Agent 在需要时自己用 shell 命令读取完整的 `SKILL.md` 正文——没有专用工具，读文件就是一次普通的 `read_file` 调用。

```
---
name: my-skill
description: One-line English description injected into the system prompt.
version: 1
updated: 2026-07-17
---

# My Skill

具体的步骤、边界和验收条件...
```

这个设计有一个关键结论：**Skill 文件可以被 Agent 本身改写**。Skill 的内容在磁盘上，没有缓存，每次读取都直接走磁盘。这让「Agent 修改自己的 Skill、然后在下一轮中按新 Skill 行动」变得可能，也是整个自进化闭环的基础。

---

## 自进化：4 个 Skill 的分工

自进化涉及两个独立的顶层 Session，以及若干由 `run_subagent` 派生的叶子 Session：

| 角色 | 职责 |
|------|------|
| Builder（顶层） | 先执行 `agent-creation`，再执行 `benchmark-design` |
| Target Agent | 被改进的 Agent；只在隔离 Workspace 里跑评估任务 |
| Evaluator（叶子） | 通过 `run_subagent` 创建；运行并私密打分一条 Benchmark Case |
| Optimizer（顶层） | 独立开一个新 Session，执行 `agent-optimization` |

### Session 1：建 Agent + 建 Benchmark

**`agent-creation`**：根据用户需求写 `AGENTS.md`（身份、指令、能力边界），安装所需 Skill。

**`benchmark-design`**：设计多 Case 的 Benchmark。每个 Case 包含两个部分：
- `statement/`：任务说明，Target Agent 看到的输入
- `rubric/`：私密评分标准，**Target Agent 永远看不到**

两者物理隔离是刻意的：如果 Agent 能看到评分标准，它会直接针对标准优化，而不是真正提升能力。

Builder 在每个 Case 首次派发前，检查任务说明的内部一致性、评分标准与任务说明是否匹配。Pilot 迭代完成后，Benchmark 冻结（Freeze），选出最低分有效版本作为 Formal Baseline，记入 `scoreboard.yaml`。

### Session 2：优化

**`agent-optimization`**（Optimizer 执行）：

1. 通过 `run_subagent` 并行派发 Evaluators，覆盖 Case × runs 矩阵
2. 根据分数和 Trace 提出一个候选改动（Candidate）
3. 编辑 Target Agent 的可编辑状态：`AGENTS.md`、Skills、config → 生成 N+1 版
4. 只有 Candidate 的评分**严格高于** Formal Baseline 才接受；否则回滚
5. 达到目标分数则提前停止；否则完成配置的轮次，保留最高分

**每轮改进前**：Agent State 打包进 `snapshots/v<version>.tar.gz`（Vault 里的密钥不进快照），`system_config.yaml` 里的 `version` 在成功优化后递增。Web UI 支持导出和导入快照。

---

## Benchmark 的存储结构

```
benchmarks/<id>/
├── benchmark_config.toml    # Benchmark 配置（Builder 的 runs 固定为 1）
├── <case-id>/
│   ├── statement/           # 任务说明，Target Agent 可见
│   └── rubric/              # 评分标准，与 Target Agent 物理隔离
└── scoreboard.yaml          # 所有评估记录，带时间戳
```

`scoreboard.yaml` 里的每条记录包含：
- 评估时的 `(provider, model_id)` 和 `thinking_level`
- `summary_title` 和 `summary`（本轮结论 + 下一轮假设）
- 分数、成本、时长的平均值
- 每个 Case 每次 Run 的 `score`、`cost`、`duration_ms`、`session_id`

`session_id` 是关键：每次 Evaluator 运行都是一个有完整 Trace 的普通 Session，Scoreboard 通过 `session_id` 链接回去，每个数字都可以追溯到生成它的那次运行。

---

## 为什么这个设计值得关注

Agent 自进化的话题很多，但大多数停在「Agent 能反思和调整」这个层级。PenguinHarness 的自进化做了几件更具体的事：

**固定考题**：Benchmark 一旦 Freeze 就不能改，这保证了不同轮次的分数可以比较。如果每轮改进都同时改考题，「分数提升」就失去了意义。

**私密评分标准**：Target Agent 在任务执行时看不到 rubric，这防止了针对标准的过拟合。

**严格改进才接受**：第一次比较直接用 Candidate 的多轮平均分对比 Formal Baseline 的单轮分（不回填 Baseline），是一个保守但清晰的接受条件。

**快照 + 回滚**：每轮改进前打快照，失败就回滚，这让实验过程是可逆的。

**Skill 可被 Agent 改写**：Optimizer 可以直接编辑 Target Agent 的 Skills，而下一轮评估就会用到修改后的 Skills。这个闭环不需要任何框架特殊支持——就是文件读写。

---

## 快速上手

**安装（macOS/Linux）：**
```bash
curl -fsSL https://penguin.ooo/install.sh | sh
penguin web   # 打开 http://127.0.0.1:7364
```

**或者 npm：**
```bash
npm install -g @prismshadow/penguin-cli
penguin web
```

**SDK（TypeScript）：**
```ts
import { createAgent, isCompleteModelMessage, userText } from "@prismshadow/penguin-core";

const agent = await createAgent({ agentId: "default_agent" });
const session = await agent.createSession({ workspaceDir: process.cwd() });

for await (const output of session.run([userText("Create hello.txt containing hi")], {
  approve: async () => "allow",
})) {
  if (isCompleteModelMessage(output) && output.payload.type === "text") {
    console.log(output.payload.text);
  }
}
```

桌面端从 https://penguin.ooo/download 下载；macOS 需要执行一次 `sudo xattr -rd com.apple.quarantine` 解除隔离标记。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## PenguinHarness: Agent Self-Improvement with a 4-Skill Closed Loop — Versioned, Fixed Benchmark, Scored, Rollback-Capable

*by Mycelium Protocol*

---

Agent self-improvement has become an increasingly prominent thread in the 2026 open-source community. PenguinHarness is worth a closer look: it doesn't invent a new concept, but engineers something concrete — making "run a benchmark, analyze missed points, edit agent configuration, verify the improvement" into a closed loop with versions, fixed test cases, score records, and rollback on failure. Four skills. The whole thing is locked down.

GitHub: https://github.com/Prism-Shadow/penguin-harness | ⭐ 1,140 | Apache-2.0 | TypeScript | 2026-07-19

Author: Yaowei Zheng (creator of LlamaFactory, GitHub: hiyouga) and the PrismShadow AI Team, built with Fable 5.

---

### Three Positions

The README opens with:

> With LangChain, you build agents by hand — at 1× speed.  
> With PenguinHarness, agents build agents — at 100×.

Three progressive claims behind that line:

**1. Cost and accuracy**

Deliberately minimal toolset over clean low-level interfaces — fewer tool calls, fewer tokens, tuned for open models like DeepSeek. Official benchmark: top accuracy on data-analysis tasks at 1/70 of Claude Code's cost.

**2. One sentence → a full agent application**

Give a task description; the agent produces a complete application — scaffold, code, run instructions. The official demo: a Claude Code documentation RAG app with clickable citations, for $0.02 on DeepSeek V4 Pro.

**3. Self-evolution**

The focus of this article. Four Agent Tuning skills form a self-improvement loop. Automatic snapshot before each round. Strict improvement required to accept a new version. Rollback otherwise.

---

### Architecture

PenguinHarness's data root is `~/.penguin/data`. Desktop and CLI installs share the same root and can be mixed freely.

**Three run modes:**

| Mode | How | Notes |
|------|-----|-------|
| Desktop app | Double-click install | macOS/Windows/Linux, no terminal needed |
| CLI + Web | `penguin web` → http://127.0.0.1:7364 | Multi-session chat, trace viewer, evaluation center |
| SDK | `@prismshadow/penguin-core` | TypeScript/Node, scriptable by agents |

**Built-in Skill library (4 groups):**

| Group | Skills |
|-------|--------|
| Office Productivity | `data-analysis`, `firecrawl`, `bento-slides` |
| Software Development | `web-design`, `software-engineering` |
| AI App Development | `penguin-sdk`, `penguin-cli`, `agenthub-models`, `vllm`, `ollama`, `llamafactory` |
| **Agent Tuning** | **`agent-creation`, `benchmark-design`, `agent-evaluation`, `agent-optimization`** |

**Supported models:**

DeepSeek V4, Kimi K3, GLM 5.2, Hunyuan 3, Qwen 3.8 Max, GPT 5.6, Gemini 3.6 Flash, Claude 5, Inkling — plus any OpenAI-protocol-compatible endpoint.

---

### The Skill System

To understand the self-improvement mechanism, you need to understand what a Skill is.

A Skill is a directory containing a `SKILL.md` file. The directory name is the authoritative identifier. The system prompt injects only each installed Skill's metadata (name + description); the agent reads the full body when it needs it via an ordinary shell `read_file` call — no dedicated tool.

```
---
name: my-skill
description: One-line English description injected into the system prompt.
version: 1
updated: 2026-07-17
---
# My Skill

Concrete steps, boundaries, acceptance criteria...
```

The critical implication: **Skill files can be rewritten by the agent itself**. Skill content lives on disk with no cache; every read goes straight to disk. This makes "agent edits its own Skill, then acts on the new Skill in the next round" possible — it's the foundation of the self-improvement loop.

---

### Self-Evolution: 4-Skill Division of Labor

Self-improvement runs across two independent top-level Sessions, plus leaf Sessions created via `run_subagent`:

| Role | Responsibility |
|------|----------------|
| Builder (top-level) | Runs `agent-creation` then `benchmark-design` |
| Target Agent | The agent being improved; runs eval tasks only, in isolated Workspaces |
| Evaluator (leaf) | Created via `run_subagent`; runs and privately scores one Case |
| Optimizer (top-level) | Opens a new Session; runs `agent-optimization` |

**Session 1: Build Agent + Build Benchmark**

`agent-creation`: writes `AGENTS.md` (identity, instructions, capability scope), installs needed Skills.

`benchmark-design`: designs a multi-Case Benchmark. Each Case has two parts:
- `statement/`: the task given to the Target Agent
- `rubric/`: the private scoring criteria — **the Target Agent never sees this**

Physical separation of statement and rubric is deliberate: an agent that can see the scoring criteria will optimize against the criteria, not actually improve its capability.

The Builder checks internal coherence of each Case before dispatch. After Pilot iterations complete, the Benchmark is frozen. The lowest-scoring valid revision becomes the Formal Baseline, recorded in `scoreboard.yaml`.

**Session 2: Optimize**

`agent-optimization` (run by the Optimizer):

1. Dispatches Evaluators in parallel via `run_subagent`, covering the Case × runs matrix
2. Uses scores and Traces to propose one bounded Candidate change
3. Edits the Target Agent's state: `AGENTS.md`, Skills, config → produces version N+1
4. Accepts the Candidate only when its score **strictly improves** over the Formal Baseline; otherwise rolls back
5. Stops early when the target score is reached; otherwise completes configured rounds, keeps the highest-scoring result

**Before each round**: the Agent State is packed into `snapshots/v<version>.tar.gz` (Vault secrets are excluded). `version` in `system_config.yaml` increments on successful optimization. The Web UI supports exporting and importing snapshots.

---

### Benchmark Storage Layout

```
benchmarks/<id>/
├── benchmark_config.toml    # Benchmark config (Builder runs fixed at 1)
├── <case-id>/
│   ├── statement/           # Task given to the Target Agent
│   └── rubric/              # Private rubric, isolated from Target Agent
└── scoreboard.yaml          # Timestamped evaluation records
```

Each record in `scoreboard.yaml` includes: evaluation `(provider, model_id)` and `thinking_level`, `summary_title` and `summary` (round conclusion and hypothesis for next round), score/cost/duration averages, and per-Run `score`, `cost`, `duration_ms`, `session_id`.

The `session_id` is the key: every Evaluator run is an ordinary Session with a full Trace. Every number can be traced back to the run that produced it.

---

### Why This Design Is Worth Attention

Agent self-improvement is widely discussed, but most proposals stay at "the agent can reflect and adjust." PenguinHarness does several more concrete things:

**Fixed benchmark**: once frozen, the Benchmark doesn't change. This makes scores from different rounds comparable. If the benchmark changes with every improvement round, "score improvement" loses meaning.

**Private rubric**: the Target Agent never sees the scoring criteria during task execution, preventing optimization against the rubric rather than genuine capability improvement.

**Strict improvement to accept**: the first comparison uses the Candidate's multi-run average against the Formal Baseline's single-run score (no backfilling the Baseline) — conservative, but unambiguous.

**Snapshot + rollback**: a snapshot before every round means the process is reversible. A failed improvement doesn't leave the agent in a degraded state.

**Skill files are editable**: the Optimizer can directly edit the Target Agent's Skills, and the next evaluation round uses the modified Skills. This loop needs no special framework support — it's just file writes.

---

### Quick Start

**Install (macOS/Linux):**
```bash
curl -fsSL https://penguin.ooo/install.sh | sh
penguin web   # opens http://127.0.0.1:7364
```

**Or npm (Node >= 24):**
```bash
npm install -g @prismshadow/penguin-cli
penguin web
```

**TypeScript SDK:**
```ts
import { createAgent, isCompleteModelMessage, userText } from "@prismshadow/penguin-core";

const agent = await createAgent({ agentId: "default_agent" });
const session = await agent.createSession({ workspaceDir: process.cwd() });

for await (const output of session.run([userText("Create hello.txt containing hi")], {
  approve: async () => "allow",
})) {
  if (isCompleteModelMessage(output) && output.payload.type === "text") {
    console.log(output.payload.text);
  }
}
```

Desktop download: https://penguin.ooo/download — macOS users run `sudo xattr -rd com.apple.quarantine /Applications/PenguinHarness.app` once to clear the quarantine flag.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
