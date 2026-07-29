---
title: "OpenAI Codex 技能市场的入口：一个小仓库打开 295 个 WorkBuddy 技能——含 47 个微信/腾讯自动化"
description: "gaixianggeng/codex-skills 是一个只有 2 个 star 的小仓库，却包含两个极具价值的 Codex 技能：init-project-workspace 初始化工作区，workbuddy-skills-navigator 打开一个 295 技能的 AI Agent 市场。这个市场里有 47 个微信/腾讯相关技能、159 个 AI/Agent 工具，全部通过 Git + Python CLI 管理。本文拆解技能格式、安装方式和 WorkBuddy 发现的具体内容。"
pubDate: "2026-07-29"
category: "Tech-Experiment"
heroImage: "../../assets/images/codex-skills-gaixianggeng-workbuddy-marketplace-openai-agent-skill-banner.jpg"
---

GitHub 上大多数"有价值的东西"不在 star 数最多的仓库里。

`gaixianggeng/codex-skills` 只有 2 个 star，但它包含两个 Codex 技能，其中一个（`workbuddy-skills-navigator`）实际上是 **WorkBuddy 技能市场的 CLI 入口**——295 个公开技能，横跨 10 个分类，包含 47 个微信/腾讯相关自动化技能，全部可以通过 Python CLI 搜索和安装。

---

## 一、Codex 技能是什么

OpenAI Codex（现在的 claude.ai 接口也支持类似格式）的技能系统允许你把一段功能打包成两个文件安装到 AI Agent 里：

```
<技能名>/
  SKILL.md           # 描述这个技能做什么、什么时候用
  agents/
    openai.yaml      # 定义 Agent 调用格式
```

安装后，Agent 在收到对应意图时会自动激活这个技能，就像给 CLI 装了一个新子命令。

技能安装到 `~/.codex/skills/`，通过 `npx skills add <git-url> --skill <name>` 命令安装。

---

## 二、仓库里有什么

`gaixianggeng/codex-skills` 包含两个技能：

### 1. `init-project-workspace`

初始化标准化项目工作区。功能：

- 在当前目录生成 `AGENTS.md`、`MEMORY.md`、`REVIEW-CHECKLIST.md`
- 创建 `agent_docs/` 子目录结构
- 写入项目的技术栈、代码规范、保护区域等约定

这个技能的设计思路和 [KhazP/vibe-coding-prompt-template](/vibe-coding-prompt-template-khazp-agents-md-prd-mvp-workflow-guide/) 一脉相承：**在开始编码前，把所有约定固化成文件**，让 Agent 每次都从完整上下文启动。

```bash
# 安装
npx skills add https://github.com/gaixianggeng/codex-skills --skill init-project-workspace

# 使用（在 Codex 对话中说）
"初始化这个项目的工作区"
```

### 2. `workbuddy-skills-navigator`

这个技能才是这个仓库真正的发现。它不是一个特定功能，而是一个**技能市场导航器**——安装后可以通过自然语言搜索和安装 WorkBuddy 上的任意技能：

```bash
# 安装
npx skills add https://github.com/gaixianggeng/codex-skills --skill workbuddy-skills-navigator

# 在 Agent 对话中使用
"帮我找微信消息自动化相关的技能"
"搜索 GitHub PR review 技能"
"安装 linkedin-post-generator 技能"
```

---

## 三、WorkBuddy 是什么

WorkBuddy 是一个 AI Agent 技能市场，目前有 **295 个公开技能**，分布在 10 个分类：

| 分类 | 技能数量 |
|---|---|
| AI/Agent 工具 | 159 |
| 腾讯/微信自动化 | **47** |
| 开发工具 | 38 |
| 内容创作 | 27 |
| 数据分析 | 14 |
| 其他 | 10 |

47 个微信/腾讯相关技能覆盖了：

- 公众号文章发布、排版、图文管理
- 企业微信消息发送、群管理
- 小程序数据上报
- 腾讯云 API 调用封装
- 微信支付订单查询

这些技能的格式和 Codex 技能一致，可以直接通过 `workbuddy-skills-navigator` 搜索并安装到你的 Codex 环境里。

---

## 四、技能格式拆解

以 `init-project-workspace` 为例，`SKILL.md` 的结构：

```markdown
# init-project-workspace

## 描述
初始化 AI Agent 友好的项目工作区，生成标准化配置文件。

## 触发条件
- 用户说"初始化工作区"、"setup workspace"、"帮我建项目结构"
- 用户新建了一个空项目目录

## 执行步骤
1. 读取当前目录的项目信息（package.json、pyproject.toml 等）
2. 生成 AGENTS.md（项目规范）
3. 生成 MEMORY.md（会话记忆模板）
4. 生成 REVIEW-CHECKLIST.md（完成标准）
5. 创建 agent_docs/ 目录和子文档
```

`agents/openai.yaml` 定义 Agent 如何调用这个技能——包括输入参数 schema、执行步骤的 prompt 模板和输出格式。

