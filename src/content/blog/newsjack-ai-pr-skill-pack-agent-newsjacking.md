---
title: "Newsjack：把 AI Agent 变成 PR 团队的开源技能包，30+ 技能覆盖新闻蹭热、危机公关、AI 搜索可见度"
titleEn: "Newsjack: Open-Source Skill Pack That Turns Your AI Agent into a PR Team — 30+ Skills for Newsjacking, Crisis PR, and AI Search Visibility"
description: "elvisun/newsjack，1,257 stars，MIT。Go CLI + Markdown skill 文件格式，安装后 Claude Code/Codex 等 Agent 获得 30+ PR 专业技能：新闻监控与蹭热点检测、pitch 邮件撰写、记者匹配、危机公关保持声明、AEO/GEO AI 搜索引擎可见度优化。Elvis Sun + PR 专家 Carly Martinetti 共同开发，配套 Medialyst 商业记者数据库服务。本地 Agent 全功能，claude.ai 网页版降级运行。"
descriptionEn: "elvisun/newsjack — 1,257 stars, MIT. Go CLI + Markdown skill files. After installation, Claude Code, Codex, and other AI agents gain 30+ PR professional skills: news monitoring and newsjacking detection, pitch writing, journalist matching, crisis PR holding statements, and AEO/GEO AI search visibility optimization. Built by Elvis Sun and PR professional Carly Martinetti, with a companion Medialyst journalist database service. Full functionality on local agents; web-based claude.ai runs in degraded mode."
pubDate: 2026-09-21
heroImage: "../../assets/images/newsjack-ai-pr-skill-pack-agent-newsjacking-banner.jpg"
category: "Tech-Experiment"
tags: ["ai-agent", "open-source", "pr", "marketing", "skill-pack", "newsjacking", "claude-code"]
lang: zh-CN
---

2026 年 5 月，Elvis Sun 和 PR 专家 Carly Martinetti 发布了 `elvisun/newsjack`，一个给 AI Agent 用的开源公关技能包。截至调研时 1,257 stars，活跃维护。核心思路很直接：把一个普通的 AI Agent 改造成一支具备完整 PR 能力的团队。

**GitHub**：github.com/elvisun/newsjack | **官网**：newsjack.sh | **License**：MIT | **Stars**：1,257+

---

## 为什么是这个时机

传统 PR 工作的核心难点不是"写"，而是"判断"：这条新闻值不值得蹭？这个角度会不会吓到记者？这份 pitch 主题行够不够吸引人？我们在 AI 搜索里的曝光足不足？

这些判断过去需要有行业经验的 PR 专业人士。Newsjack 的思路是：把这些判断规则显式地写成 Skill 文件，让 Agent 执行——不是用 AI 生成模板文字，而是用 AI 执行一套有专业逻辑的 PR 工作流。

---

## 安装

```bash
# macOS / Linux 一行安装
curl -fsSL newsjack.sh | bash

# 或 npm 安装
npm i -g newsjack@latest
```

安装后：`~/.newsjack/bin/newsjack`（CLI）和 `~/.newsjack/newsjack/`（技能包）

**claude.ai 网页版**：Customize → Personal plugins → Create plugin，填入 `elvisun/newsjack`，连接 Medialyst OAuth 解锁记者数据库功能。

---

## 4 个模块，30+ 技能

### 模块一：侦测 Detect

发现真正值得发力的新闻机会，过滤噪音：

| 技能 | 作用 |
|------|------|
| `/newsjack-monitor-setup` | 建立监控 profile（话题、竞争对手、媒体人） |
| `/newsjack-detector` | 扫描新闻，找有发言资格且热度未消的机会，可推送 Slack |
| `/news-search` | 按时间、来源检索竞争对手/行业动态 |
| `/story-origin-check` | 核查一条新闻是否还"新鲜"，避免蹭过期新闻 |
| `/relevance-coarse-filter` | 低成本粗筛，过滤无关废料 |
| `/newsjack-triage` | 按发言资格路由：现在 pitch / 跟踪 / 仅记录大新闻 |
| `/coverage-tracker-setup` & `/coverage-tracker` | 类 Google Alerts 关键词追踪 + LLM 精筛 |

