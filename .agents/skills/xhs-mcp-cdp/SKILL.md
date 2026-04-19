# Skill: xhs-mcp-cdp

> 小红书 MCP 服务 — CDP 模式（Mac Mini 24h 服务 或 MacBook 本地临时模式）
>
> 维护记录：
> - 创建：2026-04-16
> - 基于完整 CDP 调试会话提炼
> - 2026-04-17：加入 launchd 自启动配置（Mac Mini 重启自动恢复）
> - 2026-04-17：加入 MacBook 本地模式（不依赖 Mac Mini）

---

## 触发词

| 触发词 | 功能 |
|--------|------|
| `xhs cdp 模式` | 启动 CDP 发布流程 |
| `xhs 本地模式` | 同上 |
| `调试 xhs cdp` | 进入排查流程 |

---

## 架构概览

```
Claude / MCP Client
    ↓ HTTP POST /api/v1/publish
Go MCP Server (本地二进制 /tmp/xhs-mcp-mac)
    ↓ CDP WebSocket ws://localhost:9222
真实 Chrome（jhfnetboy Profile 4，已登录小红书）
    ↓ 复用已有 creator 标签页
小红书发布页 creator.xiaohongshu.com
```

**核心设计原则**：
- 不起新 Tab，复用已有 `creator.xiaohongshu.com` Tab → 绕过 WAF 指纹检测
- 不用 go-rod Input API，改为直连 page-level WebSocket 发 `Input.dispatchMouseEvent` → 产生 `isTrusted=true` 事件，Vue SPA 才能响应
- 所有 `page.Element()` 调用必须用 goroutine+channel+time.After 包裹 → 防止 WebSocket 阻塞

---

## 一、环境准备

### 1. 编译 Mac Mini 二进制

```bash
cd pipeline/deploy/xiaohongshu-mcp/src
GOOS=darwin GOARCH=arm64 go build -o /tmp/xhs-mcp-mac .
```

### 2. 启动带调试端口的 Chrome

```bash
open -na "Google Chrome" \
  --args \
  --user-data-dir="/Users/jhfnetboy/Library/Application Support/Google/Chrome/Profile 4" \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  https://creator.xiaohongshu.com/publish/publish?source=official
```

验证 Chrome CDP 可达：
```bash
curl http://localhost:9222/json/version
# 应返回 { "Browser": "Chrome/...", ... }
```

### 3. 启动 MCP Server

```bash
CHROME_CONNECT_URL=http://localhost:9222 /tmp/xhs-mcp-mac
# 或显式指定：
/tmp/xhs-mcp-mac -connect=http://localhost:9222
```

成功启动日志：
```
已连接到现有 Chrome: http://localhost:9222
MCP Server initialized with official SDK
启动 HTTP 服务器: :18060
```

---

## 二、测试

### 健康检查

```bash
curl http://localhost:18060/health
# → {"status":"ok","chrome_connected":true}
```

### 发布图文

```bash
curl -X POST http://localhost:18060/api/v1/publish \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试标题",
    "content": "测试内容 #测试",
    "tags": ["测试"],
    "images": ["/tmp/test.jpg"]
  }'
# 正常返回 HTTP 200，17s 左右完成
```

### 登录状态检查

```bash
curl http://localhost:18060/api/v1/login/status
```

---

## 三、关键代码位置

| 模块 | 文件 | 说明 |
|------|------|------|
| CDP 连接 | `src/configs/browser.go` | `GetConnectURL()` / `SetConnectURL()` |
| Tab 复用 | `src/service.go` → `cdpBrowserSession.GetPage()` | 遍历 Pages，复用 creator Tab |
| Tab 激活 | `src/service.go` | `p.Activate()` 确保视口坐标有效 |
| Tab 点击 | `src/xiaohongshu/publish.go` → `clickTabViaDevTools()` | 直连 page-level WS，发 Input 事件 |
| 超时保护 | `src/xiaohongshu/publish.go` → `waitElem()` | goroutine+channel+time.After |
| 跳过 Navigate | `src/xiaohongshu/publish.go` → `NewPublishImageAction()` | 已在发布页则跳过导航 |

---

## 四、故障排查

### 问题：每次发布都被跳到 /login（WAF 拦截）

**原因**：代码新建了 CDP Tab 并 Navigate，新 Tab 没有 WAF Cookie，被检测为机器人。

**修复**：`cdpBrowserSession.GetPage()` 复用已有 `creator.xiaohongshu.com` Tab。
```go
for _, p := range pages {
    info, _ := p.Info()
    if strings.Contains(info.URL, "creator.xiaohongshu.com") {
        p.Activate()
        return p, true  // isPersistPage=true，不 defer close
    }
}
```

---

### 问题：点击"上传图文"Tab 无响应

**原因**：Vue SPA 监听的是 `isTrusted=true` 的原生事件；go-rod `element.Click()` 发出的是 `isTrusted=false` 的 JS 事件，被忽略。

