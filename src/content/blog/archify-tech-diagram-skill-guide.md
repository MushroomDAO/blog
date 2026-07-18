---
title: "Archify：用一句话描述系统，AI 生成可交互的架构图 HTML 文件"
titleEn: "Archify: Describe Your System in Plain English, Get a Shareable Interactive Architecture Diagram"
description: "tt-a1i/archify 是一个 AI Agent Skill（2502 Stars，MIT），支持 Claude Code、Codex CLI 和 opencode。你用自然语言描述系统架构或流程，它生成一个自包含 HTML 文件：内置深浅主题切换、一键复制 PNG、4× 高清导出（PNG/JPEG/WebP/SVG）。支持 5 类技术图：架构图、工作流、时序图、数据流、生命周期图。"
descriptionEn: "tt-a1i/archify (2.5k★, MIT) is an AI agent skill for Claude Code, Codex CLI, and opencode. Describe your system in plain English → get a self-contained HTML file with dark/light theme toggle, one-click PNG copy, and 4× native raster export (PNG/JPEG/WebP/SVG). 5 diagram types: Architecture, Workflow, Sequence, Data Flow, Lifecycle."
pubDate: "2026-07-04"
updatedDate: "2026-07-04"
category: "Tech-News"
tags: ["架构图", "Archify", "AI Agent", "Claude Code", "技术文档", "可视化", "开源工具", "开发工具"]
heroImage: "../../assets/images/archify-tech-diagram-skill-guide-banner.jpg"
---

