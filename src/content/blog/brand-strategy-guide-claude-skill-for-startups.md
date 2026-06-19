---
title: "把 5 万元的品牌咨询装进 Claude：brand-strategy-guide 让小团队也能做品牌全案"
titleEn: "Putting a $50K Brand Consultancy Inside Claude: brand-strategy-guide for Small Teams"
description: "brand-strategy-guide 是一个开源的 Claude Code 技能，把专业品牌咨询方法论变成一套可对话的 AI 系统。早期创业者不用花 1.5 万到 5 万美元请咨询公司，靠 22 轮结构化对话或一份问卷，就能产出 40-100 页的品牌全案。本文讲清它是什么、谁能用、怎么上手。"
descriptionEn: "brand-strategy-guide is an open-source Claude Code skill that turns professional brand-consulting methodology into a conversational AI system. Early founders skip the $15-50K agency fee: a 22-round structured dialogue or a brief questionnaire yields a 40-100 page brand blueprint. Here's what it is, who it's for, and how to start."
pubDate: "2026-06-19"
updatedDate: "2026-06-19"
category: "Tech-News"
tags: ["品牌策略", "Claude Code", "AI Skill", "创业", "Brand Strategy", "开源工具", "小团队"]
heroImage: "../../assets/banner-startup-brand.jpg"
---

> **BLUF**：**brand-strategy-guide**（GitHub: DevinKuang/brand-strategy-guide，MIT 开源，34★）是一个把"品牌全案策略指南"方法论封装进 **Claude Code 技能**的工具。它的价值很直接：早期创业者做一套系统的品牌策略，传统上要花 **1.5 万到 5 万美元**请咨询公司；而用这个技能，你只需要回答一组结构化问题，AI 就能产出 **40-100 页**的品牌全案——从市场定位、竞争差异、品牌识别系统，到上市路线图、团队结构、预算分配。本文讲清它是什么、为谁而做、以及小团队怎么 5 分钟上手。

---

## 一、它解决的是一个真实的痛点

对一个刚起步的小团队来说,"做品牌"往往陷入两难:

- **请专业咨询**:一套完整的品牌全案 1.5 万–5 万美元起,早期团队根本掏不起;
- **自己拍脑袋**:在网上抄几个"使命愿景价值观"模板,填完发现既不指导产品、也不指导营销,纯粹是 PPT 摆设。

brand-strategy-guide 想填的就是中间那块空白:**用专业咨询的方法论框架,加上 AI 的对话能力,让没有品牌背景的创始人也能走完一遍严谨的品牌策略推演。**

它的核心理念有一句话点睛:品牌策略要回答的不是"我怎么卖更多",而是**"我在我的生态里占据什么位置?"**——也就是找到那个 **市场空白 ∩ 用户需求 ∩ 自身能力** 的生态位。

---

## 二、它到底是什么?(不是一篇 PDF,是一个会对话的顾问)

要说清楚:它**不是**一份静态文档,而是一个 **Claude Code 技能(Skill)**——本质是给 Claude 装上一套"品牌咨询顾问"的专业角色和工作流程。装好后,它以**三个并行的 Agent 角色**工作:市场研究、战略定位、执行规划。

它背后整合了 8 个成熟的商业框架,等于把一个咨询团队的知识库塞了进去:

- **黄金圈(Why-How-What)** —— 找到品牌的根本动机;
- **STP(细分-目标-定位)** —— 锁定目标市场;
- **品牌金字塔** —— 从功能利益到情感再到价值观;
- **波特五力 / PESTEL / SWOT** —— 竞争与宏观环境分析;
- **品牌原型** —— 给品牌一个人格;
- **4P/4C** —— 营销组合落地。

---

## 三、三种使用模式:按你的准备程度选

这是它对普通人最友好的设计——不强迫你一上来就想清楚所有事:

| 模式 | 怎么用 | 耗时 | 产出 |
|------|--------|------|------|
| **标准对话模式** | AI 像咨询顾问一样,跟你做 **22 轮**结构化问答 | 2-3 小时 | 40-60 页 |
| **简报文档模式** | 你先填一份结构化 Word 问卷,三个 Agent 并行生成 | 30-60 分钟 | 80+ 页 |
| **MD 输出模式** | 内容与排版分离,输出结构化 Markdown 简报 | —— | 80-100+ 页 |

