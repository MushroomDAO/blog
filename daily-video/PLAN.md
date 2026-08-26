# daily-video 规划记录

## 用户的原始想法（2026-08-26）

- 每天/每周产出 3～5 条内容，围绕 blog 提到的开源仓库做"开箱"评测。
- **为什么现在很少人真的做这件事**：普通信息分享者转发一个仓库"有多牛"很容易，但真正深入
  评测需要三样东西大部分人没有——① 技术基础 + AI 认知 + 动手部署能力；② 硬件条件（很多人
  电脑只有 16G，跑不动需要 24G/36G/64G 的本地小模型）；③ 时间。
- **以终为始**：用户想做的终点是一套**由开源组件拼装、面向中小企业和个体的 Local AI 产品**——
  local-first 指数据不出用户硬件边界，必须出边界时要经过隐私隔离。组件大部分来自开源仓库，
  部分自研定制。
- 所以视频系列不是漫无目的开箱热门仓库，而是**反向从"要拼出这套 local-first AI 产品需要哪些
  组件/能力/覆盖哪些场景"出发去找候选仓库**，找到后部署、实测、给结论（推荐给谁）——评测过程
  本身也是用户摸索这个产品该长什么样的过程。
- 节奏：现实目标每天 1 条封顶（要留时间部署测试录制剪辑），起始目标每周 3 条。全部免费。
- 想要：博客加视频频道；国内 B 站/海外 YouTube 按地域自动切换同一条视频；用现有的
  `/Users/jason/Dev/tools/MediaBot`（用户口头说的"medbo"，产出成片后落到本机固定文件夹，
  带同名元数据文件）产出视频后，自动同时发 B 站 + YouTube，发布后把真实链接写回博客展示，
  并且要记录发布状态、不能重复发布。

## 我的评估与建议

### 视频托管：YouTube + B 站，不用 Cloudflare Stream

`video-column/`（Spore Cast 付费专栏）用 Cloudflare Stream 是因为要防止完整版裸链接被
白嫖，按分钟计费的成本由付费收入覆盖。`daily-video` 是免费内容，没有收入抵消存储+流量
成本，自建播放器纯粹是找账单风险。YouTube/B 站免费存储+分发+推荐流量，受众也本来就在
这两个平台。

### 多平台分发：先做 YouTube + B 站，不铺 TikTok/Instagram

这两个平台原生支持"部署+评测"这类中长篇内容，同一条视频传两次边际成本接近零。
TikTok/Instagram 是竖屏短视频形态，跟评测内容不匹配，除非额外剪竖版切片——但"一天顶天
一条"的产出节奏没有这个余量，先不做。

### 站点集成：新增 collection + `/video/` 路由 + 地域路由 Function

- `src/content.config.ts` 新增独立的 `dailyVideo` collection（不是往 `blog` 塞 frontmatter，
  字段形状差太多：双平台链接、一句话结论）。
- 导航加"🎬 Video"入口（`Header.astro`）。
- 地域路由：博客本来就不是"纯静态到底"——`functions/` 目录下已经有 Cloudflare Pages
  Functions 在跑（`/api/search` 等）。照这个既有模式加 `functions/api/geo.js`，读
  `request.cf.country`，客户端 `VideoFrame` 组件按结果二选一渲染 iframe，不用把整站改
  SSR。**这个接口的返回值必须不缓存**——按访客地域而异，缓存住会把第一个访问者的国家
  发给后面所有人。

### 发布自动化：**发现 MediaBot 本身已经是带审批网关的编排系统，原计划的"独立轮询 skill"方案作废，需要重新对齐**

最初计划是在 blog 仓库里写一个独立的 skill：轮询 medbo 输出文件夹 → 调
`~/tools/social-auto-upload` 的 `sau` CLI（已确认支持 `sau bilibili upload-video` /
`sau youtube upload-video`，cookie 均需一次性手动登录）→ 记一份 `manifest.json` 去重 →
写回博客。

**用户纠正"medbo"实际是 `/Users/jason/Dev/tools/MediaBot` 之后，读了它的 `CLAUDE.md`/
`README.md`，发现这个假设不成立**：MediaBot 不是"一个只会吐 mp4 文件的录制工具"，而是一套
**已经有 `PublisherProvider` 抽象 + `ApprovalQueue` 审批网关 + `idempotency_key` 幂等去重 +
`CredentialStore` 密钥管理的完整发布编排系统**（`src/core/pipeline.ts` 的
`ingest → compose → validate → propose → executeDue`），并且有一条写死的不变量：
"Publishing stays with `PublisherProvider` behind the approval gate; the video skill never
publishes."——视频制作技能（`handson-video`）本身被设计成**永远不发布**，发布必须走
`PublisherProvider`。

现状缺口：
- MediaBot 的平台表里**没有 YouTube**（完全没做）。
- B 站**视频**发布走 Playwright，selector "已填但待实测确认"——MediaBot 的不变量 #5
  明确"未验证的浏览器 selector 拒绝发布"，也就是这条路径现在实际上是锁死的。
- 去重/幂等 MediaBot 已经用 `idempotency_key` 解决了，不需要 blog 仓库这边再单独维护一份
  `manifest.json`——重复维护等于自己造第二套账本，还容易和 MediaBot 的账本对不上。

在这套系统旁边另起一个独立的、绕过 `ApprovalQueue` 直接调 `sau` 的轮询 skill，等于在一个
**明确把"防止未经批准就发到真实账号"当作核心不变量**的系统边上开一个没有审批网关的第二条
发布通道——这正是 MediaBot 的不变量 #1 想要防止的事。这一点已经和用户同步，等对方确认要
不要：

1. 在 MediaBot 里新增 `bilibili-video` / `youtube-video` 两个 `PublisherProvider`（用
   `sau` CLI 当子进程包装，符合 MediaBot 自己"CLI 包装子进程"的集成优先级），走它已有的
   审批队列，`verified: true` 需要用户本人实测确认后才解锁真正发布；
2. 让"写回博客"这一步复用 MediaBot 已经支持的 blog 发布通道（README 里写"blog 是唯一
   审批后全自动、且可撤回的通道"），发布批准后自动在 `src/content/daily-video/` 生成对应
   markdown、填好双平台链接；
3. `daily-video/` 这边只需要保留内容 collection 和这份规划文档，不需要自己的
   `manifest.json`/独立轮询 skill。

这部分待用户拍板后再动 MediaBot 仓库的代码——那边的不变量是"系统对着真实账号安全"的
防线，不该在没有确认的情况下绕过或削弱。
