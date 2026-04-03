# AI 内容生产 Pipeline 设计文档

## 1. 项目概述

构建从内容创作到多平台发布的端到端 AI 内容生产管线，实现：
- **M1**: 文字 → Markdown → Blog 发布（已完成，需优化）
- **M2**: Markdown → 微信公众号格式 → 发布草稿
- **M3**: 完整 Pipeline（选题 → 写作 → 评估 → 排版 → 多平台发布）

---

## 2. Claude Skill 复用性分析

### 2.1 能否直接复用？

**答案：不能直接复用，但可以借鉴设计思路**

#### 原因分析：

| 维度 | Claude Skill | Kimi 实现 |
|------|-------------|-----------|
| **机制** | 目录 + SKILL.md + 工具调用 | 会话式交互 |
| **触发** | 自然语言关键词匹配 | 直接指令 |
| **上下文** | 持久化 Skill 上下文 | 单次会话 |
| **工具** | 内置工具（读文件、执行代码等） | 需显式调用 |

#### Claude Skill 结构（wechat-content-pipeline）:
```
skills/wechat-formatter/
├── SKILL.md          # 主定义文件（路由 + 工作流）
└── references/       # 按需加载的参考文档
    ├── themes.md
    ├── element-styles.md
    └── ...
```

#### 借鉴方案：

1. **Prompt 模板化**: 提取 SKILL.md 中的 System Prompt 和 Step-by-Step 流程
2. **工作流抽象**: 将 Skill 的多步骤流程转化为可复用的函数/脚本
3. **配置外置**: 将主题、样式等配置抽取为独立 JSON/CSS 文件
4. **工具封装**: 将 API 调用、文件操作等封装为独立工具模块

---

## 3. 架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Content Pipeline                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   M1: Blog   │  M2: WeChat  │   M3: Full   │   Extensible   │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  Text Input  │   Markdown   │   Topic AI   │   Twitter/X    │
│      ↓       │      ↓       │      ↓       │       ↓        │
│   Polisher   │  Formatter   │   Writer     │    Threads     │
│      ↓       │      ↓       │      ↓       │       ↓        │
│   Astro MD   │   WeChat     │  Evaluator   │    LinkedIn    │
│      ↓       │    HTML      │      ↓       │       ↓        │
│   Publish    │      ↓       │  Publisher   │     More...    │
│              │   Publish    │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

### 3.2 模块划分

```
pipeline/
├── core/                      # 核心引擎
│   ├── polisher.py           # AI 润色（去 AI 味）
│   ├── formatter.py          # Markdown → HTML 转换
│   └── publisher.py          # 多平台发布抽象层
│
├── platforms/                 # 平台适配器
│   ├── blog/                 # Astro Blog（M1）
│   │   ├── templates/        # 文章模板
│   │   └── publisher.py      # 本地构建 + Git 提交
│   │
│   ├── wechat/               # 微信公众号（M2）
│   │   ├── themes/           # 4种主题（借鉴 wechat-article-formatter）
│   │   │   ├── claude/       # 简约橙色
│   │   │   ├── chengyun/     # 渐变杂志风
│   │   │   ├── blue/         # 蓝色专业
│   │   │   └── sticker/      # 贴纸风格
│   │   ├── formatter.py      # Markdown → WeChat HTML
│   │   └── publisher.py      # 微信 API/CDP 发布
│   │
│   └── xiaohongshu/          # 小红书（M3+）
│       └── card_generator.py # 9:16 卡片生成
│
├── ai/                        # AI 能力层（M3）
│   ├── topic.py              # 选题分析（热点追踪）
│   ├── writer.py             # AI 写作（5种文章类型）
│   └── evaluator.py          # 质量门禁（5维度评估）
│
├── assets/                    # 资源生成（M3）
│   ├── cover_gen.py          # AI 封面图生成
│   ├── image_gen.py          # 智能配图
│   └── infographic.py        # 信息图生成
│
└── utils/                     # 工具库
    ├── image.py              # 图片处理/上传
    ├── css_inline.py         # CSS 内联（Juice）
    └── markdown.py           # Markdown 解析/规范化
```

---

## 4. 里程碑详细规划

### M1: Blog Pipeline（已完成，待优化）

**目标**: 文字输入 → 优化 Markdown → 发布到 Blog

**现状**: 
- ✅ 基础模板已存在
- ✅ Astro 构建正常
- ⚠️ 缺少 AI 润色环节
- ⚠️ 发布流程需自动化

