---
title: "两天，一个人，给博客搭完一套邮件订阅系统——不花一分钱平台费，读者数据全在自己手里"
titleEn: "Two Days, One Person: Self-Hosting an Email Newsletter — No Platform Tax, Your Readers Stay Yours"
description: "用 listmonk + Fly.io + AWS SES + GitHub Actions，给个人博客搭了一套完全自建的邮件订阅系统。中间有一次「以为要套 iframe」的纠结，和好几个只有真跑一遍才会暴露的真实 bug——包括三个不同厂商的 AI 审查模型独立抓出的同一个隐藏 bug。"
descriptionEn: "Self-hosted a full email newsletter for a personal blog with listmonk + Fly.io + AWS SES + GitHub Actions. Includes a near-miss over-engineering moment, and several real bugs that only surfaced by actually running the thing end-to-end — including one that three independently-run AI review models, from different vendors, all flagged as the same blocking issue."
pubDate: "2026-08-01"
updatedDate: "2026-08-01"
category: "Tech-Experiment"
tags: ["newsletter", "listmonk", "self-hosted", "AWS SES", "Fly.io", "GitHub Actions", "数字主权"]
heroImage: "../../assets/images/newsletter-subscription-system-listmonk-flyio-ses-banner.jpg"
---

**BLUF**：不用 Substack，不用 ConvertKit，不给任何第三方平台交"订阅税"——两天时间，用几个开源/按量计费组件，给这个博客搭了一套完全自建的邮件订阅系统。读者填邮箱、双重确认、每 2 天收一封摘要邮件，全程数据在自己手里。过程中有一次典型的"想把方案做复杂了"的时刻，也有好几个只有真的跑起来才会暴露的坑——其中一个，是三个不同厂商的 AI 审查模型各自独立跑一遍，都盯上了同一处问题。

## 为什么不直接用 Substack 这类平台？

Substack、ConvertKit、Beehiiv 这些工具确实好用，但有个绕不开的前提：读者名单是平台的，不是你的。平台随时可以改规则、抽成、限流，甚至关停——你能做的只有祈祷。这跟 Mycelium 一直在讲的"数字主权"是同一件事：表达者的读者关系，不应该攥在别人手里。

所以这次的方向很明确：自己搭。但"自己搭"不等于"从零发明轮子"——真正难的部分（双重确认防止别人拿你邮箱恶意订阅、退订令牌、防灌邮件骚扰、退信/投诉处理）早就有开源方案做得很好，自己要做的只是把这些部件拼起来，写好内容。

## 选型：每一样都有明确的"为什么"

- **listmonk**（开源邮件列表引擎）：双重确认、Altcha 无感防骚扰验证码、退订令牌全部内置，不用自己再踩一遍这些坑
- **Fly.io** 托管：无状态部署，空闲自动休眠、有请求自动唤醒，成本趋近于零（中间试过 Cloudflare Container，跑起来发现内存档位不够便宜，果断换方向——先花小成本验证再押注，比一开始就赌一个方案划算）
- **AWS SES** 发信：按量计费，不会像某些"免费层"邮件服务商那样每天硬顶 100 封，订阅人数一多就撑不住
- **GitHub Actions** 定时发送：不用自己的电脑 24 小时开机联网

## 那个"差点想复杂了"的瞬间

订阅表单怎么接是最容易想复杂的一步。第一反应是："listmonk 的确认页有验证码、有防重放 token，我肯定得套一个 iframe 把它嵌进来，或者自己写个后端代理转发。"

停下来先测了一下：listmonk 有没有把博客域名加进它的 CORS 允许来源？一条 `curl` 命令的事——结果发现**已经开了**。这意味着可以直接从浏览器发请求过去，不需要 iframe，不需要自建后端代理。原本以为"复杂方案才靠谱"的判断，被一次五分钟的实测推翻了。

现在博客底部那个订阅框，就是一个原生 `<form>`，用 `fetch()` 直接把请求送到 listmonk，原地显示"已提交"或者报错，不跳转、不弹窗、不套壳。

## 几个真实踩过的坑

写文档容易，跑起来才知道哪里有坑。下面这几个都是这次真实发生的：

**Banner 图用 SVG，网页正常、邮件里空白**。浏览器渲染 SVG 没问题，但大多数邮件客户端不渲染内联 SVG——网页确认页的 logo 显示正常，邮件里同一张图就是空的。换成 PNG 就好了。

**改设置的时候，把打码密钥原样传了回去**。后台接口读出来的密钥字段是打码的 `••••`，改别的字段（比如换个 logo 地址）如果直接把整个对象原样传回去，会把真实密码覆盖成打码字符串——刚修好的发信功能因为这个又坏了一次。

**静态站点框架生成的网址，不一定等于文件名**。有一篇文章文件名里带了句点和大写字母，框架生成路由时把这些字符处理掉了，导致邮件里那篇文章的链接和配图都指向了错误地址——不是 404，是安安静静地跳到首页，不仔细看根本发现不了。

**三个不同厂商的 AI 独立审查，都盯上了同一处**：发送脚本原本的逻辑是"等 30 秒确认发送完成，超时就报错"。三条完全独立的审查路径（不同公司的模型）不约而同标记了同一个问题：如果只是网络慢、发送其实还在正常进行，下次运行会把这批内容当成"没发过"重新发一遍——真订阅者会收到两封一样的邮件。后来改成了"待确认"状态机：没确认完成不算失败，留着状态等下一轮接着确认，绝不会因为等太久就另外重复发一次。

