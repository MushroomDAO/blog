---
title: 'DSH Remote：让 DeepSeek Harness 跑在 Mac 上，手机通过 Tailscale 私网远程控制'
titleEn: "DSH Remote: Run DeepSeek Harness on Mac, Control It From Your Phone via Tailscale Private Network"
description: "MIT 开源，TypeScript，社区独立项目。通过私有 Tailscale 网络把 DeepSeek Harness 变成手机可用的 PWA——发起任务、跟进 Agent、处理审批、回答提问，凭据和设置只留 Mac 本机，不接入公网。LaunchAgent 自启，Harness 停止后自动退出。"
descriptionEn: "MIT open-source, TypeScript, independent community project. Wraps DeepSeek Harness in a mobile PWA served over a private Tailscale network — launch tasks, monitor Agent progress, handle approvals, answer questions. Credentials and settings stay on the Mac; nothing reaches the public internet. LaunchAgent auto-starts; exits when Harness stops."
pubDate: "2026-09-15"
updatedDate: "2026-09-15"
category: "Tech-News"
tags: ["DeepSeek-Harness", "open-source", "Tailscale", "PWA", "mobile", "AI-agent", "privacy", "remote-control"]
heroImage: "../../assets/images/dsh-remote-deepseek-harness-mobile-tailscale-pwa-mac-banner.jpg"
---

> 📌 开源仓库：Zouu-X/dsh_remote
> GitHub：https://github.com/Zouu-X/dsh_remote
> License：MIT | Stars：7 | Language：TypeScript
> 独立社区项目，与 DeepSeek 官方无关联

---

DeepSeek Harness 本身是跑在桌面上的 Agent 运行时——发任务、看输出、处理审批，都要坐在电脑前。

DSH Remote 解决的是这个场景：**Mac 在家运行 Harness，人在外面，用手机控制。**

不暴露公网，不走云中转，走你自己的 Tailscale 私有网络。

---

## 架构：三层隔离

```text
手机 PWA
  │  Tailscale 私有网络 HTTPS/WSS
  ▼
Mac 上的 Tailscale Serve（TLS 终止）
  │
  ▼
Remote Host · 127.0.0.1:3090（只监听本机）
  │  身份解析 + API 白名单过滤
  ▼
DeepSeek Harness · 127.0.0.1:3080（只监听本机）
```

Harness 只绑定 `127.0.0.1:3080`，Remote Host 只绑定 `127.0.0.1:3090`——两层都不对外网开放。手机流量通过 Tailscale Serve 进来，Tailscale Serve 做 TLS 终止后打到本机 3090。

**不用 Tailscale Funnel**——Funnel 是把服务暴露给公网的，这里用的是 Serve，只在你的 tailnet 内可见。

---

## 手机能做什么

**任务控制**：
- 在已配置的任意工作区发起新任务
- 选择工作模式（auto / manual）、模型、思考强度
- 实时查看 Agent 执行过程和对话内容
- 从任务输入框追加新指令或追问
- 继续既有任务（任务列表 + 搜索）

**审批和问答**：
- 回答 Agent 在执行中提出的问题
- 处理一次性权限请求——允许一次 / 拒绝

**PWA**：添加到主屏幕，网络断开后重连自动恢复，接近原生 App 体验。

---

## 手机不能做什么（设计决策）

Remote API 是白名单制的，以下操作只在 Mac 本机可用，手机端根本没有调用入口：

- 读取或修改 DeepSeek API 凭据
- 修改 Harness 设置
- 本地文件选择和打开
- 编辑 Agent Preset

**DeepSeek API 凭据由 Harness 自己管理，DSH Remote 不读取它。** 这个边界是代码层面强制的，不是文档承诺。

Remote Host 的设备私钥保存在 macOS Keychain，不存在项目目录里。

---

## 身份验证：靠 Tailscale，不靠 Header

DSH Remote 从可信的本机代理连接解析真实 Tailscale 对端身份——不信任浏览器提交的身份 Header，因为 Header 可以伪造。

默认情况下，加入同一 tailnet 的设备都可以访问。如果只想让指定手机能连：

```bash
# 查找手机的 Tailscale 节点 ID
tailscale status

# 加入白名单
macos/launch-agent/devices.sh add <tailscale-device-id>

# 查看白名单
macos/launch-agent/devices.sh list
```

白名单脚本有一个保护：拒绝删除最后一个允许设备——防止一次误操作意外把访问范围扩大到整个 tailnet。

