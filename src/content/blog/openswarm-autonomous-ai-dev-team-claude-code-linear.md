---
title: 'OpenSwarm：把 Claude Code + Codex 组成自主开发团队，从 Linear issue 到 PR 全自动'
titleEn: "OpenSwarm: Assemble Claude Code + Codex into an Autonomous Dev Team, Linear Issue to PR Fully Automated"
description: "MIT 开源的 AI 开发团队编排器：从 Linear 拾取任务，Worker/Reviewer 对儿流水线，LanceDB 每仓库认知记忆，PR 自动驾驶，CI merge gate，SWE-bench Lite Hybrid 模式 3/3 解决。856 stars，TypeScript。"
descriptionEn: "MIT-licensed AI dev team orchestrator: picks tasks from Linear, runs Worker/Reviewer pair pipelines, LanceDB per-repo cognitive memory, PR autopilot, CI merge gate, SWE-bench Lite Hybrid mode 3/3 resolved. 856 stars, TypeScript."
pubDate: "2026-09-13"
updatedDate: "2026-09-13"
category: "Tech-News"
tags: ["AI-agent", "open-source", "Claude-Code", "multi-agent", "developer-tools", "Linear", "autonomous-coding"]
heroImage: "../../assets/openswarm-autonomous-ai-dev-team-claude-code-linear-banner.jpg"
---

> 📌 开源仓库：Intrect-io/OpenSwarm
> GitHub：https://github.com/Intrect-io/OpenSwarm
> NPM：@intrect/openswarm
> License：MIT | Stars：856

---

Claude Code、Codex、OpenRouter 上的任意模型——你手里已经有了好几把锤子，但每次要处理 Linear 上积压的 issue 时，还是得一个个手动交给 AI，等结果，review，再提 PR。

OpenSwarm 想自动化这个循环：从 issue tracker 拾取任务，分配给 Worker，用 Reviewer 验证结果，通过 Discord/Slack 上报进度，用 LanceDB 记住每个仓库的踩坑历史——下次遇到类似任务，直接召回。

---

## 一、核心流水线：Worker + Reviewer 对儿

OpenSwarm 的基本工作单元是一对 Agent：

- **Worker**：执行任务，写代码，跑测试
- **Reviewer**：检查 Worker 的输出，判断是否通过

这个 pair 架构的实际意义在于 **Hybrid 模式**：

> 前沿模型（只读）诊断问题 → 轻量模型执行修复 → 验证循环确认结果

SWE-bench Lite 的数据是：Hybrid 模式解决了 3 个实例，这 3 个实例是所有轻量模型单独跑都解决不了的——换句话说，诊断能力用对地方，可以用便宜模型完成前沿模型才能完成的任务，成本只有纯前沿方案的一小部分。

---

## 二、Worker 支持什么模型

Worker 不绑定单一模型，目前支持：

- **Codex / GPT**：ChatGPT OAuth 登录，走 Codex 或 GPT 系列
- **OpenRouter**：任意模型，API key 或 OAuth，覆盖几乎所有主流和开源模型
- **本地模型**：Ollama / LM Studio，不需要账号
- **Claude Code**（`claude -p`）：opt-in 后备，走 Claude Code CLI
- **Atlas Cloud**：内置 `atlascloud` adapter，OpenAI 兼容接口

`openswarm provider` 命令可以随时切换，正在运行的 daemon 也支持热切换，不用重启。

---

## 三、任务从哪来：Linear 或本地 SQLite

OpenSwarm 有两个任务来源，`openswarm init` 向导二选一：

**Linear**：OAuth 登录，选团队和项目，issue 自动同步。Linear 的标签、优先级、指派信息全部带过来。

**本地 SQLite**：不需要 Linear 账号，内置 issue tracker，适合个人项目或不想接第三方服务的场景。

两种模式的工作流一致——OpenSwarm 内部统一抽象，切换数据源不影响其他功能。

---

## 四、openswarm review：CI merge gate

`openswarm review` 是这个工具里设计最完整的功能。

**基本用法**：审查当前 working-tree 的改动。

**`--max` 模式**：全库审计——把 Reviewer 子 Agent 扇出到各代码区域并行跑，汇总报告，生成 Linear issue（最多 10 个，带主子关系），输出到 `.openswarm/audit/`。

**`--max --fix` 模式**：审计完成后，把独立可修复的发现分组，在隔离沙盒里跑修复，每个区域都通过 re-review 和确定性验证后，才提 PR。

