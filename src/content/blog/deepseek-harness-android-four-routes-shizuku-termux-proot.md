---
title: "DeepSeek Harness 装进安卓手机的四条路线：只有一条真能操作手机"
titleEn: "Four Ways to Put DeepSeek Harness on Android — Only One Actually Operates the Phone"
description: "把 DSH 搬上安卓有四种做法：原生 APK 走 Shizuku 免 root 系统特权（166★）、Termux 补丁层只有 100KB（51★）、内嵌 Node.js 运行时的 41MB 独立 APK（18★）、Capacitor + PRoot 塞进完整 Ubuntu 24.04 用户空间（5★）。四者都是 MIT，但本质分成两类：三个是「在手机上跑 DSH」，只有一个是「让 AI 操作这台手机」——能点屏幕、装应用、改系统设置。附各路线的权限边界、体积、保活能力对比。"
descriptionEn: "Four ways to get DeepSeek Harness onto Android: a native APK using Shizuku for root-free system privileges (166★), a 100KB Termux patch layer (51★), a 41MB standalone APK embedding a Node.js runtime (18★), and a Capacitor app shipping a full Ubuntu 24.04 userspace via PRoot (5★). All MIT — but they split into two kinds: three run DSH on the phone, and exactly one lets the AI operate the phone, tapping the screen, installing apps and changing system settings."
pubDate: 2026-09-06
updatedDate: 2026-09-06
category: "Tech-News"
tags: ["开源", "DeepSeek", "Harness", "Android", "端侧AI", "AI Agent", "Termux", "自托管"]
heroImage: "../../assets/images/deepseek-harness-android-four-routes-shizuku-termux-proot-banner.jpg"
author: "Mycelium Protocol"
---

本站写过不少 DeepSeek Harness（DSH），但一直漏掉一个方向：**它跑在手机上会怎么样。**

补上这一课的时候发现，社区在一个月内做出了四条完全不同的路线，而且它们解决的根本不是同一个问题。

**最重要的分界线**：其中三条是「**在手机上跑 DSH**」——手机只是个运行宿主，跟跑在树莓派上没本质区别；只有一条是「**让 AI 操作这台手机**」——能点屏幕、装应用、改系统设置、截图理解。

后者才是「手机变成 Agent 终端」，前者只是把电脑上的东西挪了个地方。

---

## 四条路线一览

| | 仓库 | ★ | 实现语言 | 形态 | 体积 |
|---|---|---|---|---|---|
| ① | `woaiys3/deepseek-harness-android-app` | 166 | Java | 原生 APK + 系统特权 | 仓库 6.4MB |
| ② | `Vengisk/deepseek-harness-termux` | 51 | Shell | Termux 补丁层 | **100KB** |
| ③ | `thness/dsh-mobile` | 18 | Kotlin | 内嵌 Node.js 的独立 APK | APK 41MB |
| ④ | `dphmoblie/deepseek-harness-android` | 5 | TypeScript | Capacitor + PRoot Ubuntu | 仓库 7.5MB |

四个全部 MIT 协议，全部基于 `@deepseek-ai/dsh` 0.1.0-rc.6。建库时间集中在 2026-08-13 到 08-16 这四天里——典型的社区同时开工。

---

## ① 原生 APK + Shizuku：唯一真能操作手机的那个

`woaiys3/deepseek-harness-android-app`，166 星，四条里最活跃。

它的关键不在于「把 DSH 装进 APK」，而在于**打通了三条系统特权通道**，而且是分层降级的：

1. **Root（su）** —— 有 root 就走这条，权限最高
2. **Shizuku** —— 无 root 时的主通道。Shizuku 通过 ADB 授权拿到系统 shell 权限，让普通 App 能调用本需要系统签名的 API。AI 由此能**装应用、点屏幕、改系统设置、截图、模拟输入**
3. **无障碍服务（v1.7.0 新增）** —— 系统设置里开启「屏幕助手」后，**不需要 root 也不需要 Shizuku**，AI 能读屏、点击、输入、滚动、无障碍截图理解

