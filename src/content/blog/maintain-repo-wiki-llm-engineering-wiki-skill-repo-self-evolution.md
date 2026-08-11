---
title: "maintain-repo-wiki：让 LLM Agent 把工程事实而非总结写进 Wiki"
titleEn: "maintain-repo-wiki-llm-engineering-wiki-skill-repo-self-evolution"
description: "dingrancho-alt/maintain-repo-wiki，13 stars，Python，2026-07-07。面向单仓库/多仓库的生产级工程 Wiki Skill：不把代码「总结成一篇文档」，而是把接口契约、字段传播、业务流程、排障路径这类可验证工程事实组织成能持续更新、审计、检索的知识系统。三种知识库拓扑（Repo/System/Knowledge Repo）、九类页面、Audit→Confirm→Apply 受控写入流程、可选 Capability Layer（Operation→Atomic→Composite 三层模型），配套 changed_files.py / wiki_lint.py / capability_graph.py 脚本。无证据时记为 unknown，不用推测补齐。"
descriptionEn: "dingrancho-alt/maintain-repo-wiki, 13 stars, Python, 2026-07-07. A production-grade engineering Wiki skill for single and multi-repo systems: instead of 'summarizing code into a document,' it organizes verifiable engineering facts — interface contracts, field propagation, business flows, troubleshooting paths — into a knowledge system that can be continuously updated, audited, and searched. Three topology modes (Repo/System/Knowledge Repo), nine page types, an Audit→Confirm→Apply controlled-write workflow, an optional Capability Layer (Operation→Atomic→Composite), and companion scripts: changed_files.py, wiki_lint.py, capability_graph.py. Unknown facts are recorded as unknown, never filled in with guesses."
pubDate: "2026-08-11"
updatedDate: "2026-08-11"
category: "Tech-News"
tags: ["AI Agent", "工程Wiki", "知识库", "开源", "Python", "微服务", "LLM", "Mycelium"]
heroImage: "../../assets/images/maintain-repo-wiki-llm-engineering-wiki-skill-repo-self-evolution-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

大多数「AI 生成 Wiki」的工具做的是同一件事：把代码扔进去，输出一篇 README 式的概述。问题不是这个输出写得不好——而是它不能用：没有字段来源，没有失败路径，没有运行时证据，两个月后已经过时，没有人知道哪一部分还准确。

maintain-repo-wiki 从另一个方向出发：**不总结，只记录可验证的工程事实**，并且把这件事工程化成一个能持续维护的系统。

GitHub: https://github.com/dingrancho-alt/maintain-repo-wiki | ⭐ 13 | Python | 2026-07-07

---

## 它要回答哪些问题

README 开头有一张清单，列出了一个成熟的 Wiki 应当能回答的问题：

- 这个服务的职责、入口、核心模块和上下游边界是什么？
- 一个 HTTP/RPC/event 接口的 source contract、字段来源、必填性、默认值、响应和错误行为是什么？
- 一个字段从入口到 handler、adapter、下游 RPC/event/cache/search/sort 的传播过程是什么；在哪里被映射、覆盖、过滤或兜底？
- 某项业务状态会触发哪些写入、记录、异步任务或用户可见副作用？
- 依赖超时、返空、报错或降级时，用户会看到什么；应查看哪些 metrics、logs、alerts？
- 某次代码、IDL、配置或运行时变更影响哪些 Wiki 页面、跨服务契约和能力链？

这些问题的答案必须回到**源码、IDL/source contract、测试、可验证的运行时证据**。没有证据时，记录为 `unknown` 和下一步检查，而不是用推测补齐。

---

## 三种知识库拓扑

**Repo Mode**：单仓库工程手册。

```bash
python3 <skill>/scripts/init_repo_wiki.py <repo-root>
```

```
<repo-root>/wiki/
├── overview.md
├── source-map.md
├── components/
├── flows/
├── apis/
├── runbooks/
├── queries/
├── questions/
├── decisions/
└── catalog/     # 可选 Capability Layer
```

