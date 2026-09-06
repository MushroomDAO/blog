---
title: "931 个资源分成四类：awesome-copilot 的分类学，和那个 308KB 给 agent 读的索引"
titleEn: "931 Resources in Four Categories: awesome-copilot's Taxonomy and Its 308KB Index Written for Agents"
description: "Agents 222 个、Instructions 193 个、Skills 416 个、Plugins 100 个——这套分类本身比清单更值得看：agent 是接 MCP 的专门角色，instruction 是按文件模式自动生效的编码规范，skill 是自包含带资源的文件夹，plugin 是打包好的组合。另一个值得抄的做法是 llms.txt：一份 941 行、308KB 的机器可读索引，专门给 AI agent 读，让它自己找该用哪个资源。需要澄清的是它虽在 github 组织下，但 README 写的是 community-created。"
descriptionEn: "222 agents, 193 instructions, 416 skills, 100 plugins — and the taxonomy matters more than the list: an agent is a specialized role wired to MCP servers, an instruction is a coding standard applied automatically by file pattern, a skill is a self-contained folder with bundled assets, a plugin is a curated bundle of the above. The other idea worth copying is llms.txt: a 941-line, 308KB machine-readable index written for AI agents to read so they can find the right resource themselves. Worth clarifying: it sits under the github org but the README calls it community-created."
pubDate: "2026-09-06"
updatedDate: "2026-09-06"
category: "Tech-News"
tags: ["GitHub Copilot", "Agent Skills", "插件市场", "llms.txt", "分类学", "开发者工具"]
heroImage: "../../assets/images/awesome-copilot-agents-instructions-skills-plugins-taxonomy-llms-txt-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

项目地址：https://github.com/github/awesome-copilot
网站（全文搜索）：https://awesome-copilot.github.com
机器可读索引：https://awesome-copilot.github.com/llms.txt
Learning Hub：https://awesome-copilot.github.com/learning-hub

---

## 一句话结论

**这个仓库里有 931 个资源，但真正值得看的不是数量，是它把这些东西分成了哪四类——以及它专门给 AI agent 准备了一份 308KB 的索引。**

先说清楚定位：它挂在 `github` 组织下，3.87 万 stars，但 README 自己写的是 **"A community-created collection"**（社区创建的合集），不是 GitHub 官方产品线的一部分。这一点和本站上一篇写的 `googleworkspace/cli` 情况类似——**组织名不等于官方背书**。

## 四类资源，各是什么

数一下当前规模：

| 类型 | 数量 | 是什么 |
|---|---:|---|
| 🎯 **Skills** | 416 | 自包含的文件夹，指令 + 打包好的配套资源 |
| 🤖 **Agents** | 222 | 专门化的 Copilot agent，**对接 MCP server** |
| 📋 **Instructions** | 193 | 编码规范，**按文件模式自动生效** |
| 🔌 **Plugins** | 100 | 把 agent 和 skill 按工作流**打包**成一组 |
| 🍳 **Cookbook** | — | 直接可抄的 Copilot API 使用配方 |

**这套分类比清单本身有价值**，因为它回答了一个很多人搞混的问题：什么时候该写 skill，什么时候该写 instruction。

拆开看四者的差别：

- **Instruction** 的关键词是**自动**和**文件模式**。你不用调用它——打开匹配的文件它就生效。适合"这个项目里所有 `.tsx` 文件都要遵守的约定"这类始终成立的规则。
- **Skill** 的关键词是**自包含**。一个文件夹，指令加上它需要的资源（模板、脚本、参考文档）都在里面。适合"做某件具体的事需要一套完整方法"。
- **Agent** 的关键词是**角色 + MCP**。它不只是提示词，还接着外部工具。适合"这件事需要调用外部系统"。
- **Plugin** 的关键词是**打包**。一个工作流可能同时需要两个 agent 加三个 skill，plugin 把它们捆成一个可安装单元。

本站前不久写 ELI5 时提过"skill 的长度取决于模型不知道什么"。这里补上另一半：**在写之前，先想清楚它是不是 skill。** 一条始终该遵守的规范写成 skill 是错配——它会等着被调用，而你要的是它一直生效；那应该是 instruction。

![手里拿着东西站在分格托盘前，先决定该放进哪一格：要不要被调用、要不要带配套资源、要不要接外部工具、要不要打包好几个——四个问题定分类](../../assets/images/awesome-copilot-agents-instructions-skills-plugins-taxonomy-llms-txt-fig-01.png)

