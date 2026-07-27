---
title: "bitchat：蓝牙 Mesh + Nostr 双轨制去中心化通信协议深度拆解"
description: "31k star 的开源项目 bitchat 提出了一种双轨制消息架构——本地蓝牙 Mesh 覆盖无网络场景，Nostr 协议覆盖全球触达——从协议设计、加密实现到 Courier 投递系统，逐层剖析这套无账号、无服务器的通信方案。"
pubDate: "2026-07-27"
category: "Tech-Experiment"
heroImage: "../../assets/images/bitchat-bluetooth-mesh-nostr-decentralized-messaging-permissionless-banner.jpg"
---

2025 年 7 月 4 日，一个叫 `bitchat` 的开源项目在 GitHub 上线，当天就登上了 Trending。仓库描述只有七个字：**bluetooth mesh chat, IRC vibes**。

截至目前 31,206 star，4,903 fork，iOS/macOS/Android 全平台覆盖，App Store 上架，公有领域（Public Domain）授权。仓库 README 还有一句不同寻常的提醒：

> "This repository has been the target of takedown demands."

一个收到下架通知的开源通信工具。这背后值得深挖。

---

## 一、双轨制架构

bitchat 的核心设计决策是**两套传输层并行**，由统一的 `MessageRouter` 协调：

```
[用户消息]
     ↓
MessageRouter
  ├── BLE Mesh（本地，无需网络）
  └── Nostr Protocol（全球，需要网络）
```

路由优先级：**蓝牙直连 > Nostr 回退 > Courier 队列**。

当设备在蓝牙范围内，走 BLE 直连；出范围时，如果双方互设为 Favorites 并且有网络，走 Nostr；两个都不可用，走 Courier 系统存储转发。

这不是"要么有网要么没网"的二选一，而是三层递降的覆盖方案。

---

## 二、BLE Mesh 层：受控洪泛

### 拓扑模型

每台设备同时作为 GATT Central 和 Peripheral 运行——既主动连接其他设备，也被其他设备连接。这构成一个自组织的多跳无线网格，理论上最多 **7 跳**传递消息。

没有基础设施，没有配对，没有账号。

### 洪泛控制

协议用一套参数化的确定性洪泛替代了传统路由：

| 参数 | 值 |
|---|---|
| 初始 TTL | 7 |
| 密集图（≥6 链路）广播 TTL 上限 | 5 |
| 稀疏链（≤2 链路）TTL | 保持完整 |
| 去重缓存 | LRU 1000 条，5 分钟过期 |
| 广播扇出 | log₂(degree) 子集，message-ID 为随机种子 |
| 中继抖动 | 10–220ms（密集时更宽）|

去重键由 `sender + timestamp + type + payload_digest` 组成，保证同一条消息在同一节点只被处理一次。

### 加密层

两套 Noise 协议模式，覆盖不同场景：

**Live Session — Noise XX**（双向认证 + 前向保密）：
```
Curve25519 密钥协商 + ChaCha20-Poly1305 加密 + SHA-256
```
实时私信走这条路，每条消息都在 Noise session 内传输，中继节点只看到不透明密文。

**Offline Seal — Noise X**（单向，无前向保密）：
```
消息密封到接收方静态公钥
发送方身份在密文内认证
```
Courier 存储转发走这条路。代价是：接收方静态密钥被泄露时，历史 sealed mail 可能暴露。白皮书明确标注这是已知限制，prekey scheme 是 future work。

### 分片机制

超过链路 MTU 的消息被切成 ~469 字节的分片（8 字节 fragment ID + index/total 头），每片独立路由，接收端各自重组。支持 128 条并发重组，超时 30 秒，上限 1 MiB。

---

## 三、Nostr 层：全球位置频道

bitchat 把 Nostr 用作**互联网传输层**，而不仅仅是另一种加密聊天标准。

### 位置频道

基于 Geohash 坐标划分层级频道：

```
block      → 7位 geohash，街区级
neighborhood → 6位，社区级
city       → 5位，城市级
province   → 4位，省/州级
region     → 2位，国家/大区级
```

