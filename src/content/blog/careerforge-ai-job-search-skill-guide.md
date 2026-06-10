---
title: "CareerForge：一行命令搞定 AI 求职全流程，从搜岗到拿 Offer 的完整指南"
description: "开源 AI 求职工具包 CareerForge（GitHub 61 星）提供 6 个串联 Skill：搜岗位、匹配简历、生成简历、写求职信、模拟面试、Offer 决策。一次安装，自然语言触发，帮普通求职者把投递效率提升 3-5 倍。"
titleEn: "CareerForge: One-Command AI Job Search Toolkit — Complete Guide from Search to Offer"
descriptionEn: "Open-source AI job search toolkit CareerForge (61 GitHub stars) provides 6 connected skills: job search, resume matching, resume crafting, cover letters, mock interviews, and offer decisions. One install, natural language triggers — a complete guide for job seekers to 3-5x their application efficiency."
pubDate: 2026-06-10
category: "Tech-Experiment"
tags: ["CareerForge", "AI求职", "Claude Code", "求职工具", "模拟面试", "简历优化", "Skill", "开源工具"]
lang: "zh-CN"
heroImage: "../../assets/images/careerforge-ai-job-search-toolkit.jpg"
---

## 这个工具解决什么问题

求职的本质是一个信息处理和表达问题：找到匹配的岗位、证明自己适合、在面试中表现出来。

但大多数人的求职流程是这样的：在 Boss/LinkedIn/拉钩反复刷岗位 → 改了无数版简历不知道哪版好 → 投出去石沉大海 → 面试前临时抱佛脚 → 面试时被问到没准备的问题。

**CareerForge** 把这整条链路用 6 个 AI Skill 串起来，每一步都有 AI 辅助，而且它们之间自动衔接上下文——不需要你在步骤之间重新解释背景。

---

## 项目信息

