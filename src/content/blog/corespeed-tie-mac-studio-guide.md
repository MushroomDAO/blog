---
title: "CoreSpeed TIE：把Mac Studio交给Agent，开源了哪些？"
titleEn: "CoreSpeed TIE: Give Agents Your Mac, Check the Source"
description: "CoreSpeed TIE让MCP智能体调用Mac上的终端、文件、已登录浏览器、桌面应用和本地工具。本文找到官方Apache许可插件仓库，区分插件、原生CLI与托管服务的公开范围，核查Mac安装条件、Node版本变化、目录与审批边界，并记录八项配置检查和原生CLI基础测试，给出分阶段试用与退出方法。"
descriptionEn: "Explore CoreSpeed TIE on a Mac: public plugin sources, native CLI checks, installation requirements, permission boundaries and a staged trial workflow."
wechatTitle: "CoreSpeed TIE：把Mac交给Agent"
wechatDigest: "找到官方插件仓库，核查Mac使用条件，并分清公开源码与权限边界。"
pubDate: "2026-10-31"
updatedDate: "2026-10-31"
category: "Tech-News"
tags: ["CoreSpeed", "TIE", "MCP", "Mac Studio", "Computer Use"]
heroImage: "../../assets/images/corespeed-tie-mac-studio-guide-banner.jpg"
lastPublishedAt: "2026-10-31T05:58:15Z"
---

CoreSpeed TIE让不同位置运行的Agent，经MCP使用一台已有的电脑。对Mac Studio用户来说，价值在于复用机器上的文件、开发环境、应用和登录状态；实际任务仍由相应模型、工具和这台Mac执行。

封面为多端Agent共享工作电脑的概念配图。

官方公开仓库找到了：`corespeed-io/cs`，采用Apache 2.0。需要说明的是，这里公开的主要是插件配置和Skills，不能据此认定整个TIE桌面端、Rust守护进程和云端服务都已提供完整源码。

产品：https://corespeed.io/tie

公开仓库：https://github.com/corespeed-io/cs

本次核查日期为2026年10月31日，仓库固定到提交 `edb5d7f25cbd1fa9d99ed05a9af916dfd88c88b2`。下文区分官方说明、本地已做的检查，以及尚未实测的设备控制能力。

## TIE把哪些本机能力提供给Agent？

TIE的基本结构，是本机守护进程向CoreSpeed建立出站连接，再把可用工具提供给连接该服务的MCP客户端。这样，远端Agent可以使用已有环境，而不必先把整台工作电脑重建到一个新沙箱里。

| 能力 | 可能的用途 | 验收时要看什么 |
|---|---|---|
| Shell与文件 | 读取项目、运行测试、整理生成物 | 工作目录、实际命令与账户权限 |
| 已登录的浏览器 | 在已有会话中处理网页任务 | 页面变化、提交动作与审批条件 |
| 屏幕和桌面应用 | 操作没有合适API的应用 | 辅助功能权限、画面和动作结果 |
| 本地MCP服务 | 让Agent调用本机专业工具 | 服务实际发布哪些工具 |

这里的用途是工作流示例，不是本次已经完成的远程操作测试。浏览器和屏幕能力需要单独开启；本地应用是否能稳定操作，还取决于其界面和驱动支持。

官方将浏览器与屏幕控制建立在Cua Driver之上。对应代码可在 `trycua/cua` 中查看；其许可说明把Driver与其他组件分别列出，不能把某个组件的许可直接套给整个产品集合。

发布介绍：https://corespeed.io/blog/introducing-corespeed-tie

Cua源码与许可：https://github.com/trycua/cua

https://github.com/trycua/cua/blob/main/legal/LICENSING.md

![小M通过工具桥连接远端Agent与本地Mac工作环境，概念示意](../../assets/images/corespeed-tie-mac-studio-guide-fig-01.png)

## 开源仓库里到底有什么？

本次检出的公开树包含插件manifest、MCP配置、`cs-cli`与`cs-api`技能、说明和检查工作流。没有在这份树中找到完整Rust CLI／守护进程工程或Swift菜单栏应用工程。

