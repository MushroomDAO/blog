---
title: "dsh-plugin-mobile-gateway：给 DeepSeek Harness 加上移动端，手机扫码就能用，Tailscale 一行命令搞定远程"
titleEn: "dsh-plugin-mobile-gateway: Add Mobile Access to DeepSeek Harness — QR Pairing, Tailscale One-liner for Remote"
description: "Clarklevis1995/dsh-plugin-mobile-gateway，MIT 开源，JavaScript 插件，给 DeepSeek Harness (DSH) 增加 WebSocket 移动网关。支持局域网直连、Linux 公网一键 TLS、Tailscale 远程接入三种部署方式。配套 iOS 17+ SwiftUI 原生客户端，双向同步会话、实时流、Human-in-the-loop、文件传输。适配 DSH 0.1.5-rc.2 / Session format 3。"
descriptionEn: "Clarklevis1995/dsh-plugin-mobile-gateway, MIT open source, JavaScript plugin that adds a WebSocket mobile gateway to DeepSeek Harness (DSH). Supports LAN direct connect, Linux public-IP one-click TLS, and Tailscale remote access. Companion iOS 17+ SwiftUI native client with two-way session sync, live streaming, human-in-the-loop, and file transfer. Targets DSH 0.1.5-rc.2 / Session format 3."
pubDate: "2026-09-16"
updatedDate: "2026-09-16"
category: "Tech-Experiment"
tags: ["open-source", "DeepSeek-Harness", "mobile", "WebSocket", "iOS", "plugin", "Tailscale", "MIT", "JavaScript"]
heroImage: "../../assets/images/dsh-plugin-mobile-gateway-websocket-ios-deepseek-harness-mobile-banner.jpg"
---

> 📌 开源仓库：https://github.com/Clarklevis1995/dsh-plugin-mobile-gateway
> 配套 iOS 客户端：https://github.com/Clarklevis1995/dsh-mobile
> License：MIT | Language：JavaScript | 适配：DSH 0.1.5-rc.2

---

DeepSeek Harness（DSH）本是桌面端 CLI + WebUI 的工作流，`dsh-plugin-mobile-gateway` 给它加了一扇门：手机扫一下二维码，从此 iPhone 也能接上你的 DSH 会话，发消息、看实时流、做 Human-in-the-loop 审批、传文件——**不用 VPN，不用配服务器，局域网里插上就能用**。

配套的 iOS 客户端 `dsh-mobile` 是 SwiftUI 原生实现，支持 iOS 17+，已上 TestFlight 公测。

---

## 能干什么

插件安装后，DSH WebUI 左侧边栏新增"移动设备"入口，功能列表：

- **会话与实时流**：和 WebUI 一样看到实时 token 输出，包括 Agent 执行轨迹
- **双向同步**：会话存档、重命名、排队消息的编辑/删除/Steer，手机端操作立刻同步到桌面
- **停止并稍后继续**：在手机上停止当前生成，回到桌面或在手机上继续
- **Human-in-the-loop**：Agent 等待人工确认时，手机端可以批准或拒绝
- **任务列表与 Goal 同步**：查看和管理当前运行的任务
- **图片与文件传输**：从手机上传图片或文件给 Agent
- **服务端驱动菜单**：命令、技能、模型和权限菜单由网关配置下发

---

## 三种部署方式

### 1. 局域网（最简单）

电脑和 iPhone 在同一个 WiFi 下，安装插件，WebUI 里把"网关运行模式"设为"常驻开启"，扫码配对，完成。

```bash
dsh plugin --profile web add dsh-plugin-mobile-gateway@latest
dsh web
```

WebSocket 地址：`ws://<电脑局域网 IP>:3081/ws/mobile`

防火墙只需放行私有网络的 TCP 3081，**不要暴露到公网**。

### 2. Linux 公网服务器（一键 TLS）

带固定公网 IPv4 的 Ubuntu/Debian 服务器，一行命令搞定插件 + Nginx + TLS 证书：

```bash
npm_config_registry=https://registry.npmjs.org \
npx --yes dsh-plugin-mobile-gateway@latest init
```

