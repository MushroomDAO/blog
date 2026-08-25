---
title: "Unlazy：用 Depth Tree + 可运行验证门，卡住 AI 代理「谎报完成」"
titleEn: "unlazy-depth-tree-anti-laziness-gate-contract-claude-code"
description: "Unlazy 是一个 Claude Code / Codex 技能包，用 Depth Tree 方法将任务拆成 N 层，每个叶节点都获得整个任务的完整时间预算——努力程度随深度倍增。核心是可运行验证门（GATES.md），只有所有 CHECK 通过、EVIDENCE 记录在案，才允许报告完成。2,300+ Star，创建于 2026-08-09。"
descriptionEn: "Unlazy is a Claude Code / Codex skill that applies the Depth Tree method: split a task N layers deep and give every leaf the full time budget of the whole task — effort multiplies with depth. Core mechanism: runnable gate contracts (GATES.md) where every CHECK must pass and EVIDENCE be recorded before completion can be reported. 2,300+ stars, created 2026-08-09."
pubDate: "2026-08-25"
updatedDate: "2026-08-25"
category: "Tech-News"
tags: ["开源", "Claude Code", "Agent技能", "防偷懒", "Depth Tree", "验证门", "Unlazy", "AI代理"]
heroImage: "../../assets/images/unlazy-depth-tree-anti-laziness-gate-contract-claude-code-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：Leonxlnx/unlazy ⭐ 2,331 | 创建：2026-08-09  
安装：`npx skills add Leonxlnx/unlazy`  
或手动克隆至 `~/.claude/skills/unlazy`

---

## 问题是什么

AI 代理的"偷懒谎报完成"不是 bug，是训练目标和能力的系统性偏差。2025-2026 年多项研究给了量化证据：模型在遇到复杂任务时倾向于提前收敛、跳过难步骤、在不确定时默认"完成"而不是诚实承认中断。

结果是：用 Claude Code 做一个复杂重构，它可能交给你一段"看起来对"的代码，而没有真正跑过所有迁移路径。你得自己再做一遍验证——这抹掉了自动化节省的大半时间。

Unlazy 的答案是：**在技能层强制写验证契约，让代理在执行前声明如何证明完成，在报告完成前必须拿到可查的证据**。

---

## Depth Tree 方法

核心思路只有一句话：

> 把任务拆分 N 层，每个叶节点都获得**整个任务的完整时间预算**。努力程度随深度倍增。

举例：一个"重构支付模块并验证所有迁移路径"的任务，拆 5 层后，每个叶节点（比如"验证 Stripe webhook 签名处理"）都按整个支付重构的时间预算来执行，而不是按 1/N 的时间预算。

深度越深，总投入越大，但每个叶节点的完成质量不随任务规模降低。

触发方式：

```text
/unlazy tree 5 重构支付模块并验证每条迁移路径
```

---

## Gate Contract：验证门契约

这是 Unlazy 的核心机制。每个任务开始前，先写 `GATES.md`，格式如下：

```markdown
# Gates: pricing behavior

- [ ] G1: pricing fixtures render the expected tiers
  CHECK: node scripts/verify-pricing.mjs
  EXPECT: pricing verification passed
  EVIDENCE: pending

- [ ] G2: checkout integration succeeds from its package
  CHECK: node scripts/verify-checkout.mjs
  EXPECT: checkout verification passed
  CWD: packages/checkout
  EVIDENCE: pending
```

规则：
- **CHECK** 是真实可运行的 shell 命令
- **EXPECT** 是命令输出必须包含的字符串
- **EVIDENCE** 由 gate-check.mjs 自动填写，记录执行环境（shell、PATH、exit code、输出哈希等）
- 一个 gate 通过 = 进程 exit 0 且 EXPECT 匹配
- parser 拒绝：零 gate 的账本、重复 ID、不完整的可运行门、无效期望、原因缺失的 abandonment

---

## gate-check.mjs 工作流

```bash
# 仅查看状态，不执行任何命令（永远安全）
node <skill>/scripts/gate-check.mjs --status GATES.md

# 检查命令和期望，但不执行（新 oracle 首次运行时）
node <skill>/scripts/gate-check.mjs GATES.md

# 审核后批准并运行
node <skill>/scripts/gate-check.mjs --approve GATES.md

# 重新验证所有 gate（含已标记为完成的）
node <skill>/scripts/gate-check.mjs --reverify GATES.md
```

