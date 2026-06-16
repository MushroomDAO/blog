---
title: "Apple 官方容器工具来了：一个容器一个 VM，Mac 本地开发的底层能力正在重写"
description: "Apple 正式开源了 container——一个用 Swift 写的原生 Linux 容器运行时，不依赖 Docker Desktop，直接调用 Apple Silicon 硬件虚拟化，每个容器拥有独立 Linux 内核。37k stars，v1.0.0 已发布。这篇文章带你看它的核心设计、和 Docker 的本质差异、以及现在值不值得用。"
titleEn: "Apple's Native Container Tool: One VM Per Container, Mac Local Dev Is Being Rewritten at the Foundation"
descriptionEn: "Apple open-sourced 'container' — a native Linux container runtime written in Swift, no Docker Desktop needed, runs directly on Apple Silicon hardware virtualization with one independent Linux kernel per container. 37k stars, v1.0.0 released. This article covers the core design, fundamental differences from Docker, and whether it's worth using now."
pubDate: 2026-06-15
category: "Tech-News"
tags: ["Apple", "Container", "Docker", "AppleSilicon", "macOS", "Linux", "开发工具", "虚拟化", "开源"]
lang: "zh-CN"
heroImage: "../../assets/images/apple-container-native-linux-vm-guide.png"
---

> 2026-06-15 · 技术观察

