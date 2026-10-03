---
title: "具身智能技术指南：15K 星，VLA 与机器人策略学习的中文路线图"
titleEn: "Embodied-AI-Guide: 15K Stars, a Chinese-Language Roadmap for VLA and Robot Policy Learning"
description: "TianxingChen/Embodied-AI-Guide，Lumina 具身智能社区维护，15.9K 星。最受欢迎的中文具身 AI 学习路线图。系统覆盖算法（ACT/Diffusion Policy/DP3）、VLA 模型、LLM-for-Robotics、控制理论、仿真器和硬件选型。创建者陈天行，现为 MMLab@HKU 博士生。"
descriptionEn: "TianxingChen/Embodied-AI-Guide, maintained by the Lumina Embodied AI Community, 15.9K stars. The most-starred Chinese-language learning roadmap for embodied AI. Covers algorithms (ACT / Diffusion Policy / DP3), VLA models, LLM-for-Robotics, control theory, simulators, and hardware selection. Created by Tianxing Chen, now a PhD student at MMLab@HKU."
pubDate: 2026-10-03
heroImage: "../../assets/images/embodied-ai-guide-vla-robot-learning-lumina-chinese-guide-banner.jpg"
category: "Research"
tags: ["具身智能", "机器人", "VLA", "强化学习", "开源学习资源", "路线图"]
lang: "zh-CN"
wechatTitle: "具身智能技术指南：15K星中文VLA路线图"
wechatDigest: "Lumina社区维护；15.9K星；中文具身AI学习路线；ACT/DP/VLA模型；控制理论到实机部署"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 背景

具身智能（Embodied AI）是当前 AI 研究里最热也最难入门的方向之一——它横跨机器人控制、强化学习、视觉模型、大语言模型、传感器硬件，技术栈极其分散，中文学习资料质量参差不齐。

TianxingChen/Embodied-AI-Guide 试图解决这个问题：**一份系统、持续更新的中文具身 AI 技术路线图**。目前 15.9K 星，是 GitHub 上最受欢迎的同类中文资源。

**仓库**：github.com/TianxingChen/Embodied-AI-Guide  
**社区**：Lumina 具身智能社区  
**创建者**：陈天行（Tianxing Chen），MMLab@HKU 博士生，导师 Ping Luo 教授  
**Stars**：15.9K

---

## 为什么 15K 星

具身 AI 的入门难点不在某一个技术，而在**路线不清**：先学控制理论还是强化学习？PyBullet 还是 IsaacGym？CLIP 还是 RT-2？文献读哪些？

这份指南的价值在于给出了一条**有序的路径**，而不是一堆随机的链接堆砌。陈天行在创建仓库时还是本科/硕士阶段，结合自学经历梳理了哪些坑踩了之后才知道怎么绕，这个视角对同一阶段的学习者有直接参考价值。

---

## 内容结构

### 算法模块（核心）

算法是这份指南的主体，从工程基础到前沿研究按层次展开：

**基础工程工具**  
ROS/ROS2、仿真器（PyBullet、IsaacGym、MuJoCo、Sapien）、数据格式、常用 Python 库。这部分是入门前的必备背景，很多教程跳过了，这里补上了。

**视觉基础模型**  
CLIP、DINO、SAM 等在机器人感知中的应用，以及如何把这些模型接进控制流里。

**机器人学习与策略**  
从经典控制（PID、MPC）到学习型策略（RL、IL），三条主流策略路径：

| 方法 | 代表 | 特点 |
|------|------|------|
| ACT（Transformer Policy） | ActionChunking with Transformers | Imitation Learning，实机验证多 |
| Diffusion Policy | Chi et al. | 生成式策略，对多模态分布建模好 |
| DP3（3D Diffusion Policy） | 3D 点云 + 扩散策略 | 空间感知更强 |

**LLM-for-Robotics**  
LLM 做高层规划（任务分解、指令理解），接 low-level 执行器的架构（如 RT-2、PaLM-E），以及 LLM + 传统规划器的混合范式。

**VLA（Vision-Language-Action）模型**  
RT-2、OpenVLA 等多模态端到端策略，直接从视觉和语言生成机器人动作。VLA 是目前学术界最热的研究方向，这一节提供了入门所需的论文列表和代码仓库。

**导航与感知**  
室内/室外导航、障碍物检测、占据图、SLAM。

### 硬件模块

机械臂、传感器（RGB-D、力传感器）、基础硬件选型指南。不深入，但给出了入门参考。

### 软件与仿真

仿真器对比（各自适合的场景）、benchmark 列表（RLBench、LIBERO、AgiBot 等）、数据集。

---

## 创建者背景

陈天行（Tianxing Chen）是 Lumina 具身智能社区的创始人，2025 年 9 月入学 MMLab@HKU，研究方向是**具身 AI 基础设施**：机器人基础模型、数据生成器、评估体系。

从一个在学习具身 AI 的学生，到研究如何系统性地构建具身 AI 基础设施的 PhD——这条路径本身就是这份指南覆盖的内容。

---

## 适合谁

**最适合**：
- AI/ML 背景但刚开始接触机器人和具身 AI 的研究者、工程师
- 需要系统了解具身 AI 技术栈的产品/研究方向决策者
- 刚入学具身 AI 相关方向的研究生

**不适合**：
- 需要深入某个具体算法实现细节的人（这里是路线图，不是算法详解）
- 英语资源优先的读者（指南主体是中文，部分论文链接是英文原文）

---

## 需要注意的地方

**持续更新但维护节奏不固定**。15.9K 星的规模意味着社区有一定活跃度，但具体更新频率和各章节的深度有差异，建议配合原始论文和官方文档使用，不要把这份指南当成唯一来源。