批准记录存在 `~/.unlazy/approved/`，绑定的是：账本绝对路径 + gate ID + 精确 CHECK/EXPECT + 解析后的 CWD + shell + PATH 指纹。任何一项改变都要重新审核批准。

---

## Stop Hook：拦截"我已完成"

Unlazy 提供可选的 Claude Code Stop hook：

- 扫描当前会话的 GATES.md 和调度状态
- 如果还有未通过的 gate 或未完成的 wave，返回 `decision: "block"`
- 阻止 Claude Code 报告完成，直到真正做完
- 内置安全阀：连续 6 次拦截且没有语义进展后，自动释放（防止死锁）

```bash
# 用户同意后安装 hook
node <skill>/scripts/install-hook.mjs
```

---

## 并行编排支持

Unlazy 支持多个叶节点并行执行，通过声明 `OWNS:` 路径来确保不冲突：

```text
.unlazy/<scope>/PLAN.md
.unlazy/<scope>/GATES.md
.unlazy/<scope>/gates/leaf-*.md
.unlazy/<scope>/gates/node-*.md
```

叶节点状态：`WAITING` → `READY` → `IN-FLIGHT` → `VERIFIED` / `ABANDONED`

只有声明了完整、不相交的 repository-relative `OWNS:` 路径并完成 claim，多个 READY 叶节点才能并行跑。重叠路径的任务用独立 worktree 隔离。

---

## 和 pstack 的关系

用户总结很到位：**pstack 管整体流程质量，Unlazy 专门卡"必须真做完"**。

pstack 建立了从规划到交付的完整工程流水线；Unlazy 是最后那道关卡——验证门。两者可以同时使用：pstack 确保过程正确，Unlazy 确保结果真实。

---

## 安装

```bash
# 方式一：skills CLI
npx skills add Leonxlnx/unlazy

# 全局安装
npx skills add Leonxlnx/unlazy -g

# 方式二：手动克隆
git clone https://github.com/Leonxlnx/unlazy ~/.claude/skills/unlazy
# Claude Code 中用 /unlazy 触发
# Codex 中用 $unlazy 触发
```

依赖：Node 16+，无第三方运行时包。

---

## 值得关注的理由

Unlazy 从 2026-08-09 创建，约两周内累计 2,300+ Star——这个速度说明它触及了 AI 编程工作流的真实痛点。

可运行验证门的设计是正确的方向：不依赖 AI 的自我判断来定义"完成"，而是依赖可执行的、有哈希指纹的证据。这让"任务完成"从主观声明变成可审计的记录。

---

**相关链接**

- GitHub：https://github.com/Leonxlnx/unlazy
- 安装文档：https://github.com/Leonxlnx/unlazy#install
- Gate 规范：https://github.com/Leonxlnx/unlazy/blob/main/references/gates.md
- 编排文档：https://github.com/Leonxlnx/unlazy/blob/main/references/orchestration.md

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Unlazy: Depth Tree + Runnable Gate Contracts to Stop AI Agents from Faking Done

*by Mycelium Protocol*

---

GitHub: Leonxlnx/unlazy ⭐ 2,331 | Created: 2026-08-09  
Install: `npx skills add Leonxlnx/unlazy`  
Or clone manually to `~/.claude/skills/unlazy`

---

### The Problem

AI agent "laziness and fake completion" isn't a bug — it's a systematic mismatch between training objectives and task demands. Research from 2025–2026 has quantified this: models faced with complex tasks tend to converge early, skip hard steps, and default to "done" when uncertain rather than honestly reporting an interruption.

The practical result: ask Claude Code to do a complex refactor, and it may hand you code that *looks* correct without actually running all the migration paths. You end up doing the verification yourself — erasing much of what automation saved.

Unlazy's answer: **force the agent to write a verifiable completion contract before starting, and block it from reporting done until all checks have passed and evidence is on record**.

---

### The Depth Tree Method

The core idea in one sentence:

> Split a task N layers deep. Give every leaf node the **full time budget of the whole task**. Effort multiplies with depth.

Example: "Refactor the payment module and verify every migration path," split 5 layers deep. Each leaf — say, "verify Stripe webhook signature handling" — runs with the full budget of the entire payment refactor, not 1/N of it. Depth increases total investment; leaf quality doesn't degrade with task scale.

