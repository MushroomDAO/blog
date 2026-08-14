---
title: "dots.tts：2B 全连续自回归 TTS——为什么不用离散 Token，以及这个科研底座能赋能哪些新应用"
titleEn: "dots-tts-2b-continuous-autoregressive-meanflow-voice-clone-zero-shot"
description: "dots.tts 是 dots 团队联合上交大 X-LANCE 实验室开源的全连续端到端自回归 TTS 基座模型（2B 参数）。区别于 VALL-E 等离散 Token 路线，dots.tts 直接在 AudioVAE 压缩的连续隐空间逐块生成波形，语言模型骨干为 Qwen2.5-1.5B-Base，配 AR 流匹配头（MeanFlow）。在 Seed-TTS-Eval 上达到 SOTA。开放 7 个 checkpoint、支持 SGLang Omni、提供 dots.tts.edit 语音编辑能力。本文分析其技术架构，并从科研底座出发，列举 8 个可以在这个基础上赋能的新 Feature。"
descriptionEn: "dots.tts is a 2B-parameter, fully continuous end-to-end autoregressive TTS foundation model open-sourced by dots team and X-LANCE Lab (SJTU). Unlike discrete-token approaches (VALL-E etc.), it generates audio chunk-by-chunk in the continuous latent space of AudioVAE, using Qwen2.5-1.5B-Base as the LLM backbone with an AR flow-matching head (MeanFlow). SOTA on Seed-TTS-Eval. 7 checkpoints released, SGLang Omni compatible, dots.tts.edit for instruction-controlled speech editing. This article analyzes the architecture and proposes 8 new features the foundation enables."
pubDate: "2026-08-14"
updatedDate: "2026-08-14"
category: "Tech-News"
tags: ["TTS", "语音合成", "自回归", "连续隐空间", "AudioVAE", "MeanFlow", "零样本克隆", "开源", "上交大"]
heroImage: "../../assets/images/dots-tts-2b-continuous-autoregressive-meanflow-voice-clone-zero-shot-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：studio-dots-ai/dots.tts  
参数量：2B  
许可证：开源  
合作：dots 团队 + 上海交通大学 X-LANCE 实验室  
评测：Seed-TTS-Eval SOTA（2026-08）

---

「语音合成还在卷离散 Token？这次我们换了条路。」

这是 dots.tts 项目的自我定位。换了什么路？从**离散声学 Token**（VQ-VAE、EnCodec、SoundStream）转向**连续隐空间直接生成**，配合 AR 流匹配头（MeanFlow）代替传统自回归分类。

这条路在文本侧有前例：连续嵌入的扩散语言模型（如 MDT、MDLM）。dots.tts 把这个思路搬进了语音侧，并且做成了完整可用的基座。

---

## 一、技术架构

### 全局设计

```
文本 + 参考音频（3秒）
      ↓
Qwen2.5-1.5B-Base（LLM 骨干，无 Chat template）
      ↓
AR 流匹配头（MeanFlow）
      ↓ 逐块预测连续隐向量
AudioVAE 解码器（48kHz 波形）
      ↓
最终音频
```

三个核心组件各有分工：

### 1. AudioVAE：把连续音频压缩进隐空间

AudioVAE 是整个系统的「编解码器」，负责把 48kHz 的真实音频压缩成低维连续向量序列，以及把生成的隐向量序列解码回音频。

关键设计：
- **连续隐空间**：不经过 VQ（向量量化）或任何离散化步骤
- **48kHz 输出**：比大多数 TTS 系统（24kHz）高一倍的采样率，支持宽带音频
- **压缩率**：具体 token rate 未公开，但「逐块」结构意味着 LLM 处理的序列长度可控

离散 Token 方案（EnCodec、SoundStream）的痛点在于量化误差——量化是不可逆的信息损失，会在音质和情感细节上留下天花板。连续隐空间没有量化，理论上信息损失更低。

### 2. Qwen2.5-1.5B-Base：语言模型骨干

dots.tts 不是从头训练的声学模型，而是在预训练语言模型上扩展语音能力：

- **基底**：Qwen2.5-1.5B-Base（注意：Base，不是 Chat 版本）
- **扩展**：加入语音模态的嵌入和输出头，在语音数据上继续训练

