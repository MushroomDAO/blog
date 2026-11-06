---
title: "NamiDSH实测：用迷你插件系统读懂Agent架构"
titleEn: "NamiDSH: A Tested Guide to Plugin-Based Agent Architecture"
description: "NamiDSH用精简TypeScript展示DeepSeek Harness的插件、依赖注入与Agent循环。本文核对源码行数，运行兼容性脚本、类型检查和离线HTTP工具调用，并发现当前Cordis的waterfall输出差异，解释它适合教学的原因，以及文件访问、会话持久化、权限和生产部署仍需补齐的工程边界。"
descriptionEn: "NamiDSH makes plugin-based agents readable. Local tests expose a Cordis trace difference and clarify offline mocks, file access, and production boundaries."
wechatTitle: "NamiDSH：读懂插件式Agent架构"
wechatDigest: "实跑迷你插件框架，解释依赖、生命周期与工具管线，也核对兼容性和离线运行的边界。"
pubDate: "2026-11-06"
updatedDate: "2026-11-06"
category: "Tech-Experiment"
tags: ["NamiDSH", "DeepSeek Harness", "Cordis", "Agent", "TypeScript"]
heroImage: "../../assets/images/namidsh-cordis-plugin-agent-architecture-review-banner.jpg"
lastPublishedAt: "2026-11-06T08:19:04Z"
---

NamiDSH 是一个把 Agent 插件架构缩小到可阅读规模的教学项目。它最值得学的是服务依赖、插件生命周期和工具拦截如何配合；“完整复现”和“逐行一致”需要附上版本与测试范围。

项目由 aa1143 开源，代码采用 MIT 许可证。本文固定 NamiDSH 提交 `629e9ef`，在 Node.js 26.10.0 上运行现成测试、类型检查和两条离线 HTTP 请求，并把兼容性脚本分别指向 npm 发布版 Cordis 与 DSH 当前 vendored 源码。没有调用收费模型，也没有进行生产压力测试。

仓库：https://github.com/aa1143/NamiDSH

配套交互讲解：https://namiai.tech/dsh/

上游 DSH：https://github.com/deepseek-ai/deepseek-harness

## “一千行”到底包括哪些代码？

README 的“一千来行”是帮助理解规模的说法，不能直接当作全仓库统计。按当前提交的 `.ts` 文件物理行数计算，包含注释和空行：

| 范围 | 文件数 | 行数 |
|---|---:|---:|
| `packages/cordis/src` | 9 | 899 |
| 全部 `packages`，包含 Cordis | 20 | 1,549 |
| 网页入口 `apps` 的 TypeScript | 1 | 34 |
| 原有 `tests` | 2 | 265 |

HTML 界面、文档、配置和锁文件不在上述 TypeScript 数字里。作者比较文章中的 679 行，特指剔除注释、空行后的 Cordis 核心，并非整个带 UI 的应用。

目录树有 Cordis 加 11 个 Agent 相关包。文章中的“11 个包”和仓库中 12 个包目录因此并不矛盾。`tool-time` 等演示组件也提醒我们：文件职责可以映射到 DSH，但不是每个文件都有完全相同的上游实现。

它的价值是把学习路径压短。用整个 DSH 的“一百多万行”与一个教学子集直接相除，得不出等价功能压缩率。

## Cordis 为什么像 Agent 的主板？

把 Agent 循环、模型和工具写进一个文件，最初很省事；当模型要替换、工具要审批、连接要重建时，修改就开始互相牵连。

NamiDSH 用三种角色拆开这些变化：服务定义说明有什么能力，提供者实现能力，消费者只按服务名使用。`llm` 管理模型适配器，`llm-deepseek` 和 `llm-mock` 提供不同实现；`agent-loop` 依赖 `llm`、`tools`、`sessions`、`systemPrompt`，不关心具体模型厂商。

`Context` 是插件获得的上下文，`Fiber` 是插件实例及生命周期的管理者。消费者先挂上、服务后到位也能工作：依赖不齐就等待，到齐后启动；提供者卸载时，依赖者先清理，再等待后续服务恢复。

资源回收同样归属于插件。用 `ctx.effect` 登记工具、连接和监听的撤销函数，卸载时自动清理，避免只把插件对象删掉，却留下仍会触发的监听器。

![小M在迷你主板上更换服务模块，依赖的插件等待并恢复](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-01.png)

