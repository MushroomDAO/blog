---
title: 'VoiceMem：流式双脑架构，给语音 Agent 装上真正的记忆'
titleEn: "VoiceMem: Streaming Dual-Brain Architecture for Real Voice Agent Memory"
description: "清华团队的 VoiceMem 用左脑存事实、右脑存情感，流式投机预取让检索在你说完之前就跑完，LoCoMo 达到 91.2%，比 Mem0 快 10x、省 16x token，Apache 2.0 永久开源。"
descriptionEn: "Tsinghua's VoiceMem uses a left brain for facts and right brain for emotion, streaming speculative prefetch finishes retrieval before you stop talking — 91.2% on LoCoMo, 10x faster and 16x cheaper than Mem0, Apache 2.0 forever."
pubDate: "2026-09-13"
updatedDate: "2026-09-13"
category: "Tech-News"
tags: ["voice-agent", "memory", "open-source", "streaming", "LLM", "audio-AI", "VoiceMem"]
heroImage: "../../assets/voicemem-streaming-dual-brain-voice-agent-memory-banner.jpg"
---

> 📌 开源仓库：xzf-thu/VoiceMem
> GitHub：https://github.com/xzf-thu/VoiceMem
> 项目主页：https://xzf-thu.github.io/VoiceMem/
> arXiv：2608.26005
> License：Apache 2.0 | Stars：1.4K+
> 作者：谢志飞等，清华大学

---

语音 Agent 一直缺一块拼图。

LLM 已经能流畅对话，ASR 延迟压到了 200ms 以内，TTS 开始支持打断和情感语调——但记忆这件事，还停在"把历史对话塞进 context"的暴力方案上。塞进去之后：搜准度差、token 爆炸、每次对话都重新加载所有历史，还完全不懂用户是个什么样的人。

VoiceMem 专门解决这个问题。它不是通用记忆框架的语音版本，而是从语音 Agent 的实时需求出发重新设计的记忆系统——架构叫「流式双脑」。

---

## 一、左脑存事实，右脑存情感

VoiceMem 的核心设计决策是**把记忆拆成两个不同的脑**，而不是塞进同一个向量库。

**左脑**负责事实记忆。它用 Schema + Entity 的方式组织信息：用户说「我对坚果过敏」，左脑会提取出 `entity: 用户` + `schema: 饮食禁忌` + `value: 坚果过敏`，写入结构化节点。下次查询「我的饮食禁忌」，左脑做精确的结构化检索，不靠向量相似度猜，结果就是准。

**右脑**负责情感和人格。它独立维护情绪节点和跨实体节点：用户某次说话时情绪低落，右脑会把这次情绪事件归因到时间线上；用户对某个话题总是兴奋，右脑会建立一个「用户对 X 感兴趣」的跨实体节点。这些信息和左脑的事实节点联合维护——知道用户是谁，也知道用户有什么感受。

两个脑各自检索，结果分开输出，给模型的时候是 `result_leftbrain` + `result_rightbrain` 两个独立字段。模型可以选择性使用，不需要把情绪信息和事实信息混在一起。

---

## 二、流式查询：说话说到一半，记忆已经查好了

这是 VoiceMem 最不显眼、但工程含量最高的设计。

传统做法：等用户说完 → ASR 转写 → 拿全文去查记忆 → 等查询结果 → 开始生成回复。每个环节串行，记忆查询本身就要 1.4 秒（Mem0 实测）。

VoiceMem 的做法：**边说边转写，转写够了就投机预取**。

```python
SPEC_MIN_CHARS = 6  # 攒够 6 个字就开始后台查

def on_partial(text):
    global searching
    if not searching and len(text) >= SPEC_MIN_CHARS:
        searching = True
        # 后台已经开查了，人还没说完
```

用户说「我的饮食…」，才 5 个字，VoiceMem 就已经在后台跑检索了。等用户说完「我的饮食禁忌是什么」，记忆早就查好放在那等着了。

实测延迟：**134ms**，而 Mem0 是 **1,440ms**。快了 10.7 倍。这个数字的含义是：语音 Agent 首 token 延迟不再被记忆查询拖累。

