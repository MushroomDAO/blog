---
title: "拆 google/skills：137 个 Agent Skill 里，86% 是 Google Cloud，67% 写了「别用我」"
titleEn: "Inside google/skills: 86% Is Google Cloud, and 67% Tell the Agent When Not to Use Them"
description: "Google 官方 Agent Skills 仓库 19583 星，实测统计：137 个 SKILL.md 里 cloud 占 118 个，index.json 收录 132 个，其中 88 个（67%）在 description 里显式写了「Don't use for X，改用 Y」的负向路由，平均 description 长达 437 字符。这个数字本身就是一条工程结论——当 skill 数量过百，路由歧义才是主要失败模式，Anthropic 建议的简短 description 在这个规模下会失效。"
descriptionEn: "Google's official Agent Skills repo has 19,583 stars. Measured: 137 SKILL.md files, 118 of them under cloud; index.json lists 132, of which 88 (67%) carry explicit negative routing — 'Don't use for X, use Y instead' — with descriptions averaging 437 characters. That number is itself an engineering finding: past a hundred skills, routing ambiguity becomes the dominant failure mode, and the short descriptions Anthropic recommends stop working at that scale."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-News"
tags: ["开源", "Agent Skills", "Claude Code", "Google Cloud", "AI Agent", "工程实践", "Skill", "MCP"]
heroImage: "../../assets/images/google-skills-137-agent-skills-negative-routing-vs-anthropic-banner.jpg"
author: "Mycelium Protocol"
---

「Google 也出 Agent Skills 仓库了」这条新闻本身没有信息量。有信息量的是：**打开它，数一遍，看大厂在 137 个 skill 的规模下被迫做了哪些和小仓库不一样的事。**

我数完了，最反直觉的一条是：**132 个 skill 里有 88 个（67%）在 description 里明确写了「别用我，这种情况该用另一个」。**

> 📌 仓库地址：https://github.com/google/skills
> 19583 星 ｜ Apache-2.0 ｜ Python ｜ 今天仍在推送
> 安装：`npx skills add google/skills`

本文接着本站三天前那篇《awesome-agent-skills：跨厂商路径、质量标准与反 slop》往下写——那篇讲的是标准该长什么样，这篇是一个大厂真实仓库的实测数据。

---

## 先看数字

我用 GitHub API 把整棵树拉下来数的，不是看 README 抄的：

| 指标 | 实测值 |
|---|---|
| 仓库里的 `SKILL.md` 文件数 | **137** |
| `index.json` 收录数 | **132** |
| 其中 `cloud` 分类 | **118**（86%）|
| `ads` | 14 |
| `analytics` / `developers` | 各 2 |
| `identity` | 1 |
| description 含负向路由（"Don't use"） | **88 个，占 67%** |
| description 平均长度 | **437 字符** |

第一个结论就摆在这里：**这不是一个通用 skill 集合，这是 Google Cloud 的产品文档被打包成了 agent skill。** 118/137 是 GKE、BigQuery、AlloyDB、Agent Platform、Application Design Center 这些东西。剩下的 ads 14 个是 Google Ads。

对个人开发者来说，这意味着：**除非你在用 GCP，这个仓库对你的直接价值接近于零。** 19583 星里有多少是品牌红利、多少是真在用，从星数上分不出来。

但它的**工程做法**是有价值的，而且和 skill 数量少的时候完全不一样。

---

## 为什么 67% 的 skill 要写「别用我」？

先看一个真实的 SKILL.md 头部（`skills/cloud/gke-basics/SKILL.md`）：

```yaml
---
name: gke-basics
metadata:
  category: Containers
description: >-
  Manages core GKE cluster provisioning, credentials, Autopilot vs Standard selection,
  and workload deployment. Use when creating GKE clusters, fetching kubectl credentials,
  configuring Workload Identity, or deciding between Autopilot and Standard modes.
  Don't use for specialized GKE networking (use gke-networking), advanced security hardening
  (use gke-platform-security or gke-workload-security), or cluster upgrades (use gke-upgrades).
---
```

注意最后三行。它不只说自己管什么，还点名说了三个兄弟 skill 的名字，把边界划死。