## 现在跑起来是什么样

订阅 → 收确认邮件 → 点确认 → 每 2 天收一封摘要（哪些新文章、banner+标题+摘要+链接）→ 随时可退订。整条链路走真实邮箱测过至少两轮，退信/投诉处理接了 AWS 官方的通知机制，定时发送交给 GitHub Actions 跑，不依赖任何一台常开的电脑。

内容生成那部分特意做成了可插拔的架构——现在只有"博客新文章"一个来源，以后想加别的（比如定期的行业趋势分析、只给订阅者看不上公开博客的笔记），写一个新模块接进去就行，不用动其他代码。

想收到这些更新，滑到这篇文章最下面，Footer 里就有订阅入口。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: No Substack, no ConvertKit, no platform tax to any third party — over two days, using a handful of open-source / pay-as-you-go components, this blog got a fully self-hosted email newsletter. Readers subscribe, double-confirm, and get a digest every 2 days — all data stays in our own hands. Along the way: one classic near-miss of over-engineering, and several real bugs that only surfaced by actually running the thing end-to-end — one of which, three independently-run AI review models from different vendors all flagged as the same blocking issue.

## Why not just use an existing platform?

Substack, ConvertKit, Beehiiv — these tools work well, but there's a fundamental catch: your subscriber list belongs to the platform, not you. Rules change, cuts get taken, throttling happens, services shut down — and there's nothing you can do about it. This is the same argument Mycelium keeps making about digital sovereignty: the relationship between an expressor and their readers shouldn't sit in someone else's hands.

So self-hosting was the clear direction. But "self-hosted" doesn't mean "reinvent everything" — the genuinely hard parts (double opt-in to stop malicious sign-ups, unsubscribe tokens, anti-spam, bounce/complaint handling) are already solved well by open-source tools. The actual job was wiring the pieces together and writing the content.

## The stack, and why each piece

- **listmonk** (open-source mailing list engine): double opt-in, an unintrusive proof-of-work captcha, unsubscribe tokens — all built in, so none of those easy-to-get-wrong parts had to be reimplemented
- **Fly.io** hosting: stateless deployment, auto-sleep when idle and auto-wake on request, cost approaching zero (an earlier attempt on Cloudflare Container got dropped once the memory tier turned out not cheap enough — better to spike small and pivot than commit to one path from the start)
- **AWS SES** for sending: pay-as-you-go, no hard daily cap like some "free tier" email services that break down once subscriber count grows
- **GitHub Actions** for scheduling: doesn't depend on any one machine staying powered on and connected

## The almost-over-engineered moment

The instinct for wiring up the subscribe form was: "listmonk's confirmation page has a captcha and an anti-replay token, so this has to go through an iframe, or a self-built backend proxy."

A five-minute check first: has listmonk's CORS allowlist already been opened up for the blog's own domain? One `curl` command answered it — **yes, it already had been**. That meant a direct browser `fetch()` call would work, no iframe, no backend proxy needed. The instinct that "the more complex plan must be the right one" got overturned by one quick test.

The subscribe box at the bottom of this blog is a plain `<form>` today — `fetch()` straight to listmonk, showing success or an error inline, no redirect, no popup, no wrapper.

## Real bugs, found by actually running it

Writing the design is easy; running it is where the bugs live. A few that actually happened this time:

**SVG logo — fine on the web, blank in email.** Browsers render inline SVG fine; most email clients don't. The confirmation page's logo looked correct; the same image in the email was just blank. Swapping to PNG fixed it.

**A masked secret, echoed back literally.** An admin API returns a password field masked as `••••`. Changing an unrelated setting (like a logo URL) by fetching the whole object and PUTing it back — without re-populating that masked field — silently overwrote the real password with the mask string itself. Sending broke a second time, from a fix meant to be unrelated.

**A framework's generated URL isn't always the filename.** One article's filename had a period and an uppercase letter; the static site framework normalized those away when generating its route. The email's link and image for that one article pointed to the wrong address — not a 404, just a silent redirect to the homepage. Easy to miss without checking.

**Three independent AI models, from different vendors, flagged the same thing.** The send script originally waited 30 seconds to confirm a campaign had finished, then errored out if it hadn't. Three separate review passes — different companies' models, run independently — all flagged the same issue: if the send was just slow (not actually failed), the next run would treat that batch as "never sent" and create a duplicate campaign — real subscribers would get the same email twice. The fix: a "pending" state that persists across runs instead of erroring out, so a slow send gets confirmed later instead of ever being retried as new.

## What it looks like running today

Subscribe → confirmation email → confirm → a digest every 2 days (new posts, banner + title + summary + link) → unsubscribe anytime. The full loop has been tested against real inboxes more than once; bounce/complaint handling is wired to AWS's own notification mechanism; scheduling runs on GitHub Actions, not dependent on any one always-on machine.

Content generation was built as a pluggable architecture on purpose — today there's only one source ("new blog posts"), but adding another (a periodic research digest, subscriber-only notes that never touch the public blog) just means writing one new module, nothing else changes.

Want these updates? Scroll to the bottom of this page — the subscribe box is right there in the footer.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
