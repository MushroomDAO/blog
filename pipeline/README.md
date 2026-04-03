# AI Content Pipeline

Blog + 微信公众号 一键发布系统

## 快速开始

### 方式一：Kimi Client 内（推荐）

直接发消息：
```
发布：[你的文章内容]
```

**我会**：润色 → 生成封面 → P1 Blog → P2 微信 → 返回两个链接

**特点**：全自动，无需你执行任何命令

---

### 方式二：终端命令行（脱离 Kimi）

```bash
# 极速模式（文字已润色）
./publish-fast.sh content.txt

# 标准模式（需要 AI 润色）
./publish.sh content.txt
# → 显示 AI Prompt → 你复制给 AI → 保存 /tmp/article.md → 按回车继续
```

**要求**：
- Python 3.9+
- Node.js 18+
- pnpm

---

## 两种脚本对比

| 脚本 | 适用场景 | 交互 | 速度 |
|------|---------|------|------|
| `publish-fast.sh` | 文字已润色 | 全自动 | 10秒 |
| `publish.sh` | 原始文字 | 需复制 Prompt 给 AI | 2-3分钟 |

---

## 配置文件

`.env` 文件需包含：
```
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

---

## 流程说明

```
你的文字
    ↓
[可选] AI 润色
    ↓
自动生成封面（随机 1-5）
    ↓
P1: 发布 Blog
    - 保存 Markdown
    - pnpm build
    - wrangler deploy
    ↓
P2: 发布微信
    - marked 渲染 HTML
    - 上传封面到 CDN
    - draft/add 创建草稿
    ↓
✅ 完成
    - Blog: https://blog.mushroom.cv
    - 微信: https://mp.weixin.qq.com
```
