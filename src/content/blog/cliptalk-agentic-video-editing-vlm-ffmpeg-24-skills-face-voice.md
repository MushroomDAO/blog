---
title: "ClipTalk：用自然语言剪视频，VLM + 24 个 Skill 驱动的 Agentic 视频编辑系统"
titleEn: "ClipTalk: Edit Video by Talking — VLM + 24 Skills Driving an Agentic Video Pipeline"
description: "非商业自定义许可，126 stars。三层架构：Python FastAPI + Node Pi Agent + 浏览器。24 个 SKILL.md 技能，VLM 理解画面，本地 SenseVoice/TalkNet/SFace/YOLOX 识别人脸/声纹/活跃发言人，FFmpeg 执行剪辑。6 步审批门禁，V2 算法比基线慢 14s。仅支持 Linux x86-64/WSL2，不支持 macOS/ARM。"
descriptionEn: "Custom non-commercial license, 126 stars. Three-tier: Python FastAPI + Node Pi Agent + browser. 24 SKILL.md skills, VLM for scene understanding, local SenseVoice/TalkNet/SFace/YOLOX for face/voice/active-speaker, FFmpeg for cutting. 6-step approval gates. V2 algorithm is 14s slower than baseline. Linux x86-64/WSL2 only — no macOS/ARM."
pubDate: 2026-09-20
heroImage: "../../assets/images/cliptalk-agentic-video-editing-vlm-ffmpeg-24-skills-face-voice-banner.jpg"
category: "Tech-Experiment"
tags: ["video-editing", "agent", "vlm", "ffmpeg", "local-ai", "face-recognition"]
lang: zh-CN
---