这里的错误隔离指框架管理加载失败和生命周期影响，不代表插件运行在独立进程、独立内存或权限沙箱里。错误服务的依赖者仍会受影响；同进程插件也不能视为相互不信任的租户。

## 一次提问怎样经过插件系统？

网页请求从 `webserver` 的 `POST /api/chat` 进入，创建或找到会话，再调用 `agentLoop.run()`。循环先写入用户事件，组合系统提示词和历史消息，然后通过模型服务发起流式请求。

如果模型返回工具调用，`tools` 经过执行前、执行中、执行后三道 waterfall 管线，把结果写回会话，再请求模型生成回答。默认最多 8 轮，避免无限调用工具；这限制的是轮数，并不是完整的成本预算系统。

前置监听可以批准或拒绝调用，执行管线可以接超时或沙箱，后置监听可以处理结果。但这些是扩展位置：拥有一个可挂沙箱的事件，不等于当前已经配置了沙箱。

仓库的 Agent 测试给了一个很好的小实验：挂审批插件，拦住 `get_time`；卸载审批插件，调用恢复；拔掉时间工具，工具表随之改变；拔掉 `llm` 服务，Agent 循环自动停止。它演示的是组件生命周期如何改变实际行为。

![小M让一次工具请求经过审批、执行和结果返回的路径](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-02.png)

会话保存在内存 `Map` 中，记录是只追加的事件数组，发给模型的消息从日志推导。它适合解释事件日志思想，但当前没有落盘恢复、长期记忆、历史压缩或同会话并发串行化。重启可恢复的 Agent，还需要独立的状态设计。

## 14 个场景，真的逐行一致吗？

仓库的 `npm test` 顺序运行兼容性脚本和 Agent 测试。兼容性脚本主要记录 14 个场景的状态输出，比较时要额外运行两次并执行 `diff`；单独看到脚本退出成功，并不等于完成了两套实现的等价性检验。

本次结果如下：

| 实际执行 | 结果与范围 |
|---|---|
| 原有 `npm test` | 成功退出，14 个兼容性场景输出完成，Agent 层断言通过 |
| `npm run check` | TypeScript 检查通过 |
| 同一兼容性脚本对比 npm `@deepseek-ai/cordis@4.1.0` | 两边均 114 行，1 行不同 |
| 对比 DSH 提交 `fcc0ad4` 的 vendored Cordis | 源码经 esbuild 转换后运行，同样 1 行不同 |
| 无模型 Key 的 HTTP 请求 | 首页 200；时间、目录两条请求均收到工具事件和完成事件 |

差异出现在第 9 个场景的 waterfall：迷你版输出 `RAN LS`，上游两种实现输出 `RAN UNDEFINED`。检查源码后可以解释：迷你版把原事件参数继续交给最后的默认函数，上游以 `inner()` 调用默认函数。测试默认函数依赖参数 `c`，于是结果不同。

这不是一次模型回答质量退化，也不是 14 个场景全部失效。它说明**当前版本下，原样脚本的“114 行完全一致”未能复现**。作者当时使用的上游提交未在这份说明中锁定，不能倒推作者历史结果造假。实用的做法是固定双方提交、运行同一脚本并归档差异，而不是只转发兼容性口号。

作者还主动记录过另一处有意差异：插件返回包装对象上的 `update()` 绑定方式不同，测试选择 `ctx.fiber.update()` 绕开它。项目本身已经给了读者充分理由，把它当作精选行为模型，而非完整兼容替代品。

## 离线能跑，究竟跑了什么？

无 `API_KEY` 或 `DEEPSEEK_API_KEY` 时，入口选择 `llm-mock`。它用规则识别时间、目录等词，产生工具调用，再把工具结果组成回答。这里没有下载本地语言模型，也没有离线推理能力基准。

本次在临时工作目录只放一个 `fixture.txt`，启动本地服务后，向 HTTP 接口询问时间和项目文件。两条请求分别触发 `get_time`、`list_dir`，SSE 流均以 `done` 结束，目录结果确实包含测试文件。没有配置模型密钥。

这足以证明网页服务到循环、工具、会话和事件流的主链可以在假模型下运行。它不能证明真实模型的工具选择、复杂任务规划、断线恢复或浏览器界面交互已经通过测试；本次没有执行浏览器自动操作。

