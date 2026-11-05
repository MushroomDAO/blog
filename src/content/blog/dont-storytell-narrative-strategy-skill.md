---
title: "Don’t Storytell调研：把商业材料变成一页可验证的叙事策略"
titleEn: "Don’t Storytell: An Evidence-Based Strategy Skill"
description: "Don’t Storytell是一份公开的叙事咨询Skill，帮助创始人、产品负责人和创作者从材料中识别事实、提出取舍，形成愿景、因果行动和首次履约计划。本文核对案例库规模、检索与HTML导出脚本，分析证据边界、用户场景、输入隐私和许可缺口，并用一个假设场景说明怎样把策略建议接回真实行动，而非把漂亮文案当成经营结果。"
descriptionEn: "Review Don’t Storytell: a narrative strategy skill with case retrieval and HTML export, evidence limits, licensing gaps and practical decision workflows."
wechatTitle: "Don’t Storytell：先做取舍再写叙事"
wechatDigest: "从公开案例与脚本验证出发，分析一页叙事策略如何连接事实、选择和行动。"
pubDate: "2026-11-05"
updatedDate: "2026-11-05"
category: "Research"
tags: ["Don’t Storytell", "叙事策略", "AI Skill", "创作者", "商业决策"]
heroImage: "../../assets/images/dont-storytell-narrative-strategy-skill-banner.jpg"
lastPublishedAt: "2026-11-05T01:29:47Z"
---

Don’t Storytell帮助创始人和创作者把零散商业材料整理成一页策略：判断眼下该选什么、下一步做什么，以及出现什么结果就改路。它的价值在于约束建议的依据和行动条件，而不是替经营结果作保证。

正确仓库：https://github.com/noi-liuchang/dont-storytell

原消息里的 `/dont -storytell` 是断开的地址；本文分析完整仓库，固定提交为 `d4840723dac3234e901aed94192b43f98b4c40eb`。当前Skill标注v1.2-beta.1，安装目录与调用名为 `noi-narrative-engineering`。

## 它是一份怎样的Skill？

这是面向咨询与策略整理的指令包，包含主流程、参考判断、公开案例卡、示范和两个Python辅助脚本。它没有自己的模型权重，也不是装好后自动跑业务的Agent服务。

仓库把叙事放在实际选择之后：商业要怎样持续，谁会因此得到更好的选择，创办者又有什么经历或长期坚持支撑这条路。这是一套作者提出的方法框架，不是已经验证的商业增长公式。

核心使用者包括要梳理公司方向的创始人、需要统一产品与合作方式的负责人，以及面对定位、付费和创作节奏取舍的个人或小团队。若只想修改一句广告语，完整流程未必必要。

## 从资料到一页纸，中间发生什么？

输入可以是BP、产品说明、访谈、销售记录、作品，也可以是一个尚未成熟的想法。Skill要求先判断材料能支持多深的结论：足够就成稿，证据不足则给有边界的候选建议。

| 环节 | 核心问题 | 应留下什么 |
|---|---|---|
| 整理事实 | 什么真的发生了，什么只是自述？ | 来源与真实处境 |
| 提出判断 | 哪个选择会改变后续？ | 建议、依据及暂不选的方向 |
| 明确未来 | 这条路为谁创造什么价值？ | 有条件的愿景 |
| 连接行动 | 前一步为什么能支持下一步？ | 参与者、投入条件与因果关系 |
| 首次履约 | 谁先行动，谁能见证？ | 兑现条件与改路信号 |

最有用的约束是把可核对事实、当事人原话、顾问推断和未来设想分开。缺少创始人经历，就不能补一段动人传记；顾问推荐一个方向，也不等于当事人已经认领这个身份。

![小J将事实、推断和未来设想分别整理，再形成建议](../../assets/images/dont-storytell-narrative-strategy-skill-fig-01.png)

## 案例库到底有多大，能证明什么？

本次直接读取 `references/casebook.json`，得到112张卡片、112个唯一ID、61个主体，其中正例70张、反例27张、混合15张。每张卡都有来源链接、定位提示和适用限制等字段。

仓库另称方法来自99位AI创始人、联合创始人及CXO的咨询，累计超过200小时，并整理出78项判断。这些是作者对经历和材料的说明，不是112个独立企业样本，也不是咨询成功率。

原始私人咨询材料并未公开。案例库包含同一主体的不同时期或不同决定，公开记录也更容易保留被广泛讨论的企业与英语材料。案例多，不会自动消除幸存者偏差和选择偏差。

它适合帮助提出更好的问题：哪项前提在当前团队并不存在？谁有权作出这个决定？如果换了融资能力、渠道或时代条件，这个动作是否还成立？关键历史细节要进入重大决策时，仍应打开原始来源核验。

## 两个脚本各自做了什么？

`find_cases.py`在本地JSON中检索，支持机制标签、正反类型、阶段、字面关键词与案例ID。多个标签使用AND条件，结果先跨主体分散展示；它不是向量检索，也不会自动浏览来源网页。

