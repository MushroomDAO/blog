---
title: "alibaba/skill-up：Agent Skill 的评估与自动进化闭环——Eval + 自修复一键跑通"
titleEn: "alibaba/skill-up: Agent Skill Evaluation and Auto-Evolution Loop — Eval + Auto-Fix in One Command"
description: "alibaba/skill-up，1,031 stars，Apache-2.0，Go。阿里巴巴出品的 Agent Skill 评估与进化工具，4 个月 1000+ stars。声明式 YAML 测试用例 + rule/script/agent 三种 judge 策略 + skill-upper 自动读取失败报告修复 Skill，形成 Eval → 失败分析 → 自动修复 → 再 Eval 的闭环。支持 Claude Code、Codex、Qwen Code，兼容 Anthropic evals.json 格式，内置 GitHub Actions 集成。"
descriptionEn: "alibaba/skill-up — 1,031 stars, Apache-2.0, Go. Alibaba's agent skill evaluation and evolution tool, 1K+ stars in 4 months. Declarative YAML test cases + rule/script/agent judge strategies + skill-upper auto-reads failure reports and fixes skills, forming an Eval → Failure Analysis → Auto-Fix → Re-Eval loop. Supports Claude Code, Codex, Qwen Code. Compatible with Anthropic evals.json format. Built-in GitHub Actions integration."
pubDate: 2026-09-22
heroImage: "../../assets/images/alibaba-skill-up-agent-skill-eval-evolution-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "agent", "evaluation", "skill", "claude-code", "alibaba", "go", "ci-cd", "apache"]
lang: zh-CN
---

`alibaba/skill-up`，1,031 stars，Apache-2.0，Go 语言，2026-05-09 创建，今天（2026-09-22）仍在活跃更新。阿里巴巴官方出品，4 个月破千星。

一句话：Agent Skill 的自动化评估 + 自动进化工具，把「写 Skill → 测试 → 失败 → 手动改 → 再测」的循环变成机器可跑的闭环。

**GitHub**：github.com/alibaba/skill-up | **Stars**：1,031 | **License**：Apache-2.0 | **语言**：Go ≥1.25

---

## 背景：SKILL.md 生态的质量真空

Claude Code 的 Skill、Codex 的 Skill、Qwen Code 的 Skill，核心都是一个 `SKILL.md` 或类似格式的提示词文档加上工具链配置。写完了怎么验证质量？

目前的状况是：靠手动测试。跑几次、看看输出对不对、改改描述、再跑。这在 Skill 数量少时勉强够用，当 Skill 库扩大、或需要持续维护时，没有系统化评估就是技术债。

skill-up 做的是给 Skill 套上一个正规的评估框架，并进一步把「失败 → 修复」这一步也自动化掉。

---

## 两层能力：Evaluation + Evolution

### Evaluation（评估）

声明式 YAML 测试用例 + 三种 judge 策略，自动对 Agent Skill 打分：

```yaml
# evals/eval.yaml（简化示例）
name: "my-skill-eval"
target: "../SKILL.md"
engine: claude_code
cases:
  - id: basic-usage
    input: "帮我把这段 Python 代码转成 TypeScript"
    judge:
      type: rule
      rules:
        - contains: "function"
        - not_contains: "def "
  - id: edge-case
    input: "处理空输入"
    judge:
      type: agent
      criteria: "回复应该优雅处理空输入，不崩溃，给出提示"
```

三种 judge 策略：

| 策略 | 适用场景 | 方式 |
|------|---------|------|
| **rule** | 输出包含/不含特定字符串，格式校验 | 正则/关键词规则 |
| **script** | 需要执行代码验证（如跑测试、编译）| 自定义脚本 |
| **agent** | 语义质量判断（流畅度、正确性、完整性） | 调另一个 AI 当裁判 |

报告格式：`result.json`、`grading.json`（Anthropic 格式）、JUnit XML（CI 集成）、HTML、Markdown。

### Evolution（进化）

skill-upper 是 skill-up 内置的一个 Agent Skill，专门干一件事：读失败报告 → 分析原因 → 自动修复 Skill 实现或测试用例 → 再跑评估。

闭环流程：

```
写 SKILL.md
    ↓
skill-up run → result.json（含失败用例）
    ↓
在 Agent 里："Use skill-upper to fix failures"
    ↓
skill-upper 读取失败 → 修改 SKILL.md 或补充测试定义
    ↓
skill-up run（再次） → 新 result.json
    ↓
重复直到全过
```

每次迭代在 `<skill>-workspace/iteration-N/` 下留存快照，可以回溯任何一轮的结果。