这个选择有深意：Base 模型没有 RLHF 的对话格式约束，自回归生成更自然；Qwen2.5 的中英双语能力意味着 TTS 系统天然支持中英混读，无需专门处理语言切换。

### 3. AR 流匹配头（MeanFlow）

这是架构中最核心的创新点。

传统 AR-TTS 在离散 Token 上做分类：每一步选择下一个 Token（vocabulary 上的 softmax）。这不适用于连续隐向量——连续空间无法分类。

dots.tts 的解法：**用流匹配（Flow Matching）做连续空间的下一步预测**。

MeanFlow 具体做什么：对于每一步要生成的连续隐向量，它建模一个从噪声到目标的流，训练目标是预测这个流的「均值轨迹」（Mean trajectory）。这比标准扩散推理快（步数更少），比 DDPM 类方法稳定。

效果：在 Seed-TTS-Eval 上达到 SOTA，说明这条路可行。

---

## 二、7 个 Checkpoint 和产品能力

dots.tts 开放了 7 个 checkpoint，覆盖不同能力层：

- **dots.tts**：基础 TTS，文本→语音，支持零样本音色克隆（3秒参考音频）
- **dots.tts.edit**：语音编辑——给定音频 + 文字指令（如「让这段话听起来更疑惑」），输出改变了情感/风格的新音频

**dots.tts.edit 是一个独立的能力**，需要单独的模型权重，不是 TTS 的 post-processing。它的输入是 `(音频, 编辑指令)`，输出是修改后的音频，保留原始音色，改变情感、强调、语速等维度。

**SGLang Omni 兼容**：可以把 dots.tts 作为 SGLang 多模态推理服务的一个组件，接入现有的推理基础设施。

---

## 三、与同类系统的比较

| 维度 | dots.tts | VALL-E / SoundStorm | CosyVoice / F5-TTS | ElevenLabs |
|------|----------|---------------------|-------------------|------------|
| **隐空间类型** | 连续（AudioVAE） | 离散（EnCodec） | 混合（flow+codec） | 未公开（商业） |
| **生成方式** | AR + 流匹配 | AR + 分类 | 扩散/flow | 未公开 |
| **LLM 骨干** | Qwen2.5-1.5B | 专用 AR / 无 | DiT / 专用 | 未公开 |
| **采样率** | 48kHz | 24kHz | 24kHz | 44.1kHz |
| **语音编辑** | ✅ dots.tts.edit | ❌ | ❌ | 商业版有限支持 |
| **开源** | ✅ | 部分 | ✅ | ❌ |
| **Seed-TTS-Eval** | SOTA（2026-08） | 较差 | 竞争 | 未公开 |

---

## 四、这个科研底座能赋能哪些新 Feature？

这是用户最关心的问题：**基于 dots.tts 的连续 AR 架构，我们能做哪些现有 TTS 系统做不好的事？**

### Feature 1：细粒度情感控制（比提示词更精准）

dots.tts.edit 已经有文字指令控制语音风格的能力。在此基础上，可以扩展成**量化情感控制**：不是说「让这段话更开心」，而是「情感强度 0.7，对话感 0.4」——在连续隐空间直接插值，而不是通过文本提示间接影响。

离散 Token 系统做这件事很难（要控制就是换 Token，粒度粗）。连续空间天然支持插值。

### Feature 2：多角色对话音频，一次推理出多条轨道

一段对话脚本：`[A说] 你好 / [B说] 你好呀 / [A说] 最近怎么样`。现有系统需要分别生成三次，然后手动拼接。

dots.tts 的 AR 序列结构可以扩展成**多轨道条件生成**：把两个参考音色都放进 context，模型学习根据角色标记交替生成不同音色的连续帧，一次推理输出多角色音频。

应用：有声书制作、对话 podcast、游戏 NPC 批量配音。

### Feature 3：实时语音风格迁移（Streaming 场景）

dots.tts 是 AR 的，意味着可以**边生成边输出**（streaming TTS）。在 AR 流匹配头的基础上，可以做到：

- 给定参考音色 → 实时合成（首包延迟 < 200ms）
- 中途换参考音色 → 从当前时间点起平滑过渡到新音色
- 根据文本情感分析结果 → 实时调整语速/停顿节奏

