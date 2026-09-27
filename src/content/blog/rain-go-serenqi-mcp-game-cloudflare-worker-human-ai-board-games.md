---
title: "rain-go（西窗）：人类与 AI 同桌对弈的 MCP 棋牌平台，全栈 Cloudflare 自托管"
description: "SerenQi/rain-go，MIT TypeScript，昨天开源。MCP 协议让 AI 助手成为真正的棋牌玩家，与人类同桌博弈。后端 Cloudflare Worker + Durable Objects，前端 React Vite，服务端强制隐牌隔离。支持 10 款棋牌，pnpm deploy 一键上线。"
pubDate: 2026-09-27
heroImage: "../../assets/images/rain-go-serenqi-mcp-game-cloudflare-worker-human-ai-board-games-banner.jpg"
category: "Tech-Experiment"
tags: ["MCP", "AI Agent", "Cloudflare Worker", "游戏", "开源拆解", "TypeScript"]
lang: "zh-CN"
wechatTitle: "rain-go：人类+AI同桌对弈的MCP棋牌平台"
wechatDigest: "MIT；全栈自托管Cloudflare；10款棋牌；MCP协议让AI成为真实玩家坐同一张桌"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 项目背景

**SerenQi/rain-go**（GitHub：github.com/SerenQi/rain-go）——MIT 许可证，TypeScript，2026 年 9 月 26 日才开源，目前 5 stars。

项目名「西窗」来自李商隐的《夜雨寄北》：「何当共剪西窗烛，却话巴山夜雨时」。英文名 rain-go，取的是「夜雨·棋」的双关。

一句话定位：**让 AI 助手通过 MCP 协议成为棋牌桌上的真正玩家，与人类实时对弈**。不是 AI 陪你下棋的 demo，而是支持人类 + AI 混合多人局的全栈平台，服务端强制隐牌隔离，每个玩家只能看到自己该看到的信息。

---

## 回答第一个问题：服务端是否开源？

**全套开源，MIT monorepo**。仓库结构：

```
apps/worker   ← 服务端：Cloudflare Worker（Hono 框架 + Durable Objects）
apps/web      ← 客户端：React + Vite + Tailwind v4 + Motion
packages/engine  ← 共享游戏规则（纯函数，无副作用）
```

**没有闭源服务器，没有 SaaS 依赖**。唯一的外部依赖是一个 Cloudflare 账号（免费套餐足够）。你自己部署，你自己拥有。

---

## 架构：Cloudflare Worker + Durable Objects

这个选型很有意思。

**Cloudflare Worker**（后端）：无状态执行层，用 Hono 框架处理 HTTP 路由。MCP 端点是 Streamable HTTP，符合最新 MCP 规范。

**Durable Objects**（状态层）：每一局游戏对应一个 Durable Object 实例。这是解决多人实时同步的核心——所有玩家（人类浏览器 + AI MCP 客户端）的操作都通过同一个 DO 实例序列化执行，保证状态一致性，不需要外部 Redis 或数据库。

**隐牌隔离**（安全层）：服务端按 seat token 筛选信息再推送，每个玩家只接收自己视角的数据。这对扑克类游戏（斗地主、德州扑克）尤为关键——AI 也只看自己的牌，无法作弊。

**前端**（React + Vite + Tailwind v4）：共享 `packages/engine` 里的纯函数规则模块，所以棋盘渲染逻辑与服务端判局逻辑完全对齐。

---

## MCP 集成：AI 如何真正「坐下来」打牌

这是 rain-go 最有意思的部分。

每个游戏房间生成两类 MCP URL：
- `/mcp/<ACCESS_TOKEN>` — 房主 AI（有创建房间权限）
- `/mcp/seat/<seat-token>` — 座位 AI（只控制该座位的操作）

AI 助手（Claude / GPT / 任意 MCP 客户端）调用工具：

```
new_game       创建新游戏房间，选择游戏类型
play           执行落子/出牌动作
wait_for_opponent  等待其他玩家加入或操作
get_game_state 查询当前棋盘/牌局状态
```

人类玩家在 Web 界面操作，AI 通过 MCP 工具调用操作——两者通过同一个 Durable Object 同步，互相「看到」对方的动作（但隐牌内容仍然隔离）。

---

## 支持 10 款棋牌游戏

| 类型 | 游戏 |
|------|------|
| 棋盘类 | 围棋、五子棋、黑白棋、国际象棋、中国象棋 |
| 扑克类 | 德州扑克、跑得快、斗地主 |
| 桌游类 | 大富翁（Monopoly）、飞行棋 |

游戏规则放在 `packages/engine` 里，每款游戏是独立的纯函数模块，互不干扰，也方便后续增加新游戏。

---

## 部署：真的一条命令

