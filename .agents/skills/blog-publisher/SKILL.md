---
name: blog-publisher
description: |
  Astro blog publishing workflow for blog.mushroom.cv (P1 Blog + P2 WeChat).
  
  触发词: 发布文章, 发布blog, 发布公众号, 发布
  
  使用场景:
  - 用户想发布新博客文章
  - 用户想发布微信公众号草稿
  - 用户想同时发布博客和公众号
  - 用户提供了图片和文章内容
  
  完整流程:
  1. 处理图片 → src/assets/images/
  2. 创建 markdown → src/content/blog/
  3. M1: 运行 pipeline/m1/publisher.py (build + deploy)
  4. M2: 运行 pipeline/m2/index.js (WeChat草稿)
  5. 验证: 检查文章URL和排序
  
  关键规则:
  - 所有文章文件禁止使用中文命名（使用英文slug）
  - 默认分类: Tech-News
  - 新文章默认按日期排序置顶
---

# Blog Publisher Skill

## ⚠️ 关键规则（必须遵守）

### 1. 禁止使用中文文件名
**所有文章文件必须使用英文命名，严禁使用中文！**

❌ 错误: `apfel-在-apple-silicon-mac-上零成本调用本地-appl.md`
✅ 正确: `apfel-apple-intelligence-cli-tool.md`

命名规范:
- 使用英文小写字母
- 单词之间用连字符 `-` 分隔
- 文件名基于 titleEn 或英文 slug

### 2. 默认分类
- 所有文章默认分类: **Tech-News**
- 可选分类: Tech-Experiment, Progress-Report, Research, Other

### 3. 文章排序
- 新文章默认按 `pubDate` 日期排序置顶
- 日期格式: `YYYY-MM-DD`

## 触发词
- 发布文章
- 发布blog
- 发布公众号  
- 发布

## 完整工作流程

### Step 1: 处理图片

保存图片到 `src/assets/images/`，尺寸 1200x630，质量 85：

```bash
convert input.png -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 src/assets/images/FILENAME.jpg
```

### Step 2: 创建 Markdown

文件路径: `src/content/blog/SLUG.md` (**英文文件名！**)

Frontmatter 模板:
```yaml
---
title: "中文标题"
titleEn: "english-slug"  # 用于生成文件名
description: "中文描述"
descriptionEn: "English description"
pubDate: "YYYY-MM-DD"
category: "Tech-News"  # 默认 Tech-News
tags: ["tag1", "tag2"]
heroImage: "../../assets/images/IMAGE.jpg"
---
```

### Step 3: M1 Blog 发布

```bash
python3 pipeline/m1/publisher.py src/content/blog/FILE.md --images src/assets/images/IMAGE.jpg
```

这会自动:
- 保存文章
- 处理图片
- pnpm build
- deploy 到 Cloudflare

### Step 4: M2 WeChat 发布

```bash
cd pipeline/m2 && node index.js "../../src/content/blog/FILE.md"
```

主题选项: claude | chengyun | blue | sticker | mint | purple | cyber | rose

### Step 5: 验证发布（必须执行）

```bash
# 获取部署URL
URL="https://XXXX.blog-mushroom.pages.dev"  # 从部署输出获取

# 验证文章URL可访问
curl -s "$URL/blog/SLUG/" | grep -o "文章标题" | head -1

# 验证文章在列表第一位
curl -s "$URL/blog/" | grep -oE "blog/[a-z0-9-]+" | head -1
# 应该显示: blog/SLUG
```

## 可用脚本

| 脚本 | 用途 |
|------|------|
| `./publish.sh content.txt` | 完整流程（需AI润色） |
| `./publish-fast.sh content.txt` | 极速模式（直接发布） |
| `./deploy.sh` | 仅部署 |

## 目录结构

```
src/content/blog/     # Markdown 文章（英文文件名！）
src/assets/images/    # 封面图片（英文文件名！）
pipeline/m1/          # Blog 发布 (P1)
pipeline/m2/          # WeChat 发布 (P2)
```

## 输出检查

- Blog: https://blog.mushroom.cv/blog/SLUG/
- WeChat: https://mp.weixin.qq.com

## 文件名检查清单

发布前必须确认：
- [ ] Markdown 文件名是英文（无中文字符）
- [ ] 图片文件名是英文（无中文字符）
- [ ] titleEn 字段已填写（用于生成文件名）
- [ ] pubDate 设置为今天（用于置顶）
- [ ] 部署后验证文章URL可访问
- [ ] 验证文章在 /blog 列表第一位

## 故障排除

### 文章没有在列表第一位
1. 检查是否有其他相同日期的文章
2. 删除旧的同日期文章
3. 重新构建部署

### 文章URL返回404
1. 检查文件名是否正确
2. 检查构建输出是否包含该文件
3. 检查部署是否成功

---

## ⚠️ 已知错误案例（必读，避免重犯）

### 错误1：重复文章路由（2026-04-17）

**问题描述：**
M1 publisher (`pipeline/m1/publisher.py`) 的行为是：**不使用你传入的文件，而是新建一个带时间戳的副本**（如 `aura-ai-manifesto-152839.md`）。

如果你在 M1 运行前已手动创建了同 slug 的文件（如 `aura-ai-manifesto.md`），M1 会同时构建两个文件，导致博客出现**两条重复路由**：
- `/blog/aura-ai-manifesto/`
- `/blog/aura-ai-manifesto-152839/`

**根本原因：**
M1 publish → build（含两个文件）→ deploy。之后删除原始文件再重新 build，因 Cloudflare 资产增量缓存，旧路由仍然存在，必须再做一次完整 `--branch=main` deploy 才能清除。

**正确流程：**
1. **不要**提前手动创建 `src/content/blog/SLUG.md`
2. 直接把内容写好，交给 M1 publisher 处理，它会自建带时间戳的文件
3. M1 完成后，删除旧文件（如有），`pnpm build` 一次，再 `npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main --commit-dirty=true`
4. 验证生产域名列表无重复

**验证命令：**
```bash
# 检查 dist 中是否只有一个 slug
ls dist/blog/ | grep SLUG

# 检查生产无重复
curl -s "https://blog.mushroom.cv/blog/" | grep -oE "href=\"/blog/[a-z0-9-]+/\"" | head -5
```

---

### 错误2：微信公众号 IP 白名单（errcode 40164）

**问题描述：**
M2 publisher 调用微信 API 时报错：
```
invalid ip 116.204.181.208, not in whitelist
```

**原因：** 当前服务器 IP 不在微信公众平台的 IP 白名单中。

**解决方法：**
1. 登录微信公众平台 → 开发 → 基本配置 → IP 白名单
2. 添加报错中显示的 IP 地址（如 `116.204.181.208`）
3. 保存后等约 1 分钟再重试 M2

**注意：** IP 可能随时间变化，如再次遇到此错误，重复以上步骤添加新 IP。

---

### 错误3：main 分支受保护，直接 push 失败

**问题描述：**
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
```

**解决方法：**
1. 创建新分支：`git checkout -b feat/your-branch-name`
2. Push 分支：`git push -u origin feat/your-branch-name`
3. 创建 PR：`gh pr create --title "..." --body "..."`
4. Blog 内容的部署通过 `wrangler pages deploy` 直接走，不依赖 PR 合并
