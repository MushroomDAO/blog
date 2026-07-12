---
title: "Higgs TTS 3 部署指南：21 种情感控制，给游戏角色和 AI 助手配上真实的声音"
titleEn: "Higgs TTS 3 Deployment Guide: 21 Emotion Tokens for Game Characters and AI Assistants"
description: "Boson AI 开源语音合成引擎 Higgs TTS 3：21 种情感控制，102 语言，零样本声音克隆。5 分钟 API 接入，本地部署全流程。"
descriptionEn: "Boson AI's Higgs TTS 3 open-source TTS: 21 emotion tokens, 102 languages, zero-shot voice cloning. 5-minute API integration or self-hosted deployment guide."
pubDate: "2026-07-11"
updatedDate: "2026-07-11"
category: "Tech-Experiment"
tags: ["TTS", "语音合成", "开源"]
heroImage: "../../assets/images/higgs-tts3-emotional-voice-game-assistant-guide-banner.jpg"
---

> Boson AI 于 2026 年 6 月 4 日开源 **Higgs TTS 3**——一个原生支持情感控制、副语言学特征（笑声、哭声、叹气）和零样本声音克隆的语音合成引擎。本文是面向游戏开发者、互动小说作者、AI 助手开发者的部署配置指南。

---

## 一、为什么 Higgs TTS 3 值得关注

| 能力 | 说明 |
|------|------|
| 情感控制 | 21 种情感 token（欣喜/愤怒/悲伤/恐惧等），句首放置即生效 |
| 音效内联 | 9 种副语言学音效（笑声/哭声/叹气/咳嗽等），直接嵌入文本 |
| 声音克隆 | 零样本——提供一段参考音频即可克隆任意声音，无需训练 |
| 语言支持 | 102 种语言，中文/英语/日语/韩语/法语等主流语言 WER < 5% |
| 模型规模 | Qwen3-4B 骨架 + 8 码本音频预测头，总参数 ~5B |
| 延迟 | 单并发首帧延迟 617ms，RTF=0.147（远快于实时） |

---

## 二、接入方式选择

### 路径 A：托管 API（无 GPU，5 分钟接入）

适合个人项目、原型验证、轻度使用：

```bash
curl https://api.boson.ai/v1/audio/speech \
  -H "Authorization: Bearer $BOSON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "higgs-audio-v3-tts", "input": "你好，今天心情不错！"}' \
  --output out.mp3
```

申请 API Key：[boson.ai/workspace](https://boson.ai/workspace)（免费限速预览）

---

### 路径 B：本地部署（需 ≥24GB VRAM）

模型权重 9.32 GB，官方测试硬件 H100 80GB，A100 40G/80G 也可运行。

**步骤 1：下载模型**

```bash
export HF_TOKEN=hf_xxxxxxxx
huggingface-cli download bosonai/higgs-tts-3-4b
```

**步骤 2：启动服务（SGLang-Omni，推荐）**

```bash
# Docker 方式
docker pull lmsysorg/sglang-omni:dev
docker run -it --gpus all --shm-size 32g --ipc host --network host --privileged \
  lmsysorg/sglang-omni:dev /bin/zsh

# 容器内
git clone https://github.com/sgl-project/sglang-omni.git && cd sglang-omni
uv venv .venv -p 3.12 && source .venv/bin/activate
uv pip install -v -e .

sgl-omni serve \
  --model-path bosonai/higgs-tts-3-4b \
  --port 8000
```

**备选：vLLM-Omni**

```bash
vllm-omni serve bosonai/higgs-tts-3-4b \
  --host 0.0.0.0 --port 8095 \
  --trust-remote-code --omni
```

---

## 三、基础合成

```python
import requests

resp = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={"input": "你好，今天天气怎么样？"},
)
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

---

## 四、情感控制 Token 完整列表

格式：句首放置 `<|emotion:名称|>`，可叠加韵律控制。

### 情感类（21 种）

| Token | 含义 | Token | 含义 |
|-------|------|-------|------|
| `elation` | 欣喜 | `helplessness` | 无助 |
| `amusement` | 逗乐 | `sadness` | 悲伤 |
| `enthusiasm` | 热情 | `shame` | 羞耻 |
| `determination` | 坚定 | `fear` | 恐惧 |
| `pride` | 自豪 | `anger` | 愤怒 |
| `contentment` | 满足 | `disgust` | 厌恶 |
| `affection` | 温情 | `bitterness` | 苦涩 |
| `relief` | 释怀 | `longing` | 思念 |
| `contemplation` | 沉思 | `arousal` | 激动 |
| `confusion` | 困惑 | `awe` | 敬畏 |
| `surprise` | 惊讶 | | |

### 风格类（3 种）

`singing`（哼唱）· `shouting`（高喊）· `whispering`（耳语）

### 音效类（9 种，内联放置）

`laughter`（笑声）· `crying`（哭声）· `sigh`（叹气）· `cough`（咳嗽）· `humming`（哼声）· `scream`（尖叫）· `sniff`（抽鼻）· `burping`（打嗝）· `sneeze`（打喷嚏）

> **规则**：音效 token 后紧跟拟声词，无空格。如：`<|sfx:laughter|>Haha`

### 韵律控制

| 控制 | Token |
|------|-------|
| 速度 | `speed_very_slow` / `speed_slow` / `speed_fast` / `speed_very_fast` |
| 音高 | `pitch_low`（-3 半音） / `pitch_high`（+2.5 半音） |
| 表达 | `expressive_high` / `expressive_low` |
| 停顿 | `pause`（0.4–0.7s） / `long_pause`（0.7–1.5s） |

---

## 五、场景示例

### 游戏：NPC 对话

```python
resp = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "<|emotion:anger|><|prosody:expressive_high|>你竟然敢背叛我！<|sfx:laughter|>Haha，现在后悔还来得及吗？",
        "temperature": 0.8,
        "top_k": 50,
    },
)
```

### 互动小说：情绪化叙述

```python
resp = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "<|emotion:sadness|><|prosody:speed_slow|>他走了，就这样走了。<|sfx:sigh|>Hmm……<|prosody:long_pause|>我站在原地，不知道该说什么。",
        "temperature": 0.9,
    },
)
```

### AI 情感助手：陪伴回应

```python
resp = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "<|emotion:affection|>我在呢，别担心。<|prosody:expressive_high|>你已经做得很好了！",
        "temperature": 0.7,
    },
)
```

---

## 六、声音克隆

```python
resp = requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "这是克隆声音说的一段话。",
        "references": [{
            "audio_path": "ref.wav",          # 参考音频
            "text": "这是参考音频的文本内容",   # 强烈推荐填写，显著提升克隆质量
        }],
        "temperature": 0.8,
        "top_k": 50,
    },
)
```

---

## 七、流式输出（实时播放）

```python
import wave, requests