三条通道互补，且**都不授予也能正常用**——退化成文件读写、预览、编辑（只需「所有文件访问」权限），未授权时 AI 不会反复尝试系统操作，需要时会引导你去授权。

其余工程细节：
- 包名 `com.deepseek.harness`，前台保活，锁屏挂后台不被杀，任务完成推送通知
- `dshroot` 外置到 `/sdcard/DeepSeekHarness`，**卸载重装不丢 AI 的运行时改动**
- 保留完整 DSH 内核、插件生态和 RPC API，前端用 DSH 原生界面
- 触摸优化 + 软键盘适配 + 首启权限引导页（9 项权限一站式）

**这条路线的意义**：手机第一次成为 Agent 的**操作对象**而不只是运行宿主。你可以让它去点某个 App 的按钮、改个设置、装个东西。

**代价**：Shizuku 每次重启手机都要重新用 ADB 激活（除非有 root）；无障碍服务权限在国内很多机型上会被系统「优化」掉；权限面铺得越大，出问题时的影响面也越大。

---

## ② Termux 补丁层：100KB，最轻，也最讲究

`Vengisk/deepseek-harness-termux`，51 星，**只有 100KB**——因为它根本不是 App，是一套补丁。

它解决的问题很具体：官方 `@deepseek-ai/dsh` 是给 glibc 的 Linux 发行版编译的，依赖若干原生模块，在 Android 的 Bionic libc 上要么编译失败要么行为异常。多数移植的做法是**把出问题的插件关掉**；这个仓库的做法是**打补丁让每个功能都能用**。

而且补丁是用 `diff -u` 对着未修改的上游 tarball（`@deepseek-ai/dsh` 0.1.0-rc.6）自动生成的，作者明确说这样「精确且可复现」。

它的功能状态表写得很诚实，值得抄：

| 组件 | 状态 | 说明 |
|---|---|---|
| `dsh web` | ✅ | 服务跑在 `http://127.0.0.1:3080` |
| `dsh headless` | ✅ | 单会话无头模式 |
| `dsh plugin` | ✅ | 插件管理 |
| HMR 热重载 | ✅ | 需 `--expose-internals` 启动 |
| 子进程 | ✅ | `node-pty` 对着 Termux bionic sysroot 编译 |
| **Bash 沙箱** | ⚠️ **受限** | `node-pty` 可用；**`bubblewrap` 被 Android sepolicy 在运行时挡住**，安全降级为 `SandboxUnavailableError` |
| 权限系统 | ✅ | 随 `node-pty` 恢复 |
| 会话持久化 | ✅ 已修 | `link(2)` → `rename(2)` 回退绕开 Android sepolicy |
| Bash 终端（PTY） | ✅ 已修 | Termux 下默认 shell 路径解析为 `/usr/bin/bash` |
| 移动端 UI | ✅ 自动 | 窄屏（<1024px）隐藏侧栏、目录改抽屉、对话全宽 |

**注意那行 ⚠️**：`bubblewrap` 沙箱在 Android 上是被系统安全策略（sepolicy）挡死的，不是没实现。这意味着**在手机上跑 DSH，沙箱隔离这一层是缺失的**——AI 执行的 bash 命令没有额外的隔离层保护。这条对所有基于 Termux 的方案都成立。

**适合谁**：已经在用 Termux、能接受敲命令、想要最轻量最可控的方案。

**不适合谁**：没听说过 Termux 的人。这条路线的门槛在 Termux 本身，不在 DSH。

---

## ③ 内嵌 Node.js 的独立 APK：最省事的那个

`thness/dsh-mobile`，18 星，Kotlin，**APK 41MB**。

定位很直白：**一个 APK，把完整的 DeepSeek Harness 装进口袋。** 内嵌 Node.js 运行时 + 官方 Web UI，安装即用，无需额外依赖。

