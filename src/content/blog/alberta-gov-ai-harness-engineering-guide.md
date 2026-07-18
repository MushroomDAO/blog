---
title: "当政府用 AI 军团干掉 40 年技术债：Alberta 开源方法论完全指南"
titleEn: "How a Government Used AI Agents to Kill 40 Years of Technical Debt: Alberta's Open-Source Methodology"
description: "加拿大 Alberta 省政府用 Claude Code + 四色 Agent 军团（红蓝绿黄）扫描了 4.66 亿行代码、对抗 95 个安全控制项，并将一个 25 年的 Java 系统在 4 天内重建完毕。这套 MIT 开源方法论现在任何团队都可以直接拿来用。"
descriptionEn: "The Government of Alberta used Claude Code + four-color agent teams (Red/Blue/Green/Yellow) to scan 466 million lines of code against 95 security controls and rebuild a 25-year-old Java system in four days. This MIT open-source methodology is yours to use today."
pubDate: "2026-07-09"
updatedDate: "2026-07-09"
category: "Tech-Experiment"
tags: ["Claude Code", "AI Agent", "技术债", "安全审计", "开源", "政府AI", "OWASP", "工程化", "开发流程"]
heroImage: "../../assets/images/alberta-gov-ai-harness-engineering-guide-banner.jpg"
---

2026 年 7 月，Anthropic 发布了一篇企业案例，把很多工程师看愣了。

加拿大 Alberta 省政府——管着 27 个省级部门、1280 个应用、3400 个代码仓库——**用 50 个 AI 代理并行运行 20 小时，扫完了 4.66 亿行代码**。这件事如果换成传统方式做，估计需要 6.5 年。

更让人想不到的是：他们把整套方法论开源了。MIT 协议，5 个 GitHub 仓库，21 篇白皮书，你现在就可以 `git clone` 下来用。

---

## 这到底是什么规模的问题

Alberta 省的 IT 债务不是一般的"历史遗留代码"。政府手里的应用跑着税务记录、政府采购数据、社会服务档案。有些系统是 1990 年代手写的 Java，当年建起来花了 5 个月，现在改一下要踩几十个坑。

> "我们不是在做年度审计，是在还 40 年的账。" —— Alberta 省技术与创新部长 Nate Glubish

**传统做法的问题：**
- 人工扫描代码太慢，4.66 亿行代码需要 6.5 年
- 静态分析工具只找已知漏洞模式
- 修复前没有测试 → 修了这里坏那里
- 两个开发者用同一个 AI 工具，输出结果差异很大（概率模型的天然缺陷）

Alberta 团队的解法，是构建了一套叫做 **"Harness（马具）"** 的约束框架，把 AI 的创造力套上缰绳，让输出变得可预期、可重复、可审计。

---

## 核心架构：Harness 是什么

Harness 不是一个工具，是一套让 AI 输出稳定的**结构化约束**。

Alberta 发现：两个工程师用同一个 AI 模型做同一件事，结果差异可能非常大。Harness 解决的正是这个问题——它把优秀工程师积累了 10-20 年的经验，**编码成 AI 能直接执行的指令集**。

```
Harness 的四个组成部分：

CLAUDE.md            ← 规则入口：这是什么项目、能做什么、绝对不能做什么
.claude/skills/      ← 技能文件：每种任务类型的操作手册
template/            ← 代码模板：预先解决了 100+ 个标准化决策
standards/           ← 质量标准：安全、无障碍、代码规范、测试覆盖率
```

每次 Claude Code 启动，它先读 `CLAUDE.md`。这个文件只说：项目是什么、标准是什么、什么可以改、什么不能动。所有的"会话状态"不是靠 AI 记忆的，是靠这个文件写死的。

---

## 四色 Agent：红蓝绿黄是干什么的

这是整套方法论里最有意思的部分。Alberta 构建了四支独立的审查 Agent，每支负责不同维度：

### 🟢 Green Team — 代码卫生官

