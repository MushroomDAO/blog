# Nak & Algia 安装与使用指南

## 📦 安装方法

### 方法一：Go 安装 (推荐)

```bash
# 安装 nak
go install github.com/fiatjaf/nak@latest

# 安装 algia
go install github.com/mattn/algia@latest

# 确保 PATH 包含 $HOME/go/bin
export PATH=$PATH:$HOME/go/bin
```

### 方法二：Homebrew (macOS/Linux)

```bash
# 安装 nak
brew install nak

# algia 需要源码安装或使用 release
```

### 方法三：直接下载 Release

```bash
# nak
wget https://github.com/fiatjaf/nak/releases/download/v0.19.2/nak-v0.19.2-darwin-amd64.tar.gz
tar -xzf nak-v0.19.2-darwin-amd64.tar.gz
sudo mv nak /usr/local/bin/

# algia
wget https://github.com/mattn/algia/releases/download/v0.0.83/algia_v0.0.83_darwin_amd64.zip
unzip algia_v0.0.83_darwin_amd64.zip
sudo mv algia /usr/local/bin/
```

---

## 🛠️ Nak 完整使用指南

### 1. 密钥管理

```bash
# 生成新密钥对
nak key-gen

# 输出示例:
# seed: abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
# private key: 0000000000000000000000000000000000000000000000000000000000000001
# public key: 79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798

# 从 nsec 转换为 hex
nak key-convert nsec1...
```

### 2. 发布事件 (Publish)

```bash
# 发布简单文本笔记 (kind 1)
nak event --content "Hello Nostr from nak!"

# 发布带标签的笔记
nak event --content "#bitcoin #nostr 测试" -t t=bitcoin -t t=nostr

# 回复某人 (引用事件)
nak event --content "这是一条回复" -t e=<event-id> -t p=<pubkey>

# 使用特定私钥发布
nak event --sec <hex-private-key> --content "用指定密钥发布"

# 指定中继发布
nak event --content "Hello" -r wss://relay.damus.io -r wss://nos.lol
```

### 3. 查询事件 (Request)

```bash
# 查询最新 10 条文本笔记
nak req -k 1 --limit 10 wss://relay.damus.io

# 查询特定用户的内容
nak req -k 1 -a <pubkey-hex> wss://relay.damus.io

# 查询多种类型的事件
nak req -k 0 -k 1 -k 3 --limit 100 wss://relay.damus.io

# 查询特定时间段的内容
nak req -k 1 --since 1700000000 --until 1700100000 wss://relay.damus.io

# 实时流式监听
nak req -k 1 --stream wss://relay.damus.io

# 查询特定标签的内容
nak req -k 1 -t t=bitcoin wss://relay.nostr.band
```

### 4. 元数据操作 (Kind 0)

```bash
# 设置用户资料
nak metadata --name "用户名" --about "个人简介" --picture "https://example.com/avatar.jpg"

# 查询用户资料
nak req -k 0 -a <pubkey> wss://relay.damus.io
```

### 5. 联系人列表 (Kind 3)

```bash
# 查询某人的关注列表
nak req -k 3 -a <pubkey> wss://relay.damus.io

# 获取推荐中继
nak req -k 2 --limit 10 wss://relay.damus.io
```

### 6. 加密私信 (NIP-04)

```bash
# 发送加密私信
nak event --content "私密消息" --dm <recipient-pubkey>

# 查询收到的私信
nak req -k 4 -p <your-pubkey> wss://relay.damus.io
```

### 7. 高级功能

```bash
# 批量查询多个中继
nak req -k 1 --limit 5 \
  wss://relay.damus.io \
  wss://nos.lol \
  wss://relay.nostr.band

# 使用 JSON 过滤查询
nak req --filter '{"kinds":[1],"limit":10}' wss://relay.damus.io

# 导出事件到文件
nak req -k 1 --limit 100 wss://relay.damus.io > events.jsonl

# 从文件读取并发布事件
cat event.json | nak event --pipe
```

---

## 💬 Algia 完整使用指南

### 1. 初始配置

```bash
# 创建配置目录
mkdir -p ~/.config/algia

# 创建配置文件 ~/.config/algia/config.json
cat > ~/.config/algia/config.json << 'EOF'
{
  "relays": {
    "wss://relay.damus.io": {
      "read": true,
      "write": true,
      "search": true
    },
    "wss://nos.lol": {
      "read": true,
      "write": true,
      "search": false
    },
    "wss://relay.nostr.band": {
      "read": true,
      "write": false,
      "search": true
    }
  },
  "privatekey": "nsec1...your...private...key"
}
EOF
```