明确的硬件要求（其他三个都没写这么清楚）：
- Android 8.0+（API 26）
- **4GB+ RAM 推荐**
- **500MB+ 存储**
- 首次启动等待引擎初始化**约 30 秒**

特性：前台服务后台常驻、外部存储工作区、可选 Shizuku 集成、OTA 更新支持。

**它和 ① 的区别**：① 是「AI + 手机操作能力」，③ 是「AI 装进手机」。③ 也接了 Shizuku，但重心明显在「把 DSH 搬进来能跑」，而不是「让 AI 操作系统」。

**适合谁**：想最快试一下、不想折腾权限的人。下载 41MB 的 APK，装，等 30 秒。

---

## ④ Capacitor + PRoot Ubuntu：最重，也最完整

`dphmoblie/deepseek-harness-android`，5 星，TypeScript。

思路最激进：**在手机里跑一个完整的 Ubuntu 24.04 ARM64 用户空间**，里面装 Node.js 24.19.0 和 `@deepseek-ai/dsh` 0.1.0-rc.6，用 PRoot 起来，外面套一层 Capacitor App。

CI 构建流程是：编译移动端 Harness 对话前端 → 注入进 Ubuntu 24.04 ARM64 镜像 → 把校验过的 `rootfs.bundle` 和 `runtime-manifest.json` 嵌进 APK。所以**官方 APK 离线可装**，不需要联网下载 rootfs。

有个技术细节值得注意，它把一个常见误解说破了：

> Android WebView 不跑 Node.js。安装的 Ubuntu 环境里必须有精确落在 `^22.19.0 || >=24.0.0` 范围内的 Node.js。

构建门槛也最高：Node.js `^22.19.0 || >=24.0.0`、JDK 23.0.1、Android SDK 35 + 兼容 NDK、以及一套 pin 死的 ARM64 PRoot runner/loader（来自 Operit2 Android runtime 工具链的某个具体 commit）。

**适合谁**：想要完整 Linux 环境、要跑的不只是 DSH 的人。

**代价**：最重的一条。PRoot 是用户态的系统调用拦截，性能损耗明显。

---

## 那到底选哪个？

按你想要什么来选，不是按星数：

| 你想要 | 选 |
|---|---|
| 让 AI 真正操作我的手机（点屏幕、装 App、改设置） | **① woaiys3** —— 唯一选项 |
| 最轻、最可控，我已经会用 Termux | **② Vengisk** |
| 最快试一下，别让我折腾 | **③ thness** |
| 我要一个完整 Linux，不止跑 DSH | **④ dphmoblie** |

**还有一个共同的前提要说清楚**：这四条路线跑的都是 DSH 这个 harness 本体，模型推理仍然走 API。手机在这里是 Agent 的**执行环境**，不是推理设备。想在手机上本地推理是另一个问题。

---

## 手机端 Agent 的边界在哪？

值得泼一盆冷水。哪些任务真的适合放在手机上跑？

**适合**：
- 需要手机独有能力的——读通知、操作某个只有手机版的 App、用手机的登录态
- 长时间挂着等的——前台保活加通知，跑完推给你
- 人在外面，只有手机的时候

**不适合**：
- 需要大量文件读写和编译的——手机存储 IO 和散热都跟不上
- 需要沙箱隔离的——上面说过，`bubblewrap` 在 Android 上被 sepolicy 挡死
- 长时间高负载的——发热降频，还耗电

**最实际的用法可能是**：手机当 Agent 的「远程遥控端」和「特定能力提供者」，而不是主力工作机。

---

## 缺口：我没有安卓机，四条路线一条都没实测

这条必须说在前面，本文**是路线地图，不是实测报告**。

所有信息来自四个仓库的 README、GitHub API 元数据和它们的构建文档。以下全部未验证：

