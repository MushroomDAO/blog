---
title: "Rakazo：每个 Bot 有自己的电脑、记忆和调度，开源 Grok Bot 替代"
titleEn: "Rakazo: Each Bot Gets Its Own Computer, Memory and Schedule — Open-Source Grok Bot Alternative"
description: "elie222/rakazo，3094 星，Apache 2.0，TypeScript。Inbox Zero 作者新作，定位「开源 Grok Bot 替代」。每个持久 Bot 拥有独立会话、记忆、定时任务，以及一台沙箱电脑（浏览器/终端/桌面/文件），登录状态跨会话保留。Bot 间可互相委托子任务。沙箱后端支持 Docker、E2B、Daytona、CreateOS 和 Box，可完全本地运行。Web/Electron/Expo 三端，Beta 阶段。"
descriptionEn: "elie222/rakazo, 3094 stars, Apache 2.0, TypeScript. From the author of Inbox Zero — positioned as an open-source Grok Bot alternative. Each persistent Bot gets its own conversations, memory, scheduled routines, and a sandboxed computer (browser, terminal, desktop, files) with login states preserved across sessions. Bots can delegate tasks to peer bots or short-lived subagents. Sandbox backends: Docker, E2B, Daytona, CreateOS, Box — can run fully local. Web/Electron/Expo, in beta."
pubDate: 2026-09-30
heroImage: "../../assets/images/rakazo-persistent-ai-teammate-sandbox-computer-use-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["AI同事", "自托管", "多Agent", "沙箱", "开源拆解", "TypeScript"]
lang: "zh-CN"
wechatTitle: "Rakazo：开源持久AI同事，有自己的电脑"
wechatDigest: "3094星Apache-2.0；Inbox Zero作者；每个bot有电脑+记忆+调度；多沙箱后端可选"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 「Grok Bot 替代」这个定位说了什么

Grok 有「Bots」功能——每个 Bot 有持久记忆、工具访问权限，以及 X 账号级的操作能力。Rakazo 把这个 UX 模式抽离出来，做成自托管开源版本：Bot 持久化、有调度、有沙箱电脑，可以接任何 LLM，运行在你自己的服务器上。

作者是 Elie，也是开源邮件助手 Inbox Zero 的作者（github.com/elie222/inbox-zero）。

仓库：github.com/elie222/rakazo  
**Stars：3094 | License：Apache 2.0 | Beta | 文档：rakazo.com**

---

## 持久 Bot 的三个核心属性

### 1. 会话、记忆、调度——跨会话的状态

普通 AI 聊天是无状态的——关掉窗口，下次重开什么都不记得。Rakazo 的每个 Bot 持久保存：

- **会话历史**：所有对话记录
- **记忆**：Bot 从交互中提炼的长期知识
- **定时任务（Routines）**：Bot 可以在你不在线时自动执行的调度任务
- **执行历史**：过去跑过什么，结果如何

Bot 不仅是聊天对象，更是一个有自己任务队列的持续运行工作者。

### 2. 沙箱电脑——Bot 可以操作真实界面

每个 Bot 可以拿到一台沙箱电脑，里面有：

- **浏览器**：可以打开网页、填表单、点击操作
- **终端**：运行命令、脚本
- **文件系统**：读写文件
- **图形桌面**：操作 GUI 应用

关键细节：**浏览器的登录状态跨会话保留**。网站第一次登录后，下次再派 Bot 去操作这个网站，它已经是登录状态，不需要再走一遍登录流程。

沙箱分两种：
- **团队共享电脑（Shared Team Computer）**：团队内多个 Bot 共用一台沙箱
- **私有电脑（Private Computer）**：每个 Bot 或每个用户独占隔离的沙箱

### 3. Bot 间委托——多 Agent 的持久版本

Bot 可以把子任务委托给：

- **同级 Bot（Peer Bot）**：派另一个已有 Bot 去完成特定任务
- **短期子 Agent（Short-lived Subagent）**：临时创建、任务完成后销毁

这是「多 Agent」的持久模型——不是一次性的 Agent 链，而是持续存在的协作网络，每个成员有自己的记忆和工具。

---

## 沙箱后端：本地到云端都可选

Rakazo 把计算环境抽象成可插拔的后端，支持六种提供商：

| 提供商 | 类型 | 说明 |
|--------|------|------|
| Docker | 本地 | 默认选项，完全离线可用 |
| E2B | 远程 | 专用沙箱服务，按需付费 |
| Daytona | 远程 | 开发环境即服务 |
| CreateOS | 远程云桌面 | `CREATEOS_SANDBOX_SHAPE` 可配置规格 |
| Box | 远程 | — |
| Trusted Local | 本机 | 直接使用运行 Rakazo 的本机，无隔离 |

完全本地运行：Docker + 本机 LLM（通过 Pi 连接 Ollama 等），所有数据不出网络。需要更强算力或更多并发：E2B / CreateOS 按需扩展。

---

## 应用集成：四条接入路径

Bot 访问外部工具的方式有四种：

