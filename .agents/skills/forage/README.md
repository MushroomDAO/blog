# forage

在信息流里觅食 → 分解成可用素材 → 输送进发布管道。

菌丝网络靠觅食、分解、输送养分活着（见 `protocol/MISSION.md` 的「循环」「传输」）。
这个 skill 干的是同一件事，只是养分换成了选题。

**它做什么**：巡检信息源，按你的选题指纹打分，命中的去 GitHub/HuggingFace 拉一手
资料并写初步分析，产出一份你能快速评审的清单。

**它不做什么**：不写成品文章、不发布、不做任何平台写操作（点赞/评论/关注/转发）。
那些交给已有的 `source-scanner` / `blog-publisher` / `social-auto-upload`。

---

## 一、为什么是 skill 不是独立 agent

后半程你已经有了。forage 只补前半程，产出物落进 `source/`，后面链路一行不改：

```
forage（新）                              已有，不动
────────────────────────────────        ─────────────────────────
巡检 → 打分 → 调研 → 清单
        ↓
source/YYYYMMDD-<slug>/  ──────────────→ source-scanner → blog-publisher
                                              ↓
                                         blog + 公众号草稿
                                              ↓（视频线）
                                         social-auto-upload → 小红书 / 视频号
```

做成独立 agent 等于把 source-scanner 和 blog-publisher 再实现一遍。

---

## 二、图文流程

### 1. 巡检（cron，无人值守）

每 1-2 小时一次，单次 10-15 分钟。**不是连续挂机**——长时间自动化会话是小红书
风控最主要的特征，而覆盖率不来自时长。

| 源 | 取什么 | 权重 |
|---|---|---|
| GitHub Trending + 搜索 | 新仓库、star 增速 | **一手，主力** |
| HuggingFace | `?sort=trendingScore` 榜 | **一手，主力** |
| Google Trends MCP | 验证热度方向 | 佐证 |
| X / Twitter | 时间线 + 关键词 | 一手，快 |
| 小红书 | 博主 `user-posts` + 关键词 + `feed` | **线索源，非内容源** |

小红书上多是二手解读，定位成"发现有这么个东西"，真正素材从 GitHub/HF 拉。
**博主名单只是来源之一，不要死盯，也不要高频抓取。**

### 2. 打分

规则全在 `preferences.yml`，那是给人改的文件，改完立刻生效。

```
得分 = Σ(tags 命中) + Σ(entities 命中) + Σ(bonus)
命中任一 veto → 丢弃
```

三条线分流：`收进知识库 12` / `进清单 20` / `建议深挖 30`。

**逆热度加分**：同等匹配度下，star 少、粉丝少的**加分**。作者本人发的小项目
（star 个位数）常常比被搬运过十轮的热门更有价值，热度排序天然埋没这类。

**桥接探测**（借鉴 OpenBiliClaw）：主动往"相邻但没写过"的方向探测——写了 70 篇
Claude Code、44 篇 MCP，那么 Agent 沙箱运行时、Skill 分发市场这类相邻领域应该被
主动捞，而不是等它撞进关键词表。命中桥接词的标注为「探测项」，你说对就升格进
正式权重，说不对就退出。这是防止权重表在已知圈子里打转的唯一机制。

### 3. 调研（过「建议深挖」线后执行）

这一步是全部价值所在，不能省：

1. **找一手源** — GitHub（URL/star/协议/最近提交）、HF（模型卡/参数量/量化/显存）、
   arXiv。三者都找不到 → 标注「未找到一手源」，降级为仅存档。
2. **按类型写延展**（方向见 `preferences.yml` 的 `angles`）
3. **关联本站** — 查 `src/content/blog/` 有无相关旧文。这是本站的差异化：
   不孤立介绍新东西，而是放进已有脉络。

### 4. 评审（本地页面）

产出两份，同一份数据：

- **`radar/index.html`** — 本地单文件页面，`open` 直接打开。**不部署、不上线**
  （这是你的选题库，公开等于把弹药亮给别人）。
  架构借鉴 Bento：数据以 JSON 存在文件顶部，用 File System Access API 写回自身，
  **不需要起服务器**。
- **`source/YYYYMMDD-radar/LIST.md`** — 真实数据源，`source-scanner` 吃它。

页面上每条支持：`[写] [存档] [不要] [备注]`，以及 **`[深挖]`** —— 点了就针对
这一条去拉更多一手资料、给出写作方向建议。自动过阈值和手点深挖走同一套逻辑。

