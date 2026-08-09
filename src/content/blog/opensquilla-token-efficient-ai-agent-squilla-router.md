---
title: "OpenSquilla 0.5.2：同等预算，9× token 成本降低，靠的是本地 Agent 路由器"
titleEn: "OpenSquilla 0.5.2: Same Budget, 9x Lower Token Cost, Thanks to a Local Agent Router"
description: "OpenSquilla 把「这一步用哪个模型」的决策内化到 Agent 本身：SquillaRouter 是一个在设备上运行的 LightGBM+ONNX 分类器，每个 turn 评估复杂度后路由到最便宜的胜任模型，prompt 从不离开本机做这个决策。PinchBench 结果：分数持平（0.9251 vs 0.9255），成本从 $6.23 降到 $0.69，减少 89%。6535 stars，Apache 2.0，v0.5.2 稳定版。"
descriptionEn: "OpenSquilla internalizes 'which model for this step' into the agent itself. SquillaRouter — an on-device LightGBM+ONNX classifier — scores each turn's complexity and routes to the cheapest capable model, prompt never leaves the machine for routing. PinchBench: score parity (0.9251 vs 0.9255 for Claude Opus 4.7), cost down from $6.23 to $0.69 — 89% reduction. 6,535 stars, Apache 2.0, v0.5.2 stable."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["AI Agent", "Token优化", "模型路由", "本地推理", "开源工具", "LLM成本", "Agent框架", "Mycelium"]
heroImage: "../../assets/images/opensquilla-token-efficient-ai-agent-squilla-router-banner.jpg"
---

*by Mycelium Protocol*

---

用 AI Agent 做任务最快烧掉钱的方式，是让每一步都走最贵的模型。

Claude Opus 处理「把这个字符串转成大写」，和处理「设计一套分布式事务方案」，花的钱差了几个数量级——但如果不做分流，两步用同一个模型，就是在用牛刀切黄油。