接入 290+ 个全球 Nostr Relay，在蓝牙 Mesh 之外提供基于地理位置的群聊——不需要预先知道任何人的账号。

### 私信封装格式

bitchat 的 Nostr 私信不是标准 NIP-17/NIP-44/NIP-59，而是一套**专有私信信封协议**：

```
kind-14 (inner, unsigned)  ← 实际消息
  ↓ encrypted
kind-13 (sender-signed seal)
  ↓ encrypted again  
kind-1059 (one-time key envelope)  ← 上传到 relay
```

加密方式：`v2:` 前缀 + base64url(24字节 nonce + XChaCha20-Poly1305 密文 + 16字节 tag)，密钥派生用 secp256k1 ECDH + HKDF-SHA256（借用了 NIP-44 的 label，但 key schedule 不同）。

外层时间戳随机偏移 ±15 分钟，真实时间戳加密在内层。relay 只能看到接收方 Nostr 公钥，看不到发送方身份和内容。

**不兼容任何标准 Nostr 客户端**，只与 bitchat 客户端互通。这是有意的：优先安全性，而非生态互联。

---

## 四、Courier 系统：人肉信使协议

Courier 是整套设计中最有意思的部分——一套基于**人类移动性**的存储转发机制。

### 问题：接收方不在线

发消息时，接收方可能不在蓝牙范围内，也没有网络。怎么办？

把消息交给"中间人"——附近的、可能之后遇到接收方的设备。

### 隐私寻址

信封上没有接收方的真实 ID，只有一个 **16 字节轮换标签**：

```python
tag = HMAC(recipient_static_key, UTC_day)
```

只有知道接收方静态公钥的人才能计算这个 tag。Courier 看不到发件人、收件人，也无法跨天关联同一接收方的多封邮件。

### 配额体系

```
互设 Favorites 的设备：可存 5 封
有签名公告的验证设备：可存 2 封
总池：40 槽位，其中 Favorites 专用 20
信封大小上限：16 KiB
信封生命周期：24 小时
```

### Spray-and-Wait 扩散

每封信封携带一个 **copy budget**（初始 4，上限 8）。Courier 遇到另一台符合条件的设备时，把剩余 budget 的一半传给它。这样信封在人群中扩散而不是只跟着一个人走。

传到接收方时，所有副本和原始 outbox 条目因为去重（message ID）而自动消重，不会重复投递。

---

## 五、安全分析：明确的边界

白皮书第 8 节开头直接说：

> "Metadata is the weakest part of this design, and the peer ID does not help."

这是少见的技术诚实。具体问题：

**持久化 Peer ID**：`peer_id = SHA-256(Noise_static_key)` 的前 8 字节，跨会话、跨重启、跨重装不变。被动监听者可以在不同地点追踪同一设备。

**公告包泄露邻居图**：signed announcement 携带最多 10 个直接邻居 ID，一个嗅探器可以重建本地邻接图。

**TTL 透露跳距**：origin 包以默认 TTL 7 发出，监听者可以通过 TTL 值估算发送方距离。

**Nostr 层无前向保密**：接收方静态私钥泄露 → 历史信封全部可解密。

这些都是已知限制，Future Work 里明确列了 rotating peer ID 方案——但还没实现。

---

## 六、技术判断

bitchat 在几个设计维度上做出了有意思的取舍：

**取舍 1**：选择协议可验证性而非生态兼容性。Nostr 私信不走标准 NIP-44，换来的是更强的元数据保护（sender 身份在外层不可见）。

**取舍 2**：选择实用性而非完美安全。Noise X 无前向保密，但让 Courier 存储转发成为可能。如果只用 Noise XX，离线投递就做不了。

**取舍 3**：选择物理世界的移动性作为可靠性来源。Courier 系统本质上把"人会走动"这件事变成了一种消息传递机制，在极端网络失效场景下（自然灾害、基础设施破坏）依然有效。