**M1 改进任务**:

| 任务 | 描述 | 优先级 |
|------|------|--------|
| T1 | 创建 `pipeline/m1/` 目录结构 | P0 |
| T2 | 实现 `polisher.py` - AI 润色（去 AI 味） | P0 |
| T3 | 创建文章模板选择机制（技术/研究/随笔） | P1 |
| T4 | 一键发布脚本（build + deploy.sh） | P1 |
| T5 | 图片自动处理（压缩 → assets/） | P2 |

**M1 工作流程**:
```
用户输入文字 → 选择模板类型 → AI 润色 → 生成 Frontmatter → 
保存到 src/content/blog/ → 自动 build → 自动 deploy
```

### M2: WeChat Pipeline

**目标**: Markdown → 微信 HTML → 发布草稿

**借鉴来源**: 
- `wechat-article-formatter`: 4种主题 + CSS 兼容性处理
- `wechat-article-formatter-skill`: bm.md 渲染 API
- `wechat-article-publisher-skill`: API-based 发布

**M2 实现任务**:

| 任务 | 描述 | 依赖 |
|------|------|------|
| T1 | 移植 4 种主题样式到 `platforms/wechat/themes/` | wechat-article-formatter |
| T2 | 实现 CSS 兼容性引擎（div→table 等） | wechat-article-formatter |
| T3 | 对接 bm.md API 渲染服务 | wechat-article-formatter-skill |
| T4 | 实现图片上传到微信 CDN | wechat-article-formatter-skill |
| T5 | 对接微信 draft/add API | wechat-article-formatter-skill |
| T6 | 配置 `.env` 模板（WECHAT_APP_ID/SECRET） | - |
| T7 | 一键发布脚本 `publish-wechat.sh` | T1-T6 |

**M2 工作流程**:
```
Blog Markdown → 提取正文 → 选择主题 → 渲染 WeChat HTML → 
上传图片到 CDN → 替换图片 URL → 调用 draft/add API → 
返回草稿链接
```

**M2 配置示例**:
```bash
# ~/.env
WECHAT_APP_ID=wx_xxxxxxxxxxxx
WECHAT_APP_SECRET=xxxxxxxxxxxxxxxx
BM_MD_API_KEY=optional_for_custom_css
```

### M3: Full Pipeline

**目标**: 完整内容生产管线（选题 → 写作 → 评估 → 排版 → 发布）

**借鉴来源**:
- `wechat-content-pipeline`: 6个 Skill 的完整工作流

**M3 实现任务**:

| 模块 | 功能 | 关键特性 |
|------|------|----------|
| **Topic AI** | 热点选题分析 | 追踪 AI/区块链/开发热点 |
| **Writer** | AI 写作 | 5种类型：观点/教程/盘点/评论/故事 |
| **Evaluator** | 质量门禁 | 5维度：内容/结构/可读性/原创性/SEO |
| **Polisher** | 文章润色 | 8种：grammar/style/title/structure/deai/readability/summary/seo |
| **Formatter** | 多平台排版 | Blog + WeChat + 小红书 |
| **Asset Gen** | 资源生成 | 封面图/配图/信息图/小红书卡片 |
| **Publisher** | 多平台发布 | Blog → WeChat → 小红书（串行）|

**M3 工作流程**:
```
[1] 选题 AI 推荐热点话题
      ↓ 用户确认
[2] AI Writer 生成文章大纲
      ↓ 用户确认
[3] AI Writer 生成完整文章
      ↓
[4] Evaluator 质量评估（100分制）
      ↓ 评分<80? → 返回修改
[5] Polisher 润色（去 AI 味）
      ↓ 用户确认
[6] 生成封面图 + 配图
      ↓ 用户确认
[7] 多平台排版（Blog/WeChat/小红书）
      ↓ 用户确认
[8] 一键发布到各平台
```

---

## 5. 技术选型

### 5.1 核心依赖

| 功能 | 选型 | 理由 |
|------|------|------|
| Markdown 解析 | `marked` + `marked-footnote` | wechat-content-suite 验证 |
| CSS 内联 | `juice` | 微信兼容性要求 |
| HTML 渲染 | `bm.md API` | 无需自建渲染服务 |
| 图像生成 | `Gemini API` | 支持封面/配图/信息图 |
| HTTP 请求 | `undici` | Node.js 官方推荐 |
| 微信 API | 官方 `draft/add` | 避免第三方 API 剥离样式 |

### 5.2 项目结构

