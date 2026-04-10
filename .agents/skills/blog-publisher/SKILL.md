# Blog Publisher Skill

> Astro blog publishing workflow for blog.mushroom.cv (P1 Blog + P2 WeChat)
> 
> 维护记录：
> - 创建时间: 2026-04-07
> - 最后更新: 2026-04-10 - 添加错误 10: pubDate 日期错误导致文章无法成为 Banner；更新检查清单

---

## 🎯 触发词（调用方式）

### 方式 1：直接说触发词（推荐）
当用户输入包含以下关键词时，自动激活本 skill：

| 触发词 | 示例 |
|--------|------|
| `发布文章` | "发布这篇文章" |
| `发布blog` | "发布到blog" |
| `发布公众号` | "发布到公众号" |
| `发布` + 文件路径 | "发布：research/article.md" |

### 方式 2：指定文件路径
用户可以提供 markdown 文件路径：
```
发布：research/my-article.md，分类为 Research
```

### 方式 3：直接粘贴内容
用户直接粘贴文章内容：
```
发布这篇文章：

# 标题
正文内容...
```

---

## 🔍 Skill 位置（供 AI 参考）

**本 Skill 文件位置：**
```
/Users/jason/Dev/crypto-projects/blog/.agents/skills/blog-publisher/SKILL.md
```

**当用户要求"发布"但找不到 skill 时：**
1. 检查上述路径是否存在
2. 读取 SKILL.md 获取完整流程
3. 按本 skill 定义的步骤执行

---

## 触发词

---

## 🚀 简化流程（推荐）

### 最佳实践：你直接粘贴

**步骤 1**: 你把文章内容粘贴给我  
**步骤 2**: （可选）把图片粘贴给我  
**步骤 3**: 说"发布"  
**步骤 4**: 我自动完成全部工作

---

### 图片处理约定

**你做的**:
- 直接粘贴/上传图片（任何格式）

**我做的**:
- 自动压缩到 ~100KB
- 封面：1200x630（可裁剪）
- 文章内：1200宽（不裁剪）

**压缩目标**: 100KB ± 20KB

---

### 完整示例

**你输入**:
```
发布这篇文章：

apfel: 在 Apple Silicon Mac 上零成本调用本地 Apple Intelligence

**apfel** 是一款专为搭载 Apple Silicon...

[粘贴图片]
```

**我自动执行**:
1. ✅ 提取标题
2. ✅ 生成英文 slug
3. ✅ 处理图片（压缩到 100KB）
4. ✅ 创建 markdown
5. ✅ 构建部署到 Production
6. ✅ 发布 WeChat 草稿
7. ✅ 验证并返回链接

**你得到**:
- Blog: https://blog.mushroom.cv/blog/SLUG/
- WeChat: 草稿已创建

---

### 备选方案：auto-publish.sh

适用于：批量发布、CI/CD、脚本集成

```bash
./scripts/auto-publish.sh /path/to/content.txt [/path/to/image.png]
```

---

## 🎯 图片处理规则（核心）

### 用户直接粘贴图片

**目标大小**: ~100KB (80-120KB)

**封面图片**（用于 Blog 列表和 WeChat 封面）：
```bash
# 步骤 1: 先尝试高质量压缩
convert input.png \
  -resize 1200x630^ \
  -gravity North \
  -extent 1200x630 \
  -quality 85 \
  -strip \
  cover.jpg

# 步骤 2: 如果 > 120KB，降低质量
convert input.png \
  -resize 1200x630^ \
  -gravity North \
  -extent 1200x630 \
  -quality 75 \
  -strip \
  cover.jpg

# 步骤 3: 如果还 > 120KB，进一步降低质量到 65
```

**文章内图片**（不裁剪，保持原比例）：
```bash
# 步骤 1: 先尝试高质量压缩  
convert input.png \
  -resize 1200x \
  -quality 85 \
  -strip \
  content.jpg

# 步骤 2: 如果 > 120KB，降低质量到 75 或 65
```

**压缩参数说明**:
- `-strip`: 移除元数据，减小文件大小
- `-quality 85`: 默认质量
- `-quality 75`: 如果文件太大
- `-quality 65`: 如果还是太大

