---
title: "Plannotator：把Agent的计划和改动变成可批注的工作台"
titleEn: "Plannotator: A Review Workspace for Coding Agents"
description: "Plannotator为多个编码Agent提供本地浏览器审阅界面，把计划、文档、网页和代码差异变成可定位的反馈。本文核对插件与命令的集成差别、双许可、安装及分享边界，运行39项原始纯模块测试和4个HTTP检查，分析批注如何回到正确会话，并给出团队验收、版本关联、人工批准与反馈闭环的具体工程实践建议。"
descriptionEn: "Explore Plannotator's agent review workflow, integration differences and sharing boundaries, with scoped local checks and practical feedback delivery criteria."
wechatTitle: "Plannotator：给Agent加一个审阅工作台"
wechatDigest: "把计划和代码改动变成可定位的批注，再检查反馈是否回到正确会话并得到落实。"
pubDate: "2026-11-22"
updatedDate: "2026-11-22"
category: "Tech-News"
tags: ["Plannotator", "Coding Agent", "代码审阅", "开源工具", "人工反馈"]
heroImage: "../../assets/images/plannotator-agent-review-feedback-workspace-guide-banner.jpg"
---

Plannotator让你在浏览器里审阅Agent的计划、文档、网页和代码改动，将具体批注送回Agent。它解决的不是“再多写一点代码”，而是当多个Agent同时工作时，人怎样看清提案、指出问题并留下决定。

项目地址：https://github.com/backnotprop/plannotator

本文核对版本为 `7eece56c28d1f03da7c8c6a875d78af0592f6ed0`，根包标为0.29.1，许可表达式是 `MIT OR Apache-2.0`。查询时GitHub页面约14.2k Stars；星数会变化，也不能代替稳定性判断。

## 多代理支持，等于所有功能都一样吗？

不是。仓库列出Claude Code、Codex、Copilot CLI、Gemini CLI、OpenCode、Kiro、Droid、Amp、DeepSeek Harness和Pi等，但应按“怎样接入”和“能拦截什么”来理解。

| 集成情况 | 应关注的差别 |
| --- | --- |
| Claude Code、Copilot CLI | 需要相应插件；计划与反馈工作流受宿主能力影响 |
| Codex | 当前安装说明使用实验性Stop hook；原生Windows仍有手动步骤 |
| Gemini CLI | 自动配置钩子和命令，说明要求0.36.0及以上 |
| OpenCode、DeepSeek Harness | 使用各自插件及计划工具接口 |
| Droid、Amp、Kiro | 命令、插件或示例Agent的配置方式不同；Droid说明尚无计划拦截 |
| Pi | 官方建议安装专用扩展，而不是照搬通用安装流程 |

Inbox还有另一层差别：Claude Code、Pi和OpenCode通过插件衔接，其他Agent可走MCP。不能把“存在接入口”写成“每个宿主都已经完整实测”。本文没有做十种Agent逐一端到端认证。

![小M把不同接口的插头接到同一审阅桌，保留各自适配器](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-01.png)

## 从计划批注到代码审阅，价值在哪里？

普通对话反馈容易丢位置：“第三段不对”“这个函数处理重复请求有问题”。当Agent修改文档、重排代码或切换会话后，指代就可能失效。

Plannotator把反馈放在被审阅内容附近，支持计划、Markdown、HTML及代码差异等场景。Inbox则将多个会话的问题和产物汇总起来，让人晚些回复，减少在终端之间来回寻找上下文的成本。

我们认为真正值得验收的是一条完整链路：批注指向哪份内容，属于哪个会话，发送是否成功，Agent如何修订，修订后是否重新审阅。界面能高亮一段文字，只完成其中一部分。

工程上可给每次审阅绑定版本或内容摘要，并区分“收到反馈”“已修改”“已通过验证”。这些是本文的落地建议，不是声称项目已经提供一套完整合规审批系统。

![小M将带有位置和会话标记的批注送回对应Agent，再接回修改稿](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-02.png)

## 本地具体检查了哪些代码？

Mycelium Protocol检查了三个无依赖核心模块：批注回复关系、反馈文本模板、请求来源判断。仓库直接运行测试时因全局预加载缺少 `@happy-dom/global-registrator` 而未能启动；我们没有将其算成通过。

随后将三个模块及对应原始测试共六个文件按目录复制到隔离位置，保留代码不变，避开与这些纯函数无关的UI预加载。最终39项原始测试通过，共85次断言。

这些测试覆盖孤立批注、自引用和循环回复、模板占位符、计划拒绝与普通文档批注的不同措辞，以及同源、跨站和空来源等请求条件。回复关系处理尤其值得关注：坏数据不应让一条意见从渲染树里消失。

