# 小红书自动发布工具调研报告

## 执行摘要

通过 GitHub CLI 搜索并调研了当前主流的小红书自动发布开源方案，发现了两种技术路线：浏览器自动化（CDP/Selenium）和 API 调用。本报告分析 Top 10 相关 Repository，并提出适合融入本地 AI Skill 的技术方案。

---

## Top 10 小红书自动发布 Repository 调研

### 1. XiaohongshuSkills (white0dew) ⭐ 2549
- **GitHub**: https://github.com/white0dew/XiaohongshuSkills
- **技术栈**: Python + Chrome DevTools Protocol (CDP)
- **核心功能**: 
  - 自动发布/评论/检索
  - 支持 OpenClaw、Codex、CC 等 Agent 框架
  - 基于浏览器 CDP 协议控制
- **优势**: 星数最高、功能最全、支持多框架集成
- **劣势**: 需要保持浏览器运行、依赖 Cookie 登录状态
- **适用场景**: 需要完整浏览器环境的自动化任务

### 2. xiaohongshu-bot (xTreeRoot) ⭐ 18
- **GitHub**: https://github.com/xTreeRoot/xiaohongshu-bot
- **技术栈**: Python + Selenium
- **核心功能**: 基于 Selenium 的自动化发帖、回复评论
- **优势**: 简单易用、Selenium 生态成熟
- **劣势**: Selenium 相对 CDP 更重、容易被检测
- **适用场景**: 快速原型开发、小规模自动化

### 3. tweet-to-xiaohongshu (dontbesilent12) ⭐ 5
- **GitHub**: https://github.com/dontbesilent12/tweet-to-xiaohongshu
- **技术栈**: Go
- **核心功能**: 
  - AI 智能生成标题
  - 一键截图发布
- **优势**: 编译型语言性能高、AI 集成
- **劣势**: 功能相对单一
- **适用场景**: 内容创作者快速分发

### 4. xiaohongshu-agent (jingjiansoft) ⭐ 2
- **GitHub**: https://github.com/jingjiansoft/xiaohongshu-agent
- **技术栈**: TypeScript
- **核心功能**: 
  - 多模型接入
  - 自动生成内容并发布
- **优势**: TypeScript 类型安全、现代开发体验
- **劣势**: 星数较低、社区活跃度待观察
- **适用场景**: 需要多模型集成的场景

### 5. xhs-skill (PengJiyuan) ⭐ 6
- **GitHub**: https://github.com/PengJiyuan/xhs-skill
- **技术栈**: JavaScript/Node.js
- **核心功能**: OpenClaw Skill 封装
- **优势**: 专注 OpenClaw 生态
- **劣势**: 绑定特定框架
- **适用场景**: OpenClaw 用户

### 6-10. 其他相关 Repository
- **openclaw-xiaohongshu-skill**: OpenClaw 生态的小红书 Skill
- **xhs-auto-publisher**: AI 生成文案 + Playwright 自动发布
- **xiaohongshu-auto-publisher (bradstan)**: 基础自动化工作流
- **mcp-xhs-publisher**: MCP 协议封装的小红书发布工具
- **openclaw-xiaohongshu-auto-publish**: Playwright + CDP 自动化

---

## 技术路线对比分析

| 技术路线 | 代表项目 | 优势 | 劣势 | 推荐度 |
|---------|---------|------|------|--------|
| **CDP (Chrome DevTools Protocol)** | XiaohongshuSkills | 轻量、高效、可调试 | 需要保持浏览器进程 | ⭐⭐⭐⭐⭐ |
| **Selenium** | xiaohongshu-bot | 生态成熟、文档丰富 | 资源占用高、易被检测 | ⭐⭐⭐ |
| **Playwright** | xhs-auto-publisher | 微软出品、API 友好 | 相对 CDP 更重 | ⭐⭐⭐⭐ |
| **API 调用** | 无公开项目 | 稳定、快速 | 小红书无公开 API | ❌ 不可行 |

---

## 推荐技术方案

### 核心架构：CDP + Python

基于调研结果，推荐采用 **XiaohongshuSkills** 的技术路线：

