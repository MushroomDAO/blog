---
title: "纠错一次，永不再犯——Claude Code Reflect 系统的持续学习机制"
description: "Reflect 是一个 Claude Code Skill 系统，通过分析每次对话里的纠错信号，自动把「不要用 pip，用 uv」这类修正写进 skill 文件。下次会话，错误不再重现。本文拆解它的工作原理、置信度分级机制和 Git 版本控制设计。"
pubDate: 2026-07-27
heroImage: "../../assets/images/claude-reflect-system-continual-learning-skill-correction-persistent-banner.jpg"
category: "Tech-Experiment"
tags: ["Claude Code", "持续学习", "Skill", "AI记忆", "自动化", "开发工具"]
---

使用 Claude Code 的人都踩过同一个坑：

```
第 1 次会话：Claude 用 pip 安装依赖
你：不对，用 uv，不要用 pip
Claude：好的，这次用 uv

第 2 次会话：Claude 又用 pip 了
你：我上次说了用 uv……
```

下一次会话，所有纠正都消失了。上下文窗口关掉，记忆清零。

**Reflect** 解决的就是这个问题。它不是给 Claude 加记忆，而是把你的纠错直接写进 skill 文件——下次会话从启动时就带着这个约束，不需要提醒。

---

## 工作原理：从纠错到 skill 更新

整个流程是一个闭环：

**1. 正常工作，Claude 犯错**

你让 Claude 创建一个 Python 项目，它用了 pip：
```bash
pip install fastapi
pip freeze > requirements.txt
```

**2. 你纠正它**

> "不对，用 uv，不要用 pip，uv 更快更现代。"

**3. 运行 `/reflect`**

Reflect 分析当前会话的对话历史，识别纠错信号：

```
检测到信号：
- 类型：HIGH 置信度纠正
- 模式："用 X 代替 Y"
- 旧行为: pip
- 新行为: uv
```

**4. 审核变更**

Reflect 显示它准备写入 skill 的 diff，你按 `A` 确认：

```diff
+## Critical Corrections
+
+**使用 'uv' 而不是 'pip'**
+- ✗ 不要: pip install
+- ✓ 要用: uv pip install
```

**5. 永久生效**

第 3 次、第 100 次会话，Claude 自动用 uv。纠正行为被持久化了。

---

## 置信度分级：三种信号，三种处理

Reflect 不是把所有对话都当纠错——它按置信度分级处理：

**HIGH（红色）— 明确纠正**
```
"不对，用 X 而不是 Y"
"永远不要做 X"
"每次都要检查 Y"
```
→ 写入 `Critical Corrections` 块，强制执行

**MEDIUM（黄色）— 正向确认**
```
"对，就是这样"
"这个挺好"
"完全正确"
```
→ 写入 `Best Practices` 块，记录成功模式

**LOW（绿色）— 建议和考虑**
```
"你有没有考虑过……"
"如果用 X 会怎样？"
```
→ 写入 `Considerations` 块，作为参考

这个分级设计避免了两个极端：把所有话都当成命令（噪音太多），或者只记录强制要求（丢失有价值的最佳实践）。

---

## 安全机制：每次更新都有退路

每次 skill 更新前，Reflect 做三件事：

**时间戳备份**：修改前，原文件自动备份到 `.state/backups/`，文件名带时间戳。

**YAML 验证**：更新写入前先验证语法，格式错误自动回滚，不会产生损坏的 skill 文件。

**Git 提交**：每次学习都是一个带描述的 git commit，完整保留修改历史：
```
git commit -m "reflect: learned to use uv instead of pip [HIGH confidence]"
```

这意味着学习历史是可追溯的、可回滚的，也可以通过 git 在团队间共享。

---

## 两种运行模式

**手动模式**（推荐新手）

会话结束后手动运行：
```bash
/reflect
```
你控制每次学习的节奏，每条变更都要亲自审核。

**自动模式**（持续学习）

```bash
/reflect-on
```
通过 Stop Hook 自动触发——每次会话结束时自动分析并应用学习。

Hook 配置在 `~/.claude/settings.local.json` 里：
```json
{
  "hooks": {
    "Stop": [{"command": "reflect/scripts/hook-stop.sh"}]
  }
}
```

---

## 安装和上手

```bash
# 复制到 Claude Code skills 目录
cp -r reflect ~/.claude/skills/
cp -r python-project-creator ~/.claude/skills/

# 检查状态
/reflect-status
```

仓库里还带了一个 `python-project-creator` 演示 skill——它的初始状态用 pip 和 unittest，经过几次纠错学习后，会自动切换成 uv 和 pytest。可以用它完整走一遍学习流程，理解 Reflect 在做什么。

---

## 一个更深层的问题

