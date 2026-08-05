---
title: "@cloudflare/computer：给每个 Agent 一台自己的电脑"
titleEn: "cloudflare-computer-agent-runtime-isolate-container"
description: "Cloudflare 在 Agents Week 发布 @cloudflare/computer：让 Agent 在同一个虚拟文件系统里动态切换 Isolate（快、廉价）和 Container（完整 Linux），把 Durable Object 的水平无限扩展和容器的垂直能力合二为一。早期预览已开源，给 AI 编程/任务 Agent 提供新的计算基础。"
descriptionEn: "@cloudflare/computer gives every AI agent its own virtual filesystem backed by SQLite and dynamically routes execution between cheap Isolates (Workers) and full Linux Containers — solving the fundamental scale problem of running 100M+ concurrent agents without spinning up a container for each one. Open-source early preview, part of Cloudflare Agents Week 2026."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["CloudflareAgents", "Agent架构", "Cloudflare Workers", "容器", "Isolate", "AI基础设施", "开源", "Mycelium"]
heroImage: "../../assets/images/cloudflare-computer-agent-runtime-isolate-container-banner.jpg"
---

*by Mycelium Protocol*

---

给 Agent 开一个容器（Container），这是过去一年里大多数团队的默认答案：容器里装好文件系统、Shell、依赖包，Agent 在里面干活，干完销毁。

Cloudflare 在刚结束的 Agents Week（2026 年 8 月 2-4 日）里指出了这条路的问题：**全球所有超大规模云加起来，也没有足够的计算资源给每个用户的每个 Agent 各开一个容器**。1 亿并发 Agent，1 亿个容器——这不可能。

