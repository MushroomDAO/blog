---
title: "PR-Agent：把代码审查交给 AI，11.4k star 的开源 PR 评审工具完全指南"
description: "qodo-ai/pr-agent 深度调研：/review、/describe、/improve 七条斜杠命令全拆解，三条部署路径（GitHub Actions / Docker 自托管 / Qodo Cloud），支持 OpenAI、Claude、Gemini、DeepSeek 等全系列大模型，以及如何用 .pr_agent.toml 精确控制评审行为。"
titleEn: "PR-Agent: Delegate Code Review to AI — Complete Guide to the 11.4k-Star Open-Source PR Reviewer"
descriptionEn: "Deep dive into qodo-ai/pr-agent: full breakdown of /review, /describe, /improve and seven slash commands; three deployment paths (GitHub Actions / Docker self-host / Qodo Cloud); support for OpenAI, Claude, Gemini, DeepSeek; and how to control review behavior via .pr_agent.toml."
pubDate: 2026-06-07
category: "Tech-Experiment"
tags: ["Code Review", "AI Agent", "GitHub Actions", "PR-Agent", "Open Source", "DevOps", "Qodo"]
lang: "zh-CN"
heroImage: "../../assets/images/pr-agent-qodo-code-review-banner.png"
---

代码审查（Code Review）是软件开发里最耗时、最容易出现意见分歧的环节之一。

一个有经验的 reviewer 每看一个 PR，要花 30 分钟到 2 小时：读 diff、理解上下文、找潜在 bug、想怎么表达不让对方难受。团队小的时候还好，人一多、PR 一多，review 就变成了瓶颈。

**PR-Agent** 的出发点就是解决这个问题：让 AI 先做一轮审查，把明显问题、描述缺失、改进建议全部自动列出来，人只需要复核和决策。

---

## 它是什么

