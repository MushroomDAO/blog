---
title: "用 GPT-Live 构建全双工 AI 语音客服系统：从架构理解到落地实践"
titleEn: "Building a Full-Duplex AI Voice Customer Service System with GPT-Live: From Architecture to Production"
description: "解析 GPT-Live 全双工语音架构的核心创新——解耦「说话」与「思考」、WebRTC 传输、Go 异步引擎——并提供一套从技术选型到 System Prompt 设计的完整落地指南，帮你构建自己的 AI 语音客服或自动应答系统。"
descriptionEn: "A deep dive into GPT-Live's full-duplex voice architecture — decoupling speech from reasoning, WebRTC transport, Go async engine — with a complete practical guide from technology selection to System Prompt design for building your own AI voice customer service or auto-response system."
pubDate: 2026-09-01
updatedDate: 2026-09-01
category: "Tech-Experiment"
tags: ["GPT-Live", "OpenAI Realtime API", "voice AI", "duplex", "AI客服", "WebRTC", "全双工", "语音系统", "build guide"]
heroImage: "../../assets/images/gpt-live-duplex-voice-customer-service-build-guide-banner.jpg"
author: "Mycelium Protocol"
---

## 先解决一个认知问题：为什么传统语音 AI 总感觉"不自然"

用过 Siri、早期 ChatGPT Voice、客服机器人的人都有同感：和 AI 语音对话，总有一种奇怪的"排队感"。你说完，AI 停顿一下判断你是否讲完，然后再回答。

你不能打断它，你的停顿它会误以为是结束，它的停顿你不知道是在思考还是在等待。

这不是语言模型水平的问题，是**架构设计**的问题。

传统语音 AI 的流程：

```
用户说话 → VAD（端点检测）→ STT（转文字）→ LLM（生成回答）→ TTS（转语音）→ 播放
```

这条链路里，**VAD（Voice Activity Detection）** 扮演了"轮次检测器"的角色——它需要判断你是否说完了，才能触发后续的 STT→LLM→TTS 流水线。VAD 判断早了，AI 会抢话；VAD 判断晚了，就会出现你熟悉的尴尬停顿。

GPT-Live 做的最根本的事情是：**把这个轮次检测器去掉了。**

---

## GPT-Live 架构的三个核心创新

### 1. 全双工语音模型（取消轮次检测器）

GPT-Live 采用端对端（end-to-end）的语音语言模型，直接处理音频输入和输出，而不是串联 STT + LLM + TTS 三个独立模型。

这意味着：

- 模型可以**一边说话、一边听**，真正意义上的同时双向
- 你可以随时打断它，它也可以在你停顿时不急着接话（更像真人）
- 省掉了 STT、TTS 两次转换的延迟

传统流水线延迟通常在 1.5-3 秒；GPT-Live 的目标延迟在 300-600ms，接近真实电话通话的体感。

### 2. 解耦"说话"与"思考"

这是 GPT-Live 架构里最聪明的设计决策：**把对话管理和任务执行拆开**。

```
用户 ↔ GPT-Live（低延迟，负责保持对话流畅）
           ↓ 分发重任务
       GPT-5.5（负责搜索、复杂推理、工具调用）
```

当用户提出一个需要搜索或复杂计算的问题时，GPT-Live 不会说"请稍等"然后挂起整个对话——它会继续和用户保持互动（"嗯，我来帮你查一下"），同时把后台任务交给 GPT-5.5 处理。后台思考完成后，再把结果注入到对话里。

这就是为什么 GPT-Live 的交互感觉"连贯"——因为对话线和推理线是解耦的。

### 3. 重建底层基础设施

为了把延迟压下去，OpenAI 做了一套完整的基础设施重建：

| 问题 | 解决方案 |
|---|---|
| 音频被工具调用拖慢 | 音频走独立高速通道，不与 LLM 请求共用带宽 |
| Python asyncio 在高并发下吞吐不足 | 核心系统改写为 **Go** |
| WebSocket 建连开销大 | 采用 **WebRTC**，连接从六次往返压缩到一次 |
| 长对话切换模型时会中断 | 上下文压缩和模型切换期间语音流不中断 |

