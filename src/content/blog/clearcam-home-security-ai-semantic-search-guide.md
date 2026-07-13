---
title: "普通家庭也能用：ClearCam 让旧摄像头变成能听懂你说话的 AI 监控"
titleEn: "Any Family Can Use This: ClearCam Turns Any Security Camera into an AI That Understands You"
description: "开源项目 ClearCam（892⭐）让任何 RTSP 摄像头支持 AI 目标检测、Qwen3 VL 智能通知摘要、CLIP 语义搜索，以及手机实时查看——全部本地运行，不上传任何数据。"
descriptionEn: "ClearCam (892⭐) adds AI object detection, Qwen3 VL smart notification summaries, CLIP semantic search, and live mobile viewing to any RTSP security camera — all running locally, no data leaves your home."
pubDate: "2026-07-13"
updatedDate: "2026-07-13"
category: "Tech-Experiment"
tags: ["家庭安防", "开源", "AI监控"]
heroImage: "../../assets/images/clearcam-home-security-ai-semantic-search-guide-banner.jpg"
---

> 本文基于开源项目 **roryclear/clearcam**（892⭐）整理，面向普通家庭用户，讲清楚怎么用它把家里现有的摄像头变成一套带 AI 的本地监控系统。

---

## 先说它能做什么

传统家庭监控的问题是：**录了 24 小时的视频，但当你真的想回看某件事时，只能一分钟一分钟地拖进度条。**

ClearCam 解决的就是这个问题。它给任何支持 RTSP 协议的摄像头加上这几层能力：

| 功能 | 说明 |
|------|------|
| 目标检测 | 识别人、车、动物等，实时框出 |
| 区域警报 | 画一个区域，只在该区域有人/车时通知 |
| AI 通知摘要 | 用 Qwen3 VL 视觉语言模型生成中文/英文描述（"门口有人拿了快递"） |
| 语义搜索 | 用 CLIP 模型，输入文字搜历史录像（"昨天穿红衣服的人"） |
| 手机查看 | iOS/Android App，支持实时直播和事件片段回放 |
| 端对端加密 | Premium 功能，远程查看时数据加密传输 |

核心优势是**完全本地运行**——检测、AI 推理、录像全在你自己的 Mac 或 Linux 主机上，不经过任何云服务器。

---

## 你需要准备什么

### 必须有的
- 一台 **Mac 或 Linux 电脑**（Windows 需要等 ffmpeg 修复）
- **Python 3.11 或以上**
- **ffmpeg**（`brew install ffmpeg` 或 `apt install ffmpeg`）

### 摄像头
任何支持 **RTSP 流**的 IP 摄像头都可以用。市面上 200 元以上的家用 IP 摄像头大多支持 RTSP，常见品牌如海康威视、大华、萤石、TP-Link Tapo 均可。

**还没有摄像头？**
可以先用这个公开的交通摄像头测试：
```
https://webcam.elcat.kg/Too-Ashu_Tunnel_North/index.m3u8
```

### 手机 App（可选）
- iOS：App Store 搜索「ClearCam」，或扫码下载
- Android：Google Play 搜索「ClearCam」

---

## 安装步骤：10 分钟搞定

### 第一步：拿到代码

```bash
git clone https://github.com/roryclear/clearcam.git
cd clearcam
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

依赖极少：`tinygrad`（轻量 ML 框架）、`numpy`、`opencv-python-headless`。第一次运行会自动下载模型权重。

### 第三步：启动

```bash
python3 clearcam.py
```

如果你的电脑有多核 CPU，加上 `BEAM=2` 可以显著提升推理速度（第一次运行会多花几分钟编译）：

```bash
BEAM=2 python3 clearcam.py
```

### 第四步：打开浏览器

访问 `http://localhost:8080`，你会看到 ClearCam 的管理界面。

### 第五步：添加摄像头

在界面里填入你摄像头的 RTSP 地址。格式通常是：

```
rtsp://用户名:密码@摄像头IP地址:554/stream1
```