这不等于证明它们永远不会公开，也不等于判定所有分发物都使用闭源许可。准确结论是：**已验证的公开源码范围是这份插件与Skills仓库，完整产品的可自托管性尚不能由它证明。**

npm上的 `@corespeed/cs` 是另一层分发物。本次读取的版本为 `0.11.1`，包元数据声明Apache 2.0，通过一个JavaScript启动器选择平台原生二进制。许可证标签、可下载二进制和可审阅的完整源码，是三个需要分别核对的问题。

还发现一个容易混淆的旧链接：搜索结果中的 `corespeed-io/corespeed-haas` 在本次查询返回404。不能把旧索引地址当成当前可用的TIE源码入口。

公开插件配置也不是所有客户端都加载同一份工具列表：仓库分别配置了完整MCP入口与较小的插件入口，并提供CLI技能来发现、调用工具。接入后应查看实际可见的工具，不要只按产品首页推测。

固定版本：https://github.com/corespeed-io/cs/tree/edb5d7f25cbd1fa9d99ed05a9af916dfd88c88b2

npm分发：https://www.npmjs.com/package/@corespeed/cs

## Mac Studio需要什么条件？

TIE本身是工具连接层，是否值得使用，主要看这台机器有没有需要复用的环境。已有Mac上的项目、专业应用和本地服务，往往比“特意买一台高配置机器”更能解释它的价值。

| 使用方式 | 当前官方要求或说明 |
|---|---|
| Tie for Mac菜单栏应用 | macOS 14或以上 |
| 原生CLI | 官方列有macOS Apple Silicon与Intel构建 |
| 从npm／npx启动 | 启动器需要Node.js 20或Bun |
| Mac应用0.2.0 | 已内置原生程序，无需另装Node.js |
| 浏览器与屏幕能力 | 需要开启相应提供者并授予系统权限 |

还需要CoreSpeed账号、网络连接，以及兼容相应MCP接入方式的Agent。

10月23日发布介绍中的“Node 22”要求，不能直接沿用到更新后的Mac应用。10月28日变更记录明确说明，0.2.0已携带原生程序；但通过npm启动仍有启动器要求。应同时确认应用版本和CLI版本。

本次没有找到“运行TIE需要某个M系列高配芯片或大显存”的要求。编译、渲染或本地模型是否需要更多内存与算力，是实际工具任务的要求，需要另行评估。读取帮助命令成功，也不能证明桌面控制在所有系统版本上都可靠。

版本记录：https://corespeed.io/tie/changelog

## 哪些行为已经在本地核查？

在本机Apple M4、16GB内存、macOS 26.6.2环境中，本次执行了两组有限检查。

| 检查 | 结果 | 不能据此推导什么 |
|---|---|---|
| 公开仓库8项本地配置检查 | 全部通过 | 不证明云端策略或桌面驱动安全有效 |
| npm包装包与macOS arm64包摘要 | 与registry公布的SHA-512一致 | 不等于独立供应链审计或发布者身份鉴证 |
| 原生 `cs --version` | 输出 `0.11.1` | 不证明已连接设备 |
| `cs --help`、`cs tie --help` | 均可正常输出 | 不证明认证、远程控制或审批流程跑通 |

配置检查来自上游工作流中的本地命令块，涉及JSON有效性、MCP入口、技能副本和manifest一致性等；没有运行其中的第三方扫描Action。CLI检查使用隔离配置路径，没有登录、配对设备、启动常驻连接或授予桌面权限。

这次也没有测量启动速度、驻留内存和Mac Studio性能。厂商Rust重写文章中的相关数字应视为其测量结果，不能换成这里的“实测”。

工程介绍：https://corespeed.io/blog/we-rewrote-cs-in-rust-with-a-fleet-of-agents

官网文档还出现了较新版本的命令能力，而本次拿到的npm版本是0.11.1。部署时应先看自己安装版本的帮助与变更记录，不把文档里所有命令都当作已在该二进制上验证过。

## 工作目录和审批，是否构成完整隔离？

