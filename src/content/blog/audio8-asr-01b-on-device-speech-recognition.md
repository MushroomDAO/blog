---
title: "Audio8-ASR-0.1B：0.1B 参数，LibriSpeech 2.70 WER，iPhone 本地跑只占 200MB"
titleEn: "Audio8-ASR-0.1B: 0.1B Parameters, 2.70 WER on LibriSpeech, 200 MB on-device iPhone Inference"
description: "Audio8-ASR-0.1B 是一个端到端参数量 0.324B、语言模型核心仅 0.1B 的自回归 ASR 模型，LibriSpeech test-clean WER 2.70%，Open ASR Leaderboard 七集平均 WER 7.03%。三条部署路径：Transformers（Python 服务端）、ONNX Runtime（跨平台 HTTP API）、iOS ANE（iPhone 本地，峰值内存约 200MB）。支持中英法德日韩粤 7 语言，热词增强无需微调。"
descriptionEn: "Audio8-ASR-0.1B is an autoregressive ASR model with 0.324B end-to-end parameters (0.1B LM core), achieving 2.70% WER on LibriSpeech test-clean and 7.03% average WER across the Open ASR Leaderboard seven-split. Three deployment paths: Transformers (Python server), ONNX Runtime (cross-platform HTTP API), iOS ANE (on-device iPhone, ~200 MB peak). Supports 7 languages, hotword boosting without fine-tuning."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Research"
tags: ["语音识别", "端侧AI", "开源模型", "iOS", "ONNX"]
heroImage: "../../assets/images/audio8-asr-01b-on-device-speech-recognition-banner.jpg"
---

