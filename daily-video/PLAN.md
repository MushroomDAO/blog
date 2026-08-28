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

## 2026-08-28：并入小红书，从"两条免费视频线"合并成一条

用户原本让我单独规划一条小红书内容线（视频为主图文为辅，"以终为始"从个体/中小组织痛点
倒推 blog 已发布的开源方案），过程中用户自己发现：**这跟 daily-video 的"以终为始"逻辑是
同一件事**——两边的"终点"本质上是一回事：

- daily-video 的终点："要拼出 local-first AI 产品需要哪些组件/覆盖哪些场景"
- 小红书线的终点："个体/中小组织有哪些真实痛点"

一个 local-first AI 产品要覆盖的场景，本来就是个体/中小组织的真实痛点——这不是两个问题，
是同一个问题从"产品视角"和"用户视角"各问一遍。选题、找仓库、部署评测这个最贵的环节
（技术基础+硬件条件+时间，见上面"用户的原始想法"）没有理由做两遍。

**合并后的模型：一次选题+评测，剪两个版本，发三个渠道**

```
个体/中小组织痛点场景（= local-first AI 产品要覆盖的场景，同一件事）
        ↓
反查/物色能解决它的开源仓库，部署、实测、给结论（贵的部分，只做一次）
        ↓
daily-video/topics.yml 登记一条选题
        ↓
剪两个版本（同一份素材，不同的信息密度和时长）：
  · 长版（8-15 分钟）：完整部署过程+技术细节+结论 → YouTube + B站
  · 短版（≤8 分钟，见下面时长建议）：痛点钩子前置+压缩到"怎么被解决的"，
    砍掉纯技术细节 → 小红书（竖版）
        ↓
配套一条小红书图文帖（可选，不是每条视频都配）：
  daily-video/drafts/<slug>/note.md，结构见 pipeline/m3/note-template.md
```

不再维护两份选题队列——`xhs-video/topics.yml` 已并入这份文件同目录下的
`daily-video/topics.yml`，字段加了 `channels`（这条选题要剪给哪些渠道）。

**节奏**：不再分别定"daily-video 每周3条"和"小红书每周2条"两个目标——统一按选题算，
目标**每周 2-3 条选题**，起步阶段允许有的选题只出长版或只出短版（不是每条都必须三渠道
齐发），跑顺了再考虑要不要拉到"起始每周3条"的原目标。这个数字比合并前的"3+2=5"低，
但因为最贵的研究/部署环节只做一次，实际有效产出没有变少。

**发布路径不变**：仍然是"图文走 MediaBot 现成的小红书 PublisherProvider，长视频走
待建的 bilibili/youtube provider，短视频（小红书视频）也待建 provider"——三个视频
provider 目前都没在 MediaBot 落地，都在等这份 PLAN 里"待用户拍板"那三步做完。合并
不改变这条边界，只是把"该建哪些 provider"从两份清单合成了一份：`bilibili-video` /
`youtube-video` / `xiaohongshu-video`。

### 视频规格建议

用户的直觉是控制在 5-10 分钟、别让人没耐心看完——这个方向是对的，给个更具体的建议：

- **短版（小红书）目标 5-6 分钟，硬顶 8 分钟**。逻辑跟用户说的一致：痛点定义清楚了，
  感兴趣的人会看完，不感兴趣的人前 15-30 秒就划走了——所以真正要控制的不是总时长，
  是**开头 15-30 秒必须先把痛点讲清楚**，别铺垫太久，后面即使到 6-7 分钟，只要还在讲
  "怎么解决"，感兴趣的人不会因为长度弃看。硬顶 8 分钟是为了不让"手把手部署"环节膨胀成
  完整教程——那部分内容留给长版。
- **长版（YouTube/B站）不用卡同一个上限**，8-15 分钟都合理，这边观众本来就是冲着"完整
  部署过程"来的，耐心阈值不一样。
- **画幅**：小红书是移动端 feed，主流是**竖版 9:16 或 3:4**，横版 16:9 在信息流里会被
  压缩显示、完播率通常更差——但这批内容大量涉及"看代码/看终端"的实操画面，横版更利于
  看清内容。折中做法：**录制时保持关键画面（终端/浏览器窗口）居中且留边距**，这样剪辑
  时横版素材可以直接裁出一版竖版而不切掉重点内容，不需要重新录制两遍。长版剪辑可以用
  横版满幅；短版剪辑裁成竖版。
- 以上是通用平台经验，不是从这个仓库或 MediaBot 代码里验证出来的事实——正式定下来之前，
  建议录第一条前去小红书创作服务中心确认一遍当前时长/大小上限（平台规则会变，2026-08
  这个时间点没有专门查证）。