### 目标文件大小

| 类型 | 目标大小 | 最大大小 |
|------|---------|---------|
| 封面 | ~100KB | 120KB |
| 文章内 | ~100KB | 120KB |

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
pubDate: "YYYY-MM-DD"  # 必须是今天的日期，确保文章成为 banner
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
pubDate: "YYYY-MM-DD"  # 必须是今天的日期，确保文章成为 banner
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

### ❌ 错误 5: YAML Frontmatter 引号转义错误

**发生时间**: 2026-04-08（MemPalace 文章）

**症状**: 
```
YAMLException: unexpected end of the stream within a quoted scalar
at readBlockMapping
```

**根本原因**:
- 标题或描述中包含中文引号 `"记忆宫殿"`
- YAML 解析器将引号视为字符串边界
- 导致 frontmatter 解析失败

**错误示例**:
```yaml
---
title: "MemPalace：重塑 AI 记忆的"记忆宫殿""  # ❌ 错误：内部双引号未转义
description: "从古希腊"记忆宫殿"技术中汲取灵感"  # ❌ 错误
---
```

**解决方案**:
```yaml
---
title: 'MemPalace：重塑 AI 记忆的记忆宫殿'  # ✅ 使用单引号
description: '从古希腊记忆宫殿技术中汲取灵感'  # ✅ 移除内部引号
---
```

**预防措施**:
- [ ] **避免在 YAML 值中混用双引号包裹包含双引号的文本**
- [ ] 优先使用单引号 `'` 或不使用引号
- [ ] 如果必须使用双引号，内部双引号需要转义：`\"`
- [ ] 构建前检查：`pnpm build` 会提示 YAML 解析错误

**检查命令**:
```bash
# 验证 YAML 格式
head -15 src/content/blog/article.md | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin.read())" && echo "✅ YAML 格式正确"
```

---

### ❌ 错误 6: 微信公众号 IP 白名单限制

**发生时间**: 2026-04-08（MemPalace 文章）

**症状**: 
```
Token error: {"errcode":40164,"errmsg":"invalid ip 42.243.69.232, not in whitelist"}
```

**根本原因**:
- 当前机器的公网 IP 不在微信公众号白名单中
- 微信公众号 API 要求预先配置允许的 IP 地址
- 每次更换网络环境都可能遇到此问题

**解决方案**:

**方案 1: 添加 IP 到白名单（推荐）**
```
1. 登录 https://mp.weixin.qq.com
2. 设置与开发 → 基本配置 → IP 白名单
3. 添加当前 IP: 42.243.69.232
4. 保存后等待 5-10 分钟生效
5. 重新发布
```

**方案 2: 使用已配置好的机器**
- 在之前成功发布过的机器上执行发布
- 或者使用固定的服务器/VPS

**方案 3: 手动发布**
- 复制文章内容到微信公众号后台手动发布
- 作为临时解决方案

**预防措施**:
- [ ] 记录常用的 IP 地址列表
- [ ] 在固定网络环境下发布
- [ ] 备选方案：准备手动发布的模板

**检查命令**:
```bash
# 获取当前公网 IP（多种方式）
curl -s ip.sb
curl -s ifconfig.me
curl -s https://api.ipify.org

# 测试 WeChat API 连通性（仅验证 IP）
curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=YOUR_APP_ID&secret=YOUR_SECRET" | grep -o "40164" && echo "❌ IP 不在白名单"
```

**备注**: 
- IP 白名单修改后需等待 5-10 分钟生效
- 微信公众号最多支持 50 个 IP 地址
- 如果遇到 IPv6 问题，尝试禁用 IPv6

### ❌ 错误 7: Schema 字段名错误 (cover/heroImage, excerpt/description)

**发生时间**: 2026-04-08 (OpenScreen 文章)

**症状**: 
```
[ERROR] [InvalidContentEntryDataError] blog/openscreen-free-screen-recorder.md 
→ Invalid frontmatter
```

**根本原因**:
- 使用了错误的字段名 `cover` 而不是 `heroImage`
- 使用了 `excerpt` 而不是 `description`
- 没有查看项目实际的 content schema 定义