最贴心的是它的 **"展开-确认"(Expand-Confirm)** 模式:你给一个粗糙的答案,AI 不会照单全收,而是**先复述它的理解 → 用行业背景帮你补充扩展 → 再请你确认是否准确**。这个循环能把创始人脑子里模糊的想法,逼成清晰、有行业语境支撑的洞察。换句话说,它不是替你写,而是**帮你想清楚**。

---

## 四、5 分钟上手(给完全的新手)

安装就是一行 git clone,把技能放进 Claude 的 skills 目录:

```bash
git clone https://github.com/DevinKuang/brand-strategy-guide.git \
  ~/.claude/skills/brand-strategy-guide
```

然后在 Claude Code 里直接说"帮我做品牌策略",它就会触发这个技能,问你要选哪种模式,接着开始结构化提问:你的行业、竞争对手、目标用户、产品能力、团队情况……你只管如实回答。

**可选增强**:如果你想要漂亮的 PPT 输出,可以再装 `guizang-ppt-skill`(HTML 网页式 PPT)或 `ppt-master`(生成 PPTX)。不装的话,默认输出 Markdown 简报,照样完整。

最终你会拿到:

- 一份 **40-100+ 页的品牌战略简报**(市场定位、竞争差异、品牌识别系统、上市路线图);
- 可选的 **HTML 互动演示 / PPTX**,直接能拿去见投资人;
- **可执行的计划**:团队结构建议、预算分配框架、风险地图、上线节奏。

而且它有**八项强制质量标准**(准确性、洞察深度、战略严谨、可执行性、可视化质量等)和**六个必备要素**(案例佐证、数据来源标注、方法论透明、可视化交付、可执行路线、假设与风险记录)——这意味着它不会只给你正确的废话,而是逼自己拿出有依据、能落地的东西。

---

## 五、对初创小组织,它的真正意义

放到 Mycelium 生态一直关心的命题——**让普通人和小社区掌握本该属于他们的能力**——来看,这个工具有三层价值:

1. **抹平信息差**:品牌咨询长期是大公司和高净值客户的专属服务,这个技能把同一套方法论开源成 MIT 协议,任何人都能用;
2. **降到能负担的门槛**:从 1.5 万美元降到"装个技能 + 几小时对话",这对预算紧张的早期团队是质的差别;
3. **从"填模板"到"想清楚"**:它的展开-确认循环,本质是在训练创始人的战略思维,而不是给一份用完即弃的文档。

当然要客观:它产出的是**策略草案和思考框架**,不能替代真实的市场验证和长期执行。AI 帮你把推演做扎实,但要不要进这个生态位、用户买不买账,最终还得靠你自己下场去试。把它当成一个**廉价、随叫随到、方法论严谨的品牌策略陪练**,定位就对了。

---

## FAQ

**Q:不会写代码 / 不懂 Claude Code 能用吗?**
A:基本只要会一行 `git clone` 和在 Claude 里打字对话即可。它设计的就是给非技术的创始人用,核心交互是自然语言问答。

**Q:它和直接问 ChatGPT"帮我做品牌策略"有什么区别?**
A:区别在于**结构化方法论 + 强制质量标准 + 多 Agent 协作**。直接问通用模型,容易得到泛泛而谈;这个技能用 22 轮诊断式提问和 8 大框架,把过程做成了可复现的咨询流程。

**Q:输出能直接拿去见投资人吗?**
A:可以生成 HTML/PPTX 演示稿,适合作为初稿。但建议你结合真实数据再打磨一轮——AI 给的是框架和推演,数据真实性要你自己把关。

---

> 📌 项目地址(请直接复制访问):
> GitHub —— https://github.com/DevinKuang/brand-strategy-guide
> 许可证:MIT(底层方法论《品牌全案策略指南 2.0》为作者原创)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用,须注明作者姓名及原文链接,不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: **brand-strategy-guide** (GitHub: DevinKuang/brand-strategy-guide, MIT, 34★) is a **Claude Code skill** that packages a professional brand-consulting methodology into a conversational AI system. The value is concrete: a systematic brand strategy traditionally costs **$15-50K** from an agency; with this skill you just answer a set of structured questions and the AI produces a **40-100 page** brand blueprint — from market positioning and competitive differentiation to brand identity system, go-to-market roadmap, team structure, and budget allocation. Here's what it is, who it's for, and how a small team gets started in five minutes.

---