具体地址看摄像头说明书。以萤石为例：`rtsp://admin:你的密码@192.168.1.100:554/h264/ch1/main/av_stream`

---

## 三个你会最常用的功能

### 1. 区域警报：只在特定地方触发通知

在摄像头画面里用鼠标框出一个区域（比如大门口、停车位），然后设置：

- 检测哪些目标（人、车、宠物）
- 触发多少次后发通知
- 哪些时间段有效（比如只在 22:00–07:00 开启）

这样你就不会收到"院子里的树在晃"这种噪音通知，只有真正有人或车进入关键区域时才提醒你。

### 2. AI 通知摘要：不看视频也知道发生了什么

ClearCam 内置了 **Qwen3 VL**（通义千问视觉语言模型），当检测到事件时，它会对现场截图生成一段自然语言描述，直接发到你手机：

> "门口站着一个穿深色上衣的人，手里拿着一个包裹，朝门口走来。"

而不是只说"检测到：人（1）"。

对家里老人独居的情况，这个摘要比冷冰冰的分类标签有用得多。

### 3. 语义搜索：用说话的方式找视频

这是最有意思的功能。ClearCam 使用 **CLIP 模型**对录像帧做语义嵌入，你可以在搜索框里用自然语言描述你要找的场景：

- **"红色的车"** → 找出所有出现红色汽车的片段
- **"穿蓝色衣服的人"** → 锁定特定人物
- **"骑自行车的人"** → 找出自行车进出记录
- **"晚上门口有人"** → 跨摄像头找夜间事件

CLIP 做的是**语义匹配，不是关键词搜索**——即使录像里没有文字，它也能理解"骑自行车"这个概念和画面的对应关系。

结合区域警报，还可以做**描述触发告警**：在警报设置里填入描述词，当摄像头看到符合描述的场景时主动推送通知，而不是单纯靠目标类型触发。

---

## 手机 App 怎么用

下载 ClearCam iOS 或 Android App 后：

1. 在 App 里注册（clearcam.org），获取一个 **Premium 用户 ID**
2. 把这个 ID 填入 Web 界面的设置里
3. App 就能接收通知、查看实时直播和事件片段了

> **本地模式（免费）**：在家里局域网里，不用注册也能在浏览器查看直播和录像。
> **远程模式（Premium）**：出门在外，用加密通道通过 App 远程查看，需要注册账号。

---

## 常见家庭部署方案

### 方案 A：旧 MacBook 当主机

家里闲置的 MacBook（2019 年以后的都行）装上 ClearCam，接 2–4 路摄像头，全天候运行。功耗低，安静，放在书柜角落就够了。

### 方案 B：Intel NUC / 树莓派 5

如果不想占用笔记本，买一台闲置的 Intel NUC 或树莓派 5，装 Ubuntu，运行 ClearCam。树莓派 5 可以跑 1–2 路，NUC 可以跑 3–4 路。

### 方案 C：顺带跑在 NAS 上

如果家里有群晖或威联通 NAS，且 NAS 用的是 Linux 内核，可以在 NAS 上运行 ClearCam，让 NAS 同时做监控主机和录像存储。

---

## 几个实际使用建议

**摄像头选购**：优先选支持 RTSP 且分辨率 ≥ 1080p 的型号。目标检测的准确率和分辨率直接相关。如果摄像头装在室外，选 IP66 防水级别。

**存储规划**：按 1080p 摄像头每小时约 500MB~1GB 估算。如果接 4 路、保留 7 天录像，需要大约 1TB 空间。

**AI 摘要触发频率**：Qwen3 VL 推理有一定延迟，建议设置"检测到同一对象持续 N 秒后才生成摘要"，避免高频触发。

**CLIP 搜索提示**：语义搜索对英文描述稍微比中文准，因为 CLIP 模型主要用英文数据预训练。搜索"red car"的结果通常比"红色的车"稍好。

---

## 和商业方案的区别

