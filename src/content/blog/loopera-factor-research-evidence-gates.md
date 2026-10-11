---
title: "Loopera：让因子研究先过证据门，公开仓库尚无源码"
titleEn: "Loopera: Evidence Gates for AI Factor Research"
description: "Loopera 面向基本面量化团队，把经营现象、经济假设、候选因子、确定性验证与研究记忆连接起来。本文核对公开仓库与 BSL 1.1 许可，拆解官方 147 次尝试、5 个入库候选的证据边界，解释信息时点、会计口径、逻辑盲审和增量评估为何重要，以及团队应要求哪些可复核材料。没有可运行源码或公开 API。"
descriptionEn: "Loopera links financial hypotheses, factor candidates, evidence gates and research memory. We inspect its public documentation, licensing and validation limits."
wechatTitle: "Loopera：因子研究先过证据门"
wechatDigest: "拆解基本面因子研究Agent的证据门与失败记忆，公开仓库目前没有可运行源码。"
pubDate: "2026-10-11"
updatedDate: "2026-10-11"
category: "Tech-News"
tags: ["Loopera", "AI Agent", "基本面", "因子研究", "量化研究", "研究记忆"]
heroImage: "../../assets/images/loopera-factor-research-evidence-gates-banner.jpg"
---

Loopera 是帮助量化团队把财务研究想法转成候选因子、逐层验证并保存研究经验的 AI Agent。它的公开仓库目前只提供产品与技术资料，没有可运行源码；官方研究快照也不足以证明候选具有样本外盈利能力。

项目来自 Loopera-ai/loopera，README 标注 Public preview，LICENSE 为 BSL 1.1。Mycelium Protocol 于 2026 年 10 月 11 日核对了 README、许可文件与仓库文件清单；本文是公开资料分析，没有运行其内部系统或复现因子回测。

> 项目一手源：https://github.com/Loopera-ai/loopera

## Loopera 公开了什么，可以本地部署吗？

我们读取 GitHub 的递归文件树，看到中英文 README、许可与协作文档、架构图、技术 PDF、演示视频，以及三份财务报表 Parquet 文件。公开清单没有应用源码、安装入口或可执行研究引擎，这与 README 对仓库定位的说明一致。

所以，拿到 GitHub 链接不等于拿到能够自行部署的 Agent。当前可以研究它公开的设计、案例与聚合结果，无法仅凭该仓库独立跑通“输入观点—生成因子—验证信号”的完整链路。

LICENSE 写明 Additional Use Grant 为 None，Change Date 为 2030-09-09，Change License 为 Apache 2.0；具体版本还受许可中的时间条款约束。许可自身明确说 BSL 不是开源许可证。仓库出现数据文件，也不代表第三方数据自动获得转授权。

这一点会改变技术选型结论：如果团队需要今天就能接入自有数据库、审计源代码并运行实验的开源项目，Loopera 的当前公开交付还不能满足这个需求。

## 一个经营现象如何变成可检验因子？

Loopera 的输入分为 Topic、Prompt 和 PDF。三种形式分别对应研究方向、具体主张与已有报告，随后被整理成可以追踪来源的研究对象。报告中的明确公式可以优先验证，缺少关键定义的观点则继续作为假设背景。

它公开的研究路径可以理解为：先限定数据语境，再发现经营异常、比较竞争解释、形成候选，最后验证并保存结果。这里的关键中间产物是 Research Contract：把字段、经济含义、预期方向与失效条件一起固定下来。

例如，观察到薪酬负债异常，并不能立即得出企业现金紧张的结论。正常奖金计提、结算时点与业务扩张，都可能解释这一现象。官方案例进一步引入收入与销售现金流入的关系，以比较不同机制；精确公式、时间窗口和权重没有公开。

这种结构的工程价值，在于让程序检查“实现究竟测量了什么”。如果 Agent 声称研究现金回收压力，实际计算却只是在挑选小规模企业，得到一个好看的历史结果也不能补上解释与实现之间的缺口。

![小M把经营现象放进棱镜，分出竞争解释后选择可验证的假设](../../assets/images/loopera-factor-research-evidence-gates-fig-01.png)

