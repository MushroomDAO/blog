---
title: "StartLux Decision 拆解：不生成文字，只输出概率——打遍游戏的决策模型族"
titleEn: "StartLux Decision Teardown: No Generation, Just Probabilities — The Decision Model Family That Plays Games"
description: "StartLuxLabs/Startlux-Decision，Apache-2.0，Python，51 stars。一组专用决策模型：0.8B 到 35B-A3B 六个尺寸，不生成文字，只从一次前向传播的 logit 读出每个选项的概率。Decision Index 0.2.1 得 63.88，超过 Jev 1.13 的 57.91。兼容 TypeSafe /v1/systemone 格式。GGUF 全量支持 llama.cpp 本地部署。"
descriptionEn: "StartLuxLabs/Startlux-Decision, Apache-2.0, Python, 51 stars. A family of typed decision models from 0.8B to 35B-A3B: no text generation — just probabilities read from logits after a single forward pass. Decision Index 0.2.1 score: 63.88, above Jev 1.13's 57.91. Compatible with TypeSafe /v1/systemone. GGUF variants for llama.cpp local deployment."
pubDate: 2026-10-03
heroImage: "../../assets/images/startlux-decision-typed-decision-model-jev-compatible-games-demo-banner.jpg"
category: "Tech-Experiment"
tags: ["决策模型", "Jev兼容", "开源拆解", "GGUF", "本地AI", "概率推理"]
lang: "zh-CN"
wechatTitle: "StartLux Decision：打遍游戏的概率决策模型"
wechatDigest: "六档0.8B-27B；一次前向出概率；DI 63.88超Jev 57.91；Mario/SC2/Doom打通"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 一句话定位

给它一个状态和一组选项，它返回每个选项的概率——没有文字输出，没有生成过程，答案直接从一次前向传播的 logit 里读出来。

**仓库**：github.com/StartLuxLabs/Startlux-Decision  
**协议**：Apache-2.0  
**Stars**：51（2026-09-29 创建，非常新）  
**HuggingFace**：huggingface.co/collections/startlux-models/startlux-decision-6abba92b301b573fa154d493  
**模型规格**：0.8B / 2B / 4B / 9B / 27B（dense） + 35B-A3B（MoE）

---

## 核心机制：不生成，只选

普通 LLM 的做法：给定问题，decode 出答案文字，再从文字里解析出选项。

StartLux Decision 的做法：给定状态 + 选项集合，直接在选项字母（A/B/C/D）的 logit 位置上读概率，做一次前向传播就结束。

```
输入：  state = "棋盘当前局面"
        questions = ["选择下一步：A.e4 B.d4 C.Nf3 ..."]

输出：  A: 38.2%  B: 27.1%  C: 19.4%  D: 15.3%
```

**结果**：
- 速度极快——StartLux-Decision-0.8B 在单张 H200 上为 **12.2 ms**（三个问题合并一次前向）
- 概率可以直接用作置信度，而不只是一个离散答案
- 不需要解析输出字符串，API 层没有"生成失败"的情况

**接口**：使用 TypeSafe `/v1/systemone` 格式——为 Jev 写的客户端代码无需修改即可接入。

---

## 六个尺寸

| 模型 | JevBench (231题) | DI 0.2.1 | 延迟 (H200) | GGUF Q4_K_M |
|------|-----------------|---------|------------|-------------|
| 0.8B | 179/231 (77.5%) | 38.86 | **12.2 ms** | 0.53 GB |
| 2B   | 196/231 (84.8%) | 44.19 | 15.5 ms | 1.27 GB |
| 4B   | 204/231 (88.3%) | 52.75 | 26.0 ms | 2.71 GB |
| 9B   | 201/231 (87.0%) | 58.63 | 35.7 ms | 5.63 GB |
| 27B  | 208/231 (90.1%) | **63.88** | 102.3 ms | 16.55 GB |
| 35B-A3B (MoE) | 210/231 (**90.9%**) | 61.55 | 52.5 ms | 暂无 |

35B-A3B 是 MoE，每个 token 激活约 3B 参数，速度比 27B dense 快一半（52.5 ms vs 102.3 ms），且只需一张 80GB GPU（峰值约 71 GiB）。快速线性注意力内核（flash-linear-attention、causal-conv1d）是必须项，缺少时服务器拒绝启动。

