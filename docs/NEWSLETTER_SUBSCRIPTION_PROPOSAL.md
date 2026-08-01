# 订阅 / Newsletter 功能设计方案（待 review）

> 分支：`feature/newsletter-subscribe`
> 状态：**后端（listmonk + Neon + SES + 摘要生成/发送脚本）已跑通，当前阶段是前端订阅入口模块** —— 见第 10 节（2026-07-30 更新）
> 目标：在博客底部加一个「Subscribe」按钮，读者填邮箱、确认订阅后，收到我们定期整理的新文章摘要邮件（报纸风格：一个 banner 配一段文字，反复排布）。
>
> **已拍板的决策**（jason 已确认，不用再讨论）：
> - 发送频率：**每 2 天一次**，没有新文章就跳过不发
> - 发信服务商：**Amazon SES**（不用 Resend——免费层每天 100 封的硬顶，订阅人数一多就撑不住；SES 按量计费无此限制）
> - 发信域名：**mushroom.cv**（大概率用一个专属子域名隔离信誉，具体子域名待定）
> - 授权：可以在 Cloudflare 上部署常驻 Docker 进程（Cloudflare Containers），只要技术上可行

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
- 支持通过任意 SMTP 中继发信——最终选定 **Amazon SES**（原因见下）
- REST API 可以从外部脚本触发"创建 campaign + 发送"，正好用来接我们自己写的"新文章摘要生成"脚本

**listmonk 定了，但"跑在哪"这件事经过两轮调研（含一次 Codex 联网深度挑战）才定下来，详见 3.5 节。**

---

## 3.5 托管位置：A/B/C 三方案对比，目前在验证 C

listmonk 本身需要一个能跑 Postgres 数据库的地方，这块是主要的分歧点。三个方案，按"验证顺序"排列（不是按推荐顺序——C 是首选，A 是兜底）：

| | **方案 C（首选，正在验证）** | **方案 A（兜底）** | 方案 B（不推荐，仅记录） |
|---|---|---|---|
| listmonk 程序跑在哪 | **Cloudflare Container**（无状态） | Fly.io 小型 VM | Cloudflare Workers（全部重写，不再是 listmonk）|
| 数据库 | **外部免费 Postgres**（Neon 或 Supabase 免费层） | Fly.io 持久卷本地 Postgres | Cloudflare D1 |
| 月成本 | lite 档 ~$1.7/月，若需 basic 档 ~$7/月 | ~$6.5/月 | ~$0，但工程量巨大 |
| Cloudflare 原生程度 | 高（程序体本身在 Cloudflare 上）| 低（完全在 Cloudflare 之外）| 完全原生，但已经不是 listmonk |
| 风险 | 容器休眠后磁盘清空，但 listmonk 本身无状态、数据都在外部 Postgres，理论上没事；需要实测冷启动对"确认/退订链接"的影响 | 已验证可行，业界常见部署方式，风险最低 | 要自己重新实现双重确认、退订令牌、弹跳处理、模板——相当于从零做一个 listmonk 的阉割版 |

**为什么不是简单选 A**：Codex 联网核实后指出，Cloudflare Containers 是真产品（2026-04 GA），虽然磁盘是临时的（不能放 Postgres），但**如果把 Postgres 挪到外部**（Neon/Supabase 免费层），listmonk 这个程序本身完全可以跑在 Cloudflare Container 里——这样"数据在外部，但计算在 Cloudflare 上"，比方案 A（整个应用都在 Fly.io，跟 Cloudflare 没关系）更贴近"尽量都用 Cloudflare"的诉求，而且不用像方案 B 那样自己重写 listmonk 的核心逻辑。

**关键悬念**：listmonk 能不能塞进 Cloudflare Container 最便宜的 `lite` 档位（~256MB 内存，~$1.7/月）。如果可以，方案 C 完胜（更便宜 + 更 Cloudflare 原生）；如果 listmonk 内存占用逼得我们上 `basic` 档位（1GB，~$7/月），跟方案 A 的 Fly.io 成本基本打平，那就没有硬性理由放弃 Fly.io 的省心。

