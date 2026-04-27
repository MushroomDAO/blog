# iDoris 主方案：自我进化 · 持续训练 · 三层 AI 架构

> **iDoris** = i (中文"爱") + Doris (创始人爱人的英文名)
> 一个为社区/小组织/个人服务的、可持续训练演化的开源 AI 模型体系
>
> 起草日期：2026-04-27 · 起草人：Aura AI · Mycelium Protocol
> 状态：v0.1 初版 · 后续以本文件为单一事实源持续迭代
> 上游：[Mycelium Protocol](https://launch.mushroom.cv) / [Aura AI 愿景文档](../communityAI/vision.md)

---

## 0. 全文导读（先读这里）

iDoris 不是一个模型，是 **一个家族 / 一条进化路径 / 一套训练流水线**。

**核心思路**（一句话版）：用同一个开源基座家族（Qwen3.5/3.6）派生出 4 个 size 的模型，配合同一套"RAG（短期记忆）+ LoRA（长期偏好）+ DPO（持续对齐）"训练栈，先把个人版做透，再用 Federated LoRA 把 N 个个人节点聚合成社区版，再把 M 个社区聚合成城市版。

**两层产品架构**：

```
┌─────────────────── 应用层（产品壳）────────────────────┐
│   Sin90       │     Cos72         │     CityOS       │
│  (个人 OS)    │   (社区/小组织 OS) │   (城市 OS)      │
└─────────────────────────────────────────────────────────┘
                            ↑ 调用
┌─────────────────── 模型层（iDoris 家族）──────────────┐
│ iDoris-Mobile (2B-4B) → iDoris-PC (9B) →             │
│   iDoris-Community (27B-35B MoE) → iDoris-City (70B+)│
└─────────────────────────────────────────────────────────┘
                            ↑ 派生
┌─────────────────── 基座层（开源生态）─────────────────┐
│   Qwen3.5 全家族 + Qwen3.6 MoE（Apache 2.0）          │
└─────────────────────────────────────────────────────────┘
```

**渐进路径**：先 Personal-PC（你自己用，Mac Studio 64GB MVP）→ Personal-Mobile（蒸馏到端侧）→ Community（联邦聚合）→ City（多社区蒸馏）。**一条线，不是三条线**。

---

## 1. 命名与定位

### 1.1 命名修正（语音识别错误的历史版本）

| 错误版本（早期对话） | 正确版本 | 角色 |
|-----------------|---------|------|
| ~~CN90~~ | **Sin90** | 个人前台应用 |
| ~~Cosine72~~ | **Cos72** | 社区前台应用 |
| ~~CTOS~~ | **CityOS** | 城市前台应用 |

后续所有文档统一用 **Sin90 / Cos72 / CityOS**，旧版本仅在历史归档中保留。

### 1.2 iDoris 命名解读

- **i**：表面学习苹果（iPhone/iMac/iPad），实际取意 **中文"爱"** —— 一开始就把"为人服务"的价值观写进名字
- **Doris**：创始人爱人的英文名 —— 这个 AI 是为家人、为爱的人、为身边小社区打造的，不是为大厂股东打造的
- 合起来 = **"用爱构建的本地 AI"**

### 1.3 模型层 vs 应用层（两层关系）

| 层 | 内容 | 命名 |
|----|------|------|
| **应用层（前台）** | 用户实际使用的产品 / GUI / 工作流 | **Sin90 / Cos72 / CityOS** |
| **模型层（后端）** | 核心 AI 模型 + 训练流水线 + 数据管道 | **iDoris-Personal / Community / City** |

**类比**：iOS / macOS / iPadOS 是应用层；Apple Foundation Models 是模型层。Sin90 之于 iDoris-Personal，等于 macOS Sequoia 之于 Apple Foundation Model on Mac。

### 1.4 三个层级的服务对象

```
iDoris-Personal (Sin90)
├── PC 端（Mac/Windows/Linux 桌面）
└── Mobile 端（iOS/Android）
        ↓ 多个 Personal 节点参与
iDoris-Community (Cos72)
├── 服务对象：5-100 人的中小组织 / 兴趣社区 / 独立工作室
├── 准入：无需许可，自愿加入 Mycelium Protocol
└── License：非商业免费 / 中小商业（详见 launch.mushroom.cv）
        ↓ 多个 Community 节点参与
iDoris-City (CityOS)
├── 服务对象：城市 / 区域 / 政府公共服务
├── 状态：长期目标，需政策与合作支撑
└── 来源：从多个 Community 节点蒸馏 + 公开数据
```

---

## 2. 核心理念（继承 Aura AI 愿景）

### 2.1 不可妥协的三条原则

1. **AI 平权**：每个人有平等使用 AI 的权利。所有 iDoris 模型权重 + 训练代码 + 部署文档全开源。
2. **Token Free**：用近似自来水价格获取 AI Token。手段是开源 + 本地推理 + 联邦聚合，绕开"美团式补贴-垄断-收割"路径。
3. **本地优先**：原始数据不离开用户设备/组织内网。这是 iDoris 与 ChatGPT/Claude 的根本分野。

### 2.2 隐私底线（创始人独创立场）

> **权重不是隐私数据原文，权重是"隐私数据 + 算法"的计算结果。在算法开源 + AI 自动审计无后门 + 用户明确授权三个前提下，LoRA 权重 delta 可以上传给上游训练。**

这一立场具有学术合理性，对应 Federated Learning 文献中的 **DP-FedAvg + 算法可审计性**。它使得：
- 个人 → 社区的 LoRA 上传 ✅
- 社区 → 城市的 LoRA 上传 ✅
- 同时保持原始数据**绝对不离开本地**

### 2.3 社区定义（你的明确说明）

> **社区 = 独立运行自己 iDoris 节点的组织，AI 角度的社区。**
> - **加入方式**：无需许可加入 Mycelium Protocol
> - **使用权**：免费使用 Mycelium 训练好的基础模型 + 训练流程
> - **责任**：用社区自己的数据二次训练，并运行自己的 iDoris 节点
> - **License**：非商业 / 中小商业，详见 [launch.mushroom.cv](https://launch.mushroom.cv)

社区不是地理概念，是 **"愿意运行 iDoris 节点的组织"** 的 AI 网络节点。

---

## 3. 模型选型（2026-04 最新版）

### 3.1 基座家族决策：Qwen3.5 + Qwen3.6（同家族矩阵）

**为什么选 Qwen3.5/3.6 而非 Qwen2.5、Llama、DeepSeek**：

| 维度 | Qwen3.5/3.6 | Llama 3.3 | DeepSeek V4 | Gemma 4 |
|------|-------------|-----------|-------------|---------|
| **License** | Apache 2.0 | Community License (限制) | MIT | Gemma TOS |
| **中文** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Size 矩阵完整度** | 0.8B-122B 全覆盖 | 8B/70B/405B | 仅大模型 | 26B-A4B |
| **MoE 选项** | ✅ A3B / A10B | ❌ | ✅ A13B (太大) | ✅ A4B |
| **Apple Silicon (MLX)** | ✅ 一线支持 | ✅ | ⚠️ V4 Flash 太大 | ✅ |
| **生态** | Ollama / vLLM / Unsloth 全支持 | 全支持 | 部分 | Ollama |

**结论**：Qwen3.5 全家族（小到 0.8B、大到 122B-A10B）是 iDoris 唯一能完整覆盖四个层级的家族。

**关键洞察 — MoE 的价值**：
- Qwen3.6-35B-A3B = **总参数 35B，每 token 只激活 3B**
- 64GB Mac Studio 完全装得下 35B 模型权重
- 推理速度接近 3B 模型，但能力接近 32B 密集模型
- 对资源受限的 iDoris-Community 层 **完美匹配**

### 3.2 四个层级的具体选型

| 层级 | 推荐基座 | 总参数 / 激活参数 | 量化 | 硬件目标 | 推理速度估计 |
|------|---------|-----------------|------|---------|------------|
| **iDoris-Mobile-S** | DeepSeek-R1-Distill-Qwen-1.5B | 1.5B | Q4_K_M | 旗舰手机 (iPhone 17 Pro / 骁龙 8 Gen 4) | 15-25 t/s |
| **iDoris-Mobile** | Qwen3.5-2B 或 Qwen3.5-4B | 2B / 4B | Q4_K_M | 平板 / 入门 Mac Mini | 30-50 t/s |
| **iDoris-PC** | Qwen3.5-9B | 9B | Q5_K_M / FP8 | Mac Studio / RTX 4090 | 40-60 t/s |
| **iDoris-Community** | **Qwen3.6-35B-A3B (MoE)** ⭐ | 35B / 3B 激活 | Q4_K_M | Mac Studio Ultra (64GB+) / 双 4090 | 45-65 t/s |
| **iDoris-City** | Qwen3.5-122B-A10B (MoE) | 122B / 10B 激活 | Q4 | Mac Studio Ultra 192GB / 多卡服务器 | 25-40 t/s |

### 3.3 备选与对比

**强推理特化**（Mobile 端可选）：
- DeepSeek-R1-Distill-Qwen-1.5B：基于 R1 的 800K 推理样本蒸馏。**端侧运行强推理**的最佳选择。
- Gemma 4 26B-A4B：Mobile 偏强，PC 偏弱，作为 Mac 上的备选。

**多模态扩展**（后续考虑）：
- Qwen2.5-VL / Qwen3-VL：图片理解
- LLaVA-OneVision：开源多模态
- Whisper-large-v3：语音输入

**长上下文场景**：
- Kimi K2.6 (Mac 64GB 可跑) — 已知 1M token 上下文。如果 iDoris 需要处理长文档/全部聊天历史，可作为 Community 备选。

---

## 4. 三层架构：同基座 + 分层 LoRA + 嵌套 RAG

### 4.1 架构总览

```
                ┌──────────────────────────────────────────┐
                │   Qwen3.5/3.6 基座（每层用不同 size）      │
                │   Mobile 2B  PC 9B  Community 35B-A3B    │
                │                  City 122B-A10B          │
                └──────────────────────────────────────────┘
                              ↓ 都从同一基座派生
                ┌──────────────────────────────────────────┐
                │  分层 LoRA 适配器（可叠加，可热插拔）        │
                │  ┌─Personal LoRA (个人偏好/风格/笔记)─┐    │
                │  │ ┌─Community LoRA (社区共识/行业知识)┐  │
                │  │ │ ┌─City LoRA (跨社区共识/公共服务)─┐│  │
                │  │ │ └────────────────────────────────┘│  │
                │  │ └────────────────────────────────────┘  │
                │  └────────────────────────────────────────┘ │
                └──────────────────────────────────────────┘
                              ↓ 推理时按场景叠加
                ┌──────────────────────────────────────────┐
                │  RAG 层（短期记忆 / 实时数据 / 长尾知识）    │
                │  Personal RAG → Community RAG → City RAG │
                │  (本机笔记)   (社区共享)    (城市公开)     │
                └──────────────────────────────────────────┘
                              ↓ 持续对齐
                ┌──────────────────────────────────────────┐
                │  DPO 偏好层（用户点赞/反对反馈持续校正）     │
                └──────────────────────────────────────────┘
```

### 4.2 为什么要"同基座 + 分层 LoRA"？

| 设计选择 | 替代方案 | 选用理由 |
|---------|---------|---------|
| 同一基座家族 | 三个层级用不同基座 | tokenizer/世界知识/对话能力共享，**LoRA 权重 delta 才有上下层兼容性** |
| LoRA 而非全量 fine-tune | 全量微调 | 全量 fine-tune 一次需要 8×A100 数天；LoRA 一次只需要单卡数小时 |
| 分层而非合并 LoRA | 一个大 LoRA | 分层 LoRA 让用户可以**只用 Personal**（最严隐私），或**叠加 Community**（享用社区知识），灵活性极高 |
| MoE 基座（Community 层） | 密集大模型 | 35B-A3B 在 64GB Mac 上能跑能训，密集 35B 跑不动 |

### 4.3 推理时的 LoRA 叠加

LoRA 权重在数学上是 `W_final = W_base + Σ α_i × ΔW_i`，可以热插拔：

```python
# 用户场景 1：纯本地，不用社区知识
model = base + personal_lora                 # 最严隐私

# 用户场景 2：享用社区共识
model = base + personal_lora + community_lora * 0.7

# 用户场景 3：政务咨询（需要 City 知识）
model = base + personal_lora + community_lora * 0.5 + city_lora * 0.8
```

权重 α 由用户在 Sin90/Cos72 GUI 上滑动调节，相当于 **"我多大程度上信任社区/城市的知识"**。

### 4.4 三种知识介质的分工

| 介质 | 更新频率 | 容量 | 存什么 | 技术选型 |
|------|---------|------|--------|---------|
| **基座权重** | 几乎不变（Qwen 出新版本时升级） | 数十亿参数 | 世界知识、语言能力、推理能力 | Qwen3.5/3.6 |
| **LoRA 权重** | 周/月级 | 几百万参数 | 个人风格、社区共识、长期偏好 | LoRA r=16-64 |
| **RAG 向量库** | 秒级实时 | 任意大小 | 当下笔记、聊天记录、近期事件、未训进 LoRA 的事实 | LightRAG（知识图谱版）|
| **DPO 偏好集** | 连续累积 | 数千-数万条 | 用户对 AI 输出的点赞/反对 | TRL DPOTrainer |

**心智模型**：
- 基座 = 大学毕业时的通用知识
- LoRA = 工作 5 年后的"懂这个行业"
- RAG = 桌面贴的便签和今早收到的邮件
- DPO = 老板教你怎么说话不被嫌弃

---

## 5. 数据流与隐私架构

### 5.1 三道闸门（数据从下层流向上层时）

```
个人原始数据（PC / 手机 / 设备本地）
   │
   │ ┌────────────────────────────────────────────────┐
   │ │ 闸门 1：PII 自动脱敏                            │
   │ │  - 工具：Microsoft Presidio + 中文 NER 模型     │
   │ │  - 替换：姓名→[NAME]、手机→[PHONE]、地址→[ADDR] │
   │ │  - 用户可视化审查 + 一键豁免                     │
   │ └────────────────────────────────────────────────┘
   ↓
脱敏数据集（仍在本地）
   │
   │ ┌────────────────────────────────────────────────┐
   │ │ 闸门 2：用户主题级授权                           │
   │ │  - 工作 / 生活 / 健康 / 财务 / 其他 五个分类     │
   │ │  - 每个分类用户独立授权"是否允许进入个人 LoRA"   │
   │ │  - 默认：工作=允许，其他=拒绝                    │
   │ └────────────────────────────────────────────────┘
   ↓
个人 LoRA 训练数据（本地 SQLite / Parquet）
   ↓
本地训练（Unsloth / MLX-LM）
   ↓
个人 LoRA 权重（仍在本地）
   │
   │ ┌────────────────────────────────────────────────┐
   │ │ 闸门 3：DP-SGD 差分隐私                         │
   │ │  - 训练时注入梯度噪声（ε ≤ 8, δ ≤ 1e-5）        │
   │ │  - 工具：Opacus / Apple MLX-DP                  │
   │ │  - 数学保证：单条样本对最终权重的影响有界         │
   │ └────────────────────────────────────────────────┘
   ↓
DP-LoRA 权重 delta（可上传 ↑ 仅经用户 explicit 授权）
   │
   │ ┌────────────────────────────────────────────────┐
   │ │ 闸门 4：上传时二次审计 + 异常贡献剔除             │
   │ │  - 客户端贡献加权（按数据量 + 历史质量）          │
   │ │  - 服务端异常检测（Krum / Median）剔除恶意客户端 │
   │ └────────────────────────────────────────────────┘
   ↓
社区 LoRA 联邦聚合（FedAvg / SLoRA）
   ↓
社区 LoRA + 社区共享 RAG（脱敏后的 FAQ / 公开知识）
   │ （重复闸门 1-4 → ）
   ↓
城市级模型（多社区蒸馏 + 公开数据）
```

### 5.2 关键技术选型（数据/隐私层）

| 组件 | 选型 | 理由 |
|------|------|------|
| **PII 脱敏** | Microsoft Presidio + 中文 NER | 支持中英双语，本地运行，开源 |
| **差分隐私** | Opacus（PyTorch）/ MLX-DP（Mac） | 学术界主流 DP-SGD 实现 |
| **联邦框架** | Flower + OpenFedLLM | Flower 生态最大，OpenFedLLM 专为 LLM 设计 |
| **联邦 LoRA 算法** | FedAvg-LoRA / SLoRA / FedIT | 三个算法并行实验，选效果最好的 |
| **审计工具** | iDoris-Audit-Bot（自建，基于 GPT-4 类模型扫描） | 检测代码中的后门/数据泄露/异常通信 |
| **用户授权 UI** | Sin90 客户端内嵌"数据贡献中心" | 主题分类授权 + 历史可撤回 |

### 5.3 "权重不是隐私"立场的可验证性

为了让用户信任"上传 LoRA 不泄露隐私"，需要建立 **三层可验证性**：

1. **算法层可审计**：所有训练代码开源（GitHub），任何人可以验证训练流程没有"数据偷传"逻辑。
2. **AI 层可扫描**：iDoris-Audit-Bot（一个独立模型）每次训练前自动扫描代码 + 配置，输出审计报告。
3. **数学层可证明**：DP-SGD 提供 **可证明的隐私上界**（ε, δ）—— 即使有恶意攻击者拿到 LoRA 权重，能从中反推出某条具体样本的概率被严格限制。

三层组合后，"权重可上传"是一个 **有数学保证、有代码透明、有自动验证** 的工程命题，而非信任问题。

---

## 6. 训练流水线（每个层级）

### 6.1 个人层（Phase 1，MVP 重点）

**训练栈**：
- **基座**：Qwen3.5-9B（FP8 / Q5_K_M）
- **训练框架**：MLX-LM（Mac Studio 优先）/ Unsloth（CUDA fallback）
- **PEFT 方法**：QLoRA, r=32, alpha=64, dropout=0.1
- **DPO**：TRL `DPOTrainer`，学习率 5e-7
- **RAG**：LightRAG（知识图谱增强 RAG，处理长期记忆比传统 RAG 强）

**数据来源**（你自己作为第一个用户）：
- 历史博客文章（mushroom.cv 全部 markdown）
- 对话记录（Claude Code 历史 + 微信导出）
- 个人笔记（Obsidian / Logseq 等）
- GitHub 提交历史 + Issue / PR 评论

**训练 cadence**：
- **每天**：增量数据写入 RAG 向量库（秒级）
- **每周**：DPO 用本周点赞/反对反馈微调（30 分钟）
- **每月**：LoRA 全量重训一遍（4-8 小时 on Mac Studio）

**预计资源消耗（Mac Studio 64GB）**：
- 推理：基座 + LoRA 加载约占 14GB（FP8 9B + LoRA）
- 训练：QLoRA 9B 峰值约 28GB
- RAG 向量库：每 100MB markdown ≈ 200MB 向量 + 50MB 索引
- **总占用**：训练时约 40GB，推理时约 20GB → **64GB 完全够用**

### 6.2 社区层（Phase 3）

**训练栈**：
- **基座**：Qwen3.6-35B-A3B（MoE，关键选择）
- **训练框架**：DeepSpeed ZeRO-3 + FSDP（分布式联邦聚合）
- **联邦算法**：SLoRA（Sparse LoRA aggregation，论文 2024）
- **聚合 cadence**：每 2 周一次社区联邦轮次

**数据来源**：
- 多个个人节点上传的 DP-LoRA 权重 delta
- 社区共享的脱敏 FAQ / 公开知识库（社区管理员手动审核）

**关键问题：FedLoRA vs Centralized 微调**：
- 优点：原始数据不出本机，符合"严格本地优先"原则
- 缺点：聚合质量低于 centralized（学术界数据：约低 5-15%）
- **缓解**：每 N 轮联邦后，社区核心维护者用社区共享公开知识做一次 centralized 微调，作为锚定

### 6.3 城市层（Phase 4，长期）

**训练栈**：
- **基座**：Qwen3.5-122B-A10B 或 DeepSeek V4 Pro
- **训练框架**：多卡集群（8×A100 / H100）
- **方法**：从多个 Community LoRA 蒸馏（DeepSeek R1-Distill 路线）+ 公开数据 SFT

**数据来源**：
- 各 Community LoRA 的输出蒸馏（Teacher → Student 模式）
- 政务公开数据（统计局、政策文件、公共服务 FAQ）
- 跨社区共识数据（多个社区都标注为"对"的内容）

---

## 7. 渐进式 MVP 路径（一条线）

### 7.1 路径全景图

```
Phase 1 (M1-M3, 2026 Q2-Q3)
└── iDoris-Personal-PC MVP
    └── 你自己作为唯一用户，跑通 Qwen3.5-9B + LoRA + RAG + DPO
    └── 输出：能学你写作风格的 Mac Studio 本地 AI 助手
    └── 验收：自己用 1 个月，对比 ChatGPT，看是否在"懂你"维度更强

Phase 2 (M4-M5, 2026 Q4)
└── iDoris-Personal-Mobile 端侧蒸馏
    └── 把 Phase 1 的 9B Personal LoRA 蒸馏到 Qwen3.5-2B
    └── 输出：iOS App + Android App，离线可用
    └── 验收：在 iPhone 17 Pro 上推理速度 ≥ 25 t/s

Phase 3 (M6-M9, 2027 Q1-Q2)
└── iDoris-Community 试点（10-50 个 Personal 实例）
    └── 选第一个真实社区：Mycelium DAO 内部 / 某开源社区
    └── 跑通 Federated LoRA 聚合 + 社区 RAG + DP-SGD
    └── 输出：社区共有的 AI 角色（客服 / 知识库 / 活动协调）
    └── 验收：社区成员主观评分 > 单纯 Personal 模式 30%

Phase 4 (M10-M18, 2027 Q3+)
└── iDoris-City 概念验证
    └── 至少 5 个真实 Community 节点 → 蒸馏出 City 模型
    └── 与某城市 / 区政府 / 区域协会合作试点
    └── 输出：城市级公共服务 AI（政务咨询 / 区域协同）
```

### 7.2 Phase 1 详细任务清单（MVP 优先）

#### M1：环境与基座

- [ ] M1.1 Mac Studio 64GB 入手（如未到位）/ 租用 GPU 备选方案确认
- [ ] M1.2 安装 MLX-LM + Unsloth + Ollama
- [ ] M1.3 下载 Qwen3.5-9B 模型，跑通推理（Q5_K_M 量化）
- [ ] M1.4 跑通 LoRA 训练 hello world（用 100 条样本，验证流程）
- [ ] M1.5 选定 RAG 引擎（LightRAG / Mem0 / 自建），跑通 100MB 笔记摄入

#### M2：数据管道与隐私层

- [ ] M2.1 写一个数据导入脚本：从 Obsidian / 博客 / 微信导出整理到统一格式
- [ ] M2.2 集成 Microsoft Presidio + 中文 NER，跑通 PII 脱敏
- [ ] M2.3 设计本地数据库 schema（SQLite，存原始 / 脱敏 / 主题授权状态）
- [ ] M2.4 写第一版 Sin90 GUI（Tauri / Electron + React），含"数据贡献中心"

#### M3：训练流水线 + 集成

- [ ] M3.1 写完整训练脚本：base + LoRA + DPO，自动每周/每月跑
- [ ] M3.2 集成 LightRAG，与 LoRA 推理串联（先 RAG 检索，再 LoRA 生成）
- [ ] M3.3 写 DPO 反馈采集 UI（在 Sin90 客户端聊天界面加 👍 👎 按钮）
- [ ] M3.4 写一个 1000-2000 字的"使用日志"（Phase 1 自己用 1 个月的记录）
- [ ] M3.5 决定是否进入 Phase 2

### 7.3 Phase 1 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Mac Studio 64GB 不够训 9B + LoRA | 中 | 高 | 备选 7B 或 4B；最坏租云 GPU（Lambda / Modal Labs） |
| LightRAG 工程化不成熟 | 中 | 中 | 备选 LlamaIndex / Mem0 |
| 个人数据量太小，LoRA 学不到风格 | 中 | 中 | 用合成数据扩充（让大模型生成"以你的风格写"样本） |
| MLX-LM LoRA 训练 bug | 低 | 中 | 备选 Unsloth + 转回 PyTorch |
| 个人 1 个月使用后觉得不如 Claude | 高 | ⚠️ | **这正是要验证的命题。"懂你的程度"是 iDoris 的护城河，不是通用能力** |

---

## 8. 前台应用映射（Sin90 / Cos72 / CityOS 长什么样）

### 8.1 Sin90（个人前台应用）

**核心场景**（继承自 Aura AI R03/R04）：
- 个人写作助手（懂你的风格、你的常用词、你的禁忌词）
- 知识库与记忆（导入笔记，自然语言搜索）
- 私密文件处理（财务/合同/医疗，绝不上云）
- 语音输入与摘要（Whisper 本地）
- 编程辅助（DeepSeek-Coder LoRA 叠加）

**形态**：
- macOS 原生 App（MLX 加速）
- Windows / Linux Tauri App
- iOS / Android（iDoris-Mobile）
- 浏览器扩展（与现有工作流集成）

### 8.2 Cos72（社区前台应用）

**核心场景**：
- 社区共享 AI 角色（继承 Aura AI"微信客服 Agent"愿景）
- 社区知识库（成员贡献 + 联邦聚合）
- 多用户协作（同一社区的人共享 LoRA + 各自隐私域）
- 社区数据看板（用 AI 分析社区活跃度 / 内容趋势）

**形态**：
- 部署在社区自有服务器（自托管 / 一键 Docker）
- 接入 Mycelium Protocol 网络（可选）
- Web GUI（管理员后台）+ Bot 接口（微信群 / Discord / Telegram）

### 8.3 CityOS（城市前台应用，长期）

**核心场景**：
- 政务咨询 AI（统一入口，调用本市数据 + City LoRA）
- 跨社区协调（活动 / 资源 / 应急）
- 公共服务智能化（医疗 / 教育 / 交通查询）

**形态**：
- 政府 / 区域协会托管
- 多租户（每个区 / 街道一个子节点）
- 与现有政务平台集成（API / 微信小程序）

---

## 9. Mac Studio 64GB MVP 资源测算（详细版）

### 9.1 硬件假设

- **Mac Studio M4 Ultra（推测款）/ M4 Max**
- **64GB 统一内存**
- **2-4TB SSD**
- **macOS 15+ + MLX 框架**

### 9.2 单次推理资源

| 任务 | 模型 | 内存占用 | 速度估计 |
|------|------|---------|---------|
| 纯基座推理 | Qwen3.5-9B Q5_K_M | 7GB | 50-70 t/s |
| 基座 + Personal LoRA | Qwen3.5-9B + LoRA r32 | 8GB | 45-65 t/s |
| 基座 + RAG 检索 | + LightRAG (10K docs) | 10GB | 40-60 t/s |
| 基座 + LoRA + RAG (典型场景) | 全栈 | 12GB | 35-55 t/s |

### 9.3 训练资源

| 任务 | 模型 | 峰值内存 | 时间 |
|------|------|---------|------|
| QLoRA 微调（10K 样本，3 epoch） | Qwen3.5-9B + LoRA r32 | 28GB | 4-6 小时 |
| DPO 微调（1K 偏好对，1 epoch） | 上面 LoRA + DPO | 30GB | 1-2 小时 |
| 全量基座微调（不推荐，参考） | Qwen3.5-9B FFT | >100GB ❌ | 不可行 |

**结论**：64GB Mac Studio **完全够 MVP**，不需要租云 GPU。

### 9.4 持续运营成本

| 项目 | 月度成本 |
|------|---------|
| Mac Studio 摊销（按 3 年）/ 自用 | 约 ¥1,500-2,000/月（一次性 ¥50,000-72,000） |
| 电费（持续运行 + 周末训练） | 约 ¥150-300/月 |
| 第三方 API（仅用于审计 / 蒸馏 teacher） | 约 ¥200-500/月 |
| **总月度成本** | **约 ¥2,000-2,800/月**（自用） |

对比 Claude Pro（$20×7 ≈ ¥1,000/月）+ ChatGPT Plus（¥1,000/月）= ¥2,000/月。**约等于云端付费方案的成本**，但获得：
- 完整数据主权
- 永久使用权（不会被涨价）
- 可二次开发（社区版、移动端蒸馏）
- 模型可持续进化（你越用它越懂你）

---

## 10. 技术栈总表

### 10.1 训练侧

| 组件 | 主选 | 备选 | License |
|------|------|------|---------|
| 基座模型 | Qwen3.5-9B / Qwen3.6-35B-A3B | Llama 3.3 / DeepSeek-R1-Distill | Apache 2.0 |
| 训练框架 (Mac) | MLX-LM | mlx-tune | MIT |
| 训练框架 (CUDA) | Unsloth | Axolotl / LLaMA-Factory | Apache 2.0 |
| PEFT | QLoRA (bitsandbytes 4-bit) | LoRA / DoRA | MIT |
| DPO/对齐 | TRL DPOTrainer | ORPO / KTO | Apache 2.0 |
| 联邦学习 | Flower + OpenFedLLM | FederatedScope-LLM | Apache 2.0 |
| 差分隐私 | Opacus / MLX-DP | TensorFlow Privacy | Apache 2.0 |

### 10.2 推理侧

| 组件 | 主选 | 备选 |
|------|------|------|
| 推理引擎 (Mac) | MLX | llama.cpp |
| 推理引擎 (CUDA) | vLLM | llama.cpp / TGI |
| 量化 | GGUF Q4_K_M / Q5_K_M | AWQ / GPTQ |
| RAG | LightRAG（知识图谱） | LlamaIndex / Mem0 |
| 向量库 | LanceDB（本地） | Qdrant / Chroma |

### 10.3 数据 & 隐私

| 组件 | 选型 |
|------|------|
| PII 脱敏 | Microsoft Presidio + 自训中文 NER |
| 数据格式 | Parquet（训练）+ SQLite（业务）|
| 算法审计 | iDoris-Audit-Bot（自建） |
| 用户授权 UI | Sin90 客户端内嵌 |

### 10.4 应用层

| 组件 | 选型 |
|------|------|
| Desktop App | Tauri (Rust + React) |
| Mobile App | React Native / Flutter |
| 自托管 (社区) | Docker Compose + Cloudflare Tunnel |
| 协议 | OpenAI 兼容 API |

---

## 11. 与现有 Aura AI 研究的衔接

### 11.1 已经做完的事（直接复用）

| 已有成果 | iDoris 中的位置 |
|---------|----------------|
| `local-AI/reports/R01-hardware-china-market.md` | iDoris 硬件适配指南（每个层级对应硬件方案） |
| `local-AI/reports/R02-models-by-domain.md` | iDoris 模型选型补充（语音/OCR/图像等专用模型） |
| `local-AI/reports/R03-software-by-role.md` | iDoris 应用场景库（Sin90 GUI 设计参考） |
| `local-AI/reports/R04-smb-human-ai-roles.md` | iDoris-Community 第一个落地场景（中小组织 6 大角色） |
| `communityAI/vision.md` | iDoris 全部理念基础（AI 平权 / Token Free / 本地优先 / 社会力） |
| `communityAI/article-01-orra-manifesto.md` | iDoris 对外宣传文案基础 |
| `communityAI/article-02-social-force.md` | iDoris 哲学基础（人类不可替代的三个维度） |

### 11.2 需要新做的事

- 本文档（`iDoris-master-plan.md`）✅ 当前
- `iDoris-tech-stack-detail.md`（每个组件的具体配置 + 代码片段）
- `iDoris-privacy-protocol.md`（隐私协议正式版，含数学证明）
- `iDoris-training-recipes/`（每个层级的训练脚本）
- `iDoris-launch-license.md`（License 详细版，与 launch.mushroom.cv 对应）

### 11.3 目录合并计划

```
research/
├── iDoris/                           ← 主要工作目录（当前 + 未来）
│   ├── iDoris-master-plan.md         ← 本文档 ⭐
│   ├── iDoris-tech-stack-detail.md   ← 待写
│   ├── iDoris-privacy-protocol.md    ← 待写
│   ├── iDoris-training-recipes/      ← 待写
│   └── legacy/                        ← 历史文档归档
│       ├── communityAI/              ← 整体迁移
│       └── local-AI/                 ← 整体迁移
```

**迁移命令**（待执行）：
```bash
mkdir -p research/iDoris/legacy
git mv research/communityAI research/iDoris/legacy/communityAI
git mv research/local-AI research/iDoris/legacy/local-AI
```

---

## 12. 4 个关键决策记录（本次对话沉淀）

### 决策 1：基座模型 = Qwen3.5/3.6 全家族

- **决策日期**：2026-04-27
- **决策人**：创始人（Doris 老公）
- **背景**：早期讨论用 Qwen2.5，被指出已过时
- **现状**：Qwen3.6 (2026-04) 是当前最新，Qwen3.5 全家族（0.8B-122B）在 2026-02-03 完整发布
- **决策**：iDoris 用 Qwen3.5/3.6 同家族，跨 Mobile/PC/Community/City 四个层级
- **DeepSeek 评估**：DeepSeek V4 Flash 太大（284B/13B 激活）不适合 MVP；DeepSeek-R1-Distill-Qwen-1.5B 作为 Mobile 强推理备选
- **重新评估时点**：每 6 个月评估一次基座升级（如 Qwen 4.0 出来时）

### 决策 2：iDoris vs Sin90 是两层关系

- **决策日期**：2026-04-27
- **决策**：
  - iDoris = 后端核心模型层
  - Sin90 / Cos72 / CityOS = 前台应用层
  - **不再混用，分别命名**
- **类比**：iOS / Apple Foundation Models
- **影响**：所有未来文档统一使用此命名约定

### 决策 3：隐私底线 = "权重可上传，原始数据不出本机"

- **决策日期**：2026-04-27
- **创始人立场**（直引）：
  > "权重不是直接隐私数据，是基于隐私数据+算法的计算结果，开算法开源+AI 评估无陷阱、后门、漏洞后，权重经过用户授权，可以提供给上游训练。"
- **决策**：
  - 原始数据：**绝对不离开本机**（任何情况）
  - LoRA 权重 delta：**经三层验证后可上传**（算法开源 + AI 审计 + DP-SGD + 用户主题级授权）
- **学术对应**：DP-FedAvg + Algorithm Auditing
- **实施**：iDoris-Audit-Bot + Opacus + Sin90 数据贡献中心 GUI

### 决策 4：MVP 目标 = Mac Studio 64GB（自用 + 你 = 第一用户）

- **决策日期**：2026-04-27
- **创始人立场**：MVP 目标 Mac Studio 64GB，或租云 GPU 备选
- **决策**：
  - Phase 1 在 Mac Studio 上跑通 Qwen3.5-9B + LoRA + RAG + DPO
  - 第一个用户 = 创始人本人（用自己的笔记/博客/聊天记录冷启动）
  - 验证标准：1 个月使用后，"懂我的程度" > Claude/ChatGPT
- **后备**：如 Mac Studio 不到位，租 Lambda Labs / Modal Labs A100 spot，月成本约 ¥1500-3000

### 决策 5（隐含）：社区 = 节点运营组织

- **决策日期**：2026-04-27
- **创始人立场**（直引）：
  > "社区是独立运行自己 iDoris 节点的组织，是 AI 角度的社区，无需许可加入 Mycelium Protocol，免费使用我们训练的模型和流程，来二次训练自己的社区 AI 并运行；任何中小组织，非商业或者中小商业，都可以使用（不同 license，具体看 launch.mushroom.cv）。"
- **决策**：
  - 社区不是地理概念，是 AI 网络节点
  - 无许可加入 Mycelium Protocol
  - 免费使用 + 自行二次训练
  - License 分非商业 / 中小商业，详见 launch.mushroom.cv

---

## 13. 下一步（Next Actions）

### 立刻可做（本周）

- [x] **A1**：本文档（`iDoris-master-plan.md`）✅ 已完成 v0.1
- [x] **A2**：把 `communityAI/` 和 `local-AI/` 迁移到 `research/iDoris/legacy/`（git mv）✅ 已完成
- [x] **A3**：update vision.md 中 CN90/Cosine72/CTOS → Sin90/Cos72/CityOS（命名修正）✅ 已完成
- [ ] **A4**：在 launch.mushroom.cv 上发 iDoris 立项预告

### 本月（M1 启动）

- [ ] **B1**：Mac Studio 64GB 到位 / 租云方案备选
- [ ] **B2**：MLX-LM + Unsloth 环境装好，Qwen3.5-9B 跑通推理
- [ ] **B3**：写 Sin90 数据导入脚本（Obsidian + 博客 + 微信）
- [ ] **B4**：第一次 LoRA 训练（100-500 条样本验证流程）

### 下月（M2 数据 + 隐私层）

- [ ] **C1**：集成 Presidio 中文 PII 脱敏
- [ ] **C2**：Sin90 GUI v0（数据贡献中心 + 聊天 + 反馈按钮）
- [ ] **C3**：本地数据库 schema 落地

---

## 14. 待补充章节（v0.2+）

- [ ] §A. 详细的隐私数学证明（DP-SGD ε-δ 论证）
- [ ] §B. iDoris-Audit-Bot 设计文档
- [ ] §C. SLoRA / FedIT 算法选择实验
- [ ] §D. RAG vs LoRA vs DPO 三者协同的具体配方（哪些信息进哪一层）
- [ ] §E. 中文社区 vs 全球社区的本地化策略
- [ ] §F. License 详细文本（Mycelium Public License v1）
- [ ] §G. 与现有开源生态（HuggingFace / Ollama / LangChain）的集成路径

---

## 附录 A：本次对话核心决策记录（2026-04-27）

> 记录 2026-04-27 创始人与 Aura AI 助手就 iDoris 立项的核心对话决策，作为后续文档的事实源。

### A.1 命名修正

- 早期对话中出现的 ~~CN90~~ ~~Cosine72~~ ~~CTOS~~ 是语音识别错误
- 正确命名：**Sin90**（个人）/ **Cos72**（社区）/ **CityOS**（城市）
- iDoris 是核心模型层命名，Sin90 等是前台应用层命名

### A.2 iDoris 命名解读

- 表面学习苹果 i 系列前缀
- 实际：i = 中文"爱"（love），Doris = 创始人爱人英文名
- 含义：用爱构建的本地 AI

### A.3 基座模型选型

- 旧建议（Qwen2.5）已过时，更新为 Qwen3.5/3.6 全家族
- DeepSeek V4（Flash/Pro）2026-04 刚发布，但太大不适合 MVP
- DeepSeek-R1-Distill-Qwen-1.5B 作为 Mobile 强推理备选

### A.4 隐私立场（重要哲学决策）

> "权重不是直接隐私数据，是基于隐私数据+算法的计算结果，开算法开源+AI 评估无陷阱、后门、漏洞后，权重经过用户授权，可以提供给上游训练。"

- 原始数据绝对不出本机
- LoRA 权重经审计 + 授权后可上传
- 解锁了 Federated LoRA 路线

### A.5 社区定义

> "社区是独立运行自己 iDoris 节点的组织，是 AI 角度的社区，无需许可加入 Mycelium Protocol。"

- 社区 = AI 网络节点 ≠ 地理社区
- 免许可、免费用
- License 详见 launch.mushroom.cv

### A.6 MVP 资源

- 目标硬件：Mac Studio 64GB
- 备选：租云 GPU（Lambda / Modal）
- 第一用户：创始人本人

### A.7 渐进路径（一条线）

- Phase 1 (M1-M3)：Personal-PC MVP（创始人自用）
- Phase 2 (M4-M5)：Personal-Mobile 蒸馏
- Phase 3 (M6-M9)：Community 试点
- Phase 4 (M10-M18)：City 概念验证

---

## 附录 B：参考资料 (Sources)

### 模型与基座

- [QwenLM/Qwen3 GitHub](https://github.com/QwenLM/Qwen3)
- [QwenLM/Qwen3.6 GitHub](https://github.com/QwenLM/Qwen3.6)
- [Qwen 系列 Wikipedia](https://en.wikipedia.org/wiki/Qwen)
- [Qwen3 官方博客](https://qwenlm.github.io/blog/qwen3/)
- [Qwen 3: The new open standard – Nathan Lambert](https://www.interconnects.ai/p/qwen-3-the-new-open-standard)
- [DeepSeek Official Models 2026](https://deepseekv4.network/models)
- [DeepSeek V4 Flash on HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)
- [DeepSeek V4 Pro on HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)
- [TechCrunch: DeepSeek V4 frontier preview](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/)
- [BentoML: Complete Guide to DeepSeek Models](https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond)
- [Simon Willison: DeepSeek V4 frontier-fraction-price](https://simonwillison.net/2026/Apr/24/deepseek-v4/)
- [Artificial Analysis: DeepSeek V4 Pro & Flash](https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash)
- [Run DeepSeek V4 Flash Locally Guide](https://ghost.codersera.com/blog/run-deepseek-v4-flash-locally-full-2026-setup-guide/)

### Mac Studio + LoRA

- [The Hitchhiker's Guide to Fine-Tune LLMs on a Mac (Medium)](https://medium.com/@neevdeb26/the-hitchhikers-guide-to-fine-tune-llms-on-a-mac-85174455457a)
- [ARahim3/mlx-tune GitHub](https://github.com/ARahim3/mlx-tune)
- [Run and Fine-Tune LLMs on Mac with MLX-LM 2026](https://markaicode.com/run-fine-tune-llms-mac-mlx-lm/)
- [MLX Apple Silicon AI Dev Stack](https://www.buildmvpfast.com/blog/mlx-apple-silicon-ai-development-mac-fine-tune-llm-2026)
- [Best LLM for Mac in 2026 (M1-M4 Guide)](https://willitrunai.com/blog/best-llm-for-mac-apple-silicon-2026)
- [Fine-Tuning Open Source LLMs with LoRA / QLoRA (DASRoot 2026)](https://dasroot.net/posts/2026/04/fine-tuning-open-source-llms-lora-qlora/)
- [Unsloth Studio: No-Code LLM Fine-Tuning](https://alchemictechnology.com/blog/posts/unsloth-studio-local-llm-fine-tuning.html)
- [LoRA Fine-Tuning On Apple Silicon MacBook (Towards Data Science)](https://towardsdatascience.com/lora-fine-tuning-on-your-apple-silicon-macbook-432c7dab614a/)

### 开源 LLM 生态

- [Best Open-Source LLMs in 2026 (BentoML)](https://www.bentoml.com/blog/navigating-the-world-of-open-source-large-language-models)
- [Best Open Source LLM 2026 Ranking (whatllm.org)](https://whatllm.org/best-open-source-llm)
- [Top 5 Local LLM Tools and Models in 2026 (Pinggy)](https://pinggy.io/blog/top_5_local_llm_tools_and_models/)
- [Open Source LLM Leaderboard 2026 (Onyx)](https://onyx.app/open-llm-leaderboard)
- [Self-Hosted LLM Leaderboard 2026 (Onyx)](https://onyx.app/self-hosted-llm-leaderboard)
- [Top 7 Open Source LLMs for 2026 (Instaclustr)](https://www.instaclustr.com/education/open-source-ai/top-7-open-source-llms-for-2026/)
- [Best Open Source LLMs Guide (Contabo)](https://contabo.com/blog/open-source-llms/)
- [Which Local LLM Is Better? Benchmarked 2026 (Medium)](https://medium.com/@likhitkumarvp/which-local-llm-is-better-a-deep-dive-into-open-source-ai-models-in-2026-benchmarked-b786d6e13384)

### Qwen / DeepSeek / Ollama 索引

- [Qwen Collections on HuggingFace](https://huggingface.co/Qwen/collections)
- [Ollama qwen3 library](https://ollama.com/library/qwen3)
- [Ollama qwen2.5-coder library](https://ollama.com/library/qwen2.5-coder)
- [Ollama Library Index](https://ollama.com/library)
- [Docker ai/qwen3 Image](https://hub.docker.com/r/ai/qwen3)
- [DeepSeek API on OpenRouter](https://openrouter.ai/deepseek)
- [DeepSeek V4 Flash vs Pro (InsiderLLM)](https://insiderllm.com/guides/deepseek-v4-flash-vs-pro-guide/)

### Aura AI 内部研究（已纳入 legacy）

- `research/iDoris/legacy/communityAI/vision.md` — 三大愿景 + 社会力 + 三产品体系
- `research/iDoris/legacy/communityAI/plan.md` — Aura AI 4 阶段建设计划
- `research/iDoris/legacy/communityAI/raw-notes.md` — 创始人原始口述记录
- `research/iDoris/legacy/communityAI/article-01-orra-manifesto.md` — Aura AI 宣言
- `research/iDoris/legacy/communityAI/article-02-social-force.md` — 社会力理论
- `research/iDoris/legacy/local-AI/reports/R01-hardware-china-market.md` — 硬件方案
- `research/iDoris/legacy/local-AI/reports/R02-models-by-domain.md` — 模型矩阵
- `research/iDoris/legacy/local-AI/reports/R03-software-by-role.md` — 软件清单
- `research/iDoris/legacy/local-AI/reports/R04-smb-human-ai-roles.md` — 中小组织实施手册

---

*本文档为 iDoris 项目的单一事实源（Single Source of Truth）。每次重大决策后更新。*
*v0.1 · 2026-04-27 · Aura AI · Mycelium Protocol*
