# Nostr CLI 工具研究目录

本目录包含关于 Nostr 命令行工具的研究文档和使用指南。

## 📄 文档列表

| 文档 | 描述 | 更新时间 |
|------|------|----------|
| [nostr-cli-tools.md](nostr-cli-tools.md) | Nostr CLI 工具汇总对比 (GitHub Stars, 维护状态) | 2026-04-08 |
| [nostr-cli-guide.md](nostr-cli-guide.md) | Nak & Algia 完整使用指南 | 2026-04-08 |
| [nak-algia-demo.md](nak-algia-demo.md) | Nak & Algia 功能演示与实战 | 2026-04-08 |

## 🛠️ 创建的 Skill

| Skill | 路径 | 描述 |
|-------|------|------|
| network-switch | `.agents/skills/network-switch/` | 网络代理切换工具 |

## 🚀 快速开始

### 安装工具

```bash
# 1. 开启代理
source ~/.zshrc_proxy && proxy_on

# 2. 安装 nak
go install github.com/fiatjaf/nak@latest

# 3. 安装 algia
go install github.com/mattn/algia@latest

# 4. 添加到 PATH
export PATH=$PATH:$HOME/go/bin

# 5. 关闭代理
proxy_off
```

### 基础使用

```bash
# Nak - 查询事件
nak req -k 1 --limit 10 wss://relay.damus.io

# Nak - 发布事件
nak event --content "Hello Nostr!"

# Algia - 查看时间线
algia timeline

# Algia - 发布
algia post "Hello from algia"
```

## 📊 工具对比

| 工具 | 语言 | Stars | 最佳用途 |
|------|------|-------|----------|
| nak | Go | 356 | 数据查询、事件发布、脚本自动化 |
| algia | Go | 216 | 社交互动、时间线浏览、日常使用 |
| nostril | C | 113 | 轻量级事件生成、Unix 管道 |
| noscl | Go | 277 | ⚠️ 已废弃，不推荐使用 |

## 🔗 相关链接

- [Nak GitHub](https://github.com/fiatjaf/nak)
- [Algia GitHub](https://github.com/mattn/algia)
- [Nostr 协议](https://nostr-protocol.github.io/)