[ClipTalk](https://github.com/GML-MMGroup/ClipTalk) 是 GML-MMGroup 开源的 Agentic 视频编辑系统，主张"说话就能剪"：用户用自然语言描述想要什么片段，Agent 负责理解素材、定位内容、规划剪辑、执行输出。2026-07 开源，当前 126 stars。

**仓库**：github.com/GML-MMGroup/ClipTalk | **License**：自定义非商业 Attribution License v1.1 | **Stars**：126

**注意**：许可证非 OSI 批准的开源协议，不允许商业用途，包括企业、高校用于营收目的。

---

## 系统架构

三层：

```
Browser (Vite) → Node 22 Agent Service (Pi Runtime) → Python FastAPI (媒体内核)
                                                       └── SQLite + JSON 备份
                                                       └── FFmpeg
                                                       └── 本地模型池
```

**Pi**（`0.84.4`）是 Agent 编排层，负责 Tool Calling。项目明确要求：不支持只返回 JSON 文本的模型，必须通过真实 Tool Calling 探针。

**VLM / LLM** 由用户在 Settings 页配置，支持 Volcano Ark（字节）、OpenAI 兼容接口、Anthropic 接口代理。**不内置模型权重**，必须自己接 API。

**本地运行的模型**（不需要外部 API）：

| 组件 | 模型 | 用途 |
|------|------|------|
| 语音识别 | SenseVoice Small (iic) | ASR + VAD + 说话人分离 |
| 备用 ASR | Faster-Whisper 1.1.0 | 可选 |
| 屏幕文字 | PaddleOCR 3.7.0 | 屏幕内容 OCR |
| 视觉搜索 | SigLIP2 (google) | 视觉嵌入检索 |
| 文本嵌入 | multilingual-e5-base | 语义搜索 |
| 人脸检测 | YuNet (ONNX) | 检测人脸位置 |
| 人脸识别 | SFace (ONNX) | 匹配目标人物 |
| 全身检测 | YOLOX (ONNX) | 全身 person 检测 |
| 人物重识别 | YoutuReID (ONNX) | 跨帧同一人物 |
| 声纹验证 | CAM++ (iic) | 识别说话人声纹 |
| 音频语义 | CLAP (laion) | 音频语言嵌入 |
| 目标定位 | Grounding DINO tiny | 开放词汇目标检测 |
| 活跃发言人 | TalkNet ASD | 音视频同步，谁在说话（独立 venv） |

可选升级：**WeMM-Embedding-2B**（腾讯），统一文字/图片/视频检索，需独立 Python 环境。

---

## 四种核心编辑能力

**1. 精华提取（Highlight）**
从长视频中识别"最佳时刻"，生成高亮剪辑/回顾/预告片。

**2. 人脸匹配编辑**
上传参考人脸图片，YuNet + SFace 找出目标人物出现的所有片段。

**3. 话题语义编辑**
用自然语言描述主题（如"把他们讲产品 X 的部分剪出来"），VLM + embedding 定位相关段落。

**4. 声纹编辑**
上传说话人的音频样本，CAM++ 识别其声纹并提取所有该人说话的片段。

还支持对话式细化——"再短一点"、"从讲价格那段开始"。

---

## 6 步审批门禁

ClipTalk 不是"说了就直接剪"：Agent 的每次执行都经过严格管控：

1. 任务绑定到持久化 Agent 工作区
2. Pi 选择并激活对应的 Skill（24 个 SKILL.md 格式 Skill）
3. **规划阶段只能调 `submit_plan`**，不能直接分析或渲染
4. FastAPI 验证 DAG：工具名、依赖关系、副作用类别、Skill 版本、工作区修订号
5. 审批绑定计划哈希和允许工具集，之后 Executor 才开始执行
6. 身份识别、删除操作、最终导出仍为结构化用户操作——Agent 只输出预览，**确认后才导出**

---

## 24 个 Skill

SKILL.md 格式，每个 Skill 声明 `name`、`version`、`allowed-tools`、`workflow-profile`。部分示例：

- `cliptalk-highlight-director` — 精华剪辑导演
- `cliptalk-interview-editor` — 采访视频剪辑
- `cliptalk-speaker-editor` — 说话人剪辑
- `cliptalk-person-editor` — 人物跟踪剪辑
- `cliptalk-multi-topic-assembler` — 多主题拼接
- `cliptalk-caption-layout-director` — 字幕布局导演
- `cliptalk-social-reframe-exporter` — 竖版社交媒体导出
- `cliptalk-smart-reframe` — 智能重新裁剪
- `cliptalk-delivery-qc` — 输出质量检查
- `cliptalk-source-provenance-guard` — 素材来源保护

---

## 关键数字

| 指标 | 值 |
|------|-----|
| 单文件上传上限 | 8 GB |
| 存储上限（默认） | 50 GiB |
| 最大工作进程 | 1（单 FastAPI worker） |
| V2 算法延迟（示例） | 34s vs 基线 20s（多 14s） |
| 视频采样密度 | 0.25s 一帧，边界处密化到 0.083s |
| 每候选最多采样点 | 480 个 / 最多 48 次 VLM 调用 |
| 后端测试覆盖 | 1086 通过 |
| 前端测试覆盖 | 178 测试，177 通过（1 个 known bug 已定向回归） |

---

## 不足之处

**1. 不支持 macOS / ARM**：仅 Linux x86-64 或 Windows WSL2。官方文档明确声明其他平台不受原生安装支持。

**2. V2 算法比基线慢**：更密集的证据验证（0.083s 采样 + 最多 48 次 VLM 调用）换来更高准确率，但延迟从 20s 升至 34s。如果 VLM 预算耗尽，候选片段停在"待审核"状态——不是召回保证。

**3. TalkNet 需要独立 Python 环境**：依赖冲突，必须手动配置路径。不配置就只能用 `shadow` 模式（只记日志，不修改输出）。

**4. 插件不沙盒隔离**：Plugin 在 Node Agent 进程内运行，拥有宿主进程权限。批准即信任。

**5. 文档与环境变量不一致**：`environment.example` 把 `HIGHLIGHT_ACTIVE_SPEAKER_MODE` 默认设为 `primary`，但 `active-speaker.md` 说应保持 `shadow` 直到真实视频验证通过，两者矛盾。

**6. 无 arXiv 论文、无在线 Demo、无 HuggingFace 页面**：只有代码和 GIF 演示。

**7. 非商业许可**：自定义 NC Attribution License v1.1，不可用于任何营收目的。

---

## 安装（CPU，Linux / WSL2）

```bash
git clone https://github.com/GML-MMGroup/ClipTalk.git && cd ClipTalk
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements-cpu.txt
python3 tools/prepare_recognition_models.py --data-root data  # 下载 ONNX 模型
python3 tools/doctor.py --profile cpu
./start.sh  # 浏览器开 http://localhost:5180
```

然后在 Settings 页配置 VLM（必填）。

**Docker（CPU）**：
```bash
cp .env.example .env
docker compose up --build
```

GPU 版把 `requirements-cpu.txt` 换成 `requirements-gpu.txt`，Docker 加 `docker-compose.gpu.yml` overlay。

---

## 怎么看这件事

ClipTalk 的架构设计比较严谨——6 步审批、DAG 验证、计划哈希绑定，把 Agent 的副作用控制得很明确。24 个 SKILL.md Skill 和本地化的人脸/声纹/活跃发言人检测组合，覆盖了播客剪辑、采访视频、竖版社交素材等实际场景。

短板也很实际：V2 更准但更慢，TalkNet 安装门槛高，macOS 完全不支持，许可证不允许商用。126 stars + 2026-07 创建，属于早期项目，尚未有公开基准数字证明其视频理解质量。

对于有 Linux 机器、需要本地化视频 Agent、用于研究或个人使用的场景，值得试用。

> 代码与模型仅供学习研究，许可证明确禁止商业使用。

---

<!--EN-->

## ClipTalk: Edit Video by Talking

[ClipTalk](https://github.com/GML-MMGroup/ClipTalk) (GML-MMGroup) is an agentic video editing system: describe what you want in natural language, and the agent handles scene understanding, content location, edit planning, and output delivery. Open-sourced 2026-07, 126 stars.

**Repo**: github.com/GML-MMGroup/ClipTalk | **License**: Custom Non-Commercial Attribution License v1.1 | **Stars**: 126

**Important**: Non-commercial license only — no use for revenue-generating purposes.

---

### Architecture

Three-tier: Python FastAPI (media kernel) + Node 22 Agent Service (Pi 0.84.4 runtime) + browser.

**VLM/LLM**: user-configured, not bundled. Supports Volcano Ark (ByteDance), OpenAI-compatible, Anthropic-compatible proxy. Pi requires real Tool Calling — models that only return JSON text are rejected.

**Local models (no external API)**:
- SenseVoice Small — ASR + VAD + speaker diarization
- YuNet + SFace (ONNX) — face detection + recognition
- YOLOX + YoutuReID (ONNX) — full-body person tracking
- CAM++ — voice-print speaker verification
- TalkNet ASD — active speaker detection (isolated venv)
- SigLIP2 + multilingual-e5-base — visual/text embedding search
- Grounding DINO tiny — open-vocabulary object grounding
- PaddleOCR — on-screen text
- CLAP — audio-language embedding

All cutting/encoding via FFmpeg.

---

### Four Core Editing Modes

1. **Highlight extraction** — identify best moments from long footage
2. **Face-matched editing** — upload reference face → extract all segments where that person appears
3. **Topic-based editing** — natural language query → VLM + embedding → extract relevant segments
4. **Voice-print editing** — upload voice sample → CAM++ → extract all segments where that speaker speaks

Conversational follow-ups supported: "make it shorter", "start from the pricing part".

---

### 6-Step Approval Gate

1. Task binds to durable agent workspace
2. Pi selects a SKILL.md skill (24 available)
3. Planning phase: agent may **only call `submit_plan`** — no analysis or rendering
4. FastAPI validates DAG: tool names, dependencies, side-effect classes, skill versions
5. Approval binds plan hash + allowed toolset; Executor dispatches only then
6. Identity, deletion, and final export remain user-confirmed actions — agent stops at review preview

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Max upload per file | 8 GB |
| Default storage limit | 50 GiB |
| Max workers | 1 |
| V2 algorithm latency | 34s vs baseline 20s |
| V2 sampling density | 0.25s/frame, densified to 0.083s at boundaries |
| Max sample points per candidate | 480 / up to 48 VLM calls |

---

### Limitations

1. **No macOS / ARM** — Linux x86-64 or Windows WSL2 only. Explicitly documented.
2. **V2 is slower than baseline** — 34s vs 20s. If VLM budget exhausted, candidates stay in "pending review".
3. **TalkNet requires isolated Python env** — dependency conflicts. Without it, active-speaker detection runs in `shadow` mode (logging only, no output modification).
4. **Plugins run unsandboxed** — full host-process privileges once approved.
5. **Env var doc inconsistency** — `environment.example` sets `primary` mode by default; `active-speaker.md` says keep it at `shadow` until real-video validation passes.
6. **No arXiv paper, no hosted demo, no HuggingFace page** — GIF demos only.
7. **Non-commercial license** — cannot be used for revenue-generating purposes.

---

### Installation (CPU, Linux/WSL2)

```bash
git clone https://github.com/GML-MMGroup/ClipTalk.git && cd ClipTalk
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-cpu.txt
python3 tools/prepare_recognition_models.py --data-root data
python3 tools/doctor.py --profile cpu
./start.sh  # opens at http://localhost:5180
```

Configure VLM in Settings (required). Docker: `cp .env.example .env && docker compose up --build`.

---

### Bottom Line

ClipTalk's architecture is thoughtfully constrained — the 6-step gate, DAG validation, and plan-hash binding keep agent side effects auditable. The local model stack (face/voice/active-speaker recognition) covers realistic editing scenarios without cloud dependencies. The gaps are equally real: V2 is slower, TalkNet installation is non-trivial, macOS is unsupported, and no public benchmarks exist yet. A serious early-stage project worth watching for Linux-based video production workflows.

> Code and models for research and learning only. Commercial use is prohibited under the custom license.