1. **四个 APK 是否真能装起来跑通**——尤其 ④ 的 PRoot 方案，构建要求那么严格，release APK 在不同机型上的兼容性存疑
2. **Shizuku 免 root 的实际权限边界**——README 说能「装应用、点屏幕、改系统设置」，具体能到哪一步、国内厂商 ROM 会挡掉哪些，没测
3. **性能与耗电**——四条路线的实际速度差多少、跑一个任务掉多少电，没有数字
4. **模拟器验证不了关键部分**——Shizuku 和前台保活恰恰是模拟器上测不准的东西，所以我没用模拟器凑数

想看实测的话，这需要一台真机。如果你手上有安卓机跑过其中任何一条，欢迎告诉我实际情况。

---

## 一句话总结

四条路线里，三条在回答「怎么把 DSH 搬进手机」，一条在回答「怎么让 AI 用这台手机」。**如果你要的是后者，选择只有一个；如果是前者，按你能接受的折腾程度挑就行。**

而共同的天花板是：Android 的 sepolicy 挡掉了 `bubblewrap` 沙箱——手机上跑 Agent，隔离这一层目前是缺的。

> 📌 原生 APK + Shizuku：https://github.com/woaiys3/deepseek-harness-android-app
> Termux 补丁层：https://github.com/Vengisk/deepseek-harness-termux
> 内嵌 Node.js APK：https://github.com/thness/dsh-mobile
> Capacitor + PRoot Ubuntu：https://github.com/dphmoblie/deepseek-harness-android
> DSH 上游：https://github.com/deepseek-ai/deepseek-harness

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

This site has covered DeepSeek Harness (DSH) plenty, but has consistently missed one direction: **what happens when it runs on a phone.**

Filling that gap turned up four entirely different community routes built within a single month — and they are not solving the same problem.

**The important dividing line**: three of them **run DSH on the phone**, where the phone is merely a host, not meaningfully different from a Raspberry Pi. Exactly one lets **the AI operate the phone** — tapping the screen, installing apps, changing system settings, reading the screen via screenshots.

Only the latter turns a phone into an agent terminal; the rest just relocate a desktop workload.

---

## The four routes

| | Repo | ★ | Language | Form | Size |
|---|---|---|---|---|---|
| ① | `woaiys3/deepseek-harness-android-app` | 166 | Java | Native APK + system privileges | repo 6.4MB |
| ② | `Vengisk/deepseek-harness-termux` | 51 | Shell | Termux patch layer | **100KB** |
| ③ | `thness/dsh-mobile` | 18 | Kotlin | Standalone APK embedding Node.js | APK 41MB |
| ④ | `dphmoblie/deepseek-harness-android` | 5 | TypeScript | Capacitor + PRoot Ubuntu | repo 7.5MB |

All four are MIT, all built on `@deepseek-ai/dsh` 0.1.0-rc.6. Their creation dates cluster into the four days from 2026-08-13 to 08-16 — a textbook case of a community starting at once.

---

## ① Native APK + Shizuku: the only one that truly operates the phone

`woaiys3/deepseek-harness-android-app`, 166 stars, the most active of the four.

Its significance is not "DSH packed into an APK" but **three system-privilege channels with graceful degradation**:

1. **Root (su)** — taken when available, highest privilege
2. **Shizuku** — the primary path without root. Shizuku obtains system shell privileges via ADB authorization, letting an ordinary app call APIs that normally require a system signature. From there the AI can **install apps, tap the screen, change system settings, take screenshots and simulate input**
3. **Accessibility service (added in v1.7.0)** — with "Screen Assistant" enabled in system settings, **neither root nor Shizuku is required**; the AI can read the screen, tap, type, scroll, and interpret accessibility screenshots

The channels complement each other, and **granting none of them still works** — degrading to file read/write, preview and editing (needing only "all files access"). When unauthorized, the AI does not repeatedly attempt system operations; it prompts you to authorize when needed.

