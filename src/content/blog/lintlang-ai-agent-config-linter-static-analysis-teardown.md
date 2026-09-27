---
title: "LintLang：给 AI Agent 配置文件做代码检查的静态分析工具"
description: "hermes-labs-ai/lintlang，Apache 2.0，Python，106 stars。零 LLM、零网络请求的静态 linter，专为 AGENTS.md / CLAUDE.md / GEMINI.md / SKILL.md 和 Python 提示词文件设计。H1–H7 七个检查族覆盖工具描述模糊性、缺失停止条件、schema 意图不一致等。ByteDance DeerFlow PR #5656 证明真实有效。v0.8.0 今天发布。"
pubDate: 2026-09-27
heroImage: "../../assets/images/lintlang-ai-agent-config-linter-static-analysis-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["AI Agent", "静态分析", "LLMOps", "开源拆解", "Python", "Claude Code"]
lang: "zh-CN"
wechatTitle: "LintLang：给AI Agent配置文件做代码检查"
wechatDigest: "零LLM静态扫描Agent配置；ByteDance验证真实；H1-H7七类规则；单人团队106星"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 背景：AGENTS.md 是基础设施，却没有 lint

`CLAUDE.md`、`AGENTS.md`、`SKILL.md` 这些文件已经成为每个认真开发 AI Agent 的团队的版本控制基础设施。它们定义工具、设置权限、约定行为——但它们收到的静态检查几乎为零，而同等重要的 Python/TypeScript 代码却会跑 ESLint、Ruff、Pyright。

**hermes-labs-ai/lintlang** 就是专门填这个缺口的工具。

仓库：github.com/hermes-labs-ai/lintlang  
**Stars：106 | License：Apache 2.0 | 语言：Python | 创建：2026-02-28 | 最新版本：v0.8.0（今天发布）**

作者：Rolando Bosch，Hermes Labs 创始人，迈阿密。发表过两篇相关研究论文（Zenodo），向 LangChain/Microsoft Semantic Kernel/DSPy 合计提交了 4 个 Fix PR。这是有研究基础的产品，不是草台工具。

---

## 核心设计：零 LLM，完全确定性

扫描过程中不发任何 LLM 请求，不访问网络。所有判断都是确定性的静态规则——这意味着 CI 里的结果可重现，不会因模型版本变化而漂移。

```bash
# 一次性运行，不需要安装
uvx lintlang scan .

# 扫单个文件
lintlang scan CLAUDE.md
lintlang scan agent.yaml

# CI 门控（HIGH/CRITICAL 时 exit 1）
lintlang scan . --fail-on fail

# 自动发现仓库中的所有 Agent 配置文件
lintlang scan --discover
```

输出格式：`terminal`、`markdown`、`json`、`sarif`（GitHub Code Scanning 兼容）、`gitlab`（v0.8.0 新增，GitLab Code Quality 集成）。

---

## 七个检查族（H1–H7）

### H1：工具描述模糊性

这是最重要的一族，9 条规则：

| 规则 | 检查内容 | 严重级 |
|------|---------|--------|
| H1.1 | 工具没有 description 字段 | CRITICAL |
| H1.2 | Description < 20 字符，没有具体动作 + 领域对象 | HIGH |
| H1.3 | Description 以模糊动词开头（handle、process、manage、do、perform） | MEDIUM |
| H1.4 | 两个工具同名 | CRITICAL |
| H1.5 | 两工具描述 Jaccard 词相似度过高 | HIGH |
| H1.6 | 两工具缺乏可区分的分析性词汇 | MEDIUM |
| H1.7 | Skill description 超过 1024 字符 | HIGH |
| H1.8 | Skill description 没说明何时使用 | MEDIUM/LOW |
| H1.9 | Skill name 无效，或与 SKILL.md 目录名不符 | MEDIUM |

H1.6 用有限同义词词典检测关系性不区分——即两个工具即使描述文字不同，但分析性词汇无法区分彼此（例如"Look up an order" vs "Search for orders in the system"，Jaccard 0，但都没有任何区分性词汇）。这个规则背后有一篇独立发表的研究论文：*Tool Differentia*（DOI: 10.5281/zenodo.21817243）。

### H2：缺失约束脚手架

检测无界重试语言——"keep trying until done"、"continue until success" 等——**在没有显式上界的情况下**。如果同一句话里已经说了"最多 N 次"，不触发。负向终止条件也检测：如"不要停下来直到完成"而没有停止条件。

### H3：Schema 意图不一致

- `required` 字段不在 `properties` 里（幽灵字段）
- 参数无描述
- 泛型参数名：`data`、`input`、`value`、`payload`
- `anyOf`/`oneOf` 有结构性 variant 但无描述
- 嵌套对象无描述

