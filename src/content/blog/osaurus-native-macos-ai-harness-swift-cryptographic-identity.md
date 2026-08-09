---
title: "Osaurus：在你的 Mac 上拥有 AI——密码学身份、沙盒 VM、隐私过滤，纯 Swift 原生"
titleEn: "Osaurus: Own Your AI on Mac — Cryptographic Identity, Sandbox VM, Privacy Filter, Pure Swift"
description: "osaurus-ai/osaurus，7295 stars，MIT，纯 Swift 打造的 macOS 原生 AI 哈尼斯。secp256k1 密码学身份、Alpine Linux 沙盒 VM、三层记忆、发送云端前 PII 隐私过滤、Agent 间 E2E 加密通道。模型可换，哈尼斯是复利资产。"
descriptionEn: "osaurus-ai/osaurus, 7,295 stars, MIT. Pure Swift native macOS AI harness. secp256k1 cryptographic identity, Alpine Linux sandbox VM, three-layer memory, on-device PII privacy filter before cloud sends, E2E encrypted agent channels. Models are interchangeable — the harness is what compounds."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI Agent", "开源", "macOS", "Swift", "本地优先", "隐私", "密码学", "MCP"]
heroImage: "../../assets/images/osaurus-native-macos-ai-harness-swift-cryptographic-identity-banner.jpg"
---

> **仓库**：osaurus-ai/osaurus · Swift · MIT · 7295 stars
> **最新版本**：0.22.9（2026-07-23）
> **安装**：`brew install --cask osaurus`（macOS 15.5+，Apple Silicon）

---

## 一、核心命题

Osaurus 的整个设计出发点是一句话：

> "Models are getting cheaper and more interchangeable by the day. What's irreplaceable is the layer around them — your context, your memory, your tools, your identity."

模型正在商品化。真正有复利的，是围绕模型的那一层——你的上下文、记忆、工具、身份。别人把这层放在他们的服务器上。Osaurus 把它放在你的机器上。

这不是一个聊天界面，是一个 **AI 哈尼斯**（harness）：坐在你和任何模型之间，提供让 AI 真正变成"你的 AI"所需的一切——能记住事情、能自主执行、能从任何地方访问的 Agent。

---

## 二、架构：六层哈尼斯

```
┌─────────────────────────────────────────────────────┐
│                   The Harness                       │
├──────────┬──────────┬────────────┬──────────────────┤
│ Agents   │ Memory   │ Agent Loop │ Automation       │
├──────────┴──────────┴────────────┴──────────────────┤
│              MCP Server + Client（双向）             │
├──────────┬──────────┬───────────┬───────────────────┤
│ MLX      │ OpenAI   │ Anthropic │ Ollama / Others   │
│ Runtime  │ API      │ API       │                   │
├──────────┴──────────┴───────────┴───────────────────┤
│      Plugin System (v1/v2/v3 ABI) · 20+ 原生插件   │
├──────────┬──────────┬───────────┬───────────────────┤
│ Identity │ Relay    │ Tools     │ Skills · Methods  │
├──────────┴──────────┴───────────┴───────────────────┤
│  Sandbox VM（Alpine · Apple Containerization）      │
│  vsock bridge · VirtioFS · per-agent 隔离           │
└─────────────────────────────────────────────────────┘
```

纯 Swift，无 Electron。利用 Apple Silicon 的 Neural Engine 和 MLX 框架做本地推理。

---

## 三、密码学身份：每个参与者都是密码学原语

这是 Osaurus 在同类工具里最不寻常的设计之一。

**每个参与者——人、Agent、设备——都有一个 secp256k1 密钥对**（是的，和比特币用的同一条椭圆曲线）。

权限链从你的主密钥（存在 iCloud Keychain）向下分发到每个 Agent：

- 创建可携带的访问密钥（`osk-v1` 格式）
- 精确到 Agent 粒度的权限范围
- 任何时候可撤销

实际影响：
- **Agent 身份**是密码学可验证的，不是"账号系统"
- **Relay 暴露**：每个 Agent 的公网 URL 基于它的密码学地址唯一确定——`agent.osaurus.ai/<crypto-derived-url>`
- **两个 Osaurus Agent 通信**时，连接是 E2E 加密的：X25519 密钥协商 + ChaCha20-Poly1305 加密，每次请求、每个流式 token、每个访问密钥都被密封。Relay 是盲管道，转发的是密文，无法解开。