WebRTC 的选择尤其关键——它原本是为浏览器实时视频通话设计的协议，内置 NAT 穿透、自适应比特率、丢包重传，非常适合低延迟音频场景。

---

## 建一套自己的系统：技术选型

OpenAI 提供了三种传输方式，选错了代价很高：

| 场景 | 传输方式 | 适用场景 |
|---|---|---|
| 浏览器 / 手机 App | **WebRTC** | 用户直接在前端说话，需要 P2P 低延迟 |
| 服务器媒体管道 | **WebSocket** | 你的服务器已经收到原始音频（如电话系统接入） |
| 电话系统 | **SIP** | 传统电话网接入，PSTN/VoIP |

对于 AI 客服场景，最常见的是两种：

- **网页/App 端语音助手** → WebRTC
- **电话客服接入** → SIP（对接你的 PSTN 或 VoIP 提供商）

两者可以共存在同一套 GPT-Live 后端上，只是接入层不同。

---

## 四个关键组件的设计

### 组件一：会话管理层

```
POST /v1/realtime/client_secrets    # 创建临时凭证（浏览器端专用）
WS/WebRTC → /v1/realtime           # 建立 session
```

每个用户对话是一个独立的 Realtime Session。Session 需要管理：
- **状态**：用户正在说话 / AI 正在响应 / 等待中
- **上下文压缩**：长对话需要在保持连接的前提下压缩历史
- **切换**：同一用户多轮对话之间的 session 复用

关键设计原则：**session 要是无状态的容器**，业务状态（用户身份、订单信息、历史意图）存在你自己的数据库里，通过 System Prompt 注入。

### 组件二：音频管道

WebRTC 路径（浏览器端）：

```
浏览器麦克风 → getUserMedia() → WebRTC PeerConnection → OpenAI Realtime endpoint
```

WebSocket 路径（服务器端）：

```
电话系统 → 你的媒体网关 → PCM 16kHz 原始音频 → WebSocket → OpenAI Realtime
```

音频格式要求：
- 输入：PCM 16-bit，16kHz，单声道
- 输出：支持 PCM 或 G.711（电话系统友好）

### 组件三：工具调用层（Tool Use）

这是 AI 客服的核心差异点。通过给 Realtime Session 绑定工具，AI 可以在对话中实时调用：

```json
{
  "type": "function",
  "name": "查询订单状态",
  "description": "根据订单号查询当前物流状态",
  "parameters": {
    "type": "object",
    "properties": {
      "order_id": {"type": "string", "description": "订单编号"}
    },
    "required": ["order_id"]
  }
}
```

工具列表在 Session 创建时传入，支持动态更新（用于根据用户身份动态注入可用工具）。

GPT-Live 调用工具时，语音对话不会中断——它会继续和用户说话（"稍等，我帮你查一下"），工具结果回来后自动整合进回答里。

### 组件四：Webhook 和服务器侧控制

通过 Webhooks，你可以从服务器侧主动控制 Realtime Session：

- 注入消息（主动播报）
- 截断 AI 正在说的话（处理特殊情况）
- 切换模型或上下文
- 监控 token 消耗

这对客服场景特别重要：当后台系统检测到紧急情况（比如支付失败），可以主动打断当前对话注入新信息。

---

## System Prompt 设计：AI 客服的灵魂

语音客服的 System Prompt 和文字客服有根本性的不同。

### 语音专用规则

```
你是 [品牌名] 的智能客服助手，通过语音与用户实时对话。

【语音对话规范】
- 句子要短。每句不超过 20 字，不要用长段落。
- 不要说 "根据您提供的信息"、"请问您是指" 这类冗长的客套话。
- 如果用户打断你，立即停止，听完再回答。
- 停顿要自然，不要填充 "嗯"、"呃"。
- 数字要说成口语形式："三千二百块"，不要说"3200元"。

【当你不确定用户意图时】
提一个最具体的问题，不要同时问多个。

【当工具调用需要时间时】
先告知用户："好的，我帮您查一下"，然后调用工具。
工具结果回来后，直接说结果，不要重述问题。
```

### 用户上下文注入

每次 session 创建时，在 System Prompt 的结尾动态注入用户信息：