安装方式（市场已经预注册在 Copilot CLI 和 VS Code 里）：

```bash
copilot plugin install <plugin-name>@awesome-copilot
```

老版本 CLI 或自定义配置报"市场未知"的话，先注册一次：

```bash
copilot plugin marketplace add github/awesome-copilot
copilot plugin install <plugin-name>@awesome-copilot
```

## 那个 308KB 的 llms.txt

这是本篇最值得抄的做法。

仓库在 `awesome-copilot.github.com/llms.txt` 提供了一份**机器可读的完整索引**：941 行、308KB，把所有 agent、instruction、skill 结构化列出来，README 里写明用途是"**Using this collection in an AI agent?**"。

也就是说：**这份清单的读者是 agent，不是人。**

为什么这件事重要？因为 931 个资源已经超过了任何人能记住的量，也超过了能塞进上下文窗口的量。传统解法是做个搜索框让人去搜；`llms.txt` 的解法是**让 agent 自己去读索引、自己决定该拉哪个资源**。

这跟本站关心的"渐进式披露"是同一个思路的延伸：不是把所有能力一次性塞给模型，而是给它一份目录，让它按需取。区别在于这里的目录是**跨仓库、面向分发**的。

顺带一提，`llms.txt` 是个正在形成的社区约定（类似 `robots.txt` 之于爬虫），任何有大量文档或资源的项目都可以照做。**如果你的项目希望 agent 能正确使用它，提供一份 `llms.txt` 比写更多 README 更直接。**

网站那边还有全文搜索、按类型筛选，以及一个 Learning Hub——从 agent / skill / instruction 这些核心概念，到 hooks、agentic workflow、MCP server、Copilot coding agent 的实操教程都有。

## 本站的立场

得说清楚：**Copilot 是闭源商业生态，这跟本站一贯的本地优先、去平台锁定是相反方向。** 这一点和上一篇写 `gws` 时的判断一样——工具本身做得好，但方向性要讲出来。

所以本站的建议是分开看：

- **如果你已经在用 Copilot**：这个合集是明显的效率提升，931 个资源里总有对得上的，装了就是。
- **如果你不用 Copilot**：仓库里的具体资源对你没用（它们绑定 Copilot 的机制），但**上面那两样东西可以直接搬走**——四类资源的分类学，和 llms.txt 的做法。这两样跟厂商无关。

## 一点判断

三条：

1. **分类学值得抄。** agent / instruction / skill / plugin 四分法解决了"我该写哪种"这个实际问题。关键判据是：**要不要被调用**（instruction 不用）、**要不要接外部工具**（agent 要）、**要不要带配套资源**（skill 要）、**要不要打包多个**（plugin 要）。
2. **llms.txt 值得抄。** 资源多到装不进上下文时，给 agent 一份索引让它自己找，比继续往 README 里堆更有效。
3. **注意它不是 GitHub 官方出品。** README 写的是 community-created；组织名容易造成误解，跟 `googleworkspace/cli` 是同一类情况。

最后一句实话：本站已经写过好几篇 skill 合集类的东西，坦白说这类清单的边际价值在快速递减——931 个资源里你真正会用的可能不超过五个。**真正稀缺的从来不是资源数量，是知道什么时候该用哪一类。** 这也是本篇把重心放在分类学而不是清单上的原因。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

*by Mycelium Protocol*

---

Repository: https://github.com/github/awesome-copilot
Website (full-text search): https://awesome-copilot.github.com
Machine-readable index: https://awesome-copilot.github.com/llms.txt
Learning Hub: https://awesome-copilot.github.com/learning-hub

---

## TL;DR

**This repository holds 931 resources, but the count isn't the interesting part — the four categories it sorts them into are, along with the 308KB index it prepared specifically for AI agents.**

Positioning first: it lives under the `github` org with 38.7k stars, but the README calls it **"A community-created collection"** — not part of GitHub's official product line. Same situation as `googleworkspace/cli` in our last post: **an org name is not an endorsement**.

## The four categories

Current scale:

| Type | Count | What it is |
|---|---:|---|
| 🎯 **Skills** | 416 | Self-contained folders: instructions plus bundled assets |
| 🤖 **Agents** | 222 | Specialized Copilot agents that **integrate with MCP servers** |
| 📋 **Instructions** | 193 | Coding standards **applied automatically by file pattern** |
| 🔌 **Plugins** | 100 | **Bundles** of agents and skills for a specific workflow |
| 🍳 **Cookbook** | — | Copy-paste recipes for working with Copilot APIs |

