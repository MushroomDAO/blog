---
title: "ra-jit 已更名 blaze：Rust 毫秒重编译与热更新的真实边界"
titleEn: "ra-jit Is Now blaze: Rust Builds and Live Patching"
description: "ra-jit 已更名为 blaze。本文核对官方暖构建基准、常驻编译架构、Apple Silicon 与 Linux 支持，以及 Rust 1.99.0、内存和借用检查限制，并在 M4 Mac 上验证函数修改与测试流程，解释为何局部补丁延迟不能等同于完整构建或画面更新速度，也不能承诺每个项目都快 92 倍。"
descriptionEn: "ra-jit is now blaze. We audit warm Rust build benchmarks, memory costs, live patching limits and platform support, with a functional smoke test on an M4 Mac."
wechatTitle: "ra-jit更名blaze：Rust热编译实测"
wechatDigest: "本机验证函数修改可由常驻编译器处理，拆解加速数据、内存成本与热更新限制。"
pubDate: "2026-10-25"
updatedDate: "2026-10-25"
category: "Tech-News"
tags: ["Rust", "ra-jit", "blaze", "编译器", "热更新", "开发工具"]
heroImage: "../../assets/images/ra-jit-blaze-rust-live-builds-banner.jpg"
lastPublishedAt: "2026-10-25T13:54:05Z"
---

ra-jit 能显著缩短 Rust 项目的修改后构建等待，但“改一行就快 92 倍”不能当作通用承诺。它已在 2026 年 10 月 24 日更名为 **blaze**，旧命令仍兼容；当前官方基准也明确区分首次构建、暖构建和运行中补丁应用。

Mycelium Protocol 核对了官方源码、原始测试记录和安装包，并在 M4、16GB 内存、macOS 26.6.2 上跑通了一个隔离的函数修改与测试示例。本文的速度表来自上游，没有在本机复现 ripgrep、nushell、helix 的性能测试，也没有把运行中热更新写成已完成的本机实测。

官方仓库：https://github.com/indexable-inc/blaze

旧地址会重定向：https://github.com/indexable-inc/ra-jit

资料截止 2026-10-25，文档固定在提交 `988efedad0331e57d4d0184abbd225d2223e7051`。这是 MIT / Apache-2.0 双许可证的开发工具。

## blaze 为什么能省掉修改后的大量等待？

普通 Rust 增量构建已经会复用计算结果。问题是，重新启动编译器、读取状态、处理受影响的 crate、产出目标文件并链接，仍然需要时间。小改动未必对应小等待。

blaze 把工作现场留了下来。它利用 rust-analyzer 的长期驻留查询数据库，保存解析、名称解析、类型分析等信息；修改只使相关查询失效，再由新增的代码生成层把需要更新的函数变成机器码。

默认快速路径使用 Cranelift，项目也提供 LLVM 路径。在可用的情况下，新机器码会拼接进已经存在的程序文件，并把函数入口重定向过去，避免每次都完整链接。遇到尚未覆盖的输入，工具会报告原因并回退 Cargo。

这比“整个项目编译结果全留在内存、永远只编一个函数”更准确：泛型实例、调用关系、签名变化、构建脚本和依赖变动，都可能扩大需要处理的范围。

![小M在驻留的工作现场替换一个函数模块，而不是重新搭建整座结构](../../assets/images/ra-jit-blaze-rust-live-builds-fig-01.png)

架构文档：https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/architecture.md

## “92 倍”和“10–24 倍”应该怎样看？

当前官方汇总图给出的跨项目、跨修改类型几何平均加速，分别约为 macOS arm64 的 10 倍、Linux ARM64 的 24 倍、Linux x86-64 的 11 倍。每个平台在自己的机器上与 Cargo 比较，不能把这些数字当成硬件横评。

以下摘录的是同一文档中“一处函数修改后再构建”的结果，使用 Cranelift、暖状态，并与同机增量 `cargo build` 比较：