这个格式的设计哲学和 Claude Code 的 `CLAUDE.md` + `~/.claude/skills/` 系统异曲同工：**把对 Agent 的指令从对话历史里解耦出来，变成版本可控的文件**。

---

## 五、Git 管理技能的优势

这套系统最有意思的设计是：**技能本身就是 Git 仓库**。

```bash
# 安装 = git clone + 注册
npx skills add https://github.com/gaixianggeng/codex-skills --skill workbuddy-skills-navigator

# 更新 = git pull
npx skills update workbuddy-skills-navigator

# 分叉定制 = fork + 修改 + 安装自己的版本
gh repo fork gaixianggeng/codex-skills
# 编辑 SKILL.md 和 agents/openai.yaml
npx skills add https://github.com/<你的账号>/codex-skills --skill init-project-workspace
```

这意味着：
- 技能可以 fork、定制、分享
- 团队可以维护内部私有技能仓库，和公开市场共存
- 版本历史清晰，回滚一条 `git checkout` 搞定

---

## 六、怎么开始

**方式 A：直接安装两个技能**

```bash
# 安装工作区初始化技能
npx skills add https://github.com/gaixianggeng/codex-skills --skill init-project-workspace

# 安装技能市场导航器
npx skills add https://github.com/gaixianggeng/codex-skills --skill workbuddy-skills-navigator
```

**方式 B：探索 WorkBuddy 市场**

通过 `workbuddy-skills-navigator` 安装后，在 Codex 里说：

```
"列出所有微信相关的技能"
"给我安装 wechat-article-publisher 技能"
```

**方式 C：自己写一个技能**

参考这个仓库的结构，两个文件就够了：`SKILL.md` + `agents/openai.yaml`。发布到 GitHub 后，任何人都可以用 `npx skills add` 安装。

---

## 小结

`gaixianggeng/codex-skills` 的价值不在于它本身的 2 个 star，而在于它打开的那扇门——**通过 `workbuddy-skills-navigator`，你可以访问一个有 295 个技能的市场，其中 47 个直接针对微信/腾讯生态**。

如果你在用 OpenAI Codex 或者任何兼容这套技能格式的 Agent 系统，这个仓库值得收藏。

**GitHub**: `github.com/gaixianggeng/codex-skills`（2 ⭐）

---

<!--EN-->

## The Gateway to OpenAI's Skill Marketplace: How a 2-Star GitHub Repo Unlocks 295 WorkBuddy Skills

Most valuable things on GitHub aren't in the most-starred repos.

`gaixianggeng/codex-skills` has just 2 stars. But one of its two Codex skills — `workbuddy-skills-navigator` — is actually a **CLI gateway into the WorkBuddy skill marketplace**: 295 public skills across 10 categories, including 47 WeChat/Tencent automation skills, all searchable and installable via natural language.

---

## What Codex Skills Are

The Codex (and compatible agent system) skill format lets you package functionality into two files:

```
<skill-name>/
  SKILL.md           # what the skill does, when to activate
  agents/
    openai.yaml      # agent invocation format
```

Skills install to `~/.codex/skills/` via `npx skills add <git-url> --skill <name>`. Once installed, the agent activates the skill automatically when it detects a matching intent.

---

## What's in This Repo

**`init-project-workspace`** — generates a standardized AI-agent-friendly project structure: `AGENTS.md`, `MEMORY.md`, `REVIEW-CHECKLIST.md`, and an `agent_docs/` subdirectory. The same "front-load all decisions into files before writing code" philosophy from KhazP's vibe-coding workflow.

**`workbuddy-skills-navigator`** — not a specific tool, but a **marketplace navigator**. Once installed, you can search and install any of WorkBuddy's 295 public skills through natural language in your Codex session.

---

## The WorkBuddy Marketplace

295 public skills, 10 categories:

| Category | Count |
|---|---|
| AI/Agent Tools | 159 |
| **Tencent/WeChat Automation** | **47** |
| Dev Tools | 38 |
| Content Creation | 27 |
| Data Analysis | 14 |

The 47 WeChat/Tencent skills cover: Official Account publishing and formatting, WeCom group messaging, Mini Program event tracking, Tencent Cloud API wrappers, and WeChat Pay order queries.

---

## The Git-Native Advantage

Skills ARE Git repos. Install = clone + register. Update = pull. Customize = fork + edit + install your fork. Teams can run private skill repos alongside the public marketplace. Version history is clean, rollbacks are one `git checkout`.

---

## Getting Started

```bash
# Install both skills from this repo
npx skills add https://github.com/gaixianggeng/codex-skills --skill init-project-workspace
npx skills add https://github.com/gaixianggeng/codex-skills --skill workbuddy-skills-navigator

# Then in Codex, say:
# "List all WeChat-related skills"
# "Install wechat-article-publisher"
```

Or fork the repo and write your own skill with just two files.

---

**GitHub**: `github.com/gaixianggeng/codex-skills` (2 ⭐)  
**Marketplace**: workbuddy.ai