**The taxonomy is worth more than the list**, because it answers a question people routinely get wrong: when should this be a skill, and when should it be an instruction?

The distinctions:

- **Instruction** is defined by **automatic** and **file pattern**. You never invoke it — open a matching file and it applies. Right for "every `.tsx` file in this project follows these conventions," rules that hold unconditionally.
- **Skill** is defined by **self-contained**. One folder holding the instructions plus whatever they need (templates, scripts, reference docs). Right for "doing this specific thing requires a whole method."
- **Agent** is defined by **role + MCP**. More than a prompt — it's wired to external tools. Right for "this requires calling an outside system."
- **Plugin** is defined by **bundling**. A workflow might need two agents and three skills; a plugin ties them into one installable unit.

Our ELI5 post argued that a skill's length should track what the model doesn't know. Here's the other half: **before writing it, work out whether it's a skill at all.** A standard that should always hold is miscast as a skill — it will sit there waiting to be invoked when what you wanted was continuous effect. That's an instruction.

![Standing over a compartmented sorting tray, deciding which slot a thing belongs in: does it need invoking, does it carry bundled assets, does it call external tools, does it combine several — four questions settle the category](../../assets/images/awesome-copilot-agents-instructions-skills-plugins-taxonomy-llms-txt-fig-01.png)

Installing (the marketplace is pre-registered in the Copilot CLI and VS Code):

```bash
copilot plugin install <plugin-name>@awesome-copilot
```

On older CLI versions or custom setups that report an unknown marketplace, register it once:

```bash
copilot plugin marketplace add github/awesome-copilot
copilot plugin install <plugin-name>@awesome-copilot
```

## That 308KB llms.txt

This is the most copyable idea in the post.

The project publishes a **complete machine-readable index** at `awesome-copilot.github.com/llms.txt`: 941 lines, 308KB, structurally listing every agent, instruction, and skill. The README states its purpose directly — "**Using this collection in an AI agent?**"

In other words: **the intended reader of that file is an agent, not a person.**

Why that matters: 931 resources exceed what anyone can remember, and exceed what fits in a context window. The conventional answer is a search box for humans. The `llms.txt` answer is to **let the agent read the index itself and decide which resource to pull.**

It's the same instinct as progressive disclosure, which this blog has covered before — don't hand the model every capability at once, hand it a table of contents and let it fetch on demand. The difference is that this table of contents is **cross-repository and distribution-facing**.

Worth noting that `llms.txt` is an emerging community convention (roughly what `robots.txt` is for crawlers), and any project with substantial documentation or resources can adopt it. **If you want agents to use your project correctly, shipping an `llms.txt` is more direct than writing more README.**

The website adds full-text search, filtering by type, and a Learning Hub covering core concepts (agents, skills, instructions) through hands-on guides for hooks, agentic workflows, MCP servers, and the Copilot coding agent.

## Our position

To be clear: **Copilot is a closed commercial ecosystem, which runs opposite to the local-first, anti-lock-in direction this blog favors.** Same judgment as the `gws` post — the tool is well made, and the directionality deserves saying.

So take it in two parts:

- **If you already use Copilot**: this collection is an obvious efficiency win; among 931 resources some will fit, so install them.
- **If you don't use Copilot**: the resources themselves are useless to you (they're bound to Copilot's mechanisms), but **the two ideas above transfer directly** — the four-way taxonomy and the llms.txt practice. Neither is vendor-specific.

## A closing judgment

Three points:

1. **Copy the taxonomy.** The agent / instruction / skill / plugin split resolves the practical "which one should I write" question. The deciding tests: **does it need to be invoked** (instructions don't), **does it call external tools** (agents do), **does it carry bundled assets** (skills do), **does it combine several** (plugins do).
2. **Copy llms.txt.** Once resources outgrow the context window, giving agents an index to search beats piling more into the README.
3. **Note it isn't a GitHub product.** The README says community-created; the org name misleads, exactly as with `googleworkspace/cli`.

One honest closing note: this blog has now covered several skill-collection repositories, and the marginal value of that genre is dropping fast — of 931 resources you'll likely use fewer than five. **What's actually scarce was never the count of resources; it's knowing which category applies when.** Which is why this post put the taxonomy first and the list second.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
