---
title: "claude-mem：95K 星的 Agent 跨会话记忆插件，工程拆解"
titleEn: "claude-mem: Engineering Teardown of the 95K-Star Agent Persistent Memory Plugin"
description: "thedotmack/claude-mem，Apache-2.0，95.6K stars，TypeScript。Claude Code 生态里目前最多星的第三方插件。核心机制：5 个生命周期钩子捕获 agent 行为，AI 压缩后存入本地 SQLite，下次会话通过 Chroma 向量数据库做混合检索注入上下文。3 层检索工作流（search → timeline → get_observations）实现约 10 倍 token 节省。内置中文观测模式（code--zh），支持 `<private>` 标签排除敏感内容。默认走 cmem.ai 云端存储，--provider host 可完全本地化。安装：npx claude-mem install 或 /plugin install claude-mem，支持 Claude Code / OpenCode / Codex / Grok Bot / OMP。"
descriptionEn: "thedotmack/claude-mem, Apache-2.0, 95.6K stars, TypeScript. The most-starred third-party plugin in the Claude Code ecosystem. Core mechanism: 5 lifecycle hooks capture agent behavior, AI compresses observations into local SQLite, future sessions retrieve context via Chroma hybrid search. The 3-layer retrieval workflow (search → timeline → get_observations) cuts token usage ~10x. Built-in Chinese observation mode (code--zh), `<private>` tag support. Defaults to cmem.ai cloud storage — use --provider host for fully local. Install via npx claude-mem install or /plugin install claude-mem; supports Claude Code, OpenCode, Codex, Grok Bot, OMP."
pubDate: 2026-10-04
heroImage: "../../assets/images/claude-mem-persistent-context-agent-session-memory-typescript-banner.jpg"
category: "Tech-Experiment"
tags: ["Agent记忆", "Claude Code", "开源工具", "TypeScript", "SQLite", "向量数据库", "Coding Agent"]
lang: "zh-CN"
wechatTitle: "claude-mem：95K星的Agent持久记忆插件"
wechatDigest: "95.5K星；5钩子+SQLite+Chroma；跨会话持久上下文；中文模式；10x token节省"
---

每次开新会话，coding agent 都要重新理解项目：这个变量叫什么、上次的 bug 怎么修的、有哪些约定绑的死死的……哪怕你昨天解释过，今天又要解释一遍。

claude-mem 解决的就是这个问题：把 agent 在会话里做的事情压缩成记忆，下次开会话自动注入相关上下文，让 Claude Code 记住项目历史。

GitHub: https://github.com/thedotmack/claude-mem | ⭐ 95,630 | Apache-2.0 | TypeScript

95K 星不是一般数字——这是 Claude Code 生态里目前最多星的第三方插件，Trendshift 追踪记录中持续在榜。

---

## 核心机制：5 个生命周期钩子

claude-mem 的工作方式完全依赖 Claude Code 的钩子系统，不修改模型行为，只监听 agent 的生命周期事件：

| 钩子 | 触发时机 | claude-mem 做什么 |
|------|----------|------------------|
| SessionStart | 新会话开始 | 检索并注入相关历史上下文 |
| UserPromptSubmit | 用户提交 prompt | 记录输入意图 |
| PostToolUse | 每次工具调用后 | 捕获工具使用观测（最核心） |
| Stop | agent 停止生成 | 保存当轮摘要 |
| SessionEnd | 会话结束 | 最终压缩，写入持久存储 |

捕获的内容叫 **observation**：每条包含工具名称、输入/输出摘要、时间戳、类型标签（`decision`、`bugfix`、`security_alert`、`sensitive` 等）。

数据链路：钩子捕获 → AI 压缩摘要 → 写入本地 SQLite → 向量化存入 Chroma

---

## 存储架构：SQLite + Chroma 混合

**SQLite**（`~/.claude-mem/` 目录）：
- 存 sessions、observations、summaries 三张主表
- 支持 FTS5 全文检索，关键词匹配快
- Worker 进程（Bun runtime）管理，提供本地 HTTP API + Web Viewer UI

**Chroma 向量数据库**：
- uv 包管理器安装（首次使用自动安装）
- 给 observation 做向量化，支持语义相似搜索
- 和 SQLite FTS5 做混合检索，查准率优于单一方式

**Worker 服务**：每次 Claude Code 启动时随钩子启动，监听本地端口，提供 Web Viewer（内存流实时可视化）和 REST API。

---

## 3 层检索工作流：约 10 倍 token 节省

claude-mem 提供 4 个 MCP 工具，推荐的使用模式是渐进式的 3 层工作流：