我们另把原始来源判断函数接入临时Bun HTTP服务，发出4次真实POST请求。同源及无Origin的非浏览器请求通过；跨站和 `Origin: null` 请求被拒绝。**这是纯模块接线检查，不是完整Plannotator服务的安全审计。**

本次没有安装正式二进制、改动日常Agent配置，也没有实测浏览器批注、远程PR、Inbox回投或所有宿主。通过39项测试，只说明这些范围内的行为符合断言。

## 本地运行，为什么仍要看分享与联网边界？

本地浏览器界面并不意味着所有功能都不联网。安装会下载发行包；完整安装还可能查询GitHub和npm。URL抓取、AI辅助、远程代码托管和分享又是不同的路径。

当前README说明，小分享将内容放进链接，大分享在加密后上传并于7天后过期；拿到完整链接的人可以读取。加密不等于链接具有接收者身份限制，团队仍需决定哪些内容允许分享。

还要区分旧功能与产品方向：官方文档将开源异步链接分享列为兼容保留、逐步弃用，尚未宣布移除日期；新团队分享方向是托管Workspaces。开源仓库的许可不能直接套到托管服务的全部功能。

分享文档：https://docs.plannotator.ai/open-source/workflows/sharing

仓库提供 `PLANNOTATOR_SHARE=disabled` 关闭URL分享，`PLANNOTATOR_AI=disabled` 关闭部分AI功能；后者不等于关闭全部潜在模型调用，注释终端有独立配置。更可靠的做法是按功能画出数据去向，再决定启用哪些能力。

![小M将本地审阅托盘与可带走的分享信封分开，检查信封中的内容](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-03.png)

## 一行安装之后，还要做什么？

官方提供macOS、Linux及WSL安装脚本，也有PowerShell版本。所谓“一行”是入口简化，不代表所有宿主无需配置。先阅读脚本，再按自己的宿主说明操作。

官方安装说明：https://github.com/backnotprop/plannotator#install

只需要二进制时，可使用文档中的 `--minimal`，跳过自动设置技能、钩子和命令。要做可复核部署，记录安装的发行版本；文档提供的构建证明验证是可选项，不能把默认安装描述成已经验证来源证明。

日常命令例如：

```bash
plannotator review --patch-file reading.diff
plannotator annotate http://localhost:5173
plannotator inbox
```

前者审阅给定差异，第二个针对本地运行页面，第三个打开汇总工作台。是否调用外部Agent、如何返回反馈，仍取决于具体模式和集成配置。

对工程团队，建议先选一个经常返工的流程，例如“接口改造计划审批”，用真实任务检验三件事：意见是否保留正确位置，反馈能否送达原会话，修订是否回应了每条意见。跑通这一条链，再扩大代理数量，比先把十个图标装齐更有价值。

### 批准计划就等于代码正确吗？

不等于。批准只表示接受当前提案；代码、测试、权限和上线验证仍需要单独完成。工具提高反馈的可定位性，不能自动替代人的判断。

### 是否需要同时遵守两份开源许可？

根包使用 `MIT OR Apache-2.0`，表示可按其中一种许可使用，并遵守相应义务；第三方依赖、素材和模型服务条款仍需分别核对。

### 14k Stars能证明适合生产吗？

不能。应检查目标宿主版本、反馈投递、失败恢复、数据去向及退出方式。本次模块检查提供有限证据，不构成整套产品成熟度评级。

参考：

https://github.com/backnotprop/plannotator/blob/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/packages/core/annotation-threads.ts

https://github.com/backnotprop/plannotator/blob/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/packages/shared/request-origin.ts

https://github.com/backnotprop/plannotator/tree/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/apps

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Plannotator gives people a browser workspace for reviewing agent plans, documents, pages and code changes, then returning precise comments to the agent. Its useful role is to make proposals and decisions easier to inspect when several agents are working.

Repository: https://github.com/backnotprop/plannotator

We examined commit `7eece56c28d1f03da7c8c6a875d78af0592f6ed0`. The root package reports version 0.29.1 and `MIT OR Apache-2.0`. GitHub displayed approximately 14.2k stars at lookup; that changing number is not a reliability measure.

## Does multi-agent support mean identical behavior?

No. Host integrations differ in configuration and interception. Claude Code and Copilot CLI use plugins. The Codex instructions currently rely on an experimental Stop hook, with extra native Windows steps. Gemini CLI has a minimum version requirement. OpenCode and DeepSeek Harness use their own plugin interfaces. Droid documents command support without plan interception; Amp and Kiro have different setup steps. Pi uses a dedicated extension.

