---
title: "iDoris 立项思考：一个普通研究者如何构建可持续进化的本地 AI 模型"
titleEn: "iDoris Project Launch: How an Independent Researcher Builds a Continuously Evolving Local AI"
description: "iDoris 是面向「个人→社区→城市」三层场景的本地 AI 模型项目。本文从约束推导出「必须分层+必须联邦」的结论；选定 Qwen3.5/3.6 同基座+分层 LoRA 架构；以 DP-SGD+算法可审计实现「权重可上传+原始数据不出本机」。我们不回避不确定性。"
descriptionEn: "iDoris is a 3-tier local AI project (Personal → Community → City). This article documents the launch reasoning: deriving 'must be layered + must be federated' from constraints; selecting Qwen3.5/3.6 same-backbone + stacked LoRA architecture; using DP-SGD + algorithm auditability for 'weights uploadable + raw data stays local'. We do not hide uncertainty."
pubDate: "2026-04-27"
updatedDate: "2026-04-27"
category: "Progress-Report"
tags: ["iDoris", "本地AI", "Local AI", "Federated LoRA", "Mycelium", "Aura AI", "Qwen3", "Progress-Report"]
heroImage: "../../assets/banner-mycelial-network.jpg"
---

> **立项日期**：2026-04-27 · **组织**：Aura AI / Mycelium Protocol
> **完整方案**：[research/iDoris/iDoris-master-plan.md](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
> **代码仓库**：[github.com/AuraAIHQ/iDoris](https://github.com/AuraAIHQ/iDoris)（早期阶段）
> **本文性质**：立项推导，非营销稿。每条论断都附可验证的来源。

## 摘要

iDoris 是一个面向「个人 → 社区 → 城市」三层场景的本地 AI 模型项目。命名 i = 中文"爱"，Doris = 创始人爱人英文名。

本文系统记录立项时的推导过程：

1. 从三类约束（算力、隐私、数据量）出发，推出「必须分层 + 必须联邦」的结论；
2. 选定 Qwen3.5/3.6 同基座 + 分层 LoRA + 嵌套 RAG + DPO 的混合架构；
3. 以 DP-SGD（差分隐私）+ 算法可审计性，实现「LoRA 权重可上传，原始数据绝对不出本机」；
4. 设计 4 阶段渐进式 MVP 路径，第一阶段在 64GB Mac Studio 上跑通。

本文不回避不确定性：**单用户数据是否够、联邦聚合质量是否够好、灾难性遗忘如何处理**，都将在 Phase 1 的 1-3 个月里以可观测的方式被验证。

---

## §1 起点：一个真实但被忽略的问题

我用 Claude / ChatGPT 已经超过一年。它们工程上很强、推理上很强、写作上很强。但有一件事它们做不到：**在我用了 12 个月之后，它们仍然不懂我**。

每次开新对话，我得重新介绍自己写作风格、解释项目背景、贴出常用术语表。云端大模型不会因为我的使用而进化为「我的版本」——我贡献的所有交互被用来训练 GPT-5 / Claude 5，但训练的产物属于平台，不属于我。

更深一层的问题是：**单个用户的数据量根本不足以训练一个大模型**。我的 Obsidian 笔记 + 博客 + 聊天记录加起来 1-10 GB，这个量级训不出有用的"我"——除非用某种方式把多个用户的"少量数据"以隐私安全的方式聚合起来。

**这就引出了立项的核心命题**：

> 能不能构建一个本地 AI，它持续学我，但又不需要我交出原始数据？
> 能不能让多个用户的少量数据在保护隐私的前提下，汇聚成有用的集体知识？
> 能不能从「单人 → 社区 → 城市」一条线生长出来，而不是三个独立项目？

这就是 iDoris 立项要回答的问题。

## §2 约束：先把限制条件摆出来

不谈约束的方案是空中楼阁。iDoris 立项时承认三类硬约束：

| 约束类型 | 具体限制 | 推论 |
|---------|---------|------|
| **算力** | Mac Studio 64GB（M4 Ultra 192GB 是天花板）；普通研究者预算 | 不能跑全量微调；只能 LoRA 类参数高效方法 |
| **隐私** | 原始数据绝对不离开用户设备 | 不能 centralized 训练；只能联邦学习 |
| **数据量** | 单用户 1-10GB 笔记/聊天记录 | 单点训练学不到稳定特征；需多用户聚合 |

**从这三条约束推出的强制结论**：

- 必须用 LoRA 等参数高效方法（PEFT），而非全量微调
- 必须设计一种"权重可上传 + 数据不出本机"的机制
- 必须分层架构（个人层 + 社区层 + 城市层），让数据按层级聚合而非全部送顶

这是一道**带约束的最优化问题**，不是"理想中应该有什么"，而是"在已知限制下，唯一合理的路径是什么"。

## §3 技术选型推导：为什么是 LoRA + RAG + DPO

### 3.1 为什么不能全量微调

对 Qwen3.5-9B 做全量微调（FFT），所需显存约为：

```
显存 ≈ 模型参数 × 4 (FP32 weights) + 梯度 × 4 + Adam 状态 × 8 + 激活值
     ≈ 9B × 16 (字节) + 激活
     ≈ ~144 GB（不含激活）
```

64GB Mac Studio 完全不够。云端 8×A100 训一次约 \$300-800，但**这违反"原始数据不出本机"原则**。结论：FFT 在我们的约束下不可行。

### 3.2 为什么 LoRA / QLoRA 是必然选择

LoRA（[Hu et al., 2021, arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）的核心思想是：在微调时不改动原始权重 W，而是学习一个低秩分解 ΔW = BA（B、A 是可训练的小矩阵）。可训练参数从 9B 降到约 200M（r=32 时），显存需求降到 ~28GB。

QLoRA（[Dettmers et al., 2023, NeurIPS](https://arxiv.org/abs/2305.14314)）进一步把基座量化到 4-bit，把显存压到 ~14GB。**Mac Studio 64GB 跑得动训得动 9B QLoRA**，这是工程红利。

### 3.3 为什么还需要 RAG

LoRA 把"长期偏好"固化到权重里，但有两类数据 LoRA 不擅长：

- **新事实**（今天收到的邮件、本周的会议纪要）：训进 LoRA 太慢且容易过拟合
- **长尾事实**（具体某个项目的提交历史）：稀疏数据训不进 LoRA

这部分用 **RAG**（Retrieval-Augmented Generation）解决：把这些数据存进向量库，推理时检索相关片段拼到 prompt 里。

我们计划使用 [LightRAG](https://github.com/HKUDS/LightRAG)（基于知识图谱增强的 RAG，2024-10 论文，对长期记忆比传统向量 RAG 更强）。

### 3.4 为什么还要 DPO

LoRA 学到「我写什么」，但 AI 还需要学「我喜欢什么」。这是对齐问题。

经典方法是 RLHF（人类反馈强化学习），但需要训一个奖励模型，工程复杂。**DPO**（[Rafailov et al., NeurIPS 2023](https://arxiv.org/abs/2305.18290)）证明了：直接用偏好对（chosen vs rejected）做对比损失，等价于 RLHF，且不需要奖励模型。在 Sin90 客户端聊天界面加 👍 👎 按钮即可累积 DPO 训练数据。

### 3.5 四者协同：心智模型

| 知识介质 | 更新频率 | 容量 | 存什么 | 类比 |
|---------|---------|------|--------|------|
| **基座权重** | 几乎不变 | 数十亿参数 | 世界知识、语言能力、推理能力 | 大学毕业的通用知识 |
| **LoRA 权重** | 周/月级 | 数百万参数 | 风格、长期偏好、领域知识 | 工作 5 年的"懂这个行业" |
| **RAG 向量库** | 秒级实时 | 任意 | 当下笔记、近期事件 | 桌面贴的便签 |
| **DPO 偏好集** | 持续累积 | 数千-数万对 | "我喜欢/不喜欢这种回答" | 老板教你说话不被嫌弃 |

四者各管一段，互不替代。

## §4 基座模型选型：为什么是 Qwen3.5/3.6

### 4.1 候选评估（2026-04 截至本文起草日）

| 基座 | License | 中文 | Size 矩阵 | MoE 选项 | Apple Silicon |
|------|---------|------|----------|----------|--------------|
| **Qwen3.5/3.6** | Apache 2.0 | 强 | 0.8B-122B 全覆盖 | A3B / A10B | 一线支持 |
| Llama 3.3 | Community（限制） | 中 | 8B/70B/405B | 无 | 支持 |
| DeepSeek V4 | MIT | 强 | 仅大模型 | A13B | V4 Flash 太大 |
| Gemma 4 | Gemma TOS | 弱 | 26B-A4B | A4B | 支持 |

[Qwen3.6 GitHub](https://github.com/QwenLM/Qwen3.6) 是当前最新（2026-04-22 发布 27B），Qwen3.5 全家族在 2026-02 ~ 03 完整发布（参考 [Nathan Lambert 评论](https://www.interconnects.ai/p/qwen-3-the-new-open-standard)）。

DeepSeek V4 在 2026-04-24 发布（[TechCrunch 报道](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/)），V4 Flash 是 284B 总参 / 13B 激活的 MoE。**对 64GB Mac Studio MVP 太大**，作为 City 层备选。

### 4.2 关键决策：MoE 是 Community 层的工程红利

Qwen3.6-35B-A3B = 总参数 35B，每个 token 只激活 3B。这意味着：

- 模型权重在 64GB Mac Studio 上**装得下**（量化后约 18-22GB）
- 推理速度接近 3B 模型，但能力接近密集 32B 模型
- 这是 **iDoris-Community 层的最优解**

如果选传统密集模型，要在 64GB 上跑 32B 必须激进量化（Q3 以下），质量损失大。MoE 让"中小社区也能跑准旗舰模型"成为可能（参考 [Best LLM for Mac 2026](https://willitrunai.com/blog/best-llm-for-mac-apple-silicon-2026)）。

### 4.3 iDoris 四个层级选型

| 层级 | 推荐基座 | 总参/激活参 | 硬件目标 |
|------|---------|------------|---------|
| iDoris-Mobile | Qwen3.5-2B / DeepSeek-R1-Distill-Qwen-1.5B | 2B / 1.5B | 旗舰手机 |
| iDoris-PC | Qwen3.5-9B | 9B | Mac Studio / 4090 |
| iDoris-Community | **Qwen3.6-35B-A3B** | 35B / 3B 激活 | Mac Studio Ultra / 双 4090 |
| iDoris-City | Qwen3.5-122B-A10B | 122B / 10B 激活 | 多卡服务器 |

**全家族共用 Qwen 系列基座**，这是后面"分层 LoRA 跨层级兼容"的前提。

## §5 三层架构如何"血脉相连"

### 5.1 同基座 + 分层 LoRA

LoRA 的可叠加性来自于其线性结构。在推理时：

```
W_final = W_base + Σ_i α_i × ΔW_i
        = W_base + α_personal × ΔW_personal
                 + α_community × ΔW_community
                 + α_city × ΔW_city
```

这意味着：

- 同一个用户可以**只用本地 Personal LoRA**（最严隐私模式）
- 也可以**叠加社区共识 Community LoRA**（享用社区智慧）
- 政务咨询场景可以**叠加 City LoRA**（接入公共服务知识）

α 系数由用户在 Sin90 GUI 上滑动调节，相当于"我多大程度信任社区/城市的知识"。

### 5.2 LoRA 跨 size 的可移植性

学术界已证明（参考 [SLoRA, NeurIPS 2024](https://arxiv.org/abs/2308.06522)）：在同一模型家族内，小模型上训的 LoRA 可以一定程度迁移到大模型上。这意味着 iDoris-Mobile（2B）训出的个人偏好 LoRA，可以"长大"到 PC（9B）上继续使用，不需要重新训练。

### 5.3 与前台应用的关系

iDoris 是**模型层**；Sin90、Cos72、CityOS 是**应用层**。类比：iOS 之于 Apple Foundation Models。

| 层 | 内容 | 命名 |
|----|------|------|
| 应用层 | 用户实际使用的产品 / GUI / 工作流 | **Sin90 / Cos72 / CityOS** |
| 模型层 | 核心 AI 模型 + 训练流水线 | **iDoris-Personal / Community / City** |

（早期对话里出现过 ~~CN90~~、~~Cosine72~~、~~CTOS~~，是语音识别错误，正确为 Sin90 / Cos72 / CityOS。）

## §6 数据流与隐私架构

这一节是 iDoris 的核心创新所在。

### 6.1 立场：权重不是隐私数据原文

> 权重不是直接隐私数据，是基于"隐私数据 + 算法"的计算结果。在算法开源 + AI 自动审计无后门 + 用户明确授权三个前提下，LoRA 权重 delta 可以上传给上游训练。
> ——立项时的核心立场

这一立场对应学术界的 **DP-FedAvg + Algorithm Auditing** 路线。它使得：

- 个人层 → 社区层的 LoRA 上传 ✅ 可行
- 社区层 → 城市层的 LoRA 上传 ✅ 可行
- 同时**原始数据绝对不离开本机** ✅ 不妥协

### 6.2 三道闸门 + 数学保证

```
个人原始数据 (本地)
    ↓ 闸门 1: PII 自动脱敏 (Microsoft Presidio + 中文 NER)
脱敏数据 (本地)
    ↓ 闸门 2: 用户主题级授权 (工作/生活/健康/财务分类授权)
LoRA 训练数据 (本地)
    ↓ 本地训练 (MLX-LM / Unsloth)
个人 LoRA 权重 (本地)
    ↓ 闸门 3: DP-SGD 注入梯度噪声 (ε ≤ 8, δ ≤ 1e-5)
DP-LoRA 权重 delta (可上传)
    ↓ 闸门 4: 上传时二次审计 + 异常贡献剔除 (Krum / Median)
社区 LoRA 联邦聚合 (FedAvg / SLoRA)
```

**核心数学工具是 DP-SGD**（[Abadi et al., CCS 2016](https://arxiv.org/abs/1607.00133)）：在每步梯度上注入受控的高斯噪声，使得"通过最终模型反推某条具体训练样本"的概率被严格上界。

(ε, δ) 是隐私预算：ε 越小越严格，δ 越小越严格。iDoris 的目标是 ε ≤ 8, δ ≤ 1e-5，这是工业级隐私强度。

### 6.3 联邦 LoRA 算法选择

我们计划并行试验三种算法：

- **FedAvg-LoRA**（[McMahan et al., AISTATS 2017](https://arxiv.org/abs/1602.05629) 的 LoRA 变体）
- **SLoRA**（[NeurIPS 2024](https://arxiv.org/abs/2308.06522)，专为联邦 PEFT 设计）
- **FedIT**（[ICLR 2024](https://arxiv.org/abs/2305.05644)，建立联邦 LLM 微调基准）

工程框架使用 [Flower](https://flower.ai/) + [OpenFedLLM](https://github.com/rui-ye/OpenFedLLM)。

## §7 渐进路径：一条线，不是三条线

### 7.1 路径

```
Phase 1 (M1-M3, 2026 Q2-Q3): iDoris-Personal-PC MVP
    └ 创始人作为唯一用户，跑通 Qwen3.5-9B + LoRA + RAG + DPO
    └ 输出：能学创始人写作风格的 Mac Studio 本地 AI

Phase 2 (M4-M5, 2026 Q4): iDoris-Personal-Mobile 端侧蒸馏
    └ 把 9B Personal LoRA 蒸馏到 2B 移动端
    └ 输出：iOS / Android App，离线可用

Phase 3 (M6-M9, 2027 Q1-Q2): iDoris-Community 试点
    └ 选第一个真实社区（Mycelium DAO 内部 / 某开源社区）
    └ 跑通 Federated LoRA 聚合
    └ 输出：社区共有的 AI 角色

Phase 4 (M10-M18, 2027 Q3+): iDoris-City 概念验证
    └ ≥5 个真实 Community 节点 → 蒸馏 City 模型
    └ 与某城市 / 区政府试点
```

### 7.2 为什么是 bottom-up 而非 top-down 蒸馏

DeepSeek-R1 的成功路径是 **top-down 蒸馏**：先训大模型（R1 671B），再蒸馏出小模型（1.5B / 8B / 70B）。这是商业模式：大厂集中算力训出顶级模型，分发给用户。

iDoris 走的是相反路径：**bottom-up 联邦**——个人先训自己的，再聚合到社区，再聚合到城市。原因不是技术上更优，而是：

> **数据所有权属于用户**。任何"上层模型"都必须从用户自愿贡献的数据中生长出来，不能从上向下分发。

这是工程选择背后的**所有权立场**，是 Mycelium Protocol "数字主权"理念的直接技术体现（参考 [Mycelium MISSION](https://github.com/HyperCapitalHQ/mycelium-protocol)）。

## §8 不是表演：真实的不确定性

这一节本来就该写，但特别值得单独成章——因为 AI 圈的话术污染已经让"愿景文章"等于"过度承诺"。我列出立项时已经知道但还没解决的风险：

### 风险 1：单用户数据可能不够

学术界对"训出有用 LoRA 所需的最少样本量"没有定论。常见经验值是几千到几万条。我估算自己的笔记 + 博客 + 聊天加起来约 5,000-15,000 条有效样本，**可能勉强够，可能不够**。

**缓解**：如果 Phase 1 学不到稳定风格，备选方案是用合成数据扩充（让大模型生成"以你的风格写"样本，再人工筛选）。

### 风险 2：联邦聚合质量比 centralized 低 5-15%

这是学术界已观测到的事实（参考 OpenFedLLM 论文实验）。**联邦学习的隐私收益是有代价的**。

**缓解**：每 N 轮联邦后，由社区核心维护者用社区共享公开数据做一次 centralized 微调，作为"锚点"。这是工程妥协，不是完美解。

### 风险 3：灾难性遗忘

LoRA 在持续学习中会遗忘早期能力，这叫 catastrophic forgetting。处理方法（MoE-LoRA / AdapterFusion）目前都不完美。

**缓解**：iDoris 的分层 LoRA 在某种程度上隔离了风险——基座永远不变，最坏情况是某层 LoRA 重训。

### 风险 4：MLX-LM 工程化成熟度

Apple Silicon 的 MLX 生态比 PyTorch / CUDA 慢一拍。LoRA 训练 / DPO / 联邦聚合在 MLX 上**可能有 bug 或缺接口**。

**缓解**：备选方案是租云 GPU（Lambda / Modal Labs spot）做训练，把成果同步回 Mac 做推理。

### 风险 5：根本验证标准

我打算用 1-3 个月时间验证这件事是否成立。**判断指标不是技术指标**（Perplexity / BLEU），而是主观的"懂我的程度"——对比 Claude / ChatGPT，看在写邮件、整理思路、处理私密笔记这些场景下，是否真的更懂我。

如果 3 个月后我自己觉得"还不如继续用 Claude"，iDoris-Personal 这一层就需要重新审视。**这是诚实的开放性命题，不是预设结论的论证**。

## §9 模型演进：当更先进的基座出现时，已有工作如何继承？

一个常见质疑：你现在投入做 Qwen3.5/3.6 的 LoRA / RAG / DPO，半年后 DeepSeek V5 / Llama 5 / Qwen 4 出来了，是不是白做？

### 9.1 答案：四个组件中只有一个绑定基座

iDoris 的训练栈拆为四层，**只有 LoRA 权重本身和基座绑定**。其他三层与基座无关：

| 组件 | 与基座耦合度 | 迁移成本 |
|------|------------|---------|
| RAG 向量库 | 完全无关 | **0%**（直接复用） |
| DPO 偏好数据集 | 完全无关 | **0%**（直接复用） |
| LoRA 训练数据集 | 完全无关 | **0-15%**（看 tokenizer 是否兼容） |
| LoRA 权重本身 | 完全绑定 | **100%**（必须重训） |

这是有意为之的工程选择：**把价值留在数据和方法里，不留在具体权重里**。

### 9.2 三种迁移场景的成本估算

| 场景 | 例子 | 工作量 | 说明 |
|------|------|-------|------|
| **A. 同家族升级** | Qwen3.6 → Qwen4 | ~5-10% | tokenizer 兼容，架构相似，一晚重训 LoRA + DPO |
| **B. 跨家族同 size** | Qwen3.5-9B → DeepSeek-Lite-9B（假设有此 size） | ~20-30% | tokenizer 不同需重格式化数据；架构差异需调 LoRA 配置 |
| **C. 跨架构跨 size** | Qwen3.5-9B → DeepSeek V4 Flash 284B-A13B | ~40-50% | size 跨度太大需重设 LoRA 秩；MoE 架构需不同 PEFT 策略 |

实际工程中场景 A 和 B 占绝大多数，**20-30% 的迁移成本是合理估算**。

### 9.3 何时触发迁移：两个前提条件

迁移决策不应该追新潮，而应该满足下面之一：

1. **新模型有合适 size 矩阵**：例如 DeepSeek 出 Lite-2B/9B 系列，能覆盖 Mobile/PC 层。否则 DeepSeek V4 Flash（284B/13B-A）对个人 / 社区层是空中楼阁。
2. **硬件成本下降使更大 size 可达**：例如 M5 Ultra 出来后 256GB 统一内存平民化，原本 City 层的 122B 模型可以下沉到 Community 层运行。

任何一项不满足，迁移没必要。

### 9.4 这是工程合理性，不是自我安慰

如果我们采用**单一基座 + 全量微调**，迁移成本接近 100%——因为模型本身才是产物。

我们选择**模块化 PEFT + 基座无关组件**架构，正是 2023-2025 年开源社区的主流共识：参考 HuggingFace [PEFT 库](https://github.com/huggingface/peft) 的设计哲学，参考 [LangChain](https://github.com/langchain-ai/langchain) / [LlamaIndex](https://github.com/run-llama/llama_index) 把"知识"与"模型"解耦的设计动机。

**结论**：iDoris 的训练投入不会因为基座迭代而归零，前提是我们一开始就选了正确的架构——这正是立项时的核心决策。

---

## §10 为什么是现在 + 加入方式

### 10.1 时点合理性

三件事在 2026 年 4 月前后凑齐了：

1. **模型生态成熟**：Qwen3.5/3.6（2026-02 ~ 04）、DeepSeek V4（2026-04-24）、Gemma 4 等齐发，开源 LLM 已经接近闭源旗舰
2. **硬件可达**：M4 Ultra Mac Studio 提供 64-192GB 统一内存，让"普通研究者跑大模型"从神话变成日常
3. **组织框架就绪**：[Mycelium Protocol](https://launch.mushroom.cv) 提供了集体行动的协议层 + 资金路径（冷启动模型，非 VC）

任何一项再早一年都不成立。这不是必要条件，是充分条件之一。

### 10.2 加入方式（无许可起步）

iDoris 是 **Mycelium Protocol** 旗下 [Aura AI](https://github.com/AuraAIHQ) 子组织的研究项目。所有代码 Apache 2.0 开源。

如果你也在思考：
- 「ChatGPT/Claude 用一年了为什么还不懂我？」
- 「个人 / 小社区如何拥有自己的 AI 而不被平台收割？」
- 「数据主权和 AI 能力可以同时拥有吗？」

可以通过以下方式参与：

- **代码贡献**：[github.com/AuraAIHQ/iDoris](https://github.com/AuraAIHQ/iDoris)（早期阶段，欢迎讨论 issue）
- **生态加入**：无许可加入 [Mycelium Protocol](https://launch.mushroom.cv)，免费使用模型和训练流程
- **研究讨论**：[完整方案文档](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md) 在 GitHub 公开

### 10.3 授权机制：免费，但需要轻量注册（防滥用 + 互利反馈）

License 分两档，**两档都免费**，区别只是是否需要授权：

| 规模 | License | 是否需要授权 |
|------|---------|------------|
| ≤50 人小社区 / 个人 | 永久免费 | **不需要授权**，直接用 |
| >50 人非商业 / 中小商业组织 | 免费使用 | **需要"官方授权"**（轻量注册，不收费） |

授权机制的核心目的（**不是收费**）：

- **使用方注册**：让我们知道哪些社区 / 组织在使用 iDoris，建立公开用户清单（透明）
- **反馈互通**：定期分享使用心得、踩坑记录、改进建议——这是开源社区的"血脉"
- **品牌权益保护**：防止商业冒用 / 闭源 fork / 假冒 Mycelium Protocol 之名
- **保护双生组织**：参考 Linux + RedHat 模式，保护开源组织（MushroomDAO）和商业实体（[HyperCapital](https://github.com/HyperCapitalHQ)）的合作关系

**轻量授权流程**：
1. 通过 [launch.mushroom.cv](https://launch.mushroom.cv) 提交简单注册表单（社区名、规模、联系方式、用途）
2. MushroomDAO 委员会审核（一般几天回复）
3. 通过后即可使用，每半年更新一次反馈

详细 License 文本：见 [Mycelium Protocol GitHub](https://github.com/HyperCapitalHQ/mycelium-protocol)。

---

## 参考资料

### 核心论文

- LoRA: Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- QLoRA: Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs", NeurIPS 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- DPO: Rafailov et al., "Direct Preference Optimization", NeurIPS 2023, [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)
- DP-SGD: Abadi et al., "Deep Learning with Differential Privacy", CCS 2016, [arXiv:1607.00133](https://arxiv.org/abs/1607.00133)
- FedAvg: McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data", AISTATS 2017, [arXiv:1602.05629](https://arxiv.org/abs/1602.05629)
- SLoRA: "SLoRA: Federated Parameter Efficient Fine-Tuning", NeurIPS 2024, [arXiv:2308.06522](https://arxiv.org/abs/2308.06522)
- FedIT: "Towards Building the Federated GPT", ICLR 2024, [arXiv:2305.05644](https://arxiv.org/abs/2305.05644)

### 模型与生态

- [Qwen3.6 GitHub](https://github.com/QwenLM/Qwen3.6) · [Qwen3 官方博客](https://qwenlm.github.io/blog/qwen3/) · [Nathan Lambert: Qwen 3 Open Standard](https://www.interconnects.ai/p/qwen-3-the-new-open-standard)
- [DeepSeek V4 TechCrunch](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/) · [Simon Willison on V4](https://simonwillison.net/2026/Apr/24/deepseek-v4/)
- [Best LLM for Mac 2026](https://willitrunai.com/blog/best-llm-for-mac-apple-silicon-2026) · [MLX-LM 2026 Guide](https://markaicode.com/run-fine-tune-llms-mac-mlx-lm/)
- [Unsloth](https://github.com/unslothai/unsloth) · [Flower](https://flower.ai/) · [OpenFedLLM](https://github.com/rui-ye/OpenFedLLM) · [LightRAG](https://github.com/HKUDS/LightRAG)
- [Microsoft Presidio (PII 脱敏)](https://github.com/microsoft/presidio) · [Opacus (DP-SGD)](https://opacus.ai/)

### Mycelium Protocol 内部

- [iDoris 完整方案 (master plan)](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
- [Mycelium Protocol](https://github.com/HyperCapitalHQ/mycelium-protocol) · [MushroomDAO](https://github.com/MushroomDAO)
- [Cold Launch (launch.mushroom.cv)](https://launch.mushroom.cv)
- [Sin90 (Personal OS)](https://github.com/MushroomDAO/Sin90) · [Cos72 (Community OS)](https://github.com/AAStarCommunity/Cos72)
- [BroodBrain (协议神经系统)](https://github.com/AAStarCommunity/Brood)

<!--EN-->

> **Launch Date**: 2026-04-27 · **Org**: Aura AI / Mycelium Protocol
> **Full Plan**: [research/iDoris/iDoris-master-plan.md](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
> **Code Repo**: [github.com/AuraAIHQ/iDoris](https://github.com/AuraAIHQ/iDoris) (early stage)
> **Article Type**: Launch reasoning, not marketing. Every assertion has a verifiable source.

## Abstract

iDoris is a 3-tier local AI model project covering Personal → Community → City. The name: i = Chinese "love" (爱), Doris = the founder's wife's English name.

This article documents the launch reasoning:

1. From three constraints (compute, privacy, data scale), we derive the conclusion "must be layered + must be federated";
2. We select the architecture: Qwen3.5/3.6 same backbone + stacked LoRA + nested RAG + DPO;
3. With DP-SGD (differential privacy) + algorithm auditability, we achieve "LoRA weights uploadable, raw data never leaves device";
4. We design a 4-phase progressive MVP path, with Phase 1 running on a 64GB Mac Studio.

We do not hide uncertainty: **whether single-user data is sufficient, whether federated aggregation quality is acceptable, how to handle catastrophic forgetting** — all will be empirically verified during the 1-3 month Phase 1.

---

## §1 The Starting Point: A Real but Overlooked Problem

I have used Claude / ChatGPT for over a year. They are strong at engineering, reasoning, and writing. But they cannot do one thing: **after 12 months of usage, they still don't understand me**.

Every new conversation, I have to re-introduce my writing style, explain project background, paste my term glossary. Cloud LLMs do not evolve into "my version" through my usage — all my interactions are used to train GPT-5 / Claude 5, but the resulting model belongs to the platform, not me.

A deeper problem: **a single user's data volume is far from enough to train a large model**. My Obsidian notes + blog + chat history total 1-10 GB — not enough to learn a useful "me" — unless we can aggregate "small data" from many users in a privacy-safe way.

**This is iDoris's core question**:

> Can we build a local AI that continuously learns me, without me handing over raw data?
> Can multiple users' small datasets be aggregated into useful collective knowledge while preserving privacy?
> Can we grow from "Personal → Community → City" along one continuous line, instead of three separate projects?

## §2 Constraints: State the Limits First

Plans that don't address constraints are castles in the air. iDoris launches by acknowledging three hard constraints:

| Type | Limit | Implication |
|------|-------|-------------|
| **Compute** | Mac Studio 64GB (M4 Ultra 192GB ceiling); independent researcher budget | No full fine-tuning; only PEFT methods like LoRA |
| **Privacy** | Raw data must never leave user device | No centralized training; only federated learning |
| **Data scale** | Single user 1-10GB notes/chat | Single-point training fails; need multi-user aggregation |

**Forced conclusions**:
- Must use LoRA-class PEFT, not full fine-tuning
- Must design a "weights uploadable + data stays local" mechanism
- Must layer the architecture (Personal + Community + City) so data aggregates by tier, not all sent to top

This is a **constrained optimization problem**, not "what would be ideal", but "given known limits, what is the only viable path".

## §3 Selection: Why LoRA + RAG + DPO

### 3.1 Why Not Full Fine-Tuning

For Qwen3.5-9B FFT, VRAM ≈ params × 4 (FP32) + grad × 4 + Adam × 8 + activations ≈ ~144GB. 64GB Mac Studio is far from enough. Cloud 8×A100 costs \$300-800/run, but **violates "raw data never leaves" principle**. FFT is infeasible under our constraints.

### 3.2 Why LoRA / QLoRA Are Inevitable

LoRA ([Hu et al., 2021, arXiv:2106.09685](https://arxiv.org/abs/2106.09685)) keeps original weights W frozen and learns a low-rank decomposition ΔW = BA. Trainable params drop from 9B to ~200M (r=32), VRAM to ~28GB.

QLoRA ([Dettmers et al., NeurIPS 2023](https://arxiv.org/abs/2305.14314)) further quantizes the base to 4-bit, dropping VRAM to ~14GB. **Mac Studio 64GB can train 9B QLoRA comfortably** — an engineering windfall.

### 3.3 Why RAG Too

LoRA freezes "long-term preferences" into weights, but two data types are LoRA-unfriendly:
- **Fresh facts** (today's email, this week's meeting notes): too slow / overfitting risk
- **Long-tail facts** (specific project commit history): sparse data trains poorly

These go into **RAG** (Retrieval-Augmented Generation): vector DB + retrieval at inference. We plan to use [LightRAG](https://github.com/HKUDS/LightRAG) (knowledge-graph-augmented RAG, 2024-10 paper, stronger than vanilla vector RAG for long-term memory).

### 3.4 Why DPO

LoRA learns "what I write", but the AI also needs to learn "what I prefer" — the alignment problem.

Classic RLHF requires training a reward model (engineering complexity). **DPO** ([Rafailov et al., NeurIPS 2023](https://arxiv.org/abs/2305.18290)) proves: direct contrastive loss on preference pairs (chosen vs rejected) is equivalent to RLHF, no reward model needed. Just add 👍 👎 buttons in the Sin90 chat UI to accumulate DPO data.

### 3.5 Mental Model

| Medium | Update Frequency | Capacity | Stores | Analogy |
|--------|-----------------|----------|--------|---------|
| **Base weights** | Almost never | Billions of params | World knowledge, language, reasoning | College graduation knowledge |
| **LoRA weights** | Weekly/monthly | Millions of params | Style, long-term preference, domain | "I get this industry" after 5 years |
| **RAG vector DB** | Real-time | Arbitrary | Current notes, recent events | Sticky notes on desk |
| **DPO preference set** | Continuous | Thousands-tens of thousands of pairs | "I prefer this kind of answer" | Boss teaching you how to talk |

Each owns a slice. None replaces another.

## §4 Backbone Selection: Why Qwen3.5/3.6

### 4.1 Candidate Evaluation (as of 2026-04)

| Backbone | License | Chinese | Size Matrix | MoE | Apple Silicon |
|----------|---------|---------|-------------|-----|---------------|
| **Qwen3.5/3.6** | Apache 2.0 | Strong | 0.8B-122B full | A3B / A10B | First-class |
| Llama 3.3 | Community (restricted) | Medium | 8B/70B/405B | None | Yes |
| DeepSeek V4 | MIT | Strong | Large only | A13B | V4 Flash too big |
| Gemma 4 | Gemma TOS | Weak | 26B-A4B | A4B | Yes |

[Qwen3.6 GitHub](https://github.com/QwenLM/Qwen3.6) is current latest (27B released 2026-04-22). Qwen3.5 full family released 2026-02 to 03 (see [Nathan Lambert review](https://www.interconnects.ai/p/qwen-3-the-new-open-standard)).

DeepSeek V4 was released 2026-04-24 ([TechCrunch](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/)). V4 Flash is 284B total / 13B active MoE. **Too large for 64GB Mac Studio MVP**, kept as City-tier alternative.

### 4.2 Key Decision: MoE Is the Engineering Windfall for Community Tier

Qwen3.6-35B-A3B = 35B total params, only 3B activated per token. This means:

- The model fits in 64GB Mac Studio (quantized: ~18-22GB)
- Inference speed ~3B model, capability ~dense 32B
- **Optimal for iDoris-Community**

A traditional dense 32B on 64GB requires aggressive quantization (Q3 or below) with major quality loss. MoE makes "small communities can run near-flagship models" reality (see [Best LLM for Mac 2026](https://willitrunai.com/blog/best-llm-for-mac-apple-silicon-2026)).

### 4.3 Four-Tier Selection

| Tier | Recommended Backbone | Total/Active Params | Hardware Target |
|------|---------------------|---------------------|-----------------|
| iDoris-Mobile | Qwen3.5-2B / DeepSeek-R1-Distill-Qwen-1.5B | 2B / 1.5B | Flagship phone |
| iDoris-PC | Qwen3.5-9B | 9B | Mac Studio / 4090 |
| iDoris-Community | **Qwen3.6-35B-A3B** | 35B / 3B active | Mac Studio Ultra / dual 4090 |
| iDoris-City | Qwen3.5-122B-A10B | 122B / 10B active | Multi-GPU server |

**Whole family shares Qwen series backbone** — prerequisite for cross-tier LoRA compatibility.

## §5 How the Three Tiers Are Connected by Blood

### 5.1 Same Backbone + Stacked LoRA

LoRA's stackability comes from its linear structure. At inference:

```
W_final = W_base + Σ_i α_i × ΔW_i
        = W_base + α_personal × ΔW_personal
                 + α_community × ΔW_community
                 + α_city × ΔW_city
```

This means:
- A user can use **only local Personal LoRA** (strictest privacy mode)
- Or **stack Community LoRA** to access community wisdom
- Government queries can **stack City LoRA** for public service knowledge

α coefficients are user-controlled in Sin90 GUI sliders — "how much do I trust community/city knowledge".

### 5.2 LoRA Cross-Size Portability

Academia has shown ([SLoRA, NeurIPS 2024](https://arxiv.org/abs/2308.06522)): within the same model family, LoRA trained on smaller models partially transfers to larger ones. iDoris-Mobile (2B) personal preference LoRA can "grow up" to PC (9B) without retraining.

### 5.3 Relation to Frontend Apps

iDoris is the **model layer**; Sin90, Cos72, CityOS are the **application layer**. Analogy: iOS to Apple Foundation Models.

| Layer | Content | Naming |
|-------|---------|--------|
| Application | User-facing products / GUI / workflows | **Sin90 / Cos72 / CityOS** |
| Model | Core AI models + training pipelines | **iDoris-Personal / Community / City** |

(Earlier conversations had ~~CN90~~, ~~Cosine72~~, ~~CTOS~~ — speech recognition errors. Correct: Sin90 / Cos72 / CityOS.)

## §6 Data Flow and Privacy Architecture

### 6.1 Stance: Weights Are Not Raw Privacy Data

> Weights are not direct privacy data. They are the computation result of "privacy data + algorithm". With algorithm open source + AI-automated audit confirming no backdoor + explicit user authorization, LoRA weight deltas can be uploaded for upstream training.
> — Founder's stance at launch

This corresponds to academia's **DP-FedAvg + Algorithm Auditing** approach. It enables:
- Personal → Community LoRA upload ✅ Feasible
- Community → City LoRA upload ✅ Feasible
- While **raw data absolutely never leaves device** ✅ No compromise

### 6.2 Three Gates + Mathematical Guarantees

```
Personal raw data (local)
    ↓ Gate 1: PII auto-redaction (Microsoft Presidio + Chinese NER)
Redacted data (local)
    ↓ Gate 2: Topic-level user authorization (work/life/health/finance)
LoRA training data (local)
    ↓ Local training (MLX-LM / Unsloth)
Personal LoRA weights (local)
    ↓ Gate 3: DP-SGD gradient noise (ε ≤ 8, δ ≤ 1e-5)
DP-LoRA weight delta (uploadable)
    ↓ Gate 4: Upload-time second audit + outlier rejection (Krum / Median)
Community LoRA federated aggregation (FedAvg / SLoRA)
```

**Core math: DP-SGD** ([Abadi et al., CCS 2016](https://arxiv.org/abs/1607.00133)) — controlled Gaussian noise per gradient step, strictly bounding the probability of inferring individual training samples from the final model.

(ε, δ) are privacy budgets. iDoris targets ε ≤ 8, δ ≤ 1e-5 — industrial-grade privacy.

### 6.3 Federated LoRA Algorithm Selection

We plan to experiment with three in parallel:

- **FedAvg-LoRA** ([McMahan et al., AISTATS 2017](https://arxiv.org/abs/1602.05629), LoRA variant)
- **SLoRA** ([NeurIPS 2024](https://arxiv.org/abs/2308.06522), purpose-built for federated PEFT)
- **FedIT** ([ICLR 2024](https://arxiv.org/abs/2305.05644), federated LLM benchmark)

Engineering: [Flower](https://flower.ai/) + [OpenFedLLM](https://github.com/rui-ye/OpenFedLLM).

## §7 Progressive Path: One Line, Not Three Projects

### 7.1 Roadmap

```
Phase 1 (M1-M3, 2026 Q2-Q3): iDoris-Personal-PC MVP
    └ Founder as sole user, run Qwen3.5-9B + LoRA + RAG + DPO
    └ Output: Local AI that learns founder's writing style on Mac Studio

Phase 2 (M4-M5, 2026 Q4): iDoris-Personal-Mobile distillation
    └ Distill 9B Personal LoRA to 2B mobile
    └ Output: iOS / Android App, offline-capable

Phase 3 (M6-M9, 2027 Q1-Q2): iDoris-Community pilot
    └ First real community (Mycelium DAO internal / open-source community)
    └ Run Federated LoRA aggregation
    └ Output: shared community AI roles

Phase 4 (M10-M18, 2027 Q3+): iDoris-City PoC
    └ ≥5 real Community nodes → distill City model
    └ Pilot with city / district government
```

### 7.2 Why Bottom-Up, Not Top-Down Distillation

DeepSeek-R1's success path is **top-down distillation**: train large (R1 671B), distill to small (1.5B / 8B / 70B). This is the corporate model: centralized compute trains flagship, distributes to users.

iDoris goes the opposite way: **bottom-up federation** — Personal first, then aggregate to Community, then to City. The reason isn't technical superiority but:

> **Data ownership belongs to users**. Any "upper-layer model" must grow from voluntarily contributed user data, not be distributed top-down.

This is a **stance about ownership** behind the engineering choice — direct technical embodiment of Mycelium Protocol's "digital sovereignty" ([Mycelium MISSION](https://github.com/HyperCapitalHQ/mycelium-protocol)).

## §8 Not Performance Art: The Real Uncertainties

This section deserves its own chapter — because AI hype has made "vision posts" synonymous with "overpromising". I list known-unsolved risks at launch:

### Risk 1: Single-User Data May Not Be Enough

Academia has no consensus on the minimum sample count for a useful LoRA. Common heuristic: thousands to tens of thousands. My notes + blog + chat ≈ 5,000-15,000 effective samples — **maybe just enough, maybe not**.

**Mitigation**: If Phase 1 fails to learn stable style, fallback to synthetic data augmentation (large model generates "in your style" samples, manually curated).

### Risk 2: Federated Aggregation 5-15% Worse Than Centralized

This is empirically observed (see OpenFedLLM paper experiments). **Federated learning's privacy gain has a cost**.

**Mitigation**: Periodically have community core maintainers do a centralized fine-tune on community-public data as an "anchor". This is engineering compromise, not a perfect solution.

### Risk 3: Catastrophic Forgetting

LoRA in continual learning forgets early capabilities. Solutions (MoE-LoRA / AdapterFusion) are imperfect.

**Mitigation**: iDoris's layered LoRA somewhat isolates risk — base never changes; worst case is one tier's LoRA retraining.

### Risk 4: MLX-LM Engineering Maturity

Apple Silicon's MLX ecosystem is one step behind PyTorch / CUDA. LoRA / DPO / federated aggregation on MLX **may have bugs or missing APIs**.

**Mitigation**: Fallback to renting cloud GPU (Lambda / Modal Labs spot) for training, sync results back to Mac for inference.

### Risk 5: Fundamental Validation Standard

I plan 1-3 months to verify whether this works. **The judgment metric is not technical** (Perplexity / BLEU) but subjective "how well does it understand me" — comparing against Claude / ChatGPT in writing emails, organizing thoughts, processing private notes.

If after 3 months I think "I'd rather keep using Claude", iDoris-Personal needs reassessment. **This is an honest open question, not a foregone conclusion**.

## §9 Model Evolution: When a Better Backbone Arrives, Is Prior Work Wasted?

A common challenge: you're investing in Qwen3.5/3.6 LoRA / RAG / DPO now — when DeepSeek V5 / Llama 5 / Qwen 4 come out in 6 months, is everything thrown away?

### 9.1 Answer: Only One of Four Components Is Backbone-Bound

iDoris's training stack has four components. **Only LoRA weights themselves are backbone-bound**. The other three are backbone-agnostic:

| Component | Backbone Coupling | Migration Cost |
|-----------|-------------------|----------------|
| RAG vector DB | None | **0%** (direct reuse) |
| DPO preference dataset | None | **0%** (direct reuse) |
| LoRA training corpus | None | **0-15%** (depends on tokenizer compatibility) |
| LoRA weights | Full | **100%** (must retrain) |

This is intentional engineering: **value lives in data and methodology, not in specific weights**.

### 9.2 Three Migration Scenarios

| Scenario | Example | Effort | Notes |
|----------|---------|--------|-------|
| **A. Same-family upgrade** | Qwen3.6 → Qwen4 | ~5-10% | tokenizer compatible, similar architecture, retrain LoRA + DPO overnight |
| **B. Cross-family same-size** | Qwen3.5-9B → DeepSeek-Lite-9B (assuming such size exists) | ~20-30% | Different tokenizer requires data reformatting; architecture differences need LoRA config tuning |
| **C. Cross-architecture cross-size** | Qwen3.5-9B → DeepSeek V4 Flash 284B-A13B | ~40-50% | Size jump requires LoRA rank redesign; MoE architecture needs different PEFT strategy |

In practice, A and B dominate. **20-30% migration cost is a reasonable estimate**.

### 9.3 Two Conditions for Triggering Migration

Migration shouldn't chase novelty. It should satisfy at least one of:

1. **New model has appropriate size matrix**: e.g., DeepSeek releases a Lite-2B/9B series covering Mobile/PC tiers. Without this, DeepSeek V4 Flash (284B/13B-A) is unreachable for Personal/Community tiers.
2. **Hardware costs drop enabling larger sizes**: e.g., M5 Ultra makes 256GB unified memory affordable, allowing the original City-tier 122B model to drop down to Community tier.

If neither holds, don't migrate.

### 9.4 Engineering Soundness, Not Self-Comfort

If we adopted **single backbone + full fine-tuning**, migration cost would be ~100% — because the model itself is the artifact.

We chose **modular PEFT + backbone-agnostic components**, which aligns with the 2023-2025 open-source consensus: see HuggingFace [PEFT library](https://github.com/huggingface/peft) design philosophy, see [LangChain](https://github.com/langchain-ai/langchain) / [LlamaIndex](https://github.com/run-llama/llama_index) decoupling "knowledge" from "model".

**Conclusion**: iDoris's training investment won't go to zero when backbones iterate — provided we chose the right architecture from day one. That was the core decision at launch.

---

## §10 Why Now + How to Join

### 10.1 Why This Moment

Three things converged around 2026 Q2:

1. **Model ecosystem mature**: Qwen3.5/3.6 (2026-02 ~ 04), DeepSeek V4 (2026-04-24), Gemma 4 — open-source LLMs nearing closed flagship parity
2. **Hardware accessible**: M4 Ultra Mac Studio offers 64-192GB unified memory, turning "independent researcher running large models" from myth to routine
3. **Organizational framework ready**: [Mycelium Protocol](https://launch.mushroom.cv) provides a protocol layer + funding path (cold launch, not VC) for collective action

Any one being a year earlier wouldn't have enabled this. Not necessary conditions, but a sufficient combination.

### 10.2 How to Join (Permissionless to Start)

iDoris is a research project under [Aura AI](https://github.com/AuraAIHQ), a sub-org of Mycelium Protocol. All code Apache 2.0.

If you also wonder:
- "Why doesn't ChatGPT/Claude understand me after a year?"
- "How can individuals / small communities own their AI without being harvested by platforms?"
- "Can data sovereignty and AI capability coexist?"

Join via:

- **Code**: [github.com/AuraAIHQ/iDoris](https://github.com/AuraAIHQ/iDoris) (early stage, issues welcome)
- **Ecosystem**: Permissionless join [Mycelium Protocol](https://launch.mushroom.cv); free use of models and pipelines
- **Discussion**: [Full plan](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md) public on GitHub

### 10.3 Authorization: Free, but Light Registration for >50 Person Orgs (Anti-Abuse + Mutual Feedback)

License has two tiers, **both free**. Difference is whether authorization is needed:

| Scale | License | Authorization Required |
|-------|---------|----------------------|
| ≤50 person community / individual | Permanent free | **No authorization needed**, just use |
| >50 person non-commercial / SMB | Free to use | **"Official authorization" required** (light registration, no fee) |

Authorization purpose (**not for charging fees**):

- **User registry**: Lets us know which communities / orgs are using iDoris; builds a public user list (transparent)
- **Mutual feedback**: Periodic sharing of usage notes, gotchas, improvement ideas — the lifeblood of open-source communities
- **Brand protection**: Prevents commercial misuse / closed-source forks / fake "Mycelium Protocol" branding
- **Dual-org protection**: Following the Linux + RedHat model, protects the cooperation between the open-source org (MushroomDAO) and commercial entity ([HyperCapital](https://github.com/HyperCapitalHQ))

**Light authorization process**:
1. Submit a simple registration form via [launch.mushroom.cv](https://launch.mushroom.cv) (community name, scale, contact, use case)
2. MushroomDAO committee reviews (typically responds within days)
3. Once approved, use freely. Update feedback every 6 months.

Detailed License text: see [Mycelium Protocol GitHub](https://github.com/HyperCapitalHQ/mycelium-protocol).

---

## References

### Core Papers

- LoRA: Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- QLoRA: Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs", NeurIPS 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- DPO: Rafailov et al., "Direct Preference Optimization", NeurIPS 2023, [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)
- DP-SGD: Abadi et al., "Deep Learning with Differential Privacy", CCS 2016, [arXiv:1607.00133](https://arxiv.org/abs/1607.00133)
- FedAvg: McMahan et al., "Communication-Efficient Learning", AISTATS 2017, [arXiv:1602.05629](https://arxiv.org/abs/1602.05629)
- SLoRA: NeurIPS 2024, [arXiv:2308.06522](https://arxiv.org/abs/2308.06522)
- FedIT: ICLR 2024, [arXiv:2305.05644](https://arxiv.org/abs/2305.05644)

### Models & Ecosystem

- [Qwen3.6 GitHub](https://github.com/QwenLM/Qwen3.6) · [Qwen3 Blog](https://qwenlm.github.io/blog/qwen3/) · [Nathan Lambert: Qwen 3](https://www.interconnects.ai/p/qwen-3-the-new-open-standard)
- [DeepSeek V4 TechCrunch](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/) · [Simon Willison on V4](https://simonwillison.net/2026/Apr/24/deepseek-v4/)
- [Best LLM for Mac 2026](https://willitrunai.com/blog/best-llm-for-mac-apple-silicon-2026) · [MLX-LM 2026 Guide](https://markaicode.com/run-fine-tune-llms-mac-mlx-lm/)
- [Unsloth](https://github.com/unslothai/unsloth) · [Flower](https://flower.ai/) · [OpenFedLLM](https://github.com/rui-ye/OpenFedLLM) · [LightRAG](https://github.com/HKUDS/LightRAG)
- [Microsoft Presidio](https://github.com/microsoft/presidio) · [Opacus](https://opacus.ai/)

### Mycelium Protocol Internal

- [iDoris Master Plan](https://github.com/MushroomDAO/blog/blob/main/research/iDoris/iDoris-master-plan.md)
- [Mycelium Protocol](https://github.com/HyperCapitalHQ/mycelium-protocol) · [MushroomDAO](https://github.com/MushroomDAO)
- [Cold Launch (launch.mushroom.cv)](https://launch.mushroom.cv)
- [Sin90 Personal OS](https://github.com/MushroomDAO/Sin90) · [Cos72 Community OS](https://github.com/AAStarCommunity/Cos72)
- [BroodBrain](https://github.com/AAStarCommunity/Brood)
