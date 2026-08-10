---
name: forage
description: |
  每日信息雷达：巡检小红书关注列表/关键词、GitHub Trending、HuggingFace 新模型、
  X 时间线，按 preferences.yml 的偏好画像打分，命中的去 GitHub/HuggingFace 拉一手
  资料，产出带独立分析的每日选题清单交人工评审。

  Trigger when the user says: 雷达, 跑雷达, 今天有什么, 选题清单, xhs-radar,
  刷小红书, 看看有什么新东西。

  Read-only on all platforms. Never posts, comments, likes or follows.
---

# xhs-radar

## Mission

替代人工刷信息流。目标不是"看得多"，是**把值得写的线索捞出来，并且已经替你做完第一层调研**。

产出物落进 `source/YYYYMMDD-<slug>/`，后续由现有的 `source-scanner` → `blog-publisher`
链路接管。本 skill **不写文章、不发布**，只负责采集、匹配、调研、成稿前的素材整理。

---

## 非协商规则

1. **全程只读。** 不点赞、不收藏、不评论、不关注、不转发。`agent-reach` 本身
   就声明了不做写操作，不要绕过它去调用别的工具做这些事。
2. **巡检是短程的。** 单次 3-8 分钟，不做长时间连续会话。理由见下面「节奏」。
3. **不洗稿。** 采集到的原文只作为线索和事实来源，分析必须是独立的。
   原文观点要标明出处，不能改写后当自己的。
4. **一手资料优先。** 小红书/X 上看到的是二手解读，真正的素材必须从
   GitHub 仓库、HuggingFace 模型卡、论文原文拉。拉不到就在清单里标注
   「未找到一手源」，不要用二手内容凑。
5. **产出清单，不直接发布。** 当前处于人工评审阶段。

---

## 节奏

**每 1-2 小时一次短巡检，不是连续挂机。**

这一条是刻意设计的，不是偷懒：

- 小红书风控最主要的特征之一是长时间连续的自动化会话。连续几小时是主动撞枪口。
- 覆盖率不来自时长。关注列表过一遍 + 一批关键词搜索，几分钟就能覆盖完，
  而且比人肉刷更全（人会漏、会被推荐算法带跑偏）。

单次巡检的量级参考：关注列表增量全取，关键词搜索每词取前 20 条。
两次巡检之间的间隔加随机抖动，不要卡整点。

---

## 数据源与后端

先跑 `agent-reach doctor --json` 确认当天可用性，backend 会变。

| 源 | 取什么 | 后端 |
|---|---|---|
| 小红书 | 关注的人的新笔记 + 关键词搜索 | `agent-reach` → xhs-cli（**需 cookie 有效**） |
| GitHub | Trending + 关键词搜索 + 仓库详情 | `agent-reach` → `gh` CLI |
| X / Twitter | 时间线 + 关键词搜索 + Thread | `agent-reach` → twitter-cli |
| HuggingFace | 新模型、trending 模型 | **agent-reach 不覆盖**，直接调 HF API：<br>`https://huggingface.co/api/models?sort=trendingScore&limit=50` |

小红书 cookie 失效时的表现：`xhs -v status` 返回 `code: -101 无登录信息`。
**这时不要静默跳过**——在当天清单顶部写明「小红书源缺失，本清单只覆盖其余源」，
并提示用户重新扫码登录。少一个源却不说，等于谎报覆盖率。

---

## 打分

规则全部在 `preferences.yml` 里，那个文件是给人改的，改完立刻生效。

```
得分 = Σ(命中的 tags 权重) + Σ(命中的 entities 权重) + Σ(命中的 bonus)
命中任一 veto → 直接丢弃，不计分
```

然后按 `thresholds` 三级分流：收进知识库 / 进每日清单 / 建议深挖成文。

**排除自指标签。** `preferences.yml` 的 tags 里有 `Mycelium` 这类本站自己的项目名，
它们是统计副产物，拿去匹配外部内容没有意义。打分时跳过：
`Mycelium`、`Cos72`、`Sin90`、`AirAccount`、`CometENS`、`SuperPaymaster`。

**去重。** 打分前先比对 `src/content/blog/` 里已发过的仓库/模型名。
已经写过的直接归入 veto，除非有实质性新版本（大版本号变化、架构改动）。

---

## 调研（命中「建议深挖」后执行）

这一步是整个 skill 的价值所在，不能省。