`render_strategy.py`把符合格式的JSON渲染成独立HTML，带打印样式，兼容几种输入schema。它负责排版、文本转义和链接检查，不负责生成商业判断；官方街区杂志示范明确标为虚构。

```bash
# 在已经获取并获准使用的仓库目录内运行
python3 scripts/find_cases.py --tag 治理 --sign 反例 --limit 3
python3 scripts/render_strategy.py examples/neighborhood-magazine.json strategy.html
```

这些脚本只使用Python标准库。案例检索与HTML导出可以离线完成，但在AI助手里调用完整咨询Skill仍取决于所用模型、网络和计费方式。静态导出离线，不等于整个咨询过程本地私有。

## 一个假设场景：怎样让建议接受现实检验？

假设一个小团队在做每周城市散步活动，团建客户愿意一次包场，个人用户却还没有稳定复购。以下是本文构造的场景，不是该Skill跑出的实测答案，也不对应真实客户。

策略不能只说“打造城市文化社群”。应先说清：当前优先验证个人用户的重复参与，还是围绕企业客户设计交付？两条都可能成立，但会改变活动时间、服务承诺和获客动作。

若建议先验证个人复购，就安排一次明确收费的活动，记录参与者是否愿意再次付费、带来什么新的参与者，以及收入能否覆盖当次成本。若只靠熟人支持，先缩小承诺，不能直接写成已经形成社群飞轮。

这个过程把愿景拆成可撤回的选择。衡量目标也不能只剩一个数字：复购值得观察，但参与者实际得到什么、主办方能否持续交付，同样需要证据。

![小J在两个经营方向间作出选择，并检查首次行动留下的证据](../../assets/images/dont-storytell-narrative-strategy-skill-fig-02.png)

## 本次验证了什么，又没有验证什么？

本次对固定提交做了9组离线检查，全部通过：案例数量与唯一ID检查；按标签筛选、按ID读取；无效数量和未知ID的预期报错；官方schema 3示例渲染；合成标题HTML转义；拒绝javascript来源链接；拒绝未知schema。

官方示例成功生成HTML，并保留虚构标记和打印CSS。这里验证的是脚本与数据行为，没有调用模型生成真实咨询建议，也没有测试浏览器交互、打印分页或商业转化。因此，不能将“9组检查通过”写成“策略质量已经验证”。

对实际使用者，更有意义的后续检查是：建议是否忠实于原资料，有没有把推断写成事实，是否说清承担者，出现反证后是否允许改路。让真实委托人审核，比只看输出文字是否顺滑更接近交付质量。

## 使用之前，还要确认哪些边界？

第一是隐私。销售数据、访谈和创始人经历可能包含客户或员工信息。脚本本身不发送网络请求，但完整Skill运行时，交给AI助手的材料是否出网，要看助手和模型配置；目录里有文件不等于文件只在本地处理。

第二是授权。当前提交未发现LICENSE文件，README也未标明MIT或Apache，GitHub API的license字段为null。这表示本文不能确认一份明确的开源许可，不应据“公开仓库”默认认定可任意商用改编和再分发。

GitHub关于仓库许可的说明：
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

第三是调用与安装的区别。仓库名是dont-storytell，Skill调用名是 `$noi-narrative-engineering`；官方README给出了ZIP与Git两条安装路径。本次只读取和验证，没有把第三方Skill安装进当前助手，也没有把它的角色指令作为文章写作规则。

![小J核对资料是否外发、授权是否明确，以及行动是否有证据](../../assets/images/dont-storytell-narrative-strategy-skill-fig-03.png)

## 常见问题

### 它能自动生成商业策略吗？

它指导所用AI助手根据材料形成建议；检索和渲染脚本不会独立生成策略，建议仍需要当事人确认。

### 112张案例能预测生意成功吗？

不能。它们是带来源和限制的参考材料，不是统计意义上的成功概率模型，也不是112次独立实验。

### 有公开仓库，就等于明确开源许可吗？

不能这样判断。当前提交未发现明确许可证；需要在计划使用方式下向作者确认授权，不能替作者指定许可证。

延伸阅读：写作Skill怎样防止改写时发生事实漂移？
https://blog.mushroom.cv/blog/humanizer-zh-chinese-writing-skill-fact-drift-test-labeling/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Don’t Storytell turns business materials into a concise strategy: what to choose, what to do next and which observations would justify changing direction. Its useful feature is the discipline connecting evidence to action, rather than a promise of business success.

Correct repository: https://github.com/noi-liuchang/dont-storytell

The supplied URL was split before “-storytell”. This review fixes commit `d4840723dac3234e901aed94192b43f98b4c40eb`. The skill identifies itself as v1.2-beta.1. Its invocation and installation directory name are `noi-narrative-engineering`, different from the repository name.

## What kind of package is it?

The repository contains consulting instructions, reference judgments, annotated case cards, an example and two Python helpers. It has no model weights or autonomous business execution service. The framework links a sustainable business, improved choices for affected people and the founder's experience or commitments. This is the author's method, not an experimentally established growth formula.