- **GitHub**：[rebecha1227-a11y/CareerForge](https://github.com/rebecha1227-a11y/CareerForge)
- **许可证**：MIT（完全开源）
- **支持工具**：Claude Code、Codex、Cursor、Gemini CLI、50+ AI 编程工具
- **安装方式**：一行命令

---

## 6 个 Skill 是什么

### Skill 1：Job Hunt（搜岗位）

- 覆盖 **30+ 招聘平台**，包括国内（Boss、拉钩、猎聘）和海外（LinkedIn、Indeed、Glassdoor）
- 支持 **10 个地区**：中国大陆、美加、英国、欧洲、澳新、日韩、东南亚
- 可过滤**签证担保**岗位（出国求职者必备）
- 支持中英日韩等多语言查询

触发方式：
```
"帮我找工作"
"搜一下上海的 AI 产品经理岗位，薪资 30-50K"
"找有 H1B 担保的美国软件工程师职位"
```

---

### Skill 2：Resume Match（简历匹配度分析）

把你的简历和目标 JD 都发给 AI，它会：
- 给出**量化匹配分数**（满分 100）
- 逐条分析 JD 要求你是否满足
- 指出简历里缺少的关键词
- 建议哪些经历应该重点突出

触发方式：
```
"帮我分析简历匹配度"
"分析一下这个 JD 和我的简历的契合度"
```

---

### Skill 3：Resume Craft（简历生成）

提供 **7 套专业模板**，输出 HTML + PDF：
- Editorial（杂志风格）
- Minimal（极简）
- Sidebar Navy（侧边蓝）
- Sidebar Dark（侧边深色）
- Dark Header（深色标题）
- Clean Teal（清新蓝绿）
- Elegant（优雅）

AI 会根据目标岗位自动调整重点，不是简单套模板，而是根据匹配度分析结果定制化呈现。

触发方式：
```
"帮我做一份简历"
"用 Minimal 模板生成针对这个 JD 优化过的简历"
```

---

### Skill 4：Cover Letter（求职信）

根据你的简历 + 目标 JD + 公司背景生成：
- 定制化求职信
- 招聘平台私信（更适合 Boss 直聘风格的简短版本）
- 可指定语气（正式/亲切/专业）和语言（中/英/日等）

触发方式：
```
"帮我写求职信"
"写一封发给字节跳动 AI 产品经理岗位的求职信"
```

---

### Skill 5：Mock Interview（模拟面试）

这是整个工具包里**最有价值的一环**。它模拟真实三轮面试：

**第一轮：HR 面试**（综合素质、背景匹配、薪资期望）

**第二轮：专业面试**（技术/业务能力、案例分析）

**第三轮：高管面试**（战略思维、文化适配、领导力）

每轮结束后给出：
- **6 维能力雷达图评分**（满分 10）：
  - 专业能力
  - 沟通表达
  - 逻辑思维
  - 应变能力
  - 文化适配
  - 成长潜力
- **逐题细致反馈**：示范答案 + 好的地方 + 不足 + 进阶建议
- **面试题目合集**：所有提问汇总，含核心考查点和得分

比如图中的案例：应聘 AI 产品经理岗位，HR 问"请做一个简短的自我介绍"，AI 不只是说"回答得很好"，而是给出具体建议：

> *"自我介绍控制在 90 秒内，采用'现在→过去→未来'框架；先说你最能做什么（AI 产品经理），再说几个成就（字节运营经历 + AI 项目经验），最后说你为什么选这家。"*

触发方式：
```
"帮我模拟面试"
"模拟字节跳动 AI 产品经理的三轮面试"
"针对这个 JD 帮我做面试准备"
```

---

### Skill 6：Offer Decision（Offer 决策）

拿到多个 Offer 不知道怎么选？这个 Skill 提供：
- **6 维雷达对比**（薪资、成长、稳定性、工作强度、技术栈、地理位置）
- **税后实际到手计算**（不同城市五险一金、个税差别很大）
- **工作生活影响评估**
- **谈判话术脚本**（如何要求提高薪资或调整条款）

---

## 安装：真的超简单

### 方法一：NPX（最推荐）

```bash
npx skills add rebecha1227-a11y/CareerForge -g
```

全局安装，所有支持 Skills 的 AI 工具都能用。

### 方法二：一行 Shell 命令

```bash
curl -sL https://raw.githubusercontent.com/rebecha1227-a11y/CareerForge/main/install.sh | bash
```

### 方法三：告诉你的 AI Agent

直接跟 Claude Code / Codex / Cursor 说：

```
"帮我安装这个工具包：https://github.com/rebecha1227-a11y/CareerForge"
```

AI 会自动下载全部 6 个 Skill，不需要你懂任何技术细节。

---

## 完整求职流程（串联使用）

这 6 个 Skill 设计上是串联的，AI 会自动把上一步的结果带入下一步：

```
第一步：搜岗位
  说："帮我找北京的 AI 产品经理，15-30K，要有股权"
  → 得到：20 个匹配岗位，带链接和薪资范围

第二步：分析匹配度
  说："帮我分析这个岗位和我的简历匹配度"
  → 得到：匹配分 72/100，缺少'数据分析'和'A/B 测试'关键词

第三步：优化简历
  说："根据这个 JD 帮我优化简历"
  → 得到：突出了数据分析经历，补充了 A/B 测试相关表述的新版简历

第四步：写求职信
  说："帮我写针对这家公司的求职信"
  → 得到：引用了公司最近的产品动态，呼应了 JD 里的核心痛点

第五步：模拟面试
  说："帮我模拟这个岗位的三轮面试"
  → 得到：HR + 专业 + 高管三轮，18 道题，每题都有详细反馈

第六步（拿到 Offer）：
  说："我收到了两个 Offer，帮我比较"
  → 得到：六维分析 + 推荐 + 谈判建议
```

关键优势：**AI 记住了你的简历、目标岗位和前几步的上下文**，不需要你每次都重新解释。

---

## 给第一次用 AI 求职工具的人：从哪里开始

如果你没有用过 Claude Code 或类似工具，最简单的起点：

1. **安装 Claude Code**（免费版即可开始）
2. **运行安装命令**：`npx skills add rebecha1227-a11y/CareerForge -g`
3. **第一句话**：`"帮我找一下[你的目标城市]的[你的目标岗位]"`

不需要懂代码，不需要懂 API，直接用自然语言就行。

---

## 实测效果对比

根据图中展示的面试模拟案例（应聘 AI 产品经理，有字节节假数据 + AI 项目经历背景）：

| 评估维度 | 得分 | 主要问题 |
|---------|------|---------|
| 专业能力 | 8/10 | 较强，AI 工具实际使用经验丰富 |
| 沟通表达 | 6/10 | 细节分层不足，结构化表达有提升空间 |
| 逻辑思维 | 7/10 | 框架分析能力好，量化举证偏少 |
| 应变能力 | 5/10 | 被突然提问时有明显停顿 |
| 文化适配 | 8/10 | builder mindset 符合 AI 公司文化 |
| 成长潜力 | 8/10 | 自学能力强，对 AI 产品领域认知清晰 |

**HR 面试最容易被忽视的题目**：
- "请做一个简短的自我介绍"（6/10，大多数人没有用"现在→过去→未来"结构）
- "如果薪资不够，你会怎么办"（4/10，大多数人要么怂要么激进）

这两道题在 AI 工具出现之前，几乎没有人系统练习过。CareerForge 的模拟面试让你在正式面试之前就把这些坑踩完。

---

## 适合谁用

**最适合：**
- 转行/跨行业求职（需要快速构建新领域的简历叙述逻辑）
- 第一次求职（不知道面试是什么套路）
- 海外求职（需要多语言、签证担保、跨平台搜索）
- 同时投多家公司（每家都需要定制化简历和求职信，手写太慢）
- 拿到 Offer 不知道怎么谈判

**不太适合（但也有帮助）：**
- 猎头直推的高端职位（已有内推，不需要广撒网）
- 完全不需要简历的熟人推荐

---

## 可选依赖（用到时再装）

| 功能 | 依赖 |
|------|------|
| 生成 PDF 简历 | Playwright |
| 简历照片处理 | Pillow |
| 导出 Excel 岗位清单 | openpyxl |
| 自动爬取招聘网站 | Chrome 插件（可选） |

这些都不是必须的，基础功能不需要任何额外安装。

---

## 资源汇总

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [rebecha1227-a11y/CareerForge](https://github.com/rebecha1227-a11y/CareerForge) |
| 安装脚本 | `curl -sL https://raw.githubusercontent.com/rebecha1227-a11y/CareerForge/main/install.sh \| bash` |
| NPX 安装 | `npx skills add rebecha1227-a11y/CareerForge -g` |
| 许可证 | MIT |

---

*CareerForge 是开源工具，MIT 协议，免费使用。本文基于 GitHub README 和项目截图整理，未收取任何推广费用。*

<!--EN-->

## CareerForge: AI-Powered Job Search from Search to Offer

**CareerForge** ([rebecha1227-a11y/CareerForge](https://github.com/rebecha1227-a11y/CareerForge), 61 GitHub stars, MIT) is an open-source AI job search toolkit that chains 6 skills across the complete hiring journey — from job discovery to offer negotiation.

### The 6 Skills

| Skill | What it does |
|-------|-------------|
| **Job Hunt** | Searches 30+ platforms across 10 global regions with visa sponsorship filtering |
| **Resume Match** | Scores resume-JD compatibility with keyword gap analysis |
| **Resume Craft** | Generates customized resumes from 7 templates (HTML + PDF) |
| **Cover Letter** | Creates personalized cover letters and recruiter outreach messages |
| **Mock Interview** | Runs 3-round simulated interviews with 6-dimension scoring and per-question feedback |
| **Offer Decision** | Compares offers across 6 dimensions with tax-adjusted salary calculations and negotiation scripts |

### Installation (30 seconds)

**Recommended:**
```bash
npx skills add rebecha1227-a11y/CareerForge -g
```

**Or shell script:**
```bash
curl -sL https://raw.githubusercontent.com/rebecha1227-a11y/CareerForge/main/install.sh | bash
```

**Or tell your AI agent:**
```
"Install this toolkit: https://github.com/rebecha1227-a11y/CareerForge"
```

### The Complete Workflow

Natural language triggers chain automatically:

```
"Help me find jobs" → Job Hunt
"Analyze resume match" → Resume Match  
"Make me a resume" → Resume Craft
"Write a cover letter" → Cover Letter
"Simulate an interview" → Mock Interview
"Compare my offers" → Offer Decision
```

AI preserves context between steps — your resume, target role, and match analysis carry forward automatically.

### Mock Interview: The Most Valuable Feature

The mock interview simulates three rounds (HR / Professional / Executive) and delivers:

- **6-dimension scoring** (Professional Skills, Communication, Logical Thinking, Adaptability, Cultural Fit, Growth Potential)
- **Per-question feedback**: model answer + strengths + gaps + specific improvement advice
- **Common failure points uncovered**: "Tell me about yourself" scores 6/10 for most people due to missing structure; salary negotiation questions score 4/10 on average

From the screenshot example (candidate applying for AI Product Manager):
> *"Limit your self-intro to 90 seconds. Use the Now→Past→Future framework: lead with what you can do (AI PM), add 2-3 concrete achievements, close with why this specific company."*

### Who Should Use This

Best for: career changers, first-time job seekers, overseas applicants, anyone applying to multiple companies simultaneously, and anyone who has an offer but doesn't know how to negotiate.

### Resources

- GitHub: [rebecha1227-a11y/CareerForge](https://github.com/rebecha1227-a11y/CareerForge)
- License: MIT (free, open-source)
- Supports: Claude Code, Codex, Cursor, Gemini CLI, 50+ AI tools
