# M3 小红书自动发布系统 - 详细设计文档

## 1. 项目概述

### 1.1 目标
构建与 M1(Blog)、M2(微信公众号) 类似的自动化发布系统，实现：
```
用户输入内容 → AI优化 → 随机模板 → 自动配图 → 发布到小红书草稿
```

### 1.2 与 M1/M2 对比
| 维度 | M1 Blog | M2 微信 | M3 小红书 |
|------|---------|---------|-----------|
| 服务模式 | 静态网站 | 微信API | **自建MCP服务** |
| 服务器 | Cloudflare | 微信官方 | **Mac Mini (学校机房)** |
| 图片比例 | 960x480 | 900x383 | **3:4 (900x1200)** |
| 内容风格 | 技术长文 | 技术长文 | **短句+emoji+标签** |
| 模板数量 | 1 | 8种 | **6种** |
| 维护成本 | 低 | 中 | **需要自建服务** |

## 2. 技术架构

### 2.1 多Agent架构（借鉴Claude Code模式）

```
┌─────────────────────────────────────────────────────────────────┐
│                      主Agent: publish-xhs.sh                     │
│                      (协调者 - Shell脚本)                         │
│  - 接收用户输入 content.txt                                       │
│  - 并行调用子Agents                                                │
│  - 错误处理和日志记录                                               │
└─────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
┌────────────────────┐ ┌──────────────────┐ ┌────────────────────┐
│  Agent 1: 内容优化器 │ │ Agent 2: 配图生成 │ │ Agent 3: 模板渲染   │
│  (Python)          │ │ (Python)         │ │ (Node.js)          │
│  - 小红书风格优化   │ │ - 3:4封面生成     │ │ - 6种模板选择       │
│  - 标签自动提取     │ │ - 多图组合        │ │ - HTML/富文本生成   │
│  - 字数限制检查     │ │ - 水印添加        │ │                    │
└────────────────────┘ └──────────────────┘ └────────────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              Agent 4: 发布器 (Python HTTP Client)                  │
│  - 连接 Mac Mini 上的 MCP 服务 (http://mac-mini-ip:3000)          │
│  - 上传图片到小红书 CDN                                            │
│  - 调用 publish_content API                                       │
│  - 返回草稿链接                                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 部署架构

```
用户笔记本 (本地)
    │
    │ HTTP/Tailscale
    ▼
Mac Mini (学校机房)
    ├── Docker: xiaohongshu-mcp (端口 3000)
    │   ├── 小红书API封装
    │   ├── Cookie持久化 (/app/cookies)
    │   └── 登录状态管理
    │
    └── Docker: Redis (可选，缓存)
