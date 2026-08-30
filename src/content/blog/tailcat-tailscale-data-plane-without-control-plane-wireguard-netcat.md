---
title: "Tailcat：没有 Tailscale 的 Tailscale——零帐号 WireGuard 点对点加密通道"
titleEn: "Tailcat: Tailscale's Data Plane Without the Control Plane — Zero-Account WireGuard P2P Tunnels"
description: "Tailscale 官方开源 Tailcat，用 WireGuard+DERP+magicsock 实现 netcat 风格的加密点对点通道，无需帐号、无需 root、无需改路由表，一个 token 建立直连。"
descriptionEn: "Tailscale open-sources Tailcat: WireGuard+DERP+magicsock in a netcat-style CLI. No account, no root, no routing changes — one token establishes an encrypted P2P tunnel with NAT traversal."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["networking", "WireGuard", "Tailscale", "open source", "security", "tunneling", "P2P", "DevOps"]
heroImage: "../../assets/images/tailcat-tailscale-data-plane-without-control-plane-wireguard-netcat-banner.jpg"
author: "Mycelium Protocol"
---

## "没有 Tailscale 的 Tailscale"

Tailscale 在 2026 年 TailscaleUp 大会上开源了一个反直觉的工具：**Tailcat**。

它用的是 Tailscale 的数据平面（WireGuard 加密 + DERP 中继 + magicsock NAT 穿透），但**完全绕开了 Tailscale 的控制平面**。不需要 Tailscale 帐号，不需要 root 权限，不改路由表，不改 DNS，不安装任何系统服务。

一句话理解：netcat，但走 WireGuard。

```bash
# 服务端：启动，打印一个 token
$ tailcat
# 🐈 Server listening with new address: tcomFwWCCcjS5nK...

# 客户端：把 token 传过去（任何方式：微信、邮件、Slack）
$ echo "hello" | tailcat tcomFwWCCcjS5nK...
```

两端通信全程 WireGuard 加密，NAT 自动穿透，穿透失败退回 DERP 中继。

---

## 底层技术栈：Tailscale 的"半个身子"

Tailcat 复用了 Tailscale 客户端的四个核心组件，但去掉了控制平面：

| 组件 | 作用 |
|---|---|
| **WireGuard（用户态）** | 加密所有隧道流量，不使用内核 TUN/TAP，无需 root |
| **magicsock** | 多路复用 UDP 直连 + DERP 中继，STUN 端点发现 + NAT 打洞 |
| **gVisor Netstack** | 用户态 TCP/IP 栈，在进程内接受/发起 TCP 连接，无需系统网络配置 |
| **DERP 中继** | 加密中继协议，作为汇聚点和打洞失败时的后备数据路径 |

连接流程：服务端生成 WireGuard 密钥对 → 打印 token（含公钥 + DERP 区域）→ 客户端解析 token → 双方通过 DERP 交换 "Meow/Meowed" 握手 → WireGuard 建立 → UDP 打洞尝试直连 → 成功则升级为 P2P，失败则继续走 DERP。

---

## 安装

```bash
# Go（推荐）
go install github.com/tailscale/tailcat/cmd/tailcat@latest

# Nix flakes（直接运行无需安装）
nix run github:tailscale/tailcat
nix profile install github:tailscale/tailcat
```

无需其他依赖，单二进制，跨平台。

---

## 核心用法详解

### 1. stdin/stdout 管道（最简场景）

```bash
# 服务端
$ tailcat
# 🐈 Server listening with new address: tcomFwWCC...（发给对方）

# 客户端
$ cat bigfile.tar.gz | tailcat tcomFwWCC...
# 或者
$ tailcat tcomFwWCC... > received.tar.gz
```

加密的 netcat，适合临时传文件，token 用一次就扔。

### 2. 暴露本地端口

```bash
# 服务端：把本地 8080 暴露出去
$ tailcat --serve=8080
# 🐈 Server listening with new address: tcXXX...

# 客户端：通过隧道访问
$ tailcat tcXXX... 8080
GET / HTTP/1.1
...
```

`--serve=all` 暴露所有端口。不改防火墙规则，不需要公网 IP。

### 3. 免认证 SSH（调试专用）

```bash
# 服务端（Linux/macOS）
$ tailcat --serve=no-auth-ssh
# 🐈 Server listening with new address: tcXXX...

# 客户端
$ tailcat ssh tcXXX...
$ tailcat ssh tcXXX... ls -la
```

注意：这是无认证 SSH，仅适合信任网络的临时调试。如果要认证，用 `--serve=22` 代理到系统 SSH。

### 4. SOCKS5 代理

```bash
# 让客户端的流量通过服务端网络出去
$ tailcat socks tcXXX... curl http://内网地址:8081/
# token 也可以直接当 hostname 用
$ tailcat socks curl http://tcXXX...:8081/
```

### 5. 退出节点

```bash
# 服务端作为 exit node
$ tailcat --serve=exit-node
```

### 6. 连通性测试