### 模块二：行动 Act

把信号转化为实际产出物：

| 技能 | 作用 |
|------|------|
| `/angle-generator` | 一条新闻衍生多个不同记者视角的 hook |
| `/headline-generator` | 标题 + pitch 邮件主题行 |
| `/meanest-editor` | 用资深编辑标准狠批你的 pitch（让它更好再发出去） |
| `/crisis-holding` | 危机时的保持声明、记者 Q&A 姿态（内置法律顾问审批门）|
| `/reactive-comment` | 处理来访媒体问询，只草拟真正合适的回应 |
| `/fact-check` | 逐条提取声明并核查，标出存疑的部分 |
| `/journalist-fit-check` | 这个记者真的会感兴趣吗，还是发出去只会被拉黑？ |
| `/same-outlet-ranker` | 同一媒体多位记者，只联系最合适的一位 |
| `/voice-extractor` | 提取真实写作风格，消除 AI 腔 |
| `/find-journalists` | 构建精准媒体列表（需 Medialyst 服务）|
| `/press-clip` | 把在线文章截成带原版 Logo 的 PDF 剪报（仅本地 Agent）|

### 模块三：战略 Strategize

帮创始人和非 PR 专业人士建立正确的 PR 体系：

| 技能 | 作用 |
|------|------|
| `/pr-strategist` | 创始人入门向导：受众→定位→新闻钩→节奏 |
| `/pr-calendar` | 规划 6 个月 PR 内容日历，含历年报道规律分析 |
| `/newsworthiness-check` | 冷静评估一个选题是否真的值得发 |

### 模块四：AI 搜索可见度 AEO/GEO

这是 newsjack 里最有前瞻性的一块——专门针对 AI 搜索引擎（Perplexity、ChatGPT Search、Google AI Mode 等）的内容可见度优化：

| 技能 | 作用 |
|------|------|
| `/ai-visibility-writing` | 改写内容，让 AI 搜索引擎能识别并引用 |
| `/build-ai-visibility-panel` | 端到端面板搭建，驱动以下 6 个子技能 |
| `/icp-evidence-analysis` | 理想客户画像与市场证据分析 |
| `/buyer-job-intent-analysis` | 买家意图与使用场景分析 |
| `/prompt-proximity-architecture` | 设计让 AI 引用你内容的提示词架构 |
| `/realistic-prompt-generation` | 生成真实用户查询场景 |
| `/prompt-set-qa` | 验证 prompt set 覆盖率和质量 |
| `/ai-visibility-panel-design` | 设计 AI 可见度追踪看板 |

---

## 技术架构

技术选型刻意保持轻量：

```
Go CLI 二进制（~/.newsjack/bin/newsjack）
└── Markdown Skill 文件（任何 Agent 平台可读）
    ├── /newsjack-detector.md
    ├── /angle-generator.md
    ├── /crisis-holding.md
    └── ...（30+ 技能）
```

- **Go CLI**：负责安装、自动更新（每次运行前拉最新 Release，`NEWSJACK_AUTO_UPDATE=0` 可关闭）、Slack 通知推送
- **Skill 文件**：纯 Markdown，与 Agent 平台解耦，Claude Code / Codex / Hermes / Claude.ai 都可读
- **可选后端**：Medialyst API（记者数据库、新闻检索），需注册账号，未订阅时部分技能降级运行
- **依赖项**：`/press-clip` 功能需要 Playwright / 真实 Chrome 浏览器（仅本地 Agent）

---

## 平台兼容矩阵