```
【当前用户信息】
姓名：张三
会员等级：金卡
最近订单：2026-08-28，订单号 #88776655，状态：派送中
历史问题类型：退换货（2次），物流查询（5次）

根据上述信息，优先主动提供与其历史问题相关的帮助。
```

### 打断处理

全双工最大的挑战是打断。当用户打断时，GPT-Live 会自动停止当前输出，但你的 System Prompt 需要告诉模型**如何处理打断**：

```
如果用户在你说话途中打断，直接回应打断内容，不要继续原来的话题，也不要说"您刚才打断了我"。
```

---

## 成本和限制

**定价参考**（OpenAI Realtime API，截至 2026 年）：

| 项目 | 费率 |
|---|---|
| 音频输入 | $0.06 / 分钟（约）|
| 音频输出 | $0.24 / 分钟（约）|
| Tool use token | 按文字 token 计费 |

一次标准客服对话（5分钟）：约 $0.6-1.5，取决于对话密度和工具调用频次。

**当前限制：**
- 单 session 最长持续时间：30 分钟（超时需重连）
- 并发 session 数：取决于 API tier
- 语言支持：中文支持良好，但方言和强口音识别率低于普通话

**不适合的场景：**
- 需要精确转录存档的合规场景（建议用 gpt-live-transcribe 单独留存记录）
- 超低延迟要求（< 200ms）的实时翻译
- 纯文字工单系统（没必要用 Realtime API）

---

## 最小可用版本：5 步快速启动

如果你只是想先跑通一个 demo：

```bash
# 1. 获取 API key
export OPENAI_API_KEY="sk-..."

# 2. 创建 session（服务器端）
curl -X POST https://api.openai.com/v1/realtime/client_secrets \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-realtime-2.1", "session": {"type": "voice_agent"}}'

# 3. 前端用返回的 client_secret 建立 WebRTC 连接
# 4. getUserMedia() 获取麦克风
# 5. 把音频流传给 Realtime 连接，监听 response events

# OpenAI 官方提供了完整的 starter：
# https://github.com/openai/openai-realtime-console
```

官方 Agents SDK 已内置 WebRTC 音频处理，推荐从那里开始，而不是手写底层。

---

## 这套架构的意义

GPT-Live 的全双工架构不只是"更快的语音助手"——它在改变**人机交互的默认界面**。

过去，AI 是一个你打字问它回答的工具。GPT-Live 试图让 AI 变成一个**持续在线、随时可打断、能边说话边调用工具干活**的智能代理。

对客服场景来说，这意味着可以把"等待音乐 + 人工客服"替换成一个真正能解决问题的实时语音代理。对个人来说，这是 Siri 和 Google Assistant 失败之处——GPT-Live 在一个更好的技术底座上重新来过。

语音，可能是 AI 最后一公里的真正入口。

---

*资料来源：OpenAI Realtime API 文档（platform.openai.com/docs/guides/realtime）、小红书 @雨的AI笔记《ChatGPT Voice 背后的新架构公开》、GPT-Live 文档（2026-08-14），综合分析整理。*

<!--EN-->

## First, a Perception Problem: Why Does Traditional Voice AI Feel Unnatural?

Anyone who has used Siri, early ChatGPT Voice, or a call center bot knows the feeling: talking to an AI voice assistant has a strange "queuing" quality. You speak, the AI pauses to judge whether you're done, the model thinks, and then it responds.

You can't interrupt it. Your pause makes it think you're finished. Its pause leaves you wondering whether it's thinking or waiting.

This isn't a language model capability problem. It's an **architectural** problem.

The traditional voice AI pipeline:

```
User speaks → VAD (endpoint detection) → STT (speech to text) → LLM → TTS (text to speech) → playback
```

In this chain, **VAD (Voice Activity Detection)** acts as the turn detector — it must determine when you're done speaking before the STT → LLM → TTS pipeline triggers. Early VAD interrupts the AI; late VAD creates the awkward silence you know well.

GPT-Live's most fundamental innovation: **remove the turn detector entirely.**

---

## Three Core Architectural Innovations in GPT-Live

