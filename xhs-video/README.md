# 小红书内容线（视频为主，图文为辅）

跟 [[daily-video]]（开源仓库开盒，免费长视频，YouTube/B站）、Spore Cast（`video-column/`，
付费专栏）是三条独立轨道。这条线专门服务小红书账号 **Mushroom.cv**，定位、选题逻辑、
产出节奏见 `PLAN.md`。

- `PLAN.md` — 定位、"以终为始"选题逻辑、节奏、技术方案（MediaBot 缺口）
- `topics.yml` — 选题队列（从 blog 文章反推），状态机：idea → scripted → recorded → published
- `drafts/<slug>/` — 每个选题一份草稿目录：`script.md`（视频脚本）+ `note.md`（配套图文帖文案）

发布不在这个目录里执行——图文走 MediaBot 已有的 XiaoHongShu PublisherProvider，
视频待 MediaBot 新增 PublisherProvider 后同样走它的审批队列。这个目录只管选题和草稿，
不碰真实发布，原因见 `PLAN.md` 里的"发布路径"一节。
