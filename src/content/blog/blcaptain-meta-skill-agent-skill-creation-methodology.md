---
title: "BLCaptain Meta Skill：把你反复讲给 AI 的那套经验，封装成一次安装、永久复用的 Agent Skill"
description: "你有没有这种经历：每次打开新对话，都要重新把同一套 SOP、提示词、专家判断讲给 AI 听？BLCaptain Meta Skill 是一个开源方法论包，专门解决这个问题——帮你把重复工作流产品化为可安装、可验证、可迭代的 Agent Skill。它是 Codex 与 Claude Code 7 轮协同迭代的结果。"
titleEn: "BLCaptain Meta Skill: Package Your Repeated AI Explanations into a Once-Installed, Always-Reusable Agent Skill"
descriptionEn: "Ever found yourself re-explaining the same SOP, prompts, and expert knowledge to AI every new conversation? BLCaptain Meta Skill is an open-source methodology package that productizes repetitive workflows into installable, verifiable, iterable Agent Skills — the result of 7 collaborative iterations between Codex and Claude Code."
pubDate: 2026-06-15
category: "Tech-News"
tags: ["AgentSkill", "ClaudeCode", "Codex", "MetaSkill", "AI工具", "工作流", "开源", "提示词工程", "SOP"]
lang: "zh-CN"
heroImage: "../../assets/images/blcaptain-meta-skill-agent-factory.png"
---

> 2026-06-15 · 工具观察

你有没有这种经历：

打开一个新的 AI 对话，想让它帮你做某件事，结果要先花 5 分钟把背景、规范、注意事项解释一遍。第二天，重新解释一遍。下周，再解释一遍。

**AI 的记忆是会话级的。你的知识积累是职业级的。两者之间有一道墙。**