`init` 会安装插件、用 Certbot 签 TLS 证书、配置 Nginx 反代，再到 WebUI 填一下公网 IPv4，`wss://<公网IP>/ws/mobile` 就可以用了。云安全组放行 TCP 80 和 443，不要暴露 3081 或 DSH WebUI 端口。

### 3. 家用电脑远程（Tailscale）

家用电脑没有固定公网 IP，推荐 Tailscale：

```bash
tailscale serve --bg 3081
```

生成 `wss://<设备名>.<tailnet>.ts.net` 地址，填入 WebUI 的"WebSocket 地址"后扫码。Tailscale Serve 自动 HTTPS，只允许同一 Tailnet 内的设备连接。临时调试也可以用 Cloudflare Quick Tunnel，但地址每次会变。

---

## 协议设计

插件维护独立协议 `dsh-mobile-v1`，不复用 DSH 内部 Remote 协议。`hello.protocol = 3` 握手，实时 token 通过独立 `assistant-stream` 帧推送（客户端显式订阅 `assistantStream: true`），不占用持久事件的 `seq`；普通 `event` 只携带持久消息。

历史响应带 `historyFormatVersion` 和 `cursor`，分页请求需携带 `historyFormatVersion: 3`，格式变化时客户端需清理本地历史缓存。

---

## 网关身份与状态持久化

每个网关实例有一个随机 UUID v4 身份，保存在 `~/.dsh/mobile-gateway-devices.json.gateway.json`，权限 0600，原子替换写入。**升级或迁移机器时必须一并保留这个文件**；克隆为新实例时不要复制，让它自己生成新身份重新配对。

三种运行模式：

| 模式 | 行为 |
|------|------|
| 关闭 | 立即断开移动连接，重启后仍关闭 |
| 临时开启 | 5 分钟无成功连接则自动关闭（可配置 30s–30min） |
| 常驻开启 | 无无人连接超时计时器 |

---

## 常见问题速查

| 现象 | 处理方式 |
|------|----------|
| WebUI 没有"移动设备"入口 | 确认安装在 `web` profile，完整重启 `dsh web` |
| iOS 返回 503 | WebUI 里开启"允许移动设备连接" |
| iOS 返回 401 | WebUI 里重新生成二维码并配对（二维码只能用一次，5 分钟过期） |
| Linux 公网连接超时 | 检查云安全组是否放行 TCP 80/443 |
| 查看服务端日志 | `tail -f /tmp/mobile-gateway.log` |

---

## 当前限制

- **仅适配 DSH 0.1.5-rc.2**，不再兼容更早版本；Session format 3 之前的客户端需要更新
- iOS 客户端多网关管理仍需按文档实现，当前源码尚未发布新 npm 版本
- 部分功能（Session Agent Preset、空白 Session 创建）在 App 端尚未合并
- Linux 公网一键部署仅支持 Ubuntu/Debian，不支持 CentOS
- `dsh-mobile` 仅支持 iOS 17+，没有 Android 版

---

## 总结

如果你已经在用 DeepSeek Harness，这个插件的价值很直接：把"只能在桌面用"变成"手机也能用"，而且三种部署方式覆盖了局域网家用、服务器公网、Tailscale 内网穿透三个最常见的场景，不需要额外的反代知识。配套 iOS 客户端功能完整，不是"只能看"的只读版。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: https://github.com/Clarklevis1995/dsh-plugin-mobile-gateway
> iOS Client: https://github.com/Clarklevis1995/dsh-mobile
> License: MIT | Language: JavaScript | Targets: DSH 0.1.5-rc.2

---

DeepSeek Harness (DSH) is a desktop CLI + WebUI workflow tool. `dsh-plugin-mobile-gateway` adds a door: scan a QR code from your iPhone, and you're connected to your DSH session — send messages, watch live token streams, approve human-in-the-loop checkpoints, transfer files. **No VPN, no server config needed for LAN use.** Just install and go.

The companion iOS client `dsh-mobile` is a native SwiftUI app targeting iOS 17+, currently in TestFlight public beta.

---

## What It Does

After install, the DSH WebUI left sidebar gains a "Mobile Devices" entry. Feature list:

- **Sessions and live streaming**: real-time token output and Agent execution traces, same as WebUI
- **Two-way sync**: session archive, rename, queued message edit/delete/Steer — actions sync immediately across devices
- **Stop and resume**: pause generation from mobile, continue on desktop or phone
- **Human-in-the-loop**: approve or reject Agent checkpoints from your phone
- **Task list and Goal sync**: view and manage running tasks
- **File and image transfer**: upload files or images from your phone to the Agent
- **Server-driven menus**: commands, skills, models, and permission menus pushed from gateway config

---

## Three Deployment Modes

### 1. LAN (Simplest)

Same WiFi for your computer and iPhone — install the plugin, set gateway mode to "persistent" in WebUI, scan the QR code, done.

```bash
dsh plugin --profile web add dsh-plugin-mobile-gateway@latest
dsh web
```

WebSocket address: `ws://<LAN IP>:3081/ws/mobile`

Only allow TCP 3081 from private networks. **Do not expose to the public internet.**

### 2. Linux Public Server (One-click TLS)

For a fixed-IP Ubuntu/Debian server, one command handles plugin + Nginx + TLS:

```bash
npm_config_registry=https://registry.npmjs.org \
npx --yes dsh-plugin-mobile-gateway@latest init
```

`init` installs the plugin, runs Certbot for TLS, configures Nginx reverse proxy. Enter your public IPv4 in the WebUI, and `wss://<public-IP>/ws/mobile` is ready. Open TCP 80 and 443 in your cloud security group; don't expose 3081 or the DSH WebUI port.

### 3. Home Computer Remote (Tailscale)

No fixed public IP at home? Tailscale:

```bash
tailscale serve --bg 3081
```

Get a `wss://<device>.<tailnet>.ts.net` address, enter it in the WebUI's "WebSocket Address" field, then scan to pair. Tailscale Serve provides automatic HTTPS and limits access to the same Tailnet. Cloudflare Quick Tunnel also works for temporary debugging, though the address changes each time.

---

## Protocol Design

The plugin maintains the `dsh-mobile-v1` protocol independently from DSH's internal Remote protocol. Handshake uses `hello.protocol = 3`. Live tokens are pushed as standalone `assistant-stream` frames (client subscribes with `assistantStream: true`), separate from the persistent event `seq`. Regular `event` frames carry only persistent messages.

History responses include `historyFormatVersion` and `cursor`. Pagination requests must include `historyFormatVersion: 3`; clients should clear local history cache on format changes.

---

## Gateway Identity and State Persistence

Each gateway instance gets a random UUID v4 identity stored at `~/.dsh/mobile-gateway-devices.json.gateway.json`, permissions 0600, atomic write. **Carry this file when upgrading or migrating machines.** When cloning as a new independent gateway, don't copy it — let the new instance generate fresh identity and re-pair.

Three gateway modes:

| Mode | Behavior |
|------|----------|
| Closed | Disconnect immediately; stays closed after restart |
| Temporary | Auto-close after 5 min with no successful connection (configurable 30s–30min) |
| Persistent | No idle timeout |

---

## Quick Troubleshooting

| Symptom | Fix |
|---------|-----|
| No "Mobile Devices" in WebUI | Confirm install used `web` profile; fully restart `dsh web` |
| iOS returns 503 | Enable "Allow mobile connections" in WebUI |
| iOS returns 401 | Regenerate QR code in WebUI (one-time use, expires in 5 min) |
| Linux public connection timeout | Check cloud security group for TCP 80/443 |
| View server logs | `tail -f /tmp/mobile-gateway.log` |

---

## Current Limitations

- **Only targets DSH 0.1.5-rc.2**; no backward compatibility with earlier versions; clients on older Session formats need updating
- iOS multi-gateway management requires following the integration docs; new npm version not yet published
- Some features (Session Agent Preset, blank Session creation) not yet merged in the App
- One-click public deployment only supports Ubuntu/Debian, not CentOS
- `dsh-mobile` is iOS 17+ only; no Android version

---

## Summary

If you're already using DeepSeek Harness, this plugin's value is straightforward: transforms "desktop only" into "works from your phone too." Three deployment paths cover the three most common scenarios — home LAN, cloud server, and Tailscale private tunnel — without requiring reverse-proxy knowledge. The companion iOS app is feature-complete, not a read-only viewer.

---

*Open-source code is for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution.