**[OpenSquilla](https://github.com/opensquilla/opensquilla)** 把这个决策内化到 Agent 本身：一个在设备上运行的分类器（**SquillaRouter**）评估每个 turn 的复杂度，然后路由到当前能胜任的最便宜模型。结果是**同分数，成本降低 89%**。

6535 stars，0.5.2 稳定版，Apache 2.0 许可。

---

## 核心：SquillaRouter — 在设备上做路由决策

SquillaRouter 是 OpenSquilla 的核心组件，`recommended` extra 里默认安装：

- **技术栈**：LightGBM + ONNX Runtime，本地推理
- **评分维度**：turn 长度、语言、是否含代码、关键词、语义 embedding
- **路由层级**：C0 → C1 → C2 → C3（从最廉价到最强大）
- **关键设计**：**分类在设备上运行，prompt 从不离开本机做路由决策**

这解决了一个微妙但重要的问题：传统的「LLM 路由」通常要把 prompt 发给另一个 LLM 来判断复杂度，这本身就消耗 token。SquillaRouter 用本地轻量分类器替代这一步，分类零成本，决策不出机器。

配合两个进一步的优化：
- **自适应推理**：只对 SquillaRouter 评分为复杂的 turn 请求扩展推理（CoT）
- **自适应 system prompt**：简单任务用轻量指令，复杂任务用完整指令——不让 prompt cache 被简单任务的全量 prompt 浪费

---

## 数据说话：PinchBench 1.2.1（25 个任务）

| Agent | 后端模型 | 平均分 | 总 Input tokens | 总 Cost |
|-------|---------|--------|-----------------|---------|
| **OpenSquilla** | 路由器（Opus 4.7 + GLM 5.1 + DS4 Flash） | 0.9251 | 1,721,328 | **$0.688** |
| OpenClaw | Claude Opus 4.7（单一模型） | 0.9255 | 3,066,243 | $6.233 |

分数几乎持平（差距 0.0004），成本降低 89%，token 消耗减少 44%。

这组数据有一个值得注意的地方：OpenSquilla 用的总 input token 更少（更少重复大量 prompt），但 output token 也更少——说明路由器确实把简单任务分流到了更简洁的模型，而不是把所有工作都扔给 Opus 然后精简输出。

---

## 架构：一个统一的 turn 循环，多个接入面

OpenSquilla 的架构思路是**微内核**：所有接入面（Web UI、CLI、消息频道）共用同一个 `TurnRunner`，工具分发、重试、决策日志行为完全一致。

```
Gateway（127.0.0.1:18791，Starlette ASGI）
   ├── Web UI（/control/，Vue 控制台）
   ├── CLI（opensquilla chat / opensquilla agent）
   └── 消息频道（Feishu / Telegram / Discord / DingTalk / WeCom / Slack / Matrix / QQ）
              ↓
         TurnRunner（统一 turn 循环）
              ├── SquillaRouter（本地分类，路由到 C0~C3 层）
              ├── Provider 层（20+ LLM 提供商，主备 fallback）
              ├── 工具层（文件/Shell/Git/搜索/文档/图像/TTS...）
              ├── 技能层（15 个内置 skill，按需加载）
              └── 内存层（MEMORY.md + Markdown 笔记 + SQLite FTS + sqlite-vec）
```

**Provider 层**支持 20+ 提供商：TokenRhythm、OpenRouter、OpenAI、Anthropic、Ollama、DeepSeek、Gemini、DashScope/Qwen、Moonshot、Mistral、Groq、智谱、SiliconFlow、vLLM、LM Studio……每个 provider 有主备 fallback 配置，一个 provider 不可用自动切换，代码和配置 schema 不需要改。

---

## 安装和上手

**快速安装**（推荐，全平台）：

```sh
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.5.2/opensquilla-0.5.2-py3-none-any.whl"
```

`recommended` extra 包含 SquillaRouter 依赖（ONNX Runtime、LightGBM、NumPy、tokenizers）。

**桌面安装**（macOS/Windows，含 Electron Shell + Vue 控制台）：
- macOS Apple Silicon：[OpenSquilla-0.5.2-mac-arm64.dmg](https://github.com/opensquilla/opensquilla/releases/download/v0.5.2/OpenSquilla-0.5.2-mac-arm64.dmg)（已签名公证）
- Windows x64：[OpenSquilla-0.5.2-win-x64.exe](https://github.com/opensquilla/opensquilla/releases/download/v0.5.2/OpenSquilla-0.5.2-win-x64.exe)

**配置和运行**：

```sh
opensquilla onboard              # 交互式初始化向导
opensquilla gateway run          # 前台运行，127.0.0.1:18791
opensquilla chat                 # 交互 REPL
opensquilla agent -m "你的任务"  # 单次自动化模式
```

**非交互环境（CI/SSH）**：

```sh
export OPENROUTER_API_KEY="sk-..."
opensquilla onboard --provider openrouter --api-key-env OPENROUTER_API_KEY
```

**macOS 注意事项**：`libomp` 需要单独安装（桌面版已内置，终端安装需要 `brew install libomp`）；安装后重启 gateway，SquillaRouter 激活。

---

## 安全沙箱：三层策略

OpenSquilla 把代码执行安全做了细化设计：

| 策略层 | 适用场景 | 隔离技术 |
|--------|---------|---------|
| Standard | 日常使用 | 基础权限控制 |
| Strict | 更高安全要求 | 系统调用限制 |
| Locked | 生产/不可信输入 | Linux: Bubblewrap；macOS: Seatbelt(`sandbox-exec` + SBPL)；Windows: 原生后端 |

额外保护：
- **自动暂停**：拒绝日志超过阈值后，自主运行自动暂停等待人工决策
- **prompt 注入防护**：技能元数据和工具结果经 XML escape
- **拒绝产物清除**：被拒绝的输出从 replay 里移除

---

## 持久内存

默认使用本地 embedding（ONNX，随包内置），也可以接 OpenAI 或 Ollama。存储结构：
- `MEMORY.md`：结构化长期记忆（对标 Claude Code 的 auto memory 机制）
- 带日期的 Markdown 笔记：时序事件
- SQLite 全文搜索（FTS）+ sqlite-vec 语义向量检索

可选指数衰减（旧记忆权重随时间降低）和 "dream 整合"（对历史记忆做压缩汇总）。

---

## v0.5.0 稳定版的关键升级

0.5.0 是 0.5 线的第一个稳定版，汇聚了四个预览版的成果：

- **Model Ensemble 路由**：一个 turn 可以跨多个模型运行；on-device 路由保证分类本地完成
- **安全升级保护**：带预览的迁移、profile 恢复、Windows 卸载时 profile 数据保护
- **桌面成熟度**：macOS 签名 + 公证，in-app 更新，gateway 启动恢复
- **成本追踪**：精确到账单算术的日度 token 用量报告，持久账本

---

## 从 OpenClaw / Hermes 迁移

如果已有 OpenClaw 或 Hermes 的历史数据：

```sh
# 预览迁移计划（不执行）
opensquilla migrate openclaw --json
opensquilla migrate hermes --json

# 执行迁移
opensquilla migrate openclaw --apply
opensquilla migrate hermes --apply

# 一次迁移两个
opensquilla migrate --source openclaw,hermes --apply
```

会迁移：memory、persona 文件、skills、MCP/channel 配置。加 `--migrate-secrets` 才会迁移密钥（建议先看预览报告）。

---

## 技术报告：路由器即数据飞轮

2026 年 7 月，团队在 arXiv 发布技术报告 [**《Agentic Routing: The Harness-Native Data Flywheel》**](https://arxiv.org/abs/2607.11399)：

核心主张是 harness-native 路由器会把日常 agent 流量自动转化为自我改进的数据飞轮——每次 turn 的路由决策和结果，都可以反馈给分类器。报告还展示了 **multi-model ensemble routing 超越 Fable 5** 的结果。

---

## 为什么值得关注

AI Agent 的成本问题正在成为生产部署的核心约束。大多数解决方案是「用更便宜的模型」（降质）或「减少 Agent 调用次数」（降频）——两者都是在压缩能力换成本。

OpenSquilla 的思路不同：**把路由决策内化到 Agent 内部，对复杂度分层，便宜任务走便宜模型，只有真正需要强模型的 turn 才触发它**。这不是妥协，而是资源精确分配。

数据的直白对比：同等测试集，分数 0.9251 vs 0.9255，成本 $0.688 vs $6.233。如果你在用 Agent 跑任何接近生产规模的任务，这个差距不是优化项——是运营层面的决定性差距。

仓库：[github.com/opensquilla/opensquilla](https://github.com/opensquilla/opensquilla)  
网站：[opensquilla.ai](https://opensquilla.ai)  
技术报告：[arxiv.org/abs/2607.11399](https://arxiv.org/abs/2607.11399)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenSquilla 0.5.2: Same Score, 89% Less Cost — On-Device Agent Routing

*by Mycelium Protocol*

The fastest way to burn money on AI agents is to route everything to your most capable model regardless of what the task actually requires. **[OpenSquilla](https://github.com/opensquilla/opensquilla)** internalizes the routing decision into the agent itself: **SquillaRouter** — an on-device LightGBM+ONNX classifier — scores each turn's complexity and routes to the cheapest model that can handle it. The prompt never leaves the machine to make that call.

Result on PinchBench 1.2.1 (25 tasks): **score parity, cost down from $6.23 to $0.69 — 89% reduction**. 6,535 stars, Apache 2.0, v0.5.2 stable.

### How SquillaRouter Works

```
Every turn → SquillaRouter (local LightGBM + ONNX, on-device)
  Scores: length, language, code presence, keywords, semantic embeddings
  Routes to: C0 (cheapest) → C1 → C2 → C3 (most capable)
  Classification cost: zero tokens, stays on-machine
```

Two additional mechanisms amplify the savings:
- **Adaptive reasoning**: extended reasoning (CoT) requested only when SquillaRouter marks a turn as complex
- **Adaptive system prompt**: lightweight instructions for simple turns, full instructions for complex ones — preserving prompt cache for turns that actually need it

### The Numbers

| Agent | Model | Score | Input tokens | Cost |
|-------|-------|-------|-------------|------|
| OpenSquilla | Router (Opus 4.7, GLM 5.1, DS4 Flash) | 0.9251 | 1,721,328 | **$0.688** |
| OpenClaw | Claude Opus 4.7 only | 0.9255 | 3,066,243 | $6.233 |

Score difference: 0.0004. Cost difference: 9×. The routed input token count is also 44% lower — simpler turns genuinely get handled by simpler models, not by premium models with compressed responses.

### Architecture: Microkernel with Unified Turn Loop

All entry points — Web UI, CLI, and messaging channels — share one `TurnRunner`. Tool dispatch, retries, and decision logging behave identically everywhere.

**20+ LLM providers**: TokenRhythm, OpenRouter, OpenAI, Anthropic, Ollama, DeepSeek, Gemini, DashScope/Qwen, Moonshot, Mistral, Groq, Zhipu, SiliconFlow, vLLM, LM Studio, and more — with primary-plus-fallback selection, no code or config schema changes required.

**15 bundled skills** that load only when the task needs them: coding, GitHub, cron, pptx/docx/xlsx/pdf, summarization, tmux, weather, and more.

**Channels**: Feishu, Telegram, Discord, DingTalk, WeCom, Slack, Matrix, QQ.

### Quick Install

```sh
uv tool install --python 3.12 \
  "opensquilla[recommended] @ https://github.com/opensquilla/opensquilla/releases/download/v0.5.2/opensquilla-0.5.2-py3-none-any.whl"
```

Desktop installers (Electron shell + Vue control console):
- macOS Apple Silicon: signed + notarized .dmg
- Windows x64: .exe installer

```sh
opensquilla onboard        # interactive first-run wizard
opensquilla gateway run    # start gateway at 127.0.0.1:18791
opensquilla chat           # interactive REPL
```

### Security Sandbox

Three policy tiers: Standard → Strict → Locked. Isolation technologies: Bubblewrap (Linux), Seatbelt/`sandbox-exec` with generated SBPL profiles (macOS), Windows native backend. Denial ledger auto-pauses autonomous runs after repeated denials. Tool results and skill metadata XML-escaped against prompt injection.

### What's New in 0.5.0 (Stable)

- **Model Ensemble + multi-provider routing**: one turn can run across several models; on-device classification keeps routing decisions local
- **Safe upgrades**: guarded migration previews, profile recovery, Windows profile-data preservation on uninstall
- **Desktop maturity**: signed + notarized macOS builds, in-app updates
- **Cost reporting**: per-turn and per-session token rollups on a durable ledger with exact billing arithmetic

### Migration from OpenClaw or Hermes

```sh
opensquilla migrate openclaw --json    # dry run first
opensquilla migrate openclaw --apply   # apply
```

Migrates memory, persona files, skills, MCP/channel config. Add `--migrate-secrets` only after reviewing the dry-run report.

### Technical Report

The team published [*Agentic Routing: The Harness-Native Data Flywheel*](https://arxiv.org/abs/2607.11399) (arXiv 2607.11399, July 2026): the harness-native router converts everyday agent traffic into a self-improving data flywheel. It also shows multi-model ensemble routing surpassing Fable 5.

### Why It Matters

Most "cost optimization" approaches either downgrade to weaker models or reduce call frequency — both compress capability to reduce spend. OpenSquilla's approach is different: route by actual complexity, so cheap turns go to cheap models and premium capacity fires only when genuinely needed. That's not a tradeoff — it's precision resource allocation.

$6.23 → $0.69 on the same task set. For production-scale agent workloads, that difference isn't a nice-to-have — it's the difference between sustainable and not.

Repository: [github.com/opensquilla/opensquilla](https://github.com/opensquilla/opensquilla) · Site: [opensquilla.ai](https://opensquilla.ai) · arXiv: [2607.11399](https://arxiv.org/abs/2607.11399)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
