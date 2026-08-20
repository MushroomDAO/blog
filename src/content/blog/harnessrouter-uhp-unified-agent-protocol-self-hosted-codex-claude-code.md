---
title: "HarnessRouter：单容器自托管多 AI 编码 Agent，UHP 统一协议让 Claude Code / Codex / Hermes 共用一套 API"
titleEn: "harnessrouter-uhp-unified-agent-protocol-self-hosted-codex-claude-code"
description: "HarnessRouter 社区版是一个开源（Apache 2.0）的自托管 Agent 调度平台，单 Docker 容器运行，内置 Claude Code、Codex、Hermes 三套 Agent harness，通过 UHP（统一 Harness 协议）统一 API，所有数据本地留存，无遥测，无账号，适合私有化部署、产品内嵌 AI 编码能力和多 Agent 对比评测。Starter Kit 提供 Slides / Sheets / Dashboards / Videos 四个开箱即用产品。"
descriptionEn: "HarnessRouter Community Edition is an open-source (Apache 2.0) self-hosted agent scheduling platform. Single Docker container, three built-in agent harnesses (Claude Code, Codex, Hermes), unified via UHP (Unified Harness Protocol) as one API. All data stays local, no telemetry, no account required. Built for private deployment, embedding AI coding capability in products, and multi-agent benchmarking. Starter Kit includes four ready-to-launch products: Slides, Sheets, Dashboards, Videos."
pubDate: "2026-08-20"
updatedDate: "2026-08-20"
category: "Tech-News"
tags: ["AI编码Agent", "自托管", "UHP", "Claude Code", "Codex", "开源", "私有部署", "Agent调度"]
heroImage: "../../assets/images/harnessrouter-uhp-unified-agent-protocol-self-hosted-codex-claude-code-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：HarnessRouter/harnessrouter  
官网：harnessrouter.ai  
协议：unifiedharnessprotocol.org  
许可证：Apache 2.0（社区版）  
部署：Docker 单容器，约 700MB

---

「LLM 返回 token；harness 给它一个沙箱、工具集和循环，让它返回真正的文件。」

这是 HarnessRouter 对「Agent harness」的定义。LLM 本身是一个语言预测器，harness 是把它变成能干活的 Agent 的那一层——管理文件系统访问、工具调用、多轮循环、流式输出、取消信号和失败处理。

问题是：Claude Code、Codex、Hermes 各有自己的 harness 接口，想在产品里接入多个 Agent，就要分别集成每一套 API。HarnessRouter 的答案是给它们套上同一个协议层，做成统一的单容器服务。

---

## 一、核心能力

### 统一 Harness 协议（UHP）

UHP（Unified Harness Protocol）是 HarnessRouter 开放的协议标准，定义了 harness 的统一 API：任务创建、会话管理、流式输出、文件传输、取消信号、失败处理。

社区版实现了 UHP Full 类合规（`UHP-class Full` 徽章），和托管版使用同一个协议。**一次接入 HarnessRouter API，就能切换任意支持 UHP 的 Agent**，不需要改客户端代码。

### 开箱三套 Agent Harness

第一次启动时，容器自动安装：

- **Claude Code**（Anthropic 自有协议，Anthropic 条款适用）
- **Codex**（Apache 2.0）
- **Hermes**（需自行确认上游许可）

Claude Code 和 Hermes 不打包进 Docker 镜像——这是许可证决策而非打包偏好：两者都无法被再发行进公开镜像，第一次启动时从上游直接安装，意味着你在自己的机器上、在你自己接受的条款下安装它们。

```
[harnessrouter] installing Claude Code (Anthropic's terms apply)…
[harnessrouter] installing Codex (Apache-2.0)…
[harnessrouter] installing Hermes (check its upstream license before use)…
[harnessrouter] ready on :3000
```

### 本地数据，零遥测

- API 密钥只用于调用对应 Provider，**不离开容器**，不进遥测
- 所有数据（数据库、文件、Agent CLI）存在 Docker volume（`/data`）
- 无账号注册，无云端依赖
- 首次启动约 30 秒（安装 Agent CLI），之后几秒内就绪

### Web 控制台

访问 `localhost:3000`，可视化管理 Agent 任务、调试运行过程、配置 Provider 密钥。

---

## 二、快速部署

### 最简启动（四行）

