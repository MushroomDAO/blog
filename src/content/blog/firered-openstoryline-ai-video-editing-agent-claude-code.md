---
title: "FireRed-OpenStoryline：用对话剪视频，把剪辑工作流存成可复用的 Skill"
titleEn: "FireRed-OpenStoryline: Conversational AI Video Editing Agent with Reusable Style Skills"
description: "FireRedTeam 开源的 AI 视频剪辑 Agent，自然语言驱动从素材搜集到成片全流程。核心亮点：编辑工作流可存为 Skill 复用，支持 Claude Code /openstoryline-use 直接调用。3141 stars，Apache 2.0。"
descriptionEn: "FireRedTeam's open-source AI video editing agent drives the entire pipeline — from media sourcing to final cut — through natural language. Standout feature: editing workflows save as reusable Skills, with native Claude Code /openstoryline-use integration. 3141 stars, Apache 2.0."
pubDate: "2026-07-23"
updatedDate: "2026-07-23"
category: "Tech-Experiment"
tags: ["AI视频", "视频剪辑", "Agent", "Claude Code", "LangChain", "MCP", "开源", "内容创作"]
heroImage: "../../assets/images/firered-openstoryline-ai-video-editing-agent-claude-code-banner.jpg"
---

> **仓库**：FireRedTeam/FireRed-OpenStoryline · Python · Apache 2.0 · 3141 stars  
> **开源时间**：2026-02-10  
> **Demo**：fireredteam-firered-openstoryline.hf.space  
> **ModelScope**：modelscope.cn/studios/FireRedTeam/FireRed-OpenStoryline

---

## 一、做什么

FireRed-OpenStoryline 把视频剪辑变成一个对话任务。

不是给专业剪辑软件加 AI 助手，而是从头设计一个 Agent——你描述想要的效果，Agent 负责搜素材、写脚本、剪片、配音、配乐、调字体颜色，所有操作都通过自然语言。

支持的风格覆盖主流短视频场景：种草、开箱、搞笑、好物推荐、宠物说话、旅行 Vlog、年度回顾、艺术风。

---

## 二、五个核心能力

### 1. 智能媒体搜索与组织

自动联网下载符合主题的图片和视频素材，做片段分割和内容理解，按主题整理。

### 2. 脚本生成 + Few-shot 风格迁移

结合用户主题、视觉理解、情绪识别自动生成旁白。**重点**：内置 Few-shot 风格迁移——给出参考文案样本，系统能精确复制其语气、节奏和句式。

```
# 例：给 Agent 一段参考文案
"用这个文案的风格帮我写一段产品介绍脚本，像小红书种草那种"
```

### 3. 音乐 / 配音 / 字体推荐

描述情感基调（"克制"、"情感浓郁"、"纪录片风格"），系统自动匹配配乐和配音风格，支持智能节拍同步，支持导入个人歌单。

### 4. 对话式精修

所有精修操作通过自然语言完成：

```
"把第 3 段换成另一个视角的素材"
"把字幕颜色改成白色，移到画面下方 1/4 处"
"把背景音乐再轻一点，突出配音"
"把开头 5 秒剪掉"
```

### 5. 编辑技能存档（Skill Archiving）

这是最有价值的功能之一：把完整的剪辑工作流保存为一个自定义 Skill，换素材后一键复现同款风格。

如果你做的是固定格式的批量内容（同一 IP 的系列视频、固定风格的产品评测），这个功能把重复工作量从线性变成常数。

---

## 三、近期新增功能

**AI 转场生成**（2026-04-02）：根据前一段的末尾帧、下一段的开头帧和自然语言描述，自动生成转场镜头。让场景切换更自然、叙事更连贯。注意：成本相对高，按需开启。

**ASR 粗剪**（2026-03-22）：语音视频专用。自动识别并删除口头语（"嗯"、"那个"）、重复句和停顿，生成对齐时间戳的片段，减少手动粗剪的工作量。

---

## 四、Claude Code 集成

项目内置了两个 Claude Code Skills：

```bash
/openstoryline-install   # 安装、配置、验证环境
/openstoryline-use       # 启动服务、运行剪辑工作流
```

**从项目目录启动 Claude Code**（最简方式）：

```bash
git clone https://github.com/FireRedTeam/FireRed-OpenStoryline.git
cd FireRed-OpenStoryline
claude  # 启动后直接可用 /openstoryline-install
```