他们给出的答案是 **[@cloudflare/computer](https://github.com/cloudflare/computer)**（早期预览，已开源）。

---

## 问题根源：Agent 不需要一直用容器

容器很重，但 Agent 大多数时候做的事很轻：读写文件、检查 git 状态、解析 JSON、处理数据。这些操作根本不需要完整的 Linux userland。

Cloudflare 的观察是：**绝大多数 Agent 操作可以在 Isolate（Workers）里完成，只有在需要 `npm`、原生二进制、或者完整 Shell 环境时才需要容器**。目标是让容器调用比例低于 10%。

这个观察来自他们自己在用的 Agent 架构：Agent 逻辑运行在 Durable Object（Isolate）里，容器按需作为工具挂载上来。

---

## 架构：共享文件系统 + 双执行后端

`@cloudflare/computer` 的核心是 **Workspace**——一个以 SQLite 为底层存储的虚拟文件系统：

```
Workspace（虚拟文件系统，SQLite 持久化）
   ├── 来源：git repo、云存储 bucket、任意文件
   ├── Isolate 后端（fast, cheap）
   │   └── just-bash → 翻译成 JS → Dynamic Worker 执行
   │       文件系统通过 Worker Binding 直接访问
   └── Container 后端（full Linux）
       └── Cloudflare Containers + FUSE 挂载
           修改自动同步回 Workspace
```

两个后端共用同一套文件，共用同一个 `exec(string, options)` 接口。Agent 的 system prompt 里描述两个 backend 的特点，模型自行选择——经测试，前沿模型的选择准确率很高。

---

## 快速上手

```bash
npm install @cloudflare/computer
```

最小示例：在 `@cloudflare/think` Agent 里挂载一个 Workspace：

```typescript
import { Think } from "@cloudflare/think";
import { Workspace } from "@cloudflare/computer";
import { createWorkersAI } from "workers-ai-provider";

export class Agent extends Think {
  override workspace = new Workspace({
    storage: this.ctx.storage,
    useThink: true,
  });

  override getModel() {
    return createWorkersAI({ binding: this.env.AI })("@cf/zai-org/glm-5.2");
  }

  override getSystemPrompt() {
    return `你是一个 bug 分诊 Agent。
用 /workspace/repo 里的代码复现 bug，定位问题，在安全的情况下
做出精准修复，然后验证。`;
  }
}
```

接上 Cloudflare Container 后端：

```typescript
import {
  CloudflareContainerBackend,
  withWorkspaceContainer,
} from "@cloudflare/computer/backends/container";

export class Agent extends withWorkspaceContainer(Think) {
  override workspace = new Workspace({
    storage: this.ctx.storage,
    useThink: true,
    backends: [
      new CloudflareContainerBackend({
        container: () => this,
        workspace: {
          binding: "Agent",
          id: this.ctx.id.toString(),
        },
      }),
    ],
  });
}
```

暴露文件/git/shell 工具给模型：

```typescript
import { createAITools } from "@cloudflare/computer/tools";

override getTools() {
  return {
    ...createAITools({
      workspace: this.workspace,
      shell: {
        defaultBackend: "container",
        backends: {
          container: {
            description:
              "完整 Linux 环境：npm、node、包管理器、测试运行器、原生命令都在 PATH 里。" +
              "只有任务超出文件操作范围时才用它。",
          },
        },
      },
    }),
    replyToIssue,  // 你自己的产品工具
  };
}
```

Agent 开始前用 API 预置环境：

```typescript
async startTriage(report: { title: string; body: string; repoUrl: string }) {
  await this.workspace.fs.mkdir("/workspace", { recursive: true });
  await this.workspace.fs.writeFile(
    "/workspace/BUG_REPORT.md",
    `# ${report.title}\n\n${report.body}\n`,
  );
  await this.workspace.git.clone({
    url: report.repoUrl,
    dir: "/workspace/repo",
  });

  return this.submitMessages([{
    id: crypto.randomUUID(),
    role: "user",
    parts: [{ type: "text", text: `分诊这个 bug: ${report.title}` }],
  }]);
}
```

`Workspace` 还提供 `node:fs` 兼容的 wrapper，可以直接配合第三方 Node.js 库使用。

---

## 为什么是 Isolate 而不是容器

Cloudflare 在这个方向上押注了将近 10 年：

- **2017**：推出 Cloudflare Workers（Isolate 模型）
- **2020**：推出 Durable Objects（持久化 Isolate，有状态，横向无限扩展）
- **2024**：Durable Objects 里嵌入 SQLite，横向扩展同时获得垂直能力
- **2025**：Durable Objects 可以按需挂载容器沙箱（Container 进 GA beta）
- **2026**：`@cloudflare/computer` 把这一套封装成统一 API

Isolate 的优势：
- 毫秒级冷启动（容器是秒级）
- 空闲时自动 hibernate（不计费）
- 理论上横向无限扩展
- 可以动态派生新的 Isolate 执行不可信代码

容器的优势：
- 完整 Linux userland
- 任意二进制、任意包管理器
- 垂直扩展能力（大内存、多核）

`@cloudflare/computer` 让两者在同一个工作流里并存，而不是强迫开发者选择。

---

## 技术细节

**Isolate 后端**：使用 [just-bash](https://justbash.dev/) 把 Shell 命令翻译成 JavaScript，在 Dynamic Worker 里执行。Workspace 的文件通过 Worker Binding 直接可见，不需要网络传输。

**Container 后端**：使用 FUSE（Filesystem in Userspace）把 Workspace 挂载到容器里。文件变更实时同步回 Workspace（SQLite），Agent 状态始终一致。

**audit 和 access control**：所有 exec 操作都有 gate 和 audit trail，可以精确控制 Agent 允许执行哪些操作。

---

## 现在能用来做什么

Cloudflare 内部已经在用这套架构做：
- 仅用 Isolate 来 build、test、deploy JavaScript 应用
- 给每个客户生成定制化文档
- 用 Web Browser 执行复杂任务

开源仓库：[github.com/cloudflare/computer](https://github.com/cloudflare/computer)，含 step-by-step tutorial（`examples/tutorial/`）。

---

## 背景：Agents Week 全景

`@cloudflare/computer` 是 Cloudflare Agents Week（8月2-4日）集中发布的一部分，同期还有：

- **Agent Development Lifecycle**：从 PR 审查到部署的 Agent 驱动 CI/CD
- **Cloudflare Agents**：统一管理所有部署中的 Agent session 和性能数据
- **Cloudflare Wallets**：Agent 原生支付和身份（x402 协议）
- **Local tracing**：`wrangler dev` 结构化 trace，Agent 可以直接 debug Worker
- **Dynamic Workers + Object Capabilities**：Worker 间零序列化传递对象引用

整个 Agents Week 的主线是：**云基础设施必须为 Agent 原生设计，而不只是把为人类浏览器设计的 Web 基础设施接上 AI**。`@cloudflare/computer` 是这个主线上计算层的核心。

仓库：[github.com/cloudflare/computer](https://github.com/cloudflare/computer)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## @cloudflare/computer: Give Every AI Agent Its Own Computer

*by Mycelium Protocol*

Spinning up a container for every agent has been the default for the past year. Cloudflare's Agents Week (August 2-4, 2026) named the problem with that approach: **there isn't enough compute on every hyperscaler combined to give 100 million concurrent agents their own containers**. Their answer is **[@cloudflare/computer](https://github.com/cloudflare/computer)** — an early-preview, open-source agent runtime that dynamically routes execution between cheap Isolates and full Linux Containers, both sharing the same virtual filesystem.

### The Core Insight

Most agent work is light: read/write files, check git state, parse JSON, process data. None of that needs a full Linux userland. Cloudflare's goal with @cloudflare/computer is to keep container invocations below 10% of total execution — with Isolates (Cloudflare Workers) handling the rest.

The architecture that made this possible: agent logic runs in a Durable Object (an Isolate with persistent state and infinite horizontal scale); containers mount on-demand as tools via FUSE. @cloudflare/computer packages this pattern into a single installable abstraction.

### Architecture: Shared Filesystem, Dual Backends

The central piece is **Workspace** — a virtual filesystem backed by SQLite:

```
Workspace (SQLite-backed virtual filesystem)
   ├── Sources: git repos, cloud storage buckets, arbitrary files
   ├── Isolate backend (fast, cheap)
   │   └── just-bash → JS → Dynamic Worker
   │       Filesystem visible via Worker Binding
   └── Container backend (full Linux)
       └── Cloudflare Containers + FUSE mount
           Changes sync back to Workspace automatically
