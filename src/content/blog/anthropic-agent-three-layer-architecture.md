---
title: "Anthropic 的三层 Agent 架构：从一个 Claude 到一支 Agent 团队"
titleEn: "Anthropic's Three-Layer Agent Architecture: From One Claude to an Agent Team"
description: "Sequoia Podcast 访谈 Anthropic 平台负责人揭示了其内部 Agent 架构的三层设计：知识层、执行层、协同层。很多人还在研究怎么写 Prompt，Anthropic 已经在研究如何让 Agent 团队协同工作，本文结合官方文档拆解每一层的构件和实现方式。"
descriptionEn: "A Sequoia Podcast interview with Anthropic's platform lead revealed their three-layer agent architecture: Knowledge, Execution, and Coordination. While most are still learning to write prompts, Anthropic is already orchestrating teams of agents. This article breaks down each layer with official documentation and practical examples."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["AI Agent", "Anthropic", "多智能体", "MCP", "Claude Code", "架构设计", "Token Jobs"]
heroImage: "../../assets/images/anthropic-agent-three-layer-architecture-banner.jpg"
---

> 来源：Sequoia Capital「Training Data」Podcast，Anthropic 平台负责人访谈。字幕截图显示：*"You are responsible for building Anthropic's platform — important, if not, the most important developer platform in the world."*

---

## 一句话击中要害

> 很多人还在研究怎么写 Prompt，Anthropic 已经在研究如何让 **Agent 团队协同工作**。

这不是夸张，而是 Anthropic 平台负责人在接受 Sequoia 访谈时说的。她描述了一个 Anthropic 内部已在运行的系统：**5 种不同职责的 Token Jobs，当这些能力开放给开发者，就能自由组合出数以万计的 Agent 工作流。**

这背后的底层设计，是一套三层 Agent 架构。

---

## 三层架构全景

```
┌─────────────────────────────────────────────────┐
│         第三层：协同层（Coordination Layer）        │
│    多 Agent 分工 · Token Jobs · Meta-Harness      │
│    规划 → 执行 → 评审 → 优化 → 自我迭代           │
├─────────────────────────────────────────────────┤
│          第二层：执行层（Execution Layer）          │
│    Harness · Managed Infrastructure · Sandboxes  │
│    改代码 · 调工具 · 跑脚本 · 处理工作流           │
├─────────────────────────────────────────────────┤
│          第一层：知识层（Knowledge Layer）          │
│    Skills · Memory · MCP · Context Grounding     │
│    先把正确的信息交给 Claude，再让它开始工作       │
└─────────────────────────────────────────────────┘
```

三层之间的关系不是堆叠，而是**前提条件**：没有扎实的知识层，执行层做错事；没有执行层的能力，协同层无事可协同。

---

## 第一层：知识层（Knowledge Layer）

**核心思想：上下文准备得越充分，Agent 表现就越稳定。**

知识层解决的是「Claude 知道什么」的问题。它包含四个构件：

### Skills — 按需加载的专业知识

Skills 是挂载在 `.claude/skills/` 下的 Markdown 文件包，Claude 在判断相关时自动加载，或由用户用 `/skill-name` 直接调用。

```
.claude/skills/
├── api-conventions/
│   └── SKILL.md       # 描述你的 API 设计规范
├── deploy-prod/
│   └── SKILL.md       # 生产环境部署的完整步骤
└── code-review/
    └── SKILL.md       # 代码审查的具体检查项
```

Skills 和 CLAUDE.md 的区别：CLAUDE.md 是**每次会话都加载**的全局上下文，Skills 是**按需调用**的领域知识。CLAUDE.md 内容越少越好，Skills 则可以精细拆分。

### Memory — 持久化的项目上下文

`CLAUDE.md` 是 Claude 每次启动都会读取的「记忆文件」。关键内容包括：

```markdown
# CLAUDE.md

## 构建命令
- `pnpm dev` — 启动开发服务器
- `pnpm test` — 运行测试（必须全部通过才能提交）

## 代码规范
- 所有函数必须有 JSDoc 注释
- 禁止使用 `any` 类型

## 架构约定
- 状态管理统一用 Zustand，不要引入其他库
- API 调用全部走 `/src/api/` 目录下的封装
```

原则：只写 Claude 无法从代码本身推断的内容。每一行都问自己：「删掉这行，Claude 会犯错吗？」不会的就删。