**错误示例**:
```yaml
---
title: 'OpenScreen：免费开源的 Screen Studio 替代品'
cover: '../../assets/blog/openscreen/cover.jpg'        # ❌ 错误字段名
excerpt: '无需39美元每月...'                          # ❌ 错误字段名
category: '工具推荐'                                   # ❌ 中文枚举值不被接受
---
```

**解决方案**:
```yaml
---
title: 'OpenScreen：免费开源的 Screen Studio 替代品'
heroImage: '../../assets/blog-cover-openscreen.jpg'    # ✅ 正确字段名
description: '无需39美元每月...'                      # ✅ 正确字段名
category: 'Tech-News'                                 # ✅ 英文枚举值
---
```

**预防措施**:
- [ ] **第一步**：检查 `src/content.config.ts` 中的 schema 定义
- [ ] 确认所有必需字段：`title`, `description`, `pubDate`, `category`
- [ ] 确认可选字段：`heroImage` (不是 cover), `tags`
- [ ] category 必须是枚举值之一：`Tech-Experiment`, `Progress-Report`, `Research`, `Tech-News`, `Other`
- [ ] tags 必须是英文数组

**检查命令**:
```bash
# 查看 Schema 定义
cat src/content.config.ts

# 查看已有文章的正确格式
head -15 src/content/blog/EXISTING-ARTICLE.md
```

---

### ❌ 错误 10: pubDate 日期错误导致文章无法成为 Banner

**发生时间**: 2026-04-10

**症状**: 
- 新发布的文章没有成为首页 banner（大图展示）
- 文章按日期排序后不在第一位
- 昨天的文章仍然占据 banner 位置

**根本原因**:
- `pubDate` 错误地设置为昨天的日期 `2026-04-09`
- 博客首页按 `pubDate` 降序排列，日期相同或较早的文章不会排在第一位
- CSS `ul li:first-child` 选择器决定 banner，必须是排序后的第一篇文章

**错误示例**:
```yaml
---
# 错误：使用了昨天的日期
title: '今天的文章'
pubDate: '2026-04-09'  # ❌ 错误：应该是 2026-04-10
category: 'Research'
---
```

**解决方案**:
```yaml
---
# 正确：使用今天的日期
title: '今天的文章'
pubDate: '2026-04-10'  # ✅ 正确：使用发布当天的日期
category: 'Research'
---
```

**预防措施**:
- [ ] **创建 markdown 前**：确认今天的日期
- [ ] 使用 `date +%Y-%m-%d` 获取当前日期
- [ ] 检查清单中包含日期验证项
- [ ] 发布后验证文章在列表第一位

**日期获取命令**:
```bash
# 获取今天日期
date +%Y-%m-%d
# 输出: 2026-04-10
```

---

### ❌ 错误 9: 没有使用 Skill 而手动操作（严重）

**发生时间**: 2026-04-09

**症状**: 
- AI 没有读取 skill 文档，直接手动执行发布流程
- 图片放到了错误的目录 `public/images/`
- 使用了错误的 heroImage 路径格式 `/images/xxx.png`
- 构建失败：`[ImageNotFound] Could not find requested image`

**根本原因**:
- AI 没有找到 skill 的位置
- 用户提示 "用 skill 完成工作" 但 AI 仍手动操作
- 忽略了 `.agents/skills/` 目录下的 skill 文件

**正确流程**:
```bash
# 1. 首先读取 skill 文档
cat /Users/jason/Dev/crypto-projects/blog/.agents/skills/blog-publisher/SKILL.md

# 2. 按照 skill 定义的标准流程执行：
#    - 询问用户是否提供图片
#    - 处理图片（封面 1200x630，文章内 1200宽）
#    - 生成英文 slug 文件名
#    - 创建 markdown 到 src/content/blog/
#    - 构建并部署到 production
#    - 发布微信草稿
```

**预防措施**:
- [ ] **第一步**：检查 `.agents/skills/` 目录是否存在 skill
- [ ] **必须读取** skill 文档后再开始操作
- [ ] 封面图片路径使用 `../../assets/images/cover-[slug].jpg`
- [ ] 图片必须放在 `src/assets/images/` 而非 `public/images/`

---

### ❌ 错误 8: 图片路径不支持子目录

