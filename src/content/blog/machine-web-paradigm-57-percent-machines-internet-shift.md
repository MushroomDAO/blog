---
title: "57.5%：互联网的主角换了，只是大多数人还没发现"
titleEn: "57.5%: The Internet Has a New Protagonist — Most People Haven't Noticed"
description: "Cloudflare CEO Matthew Prince 2026年6月推文：全球HTML页面HTTP请求里，机器人占57.5%，人类只剩42.5%。这不是流量波动，是互联网三十年来第一次主角替换。梳理数据背后的结构、逻辑与每个人必须面对的现实。"
descriptionEn: "Cloudflare CEO Matthew Prince's June 2026 tweet: of all global HTML page HTTP requests, bots now account for 57.5% while humans trail at 42.5%. This isn't a traffic fluctuation — it's the internet's first protagonist swap in thirty years. An analysis of the structure, logic, and reality everyone must now face."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Research"
tags: ["AI Agent", "Web范式", "机器流量", "互联网", "Cloudflare", "pay-to-crawl", "AEO", "内容创作"]
heroImage: "../../assets/images/machine-web-paradigm-57-percent-machines-internet-shift-banner.jpg"
---

> **先把口径钉死。**  
> 2026年6月3日，Cloudflare CEO Matthew Prince 发推：全球HTML页面的HTTP请求里，机器人（bots）占比 **57.5%**，人类（humans）只剩 **42.5%**。他附了一句话："Welp, that happened faster than I predicted."  
>
> 他原本预测这个临界点在2027年底，后来改到2027年初，结果2026年中就到了。

这不是耸人听闻的标题，是统计事实。但"机器超过人"这个句子容易被误读——过度解读成科幻末日，也容易被轻描淡写成"不就是爬虫多了点嘛"。真实发生的事情，比这两种反应都更值得认真对待。

---

## 一、数字本身

Matthew Prince 推文的数字不孤立。

- **美国更极端**：机器人占国内Web请求的 **71.5%**，是全球最被自动化渗透的市场。
- **多家数据源交叉验证**：Imperva《2024恶劣机器人报告》显示自动化流量当年就破了50%门槛（51%）；Thales《2026坏机器人报告》给出2025年人类流量47%、机器人53%。
- **Cloudflare自家网络**（约占全球20%网站）：到2025年底，机器/人类已是约53% vs 47%。
- **增速剪刀差**：2025年AI驱动流量暴涨187%，增速约为人类网络活动的 **8倍**。

有一个细节需要单独说：57.5% 指的是 **HTTP请求数**，不是带宽（GB）。真正按流量字节算，人类仍占大头——因为视频。人刷视频吞掉的带宽，机器抓文本和结构化内容无法比。短期内在"字节维度"，机器还超不过人。

但这恰恰是理解这件事的关键切入点：**Web的"默认受众"正在从人变成机器，只是先体现在请求维度**。你每次点开一个页面，背后可能有几百个机器请求在同时读取它。

---

## 二、三股驱动力，不是一个来源

机器流量不是单一来源，是三股合力：

**LLM训练爬虫**：为喂大模型而批量抓取。Anthropic、OpenAI、Meta、各家中文模型厂商都有。数量级是此前学术爬虫的百倍到千倍。

**AI搜索/答案引擎**：ChatGPT Search、Gemini、Perplexity、国内的秘塔、360AI搜索。它们不再把用户送回原站，而是直接在答案里给结果。抓你，但不带你回流。

**自主Agent**：这是增速最快的一类。一个Agent执行一个购物比价任务，可能扫5000个网站——人类做同样的事逛5个。请求量是人类的千倍级，且随着Agent能力增强会继续放大。

Matthew Prince把这次变革类比 Web 从桌面端转向移动端——不是功能升级，是"人获取信息的方式彻底变了"。

---

## 三、旧的交换逻辑断了

互联网的商业模式建立在一个隐含假设上：**抓你的内容，最终会把用户送回来**。

传统搜索时代，Google爬虫抓页面、建索引，把用户导回原站，网站靠广告/订阅变现。这是内容创作值得投入的基础逻辑。

AI时代这条链断了。

Cloudflare 用 **crawl-to-referral ratio（抓取-导流量比）** 把这件事量化到了残酷：

- **Anthropic的爬虫**：每带来1个HTML回流，先抓了 **70,900页**。
- **OpenAI的爬虫**：带来和旧Google同等回流，难度高出约 **750倍**。