```bash
$ tailcat ping --until-direct tcXXX...
pong in 42.1ms via DERP(sfo)
pong in 1.2ms via 203.0.113.7:41641  # 已 P2P 直连
```

---

## 密钥管理：一次性 vs 持久地址

**默认（临时密钥）**：每次启动生成新密钥，进程退出后 token 永久失效。分享出去的 token 只对这一次有效，最安全。

**持久密钥（`genkey`）**：生成并保存到磁盘，地址稳定，适合发布到 DNS：

```bash
# 服务端：生成固定区域密钥
$ tailcat genkey --fixed-region
# saved to ~/.config/tailcat/keys/default.private.json
# token: tcXXX...（可发布到 DNS TXT 记录）

# 之后每次启动自动使用保存的密钥
$ tailcat --serve=22
# 🐈 Server listening with saved key "default": tcXXX...（和上面一样）
```

**DNS TXT 记录**：把 token 发布成 TXT 记录，客户端可以用域名代替 token：

```
my-server.example.com. 300 IN TXT "tailcat=tcXXX..."
```

```bash
$ tailcat ssh my-server.example.com
```

---

## 典型落地场景

### 场景一：开发者临时协作——无账号共享本地服务

你在 localhost:3000 跑着 demo，产品想看一眼。不需要 ngrok 账号、不需要配置 Cloudflare Tunnel：

```bash
$ tailcat --serve=3000
# 把打印的 token 发给产品，他跑：
$ tailcat tcXXX... 3000
```

WireGuard 加密，token 关掉就失效，没有持久的外部暴露。

### 场景二：无公网 IP 服务器的安全 SSH 入口

NAT 后面的服务器，没有公网 IP，不想开防火墙端口。用 Tailcat 配合 DNS，做一个永久 SSH 入口：

```bash
# 服务端：生成客户端密钥（只允许特定客户端连接）
client$ tailcat genkey --client
# → nodekey:cfb6bf...（只需要把这个公钥告诉服务端）

# 服务端：只允许该客户端，发布到 DNS
server$ tailcat genkey --fixed-region
server$ tailcat --serve=22 --allow=nodekey:cfb6bf...
```

DNS TXT 记录发布后，客户端：

```bash
$ tailcat ssh my-server.example.com
```

WireGuard 在 SSH 握手之前就完成了双向认证，陌生人的连接被静默丢弃，SSH 服务器根本看不到它。

### 场景三：CI/CD 访问内网资源

GitHub Actions 需要访问内网数据库或服务，但不想在 CI 环境里装完整的 VPN 客户端：

```bash
# 内网机器：持久监听
$ tailcat --serve=5432  # PostgreSQL
# 把 token 存在 GitHub Secrets 里

# CI 里：
$ tailcat ${{ secrets.TAILCAT_TOKEN }} 5432 < query.sql
```

单二进制，3 秒内建立加密隧道，CI 任务完成后连接自动断开。

### 场景四：Go 库——在程序里嵌入 P2P 通信

```go
// 服务端
s := &tailcat.Server{
    OnTCP: func(port uint16) func(net.Conn) {
        return func(c net.Conn) {
            // 处理连接...
        }
    },
}
s.Start()
fmt.Println(s.ConnBlob())  // 打印 token

// 客户端
cl := tailcat.NewClient(tailcat.ConnBlob(os.Args[1]))
conn, _ := cl.DialTCPPort(ctx, 80)
```

不需要自己管理 STUN/ICE/DERP，Tailscale 已经把复杂的 NAT 穿透封装好了。

### 场景五：带自建 DERP 的完全私有化

不想用 Tailscale 的公共 DERP 中继（有速率限制）：

```bash
# 自建 DERP（需要有域名和 TLS 证书）
# 参考：github.com/tailscale/tailscale/tree/main/cmd/derper

# 用自建 DERP 生成密钥
$ tailcat genkey --region=derp.example.com
# token 里已经嵌入了你的 DERP 服务器信息，客户端无需配置任何额外标志
```

完全不接触 Tailscale 的任何服务器。

---

## 注意事项