```bash
# 1. 拉取镜像（约 700MB）
docker pull harnessrouter/harnessrouter

# 2. 运行（无需预设任何密钥）
docker run -d --name harnessrouter \
  -p 127.0.0.1:3000:3000 \
  -v harnessrouter:/data \
  harnessrouter/harnessrouter

# 3. 等待就绪（约 30 秒）
docker logs -f harnessrouter
# 出现 "ready on :3000" 后打开浏览器

# 4. 登录（默认凭证，务必立即修改）
# http://localhost:3000  用户名: harnessrouter  密码: harnessrouter
```

`-p 127.0.0.1:3000:3000` 把服务绑定到回环地址，只有本机可访问——这是默认安全设计。Provider 密钥在控制台里粘贴，不是通过环境变量传入，也不会进 shell 历史记录。

### 自定义凭证

```bash
docker run -d --name harnessrouter \
  -p 127.0.0.1:3000:3000 \
  -v harnessrouter:/data \
  -e HR_AUTH_USER=你的用户名 \
  -e HR_AUTH_PASSWORD=你的密码 \
  harnessrouter/harnessrouter
```

密码哈希存在 volume 里（`/data/selfhost-auth.json`：用户名 + salt + hash，不存明文），控制台改密后环境变量就不再生效。

---

## 三、Starter Kit：四个开箱即用产品

HarnessRouter/starter-kit 仓库里预置了四个完整产品，在控制台「Starter Kits」页面一键启动：

### Slides：对话设计幻灯片

说出想要什么演示文稿，Agent 像设计师一样工作——先定结构、再定样式系统、再逐页完成。产出是**可拖动、可编辑的对象画布**，不是截图或 PDF。

### Sheets：有一列是 Agent 的表格

行是你的数据，「Agent 列」对每一行跑一次 Agent——以左边的列作为输入，把 Agent 的输出填进单元格。200 行数据 = 200 次 Agent 运行，不需要自己编排。

### Dashboards：问数据库一个问题

描述你想理解什么，Agent 读取 schema，决定用哪些图表来回答，写 SQL，渲染出来。打开 dashboard 时自动重新查询，数据是今天的。**只使用 SELECT-only 账户，每条 SQL 在执行前都经过检查。**

### Videos：描述视频，看镜头一个个出来

Agent 规划镜头，为每个镜头写提示词，渲染，铺到时间轴上。可在真实时间轴上剪辑——裁剪、分割、图层、背景音乐、旁白——导出成单个文件。镜头可以从静帧开始，也可以从上一个镜头的最后一帧继续，让两段镜头无缝衔接。

---

## 四、设计哲学：会话即文档

Starter Kit 四个产品背后是同一个模型：**会话即文档**。

演示文稿列表就是 harness 的会话列表；工作文件是那个会话工作区里的文件。删除会话，工作就一起消失。这个设计让「AI 产出的工件」有了自然的生命周期——不是漂浮在某个地方等你去找，而是和它所在的会话绑定在一起。

---

## 五、适用场景

**产品内嵌 AI 编码 Agent**：通过 UHP API 把 HarnessRouter 作为产品后端，前端只对接一套 API，切换底层 Agent 不改代码。Starter Kit 的四个产品是现成的参考实现。

**多 Agent 对比评测**：三套 Agent（Claude Code / Codex / Hermes）跑同一任务，对比输出质量和成本。都通过同一个 UHP 接口，基准对比更公平。

**私有化部署**：密钥不离开容器，无遥测，无第三方账号，适合有数据合规要求的团队。API 密钥在控制台粘贴不进 shell 历史。

**本地开发实验**：想跑 Claude Code 或 Codex 做一个实验，但不想搭复杂环境。单 docker run 命令，三套 Agent 自动装好，控制台可视化调试。

---

## 六、注意事项

**默认密码必须立即修改**：启动后容器会持续警告直到你改掉。把实例暴露在公网前必须先改。

**首次启动慢**：约 30 秒安装 Agent CLI，此时访问 localhost:3000 会被拒绝连接，这是正常现象，不是容器坏了。之后每次启动几秒内就绪。

**许可证层次**：HarnessRouter 容器本身是 Apache 2.0，但内部安装的 Claude Code 受 Anthropic 条款约束、Hermes 需自行确认上游许可。使用前请阅读各 Agent 的条款。

**Docker Compose 模式**：默认 compose 文件把 3000 端口绑定到所有接口，比单行 docker run 暴露面更大。需要修改一行配置改为回环绑定。

---