Likely users include founders choosing a direction, product leads aligning product and partnerships, and creators balancing positioning, revenue and delivery. A full strategy process is unnecessary when the request is merely to edit one sentence.

## How does the workflow connect facts to decisions?

Inputs can include a pitch deck, interviews, product documentation, sales records or an early idea. The skill asks whether the evidence supports a complete recommendation or only a provisional candidate.

| Stage | Question | Useful output |
|---|---|---|
| Facts | What actually happened? | Sources and present constraints |
| Judgment | Which choice changes what follows? | Recommendation, reasons and deferred direction |
| Vision | Whose situation improves? | A conditional future |
| Sequence | Why does one action enable another? | Participants and commitments |
| First delivery | Who acts and who witnesses it? | Acceptance and revision conditions |

It separates checkable facts, a participant's statements, consultant inference and future proposals. Missing biography should stay missing. Recommending an identity does not mean the founder has accepted it.

![Little J separates facts, inference and proposals before recommending action](../../assets/images/dont-storytell-narrative-strategy-skill-fig-01.png)

## What does the casebook establish?

Local inspection found 112 cards, 112 unique IDs and 61 subjects: 70 positive, 27 negative and 15 mixed cases. Cards include a source URL, a locator and limitations. This confirms the structure and count, not the correctness of every historical claim.

The author reports consulting with 99 AI founders, co-founders and executives for more than 200 hours, plus a collection of 78 judgments. Those are experience and corpus claims, not an effectiveness benchmark. Private raw consultation records are excluded. Repeated subjects and selection toward visible public histories prevent treating the cards as independent business experiments.

Cases can challenge a premise: does this team possess the same authority, distribution or resources? Would the decision survive different market conditions? Before a historical detail supports a consequential commitment, check the original source rather than relying on the card alone.

## What do the Python helpers do?

`find_cases.py` filters local JSON by mechanism tags, sign, stage, literal terms or ID. Repeated tags are ANDed; results prioritize different subjects before returning additional cases from one subject. It is neither semantic retrieval nor automatic source verification.

`render_strategy.py` converts structured JSON into standalone HTML with print CSS. It supports several schemas, escapes text and checks source-link schemes. It does not generate the strategic judgment. The supplied neighborhood-magazine example explicitly describes fictional inputs.

Both scripts use the standard library and work offline. Running the consulting skill inside an AI assistant is a separate process whose privacy, connectivity and cost depend on that assistant and its model.

## How could a team use the method responsibly?

Consider a hypothetical city-walk organizer deciding between corporate bookings and repeat individual customers. This scenario was constructed for this review; it is not an observed customer or a generated consulting result.

The first decision changes scheduling, service promises and acquisition. If the team chooses to investigate individual repeat participation, start with a clearly priced event and examine subsequent paid attendance, actual participant benefit and delivery cost. Support from friends should not be described as a proven community growth loop.

This makes the proposal reversible. A useful strategy identifies a decision, an owner and evidence that could defeat it, rather than providing a compelling story immune to contradictory facts.

![Little J chooses a direction and checks evidence from the first delivery](../../assets/images/dont-storytell-narrative-strategy-skill-fig-02.png)

## What was actually verified?

Nine offline check groups passed against the pinned source: case counts and unique IDs; tag filtering; ID retrieval; expected errors for a non-positive limit and an unknown ID; rendering the official schema-3 example; escaping a synthetic HTML title; rejecting a javascript source URL; and rejecting an unknown schema.

The generated page retained its fictional label and print CSS. No model consultation, browser interaction, printed pagination or business conversion was tested. These checks demonstrate helper behavior, not strategy quality. A real evaluation should inspect faithfulness to inputs, explicit assumptions, responsibility and willingness to revise a recommendation.

## What should be checked before adoption?

Business inputs can contain sensitive customer or employee information. The helpers contain no network-sending operation, but materials supplied to an AI assistant may go to a remote provider. An offline HTML output does not prove an entirely local consulting workflow.

No LICENSE file or explicit MIT/Apache grant was found at this revision, and GitHub's license field was null. Public visibility should not be presented as an unrestricted permission to modify and redistribute commercially. The repository is introduced here as a public skill package with unresolved licensing, rather than assigned a license it does not declare.

GitHub licensing guidance:
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

The README offers ZIP and Git installation routes and uses `$noi-narrative-engineering` as the invocation. This review did not install the third-party skill or adopt its role instructions.

![Little J checks data handling, declared permission and evidence](../../assets/images/dont-storytell-narrative-strategy-skill-fig-03.png)

## FAQ

### Does it independently generate a business strategy?

The instructions guide an AI assistant. The search and render helpers do not independently generate recommendations, and the decision owner must still assess them.

### Can 112 cards predict success?

No. They are reference materials with limitations, not a statistical success model or 112 independent experiments.

### Is a public repository necessarily openly licensed?

No. This revision lacks an identified license. Confirm the intended use with its author rather than assuming a grant.

Related reading on factual drift when using a writing skill:
https://blog.mushroom.cv/blog/humanizer-zh-chinese-writing-skill-fact-drift-test-labeling/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