```
第 1 层：search → 紧凑索引，每条结果约 50–100 tokens
         ↓ 找到感兴趣的 ID
第 2 层：timeline → 某个 observation 的时间线上下文
         ↓ 过滤出真正相关的 ID
第 3 层：get_observations → 只取这几条的完整内容，约 500–1,000 tokens/条
```

核心逻辑：先用低成本操作定位，再对确定相关的 ID 取全文。相比直接取全文，token 消耗差约 10 倍。

```typescript
// 典型用法：
// 1. 找 authentication 相关的 bugfix
search(query="authentication bug", type="bugfix", limit=10)

// 2. 看看 ID=123 前后发生了什么
timeline(observation_id=123)

// 3. 只取确认相关的几条
get_observations(ids=[123, 456])
```

---

## 安装方式

**方式一：npx 安装（最推荐）**

```bash
npx claude-mem install
```

安装完成后，会提示在浏览器完成 email 登录（magic link，无需信用卡）。登录后会分配 memory key，解锁 claude-mem observer（官方说法：14 天免费试用，"可获得最多 100% 更多 plan 使用量"）。

跳过登录：设置 `CLAUDE_MEM_ONLINE_OPTIN=false` 或传 `--provider` 参数。

**方式二：Claude Code 插件市场**

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

重启 Claude Code 即生效。

**注意：** npm 全局安装（`npm install -g claude-mem`）只安装 SDK 库，不注册钩子，不要用这个。

**支持的 IDE / Harness：** Claude Code、OpenCode、Antigravity CLI、OMP（Oh My Pi）、Grok Bot、OpenClaw Gateway

---

## 隐私控制与本地化

**`<private>` 标签**：在 prompt 里用 `<private>...</private>` 包住的内容，不会进入 observation 存储。适合包含密钥、个人信息的指令。

**完全本地化**：如果不想走 cmem.ai 云端，装完后选 `--provider host`，或者在 `~/.claude-mem/settings.json` 里手动配置使用 Anthropic plan / 自己的 OpenRouter 或 Gemini key 做压缩。

**中文观测模式**：修改 `~/.claude-mem/settings.json`：

```json
{
  "CLAUDE_MEM_MODE": "code--zh"
}
```

中文模式内置，observations 和摘要用中文生成，无需额外安装。重启 Claude Code 生效。

---

## 局限与注意

**默认走云端**：默认安装会推你登录 cmem.ai，14 天后如不订阅，记忆压缩回退到 Anthropic plan 额度。如果只想本地跑，安装时加 `--provider host` 或 `CLAUDE_MEM_ONLINE_OPTIN=false`。

**依赖链**：需要 Node.js ≥ 20、Bun（自动安装）、uv（自动安装，用于 Chroma）。首次在新机器装，依赖链比较长，偶有环境冲突。

**Chroma 版本敏感**：向量搜索依赖 uv 管理的 Chroma，Python 环境变化可能导致 Chroma 启动失败——遇到检索异常先排查 `uv` 和 Chroma 是否正常。

**不是所有 harness 都一样**：Grok Bot 等无钩子支持的 harness 走日志监听，覆盖率和钩子模式有差距。

**版本号**：v13.29.0，不是语义化版本——主版本号不代表破坏性变更，只是迭代计数。

---

## 适合谁用

**适合**：在同一个项目上长期工作、每天开多个 Claude Code / OpenCode / Codex 会话的开发者。代码库约定多、历史 bug 多、agent 经常需要理解"之前做过什么"的场景效果最明显。

**有顾虑时**：选 `--provider host` 完全本地，观测数据不出机器。企业内网或对隐私要求高的项目，在确认数据流之前不要装默认版本。

**不需要**：偶尔用 Claude Code 做一次性任务的场景——记忆积累需要持续使用才有价值。

---

> Apache-2.0 开源，商业使用无限制。默认安装含 cmem.ai 账号和 14 天云端试用，使用前请确认数据流向。开源仅供学习参考。

---

<!--EN-->

## claude-mem: Engineering Teardown of the 95K-Star Claude Code Memory Plugin

Every new session, your coding agent starts from zero: what this variable means, how that bug was fixed last week, which conventions are locked in. Even if you explained it yesterday, you explain it again today.

claude-mem solves this: compresses what the agent did in a session into memory, automatically injects relevant context into future sessions.

GitHub: https://github.com/thedotmack/claude-mem | ⭐ 95,630 | Apache-2.0 | TypeScript

95K stars is not a typical number — this is the most-starred third-party plugin in the Claude Code ecosystem, consistently tracked on Trendshift.

