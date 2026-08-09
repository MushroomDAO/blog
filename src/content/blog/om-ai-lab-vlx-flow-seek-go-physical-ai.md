---
title: "om-ai-lab VLX三件套：让AI真正看懂、认准、导航物理世界"
titleEn: "om-ai-lab's VLX Trio: Teaching AI to See, Pinpoint and Navigate the Physical World"
description: "om-ai-lab 发布 VLX-Flow、VLX-Seek、VLX-Go 三个模型，分别解决物理AI最核心的三个难题：流式视频理解、精准目标定位、轻量导航决策。0.6B 模型在追踪率上超越 7B 级选手，Linear Attention 让 TTFT 随流增长趋近水平线。"
descriptionEn: "om-ai-lab releases three VLX models tackling the hardest problems in physical AI: VLX-Flow for streaming video memory, VLX-Seek for fine-grained spatial grounding via region tokens, and VLX-Go — a 0.6B waypoint planner that beats 7B models on tracking rate."
pubDate: "2026-07-30"
updatedDate: "2026-07-30"
category: "Tech-News"
tags: ["Physical AI", "VLM", "视频理解", "具身智能", "om-ai-lab", "VLX", "机器人", "Mycelium"]
heroImage: "../../assets/images/om-ai-lab-vlx-flow-seek-go-physical-ai-banner.jpg"
---

*by Mycelium Protocol*

---

大模型做视觉理解，这条路已经走了很久。GPT-4o 能看图，Claude 能读文档，Gemini 能处理长视频——但它们的共同前提是：**视频是一个文件，我处理完再回答你**。

这个假设在手机、服务器上没问题。但装在机器人身上、无人机上、工厂摄像头里，完全不行。那些设备要处理的，是永不停止的实时画面流。

om-ai-lab 最近连续发布了三个模型，每一个都在戳这条路上的一个具体窟窿。

---

## VLX-Flow：视频不是文件，是一条水流

