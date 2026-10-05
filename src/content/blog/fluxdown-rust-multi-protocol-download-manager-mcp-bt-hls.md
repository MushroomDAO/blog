---
title: "FluxDown：Rust 驱动的免费开源 IDM 替代，内置 MCP Server"
titleEn: "FluxDown: Rust-Powered Free Open-Source IDM Alternative with Built-in MCP Server"
description: "zerx-lab/FluxDown，AGPL-3.0，3914 stars，Rust，2026-07-03。定位免费开源 IDM 替代品，Rust+Tokio 下载引擎（独立于任何 UI 和 FFI），支持 HTTP/HTTPS、FTP、BitTorrent（DHT/UPnP/磁力）、eD2K（Kad DHT、MD4 校验）、HLS（AES 解密）、DASH，动态分段加速（空闲线程接管慢分段）。Chrome/Edge/Firefox 浏览器扩展三层拦截；内置 12 工具 MCP Server（Streamable HTTP），让 Claude、Cursor 等 AI 直接管理下载；跨平台覆盖 Windows/macOS/Linux/Android/NAS/Docker。桌面用 GPUI，移动端用 Flutter，Web 管理界面用 React，CLI 和 aria2 兼容 JSON-RPC 全覆盖。"
descriptionEn: "zerx-lab/FluxDown, AGPL-3.0, 3914 stars, Rust, 2026-07-03. Free open-source IDM alternative: Rust+Tokio download engine (independent of any UI/FFI), supporting HTTP/HTTPS, FTP, BitTorrent (DHT/UPnP/magnet), eD2K (Kad DHT, MD4 verification), HLS (AES-decrypted), DASH; dynamic segmentation with slow-segment rescue. Chrome/Edge/Firefox browser extension with 3-layer interception; 12-tool built-in MCP Server (Streamable HTTP) for Claude/Cursor AI control; cross-platform Windows/macOS/Linux/Android/NAS/Docker. GPUI desktop, Flutter Android, React Web UI, CLI, aria2-compatible JSON-RPC."
pubDate: 2026-10-05
heroImage: "../../assets/images/fluxdown-rust-multi-protocol-download-manager-mcp-bt-hls-banner.jpg"
category: "Tech-Experiment"
tags: ["下载工具", "Rust", "开源工具", "MCP", "BitTorrent", "跨平台"]
lang: "zh-CN"
wechatTitle: "FluxDown：免费开源IDM替代，含MCP Server"
wechatDigest: "AGPL 3914星；Rust+Tokio；BT/eD2K/HLS/DASH；内置MCP；全平台+NAS"
---

IDM（Internet Download Manager）是一个技术上已经很老但依然活跃的工具：单线程 HTTP 太慢、迅雷广告太多、浏览器自带下载没有多线程加速，IDM 这些年凭借稳定的多线程分段和浏览器集成一直有市场。它的问题是只支持 Windows、需要付费（$24.95 本体加每年续费），且不支持 BT/磁力。

FluxDown 的定位非常明确：把 IDM 的核心功能复刻到开源跨平台版本上，同时把协议覆盖范围和平台覆盖范围都扩出去。

从 2026-07-03 开仓到今天（2026-10-05），3 个月内累积了 3914 星，说明这个定位本身是有需求的。

GitHub: https://github.com/zerx-lab/FluxDown | ⭐ 3914 | AGPL-3.0 | Rust

---

## 架构：一个引擎，多个宿主

FluxDown 的架构核心是把下载引擎（`fluxdown_engine`）完全独立出来：纯 Rust + Tokio，没有 UI 依赖，没有 FFI，不依赖任何特定宿主。

```
GPUI 桌面  ──→  fluxdown-agent  ──→  fluxdownd  ──→  fluxdown_engine
React Web  ──→  同一个 agent                          │
Flutter 移动端  ──→  hub 宿主  ──────────────────────→ │
CLI         ──→  直接嵌入（standalone 模式）  ──────→  │
                                                      ├──→  HTTP/HTTPS/FTP/BT/eD2K/HLS/DASH
                                                      └──→  SQLite / PostgreSQL
```

三个分工：
- **daemon（fluxdownd）**：持有引擎、下载数据库、队列、RSS、插件和 webhook，是下载核心
- **agent（fluxdown-agent）**：管 UI 网关、FluxCloud 账号/同步、设备协作、浏览器捕获和桌面系统托盘
- **共享合约（native/protocol + native/api）**：REST、aria2 和 MCP 都基于同一个 `ApiHost` trait

桌面用 GPUI（zed 编辑器同款 GPU UI 框架），移动端用 Flutter，服务器端 Web 管理界面用 React+TypeScript+Vite。这三个 UI 共用同一套下载引擎，引擎本身不关心谁在驱动它。

