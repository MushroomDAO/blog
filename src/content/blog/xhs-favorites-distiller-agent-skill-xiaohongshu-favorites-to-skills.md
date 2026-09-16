---
title: "xhs-favorites-distiller：把小红书收藏变成 Agent Skill，不是每篇都变，只有真有用的才通过"
titleEn: "xhs-favorites-distiller: Turn XiaoHongShu Favorites into Agent Skills — Not Every Post, Only the Ones That Actually Help"
description: "B1lli/xhs-favorites-distiller，Apache 2.0，Python 3.10+，把小红书（或微信）收藏里的方法蒸馏成可安装的 Agent skill。核心机制：价值筛选 + 消融测试 + 自然触发验证，未经证实的候选不进入宿主发现目录。消融实验显示去掉「自然触发」要求后，3/3 案例出现提前激活；全流程测试 24/24 正确通过。"
descriptionEn: "B1lli/xhs-favorites-distiller, Apache 2.0, Python 3.10+. Turns saved XiaoHongShu (or WeChat) favorites into installable Agent skills. Core mechanism: value filtering + ablation testing + natural-trigger verification. Unverified candidates stay outside the host's discovery directory. Ablation: removing the natural-trigger requirement caused premature activation in 3/3 trials; full-method passed 24/24."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Tech-Experiment"
tags: ["open-source", "agent-skills", "xiaohongshu", "codex", "claude-code", "distillation", "evaluation", "Python", "skill-management"]
heroImage: "../../assets/images/xhs-favorites-distiller-agent-skill-xiaohongshu-favorites-to-skills-banner.jpg"
---

> 📌 开源仓库：https://github.com/B1lli/xhs-favorites-distiller
> License：Apache 2.0 | Language：Python 3.10+ | 发布：2026-09-15

---

你的小红书收藏夹里大概存了几百条"有用的东西"。

打开一看：健身动作、早餐配方、PPT 技巧、AI 提示词、时间管理方法……一条条看完，每条都觉得"嗯，记住了"。三周后你遇到原本能用上那条方法的情境，你完全没想起来。收藏只是收藏，不是技能。

xhs-favorites-distiller 想做的事只有一件：**把你收藏里真正有用的方法，变成 Agent 每次遇到对应情境时会自动用上的 skill。** 不是每篇都变，也不是帮你整理摘要，而是找到那几条能改变你实际行为的方法，严格验证后，安装进去。

---

## 核心逻辑：一条收藏 ≠ 一个技能

这是整个项目的基础前提。

作者在 README 写得直白：**一条收藏要想变成有效 skill，必须满足三个条件：有一个具体的反复出现的失败场景、有一个因此改变的行动、有一个可观测的结果。** 满足不了这三条，原文进待评队列，等到有真实失败证据出现时再重评。

这个设计对应了一个常见问题：用 AI 把收藏批量处理成笔记或 prompt，感觉做了很多，实际上用的还是老习惯，新"技能"一次都没触发过。

---

## 四步流水线

**1. 导入（Ingest）**

把获准的收藏原文整理成标准 JSON：每条需要 `source`、稳定 `id`、`title`、`url`、`content`、布尔 `complete` 字段。完全相同的内容不重复入队；标题、链接或正文有变化会再次待评。

```sh
python3 skills/xhs-favorites-distiller/scripts/inbox.py \
  --data-dir .local/demo ingest examples/notes.json
```

**2. 评估（Assess）**

Agent 读待评原文，结合用户的**真实任务和失败证据**判断，用当前 `revision` 记录结论：

```sh
python3 skills/xhs-favorites-distiller/scripts/inbox.py \
  --data-dir .local/demo assess reading-export example-01 \
  --revision 1 --decision needs-evidence \
  --reason '尚无真实失败产物，先保留方法候选'
```

三种判断：`skip`（跳过）、`candidate`（候选）、`needs-evidence`（等待证据）。**工具不会把 candidate 自动安装或认定有效**，判断只是当前记录。

**3. 验证（Verify）**

候选 skill 需要通过两项测试才能进入激活考虑：

- **效果对照**：与未使用该方法的基线比较，确认有实际提升
- **消融测试**：关键步骤一一移除，验证哪个环节真正起作用
- **自然触发验证**：skill 必须在对应情境下被自然发现并使用，而不是每次都要显式点名——这一条决定了它是不是真的"装进去了"

**4. 激活（Activate）**

通过验证的 skill 才进入宿主的发现目录，真正参与 Agent 的日常任务。未经验证的候选在整个过程中不影响任何工作流。

