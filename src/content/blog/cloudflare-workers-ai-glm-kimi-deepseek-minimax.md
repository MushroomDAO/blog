---
title: "Cloudflare 悄悄把 GLM-5.2、Kimi K3、DeepSeek V4 都接上了，而且只要一个 token"
titleEn: "Cloudflare Quietly Added GLM-5.2, Kimi K3, and DeepSeek V4 — All Behind One Token"
description: "Cloudflare Workers AI 已上线 GLM-5.2、Kimi K2.7 Code、1M 上下文的 Kimi K3、DeepSeek V4 Pro、MiniMax M3，同一个 token、同一行代码即可调用，还理清了自托管与第三方托管的价格和数据边界。"
descriptionEn: "Cloudflare Workers AI now serves GLM-5.2, Kimi K2.7 Code, 1M-context Kimi K3, DeepSeek V4 Pro, and MiniMax M3 — all callable with one token and one line of code, with a clear line between self-hosted and third-party pricing and data boundaries."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["Cloudflare", "Workers AI", "GLM-5.2", "Kimi K3", "DeepSeek V4", "MiniMax", "边缘推理"]
heroImage: "../../assets/images/cloudflare-workers-ai-glm-kimi-deepseek-minimax-banner.jpg"
---

> **一句话结论**：你现在可以在 Cloudflare Worker 里，用**同一行代码**调用 GLM-5.2、Kimi K2.7-Code、DeepSeek V4 Pro、MiniMax M3——不用去各家申请 API key，不用管各家计费，推理还跑在离用户最近的边缘节点上。

## 起因

我们在做的应用要嵌 AI 能力。常规做法是：选一家模型厂商 → 申请 key → 管额度 → 写适配层 → 想换模型时再来一遍。如果同时想用几家的开源模型，这套流程就得复制几份。

所以有个很自然的问题：**Cloudflare 的 Workers AI，到底能不能直接给到最新的开源模型？** 如果能，应用和 AI 就是同一个运行时里的事，而不是「应用去调远端 API」。

于是把官方文档、blog、changelog 翻了一遍。结果比预期好。

## 结论：你想要的基本都有

| 模型 | 有没有 | 调用 ID |
|:---|:---|:---|
| **GLM-5.2**（智谱，agentic coding） | ✅ 2026-06-16 上线 | `glm-5.2` |
| **Kimi K2.7 Code**（月之暗面，1T MoE） | ✅ 2026-06-12 上线 | `kimi-k2.7-code` |
| **Kimi K3**（**1M 上下文**） | ✅ | `moonshotai/kimi-k3` |
| **DeepSeek V4 Pro** | ✅ | `deepseek/deepseek-v4-pro` |
| **MiniMax M3** | ✅ | `minimax/m3` |
| GLM 5.3 / DeepSeek V4 Flash | ❌ 暂无 | — |

除此之外还有 `gpt-oss-120b/20b`（OpenAI 开源权重）、`llama-4-scout`、`qwen3-30b`、`gemma-4-26b`、`nemotron-3-120b`……

调用长这样，**自托管和第三方完全一致**：

```js
const res = await env.AI.run('glm-5.2', {
  messages: [{ role: 'user', content: '...' }]
})

// 换成 DeepSeek V4 Pro？改一个字符串而已
const res2 = await env.AI.run('deepseek/deepseek-v4-pro', {
  messages: [{ role: 'user', content: '...' }]
})
```

**不需要 DeepSeek 的 key，也不需要 Fireworks 的 key**——用你自己的 Cloudflare token，Cloudflare 统一计费。这是整件事里最省心的部分。

## 但有一条分界线，不讲清楚会踩坑

模型分两类，**调用方式一样，商业属性完全不同**：

|  | Cloudflare 自托管 | 第三方托管 |
|:---|:---|:---|
| 谁的 GPU | Cloudflare 自己的 | 合作方（DeepSeek V4 Pro 走 Fireworks） |
| 价格 | **文档公开单价** | **只在 dashboard 能看到** |
| 数据 | 不出 Cloudflare | 出网到合作方 |

GLM、Kimi K2.x、Qwen、gpt-oss、Llama 4 属于**自托管**；DeepSeek V4 Pro、Kimi K3、MiniMax M3 属于**第三方**。

所以：**第三方那批，决策前必须登 dashboard 查价**，别拿自托管的价格去估算。涉及敏感数据的场景，也建议只用自托管那批。

## 价格：便宜档真的很便宜

免费额度每天 10,000 Neurons，超出后 $0.011/1000 Neurons。自托管部分单价公开：

