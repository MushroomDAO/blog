---
title: "镜探 + Avatar Forge：从拆解爆款到数字人口播，Agent Skill 组合完成整条视频创作流水线"
titleEn: "CineSleuth + Avatar Forge: From Film Analysis to Digital Human Video — Agent Skills for the Full Creator Pipeline"
description: "LycheeAILab 的两个开源 Agent Skill：CineSleuth（镜探）负责逐帧拆解视频、提取台词场景镜头和创作意图；Avatar Forge 负责把文案、图片和声音变成完整的数字人口播视频。两者组合，形成「看懂爆款 → 提炼改写 → 数字人演绎」的完整视频创作流水线。"
descriptionEn: "Two open-source Agent Skills from LycheeAILab: CineSleuth breaks down any video frame-by-frame, extracting transcripts, scenes, shots, and creative intent; Avatar Forge turns scripts, photos, and voices into full digital human videos. Together they form a complete 'analyze viral content → rewrite → produce with digital human' creator pipeline."
pubDate: 2026-09-04
updatedDate: 2026-09-04
category: Tech-Experiment
tags: ["AI", "视频创作", "数字人", "Agent Skill", "Codex", "WorkBuddy", "拉片", "口播", "LycheeAILab"]
heroImage: "../../assets/images/avatar-forge-cine-sleuth-video-digital-human-agent-skill-banner.jpg"
author: "Mycelium Protocol"
---

视频创作有两个最耗时的环节：**把一条好视频真正看懂**，以及**把一个想法真正演出来**。

LycheeAILab 用两个开源 Agent Skill 分别解决了这两件事：