### 1. Full-Duplex Speech Model (No Turn Detection)

GPT-Live uses an end-to-end speech language model that handles audio input and output directly, rather than chaining STT + LLM + TTS as three separate models.

This means:
- The model can **speak and listen simultaneously**, true full-duplex
- You can interrupt at any time; it doesn't rush to fill your pause
- STT and TTS conversion latency is eliminated

Traditional pipeline latency: typically 1.5–3 seconds. GPT-Live target: 300–600ms — approaching the feel of a real phone call.

### 2. Decoupling "Speaking" from "Thinking"

The smartest architectural decision in GPT-Live: **separate conversation management from task execution.**

```
User ↔ GPT-Live (low-latency, keeps conversation flowing)
         ↓ offloads heavy tasks
     GPT-5.5 (search, complex reasoning, tool calls)
```

When a user asks something requiring search or complex calculation, GPT-Live doesn't say "please hold" and freeze — it continues engaging the user ("Let me check that for you") while dispatching the task to GPT-5.5 in the background. When the result comes back, it's woven into the response.

This is why GPT-Live conversations feel *coherent* — the dialogue thread and reasoning thread are decoupled.

### 3. Infrastructure Rebuild

To hit latency targets, OpenAI rebuilt the whole underlying stack:

| Problem | Solution |
|---|---|
| Audio blocked by tool calls | Audio on a dedicated fast path, separate from LLM requests |
| Python asyncio limits throughput | Core system rewritten in **Go** |
| WebSocket handshake overhead | **WebRTC** — connection from 6 round trips to 1 |
| Model switches interrupt audio | Context compression and model switching don't pause the voice stream |

The WebRTC choice is particularly significant — designed for browser real-time video calling, it includes NAT traversal, adaptive bitrate, and packet loss recovery, all ideal for low-latency audio.

---

## Building Your Own System: Technology Selection

OpenAI offers three transport options; choosing the wrong one is expensive:

| Scenario | Transport | Use case |
|---|---|---|
| Browser / mobile app | **WebRTC** | User speaks directly in the front end |
| Server media pipeline | **WebSocket** | Your server already receives raw audio (e.g., phone system integration) |
| Telephone system | **SIP** | Traditional phone network (PSTN/VoIP) |

For AI customer service, the two most common paths:
- **Web/app voice assistant** → WebRTC
- **Phone support integration** → SIP (connect to your PSTN or VoIP provider)

Both can share the same GPT-Live backend; only the entry layer differs.

---

## Four Key Component Designs

### Component 1: Session Management

```
POST /v1/realtime/client_secrets    # Create ephemeral credentials (browser-side)
WS/WebRTC → /v1/realtime           # Open session
```

Each user conversation is an independent Realtime Session. Sessions manage:
- **State**: user speaking / AI responding / idle
- **Context compression**: long conversations need compression while keeping the connection alive
- **Handoff**: session reuse across a single user's multi-turn conversation

Key design principle: **sessions should be stateless containers**. Business state (user identity, order data, intent history) lives in your own database, injected via System Prompt.

### Component 2: Audio Pipeline

WebRTC path (browser):
```
Browser microphone → getUserMedia() → WebRTC PeerConnection → OpenAI Realtime endpoint
```

WebSocket path (server):
```
Phone system → your media gateway → PCM 16kHz raw audio → WebSocket → OpenAI Realtime
```

Audio format requirements: PCM 16-bit, 16kHz, mono input; PCM or G.711 output (phone-system compatible).

### Component 3: Tool Call Layer

This is the core differentiator for AI customer service. By binding tools to the Realtime Session, the AI can call real-time functions during conversation:

```json
{
  "type": "function",
  "name": "check_order_status",
  "description": "Check current shipping status by order ID",
  "parameters": {
    "type": "object",
    "properties": {
      "order_id": {"type": "string", "description": "Order number"}
    },
    "required": ["order_id"]
  }
}
```

GPT-Live does not pause the voice conversation when calling a tool — it continues talking ("Let me pull that up for you"), then weaves the tool result into the response when it returns.

### Component 4: Webhooks and Server-Side Control