**System Mode**：只维护跨服务事实——服务目录、依赖图、契约、端到端链路、跨服务字段流——不复制每个仓库的完整内容。

**Knowledge Repo Mode**：建立独立知识库仓库，每个输入仓库保留本地事实，系统层只记录跨仓库关系。`sources.yaml` 记录所有输入来源（URL、本地路径、分支、角色）。

---

## 九类页面的职责划分

| 页面 | 核心问题 |
|------|---------|
| `overview.md` | 服务职责、技术栈、目录地图、入口点和架构 |
| `source-map.md` | 哪段源码对应哪个知识页面；变更后该更新哪里 |
| Component | 模块职责、公开接口、依赖、失败影响、变更注意事项 |
| API | route/method、handler、IDL/source contract、字段表、示例、错误行为 |
| Business Flow | 输入、校验/映射、分支、下游构造、状态副作用、输出、失败模式 |
| Field Propagation | 字段的 source、mapping、destination、default/fallback、下游使用、观测手段 |
| Config / Cache | 配置源、JSON shape、默认值、TTL、失效路径、测试开关、runtime impact |
| External Dependency | hard/degradable 分类、timeout/error、fallback、用户可见影响 |
| Runtime / Runbook | 症状、metrics、logs、alerts、fast checks、mitigation、owner、escalation |
| Query | 脱敏的复用问答、证据、适用范围、知识缺口、权威页面链接 |
| Question | 哪些事实尚未验证，已搜索过什么，下一步查哪里 |
| Decision | 背景、决策、影响、备选方案、重新评估条件 |

---

## 受控写入：Audit → Confirm → Apply

这是这个 Skill 里最关键的设计。Agent 在写 Wiki 之前必须经过三步：

**1. Audit**：确认源码仓库、知识库、base/head；分析受影响页面、相关 Query、冲突、过期风险、证据缺口和未映射变更。

**2. Confirm**：输出拟新增、更新、迁移或废弃的页面清单；等待用户明确确认。初始的「更新 Wiki」请求**不等于确认**。

**3. Apply**：再次确认源码 HEAD 与审计基线未偏离，只修改确认范围；同步必要的 index.md、source map、Query 和系统页面。

**4. Verify**：对本次范围运行 changed-only quality lint，报告实际变更、计划偏差与剩余缺口。

这个流程的核心是：**Agent 不能在一次查询中顺手污染 Wiki**。写入是一个需要用户明确确认的操作，不是推断的结果。

---

## 变更影响分析与 Lint

```bash
# 扫描暂存、未暂存和未跟踪的源码变更，映射到受影响的 Wiki 页面
python3 <skill>/scripts/changed_files.py --wiki wiki

# 显式指定变更文件
python3 <skill>/scripts/changed_files.py --wiki wiki \
  --changed service/handler.py domain/request.py

# 检查已提交的 revision range
python3 <skill>/scripts/changed_files.py --wiki wiki \
  --base origin/main --head HEAD
```

```bash
# 基础结构检查（frontmatter、链接、索引、TODO/TBD/FIXME）
python3 <skill>/scripts/wiki_lint.py wiki

# 完整质量报告（API 字段表、IDL source、依赖 failure impact、Flow、Runbook 等）
python3 <skill>/scripts/wiki_lint.py wiki --quality

# 只检查本次范围（默认 Apply 后门禁）
python3 <skill>/scripts/wiki_lint.py wiki --quality --changed-only
```

---

## 可选的 Capability Layer

Capability Layer 是面向高频业务咨询的可选增强，用三层模型表达「这个系统能不能做 X」：

```
真实执行单元           稳定业务语义              可组合目标
Operation ──────▶ Atomic Capability ──────▶ Composite Capability
HTTP/RPC/function  subject+action+            SEQUENCE/ALL_OF/
event/job/storage  input/output+constraints   ONE_OF/FALLBACK
```

查询结论不是二值的——有五种状态：