**任务：** 代码质量审查，不留情面

具体检查内容：
- 依赖项健康度（有没有已知漏洞的包、`package-lock.json` 缺失等）
- Secrets 泄露（代码里硬编码了 API key？）
- 测试覆盖率缺口
- CI/CD 流水线漏洞
- 运行时 Bug（空指针、类型不匹配、边界条件）
- 代码规范合规性

运行方式：`/greenteam`，输出报告到 `deliverables/`。**确定性检查**，没有模糊判断。

---

### 🟡 Yellow Team — AI 味道探测器

**任务：** 审查文档和对外文字，剔除 AI 生成的痕迹

12 条规则，包括：
- 检测 em-dash 滥用（AI 写作的典型特征）
- 检测"虽然 X，但 Y"结构的过度使用
- 检测被禁用的词汇列表（government-approved writing standards）
- 检测分词尾巴（participial tails）
- 检测过于整齐的三点列表结构

运行方式：`/yellowteam path/to/doc.md`，输出 AI 气味报告。政府文件必须过这一关才算完成。

---

### 🔴 Red Team — 攻击模拟器

**任务：** 从外部视角攻击这个应用

三阶段流程：
1. **侦察（Recon）**：扫描暴露的端点、错误信息、版本信息泄露
2. **代码分析**：识别可利用的漏洞模式（SQL 注入点、不当的身份验证逻辑）
3. **PoC + 修复建议**：写出具体的攻击路径，附上精确的 `file:line` 引用

> 这就是 Anthropic 案例里说的"Claude 引用精确文件行号"——Red Team 的输出必须精确到代码位置，不接受模糊描述。

运行方式：`/redteam`，输出到 `deliverables/`。

---

### 🔵 Blue Team — 防御体系构建者

**任务：** 按照国际安全标准评估应用的防御能力

覆盖标准：
- **OWASP ASVS L2**（应用安全验证标准）
- **CAS**（Canadian Cybersecurity Architecture Standard）
- 威胁建模（Threat Modeling）
- 完整的 OWASP Top 10 走查

运行方式：`/blueteam`，生成带优先级排序的修复计划，同样精确到文件和行号。

---

## 95 个安全控制项：每次提交都要过

这 95 个控制项分布在四色 Agent 里，每次代码提交都会自动运行。拆开来看：

| Agent | 类型 | 控制项来源 |
|-------|------|-----------|
| Blue | 确定性 + 概率性 | OWASP ASVS L2, CAS |
| Red | 概率性 | 实际攻击面分析 |
| Green | 确定性 | 代码质量规范 |
| Yellow | 确定性 | 政府写作标准 |

**关键点**：确定性检查（deterministic）的结果是固定的，有就是有，没有就是没有。概率性检查（probabilistic）是 Claude 的判断，输出包含置信度评分。两类检查的报告格式不同，工程师处理方式也不同。

---

## 两阶段扫描：省政府是怎么扫 4.66 亿行代码的

```
阶段一：规则引擎扫描
  ├── 对每个仓库运行已知漏洞模式匹配
  ├── 输出：初步标记列表（文件路径 + 漏洞类型 + 代码行号）
  └── 速度快，覆盖广，但只找已知模式

阶段二：Claude 深度审查
  ├── 对阶段一标记的位置做上下文分析
  ├── Claude 输出：精确的 file:line 引用 + 漏洞确认 + 修复建议
  └── 找到了传统工具漏掉的问题
```

50 个 Agent 并行运行，每个 Agent 处理一部分仓库。用的是：
- **Claude Opus**：处理需要长链推理的任务（整体架构分析、威胁建模）
- **Claude Sonnet**：处理并行运行的深度扫描（便宜、快、可大量并发）

---

## 开源仓库：你现在就能用的部分

Alberta 开源了 5 个仓库（MIT 协议）：

