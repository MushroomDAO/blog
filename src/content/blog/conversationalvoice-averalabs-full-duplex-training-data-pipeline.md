---
title: "ConversationalVoice：把真实双人录音变成全双工训练数据的端到端流水线"
titleEn: "ConversationalVoice: End-to-End Pipeline for Turning Real Two-Person Recordings into Full-Duplex Training Data"
description: "avera-labs/ConversationalVoice，51 stars，BSL 1.1 许可证（非生产免费，生产环境商用需授权，4年后转 MIT）。AveraLabs 出品，配套 arXiv 2609.08147 论文。一条 9 阶段 Celery 流水线，将真实双人录音自动转成全双工语音模型训练数据，每段对话产出三类数据：分离 / 重建 / 扩写。内部使用 DialogueSidon（说话人分离）、Qwen3-ASR（转写）、Qwen3-TTS（语音合成）。需要 CUDA GPU + PostgreSQL + Redis + S3 存储。"
descriptionEn: "avera-labs/ConversationalVoice — 51 stars, BSL 1.1 license (non-production free; production commercial use requires authorization; converts to MIT in 4 years). By AveraLabs, with accompanying arXiv 2609.08147 paper. A 9-stage Celery pipeline that automatically converts real two-person recordings into full-duplex voice model training data, producing three complementary data types per conversation: Separation / Reconstruction / Expansion. Internally uses DialogueSidon (speaker separation), Qwen3-ASR (transcription), and Qwen3-TTS (voice synthesis). Requires CUDA GPU + PostgreSQL + Redis + S3 storage."
pubDate: 2026-09-22
heroImage: "../../assets/images/conversationalvoice-averalabs-full-duplex-training-data-pipeline-banner.jpg"
category: "Tech-Experiment"
tags: ["speech-ai", "full-duplex", "voice-ai", "training-data", "open-source", "pipeline", "asr"]
lang: zh-CN
---

全双工语音 AI 的训练数据问题，比模型架构问题更难解。AveraLabs 这篇工作直接切入数据稀缺这一卡点。

`avera-labs/ConversationalVoice` 是一条端到端的自动化流水线：输入是真实的双人对话录音，输出是可直接用于训练全双工语音模型的三类标注数据。有配套论文（arXiv 2609.08147）。

**GitHub**：github.com/avera-labs/ConversationalVoice | **Stars**：51 | **⚠️ License**：Business Source License 1.1 | **论文**：arxiv.org/abs/2609.08147

---

## 为什么训练数据是全双工的瓶颈

全双工（Full-Duplex）的意思是：AI 同时在听、同时在说，双向并行——可以被打断、可以在对方说话时插一句"嗯嗯"，就像真人对话。这不是 push-to-talk，不是 VAD 检测到静音再回复，是真正的双流并行。

训练全双工模型，需要的数据有严格要求：
- 每个说话人的音轨必须**分离**（不是混在一起的单声道）
- 时间轴必须完整保留（抢话、重叠、反馈声都在原位置）
- 量要足够大

现实是：公开语音数据约有 100 万小时，但几乎没有已分离成双轨且保留交互时序的对话录音。大部分真实双人录音都是单声道混合，两个人的声音纠缠在一起，用传统方法根本没法直接当训练数据。

这就是 ConversationalVoice 要解决的问题。

---

## 三类数据：每段对话产出三倍训练信号

流水线对每段输入录音，输出三类互补数据：

### 1. 分离（Separation）
从真实录音中恢复出每个说话人的独立音轨，同时保留：
- 稳定的说话人标识（说话人 A 和 B 始终对应同一个人）
- 规范化的转录文本
- **原始交互时序**：真实发生的停顿、重叠、打断、反馈声完全按原样保留

这是"最像真实对话"的数据，但音质受原始录音限制。

### 2. 重建（Reconstruction）
用声音克隆技术，对分离后的文本和说话人身份做**高质量重新合成**：
- 用 Qwen3-TTS 重新渲染同一段对话
- 加入词级对齐和语音风格指令
- 保留原始的说话顺序和重叠时序

结果：音质更好、更干净，是同一段对话的合成版本。

### 3. 扩写（Expansion）
在原始对话的说话人身份和交互模式约束下，**生成全新内容**：
- 新的话题和对话内容
- 保持同一对说话人的声音特征
- 按原始录音中的真实交互节奏生成

结果：同一对声音，新的对话，保留了真实对话的交互风格。