这套设计在 AI Agent 生态里目前是极少见的——大多数工具的 Agent 之间通信走的是明文 HTTP 或 JWT，而不是前向保密的密码学通道。

---

## 四、沙盒 VM：每个 Agent 有自己的 Linux

在 macOS 26（Tahoe）上，Osaurus 使用 Apple 的 Containerization framework 给每个 Agent 运行一个 Alpine Linux VM：

```
┌──────────────┐       ┌─────────────────────────────┐
│   Osaurus    │       │   Linux VM (Alpine)          │
│              │       │                              │
│  Sandbox Mgr ┼───────┤→ /workspace  (VirtioFS)      │
│  Host API   ←┼─vsock─┤→ osaurus-host bridge         │
│              │       │                              │
│              │       │  agent-alice  (Linux user)   │
│              │       │  agent-bob    (Linux user)   │
└──────────────┘       └─────────────────────────────┘
```

- 每个 Agent 有独立的 Linux 用户和 home 目录
- 完整开发环境：shell、Python、Node.js、编译器、包管理器
- vsock bridge 让沙盒里的 Agent 能回连 Osaurus（推理、记忆、secrets）——隔离但不断网
- macOS 15.x 回退到 macOS Seatbelt sandbox

这意味着：Agent 跑任意代码，不会影响你的 Mac。这在现有的 AI coding 工具里是不常见的硬安全保证。

---

## 五、三层记忆

Osaurus 的记忆系统设计上把"记住什么"和"什么时候注入"分开处理：

**三层**：
1. **身份层**：你是谁、偏好、固定信息
2. **钉固事实**：手动标记的关键知识
3. **会话片段**：过去对话里蒸馏出来的事件

**关键设计**：Agent **只在会话结束时蒸馏一次**，不是每个 turn 都写记忆。后台整合器负责衰减旧记忆、合并相似片段、驱逐不重要的内容——记忆保持精锐而不膨胀。

**注入控制**：每个请求最多注入一个紧凑片段（基于相关性 RAG 搜索），大多数 turn 注入 ≤800 tokens，很多 turn 零注入。

这个设计解决了"长对话记忆膨胀"的问题，代价是实时性（当次会话内写的内容要等会话结束才固化）。

---

## 六、隐私过滤器：发云端之前先过 PII 扫描

当你要发内容给云端模型时，Osaurus 在本地先跑一个分类器：

**`openai/privacy-filter`**（Apache-2.0，1.5B 参数，50M 激活的稀疏 MoE）

检测范围：姓名、邮件、电话、URL、地址、日期、账号，以及 SSN、信用卡、IBAN、AWS key、GitHub token、你自定义的 pattern。

被检测到的实体替换成稳定占位符 `[PERSON_1]`、`[EMAIL_2]`，流式回复时在本地实时还原——对话读起来正常，但云端实际收到的是脱敏版本。

**Fail-closed 设计**：如果脱敏后扫描还发现有遗漏，发送被阻止。Insights 面板显示云端实际收到的字节。

---

## 七、Drop-in API 兼容层

Osaurus 在 `127.0.0.1:1337` 暴露兼容端点：

```
OpenAI    → http://127.0.0.1:1337/v1/chat/completions
Anthropic → http://127.0.0.1:1337/anthropic/v1/messages
Ollama    → http://127.0.0.1:1337/api/chat
```

任何已经用这些 API 的工具，改一个 base URL 就能指向 Osaurus——本地推理、记忆、工具全部接管，上层代码不用改。

---

## 八、支持的模型

