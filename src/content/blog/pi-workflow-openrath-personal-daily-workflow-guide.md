---
title: "pi-workflow v1.1.0：普通个人如何用 Pi Agent 把日常工作流变成可复用的自动化流水线"
titleEn: "pi-workflow v1.1.0: How Ordinary Individuals Build Reusable Automated Pipelines with Pi Agent"
description: "pi-workflow 是 Pi Agent 的子任务编排扩展，一键安装后用自然语言调度深度调研、代码评审、规范比对、变更评估 4 套预制流程，也可以写 JSON 自定义 DAG。文章重点讲普通个人怎么把学习、研究、写作、项目管理等日常工作流接进来，以及底层框架 OpenRath 的 PyTorch 式设计思想。"
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["Pi Agent", "工作流编排", "AI自动化", "OpenRath", "个人效率", "DAG", "开源工具", "subagent", "研究工作流", "代码评审"]
heroImage: "../../assets/images/pi-workflow-openrath-personal-daily-workflow-guide-banner.jpg"
---

> **pi-workflow**：[AgwaB/pi-workflow](https://github.com/AgwaB/pi-workflow) · npm: `@agwab/pi-workflow` · v1.1.0 · MIT  
> **OpenRath**：[Rath-Team/OpenRath](https://github.com/Rath-Team/OpenRath) · PyPI: `openrath` · BSD-3-Clause · arXiv: 2606.19409  
> **平台**：macOS / Linux（WSL 可用）· 需要 Node.js ≥22.19.0

---

## 先说清楚两个东西的关系

**OpenRath** 是底层框架——把多 Agent 多 Session 运行时变成像 PyTorch 一样的可组合 Python 对象：Session（对话状态流）、Sandbox（执行环境）、Memory（持久记忆）、Tool（工具调用）、Agent（Session 变换层）、Workflow（Agent 组合容器）、Selector（运行时路由器）。

**pi-workflow** 是建在这套架构之上、专门给 Pi Agent 用的工作流编排扩展：一键安装，自然语言调度，4 个开箱即用的预制流程，支持 JSON 自定义 DAG，全本地缓存，可断点续跑。

普通人用 pi-workflow，不需要理解 OpenRath 的底层设计——但理解它的设计哲学，能帮你想清楚"我的工作流该怎么拆"。

---

## OpenRath 的核心比喻：把 PyTorch 的方式用在 Agent 上

| PyTorch 概念 | OpenRath 对应 | 含义 |
|---|---|---|
| `Tensor` | `Session` | 流动的运行时值：有序 chunk、执行位置、lineage |
| `Device` | `Sandbox` | 工具真正运行的地方：本地进程、云沙箱 |
| `Parameter` | `Memory` | 跨次运行持久化的 Agent 状态 |
| `Function` | `Tool` | 模型可见 schema + 运行时行为的可调用操作 |
| `nn.Linear` | `Agent` | 把一个 Session 映射到另一个 Session 的可复用层 |
| `nn.Module` | `Workflow` | Agent、工具、Session 变换的可嵌套组合容器 |
| 控制流 | `Selector` | LLM 驱动的路由器，实现动态 `if` / `while` |

**关键洞察**：大多数框架的核心是"Agent 循环"，OpenRath 的核心是"Session"。当一个应用需要多 Agent、多分支、持久记忆、沙箱执行、可追溯 lineage 时，"从 Session 出发"比"从循环出发"更容易扩展。

---

## pi-workflow 安装

```bash
# 一键安装（自动安装 /workflow 面板 + workflow-guide skill + execution-router skill）
pi install npm:@agwab/pi-workflow

# 重新加载 Pi
# （安装完按提示 reload 即可）

# 后续更新
pi update npm:@agwab/pi-workflow
```

---

## 4 个开箱即用的预制流程

### 1. deep-research（深度调研）

最常用。给一个主题或仓库，自动多步骤调研并汇总架构、权衡、核心设计。

```
# 自然语言方式
Use the bundled deep-research workflow to research this repository and summarize the architecture tradeoffs.

# 精确控制
/workflow run deep-research "研究 Redis 的 Cluster 模式和 Sentinel 模式的架构差异"
```

**个人用法**：
- 学一个新技术栈：`/workflow run deep-research "调研 Rust async 运行时 Tokio vs async-std 的设计差异"`
- 评估一个开源项目：`/workflow run deep-research "调研 Helix 编辑器和 Neovim 的插件生态差异"`
- 准备一次讨论：`/workflow run deep-research "总结 RAG vs Fine-tuning 的适用场景和成本差异"`

### 2. deep-review（深度代码评审）

从多个角度审查当前 diff，不只看表面，会查并发安全、错误处理、测试覆盖等。

```
Use the deep-review workflow to review the current diff from multiple perspectives.

/workflow run deep-review "审查这次 PR 的 API 设计和错误处理"
```

**个人用法**：
- 提交前自检：`/workflow run deep-review "检查我今天的改动有没有安全问题"`
- 学习他人代码：`/workflow run deep-review "分析这个开源库的事务处理逻辑"`

### 3. spec-review（规范比对）

把文档/API SPEC 和实现代码、测试对比，找出不一致的地方。

```
Use the spec-review workflow to compare docs/API_SPEC.md against the implementation and tests.

/workflow run spec-review "比较 openapi.yaml 和现有接口实现"
```

**个人用法**：
- 接口对齐检查：`/workflow run spec-review "对比 PRD 文档和现有功能实现的差距"`
- 文档维护：`/workflow run spec-review "检查 README 的快速开始步骤是否还能跑通"`

### 4. impact-review（变更影响评估）

分析一次变更会影响哪些下游模块、测试、调用方。

```
/workflow run impact-review "评估删除 legacy_auth 模块的影响范围"
```

**个人用法**：
- 重构前评估：`/workflow run impact-review "重命名 UserService 会影响多少地方"`
- 依赖升级：`/workflow run impact-review "升级 React 18 到 19 的变更影响"`

---

## 自适应模式：不知道用哪个流程时

```bash
# 让 Pi 自己规划、分发、汇总
/workflow dynamic "帮我分析这个项目的技术债，给出优先级排序和改善建议"
```

动态模式会自动规划任务图、并行分发子任务、汇总结果——适合开放性问题，不需要预先定好阶段。

---

## 自定义 JSON DAG：把你的日常流程固化下来

这是 pi-workflow 最有价值的功能：把反复做的工作流写成 JSON，以后一句话触发。

### 6 种标准阶段类型

| 类型 | 用途 | 示例 |
|---|---|---|
| `single` | 单步执行，一个 Agent 处理 | 计划、总结、分析 |
| `parallel` | 多角度并行，互不依赖 | 同时从安全/性能/可读性审查代码 |
| `loop` | 循环直到条件满足 | 反复改进直到通过质量门槛 |
| `batch` | 批量分发同类任务 | 对 N 个文件各自做同样的处理 |
| `fan-in` | 汇总多路结果 | 合并并行阶段的结论 |
| `adaptive` | 动态编排，Pi 自己决定 | 不确定需要几步时 |

### 示例：个人周报生成工作流

```json
{
  "schemaVersion": 1,
  "name": "weekly-report",
  "description": "从 Git log、任务记录、Notes 生成周报",
  "defaults": {
    "agent": "researcher",
    "readOnly": true,
    "tools": ["read", "grep", "find", "bash"]
  },
  "artifactGraph": {
    "stages": [
      {
        "id": "collect",
        "type": "parallel",
        "tasks": [
          { "prompt": "汇总本周 git log，按模块分组，提取关键变更", "tools": ["bash"] },
          { "prompt": "读取本周任务记录，提取已完成和未完成项" },
          { "prompt": "读取本周的学习笔记和技术调研记录" }
        ]
      },
      {
        "id": "synthesize",
        "type": "single",
        "dependsOn": ["collect"],
        "prompt": "整合上面三路内容，生成结构化周报：本周完成、下周计划、风险和阻塞、技术沉淀。格式清晰，可直接发给团队。"
      }
    ]
  }
}
```

保存为项目里的 `.pi/workflows/weekly-report.json`，以后直接：

```
/workflow run weekly-report "生成本周技术周报"
```

### 示例：发布前检查工作流

```json
{
  "name": "release-check",
  "description": "版本发布前的标准化检查清单",
  "artifactGraph": {
    "stages": [
      {
        "id": "docs-check",
        "type": "single",
        "prompt": "检查 CHANGELOG、README、版本号是否更新，找出不一致"
      },
      {
        "id": "test-check",
        "type": "single",
        "prompt": "检查测试覆盖率，找出最近改动但没有对应测试的部分"
      },
      {
        "id": "dependency-check",
        "type": "single",
        "prompt": "检查 package.json / pyproject.toml 依赖有无已知漏洞，版本是否 pinned"
      },
      {
        "id": "final-verdict",
        "type": "fan-in",
        "dependsOn": ["docs-check", "test-check", "dependency-check"],
        "prompt": "汇总三路检查结果，给出 Go/No-go 决策和必须修复的问题列表"
      }
    ]
  }
}
```

---

## 执行路由决策：不确定用什么方式时

```bash
# 让 Pi 帮你决定：直接处理 / 单 Agent / 某个已有 workflow / 新建 workflow
/skill:execution-router decide whether this repository review should use a single-agent pass, deep-review, or a targeted verifier.
```

workflow-guide 技能帮你**创建和验证新工作流定义**：

```bash
# 创建工作流
/skill:workflow-guide create a workflow for weekly release readiness.
It should inspect docs, tests, recent changes, package metadata, and produce a final checklist.
Save it as a reusable project workflow.

# 自定义已有流程
/skill:workflow-guide customize deep-review for frontend accessibility and UX review.
```

---

## 断点续跑：长任务不怕中断

pi-workflow 的所有执行记录**全本地缓存**，任务中断后可以恢复：

```bash
# 查看当前运行状态
/workflow status

# 恢复中断的运行
/workflow resume <run-id>

# 查看历史运行和产物
/workflow list
```

---

## 个人日常场景地图

| 场景 | 推荐工作流 | 示例命令 |
|---|---|---|
| 学新技术 | deep-research | `/workflow run deep-research "调研 Rust 异步运行时"` |
| 写技术文章 | deep-research + 自定义 | 先调研，再用 custom workflow 写作 |
| 提交代码前 | deep-review | `/workflow run deep-review "审查今天的改动"` |
| 重构评估 | impact-review | `/workflow run impact-review "删除旧模块的影响"` |
| 写周报 | 自定义 weekly-report | `/workflow run weekly-report "生成本周报告"` |
| 版本发布 | 自定义 release-check | `/workflow run release-check "v2.1.0 发布前检查"` |
| 接手老项目 | deep-research | `/workflow run deep-research "调研这个项目的架构和历史决策"` |

---

## 核心判断

pi-workflow 解决的是一个常见的低效问题：每次做类似的事（调研、评审、周报），都要手动拆步骤、粘贴上下文、等结果、再整合——工作的"脚手架"被反复重建。

把这个脚手架固化成 JSON 工作流，每次用一句话触发，结果可复查、可恢复、可改进。这不是"自动化替代思考"，而是"把重复的执行层外包出去，把精力留给判断层"。

对普通个人来说，最实用的起点是：先用 `deep-research` 和 `deep-review` 两个开箱即用流程感受效果，然后用 `workflow-guide` 把自己最频繁的一个重复流程写成 JSON，固化下来。

---

## 参考资源

- **pi-workflow**：[AgwaB/pi-workflow](https://github.com/AgwaB/pi-workflow)
- **OpenRath**：[Rath-Team/OpenRath](https://github.com/Rath-Team/OpenRath) · [docs.openrath.com](https://docs.openrath.com)
- **OpenRath 论文**：arXiv:2606.19409
- **pi-subagent**：[AgwaB/pi-subagent](https://github.com/AgwaB/pi-subagent)

© 2026 Author: Mycelium Protocol
