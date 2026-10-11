---
title: "Vorssaint：把 Mac 日常工具收进一个菜单栏"
titleEn: "Vorssaint: A Modular Mac Menu Bar Toolkit"
description: "Vorssaint 将应用音量、系统监控、窗口管理、剪贴板与文件工具集中到菜单栏，可按需启用。本文核对 v3.4.1 DMG 的哈希、arm64 架构、系统版本、签名与公证，说明 macOS 14 与混音功能 14.4 的区别，以及权限和联网边界，帮助 Apple Silicon 用户确认下载来源、安装步骤和所需功能。"
descriptionEn: "Explore Vorssaint's modular Mac menu bar tools, verified v3.4.1 DMG, Apple Silicon support, audio version gates, permissions and local-first network limits."
wechatTitle: "Vorssaint：Mac菜单栏工具箱"
wechatDigest: "按需启用音量、监控与窗口工具，附官方DMG实查及系统版本边界。"
pubDate: "2026-10-11"
updatedDate: "2026-10-11"
category: "Tech-News"
tags: ["Vorssaint", "macOS", "Apple Silicon", "菜单栏工具", "开源软件", "效率工具"]
heroImage: "../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-banner.jpg"
---

Vorssaint 把应用音量、系统监控、窗口操作、剪贴板和文件工具放进一个 Mac 菜单栏入口，并允许按需启用功能。它适合希望减少常驻小工具、又想保留原生操作方式的 Apple Silicon 用户。

项目位于 `vorssaint/vorssaint-utils`，源码采用 GPL-3.0-or-later。2026 年 10 月 11 日的 GitHub 快照为 26,110 Star，最新版为 v3.4.1。关注度不能替代功能评测，我们此次实际检查的是官方安装包的来源、架构、签名与公证。

笔记里的获取方式成立：从 Releases 下载 DMG，打开后把 Vorssaint 拖入「应用程序」。官方要求 Apple Silicon、macOS 14 Sonoma 或更新版本；但部分能力有更高的系统门槛，例如应用级混音的音频 tap 需要 macOS 14.4+。

代码库：https://github.com/vorssaint/vorssaint-utils
官方 Releases：https://github.com/vorssaint/vorssaint-utils/releases
本次检查版本：https://github.com/vorssaint/vorssaint-utils/releases/tag/v3.4.1

## 一个入口里有哪些工具？

与其逐一列出几十个开关，更有用的是按日常任务理解它。

| 使用场景 | 官方提供的能力 | 选择时关注什么 |
| --- | --- | --- |
| 听音频与开会 | 按应用调整音量、分配输出设备、切换音频输出、麦克风控制 | 混音需要系统音频录制权限；各设备与系统版本支持不同 |
| 查看机器状态 | CPU、GPU、内存、温度、电池与网络信息，历史图和阈值提醒 | 监控采样会消耗资源；本次未测常驻 CPU 或耗电 |
| 多窗口工作 | 应用/窗口切换、窗口布局、Dock 预览、防误关闭 | 控制窗口通常需辅助功能；预览另需屏幕录制 |
| 输入与搬运内容 | 剪贴板历史、纯文本粘贴、文本片段、文件 Shelf、Finder 快捷操作 | 先确认是否需要保存复制历史，别把清空系统剪贴板等同于清空历史 |
| 整理应用与文件 | 应用更新、卸载残留预览、Homebrew 管理、端口查看与清理工具 | 删除、结束进程、安装升级是不同类型的操作，按需求启用 |
| 屏幕与日常控制 | 保持唤醒、截图录屏、OCR、颜色拾取、媒体转换和 Dynamic Island | 相机、录音、日历等权限分别控制，不需要一次授予全部 |

README 描述的 Dynamic Island 不只适用于带刘海的内置屏幕，v3.4.1 还支持其他显示器上的浮动形态。它也能展示代码助手的使用量与任务状态，这只是相关信息的展示入口，不能把工具箱当成一个新模型或执行工作任务的智能体。

风扇控制在官方功能列表中仍标为 beta；显示器硬件亮度控制也取决于设备，可能使用软件调暗作为后备。安装包能运行，与每台机器上的全部功能都可用，是两回事。