**这是被规模逼出来的。** 当仓库里有 40 多个 GKE 相关 skill——gke-basics、gke-networking、gke-inference、gke-backup-dr、gke-batch-hpc、gke-alert-configuration、gke-app-onboarding、gke-upgrades……——模型面对「帮我配一下 GKE 集群的网络」时，光靠正向描述根本分不清该调哪个。多个 skill 的正向描述会互相重叠，而重叠区就是路由失败区。

负向路由是在**显式切割重叠区**。

这也解释了 437 字符的平均 description 长度。Anthropic 的 skill 约定倾向简短 description，那是在**十几个 skill**的假设下成立的——彼此差异明显，短描述足够区分。到了一百多个同域 skill 的规模，短描述必然产生歧义，唯一的解法是把「不是什么」也写进去。

**可迁移的结论**：判断你的 skill 该写多长的 description，不看 Anthropic 的示例，看**你的 skill 之间有多容易混淆**。差异大就短，同域密集就必须写负向路由。

---

## 分发这一层：它没自建市场，走了三条现成的路

这是第二个值得看的点。`google/skills` 同时挂了三套分发机制：

**其一，`index.json`。** 机器可读的索引，132 条，每条是 `{name, description, entrypoint}`。entrypoint 是一个 raw.githubusercontent.com 的 URL：

```
https://raw.githubusercontent.com/google/skills/main/skills/cloud/agent-platform-alert-configuration/SKILL.md
```

也就是说，skill 内容是**远程按需拉取**的，不是必须先克隆整个仓库。文件头写着 `"generator":"This file is generated. Do not edit it by hand."`——索引是构建产物。

**其二，`skills.sh` / `agentskills.io`。** 安装命令是 `npx skills add google/skills`，走的是第三方的跨厂商分发渠道，不是 Google 自己的市场。

**其三，`.claude-plugin/marketplace.json`。** 它同时是一个 Claude Code 插件市场。有意思的是里面的插件并不指向本仓库，而是指向 `gemini-cli-extensions/*` 下的一堆独立仓库（alloydb、alloydb-omni、bigtable……），每个都 pin 了版本号：

```json
{
  "name": "alloydb",
  "source": { "source": "github", "repo": "gemini-cli-extensions/alloydb", "ref": "0.2.0" },
  "description": "Create, connect, and interact with an AlloyDB for PostgreSQL database and data."
}
```

**Google 没有建自己的 skill 商店。** 一个有能力建市场的公司选择接入别人的渠道，这条信号比 137 个 skill 本身更值得注意——说明当下 skill 生态的竞争点不在分发，在内容。

---

## 那供应链风险呢？

`npx skills add google/skills` 这条命令做的事是：从第三方 registry 解析、从 GitHub 拉取 Markdown、写进你的 agent 目录。然后你的 agent 会读并执行这些 Markdown 里的指令。

**这是一条完整的代码执行路径，只是内容不叫「代码」而叫「skill」。**

几个还没有好答案的问题：

- `skills.sh` / `agentskills.io` 由谁维护、审核标准是什么？README 里没写。
- entrypoint 指向 `main` 分支而不是某个 tag —— 内容会随上游变化，你装的和明天装的可能不是同一份。相比之下 marketplace.json 里的插件都 pin 了版本号，两套机制的严谨度不一致。
- skill 的 Markdown 里可以写任意指令。一个被入侵的仓库，或一个善意但写错的 skill，后果是 agent 照做。

这个风险不是 Google 独有的，是整个 skill 生态共有的。但 Google 下场把量做到 137 个，等于把这个问题的规模放大了。

---

## 那么，这个仓库对不用 GCP 的人还有什么用？

三条，都不是「装来用」：

1. **它是负向路由的最佳范本。** 88 个真实样本，看别人怎么划 skill 边界，比看规范文档有用。写自己的 skill 集合时可以直接抄这个句式。
2. **它是「skill 数量到了会发生什么」的实证。** 你的 skill 从 10 个长到 50 个时会遇到的路由问题，它已经遇到过并给了解法。
3. **它示范了 index.json 这种构建产物式的索引。** 如果你要做自己的 skill 分发，这套 `{name, description, entrypoint}` + 远程拉取的结构可以直接借鉴。