**主要是路线图，不是教程**。指南给出的是"应该学什么、看什么"，不是手把手的代码教程。实际动手时还需要找对应的 notebook 或 tutorial 系列。

**硬件部分较浅**。对于需要真实机器人上手的工程师，这部分内容不够用，还需要参考具体平台的文档。

---

## 关键信息

| 字段 | 值 |
|------|----|
| 仓库 | TianxingChen/Embodied-AI-Guide |
| Stars | 15.9K |
| 社区 | Lumina 具身智能社区 |
| 创建者 | 陈天行（MMLab@HKU 博士生）|
| 主要语言 | 中文（含英文论文链接） |
| 核心内容 | 算法/VLA/LLM-for-Robotics/控制/仿真/硬件 |
| 定位 | 学习路线图，不是算法详解 |

---

## 综合判断

15.9K 星对于一份纯文档类仓库来说，是很强的社区信号。这说明具身 AI 中文学习资源的需求是真实存在的，而现有资源中这份指南填补了系统性路线图的空白。

它最大的价值不是内容深度，而是**组织方式**：把一个极度碎片化的领域整理成了一条可以走通的路径。对于刚入门的人，省去了"我该从哪里开始"这个最大的障碍。

创建者本身的学术背景和研究方向也保证了内容的专业性——他不是在整理网上随机链接，而是在梳理自己从学习者到研究者路径上的真实经验。

---

> 开源仅供学习，具体许可证请以仓库为准。

---

<!--EN-->

## Embodied-AI-Guide: 15K Stars, a Chinese-Language Roadmap for VLA and Robot Policy Learning

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Background

Embodied AI is one of the hottest and most difficult fields to enter right now — it spans robot control, reinforcement learning, vision models, large language models, and sensor hardware. The stack is fragmented, and quality learning resources in Chinese are scarce.

TianxingChen/Embodied-AI-Guide addresses this: **a systematic, continuously updated Chinese-language roadmap for embodied AI**. It currently has 15.9K stars — the most-starred Chinese-language resource of its kind on GitHub.

**Repo**: github.com/TianxingChen/Embodied-AI-Guide  
**Community**: Lumina Embodied AI Community  
**Creator**: Tianxing Chen (陈天行), PhD student at MMLab@HKU, supervised by Prof. Ping Luo  
**Stars**: 15.9K

---

### Why 15K Stars

The hard part of entering embodied AI isn't any single technology — it's the **unclear path**: Do I start with control theory or reinforcement learning? PyBullet or IsaacGym? CLIP or RT-2? Which papers matter?

This guide's value is giving a **structured order**, not just a pile of links. Chen created this during his undergraduate/master's years, distilling hard-won lessons from self-study. That perspective has direct relevance for learners at the same stage.

---

### Content Structure

**Algorithm module (core)**

Organized from engineering foundations to research frontiers:

- Engineering tools: ROS/ROS2, simulators (PyBullet, IsaacGym, MuJoCo, Sapien), data formats
- Vision foundation models: CLIP, DINO, SAM in robot perception pipelines
- Robot learning and policies — from classical control (PID, MPC) to learning-based:

| Method | Representative | Characteristic |
|--------|---------------|----------------|
| ACT (Transformer Policy) | ActionChunking with Transformers | Imitation learning, strong real-robot results |
| Diffusion Policy | Chi et al. | Generative policy, handles multimodal action distributions |
| DP3 (3D Diffusion Policy) | 3D point cloud + diffusion | Stronger spatial perception |

- LLM-for-Robotics: LLM as high-level planner (task decomposition, instruction understanding), connecting to low-level executors (RT-2, PaLM-E), hybrid LLM + classical planner architectures
- VLA (Vision-Language-Action) models: RT-2, OpenVLA, and the paper list for this research frontier
- Navigation: indoor/outdoor navigation, SLAM, obstacle detection

**Hardware module**: Robot arms, RGB-D sensors, force sensors, basic hardware selection guidance.

**Software and simulation**: Simulator comparisons, benchmark list (RLBench, LIBERO, AgiBot), datasets.

---

### Creator Background

Tianxing Chen founded the Lumina Embodied AI Community and enrolled at MMLab@HKU in September 2025. His research focus is **Embodied AI Infrastructure**: Robotic Foundation Models, Data Generators, and Evaluation Systems.

The path from "student learning embodied AI" to "PhD building infrastructure for embodied AI" mirrors the content this guide covers.

---

### Who It's For

**Best suited for**:
- AI/ML practitioners just entering robotics and embodied AI
- Decision-makers who need a systematic overview of the embodied AI stack
- Graduate students entering embodied AI research

**Not suited for**:
- Deep implementation details of specific algorithms (this is a roadmap, not a textbook)
- English-only readers (guide is primarily Chinese, with English paper links)

---

### Important Caveats

**Continuously updated but on an irregular schedule.** 15.9K stars indicates community activity, but coverage depth varies by section. Use it alongside original papers and official documentation, not as a sole source.

**Roadmap, not tutorial.** It tells you what to study and what to read — not step-by-step code tutorials. Hands-on work still requires dedicated notebooks and tutorial series.

**Hardware section is shallow.** Engineers who need to deploy on real robots will need to supplement with platform-specific documentation.

---

### Verdict

15.9K stars for a pure documentation repo is strong community signal. It means the need for systematic Chinese-language embodied AI resources is real, and this guide filled a gap that wasn't being filled.

Its main value isn't depth — it's **organization**: taking an extremely fragmented field and structuring it into a navigable path. For newcomers, it removes the biggest obstacle: "I don't know where to start."

The creator's own academic trajectory, from learner to infrastructure researcher, ensures the content is grounded in genuine experience rather than curated links.

---

> Open source for learning only. Check the repository for current license terms.
