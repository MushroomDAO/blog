---
title: "STM32MP157F-DK2 硬件迁移记录：把 AirAccount KMS 从模拟器搬到真实 TEE 硬件"
description: "AirAccount KMS 原本跑在 Mac mini M4 的 Docker/QEMU OP-TEE 模拟环境里，断电丢过私钥和 Key ID。这篇记录了迁移到 STM32MP157F-DK2 真实 TrustZone 硬件的环境搭建过程、Mac 连接开发板的真实踩坑，以及后续三阶段路线图。"
pubDate: 2025-12-03
category: "Hardware"
tags: ["STM32MP157F-DK2", "OP-TEE", "TrustZone", "AirAccount", "TEE", "嵌入式", "ARM", "KMS"]
heroImage: "../../assets/images/stm32mp157f-dk2-airaccount-tee-hardware-migration.jpg"
---

> **时间**：2025 年 11-12 月
> **作者**：Jason（AAstar）
> **硬件**：STM32MP157F-DK2（ARM Cortex-A7 双核 + Cortex-M4，OP-TEE/TrustZone）
> **仓库**：github.com/jhfnetboy/STM32MP157F-DK2

## 起因：模拟器里丢了私钥

AirAccount KMS（密钥管理服务）当时跑在 CMU ICDI 的一台 Mac mini M4 上，用 Docker/QEMU 模拟 OP-TEE TrustZone 环境。这套模拟方案出过真实事故：断电之后，Key ID 和已生成的私钥直接丢失——模拟环境本身不提供真正的持久化存储，服务也没法 24/7 稳定运行。

结论很直接：继续在模拟器上迭代解决不了根本问题，模拟环境本身就不该是生产路径。于是启动了这个仓库，把 KMS 从 Docker/QEMU 模拟迁移到 STM32MP157F-DK2 真实硬件——用真正的 ARM TrustZone 安全区、真正的 eMMC/RPMB 持久化存储，目标是搭一条能撑住断电、能长期运行、未来能做去中心化部署的硬件路径。

## 为什么是这块板子

STM32MP157F-DK2 是意法半导体（STMicroelectronics）的一块开发板：ARM Cortex-A7 双核主频跑 Linux，配一个独立的 Cortex-M4 协处理器，官方 BSP 自带 OP-TEE（Open Portable Trusted Execution Environment）支持，也就是说 TrustZone 安全世界/普通世界的隔离是硬件级的，不是软件模拟出来的。密钥可以真正存进安全存储，断电也不会凭空消失。

## 这两周半实际做了什么

这个仓库从 2025 年 11 月 16 日建仓到 12 月 3 日最后一次提交，一共 20 次提交，活跃期集中在两个时间段：11 月 16 日当天写完了 README 骨架，隔了两周多，12 月 2-3 日集中补齐了真正有分量的文档——环境搭建脚本、Mac 连接开发板的排障记录、USB 键盘快速上手指南，以及把所有文档转成中英双语。

老实说清楚这个仓库当前的真实状态：**这一阶段做的是环境搭建和踩坑记录，不是已经写完的 KMS 硬件实现**——真正的密钥管理 Trusted Application（TA）代码、host 端 API，仓库里明确标成"计划中"，还没有写。这篇笔记记录的是"把开发环境和连接方式跑通"这一步，不是"KMS 已经在硬件上跑起来了"。

### 交叉编译环境：一个脚本装齐整套工具链

`scripts/setup-ubuntu-dev-env.sh` 是这一阶段最实在的产出，一个脚本把 Ubuntu/Debian 开发机需要的东西装齐：

- ARM 交叉编译工具链：`gcc-arm-linux-gnueabihf`/`g++-arm-linux-gnueabihf`/`binutils-arm-linux-gnueabihf`，装完用 `arm-linux-gnueabihf-gcc --version` 验证
- Yocto 构建依赖（跑 OP-TEE 官方构建系统需要）：`gawk`、`diffstat`、`texinfo`、`chrpath`、`socat`、`python3-pexpect`、`python3-jinja2` 等一长串
- 串口工具：`minicom`/`screen`/`picocom`/`cu`，并把当前用户加进 `dialout` 组（不加组，串口设备权限会拒绝访问）
- 网络工具 + NFS/TFTP 服务端（板子通过网络启动/挂载根文件系统时要用）：建 `/srv/nfs/stm32mp1`，配 `/etc/exports`、`/srv/tftp`
- 调试工具：`gdb-multiarch`、`gdbserver`、`openocd`、`stlink-tools`
- 一份 udev 规则 `/etc/udev/rules.d/49-stlinkv2.rules`，写死了 ST-LINK/V2、V2-1、V3 以及 STM32MP1 DFU 模式的 USB vendor/product ID（vendor `0483`，product `3748`/`374b`/`374d-f`/`3753`/`df11`）——没有这份规则，Linux 主机插上 ST-LINK 调试器很可能因为权限问题连不上

