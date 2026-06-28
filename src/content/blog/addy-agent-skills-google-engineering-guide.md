---
title: "Agent Skills：Google 工程师 67K 星，24 Skill + 8 命令覆盖完整研发链路"
titleEn: "Addy's Agent Skills: Google Engineer's 67K-Star AI Coding Skill Pack — Google Engineering Practices Baked In"
description: "Google Chrome Engineering Manager Addy Osmani 开源 agent-skills（67K⭐），将谷歌软件工程规范（Hyrum定律、Beyonce规则、Chesterton栅栏等）封装为 24 个 Skill + 8 条命令，覆盖 DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP 完整开发链路，兼容 Claude Code / Cursor / Gemini CLI / Windsurf，两行命令即可安装。"
descriptionEn: "Google Chrome Engineering Manager Addy Osmani open-sources agent-skills (67K stars) — 24 skills + 8 slash commands encoding Google's software engineering norms (Hyrum's Law, Beyonce Rule, Chesterton's Fence) across the full DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP lifecycle. Compatible with Claude Code, Cursor, Gemini CLI, Windsurf. Two commands to install."
pubDate: "2026-06-28"
updatedDate: "2026-06-28"
category: "Tech-News"
tags: ["AI编程", "Claude Code", "Gemini CLI", "工程规范", "开源工具", "Cursor", "Skill", "Google工程实践"]
heroImage: "../../assets/images/addy-agent-skills-google-engineering-guide-banner.jpg"
---

> **一句话定位**：这是目前最系统的 AI 编程 Skill 包——Addy Osmani（Google Chrome Engineering Manager）把谷歌内部软件工程规范（《Software Engineering at Google》里的原则）直接烤进 AI Agent 的工作流，让 AI 编程从「只管速度」变成「按生产级标准交付」。

---

## 项目信息

GitHub：https://github.com/addyosmani/agent-skills （67,321 ⭐，MIT 开源）

作者：Addy Osmani — Google Chrome Engineering Manager（著有《Learning JavaScript Design Patterns》《Image Optimization》等）

---

## 为什么 AI 编程需要这个？

AI coding agent 有一个根本性的偏差：**默认走最短路径**。

这意味着：
- 跳过写 Spec，直接开始写代码
- 「先实现，测试以后再说」
- Code Review 点到为止，不做安全检查
- 部署前不做性能验证
- 没有可观测性配套，上线就是盲飞

这些习惯在原型阶段没问题，但会在生产环境里留下技术债。

**Agent Skills 的解法**：把高级工程师的工作纪律和判断力编码为结构化 Skill，让 AI Agent 在每个开发阶段始终遵循同样的质量标准。每个 Skill 不只是文档，而是**工作流**——有步骤、有检查点、有退出条件。

---

## 完整管线：8 条命令

```
  DEFINE          PLAN           BUILD          VERIFY         REVIEW          SHIP
 ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐
 │ Idea │ ───▶ │ Spec │ ───▶ │ Code │ ───▶ │ Test │ ───▶ │  QA  │ ───▶ │  Go  │
 │Refine│      │  PRD │      │ Impl │      │Debug │      │ Gate │      │ Live │
 └──────┘      └──────┘      └──────┘      └──────┘      └──────┘      └──────┘
  /spec          /plan          /build        /test         /review       /ship
```

| 命令 | 阶段 | 核心原则 |
|---|---|---|
| `/spec` | DEFINE | 先写 Spec，再写代码 |
| `/plan` | PLAN | 小而原子的任务拆解 |
| `/build` | BUILD | 一次一个薄切片 |
| `/test` | VERIFY | 测试是证明，不是额外工作 |
| `/review` | REVIEW | 每次合并前改善代码健康度 |
| `/webperf` | REVIEW | 先测量，再优化 |
| `/code-simplify` | REVIEW | 清晰优先于聪明 |
| `/ship` | SHIP | 越快越安全（配合 feature flag）|

**进阶用法**：`/build auto`——生成计划后全程自动执行，你只需批准一次计划，AI 自动逐任务实现并提交。每个任务仍然是测试驱动 + 单独提交，遇到失败或高风险步骤自动暂停。

技能也会**自动触发**——设计 API 会激活 `api-and-interface-design`，构建 UI 会激活 `frontend-ui-engineering`，无需手动调用。

---

## 24 个 Skill 详解

### 元技能（1 个）

**`using-agent-skills`**：入口技能，根据当前任务自动匹配最合适的 Skill，并定义全局运作规则。每次会话开始时加载。

### Define 阶段（3 个）

