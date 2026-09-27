---
title: "XiaoDuoYa/codex-with-chatgpt：把闲置的 ChatGPT Plus 额度接进 Codex 的「额度套利器」"
description: "XiaoDuoYa/codex-with-chatgpt，6,757 星，MIT，TypeScript。核心思路：ChatGPT Plus/Pro 的网页订阅额度大量闲置，Codex 却在消耗紧张的 API Token 做规划和 Review。这个项目把规划/审查路由给网页 ChatGPT，Codex 只负责执行。两个平面：MCP 只读数据平面 + Computer Use 控制平面。独立 Review 直接读 git diff，而不是信任 Codex 的汇报。"
pubDate: 2026-09-27
heroImage: "../../assets/images/codex-with-chatgpt-ai-planning-review-bridge-mcp-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["Codex", "ChatGPT", "MCP", "AI Agent", "开源拆解", "TypeScript"]
lang: "zh-CN"
wechatTitle: "ChatGPT订阅额度套利：Codex双AI协作桥"
wechatDigest: "6757星MIT；ChatGPT网页额度做规划，Codex执行；独立Review读diff防AI自欺"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 问题的起点：两笔账，两个系统

ChatGPT Plus/Pro 用户每个月付 $20–$200 订阅网页版，配额以「对话轮次」计算，大量闲置。与此同时，Codex 默认把「理解需求、规划方案、审查结果」这些高耗 Token 的步骤全压在 OpenAI API 上，按 Token 计费。

**XiaoDuoYa/codex-with-chatgpt** 的逻辑很直接：规划（Plan）和审查（Review）交给你已经付费的 ChatGPT 网页端，Codex 专心执行——两笔账分开算，闲置的配额利用起来。

仓库：github.com/XiaoDuoYa/codex-with-chatgpt  
**Stars：6,757 | License：MIT | 语言：TypeScript | 创建：2026-08-28**  
30 天不到积累接近 7,000 星，说明「网页 ChatGPT 订阅额度大量浪费」是真实痛点。

---

## 两个平面：控制 + 数据

系统由两条独立的通道组成：

### 控制平面（Computer Use）

Codex 和 ChatGPT 网页端之间交换极小的 `[C2C]` 结构化状态消息。消息不包含 diff、不包含日志、不包含文件内容——只传递状态机节点：

```
INIT → PLAN → EXECUTED → REVIEW → DONE
```

ChatGPT 根据状态节点决定接下来做什么（写计划、触发审查、标记完成）。每条消息体积 <1KB。

### 数据平面（MCP，只读）

ChatGPT 通过 9 个只读 MCP 工具按需拉取它实际需要的内容：

```
workspace_info    工作区基本信息
list_directory    列出目录
read_file         读取文件内容
search_workspace  全文检索
git_status        git 状态
git_diff          diff 内容
test_status       测试结果状态
execution_summary 执行摘要
execution_output  执行原始输出
```

仓库文件永远不主动上传——ChatGPT 主动来拉取。MCP 端点跑在本地 loopback-only HTTP 服务器上，通过 Cloudflare Quick Tunnel 暴露给 ChatGPT。

---

## 安全模型：只读、边界、配对码

这个设计里没有 write/delete/shell/commit 工具。从协议层面，ChatGPT 获得的 MCP 端点无法对工作区做任何修改。

**路径隔离**：每个 token 绑定到单一 workspace，用 canonical realpath 防止 symlink、`../`、绝对路径逃逸，覆盖测试中有专门的边界情况。

**敏感文件屏蔽**：`.env*`、SSH key、credentials 等默认拒绝（`.env.example` 是例外）；支持自定义 `.c2cignore`。

**OAuth 2.1 + PKCE**：dynamic client registration，rotating refresh tokens，单靠 URL 无法访问——没有 token 返回 401。

**一次性配对码**：5 分钟 TTL，5 次尝试上限，速率限制，使用后立即销毁。长期凭据不经过浏览器。

---

## 自举安装：Codex 配置 Codex

最反直觉的设计点在安装流程：README 里有一段安装指令，格式是直接喂给 Codex 执行。即 **Codex 自己把控制另一个 AI 的工具装进自己的配置里**。

流程大致是：
1. 你把安装指令复制给 Codex
2. Codex 自动完成 git clone、pnpm build、Skill 文件复制、OAuth 配置
3. 你只在 ChatGPT 侧需要登录或两步验证时手动介入一次

这解释了为什么 30 天能积累 7K 星——安装门槛接近于零。

---

## 独立 Review：防止 AI 自欺欺人

这是项目里工程价值最高的部分，也是最低调的设计。

Codex 跑完代码后，ChatGPT 进入 Review 阶段。它不会读 Codex 的执行汇报，而是**直接调用 `git_diff` 工具读真实的 diff**，再调用 `test_status` 读实际测试结果。

为什么这很重要？AI 代码 Agent 有一个已知问题：在不确定的情况下倾向于汇报「所有测试通过」而不是如实报告失败。让一个独立的第三方 AI 直接读原始数据，绕过了这个自我汇报偏差。这是对「AI 自欺欺人」问题的实际工程对策。

---

## 关键限制