**2026-07-29 定案：回退方案 A（Fly.io），但复用方案 C 已经建好的 Neon Postgres，不用 Fly 自带的持久卷 Postgres。** 触发原因：spike 过程中 `instance_type` 被迫从 `lite` 升到 `basic`，成本优势消失，遂按上面的退出条件回退。实际部署比预想更省：listmonk 本身无状态，Fly machine 配了 `auto_stop_machines`（`min_machines_running = 0`），只在有请求时才计费，闲时成本趋近于 $0，比最初估算的 ~$6.5/月更低。部署位置：`pipeline/newsletter/listmonk-fly/`（`pipeline/newsletter/listmonk-container/` 的 Cloudflare Container spike 保留作记录，不再维护）。

Codex 建议的验证步骤（**正在按这个走**）：
1. 部署 listmonk 到 Cloudflare Container，指向 Neon 或 Supabase 免费 Postgres
2. 把 listmonk 的数据库连接池配置得尽量小（降低内存占用）
3. 实测：订阅 → 双重确认 → 退订 → 发一次 campaign → 容器休眠后再点确认/退订链接，看还灵不灵
4. 看 `lite` 档位扛不扛得住，扛不住就上 `basic`
5. 如果 `lite` + 外部免费 Postgres 跑得通 → 定方案 C；跑不通/需要 `basic` → 回退方案 A（Fly.io）

Neon vs Supabase 免费层的取舍：Neon 支持 scale-to-zero（不活跃时自动休眠，唤醒较快），Supabase 免费层是"一周不活跃就整个暂停"（需要手动去 dashboard 唤醒，对我们这种"两天发一次"的低频场景有一定风险）——**倾向选 Neon**。

---

## 4. 整体架构（方案 C，验证中；括号内为方案 A 的差异）