这是实时 Agent 语音交互（如 huniu 场景）的关键能力。

### Feature 4：多语言无缝切换（Code-switching TTS）

Qwen2.5-1.5B-Base 本身是强中英双语模型。在此基础上，dots.tts 可以直接处理中英混读文本，不需要检测语言边界、切换模型。

扩展方向：加入更多语言数据（日语、韩语、法语），训练出真正的多语言版本，同一音色说不同语言，音色一致性优于「分语言训练」的方案。

### Feature 5：情感感知 TTS（从对话历史推断情感）

在 Agent 场景里，TTS 的输入通常不只是一句话——还有对话历史上下文。可以扩展 dots.tts 的条件输入，把对话历史编码成额外的 context vector，让模型根据当前对话情绪状态决定语气。

具体实现：在 Qwen2.5 backbone 的输入侧，拼接 `(对话历史摘要向量, 参考音色, 当前文本)` → 生成的语音情感跟上下文匹配，而不是每句话都是相同的中性语气。

### Feature 6：语音记忆和音色库

dots.tts 的零样本克隆只需要 3 秒参考音频。可以构建一个**音色库管理系统**：

- 给每个常用角色/人物存储参考音频（3-10秒）
- 推理时从库里检索，无需每次提供
- 支持多参考融合（如：「60% 音色A + 40% 音色B」，在连续隐空间插值）

这是个工程问题，但 dots.tts 的连续空间特性使得音色插值有数学意义（离散 Token 插值没有语义意义）。

### Feature 7：语音编辑的精准时间定位

dots.tts.edit 目前的粒度是全段编辑。工程扩展方向：**词级别的时间戳定位编辑**——「第 3 到第 7 秒的"真的吗"这句话，让它听起来更惊讶」——只改这段，其余保持不变。

实现思路：把文本对齐（forced alignment）结果作为额外的条件，让编辑头知道哪些音频帧对应哪些词，精准施加编辑 delta。

### Feature 8：与 LLM Agent 的深度集成（端到端语音 Agent）

最后也是最大的方向：**dots.tts 不是一个独立的工具，它是语音 Agent 基础设施的一层**。

在 SGLang Omni 支持下，可以构建：
```
用户说话
  → STT（whisper / FunASR）
  → LLM（Qwen / Claude）
  → dots.tts（连续 AR，首包 < 200ms）
  → 用户听到回复
```

与现有方案的区别：dots.tts 的连续 AR 特性让它可以「边想边说」——LLM 生成文本的同时，TTS 流式合成对应的音频，而不是等全部文本生成完再合成。这把端到端延迟从 3-5 秒压到 1-2 秒以内，是语音 Agent 体验的质变。

---

## 五、局限和开放问题

**韵律控制粒度**：目前通过文字指令控制（dots.tts.edit），但没有显式的韵律符号（停顿标注、重音标注）输入。对于需要精确控制停顿位置的场景（如：广播稿、演讲稿），还需要扩展。

**推理速度**：流匹配头比分类头慢（需要多步 ODE 积分）。MeanFlow 已经是优化过的版本，但在 CPU 或低端 GPU 上的实时性仍需验证。

**数据和训练开销**：连续隐空间的 TTS 训练比离散 Token 路线需要更多计算——量化误差本来是帮助收敛的，去掉它意味着模型需要更精准地学习连续分布。微调自己的音色需要的数据量和计算资源还未有明确文档。

**多说话人可扩展性**：当前版本是零样本克隆（3秒），但是否支持同时建模几百个说话人的「speaker ID embed」模式，文档未明确。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## dots.tts: 2B Fully Continuous Autoregressive TTS — Why No Discrete Tokens, and What New Features This Foundation Enables

*by Mycelium Protocol*

---

GitHub: studio-dots-ai/dots.tts  
Parameters: 2B  
License: Open source  
Collaboration: dots team + X-LANCE Lab, Shanghai Jiao Tong University  
Benchmark: SOTA on Seed-TTS-Eval (2026-08)

---

"Still building on discrete tokens? We took a different path."

That's the self-positioning of dots.tts. The different path: from **discrete acoustic tokens** (VQ-VAE, EnCodec, SoundStream) to **direct generation in the continuous latent space** of an AudioVAE, with an AR flow-matching head (MeanFlow) instead of traditional next-token classification.

