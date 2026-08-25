---
title: "dsh-web：DeepSeek Harness 的插件生态包，任务看板 + SSH + 移动端 + 图像理解三步装齐"
titleEn: "dsh-web-deepseek-harness-web-plugin-sidebar-all-in-one"
description: "dsh-web 是 DeepSeek Harness（DSH）Web GUI 的插件聚合生态包，一条命令装齐任务看板、移动端远程、SSH 运维、图像理解、皮肤、Git 图谱、梁神模式、救助模式等全部能力。一切皆插件，可插拔可替换，附创意工坊（dsh-market.com）社区分发体系。6,000+ Star，Apache 2.0。"
descriptionEn: "dsh-web is the plugin ecosystem bundle for DeepSeek Harness (DSH) Web GUI. One command installs: task board with cron scheduling, mobile remote control, SSH ops terminal, image understanding, skins, Git graph, LiangShen mode, rescue mode, and more. Everything is a plugin — composable and replaceable. Creative Workshop (dsh-market.com) for community distribution. 6k+ stars, Apache 2.0."
pubDate: "2026-08-25"
updatedDate: "2026-08-25"
category: "Tech-News"
tags: ["开源", "DeepSeek", "AI编程", "插件生态", "SSH运维", "移动端", "dsh-web", "任务看板"]
heroImage: "../../assets/images/dsh-web-deepseek-harness-web-plugin-sidebar-all-in-one-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：zhu1090093659/dsh-web ⭐ 6,031 | Forks 386 | TypeScript | Apache 2.0  
创意工坊：https://dsh-market.com  
npm：@linxin666/dsh-web-all  
创建：2026-08-12

---

## 三步装齐

```bash
# ① 安装
dsh plugin --profile web add @linxin666/dsh-web-all@latest

# ② 重启
dsh web

# ③ 侧边栏所有功能一键开启
```

前提：已安装 DeepSeek Harness，`dsh web` 可正常启动。

---

## 是什么

dsh-web 是 DeepSeek Harness（DSH）Web GUI 的**插件聚合生态包**，理念是「一切皆插件」：每个功能都是独立的 npm 包，可插拔、可替换、可再开发——装全家桶是完整 AI 开发工作台，只挑一两个也能静默融入原生界面。

| 能力 | 原生 dsh web | dsh-web 全家桶 |
|------|-------------|----------------|
| 任务看板 | 无 | 多列看板 + cron 定时真实执行 |
| 移动端远程 | 无 | 扫码配对、SSE 实时同步；同链接也可配对 PC 浏览器 |
| SSH 运维 | 无 | 终端 / 文件传输 / 隧道 / 集群 |
| 图像理解 | 无 | describe_image 视觉工具（兼容所有 OpenAI 视觉端点） |
| 右侧面板 | 无 | 资源管理器 / 编辑器 / 终端 / Git / 浏览器 |
| Git 图谱 | 无 | 分支选择器 + 提交历史泳道图 |
| 主题皮肤 | 默认 | Blue Fantasy 内置，其他皮肤从创意工坊按需安装 |
| Agent 预设 | 官方预设 | + 梁神模式（两阶段锚定，实测 98.5 分） |
| 救助模式 | 无 | dsh-doctor：事务式快照/回滚，默认开启 |

---

## 各插件功能详解

### 任务看板（Task Board）

五列看板：待规划 / 待办 / 进行中 / 已完成 / 已失败。点卡片上的「执行」，任务交给真实的 DSH Agent 会话跑，跑完状态自动回写。

支持 cron 定时执行：详情里配表达式（比如每天 23:00 自动升级 DSH、每周一 09:00 生成周报），关闭浏览器后仍按时跑。附可选的空闲睡眠保护，支持 Windows / macOS / Linux（systemd-logind），允许屏幕熄灭，阻止整机因空闲睡眠中断任务。

### 移动端远程控制（Mobile Remote）