### 2. 时间线功能

```bash
# 查看全局时间线 (最新 20 条)
algia timeline

# 简写形式
algia tl

# 实时流式查看
algia stream

# 查看自己的时间线
algia timeline --me
```

### 3. 发布内容

```bash
# 发布新笔记
algia post "Hello Nostr world!"

# 简写
algia n "一条消息"

# 发布带主题标签的笔记
algia post "Learning about #nostr and #bitcoin"

# 回复某条笔记
algia reply <note-id> "这是一条回复"

# 简写
algia r <note-id> "回复内容"

# 转发 (repost)
algia repost <note-id>

# 简写
algia b <note-id>

# 取消转发
algia unrepost <note-id>
```

### 4. 互动功能

```bash
# 点赞
algia like <note-id>

# 简写
algia l <note-id>

# 取消点赞
algia unlike <note-id>

# 打赏 (Zap)
algia zap <note-id>

# 给指定用户打赏
algia zap <npub>

# 删除自己的笔记
algia delete <note-id>
```

### 5. 私信 (DM)

```bash
# 查看私信列表
algia dm-list

# 查看与某人的私信对话
algia dm-timeline <pubkey>

# 发送私信
algia dm-post <pubkey> "私信内容"
```

### 6. 搜索功能

```bash
# 搜索包含关键词的笔记
algia search "bitcoin"

# 简写
algia s "nostr"
```

### 7. 个人资料

```bash
# 查看某人的资料
algia profile <pubkey-or-npub>

# 查看自己的资料
algia profile
```

### 8. 特殊功能

```bash
# 发布 "ぽわ〜" (日式感叹)
algia powa

# 发布 "ぷる" (日式感叹)
algia puru

# 使用特定配置文件
algia -a other_profile timeline

# 显示详细日志
algia -V timeline
```

---

## 🔧 实用组合示例

### 场景 1: 备份自己的所有笔记

```bash
# 使用 nak 备份
nak req -k 1 -a <your-pubkey> --limit 1000 \
  wss://relay.damus.io \
  wss://nos.lol \
  wss://relay.nostr.band > my-notes.jsonl
```

### 场景 2: 查找热门话题

```bash
# 搜索带 #bitcoin 标签的最新内容
nak req -k 1 -t t=bitcoin --limit 50 wss://relay.nostr.band
```

### 场景 3: 监控提及自己的内容

```bash
# 实时监听提及自己的事件
nak req -k 1 -t p=<your-pubkey> --stream wss://relay.damus.io
```

### 场景 4: 批量关注用户

```bash
# 先获取推荐的关注列表
nak req -k 3 -a <trusted-pubkey> wss://relay.damus.io
```

### 场景 5: 发布长文 (拆分多条)

```bash
# 使用 algia 发布
algia post "第一部分内容... (1/3)"
algia post "第二部分内容... (2/3)"
algia post "第三部分内容... (3/3)"
```

---

## 🆚 Nak vs Algia 功能对比

| 功能 | Nak | Algia |
|------|-----|-------|
| 发布文本笔记 | ✅ | ✅ |
| 查看时间线 | ❌ | ✅ |
| 实时流监听 | ✅ | ✅ |
| 回复/转发 | ✅ | ✅ |
| 点赞 | ❌ | ✅ |
| 私信 | ✅ | ✅ |
| 搜索 | ❌ | ✅ |
| Zap (打赏) | ❌ | ✅ |
| 用户资料管理 | ✅ | ✅ |
| 批量查询 | ✅ | ❌ |
| 管道支持 | ✅ | ❌ |
| 多中继同时查询 | ✅ | ❌ |
| NWC 钱包连接 | ❌ | ✅ |

---

## 💡 最佳实践

1. **日常使用**: 用 **algia** 作为主力客户端 (查看时间线、互动)
2. **数据查询**: 用 **nak** 做复杂查询和数据导出
3. **自动化脚本**: 用 **nak** 配合 shell 脚本实现自动化
4. **密钥安全**: 永远不要把私钥提交到代码仓库
5. **多中继**: 配置多个中继以提高可靠性

---

## 🐛 常见问题

### Q: 连接中继失败?
```bash
# 检查网络
ping relay.damus.io

# 使用代理
HTTP_PROXY=http://proxy:8080 algia timeline
```

### Q: 如何导入已有密钥?
```bash
# 将 nsec 添加到 algia 配置
# 或使用 nak 转换
nak key-convert nsec1...
```

### Q: 如何测试而不泄露真实密钥?
```bash
# 生成测试密钥
nak key-gen
# 使用生成的密钥进行测试
```

---

*最后更新: 2026-04-08*
