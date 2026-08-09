---
title: "仅27B参数，微软开源Fara 1.5超越OpenAI Operator：完整电脑操作Agent技术解析"
titleEn: "Only 27B Params: Microsoft's Open-Source Fara 1.5 Beats OpenAI Operator — a Full Computer-Use Agent Breakdown"
description: "微软 Research AI Frontiers 团队发布 Fara 1.5，提供 4B、9B、27B 三种规模的电脑操作 Agent 模型，全部 MIT 开源。Fara1.5-27B 在 Online-Mind2Web 基准拿下 72.3% 成功率，超越 OpenAI Operator（58.3%）和 Gemini 2.5 Computer Use（57.3%）。模型基于 Qwen3.5 构建，通过 FaraGen1.5 数据管道训练，权重已开放于 HuggingFace。"
descriptionEn: "Microsoft Research AI Frontiers releases Fara 1.5 — a family of computer use agent models at 4B, 9B, and 27B scales, all MIT-licensed open source. Fara1.5-27B achieves 72.3% on Online-Mind2Web, outperforming OpenAI Operator (58.3%) and Gemini 2.5 Computer Use (57.3%). Built on Qwen3.5, trained via FaraGen1.5 data pipeline, weights available on HuggingFace."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-News"
tags: ["Fara", "微软", "电脑操作Agent", "Computer Use", "开源模型", "Qwen3.5", "AI Agent", "Mycelium"]
heroImage: "../../assets/images/fara15-microsoft-computer-use-agent-27b-beats-openai-operator-banner.jpg"
---

*by Mycelium Protocol*

---

微软 Research AI Frontiers 团队在 2026 年 7 月发布了一个开源的电脑操作 Agent 模型家族 **Fara 1.5**，提供 4B、9B、27B 三种参数规模，全部以 MIT 授权释出，权重托管于 HuggingFace。

其中 **Fara1.5-27B** 在 Online-Mind2Web 基准检测拿下 **72.3%** 的高成功率，超越 OpenAI Operator 的 58.3% 与 Google Gemini 2.5 Computer Use 的 57.3%。9B 版本也达到 63.4%，在同等规模中刷新了 SOTA。

---

## 它能做什么

Fara 1.5 是**原生电脑操作 Agent**（Computer Use Agent，CUA）。给它一个任务描述，它直接在浏览器截图上观察当前状态，然后输出鼠标点击、键盘输入、搜索等操作——不需要 accessibility tree，不需要额外的页面解析模型，直接对坐标预测。

可以处理的任务类型包括：

- 搜索信息并整理结果
- 填写表单、管理账号设置
- 订票（机票、电影、餐厅）
- 跨站比价购物
- 查找职位、房源信息

循环逻辑是 **observe → think → act**：截图输入 + 对话历史 → 推理当前任务状态 → 输出下一步操作。

---

## 跑分数据

| 模型 | 规模 | WebVoyager | Online-Mind2Web |
|------|------|------------|-----------------|
| OpenAI Operator | 闭源 | 87.0 | 58.3 |
| Gemini 2.5 Computer Use | 闭源 | — | 57.3 |
| GPT-5 SoM | 闭源 | 90.6 | 57.7 |
| **Fara1.5-4B** | 4B | 80.8 | 57.3 |
| **Fara1.5-9B** | 9B | 86.6 | 63.4 |
| **Fara1.5-27B** | 27B | **89.3** | **72.3** |

Fara1.5-9B 比上一代 Fara-7B 在 Online-Mind2Web 上提升了 **29.3 个百分点**。

---

## 技术核心：FaraGen1.5 数据管道

Fara 1.5 的核心不只是模型本身，而是支撑它的数据生成管道 **FaraGen1.5**，由三部分组成：

**环境（Environments）**

- 真实网站上的开放互联网任务
- 6 个合成 FaraEnv 环境（Mail、Calendar、Stream、ML、Stay、Scheduler）——这些是功能完整的 UI 克隆，用于模拟需要登录或会触发不可逆操作的场景，同时支持基于执行结果的精确验证

**求解器（Solvers）**