## 为什么“按需安装”比全开更有价值？

官方 Features Hub 可以单独安装或卸载功能，也提供预设组合。这里的“安装功能”是在工具箱内部选择模块，和下载整个 DMG 是不同层次；文档说明卸载模块后会停止加载并从界面移除，重新安装可以恢复其设置。

这有助于处理两个实际问题。第一，菜单栏入口集中后，仍需要控制后台监听和采样数量。第二，不同模块涉及的权限不同，只选择所需工具，才容易理解每项授权为何出现。

我们的判断是：这个项目值得关注的地方在于功能生命周期和权限一起管理。它不自动证明比多个独立工具更省内存或电量；要回答性能问题，需要在同一台机器、同一组功能和同一工作负载下测量。

开始时可以只启用两三项明确需要的功能。例如办公场景先试系统监控和窗口布局；音频场景再加入按应用音量。已有工具在处理快捷键或鼠标行为时，也应检查重复绑定，避免相同动作被两套程序同时接管。

![小M只打开系统监控、窗口布局和应用音量三个所需工具抽屉，其余模块保持关闭](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-01.png)

## 如何从正确入口下载安装？

1. 打开官方仓库，进入 Releases。
2. 下载对应版本的 DMG；本次文件名为 `Vorssaint-3.4.1.dmg`。
3. 打开磁盘映像，把 `Vorssaint.app` 拖入「应用程序」。
4. 从应用程序启动，按功能选择和系统提示完成配置。

官方也提供 Homebrew 入口：

```bash
brew install --cask vorssaint
```

GitHub 同名搜索结果、源码 ZIP、官方 DMG 与第三方重新打包版本并不相同。仓库说明官方构建由维护者发布；源码许可与名称、图标等品牌规则分别写在 LICENSE 和 TRADEMARKS.md 中。自行编译或分发修改版时，应核对对应文件，不把修改版呈现为官方发布。

源码开发构建示例是 `./build.sh --dev`。官方把 Developer variant 单独区分，并将安装和启动放在 `--install` 选项下。仅下载源代码，不等于已安装可用应用；本文没有执行日常环境安装，也没有启动应用。

## macOS 14+ 是否表示所有能力都支持 14.0？

不表示。我们从 DMG 里的 Info.plist 读到最低版本 `14.0`，并用 `file` 确认主程序为 arm64。这与官方的 Apple Silicon、macOS 14+ 要求一致。

同时，v3.4.1 对应的应用级音量实现对 Core Audio process tap 使用 macOS 14.4 的可用性判断。若你的系统停留在 14.0，不能仅因应用可安装，就期待按应用音量调节完整工作。

Release notes 还单独写明，按应用将音频发送到 AirPlay 的能力面向 macOS 27+。这个条件更高，与工具箱整体的最低系统版本不能混为一谈。本文没有测试音频路由、耳机、AirPlay 或不同系统版本的行为。

版本功能应优先对照发行说明，而不是只看更新中的 main 分支。此次文章的主文档快照为 `21eb10b80c4cb81fb4ff81c93a6d3afb18e74651`，安装包则固定为 v3.4.1；特定音频门槛也核对了对应 Release 源码。

## 权限和“本地优先”分别意味着什么？

官方将权限按功能划分。窗口控制与部分鼠标键盘行为需要辅助功能；窗口图像、截图和 OCR 需要屏幕录制；混音需要系统音频录制；相机、麦克风、日历与选定文件夹又是独立入口。

![小M用独立权限钥匙开启工具抽屉：系统音频录制对应混音，辅助功能对应窗口控制，屏幕录制对应窗口预览](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-02.png)

如果拒绝屏幕录制，官方文档说明应用切换可以退回图标模式，而依赖图像的预览与截屏功能不可用。这种降级比“必须全部授权才可启动”更有实际意义。具体功能仍应按对应版本帮助与系统提示判断。

“本地优先”也不等于永不联网。官方隐私文档列出了更新检查、手动网速测试、Homebrew 操作、可选歌词查询，以及显式创建截图或录屏临时链接等网络路径。分享临时链接会上传选中的内容，因此不能同时宣称所有截图始终只留在机器上。