```
┌─────────────────────┐
│  blog.mushroom.cv    │  Astro 静态站（Cloudflare Pages）
│  底部 Subscribe 按钮  │──POST email──┐
└──────────────────────┘               │
                                        ▼
                         ┌───────────────────────────┐
                         │ listmonk on Cloudflare      │  订阅确认 / 退订 / 名单管理
                         │ Container（无状态，lite档）  │  （方案A：Fly.io 小型VM代替）
                         └─────────────┬─────────────┘
                                       │ Postgres 连接
                                       ▼
                         ┌───────────────────────────┐
                         │  Neon 免费 Postgres（外部）  │  （方案A：Fly.io 本地持久卷 Postgres）
                         └───────────────────────────┘
                                       │
                         ┌───────────────────────────┐
                         │  listmonk ──SMTP──▶ Amazon SES │  实际发信
                         └───────────────────────────┘

┌───────────────────────────────────────────────────────┐
│  定时任务（cron，复用 update-analytics.sh 同款套路）       │
│  1. 读 Astro content collection：拿最近 2 天周期内的新文章  │
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

## 7. 决策记录

**已拍板**：
1. ~~发送频率~~ → **每 2 天一次，没新文章就跳过不发**
2. ~~发信服务商~~ → **Amazon SES**（Resend 免费层 100 封/天硬顶，订阅量一大就撑不住；分组也绕不开这个总量限制）
3. ~~发信域名~~ → **mushroom.cv**（子域名待部署时定，如 `updates.mushroom.cv`）
4. ~~托管方式~~ → 见第 3.5 节，**正在验证方案 C**（Cloudflare Container + Neon），跑不通回退方案 A（Fly.io）

**还需要你拍板**：
1. **订阅入口交互**：简单跳转到 listmonk 自带的订阅页，还是我们在 Astro 里做一个更好看的自定义弹窗（工作量更大，但视觉统一）？
2. **AGPL 许可证边界**（Codex review 指出原方案说法过于绝对）：只要我们**不修改 listmonk 源码**、只是部署官方镜像自用，AGPL 对我们没有额外义务；但如果以后为了适配需求去改了 listmonk 的代码，AGPL §13 的网络传播条款就会要求向能访问这个服务的人提供修改后的源码——**目前计划是不改源码，只用它的 API**，这条先记录在案，以后万一要改源码再重新评估
3. **合规细节**（Codex review 指出原方案完全没提）：订阅表单需要一句同意文案（比如"提交邮箱即代表同意接收更新邮件，可随时退订"）、邮件需要带标准的 `List-Unsubscribe` header（大部分邮件客户端会识别并显示"一键退订"按钮，比邮件里的文字链接更可靠）、以及一份简单的"我们怎么处理你的邮箱数据"的说明——这些不需要复杂的隐私政策，但至少要有一两句话

---

## 8. 上线前必须完成的检查清单（2026-07-30 核对实际状态）

- [x] ~~反向代理/白名单~~ → **降级为非阻塞项**：实测 listmonk 公开订阅页已内置 **Altcha**（工作量证明验证码，浏览器自动求解），防灌邮件骚扰已经被 listmonk 自己解决，不需要额外接 Turnstile；但 `/admin` 后台仍是密码保护、无路由级隔离地暴露在 Fly.io 公网 URL 上，建议后续补 Cloudflare Access，见第 10.6 节
- [x] ~~Cloudflare Turnstile~~ → 不需要，listmonk 自带 Altcha 已覆盖
- [ ] 确认 SES 的 bounce/complaint 是走 SNS webhook 回调 listmonk（**阻塞中：IAM 权限不够**，任务 #14）
- [ ] mushroom.cv 发信子域名的 SPF / DKIM / DMARC 配置完成，且用 Gmail / Outlook / iCloud 测试账号做过真实送达测试（状态待验证，AWS 已批准生产配额但未做真实送达测试）
- [x] cron 脚本有状态持久化（记录上次发送到哪）→ `send-newsletter.sh` + `last-sent.json` 已实现，失败不更新状态、可安全重试；`flock` 防止并发/重复调度重复发送；`last-sent.json` 记录已发送 slug 集合（而不仅是时间戳），避免同一天发布的多篇文章因为 `pubDate` 只写日期没写时间而被误判"已经发过"从而永久漏发（Codex review 发现，2026-08-01 修复）
- [~] 邮件模板：`build-digest.py` 已处理无 heroImage 兜底（`favicon.svg`）、绝对图片 URL、最多 7 篇上限；暗色模式/手机端渲染/纯文本兜底版本未验证
- [ ] 邮件带标准 `List-Unsubscribe` header，订阅表单有同意文案 → 待验证（listmonk 通常自动加，需实测一封真实邮件的 header）
- [ ] 全链路真人测试：自己订阅 → 收确认邮件 → 点确认 → 收一期摘要 → 点退订 → 确认真的退订成功 → **等前端入口做完后一起测**

## 9. 下一步

**当前阶段：可行性验证（spike），不是正式实现**——先花小成本确认方案 C 能不能跑通，再决定要不要投入完整实现。

1. [进行中] clone listmonk，研究能否塞进 Cloudflare Container `lite` 档
2. [进行中] 起草 Container 部署配置
3. [需要 jason] 创建 Neon 免费 Postgres 项目
4. [需要 jason] 确认/创建 Amazon SES 账号，验证 mushroom.cv 发信子域名
5. 部署 + 跑通端到端测试（订阅/确认/退订/发送/容器休眠唤醒后链接仍有效）
6. 根据结果定案方案 C 或回退方案 A，更新本文档

**验证通过后的正式实现步骤**（不变）：
1. 部署 listmonk 到定案的托管位置 + 反向代理白名单，配置 SES SMTP 中继
2. 配置发信域名 SPF/DKIM/DMARC，做真实送达测试
3. Astro 端加 Subscribe 组件（按钮 + 表单 + Turnstile）
4. 写 `pipeline/newsletter/build-digest.py`（读 content collection → 生成报纸风格 HTML，处理图片兜底）
5. 写 `scripts/send-newsletter.sh`（调用 listmonk Campaign API，带状态持久化）+ crontab（每 2 天一次）
6. 走一遍第 8 节的检查清单，全部打勾后再面向真实订阅者发送

---

## 10. 前端订阅模块设计（当前阶段，2026-07-30）

### 10.1 现状核查

后端比原计划更成熟：listmonk 已跑在 Fly.io（`pipeline/newsletter/listmonk-fly/fly.toml`，接 Neon Postgres）；`build-digest.py`（生成报纸风格摘要 HTML）+ `send-newsletter.sh`（调 campaign API 发送，带 `last-sent.json` 状态持久化防重发/漏发）都已写好；AWS SES 已经批下生产配额（50,000 封/天，14 封/秒，刚出 sandbox）。

**实测确认**（`curl` 探测 `list.mushroom.cv`）：
- 公开订阅页 `https://list.mushroom.cv/subscription/form` 返回 200，页面 HTML 里能搜到 `altcha`/`captcha` 字样 —— listmonk 原生内置了 **Altcha**（工作量证明式验证码，浏览器端自动求解、用户完全无感），防灌邮件骚扰这条已经被 listmonk 自己解决，**不需要我们另接 Cloudflare Turnstile**，原方案这条可以简化掉
- `/admin` 返回 307（跳转登录页），只受密码保护，没有反向代理白名单隔离——整个应用暴露在公网。个人博客场景下风险可接受，但建议后续加固，见 10.6
- 前端订阅入口：**0%**，`src/`、`Header.astro`、`Footer.astro`、`BlogPost.astro`、`index.astro` 全部搜不到一处 Subscribe 相关代码，是本阶段唯一要交付的东西

