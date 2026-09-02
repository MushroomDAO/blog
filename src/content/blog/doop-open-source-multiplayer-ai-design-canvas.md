---
title: "Doop：Paper.design 的开源替代——人和 AI Agent 实时同画布做设计"
titleEn: "Doop: The Open-Source Paper.design Alternative Where Humans and AI Agents Design Together, Live"
description: "kgoedecke/doop 开源仅两周：多人实时设计画布，Canvas+Frame 用 sandboxed iframe 渲染真实 HTML，AI agent 通过内置 MCP server（15 个工具）流式把设计画进画布，人在旁边实时围观甚至接管。bun run dev 零配置自托管，内置 Postgres。AGPL-3.0，564 star。"
descriptionEn: "kgoedecke/doop, two weeks old: a multiplayer design canvas where Canvas+Frame render real HTML in sandboxed iframes, and AI agents stream designs in live through a built-in 15-tool MCP server while humans watch — or take over. Zero-config self-host via bun run dev, embedded Postgres. AGPL-3.0, 564 stars."
pubDate: "2026-09-02"
updatedDate: "2026-09-02"
category: "Tech-Experiment"
tags: ["AI Agent", "MCP", "开源", "设计工具", "多人协作", "TypeScript", "Claude Code", "自托管", "AGPL"]
heroImage: "../../assets/images/doop-open-source-multiplayer-ai-design-canvas-banner.jpg"
author: "Mycelium Protocol"
---

项目地址：https://github.com/kgoedecke/doop
许可：AGPL-3.0 ｜ 语言：TypeScript ｜ 创建于 2026-08-22，本文写作时不到两周，564 star，12 个 open issue

## BLUF

Doop 是 Paper.design 的开源替代：一块多人实时设计画布，人在浏览器里直接编辑，AI agent 通过内置的 MCP server 编辑——两者共享同一个画布，同一份状态，实时可见。核心模型很简单：**Canvas 装 Frame，Frame 是真实 HTML，渲染在沙箱 iframe 里**，不是截图、不是设计稿导出件。Agent 把设计一段一段"流"进 Frame，人在旁边看着它长出来，看不顺眼随时接管编辑。

和大多数"agent 生成一版设计甩给你看"的工具不同，Doop 的定位是**过程可见、可被打断**——这也是它和本站之前写过的批量出图管线（比如无人值守跑一批 banner）完全不同的一类工具：那些是流水线，Doop 是一个人和 agent 共享的工作台。

## 它怎么工作：Canvas + Frame + 沙箱渲染

一个 Canvas 是一个可分享的地址（`/c/<id>`），里面装若干 Frame——每个 Frame 是一块渲染真实 HTML 的画板，跑在 `<iframe sandbox="allow-scripts">` 里：脚本能执行，但没有同源访问权限，也碰不到宿主应用。新 HTML 通过 `postMessage` 传入，用 DOM diff 原地打补丁（`src/lib/frameRuntime.ts`），不会整页刷新导致白屏——`<script>` 变了就重新执行，没变的样式和字体保持不动。

多人协同走的是一个 per-canvas 的 WebSocket room：光标位置、在线状态、每个 Frame 谁在编辑、拖拽位置，全部实时广播；REST 和 MCP 的写操作都经过同一套"共享 actions 层"广播进房间，所以人和 agent 的编辑走的是完全相同的管线，不存在"agent 编辑是二等公民"的情况。

## Agent 怎么把设计"画"进去：15 个 MCP 工具

`/mcp` 是一个无状态的 streamable HTTP 端点，走标准 MCP OAuth——`claude mcp add --transport http doop http://localhost:4300/mcp` 一条命令接入 Claude Code，浏览器弹窗授权后，agent 就"以你的身份"操作画布。

| 工具 | 作用 |
|---|---|
| `get_guide` | agent 接入后第一件事：加载完整操作手册 |
| `set_status` | 广播一句话"我在做什么"，实时显示在工作条和活动流 |
| `get_feedback` | 拉取并认领人类留下的反馈（给轮询式的"值守 agent"用）|
| `list_canvases` / `create_canvas` / `get_canvas` | 列出 / 创建 / 读取画布布局 |
| `view_website` | 只读预览一个公网页面（截图+文字），不改画布 |
| `import_webpage` | 把一个公网 URL 导入成可编辑的 HTML 快照 Frame |
| `create_frame` / `get_frame` | 新建 / 读取 Frame（含 HTML）|
| `get_frame_screenshot` | 无头渲染 Frame 并返回 PNG——让 agent"看见"自己画的东西 |
| `set_frame_html` | 一次性替换 Frame 的 HTML，全员实时看到 |
| `append_frame_html` | **流式**：分块（`start`/`done`标记）把设计画进去，人看着它一点点长出来 |
| `edit_frame_html` | 精确 find/replace，原地变形渲染，不用整块重发 |
| `update_frame` / `delete_frame` | 改名/移动/缩放 / 删除 |