**实测交互率对比**（扩写 vs 重建）：扩写产生的对话轮次少 4.6%，重叠少 8.0%，反馈声少 13.2%，打断少 16.0%——扩写数据比重建略"整洁"，说明自由生成的对话天然比真实对话更规整。

---

## 9 阶段流水线架构

系统设计为独立 Celery worker 的分布式流水线，每个阶段对应一个专用队列，PostgreSQL 追踪全链路数据血缘：

| 阶段 | 功能 |
|------|------|
| 1. Ingest API | 标准化 WAV 生成 |
| 2. VAD 分割 | 识别对话窗口 |
| 3. 说话人日志化（Diarization） | 检测说话人轮次 |
| 4. 质量过滤 | 验证是否为双说话人段 |
| 5. 分离 | 隔离说话人轨道（DialogueSidon） |
| 6. 通用转写 | 非中文音频 ASR（Qwen3-ASR-1.7B） |
| 7. 中文转写 | Paraformer + CT-PUNC（离线 ModelScope 快照） |
| 8. 说话人 profile 提取 | WavLM embedding |
| 9. 对话扩写 + 终端评估 | 生成 + Gemini 多模态质量评分 |

---

## 内部使用的模型栈

| 模块 | 模型 |
|------|------|
| 说话人分离 + 还原 | **DialogueSidon**（VAE + 扩散潜变量预测，SIGDIAL 2026，arXiv 2604.09344） |
| 说话人验证 | **WavLM** embeddings |
| ASR（非中文） | **Qwen3-ASR-1.7B** |
| ASR（中文） | **Paraformer + CT-PUNC**（离线，需本地 ModelScope 快照） |
| 语音合成 | **Qwen3-TTS** |
| 自动评估 | **Gemini** 多模态 |
| 音质评分 | **NISQA** + **DNSMOS** |

其中 DialogueSidon 是东京大学 / NTT / Sony 团队的工作（不是 AveraLabs 自研），ConversationalVoice 把它作为分离阶段的核心组件引入。

---

## 质量指标（论文数据）

| 指标 | 分离 | 重建 | 扩写 |
|------|------|------|------|
| NISQA MOS（语音质量） | 3.56 | 4.41 | 4.61 |
| 说话人相似度（声音克隆） | 0.983–0.991 | 0.983–0.991 | — |
| Gemini 上下文连贯性 | — | — | 4.94 / 5 |
| Gemini 对话自然度 | — | — | 4.80 / 5 |

重建和扩写的音质（NISQA MOS 4.41 / 4.61）明显优于分离数据（3.56），因为分离数据受原始录音质量限制。

---

## 硬件与基础设施要求

### 计算资源

- **NVIDIA CUDA GPU**：必须（DialogueSidon 分离、Qwen3-ASR 转写、Qwen3-TTS 合成均需要 GPU）
- 论文未给出精确的显存要求，但组合模型栈建议 **24GB+ 显存**（Qwen3-ASR 2B + Qwen3-TTS + DialogueSidon 同时加载）
- CPU 推理不支持

### 服务依赖

```
必须自建或托管：
├── PostgreSQL          — 流水线状态 + 数据血缘追踪
├── Redis               — Celery 消息 broker
└── S3 或 S3 兼容存储  — 音频文件存储（MinIO 可替代 AWS S3）
```

### API 密钥

- **HuggingFace Token**：VAD、Diarization、分离、转写模型访问
- **OpenRouter API Key**：说话人 profile 提取、扩写生成、Qwen3-TTS 合成
- **Gemini API**（或 OpenRouter 路由到 Gemini）：扩写质量评估

### 本地模型快照（中文支持）

中文转写阶段需要离线的 ModelScope 模型快照：
- `damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch`
- `damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch`

### 软件依赖

```bash
# 包管理（推荐）
pip install uv

# 系统依赖
apt-get install ffmpeg  # 或 brew install ffmpeg

# 安装流水线
uv pip install -r requirements.txt
```

### 最小推荐配置

| 组件 | 推荐规格 |
|------|---------|
| GPU | NVIDIA RTX 3090 / A5000 (24GB) 或以上 |
| CPU | 8 核以上 |
| 内存 | 32GB RAM |
| 存储 | 500GB+（音频文件 + 模型快照） |
| 网络 | 需要访问 HuggingFace 和 OpenRouter |

---

## 工程部署指导

### 1. 本地开发部署

