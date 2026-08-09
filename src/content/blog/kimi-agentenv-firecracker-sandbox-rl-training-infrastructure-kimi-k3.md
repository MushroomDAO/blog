---
title: "Kimi AgentENV：驱动 Kimi K3 RL 训练的 Firecracker 沙箱基础设施深度拆解"
titleEn: "Kimi AgentENV: Inside the Firecracker Sandbox Infrastructure Powering Kimi K3's RL Training"
description: "kvcache-ai 开源的 AgentENV（AENV）是 Kimi K3 Agentic RL 训练的底层沙箱平台，基于 Firecracker microVM + overlaybd + ublk，实现 50ms 启动/恢复、100ms 快照和运行时 Fork，并提供 E2B 兼容 API。MIT 开源，Rust 实现，可自托管替代 E2B。"
pubDate: "2026-07-28"
category: "Research"
heroImage: "../../assets/images/kimi-agentenv-firecracker-sandbox-rl-training-infrastructure-kimi-k3-banner.jpg"
---

Kimi K3 的 Agentic RL 训练，需要同时跑大量 Agent 执行环境——代码解释器、工具调用沙箱、终端环境。

每个 RL rollout 需要一个隔离的 Linux 环境。并行度越高，训练效率越高。但每个环境都是完整的 VM，冷启动慢、闲置贵、扩展难。

AgentENV（AENV）是 Kimi 团队为解决这个问题而构建的基础设施，2026 年 7 月 23 日开源，MIT 授权，Rust 实现。

---

## 一、AgentENV 解决的问题

传统的 Agent 沙箱方案面临三个根本矛盾：

**冷启动慢 vs. 任务到来突发**：RL 训练的 rollout 以批为单位到来，需要瞬间拉起大量环境。完整 VM 冷启动几秒乃至几十秒，严重影响吞吐。

**闲置贵 vs. 利用率波动**：RL 训练中，环境并非持续繁忙。等模型推理、等工具返回结果的时间，环境在空等，但仍然占着 CPU 和内存。

**镜像大 vs. 节点多**：不同 Agent 任务需要不同的基础镜像（Python 版本、工具链、数据集），每个节点都预先 pull 一套不现实，按需加载才能扩展。

AgentENV 用四个核心机制回应这四个问题：

---

## 二、技术架构：四层设计

### 1. Firecracker microVM——内核级隔离

每个沙箱是一个独立的 Firecracker microVM，拥有完整的 Linux 内核。

相比 Docker/gVisor，Firecracker 提供更强的安全边界（独立内核，非共享 syscall 过滤），同时比完整 VM 更轻量（无固件、无模拟设备总线）。

RL 训练场景里，每个沙箱都会执行来自模型的任意代码。Firecracker 的内核级隔离在这里不是可选的，是必须的。

### 2. overlaybd——按需加载的分层镜像

overlaybd 是一种基于 **LSMT（Log Structured Merge Tree）** 的分层块设备格式：

```
┌─────────────────────────────┐
│ upper layer (r/w, 当前修改) │
├─────────────────────────────┤
│ layer N (r/o, OCI 镜像层)   │
│ ...                         │
│ layer 0 (r/o, 基础层)       │
└─────────────────────────────┘
```

关键特性：

- **按需加载**：本地磁盘作为有界缓存，冷数据淘汰，热数据保留。镜像可以超过单节点磁盘容量，不需要预先 pull 到每台机器
- **CoW（Copy-on-Write）**：多个沙箱共享同一组只读基础层，只有各自的修改（upper layer）独立存储
- **快照**：`snapshot_runtime()` 通过 reflink（支持 CoW 的文件系统上的零拷贝）将 upper layer 持久化

读路径：从上往下搜索各层的 segment index，第一个包含目标块范围的层提供数据。

### 3. ublk——零拷贝用户态块设备

ublk 是 AgentENV 的 I/O 层，基于 Linux 内核的 ublk 驱动，在用户态实现块设备：

```
Firecracker VM
    /dev/vda (rootfs)
    /dev/vdb (extra)
         ↓
    /dev/ublkbN (ublk 块设备)
         ↓
    overlaybd 层叠镜像
         ↓
    io_uring (async I/O)
```