内容被读取，但人不来了。这是"易主"对内容方的真实代价。旧的"抓-回流-变现"三角已塌，内容创作者现在面对的是：被大量抓取，但广告收入、订阅收入的来源——真人访客——在减少。

---

## 四、为什么是Cloudflare先喊出来

Cloudflare 管着全球20%以上的Web流量，每天处理数万亿次请求——它既有数据，也有立场。

更重要的是，它早就动手了：
- **2024年9月**：让站长一键屏蔽AI爬虫，超100万客户启用封锁。
- **2025年中**：把新域名的AI爬虫默认策略改成 permission-based（需授权才许抓）。
- **下一步判断**：Web的下一步很可能是 **pay-to-crawl（付费抓取）**——从"能不能抓"走到"要抓可以，但你得付费"。

需要带着眼光看Cloudflare的这些动作：它是中间人。它既卖盾（爬虫屏蔽产品），也卖矛（AI Gateway，帮AI厂商更好地访问Web内容）。pay-to-crawl对Cloudflare来说是完美的商业模式——它坐在流量管道中央，抽取通行费。

这不是阴谋论，是商业逻辑。但这个方向如果成真，内容创作者和AI厂商之间会出现一个新的中间层，Cloudflare就是那个中间层。

---

## 五、37%是恶意的，指标已经失真

自动化流量里，并不全是"好机器人"。

按Cloudflare的分类：所有自动化流量中，**37%是恶意"坏机器人"**，合法爬虫只占14%。

这个数字有一个被低估的影响：**你后台看见的"阅读量"，可能已经掺了大量机器人**。小红书、公众号、独立博客的访问数据里，爬虫行为越来越多——它们触发了页面加载，但不是人在阅读。

"Vanity metrics"正在系统性失真。

这意味着：把流量数据涨跌当成"市场对你内容的反馈"，是踩进了一个正在扩大的坑。机器反馈不是市场反馈。流量数据作为决策信号的可靠性，在2025-2026年有结构性下降。

---

## 六、这对普通人意味着什么

不是做内容的人，不需要操心pay-to-crawl和crawl-to-referral ratio。但这件事会以更隐蔽的方式影响每个互联网用户。

**你获取信息的方式正在变**。当你在ChatGPT或Gemini里问一个问题，得到的答案经过了这个链路：原始内容→AI爬虫抓取→LLM训练或实时检索→AI综合生成答案→你收到。你没有直接接触原始内容，你接触的是机器对内容的处理结果。

这是效率提升，也是距离拉远。

**"真人在场"正在成为稀缺信号**。当大多数web活动是机器行为时，确认"这个互动是真人发起的"变得更有价值，也更难做到。Cloudflare已经在卖这个——Turnstile（人机验证）、Bot Management产品的定价在2025年提高了，因为需求在增长。

**你写的内容，第一个读者可能是机器**。这不是悲观的说法，而是一个新的设计约束。如果机器是内容的第一道过滤器——决定什么被索引、被引用、被推送给人——那么"让机器能准确理解你在说什么"和"让人读起来顺畅"同等重要。SEO让位给 **AEO（Answer Engine Optimization，答案引擎优化）**，这个转变已经在发生。

---

## 七、我的判断

这场转移有几个层面值得区分，因为混在一起说容易产生错误的恐慌或错误的乐观。

**第一，这是结构性的，不是阶段性的**。机器流量不会因为AI热度下去而减少——AI Agent的应用面在扩大，自动化工具在普及，这两件事都是单向过程。57.5%会继续涨，不会回到低于50%。

**第二，"机器主导"不等于"内容无价值"**。字节维度人类仍占大头，体验、情感、创作还是人的主场。但"内容的第一道分发"已经交给算法和Agent裁决——你写给人看，但先过机器这关。这两件事同时成立。

**第三，pay-to-crawl如果成真，对小创作者是双刃剑**。好处：内容被抓取该有补偿。坏处：站太小、没被索引，就直接从AI的答案里"消失"。大平台背书的内容和有钱入场的内容会更有优势。中小创作者的生存策略，不是反对机器，而是让自己"值得被机器读取且值得被付费"。

**第四，递归风险是长期的**。AI为训练目的抓取内容，用这些内容训练出来的AI生成新内容，新内容又被更多AI抓取——这个递归循环意味着Web内容库里AI生成内容的比例会持续增大。这会如何影响未来训练数据的质量，是一个目前没人能准确回答的问题，但方向是明确的。

---