```

Both backends share the same files and the same `exec(string, options)` interface. The agent's system prompt describes each backend's capabilities; frontier models are reliable at picking the right one.

### Minimal Setup

```bash
npm install @cloudflare/computer
```

Wire a Workspace to a `@cloudflare/think` agent, expose file/git/shell tools, set the system prompt — the agent can now read, write, run shell commands in isolates, or escalate to a container when it needs npm or native binaries. The `Workspace` class also provides a `node:fs`-compatible wrapper for third-party JavaScript libraries.

### Why Isolates, Not Just Containers

Cloudflare has been making this bet for almost 10 years:

| Year | Milestone |
|------|-----------|
| 2017 | Cloudflare Workers (Isolate model) |
| 2020 | Durable Objects (stateful, hibernate, infinite horizontal scale) |
| 2024 | SQLite inside Durable Objects (vertical capability added) |
| 2025 | Durable Objects can spin up container sandboxes on-demand |
| 2026 | @cloudflare/computer wraps all of this into one API |

Isolates: millisecond cold start, auto-hibernate when idle (no billing), infinite horizontal scale.  
Containers: full Linux, any binary, package managers, vertical scale.  
@cloudflare/computer: both, in the same workflow, without forcing a choice.

### What Cloudflare Is Already Building With It

- JavaScript apps built, tested, and deployed entirely in Isolates
- Per-customer documentation generated at scale
- Web browser automation for complex tasks

All from the same @cloudflare/computer primitives.

### Agents Week Context

@cloudflare/computer shipped alongside Agent Development Lifecycle (AI-driven CI/CD), Cloudflare Agents (unified agent session management), Cloudflare Wallets (x402 agent payments), local tracing for Workers, and Dynamic Workers with object capabilities. The through-line: cloud infrastructure needs to be designed agent-native, not retrofitted from human-facing web infrastructure.

Early preview: [github.com/cloudflare/computer](https://github.com/cloudflare/computer) · includes step-by-step tutorial at `examples/tutorial/`

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