Other engineering details:
- Package `com.deepseek.harness`, foreground service keeps it alive under lock screen, notification on task completion
- `dshroot` externalized to `/sdcard/DeepSeekHarness`, so **reinstalling does not wipe the AI's runtime changes**
- Full DSH kernel, plugin ecosystem and RPC API retained; the front end is DSH's native UI
- Touch tuning, soft-keyboard handling, and a first-launch permission walkthrough covering nine permissions

**Why it matters**: the phone becomes the agent's **object of operation**, not just its host. You can have it tap a button in some app, change a setting, install something.

**The cost**: Shizuku needs ADB re-activation after every reboot unless you have root; accessibility permissions get "optimized" away by many vendor ROMs; and the broader the permission surface, the larger the blast radius when something goes wrong.

---

## ② Termux patch layer: 100KB, lightest, most rigorous

`Vengisk/deepseek-harness-termux`, 51 stars, **just 100KB** — because it is not an app, it is a patch set.

The problem is specific: official `@deepseek-ai/dsh` is built for glibc Linux distributions and depends on native modules that fail to compile or misbehave on Android's Bionic libc. Most ports **disable the offending plugins**; this repo **patches the source so every feature works**.

The patches are generated automatically with `diff -u` against pristine upstream tarballs (`@deepseek-ai/dsh` 0.1.0-rc.6), which the author notes makes them "exact and reproducible."

Its feature-status table is admirably honest and worth copying:

| Component | Status | Notes |
|---|---|---|
| `dsh web` | ✅ | Server on `http://127.0.0.1:3080` |
| `dsh headless` | ✅ | Single-session headless mode |
| `dsh plugin` | ✅ | Plugin management |
| HMR | ✅ | Launched with `--expose-internals` |
| Subprocess | ✅ | `node-pty` compiled against the Termux bionic sysroot |
| **Bash sandbox** | ⚠️ **Limited** | `node-pty` works; **`bubblewrap` is blocked at runtime by Android sepolicy**, degrading safely to `SandboxUnavailableError` |
| Permission system | ✅ | Restored with `node-pty` |
| Session persistence | ✅ Fixed | `link(2)` → `rename(2)` fallback for Android sepolicy |
| Bash terminal (PTY) | ✅ Fixed | Default shell resolved to `/usr/bin/bash` on Termux |
| Mobile UI | ✅ Auto | Narrow screens (<1024px): sidebar hidden, directory as drawer, full-width conversation |

**Note that ⚠️ row**: the `bubblewrap` sandbox is blocked by Android's security policy (sepolicy), not merely unimplemented. Which means **running DSH on a phone lacks the sandbox isolation layer** — the bash commands an AI executes have no extra isolation protecting them. This holds for every Termux-based approach.

**Good for**: people already using Termux, comfortable with a command line, wanting the lightest and most controllable option.

**Not good for**: anyone who has never heard of Termux. The barrier here is Termux itself, not DSH.

---

## ③ Standalone APK with embedded Node.js: the easy one

`thness/dsh-mobile`, 18 stars, Kotlin, **41MB APK**.

The pitch is blunt: **one APK that puts the full DeepSeek Harness in your pocket.** Embedded Node.js runtime plus the official Web UI, install and go, no extra dependencies.

Explicit hardware requirements — the only one of the four to state them this clearly:
- Android 8.0+ (API 26)
- **4GB+ RAM recommended**
- **500MB+ storage**
- **~30 seconds** for first-launch engine initialization

Features: foreground service persistence, external-storage workspace, optional Shizuku integration, OTA updates.

**Versus ①**: ① is "AI plus the ability to operate the phone"; ③ is "AI installed into the phone." ③ does wire up Shizuku, but its center of gravity is clearly getting DSH running rather than having the AI drive the system.

**Good for**: trying it fast without fighting permissions. Download 41MB, install, wait 30 seconds.

---

## ④ Capacitor + PRoot Ubuntu: heaviest, most complete

`dphmoblie/deepseek-harness-android`, 5 stars, TypeScript.

