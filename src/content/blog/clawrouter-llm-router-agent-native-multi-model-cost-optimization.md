---
title: "ClawRouter：专为 AI Agent 设计的 LLM 路由框架，55+ 模型、92% 省钱、<1ms 本地决策"
titleEn: "ClawRouter: Agent-Native LLM Router — 55+ Models, 92% Cost Savings, <1ms Local Routing"
description: "BlockRunAI/ClawRouter，6673 stars，MIT，TypeScript。专为自主 AI Agent 构建的智能 LLM 路由器：钱包签名代替 API key，USDC 微支付代替信用卡，15维度本地评分在 <1ms 内选出最便宜的足够好的模型。8个永久免费模型，混合均价 $2.05/M（vs Claude Opus $25/M），节省92%。"
descriptionEn: "BlockRunAI/ClawRouter, 6,673 stars, MIT, TypeScript. An intelligent LLM router built for autonomous AI agents: wallet signatures instead of API keys, USDC micropayments instead of credit cards, 15-dimension local scoring picks the cheapest capable model in <1ms. 8 forever-free models, blended average $2.05/M vs $25/M for Claude Opus — 92% savings."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI Agent", "LLM路由", "开源", "成本优化", "多模型", "Web3", "USDC", "TypeScript", "工具"]
heroImage: "../../assets/images/clawrouter-llm-router-agent-native-multi-model-cost-optimization-banner.jpg"
---

> **仓库**：BlockRunAI/ClawRouter · TypeScript · MIT · 6673 stars
> **获奖**：USDC Hackathon — Agentic Commerce Winner
> **npm**：`@blockrun/clawrouter` · **官网**：blockrun.ai

---

## 一、从一个问题出发

现有的 LLM 路由工具——OpenRouter、LiteLLM、Martian、Portkey——都是为**人类开发者**设计的：注册账号、生成 API key、绑信用卡、在仪表板里手选模型。

这套流程，AI Agent 一步都做不到。

ClawRouter 的出发点就是这一句话：

> "Agents can't sign up for accounts. Agents can't enter credit cards. Agents can only sign transactions."

---

## 二、它做了什么

ClawRouter 是一个本地运行的 LLM 代理路由器。你启动它之后，它在 `localhost:8402` 开一个 OpenAI 兼容的端点，任何工具只要把 API 地址指向这里，就能无感接入 55+ 个模型，路由逻辑全部在本地执行，不到 1ms 出结果。

和同类工具相比，它同时达成了五个条件——目前只有它一家：

| | OpenRouter | LiteLLM | Martian | Portkey | **ClawRouter** |
|--|-----------|---------|---------|---------|----------------|
| 开源 | ✗ | ✓ | ✗ | 部分 | **✓** |
| 智能路由 | 手动选 | 手动选 | 智能（闭源）| 观测 | **智能（开源）** |
| 本地运行 | ✗ | ✓ | ✗ | ✗ | **✓** |
| 加密原生 | ✗ | ✗ | ✗ | ✗ | **✓** |
| Agent 就绪 | ✗ | ✗ | ✗ | ✗ | **✓** |

---

## 三、路由机制：15维评分，四级分层

每个请求进来，路由引擎在本地对其做 **15 个维度的评分**（不调用任何外部 API），给请求打一个复杂度标签，然后选出那个层级里最便宜的可用模型。

四个复杂度层级 × 三种路由策略：

| 层级 | ECO（最省钱）| AUTO（默认）| PREMIUM（最高质量）|
|------|------------|------------|-----------------|
| **SIMPLE** | free/mistral-large-3-675b（**免费**）| gemini-2.5-flash | kimi-k2.7 |
| **MEDIUM** | gemini-3.1-flash-lite（$0.25/$1.50）| kimi-k2.7（$0.95/$4.00）| gpt-5.3-codex |
| **COMPLEX** | gemini-3.1-flash-lite | gemini-3.1-pro（$2/$12）| claude-opus-4.8 |
| **REASONING** | deepseek-reasoner（$0.20/$0.40）| deepseek-reasoner | claude-sonnet-4.6 |

价格：千 token 输入/输出，单位美元。

**效果**：混合均价 **$2.05/M tokens**，对比 Claude Opus 4.8 的 $25/M，节省 **92%**。

路由策略用 `/model` 命令切换：

```bash
/model free       # 全部走免费模型，$0
/model auto       # 默认，平衡质量与成本（省74-100%）
/model eco        # 最省钱（省95-100%）
/model premium    # 最高质量，不省钱
```