**发生时间**: 2026-04-08 (OpenScreen 文章)

**症状**: 
```
[ImageNotFound] Could not find requested image `../../assets/blog/openscreen/cover.jpg`
```

**根本原因**:
- Astro image schema 不支持子目录路径解析
- 图片放在 `src/assets/blog/openscreen/cover.jpg` 无法被正确识别

**解决方案**:
```bash
# 将图片移到 assets 根目录
mv src/assets/blog/openscreen/cover.jpg src/assets/blog-cover-openscreen.jpg

# 更新 frontmatter
heroImage: '../../assets/blog-cover-openscreen.jpg'
```

**预防措施**:
- [ ] 封面图片直接放在 `src/assets/` 根目录
- [ ] 使用命名前缀区分不同文章：`blog-cover-[slug].jpg`
- [ ] 不要用子目录存放封面图片

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
- [ ] **pubDate 使用今天的日期**（确保文章成为默认 banner）
- [ ] 使用 `--branch=main` 部署
- [ ] 验证生产环境可访问
- [ ] 验证文章在列表第一位（banner）
- [ ] WeChat 草稿正常

---

## 发布后复盘总结（必须执行）

每次发布完成后，必须记录本次发布的经验，持续改进流程。

### 复盘模板

```markdown
## 发布复盘: [文章标题]

**发布时间**: YYYY-MM-DD
**文章**: [标题] / [Slug]

### 本次发布遇到的问题

| 序号 | 问题描述 | 错误信息 | 根本原因 |
|------|----------|----------|----------|
| 1 | | | |
| 2 | | | |

### 解决方案

1. **问题 X**: [如何解决]

### 改进措施（预防下次发生）

- [ ] [具体的预防措施]
- [ ] [流程优化建议]

### 本次新增/更新的 Skill 条目

- [错误 N]: [问题名称]

### 耗时统计

- 图片处理: X 分钟
- 文章创建: X 分钟
- 构建部署: X 分钟
- WeChat 发布: X 分钟
- 问题解决: X 分钟
- **总计**: X 分钟

### 备注

[其他需要注意的事项]
```

### 复盘示例：MemPalace 文章 (2026-04-08)

```markdown
## 发布复盘: MemPalace：重塑 AI 记忆的记忆宫殿

**发布时间**: 2026-04-08
**文章**: MemPalace / mempalace-ai-memory-palace

### 本次发布遇到的问题

| 序号 | 问题描述 | 错误信息 | 根本原因 |
|------|----------|----------|----------|
| 1 | YAML 解析失败 | `YAMLException: unexpected end of the stream within a quoted scalar` | 标题中包含双引号，与 YAML 引号冲突 |
| 2 | 微信 IP 白名单 | `errcode:40164, invalid ip not in whitelist` | 当前机器 IP 不在公众号白名单中 |
| 3 | 微信图片路径错误 | `Image not found: pipeline/src/assets/images/xxx.jpg` | 路径解析错误，只回到 pipeline/ 目录而非根目录 |

### 解决方案

1. **YAML 引号问题**: 将双引号改为单引号包裹标题，或移除内部引号
2. **IP 白名单**: 登录微信公众号后台添加当前 IP，等待 5-10 分钟后重试
3. **图片路径问题**: 修复 `wechat-renderer.js`，将 `../..` 改为 `../../..`

### 改进措施

- [x] 更新 Skill：添加 "错误 5: YAML Frontmatter 引号转义错误"
- [x] 更新 Skill：添加 "错误 6: 微信公众号 IP 白名单限制"
- [x] 更新 Skill：添加 "错误 7: 微信图片路径解析错误"
- [ ] 下次发布前检查标题是否含特殊字符
- [ ] 在固定网络环境发布，或提前确认 IP 白名单
- [ ] 修改路径代码时验证文件是否存在

### 本次新增/更新的 Skill 条目

- [错误 5]: YAML Frontmatter 引号转义错误
- [错误 6]: 微信公众号 IP 白名单限制
- [错误 7]: 微信图片路径解析错误

### 耗时统计

- 图片处理: 3 分钟
- 文章创建: 2 分钟
- 构建部署: 2 分钟
- WeChat 发布: 5 分钟（首次，含 IP 白名单问题）
- WeChat 重发布: 2 分钟（修复图片路径）
- **总计**: 14 分钟

### 备注

- 两张图片处理：封面 113KB，内容图 151KB + 61KB
- 图片路径修复：`path.join(__dirname, '../../..', ...)` 才是正确的

- 两张图片处理：封面 113KB，内容图 151KB + 61KB
- 微信发布因 IP 问题需要重试
```

