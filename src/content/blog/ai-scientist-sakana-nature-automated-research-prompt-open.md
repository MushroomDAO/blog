---
title: "AI Scientist：Sakana AI 的全自动科研系统，2026 年 3 月登上 Nature"
titleEn: "The AI Scientist: Sakana AI's Fully Automated Research System Published in Nature (March 2026)"
description: "SakanaAI/AI-Scientist，14.6K stars，自定义许可证。首个端到端全自动科学发现系统：LLM 从选题、写代码、跑实验、生成 LaTeX 论文，到自动同行评审，整条流水线不需要人类介入。2026 年 3 月完整工作发表于 Nature，提示词在论文附录全文公开。"
descriptionEn: "SakanaAI/AI-Scientist — 14.6K stars, custom license. The first end-to-end fully automated scientific discovery system: LLM selects topics, writes code, runs experiments, generates LaTeX papers, and conducts automated peer review — no human intervention required. Full work published in Nature, March 2026. All prompts publicly available in the paper appendix."
pubDate: 2026-10-03
heroImage: "../../assets/images/ai-scientist-sakana-nature-automated-research-prompt-open-banner.jpg"
category: "Research"
tags: ["自动科研", "Sakana AI", "Nature", "LLM", "科学发现", "AI Agent"]
lang: "zh-CN"
wechatTitle: "AI Scientist：Nature认证的全自动科研系统"
wechatDigest: "Sakana AI；14.6K星；全自动科研流水线；2026年3月登Nature；提示词在附录全公开"
---

AI 到底能不能做科研？不是「辅助人类做科研」，而是从想选题、写代码、跑实验、写论文，到组织同行评审——全程不需要人介入？

Sakana AI 在 2024 年底给出了第一个完整的系统答案，2026 年 3 月这项工作发表在了 Nature。

GitHub: https://github.com/SakanaAI/AI-Scientist | ⭐ 14,649 | 自定义许可证

---

## 它做什么

**The AI Scientist** 是一个端到端的自动化科学发现框架。给定一个研究领域模板，它会：

1. **选题**：LLM 根据已有文献和实验模板，生成新的研究方向假设
2. **写代码**：调用 Aider（AI 代码编辑工具）实现实验代码
3. **跑实验**：自动执行实验，记录指标
4. **写论文**：生成完整的 LaTeX 学术论文，包含摘要、方法、结果、讨论
5. **同行评审**：另一个 LLM 扮演审稿人，对论文打分并给出评审意见

整个流水线输出的是真实的、可以直接提交给会议的 PDF 论文。

---

## 三个研究模板

项目提供三个由作者维护的模板，分别覆盖：

- **NanoGPT**：字符级语言模型实验（训练、架构变体、泛化）
- **2D Diffusion**：低维扩散模型（生成模型、降噪策略）
- **Grokking**：Transformer 泛化现象（Grokking 加速、权重初始化）

这些模板定义了「合法的实验范围」——AI Scientist 在模板边界内自由探索，而不是在整个 AI 领域里乱试。社区可以贡献新模板，但作者不负责维护社区模板。

---

## 实际产出的论文

README 列出了系统生成的代表性论文，标题包括：

- *DualScale Diffusion: Adaptive Feature Balancing for Low-Dimensional Generative Models*
- *Adaptive Learning Rates for Transformers via Q-Learning*
- *Grokking Through Compression: Unveiling Sudden Generalization via Minimal Description Length*

这些不是摘要或段落——是有方法、有实验、有图表的完整 PDF。Drive 文件夹里存着所有运行结果，包括用 Claude 生成的一批完整论文。

---

## 提示词在 Nature 论文附录全文公开

这件事值得单独说。

2026 年 3 月整项工作发表在 Nature 之后，论文附录包含了系统使用的全部核心提示词——选题提示、实验规划提示、论文生成提示、同行评审提示。

这意味着任何人都可以：
- 看懂系统的完整工作机制
- 直接复现或改进具体模块
- 把提示词移植到自己的研究领域

Sakana AI 不只是发表了结果，而是公开了「如何做到」。

---

## 运行要求

这套系统不轻。

**硬件**：Linux + NVIDIA GPU（CUDA），CPU 几乎不可用。当前三个模板在 CPU 上跑「可能需要不切实际的时长」。

**API 费用**：每篇论文需要多轮 LLM 调用（选题、代码、实验分析、论文写作、评审），推荐使用 GPT-4o 或 Claude Sonnet 3.5 等边界模型，单次完整运行成本不低。

**安装**：
```bash
conda create -n ai_scientist python=3.11
conda activate ai_scientist
sudo apt-get install texlive-full   # LaTeX 环境，安装时间较长
pip install -r requirements.txt
```

支持 OpenAI、Anthropic、AWS Bedrock、Vertex AI 等多种 API 后端，也支持开源权重模型，但效果推荐「能力不低于 GPT-4」的边界模型。

---

## 安全警告

README 明确标注：

> **Caution!** 这个代码库会执行 LLM 生成的代码。存在使用危险包、访问网络、spawn 进程等风险。请务必容器化并限制网络访问。