| 模型 | 输入 $/M | 输出 $/M |
|:---|---:|---:|
| `qwen3-30b-a3b-fp8` | **0.051** | 0.335 |
| `glm-4.7-flash` | **0.060** | 0.400 |
| `gpt-oss-20b` | 0.200 | 0.300 |
| `llama-4-scout-17b` | 0.270 | 0.850 |
| `gpt-oss-120b` | 0.350 | 0.750 |
| `kimi-k2.7-code` | 0.950 | 4.000 |
| `glm-5.2` | 1.400 | 4.400 |

`glm-4.7-flash` 值得单独说：**131K 上下文、$0.06/M 输入、工具调用支持 100+ 语言**，便宜到可以当默认档，复杂请求再往上升级。

⚠️ `glm-5.2` 和 `kimi-k2.*` **需要 Workers Paid 计划**，免费额度只够验证。

## 为什么这件事值得关注？

**不是「又多了一个 API 聚合器」。** 区别在三处：

**① 推理和应用在同一个边缘节点。** 不是 Worker 去调远端 API，而是模型就跑在你代码执行的地方。流式输出、多轮工具调用这类场景，首字延迟差别很直观。

**② 一套凭证、一套账单。** 不用为 GLM/Kimi/MiniMax/DeepSeek 各开账号、各管 key 和额度。

**③ 和其余原语天然同构。** Durable Objects 存会话、KV/R2 存产物、Queues 异步、Workflows 编排、Vectorize 做 RAG、AI Gateway 做缓存限流——同一个账号同一个运行时，不用在几朵云之间搬数据。

## 他们是真在自己跑，不是贴牌

Cloudflare 有篇工程博客讲了怎么把这些大模型塞进自己的机器：

- **KV Cache 从 BF16 量化到 FP8**：缓存减半，Kimi K2.6 的上下文容量从 686K 涨到 **1.37M tokens**，峰值并发吞吐 **+41%**
- **GLM 权重从 INT8 压到 INT4**：体积 705GB → **421GB**（-40%），同样硬件能放 1.18M tokens 的 KV cache；低并发下解码吞吐 **+55%**（60 → 92 tokens/s）
- **prefill / decode 池分离**：解码用 INT4、预填用 FP8，各取所长
- **缓存完整性校验**：防止请求读到别人的 cache page，开销 <1%

这些优化说明大模型是**真自托管**并做了针对性工程，不是简单转发请求。

## 上新快，但弃用也快

看 2026 年的 changelog，节奏是每月 6–20 个模型变更：

- **6-16** GLM-5.2 上线
- **6-12** Kimi K2.7 Code 上线（**四天内两个大模型**）
- **5-08** 一次性弃用 **19 个**老模型（Llama 3/3.1、Mistral 7B、Gemma 7B、Phi-2…）
- 4-20 Kimi K2.6 · 4-04 Gemma 4 · 3-19 Kimi K2.5 · 3-11 Nemotron 3 · 2-13 GLM-4.7-Flash

**开源模型发布后通常数周内就能用上**——这是好消息。但 5 月那次一口气砍掉 19 个模型也提醒我们：**生产代码不要硬编码模型 ID**，留一层映射，并盯住 changelog 的 deprecation 公告。

## 怎么开始？

1. **先用便宜档验证形态**：`qwen3-30b-a3b-fp8` 或 `glm-4.7-flash`，免费额度就能跑通端到端
2. **需要强推理/长上下文再升级**到 `glm-5.2` 或 `kimi-k2.7-code`
3. **1M 上下文场景**（整仓代码、长文档）才考虑 `moonshotai/kimi-k3`——**先查价**
4. **架构上留模型映射层**，配合 AI Gateway 做缓存、限流、可观测

## 常见问题

**Q：不用自己申请 DeepSeek/Kimi 的 key，是不是意味着完全免费？**
不是。第三方托管的模型（DeepSeek V4 Pro、Kimi K3、MiniMax M3）仍按量计费，只是账单统一走 Cloudflare，具体单价要登 dashboard 查，文档不公开。

**Q：敏感数据能用第三方托管的模型吗？**
不建议。第三方托管意味着推理请求会出网到合作方基础设施（如 Fireworks），涉及敏感数据的场景应只用 Cloudflare 自托管的那批模型。

**Q：生产环境该怎么防止模型被弃用影响服务？**
不要在业务代码里硬编码模型 ID，做一层模型映射配置，并关注 Workers AI 的 changelog——2026-05-08 曾一次性弃用 19 个老模型。