## 证据门具体检查什么？

根据 README，AI Agent 提出和修订想法，确定性 Harness 负责计算与检查，研究员保留关键审阅和决策权。公开的六类证据门涵盖以下问题：

| 检查 | 研究员需要确认的问题 |
| --- | --- |
| 执行与覆盖 | 是否能稳定计算，数据是否足以比较公司？ |
| 信息时点 | 做出历史判断时，这条财务信息是否已经公开？ |
| 会计口径 | 存量、期间流量和累计流量是否被正确处理？ |
| 逻辑一致性 | 字段、实现、经济机制与预期方向是否吻合？ |
| 研究新颖性 | 是否只是已有因子的换名或轻微变体？ |
| 表现与增量 | 是否有历史支持，是否增加了已有因子之外的信息？ |

信息时点是尤其容易被低估的一关。财报所属季度与投资者实际看到报告的日期不同；后续更正也可能改变数据。本文的独立判断是，若交付只包含最终数值，没有公告日期、版本与可见性记录，就很难审核是否混入未来信息。

官方案例还描述了逻辑盲审：审查角色先看假设、字段和实现，不读取回测收益。这种安排有助于减少“因为成绩好，所以故事一定合理”的倒推，但它本身不能替代独立的样本外测试。

对于 PDF 输入，README 要求保留原始窗口、分母、范围等来源约束；关键数据缺失时记录原因。这个设计值得借鉴：一个系统若默默替换字段，原始报告与实际实验就可能已经变成两个问题。

![小M操作证据闸门，只让附有可核对证据的候选通过](../../assets/images/loopera-factor-research-evidence-gates-fig-02.png)

## 147 次尝试、5 个入库，能说明什么？

官方披露的内部运行快照包括 147 次候选尝试、66 项结构化假设与 37 个研究模式。147 次尝试中，130 个形成有效候选，125 个明确停止，5 个进入研究库；另有 17 次没有形成有效候选。

我们仅做公开数字的算术核对：130 = 125 + 5，147 = 130 + 17；5/147 约为 3.4%，5/130 约为 3.8%。前者是全部尝试的入库比例，后者是有效候选的入库比例，都不能解释为交易胜率或盈利概率。

值得继续追问的是，公开列出的六类停止位置合计为 127 次，而顶层漏斗列出 125 个有效候选停止。资料没有给出逐项映射，无法确认分类是否重叠、采用了不同口径或来自不同快照。因此不宜把分类表直接重建成互斥漏斗。

README 也承认，5 个入库候选集中在经营负债异常主线。这个集中度提示研究多样性仍有限，不能从“入库 5 个”推导出已经覆盖大量独立风险来源。

更关键的是，公开材料没有同时给出可复核的样本区间、股票池、调仓规则、交易成本与换手假设，也未公开生产公式。因此我们没有依据判断收益水平、容量或样本外稳定性。官方模拟评估关于发现能力与误发现过滤的描述，同样需要可运行实验才能独立检验。

## 为什么失败记忆比多生成公式更值得关注？

失败原因可以改变下一轮研究。如果一个候选失败于信息时点，下一轮应修正数据可见性；如果失败于缺少增量，下一轮应寻找新的经营机制。只留下“未通过”三个字，Agent 很容易换个名字再试同一件事。

Mycelium Protocol 的判断是，Loopera 最有启发的地方是把假设、证据、停止位置与研究谱系放在同一条记录中。这类记忆如果能够被查询并与新候选匹配，就有机会节省重复研究；公开文档尚不足以证明它实际节省了多少时间或模型成本。

![小M把失败候选的原因缝进记忆树，新假设从留下的线索继续生长](../../assets/images/loopera-factor-research-evidence-gates-fig-03.png)

评估此类产品时，可以先要求一条完整、可追踪的候选记录：输入材料及其版本、当时可见的财务截面、研究契约、实现版本、每关结果、历史研究匹配和最终停止原因。随后用预先冻结的样本外区间检验结果，而不只看精选案例。

与本站介绍的 FinceptTerminal 金融终端相比，Loopera 的公开设计更聚焦因子研究过程及证据治理。两者解决的工作不同，不能仅凭都有金融数据和 Agent 就视作同类替代品。

