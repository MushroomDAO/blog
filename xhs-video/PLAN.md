# 小红书内容线 · 定位与流程

## 定位

小红书账号（Mushroom.cv）跟 blog + 公众号是**互补关系**，不是同一份内容换个平台发：

- 公众号/blog：完整文章，深度技术拆解，读者已经在"研究模式"
- 小红书：**视频为主，图文为辅**，服务的是还没决定要不要花时间研究的人——先靠一个具体
  痛点把人截住，再决定要不要往下看

## 核心叙事逻辑：以终为始

不是"这周 blog 发了什么就搬运什么"，是反过来走：

1. **起点是人，不是技术**：AI 是服务人类的工具，但普通人和中小企业/组织要用好 AI，
   中间隔着一层"怎么协作"的门槛——就像智能手机，会用和不会用的人能力差距很大，
   AI 时代这个差距会更大。
2. **终点是问题，不是产品**：先列个体或中小组织真实会卡住的场景/痛点（报销单据手动
   录入太慢、合同条款人工比对费时、客户咨询回复跟不上……），这些痛点清单本身可能先
   整理在 blog 上（作为"问题地图"）。
3. **中间是路径，不是安利**：从痛点出发，反向找 blog 已经写过的开源项目/Agent 方案，
   拼出"这个痛点 → 装什么开源模型/工具 → 怎么搭 Agent → 最终效果"这条路径，做成一条
   视频。

**举例说明思路**（假设性示例，不是已定选题）：企业发票报销手动录入慢 → 找到 blog 上
写过的某个开源 OCR/文档理解模型 + Agent 开发方案 → 组合起来 → 效果是"用手机拍照就能
快速录入报销单"。视频讲的是"这个痛点怎么被解决掉的"，不是"这个模型参数有多牛"。

## 选题来源与流程

```
blog 已发布文章（开源工具/Agent方案）
        ↓ 反向匹配
个体/中小组织的真实痛点场景（可能先沉淀成 blog 的"问题地图"文章）
        ↓ 选题成型
xhs-video/topics.yml 登记一条选题（status: idea）
        ↓ 写脚本
xhs-video/drafts/<slug>/script.md（视频脚本：痛点钩子 → 方案路径 → 效果展示 → 引导）
        ↓ 制作（复用已有工具栈，见下）
剪好的视频文件 → 交给我（放固定目录，见 README）
        ↓ 配套图文帖
xhs-video/drafts/<slug>/note.md（用 pipeline/m3/note-template.md 结构）
        ↓ 发布（见下节"发布路径"）
topics.yml 状态更新为 published，回填小红书笔记链接
```

## 产出节奏

目标**每周 2 条高质量视频**，配套图文帖看情况加发（不是每条视频都必须配图文）。
这个节奏低于"开源仓库开盒"系列（目标每周 3 条起、现实每天 1 条封顶）——原因是这条线
每条视频要多一步"痛点场景调研+路径设计"，不是单纯的"跑一遍开源仓库给结论"。

## 制作工具栈（复用已有，不新增）

脚本用 Claude Code、剪辑用 video-use、配音用 VidDub CosyVoice2、全自动化用
OpenMontage/html-video——跟 [[project_oss_teardown_video_series]] 里记的是同一套。

## 发布路径（关键：不绕过 MediaBot）

`~/Dev/tools/MediaBot` 是这个生态里唯一被授权碰真实账号的发布网关，硬规矩是
"视频/图文制作 skill 永远不直接发布，发布必须走 PublisherProvider 审批网关"
（[[project_oss_teardown_video_series]] 记录过这条不变量，2 天前刚确认过）。

现状（2026-08-28 盘点）：

| 内容类型 | MediaBot 能力 | 状态 |
|---|---|---|
| 小红书图文 | `src/providers/publisher/xiaohongshu.ts`，驱动 `xhs` CLI | **已就绪**，cookie 已修好（见 [[project_xhs_cookie_source]]） |
| 小红书视频 | 无 | **缺口**，需要新建 `XiaohongshuVideoPublisher`，走 `~/tools/social-auto-upload` 的 `sau xiaohongshu upload-video` |
| MediaBot 账号配置 | `~/.mediabot/config.json` | **未初始化**，`mediabot providers` 目前只有 dryrun，还没配真实小红书账号 |

用户已确认（2026-08-28）：视频发布走"扩展 MediaBot"路线，不单开旁路。

### 落地还差三步（下一次专门碰 MediaBot 仓库时做，不在这个仓库里做）

1. `mediabot init` + 配置 Mushroom.cv 小红书账号（secret 走 `mediabot secret set`，不进
   `config.json` 明文——这是 MediaBot 的不变量#8）。
2. 新建 `XiaohongshuVideoPublisher`（参考现有 `xiaohongshu.ts` 图文 provider 的结构，
   驱动 `sau xiaohongshu upload-video`），且必须有人工watch跑一遍并标记
   `verified: true`（不变量#5，未验证的 selector 拒绝发布）。
3. 把这个仓库 `xhs-video/drafts/` 里的草稿接进 MediaBot 的 compose/queue 流程，
   或者先手动 `mediabot run`/`approve` 单条测试。

在这三步落地前，图文帖可以走 MediaBot 现成的 provider 发布；视频只能先人工发
（我剪辑/生成草稿，你在小红书 App 里手动发布），或者用 `sau xiaohongshu upload-video`
先跑一次性的人工监督测试（不建常驻自动化）。

## 跟另外两条视频线的关系

- **Spore Cast**（`video-column/`）：付费专栏，5-7 分钟深度实操，blog 自建播放器+
  Cloudflare Stream 付费墙，等用户拍板四个开放问题才启动。
- **开源仓库开盒**（`daily-video/`）：免费长视频，YouTube/B站分发，"从要构建的产品
  倒推该测哪个仓库"的选题逻辑，跟这条线的"以终为始"是同一个方法论用在不同场景。
- **本条线（小红书）**：免费短内容，视频为主图文为辅，"从个体/中小组织痛点倒推该配
  哪个开源方案"，天然是前两条线的**上层引流/验证层**——个体的模糊痛点在这里先被
  验证是不是真痛点，验证过的再考虑要不要长出一条完整的开源仓库测评或付费深度内容。
