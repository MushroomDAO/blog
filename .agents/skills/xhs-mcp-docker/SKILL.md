# Skill: xhs-mcp-docker

> 小红书 MCP 服务 — Docker 模式（容器化 Chromium + 扫码登录）
>
> 维护记录：
> - 创建：2026-04-16
> - 适用场景：无需已登录 Chrome；通过 QR 码认证；适合部署到新机器

---

## 触发词

| 触发词 | 功能 |
|--------|------|
| `xhs docker 模式` | 启动 Docker 发布流程 |
| `xhs 容器模式` | 同上 |
| `调试 xhs docker` | 进入排查流程 |

---

## 架构概览

```
Claude / MCP Client
    ↓ HTTP POST /api/v1/publish
Go MCP Server（容器内 :18060）
    ↓ CDP WebSocket（容器内 chromium --remote-debugging-port=9222）
Chromium（无头，ARM64 Debian bookworm）
    ↓
小红书发布页
```

**与 CDP 模式区别**：
- Chromium 在容器内自动启动，不依赖宿主机 Chrome
- 登录通过 QR 码完成，cookie 持久化到宿主机 `cookies/cookies.json`
- 适合新机器部署或 CI/CD 场景

---

## 一、环境准备

### 目录结构

```
pipeline/deploy/xiaohongshu-mcp/
├── docker-compose.yml
├── Dockerfile.arm64          # ARM64 镜像（Mac Mini / Apple Silicon）
├── start.sh                  # 一键启动脚本
├── cookies/
│   └── cookies.json          # 持久化登录 cookie（宿主机挂载）
├── data/                     # 图片等媒体文件挂载目录
└── logs/                     # 日志输出
```

### 构建镜像

```bash
cd pipeline/deploy/xiaohongshu-mcp

# ARM64（Mac Mini / Apple Silicon）
docker build -f Dockerfile.arm64 -t xhs-mcp:local .

# AMD64（x86 服务器）
docker build -f Dockerfile -t xhs-mcp:local .
```

> **重要**：ARM64 镜像必须用 `debian:bookworm-slim` + `apt-get install chromium`。
> Ubuntu 22.04 上的 chromium 是 snap 包，容器内无法运行（snap 需要 systemd）。

### 一键启动

```bash
cd pipeline/deploy/xiaohongshu-mcp
./start.sh
# 等价于 docker-compose up -d
```

`docker-compose.yml` 关键配置：
```yaml
services:
  xhs-mcp:
    image: xhs-mcp:local          # 或 dockerhub 镜像
    ports:
      - "127.0.0.1:3456:18060"    # 宿主机 3456 → 容器 18060
    volumes:
      - ./cookies:/app/cookies    # cookie 持久化
      - ./data:/app/data          # 媒体文件
      - ./logs:/app/logs
    environment:
      - CHROME_FLAGS=--no-sandbox --disable-dev-shm-usage
```

---

## 二、登录流程

### 第一次登录（扫码）

```bash
# 1. 获取 QR 码
curl http://localhost:3456/api/v1/login/qrcode
# 返回 base64 图片或 URL，用终端二维码工具显示

# 2. 手机扫码登录小红书

# 3. 轮询确认登录成功
curl http://localhost:3456/api/v1/login/status
# → {"logged_in": true}
```

登录成功后 cookie 自动写入 `cookies/cookies.json`，下次启动自动加载，无需重新扫码。

### 验证登录持久化

```bash
# 重启容器后检查
docker-compose restart
curl http://localhost:3456/api/v1/login/status
```

---

## 三、测试

### 健康检查

```bash
curl http://localhost:3456/health
# → {"status":"ok"}
```

### 发布图文

```bash
# 图片需放到宿主机 data/ 目录（容器挂载为 /app/data/）
cp /path/to/image.jpg pipeline/deploy/xiaohongshu-mcp/data/

curl -X POST http://localhost:3456/api/v1/publish \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试标题",
    "content": "测试内容 #测试",
    "tags": ["测试"],
    "images": ["/app/data/image.jpg"]
  }'
```

