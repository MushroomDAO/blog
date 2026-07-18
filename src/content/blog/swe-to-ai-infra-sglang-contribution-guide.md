---
title: "从大厂 SWE 到 AI Infra：一年入门指南，从贡献 SGLang PR 开始"
titleEn: "From Big-Tech SWE to AI Infra in One Year: A Guide Starting with SGLang Contributions"
description: "一位从大厂业务代码转型的工程师分享：如何在一年内从零开始入门 AI Infra，以贡献 SGLang（LMSys 的 LLM 推理框架）PR 为路径，包含如何阅读大型开源代码库、如何找到第一个可贡献的 PR、以及 AI 基础设施的核心概念入门。"
descriptionEn: "A software engineer who transitioned from big-tech business code to AI infrastructure in one year shares their path: learning to navigate massive open-source codebases like SGLang (LMSys's LLM serving framework), finding and completing meaningful PRs, and building the foundations needed for AI infra work. Practical guide for newcomers."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-Experiment"
tags: ["AI基础设施", "SGLang", "LLM推理", "职业转型", "开源贡献", "AI Infra", "大模型", "工程师"]
heroImage: "../../assets/images/swe-to-ai-infra-sglang-contribution-guide-banner.jpg"
---

> **来源**: 小红书作者 Ccyest (@Ccyest) 的个人经历分享  
> **主题**: 从大厂 SWE 转型 AI Infra，以 SGLang 贡献为切入点

---

## 一年前的状态

业务代码、CRUD、需求评审、代码 review、上线、hotfix。

这是大多数大厂 SWE 的日常。技术扎实，但离 AI 的核心——模型推理、分布式训练、GPU 调度——感觉很远。

Ccyest 一年前就是这个状态。现在，他在给 SGLang 提 PR。

这篇文章分享他的转型路径，特别关注三件事：**如何转、如何读巨型开源代码库、如何找到并完成第一个好 PR**。

---

## 什么是 SGLang？为什么从这里入手？