HarnessRouter 解决的是一个实际问题：AI 编码 Agent 正在碎片化，每个 harness 一套 API，想做产品集成或横向对比都要分别处理。UHP 协议层加上单容器部署，是目前这个问题最轻量的一个开源答案。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## HarnessRouter: Single-Container Self-Hosted Multi-Agent Scheduler — UHP Unified Protocol for Claude Code, Codex, and Hermes

*by Mycelium Protocol*

---

GitHub: HarnessRouter/harnessrouter  
Site: harnessrouter.ai  
Protocol: unifiedharnessprotocol.org  
License: Apache 2.0 (Community Edition)  
Deploy: Single Docker container, ~700 MB

---

"An LLM returns tokens. A harness gives it a sandbox, tools, and a loop, so it returns the actual file."

That's HarnessRouter's definition of an agent harness. The LLM is a language predictor; the harness is the layer that turns it into something that can do work — managing filesystem access, tool calls, multi-turn loops, streaming output, cancellation, and failure handling.

The problem: Claude Code, Codex, and Hermes each have their own harness interface. Integrating multiple agents into a product means integrating each API separately. HarnessRouter's answer: wrap them all in a common protocol layer and ship it as a single containerized service.

---

### Core Capabilities

**Unified Harness Protocol (UHP)**: An open standard defining the unified harness API — task creation, session management, streaming output, file transfer, cancellation, failure handling. Community Edition implements UHP Full-class conformance, the same protocol as the hosted service. One integration, any UHP-conformant agent.

**Three built-in agent harnesses**: Claude Code (Anthropic terms), Codex (Apache 2.0), and Hermes (verify upstream license). These are fetched from upstream on first start rather than shipped in the image — a licensing decision, not a packaging preference. You install them yourself, under their respective terms.

**Local data, zero telemetry**: API keys stay in the container, only used to call their provider. All data (database, files, agent CLIs) on a Docker volume. No account creation, no cloud dependency.

**Web console** at `localhost:3000` for visual task management, debugging, and provider key configuration.

---

### Deploy in Four Lines

```bash
docker pull harnessrouter/harnessrouter

docker run -d --name harnessrouter \
  -p 127.0.0.1:3000:3000 \
  -v harnessrouter:/data \
  harnessrouter/harnessrouter

docker logs -f harnessrouter  # wait for "ready on :3000"

# Sign in: localhost:3000  user: harnessrouter  pw: harnessrouter
# Change the password immediately.
```

`-p 127.0.0.1:3000:3000` binds to loopback only — the default security posture. Provider keys are pasted in the console, never passed as environment variables, and never enter shell history.

---

### Starter Kit: Four Ready-to-Launch Products

**Slides**: Describe a presentation. The agent works like a designer — structure first, then style system, then slide by slide. The output is a draggable, editable canvas of objects, not a screenshot.

**Sheets**: Your rows are data; an agent column runs an agent once per row, using left-side columns as input, filling each cell with the agent's output. 200 rows = 200 agent runs without manual orchestration.

**Dashboards**: Describe what you want to understand. The agent reads your schema, decides which charts answer it, writes SQL, renders panels. Opens with live queries. SELECT-only database account; every statement checked before execution.

**Videos**: Describe the film. The agent plans shots, writes a prompt per shot, renders them, lays them on a timeline as they arrive. Real timeline editing — trim, split, layers, audio, voice-over, export. Shots can seed from a still or continue from the previous shot's last frame for seamless joins.

All four follow the same model: **a session is a document**. The document is a file in the session's workspace. Delete the session, the work goes with it.

---

### Use Cases

**Embed AI coding agent capability in a product**: HarnessRouter as product backend, one UHP API for the frontend, switch underlying agents without changing client code.

**Multi-agent benchmarking**: Three agents (Claude Code / Codex / Hermes) on the same task through the same interface. Fair comparison baselines.

**Private deployment**: Keys don't leave the container, no telemetry, no third-party accounts. For teams with data compliance requirements.

**Local experimentation**: One `docker run`, three agents installed, visual console — no complex environment setup.

---

### Things to Watch

Default password must be changed immediately — the container warns on every start until you do. First start takes ~30 seconds for CLI installation; `localhost:3000` refuses connections during this window, which is normal. Docker Compose mode binds to all interfaces by default — change one line for loopback-only. Each embedded agent has its own license terms beyond HarnessRouter's Apache 2.0.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