首次安装仍需取得仓库和开发依赖。所谓零运行时依赖，不是首次搭建完全不联网；原生运行 TypeScript 也不替代 `tsc` 的类型检查。

![小M区分可观察的离线演示与尚待补齐的生产能力](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-03.png)

## 文件工具与生产部署，还要补什么？

最值得做的练习，是沿着边界继续读源码。`tool-fs` 用 `resolve`、`relative` 检查路径，能挡住直接的 `../` 越界；但没有把符号链接目标解析后再次验证。

在完全自建的临时夹具中，本次确认直接父目录访问被拒绝，而工作目录内指向夹具外普通文件的符号链接仍可读取。没有接触真实私人文件，也未测试任何在线服务。结论限于：当前路径检查是词法边界，不能作为强文件沙箱。

另外，`read_file` 对大文件先完整 `readFile` 再切字符串，因此 `maxBytes` 既不是严格的读取内存上限，也不是精确的 UTF-8 字节截断。让教学样例处理大型不可信输入前，需要调整真正的读取方式。

转向实际服务时，优先补齐以下能力：

- 在 HTTP 和工具入口验证数据，设置请求体、文件、超时和总预算上限。
- 明确工具权限；对敏感文件处理符号链接与竞态，必要时用操作系统隔离。
- 为会话增加持久化、失败恢复、同会话调度和取消传播验证。
- 保持本地监听默认值；若开放到网络，另做认证、访问控制与部署审查。
- 为插件更新、依赖失效、审批撤销和资源回收写可重跑的行为测试。

## 怎样用它学会搭自己的框架？

需要 Node.js 22.18 或以上。可用一个空工作目录开始，避免第一次演示就把日常项目交给工具读取：

```bash
git clone https://github.com/aa1143/NamiDSH.git
cd NamiDSH
npm ci --ignore-scripts
npm test
npm run check
env -u API_KEY -u DEEPSEEK_API_KEY WORKSPACE="$(mktemp -d)" npm start
```

浏览器打开 `http://localhost:3000`。空目录没有文件可列出，可以先询问时间，再往临时目录放一个测试文本。

第一遍先运行离线应用与测试，观察“少一个服务，哪些插件会停止”。第二遍按 `context → registry → fiber → reflect → events` 读核心，把创建、加载、依赖变化和卸载各画出一条路径。

第三遍只做一个改动：沿用测试中的前置管线，加一个明确拒绝某类工具的插件，再验证卸载后行为恢复。第四遍替换一个模型适配器，检查循环是否真的无需知道厂商。接入真实模型时，费用与数据流向需要单独确认。

最后才对照 DSH 的 `vendor/cordis`、`packages/core/agent-loop` 和 `packages/core/tools`，研究教学版省去的隔离、调度、复杂 effect 与诊断机制。此前的 DSH Go 分析也解释了：手机界面和底层 Harness 是不同层次：https://blog.mushroom.cv/blog/dsh-go-android-harness-phone-agent-review/

Mycelium Protocol 的判断是：NamiDSH 把运行时最难讲清的依赖与清理变得可以实验，这就是它的教学价值。是否适合生产，应由具体权限、恢复能力和负载测试决定。

## 常见问题

### 它是 DeepSeek 官方发布的吗？

这是 aa1143 的社区教学项目。可对照官方 DSH 的架构学习，不能将其描述为 DeepSeek 官方精简发行版。

### 离线模式能完成任意任务吗？

不能。默认离线适配器是规则假模型，主要演示时间和目录工具。真实推理要接模型适配器；已有离线演示不代表附带本地大模型。

### 14 个场景是否证明完整兼容？

不能。它们覆盖选定的生命周期行为，且本次对当前上游运行原样脚本发现一行 waterfall 差异。完整兼容还需要版本锁定、更多异常与并发场景。

### 能直接公开部署吗？

当前默认监听 `127.0.0.1`，适合本机学习。公开服务需要另外设计认证、输入限制、工具权限、状态持久化与隔离，不能把教学检查当作安全认证。

## 一手资料与复核范围

NamiDSH 源码固定版本：https://github.com/aa1143/NamiDSH/tree/629e9efcb121b2805a2f3c48565144b732c0ff7f

作者的差异说明：https://github.com/aa1143/NamiDSH/blob/629e9efcb121b2805a2f3c48565144b732c0ff7f/docs/07-compare.md

