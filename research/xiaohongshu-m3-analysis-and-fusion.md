# M3 小红书系统分析 & 融合方案

## 📋 现状分析

发现 `research-xiaohongshu` 分支已有完整的 **M3 小红书自动发布系统**，基于 `xpzouying/xiaohongshu-mcp` 构建。

---

## 🔍 M3 现有系统架构

```
┌────────────────────────────────────────────────────────────────┐
│                    M3 小红书发布系统                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 内容优化器    │    │  配图生成器   │    │  模板渲染器   │     │
│  │ optimizer.py │    │ cover_gen.py │    │  renderer/   │     │
│  │              │    │              │    │              │     │
│  │ • 小红书风格 │    │ • 3:4 比例   │    │ • 6种模板    │     │
│  │ • Emoji添加 │    │ • 6种主题   │    │ • HTML输出   │     │
│  │ • 标签提取  │    │ • 水印添加  │    │              │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              publisher.py (HTTP Client)                  │  │
│  │         连接 MCP 服务: xpzouying/xiaohongshu-mcp         │  │
│  └───────────────────────────┬─────────────────────────────┘  │
│                              │                                 │
│                              ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Docker: xiaohongshu-mcp                                │  │
│  │  • 小红书 API 封装                                       │  │
│  │  • Cookie 持久化                                        │  │
│  │  • 扫码登录                                             │  │
│  │  • 图片上传                                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 状态 | 说明 |
|------|------|------|
| `optimizer.py` | ✅ 完成 | 小红书风格优化，emoji/标签自动添加 |
| `cover_generator.py` | ✅ 完成 | 900x1200 配图，6种配色主题 |
| `renderer/` | ✅ 完成 | 6种视觉模板，HTML/富文本输出 |
| `publisher.py` | ✅ 完成 | MCP HTTP Client，连接 Docker 服务 |
| `publish-xhs.sh` | ✅ 完成 | 一键发布脚本 |
| Docker MCP | ✅ 配置 | `xpzouying/xiaohongshu-mcp:latest` |

---

## ⚖️ 方案对比：M3 vs GitHub 调研方案

| 维度 | M3 现有系统 | GitHub 调研方案 |
|------|------------|----------------|
| **API 方式** | MCP HTTP 服务 | CDP 浏览器自动化 |
| **小红书连接** | 封装好的 MCP Docker | 直接控制浏览器 |
| **稳定性** | ⭐⭐⭐⭐⭐ Cookie持久化 | ⭐⭐⭐ 依赖浏览器状态 |
| **维护成本** | 低（Docker托管） | 高（需维护浏览器） |
| **部署难度** | 中等（需Mac Mini） | 低（本地运行） |
| **功能完整性** | ✅ 内容+配图+模板全套 | ❌ 需自行开发 |

### 结论
**M3 现有系统明显更优**，采用成熟的 MCP 服务而非浏览器自动化。

---

## 🚀 融合方案：M3 + 本地 AI Skill 集成

### 目标
将 M3 系统融入 `.agents/skills/xhs-publisher/`，与现有 M1/M2 统一。

### 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│              Unified Publisher Skill (本地 AI)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Trigger: "发布到小红书" / "小红书：主题" / "小红书定时：时间" │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                               │                                  │
│  ┌────────────────────────────┼───────────────────────────────┐ │
│  │                            ▼                               │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │          xhs-publisher Skill Core                   │  │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │ │
│  │  │  │  Content    │  │   Cover     │  │   Template  │  │  │ │
│  │  │  │  Optimizer  │  │  Generator  │  │   Render    │  │  │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │ │
│  │  └─────────────────────────┬───────────────────────────┘  │ │
│  │                            │                               │ │
│  │  ┌─────────────────────────▼────────────────────────────┐  │ │
│  │  │              MCP Client (publisher.py)                │  │ │
│  │  │         连接远程 MCP 服务 (Mac Mini/Tailscale)       │  │ │
│  │  └─────────────────────────┬────────────────────────────┘  │ │
│  └────────────────────────────┼───────────────────────────────┘ │
│                               │                                  │
│                    ┌──────────┴──────────┐                       │
│                    ▼                     ▼                       │
│  ┌────────────────────────┐  ┌────────────────────────┐          │
│  │    M1: Blog            │  │    M2: WeChat          │          │
│  │    (已有)              │  │    (已有)              │          │
│  └────────────────────────┘  └────────────────────────┘          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │    M3: XiaoHongShu                                         │  │
│  │    ┌────────────────────────────────────────────────────┐  │  │
│  │    │  Mac Mini (机房)                                    │  │  │
│  │    │  ┌──────────────────────────────────────────────┐  │  │  │
│  │    │  │  Docker: xpzouying/xiaohongshu-mcp          │  │  │  │
│  │    │  │  • Port: 3456                                │  │  │  │
│  │    │  │  • Cookie 持久化                             │  │  │  │
│  │    │  │  • 扫码登录                                  │  │  │  │
│  │    │  └──────────────────────────────────────────────┘  │  │  │
│  │    └────────────────────────────────────────────────────┘  │  │
│  │                         ▲                                  │  │
│  │                         │ Tailscale/Frp                   │  │
│  │                         │ (内网穿透)                      │  │
│  └─────────────────────────┼──────────────────────────────────┘  │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   小红书官方    │
                    │   API/CDN      │
                    └─────────────────┘
```