| 项目 | 平台 | Cargo | blaze | 上游标注加速 |
|---|---|---:|---:|---:|
| ripgrep 15.1.0 | macOS arm64 | 993ms | 126ms | 7.9 倍 |
| nushell 0.108.0 | macOS arm64 | 1.81s | 454ms | 4.0 倍 |
| ripgrep 15.1.0 | Linux x86-64 | 508ms | 56ms | 9.1 倍 |
| nushell 0.108.0 | Linux x86-64 | 1.25s | 236ms | 5.3 倍 |
| helix 25.07.1 | Linux x86-64 | 2.15s | 116ms | 19 倍 |
| biome 2.6.3 | Linux x86-64 | 2.12s | 2.38s | 0.9 倍 |

这里既有明显提速，也有略慢的案例。另一个“修改被广泛调用的函数”场景中，Linux ARM64 上的 bevy 从 32.13 秒变为 352 毫秒，表中标为约 91 倍。它说明某些修改确实可以接近百倍提速，但不能据此认定所有修改都如此；本文没有在固定版本的当前 README 和基准正文中找到明确的“92 倍”对应项。

测试条件也影响解释：Mac 数据来自 M5 Max、18 核、128GiB 内存，测试时还有其他任务运行，起始负载约 48，重复 3 次取中位数；Linux x86-64 数据来自 EPYC 9R45 主机，限制到 16 核，重复 5 次。它们不是普通 16GB 笔记本的速度承诺。

基准脚本会记录样本、构建实际由谁执行，并在修改后检查程序输出与 Cargo 是否一致。值得同时看到的是，主要编辑操作添加的是不改变程序输出的语句；这能比较构建路径，但不能代替每种真实功能变更的语义验证。

官方完整方法、内存表及原始 JSON：https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/benchmarks.md

## 毫秒构建与“不重启热更新”是一回事吗？

要分别计时。

| 计时范围 | 包含什么 | 不应被解释为什么 |
|---|---|---|
| 首次构建与预热 | Cargo 首次构建、工作区加载、数据库准备 | 不属于暖修改的几十毫秒 |
| 修改后暖构建 | 检测修改、分析、代码生成、更新程序文件 | 不一定代表运行中的程序已更新 |
| 运行时应用补丁 | 已生成补丁写入进程、重定向函数入口等 | 不包含前面的编译和队列等待 |
| 用户感知延迟 | 从编辑到新行为、画面或请求结果可见 | 不能直接由补丁应用时间推算 |

官方使用示例中的 `745.4µs` 是一次补丁应用日志。另一个较大的 den 应用记录中，保存到拼接完成需要约 1.0–1.5 秒，运行时应用补丁仅约 0.4–0.6 毫秒。这两组数可以同时成立。

热更新文档还区分单次编辑、连续输入和包含临时语法错误的真实按键回放；不同路径的等待差别很大。部分记录针对历史提交，不能用其中一项最漂亮的数字替代当前所有使用情形。

![小M把冷启动、暖构建与运行时应用补丁放到不同计时器上](../../assets/images/ra-jit-blaze-rust-live-builds-fig-02.png)

热更新原理与测试记录：https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/live.md

## 怎样让正在运行的程序接收新代码？

单纯使用 `cargo blaze build`，主要获得的是构建加速。需要运行中更新时，程序还要接入 `ra-jit-live`，并主动接收补丁。例如在游戏或 GUI 每帧之间调用 `poll`：

```toml
[dependencies]
ra-jit-live = "0.1"
```

```rust
let mut live = ra_jit_live::Live::start().ok();
loop {
    if let Some(outcome) = live.as_mut().and_then(|it| it.poll()) {
        eprintln!("ra-jit: {outcome}");
    }
    // 执行一帧或一个明确的工作单元。
}
```

用 `cargo blaze run` 启动，再在另一个终端修改并执行 `cargo blaze build`。blaze 自己没有文件监听构建模式；想保存即构建，可以另外使用 `watchexec -e rs -- cargo blaze build`。

函数行为变了，往往可以替换。正在持有的数据结构形状变了，就不能假设旧数据自动变成新布局。官方会在相关类型变化、重新链接等情况下要求重启。这决定了它更适合调算法、界面和交互，而不是承诺所有重构都不停机。