```bash
# 克隆仓库
git clone https://github.com/avera-labs/ConversationalVoice
cd ConversationalVoice

# 启动基础设施
docker-compose up -d postgres redis minio  # 若使用 Docker Compose

# 配置环境变量
cp .env.example .env
# 填写：HUGGINGFACE_TOKEN, OPENROUTER_API_KEY, 
# PostgreSQL 连接字符串, Redis URL, S3 配置

# 安装依赖
uv pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 下载中文 ModelScope 快照（若需要中文支持）
python scripts/download_modelscope.py
```

### 2. 启动各阶段 Celery Worker

每个流水线阶段是一个独立的 Celery worker，需要分别启动：

```bash
# 阶段 1-4（轻量，CPU 可以）
celery -A pipeline worker -Q ingest,vad,diarization,quality_filter --concurrency=4

# 阶段 5（GPU 密集：说话人分离）
celery -A pipeline worker -Q separation --concurrency=1 --pool=solo

# 阶段 6-7（GPU：ASR 转写）
celery -A pipeline worker -Q transcription_general,transcription_chinese --concurrency=1

# 阶段 8-9（GPU：profile 提取 + 扩写生成）
celery -A pipeline worker -Q speaker_extraction,expansion --concurrency=1
```

### 3. 提交音频处理任务

```bash
# 通过 Ingest API 提交音频文件
curl -X POST http://localhost:8000/api/ingest \
  -F "audio=@conversation.wav" \
  -F "language=zh"  # 或 en

# 查询任务状态
curl http://localhost:8000/api/status/{task_id}
```

### 4. 输出格式

每段对话输出结构：

```
output/
├── separation/
│   ├── speaker_A.wav     # 分离后的 A 说话人音轨
│   ├── speaker_B.wav     # 分离后的 B 说话人音轨
│   └── metadata.json     # 时间戳、说话人 ID、转录
├── reconstruction/
│   ├── speaker_A_recon.wav
│   ├── speaker_B_recon.wav
│   └── metadata.json     # 词级对齐、合成指令
└── expansion/
    ├── speaker_A_exp.wav
    ├── speaker_B_exp.wav
    └── metadata.json     # 新对话内容、Gemini 质量评分
```

---

## ⚠️ 许可证：BSL 1.1，不是开源许可证

这是使用前最重要的一点：

**Business Source License 1.1** 不是传统开源许可证：

- ✅ **非生产环境**（本地研究、学习、测评、教育）：免费使用
- ✅ **学术研究**：明确允许，包括生产规模基准测试
- ❌ **生产环境商用**（用该流水线构建商业服务或训练商业模型）：需要向 AveraLabs 购买单独的商业授权
- 🕒 **4 年后转 MIT**：首次公开发布之日起 4 年后，自动转为 MIT 许可证

简单说：个人研究和学术使用没有问题；想用这条流水线处理数据、训练商业语音产品，需要先联系 AveraLabs。

---

## 下游模型与场景

论文明确列出该数据集针对的下游模型：
- **dGSLM**（双流全双工 GSLM）
- **Moshi**（Kyutai 全双工语音模型）
- Full-Duplex-Bench 基准测试中评测的所有系统

AveraLabs 还发布了 **InteractionBench**（github.com/avera-labs/InteractionBench），对 GPT-Live-1、Gemini-Live、Moshi、FreezeOmni 等 7 个实时语音 AI 系统进行了 4 个维度的评测：对话时序、语音任务准确率、副语言控制、长对话记忆。两个工作形成配套：一个造数据，一个测效果。

---

## 不足之处

**1. Stars 偏少（51）**：项目曝光度有限，工程成熟度不确定。

**2. BSL 1.1 限制商业使用**：不能把这条流水线直接用于生产数据服务，除非购买商业授权，会影响部分场景的采用。

**3. 基础设施门槛高**：PostgreSQL + Redis + S3 + 24GB GPU，不是轻量工具，本地跑完整流水线需要一台配置不低的机器。

**4. 依赖 OpenRouter 外部 API**：扩写和合成阶段调用云端 API（Qwen3-TTS 通过 OpenRouter），数据不完全留本地，有隐私和成本顾虑。

**5. 未公开数据集规模**：论文没有说明处理了多少小时的数据，扩展性指标不明确。

**6. 中文 ModelScope 依赖**：中文转写需要手动下载 ModelScope 模型快照，在某些网络环境下比较麻烦。

---

## 怎么看这个工作

ConversationalVoice 切入了一个真实的工程痛点：全双工语音模型的数据匮乏不只是"数量不够"，而是"正确格式的数据几乎不存在"。把单声道录音分离成双轨、再用克隆语音扩充，让每段录音产出三类数据，这个思路有工程价值。

