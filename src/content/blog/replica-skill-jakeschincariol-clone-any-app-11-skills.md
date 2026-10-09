---
title: "Replica：11 个 Skill，把任何 App 克隆一遍"
titleEn: "Replica: 11 Skills to Clone Any App from Scratch"
description: "Jake Schincariol 开源 replica-skill（MIT，1.3K stars）：11 个 Claude Code Skill，把「看一个 App 然后自己造一个」系统化。流程分 11 步：/replica-recon 逆向分析功能和页面流程，/replica-architect 规划技术栈，/replica-design 重建设计系统，/replica-build 逐屏实现，/replica-backend 接入 Auth/支付，/replica-test 找 Bug，/replica-diff 评估完整度，/replica-entrepreneur 读差评挖痛点，/replica-brand 清除原产品痕迹，/replica-launch 写落地页，/replica-deploy 部署上线。附 6 个 Python 工具脚本（标准库，无需 pip）。clean-room 机制：只分析公开页面和自己的账号，不复制代码或素材，部署前 sweep.py 扫描原产品残留。"
descriptionEn: "Jake Schincariol open-sourced replica-skill (MIT, 1.3K stars): 11 Claude Code Skills that systematize 'see an app then build your own version.' 11-step pipeline: /replica-recon reverse-analyzes features and flows, /replica-architect plans the tech stack, /replica-design rebuilds the design system, /replica-build implements screen by screen, /replica-backend integrates auth/payments, /replica-test finds bugs, /replica-diff measures completeness, /replica-entrepreneur mines negative reviews for pain points, /replica-brand clears original product traces, /replica-launch writes landing page copy, /replica-deploy ships to your domain. Includes 6 Python utility scripts (stdlib, no pip). Clean-room: only reads public pages and your own account, never copies source code or assets, sweep.py scans for originator traces before deploy."
pubDate: 2026-10-09
heroImage: "../../assets/images/replica-skill-jakeschincariol-clone-any-app-11-skills-banner.jpg"
category: "Tech-Experiment"
tags: ["Claude Code", "Skill", "App克隆", "indie hacker", "开源工具"]
lang: "zh-CN"
wechatTitle: "Replica：11个Skill把任何App克隆一遍"
wechatDigest: "MIT 1.3K；11步Claude Code套件；逆向分析→重写→差评提炼→扫描清除→部署"
---

如果你看了一个 App，觉得「这个我也能做，而且能做得更好」——replica-skill 就是把这个想法走完的 11 步流程。

MIT，1.3K stars，2026-10-03 发布，一周内涨到这个数。

GitHub: https://github.com/Jakeschincariol/replica-skill

---

## 11 个 Skill 的分工

| Skill | 做什么 |
|-------|--------|
| `/replica-recon` | 逆向分析目标 App 的页面流程、组件、数据模型（只读公开页面和自己的账号） |
| `/replica-architect` | 规划技术栈、数据库 Schema、API 设计 |
| `/replica-design` | 重建设计系统（颜色 token、字体、间距、组件） |
| `/replica-build` | 逐屏重实现 App |
| `/replica-backend` | 接入 Auth、数据库、支付、第三方集成 |
| `/replica-test` | 跑完所有流程，按严重度记录 Bug |
| `/replica-diff` | 对比克隆版与原版，给出功能完整度评分 + 缺漏清单 |
| `/replica-entrepreneur` | 读真实用户差评，提取痛点，给出差异化定位方向 |
| `/replica-brand` | 重命名品牌，扫描并清除所有原产品痕迹（名称/域名/颜色） |
| `/replica-launch` | 生成落地页文案、定价页、应用商店描述 |
| `/replica-deploy` | 预检通过后部署到你的域名 |

---

## 随附的 Python 工具脚本

Skills 调用这 6 个 Python 工具脚本（Python 3.8+，只用标准库，无需 pip install）：

- `imgdiff.py` — 截图布局对比（忽略颜色差异，专注结构差异）
- `parity.py` — 功能完整度评分
- `reviews.py` — 用户差评排序（只保留带链接的有据可查的评论）
- `contrast.py` — WCAG 对比度检查
- `sweep.py` — 代码库扫描原产品名称/域名/颜色残留
- `listing.py` — 应用商店文案字数和抄袭检查

`/replica-deploy` 在 `sweep.py` 扫描通过之前会拒绝部署。

---

## `/replica-entrepreneur`：从差评里找机会

这是整套流程里最有意思的一个 Skill。

原版 App 的用户差评里记录着真实的痛点——功能缺失、交互反直觉、性能问题、价格不合理。`/replica-entrepreneur` 读这些差评，提取共性痛点，转化成「你的版本在哪里可以做得不一样」的定位方向。

它不是帮你抄一个一模一样的克隆，而是帮你造一个**从用户抱怨出发的改进版**。

