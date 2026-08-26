---
title: "Disk Analyzer：原生 SwiftUI 磁盘分析工具，交互式旭日图 + 中英双语，无遥测，开源免费"
titleEn: "disk-analyzer-macos-native-sunburst-swift-bilingual"
description: "daniel-weih/disk-analyzer 是一款原生 macOS 磁盘空间分析工具，基于 SwiftUI 开发，核心是多级交互式旭日图（双击下钻）。区分「已分配磁盘空间」和「文件逻辑大小」，处理稀疏文件和硬链接不会造成误导性统计。中英文界面在应用内一键切换并记忆设置。无网络请求、无遥测、无账号。支持 Apple Silicon，MIT 开源，v2.2.0 提供预构建 DMG。"
descriptionEn: "daniel-weih/disk-analyzer is a native macOS disk space analyzer built with SwiftUI, centered on an interactive multi-level sunburst chart with double-click drill-down. Distinguishes allocated disk space (st_blocks) from logical file size (st_size), handles sparse files and hard links correctly. In-app Chinese/English switching remembered across launches. No network requests, no analytics, no accounts. Apple Silicon native, MIT license, v2.2.0 prebuilt DMG available."
pubDate: "2026-08-26"
updatedDate: "2026-08-26"
category: "Tech-News"
tags: ["开源", "macOS", "Swift", "SwiftUI", "磁盘分析", "工具", "Apple Silicon", "中文支持"]
heroImage: "../../assets/images/disk-analyzer-macos-native-sunburst-swift-bilingual-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

GitHub：daniel-weih/disk-analyzer ⭐ 1 | Swift | MIT | v2.2.0  
语言：原生 SwiftUI | 系统要求：macOS 13+，Apple Silicon  
发布：2026-08-26 | 中英双语界面

---

## 这是什么

Disk Analyzer 是一个原生 macOS 磁盘空间分析工具。

它的核心是一个多级交互式旭日图（sunburst chart）——可以双击下钻进入子目录，直观地看到哪些文件夹和文件占用了最多空间。同时提供目录和文件的排名列表，以及搜索和排序功能。

值得关注的是它在磁盘计算上的用心：区分**已分配磁盘空间**（`st_blocks × 512`，与 `du -sk` 一致）和**文件逻辑大小**（`st_size`）——对于稀疏文件、硬链接、APFS 克隆，这两个数字可以差异很大，大多数磁盘工具不做区分，会给出误导性总量。

界面支持简体中文和英文，在应用内一键切换，并在多次启动间记忆设置。

---

## 核心功能

**可视化与导航**
- 多级旭日图，双击下钻进入子目录
- 当前目录级别、最大目录、最大文件三组排名
- 搜索、按大小/名称排序
- Finder 中显示文件、安全移入废纸篓（需确认）
- Home 按钮保留最近一次扫描结果和下钻位置

**扫描范围**
- 启动磁盘（整机）
- 当前用户主目录
- 外置存储卷
- 任意选择的文件夹

**精确的磁盘计量**

| 指标 | 实现方式 | 说明 |
|------|---------|------|
| 已分配大小 | `lstat(2)` → `st_blocks × 512` | 同 `du -sk`，稀疏文件只计已分配块，硬链接 inode 只计一次 |
| 文件大小 | `st_size` | 文件内容的表观长度，稀疏文件/硬链接/APFS 克隆可能远大于实际占用 |

不跨文件系统边界，使用设备和 inode 标识避免 APFS firmlink 路径重复计数，优先显示 `/Users`、`/Applications` 等可理解路径。

**诊断信息**
- 显式报告跳过的挂载卷和文件系统边界
- 不静默地把不可读路径处理为零字节
- APFS 快照、可清除空间、共享克隆区域单独展示，不混入普通目录总量

---

## 隐私与安全

- **无网络请求**：没有分析 SDK、遥测、账号、云存储
- **扫描结果留在内存**：不以浏览历史形式持久化
- **只读元数据**：读取名称、路径和文件系统元数据，不读取文件内容
- **清理使用系统废纸篓**：可恢复，需要用户确认
- **受保护的系统根目录**（`/System` 等）无法从应用内移入废纸篓

**完全磁盘访问权限**

macOS 不允许应用自行授予"完全磁盘访问"权限。Disk Analyzer 在需要广泛扫描之前，引导用户前往"系统设置 → 隐私与安全性 → 完全磁盘访问"，并通过对受保护 TCC 数据库的只读探针验证权限是否真正生效——而不是简单地把"打开设置"或"重启应用"当作已授权的证明。

---

## 安装

**方式一：从源码构建（推荐）**

需要 macOS 13+、Xcode 或 Xcode 命令行工具附带的 Swift 工具链。

```bash
git clone https://github.com/daniel-weih/disk-analyzer.git
cd disk-analyzer
swift run
```

构建应用包：

```bash
./scripts/package_app.sh
open dist/DiskAnalyzer.app
```

构建并验证 DMG：

```bash
./scripts/package_dmg.sh
open dist/DiskAnalyzer-2.2.0-arm64.dmg
```

**方式二：直接下载 DMG**