| 结论 | 含义 |
|------|------|
| `supported` | 完整链路和约束成立，有运行时状态确认 |
| `conditionally_supported` | 契约成立，但只确认到声明/实现/部署 |
| `partially_supported` | 必需链路中部分满足、部分不满足 |
| `unsupported` | 存在直接、明确的排除证据 |
| `unknown` | 覆盖不足、约束未闭合、证据冲突或运行时状态未确认 |

---

## 这个设计的核心主张

LLM Agent 在代码库里最容易犯的错误是**用推断替代证据**。「这个字段应该是必填的」「这个依赖超时应该返回空」——这类推断在生成 Wiki 时听起来很合理，但一旦写进去就很难被发现是错的，直到线上出现问题的时候。

maintain-repo-wiki 的答案是：**所有事实必须有来源，没有来源就记 unknown**。这听起来像是一个保守的设计，但对于工程知识库来说，一个写着 `unknown` 的字段比一个写着错误答案的字段有用得多——前者告诉读者还需要去查，后者让读者以为已经知道了。

代码仓库是活的。Wiki 也应该是活的，而不是一次生成、永久过时的文档。这个 Skill 试图把「Wiki 维护」变成工程师工作流的一部分：代码变更→映射受影响页面→Audit→Confirm→Apply→Lint。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## maintain-repo-wiki: Engineering Facts, Not Summaries, into Your Wiki

*by Mycelium Protocol*

---

Most "AI-generated Wiki" tools do the same thing: feed in code, get back a README-style overview. The problem isn't that the output is badly written — it's that it's unusable: no field origins, no failure paths, no runtime evidence, stale two months later, nobody knows which parts are still accurate.

maintain-repo-wiki starts from the other direction: **don't summarize, record only verifiable engineering facts** — and engineer the act of doing so into a system that can be maintained continuously.

GitHub: https://github.com/dingrancho-alt/maintain-repo-wiki | ⭐ 13 | Python | 2026-07-07

---

### The Questions It Answers

The README opens with a list of questions a mature Wiki should be able to answer:

- What is this service's responsibility, entry points, core modules, and upstream/downstream boundary?
- What are an HTTP/RPC/event interface's source contract, field origins, required fields, defaults, responses, and error behavior?
- How does a field propagate from entry point through handler, adapter, and downstream RPC/event/cache/search/sort — where is it mapped, overridden, filtered, or defaulted?
- What writes, records, async tasks, or user-visible side effects does a business state transition trigger?
- When a dependency times out, returns empty, or errors: what does the user see, and which metrics/logs/alerts/request identifiers should you check?

All answers must trace back to **source code, IDL/source contract, tests, or verifiable runtime evidence**. When there is no evidence, the fact is recorded as `unknown` with a note on where to look next — never filled in with guesses.

---

### Three Topology Modes

**Repo Mode**: an engineering manual for one repository.

```bash
python3 <skill>/scripts/init_repo_wiki.py <repo-root>
```

Produces `wiki/` under the repo root: overview, source-map, components, flows, apis, runbooks, queries, questions, decisions, and optional capability catalog.

**System Mode**: maintains only cross-service facts — service catalog, dependency graph, contracts, end-to-end request flows, cross-service field flows, system runbooks — without duplicating each repo's full Wiki.

**Knowledge Repo Mode**: a standalone knowledge repository. Each input repo keeps its own local facts; the system layer records only cross-repo relationships. `sources.yaml` records all input sources (URL, local path, branch, role).

---

### Nine Page Types