### Mac 用户的真实坑：ST-LINK 串口在 macOS 上根本不出现

`docs/troubleshooting-mac-connection.md` 记的是一个真实踩过的坑：在 Mac 上插上 ST-LINK，`ls /dev/tty.usbmodem*` 直接"no matches found"，设备根本没出现。根因是 macOS（尤其 Apple Silicon、Monterey 及之后版本）对 ST-LINK 这类 USB-serial 设备的驱动支持本来就有限，不是权限问题，装驱动、加 sudo 都解决不了。

这份文档给出的实用解法是**放弃跟串口较劲，走网络连接**：

- 方案一：直接在板子自带的 LCD 触摸屏（Weston 桌面）上用 `nmcli`/`nmtui` 配好 WiFi，之后完全通过网络 SSH/VNC（`wayvnc`/`x11vnc`）进板子，不再需要串口线
- 方案二：接网线，用 `nmap`/`arp -a` 在局域网里找到板子分到的 IP，直接 SSH
- 方案三：真要修 ST-LINK USB 问题，检查 `brew list stlink`/`libusb`、`system_profiler SPUSBDataType`、固件版本和 macOS 权限设置逐项排查
- 方案四：开 Mac 的网络共享（Internet Sharing），把板子直接接在 Mac 提供的网段里

推荐的开发流程因此也跟着调整：Mac 用户不再走"本地交叉编译→烧录"这条路，而是直接 SSH/VNC 进板子，把 AirAccount 仓库克隆到板子本地、在板子上跑 `make` 直接编译——绕开了 Mac 上 USB/串口这条最容易出问题的链路。

### 架构：从模拟器到硬件，服务分层没有变

迁移过程中重新画过一次架构图：客户端层（CLI/WebApp/SDK）→ API 网关（Cloudflare Tunnel + 负载均衡）→ KMS 服务层（KMS API Server :8080，AWS 兼容接口，健康监控）→ 核心逻辑层（KMS Core 加密逻辑、协议定义）→ TEE 层（KMS Host → Trusted Application → 安全存储）。这条分层本身在模拟器和真实硬件上是一致的——迁移改变的是最底下 TEE 层的实现介质，从"QEMU 模拟出来的假 TrustZone"换成"STM32MP157F-DK2 真实的 TrustZone 安全区"，上层服务逻辑不需要重写。

### 三阶段路线图

`ROADMAP.md` 定了三个阶段：

1. **Phase 1（2-3 个月，当前阶段）**：硬件采购、开发环境搭建、OP-TEE 开发（从 Hello World TA 起步，逐步移植 KMS TA、实现密钥生成/签名、验证 RPMB/eMMC 安全存储断电不丢数据）、集成与性能测试（目标 >50 TPS）。
2. **Phase 2（2-3 个月）**：工业级硬件选型（初步推荐 Phytec phyBOARD-Sargas，目标单节点成本控制在 500 美元以内）、软件迁移、生产环境单节点部署，配 Prometheus/Grafana 监控。
3. **Phase 3（6-9 个月）**：清迈社区去中心化实验——3-5 个节点，用 Shamir/TSS 做密钥分片，WireGuard 打通节点间网络，治理代币/智能合约部署在 Ethereum/Polygon，招募 10-50 个社区用户做真实测试，第三方安全审计，公开发布。

预算表里给出的硬件预估：2 块 STM32MP157F-DK2（每块约 100 美元）+ 5 块 Phytec phyBOARD-Sargas（每块约 300 美元）等，硬件总计约 2,800 美元，加上年运营预算约 8,400 美元，总计约 12,200 美元——这是一个刻意压缩成本、面向社区可复制的预算规模，不是企业级采购量级。

## 现在的真实状态