截至本文固定版本，使用文档把 Apple Silicon macOS 列为已支持的 live 路径，Linux x86-64 支持已进入 main、随下个版本发布。下载包和 main 文档必须对应着看，不能把 Linux 构建加速直接等同于已发布包支持所有 Linux 热更新。

![小M可以更换同形函数模块，但已有数据改变形状时选择重启](../../assets/images/ra-jit-blaze-rust-live-builds-fig-03.png)

## Mac 和 Linux 上需要准备什么？

官方要求 Rust 1.99.0 及 `rust-src`。当前 `cargo blaze` 会使用这个版本，即使项目另有 `rust-toolchain.toml`。需要 nightly 特性的代码不能因此自动兼容。

| 环境 | 当前应如何判断 |
|---|---|
| Apple Silicon Mac | 支持构建加速；可按对应版本接入 live |
| Intel Mac | 官方安装文档明确不支持 |
| Linux x86-64 / ARM64 | 支持构建加速；预编译 Linux 包要求 glibc |
| Windows | 当前每次构建交给 Cargo，不能据此期待加速 |

更实际的门槛是内存。官方 Mac 峰值表中，ripgrep 的一次函数编辑从 Cargo 的 235MB 变为 blaze 的 2.9GB；nushell 从 1.1GB 变为 12.5GB；bun 对应项达到 26.1GB。这里是执行构建工作的相关进程的峰值统计，不等于仅一个编译器进程，也没有包含整台电脑的所有应用。

因此，我的选型建议是：16GB Mac 先试小项目并观察内存压力；大工作区要把 IDE、浏览器、运行中的程序与编译器一起计入预算。对于上游已经测到二十多 GB 的工作负载，32GB 甚至更大容量才有讨论余地，仍不能仅凭总内存保证跑得顺。这是基于峰值的工程判断，不是官方最低配置。

官方安装命令可用，但建议先下载审阅脚本，再执行：

```sh
curl -fL https://raw.githubusercontent.com/indexable-inc/blaze/main/install.sh -o /tmp/blaze-install.sh
less /tmp/blaze-install.sh
sh /tmp/blaze-install.sh

cd your-project
cargo blaze run
# 修改一个函数后再次执行。
cargo blaze run
cargo blaze status
```

安装器会写入 Cargo 的 bin 目录，并按需安装工具链，默认无需交互。首次验证先用显式 `cargo blaze` 命令，不急于 `cargo blaze enable`：后者会修改用户级 Cargo 配置，影响其他项目；官方也提醒，这条间接路径在某些项目中可能更慢。

安装与使用：https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/install.md

https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/usage.md

## 本机实际验证了什么？

我们没有修改博客项目的 Cargo 配置。测试在 `/tmp` 隔离目录中使用官方 nightly Apple Silicon 包，SHA-256 与发布的 `SHA256SUMS` 一致；归档指纹为 `29e29754367ae1b35d519194dcadded0699505a660fed07b48b4dc704428fb99`。

这份包仍叫 ra-jit，`--version` 显示 `0.0.0`，状态记录的构建标识为 `0.0.0-3ad3370-18e0426dc9ebce00`。因此，下面是该下载包的功能记录，不代表已实测当前 main 的所有功能。

1. 使用 Rust 1.99.0 与 `rust-src` 构建一个无外部依赖的小程序，输出 `41`。
2. 把函数返回值和对应断言改为 `42`，再次运行，输出确实变成 `42`。
3. 输出出现 `[ra-jit]`，状态显示 dev 工作区有一次由 daemon 执行的构建。
4. 首次测试构建后，再运行暖测试，1 项测试通过，test 工作区也记录了 daemon 构建。
5. 独立执行普通 `cargo +1.99.0 check` 成功；完成后停止本次隔离 daemon。

这足以确认“下载包在本机能运行、函数修改能走驻留路径、程序行为随之改变”。它没有测出可用于宣传的加速倍率，也没有验证大型项目、运行时状态保持、长时间稳定性或所有借用错误。

