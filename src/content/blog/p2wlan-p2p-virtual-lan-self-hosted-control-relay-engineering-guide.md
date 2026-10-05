---
title: "P2WLAN 自托管部署工程指南：Control + Relay 全栈搭建，从零到联机"
titleEn: "P2WLAN Self-Hosted Deployment Engineering Guide: Full-Stack Control + Relay Setup from Scratch"
description: "yhan-sun/p2wlan，MIT，1799 stars，Rust + Flutter + Go，2026-07-16。跨平台 P2P 虚拟局域网工具，覆盖 Windows / macOS / Linux / Android，支持 GUI 客户端与 CLI。核心：LAN Direct → IPv6/IPv4 UDP 打洞 → 加密 Relay 三级连接策略，基于 WireGuard-like Noise 数据面（X25519/ChaCha20-Poly1305/BLAKE2s）。自托管路径：Linux + systemd，安装 `p2wlan-server` 归档，`install-server.sh` 一键完成 Control + Relay 双服务，HTTPS 443 反向代理 Control，TLS 18081 接 Relay 数据连接。本文工程指导覆盖：服务器选型、端口规划、TLS、配置生成、Docker Compose 备选方案、升级与恢复、常见 NAT 穿透失败排查。典型场景：Minecraft/Terraria 联机、NAS 外网访问、跨地域开发机互联。"
descriptionEn: "yhan-sun/p2wlan, MIT, 1799 stars, Rust + Flutter + Go, 2026-07-16. Cross-platform P2P virtual LAN tool for Windows / macOS / Linux / Android, with both GUI client and CLI. Core: LAN Direct → IPv6/IPv4 UDP hole-punching → Encrypted Relay three-tier connection strategy, WireGuard-like Noise data plane (X25519/ChaCha20-Poly1305/BLAKE2s). Self-hosting path: Linux + systemd, install server-vX.Y.Z archive, install-server.sh sets up both Control and Relay services; HTTPS 443 reverses-proxies Control, TLS 18081 handles Relay data connections. Engineering guide covers: server sizing, port layout, TLS setup, config generation, Docker Compose alternative, upgrade/restore procedures, common NAT traversal failure diagnostics. Typical use cases: Minecraft/Terraria LAN play, NAS remote access, cross-region dev machine networking."
pubDate: 2026-10-05
heroImage: "../../assets/images/p2wlan-p2p-virtual-lan-self-hosted-control-relay-engineering-guide-banner.jpg"
category: "Tech-Experiment"
tags: ["组网", "P2P", "自托管", "NAT穿透", "VPN", "开源工具", "Rust"]
lang: "zh-CN"
wechatTitle: "P2WLAN：P2P虚拟局域网自托管工程指南"
wechatDigest: "MIT 1799星；Rust+Go+Flutter；NAT穿透直连优先；自托管Control+Relay；游戏/NAS/远程开发"
---

把异地的设备组成一个局域网，方法有很多，但多数方案要么需要配公网 IP，要么依赖商业服务的控制面，要么在两端都是对称 NAT 时无法直连。P2WLAN 的出发点是：优先建立点对点直连，直连真的不行时再走加密中继，并且把控制面（Control）和中继（Relay）都设计成可以自己部署的。

GitHub: https://github.com/yhan-sun/p2wlan | ⭐ 1799 | MIT | Rust + Go + Flutter | 2026-07-16

---

## 架构概览

P2WLAN 把网络分成三个平面：

| 平面 | 实现 | 职责 |
|------|------|------|
| 控制面 Control | Go + SQLite | 身份认证、设备注册、虚拟 IP 分配、凭据管理、信令 |
| 数据面 Daemon | Rust | TUN 虚拟网卡、路由、NAT 穿透、加密会话、Relay 回退 |
| 中继 Relay | Go | 密文转发（仅在直连不可用时参与） |

GUI 客户端用 Flutter 开发，覆盖 Windows / macOS / Linux / Android。Linux 无桌面环境可用 CLI 包。

连接策略按优先级：

```
LAN Direct → IPv6 Direct → IPv4 UDP 打洞 → 加密 Relay
```

同一局域网内的设备直接通信，不走任何服务器。跨网络时先尝试 IPv6 和 UDP 打洞；打洞受阻时自动使用端到端加密的 Relay——业务流量始终加密，Relay 只能看到密文。

数据面使用 WireGuard-like Noise 协议（X25519 密钥交换、ChaCha20-Poly1305 加密、BLAKE2s 哈希），**不是官方 WireGuard 实现，不声明 WireGuard 互操作兼容**。

---