---

## 缺口：我没验证的部分

- **没实际装几个 Google skill 跑过。** 内容质量如何、是不是把文档换行塞进 Markdown 就算 skill，我只读了结构没跑过实例。
- **skills.sh 的审核机制没查。** 上面提的供应链问题是基于分发路径推的，不是看了它的审核流程得出的。
- **137 vs 132 的差额没查清。** 仓库里 137 个 SKILL.md，索引只收 132 个，差 5 个。可能是草稿、可能是子目录里的引用文件，没深究。

---

## 一句话总结

`google/skills` 作为工具集，对不用 GCP 的人价值有限；作为**规模化 skill 工程的样本**，它给了一条能直接用的结论：**skill 数量过百时，description 的主要职责从「说明我能做什么」变成「切割我和邻居的边界」，67% 的负向路由率就是这个转变的量化证据。**

> 📌 仓库：https://github.com/google/skills
> 机器可读索引：https://raw.githubusercontent.com/google/skills/main/index.json
> 本站相关：《awesome-agent-skills：跨厂商路径、质量标准与反 slop》

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

"Google shipped an Agent Skills repo" carries no information by itself. What carries information is opening it, counting, and seeing what a large vendor is **forced** to do differently at 137 skills that a small repo never faces.

I counted. The most counterintuitive finding: **88 of 132 skills (67%) explicitly state in their description when *not* to use them and which sibling skill to use instead.**

> 📌 Repository: https://github.com/google/skills
> 19,583 stars ｜ Apache-2.0 ｜ Python ｜ still being pushed today
> Install: `npx skills add google/skills`

This continues from this site's post three days ago on cross-vendor skill paths and quality criteria — that one covered what a standard should look like; this one is measured data from a real vendor repo.

---

## The numbers first

Pulled via the GitHub API over the full tree, not copied from the README:

| Metric | Measured |
|---|---|
| `SKILL.md` files in the repo | **137** |
| Entries in `index.json` | **132** |
| Under `cloud` | **118** (86%) |
| `ads` | 14 |
| `analytics` / `developers` | 2 each |
| `identity` | 1 |
| Descriptions with negative routing ("Don't use") | **88 — 67%** |
| Average description length | **437 characters** |

The first conclusion is right there: **this is not a general-purpose skill collection; it is Google Cloud's product documentation packaged as agent skills.** 118 of 137 are GKE, BigQuery, AlloyDB, Agent Platform, Application Design Center. The 14 under `ads` are Google Ads.

For an individual developer that means: **unless you are on GCP, the direct value of this repo is close to zero.** How much of the 19,583 stars is brand gravity versus actual use cannot be separated from the star count.

Its **engineering choices**, however, are worth studying — and they look nothing like what a small skill set does.

---

## Why do 67% of the skills say "don't use me"?

Here is a real SKILL.md header (`skills/cloud/gke-basics/SKILL.md`):

```yaml
---
name: gke-basics
metadata:
  category: Containers
description: >-
  Manages core GKE cluster provisioning, credentials, Autopilot vs Standard selection,
  and workload deployment. Use when creating GKE clusters, fetching kubectl credentials,
  configuring Workload Identity, or deciding between Autopilot and Standard modes.
  Don't use for specialized GKE networking (use gke-networking), advanced security hardening
  (use gke-platform-security or gke-workload-security), or cluster upgrades (use gke-upgrades).
---
```

Note the last three lines. It does not only state what it covers; it names three sibling skills and hard-codes the boundary.

**Scale forced this.** With 40-odd GKE skills in one repo — gke-basics, gke-networking, gke-inference, gke-backup-dr, gke-batch-hpc, gke-alert-configuration, gke-app-onboarding, gke-upgrades — a model facing "help me set up networking on my GKE cluster" cannot pick correctly from positive descriptions alone. Positive descriptions overlap, and the overlap region is exactly where routing fails.

Negative routing **explicitly carves out the overlap**.

It also explains the 437-character average. Anthropic's skill convention favors short descriptions — which holds under the assumption of **a dozen or so skills**, distinct enough that brevity suffices. At a hundred-plus same-domain skills, short descriptions are guaranteed to be ambiguous, and the only fix is to write down what a skill is *not*.