> **GitHub**: [tt-a1i/archify](https://github.com/tt-a1i/archify) · **2,502 Stars** · **MIT** · **v2.8.0**  
> **项目主页**: [tt-a1i.github.io/archify](https://tt-a1i.github.io/archify/)  
> **支持**: Claude Code · Codex CLI · opencode · Claude.ai

---

## 这个工具解决什么问题

你在写系统设计文档，需要一张架构图。

以前的选项：
- **用 draw.io / Figma 手画** → 费时间，改一次要重画
- **用 Mermaid** → 语法学习成本，布局不可控，视觉效果一般
- **截图 + 标注** → 不能主题切换，分辨率低，维护难

Archify 的方式：用自然语言描述系统，Claude 帮你画好，输出一个 **自包含 HTML 文件**。打开后可以：
- 一键切深色 / 浅色主题（SVG 还能自动跟随系统主题）
- 4× 高清导出 PNG / JPEG / WebP（不是放大截图，是原生渲染）
- 导出双主题 SVG，直接放进 README 或技术文档

---

## 5 种技术图类型

| 类型 | 适合场景 | 示例描述 |
|---|---|---|
| **Architecture** | 系统组件、云资源、数据库、缓存、服务边界 | "React 前端 + Node.js API + PostgreSQL + Redis" |
| **Workflow** | CI/CD、审批链、runbook、Agent 工具调用流程 | "用户提交 → Agent 规划 → 审批 → 工具调用 → 返回结果" |
| **Sequence** | API 调用链、鉴权、缓存回源、异步 trace | "前端调 API，API 验 JWT，查 Redis，miss 后回源 Postgres" |
| **Data Flow** | 数据管线、ETL/ELT、PII 边界、数据血缘 | "Web 端点击流 → 数据清洗 → Kafka → 数仓 → 模型消费" |
| **Lifecycle** | 状态机、任务 / 订单 / 部署生命周期 | "任务状态：排队 → 规划 → 执行 → 等待审批 → 完成 / 取消" |

---

## 快速安装（Claude Code 用户）

```bash
# 1. 下载 archify.zip
# 打开 https://github.com/tt-a1i/archify → Code → Download ZIP
# 或直接 clone：
git clone https://github.com/tt-a1i/archify /tmp/archify

# 2. 安装到 Claude Code（全局，所有项目都能用）
mkdir -p ~/.claude/skills/
cp -r /tmp/archify/archify ~/.claude/skills/

# 3. 安装依赖（首次）
cd ~/.claude/skills/archify && npm install
```

安装后 Claude Code 会自动识别这个 Skill，无需配置。

**其他工具安装路径**：

| 工具 | 安装命令 |
|---|---|
| Codex CLI | `unzip archify.zip -d ~/.agents/skills/` |
| opencode | `unzip archify.zip -d ~/.config/opencode/skills/` |
| Claude.ai | Settings → Capabilities → Skills → 上传 archify.zip |
| Claude.ai Projects | 上传 archify.zip 到 Project Knowledge（仅支持 Architecture 类型）|

---

## 使用方法：就是说话

安装后，直接在 Claude Code 里描述你的系统：

### 架构图

```
Use your archify skill to create an architecture diagram:
- React 前端
- Node.js API（Express）
- PostgreSQL 数据库
- Redis 缓存
- AWS S3 存储静态资源
- JWT 鉴权
```

### 时序图

```
Use archify to draw a sequence diagram:
用户打开页面，前端调 API，API 验证 JWT，查 Redis，
cache miss 后回源查 Postgres，返回 JSON，发出 trace 日志
```

### 工作流

```
Use archify to draw a workflow:
用户提交请求 → Agent 规划 → 需要审批时走审批链 → 工具调用 → Trace 日志 → 最终回复
```

### 数据流

```
Use archify to draw a data flow:
Web 和 Mobile 产生点击流事件，Edge API 收集，
Consent Gate 过滤 PII，Kafka 传输，Warehouse 存储，
Feature Store 做 feature 计算，Dashboard 和 ML Model 消费下游数据
```

### 状态机 / 生命周期

```
Use archify to draw a lifecycle diagram:
Agent 任务从 Queued 开始，经过 Planning → Executing → Reviewing，
可以暂停在 Needs Approval 或 Blocked，
Failed 可重试，Cancelled / Expired / Completed 是终态
```

---

## 生成结果是什么

Claude 会输出一个 `.html` 文件。用浏览器打开，你会看到：

**右上角两个按钮**：
- **Dark / Light** 切换主题（快捷键 `T`），偏好保存到 localStorage
- **Export** 打开导出菜单（快捷键 `E`）

**导出菜单**：

| 操作 | 说明 |
|---|---|
| Copy PNG | 直接复制到剪贴板，粘贴进 Slack / Notion / GitHub |
| Download PNG | 4× 原生分辨率，适合 Retina 屏和演示 PPT |
| Download JPEG | 4× 原生，有背景色（无透明）|
| Download WebP | 4× 原生，文件更小 |
| Download SVG | 双主题自包含向量图，放进 README 自动跟随读者的系统深浅色 |

**快捷键**：`T` 切主题，`E` 打开导出，方向键导航菜单，`Enter` 确认，`Esc` 关闭。

---

## SVG 放进 README 有多好用

这是 Archify 2.4 加的功能，很实用：

导出的 SVG 文件内置了 **两套颜色变量**（深色和浅色）加上 `@media (prefers-color-scheme)` 规则。所以同一个 `.svg` 文件放进 README 或文档：
- 读者用深色模式 → 显示深色图
- 读者用浅色模式 → 显示浅色图
- 不需要维护两张图，也不需要 `<picture>` 标签

```markdown
<!-- README 里直接这样用 -->
![系统架构图](docs/architecture.svg)
```

---

## 七种颜色语义

Archify 的颜色不是随机选的，每种颜色有固定含义，Claude 生成图时会自动对应：

| 组件类型 | 颜色 | 适用场景 |
|---|---|---|
| Frontend | 青色（Cyan）| 客户端、UI、边缘设备 |
| Backend | 翠绿（Emerald）| 服务器、API、服务 |
| Database | 紫色（Violet）| 数据库、存储、AI/ML |
| Cloud / AWS | 琥珀（Amber）| 云服务、基础设施 |
| Security | 玫瑰（Rose）| 鉴权、安全组、加密 |
| Message Bus | 橙色（Orange）| Kafka、RabbitMQ、事件总线 |
| External | 灰石（Slate）| 通用、外部系统 |

深浅模式会同步切换，不会出现深色图里有浅色节点的问题。

---

## 迭代修改很方便

生成后，直接在对话里说：

```
把 Redis 改成 DynamoDB
把 Auth Service 移到左边
给 API Gateway 加一个颜色标注
在 Kafka 和 Worker 之间加一个 Dead Letter Queue
```

Claude 会根据你的描述修改并重新生成 HTML 文件，不用从头来。

---

## 验证生成质量

Archify 内置了生成质量检查：

```bash
# 检查生成的 HTML 是否有问题
node ~/.claude/skills/archify/bin/archify.mjs check output.html

# 验证 workflow JSON 格式
node ~/.claude/skills/archify/bin/archify.mjs validate workflow input.json --json
```

检查内容：SVG 是否完整、数值是否合法、箭头是否有误（两点对角线 / 跨越无关节点）。

---

## 适合这些场景

**写得好，不如画得快**：
- 系统设计文档，配一张架构图比文字清楚得多
- PR 描述里的流程说明
- Runbook 里的故障处理流程
- 给非技术同事解释系统结构
- 面试/答辩时快速出一张系统图

**不适合**：
- 需要精确像素控制的设计稿（用 Figma）
- 高度自定义动画（用 Motion Canvas）
- 复杂数学 / 3D 图形（用 Manim）

---

## 在线 Demo

附上用 Archify 生成的 Archify 自身工作流技术图（单文件 HTML，支持深浅主题切换和导出）：

👉 [archify-workflow-demo.html](../../assets/diagrams/archify-workflow-demo.html) — 浏览器打开，按 `T` 切换主题，按 `E` 导出

---

> **安装包**: [archify.zip](https://github.com/tt-a1i/archify/blob/main/archify.zip) · **版本**: v2.8.0  
> **相关**: 基于 [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) v1.0 发展而来

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: Archify (tt-a1i/archify, 2.5k★, MIT) is an agent skill for Claude Code, Codex CLI, and opencode. Describe your system in plain English → a self-contained HTML file with dark/light theme toggle, 4× native raster export (PNG/JPEG/WebP), and dual-theme SVG (follows the host's `prefers-color-scheme`). 5 diagram types: Architecture, Workflow, Sequence, Data Flow, and Lifecycle. v2.8.0.

---

## Install (Claude Code)

```bash
git clone https://github.com/tt-a1i/archify /tmp/archify
mkdir -p ~/.claude/skills/ && cp -r /tmp/archify/archify ~/.claude/skills/
cd ~/.claude/skills/archify && npm install
```

Other agents: `~/.agents/skills/` for Codex CLI, `~/.config/opencode/skills/` for opencode, zip upload via Claude.ai Settings → Capabilities → Skills.

## Use It: Just Describe

```
Use your archify skill to create an architecture diagram:
- React frontend + Node.js API + PostgreSQL + Redis
- JWT authentication, AWS S3 for assets
```

Works for all 5 types: **Architecture** (components/cloud/services), **Workflow** (CI/CD/agent tool calls/approval chains), **Sequence** (API chains/cache fallback/auth), **Data Flow** (ETL/PII boundaries/data lineage), **Lifecycle** (state machines/order/deployment).

Iterate by chat: "add Redis", "move auth left", "add a dead letter queue after Kafka."

## The Output

A self-contained `.html` file. Open in any browser:

- **T** — toggle dark/light theme (persisted to localStorage)
- **E** — Export menu: Copy PNG to clipboard, Download PNG/JPEG/WebP (4× native resolution, no upsampling blur), Download SVG (dual-theme self-contained — one file follows the host's `prefers-color-scheme` automatically)

## SVG in README

The exported SVG includes both dark/light CSS variable sets + `@media (prefers-color-scheme)`. Drop one `.svg` file in your README — it shows dark for dark-mode readers, light for light-mode readers. No two-PNG `<picture>` dance needed.

## 7-Color Semantic Palette

Cyan (Frontend) · Emerald (Backend) · Violet (Database/ML) · Amber (Cloud/AWS) · Rose (Security/Auth) · Orange (Message Bus) · Slate (External). Claude maps components to colors automatically; both themes switch together.

**Links**: [GitHub](https://github.com/tt-a1i/archify) · [Project page](https://tt-a1i.github.io/archify/) · [archify.zip](https://github.com/tt-a1i/archify/blob/main/archify.zip)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