---

## 游戏演示：为什么用游戏测决策模型

游戏天然具备决策模型需要的所有特性：
- 每一步都是「从有限选项中选一个」
- 有明确的输赢判定，不依赖人工评分
- 覆盖不同的时间尺度（实时反应、战略规划）和信息密度

六个游戏全部是 StartLux-Decision-27B 的真实运行录像：

**电脑操控（计算机使用）**  
真实 Chrome 打开模拟电商，每步两个问题：页面上哪个控件是下一步操作对象、任务是否完成。模型从不输出文字——点击文本框只会打开它的建议列表。任务：找最便宜的 AA 8 节装含免费配送，下单到指定地址，完成。

**国际象棋（对阵 Jev 1.13）**  
每轮一个问题，选项是当前所有合法棋步，模型只看棋盘文字描述和步骤历史。256 局比赛（每个开局颜色各一次），StartLux-Decision-27B 得分 58.4%，+59 Elo（置信区间 +37 到 +82）；85 局决出胜负中赢了 64 局。

**超级马里奥兄弟（1-1 关卡）**  
每步 11 种行动选择。Harness 把每种行动在模拟器里预跑一步，把结果（进度、Mario 是否存活）用文字描述给模型。模型只读这些描述，选出一步，最终通过 1-1 关。

**星际争霸 II（对阵 Hard AI）**  
每 12 秒游戏时间一次请求，三个问题：下一步造什么、优先攻击什么单位、进攻还是防守还是采矿。战术执行（工人调度、单位控制）由脚本 bot 负责，模型只做战略决策。最终打败内置 Hard AI。

**Doom 死亡竞技**  
每 4 个游戏帧一次请求，三个问题：攻击哪个敌人、是否开火、如何移动。游戏状态是引擎生成的文字描述，模型从不看视频帧。

**JevBall（足球）**  
球场附近的每个球员各一次请求，每个请求最多 14 种行动选择（传球、射门、带球、逼抢等）。游戏不等待模型——物理和移动由游戏自己处理，超时自动用内置策略兜底。

---

## Decision Index 0.2.1 结果

Decision Index（DI）是 38 个分类/选择基准的加权均值，每个基准按"高于随机猜测多少"归一化。

| 系统 | DI 0.2.1 | 知识推理 | 语言理解 | 检索分类 | 工具自动化 |
|------|---------|---------|---------|---------|---------|
| StartLux-Decision-27B | **63.88** | 44.3 | **74.5** | **66.8** | **82.2** |
| StartLux-Decision-35B-A3B | 61.55 | 42.4 | 73.6 | 65.8 | 76.2 |
| StartLux-Decision-9B | 58.63 | 38.0 | 71.3 | 64.1 | 73.2 |
| **Jev 1.13**（当前公榜最高） | 57.91 | **51.4** | 62.0 | 55.4 | 75.1 |
| StartLux-Decision-4B | 52.75 | 32.1 | 63.9 | 56.7 | 72.3 |

StartLux-Decision-27B 在 38 个基准中 31 个超过 Jev 1.13，落后的主要在知识推理类（GPQA Diamond、BBH、MMLU-Pro 等）——这类题通常需要大量知识广度，而决策模型专注的是结构化选择任务。

**注意**：这些跑分是 StartLuxLabs 自己提交的，尚未进入 DI 公榜，原话是"our runs are not on the board"。训练数据包含 38 个基准中 14 个的公开训练集（已标注 †），对应基准的测试题已过滤掉。

---

## 本地部署：GGUF + llama.cpp

每个 dense 尺寸都有 BF16、Q8_0、Q4_K_M 三种 GGUF。量化保真度：

- **BF16**：等同原始权重（99-100% 相同答案）
- **Q8_0**：接近无损（99-100% 相同）
- **Q4_K_M**：4B 以上 96-98% 保真；0.8B 和 2B 损失更大，建议用 Q8_0

本地跑 4B Q8_0 的命令：

```bash
hf download startlux-models/StartLux-Decision-4B-Q8_0-GGUF --local-dir StartLux-Decision-4B-Q8_0-GGUF
cd StartLux-Decision-4B-Q8_0-GGUF && pip install -r requirements.txt
llama-server -m StartLux-Decision-4B-Q8_0.gguf -ngl 99 -c 16384 --parallel 4 --port 8081 &
python -m startlux_decision.gguf_server --model-dir . --llama http://127.0.0.1:8081 --port 8090
```

