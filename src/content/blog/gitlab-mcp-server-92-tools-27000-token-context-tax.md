---
title: "92 个 MCP 工具吃掉 27000 tokens：一个 0 star 项目量出了 MCP 的上下文税"
titleEn: "92 MCP Tools Cost 27,000 Tokens: A Zero-Star Project Measured MCP's Context Tax"
description: "penaivanalejandro/gitlab-mcp-server 是个 0 star 的本地 MCP，但它的 README 干了一件几乎没人做的事：把 92 个工具定义的上下文开销逐组量化——全开 27340 tokens，只开 issues 组 3884 tokens，省 86%。平均每个工具定义约 297 tokens，你还没打字就已经花掉了。附 GITLAB_TOOL_GROUPS 分组加载、GITLAB_READ_ONLY 只读模式、以及 read_api 最小 token 权限这三层收敛方案。"
descriptionEn: "penaivanalejandro/gitlab-mcp-server has zero stars, but its README does something almost nobody does: it quantifies the context cost of 92 tool definitions group by group — 27,340 tokens with everything on, 3,884 with only the issues group, an 86% saving. That averages ~297 tokens per tool definition, spent before you type a word. It ships three layers of mitigation: GITLAB_TOOL_GROUPS scoping, a GITLAB_READ_ONLY mode, and minimal read_api token scope."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-News"
tags: ["MCP", "开源", "Claude Code", "上下文工程", "本地优先", "AI Agent", "GitLab", "安全"]
heroImage: "../../assets/images/gitlab-mcp-server-92-tools-27000-token-context-tax-banner.jpg"
author: "Mycelium Protocol"
---

**你装的每一个 MCP server，都在你打字之前就先吃掉一块上下文。** 这件事所有人都知道，但几乎没人给出过具体数字。

一个 0 star、建库两天的小项目给了：**92 个工具定义 = 27,340 tokens**，而且逐组列了表。

> 📌 项目地址：https://github.com/penaivanalejandro/gitlab-mcp-server
> MIT ｜ TypeScript ｜ Node.js 20+ ｜ 支持 Claude Desktop 与 Claude Code，三平台

说明一下：这个项目**我最初判为「只存档，不值得写」**，理由是「标准的 API-to-MCP 包装，没有独特机制」。这个判断是错的——我停在了 README 的前 1/3，没读到下面这张表。机制不新颖不等于没有值得写的东西。

---

## 那张表

README 里原话是：

> 全部 92 个工具定义会在**每一条消息**上发给模型，这大约花掉你**27,000 tokens 的上下文窗口，而你还没开始打字**。

| 加载的组 | 工具数 | ~Tokens | 相比全开省下 |
|---|---:|---:|---:|
| *（默认全开）* | 92 | **27,340** | — |
| `merge_requests` | 22 | 6,902 | 75% |
| `repository` | 15 | 5,288 | 81% |
| `issues` | 11 | 3,884 | 86% |
| `ci_pipelines` | 12 | 3,129 | 89% |
| `milestones` | 8 | 1,975 | 93% |
| `members_users` | 6 | 1,514 | 94% |
| `releases` | 5 | 1,288 | 95% |
| `labels` | 5 | 1,252 | 95% |
| `wiki` | 5 | 1,127 | 96% |
| `activity` | 3 | 984 | 96% |

**算一下平均值：27,340 ÷ 92 ≈ 每个工具定义 297 tokens。**

这个数字值得记住，因为它可以直接迁移到你装的任何 MCP server 上：

- 装 5 个各 20 工具的 MCP server = 100 个工具 ≈ **30,000 tokens 常驻开销**
- 在 200k 上下文里，这是 15% 一开始就没了
- 而且是**每一条消息**都要重发，不是一次性的

**这就是 MCP 的上下文税。** 它不显示在任何地方，你只会隐约感觉到「最近上下文怎么不够用了」。

---

## 它给的收敛方案：三层，从粗到细

这才是这个项目真正的价值——它不只是量了，还给了解法。

### 第一层：只加载需要的工具组

```json
"env": {
  "GITLAB_TOKEN": "glpat-...",
  "GITLAB_TOOL_GROUPS": "issues,merge_requests"
}
```

组可以叠加。做代码评审加 CI 排查的话，`issues,merge_requests,ci_pipelines` 给你 45 个工具，省掉一半开销。