三层"教 agent 怎么用"的设计值得单独提一句：MCP `initialize` 时的简短 instructions、`get_guide` 工具返回的完整操作手册（含"必须先截图审查"这类强制检查点）、以及每次工具调用结果里的"结果提示"（比如告诉 agent "你还没看过自己画的东西，调 `get_frame_screenshot` 再继续"）。这套三层引导据 README 说和 Paper.design 商业版用的是同一套架构。

**流式渲染怎么做到不卡顿**：agent 发来的 HTML 立刻落库，但观众看到的是打字机式的匀速重放（约 500 字符/秒，遇到积压会加速到约 8 秒内追平）——哪怕 agent 一次性甩来一大段完整 HTML，观众看到的也是平滑的"正在画"效果。重放过程中还会做"愈合"：半截的标签会被丢掉，没闭合的 `<script>` 直接截断（绝不执行半成品 JS），没闭合的 `<style>` 会被补上，防止页面因为半截样式而空白。人如果在检查器里直接改了 HTML，会立刻打断任何正在进行的流式重放——人接管优先。

## 三条接入路径

```bash
# 本地开发，零配置，内置 PGlite（嵌入式 Postgres），无需外部服务
git clone https://github.com/kgoedecke/doop && cd doop
bun install && bun run dev
# Web: localhost:4300  API/WS/MCP: localhost:4400
```

```bash
# 生产自托管，一条命令
BETTER_AUTH_SECRET=$(openssl rand -hex 32) docker compose up -d
```

或者直接用官方托管版 doop.design，不想自己跑就用这个。三条路径背后是同一套账号体系（better-auth，邮箱+密码或 OIDC SSO），画布默认私有，Figma 式的邀请协作或链接分享二选一，MCP 接入的 agent 继承批准者本人的权限——不会出现"agent 权限比人大"的情况。

## Doop Agent：内置团队 vs 自带 agent，两条完全独立的账单

这是这个项目里我觉得最值得展开说的一块，因为它把"谁付钱"和"谁在设计"这两件事拆得很干净：

- **路径一：Doop Agent（内置）**——排一张卡片或在评论里 `@提及`一个角色（UX/文案/品牌/无障碍），服务端自己的 agent 会在没有人盯着的情况下把活接下来。默认吃服务端配置的 `ANTHROPIC_API_KEY`，`RESIDENT_TASK_LIMIT` 免费任务用完后，账号必须连一个 ChatGPT 订阅或 OpenAI key 才能继续——连上的那一刻起就不再计入服务端的免费额度，账单转到用户自己头上。
- **路径二：自带 agent（BYO，走 MCP）**——Claude Code 或任何 MCP 客户端 OAuth 接进来，跑在**你自己的订阅上，从不计费给服务端**。

README 专门用粗体强调了一句容易被忽略的合规提醒：用第三方服务器驱动用户的 ChatGPT 订阅，这件事本身不在 OpenAI 服务条款的许可范围内，重度使用可能触发账号限流甚至封禁——API key 付费路径才是官方认可的稳妥方案；如果自建实例要接入真实用户，`CHATGPT_CONNECT_DISABLED=1` 能直接关掉订阅接入这条路，只留 API key。这条提醒对任何想拿 Doop 底座做自己产品的人都很重要，容易被"零配置就能跑"的宣传掩盖过去。

## AGPL-3.0：自己用没问题，包装成服务给别人用要小心

License 是 GNU AGPL v3——README 原话："use it, self-host it, modify it — but if you offer a modified version as a service, you must publish your changes under the same license"。翻译过来：本地跑、内部用、随便改都没问题；但如果你改了代码之后把它包装成一个服务开放给别人用（哪怕不分发二进制，只是当 SaaS 跑），也必须把你的修改开源。这和本站更常见的 MIT/Apache-2.0 项目不是一回事，商用前务必看清楚。另外 doop 这个名字和 logo 是商标，不在代码许可范围内，衍生服务需要换名字。

## 缺口，说清楚

- **早期项目**：创建不到两周，12 个 open issue，单人（Kevin Goedecke，本职在做 AI 演示文稿工具 SlideSpeak）主导维护，长期稳定性和真实多人并发场景都还没有社区规模验证。
- **本站没有一手实测**：本文所有信息来自仓库 README 和公开的 gh api 元数据，没有实际自托管跑一遍、也没有真的接 Claude Code 测过 15 个 MCP 工具的实际手感——这些细节（比如 `append_frame_html` 分块大小怎么调最流畅、`get_frame_screenshot` 的渲染延迟有多少）需要真正部署一次才能补全。
- **生产部署有硬要求**：`bun run dev` 的零配置只适合本地试玩，README 明确说生产环境"别跳过"接一个真正的 Postgres——PGlite 只适合单实例+持久化卷这种场景，不是生产默认项。