**The transferable rule**: to decide how long your skill descriptions should be, do not look at Anthropic's examples — look at **how easily your skills can be confused with each other**. Distinct means short; dense and same-domain means you must write negative routing.

---

## Distribution: no in-house marketplace, three existing channels instead

The second thing worth studying. `google/skills` ships three distribution mechanisms at once.

**One, `index.json`.** A machine-readable index of 132 entries, each `{name, description, entrypoint}`. The entrypoint is a raw.githubusercontent.com URL:

```
https://raw.githubusercontent.com/google/skills/main/skills/cloud/agent-platform-alert-configuration/SKILL.md
```

Skill content is **fetched remotely on demand**; cloning the whole repo is not required. The file header reads `"generator":"This file is generated. Do not edit it by hand."` — the index is a build artifact.

**Two, `skills.sh` / `agentskills.io`.** The install command is `npx skills add google/skills`, which goes through a third-party cross-vendor channel, not a Google-owned marketplace.

**Three, `.claude-plugin/marketplace.json`.** The repo doubles as a Claude Code plugin marketplace. Notably, the plugins listed do not point back at this repo but at separate `gemini-cli-extensions/*` repos (alloydb, alloydb-omni, bigtable...), each pinned to a version:

```json
{
  "name": "alloydb",
  "source": { "source": "github", "repo": "gemini-cli-extensions/alloydb", "ref": "0.2.0" },
  "description": "Create, connect, and interact with an AlloyDB for PostgreSQL database and data."
}
```

**Google did not build its own skill store.** A company perfectly capable of building a marketplace chose to plug into someone else's — a stronger signal than the 137 skills themselves, suggesting the current competitive front in the skill ecosystem is content, not distribution.

---

## What about supply chain risk?

What `npx skills add google/skills` does: resolve through a third-party registry, fetch Markdown from GitHub, write it into your agent's directory. Your agent then reads and executes the instructions in that Markdown.

**That is a complete code-execution path; the payload is simply called a "skill" instead of "code."**

Open questions with no good answer yet:

- Who maintains `skills.sh` / `agentskills.io`, and what is the review standard? The README does not say.
- Entrypoints point at `main`, not a tag — content drifts with upstream, so what you install today may differ from tomorrow. By contrast, every plugin in marketplace.json is version-pinned; the two mechanisms are not equally rigorous.
- A skill's Markdown can contain arbitrary instructions. A compromised repo — or a well-meaning but wrong skill — results in the agent doing as told.

This risk is not unique to Google; it belongs to the whole skill ecosystem. But shipping 137 of them scales the problem up.

---

## So what is it good for if you are not on GCP?

Three things, none of them "install and use":

1. **It is the best available corpus of negative routing.** 88 real samples of how to carve skill boundaries — more useful than reading a spec. The phrasing is directly copyable for your own skill set.
2. **It is evidence of what happens as skill count grows.** The routing problems you will hit going from 10 to 50 skills, it already hit, with a working answer.
3. **It demonstrates a build-artifact index.** If you are building your own skill distribution, the `{name, description, entrypoint}` plus remote-fetch structure is worth borrowing.

---

## Gaps: what I did not verify

- **I did not install and run any of the Google skills.** Content quality — whether these are real skills or documentation reflowed into Markdown — is unverified; I read structure, not instances.
- **I did not investigate skills.sh's review process.** The supply-chain points above are inferred from the distribution path, not from reading its review policy.
- **The 137 vs 132 gap is unexplained.** Five SKILL.md files on disk are absent from the index; could be drafts or reference files in subdirectories. Not chased down.

---

## In one line

As a toolset, `google/skills` offers little to anyone off GCP. As a **sample of skill engineering at scale**, it yields one directly usable conclusion: **past a hundred skills, a description's primary job shifts from "explain what I do" to "carve the boundary between me and my neighbors" — and a 67% negative-routing rate is the quantified evidence of that shift.**

> 📌 Repository: https://github.com/google/skills
> Machine-readable index: https://raw.githubusercontent.com/google/skills/main/index.json

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