系统会让 LLM 写代码然后直接运行。这不是问题，而是设计——实验必须在真实环境里跑。但在生产环境或者不受控制的机器上跑之前，Docker 隔离是必须的。

---

## 已知局限

**幻觉引用**：论文生成阶段会出现不存在的参考文献。这是当前 LLM 科研能力的核心短板之一。

**领域局限**：三个模板覆盖的都是可以快速实验的小规模 ML 任务。化学、生物、物理等需要真实实验的领域暂不适用。

**论文质量**：生成的论文通过了 LLM 评审，但人工审稿的质量评估更复杂。Sakana AI 在 blog 和论文里对此都有比较诚实的讨论。

---

## 许可证说明

项目使用「The AI Scientist Source Code License Version 1.0」，基于 Responsible AI Source Code License (RAIL) v1.1，**不是标准开源许可证**。具体使用限制需要阅读完整许可文本，商业用途尤其需要核实条款。

---

## 意义

Nature 接受这篇论文，本身是一个信号：AI 辅助科研从「能做到」到「机构认可」的边界在移动。

提示词公开在附录是另一个信号：作者不只是展示结果，而是把整个方法论透明化——任何研究组都可以拿这套框架研究「自动化科研本身的局限在哪」。

对多数开发者来说，最实际的价值可能不是直接用它跑科研，而是把它拆开，看一个「让 LLM 完成复杂长程任务」的完整系统是怎么做提示词工程和流程设计的。附录已经把这部分彻底开放了。

---

> 本文涉及软件使用自定义许可证（基于 RAIL v1.1），商业使用前请阅读完整许可文本。仅供技术学习参考。

---

<!--EN-->

## The AI Scientist: Fully Automated Research, Published in Nature

Can AI actually do science? Not "assist humans with science" — but go from idea generation to code, experiments, full paper, and peer review, without human intervention?

Sakana AI released the first complete system-level answer in late 2024. In March 2026, the full work was published in Nature.

GitHub: https://github.com/SakanaAI/AI-Scientist | ⭐ 14,649 | Custom license

---

### What It Does

**The AI Scientist** is an end-to-end automated scientific discovery framework. Given a research domain template, it:

1. **Ideation**: LLM generates new research hypotheses from existing literature and experimental templates
2. **Coding**: Calls Aider (an AI code editor) to implement experiment code
3. **Experimentation**: Executes experiments automatically, records metrics
4. **Paper writing**: Generates a complete LaTeX academic paper — abstract, methods, results, discussion
5. **Peer review**: A separate LLM instance acts as reviewer, scores and critiques the paper

The pipeline outputs real, conference-submittable PDF papers.

---

### Three Research Templates

The project ships three author-maintained templates:

- **NanoGPT**: Character-level language model experiments (training, architecture variants, generalization)
- **2D Diffusion**: Low-dimensional diffusion models (generative modeling, denoising strategies)
- **Grokking**: Transformer generalization (grokking acceleration, weight initialization)

Templates define the "legal" experiment space — the AI Scientist explores freely within template boundaries. The community can contribute new templates, but authors don't maintain community contributions.

---

### Prompts Published in the Nature Appendix

The full work published in Nature (March 2026) includes all core prompts in the appendix — ideation prompts, experiment planning prompts, paper generation prompts, peer review prompts.

This means anyone can:
- Understand the complete system mechanism
- Reproduce or improve specific modules directly
- Port prompts to their own research domain

Sakana AI didn't just publish results — they published the how.

---

### Requirements

**Hardware**: Linux + NVIDIA GPU (CUDA). CPU runs are described as "infeasible" for current templates.

**API cost**: Each paper requires many LLM call rounds (ideation, coding, analysis, writing, review). Authors recommend frontier models above GPT-4 capability. A single full run is not cheap.

**Safety**: README explicitly warns that the system executes LLM-generated code. Containerize and restrict network access before running.

---

### Known Limitations

- **Hallucinated citations**: Paper generation produces non-existent references — a core LLM research limitation
- **Domain scope**: Templates cover small-scale ML tasks that can be experimentally validated quickly; chemistry, biology, physics requiring physical experiments are out of scope
- **Paper quality**: Papers pass LLM review; human expert evaluation is more nuanced — Sakana AI discusses this honestly in the paper and blog

---

### License Note

The project uses "The AI Scientist Source Code License Version 1.0," based on RAIL v1.1. **This is not a standard open-source license.** Review the full license text before commercial use.

---

### What It Means

Nature accepting this paper signals that AI-assisted research is crossing from "possible" to "institutionally recognized."

Publishing prompts in the appendix signals transparency: any research group can use this framework to study "where are the limits of automated research?" — the methodology is fully open.

For most developers, the most practical value may not be running it for actual research, but dissecting it to understand how a complex long-horizon LLM task system is structured in terms of prompt engineering and workflow design. The appendix makes this completely accessible.

---

> This project uses a custom license based on RAIL v1.1. Review the full license text before commercial use. For technical reference only.
