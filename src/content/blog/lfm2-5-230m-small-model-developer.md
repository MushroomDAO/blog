---
title: "LFM2.5-230M 开发者探索指南：213 tok/s 的小模型，普通人能做什么？"
titleEn: "LFM2.5-230M Developer Guide: What Can You Actually Build with a 213 tok/s Small Model?"
description: "Liquid AI 开源的 LFM2.5-230M 在手机 CPU 上跑出 213 tok/s，Raspberry Pi 上 42 tok/s，支持 32K 上下文和 Tool Use。本文从 6 个方向拆解普通开发者可以用它做什么：端侧 Agent、浏览器推理、Android App、低成本微调、IoT 部署和多 Agent 协作。"
descriptionEn: "Liquid AI's open-source LFM2.5-230M hits 213 tok/s on a phone CPU and 42 tok/s on a Raspberry Pi, with 32K context and Tool Use support. This guide maps 6 concrete directions for individual developers: edge agents, browser inference, Android apps, low-cost fine-tuning, IoT deployment, and multi-agent systems."
pubDate: "2026-06-26"
updatedDate: "2026-06-26"
category: "Tech-News"
tags: ["小模型", "边缘AI", "LFM2.5", "Liquid AI", "端侧推理", "开发者指南"]
heroImage: "../../assets/images/lfm2-5-230m-small-model-developer-banner.jpg"
---

> **一句话结论（BLUF）**：LFM2.5-230M 不是大模型的缩水版，而是为端侧场景专门设计的一类模型——它的价值不在于「能不能替代 GPT-4o」，而在于「能不能在没有 GPU、没有网络、没有云服务账单的地方跑起来」。230M 参数、213 tok/s、32K 上下文，这个组合在 2026 年打开了一批以前不存在的可能性。

模型地址（HuggingFace）：LiquidAI/LFM2.5-230M-Instruct  
社区项目：https://github.com/Jeevav62/pocketlfm · https://github.com/gyunggyung/Tiny-MoA

---

## 一、先搞清楚：这个小模型为什么值得关注？

过去一年，大家的注意力都在大模型的能力竞争上——上下文更长、推理更强、多模态更全。但另一条线同样在悄悄进化：**小模型**。

LFM2.5-230M 是 Liquid AI 最新发布的 LFM2.5 系列里最小的模型，关键参数如下：

| 指标 | 数值 |
|---|---|
| 参数量 | 230M |
| 预训练 Tokens | 19T |
| 上下文窗口 | 32K |
| Galaxy S25 Ultra（仅 CPU）| **213 tok/s** |
| Raspberry Pi 5（仅 CPU）| **42 tok/s** |
| 支持格式 | GGUF（llama.cpp）/ MLX / vLLM+SGLang / ONNX |
| 原生能力 | Agent、Tool Use、Data Extraction |

**213 tok/s 是什么概念？**

人类阅读速度大约是 5-7 tok/s。213 tok/s 意味着在手机上用 CPU 就能实现比阅读速度快 30 倍以上的生成——响应几乎是即时的，完全不需要等待。

更重要的是：**仅 CPU**，不需要 GPU，不需要云服务，不需要网络。

### 为什么 Liquid AI 的架构特别适合小模型？

LFM（Liquid Foundation Model）采用混合架构——线性递归层 + 选择性注意力机制，而不是纯 Transformer。这个设计的关键优势：

- **线性时间复杂度**：处理长上下文时不会像标准 Attention 一样 O(n²) 爆炸；
- **内存效率更高**：在相同参数量下，能处理更长的上下文；
- **CPU 友好**：线性操作对 CPU 比 Attention 矩阵乘法更友好。

这解释了为什么 230M 参数的小模型能在 CPU 上跑出 213 tok/s，同时支持 32K 上下文——这在纯 Transformer 小模型里几乎不可能同时做到。

---

## 二、普通开发者能做什么？6 个探索方向

### 方向 1：树莓派 / 旧笔记本上的本地 Agent