补记这篇笔记的时候需要说清楚：这仓库这一阶段的产出是环境和文档，不是可运行的硬件 KMS。真正有价值、后续值得回头看的是两件事——一是 `setup-ubuntu-dev-env.sh` 这个一次装齐交叉编译+调试工具链的脚本，二是"macOS 连 ST-LINK 大概率连不上、走网络反而更稳"这条踩坑经验，这条对任何在 Mac 上折腾 STM32MP1 系列板子的人都通用，不是这个项目独有的坑。

相关项目：AirAccount KMS（github.com/AAStarCommunity/AirAccount，`KMS` 分支）；这套迁移工作也在 ETHGlobal 伊斯坦布尔黑客松上做过展示（ethglobal.com/showcase/airaccount-swqix）。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **When**: November-December 2025
> **Author**: Jason (AAstar)
> **Hardware**: STM32MP157F-DK2 (dual-core ARM Cortex-A7 + Cortex-M4, OP-TEE/TrustZone)
> **Repo**: github.com/jhfnetboy/STM32MP157F-DK2

## The trigger: losing private keys in a simulator

AirAccount KMS (Key Management Service) was running on a Mac mini M4 at CMU ICDI, using Docker/QEMU to simulate an OP-TEE TrustZone environment. That simulation setup had a real incident: after a power failure, Key IDs and already-generated private keys were simply gone — the emulated environment never provided real persistent storage, and the service couldn't stay up 24/7 either.

The conclusion was direct: continuing to iterate on top of a simulator wasn't going to fix the underlying problem — the simulated environment itself was never a viable production path. This repo was started to migrate the KMS off Docker/QEMU emulation and onto real STM32MP157F-DK2 hardware — a genuine ARM TrustZone secure world, genuine eMMC/RPMB persistent storage, aiming for a hardware path that survives power loss, runs long-term, and can eventually support decentralized deployment.

## Why this board

The STM32MP157F-DK2 is an STMicroelectronics development board: a dual-core ARM Cortex-A7 running Linux, paired with an independent Cortex-M4 coprocessor, with official BSP support for OP-TEE (Open Portable Trusted Execution Environment) — meaning the isolation between the TrustZone secure world and the normal world is hardware-enforced, not software-simulated. Keys can actually live in secure storage and survive a power failure instead of vanishing.

## What actually got done in these two and a half weeks

This repo went from its first commit on November 16, 2025 to its last on December 3, 2025 — 20 commits total, concentrated into two bursts: the README skeleton got written on November 16 itself, then after a gap of over two weeks, December 2-3 saw the bulk of the substantive documentation — the environment setup script, the Mac-connection troubleshooting notes, the USB-keyboard quick-start guide, and converting everything to bilingual EN/CN.

Being honest about where this repo actually stands: **this phase was environment setup and troubleshooting notes, not a finished KMS hardware implementation.** The actual key-management Trusted Application (TA) code and host-side API are explicitly marked "coming" in the repo — they haven't been written yet. This note documents getting the dev environment and connection method working, not "the KMS is already running on hardware."

### Cross-compile toolchain: one script to set up the whole stack

`scripts/setup-ubuntu-dev-env.sh` is the most concrete output from this phase — a single script that installs everything an Ubuntu/Debian dev machine needs:

- ARM cross-compilation toolchain: `gcc-arm-linux-gnueabihf`/`g++-arm-linux-gnueabihf`/`binutils-arm-linux-gnueabihf`, verified afterward with `arm-linux-gnueabihf-gcc --version`
- Yocto build dependencies (needed to run OP-TEE's official build system): a long list including `gawk`, `diffstat`, `texinfo`, `chrpath`, `socat`, `python3-pexpect`, `python3-jinja2`
- Serial tools: `minicom`/`screen`/`picocom`/`cu`, plus adding the current user to the `dialout` group — skip that group and serial-device permissions get denied
- Networking tools plus an NFS/TFTP server (needed when the board network-boots or mounts its rootfs over the network): creates `/srv/nfs/stm32mp1`, configures `/etc/exports` and `/srv/tftp`
- Debug tools: `gdb-multiarch`, `gdbserver`, `openocd`, `stlink-tools`
- A udev rules file, `/etc/udev/rules.d/49-stlinkv2.rules`, hardcoding the USB vendor/product IDs for ST-LINK/V2, V2-1, V3, and STM32MP1 DFU mode (vendor `0483`, products `3748`/`374b`/`374d-f`/`3753`/`df11`) — without this rule, a Linux host plugging in an ST-LINK debugger is very likely to fail with a permissions error

### The real Mac problem: the ST-LINK serial port never shows up on macOS

`docs/troubleshooting-mac-connection.md` documents a genuine issue hit along the way: plugging an ST-LINK into a Mac and running `ls /dev/tty.usbmodem*` returned "no matches found" — the device simply never appeared. The root cause is that macOS (especially Apple Silicon, Monterey and later) has inherently limited driver support for ST-LINK-style USB-serial devices — it's not a permissions problem, and installing drivers or adding `sudo` doesn't fix it.

The practical fix this doc lands on is **giving up on fighting the serial connection and going over the network instead**:

- Option 1: configure WiFi directly on the board's own LCD touchscreen (Weston desktop) using `nmcli`/`nmtui`, then do everything over network SSH/VNC (`wayvnc`/`x11vnc`) — no serial cable needed at all
- Option 2: plug in Ethernet, use `nmap`/`arp -a` to find the board's IP on the local network, and SSH in directly
- Option 3: if you actually need to fix the ST-LINK USB issue, check `brew list stlink`/`libusb`, `system_profiler SPUSBDataType`, firmware version, and macOS permission settings one by one
- Option 4: turn on Mac Internet Sharing and put the board directly on the network segment the Mac provides

The recommended dev workflow shifted accordingly: Mac users stopped trying to cross-compile locally and flash, and instead SSH/VNC directly into the board, clone the AirAccount repo onto the board itself, and run `make` right there — sidestepping the USB/serial link that was the most failure-prone part of the whole chain.

### Architecture: same service layers, different TEE substrate

The architecture got redrawn during the migration: Client Layer (CLI/WebApp/SDK) → API Gateway (Cloudflare Tunnel + load balancing) → KMS Service Layer (KMS API Server on :8080, AWS-compatible interface, health monitoring) → Core Logic Layer (KMS Core crypto logic, protocol definitions) → TEE Layer (KMS Host → Trusted Application → secure storage). This layering is the same on the simulator and on real hardware — what the migration actually changes is the implementation medium at the bottom TEE layer, swapping "QEMU-simulated fake TrustZone" for "STM32MP157F-DK2's genuine TrustZone secure world," without needing to rewrite the layers above it.

### The three-phase roadmap

`ROADMAP.md` lays out three phases:

1. **Phase 1 (2-3 months, current)**: hardware procurement, dev-environment setup, OP-TEE development (starting from a Hello World TA, then porting the KMS TA, implementing key generation/signing, verifying RPMB/eMMC secure storage survives power loss), integration and performance testing (targeting >50 TPS).
2. **Phase 2 (2-3 months)**: industrial hardware selection (Phytec phyBOARD-Sargas is the current recommendation, targeting under $500 per node), software migration, single-node production deployment with Prometheus/Grafana monitoring.
3. **Phase 3 (6-9 months)**: the Chiang Mai decentralization experiment — 3-5 nodes, Shamir/TSS key sharding, WireGuard mesh networking between nodes, governance tokens/smart contracts on Ethereum/Polygon, recruiting 10-50 real community users for testing, third-party security audit, public launch.

The budget table estimates hardware costs: 2x STM32MP157F-DK2 (~$100 each) plus 5x Phytec phyBOARD-Sargas (~$300 each) and similar, roughly $2,800 in hardware, plus about $8,400/year in operating budget, totaling roughly $12,200 — a deliberately compressed, community-replicable scale, not enterprise procurement.

## Where things actually stand now

Backfilling this note, it's worth being clear: this phase's output was environment and documentation, not a running hardware KMS. The two things genuinely worth carrying forward are the `setup-ubuntu-dev-env.sh` script that sets up the full cross-compile/debug toolchain in one pass, and the lesson that "ST-LINK on macOS will probably fail to connect, and going over the network is more reliable anyway" — a piece of experience that applies to anyone wrestling with an STM32MP1-family board on a Mac, not something specific to this project.

Related project: AirAccount KMS (github.com/AAStarCommunity/AirAccount, `KMS` branch); this migration work was also showcased at the ETHGlobal Istanbul hackathon (ethglobal.com/showcase/airaccount-swqix).

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
