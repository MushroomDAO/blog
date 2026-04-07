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

图片命名也禁止使用中文！

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
