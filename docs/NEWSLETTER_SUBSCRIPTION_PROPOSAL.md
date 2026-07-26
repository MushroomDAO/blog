# 订阅 / Newsletter 功能设计方案（待 review）

> 分支：`feature/newsletter-subscribe`
> 状态：**方案草案，未开始实现** —— 等待 jason review + 拍板技术选型
> 目标：在博客底部加一个「Subscribe」按钮，读者填邮箱、确认订阅后，收到我们定期整理的新文章摘要邮件（报纸风格：一个 banner 配一段文字，反复排布）。

---

## 1. 产品需求（复述确认）

1. **入口**：站点底部一个 Subscribe 按钮 → 弹出/跳转一个输入框 → 填 email → 提交
2. **确认**：提交后发一封确认邮件（双重确认 / double opt-in），点确认链接才算订阅成功——不是填了就算数，避免被人拿别人邮箱乱填
3. **内容生产**：后台定期（频率待定，见第 7 节）自动提炼「新发布的文章」，生成一份摘要
4. **邮件版式**："报纸风格"——开头一段固定介绍语，中间是若干个 **banner 图 + 标题 + 一段摘要** 的卡片块（每篇新文章一块），末尾固定的宣传文案 + logo + 退订链接
5. **阅读体验**：读者不用打开网站，在邮件客户端里刷标题+摘要就能了解"最近发了什么"；想看全文再点"阅读全文"链接跳回 blog.mushroom.cv
6. **退订**：邮件里必须有退订按钮/链接，一键退订

---

## 2. 历史调研回顾（本地 KB + 历史文章里翻到的相关内容）

翻了 `~/mycelium-kb`（basic-memory）和全部已发布文章，跟"订阅/邮件自动化"直接相关的只有两条，都不是现成答案，但提供了参考：

