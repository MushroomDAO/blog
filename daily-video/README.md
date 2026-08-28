# daily-video

免费的"开源仓库开盒"视频系列——内容与发布记录放这里，不是 skill 代码本体
（skill 按仓库约定放在 `.agents/skills/daily-video-publish/`，见下方"和其他目录的关系"）。

## 是什么

围绕用户正在摸索的 **local-first AI**（数据不出用户硬件边界的开源 AI 产品栈）产品方向，
反向去找"要拼出这套东西需要哪些开源组件/覆盖哪些个体或中小组织的真实痛点场景"，逐个
部署、实测、给结论。同一次选题+评测剪两个版本：长版（8-15 分钟，YouTube+B站，完整部署
过程）+ 短版（≤8 分钟，小红书竖版，痛点钩子前置），可选配一条小红书图文帖。视频由
[MediaBot](/Users/jason/Dev/tools/MediaBot)（本机制作工作台，负责选题/脚本/录制/剪辑/配音）
产出，目标节奏每周 2-3 条选题（2026-08-28 起并入原小红书独立选题线，见 `PLAN.md`
"并入小红书"一节）。

完整背景和决策记录见 `PLAN.md`；统一选题队列见 `topics.yml`；每条选题的脚本/图文帖草稿/
本地预览见 `drafts/<slug>/`。

## 和其他目录的关系

- **`video-column/`（Spore Cast，付费专栏）**：两者完全独立。`daily-video` 是免费引流线，
  不接 Spore Cast 的 D1 + Cloudflare Stream 付费墙架构。跑顺之后，精品内容可能被挑出来
  并入付费专栏逻辑，但那是未来的事，现在按独立轨道维护。
- **`.agents/skills/daily-video-publish/`**：真正的发布自动化逻辑（扫描/去重/上传/写回博客）
  放在这里，跟着仓库既有的 skill 存放约定（`.agents/skills/` 是源，`.claude/skills/` 是本地
  镜像）。这个目录只放规划文档、选题队列、内容 collection（`src/content/daily-video/`）和
  发布记录，不直接发布——发布必须走 MediaBot 的 `PublisherProvider` 审批网关。
- **`.agents/skills/daily-video-planner/`**：选题登记 + 脚本/图文帖草稿 + 本地预览，产出
  写进这个目录，同样不负责发布。

## 内容怎么进博客

- Astro content collection：`dailyVideo`（定义在 `src/content.config.ts`），文件放
  `src/content/daily-video/*.md`
- 列表页：`/video/`，详情页：`/video/<slug>/`
- 导航：`Header.astro` 顶部菜单已加"🎬 Video"入口
- 同一条视频两个平台链接（`bilibiliUrl` / `youtubeUrl`）由 `VideoFrame` 组件按访客地域
  （`/api/geo` Pages Function 读 Cloudflare 边缘的 `request.cf.country`）自动二选一展示，
  国内默认 B 站、海外默认 YouTube，用户可以手动切换并记住选择