| Skill | 做什么 | 何时用 |
|---|---|---|
| `interview-me` | 一次一问，从用户那里提取真实需求而非表面需求，直到 95% 置信度 | 任务描述模糊、用户说「问我」或「帮我想清楚」|
| `idea-refine` | 结构化发散 / 收敛思维，把模糊概念转化为具体方案 | 有粗略概念但需要探索 |
| `spec-driven-development` | 在写任何代码之前，先写覆盖目标、命令、结构、代码风格、测试、边界的 PRD | 启动新项目、新功能或重大变更 |

**核心原则**：Spec Before Code。没有 Spec 的代码是技术债的起点。

### Plan 阶段（1 个）

| Skill | 做什么 |
|---|---|
| `planning-and-task-breakdown` | 把 Spec 拆解成带验收标准和依赖顺序的小型可验证任务 |

**核心原则**：任务小而原子——每个任务应能被独立实现、测试、提交。

### Build 阶段（7 个）

| Skill | 做什么 | 核心工程原则 |
|---|---|---|
| `incremental-implementation` | 薄垂直切片实现，用 feature flag，每个切片都测试并提交 | 可回滚的安全默认值 |
| `test-driven-development` | Red-Green-Refactor，测试金字塔（80/15/5），DAMP over DRY | Beyonce Rule：改变行为就改变测试 |
| `context-engineering` | 在正确时间给 Agent 喂正确信息（rules 文件、context packing、MCP 集成）| 防止输出质量下滑 |
| `source-driven-development` | 每个框架决策都引用官方文档，标注未验证内容 | 消除 AI 幻觉的框架知识 |
| `doubt-driven-development` | 对每个非平凡决策做对抗性新上下文评审，CLAIM→EXTRACT→DOUBT→RECONCILE→STOP | 高风险、生产、安全、不可逆操作 |
| `frontend-ui-engineering` | 组件架构、设计系统、状态管理、响应式设计、WCAG 2.1 AA 无障碍 | 构建或修改用户界面时 |
| `api-and-interface-design` | 合约优先设计，Hyrum 定律，One-Version Rule，错误语义，边界验证 | 设计 API、模块边界或公共接口 |

**特别值得说的几个原则：**

- **Beyonce Rule**（测试）：「If you liked it you should have put a test on it」——改变行为时必须更新测试，测试是代码行为的证明
- **Hyrum's Law**（API 设计）：一旦有足够多用户，所有可观测到的行为都会被依赖，不论文档怎么说——API 设计必须考虑所有可观测行为
- **Doubt-Driven Development**：特别有价值——强制 AI 用新的上下文审查自己的重要决策，防止「看起来对就当作对了」

### Verify 阶段（2 个）

| Skill | 做什么 |
|---|---|
| `browser-testing-with-devtools` | Chrome DevTools MCP 获取实时运行时数据——DOM 检查、控制台日志、网络追踪、性能分析 |
| `debugging-and-error-recovery` | 五步分诊法：重现 → 定位 → 简化 → 修复 → 保护；停线规则，安全回退 |

### Review 阶段（4 个）

| Skill | 核心方法 |
|---|---|
| `code-review-and-quality` | 五轴评审，单次 PR ~100 行，严重性标签（Nit/Optional/FYI）|
| `code-simplification` | Chesterton 栅栏（删代码前先理解为什么存在）、Rule of 500，保持行为不变 |
| `security-and-hardening` | OWASP Top 10 预防，认证模式，secrets 管理，依赖审计，三层边界系统 |
| `performance-optimization` | 先测量：Core Web Vitals 目标，分析工作流，bundle 分析，反模式检测 |

**Chesterton 栅栏规则**：在理解一段代码为什么存在之前，不要删除它。AI 经常为了「简化」而破坏隐藏的不变量，这个规则阻止这种行为。

### Ship 阶段（6 个）

| Skill | 核心方法 |
|---|---|
| `git-workflow-and-versioning` | Trunk-based 开发，原子提交，~100 行变更粒度，commit-as-save-point 模式 |
| `ci-cd-and-automation` | Shift Left（越早发现越便宜），feature flag，质量门管道，失败反馈循环 |
| `deprecation-and-migration` | 代码即负债的思维，强制 vs 建议废弃，迁移模式，僵尸代码清除 |
| `documentation-and-adrs` | 架构决策记录（ADR），API 文档，行内文档标准——记录「为什么」而非「是什么」|
| `observability-and-instrumentation` | 结构化日志，RED 指标，OpenTelemetry 追踪，症状型告警——边构建边埋点 |
| `shipping-and-launch` | 发布前检查表，feature flag 生命周期，分阶段 rollout，回滚流程，监控配置 |