- **[镜探 / CineSleuth](https://github.com/LycheeAILab/cine-sleuth)**：把视频交给 Agent，说一句你想分析什么，它自动提取台词、重建场景、拆解镜头，完成全片理解
- **[Avatar Forge](https://github.com/LycheeAILab/avatar-forge)**：一张人物图片 + 一段已授权声音 + 一份口播稿，生成完整的数字人口播视频

单独用，各自解决一个问题。组合起来，就是一条从「看懂爆款」到「数字人演绎」的完整视频创作流水线。

---

## 镜探（CineSleuth）：让 Agent 真正读懂一条视频

### 它在解决什么

「拉片」是电影圈的专业术语：把一条视频逐帧、逐镜地仔细研究，提取其中的创作逻辑。

做内容的人都知道它有多价值——真正把一条爆款拉透，等于把它的创作方法论学到手。但传统拉片极耗时：要手动打时间码、记台词、标场景、分析镜头语言，一条 3 分钟的视频可能要花 2 小时。

CineSleuth 把这件事交给 Agent 做。

### 七种分析能力

| 能力 | 输入 | 交付 |
|------|------|------|
| **台词取证** | 本地视频 | 逐句台词、说话人、语气、字幕差异与精确时间码 |
| **逐镜拆解** | 想关注的维度（导演/摄影/剪辑）| 景别、角度、运动、转场、人物动作与画面文字 |
| **场景重建** | 任意视频 | 物理场景、镜头和内容段落的清晰区分 |
| **声音分析** | 原始音轨 | 人声、音乐、环境声、音效、静音与声画关系 |
| **结构分析** | 分析目标 | 开场钩子、节奏、信息密度、情绪推进与 CTA |
| **镜头提示词** | 视频中每个画面 | 逐镜生成可直接用于视频生成的中文提示词 |
| **长视频拉片** | 最长 5 分钟视频 | 本地智能切分、断点续跑、跨片段合并与完整报告 |

### 一句话触发，不需要记命令

```text
使用 CineSleuth 完整拉片这个视频，输出逐句台词、物理场景、逐镜表和视听分析。
```

```text
使用 CineSleuth 拆解这条短视频的开场钩子、内容结构、节奏、字幕设计和声音设计。
```

```text
使用 CineSleuth 从导演和剪辑角度分析这部短片，重点说明每个镜头为什么放在这里。
```

### 技术架构

```
视频 → 本地媒体探测 → 语音边界 + 镜头边界 → 智能切片
     → 分段证据 → 全局时间线 → Agent 推理 → 完整拉片报告
```

关键设计：
- **本地切片**：时间码测量和分片在用户设备上完成，不上传原始视频片段
- **断点续跑**：已完成的片段保留进度，中断后只处理缺失部分
- **场景不等于切片**：技术分段不会自动制造新的场景，跨段场景由 Agent 根据地点、时间、人物连续性合并
- **证据先于结论**：每个判断都回到具体时间码，听不清 / 看不清时直接说明，不猜

---

## Avatar Forge：让数字人把文案「演出来」

### 它在解决什么

口播视频需要出镜。这件事有几个障碍：有些人不想出镜、没有专业拍摄条件、需要快速批量产出不同角色的内容。

Avatar Forge 的解法：一张清晰的人物图片 + 一段已授权的参考声音，创建你的专属数字人，然后把任何口播稿变成可以交付的视频。

也可以直接用内置的「丰富公模」快速起步——不需要提供自己的图片和声音。

### 五种核心能力

| 能力 | 输入 | 交付 |
|------|------|------|
| **丰富公模** | 文案或成品音频 | 快速数字人口播视频 |
| **专属数字人** | 一张清晰人物图片 | 可用于口播的个人数字人 |
| **声音克隆** | 一段已授权参考声音 | 专属音色与自然口播音频 |
| **视频文案再创作** | 上传视频或有权使用的抖音链接 | 原始转写稿 + 独立改写稿 |
| **创作工具组合** | 数字人视频与创作目标 | 接入 HyperFrames 或 ChatCut，完成字幕和剪辑 |

### 完整创作流

```
选择公模 ──────────────────────────→ 数字人口播视频
上传图片 → 专属数字人 ─────────────↗
参考声音 → 专属音色 ──────────────↗
上传/引用视频 → 提取原文案 → 改写新文案 ─(可选)→ 上述任意路径
数字人视频 → HyperFrames / ChatCut → 完整短视频成品
```

每个步骤都可以独立使用：只需要文案改写、只需要声音克隆、只需要生成一条视频——任意组合。

### 安全设计

- **费用确认**：未经用户明确确认，不提交可能产生费用的生成任务
- **声音授权**：只克隆本人声音或已明确授权的声音
- **抖音下载**：不读取 Edge/Chrome 登录态，不依赖 Windows DPAPI 或浏览器扩展
- **密钥不下发**：第三方服务凭据留在服务端，不进入仓库或日志
- **禁止冒充**：不得用于冒充他人或制作违法内容

---

## 两个 Skill 的组合工作流

用一个具体场景说明两者如何联动：

**目标**：看到一条爆款口播视频，想做一条同赛道的内容，用自己的数字人表达。

### 完整流程

```
Step 1 → CineSleuth 拉片爆款视频
         ↓ 输出：台词、场景结构、逐镜表、节奏分析、开场钩子、镜头提示词

Step 2 → Avatar Forge 「视频文案再创作」
         ↓ 输入：同一条视频（或 CineSleuth 提取的转写稿）
         ↓ 输出：原始转写稿 + 改写后的新文案（保持结构，内容原创）

Step 3 → Avatar Forge 生成数字人口播
         ↓ 输入：改写稿 + 专属数字人（或公模）+ 专属音色（或公模声音）
         ↓ 输出：完整数字人口播视频

Step 4 → HyperFrames / ChatCut 后期包装
         ↓ 字幕、配乐、B-roll、节奏剪辑、最终导出
```

**一句话指令版本**（在 Codex 或 WorkBuddy 里）：

```text
第一步：使用 CineSleuth 拆解这条视频的完整结构，输出台词、场景、逐镜表和开场钩子分析。
第二步：使用 Avatar Forge 从同一条视频提取原文案，并改写成 60 秒、自然口语风格的新稿。
第三步：确认改写稿后，使用 Avatar Forge 用我的专属数字人生成口播视频。
```

每个步骤独立确认，不自动串联——你可以在改写稿环节修改，在生成前调整数字人选择。

### 更多使用场景

**场景 A：快速复刻成功模版**
拿到任意一条自己有权分析的行业爆款 → CineSleuth 提取其结构模版 → Avatar Forge 用同样结构生成新内容

**场景 B：批量制作不同角色内容**
同一份改写稿 → Avatar Forge 切换不同公模 → 同一内容的多个数字人版本

**场景 C：纯分析用途**
只用 CineSleuth：学习某导演的镜头语言、研究某个广告的信息层次、提取某部短片的叙事节奏

**场景 D：纯创作用途**
只用 Avatar Forge：已有写好的文案和声音，直接生成数字人视频，不需要拉片

---

## 安装方式

两个 Skill 都支持 **Codex**（插件）和 **WorkBuddy**（Skill）。

### CineSleuth（镜探）

**Codex 自动安装**：
```text
阅读 https://raw.githubusercontent.com/LycheeAILab/cine-sleuth/main/INSTALL.md，
帮我安装或升级 CineSleuth 插件并创建一个新任务。
```

**WorkBuddy**：
下载 [cine-sleuth-workbuddy-1.0.3.zip](https://github.com/LycheeAILab/cine-sleuth/releases/download/v1.0.3/cine-sleuth-workbuddy-1.0.3.zip)，在 Skills 页面上传。

### Avatar Forge

**Codex 自动安装**：
```text
阅读 https://raw.githubusercontent.com/LycheeAILab/avatar-forge/main/INSTALL.md，
帮我安装或升级 Avatar Forge。
```

**WorkBuddy**：
下载 [avatar-forge-workbuddy-2.2.0.zip](https://github.com/LycheeAILab/avatar-forge/releases/tag/v2.2.0)，在 Skills 页面上传。

两个 Skill 首次调用都会通过 `lab.lycheeai.com.cn` 完成授权，授权后本地只保存用户自己的可撤销 Lab API Key，底层服务凭据不会下发到客户端。

---

## 相关链接

- **CineSleuth**：[github.com/LycheeAILab/cine-sleuth](https://github.com/LycheeAILab/cine-sleuth)
- **Avatar Forge**：[github.com/LycheeAILab/avatar-forge](https://github.com/LycheeAILab/avatar-forge)
- **LycheeAILab**：[lab.lycheeai.com.cn](https://lab.lycheeai.com.cn)

<!--EN-->

Two bottlenecks define video creation: **truly understanding a great video**, and **actually producing your own**.

LycheeAILab's two open-source Agent Skills each solve one:

- **[CineSleuth / 镜探](https://github.com/LycheeAILab/cine-sleuth)**: Hand any video to an Agent, say what you want to understand — it automatically extracts transcripts, reconstructs scenes, breaks down shots, and delivers a full film analysis
- **[Avatar Forge](https://github.com/LycheeAILab/avatar-forge)**: One photo + one authorized voice sample + one script → complete digital human video

Used alone, each solves a distinct problem. Used together, they form a complete pipeline: **analyze viral content → rewrite → produce with a digital human**.

---

## CineSleuth: Teaching an Agent to Actually Read a Video

### The Problem It Solves

"Film analysis" (拉片) is a professional practice: studying a video frame-by-frame, shot-by-shot, to extract its creative logic.

Any content creator knows its value — truly analyzing a viral video means extracting its production methodology. But traditional film analysis is brutal: manually logging timecodes, transcribing dialogue, labeling scenes, and analyzing cinematographic language. A 3-minute video can take 2 hours.

CineSleuth delegates this to an Agent.

### Seven Analysis Capabilities

| Capability | Input | Output |
|------------|-------|--------|
| **Transcript forensics** | Local video | Sentence-by-sentence dialogue, speaker ID, tone, caption discrepancies, exact timecodes |
| **Shot-by-shot breakdown** | Your analysis dimension (director / cinematography / editing) | Shot scale, angle, movement, transition, character action, on-screen text |
| **Scene reconstruction** | Any video | Clear separation of physical locations, shots, and content segments |
| **Sound analysis** | Original audio | Voice, music, ambience, effects, silence, audio-visual relationship |
| **Structure analysis** | Analysis target | Opening hook, pacing, information density, emotional arc, CTA |
| **Shot prompts** | Each frame in the video | Per-shot Chinese prompts ready for video generation |
| **Long video analysis** | Videos up to 5 minutes | Local intelligent segmentation, resume on interrupt, cross-segment merging, full report |

### One Sentence to Trigger, No Commands to Memorize

```text
Use CineSleuth to fully analyze this video — output line-by-line transcript, physical scenes, shot table, and audiovisual analysis.
```

```text
Use CineSleuth to break down this short video's opening hook, content structure, pacing, subtitle design, and sound design.
```

```text
Use CineSleuth to analyze this short film from a director and editor perspective — focus on why each shot is placed here.
```

### Technical Design

```
Video → Local media probe → Speech boundaries + Shot boundaries → Smart segmentation
      → Per-segment evidence → Global timeline → Agent reasoning → Full analysis report
```

Key design decisions:
- **Local slicing**: Timecode measurement and segmentation happen on-device; raw footage is not shipped off
- **Resume on interrupt**: Completed segments are saved; interrupted sessions only process missing parts
- **Scenes ≠ slices**: Technical segments don't auto-create new scenes; cross-segment scenes are merged by the Agent based on location, time, and character continuity
- **Evidence before conclusion**: Every judgment references a specific timecode; unclear audio/visual is flagged directly, never guessed

---

## Avatar Forge: Making the Digital Human Perform Your Script

### The Problem It Solves

Talking-head videos require someone on camera. Barriers: some people don't want to appear, professional recording setups are expensive, rapid batch production of multiple personas is impossible.

Avatar Forge's solution: one clear photo + one authorized voice sample → your own digital human that performs any script you give it.

Or skip the custom assets entirely and use the built-in library of ready-made digital humans for instant production.

### Five Core Capabilities

| Capability | Input | Output |
|------------|-------|--------|
| **Stock digital humans** | Script or produced audio | Quick digital human talking-head video |
| **Custom digital human** | One clear photo | A personal digital human ready for video production |
| **Voice cloning** | One authorized reference recording | Custom voice profile and natural talking-head audio |
| **Video script re-creation** | Local video or authorized Douyin link | Original transcript + independently rewritten script |
| **Tool integration** | Digital human video + creative goal | Hand off to HyperFrames or ChatCut for packaging and editing |

### Full Creation Flow

```
Choose stock avatar ─────────────────→ Digital human talking-head video
Upload photo → Custom digital human ─↗
Reference voice → Custom voice ──────↗
Upload/link video → Extract script → Rewrite script ─(optional)→ Any of the above
Digital human video → HyperFrames / ChatCut → Complete short video
```

Every step is independently usable — only need a script rewrite, only need voice cloning, only need one video — any combination works.

---

## The Combined Workflow

A concrete scenario: you find a viral talking-head video in your niche. You want to create your own content with the same structure, performed by your own digital human.

### Complete Pipeline

```
Step 1 → CineSleuth analyzes the viral video
         ↓ Output: transcript, scene structure, shot table, pacing analysis, hook breakdown, shot prompts

Step 2 → Avatar Forge "Video Script Re-creation"
         ↓ Input: the same video (or CineSleuth's transcript)
         ↓ Output: original transcript + independently rewritten script (same structure, original content)

Step 3 → Avatar Forge generates digital human video
         ↓ Input: rewritten script + custom digital human (or stock) + custom voice (or stock)
         ↓ Output: complete digital human talking-head video

Step 4 → HyperFrames / ChatCut for finishing
         ↓ Captions, music, B-roll, pacing edits, final export
```

**One-prompt version** (in Codex or WorkBuddy):

```text
Step 1: Use CineSleuth to break down the full structure of this video — output transcript, scenes, shot table, and opening hook analysis.
Step 2: Use Avatar Forge to extract the original script from the same video, then rewrite it into a 60-second, natural conversational style version.
Step 3: After I confirm the rewrite, use Avatar Forge to generate a talking-head video with my custom digital human.
```

Each step is individually confirmed — you can refine the rewrite before generation, and adjust digital human selection before committing.

### More Use Cases

**Case A: Quickly template successful formats**  
Take any video you have rights to analyze → CineSleuth extracts its structural template → Avatar Forge produces new content with the same structure

**Case B: Batch produce multi-persona content**  
Same rewritten script → Avatar Forge switches between different stock avatars → Multiple digital human versions of the same content

**Case C: Pure analysis**  
CineSleuth only: study a director's cinematographic language, research an ad's information hierarchy, extract a short film's narrative pacing

**Case D: Pure production**  
Avatar Forge only: already have a script and voice — generate the digital human video directly, no analysis needed

---

## Installation

Both Skills support **Codex** (plugin) and **WorkBuddy** (skill).

### CineSleuth

**Codex auto-install**:
```text
Read https://raw.githubusercontent.com/LycheeAILab/cine-sleuth/main/INSTALL.md,
and install or upgrade the CineSleuth plugin for me, then create a new task.
```

**WorkBuddy**: Download [cine-sleuth-workbuddy-1.0.3.zip](https://github.com/LycheeAILab/cine-sleuth/releases/download/v1.0.3/cine-sleuth-workbuddy-1.0.3.zip) and upload it on the Skills page.

### Avatar Forge

**Codex auto-install**:
```text
Read https://raw.githubusercontent.com/LycheeAILab/avatar-forge/main/INSTALL.md,
and install or upgrade Avatar Forge for me.
```

**WorkBuddy**: Download [avatar-forge-workbuddy-2.2.0.zip](https://github.com/LycheeAILab/avatar-forge/releases/tag/v2.2.0) and upload it on the Skills page.

Both Skills authorize via `lab.lycheeai.com.cn` on first use. After authorization, only your own revocable Lab API Key is stored locally — service-side credentials are never sent to the client.

---

## Links

- **CineSleuth**: [github.com/LycheeAILab/cine-sleuth](https://github.com/LycheeAILab/cine-sleuth)
- **Avatar Forge**: [github.com/LycheeAILab/avatar-forge](https://github.com/LycheeAILab/avatar-forge)
- **LycheeAILab**: [lab.lycheeai.com.cn](https://lab.lycheeai.com.cn)