---

## 三、搜准度和 token 消耗：两个都赢

记忆系统的核心矛盾是**准度和 token 消耗的 tradeoff**：想准就多塞历史，多塞就贵。

VoiceMem 在两个方向都给出了比较极端的结果：

| 指标 | VoiceMem | Mem0 | EverMemOS |
|------|----------|------|-----------|
| LoCoMo（事实记忆） | **91.2%** | 61.68% | — |
| PersonaMem（人格理解） | **69.44%** | — | — |
| 检索延迟 | **134ms** | 1,440ms | — |
| 记忆 token/次 | **430** | 6,956 | 1,899 |
| 最大检索条数 | Top-5 | — | — |

LoCoMo 基准测试的协议是：只给模型检索到的记忆，不给原始对话历史，测模型能不能答对。这测的是记忆系统本身，不是模型的阅读理解能力。VoiceMem 在 10 个对话、152 个问题上跑出 91.4%，其中 multi-hop 88.2%、temporal 85.7%、single-hop 95.1%。

430 token 是什么概念？Claude Sonnet 上下文 200K，但每次请求付费按 token 算。一个对话用 6,956 token 的记忆注入，和用 430 token，同样的对话量差 16 倍的成本。

---

## 四、多模态输入：不只是文字

VoiceMem 的入库接口接受**音频文件**，内部自动完成：
- ASR 转写（paraformer-zh-streaming）
- 说话人识别（3D-Speaker）
- 场景感知
- 情绪检测
- 本地 Embedding 抽取

这意味着不需要先把音频转成文字再送给记忆系统。可以直接扔一段多人对话的录音进去，VoiceMem 会区分不同说话人，分别建立记忆节点。

```python
vm = VoiceMem(mode="normal", openai_key="api_xxx", top_k=5)
vm.warmup()
vm.ingest(audio="assets/input.wav")  # 直接喂音频
result = vm.search("我的饮食禁忌是什么？")
print(result.result_leftbrain, result.result_rightbrain)
```

本地推理全部用 CPU/Metal 跑，不需要 GPU。`warmup()` 是懒加载提前预热，避免第一次查询等模型加载。

---

## 五、接入自己的语音模型：只替换生成那一步

VoiceMem 的架构是完全解耦的：记忆部分和生成部分之间只有一个接口——`memory_context`。

```python
def my_reply(text, memory_context):
    return my_model.generate(system=memory_context, user=text)

vm = VoiceMem(reply=my_reply)
```

换上自己的模型，记忆那半边一行都不用动。OpenAI API 只用于入库时的**事实信息提取**，检索完全在本地跑。

官方还开源了 VoiceMem 模型系列（Qwen2.5-Omni、Qwen3-Omni、Step-Audio2-Mini 的适配器），这些模型经过 ChatMem-400K 数据集的三阶段 OPD 训练，能直接理解 VoiceMem 输出的记忆格式，不需要额外的 prompt 工程。

---

## 六、几个值得关注的工程细节

**SessionBuffer 和长期记忆的分界**：每轮对话先进内存 SessionBuffer，异步写入确认产生持久记忆后才从 Buffer 移除。没有产生长期记忆的临时对话保留到本次会话结束。不同 Memory Space 和不同 WebSocket 会话互相隔离。

**打断处理是两阶段的**：VAD 首先暂停并保留音频队列；明确停止指令或稳定 ASR 文本确认后才清空并取消回复。附和、回声、单音节碎片会恢复播放，不触发打断。

**TTS 时间轴对齐**：两种回复模式共用以 PCM 样本位置为基准的输出时间轴。浏览器 AudioWorklet 回报实际渲染进度，打断时只把已经播放的回复写入 SessionBuffer——没播完的那部分不会被记录为"用户已经听到的内容"。

---

## 安装与快速试用

```bash
git clone https://github.com/xzf-thu/VoiceMem.git
cd VoiceMem
pip install voicemem

# 可选：官方微调的 Qwen 回复模型
pip install "voicemem[slm]"

# 下载本地模型（ASR/声纹/场景/情绪/Embedding 全套）
pip install -U huggingface_hub
hf download zhifeixie/VoiceMem_Default_Models_Env --local-dir ./models

# 本地 Web Demo
python web/run.py
# 访问 http://localhost:8787
```