| Page | Core question |
|------|---------------|
| `overview.md` | Service responsibility, tech stack, directory map, entry points, architecture |
| `source-map.md` | Which source maps to which page; what to update after a change |
| Component | Module responsibility, public interfaces, dependencies, failure impact |
| API | route/method, handler, IDL/source contract, field table, examples, error behavior |
| Business Flow | Input, validation/mapping, branches, downstream construction, side effects, failure modes |
| Field Propagation | Source, mapping, destination, default/fallback, downstream use, observability |
| Config / Cache | Config source, JSON shape, defaults, TTL, invalidation, test toggles, runtime impact |
| External Dependency | hard/degradable, timeout/error, fallback, user-visible impact |
| Runtime / Runbook | Symptoms, metrics, logs, alerts, fast checks, mitigation, owner, escalation |
| Query | Sanitized reusable Q&A, evidence, scope, knowledge gaps, canonical page links |
| Question | Unverified facts, what was already searched, where to look next |
| Decision | Background, decision, impact, alternatives, re-evaluation conditions |

---

### Controlled Writes: Audit → Confirm → Apply

This is the most important design in the Skill. Before writing anything to the Wiki, the agent goes through three gates:

**1. Audit**: confirm the source repo, knowledge base, base/head, and trigger; analyze affected pages, related queries, conflicts, staleness risks, evidence gaps, and unmapped changes.

**2. Confirm**: output a list of pages to add, update, migrate, or retire; wait for explicit user confirmation. An initial "update the Wiki" request **does not count as confirmation**.

**3. Apply**: re-verify the source HEAD hasn't drifted from the audit baseline; edit only the confirmed scope; sync necessary index.md, source map, queries, and system pages.

**4. Verify**: run changed-only quality lint on the scope; report actual changes, plan deviations, and remaining gaps.

The point: **the agent cannot incidentally pollute the Wiki during a query session**. Writes are an explicitly confirmed operation, not the byproduct of reading.

---

### Change Impact Analysis and Lint

```bash
# Map staged/unstaged/untracked source changes to affected Wiki pages
python3 <skill>/scripts/changed_files.py --wiki wiki

# Explicit files
python3 <skill>/scripts/changed_files.py --wiki wiki \
  --changed service/handler.py domain/request.py

# Committed range
python3 <skill>/scripts/changed_files.py --wiki wiki \
  --base origin/main --head HEAD
```

```bash
# Structural checks: frontmatter, links, index, TODO/TBD/FIXME
python3 <skill>/scripts/wiki_lint.py wiki

# Full quality report: API field tables, IDL source, failure impact, Flows, Runbooks
python3 <skill>/scripts/wiki_lint.py wiki --quality

# Changed-only gate (default after Apply)
python3 <skill>/scripts/wiki_lint.py wiki --quality --changed-only
```

---

### Optional Capability Layer

For high-frequency business queries across services, the Capability Layer adds structured reasoning about "can the system do X?" in three tiers:

```
Real execution unit         Stable business semantics    Composable goal
Operation ──────────▶ Atomic Capability ──────────▶ Composite Capability
HTTP/RPC/function      subject+action+               SEQUENCE/ALL_OF/
event/job/storage      input/output+constraints      ONE_OF/FALLBACK
```

Query conclusions are not binary — five states:

| Conclusion | Meaning |
|------------|---------|
| `supported` | Complete chain and constraints hold, runtime state confirmed |
| `conditionally_supported` | Contract holds, confirmed only to declared/implemented/deployed |
| `partially_supported` | Some required chain links confirmed, some explicitly not |
| `unsupported` | Direct, explicit exclusion evidence exists |
| `unknown` | Insufficient coverage, open constraints, conflicting evidence, or unconfirmed runtime state |

---

### The Core Claim

The easiest mistake an LLM agent makes in a codebase is **substituting inference for evidence**. "This field should be required." "This dependency timeout probably returns empty." These inferences sound reasonable when generating a Wiki — but once written, they're nearly impossible to notice as wrong until something breaks in production.

maintain-repo-wiki's answer: **every fact must have a source; if there's no source, write unknown**. This sounds conservative. For an engineering knowledge base, it's strictly more useful: a field that says `unknown` tells the reader they still need to investigate; a field with a wrong answer makes the reader think they already know.

Code repositories are living. Wikis should be too — not a one-time generation that goes stale immediately, but a system that updates as the code changes: change → map affected pages → Audit → Confirm → Apply → Lint.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