From your server, you can actively control a Realtime Session:
- Inject messages (proactive announcements)
- Truncate what the AI is saying (for emergency interruption)
- Switch models or update context
- Monitor token consumption

Critical for customer service: if your backend detects an event (payment failure, account flag), it can break into the live conversation and inject new information without requiring the user to ask.

---

## System Prompt Design: The Soul of AI Customer Service

Voice customer service System Prompts are fundamentally different from text-based ones.

### Voice-Specific Rules

```
You are the voice customer service assistant for [Brand]. You are having a live spoken conversation with the user.

[Voice conversation rules]
- Keep sentences short. No more than 15 words per sentence. No long paragraphs.
- Avoid filler phrases like "Based on the information you've provided" or "Could you clarify."
- If the user interrupts you, stop immediately, listen, then respond.
- Pauses should feel natural. Do not fill silence with "um" or "uh."
- Say numbers as words: "three thousand two hundred dollars," not "$3,200."

[When uncertain about user intent]
Ask one specific question. Never ask multiple questions at once.

[When a tool call takes time]
Acknowledge first: "Let me check that for you." Call the tool.
When the result arrives, deliver it directly — don't recap the question.
```

### User Context Injection

Dynamically append user context to the System Prompt at session creation:

```
[Current user]
Name: John Smith
Membership: Gold
Most recent order: 2026-08-28, #88776655, status: In transit
Past inquiry types: returns (2x), shipping inquiry (5x)

Proactively offer help relevant to their history.
```

### Interruption Handling

Full-duplex's biggest challenge is interruptions. GPT-Live auto-stops current output when interrupted, but your System Prompt must tell the model how to *handle* it:

```
If the user interrupts while you're speaking, immediately respond to what they said. Do not continue your previous sentence. Do not say "as I was saying" or "you interrupted me."
```

---

## Costs and Limits

**Pricing reference** (OpenAI Realtime API, as of 2026):

| Item | Rate |
|---|---|
| Audio input | ~$0.06 / minute |
| Audio output | ~$0.24 / minute |
| Tool use tokens | Billed as text tokens |

A standard 5-minute customer service call: approximately $0.60–$1.50 depending on conversation density and tool call frequency.

**Current limitations:**
- Max session duration: 30 minutes (reconnect required)
- Concurrent sessions: depends on your API tier
- Language: Mandarin works well; strong accents and dialects have lower accuracy

**Poor fits:**
- Compliance-regulated precise transcription archiving (use gpt-live-transcribe separately)
- Sub-200ms ultra-low-latency real-time translation
- Pure text ticket systems (no need for Realtime API)

---

## Minimum Viable Version: 5 Steps to Get Running

To demo this quickly:

```bash
# 1. Set your API key
export OPENAI_API_KEY="sk-..."

# 2. Create session (server-side)
curl -X POST https://api.openai.com/v1/realtime/client_secrets \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-realtime-2.1", "session": {"type": "voice_agent"}}'

# 3. Use the returned client_secret to open WebRTC from the browser
# 4. getUserMedia() to capture microphone
# 5. Pipe audio to the Realtime connection and listen for response events

# Official starter:
# https://github.com/openai/openai-realtime-console
```

The official Agents SDK has built-in WebRTC audio handling — start there rather than writing the low-level transport from scratch.

---

## Why This Architecture Matters

GPT-Live's full-duplex design isn't just "faster voice assistant" — it's changing the **default interface for human-AI interaction**.

Previously, AI was a tool you typed questions into. GPT-Live is building something that stays online, can be interrupted at any time, and can call tools while talking. For customer service, this means replacing "hold music + human agent" with a real-time voice agent that actually resolves issues. For individuals, this is exactly where Siri and Google Assistant failed — GPT-Live is trying again on a better technical foundation.

Voice may be the true last mile for AI.

---

*Sources: OpenAI Realtime API documentation (platform.openai.com/docs/guides/realtime), XiaoHongShu @雨的AI笔记 "ChatGPT Voice 背后的新架构公开", XiaoHongShu @老农API "GPT-Live 双工, 接入Codex / ChatGPT Work", GPT-Live document PDF by 林默 Moon (2026-08-14). Analysis and synthesis by Mycelium Protocol.*
