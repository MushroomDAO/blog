---
title: "Higgsfield Zephyr: Special 全开源：K-pop 机甲 AI 电影的完整制作工艺"
titleEn: "higgsfield-zephyr-special-kpop-mecha-ai-film-open-source-seedance"
description: "Higgsfield 将旗下 K-pop 机甲 AI 短片系列《ZEPHYR: Special》的完整制作过程全部开源：所有提示词、角色资产、失败镜头、最终剪辑版本，共 197 个资产公开发布于平台上，任何人都可以直接进入 Cinema Studio 查看和复用。主创团队披露了两个「不可能镜头」的实现方法：倒置角色参考图技巧和锚点式最小提示词策略。底层模型是 Seedance 2.5，结合 Higgsfield Soul 2 进行角色和服装设计，再用 Nano Banana 2 Pro 精修成最终资产。文章总结了整条 AI 电影工业流水线——从角色开发、机甲设计、场景控制，到 Higgsfield 全平台工具组的工程假设和实战指导。"
descriptionEn: "Higgsfield has fully open-sourced the production process of ZEPHYR: Special, their K-pop mecha AI short film — all prompts, character assets, failed takes, and final cuts (197 assets total) are publicly available in Cinema Studio for anyone to study and remix. The team reveals two 'impossible shot' techniques: the inverted character sheet method and anchor-point minimal prompting. The underlying model is Seedance 2.5, with Higgsfield Soul 2 for character/costume design and Nano Banana 2 Pro for final asset refinement. This article walks through the complete AI film pipeline — character development, mech design, scene control, and the engineering assumptions and production guidance behind Higgsfield's toolchain."
pubDate: "2026-08-12"
updatedDate: "2026-08-12"
category: "Tech-News"
tags: ["AI视频", "AI电影", "Higgsfield", "Seedance", "开源", "视频生成", "提示词工程", "Mycelium"]
heroImage: "../../assets/images/higgsfield-zephyr-special-kpop-mecha-ai-film-open-source-seedance-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

这是 AI 视频领域第一次有人把一部机甲 K-pop 短片的完整制作过程拆开来给你看：提示词、角色参考图、失败镜头、成功镜头，连创作过程中走过的弯路都留着，全部公开。

**《ZEPHYR: Special》**，Higgsfield 出品，约 5 分 7 秒，使用 Seedance 2.5 制作，发布后 16 小时内超过 11,000 次播放。

完整项目文件：https://higgsfield.ai/original-series/zephyr-special/full-film  
（在 Cinema Studio 中打开即可查看所有提示词和资产）

---

## 这是谁的故事

《Zephyr》的世界里，有一支由五个女孩组成的小队——她们既是 K-pop 偶像，也是驾驶机甲的战斗精英。五个角色，每人都有独立的性格设定、服装设计、专属机甲：

- **MIRA** — 战略型领袖，机甲配备火焰喷射器
- **REINA** — 近战专家，爆发力强
- **NAOMI** — 技术型成员，机甲装备钩爪，是《Special》这集的核心视角
- **ZERO** — 冷静型狙击手
- **HARUMIN** — 支援型角色，小队的情感纽带

《Special》的剧情：Naomi 深陷险境，机甲倒扣，生死悬于一线。就在此时，一位神秘的客座角色出现，用超越小队认知的机甲战斗技巧将她解救。

---

## 两个「不可能镜头」

主创团队在开源说明里重点披露了两个技术难题，以及他们最终如何解决它的。

### 技巧 1：倒置角色参考图

Naomi 的机甲在这场戏里是倒扣着的。他们需要画面传达出失重感和混乱感。

**第一个方案：精确提示词描述物理状态。**

失败。模型生成的结果没有准确捕捉倒置状态下的物理感。

**解决方案：把问题推到输入阶段。**

他们把角色参考图直接倒置——把物理状态「烘焙」到输入里，而不是试图在提示词里解释物理原理。这样，提示词就不需要再解释「为什么是这个姿态」，可以专注描述画面的细节和情绪。

结果：Naomi 有了一个专属的「倒置状态」角色参考图。

**工程层面的核心假设：模型更擅长从视觉输入推断物理状态，而不是从文本描述重建物理状态。** 把物理信息编码进图像输入，是绕开文本-物理转换损耗最有效的方式。

---

### 技巧 2：锚点式最小提示词

Naomi 被从机甲里救出来的镜头，是这集里最紧张的画面之一：需要同时传达危险感、机甲的巨大重量、Naomi 的体力和无畏，以及她骨子里的优雅和脆弱。

**他们没有用精确描述每一帧动作的方式写提示词。**