**为什么值得做：** 42 tok/s 在 Raspberry Pi 5 上——这是第一次，一个真正能用的 AI Agent 可以在 35 美元的单板计算机上运行。

**适合的场景：**
- 家庭自动化 Agent（控制 Home Assistant、读取传感器、执行脚本）
- 本地网络监控 + 异常报警
- 离线文档摘要和提取（不上传到云端）
- 低功耗服务器上的自动化任务

**怎么开始：**

```bash
# 安装 llama.cpp（Raspberry Pi 4/5 都支持 ARM64）
pip install llama-cpp-python

# 下载 GGUF 模型（Q4_K_M 约 150MB）
huggingface-cli download LiquidAI/LFM2.5-230M-Instruct-GGUF \
  --include "*Q4_K_M.gguf" --local-dir ./models

# 用 Python 跑 Tool Use
from llama_cpp import Llama
llm = Llama(model_path="./models/LFM2.5-230M-Instruct-Q4_K_M.gguf",
            n_ctx=4096, n_threads=4)

tools = [{
    "type": "function",
    "function": {
        "name": "get_temperature",
        "description": "读取当前室内温度",
        "parameters": {"type": "object", "properties": {}}
    }
}]

response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "现在室内温度多少？"}],
    tools=tools
)
```

**关键点：** 230M 的 Tool Use 能力有限，适合单工具、单步任务。不要期望它能规划复杂的多步 Agent 链——那是 1.2B 以上模型的地盘。

---

### 方向 2：浏览器里跑 AI，零服务器成本

**为什么值得做：** ONNX + Transformers.js 让模型直接在浏览器里运行，用户下载一次模型（约 150-200MB），之后所有推理在本地完成——无服务器、无 API 费用、无隐私问题。

已经有人做了：`sitammeur/lfm2.5-thinking-web`——用 React + Transformers.js + ONNX Runtime Web（WebGPU 加速），把 LFM2.5-1.2B-Thinking 直接跑在浏览器里。230M 版本会更小、更快。

**适合的场景：**
- 给工具网站加 AI 功能（写作助手、数据提取、格式转换）
- 离线优先的 PWA 应用（飞机上也能用的 AI 工具）
- 隐私敏感场景（法律、医疗、个人日记）

**怎么开始：**

```javascript
import { pipeline } from '@huggingface/transformers';

// 浏览器里加载模型（首次下载后缓存）
const generator = await pipeline(
  'text-generation',
  'LiquidAI/LFM2.5-230M-Instruct-ONNX',
  { device: 'webgpu' }  // 有 GPU 用 GPU，没有降级到 wasm
);

const result = await generator(
  '<|im_start|>user\n帮我提取这段文字中的关键数据<|im_end|>\n<|im_start|>assistant\n',
  { max_new_tokens: 200 }
);
```

**注意：** LFM2.5 使用 ChatML 格式（`<|im_start|>` / `<|im_end|>`），这是标准格式，Transformers.js 完全支持。

---

### 方向 3：Android 离线 AI App

**为什么值得做：** 现有参考实现 `Jeevav62/pocketlfm` 已经证明了可行性——llama.cpp + Android NDK，在手机上完全离线运行 LFM2.5-1.2B（750MB Q4_K_M），230M 版本会更轻量（约 150MB）。

**适合的场景：**
- 个人助手 App（不上传对话到任何服务器）
- 字段提取工具（名片扫描、收据识别后提取结构化数据）
- 离线翻译 / 摘要
- 低功耗设备上的专用工具（物流扫描枪、工业 PDA）

**技术路径：**

```kotlin
// Kotlin + llama.cpp (NDK)
// 参考 pocketlfm 的架构：
// 1. ModelDownloader.kt - 首次下载 GGUF
// 2. LlamaContext.kt - JNI 桥接 llama.cpp
// 3. ChatViewModel.kt - 管理会话状态
// 4. ChatML 模板：
fun buildPrompt(messages: List<Message>): String {
    return messages.joinToString("") { msg ->
        "<|im_start|>${msg.role}\n${msg.content}<|im_end|>\n"
    } + "<|im_start|>assistant\n"
}
```