## 自托管决策树

在开始部署前，先确认你需要什么：

**只是联机用**：如果你有朋友愿意部署 Control，直接用他的地址即可，不需要自己部署服务器。

**需要自己控制数据**：部署 Control + Relay，服务器、带宽和域名由自己承担。

**硬件要求**：Control + Relay 对资源要求不高，1 核 1 GB VPS 即可，建议 2 核 2 GB（SQLite 写入敏感延迟）。带宽决定 Relay 吞吐上限——如果多数连接能直连，Relay 只是备用，带宽压力很小。

**操作系统**：公开支持和 CI 验证路径是 **Ubuntu 22.04 + systemd**。Ubuntu 20.04 可启动服务端二进制，但完整 systemd 管理链路未在 CI 端到端验收；其他发行版能跑但不在官方兼容矩阵里。

---

## 服务器端口规划

部署前先确认服务器防火墙和云安全组允许以下端口：

| 端口 | 协议 | 用途 | 公网开放 |
|------|------|------|---------|
| 443 | TCP（HTTPS/WSS）| Control API + WebSocket + Admin 管理台 | 是 |
| 18081 | TCP（TLS）| Relay 数据连接 | 是 |
| 80 | TCP（HTTP）| Let's Encrypt ACME 或重定向到 443 | 可选 |
| 18080 | TCP（HTTP）| Control 内部监听（loopback only）| 否 |
| 18082 | TCP（HTTP）| Relay metrics + readyz（loopback only）| 否 |

Control 默认只监听 loopback（127.0.0.1:18080），公网入口必须通过反向代理（nginx/Caddy 等）暴露，代理需保留 `WebSocket Upgrade`。Relay 直接监听 TLS 18081，不经过反向代理。

---

## 安装步骤

### 1. 下载服务端归档

服务端归档使用独立的 `server-vX.Y.Z` Release 标签（不是客户端标签）。从 GitHub Releases 下载对应架构的归档和 checksum：

```bash
# 将 vX.Y.Z 替换为实际版本号，例如 server-v0.8.1
SERVER_VERSION=server-vX.Y.Z
wget "https://github.com/yhan-sun/p2wlan/releases/download/${SERVER_VERSION}/p2wlan-server-linux-amd64.tar.gz"
wget "https://github.com/yhan-sun/p2wlan/releases/download/${SERVER_VERSION}/p2wlan-server-linux-amd64.tar.gz.sha256"
```

### 2. 校验归档完整性

```bash
sha256sum -c p2wlan-server-linux-amd64.tar.gz.sha256
```

输出 `OK` 才继续。

### 3. 解压并安装

```bash
tar -xzf p2wlan-server-linux-amd64.tar.gz
sudo ./install-server.sh --archive p2wlan-server-linux-amd64.tar.gz --role all
```

`--role all` 同时安装 Control 和 Relay。也可以分机部署：`--role control` 或 `--role relay`。

安装脚本会：
- 创建 `p2wlan` 系统用户
- 安装 `p2wlan-control`、`p2wlan-relay`、`p2wlan-config`、`p2wlan-db` 等二进制
- 生成 systemd 服务文件
- 通过 `p2wlan-server init` 生成 JWT_SECRET、Relay 凭据、CONTROL_ADMIN_TOKEN 并写入受保护的 `control.env`

安装不会自动启动服务，也不需要在服务器上预装 Go 或 Node.js。

### 4. 配置域名与 TLS

编辑配置文件（安装后位于 `/etc/p2wlan/` 或安装脚本提示的路径），填入：
- Control 的 HTTPS 域名（如 `control.example.com`）
- Relay 的 TLS 域名（可以与 Control 同域或子域）
- TLS 证书和私钥路径

```bash
# 生成配置模板（在新目录执行）
sudo p2wlan-config --control-domain control.example.com \
                   --relay-domain relay.example.com \
                   --output /etc/p2wlan/
```

TLS 证书推荐用 Let's Encrypt / Certbot 获取，Relay 也需要证书（不走反向代理，TLS 在 Relay 进程内终止）。

### 5. 配置反向代理（nginx 示例）

Control 监听 loopback，需要通过 nginx 或 Caddy 暴露到 443：