### 复盘示例：OpenScreen 文章 (2026-04-08)

```markdown
## 发布复盘: OpenScreen：免费开源的 Screen Studio 替代品

**发布时间**: 2026-04-08
**文章**: OpenScreen / openscreen-free-screen-recorder

### 本次发布遇到的问题

| 序号 | 问题描述 | 错误信息 | 根本原因 |
|------|----------|----------|----------|
| 1 | Schema 字段错误 | `InvalidContentEntryDataError: Invalid frontmatter` | 使用了 `cover` 而非 `heroImage`，`excerpt` 而非 `description` |
| 2 | 图片路径不支持子目录 | `ImageNotFound: Could not find requested image` | Astro 不支持子目录图片路径，必须放根目录 |
| 3 | 图片压缩不当 | 封面 515KB → 压缩后仍 143KB → 109KB | 未一次性设置正确的压缩质量 |
| 4 | 分支合并冲突 | `CONFLICT in pipeline/m2/renderer/wechat-renderer.js` | update-images 分支与 main 分支代码冲突 |
| 5 | 未更新公网 IP 获取命令 | 技能文档缺少简化的 IP 获取方式 | 没有记录 `curl ip.sb` 等更简单的命令 |

### 解决方案

1. **Schema 字段错误**: 检查 `src/content.config.ts`，使用正确的字段名 `heroImage` 和 `description`
2. **图片路径问题**: 将封面移到 `src/assets/` 根目录，命名为 `blog-cover-[slug].jpg`
3. **图片压缩**: 直接使用 `sips -s formatOptions 55` 一次性压缩到 ~100KB
4. **分支合并冲突**: 使用 `git checkout --ours` 保留 main 分支的完整版本（含本地图片支持）
5. **IP 获取命令**: 添加 `curl ip.sb` 和 `curl ifconfig.me` 到技能文档

### 改进措施

- [x] 更新 Skill：添加 "错误 7: Schema 字段名错误"
- [x] 更新 Skill：添加 "错误 8: 图片路径不支持子目录"
- [x] 更新 Skill：更新 IP 获取命令，添加 `curl ip.sb` 和 `curl ifconfig.me`
- [ ] 发布前检查 schema 字段名
- [ ] 封面图片统一命名格式：`blog-cover-[slug].jpg`
- [ ] 合并分支前先检查差异

### 本次新增/更新的 Skill 条目

- [错误 7]: Schema 字段名错误 (cover/heroImage, excerpt/description)
- [错误 8]: 图片路径不支持子目录
- [更新]: IP 获取命令添加简化版本

### 耗时统计

- 图片处理: 5 分钟（多次压缩尝试）
- 文章创建: 3 分钟
- 构建部署: 4 分钟（含 schema 错误排查）
- 分支合并: 3 分钟（解决冲突）
- WeChat 发布: 2 分钟
- **总计**: 17 分钟

### 备注

- 封面图：109KB，压缩质量 55%
- 合并了 feature/blog-comments 和 update-images 分支
- Blog 现在支持 Giscus 评论功能
- 分支策略：main 可直接 push，无需 PR
```

### 复盘执行检查清单

- [ ] 记录本次遇到的所有错误
- [ ] 分析每个错误的根本原因
- [ ] 记录解决方案
- [ ] 提出改进措施（预防下次发生）
- [ ] 更新 Skill 文档（添加新的错误案例）
- [ ] 统计发布耗时
- [ ] 总结可复用的经验

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
| 2026-04-08 | MemPalace 文章发布实战：添加 YAML 引号错误和微信 IP 白名单错误案例 |
| 2026-04-09 | 添加错误 9：没有使用 Skill 而手动操作；完善触发词和 skill 发现机制 |