**一句话总结**：互联网没有"死"，它只是换了主角——从人读网，到机读网。当57.5%的请求来自机器，游戏规则已经不同了，只是大多数人还在用旧规则打牌。

---

*数据来源：Matthew Prince (@eastdakota) Twitter/X 2026-06-03；Cloudflare Radar；Imperva Bad Bot Report 2024；Thales Bad Bot Report 2026；小红书笔记「Cloudflare CEO 马修·普林斯，揭开Web范式转移」作者陈堃，2026-07-24采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Let's nail down the exact scope first.**  
> On June 3, 2026, Cloudflare CEO Matthew Prince tweeted: of all global HTML page HTTP requests, bots account for **57.5%** while humans trail at only **42.5%**. He added one line: "Welp, that happened faster than I predicted."  
>
> He had originally predicted this tipping point would arrive by end of 2027, later revised to early 2027 — and yet here we are at mid-2026.

This isn't a sensationalist headline — it's a statistical fact. But the sentence "machines outnumber humans" is easy to misread: either over-interpreted as science-fiction doom, or dismissed as "what's the big deal, just a few more crawlers." What's actually happening deserves more serious attention than either reaction.

---

## 1. The Numbers Themselves

Matthew Prince's tweet figures don't stand alone.

- **The U.S. is even more extreme**: bots account for **71.5%** of domestic web requests — the most automation-penetrated market in the world.
- **Cross-validated by multiple data sources**: Imperva's *2024 Bad Bot Report* showed automated traffic surpassing the 50% threshold (51%) that year; Thales' *2026 Bad Bot Report* puts 2025 human traffic at 47% and bot traffic at 53%.
- **Cloudflare's own network** (covering roughly 20% of global websites): by end of 2025, machine-to-human traffic was approximately 53% vs. 47%.
- **Diverging growth rates**: AI-driven traffic surged 187% in 2025 — roughly **8 times** the growth rate of human web activity.

One detail deserves special mention: the 57.5% figure refers to **HTTP request count**, not bandwidth (GB). Measured by actual bytes transferred, humans still dominate — because of video. The bandwidth humans consume streaming video dwarfs what machines consume crawling text and structured content. In the near term, machines have not yet surpassed humans in the "byte dimension."

But this is precisely the key entry point for understanding what's happening: **the web's "default audience" is shifting from humans to machines — it's just showing up first in the request dimension**. Every time you open a page, there may be hundreds of machine requests reading it simultaneously.

---

## 2. Three Drivers, Not One Source

Machine traffic doesn't come from a single source — it's three forces combined:

**LLM training crawlers**: mass-scraping to feed large models. Anthropic, OpenAI, Meta, and every Chinese model vendor does this. The scale is one hundred to one thousand times that of previous academic crawlers.

**AI search / answer engines**: ChatGPT Search, Gemini, Perplexity, and domestic equivalents like Metaso and 360 AI Search. They no longer send users back to the original site — they deliver results directly inside the answer. They crawl you, but don't send traffic back.

**Autonomous Agents**: the fastest-growing category. A single agent executing a price-comparison task might scan 5,000 websites — a human doing the same thing visits 5. Request volume is three orders of magnitude above human behavior, and it will keep amplifying as agent capabilities grow.

Matthew Prince likens this shift to the web's transition from desktop to mobile — not a feature upgrade, but a fundamental change in "how people obtain information."

---

## 3. The Old Exchange Logic Has Broken

The internet's business model was built on an implicit assumption: **crawl my content, eventually send users back to me**.

In the traditional search era, Google's crawler indexed pages and directed users back to the original site; websites monetized through ads and subscriptions. This was the foundational logic that made investing in content worthwhile.

That chain has broken in the AI era.

Cloudflare quantified this with brutal precision using the **crawl-to-referral ratio**:

- **Anthropic's crawler**: crawls **70,900 pages** for every single HTML referral it generates.
- **OpenAI's crawler**: to generate the same referral volume as old Google, the effort required is roughly **750 times** greater.

Content is read, but people don't come. This is the true cost of the "change of protagonist" for content providers. The old crawl-referral-monetize triangle has collapsed. Content creators now face a reality where they are massively crawled, while the source of ad revenue and subscription revenue — real human visitors — is shrinking.

---

## 4. Why Cloudflare Was First to Speak Up

Cloudflare manages over 20% of global web traffic, processing trillions of requests daily — it has both the data and a stake in the outcome.