| | ClearCam | 海康威视/萤石云 | Nest Cam |
|-|----------|----------------|---------|
| 数据存储 | 本地 | 云端 | 云端 |
| 隐私 | 完全自主 | 品牌服务器 | Google |
| 月费 | 免费（本地） | 云存储收费 | 订阅制 |
| AI 能力 | 语义搜索 + AI 摘要 | 有限 | 有限 |
| 自定义程度 | 开源可改 | 闭源 | 闭源 |

如果你对数据隐私有要求，或者不想每月付订阅费，ClearCam 是目前最完整的本地自托管方案之一。

---

GitHub：github.com/roryclear/clearcam

iOS App：App Store 搜索「ClearCam」

Android App：Google Play 搜索「ClearCam」

© 2026 Author: Mycelium Protocol

<!--EN-->

## Any Family Can Use This: ClearCam Turns Any Security Camera into an AI That Understands You

> Based on **roryclear/clearcam** (892⭐) — a self-hosted AI security camera system running entirely on your own Mac or Linux machine.

---

### What It Does

Traditional home security systems record 24 hours of footage but finding a specific event means scrubbing through hours of video. ClearCam solves this with a local AI layer on top of any RTSP security camera:

| Feature | Description |
|---------|-------------|
| Object Detection | YOLOv9 + RF-DETR, real-time bounding boxes for people, cars, animals |
| Zone Alerts | Draw a custom zone; only trigger when objects enter that area |
| AI Notification Summaries | Qwen3 VL generates natural-language descriptions of what happened |
| Semantic Search | CLIP-powered search: type "person in red jacket" to find matching clips |
| Mobile App | iOS and Android apps for live viewing and event clips |
| End-to-End Encryption | Premium: encrypted remote viewing via the app |

Everything runs locally. No footage leaves your home.

---

### Requirements

- Mac or Linux (Windows needs an ffmpeg fix)
- Python 3.11+
- ffmpeg
- Any RTSP-capable IP camera (most cameras above ~$30 support RTSP)

**No camera yet?** Test with this public traffic feed: https://webcam.elcat.kg/Too-Ashu_Tunnel_North/index.m3u8

---

### Setup in 10 Minutes

```bash
git clone https://github.com/roryclear/clearcam.git
cd clearcam
pip install -r requirements.txt
python3 clearcam.py
# open http://localhost:8080
```

Add your RTSP URL in the web UI:
```
rtsp://username:password@camera-ip:554/stream1
```

For extra performance on multi-core CPUs:
```bash
BEAM=2 python3 clearcam.py
```

---

### The Three Features You'll Use Most

**Zone Alerts**: Draw a zone on the camera view (front door, parking spot), select which object types to monitor, set active hours, and set a notification count threshold. Eliminates false alerts from trees moving.

**AI Notification Summaries (Qwen3 VL)**: Instead of "Detected: person (1)", you get: "A person in a dark jacket is approaching the front door carrying a package." Runs locally on every detection event.

**Semantic Search (CLIP)**: Type a natural language description in the search box — "red car", "person with bicycle", "someone at the door at night" — and CLIP searches all recorded frames for semantic matches. This is meaning-based, not keyword-based: it understands concepts even without text in the video.

---

### Deployment Options for Families

| Option | Hardware | Cameras |
|--------|----------|---------|
| Idle MacBook | Any 2019+ MacBook | 2–4 cameras |
| Intel NUC (Ubuntu) | Any Gen 8+ NUC | 3–4 cameras |
| Raspberry Pi 5 | Pi 5 8GB | 1–2 cameras |
| Existing Linux NAS | Synology/QNAP (Linux) | 1–2 cameras |

**Storage**: ~500MB–1GB per camera per hour at 1080p. 4 cameras × 7 days ≈ ~1TB.

---

### vs. Commercial Systems

| | ClearCam | Cloud NVR (Hikvision/Nest) |
|-|----------|---------------------------|
| Data location | Your hardware | Brand servers |
| Monthly fee | Free (local) | Subscription |
| AI search | Semantic (CLIP) | Limited |
| Privacy | Full control | Third-party |
| Customizable | Open source | Closed |

GitHub: github.com/roryclear/clearcam

© 2026 Author: Mycelium Protocol