**最省力的起点：** Fork `Jeevav62/pocketlfm`，把模型 URL 换成 230M 的 GGUF，在 `ModelDownloader.kt` 改一行就能跑 230M 版本。

---

### 方向 4：低成本微调，定制专属助手

**为什么值得做：** `benitomartin/grumpy-chef-finetuning-dpo` 已经完整演示了流程：用 Unsloth + QLoRA，在 1.2B 基座上做 SFT + DPO，只需要 300 个样本，可训练参数仅 1.86%（22.2M / 1.19B）。230M 版本资源需求更低——本地 RTX 4060 就能跑完整个微调流程。

**什么时候应该微调：**
- 你有专业领域数据（法律条文、医疗术语、客服对话）
- 你需要特定的输出格式（JSON 提取、固定模板）
- 你想给模型注入特定的「人格」或「角色」

**微调流程：**

```python
from unsloth import FastLanguageModel

# 加载基座模型（QLoRA 4-bit，节省显存）
model, tokenizer = FastLanguageModel.from_pretrained(
    "LiquidAI/LFM2.5-230M-Base",
    max_seq_length=2048,
    load_in_4bit=True,
)

# 添加 LoRA 适配器（r=16 对 230M 够用）
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=32,
    lora_dropout=0.05,
)

# SFT 训练（300+ 样本即可有效果）
from trl import SFTTrainer
trainer = SFTTrainer(model=model, tokenizer=tokenizer, ...)
trainer.train()
```

**成本估算：** 230M + 300 样本 + Colab T4 GPU = 大约 1-2 小时训练时间，免费额度内可以完成。本地 RTX 4060 更快。

**导出用于生产：**

```bash
# 导出 GGUF，放到手机 / Pi / Ollama 上跑
python -m llama_cpp.server --model fine-tuned-model.gguf
# 或者
ollama create my-custom-assistant -f Modelfile
```

---

### 方向 5：IoT 和嵌入式场景——真正的端侧 AI

**为什么值得做：** 这是 230M 最有想象力的方向。Raspberry Pi 5 上 42 tok/s，意味着一个回复（100 tokens）只需要 2.4 秒——对于 IoT 场景，这完全可以接受。

**具体应用场景：**

**智能家居 NLP 接口**：接入家庭传感器数据，用自然语言查询和控制：
```
用户："卧室温度多少？" 
→ LFM2.5-230M 解析意图 → 调用 Tool 读传感器 → 返回结果
```

**工业质检**：配合摄像头，对检测到的异常用 LFM2.5-VL 描述，230M Text 做结构化数据提取：
```
图像检测 → VL 模型描述缺陷 → 230M 提取结构化报告 → 写入数据库
```

**离线日志分析**：在无网络环境（工厂、矿山、海上平台）实时分析日志，生成摘要和告警：
```bash
# 持续读取日志，异常时用 AI 生成摘要
tail -f /var/log/system.log | python3 analyze_with_lfm.py
```

**关键优势：** 整个推理链路不依赖网络，适合安全隔离环境。

---

### 方向 6：多小模型协作——Tiny MoA

**为什么值得做：** `gyunggyung/Tiny-MoA` 展示了一个有趣思路：用 LFM2.5-1.2B-Thinking 做「大脑」（规划），600M Reasoner 做推理，90M Tool Caller 做工具调用，三个小模型协作，全程 CPU，16GB RAM 就够。

230M 版本可以承担更轻量的角色：高速工具路由、数据提取、格式转换，把推理留给稍大的模型。

**协作架构：**

```
用户请求
   ↓
[LFM2.5-230M] 任务路由器
  ├── 简单问答 → 直接回答（230M 独立处理）
  ├── 复杂推理 → 传给 1.2B 模型
  ├── 工具调用 → 解析 Tool 参数 → 执行 → 返回结果
  └── 数据提取 → 结构化输出（230M 最擅长）
```

**为什么 230M 适合做路由器：** 速度极快（213 tok/s），可以快速判断请求类型，把计算资源按需分配，整体延迟更低。