[PR-Agent](https://github.com/qodo-ai/pr-agent)（`qodo-ai/pr-agent`）是由 Qodo（原 CodiumAI）开发的开源 AI 代码审查工具。2026 年 4 月，Qodo 宣布将项目正式移交给社区维护（迁移到 [The-PR-Agent](https://github.com/The-PR-Agent/pr-agent) 组织），回归 Apache 2.0 协议，由开发者社区驱动。

| 指标 | 数值 |
|------|------|
| GitHub Star | **11,400+** |
| Fork | **1,500+** |
| 协议 | Apache 2.0 |
| 语言 | Python（99.9%） |
| 当前版本 | 0.36.0（2026-06-01） |
| Python 要求 | >=3.12 |

**支持的 Git 平台**：GitHub / GitLab / Bitbucket / Azure DevOps / Gitea

**支持的 AI 模型**：OpenAI GPT-4o/o3/o4-mini、Anthropic Claude Sonnet 4.6、Google Gemini 2.5 Pro、DeepSeek、Meta Llama 4、xAI Grok-3、以及通过 OpenRouter 统一接入的全部主流模型

---

## 核心命令：七条斜杠

PR-Agent 的交互方式极其简单——在 PR 的评论区输入斜杠命令，它就会做对应的工作：

| 命令 | 功能 | 典型耗时 |
|------|------|---------|
| `/review` | AI 全面代码审查，含安全、逻辑、风格问题 | ~30 秒 |
| `/describe` | 自动生成 PR 标题、摘要、变更类型、标签 | ~20 秒 |
| `/improve` | 逐行代码改进建议，生成可直接 commit 的 diff | ~30 秒 |
| `/ask <问题>` | 针对 PR 变更的自由问答 | ~20 秒 |
| `/walkthrough` | 逐步解释变更逻辑，验证 diff 是否符合意图 | ~25 秒 |
| `/labels` | 根据代码变更建议 PR 标签 | ~15 秒 |
| `/update_changelog` | 自动更新 CHANGELOG.md | ~20 秒 |

每条命令都是**单次 LLM 调用**，不会产生循环对话，成本可控。

---

## 三条部署路径

### 路径 1：GitHub Actions（最快，5 分钟上线）

适合：GitHub 用户，不想维护服务器，希望 PR 开了自动跑。

在你的仓库创建 `.github/workflows/pr-agent.yml`：

```yaml
name: PR-Agent

on:
  pull_request:
    types: [opened, reopened]
  issue_comment:
    types: [created]

permissions:
  issues: write
  pull-requests: write
  contents: write

jobs:
  pr_agent_job:
    if: ${{ github.event.sender.type != 'Bot' }}
    runs-on: ubuntu-latest
    name: Run PR-Agent on PR events
    steps:
      - name: PR Agent action step
        id: pragent
        uses: Codium-ai/pr-agent@main
        env:
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

然后在 GitHub 仓库 Settings → Secrets 里添加 `OPENAI_KEY`（或你选择的模型的 API Key）。

这样每次有人开 PR，或者在 PR 下评论 `/review`，Action 就会自动触发。

**用 Claude 替代 OpenAI**：

```yaml
env:
  ANTHROPIC.KEY: ${{ secrets.ANTHROPIC_KEY }}
  CONFIG.AI_PROVIDER: "anthropic"
  CONFIG.MODEL: "claude-sonnet-4-6"
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**用 Gemini 替代 OpenAI**：

```yaml
env:
  GOOGLE_AI_STUDIO.KEY: ${{ secrets.GEMINI_API_KEY }}
  CONFIG.AI_PROVIDER: "google_ai_studio"
  CONFIG.MODEL: "gemini-2.5-pro"
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**用 DeepSeek（成本最低）**：

```yaml
env:
  OPENAI.KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  OPENAI.API_BASE: "https://api.deepseek.com/v1"
  CONFIG.MODEL: "deepseek/deepseek-chat"
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### 路径 2：Docker 自托管（完全私有，数据不出内网）

适合：GitLab / Bitbucket / Azure DevOps 用户，或需要私有化部署的企业。

```bash
# 克隆仓库
git clone https://github.com/qodo-ai/pr-agent.git
cd pr-agent

# 创建配置文件
cat > config.toml << 'EOF'
[config]
model = "gpt-4o"
git_provider = "github"

[openai]
key = "sk-your-openai-key"

[github]
user_token = "ghp_your-github-token"
webhook_secret = "your-webhook-secret"
EOF

# Docker 运行
docker run -d \
  --name pr-agent \
  -p 3000:3000 \
  -v $(pwd)/config.toml:/app/config.toml \
  pragent/pr-agent:latest \
  --webhook_server
```

然后在 GitHub 仓库 Settings → Webhooks 里添加：
- Payload URL: `http://your-server:3000/api/v1/github_webhooks`
- Content type: `application/json`
- Secret: 和 `webhook_secret` 一致
- Events: `Pull requests` + `Issue comments`

**GitLab 自托管**，改 `config.toml`：

```toml
[config]
git_provider = "gitlab"

[gitlab]
personal_access_token = "glpat-your-token"
webhook_secret = "your-secret"
```

---

### 路径 3：Qodo Cloud（零配置，30 PR/月免费）

适合：快速试用，个人开发者。

1. 访问 [www.qodo.ai](https://www.qodo.ai) 注册账号
2. 连接你的 GitHub 仓库（OAuth 授权）
3. 完成，PR 自动获得 AI 审查

免费额度：每月 30 次 PR 审查（组织共享，不是每人 30 次）。付费版 $30/用户/月，企业版按需定制。

---

## 配置文件：`.pr_agent.toml`

在仓库根目录放一个 `.pr_agent.toml`，可以精确控制 PR-Agent 的行为：

```toml
[config]
# 指定模型（所有 OpenAI 兼容接口均可）
model = "gpt-4o"
# 响应语言（ISO 格式，支持中文！）
response_language = "zh-CN"
# 最大 token 数
max_model_tokens = 32000
# 温度（0 = 更严格一致，1 = 更有创意）
temperature = 0.1

[pr_reviewer]
# 是否显示审查工作量估算（S/M/L/XL）
require_score_review = true
# 是否只评论变更部分（不全文扫描）
num_code_suggestions = 4
# 是否要求 security 专项检查
require_security_review = true
# 是否需要测试覆盖检查
require_tests_review = true

[pr_description]
# 是否自动打标签
publish_labels = true
# 是否生成代码 walkthrough
enable_pr_diagram = true

[pr_code_suggestions]
# 每次 /improve 最多几条建议
num_code_suggestions_per_chunk = 5

[ignore]
# 不审查这些文件类型
glob = ["*.lock", "*.min.js", "dist/**", "*.generated.ts"]
```

**重要技巧：中文响应**

设置 `response_language = "zh-CN"` 后，PR-Agent 所有输出（审查意见、描述、建议）都会变成中文，对中文团队非常友好。

---

## 实际工作流演示

### 场景：开一个 PR 之后

开发者 Alice 开了一个 PR，修改了用户认证逻辑。

**Step 1：自动触发描述生成**（GitHub Actions 已配置 `on: pull_request: opened`）

PR-Agent 自动为 PR 写了：
```
## 变更类型
- [x] Bug Fix
- [x] Security

## 摘要
修复了 JWT token 刷新逻辑中的竞争条件。当并发请求同时触发 token 刷新时，
旧 token 可能在短暂窗口内被接受。

## 变更详情
- auth/jwt.go: 添加互斥锁保护 token 刷新临界区
- auth/middleware.go: 修复 token 过期检查顺序
- tests/auth_test.go: 新增并发刷新测试用例

## 审查工作量
估计: M（中等），约 15-25 分钟
```

**Step 2：reviewer Bob 触发代码审查**

Bob 在 PR 下评论 `/review`，30 秒后：

```
## 代码审查

### 关键问题（需要修复）
- [安全] auth/jwt.go:45 — 互斥锁的 defer Unlock() 位置不正确，
  在 panic 时可能导致死锁。建议改为 defer mu.Unlock()
  紧跟在 mu.Lock() 之后

### 可能的问题
- auth/middleware.go:82 — 错误日志记录了完整的 JWT token 内容，
  可能造成 token 泄露，建议只记录 token 的前8位

### 建议
- 考虑为并发测试添加 -race 标志检测竞争条件
- README 缺少 JWT 刷新配置说明

### 工作量
估计: M（已核验）
```

**Step 3：Alice 触发代码改进**

Alice 评论 `/improve`：

```
## 代码改进建议

### 建议 1（auth/jwt.go:45）
将 defer 位置移到 Lock 之后，防止 panic 时死锁

当前代码:
```go
func (s *Service) RefreshToken(old string) (string, error) {
    s.mu.Lock()
    // ... 一些代码 ...
    defer s.mu.Unlock()  // ❌ defer 位置太晚
```

建议改为:
```go
func (s *Service) RefreshToken(old string) (string, error) {
    s.mu.Lock()
    defer s.mu.Unlock()  // ✅ 紧跟 Lock
    // ... 一些代码 ...
```

[一键接受此建议]
```

**Step 4：自由问答**

Bob 评论 `/ask 这个并发锁方案在高并发场景下性能如何？是否考虑过 sync.RWMutex？`

PR-Agent 直接针对代码和问题给出具体分析。

---

## 高级用法

### OpenRouter 统一多模型接入

OpenRouter 让你用一个 API Key 访问 OpenAI、Claude、Gemini、Llama 等所有模型，并可以按 PR 类型选不同模型：

```toml
[openai]
key = "sk-or-your-openrouter-key"
api_base = "https://openrouter.ai/api/v1"

[config]
# 安全敏感 PR 用最强模型
model = "anthropic/claude-sonnet-4-6"
# 或用便宜的 DeepSeek 跑日常 PR
# model = "deepseek/deepseek-chat"
```

OpenRouter 对每笔请求加收 5.5% 费用，但省去了维护多个 API Key 的麻烦，还有统一的用量监控。

### 只在特定目录触发

```toml
[ignore]
# PR 只修改了文档/配置时不触发详细代码审查
glob = ["docs/**", "*.md", "*.yml"]
```

### 自定义评审重点

```toml
[pr_reviewer]
# 自定义关注点（会加入 prompt 中）
extra_instructions = """
我们的项目使用 Go 1.22+，请特别关注：
1. goroutine 泄露风险
2. context 正确传递
3. error wrapping 规范（%w 不是 %v）
4. 所有数据库操作必须有事务
"""
```

---

## 真实效果数据

根据多个团队的实际报告：

| 指标 | 变化 |
|------|------|
| 平均 PR 审查时间 | **从 2 小时降到 45 分钟（-62%）** |
| 安全问题发现率 | **提升约 4 倍** |
| PR 描述质量 | 显著改善，新人 PR 描述从无到有 |
| Reviewer 负担 | 从"看所有细节"变成"决策和判断" |

Qodo 2.0 多 Agent 架构（2026 年 2 月发布）的实测数据：
- 在代码审查 benchmark 上 F1 值 **60.1%**，比最近竞争对手高 9%
- Recall（召回率）**56.7%**，高于其他工具

---

## 我的判断

**值得部署，尤其是中小团队。**

几个观察：

**1. GitHub Actions 路径太顺了**：从零到 PR 自动审查，真的只需要 5 分钟，加一个 yaml 文件，添加一个 secret。门槛比所有同类工具都低。

**2. 命令设计合理**：不是把 AI 塞进一个黑盒，而是明确的工具集——`/describe` 是描述，`/review` 是审查，`/improve` 是建议。每个工具职责清晰，reviewer 自己决定什么时候触发什么。

**3. 中文支持真实可用**：`response_language = "zh-CN"` 不是摆设，中文团队配置后整个交互都是中文，review 意见可以直接和国内同事沟通。

**4. 社区移交是好事**：2026 年 4 月 Qodo 把项目交给 The-PR-Agent 社区，Apache 2.0 协议，意味着没有商业锁定风险，可以长期依赖。

**需要注意**：

- 需要自己支付 LLM API 费用（DeepSeek 最便宜，一次审查约 $0.01-$0.05）
- AI 审查不能替代人工——它找不到业务逻辑错误，也不了解你的产品背景
- 配置需要花时间调教，才能把无关噪音（如 lock 文件变更）过滤掉

---

**快速上手：三步走**

```bash
# 1. 安装（用于 CLI 测试）
pip install pr-agent

# 2. 测试一个 PR（CLI 模式）
OPENAI_API_KEY=sk-xxx pr-agent review --pr_url https://github.com/owner/repo/pull/123

# 3. 正式部署 → 创建 .github/workflows/pr-agent.yml（见上文）
```

---

**GitHub**: qodo-ai/pr-agent（现社区维护: The-PR-Agent/pr-agent）  
**官方文档**: pr-agent-docs.codium.ai  
**Qodo Cloud 试用**: qodo.ai（30 PR/月免费）

<!--EN-->

## PR-Agent: Delegate Code Review to AI — Complete Guide to the 11.4k-Star Open-Source PR Reviewer

Code review is one of the most time-consuming and friction-prone steps in software development.

An experienced reviewer can spend 30 minutes to 2 hours on a single PR — reading the diff, understanding context, spotting potential bugs, and choosing words carefully. That's manageable in a small team, but as team size and PR volume grow, review becomes the bottleneck.

**PR-Agent** addresses this directly: let AI run a first-pass review — surfacing missing descriptions, potential bugs, and improvement suggestions — so humans can focus on decision-making rather than discovery.

---

## What It Is

[PR-Agent](https://github.com/qodo-ai/pr-agent) (`qodo-ai/pr-agent`) is an open-source AI code review tool built by Qodo (formerly CodiumAI). In April 2026, Qodo donated the project to the community (now maintained under [The-PR-Agent](https://github.com/The-PR-Agent/pr-agent) organization), returning to Apache 2.0.

| Metric | Value |
|--------|-------|
| GitHub Stars | **11,400+** |
| Forks | **1,500+** |
| License | Apache 2.0 |
| Language | Python (99.9%) |
| Current Version | 0.36.0 (2026-06-01) |
| Python Required | >=3.12 |

**Supported Git platforms:** GitHub / GitLab / Bitbucket / Azure DevOps / Gitea

**Supported AI models:** OpenAI GPT-4o/o3/o4-mini, Anthropic Claude Sonnet 4.6, Google Gemini 2.5 Pro, DeepSeek, Meta Llama 4, xAI Grok-3, and all major models via OpenRouter

---

## Core Commands: Seven Slash Commands

PR-Agent's interaction model is simple: comment a slash command on a PR, and it does the work.

| Command | Function | Typical Time |
|---------|----------|--------------|
| `/review` | Full AI code review: security, logic, style issues | ~30s |
| `/describe` | Auto-generate PR title, summary, change type, labels | ~20s |
| `/improve` | Line-by-line code improvement suggestions (commit-ready diffs) | ~30s |
| `/ask <question>` | Free-form Q&A about the PR changes | ~20s |
| `/walkthrough` | Step-by-step explanation, verifies diff matches intent | ~25s |
| `/labels` | Suggest PR labels based on code changes | ~15s |
| `/update_changelog` | Auto-update CHANGELOG.md | ~20s |

Every command is a **single LLM call** — no conversation loops, predictable cost.

---

## Three Deployment Paths

### Path 1: GitHub Actions (Fastest — live in 5 minutes)

Best for: GitHub users who want automatic reviews without maintaining a server.

Create `.github/workflows/pr-agent.yml` in your repository:

```yaml
name: PR-Agent

on:
  pull_request:
    types: [opened, reopened]
  issue_comment:
    types: [created]

permissions:
  issues: write
  pull-requests: write
  contents: write

jobs:
  pr_agent_job:
    if: ${{ github.event.sender.type != 'Bot' }}
    runs-on: ubuntu-latest
    name: Run PR-Agent on PR events
    steps:
      - name: PR Agent action step
        id: pragent
        uses: Codium-ai/pr-agent@main
        env:
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Add `OPENAI_KEY` to GitHub repository Settings → Secrets. Done.

**Use Claude instead:**

```yaml
env:
  ANTHROPIC.KEY: ${{ secrets.ANTHROPIC_KEY }}
  CONFIG.AI_PROVIDER: "anthropic"
  CONFIG.MODEL: "claude-sonnet-4-6"
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Use DeepSeek (cheapest option):**

```yaml
env:
  OPENAI.KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  OPENAI.API_BASE: "https://api.deepseek.com/v1"
  CONFIG.MODEL: "deepseek/deepseek-chat"
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### Path 2: Docker Self-Hosted (Fully private, data stays on-premise)

Best for: GitLab / Bitbucket / Azure DevOps users, or teams with strict data governance requirements.

```bash
git clone https://github.com/qodo-ai/pr-agent.git
cd pr-agent

# Create config file
cat > config.toml << 'EOF'
[config]
model = "gpt-4o"
git_provider = "github"

[openai]
key = "sk-your-openai-key"

[github]
user_token = "ghp_your-github-token"
webhook_secret = "your-webhook-secret"
EOF

# Run with Docker
docker run -d \
  --name pr-agent \
  -p 3000:3000 \
  -v $(pwd)/config.toml:/app/config.toml \
  pragent/pr-agent:latest \
  --webhook_server
```

Then add a GitHub webhook pointing to `http://your-server:3000/api/v1/github_webhooks`.

---

### Path 3: Qodo Cloud (Zero config, 30 PRs/month free)

Best for: quick evaluation, individual developers.

1. Sign up at [www.qodo.ai](https://www.qodo.ai)
2. Connect your GitHub repository via OAuth
3. Done — PRs automatically receive AI reviews

Free tier: 30 PR reviews per month (shared pool per org). Teams plan: $30/user/month. Enterprise: custom pricing.

---

## Configuration: `.pr_agent.toml`

Place this file in your repository root to control PR-Agent behavior:

```toml
[config]
model = "gpt-4o"
response_language = "en-US"     # "zh-CN" for Chinese responses!
max_model_tokens = 32000
temperature = 0.1

[pr_reviewer]
require_score_review = true
num_code_suggestions = 4
require_security_review = true
require_tests_review = true

[pr_description]
publish_labels = true
enable_pr_diagram = true

[pr_code_suggestions]
num_code_suggestions_per_chunk = 5

[ignore]
glob = ["*.lock", "*.min.js", "dist/**", "*.generated.ts"]
```

**Custom review focus** — inject domain knowledge directly into the review prompt:

```toml
[pr_reviewer]
extra_instructions = """
This project uses Go 1.22+. Pay special attention to:
1. Goroutine leak risks
2. Proper context propagation
3. Error wrapping convention (use %w not %v)
4. All database operations must use transactions
"""
```

---

## Real-World Outcomes

Based on multiple team reports:

| Metric | Change |
|--------|--------|
| Average PR review time | **From 2 hours → 45 minutes (−62%)** |
| Security issue detection rate | **~4x improvement** |
| PR description quality | Significant improvement, especially from junior developers |
| Reviewer focus | Shifts from "find all the details" to "validate and decide" |

Qodo 2.0's multi-agent architecture benchmark results (February 2026):
- F1 score: **60.1%** — 9% above the nearest competitor
- Recall: **56.7%** — highest among compared tools

---

## My Assessment

**Worth deploying, especially for small-to-medium teams.**

Key observations:

**1. GitHub Actions path is frictionless**: From nothing to automatic PR review in under 5 minutes — one yaml file, one secret. The lowest barrier of any comparable tool.

**2. Command design is principled**: Not a black box — it's a clear toolkit. `/describe` is description, `/review` is review, `/improve` is suggestions. Reviewers decide when to trigger what.

**3. Community handoff reduces risk**: With the April 2026 move to The-PR-Agent community org under Apache 2.0, there's no vendor lock-in. Safe to depend on long-term.

**Things to be aware of:**
- You pay your own LLM API costs (DeepSeek is cheapest, ~$0.01-$0.05 per review)
- AI review cannot replace human judgment on business logic and product context
- Configuration needs tuning to filter out noise (e.g., lock files, generated files)

---

**Quick Start**

```bash
# Install CLI for local testing
pip install pr-agent

# Test on a specific PR
OPENAI_API_KEY=sk-xxx pr-agent review --pr_url https://github.com/owner/repo/pull/123

# Production: create .github/workflows/pr-agent.yml (see above)
```

---

**GitHub**: qodo-ai/pr-agent (community: The-PR-Agent/pr-agent)  
**Docs**: pr-agent-docs.codium.ai  
**Qodo Cloud**: qodo.ai (30 PRs/month free)
