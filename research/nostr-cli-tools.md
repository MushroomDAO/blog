# Nostr 命令行工具汇总

> 生成时间: 2026-04-08

本文档汇总了基于 Nostr 协议的命令行通信工具，包含 GitHub 链接、Star 数量、最近提交时间等关键信息。

---

## 📊 工具对比一览

| 工具名称 | 语言 | Stars | 最近提交 | 维护状态 | 推荐度 |
|---------|------|-------|----------|----------|--------|
| **nak** | Go | 356 | 2026-04-05 | ✅ 活跃 | ⭐⭐⭐⭐⭐ |
| **algia** | Go | 216 | 2026-03-18 | ✅ 活跃 | ⭐⭐⭐⭐⭐ |
| **noscl** | Go | 277 | 2024-01-27 | ⚠️ 基本废弃 | ⭐⭐⭐ |
| **nostril** | C | 113 | 2025-12-14 | ✅ 维护中 | ⭐⭐⭐⭐ |
| **nostr-commander-rs** | Rust | 79 | 2024-10-01 | ⚠️ 更新较少 | ⭐⭐⭐ |

---

## 🏆 推荐工具详情

### 1. nak (强烈推荐)

- **GitHub**: https://github.com/fiatjaf/nak
- **Stars**: 356 ⭐
- **最近提交**: 2026-04-05
- **语言**: Go
- **维护状态**: ✅ 活跃维护
- **描述**: 一个功能全面的 Nostr 命令行工具，可以"做所有 Nostr 相关的事情"

**安装**:
```bash
go install github.com/fiatjaf/nak@latest
# 或使用 Homebrew
brew install nak
```

**常用命令**:
```bash
# 生成密钥
nak key-gen

# 发布文本笔记
nak event --content "Hello Nostr!" --kind 1

# 查询事件
nak req -k 1 --limit 10 wss://relay.damus.io

# 查询某用户的推文
nak req -k 1 -a <pubkey> wss://relay.nostr.band

# 监听实时消息
nak req -k 1 --stream wss://relay.damus.io
```

---

### 2. algia

- **GitHub**: https://github.com/mattn/algia
- **Stars**: 216 ⭐
- **最近提交**: 2026-03-18
- **语言**: Go
- **维护状态**: ✅ 活跃维护
- **描述**: 功能完整的 Nostr CLI 客户端，支持时间线、私信、点赞、转发等

**安装**:
```bash
go install github.com/mattn/algia@latest
```

**常用命令**:
```bash
# 查看时间线
algia timeline

# 发布新笔记
algia post "Hello Nostr!"

# 发送私信
algia dm-post <pubkey> "私信内容"

# 点赞
algia like <note-id>

# 转发
algia repost <note-id>

# 查看个人资料
algia profile <pubkey>

# Zap (打赏)
algia zap <note-id>
```

**配置** (位于 `~/.config/algia/config.json`):
```json
{
  "relays": {
    "wss://relay-jp.nostr.wirednet.jp": {
      "read": true,
      "write": true,
      "search": false
    }
  },
  "privatekey": "nsecXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

---

### 3. nostril

- **GitHub**: https://github.com/jb55/nostril
- **Stars**: 113 ⭐
- **最近提交**: 2025-12-14
- **语言**: C
- **维护状态**: ✅ 维护中
- **描述**: 轻量级 C 语言 CLI 工具，用于创建和签名 Nostr 事件

**安装**:
```bash
# macOS
brew install nostril

# 或使用源码编译
git clone https://github.com/jb55/nostril.git
cd nostril
make && sudo make install
```

**常用命令**:
```bash
# 生成事件
nostril --sec <key> --content "this is a message"

# 发送到中继
nostril --envelope --sec <key> --content "hello" | websocat wss://relay.damus.io

# 发送私信 (NIP-04)
nostril --envelope --dm <pubkey> --sec <key> --content "secret message" | websocat wss://relay.damus.io

# 挖矿 pubkey (Proof of Work)
nostril --mine-pubkey --pow <difficulty>

# 回复事件
nostril --envelope --sec <key> --content "reply" --tag e <thread_id> --tag e <note_id> | websocat wss://relay.damus.io
```

---

### 4. noscl

- **GitHub**: https://github.com/fiatjaf/noscl
- **Stars**: 277 ⭐
- **最近提交**: 2024-01-27
- **语言**: Go
- **维护状态**: ⚠️ 项目已被标记为"somewhat abandoned"，作者推荐使用 algia 或 nak
- **描述**: 基础的 Nostr 命令行客户端

**注意**: 虽然功能可用，但项目已不再活跃维护。建议迁移到 **nak** 或 **algia**。

**安装**:
```bash
go install github.com/fiatjaf/noscl@latest
```

---

### 5. nostr-commander-rs

- **GitHub**: https://github.com/8go/nostr-commander-rs
- **Stars**: 79 ⭐
- **最近提交**: 2024-10-01
- **语言**: Rust
- **维护状态**: ⚠️ 更新较少
- **描述**: Rust 编写的 CLI 客户端，支持发布、私信、关注用户和频道

**安装**:
```bash
cargo install nostr-commander-rs
```

**常用命令**:
```bash
# 创建用户
nostr-commander-rs --create-user --name "用户名" --about "简介"

# 发布消息
nostr-commander-rs --publish "Hello World"

# 发送私信
nostr-commander-rs --dm <pubkey> "私信内容"

# 添加联系人
nostr-commander-rs --add-contact --key <pubkey> --alias "昵称"

# 订阅频道
nostr-commander-rs --subscribe-channel <channel-hash>
```

---

## 🔧 其他相关工具

### Python 库

**nostr** (Python):
```bash
pip install nostr
```

```python
from nostr.key import PrivateKey
from nostr.relay import Relay

private_key = PrivateKey()
relay = Relay("wss://relay.damus.io")
relay.publish_note("Hello from Python!")
```

---

## 📋 快速选择指南

| 使用场景 | 推荐工具 | 原因 |
|---------|---------|------|
| 全面功能 + 活跃维护 | **nak** | 功能最全面，持续更新 |
| 社交功能 (时间线/私信/Zap) | **algia** | 支持完整社交功能 |
| 轻量级/脚本化 | **nostril** | 简单快速，Unix 哲学 |
| 与管道工具链集成 | **nostril** | 标准输出，易于管道 |
| Rust 生态 | **nostr-commander-rs** | Rust 实现 |

---

## 📚 参考资源

- [Nostr 协议规范](https://github.com/nostr-protocol/nostr)
- [Awesome Nostr](https://github.com/aljazceru/awesome-nostr) - Nostr 生态系统资源汇总
- [Nostr 中继列表](https://nostr.watch/)

---

*本文档由自动化工具生成，数据来源于 GitHub API*
