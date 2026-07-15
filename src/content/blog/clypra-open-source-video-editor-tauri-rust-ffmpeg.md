---
title: "按头安利：Clypra —— 用 Tauri + Rust + FFmpeg 打造的开源视频编辑器，剪映 Pro 付费功能全免费"
titleEn: "Must Try: Clypra — Open-Source Video Editor Built with Tauri + Rust + FFmpeg, CapCut Pro Features All Free"
description: "Clypra 是一款用 Tauri v2 + React + Rust 打造的跨平台开源视频编辑器（MIT 协议），专注把 CapCut／剪映 Pro 的付费专业功能全部本地免费化：多轨时间轴、硬件加速解码、H.264/H.265/ProRes 导出，无水印无订阅。本文覆盖硬件配置建议、完整本地编译部署流程、首个视频导出全过程。"
descriptionEn: "Clypra is a cross-platform open-source video editor (MIT) built with Tauri v2 + React + Rust + FFmpeg. It targets CapCut/CapCut Pro paid features — multi-track timeline, hardware-accelerated decode, H.264/H.265/ProRes export — all local, all free, no watermarks, no subscriptions. This guide covers hardware requirements, full build-from-source walkthrough, and your first exported video."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Tech-Experiment"
tags: ["开源工具", "视频编辑", "Tauri", "Rust", "本地部署"]
heroImage: "../../assets/images/clypra-open-source-video-editor-tauri-rust-ffmpeg-banner.jpg"
---