**修复**：`clickTabViaDevTools()` 绕过 go-rod，直连 page-level WebSocket：
```go
// 1. GET http://localhost:9222/json → 找到 creator tab 的 wsDebuggerUrl
// 2. 建立 WebSocket 连接
// 3. 发送 Input.dispatchMouseEvent { type: "mousePressed", ... }
// 4. 发送 Input.dispatchMouseEvent { type: "mouseReleased", ... }
```

坐标通过 `page.Element(".publish-tab").Eval("this.getBoundingClientRect()")` 获取。

---

### 问题：`page.Timeout(30s).Element(sel)` 永久阻塞

**原因**：go-rod Timeout 只设 context deadline，但底层 WebSocket `ReadMessage()` 不响应 context cancel，goroutine 泄漏且调用方永远不返回。

**修复**：所有 Element 查询用 goroutine+channel 封装：
```go
waitElem := func(sel string, timeout time.Duration) (*rod.Element, error) {
    type result struct { e *rod.Element; err error }
    ch := make(chan result, 1)
    go func() { e, err := page.Element(sel); ch <- result{e, err} }()
    select {
    case r := <-ch: return r.e, r.err
    case <-time.After(timeout): return nil, errors.Errorf("等待 %s 超时", sel)
    }
}
```

---

### 问题：`div.upload-content` 等待超时

**原因**：这个 div 只有在点击"上传图文"Tab 之后才存在，代码却在点击之前等待。

**修复**：先调用 `mustClickPublishTab()`，再等 `div.upload-content`。

---

### 问题：`element outside viewport`

**原因**：CDP 切换到已有 Tab 后，Tab 可能在后台，元素视口坐标无效。

**修复**：`p.Activate()` 将 Tab 前置后再操作。

---

### 问题：go-rod Input domain 超时（`target.Click()` 超时）

**原因**：go-rod 的 browser-level CDP session 是多路复用的，`Input.dispatchMouseEvent` 响应被丢失或超时。

**修复**：Input 事件完全不走 go-rod，直接 `clickTabViaDevTools()` 开 page-level WebSocket。

---

### 问题：`box.Quads[0].Bound()` 编译报错

**原因**：`proto.DOMQuad` 没有 `Bound()` 方法，只有 `Center()`。

**修复**：改用 `box.Quads[0].Center()`。

---

## 五、完整发布流程时序

```
GET /api/v1/publish
    ↓
cdpBrowserSession.GetPage()
    → 遍历 Chrome tabs
    → 找到 creator.xiaohongshu.com tab
    → Activate()
    ↓
NewPublishImageAction(page)
    → 检查当前 URL，已在发布页 → 跳过 Navigate
    → waitElem("div.upload-tab 或类似", 10s)
    → clickTabViaDevTools("上传图文", x, y)  ← page-level WS, isTrusted=true
    → waitElem("div.upload-content", 10s)
    ↓
PublishImage(ctx, content)
    → uploadImages(page, imagePaths)
        → fileInput.SetFiles(...)
        → 等待图片缩略图出现
    → submitPublish(page, title, content, tags, ...)
        → 填写标题
        → 填写正文
        → 点击发布按钮
    ↓
HTTP 200，~17s
```

---

## 六、Mac Mini 重启自动恢复

### 自动启动流程

```
macOS 登录
    → launchd 加载 com.xhs-mcp-cdp.plist
    → 运行 ~/Library/Scripts/xhs-cdp-start.sh
    → 检测 Chrome CDP（9222）→ 已有 Chrome 跳过启动，没有则用 jhfnetboy Profile 4 打开
    → 启动 ~/Library/Scripts/xhs-mcp-mac
    → 服务在 :18060 就绪
```

### 前提：开启自动登录（必须手动确认一次）

LaunchAgent 仅在用户登录后触发。Mac Mini 必须配置自动登录，否则重启后停在登录界面：

> **系统设置 → 用户与群组 → 自动登录 → 选择 nicolasshuaishuai**

### MacBook 访问

```bash
# Tailscale 直连（18060 绑定 0.0.0.0，直接可达）
curl http://<Mac Mini Tailscale IP>:18060/health

# 日志查看（SSH 进 Mac Mini）
tail -f ~/Library/Logs/xhs-mcp-cdp.log
```

### 关键文件

| 文件 | 作用 |
|------|------|
| `~/Library/LaunchAgents/com.xhs-mcp-cdp.plist` | launchd 服务定义 |
| `~/Library/Scripts/xhs-cdp-start.sh` | 启动脚本（Chrome + MCP） |
| `~/Library/Scripts/xhs-mcp-mac` | MCP 二进制（需手动更新，不入 git） |
| `~/Library/Logs/xhs-mcp-cdp.log` | 运行日志 |

### 手动操作

```bash
# 查看服务状态
launchctl list com.xhs-mcp-cdp

# 重启服务
launchctl unload ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist
launchctl load   ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist

# 更新二进制（重新编译后）
cp /Volumes/UltraDisk/Dev2/tools/blog/pipeline/deploy/xiaohongshu-mcp/xhs-mcp-mac \
   ~/Library/Scripts/xhs-mcp-mac
launchctl unload ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist
launchctl load   ~/Library/LaunchAgents/com.xhs-mcp-cdp.plist
```