传统 AI 编程助手的记忆模型是会话级的：上下文在，记忆在；上下文清空，一切重置。这在个人使用时是轻微摩擦，在团队使用时是持续的培训成本——每个新会话都要重新建立同样的上下文。

Reflect 的思路是把"团队约定"从对话历史里抽出来，写进 skill 文件。skill 文件是持久的、可版本控制的、可 git push 分享的。这相当于把软性的"口头约定"变成了机器可读的硬约束。

它目前还是工具层面的解法——依赖 Claude Code 读取 skill 文件的行为。但这个方向的逻辑是清晰的：**会话是短暂的，规则应该是持久的。**

---

项目地址：[github.com/haddock-development/claude-reflect-system](https://github.com/haddock-development/claude-reflect-system)（198 ⭐，MIT License）

<!--EN-->

## Correct Once, Never Again — How Claude Reflect Builds Persistent AI Memory

Every developer who uses Claude Code has hit the same wall:

```
Session 1: Claude uses pip
You:       "No, use uv instead"
Claude:    "Got it, using uv"

Session 2: Claude uses pip again
You:       "I told you last time…"
```

Context window closes, memory resets. Every session starts from scratch.

**Reflect** solves this at the infrastructure level. It doesn't add memory to Claude — it writes your corrections directly into skill files. The next session starts with that constraint already loaded, no reminder needed.

---

## How It Works: From Correction to Skill Update

The full loop:

**1. Claude makes a mistake**

You ask for a Python project, it uses pip:
```bash
pip install fastapi
pip freeze > requirements.txt
```

**2. You correct it**

> "No, use uv instead of pip — it's faster and modern."

**3. Run `/reflect`**

Reflect analyzes the conversation history and identifies the correction signal:

```
Signal detected:
- Type: HIGH confidence correction
- Pattern: "use X instead of Y"
- Old: pip
- New: uv
```

**4. Review the diff**

Reflect shows what it's about to write to the skill. Press `A` to approve:

```diff
+## Critical Corrections
+
+**Use 'uv' instead of 'pip'**
+- ✗ Don't: pip install
+- ✓ Do: uv pip install
```

**5. Permanent**

Session 3, session 100 — Claude uses uv automatically. The correction is persisted.

---

## Three Confidence Levels

Reflect doesn't treat every comment as a correction — it grades signals:

**HIGH (red) — Explicit corrections**
```
"No, use X instead of Y"
"Never do X"
"Always check Y first"
```
→ Written to `Critical Corrections` block — enforced

**MEDIUM (yellow) — Positive confirmations**
```
"Yes, exactly like that"
"That works well"
"Perfect"
```
→ Written to `Best Practices` block — recorded as successful patterns

**LOW (green) — Suggestions and observations**
```
"Have you considered…?"
"What about using X?"
```
→ Written to `Considerations` block — reference only

This grading prevents both failure modes: treating every utterance as a command (too noisy), or recording only hard requirements (losing valuable best-practice signal).

---

## Safety: Every Update Has a Rollback

Before each skill update, Reflect does three things:

**Timestamped backup**: original file auto-saved to `.state/backups/` with a timestamp before any change.

**YAML validation**: syntax checked before writing. Malformed output triggers automatic rollback — no corrupted skill files.

**Git commit**: each learning produces a git commit with a description:
```
git commit -m "reflect: learned to use uv instead of pip [HIGH confidence]"
```

Learning history is traceable, reversible, and shareable across teams via git.

---

## Two Operation Modes

**Manual mode** (recommended for starting out):
```bash
/reflect
```
You control the pace. Every change requires your explicit approval.

**Auto mode** (continuous learning):
```bash
/reflect-on
```
Triggers automatically via Stop Hook at the end of each session. Hook config in `~/.claude/settings.local.json`:
```json
{
  "hooks": {
    "Stop": [{"command": "reflect/scripts/hook-stop.sh"}]
  }
}
```

---

## Installation

```bash
cp -r reflect ~/.claude/skills/
cp -r python-project-creator ~/.claude/skills/
/reflect-status
```

The repo includes `python-project-creator` as a working demo — it starts using pip and unittest, then evolves to uv and pytest through corrections. Walk through it to see the full learning cycle in action.

---

## The Deeper Issue

Traditional AI assistants have session-scoped memory: context active, memory active; context cleared, everything resets. For individual use, this is friction. For team use, it's ongoing training cost — every new session re-establishes the same context.

Reflect's approach: lift "team conventions" out of conversation history and write them into skill files. Skill files are persistent, version-controlled, and shareable via git. It turns soft oral agreements into machine-readable hard constraints.

It's currently a tooling-layer solution — dependent on Claude Code's skill-file loading behavior. But the direction is clear: **sessions are ephemeral; rules should be permanent.**

**Project**: [github.com/haddock-development/claude-reflect-system](https://github.com/haddock-development/claude-reflect-system) (198 ⭐, MIT)