侧边栏底部的手机图标打开配对面板。扫二维码（或复制链接）配对后，手机进入独立移动端界面：看会话、开新会话、收发消息、切模型和思考强度、调权限预设，与桌面端实时同步（SSE）。

同一份配对链接也能配对 PC 浏览器，让另一台电脑运行完整 Web GUI。配对令牌一次性限时，「停止」随时吊销所有设备。开 cloudflared 公网隧道后可跨网络使用。

> Cloudflare quick tunnel（trycloudflare.com）和 Tailscale Serve 不透传 SSE，实时推送会降级为轮询；需即时推送则用 named tunnel。

### 远程连接（SSH Ops）

- **Web 终端**：xterm.js，实时输出，窗口大小自适应
- **文件传输**：SFTP 上传 / 下载，进度条，可浏览远程目录
- **端口转发**：本地隧道直连远程内网服务（数据库、API、管理后台），仅监听 127.0.0.1
- **集群执行**：一条命令并发多台主机，按别名 / 环境 / 标签过滤
- **Agent 直连**：Agent 和面板共用同一份主机配置，对话说"连一下 xxx 看状态"，Agent 即去远程执行

主机配置存在 `~/.dsh/dsh-ssh.json`，支持从 `~/.ssh/config` 一键导入，密钥 / 密码认证均可。

### 图像理解（Image Understanding）

给纯文本模型补视觉通道：`describe_image` 工具检测到图片（本地路径 / https URL / 会话附件）后，发给配置好的 OpenAI 兼容视觉端点（Qwen-VL、GLM-4V、GPT-4o、本地 Ollama 均可），**只有返回文本进入会话记录，图片本身不进**。

输入框加了图片按钮，选图后生成附件引用插入草稿，模型用 `describe_image` 分析。支持 `prompt` 参数自定义指令（OCR / UI 诊断 / 翻译），比默认描述准。配置在设置 → 插件配置 → Image understanding。

### 梁神模式（LiangShen Mode）

两阶段锚定的 Agent 预设（`dsh-liangshen`）：

- **第一阶段**：首轮模型请求只看到精确双工具（持久 `bash` + `str_replace_editor`）和一行 persona，无运行时上下文注入
- **第二阶段**：首次工具调用后，检测到首个 minimal-like 推理块时切换为 PTC Mode，恢复完整工具注册表和所有 prompt section

效果：Standard/PTC 模式约 91/92 分，Minimal 模式约 99/96 分，梁神模式 Windows 原生实测均值 **98.5**，在不牺牲完整工具能力的前提下维持高质量输出。Resume 不丢状态，支持 plan mode。

### 救助模式（dsh-doctor）

事务式救援体系，**默认开启**：

- Doctor Supervisor 后台服务检测启动失败、崩溃、心跳丢失、Web 故障、白屏
- 每次修复是一个事务：快照当前 profile → 在候选环境应用确定性规则 → 经隔离 dump-config + Web 健康门禁 → 原子提升，失败按字节回滚
- Web 控制台（设置 → 插件配置 → Doctor 卡片）展示故障事件，提供诊断、修复、回滚动作
- 「发送给 Harness」把最近故障摘要和错误堆栈投回当前会话，让 Agent 就地诊断

---

## 创意工坊（dsh-market.com）

对标 Steam Workshop：社区统一分发皮肤、宠物与插件。按设备点赞热度排序，前三名登首页颁奖台；皮肤支持实时试穿预览，插件提供一键复制安装命令。

Blue Fantasy 蓝色幻想皮肤随皮肤插件内置：鲸鱼插画垫在半透明面板下，靛蓝色调贯穿全局。鲸鱼娘宠物和其他皮肤从工坊浏览、试穿后按需安装。

站点本身纯静态构建，由脚本从三类真值源（skin.json / pet.json / community.json）确定性生成，点赞等动态能力由 Cloudflare Workers + D1 承载，push 到 main 自动部署。