### H4：上下文边界侵蚀

- "记住所有内容"/"使用完整对话历史"等无作用域的上下文指令
- **H4.5（MEDIUM）**：指令文档引用了不存在的相对文件路径——你的 CLAUDE.md 指向了一个不存在的 `docs/STYLE.md`，就会触发

### H5：隐式指令失效

模糊限定词：「be concise」、「be helpful」、「use common sense」；模糊条件：「as needed」、「when appropriate」；修辞性动词：「lean into」、「err on the side of」。对话 Prompt 额外检查负向指令密度和缺乏优先级排序的大型指令集。

### H6：输出格式合约冲突

在同一 Prompt 里要求 JSON 和 Markdown 而未消歧义；未解析的模板变量（`{{variable}}` 类型）；缺少格式说明；缺少版本标记。

### H7：角色混乱

消息数组结构问题：多个 system 消息、system 消息不在位置 0、连续同角色消息、孤立 tool result（前面没有对应 tool use）、消息缺少 role 字段。

### Python 文件检查

- **P1：未校准阈值**——`confidence_threshold = 0.7` 类的硬编码数字，没有校准注释
- **P2：嵌入脚手架**——超过 500 字符（LOW）或 200–500 字符（INFO）的内嵌 Prompt，建议外部化

---

## ByteDance DeerFlow 案例：真实有效

README 展示了一个可验证的真实案例：LintLang 发现了 ByteDance DeerFlow 项目的 Vercel skill 里存在 H1.9 缺陷（skill name 与目录名不一致），这个问题被修复，合并为 **PR #5656**（github.com/bytedance/deer-flow/pull/5656）。

这不是捏造的演示案例——是公开可查的外部 PR。说明工具在真实生产项目里能找到真实问题。

---

## 与主流 Agent 工具链的集成

- GitHub Actions + SARIF 上传（GitHub Code Scanning 可显示）
- GitLab Code Quality（v0.8.0 新增）
- pre-commit hook
- **Claude Code 插件**（PostToolUse hook + 按需 Audit skill）
- Cursor 市场插件
- GitHub Copilot CLI skill
- Gemini CLI Extension
- MegaLinter external descriptor

项目在 `.claude-plugin/`、`.cursor-plugin/`、`.hermes/`、`gemini-extension.json` 里直接提供集成配置——这不是说说而已，是针对主流 Agent 开发工具链的完整覆盖。

---

## 四个需要正视的局限

### 1. 跨文件不聚合

工具对比只在单个文件内进行。两个独立 MCP server 配置文件里各有一个叫 `search` 的工具，H1.4/H1.5 不会触发——系统不把整个 repo 的所有工具视为一个选择命名空间。

### 2. 评估只有 5 个内置 fixtures

`evals/sample-detection-rate.sh` 检测 4 个坏样本 + 1 个干净样本，是回归测试，不是准确率评估。文档明确说："These five fixtures do not estimate accuracy, false-positive rate, or behavior on external projects." 没有外部精确率/召回率数据。

### 3. H1.6 同义词词典有限

「kill」/「terminate」、「approve」/「authorize」这样的同义词对**不被检测**。词典明确有限，文档有说明。没有外部标注语料的基准测试。

### 4. 已知发现遗漏

`.cursor/rules`、`.claude/agents`、`.windsurfrules` 不在 `--discover` 自动识别范围里，文档明确列出这些为"known omissions"。需要手动作为参数传入。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 106 |
| License | Apache 2.0 |
| 语言 | Python |
| 创建时间 | 2026-02-28 |
| 今日版本 | v0.8.0（2026-09-27） |
| 版本数量 | 8 个 release（7 个月） |
| 运行时依赖 | 1 个（pyyaml≥6.0.3） |
| 支持文件格式 | .yaml/.yml/.json/.md/.txt/.prompt/.py |
| 外部验证案例 | ByteDance DeerFlow PR #5656 |
| 内置评估 fixtures | 5 个（非准确率基准） |

---

## 综合判断

这个工具的核心主张正确：Agent 配置文件是可执行基础设施，应该接受与源代码同等级别的静态分析。零 LLM 依赖 + 完全确定性是正确的 CI 设计选择。H1 工具描述模糊性检查、H2 无界重试检测、H4.5 悬空引用检查——这些都在解决实际存在的问题，ByteDance 案例验证了至少一种规则在生产代码里有效。

106 星、单人公司、无外部精确率测试——这三点要知道。项目目前更像是"一个研究背景扎实的人写的好工具"，而不是"大规模验证的行业标准"。但如果你在维护 CLAUDE.md 或 SKILL.md，`uvx lintlang scan .` 一行命令值得跑一遍。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## LintLang: Static Analysis Linter for AI Agent Configuration Files

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Background: AGENTS.md Is Infrastructure With No Lint