with requests.post(
    "http://localhost:8000/v1/audio/speech",
    json={
        "input": "<|emotion:enthusiasm|>欢迎来到这个世界！",
        "stream": True,
        "response_format": "pcm",
    },
    stream=True,
) as resp:
    sample_rate = int(resp.headers.get("x-sample-rate", 24000))
    chunks = [c for c in resp.iter_content(chunk_size=None) if c]
    # 实时场景：直接把 chunk 送入 pyaudio/sounddevice 播放

with wave.open("output.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate)
    f.writeframes(b"".join(chunks))
```

首帧延迟 < 1 秒（H100 单并发实测 617ms）。

---

## 八、与同类模型对比

| 模型 | SeedTTS WER↓ | 情感控制 | 声音克隆 | 多语言 |
|------|-------------|---------|---------|--------|
| **Higgs TTS 3** | **1.11** | ✅ 43 种 token | ✅ 零样本 | 102 语言 |
| Fish Audio S2 Pro | 1.31 | 有限 | ✅ | 较少 |
| MOSS-TTS-v1.5 | 1.73 | 无 | 有限 | 有限 |
| Qwen3-TTS-1.7B | 1.30 | 无 | 无 | 中英为主 |
| ChatTTS | — | 无 | 无 | 仅中文 |

---

## 九、许可证说明

- 研究 + 非商业：免费
- **创作者豁免**：YouTuber/播客/视频创作者商业内容免费使用，需注明"This audio was created with Boson AI's Higgs Audio"
- 商业部署（嵌入产品/API 服务）：需单独授权

---

GitHub：[boson-ai/higgs-audio](https://github.com/boson-ai/higgs-audio)

HuggingFace：[bosonai/higgs-tts-3-4b](https://huggingface.co/bosonai/higgs-tts-3-4b)（9.32 GB）

API 文档：[docs.boson.ai](https://docs.boson.ai/models/higgs-audio-tts/overview)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Higgs TTS 3 Deployment Guide: Emotional Voice for Games and AI Assistants

> Boson AI open-sourced Higgs TTS 3 on June 4, 2026 — a production-grade TTS engine with 43 emotion/style control tokens, 102-language support, and zero-shot voice cloning.

---

### Why It Matters

Higgs TTS 3 is the first TTS model to combine all three of: fine-grained emotion tokens, paralinguistic sound effects (laughter, crying, sighs inline in text), and zero-shot voice cloning in one open-weight model. The result is AI-generated speech that feels like a real performance, not a narrator.

---

### Two Integration Paths

**Cloud API (5 minutes, no GPU)**:
```bash
curl https://api.boson.ai/v1/audio/speech \
  -H "Authorization: Bearer $BOSON_API_KEY" \
  -d '{"model": "higgs-audio-v3-tts", "input": "Hello!"}' -o out.mp3
```
Get key at: boson.ai/workspace

**Self-hosted (≥24GB VRAM)**:
```bash
huggingface-cli download bosonai/higgs-tts-3-4b  # 9.32 GB
sgl-omni serve --model-path bosonai/higgs-tts-3-4b --port 8000
```

---

### Emotion Control (21 tokens)

Place at sentence start: `<|emotion:anger|>`, `<|emotion:sadness|>`, `<|emotion:affection|>`, etc.

Sound effects inline: `<|sfx:laughter|>Haha` · `<|sfx:sigh|>Hmm` · `<|sfx:crying|>Oh no`

Prosody: `<|prosody:speed_slow|>` · `<|prosody:expressive_high|>` · `<|prosody:long_pause|>`

---

### Game NPC Example

```python
resp = requests.post("http://localhost:8000/v1/audio/speech", json={
    "input": "<|emotion:anger|><|prosody:expressive_high|>You dare betray me! <|sfx:laughter|>Haha — it's too late.",
    "temperature": 0.8,
})
```

---

### Voice Cloning

```python
resp = requests.post("http://localhost:8000/v1/audio/speech", json={
    "input": "Cloned voice speaking now.",
    "references": [{"audio_path": "ref.wav", "text": "Reference text here"}],
})
```

---

### Benchmark

WER (lower = better): Higgs TTS 3 scores **1.11** on SeedTTS vs Fish Audio 1.31, MOSS 1.73, Qwen3 1.30. Win-rate in human preference: **53.65%** overall, **68.57%** on paralinguistics.

License: free for research + content creators (attribution required), commercial deployment needs licensing.

GitHub: github.com/boson-ai/higgs-audio · HuggingFace: bosonai/higgs-tts-3-4b

© 2026 Author: Mycelium Protocol