### 10.2 集成方式：复用 listmonk 自带订阅页，不重新造轮子

listmonk 的公开订阅表单里有一个 `nonce` 隐藏字段——页面加载时服务端生成的一次性令牌，配合 Altcha 防重放。这意味着**不能**把这段 HTML 静态复制粘贴到 Astro 页面里自己 POST（nonce 会失效）。真正可行的两条路：

| 方案 | 做法 | 取舍 |
|---|---|---|
| **A. iframe 内嵌（推荐，本阶段采用）** | Astro 里放按钮，点击弹出轻量 modal，modal 内 `<iframe>` 实时加载 `https://list.mushroom.cv/subscription/form?...`。每次都是真实加载 listmonk 页面，nonce/Altcha/双重确认全部有效，零新增后端代码 | 工程量最小、安全性最有保障（全部复用 listmonk 已踩过坑的现成能力）；样式局限于 iframe 内部（可在 listmonk 后台 Appearance 设置调主题色做基本融入，做不到像素级统一） |
| B. 自建表单 + Pages Function 代理转发 listmonk public API | Astro 自己做输入框 UI，提交给一个新增的 Cloudflare Pages Function，Function 转发到 listmonk 的 `/api/public/subscription` | 样式可完全定制；但这个静态站目前没有任何 SSR/Pages Function（需要引入 adapter 或 `functions/` 目录），还要研究清楚该 API 对 Altcha token 的校验方式，工程量和不确定性都明显更高 |

**结论：先做方案 A**。避免不必要的抽象和新基础设施——listmonk 已经把双重确认、防骚扰、退订令牌这些最容易出错的部分做完了，我们只需要把入口"焊"在博客的几个位置上。如果之后觉得 iframe 视觉太突兀，再升级到方案 B（10.6 节请你确认是否接受）。

### 10.3 独立目录/模块结构

新建 `src/components/subscribe/`：

```
src/components/subscribe/
├── SubscribeButton.astro   # 按钮/链接，variant prop 控制样式："header" | "footer" | "inline" | "hero"
├── SubscribeModal.astro    # <dialog> 弹窗 + iframe + 关闭按钮，原生 JS，不引入前端框架
└── config.ts               # 导出 LISTMONK_SUBSCRIBE_URL 常量（拼好 list UUID），全站改一处
```

