---
title: "FunClip：用语音识别做视频剪辑的索引层"
titleEn: "FunClip: Using Speech Recognition as a Video Clipping Index Layer"
description: "modelscope/FunClip，MIT，6363 stars，Python，v2.2.1，阿里巴巴达摩院通义实验室 FunASR 团队开源。核心路径：Paraformer-Large（ModelScope 1300 万下载）把视频转成带毫秒时间戳的文字稿，用户或大模型在文字上选段，系统反向定位到视频时间轴完成裁剪。支持 CAM++ 说话人识别按人剪辑、SeACo-Paraformer 热词定制、MOSS-Transcribe-Diarize 长音频说话人分离、Gradio 本地 Web 界面、LLM 智能选段，以及两阶段 CLI 工作流。"
descriptionEn: "modelscope/FunClip, MIT, 6363 stars, Python, v2.2.1, open-sourced by Alibaba DAMO FunASR team. Core path: Paraformer-Large (13M+ ModelScope downloads) transcribes video to text with millisecond timestamps; users or LLMs select segments in text; system reverse-maps back to the video timeline for clipping. Supports CAM++ speaker diarization, SeACo-Paraformer hotwords, MOSS-Transcribe-Diarize for long-form audio, local Gradio UI, LLM-assisted segment selection, and a two-stage CLI workflow."
pubDate: 2026-10-05
heroImage: "../../assets/images/funclip-video-speech-index-clipping-funasr-paraformer-banner.jpg"
category: "Tech-Experiment"
tags: ["视频剪辑", "语音识别", "FunASR", "Paraformer", "开源工具", "本地部署"]
lang: "zh-CN"
wechatTitle: "FunClip：用语音识别做视频剪辑索引"
wechatDigest: "MIT 6363星；Paraformer大模型；语音→文字时间戳→选段→裁剪；Gradio本地可部署"
---

传统视频剪辑工具要求你知道想要的画面在哪一秒。找段落的方法是拖进度条，看画面，再拖，再看。这个过程在短视频时代尚可接受，碰到会议录像、访谈素材或讲座录制，每小时视频可能需要一个人花一小时以上才能把需要的段落定位出来。

FunClip 给这个问题换了一个视角：与其在视频维度上找位置，不如先把视频转换成一个文字维度的索引，再在文字上操作，让系统负责反向映射回视频时间轴。

这条路径能走通的前提是：ASR 的时间戳精度要足够高，且模型要足够快才能被日常使用。Paraformer-Large 满足了这两个条件。

GitHub: https://github.com/modelscope/FunClip | ⭐ 6363 | MIT | Python | v2.2.1

---

## 核心工作流：两阶段定位

FunClip 的设计从技术上被拆成两个清晰的阶段：

**第一阶段：转录**

```bash
python funclip/videoclipper.py --stage 1 \
    --file your_video.mp4 \
    --output_dir ./output
```

执行完毕后，`output/` 里有完整的文字稿和全视频 SRT 字幕文件。每个词都带毫秒级时间戳，这是后续反向定位的基础。

**第二阶段：裁剪**

```bash
python funclip/videoclipper.py --stage 2 \
    --file your_video.mp4 \
    --output_dir ./output \
    --dest_text '你想要的那句话' \
    --start_ost 0 \
    --end_ost 100 \
    --output_file './output/res.mp4'
```

`--dest_text` 接受你从第一阶段文字稿里复制出来的任意文本片段，系统找到对应的时间区间，加上 `start_ost`/`end_ost` 的毫秒偏移余量，完成裁剪。

用 Gradio 界面操作时这两步合并成一个交互流程：上传视频 → 等转录完成 → 在文字稿上框选 → 点击"裁剪"按钮。

---

## 模型层的选择

默认用 Paraformer-Large，但 v2.2.x 已经支持多个模型切换：

| 场景 | 启动命令 |
|------|---------|
| 默认中文视频（Paraformer） | `python funclip/launch.py` |
| 精准转录（旗舰 Fun-ASR-Nano） | `python funclip/launch.py -m fun-asr-nano` |
| 多语言+情感+音频事件检测 | `python funclip/launch.py -m sensevoice` |
| 长音频+说话人分离（MOSS） | `python funclip/launch.py --model moss --moss-backend vllm` |
| 英语视频 | `python funclip/launch.py -l en` |

**Paraformer-Large** 是 ModelScope 上中文 ASR 下载量最高的开源模型之一，超过 1300 万次。它的优势是在端到端的前向传播里同时预测文字和时间戳，不需要单独的对齐步骤，保证了剪辑定位精度。

**CAM++ 说话人识别**：识别出谁在说话并打上 `spkS01`、`spkS02` 标签。这让按人剪辑成为可能——如果你需要某人的全部发言，直接选说话人 ID 而不是逐段复制文字。MOSS 路径使用端到端的说话人分离，不需要额外的 VAD 模型，但精确的任意文本定位仍然依赖 Paraformer 的 token 级时间戳。

**SeACo-Paraformer 热词**：对专有名词、人名、产品名等识别率低的词可以预先注入，提升这些词的识别准确率。在会议场景下尤其有用。

---

## 安装

```bash
git clone https://github.com/modelscope/FunClip.git
cd FunClip
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python funclip/launch.py
```

访问 `http://localhost:7860`。模型权重首次启动时自动下载（不包含在源码包里）。国内网络会自动路由到 ModelScope 镜像。

几个注意点：
- 需要 Python 3.12，安装文档里有 Linux CPU 和 Windows 的具体说明
- `funasr>=1.4.9` 是硬性依赖，老安装需要手动升级
- v2.2.1 的字幕渲染改用 Pillow，不再依赖 ImageMagick（除非你用 MoviePy 的 TextClip）
- Transformers 4.x 环境，不要和其他依赖 Transformers 5.x 的项目混用

