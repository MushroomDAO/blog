---
title: 'Immich：114K Stars 的自托管 Google Photos，为什么它是目前最成熟的开源替代方案'
titleEn: "Immich: 114K-Star Self-Hosted Google Photos — Why It's the Most Mature Open-Source Alternative"
description: "AGPL-3.0 开源，NestJS + SvelteKit + Flutter，完整的人脸识别、CLIP 语义搜索、RAW 支持、OAuth 登录、Docker 部署。114K stars，2022 年创建，持续活跃更新。自托管不等于备份——3-2-1 原则是必须的。"
descriptionEn: "AGPL-3.0, NestJS + SvelteKit + Flutter, face recognition, CLIP semantic search, RAW support, OAuth, Docker deployment. 114K stars, created 2022, actively maintained. Self-hosting isn't backup — the 3-2-1 rule still applies."
pubDate: "2026-09-15"
updatedDate: "2026-09-15"
category: "Tech-News"
tags: ["self-hosted", "open-source", "photos", "Google-Photos", "privacy", "NestJS", "Flutter", "Docker", "AGPL"]
heroImage: "../../assets/images/immich-self-hosted-google-photos-alternative-114k-stars-banner.jpg"
---

> 📌 开源仓库：immich-app/immich
> GitHub：https://github.com/immich-app/immich
> 官网：https://immich.app
> License：AGPL-3.0 | Stars：114,218 | Forks：6,919

---

Google Photos 的问题不是功能不好，而是你的照片、视频、元数据全部在 Google 的服务器上，Google 扫描分析它们，免费额度用完要付钱，某天可能关闭或改变政策。

Immich 把 Google Photos 的体验复刻到你自己的服务器上：自动备份、人脸识别、语义搜索、相册分享、RAW 支持——全部跑在你控制的机器上。

114K stars，2022 年创建，今天仍然在活跃更新。这是目前社区认可度最高的开源 Google Photos 替代方案。

---

## 一、技术栈拆解

Immich 不是一个脚本，而是一个完整的系统：

```
immich/
├── server/          # NestJS 后端 API
├── web/             # SvelteKit 前端
├── mobile/          # Flutter iOS + Android App
├── machine-learning/ # 人脸识别 + CLIP 模型服务
└── docker/          # Docker Compose 部署配置
```

**后端（NestJS + Node.js）**：处理媒体上传、元数据、缩略图生成、相册管理、用户权限。

**前端（SvelteKit）**：Web 界面，支持时间线浏览、地图视图、相册管理、管理后台。

**移动端（Flutter）**：iOS 和 Android 原生应用，支持后台自动备份。与 Google Photos App 的体验设计对齐——切换成本低。

**机器学习服务**：独立微服务，运行人脸识别模型和 CLIP 语义搜索模型。可以在有 GPU 的机器上加速，也可以纯 CPU 跑（慢一些）。

---

## 二、核心功能清单

| 功能 | 移动端 | Web |
|------|--------|-----|
| 上传/查看照片视频 | ✓ | ✓ |
| 自动备份 | ✓ | — |
| 人脸识别 | ✓ | ✓ |
| 语义搜索（metadata/对象/CLIP） | ✓ | ✓ |
| 相册共享 | ✓ | ✓ |
| RAW 格式支持 | ✓ | ✓ |
| OAuth 单点登录 | ✓ | ✓ |
| 管理后台 | — | ✓ |

值得展开说的三个：

**语义搜索**：不只是文件名搜索，而是三层：元数据（拍摄时间、地点、设备）+ 对象识别（"有狗的照片"）+ CLIP 语义检索（"海边日落"）。找照片的方式和 Google Photos 几乎一致。

**人脸识别**：自动检测并聚合相同人物的照片，支持手动标注名字。数据本地，不送第三方。

**RAW 支持**：相机用户直接备份 RAW 文件，Web 界面生成预览缩略图，原始文件完整保留。

---

## 三、部署：Docker Compose