`Header.astro`/`Footer.astro`/`BlogPost.astro`/`index.astro` 各自 import `SubscribeButton`；`SubscribeModal` 全局只需一份（放进共享 Layout 或直接放 `Footer.astro`，因为 Footer 在所有页面都渲染），多个按钮通过 `dialog.showModal()` 共享同一个弹窗。

### 10.4 四个入口位置

1. **Header**：RSS 图标旁加一个「📮 Subscribe」文字链接，视觉复用现有 `.rss-icon` 语言
2. **Footer**（全站所有页面共享）：社交链接下方加一个居中按钮 + 一句话（"每 2 天收一次新文章摘要，随时可退订"）
3. **文章页**（`BlogPost.astro`）：**（Codex 纠正：原文写反了）** 实际代码顺序是「相关文章 → Comments → Disclaimer」，插入点应放在**相关文章区块之后、`<Comments />` 之前**（`src/layouts/BlogPost.astro:395` 附近），做成稍醒目的卡片式 CTA——读者刚看完正文、还没进入评论区，这是转化率最高的位置
4. **首页**（`index.astro`）：轮播区上方放一条不打扰的横幅，Footer 之前再放一个稍大的订阅区块——对应"头部和底部都放"
5. **每封邮件**：`build-digest.py` 模板里已有固定 footer + 退订链接，现成的，不需要新做，只需要走一遍真人测试确认体验

### 10.5 反馈沟通

不新建反馈系统——个人博客量级用不上工单/表单。做法：campaign 的 `Reply-To` 设成一个真实监控的邮箱，邮件 footer 加一句"回复这封邮件告诉我们你的想法"；`send-newsletter.sh` 创建 campaign 时加一个 `from_email`/reply-to 字段即可。如果以后反馈量大到需要结构化收集，再考虑加个简单表单，现在不做。

### 10.6 Codex 评审结论（已按此修正方案，2026-07-30）

请 Codex 对本节做了严格评审，结论是**原方案把两项风险错误地降级为"非阻塞"**，已按其意见修正：

1. **iframe 方案本身成立**，但需要补 5 项验收条件才能上线：懒加载（点击后才设置 `src`，不参与首屏/SEO/性能）、`<dialog>` 弹窗、移动端与暗色模式适配 CSS、iframe 加载失败时"在新标签页打开"兜底链接、Safari ITP 下 session/nonce 实测。**本阶段实现里一并做**，不再是"以后再说"。
2. **模块目录需要多拆一个文件**：`SubscribeButton.astro` / `SubscribeModal.astro` / `SubscribeCta.astro`（文章页专用的卡片式样式，和 Header/Footer 的按钮视觉不同）/ `config.ts`（常量）/ `subscribeModal.ts`（iframe 懒加载 + 弹窗开关的原生 JS，从 `.astro` 文件里拆出来单独维护）。
3. **`/admin` 公网可达 —— Codex 明确否决"非阻塞"这个判断**：后台掌握订阅者邮箱和发信能力，被撞库影响的是 SES 账号信誉和发信合规，不是小事。**改为本阶段必须处理的 P0 项**：实测确认 `list.mushroom.cv` 走 Cloudflare 代理（DNS 解析到 Cloudflare anycast IP），具备用 **Cloudflare Access** 保护 `/admin*` + 管理 `/api/*`（只放行 `/subscription/*` 和 `/api/public/*`）的前提条件；`send-newsletter.sh` 调用管理 API 时需要加 Access Service Token header。**但受限于当前 `CLOUDFLARE_API_TOKEN` 权限范围不够读取 zone/Access 配置**，这一步需要你要么提供有 Zone/Access 权限的 token，要么直接在 Cloudflare Dashboard 里手动配置 Access 应用——我可以写好具体配置项（受保护路径、放行路径、Service Token 用法），但落地这一步需要你的账号权限。
4. **补充遗漏的安全项**：仓库里没有 `public/_headers`，博客站没有配置 CSP/`Referrer-Policy`/`X-Frame-Options`，也没有约束谁能 iframe 我们、我们能 iframe 谁。新增 `public/_headers`：博客侧限定只能 `frame-src https://list.mushroom.cv`；listmonk 侧订阅页要设 `frame-ancestors https://blog.mushroom.cv`（只允许博客嵌入），`/admin` 路径设 `frame-ancestors 'none'`（listmonk 侧这个配置需要在 Fly 部署的 nginx/listmonk 设置里加，属于后端改动，本阶段一并列入待办）。
5. **SES bounce/complaint SNS webhook —— Codex 明确否决"可以先上线、后补"**：这是发送生产邮件前的硬性合规前置条件，不是锦上添花（持续发给失效/投诉邮箱会直接拖累 SES 账号信誉，可能被限流甚至封号）。**改为 P0 阻塞项**，但当前卡在 IAM 权限不够（任务 #14），需要你在 AWS 账号里授权后才能继续 —— 本地也没有配置 AWS CLI 凭据，我无法直接查/改 SES 设置。
6. **发送频率**：这次提到"每日模板"，但之前拍板的是**每 2 天一次**——本轮方案文档默认维持不变，如果要改成每天告诉我一声即可（`build-digest.py --since-days` 默认值 + crontab 表达式，改动很小）。