- 可接入多种模型，包括 GPT-5.4 等强 Frontier 模型
- 配备用户模拟器，支持多轮对话训练

**验证器（Verifiers）**

三层过滤：
1. 任务正确性（Universal Verifier LLM 裁判）
2. 效率（惩罚冗余操作）
3. 关键节点遵循（用户确认、缺失信息提示、不可逆操作暂停）

训练集最终约 200 万样本：~60% 真实网络轨迹、12.8% 合成环境、12.5% 表单填写、8.8% 基础定位、4.9% VQA、0.8% GUI 拖拽任务。

---

## 关键能力细节

**直接坐标预测**

Fara 1.5 不依赖 accessibility tree。它直接在截图像素上预测操作坐标，这意味着它能处理那些 DOM 结构混乱或根本没有 accessibility 支持的网页。

**多轮用户交互**

通过用户模拟器在多轮对话中训练，Fara 1.5 学会了：
- 主动询问缺失信息
- 标记模糊任务
- 在执行不可逆操作前暂停并请求用户确认

这解决了自动化 Agent 最容易出问题的场景——"你让它订机票，它直接付款了"。

**可审计性**

与 Magentic-UI 集成后，所有操作都有日志可追溯，并在关键节点弹出用户确认界面。

---

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/microsoft/fara.git
cd fara
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install

# 2. 从 Microsoft Foundry 部署 Fara1.5-9B，创建配置文件
cat > azure_foundry_config.json << 'EOF'
{
    "model": "Fara1.5-9B",
    "base_url": "https://your-endpoint.inference.ml.azure.com/",
    "api_key": "YOUR_API_KEY_HERE"
}
EOF

# 3. 运行任务
fara-cli --task "What's the weather in New York now?" \
         --endpoint_config azure_foundry_config.json