## FAQ

**这和用 Figma 插件调 AI 生图有什么区别？**
区别在"过程"：Figma 插件是"AI 生成一版，你要么接受要么重来"，Doop 是 agent 和人共享同一个实时画布，agent 流式地画、每一步都可见，人可以在任意时刻直接接管编辑，agent 甚至能"看见"自己的渲染结果（`get_frame_screenshot`）再自我修正，不是一次性产出物。

**免费额度用完之后被迫停用吗？**
不会。README 说得很清楚："free tier is a trial that gets people here, not a balance to spend down first"——连上自己的 ChatGPT 订阅或 OpenAI key 从下一个任务立刻生效，不需要等免费额度先清零。

**自己接的 agent（比如 Claude Code）要花服务端的钱吗？**
不需要。走 MCP OAuth 接入的 agent 完全跑在使用者自己的模型订阅上，"从不计费给服务端"是 README 原话，和内置的 Doop Agent 是两套完全独立的账单体系。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Project: https://github.com/kgoedecke/doop
License: AGPL-3.0 | Language: TypeScript | Created 2026-08-22, under two weeks old at time of writing, 564 stars, 12 open issues

## BLUF

Doop is the open-source alternative to Paper.design: a multiplayer design canvas where humans edit in the browser and AI agents edit through a built-in MCP server — both share the same canvas, the same state, in real time. The core model is simple: **a Canvas holds Frames, and a Frame is real HTML**, rendered in a sandboxed iframe — not a screenshot, not an exported design file. Agents stream a design into a Frame chunk by chunk, and humans watch it grow, free to take over editing at any moment.

Unlike most "agent generates a version and hands it to you" tools, Doop's premise is that the **process itself stays visible and interruptible** — which also makes it a fundamentally different category from unattended batch-generation pipelines this site has covered before (like a script that cranks out a stack of banners overnight): those are pipelines, Doop is a shared workbench for a human and an agent.

## How it works: Canvas + Frame + sandboxed rendering

A Canvas is a shareable address (`/c/<id>`) holding a number of Frames — each an artboard that renders real HTML inside `<iframe sandbox="allow-scripts">`: scripts run, but with no same-origin access and no reach into the host app. New HTML arrives via `postMessage` and gets DOM-morphed in place (`src/lib/frameRuntime.ts`) instead of a full reload — `<script>` tags that changed re-execute, unchanged styles and fonts stay untouched, so nothing white-flashes.

Multiplayer runs over a per-canvas WebSocket room: cursor positions, presence, per-frame "who's editing," drag positions all broadcast live. REST and MCP mutations both flow through the same shared actions layer into that room, so human and agent edits go through identical plumbing — an agent's edit isn't a second-class citizen.

## How agents "paint" into it: 15 MCP tools

`/mcp` is a stateless streamable-HTTP endpoint behind standard MCP OAuth — `claude mcp add --transport http doop http://localhost:4300/mcp` connects Claude Code in one command; a browser window opens for approval, and from then on the agent works **as you**.

| Tool | What it does |
|---|---|
| `get_guide` | First call any connecting agent makes: loads the full playbook |
| `set_status` | Broadcasts a one-line "what I'm doing" to the working strip and activity feed |
| `get_feedback` | Fetch and claim open human feedback (for a polling "caretaker" agent) |
| `list_canvases` / `create_canvas` / `get_canvas` | List / create / read canvas layout |
| `view_website` | Read-only preview of a public page (screenshot + text), doesn't touch the canvas |
| `import_webpage` | Import a public URL as an editable HTML-snapshot Frame |
| `create_frame` / `get_frame` | Create / read a Frame (including its HTML) |
| `get_frame_screenshot` | Headless render returned as PNG — lets the agent *see* its own design |
| `set_frame_html` | Replace a Frame's HTML in one shot, live for everyone |
| `append_frame_html` | **Stream** a design in chunks (`start`/`done` flags) — viewers watch it build up |
| `edit_frame_html` | Targeted find/replace, morphs in place without resending the whole block |
| `update_frame` / `delete_frame` | Rename/move/resize / remove |

