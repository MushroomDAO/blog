# Nak & Algia 功能演示与实战

> 创建时间: 2026-04-08
> 环境: macOS + Go 1.21+

---

## 📦 安装步骤 (带代理)

### 1. 设置代理并安装

```bash
# 加载代理配置
source ~/.zshrc_proxy

# 开启代理
proxy_on

# 安装 nak
go install github.com/fiatjaf/nak@latest

# 安装 algia
go install github.com/mattn/algia@latest

# 添加到 PATH
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.zshrc
source ~/.zshrc

# 关闭代理
proxy_off
```

### 2. 验证安装

```bash
nak --help
algia --help
```

---

## 🔧 Nak 功能详解与演示

### 核心功能概览

```
nak
├── key-gen          # 生成密钥对
├── key-convert      # 密钥格式转换
├── event            # 发布事件
├── req              # 查询事件
├── metadata         # 设置用户资料
└── fs               # 文件系统操作
```

### 1. 密钥管理演示

```bash
# 生成新密钥对
$ nak key-gen

seed: abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
private key: 0000000000000000000000000000000000000000000000000000000000000001
public key: 79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798

# 转换密钥格式 (nsec <-> hex)
$ nak key-convert nsec1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
<hex-private-key>
```

### 2. 发布事件 (Publishing)

#### 基本发布
```bash
# 发布简单文本笔记 (kind 1)
$ nak event --content "Hello Nostr from nak CLI!"

# 带话题标签
$ nak event --content "Bitcoin is freedom money #bitcoin #nostr" \
  -t t=bitcoin -t t=nostr

# 指定多个中继发布
$ nak event --content "Multi-relay post" \
  -r wss://relay.damus.io \
  -r wss://nos.lol \
  -r wss://relay.nostr.band
```

#### 回复与互动
```bash
# 回复某条笔记 (需要原始事件ID和作者pubkey)
$ nak event --content "这是一条回复" \
  -t e=<event-id> \
  -t p=<author-pubkey> \
  -t e=<root-event-id>,root

# 示例 (使用真实ID):
$ nak event --content "Great post!" \
  -t e=abcdef1234567890... \
  -t p=1234567890abcdef...
```

#### 使用特定密钥发布
```bash
# 使用 hex 私钥
$ nak event --sec <64-char-hex-key> --content "Signed with specific key"

# 从环境变量读取 (更安全)
$ nak event --sec "$NOSTR_PRIVATE_KEY" --content "Hello"
```

### 3. 查询事件 (Querying)

#### 基础查询
```bash
# 查询最新10条文本笔记
$ nak req -k 1 --limit 10 wss://relay.damus.io

# 输出格式 (JSON Lines):
{"id":"...","pubkey":"...","created_at":1234567890,"kind":1,"tags":[],"content":"...","sig":"..."}
```

#### 按作者查询
```bash
# 查询特定用户的所有笔记
$ nak req -k 1 -a <32-byte-pubkey-hex> wss://relay.damus.io

# 查询用户的元数据 (头像、简介等)
$ nak req -k 0 -a <pubkey> wss://relay.damus.io

# 查询用户的关注列表
$ nak req -k 3 -a <pubkey> wss://relay.damus.io
```

#### 高级过滤
```bash
# 按时间段查询
$ nak req -k 1 \
  --since $(date -v-1d +%s) \
  --until $(date +%s) \
  wss://relay.damus.io

# 按话题标签查询
$ nak req -k 1 -t t=bitcoin wss://relay.nostr.band

# 查询多种事件类型
$ nak req -k 0 -k 1 -k 3 --limit 100 wss://relay.damus.io

# 复杂过滤 (JSON)
$ nak req --filter '{"kinds":[1],"authors":["pubkey1","pubkey2"],"limit":50}' \
  wss://relay.damus.io
```

#### 实时监听
```bash
# 实时流式监听新事件
$ nak req -k 1 --stream wss://relay.damus.io

# 监听提及自己的事件
$ nak req -k 1 -t p=<your-pubkey> --stream wss://relay.damus.io

# 监听特定话题
$ nak req -k 1 -t t=bitcoin --stream wss://relay.damus.io
```