---

## 4 个专家 Agent 角色

除了 Skill 之外，还有 4 个预配置的专家 Agent，可以单独召唤做定向审查：

| Agent | 角色 | 视角 |
|---|---|---|
| `code-reviewer` | Senior Staff Engineer | 五轴代码评审，「这代码一个 Staff Engineer 会批准吗？」|
| `test-engineer` | QA 专家 | 测试策略、覆盖分析、Prove-It 模式 |
| `security-auditor` | 安全工程师 | 漏洞检测、威胁建模、OWASP 评估 |
| `web-performance-auditor` | Web 性能工程师 | Core Web Vitals 审计，Quick/Deep 两种模式 |

用法示例：
```
# 调用安全审计
让 security-auditor 检查这段认证代码

# 调用性能审计
/webperf
```

---

## 安装与使用

### Claude Code（推荐，最完整支持）

**方式一：Plugin Marketplace（一键安装）**
```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

**方式二：本地克隆**
```bash
git clone https://github.com/addyosmani/agent-skills.git
claude --plugin-dir /path/to/agent-skills
```

安装后，直接使用 8 条斜线命令（`/spec`、`/plan`、`/build`……）或描述任务让 AI 自动匹配 Skill。

### Gemini CLI

```bash
# 从 GitHub 直接安装
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# 本地克隆安装
git clone https://github.com/addyosmani/agent-skills.git
gemini skills install ./agent-skills/skills/
```

### Cursor

把任意 `SKILL.md` 复制到 `.cursor/rules/`，或把整个 `skills/` 目录加入 Cursor 规则配置。

### Antigravity CLI

```bash
# 从 GitHub 安装
agy plugin install https://github.com/addyosmani/agent-skills.git