---

**参考资料**

- Workers AI 模型目录：https://developers.cloudflare.com/workers-ai/models/
- Cloudflare AI 全模型目录（214 个）：https://developers.cloudflare.com/ai/models/
- Workers AI 定价：https://developers.cloudflare.com/workers-ai/platform/pricing/
- Workers AI Changelog：https://developers.cloudflare.com/workers-ai/changelog/
- Cloudflare 工程博客《Smaller, faster, safer — running Kimi and GLM at scale》：https://blog.cloudflare.com/smaller-faster-safer-models/
- Cloudflare 博客《Powering the agents — Workers AI now runs large models》：https://blog.cloudflare.com/workers-ai-large-models/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **TL;DR**: You can now call GLM-5.2, Kimi K2.7-Code, DeepSeek V4 Pro, and MiniMax M3 from a Cloudflare Worker using **the same line of code** — no need to apply for API keys from each vendor, no need to juggle separate billing, and inference runs on the edge node closest to your user.

## Why We Looked Into This

Our app needs embedded AI capability. The usual playbook is: pick a model vendor → apply for a key → manage quotas → write an adapter layer → repeat when you want to switch models. Want to use several vendors' open models at once? Multiply that process.

So a natural question came up: **can Cloudflare's Workers AI directly serve the latest open-source models?** If it can, "app" and "AI" become one runtime instead of "app calling a remote API."

We went through the official docs, blog posts, and changelog. The result was better than expected.

## The Answer: Basically Everything You Want Is There

| Model | Available? | Model ID |
|:---|:---|:---|
| **GLM-5.2** (Zhipu, agentic coding) | ✅ launched 2026-06-16 | `glm-5.2` |
| **Kimi K2.7 Code** (Moonshot AI, 1T MoE) | ✅ launched 2026-06-12 | `kimi-k2.7-code` |
| **Kimi K3** (**1M context**) | ✅ | `moonshotai/kimi-k3` |
| **DeepSeek V4 Pro** | ✅ | `deepseek/deepseek-v4-pro` |
| **MiniMax M3** | ✅ | `minimax/m3` |
| GLM 5.3 / DeepSeek V4 Flash | ❌ not yet | — |