2026 年 6 月，Apple 在 GitHub 上悄悄推送了一个仓库：[apple/container](https://github.com/apple/container)。

没有发布会，没有 WWDC 主题演讲，就这么出现了。两周内收获 37,000+ stars，成为近期最受关注的开发工具开源项目之一。

---

## 它是什么

`container` 是 Apple 官方的**原生 Linux 容器运行时**。

一句话：在 Mac 上运行 Linux 容器，不需要安装 Docker Desktop。

它直接调用 macOS 的 Virtualization.framework（Apple 自家的虚拟化框架），用 Swift 编写（代码库 98% 是 Swift），完全兼容 OCI 标准容器镜像——你现有的 Docker 镜像可以直接用。

```bash
# 拉取镜像（和 docker pull 完全一样的镜像）
container pull ubuntu:latest

# 运行容器
container run -it ubuntu:latest bash

# 构建镜像
container build -t myapp:1.0 .
```

---

## 最核心的设计：一个容器一个 VM

这是 `container` 和 Docker Desktop 最本质的差异，值得认真理解。

**Docker Desktop 的模型**：

```
Mac
  └── 一个共享的 Linux VM
          ├── 容器 A
          ├── 容器 B
          └── 容器 C
              (共享同一个 Linux kernel)
```

所有容器跑在同一个 VM 里，共享一个 Linux 内核。这在 Linux 上是正常的——因为主机本身就是 Linux；但在 Mac 上，这意味着先跑一个"翻译层 VM"，所有容器再在其中叠加。

**Apple container 的模型**：

```
Mac (Apple Silicon · Virtualization.framework)
  ├── 容器 A → 独立 VM（独立 Linux kernel）
  ├── 容器 B → 独立 VM（独立 Linux kernel）
  └── 容器 C → 独立 VM（独立 Linux kernel）
```

每个容器有自己的轻量级 Linux 内核，完全隔离。容器 A 的内核崩溃了，不影响容器 B 和 C。

这种设计在业界叫 **microVM 架构**，AWS 的 Firecracker（Lambda 背后的技术）也是类似思路。Apple 把它带到了 Mac 本地开发环境。

**隔离性提升的实际意义**：
- 一个容器的进程无法感知另一个容器的存在（内核级别的隔离，不只是 namespace 级别）
- 适合需要严格安全边界的开发场景，比如在本地跑不信任的依赖或测试沙箱
- 容器之间的资源竞争更可预测

---

## 性能表现

社区基准测试的结论让人有点意外——在 Apple Silicon 上，`container` 的性能**超过了 Docker Desktop**：

| 指标 | Apple container | Docker Desktop |
|------|:---:|:---:|
| CPU 吞吐量 | ↑ 超过 | 基准 |
| 内存吞吐量 | ↑ 超过 | 基准 |
| 镜像拉取速度 | 相近 | 相近 |
| 启动时间 | 需启动独立 VM | VM 已常驻 |

性能优势来自 Virtualization.framework 对 Apple Silicon 硬件虚拟化扩展的直接调用，没有额外的翻译层。

启动时间方面，每个容器需要启动一个轻量级 VM，比 Docker Desktop（VM 已常驻）的容器启动慢一些，但 Apple 对这个 VM 做了专门优化，实际体验比你想象的快。

---

## 和其他工具的比较

| 工具 | 类型 | Mac 性能 | 隔离强度 | 生态成熟度 |
|------|------|---------|---------|----------|
| **Apple container** | 官方原生 | 最优 | 最强（VM级） | 较新 |
| **Docker Desktop** | 跨平台 | 一般 | 中（共享VM） | 最成熟 |
| **OrbStack** | 商业 | 很好 | 中 | 成熟 |
| **Colima** | 开源社区 | 好 | 中 | 较成熟 |
| **Podman** | Red Hat 开源 | 有限 | 中 | Linux 强 |

OrbStack 目前在轻量化和易用性上仍是很强的竞品，且不需要 macOS 26。

---

## 跨架构：Rosetta 2 直接用上

如果你在 Apple Silicon 上需要运行 `linux/amd64` 的容器（比如很多生产环境还在 x86），`container` 内置了 Rosetta 2 支持——x86_64 的 Linux 二进制在 ARM VM 里通过 Rosetta 翻译执行，透明无感。

这对跨架构调试和 CI 场景很有用。

---

## 硬性门槛

在你决定试用之前，有两个硬性要求必须满足：

1. **Apple Silicon Mac**（M1/M2/M3/M4）：不支持 Intel Mac，没有例外
2. **macOS 26（Tahoe）或更高版本**：依赖 Virtualization.framework 的新 API，无法向下兼容

macOS 26 目前（2026-06）还比较新。如果你的 Mac 还没升级，或者团队有 Intel Mac 用户，现在切换会有问题。

---

## 不做什么的说明

Apple `container` **不包含**：
- Docker Compose（需要单独适配）
- Kubernetes 本地集群（如 minikube/kind）
- 图形界面（纯 CLI）
- Windows/Linux 支持（仅 macOS）

它是一个**底层运行时**，不是完整的开发工具链。把它理解为"Mac 上的 containerd/runc 等价物"更准确。

---

## 我的判断

它短期内更像一个**值得技术团队试验和观察的基础设施项目**，而不是所有开发者立刻切换的默认工具。

macOS 26 的要求卡住了大多数当前用户。生态工具（Compose、GUI、IDE 插件）还需要时间跟上。Docker Desktop 和 OrbStack 的存量用户体验仍然更完整。

但它已经传递出一个强信号：**Apple Silicon 时代，Mac 本地开发环境的底层能力正在被重新整理**。

- Apple 自己的虚拟化框架比任何第三方实现都更贴近硬件
- "一VM一容器"的隔离模型在安全性上是真实提升
- 官方维护意味着长期迭代有保证，不依赖社区活跃度

**如果你是以下开发者，这个项目值得认真看一眼**：

- 开发工具、平台工程、DevOps 方向
- AI 模型本地运行环境（需要隔离但高性能的容器）
- macOS 原生工具链开发者
- 关注容器安全边界的场景

不是因为它一定会替代谁，而是因为它展示了 **Mac 容器体验可能走向哪里**。

---

## 快速上手

**前提**：Apple Silicon Mac + macOS 26+

从 [GitHub Releases](https://github.com/apple/container/releases) 下载签名安装包，双击安装后：

```bash
# 启动服务
container system start

# 验证安装
container version

# 跑一个 Ubuntu 容器试试
container run -it ubuntu:latest bash

# 用完停止服务，释放资源
container system stop
```

命令风格和 Docker 高度相似，上手成本极低。

---

**项目地址**：[github.com/apple/container](https://github.com/apple/container)  
**许可证**：Apache 2.0 · **语言**：Swift 98% · **版本**：v1.0.0（2026-06-09）

<!--EN-->

## Apple's Native Container Tool: One VM Per Container

Apple quietly open-sourced `container` on GitHub — a native Linux container runtime for Mac, written in Swift, requiring no Docker Desktop. 37k+ stars in two weeks.

### The Core Design: One Container = One VM

Docker Desktop runs all containers inside a single shared Linux VM. Apple container gives each container its own lightweight Linux VM with an independent kernel.

```
Apple container model:
Mac (Apple Silicon · Virtualization.framework)
  ├── Container A → independent VM (independent Linux kernel)
  ├── Container B → independent VM (independent Linux kernel)
  └── Container C → independent VM (independent Linux kernel)
```

This is microVM architecture — the same concept behind AWS Firecracker — brought to Mac local dev.

### Performance

Community benchmarks show `container` outperforms Docker Desktop on Apple Silicon in CPU and memory throughput, thanks to direct hardware virtualization via Virtualization.framework. Container startup is slightly slower (each container boots a VM), but Apple has heavily optimized the boot path.

### Hard Requirements

- **Apple Silicon Mac only** (no Intel Mac support)
- **macOS 26 (Tahoe) or later** (no backwards compatibility)

### What It Doesn't Include

No Docker Compose, no Kubernetes, no GUI — it's a low-level container runtime, equivalent to containerd/runc for Mac.

### My Take

Short-term, it's an infrastructure project worth experimenting with, not an immediate default switch for all developers. macOS 26 requirement blocks most current users, and the tooling ecosystem needs time to catch up.

But the signal is clear: **Apple Silicon era Mac dev tooling is being rewritten at the foundation.** Apple's own virtualization framework will always have hardware advantages no third party can match.

Worth watching seriously if you work on dev tools, platform engineering, local AI runtimes, DevOps, or macOS-native tooling.

**Project**: [github.com/apple/container](https://github.com/apple/container) · Apache 2.0 · v1.0.0