## 为什么仍应保留普通 Cargo 检查？

发布版和 main 的借用检查能力存在差别；当前文档中的覆盖比例也尚未完全同步。共同结论很明确：自有借用检查仍不完整，可能接受 rustc 会拒绝的程序。

`cargo blaze check` 不能自动等同于普通 rustc 的完整判定。尤其开启用户级接管后，原本以为独立的 `cargo check` 也可能经过 blaze。初次评估保留显式命令、独立 rustc 检查与既有 CI，是比较容易核实的做法。

另一个边界是生成程序的运行性能。构建快不意味着生成的程序也更快；官方单独测了 LLVM 路径与 release 程序，结果也有差距。开发期反馈循环与交付时的 release 构建，应分别评估。

借用检查文档：https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/borrowck.md

## 哪些团队值得先试？

最合适的起点是反复修改函数体、测试短、启动或恢复场景很费时的 Rust 项目。游戏和 GUI 可以进一步评估 live，以免每次都重新进入同一个调试状态。

试点时固定一个提交、一个工具链、同样的 features 和 profile，把冷启动、暖修改、回退次数、内存峰值、测试结果分开记录。连续输入和真实功能变化也要覆盖，不能只测“什么都没改”的重复命令。

如果经常改依赖或构建脚本、依赖 nightly、内存紧张，或者必须依靠完整编译器检查才能继续执行，先确认这些边界比追逐最高倍率更有价值。blaze 最值得关注的工程方向，是让编译器成为保留工作现场的服务；它能带来的收益，最终取决于你的修改是否落在可复用的路径上。

## 常见问题

### ra-jit 和 blaze 是两个项目吗？

不是。官方在 2026-10-24 改名，旧仓库地址重定向，`cargo ra-jit` 仍兼容。旧 nightly 文件名和日志标记也可能继续出现 ra-jit。

### 安装后所有 Rust 程序都能不停机更新吗？

不能。运行中更新需要程序接入 live runtime、使用支持的平台和版本；已有数据类型布局变化等情况仍需重启。

### “快 92 倍”可以写进项目收益预期吗？

不能直接写。当前官方有接近百倍的特定修改案例，也有较小收益和退化案例。需要在自己的项目里用同条件、有正确性验证的暖编辑测试建立预期。

原文与后续更新：https://blog.mushroom.cv/blog/ra-jit-blaze-rust-live-builds/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

ra-jit can shorten Rust's edit–build loop substantially. It became blaze on October 24, 2026, and the old command remains compatible. A universal “92× faster” claim is unsupported: warm builds, first-build loading and applying an already compiled live patch measure different work.

Mycelium Protocol reviewed the official source and benchmark records and ran a functional smoke test on an M4 Mac with 16GB memory and macOS 26.6.2. The performance numbers below are upstream results, not our measurements. We did not benchmark large projects or demonstrate live process updates locally.

Repository: https://github.com/indexable-inc/blaze

Former address: https://github.com/indexable-inc/ra-jit

Research cutoff: October 25, 2026. Documentation is pinned to `988efedad0331e57d4d0184abbd225d2223e7051`. The project is dual-licensed MIT / Apache-2.0.

## How does blaze reduce edit time?

Rust already supports incremental compilation. Repeated compiler startup, loading state, processing affected crates and linking still cost time.

blaze retains a rust-analyzer query database in a resident process. An edit invalidates relevant queries, and its code generator turns affected functions into machine code. The fast path uses Cranelift; an LLVM path is also available. When possible, it splices code into an existing executable and redirects function entries rather than performing a full link.

This does not guarantee exactly one function is rebuilt. Generic instances, callers, signatures, build scripts and dependency changes can expand the work. Unsupported cases are reported and may fall back to Cargo.