```yaml
# docker-compose.yml（简化版）
services:
  immich-server:
    image: ghcr.io/immich-app/immich-server:release
    volumes:
      - ${UPLOAD_LOCATION}:/usr/src/app/upload
    env_file: .env
    ports:
      - '2283:2283'

  immich-machine-learning:
    image: ghcr.io/immich-app/immich-machine-learning:release
    volumes:
      - model-cache:/cache

  database:
    image: ghcr.io/immich-app/postgres:14-vectorchord0.3.0-pgvectors0.2.0
    env_file: .env

  redis:
    image: docker.io/redis:6.2-alpine
```

依赖：PostgreSQL（含 pgvectors 向量插件）+ Redis。官方文档有完整的 Docker Compose 文件，通常十几分钟可以跑起来。

**硬件要求**：至少 4GB 内存，机器学习服务可按需关闭（关掉后就没有人脸识别和 CLIP 搜索）。NAS 用户可以把 Docker 跑在 Synology、TrueNAS、QNAP 上——社区文档覆盖了主流 NAS 平台。

---

## 四、必须提：自托管 ≠ 备份

Immich 在文档和 README 里多次强调这一点：

> **Always follow the 3-2-1 backup plan for your precious photos and videos!**
> 3 份副本，2 种介质，1 份异地

**自托管只解决了"数据在自己手里"的问题，不解决"数据安全"的问题。** 如果你的服务器硬盘坏了、房子被淹了、Docker volume 误操作删了，Immich 没有任何内置保障。

实际的备份策略：
- Immich 跑在本地 NAS
- NAS 做本地 RAID（防单盘故障）
- 定期把数据同步到云存储（Backblaze B2、Wasabi 等便宜的对象存储）
- 或者另外一台不在同一地点的设备

把 Google Photos 替换成 Immich，记得同时把备份策略也建起来。

---

## 五、许可证：AGPL-3.0 的含义

AGPL-3.0 对个人自托管没有任何限制——装在家里的服务器上随便跑。

如果你要把 Immich 改造后作为 SaaS 服务对外提供，AGPL 要求你也开源改动后的代码，并且给用户下载源码的权利。这是专门防止"拿开源代码做云服务但不回馈社区"的条款。

个人用户、小团队内部用：无影响。商业 SaaS 用：需要仔细看许可证条款。

---

## 拆解结论

114K stars 不是靠营销起来的——Immich 在 2022 年之后几乎没有停止过活跃开发（今天仍在推送），社区文档覆盖主流 NAS 和部署场景，功能完整度对标 Google Photos 的核心功能。

如果你有一台 NAS 或者 VPS，想从 Google Photos 迁出来，Immich 是目前最成熟、最接近即插即用的选项。

需要记住的一点：装完之后，把备份策略也一起建好。

---

## 开源代码与模型仅供学习、勿直接用于工作。

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: immich-app/immich
> GitHub: https://github.com/immich-app/immich
> Website: https://immich.app
> License: AGPL-3.0 | Stars: 114,218 | Forks: 6,919

---

Google Photos' problem isn't that it lacks features — it's that your photos, videos, and metadata all live on Google's servers, Google scans and analyzes them, the free quota runs out, and policies can change any day.

Immich replicates the Google Photos experience on your own server: automatic backup, face recognition, semantic search, album sharing, RAW support — all running on hardware you control.

114K stars, created 2022, still actively updated today. This is the highest-community-validated open-source Google Photos alternative available.

---

## I. Tech Stack Breakdown

Immich isn't a script — it's a complete system:

```
immich/
├── server/          # NestJS backend API
├── web/             # SvelteKit frontend
├── mobile/          # Flutter iOS + Android app
├── machine-learning/ # Face recognition + CLIP model service
└── docker/          # Docker Compose deployment configs
```

**Backend (NestJS + Node.js):** handles media upload, metadata, thumbnail generation, album management, user permissions.