### 4. 元数据管理

```bash
# 设置个人资料
$ nak metadata \
  --name "MyName" \
  --about "Nostr enthusiast and developer" \
  --picture "https://example.com/avatar.jpg" \
  --nip05 "me@example.com"

# 发布到指定中继
$ nak metadata --name "Test" -r wss://relay.damus.io
```

### 5. 批量操作

```bash
# 同时查询多个中继
$ nak req -k 1 --limit 20 \
  wss://relay.damus.io \
  wss://nos.lol \
  wss://relay.nostr.band

# 备份自己的所有笔记
$ nak req -k 1 -a <your-pubkey> --limit 1000 \
  wss://relay.damus.io > my-notes-backup.jsonl

# 导出关注列表
$ nak req -k 3 -a <your-pubkey> wss://relay.damus.io > following.jsonl
```

---

## 💬 Algia 功能详解与演示

### 核心功能概览

```
algia
├── timeline (tl)     # 查看时间线
├── stream            # 实时流
├── post (n)          # 发布笔记
├── reply (r)         # 回复
├── repost (b)        # 转发
├── like (l)          # 点赞
├── delete (d)        # 删除
├── search (s)        # 搜索
├── dm-*              # 私信功能
└── profile           # 查看资料
```

### 1. 配置文件设置

```bash
# 创建配置目录
mkdir -p ~/.config/algia

# 创建配置文件
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
  "privatekey": "nsec1yourprivatekeyhere"
}
EOF

# 设置权限
chmod 600 ~/.config/algia/config.json
```

### 2. 时间线功能

```bash
# 查看最新全局时间线 (20条)
$ algia timeline

# 简写
$ algia tl

# 实时流式查看 (持续更新)
$ algia stream

# 按 Ctrl+C 停止
```

**时间线输出示例**:
```
[2026-04-08 15:30] @alice 🌟
Hello Nostr world! This is my first post.

[2026-04-08 15:28] @bob
Check out this #bitcoin analysis thread 👇

[2026-04-08 15:25] @charlie ✨
Just published a new article on #nostr development
```

### 3. 发布内容

```bash
# 发布新笔记
$ algia post "Hello Nostr from algia CLI!"

# 简写
$ algia n "Quick update"

# 发布带标签
$ algia post "Learning about decentralized social media #nostr"

# 回复笔记 (使用 note ID)
$ algia reply note1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx "Great post!"

# 简写
$ algia r note1xxx "Agreed!"

# 转发
$ algia repost note1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 简写
$ algia b note1xxx

# 取消转发
$ algia unrepost note1xxx
```

### 4. 互动功能

```bash
# 点赞
$ algia like note1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 简写
$ algia l note1xxx

# 取消点赞
$ algia unlike note1xxx

# 打赏 (Zap) - 需要配置 NWC
$ algia zap note1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 给指定用户打赏
$ algia zap npub1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. 搜索功能

```bash
# 搜索包含关键词的笔记
$ algia search "bitcoin"

# 简写
$ algia s "nostr development"

# 搜索结果会显示最近的匹配笔记
```

### 6. 私信 (DM)

```bash
# 查看私信列表
$ algia dm-list

# 查看与某人的对话
$ algia dm-timeline npub1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 发送私信
$ algia dm-post npub1xxx "Hey, how are you doing?"
```

### 7. 个人资料

```bash
# 查看某人的资料
$ algia profile npub1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 查看自己的资料
$ algia profile

# 输出包含: 用户名、简介、头像、NIP-05验证状态等
```

### 8. 特殊功能

```bash
# 日式萌语发布
$ algia powa    # 发布 "ぽわ〜"
$ algia puru    # 发布 "ぷる"

# 使用详细模式 (显示调试信息)
$ algia -V timeline

# 使用不同配置文件
$ algia -a work_profile timeline
```

---

## 🎯 实战场景

### 场景1: 每日工作流程

```bash
# 1. 查看时间线
algia tl