ublk 通过 io_uring 异步处理所有 I/O，在内核 6.8+ 上使用 sparse buffer table 实现零拷贝（`AutoRegBuffer`）。存储数据和内存快照数据共享宿主机的 page cache，避免重复缓存。

单独的 `uvm-ublk-daemon` 进程管理所有 ublk 设备，通过 Unix domain socket 与主进程通信。这种分离让 ublk 设备的所有权和 io_uring 控制集中在专用进程里，主服务则专注于生命周期管理。

### 4. 快照与 Fork——并行 rollout 的核心

这是 AgentENV 在 RL 训练场景下最关键的设计。

**快照**：
- 对内存和文件系统变更做增量快照
- <100ms 完成，即使沙箱正在进行大量磁盘写入
- 持久化到 S3 兼容对象存储或共享分布式文件系统

**从快照启动/恢复**：
- <50ms 启动或恢复一个沙箱
- 冷启动即快照恢复，不是从零初始化

**Fork**：
- 一个正在运行的沙箱可以 Fork 出多个独立沙箱
- 这是 RL 训练中非常有价值的特性：**在同一个任务中途点，让不同的模型策略并行探索不同的执行路径**

**暂停/恢复**：
- 暂停 <100ms
- 闲置环境快速释放 CPU 和内存（Memory Ballooning 将可回收的 guest 内存还给宿主机）
- 有新任务到来时快速恢复

---

## 三、系统整体架构

```
┌───────────────────────────────────────────────────────────┐
│                    AgentENV Node                          │
│                                                           │
│  ┌──────────┐   ┌──────────────┐                          │
│  │ API      │──>│ Orchestrator │                          │
│  │ (Axum)   │   │ (lifecycle)  │                          │
│  └──────────┘   └──────┬───────┘                          │
│                        │                                  │
│              ┌─────────▼───────────┐                      │
│              │  Firecracker VM     │                      │
│              │  /dev/vda (rootfs)  │                      │
│              │  /dev/vdb (extra)   │                      │
│              └─────────────────────┘                      │
│                         ↓                                 │
│              ┌──────────────────────┐                     │
│              │  ublk + overlaybd    │                     │
│              │  (分层块设备 + 快照)  │                     │
│              └──────────────────────┘                     │
└───────────────────────────────────────────────────────────┘
                         ↕
        ┌──────────────────────────────────┐
        │  Distributed Control Plane       │
        │  (gateway + scheduler, prototype) │
        └──────────────────────────────────┘
```

多节点部署支持 Kubernetes，通过 Gateway + Scheduler 做跨节点路由（当前是 prototype 状态）。节点间快照分发走 P2P 传输协议。

---

## 四、E2B 兼容 API