也可以直接钉死某个模型：`/model grok`、`/model br-sonnet`、`/model claude-opus`。

---

## 四、Agent 原生设计：三个关键

### 4.1 免注册，钱包就是身份

首次运行时，ClawRouter 本地生成一个钱包。这个钱包地址就是你的身份，不需要邮箱、不需要密码、没有账号系统。Agent 程序可以持有这个钱包，像签交易一样"登录"。

```bash
npx @blockrun/clawrouter
# 首次运行打印钱包地址，也是你的认证凭证
```

### 4.2 USDC 微支付，x402 协议

付费模型的计费走 [x402 协议](https://x402.org)——HTTP 请求本身携带 USDC 支付指令，在 Base 或 Solana 上结算。Agent 无需预先绑定信用卡，只要钱包里有 USDC，每次调用自动扣费，精确到 token 级别。

充值 $5 可以跑几千次请求。8 个免费模型完全不需要充值。

### 4.3 8 个永久免费模型，无需注册

免费层包含真正有竞争力的模型：

- Mistral Large 3（**675B 参数**）
- Qwen3-Next 80B（**262K 上下文**）
- Nemotron Omni（**支持视觉**）
- 以及另外 5 个 NVIDIA 托管模型

这个层级不需要任何余额、不需要注册，`npx @blockrun/clawrouter` 一条命令就能跑起来。

---

## 五、接入两分钟

### 选项 A：独立代理（continue.dev / Cursor / 任何 OpenAI 兼容客户端）

```bash
# 启动本地代理
npx @blockrun/clawrouter
```

代理起在 `http://localhost:8402`，用任何 OpenAI SDK 指向它：

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8402", api_key="x402")
response = client.chat.completions.create(
    model="blockrun/auto",   # 智能路由
    messages=[{"role": "user", "content": "你好"}]
)
```

continue.dev 配置（`~/.continue/config.yaml`）：

```yaml
models:
  - name: ClawRouter Auto
    provider: openai
    model: blockrun/auto
    apiBase: http://localhost:8402/v1/   # 注意末尾斜杠
    apiKey: x402
```

Cursor：设置 → Models → OpenAI-compatible，base URL 填 `http://localhost:8402`，API key 填 `x402`，model 填 `blockrun/auto`。

### 选项 B：OpenClaw Agent 插件（一行命令）

```bash
curl -fsSL https://blockrun.ai/ClawRouter-update | bash
openclaw gateway restart
```

安装脚本处理全部配置：注册插件、同步模型列表、写认证文件、初始化钱包。完成后 `blockrun/auto` 成为默认模型。

---

## 六、不只是文本路由

ClawRouter 还把图像、视频、语音电话都路由了进来：

**图像生成**（`/cr-imagegen`）

```
/cr-imagegen a misty mountain at dawn
/cr-imagegen --model banana-pro --size 4096x4096 abstract geometric art
```

| 模型 | 提供商 | 价格 | 最大分辨率 |
|------|--------|------|-----------|
| nano-banana | Google Gemini Flash | $0.05/张 | 1024×1024 |
| banana-pro | Google Gemini Pro | $0.10/张 | 4096×4096 |
| gpt-image-2 | OpenAI | $0.06/张 | 1536×1024 |
| seedream | ByteDance | $0.045/张 | 2848×1600 |
| zai/cogview-4 | Zhipu | $0.015/张 | 1440×1440 |

**视频生成**（`/videogen`）

```
/videogen --model seedance-2-fast --duration=5 a cat waving
```

支持 Seedance 2（ByteDance）、Sora 2（Azure）、Grok Video，5秒视频约 $0.42-$1.49。

**AI 电话**（`/cr-call`）

```
/cr-call +14155552671 "Hi, calling to confirm tomorrow's 3pm meeting"
```

Bland.ai 支持，$0.54 固定费用，支持最长 30 分钟，支持转录和录音。

---

## 七、与其他路由器的本质区别

ClawRouter 之前，"智能路由"的意思是：你在仪表板里配规则，平台帮你调 API。路由逻辑在对方服务器上跑，每次路由决策要走一次网络。

ClawRouter 的路由是**完全本地**的：

```
Request → 本地 15维评分器 → Tier → 最优模型 → 直接转发
         （不到1ms，无外部依赖）
```

没有中间服务器知道你在用什么模型、问了什么问题。

对 Agent 系统来说这很重要：Agent 需要高频调用 LLM，路由延迟如果是 50-100ms，在一个多步 Agent 里会累积成秒级延迟。<1ms 的本地路由把这个成本消除了。

---

## 八、适合什么场景

**直接适合**：
- 有多步 AI Agent，每步的任务复杂度差异大（写摘要 vs 代码推理）
- 跑大量 LLM 请求，想在不降低效果的前提下控制成本
- 想让 Agent 在没有人工干预的情况下自主管理 LLM 调用
- 需要接入多个模型提供商，不想维护多套 SDK

**需要额外考虑**：
- 15维本地评分是静态规则，不如端到端训练的路由模型那么精准（Martian 宣称的那种）
- 免费模型质量参差，关键任务建议用 `/model premium`
- x402 + USDC 是加密支付，对不接触 Web3 的团队有上手成本
- 视频/电话这些能力是按量付费的，需要提前预估成本

---

*数据来源：GitHub BlockRunAI/ClawRouter，2026-07-24 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: BlockRunAI/ClawRouter · TypeScript · MIT · 6,673 stars
> **Award**: USDC Hackathon — Agentic Commerce Winner
> **npm**: `@blockrun/clawrouter` · **Homepage**: blockrun.ai

---

## 1. Starting from a Problem

Every existing LLM routing tool — OpenRouter, LiteLLM, Martian, Portkey — was designed for **human developers**: sign up for an account, generate an API key, enter a credit card, and pick a model from a dashboard.

AI agents can't do any of that.

ClawRouter opens with exactly this premise:

> "Agents can't sign up for accounts. Agents can't enter credit cards. Agents can only sign transactions."

---

## 2. What It Does

ClawRouter is a locally-running LLM proxy router. Once started, it opens an OpenAI-compatible endpoint at `localhost:8402`. Any tool that points its API address here gets transparent access to 55+ models — all routing logic runs locally in under 1ms, with zero external API calls.

Compared to alternatives, it's the only one that simultaneously checks all five boxes:

| | OpenRouter | LiteLLM | Martian | Portkey | **ClawRouter** |
|--|-----------|---------|---------|---------|----------------|
| Open source | ✗ | ✓ | ✗ | Partial | **✓** |
| Smart routing | Manual | Manual | Smart (closed) | Observability | **Smart (open source)** |
| Runs locally | ✗ | ✓ | ✗ | ✗ | **✓** |
| Crypto native | ✗ | ✗ | ✗ | ✗ | **✓** |
| Agent ready | ✗ | ✗ | ✗ | ✗ | **✓** |

---

## 3. How Routing Works: 15 Dimensions, 4 Tiers

When a request comes in, the routing engine evaluates it across **15 dimensions locally** (no external API calls), assigns a complexity tier, then picks the cheapest capable model for that tier.

Four complexity tiers × three routing strategies:

| Tier | ECO (cheapest) | AUTO (default) | PREMIUM (best quality) |
|------|---------------|----------------|----------------------|
| **SIMPLE** | free/mistral-large-3-675b (**FREE**) | gemini-2.5-flash | kimi-k2.7 |
| **MEDIUM** | gemini-3.1-flash-lite ($0.25/$1.50) | kimi-k2.7 ($0.95/$4.00) | gpt-5.3-codex |
| **COMPLEX** | gemini-3.1-flash-lite | gemini-3.1-pro ($2/$12) | claude-opus-4.8 |
| **REASONING** | deepseek-reasoner ($0.20/$0.40) | deepseek-reasoner | claude-sonnet-4.6 |

Prices: per million input/output tokens in USD.

**Net result**: blended average **$2.05/M tokens** vs Claude Opus 4.8 at $25/M — **92% savings**.

Switch strategies with `/model`:

```bash
/model free       # free models only, $0
/model auto       # default — balanced quality and cost (74–100% savings)
/model eco        # maximum savings (95–100%)
/model premium    # best quality, no savings
```

Pin a specific model: `/model grok`, `/model br-sonnet`, `/model claude-opus`.

---

## 4. Agent-Native Design: Three Core Properties

### 4.1 No signup — your wallet is your identity

On first run, ClawRouter generates a wallet locally. That wallet address is your identity — no email, no password, no account system. An agent program can hold this wallet and "authenticate" by signing transactions, exactly as it would with any blockchain operation.

```bash
npx @blockrun/clawrouter
# First run prints your wallet address — your auth credential
```

### 4.2 USDC micropayments via x402

Paid model billing runs through the [x402 protocol](https://x402.org) — HTTP requests carry USDC payment instructions, settling on Base or Solana. No credit card needs to be pre-linked. Agents deduct automatically per request, to the token level.

$5 of USDC covers thousands of requests. The 8 free models require zero balance.

### 4.3 8 forever-free models — no signup required

The free tier includes genuinely capable models:

- Mistral Large 3 (**675B parameters**)
- Qwen3-Next 80B (**262K context**)
- Nemotron Omni (**vision-capable**)
- 5 additional NVIDIA-hosted models

No balance needed, no registration — `npx @blockrun/clawrouter` is the entire setup.

---

## 5. Two-Minute Setup

### Option A: Standalone proxy (continue.dev / Cursor / any OpenAI-compatible client)

```bash
# Start the local proxy
npx @blockrun/clawrouter
```

Proxy runs at `http://localhost:8402`. Point any OpenAI SDK at it:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8402", api_key="x402")
response = client.chat.completions.create(
    model="blockrun/auto",
    messages=[{"role": "user", "content": "Hello"}]
)
```

continue.dev config (`~/.continue/config.yaml`):

```yaml
models:
  - name: ClawRouter Auto
    provider: openai
    model: blockrun/auto
    apiBase: http://localhost:8402/v1/   # trailing slash required
    apiKey: x402
```

Cursor: Settings → Models → OpenAI-compatible, base URL: `http://localhost:8402`, API key: `x402`, model: `blockrun/auto`.

### Option B: OpenClaw Agent plugin (single command)

```bash
curl -fsSL https://blockrun.ai/ClawRouter-update | bash
openclaw gateway restart
```

The script handles everything: plugin registration, model list sync, auth profile, wallet initialization. After completion, `blockrun/auto` becomes your default model.

---

## 6. Beyond Text: Images, Video, Voice

ClawRouter routes image generation, video, and voice calls through the same local proxy:

**Image generation** (`/cr-imagegen`)

```
/cr-imagegen a misty mountain at dawn
/cr-imagegen --model banana-pro --size 4096x4096 abstract art
```

| Model | Provider | Price | Max Size |
|-------|----------|-------|----------|
| nano-banana | Google Gemini Flash | $0.05/image | 1024×1024 |
| banana-pro | Google Gemini Pro | $0.10/image | 4096×4096 |
| gpt-image-2 | OpenAI | $0.06/image | 1536×1024 |
| seedream | ByteDance | $0.045/image | 2848×1600 |
| zai/cogview-4 | Zhipu | $0.015/image | 1440×1440 |

**Video generation** (`/videogen`)

```
/videogen --model seedance-2-fast --duration=5 a cat waving
```

Supports Seedance 2 (ByteDance), Sora 2 (Azure), Grok Video. 5-second clips run ~$0.42–$1.49.

**AI phone calls** (`/cr-call`)

```
/cr-call +14155552671 "Hi, calling to confirm tomorrow's 3pm meeting"
```

Powered by Bland.ai, $0.54 flat per call, up to 30 minutes, with transcript and recording retrieval.

---

## 7. The Core Distinction from Other Routers

Before ClawRouter, "smart routing" meant: you configure rules in a dashboard, the platform calls the API for you. Routing logic runs on someone else's server; every routing decision crosses a network.

ClawRouter's routing is **entirely local**:

```
Request → Local 15-dimension scorer → Tier → Best model → Direct forward
         (sub-1ms, zero external dependencies)
```

No intermediate server knows what model you're using or what you asked.

For agent systems this matters: agents call LLMs at high frequency. If each routing decision adds 50–100ms, that accumulates to seconds of latency in a multi-step agent pipeline. Sub-1ms local routing eliminates this overhead entirely.

---

## 8. When to Use It

**Good fit**:
- Multi-step AI agents where task complexity varies significantly per step (summarization vs. code reasoning)
- High-volume LLM workloads where you want to control costs without sacrificing output quality
- Agents that need to operate autonomously without human-managed API keys
- Multi-provider model access without maintaining separate SDKs

**Worth thinking about**:
- The 15-dimension local scorer is rule-based — not as precisely calibrated as an end-to-end trained routing model (like Martian claims)
- Free model quality varies; use `/model premium` for mission-critical tasks
- x402 + USDC is crypto payment — some friction for teams without Web3 exposure
- Image/video/voice capabilities are pay-as-you-go — estimate volume before committing

---

*Data source: GitHub BlockRunAI/ClawRouter, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