**Codex 给出的最终优先级排序（P0 必须本阶段解决，P1 可延后）**：
- P0：`/admin` + 管理 API 隔离（需要你的 Cloudflare 权限）
- P0：SES bounce/complaint SNS webhook（需要你的 AWS IAM 权限）
- P0：SPF/DKIM/DMARC + `List-Unsubscribe` header 全链路实测（**实测发现连 SPF/DMARC 记录都还没配置**，需要先定发信子域名再去 AWS SES 拿 DKIM CNAME 值写入 DNS）
- P0：`public/_headers`（CSP/frame-src/Referrer-Policy）—— 这一项我可以直接做，不需要额外权限
- P0：iframe 懒加载 + 移动端/暗色/Safari/失败兜底验收 —— 这一项我可以直接做
- P1：自建表单代理方案（方案 B）可以延后，先用 iframe 方案上线

**结论：前端订阅模块（本阶段主线）+ `_headers` 我现在就做；`/admin` 隔离、SES webhook、DNS 记录这三项需要你的账号权限，做完前端后会给你一份具体的操作清单。**

---

## 11. 推翻 iframe 方案，改为直接 fetch()（2026-07-31）

jason 反馈体验：点开是个弹窗、弹窗里又整个跳转加载一次 listmonk 的独立页面，感觉像"套娃"，要求就是"输入邮箱、点确认，直接完事"。重新探测 listmonk 实例后发现方案 A（iframe）从一开始就不是唯一可行路径——**方案 B（自建表单直连 listmonk API）其实已经具备条件，只是第 10.2 节评审时没有实测就把它判得太难**。

**实测发现（`curl` 探测 `list.mushroom.cv`）**：
- `POST /subscription/form`（同一个 URL 既是订阅页也是提交目标）已经对 `https://blog.mushroom.cv` 开了 CORS：`Access-Control-Allow-Origin` 精确回显这个域名（不是 `*`，换一个 Origin 测试确认不会回显——是白名单，不是开放策略）。GET 页面、POST 提交、OPTIONS 预检、Altcha 的 challenge 接口（`/api/public/captcha/altcha`）和脚本（`/public/static/altcha.umd.js`）全部允许跨域。这大概率是之前"端到端测试"（任务 #11）阶段顺手配置过 listmonk 的 CORS 允许来源，一直没被前端用上。
- 表单字段：`email`、`nonce`（留空即可，不校验值）、`l`（list UUID，`575531a8-2817-4787-aa78-df7338e1747d`）、`altcha`（由 Altcha widget 自动写入隐藏字段）。错误响应是 HTML，用 `<h2>Error</h2>` 后面的 `<div>` 文本判断失败原因（实测触发过 "Invalid CAPTCHA."）。