| 平台 | 支持程度 |
|------|---------|
| Claude Code / Codex / Hermes | ✅ 全功能 |
| claude.ai / Claude Cowork | ⚠️ 降级（无跨会话状态，monitor-setup 等不可用）|
| ChatGPT 企业版 Skills beta | ⚠️ 降级（同上）|
| 消费级 ChatGPT | ❌ 基本不可用 |

**关键限制**：`/newsjack-monitor-setup`、`/coverage-tracker-setup`、`/press-clip` 需要持久化状态，必须跑本地 Agent，在 claude.ai 网页版会退化为一次性无记忆模式。

---

## 两位作者的背景

**Elvis Sun**（开发者）：加拿大滑铁卢，51 个公开仓库，同时维护 `hermes-agent`（个人 AI Agent 框架）和 `loss-function-development`（175 stars）。技术侧主导。

**Carly Martinetti**（PR 专家）：X @prcarly，技能内容的主要设计者，PR 工作流逻辑的来源。这套技能包的差异化在于 Carly 把多年 PR 经验提炼进了 Markdown prompt 文件，不是随便一个技术人员写的"AI 写 PR 邮件"模板。

---

## 配套商业服务：Medialyst

免费版 newsjack 已经可以运行大部分技能。付费的 Medialyst（medialyst.ai）提供：

- 真实记者数据库（`/find-journalists` 完整版）
- 历史报道检索（`/pr-calendar` 有规律分析）
- 新闻 API（`/newsjack-detector` 更准确的热度判断）

项目本身 MIT 开源，Medialyst 是独立的商业服务，非必须。

---

## 不足之处

**1. 本地 Agent 才能发挥全部价值**：最有用的监控、追踪、press-clip 功能都需要持久化状态，claude.ai 网页版用不了。如果你主要用 claude.ai 而不是本地 Claude Code，功能会打折扣。

**2. 记者数据库付费**：`/find-journalists` 的完整功能依赖 Medialyst 订阅，免费版构建精准媒体列表的效果有限。

**3. 年轻项目**：2026 年 5 月创建，社区体量中等（1257 stars / 111 forks），未经大量生产环境验证。

**4. Windows 支持不佳**：curl 一键安装不支持 Windows，需绕行。

**5. AEO/GEO 技能的测量困难**：AI 搜索可见度本质上很难直接量化，这 6 个技能的效果主观性强，缺乏标准化验证指标。

---

## 怎么看这件事

Newsjack 有一个值得关注的设计选择：不试图做 PR SaaS，而是把专业 PR 逻辑封装成 Agent 技能文件。这条路成本极低（Go CLI + Markdown），但依赖你的 Agent 有足够的上下文理解能力——Claude Code 或 Codex 在本地跑，效果比在 claude.ai 网页版好很多。

AEO/GEO 模块是最有差异化的部分。随着 Perplexity、ChatGPT Search、Google AI Mode 成为真实流量入口，"内容能不能被 AI 搜索引擎引用"会越来越重要。Newsjack 专门为此建了一套工作流，是目前 AI 搜索可见度优化领域少有的结构化方案。

适合用户：创业公司创始人、小型 PR 团队、独立运营者——需要 PR 专业能力但支付不起专职 PR 人员的场景。前提是愿意本地跑 Claude Code 或类似工具。

> 代码仅供学习研究，请遵守 MIT 协议。连接第三方服务前请仔细阅读 Medialyst 服务条款。

---

<!--EN-->

## Newsjack: Open-Source Skill Pack That Turns Your AI Agent into a PR Team

`elvisun/newsjack` gives AI agents (Claude Code, Codex, Hermes) a complete set of 30+ professional PR skills. Built by Elvis Sun (developer) and Carly Martinetti (PR professional), MIT licensed, 1,257+ stars as of September 2026.

**GitHub**: github.com/elvisun/newsjack | **Docs**: newsjack.sh | **License**: MIT | **Stars**: 1,257+

---

### The Core Idea