决策逻辑不在模型权重里，在 `startlux_decision.gguf_server` 里——这意味着 llama.cpp 运行权重，Python 层处理 TypeSafe 协议和 logit 读取。

**35B-A3B 目前没有 GGUF**，只有原始权重（需要 80GB VRAM）。

---

## 需要知道的限制

**知识广度不是强项**。在 GPQA Diamond（71.4% vs 34.0%）、BBH（89.7% vs 71.3%）、MMLU-Pro（80.5% vs 66.0%）上，Jev 1.13 明显领先。StartLux Decision 专为结构化选择任务优化，不是通用知识模型。

**自报基准，未上公榜**。DI 0.2.1 的 63.88 是 StartLuxLabs 自己的跑分，未经 DI 官方验证，不在公开排行榜上。

**快速线性注意力内核是硬依赖**。没有 flash-linear-attention 和 causal-conv1d，服务器拒绝启动。这在消费级 GPU 上可能有兼容性问题。

**35B-A3B 暂无 GGUF**。需要单张 80GB 专业 GPU，家用设备无法本地运行最大模型。

**项目极新**。2026-09-29 创建，51 stars，社区反馈和实际部署案例极少，生产可靠性未知。

---

## 关键数字

| 字段 | 值 |
|------|----|
| 仓库 | StartLuxLabs/Startlux-Decision |
| 协议 | Apache-2.0 |
| 创建 | 2026-09-29（极新） |
| Stars | 51 |
| 模型尺寸 | 0.8B / 2B / 4B / 9B / 27B / 35B-A3B |
| 最小本地部署 | 0.8B Q4_K_M = **0.53 GB** |
| 最快响应 | 0.8B on H200 = **12.2 ms**（3题合并） |
| DI 0.2.1（自报） | 27B: 63.88 / Jev: 57.91 |
| API 格式 | TypeSafe /v1/systemone（Jev 兼容） |

---

## 综合判断

StartLux Decision 的思路清晰：决策场景不需要语言生成能力，直接在 logit 层读概率既快又精确。这条路已经有 Jev 和 SemIf 等在走，StartLux 的差异点是规模（六个尺寸全覆盖）和游戏演示的说服力——用真实的 Mario、SC2、Doom 运行录像来展示"决策模型能做什么"，比 benchmark 数字更直观。

项目极新（5天），51 stars，自报基准未上公榜——这些都是需要时间验证的不确定性。GGUF 支持和 llama.cpp 兼容性是实际落地的加分点：0.53 GB 的 Q4_K_M 意味着 0.8B 模型可以在几乎所有设备上本地跑。

Apache-2.0 协议，商用无限制。

---

> 开源仅供学习，Apache-2.0 协议，商业使用无限制。

---

<!--EN-->

## StartLux Decision Teardown: Probabilities, Not Generation

> **Open source for learning only**: All projects discussed are from public repositories.

---

### One-Line Summary

Give it a state and a set of options; it returns a probability for each option — no text output, no generation loop, the answer is read directly from logits after a single forward pass.

**Repo**: github.com/StartLuxLabs/Startlux-Decision  
**License**: Apache-2.0  
**Stars**: 51 (created 2026-09-29, very new)  
**Models**: 0.8B / 2B / 4B / 9B / 27B (dense) + 35B-A3B (MoE)

---

### Core Mechanism: Select, Don't Generate

Standard LLM approach: decode answer text from the question, parse the chosen option from the output string.

StartLux Decision approach: given a state and option set, read probabilities directly from the logit positions of the option letters (A/B/C/D) — one forward pass, done.

**Results**:
- Very fast — StartLux-Decision-0.8B: **12.2 ms** per request (3 questions in one forward pass) on a single H200
- Probabilities usable directly as confidence scores, not just a discrete answer
- No output parsing, no "generation failure" at the API layer

**Interface**: TypeSafe `/v1/systemone` format — clients written for Jev work unchanged.

---

### Six Sizes

