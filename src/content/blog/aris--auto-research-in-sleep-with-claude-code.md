---
title: 'ARIS: 让 AI 在你睡觉时做科研'
titleEn: 'ARIS: Auto Research in Sleep with Claude Code'
description: '一个基于双模型协作的自主 ML 科研系统，让 Claude Code 执行，GPT 审稿，实现全自动研究流水线'
descriptionEn: 'A dual-model collaborative autonomous ML research system using Claude Code for execution and GPT for review'
pubDate: '2026-04-03'
category: 'Research'
tags: ['claude-code', 'ai-research', 'multi-agent', 'ml-pipeline', 'automation']
heroImage: '../../assets/blog-cover-20260403.jpg'
---

## 科研自动化的痛点

做过 ML 研究的人都知道，一个完整的研究周期要经历多少重复劳动：读论文、找 idea、写代码、跑实验、分析结果、写 paper、回应审稿意见... 而这些任务往往被割裂在不同的工具里，上下文不断丢失。

最近发现的一个有趣项目 **ARIS**（Auto Research in Sleep），尝试用 Claude Code 的自定义 Skill 系统把整个科研流程串起来。核心理念很简单：**让 Claude 在你睡觉时干活，醒来时论文已经被审了好几轮**。

## 双模型协作机制

ARIS 的设计亮点在于**跨模型协作**：

- **执行者**：Claude Code —— 负责读文件、改代码、跑实验、收结果
- **审稿人**：GPT-5.4（通过 Codex MCP）—— 负责打分、找弱点、提修改建议

两个模型互不评审自己的输出，形成真正的反馈闭环。

### 为什么不用单模型自我博弈？

技术上 Claude 的 subagent 可以同时承担执行和审稿，但容易陷入**局部最优**——同一个模型审自己的东西会有盲区。

作者打了个有趣的比方：单模型自审是 stochastic bandit（噪声可预测），跨模型审稿则是 adversarial bandit（审稿者会主动找茬）——而后者天然更难被「糊弄」。

至于为什么是**两个模型而不是更多**？因为 1→2 的收益最大，增加到 3、4 个审稿人只会提升 API 开销，边际收益递减。

## 实际能做什么？

ARIS 提供几条核心命令：

### 1. 全自动研究流水线

给一个研究方向，ARIS 自己搞定全套：

```
/research-pipeline "离散扩散语言模型的 factorized gap"
```

### 2. 基于现有工作的改进

有篇论文想改进？把论文链接和代码仓库给它：

```
/research-pipeline "改进方法 X" \
  --ref https://arxiv.org/abs/2406.04329 \
  --repo https://github.com/org/project
```

流程是：读论文 → 分析弱点 → 克隆代码 → 生成改进方案 → 跑实验 → 写 paper。

### 3. Rebuttal 辅助

审稿意见来了也不用慌：

```
/rebuttal "paper/ + reviews" --venue ICML --limit 5000
```

系统会解析每条意见、制定策略、起草回应，并确保**不编造、不过度承诺、全覆盖**三道安全门。

## 轻量到离谱的架构

ARIS 的另一个吸引我的点是**零依赖**。整个系统就是纯 Markdown 文件：

- 没有框架要学
- 没有数据库要维护
- 没有 Docker 要配
- 没有守护进程要看管

每个 skill 就是一个 `SKILL.md`，任何 LLM 都能读懂。你可以把它迁移到 Codex CLI、Cursor、Trae、Windsurf 或者其他 agent 框架，工作流照样跑。

## 实际落地效果

项目展示了两篇完全由 ARIS 完成的论文：

| 论文 | 评分 | 会议 | 作者 | 配置 |
|------|------|------|------|------|
| CS 论文 | 8/10 "clear accept" | CS 会议 | @DefanXue & @Monglitay | Claude + GPT-5.4 |
| AAAI 论文 | 7/10 "good paper, accept" | AAAI 2026 | @xinbo820-web | 纯 Codex CLI |

## 一点思考

ARIS 的价值不只是「自动化」，而是**把科研流程从「人驱动」变成「流程驱动」**。研究者从执行者变成策展人，把精力集中在定义问题和判断方向上，而具体的 dirty work 交给 AI。

当然，这种工作流更适合偏工程、偏实验的 ML 方向。对于需要深度数学推导或者领域洞察的研究，AI 还替代不了人类的直觉。但作为一个**快速原型验证工具**，ARIS 的思路很值得借鉴。

---

**项目地址**: https://github.com/jhfnetboy/ARIS  
**核心**: Claude Code + GPT-5.4 / Codex CLI 双模型协作