```nginx
server {
    listen 443 ssl;
    server_name control.example.com;
    
    ssl_certificate /etc/letsencrypt/live/control.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/control.example.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # 保留 WebSocket
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**必须保留 `WebSocket Upgrade` 头**，否则客户端信令连接会失败。

### 6. 启动服务

```bash
sudo systemctl enable --now p2wlan-control
sudo systemctl enable --now p2wlan-relay
```

### 7. 验证

```bash
sudo p2wlan-server verify --service all   # 检查发布归档和版本
sudo p2wlan-server check  --service all   # 检查健康端点
sudo p2wlan-server doctor --service all   # 完整检查：systemd、凭据、TLS、备份、磁盘
```

---

## Docker Compose 方案

如果不想管 systemd，可以用 Compose。官方提供 Compose 配置，Control 默认发布到 loopback，容器以非 root、只读根文件系统运行。

关键注意事项：
- **生产环境必须用固定镜像摘要**（`image: xxx@sha256:...`），不能用 `latest` 或可变标签
- Compose 镜像包含 `p2wlan-db`，可在挂载的数据卷上生成 SQLite 快照
- 恢复流程：停止 Control → 用同一镜像的 `p2wlan-db --verify` 验证快照 → 启动并检查服务
- `p2wlan-server backup/restore` 命令只适用于 systemd 安装路径，不适用于 Compose 容器

---

## 客户端配置：指向自托管 Control

服务器部署完成后，客户端在登录页的"高级选项 → 自托管服务器"中填写 Control 地址：

```
https://control.example.com
```

CLI 配置：

```bash
p2wlan config set control https://control.example.com
p2wlan login -u your-username
p2wlan up
p2wlan status
```

需要互联的所有设备必须指向同一个 Control。不同账号之间通过房间互联。

---

## 房间式联机：工程视角

P2WLAN 的"房间"是一个独立的虚拟网络边界，有单独的虚拟 IP 段，不与个人网络混用。这个设计对以下场景很有用：

- **游戏联机**：为一次 Minecraft 存档创建一个房间，游戏结束后房间可以删除或保留
- **临时协作**：把外部协作者加入临时房间，访问特定服务，不需要把他们加入整个网络
- **隔离测试**：开发环境和生产设备分开房间，避免路由冲突

房间虚拟 IP 与个人网络虚拟 IP 是独立的——`p2wlan up` 启动个人网络，`p2wlan room connect <id>` 加入房间网络，两者可以同时运行。

---

## NAT 穿透失败排查

P2WLAN 对 NAT 类型的处理策略：不会因为"对称 NAT"标签就放弃直连，而是按实测端口规律选择探测策略。常见失败场景：

| 现象 | 可能原因 | 检查点 |
|------|----------|--------|
| 两端一直走 Relay | 双端对称 NAT + 随机端口映射 + 严格过滤 | 用 `p2wlan status --json` 查路径，确认是否触发了预期行为 |
| 连接超时 | Control 的 WebSocket 反向代理配置错误 | 检查 nginx 是否加了 `Upgrade: websocket` 头 |
| Relay 不可达 | TLS 18081 端口被防火墙拦截 | 从客户端 telnet/nc 测试 18081 端口 |
| 校园网/CGNAT | IPv4 UDP 完全被阻断 | 确认是否有 IPv6 地址，优先用 IPv6 直连绕过 IPv4 NAT |

诊断工具：

```bash
p2wlan doctor          # 全面检查
p2wlan route verify    # 路径验证
p2wlan logs -f         # 实时日志
p2wlan support-bundle  # 生成本地诊断包（不加 --upload 不发送）
```

---

## 升级步骤（systemd 路径）

```bash
# 1. 下载新版归档和 checksum
# 2. 校验
sha256sum -c p2wlan-server-linux-amd64.tar.gz.sha256
# 3. 升级（会自动备份当前版本）
sudo p2wlan-server upgrade --archive p2wlan-server-linux-amd64.tar.gz
# 4. 验证
sudo p2wlan-server verify --service all
sudo p2wlan-server doctor --service all
```

升级前建议先备份 SQLite 数据库：

```bash
sudo p2wlan-server backup --output /path/to/backup/
```

---

## 已知边界

**Ubuntu 20.04 的完整兼容性未验证**：CI 只验证了静态二进制能启动，完整 systemd + 网络 + 业务链路没有端到端验收。生产部署优先 Ubuntu 22.04。

**管理台当前只读**：`/admin/` 管理台提供账号、设备、连接状态查看，不提供删除设备、修改房间等写操作。

**分机部署 Control 和 Relay 需额外配置**：撤权 feed 使用独立的 HTTPS + Bearer token，凭据不能与 JWT_SECRET 复用，需按[配置参考](https://github.com/yhan-sun/p2wlan/blob/main/docs/reference/configuration.md)手动配置。

**Relay 带宽由部署者承担**：如果直连成功率低（例如企业网络 UDP 被大量阻断），Relay 会承接主要流量，带宽成本需提前规划。

---

> MIT 开源。自托管部署的 Control/Relay 服务器、带宽和域名费用由部署者自行承担。服务端公开支持 Ubuntu 22.04 + systemd，其他平台需自行验证。开源仅供学习参考。

---

<!--EN-->

## P2WLAN Self-Hosted Deployment Engineering Guide

P2WLAN is a cross-platform P2P virtual LAN tool: LAN Direct → IPv6/IPv4 UDP hole-punching → Encrypted Relay, with Control and Relay both open-source and self-hostable.

GitHub: https://github.com/yhan-sun/p2wlan | ⭐ 1799 | MIT | Rust + Go + Flutter | 2026-07-16

---

### Architecture

**Control Plane** (Go + SQLite): auth, device registration, virtual IP assignment, signaling  
**Data Plane / Daemon** (Rust): TUN interface, routing, NAT traversal, encrypted sessions, Relay fallback  
**Relay** (Go): ciphertext forwarding (only when direct connection unavailable)  
**GUI** (Flutter): Windows/macOS/Linux/Android + CLI for headless

Connection priority: `LAN Direct → IPv6 Direct → IPv4 UDP punch → Encrypted Relay`

WireGuard-like Noise protocol (X25519, ChaCha20-Poly1305, BLAKE2s). Not official WireGuard, no interoperability claimed.

---

### Port Layout

| Port | Protocol | Use | Public |
|------|----------|-----|--------|
| 443 | HTTPS/WSS | Control API + WebSocket + Admin UI | Yes |
| 18081 | TLS | Relay data connections | Yes |
| 18080 | HTTP | Control internal (loopback only) | No |
| 18082 | HTTP | Relay metrics + readyz (loopback only) | No |

Control only listens on loopback; expose via nginx/Caddy with `WebSocket Upgrade` headers preserved. Relay terminates TLS directly on 18081.

---

### Install

```bash
# 1. Download server archive + checksum from server-vX.Y.Z release
sha256sum -c p2wlan-server-linux-amd64.tar.gz.sha256
sudo ./install-server.sh --archive p2wlan-server-linux-amd64.tar.gz --role all
sudo p2wlan-server verify --service all
```

The script creates a `p2wlan` system user, installs binaries, generates systemd units, and runs `p2wlan-server init` to generate JWT_SECRET, Relay credentials, and CONTROL_ADMIN_TOKEN into a protected `control.env`. No Go or Node.js needed on the server.

---

### nginx Reverse Proxy (minimal)

```nginx
server {
    listen 443 ssl;
    server_name control.example.com;
    # TLS config...
    location / {
        proxy_pass http://127.0.0.1:18080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # Required: WebSocket
        proxy_set_header Host $host;
    }
}
```

---

### Start Services

```bash
sudo systemctl enable --now p2wlan-control
sudo systemctl enable --now p2wlan-relay
sudo p2wlan-server doctor --service all
```

---

### Client Configuration

In the login UI under Advanced → Self-hosted server:
```
https://control.example.com
```

CLI: `p2wlan config set control https://control.example.com`