**新方案**：`SubscribeForm.astro` 直接渲染真表单（email 输入框 + Altcha widget + 提交按钮），JS 用 `fetch()` 直接 POST 到 `list.mushroom.cv/subscription/form`，就地展示"已提交/失败"文案——**不跳转、不新开标签页、不套 iframe**。Altcha 的加载脚本只在 `Footer.astro`（全站必渲染一次）里放一份，避免自定义元素重复注册。已删除 `SubscribeButton.astro`、`SubscribeModal.astro`。

**2026-08-01 二次修正**：最初的四入口设计（Header/首页横幅/首页底部 CTA/文章页 CTA 各放一份表单）上线后 jason 反馈"文章页底部看起来像两个订阅框"——一张提示卡片 + 紧接着 Footer 的真表单，视觉上像重复。改成**全站只有 Footer 一处真表单**（`id="subscribe"`）：Header、首页横幅都是纯锚点链接跳过去；`SubscribeCta.astro`（文章页 + 首页底部曾经内嵌的卡片式表单）已删除，不再有独立的 CTA 表单实例。

第 10.2 节里"方案 B 工程量和不确定性都明显更高"这个判断被推翻——真正的不确定性只有 CORS 是否已开，验证一次就知道，不需要新增 Pages Function/后端代理。10.6 节里 P1 的"自建表单代理方案可延后"也一并作废，直接跳过 iframe 上线。

---

## 12. 内容源模块化（2026-08-01）

`build-digest.py` 原来是单体脚本：扫 `src/content/blog/`、拼 HTML、写文件全挤在一起。jason 计划以后往摘要邮件里加博客之外的内容——Google Trends AI 相关趋势分析、个人对最近文章/实验的看法（这类内容不打算发到公开博客，只给订阅者看）——所以重构成了内容源插件模式：

```
pipeline/newsletter/
├── sources/
│   ├── __init__.py     # 注册表：SOURCES = {"blog": blog, ...}
│   ├── base.py          # DigestItem schema（title/summary/pub_date/banner_url/link/body_html）
│   └── blog.py           # 现有博客扫描逻辑，原样迁移，行为不变
├── templates.py          # 卡片/正文两种渲染模板 + render(items)
├── notes/README.md       # "notes" 内容源的文档（脚本还没写，先定好目录和 frontmatter 约定）
└── build-digest.py       # 编排层：调用每个已注册源的 collect()，合并排序渲染
```

**加一个新内容源的步骤**：写 `sources/<name>.py`，实现 `collect(window_start, sent_ids) -> list[DigestItem]`，在 `sources/__init__.py` 的 `SOURCES` 里注册一行。`build-digest.py`、`send-newsletter.sh`、`templates.py` 都不用改。

**两个已知的具体场景，接口已经预留好**：
- **Google Trends 分析**：`link=None` 不行的话（如果打算配一篇独立分析页）就设 `link`；如果只想邮件里直接讲清楚不额外做页面，就设 `body_html`，两种都支持。
- **个人笔记/实验记录**（不上公开博客）：约定见 `notes/README.md`——frontmatter 三个字段（title/pubDate/summary）+ 正文转 HTML 塞进 `body_html`，`link` 留空。

**去重 key 的兼容处理**：`sent_slugs`（字段名没改，兼容老状态）里，博客条目继续用不带前缀的裸 slug（不破坏已有的 `last-sent.json`/`last-sent.seed.json`）；新内容源的 id 建议自己带前缀（比如 `trends:2026-08-01-xxx`），避免和博客 slug 撞车。

**验证**：重构后跑了一遍真实内容（10 篇文章，含之前修的 slug bug 那篇），渲染结果、去重、退订标签逐项比对跟重构前一致；`send-newsletter.sh` 走完整流程测过，行为没变。