```
blog/                           # 现有项目
├── docs/                       # 设计文档（当前目录）
├── pipeline/                   # 新增: AI Pipeline
│   ├── m1/                    # M1: Blog Pipeline
│   │   ├── polisher.py
│   │   ├── templates/
│   │   └── publish.py
│   │
│   ├── m2/                    # M2: WeChat Pipeline
│   │   ├── platforms/
│   │   │   └── wechat/
│   │   │       ├── themes/
│   │   │       ├── formatter.py
│   │   │       └── publisher.py
│   │   └── publish-wechat.sh
│   │
│   └── m3/                    # M3: Full Pipeline
│       ├── ai/
│       │   ├── topic.py
│       │   ├── writer.py
│       │   └── evaluator.py
│       ├── assets/
│       │   ├── cover_gen.py
│       │   └── image_gen.py
│       └── pipeline.py        # 主入口
│
├── submodules/                # 参考子模块（只读）
│   ├── wechat-content-pipeline/
│   ├── wechat-article-formatter/
│   ├── wechat-article-formatter-skill/
│   └── wechat-article-publisher-skill/
│
└── src/content/blog/          # 文章目录
```

---

## 6. 实现策略

### 6.1 渐进式开发

```
Phase 1: M1 优化（1周）
   - 稳定现有的 Blog 发布流程
   - 添加 AI 润色环节

Phase 2: M2 微信（2周）
   - 移植 4 种主题
   - 对接微信 API
   - 实现一键发布

Phase 3: M3 完整（4周+）
   - AI 写作能力
   - 质量评估
   - 资源生成
   - 多平台协调
```

### 6.2 与现有 Blog 集成

```python
# 伪代码：M2 发布流程
def publish_to_wechat(markdown_file):
    # 1. 读取 Blog Markdown
    article = parse_frontmatter(markdown_file)
    
    # 2. 选择主题并渲染
    html = render_with_bmmd(
        markdown=article.content,
        theme="green-simple",
        custom_css=load_theme_css("claude")
    )
    
    # 3. 上传图片到微信 CDN
    image_map = upload_images_to_wechat(
        article.images,
        app_id=env.WECHAT_APP_ID,
        app_secret=env.WECHAT_APP_SECRET
    )
    
    # 4. 替换图片 URL
    html = replace_image_urls(html, image_map)
    
    # 5. 发布草稿
    draft_id = wechat_api.draft.add(
        title=article.title,
        content=html,
        thumb_media_id=image_map.cover_id
    )
    
    return f"https://mp.weixin.qq.com/.../draft_id={draft_id}"
```

---

## 7. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 微信 API 限制 | 高 | 使用官方 API，避免第三方；做好错误重试 |
| bm.md 服务不稳定 | 中 | 预留自建渲染方案（marked + juice）|
| AI 生成内容质量 | 中 | 人工确认点设计；质量门禁评估 |
| 图片版权问题 | 中 | 使用 AI 生成图片；标注来源 |

---

## 8. 附录

### 8.1 参考子模块功能对照

| 功能 | wechat-content-pipeline | wechat-article-formatter | wechat-article-formatter-skill | wechat-article-publisher-skill |
|------|------------------------|-------------------------|-------------------------------|------------------------------|
| Markdown→HTML | ✅ CLI | ✅ CLI | ✅ API | - |
| 主题系统 | 3种 | 4种 | - | - |
| AI 润色 | ✅ 8种 | - | - | - |
| 封面生成 | ✅ | - | - | - |
| 智能配图 | ✅ | - | - | - |
| 信息图 | ✅ | - | - | - |
| 小红书 | ✅ | - | - | - |
| 微信发布 | ✅ API | ✅ CDP | ✅ API | ✅ API |
| AI 写作 | ✅ | - | - | - |
| 质量评估 | ✅ | - | - | - |
| 选题 | ✅ | - | - | - |

### 8.2 关键设计决策

1. **为什么不用 CDP（浏览器自动化）？**
   - CDP 需要本地 Chrome，部署复杂
   - API 方式更稳定，跨平台
   - 微信官方 API 支持 draft/add

2. **为什么优先 bm.md 而非自建渲染？**
   - bm.md 已解决微信兼容性
   - 支持多种主题
   - 维护成本低

3. **为什么分 M1/M2/M3？**
   - 渐进式降低风险
   - M1 已可用，快速验证价值
   - M2 解决核心痛点（微信发布）
   - M3 构建完整能力