---

### Architecture

```
Text + reference audio (3 seconds)
      ↓
Qwen2.5-1.5B-Base (LLM backbone, no chat template)
      ↓
AR flow-matching head (MeanFlow)
      ↓ chunk-by-chunk continuous latent prediction
AudioVAE decoder (48kHz audio)
      ↓
Final audio
```

**AudioVAE**: Compresses 48kHz audio into a continuous low-dimensional latent sequence — no VQ, no quantization step, no information loss from discretization.

**Qwen2.5-1.5B-Base**: The LLM backbone extended with speech modality embeddings and output head. Base model (not Chat) means no RLHF dialog format constraints — more natural autoregressive generation. Also means native Chinese/English bilingual capability.

**MeanFlow (AR Flow-Matching head)**: For each step, models a flow from noise to the target continuous vector, trained to predict the mean trajectory. Faster than DDPM-class methods, more stable than single-step prediction. This is what makes discrete-token classification unnecessary.

---

### 7 Checkpoints and Product Capabilities

dots.tts opens 7 checkpoints covering:
- **dots.tts**: Zero-shot voice cloning TTS (3-second reference audio → matching voice)
- **dots.tts.edit**: Speech editing — given `(audio, text instruction)`, outputs audio with modified emotion/style while preserving the original voice

dots.tts.edit is a separate capability (separate weights). It's not post-processing — it's a model that understands `(audio, instruction)` jointly and outputs modified audio.

**SGLang Omni compatible**: Can be integrated as a component in SGLang's multimodal inference serving.

---

### 8 New Features This Foundation Enables

**1. Fine-grained emotion control via latent interpolation**
Continuous space supports interpolation: "emotion intensity 0.7, conversational feel 0.4" — directly manipulate the latent, not through vague text prompts. Discrete token systems can't do this meaningfully.

**2. Multi-character dialogue audio in one pass**
Extend the AR sequence to be multi-track conditioned: provide two reference voices, the model alternates between them based on speaker tags. One inference pass, multi-character audio, no manual stitching.

**3. Real-time streaming TTS with mid-stream voice switching**
AR generation = streaming output (first packet < 200ms). Enable mid-stream voice transitions: swap reference audio context partway through, model smoothly transitions to the new voice from that point.

**4. Code-switching TTS (Chinese/English/multilingual in one stream)**
Qwen2.5-1.5B-Base is natively bilingual. No language boundary detection needed, no model switching. Extension: add more language training data for a truly multilingual foundation model where voice identity is consistent across languages.

**5. Context-aware emotion inference**
In agent scenarios, the input isn't just one sentence — there's conversation history. Extend the conditioning to include a conversation history embedding: `(history vector, reference voice, current text)` → the synthesized voice's emotion matches the conversation state.

**6. Voice library with latent interpolation**
Zero-shot cloning needs only 3 seconds. Build a voice library where interpolation between voices is mathematically meaningful in continuous space (unlike discrete token "interpolation" which has no semantic validity). "60% voice A + 40% voice B" has a real latent representation.

**7. Word-level timestamp-guided speech editing**
dots.tts.edit currently edits whole segments. Engineering extension: provide forced alignment timestamps as additional conditioning, enabling "edit only the phrase at 3-7 seconds" while keeping the rest unchanged.

**8. End-to-end streaming voice agent**
In SGLang Omni: LLM generates tokens → dots.tts streams synthesis simultaneously → user hears the response while the LLM is still thinking. Reduces end-to-end latency from 3-5 seconds to 1-2 seconds. This is the quality leap for voice agent UX.

---

### Open Questions

- **Prosody control granularity**: Instruction-based control exists (dots.tts.edit), but no explicit pause/stress markup input for precise broadcast-quality control.
- **Inference speed on low-end hardware**: MeanFlow is faster than standard diffusion but still slower than single-step classification. Real-time viability on CPU not yet documented.
- **Fine-tuning data requirements**: Removing quantization means the model must learn more precise continuous distributions — training cost likely higher than discrete-token counterparts.
- **Multi-speaker ID mode**: Zero-shot cloning from 3-second audio is confirmed; whether a speaker-ID embedding mode (hundreds of speakers baked in) is supported is not yet documented.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