### 查看日志

```bash
docker-compose logs -f
# 或查看挂载日志文件
tail -f pipeline/deploy/xiaohongshu-mcp/logs/app.log
```

---

## 四、与 Tailscale 集成（远程访问）

Mac Mini 上运行后，通过 Tailscale 暴露到内网：

```bash
# Mac Mini 上启动 proxy
python3 pipeline/deploy/xiaohongshu-mcp/proxy.py

# 查看 Tailscale IP
tailscale ip -4
# → 100.x.x.x

# 客户端（笔记本 / Claude）访问
curl http://100.x.x.x:3456/health
```

客户端配置：
```bash
# .env
XHS_MCP_URL=http://100.x.x.x:3456
```

---

## 五、故障排查

### 问题：镜像构建失败（chromium not found）

**原因**：用了 Ubuntu 22.04，chromium 是 snap 包，容器内无法安装运行。

**修复**：改用 `debian:bookworm-slim`：
```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y chromium ...
```

---

### 问题：容器启动后 Chrome 无法启动

**原因**：缺少 `--no-sandbox`（容器内无法用 Chrome sandbox）。

**修复**：环境变量或启动参数加 `--no-sandbox --disable-dev-shm-usage`：
```yaml
environment:
  - CHROME_FLAGS=--no-sandbox --disable-dev-shm-usage
```

---

### 问题：登录后重启容器又要扫码

**原因**：`cookies/` 目录未挂载或路径错误。

**修复**：确认 `docker-compose.yml` 中 volume 挂载正确，且宿主机 `cookies/` 目录可写：
```bash
ls -la pipeline/deploy/xiaohongshu-mcp/cookies/
# 应存在 cookies.json 且有内容
```

---

### 问题：发布时图片找不到

**原因**：请求中的图片路径是宿主机路径，但容器内路径不同。

**修复**：图片必须放在 `data/` 挂载目录，路径写成容器内路径 `/app/data/xxx.jpg`。

---

### 问题：3456 端口无法从外网访问

**原因**：docker-compose 绑定了 `127.0.0.1:3456`，只允许本机访问。

**修复方案 A**：改为 `0.0.0.0:3456:18060`（注意安全风险）。
**修复方案 B**（推荐）：使用 `proxy.py` 通过 Tailscale 暴露，不直接开放端口。

---

### 问题：发布时 WAF 拦截（跳转 /login）

**原因**：容器内 Chromium 是全新 session，没有历史 fingerprint。

**解决**：确保 cookie 正确加载；如持续被拦截，重新扫码登录刷新 session。

> **注意**：Docker 模式的 WAF 绕过能力弱于 CDP 模式（真实 Chrome Profile）。如果频繁被拦截，建议改用 CDP 模式（见 `xhs-mcp-cdp` skill）。

---

## 六、Docker vs CDP 模式选择

| 场景 | 推荐模式 |
|------|----------|
| Mac Mini 长期运行，已有登录 Chrome | **CDP 模式**（更稳定，WAF 绕过更好） |
| 新机器初次部署 | **Docker 模式**（扫码登录方便） |
| CI/CD 自动化 | **Docker 模式**（无需桌面） |
| WAF 频繁拦截 | **CDP 模式**（真实 Profile，指纹最佳） |
| 服务器（Linux x86） | **Docker 模式**（无 Chrome 桌面） |

---

## 七、相关文件

| 文件 | 说明 |
|------|------|
| `Dockerfile.arm64` | ARM64 镜像定义（Debian + Chromium） |
| `docker-compose.yml` | 服务编排、端口、挂载 |
| `start.sh` | 一键启动脚本 |
| `proxy.py` | Tailscale 内网代理 |
| `status.sh` | 检查服务状态脚本 |
| `cookies/cookies.json` | 持久化 cookie（不入版本控制） |