Also available: `gpt-oss-120b/20b` (OpenAI's open weights), `llama-4-scout`, `qwen3-30b`, `gemma-4-26b`, `nemotron-3-120b`, and more.

The call shape is **identical for self-hosted and third-party models**:

```js
const res = await env.AI.run('glm-5.2', {
  messages: [{ role: 'user', content: '...' }]
})

// Switch to DeepSeek V4 Pro? Just change one string.
const res2 = await env.AI.run('deepseek/deepseek-v4-pro', {
  messages: [{ role: 'user', content: '...' }]
})
```

**No DeepSeek key, no Fireworks key needed** — you use your own Cloudflare token, and Cloudflare handles billing centrally. This is the most convenient part of the whole thing.

## One Dividing Line You Need to Know, Or You'll Get Burned

The models split into two categories that **call the same way but have completely different commercial properties**:

|  | Cloudflare self-hosted | Third-party hosted |
|:---|:---|:---|
| Whose GPU | Cloudflare's own | Partner infrastructure (DeepSeek V4 Pro runs on Fireworks) |
| Price | **Publicly documented** | **Only visible in the dashboard** |
| Data | Never leaves Cloudflare | Egresses to the partner |

GLM, Kimi K2.x, Qwen, gpt-oss, and Llama 4 are **self-hosted**; DeepSeek V4 Pro, Kimi K3, and MiniMax M3 are **third-party**.

So: **for the third-party batch, you must log into the dashboard and check pricing before deciding** — don't estimate cost using self-hosted pricing. For sensitive-data workloads, stick to the self-hosted batch.

## Pricing: The Cheap Tier Is Genuinely Cheap

Free tier is 10,000 Neurons/day; beyond that it's $0.011 per 1,000 Neurons. Self-hosted pricing is public:

| Model | Input $/M | Output $/M |
|:---|---:|---:|
| `qwen3-30b-a3b-fp8` | **0.051** | 0.335 |
| `glm-4.7-flash` | **0.060** | 0.400 |
| `gpt-oss-20b` | 0.200 | 0.300 |
| `llama-4-scout-17b` | 0.270 | 0.850 |
| `gpt-oss-120b` | 0.350 | 0.750 |
| `kimi-k2.7-code` | 0.950 | 4.000 |
| `glm-5.2` | 1.400 | 4.400 |

`glm-4.7-flash` deserves a callout: **131K context, $0.06/M input, tool calling in 100+ languages** — cheap enough to be your default tier, upgrading only for complex requests.

⚠️ `glm-5.2` and `kimi-k2.*` **require a Workers Paid plan** — the free tier is only enough for validation.

## Why Does This Matter?

**This isn't "yet another API aggregator."** The difference is in three places:

**① Inference and app share the same edge node.** The Worker isn't calling a remote API — the model runs right where your code executes. For streaming output and multi-turn tool calling, the first-token latency difference is very noticeable.

**② One credential, one bill.** No separate accounts, keys, or quotas for GLM/Kimi/MiniMax/DeepSeek.

**③ Native composability with the rest of the primitives.** Durable Objects for sessions, KV/R2 for artifacts, Queues for async work, Workflows for orchestration, Vectorize for RAG, AI Gateway for caching and rate limiting — all in the same account, same runtime, no shuffling data between clouds.

## They're Actually Running It Themselves, Not Just Reselling It

Cloudflare published an engineering blog post on how they fit these large models onto their own hardware:

- **KV cache quantized from BF16 to FP8**: cache halved, Kimi K2.6's context capacity grew from 686K to **1.37M tokens**, peak concurrent throughput **+41%**
- **GLM weights compressed from INT8 to INT4**: size dropped from 705GB to **421GB** (-40%), the same hardware now fits 1.18M tokens of KV cache; low-concurrency decode throughput **+55%** (60 → 92 tokens/s)
- **Separate prefill/decode pools**: INT4 for decode, FP8 for prefill, each optimized for its job
- **Cache integrity verification**: prevents a request from reading another tenant's cache page, at <1% overhead

These optimizations show this is **genuine self-hosting** with targeted engineering, not simple request forwarding.

## New Models Arrive Fast, But Deprecations Are Fast Too

Looking at the 2026 changelog, the pace is 6–20 model changes per month:

- **6-16** GLM-5.2 launched
- **6-12** Kimi K2.7 Code launched (**two major models in four days**)
- **5-08** 19 old models deprecated at once (Llama 3/3.1, Mistral 7B, Gemma 7B, Phi-2…)
- 4-20 Kimi K2.6 · 4-04 Gemma 4 · 3-19 Kimi K2.5 · 3-11 Nemotron 3 · 2-13 GLM-4.7-Flash

**Open-source models typically become available within weeks of release** — that's the good news. But the May deprecation of 19 models in one shot is a reminder: **don't hardcode model IDs in production code**. Keep a mapping layer, and watch the changelog's deprecation notices.

## How to Get Started

1. **Validate the shape with the cheap tier first**: `qwen3-30b-a3b-fp8` or `glm-4.7-flash` — the free tier is enough for an end-to-end test
2. **Upgrade to `glm-5.2` or `kimi-k2.7-code`** when you need stronger reasoning or longer context
3. **Only consider `moonshotai/kimi-k3`** for 1M-context use cases (whole-repo code, long documents) — **check pricing first**
4. **Keep a model-mapping layer in your architecture**, paired with AI Gateway for caching, rate limiting, and observability

## FAQ

**Q: Not needing separate DeepSeek/Kimi keys — does that mean it's free?**
No. Third-party-hosted models (DeepSeek V4 Pro, Kimi K3, MiniMax M3) are still billed by usage; billing is just consolidated through Cloudflare. Exact pricing isn't published and must be checked in the dashboard.

**Q: Can I use the third-party-hosted models for sensitive data?**
Not recommended. Third-party hosting means inference requests egress to partner infrastructure (e.g., Fireworks). Sensitive-data workloads should stick to Cloudflare's self-hosted models.

**Q: How do I protect production from model deprecations?**
Don't hardcode model IDs in business logic — keep a model-mapping config layer and watch the Workers AI changelog. On 2026-05-08, Cloudflare deprecated 19 old models in a single announcement.

---

**References**

- Workers AI model catalog: https://developers.cloudflare.com/workers-ai/models/
- Cloudflare AI full model catalog (214 models): https://developers.cloudflare.com/ai/models/
- Workers AI pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Workers AI changelog: https://developers.cloudflare.com/workers-ai/changelog/
- Cloudflare engineering blog, "Smaller, faster, safer — running Kimi and GLM at scale": https://blog.cloudflare.com/smaller-faster-safer-models/
- Cloudflare blog, "Powering the agents — Workers AI now runs large models": https://blog.cloudflare.com/workers-ai-large-models/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
