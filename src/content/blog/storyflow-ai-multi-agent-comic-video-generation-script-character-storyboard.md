---
title: "StoryFlow AI：7 个 Agent 流水线，一段文字变成一部完整漫剧 MP4"
titleEn: "StoryFlow AI: 7-Agent Pipeline Turns a Paragraph into a Full Comic Drama MP4"
description: "xiaozhang-art/storyflow-ai 开源，Multi-Agent 漫剧自动生成平台，7 步 Agent 流水线（剧本→角色→分镜→图片/配音并行→图生视频→合成），含 Director 决策引擎、断点续传、Montage 渲染引擎，Docker Compose 一键部署。"
descriptionEn: "xiaozhang-art/storyflow-ai is an open-source multi-agent comic drama generation platform. 7-step agent pipeline (script→character→storyboard→image/voice parallel→i2v→compose), with Director LLM decision engine, checkpoint resume, and Montage rendering engine. One Docker Compose deploy."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["multi-agent", "video generation", "AI", "open source", "comic", "LLM", "FastAPI", "Docker"]
heroImage: "../../assets/images/storyflow-ai-multi-agent-comic-video-generation-script-character-storyboard-banner.jpg"
author: "Mycelium Protocol"
---

## 一段文字进去，一部漫剧出来

**StoryFlow AI**（`xiaozhang-art/storyflow-ai`）是一个 Multi-Agent Workflow 平台，目标是一件事：输入创意文字，自动完成剧本、角色设计、分镜、图片生成、图生视频、配音、视频剪辑全流程，输出完整 MP4 漫剧视频。

不是 demo，是一个带生产级 Runtime 的完整开源平台。

---

## 7 个 Agent 的流水线

```
创意文字
  ↓
Script Agent ── 剧本（大纲 + 角色 + 分集剧本）
  ↓
Character Agent ── 角色视觉化设计（4 维外貌描述）
  ↓
Storyboard Agent ── 分镜（镜头 + 时长 + 画面 + 台词）
  ↓
Image Agent          Voice Agent   ← 并行执行
（场景图片生成）    （多供应商 TTS 配音）
  ↓                      ↓
Image-to-Video Agent     ↓
  ↓                      ↓
        Video Agent ← 合并
（转场拼接 + 字幕 + BGM + 音频合成）
        ↓
     story.mp4
```

Image-to-Video 和 Voice 两路并行，减少总生成时间。整个流程通过 YAML DSL 工作定义文件（`workflows/comic.yaml`）驱动——你可以直接改 YAML 调整步骤顺序、并行组、质量门控。

---

## Runtime：不只是串联 API

StoryFlow AI 最有工程价值的部分是它的 **Runtime 层**，这不是简单的 for 循环调用 API，而是一套完整的 Agent 执行基础设施：

### Director：LLM 决策大脑

每步执行后，Director 分析所有产出物，做出 6 种决策之一：

| 决策 | 含义 |
|---|---|
| `PROCEED` | 继续下一步 |
| `RETRY` | 重试当前步骤 |
| `ROLLBACK` | 回退到更早的步骤重新执行 |
| `REWRITE_PROMPT` | 重写 Prompt 后重试 |
| `SKIP` | 跳过当前步骤 |
| `INSERT_STEP` | 插入修复步骤 |

角色图片生成质量不达标？Director 决策 `REWRITE_PROMPT`，自动重写角色描述再试一次。分镜逻辑断裂？`ROLLBACK` 回到 Storyboard Agent 重新拆解。默认关闭，通过 `ENABLE_DIRECTOR=true` 启用。

### 其他 Runtime 组件

- **AgentConversationBus**：Agent 间结构化通信（A2A），携带角色档案、约束、质量反馈
- **StoryMemory**：多维记忆系统（场景/视觉/风格/世界/角色/时间线），保证跨 Agent 的一致性
- **QualityEngine**：剧本/角色/分镜/图片/配音各层质量门控，每层都有通过标准
- **ModelRouter**：按场景智能选择 LLM 模型（生成剧本用 GPT-4o，做简单格式化用更便宜的模型）
- **SessionManager + ArtifactManager**：会话追踪 + 产物存储，支持**断点续传**和**单步重跑**

---

## Montage 渲染引擎