Inbox integration also has levels: Claude Code, Pi and OpenCode connect through plugins, while other agents can use MCP. An available interface is not proof of end-to-end testing across every host. We did not perform such certification.

![Little M connects different agent plugs to one desk through individual adapters](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-01.png)

## What makes positioned feedback useful?

A chat message such as “the third section is wrong” becomes ambiguous when content moves or the conversation changes. Positioned annotations keep the comment near the material under review. Inbox gathers questions and artifacts from several sessions so a person can return later with a decision.

Our suggested acceptance chain is broader than highlighting text: identify the reviewed version, preserve the target and session, confirm delivery, inspect the revision and review it again. Consider separate states for received feedback, implemented changes and verified outcomes. These are engineering recommendations, not a claim that Plannotator supplies a complete compliance approval system.

![Little M returns a positioned, session-linked comment and receives a revised artifact](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-02.png)

## What did the local checks establish?

Mycelium Protocol inspected three dependency-free modules: reply threading, feedback templates and request-origin decisions. Running their tests directly in the checkout initially failed because the repository-wide UI preload lacked `@happy-dom/global-registrator`. That attempt was not counted as a pass.

We copied the three original modules and their tests, unchanged, into an isolated directory with the same relative layout. All 39 original tests passed, making 85 assertions. They cover orphaned, self-referencing and cyclic reply relationships, template substitution, different feedback modes and request-origin conditions.

The threading rules matter because malformed relationships should not cause a review comment to disappear. A feedback system must preserve objections even when an incoming tool supplies broken metadata.

Four further real POST requests exercised the original origin-check function wired into a temporary Bun HTTP harness. Same-origin and non-browser requests without Origin passed; cross-site and null-origin requests were refused. **This was a narrow module wiring check, not an audit of the full Plannotator server.**

We did not install its release binary, change everyday agent configurations or test the full browser, PR review, Inbox delivery or every supported host. Passing these tests establishes only the checked behaviors.

## Why distinguish local review from sharing?

A local browser interface does not imply that installation, URL fetching, AI helpers, remote repositories and sharing all remain offline. Read the network boundaries of each feature separately.

The current sharing description distinguishes small content embedded in links from larger encrypted uploads that expire after seven days. A person with the complete link can read the content. Encryption does not establish recipient-specific authorization.

Official documentation labels the legacy OSS link-sharing flow deprecated and retained for compatibility, without an announced retirement date. Hosted Workspaces is the direction for new team sharing. The repository license does not establish the terms or availability of every hosted feature.

Sharing reference: https://docs.plannotator.ai/open-source/workflows/sharing

URL sharing can be disabled with `PLANNOTATOR_SHARE=disabled`. `PLANNOTATOR_AI=disabled` disables selected AI features, while the annotate agent terminal is configured separately. Map the enabled paths rather than treating one switch as proof of zero external model access.

![Little M separates a local review tray from an envelope that can leave the desk](../../assets/images/plannotator-agent-review-feedback-workspace-guide-fig-03.png)

## What comes after a one-line installer?

The installer simplifies entry, but host-specific steps remain. Read it before execution and follow the instructions for the target agent. The documented `--minimal` option installs the binary without automatically configuring skills, hooks or commands. Record the release version for reproducibility. Build attestation verification is optional; do not describe the default installation as already having performed it.

Installation reference: https://github.com/backnotprop/plannotator#install

Example commands:

```bash
plannotator review --patch-file reading.diff
plannotator annotate http://localhost:5173
plannotator inbox
```

These represent different review surfaces. External agent use and feedback delivery still depend on the selected workflow and configuration.

Start with one expensive source of rework, such as an interface migration plan. Test whether comments remain correctly attached, reach the original session and receive a substantive response. Expand the number of agents after that loop works.

### Does approving a plan establish correct code?

No. Approval accepts the proposal. Implementation, tests, permissions and deployment verification remain separate responsibilities.

### Must both licenses be applied together?

The root expression is `MIT OR Apache-2.0`, allowing use under either license subject to its obligations. Dependencies, added assets and model services have their own terms.

### Do stars demonstrate production readiness?

No. Check the target host version, feedback delivery, recovery, data movement and exit behavior. Our scoped tests are limited evidence, not an overall maturity rating.

Sources:

https://github.com/backnotprop/plannotator/blob/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/packages/core/annotation-threads.ts

https://github.com/backnotprop/plannotator/blob/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/packages/shared/request-origin.ts

https://github.com/backnotprop/plannotator/tree/7eece56c28d1f03da7c8c6a875d78af0592f6ed0/apps

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