```
┌─────────────────────────────────────────────────────────────┐
│                    本地 AI Skill 架构                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   内容生成    │  │   图片处理    │  │   定时调度       │  │
│  │  (LLM API)   │  │  (Pillow)    │  │  (APScheduler)   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│         └──────────────────┼────────────────────┘            │
│                            ▼                                 │
│                   ┌─────────────────┐                        │
│                   │  XHS Publisher  │                        │
│                   │   Skill Core    │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│              ┌─────────────┴─────────────┐                   │
│              ▼                           ▼                   │
│    ┌──────────────────┐      ┌────────────────────┐         │
│    │  Chrome Browser  │      │   Cookie Manager   │         │
│    │  (CDP Protocol)  │      │   (Session Store)  │         │
│    └────────┬─────────┘      └────────────────────┘         │
│             │                                                │
│             ▼                                                │
│    ┌──────────────────┐                                     │
│    │   小红书 Web     │                                     │
│    └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

### 技术选型理由

1. **CDP 协议**: 直接控制 Chrome，比 Selenium 更轻量、更难被检测
2. **Python**: 与现有 AI 生态（LLM 调用、图像处理）无缝集成
3. **Cookie 持久化**: 避免频繁登录，提高稳定性
4. **模块化设计**: 便于集成到更大的 Agent 系统中

---

## 完整工作流程

### Phase 1: 内容准备
```python
# 1. 内容生成
content = llm.generate("根据主题生成小红书文案")

# 2. 图片处理
images = process_images(raw_images, watermark=True)

# 3. 标题优化
title = generate_title(content, keywords=["AI", "效率工具"])
```

### Phase 2: 发布执行
```python
# 4. 初始化浏览器
browser = CDPBrowser(headless=True)

# 5. 登录（使用缓存 Cookie）
xhs = XHSPublisher(browser)
xhs.login_with_cookies(stored_cookies)

# 6. 发布内容
xhs.publish(
    title=title,
    content=content,
    images=images,
    tags=["AI工具", "效率"]
)

# 7. 清理
browser.close()
```

### Phase 3: 监控反馈
```python
# 8. 获取数据
stats = xhs.get_post_stats(post_id)

# 9. 互动管理
comments = xhs.get_comments(post_id)
xhs.reply_comment(comment_id, reply_content)
```

---

## 融入本地 AI Skill 的方案

### 1. Skill 结构设计

```
.agents/skills/xhs-publisher/
├── SKILL.md              # Skill 文档
├── config.yaml           # 配置模板
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── publisher.py  # 核心发布逻辑
│   │   ├── browser.py    # CDP 浏览器控制
│   │   └── auth.py       # 登录认证管理
│   ├── content/
│   │   ├── generator.py  # AI 内容生成
│   │   └── processor.py  # 图片/视频处理
│   └── utils/
│       ├── cookies.py    # Cookie 管理
│       └── scheduler.py  # 定时任务
└── tests/
    └── test_publisher.py
```

### 2. 触发词设计

| 触发词 | 功能 |
|--------|------|
| "发布到小红书" | 使用默认配置发布 |
| "小红书：主题" | 指定主题自动生成并发布 |
| "小红书定时：时间" | 设置定时发布 |
| "小红书数据" | 获取最近发布数据统计 |

### 3. 配置示例

```yaml
# config.yaml
xiaohongshu:
  # 登录配置
  auth:
    cookie_path: "~/.config/xhs-publisher/cookies.json"
    session_ttl: 86400  # 24小时
  
  # 内容生成配置
  content:
    llm_provider: "openai"  # 或本地模型
    model: "gpt-4o-mini"
    max_length: 1000
    default_tags: ["AI", "效率工具", "技术分享"]
  
  # 发布策略
  publishing:
    default_time: "09:00"  # 默认发布时间
    interval_min: 3600     # 最小发布间隔（秒）
    retry_count: 3         # 失败重试次数
  
  # 浏览器配置
  browser:
    headless: true
    user_data_dir: "~/.config/xhs-publisher/chrome"
    viewport: { width: 1920, height: 1080 }
```

### 4. 集成到现有 Blog Publisher

```python
# 扩展现有 blog-publisher skill
class UnifiedPublisher:
    def publish(self, content, platforms: List[str]):
        """
        platforms: ["blog", "wechat", "xiaohongshu"]
        """
        results = {}
        
        if "blog" in platforms:
            results["blog"] = self.publish_to_blog(content)
            
        if "wechat" in platforms:
            results["wechat"] = self.publish_to_wechat(content)
            
        if "xiaohongshu" in platforms:
            # 转换内容为小红书格式
            xhs_content = self.convert_to_xhs_format(content)
            results["xiaohongshu"] = self.publish_to_xhs(xhs_content)
            
        return results
```

---

## 风险与应对

| 风险 | 应对措施 |
|------|----------|
| 账号封禁 | 控制发布频率、模拟人工操作、使用独立账号 |
| Cookie 过期 | 定期更新、自动重登录机制 |
| 页面结构变更 | 使用相对稳定的 CDP 选择器、定期更新 |
| 内容审核 | AI 预审内容、避免敏感词 |

---

## 下一步行动

1. **验证可行性**: 跑通 XiaohongshuSkills 基础流程
2. **封装 Skill**: 按照上述结构创建 xhs-publisher skill
3. **集成测试**: 与现有 blog-publisher 集成测试
4. **文档编写**: 完善 SKILL.md 使用文档

---

*报告生成时间: 2026-04-15*
*调研工具: GitHub CLI (gh)*
