# XHS Publisher Skill

> 小红书自动发布 Skill - 基于 M3 系统封装
> 
> 维护记录：
> - 创建时间: 2026-04-16
> - 合并 M3 完整功能到主分支

---

## 🎯 触发词

| 触发词 | 功能 |
|--------|------|
| `发布到小红书` | 发布当前文章到小红书 |
| `小红书：主题` | 指定主题自动生成并发布 |
| `小红书预览` | 生成预览不发布 |
| `发布到 blog 和小红书` | 多平台同时发布 |

---

## 🏗️ 架构

```
用户输入
    ↓
Content Optimizer (小红书风格优化)
    ↓
Cover Generator (3:4 配图生成)
    ↓
Template Renderer (6种主题)
    ↓
MCP Publisher (连接 Mac Mini)
    ↓
小红书官方 API
```

---

## 📋 前置要求

### 1. Mac Mini MCP 服务部署
```bash
# 在 Mac Mini 上执行
cd pipeline/deploy/xiaohongshu-mcp
docker-compose up -d

# 扫码登录
curl http://localhost:3456/api/login-qrcode

# 验证登录
curl http://localhost:3456/api/check-login
```

### 2. 网络配置 (Tailscale)
```bash
# Mac Mini 上
brew install tailscale
sudo tailscale up

# 查看 IP
tailscale ip -4
# 输出: 100.x.x.x
```

### 3. 本地环境变量
```bash
# .env
XHS_MCP_URL=http://100.x.x.x:3456  # Mac Mini Tailscale IP
```

---

## 🚀 使用方式

### 方式 1: 一键脚本
```bash
./publish-xhs.sh content.txt [--theme blue]
```

### 方式 2: Python API
```python
from pipeline.m3.optimizer import XHSOptimizer
from pipeline.m3.cover_generator import XHSCoverGenerator
from pipeline.m3.publisher import XiaohongshuPublisher

# 优化内容
optimizer = XHSOptimizer()
result = optimizer.optimize("原始内容")

# 生成配图
generator = XHSCoverGenerator()
images = generator.generate(result['title'], count=3)

# 发布
publisher = XiaohongshuPublisher()
publisher.publish(
    title=result['title'],
    content=result['content'],
    images=images,
    tags=result['tags']
)
```

---

## 🎨 6种视觉主题

| 主题 | 名称 | 适合内容 |
|------|------|----------|
| fresh | 清新绿 | 生活、自然 |
| orange | 活力橙 | 科技、创新 |
| pink | 甜美粉 | 美妆、时尚 |
| blue | 专业蓝 | 技术、商务 |
| purple | 神秘紫 | 艺术、创意 |
| brown | 暖棕 | 文化、历史 |

---

## ⚠️ 限制与注意事项

| 项目 | 限制 | 说明 |
|------|------|------|
| 标题 | 20字 | 超过自动截断 |
| 正文 | 1000字 | 超过需精简 |
| 图片 | 1-9张 | 默认3张 |
| 发布频率 | 有风控 | 建议间隔1小时以上 |
| MCP 服务 | 必需 | 需保持 Mac Mini 运行 |

---

## 🔧 故障排查

### MCP 服务无法连接
```bash
# 检查 Mac Mini 服务状态
curl http://100.x.x.x:3456/health

# 检查 Tailscale 连接
ping 100.x.x.x
```

### 登录状态过期
```bash
# 重新扫码登录
curl http://100.x.x.x:3456/api/login-qrcode
```

---

## 📚 相关文档

- M3 详细设计: `docs/M3_Xiaohongshu_Architecture.md`
- MCP 部署指南: `pipeline/deploy/xiaohongshu-mcp/README.md`
- 测试脚本: `pipeline/m3/test-suite.sh`