| 来源 | 内容 | 跟这次的关系 |
|---|---|---|
| [Dittofeed 一文](https://blog.mushroom.cv/blog/dittofeed-open-source-customer-engagement/)（2026-05-24 发过） | MIT 开源的全渠道用户消息自动化平台（Journey Builder + Broadcasts + Segmentation + Template Editor），Customer.io 的免费替代，自托管 | 功能强大但定位是**产品的用户运营**（注册欢迎邮件、流失挽回、行为触发），比一个"博客订阅每日/每周摘要"重得多，运维成本（Postgres + Redis + ClickHouse）对个人博客不划算，**不建议直接用**，但它的 Broadcasts 模块设计（按 segment 群发一次性消息）思路值得借鉴 |
| [ai-intel-workbench 一文](https://blog.mushroom.cv/blog/ai-intel-workbench-daily-dashboard-guide/)（2026-06-30 发过） | 本地 Agent 每天自动调研 5 个维度，生成可视化 HTML 情报看板 | 内容组织的"每日 digest"心智一致，但它解决的是"**从外部信源提炼**"（大厂动态/论文/开源），我们这次的信源是**自己的新文章**，简单得多——不需要 Agent 去抓取和判断相关性，直接读 Astro content collection 就有标题/简介/banner/日期，不需要额外的"智能提炼"这一步 |

结论：**没有直接能照抄的历史方案**，本地也没有别的"邮件订阅系统"技术选型记录——这是一个新命题，需要重新选型。

---

## 3. GitHub 开源方案调研（技术选型对比）

搜了 GitHub 上 star 数最高、目前仍活跃维护的自托管邮件订阅/newsletter 项目（star 数为 2026-07-26 查询快照，仅供相对量级参考，之后会持续增长）：

| 项目 | Star | 语言 / 依赖 | License | 定位 | 是否适合我们 |
|---|---|---|---|---|---|
| **[knadh/listmonk](https://github.com/knadh/listmonk)** | 22.4k | Go 单二进制 + Postgres | AGPL-3.0 | **专精**自托管邮件订阅/邮件列表管理：双重确认订阅、退订、弹跳处理、可视化后台、REST API 触发群发 | ✅ **推荐**——功能刚好覆盖我们要的一切，且"服务化使用不涉及分发"，AGPL 对我们没有实际约束 |
| [TryGhost/Ghost](https://github.com/TryGhost/Ghost) | 54.5k | Node.js + MySQL | MIT | 完整 CMS，自带会员+订阅+付费专栏 | ❌ 也可以只把 Ghost 当"订阅后端"单独跑、不迁移博客本体，但这样等于多维护一整个 CMS 只为了用它的订阅模块，比 listmonk 重得多，性价比更低，故仍不选 |
| [Billionmail/BillionMail](https://github.com/Billionmail/BillionMail) | 15.3k | Go，含完整 MailServer | AGPL/开源 | 自建邮件服务器 + 营销邮件一体化，彻底摆脱第三方 ESP | ⚠️ 自建 MTA 意味着要自己搞定 IP 信誉、反垃圾邮件黑名单——对个人博客风险大于收益，不建议 |
| [pentacent/keila](https://github.com/pentacent/keila) | 2.2k | Elixir + Postgres | AGPL-3.0 | 轻量版 newsletter 工具，也支持双重确认订阅、SES/SendGrid/Mailgun/Postmark 中继 | 备选——功能足够但社区规模小于 listmonk，没有发现具体的功能缺口，如果 Postgres+Docker 觉得 listmonk 太重可以考虑它 |
| [Mailtrain-org/mailtrain](https://github.com/Mailtrain-org/mailtrain) | 5.7k | Node.js + MySQL | GPL-3.0 | 老牌自托管newsletter工具 | 备选——项目活跃度低于 listmonk（上次更新 2025-10），不推荐 |
| [Notifuse/notifuse](https://github.com/Notifuse/notifuse) | 2k | Go | 开源 | 较新的邮件平台 | 观察中，社区规模小，暂不选 |
| DIY：Cloudflare Worker + D1 全手写 | — | 复用现有 hack5.net 同款技术栈 | — | 完全掌控，零额外服务 | ⚠️ 要自己实现双重确认、退订令牌、弹跳处理这些"listmonk 已经踩过坑"的细节，重复造轮子，性价比低 |

**推荐结论：自托管 [listmonk](https://listmonk.app)，作为"开源框架小改一下"的基础。**

理由：
- 双重确认订阅、退订、弹跳/投诉处理、订阅表单、REST API 全部现成，这些正是最容易踩坑的部分（比如退订令牌防伪造、弹跳率控制账号信誉）
- 支持通过任意 SMTP 中继发信——可以接 **Resend**（我们在 hack5.net 项目里已经在用 Resend 做付费资源）、Postmark 或 Amazon SES，不用自己当 MTA
- REST API 可以从外部脚本触发"创建 campaign + 发送"，正好用来接我们自己写的"新文章摘要生成"脚本
- 单 Docker 容器 + Postgres，可以跟 `xiaohongshu-mcp` 一样部署在 Mac Mini 上，成本 $0（只是多占一点内存/磁盘）

---

## 4. 整体架构

```
┌─────────────────────┐
│  blog.mushroom.cv    │  Astro 静态站（Cloudflare Pages）
│  底部 Subscribe 按钮  │──POST email──┐
└──────────────────────┘               │
                                        ▼
                         ┌───────────────────────────┐
                         │ listmonk（Mac Mini Docker）│  订阅确认 / 退订 / 名单管理
                         │  Postgres + 公开订阅表单API │
                         └─────────────┬─────────────┘
                                       │ SMTP relay
                                       ▼
                         ┌───────────────────────────┐
                         │   Resend / Postmark        │  实际发信（避免自建 MTA）
                         └───────────────────────────┘

┌───────────────────────────────────────────────────────┐
│  定时任务（cron，复用 update-analytics.sh 同款套路）       │
│  1. 读 Astro content collection：拿最近周期内的新文章      │
│     （title / description / heroImage / pubDate / slug）│
│  2. 渲染"报纸风格"HTML 模板（intro + N×banner卡片 + 固定footer）│
│  3. 调 listmonk Campaign API：创建 campaign + 发送给已确认订阅名单│
└───────────────────────────────────────────────────────┘
```

**关于"前端直连 listmonk"这一点，Codex review 后修正**：最初以为可以让 Astro 表单直接 POST 到 listmonk 的公开订阅接口、不需要中间层——**这个判断过于乐观**，有两个问题必须堵上：

1. **只暴露该暴露的路由**：listmonk 后台 `/admin/*` 和大部分 `/api/*` 是管理接口，绝不能让公网直接摸到；只有明确的公开订阅路由（`POST /api/public/subscription`，具体路径以我们实际部署的版本文档为准）可以对外，需要在 Mac Mini 前面加一层反向代理（Caddy/Nginx 或 Cloudflare Tunnel）做路由白名单，而不是把 listmonk 整个端口裸露到公网
2. **防灌邮件骚扰**：双重确认能防止"陌生人的邮箱被真订阅"，但防不了"有人拿别人的邮箱疯狂提交，让对方持续收到确认邮件"这种骚扰——订阅表单必须加 **Cloudflare Turnstile（人机验证）+ 同 IP/同邮箱的提交频率限制**，这两个是上线前的硬性前置条件，不是"以后再说"的优化项

---

## 5. 邮件内容设计（参考成熟 newsletter 范本）

调研了几个公认做得好的订阅邮件范本，抽出共同结构（这几个都是"文字+图片卡片"式 newsletter 的代表）：

- **TLDR Newsletter**（科技新闻日报）：顶部一句话导语 → 按分类分组的条目，每条「粗体标题 + 一句话摘要 + (▸ 阅读全文 X分钟)」→ 底部固定 CTA
- **Morning Brew**：更强的"人格化"开场白（一段轻松的话唠式导语）→ 图文卡片 → 底部固定的品牌 footer + 退订
- **Product Hunt Digest**：每条都是"缩略图 + 标题 + 一句话 + 数据角标"的卡片，视觉上像信息流

我们的版式（对应用户描述的"一个banner一个文字"）：

```
┌─────────────────────────────────────┐
│ 🍄 Mushroom Research Blog            │  ← 顶部品牌头
│ 2026-07-27 · 本周更新                 │
├─────────────────────────────────────┤
│ 一段固定/半固定的开场语                 │  ← 可以是纯固定文案，也可以让 AI 按本期
│（比如："这周我们看了 N 篇...主题是..."）│    文章自动生成一句"本期串场语"
├─────────────────────────────────────┤
│ [banner 图]                          │
│ **文章标题**                          │  ← 每篇文章一个卡片块
│ 一段摘要（沿用 frontmatter description）│
│ → 阅读全文                            │
├─────────────────────────────────────┤
│ [banner 图]                          │
│ **文章标题 2**                        │
│ 摘要...                              │
│ → 阅读全文                            │
├─────────────────────────────────────┤
│         ... 重复 N 次 ...             │
├─────────────────────────────────────┤
│ 固定宣传文案 + logo                    │  ← "🍄 Mushroom Research Blog｜非营利
│ 关于我们 / 免责声明 / 社交链接           │    个人科技观察..."（复用已有免责声明）
│ [退订]                                │
└─────────────────────────────────────┘
```

摘要文字直接复用文章 frontmatter 的 `description` 字段（已经是精炼过的中文摘要），**不需要额外 AI 摘要生成这一步**——省一层复杂度和 token 成本。

**几个需要定下来的细节（Codex review 提出）**：
- **每期条数上限**：按现在的发文节奏（1-3 篇/天），一周攒下来可能有 10+ 篇，一封邮件全塞进去太长、也容易被垃圾邮件过滤器判定为"图片过多的营销邮件"。建议**每期最多放 5-7 篇**（按热度/时间倒序取前 N），其余在末尾放一句"本期还有 X 篇，去博客看全部"
- **中英文**：博客是双语的（`description` + `descriptionEn`），邮件先只做**中文版**（跟公众号口径一致），英文版列为 v2 待办，除非你现在就想要双语邮件
- **图片是否必现**：`heroImage` 在 schema 里是可选字段（`.optional()`），不是每篇文章都保证有——模板要处理"没有 banner 图就只显示标题+摘要"的兜底情况，同时 banner 在邮件里必须是**绝对 URL**（`https://blog.mushroom.cv/...`），不能用站内相对路径

---

## 6. 与现有系统的复用关系，以及需要补的坑（Codex review 后更新）

- **免责声明**：邮件 footer 的文案基调复用 `Disclaimer.astro` 里的定位声明，但**不能直接把 Astro 组件塞进邮件**——邮件客户端不支持外部 CSS/现代布局，需要单独写一份"邮件安全"的纯内联样式 footer（表格布局、内联 style），内容上保持口径一致即可
- **定时任务模式**：复用 `scripts/update-analytics.sh` + crontab 的思路，但**要加状态记录**：脚本必须持久化"上一次成功发送到哪个时间点/哪些文章 ID"（比如写一个 `pipeline/newsletter/last-sent.json`），避免任务失败重跑后重复发送或漏发——不能像 analytics 脚本那样每次都是无状态的全量刷新
- **banner 图**：用文章已有的 `heroImage`，但要在生成邮件 HTML 时解析成绝对 CDN URL，并规定一个兜底图（没有 heroImage 时用），同时限制图片总数/总体积，避免触发反垃圾邮件的"图片邮件"评分

---

## 7. 需要你拍板的问题

1. **发送频率**：你说"每天"，但博客不是每天都发新文章（这几周大概 1-3 篇/天不等，但也有空窗期）。建议二选一：
   - **(a) 固定节奏**（如每周一次，"周报"），没有新文章就跳过不发——**推荐**，读者预期稳定，不会收到空邮件
   - (b) 真正按天判断，当天有新文章才发（更贴近你说的"每天"，但要处理"很多天没发"的空窗）
2. **发信服务商**：Resend（我们已在用）、Postmark 还是 Amazon SES？—— **待验证一个具体点**：listmonk 内建的"弹跳/投诉自动处理"是官方文档明确支持 SES/Postmark/SendGrid 的 webhook 回调，Resend 是否有等价的 bounce webhook 集成，我还没有实测确认，**部署前需要先验证这一点**，如果 Resend 不支持，弹跳处理就要退化成"listmonk 走 SMTP 发信，但弹跳靠 Resend 自己的 dashboard 人工看"，体验会差一些
3. **发信域名**：用 `blog.mushroom.cv` 还是单独开一个 `news.mushroom.cv` 子域名发信？—— 单独子域名可以隔离发信信誉（万一某次误判进垃圾箱，不连累主站其他邮件），**建议用独立子域名**
4. **listmonk 部署位置**：Mac Mini（跟 xiaohongshu-mcp 同机）还是找个小 VPS？—— 这里有个之前漏掉的点：Mac Mini 关机/断网影响的不只是"收不到新订阅请求"，**已经发出去的邮件里的"确认订阅"和"退订"链接也会一并失效**（因为这两个动作都要回调 listmonk）。如果 Mac Mini 不是 7x24 挂机，建议要么认这个风险、要么放到一个几美元/月的小 VPS 上换稳定性
5. **订阅入口交互**：简单跳转到 listmonk 自带的订阅页，还是我们在 Astro 里做一个更好看的自定义弹窗（工作量更大，但视觉统一）？
6. **AGPL 许可证边界**（Codex review 指出原方案说法过于绝对）：只要我们**不修改 listmonk 源码**、只是部署官方镜像自用，AGPL 对我们没有额外义务；但如果以后为了适配需求去改了 listmonk 的代码，AGPL §13 的网络传播条款就会要求向能访问这个服务的人提供修改后的源码——**目前计划是不改源码，只用它的 API**，这条先记录在案，以后万一要改源码再重新评估
7. **合规细节**（Codex review 指出原方案完全没提）：订阅表单需要一句同意文案（比如"提交邮箱即代表同意接收更新邮件，可随时退订"）、邮件需要带标准的 `List-Unsubscribe` header（大部分邮件客户端会识别并显示"一键退订"按钮，比邮件里的文字链接更可靠）、以及一份简单的"我们怎么处理你的邮箱数据"的说明——这些不需要复杂的隐私政策，但至少要有一两句话

---

## 8. 上线前必须完成的检查清单（Codex review 补充，非"锦上添花"）

- [ ] 反向代理/白名单：只暴露 listmonk 的公开订阅路由，其余端口/接口不对公网开放
- [ ] Cloudflare Turnstile + 提交频率限制，挂在订阅表单上
- [ ] 确认 Resend（或最终选定的 ESP）是否支持 listmonk 的 bounce webhook 集成
- [ ] 独立发信子域名的 SPF / DKIM / DMARC 配置完成，且用 Gmail / Outlook / iCloud 测试账号做过真实送达测试（不是只看"发送成功"）
- [ ] cron 脚本有状态持久化（记录上次发送到哪），失败重跑不会重复/漏发
- [ ] 邮件模板：无 heroImage 兜底、绝对图片 URL、图片数量/体积上限、纯文本兜底版本、暗色模式检查、手机端渲染检查
- [ ] 邮件带标准 `List-Unsubscribe` header，订阅表单有同意文案
- [ ] 全链路真人测试：自己订阅 → 收确认邮件 → 点确认 → 收一期摘要 → 点退订 → 确认真的退订成功

## 9. 下一步（方案确认后再动手）

1. 部署 listmonk（Docker + Postgres）+ 反向代理白名单，配置 SMTP 中继
2. 配置发信域名 SPF/DKIM/DMARC，做真实送达测试
3. Astro 端加 Subscribe 组件（按钮 + 表单 + Turnstile）
4. 写 `pipeline/newsletter/build-digest.py`（读 content collection → 生成报纸风格 HTML，处理图片兜底）
5. 写 `scripts/send-newsletter.sh`（调用 listmonk Campaign API，带状态持久化）+ crontab
6. 走一遍第 8 节的检查清单，全部打勾后再面向真实订阅者发送