# 本地克隆安装
git clone https://github.com/addyosmani/agent-skills.git
agy plugin install ./agent-skills
```

### Windsurf

把 Skill 内容加入 Windsurf 规则配置（见 `docs/windsurf-setup.md`）。

---

## Skill 的工作原理：三个核心设计选择

### 1. 工作流而非文档

每个 SKILL.md 的结构：
```
┌─────────────────────────────────────────────────┐
│  SKILL.md                                       │
│  ┌─ Frontmatter ─────────────────────────────┐  │
│  │ name: lowercase-hyphen-name               │  │
│  │ description: Guides agents through [task] │  │
│  └───────────────────────────────────────────┘  │
│  Overview    → 这个 Skill 做什么               │
│  When to Use → 触发条件                        │
│  Process     → 分步工作流                      │
│  Rationalizations → 借口 + 反驳               │
│  Red Flags   → 出问题的信号                    │
│  Verification → 证据要求                      │
└─────────────────────────────────────────────────┘
```

### 2. 反合理化表（Anti-Rationalization）

每个 Skill 都内置了一张「借口-反驳」对照表。AI Agent 跳过步骤时总有看似合理的借口，这张表强制处理这些借口：

| 常见借口 | 记录在案的反驳 |
|---|---|
| 「先实现，测试以后加」| 无测试的代码无法证明正确性，测试债比技术债更贵 |
| 「这个改动太小，不需要 Spec」| 80% 的 bug 来自「小改动」 |
| 「看起来是对的」| 「看起来对」永远不是证据，测试是 |
| 「性能优化可以以后做」| 性能问题被合并后修复成本 10 倍于预防 |

### 3. 渐进式加载（Progressive Disclosure）

`SKILL.md` 是入口，只在需要时才加载配套的 references/ 文件，保持 token 消耗最小化。不是一次把所有内容塞进 context，而是按需加载。

---

## 内置的谷歌工程实践

Skills 中直接嵌入了来自《Software Engineering at Google》和谷歌工程规范的原则：

| 原则 | 来源 | 应用位置 |
|---|---|---|
| **Hyrum's Law** | Google SWE 内部传统 | `api-and-interface-design` |
| **Beyonce Rule** | Google Testing Blog | `test-driven-development` |
| **Chesterton's Fence** | 哲学→Google 工程文化 | `code-simplification` |
| **Trunk-Based Development** | Google DevOps 研究 | `git-workflow-and-versioning` |
| **Shift Left** | DevOps 最佳实践 | `ci-cd-and-automation` |
| **Code as Liability** | Google SWE 文化 | `deprecation-and-migration` |
| **Test Pyramid (80/15/5)** | Google Testing 框架 | `test-driven-development` |
| **Core Web Vitals** | Google Chrome 团队 | `performance-optimization` |
| **OWASP Top 10** | 安全工程标准 | `security-and-hardening` |
| **RED Metrics** | Google SRE 实践 | `observability-and-instrumentation` |

这些不是「在 README 里提一下」的原则，而是被直接编码进 AI 的分步工作流里。

---

## 实际使用建议

### 快速开始（推荐路径）

1. 安装到 Claude Code（两行命令）
2. 新项目开始时先用 `/spec` 写需求文档
3. 用 `/plan` 拆分任务
4. 用 `/build` 逐任务实现（或 `/build auto` 全自动）
5. 用 `/review` 在合并前做质量检查
6. 用 `/ship` 管理发布

### 最有价值的几个 Skill

**初学者最先感受到价值的：**
- `spec-driven-development`：强制在写代码前先想清楚要做什么
- `test-driven-development`：从「写完再测」改变为「测试即证明」
- `code-review-and-quality`：五轴评审框架，让 PR Review 有结构可循

**进阶用户最喜欢的：**
- `doubt-driven-development`：生产环境变更前的强制自我审查，防止 AI 的自信盲区
- `observability-and-instrumentation`：边写代码边埋监控，而不是出问题了再加
- `shipping-and-launch`：发布前检查表，feature flag 生命周期管理

### 对不同工具用户的建议

| 工具 | 建议 |
|---|---|
| Claude Code 用户 | Plugin Marketplace 安装，使用 `/spec`→`/plan`→`/build auto` 自动化流程 |
| Cursor 用户 | 把最常用的 3-4 个 SKILL.md 复制到 `.cursor/rules/` |
| Gemini CLI 用户 | `gemini skills install` 一键安装，命令与 Claude Code 相同 |
| 多工具混用 | 统一用 GitHub 克隆，各工具从同一份 skills/ 目录加载 |

---

## 资源汇总

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/addyosmani/agent-skills |
| Claude Code 安装文档 | `docs/claude-code-setup.md` |
| Cursor 安装文档 | `docs/cursor-setup.md` |
| Gemini CLI 安装文档 | `docs/gemini-cli-setup.md` |
| Agent 角色文档 | `docs/agents.md` |
| Skill 格式规范 | `docs/skill-anatomy.md` |
| 与其他 Skill 包对比 | `docs/comparison.md` |
| AgentSkills 生态 | https://agentskills.io |

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **In one line**: Addy Osmani (Google Chrome Engineering Manager) baked Google's software engineering norms (Hyrum's Law, Beyonce Rule, Chesterton's Fence, trunk-based dev) into 24 AI agent skills + 8 slash commands, covering the complete DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP lifecycle. 67K stars. MIT. Two commands to install.

---

## What This Solves

AI coding agents default to the shortest path — skipping specs, tests, security reviews, and the practices that make software reliable. Agent Skills gives agents structured workflows enforcing the same discipline senior engineers bring to production code.

**Key design principle**: these aren't reference docs you tell AI to read — they're step-by-step workflows agents follow, with checkpoints, exit criteria, and anti-rationalization tables that counter common excuses for skipping steps.

---

## The 8 Commands

| Command | Phase | Principle |
|---|---|---|
| `/spec` | DEFINE | Spec before code |
| `/plan` | PLAN | Small, atomic tasks |
| `/build` | BUILD | One vertical slice at a time |
| `/test` | VERIFY | Tests are proof |
| `/review` | REVIEW | Improve code health before merge |
| `/webperf` | REVIEW | Measure before you optimize |
| `/code-simplify` | REVIEW | Clarity over cleverness |
| `/ship` | SHIP | Faster is safer (with feature flags) |

Pro tip: `/build auto` — approve the plan once, then it runs autonomously through all tasks.

---

## 24 Skills at a Glance

**Define (3)**: `interview-me` · `idea-refine` · `spec-driven-development`

**Plan (1)**: `planning-and-task-breakdown`

**Build (7)**: `incremental-implementation` · `test-driven-development` · `context-engineering` · `source-driven-development` · `doubt-driven-development` · `frontend-ui-engineering` · `api-and-interface-design`

**Verify (2)**: `browser-testing-with-devtools` · `debugging-and-error-recovery`

**Review (4)**: `code-review-and-quality` · `code-simplification` · `security-and-hardening` · `performance-optimization`

**Ship (6)**: `git-workflow-and-versioning` · `ci-cd-and-automation` · `deprecation-and-migration` · `documentation-and-adrs` · `observability-and-instrumentation` · `shipping-and-launch`

---

## Install (Claude Code)

```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

**Gemini CLI:**
```bash
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills
```

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution.