![Xiao-M replaces a function module while retaining the compiler's working state](../../assets/images/ra-jit-blaze-rust-live-builds-fig-01.png)

Architecture: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/architecture.md

## What do the speedup numbers actually mean?

The official aggregate chart reports geometric means of roughly 10× on macOS arm64, 24× on Linux ARM64 and 11× on Linux x86-64 across projects and edit types. Each platform has its own machine; these are within-host comparisons, not an architecture contest.

Selected single-function edits, with both paths warm and the same linker, show the variation:

| Project | Platform | Incremental Cargo | blaze | Reported speedup |
|---|---|---:|---:|---:|
| ripgrep 15.1.0 | macOS arm64 | 993ms | 126ms | 7.9× |
| nushell 0.108.0 | macOS arm64 | 1.81s | 454ms | 4.0× |
| ripgrep 15.1.0 | Linux x86-64 | 508ms | 56ms | 9.1× |
| nushell 0.108.0 | Linux x86-64 | 1.25s | 236ms | 5.3× |
| helix 25.07.1 | Linux x86-64 | 2.15s | 116ms | 19× |
| biome 2.6.3 | Linux x86-64 | 2.12s | 2.38s | 0.9× |

A different edit to a widely used bevy function on Linux ARM64 takes 32.13s under Cargo and 352ms under blaze, approximately 91×. That is a compelling specific case. We did not locate an exact “92×” entry in the pinned current README or benchmark text, and cannot attribute the circulating headline to that row with certainty.

The Mac benchmark used an 18-core M5 Max with 128GiB memory, other work running and an initial load average around 48; it reports medians of three edits. The x86-64 host used an EPYC 9R45 restricted to 16 cores and five repetitions. Neither is a performance guarantee for a 16GB laptop.

The harness retains samples, records whether the daemon or Cargo built each edit, and checks resulting program output. Its main edit operations add statements that preserve program output. These exercise build paths but cannot validate every behavior-changing application edit.

Methodology and raw records: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/benchmarks.md

## Is a submillisecond patch the entire feedback loop?

No. Keep four boundaries separate:

| Measurement | What it includes |
|---|---|
| First build and warm-up | Initial Cargo work, workspace loading and database preparation |
| Warm edit build | Change detection, analysis, code generation and executable update |
| Live patch application | Installing an already generated patch in a running process |
| Visible feedback | Everything until new behavior or pixels become observable |

The usage guide's `745.4µs` log concerns patch application. A larger den application record reports approximately 1.0–1.5s from save to splicing, followed by 0.4–0.6ms of application inside the running process. Both can be true.

The live documentation also distinguishes isolated edits, bursts and realistic typing with temporary syntax errors. Some results refer to historical commits. One attractive number cannot represent all those workloads or establish keystroke-to-pixels latency.

![Xiao-M keeps cold startup, warm compilation and live patch application on separate timers](../../assets/images/ra-jit-blaze-rust-live-builds-fig-02.png)

Live implementation and measurements: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/live.md

## What is required for live updates?

Fast executable builds alone do not update every running process. The application must link `ra-jit-live` and receive patches, for example by calling `Live::poll` between GUI or game frames. The Chinese section contains the minimal integration example from the usage guide.

Start with `cargo blaze run`, then build edits from another terminal. blaze has no built-in watch mode; a watcher such as `watchexec -e rs -- cargo blaze build` can trigger builds on saves.

Replacing function behavior can preserve process state. Changing a type whose values already exist cannot automatically migrate that state. Relevant layout changes and relinking can require a restart.

At the pinned revision, the usage guide describes live support on Apple Silicon macOS. Linux x86-64 support is on main for the next release. Match documentation to the downloaded version rather than assuming all Linux build acceleration implies released live support.

![A function replacement fits, while changing existing data shape requires a restart](../../assets/images/ra-jit-blaze-rust-live-builds-fig-03.png)

## Which machines and toolchains are supported?

blaze currently requires Rust 1.99.0 and `rust-src`. The current wrapper selects that version even when the project pins another toolchain. Nightly-only code does not become compatible automatically.

| Environment | Current position |
|---|---|
| Apple Silicon Mac | Build acceleration; live integration on supported versions |
| Intel Mac | Unsupported in the installation guide |
| Linux x86-64 / ARM64 | Build acceleration; prebuilt Linux packages require glibc |
| Windows | Builds currently go to Cargo |

Memory is a material cost. The official Mac table lists peak memory during a function edit of 2.9GB for blaze versus 235MB for Cargo on ripgrep, 12.5GB versus 1.1GB on nushell, and 26.1GB for blaze on bun. These peaks include related working processes, not merely one compiler process or every application on the host.

A 16GB Mac is a reasonable place to try a small project while watching memory pressure. Large workspaces need room for the editor, browser and application too. Workloads already measured above 20GB justify considering 32GB or more, without treating that as a guaranteed minimum specification. This is capacity planning, not an official requirement.

Download and inspect the installer before running it:

```sh
curl -fL https://raw.githubusercontent.com/indexable-inc/blaze/main/install.sh -o /tmp/blaze-install.sh
less /tmp/blaze-install.sh
sh /tmp/blaze-install.sh
cd your-project
cargo blaze run
# Edit a function, then repeat.
cargo blaze run
cargo blaze status
```

The installer writes binaries into Cargo's bin directory and installs the toolchain as needed, without prompting. Start with explicit commands. `cargo blaze enable` changes user-level Cargo configuration across projects, and the guide notes that this indirect path can be slower in some projects.

Installation: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/install.md

Usage: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/usage.md

## What did our M4 smoke test establish?

We used an isolated temporary directory and the official nightly Apple Silicon archive. Its SHA-256 matched the published checksums: `29e29754367ae1b35d519194dcadded0699505a660fed07b48b4dc704428fb99`.

The archive still uses the old ra-jit name. Its version command prints `0.0.0`, while daemon status identifies build `0.0.0-3ad3370-18e0426dc9ebce00`. This test therefore covers that package, not every feature described by current main.

We built a dependency-free program returning `41`, changed its function and assertion to `42`, and observed the new output. The next run displayed `[ra-jit]`; daemon status recorded a dev build. After the initial test build, a warm test also used the daemon and passed its one test. A separate `cargo +1.99.0 check` succeeded. We then stopped the isolated daemon and never enabled global interception.

That establishes basic package execution, a resident edit-build path and changed program behavior. It does not establish a speedup ratio, large-project performance, live state preservation or long-term correctness.

## What should remain in the engineering workflow?

Keep independent rustc validation and existing CI. Released and main-branch borrow-checking capabilities differ; the pinned documents also disagree on exact coverage percentages. They agree that the custom checker remains incomplete and can accept programs rustc rejects.

`cargo blaze check` is not automatically an equivalent replacement for full rustc checking. Global interception can also route a seemingly ordinary `cargo check` through blaze. Explicit commands and an independent reference path make an initial trial easier to verify.

Build speed is also separate from generated-program speed. The project measures LLVM-built program runtime against Cargo release builds and reports differences. Evaluate development feedback and production release behavior separately.

Borrow checker: https://github.com/indexable-inc/blaze/blob/988efedad0331e57d4d0184abbd225d2223e7051/docs/borrowck.md

A useful pilot fixes source revision, toolchain, features and profiles, then records cold setup, warm edits, fallbacks, memory and correctness separately. Include real behavior changes and typing patterns. Repeated no-op commands are insufficient.

blaze is most promising for repeated function-body edits and applications expensive to restart or return to a debugging state. Its central engineering idea is retaining compiler working state as a service. The benefit depends on how often your edits stay within the reusable path.

## FAQ

### Are ra-jit and blaze separate projects?

No. The project renamed on October 24, 2026. The former repository redirects, the old command remains compatible, and old packages and logs may still use ra-jit.

### Does installation give every Rust program live updates?

No. Live updates require runtime integration and a supported platform and package version. Existing data-layout changes can still require restarting.

### Can we budget around a 92× speedup?

Not without measuring the relevant workload. Upstream includes near-hundredfold specific edits, modest gains and regressions. Establish a same-condition warm-edit baseline with correctness checks on your own project.

Canonical article: https://blog.mushroom.cv/blog/ra-jit-blaze-rust-live-builds/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
