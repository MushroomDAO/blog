---
title: "腾讯 Youtu-Parsing-Omni：一个 5B 模型解析文档、图表、音频、视频"
titleEn: "Tencent Youtu-Parsing-Omni: One 5B Model to Parse Documents, Charts, Audio, and Video"
description: "腾讯 Youtu Lab 开源 Youtu-Parsing-Omni（88 stars，自定义 License，含 EU 排除条款）：5B 参数全模态解析模型，单个统一编码器覆盖 8 种输入模态（文档页面、自然图像、图表、流程图、几何图、音频、自然视频、含文字视频），所有任务输出统一的 OmniSchema JSON。感知层输出版面块、OCR 文字+bbox、表格 OTSL、LaTeX 公式、音频时间戳+ASR+声学事件、视频镜头运动；认知层输出描述/叙事/结构化报告。OmniDocBench 96.96 自报 SOTA；OmniParsingBench 75.08，最强开源权重（Gemini-3-Pro 77.44）。推理依赖 vLLM 0.19.0 + 自定义插件 + CUDA，还需一套独立的 transformers 5.10.2 环境，两套环境不兼容，设置门槛较高。"
descriptionEn: "Tencent Youtu Lab open-sourced Youtu-Parsing-Omni (88 stars, custom license with EU exclusion): a 5B-parameter omni-modal parsing model with a single unified encoder covering 8 input modalities (document, natural image, chart, flowchart, geometry, audio, natural video, text-rich video). All tasks emit a unified OmniSchema JSON. Perception layer outputs layout blocks, OCR text+bbox, OTSL tables, LaTeX formulas, audio timestamps+ASR+acoustic events, camera motion. Cognition layer outputs description/narrative/structured report. Self-reported SOTA on OmniDocBench (96.96); best open-weight on OmniParsingBench (75.08 vs Gemini-3-Pro 77.44). Inference requires vLLM 0.19.0 + custom plugin + CUDA, plus a separate incompatible transformers 5.10.2 environment."
pubDate: 2026-10-10
heroImage: "../../assets/images/youtu-parsing-omni-tencent-5b-multimodal-document-parser-banner.jpg"
category: "Research"
tags: ["多模态", "文档解析", "OCR", "腾讯", "开源模型"]
lang: "zh-CN"
wechatTitle: "腾讯5B全模态解析Youtu-Parsing-Omni"
wechatDigest: "88星；License含EU排除；8模态→统一JSON；OmniDocBench 96.96 SOTA"
---

大多数解析工具要么处理文档，要么处理图像，要么处理音频——分门别类，各司其职。

Youtu-Parsing-Omni 想把这件事做成一个：**一个 5B 模型，一个统一 JSON，八种输入模态。**

GitHub: https://github.com/TencentCloudADP/youtu-parsing
HuggingFace: https://huggingface.co/tencent/Youtu-Parsing-Omni

88 stars，腾讯 Youtu Lab 出品，TencentCloudADP 发布。

---

## 八种模态，一个出口

`--task` 参数决定任务类型：

| 任务 | 输入 |
|------|------|
| `document` | 文档页（PDF、扫描件） |
| `natural_image` | 自然图像或照片 |
| `graphics_chart` | 柱状图/折线图/饼图 |
| `graphics_flowchart` | 流程图和示意图 |
| `graphics_geometric` | 几何图（数学/科学题） |
| `audio` | 音频片段 |
| `natural_video` | 自然视频（无大量覆盖文字） |
| `textrich_video` | 含文字视频（课件、录屏） |

**所有任务输出同一个 OmniSchema JSON**，内部字段按任务类型填充，结构如下：

```json
{
  "modality": "image",
  "subtype": "document",
  "elements": [
    {
      "type": "text",
      "content": "...",
      "bbox": "<box><x_85><y_275><x_1000><y_1000></box>"
    }
  ],
  "reading_order": [0, 1, 2],
  "global_description": "..."
}
```

音视频输出中 `segments` 字段携带 `HH:MM:SS` 时间戳。

---

## 感知层输出什么

| 输入类型 | 感知输出 |
|---------|---------|
| 文档 | 版面块 + OCR + bbox + 表格（OTSL） + 公式（LaTeX） + 阅读顺序 |
| 图表 | Markdown 表（图表）、Mermaid（流程图）、点线弧测量（几何） |
| 音频 | 时间戳 + 说话人 ASR + 非语音声学事件标签 |
| 自然视频 | 时间戳 + 场景描述 + 镜头运动标签 |
| 含文字视频 | 时间戳 + ASR + OCR + `structured_report`（Markdown 结构化摘要） |

bbox 用特殊 token 表示，坐标系归一化到 0–1000 网格：`<box><x_85><y_275><x_1000><y_1000></box>`

