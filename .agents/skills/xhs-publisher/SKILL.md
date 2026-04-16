# XHS Publisher Skill

> 小红书自动发布 Skill - 基于 MCP 服务
> 
> 维护记录：
> - 创建时间: 2026-04-16
> - 更新: 2026-04-16 - 添加失败教训、简化发布流程

---

## 🎯 触发词

| 触发词 | 功能 |
|--------|------|
| `发布到小红书` | 发布内容到小红书 |
| `小红书：主题` | 指定主题自动生成并发布 |

---

## 🚀 快速发布（推荐方式）

### 方式 1: 直接 curl（最稳定）

```bash
export XHS_MCP_URL=http://100.66.210.41:3456

# 准备内容
cat > /tmp/post.txt << 'EOF'
忘记拍红烧肉了，村里的小饭店，真不错~
EOF

# 准备图片（压缩到 < 500KB）
convert input.png -resize 900x1200 -quality 85 /tmp/cover.jpg

# 发布
curl -s $XHS_MCP_URL/api/v1/publish \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$(head -1 /tmp/post.txt)\",\n    \"content\": \"正文内容\",\n    \"images\": [\"/tmp/cover.jpg\"],\n    \"tags\": [\"生活方式\", \"美食\"]\n  }"
```

### 方式 2: 使用 Skill 脚本

```bash
./.agents/skills/xhs-publisher/scripts/publish.sh content.txt --images photo.jpg
```

---

## ⚠️ 重要限制（失败教训）

### 1. 图片要求
| 项目 | 要求 | 失败案例 |
|------|------|----------|
| **数量** | 至少 1 张 | 不传图片会报错 `min: 1` |
| **大小** | < 500KB | 1.7MB 图片导致超时 |
| **格式** | JPG/PNG | - |
| **路径** | 本地绝对路径 | 相对路径可能失败 |

### 2. 压缩图片命令
```bash
# 压缩到 900x1200，质量 85%
convert input.png -resize 900x1200 -quality 85 output.jpg

# 或用 magick (ImageMagick 7+)
magick input.png -resize 900x1200 -quality 85 output.jpg
```

### 3. MCP 服务要求
- 必须先扫码登录
- Mac Mini 必须运行 Docker
- Tailscale 网络必须连通

---

## 🔧 故障排查

### 检查服务状态
```bash
# 1. 检查 MCP 健康
curl http://100.66.210.41:3456/health

# 2. 检查登录状态
curl http://100.66.210.41:3456/api/v1/login/status

# 3. 查看 MCP 日志（Mac Mini 上）
docker logs xhs-mcp --tail 50
```

### 常见问题

**Q: 发布超时怎么办？**  
A: 图片太大，压缩到 < 500KB

**Q: 提示需要图片怎么办？**  
A: MCP 强制要求至少 1 张图片，必须提供

**Q: 图片路径怎么写？**  
A: 使用本地绝对路径，如 `/Users/xxx/Pictures/photo.jpg`

---

## 📁 文件位置

- MCP 服务: `pipeline/deploy/xiaohongshu-mcp/`
- Skill 封装: `.agents/skills/xhs-publisher/`
- 发布脚本: `publish-xhs.sh`

---

## 📚 参考

- MCP 详细文档: `submodules/xiaohongshu-mcp/README.md`
- 部署指南: `pipeline/deploy/xiaohongshu-mcp/README.md`