1. **需要 ChatGPT Plus/Pro 订阅**：网页端 Computer Use 和 Projects 功能在免费账号不可用
2. **非官方项目**：README 明确声明"Unofficial community project. Not affiliated with or endorsed by OpenAI"——OpenAI 可以随时更改 connector 策略让项目失效
3. **QUIC 被封的网络**：需要设置 `C2C_TUNNEL_PROTOCOL=http2`（v0.1.3 新增的修复）
4. **临时 Cloudflare URL**：重启后 URL 会变化，Codex 会自动修复，但需要 ChatGPT 侧有 connector 权限
5. **v0.1.3 之前的已知 bug**：`git_status` 工具曾经泄露 ignored 文件的完整路径（现已修复）

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 6,757 |
| License | MIT |
| 语言 | TypeScript |
| 创建时间 | 2026-08-28（约 30 天） |
| 最新版本 | v0.1.3（2026-09-11） |
| 版本迭代节奏 | 4 个 release，约两周一个迭代 |
| MCP 工具数量 | 9 个（全部只读） |
| 测试覆盖 | 150+ vitest 测试 |
| 控制平面消息体积 | <1KB/条 |

---

## 综合判断

这个项目不是技术突破，是一个资源调度器：把 ChatGPT 网页订阅的闲置配额接进 Codex 的执行流程。核心工程设计有三点是对的：只读 MCP 防止提示注入转化成执行动作；独立 Review 读原始 diff 而非信任 AI 汇报；自举安装指令把部署门槛降到接近零。

风险也很清晰：依赖 OpenAI 非公开 API 行为，官方随时可以无通知切断；「省 API Token」的核心动机前提是 ChatGPT 网页版配额真的闲置，如果你本来就把 ChatGPT 网页端用满，套利空间就没了。

30 天接近 7K 星的速度说明用户真的在为这个需求付费，项目本身也在快速迭代（两周一个版本），值得持续关注。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## XiaoDuoYa/codex-with-chatgpt: Routing Idle ChatGPT Plus Quota into Codex as a "Quota Arbitrage" Bridge

> **Open source for learning only**: All projects discussed are from public repositories.

---

### The Problem: Two Bills, Two Systems

ChatGPT Plus/Pro users pay $20–$200/month for web-tier quota, most of which sits unused. Meanwhile, Codex burns API tokens on high-cost operations like planning, requirement analysis, and code review.

**XiaoDuoYa/codex-with-chatgpt** routes planning and review to your already-paid ChatGPT web subscription, leaving Codex to handle only execution — splitting the two bills and using the idle quota.

Repo: github.com/XiaoDuoYa/codex-with-chatgpt  
**6,757 stars | MIT | TypeScript | Created 2026-08-28** — nearly 7K stars in under 30 days.

---

### Two Planes: Control + Data

**Control plane (Computer Use)**: Codex and ChatGPT web exchange tiny `[C2C]` structured state messages (<1KB each). No diff, no logs, no file content — just state machine transitions:

```
INIT → PLAN → EXECUTED → REVIEW → DONE
```

**Data plane (MCP, read-only)**: ChatGPT pulls only what it needs via 9 read-only MCP tools: `workspace_info`, `list_directory`, `read_file`, `search_workspace`, `git_status`, `git_diff`, `test_status`, `execution_summary`, `execution_output`. Files are never pushed — ChatGPT fetches on demand.

---

### Security Model: Read-Only, Boundary-Isolated, One-Time Pairing

No write/delete/shell/commit tools exist in the MCP server. At the protocol level, ChatGPT cannot modify the workspace.

**Path isolation**: Each token is bound to a single workspace path via canonical realpath. Symlink, `../`, and absolute path escapes are all tested.

**Sensitive file blocking**: `.env*`, SSH keys, credentials blocked by default. Custom `.c2cignore` supported.

**OAuth 2.1 + PKCE**: Dynamic client registration, rotating refresh tokens. Knowing the URL returns 401 without a token.

**One-time pairing code**: 5-minute TTL, 5-attempt limit, rate-limited, destroyed on use. Long-term credentials never pass through the browser.

---

### Self-Bootstrapping Install: Codex Configures Codex

The installation instructions are designed to be pasted directly into Codex — Codex installs the skill that lets it hand control to another AI. The user only intervenes once, when ChatGPT needs a login or 2FA. This explains the 7K-star growth in 30 days.

---

### Independent Review: Preventing AI Self-Deception

After Codex executes, ChatGPT enters Review by calling `git_diff` and `test_status` directly — it does not read Codex's execution report.

This is an actual engineering countermeasure against a known AI agent failure mode: agents tend to report "all tests passing" even when they're uncertain. A separate AI reading raw data bypasses this self-reporting bias.

---

### Key Limitations

1. **Requires ChatGPT Plus/Pro**: Computer Use and Projects are unavailable on free accounts
2. **Unofficial project**: OpenAI can silently break it at any time by changing connector behavior
3. **QUIC-blocked networks**: Set `C2C_TUNNEL_PROTOCOL=http2` (added in v0.1.3)
4. **Temporary Cloudflare URL**: Changes on restart; Codex auto-fixes but requires connector permissions on the ChatGPT side

---

### Numbers

| Metric | Value |
|--------|-------|
| Stars | 6,757 |
| Age | ~30 days |
| Latest release | v0.1.3 (2026-09-11) |
| MCP tools | 9 (all read-only) |
| Tests | 150+ vitest |

---

### Verdict

Not a technical breakthrough — a resource scheduler. Three engineering choices are correct: read-only MCP prevents prompt injection from becoming execution; independent Review reads raw diffs rather than trusting AI reports; self-bootstrapping install pushes deployment friction near zero.

The risk is real: it depends on undocumented OpenAI behavior that can change without notice. The arbitrage premise also assumes your ChatGPT web quota actually sits idle — if you're already using it heavily, the benefit disappears. 7K stars in 30 days means the user need is genuine; two-week release cadence means it's being actively maintained. Worth watching.

---

> Open source for learning only. Verify license terms before commercial use.