---

## 下载引擎：动态分段 + 慢段救援

FluxDown 的分段逻辑在运行时动态切割，而不是一开始就固定分 N 段：

- 文件在下载过程中，如果某个分段的速度异常慢（服务器限速或路由问题），空闲的工作线程会自动接管这个慢分段，把它再拆分继续下载
- 最终把所有分段合并，整体速度取决于服务器能给多少带宽，而不是"最慢那一段"

持久化用 SQLite（WAL 模式），服务器部署可以改 PostgreSQL。中断后可以从持久化状态恢复——这是与浏览器下载最根本的区别。

---

## 协议覆盖

| 协议 | 备注 |
|------|------|
| HTTP/HTTPS | 多线程分段，Range 请求 |
| FTP | 完整支持 |
| BitTorrent | DHT/UPnP/磁力链接 |
| eD2K | eMule 链接格式，含 Kad DHT 来源发现 + MD4 完整性校验 |
| HLS | M3U8 流媒体，AES 解密 |
| DASH | 自适应流媒体 |

eD2K 支持比较少见，这是 eMule 网络用的协议，在国内还有一批用户用它下载老资源。HLS AES 解密意味着可以处理加密的视频流，但要注意版权和服务条款。

---

## 浏览器扩展：三层拦截

扩展基于 WXT 构建，同时支持 Chrome/Edge（Chrome Web Store）和 Firefox（AMO）。

三层拦截机制：
1. 标准下载拦截（覆盖浏览器内置下载）
2. 流媒体嗅探（检测 HLS/DASH 链接）
3. Alt+Click 旁路 + 右键发送

扩展通过 Native Messaging 连接到本地桌面 agent，不走任何云端中转。也有 Tampermonkey userscript 版本。

---

## MCP Server：让 AI 直接管理下载

这是 FluxDown 和其他下载工具拉开差距的地方之一。

内置 MCP Server 实现了 Streamable HTTP（JSON-RPC 2.0，`POST /mcp`），复用管理 API 的同一端口（17800），12 个工具：

| 工具 | 作用 |
|------|------|
| `download_add` | 新建下载任务（HTTP/FTP/磁力/BT） |
| `download_list` | 列出任务及进度/速度/状态 |
| `download_get` | 按 ID 获取单个任务 |
| `download_pause` / `download_resume` | 暂停/恢复单任务 |
| `download_pause_all` / `download_resume_all` | 全局暂停/恢复 |
| `download_remove` | 删除任务（可选删文件） |
| `queue_list` | 列出命名队列 |
| `rss_list` | 列出 RSS 订阅 |
| `rss_add` | 订阅 RSS 并设定轮询间隔 |
| `rss_remove` | 删除 RSS 订阅 |

在 Claude Desktop 或 Cursor 配置文件里加入：

```json
{
  "mcpServers": {
    "fluxdown": {
      "url": "http://127.0.0.1:17800/mcp",
      "headers": { "Authorization": "Bearer <your-token>" }
    }
  }
}
```

之后你可以直接对 AI 说"帮我下载这个链接"或"暂停所有下载"。

桌面版默认关闭 MCP 和管理 API，需要在 Settings → API Service 里手动开启并生成 token；服务器版默认开启，启动时必须设 access key。

---

## 服务器 / NAS 部署

Docker 最简单：

```bash
docker compose -f docker/docker-compose.yml up -d
```

默认监听 `0.0.0.0:17800`，首次访问 `http://<server>:17800/` 完成设置向导（设置 access key，8–128 个可见 ASCII 字符，包含至少一个字母和一个数字）。

几个注意点：
- 如果要公网访问，**必须套 HTTPS 反向代理**，不要裸 HTTP 暴露
- `/data` 挂载持久化（数据库/日志/access key），`/root/Downloads` 挂载下载目录
- `/data` 建议 SSD/缓存盘，特别是下载盘需要自动睡眠的场景
- 通过 `FLUXDOWN_TOKEN` 环境变量或 secret manager 设置初始 key，不要提交到代码仓库
- `fluxdown-agent` 和 `fluxdownd` 必须在同一目录

原生 NAS 包：Synology DSM 6/7 `.spk`、QNAP `.qpkg`、OpenWrt `.ipk`、Unraid CA 模板、CasaOS/ZimaOS 应用商店。

---

## 接口层

| 接口 | 端点 | 用途 |
|------|------|------|
| REST 管理 API | `/api/v1/*` | 任务/队列/RSS 管理 |
| OpenAPI | `/api/v1/openapi.json` | 机器可读 API schema |
| aria2 兼容 JSON-RPC | `/jsonrpc`（HTTP/WebSocket） | 和 aria2 生态集成 |
| MCP | `/mcp` | AI agent 工具层 |
| 官方 UI WebSocket | `/rpc` | GPUI/Web UI 网关 |

