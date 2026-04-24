# XHS Publisher Skill

> 小红书自动发布 Skill - 基于 MCP 服务
> 
> 维护记录：
> - 创建时间: 2026-04-16
> - 更新: 2026-04-16 - 添加图片自动压缩（~200KB）
> - 更新: 2026-04-24 - 发布记录中添加 updatedDate 字段要求

---

## 🎯 触发词

| 触发词 | 功能 |
|--------|------|
| `发布到小红书` | 发布内容到小红书（自动压缩图片） |
| `小红书：主题` | 指定主题自动生成并发布 |

---

## 🚀 快速发布（自动压缩图片）

### 方式 1: 使用 Skill 脚本（推荐）

```bash
# 自动压缩图片到 ~200KB 并发布
./.agents/skills/xhs-publisher/scripts/publish.sh content.txt --images photo.jpg

# 多张图片
./.agents/skills/xhs-publisher/scripts/publish.sh content.txt --images img1.jpg img2.jpg img3.jpg
```

### 方式 2: 直接 curl（手动压缩）

```bash
export XHS_MCP_URL=http://100.66.210.41:3456

# 1. 压缩图片（3:4比例，~200KB）
convert input.png \
  -resize 900x1200^ \
  -gravity center \
  -extent 900x1200 \
  -quality 75 \
  output.jpg

# 2. 检查大小
ls -lh output.jpg  # 应该在 200KB 左右

# 3. 发布
curl -s $XHS_MCP_URL/api/v1/publish \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title": "标题",
    "content": "正文",
    "images": ["/absolute/path/to/output.jpg"],
    "tags": ["生活方式", "美食"]
  }'
```

---

## 📸 图片压缩（关键！）

### 为什么必须压缩？

| 问题 | 原因 | 后果 |
|------|------|------|
| 图片太大 | 原图 1-5MB | MCP 上传超时（60s+） |
| 尺寸不对 | 非 3:4 比例 | 小红书显示被裁剪 |
| 质量太高 | 100% quality | 文件大小翻倍 |

### 自动压缩参数

Skill 会自动执行以下压缩流程：

```bash
convert input.jpg \
  -resize 900x1200^ \      # 3:4 比例（小红书推荐）
  -gravity center \         # 居中裁剪
  -extent 900x1200 \        # 强制尺寸
  -quality 85 \             # 初始质量
  -strip \                  # 移除元数据
  output.jpg
```

**如果仍 > 200KB，自动降级：**
- quality 85 → 75 → 65 → 55 → 45

### 压缩示例

```bash
# 原图 3.5MB
ls -lh /Users/jason/Pictures/food.png
# 3.5M

# Skill 自动压缩后
ls -lh /tmp/xhs_images/food_xhs.jpg
# 180K ✅
```

---

## ⚠️ 重要限制

### 1. 图片要求
| 项目 | 要求 | 处理方式 |
|------|------|----------|
| **数量** | 至少 1 张 | ❌ 不传会报错 |
| **大小** | < 200KB | ✅ Skill 自动压缩 |
| **尺寸** | 3:4 (900x1200) | ✅ Skill 自动调整 |
| **格式** | JPG/PNG | ✅ 自动转换 |

### 2. MCP 服务要求
- Mac Mini 必须运行 Docker
- 必须先扫码登录
- Tailscale 网络必须连通

---

## 🔧 故障排查

### 发布超时
```bash
# 原因：图片太大
# 解决：手动压缩到 < 100KB
convert input.jpg -resize 900x1200 -quality 65 output.jpg
```

### 图片上传失败
```bash
# 检查图片是否存在
ls -la /path/to/image.jpg

# 检查是否可读取
file /path/to/image.jpg
```

### 检查服务状态
```bash
# 1. MCP 健康
curl http://100.66.210.41:3456/health

# 2. 登录状态
curl http://100.66.210.41:3456/api/v1/login/status

# 3. 查看日志（Mac Mini 上）
docker logs xhs-mcp --tail 50
```

---

## 📝 发布记录规范

每次通过 XHS Publisher 发布内容后，同步更新对应博客文章的 `updatedDate` 字段（如果该内容同时有博客版本）：

```yaml
# 在对应的 src/content/blog/SLUG.md frontmatter 中：
updatedDate: "YYYY-MM-DD"  # 填写今天日期
```

这确保博客 sitemap 的 `<lastmod>` 反映最新发布时间，提升 Perplexity 等 AI 引擎的内容新鲜度信号。

---

## 📁 文件位置

- Skill 代码: `.agents/skills/xhs-publisher/`
- 图片压缩器: `src/core/image_compressor.py`
- MCP 服务: `pipeline/deploy/xiaohongshu-mcp/`
- 发布脚本: `scripts/publish.sh`

---

## 📚 参考

- MCP 详细文档: `submodules/xiaohongshu-mcp/README.md`
- 部署指南: `pipeline/deploy/xiaohongshu-mcp/README.md`
- Blog Publisher: `.agents/skills/blog-publisher/SKILL.md`