### MCP — 连接外部世界的协议

MCP（Model Context Protocol）让 Claude 能够实时读取外部数据源，而不是依赖训练时的知识。

典型 MCP 连接场景：

| MCP Server | Claude 获得的能力 |
|---|---|
| GitHub MCP | 读 Issues、创建 PR、查 CI 状态 |
| Figma MCP | 直接读取设计稿规范和标注 |
| Postgres MCP | 查询数据库，理解数据结构 |
| Sentry MCP | 读取生产环境报错和堆栈追踪 |
| Linear MCP | 读取任务描述，直接解决 Issue |

MCP 的价值不是「工具调用」，而是**消除 Claude 的信息盲区**。上下文越完整，响应越精准。

### Context Grounding — 给正确的信息，不给多余的

Grounding 是一个工程习惯，不是一个具体工具：**在让 Claude 工作之前，主动准备好它需要的上下文。**

实践对比：

| 做法 | 示例 |
|---|---|
| ❌ 模糊指令 | "修复登录 bug" |
| ✅ Grounded 指令 | "用户报告 session 过期后登录失败。检查 `src/auth/` 里的 token refresh 逻辑，写一个能复现问题的失败测试，然后修复它" |

---

## 第二层：执行层（Execution Layer）

**核心思想：Claude 在这一层不再只是聊天，而是真正把想法变成现实结果。**

### Harness — 自主执行的循环

Harness 是 Agent 的执行引擎，驱动一个自主循环：读文件 → 理解上下文 → 制定计划 → 执行动作 → 验证结果 → 迭代。

Claude Code 是 Harness 最直接的体现：

```bash
# Claude Code 的典型执行路径
claude "实现用户邮件验证功能"

# Claude 会自动：
# 1. 探索代码库结构（Explore）
# 2. 制定实现计划（Plan）
# 3. 编写代码（Code）
# 4. 运行测试（Verify）
# 5. 迭代修复直到通过（Iterate）
```

Harness 的关键是**给 Claude 一个可以验证的终止条件**，而不是让它自己判断「看起来做完了」：

```markdown
# 在 CLAUDE.md 或 prompt 里明确验证条件
任务完成条件：
- `pnpm test` 全部通过
- `pnpm build` 无报错
- 新功能有对应的单元测试覆盖
```

### Managed Infrastructure — 托管的执行环境

Anthropic 把底层基础设施的复杂性托管起来，让开发者只需要关注业务逻辑：

- **会话管理**：Claude 自动维护上下文连续性，支持跨消息的任务追踪
- **工具调用**：标准化的工具接口，Claude 按需调用文件读写、终端命令、API 请求
- **状态追踪**：任务进度、已完成步骤、待处理问题全部由框架维护

### Sandboxes — 安全边界内的自由执行

Sandbox 是 OS 级别的隔离环境，让 Claude 能够在受限范围内自由操作，不用每一步都等人工确认：

```json
// .claude/settings.json
{
  "sandbox": true,
  "allowedPaths": ["/project/src", "/project/tests"],
  "allowedCommands": ["npm test", "npm run lint", "git diff"],
  "blockedPaths": ["/etc", "/Users"]
}
```

Sandbox 解决的核心矛盾：**你想让 Claude 自主工作，又担心它做出不可逆的操作**。有了 Sandbox，Claude 可以在安全边界内快速迭代，真正需要你关注的操作才会触发权限提示。

---

## 第三层：协同层（Coordination Layer）

**核心思想：从「一个 Agent 做所有事」到「多个 Agent 分工协作，系统不断自我迭代」。**

### 为什么需要多 Agent？

单 Agent 的极限在于：上下文窗口是有限的，一个 Agent 同时规划、执行、评审会相互干扰，而且做错了没有独立的纠错机制。

协同层的解法是**分工**：

```
┌──────────┐     任务描述      ┌──────────┐
│  规划 Agent │ ──────────────→ │  执行 Agent │
└──────────┘                   └──────────┘
                                      │ 执行结果
                                      ▼
                               ┌──────────┐
                               │  评审 Agent │
                               └──────────┘
                                      │ 反馈
                                      ▼
                               ┌──────────┐
                               │  优化 Agent │
                               └──────────┘
                                      │
                                      ▼
                               下一轮迭代 ↩
```

每个 Agent 有独立的上下文窗口，关注自己的专业领域，互不干扰，整体能力超出任何单个 Agent。