**全局安装**（任意目录可用）：

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/openstoryline-install ~/.claude/skills/
cp -R .claude/skills/openstoryline-use ~/.claude/skills/
```

**其他 Agent（Codex 等）**：

```bash
npx skills add FireRedTeam/FireRed-OpenStoryline --skill openstoryline-install
npx skills add FireRedTeam/FireRed-OpenStoryline --skill openstoryline-use
```

---

## 五、快速上手

```bash
# 1. 克隆 + 环境
git clone https://github.com/FireRedTeam/FireRed-OpenStoryline.git
cd FireRed-OpenStoryline
conda create -n storyline python=3.11 && conda activate storyline
sh build_env.sh   # 自动下载模型和资源（macOS/Linux）

# 2. 配置 API Key（config.toml）
# 详见 docs/source/en/api-key.md

# 3. 启动 MCP Server
PYTHONPATH=src python -m open_storyline.mcp.server

# 4. 选界面：CLI 或 Web
python cli.py
# 或
uvicorn agent_fastapi:app --host 127.0.0.1 --port 8005
```

也可以用 Docker：

```bash
docker pull openstoryline/openstoryline:v1.0.1
docker run -v $(pwd)/config.toml:/app/config.toml \
           -v $(pwd)/outputs:/app/outputs \
           -p 7860:7860 openstoryline/openstoryline:v1.0.1
```

---

## 六、架构

```
用户自然语言
  → LangChain Agent（规划 + 工具编排）
    → MCP Server（工具接口层）
      → Video Processing Nodes（MoviePy + FFmpeg）
      → Media Search（联网素材获取）
      → Script Engine（LLM + few-shot 风格迁移）
      → ASR（本地/云端语音识别）
    → Storage（Agent Memory + Skill 存档）
```

---

## 七、判断

Few-shot 风格迁移和 Skill 存档是这个项目里最值得关注的两个设计。

**风格迁移**解决的是「AI 写的文案不像我的风格」这个问题。不是让模型猜，而是给几个例子让它学——对固定风格创作者来说，这个功能让 AI 文案从「凑合用」变成「可以直接发」。

**Skill 存档**解决的是「每次都要重新配置」的问题。做固定格式内容的人（比如 Vlog 系列、产品评测系列）有统一的剪辑风格——色调、节奏、字体、BGM 风格。把这套风格存成 Skill，下次换素材直接调用，剪辑工作量大幅压缩。

ASR 粗剪是对说话类视频最直接的提效工具。讲解、教程、访谈类内容里，自动去掉停顿和口头语是实实在在节省时间的操作。

目前整体处于 Agent 驱动的探索阶段，复杂任务的稳定性和成品质量取决于底层 LLM 和素材质量。3141 stars 对一个 2 月开源的项目来说增长很快，说明这个方向有真实需求。

---

*数据来源：GitHub FireRedTeam/FireRed-OpenStoryline，2026-07-23 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: FireRedTeam/FireRed-OpenStoryline · Python · Apache 2.0 · 3141 stars  
> **Open-sourced**: 2026-02-10  
> **Demo**: fireredteam-firered-openstoryline.hf.space  
> **ModelScope**: modelscope.cn/studios/FireRedTeam/FireRed-OpenStoryline

---

## 1. What It Does

FireRed-OpenStoryline turns video editing into a conversational task.

Rather than bolting an AI assistant onto professional editing software, it designs an Agent from the ground up — you describe the effect you want, and the Agent handles sourcing footage, writing the script, cutting the video, adding voiceover, selecting music, and adjusting fonts and colors, all through natural language.

Supported styles cover the main short-video formats: product recommendation, unboxing, comedy, product reviews, talking-pet videos, travel vlogs, year-in-review, and artistic style.

---

## 2. Five Core Capabilities

### 1. Intelligent Media Search and Organization

Automatically fetches images and video clips from the internet that match the theme, performs shot segmentation and content understanding, and organizes them by topic.

### 2. Script Generation + Few-Shot Style Transfer

Automatically generates narration by combining the user's theme, visual understanding, and emotion recognition. **Key feature**: built-in few-shot style transfer — provide a few reference copy samples and the system can precisely replicate their tone, rhythm, and sentence structure.

```
# Example: give the Agent a reference copy sample
"Write a product introduction script in the style of this copy, like a Xiaohongshu recommendation post"
```

### 3. Music / Voiceover / Font Recommendations

Describe the emotional tone ("restrained", "emotionally rich", "documentary style") and the system automatically matches background music and voiceover style, with intelligent beat synchronization and support for importing personal playlists.

### 4. Conversational Refinement

All refinement operations are completed through natural language:

```
"Replace segment 3 with footage from a different angle"
"Change the subtitle color to white and move it to the lower quarter of the frame"
"Bring the background music down a bit to let the voiceover stand out"
"Cut the first 5 seconds"
```

### 5. Skill Archiving

One of the most valuable features: save a complete editing workflow as a custom Skill, then reproduce the same style with new footage in one click.

If you produce batch content in a fixed format (a video series under the same IP, product reviews with a consistent style), this feature converts repetitive work from a linear burden into a constant one.

---

## 3. Recent Feature Additions

**AI Transition Generation** (2026-04-02): Based on the last frame of the preceding segment, the first frame of the next segment, and a natural-language description, automatically generates transition shots. Makes scene cuts smoother and narrative more coherent. Note: relatively high cost — enable on demand.

**ASR Rough Cut** (2026-03-22): Designed for spoken-word video. Automatically identifies and removes filler words ("um", "like"), repeated sentences, and pauses, generating timestamp-aligned segments that reduce manual rough-cut work.

---

## 4. Claude Code Integration

The project ships two built-in Claude Code Skills:

```bash
/openstoryline-install   # Install, configure, and verify the environment
/openstoryline-use       # Start the service and run editing workflows
```

**Launch Claude Code from the project directory** (simplest approach):

```bash
git clone https://github.com/FireRedTeam/FireRed-OpenStoryline.git
cd FireRed-OpenStoryline
claude  # /openstoryline-install is available immediately after launch
```

**Global installation** (available from any directory):

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/openstoryline-install ~/.claude/skills/
cp -R .claude/skills/openstoryline-use ~/.claude/skills/
```