---

### Core Mechanism: 5 Lifecycle Hooks

claude-mem works entirely via Claude Code's hook system — it doesn't modify model behavior, only listens to lifecycle events:

| Hook | Fires When | What claude-mem Does |
|------|------------|----------------------|
| SessionStart | New session starts | Retrieves + injects relevant past context |
| UserPromptSubmit | User submits a prompt | Records intent |
| PostToolUse | After each tool call | Captures tool-use observations (the core) |
| Stop | Agent stops generating | Saves turn summary |
| SessionEnd | Session ends | Final compression, writes to persistent storage |

Each captured record is an **observation**: tool name, input/output summary, timestamp, type tag (`decision`, `bugfix`, `security_alert`, `sensitive`, etc.).

Data flow: hooks capture → AI compresses → SQLite storage → vectors in Chroma

---

### Storage: SQLite + Chroma Hybrid

**SQLite** (`~/.claude-mem/`): three main tables for sessions, observations, and summaries. FTS5 full-text search for keyword matching. Managed by a Worker process (Bun runtime) that exposes a local HTTP API and a web viewer UI.

**Chroma vector database**: installed via uv (auto-installed on first use). Semantic similarity search via embedding. Combined with SQLite FTS5 for hybrid retrieval — better precision than either alone.

---

### 3-Layer Retrieval Workflow: ~10x Token Savings

claude-mem provides 4 MCP tools. The recommended pattern is progressive:

```
Layer 1: search → compact index, ~50–100 tokens/result
          ↓ identify interesting IDs
Layer 2: timeline → chronological context around specific IDs
          ↓ filter to truly relevant IDs
Layer 3: get_observations → full details for those IDs only, ~500–1,000 tokens/result
```

Fetch only what you've already confirmed is relevant. Token cost difference vs. fetching everything upfront: roughly 10x.

```typescript
search(query="authentication bug", type="bugfix", limit=10)
timeline(observation_id=123)
get_observations(ids=[123, 456])
```

---

### Installation

**Primary method:**

```bash
npx claude-mem install
```

Post-install, the installer prompts for browser sign-in to cmem.ai (email magic link, no card). This provisions a memory key and enables the claude-mem observer — 14-day free trial. After trial, falls back to your Anthropic plan unless you subscribe.

Skip sign-in: `--provider host`, `CLAUDE_MEM_ONLINE_OPTIN=false`, or run in CI.

**From Claude Code plugin marketplace:**

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Restart Claude Code. Note: `npm install -g claude-mem` installs the SDK library only — it does not register hooks. Always use `npx claude-mem install`.

**Supported harnesses:** Claude Code, OpenCode, Antigravity CLI, OMP, Grok Bot, OpenClaw Gateway.

---

### Privacy and Local Mode

**`<private>` tags**: wrap any prompt content in `<private>...</private>` to exclude it from observation storage — useful for instructions containing credentials or personal information.

**Fully local**: pass `--provider host` at install time, or configure `~/.claude-mem/settings.json` to use your Anthropic plan / OpenRouter / Gemini key for compression. Observations stay on-device.

**Chinese observation mode**: set `"CLAUDE_MEM_MODE": "code--zh"` in `~/.claude-mem/settings.json`. Built-in — no additional install. Observations and summaries generate in Chinese. Restart Claude Code to apply.

---

### Constraints

**Defaults to cloud**: the default install prompts for a cmem.ai account. After the 14-day trial, memory compression charges against Anthropic plan unless you subscribe. For fully local, use `--provider host` at install.

**Dependency chain**: Node.js ≥ 20, Bun (auto-installed), uv + Chroma (auto-installed). The auto-install chain is generally smooth but can conflict with non-standard Python/Node environments.

**Chroma sensitivity**: vector search depends on uv-managed Chroma. Python environment changes may cause Chroma startup failures — if retrieval breaks, check `uv` and Chroma health first.

**Harness coverage varies**: Grok Bot (no native hooks) uses log-file watching — coverage isn't equivalent to hook-based harnesses.

---

### Who Should Use It

**Good fit**: developers who work on the same project daily across many sessions, accumulate project conventions, and regularly want the agent to remember past decisions and bugfixes.

**Privacy-first**: use `--provider host` at install for fully local. Verify data flow before deploying on corporate networks or sensitive projects.

**Skip it**: one-off or infrequent Claude Code use — memory accumulation only pays off with sustained usage.

---

> Apache-2.0, no commercial restrictions. Default install includes a cmem.ai account and 14-day cloud trial — verify data flow before production use. For technical reference only.
