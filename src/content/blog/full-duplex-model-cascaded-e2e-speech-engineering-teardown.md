---
title: "Full-Duplex-Model 拆解：两路全双工语音方案，最低配 RTX 4090，AEC3 是关键"
description: "GHJ20001017/Full-Duplex-Model，基于 HuggingFace speech-to-speech 增强，提供级联方案（AEC3 + VAD + Parakeet/Paraformer ASR + LLM + TTS，接 OpenAI Realtime 协议）和端到端方案（重叠音流直接建模）。级联方案全本地跑通最低需 RTX 4090（24GB），开 AEC3 才能解决 AI 听自己说话的回声问题。端到端方案仍处于训练实验阶段，需要 A100 级 GPU。"
pubDate: 2026-09-29
heroImage: "../../assets/images/full-duplex-model-cascaded-e2e-speech-engineering-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["全双工", "语音AI", "AEC3", "实时推理", "开源拆解", "硬件要求"]
lang: "zh-CN"
wechatTitle: "Full-Duplex-Model：级联+端到端全双工语音方案"
wechatDigest: "AEC3消回声+级联管道；Parakeet+Paraformer；最低RTX 4090；E2E训练需A100"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 全双工到底难在哪

普通语音助手是半双工的：用户说完，检测到停顿，AI 才开始说话；AI 说话时，用户无法打断。全双工的目标是：**AI 一边说话一边在听，用户随时可以插话，AI 也随时可以响应**——像真实对话一样。

这有两个核心工程难题：

**1. 回声问题（Echo）**：AI 的扬声器输出被麦克风收进去，AI 就会「听到自己说话」，把自己的输出当用户输入处理，形成反馈环。这不是软件 bug，是物理问题——麦克风真的在收扬声器的声音。

**2. 打断问题（Barge-in）**：用户在 AI 说话过程中开口，系统需要识别这是真打断（要响应）还是背景噪声（要忽略），并在合适的语义断点切换发言权。

仓库：github.com/GHJ20001017/Full-Duplex-Model  
**定位：Cascaded Full-Duplex Model + End-to-End Full-Duplex Model 两种方案**  
基础：HuggingFace speech-to-speech（增强扩展版）

---

## 方案一：级联架构（工程落地用）

级联方案把全双工拆分成一条流水线，每个组件独立可替换：

```
麦克风输入
    ↓
AEC3（WebRTC EchoCanceller3）— 消回声
    ↓
VAD（语音活动检测）
    ↓
openWakeWord（唤醒词过滤）
    ↓
ASR（语音转文字）
  英文：Parakeet TDT（NVIDIA，0.6B）
  中文：Paraformer 流式
    ↓
LLM（任意 OpenAI 兼容端点）
    ↓
TTS（语音合成）
    ↓
OpenAI Realtime 协议（WebSocket + WebRTC）传输
```

### AEC3：回声问题的工程解

AEC3（EchoCanceller3）是 WebRTC 原生的声学回声消除模块，CPU 运行，无需 GPU。它在音频进入 VAD 和 ASR 之前，先把扬声器播放的信号从麦克风信号里减掉。

这是全双工架构的关键一环：没有 AEC3 或等效的回声消除，AI 就会把自己说的话重新识别为用户输入，触发无意义的回复循环。级联方案选择在信号层面解决这个问题，而不是让 LLM 去「理解」哪些是自己说的话。

### openWakeWord：唤醒门控

openWakeWord 在客户端本地运行（CPU），默认唤醒词是 `hey jarvis`。唤醒前不上传音频——这既节省带宽，也把计算资源留给真正需要响应的时刻。

对于 24 小时在线的设备，唤醒门控是必要设计：始终上传音频并跑 ASR，GPU 利用率会长期偏高，且产生大量无用转写。

### Parakeet：流式 ASR，500ms 出首个分段

英文 ASR 使用 NVIDIA Parakeet TDT（0.6B 参数），每 **500ms** 输出一次部分转写结果，滑动窗口划分句子边界。这意味着用户说话时，LLM 可以提前看到部分内容并开始思考，而不是等完整句子。

Parakeet TDT 0.6B v3 的 VRAM 占用约 **2GB**，需要 NVIDIA GPU，Compute Capability ≥ 7.5（即 Turing 架构，RTX 2000 系及以上）。