DSH 对照提交：https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis

测试日志、114 行对照和离线请求证据随本文源材料保存。封面为模块化教学的示意照片，不是 NamiDSH 硬件产品。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

NamiDSH is a teaching project that makes a plugin-based agent runtime small enough to read. Its useful lessons concern service dependencies, lifecycle ownership and tool interception. Claims of complete reproduction or identical behavior require a pinned version and a defined test scope.

Community developer aa1143 publishes it under MIT. This review pins NamiDSH at `629e9ef` and runs its tests, TypeScript check and two offline HTTP requests on Node.js 26.10.0. Compatibility traces are compared with both the published Cordis package and the current vendored DSH source. No paid model or production load was tested.

Repository: https://github.com/aa1143/NamiDSH

Interactive explanation: https://namiai.tech/dsh/

Upstream: https://github.com/deepseek-ai/deepseek-harness

## What does “about a thousand lines” include?

Physical TypeScript line counts at this commit, including comments and blank lines, are 899 across nine Cordis source files, 1,549 across all 20 package source files, 34 in the application entry point and 265 in the two original test files. HTML, documentation, configuration and lockfiles are separate.

The author's 679-line figure refers to the Cordis core after comments and blank lines are removed. It does not describe the whole application with its UI. The directory contains Cordis plus 11 agent-related packages. Responsibility mappings help navigate upstream DSH, but demonstration components are not necessarily identical upstream implementations.

This is a compact learning path. Dividing the size of a full DSH repository by the size of a selected teaching subset would not measure equivalent functionality.

## Why does Cordis resemble an agent motherboard?

NamiDSH separates service contracts, providers and consumers. The model runtime manages adapters, while `llm-deepseek` and `llm-mock` supply implementations. The agent loop consumes four services—`llm`, `tools`, `sessions` and `systemPrompt`—without selecting a vendor itself.

A plugin receives a `Context`; its `Fiber` manages loading and lifecycle. A consumer mounted before its provider waits for dependencies. When the provider disappears, consumers clean up before losing access to the service and wait for recovery.

`ctx.effect` associates resource cleanup with the owning plugin. Listeners, tool registrations and connections can therefore be withdrawn when their plugin unloads. Deleting an object alone would not provide that guarantee.

![Little M replaces a service module while dependent plugins wait and recover](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-01.png)

Framework failure handling is not process or memory isolation. Dependents of a failed service can still stop, and mutually untrusted plugins need an actual security boundary.

## How does a request traverse the plugins?

`POST /api/chat` reaches the web server, creates or retrieves a session and calls the agent loop. The loop appends the user event, derives model messages from history and streams through the selected adapter.

Tool calls pass through pre-execution, execution and post-execution waterfall hooks. Results become session events, followed by another model request. The default eight-round limit prevents an unlimited loop, but is not a complete cost budget.

The existing agent test mounts a guard that rejects `get_time`, unloads it to restore execution, removes the time tool and finally removes the model service. Assertions verify the resulting behavior. Hooks provide extension locations; a place to attach a sandbox does not supply one automatically.

![Little M follows a tool request through approval, execution and returned results](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-02.png)

Sessions are in-memory map entries containing append-only event arrays. Model messages are derived from those events. The sample does not implement disk recovery, long-term memory, history compression or per-session concurrency serialization.

## Are all 14 scenarios identical to upstream?

The compatibility script records traces for 14 scenarios. `npm test` runs this script and the separate agent assertions. A successful exit alone does not compare two implementations: users must run the script twice and diff the output.

| Local check | Observed result |
|---|---|
| Original `npm test` | Completed all scenario traces and passed agent assertions |
| `npm run check` | Passed |
| Comparison with npm `@deepseek-ai/cordis@4.1.0` | 114 lines per trace, one different line |
| Comparison with vendored Cordis at DSH `fcc0ad4` | Same one-line difference after esbuild conversion |
| HTTP requests without model keys | Homepage 200; time and directory tools both completed |

Scenario nine produces `RAN LS` in NamiDSH and `RAN UNDEFINED` in both upstream variants. The miniature implementation forwards the event arguments to the final default function. Upstream invokes that function as `inner()`. The test's default callback expects a parameter, explaining the difference.

This is a narrow event API difference, not a model quality regression or failure of every scenario. It does mean the exact “114 identical lines” claim was not reproduced against the versions checked here. The author's historical upstream commit is not pinned in that explanation; these results do not establish what happened in the original experiment.

