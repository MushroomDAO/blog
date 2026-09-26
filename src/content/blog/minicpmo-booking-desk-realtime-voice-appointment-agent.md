---
title: "MiniCPM-o Booking Desk：全双工语音预约台，状态机控 DB 写入，Judge LLM 防幻觉确认"
titleEn: "MiniCPM-o Booking Desk: Full-Duplex Voice Appointment Agent with State Machine and Judge LLM"
description: "AlessandroBonomo28/Minicpm-o-booking-desk，Python，MiniCPM-o 4.5 驱动的实时语音预约台 Demo。三通道架构：音频（VAD+Whisper）+ 视觉（每秒刷新的操作员屏幕帧）+ 控制 token（force_speak/force_listen）。状态机全权控制 DB 写入，模型输出不直接碰数据库；Judge LLM 核查模型口播内容防幻觉确认。实测 4 分 13 秒，2 次预约，零误写。需 32GB VRAM（RTX 5090 实测 29GB）。附完整架构拆解。"
descriptionEn: "AlessandroBonomo28/Minicpm-o-booking-desk — Python, MiniCPM-o 4.5 real-time voice appointment booking demo. Three-channel design: audio (VAD+Whisper) + vision (operator screen refreshed every second) + control tokens (force_speak/force_listen). State machine owns all DB writes — model output never touches the database directly. Judge LLM verifies spoken claims against DB state to prevent hallucinated confirmations. Demo: 4m13s, 2 bookings, zero erroneous writes. Requires 32GB VRAM (RTX 5090 tested at 29GB)."
pubDate: 2026-09-26
wechatTitle: "MiniCPM-o预约台：Judge LLM防幻觉确认"
wechatDigest: "全双工语音+状态机控DB；视觉通道每秒刷新操作员屏；Judge LLM防幻觉；32GB VRAM"
heroImage: "../../assets/images/minicpmo-booking-desk-realtime-voice-appointment-agent-banner.jpg"
category: "Tech-Experiment"
tags: ["open-source", "voice-agent", "minicpm", "full-duplex", "state-machine", "llm", "demo", "python"]
lang: zh-CN
---

`AlessandroBonomo28/Minicpm-o-booking-desk`，Python，5 stars，2026 年 9 月发布。用 MiniCPM-o 4.5 搭了一个全双工语音预约台 Demo——模型持续监听和说话，不需要轮流等待停顿，同时用状态机管数据库写入，用 Judge LLM 核查模型口播内容，防止幻觉出现在客户确认环节。

**GitHub**：github.com/AlessandroBonomo28/Minicpm-o-booking-desk

---

## 三通道设计

这个项目最值得看的是它怎么把语音、视觉、控制信号分成三条独立通道来驱动模型。

**通道一：音频**

只传客户声音。VAD（语音活动检测）判断客户说完了没有，说完后 Whisper large-v3-turbo 转写，结果送进模型。麦克风不做回声消除，需要用有线耳机物理隔开扬声器和麦克风。

**通道二：视觉**

每秒渲染一帧「操作员屏幕」图像，实时注入模型的视觉输入。这个屏幕显示当前预约状态、已确认的时间槽、挂起的操作——模型通过读这个视觉帧来了解当前状态，而不是靠上下文记忆。

这个设计的意义在于：视觉帧是系统控制的，内容是确定的，不是模型自己生成的。模型只是「读」，不「写」。

**通道三：控制 token**

`force_speak`：强制模型开口，适用于客户沉默超时或需要主动确认。
`force_listen`：强制模型停止说话进入监听，适用于客户打断。

这两个 token 不走自然语言，直接控制对话流，绕开了传统全双工语音中「说到一半被打断怎么办」的问题。

---

## 状态机和 Judge LLM

这是防错架构的两个核心。

**状态机**

所有数据库写入都经过状态机，模型输出永远不直接操作 DB。

工作流是这样的：模型语音输出 → Cloud LLM 提取器解析事件（`set` / `yes` / `no` / `cancel`）→ 状态机验证是否合法 → 通过后写入 DB → 刷新操作员屏幕 → 模型看到更新后的屏幕继续对话。

「yes」和「cancel」需要客户明确说出，才触发对应事件。客户说「你帮我定」时，状态机会提议一个时间槽而不是直接写入。

**Judge LLM**

每次模型说话，Judge LLM 会核查模型的口播内容是否和 DB 里的实际状态一致——如果模型说「已经帮您预约好了周五下午两点」，Judge 会对比 DB，确认真的写进去了才放过，否则拦截。

这解决了一个真实的幻觉风险：模型可能「确认」了一个实际上没写成功的预约。Judge LLM 在这里是质检环节而不是决策环节。

---

## 处理流水线

```
客户说话
    ↓
VAD（语音活动检测）
    ↓
Whisper large-v3-turbo（转写）
    ↓
Cloud LLM 提取器（解析事件: set/yes/no/cancel）
    ↓
状态机（验证 + DB 写入）
    ↓
操作员屏幕刷新（下一帧视觉输入）
    ↓
MiniCPM-o 4.5 生成语音回复
    ↓
Judge LLM 核查口播内容
    ↓
播放给客户
```

提取器和 Judge 默认走云端 API，有 Qwen3-1.7B 本地备选。

---

## 实测数据

延迟：
- 端到端：1.5–3 秒
- `force_speak` 强制开口：0.5–1.2 秒
- 提取器 + Judge 调用：0.8–1.4 秒

Demo 录像（youtu.be/Yx80VoA8Vw4）：4 分 13 秒，完成 2 次预约含 1 次取消，客户打断测试，DB 操作面板实时可见，零误写。

---

## 硬件要求

**GPU**：32GB VRAM（作者用 RTX 5090，实测峰值约 29GB）