---

## 📁 Skill 文件结构

```
.agents/skills/xhs-publisher/
├── SKILL.md                    # Skill 文档
├── config.yaml                 # 配置文件模板
├── requirements.txt            # Python 依赖
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── skill.py           # Skill 主入口
│   │   ├── optimizer.py       # 内容优化器 (从 M3 迁移)
│   │   ├── cover_generator.py # 配图生成器 (从 M3 迁移)
│   │   └── template.py        # 模板渲染器 (从 M3 迁移)
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── client.py          # MCP HTTP Client (从 M3 迁移)
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # 配置管理
│       └── logger.py          # 日志工具
├── scripts/
│   └── publish-xhs.sh         # 一键发布脚本 (从 M3 迁移)
└── tests/
    └── test_publisher.py
```

---

## 🔧 需要完成的任务

### Phase 1: MCP 服务部署 (基础设施)
- [ ] 在 Mac Mini 上部署 `xiaohongshu-mcp` Docker
- [ ] 配置 Tailscale/frp 内网穿透
- [ ] 扫码登录并验证 Cookie 持久化
- [ ] 测试 API 连通性

### Phase 2: Skill 迁移
- [ ] 迁移 `optimizer.py` → `src/core/optimizer.py`
- [ ] 迁移 `cover_generator.py` → `src/core/cover_generator.py`
- [ ] 迁移 `renderer/` → `src/core/template.py`
- [ ] 迁移 `publisher.py` → `src/mcp/client.py`
- [ ] 迁移 `publish-xhs.sh` → `scripts/publish-xhs.sh`

### Phase 3: Skill 封装
- [ ] 创建 `SKILL.md` 文档
- [ ] 定义触发词和参数
- [ ] 集成到 `blog-publisher` 统一入口
- [ ] 添加错误处理和重试机制

### Phase 4: 统一发布入口
```python
# 示例：统一发布
用户输入: "发布：AI新文章.md 到 blog 和小红书"

skill.publish(
    content="AI新文章.md",
    platforms=["blog", "xiaohongshu"],
    options={
        "xiaohongshu": {
            "theme": "blue",
            "image_count": 3
        }
    }
)
```

---

## 📝 配置文件示例

```yaml
# .agents/skills/xhs-publisher/config.yaml

# MCP 服务连接
mcp:
  # 可通过 Tailscale IP 或 frp 域名访问
  url: "http://100.x.x.x:3456"  # Mac Mini Tailscale IP
  timeout: 60
  retry_count: 3

# 内容优化
content:
  max_title_length: 20
  max_content_length: 1000
  default_category: "tech"
  emoji_density: "medium"  # low/medium/high

# 配图生成
cover:
  width: 900
  height: 1200
  default_theme: "blue"
  available_themes:
    - fresh    # 清新绿
    - orange   # 活力橙
    - pink     # 甜美粉
    - blue     # 专业蓝
    - purple   # 神秘紫
    - brown    # 暖棕
  watermark: true
  watermark_text: "Mushroom Blog"

# 发布策略
publishing:
  min_interval: 3600  # 最小发布间隔（秒）
  max_daily_posts: 5  # 每日最大发布数
  auto_schedule: true
  default_publish_time: "09:00"

# 安全设置
security:
  confirm_before_publish: true
  allow_sensitive_topics: false
```

---

## 🎯 触发词设计

| 触发词 | 功能 |
|--------|------|
| `发布到小红书` | 发布当前文章到小红书 |
| `小红书：主题` | 指定主题自动生成并发布 |
| `小红书定时：时间` | 设置定时发布 |
| `小红书预览` | 生成预览不发布 |
| `小红书数据` | 获取最近发布数据 |
| `发布到 blog 和小红书` | 多平台同时发布 |

---

## ⚠️ 风险评估

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| MCP 服务不可用 | 高 | 本地 Docker 备份、健康检查 |
| 小红书账号封禁 | 高 | 控制频率、模拟人工、小号测试 |
| 网络不稳定 | 中 | Tailscale + frp 双通道 |
| Cookie 过期 | 中 | 自动检测、提醒重登录 |

---

## ✅ 下一步行动

1. **立即行动**: 在 Mac Mini 上部署 MCP 服务
   ```bash
   cd pipeline/deploy/xiaohongshu-mcp
   docker-compose up -d
   ```

2. **本周完成**: 测试完整发布流程
   ```bash
   ./publish-xhs.sh test-content.md
   ```

3. **下周完成**: Skill 封装和文档
   - 创建 `.agents/skills/xhs-publisher/`
   - 编写 `SKILL.md`
   - 集成到主流程

4. **长期优化**: 统一 M1/M2/M3 发布入口

---

## 📚 参考资源

- M3 设计文档: `docs/M3_Xiaohongshu_Architecture.md`
- MCP 部署指南: `pipeline/deploy/xiaohongshu-mcp/README.md`
- MCP 镜像: https://github.com/xpzouying/xiaohongshu-mcp
- GitHub 调研: `research/xiaohongshu-auto-publish-research.md`

---

*分析时间: 2026-04-15*
*结论: M3 系统已成熟，只需完成部署和 Skill 封装即可投入使用*
