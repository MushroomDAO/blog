---
title: "多 Agent 无人值守跑 4 天做了什么：OpenClaw 网关架构拆解"
titleEn: "What Actually Makes a 4-Day Unattended Multi-Agent Run Safe: Inside OpenClaw's Gateway Architecture"
description: "小红书上有人晒出用多 Agent 无人值守跑了 4 天、重构 14 万行代码的实录。真正的问题不是「能不能跑」，是「凭什么敢让它跑 4 天不看」——答案在 OpenClaw（38.8 万 star）的网关架构里：可信网关/不可信执行分离、失败即拒绝的确定性策略、10 分钟 TTL 的一次性凭证、崩溃循环断路器。"
descriptionEn: "A viral post showed a multi-agent run that went unattended for 4 days and refactored 140k lines of code. The real question isn't whether it can run — it's what makes it safe to leave unwatched for days. The answer lives in OpenClaw's (388k-star) gateway architecture: trusted-gateway/untrusted-execution separation, fail-closed deterministic policy, 10-minute-TTL scoped credentials, and a crash-loop breaker."
pubDate: "2026-08-30"
updatedDate: "2026-08-30"
category: "Tech-Experiment"
tags: ["OpenClaw", "多Agent编排", "无人值守", "Agent Gateway", "开源"]
heroImage: "../../assets/images/openclaw-gateway-unattended-multi-agent-orchestration-banner.jpg"
---

> 小红书博主"小天fotos"发了一条视频：多 Agent 无人值守跑了 4 天，重构了自己的项目，产出 14 万行代码、200+ 合并 PR。视频章节标题很实在——"长任务为什么难""编排者 Agent""可复用的 YAML 编排模板""环境也是编排的一环"。这篇不复述那条视频，视频只是引子：真正值得拆的是让这件事"敢无人值守"的底层机制——OpenClaw（GitHub 38.8 万 star）的网关架构。

## 先说清楚问题是什么

"多 Agent 无人值守跑 4 天"这句话本身不难做到——写个循环脚本、接上 LLM API，理论上也能"跑 4 天"。难的是**敢**跑 4 天：中途一个 Agent 犯了错、拿到了不该有的权限、陷入死循环疯狂调用付费 API、或者环境状态被搞乱到没法恢复，操作者不在场，谁来兜底？

这不是"多 Agent 编排"这个话题第一次被讨论，但大部分讨论停在"怎么分工"（谁做规划、谁做执行、谁做审查），很少有人认真回答"权限失控了怎么办"这个更硬核的工程问题。视频里提到的"环境也是编排的一环"其实已经点到了这一层，只是没有展开讲。

## 什么让无人值守多天运行是安全的，而不是一场赌博？

OpenClaw 的定位是"跑在你自己设备上的个人 AI 助手"，架构核心是一句话："可信网关，不可信执行，确定性策略"（trusted gateway, untrusted execution, deterministic policy）。拆开看，这几条机制直接对应"无人值守敢不敢跑"这个问题：

**网关和执行分离**。凭证、策略判断、状态都留在网关这一侧；真正干活的执行环境（本地沙箱、远程节点、云端 worker）拿不到网关的权限——即使某个 Agent 的执行环境被攻破或者行为失控，它手里也没有可以进一步作恶的凭证。

**拒绝是结构性的，不是"请模型自觉"**。官方文档原话是"denial is structural, not a request the model is asked to honor; approval paths fail closed"——工具要么存在要么不存在，模型没法"商量"出一个例外；审批链路一旦走不通，默认结果是拒绝，不是放行。

**凭证按次发放、10 分钟过期**。云端 worker 拿到的是"per-dispatch minted credentials stored hashed at rest with a ten-minute TTL"——每次任务派发单独铸造凭证，落盘时哈希存储，10 分钟自动失效。就算凭证泄露，能被滥用的时间窗口也被死死摁住。

**执行环境默认隔离**。跑在 Docker/Podman 容器里，"read-only root, all capabilities dropped, non-root user"是默认配置；远程节点要经过内容哈希校验。

**崩溃循环断路器**。原文是"crash-loop breaker keeps the control plane reachable while suppressing channel autostart"——一旦检测到反复崩溃，断路器会压住自动重启，但控制面板本身保持可访问，操作者随时能回来接管，不会陷入"疯狂重启→疯狂出错"的死循环。

**审批门槛绑定内容哈希**。需要审批的命令要同时匹配"canonical command, cwd, environment hash, and content-hashed file operands"——不是"这条命令批准过就永远批准"，环境或者文件内容一变，哈希对不上，自动拒绝重新审批。这是防止"用一次批准的操作去偷换成另一次危险操作"的具体手段。

## 一个容易被忽略的关键限制

这套安全机制不是开箱默认开启的。官方原话："Sandboxing and approvals are off by default. Hardening is deliberate configuration"——沙箱和审批默认是关的，个人日常使用不需要这层开销，但**要做无人值守、企业级的长时间运行，必须显式开启**。

这一点值得单独拎出来说：如果只是照着教程"装完就跑"，默认配置跑无人值守多天大概率不是那条视频展示的安全版本——那条 4 天无人值守的实录，前提大概率是操作者已经手动打开了沙箱和审批这两层。

## 视频里那三个实践细节，套进这套架构看

- **编排者 Agent**：一个专门负责"分派任务、不做具体执行"的上层 Agent，天然贴合网关"只做策略判断，不碰真正执行"的分层——编排者本身也应该是"可信"那一侧，不该直接拿到执行权限。
- **可复用的 YAML 编排模板**：把任务拆解成结构化、可重放的配置，而不是每次现场即兴指挥——这跟网关"审批绑定 canonical command + 内容哈希"是同一个思路：结构化、可复现的任务描述，才有东西可以被稳定地校验和批准。
- **环境也是编排的一环**：这正好呼应"执行环境隔离 + 内容哈希校验"——环境状态本身要能被明确追踪、可复现，不然任务失败了都不知道是代码错了还是环境漂移了。