剪贴板历史按文档存储在本机。自动清空系统剪贴板不会删除已经保存的历史项目，若目标是移除敏感复制内容，需要分别检查系统剪贴板与工具内历史。

可选 AI Agents 区域会读取已有助手会话日志中的用量、模型和项目等信息，官方说明新设置默认关闭。部分 API 价值是依据价格表估算的数字，应与真实订阅支出区分；本文没有启用该功能或审计全部数据流。

权限说明：https://github.com/vorssaint/vorssaint-utils/blob/21eb10b80c4cb81fb4ff81c93a6d3afb18e74651/docs/PERMISSIONS.md
隐私说明：https://github.com/vorssaint/vorssaint-utils/blob/21eb10b80c4cb81fb4ff81c93a6d3afb18e74651/docs/PRIVACY.md

## 官方 DMG 的本地检查结果是什么？

此次检查在 Apple Silicon Mac、macOS 26.6.2 上进行。安装包只读挂载后检查，完成即卸载磁盘映像；没有把应用复制到 Applications，也没有运行程序、申请权限或测试删除与系统调整功能。

| 检查 | 实际结果 | 能证明什么 |
| --- | --- | --- |
| 下载包大小 | 26,722,813 字节，约 26.7 MB | 此次下载的固定发行资产大小 |
| SHA-256 | 与 GitHub Release 资产 digest 一致 | 下载内容与该官方资产记录匹配 |
| 主程序架构 | Mach-O arm64 | 此安装包主程序面向 Apple Silicon |
| Info.plist | 版本 3.4.1，build 101，最低 macOS 14.0 | 包内声明与分发说明相符 |
| 代码签名 | `codesign --verify --deep --strict` 通过 | 包内签名验证通过 |
| Gatekeeper | `accepted`，来源为 Notarized Developer ID | 本机评估接受该带公证的构建 |
| 公证票据 | `stapler validate` 通过 | 包附带的公证票据校验通过 |

DMG 的 SHA-256 为：

```text
d3cebdd07795826294d821946cb1d40f5e8b85d2883a81153c552046cc80ab3a
```

这是分发验证，不是功能体验或安全审计。我们没有测量常驻内存、耗电、音频延迟、快捷键冲突、卸载准确率，也不能由签名通过推导出所有功能都无缺陷。

![小M先比对下载磁盘映像与官方记录的指纹，再检查签名和公证票据，应用仍未安装、未启动](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-03.png)

检查记录：https://github.com/MushroomDAO/blog/tree/main/source/20261011-vorssaint-utils

如果你只想沿用笔记中的安装路径，官方 Releases 是已确认的入口。安装后，先选少量工具，再逐项检查生效行为、权限与后台占用，比根据功能清单全开更容易判断是否适合自己。

另一类 Mac 原生工具可参考本站 EnvManage 来源核对：
https://blog.mushroom.cv/blog/onetake-envmanage-source-check/

## 常见问题

### Intel Mac 能用这个安装包吗？

官方要求 Apple Silicon。本次检查的 DMG 主程序是 arm64，没有确认 Intel 构建，不应把它当成 Universal 安装包。

### 它需要账号或订阅吗？

官方说明无账号、无订阅，源码采用 GPL-3.0-or-later。涉及外部包管理器、歌词服务或截图分享等能力，仍按各自路径运行。

### macOS 14.0 可以直接使用应用级混音吗？

不能仅凭应用的最低版本判断。对应音频 tap 在 Release 源码中要求 macOS 14.4+，其他能力也应单独核对版本与设备条件。

### 签名和公证通过意味着已经测过全部功能吗？

没有。它们核对发行包的签名和平台接受状态。本文没有运行应用，功能效果与后台开销需要另做体验与测量。

源码与下载：https://github.com/vorssaint/vorssaint-utils
固定发行页：https://github.com/vorssaint/vorssaint-utils/releases/tag/v3.4.1

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Vorssaint brings per-app volume, system monitoring, window controls, clipboard and file tools into one Mac menu bar entry, with features selected individually. It targets Apple Silicon users who want fewer separate utility apps while retaining native controls.

The GPL-3.0-or-later source lives at `vorssaint/vorssaint-utils`. Our October 11, 2026 snapshot recorded 26,110 stars; the latest release was v3.4.1. Popularity is not a functional benchmark. Our local verification covered the official distribution package, architecture, signature and notarization.

