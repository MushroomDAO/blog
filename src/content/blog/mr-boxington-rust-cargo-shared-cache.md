---
title: "mr boxington：让 Rust 工作区共享 Cargo 编译缓存"
titleEn: "mr boxington: A shared Cargo cache for Rust workspaces"
description: "mr boxington 的 mbx 为 Rust 项目复用 Cargo 编译产物，管理 target 目录并协调并行构建。本文核对安装与缓存原理，在 Mac 验证不同路径源码副本的命中、修改后的正确输出和清理预览，区分共享缓存、Cargo 新鲜度与私有增量状态，说明工作树、CI、磁盘预算及调试信息路径的使用边界。"
descriptionEn: "Explore mr boxington's shared Cargo cache, target cleanup and build scheduling, with a Mac functional check and clear limits for incremental work and remote CI."
wechatTitle: "mbx：多个Rust工作区共享编译缓存"
wechatDigest: "实测跨路径缓存复用，说明增量编译、磁盘清理与并行构建的边界。"
pubDate: "2026-10-29"
updatedDate: "2026-10-29"
category: "Tech-News"
tags: ["Rust", "Cargo", "mr boxington", "构建缓存", "开发工具"]
heroImage: "../../assets/images/mr-boxington-rust-cargo-shared-cache-banner.jpg"
lastPublishedAt: "2026-10-29T09:13:28Z"
---

mr boxington 的 `mbx` 让不同 Rust 工作区复用已经完成的编译工作，并管理构建文件占用。对于经常切分支、开 worktree，或让多个编程 Agent 同时构建项目的团队，它能减少重复编译和遗留 `target/` 的维护成本。

项目位于 `jdx/mr-boxington`，采用 MIT 许可。本文核查日期为 2026 年 10 月 29 日，文档源码固定为 `14ce94d8db352d0f39c5d02786e20ba5a394a680`，本地验证使用正式发布的 `mbx 1.28.0`，该版本发布于 10 月 26 日。

GitHub：https://github.com/jdx/mr-boxington

文档：https://mr-boxington.jdx.dev/

## mbx 怎样复用编译工作？

Cargo 仍负责依赖解析、构建计划和工具执行。`mbx` 在编译器调用边界检查输入，能找到匹配结果时恢复产物，找不到时调用真实编译器。每条构建命令有自己的缓存代理，命令结束代理也退出，不需要维护一个常驻守护进程。

它会把已知的工作区、输出目录、工具链等路径映射成稳定占位符，再结合源码和相关编译条件生成键。这样，等价源码搬到另一个绝对路径后，仍有机会复用相同工作，而不是因为目录不同就全部重编。

![小M把两个工作区需要的相同编译产物放进一个共享存储，分别取用](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-01.png)

“有机会复用”很重要。工具链、特性开关、目标平台、输入或相关环境变化，都可能改变匹配结果。不能准确建模的调用会 bypass，继续正常运行编译器，不应把它计作缓存故障。

这类复用以编译调用及产物为对象。它不提供函数级 JIT，也不会把新代码热替换进正在运行的程序。

跨路径命中也不等于所有路径字符串都被重写。官方提示恢复的调试信息可能保留原检出路径，调试器源码定位与路径敏感的任务还应单独验证。

原理：https://mr-boxington.jdx.dev/how-it-works

限制：https://mr-boxington.jdx.dev/limits

## 共享缓存、增量状态与 target 是一回事吗？

不是。排查磁盘或构建结果时，先分清这几类数据：

| 数据或机制 | 用途 | 共享范围 |
|---|---|---|
| 共享 action store | 保存可匹配的完整编译产物 | 等价构建和不同检出目录之间 |
| 私有增量状态 | 复用正在修改的 crate 的中间工作 | 属于相应检出目录，不作为完整共享产物发布 |
| Cargo 的 target 目录 | 存放构建结果，并受 Cargo 目录锁影响 | 由该次构建选择的输出目录决定 |
| 托管 target 与 GC | 统一放置、预算管理和回收旧输出 | 受本机配置与清理规则控制 |

