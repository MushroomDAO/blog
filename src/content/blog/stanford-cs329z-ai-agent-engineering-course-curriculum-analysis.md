---
title: "斯坦福 CS329Z：AI Agent 工程正式进入大学课程，拆解全部 22 讲内容"
titleEn: "Stanford CS329Z: AI Agent Engineering Enters the University Curriculum — Breaking Down All 22 Lectures"
description: "斯坦福 2026 年秋季新增 CS329Z《AI Agent 工程》课程，由 Diyi Yang、Michael Ryan 和 John Yang 主讲。本文完整拆解 11 周 22 讲的课程结构、必读论文清单和两份作业，分析它对 Agent 工程师的实用价值。"
descriptionEn: "Stanford added CS329Z 'Engineering AI Agents' to its Fall 2026 curriculum, taught by Diyi Yang, Michael Ryan, and John Yang. This article breaks down all 11 weeks and 22 lectures, required reading list, and two assignments — and what the curriculum tells us about the state of AI agent engineering as a discipline."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: Research
tags: ["AI", "Agent", "斯坦福", "课程", "RAG", "评测", "DSPy", "MCP", "教育", "工程"]
heroImage: "../../assets/images/stanford-cs329z-ai-agent-engineering-course-curriculum-analysis-banner.jpg"
author: "Mycelium Protocol"
---

AI Agent 从研究话题变成工程学科，有一个重要的信号：大学开始开课了。