### Subagents — Claude Code 里的原生支持

在 Claude Code 里，Subagent 是最简单的多 Agent 实现：

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: 专注于安全漏洞的代码审查，找注入、越权、信息泄露等问题
tools: Read, Grep
---
你是一个专业的安全审查员。只检查安全问题，不评论其他代码质量问题。
对每个发现的问题，给出：严重程度、漏洞描述、具体代码位置、修复建议。
```

调用方式：
```
"用 security-reviewer subagent 审查刚写的 API 接口"
```

Subagent 运行在独立上下文，主 Agent 的操作历史不会污染它的判断——这正是独立评审的价值。

### Token Jobs — Anthropic 的异步 Agent 任务系统

这是访谈里最值得关注的概念：**Token Jobs 是 Anthropic 内部运行的异步后台 Agent 任务**，每种 Job 有明确的职责边界。

目前已知的 5 种 Token Jobs 职责划分模式：

| Job 类型 | 职责 | 类比 |
|---|---|---|
| 规划 Job | 分解任务、制定执行路径 | 架构师 |
| 执行 Job | 实际编写代码、修改文件 | 工程师 |
| 评审 Job | 检查执行结果的质量和正确性 | 代码审查员 |
| 优化 Job | 根据评审反馈改进结果 | 重构专家 |
| 反馈 Job | 汇总结果、更新知识库 | 项目经理 |

当开放给开发者后，这些 Job 类型可以自由组合，形成针对不同业务场景的 Agent 工作流。

### Meta-Harness — 驱动整个协同系统的引擎

Meta-Harness 是协同层的执行引擎，负责：

1. **分配任务**：根据 Job 类型把工作分配给合适的 Agent
2. **维护状态**：追踪哪些 Job 完成、哪些失败、整体进度
3. **路由结果**：把一个 Agent 的输出作为下一个 Agent 的输入
4. **处理异常**：某个 Job 失败时的重试和降级策略

---

## 如何用 Claude Code 实现三层架构

把三层架构落地到实际项目：

### 第一层：建好知识基础

```bash
# 1. 初始化 CLAUDE.md
claude /init

# 2. 创建项目专属 Skills
mkdir -p .claude/skills/deploy
cat > .claude/skills/deploy/SKILL.md << 'EOF'
# 部署流程 Skill
部署前检查清单：
- [ ] 所有测试通过
- [ ] 环境变量已更新
- [ ] 数据库迁移已准备
部署命令：`./scripts/deploy.sh production`
EOF

# 3. 配置 MCP（连接 GitHub、数据库等）
# 在 ~/.claude.json 里添加 MCP 服务
```

### 第二层：配置执行环境

```json
// .claude/settings.json
{
  "sandbox": true,
  "permissions": {
    "allow": [
      "npm:test",
      "npm:run lint",
      "git:diff",
      "git:status"
    ]
  },
  "hooks": {
    "PostToolUse[Edit]": "npm run lint --fix",
    "Stop": "npm test"
  }
}
```

Stop Hook 是执行层的关键：**确保 Claude 在任务「完成」前，自动跑验证**，不给它留下「看起来完成了」的空间。

### 第三层：部署多 Agent 工作流

```bash
# 创建三个专职 Subagent
mkdir -p .claude/agents

# 执行 Agent：写代码
cat > .claude/agents/implementer.md << 'EOF'
---
name: implementer
description: 负责功能实现，只写代码不做评审
tools: Read, Edit, Write, Bash
---
专注实现，不评价代码质量，那是 reviewer 的工作。
实现完成后，运行测试并报告结果。
EOF