```
GovAlta/COMMON-HARNESS          ← 核心！含四色 Agent + 8 阶段流水线 + 模板
GovAlta/THE-VELOCITY-WHITE-PAPERS  ← 白皮书网站本身（含 AI 驱动的 CMS）
GovAlta/PRONGHORN-RED           ← AI 设计工厂：React + Supabase 版
GovAlta/PRONGHORN-BLUE          ← AI 设计工厂：Azure 对齐版
GovAlta/VELOCITY-GAME-ENGINE    ← AI 时代的项目管理工具
```

重点在 `COMMON-HARNESS`。

---

## 上手 COMMON-HARNESS：三步走

### 第一步：克隆到你的项目目录

```bash
git clone https://github.com/GovAlta/COMMON-HARNESS my-project
cd my-project

# 在这个目录里打开 Claude Code
# 所有 skills、hooks、standards 自动加载
```

### 第二步：从模板初始化应用

```
# Claude Code 里执行
/build fullstack     # 生成完整应用：Vue 3 + Express + Postgres
/build frontend      # 只要前端
/build backend       # 只要后端
```

模板预置决策（你不用再做这些选择）：
- 身份认证：单点登录（SSO）
- 输入验证：已集成
- 密钥管理：已配置
- 日志和防护：已启用
- 无障碍标准（WCAG 2.1 AA）：已内置

### 第三步：走 8 阶段流水线

```
/phase1-requirements    # 需求文档 → 结构化 FR/NFR
/phase2-planning        # 任务分解 + 关键路径
/phase3-architecture    # 系统设计 + ADR + 威胁模型
/phase4-prototyping     # 验证技术路径（tracer-bullet）
/phase5-development     # 实际开发（调用 /build + 31 个构建指南）
/phase6-user-testing    # 测试计划 + 问题分类
/phase7-user-acceptance # UAT 脚本 + 利益相关方确认
/phase8-deployment      # 部署手册 + 烟雾测试 + 发布说明
```

**每个阶段都有硬性前置条件**：没有完成上一阶段的产出，下一个阶段直接 block，不让跳过。

---

## 运行安全审查：四色 Agent 实战

以一个已有项目为例：

```bash
# 1. 把 COMMON-HARNESS 的 .claude/ 目录复制到你的项目
cp -r /path/to/COMMON-HARNESS/.claude ./

# 2. 在 Claude Code 里运行
```

在 Claude Code 对话框里：

```
# 代码质量审查（deterministic，几分钟）
/greenteam

# 写作/文档审查（deterministic）
/yellowteam docs/README.md

# 安全攻击面分析（概率性，较耗时）
/redteam

# 防御合规评估（OWASP ASVS L2）
/blueteam
```

报告输出到 `.ai/reports/` 和 `deliverables/`，格式统一，每条发现都有 `file:line` 精确定位。

---

## 不用完整流水线，只用 Agent 审查也可以

如果你已有项目，只是想加入四色 Agent 做持续安全审查：

```
.claude/
├── skills/
│   ├── blueteam/         ← 复制这四个
│   ├── redteam/
│   ├── greenteam/
│   └── yellowteam/
└── standards/            ← 可选，但建议带上
```

建议在 CI/CD 里挂上 Green Team 和 Yellow Team（确定性，快），Red Team 和 Blue Team 在 PR 前或重大发布前手动触发。

---

## Alberta 数据：这套方法真实跑出来的结果

| 指标 | 数值 |
|------|------|
| 扫描代码量 | 4.66 亿行 |
| 完成时间 | 20 小时（传统方法估计 6.5 年） |
| 并行 Agent 数量 | 约 50 个 |
| 每次提交检查项 | ~95 个安全控制 |
| 一个 Level 3 培训班（100 人，6 天）产出 | 560 个通过安全审查的应用 |
| 一个 25 年 Java 系统的重建时间 | 4-5 天（原本建了 5 个月） |

---

## 为什么叫"Harness（马具）"

Deputy Minister Janak Alford 的比喻很准：