默认托管模式会把输出放入缓存目录，并在项目的 `target` 位置留下链接。用户显式设置 `--target-dir`、`CARGO_TARGET_DIR` 等时，工具会尊重指定位置；不能推断这些自选目录都会被自动托管清理。

当前文档还说明，`mbx` 会为活跃编辑的 crate 保留私有增量状态。这与跨工作区共享完整产物是不同机制，也解释了为什么修改源码后不一定继续向共享 store 写入产物。

![小M分别管理共享产物箱和各工作区自己的增量抽屉，不能把两者混为一谈](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-02.png)

托管目录：https://mr-boxington.jdx.dev/managed-targets

增量编译：https://mr-boxington.jdx.dev/incremental

## 在 Mac 上怎样先试用，而不改全部构建习惯？

最容易控制影响范围的方式，是安装后先显式运行 `mbx build`，确认效果再决定是否接管普通 `cargo` 命令。

```bash
cargo install mbx --version 1.28.0 --locked
mbx --version
mbx build
```

从源码安装 `mbx` 需要 Rust 1.91 或以上。官方也提供预编译发行包，当前覆盖 Apple Silicon macOS、Linux x86-64／ARM64 和 Windows x86-64／ARM64。发行包没有列出 Intel Mac 二进制；其他平台可按文档尝试源码构建，本文没有验证 Intel Mac。

若已经使用 mise，当前文档为 mise 2026.9.2 以上提供 Rust 的 `mr_boxington` 选项。这里把作用范围限制在项目中：

```bash
mise use --tool-option mr_boxington=true rust mr-boxington
mise exec -- cargo build
```

这条命令会修改项目工具配置。项目已经固定 Rust 版本时，应在现有配置上增加选项，避免无意更换工具链。需要全局生效时才使用官方示例中的 `--global`。

单独安装后，也可通过 `mbx setup` 配置普通 Cargo 调用；这个步骤会修改包装与接入配置，不是运行 `mbx build` 的前提。编辑器、桌面 Agent 和终端的 PATH 可能不同，终端生效不代表它们也已接入。

安装：https://mr-boxington.jdx.dev/installation

接入：https://mr-boxington.jdx.dev/setup

## 本地功能检查实际看到了什么？

Mycelium Protocol 在 Apple M4、16GB 内存、macOS 26.6.2 和 Rust 1.98.1 上使用官方 Apple Silicon 发行包，核对了下载文件的 SHA-256 与官方清单及 GitHub API digest。一致性校验不等于已完成 Sigstore 证明验证，本次没有验证该证明。

测试全部在临时目录进行，没有运行全局 `mbx setup`，没有修改日常 Cargo 配置。样例只有一个无第三方依赖的 Rust 包，含一个库和一个读取库返回值的可执行程序。

两份相同源码分别放在不同绝对路径，三轮构建各用全新的显式输出目录，共用一个独立 `MBX_CACHE_DIR`。结果如下：

| 场景 | 观察结果 | 程序输出 |
|---|---|---|
| 第一份源码，空共享缓存 | 0 hit，2 次编译无法预先推导键，编译后保存结果 | 本轮用于填充缓存 |
| 第二份源码，不同路径和空输出目录 | 2 hit，恢复了匹配产物 | `42` |
| 第二份源码把库返回值改为 43，再用空输出目录 | 没有命中旧产物，产生 miss 与未查询调用，编辑相关编译保留私有增量状态 | `43` |

冷启动时没有已有 dep-info 或预测信息，可能先无法查键，再把成功产物保存下来。因此第一行的 “0 miss” 不表示没有工作，更不意味着缓存已经命中。

本次显式设置了 `CARGO_INCREMENTAL=0`，但 `mbx` 自身的 learned incremental 机制保留默认值；源码修改后，日志确实记录了私有增量状态。不能把 Cargo 这个环境变量当成关闭 `mbx` 全部增量机制的开关。

第二轮日志还有 5 次 bypass，分别来自编译器查询和标准输入调用；这不否定两次真实缓存命中。`mbx explain --last` 也确认这轮没有记录 cache miss。