斯坦福 2026 年秋季新增了 **CS329Z《Engineering AI Agents》**（AI Agent 工程），由 Diyi Yang、Michael Ryan 和 John Yang 共同主讲。课程官网：[cs329z.stanford.edu](https://cs329z.stanford.edu/)

这不是一门"AI 概论"或"如何使用 ChatGPT"的课。课程从第一周就让学生从零实现 RAG 流水线和工具调用系统，第二份作业就要求写 LLM-as-Judge 和错误分析。

本文完整拆解 11 周 22 讲的内容，分析它的知识体系和对实践者的价值。

---

## 课程定位：从单一模型到复合 AI 系统

课程第一讲的标题是「What Are Agentic Systems?」，核心问题是：**从单一模型到复合 AI 系统，什么时候复合系统赢？**

必读论文是 Zaharia 等人 2024 年的 BAIR Blog 文章《The Shift from Models to Compound AI Systems》——这篇文章提出了一个至今仍有价值的判断：AI 的竞争优势正在从"更强的模型"转移到"更好的系统组合"。

课程明确给出了三个 Agent 工程的核心挑战：
1. **分解**（Decomposition）：如何把任务拆给合适的组件
2. **数据**（Data）：Agent 需要什么数据，怎么收集
3. **评测**（Evaluation）：怎么知道 Agent 做对了

这三个挑战构成了整个课程的骨架。

---

## 11 周 22 讲：完整课程结构

### 第 1 周：基础层

**9/23 - 第 1 讲：基础与全景**
从单体模型到复合 AI 系统到 Agent 的演进路径，三个工程挑战，课程导论。

**9/28 - 第 2 讲：面向开发者的 LLM**
APIs & SDKs（以 litellm 为例）、结构化输出与约束生成、解码策略与测试时计算、**上下文工程（Context Engineering）**、模型选择、成本与延迟权衡。

必读：Anthropic 的[《Building Effective Agents》](https://www.anthropic.com/engineering/building-effective-agents)和[《Effective Context Engineering》](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)。

---

### 第 2 周：核心构件

**9/30 - 第 3 讲：RAG（从零实现）**
Grounding 与幻觉问题、Embedding 与向量存储、Chunking 策略、混合检索、Cross-encoder 和 ColBERT（后期交互）。

**关键**：动手实现 RAG 流水线，不是调包。

**10/5 - 第 4 讲：工具调用与函数调用**
REPL、Function-calling API、**Model Context Protocol（MCP）**、好工具的设计原则、代码执行沙箱、错误处理与重试。

必读：MCP 规范（2025 年 Linux Foundation 版本）。

---

### 第 3 周：框架与设计模式

**10/7 - 第 5 讲：框架与编排**
DSPy（Signatures、Modules、Optimizers）、LangChain/LangGraph、LlamaIndex；框架抽象了什么、从零实现获得了什么；选择合适抽象层次的原则。

**10/12 - 第 6 讲：Agent 设计模式与脚手架**
Workflow vs. Agent 的分类法、五种可组合工作流模式、Agent 模式（**ReAct**、Plan-and-Execute、Reflection），以及脚手架作为设计决策。

必读：ReAct 论文（ICLR 2023）。

---

### 第 4 周：记忆与多 Agent

**10/14 - 第 7 讲：Agent 记忆架构**
短期 vs 长期记忆、记忆作为工具调用动作、文件系统作为外化记忆、结构化记忆范式、跨 Agent 记忆。

必读：MemGPT（"Towards LLMs as Operating Systems"）；拓展阅读：Mem0、生成式 Agent。

**10/19 - 第 8 讲：多 Agent 系统**
单 Agent vs 多 Agent 架构、编排模式、状态转移与交接、委托与协作模式、协调挑战与错误传播。

必读：AutoGen 论文（COLM 2024）；拓展阅读：多 Agent 失败原因分析（「Why Do Multi-Agent LLM Systems Fail?」）、"Don't Sleep on Single-agent Systems"。

---

### 第 5 周：优化

**10/21 - 第 9 讲：优化全景**
从 Prompt 到微调的优化路径；Prompt 优化（GEPA、MIPROv2、OPRO、TextGrad）；测试时计算扩展；LoRA/QLoRA；蒸馏；RLHF/DPO 概览；**何时优化 Prompt vs 权重 vs 推理计算**。

必读：GEPA（2026 年的新论文，Prompt 进化可超越 RL）。

**10/26 - 第 10 讲：嘉宾讲座（TBA）**

---

### 第 6 周：数据工程

**10/28 - 第 11 讲：Agent 需要什么数据**
Trace、示范和反馈；优化用数据 vs 评测用数据；**数据飞轮**；合成数据生成；从人机交互收集数据。

**11/2 - 第 12 讲：数据选择与质量**
最大信息量数据的发现、过滤与选择策略、精小但精准的基准集、标注实践、质量评估、从 Agent Trace 构建数据集。

必读：SWE-smith 论文（如何为 SE Agent 扩展数据）；LIMA（"Less Is More for Alignment"）。

---

### 第 7 周：评测

**11/4 - 第 13 讲：评测基础与基准设计**
为什么 Agent 评测难、**四元组框架**（请求、环境、停止条件、评分器）、好基准的特征、真实脚手架的重要性。

**11/9 - 第 14 讲：LLM-as-Judge 与评测基础设施**
三类评分器类型、Judge Prompt 设计、已知偏差、Pairwise vs Pointwise 评估、非确定性指标（pass@k vs pass^k）、Harness 设计、Anthropic 的 8 步路线图。

必读：Anthropic 的「Demystifying Evals for AI Agents」；AutoMetrics 论文（自动生成评估器）。

---

### 第 8 周：安全

**11/11 - 第 15 讲：Agent 安全与护栏**
工具访问的隐私风险、**Prompt Injection（包括间接注入）**、Red-teaming、沙箱与权限模型、输出护栏、法律责任、负责任部署、Human-in-the-loop 模式。

必读：PrivacyLens、LLM Agent 隐私风险分析、去匿名化攻击论文。

**11/16 - 第 16 讲：嘉宾讲座（TBA）**

---

### 第 9 周：编码 Agent 与主动 Agent

**11/18 - 第 17 讲：编码与软件 Agent**
编码 Agent 的端到端工作流；SWE-agent、**Claude Code**、OpenHands 三种架构对比；脚手架作为设计决策；SWE-bench 与四元组框架的实际应用；软件开发的未来。

必读：SWE-agent 论文（NeurIPS 2024）、OpenHands 论文（ICLR 2025）；拓展阅读：Claude Code 最佳实践、Effective Harnesses。

**11/30 - 第 18 讲：主动 Agent（Proactive Agents）**
从被动到主动；**General User Models（GUM）**；下一动作预测；开源主动个人 Agent；隐私与信任含义；何时 Agent 应主动发起 vs 等待（混合主动性）。

---

### 第 10-11 周：前沿与展示

**12/2 - 第 19 讲：前沿与开放问题**
多模态 Agent、Web Agent 与 Computer Use、科学 Agent、长时运行 Agent 架构、生产与可观测性（Tracing、监控、成本管理）；可靠性、可扩展性、可解释性的开放问题。

---

## 两份作业：从实现到评测

### 作业一：从零构建 Agent

要求学生编写一个能够**检索论文、调用工具并完成推理**的 Agent——对应第 2-5 讲的内容。这不是调用已有的 Agent 框架，而是从头实现核心组件。

### 作业二：评测工程

第二份作业转向评测：
- **代码评分器**：基于规则或代码的确定性评分
- **LLM-as-Judge**：设计 Judge Prompt，处理已知偏差
- **错误分析**：系统地分析 Agent 失败的模式

评测在 AI 工程里往往被低估，CS329Z 单独用一周加作业来处理它，这个比重本身就是一个信号。

---

## 课程必读清单：20 篇关键文献

从整个课程的必读列表里，整理出几个值得关注的模式：

**基础层**（值得任何 Agent 工程师读的）
- Zaharia et al.《The Shift from Models to Compound AI Systems》
- Anthropic《Building Effective Agents》
- Anthropic《Effective Context Engineering》
- Yao et al.《ReAct: Synergizing Reasoning and Acting》（ICLR 2023）

**评测层**（容易被忽视但最重要）
- Zhu et al.《Establishing Best Practices for Building Rigorous Agentic Benchmarks》
- Anthropic《Demystifying Evals for AI Agents》
- Ryan et al.《AutoMetrics》（自动生成评估器）

**工程层**
- MCP 规范（Linux Foundation 2025）
- Khattab et al.《DSPy》（ICLR 2024）
- Wu et al.《AutoGen》（COLM 2024）
- Packer et al.《MemGPT》

**安全层**
- 间接 Prompt Injection 相关论文
- OpenAI《Understanding Prompt Injections》

---

## 这门课告诉我们什么

### Agent 工程已经有了标准知识体系

CS329Z 的课程结构说明，AI Agent 工程作为一个学科，已经有了足够清晰的知识边界：RAG → 工具调用 → Agent Loop → 记忆 → 多 Agent → 优化 → 数据 → 评测 → 安全。

这个体系不是凭空发明的，而是从过去两年的大量工程实践里沉淀出来的。斯坦福能开这门课，说明这些知识已经稳定到可以教学的程度。

### 评测和数据工程是被低估的核心技能

课程把评测单独用两讲处理（第 13、14 讲），数据工程也用了两讲（第 11、12 讲），共占 22 讲里的 4 讲。

很多 Agent 开发者花大量时间在模型选择和 Prompt 调整上，却很少系统地做评测。CS329Z 的比重分配暗示了一个判断：**会评测的工程师，比只会 Prompting 的工程师更值钱。**

### MCP 已经是标准课程内容

MCP（Model Context Protocol）出现在第 4 讲的必读清单里。这个协议去年还是新东西，现在斯坦福已经把它列为 Agent 工程师的必知内容。

### 安全是一等公民

安全专门占了一整讲，且覆盖的不是抽象的安全原则，而是具体的攻击类型（Prompt Injection、间接注入、去匿名化攻击）和防御手段（沙箱、权限模型、输出护栏）。课程把 Prompt Injection 定性为"Frontier Security Challenge"——不是可选项，是必须面对的工程问题。

---

## 课程链接

官方网站：[cs329z.stanford.edu](https://cs329z.stanford.edu/)

主讲教师：Diyi Yang（Stanford NLP）、Michael Ryan、John Yang（SWE-agent 团队成员之一）

<!--EN-->

When AI agents move from a research topic to an engineering discipline, one signal stands out: universities start teaching it.

Stanford added **CS329Z "Engineering AI Agents"** to its Fall 2026 curriculum, co-taught by Diyi Yang, Michael Ryan, and John Yang. Course website: [cs329z.stanford.edu](https://cs329z.stanford.edu/)

This isn't an "AI Overview" or "How to Use ChatGPT" course. From week one, students implement a RAG pipeline and tool-calling system from scratch. The second assignment requires writing an LLM-as-Judge and running error analysis.

This article breaks down all 11 weeks and 22 lectures.

---

## Course Positioning: From Single Models to Compound AI Systems

The first lecture is titled "What Are Agentic Systems?" The central question: **on the spectrum from monolithic models to compound AI systems to agents — when do compound systems win?**

Required reading is Zaharia et al.'s 2024 BAIR Blog post "The Shift from Models to Compound AI Systems" — a paper arguing that competitive advantage in AI is shifting from "stronger models" to "better system composition."

The course explicitly frames three core engineering challenges for agents:
1. **Decomposition**: How to break tasks across the right components
2. **Data**: What data agents need and how to collect it
3. **Evaluation**: How to know the agent is doing the right thing

These three challenges form the skeleton of the entire course.

---

## Complete Course Structure: 11 Weeks, 22 Lectures

### Week 1: Foundations

**9/23 — Lecture 1: Foundations & Landscape**
The spectrum from monolithic models to compound AI systems; when compound systems win; the three engineering challenges.

**9/28 — Lecture 2: LLMs for Builders**
APIs & SDKs (litellm), structured I/O and constrained generation, decoding strategies and test-time compute, **context engineering**, model selection, cost/latency tradeoffs.

Required: Anthropic's "Building Effective Agents" and "Effective Context Engineering for AI Agents."

---

### Week 2: Core Building Blocks

**9/30 — Lecture 3: RAG (from scratch)**
Grounding and hallucination, embeddings and vector stores, chunking strategies, hybrid search, cross-encoders and ColBERT. Hands-on: build a RAG pipeline from scratch.

**10/5 — Lecture 4: Tool Use & Function Calling**
The REPL, function-calling APIs, **Model Context Protocol (MCP)**, designing good tools, code-execution sandboxes, error handling and retries.

Required: MCP Specification (Linux Foundation, 2025).

---

### Week 3: Frameworks & Patterns

**10/7 — Lecture 5: Frameworks & Orchestration**
DSPy (signatures, modules, optimizers), LangChain/LangGraph, LlamaIndex; what frameworks abstract vs. what you built from scratch; choosing abstraction levels.

**10/12 — Lecture 6: Agent Design Patterns & Scaffolds**
Workflows vs. agents taxonomy; five composable workflow patterns; agent patterns (**ReAct**, plan-and-execute, reflection); scaffolds as design decisions.

Required: ReAct paper (ICLR 2023).

---

### Week 4: Memory & Multi-Agent

**10/14 — Lecture 7: Agent Memory Architectures**
Short- vs. long-term memory, memory as tool-based actions, file system as externalized memory, structured memory paradigms, cross-agent memory.

Required: MemGPT. Extended: Mem0, Generative Agents.

**10/19 — Lecture 8: Multi-Agent Systems**
Single vs. multi-agent architectures, orchestration patterns, handoffs and state transfer, delegation and collaboration, coordination challenges and error propagation.

Required: AutoGen (COLM 2024). Extended: "Why Do Multi-Agent LLM Systems Fail?", "Don't Sleep on Single-agent Systems."

---

### Week 5: Optimization

**10/21 — Lecture 9: Optimization Landscape**
From prompts to fine-tuning; prompt optimization (GEPA, MIPROv2, OPRO, TextGrad); test-time compute scaling; LoRA/QLoRA; distillation; RLHF/DPO; **when to optimize prompts vs. weights vs. inference compute**.

Required: GEPA (2026) — prompt evolution outperforming RL.

---

### Week 6: Data Engineering

**10/28 — Lecture 11: What Data Do Agents Need?**
Traces, demonstrations, and feedback; data for optimization vs. evaluation; **data flywheels**; synthetic data generation; collecting data from human-agent interaction.

**11/2 — Lecture 12: Data Selection & Quality**
Finding maximally informative data, filtering and selection strategies, tiny-but-targeted benchmarks, annotation practices, quality assessment, building datasets from agent traces.

Required: SWE-smith, LIMA.

---

### Week 7: Evaluation

**11/4 — Lecture 13: Evaluation Fundamentals & Benchmark Design**
Why agent evals are hard; the **4-tuple framework** (request, environment, stopping criteria, scorer); properties of good benchmarks; realistic scaffolding.

**11/9 — Lecture 14: LLM-as-Judge & Evaluation Infrastructure**
Three grader types, judge prompt design, known biases, pairwise vs. pointwise evaluation, non-determinism metrics (pass@k vs. pass^k), harness design, Anthropic's 8-step roadmap.

Required: Anthropic's "Demystifying Evals for AI Agents"; AutoMetrics.

---

### Week 8: Safety

**11/11 — Lecture 15: Agent Safety & Guardrails**
Privacy risks of tool access, **prompt injection (including indirect injection)**, red-teaming, sandboxing and permission models, output guardrails, liability, responsible deployment, human-in-the-loop patterns.

---

### Week 9: Coding & Proactive Agents

**11/18 — Lecture 17: Coding & Software Agents**
How coding agents work end-to-end; **SWE-agent, Claude Code, and OpenHands** architectures compared; SWE-bench and the 4-tuple framework in practice.

Required: SWE-agent (NeurIPS 2024), OpenHands (ICLR 2025). Extended: Claude Code Best Practices.

**11/30 — Lecture 18: Proactive Agents**
From reactive to proactive; General User Models (GUM); Next Action Prediction; open-source proactive personal agents; mixed initiative design.

---

### Week 11: Frontiers

**12/2 — Lecture 19: Open Problems**
Multimodal agents, web agents and computer use, science agents, long-running agent architectures, production observability (tracing, monitoring, cost management).

---

## Two Assignments: From Implementation to Evaluation

**Assignment 1: Build an Agent From Scratch**
Students write an agent that retrieves papers, calls tools, and completes reasoning tasks — corresponding to weeks 2-5. Not "use an existing framework" but implement the core components.

**Assignment 2: Evaluation Engineering**
- **Code scorer**: deterministic, rule-based or code-based scoring
- **LLM-as-Judge**: design judge prompts, handle known biases
- **Error analysis**: systematically analyze failure patterns

Evaluation is often underestimated in AI engineering. CS329Z allocating a full week plus an assignment to it is itself a signal.

---

## What This Course Tells Us

**Agent engineering has a stable knowledge base.** CS329Z's curriculum structure shows that the field now has clear enough boundaries to be taught: RAG → Tool Use → Agent Loop → Memory → Multi-Agent → Optimization → Data → Evaluation → Safety. This knowledge stabilized from two years of engineering practice.

**Evaluation and data engineering are undervalued core skills.** The course gives 4 of 22 lectures to evaluation and data engineering combined. Many engineers spend most of their time on model selection and prompting while doing minimal systematic evaluation. The allocation signals: engineers who can build evaluation systems are more valuable than engineers who can only prompt.

**MCP is now standard curriculum.** The Model Context Protocol appears in week 2's required reading. A protocol that was new last year is now required knowledge for Stanford agent engineers.

**Safety is a first-class citizen.** A dedicated lecture covers specific attack types (prompt injection, indirect injection, deanonymization) and defenses (sandboxing, permission models, output guardrails). The course frames prompt injection as a "Frontier Security Challenge" — not optional content.

---

## Link

Course website: [cs329z.stanford.edu](https://cs329z.stanford.edu/)

Instructors: Diyi Yang (Stanford NLP), Michael Ryan, John Yang (SWE-agent team)