---

## 安装

需要：一台已配置 Harness 的 Mac，Mac 和手机都装 Tailscale 并登录同一 tailnet，且开启 MagicDNS。

```bash
git clone https://github.com/Zouu-X/dsh_remote.git dsh-remote
cd dsh-remote
./macos/launch-agent/setup.sh
```

安装脚本检查环境、安装依赖、构建手机端、安装 LaunchAgent、配置 Tailscale Serve，最后打印手机访问地址。缺少 Node.js 或 Tailscale 且有 Homebrew 时会提示标准安装路径。

安装完成后，按脚本打印的命令启动 Harness：

```bash
npx @deepseek-ai/dsh web --trusted-host <你的-Mac>.<你的-tailnet>.ts.net
```

Harness 跑起来，DSH Remote 自动上线。Harness 停，Remote Host 随之退出。

手机打开脚本打印的地址，加到主屏幕即可。

---

## LaunchAgent：开机自启，不用手动管理

安装后会注册一个用户级 macOS LaunchAgent，登录时自动启动并等待 Harness。不用每次开机手动跑命令。

**唤醒策略**：默认 `auto`——有 Harness Session 运行时阻止 Mac 休眠，没有 Session 时不干预。

常用诊断：

```bash
# 确认两个本地服务在监听
lsof -nP -iTCP:3080 -sTCP:LISTEN
lsof -nP -iTCP:3090 -sTCP:LISTEN

# 检查 Remote Host 健康
curl http://127.0.0.1:3090/api/health

# 查看 Tailscale Serve 状态
tailscale serve status

# 跟踪日志
tail -f ~/.dsh-remote/logs/remote-host.err.log
```

卸载：`macos/launch-agent/uninstall.sh`

---

## 包结构（TypeScript monorepo）

| 包 | 职责 |
|----|------|
| `apps/mobile-web` | React/Vite 手机 PWA |
| `packages/remote-protocol` | 版本化 RPC 与事件信封 |
| `packages/remote-domain` | Host/工作区/任务/审批/问题/事件历史模型 |
| `packages/remote-client` | `AgentHostTransport`，tailnet 直连传输 |
| `packages/remote-host` | Loopback HTTP/WS Host，身份边界 |
| `packages/auth-core` | Principal/角色/能力/远程方法策略 |
| `packages/adapter-deepseek` | **唯一**使用 Harness 线协议的包 |
| `macos/launch-agent` | 安装、LaunchAgent 模板、访问管理、诊断 |

设计上只有 `adapter-deepseek` 依赖 Harness 内部协议——Harness 升级时只需要改这一个包，其余层不受影响。

---

## 拆解结论

DSH Remote 解决的问题很具体：Mac 做 Agent 主机，手机做随身控制面板，私网隔离，不上公网。

这个方向上设计做得比较干净的地方：白名单 API 边界（凭据不可远程读）、Tailscale 对端身份验证（不信任 Header）、LaunchAgent 生命周期绑定 Harness（Harness 停了自动退出）。

7 stars，刚创建不满一个月，MIT 开源，TypeScript。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: Zouu-X/dsh_remote
> GitHub: https://github.com/Zouu-X/dsh_remote
> License: MIT | Stars: 7 | Language: TypeScript
> Independent community project, not affiliated with or endorsed by DeepSeek

---

DeepSeek Harness is a desktop-bound Agent runtime — launching tasks, watching output, handling approvals all require sitting at your computer.

DSH Remote solves one specific scenario: **Harness is running on a Mac at home, you're out, and you want to control it from your phone.**

No public internet exposure. No cloud relay. Just your private Tailscale network.

---

## Architecture: Three Layers of Isolation

```text
Mobile PWA
  │  HTTPS/WSS over private Tailscale network
  ▼
Tailscale Serve on Mac (TLS termination)
  │
  ▼
Remote Host · 127.0.0.1:3090 (loopback only)
  │  Identity resolution + API allowlist filtering
  ▼
DeepSeek Harness · 127.0.0.1:3080 (loopback only)
```

Harness binds only to `127.0.0.1:3080`, Remote Host binds only to `127.0.0.1:3090` — neither is reachable from outside the machine. Mobile traffic enters through Tailscale Serve, which terminates TLS before forwarding to port 3090 on the same machine.

**Tailscale Serve, not Funnel** — Funnel exposes services to the public internet; Serve keeps everything inside your tailnet.

---

## What You Can Do From Your Phone

