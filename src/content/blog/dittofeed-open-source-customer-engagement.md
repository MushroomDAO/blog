---
title: "Dittofeed：开源的全渠道用户消息自动化平台，Customer.io 的免费替代"
titleEn: "Dittofeed: Open-Source Omni-Channel Customer Engagement, a Free Alternative to Customer.io"
description: "Dittofeed 是一个 MIT 授权的开源用户消息自动化平台，支持 Email、SMS、Push、WhatsApp 等多渠道，可视化旅程构建器 + 自托管部署，替代 Customer.io 和 OneSignal。"
descriptionEn: "Dittofeed is an MIT-licensed open-source customer engagement platform supporting Email, SMS, Push, and WhatsApp, with a visual journey builder and self-hosting — a free alternative to Customer.io and OneSignal."
pubDate: 2026-05-24
updatedDate: 2026-05-24
category: Tech-News
tags: ["Open-Source", "Customer-Engagement", "Marketing-Automation", "Self-Hosted", "SaaS-Tools"]
heroImage: "../../assets/images/dittofeed-open-source-customer-engagement-banner.jpg"
---

> **BLUF**：Dittofeed 是一个完全开源（MIT）的全渠道用户消息自动化平台，用可视化旅程构建器替代 Customer.io、OneSignal 等昂贵的商业 SaaS，支持自托管、Git 版本控制，以及 Email、SMS、Push、WhatsApp、Slack 多渠道消息推送。

> 📌 GitHub 仓库：
> https://github.com/dittofeed/dittofeed
>
> 📌 在线演示：
> https://demo.dittofeed.com/dashboard
>
> 📌 官方文档：
> https://docs.dittofeed.com/introduction

---

## 它解决什么问题？

任何有用户系统的产品，都面临同一个问题：**怎么在合适的时机给合适的用户发合适的消息**。

用户注册了但没激活怎么办？付费用户突然流失怎么触达？新功能上线怎么通知老用户？这些场景靠人工操作不现实，需要一套**消息自动化系统**。

市面上主流的商业解决方案——Customer.io、Braze、OneSignal——功能成熟，但价格不菲。Customer.io 基础套餐 $100+/月，Braze 面向企业，报价更高，且用户数据全部在第三方服务器上。

Dittofeed 做了一件事：**把这套能力完整开源，让团队自托管，数据留在自己手里，费用降为零**。

## 四个核心模块

**1. Journey Builder（用户旅程）**

可视化拖拽界面，构建基于事件或时间的自动化消息流。典型例子：

- 用户注册 → 立即发欢迎邮件 → 3 天后检查是否激活 → 未激活发提醒 → 7 天未响应发短信
- 用户升级付费 → 发确认邮件 → 30 天后发使用报告 → 续费前 7 天发提醒

每个节点可以设置条件分支、延迟、用户属性过滤，逻辑复杂度接近商业产品。

**2. Broadcasts（广播）**

一次性群发消息，支持按用户段（Segment）精确筛选接收人群。发布新功能公告、限时活动通知等场景。

**3. Segmentation（用户分组）**

基于用户属性（注册时间、地区、套餐类型、行为事件）创建动态用户段，支持多条件组合。用户段和旅程、广播联动，实现精准触达。

**4. Template Editor（消息模板）**

支持 HTML/MJML 手写模板，也提供低代码可视化编辑器。模板可以纳入 Git 版本控制——这对开发者团队来说是个关键优势，所有改动有记录可追溯，可在 CI 中测试。

## 支持的消息渠道

| 渠道 | 说明 |
|------|------|
| Email | 对接 Sendgrid、Amazon SES、Postmark 等主流 ESP |
| SMS | 短信推送 |
| Push | iOS/Android 移动端推送通知 |
| WhatsApp | WhatsApp 消息 |
| Slack | 工作区消息通知 |
| Webhook | 自定义 HTTP 回调，对接任意系统 |

## 数据接入方式

三种接入路径：

- **Segment**：如果已在用 Segment 做数据收集，可以直接接入
- **Reverse ETL**：从数据仓库（BigQuery、Snowflake）同步用户数据
- **Dittofeed API**：直接调用 REST API 推送用户事件和属性，最简单直接

## 开发者友好的细节

Dittofeed 在工程体验上明显区别于传统营销工具：

- **Git 工作流**：消息模板、旅程配置可以像代码一样提交到 Git，支持 branch、review、回滚
- **Testing SDK**：在 CI 中测试消息旅程的正确性，不用在生产环境手动 QA
- **自托管**：Docker Compose 一键部署，所有用户 PII 数据留在自己的 VPC
- **嵌入式组件**（企业版）：Journey Builder、Segment Builder 可以通过 iframe 或 React 组件嵌入到自己的产品中，支持白标

## 与竞品的直接对比

| 维度 | Dittofeed | Customer.io | OneSignal | Braze |
|------|-----------|-------------|-----------|-------|
| 开源 | ✅ MIT | ❌ | ❌ | ❌ |
| 自托管 | ✅ | ❌ | ❌ | ❌ |
| 价格 | 免费 | $100+/月 | 有免费层，付费贵 | 企业报价 |
| Email | ✅ | ✅ | ✅ | ✅ |
| Push | ✅ | ✅ | ✅ | ✅ |
| WhatsApp | ✅ | ✅ | ❌ | ✅ |
| Git 工作流 | ✅ | ❌ | ❌ | ❌ |
| CI 测试 | ✅ | ❌ | ❌ | ❌ |