这是试用前最值得弄清楚的边界。官方CLI文档区分了两件事：文件工具被限制在共享目录内；Shell命令从相应目录开始运行，但以用户账户身份执行，能够触及该账户可以访问的资源。

因此，`--root`不能被理解为操作系统级沙箱。目录设置、提供者开关、命令拒绝列表与审批策略各有作用；需要更强隔离时，还要从账户、任务环境或虚拟机层面设计。

“每次经过规则”也不表示“每次都会弹出人工确认”。CoreSpeed的Approvals文档说明，新组织的该功能默认关闭；开启后，Balanced默认行为允许普通写入，破坏性操作才进入相应判断。TIE本机的开关和拒绝列表是另一层控制，不能把它们混为同一个保证。

实际试用应对照自己的设置验证：哪些读取直接执行、哪些写入暂停、哪些操作被拒绝，以及暂停连接后是否还能调用。这样才能判断规则是否符合自己的工作方式。

CLI边界：https://corespeed.io/docs/cli/tie

审批说明：https://corespeed.io/docs/approvals

![小M区分工作文件夹范围、用户账户权限与审批开关，概念示意](../../assets/images/corespeed-tie-mac-studio-guide-fig-02.png)

## 怎样做一次范围明确的试用？

下面是一条建议的验收流程，并非本次已经远程跑通的记录。

1. 在已有Mac上确认系统与应用版本，准备一个单独的测试文件夹，只放可公开或可丢弃的资料。
2. 通过官方应用或CLI配对设备，先保持私有范围，核对实际启用的提供者和共享目录。
3. 先让Agent列目录、读一份测试文本；再按预期策略创建临时文件，核对结果与活动记录。
4. 确认有需要后，再开启浏览器或屏幕能力，测试一个没有对外提交的简单任务。
5. 验证暂停、恢复与解绑，并检查哪些持久设置仍保留。

官方CLI提供的目录参数可用于限定文件工具范围，例如：

```bash
npx @corespeed/cs@0.11.1 tie --root ~/Work/agent-sandbox
```

文件夹需要事先存在；这条命令会进入配对及持久连接流程，不是单纯检查安装。撤销设备连接使用官方说明中的 `cs untie`。如果只是临时停止，应了解暂停与解绑的区别。

本地保留登录态，也不等于所有业务内容全程离线：工具输出、文件结果或画面可能成为Agent的输入。应该把凭据存放位置、工具数据流向和模型服务的数据政策分别评估。本次没有进行网络抓包验证。

成本也分几层：Mac运行成本、Agent使用的模型费用，以及CoreSpeed平台与工具的计费。官网有免费额度和付费计划，不能据此推导整条工作流无限免费。

价格与额度：https://corespeed.io/pricing

活动记录：https://corespeed.io/docs/activity

![小M沿着读取、受控写入与退出三个步骤验收连接，概念示意](../../assets/images/corespeed-tie-mac-studio-guide-fig-03.png)

## 与Infinity、GameFactory-3A是什么关系？

这条消息中的三个项目分别处理不同层次的问题。Infinity关注Agent等待工具和事件时的运行资源；GameFactory-3A关注游戏资产与引擎代码的生成组织；TIE关注Agent如何接触一台已有电脑的能力。

Infinity官网中的GitHub入口指向 `hydro-project/infinity`；`hydro-project/hydro`是更广的Rust分布式编程框架。7.5万个等待态Agent的内存口径，不是7.5万次同时模型推理，也不能拿来证明TIE的远程控制性能。

Infinity已有文章：https://blog.mushroom.cv/blog/aws-infinity-agent-runtime/

GameFactory-3A已有文章：https://blog.mushroom.cv/blog/gamefactory-3a-open-source-coding-agent-game-generation-ue5-blender-unity/

本次保留这两篇旧稿，不新建重复文章。它们可以作为上下文阅读，但没有在本次把三套系统组合成一个已验证的生产方案。

## 常见问题

### 需要Mac Studio才能用吗？

官方支持范围覆盖其他Mac和平台，Mac Studio不是必要条件。应先确认操作系统、应用和具体任务要求，再判断现有机器是否适合。

### 能否只克隆公开仓库就自托管整个TIE？