**Frontend (SvelteKit):** web UI with timeline browsing, map view, album management, admin console.

**Mobile (Flutter):** native iOS and Android apps with background auto-backup. The UX mirrors Google Photos — low switching cost.

**Machine learning service:** independent microservice running face recognition and CLIP semantic search models. GPU-accelerated if available; CPU-only mode works (slower).

---

## II. Feature Matrix

| Feature | Mobile | Web |
|---------|--------|-----|
| Upload/view photos and videos | ✓ | ✓ |
| Auto-backup | ✓ | — |
| Facial recognition | ✓ | ✓ |
| Semantic search (metadata/objects/CLIP) | ✓ | ✓ |
| Album sharing | ✓ | ✓ |
| RAW format support | ✓ | ✓ |
| OAuth SSO | ✓ | ✓ |
| Admin console | — | ✓ |

Three worth expanding on:

**Semantic search:** three layers — metadata (date, location, device) + object detection ("photos with a dog") + CLIP semantic retrieval ("sunset at the beach"). Matches the Google Photos search experience closely.

**Face recognition:** auto-detects and clusters photos of the same person; supports manual name labeling. All data stays local, nothing sent to a third party.

**RAW support:** camera users back up RAW files directly; the web UI generates preview thumbnails while preserving the original files intact.

---

## III. Deployment: Docker Compose

```yaml
# docker-compose.yml (simplified)
services:
  immich-server:
    image: ghcr.io/immich-app/immich-server:release
    volumes:
      - ${UPLOAD_LOCATION}:/usr/src/app/upload
    env_file: .env
    ports:
      - '2283:2283'

  immich-machine-learning:
    image: ghcr.io/immich-app/immich-machine-learning:release
    volumes:
      - model-cache:/cache

  database:
    image: ghcr.io/immich-app/postgres:14-vectorchord0.3.0-pgvectors0.2.0
    env_file: .env

  redis:
    image: docker.io/redis:6.2-alpine
```

Dependencies: PostgreSQL (with pgvectors extension) + Redis. The official docs include a complete Docker Compose file — most deployments are up in under 15 minutes.

**Hardware requirements:** minimum 4GB RAM. The ML service can be disabled (which removes face recognition and CLIP search). NAS users can run Docker on Synology, TrueNAS, or QNAP — community docs cover the major NAS platforms.

---

## IV. Important: Self-Hosted ≠ Backed Up

Immich emphasizes this repeatedly in docs and README:

> **Always follow the 3-2-1 backup plan for your precious photos and videos!**
> 3 copies, 2 different media, 1 offsite

**Self-hosting solves "data in your own hands" — it doesn't solve "data is safe."** If your server's drive fails, your house floods, or you accidentally delete a Docker volume, Immich has no built-in protection.

A practical backup strategy:
- Immich on a local NAS
- NAS with local RAID (protection against single drive failure)
- Regular sync to cloud object storage (Backblaze B2, Wasabi, etc.)
- Or a second device at a different physical location

When you migrate from Google Photos to Immich, build your backup strategy at the same time.

---

## V. License: What AGPL-3.0 Means

AGPL-3.0 imposes no restrictions on personal self-hosting — run it on your home server freely.

If you modify Immich and offer it as a SaaS service, AGPL requires you to open-source your changes and give users access to download the source code. This is specifically designed to prevent "take open-source code, build a cloud service, give nothing back."

Personal use, internal team use: no impact. Commercial SaaS: read the license terms carefully.

---

## Teardown Summary

114K stars didn't come from marketing — Immich has been under active development almost continuously since 2022 (with commits landing today), community docs cover major NAS and deployment scenarios, and feature completeness matches Google Photos' core functionality.

If you have a NAS or VPS and want to migrate out of Google Photos, Immich is the most mature, closest-to-plug-and-play option available.

One thing to remember: after setup, also build your backup strategy.

---

*Open-source code and models are for learning purposes only — do not use directly in production work.*

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