1. **Composio**：托管应用目录，预集成主流 SaaS（GitHub、Slack、Gmail 等），需要 Composio API key
2. **Pipedream Connect**：另一个托管集成平台，需要 Pipedream 项目凭据
3. **MCP 服务器**：用户可以添加任意 HTTPS MCP 端点
4. **OpenAPI 文档**：上传一份 OpenAPI JSON，Bot 可以直接调用该 API 的所有接口

连接器凭据在服务端加密存储，API 不会返回明文。

**Treg** 是第四种工具来源，使用量计费。自托管需要自己的 Treg 令牌；如果你把 Rakazo 做成托管服务对外提供，需要与 Treg 签署书面协议——这不是开源限制，是 Treg 自己的集成条款。

---

## 语音模式

Rakazo 支持语音交互，三种模式：

- **听取语音回复**：Bot 用语音回答
- **语音输入（Dictate）**：说话代替打字
- **语音通话（Call）**：像打电话一样和 Bot 实时对话

语音合成后端：ElevenLabs、OpenAI TTS、Cartesia、Fish Audio——自带 API key 接入，不绑定单一提供商。

---

## 技术栈与仓库结构

pnpm monorepo，核心模块：

```
apps/
  web        React 19 + Vite + Tailwind（主 Web 界面）
  api        Hono + oRPC（后端 API）
  worker     Graphile Worker（后台任务）
  desktop    Electron（桌面端）
  mobile     Expo（iOS/Android）
  www        公开营销网站（多语言）
packages/
  domain, contracts, persistence, adapters, UI
infra/
  Docker Compose 配置，沙箱镜像构建
```

UI 语言：英文、简体中文、德文、韩文、土耳其文、印地文、葡萄牙文（巴西）、西班牙文、俄文。

---

## 自托管方式

最快的本地部署（需要 Docker）：

```bash
mkdir -p rakazo && cd rakazo
curl -fsSLO https://raw.githubusercontent.com/elie222/rakazo/main/infra/compose/install-images.sh
bash install-images.sh
```

自动下载 Compose 文件、生成随机密钥、启动服务。打开 `http://127.0.0.1:5173`，创建账号，连接模型，建第一个 Bot。

VPS 部署（带 HTTPS）：

```bash
bash install-images.sh --prepare-only
# 编辑 .env：设置 RAKAZO_HOST=your.domain，选择 SANDBOX_PROVIDER
bash install-images.sh
```

配合 Caddy 或 Nginx 提供 HTTPS。桌面端用「连接到已有实例」模式指向 VPS 地址。

镜像支持 `linux/amd64` 和 `linux/arm64`，`edge` 标签跟主分支最新构建。

---

## 几个需要知道的点

**Beta 阶段**

README 明确标注 Beta，功能和 API 可能变化。不适合压到关键业务流程上，或做好版本锁定和降级预案。

**Computer-use 依赖视觉 LLM**

浏览器和图形桌面操作本质上是「截图 → 分析 → 点击」循环。需要支持图片输入的模型（Claude、GPT-4o、Qwen VL 等）。纯文本模型无法驱动 GUI 操作；终端和文件操作不需要视觉能力。

**模型凭据通过 Pi 管理**

Pi 是一个模型管理层，自托管时你在 Pi 里填入 API key，Bot 通过 Pi 调用不同提供商的模型。这是灵活性的来源，也意味着多一层依赖。

**Treg 工具源计量收费**

如果使用 Treg 提供的工具（非 Composio/Pipedream），是按使用量收费的独立服务。自托管场景下，自己管理 Treg token 即可；如果把 Rakazo 包装成托管服务对外售卖，需要先和 Treg 谈协议。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 3,094 |
| License | Apache 2.0 |
| 状态 | Beta |
| 客户端 | Web / Electron / Expo |
| 沙箱后端 | Docker / E2B / Daytona / CreateOS / Box / 本地 |
| 应用集成 | Composio / Pipedream / MCP / OpenAPI / Treg |
| 语音后端 | ElevenLabs / OpenAI / Cartesia / Fish Audio |
| UI 语言 | 9 种（含简体中文） |
| Node 要求 | 22.22.2+ / 24.x / 26+（不支持 23.x / 25.x） |

---

## 综合判断

Rakazo 做的事情，用一句话说清楚：把「有记忆、有电脑、有调度、有同伴」的 Agent 变成可以自托管的产品。

这不是聊天机器人，也不是一次性 Agent 脚本——Bot 是持续在线的工作者，你给它账号、工具和任务，它在后台默默跑，需要你的时候才来找你。浏览器登录状态跨会话保留这个细节，说明设计者真的把「Bot 作为长期工作者」这件事认真对待了。

3094 星 + Apache 2.0 + Inbox Zero 作者的背书，值得测试。Beta 阶段意味着接受早期不稳定性；视觉 LLM 依赖和 Treg 计量费用是用前要确认的两个隐性成本。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## Rakazo: Each Bot Gets Its Own Computer, Memory and Schedule — Open-Source Grok Bot Alternative