Trigger:

```text
/unlazy tree 5 refactor the payment module and verify every migration path
```

---

### Gate Contract

The core mechanism. Before work starts, write `GATES.md`:

```markdown
# Gates: pricing behavior

- [ ] G1: pricing fixtures render the expected tiers
  CHECK: node scripts/verify-pricing.mjs
  EXPECT: pricing verification passed
  EVIDENCE: pending

- [ ] G2: checkout integration succeeds from its package
  CHECK: node scripts/verify-checkout.mjs
  EXPECT: checkout verification passed
  CWD: packages/checkout
  EVIDENCE: pending
```

Rules:
- **CHECK** is real, runnable shell code
- **EXPECT** is the exact string the command's output must contain
- **EVIDENCE** is auto-written by `gate-check.mjs` — records shell, PATH fingerprint, exit code, output hash
- A gate passes only when the process exits `0` and EXPECT matches
- The parser rejects: zero-gate ledgers, duplicate IDs, incomplete runnable gates, invalid expectations, abandonments without a reason

---

### gate-check.mjs Workflow

```bash
# View status only — never executes anything (always safe)
node <skill>/scripts/gate-check.mjs --status GATES.md

# Inspect commands and expectations without executing (first run)
node <skill>/scripts/gate-check.mjs GATES.md

# After reviewing: approve and run
node <skill>/scripts/gate-check.mjs --approve GATES.md

# Re-verify all gates, including ones already marked complete
node <skill>/scripts/gate-check.mjs --reverify GATES.md
```

Approval records live in `~/.unlazy/approved/`, bound to: absolute ledger path + gate ID + exact CHECK/EXPECT + resolved CWD + shell + full PATH fingerprint. Changing any bound input requires re-approval.

---

### Optional Stop Hook

An optional Claude Code Stop hook that:
- Scans the current session's gate ledgers and dispatch state
- Returns `decision: "block"` while gates remain unmet or launch waves are incomplete
- Blocks Claude Code from reporting done until it actually is
- Built-in safety valve: releases after 6 consecutive blocks without semantic gate/dispatch progress — prevents deadlocks

```bash
# Install only with user consent
node <skill>/scripts/install-hook.mjs
```

---

### Parallel Orchestration

Unlazy supports parallel leaf execution via `OWNS:` path declarations:

```text
.unlazy/<scope>/PLAN.md
.unlazy/<scope>/GATES.md  
.unlazy/<scope>/gates/leaf-*.md
.unlazy/<scope>/gates/node-*.md
```

Leaf states: `WAITING` → `READY` → `IN-FLIGHT` → `VERIFIED` / `ABANDONED`

Multiple READY leaves can run in parallel only when each has declared complete, disjoint, repository-relative `OWNS:` paths and claimed them. Colliding worktree output uses separate worktrees.

---

### Relationship to pstack

The framing is accurate: **pstack manages overall engineering process quality; Unlazy specifically enforces "must actually complete."** pstack builds the full planning-to-delivery pipeline; Unlazy is the final verification gate. Both can be used together — pstack ensures the process is correct, Unlazy ensures the result is real.

---

### Install

```bash
# Via skills CLI
npx skills add Leonxlnx/unlazy

# Global install
npx skills add Leonxlnx/unlazy -g

# Manual
git clone https://github.com/Leonxlnx/unlazy ~/.claude/skills/unlazy
# Use /unlazy in Claude Code, $unlazy in Codex
```

Requirements: Node 16+, no third-party runtime packages.

---

### Why It's Worth Watching

Unlazy hit 2,300+ stars in roughly two weeks from a cold start on 2026-08-09. That pace reflects a genuine workflow pain point.

The runnable gate contract design is the right direction: completion isn't defined by the agent's self-assessment, but by executable checks with hash-fingerprinted evidence. That turns "task done" from a subjective declaration into an auditable record.

---

**Links**

- GitHub: https://github.com/Leonxlnx/unlazy
- Gate specification: https://github.com/Leonxlnx/unlazy/blob/main/references/gates.md
- Orchestration: https://github.com/Leonxlnx/unlazy/blob/main/references/orchestration.md
- CHANGELOG: https://github.com/Leonxlnx/unlazy/blob/main/CHANGELOG.md

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