---

## 拆解结论

VoiceMem 解决的是一个真实问题：**现有语音 Agent 要么不会记忆，要么记忆方式贵且慢且准度差**。它的技术路线不是"通用记忆系统加语音接口"，而是针对实时语音交互场景重新设计——流式查询、双脑分离、本地推理、最小 token 注入。

1,445 stars，Apache 2.0，从首发到现在不到一个月，v0.0.2 已经修了事件日期链路、移除右脑冗余类别、开放 TTS 层。从节奏来看，这个项目是在认真迭代的。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: xzf-thu/VoiceMem
> GitHub: https://github.com/xzf-thu/VoiceMem
> Project Page: https://xzf-thu.github.io/VoiceMem/
> arXiv: 2608.26005
> License: Apache 2.0 | Stars: 1.4K+
> Authors: Zhifei Xie et al., Tsinghua University

---

Voice agents have been missing one piece.

LLMs already hold a fluid conversation. ASR latency is below 200ms. TTS is starting to handle interrupts and emotional tone — but memory still lives in the "stuff the full history into context" brute-force zone. The consequences: poor recall precision, token explosions, full history reload every turn, and no concept of who the user actually is.

VoiceMem addresses this directly. It's not a general-purpose memory framework with a voice wrapper tacked on. It's a memory system redesigned from scratch for real-time voice agent requirements — built on what they call a "streaming dual-brain" architecture.

---

## I. Left Brain for Facts, Right Brain for Emotion

VoiceMem's core design decision: **split memory into two different brains** rather than pushing everything into a single vector store.

The **left brain** handles factual memory. It organizes information using Schema + Entity: when the user says "I'm vegetarian and allergic to nuts," the left brain extracts `entity: user` + `schema: dietary restriction` + `value: nut allergy` and writes it as a structured node. Next query: "what are my dietary restrictions?" — the left brain does precise structural retrieval, no vector similarity guessing. The results are accurate.

The **right brain** handles emotion and personality. It independently maintains emotion nodes and cross-entity nodes: if the user sounded low during one conversation, the right brain attributes that emotional event onto a timeline. If the user is consistently enthusiastic about some topic, the right brain builds a cross-entity node for "user is interested in X." This information is jointly maintained with the left brain's factual nodes — knowing who the user is, and also knowing how they feel.

The two brains retrieve independently and output separately: `result_leftbrain` + `result_rightbrain` as distinct fields. The model can use them selectively — no forced blending of emotional state with factual content.

---

## II. Streaming Retrieval: Memory Done Before You Finish Talking

This is VoiceMem's least visible but most engineered design.

The traditional flow: wait for user to finish → ASR transcription → full text retrieval → wait for results → begin generation. Every step in series. Memory lookup alone takes 1.4 seconds (Mem0 benchmarked).

VoiceMem's approach: **transcribe as you speak, speculative prefetch when there's enough text**.

```python
SPEC_MIN_CHARS = 6  # six characters in and retrieval starts in the background

def on_partial(text):
    global searching
    if not searching and len(text) >= SPEC_MIN_CHARS:
        searching = True
        # retrieval already running, user hasn't finished yet
```

The user says "what are my diet…" — five characters in — and VoiceMem has already kicked off retrieval in the background. By the time they complete "what are my dietary restrictions?", the memory results are ready and waiting.

Measured latency: **134ms**, versus Mem0 at **1,440ms**. That's 10.7x faster. What this means in practice: a voice agent's time-to-first-token is no longer bottlenecked by memory retrieval.

---

## III. Accuracy and Token Cost: Winning Both

Memory systems face a core tradeoff: **precision vs. token cost**. More history → better recall → more expensive.

VoiceMem delivers fairly extreme numbers on both dimensions:

| Metric | VoiceMem | Mem0 | EverMemOS |
|--------|----------|------|-----------|
| LoCoMo (factual) | **91.2%** | 61.68% | — |
| PersonaMem (personality) | **69.44%** | — | — |
| Retrieval latency | **134ms** | 1,440ms | — |
| Memory tokens / query | **430** | 6,956 | 1,899 |
| Max retrieved | Top-5 | — | — |

The LoCoMo benchmark protocol: give the model only retrieved memories (no raw conversation history) and test whether it can answer questions. It measures the memory system, not the model's reading comprehension. VoiceMem hits 91.4% on 10 conversations, 152 questions — multi-hop 88.2%, temporal 85.7%, single-hop 95.1%.

430 tokens in context versus 6,956: 16x cheaper per query at the same conversation volume.

---

## IV. Multimodal Input: Beyond Text

VoiceMem's ingest interface accepts **audio files directly**, internally running:
- ASR transcription (paraformer-zh-streaming)
- Speaker identification (3D-Speaker)
- Scene detection
- Emotion recognition
- Local embedding extraction

No preprocessing step required. Feed a multi-party conversation recording and VoiceMem separates speakers, building independent memory nodes for each.

```python
vm = VoiceMem(mode="normal", openai_key="api_xxx", top_k=5)
vm.warmup()
vm.ingest(audio="assets/input.wav")  # direct audio input
result = vm.search("what are my dietary restrictions?")
print(result.result_leftbrain, result.result_rightbrain)
```

All local inference runs on CPU/Metal — no GPU needed. `warmup()` handles lazy model preloading so the first query doesn't stall waiting for model initialization.

---

## V. Plugging In Your Own Voice Model

VoiceMem's architecture is fully decoupled. The interface between memory and generation is a single point: `memory_context`.

```python
def my_reply(text, memory_context):
    return my_model.generate(system=memory_context, user=text)

vm = VoiceMem(reply=my_reply)
```

Swap in your own model; the memory side is unchanged. The OpenAI API is used only for **fact extraction at write time** — retrieval runs entirely locally.

The team also open-sourced the VoiceMem model family (adapters for Qwen2.5-Omni, Qwen3-Omni, Step-Audio2-Mini) trained on ChatMem-400K via a three-stage OPD pipeline. These models natively understand VoiceMem's memory output format without additional prompt engineering.

---

## VI. Engineering Details Worth Noting

**SessionBuffer vs. persistent memory**: Each conversation turn first goes into an in-memory SessionBuffer. After async memory write confirms a persistent memory was created, the turn is evicted from the buffer. Turns that don't produce long-term memories persist until end-of-session. Different Memory Spaces and different WebSocket sessions are isolated from each other.

**Two-phase interrupt handling**: VAD first pauses and holds the audio queue; a definitive stop signal or stable ASR confirmation then clears the queue and cancels the reply. Back-channels, echo, and sub-second fragments restore playback without triggering an interrupt.

**TTS timeline alignment**: Both reply modes share a PCM-sample-position output timeline. The browser AudioWorklet reports actual render progress; at interrupt time, only the already-played portion of the reply is written into SessionBuffer — the unplayed part is not recorded as "user already heard this."

---

## Quick Start

```bash
git clone https://github.com/xzf-thu/VoiceMem.git
cd VoiceMem
pip install voicemem

# Optional: official fine-tuned Qwen reply model
pip install "voicemem[slm]"

# Download bundled local models (ASR / speaker ID / scene / emotion / embedding)
pip install -U huggingface_hub
hf download zhifeixie/VoiceMem_Default_Models_Env --local-dir ./models

# Local web demo
python web/run.py
# Visit http://localhost:8787
```

---

## Teardown Summary

VoiceMem addresses a real problem: **existing voice agents either don't do memory at all, or do it in ways that are expensive, slow, and imprecise**. The technical approach isn't "general memory system with a voice interface" — it's a ground-up redesign for real-time voice interaction: streaming retrieval, dual-brain separation, local inference, minimal token injection.

1,445 stars, Apache 2.0, less than a month since first release. v0.0.2 already fixed event date attribution, removed redundant right-brain categories, and opened up the TTS layer. The iteration cadence suggests this is being actively developed.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