31k star，来自 GitHub 之外的外部压力，以及 2025 年 7 月 4 日的上线日期——这个项目的存在本身就是一个关于通信基础设施脆弱性的技术声明。

> 源码：github.com/permissionlesstech/bitchat  
> iOS/macOS App Store：bitchat mesh  
> Android：github.com/permissionlesstech/bitchat-android  
> 技术白皮书：WHITEPAPER.md（v2.0，2026-07-06）  
> 协议授权：Public Domain

<!--EN-->

## bitchat: Deep Dive into a Dual-Transport Decentralized Messaging Protocol

On July 4, 2025 — US Independence Day — an open-source project called `bitchat` appeared on GitHub and immediately trended. Its repo description: **bluetooth mesh chat, IRC vibes**.

31,206 stars, 4,903 forks, iOS/macOS/Android coverage, App Store distribution, Public Domain license. The README includes an unusual note:

> "This repository has been the target of takedown demands."

A communication tool served with takedown notices. Worth examining closely.

---

## The Dual-Transport Architecture

bitchat's core design decision is **two parallel transport layers**, coordinated by a unified `MessageRouter`:

```
[User Message]
      ↓
MessageRouter
  ├── BLE Mesh (local, no internet needed)
  └── Nostr Protocol (global, internet required)
```

Routing priority: **Bluetooth direct > Nostr fallback > Courier queue**.

When devices are in Bluetooth range, use BLE. Out of range, if both parties are mutual Favorites with internet access, use Nostr. When neither is available, the Courier system queues for store-and-forward delivery.

This isn't a binary "internet or no internet" choice — it's a three-tier degrading coverage model.

---

## BLE Mesh Layer: Controlled Flooding

### Topology Model

Each device runs simultaneously as both a GATT Central and Peripheral — actively connecting to other devices while being discoverable. This forms a self-organizing multi-hop wireless mesh with a maximum of **7 hops**.

No infrastructure, no pairing, no accounts.

### Flood Control

The protocol replaces traditional routing with parameterized deterministic flooding:

| Parameter | Value |
|---|---|
| Initial TTL | 7 |
| Dense graph (≥6 links) broadcast TTL cap | 5 |
| Sparse chain (≤2 links) TTL | Full depth |
| Dedup cache | LRU 1000 entries, 5-minute expiry |
| Broadcast fanout | log₂(degree) subset, message-ID seeded |
| Relay jitter | 10–220ms (wider when dense) |

Dedup key: `sender + timestamp + type + payload_digest` — ensures each message is processed only once per node.

### Encryption

Two Noise protocol modes for different scenarios:

**Live Session — Noise XX** (mutual auth + forward secrecy):
```
Curve25519 key agreement + ChaCha20-Poly1305 + SHA-256
```
Live DMs use this path. All payloads travel inside the Noise session; relay nodes see only opaque ciphertext.

**Offline Seal — Noise X** (one-way, no forward secrecy):
```
Message sealed to recipient's static public key
Sender identity authenticated inside ciphertext
```
Courier store-and-forward uses this. The trade-off: compromise of recipient's static key could expose historical sealed mail. The whitepaper explicitly flags this as a known limitation; a prekey scheme is listed as future work.

### Fragmentation

Packets exceeding link MTU split into ~469-byte fragments (8-byte fragment ID + index/total header), each routed independently and reassembled at each receiving node. Supports 128 concurrent assemblies, 30-second timeout, 1 MiB cap.

---

## Nostr Layer: Global Location Channels

bitchat uses Nostr as an **internet transport layer**, not just another encrypted chat standard.

### Location Channels

Hierarchical channels based on Geohash coordinates:

```
block        → 7-char geohash, city block level
neighborhood → 6-char, district level
city         → 5-char, city level
province     → 4-char, state/province level
region       → 2-char, country/large region level
```

Connected to 290+ global Nostr relays, providing location-based group chat beyond Bluetooth range — no need to know anyone's account in advance.

### Private Message Envelope Format