---

## LLM 辅助选段

从 v2.x 开始，FunClip 支持把转录结果喂给 LLM 让它代替人工决定选哪些段落。工作流：转录 → 文字稿传给 LLM → LLM 返回 `N. [start-end] text` 格式的选段列表 → "AI Clip" 按钮直接裁剪。

内置支持 OrcaRouter（OpenAI-compatible 路由网关，模型选 `orcarouter/auto`），也支持 TwelveLabs Pegasus——Pegasus 是视频理解模型，能看画面和音频而不只是文字稿，对纯靠文字无法判断的场景（动作、场景切换、画面事件）更有优势，但需要 `pip install twelvelabs` 和 API key。

---

## 生态位置

FunClip 在 FunAudioLLM 家族里负责视频应用层：

- **FunASR**：工业级语音识别工具包（VAD/ASR/标点/说话人）
- **Fun-ASR-Nano**：旗舰端到端 LLM-based ASR，31 语言，有 GGUF 版可在本地跑
- **SenseVoice**：多语言语音理解，有 GGUF 版
- **CosyVoice**：多语言语音合成，零样本克隆

FunClip 不是孤立工具，是这个生态的上层应用接口。如果只需要离线语音转录而不需要剪辑 UI，可以直接用 Fun-ASR-Nano-GGUF 或 SenseVoiceSmall-GGUF 的 llama.cpp 运行时。

---

## 使用边界

**没有离线打包安装器**：需要 Python 环境和 git，首次用模型时要联网下载权重。

**中文优化**：Paraformer-Large 是中文 ASR 模型，英文用 Paraformer-English 模型效果好，但生态深度不及中文方向。多语言方向依赖 SenseVoice 或 Fun-ASR-Nano。

**MOSS 的限制**：MOSS 的时间戳是段级而非 token 级，精确的任意文本定位（比如剪一句话的后半段）仍然需要 Paraformer。同时 MOSS 需要 vLLM 服务，门槛更高。

**LLM 选段质量**：AI Clip 的结果质量取决于 LLM 理解转录文字的能力，长音频的全文字稿可能超出上下文窗口。

---

> MIT 开源。阿里巴巴达摩院 FunASR 团队维护，v2.2.1 截至 2026-09-01。开源仅供学习参考。

---

<!--EN-->

## FunClip: Using Speech Recognition as a Video Clipping Index Layer

Traditional video editing tools require you to know which second contains the footage you need. The workflow is: drag the timeline, look, drag again, look again. This is manageable for short videos, but with conference recordings, interview footage, or lecture recordings, locating the needed segments in a one-hour video can easily take more than an hour.

FunClip reframes this: instead of searching in the video dimension, first convert the video into a text-dimension index, operate on the text, and let the system handle the reverse mapping back to the video timeline.

This works because Paraformer-Large delivers both the millisecond-precision timestamps and the inference speed necessary for daily use.

GitHub: https://github.com/modelscope/FunClip | ⭐ 6363 | MIT | Python | v2.2.1

---

### Two-Stage Workflow

**Stage 1 — Transcribe**: Convert video to timestamped text. Every word gets a millisecond timestamp that enables subsequent reverse lookup.

**Stage 2 — Clip**: Pass a text fragment copied from the transcript to `--dest_text`; the system finds the corresponding time range and adds millisecond padding via `--start_ost`/`--end_ost` offsets.

In the Gradio UI these two stages merge into one interactive flow: upload → wait for transcription → select in the text → click "Clip."

---

### Model Options

| Scenario | Command |
|----------|---------|
| Default Chinese (Paraformer) | `python funclip/launch.py` |
| High-accuracy (Fun-ASR-Nano) | `python funclip/launch.py -m fun-asr-nano` |
| Multilingual + emotion + audio events | `python funclip/launch.py -m sensevoice` |
| Long-form + speaker diarization (MOSS) | `python funclip/launch.py --model moss` |
| English | `python funclip/launch.py -l en` |

**Paraformer-Large** predicts text and timestamps in a single end-to-end forward pass — no separate alignment step. Over 13 million downloads on ModelScope.

**CAM++ speaker recognition** assigns `spkS01`, `spkS02` labels, enabling clip-by-speaker without manually selecting each utterance.

**SeACo-Paraformer hotwords**: inject domain-specific terms (proper nouns, product names) to improve recognition accuracy.

**MOSS path** provides long-form ASR + anonymous speaker labels in a single model, but segment-level timestamps only — precise arbitrary text clipping still requires Paraformer's token timestamps.

---

### LLM-Assisted Selection

v2.x adds an AI Clip mode: transcript → LLM → `N. [start-end] text` segment list → direct clip. Supports OrcaRouter (any model via `orcarouter/auto`) and TwelveLabs Pegasus (video understanding model that reads visuals + audio, not just the transcript — useful when text alone is ambiguous).

---

### Ecosystem Position

FunClip is the application layer of the FunAudioLLM family. If you only need offline transcription without the clipping UI, use Fun-ASR-Nano-GGUF or SenseVoiceSmall-GGUF directly via llama.cpp runtime — lower overhead, no Gradio dependency.

---

### Limitations

No offline installer — requires Python 3.12, git, and network access for model weight download. English coverage lighter than Chinese. MOSS requires a vLLM service with higher setup overhead. LLM segment selection quality depends on the LLM's ability to process the full transcript, which may exceed context windows for long recordings.

---

> MIT. Maintained by Alibaba DAMO FunASR team, v2.2.1 as of 2026-09-01. For technical reference only.