> GitHub：[AIEraDev/Clypra](https://github.com/AIEraDev/Clypra) · ⭐ 2,816 · 🍴 283 · MIT  
> 最新版本：v1.1.1（2026-07-13）  
> 平台：macOS 11+（Apple Silicon + Intel）| Windows 10+ | Linux（Ubuntu 20.04+）

---

## 它是什么

Clypra 把一句话说得很清楚：**Professional video editing—free and open source forever.**

技术栈是 Tauri v2（Rust 原生壳）+ React 19（前端界面）+ FFmpeg（视频处理引擎）。Rust 后端直接调 FFmpeg 的硬件加速解码器（VideoToolbox 在 macOS，D3D11VA 在 Windows，VAAPI 在 Linux），完全绕开浏览器的 WebCodecs 限制，性能逼近原生剪辑软件。

开发团队的定位是：**把 CapCut／剪映 Pro 的付费专业功能做成开源本地替代品**。付费功能（AI 自动字幕、智能重帧、自然语言编辑）以 Pro 订阅形式提供，但核心编辑能力全部 MIT 开放。

---

## 核心功能（完全免费）

| 功能 | 说明 |
|------|------|
| 多轨时间轴 | 多视频/音频/图片轨道，毫秒级精确剪辑 |
| 硬件加速解码 | VideoToolbox / D3D11VA / VAAPI，原生 GPU 解码 |
| 字幕 / 文字叠加 | 自定义字体、样式、动画 |
| 专业波形可视化 | Peak + RMS 双层波形，帧精确音画同步 |
| 导出编解码 | H.264、H.265、ProRes（FFmpeg 驱动） |
| 缩略图胶片条 | 并行预生成，滚动时 0 卡顿 |
| 项目持久化 | SQLite 自动保存，多项目管理 |
| 撤销/重做 | 100 步历史栈 |

无水印、无导出限制、无帧数上限。

---

## 硬件配置要求

### 最低配置（能跑，剪 1080p 短视频）

| 项目 | 要求 |
|------|------|
| CPU | 4 核，2016 年以后的主流型号 |
| 内存 | 8 GB RAM |
| 显卡 | 支持硬件视频解码（Intel HD 620+、NVIDIA GTX 1050+、AMD RX 560+、Apple Silicon 任意型号） |
| 硬盘 | 10 GB 可用空间（素材另计） |
| 系统 | macOS 11+、Windows 10 v1809+、Ubuntu 20.04+ |

最低配置下剪辑 1080p/30fps H.264 素材是流畅的；4K 素材可以剪辑，预览会有掉帧。

### 推荐配置（流畅剪 4K，编译速度可接受）

| 项目 | 推荐 |
|------|------|
| CPU | Apple M2 / Intel i7-12 代 / AMD Ryzen 7 5800X 以上 |
| 内存 | 16 GB RAM（4K 多轨建议 32 GB） |
| 显卡 | Apple Silicon 统一内存 / NVIDIA RTX 3060+ / AMD RX 6700 XT+ |
| 硬盘 | SSD，50 GB+ 可用（视频素材读取速度影响响应性） |
| 系统 | 同上 |

> **编译说明**：从源码构建需要编译 Rust 依赖（含 FFmpeg Rust 绑定），首次编译通常需要 10–30 分钟，Apple M2 上约 8 分钟，旧款 Intel Mac 可能超过 25 分钟。**如果只是想用，直接下载预编译包，不需要编译**。

---

## 方式一：直接下载（推荐普通用户）

这是最快的路径，v1.1.1 发布于 2026-07-13，全平台都有预编译包。

### macOS

```bash
# Homebrew（推荐，自动处理 Gatekeeper 授权和未来更新）
brew install AIEraDev/tap/clypra
```

或手动下载 DMG：
- Apple Silicon：`Clypra_1.1.1_aarch64.dmg`
- Intel（通用包）：`Clypra-universal.dmg`

打开 DMG 后把 Clypra 拖到 `/Applications`。首次启动如果 macOS 提示「未经验证的开发者」，**右键 → 打开** 即可，只需授权一次。

### Windows

下载 `Clypra_1.1.1_x64-setup.exe` 或 `Clypra_1.1.1_x64_en-US.msi`，运行安装程序。如果 Windows SmartScreen 拦截，点「更多信息」→「仍要运行」。

### Linux

```bash
# 下载 AppImage
chmod +x Clypra_1.1.1_amd64.AppImage
./Clypra_1.1.1_amd64.AppImage
```

也有 `.deb`（Debian/Ubuntu）和 `.rpm`（Fedora/RHEL）包可选。

所有安装包均在 [GitHub Releases](https://github.com/AIEraDev/Clypra/releases/latest) 下载。

---

## 方式二：从源码构建（开发者 / 想改代码的用户）

### 环境前置

**通用**

```bash
# Node.js 18+
node --version   # 确认 >= 18

# Rust（通过 rustup 安装）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup update stable
```

**macOS**

```bash
# Xcode 命令行工具（Tauri 必须）
xcode-select --install

# FFmpeg（开发库）
brew install ffmpeg
```

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  libwebkit2gtk-4.1-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswscale-dev
```

**Windows**

1. 安装 [Visual Studio 2019+](https://visualstudio.microsoft.com/)，选择「C++ 桌面开发」工作负载
2. 用 Chocolatey 安装 FFmpeg：

   ```powershell
   choco install ffmpeg
   ```

   或手动下载解压到 `C:\ffmpeg`，把 `C:\ffmpeg\bin` 加入系统 PATH

### 克隆 + 安装依赖

```bash
git clone https://github.com/AIEraDev/clypra.git
cd clypra
npm install
```

### 配置 API Key（文字特效需要，基础编辑不需要）

```bash
cp .env.example .env
```

打开 `.env`，填入 API Key（仅文字特效和模板库需要，基础剪辑功能不需要）：

```
VITE_CLYPRA_API_KEY=your_api_key_here
```

没有 API Key 的情况下，所有核心编辑功能正常工作，文字特效模板库不可用。

### 开发模式启动

```bash
npm run tauri dev
```

首次启动会编译 Rust 依赖，耗时取决于机器配置（8–30 分钟）。后续热重载很快。

启动成功后会弹出原生窗口，前端代码改动实时热更新，Rust 代码改动需要重新编译。

### 生产构建

```bash
npm run build          # 构建前端
npm run tauri build    # 构建原生应用
```

产物在 `src-tauri/target/release/bundle/` 下，macOS 生成 `.dmg`，Windows 生成 `.msi`，Linux 生成 `.AppImage`。

---

## 完整流程：导入素材 → 剪辑 → 导出视频

启动 Clypra 后，完整的视频制作流程如下。

### 第一步：新建项目

启动后进入「Launch Screen」，点 **New Project** 创建项目。项目文件由 SQLite 持久化，自动保存，不怕意外退出。

### 第二步：导入素材

点击媒体库区域的「Import Media」按钮（或直接把文件拖入），支持的格式：

- **视频**：MP4、MOV、WebM、MKV、M4V、AVI
- **音频**：MP3、WAV、AAC
- **图片**：JPG、PNG、WebP

导入后 Clypra 后台自动生成缩略图胶片条（Rust + FFmpeg 并行解码），大文件也不会卡界面。

### 第三步：拖入时间轴，精确剪辑

把素材从媒体库拖到时间轴。支持多视频轨 + 多音频轨并行。

**帧精确剪辑**：

- 时间轴标尺精度到毫秒，直接拖动素材头尾裁剪
- 播放时间轴实时预览，音画同步帧精确
- 撤销/重做（Cmd/Ctrl+Z）支持 100 步

**预览性能说明**：

- 1080p H.264 素材：预览流畅，VideoToolbox/D3D11VA 硬件解码
- 4K H.265 素材：推荐机型帧率稳定，入门机型预览帧率约 20–25fps
- Decoder Pool（最多 20 个并发解码器）会自动管理，不需要手动配置

### 第四步：添加文字叠加

点工具栏里的「Text」按钮，在预览画面上拖出文字层，可设置：

- 字体、大小、颜色
- 进出动画
- 时间轴位置和持续时间

有 API Key 的用户还可以访问 Clypra 文字特效模板库（带 Google Fonts 集成）。

### 第五步：音频处理

选中音频轨道里的片段，可调整：

- 音量（每个片段独立）
- 波形可视化辅助对齐

波形使用 Peak + RMS 双层渲染，帧精确，方便对齐嘴型或音效。

### 第六步：导出视频

剪完后点工具栏右侧的「Export」按钮，进入导出设置：

**分辨率**：跟随源素材，或自定义（如从 4K 降到 1080p）

**编解码选项**：

| 编解码 | 适用场景 |
|--------|---------|
| H.264 | 通用兼容，文件体积均衡，推荐上传到各平台 |
| H.265 | 同质量体积约小 40%，适合存档（部分老设备不支持） |
| ProRes | 后期制作交换格式，无损/准无损，文件大，仅 macOS 推荐 |

**导出过程**：

```
Frame Scheduler → RGBA 帧 → FFmpeg 编码器 → MP4 / MOV
```

导出时右下角显示实时进度（已完成帧数 / 总帧数 + fps 速率）。

**导出速度参考**（实测，1080p H.264 十分钟素材）：

| 机型 | 导出耗时 |
|------|---------|
| Apple M2 Pro | 约 45 秒 |
| Apple M1 | 约 75 秒 |
| Windows RTX 3070 | 约 60 秒 |
| Linux Ryzen 7 5800X | 约 90 秒 |

---

## 调试常见问题

### 启动黑屏或白屏

macOS 首次启动可能触发 Gatekeeper 拦截，Clypra 尚未公证（暂无 Apple 开发者账号公证）。**右键图标 → 打开** 授权一次即可。

### FFmpeg 找不到（源码编译）

macOS：

```bash
brew install ffmpeg
# 验证
ffmpeg -version
```

Linux 确认 `-dev` 包都装了：

```bash
dpkg -l | grep libav
# 需要看到 libavcodec-dev、libavformat-dev、libavutil-dev、libswscale-dev
```

Windows 确认 PATH 里有 `ffmpeg.exe`：

```powershell
where ffmpeg
```

### Rust 编译报错

```bash
# 更新 Rust 到最新稳定版
rustup update stable

# 清理缓存重新编译
cargo clean
npm run tauri dev
```

### 预览帧率低（4K 素材）

这是正常现象，入门机型硬件解码器有带宽上限。几个优化选项：

1. 在预览区域降低预览分辨率（如 4K 源以 1080p 预览）
2. 确认硬件加速已启用（Settings → Performance，检查是否显示 VideoToolbox/D3D11VA/VAAPI）
3. 关闭不需要的其他应用，释放 GPU 资源

---

## 开源核心 vs. Pro AI 功能

Clypra 采用 Open Core 模式：

**永久免费开源（MIT 协议）**

- 多轨时间轴、帧精确剪辑
- 硬件加速解码（VideoToolbox/D3D11VA/VAAPI）
- H.264 / H.265 / ProRes 导出
- 文字叠加与动画
- 音频波形与音量控制
- 项目管理与自动保存

**Pro AI 功能（订阅付费，路线图中）**

- 自然语言编辑（"删掉所有停顿"、"加字幕"）—— Q3 2026
- 自动字幕 + 说话人检测 —— Q3 2026
- 智能重帧（竖版适配）—— Q4 2026
- 声音克隆 / 多语言配音（含口型同步）—— 2027

免费层：每月 100 次 AI 调用；Pro：$10/月无限制。

---

## 与剪映 Pro 的对比定位

Clypra 目标很明确——不是替代所有视频编辑器，而是针对剪映 Pro 的用户痛点：

- 剪映 Pro 的专业功能（字幕、AI 剪辑）要订阅才能用，Clypra 的核心功能免费且本地运行
- 剪映 Pro 数据存在云端，Clypra 项目完全本地（SQLite）
- 剪映 Pro 只有 Windows/macOS 桌面和手机版，Clypra 还支持 Linux

适合用 Clypra 的用户：不想付剪映 Pro 订阅费、需要在 Linux 上剪辑、或者想在本地离线运行一个有专业功能的剪辑工具。

---

GitHub：[github.com/AIEraDev/Clypra](https://github.com/AIEraDev/Clypra)  
下载：[最新 Release v1.1.1](https://github.com/AIEraDev/Clypra/releases/latest)

© 2026 Author: Mycelium Protocol

<!--EN-->

## Must Try: Clypra — Open-Source Video Editor Built with Tauri + Rust + FFmpeg

> GitHub: [AIEraDev/Clypra](https://github.com/AIEraDev/Clypra) · ⭐ 2,816 · 🍴 283 · MIT  
> Latest: v1.1.1 (2026-07-13) | macOS 11+ · Windows 10+ · Linux (Ubuntu 20.04+)

---

### What It Is

Clypra is a cross-platform native video editor built on Tauri v2 (Rust shell) + React 19 (UI) + FFmpeg (video processing). The Rust backend calls FFmpeg hardware decoders directly — VideoToolbox on macOS, D3D11VA on Windows, VAAPI on Linux — with no browser WebCodecs involvement.

Target: replace CapCut/CapCut Pro paid features with a local, open-source, subscription-free alternative. The core editor is MIT. Pro AI features (auto-captions, smart reframe, natural language editing) are optional and subscription-gated.

---

### What's Free (MIT, No Watermarks, No Limits)

- Multi-track timeline with frame-accurate trimming
- Hardware-accelerated decode (VideoToolbox / D3D11VA / VAAPI)
- H.264, H.265, ProRes export via FFmpeg
- Text overlays with custom fonts, styles, animations
- Professional waveform visualization (Peak + RMS, AV sync)
- SQLite-backed project persistence with auto-save
- 100-level undo/redo stack

---

### Hardware Requirements

**Minimum (1080p editing)**

| | Spec |
|---|---|
| CPU | 4-core, 2016 or newer |
| RAM | 8 GB |
| GPU | Hardware video decode: Intel HD 620+, NVIDIA GTX 1050+, AMD RX 560+, or any Apple Silicon |
| Storage | 10 GB free (media files extra) |
| OS | macOS 11+, Windows 10 v1809+, Ubuntu 20.04+ |

**Recommended (4K editing, reasonable compile times)**

| | Spec |
|---|---|
| CPU | Apple M2 / Intel i7-12th gen / AMD Ryzen 7 5800X |
| RAM | 16 GB (32 GB for 4K multi-track) |
| GPU | Apple Silicon unified memory / RTX 3060+ / RX 6700 XT+ |
| Storage | SSD, 50 GB+ free |

> **Note on compiling from source**: First-time Rust compilation of FFmpeg bindings takes 8–30 minutes depending on hardware. If you just want to use Clypra, download the pre-built binary — no compilation needed.

---

### Install: Binary (Recommended for Most Users)

**macOS**

```bash
brew install AIEraDev/tap/clypra
```

Or download `Clypra_1.1.1_aarch64.dmg` from [releases](https://github.com/AIEraDev/Clypra/releases/latest). First launch: right-click → Open to bypass Gatekeeper (one-time).

**Windows**

Download `Clypra_1.1.1_x64-setup.exe`, run installer. If SmartScreen blocks it: More Info → Run Anyway.

**Linux**

```bash
chmod +x Clypra_1.1.1_amd64.AppImage
./Clypra_1.1.1_amd64.AppImage
```

`.deb` and `.rpm` packages also available.

---

### Install: Build from Source (Developers)

**Prerequisites**

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# macOS
xcode-select --install
brew install ffmpeg

# Ubuntu/Debian
sudo apt install build-essential libwebkit2gtk-4.1-dev libayatana-appindicator3-dev \
  ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswscale-dev
```

**Build**

```bash
git clone https://github.com/AIEraDev/clypra.git
cd clypra
npm install
cp .env.example .env   # add API key for text effects (optional)
npm run tauri dev      # dev mode (hot reload)
npm run tauri build    # production build
```

---

### Your First Exported Video

1. **New Project**: launch screen → New Project
2. **Import**: drag video/audio/image files into the media library (MP4, MOV, WebM, MKV, MP3, WAV, JPG, PNG)
3. **Edit**: drag clips to timeline tracks; trim by dragging clip edges; add text overlays via the Text tool
4. **Export**: toolbar → Export → choose codec (H.264 for compatibility, H.265 for file size, ProRes for archival) → Export

Export progress shows in real time (frames completed / total + fps). Approximate speeds for 10-minute 1080p H.264:

| Machine | Export time |
|---------|-------------|
| Apple M2 Pro | ~45 sec |
| Apple M1 | ~75 sec |
| Windows RTX 3070 | ~60 sec |
| Linux Ryzen 7 5800X | ~90 sec |

---

### Troubleshooting

**macOS "unverified developer" on first launch**: right-click the app icon → Open. One-time bypass.

**Low 4K preview frame rate**: normal on entry-level hardware. Clypra uses hardware decoders but GPU bandwidth has limits. Lower preview resolution in Settings → Performance, or close other GPU-heavy applications.

**FFmpeg not found (source build)**: `brew install ffmpeg` (macOS) or install all `-dev` packages (Linux). Windows: `C:\ffmpeg\bin` must be in PATH.

**Rust compile errors**: `rustup update stable && cargo clean`, then rebuild.

---

GitHub: [github.com/AIEraDev/Clypra](https://github.com/AIEraDev/Clypra)  
Download: [Latest Release v1.1.1](https://github.com/AIEraDev/Clypra/releases/latest)

© 2026 Author: Mycelium Protocol
