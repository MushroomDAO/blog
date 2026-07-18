---
title: "Caveman：83K Star，让 AI Agent 省 65% Token 的神奇骚操作"
titleEn: "Caveman: 83K Stars — Make AI Agents Talk Like Cavemen, Save 65% Output Tokens"
description: "Caveman 是一个 Claude Code/Codex/Cursor 的 skill 插件，83,000+ Stars，让 AI Agent 用「穴居人语言」回复（去掉废话、保留技术精度），节省 65% 的输出 Token，同时保持代码、命令、错误信息字节精确。JS 实现，MIT 开源，30+ Agent 支持，安装即生效。"
descriptionEn: "Caveman (82,990 ⭐, JavaScript, MIT) is a skill/plugin for Claude Code, Codex, Cursor, and 30+ AI coding agents. Install once, and the agent drops filler words and answers in compressed caveman-speak — 65% fewer output tokens, technically identical results. Code, commands, and error messages remain byte-for-byte exact."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-News"
tags: ["AI Agent", "Claude Code", "Token优化", "开源", "开发工具", "Codex", "Cursor", "skill"]
heroImage: "../../assets/images/caveman-ai-agent-token-reduction-skill-banner.jpg"
---

> **GitHub**: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) · ⭐ 82,990 · JavaScript · MIT  
> **适用**: Claude Code / Codex / Cursor / Windsurf / Cline / Copilot / 30+ agents

---

## 83K Stars 是因为一个让人发笑的洞察

```
正常 AI Agent（69 tokens）:
"The reason your React component is re-rendering is likely because 
you're creating a new object reference on each render cycle. When 
you pass an inline object as a prop, React's shallow comparison 
sees it as a different object every time, which triggers a re-render. 
I'd recommend using useMemo to memoize the object."

Caveman AI Agent（19 tokens）:
"New object ref each render. Inline object prop = new ref = re-render. 
Wrap in `useMemo`."
```

**同样的答案。三分之一的词。技术信息一个字没丢。**

这就是 Caveman 做的事：让你的 AI Agent 像穴居人一样说话——不是让它变笨，而是**让它的嘴变小**。

---

## 为什么 65% Token 节省是真实的

很多 AI Agent 的回复结构是这样的：

```
[礼貌开头] + [废话说明] + [实际答案] + [礼貌结尾]
    15%           20%            55%          10%
```

Caveman 去掉的是前面 45% 的填充——开头的"当然可以！"、中间的解释性铺垫、结尾的"希望这有帮助！"。

**保留的是什么**：
- 代码块（字节精确）
- 命令（字节精确）
- 错误信息（字节精确）
- 技术推理（核心结论保留）

---

## 实际效果对比

| 场景 | 正常 | Caveman | 节省 |
|---|---|---|---|
| 解释 React re-render | 69 tokens | 19 tokens | **72%** |
| 调试 auth middleware | 58 tokens | 18 tokens | **69%** |
| 写一个 async 函数 | ~80 tokens | ~28 tokens | **65%** |
| 解释 git rebase | ~120 tokens | ~40 tokens | **67%** |

官方测试数据：平均节省 **65% 输出 Token**，输入 token 不变，技术准确率 100%。

---

## 安装：三分钟搞定

### Claude Code

```bash
# 方法 1：直接告诉 Claude Code
"安装 caveman skill"
# Claude Code 会自动从 GitHub 安装

# 方法 2：手动
git clone https://github.com/JuliusBrussee/caveman ~/.claude/skills/caveman
```

### Codex

```bash
git clone https://github.com/JuliusBrussee/caveman ~/.codex/skills/caveman
```

### Cursor / Windsurf

```bash
# 同理，克隆到对应的 skills 目录
git clone https://github.com/JuliusBrussee/caveman \
  ~/.cursor/skills/caveman  # 或对应路径
```

安装后，Agent 自动读取 skill 文件，下次响应就开始以穴居人模式回复。

---

## 强度等级：选你的「穴居人层级」

Caveman 提供几个压缩强度选项（通过配置 INSTALL.md 里的选项）：