## 1. It Solves a Real Pain

For an early-stage team, "doing branding" usually splits into two bad options: pay $15-50K for a consultancy you can't afford, or copy a "mission/vision/values" template that guides neither product nor marketing. brand-strategy-guide fills the gap: **professional consulting frameworks + AI dialogue, so a founder with no branding background can still walk through a rigorous strategy process.**

Its core idea: brand strategy answers not "how do I sell more" but **"what position do I occupy in my ecosystem?"** — finding the niche where *market gap ∩ user need ∩ your capability* meet.

## 2. What It Actually Is (a Conversational Consultant, Not a PDF)

It is **not** a static document — it's a **Claude Code Skill** that gives Claude a professional brand-consultant persona and workflow. Once installed, it works as **three parallel Agent roles**: market research, positioning, and execution planning. Under the hood it integrates eight established frameworks — Golden Circle, STP, Brand Pyramid, Porter's Five Forces, PESTEL, SWOT, Brand Archetypes, and 4P/4C — effectively loading a consulting team's knowledge base.

## 3. Three Modes — Pick by How Prepared You Are

| Mode | How | Time | Output |
|------|-----|------|--------|
| **Standard dialogue** | AI runs a **22-round** consultant-style Q&A | 2-3 hrs | 40-60 pages |
| **Brief document** | Fill a structured Word questionnaire; three Agents generate in parallel | 30-60 min | 80+ pages |
| **MD output** | Content separated from formatting; structured Markdown brief | — | 80-100+ pages |

The friendliest touch is the **Expand-Confirm** pattern: you give a rough answer, and the AI doesn't just accept it — it restates its understanding → expands with industry context → asks you to confirm. That loop turns a founder's fuzzy ideas into clear, context-grounded insight. It doesn't write *for* you; it helps you *think clearly*.

## 4. Five-Minute Start (for Total Beginners)

Install is one `git clone` into Claude's skills directory:

```bash
git clone https://github.com/DevinKuang/brand-strategy-guide.git \
  ~/.claude/skills/brand-strategy-guide
```

Then in Claude Code just say "help me build a brand strategy" — it triggers the skill, asks which mode, and starts structured questions about your industry, competitors, target users, product, and team. Just answer honestly. **Optional**: install `guizang-ppt-skill` (HTML PPT) or `ppt-master` (PPTX) for polished decks; without them, output defaults to a complete Markdown brief.

You end up with a 40-100+ page strategic brief, an optional HTML/PPTX presentation ready for investor meetings, and executable plans (team structure, budget framework, risk map, launch sequencing). It enforces **eight quality benchmarks** and **six required components** (case evidence, sourced data, methodology transparency, visual deliverables, executable roadmaps, documented assumptions/risks) — so it won't hand you correct-sounding fluff.

## 5. Why It Matters for Small Orgs

Through the lens Mycelium cares about — **putting capability back in the hands of ordinary people and small communities** — this tool offers three things: it **closes the information gap** (consulting methodology, long reserved for big clients, open-sourced under MIT); it **lowers cost to the affordable** (from $15K to "install a skill + a few hours"); and it **shifts from filling templates to thinking clearly** (the Expand-Confirm loop trains strategic thinking).

To be fair: it produces a **strategy draft and thinking framework**, not a substitute for real market validation and execution. The AI makes your reasoning rigorous, but whether to enter that niche and whether users bite is still on you. Treat it as a **cheap, on-demand, methodologically rigorous brand-strategy sparring partner** and you've got it right.

## FAQ

**Q: Can I use it without coding skills?**
A: Essentially you just need one `git clone` and the ability to chat in Claude. It's designed for non-technical founders; the core interaction is natural-language Q&A.

**Q: How is it different from just asking ChatGPT "build me a brand strategy"?**
A: Structured methodology + enforced quality standards + multi-agent collaboration. A generic prompt yields generalities; this skill turns it into a reproducible consulting process via 22-round diagnostic questioning and eight frameworks.

**Q: Can the output go straight to investors?**
A: It can generate HTML/PPTX decks suitable as a first draft. Refine with real data — the AI gives framework and reasoning; you own data accuracy.

---

> 📌 Project (copy to visit):
> GitHub — https://github.com/DevinKuang/brand-strategy-guide
> License: MIT (the underlying methodology, *Brand Comprehensive Strategy Guide 2.0*, is the author's original work)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