相反，他们只设定了几个关键锚点，把更多创作自由留给模型：

> 我们想传达的是危险感、机甲的巨大重量、Naomi 的体力和无畏——在不失去她的优雅和脆弱的前提下。

结果：模型在锚点约束内自主填充了动作细节，反而产生了他们原本想要但无法用精确提示词复现的那种「真实感」。

**工程层面的核心假设：复杂动作场景中，过度精确的提示词会压缩模型的创作空间，导致僵硬感。给定结果期望（情绪/物理结果）而非过程描述，能得到更自然的动作。**

---

## 开源了什么

《ZEPHYR: Special》一共公开了 **197 个资产**，包括：

- 所有使用的提示词（无一保留）
- 最终入选剪辑的镜头
- 失败镜头（bloopers）——包括走过的弯路和被淘汰的方案
- 角色参考图（包括「倒置状态」等特殊状态版本）

任何人都可以在 Higgsfield Cinema Studio 里打开这个项目，看到完整的生成记录，从第一版到最终版本，一步步的迭代过程完全透明。

---

## 第一集的工程教训（Seedance 2.0）

团队同样公开了《Zephyr》第一集（使用 Seedance 2.0 制作）的制作经验，那时他们还在摸索这条生产流水线。

### 机甲角色参考图：细节的双刃剑

最初，他们制作了包含所有细节的「主参考图」：武器系统、舱盖开合机制、各种状态。

**问题**：模型看到细节，就会尝试展示细节。

具体来说：机甲的舱口在角色参考图里是开着的（作为一种状态说明），结果模型几乎在所有场景里都把舱口画成开着的，或者在「应该关闭」和「开着」两个状态之间形成冲突，导致机甲外形发生变形。

**解决方案**：

1. **多版角色参考图，分状态管理**：把武器收纳状态和展开状态分成两张参考图。只有场景里需要展示武器时，才上传带武器的参考图。

2. **局部特写作为独立输入**：如果需要展示武器的具体工作方式（比如 Mira 的喷火器怎么伸出来），把这个部件的特写图单独上传，而不是期望模型从整体参考图里「聚焦」到这个细节。

3. **参考图上的文字说明几乎无效**：「Retractable revolver in the arm」之类的注解对模型没有实质帮助——你还是需要在提示词里完整描述武器的动作过程。别依赖参考图上的标注。

### 样式前缀的重要性

《第一集》里，他们还没有建立统一的样式前缀（style prefix）。这导致不同场景之间的视觉风格不够统一。

**建议**：在开始制作前建立一个固定的样式前缀（打光风格、色调、摄影机语言），放在所有提示词开头，保持整集的视觉一致性。

---

## 角色创建流水线

**整条角色创建流水线**分三步：

### 第一步：角色设定
用 Higgsfield Supercomputer 或 Claude 进行角色性格头脑风暴。主创团队明确说：「你可以很快通过与 AI 协作，获得那层基础深度——别让知识不足成为创作的障碍，直接开始吧。」

性格设定的作用不只是故事，更是**生成指南**：知道角色的性格，才能准确描述她的表演、反应和潜在故事弧。

### 第二步：服装和形象设计
用 **Higgsfield Soul 2** 进行角色和服装创作。Soul 2 的时尚能力几乎没有限制，可以处理任意风格混搭和细节组合，用来设计偶像 × 战士的复合形象效果最佳。

### 第三步：角色参考图精修
用 **Nano Banana 2 Pro** 和 **Seedream** 把设计稿整合成最终角色参考图资产。

---

## Seedance 2.5 改变了什么

《Zephyr》第一集用的是 Seedance 2.0（那时刚发布，团队还在大量实验）。

《Zephyr: Special》用的是 **Seedance 2.5**。主创团队在项目说明里直接说：

> 今天，AI 创作者在与「演员」合作方面的体验，已经越来越接近在真实片场的感受。技术层面的取巧和与模型的博弈正在退场，这让你能更深入地沉浸到创作过程中，打磨那些细微之处。

**Seedance 2.5 带来的最关键变化**：角色一致性和场景控制能力大幅提升——这是那两个「不可能镜头」能在没有妥协的情况下实现的底层原因。

---

## Higgsfield 平台生态

Higgsfield 不只是一个视频生成工具，它在构建一个**AI 原生的内容生产平台**：

| 工具 | 用途 |
|------|------|
| **Cinema Studio** | 场景控制、项目管理、生成历史追踪 |
| **Soul 2** | 角色/人物/服装创作 |
| **Nano Banana 2 Pro** | 图像精修 |
| **Seedream** | 角色参考图整合 |
| **Seedance 2.5** | 主视频生成模型（ByteDance） |
| **Supercomputer** | AI 辅助头脑风暴 |
| **Academy** | 制作流程课程（免费）|