```bash
openswarm review          # 审查 diff
openswarm review --max    # 全库审计 + Linear issues
openswarm review --max --fix  # 审计 + 修 + PR
```

作为 CI merge gate 的退出码设计：
- `0`：通过（或没东西可审）
- `1`：gate 跑了，有 reject
- `2`：gate 没跑（配额耗尽、provider 错误等）——永远不应该算通过

GitHub Actions composite action 已内置，直接 `uses: unohee/OpenSwarm@main`，输出 `decision`、`gate-ran`、`sarif-file`。

---

## 五、openswarm pr：PR 自动驾驶

```bash
openswarm pr status        # 快照：冲突 / CI / review 意见
openswarm pr fix           # 一次性修当前分支的 open PR
openswarm pr review        # 重新应用 reviewer 反馈
openswarm pr review --fresh  # 对 PR diff 跑新的 code review 并发评论
openswarm pr review --all    # 审查仓库所有 open PR
openswarm pr watch         # 循环修直到 merge-ready（默认 5 轮）
openswarm pr create        # 本地修 → commit → push → gh pr create
```

`openswarm pr watch` 是"扔进去等"模式：设定目标（merge-ready），OpenSwarm 循环执行 fix → re-review → verify，直到通过或轮次耗尽，中途通过 Discord/Slack 上报进度。

---

## 六、LanceDB 认知记忆：仓库级学习

每个 Worker 跑完任务后，结果会写入该仓库的 LanceDB 知识库。下次有类似任务时，这些历史结果会被召回注入 prompt。

这不是全局记忆，而是**仓库级别的专属知识积累**：A 项目踩的坑不会污染 B 项目，但 A 项目自己的经验会越来越丰富。随着任务数量增加，Worker 处理该仓库的效果理论上会持续提升。

---

## 七、沙盒：Linux 上的 bubblewrap

验证步骤跑在沙盒里，失败关闭（fail closed）——无法沙盒化就拒绝运行，不会静默降级成明文执行。

Linux 环境需要装 bubblewrap：

```bash
sudo apt-get install -y bubblewrap
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
# GitHub Actions ubuntu-latest 需要这两步，否则 bwrap 会报 Permission denied
```

macOS 用平台沙盒，不需要额外配置。

---

## 快速开始

```bash
npm install -g @intrect/openswarm

# 交互式向导：provider 认证 + Linear OAuth + 写 config.yaml
openswarm init

# 环境诊断
openswarm doctor

# 启动 TUI
openswarm
```

TUI 有 Chat / Projects / Tasks / Stuck / Issues / Logs 六个标签，状态栏实时显示当前 provider、模型、消息数、累计成本。

---

## 拆解结论

OpenSwarm 做的事是：把"给 AI 分配编程任务"这件原来需要人全程盯着的事，拆成可以自动化的流水线——任务从 Linear 来，Worker 跑，Reviewer 验，进度上 Discord，历史存 LanceDB，PR 自动跑 CI gate。

856 stars，TypeScript，MIT 开源。Hybrid 模式的设计（只读诊断 + 轻量实现）是个值得关注的工程思路——用对模型的地方，用对能力，不一定要全程上最贵的那个。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: Intrect-io/OpenSwarm
> GitHub: https://github.com/Intrect-io/OpenSwarm
> NPM: @intrect/openswarm
> License: MIT | Stars: 856

---

Claude Code, Codex, any model on OpenRouter — you have multiple tools already, but every time you need to work through a backlog of Linear issues, you're still manually handing each one to AI, waiting for results, reviewing, then opening a PR.

OpenSwarm wants to automate that loop: pick up tasks from an issue tracker, assign to Workers, validate with Reviewers, report progress via Discord/Slack, and remember each repository's history in LanceDB — so next time a similar task comes up, it recalls what worked.

---

## I. Core Pipeline: Worker + Reviewer Pairs

OpenSwarm's fundamental unit is a pair of agents:

- **Worker**: executes tasks, writes code, runs tests
- **Reviewer**: checks Worker output and decides whether it passes

The practical value of this pair architecture is **Hybrid mode**:

> Frontier model (read-only) diagnoses the problem → lightweight model executes the fix → verification loop confirms the result

SWE-bench Lite numbers: Hybrid mode resolved 3 instances that every single lightweight model had failed on independently. Diagnostic capability applied correctly lets a cheaper model complete what otherwise requires a frontier model — at a fraction of the cost.

---