---

## 单独安装某个插件

不需要全家桶时，按需安装：

```bash
dsh plugin --profile web add @linxin666/dsh-client-ui-task-board@latest    # 任务看板
dsh plugin --profile web add @linxin666/dsh-ssh@latest                     # SSH 运维
dsh plugin --profile web add @linxin666/dsh-tool-describe-image@latest     # 图像理解
dsh plugin --profile web add @linxin666/dsh-pet@latest                     # 宠物
dsh plugin --profile web add @linxin666/dsh-liangshen@latest               # 梁神模式
dsh plugin --profile web add @linxin666/dsh-doctor@latest                  # 救助模式
dsh plugin --profile web add dsh-better-sidebar@latest                     # 右侧面板
```

---

## 为什么"一切皆插件"

DSH 本身已经是成熟的 AI 编程 harness。dsh-web 解决的是 Web GUI 功能碎片化的问题：每个团队需要的组合不同（有人要 SSH，有人要移动端，有人只要皮肤），但过去每个功能都需要单独寻找、单独配置、手动维护兼容性。

插件体系把这个问题收拢进统一的安装机制（官方 profile 机制，不改 DSH 源码），创意工坊解决发现和分发，救助模式解决升级和故障，三者合起来构成一个可持续维护的生态，而不是一堆散包。

---

**相关链接**

- GitHub：https://github.com/zhu1090093659/dsh-web
- 创意工坊：https://dsh-market.com
- npm（聚合包）：https://www.npmjs.com/package/@linxin666/dsh-web-all

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## dsh-web: The DeepSeek Harness Plugin Ecosystem — Task Board, SSH, Mobile, and Image Understanding in Three Steps

*by Mycelium Protocol*

---

GitHub: zhu1090093659/dsh-web ⭐ 6,031 | Forks 386 | TypeScript | Apache 2.0  
Creative Workshop: https://dsh-market.com  
npm: @linxin666/dsh-web-all  
Created: 2026-08-12

---

### Three Steps

```bash
# ① Install
dsh plugin --profile web add @linxin666/dsh-web-all@latest

# ② Restart
dsh web

# ③ Enable everything from the sidebar
```

Prerequisite: DeepSeek Harness installed and `dsh web` running normally.

---

### What It Is

dsh-web is the **plugin ecosystem bundle** for DeepSeek Harness (DSH) Web GUI. The philosophy: everything is a plugin. Each feature is an independent npm package — composable, replaceable, and re-developable. Install the full bundle for a complete AI development workstation, or pick one or two and they quietly blend into the native interface.

| Capability | Native dsh web | dsh-web bundle |
|------------|---------------|----------------|
| Task board | None | Multi-column kanban + real cron execution |
| Mobile remote | None | QR code pairing, SSE sync; same link pairs PC browsers too |
| SSH ops | None | Terminal / file transfer / tunnels / cluster |
| Image understanding | None | `describe_image` tool (any OpenAI-compatible vision endpoint) |
| Right panel | None | File explorer / editor / terminal / Git / browser |
| Git graph | None | Branch selector + commit history swim-lane |
| Themes | Default | Blue Fantasy built-in, others from the Creative Workshop |
| Agent presets | Official | + LiangShen mode (two-phase anchored, 98.5 avg score) |
| Rescue mode | None | dsh-doctor: transactional snapshot/rollback, on by default |

---

### Plugin Breakdown

**Task Board** — Five columns: backlog / todo / in-progress / done / failed. "Execute" sends the task to a real DSH agent session; status updates automatically. Cron scheduling works after the browser closes. Optional idle-sleep protection on Windows, macOS, and Linux.

**Mobile Remote** — Pair via QR code. Phone gets a dedicated mobile UI: view sessions, start new ones, send messages, switch model and thinking intensity, adjust permission presets — all in real-time sync with desktop (SSE). The same pairing link works for a PC browser too. Tokens are one-use and time-limited. Cloudflare named tunnels enable cross-network pairing.