## 适合哪些场景？

**适合**：
- B2C/B2B SaaS 产品，有用户激活、留存、转化的消息需求
- 重视数据隐私、希望用户数据自托管的团队
- 开发者主导、习惯 Git 工作流的工程团队
- 预算有限的早期团队，想用商业级功能但付不起商业产品价格

**不适合**：
- 无用户系统的纯内容站
- 非技术团队（部署和运维需要一定工程能力）
- 需要极高发送量且不想自建运维的场景（此时商业 ESP 可能更省心）

## 路线图亮点

Q3 2025 计划中的功能值得关注：
- **LLM 集成**：用 AI 辅助生成旅程、用户段和消息模板
- **Stripe 集成**：同步 Stripe 客户数据，实现付费行为触发的消息自动化
- **Git 资源管理**：在不同 workspace 之间迁移旅程和模板配置

**FAQ**

**Q：Dittofeed 和 Segment 是什么关系？**
A：Segment 是数据收集和路由平台（CDP），Dittofeed 是消息发送平台。两者互补——Segment 负责把用户行为数据收集并路由到各目标，Dittofeed 可以作为 Segment 的下游，接收用户数据后触发消息自动化。

**Q：自托管需要什么基础设施？**
A：Docker Compose 方式需要一台 Linux 服务器，官方建议至少 2 核 4GB RAM。依赖 PostgreSQL（主数据库）、ClickHouse（分析）、Temporal（工作流调度）和 Kafka/Redpanda（消息队列），这些都通过 docker-compose.yml 一并启动，无需单独配置。

**Q：License 是否允许商用？**
A：核心功能 MIT 授权，完全免费且可商用。多租户、白标嵌入等高级功能是闭源的企业版，需要联系官方授权。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: Dittofeed is a fully open-source (MIT) omni-channel customer engagement platform that replaces expensive SaaS tools like Customer.io and OneSignal. It features a visual journey builder, multi-channel messaging (Email, SMS, Push, WhatsApp), self-hosting via Docker, and developer-first features like Git workflows and CI testing.

> 📌 GitHub:
> https://github.com/dittofeed/dittofeed
>
> 📌 Live demo:
> https://demo.dittofeed.com/dashboard

## What Problem Does It Solve?

Any product with a user base needs to send the right message to the right user at the right time — activation reminders, churn prevention, feature announcements. The commercial tools (Customer.io, Braze, OneSignal) are mature but expensive, and they hold your user PII on their servers.

Dittofeed gives you the same capabilities, self-hosted, for free.

## Four Core Modules

**Journey Builder**: Visual drag-and-drop automation flows triggered by user events or time delays. Build flows like: user registers → check activation at day 3 → send reminder if inactive → escalate to SMS at day 7.

**Broadcasts**: One-off messages to segmented user groups — new feature announcements, limited-time offers.

**Segmentation**: Dynamic user segments based on attributes and behavioral events, with multi-condition filtering.

**Template Editor**: HTML/MJML templates or low-code visual editor. Templates can be checked into Git, reviewed, and tested in CI — a meaningful developer ergonomics advantage over competitors.

## Supported Channels

Email (Sendgrid, Amazon SES, Postmark), SMS, mobile Push (iOS/Android), WhatsApp, Slack, and custom Webhooks.

## Why Developers Prefer It

- Git-based workflows for templates and journey configs — full version history and rollback
- Testing SDK to validate message journeys in CI before production
- Self-hosted: user PII stays in your own VPC
- Docker Compose deployment: one command, all dependencies included (PostgreSQL, ClickHouse, Temporal, Kafka/Redpanda)

## Competitive Comparison

Dittofeed vs. Customer.io: MIT open source vs. $100+/month proprietary. Dittofeed adds Git workflows and CI testing that Customer.io lacks. Customer.io has a larger ecosystem and more mature support.

The trade-off is operational overhead: self-hosting means you own the infrastructure. For teams with engineering capacity, it's a clear win. For non-technical teams, the managed cloud tier (app.dittofeed.com) reduces that burden.

## Roadmap to Watch

Q3 2025 plans include LLM integration (AI-assisted journey and segment generation), Stripe customer data sync, and Git-based resource management for multi-workspace transfers.

**FAQ**

**Q: How does this relate to Segment (the CDP)?**
A: Complementary, not competing. Segment collects and routes behavioral data; Dittofeed receives it and triggers message automation. Dittofeed has native Segment integration.

**Q: What infrastructure does self-hosting require?**
A: Minimum 2 CPU / 4GB RAM Linux server. Docker Compose launches all dependencies (PostgreSQL, ClickHouse, Temporal, Kafka/Redpanda) in one command.

**Q: Is commercial use allowed?**
A: Core features are MIT-licensed — free and fully commercial. Multi-tenancy, white-label embedding, and certain enterprise features are closed-source and require a commercial license.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