中文使用 Paraformer 流式版本，架构来自达摩院，同样支持实时流式输出。

### OpenAI Realtime 协议传输层

LLM 接入通过 OpenAI Realtime 协议完成，支持 WebSocket 和 WebRTC 两种传输方式。WebRTC 处理网络抖动、丢包和时钟漂移——实时语音延迟要求严苛，TCP 的重传机制反而会造成卡顿，WebRTC 基于 UDP 并有完善的 QoS 机制。

---

## 方案二：端到端架构（研究方向）

端到端方案直接从**重叠音频流**建模输出音频：用户说话和 AI 说话的混合音频进入模型，直接输出 AI 的回应音频，中间不经过 STT / LLM / TTS 三步分解。

理论优势是延迟更低——级联方案的每个组件都有处理时延（ASR 500ms 首个分段 + LLM 首 token + TTS 首片段），理论上全链路在 800ms 到 1.5 秒之间。端到端模型消除了这些串行开销，有望实现真正的「实时感」（<300ms）。

但目前这部分仍是**训练代码 + 实验方向**，不是可以直接部署的推理服务。

---

## 硬件要求量化

### 级联方案各组件 VRAM 分解

| 组件 | 运行方式 | VRAM 需求 |
|------|---------|---------|
| AEC3 回声消除 | CPU 原生 WebRTC | 0 |
| openWakeWord 唤醒 | CPU | 0 |
| VAD | CPU | 0 |
| Parakeet TDT 0.6B（英文 ASR） | GPU | ~2GB |
| Paraformer 流式（中文 ASR） | GPU | ~2-3GB |
| TTS（HuggingFace speech-to-speech） | GPU | ~2-4GB |
| LLM 3B 量化 | GPU | ~4-6GB |
| LLM 7B/8B 全精度 | GPU | ~14-16GB |
| LLM 7B/8B 量化 INT4 | GPU | ~4-6GB |

### 三种部署配置

**配置 A：全本地，旗舰消费级（RTX 4090 / 24GB VRAM）**

- Parakeet ASR：2GB
- LLM 8B 量化：~5-6GB
- TTS：~3GB
- 其余组件 CPU
- 合计：~10-11GB，有余量跑 LLM 更大量化版本
- 这是目前能全本地跑的**最低实用配置**，不含 LLM 全精度

如要本地跑 LLM 全精度 8B，合计约 20-22GB，仍在 24GB 边界内，但没有余量。

**配置 B：全本地，数据中心级（A100 40GB）**

- 可以运行 LLM 70B 量化版，或多路并发
- 合计 <40GB，有余量
- 建议 E2E 方案训练和推理使用

**配置 C：LLM 云端，本地只跑 ASR + TTS（RTX 3060 / 12GB）**

- Parakeet ASR：2GB
- TTS：3GB
- LLM 走 OpenAI / Anthropic / 自建 API
- 合计：~5GB，RTX 3060（12GB）轻松跑
- 但 LLM 调用延迟受网络影响，不适合延迟要求极严格的场景

### 延迟预算（级联方案）

| 阶段 | 典型延迟 |
|------|---------|
| AEC3 处理 | ~1ms |
| VAD + 唤醒词 | ~30ms |
| ASR（首个分段） | ~500ms |
| LLM 首 token（本地 8B 量化） | ~100-300ms |
| TTS 首帧 | ~200-400ms |
| **链路总延迟（首字可听）** | **~800ms–1.2s** |

800ms–1.2 秒是真实的级联方案延迟。研究数据显示：<300ms 感觉自然，500ms 感觉有轻微延迟，>700ms 用户感知明显。级联方案目前仍在「明显有延迟」区间，但对于大多数客服/助手场景可以接受。

端到端方案的目标是把这个延迟压到 300ms 以内，但训练成本和推理硬件要求也随之大幅上升。

---

## 三个需要正视的问题

### 1. 级联和端到端是两个独立工程问题

级联方案的核心挑战是**把各组件的延迟叠加控制在可接受范围内**，以及 AEC3 和 LLM 打断逻辑的调优。端到端方案的挑战是**收集足够的重叠音频训练数据**，以及推理时的实时性保证。两者不是同一条技术路线，不能混用。

### 2. 唤醒词方案牺牲了「真全双工」体验