- **稳定性**：CLI 标志、Go API、wire format 均可能变动，目前无 API 稳定性承诺
- **公共 DERP 中继有速率限制**，生产高流量场景建议自建
- **免认证 SSH 仅供临时调试**，不要在生产环境使用
- **token 是凭证**：持久密钥的 token 一旦泄漏，历史上所有拿到过它的人都能连上（除非用 `--allow` 限制）
- 浏览器 WebAssembly 演示：[tailscale.github.io/tailcat](https://tailscale.github.io/tailcat/)（目前只走 DERP，无直连）

---

## 总结

Tailcat 是一个精准的点状工具：它把 Tailscale 数据平面的最有价值的部分（WireGuard 加密 + 自动 NAT 穿透）提取出来，做成一个无需注册、无需安装、无需权限的 netcat 替代品。对于"临时加密通道"这个需求，它是目前最轻量的可信方案之一。

**GitHub**: [tailscale/tailcat](https://github.com/tailscale/tailcat)  
**Web Demo**: https://tailscale.github.io/tailcat/  
**DERP Map**: https://tailcat.dev/derpmap.json

<!--EN-->

## Tailcat: Tailscale's Data Plane Without the Control Plane

Tailscale open-sourced **Tailcat** at TailscaleUp 2026, and it's exactly as counterintuitive as it sounds: Tailscale's encrypted data plane — WireGuard + DERP relays + magicsock NAT traversal — running without a Tailscale account, without root, without touching your routing table or DNS.

Think of it as netcat, but over WireGuard.

```bash
# Server side: start, get a token
$ tailcat
# 🐈 Server listening with new address: tcomFwWCCcjS5nK...

# Client side: pass the token any way you like (Slack, email, etc.)
$ echo "hello" | tailcat tcomFwWCCcjS5nK...
```

All traffic is WireGuard-encrypted. NAT traversal happens automatically; if UDP hole-punching fails, DERP relays serve as an encrypted fallback.

### Technical Stack

Tailcat reuses four Tailscale client components, minus the control plane:

| Component | Role |
|---|---|
| **Userspace WireGuard** | Encrypts all tunnel traffic; no kernel TUN/TAP, no root required |
| **magicsock** | Multiplexes UDP direct + DERP relay, STUN endpoint discovery, UDP hole-punching |
| **gVisor Netstack** | Userspace TCP/IP stack — accepts/dials connections inside the process, no OS network config |
| **DERP relay** | Encrypted relay protocol, rendezvous channel + fallback when direct path fails |

Connection flow: server generates WireGuard keypair → prints token (public key + DERP region) → client parses token → both sides exchange "Meow/Meowed" handshake over DERP → WireGuard tunnel established → UDP hole-punching attempted → upgrade to P2P or stay on DERP.

### Install

```bash
go install github.com/tailscale/tailcat/cmd/tailcat@latest
# Or with Nix:
nix run github:tailscale/tailcat
```

Single binary, no other dependencies.

### Core Commands

**Pipe stdin/stdout** (simplest use case):
```bash
$ tailcat                                     # server: get token
$ cat bigfile.tar.gz | tailcat <token>        # client: send
$ tailcat <token> > received.tar.gz           # client: receive
```

**Expose local ports**:
```bash
$ tailcat --serve=8080       # expose port 8080
$ tailcat --serve=all        # expose all ports
$ tailcat <token> 8080       # client connects
```

**Auth-free SSH** (debug only, trusted networks):
```bash
$ tailcat --serve=no-auth-ssh   # server
$ tailcat ssh <token>            # client
```

**SOCKS5 proxy** through the tunnel:
```bash
$ tailcat socks <token> curl http://internal:8081/
```

**Connectivity check**:
```bash
$ tailcat ping --until-direct <token>
pong in 42.1ms via DERP(sfo)
pong in 1.2ms via 203.0.113.7:41641   # direct P2P achieved
```

### Typical Use Cases

**Developer collaboration without accounts**: Share localhost:3000 with a teammate — no ngrok account, no Cloudflare Tunnel config. One command, WireGuard-encrypted, token expires when you kill the process.

**Persistent SSH entry point behind NAT**: No public IP, no open firewall ports. Generate a saved key, publish the token as a DNS TXT record, restrict to a specific client key with `--allow`. Anyone else's handshake is silently dropped before the SSH server even sees it.

**CI/CD accessing internal resources**: Single binary in a GitHub Actions runner, token stored as a Secret, encrypted tunnel to an internal database. Done in 3 seconds, auto-closes when the job finishes.

**Embed in Go programs**: Import `github.com/tailscale/tailcat` directly — no STUN/ICE management, NAT traversal already handled. Build P2P features into your own Go application in a dozen lines.

**Fully private with your own DERP**: Run your own DERP server (needs a hostname + TLS), generate keys with `--region=derp.example.com`. The token embeds your relay's hostname; clients never contact Tailscale's infrastructure.

### Key Management

**Ephemeral keys (default)**: Fresh keypair each run, discarded on exit. Token is single-use. Safest default.

**Saved keys** (`tailcat genkey`): Stable address across restarts, suitable for publishing to DNS. Use `--allow=nodekey:<pubkey>` to restrict which clients can connect.

### Caveats

- No API or CLI stability promises — flags, wire format, and Go API may change
- Public DERP relays are free but rate-limited — self-host for production traffic
- Auth-free SSH is debugging-only; never use in production
- A persisted token is a credential — if leaked, anyone who ever had it can reconnect (unless you use `--allow`)

### Summary

Tailcat extracts the most valuable piece of Tailscale — WireGuard encryption + automatic NAT traversal — into a zero-registration, zero-installation, zero-privilege netcat replacement. For the "I need a temporary encrypted tunnel right now" use case, it is the lightest credible option available.

**GitHub**: [tailscale/tailcat](https://github.com/tailscale/tailcat)  
**Web Demo**: https://tailscale.github.io/tailcat/