[SGLang](https://github.com/sgl-project/sglang) 是 UC Berkeley LMSys 团队（Chatbot Arena 的团队）开发的 LLM 推理框架。

**核心价值**：在不降低模型准确率的情况下，大幅提升 LLM 的推理吞吐量和延迟。

它在 LLM 部署栈里的位置：

```
用户请求
    ↓
API Server（FastAPI/OpenAI 兼容接口）
    ↓
SGLang Runtime（调度、批处理、KV Cache 管理）
    ↓
模型权重（在 GPU 上）
    ↓
推理结果
```

为什么 SGLang 是入门 AI Infra 的好切入点：

1. **代码质量高**：LMSys 团队的工程水平，文档相对完整
2. **活跃社区**：issue 和 PR 很多，新人贡献空间大
3. **覆盖面广**：涉及 CUDA、Python、分布式系统、API 设计，从哪个角度都能切入
4. **SGLang-Omni**：最新的多模态扩展，更多新 feature 等待实现，低挂果（low-hanging fruit）多

---

## 第一步：读懂一个你完全不懂的巨型代码库

这是转型的第一个硬关——SGLang 的代码库有几万行，涉及你不熟悉的技术栈。

**不能从头读，要有策略。**

### 方法一：从入口点出发

找到代码库的主要入口，理解它做了什么：

```bash
# SGLang 的典型启动方式
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-8B-Instruct \
    --port 30000

# 找到这个命令对应的代码：
# sglang/launch_server.py → SRT Server → Scheduler → Worker
```

跟着执行路径走，你会自然遇到所有核心模块。

### 方法二：用 AI Agent 辅助

现在有了 Claude Code、Cursor、DeepWiki 等工具，读大型代码库的效率大幅提升：

```
# 实际工作流
1. 用 DeepWiki 生成 SGLang 的架构概览（https://deepwiki.com/sgl-project/sglang）
2. 用 Claude Code 问："这个函数在做什么，它被谁调用？"
3. 用 Cursor 的 go-to-reference 跳转到调用方
```

不是让 AI 替你读，而是用 AI 作为导航工具，帮你在代码图里快速定向。

### 方法三：跑起来，然后改一处

把 SGLang 跑起来，然后改一个小地方，看效果变化。这是理解系统行为最快的方法：

```python
# 比如修改 max_batch_size 的默认值，看吞吐量怎么变
# 或者在 scheduler 里加一行日志，看它在什么情况下调度
```

通过"改 → 观察 → 理解"的循环，建立对系统的直觉。

---

## 第二步：找到一个好的第一个 PR

随机挑一个 issue 可能导致两个结果：要么太难，做不完；要么太简单，没收获。

**找 good first issue 的策略**：

```bash
# 在 GitHub 上过滤
https://github.com/sgl-project/sglang/issues?q=label%3A"good+first+issue"+is%3Aopen

# 或者搜索特定类型
https://github.com/sgl-project/sglang/issues?q=label%3A"documentation"+is%3Aopen
```

### 好的第一个 PR 的特征

1. **范围清晰**：问题描述明确，解决方案是"加一个功能"或"修一个 bug"，不是"重构整个模块"
2. **有测试路径**：你能自己验证修复是否正确
3. **不需要大量领域知识**：Python 层的改动比 CUDA kernel 改动容易入手
4. **维护者有回应**：看 issue 下面的讨论，维护者如果对这个问题有兴趣，你的 PR 更容易被 merge

### Ccyest 的路径

他选择了 **SGLang-Omni**（多模态扩展）作为切入点，原因：
- 比 core SGLang 新，代码更现代
- Feature 还在快速增加，新功能 PR 比 bugfix 更有意思
- 社区相对小，维护者更容易注意到新贡献者

**联系方式**：如果你对 SGLang-Omni 社区有兴趣，可以通过主包联系（原帖中有说明）。

---

## 第三步：完成你的第一个 PR

这是很多人卡住的地方——不是不会写代码，而是不知道 PR 应该是什么样子。

### PR 的标准流程

```bash
# 1. Fork + 创建 branch
git checkout -b feat/your-feature-name

# 2. 写代码 + 写测试
# SGLang 的测试在 tests/ 目录，pytest 运行

# 3. 本地跑测试
pytest tests/test_your_component.py -v

# 4. 检查代码风格
pre-commit run --all-files  # SGLang 用 pre-commit

# 5. Push + 开 PR
# PR 标题格式：[Component] Short description
# 比如：[Scheduler] Fix batch size overflow in continuous batching
```

### PR 描述要写什么

好的 PR 描述包含：
- **Why**：为什么需要这个改动（link 到对应的 issue）
- **What**：改了什么（简要描述，不需要逐行解释）
- **How to test**：怎么验证这个改动正确
- **Benchmark**（如果涉及性能）：改动前后的对比数据

### 处理 Code Review

你的 PR 会收到 review 意见。常见的：
- 代码风格问题（格式化、命名）
- 边界条件没处理
- 测试覆盖不够
- 更好的实现方式

这是学习的机会，不是批评。认真对待每一条 review 意见，比写 10 个不被 merge 的 PR 学到的多。

---

## AI Infra 的核心概念入门清单

如果你完全是新手，以下概念需要在入门过程中逐步建立：

### 模型推理层
- **KV Cache**：Key-Value Cache，Transformer 推理加速的核心机制
- **Continuous Batching**：动态批处理，提升 GPU 利用率
- **PagedAttention**：vLLM 提出的 KV Cache 管理方法，SGLang 也有类似实现
- **Tensor Parallelism**：大模型跨多 GPU 并行的方法

### 服务层
- **OpenAI 兼容 API**：大多数 LLM 服务都兼容这个接口，理解它的参数
- **Streaming**：流式输出的实现（SSE / WebSocket）
- **Load Balancing**：多实例部署时的请求分发

### 学习资源推荐
- [LMSys Blog](https://lmsys.org/blog/)：最直接的 SGLang 相关文章
- [vLLM 论文](https://arxiv.org/abs/2309.06180)：PagedAttention，KV Cache 管理的奠基工作
- [SGLang 论文](https://arxiv.org/abs/2312.07104)：理解 SGLang 的设计动机

---

## 一年时间线参考

```
Month 1-2:  建立基础
            - Linux 命令行熟练
            - Python 进阶（async, multiprocessing）
            - GPU 基础知识（CUDA 概念，不需要写 CUDA）

Month 3-4:  读懂一个框架
            - 把 SGLang 跑起来
            - 读 core 代码路径
            - 跑 benchmark

Month 5-6:  第一个贡献
            - 找到 good first issue
            - 提第一个 PR
            - 处理 review，merge

Month 7-9:  深入专题
            - 选一个子方向深入（KV Cache / 调度 / 多模态）
            - 多提几个有实质性内容的 PR

Month 10-12: 建立声誉
             - 在 issue 里帮别人解答
             - 参与更大的 feature 设计讨论
             - 考虑做 Roadshow（分享自己的学习/贡献经历）
```

---

## 最后一点

Ccyest 最后说：分享这些，是希望它对你有所帮助，也能作为一条路径参考。

AI Infra 的门槛看起来高，主要是因为"不知道从哪开始"。从贡献 SGLang 开始，这条路是走得通的。

如果你有兴趣参与 SGLang-Omni 社区，在原帖的评论区可以找到联系方式。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。  
> 内容基于 Ccyest 在小红书发布的个人经历分享

<!--EN-->

> **TL;DR**: A software engineer who transitioned from writing business code at a big tech company to contributing PRs to SGLang (LMSys's LLM serving framework) shares the practical path: how to navigate massive open-source codebases, find a meaningful first PR, and build AI infra foundations — all within one year. Uses SGLang / SGLang-Omni as the concrete entry point.

---

## Why SGLang?

SGLang is UC Berkeley LMSys's LLM inference framework — the team behind Chatbot Arena. It handles scheduling, batching, and KV cache management for LLM serving. High code quality, active community, lots of room for contributions from newcomers.

SGLang-Omni (the multimodal extension) has more low-hanging fruit: new features being added rapidly, smaller community, easier for newcomers to get noticed.

## How to Read a Massive Codebase You Know Nothing About

**Strategy 1 — Follow the entry point**: Find the main startup command, trace the execution path through the code. You'll encounter all core modules naturally.

**Strategy 2 — AI-assisted navigation**: Use DeepWiki for architecture overview, Claude Code or Cursor for "what does this function do and who calls it?" AI is a navigation tool, not a replacement for reading.

**Strategy 3 — Run, change one thing, observe**: Make a small, safe modification (add a log statement, change a config value), observe the behavior change. "Modify → observe → understand" builds intuition faster than reading alone.

## Finding a Good First PR

Filter for `good-first-issue` labels. A good first PR has: clear scope, testable correctness, Python-layer changes (easier than CUDA), and an engaged maintainer in the issue thread.

## The One-Year Timeline

- **Month 1-2**: Linux CLI fluency, Python async/multiprocessing, GPU basics (concepts, not CUDA programming)
- **Month 3-4**: Get SGLang running, read core execution path, run benchmarks
- **Month 5-6**: First contribution — find an issue, submit PR, handle review, get merged
- **Month 7-9**: Pick a sub-area to go deep (KV cache, scheduling, multi-modal)
- **Month 10-12**: Build reputation — answer questions in issues, participate in feature design discussions

## Core Concepts to Build

| Layer | Key Concepts |
|---|---|
| Inference | KV Cache, Continuous Batching, PagedAttention, Tensor Parallelism |
| Serving | OpenAI-compatible API, Streaming (SSE), Load Balancing |

**Resources**: [LMSys Blog](https://lmsys.org/blog/) · [vLLM paper](https://arxiv.org/abs/2309.06180) · [SGLang paper](https://arxiv.org/abs/2312.07104)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
> Based on Ccyest's personal experience shared on Xiaohongshu (XHS).