openWakeWord 门控意味着不说 "hey jarvis" 就不上传音频——这是有意为之的设计取舍，但从用户体验角度，它不是「随时可以说话」的全双工，而是「唤醒后全双工」。真正的免唤醒全双工需要始终运行 VAD，计算资源消耗更高。

### 3. 端到端方案仍是训练代码

仓库里的端到端部分目前是训练框架，还没有对应的推理服务部署示例。工程落地需要自行实现推理 server，并解决实时流式解码的工程细节。

---

## 工程价值在哪

对于想自建全双工语音助手的团队，这个仓库的实际价值是：

1. **AEC3 集成方案**：WebRTC 原生回声消除与 Python 语音管道的集成代码，这个细节通常需要自己踩坑
2. **OpenAI Realtime 协议的开源实现**：理解协议结构，在不依赖 OpenAI 云端的前提下自建全双工通道
3. **中英双语 ASR 切换**：Parakeet（英文）+ Paraformer（中文）的流式双轨配置

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| 方案类型 | 级联（生产）+ 端到端（研究） |
| 回声消除 | WebRTC AEC3，CPU，0 VRAM |
| ASR（英文） | Parakeet TDT 0.6B，~2GB VRAM |
| ASR（中文） | Paraformer 流式，~2-3GB VRAM |
| ASR 首分段延迟 | 500ms |
| 全本地最低配置 | RTX 4090（24GB） |
| ASR+TTS 云 LLM 最低配置 | RTX 3060（12GB） |
| E2E 训练最低配置 | A100 40GB |
| 级联方案总延迟 | ~800ms–1.2s（首字可听） |

---

## 综合判断

Full-Duplex-Model 是一个工程实用性较强的参考实现，把 AEC3 集成、流式 ASR、OpenAI Realtime 协议这几块不容易的工程细节打通了。级联方案可以直接落地：RTX 4090 全本地，或 RTX 3060 + 云端 LLM 都能跑。

硬件要求的实质是 LLM 的大小。AEC3、VAD、唤醒词检测都是 CPU 任务，Parakeet ASR 只要 2GB，TTS 要 3-4GB——真正吃显存的是 LLM。如果 LLM 走 API，12GB 消费级 GPU 就够了；要本地大模型，才需要 RTX 4090 起步。

端到端方案还在研究阶段，不建议作为生产路线，但作为了解全双工建模方向的学习材料有价值。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## Full-Duplex-Model Teardown: Two Approaches, RTX 4090 Minimum, AEC3 Is the Key

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Why Full-Duplex Is Hard

Normal voice assistants are half-duplex: wait for the user to stop, detect silence, then respond. Full-duplex means the AI listens while speaking — users can interrupt anytime.

Two core engineering problems:

**1. Echo problem**: The speaker output gets picked up by the microphone. The AI hears itself and treats its own output as user input. This is a physics problem, not a software bug.

**2. Barge-in detection**: When the user speaks while the AI is talking, the system must decide: real interruption (respond) or background noise (ignore), and switch roles at a semantically clean breakpoint.

Repo: github.com/GHJ20001017/Full-Duplex-Model  
**Two approaches: Cascaded (production-oriented) + End-to-End (research direction)**  
Base: HuggingFace speech-to-speech, significantly extended

---

### Approach 1: Cascaded Architecture (Production Use)

```
Mic input
  → AEC3 (WebRTC EchoCanceller3) — echo cancellation
  → VAD (voice activity detection)
  → openWakeWord — local wake-word gating
  → Streaming ASR: Parakeet TDT (English) / Paraformer (Chinese)
  → LLM (any OpenAI-compatible endpoint)
  → TTS
  → OpenAI Realtime Protocol (WebSocket + WebRTC) transport
```

**AEC3** runs on CPU (WebRTC native). It subtracts the speaker signal from the microphone feed before any voice processing. Without this, the AI feeds back on itself indefinitely. The cascaded design solves echo at the signal level, not at the LLM reasoning level.

**openWakeWord** runs on CPU. Default wake word: "hey jarvis". No audio is uploaded before activation — this saves bandwidth and compute for always-on devices.

**Parakeet TDT 0.6B** (English ASR): outputs partial results every **500ms** with sliding window sentence boundaries, allowing the LLM to start processing before the user finishes speaking. VRAM: ~2GB. Requires NVIDIA GPU, Compute Capability ≥ 7.5 (Turing / RTX 2000+).