> "凭借 Arthur C. Clarke 第三定律的灵感——任何足够先进的技术都与魔法无异——我认为，任何足够完善的模板都与代码无异。**最好的 Harness 就是代码本身。**"

你不能用 AI 写 Harness（会有"复印机问题"，每一代副本都会降级）。你需要人工打磨每一个技能文件，用真实项目测试，反复迭代。但一旦你的 Harness 成熟了，它就像一位 20 年经验的工程师坐在每个人旁边，实时纠偏。

---

## 适合谁用

**直接能用的场景：**
- 已经在用 Claude Code 的开发团队
- 需要通过安全审计的政府/金融/医疗项目
- 想让 AI 代码质量从"随机"变"可重复"的团队
- 正在做遗留系统现代化改造的项目

**需要适配的部分：**
- 技术栈（默认是 Vue 3 + Node.js + Postgres；换成你的栈需要修改 template/）
- 合规标准（Blue Team 默认是 OWASP + Canadian CAS；其他国家/行业标准需要调整 skill 文件）
- 写作风格（Yellow Team 的规则是政府英文写作标准；可以替换成你的技术写作规范）

---

## 资源

- [GovAlta/COMMON-HARNESS](https://github.com/GovAlta/COMMON-HARNESS) — 核心 Harness，MIT
- [GovAlta/PRONGHORN-RED](https://github.com/GovAlta/PRONGHORN-RED) — AI 设计工厂，MIT
- [GovAlta/VELOCITY-GAME-ENGINE](https://github.com/GovAlta/VELOCITY-GAME-ENGINE) — AI 项目管理，MIT
- [thevelocitywhitepapers.com](https://thevelocitywhitepapers.com) — 21 篇白皮书（含音频版）
- [Anthropic 案例研究](https://www.anthropic.com/news/alberta-government-claude-cybersecurity) — 官方案例
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) — Agent 构建基础

© 2026 Author: Mycelium Protocol

<!--EN-->

## How a Government Used AI Agents to Kill 40 Years of Technical Debt: Alberta's Open-Source Methodology

In July 2026, Anthropic published a case study that stopped a lot of engineers cold.

The Government of Alberta — managing 27 provincial ministries, 1,280 applications, and 3,400 code repositories — **deployed 50 AI agents in parallel for 20 hours and scanned 466 million lines of code**. The same work through traditional means would have taken an estimated 6.5 years.

The kicker: they open-sourced the entire methodology. MIT license, five GitHub repositories, 21 white papers, `git clone` and go.

---

### The Problem at Scale

Alberta's technical debt isn't typical. The province's systems hold tax records, procurement data, and social services case files. Some applications are hand-coded Java from the 1990s — one subsidy portal took five months to build 25 years ago.

Traditional scanning tools only catch known patterns. Human audits can't scale to 466 million lines. And when two developers prompt the same AI model for the same task, the outputs diverge unpredictably — a catastrophic property for government systems where repeatability and auditability are non-negotiable.

Alberta's answer was a **Harness**: a structured constraint framework that channels AI capability into repeatable, auditable outputs. Think of it as codifying 10-20 years of senior engineering judgment into instruction sets the AI can execute deterministically.

---

### Harness Architecture

```
CLAUDE.md            ← Session entry point: what this project is, what the agent may/must not do
.claude/skills/      ← Per-task playbooks loaded on demand
template/            ← Pre-decided application scaffold (100+ settled decisions)
standards/           ← Security, accessibility, testing, naming conventions
```

Every Claude Code session opens with `CLAUDE.md`. It's short and opinionated: what the project is, which standards apply, what can change, what is off-limits. Session state isn't in AI memory — it's written down.

Skills auto-discover and load only when the task matches. Each skill is a narrow, opinionated playbook for one kind of work: how to write a database migration, how to run a security audit, how to review prose for AI tells. Minimal prose, maximum specificity.

---

### The Four-Color Agent Teams

Four specialized review agents ship with the harness and gate every application:

**🟢 Green Team — Code Hygiene**
Runs deterministic checks: dependency vulnerabilities, hardcoded secrets, test coverage gaps, CI/CD misconfigurations, runtime bugs. Output: `deliverables/greenteam-report.md`. Run with `/greenteam`.

**🟡 Yellow Team — AI-Smell Detector**
Audits documentation and public-facing prose against 12 rules covering em-dash overuse, "not X but Y" constructions, banned vocabulary, participial tails, and other AI-prose markers. Government text must pass this before publishing. Run with `/yellowteam`.

**🔴 Red Team — Attacker Simulator**
Three-stage offensive analysis: reconnaissance (exposed endpoints, version leakage), code analysis (injectable inputs, broken auth logic), then a PoC attack path with exact `file:line` references. Run with `/redteam`.

**🔵 Blue Team — Defensive Assessor**
Maps the application against OWASP ASVS Level 2 and the Canadian Cybersecurity Architecture Standard (CAS). Produces a ranked remediation plan with precise file references. Run with `/blueteam`.

Together, they cover roughly **95 security controls on every pass**.

---

### The Two-Stage Scanning Pipeline

How Alberta scanned 466 million lines in 20 hours:

```
Stage 1 — Rules Engine
  ├── Known-pattern matching across all repositories
  ├── Output: flags with file path + vulnerability type + line number
  └── Fast, broad coverage, catches known patterns

Stage 2 — Claude Deep Review
  ├── Context-aware analysis of Stage 1 flags
  ├── Output: confirmed findings with exact file:line, remediation plan
  └── Catches what automated tools missed
```

50 agents ran in parallel — Claude Opus for long-horizon reasoning (architecture analysis, threat modeling), Claude Sonnet for the parallel scans (fast, cheap, highly concurrent).

---

### Getting Started with COMMON-HARNESS

```bash
git clone https://github.com/GovAlta/COMMON-HARNESS my-project
cd my-project
# Open Claude Code here — skills, hooks, standards auto-discover
```

Scaffold an application from the pre-decided template:
```
/build fullstack    # Vue 3 + Express + Postgres, SSO, WCAG 2.1 AA pre-wired
/build frontend     # client only
/build backend      # server only
```

Walk the 8-phase lifecycle (each phase hard-blocks without the prior phase's deliverable):
```
/phase1-requirements → /phase2-planning → /phase3-architecture → /phase4-prototyping
→ /phase5-development → /phase6-user-testing → /phase7-user-acceptance → /phase8-deployment
```

Run security review on any project:
```
/greenteam      # deterministic, minutes
/yellowteam     # deterministic, documents only
/redteam        # probabilistic, attack surface analysis
/blueteam       # probabilistic, OWASP ASVS L2 compliance
```

---

### Alberta's Results

| Metric | Value |
|--------|-------|
| Code scanned | 466 million lines |
| Time to complete | 20 hours (traditional estimate: 6.5 years) |
| Parallel agents | ~50 |
| Security controls per pass | ~95 |
| 100-person Level 3 cohort output (6 days) | 560 security-cleared applications |
| Legacy Java subsidy portal rebuilt | 4–5 days (original build: 5 months) |

---

### Resources

- [GovAlta/COMMON-HARNESS](https://github.com/GovAlta/COMMON-HARNESS) — Harness, MIT
- [GovAlta/PRONGHORN-RED](https://github.com/GovAlta/PRONGHORN-RED) — AI design factory, MIT
- [GovAlta/VELOCITY-GAME-ENGINE](https://github.com/GovAlta/VELOCITY-GAME-ENGINE) — AI-era project management, MIT
- [thevelocitywhitepapers.com](https://thevelocitywhitepapers.com) — 21 white papers with audio narration
- [Anthropic case study](https://www.anthropic.com/news/alberta-government-claude-cybersecurity)

© 2026 Author: Mycelium Protocol