aria2 兼容层意味着能接入现有的 aria2 管理界面和脚本生态。

CLI 用法：

```bash
fluxdown ping
fluxdown add "https://example.com/file.zip"
fluxdown --json list

# standalone 模式，嵌入引擎直接下载，不走服务
fluxdown add --local "https://example.com/file.zip"
```

注意：standalone 模式不能和正在运行的服务共享同一个 data 目录，使用前需停止服务。

---

## 许可证与隐私

**AGPL-3.0**：如果你把 FluxDown 作为网络服务运行并修改了源码，必须开放这些修改。个人本地使用不受影响。

**遥测**：不是零遥测应用，默认有匿名安装统计和日活统计（可以通过 `analytics_enabled` 关闭）。不收集下载内容和任务信息。本地下载不需要 FluxCloud 账号，云功能完全可选。

---

> AGPL-3.0 开源。zerx-lab 维护，2026-07-03 开仓，截至 2026-10-05 共 3914 星。开源仅供学习参考。

---

<!--EN-->

## FluxDown: Rust-Powered Free Open-Source IDM Alternative with Built-in MCP Server

IDM (Internet Download Manager) has dominated multi-threaded download acceleration and browser integration for years. Its problems: Windows-only, paid ($24.95 plus annual renewals), no BitTorrent support. FluxDown targets exactly this gap — free, open-source, cross-platform, and with BitTorrent/eD2K/HLS/DASH on top.

From first commit on 2026-07-03 to 3914 stars in three months, the demand for this positioning is clearly real.

GitHub: https://github.com/zerx-lab/FluxDown | ⭐ 3914 | AGPL-3.0 | Rust

---

### Architecture: One Engine, Multiple Hosts

`fluxdown_engine` is a pure Rust+Tokio library with zero UI or FFI dependencies. Multiple hosts connect to it:

- **GPUI desktop**: `fluxdown-desktop → fluxdown-agent → fluxdownd → engine`
- **Flutter mobile**: `Flutter app → hub → engine`
- **CLI (standalone mode)**: directly embeds the engine
- **Headless server**: agent + daemon + React Web UI

The daemon owns downloads (engine, database, queues, RSS, plugins, webhooks). The agent owns integration (UI gateway, FluxCloud, browser capture, desktop tray). Both expose the same REST/aria2/MCP interfaces through a shared `ApiHost` trait.

---

### Download Engine: Dynamic Segmentation + Slow-Segment Rescue

Segments split dynamically at runtime, not fixed at start. If a segment falls behind (server throttling, routing issues), idle workers take it over and re-split it. Combined with SQLite WAL persistence for resumable state, this is the core IDM-competitive feature.

---

### Protocol Coverage

HTTP/HTTPS, FTP, BitTorrent (DHT/UPnP/magnet), eD2K (Kad DHT source discovery + MD4 integrity verification), HLS (AES-decrypted), DASH. The eD2K support is unusual — still used for legacy resources on eMule networks.

---

### Browser Extension: 3-Layer Interception

Chrome/Edge (Chrome Web Store), Firefox (AMO). Three layers: standard download interception, streaming media sniffing (HLS/DASH detection), Alt+Click bypass + right-click send. Connects to the desktop agent via Native Messaging — no cloud relay. Tampermonkey userscript also available.

---

### Built-in MCP Server: AI-Managed Downloads

12 tools over Streamable HTTP (JSON-RPC 2.0, `POST /mcp`) on the same port as the management API. `download_add`, `download_list`, `download_pause/resume`, `download_remove`, `queue_list`, `rss_add/remove`. Configure Claude Desktop or Cursor to point at `http://127.0.0.1:17800/mcp` with a Bearer token and AI agents can manage your downloads directly.

Desktop enables this manually via Settings → API Service. Server mode enables it by default with a required access key.

---

### Server/NAS Deployment

```bash
docker compose -f docker/docker-compose.yml up -d
# Open http://<server>:17800/ to set access key (8–128 ASCII, letter + digit required)
```

Native packages for Synology DSM 6/7, QNAP, OpenWrt, Unraid CA, CasaOS/ZimaOS. Persist `/data` (database/logs/key) and download directory. Prefer SSD for `/data` when download disks sleep.

---

### License and Privacy

AGPL-3.0: modifications to source code must be disclosed if you run it as a network service. Local use is unaffected. Not zero-telemetry: anonymous install/daily-active stats enabled by default (`analytics_enabled` can disable it). Does not collect download content or task data. Local downloads require no FluxCloud account; cloud features are opt-in.

---

> AGPL-3.0. Maintained by zerx-lab, 3914 stars as of 2026-10-05. For technical reference only.