[下载 Disk Analyzer 2.2.0（Apple Silicon）](https://github.com/daniel-weih/disk-analyzer/releases/download/v2.2.0/DiskAnalyzer-2.2.0-arm64.dmg)

> 注意：可下载版本使用 ad-hoc 签名，未经 Apple 公证。macOS 可能提示无法验证开发者。Control-click 应用图标 → 选择"打开"即可绕过。

---

## 为什么值得关注

macOS 上的磁盘分析工具不少——DaisyDisk、GrandPerspective、OmniDiskSweeper，都是老牌付费或老旧软件。

Disk Analyzer 的差异点：

1. **原生 SwiftUI**：不是 Electron，不是 Qt，跟系统外观完全一致
2. **磁盘计量诚实**：把已分配空间和逻辑大小分开报告，不给你一个看起来很大但含义不清的数字
3. **完全免费开源**：MIT，代码在 GitHub，没有付费功能、没有订阅
4. **中文界面**：国内用户不需要切系统语言，应用内一键切换，重启记忆

刚发布一天，Stars 还是个位数，但功能完整度和代码质量看起来是认真做的项目。

---

**相关链接**

- GitHub：https://github.com/daniel-weih/disk-analyzer
- 下载（v2.2.0 DMG）：https://github.com/daniel-weih/disk-analyzer/releases/download/v2.2.0/DiskAnalyzer-2.2.0-arm64.dmg

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Disk Analyzer: Native SwiftUI Disk Space Tool for macOS — Sunburst Chart, Bilingual, No Telemetry, Open Source

*by Mycelium Protocol*

---

GitHub: daniel-weih/disk-analyzer ⭐ 1 | Swift | MIT | v2.2.0  
Language: Native SwiftUI | Requirements: macOS 13+, Apple Silicon  
Released: 2026-08-26 | Chinese/English bilingual interface

---

### What It Is

Disk Analyzer is a native macOS disk space analyzer.

Its core feature is an interactive multi-level sunburst chart — double-click any ring segment to drill down into a subdirectory and see exactly where space is going. Alongside the chart are sortable directory and file ranking lists, plus search.

It pays careful attention to disk accounting: it distinguishes **allocated disk space** (`st_blocks × 512`, consistent with `du -sk`) from **logical file size** (`st_size`). For sparse files, hard links, and APFS clones, these numbers can differ dramatically — most disk tools don't separate them, leading to misleading totals.

The interface supports Simplified Chinese and English, switchable inside the app, with the choice remembered across launches.

---

### Core Features

**Visualization and navigation**
- Multi-level sunburst chart with double-click drill-down
- Three ranking views: current directory level, largest directories, largest files
- Search, sort by size or name
- Reveal in Finder, safe move-to-Trash (requires confirmation)
- Home button preserves the most recent scan result and drill-down position

**Scan scope**
- Startup disk (full machine)
- Current user's home directory
- External volumes
- Any selected folder

**Precise disk accounting**

| Metric | Implementation | Notes |
|--------|---------------|-------|
| Allocated size | `lstat(2)` → `st_blocks × 512` | Same as `du -sk`; sparse files count only allocated blocks; same hard-linked inode counted once |
| File size | `st_size` | Apparent content length; sparse files/hard links/APFS clones can be much larger than actual disk use |

Scans don't cross filesystem boundaries. Device and inode identities prevent duplicate APFS firmlink paths; understandable paths like `/Users` and `/Applications` are preferred in results.

**Diagnostics**
- Explicitly reports skipped mounted volumes and filesystem boundaries
- Never silently treats unreadable paths as zero bytes
- APFS snapshots, purgeable space, and shared clone extents are kept distinct from ordinary directory totals

---

### Privacy and Safety

- **No network requests**: no analytics SDKs, telemetry, accounts, or cloud storage
- **Scan results stay in process memory**: not persisted as browsing history
- **Read-only metadata**: reads names, paths, and filesystem metadata; never file contents
- **Cleanup via system Trash**: recoverable, requires user confirmation
- **Protected system roots** (`/System`, etc.) cannot be moved to Trash from the app

**Full Disk Access**

macOS doesn't allow an app to grant itself Full Disk Access. Before a broad scan, Disk Analyzer guides the user to System Settings → Privacy & Security → Full Disk Access, and verifies the grant using a read-only probe of a protected TCC database — rather than treating "opened Settings" or "restarted the app" as proof that access was actually granted.

---

### Install

**Option 1: Build from source (recommended)**

Requires macOS 13+ and the Swift toolchain from Xcode or Xcode Command Line Tools.

```bash
git clone https://github.com/daniel-weih/disk-analyzer.git
cd disk-analyzer
swift run
```

Build an app bundle:

```bash
./scripts/package_app.sh
open dist/DiskAnalyzer.app
```

Build and verify a DMG:

```bash
./scripts/package_dmg.sh
open dist/DiskAnalyzer-2.2.0-arm64.dmg
```

**Option 2: Download the DMG**

[Download Disk Analyzer 2.2.0 for Apple Silicon](https://github.com/daniel-weih/disk-analyzer/releases/download/v2.2.0/DiskAnalyzer-2.2.0-arm64.dmg)

> Note: the downloadable app uses an ad-hoc signature and is not notarized by Apple. macOS may warn it cannot verify the developer. Control-click the app in Finder → Open to bypass.

---

### Why It Matters

macOS disk analyzers aren't new — DaisyDisk, GrandPerspective, OmniDiskSweeper have been around for years. Most are paid, abandoned, or both.

Disk Analyzer's differentiators:

1. **Native SwiftUI**: not Electron, not Qt — matches the system UI completely
2. **Honest disk accounting**: reports allocated space and logical size separately, not a single ambiguous number
3. **Fully free and open source**: MIT, code on GitHub, no paid features, no subscriptions
4. **Bilingual**: in-app Chinese/English switching — no need to change system language

Released today, still in single-digit stars, but the feature completeness and design care suggest a serious project worth watching.

---

**Links**

- GitHub: https://github.com/daniel-weih/disk-analyzer
- Download (v2.2.0 DMG): https://github.com/daniel-weih/disk-analyzer/releases/download/v2.2.0/DiskAnalyzer-2.2.0-arm64.dmg

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