AgentENV 暴露的 HTTP API 与 [E2B](https://e2b.dev) 完全兼容。

这意味着：已有的、基于 E2B SDK 的代码**不需要任何修改**，只需要换一个环境变量：

```bash
export E2B_API_URL=http://your-aenv-server:8000
```

然后正常用 E2B 的 Python / TypeScript SDK 即可。

```python
from e2b_code_interpreter import Sandbox

# 指向 AgentENV，不用改其他任何代码
sandbox = Sandbox()
execution = sandbox.run_code("print('hello from AgentENV')")
print(execution.text)
```

对于已经在用 E2B 跑 Agent 代码执行的团队，这条迁移路径几乎无摩擦。

---

## 五、快速上手

单节点部署（需要 Linux kernel 6.8+，`/dev/kvm` 访问权限）：

```bash
# Ubuntu 24.04 install script
curl -fsSL https://raw.githubusercontent.com/kvcache-ai/AgentENV/main/scripts/install.sh | sudo bash
sudo systemctl start aenv

# 或者 Docker
docker pull ghcr.io/kvcache-ai/aenv-server:latest
docker run -d --privileged -v /dev:/dev -p 8000:8000 ghcr.io/kvcache-ai/aenv-server:latest
```

基本使用：

```bash
# 认证
aenv auth  # server URL: http://127.0.0.1:8000, API key: dummy

# 拉取模板并启动沙箱
aenv pull ubuntu:22.04 --name ubuntu
aenv start ubuntu          # 启动并进入交互式 shell
aenv start ubuntu --detach # 后台启动，输出 sandbox ID

# 管理
aenv pause <sandbox-id>
aenv resume <sandbox-id>
aenv timeout <sandbox-id> 600  # 延长 TTL
aenv delete <sandbox-id>
```

---

## 六、技术判断

AgentENV 公开了一个在 AI 基础设施层面很重要的工程选择：**把 RL 训练环境的沙箱设计，从"服务"模式改成"状态机 + 快照"模式。**

传统思路是：每个 rollout 起一个新的容器，跑完销毁。慢，浪费。

AgentENV 的思路是：环境是一个可以快速序列化/反序列化的状态机。快照 = 检查点。Fork = 从检查点分叉出并行探索。暂停 = 让出资源但不销毁状态。

这个设计和 RL 训练的特点高度契合：
- 很多 rollout 从相同的初始状态开始（Fork 比重新创建便宜 100x）
- 中途的"任务节点"可以被多个后续策略共享（快照复用）
- GPU 利用率波动时，环境可以被暂停而不销毁（Memory Ballooning 释放资源）

更重要的是：开源后，任何需要大规模 Agent 执行环境的团队——无论是做 RL 训练还是做 Agent 产品——都可以直接在自己的基础设施上跑一套。E2B 兼容的 API 把迁移成本降到了最低。

> 项目：github.com/kvcache-ai/AgentENV（898 ⭐，MIT）  
> 文档：kvcache-ai.github.io/AgentENV  
> 语言：Rust  
> 需求：Linux kernel 6.8+，/dev/kvm  
> 许可：MIT License

<!--EN-->

## Kimi AgentENV: Deep Dive into the Firecracker Sandbox Infrastructure Behind Kimi K3 RL Training

Kimi K3's Agentic RL training needs to run large numbers of agent execution environments simultaneously — code interpreters, tool-call sandboxes, terminal environments.

Each RL rollout requires an isolated Linux environment. The higher the parallelism, the higher the training efficiency. But each environment is a full VM — slow cold start, expensive idle, hard to scale.

AgentENV (AENV) is the infrastructure Kimi's team built to solve this problem, open-sourced July 23, 2026, MIT licensed, written in Rust.

---

## The Problem AgentENV Solves

Traditional agent sandbox approaches face three fundamental tensions:

**Slow cold start vs. bursty task arrival**: RL training rollouts arrive in batches, requiring sudden environment bursts. Full VM cold starts take seconds to tens of seconds, severely impacting throughput.

**Expensive idle vs. fluctuating utilization**: In RL training, environments aren't continuously busy. While waiting for model inference or tool results, environments sit idle but still hold CPU and memory.

**Large images vs. many nodes**: Different agent tasks need different base images (Python versions, toolchains, datasets). Pre-pulling a complete set to every node isn't feasible; on-demand loading is the only path to scale.

AgentENV responds to these with four core mechanisms:

---

## Technical Architecture: Four Layers

### 1. Firecracker microVM — Kernel-Level Isolation

Each sandbox is an independent Firecracker microVM with its own full Linux kernel.

Compared to Docker/gVisor, Firecracker provides stronger security boundaries (independent kernel, not shared syscall filters), while being more lightweight than full VMs (no firmware, no device bus emulation).

In RL training scenarios, each sandbox executes arbitrary code from the model. Firecracker's kernel-level isolation isn't optional here — it's required.

### 2. overlaybd — On-Demand Layered Images

overlaybd is an **LSMT (Log Structured Merge Tree)**-based layered block device format:

```
┌─────────────────────────────┐
│ upper layer (r/w, current)  │
├─────────────────────────────┤
│ layer N (r/o, OCI image)    │
│ ...                         │
│ layer 0 (r/o, base layer)   │
└─────────────────────────────┘
```

Key features:
- **On-demand loading**: local disk acts as a bounded cache, evicting cold, retaining hot. Images can exceed single-node disk capacity without pre-pulling to every machine
- **Copy-on-Write**: multiple sandboxes share the same read-only base layers; only each sandbox's modifications (upper layer) are stored independently
- **Snapshots**: `snapshot_runtime()` persists the upper layer via reflink (zero-copy on CoW-supporting filesystems)

Read path: search each layer's segment index top-down; the first layer containing a mapping for the requested block range serves the data.

### 3. ublk — Zero-Copy Userspace Block Device

ublk is AgentENV's I/O layer, implementing block devices in userspace via Linux's ublk kernel driver:

```
Firecracker VM
    /dev/vda (rootfs)
    /dev/vdb (extra)
         ↓
    /dev/ublkbN (ublk block device)
         ↓
    overlaybd layered image
         ↓
    io_uring (async I/O)
```

ublk handles all I/O asynchronously through io_uring, achieving zero-copy on kernel 6.8+ via sparse buffer tables (`AutoRegBuffer`). Storage data and memory-snapshot data share the host's page cache, avoiding duplicate caching.

A dedicated `uvm-ublk-daemon` process manages all ublk devices, communicating with the main process via Unix domain socket. This separation keeps ublk device ownership and io_uring control in a dedicated process while the main service focuses on lifecycle management.

### 4. Snapshots and Fork — Core for Parallel Rollouts

This is AgentENV's most critical design for RL training scenarios.

**Snapshots**:
- Incremental snapshots of memory and filesystem changes
- Completes in <100ms even under heavy disk modification
- Persisted to S3-compatible object storage or shared distributed filesystem

**Boot/resume from snapshot**:
- <50ms to start or resume a sandbox
- Cold start = snapshot restore, not zero-initialization

**Fork**:
- A running sandbox can fork into multiple independent sandboxes
- Extremely valuable for RL training: **at a mid-task checkpoint, let different model policies explore different execution paths in parallel**

**Pause/resume**:
- Pause in <100ms
- Idle environments quickly release CPU and memory (Memory Ballooning returns reclaimable guest memory to host)
- Fast resume when new work arrives

---

## The E2B-Compatible API

AgentENV's HTTP API is fully compatible with [E2B](https://e2b.dev).

This means existing E2B SDK-based code **requires zero modification** — just change one environment variable:

```bash
export E2B_API_URL=http://your-aenv-server:8000
```

Then use the standard E2B Python/TypeScript SDK normally:

```python
from e2b_code_interpreter import Sandbox

# Points to AgentENV, nothing else changes
sandbox = Sandbox()
execution = sandbox.run_code("print('hello from AgentENV')")
print(execution.text)
```

For teams already using E2B for agent code execution, this migration path has near-zero friction.

---

## Quick Start

Single-node deployment (requires Linux kernel 6.8+, `/dev/kvm` access):

```bash
# Ubuntu 24.04 install script
curl -fsSL https://raw.githubusercontent.com/kvcache-ai/AgentENV/main/scripts/install.sh | sudo bash
sudo systemctl start aenv

# Or Docker
docker pull ghcr.io/kvcache-ai/aenv-server:latest
docker run -d --privileged -v /dev:/dev -p 8000:8000 ghcr.io/kvcache-ai/aenv-server:latest
```

Basic usage:

```bash
aenv auth  # server URL: http://127.0.0.1:8000
aenv pull ubuntu:22.04 --name ubuntu
aenv start ubuntu          # start and attach interactive shell
aenv start ubuntu --detach # background start, outputs sandbox ID
aenv pause <sandbox-id>
aenv resume <sandbox-id>
aenv delete <sandbox-id>
```

---

## Technical Verdict

AgentENV reveals an important engineering choice at the AI infrastructure layer: **shifting RL training environment sandbox design from a "service" model to a "state machine + snapshot" model.**

The traditional approach: spin up a new container per rollout, destroy it when done. Slow, wasteful.

AgentENV's approach: an environment is a state machine that can be quickly serialized/deserialized. Snapshot = checkpoint. Fork = branch parallel explorations from a checkpoint. Pause = yield resources without destroying state.

This design aligns closely with RL training characteristics:
- Many rollouts start from the same initial state (Fork is ~100× cheaper than recreating)
- Mid-task "checkpoints" can be shared across multiple subsequent policies (snapshot reuse)
- When GPU utilization fluctuates, environments can be paused without destruction (Memory Ballooning reclaims resources)

More importantly: now that it's open source, any team needing large-scale agent execution environments — whether for RL training or agent products — can run their own stack. The E2B-compatible API reduces migration cost to near zero.

> Project: github.com/kvcache-ai/AgentENV (898 ⭐, MIT)  
> Docs: kvcache-ai.github.io/AgentENV  
> Language: Rust  
> Requirements: Linux kernel 6.8+, /dev/kvm  
> License: MIT License