```

### 2.3 数据流

```
content.txt
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  Step 1: 内容优化 (pipeline/m3/optimizer.py)               │
│  输入: 原始Markdown                                          │
│  输出: {title, content, tags[], keywords[]}                  │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  Step 2: 配图生成 (pipeline/m3/cover_generator.py)         │
│  输入: title, keywords, theme                               │
│  输出: [image_path1, image_path2, ...] (1-9张)              │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  Step 3: 模板渲染 (pipeline/m3/renderer/xhs-renderer.js)   │
│  输入: content, images, theme                               │
│  输出: HTML富文本 (适合小红书的格式)                          │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  Step 4: 发布 (pipeline/m3/publisher.py)                   │
│  输入: title, html_content, images[], tags[]                │
│  动作:                                                       │
│    1. 上传图片到小红书CDN                                     │
│    2. 调用POST /api/publish                                  │
│  输出: {note_id, url, status}                               │
└────────────────────────────────────────────────────────────┘
```

## 3. 功能规划

### 3.1 第一期：基础发布（核心功能）

#### 已实现（克隆代码库）
- [x] 小红书API封装
- [x] 扫码登录
- [x] Cookie持久化
- [x] 图文发布API

#### 需开发
- [ ] 内容优化器（小红书风格）
- [ ] 3:4配图生成
- [ ] 6种随机模板
- [ ] 一键发布脚本
- [ ] Mac Mini部署配置

### 3.2 第二期：高级功能（可选）

基于MCP已有功能扩展：

| 功能 | MCP支持 | 开发优先级 |
|------|---------|-----------|
| 搜索帖子 | ✅ | P2 |
| 查看推荐流 | ✅ | P2 |
| 评论回复 | ✅ | P3 |
| 点赞/收藏 | ✅ | P3 |
| 关注用户 | ✅ | P3 |
| 数据分析 | ✅ | P3 |
| 定时发布 | ✅ | P2 |

## 4. 技术细节

### 4.1 小红书限制与适配

| 项目 | 限制 | 适配方案 |
|------|------|---------|
| 标题 | 20字 | 超过时自动截断+省略号 |
| 正文 | 1000字 | 超过时提醒用户精简 |
| 图片 | 1-9张 | 默认3张，根据内容自动选择 |
| 图片比例 | 3:4最佳 | 生成900x1200 |
| 标签 | 最多10个 | 自动提取3-5个 |
| 发布频率 | 有风控 | 加延迟+随机间隔 |

### 4.2 6种视觉模板

```javascript
const THEMES = {
  // 1. 清新绿 - 生活方式
  fresh: {
    name: '清新绿',
    primary: '#10b981',
    bgLight: '#ecfdf5',
    text: '#064e3b',
    emoji: '🌿',
    font: 'sans-serif'
  },
  
  // 2. 活力橙 - 美食探店
  orange: {
    name: '活力橙',
    primary: '#f97316',
    bgLight: '#fff7ed',
    text: '#7c2d12',
    emoji: '🍊',
    font: 'sans-serif'
  },
  
  // 3. 甜美粉 - 美妆穿搭
  pink: {
    name: '甜美粉',
    primary: '#ec4899',
    bgLight: '#fdf2f8',
    text: '#831843',
    emoji: '💕',
    font: 'sans-serif'
  },
  
  // 4. 专业蓝 - 职场学习
  blue: {
    name: '专业蓝',
    primary: '#3b82f6',
    bgLight: '#eff6ff',
    text: '#1e3a8a',
    emoji: '💼',
    font: 'sans-serif'
  },
  
  // 5. 神秘紫 - 创意艺术
  purple: {
    name: '神秘紫',
    primary: '#8b5cf6',
    bgLight: '#f5f3ff',
    text: '#4c1d95',
    emoji: '🔮',
    font: 'sans-serif'
  },
  
  // 6. 暖棕 - 读书文化
  brown: {
    name: '暖棕',
    primary: '#a16207',
    bgLight: '#fefce8',
    text: '#713f12',
    emoji: '🍂',
    font: 'serif'
  }
};
```

### 4.3 MCP API调用示例

```python
# 发布图文
import requests

XHS_MCP_URL = "http://mac-mini-ip:3000"  # 部署后替换

def publish_note(title, content, image_paths, tags):
    """调用MCP服务发布小红书"""
    
    # 1. 上传图片到小红书CDN
    uploaded_images = []
    for path in image_paths:
        with open(path, 'rb') as f:
            resp = requests.post(
                f"{XHS_MCP_URL}/api/upload",
                files={'file': f}
            )
            uploaded_images.append(resp.json()['url'])
    
    # 2. 发布
    payload = {
        "title": title,
        "content": content,
        "images": uploaded_images,
        "tags": tags,
        "visibility": "public",  # public/private/fans
        "is_original": True
    }
    
    resp = requests.post(
        f"{XHS_MCP_URL}/api/publish",
        json=payload
    )
    
    return resp.json()