视频合成层从 [OpenMontage](https://github.com/calesthio/OpenMontage) 提取，通过 `montage_adapter.py` 单点桥接，与业务逻辑完全解耦：

| 组件 | 能力 |
|---|---|
| **TTSEngine** | 5 供应商自动选择 + 静默降级（OpenAI → DashScope → ElevenLabs → Google → Piper） |
| **SubtitleEngine** | SRT/VTT 生成，词级时间轴对齐 |
| **AudioMixer** | 多轨混合 / sidechain ducking / BGM 分段配乐 / loudnorm |
| **VideoComposer** | 转场拼接 + 字幕烧录 + 多音轨合成 + 7 步质量检测 |
| **MediaProfiles** | YouTube / TikTok / Instagram / LinkedIn / Cinematic 等 10 种输出预设 |

通过 `MONTAGE_ENABLED=false` 可降级为原始 FFmpeg 实现，不依赖 Montage。

---

## 外部服务：全部有降级

每个依赖外部 API 的层都有完整的 fallback 链：

```
TTS:        OpenAI → DashScope → ElevenLabs → Google → Piper → 静默占位
图片生成:   DashScope 通义万相 → DALL-E 3 → Mock
图生视频:   Kling → Runway → FFmpeg 静态图转视频
视频合成:   Montage 引擎 → Legacy FFmpeg concat
Agent失败:  tenacity 3次重试 → Director 决策(SKIP/ROLLBACK)
```

不会因为某一个 API 不可用就整体崩掉。

---

## 快速部署

### Docker Compose（推荐）

```bash
git clone https://github.com/xiaozhang-art/storyflow-ai.git
cd storyflow-ai/deploy

cp .env.example .env
# 编辑 .env，最少填 LLM_API_KEY 和 LLM_BASE_URL

docker compose up -d
```

三个服务：PostgreSQL、Redis、Backend（内置 FFmpeg）。

### 本地开发

```bash
# 只起基础设施
cd deploy && docker compose up -d postgres redis && cd ..

# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend && npm install && npm run dev
```

### 最小配置（只需 LLM）

```env
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1   # 任意 OpenAI 兼容地址
LLM_MODEL=gpt-4o
```

图片、视频、语音都有 Mock 降级，只配 LLM 就能走完整个流程（图片用占位图）。

---

## 核心 API

```bash
# 创建故事
POST /api/story
{"title": "星际侦探", "description": "2087年，..."}

# 启动生成（异步，WebSocket 推进度）
POST /api/story/{id}/generate

# 实时进度
WS /api/task/{id}/ws

# 查看结果
GET /api/story/{id}/result
# 返回：video_url + 剧本 + 角色 + 分镜

# 断点续传
GET /api/story/{id}/checkpoints
POST /api/story/{id}/resume {"checkpoint_id": "..."}

# 单步重跑
POST /api/runtime/session/{id}/rerun/{step}
```

---

## 适合哪些场景

**内容创作者**：短剧/微剧创作，特别是漫改类内容。输入 IP 故事梗概，自动生成分镜和画面，大幅压缩从创意到视频的时间。

**开发者/研究者**：StoryFlow Runtime 是一个完整的 Multi-Agent 执行框架参考实现——Director 决策、Agent 间消息总线、多维记忆、质量门控、断点续传——可以拆出来用于其他多步 Agent 场景。

**企业内容团队**：10 种媒体输出预设（YouTube/TikTok/Instagram/Cinematic……）+ Docker Compose 部署，可以接入内部内容流水线。

---

## 技术栈一览

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite 5 + Ant Design 5 |
| 后端 | Python 3.11+ / FastAPI 4.0 / SQLAlchemy 2.0 (async) |
| LLM | OpenAI 兼容 API（GPT-4o / Qwen / DeepSeek） |
| 图片 | 通义万相 / DALL-E 3 |
| 图生视频 | Kling / Runway |
| 配音 | OpenAI TTS / CosyVoice / ElevenLabs / Google / Piper |
| 视频合成 | FFmpeg + Montage VideoComposer |
| 数据库 | PostgreSQL 16 (asyncpg) |
| 缓存/消息 | Redis 7 (PubSub) |
| 部署 | Docker Compose |

---

## 总结

StoryFlow AI 的工程密度比一般"AIGC 工具"高出一个量级：7 Agent 流水线本身只是前台，后面还有一整套 Runtime（Director 决策、多维记忆、质量门控、断点续传、多级降级）在撑着。对于想做 AI 内容自动化、或者研究 Multi-Agent 架构的团队，这是一个值得深读的完整参考实现。

**GitHub**: [xiaozhang-art/storyflow-ai](https://github.com/xiaozhang-art/storyflow-ai)  
**部署**: `docker compose up -d`（三服务，含 FFmpeg）

<!--EN-->

## StoryFlow AI: 7-Agent Pipeline Turns a Paragraph into a Full Comic Drama MP4

**StoryFlow AI** (`xiaozhang-art/storyflow-ai`) is a Multi-Agent Workflow platform with one purpose: input creative text, automatically complete scriptwriting, character design, storyboarding, image generation, image-to-video, voice synthesis, and video editing — output a complete MP4 comic drama.

Not a demo. A complete open-source platform with a production-grade Runtime.

### 7-Agent Pipeline

```
Creative text
  ↓
Script Agent (outline + characters + episodic script)
  ↓
Character Agent (4-dimension visual design)
  ↓
Storyboard Agent (shots + duration + scene + dialogue)
  ↓
Image Agent          Voice Agent    ← parallel
(scene images)       (multi-vendor TTS)
  ↓                      ↓
Image-to-Video Agent     ↓
  ↓                      ↓
        Video Agent ← merge
(transition + subtitles + BGM + audio mix)
        ↓
     story.mp4
```

Image-to-Video and Voice run in parallel to reduce total generation time. The entire pipeline is driven by a YAML DSL workflow definition (`workflows/comic.yaml`) — edit the YAML to adjust step order, parallel groups, and quality gates.

### Runtime: More Than Chained API Calls

The most engineered part of StoryFlow AI is its **Runtime layer** — not a simple for-loop calling APIs, but a complete Agent execution infrastructure.

**Director**: After each step, an LLM or rule engine analyzes all outputs and makes one of six decisions: `PROCEED`, `RETRY`, `ROLLBACK`, `REWRITE_PROMPT`, `SKIP`, or `INSERT_STEP`. Character image quality fails? Director rewrites the prompt and retries. Storyboard logic breaks? Rollback to the Storyboard Agent. Off by default, enabled via `ENABLE_DIRECTOR=true`.

**Other Runtime components**:
- **AgentConversationBus**: Structured A2A messages between agents carrying character profiles, constraints, and quality feedback
- **StoryMemory**: Multi-dimensional memory (scene/visual/style/world/character/timeline) ensuring cross-agent consistency
- **QualityEngine**: Quality gates at each layer (script/character/storyboard/image/voice) with explicit pass criteria
- **ModelRouter**: Intelligent model selection by task (GPT-4o for script generation, cheaper models for simple formatting)
- **SessionManager + ArtifactManager**: Session tracking + artifact storage, supporting **checkpoint resume** and **single-step re-run**

### Montage Rendering Engine

The video composition layer is extracted from OpenMontage, bridged via a single `montage_adapter.py`, fully decoupled from business logic:

- **TTSEngine**: 5-vendor auto-selection + silent fallback (OpenAI → DashScope → ElevenLabs → Google → Piper)
- **AudioMixer**: Multi-track mixing / sidechain ducking / segmented BGM / loudnorm
- **VideoComposer**: Transition stitching + subtitle burning + multi-track audio + 7-step quality check
- **MediaProfiles**: 10 output presets: YouTube / TikTok / Instagram / LinkedIn / Cinematic, and more

Set `MONTAGE_ENABLED=false` to fall back to raw FFmpeg — no Montage dependency.

### Full Fallback Chain for Every External Service

```
TTS:      OpenAI → DashScope → ElevenLabs → Google → Piper → silent placeholder
Images:   DashScope Wanxiang → DALL-E 3 → Mock
I2V:      Kling → Runway → FFmpeg static-image video
Video:    Montage → Legacy FFmpeg concat
Agents:   tenacity 3 retries → Director SKIP/ROLLBACK
```

### Quick Deploy

```bash
git clone https://github.com/xiaozhang-art/storyflow-ai.git
cd storyflow-ai/deploy
cp .env.example .env
# Set LLM_API_KEY and LLM_BASE_URL at minimum
docker compose up -d
```

Three services: PostgreSQL, Redis, Backend (FFmpeg included). Minimum config is just an LLM key — every other API has a mock/fallback so you can run the full pipeline.

### Who It's For

**Content creators**: Short-drama / webtoon production. Input a story synopsis, get storyboards and visuals. Compresses the creative-to-video cycle.

**Developers / researchers**: The StoryFlow Runtime is a complete multi-agent execution framework reference implementation — Director decisions, Agent message bus, multi-dimensional memory, quality gates, checkpoint resume. Extractable for other multi-step agent use cases.

**Enterprise content teams**: 10 media output presets (YouTube/TikTok/Instagram/Cinematic…) + Docker Compose = ready to integrate into internal content pipelines.

StoryFlow AI's engineering density is a full level above the average "AIGC tool." The 7-agent pipeline is just the front stage; behind it is a full Runtime infrastructure. For teams building AI content automation or studying multi-agent architecture, this is a complete reference worth reading in depth.

**GitHub**: [xiaozhang-art/storyflow-ai](https://github.com/xiaozhang-art/storyflow-ai)  
**Deploy**: `docker compose up -d` (3 services, FFmpeg included)