**Higgsfield Academy** 目前有几门重点课程与这个话题直接相关：
- *Blockbuster 4K: The AI Filmmaking Pipeline*（40 分钟，从脚本到逐场景提示词工程）
- *Build an Ultra-Realistic Short Film in 4K*（33 分钟，Claude Fable 5 + Seedance 2.0 4K 足球剧）
- *Add AI VFX to Real Footage*（12 分钟，真实素材 + AI VFX 合成）

**Higgsfield Global Film Festival** 目前正在进行，奖金池 **100 万美元**。Higgsfield 选择在此时开放《Zephyr》和《Hell Grind》的完整制作文件，意图很明显：帮助参赛者真正理解生产工艺。

---

## 《Hell Grind》：另一个开源参照

同期，Higgsfield 也开源了另一部原创系列《Hell Grind》第一集——四个街头少年意外得到神秘力量。这集的规模更大：

- 365,561 次观看
- 115,446 次生成（公开的完整生成历史）
- 3,138 个公开资产

这两套开源素材合在一起，构成了目前 AI 视频领域**最完整、最透明的生产案例库**之一。

---

## 实战总结

从《Zephyr》整个开源项目里，可以提炼出一套 AI 电影工业的核心工程思路：

1. **把物理状态编进输入，别试图用文字解释物理** ——倒置参考图技巧
2. **复杂动作场景：只给锚点，不给过程** ——锚点式最小提示词
3. **多状态角色参考图** ——每个重要状态（收纳/展开/特殊）单独一张，别共用
4. **局部特写优先于整体参考图** ——细节展示用独立输入
5. **样式前缀统一视觉语言** ——在所有提示词开头建立一致的打光/色调/摄影机前缀
6. **先做性格，再做生成** ——知道角色是谁，才能准确描述她该怎么演
7. **公开失败镜头是最好的工程文档** ——bloopers 比成功镜头更能说明问题在哪里

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Higgsfield Zephyr: Special — Fully Open-Source K-Pop Mecha AI Film with Complete Production Breakdown

*by Mycelium Protocol*

---

This is the first time in the AI video space that someone has torn open an entire mecha K-pop short film and shown you exactly how it was made: every prompt, every character reference, every failed take alongside the final cuts — all public.

**ZEPHYR: Special**, produced by Higgsfield, runs 5 minutes 7 seconds, built on Seedance 2.5, and hit 11,000+ views within 16 hours of release.

Full project files: https://higgsfield.ai/original-series/zephyr-special/full-film  
(Open in Cinema Studio to browse all prompts and assets)

---

### The World of Zephyr

In the Zephyr universe, five girls are simultaneously K-pop idols and elite mecha pilots:

- **MIRA** — strategic leader, mech carries a flamethrower
- **REINA** — close-combat specialist, explosive power
- **NAOMI** — technical specialist, mech equipped with a grappling hook; central perspective of *Special*
- **ZERO** — calm sniper type
- **HARUMIN** — support role, the squad's emotional anchor

*Special* episode: Naomi is in dire straits, her mech trapped upside-down. A mysterious guest character with mech combat mastery beyond the squad's expectations rescues her.

---

### Two "Impossible Shots" — and How They Did Them

The production team disclosed the engineering challenges and solutions behind two shots in the open-source brief.

**Technique 1: The inverted character sheet**

Naomi's mech is upside-down in the opening action. The team needed to convey disorientation and shifted gravity.

First attempt: precise prompting to describe the physical state. It failed — the model didn't accurately reproduce the upside-down physics.

Solution: **invert the input, not the prompt.** They flipped the character reference sheet so the physics were baked into the input stage. The prompt no longer needed to explain *why* the mech was inverted — it could focus on the emotional and visual details instead.

Result: Naomi now has a dedicated "inverted state" character sheet.

**Engineering assumption**: *The model is better at inferring physical states from visual inputs than reconstructing them from text descriptions. Encoding physics into the image input bypasses the text-to-physics translation loss.*

**Technique 2: Anchor-point minimal prompting**

Naomi's rescue from the mech needed to convey danger, the immense weight of the mech, Naomi's physical capability and fearlessness — without losing her grace and vulnerability.

The team opted for less strict prompting, giving the model more creative control by specifying only key anchor points:

> We wanted to convey a sense of danger, the massive weight of the mech, and Naomi's physicality and fearlessness — without losing her grace and vulnerability.