延伸阅读：https://blog.mushroom.cv/blog/finceptterminal--open-source-bloomberg-terminal-alternative/

## 常见问题

### Loopera 现在是可部署的开源 Agent 吗？

当前公开仓库不是源码发行包，没有可运行代码、安装包、CLI 或公开 API；BSL 1.1 也明确不属于开源许可证。具体产品访问和授权须查看官方提供的渠道。

### 入库候选可以直接用于交易吗？

不能根据现有公开证据得出这一结论。入库只说明候选通过官方该轮研究流程，仍需可复核的样本外测试、成本评估与独立审查。

### 小团队可以借鉴什么？

可以先把自然语言假设整理成研究契约，再分别保存数据时点、逻辑审查和失败原因。即便没有多 Agent 编排，结构化的研究记录也能让人工实验更容易复核。

## 一手资料与核对范围

核对日期：2026-10-11。本文读取公开文件与 GitHub 文件树，算术复核聚合数字；没有执行内部 Agent、下载财务数据做回测或验证投资表现。来源快照和核对记录已本地保存。

产品、案例与运行快照：https://github.com/Loopera-ai/loopera/blob/main/README.md

许可原文：https://github.com/Loopera-ai/loopera/blob/main/LICENSE

公开文件清单：https://github.com/Loopera-ai/loopera/tree/main

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Loopera is an AI agent designed to turn financial research ideas into candidate factors, evaluate them through evidence gates and retain research experience. Its public repository currently contains product and technical documentation rather than runnable source code. Its reported research snapshot does not establish out-of-sample profitability.

The project is published under Loopera-ai/loopera, with a Public preview badge and a BSL 1.1 license. Mycelium Protocol inspected the README, license and repository inventory on October 11, 2026. This is a review of public evidence: we did not run the internal system or reproduce its backtests.

> Primary source: https://github.com/Loopera-ai/loopera

## What is public, and can you deploy Loopera locally?

The recursive GitHub tree contains Chinese and English documentation, licensing and collaboration files, an architecture image, a technical PDF, a demo video and three financial-statement Parquet files. We found no application source, installation entry point or executable research engine. This matches the README's stated scope.

The current delivery lets readers examine the proposed workflow, examples and aggregate results. It does not let an independent team reproduce the complete idea-to-factor-to-validation pipeline from this repository alone.

The LICENSE specifies Additional Use Grant: None, a Change Date of September 9, 2030, and Apache 2.0 as the Change License. The timing clause also applies separately to versions. The license explicitly states that BSL is not an open-source license. Third-party data is not automatically relicensed by the repository's terms.

For a team that needs to connect its own database, inspect implementation code and run experiments today, the current public delivery is insufficient.

## How does a business observation become a testable factor?

The documented inputs are Topic, Prompt and PDF: a research direction, a specific thesis or an existing report. Explicit formulas can enter candidate validation, while incomplete claims remain hypothesis context with their source constraints preserved.

The proposed workflow starts with the available data context, identifies an operating anomaly, compares competing explanations, constructs a candidate and evaluates it before saving the outcome. Its Research Contract binds the fields, economic meaning, expected direction and failure conditions together.

In the official example, unusual payroll liabilities can reflect bonus accruals, settlement timing or expansion as well as cash pressure. The proposed investigation adds the relationship between revenue and cash received from sales to help distinguish mechanisms. Exact formulas, windows and weights are withheld.

The engineering benefit is that reviewers can ask whether implementation measures the stated mechanism. A candidate supposedly measuring collection pressure might instead be identifying company size; attractive historical performance would not resolve that mismatch.

![Xiao-M uses a prism to separate competing explanations before choosing a testable hypothesis](../../assets/images/loopera-factor-research-evidence-gates-fig-01.png)

## What do the evidence gates check?

The documented division of work assigns proposal and revision to the agent, calculation and checks to a deterministic harness, and key review decisions to human researchers.

| Gate | Question to establish |
| --- | --- |
| Execution and coverage | Can it compute reliably across enough companies? |
| Information timing | Was the information public at the historical decision time? |
| Accounting conventions | Are stocks, period flows and cumulative flows handled consistently? |
| Logical consistency | Do implementation, mechanism and expected direction agree? |
| Research novelty | Is it substantively different from previous candidates? |
| Performance and incrementality | Is there historical support and information beyond existing factors? |