# 评审 Agent：独立判断
cat > .claude/agents/reviewer.md << 'EOF'
---
name: reviewer
description: 独立代码审查，不受实现过程影响
tools: Read, Grep
---
从一个全新视角审查代码。假设实现可能有问题，
主动寻找 bug、边界条件遗漏、性能问题、安全隐患。
EOF
```

调用三层工作流：

```
"用 implementer 实现用户注册功能，完成后用 reviewer 进行独立审查，
把审查结果反馈给 implementer 修复，直到 reviewer 满意为止"
```

---

## 为什么这是「最重要的开发者平台」

Anthropic 在 Sequoia 访谈里说这句话的时候，背后的逻辑是：

**以前的 developer platform 卖的是工具，这次卖的是能力。**

传统 developer platform（AWS、Stripe、GitHub）让你少写基础设施代码。Claude 平台让你**少写业务代码本身**——你描述意图，Agent 负责实现，另一个 Agent 负责评审，另一个负责优化，整个系统自我迭代。

这不是效率提升，这是开发模式的重构：

| 旧模式 | 新模式 |
|---|---|
| 工程师写代码，AI 辅助 | 工程师描述需求，Agent 团队协作实现 |
| 一个人看着 AI 输出 | 一个 Agent 评审另一个 Agent |
| 手动运行测试验证 | Stop Hook 保证任务完成前自动验证 |
| 单次对话完成任务 | Token Jobs 异步并发处理多个任务 |

三层架构不是 Anthropic 的产品功能，**它是构建下一代软件的工程方法**。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Anthropic's Three-Layer Agent Architecture: From One Claude to an Agent Team

> Source: Sequoia Capital "Training Data" Podcast, interview with Anthropic's platform lead. Caption: *"You are responsible for building Anthropic's platform — important, if not, the most important developer platform in the world."*

### The Insight That Changes Everything

> While most people are still learning to write prompts, Anthropic is already engineering **teams of agents that coordinate with each other**.

Anthropic's platform lead described a system already running internally: **5 different Token Jobs with distinct responsibilities**. When opened to developers, these become composable building blocks for tens of thousands of agent workflows.

The underlying design is a three-layer agent architecture.

---

### The Three-Layer Architecture

```
┌──────────────────────────────────────────────────┐
│       Layer 3: Coordination Layer                 │
│  Multi-agent division · Token Jobs · Meta-Harness │
│  Plan → Execute → Review → Optimize → Self-iterate│
├──────────────────────────────────────────────────┤
│       Layer 2: Execution Layer                    │
│  Harness · Managed Infrastructure · Sandboxes     │
│  Modify code · Call tools · Run scripts            │
├──────────────────────────────────────────────────┤
│       Layer 1: Knowledge Layer                    │
│  Skills · Memory · MCP · Context Grounding        │
│  Give Claude the right information before it acts  │
└──────────────────────────────────────────────────┘
```

These layers are prerequisites, not just components: weak knowledge layer → wrong execution; no execution capability → nothing for coordination to orchestrate.

---

### Layer 1: Knowledge Layer

**Core idea:** The more complete the context, the more reliable the agent.

- **Skills** (`.claude/skills/`): Domain-specific knowledge packages loaded on demand or via `/skill-name`
- **Memory** (`CLAUDE.md`): Persistent project context read at every session — keep it short, only what Claude can't infer from code
- **MCP Servers**: Real-time connections to GitHub, databases, Figma, monitoring tools — eliminating Claude's information blind spots
- **Context Grounding**: Engineering discipline of preparing the right context before asking Claude to act

### Layer 2: Execution Layer

**Core idea:** Claude stops chatting and starts producing real results.

- **Harness**: The autonomous execution loop — Explore → Plan → Code → Verify → Iterate
- **Managed Infrastructure**: Session management, tool calling, and state tracking handled by the framework
- **Sandboxes**: OS-level isolation enabling Claude to work freely within defined boundaries without constant permission prompts

Key pattern — always give Claude a verifiable completion condition:
```json
{
  "hooks": {
    "Stop": "npm test"   // blocks the task from ending until tests pass
  }
}
```

### Layer 3: Coordination Layer

**Core idea:** From "one agent does everything" to "specialized agents collaborating and self-improving."

- **Subagents**: Independent context windows for specialized tasks (implementer, reviewer, security-checker)
- **Token Jobs**: Anthropic's async agent task system — 5 job types internally (planner, executor, reviewer, optimizer, feedback aggregator)
- **Meta-Harness**: Orchestration engine routing outputs between agents, tracking state, handling failures

The key insight: the agent doing the work should **not** be the one grading it. Independent subagents eliminate the blind spot of self-evaluation.

---

### This Isn't Just a Feature — It's a New Development Model

| Old Model | New Model |
|---|---|
| Engineers write code, AI assists | Engineers describe intent, agent teams implement |
| One person watches AI output | One agent reviews another agent |
| Manually run tests | Stop Hooks enforce verification automatically |
| Single conversation per task | Token Jobs handle tasks asynchronously in parallel |

The three-layer architecture is not a product feature. **It is the engineering methodology for building the next generation of software.**

© 2026 Author: Mycelium Protocol