1. **找一手源**
   - GitHub：仓库 URL、star 数、协议、最近提交时间、README、语言构成
   - HuggingFace：模型卡、参数量、量化版本、显存需求、许可证
   - 论文：arXiv 编号和摘要
   - 三者都找不到 → 标注「未找到一手源」，降级为「仅存档」

2. **按类型写延展分析**（方向见 `preferences.yml` 的 `angles`）
   - **模型类** → 部署步骤、硬件选型、成本估算、显存实测、同级对比
   - **工具/Skill 类** → 从安装到跑通的完整路径、适合谁、和现有工具的边界、踩坑点
   - **创业/商业类** → 创业者怎么用、适合哪个阶段、成本结构、可迁移到哪些行业
   - **架构/论文类** → 核心机制拆解、工程上能落地的部分、与本站已发文章的关联

3. **关联本站**
   查 `src/content/blog/` 有没有相关旧文，有就在清单里标出来。
   这是这个博客的差异化——不是孤立介绍一个新东西，而是放进已有的脉络里。

---

## 产出

### 每日清单

写到 `source/YYYYMMDD-radar/LIST.md`，人工评审用。每条包含：

```markdown
## [得分 34] 项目名 —— 一句话说清它是什么

- **线索来自**：小红书 @某人 / GitHub Trending / X
- **一手源**：GitHub URL（stars、协议、最近提交） / HF 模型卡 URL
- **为什么命中**：开源(10) + AI Agent(7.4) + 本地可跑(3) + 有成本数字(2.5)
- **本站关联**：与《某篇旧文》同一方向 / 无
- **我的初步判断**：值得写 / 只存档 / 存疑（说明理由）
- **延展角度**：具体列出准备怎么展开，不要写「深入分析」这种空话
- **缺口**：还需要确认什么（没跑过的部署步骤、没验证的性能数字）
```

排序按得分降序。**每条都要写「我的初步判断」，包括判断为不值得写的理由**——
这些否定判断是训练偏好画像最有价值的信号。

### 知识库

过了「收进知识库」线但没进清单的，写到
`~/mycelium-kb/content/mempalace/radar-YYYYMMDD-<slug>.md`，当弹药库存着。
格式参考该目录下已有文件的 frontmatter。

### 反馈沉淀

用户对清单的每次反馈（这条该写/不该写/角度不对）记到
`.agents/skills/xhs-radar/FEEDBACK.md`，格式：

```markdown
## 2026-08-09
- ❌ 判为「值得写」但用户否掉：<项目> —— 用户理由：<原话>
  → 调整：<具体改哪个权重，或加哪条 veto>
- ✅ 判为「只存档」但用户要写：<项目> —— 用户理由：<原话>
  → 调整：<...>
```

**每积累 10 条反馈，回头修一次 `preferences.yml` 并在 FEEDBACK.md 记录改了什么。**
这是这套东西从"关键词匹配"长成"有你的判断力"的唯一路径。

---

## 已知缺口与坑

- **小红书 cookie 会周期性失效**，需要人工扫码。没有自动续期方案。
  失效判据：`xhs -v status` 返回 `code: -101`。
- **HuggingFace 走裸 API**，没有 agent-reach 的统一错误处理，需要自己重试。
  可用端点（已验证）：
  `https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=50`
- **`gh` 的字段名在子命令之间不一致，本会话被咬了三次。** 每次表现都像
  「认证挂了」或「搜索无结果」，实际只是字段名错：
  | 要什么 | 用什么 | 不能用 |
  |---|---|---|
  | star 数（搜索） | `gh search repos --json stargazersCount` | `stargazerCount` |
  | star 数（单仓库） | `gh repo view --json stargazerCount` | `stargazersCount` |
  | 开源协议 | `gh api repos/O/N --jq .license.spdx_id` | `--json licenseInfo`（search 里不存在；repo view 里常返回 null） |
  **协议判定必须走 `gh api`。** 用 `gh repo view --json licenseInfo` 会把
  一堆有 MIT/Apache 协议的仓库误判成「未声明」——第 1 轮清单里每一条的
  协议警告都是这么来的，全是假的。
- **`gh` 的调试输出会污染 JSON。** 本机 gh 会往 stdout 打 `* Request at ...`
  追踪行，直接 `| python3 -c "json.load(...)"` 必然报
  `Expecting value: line 1 column 1`。所有 gh 调用都要写成：
  ```bash
  GH_DEBUG= gh search repos "..." --json ... 2>/dev/null | ...
  ```
  这不是 gh 坏了——认证是好的，只是输出多了东西。
- **得分阈值是拍的初值**，跑一周后必须按实际淘汰率重调。