All devices that need to communicate must point to the same Control. Cross-account networking happens via rooms.

---

### Room-Based Networking

Rooms are isolated virtual networks with independent IP ranges, separate from the personal network. Use cases: game sessions (Minecraft/Terraria), temporary collaboration access, staging/production isolation.

`p2wlan up` starts the personal network. `p2wlan room connect <id>` joins a room network. Both can run simultaneously.

---

### NAT Traversal Failure Diagnostics

P2WLAN doesn't give up on direct connection just because one or both sides have symmetric NAT — it selects port prediction, fixed anchor, or birthday probing strategies based on measured port behavior. When direct truly fails, it falls back to Relay automatically.

Key diagnostics:
- `p2wlan status --json` — see current path type
- `p2wlan doctor` — comprehensive health check
- `p2wlan route verify` — path verification
- `p2wlan logs -f` — live log stream

Campus networks and CGNAT that block UDP entirely: check for IPv6 availability and force IPv6 direct connection to bypass IPv4 NAT entirely.

---

### Known Limits

Ubuntu 20.04 static binary compatibility only (full systemd chain not end-to-end validated in CI). Admin UI is read-only currently. Split Control/Relay deployment requires manual revocation feed configuration. Relay bandwidth cost falls on the deployer.

---

> MIT. Self-hosted Control/Relay server, bandwidth, and domain costs are the deployer's responsibility. Officially supported: Ubuntu 22.04 + systemd. For technical reference only.