| 等级 | 风格 | 适合场景 |
|---|---|---|
| **Grunt** | 极简，纯命令 | 你已经知道背景，只要代码 |
| **Caveman**（默认） | 简洁技术 | 日常编码，平衡 |
| **Verbose Caveman** | 多保留推理 | 复杂问题，需要理解过程 |

---

## Caveman 2：正在开发

根据 README，Caveman 2 正在开发中，计划功能：
- 输入 token 也压缩（系统提示压缩）
- 基于上下文自动调整压缩强度
- 更多 Agent 平台支持

---

## 为什么这个方案工作但没人想到？

关键洞察来自一个观察：AI Agent 的冗余输出不是模型能力不足，而是**训练数据偏向**——训练数据里大量是对话体的、礼貌的、解释性的文本。

Caveman 通过在 system prompt / skill 里加约束，相当于给模型换了一套"说话方式"。模型的推理能力没变，只是输出格式变了。

这和 Karpathy 说的"token 就是思考"一个道理——当你限制输出 token，模型被迫更精准地表达，反而减少了模棱两可的空话。

---

## 实际使用建议

**强烈推荐的场景**：
- 日常 Claude Code 使用（直接省钱省时间）
- API 调用量大的生产环境
- 对响应速度敏感的工具

**注意场景**：
- **学习新概念时**：你可能需要解释，这时候暂时关掉 Caveman
- **代码审查**：你可能需要 AI 解释为什么这样写，不只是结果
- **非英语用户**：穴居人语言是英文风格的压缩，中文的效果可能不一样

---

## 安全性：这个 skill 在做什么？

一个合理的问题：给 AI Agent 安装一个 skill，里面有什么？

Caveman 的实现非常透明，核心就是修改 system prompt 或 skill 指令，告诉模型用简洁模式回答。没有数据上传，没有外部 API 调用，MIT 开源可以完整审计。

---

## 总结

83K Stars 不是意外——它解决了一个真实痛点，方法出乎意料地简单。如果你每天用 Claude Code 或 Codex，装上 Caveman 之后的效果是立竿见影的：速度更快，费用更低，回答更直接。

穴居人有时候说话更有效率。

> **链接**: [GitHub](https://github.com/JuliusBrussee/caveman) · [安装指南](https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Caveman (82,990 ⭐, JavaScript, MIT) is a skill plugin for Claude Code, Codex, Cursor, Windsurf, Cline, Copilot, and 30+ AI coding agents. Install once; the agent drops filler words and answers in compressed caveman-speak. Code, commands, and error messages stay byte-for-byte exact. Technical accuracy: 100%. Output tokens saved: **65% average**. Input tokens: unchanged.

---

## The Core Insight

Most AI agent responses look like:
```
[Polite opener] + [Explanation padding] + [Actual answer] + [Polite closer]
      15%               20%                    55%               10%
```

Caveman strips the 45% filler and keeps the 55% that matters. The model's reasoning capability is unchanged — only its verbosity is constrained.

## Before / After

**Normal Claude (69 tokens)**:
> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."

**Caveman Claude (19 tokens)**:
> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

Same fix. Third of the words. Nothing technical lost.

## Install (3 minutes)

```bash
# Claude Code
git clone https://github.com/JuliusBrussee/caveman ~/.claude/skills/caveman

# Or just tell Claude Code: "install caveman skill"
```
Works with Codex, Cursor, Windsurf, Cline, Copilot, Gemini, and 27+ more. Skill auto-loads on next session.

## Compression Levels

| Level | Style | When |
|---|---|---|
| Grunt | Minimal, commands only | You know the context, just need the code |
| **Caveman** (default) | Concise technical | Daily coding, balanced |
| Verbose Caveman | Keeps more reasoning | Complex problems where you need the why |

## When NOT to Use It

- Learning a new concept (you need the explanation)
- Code review (you want the model to explain reasoning, not just show results)

## What It Does Under the Hood

Caveman modifies the system prompt / skill instructions to constrain verbosity. No external API calls, no data upload. MIT licensed — fully auditable.

**Links**: [GitHub](https://github.com/JuliusBrussee/caveman) · [Install Guide](https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