**本地（MLX，完全离线）**：Gemma 4、Qwen3.6、GPT-OSS、Llama 等。Osaurus 在 Hugging Face 维护了自己的[优化模型库](https://huggingface.co/OsaurusAI)，针对 Apple Silicon 做了量化。

**Apple Foundation Models**（macOS 26+）：通过 Apple 原生接口，零推理成本，完全私密。

**Liquid AI LFM**：非 Transformer 架构，为边缘部署优化，工具调用性能强。

**云端**：OpenAI、Anthropic、Gemini、xAI/Grok、Venice AI、OpenRouter、Ollama、LM Studio，以及 Osaurus Router（按用量计费，Osaurus 不存储 prompt 内容）。

---

## 九、数字和判断

- 7295 stars，406 forks
- 2025-08-17 创建，约11个月做到版本 0.22.9——迭代节奏每周有发布
- 53 open issues，88 open PRs——社区活跃
- Trendshift 有榜单收录，说明趋势数据被监控工具认可

**判断**：

Osaurus 是目前见过的 AI 工具里，**在安全和隐私工程上走得最深的开源项目之一**。密码学身份（secp256k1）、沙盒 VM（Apple Containerization）、发送前 PII 过滤、Agent 间 E2E 加密通道——这些不是 README 里的市场语言，是有实现的工程选择。

macOS 专属 + 纯 Swift 是有意识的约束：利用 Apple Silicon 的 Neural Engine 和 Metal，换取性能和原生体验，代价是平台锁定。

7295 stars 对一个 macOS-only 原生应用来说很健康。对比跨平台的 Electron 工具，原生 Swift 的受众面天然更窄，但用户黏性和性能上限都更高。

和 OpenWorker（吴恩达，跨平台 Python + Tauri）、Postiz（社媒调度）相比，Osaurus 针对的是**想彻底控制自己的 AI 基础设施的 Mac 用户**——不只是想用 AI，而是想拥有 AI。

---

*数据来源：GitHub osaurus-ai/osaurus，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: osaurus-ai/osaurus · Swift · MIT · 7,295 stars
> **Latest Release**: 0.22.9 (2026-07-23)
> **Install**: `brew install --cask osaurus` (macOS 15.5+, Apple Silicon)

---

## 1. The Core Thesis

Osaurus builds from a single premise:

> "Models are getting cheaper and more interchangeable by the day. What's irreplaceable is the layer around them — your context, your memory, your tools, your identity."

Models are commoditizing. What actually compounds is the layer around them — your context, memory, tools, identity. Others keep that layer on their servers. Osaurus keeps it on your machine.

This isn't a chat interface — it's an **AI harness**: sitting between you and any model, providing everything needed to make AI genuinely *yours* — agents that remember, execute autonomously, and stay reachable from anywhere.

---

## 2. Architecture: Six-Layer Harness

```
┌─────────────────────────────────────────────────────┐
│                   The Harness                       │
├──────────┬──────────┬────────────┬──────────────────┤
│ Agents   │ Memory   │ Agent Loop │ Automation       │
├──────────┴──────────┴────────────┴──────────────────┤
│              MCP Server + Client (bidirectional)    │
├──────────┬──────────┬───────────┬───────────────────┤
│ MLX      │ OpenAI   │ Anthropic │ Ollama / Others   │
│ Runtime  │ API      │ API       │                   │
├──────────┴──────────┴───────────┴───────────────────┤
│      Plugin System (v1/v2/v3 ABI) · 20+ native     │
├──────────┬──────────┬───────────┬───────────────────┤
│ Identity │ Relay    │ Tools     │ Skills · Methods  │
├──────────┴──────────┴───────────┴───────────────────┤
│  Sandbox VM (Alpine · Apple Containerization)       │
│  vsock bridge · VirtioFS · per-agent isolation      │
└─────────────────────────────────────────────────────┘
```

Pure Swift, no Electron. Leverages Apple Silicon's Neural Engine and the MLX framework for local inference.

---

## 3. Cryptographic Identity: Every Participant Is a Cryptographic Primitive

This is one of the most unusual design choices in Osaurus compared to similar tools.

**Every participant — human, agent, device — gets a secp256k1 keypair** (the same elliptic curve Bitcoin uses).

Authority flows from your master key (stored in iCloud Keychain) down to each agent:

- Create portable access keys (`osk-v1` format)
- Permissions scoped to individual agents
- Revocable at any time

The practical implications:
- **Agent identity** is cryptographically verifiable, not an account system
- **Relay exposure**: each agent's public URL is derived from its cryptographic address — `agent.osaurus.ai/<crypto-derived-url>`
- **When two Osaurus agents communicate**, the connection is E2E encrypted: X25519 key exchange + ChaCha20-Poly1305, every request, every streamed token, and every access key sealed. The relay is a blind pipe forwarding ciphertext it cannot open.

This design is rare in the AI agent ecosystem. Most tools' agents communicate over plaintext HTTP or JWTs — not forward-secret cryptographic channels.

---

## 4. Sandbox VM: Each Agent Gets Its Own Linux

On macOS 26 (Tahoe), Osaurus uses Apple's Containerization framework to run an Alpine Linux VM per agent:

```
┌──────────────┐       ┌─────────────────────────────┐
│   Osaurus    │       │   Linux VM (Alpine)          │
│              │       │                              │
│  Sandbox Mgr ┼───────┤→ /workspace  (VirtioFS)      │
│  Host API   ←┼─vsock─┤→ osaurus-host bridge         │
│              │       │                              │
│              │       │  agent-alice  (Linux user)   │
│              │       │  agent-bob    (Linux user)   │
└──────────────┘       └─────────────────────────────┘
```

- Each agent gets its own Linux user and home directory
- Full dev environment: shell, Python, Node.js, compilers, package managers
- vsock bridge lets sandboxed agents call back to Osaurus (inference, memory, secrets) — isolated but not disconnected
- macOS 15.x fallback: macOS Seatbelt sandbox

The upshot: agents run arbitrary code with zero risk to your Mac. This is a hard security guarantee that's uncommon in existing AI coding tools.

---

## 5. Three-Layer Memory

Osaurus separates *what to remember* from *when to inject it*:

**Three layers:**
1. **Identity layer**: who you are, preferences, fixed facts
2. **Pinned facts**: manually marked key knowledge
3. **Session episodes**: events distilled from past conversations

**Key design**: agents distill conversations **once at session end** — not on every turn. A background consolidator decays old memories, merges similar episodes, and evicts low-salience content. Memory stays sharp rather than bloating.

**Injection control**: at most one compact slice per request (RAG-ranked by relevance), most turns inject ≤800 tokens, many inject zero.

This solves the "long-conversation memory bloat" problem at the cost of real-time immediacy — content written within the current session doesn't consolidate until the session ends.

---

## 6. Privacy Filter: PII Scan Before Every Cloud Send

When sending content to a cloud model, Osaurus first runs a local classifier:

**`openai/privacy-filter`** (Apache-2.0, 1.5B params, 50M active sparse-MoE)

Detection scope: names, emails, phones, URLs, addresses, dates, account numbers — plus regex for SSNs, credit cards, IBAN, AWS keys, GitHub tokens, and custom patterns you define.

Detected entities are replaced with stable placeholders `[PERSON_1]`, `[EMAIL_2]`; streaming replies are de-anonymized locally on the fly so the conversation reads naturally, but the cloud received a redacted version.

**Fail-closed design**: if a post-scrub scan finds anything that leaked, the send is blocked. The Insights panel shows the exact bytes the cloud actually saw.

---

## 7. Drop-in API Compatibility Layer

Osaurus exposes compatible endpoints at `127.0.0.1:1337`:

```
OpenAI    → http://127.0.0.1:1337/v1/chat/completions
Anthropic → http://127.0.0.1:1337/anthropic/v1/messages
Ollama    → http://127.0.0.1:1337/api/chat
```

Any existing tool that uses these APIs routes to Osaurus by changing one base URL — local inference, memory, and tools take over, no upstream code changes required.

---

## 8. Supported Models

**Local (MLX, fully offline)**: Gemma 4, Qwen3.6, GPT-OSS, Llama, and more. Osaurus maintains its own [optimized model library on Hugging Face](https://huggingface.co/OsaurusAI) with curated Apple Silicon quantizations.

**Apple Foundation Models** (macOS 26+): via Apple's native interface, zero inference cost, fully private.

**Liquid AI LFM**: non-transformer architecture, edge-optimized, strong tool-calling performance.

**Cloud**: OpenAI, Anthropic, Gemini, xAI/Grok, Venice AI, OpenRouter, Ollama, LM Studio, and Osaurus Router (pay-as-you-go; Osaurus doesn't store prompt content).

---

## 9. Numbers and Assessment

- 7,295 stars, 406 forks
- Created 2025-08-17 — reached v0.22.9 in roughly 11 months, with weekly releases
- 53 open issues, 88 open PRs — active community
- Listed on Trendshift, indicating trend-monitoring tools are tracking it

**Assessment:**

Osaurus is one of the most deeply engineered open-source AI tools on the security and privacy front. Cryptographic identity (secp256k1), sandbox VMs (Apple Containerization), pre-send PII filtering, E2E encrypted agent channels — these aren't marketing language in the README. They're implemented engineering decisions.

macOS-only + pure Swift is a deliberate constraint: it buys performance from Apple Silicon's Neural Engine and Metal, at the cost of platform lock-in.

7,295 stars for a macOS-only native app is healthy. Native Swift naturally has a narrower addressable audience than cross-platform Electron tools, but higher ceiling on performance and user retention.

Compared with OpenWorker (Andrew Ng, cross-platform Python + Tauri) and Postiz (social media scheduling), Osaurus targets **Mac users who want to completely own their AI infrastructure** — not just use AI, but own it.

---

*Data source: GitHub osaurus-ai/osaurus, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