```

## 5. 开发计划

### 5.1 Phase 1: 基础设施（1天）
- [ ] 创建 `pipeline/m3/` 目录结构
- [ ] 编写 Mac Mini 部署配置
- [ ] 编写 Docker Compose 文件

### 5.2 Phase 2: 内容优化（2天）
- [ ] `pipeline/m3/optimizer.py`
- [ ] 小红书风格转换
- [ ] 标签提取算法

### 5.3 Phase 3: 配图生成（2天）
- [ ] `pipeline/m3/cover_generator.py`
- [ ] 3:4图片生成
- [ ] 水印添加
- [ ] 多图组合

### 5.4 Phase 4: 渲染器（1天）
- [ ] `pipeline/m3/renderer/xiaohongshu-renderer.js`
- [ ] 6种模板实现
- [ ] 富文本生成

### 5.5 Phase 5: 发布器（1天）
- [ ] `pipeline/m3/publisher.py`
- [ ] MCP API封装
- [ ] 图片上传
- [ ] 错误处理

### 5.6 Phase 6: 集成（1天）
- [ ] `publish-xhs.sh` 一键脚本
- [ ] 与 M1/M2 打通
- [ ] 测试优化

**总计：8天**

## 6. 直接使用 vs 集成开发

### 6.1 直接使用MCP（不可行）
```bash
# 这样只能发原始内容，没有优化
$ curl http://mac-mini:3000/api/publish \
    -d '{"title":"标题","content":"正文","images":["a.jpg"]}'
# ❌ 没有风格优化
# ❌ 没有配图生成
# ❌ 没有模板美化
```

### 6.2 需要开发的集成层（必须）
```bash
# 一键发布，包含所有优化
$ ./publish-xhs.sh content.txt
# ✅ 自动优化为小红书风格
# ✅ 生成3:4配图+水印
# ✅ 随机选择6种模板
# ✅ 上传到小红书CDN
# ✅ 创建草稿
```

**开发必要性**：克隆的代码库只提供底层API，我们需要开发"智能层"来实现与M1/M2一致的用户体验。

## 7. 文件结构规划

```
pipeline/
├── m3/                               # 小红书发布模块
│   ├── __init__.py
│   ├── optimizer.py                  # 内容优化器
│   ├── cover_generator.py            # 配图生成
│   ├── publisher.py                  # 发布器
│   ├── renderer/
│   │   ├── xiaohongshu-renderer.js   # 渲染器
│   │   └── themes.js                 # 6种模板配置
│   ├── utils/
│   │   ├── text_processor.py         # 文本处理
│   │   └── image_processor.py        # 图片处理
│   └── config.py                     # 配置(Mac Mini地址等)
│
├── deploy/                           # 部署配置
│   └── xiaohongshu-mcp/
│       ├── docker-compose.yml        # Mac Mini部署
│       └── README.md                 # 部署指南
│
└── publish-xhs.sh                    # 一键发布脚本
```

## 8. 部署指南（Mac Mini）

### 8.1 前置要求
- Mac Mini 有 Docker 环境
- 可访问互联网
- 建议配置：4核8G+

### 8.2 部署步骤
```bash
# 1. 在Mac Mini上克隆仓库
git clone https://github.com/MushroomDAO/blog.git
cd blog/pipeline/deploy/xiaohongshu-mcp

# 2. 启动MCP服务
docker-compose up -d

# 3. 获取登录二维码
curl http://localhost:3000/api/login-qrcode

# 4. 用小红书App扫码登录

# 5. 测试发布
curl http://localhost:3000/api/check-login
```

### 8.3 网络配置
```bash
# 方案A: Tailscale (推荐)
tailscale up
# 获取 Tailscale IP: 100.x.x.x

# 方案B: 公网IP
# 如果有公网IP，直接端口映射

# 方案C: frp内网穿透
# 配置frpc连接到frps
```

## 9. 下一步行动

### 开发阶段（我来完成）
1. ✅ 创建设计文档（已完成）
2. ⏳ 开发 Phase 1-6（预计8天）
3. ⏳ 完成后通知用户

### 部署阶段（用户完成）
1. 在Mac Mini部署MCP服务
2. 配置网络访问（Tailscale推荐）
3. 扫码登录小红书

### 集成测试（一起完成）
1. 测试发布一篇帖子
2. 调整优化策略
3. 正式上线

---

**状态**: 设计文档完成，准备开始开发
