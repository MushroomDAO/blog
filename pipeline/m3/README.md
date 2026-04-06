# M3 小红书自动化发布系统

基于 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 的小红书自动化发布流水线。

## 架构

```
文章 Markdown ──→ optimizer.py ──→ 标题 + 短内容 + 标签
                         │
                         ↓
              cover_generator.py ──→ 900x1200 封面图
                         │
                         ↓
       xiaohongshu-renderer.js ──→ HTML 渲染
                         │
                         ↓
                 publisher.py ──→ MCP API ──→ 小红书
```

## 端口配置

MCP 服务使用端口 **3456**（已从默认 3000 修改，避免冲突）

```bash
# MCP URL 环境变量
export XHS_MCP_URL=http://localhost:3456
```

## 文件结构

```
pipeline/m3/
├── config.py                    # 配置管理
├── optimizer.py                 # 内容优化器
├── cover_generator.py           # 封面生成器
├── publisher.py                 # MCP API 客户端
├── test-suite.sh               # 完整测试套件
├── renderer/
│   ├── xiaohongshu-renderer.js  # 内容渲染器
│   └── themes.js               # 6套视觉主题
└── README.md                    # 本文档
```

## 快速开始

### 1. 启动 MCP 服务（Mac Mini）

```bash
cd pipeline/deploy/xiaohongshu-mcp
docker-compose up -d
```

### 2. 首次登录

```bash
# 获取二维码
curl http://localhost:3456/api/v1/login/qrcode

# 或保存二维码图片
python3 pipeline/m3/publisher.py --qrcode
```

用手机小红书 APP 扫描二维码登录。

### 3. 运行测试

```bash
# 运行所有测试
./pipeline/m3/test-suite.sh

# 运行单个测试
./pipeline/m3/test-suite.sh health    # MCP 健康检查
./pipeline/m3/test-suite.sh optimizer # 内容优化器
./pipeline/m3/test-suite.sh cover     # 封面生成器
./pipeline/m3/test-suite.sh renderer  # 渲染器
./pipeline/m3/test-suite.sh pipeline  # 完整流水线
```

### 4. 发布内容

```bash
# 一键发布
./publish-xhs.sh content.md

# 或指定主题
./publish-xhs.sh content.md --theme blue
```

## 模块说明

### optimizer.py - 内容优化器

将技术文章转换为小红书风格：

- 提取标题和标签
- 添加 Emoji 装饰
- 缩短句子，适配移动端阅读
- 限制 1000 字以内

```python
from optimizer import optimize_for_xiaohongshu

title, content, tags = optimize_for_xiaohongshu(markdown_content)
```

### cover_generator.py - 封面生成器

生成 3:4 比例封面图：

```python
from cover_generator import generate_cover

cover_path = generate_cover(
    title="文章标题",
    theme="blue",  # 可选: mint, orange, pink, blue, purple, brown
    output_path="/tmp/cover.jpg"
)
```

### publisher.py - 发布器

完整的 MCP API 客户端：

```python
from publisher import XiaohongshuPublisher

publisher = XiaohongshuPublisher()

# 检查登录
status = publisher.check_login()
print(f"Logged in: {status.is_logged_in}")

# 发布图文
result = publisher.publish(
    title="标题",
    content="正文内容",
    images=["/path/to/cover.jpg"],
    tags=["AI", "技术"],
    visibility="公开可见"
)

# 搜索内容
results = publisher.search_feeds(keyword="AI", sort_by="最新")

# 获取用户主页
profile = publisher.get_my_profile()
```

## API 端点

MCP 服务提供的 HTTP API（端口 3456）：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/login/status` | GET | 检查登录状态 |
| `/api/v1/login/qrcode` | GET | 获取登录二维码 |
| `/api/v1/publish` | POST | 发布图文 |
| `/api/v1/publish_video` | POST | 发布视频 |
| `/api/v1/feeds/list` | GET | 获取推荐列表 |
| `/api/v1/feeds/search` | GET/POST | 搜索内容 |
| `/api/v1/feeds/detail` | POST | 获取帖子详情 |
| `/api/v1/user/me` | GET | 获取当前用户信息 |

完整 API 文档参考：[xiaohongshu-mcp/docs/API.md](../../submodules/xiaohongshu-mcp/docs/API.md)

## 限制

根据小红书平台限制：

- 标题：最多 20 字
- 正文：最多 1000 字
- 图片：1-9 张
- 每日发布：最多 50 篇
- 定时发布：1 小时至 14 天内

## 故障排除

### MCP 服务无响应

```bash
# 检查服务状态
curl http://localhost:3456/health

# 查看 Docker 日志
docker-compose logs xiaohongshu-mcp

# 检查端口占用
lsof -i :3456
```

### 登录失败

1. 确认二维码未过期（默认 300 秒）
2. 确认使用小红书 APP 而非微信扫码
3. 检查账号是否被封禁
4. 尝试删除 cookies 重新登录：
   ```bash
   curl -X DELETE http://localhost:3456/api/v1/login/cookies
   ```

### 发布失败

1. 检查图片路径是否正确（不支持中文路径）
2. 确认图片大小（建议 < 5MB）
3. 检查内容是否包含敏感词
4. 查看 MCP 服务日志

## 参考

- [xiaohongshu-mcp GitHub](https://github.com/xpzouying/xiaohongshu-mcp)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [小红书创作服务中心](https://creator.xiaohongshu.com/)