## 想自己试，先做这三件事

不用照抄整套 4 天无人值守，先把安全层立住：显式打开沙箱和审批（默认是关的）；把常跑的任务写成结构化模板而不是临场指挥，方便复现和审计；控制面板保持可访问，随时能接管——不是"设置完就撒手不管"，是"设置完让人可以安心不盯着"。

原始视频：小红书 @小天fotos，标题"多Agent无人值守跑了4天，怎么编排的？"
OpenClaw 项目主页：github.com/openclaw/openclaw（38.8 万 star，MIT 许可）
架构说明原文：docs.openclaw.ai/start/why-openclaw

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> XiaoHongShu creator "小天fotos" posted a video: a multi-agent run went unattended for 4 days, refactored their own project, and produced 140k lines of code across 200+ merged PRs. The video's own chapter titles are refreshingly concrete — "why long tasks are hard," "the orchestrator agent," "reusable YAML orchestration templates," "environment is part of the orchestration too." This piece doesn't retell that video — it's just the trigger. What's actually worth digging into is the mechanism that makes it safe to *dare* leave this unattended: OpenClaw's (388k GitHub stars) gateway architecture.

## What the question actually is

"Multi-agent unattended for 4 days" isn't hard to attempt — a loop script and an LLM API can technically "run for 4 days" too. What's hard is *daring* to: if one agent makes a mistake mid-run, gains permissions it shouldn't have, spirals into a runaway loop burning paid API calls, or corrupts environment state past recovery, and no one is watching — who catches it?

Multi-agent orchestration itself isn't a new topic, but most discussions stop at "how to divide labor" (who plans, who executes, who reviews) and rarely engage the harder engineering question: what happens when permissions go wrong. The video's own "environment is part of the orchestration too" chapter gestures at this layer without fully unpacking it.

## What actually makes an unattended multi-day run safe, not a gamble?

OpenClaw positions itself as "a personal AI assistant that runs on your own devices," and its architecture centers on one line: "trusted gateway, untrusted execution, deterministic policy." Broken down, each piece maps directly onto the "can this be trusted unattended" question:

**Gateway and execution are separated.** Credentials, policy decisions, and state stay on the gateway side; the actual execution environments (local sandboxes, remote nodes, cloud workers) never hold gateway authority — even if one agent's execution environment is compromised or misbehaves, it has no credentials to escalate with.

**Denial is structural, not a request the model is asked to honor.** Per the docs: "approval paths fail closed." Tools either exist or don't — a model can't negotiate an exception. When an approval path is unreachable, the default outcome is denial, not pass-through.

**Credentials are minted per dispatch, with a 10-minute TTL.** Cloud workers receive "per-dispatch minted credentials stored hashed at rest with a ten-minute TTL" — freshly minted for each task, hashed at rest, auto-expiring in 10 minutes. Even a leaked credential has a tightly bounded window of usefulness.

**Execution is sandboxed by default.** Runs in Docker/Podman containers with "read-only root, all capabilities dropped, non-root user" as defaults; remote nodes are verified via content hashing.

**A crash-loop breaker protects against runaway restarts.** "Crash-loop breaker keeps the control plane reachable while suppressing channel autostart" — on repeated crashes, the breaker suppresses auto-restart while keeping the control plane reachable, so the operator can come back and take over instead of the system spiraling into crash-restart-crash.

**Approval gates are bound to content hashes.** Gated commands must match "canonical command, cwd, environment hash, and content-hashed file operands" — an approval isn't a blanket "yes forever"; if the environment or file contents drift, the hash mismatches and it's automatically denied, re-requiring approval. This is a concrete defense against swapping a once-approved operation for a different, dangerous one.

## A limitation easy to miss

None of this is on by default. Per the docs: "Sandboxing and approvals are off by default. Hardening is deliberate configuration" — personal daily use doesn't need this overhead, but **unattended, enterprise-grade long runs require explicitly turning it on**.

Worth calling out on its own: if you just install and run with defaults, an unattended multi-day run is very likely *not* the hardened version shown in that video — that 4-day unattended run almost certainly had sandboxing and approvals manually enabled first.

## The three practitioner details from the video, mapped onto this architecture

- **Orchestrator agent**: a top-level agent dedicated to dispatching tasks, not executing them — naturally fits the gateway's layering: the orchestrator itself belongs on the "trusted" side and shouldn't hold direct execution privileges.
- **Reusable YAML orchestration templates**: decomposing tasks into structured, replayable configuration instead of improvised on-the-fly instruction — the same idea as "approval bound to canonical command + content hash": structured, reproducible task descriptions are what can actually be reliably verified and approved.
- **Environment as part of the orchestration**: echoes "execution isolation + content-hash verification" directly — environment state itself needs to be explicitly tracked and reproducible, or a failed task leaves you unable to tell whether the code broke or the environment drifted.

## If you want to try this, do three things first

Don't copy the full 4-day unattended run — get the safety layer standing first: explicitly enable sandboxing and approvals (off by default); write recurring tasks as structured templates instead of improvising each time, so they're reproducible and auditable; keep the control plane reachable — the goal isn't "set it and forget it," it's "set it up so you can safely not be watching."

Original video: XiaoHongShu @小天fotos, "多Agent无人值守跑了4天，怎么编排的？"
OpenClaw project: github.com/openclaw/openclaw (388k stars, MIT license)
Architecture doc: docs.openclaw.ai/start/why-openclaw

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
