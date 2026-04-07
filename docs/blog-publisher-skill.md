# Blog Publisher Skill

> Astro blog publishing workflow for blog.mushroom.cv (P1 Blog + P2 WeChat)
> 
> 维护记录：
> - 创建时间: 2026-04-07
> - 最后更新: 2026-04-07 - 改进图片处理流程

---

## 触发词
- 发布文章
- 发布blog
- 发布公众号  
- 发布

---

## 🚀 自动化方案（推荐）

### 方案 1: 使用 auto-publish.sh（最小交互）

适用于：你提供文字内容和图片路径

```bash
# 1. 准备内容文件
echo "文章标题

文章内容..." > /tmp/article.txt

# 2. 一键发布（带图片）
./scripts/auto-publish.sh /tmp/article.txt /path/to/image.png

# 3. 一键发布（无图片）
./scripts/auto-publish.sh /tmp/article.txt
```

**自动化程度**: 90%
- ✅ 自动提取标题
- ✅ 自动生成英文 slug
- ✅ 自动处理图片（封面+文章内）
- ✅ 自动创建 markdown
- ✅ 自动构建部署
- ✅ 自动发布 WeChat
- ⚠️ 需要你提供内容文件路径

---

### 方案 2: Skill 引导模式（当前实现）

适用于：你直接说"发布文章"，我引导完成

**自动化程度**: 70%
- 需要确认是否提供了图片
- 需要确认图片路径
- 其余步骤自动执行

---

### 方案 3: 完全自动化（理想状态）

**限制**: 目前无法实现完全自动化，因为：

1. **无法自动检测图片** - 不知道你把图片放在哪里
2. **无法自动确定 slug** - 需要确认英文文件名
3. **无法自动验证内容** - 需要确认内容是否完整

**改进建议**: 标准化输入

```
约定目录结构：
/tmp/blog-publish/
  ├── content.txt      # 文章内容
  └── image.png        # 配图（可选）

这样我可以自动检测：
- 如果存在 image.png → 使用它
- 如果不存在 → 使用默认封面
```

---

## 🎯 图片处理规则（核心）

### 用户提供了图片

**封面图片处理**：
- 尺寸：1200x630（强制比例）
- 操作：缩放 + 裁剪（从顶部裁剪）
- 质量：85%
- 命令：
```bash
convert input.png -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 src/assets/images/cover-FILENAME.jpg
```

**文章内图片处理**：
- 尺寸：最大宽度 1200px（保持原比例）
- 操作：**只缩放，不裁剪**
- 质量：85%
- 命令：
```bash
convert input.png -resize 1200x -quality 85 src/assets/images/content-FILENAME.jpg
```

### 用户没有提供图片

- 使用默认封面：`src/assets/images/blog-placeholder-X.jpg`（随机选择 1-5）
- 文章内不插入图片

---

## ⚠️ 关键规则（必须遵守）

### 1. 禁止使用中文文件名
**所有文件必须使用英文命名，严禁使用中文！**

❌ 错误: `apfel-在-apple-silicon-mac-上...md`
✅ 正确: `apfel-apple-silicon-local-ai.md`

命名规范:
- 使用英文小写字母
- 单词之间用连字符 `-` 分隔

### 2. 默认分类
- 所有文章默认分类: **Tech-News**

### 3. 文章排序
- 新文章默认按 `pubDate` 日期排序置顶

---

## 完整工作流程

### Step 1: 询问并处理图片

**询问用户**："是否提供了图片用于封面和文章内？"

#### 情况 A: 用户提供了图片

```bash
# 1. 处理封面（1200x630，可裁剪）
convert user-image.png \
  -resize 1200x630^ \
  -gravity North \
  -extent 1200x630 \
  -quality 85 \
  src/assets/images/cover-article-slug.jpg

# 2. 处理文章内图片（最大1200宽，不裁剪，保持比例）
convert user-image.png \
  -resize 1200x \
  -quality 85 \
  src/assets/images/content-article-slug.jpg

# 3. 记录路径
COVER_IMAGE="../../assets/images/cover-article-slug.jpg"
CONTENT_IMAGE="../../assets/images/content-article-slug.jpg"
```

#### 情况 B: 用户没有提供图片

```bash
# 使用随机默认封面（1-5）
COVER_NUM=$((RANDOM % 5 + 1))
COVER_IMAGE="../../assets/blog-placeholder-${COVER_NUM}.jpg"
CONTENT_IMAGE=""  # 文章内不插入图片
```

### Step 2: 创建 Markdown

文件路径: `src/content/blog/SLUG.md`（英文文件名）

#### 情况 A: 用户提供了图片

```markdown
---
title: "中文标题"
titleEn: "english-slug"
description: "描述"
descriptionEn: "English description"
pubDate: "YYYY-MM-DD"
category: "Tech-News"
tags: ["tag1", "tag2"]
heroImage: "../../assets/images/cover-article-slug.jpg"
---

## 标题

![图片描述](../../assets/images/content-article-slug.jpg)

正文内容...
```

#### 情况 B: 用户没有提供图片

```markdown
---
title: "中文标题"
titleEn: "english-slug"
description: "描述"
descriptionEn: "English description"
pubDate: "YYYY-MM-DD"
category: "Tech-News"
tags: ["tag1", "tag2"]
heroImage: "../../assets/blog-placeholder-1.jpg"
---

## 标题

正文内容...（无图片）
```

### Step 3: M1 Blog 发布