---

## 安装

**CLI 直接安装：**

```bash
curl -fsSL https://raw.githubusercontent.com/alibaba/skill-up/main/install.sh | bash
```

**以 Skill 形式安装到 Codex：**

```bash
npx skills add https://github.com/alibaba/skill-up/tree/main/skills/skill-upper -g -a codex -y
```

**以 Skill 形式安装到 Claude Code：**

```bash
npx skills add https://github.com/alibaba/skill-up/tree/main/skills/skill-upper -g -a claude-code -y
```

安装后 skill-upper 在 Claude Code/Codex 里就是一个普通 Skill，可以直接调用。

---

## 使用流程

### 方式一：通过 skill-upper（推荐）

在 Agent 对话框里：

```
Use skill-upper to evaluate this Skill. Read SKILL.md, create realistic eval cases, 
validate the configuration, and run skill-up.
```

skill-upper 自动：
1. 读取 `SKILL.md`，理解 Skill 的目标和功能
2. 生成评估用例（`evals/cases/<case-id>.yaml`）
3. 生成 `evals/eval.yaml` 配置
4. 运行 `skill-up run`
5. 读取失败报告，迭代修复

生成的目录结构：

```
my-skill/
├── SKILL.md
└── evals/
    ├── eval.yaml
    └── cases/
        ├── basic-test.yaml
        ├── edge-case-empty.yaml
        └── ...

my-skill-workspace/
├── iteration-1/result.json
├── iteration-2/result.json
└── ...
```

### 方式二：CLI 直接运行

```bash
# 验证配置语法
skill-up validate evals/eval.yaml

# 列出所有测试用例
skill-up list-cases evals/eval.yaml

# 执行评估
skill-up run evals/eval.yaml

# 从历史结果重新生成报告
skill-up report workspace/iteration-1/result.json

# 导入 Anthropic 格式的 evals
skill-up import evals.json

# 调试 judge 逻辑
skill-up debug judge input.json
```

### 配置优先级

```
内置默认 < ~/.config/skill-up/config.yaml < ./.skill-up.yaml < --config <path>
```

初始化用户配置：

```bash
skill-up init
```

---

## GitHub Actions 集成

一行接入 CI：

```yaml
- uses: alibaba/skill-up@main
  with:
    engine: claude_code           # 或 codex / qodercli / qwen_code
    api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    base-url: https://api.anthropic.com
    skill-target: evals/eval.yaml
```

每次 PR 合并前自动跑 Skill 评估，失败则 CI 不通过。

**注意**：GitHub Action 仅支持 Linux runner，不支持 macOS 和 Windows CI runner。

---

## 支持的 Agent 引擎

| 引擎 | 状态 |
|------|------|
| Claude Code | ✅ 支持 |
| Codex | ✅ 支持 |
| Qwen Code | ✅ 支持 |
| Qoder CLI | ✅ 支持 |
| 自定义引擎 | ✅ 实现 local transport 接口 |

跨引擎对比评估也是典型用例：同一套测试用例，分别跑 Claude Code 和 Qwen Code，对比结果。

---

## Anthropic evals.json 兼容

skill-up 的输出格式与 Anthropic Agent Skills 的 `evals.json` 兼容，也支持导入已有的 Anthropic 评估结果：

```bash
skill-up import anthropic-evals.json
```

这意味着已经在用 Anthropic 官方评估框架的项目可以直接迁入，不用重写测试。

---

## 与同类工具对比

| 工具 | 关注点 | 自动修复 | 多引擎 | CI 集成 |
|------|--------|---------|--------|---------|
| **skill-up** | Agent Skill 质量 | ✅ skill-upper | ✅ 4+ 引擎 | ✅ GitHub Actions |
| Anthropic evals | Claude 模型评估 | ❌ | ❌ Claude only | 手动 |
| OpenAI Evals | GPT 模型评估 | ❌ | ❌ OAI only | 手动 |
| DeepEval | RAG/LLM 质量 | ❌ | 部分 | ✅ |

skill-up 的核心差异是**多引擎 + 自动进化**。测试框架本身不新鲜，新鲜的是把「失败 → AI 自动修复 → 再测」这一环也跑通了。

---

## 局限性

**1. Go ≥1.25 要求**：构建需要较新版本的 Go，旧环境需要升级。

**2. GitHub Action 仅限 Linux**：macOS 和 Windows CI runner 不支持，本地 Windows 使用有单独限制说明。

**3. 无性能基准数据**：文档没有提供 skill-up 本身的执行耗时或 overhead 数据。