**Task control:**
- Launch new tasks in any configured workspace
- Choose agent mode (auto / manual), model, thinking intensity
- Watch Agent execution and conversation in real time
- Queue new instructions or follow-ups from the task input box
- Continue existing tasks (task list + search)

**Approvals and questions:**
- Answer questions the Agent asks during execution
- Handle one-time permission requests — allow once or deny

**PWA:** Add to home screen. Auto-reconnects after network drops. Near-native app experience.

---

## What Your Phone Can't Do (A Design Choice)

The Remote API is an allowlist. The following operations have no remote entry point at all:

- Reading or modifying DeepSeek API credentials
- Changing Harness settings
- Local file selection and opening
- Editing Agent Presets

**DeepSeek API credentials are managed by Harness itself; DSH Remote never reads them.** This boundary is enforced at the code level, not just documented.

The Remote Host's device private key lives in macOS Keychain — not in the project directory.

---

## Identity Verification: Tailscale Peer, Not Headers

DSH Remote resolves the true Tailscale peer identity from the trusted local proxy connection — it does not trust identity headers from the browser, since headers can be forged.

By default, any device authenticated in the same tailnet can connect. To restrict access to a specific phone:

```bash
# Find your phone's Tailscale node ID
tailscale status

# Add to allowlist
macos/launch-agent/devices.sh add <tailscale-device-id>

# View current allowlist
macos/launch-agent/devices.sh list
```

The allowlist script refuses to remove the last allowed device — preventing a single edit from accidentally opening access to the entire tailnet.

---

## Installation

Requirements: a Mac with Harness configured, Tailscale installed and signed into the same tailnet on both Mac and phone, MagicDNS enabled.

```bash
git clone https://github.com/Zouu-X/dsh_remote.git dsh-remote
cd dsh-remote
./macos/launch-agent/setup.sh
```

The setup script checks the environment, installs dependencies, builds the mobile PWA, installs the LaunchAgent, configures Tailscale Serve, and prints the phone's access URL. If Node.js or Tailscale is missing and Homebrew is present, it suggests the standard install path.

After setup, start Harness with the command the script prints:

```bash
npx @deepseek-ai/dsh web --trusted-host <your-mac>.<your-tailnet>.ts.net
```

Once Harness is running, DSH Remote comes online. When Harness stops, Remote Host exits too.

Open the printed URL on your phone and add it to the home screen.

---

## LaunchAgent: Auto-Start, No Manual Management

Installation registers a user-level macOS LaunchAgent that starts at login and waits for Harness. No need to manually launch anything after reboot.

**Wake strategy:** defaults to `auto` — prevents Mac sleep while a Harness Session is active; leaves sleep behavior alone when there's no active session.

Useful diagnostics:

```bash
# Confirm both local services are listening
lsof -nP -iTCP:3080 -sTCP:LISTEN
lsof -nP -iTCP:3090 -sTCP:LISTEN

# Check Remote Host health
curl http://127.0.0.1:3090/api/health

# Check Tailscale Serve config
tailscale serve status

# Stream logs
tail -f ~/.dsh-remote/logs/remote-host.err.log
```

Uninstall: `macos/launch-agent/uninstall.sh`

---

## Package Structure (TypeScript Monorepo)

| Package | Role |
|---------|------|
| `apps/mobile-web` | React/Vite mobile PWA |
| `packages/remote-protocol` | Versioned RPC and event envelopes |
| `packages/remote-domain` | Host/workspace/session/approval/question/event models |
| `packages/remote-client` | `AgentHostTransport`, tailnet direct transport |
| `packages/remote-host` | Loopback HTTP/WS Host, identity boundary |
| `packages/auth-core` | Principal/role/capability/remote method policy |
| `packages/adapter-deepseek` | **Only** package using the Harness wire protocol |
| `macos/launch-agent` | Setup, LaunchAgent template, access management, diagnostics |

The design isolates all Harness protocol dependencies in `adapter-deepseek` alone — when Harness upgrades, only that one package needs updating. The rest of the stack doesn't care.

---

## Teardown Summary

DSH Remote solves a specific problem cleanly: Mac as Agent host, phone as mobile control panel, private-network-only access.

What's done well design-wise: the allowlist API boundary (credentials can't be read remotely), Tailscale peer identity verification (headers not trusted), and the LaunchAgent lifecycle tied to Harness (Remote Host exits when Harness stops).

7 stars, created less than a month ago, MIT open-source, TypeScript.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