---

## 七、MacBook 本地模式（不依赖 Mac Mini）

出差、Mac Mini 关机、或只想在 MacBook 上调试时，直接在 MacBook 本地跑同一套流程。

### 方案 A — CDP 原生模式（推荐，5 分钟内可用）

原理与 Mac Mini 完全相同，只是在 MacBook 本机启动 Chrome + binary。

**第一步：编译 binary（只需一次）**

```bash
cd /path/to/blog/pipeline/deploy/xiaohongshu-mcp/src
GOOS=darwin GOARCH=arm64 go build -o ~/Library/Scripts/xhs-mcp-mac .
```

**第二步：启动 Chrome（用你的小红书 profile）**

```bash
# 找到你登录了小红书的 Chrome Profile 编号
for p in ~/Library/Application\ Support/Google/Chrome/Profile\ *; do
  email=$(python3 -c "import json; d=json.load(open('$p/Preferences')); print(d.get('account_info',[{}])[0].get('email','?'))" 2>/dev/null)
  echo "$p → $email"
done

# 替换下面的 Profile 4 为你的实际编号
open -na "Google Chrome" --args \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome/Profile 4" \
  --remote-debugging-port=9222 \
  --no-first-run \
  https://creator.xiaohongshu.com/publish/publish?source=official
```

**第三步：启动 MCP Server**

```bash
CHROME_CONNECT_URL=http://localhost:9222 ~/Library/Scripts/xhs-mcp-mac
# 看到 "启动 HTTP 服务器: :18060" 即就绪
```

**第四步：发布（MacBook 本地直接用 localhost）**

```bash
XHS=http://localhost:18060

# 上传图片
P1=$(curl -sX POST $XHS/api/v1/upload -F "file=@img1.jpg" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['path'])")

# 发布
curl -X POST $XHS/api/v1/publish \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"标题\",\"content\":\"正文\",\"images\":[\"$P1\"],\"tags\":[\"标签\"]}"
```

**日志：**

```bash
# MCP server 日志直接输出在终端
# Chrome CDP 调试
curl http://localhost:9222/json/version
```

---

### 方案 B — Docker 本地模式（需要 Docker Desktop）

适合需要干净隔离环境或不想污染本机 Chrome profile 的场景。

```bash
cd /path/to/blog/pipeline/deploy/xiaohongshu-mcp

# 1. 构建镜像（ARM64 MacBook）
docker build -f src/Dockerfile.arm64 -t xhs-mcp:local src/

# 2. 启动容器（映射到本机 3456）
docker run -d \
  --name xhs-mcp-local \
  -p 127.0.0.1:3456:18060 \
  -v $(pwd)/cookies:/app/cookies \
  -v $(pwd)/data:/app/data \
  xhs-mcp:local

# 3. 扫码登录
curl http://localhost:3456/api/v1/login/qrcode

# 4. 使用（端口 3456）
XHS=http://localhost:3456
```

---

### 两种方案对比

| | 方案 A（CDP 原生） | 方案 B（Docker） |
|--|--|--|
| 启动速度 | ~5s | ~30s |
| 依赖 | Chrome 已登录小红书 | Docker Desktop |
| WAF 绕过 | 最好（真实 Profile） | 一般 |
| 首次登录 | 已在 Chrome 里 | 需要扫码 |
| 适合场景 | 日常使用、快速调试 | 隔离测试、CI |

---

### 一键启动脚本（方案 A）

保存为 `~/bin/xhs-local` 后 `chmod +x`，以后直接 `xhs-local` 启动：

```bash
#!/bin/bash
# XHS MCP 本地快速启动（MacBook 用）

PROFILE="${XHS_CHROME_PROFILE:-$HOME/Library/Application Support/Google/Chrome/Profile 4}"
BINARY="$HOME/Library/Scripts/xhs-mcp-mac"

# 检查 binary
if [ ! -f "$BINARY" ]; then
  echo "Binary not found. Build first:"
  echo "  cd pipeline/deploy/xiaohongshu-mcp/src"
  echo "  go build -o ~/Library/Scripts/xhs-mcp-mac ."
  exit 1
fi

# 检查 Chrome CDP
if ! curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
  echo "Starting Chrome..."
  open -na "Google Chrome" --args \
    --user-data-dir="$PROFILE" \
    --remote-debugging-port=9222 \
    --no-first-run \
    https://creator.xiaohongshu.com/publish/publish?source=official
  sleep 5
fi

echo "Starting XHS MCP on :18060..."
exec env CHROME_CONNECT_URL=http://localhost:9222 "$BINARY"
```

---

## 八、已知限制

- Chrome 必须保持运行且停留在 `creator.xiaohongshu.com`（关闭 Tab 后下次发布会新开 Tab，可能触发 WAF）
- 本模式不适合无头/CI 环境，需要真实 macOS 桌面
- 9222 端口只绑定 localhost，不暴露到外网
- 小红书 session cookie 在浏览器的 Profile 里，换 Profile 需重新登录