bitchat's Nostr DMs are **not** standard NIP-17/NIP-44/NIP-59 — they use a proprietary private envelope protocol:

```
kind-14 (inner, unsigned)  ← actual message
  ↓ encrypted
kind-13 (sender-signed seal)
  ↓ encrypted again
kind-1059 (one-time key envelope)  ← uploaded to relay
```

Encryption: `v2:` prefix + base64url(24-byte nonce + XChaCha20-Poly1305 ciphertext + 16-byte tag), keys derived via secp256k1 ECDH + HKDF-SHA256 (borrows NIP-44 label, different key schedule).

Outer timestamps randomized ±15 minutes; actual message timestamp encrypted in the inner layer. Relays see only the recipient's Nostr public key, never sender identity or content.

**Not compatible with any standard Nostr client** — intentionally. Security takes precedence over ecosystem interoperability.

---

## Courier System: The Human Relay Protocol

The Courier system is the most interesting part of the design — a store-and-forward mechanism based on **human mobility**.

### The Problem: Recipient is Offline

When you send a message, the recipient may be out of Bluetooth range with no internet. The solution: entrust the message to a nearby device that might physically encounter the recipient later.

### Privacy-Preserving Addressing

The envelope carries no real recipient ID — only a **16-byte rotating tag**:

```python
tag = HMAC(recipient_static_key, UTC_day)
```

Only parties who already know the recipient's static public key can compute this tag. Couriers learn neither sender nor recipient, and cannot correlate the same recipient's mail across different days.

### Quota System

```
Mutual Favorites devices: can store 5 envelopes each
Signature-verified peers:  can store 2 envelopes each
Total pool: 40 slots, 20 reserved for Favorites
Envelope size cap: 16 KiB
Envelope lifetime: 24 hours
```

### Spray-and-Wait Diffusion

Each envelope carries a **copy budget** (initial 4, max 8). When a Courier meets another eligible device, it hands over half its remaining budget, allowing mail to diffuse through a crowd rather than riding a single person.

At delivery, all copies and the original outbox entry are deduplicated by message ID — no duplicate delivery.

---

## Security Analysis: Explicit Boundaries

Whitepaper section 8 opens directly:

> "Metadata is the weakest part of this design, and the peer ID does not help."

This is rare technical honesty. Specific issues:

**Persistent Peer ID**: `peer_id = first 8 bytes of SHA-256(Noise_static_key)`. Stable across sessions, reboots, reinstalls. A passive listener can track the same device across locations.

**Announcement packets expose neighbor graph**: Signed announcements carry up to 10 direct neighbor IDs. A single sniffer can reconstruct the local adjacency graph.

**TTL leaks hop distance**: Origin packets launch at TTL 7. Listeners can estimate sender distance from the TTL value.

**Nostr layer lacks forward secrecy**: Compromise of recipient's static private key → all stored envelopes to that key become decryptable.

All acknowledged limitations. Future Work lists a rotating peer ID scheme — not yet implemented.

---

## Technical Verdict

bitchat makes interesting design trade-offs across several dimensions:

**Trade-off 1**: Protocol verifiability over ecosystem compatibility. Nostr DMs don't use standard NIP-44, in exchange for stronger metadata protection (sender identity invisible at the outer layer).

**Trade-off 2**: Practicality over perfect security. Noise X lacks forward secrecy, but enables Courier store-and-forward. Noise XX only would make offline delivery impossible.

**Trade-off 3**: Physical-world mobility as a reliability primitive. The Courier system turns "people move around" into a message delivery mechanism — effective in extreme network failure scenarios (natural disasters, infrastructure destruction).

31k stars, external pressure from takedown demands, and a July 4 launch date — this project's existence is itself a technical statement about the fragility of communication infrastructure.

> Source: github.com/permissionlesstech/bitchat  
> iOS/macOS: App Store — bitchat mesh  
> Android: github.com/permissionlesstech/bitchat-android  
> Technical Whitepaper: WHITEPAPER.md (v2.0, 2026-07-06)  
> License: Public Domain