**4. 自动修复质量依赖底层 Agent**：skill-upper 的修复能力取决于你用的 Agent 引擎水平，Claude Code 和 Qwen Code 的修复效果可能有差异。

**5. agent judge 引入额外成本**：用 AI 做 judge 会产生额外 API 调用费用，大规模评估时需要估算成本。

---

## 怎么看这个项目

Skill 生态的质量问题是真实的——随着 Claude Code Skill、Codex Skill 越来越多，「写完没法系统测」是个普遍痛点。skill-up 的工程切入点清晰：声明式测试用例 + 多种 judge + CI 集成，覆盖了大多数 Skill 验证需求。

skill-upper 的「失败 → AI 自修复」闭环是更有意思的设计，但这也是目前最不确定的部分——AI 自动修复 Skill 的可靠程度取决于具体任务，不是所有失败都能被自动解决。

阿里巴巴官方背书 + Apache-2.0 + 4 个月 1000+ stars，是认真做工具的信号。有 Agent Skill 开发需求的团队值得评估。

> Apache-2.0，开源仅供学习研究参考。

---

<!--EN-->

## alibaba/skill-up: Agent Skill Evaluation and Auto-Evolution Loop

`alibaba/skill-up` (1,031 stars, Apache-2.0, Go ≥1.25) is Alibaba's evaluation and evolution tool for Agent Skills — 1K+ stars in 4 months of active development.

**GitHub**: github.com/alibaba/skill-up | **Stars**: 1,031 | **License**: Apache-2.0

---

### What It Does

Provides a systematic evaluation framework for Agent Skills (Claude Code Skills, Codex Skills, Qwen Code Skills), plus an auto-evolution loop:

1. **Evaluation**: Declarative YAML test cases + three judge strategies (rule/script/agent) → structured reports
2. **Evolution**: `skill-upper` skill reads failure reports, auto-fixes the Skill or test cases, re-runs evaluation — closing the loop

---

### Installation

```bash
# CLI
curl -fsSL https://raw.githubusercontent.com/alibaba/skill-up/main/install.sh | bash

# As a skill in Claude Code
npx skills add https://github.com/alibaba/skill-up/tree/main/skills/skill-upper -g -a claude-code -y

# As a skill in Codex
npx skills add https://github.com/alibaba/skill-up/tree/main/skills/skill-upper -g -a codex -y
```

---

### Core Workflow

```
Write SKILL.md
    ↓
skill-up run → result.json (with failures)
    ↓
"Use skill-upper to fix failures"
    ↓
skill-upper reads failures → modifies SKILL.md or test cases
    ↓
skill-up run (again) → new result.json
    ↓
Repeat until all pass
```

---

### Test Case Format

```yaml
# evals/eval.yaml
name: "my-skill-eval"
target: "../SKILL.md"
engine: claude_code
cases:
  - id: basic-usage
    input: "Convert this Python to TypeScript"
    judge:
      type: rule
      rules:
        - contains: "function"
  - id: semantic-quality
    input: "Handle edge case"
    judge:
      type: agent
      criteria: "Response should handle edge case gracefully and explain the limitation"
```

**Three judge types**:
- `rule`: keyword/regex checks
- `script`: run a script to verify output
- `agent`: use another AI to evaluate quality

---

### GitHub Actions

```yaml
- uses: alibaba/skill-up@main
  with:
    engine: claude_code
    api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    base-url: https://api.anthropic.com
    skill-target: evals/eval.yaml
```

Note: Only Linux runners supported; macOS/Windows CI runners not available.

---

### Supported Engines

Claude Code, Codex, Qwen Code, Qoder CLI, custom (via local transport interface). Cross-engine comparison (same test suite on different agents) is a supported use case.

---

### Limitations

1. **Go ≥1.25** required
2. **GitHub Action Linux only**: no macOS/Windows CI runner support
3. **No performance benchmarks**: no overhead data for skill-up itself
4. **Auto-fix quality is model-dependent**: skill-upper's effectiveness depends on the underlying agent engine
5. **Agent judge costs**: AI-as-judge adds API call costs at scale

---

### Why It Matters

The SKILL.md ecosystem is growing fast, and systematic quality validation has been missing. skill-up fills this gap with a proper eval framework + CI integration + the distinctive addition of an AI-driven auto-fix loop. The evolution loop is the most interesting and least proven piece — useful but not magic.

Apache-2.0, Alibaba-backed, 1K+ stars in 4 months: a credible signal that this is a serious engineering tool, not a prototype.

> Apache-2.0. For learning and research reference only.