`CLAUDE.md`, `AGENTS.md`, `SKILL.md` are now version-controlled infrastructure at every serious AI agent shop. They define tools, set permissions, and specify behavior — but receive almost zero static scrutiny, while equivalent Python/TypeScript code runs ESLint, Ruff, and Pyright.

**hermes-labs-ai/lintlang** fills that gap.

Repo: github.com/hermes-labs-ai/lintlang  
**106 stars | Apache 2.0 | Python | Created 2026-02-28 | v0.8.0 released today**

Author: Rolando Bosch, Hermes Labs (Miami). Published two research papers on the topic, merged 4 fix PRs into LangChain/Semantic Kernel/DSPy. Research-backed, not a weekend project.

---

### Core Design: Zero LLM, Fully Deterministic

No LLM calls. No network requests. All checks are deterministic static rules — CI results are reproducible across model version changes.

```bash
uvx lintlang scan .          # run once, no install
lintlang scan CLAUDE.md      # scan single file
lintlang scan . --fail-on fail   # CI gate on HIGH/CRITICAL
lintlang scan --discover     # auto-find all agent config files
```

Output formats: terminal, markdown, json, sarif (GitHub Code Scanning), gitlab (new in v0.8.0).

---

### Seven Check Families (H1–H7)

**H1: Tool Description Ambiguity** — 9 rules covering missing descriptions, vague verbs (handle/process/manage), duplicate tool names, near-duplicate descriptions (Jaccard similarity), and relational non-distinction (two tools with no differentiating analytical terms). H1.6 is backed by a published research paper: *Tool Differentia* (DOI: 10.5281/zenodo.21817243).

**H2: Missing Constraint Scaffolding** — detects unbounded retry language ("keep trying until", "continue until") without explicit bounds. Does NOT fire if the same sentence states a limit.

**H3: Schema-Intent Mismatch** — phantom required fields, undescribed parameters, generic names (data/input/value/payload), undescribed anyOf/oneOf variants.

**H4: Context Boundary Erosion** — unscoped "remember everything" instructions; **H4.5**: checks that relative file paths referenced in instruction documents actually exist on disk.

**H5: Implicit Instruction Failure** — vague qualifiers (be concise, be helpful, use common sense), ambiguous conditionals (as needed, when appropriate), figurative verbs (lean into, err on the side of).

**H6: Output Format Contract Violation** — conflicting format requirements (JSON + Markdown without disambiguation), unresolved template variables.

**H7: Role Confusion** — malformed message arrays: multiple system messages, system message not at position 0, orphan tool results.

**Python checks**: P1 (uncalibrated numeric thresholds), P2 (long embedded prompts suggesting externalization).

---

### Real Proof: ByteDance DeerFlow PR #5656

LintLang found an H1.9 defect in ByteDance's DeerFlow project (Vercel skill, name mismatch with directory). It was fixed and merged as **PR #5656** (github.com/bytedance/deer-flow/pull/5656). Publicly verifiable — not a staged demo.

---

### Four Limitations to Know

1. **Cross-file tools are never compared.** Two MCP server files each having a `search` tool won't trigger H1.4/H1.5/H1.6.
2. **Evaluation is 5 built-in fixtures.** Not a precision/recall benchmark.
3. **H1.6 synonym lexicon is finite.** "kill"/"terminate", "approve"/"authorize" pairs not detected.
4. **`.cursor/rules`, `.claude/agents`, `.windsurfrules` not auto-discovered.** Listed as known omissions; must be passed explicitly.

---

### Numbers

| Metric | Value |
|--------|-------|
| Stars | 106 |
| Runtime dependencies | 1 (pyyaml) |
| Check families | 7 (H1–H7) + 2 Python (P1–P2) |
| Integrations | GitHub Actions, SARIF, GitLab, pre-commit, Claude Code, Cursor, Gemini CLI |
| External validation | ByteDance DeerFlow PR #5656 |

---

### Verdict

The core claim is correct: agent config files deserve the same static scrutiny as source code. Zero-LLM deterministic checks are the right CI design. H1 ambiguity detection, H2 unbounded retry detection, H4.5 stale reference check — these solve real problems. The ByteDance case proves at least one rule catches real bugs in real production code.

106 stars, single-person company, no external precision measurement. This is "a research-backed developer's good tool," not "industry-standard validated at scale." If you maintain a CLAUDE.md or SKILL.md, `uvx lintlang scan .` is worth one run.

---

> Open source for learning only. Verify license terms before commercial use.