Worth calling out is the three-layer approach to steering agents: brief `instructions` at MCP `initialize`, the full playbook returned by `get_guide` (including mandatory checkpoints like "review with a screenshot before moving on"), and result nudges baked into tool responses (e.g., telling the agent it hasn't *seen* its own design yet and should call `get_frame_screenshot`). The README says this three-layer scheme is the same architecture Paper.design's commercial product uses.

**How streaming stays smooth**: agent HTML lands in the store immediately, but viewers see a typewriter-style steady reveal (~500 chars/second, accelerating to clear any backlog within ~8s) — so even an agent that sends one giant chunk plays back as a smooth live build. Mid-reveal HTML gets "healed" before broadcast: a trailing half-written tag is dropped, an unclosed `<script>` is cut (never running half-written JS), and an unclosed `<style>` gets auto-closed so content paints instead of going blank. A human editing the HTML directly in the inspector immediately cancels any open stream — humans always take priority.

## Three ways in

```bash
# Local dev, zero config, embedded PGlite (Postgres), no external services
git clone https://github.com/kgoedecke/doop && cd doop
bun install && bun run dev
# Web: localhost:4300  API/WS/MCP: localhost:4400
```

```bash
# Production self-host, one command
BETTER_AUTH_SECRET=$(openssl rand -hex 32) docker compose up -d
```

Or just use the hosted doop.design if you don't want to run anything. All three paths share the same account system (better-auth, email/password or OIDC SSO); canvases are private by default with Figma-style invite or link sharing, and agents connected over MCP inherit exactly the permissions of the human who approved them — there's no scenario where an agent ends up with more access than the person running it.

## Doop Agent vs bring-your-own: two completely separate bills

This is the part of the project most worth unpacking, because it cleanly separates "who's paying" from "who's designing":

- **Path one: the built-in Doop Agent** — queue a card or `@mention` a role (UX, copy, brand, accessibility) in a comment, and the server's own agent picks it up unattended. It runs on the server's `ANTHROPIC_API_KEY` by default; once `RESIDENT_TASK_LIMIT` free tasks are used up, the account must connect a ChatGPT subscription or OpenAI key to keep going — and the moment it connects, it stops costing the server anything and the bill moves to the user.
- **Path two: bring your own agent, over MCP** — Claude Code or any MCP client connects via OAuth and runs entirely on **your own subscription, never metered against the server.**

The README flags a compliance point worth not missing, in bold: driving a user's ChatGPT subscription from a third-party server isn't something OpenAI's terms sanction, and heavy use risks rate-limiting or suspension — the API-key path is the fully supported route. Anyone standing up a real instance for real users should know `CHATGPT_CONNECT_DISABLED=1` exists to turn the subscription flow off entirely and leave only the key path. It's an easy detail to miss under "zero-config, just works" marketing.

## AGPL-3.0: fine to self-host, be careful wrapping it as a service

The license is GNU AGPL v3 — README's own words: "use it, self-host it, modify it — but if you offer a modified version as a service, you must publish your changes under the same license." Running it locally, internally, or modified for your own use is fine; but if you take a modified version and offer it as a service to others — even without distributing a binary, just running it as SaaS — you must open-source your changes too. That's a different deal from the MIT/Apache-2.0 projects more commonly covered here, and worth checking closely before building a commercial product on top. The doop name and logo are also trademarks, not covered by the code license — a derived service needs to rebrand.

## The gaps, stated plainly

- **Early-stage**: under two weeks old, 12 open issues, maintained by one person (Kevin Goedecke, whose day job is an AI presentation tool, SlideSpeak) — long-term stability and real multiplayer-at-scale behavior haven't been community-validated yet.
- **No independent verification from this site**: everything here comes from the README and public `gh api` metadata — we have not self-hosted it or connected Claude Code to actually exercise the 15 MCP tools. Details like the ideal `append_frame_html` chunk size or `get_frame_screenshot`'s real render latency need an actual deployment to confirm.
- **Production has real requirements**: the zero-config `bun run dev` path is for local play only — the README explicitly says "don't skip" wiring a real Postgres in production, since the PGlite fallback only suits a single instance with a persistent volume, not a production default.

## FAQ

**How is this different from an AI image-generation plugin in Figma?**
The difference is the process: a Figma plugin gives you "one AI-generated version — accept it or regenerate," while Doop puts the agent and the human on the same live canvas — the agent streams, every step is visible, and the human can take over editing at any moment. The agent can even *see* its own render (`get_frame_screenshot`) and self-correct — it's not a one-shot artifact.

**Do you get locked out once the free tier runs out?**
No. The README is explicit: "the free tier is a trial that gets people here, not a balance to spend down first" — connecting your own ChatGPT subscription or OpenAI key takes effect from the very next task, no need to wait for the free balance to hit zero.

**Does an agent I connect myself (like Claude Code) cost the server anything?**
No. An agent connected via MCP OAuth runs entirely on the connecting user's own model subscription — "never metered against the server" is the README's own phrasing — a completely separate billing track from the built-in Doop Agent.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