```

或者在 [Magentic-UI](https://github.com/microsoft/magentic-ui) 中以可视化方式使用，支持沙箱浏览器环境 + 操作日志界面。

---

## 两个配套基准

**WebTailBench**：609 个任务，覆盖 11 类真实网络任务，重点测试现有基准忽视的长尾场景（购物对比、跨站任务、多步组合）。数据集在 HuggingFace：`microsoft/WebTailBench`。

**CUAVerifierBench**：专门评估"给 Agent 打分的裁判"质量。包含 Fara Agent 轨迹 + 人工标注判断 + Universal Verifier 输出，用于开发和比较 Agent 评估方法。

---

## 为什么值得关注

Fara 1.5 有几个值得注意的点：

**27B 就能超越闭源大厂**。这不是微调一个聊天模型，而是专门训练的 CUA 模型，规模 27B，成本远低于调用 OpenAI Operator。

**方法论开放**。FaraGen1.5 管道（环境 + 求解器 + 验证器）的设计细节公开发表，任何团队都可以基于这个框架构建自己的垂直领域 Agent 训练数据。

**坐标直接预测 vs. accessibility tree**。这个选择意味着 Fara 1.5 能处理 accessibility tree 不完整或不可用的场景，覆盖范围更广。

仓库：[github.com/microsoft/fara](https://github.com/microsoft/fara) · HuggingFace：[microsoft/Mage-VL](https://aka.ms/fara1.5-hf) · 论文：[arxiv 2606.20785](https://arxiv.org/abs/2606.20785)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Microsoft Fara 1.5: A 27B Open-Source Agent That Outperforms OpenAI Operator

*by Mycelium Protocol*

Microsoft Research AI Frontiers released **Fara 1.5** in July 2026 — a family of native computer use agent (CUA) models at three scales: 4B, 9B, and 27B. All three are MIT-licensed and available on HuggingFace.

**Fara1.5-27B achieves 72.3% on Online-Mind2Web**, outperforming OpenAI Operator (58.3%) and Gemini 2.5 Computer Use (57.3%). The 9B version reaches 63.4% — a new state of the art for its size class, and a +29.3 point improvement over the previous Fara-7B.

### What It Does

Fara 1.5 is a native Computer Use Agent. Given a task description, it observes the current browser state through a screenshot, reasons about what to do next, and outputs mouse clicks, keyboard inputs, or web searches — **with no accessibility tree, no separate parsing model, direct coordinate prediction on the screenshot**.

Supported task types: information search and summarization, form filling, account management, booking (flights, restaurants, movie tickets), cross-retailer price comparison, job and real estate searches.

The loop: **observe (screenshot + conversation history) → think → act**.

### Performance

| Model | Size | WebVoyager | Online-Mind2Web |
|-------|------|------------|-----------------|
| OpenAI Operator | closed | 87.0 | 58.3 |
| Gemini 2.5 CU | closed | — | 57.3 |
| GPT-5 SoM | closed | 90.6 | 57.7 |
| **Fara1.5-4B** | 4B | 80.8 | 57.3 |
| **Fara1.5-9B** | 9B | 86.6 | 63.4 |
| **Fara1.5-27B** | 27B | **89.3** | **72.3** |

### FaraGen1.5: The Data Pipeline

The core innovation behind Fara 1.5 is **FaraGen1.5**, a scalable training data pipeline with three modular components:

**Environments** — open-internet tasks on live websites plus six synthetic FaraEnvs (Mail, Calendar, Stream, ML, Stay, Scheduler). These are functional UI clones that simulate authentication-gated or irreversible-action domains while enabling ground-truth execution-based verification.

**Solvers** — a solver harness powered by strong frontier models (including GPT-5.4) paired with a user simulator for multi-turn rollouts.

**Verifiers** — three complementary filters: task correctness (Universal Verifier LLM judge), efficiency (penalizing redundant actions), and critical-point adherence (flagging missing info, ambiguous tasks, unapproved irreversible actions).

Training mix: ~2M samples — 60% web trajectories, 12.8% synthetic environments, 12.5% form filling, 8.8% grounding, 4.9% VQA, 0.8% GUI drag tasks.

### Key Technical Choices

**Direct coordinate prediction on screenshots.** No accessibility tree dependency. This means Fara 1.5 handles pages with incomplete or absent accessibility support — a significant portion of the real web.

**Multi-turn user interaction via user simulator.** Trained to ask for missing information, flag ambiguous tasks, and pause before irreversible actions. This is the critical safety behavior that distinguishes a deployable agent from a dangerous one.

**Auditable action logging via Magentic-UI.** A sandboxed browser environment with user confirmation prompts at critical points and full action logs. For users who want automation without blind trust.

### Quick Start

```bash
git clone https://github.com/microsoft/fara.git && cd fara
python3 -m venv .venv && source .venv/bin/activate
pip install -e . && playwright install
# Deploy Fara1.5-9B from Microsoft Foundry, create config, then:
fara-cli --task "Find flights from SF to NYC next Friday" \
         --endpoint_config azure_foundry_config.json
```

Or use Magentic-UI for a visual interface with action logging.

### Two Companion Benchmarks

**WebTailBench** (609 tasks, 11 real-world task types): focuses on long-tail scenarios underrepresented in existing benchmarks — shopping lists, comparison shopping, compositional cross-site tasks. Dataset: `microsoft/WebTailBench` on HuggingFace.

**CUAVerifierBench**: evaluates the *judges* that score CUA agents, not the agents themselves. Pairs Fara trajectories with human verdicts and Universal Verifier outputs to enable systematic development of better evaluation methods.

### Why This Matters

A 27B open-source model outperforming closed proprietary systems on a standardized web-automation benchmark is a meaningful signal. The FaraGen1.5 pipeline design — environments + solvers + verifiers — is fully described in the paper and reproducible: teams can adapt it for vertical domains without starting from scratch.

The choice to avoid accessibility trees broadens applicability. The built-in user confirmation behaviors address the safety concerns that make autonomous agents risky in practice.

Repository: [github.com/microsoft/fara](https://github.com/microsoft/fara) · HuggingFace: [aka.ms/fara1.5-hf](https://aka.ms/fara1.5-hf) · Paper: [arxiv 2606.20785](https://arxiv.org/abs/2606.20785)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