## II. Supported Worker Models

Workers aren't bound to a single model:

- **Codex / GPT**: ChatGPT OAuth login, Codex or GPT series
- **OpenRouter**: any model, API key or OAuth, covering nearly all major and open-source models
- **Local models**: Ollama / LM Studio, no account needed
- **Claude Code** (`claude -p`): opt-in fallback via the Claude Code CLI
- **Atlas Cloud**: built-in `atlascloud` adapter, OpenAI-compatible

`openswarm provider` switches at any time — a running daemon switches in place without restart.

---

## III. Task Sources: Linear or Local SQLite

Two task sources, configured during `openswarm init`:

**Linear**: OAuth login, pick team and project, issues sync automatically. Labels, priorities, and assignments all carry over.

**Local SQLite**: no Linear account needed, built-in issue tracker — suitable for personal projects or when you don't want third-party integrations.

Both modes share the same internal workflow abstraction — switching the data source doesn't affect anything else.

---

## IV. openswarm review: CI Merge Gate

`openswarm review` is the most fully designed feature in this tool.

**Basic**: review working-tree changes.

**`--max` mode**: full-codebase audit — fans reviewer subagents across code areas in parallel, synthesizes a report, creates Linear issues (up to 10, with parent/child relationships), outputs to `.openswarm/audit/`.

**`--max --fix` mode**: after the audit, groups independently fixable findings, runs fixes in isolated sandboxes, publishes a PR only after every area passes re-review and deterministic verification.

```bash
openswarm review          # review diff
openswarm review --max    # full-codebase audit + Linear issues
openswarm review --max --fix  # audit + fix + PR
```

CI gate exit codes:
- `0`: passed (or nothing to review)
- `1`: gate ran, verdict is reject
- `2`: gate did NOT run (quota exhausted, adapter failure) — must never count as a pass

GitHub Actions composite action is built in: `uses: unohee/OpenSwarm@main`, outputs `decision`, `gate-ran`, `sarif-file`.

---

## V. openswarm pr: PR Autopilot

```bash
openswarm pr status        # snapshot: conflicts / CI / review feedback
openswarm pr fix           # one-shot fix for the current branch's open PR
openswarm pr review        # re-apply reviewer feedback
openswarm pr review --fresh  # run a fresh code review of the PR diff and post as comment
openswarm pr review --all    # review all open PRs in the repo
openswarm pr watch         # loop fix until merge-ready (default 5 rounds)
openswarm pr create        # local fix → commit → push → gh pr create
```

`openswarm pr watch` is fire-and-monitor mode: set the goal (merge-ready), OpenSwarm cycles through fix → re-review → verify until it passes or rounds run out, reporting progress via Discord/Slack throughout.

---

## VI. LanceDB Cognitive Memory: Per-Repository Learning

After each Worker task completes, the outcome is written to that repository's LanceDB knowledge base. For similar future tasks, those historical results are recalled and injected into the prompt.

This isn't global memory — it's **per-repository knowledge accumulation**: Project A's lessons don't pollute Project B, but Project A's own experience compounds over time. As task count grows, Worker performance on that codebase theoretically improves continuously.

---

## VII. Sandbox: bubblewrap on Linux

Verification runs inside a sandbox and fails closed — if sandboxing isn't available, it refuses to run rather than silently falling back to unsandboxed execution.

Linux requires bubblewrap:

```bash
sudo apt-get install -y bubblewrap
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
# GitHub Actions ubuntu-latest needs both — the image defaults the sysctl to 1,
# which makes even "bwrap --unshare-user" fail with Permission denied
```

macOS uses the platform sandbox — no extra setup needed.

---

## Quick Start

```bash
npm install -g @intrect/openswarm

# Interactive wizard: provider auth + Linear OAuth + write config.yaml
openswarm init

# Diagnose environment
openswarm doctor

# Launch TUI
openswarm
```

The TUI has six tabs: Chat / Projects / Tasks / Stuck / Issues / Logs. The status bar shows current provider, model, message count, and cumulative cost in real time.

---

## Teardown Summary

OpenSwarm automates the loop of "hand a programming task to AI" — tasks come from Linear, Workers execute, Reviewers validate, progress reports to Discord, history lands in LanceDB, PRs run a CI gate.

856 stars, TypeScript, MIT open-source. The Hybrid mode design (read-only diagnosis + lightweight implementation) is an engineering approach worth noting: apply the right model at the right capability point rather than defaulting to the most expensive option throughout.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