---

## Clean-Room 机制

项目的 Clean-Room 定义：
- **只看**：功能做了什么、用户怎么走流程
- **不碰**：源代码、素材、Logo、商标、私有 API
- **从零写**：所有实现代码由 Claude Code 生成，不复制原版

`/replica-recon` 限定在公开页面和你自己的账号内操作，不绕过登录墙或 ToS。

项目明确建议上线前做**商标检索和法律审查**——clean-room 不等于免责，它只是降低代码层面的侵权风险。

---

## 技术栈

Skills 本身是 Claude Code 的 skill 文件夹（每个含 `SKILL.md`），文档举例的参考架构是 Next.js + Postgres + Stripe + Resend，但 `/replica-architect` 会根据目标 App 实际情况规划，不强制这个栈。

---

## 已知边界

- **复杂度上限**：订票类 App 可行，电子表格引擎级别的产品不现实
- **不提供法律建议**，上线前务必自行做商标检索和法律审查
- 只支持 Claude Code（Skill 格式），不是通用 Agent 脚本
- 1.3K stars，2026-10-03 才发布，尚未经过大量实战验证

---

## 一句话说清楚

replica-skill 是一套 Claude Code Skill，把「克隆一个 App」分成 11 步系统化：逆向分析功能→重建设计和代码→差评驱动差异化→清除原产品痕迹→部署上线。MIT，1.3K stars，一周内增速很快。

---

> MIT。Jake Schincariol（opusjake.ai），2026-10-03 发布，1.3K stars。开源仅供学习参考，上线前请做法律审查。

---

<!--EN-->

## Replica: 11 Skills to Clone Any App from Scratch

If you've looked at an app and thought "I could build this, and build it better" — replica-skill is the 11-step system for turning that thought into a shipped product.

MIT, 1.3K stars, published 2026-10-03, reached 1,000+ in one week.

GitHub: https://github.com/Jakeschincariol/replica-skill

---

### 11-Skill Pipeline

| Skill | What it does |
|-------|-------------|
| `/replica-recon` | Reverse-analyzes flows, components, data models (public pages + your own account only) |
| `/replica-architect` | Plans tech stack, DB schema, API design |
| `/replica-design` | Rebuilds the design system (color tokens, type, spacing, components) |
| `/replica-build` | Implements the app screen by screen |
| `/replica-backend` | Integrates auth, database, payments, third-party services |
| `/replica-test` | Tests all flows, logs bugs by severity |
| `/replica-diff` | Compares clone vs. original, produces completeness score + gap list |
| `/replica-entrepreneur` | Mines real negative reviews, extracts pain points, generates differentiation angles |
| `/replica-brand` | Renames brand, scans and removes all original product traces |
| `/replica-launch` | Generates landing page copy, pricing page, app store description |
| `/replica-deploy` | Deploys to your domain after pre-checks pass |

---

### Bundled Python Tools

Six utility scripts (Python 3.8+, stdlib only, no pip install):

- `imgdiff.py` — screenshot layout diff (color-agnostic, structural diff only)
- `parity.py` — feature completeness scoring
- `reviews.py` — negative review ranking (keeps only citable, linked reviews)
- `contrast.py` — WCAG contrast check
- `sweep.py` — codebase scan for original product name/domain/color traces
- `listing.py` — app store copy length and plagiarism check

`/replica-deploy` refuses to deploy until `sweep.py` passes clean.

---

### `/replica-entrepreneur`: Mining Competitor Pain Points

This is the most interesting Skill in the set.

Real negative reviews document genuine pain points — missing features, counterintuitive interactions, performance issues, pricing frustration. `/replica-entrepreneur` reads these reviews, extracts common themes, and turns them into positioning angles: where your version can be meaningfully different.

It's not helping you clone the app identically — it's helping you build the version that users actually wanted.

---

### Clean-Room Mechanism

The project's clean-room definition:
- **Analyzes**: what features do, how users flow through them
- **Does not touch**: source code, assets, logos, trademarks, private APIs
- **Builds from scratch**: all implementation is written by Claude Code, not copied

The project explicitly recommends doing **trademark searches and legal review before launch** — clean-room reduces code-level infringement risk, not all risk.

---

### Known Limits

- **Complexity ceiling**: booking apps are feasible; spreadsheet-engine-level products are not
- No legal advice included; do your own review
- Claude Code only (Skill format)
- Very new (2026-10-03), limited real-world validation

---

### TL;DR

replica-skill is a Claude Code Skill set that systematizes "clone an app" into 11 steps: reverse-analyze features → rebuild design and code → differentiate from negative reviews → sweep for original traces → deploy. MIT, 1.3K stars, fast-growing week one.

---

> MIT. Jake Schincariol (opusjake.ai), published 2026-10-03, 1.3K stars. For reference only — do legal review before launching.