**Other agents (Codex, etc.)**:

```bash
npx skills add FireRedTeam/FireRed-OpenStoryline --skill openstoryline-install
npx skills add FireRedTeam/FireRed-OpenStoryline --skill openstoryline-use
```

---

## 5. Quick Start

```bash
# 1. Clone + environment
git clone https://github.com/FireRedTeam/FireRed-OpenStoryline.git
cd FireRed-OpenStoryline
conda create -n storyline python=3.11 && conda activate storyline
sh build_env.sh   # automatically downloads models and resources (macOS/Linux)

# 2. Configure API Key (config.toml)
# See docs/source/en/api-key.md for details

# 3. Start MCP Server
PYTHONPATH=src python -m open_storyline.mcp.server

# 4. Choose interface: CLI or Web
python cli.py
# or
uvicorn agent_fastapi:app --host 127.0.0.1 --port 8005
```

Docker is also available:

```bash
docker pull openstoryline/openstoryline:v1.0.1
docker run -v $(pwd)/config.toml:/app/config.toml \
           -v $(pwd)/outputs:/app/outputs \
           -p 7860:7860 openstoryline/openstoryline:v1.0.1
```

---

## 6. Architecture

```
User natural language
  → LangChain Agent (planning + tool orchestration)
    → MCP Server (tool interface layer)
      → Video Processing Nodes (MoviePy + FFmpeg)
      → Media Search (online media retrieval)
      → Script Engine (LLM + few-shot style transfer)
      → ASR (local/cloud speech recognition)
    → Storage (Agent Memory + Skill Archive)
```

---

## 7. Assessment

Few-shot style transfer and Skill archiving are the two design choices most worth paying attention to in this project.

**Style transfer** addresses the problem of "AI-written copy that doesn't sound like my voice." Instead of having the model guess, you give it a few examples to learn from — for creators with a consistent style, this elevates AI-generated copy from "good enough" to "ready to publish."

**Skill archiving** addresses the problem of "having to reconfigure everything from scratch each time." Creators producing fixed-format content (Vlog series, product review series) have a unified editing style — color grading, pacing, fonts, BGM style. Saving that style as a Skill lets you load it directly next time you have new footage, dramatically compressing the editing workload.

ASR rough-cut is the most direct efficiency tool for spoken-word video. For explanatory videos, tutorials, and interviews, automatically removing pauses and filler words is a genuine time-saver.

The project is currently in an exploratory, Agent-driven phase — the stability of complex tasks and the quality of the final output depend on the underlying LLM and the quality of the source material. 3141 stars for a project open-sourced in February is fast growth, signaling real demand for this direction.

---

*Data source: GitHub FireRedTeam/FireRed-OpenStoryline, collected 2026-07-23.*

© 2026 Author: Mycelium Protocol