目前检查的仓库主要是插件与Skills。没有找到足以支持这一结论的完整产品源码与自托管流程，因此不能作出这样的承诺。

### 安装之后所有Agent都会自动获得整台Mac吗？

实际可达能力取决于设备归属、共享范围、提供者开关、系统授权与规则。应该用实际工具列表和受控任务验证，而不是从“兼容MCP”直接推导权限范围。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

CoreSpeed TIE lets MCP agents running elsewhere use an existing computer. For a Mac Studio owner, its value is reusing files, development environments, applications and signed-in sessions. Models, tools and the host Mac still perform the actual work.

The cover illustrates a shared workstation concept.

The official public repository is `corespeed-io/cs`, under Apache 2.0. Its verified contents are chiefly plugin configuration and skills; that does not establish complete public source for the desktop app, Rust daemon or hosted service.

Product: https://corespeed.io/tie

Repository: https://github.com/corespeed-io/cs

This review pins `edb5d7f25cbd1fa9d99ed05a9af916dfd88c88b2`, checked October 31, 2026. Vendor descriptions and limited local checks are distinguished from untested remote-control behavior.

## What can agents reach?

A local daemon opens an outbound connection to CoreSpeed and exposes enabled tools to its MCP clients. This can reuse an established environment rather than reconstructing it inside a fresh sandbox.

| Capability | Possible use | Acceptance concern |
|---|---|---|
| Shell and files | Read projects, run tests, organize outputs | Working directory and account privileges |
| Signed-in browser | Work within an existing session | Page changes and submission controls |
| Screen and desktop | Operate applications without suitable APIs | OS permissions and observed results |
| Local MCP servers | Reach specialized local tools | Actual exported tool surface |

These are workflow examples, not completed remote tests here. Browser and screen providers require separate enablement; application reliability depends on driver and UI support.

CoreSpeed identifies Cua Driver as the browser/screen foundation. Its source is in `trycua/cua`, whose licensing separates Driver from other components.

Launch: https://corespeed.io/blog/introducing-corespeed-tie

Driver source and licensing: https://github.com/trycua/cua

https://github.com/trycua/cua/blob/main/legal/LICENSING.md

![XiaoM bridges a remote agent to local Mac tools; conceptual illustration](../../assets/images/corespeed-tie-mac-studio-guide-fig-01.png)

## What is actually public?

The checked tree contains manifests, MCP configuration, CLI/API skills, documentation and checks. It does not contain a complete Rust daemon/CLI project or Swift menu-bar app project. That bounds what was verified, rather than proving the components will never be published or all distributions are proprietary.

The inspected npm package, `@corespeed/cs` 0.11.1, declares Apache 2.0 and launches platform-native binaries through JavaScript. A license label, downloadable binaries and auditable complete source are separate observations. An older indexed `corespeed-haas` repository link returned404.

Plugin configurations also distinguish the full MCP endpoint from a smaller plugin surface, with CLI skills for tool discovery and calls. Check the actual loaded tools rather than inferring them from the landing page.

Pinned source: https://github.com/corespeed-io/cs/tree/edb5d7f25cbd1fa9d99ed05a9af916dfd88c88b2

Package: https://www.npmjs.com/package/@corespeed/cs

## What does a Mac require?

The useful question is whether an existing machine holds an environment worth reusing. TIE itself does not establish a need to purchase a high-end workstation.

Access also depends on a CoreSpeed account, network connectivity and a compatible MCP client.

The current Mac app requires macOS 14 or later. Version 0.2.0 bundles its native program and no longer needs a separate Node installation. The npm/npx launch path still needs Node 20 or Bun. CLI builds cover Apple Silicon and Intel Macs.

The October 23 launch's Node 22 requirement is therefore stale for the updated app. Check both app and CLI versions. Compute and memory requirements for compilation, rendering or local models belong to those workloads, not to the bridge alone.

Changelog: https://corespeed.io/tie/changelog

## What was checked locally?

Tests ran on Apple M4, 16 GB, macOS 26.6.2:

| Check | Result | Limit |
|---|---|---|
| Eight upstream local configuration checks | Passed | Not cloud-policy or driver validation |
| npm wrapper/native package digests | Matched registry SHA-512 | Not independent publisher attestation |
| Native `cs --version` | 0.11.1 | No paired device established |
| CLI and Tie help | Printed successfully | No authentication or remote-control validation |

The repository checks cover JSON, endpoint configuration, skill copies and manifest consistency. The third-party scanner Action was not run. An isolated config path was used for help/version checks; no login, pairing, persistent connection or OS permission grant occurred.

No startup, RAM or Mac Studio benchmark was performed. Performance figures in the Rust rewrite post remain vendor measurements. Documentation also includes newer commands than the inspected 0.11.1 binary, so check installed help and release notes before assuming availability.

Engineering post: https://corespeed.io/blog/we-rewrote-cs-in-rust-with-a-fleet-of-agents

## Are directories and approvals complete isolation?

Official CLI documentation distinguishes file-tool roots from shell execution. File tools stay within shared roots; commands start there but run with the user's account privileges. A root setting is not an OS sandbox.

Provider switches, deny lists and approval policy are distinct controls. The platform's Approvals documentation says new organizations start with that feature off; after activation, Balanced permits ordinary writes by default. Passing through policy does not imply a human prompt for every action. Verify the actual configuration with controlled reads, writes, denials and pause tests.

CLI boundaries: https://corespeed.io/docs/cli/tie

Approval policy: https://corespeed.io/docs/approvals

![XiaoM distinguishes a working folder, account privileges and approval controls](../../assets/images/corespeed-tie-mac-studio-guide-fig-02.png)

## How should a first trial work?

This is a proposed acceptance sequence, not a completed end-to-end deployment:

1. Confirm versions and prepare a dedicated folder containing disposable test data.
2. Pair through the official app or CLI, initially retaining private scope and checking enabled providers.
3. List and read test files, then perform a controlled write under the intended policy and inspect the outcome.
4. Enable browser/screen only when needed and try a task without external submission.
5. Verify pause, resume and revocation, including persistent settings.

For an already-existing test directory, the inspected CLI supports:

```bash
npx @corespeed/cs@0.11.1 tie --root ~/Work/agent-sandbox
```

This enters pairing and persistent connection setup; it is not a harmless installation check. Official documentation distinguishes pausing from revoking with `cs untie`.

Local credentials do not establish that every business-data result remains offline. Tool outputs, file results or screen content can become agent inputs. Evaluate credentials, tool data flows and model-provider policies separately; no network-capture validation was performed here.

Costs likewise include host operation, model use and platform/tool charges. Free credits and paid plans do not establish unlimited free operation.

Pricing: https://corespeed.io/pricing

Activity records: https://corespeed.io/docs/activity

![XiaoM progresses through read, controlled write and exit checks](../../assets/images/corespeed-tie-mac-studio-guide-fig-03.png)

## How does it relate to Infinity and GameFactory-3A?

Infinity addresses runtime resources while agents await events or tools. GameFactory-3A organizes game assets and engine-code generation. TIE connects agents to capabilities on an existing computer.

Infinity's homepage links to `hydro-project/infinity`; `hydro-project/hydro` is the broader distributed Rust framework. The 75,000-idle-agent memory claim is not simultaneous model inference or evidence of TIE performance.

Existing Infinity article: https://blog.mushroom.cv/blog/aws-infinity-agent-runtime/

Existing GameFactory-3A article: https://blog.mushroom.cv/blog/gamefactory-3a-open-source-coding-agent-game-generation-ue5-blender-unity/

These articles are reused, not republished. No combined production system involving all three was tested in this review.

## FAQ

### Is Mac Studio required?

No. Official platform support is broader. Match the OS, applications and actual workload to the existing machine.

### Can the public repository self-host all of TIE?

The inspected tree chiefly supplies plugins and skills. Complete product source and a self-hosting workflow were not established.

### Does installation give every agent the whole Mac?

Reach depends on ownership, sharing, providers, OS grants and policy. Verify actual tool visibility and controlled tasks instead of inferring permissions from MCP compatibility.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