### 5. 反馈沉淀

三种方式都行：页面点按钮 / 直接改 `LIST.md` / 口头告诉我。

全部记进 `FEEDBACK.md`：「我判断了什么 / 你否掉的理由 / 该改哪个权重」。
**每 10 条反馈回头修一次 `preferences.yml` 并记录改了什么。**

你的**否定**判断比肯定判断值钱——那是权重表里没有的信息。

---

## 三、视频流程

两类视频，共用目录结构，分叉在制作方式。

```
source/YYYYMMDD-<slug>/
├── LIST.md            觅食产出的线索 + 分析
├── article.md         成文（图文线的产物）
└── video/
    ├── script.md      口播稿 / 录屏解说词
    ├── raw/           你录的原始素材（录屏 mp4 / 口播 mp4）
    └── out/           渲染成片
```

### A. 录屏类（操作指导，3-5 分钟）

```
你录屏  →  放进 video/raw/
              ↓
        article.md 自动生成 video/script.md（把文章的操作步骤转成解说词 + 时间点）
              ↓
        HyperFrame 写 HTML 叠加层：字幕、高亮框、步骤标注、转场
              ↓
        渲染 → video/out/xxx.mp4
              ↓
        social-auto-upload → 小红书 / 视频号
```

**你只需要做一件事：录屏，扔进 `raw/`。** 剪辑、字幕、标注都是 HTML 生成的。

### B. 口播类（分享心得）

```
article.md  →  生成 video/script.md（口播稿，控制在 60-90 秒）
                  ↓
       你照稿录一条 → video/raw/    （或走 TTS，但真人声更好）
                  ↓
       HyperFrame 合成动态画面：动态字幕、关键词弹出、配图切换、motion graphics
                  ↓
       渲染 → video/out/xxx.mp4 → social-auto-upload
```

**这一步解决你说的「画面不变会降权」**：HyperFrame 让画面持续变化，
不是一张静态图配音。

### HyperFrame 的能力边界（重要）

它是 HeyGen 开源的 HTML→视频渲染框架：你（或 Agent）写 HTML/CSS 组件，
它用无头浏览器逐帧捕获成 MP4。为 AI Agent 设计，Claude Code / Codex 直接能驱动。

**但它不生成画面，只合成和增强已有素材。** 不做写实图像、不做数字人。
所以口播的人声画面必须你自己录，它负责让画面动起来。

本站还没写过 HyperFrame——以本站选题指纹（开源 + Agent 驱动 + 有部署路径），
这本身就是该写的一篇。

### 平台能力现状

| 目标 | 工具 | 说明 |
|---|---|---|
| 小红书图文 | `xhs post --images` | xhs-cli 原生 |
| 小红书视频 | `sau xiaohongshu upload-video` | **xhs-cli 不支持视频**，必须走 social-auto-upload |
| 视频号 | `sau tencent upload-video` | **微信没有公开的视频号发布 API**，浏览器自动化是唯一途径 |
| 公众号 | `pipeline/m2/index.js` | 已有 |

---

## 四、自动化程度

技术上能全自动（cron 串到发布）。**但前一个月不要。**

理由不是技术风险，是你的判断力还没被提取出来。现在 `preferences.yml` 只是 410 篇的
频次统计——它知道你写过什么，不知道你**为什么写这个不写那个**。那部分只存在于你
每次说「这个不行」的时候。跑够几十轮反馈后，权重表才配得上自动发布。

---

## 五、文件

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 执行规则（给 agent 读） |
| `preferences.yml` | 偏好权重表（**给人改**，改完立刻生效） |
| `FEEDBACK.md` | 反馈流水账 + 权重调整记录 |
| `README.md` | 本文件 |

## 六、待办

- [ ] `preferences.yml` 加 `bridges` 段（桥接探测词）
- [ ] `radar/index.html` 生成器
- [ ] 挖 Heinu1 会话语料（`~/.claude/projects/-Users-jason-Dev-tools-Heinu1/`，
      6816 条用户消息）提取表达偏好和工作流习惯，补进 `preferences.yml`
- [ ] 关注列表：`xhs-cli 0.6.4` 的 27 个端点里没有读取自己关注列表的，
      只有 `user/follow` 和 `user/unfollow`（写）。要拿得走 CDP 读关注页
      （`xhs-mcp-cdp` skill 是现成底座）。当前用手工名单绕过。