The supplied installation path is confirmed: download the DMG from Releases and drag Vorssaint into Applications. The declared minimum is Apple Silicon and macOS 14 Sonoma, while individual features can require newer systems. Per-app audio taps, for example, need macOS 14.4+.

Repository: https://github.com/vorssaint/vorssaint-utils
Releases: https://github.com/vorssaint/vorssaint-utils/releases
Inspected version: https://github.com/vorssaint/vorssaint-utils/releases/tag/v3.4.1

## Which everyday jobs does it cover?

| Task | Official capabilities | Boundary to consider |
| --- | --- | --- |
| Audio and calls | Per-app volume, output routing, output switching and microphone controls | Mixer needs system audio permission; devices and versions vary |
| Machine status | CPU, GPU, memory, temperatures, battery, network and history | Sampling consumes resources; we did not measure idle cost |
| Window work | Switcher, layouts, Dock previews and accidental-close protection | Controls need Accessibility; image previews additionally need Screen Recording |
| Moving content | Clipboard history, plain-text paste, snippets, Shelf and Finder actions | Clearing the system clipboard does not erase saved history |
| App/file management | Updates, uninstaller review, Homebrew, port and cleanup tools | Removal, process termination and software installation are distinct operations |
| Daily controls | Keep awake, capture, OCR, color picking, media conversion and Dynamic Island | Camera, audio, calendar and folder permissions remain separate |

Release v3.4.1 expands Dynamic Island to floating forms on displays without a notch. Its AI Agents view can display coding-assistant usage and task information; that does not make the toolkit a model or a task-executing agent.

Fan control remains labeled beta. Hardware display brightness depends on the device, with software dimming available as a fallback. A compatible installation does not establish universal support for every feature.

## Why choose modules instead of enabling everything?

The Features Hub installs or uninstalls individual modules and offers presets. This is an in-app lifecycle choice, separate from installing the DMG. Documentation says removed features stop loading and disappear, with settings restored when reinstalled.

That can make both background work and permission requests easier to understand. Consolidating icons does not eliminate sampling and input listeners. Different modules also require different access.

Our assessment is that managing feature lifecycle together with permission visibility is the useful design choice. It does not prove lower memory or battery consumption than separate utilities. That comparison needs the same machine, selected features and workload.

Start with two or three specific needs. For office work, try monitoring and window layouts; add per-app audio when required. Check for overlapping shortcuts or mouse behaviors when existing utilities handle the same actions.

![Xiao-M opens only the three needed drawers for system monitoring, window layouts and per-app volume, leaving all other modules closed](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-01.png)

## How do you obtain the official build?

1. Open the official repository and its Releases page.
2. Download the chosen DMG; we inspected `Vorssaint-3.4.1.dmg`.
3. Open the image and drag `Vorssaint.app` into Applications.
4. Launch it and choose features and their required permissions.

The documented Homebrew path is:

```bash
brew install --cask vorssaint
```

A source ZIP, official DMG, similarly named search result and third-party repack are different artifacts. The repository states that official builds come from the maintainer. LICENSE covers source copyright; TRADEMARKS.md separately specifies identity rules for unofficial or modified distributions.

For source development, `./build.sh --dev` creates a separate Developer variant; `--install` adds installation and launch. Downloading source is not installing an application. We did neither a daily-environment installation nor an application launch.

## Does macOS 14+ mean every feature works on 14.0?

No. The inspected Info.plist declares `14.0`, and the executable is arm64, confirming the overall distribution requirement.

The release's per-app mixer implementation gates Core Audio process taps on macOS 14.4. A user on 14.0 therefore should not infer complete mixer support from the minimum app version.

Release notes separately place per-app AirPlay routing on macOS 27+. This higher feature gate is independent of the toolkit's minimum. We did not test audio devices, AirPlay or behavior across operating-system releases.

Our main documentation snapshot is `21eb10b80c4cb81fb4ff81c93a6d3afb18e74651`, while the binary is pinned to v3.4.1. The audio availability gate was also checked against the corresponding release source. Evolving main documentation should not replace release-specific evidence.

