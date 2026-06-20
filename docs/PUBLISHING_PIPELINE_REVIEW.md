# 发布流程评估与优化 / Publishing Pipeline Review

> 评估日期：2026-06-20 ｜ 范围：M1（博客）+ M2（公众号）发布链路
> 关联：`.agents/skills/blog-publisher`、`.agents/skills/banner-creator`、`scripts/publish-blog.sh`

本文档分三部分：**透彻评估现状 → 已执行的优化 → 未来方向**。

---

## 一、现状评估（Assessment）

### 1.1 发布链路全景

三条独立流水线，但 M1/M2 是日常主力，M3（小红书）独立：

| 流水线 | 目标 | 当前入口 |
|--------|------|----------|
| **M1** | Astro 博客 → Cloudflare Pages | 多个脚本 + blog-publisher skill 的 Fast Path |
| **M2** | 微信公众号草稿 | `pipeline/m2/index.js` |
| **M3** | 小红书 | `publish-xhs.sh` |

### 1.2 核心问题：一件事，五种做法

M1 的"发布"散落在至少 5 个入口，逻辑各异、互相漂移：

| 入口 | 问题 |
|------|------|
| `publish.sh` | 需手动 AI 润色 + 按 Enter，阻塞自动化 |
| `publish-fast.sh` | 自动 frontmatter，但质量低 |
| `scripts/auto-publish.sh` | 最自动化，但 `tags=["tech","ai"]`、`titleEn=slug`、`description=正文前几行`——**SEO 质量差**；且 deploy 命令**缺少** `NODE_TLS_REJECT_UNAUTHORIZED=0` 和 `--commit-dirty=true`，与实际可用命令不一致 |
| `pipeline/m1-to-m2.sh` | 功能最全（full/blog-only/wechat-only 三模式），但含交互暂停 |
| `blog-publisher` skill 的 Fast Path | **实际唯一稳定可用的路径**（本会话发布 4 篇都走它），但全靠手工逐步执行，未固化成脚本 |

**根因**：可用的知识在 skill 文档里（人/模型脑子里），但没有被固化成一个幂等、可重复执行的脚本。脚本们则是历史沉积，没人敢删也没人维护。

### 1.3 具体痛点清单

| 痛点 | 位置 | 影响 |
|------|------|------|
| 5 套 slug/frontmatter 生成逻辑 | `publish*.sh`、`auto-publish.sh:42-45`、`publisher.py:22-29` | 同标题可能生成不同 slug；重复路由风险 |
| deploy 命令不一致 | `auto-publish.sh:121`、`deploy.sh:21` vs 实际可用命令 | 缺 TLS/commit-dirty 标志会失败 |
| `NODE_TLS_REJECT_UNAUTHORIZED=0` 无文档 | `scripts/publish.sh:64` | 治标不治本，根因未记录（代理环境 TLS） |
| 交互暂停 | `publish.sh`、`m1-to-m2.sh:119,166` | 无法 CI/自动化 |
| 硬编码路径 | `publisher.py:17-19`、`m2/index.js:10-11` | 换目录就崩 |
| slug 冲突用时间戳兜底 | `publisher.py:51-54` | 文件名不可预测 |
| 封面无校验 | 所有 cover 调用 | 封面生成失败可能静默，文章无图发布 |
| 封面非写实 | `m1/cover_generator.py`（960×480 随机占位图）| 质量低，尺寸还和站点 1200×630 不符 |
| 微信 40164 IP 白名单 | `scan-sources.sh:48` | 报错才发现，需手动加白名单 |
| 公众号草稿无法改封面 | M2 设计 | 换 banner 需新建草稿，旧草稿堆积 |

### 1.4 多用户配置（健康）

`config/index.js` 按 `BLOG_USER` 加载 `config/users/{user}.js`，含 `projectName`/`domain`/微信/小红书配置，结构清晰。**问题**：脚本大多硬编码 `blog-mushroom`，没真正读 config。

---

## 二、已执行的优化（Executed）