---

## 三、不要踩的坑：230M 的边界

小模型有其能力边界，清晰认识边界比盲目尝试重要：

| 场景 | 230M 适合吗？ | 说明 |
|---|---|---|
| 单步 Tool Use | ✅ 适合 | 调用 1-2 个工具，提取参数 |
| 数据结构化提取 | ✅ 非常适合 | JSON 输出、字段提取 |
| 文本分类 / 路由 | ✅ 非常适合 | 速度快、成本低 |
| 摘要（短文本）| ✅ 适合 | 500 字以内效果好 |
| 复杂多步推理 | ❌ 不适合 | 用 1.2B 或更大模型 |
| 代码生成 | ⚠️ 有限 | 短代码片段可以，复杂逻辑不行 |
| 长文档摘要 | ⚠️ 有限 | 上下文有限时可以，但质量不及大模型 |
| 创意写作 | ❌ 不适合 | 生成质量有明显差距 |

**黄金定律：** 230M 做的是「快速、准确地完成一个明确任务」，不是「理解和推理复杂情境」。把它放在流水线的对的位置，效果非常好；放错位置，会让你失望。

---

## 四、上手路径推荐

根据你的技术背景选起点：

**0 代码门槛：** 用 Ollama 拉模型，本地聊天  
```bash
ollama run hf.co/LiquidAI/LFM2.5-230M-Instruct-GGUF:Q4_K_M
```

**Python 开发者：** llama-cpp-python + Tool Use，做本地 Agent  
**Web 开发者：** Transformers.js + ONNX，做浏览器 AI 工具  
**Android 开发者：** Fork pocketlfm，改模型 URL，出自己的 App  
**嵌入式/IoT：** Raspberry Pi 5 + llama.cpp，做离线端侧 Agent  
**ML 开发者：** Unsloth + QLoRA 微调，定制专属模型  

---

## FAQ

**Q：230M 真的能用吗？还是只是噱头？**  
对于结构化提取、工具路由、快速分类这类任务，230M 是完全够用的。如果你期望它有 GPT-4o 的推理能力，那确实不行。定位清楚，用处很大。

**Q：和 Phi-3-mini / Gemma-2B 比怎么样？**  
Phi-3-mini 参数更多（3.8B）；Gemma-2B 参数多 9 倍。比较的维度不同：LFM2.5-230M 胜在 CPU 推理速度和端侧效率，而不是在比参数量谁更大。

**Q：Apple Silicon（Mac）上怎么跑？**  
用 MLX 框架：
```bash
pip install mlx-lm
mlx_lm.generate --model LiquidAI/LFM2.5-230M-Instruct-mlx --prompt "你好"
```
MLX 利用 Apple Silicon 的统一内存架构，速度比 llama.cpp 更快。

**Q：微调需要多少数据？**  
垂直领域任务（提取、分类）100-300 样本可以看到明显效果；角色/风格微调 200-500 样本；更复杂的知识注入需要 1000+。

**Q：GGUF 各种量化版本怎么选？**  
- Q4_K_M：推荐，质量/速度最平衡（约 150MB）
- Q8_0：质量最好，体积约 230MB
- Q2_K：体积最小（80MB），质量下降明显，慎用

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: LFM2.5-230M is not a shrunken large model — it's a model purpose-built for edge scenarios. Its value isn't "can it replace GPT-4o?" but "can it run without a GPU, without a network connection, without a cloud bill?" 230M parameters, 213 tok/s on a phone CPU, 32K context — this combination opens a category of possibilities that didn't exist before.

Model: LiquidAI/LFM2.5-230M-Instruct (HuggingFace)  
Community projects: https://github.com/Jeevav62/pocketlfm · https://github.com/gyunggyung/Tiny-MoA

---

## Why Does This Small Model Actually Matter?

LFM2.5-230M is the smallest model in Liquid AI's LFM2.5 family. Key numbers:

| Metric | Value |
|---|---|
| Parameters | 230M |
| Pretrain Tokens | 19T |
| Context Window | 32K |
| Galaxy S25 Ultra (CPU only) | **213 tok/s** |
| Raspberry Pi 5 (CPU only) | **42 tok/s** |
| Supported Formats | GGUF / MLX / vLLM+SGLang / ONNX |
| Native Capabilities | Agent, Tool Use, Data Extraction |

**What does 213 tok/s mean in practice?**

Human reading speed is roughly 5-7 tok/s. 213 tok/s means generating a 100-token reply in under half a second on a phone CPU — effectively instant, no cloud, no network required.

### Why the LFM Architecture Suits Small Models

LFM (Liquid Foundation Model) uses a hybrid architecture — linear recurrence layers + selective attention — rather than pure Transformer. Key advantages:

- **Linear time complexity** for long contexts, no O(n²) attention explosion
- **Higher memory efficiency** at the same parameter count
- **CPU-friendly** linear operations outperform attention matrix multiplications on CPU

This is why a 230M model hits 213 tok/s on CPU while supporting 32K context — nearly impossible with a pure Transformer at the same scale.

---

## 6 Concrete Directions for Developers

### Direction 1: Local Agent on Raspberry Pi or Old Laptop

42 tok/s on a Raspberry Pi 5 — for the first time, a genuinely useful AI agent can run on a $35 single-board computer.

**Good use cases:** home automation agents (Home Assistant + sensors + scripts), local network monitoring, offline document extraction, low-power server automation.

```bash
pip install llama-cpp-python

# Download GGUF (~150MB Q4_K_M)
huggingface-cli download LiquidAI/LFM2.5-230M-Instruct-GGUF \
  --include "*Q4_K_M.gguf" --local-dir ./models
```

```python
from llama_cpp import Llama
llm = Llama(model_path="./models/LFM2.5-230M-Instruct-Q4_K_M.gguf",
            n_ctx=4096, n_threads=4)

tools = [{"type": "function", "function": {
    "name": "read_temperature", "description": "Read current room temperature",
    "parameters": {"type": "object", "properties": {}}
}}]
response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "What's the current temperature?"}],
    tools=tools
)
```

**Key constraint:** 230M Tool Use works for single-tool, single-step tasks. Don't expect complex multi-step planning — that's 1.2B+ territory.

---

### Direction 2: Browser AI with Zero Server Cost

ONNX + Transformers.js lets models run directly in the browser. The user downloads the model once (~150-200MB), then all inference runs locally — no server, no API fees, no privacy risk.

Reference: `sitammeur/lfm2.5-thinking-web` does this with LFM2.5-1.2B-Thinking. The 230M version will be significantly lighter and faster.

```javascript
import { pipeline } from '@huggingface/transformers';

const generator = await pipeline(
  'text-generation',
  'LiquidAI/LFM2.5-230M-Instruct-ONNX',
  { device: 'webgpu' }  // falls back to wasm if no WebGPU
);

// LFM2.5 uses ChatML format
const result = await generator(
  '<|im_start|>user\nExtract the key data from this text<|im_end|>\n<|im_start|>assistant\n',
  { max_new_tokens: 200 }
);
```

**Best for:** Adding AI features to tools sites, offline-first PWAs, privacy-sensitive applications.

---

### Direction 3: Offline Android App

`Jeevav62/pocketlfm` proves the feasibility — llama.cpp + Android NDK, running LFM2.5-1.2B (750MB GGUF) fully on-device. The 230M version drops to ~150MB.

**Fastest start:** Fork `pocketlfm`, change the model URL in `ModelDownloader.kt` to the 230M GGUF, and you have a running 230M app with one line changed.

```kotlin
// ModelDownloader.kt - change this one constant
const val DEFAULT_MODEL_URL = 
    "https://huggingface.co/LiquidAI/LFM2.5-230M-Instruct-GGUF/resolve/main/LFM2.5-230M-Instruct-Q4_K_M.gguf"

// ChatML prompt template (unchanged — same format as 1.2B)
fun buildPrompt(messages: List<Message>): String {
    return messages.joinToString("") {
        "<|im_start|>${it.role}\n${it.content}<|im_end|>\n"
    } + "<|im_start|>assistant\n"
}
```