---

## 消融实验结果

项目发布时附带了一套正式评测，使用 Codex CLI + 合成固定场景，8 种情境 × 3 次重复：

| 测试组 | 正确权限判断 | 提前激活次数 |
|--------|------------|------------|
| 完整方法 | 24/24 | 0/18 |
| 无方法基线 | 24/24 | 0/18 |
| 无价值筛选 | 24/24 | 0/18 |
| **无自然触发要求** | **21/24** | **3/18** |

结论很清楚：**去掉「自然触发」要求是唯一导致提前激活的因素**，3/3 案例失败，这一条在当前工作流中是必须保留的。价值筛选在合成场景上没有测出增量贡献，但这更多反映了合成场景的局限，不是价值筛选本身没用。

作者没有掩饰局限：**真实世界的 skill 效果未经证实（UNPROVEN）。** 测试覆盖的是决策逻辑的正确性，不是"用户实际工作有没有因此改善"这个最终问题。

---

## 安装

**安装到 Claude Code：**
```sh
git clone https://github.com/B1lli/xhs-favorites-distiller.git
cd xhs-favorites-distiller
python3 scripts/install.py --skills-dir ~/.claude/skills
```

**安装到 Codex（默认）：**
```sh
python3 scripts/install.py
# 默认安装到 $CODEX_HOME/skills/ 或 ~/.codex/skills/
```

安装后开一个新会话，让 Agent 完成首次配置（首次配置文档在仓库 `docs/first-install.md`）：

> 用 xhs-favorites-distiller 把我收藏里的有效方法接入日常工作，先检查来源和我的实际痛点。

首次配置包含三件事：接通收藏来源并试读、创建每日 18:00 检查任务、记录来源授权配置。只复制文件不算完成安装。

**本地工具无第三方依赖**，标准库即可跑通。需要 Python 3.10+。

---

## 数据与隐私

个人收藏原文、用户画像、来源授权和评测私料**与代码仓库完全分离**，默认存在 `~/.local/share/saved-to-practice/`（可用 `--data-dir` 或 `SAVED_TO_PRACTICE_DATA` 变量覆盖）。项目本身只含原创代码、说明文档和合成示例数据，不含任何真实收藏内容。

收藏的采集来源有两条路：

1. **宿主内置浏览器**（优先）：Claude Code 或 Codex 的内置浏览器工具，直接访问已登录的小红书/微信
2. **Playwright 回退**：宿主不支持内置浏览器时的备选，需要安装 Playwright + Chromium，采集前需用户自行登录

项目**不内置免登录爬虫**，也不保证所有宿主都能读到收藏。

---

## 升级说明

旧版本叫 `saved-to-practice`，变量名和数据目录沿用旧名，历史收藏、判断记录和登录状态可直接复用。升级时把旧技能目录移到发现目录之外备份，再安装新版，避免两个入口同时激活。

---

## 适合谁

这个项目的用户画像很窄：**已经在用 Agent（Codex 或 Claude Code）做日常任务，同时在小红书或微信上有大量收藏，想让 Agent 真正用上那些方法**——不是"我要整理收藏"，而是"我希望下次遇到对应情境时，Agent 直接帮我做好了"。

如果你只是想整理笔记，用 Readwise 或者直接让 Claude 总结就够了。这个工具解决的是更具体的问题：把方法从收藏里搬到工作流里，且搬得有验证、可回退、不干扰已有 skill。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/B1lli/xhs-favorites-distiller
> License: Apache 2.0 | Language: Python 3.10+ | Published: 2026-09-15

---

You probably have hundreds of "useful things" saved in your XiaoHongShu favorites.

Open them up: fitness moves, breakfast recipes, PPT tips, AI prompts, time management methods — you skim through, think "got it," and move on. Three weeks later you hit exactly the situation where one of those methods would've helped. You never thought of it. Saving isn't learning. A collection isn't a skill.

xhs-favorites-distiller does exactly one thing: **turn the methods in your saved favorites into Agent skills that get used automatically when the matching situation comes up.** Not every post, not a summary dump — just the handful of methods that can actually change your behavior, rigorously verified before they go live.

---

## Core logic: one saved post ≠ one skill

This is the project's foundational premise.

The author states it plainly in the README: **for a saved post to become a valid skill, it needs three things: a concrete recurring failure scenario, a changed action that addresses it, and an observable result.** If a post doesn't clear that bar, it goes into the pending queue and waits for real failure evidence before being reconsidered.