**仓库**: [github.com/om-ai-lab/VLX-Flow](https://github.com/om-ai-lab/VLX-Flow)

传统 VLM 处理视频的方式是：

```
offline video request → full reprocessing → answer
```

时间越长的视频，context 越大，每次回答都要重新处理一遍全部历史帧。延迟随着流增长，内存也随之膨胀。

VLX-Flow 的设计逻辑是把这条单向管道改成：

```
continuous observation → incremental memory update → instant interaction
```

具体怎么做？两层内存机制：

**Visual Cache（视觉缓存）**：保存最近几帧的细节特征，用于即时事件检测和当前状态判断。

**Semantic Memory（语义记忆）**：把历史视频流压缩成高层语义状态，包括此前的描述、问答对话、观测到的关键事件——不是原始帧，而是提炼后的"理解"。

这两层配合，让模型既不丢最近的细节，也不用无限膨胀 context。

然后是推理效率的关键：**Linear Attention**。标准 Transformer 的 KV Cache 随序列长度线性增长，每一次新 token 进来都要和全量历史做注意力计算。VLX-Flow 在语言模型中引入 Linear Attention 层，历史通过循环状态压缩维护，增量更新。

结果体现在 TTFT（Time to First Token）曲线上：

- Full Attention：随历史增长线性上升
- SlideWindow：周期性重置，锯齿上升
- **VLX-Flow：水平线，长流也稳**

这对摄像头、机器人眼睛这类持续工作的场景，是本质性改变。

---

## VLX-Seek：不只是"看到了"，还要"在哪里"

**仓库**: [github.com/om-ai-lab/VLX-Seek](https://github.com/om-ai-lab/VLX-Seek)  
**模型**: [omlab/VLX-Seek-1.5-10B](https://huggingface.co/omlab/VLX-Seek-1.5-10B)（2026-07-23 开源）

现有 VLM 的定位方式是输出坐标：

```
"Find the red car" → [x1:0.23, y1:0.41, x2:0.67, y2:0.89]
```

这对语言模型很不友好。坐标是长数字串，多目标就要输出更多数字，一个格式错误整个结果就废了。而且解码长度随目标数量线性增长。

VLX-Seek 把任务重新定义了：

```
image + region tokens + text query → retrieve matching regions → grounded answer
```

先用一个轻量的 region detector（WeDetect-Base-Uni，或者任何你自己的检测器）提取候选区域，编码成可寻址的 region token：`<obj0>`, `<obj1>`, `<obj2>`...

语言模型的任务不再是"生成坐标"，而是"从这些 region token 里选出哪个匹配描述"：

```
<ground>people wearing red</ground><objects><obj2><obj5></objects>
```

几个好处立竿见影：
- 输出更短：5个目标只需要5个 token，不是5组8位坐标
- 解码更快：LLM 本来就擅长选择和引用，不擅长精确生成数字
- 拒绝幻觉更容易：没有目标时输出 `None`，比强行生成越界坐标更自然

VLX-Seek 1.5（10B，已开源）的改进方向：
- 加入无人机视角、监控视角、机械臂视角训练数据（面向具身场景）
- 更快的 proposal pipeline + 更多 Linear Attention 层
- 硬负样本训练，改善"目标不存在时不乱报"

---

## VLX-Go：从"看"到"动"

**仓库**: [github.com/om-ai-lab/VLX-Go](https://github.com/om-ai-lab/VLX-Go)

VLX-Go 是三个里最小也最出乎意料的一个。

它要解决的问题：给机器人、无人机一个导航规划能力——不是描述场景，是决定"下一步往哪里走"。

输入：
- 最近几帧历史画面 `{I_{t-k}, ..., I_{t-1}}`
- 当前帧 `I_t`
- 自然语言指令（如 "follow the target person and avoid obstacles"）

输出：短程路径点序列 `{w_1, ..., w_T}`，直接交给控制器执行。

架构上分成两阶段：
1. **离线轨迹学习**：从示范数据中学跟踪目标、生成路径点
2. **在线优化**：从仿真器反馈中学习，处理遮挡、障碍物、闭环漂移

在 EVT-Bench 的 STT 任务上，VLX-Go（0.6B）对比结果：

| 模型 | 参数量 | 成功率 SR ↑ | 追踪率 TR ↑ | 碰撞率 CR ↓ |
|------|------|------|------|------|
| TrackVLA | 7B | 85.1% | 78.6% | **1.65%** |
| NavFoM | 7B | 85.0% | 80.5% | - |
| Qwen-RobotNav-8B | 8B | 78.6% | 89.7% | 5.7% |
| **VLX-Go** | **0.6B** | **85.42%** | **94.08%** | 6.55% |

0.6B 的模型，成功率持平 7B 级别选手，追踪率超过所有人（+13.58% vs TrackVLA）。参数量是 TrackVLA 的 1/12。

碰撞率相对较高（6.55% vs 1.65%），这是当前主要的优化方向——需要更好的安全约束和控制器协同。

---

## 三个模型的整体定位

om-ai-lab 把这三个模型放在一起，逻辑很清晰：

| 模型 | 解决什么 | 关键创新 | 状态 |
|------|------|------|------|
| VLX-Flow | 连续视频流理解 | 两层内存 + Linear Attention | 代码发布，权重 coming soon |
| VLX-Seek | 精准目标定位 | Region token 替代坐标生成 | 10B 已开源 |
| VLX-Go | 轻量导航决策 | 0.6B 路径点预测，闭环评估 | 权重 coming soon |

这三个解决的是物理 AI 的**感知-定位-行动**三层：看懂（Flow）→ 找准（Seek）→ 走到（Go）。

传统 VLM 研究主要在"看懂"这层。VLX-Seek 和 VLX-Go 把链路往下延伸，直接对接具身智能的使用场景：无人机跟踪、工厂质检、机器人导航、监控预警。

VLX-Seek 1.5-10B 是当前唯一可以直接用的权重，其余两个权重还在路上。对需要做 grounding 任务的团队，现在是入手研究的好时机。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。一个持续追踪 AI 工具、系统和实验的内容节点。
> 关注公众号获取更新，或在 GitHub 找到我们。

---

<!--EN-->

## VLX-Flow, VLX-Seek, VLX-Go: om-ai-lab's Physical AI Trilogy

*by Mycelium Protocol*

Most VLMs are built on a silent assumption: video is a file. You hand it over, the model processes it in full, and then it answers. That works fine for offline analysis—but falls apart the moment you mount a camera on a robot, drone, or factory floor. Those devices see an infinite stream that never stops.

om-ai-lab's three recent releases each target a specific gap in physical AI vision pipelines.

### VLX-Flow: Video Is a River, Not a File

The shift VLX-Flow makes is architectural:

```
before: offline video → full reprocessing → answer
after:  continuous stream → incremental memory update → instant interaction
```

Two memory layers maintain continuity without an ever-growing context:

- **Visual Cache**: recent frame-level details for immediate event detection
- **Semantic Memory**: compressed high-level narrative from the full stream history — prior observations, Q&A pairs, model answers

The efficiency unlock is **Linear Attention**. Standard self-attention requires the KV cache to grow with every new frame. Linear Attention maintains history through a recurrent state, updated incrementally — keeping TTFT (time to first token) flat as the stream grows. Full Attention climbs linearly. SlideWindow oscillates with periodic resets. VLX-Flow stays horizontal.

### VLX-Seek: From "There" to "Exactly Where"

VLX-Seek's core insight is that making an LLM generate bounding-box coordinates is the wrong abstraction. Coordinates are long numeric sequences, fragile to formatting errors, and scale poorly with multiple targets.

Instead, VLX-Seek reformulates localization as **region retrieval**:

1. A lightweight detector (WeDetect or any detector) proposes candidate regions
2. These become addressable region tokens: `<obj0>`, `<obj1>`, `<obj2>`...
3. The LLM selects and references them: `<ground>person in red</ground><objects><obj2><obj5></objects>`

This makes localization a selection task rather than a generation task — something LLMs already handle well. Output is shorter (5 token IDs vs 5 × 4 coordinate floats), decoding is faster, and absent-target rejection is explicit via a `None` format. VLX-Seek 1.5-10B is open-sourced as of 2026-07-23.

### VLX-Go: From Watching to Moving

VLX-Go completes the chain. Given recent visual history, the current frame, and a natural-language instruction, it outputs short-horizon local waypoints that a downstream controller executes directly.

At 0.6B parameters it achieves:
- **85.42% success rate** — matching 7B-class models
- **94.08% tracking rate** — +13.5 points over the 7B TrackVLA baseline

At 1/12th the parameter count. The collision rate (6.55% vs 1.65% for TrackVLA) remains the open challenge, requiring tighter safety constraint integration with the controller.

### The Integrated Picture

The three models address physical AI's fundamental stack:

| Model | Role | Key Innovation | Status |
|-------|------|----------------|--------|
| VLX-Flow | See (streaming) | Two-layer memory + Linear Attention | Code public, weights soon |
| VLX-Seek | Locate (grounding) | Region tokens replace coordinate generation | 10B open-sourced |
| VLX-Go | Move (navigation) | 0.6B closed-loop waypoint planner | Weights coming soon |

Traditional VLM research stops at "understand the scene." VLX-Seek and VLX-Go extend the chain into actuation — the part that actually matters for drones, robots, and surveillance systems operating in the real world.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