**这个设计值得所有 MCP 作者抄。** 大多数 MCP server 是「全有或全无」——要么装上把全部工具塞进上下文，要么不装。分组加载让用户能按实际用法裁剪。

### 第二层：只读模式

```json
"env": {
  "GITLAB_READ_ONLY": "true"
}
```

开启后 92 个工具收缩到 **47 个只读工具**。注意它的实现是双保险：

> 写工具会从列表里移除，**并且**按名字调用时会被拒绝。

也就是说不只是「不告诉模型有这些工具」，而是「就算模型硬猜出名字来调，也会被挡回去」。这个区别很重要——只从列表里删掉，等于只做了「隐藏」不做「禁止」。

### 第三层：token 权限本身就最小化

README 关于 GitLab token scope 那段写得非常克制，值得整段引用：

> **只勾一个框。** ……如果你选 `read_api`，同时在配置里设 `GITLAB_READ_ONLY=true`。这是最安全的试用方式：Claude 在物理上无法创建、编辑、删除或合并任何东西。
>
> **其他每个框都别勾。** 你不需要 `read_user`、`write_repository`、`read_registry`、`create_runner`、`k8s_proxy`、`ai_features` 或 `self_rotate`。……**每多一个 scope，都是万一 token 泄露时多出来的伤害。**

对应关系：

| 你想要 | GitLab token scope | 得到 |
|---|---|---|
| 读 + 写 | `api` | 全部 92 个工具 |
| 只读，什么都改不了 | `read_api` | 47 个只读工具 |

而且它明确建议**两层一起用**：`read_api` 的 token 配 `GITLAB_READ_ONLY=true`，这样限制由 GitLab 服务端和这个 server 双重强制，不是只靠 server 自觉。

**这就是「深度防御」在一个 0 star 小项目里的正确实现。** 很多商业产品都做不到这个程度。

---

## 为什么说「机制不新颖」不构成否决理由？

我最初的否决逻辑是：这是标准的 API-to-MCP 包装，没有独特机制。

**这个逻辑本身有毛病。** 本站的第一性原则是「我自己要不要用」，不是「机制新不新」。一个工具对个人用户的价值，恰恰常常来自它**平庸但够用、而且把细节做完了**。

看它做完的细节：

- **Claude Desktop 找不到 node 的坑**——README 专门解释了：Claude Desktop 用最小 PATH 启动 server，不是你 shell 的 PATH，所以 `"command": "node"` 会失败即使终端里 node 好好的。给了 `which node` 拿绝对路径的解法。
- **Windows 路径反斜杠**——提醒 JSON 里要双写 `\\`。
- **改了配置不生效**——提醒 Claude Desktop 要完全退出，关窗口不算（它还在托盘/菜单栏里）。
- **改了代码不生效**——提醒重跑 `npm run build`，Claude 跑的是 `dist/` 不是 `src/`。
- **日志在哪**——三平台路径全给了，配 `LOG_LEVEL=debug`。
- **401 / 403 分别怎么办**——401 是 token 错了或带了空格，403 是 scope 不够。

这些没有一条是「新机制」，但每一条都是真人踩过的坑。**这套东西合起来，就是 PGL 那份公约里说的「妈妈测试」**——一个人能不能靠 README 自己装起来。

---

## 它还顺手挡了一个容易被忽略的攻击面

自建 GitLab 那节：

> 私有地址和纯 `http://` 对内网自建实例是支持的。云元数据端点（`169.254.169.254`）和其他特殊用途网段**始终被阻断**。

`169.254.169.254` 是 AWS/GCP/Azure 的实例元数据服务。如果一个 MCP server 允许你把 base URL 指向任意地址，而它又跑在云主机上，那就是一个现成的 SSRF——让模型去读元数据端点，可能拿到实例的临时凭证。

它默认挡住了。**一个 0 star 项目想到了这个，值得说一句。**

---

## 那它到底适不适合你？

**适合**：
- 你用 GitLab（gitlab.com 或自建），且已经在用 Claude Code / Claude Desktop
- 你想要 PAT 不出本机——它全程本地运行，token 只在你机器上
- 你想找一个 MCP server 的写法参考，尤其是权限与上下文收敛这两块

**不适合**：
- 你只用 GitHub——那这个仓库对你的直接价值是零，但上面那张 token 成本表仍然适用
- 你需要生产级保障——0 star、建库两天、作者无其他作品，维护持续性是个真问题

---

## 缺口：我没装过

如实说明，本文基于源码与文档，**没有实际安装运行**：