This design targets a real pattern: batch-processing favorites with AI into notes or prompts feels productive, but the "skills" never trigger, and you still fall back on old habits.

---

## The four-stage pipeline

**1. Ingest**

Organize your approved source text into a standard JSON format: each entry needs `source`, a stable `id`, `title`, `url`, `content`, and a boolean `complete`. Identical duplicates aren't re-queued; any change to title, URL, or body triggers re-evaluation.

```sh
python3 skills/xhs-favorites-distiller/scripts/inbox.py \
  --data-dir .local/demo ingest examples/notes.json
```

**2. Assess**

The Agent reads pending source text and evaluates it against the user's **real tasks and failure evidence**, recording its judgment at the current `revision`:

```sh
python3 skills/xhs-favorites-distiller/scripts/inbox.py \
  --data-dir .local/demo assess reading-export example-01 \
  --revision 1 --decision needs-evidence \
  --reason 'No real failure artifact yet; keep as method candidate'
```

Three verdicts: `skip`, `candidate`, `needs-evidence`. **The tool does not auto-install or validate a candidate** — judgments are recorded state, not automated actions.

**3. Verify**

A candidate skill must clear two tests before activation is considered:

- **Effect comparison**: compare against an unassisted baseline to confirm real improvement
- **Ablation testing**: remove key steps one at a time to identify what actually matters
- **Natural-trigger verification**: the skill must activate on its own when the situation arises, without being explicitly invoked — this determines whether it's genuinely "installed"

**4. Activate**

Only verified skills enter the host's discovery directory and participate in day-to-day agent tasks. Unverified candidates never touch any live workflow.

---

## Ablation results

The project ships a formal evaluation using Codex CLI with synthetic fixed scenarios, 8 scenarios × 3 repetitions:

| Arm | Correct permission decisions | Premature activations |
|-----|-----------------------------|-----------------------|
| Full method | 24/24 | 0/18 |
| No-method baseline | 24/24 | 0/18 |
| Without value filter | 24/24 | 0/18 |
| **Without natural-trigger requirement** | **21/24** | **3/18** |

The conclusion is clear: **removing the natural-trigger requirement is the only change that causes premature activation** — 3/3 trials failed. This requirement must be retained within this workflow. The value filter showed no incremental contribution on synthetic fixtures, which likely reflects the limits of synthetic scenarios rather than the filter being useless.

The author doesn't hide the caveat: **real-world skill effect remains UNPROVEN.** The tests cover correctness of decision logic, not the ultimate question of whether the user's actual work improves.

---

## Installation

**Install to Claude Code:**
```sh
git clone https://github.com/B1lli/xhs-favorites-distiller.git
cd xhs-favorites-distiller
python3 scripts/install.py --skills-dir ~/.claude/skills
```

**Install to Codex (default):**
```sh
python3 scripts/install.py
# Installs to $CODEX_HOME/skills/ or ~/.codex/skills/
```

After install, open a new session and let the Agent complete first-time setup (guide in `docs/first-install.md`):

> Use xhs-favorites-distiller to connect effective methods from my favorites to my daily workflow — start by checking my sources and real pain points.

First setup involves three things: connect the source and do a trial read, create a daily 18:00 check task, and record source authorization config. Just copying files is not a complete install.

**Local tools have no third-party dependencies** — standard library only. Requires Python 3.10+.

---

## Data and privacy

Personal source text, user profiles, source authorization, and evaluation records are **completely separate from the code repository**, stored by default at `~/.local/share/saved-to-practice/` (overridable via `--data-dir` or `SAVED_TO_PRACTICE_DATA`). The repo contains only original code, documentation, and synthetic example data — no real favorites content.

Two paths for collection:

1. **Host browser (preferred)**: Claude Code or Codex built-in browser tools, accessing an already-logged-in XiaoHongShu/WeChat session
2. **Playwright fallback**: when host browser isn't available; requires Playwright + Chromium installation and manual login

The project **does not include a no-login scraper** and does not guarantee all hosts can access favorites.

---

## Who it's for

The target user is narrow: **someone already using an Agent (Codex or Claude Code) for daily work, with a large body of favorites on XiaoHongShu or WeChat, who wants the Agent to actually use those methods** — not "I want to organize my bookmarks," but "I want the Agent to handle things correctly next time the right situation comes up."

If you just want organized notes, Readwise or a Claude summary session is enough. This tool addresses a more specific problem: moving methods from a collection into a workflow, with verification, rollback support, and no interference with existing skills.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
