# XHS Publisher Skill

> 小红书自动发布 Skill - 基于 MCP CDP 服务
> 
> 维护记录：
> - 创建时间: 2026-04-16
> - 更新: 2026-04-16 - 添加图片自动压缩（~200KB）
> - 更新: 2026-04-17 - **切换到 CDP 模式（端口 18060），明确上传-发布一次性流程**
> - 更新: 2026-04-24 - 发布记录中添加 updatedDate 字段要求

---

## 🎯 触发词

| 触发词 | 功能 |
|--------|------|
| `发布到小红书` | 发布内容到小红书（Mac Mini 远程服务） |
| `发布小红书本地` | 发布内容到小红书（MacBook 本地 Chrome） |
| `小红书：主题` | 指定主题自动生成并发布 |
| `xhs测试` | 测试 MCP 服务连接 |

---

## 🚀 模式一：MacBook 本地发布（推荐）

**触发词：`发布小红书本地`**

在 MacBook 上直接运行 Chrome，无需连接 Mac Mini。

### 首次设置

```bash
# 1. 编译二进制（只需一次）
cd pipeline/deploy/xiaohongshu-mcp/src
go build -o ~/Library/Scripts/xhs-mcp-mac .

# 2. 后续启动服务
cd pipeline/deploy/xiaohongshu-mcp
./start-local.sh
# → Chrome 自动打开，服务在 localhost:18060 就绪
```

### 发布流程

```bash
export XHS=http://localhost:18060

# 1. 压缩图片
convert input.jpg -resize 900x1200> -quality 85 /tmp/img.jpg

# 2. 上传
P1=$(curl -sX POST $XHS/api/v1/upload -F "file=@/tmp/img.jpg" | \
  python3 -c "import sys,json;print(json.load(sys.stdin)['data']['path'])")

# 3. 立即发布
curl -sX POST $XHS/api/v1/publish \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"标题\",\"content\":\"正文\",\"images\":[\"$P1\"],\"tags\":[\"标签\"]}" \
  --max-time 600
```

### 服务管理

- **自动检测 Chrome**：已开就复用，没开就启动
- **binary 检查**：不存在会给出编译提示
- **日志位置**：`/tmp/xhs-mcp-local.log`

---

## 🚀 模式二：Mac Mini 远程发布

**触发词：`发布到小红书`**

通过 Tailscale 连接 Mac Mini 上的服务。

### ⚠️ 关键流程：上传 → 立即发布

**路径是一次性的！** 上传成功后必须立即发布，不能重复使用该路径。

```bash
# ========== 完整发布流程 ==========
export XHS=http://100.66.210.41:18060

# 1. 压缩图片（MacBook 本地执行）
convert input1.jpg -resize 900x1200> -quality 85 /tmp/img1.jpg
convert input2.jpg -resize 900x1200> -quality 85 /tmp/img2.jpg

# 2. 上传图片（Mac Mini 返回临时路径）
PATH1=$(curl -sX POST $XHS/api/v1/upload -F "file=@/tmp/img1.jpg" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data']['path'])")
PATH2=$(curl -sX POST $XHS/api/v1/upload -F "file=@/tmp/img2.jpg" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['data']['path'])")

echo "图片1: $PATH1"
echo "图片2: $PATH2"

# 3. 立即发布（必须使用刚上传的路径，不能等待！）
curl -sX POST $XHS/api/v1/publish \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"标题\",\"content\":\"正文内容\",\"images\":[\"$PATH1\",\"$PATH2\"],\"tags\":[\"标签1\",\"标签2\"]}" \
  --max-time 600
```

---

## 📸 图片压缩（关键！）

### 为什么必须压缩？

| 问题 | 原因 | 后果 |
|------|------|------|
| 图片太大 | 原图 1-5MB | 上传超时（60s+） |
| 尺寸不对 | 非 3:4 比例 | 小红书显示被裁剪 |
| 质量太高 | 100% quality | 文件大小翻倍 |

### 压缩参数