The author also documents an intentional difference in method binding on the plugin wrapper. The comparison uses `ctx.fiber.update()` to avoid it. Together, these details make version-pinned trace comparison more informative than an unqualified compatibility label.

## What actually runs offline?

Without `API_KEY` or `DEEPSEEK_API_KEY`, the application selects a rule-based mock. It recognizes time and directory requests, emits tool calls and formats returned results. It does not download or run a language model.

For the HTTP check, a temporary workspace contained one `fixture.txt`. Requests for the time and project files produced `get_time` and `list_dir` events, and both SSE streams ended with `done`. The directory response included the fixture. Model keys were absent.

This verifies the server-to-loop-to-tool-to-session event path under a mock. It does not evaluate real model planning, task success, reconnection or browser interaction. No browser automation was performed. Initial repository and development dependency installation can still need network access, and native TypeScript execution does not replace type checking.

![Little M distinguishes observable offline behavior from missing production capabilities](../../assets/images/namidsh-cordis-plugin-agent-architecture-review-fig-03.png)

## Which boundaries need more engineering?

The file tool uses lexical path resolution to block direct parent traversal. A fixture-only check confirmed that `../outside.txt` was blocked, but a workspace symlink to a harmless file outside the workspace remained readable. No private files or online services were accessed. The finding demonstrates that this check is not a strong filesystem sandbox.

For large files, `read_file` reads the full file before slicing the decoded string. Its `maxBytes` setting is therefore neither a strict read-memory limit nor exact UTF-8 byte truncation.

Before building a real service, add boundary validation, request and file limits, deadlines and total budgets. Define tool permissions and handle symlinks and filesystem races, with OS isolation where appropriate. Add durable session state, recovery, scheduling and cancellation tests. Keep the local listener default; network deployment requires authentication and access controls.

## How should a developer learn from it?

Use Node.js 22.18 or newer. Clone the repository, run `npm ci --ignore-scripts`, `npm test` and `npm run check`. To select the mock explicitly and keep the demonstration away from normal projects, start with `env -u API_KEY -u DEEPSEEK_API_KEY WORKSPACE="$(mktemp -d)" npm start`, then open `http://localhost:3000`. An empty workspace has no files to list; begin with the time tool or add a harmless fixture.

First run the offline application and tests, observing which components stop when a dependency disappears. Then read `context`, `registry`, `fiber`, `reflect` and `events`, tracing creation, loading, dependency changes and disposal.

Next implement one narrow guard using the existing pre-execution pattern and verify that unloading restores behavior. Replace a model adapter without changing the loop. Only then compare DSH's vendored Cordis and its production agent-loop and tool runtime, where scheduling, isolation, effects and diagnostics are more involved.

The earlier DSH Go review distinguishes mobile interfaces from the runtime underneath: https://blog.mushroom.cv/blog/dsh-go-android-harness-phone-agent-review/

Mycelium Protocol's assessment is that NamiDSH makes dependency and cleanup behavior experimentally accessible. Production suitability must be established separately through permissions, recovery guarantees and workload tests.

## FAQ

### Is NamiDSH an official DeepSeek release?

No. It is aa1143's community teaching project, designed to explain architecture that can be compared with official DSH source.

### Can offline mode perform arbitrary tasks?

No. The default adapter is a small rule-based mock, mainly demonstrating time and directory tools. Real inference requires a model adapter.

### Do 14 scenarios prove complete compatibility?

No. They cover selected behavior. This review found a waterfall trace difference against two current upstream forms. Version locking and wider exceptional and concurrent scenarios remain necessary.

### Is it ready for public deployment?

The default server binds to `127.0.0.1`. A public service needs authentication, input limits, permissions, persistence and isolation beyond the teaching sample.

## Primary sources and scope

Pinned NamiDSH source: https://github.com/aa1143/NamiDSH/tree/629e9efcb121b2805a2f3c48565144b732c0ff7f

Author's comparison notes: https://github.com/aa1143/NamiDSH/blob/629e9efcb121b2805a2f3c48565144b732c0ff7f/docs/07-compare.md

Vendored Cordis comparison: https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis

Test logs, both 114-line comparisons and HTTP evidence are archived with the article source. The cover is an illustrative modular electronics scene, not a NamiDSH hardware product.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