More importantly, it has already acted:
- **September 2024**: enabled site owners to block AI crawlers with one click; over 1 million customers activated the block.
- **Mid-2025**: changed the default AI crawler policy for new domains to permission-based (authorization required before crawling).
- **Next anticipated step**: the web's next chapter is likely **pay-to-crawl** — moving from "can you crawl?" to "you can crawl, but you have to pay."

Cloudflare's moves should be read with clear eyes: it is an intermediary. It sells both shield (crawler-blocking products) and spear (AI Gateway, helping AI vendors better access web content). Pay-to-crawl is a perfect business model for Cloudflare — it sits at the center of the traffic pipeline, collecting tolls.

This isn't conspiracy theory; it's commercial logic. But if this direction materializes, a new intermediary layer will emerge between content creators and AI companies — and Cloudflare is that layer.

---

## 5. 37% Is Malicious — Metrics Are Already Distorted

Not all automated traffic consists of "good bots."

By Cloudflare's classification: of all automated traffic, **37% are malicious "bad bots"**; legitimate crawlers account for only 14%.

This number has an underappreciated implication: **the "read counts" you see in your analytics may already be heavily contaminated by bots**. On platforms like Xiaohongshu, WeChat public accounts, and independent blogs, crawler behavior is increasingly present — they trigger page loads, but no human is actually reading.

"Vanity metrics" are undergoing systemic distortion.

This means: treating traffic fluctuations as "market feedback on your content" is stepping into an expanding pit. Machine feedback is not market feedback. The reliability of traffic data as a decision signal has structurally declined in 2025–2026.

---

## 6. What This Means for Ordinary People

If you're not a content creator, you don't need to worry about pay-to-crawl or crawl-to-referral ratios. But this will affect every internet user in subtler ways.

**How you obtain information is changing**. When you ask a question in ChatGPT or Gemini, the answer you receive has traveled this chain: original content → AI crawler scrapes → LLM training or real-time retrieval → AI synthesizes answer → you receive it. You never directly encountered the original content; what you encountered was a machine's processed interpretation of it.

This is an efficiency gain, and also an added degree of separation.

**"Real human presence" is becoming a scarce signal**. When most web activity is machine behavior, confirming that "this interaction was initiated by a real person" becomes more valuable — and harder to achieve. Cloudflare is already selling this: Turnstile (human verification) and Bot Management products saw price increases in 2025 because demand is growing.

**The first reader of your content may be a machine**. This isn't pessimism — it's a new design constraint. If machines are the first filter for content — deciding what gets indexed, cited, and pushed to humans — then "allowing machines to accurately understand what you're saying" is just as important as "reading smoothly for humans." SEO is yielding to **AEO (Answer Engine Optimization)**, and this shift is already underway.

---

## 7. My Assessment

This transition has several layers worth distinguishing, because conflating them easily generates false panic or false optimism.

**First, this is structural, not cyclical**. Machine traffic will not decrease if AI hype subsides — AI Agent applications are expanding, automation tools are proliferating, and both are one-way processes. 57.5% will keep rising; it will not fall back below 50%.

**Second, "machine dominance" does not equal "content has no value"**. Humans still dominate in byte volume; experience, emotion, and creativity remain human territory. But "the first layer of content distribution" has already been handed over to algorithms and agents to adjudicate — you write for humans, but machines review it first. Both things are simultaneously true.

**Third, pay-to-crawl — if it materializes — is a double-edged sword for small creators**. Upside: content crawled should be compensated. Downside: if your site is too small and not indexed, you simply "disappear" from AI answers. Content backed by major platforms and content that can afford to participate will have advantages. The survival strategy for small and mid-sized creators is not to fight machines, but to make yourself "worth being read by machines — and worth paying for."

**Fourth, the recursive risk is long-term**. AI crawls content for training purposes; AI trained on that content generates new content; new content is crawled by more AI — this recursive loop means the proportion of AI-generated content in the web's content pool will keep growing. How this will affect the quality of future training data is a question nobody can accurately answer today, but the direction is clear.

---

**In a sentence**: the internet hasn't "died" — it has simply changed protagonists, from humans reading the web to machines reading the web. When 57.5% of requests come from machines, the rules of the game have already changed; most people just haven't noticed they're still playing by the old rules.

---

*Data sources: Matthew Prince (@eastdakota) Twitter/X 2026-06-03; Cloudflare Radar; Imperva Bad Bot Report 2024; Thales Bad Bot Report 2026; Xiaohongshu post "Cloudflare CEO Matthew Prince Reveals the Web Paradigm Shift" by Chen Kun, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