**Paraformer** (Chinese ASR): streaming version from DAMO Academy, ~2-3GB VRAM.

**OpenAI Realtime Protocol** over WebSocket + WebRTC. WebRTC uses UDP with QoS — for real-time audio, TCP retransmission causes stutter; WebRTC handles packet loss and jitter correctly.

---

### Approach 2: End-to-End Architecture (Research)

The E2E model directly processes **overlapping audio streams** (user + AI audio mixed) and outputs the AI's response audio. No STT → LLM → TTS decomposition.

Theory: eliminating the serial cascade removes most latency (target: sub-300ms vs. ~800ms–1.2s for cascaded).

Reality: this part is **training code + research direction**. There is no deployable inference server included. Production deployment requires implementing the inference server and solving real-time streaming decoding from scratch.

---

### Hardware Requirements

**VRAM by component:**

| Component | Runtime | VRAM |
|-----------|---------|------|
| AEC3 echo cancellation | CPU | 0 |
| openWakeWord | CPU | 0 |
| VAD | CPU | 0 |
| Parakeet TDT 0.6B (English ASR) | GPU | ~2GB |
| Paraformer streaming (Chinese ASR) | GPU | ~2–3GB |
| TTS | GPU | ~2–4GB |
| LLM 8B INT4 quantized | GPU | ~4–6GB |
| LLM 8B full precision | GPU | ~14–16GB |

**Three deployment configurations:**

**Config A — All-local, consumer tier (RTX 4090, 24GB)**
- Parakeet: 2GB + LLM 8B INT4: ~5GB + TTS: 3GB = ~10GB. RTX 4090 (24GB) is the practical minimum for a fully local stack with a capable LLM. Running LLM full precision 8B pushes to ~20–22GB, right at the limit.

**Config B — All-local, datacenter (A100 40GB)**
- Enables 70B quantized LLM, multi-session concurrency, or E2E model inference.

**Config C — Cloud LLM, local ASR + TTS (RTX 3060, 12GB)**
- Parakeet + TTS: ~5GB total. RTX 3060 (12GB) comfortably handles ASR and TTS; LLM is a remote API call. Latency depends on network, not suitable for sub-500ms requirements.

**Cascaded latency budget:**

| Stage | Typical |
|-------|---------|
| AEC3 | ~1ms |
| VAD + wake word | ~30ms |
| ASR first partial | ~500ms |
| LLM first token (local 8B INT4) | ~100–300ms |
| TTS first frame | ~200–400ms |
| **Total to first audible word** | **~800ms–1.2s** |

Research benchmarks: <300ms feels natural, 500ms slightly delayed, >700ms noticeably broken. Cascaded approaches currently sit in the "perceptible but acceptable" range for most assistant use cases.

---

### Three Engineering Caveats

**1. Cascaded and E2E are separate engineering problems.** Cascaded: tune latency per component and AEC3/barge-in logic. E2E: collect overlapping audio training data and build a real-time inference server. You cannot mix them.

**2. Wake-word gating is not true always-on full-duplex.** "hey jarvis" before speaking is a deliberate tradeoff — it saves compute at the cost of "always ready to talk" UX. True always-on requires continuous VAD running 24/7.

**3. E2E is not deployable yet.** Training framework only; no inference server or streaming decoding example included.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Echo cancellation | AEC3 WebRTC, CPU, 0 VRAM |
| ASR (English) | Parakeet TDT 0.6B, ~2GB VRAM |
| ASR first partial | 500ms |
| Min all-local config | RTX 4090 (24GB) |
| Min ASR+TTS only (cloud LLM) | RTX 3060 (12GB) |
| Min E2E training | A100 40GB |
| Cascaded total latency | ~800ms–1.2s |

---

### Verdict

The real hardware gate is the LLM. AEC3, VAD, and wake-word are all CPU tasks. Parakeet needs only 2GB VRAM. TTS needs 3–4GB. If you use a remote LLM API, a 12GB consumer GPU handles everything local. If you want local LLM inference with a capable 8B model, RTX 4090 (24GB) is the minimum.

The cascaded implementation provides valuable reference for AEC3 Python integration and OpenAI Realtime protocol, which are non-trivial to wire together. The E2E direction is worth watching but not ready for production.

---

> Open source for learning only. Verify license terms before commercial use.