The model filled in the action details within those constraints and produced something the team couldn't have generated with precise frame-by-frame description.

**Engineering assumption**: *In complex action sequences, overly precise prompts compress the model's creative space and produce stiffness. Specifying the desired outcome (emotion/physical result) rather than the process yields more natural motion.*

---

### What's Open-Sourced

*ZEPHYR: Special* has published **197 assets**, including:

- All prompts used (no exceptions)
- Final cuts that made the edit
- Failed takes and bloopers — including dead-end approaches
- Character reference sheets (including special states like the inverted sheet)

Anyone can open the project in Higgsfield Cinema Studio and see the complete generation history, from the first draft to the final version.

---

### Episode 1 Engineering Lessons (Seedance 2.0)

The team also shared lessons from the original Zephyr episode (made on Seedance 2.0, when they were still establishing the pipeline).

**The mech character sheet trap**

Initial approach: a single "master sheet" showing all mech details — weapons, cockpit mechanism, all states.

Problem: *if the model sees a detail, it will try to show that detail.* The open hatch mechanism, visible on the character sheet as a state illustration, kept appearing even in scenes where the hatch should have been closed. The two states conflicted, deforming the overall mech design.

Solutions:
1. **Separate character sheets per state**: maintain distinct sheets for weapons retracted vs. extended. Only include the weapon on a sheet when it appears in the scene.
2. **Close-ups as standalone inputs**: for specific weapon operations (Mira's flamethrower extending), upload a close-up of just that component as a separate input — don't rely on the model zooming into a full-body sheet.
3. **Text annotations on character sheets are nearly useless**: labels like "retractable revolver in arm" don't get interpreted as instructions. You still need to describe the full weapon action in the prompt.

**Style prefix discipline**

Episode 1 lacked a unified style prefix, leading to visual inconsistency across scenes. Recommendation: establish a consistent style prefix (lighting style, color temperature, camera language) before production begins, and open every prompt with it.

---

### Character Creation Pipeline

Three stages:

**Stage 1 — Character development**: brainstorm with Higgsfield Supercomputer or Claude. The team explicitly says: "you can easily get that foundational layer of depth just by brainstorming with AI — don't let a lack of knowledge stand in the way." Knowing a character's personality is also a generation guide: it makes it far easier to write their acting, reactions, and story arcs.

**Stage 2 — Costume and appearance**: Higgsfield Soul 2 for character and costume creation. Soul 2's fashion capabilities handle any style combination, making it ideal for the idol × warrior aesthetic.

**Stage 3 — Character sheet refinement**: Nano Banana 2 Pro and Seedream to compile and refine designs into final reference sheet assets.

---

### What Seedance 2.5 Changed

*Zephyr* Episode 1 was built on Seedance 2.0 (just released, heavy experimentation). *Special* runs on Seedance 2.5. The team describes the difference directly:

> Today, AI creators are gaining an experience working with actors that closely mirrors being on an actual set. Technical workarounds and wrestling with models are taking a backseat.

The two "impossible shots" were achievable without compromise specifically because Seedance 2.5's character consistency and scene control had advanced far enough to execute them.

---

### The Platform Stack

Higgsfield is building an AI-native content production platform, not just a generation tool:

| Tool | Role |
|------|------|
| Cinema Studio | Scene control, project management, full generation history |
| Soul 2 | Character / costume design |
| Nano Banana 2 Pro | Image refinement |
| Seedream | Character sheet compilation |
| Seedance 2.5 | Primary video generation model (ByteDance) |
| Supercomputer | AI-assisted brainstorming |
| Academy | Production pipeline courses (free) |

**Hell Grind** (also open-sourced simultaneously) provides another reference point: 365,561 views, 115,446 generations, 3,138 public assets — a complete parallel production case study.

The **Higgsfield Global Film Festival** ($1M prize pool) is running now. The timing of these open-source releases is deliberate: share the production craft to help entrants understand what separates technically accomplished AI filmmaking from content generation.

---

### Seven Engineering Principles

Extracted from the full Zephyr open-source project:

1. **Encode physics in the input, not the prompt** — inverted character sheet technique
2. **Complex action scenes: anchor points, not process description** — let the model fill in movement details
3. **Multi-state character sheets** — separate sheet for each important state (retracted/extended/special)
4. **Close-up inputs for detail operations** — don't expect the model to zoom into a full-body sheet
5. **Style prefix for visual coherence** — establish consistent lighting/tone/camera language before production
6. **Character first, then generation** — personality drives performance, reactions, and arc
7. **Publish the failures** — bloopers reveal where the real engineering problems were, more clearly than successes do

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