Traditional PR work is hard not because of writing, but judgment: Is this news worth jumping on? Will this angle appeal to the journalist or get you blocked? Is this pitch subject line compelling? Are we showing up in AI search results?

Newsjack encodes those judgment rules explicitly into Markdown skill files and lets agents execute them — not "AI writes PR templates," but "AI executes a professional PR workflow."

---

### Installation

```bash
curl -fsSL newsjack.sh | bash
# or
npm i -g newsjack@latest
```

For claude.ai/Cowork: Customize → Personal plugins → Create plugin → type `elvisun/newsjack`.

---

### 4 Modules, 30+ Skills

**Detect** — Find news opportunities worth acting on:
`/newsjack-monitor-setup`, `/newsjack-detector` (Slack push), `/news-search`, `/story-origin-check`, `/relevance-coarse-filter`, `/newsjack-triage`, `/coverage-tracker-setup`, `/coverage-tracker`

**Act** — Convert signals into deliverables:
`/angle-generator`, `/headline-generator`, `/meanest-editor` (adversarial pitch critique), `/crisis-holding` (with legal approval gate), `/reactive-comment`, `/fact-check`, `/journalist-fit-check`, `/same-outlet-ranker`, `/voice-extractor`, `/find-journalists` (Medialyst), `/press-clip` (PDF tearsheet, local only)

**Strategize** — Build the right PR system:
`/pr-strategist` (beginner guide for founders), `/pr-calendar` (6-month calendar with historical coverage analysis), `/newsworthiness-check`

**AEO/GEO — AI Search Visibility**:
`/ai-visibility-writing`, `/build-ai-visibility-panel` + 6 sub-skills covering ICP evidence, buyer intent, prompt proximity architecture, realistic prompt generation, QA, and panel design.

---

### Architecture

```
Go CLI binary (~/.newsjack/bin/newsjack)
└── Markdown Skill files (platform-agnostic)
    ├── /newsjack-detector.md
    ├── /angle-generator.md
    └── ...
```

Go handles installation, auto-update (pulls latest release on each run, disable with `NEWSJACK_AUTO_UPDATE=0`), and Slack notifications. Skill files are plain Markdown — any agent platform can read them.

Optional: Medialyst API (journalist database, news search) for full functionality on `/find-journalists`, `/pr-calendar`, and `/newsjack-detector`.

---

### Platform Compatibility

| Platform | Status |
|----------|--------|
| Claude Code / Codex / Hermes | ✅ Full functionality |
| claude.ai / Claude Cowork | ⚠️ Degraded (no cross-session state; monitor/tracker skills unavailable) |
| ChatGPT Enterprise Skills beta | ⚠️ Degraded (same limitations) |
| Consumer ChatGPT | ❌ Barely usable |

The most valuable skills — news monitoring, coverage tracking, press clip — require persistent state and only work fully on local agents.

---

### Limitations

1. **Local agent required for full value**: Monitor, tracker, and press-clip skills need persistent state — unavailable on claude.ai web.
2. **Journalist database requires paid Medialyst**: `/find-journalists` full version is behind a subscription.
3. **Young project**: Created May 2026, ~4 months old, moderate community size.
4. **Windows support poor**: curl installer doesn't support Windows.
5. **AEO/GEO metrics are hard to quantify**: AI search visibility is inherently difficult to measure; the 6 GEO skills lack standardized validation metrics.

---

### Bottom Line

The AEO/GEO module is the most differentiated part of Newsjack. As Perplexity, ChatGPT Search, and Google AI Mode become real traffic sources, "can AI search engines cite your content" is increasingly important. Newsjack has one of the few structured frameworks for this problem.

Best fit: startup founders, small PR teams, solo operators who need PR professional judgment but can't afford a full-time PR person — and who are willing to run Claude Code or a similar local agent.

> Code for learning and research use only. MIT license. Review Medialyst terms of service before connecting third-party services.