## How do permissions and local-first behavior differ?

Official documentation groups permissions by feature. Accessibility supports window and some input control; Screen Recording supports images and captures; System Audio Recording supports the mixer. Camera, microphone, calendars and chosen folders have separate access.

![Xiao-M unlocks tool drawers with independent permission keys: System Audio Recording for mixing, Accessibility for window control and Screen Recording for window previews](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-02.png)

Without Screen Recording, the documented switcher can use app icons, while image-dependent previews and captures remain unavailable. This is a useful fallback rather than a requirement to grant every permission together.

Local-first does not mean disconnected. The privacy document lists update checks, manually initiated speed tests, Homebrew operations, optional lyric lookup and explicitly created temporary screenshot or recording links. Sharing a link uploads selected content; it cannot simultaneously guarantee that every capture always stays local.

Clipboard history is described as locally stored. Automatic system-clipboard clearing preserves already saved history, so sensitive-content removal needs attention to both stores.

The optional AI Agents view reads selected usage, model and project metadata from existing assistant logs and is off on new setups according to the documentation. API-value estimates should be distinguished from actual subscription spending. We did not enable this feature or audit all data flows.

Permissions: https://github.com/vorssaint/vorssaint-utils/blob/21eb10b80c4cb81fb4ff81c93a6d3afb18e74651/docs/PERMISSIONS.md
Privacy: https://github.com/vorssaint/vorssaint-utils/blob/21eb10b80c4cb81fb4ff81c93a6d3afb18e74651/docs/PRIVACY.md

## What did the local DMG inspection establish?

On an Apple Silicon Mac running macOS 26.6.2, we mounted the package read-only and detached it after inspection. We did not copy the app into Applications, launch it, request permissions or test destructive/system-adjustment features.

| Check | Result | Interpretation |
| --- | --- | --- |
| Asset size | 26,722,813 bytes, about 26.7 MB | Size of this pinned release download |
| SHA-256 | Matches GitHub's release asset digest | Bytes match the recorded official artifact |
| Architecture | Mach-O arm64 | Main executable targets Apple Silicon |
| Info.plist | 3.4.1, build 101, minimum macOS 14.0 | Package declarations match distribution notes |
| Signature | Deep, strict codesign verification passed | Bundle signature validation passed |
| Gatekeeper | Accepted, Notarized Developer ID | This machine accepted the notarized build |
| Stapled ticket | `stapler validate` passed | Attached notarization ticket validation passed |

DMG SHA-256:

```text
d3cebdd07795826294d821946cb1d40f5e8b85d2883a81153c552046cc80ab3a
```

This is distribution verification, not a functional review or security audit. We did not measure idle memory, battery, audio latency, shortcut conflicts or uninstaller accuracy. A valid signature does not establish defect-free features.

![Xiao-M compares the downloaded disk image fingerprint with the official record, then checks its signature and notarization ticket while the app remains uninstalled and unopened](../../assets/images/vorssaint-utils-macos-menu-bar-toolkit-fig-03.png)

Evidence: https://github.com/MushroomDAO/blog/tree/main/source/20261011-vorssaint-utils

For the supplied download workflow, official Releases is the confirmed entry. Select a small set of features, verify behavior and inspect permissions and background use before broadening the setup.

Related native Mac tooling: https://blog.mushroom.cv/blog/onetake-envmanage-source-check/

## Frequently asked questions

### Is this an Intel-compatible installer?

The project requires Apple Silicon, and the inspected main executable is arm64. We did not confirm an Intel build; this artifact should not be presented as Universal.

### Does it require an account or subscription?

The project states neither is required and licenses its source under GPL-3.0-or-later. Optional external services and package-manager operations still use their respective paths.

### Does macOS 14.0 guarantee per-app mixing?

No. The release source requires macOS 14.4+ for the relevant audio taps. Other features need their own version and device checks.

### Have all features been tested because notarization passed?

No. Signature and notarization checks concern distribution and platform acceptance. We did not run the app; usability and resource costs require separate measurement.

Source and download: https://github.com/vorssaint/vorssaint-utils
Pinned release: https://github.com/vorssaint/vorssaint-utils/releases/tag/v3.4.1

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
