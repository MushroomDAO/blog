---
title: "OpenAI 实时语音一小时花 $18，这两个开源模型让你不花一分钱"
titleEn: "OpenAI Realtime Voice Costs $18/Hour — Two Open-Source Models Let You Run It Free"
description: "OpenAI 发布三款实时语音模型，定价可达每小时 $18——比很多私教还贵。Kyutai 的 Moshi 和 gpt-omni 的 Mini-Omni 是两个完全开源的端到端实时语音替代方案，本地运行，支持 Apple Silicon MLX，延迟低至 160ms。"
descriptionEn: "OpenAI's three realtime voice models can cost up to $18/hour — more expensive than many tutors. Moshi by Kyutai and Mini-Omni by gpt-omni are two fully open-source end-to-end realtime voice alternatives that run locally on Apple Silicon via MLX with as low as 160ms latency."
pubDate: "2026-05-10"
updatedDate: "2026-05-10"
category: "Tech-News"
tags: ["实时语音", "开源", "Moshi", "Mini-Omni", "Apple Silicon", "MLX", "OpenAI", "语音AI", "本地推理"]
heroImage: "../../assets/banner-ai-personal-assistant.jpg"
---

**结论先行（BLUF）**：OpenAI 的三款实时语音模型（`gpt-4o-realtime-preview`、`gpt-4o-mini-realtime-preview`、`gpt-realtime`）定价可达 **$0.30/分钟，即 $18/小时**——一场一小时的语音对话成本与国内私教相当。而 Kyutai 的 **Moshi** 和清华团队的 **Mini-Omni** 是两个完全开源的端到端实时语音替代方案，免费、本地运行，支持 Apple Silicon MLX 量化部署，理论延迟 160ms。本文整理所有关键链接，开箱即用。

---

## OpenAI 实时语音到底多贵？

OpenAI 目前有三款面向开发者的实时语音 API：

| 模型 | 定位 | 音频输入 | 音频输出 |
|------|------|---------|---------|
| `gpt-4o-realtime-preview` | 旗舰，首发版 | $0.06/分钟 | $0.24/分钟 |
| `gpt-4o-mini-realtime-preview` | 轻量平价版 | 更低 | 更低 |
| `gpt-realtime` | 最新生产级别，比旗舰版便宜约 20% | ~$0.05/分钟 | ~$0.19/分钟 |

**一次典型的一小时语音通话（双向实时）**：

- 用户说话 60 分钟：$0.06 × 60 = **$3.60**
- AI 回应 60 分钟：$0.24 × 60 = **$14.40**
- **合计：$18/小时**

国内一线城市一对一私教平均 ¥150/小时（约 $21），OpenAI 的 API 成本已经追上人力价格——而且这还只是模型调用费，不含服务器、应用开发和运营成本。

有开发者在社区调侃：「用 OpenAI 语音 API 做英语陪练，成本比雇一个菲律宾外教还贵。」

---

## 两个开源替代品，性能不弱

### Moshi — 全球首个全双工端到端实时语音模型

由法国 AI 研究机构 Kyutai 发布，是目前**性能最强**的开源实时语音模型。

**核心技术亮点**：

- **全双工（Full-Duplex）**：没有明确的对话回合，可以处理重叠对话、打断和插话——就像真实人类通话
- **理论延迟 160ms**，在 L4 GPU 上实际延迟约 200ms
- **Inner Monologue（内心独白）**：生成语音的同时也生成对应文本，用于辅助推理而非中间转换
- **非语言信息捕获**：可以识别语气、情绪、停顿等非语言信息
- **Mimi 音频编解码器**：自研流式神经音频 Codec，低延迟高质量

**语音问答基准测试**（Llama Questions）：

| 模型 | 得分 |
|------|------|
| **Moshi** | **62.3** |
| SpeechGPT | 21.6 |

**所有链接**：

