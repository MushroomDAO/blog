---
title: "自己动手搭全双工 AI 语音通话：LiveKit Agents + 阿里云 STT + Cartesia TTS"
titleEn: "Build a Full-Duplex AI Voice Call App: LiveKit Agents + Aliyun STT + Cartesia TTS"
description: "用 LiveKit Agents 搭一路全双工 AI 语音/视频通话：用户说话 → 流式 STT（阿里云） → 大模型推理 → 流式 TTS（Cartesia）→ 播放。支持打断、抢先生成、摄像头/屏幕共享；两端都有免费额度，本文给出完整代码路径和架构讲解。"
descriptionEn: "Build a full-duplex AI voice/video call pipeline with LiveKit Agents: mic → streaming STT (Aliyun) → LLM → streaming TTS (Cartesia) → speaker. Supports user interruptions, preemptive generation, camera and screen sharing. Both STT and TTS have free tiers. Complete code walkthrough and architecture breakdown."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Tech-Experiment"
tags: ["LiveKit", "语音AI", "全双工", "STT", "TTS", "Python", "实时通话"]
heroImage: "../../assets/images/livekit-full-duplex-ai-voice-video-call-banner.jpg"
---

> 核心仓库：[livekit/agents](https://github.com/livekit/agents) · ⭐ 11,369 · Apache-2.0  
> 入门模板：[livekit-examples/agent-starter-python](https://github.com/livekit-examples/agent-starter-python)  
> 前端模板：[livekit-examples/agent-starter-react](https://github.com/livekit-examples/agent-starter-react)  
> 示例库：[livekit-examples/python-agents-examples](https://github.com/livekit-examples/python-agents-examples) · 50+ 个场景

---

## 全双工和半双工有什么区别

普通语音助手大多是**半双工**的：用户说完 → 检测到静音停止 → AI 开始处理 → AI 回复。在这个模型里，AI 说话期间不监听用户，用户也没法打断。

**全双工**的行为不同：AI 说话的同时，麦克风全程开着，用户随时可以插话打断。收到打断信号后，AI 立刻停止播放并重新响应。这才是电话通话的交互体感。

LiveKit Agents 从架构上原生支持全双工，主要靠两个机制：

1. **`preemptive_generation=True`**：不等 STT 确认用户说完，收到中间结果就提前启动 LLM 推理，减少感知延迟。
2. **`TurnDetector`**：语义理解 + 声学特征（语调、停顿）联合判断是否轮到 AI 说话，比单纯靠静音检测准确得多。

---

## 整体架构

```
用户麦克风
    │
    ▼
LiveKit Cloud 房间（WebRTC）
    │  音频轨道
    ▼
AgentSession
    ├─ STT（阿里云流式识别）→ 逐词输出文字
    ├─ TurnDetector（判断用户轮次结束）
    ├─ LLM（OpenAI / Claude / 任意大模型）
    └─ TTS（Cartesia Sonic-3）→ 流式音频
         │
         ▼
    LiveKit Cloud 房间
         │
         ▼
    用户扬声器
```

摄像头或屏幕共享走同一条 WebRTC 通道，Agent 通过视频流订阅最新帧，在每个用户轮次结束时把截帧注入多模态消息。

---

## 环境准备

### 1. 安装依赖

```bash
pip install \
  "livekit-agents[openai,aliyun,cartesia,silero,turn-detector]>=1.0" \
  livekit-plugins-noise-cancellation
```

### 2. 申请免费额度

**阿里云实时语音识别**（STT，中文识别最好）：
- 控制台搜「智能语音交互」→ 免费试用
- 新用户每月赠 10 小时实时识别额度
- 获得 `ALIYUN_ACCESS_KEY_ID`、`ALIYUN_ACCESS_KEY_SECRET`、`ALIYUN_APP_KEY`

**Cartesia**（TTS，支持音色克隆）：
- 官网注册 → 每月 10 万字符免费
- 获得 `CARTESIA_API_KEY`
- 内置音色 ID：`9626c31c-bec5-4cca-baa8-f8ba9e84c8bc`（可换成克隆的自定义音色）

**LiveKit Cloud**：
- 免费套餐包含每月 10 万分钟中继
- 获得 `LIVEKIT_URL`、`LIVEKIT_API_KEY`、`LIVEKIT_API_SECRET`

把这些写进 `.env`：

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxx
ALIYUN_ACCESS_KEY_ID=LTAIxxxxxxxxxxxx
ALIYUN_ACCESS_KEY_SECRET=xxxxxxxxxxxxxxxx
ALIYUN_APP_KEY=xxxxxxxx
CARTESIA_API_KEY=sk-xxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxx
```

---

## 核心代码：全双工语音 Agent

```python
# agent.py
import asyncio
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.voice import TurnHandlingOptions
from livekit.plugins import aliyun, cartesia, openai, turn_detector
from livekit.plugins import noise_cancellation as nc

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""你是一个友好的 AI 助手。
用自然、口语化的中文回答，避免使用 Markdown 格式。
回答简洁——这是语音对话，不是文章。""",
        )

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        # STT：阿里云流式识别，中文优秀
        stt=aliyun.STT(language="zh-CN"),

        # LLM：可换成任意支持流式的模型
        llm=openai.LLM(model="gpt-4o-mini"),

        # TTS：Cartesia Sonic-3，延迟低，支持音色克隆
        tts=cartesia.TTS(
            model="sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",  # 或换成克隆音色 ID
        ),

        # 轮次检测：语义 + 声学联合判断，比单纯静音检测准
        turn_handling=TurnHandlingOptions(
            turn_detection=turn_detector.EOUModel(),
        ),

        # 抢先生成：STT 中间结果出来就启动 LLM，减少感知延迟
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options={
            "audio_input": {
                # AI 消噪：过滤背景噪声、回声
                "noise_cancellation": nc.BVC(),
            }
        },
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

启动：

```bash
python agent.py dev
```

---

## 全双工的关键机制

### 抢先生成（preemptive_generation）

```
用户在说话中...
STT 出中间结果: "帮我查一下明天北京的"
              ↓
         LLM 已经开始推理（不等用户说完）
用户继续: "天气"
STT 最终结果: "帮我查一下明天北京的天气"
              ↓
         LLM 继续基于最终结果完成回答
```

如果用户说了一半改变了意思，框架会取消上一次推理并用新的完整结果重新推理。整个过程用户无感知，只感觉响应极快。

### 打断处理

用户在 AI 说话时开口：

1. VAD 检测到用户语音
2. TTS 播放立即停止
3. STT 开始识别新的用户输入
4. 轮次检测器等待用户说完
5. LLM 基于新输入生成回复

整个切换链路完全自动，不需要写任何打断逻辑。

---

## 加入摄像头和屏幕共享（多模态）

在基础 Agent 上扩展视频处理能力：

```python
import asyncio
from livekit import rtc
from livekit.agents import Agent, AgentSession, get_job_context
from livekit.agents.multimodal import ImageContent

class VisionAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="你能看到用户的摄像头画面或屏幕共享。用中文描述和分析你看到的内容。",
        )
        self._latest_frame = None
        self._video_stream = None

    async def on_enter(self):
        room = get_job_context().room

        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            # 订阅摄像头或屏幕共享视频轨道
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                self._create_video_stream(track)

    def _create_video_stream(self, track):
        self._video_stream = rtc.VideoStream(track)

        async def read_stream():
            async for event in self._video_stream:
                # 持续更新最新帧，不丢帧但也不堆积
                self._latest_frame = event.frame

        asyncio.create_task(read_stream())

    async def on_user_turn_completed(self, turn_ctx, new_message):
        # 每次用户说完话，把最新截帧注入这轮消息
        if self._latest_frame is not None:
            new_message.content.append(
                ImageContent(image=self._latest_frame)
            )
            self._latest_frame = None  # 消费后清空，避免重复发送
```

这个模式的优点：只在用户说话时抓取帧，不会因为持续发图片而撑大 token 用量。用户每说一次话，AI 就"看"一次当前画面并结合语音内容一起回答。

---

## 前端接入

LiveKit 提供各平台官方 SDK，都支持同一套房间逻辑：

### Web（React + Next.js）

用 [agent-starter-react](https://github.com/livekit-examples/agent-starter-react) 模板：

```bash
npx create-next-app -e https://github.com/livekit-examples/agent-starter-react
```

关键组件：

```tsx
import { LiveKitRoom, useLocalParticipant } from "@livekit/components-react";

export default function CallPage() {
  return (
    <LiveKitRoom
      serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
      token={roomToken}
      connect={true}
    >
      <VoiceCallUI />
    </LiveKitRoom>
  );
}

function VoiceCallUI() {
  const { localParticipant } = useLocalParticipant();

  const enableCamera = () => localParticipant.setCameraEnabled(true);
  const shareScreen = () => localParticipant.setScreenShareEnabled(true);

  return (
    <div>
      <button onClick={enableCamera}>开启摄像头</button>
      <button onClick={shareScreen}>分享屏幕</button>
    </div>
  );
}
```

### iOS（Swift）

```swift
import LiveKit

let room = Room()
try await room.connect(url, token: token)

// 发布麦克风
try await room.localParticipant.setMicrophone(enabled: true)

// 发布摄像头
try await room.localParticipant.setCamera(enabled: true)
```

### Flutter / React Native / Android

LiveKit 官方均有对应 SDK：`livekit_client`（Flutter）、`@livekit/react-native`、`io.livekit.android`。接入模式相同——连接房间、发布音频轨道、订阅 Agent 的音频回放。

---

## 部署

Agent Worker 是一个常驻进程，监听 LiveKit Cloud 分配的任务：

```bash
# 生产环境启动
python agent.py start

# Docker
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY agent.py .
CMD ["python", "agent.py", "start"]
```

LiveKit Cloud 在用户发起通话时自动将任务路由到可用的 Worker。如果多个用户同时通话，框架会在多个 Worker 实例之间做负载均衡。

---

## 音色克隆（Cartesia）

Cartesia 的音色克隆可以用 5-10 分钟的音频训练出一个新音色：

1. Cartesia 控制台 → Voices → Create Voice
2. 上传录音（安静环境，清晰发音）
3. 获得新 voice ID

替换 agent 里的 voice 参数：

```python
tts=cartesia.TTS(
    model="sonic-3",
    voice="你的克隆音色ID",
)
```

克隆音色和原版 Sonic-3 的延迟、质量一致，只是换了发音人。可以做专属品牌语音、角色扮演、人设一致的 AI 助手。

---

## 和其他方案的对比

| 方案 | 全双工 | 延迟 | 部署 | 中文支持 |
|------|--------|------|------|----------|
| LiveKit Agents | ✅ 原生 | 低（WebRTC） | 自托管 / Cloud | ✅（插件可选） |
| OpenAI Realtime API | ✅ | 低 | 仅 OpenAI | 有限 |
| Vocode | ✅ | 中 | 自托管 | 需自配 |
| WebRTC + 自建 STT/TTS | 自己实现 | 取决于实现 | 完全自控 | 自配 |

LiveKit Agents 的优势是**插件生态**：STT/TTS/LLM 都可以单独替换，不锁定某家厂商，而且 WebRTC 基础设施处理好了 NAT 穿透、音频回声消除、网络抖动缓冲这些底层问题。

---

## 免费额度能跑多久

| 服务 | 免费额度 | 大约能跑多少对话 |
|------|---------|----------------|
| LiveKit Cloud | 每月 10 万分钟 | 约 1,667 小时通话 |
| 阿里云 STT | 每月 10 小时 | 约 600 分钟语音输入 |
| Cartesia | 每月 10 万字符 | 约 1,000 次中等长度回复 |
| OpenAI GPT-4o mini | 约 5 美元起充 | 极低成本 |

做 demo 和早期测试，三个免费套餐叠在一起完全够用，不需要先掏钱。

---

## 快速开始

```bash
# 1. 克隆模板
git clone https://github.com/livekit-examples/agent-starter-python
cd agent-starter-python

# 2. 安装
pip install -r requirements.txt

# 3. 配置 .env（填入上面申请的所有 key）
cp .env.example .env

# 4. 启动 Agent
python agent.py dev

# 5. 浏览器打开前端
# https://agents-playground.livekit.io/?tab=voice
# 填入 LiveKit URL + API key，点 Connect
```

---

## 延伸阅读

- [livekit/agents 官方文档](https://docs.livekit.io/agents/)
- [python-agents-examples：50+ 场景](https://github.com/livekit-examples/python-agents-examples)（电话外呼、语音 RAG、多语言、情感识别等）
- [Cartesia 音色克隆指南](https://docs.cartesia.ai/getting-started/voice-cloning)
- [阿里云实时语音识别 SDK](https://help.aliyun.com/zh/isi/developer-reference/real-time-speech-recognition)

---

## 全开源自部署方案：零 API 费用的流程和成本

如果不想依赖任何付费云服务，四个组件都有对应的开源替代：

### 组件替换表

| 组件 | 云端方案 | 开源自部署替代 |
|------|----------|----------------|
| WebRTC 服务器 | LiveKit Cloud | LiveKit Server（开源，Docker 部署） |
| STT | 阿里云实时识别 | FunASR（达摩院，中文最强） / faster-whisper |
| LLM | OpenAI GPT | Ollama + Qwen2.5-7B / vLLM + 任意开源模型 |
| TTS | Cartesia Sonic-3 | Kokoro-TTS（82M 参数，CPU 可跑） / Fish Speech（支持音色克隆） |
| 轮次检测 | LiveKit TurnDetector | Silero VAD（已集成在 LiveKit 插件里） |

LiveKit Server 本身就是开源项目（这就是 LiveKit Cloud 的底层），完整自部署只需要部署 LiveKit Server 和三个推理服务，Agent Worker 代码逻辑完全不变。

---

### 硬件要求

自部署的瓶颈在 LLM 推理，其余服务对算力要求不高：

| 服务 | 最低配置 | 推荐配置 |
|------|----------|----------|
| LiveKit Server | 2 核 / 4 GB RAM | 4 核 / 8 GB RAM（支持百路以上并发） |
| STT（faster-whisper base/small） | 4 核 CPU | GPU 可加速 3-5× |
| STT（FunASR Paraformer-zh） | 8 GB RAM | A10 / 3090 GPU |
| TTS（Kokoro-TTS） | 2 核 CPU，无 GPU | CPU 延迟约 200ms，可接受 |
| TTS（Fish Speech） | 4 GB VRAM | 8 GB VRAM（推理更快） |
| LLM（Qwen2.5-7B int4） | 8 GB VRAM | 12 GB VRAM（batch 更大） |
| LLM（Qwen2.5-14B int4） | 12 GB VRAM | 24 GB VRAM（RTX 3090/4090） |

**最实用的本地一体机选择**：Mac mini M4 Pro（24 GB 统一内存）可以跑 Qwen2.5-14B + faster-whisper + Kokoro-TTS，一台机器搞定，购入成本约 1 万元人民币，跑通后无任何后续费用。

---

### 成本估算（月度）

**场景 A：开发测试，偶尔使用**

| 项目 | 方式 | 月费 |
|------|------|------|
| LiveKit Server | 最小 VPS（1C2G） | ¥30 |
| STT + TTS + LLM | 本地 Mac / 现有设备 | 0 |
| **合计** | | **≈ ¥30/月** |

**场景 B：轻量生产，小规模并发（10 路以内）**

| 项目 | 方式 | 月费 |
|------|------|------|
| LiveKit Server | 4C8G VPS | ¥80-150 |
| GPU 推理（STT + LLM + TTS） | 云 GPU 按需 A10（~4h/天） | ¥500-800 |
| 带宽 | 含在 VPS 里 | 0 |
| **合计** | | **≈ ¥600-950/月** |

**场景 C：一次性购买 GPU 服务器，长期运营**

| 项目 | 方式 | 成本 |
|------|------|------|
| 服务器（RTX 4090 × 1） | 二手主机 | ¥15,000 一次性 |
| 带宽（100Mbps 独享） | IDC 托管 | ¥500-800/月 |
| 电费（约 350W 满负载） | | ¥300-500/月 |
| **合计** | | 约 16 个月回本，之后 ≈ ¥800-1300/月 |

和云端方案对比：阿里云 STT 超免费额度后约 ¥3.5/小时；Cartesia 超免费额度后 $0.065/千字符；加上 LLM API，高频使用场景下云端月费很快超过自部署的电费+带宽。

---

### 自部署的代码改动

LiveKit Agent 代码只需把插件换成指向本地端口，逻辑层完全不变：

**第一步：启动本地服务**

```bash
# LiveKit Server
docker run -d \
  -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server --dev

# LLM：Ollama
brew install ollama
ollama pull qwen2.5:7b
ollama serve  # 监听 localhost:11434

# TTS：Kokoro-FastAPI（OpenAI 兼容端口）
pip install kokoro-fastapi
python -m kokoro_fastapi  # 监听 localhost:8880

# STT：faster-whisper 的 OpenAI 兼容服务
pip install faster-whisper-server
uvicorn faster_whisper_server.main:app --port 8000
# 或用 whisper.cpp 的 server 模式
```

**第二步：Agent 代码只改 base_url**

```python
from livekit.plugins import openai as lk_openai
from livekit.plugins import silero

session = AgentSession(
    # STT → 本地 faster-whisper，OpenAI 兼容接口
    stt=lk_openai.STT(
        base_url="http://localhost:8000/v1",
        api_key="not-needed",
        model="Systran/faster-whisper-large-v3",
        language="zh",
    ),

    # LLM → 本地 Ollama（qwen2.5:7b 或更大）
    llm=lk_openai.LLM(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model="qwen2.5:7b",
    ),

    # TTS → 本地 Kokoro，OpenAI 兼容接口
    tts=lk_openai.TTS(
        base_url="http://localhost:8880/v1",
        api_key="not-needed",
        model="kokoro",
        voice="af_heart",   # Kokoro 内置音色
    ),

    # 轮次检测 → 换成 Silero VAD（纯本地）
    vad=silero.VAD.load(),

    preemptive_generation=True,
)
```

LiveKit Server 本地启动后，`.env` 里的 `LIVEKIT_URL` 改成 `ws://localhost:7880`，其余不变。

---

### 延迟对比

引入本地推理后，延迟构成变了：

| 环节 | 云端方案 | 本地方案（RTX 4090） |
|------|----------|---------------------|
| STT 首字延迟 | 100-200ms（网络 RTT） | 50-100ms |
| LLM 首 token | 300-600ms（云端 API） | 100-300ms（本地 int4） |
| TTS 首帧音频 | 80-150ms（Cartesia） | 50-200ms（Kokoro CPU） |
| WebRTC 传输 | 20-50ms（LiveKit Cloud） | 10-30ms（本地局域网） |

本地推理的 STT 和 LLM 延迟通常**低于云端**（省了网络 RTT），TTS 延迟取决于是否有 GPU。整体感知延迟：局域网内全本地方案可以做到 500ms 以内首次响应。

---

### 什么情况选哪种方案

| 场景 | 建议 |
|------|------|
| 快速验证 / demo | 云端免费额度，0 成本启动 |
| 个人工具，偶尔自用 | 本地 Mac + 免费 LiveKit 套餐（只有 LiveKit Server 一个成本） |
| 产品化，高频使用 | 自部署 GPU 服务器，16 个月内成本低于云端累计费用 |
| 数据不能出境 / 合规要求 | 必须全链路自部署，云端 API 不可用 |
| 需要自定义音色克隆 | Fish Speech（开源克隆）替代 Cartesia |

---

## 延伸阅读

- [livekit/agents 官方文档](https://docs.livekit.io/agents/)
- [python-agents-examples：50+ 场景](https://github.com/livekit-examples/python-agents-examples)（电话外呼、语音 RAG、多语言、情感识别等）
- [Cartesia 音色克隆指南](https://docs.cartesia.ai/getting-started/voice-cloning)
- [阿里云实时语音识别 SDK](https://help.aliyun.com/zh/isi/developer-reference/real-time-speech-recognition)
- [FunASR 流式识别部署文档](https://github.com/modelscope/FunASR)
- [Kokoro-TTS 本地部署](https://github.com/remsky/Kokoro-FastAPI)
- [Fish Speech 音色克隆](https://github.com/fishaudio/fish-speech)

---

© 2026 Author: Mycelium Protocol

<!--EN-->

## Build a Full-Duplex AI Voice Call App: LiveKit Agents + Aliyun STT + Cartesia TTS

> Core repo: [livekit/agents](https://github.com/livekit/agents) · ⭐ 11,369 · Apache-2.0  
> Starter: [livekit-examples/agent-starter-python](https://github.com/livekit-examples/agent-starter-python)  
> Examples: [livekit-examples/python-agents-examples](https://github.com/livekit-examples/python-agents-examples) · 50+ scenarios

---

### Full-Duplex vs Half-Duplex

Most voice assistants are **half-duplex**: user speaks → silence detected → AI processes → AI responds. The mic is off while AI speaks; there's no interruption.

**Full-duplex**: mic stays open throughout. User can interrupt the AI mid-sentence; the AI stops speaking and re-responds in real time. LiveKit Agents supports this natively via two mechanisms:

1. **`preemptive_generation=True`**: LLM inference starts from partial STT results, before the user finishes speaking — reduces perceived latency.
2. **`TurnDetector`**: semantic understanding + acoustic cues (intonation, pitch) to detect end of user turn, more accurate than silence-only detection.

---

### Architecture

```
User mic
  │
  ▼
LiveKit Cloud room (WebRTC)
  │ audio track
  ▼
AgentSession
  ├─ STT (Aliyun streaming) → interim + final text
  ├─ TurnDetector (EOU model)
  ├─ LLM (any streaming-capable model)
  └─ TTS (Cartesia Sonic-3) → streaming audio
       │
       ▼
  LiveKit Cloud room
       │
       ▼
  User speaker
```

Camera or screen share travels the same WebRTC channel. The Agent subscribes to the video track and injects the latest frame into each user turn's message.

---

### Core Code

```python
# agent.py
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.voice import TurnHandlingOptions
from livekit.plugins import aliyun, cartesia, openai, turn_detector
from livekit.plugins import noise_cancellation as nc

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a friendly voice assistant. Be concise — this is a spoken conversation.",
        )

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=aliyun.STT(language="zh-CN"),         # or deepgram, azure, etc.
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            model="sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=turn_detector.EOUModel(),
        ),
        preemptive_generation=True,                # start LLM from partial STT
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options={"audio_input": {"noise_cancellation": nc.BVC()}},
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### Vision (Camera + Screen Share)

```python
class VisionAssistant(Agent):
    def __init__(self):
        super().__init__(instructions="Describe and analyze what you see.")
        self._latest_frame = None

    async def on_enter(self):
        room = get_job_context().room

        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                self._create_video_stream(track)

    def _create_video_stream(self, track):
        self._video_stream = rtc.VideoStream(track)
        async def read_stream():
            async for event in self._video_stream:
                self._latest_frame = event.frame
        asyncio.create_task(read_stream())

    async def on_user_turn_completed(self, turn_ctx, new_message):
        if self._latest_frame is not None:
            new_message.content.append(ImageContent(image=self._latest_frame))
            self._latest_frame = None
```

---

### Free Tier Summary

| Service | Free tier |
|---|---|
| LiveKit Cloud | 100,000 min/month |
| Aliyun STT | 10 hrs/month (new user) |
| Cartesia TTS | 100,000 chars/month |

Enough for demos and early testing without paying upfront.

---

---

### Going Fully Open-Source: Self-Hosted Stack, Cost, and Workflow

Every component has an open-source self-hosted replacement — no API keys required after initial setup.

**Component swap table**

| Component | Cloud option | Open-source self-hosted |
|---|---|---|
| WebRTC server | LiveKit Cloud | LiveKit Server (open-source, Docker) |
| STT | Aliyun | FunASR (best Chinese) / faster-whisper |
| LLM | OpenAI GPT | Ollama + Qwen2.5-7B / vLLM |
| TTS | Cartesia Sonic-3 | Kokoro-TTS (82M params, runs on CPU) / Fish Speech (voice cloning) |
| Turn detection | LiveKit TurnDetector | Silero VAD (already in LiveKit plugins) |

LiveKit Server is the open-source project that LiveKit Cloud is built on — the Agent code stays exactly the same; only the `base_url` and credentials change.

**Hardware minimums**

The LLM is the bottleneck; STT and TTS can run on CPU:

| Service | Minimum | Recommended |
|---|---|---|
| LiveKit Server | 2 core / 4 GB | 4 core / 8 GB |
| faster-whisper (small) | 4-core CPU | GPU (3-5× faster) |
| FunASR Paraformer-zh | 8 GB RAM | A10 / RTX 3090 |
| Kokoro-TTS | 2-core CPU | CPU ~200ms latency, acceptable |
| LLM Qwen2.5-7B int4 | 8 GB VRAM | 12 GB VRAM |
| LLM Qwen2.5-14B int4 | 12 GB VRAM | 24 GB VRAM (RTX 3090/4090) |

A Mac mini M4 Pro (24 GB unified memory) runs Qwen2.5-14B + faster-whisper + Kokoro-TTS on a single machine — no ongoing API costs.

**Monthly cost breakdown**

| Scenario | Setup | Monthly cost |
|---|---|---|
| Dev / testing | Cheapest VPS for LiveKit Server + local Mac for inference | ~$5/month |
| Light production (≤10 concurrent) | 4C8G VPS + cloud GPU on-demand (A10, ~4hr/day) | $80–130/month |
| Dedicated GPU server (RTX 4090) | ~$2,000 one-time + ~$150/month (hosting + power) | Breaks even vs cloud API in ~16 months |

**Code changes — only the base_url moves**

```bash
# LiveKit Server (local)
docker run -d -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server --dev

# LLM
ollama pull qwen2.5:7b && ollama serve     # localhost:11434

# TTS (OpenAI-compatible)
python -m kokoro_fastapi                    # localhost:8880

# STT (OpenAI-compatible)
uvicorn faster_whisper_server.main:app --port 8000
```

```python
session = AgentSession(
    stt=lk_openai.STT(
        base_url="http://localhost:8000/v1",
        api_key="not-needed",
        model="Systran/faster-whisper-large-v3",
        language="zh",
    ),
    llm=lk_openai.LLM(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model="qwen2.5:7b",
    ),
    tts=lk_openai.TTS(
        base_url="http://localhost:8880/v1",
        api_key="not-needed",
        model="kokoro",
        voice="af_heart",
    ),
    vad=silero.VAD.load(),          # local VAD replaces cloud TurnDetector
    preemptive_generation=True,
)
```

**Latency comparison**

| Stage | Cloud | Local (RTX 4090) |
|---|---|---|
| STT first token | 100–200ms (network RTT) | 50–100ms |
| LLM first token | 300–600ms (API round trip) | 100–300ms (int4 local) |
| TTS first audio frame | 80–150ms (Cartesia) | 50–200ms (Kokoro CPU) |
| WebRTC transport | 20–50ms (LiveKit Cloud) | 10–30ms (LAN) |

Local inference typically **beats cloud latency** on STT and LLM by eliminating network round trips. In a LAN setup, sub-500ms first response is achievable.

**When to pick which**

| Use case | Recommendation |
|---|---|
| Demo / proof of concept | Free cloud tiers, zero upfront cost |
| Personal tool, occasional use | Local Mac + free LiveKit plan |
| Product, high-frequency usage | Dedicated GPU server; cheaper than cloud API within ~16 months |
| Compliance / data cannot leave premises | Full self-hosted, no cloud API |
| Custom voice cloning | Fish Speech (open-source clone) instead of Cartesia |

---

GitHub: [livekit/agents](https://github.com/livekit/agents)  
Playground: [agents-playground.livekit.io](https://agents-playground.livekit.io)  
Self-hosted STT: [remsky/Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) · [fishaudio/fish-speech](https://github.com/fishaudio/fish-speech) · [modelscope/FunASR](https://github.com/modelscope/FunASR)

© 2026 Author: Mycelium Protocol