这是一项功能检查，不是性能横评。没有测试大项目、真实 Git worktree、并行任务、远程缓存、CI 或 Windows；样例中两个编译单元的结果不能推算成大型项目的加速倍数。16GB 也是测试机器配置，不是官方最低要求。

## 怎样避免把 Cargo 新鲜度当成缓存收益？

在同一个已构建的 `target` 里再次运行，Cargo 可能发现无需调用编译器。即使几乎立即结束，也不能证明产物来自 `mbx` 共享缓存。

官方建议用等价输入和两个此前不存在的输出目录观察复用：

```bash
mbx build --target-dir target/cache-demo-first
mbx build --target-dir target/cache-demo-second
mbx explain --last
```

重复实验时换新目录，保留原缓存，不必先清空整个 store。检查 hit、miss、bypass 和未查询调用，才能知道哪里被复用。普通编译输出里出现 `Compiling`，也不等于每个动作都真的重新运行了编译器，应结合缓存摘要判断。

同样，摘要中的 estimated compiler time avoided 是多个动作的估算和，不能直接当成整次构建节省的墙钟时间。若要报告速度，应另做可重复的冷／热状态、工具链、特性和输入控制。

结果解释：https://mr-boxington.jdx.dev/cache-results

## 多个 Agent 和 CI 应该怎样接入？

多个编程 Agent 各有独立工作区时，`mbx` 可以复用等价依赖编译的结果，减少每个目录都重新做一遍的工作。代码文件和 Git 隔离仍由原来的工作区机制负责。

官方还提供共享编译预算和在途重复工作合并。要让独立 Cargo 命令真正并行，每次构建仍需使用适当的独立输出目录，否则 Cargo 自己的目录锁可能先让它们排队。共享缓存不会自动消除目录锁。

![小M让多个构建使用独立输出托盘，同时遵守一个共同的资源预算](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-03.png)

CI 可以通过 GitHub Action、兼容缓存服务器或 S3 后端接入。各后端的读写策略需要分别配置，不能把所有 PR 都设成可信缓存写入方。官方 Action 默认在成功的默认分支 push 后保存，PR 默认恢复；同仓库 PR 可通过专门选项另存自己的条目，fork PR 不保存。

在实际团队中，先让一个经常重复构建的项目试用。保留原测试和编译检查，对比固定场景的结果与磁盘使用，再决定是否扩大到所有 Agent 或 CI。

并行构建：https://mr-boxington.jdx.dev/scheduling

GitHub Action：https://mr-boxington.jdx.dev/github-action

## 磁盘清理和异常命中从哪里查？

先使用观察命令，确认清理对象和缓存状态：

```bash
mbx explain --last
mbx cache stats --json
mbx gc --dry-run
```

`explain --last` 读取当前工作区最近记录，不会重跑 Cargo。`gc --dry-run` 只预览清理。本次隔离测试也执行了清理预览，没有实际删除缓存或用户项目目录。

需要设置存储上限时，可阅读 `gc.max_total_size`、action store 和私有增量状态的各项预算。不要只看逻辑文件大小就宣称真实磁盘节省比例：reflink、hard link、普通复制以及文件系统都会影响物理占用。

对于多数 Rust 开发者，先解决重复编译、解释缓存结果，再接入磁盘治理和并行预算，比一开始只盯“快了几倍”更容易判断工具是否适合项目。

配置：https://mr-boxington.jdx.dev/configuration

相关阅读：Agent Relay 处理 Agent 之间的消息与上下文，`mbx` 处理它们各自构建时的重复工作。
https://blog.mushroom.cv/blog/agent-relay-coding-agent-collaboration/

## 常见问题

### 安装后会自动让全部 cargo 命令走缓存吗？

直接运行 `mbx build` 即可试用；普通 Cargo 命令是否接入，取决于 mise、shim 或 setup 配置，还要核对执行环境的 PATH。

### 冷缓存第一次构建就能省掉全部编译吗？

不能。首次需要填充 store，还可能没有预测信息。只有后续等价调用才能复用可用结果，不支持建模的调用仍正常编译。

### mbx 会取代 worktree 或提供运行中热更新吗？