```bash
convert input.jpg \
  -resize 900x1200> \    # 最大 900x1200，保持比例
  -quality 85 \           # 初始质量
  output.jpg
```

**如果仍 > 200KB，逐级降级：**
- quality 85 → 75 → 65 → 55

---

## ⚠️ 重要限制

### 1. 图片要求
| 项目 | 要求 | 处理方式 |
|------|------|----------|
| **数量** | 至少 1 张 | ❌ 不传会报错 |
| **大小** | < 200KB | ✅ 本地压缩 |
| **格式** | JPG | ✅ 自动转换 |

### 2. 一次性路径（重要！）

```
❌ 错误：上传 → 等待 → 发布 → 失败 → 用同样路径重试
✅ 正确：上传 → 立即发布（成功或失败都结束了）
```

**服务端行为：**
- 上传返回的 `path` 是临时文件
- 发布完成后（无论成功失败），服务端自动删除
- 重试用同样路径会报"文件不存在"

### 3. MCP 服务（CDP 模式）

- **地址**: `http://100.66.210.41:18060`
- **模式**: CDP (Chrome DevTools Protocol)
- **要求**: Mac Mini 必须运行 Chrome + xhs-mcp-mac 二进制
- **登录**: 需先扫码登录（Mac Mini 本地浏览器）

---

## 🔧 故障排查

### 发布失败：文件不存在

**现象:** `文件不存在` / `context deadline exceeded`

**原因:** 
1. 使用了已被删除的路径（之前发布过）
2. 上传后太久才发布，路径过期

**解决:**
```bash
# 重新上传新图片，不要重用旧路径！
# ❌ 不要：curl ... -d '{"images":["/old/path.jpg"]}'
# ✅ 要：重新执行 upload 获取新路径
```

### 检查服务状态

```bash
export XHS=http://100.66.210.41:18060

# 1. 健康检查
curl $XHS/health

# 2. 登录状态
curl $XHS/api/v1/login/status

# 3. 查询限制
curl $XHS/api/v1/limits
```

### Mac Mini 服务管理

```bash
# 在 Mac Mini 上执行：
# 查看服务状态
launchctl list | grep xhs-mcp

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist
launchctl load ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist

# 查看日志
tail -f /tmp/xhs-mcp.log
```

### Mac Mini 服务管理

```bash
# 在 Mac Mini 上执行：
# 查看服务状态
launchctl list | grep xhs-mcp

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist
launchctl load ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist

# 查看日志
tail -f /tmp/xhs-mcp.log
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
- MCP 服务代码: `submodules/xiaohongshu-mcp/`
- MCP 部署配置: `pipeline/deploy/xiaohongshu-mcp/`
- 图片压缩器: `src/core/image_compressor.py`

---

## 📚 参考

- MCP 详细文档: `submodules/xiaohongshu-mcp/README.md`
- 部署指南: `pipeline/deploy/xiaohongshu-mcp/README.md`

---

## 📝 成功案例（2026-04-17）

```bash
# 内容：明天早饭是牛奶麦片，还有花生豆
# 图片：2张（花生 + 牛奶）
# 结果：✅ 发布成功

export XHS=http://100.66.210.41:18060

# 压缩图片
convert peanut.jpg -resize 900x1200> -quality 85 /tmp/peanut.jpg  # 121KB
convert milk.jpg -resize 900x1200> -quality 85 /tmp/milk.jpg      # 74KB

# 上传
PATH1=$(curl -sX POST $XHS/api/v1/upload -F "file=@/tmp/peanut.jpg" | ...)
PATH2=$(curl -sX POST $XHS/api/v1/upload -F "file=@/tmp/milk.jpg" | ...)

# 立即发布
curl -sX POST $XHS/api/v1/publish \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"明天早饭\",\"content\":\"明天早饭是牛奶麦片，还有花生豆。。。。\",\"images\":[\"$PATH1\",\"$PATH2\"],\"tags\":[\"早餐\",\"生活日常\"]}" \
  --max-time 600

# 响应：{"success": true, "message": "发布成功"}
```