> **Open source for learning only**: All projects discussed are from public repositories.

---

### What "Grok Bot Alternative" Actually Means

Grok has a "Bots" feature — each bot has persistent memory, tool access, and the ability to act on X. Rakazo takes that UX pattern and makes it self-hostable and open-source: persistent bots with schedules, sandboxed computers, any LLM you choose, running on your own server.

Author: Elie, also the creator of Inbox Zero (github.com/elie222/inbox-zero).

Repo: github.com/elie222/rakazo  
**3,094 stars | Apache 2.0 | Beta | Docs: rakazo.com**

---

### Three Core Properties of a Persistent Bot

**Conversations, memory, and routines across sessions**

Standard AI chat is stateless — close the window, start over next time. Rakazo bots persistently maintain conversations, memory (extracted long-term knowledge), scheduled routines (tasks that run while you're offline), and execution history.

**A sandboxed computer**

Each bot can access a sandbox with browser, terminal, file system, and graphical desktop. The key detail: **browser login states persist across sessions**. Log in once, and the bot stays logged in — no re-authentication on every run.

Two computer types: Shared Team Computer (shared among bots) and Private Computer (isolated per bot or user).

**Bot-to-bot delegation**

Bots can delegate subtasks to peer bots or ephemeral short-lived subagents. This is the persistent multi-agent model — a network of continuously running, memory-having collaborators, not a one-shot agent chain.

---

### Sandbox Backends

| Provider | Type | Notes |
|----------|------|-------|
| Docker | Local | Default; fully offline |
| E2B | Remote | On-demand sandbox service |
| Daytona | Remote | Dev environments as a service |
| CreateOS | Remote cloud desktop | Configurable shape/rootfs |
| Box | Remote | — |
| Trusted Local | Host machine | No isolation — the Rakazo host itself |

Fully local: Docker + local LLM via Pi. Scale out: E2B/CreateOS on demand.

---

### Integrations: Four Entry Points

1. **Composio** — managed SaaS catalog (GitHub, Slack, Gmail, etc.)
2. **Pipedream Connect** — another managed integration platform
3. **MCP servers** — any HTTPS MCP endpoint
4. **OpenAPI documents** — upload JSON, bot calls all endpoints

Connector credentials are server-side encrypted; the API never returns them in plaintext.

**Treg** is a usage-metered tool source. Self-hosters supply their own Treg token. If you wrap Rakazo into a hosted service for external customers, a written agreement with Treg is required for resale.

---

### Self-Hosting

Quick local deploy (requires Docker):

```bash
mkdir -p rakazo && cd rakazo
curl -fsSLO https://raw.githubusercontent.com/elie222/rakazo/main/infra/compose/install-images.sh
bash install-images.sh
# Open http://127.0.0.1:5173, create account, connect a model, create first bot
```

VPS deployment with HTTPS: run `--prepare-only`, edit `.env` (`RAKAZO_HOST`, `SANDBOX_PROVIDER`), then rerun. Add Caddy or Nginx for HTTPS. Desktop app connects via "Existing instance."

Images: `linux/amd64` and `linux/arm64`. `edge` tag tracks main.

---

### Four Things to Know

**Beta status.** Explicitly labeled. API and features may change. Version-lock for any serious deployment.

**Computer-use requires a vision LLM.** Browser and desktop interaction is the screenshot → analyze → click loop. Needs a vision-capable model (Claude, GPT-4o, Qwen VL). Text-only models can't drive GUI; terminal and file ops don't need vision.

**Model credentials via Pi.** Pi is the model management layer — fill in API keys, bots call providers through it. Flexibility at the cost of one more dependency.

**Treg is metered.** Only relevant if you use Treg-sourced tools specifically. Self-hosted personal use: manage your own token. Reselling as a hosted service: contract required.

---

### Key Numbers

| Metric | Value |
|--------|-------|
| Stars | 3,094 |
| License | Apache 2.0 |
| Status | Beta |
| Clients | Web / Electron (desktop) / Expo (mobile) |
| Sandbox backends | Docker / E2B / Daytona / CreateOS / Box / local |
| App integrations | Composio / Pipedream / MCP / OpenAPI / Treg |
| Voice backends | ElevenLabs / OpenAI / Cartesia / Fish Audio |
| UI languages | 9 (including Simplified Chinese) |

---

### Verdict

Rakazo does one thing and takes it seriously: making "an agent with memory, a computer, a schedule, and coworkers" into a self-hostable product.

This isn't a chatbot or a one-shot agent script — bots are continuously running workers. You give them accounts, tools, and routines; they run in the background and surface when they need you. The detail of browser login states persisting across sessions shows the design is genuinely committed to the "bot as long-running worker" model.

3,094 stars + Apache 2.0 + the Inbox Zero author's track record: worth testing. Beta means tolerating early instability. Vision LLM dependency and Treg metered billing are the two hidden costs to confirm before committing.

---

> Open source for learning only. Verify license terms before commercial use.