---

## 认知层输出什么

每个任务的输出里都有 `global_description`，内容随任务类型变化：
- 图表/文档 → 内容摘要
- 自然图像 → 场景描述
- 自然视频 → 跨时序的动作/事件叙事
- 含文字视频 → 结构化内容报告

---

## 单一编码器的设计

常见多模态模型用**分开的视觉塔 + 音频塔**，Youtu-Parsing-Omni 改成一个统一的 **Youtu-Omni-Encoder**：

- 模态-specific 的薄层 stem 把像素/log-mel 频谱图映射成 token
- 所有 token 在同一个双向 Transformer 里处理，用 `(t, h, w)` 统一位置编码
- 图片、音频帧、视频帧可以打包进同一次前向计算

视频处理时音视频融合层在每个音频到帧的时间边界打开新的注意力窗口，视频帧可以「看到」同一时刻的声音。

训练用了作者自己提出的 OSAD 流程：SFT → schema 路由 RLVR → OmniSchema-Aware On-Policy Distillation，不依赖单独的教师模型，靠模型自采样 + 准入门控迭代自蒸馏。

---

## Benchmark（自报）

**OmniDocBench v1.6**（文档解析，自报开源 SOTA）：

| 指标 | 分数 |
|------|------|
| 整体 | **96.96**（对比 TeleOCR 96.91） |
| 表格 TEDS | 96.79 |
| 公式 CDM | 96.80 |

**OmniParsingBench**（跨模态，最强开源权重）：

| 类别 | 分数 |
|------|------|
| 平均 | 75.08（Gemini-3-Pro 77.44） |
| 图表 | **95.02**（超 Gemini-3-Pro 92.79） |
| 音频 | **78.08**（超 Gemini-3-Pro 76.74） |
| 几何图 | 74.33 |
| 自然图像 | 62.84 |

以上均为作者自报，论文 arXiv 编号标注为 TBD，未经外部独立复现验证。

---

## 推理环境（门槛较高）

两套**不兼容的 Python 环境**都要配：

**vLLM 服务（推荐，benchmark 结果从这套来）：**
```bash
pip install vllm==0.19.0 transformers==5.2.0
pip install vllm-plugin-vita-omni   # 自定义插件，不可缺
# ⚠️ 这套环境里不能装 peft
MODEL=tencent/Youtu-Parsing-Omni GPU=0 bash scripts/vllm.sh
# 启动 OpenAI 兼容服务 127.0.0.1:8000
python examples/infer_vllm.py --task document --media file.pdf
```

**Transformers 推理：**
```bash
pip install transformers==5.10.2
# trust_remote_code=True，建议用 --revision 锁定 commit
```

其他依赖：Python ≥ 3.10，CUDA GPU（BF16 权重），`ffmpeg`（音视频处理）。

---

## License 注意

许可证结构类似 Apache-2.0，但附加了一条：**"本软件不适用于欧盟境内使用"**。如与标准 Apache-2.0 有冲突，以该条款为准。EU 用户需注意。

---

## 已知边界

- 自报 benchmark，论文 arXiv 编号 TBD，尚无外部独立验证
- 需要两套不兼容环境，设置复杂度较高
- `natural_image` 任务在 OmniParsingBench 得分 62.84，低于其他模态
- 88 stars，极早期，生产稳定性未经验证
- License 含 EU 排除条款，不是标准开源

---

## 一句话说清楚

Youtu-Parsing-Omni 是腾讯 Youtu Lab 的 5B 全模态解析模型：一个统一编码器覆盖 8 种输入，所有任务输出统一 OmniSchema JSON，文档/图表/音频/视频的感知与认知结果结构一致。OmniDocBench 96.96（自报 SOTA），OmniParsingBench 75.08（最强开源权重）。推理依赖 vLLM 0.19.0 + 自定义插件，门槛不低。

---

> 88 stars，腾讯 Youtu Lab，License 含 EU 排除条款。开源仅供学习参考，EU 用户注意 License 条款，论文 arXiv 编号 TBD。

---

<!--EN-->

## Tencent Youtu-Parsing-Omni: One 5B Model to Parse Documents, Charts, Audio, and Video

Most parsing tools handle one modality: documents, images, or audio — specialized and siloed. Youtu-Parsing-Omni aims to do it in one: **one 5B model, one unified JSON, eight input modalities.**

GitHub: https://github.com/TencentCloudADP/youtu-parsing
HuggingFace: https://huggingface.co/tencent/Youtu-Parsing-Omni

88 stars, Tencent Youtu Lab, published under TencentCloudADP.

---

### Eight Modalities, One Output

The `--task` parameter selects the task:

| Task | Input |
|------|-------|
| `document` | Document pages (PDF, scans) |
| `natural_image` | Photographs or general images |
| `graphics_chart` | Bar/line/pie charts |
| `graphics_flowchart` | Flowcharts and diagrams |
| `graphics_geometric` | Geometry figures (math/science) |
| `audio` | Audio clips |
| `natural_video` | Video without heavy text overlay |
| `textrich_video` | Text-rich video (slides, screencasts) |

**All tasks emit the same OmniSchema JSON** — field population varies by task type. Fields: `modality`, `subtype`, `elements` (with `type`, `content`, `bbox`), `reading_order`, `segments` (timestamped for audio/video), `global_description`.

Bounding boxes use special tokens on a 0–1000 normalized grid: `<box><x_85><y_275><x_1000><y_1000></box>`

---

### What the Perception Layer Outputs

| Input | Perception Output |
|-------|------------------|
| Document | Layout blocks + OCR + bbox + OTSL tables + LaTeX formulas + reading order |
| Chart/diagram | Markdown table (charts), Mermaid (flowcharts), point/arc/measurement (geometry) |
| Audio | Timestamps + speaker ASR + non-vocal acoustic event labels |
| Natural video | Timestamps + scene descriptions + camera motion labels |
| Text-rich video | Timestamps + ASR + OCR + `structured_report` (Markdown) |

---

### Single Unified Encoder Design

Rather than separate vision and audio towers, Youtu-Parsing-Omni uses one unified **Youtu-Omni-Encoder**: modality-specific thin stems map pixels/log-mel spectrograms to tokens; all tokens process together in a shared bidirectional Transformer with `(t, h, w)` positional encoding. Images, audio chunks, and video frames can be packed into a single forward pass.

For video, fusion layers open a new attention window at each audio-to-frame temporal boundary, so video frames attend to the sound from the same moment.

Training pipeline: SFT → schema-routed RLVR → OmniSchema-Aware On-Policy Distillation (OSAD). No separate teacher model — the model self-samples with an admission gate (JSON validity, schema conformance, box syntax, repetition), then iteratively distills from itself.

---

### Benchmarks (Self-Reported)

**OmniDocBench v1.6** (document parsing, claimed best open-weight):

| Metric | Score |
|--------|-------|
| Overall | **96.96** (vs TeleOCR 96.91) |
| Table TEDS | 96.79 |
| Formula CDM | 96.80 |

**OmniParsingBench** (cross-modal, best open-weight):

| Category | Score |
|----------|-------|
| Average | 75.08 (Gemini-3-Pro 77.44) |
| Chart | **95.02** (beats Gemini-3-Pro 92.79) |
| Audio | **78.08** (beats Gemini-3-Pro 76.74) |
| Geometry | 74.33 |
| Natural image | 62.84 |

All numbers are self-reported. The paper arXiv ID is listed as TBD — no independent external validation found yet.

---

### Inference Setup (Non-Trivial)

Two **incompatible Python environments** are required:

**vLLM (recommended; benchmark results from this):**
```bash
pip install vllm==0.19.0 transformers==5.2.0
pip install vllm-plugin-vita-omni  # custom plugin, required
# Do NOT install peft in this env
MODEL=tencent/Youtu-Parsing-Omni GPU=0 bash scripts/vllm.sh
python examples/infer_vllm.py --task document --media file.pdf
```

**Transformers inference:**
```bash
pip install transformers==5.10.2  # incompatible with vLLM env
# trust_remote_code=True, pin with --revision for safety
```

Requirements: Python ≥ 3.10, CUDA GPU (BF16 weights), `ffmpeg` for audio/video.

---

### License Warning

The license is Apache-2.0 in structure, but adds one clause: **"IS NOT INTENDED FOR USE WITHIN THE EUROPEAN UNION"** — this clause prevails in case of conflict. EU users need to be aware.

---

### Known Limits

- Self-reported benchmarks; arXiv ID TBD; no independent external validation yet
- Two incompatible environments make setup non-trivial
- `natural_image` score (62.84) notably lower than other modalities
- 88 stars, very early stage
- License has EU exclusion — not standard open source

---

### TL;DR

Youtu-Parsing-Omni is Tencent Youtu Lab's 5B omni-modal parsing model: one unified encoder for 8 input types, all tasks emit a unified OmniSchema JSON. Self-reported SOTA on OmniDocBench (96.96) and best open-weight on OmniParsingBench (75.08 vs Gemini-3-Pro 77.44). Inference requires vLLM 0.19.0 + custom plugin; setup bar is not low. License excludes EU use.

---

> 88 stars, Tencent Youtu Lab, custom license (EU excluded). For reference only — EU users check the LICENSE carefully; arXiv ID TBD.