# 2. 发布今日想法
algia post "Working on #nostr tools today 💪"

# 3. 回复感兴趣的帖子
algia r note1xxx "Interesting perspective!"

# 4. 点赞好内容
algia l note1yyy
```

### 场景2: 数据备份

```bash
# 使用 nak 备份自己的全部数据
#!/bin/bash
PUBKEY="your-pubkey-hex"
BACKUP_DIR="$HOME/nostr-backup/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份笔记
nak req -k 1 -a "$PUBKEY" --limit 5000 \
  wss://relay.damus.io \
  wss://nos.lol \
  wss://relay.nostr.band > "$BACKUP_DIR/notes.jsonl"

# 备份元数据
nak req -k 0 -a "$PUBKEY" wss://relay.damus.io > "$BACKUP_DIR/metadata.json"

# 备份关注列表
nak req -k 3 -a "$PUBKEY" wss://relay.damus.io > "$BACKUP_DIR/following.json"

echo "备份完成: $BACKUP_DIR"
```

### 场景3: 监控特定话题

```bash
# 实时监控 #bitcoin 话题
nak req -k 1 -t t=bitcoin --stream wss://relay.nostr.band | \
  while read -r event; do
    content=$(echo "$event" | jq -r '.content')
    echo "[$(date '+%H:%M:%S')] $content"
  done
```

### 场景4: 批量关注用户

```bash
# 从 JSON 文件批量关注
#!/bin/bash
while IFS= read -r pubkey; do
  echo "Processing: $pubkey"
  # 这里需要使用 nostr-commander-rs 或其他支持批量关注的工具
  # algia 目前不支持程序化批量关注
done < pubkeys.txt
```

---

## ⚡ 性能对比

| 操作 | Nak | Algia | 推荐 |
|------|-----|-------|------|
| 快速发布 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | nak |
| 查看时间线 | ❌ | ⭐⭐⭐⭐⭐ | algia |
| 实时监听 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | nak |
| 社交互动 | ⭐⭐ | ⭐⭐⭐⭐⭐ | algia |
| 数据导出 | ⭐⭐⭐⭐⭐ | ❌ | nak |
| 批量操作 | ⭐⭐⭐⭐ | ⭐⭐ | nak |
| 易用性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | algia |

---

## 🔐 安全建议

1. **私钥管理**
   ```bash
   # 使用环境变量
   export NOSTR_NSEC="nsec1..."
   
   # 在命令中使用
   nak event --sec "$(nostr-key-convert $NOSTR_NSEC)" --content "Hello"
   ```

2. **配置文件权限**
   ```bash
   chmod 600 ~/.config/algia/config.json
   ```

3. **测试时使用临时密钥**
   ```bash
   # 生成测试密钥
   nak key-gen > /tmp/test-key.txt
   TEST_KEY=$(grep "private key:" /tmp/test-key.txt | awk '{print $3}')
   nak event --sec "$TEST_KEY" --content "Test"
   rm /tmp/test-key.txt
   ```

---

## 🐛 常见问题解决

### Q1: 连接中继失败
```bash
# 检查网络
ping relay.damus.io

# 测试 WebSocket
wscat -c wss://relay.damus.io

# 使用代理
proxy_on
algia timeline
proxy_off
```

### Q2: 事件发布成功但看不到
- 中继可能拒绝了事件 (检查内容是否合规)
- 使用 `nak req` 直接查询该中继确认
- 检查时间戳是否正确

### Q3: 密钥格式错误
```bash
# nsec 转 hex
nak key-convert nsec1...

# hex 转 npub (需要其他工具)
```

---

## 📚 相关资源

- [Nak GitHub](https://github.com/fiatjaf/nak)
- [Algia GitHub](https://github.com/mattn/algia)
- [Nostr 协议](https://github.com/nostr-protocol/nostr)
- [NIP 规范](https://github.com/nostr-protocol/nips)

---

*文档版本: 1.0*
*最后更新: 2026-04-08*