1. **92 个工具的实际可用率没验证。** 声明了 92 个，有多少真能跑通、有多少在边缘情况下报错，不知道。
2. **27,340 这个数字是作者测的，我没复现。** 它取决于用哪个模型的 tokenizer，量级应该没错，具体数字可能有出入。
3. **只读模式的实际强度没测。** README 说写工具会被「按名字拒绝」，我没试过绕过。
4. **作者背景不明。** 单一仓库、建库两天，长期维护存疑。

---

## 一句话总结

这个项目本身是个称职的 GitLab MCP，但它最有价值的输出不是那 92 个工具，是**一张把 MCP 上下文税量化了的表**，以及配套的三层收敛方案。

**可以直接拿走的结论**：每个 MCP 工具定义约 297 tokens；装之前先问「我真的要它全部工具吗」；能分组就分组，能只读就只读，token scope 能小就小。

顺便记一条我自己的教训：**判断一个工具值不值得写，别停在 README 的前三分之一。**「机制不新颖」不是否决理由，把细节做完本身就是一种稀缺能力。

> 📌 项目地址：https://github.com/penaivanalejandro/gitlab-mcp-server
> MCP 协议：https://modelcontextprotocol.io

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**Every MCP server you install eats a slice of your context before you type a word.** Everyone knows this; almost nobody has published a number.

A zero-star project, two days old, did: **92 tool definitions = 27,340 tokens** — with a per-group breakdown.

> 📌 Repository: https://github.com/penaivanalejandro/gitlab-mcp-server
> MIT ｜ TypeScript ｜ Node.js 20+ ｜ Claude Desktop and Claude Code, three platforms

A disclosure: **I initially filed this as "archive only, not worth writing,"** on the grounds that it was a standard API-to-MCP wrapper with no novel mechanism. That judgment was wrong — I stopped a third of the way into the README and never reached the table below. An unremarkable mechanism does not mean there is nothing worth writing about.

---

## The table

The README's own words:

> All 92 tool definitions are sent to the model on **every** message, which costs about **27,000 tokens of your context window before you've typed anything**.

| Groups loaded | Tools | ~Tokens | Saved vs. all |
|---|---:|---:|---:|
| *(default — all)* | 92 | **27,340** | — |
| `merge_requests` | 22 | 6,902 | 75% |
| `repository` | 15 | 5,288 | 81% |
| `issues` | 11 | 3,884 | 86% |
| `ci_pipelines` | 12 | 3,129 | 89% |
| `milestones` | 8 | 1,975 | 93% |
| `members_users` | 6 | 1,514 | 94% |
| `releases` | 5 | 1,288 | 95% |
| `labels` | 5 | 1,252 | 95% |
| `wiki` | 5 | 1,127 | 96% |
| `activity` | 3 | 984 | 96% |

**Do the division: 27,340 ÷ 92 ≈ 297 tokens per tool definition.**

That number is worth memorizing, because it transfers to any MCP server you install:

- Five MCP servers with 20 tools each = 100 tools ≈ **30,000 tokens of standing overhead**
- In a 200k window, that is 15% gone before you begin
- And it is resent on **every message**, not paid once

**This is MCP's context tax.** It shows up nowhere in the UI; you only get a vague sense that context has been running short lately.

---

## Its mitigations: three layers, coarse to fine

This is the project's real contribution — it did not just measure the problem, it shipped answers.

### Layer one: load only the tool groups you need

```json
"env": {
  "GITLAB_TOKEN": "glpat-...",
  "GITLAB_TOOL_GROUPS": "issues,merge_requests"
}
```

Groups compose. For review-plus-CI work, `issues,merge_requests,ci_pipelines` gives 45 tools at roughly half the overhead.

**Every MCP author should copy this design.** Most MCP servers are all-or-nothing: install and inject every tool, or do not install. Group loading lets users trim to actual usage.

### Layer two: read-only mode

```json
"env": {
  "GITLAB_READ_ONLY": "true"
}
```

92 tools shrink to **47 read-only tools**. Note the implementation is belt-and-braces:

> Write tools are removed from the list **and** rejected if called by name.

So it is not merely "don't tell the model these exist" but "even if the model guesses the name, the call is refused." That distinction matters — removing from the list alone is hiding, not forbidding.

### Layer three: minimize the token scope itself

The README's section on GitLab token scopes is unusually disciplined and worth quoting:

> **Check exactly one box.** … If you pick `read_api`, also set `GITLAB_READ_ONLY=true`. That is the safest way to try this out: Claude physically cannot create, edit, delete or merge anything.
>
> **Leave every other box unchecked.** You do not need `read_user`, `write_repository`, `read_registry`, `create_runner`, `k8s_proxy`, `ai_features` or `self_rotate`. … **Every extra scope is additional damage if the token ever leaks.**

The mapping:

| You want | GitLab token scope | You get |
|---|---|---|
| Read and write | `api` | All 92 tools |
| Read only, nothing modifiable | `read_api` | 47 read-only tools |

And it explicitly recommends **both layers together**: a `read_api` token plus `GITLAB_READ_ONLY=true`, so the restriction is enforced by GitLab's server as well as by this one — not left to the server's good behavior.

**That is defense in depth, implemented correctly, in a zero-star project.** Plenty of commercial products do not go this far.

---

## Why "the mechanism isn't novel" is not a valid rejection

My original rejection reasoned: standard API-to-MCP wrapper, no novel mechanism.

**That reasoning is itself faulty.** This site's first principle is "would I use it," not "is the mechanism new." A tool's value to an individual very often comes from being **unremarkable but sufficient — with the details actually finished**.

Look at the details it finished:

- **Claude Desktop cannot find `node`** — the README explains that Claude Desktop launches servers with a minimal PATH, not your shell's, so `"command": "node"` fails even when node works fine in a terminal. It gives the `which node` absolute-path fix.
- **Windows backslashes** — a reminder to double `\\` in JSON.
- **Config changes not taking effect** — a reminder that Claude Desktop must fully quit; closing the window leaves it in the tray.
- **Code changes not taking effect** — a reminder to re-run `npm run build`, since Claude runs `dist/`, not `src/`.
- **Where the logs are** — all three platform paths, with `LOG_LEVEL=debug`.
- **401 versus 403** — 401 means a wrong or whitespace-padded token; 403 means the scope is insufficient.

Not one of these is a new mechanism, and every one is a hole a real person fell into. **Together they are exactly what the PGL charter calls the "mom test"** — can one person install this from the README alone.

---

## It also closes an easily missed attack surface

From the self-hosted section:

> Private addresses and plain `http://` work for self-hosted instances on internal networks. Cloud metadata endpoints (`169.254.169.254`) and other special-use ranges are always blocked.

`169.254.169.254` is the instance metadata service on AWS/GCP/Azure. An MCP server that lets you point its base URL anywhere, running on a cloud host, is a ready-made SSRF — have the model read the metadata endpoint and possibly obtain the instance's temporary credentials.

It blocks that by default. **A zero-star project thinking of this deserves a mention.**

---

## Is it for you?

**Yes if**:
- You use GitLab (gitlab.com or self-hosted) and already run Claude Code / Claude Desktop
- You want the PAT to stay local — it runs entirely on your machine
- You want a reference implementation for writing an MCP server, particularly on permissions and context economy

**No if**:
- You are GitHub-only — the repo itself is worth zero to you, though the token-cost table still applies
- You need production guarantees — zero stars, two days old, an author with no other work; maintenance continuity is a real question

---

## Gaps: I did not install it

Stated plainly — this post is based on source and documentation, **without installing or running it**:

1. **The real success rate of all 92 tools is unverified.** How many work end-to-end, and how many break on edge cases, is unknown.
2. **The 27,340 figure is the author's, unreproduced by me.** It depends on which model's tokenizer is used; the order of magnitude should hold, the exact number may vary.
3. **Read-only enforcement strength is untested.** The README claims writes are rejected by name; I did not try to bypass it.
4. **The author is unknown.** A single repo, two days old; long-term maintenance is uncertain.

---

## In one line

The project is a competent GitLab MCP, but its most valuable output is not the 92 tools — it is **a table that quantifies MCP's context tax**, plus three layers of mitigation to go with it.

**The takeaway you can use anywhere**: roughly 297 tokens per MCP tool definition; before installing, ask whether you truly need all of a server's tools; scope by group where you can, go read-only where you can, and keep the token scope as small as it goes.

And a lesson for me: **do not judge whether a tool is worth writing about from the first third of its README.** "The mechanism isn't novel" is not a rejection — finishing the details is its own scarce skill.

> 📌 Repository: https://github.com/penaivanalejandro/gitlab-mcp-server
> MCP protocol: https://modelcontextprotocol.io

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