| Model | JevBench (231 items) | DI 0.2.1 | Latency (H200) | Q4_K_M GGUF |
|-------|---------------------|---------|----------------|-------------|
| 0.8B | 179/231 | 38.86 | **12.2 ms** | 0.53 GB |
| 2B   | 196/231 | 44.19 | 15.5 ms | 1.27 GB |
| 4B   | 204/231 | 52.75 | 26.0 ms | 2.71 GB |
| 9B   | 201/231 | 58.63 | 35.7 ms | 5.63 GB |
| 27B  | 208/231 | **63.88** | 102.3 ms | 16.55 GB |
| 35B-A3B (MoE) | **210/231** | 61.55 | 52.5 ms | not yet |

The 35B-A3B is MoE with ~3B active parameters per token, half the latency of the 27B dense model, fitting in one 80GB GPU (~71 GiB peak). Flash-linear-attention and causal-conv1d kernels are hard requirements — the server refuses to start without them.

---

### Game Demos: Why Games?

Games naturally have everything a decision model needs: every step is "pick one from a finite option set," outcomes are unambiguous, and they span different time scales and information densities. All six are real runs of StartLux-Decision-27B:

**Computer Use**: Real Chrome opens a mock store. Two questions per step: which visible control to use next, and whether the task is done. The model never types text. Task: find the cheapest 8-pack AA batteries with free delivery and order to the right address. Completed.

**Chess vs. Jev 1.13**: One question per turn — choose from all legal moves, given board and move history in text. 256 games; StartLux-Decision-27B scores 58.4%, +59 Elo (interval +37 to +82), wins 64 of 85 decisive games.

**Super Mario Bros. (World 1-1)**: 11 actions per step. The harness plays each action one step ahead in the emulator and describes the outcome; the model reads only those descriptions. Cleared World 1-1.

**StarCraft II vs. Hard AI**: One request every 12 game-seconds: what to build, which units to prioritize, attack/defend/gather. A scripted bot executes the choices. Beat the Hard AI.

**Doom Deathmatch**: Three questions every 4 game tics — which enemy to target, whether to fire, how to move. State is text from the game engine; the model never sees video frames.

**JevBall (football)**: One request per player near the play, up to 14 actions each. The game doesn't wait for the model — physics and distant players are handled by the built-in policy.

---

### Decision Index 0.2.1

DI is a weighted mean of 38 classification/choice benchmarks, each normalized to "how much better than random guessing."

StartLux-Decision-27B reaches **63.88**, above Jev 1.13's **57.91** (current public board leader). It leads on 31 of 38 benchmarks; Jev leads in knowledge-breadth tasks (GPQA Diamond 71.4% vs 34.0%, BBH 89.7% vs 71.3%) — tests that reward general knowledge over structured selection.

**Important caveat**: These scores are StartLuxLabs' own runs and are not on the public DI board ("our runs are not on the board"). Training data includes public train splits of 14 of the 38 benchmarks (marked †); test items were filtered out.

---

### GGUF Quantization Fidelity

BF16 and Q8_0 match the original weights on 99-100% of items. Q4_K_M keeps 96-98% agreement at 4B and up; at 0.8B and 2B, more answers change — Q8_0 is the better choice at those sizes. 35B-A3B is not yet available as GGUF.

---

### Limitations

**Knowledge breadth is not the strength.** On GPQA Diamond, BBH, MMLU-Pro — Jev 1.13 leads significantly. StartLux Decision is optimized for structured selection tasks, not general knowledge.

**Self-reported benchmarks, not on public board.** The 63.88 DI score hasn't been independently verified.

**Hard dependency on fast linear-attention kernels.** Consumer GPU compatibility may vary.

**35B-A3B has no GGUF.** Requires a single 80GB professional GPU.

**Extremely new project.** 5 days old, 51 stars — community validation and production reliability are unknown.

---

### Verdict

The approach is clear: decision tasks don't need language generation capability; reading probabilities directly from logits is both faster and more precise. This path already has Jev and SemIf on it; StartLux's differentiators are the full size ladder (0.8B to 35B) and the convincing game demos — real video of Mario, SC2, Doom runs is more visceral than benchmark numbers.

The project is very new, benchmarks are self-reported, and community feedback is thin. GGUF support and llama.cpp compatibility are practical pluses for local deployment: 0.53 GB for 0.8B Q4_K_M means it runs on nearly any device.

Apache-2.0, commercial use unrestricted.

---

> Open source for learning only. Apache-2.0 license — commercial use unrestricted.