[BLCaptain Meta Skill](https://github.com/dososo/blcaptain-meta-skill) 是一个刚刚开源的项目，专门用来拆掉这道墙——把你反复讲给 AI 的那套 SOP、提示词、专家经验，打包成一个可以安装到任何 Agent 上的 Skill 文件，下次直接调用，再不用重讲。

---

## 它是什么

这是一个"做 Skill 的 Skill"，也就是 **Meta Skill**。

普通 Skill 帮你完成某件事；Meta Skill 帮你把"如何完成某件事的方法论"本身封装起来。

用一句话说：**BLCaptain 是一套把工作经验产品化为 Agent Skill 的 8 步方法论框架，本身就以 Skill 的形式发布**，可以直接安装到 Claude Code、Codex 等支持 Agent Skill 的工具里。

---

## 它是怎么来的

这个项目本身就是用它所提倡的方法构建的——**Codex 与 Claude Code 进行了 7 轮协同迭代**：

```
Claude Code 负责：读代码 · 拆需求 · 做架构规划 · review 审计
Codex    负责：改代码 · 跑命令 · 修测试 · 补验证证据
```

两个 AI 系统各发挥所长——Claude Code 擅长全局理解和判断，Codex 擅长精确执行和验证——7 轮下来，把一套"如何封装 Skill"的方法论本身打磨成了可安装的 Skill。

这个 meta 结构本身就是一个论证：**这套方法经受住了自身的检验**。

---

## 核心思路：先问值不值得

绝大多数 Meta Skill 的问题是：它们只告诉你怎么做，没告诉你要不要做。

BLCaptain 的第一步是一个 **Non-Skill 门控**：

在开始封装之前，先回答这些问题：
- 这个任务是否重复发生（至少每周或每月）？
- 输出是否有明确的质量标准？
- 是否存在已知的失败模式？
- 这比写一个模板、脚本或文档更值得维护成本吗？

如果答案是否，BLCaptain 会直接告诉你：**不需要做成 Skill，用更轻量的方案代替**。

这是一个少见但非常实用的设计——过滤掉那些不值得封装的任务，避免把时间浪费在过度工程化上。

---

## 8 步工作流

通过门控检查后，进入正式的 8 步流程：

| 步骤 | 核心动作 |
|------|---------|
| **① 调研** | 收集真实任务样本、成功案例和失败案例 |
| **② 分析** | NABC 分析（需求/方法/收益/竞品）+ ROI 评估 + 边界定义 |
| **③ 计划** | 设计文件结构、资源架构、验证策略 |
| **④ 开发** | 写 SKILL.md 入口 + 补充资源文件 + 模板 + 验证脚本 |
| **⑤ 验证** | 检查结构完整性、链接有效性、Token 预算 |
| **⑥ 测试** | 正例/负例/边缘场景/压力测试，每一条都要有证据 |
| **⑦ 审计验收** | 判断是否可以发布，列出阻塞项和缺失证据 |
| **⑧ 总结迭代** | 记录发现、风险和下一轮改进方向 |

---

## 最关键的设计：薄入口，深资源

SKILL.md 是每个 Agent Skill 的"入口文件"。常见的做法是把所有内容都塞进这一个文件，变成一个巨大的 prompt。

BLCaptain 的设计原则完全相反：

> **SKILL.md 只放高信号内容（触发条件、第一步、资源导航），复杂内容放到资源目录，按需加载。**

产出物的标准结构是：

```
your-skill/
  SKILL.md          ← 薄入口（≤1300 tokens）
  references/       ← 方法论深度文档
  assets/templates/ ← 可复用的模板
  scripts/          ← 可执行的验证脚本
  evals/            ← 测试证据
  examples/         ← 典型案例
  manifest.json     ← 治理元数据
```

**为什么这样设计**：Agent 有 context 限制。一次性加载所有内容既浪费 token，又让 Agent 难以聚焦。薄入口让 Agent 知道"有什么资源可用"，只在需要时才加载相应内容——效率更高，行为更可控。

---

## 证据驱动的发布

BLCaptain 另一个与众不同的地方：**不以"看起来完整"作为发布标准，而以"能证明行为"为发布标准**。

发布前必须有：
- Route 评估记录（13 条路径测试全过）
- 正例和反例的测试输出
- 已知 gotchas 的文档（基于真实失败案例，不是假设）
- context budget 验证（确认入口在 Token 限额内）

这类似于软件工程里的"发布门控"——不是凭感觉觉得好了就发，而是有明确的通过条件。

---

## 适合哪些场景

**值得封装成 Skill 的任务特征**：
- 重复发生（每周/每月都要做）
- 有清晰的输出质量标准
- 有已知的失败模式可以沉淀
- 维护成本低于每次重新解释的成本

**具体场景举例**：
- 产品经理：把 PRD 写作规范封装成 Skill，每次让 AI 写需求文档自动遵循格式
- 运营：把内容审核 SOP 封装成 Skill，AI 按你的标准而不是它自己的标准判断
- 开发者：把 Code Review 检查项封装成 Skill，统一团队 review 标准
- 设计师：把视觉规范封装成 Skill，AI 生成内容自动符合品牌风格
- 创作者：把写作语气和格式规范封装成 Skill，保持内容一致性

**不适合封装的情况**：
- 一次性的问题或探索性任务
- 流程还在频繁变化、尚未稳定的工作
- 用一个模板或脚本就能解决的事情

---

## 技术信息

- **GitHub**：[dososo/blcaptain-meta-skill](https://github.com/dososo/blcaptain-meta-skill)
- **发布时间**：2026-06-13（刚刚开源，2天前）
- **语言**：Python（验证脚本）+ Markdown（Skill 内容）
- **许可证**：个人和开源项目免费使用，商业用途需授权
- **兼容**：Claude Code、Codex CLI、以及其他支持 Agent Skill 格式的工具

---

## 安装和调用

```bash
# 克隆仓库
git clone https://github.com/dososo/blcaptain-meta-skill

# 将 skill 目录放到你的 skills 目录下
cp -r blcaptain-meta-skill/blcaptain-meta-skill ~/.claude/skills/

# 在 Claude Code 或 Codex 中调用
$blcaptain-meta-skill
```

调用后，它会引导你走完 8 个步骤，帮你把手头的工作流封装成一个新的 Skill。

---

## 一点思考

这个项目打动我的地方，不是它有多复杂，而是它解决的是一个**非常真实但经常被忽视**的问题：

AI 工具的能力边界，往往不在于模型本身，而在于**你有没有办法把自己的专业判断持久化**。

Claude Code 或 Codex 很强，但每次新会话，你的经验从零开始——除非你花时间封装它。BLCaptain 提供的，是一套让这件事变得系统化、可验证的方法。

它目前刚开源，stars 还很少（16），文档体系也在建立中。但它解决的问题方向是对的，8 步框架也足够严谨。如果你已经在用 Claude Code 或 Codex，并且有一些反复使用的工作流，这个项目值得花一小时认真看一遍。

---

**GitHub**：[dososo/blcaptain-meta-skill](https://github.com/dososo/blcaptain-meta-skill)

<!--EN-->

## BLCaptain Meta Skill: Package Your Repeated AI Instructions Once, Use Forever

Every time you open a new AI conversation, you spend 5 minutes re-explaining the same SOPs, prompts, and expert rules. AI memory is session-level; your expertise is career-level. BLCaptain Meta Skill bridges the gap.

### What It Is

A "meta skill" — a Skill that creates other Skills. It's an 8-step methodology framework for productizing repetitive workflows into installable, verifiable, iterable Agent Skills, itself distributed as an Agent Skill you can install into Claude Code or Codex.

### How It Was Built

7 collaborative iterations between Codex and Claude Code:
- Claude Code: reads code, breaks down requirements, architecture planning, audit review
- Codex: modifies code, runs commands, fixes tests, supplements validation evidence

### The Non-Skill Gate

Before packaging anything, answer: Does this task repeat regularly? Are there clear quality standards? Are failure modes known? Is it worth more than writing a template or script? If not, BLCaptain tells you: don't make it a Skill.

### 8-Step Workflow

Research → Analysis (NABC/ROI) → Plan → Develop → Validate → Test → Audit → Iterate

### Key Design: Thin Entry, Deep Resources

SKILL.md stays minimal (≤1300 tokens) — only triggers, first steps, and navigation. Complexity lives in `references/`, `assets/templates/`, `evals/`, `scripts/`, `examples/`. Loaded on demand, not all at once.

### Evidence-Driven Release

Not "looks complete" but "behavior proven": 13 route test cases, positive/negative scenario outputs, real-failure-based gotchas, context budget verification.

**GitHub**: [dososo/blcaptain-meta-skill](https://github.com/dososo/blcaptain-meta-skill) · Free for personal/OSS · Commercial requires authorization
