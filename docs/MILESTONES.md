# M1/M2/M3/M4 里程碑规划与实现状态

## 📊 总览

| 里程碑 | 状态 | 核心功能 | 完成度 |
|--------|------|---------|--------|
| **M1** | ✅ 已完成 | Blog Pipeline | 100% |
| **M2** | ✅ 已完成 | WeChat Pipeline | 100% |
| **M3** | 🚧 规划中 | Full AI Pipeline | 0% |
| **M4** | 📋 新增 | 多用户/多公众号配置 | 规划中 |

---

## ✅ M1: Blog Pipeline

### 目标
原始文字 → AI 润色 → Markdown → 发布到 Astro Blog

### 已实现功能

| 功能 | 状态 | 文件 |
|------|------|------|
| AI 润色 Prompt 生成 | ✅ | `pipeline/m1/polisher.py` |
| 自动封面生成（随机 1-5） | ✅ | `pipeline/m1/cover_generator.py` |
| 文章保存 + frontmatter | ✅ | `pipeline/m1/publisher.py` |
| 自动 Build | ✅ | `pipeline/m1/publisher.py` |
| 自动 Deploy | ✅ | `pipeline/m1/publisher.py` |
| 一键脚本 | ✅ | `publish-fast.sh` / `publish.sh` |

### 使用方式

**方式 1: Kimi Client 内**
```
发布：[你的文字内容]
```

**方式 2: 终端命令**
```bash
./publish-fast.sh content.txt    # 已润色文字，全自动
./publish.sh content.txt         # 原始文字，交互式润色
```

### 输出
- Blog: https://blog.mushroom.cv

---

## ✅ M2: WeChat Pipeline

### 目标
Blog Markdown → 微信兼容 HTML → 发布到公众号草稿

### 已实现功能

| 功能 | 状态 | 文件 |
|------|------|------|
| Markdown → 微信 HTML 渲染 | ✅ | `pipeline/m2/renderer/wechat-renderer.js` |
| 4 种主题（Claude/橙韵/蓝色/贴纸） | ✅ | `wechat-renderer.js` THEME 配置 |
| 微信 CSS 兼容性处理 | ✅ | table 包裹、inline style |
| 封面图上传 CDN | ✅ | `pipeline/m2/wechat-api/client.js` |
| draft/add 发布草稿 | ✅ | `wechat-api/client.js` |
| 集成到 M1 流程 | ✅ | 自动串联执行 |

### 使用方式

**已集成到 M1 流程**，无需单独调用。发布 Blog 后自动执行 P2。

### 输出
- 微信草稿箱: https://mp.weixin.qq.com

---

## 🚧 M3: Full AI Pipeline

### 目标
完整 AI 内容生产管线：选题 → 写作 → 评估 → 排版 → 多平台发布

### 规划功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **Topic AI** | 热点选题分析 | 🚧 未开始 |
| **AI Writer** | 5种文章类型（观点/教程/盘点/评论/故事） | 🚧 未开始 |
| **Evaluator** | 质量门禁（5维度100分制） | 🚧 未开始 |
| **Polisher** | 8种润色（grammar/style/deai等） | 🚧 未开始 |
| **Cover Gen** | AI 生成封面图 | 🚧 未开始 |
| **Multi-platform** | 小红书/知乎/掘金扩展 | 🚧 未开始 |

### 工作流程
```
[1] 选题 AI 推荐热点
      ↓ 用户确认
[2] AI Writer 生成大纲
      ↓ 用户确认
[3] AI Writer 生成全文
      ↓
[4] Evaluator 质量评估（<80分→修改）
      ↓
[5] Polisher 润色
      ↓ 用户确认
[6] 生成封面 + 配图
      ↓ 用户确认
[7] 多平台排版
      ↓ 用户确认
[8] 一键发布到所有平台
```

---

## 📋 M4: 多用户/多公众号配置（新增）

### 需求背景
除了你自己使用外，其他用户也需要：
- 发布到 **不同的公众号**（不是 blog.mushroom.cv）
- 使用 **自己的微信 API 密钥**
- 可能发布到 **不同的 Blog 域名**

### 设计方案

#### 方案 A: 配置文件方式（推荐）

```yaml
# config/users.yaml
users:
  alice:
    blog:
      domain: "blog.alice.com"
      repo: "alice/blog"
    wechat:
      app_id: "${ALICE_APP_ID}"
      app_secret: "${ALICE_APP_SECRET}"
      default_theme: "blue"
  
  bob:
    blog:
      domain: "tech.bob.io"
      repo: "bob/tech-blog"
    wechat:
      app_id: "${BOB_APP_ID}"
      app_secret: "${BOB_APP_SECRET}"
      default_theme: "claude"
```

**使用方式**:
```bash
# 指定用户发布
./publish.sh --user alice content.txt
```

#### 方案 B: 环境变量方式

```bash
# 切换用户配置
export CURRENT_USER=alice
./publish-fast.sh content.txt
```

#### 方案 C: 独立部署（最安全）

每个用户 Fork 仓库，配置自己的 `.env`：
```bash
# 用户自己的仓库
WECHAT_APP_ID=wx_alice_xxx
WECHAT_APP_SECRET=alice_secret
BLOG_DOMAIN=blog.alice.com
```

### 推荐实现

**方案 A + C 结合**:

1. **主仓库** 支持多用户配置（方案A）
2. **敏感信息** 通过环境变量注入（每个用户自己的服务器配置）
3. **可选 Fork** 用户也可以完全独立部署（方案C）

### M4 任务列表

| 任务 | 描述 | 优先级 |
|------|------|--------|
| T1 | 用户配置 YAML 设计 | P0 |
| T2 | 多用户环境变量支持 | P0 |
| T3 | 发布脚本 `--user` 参数 | P1 |
| T4 | 不同用户主题默认配置 | P1 |
| T5 | 用户权限管理（可选） | P2 |

---

## 📈 实现总结

### 已完成（M1 + M2）
- ✅ 原始文字 → AI 润色 → Markdown
- ✅ 自动生成封面（随机 1-5）
- ✅ 发布 Astro Blog
- ✅ Markdown → 微信 HTML
- ✅ 4 种主题样式
- ✅ 上传封面 + 发布微信草稿
- ✅ 一键脚本 `publish-fast.sh`

### 待开发（M3 + M4）
- 🚧 AI 自动写作
- 🚧 质量评估系统
- 🚧 AI 封面生成
- 🚧 多平台扩展（小红书等）
- 📋 多用户/多公众号配置

---

## 🎯 下一步建议

**选择 1: 先做 M3（AI 能力）**
- 提升内容生产能力
- 适合个人效率提升

**选择 2: 先做 M4（多用户）**
- 支持团队协作
- 适合产品化/SaaS 化

**选择 3: M3 + M4 并行**
- M3 做核心功能
- M4 做配置系统