用 DialogueSidon 做分离核心、Qwen3-ASR 做转写、Qwen3-TTS 做合成、Gemini 做评估——整条链路复用了现有最强的开源/API 组件，没有重复造轮子，架构上是合理的。

BSL 1.1 的许可证选择有商业逻辑：学术社区可以免费用来做研究和基准测试，这帮助论文传播和技术验证；商业公司要用于训练产品则需要付费，这保护了 AveraLabs 的商业价值。4 年后转 MIT，也给了社区一个明确的时间预期。

目标用户：想做全双工语音模型研究的学术团队；有自己的对话录音库、想把它转成训练数据的组织——前提是不打算商用，或者愿意向 AveraLabs 购买授权。

> 代码 Business Source License 1.1，生产商用需授权，仅供学习研究参考。

---

<!--EN-->

## ConversationalVoice: Pipeline for Full-Duplex Training Data from Real Conversations

`avera-labs/ConversationalVoice` (51 stars) is an end-to-end pipeline from AveraLabs that converts real two-person audio recordings into curated training data for full-duplex speech models. Accompanied by arXiv paper 2609.08147.

**GitHub**: github.com/avera-labs/ConversationalVoice | **Stars**: 51 | **⚠️ License**: BSL 1.1 | **Paper**: arxiv.org/abs/2609.08147

---

### Why Training Data Is the Full-Duplex Bottleneck

Full-duplex voice AI listens and speaks simultaneously on parallel streams — no push-to-talk, no VAD gate, real interruptions and backchannels. Training it requires audio data where each speaker's track is **separated** and interaction timing is **preserved intact**.

Reality: ~1M hours of public speech data exists, but almost none is split into per-speaker dual tracks with natural overlap and timing preserved. Most real two-person recordings are monaural mixtures — two speakers entangled in a single channel.

ConversationalVoice converts those monaural mixtures into usable training data.

---

### Three Output Data Types Per Conversation

**Separation** — Recovers individual speaker tracks from real recordings, preserving original interaction timing (pauses, overlaps, backchannels, interruptions exactly as they occurred). Audio quality is limited by the source recording.

**Reconstruction** — Re-synthesizes the same conversation using Qwen3-TTS voice cloning, with word-level alignment and delivery instructions. Higher audio quality; same turn order and overlap timing as the original.

**Expansion** — Generates entirely new dialogue constrained by the original speakers' voice profiles and interaction pattern. New content, same conversational fingerprint.

Measured interaction rate differences between Expansion and Reconstruction: 4.6% fewer turns, 8.0% fewer overlaps, 13.2% fewer backchannels, 16.0% fewer interruptions — expanded dialogue is slightly more "tidy" than real conversation.

---

### Pipeline Architecture: 9 Celery Stages

| Stage | Function |
|-------|----------|
| 1. Ingest API | Normalized WAV creation |
| 2. VAD split | Conversation window detection |
| 3. Diarization | Speaker turn detection |
| 4. Quality filter | Validates two-speaker segments |
| 5. Separation | Speaker track isolation (DialogueSidon) |
| 6. General transcription | Qwen3-ASR-1.7B for non-Chinese |
| 7. Chinese transcription | Paraformer + CT-PUNC (offline ModelScope) |
| 8. Speaker profile extraction | WavLM embeddings |
| 9. Dialogue expansion + evaluation | Generation + Gemini quality scoring |

Each stage runs as an independent Celery worker on a dedicated queue; PostgreSQL tracks data lineage across all stages.

---

### Internal Model Stack

| Module | Model |
|--------|-------|
| Speaker separation + restoration | **DialogueSidon** (VAE + diffusion latent predictor, SIGDIAL 2026, arXiv 2604.09344) |
| Speaker verification | **WavLM** embeddings |
| ASR (non-Chinese) | **Qwen3-ASR-1.7B** |
| ASR (Chinese) | **Paraformer + CT-PUNC** (offline, local ModelScope snapshots required) |
| Voice synthesis | **Qwen3-TTS** |
| Quality evaluation | **Gemini** multimodal |
| Speech quality scoring | **NISQA** + **DNSMOS** |

Note: DialogueSidon is from the University of Tokyo / NTT / Sony team — not AveraLabs. ConversationalVoice integrates it as the separation component.

---

### Quality Metrics (from paper)