---

### Direction 4: Low-Cost Fine-Tuning for a Specialized Assistant

`benitomartin/grumpy-chef-finetuning-dpo` demonstrates the full pipeline: Unsloth + QLoRA, SFT + DPO on LFM2.5-1.2B-Base, 300 samples, only 1.86% trainable parameters. With 230M, the resource requirements drop further — a local RTX 4060 can handle the full training run.

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "LiquidAI/LFM2.5-230M-Base",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model, r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=32,
)
```

**Cost estimate:** 230M + 300 samples + Colab T4 = 1-2 hours, within free tier. Locally on an RTX 4060, faster.

**When to fine-tune:** specialized domain data (legal, medical, customer service), specific output formats (JSON extraction, fixed templates), or embedding a particular persona or role.

---

### Direction 5: IoT and Embedded AI

42 tok/s on Raspberry Pi 5 means a 100-token reply in 2.4 seconds — acceptable for IoT use cases. More importantly: no network dependency, suitable for air-gapped environments.

**Concrete examples:**

Smart home NLP interface — connect sensor data, query and control with natural language:
```
User: "What's the bedroom temperature?" 
→ LFM2.5-230M parses intent → calls Tool → reads sensor → returns result
```

Offline log analysis — real-time analysis without cloud in factories, mines, or offshore platforms:
```bash
tail -f /var/log/system.log | python3 analyze_with_lfm.py
```

Industrial data extraction — structured JSON from unstructured sensor or inspection reports.

---

### Direction 6: Tiny Multi-Agent Collaboration

`gyunggyung/Tiny-MoA` shows an interesting pattern: LFM2.5-1.2B-Thinking as the "brain" (planning), 600M Reasoner for reasoning, 90M Tool Caller for tool dispatch — three small models collaborating, CPU-only, 16GB RAM.

The 230M model is a natural fit for fast task routing and data extraction in a multi-agent pipeline:

```
User request
   ↓
[LFM2.5-230M] Task Router (fast, cheap)
  ├── Simple Q&A → answer directly (230M handles it)
  ├── Complex reasoning → delegate to 1.2B model
  ├── Tool call → parse parameters → execute → return
  └── Data extraction → structured JSON output
```

The 230M's speed (213 tok/s) makes it ideal as a router — it classifies requests in milliseconds and distributes compute resources accordingly.

---

## What 230M Can't Do: Know the Limits

| Task | 230M? | Notes |
|---|---|---|
| Single-step Tool Use | ✅ Yes | 1-2 tools, parameter extraction |
| Structured data extraction | ✅ Excellent | JSON output, field extraction |
| Text classification / routing | ✅ Excellent | Fast, low cost |
| Short-text summarization | ✅ Yes | Good under 500 words |
| Complex multi-step reasoning | ❌ No | Use 1.2B+ |
| Code generation | ⚠️ Limited | Short snippets only |
| Long-document summarization | ⚠️ Limited | Quality gap vs larger models |
| Creative writing | ❌ No | Noticeable quality drop |

**The rule:** 230M does "quickly and accurately complete one well-defined task." It doesn't "understand and reason about complex situations." Put it in the right position in a pipeline and it performs very well. Wrong position, and you'll be disappointed.

---

## Quick Start by Background

**Zero code:** `ollama run hf.co/LiquidAI/LFM2.5-230M-Instruct-GGUF:Q4_K_M`  
**Python developer:** llama-cpp-python + Tool Use → local agent  
**Web developer:** Transformers.js + ONNX → browser AI tool  
**Android developer:** Fork pocketlfm, change model URL  
**Embedded/IoT:** Raspberry Pi 5 + llama.cpp → offline edge agent  
**ML developer:** Unsloth + QLoRA fine-tuning → custom model  
**Apple Silicon:** `mlx_lm.generate --model LiquidAI/LFM2.5-230M-Instruct-mlx`

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
