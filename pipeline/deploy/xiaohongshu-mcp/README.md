# 小红书 MCP 服务部署指南

## 部署环境
- Mac Mini (学校机房)
- Docker & Docker Compose
- 内网穿透 (Tailscale/frp/公网IP)

## 快速开始

### 1. 安装 Docker
```bash
# Mac Mini 上执行
brew install --cask docker
# 或手动下载 Docker Desktop for Mac
```

### 2. 启动服务
```bash
cd pipeline/deploy/xiaohongshu-mcp
docker-compose up -d
```

### 3. 获取登录二维码
```bash
# 方法1: 直接访问
curl http://localhost:3456/api/login-qrcode

# 方法2: 查看日志
docker logs xhs-mcp
```

### 4. 扫码登录
- 用小红书 App 扫描二维码
- 登录状态会自动保存到 `./cookies`

### 5. 验证登录
```bash
curl http://localhost:3456/api/check-login
```

## 网络配置

### 方案A: Tailscale (推荐)
```bash
# Mac Mini 上安装 Tailscale
brew install tailscale
sudo tailscale up

# 查看 Tailscale IP
tailscale ip -4
# 输出类似: 100.x.x.x

# 其他设备通过 Tailscale IP 访问
# http://100.x.x.x:3456
```

### 方案B: 公网IP
如果有公网IP，配置路由器端口映射：
- 外部 3456 → Mac Mini 3456

### 方案C: frp内网穿透
参考 frp 官方文档配置 frpc + frps

## 常用命令

```bash
# 查看日志
docker logs -f xhs-mcp

# 重启服务
docker-compose restart

# 更新镜像
docker-compose pull && docker-compose up -d

# 停止服务
docker-compose down

# 查看状态
docker ps
```

## API 文档

服务启动后访问: http://localhost:3456/docs

### 主要接口
- `POST /api/login-qrcode` - 获取登录二维码
- `GET /api/check-login` - 检查登录状态
- `POST /api/publish` - 发布图文
- `POST /api/upload` - 上传图片

## 故障排查

### 容器无法启动
```bash
# 检查日志
docker logs xhs-mcp

# 检查端口占用
lsof -i :3456
```

### 登录失败
```bash
# 删除Cookie重新登录
rm -rf cookies/*
docker-compose restart
```

### 网络不通
```bash
# 测试本地访问
curl http://localhost:3456/health

# 测试外部访问 (替换为实际IP)
curl http://100.x.x.x:3456/health
```