> HuggingFace：[AutoArk-AI/Audio8-ASR-0.1B](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B)  
> GitHub：[AutoArk/open-audio-opd](https://github.com/AutoArk/open-audio-opd)  
> 论文：[arXiv:2605.28139](https://arxiv.org/abs/2605.28139)  
> 许可：CC-BY-NC-4.0（非商业）

---

## 它的位置

做语音识别，通常面临一个取舍：

- **Whisper large-v3**：精度高，参数 1.5B，服务器端跑没问题，手机跑不动
- **Whisper tiny**：参数 39M 能跑手机，但 WER 差得多
- **端侧专有方案**（Apple 语音识别 / Google STT）：精度够，但不开源、不可控、必须联网

Audio8-ASR-0.1B 的目标是填这个空白：**LM 核心只有 0.1B，端到端约 0.324B，却在公开评测上接近甚至持平大模型的表现，同时真正能在手机本地跑。**

---

## 基准成绩

在 Open ASR Leaderboard 的 7 个英文测试集（AMI / Earnings22 / GigaSpeech / LibriSpeech clean + other / SPGISpeech / VoxPopuli）：

| 测试集 | WER (%) | RTFx（H200） |
|--------|---------|------------|
| LibriSpeech test.clean | **2.70** | 687 |
| LibriSpeech test.other | 6.59 | 610 |
| SPGISpeech | 3.73 | 870 |
| VoxPopuli | 4.39 | 686 |
| GigaSpeech | 8.48 | 641 |
| AMI Cleaned | 10.99 | 396 |
| Earnings22 | 12.31 | 654 |
| **7集平均** | **7.03** | **741** |

中文（WenetSpeech）：

| 测试集 | CER (%) |
|--------|---------|
| WenetSpeech meeting | 8.842 |
| WenetSpeech net | 7.976 |

RTFx 是实时倍率（741× 意味着处理 1 秒音频只需约 1.3ms），这个数字是 H200 服务器上的测量结果，但它说明模型本身的计算量很小——这正是它能跑在手机上的根本原因。

---

## 模型结构

```
音频输入（16kHz）
   ↓
Log-Mel 特征提取
   ↓
Qwen3-ASR 音频编码器（来自 Qwen3-ASR-0.6B，冻结 + 适配）
   ↓
MLP 适配器 / 投影层
   ↓
8 层 Qwen 风格因果 LM（104M 参数）← 这是 0.1B 的部分
   ↓
文字输出
```

LM backbone 基于 [Ref-Pretrain-Qwen-104M](https://huggingface.co/MiniLLM/Ref-Pretrain-Qwen-104M)，音频编码器来自 Qwen3-ASR-0.6B，但在 Audio8 训练阶段重新训练了适配器和投影层。

端到端 unique 参数约 0.324B（含音频编码器共享权重），语言模型部分约 0.104B。

---

## 三条部署路径

### 路径一：Transformers（Python 服务端）

最快上手，适合服务端 API、本地研究、快速集成原型。

```bash
pip install transformers torch
```

```python
import torch
from transformers import AutoModelForCausalLM, AutoProcessor

model_path = "AutoArk-AI/Audio8-ASR-0.1B"
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if device == "cuda" else torch.float32

processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=dtype,
    attn_implementation="eager",
).to(device).eval()

conversation = [{
    "role": "user",
    "content": [
        {"type": "audio", "path": "audio.wav"},
        {"type": "text", "text": "Please transcribe this audio."},
    ],
}]

batch = processor.apply_chat_template(
    conversation, return_tensors="pt", sampling_rate=16000,
    audio_padding="longest", add_generation_prompt=True,
    audio_max_length=30 * 16000,
)
batch = {k: v.to(device) if hasattr(v, "to") else v for k, v in dict(batch).items()}

with torch.inference_mode():
    ids = model.generate(**batch, max_new_tokens=128, do_sample=False)

text = processor.decode(ids[0, batch["input_ids"].shape[1]:], skip_special_tokens=True).strip()
print(text)
```

命令行：

```bash
python examples/transcribe.py audio.wav --model AutoArk-AI/Audio8-ASR-0.1B
```

**适用场景**：会议记录后处理、音频内容批量转写、服务器端 API（GPU 推理，可处理高并发）。

---

### 路径二：ONNX Runtime（跨平台 HTTP API）

适合**在线 Web 应用**、Windows/Linux/macOS 本地应用、Android 集成。

提供 int4 / int8 / fp32 三种精度变体，默认 `int8+int8` 组合，峰值内存约 1.1GB（CPU）。

```bash
# 下载 ONNX Runtime 版本
git lfs install
git clone https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-onnx-runtime
cd Audio8-ASR-0.1B-onnx-runtime

python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-onnx.txt

# 启动 WebUI + HTTP API（默认端口 7860）
./run_local.sh
```

**HTTP API 集成**（适合在线应用）：

服务启动后，`POST /asr` 接收 multipart 音频文件：

```bash
# 转写本地文件
curl -X POST http://127.0.0.1:7860/asr \
  -F "audio=@recording.wav" \
  -F "max_new_tokens=256" \
  -F "cache_precision=int8" \
  | python3 -m json.tool
```

响应结构：

```json
{
  "text": "你好，能听见我说话吗？Hello, can you hear me right now?",
  "raw": "<|zh|>你好，能听见我说话吗？<|en|>Hello, can you hear me right now?",
  "elapsed_seconds": 0.404,
  "audio_seconds": 4.5,
  "generated_tokens": 17,
  "backend": "onnx_cache",
  "cache_precision": "int8",
  "audio_precision": "int8"
}
```

**Python 直接调用**：

```python
from asr_onnx_runtime import OnnxCacheAsrEngine
from pathlib import Path

engine = OnnxCacheAsrEngine("model_bundle", cache_precision="int8", audio_precision="int8")
result = engine.transcribe(Path("audio.wav").read_bytes(), max_new_tokens=256)
print(result["text"])
```

**热词增强**（产品词、专有名词，无需微调）：

```bash
curl -X POST http://127.0.0.1:7860/asr \
  -F "audio=@meeting.wav" \
  -F "hotwords=Audio8,AutoArk,OpenAI" \
  -F "hotword_start_boost=6.0"
```

有用的辅助端点：

```
GET /health          # 服务健康检查
GET /api/runtime     # 当前精度配置和可用变体
GET /metrics         # 内存占用、推理统计
POST /api/reload     # 热切换精度（无需重启）
```

---

### 路径三：iOS ANE（iPhone 本地，约 200MB）

适合**需要离线、低延迟、高隐私的 iOS 应用**（会议 App、实时字幕、语音助手）。

这条路径是 `Audio8-ASR-0.1B-iOS-ANE` 包：

- 音频编码器：Core ML `.mlmodelc`，跑在 **Apple Neural Engine**
- 解码器：ONNX Runtime int4，跑在 CPU
- 峰值内存：约 183–224MB（iPhone 实测，随机型/iOS 版本有浮动）

**iOS 集成步骤**：

```bash
brew install xcodegen

# 克隆模型包（含 Swift SDK 和 Demo App）
git lfs install
git clone https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-iOS-ANE
cd Audio8-ASR-0.1B-iOS-ANE

# 验证 Swift SDK（macOS Apple Silicon）
cd SpeechKit
swift package resolve
swift build
swift run dev-check

# 转写本地文件（CLI 验证）
swift run -c release asrkit-cli .. --file path/to/audio.wav
```

**打开 Demo App**：

```bash
cd ASRDemo
xcodegen generate
open ASRDemo.xcodeproj
# → 选择 ASRDemo target，配置签名团队，在 iPhone 上运行
```

**在自己的 App 里集成**（Swift）：

```swift
import SpeechKit
import ASRKit

// 初始化，bundle 里包含 Core ML 模型和 ONNX 解码器
let asr = try ASREngine(bundleURL: Bundle.main.url(forResource: "ASRModels", withExtension: "bundle")!)

// 转写一段录音（WAV/PCM）
let result = try await asr.transcribe(audioData: pcmData, sampleRate: 16000)
print(result.text)  // → "你好，能听见我说话吗？"
```

**延迟构成**（iPhone 实测，4.5 秒音频片段）：

| 阶段 | 耗时 |
|------|------|
| Log-Mel 特征提取 | 63ms |
| Core ML 音频塔（ANE） | 41ms |
| ONNX int4 解码（CPU） | 299ms |
| **全流程** | **404ms** |

---

## 如何做近实时 / 双工 ASR

Audio8-ASR-0.1B 本身是块式（chunk-based）模型，单次处理上限 30 秒音频。要实现**低延迟流式转写**，需要在应用层做滑动窗口：

```python
# 伪代码：滑动窗口流式转写（ONNX HTTP API 版）
import asyncio, httpx, sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000
CHUNK_SEC = 5          # 每次送入 5 秒音频
STEP_SEC = 2           # 每 2 秒触发一次转写（滑动步长）

buffer = np.zeros(0, dtype=np.float32)
async def stream_asr():
    async with httpx.AsyncClient() as client:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as mic:
            while True:
                await asyncio.sleep(STEP_SEC)
                chunk, _ = mic.read(STEP_SEC * SAMPLE_RATE)
                buffer = np.concatenate([buffer, chunk.flatten()])
                window = buffer[-CHUNK_SEC * SAMPLE_RATE:]  # 取最近 5s
                wav_bytes = to_wav_bytes(window, SAMPLE_RATE)
                r = await client.post("http://127.0.0.1:7860/asr",
                                      files={"audio": ("chunk.wav", wav_bytes)},
                                      data={"max_new_tokens": "128"})
                print("\r" + r.json()["text"], end="", flush=True)

asyncio.run(stream_asr())
```

**iOS 双工思路**：

1. 用 `AVAudioEngine` 持续录音，攒够 5s 音频
2. 每 2s 裁一个滑动窗口，调用 `ASREngine.transcribe()`
3. 用文本 diff 检测增量内容，追加到转写结果区域
4. 用户说话停顿（VAD 检测静音 800ms）时触发最终确认转写

`mel 63ms + tower 41ms` 这两步完成后就有音频特征了，解码的 299ms 是真正的"思考时间"。对于 5 秒窗口，总延迟约 400ms，体感流畅度接近实时字幕水准（非 token 级流式）。

---

## 热词增强

热词是 decode-time 逻辑推注，不改变模型权重：

```python
# ONNX Runtime Python 版
result = engine.transcribe(
    audio_bytes,
    hotwords="会议纪要,Action Item,AutoArk",
    hotword_start_boost=6.0,
    hotword_continuation_boost=8.0,
    hotword_topk=50,
)
```

适合场景：专有名词（人名、公司名、产品名）、行业术语、地名。  
注意：boost 值过高可能导致强制插入热词，建议从 `Normal`（6.0）开始调，只在必要时切 `Strong`。

---

## 语言支持

| 语言 | 代码 |
|------|------|
| 中文（普通话） | zh |
| 英文 | en |
| 粤语 | yue |
| 法语 | fr |
| 德语 | de |
| 日语 | ja |
| 韩语 | ko |

语言无需手动指定，模型从音频自动识别语言（也支持中英混说，如 banner 里的实测截图）。

---

## 选哪条路径

| 场景 | 推荐路径 |
|------|---------|
| 服务端 API、GPU 批量转写 | Transformers（Python） |
| 在线 Web 应用、跨平台桌面、Android | ONNX Runtime HTTP API |
| iOS App，离线/低延迟/隐私保护 | iOS ANE（SpeechKit） |
| 快速验证效果 | ONNX Runtime WebUI（`./run_local.sh`） |

---

## 许可证

**CC-BY-NC-4.0**：可用于研究、教育、个人项目，**不允许商业使用**。  
商业授权请联系 AutoArk-AI。

---

**HuggingFace**：  
· [Audio8-ASR-0.1B](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B)（Transformers）  
· [Audio8-ASR-0.1B-onnx-runtime](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-onnx-runtime)（ONNX HTTP API）  
· [Audio8-ASR-0.1B-iOS-ANE](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-iOS-ANE)（Swift SDK）  

**论文**：[arXiv:2605.28139](https://arxiv.org/abs/2605.28139)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Audio8-ASR-0.1B: 0.1B Parameters, 2.70 WER on LibriSpeech, 200 MB on iPhone

> HuggingFace: [AutoArk-AI/Audio8-ASR-0.1B](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B)  
> Paper: [arXiv:2605.28139](https://arxiv.org/abs/2605.28139) · License: CC-BY-NC-4.0

---

### What It Is

Audio8-ASR-0.1B is an autoregressive ASR model with a 0.1B LM core (0.324B end-to-end). It achieves 2.70% WER on LibriSpeech test-clean and 7.03% average WER across the Open ASR Leaderboard 7-split — competitive with models several times larger — while fitting in 200 MB on an iPhone running on Apple Neural Engine.

Architecture: Qwen3-ASR audio encoder → MLP adapter/projector → 8-layer Qwen-style causal LM (104M params). Languages: English, Chinese (Mandarin + Cantonese), French, German, Japanese, Korean.

---

### Benchmark

| Dataset | WER (%) | RTFx (H200) |
|---------|---------|------------|
| LibriSpeech test.clean | **2.70** | 688× |
| LibriSpeech test.other | 6.59 | 611× |
| SPGISpeech | 3.73 | 870× |
| VoxPopuli | 4.39 | 686× |
| GigaSpeech | 8.48 | 641× |
| Earnings22 | 12.31 | 654× |
| **7-split mean** | **7.03** | **741×** |

---

### Three Deployment Paths

**Path 1 — Transformers (Python server, GPU)**

```python
from transformers import AutoModelForCausalLM, AutoProcessor
processor = AutoProcessor.from_pretrained("AutoArk-AI/Audio8-ASR-0.1B", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("AutoArk-AI/Audio8-ASR-0.1B", trust_remote_code=True, torch_dtype="auto").cuda().eval()
# ... standard generate() pipeline
```

Best for: server-side batch transcription, GPU inference API.

**Path 2 — ONNX Runtime (cross-platform HTTP API)**

```bash
git clone https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-onnx-runtime
cd Audio8-ASR-0.1B-onnx-runtime
pip install -r requirements-onnx.txt
./run_local.sh   # → http://127.0.0.1:7860
```

```bash
curl -X POST http://127.0.0.1:7860/asr -F "audio=@audio.wav"
# → {"text": "...", "elapsed_seconds": 0.4, ...}
```

Precision variants: fp32 / int8 (default) / int4. Peak memory: ~1.1 GB CPU.  
Best for: web apps, cross-platform desktop, Android integration.

**Path 3 — iOS ANE (Swift SDK, ~200 MB)**

```bash
git clone https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-iOS-ANE
cd Audio8-ASR-0.1B-iOS-ANE/SpeechKit
swift run dev-check
swift run -c release asrkit-cli .. --file audio.wav
```

Audio tower runs on Apple Neural Engine (Core ML), decoder on CPU (ONNX int4). On-device, no network required. Demo app in `ASRDemo/` (XcodeGen → Xcode → iPhone).

End-to-end latency on iPhone (4.5s audio): mel 63ms + ANE tower 41ms + CPU decode 299ms = **404ms total**.

---

### Near-Realtime / Duplex ASR

Audio8 processes up to 30-second chunks. For streaming, implement a sliding window at the application layer:

- Every 2 seconds, grab the last 5 seconds of mic audio
- POST to `/asr`, display incremental transcript
- On voice-activity silence (800ms), commit final result

404ms end-to-end for a 5s window is sufficient for near-realtime caption display.

---

### Hotword Boosting

No fine-tuning required. Inject proper nouns at decode time:

```python
result = engine.transcribe(audio_bytes, hotwords="ProductName,CompanyName")
```

Available in all three deployment paths.

---

**License: CC-BY-NC-4.0** — research and personal use permitted; commercial use requires a separate license from AutoArk-AI.

© 2026 Author: Mycelium Protocol
