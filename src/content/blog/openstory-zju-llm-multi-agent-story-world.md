---
title: "浙大开源 OpenStory（万象谱）：LLM 驱动多 Agent 让《红楼梦》和《西部世界》活起来"
titleEn: "ZJU Open-Sources OpenStory: LLM Multi-Agent Framework Brings Dream of the Red Chamber and Westworld to Life"
description: "ZJU-LLMs/OpenStory（万象谱，321 stars）是浙大 LLM 组开源的多智能体故事推演框架。它基于 Agent-Kernel 构建，已落地两个完整故事世界：《红楼梦》大观园（人物自主社交推演）和《西部世界》（Host 逐渐觉醒的仿真乐园）。Agent 不是聊天机器人，是有感知-计划-执行-反思完整生命周期的独立行为体；他们在地图上自主行走、产生冲突、积累记忆，玩家可以观察也可以介入。"
descriptionEn: "ZJU-LLMs/OpenStory (321 stars) is an open-source multi-agent story simulation framework from Zhejiang University's LLM group. Built on Agent-Kernel, it ships two complete story worlds: Dream of the Red Chamber's Grand View Garden (autonomous character social simulation) and Westworld (Hosts gradually achieving consciousness). Agents aren't chatbots — they have a full perception-planning-execution-reflection lifecycle, moving autonomously on maps, generating dramatic conflicts, and accumulating memories. Players can watch or intervene."
pubDate: "2026-07-21"
updatedDate: "2026-07-21"
category: "Tech-Experiment"
tags: ["多智能体", "社会仿真", "红楼梦", "西部世界", "LLM", "OpenStory", "浙大", "开源", "AI Agent", "故事生成"]
heroImage: "../../assets/images/openstory-zju-llm-multi-agent-story-world-banner.jpg"
---