> Note: Cloudflare quick tunnel (trycloudflare.com) and Tailscale Serve don't forward SSE — real-time push downgrades to polling. For instant push, use a named tunnel.

**SSH Ops** — xterm.js terminal, SFTP file transfer with progress, port forwarding (loopback-only), cluster-wide command execution with tag/environment filters, and agent integration (say "check the status on xxx" in chat; the agent runs it remotely). Configuration in `~/.dsh/dsh-ssh.json`, imports from `~/.ssh/config`.

**Image Understanding** — Adds vision to text-only models. `describe_image` detects images (local path / https URL / session attachment), sends them to any OpenAI-compatible vision endpoint (Qwen-VL, GLM-4V, GPT-4o, local Ollama), and **only the returned text enters the session** — the image itself doesn't. Custom `prompt` param supports OCR, UI diagnosis, translation.

**LiangShen Mode** — Two-phase anchored agent preset:
- Phase 1: model sees only two tools (persistent `bash` + `str_replace_editor`) and one persona line — no runtime context injection
- Phase 2: after first tool call, when a minimal-like reasoning block appears, switches to PTC Mode with full tool registry and all prompt sections

Standard/PTC scores ~91/92; Minimal ~99/96; LiangShen averages **98.5** on Windows native — maintains full tool capability without sacrificing output quality. Resume-safe, plan mode supported.

**Rescue Mode (dsh-doctor)** — Transactional rescue, on by default. Detects crashes, heartbeat loss, web failures, white screens. Each fix is a transaction: snapshot → apply deterministic rules → isolated dump-config + web health gate → atomic promotion. Failure rolls back byte-for-byte. Web console shows fault events with diagnose/fix/rollback actions; "Send to Harness" formats the latest fault summary into a troubleshooting prompt in the current session.

---

### Creative Workshop (dsh-market.com)

Positioned like Steam Workshop for DSH. Community distributes skins, pets, and plugins. Rankings by device upvotes; top three on the front page podium. Skins support live preview before install; plugins get one-click install commands.

Blue Fantasy is the built-in default: whale illustration under translucent panels, indigo tones throughout. Other skins and the whale-girl pet are available on the Workshop.

The site itself is a pure static build, generated deterministically from three source-of-truth files (skin.json / pet.json / community.json). Dynamic features (likes, per-device votes) run on Cloudflare Workers + D1. Push to main deploys automatically.

---

### Individual Plugin Install

When the full bundle is more than you need:

```bash
dsh plugin --profile web add @linxin666/dsh-client-ui-task-board@latest    # Task board
dsh plugin --profile web add @linxin666/dsh-ssh@latest                     # SSH ops
dsh plugin --profile web add @linxin666/dsh-tool-describe-image@latest     # Image understanding
dsh plugin --profile web add @linxin666/dsh-liangshen@latest               # LiangShen mode
dsh plugin --profile web add @linxin666/dsh-doctor@latest                  # Rescue mode
dsh plugin --profile web add dsh-better-sidebar@latest                     # Right panel
```

---

### Why "Everything Is a Plugin"

DSH is already a mature AI coding harness. dsh-web solves Web GUI feature fragmentation: every team needs a different combination (some need SSH, some need mobile, some just want a skin), but until now each feature required finding separately, configuring separately, and manually managing compatibility.

The plugin architecture routes this through DSH's official profile mechanism — no source code changes to DSH itself. The Creative Workshop handles discovery and distribution. Rescue mode handles upgrades and failures. Together they form a maintainable ecosystem, not a pile of loose packages.

---

**Links**

- GitHub: https://github.com/zhu1090093659/dsh-web
- Creative Workshop: https://dsh-market.com
- npm: https://www.npmjs.com/package/@linxin666/dsh-web-all

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
