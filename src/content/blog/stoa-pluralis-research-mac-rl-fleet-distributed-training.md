---
title: "14 台 Mac 跨越四国做 RL 后训练：Pluralis Research 的 stoa 实验"
titleEn: "14 Macs Across Four Countries Do RL Post-Training: Pluralis Research's stoa Experiment"
description: "Pluralis Research 开源 stoa：把 RL 后训练的 rollout 生成和梯度更新彻底解耦——巴黎/苏黎世/都柏林/多伦多的 14 台 Mac 用 MLX 生成经验，一张 B200 负责学习，双方只通过 Cloudflare R2 bucket 见面。8B MoE 模型在论文搜索问答任务上 pass@1 从 0.29 涨到 0.63。"
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["分布式训练", "RL后训练", "Apple Silicon", "MLX", "MoE", "GRPO", "去中心化AI", "Pluralis Research", "开源", "B200"]
heroImage: "../../assets/images/stoa-pluralis-research-mac-rl-fleet-distributed-training-banner.jpg"
---

> **GitHub**：[PluralisResearch/stoa](https://github.com/PluralisResearch/stoa) · **Stars**：6  
> **机构**：Pluralis Research · **作者**：Erfan Miahi  
> **许可**：MIT · **状态**：Proof of concept（生产级版本开发中）  
> **配套博文**："RL Post-Training on Macs", Pluralis Research Blog, July 2026

---

## 这个实验在做什么

RL 后训练（RLVR / GRPO 这条路）是现在提升推理模型能力最有效的方法之一，但有个问题：**生成 rollout 是整个流程里最消耗资源的部分**——模型要不断做题、搜索、生成答案，这个过程完全是推理，不涉及梯度，但你必须有 GPU 才能跑。

Pluralis Research 的做法是：**把"生成经验"和"从经验学习"彻底分开**。

- 巴黎、苏黎世、都柏林、多伦多的 14 台 Apple Silicon Mac（其中一台是研究员自己在用的 MacBook）—— 用 MLX 不停跑模型，生成 rollout，上传到 Cloudflare R2。
- 数据中心里的一张 NVIDIA B200 —— 从 R2 拉 rollout，跑 GRPO 梯度更新，把新权重的 delta 发回 R2。

**两侧唯一的共享层是 R2 bucket。** Mac 不知道 GPU 在哪，GPU 不知道 Mac 在哪。任何一台 Mac 中途掉线，trainer 继续用已经到的 rollout 学习。

---

## 参考实验结果

**模型**：LFM2.5-8B-A1B（Liquid AI 的 MoE 模型，8.3B 总参数，每个 token 只激活约 1B）  
**任务**：PaperSearchQA（PSQA）——给定问题，搜索论文，回答并引用原文  
**硬件**：14 台 Apple Silicon Mac + 1 张 B200

| 指标 | 训练前 | 训练后 |
|---|---|---|
| cover-EM pass@1 | 0.29 | **0.63** |
| cover-EM pass@8 | — | **~0.83** |
| 搜索率 | 0.22 | **0.85** |

搜索率从 0.22 涨到 0.85 说明：模型不只是学会了怎么回答，而是学会了**主动去找答案**。pass@1 从 0.29 到 0.63，翻了一倍多。

---

## 系统架构：解耦的核心设计

```
Mac Worker (MLX)          Cloudflare R2          GPU Trainer (slime/Megatron)
     │                         │                          │
     ├── 生成 rollout ──────>  rollouts/          ←──── 拉 rollout
     │   (做题/搜索/生成)       (不可变记录)               │
     │                         │                    跑 GRPO 步
     ├── 轮询版本指针 <──────  current.json        ────> │
     │                         │                          │
     └── 拉 PULSE delta <────  versions/PULSE    <──── 发布权重 delta
```

### R2 目录结构

```
<run>/
  rollouts/        ← 每个 worker 的不可变 rollout 记录
  current.json     ← 当前版本指针（trainer 每步更新）
  anchors/         ← 完整权重 checkpoint
  versions/        ← 各版本的 PULSE 稀疏 delta
```

Worker 轮询 `current.json`，只在版本号推进时拉 delta。新加入的 Mac 拉最近的 anchor + 自那以后的所有 delta，重建当前权重，开始生产 rollout。

---

## 三个关键技术决策

### 1. PULSE — 稀疏无损权重 delta

全量 8B 模型权重每步都传一次是不现实的。PULSE 只传 anchor checkpoint 之间的**稀疏增量**（sparse-lossless delta）：

- Anchor：每隔若干步存一次完整权重
- Delta：两个 anchor 之间的稀疏差分，体积小得多
- Worker 重建路径：最近的 anchor + 后续所有 delta

这让 Mac 拉取新权重的网络开销可以接受，即使跨洲也能跑。

### 2. DPPO Gate — 离策略矫正

Mac 生成 rollout 时用的是当时的权重版本，等 rollout 上传到 trainer 时，权重可能已经更新了几步——这就是"离策略"问题（off-policy）。

`trainer/dppo_gate.py` 实现了 DPPO（Decoupled PPO）矫正门控：trainer 在做 PPO 步之前，先用 worker 记录的 logprob 做重要性采样矫正，过滤掉陈旧度超过阈值的 rollout，再做 dual-clip PPO 更新。

这是让异步多 worker 训练不发散的核心机制。

### 3. Staleness 过滤 + Rollout 复用

Trainer 对每批 rollout 做两层过滤：

- **陈旧度过滤**：与当前权重版本差距太大的 rollout 被丢弃
- **复用过滤**：同一个问题如果已经有足够多的 rollout，不再重复消耗

这让 Mac 舰队的利用率和 trainer 的学习效率之间保持平衡。

---

## 快速上手

### 需要什么

- 每台 Mac：`uv`（Python 包管理），Apple Silicon（任意型号）
- Cloudflare R2 bucket + S3 token（免费套餐够用）
- 至少一张 CUDA GPU（A100/H100 跑 1.5B quickstart，B200 跑 8B 参考实验）

### Mac 端测试（不需要 GPU）

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# clone 并安装依赖
git clone https://github.com/PluralisResearch/stoa
cd stoa
uv sync --extra worker --extra data

# 配置 R2
cp .r2env.example ~/.r2env && chmod 600 ~/.r2env
$EDITOR ~/.r2env   # 填入 bucket / access_key / secret_key

# 本地端到端测试（2组，4个样本，128 token）
uv run python worker/run_local_e2e.py 2 4 128
```

这一步跑 Qwen2.5-1.5B 做 GSM8K rollout，验证 R2 读写，不需要 trainer GPU。

### 完整运行（trainer + Mac fleet）

```bash
# Trainer 端（slime/Megatron 容器）
DRL_RUN=my-gsm8k DRL_PULSE_PLANE=bf16 bash envs/gsm8k/run_qwen25_gsm8k_decoupled.sh

# 每台 Mac
DRL_RUN=my-gsm8k DRL_PULSE_PLANE=bf16 bash worker/run_dRL_worker_gsm8k.sh
```

两端用同一个 `DRL_RUN` 名和 R2 bucket，Mac 就自动接入 fleet。可以随时多起几台或关掉几台。

### 复现参考实验（8B PaperSearchQA）

完整配方在 [`runs/psqa-decoupled/REPRODUCE.md`](https://github.com/PluralisResearch/stoa/blob/main/runs/psqa-decoupled/REPRODUCE.md)。LFM2 slime 插件在仓库里，trainer 用公开的 slime base，可以重跑曲线（但因为离策略 RL 有随机性，exact checkpoint 不可复现）。

### 可以租 Mac

如果没有 14 台 Mac，可以租：
- [Scaleway](https://www.scaleway.com/)
- [Flow Swiss](https://flow.swiss/)
- [AWS EC2 Mac](https://aws.amazon.com/ec2/instance-types/mac/)（最少 24 小时独占主机）

---

## 为什么这个实验有意义

### 打破"RL = 需要很多 GPU"的假设

这个实验的核心结论是：**RL 后训练里最大量的计算（生成 rollout）不需要 GPU**。Apple Silicon Mac 用 MLX 做推理的效率足够高，可以成为有效的 rollout 生产者。

真正需要 GPU 的部分——梯度更新——集中到一张高端卡（B200）上做。这张卡大部分时间在做有效的学习，不用自己跑推理。

### 异步解耦是可行的

14 台 Mac 不同步，不等待彼此，随时可以掉线——trainer 不 care，继续消费已经到的 rollout。这个"无协调"的设计大幅降低了运维复杂度。

### 跨洲延迟可以接受

巴黎到都柏林到多伦多，跨越大西洋，网络延迟不低。但 PULSE delta 压缩 + R2 作为中间层，让权重传输的带宽开销降到可接受范围。Rollout 上传是异步的，不阻塞任何人。

---

## Pluralis Research 的其他相关项目

| 项目 | Stars | 描述 |
|---|---|---|
| **node0** | 96 | Protocol Learning 去中心化预训练活动，用户贡献计算力协同训练 7.5B 模型 |
| **agora** | 29 | Collaborative training library |
| **AsyncPP** | 23 | 异步流水线并行优化 |
| **AsyncMesh** | 4 | AsyncMesh 实现 |

stoa 是这个体系里专注于 RL 后训练的组件，node0 更偏向预训练阶段的去中心化协作。

---

## 技术局限与当前状态

README 明确标注：**Proof of concept，未做生产加固**。

几个实际限制：
- 当前适配器只验证了 GSM8K 和 PaperSearchQA 两个任务
- Trainer 必须在 `/root/dRL` 目录（脚本硬编码路径）
- Mac 端依赖 MLX，只支持 Apple Silicon
- B200 GPU 用于参考实验，更低端的 GPU 也支持但未系统测试

生产级版本承诺发布，但时间未定。

---

## 核心判断

这个实验的价值不在于"14 台 Mac 比 GPU 便宜"（它们不一定更便宜），而在于证明了一个架构可能性：**RL 训练的计算可以在异构、分散、可靠性低的硬件上分布运行**，只要解耦设计得好。

PULSE delta + Cloudflare R2 + staleness 过滤这三件事组合在一起，构成了一个不需要中央协调的分布式训练基础设施雏形。

如果这个架构成熟化，意味着：手头有几台 Mac 的个人研究者，可以参与 8B 级别模型的 RL 后训练实验，不再需要申请 GPU 集群资源。这个门槛的降低本身就值得关注。

---

## 参考资源

- **stoa**：[PluralisResearch/stoa](https://github.com/PluralisResearch/stoa)
- **复现指南**：[runs/psqa-decoupled/REPRODUCE.md](https://github.com/PluralisResearch/stoa/blob/main/runs/psqa-decoupled/REPRODUCE.md)
- **MLX**：[ml-explore/mlx](https://github.com/ml-explore/mlx)
- **slime**：[THUDM/slime](https://github.com/THUDM/slime)
- **GRPO**：DeepSeekMath，[arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)
- **DPPO**：Qi et al., [arxiv.org/abs/2602.04879](https://arxiv.org/abs/2602.04879)
- **LFM2.5-8B-A1B**：Liquid AI Foundation Model

© 2026 Author: Mycelium Protocol