不会。它复用构建产物并管理编译资源，不负责源码分支隔离，也不是把函数补丁注入运行中程序的热替换工具。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

mr boxington's `mbx` reuses completed compiler work across Rust workspaces and manages build storage. It targets repeated builds across branches, checkouts and coding-agent workspaces.

The project is `jdx/mr-boxington`, licensed under MIT. This review inspected source commit `14ce94d8db352d0f39c5d02786e20ba5a394a680` on October 29, 2026. The functional check used release `mbx 1.28.0`, published October 26.

Repository: https://github.com/jdx/mr-boxington

Documentation: https://mr-boxington.jdx.dev/

## How does compiler-output reuse work?

Cargo still resolves dependencies, plans builds and runs tools. At the compiler boundary, mbx restores matching outputs or invokes the real compiler. Each command starts its own cache agent, which exits with the build. There is no persistent daemon to maintain.

Known workspace, target and toolchain paths become stable placeholders in cache keys. Equivalent source at different absolute paths can therefore share work. Toolchains, features, targets, inputs and relevant environment still affect matching. Unsupported invocations bypass caching and run normally.

![XiaoM stores matching compiler outputs once for two independent workspaces](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-01.png)

The reuse unit is a modeled invocation and its outputs. This is not function-level JIT or hot replacement inside a running process.

A cross-path hit does not rewrite every path string. Restored debug information can retain the original checkout path. Verify debugger source lookup and path-sensitive behavior separately.

Mechanism: https://mr-boxington.jdx.dev/how-it-works

Limits: https://mr-boxington.jdx.dev/limits

## Separate shared outputs from private incremental state

| Mechanism | Purpose | Scope |
|---|---|---|
| Shared action store | Complete matching compiler outputs | Equivalent builds and checkouts |
| Private incremental state | Intermediate work for edited crates | Associated with its checkout, not published as a complete shared result |
| Cargo target directory | Build outputs and Cargo's directory lock | The output location selected for that build |
| Managed targets and GC | Placement, budgets and collection | Local policy and configured limits |

Managed mode normally puts outputs under the cache directory and leaves a target link in the project. Explicit `--target-dir` or `CARGO_TARGET_DIR` settings are respected. Do not assume these custom directories receive automatic managed-target cleanup.

mbx can retain private incremental state for active edits while sharing eligible complete outputs elsewhere. These mechanisms explain different build outcomes.

![XiaoM keeps shared artifacts separate from private incremental drawers](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-02.png)

Targets: https://mr-boxington.jdx.dev/managed-targets

Incremental state: https://mr-boxington.jdx.dev/incremental

## Try it before changing global Cargo behavior

Install and invoke mbx explicitly:

```bash
cargo install mbx --version 1.28.0 --locked
mbx --version
mbx build
```

Building mbx requires Rust 1.91 or newer. Published binaries cover Apple Silicon macOS, Linux x86-64 and ARM64, and Windows x86-64 and ARM64. The release does not list an Intel Mac archive. Source builds on other platforms are documented but were not tested here.

With mise 2026.9.2 or newer, the documented Rust option can be configured at project scope:

```bash
mise use --tool-option mr_boxington=true rust mr-boxington
mise exec -- cargo build
```

This edits project tool configuration. Preserve an existing Rust pin when adding the option. Use `--global` only when that scope is intended.

Standalone `mbx setup` configures ordinary Cargo invocation; it is not required for explicit `mbx build`. Editors, desktop agents and terminals can have different PATH settings, so check each actual execution environment.

Install: https://mr-boxington.jdx.dev/installation

Setup: https://mr-boxington.jdx.dev/setup

## What did the local functional check show?

Mycelium Protocol tested the official Apple Silicon archive on an M4 Mac with 16GB memory, macOS 26.6.2 and Rust 1.98.1. Its SHA-256 matched the official checksum list and GitHub API digest. The Sigstore attestation was not verified.

Everything ran in temporary directories with a dedicated cache. No global setup or everyday Cargo configuration changed. The sample package had one library, one executable and no third-party dependencies.

Two identical source copies used different absolute paths. Each of three builds had a fresh explicit output directory:

| Scenario | Cache observations | Executed output |
|---|---|---|
| First copy, empty cache | Zero hits; two compilations had no usable prediction before compilation | Used to populate the store |
| Second copy, different path | Two cache hits restored matching outputs | `42` |
| Second copy, library changed to return 43 | No stale hit; miss and unconsulted calls, followed by private incremental handling | `43` |

A cold invocation can lack dep-info or prediction needed to derive a lookup key. Zero misses on that first build do not mean no compiler work occurred.

The test set `CARGO_INCREMENTAL=0`, but left mbx's learned-incremental policy at its default. Logs showed private state after the source edit. That Cargo setting is not a switch for every mbx incremental mechanism.

The restored build also bypassed five compiler-query or standard-input calls. Those bypasses do not negate its two real hits. `mbx explain --last` reported no cache misses for that build.

This was a functional check, not a speed comparison. It did not test large projects, actual Git worktrees, concurrent builds, remote caches, CI or Windows. Two sample compilation units cannot establish a general speedup. The machine's 16GB memory is not an official minimum.

## Avoid confusing Cargo freshness with cache reuse

A repeat build into the same target may need no compiler invocation because Cargo considers outputs fresh. A near-instant finish does not establish shared-cache restoration.

The official diagnostic recipe uses equivalent inputs and previously unused output directories:

```bash
mbx build --target-dir target/cache-demo-first
mbx build --target-dir target/cache-demo-second
mbx explain --last
```

Use new directories for a new experiment instead of deleting the entire store. Inspect hits, misses, bypasses and unconsulted invocations. Cargo's `Compiling` message alone does not tell which actions ran a compiler.

Estimated compiler time avoided is summed across actions. It is not wall-clock time saved. A speed report needs repeatable control over cold and warm state, toolchains, features and inputs.

Counters: https://mr-boxington.jdx.dev/cache-results

## Coordinate builds from multiple agents and CI

Independent coding-agent workspaces can reuse equivalent dependency compilations. Their source and Git isolation remain separate responsibilities.

The project also provides a shared compiler budget and in-flight deduplication. Independent Cargo commands still need suitable separate targets to avoid Cargo's own directory lock. A shared cache does not remove that lock.

![XiaoM gives builds separate output trays under one shared resource budget](../../assets/images/mr-boxington-rust-cargo-shared-cache-fig-03.png)

CI can use the GitHub Action, a compatible cache server or S3. Configure backend trust and write policies explicitly. The official Action saves after successful default-branch pushes by default; pull requests normally restore. An option lets same-repository PRs save their own entries, while fork PRs never save.

Pilot one project with repeated build work. Keep its normal tests, inspect fixed scenarios and storage, then decide whether to expand to all agents or CI.

Scheduling: https://mr-boxington.jdx.dev/scheduling

Action: https://mr-boxington.jdx.dev/github-action

## Inspect before cleaning

```bash
mbx explain --last
mbx cache stats --json
mbx gc --dry-run
```

`explain --last` reads the latest recorded build for the current workspace without rerunning Cargo. GC dry-run previews collection. This check ran the preview without deleting caches or user projects.

Configuration includes a combined budget and separate limits for stored actions and private incremental work. Logical size alone does not establish physical disk savings: reflinks, hard links, copies and filesystems affect allocation.

Start with identifiable repeated compiler work and understandable cache outcomes. Add storage and scheduling policy after confirming those basics.

Configuration: https://mr-boxington.jdx.dev/configuration

Related: Agent Relay handles agent communication and shared context. mbx addresses repeated work in their builds.
https://blog.mushroom.cv/blog/agent-relay-coding-agent-collaboration/

## Frequently asked questions

### Does installation automatically wrap every Cargo command?

No. Explicit mbx commands work directly. Ordinary Cargo integration depends on mise, shim or setup configuration and the process's PATH.

### Can an empty cache skip the first build?

No. Initial builds populate the store and may lack predictions. Unsupported actions continue to compile normally.

### Does mbx replace worktrees or hot-update running programs?

No. It manages compiler outputs and resources. Source isolation and runtime hot replacement are different capabilities.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