**其他**：Python 3.10、PyTorch + CUDA、有线耳机（必须，防麦克风拾到扬声器声音）

这个配置基本把这个 Demo 锁死在高端工作站或云 GPU 上。MiniCPM-o 4.5 本身的全模态（视觉+音频）推理是内存占用的主要来源。

Mac / 16GB 显存 GPU 跑不了。

---

## 架构值得借鉴的地方

**视觉通道传状态**：不通过文字 prompt 告诉模型当前状态，而是渲染成图像帧让模型「看」——绕开了长 context 累积的问题，状态刷新频率独立可控。

**模型不碰 DB**：模型输出 → 事件提取 → 状态机验证 → DB 写入，每一层是独立的，任何一层拒绝就截止。这是一个比「用 tool call 让模型直接写 DB」更保守的设计。

**Judge 而不是更大的模型**：不是靠模型本身更聪明来防幻觉，而是加一层外部核查。这个思路在生产环境比依赖模型自我约束更可靠。

---

## 局限性

**1. 硬件门槛**：32GB VRAM，消费者市场只有 RTX 5090 或数据中心卡够用，个人开发者难以本地验证。

**2. 英语限制**：当前仅支持英语，Whisper 和提取器都按英语设计。

**3. 云端依赖**：提取器和 Judge 默认走 API，本地备选 Qwen3-1.7B 质量是否接近未知。

**4. 无许可证**：仓库没有明确 LICENSE 文件，技术上是「版权保留」。继承上游 MiniCPM-o Apache 2.0 的说法没有在仓库里明确声明，商用前需向作者确认。

**5. Demo 规模**：5 stars，个人项目，未经生产验证，麦克风隔离完全靠外部硬件。

---

## 怎么看这个项目

这不是一个可以直接拿来用的产品，而是一个「三通道 + 状态机 + Judge」架构的工作演示。

在当前多模态语音 Agent 方向，大多数项目仍在解决「让模型说话更流畅」，这个 Demo 的重点在「怎么让模型不乱写数据库」和「怎么在不增加 context 长度的情况下持续传递状态」——这两个问题是真实生产场景里更难的部分。

视觉通道传操作员屏幕这个设计，如果在 32GB 以下的机器上能跑起来，会是个有意思的状态管理方案。

> 开源仅供学习研究参考。仓库无明确 LICENSE，商用需向作者确认授权。

---

<!--EN-->

## MiniCPM-o Booking Desk: Full-Duplex Voice Agent with State Machine and Judge LLM

`AlessandroBonomo28/Minicpm-o-booking-desk` — Python, 5 stars. A real-time voice appointment booking desk demo powered by MiniCPM-o 4.5. Three-channel design, state machine-owned DB writes, Judge LLM prevents hallucinated confirmations.

**GitHub**: github.com/AlessandroBonomo28/Minicpm-o-booking-desk

---

### Three-Channel Architecture

**Audio channel**: Customer speech only. VAD detects end-of-utterance → Whisper large-v3-turbo transcribes.

**Vision channel**: Operator "screen" rendered as frames, injected into the model's vision input every second. Shows current booking state, confirmed slots, pending operations — the model reads this rather than relying on context memory.

**Control tokens**: `force_speak` / `force_listen` steer conversation flow without natural language overhead. Handles interruptions cleanly.

---

### State Machine + Judge LLM

**State machine**: All DB writes go through it. Pipeline: model output → extractor LLM (emits `set`/`yes`/`no`/`cancel` events) → state machine validates → DB write → screen refresh. Model output never touches the DB directly. Booking requires explicit "yes"; "cancel" requires explicit confirmation.

**Judge LLM**: After each model utterance, verifies that spoken claims match DB state. If the model says "I've booked you for Friday 2pm," the Judge checks the DB before the audio plays. Prevents hallucinated confirmations from reaching the caller.

---

### Performance (Demo)

| Metric | Value |
|--------|-------|
| End-to-end latency | 1.5–3 s |
| force_speak opening | 0.5–1.2 s |
| Extractor + Judge call | 0.8–1.4 s |
| Demo session | 4m13s, 2 bookings, 0 erroneous writes |

Demo video: youtu.be/Yx80VoA8Vw4

---

### Hardware Requirements

- **32GB VRAM** (RTX 5090 tested at ~29GB peak)
- Python 3.10, PyTorch + CUDA
- Wired headset required (no software echo cancellation)

16GB VRAM cards and Mac cannot run this.

---

### What's Worth Borrowing

**Vision channel for state**: State is rendered as image frames rather than appended text — context length stays constant, state refresh rate is independently controlled.

**Model never touches DB**: Multi-layer validation (model → extractor → state machine → DB) means each layer can reject without side effects.

**External judge over smarter model**: Production-grade hallucination prevention doesn't rely on model self-restraint; it adds an independent verification layer.

---

### Limitations

1. **Hardware**: 32GB VRAM locks this to RTX 5090 or data center GPUs
2. **English only**: Whisper and extractor designed for English
3. **Cloud dependency**: Extractor/Judge default to API; local Qwen3-1.7B fallback quality unknown
4. **No explicit license**: Repo has no LICENSE file; upstream Apache 2.0 inheritance not formally stated
5. **Demo scale**: Personal project, 5 stars, not production-validated

---

### Assessment

This isn't a deployable product — it's a working demonstration of a "three-channel + state machine + judge" architecture pattern. Where most voice agent projects focus on making speech smoother, this one focuses on preventing the model from making erroneous DB writes and on maintaining state without growing context. The vision-channel state injection is an interesting pattern for any application where current state changes frequently and you don't want to pay the cost of long context accumulation.

> For learning and research reference only. No explicit license in the repo — confirm with the author before commercial use.