> **GitHub**：[ZJU-LLMs/OpenStory](https://github.com/ZJU-LLMs/OpenStory) · ⭐ 321 · Python · MIT  
> **出品**：浙江大学 LLM 组（ZJU-LLMs）  
> **底层框架**：[Agent-Kernel](https://github.com/ZJU-LLMs/Agent-Kernel)

---

## 这不是 NPC 对话，是一个活的世界

大多数"AI + 游戏"的尝试是这样的：你问角色一个问题，角色用 LLM 生成一段对话，然后等你的下一个输入。

**OpenStory 做的是另一件事**：它构建了一个可以自主运转的世界，角色不需要等你输入就会自己去做事。

林黛玉会因为贾宝玉的一句话而郁郁寡欢，然后去葬花；贾宝玉会在大观园里漫无目的地游荡，遇到不同的人产生不同的化学反应；西部世界的 Dolores 会在日复一日的循环中积累隐约的熟悉感，直到某个触发点让她开始质疑自己所在的世界。

这不是剧本，是 **LLM 驱动的多 Agent 推演**。

---

## 两个已落地的故事世界

### Story 1：红楼梦大观园

第一个完整故事世界。以《红楼梦》为背景，在 1:1 仿真的大观园地图上，多个 Agent 同时运行，每个角色都有：

- 独立的性格设定和背景档案
- 对当前环境的感知能力（谁在附近、发生了什么）
- 自主规划下一步行动
- 对互动的记忆和反思

系统不是走剧本，而是给定性格设定和环境约束，让 Agent 自己推演出戏剧性冲突。林黛玉的敏感多思、贾宝玉的叛逆多情、整个贾府在历史车轮下的命运交织——这些不是预设的，是从 Agent 行为中自然涌现的。

**两种游玩模式**：
- **自由模式**：观察角色的自主行动，看 AI 把红楼梦演成什么样子
- **剧情模式**：以复兴大观园为目标，玩家向角色下达指令，AI 根据你的选择推演剧情走向；支持故事回溯，回到历史节点重选

### Story 2：西部世界（West World）

第二个故事世界，灵感来自同名美剧。仿真乐园里，Host 会：

- **感知场景**：注意到环境变化、其他角色的行为
- **规划行动**：移动、交谈、完成设定的任务循环
- **积累记忆**：反复出现的日常、难以解释的熟悉感、他人的只言片语
- **逐渐觉醒**：记忆积累到一定程度，开始发现循环背后的真相

两种模式：
- **自由模式**：观察 Dolores、Maeve、Teddy 等角色的自主互动和命运分岔
- **剧情模式**：扮演一名 Host，选择结盟、隐藏异常或逃离乐园，在 Overseer 的监控与干预下推演觉醒故事

Overseer 会实时监控 Host 的异常行为并介入——这个对抗张力让游戏不只是被动观察。

---

## 技术架构：Agent-Kernel 作为底层

OpenStory 的核心不是一个独立系统，而是建在 [Agent-Kernel](https://github.com/ZJU-LLMs/Agent-Kernel) 之上的上层框架。

### Agent 的完整生命周期

每个 Agent 都有四个阶段：

```
感知（Perception）
    ↓
规划（Planning）
    ↓
执行（Execution）
    ↓
反思（Reflection）
    ↓
（下一个 Tick）
```

这不是一次性的"输入→输出"，而是一个持续运转的循环。Agent 在每个 Tick 里感知当前环境，基于历史记忆和性格设定规划行动，执行后反思结果，为下一个 Tick 更新状态。

### 动态 Agent 管理

底层 Agent-Kernel 支持在推演过程中**动态增删 Agent**——这意味着可以在故事进行中引入新角色，或者让角色"死亡"退出系统，而不需要重启整个仿真。静态剧本的约束消失了。

### 插件化设计

感知、计划、执行、反思各阶段都是插件，可以独立替换和扩展。整个系统通过 YAML 文件配置：

- `simulation_config.yaml`：全局入口，Pod 数量、最大 Tick 数
- `models_config.yaml`：LLM 模型接口和参数（OpenAI 兼容）
- `system_config.yaml`：消息总线（Redis）和时钟配置

### 基础设施

- **Redis**：消息总线和缓存，端口 6379
- **Ray**：分布式运行时，支持多 Agent 并行推演
- **前端**：本地 Web 界面，`http://localhost:8000/frontend/index.html`，实时展示 Agent 在地图上的位置、状态和互动记录

---

## 快速上手

```bash
# 1. 安装 Agent-Kernel
git clone https://github.com/ZJU-LLMs/Agent-Kernel.git
cd Agent-Kernel
pip install -e "packages/agentkernel-distributed[all]"

# 2. 启动 Redis（需要本地已安装）
redis-server

# 3. 运行红楼梦
python -m examples.story_of_the_stone.run_simulation

# 4. 访问可视化界面
# http://localhost:8000/frontend/index.html
```

也有 **Launcher 客户端**版本（一键点击即玩），前往 [releases](https://github.com/ZJU-LLMs/OpenStory/releases) 下载。

---

## 这个项目在探索什么

OpenStory 的核心命题是：**LLM 驱动的多 Agent 能不能涌现出真实的戏剧性？**

大多数 AI 生成叙事的路径是：给 LLM 一个提示，让它生成一段故事文本。OpenStory 的路径完全不同：它构建一个多 Agent 的社会环境，给每个 Agent 性格、记忆和行动能力，然后让系统自己跑起来，**戏剧性从 Agent 之间的交互中涌现**。

这和斯坦福的 Smallville（generative agents 的原型实验）类似，但 OpenStory 直接对准了有深厚人文底蕴的具体故事世界——选《红楼梦》和《西部世界》不是偶然，这两个世界恰好代表了两种截然不同的叙事问题：

- **红楼梦**：高密度的社会关系网络，角色之间的互动充满层次和含义
- **西部世界**：记忆和觉醒的主题，正好对应 Agent 的记忆积累机制

用 AI 来仿真人类最复杂的情感叙事，本身就是一个有趣的测试床。

---

## 数据一览

| 属性 | 值 |
|---|---|
| Stars | 321（2026-07-21） |
| 创建时间 | 2026-04-01 |
| 语言 | Python |
| 开源协议 | MIT |
| 出品方 | 浙江大学 LLM 组 |
| 底层框架 | Agent-Kernel |
| 已落地故事 | 红楼梦、西部世界 |
| 消息总线 | Redis |
| 分布式运行时 | Ray |
| LLM 接口 | OpenAI 兼容 |
| 客户端 | Launcher（一键安装） |
| 媒体报道 | 新智元 |

© 2026 Author: Mycelium Protocol

<!--EN-->

## OpenStory: LLM Multi-Agent Framework for Living Story Worlds

**GitHub**: [ZJU-LLMs/OpenStory](https://github.com/ZJU-LLMs/OpenStory) · ⭐ 321 · Python · MIT  
**By**: Zhejiang University LLM Group  
**Foundation**: [Agent-Kernel](https://github.com/ZJU-LLMs/Agent-Kernel)

### Not NPC Dialogue — A Self-Running World

Most "AI + game" projects work like this: you ask a character a question, the LLM generates a response, and the character waits for your next input.

OpenStory does something different: it builds a world that runs autonomously. Characters don't wait for your input — they act on their own.

Lin Daiyu will grow melancholy after a careless remark from Jia Baoyu and go bury flowers. Dolores will accumulate faint familiarity across repeated loops until a trigger makes her question the nature of her reality. These aren't scripted sequences — they're emergent behaviors from LLM-driven multi-agent simulation.

### Two Shipped Story Worlds

**Story 1: Dream of the Red Chamber (红楼梦)**

A 1:1 replica of the Grand View Garden (大观园) with multi-agent characters from the classic novel. Each agent has an independent personality profile, perceives its environment (who's nearby, what's happening), plans its next action, and reflects on interactions to update its memory. The dramatic conflicts — Lin Daiyu's sensitivity, Jia Baoyu's rebelliousness, the Jia family's interwoven fates — emerge from agent behavior, not a pre-written script.

Two modes: **Free** (observe autonomous character interactions) and **Story** (player gives directives toward a goal, AI simulates the consequences; includes story rewind to branch points).

**Story 2: Westworld (西部世界)**

A simulated park where Hosts accumulate memories across loops. Agents: perceive the scene, plan their routine actions, accumulate memories of recurring events and half-heard conversations, and gradually discover the truth behind the loop. An Overseer monitors and intervenes when anomalies appear — creating adversarial tension.

Two modes: **Free** (observe Dolores, Maeve, Teddy's autonomous diverging fates) and **Story** (play as a Host — choose to form alliances, hide anomalies, or attempt escape from the park).

### Technical Architecture

**Agent lifecycle** (4 stages per Tick):
```
Perception → Planning → Execution → Reflection → (next Tick)
```

Not a one-shot input→output. Each Tick, agents sense the current environment, plan based on personality and accumulated memory, execute, then reflect — updating state for the next cycle.

**Dynamic agent management**: Agent-Kernel supports adding/removing agents mid-simulation. Characters can "die" and leave, or new ones can enter, without restarting the system.

**Plugin-based design**: Each lifecycle stage is a plugin — independently replaceable. Configuration via YAML files:
- `simulation_config.yaml`: global entry, Pod count, max Ticks
- `models_config.yaml`: LLM API config (OpenAI-compatible)
- `system_config.yaml`: Redis message bus and timer

**Infrastructure**: Redis (message bus, port 6379) + Ray (distributed runtime for parallel agent simulation) + local web frontend at `localhost:8000`.

### Quick Start

```bash
# Install Agent-Kernel
git clone https://github.com/ZJU-LLMs/Agent-Kernel.git
cd Agent-Kernel && pip install -e "packages/agentkernel-distributed[all]"

# Run Dream of the Red Chamber
python -m examples.story_of_the_stone.run_simulation
# → http://localhost:8000/frontend/index.html
```

Or download the one-click Launcher client from [releases](https://github.com/ZJU-LLMs/OpenStory/releases).

### What This Explores

OpenStory's core question: **can LLM-driven multi-agent systems produce genuine dramatic emergence?**

The alternative path (generate story text from a prompt) produces text. OpenStory's path produces a social environment — give agents personality, memory, and action capability, then let the system run. Drama emerges from inter-agent interaction, not from a language model told to write drama.

Choosing Dream of the Red Chamber and Westworld isn't arbitrary: the two represent fundamentally different narrative problems. Red Chamber has a high-density social relationship network where inter-character interactions carry layers of meaning. Westworld's core theme — memory and awakening — maps directly onto the agent memory-accumulation mechanism. Testing LLM agents against humanity's most complex emotional narratives is a revealing benchmark.

© 2026 Author: Mycelium Protocol