```bash
# 构建
pnpm build

# 部署到 Production（必须加 --branch=main）
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main
```

### Step 4: M2 WeChat 发布

```bash
cd pipeline/m2 && node index.js "../../src/content/blog/FILE.md"
```

### Step 5: 验证发布

```bash
# 验证生产环境文章URL
curl -s "https://blog.mushroom.cv/blog/SLUG/" | grep "文章标题"

# 验证文章在列表第一位
curl -s "https://blog.mushroom.cv/blog/" | grep -oE "blog/[a-z0-9-]+" | head -1
```

---

## 图片处理对比表

| 用途 | 尺寸 | 裁剪 | 命令 |
|------|------|------|------|
| **封面** | 1200x630 | ✅ 可以裁剪 | `-resize 1200x630^ -gravity North -extent 1200x630` |
| **文章内** | 最大1200宽 | ❌ 不裁剪 | `-resize 1200x` |

---

## 常见错误案例库

### ❌ 错误 1: 封面和文章内图片混淆处理

**症状**: 
- 文章内图片被裁剪，内容丢失
- 或封面图片比例不对

**根本原因**:
- 使用了相同的处理命令
- 没有区分封面和文章内的不同需求

**解决方案**:
```bash
# 封面：强制 1200x630，可裁剪
convert input.png -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 cover.jpg

# 文章内：最大1200宽，保持比例，不裁剪
convert input.png -resize 1200x -quality 85 content.jpg
```

**预防措施**:
- [ ] 封面和文章内使用不同的文件名（cover-xxx vs content-xxx）
- [ ] 封面必须 1200x630，文章内保持原比例

---

### ❌ 错误 2: 没有使用用户提供的图片

**发生时间**: 2026-04-07

**症状**: 
- 使用了自动生成或默认封面
- 忽略了用户提供的图片

**根本原因**:
- 没有询问用户是否提供了图片
- publish-fast.sh 自动生成封面覆盖了用户图片

**解决方案**:
```bash
# 1. 询问用户："是否提供了图片？"
# 2. 如果提供了，使用用户图片
# 3. 如果没有，使用默认封面

# 处理用户图片
if [ -f "$USER_IMAGE" ]; then
    # 生成封面（裁剪）
    convert "$USER_IMAGE" -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 cover.jpg
    # 生成文章内图片（不裁剪）
    convert "$USER_IMAGE" -resize 1200x -quality 85 content.jpg
else
    # 使用默认封面
    COVER="../../assets/blog-placeholder-$((RANDOM % 5 + 1)).jpg"
fi
```

**预防措施**:
- [ ] **第一步**：明确询问用户是否提供了图片
- [ ] 如果提供了，禁用自动生成封面
- [ ] 检查最终使用的是否为用户图片

---

### ❌ 错误 3: 文件名包含中文

**症状**: 文件名如 `apfel-在-apple-silicon-mac-上...md`

**解决方案**: 手动创建英文文件名

**预防措施**:
- [ ] 检查文件名：`ls src/content/blog/*.md | grep -P '[\x{4e00}-\x{9fff}]'`

---

### ❌ 错误 4: 部署到 Preview 而非 Production

**症状**: Preview URL 可以访问，但 blog.mushroom.cv 没有更新

**解决方案**:
```bash
# 错误
npx wrangler pages deploy dist --project-name=blog-mushroom

# 正确
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main
```

**预防措施**:
- [ ] 总是添加 `--branch=main`
- [ ] 验证生产环境 URL

---

## 发布检查清单

- [ ] 询问用户是否提供了图片
- [ ] 如果提供了图片：
  - [ ] 生成封面（1200x630，可裁剪）
  - [ ] 生成文章内图片（1200宽，不裁剪）
  - [ ] 在 markdown 中插入文章内图片
- [ ] 如果没有提供图片：
  - [ ] 使用随机默认封面
  - [ ] 文章内不插入图片
- [ ] Markdown 文件名是英文
- [ ] 图片文件名是英文
- [ ] 使用 `--branch=main` 部署
- [ ] 验证生产环境可访问
- [ ] 验证文章在列表第一位
- [ ] WeChat 草稿正常

---

## 快速命令参考

```bash
# ========== 图片处理 ==========

# 封面：1200x630，可裁剪
convert input.png -resize 1200x630^ -gravity North -extent 1200x630 -quality 85 cover.jpg

# 文章内：1200宽，不裁剪，保持比例
convert input.png -resize 1200x -quality 85 content.jpg

# ========== 构建部署 ==========

pnpm build
npx wrangler pages deploy dist --project-name=blog-mushroom --branch=main

# ========== 验证 ==========

curl -s "https://blog.mushroom.cv/blog/SLUG/" | grep "标题"
curl -s "https://blog.mushroom.cv/blog/" | grep -oE "blog/[a-z0-9-]+" | head -1

# ========== WeChat ==========

cd pipeline/m2 && node index.js "../../src/content/blog/FILE.md"
```

---

## 目录结构

```
src/content/blog/              # Markdown 文章（英文文件名）
src/assets/images/             # 用户上传的图片
  ├── cover-article-slug.jpg   # 封面图片（1200x630）
  └── content-article-slug.jpg # 文章内图片（1200宽，原比例）
src/assets/                    # 默认封面
  └── blog-placeholder-1~5.jpg # 默认封面（5张）
```

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-04-07 | 初始版本 |
| 2026-04-07 | 改进图片处理流程，区分封面和文章内图片处理规则 |