The most aggressive approach: **run a full Ubuntu 24.04 ARM64 userspace inside the phone**, containing Node.js 24.19.0 and `@deepseek-ai/dsh` 0.1.0-rc.6, started via PRoot, wrapped in a Capacitor app.

CI builds the mobile Harness conversation front end, injects it into an Ubuntu 24.04 ARM64 image, then embeds a verified `rootfs.bundle` and `runtime-manifest.json` into the APK. The official APK therefore **installs offline** with no rootfs download.

One technical note punctures a common misconception:

> The Android WebView does not run Node.js. The installed Ubuntu environment must contain Node.js in the exact supported range `^22.19.0 || >=24.0.0`.

Build requirements are also the steepest: Node.js `^22.19.0 || >=24.0.0`, JDK 23.0.1, Android SDK 35 with a compatible NDK, and a pinned ARM64 PRoot runner/loader from a specific commit of the Operit2 Android runtime toolchain.

**Good for**: wanting a complete Linux environment, running more than just DSH.

**The cost**: the heaviest route. PRoot intercepts syscalls in userspace, with a noticeable performance penalty.

---

## So which one?

Pick by what you want, not by star count:

| You want | Pick |
|---|---|
| The AI to actually operate my phone (tap, install, change settings) | **① woaiys3** — the only option |
| Lightest and most controllable; I know Termux | **② Vengisk** |
| Fastest trial, no fiddling | **③ thness** |
| A full Linux, not just DSH | **④ dphmoblie** |

**One shared premise worth stating**: all four run the DSH harness itself; model inference still goes through an API. The phone here is the agent's **execution environment**, not an inference device. Local inference on a phone is a separate problem.

---

## Where are the limits of a phone-side agent?

Time for cold water. Which tasks actually belong on a phone?

**Suited**:
- Anything needing phone-only capability — reading notifications, driving a mobile-only app, using the phone's logged-in sessions
- Long waits — foreground persistence plus notification, pushed to you when done
- Being out with only a phone

**Not suited**:
- Heavy file IO and compilation — phone storage IO and thermals cannot keep up
- Anything needing sandbox isolation — as noted, `bubblewrap` is blocked by sepolicy on Android
- Sustained high load — thermal throttling, plus battery drain

**The realistic use** is probably the phone as the agent's remote control and provider of specific capabilities, not as a primary workstation.

---

## Gaps: I have no Android device, and tested none of the four

Stated up front — this post is **a route map, not a hands-on report**.

Everything comes from the four repos' READMEs, GitHub API metadata and their build documentation. All of the following is unverified:

1. **Whether the four APKs actually install and run** — especially ④, whose build requirements are strict enough to make release-APK compatibility across devices questionable
2. **The real permission ceiling of root-free Shizuku** — the README claims installing apps, tapping the screen and changing system settings; how far that goes in practice, and which vendor ROMs block what, is untested
3. **Performance and battery** — no numbers on relative speed or drain per task
4. **An emulator cannot verify the parts that matter** — Shizuku and foreground persistence are precisely what emulators measure badly, so I did not use one to pad this out

Testing this needs a real device. If you have run any of these on hardware, I would like to hear how it actually went.

---

## In one line

Three of the four routes answer "how do I get DSH onto a phone"; one answers "how do I let an AI use this phone." **If you want the latter, there is exactly one choice; if the former, pick by how much fiddling you tolerate.**

The shared ceiling: Android's sepolicy blocks the `bubblewrap` sandbox — running an agent on a phone currently has no isolation layer.

> 📌 Native APK + Shizuku: https://github.com/woaiys3/deepseek-harness-android-app
> Termux patch layer: https://github.com/Vengisk/deepseek-harness-termux
> Embedded Node.js APK: https://github.com/thness/dsh-mobile
> Capacitor + PRoot Ubuntu: https://github.com/dphmoblie/deepseek-harness-android
> DSH upstream: https://github.com/deepseek-ai/deepseek-harness

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