### 2.1 固化唯一权威发布脚本 `scripts/publish-blog.sh`

把 blog-publisher Fast Path 这条"实际可用"的流程固化成一个幂等脚本：

```
publish-blog.sh <article.md> [--wechat] [--theme NAME] [--no-deploy]
```

它做对了之前散落各处的事：
- **从 config 读 projectName/domain**（不再硬编码），支持多用户；
- **发布前校验**：frontmatter 必填字段、tags≥3、双语 `<!--EN-->`、版权块、**banner 文件真实存在**；
- **正确的 deploy 命令**：`NODE_TLS_REJECT_UNAUTHORIZED=0 ... --commit-dirty=true`；
- **构建后校验路由**、**部署后校验线上 200**；
- **可选 `--wechat`** 一步建公众号草稿；
- 无交互暂停，可自动化。

### 2.2 写实风格 banner 能力 `banner-creator` skill

替代低质量随机占位封面：用本地 FLUX.2 为每篇文章生成**写实风格** banner，**1200×630、<99KB**（`-define jpeg:extent=98KB` 硬约束），关键词→真实场景映射。详见 `.agents/skills/banner-creator/SKILL.md`。已被 blog-publisher 第 2 步设为默认封面来源。

### 2.3 banner 池清理

从 blog-publisher 默认池移除 7 张插画风 banner，提升 5 张写实 banner，并标注 Deprecated（文件保留，因 39 篇历史文章仍引用）。

### 2.4 遗留脚本标注废弃

`publish.sh`、`publish-fast.sh`、`scripts/auto-publish.sh` 头部加运行时废弃警告，指向 `publish-blog.sh`（保留可运行，不删除，避免破坏历史习惯）。

### 2.5 文档对齐

更新 blog-publisher SKILL.md：第 2 步默认走 banner-creator；脚本表把 publish-blog.sh 标为 CANONICAL。

---

## 三、未来方向（Future Directions）

按优先级：

1. **统一 slug/frontmatter 生成**（高）：把 5 套逻辑收敛成一个 `scripts/lib/slugify.sh` 或 node 模块，publish-blog.sh 与 publisher.py 共用，彻底消除"同题不同 slug"。

2. **根治 TLS workaround**（高）：定位代理环境下 wrangler TLS 失败的根因（很可能是企业代理证书），用 `NODE_EXTRA_CA_CERTS` 指向 CA 证书替代 `NODE_TLS_REJECT_UNAUTHORIZED=0`，消除安全隐患。

3. **M2 草稿幂等**（中）：公众号 API 无法改封面导致草稿堆积。可在 `pipeline/m2` 维护 `slug→media_id` 映射，重发时先删旧草稿（`draft/delete`）再建，避免重复。

4. **发布前 40164 预检**（中）：publish-blog.sh 的 `--wechat` 前先探测当前出口 IP 是否在白名单，提前给出可读提示，而非等 API 报错。

5. **banner-creator 全局化 + 评测**（中）：已封装为全局 skill（见下）。下一步可加一个轻量"写实度/相关度"自检（如二次让模型看图打分，不达标自动换 seed 重生成）。

6. **一条命令端到端**（低）：`publish-blog.sh` 增加 `--gen-banner "<prompt>"`，把 banner 生成也纳入同一命令，实现"写完 md → 一条命令上线 blog+公众号+封面"。

7. **M3 并入**（低）：把小红书发布也纳入 publish-blog.sh 的 `--xhs` 开关，三平台一致入口。

---

## 附：推荐的标准发布动作（给模型/人）

```bash
# 1. 写好 src/content/blog/<slug>.md（含完整双语 frontmatter + 版权块）
# 2. 生成写实封面
bash .agents/skills/banner-creator/generate-banner.sh "<slug>" "<english scene prompt>"
#    把打印出的 heroImage 行填进 frontmatter
# 3. 一条命令发布 blog + 公众号
scripts/publish-blog.sh src/content/blog/<slug>.md --wechat --theme blue
```