Our assessment is that data visibility deserves particular attention. A reporting period is different from a publication date, and subsequent revisions can alter the values. Final tables without publication dates and version records provide an inadequate basis for auditing future-information leakage.

The example also describes reviewing economic logic without reading backtest returns. That separation can reduce results-driven storytelling, but it does not substitute for independent out-of-sample evaluation.

For PDF inputs, the documented policy preserves the original denominator, window and scope and records missing fields. Silent substitutions would otherwise make the implemented experiment diverge from the report being evaluated.

![Xiao-M operates an evidence gate that admits candidates only with inspectable support](../../assets/images/loopera-factor-research-evidence-gates-fig-02.png)

## What do 147 attempts and five accepted candidates establish?

The official internal snapshot reports 147 attempts, 66 structured hypotheses and 37 research patterns. Of the attempts, 130 became valid candidates, with 125 stopped and five admitted to the research library; 17 did not become valid candidates.

We checked only the arithmetic: 130 = 125 + 5 and 147 = 130 + 17. Admission rates are approximately 3.4% of all attempts or 3.8% of valid candidates. Neither is a trading win rate or probability of profit.

A separate public table of six stopping categories sums to 127, compared with 125 stopped valid candidates in the headline funnel. Without a record-level mapping, we cannot determine whether the categories overlap, use another denominator or reflect different snapshots. They should not be reconstructed as a mutually exclusive funnel.

All five admitted candidates reportedly cluster around operating-liability anomalies, indicating limited current diversity. The public material does not jointly disclose a reproducible sample period, universe, rebalancing rules, transaction costs and turnover assumptions, nor production formulas. It therefore cannot establish returns, capacity or out-of-sample stability.

Descriptions of synthetic evaluations are also author-reported. Independent verification would require executable experiments and their protocols.

## Why retain failed research?

Different failures should lead to different next experiments. A timing failure calls for fixing information availability; a lack of incremental value calls for exploring a different mechanism. A record that merely says “failed” leaves an agent free to repeat the same idea under a new name.

Mycelium Protocol finds the connection between hypotheses, evidence, stopping points and research lineage the most useful design lesson. Searchable records could reduce repeated work, although the public documentation does not establish actual time or model-cost savings.

![Xiao-M stitches failure reasons into a memory tree so new hypotheses can build on earlier evidence](../../assets/images/loopera-factor-research-evidence-gates-fig-03.png)

An evaluation can start by requesting a complete candidate trace: input and version, historically visible data, contract, implementation revision, gate decisions, similarity checks and stopping reason. Results should then be evaluated on a pre-frozen out-of-sample interval rather than selected examples alone.

Compared with the FinceptTerminal financial terminal previously covered on this blog, Loopera's documented design focuses on factor research and evidence governance. Their workflows differ despite both involving financial data and agents.

Related reading: https://blog.mushroom.cv/blog/finceptterminal--open-source-bloomberg-terminal-alternative/

## FAQ

### Is Loopera currently a deployable open-source agent?

No runnable source, installer, CLI or public API is provided in the current repository. BSL 1.1 explicitly is not an open-source license. Consult the official channels for product access and applicable terms.

### Can accepted candidates be traded directly?

The public evidence does not support that conclusion. Admission to an internal research library still requires independently reproducible out-of-sample testing and cost evaluation before any trading decision.

### What can a small team adopt?

Start with structured research contracts, historical data-visibility records, separate logic reviews and specific failure reasons. These can improve auditability even without multi-agent orchestration.

## Primary sources and verification scope

Checked on October 11, 2026. We inspected public files and the repository tree and checked aggregate arithmetic. We did not execute the internal agent, backtest the financial datasets or verify investment performance.

Product, case and snapshot: https://github.com/Loopera-ai/loopera/blob/main/README.md

License: https://github.com/Loopera-ai/loopera/blob/main/LICENSE

Public inventory: https://github.com/Loopera-ai/loopera/tree/main

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