```bash
# 一次性配置（约 2 分钟）
npx wrangler login
cd apps/worker && npx wrangler secret put ACCESS_TOKEN
cd ../..

# 之后每次部署
pnpm deploy
```

`pnpm deploy` 从根目录运行，构建前端，同时部署 Worker 和静态资源，得到一个 `*.workers.dev` URL。加自定义域名在 Cloudflare 面板或 `wrangler.jsonc` 里配。

本地开发：`pnpm install && pnpm dev`，跑在 `localhost:8787`。

---

## 适合什么场景

**适合**：
- 想给 Claude Code / MCP 客户端搭一个真正的博弈场景做能力测试
- 研究 AI 游戏策略（这是真实对弈，不是模拟）
- Cloudflare Worker 全栈架构学习（Durable Objects 状态管理是教科书级别示例）
- 给 AI 朋友的趣味项目（字面意义上的「和 AI 下棋」）

**注意**：
- 项目昨天刚开源，生产成熟度低，issue 还空着
- 10 款游戏的规则完整性和边界情况（悔棋、断线重连、超时处理）需要自行评估
- Cloudflare 免费套餐有请求次数和 CPU 时间限制，高并发长局面可能触发

---

## 关键数字

| 指标 | 值 |
|------|-----|
| Stars | 5 |
| License | MIT |
| 语言 | TypeScript |
| 开源时间 | 2026-09-26（昨天） |
| 后端 | Cloudflare Worker + Durable Objects |
| 前端 | React + Vite + Tailwind v4 |
| 支持游戏数 | 10 |
| 外部依赖 | Cloudflare 账号（免费套餐可用） |

---

## 综合判断

架构选型干净，Durable Objects 解决多人实时同步的思路是对的，服务端隐牌隔离让 AI 和人类站在公平起跑线上，MCP 集成思路新颖。项目昨天才开源、5 个 star，谈不上生产可用，但代码结构清晰，Cloudflare 全栈一键部署降低了自托管门槛。

如果你想搭一个「真正能和 Claude 下棋」的游乐场，这是目前最直接的方案。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## rain-go (West Window): MCP Game Platform for Humans and AI at the Same Board

> **Open source for learning only**: Analysis is for technical research purposes only.

---

### What It Is

**SerenQi/rain-go** (github.com/SerenQi/rain-go) — MIT, TypeScript, open-sourced September 26, 2026 (yesterday). Currently 5 stars.

Named after a Li Shangyin poem: "When will we trim candles together by the west window, and talk of the night I wrote you from these rainy mountains?" Rain-go is a multiplayer board/card game platform where human players (via web browser) and AI assistants (via MCP protocol) sit at the same table and play together.

---

### Is the Server Open Source? Yes, Fully.

MIT monorepo:

```
apps/worker    ← server: Cloudflare Worker (Hono + Durable Objects)
apps/web       ← client: React + Vite + Tailwind v4
packages/engine ← shared game rules (pure functions)
```

No closed server. No SaaS dependency. Only dependency: a Cloudflare account (free tier works).

---

### Architecture: Cloudflare Worker + Durable Objects

**Worker**: Stateless execution layer using Hono framework. MCP endpoint is Streamable HTTP per current MCP spec.

**Durable Objects**: Each game session gets its own DO instance. All player actions (human browser + AI MCP client) are serialized through the same DO — consistent state without external Redis or DB.

**Server-side hidden-hand isolation**: Each player's MCP seat token filters the game state before pushing it. In poker games (Texas Hold'em, Landlord), the AI truly only sees its own cards — no cheating possible even in principle.

---

### MCP Integration: How AI "Sits Down" to Play

Each game room generates two types of MCP URLs:
- `/mcp/<ACCESS_TOKEN>` — host AI (can create rooms)
- `/mcp/seat/<seat-token>` — seat AI (controls one seat)

AI assistants call tools: `new_game`, `play`, `wait_for_opponent`, `get_game_state`. Humans play on the web UI. Both sync through the same Durable Object.

---

### 10 Games Supported

Board games (Go, Gomoku, Othello, Chess, Chinese Chess), card games (Texas Hold'em, Running Fast, Landlord), and tabletop games (Monopoly, Flying Chess).

Game rules live in `packages/engine` as independent pure-function modules.

---

### Deploy

```bash
npx wrangler login
cd apps/worker && npx wrangler secret put ACCESS_TOKEN
cd ../.. && pnpm deploy
```

Gets you a `*.workers.dev` URL. Local dev: `pnpm install && pnpm dev` on localhost:8787.

---

### Verdict

Clean architecture, correct use of Durable Objects for real-time multiplayer state, server-side fairness for AI players, novel MCP integration. Opened yesterday with 5 stars — not production-ready, but the clearest existing path to "play Go with Claude."

---

> Open source for learning only.