| 资源 | 链接 |
|------|------|
| GitHub | [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) |
| HuggingFace（PyTorch，男声 Moshiko） | [kyutai/moshiko-pytorch-bf16](https://huggingface.co/kyutai/moshiko-pytorch-bf16) |
| HuggingFace（PyTorch，女声 Moshika） | [kyutai/moshika-pytorch-bf16](https://huggingface.co/kyutai/moshika-pytorch-bf16) |
| **Apple Silicon MLX（男声，BF16）** | [kyutai/moshiko-mlx-bf16](https://huggingface.co/kyutai/moshiko-mlx-bf16) |
| **Apple Silicon MLX（女声，BF16）** | [kyutai/moshika-mlx-bf16](https://huggingface.co/kyutai/moshika-mlx-bf16) |
| **Apple Silicon MLX（Q4 量化，省内存）** | [kyutai/moshiko-mlx-q4](https://huggingface.co/kyutai/moshiko-mlx-q4) |
| HuggingFace 模型文档 | [transformers/moshi](https://huggingface.co/docs/transformers/model_doc/moshi) |
| 论文 | [arXiv:2410.00037](https://huggingface.co/papers/2410.00037) |

Mac 用户推荐直接下载 MLX 量化版（moshiko-mlx-q4），内存占用大幅降低，M1/M2 也能跑。

---

### Mini-Omni — 0.5B 小模型，小而美

由 gpt-omni 团队发布的极轻量端到端语音对话模型，**参数量仅 0.5B**，是目前已知最小的可运行实时语音模型之一。

**核心技术亮点**：

- **无独立 ASR/TTS 模块**：端到端生成，不依赖 Whisper + TTS 的串联管线
- **并行文本+音频 Token 生成**：同时生成文字和语音 token，避免串行等待
- **Batch Parallel Decoding**：让语音生成过程能借鉴文本推理能力
- 使用 Qwen2 作为语言骨干 + SNAC 音频解码
- Mini-Omni2 进化版支持**视觉+音频+文本**三模态

**所有链接**：

| 资源 | 链接 |
|------|------|
| GitHub（Mini-Omni） | [gpt-omni/mini-omni](https://github.com/gpt-omni/mini-omni) |
| HuggingFace（Mini-Omni） | [gpt-omni/mini-omni](https://huggingface.co/gpt-omni/mini-omni) |
| GitHub（Mini-Omni2，含视觉） | [gpt-omni/mini-omni2](https://github.com/gpt-omni/mini-omni2) |
| HuggingFace（Mini-Omni2） | [gpt-omni/mini-omni2](https://huggingface.co/gpt-omni/mini-omni2) |
| 论文 | [arXiv:2408.16725](https://huggingface.co/papers/2408.16725) |

Mini-Omni 的语音推理能力不如文本模式，但对轻量场景（边缘设备、低算力 Mac、树莓派级别应用）极具价值。

---

## 如何在 Apple Silicon Mac 上运行 Moshi？

Kyutai 已经为 MLX 框架提供了专用支持：

```bash
# 安装 moshi-mlx
pip install moshi-mlx

# 运行（自动从 HuggingFace 下载 MLX 量化模型）
python -m moshi_mlx.local_web -q 4   # Q4 量化版，内存最省
python -m moshi_mlx.local_web -q 8   # Q8 版，质量更好
```

浏览器打开 `http://localhost:8998` 即可开始实时语音对话。

---

## 真的可以替代 OpenAI 吗？

| 维度 | OpenAI gpt-realtime | Moshi（开源） | Mini-Omni（开源） |
|------|---------------------|--------------|-----------------|
| 延迟 | 未公开，商业级 | 160ms（理论）| 未公开 |
| 语言质量 | ★★★★★ | ★★★★ | ★★★ |
| 本地部署 | ✗ | ✓ | ✓ |
| 隐私 | 数据上云 | 本地 | 本地 |
| 成本 | $18/小时 | **¥0** | **¥0** |
| Apple Silicon | ✗ | ✓（MLX） | ✓ |
| 全双工 | ✓ | ✓ | 部分支持 |

对于**个人开发者、研究者、注重隐私的场景**：Moshi 是目前最具竞争力的开源实时语音方案。Mini-Omni 的价值在于极低的资源门槛——0.5B 参数意味着几乎任何设备都能跑。

OpenAI 的商业 API 在质量和生态成熟度上仍有优势，但 $18/小时的成本意味着大多数个人和小团队无法负担长时间的语音交互应用。开源方案正在以每个季度一次的速度快速逼近商业水准。

---

## 为什么这很重要？

语音是人类交互最自然的方式。当实时语音对话的成本从「每小时 $18」降到「本地免费」，将会打开哪些应用场景？

- 全天候语言学习陪伴，不受次数限制
- 隐私保护的语音日记、情绪助理
- 离线运行的语音家庭助手
- 轻量 IoT 设备的语音控制

Moshi 和 Mini-Omni 只是开始。端到端实时语音的开源化，正在把这个原本属于 OpenAI 的市场系统性地打开。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: OpenAI's three realtime voice models (`gpt-4o-realtime-preview`, `gpt-4o-mini-realtime-preview`, `gpt-realtime`) can cost up to **$0.30/minute — $18/hour** in a full-duplex conversation, comparable to hiring a private tutor. Kyutai's **Moshi** and the **Mini-Omni** from gpt-omni are two fully open-source, end-to-end realtime voice alternatives. They run locally on Apple Silicon via MLX with 160ms theoretical latency and zero API cost. This article collects all the key links.

---

## How Expensive Is OpenAI Realtime Voice?

OpenAI currently offers three developer-facing realtime voice APIs:

| Model | Purpose | Audio Input | Audio Output |
|-------|---------|-------------|-------------|
| `gpt-4o-realtime-preview` | Flagship, original release | $0.06/min | $0.24/min |
| `gpt-4o-mini-realtime-preview` | Lightweight, budget option | Lower | Lower |
| `gpt-realtime` | Latest production-grade, ~20% cheaper than flagship | ~$0.05/min | ~$0.19/min |

**One-hour real-time conversation (full-duplex)**:

- User speaks 60 minutes: $0.06 × 60 = **$3.60**
- AI responds 60 minutes: $0.24 × 60 = **$14.40**
- **Total: $18/hour**

A private tutor in a major city averages $20-30/hour. OpenAI's API cost has reached human price parity — and that's just the model call cost, not servers, development, or operations.

One developer quipped in the community: *"Using the OpenAI Voice API as a language tutor costs more than hiring a Filipino English teacher."*

---

## Two Open-Source Alternatives That Actually Compete

### Moshi — The World's First Full-Duplex End-to-End Realtime Voice Model

Released by French AI research lab Kyutai, Moshi is the **highest-performing** open-source realtime voice model available today.

**Key technical innovations**:

- **Full-Duplex**: No conversation turns — handles overlapping speech, interruptions, and interjections like a real human call
- **160ms theoretical latency**, ~200ms in practice on an L4 GPU
- **Inner Monologue**: Generates both speech and corresponding text simultaneously — text is used as auxiliary reasoning, not as an intermediate conversion step
- **Non-verbal signal capture**: Understands tone, emotion, and speech rhythm
- **Mimi audio codec**: A custom streaming neural audio codec optimized for low-latency high-quality output

**Benchmark (Llama Questions)**:

| Model | Score |
|-------|-------|
| **Moshi** | **62.3** |
| SpeechGPT | 21.6 |

**All links**:

| Resource | Link |
|----------|------|
| GitHub | [kyutai-labs/moshi](https://github.com/kyutai-labs/moshi) |
| HuggingFace (PyTorch, male voice Moshiko) | [kyutai/moshiko-pytorch-bf16](https://huggingface.co/kyutai/moshiko-pytorch-bf16) |
| HuggingFace (PyTorch, female voice Moshika) | [kyutai/moshika-pytorch-bf16](https://huggingface.co/kyutai/moshika-pytorch-bf16) |
| **Apple Silicon MLX (male, BF16)** | [kyutai/moshiko-mlx-bf16](https://huggingface.co/kyutai/moshiko-mlx-bf16) |
| **Apple Silicon MLX (female, BF16)** | [kyutai/moshika-mlx-bf16](https://huggingface.co/kyutai/moshika-mlx-bf16) |
| **Apple Silicon MLX (Q4 quantized, low RAM)** | [kyutai/moshiko-mlx-q4](https://huggingface.co/kyutai/moshiko-mlx-q4) |
| HuggingFace model docs | [transformers/moshi](https://huggingface.co/docs/transformers/model_doc/moshi) |
| Paper | [arXiv:2410.00037](https://huggingface.co/papers/2410.00037) |

Mac users should download the MLX Q4 quantized version — it dramatically reduces memory requirements and runs on M1/M2 devices.

---

### Mini-Omni — 0.5B Parameter Model, Small but Capable

Released by the gpt-omni team, Mini-Omni is an ultra-lightweight end-to-end voice dialogue model with **only 0.5B parameters** — one of the smallest runnable realtime voice models known today.

**Key technical innovations**:

- **No separate ASR/TTS modules**: Pure end-to-end generation, no Whisper + TTS pipeline required
- **Parallel text + audio token generation**: Generates text and speech tokens simultaneously, eliminating serial waiting
- **Batch Parallel Decoding**: Lets speech generation borrow from text reasoning capabilities
- Uses Qwen2 as the language backbone + SNAC audio decoder
- Mini-Omni2 adds **vision + audio + text** trimodal support

**All links**:

| Resource | Link |
|----------|------|
| GitHub (Mini-Omni) | [gpt-omni/mini-omni](https://github.com/gpt-omni/mini-omni) |
| HuggingFace (Mini-Omni) | [gpt-omni/mini-omni](https://huggingface.co/gpt-omni/mini-omni) |
| GitHub (Mini-Omni2, with vision) | [gpt-omni/mini-omni2](https://github.com/gpt-omni/mini-omni2) |
| HuggingFace (Mini-Omni2) | [gpt-omni/mini-omni2](https://huggingface.co/gpt-omni/mini-omni2) |
| Paper | [arXiv:2408.16725](https://huggingface.co/papers/2408.16725) |

Mini-Omni's voice reasoning lags behind text mode, but its value lies in extreme accessibility — at 0.5B parameters, nearly any device can run it.

---

## Running Moshi on Apple Silicon Mac

Kyutai provides native MLX support:

```bash
# Install
pip install moshi-mlx

# Run (auto-downloads MLX quantized model from HuggingFace)
python -m moshi_mlx.local_web -q 4   # Q4 quantized, lowest RAM
python -m moshi_mlx.local_web -q 8   # Q8, better quality
```

Open `http://localhost:8998` in your browser to start a realtime voice conversation.

---

## Can They Actually Replace OpenAI?

| Dimension | OpenAI gpt-realtime | Moshi (open-source) | Mini-Omni (open-source) |
|-----------|---------------------|---------------------|------------------------|
| Latency | Undisclosed, commercial-grade | 160ms theoretical | Undisclosed |
| Language Quality | ★★★★★ | ★★★★ | ★★★ |
| Local Deployment | ✗ | ✓ | ✓ |
| Privacy | Data sent to cloud | Local only | Local only |
| Cost | $18/hour | **$0** | **$0** |
| Apple Silicon | ✗ | ✓ (MLX) | ✓ |
| Full-Duplex | ✓ | ✓ | Partial |

For **individual developers, researchers, and privacy-sensitive use cases**, Moshi is the most competitive open-source realtime voice solution available today. Mini-Omni's value is its extreme low resource requirement — 0.5B parameters means almost any device can run it.

OpenAI's commercial API still leads in quality and ecosystem maturity, but $18/hour makes sustained voice interaction applications unaffordable for most individuals and small teams. Open-source alternatives are closing the gap every quarter.

---

## Why This Matters

Voice is the most natural interface for human interaction. When the cost of realtime voice conversation drops from "$18/hour" to "free and local," what applications become possible?

- Unlimited-session language learning companions
- Privacy-preserving voice journals and emotional assistants
- Offline voice home assistants
- Voice control for lightweight IoT devices

Moshi and Mini-Omni are just the beginning. The open-sourcing of end-to-end realtime voice is systematically opening a market that OpenAI tried to own.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