| Metric | Separation | Reconstruction | Expansion |
|--------|-----------|----------------|-----------|
| NISQA MOS (speech quality) | 3.56 | 4.41 | 4.61 |
| Speaker similarity (voice cloning) | 0.983–0.991 | 0.983–0.991 | — |
| Gemini contextual coherence | — | — | 4.94 / 5 |
| Gemini dialogue naturalness | — | — | 4.80 / 5 |

---

### Hardware and Infrastructure Requirements

**Compute:**
- NVIDIA CUDA GPU required — no CPU inference support
- Recommended: **24GB+ VRAM** (Qwen3-ASR ~2B + Qwen3-TTS + DialogueSidon combined)
- Minimum recommended: RTX 3090 / A5000 or equivalent

**Services (must self-host or provision):**
```
PostgreSQL    — pipeline state + data lineage
Redis         — Celery message broker  
S3 storage    — audio file storage (MinIO works as AWS S3 substitute)
```

**API keys:**
- HuggingFace Token — VAD, diarization, separation, transcription models
- OpenRouter API Key — speaker extraction, expansion generation, Qwen3-TTS synthesis
- Gemini API — quality evaluation (or route via OpenRouter)

**For Chinese support:** Local ModelScope snapshots of Paraformer and CT-PUNC (manual download required)

**Software:** `uv` package manager + FFmpeg + `requirements.txt`

---

### Deployment

```bash
# Start infrastructure
docker-compose up -d postgres redis minio

# Configure environment
cp .env.example .env
# Fill in: HUGGINGFACE_TOKEN, OPENROUTER_API_KEY, DB/Redis/S3 config

# Install and initialize
uv pip install -r requirements.txt
python scripts/init_db.py

# Start Celery workers per stage
celery -A pipeline worker -Q ingest,vad,diarization,quality_filter --concurrency=4
celery -A pipeline worker -Q separation --concurrency=1 --pool=solo         # GPU
celery -A pipeline worker -Q transcription_general,transcription_chinese --concurrency=1  # GPU
celery -A pipeline worker -Q speaker_extraction,expansion --concurrency=1  # GPU

# Submit audio for processing
curl -X POST http://localhost:8000/api/ingest -F "audio=@dialogue.wav" -F "language=en"
```

---

### ⚠️ License: BSL 1.1 — Not a Standard Open-Source License

**Business Source License 1.1** grants:
- ✅ Non-production use: free (local research, education, evaluation)
- ✅ Academic research at production scale: explicitly permitted
- ❌ Commercial production use: requires a separate commercial license from AveraLabs
- 🕒 Converts to MIT 4 years after first public distribution

Do not use this pipeline to build or train commercial voice products without licensing from AveraLabs.

---

### Downstream Targets and Companion Work

The paper explicitly targets: **dGSLM**, **Moshi** (Kyutai), and models on Full-Duplex-Bench.

AveraLabs also published **InteractionBench** (github.com/avera-labs/InteractionBench) — a benchmark evaluating 7 real-time voice AI systems (GPT-Live-1, Gemini-Live, Moshi, FreezeOmni, etc.) on 4 axes: conversational timing, spoken-task accuracy, paralinguistic control, long-conversation grounding. The two repos form a pair: one builds training data; the other evaluates trained systems.

---

### Limitations

1. **Low star count (51)**: Limited exposure; engineering maturity uncertain.
2. **BSL 1.1 commercial restriction**: Cannot use in commercial production without paying AveraLabs.
3. **High infrastructure bar**: PostgreSQL + Redis + S3 + 24GB GPU — not a lightweight tool.
4. **External API dependency**: Expansion and synthesis call OpenRouter cloud APIs — data doesn't stay fully local.
5. **Dataset scale unpublished**: No hours-processed figures in the paper.
6. **Chinese ModelScope dependency**: Manual snapshot download required; challenging in restricted network environments.

---

### Bottom Line

ConversationalVoice addresses a real bottleneck: full-duplex model training data is scarce not just in quantity but in the right format. Converting monaural mixtures into separated dual tracks, then amplifying each recording into three data types, is a sound engineering approach to the data problem.

The architecture uses best-in-class existing components (DialogueSidon for separation, Qwen3-ASR for transcription, Qwen3-TTS for synthesis) rather than building from scratch. The BSL 1.1 license makes economic sense: academic users can benchmark and research freely, while commercial users fund continued development.

Best fit for: academic groups studying full-duplex voice models; organizations with existing dialogue recording libraries that want to convert them into training data — provided they're doing research, not building a commercial product.

> Code under Business Source License 1.1. Commercial production use requires authorization from AveraLabs. For learning and research only.
