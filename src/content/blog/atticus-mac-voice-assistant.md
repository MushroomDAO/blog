---
title: "Atticus Mac：本地语音识别、快捷动作与模型协作的桌面助手"
titleEn: "Atticus Mac: Voice, Shortcuts and Desktop Agents"
description: "Atticus 是 MIT 开源的 macOS 语音助手，结合 Apple 设备端识别、快速指令、学习式快捷方式与模型推理。本文核对源码、系统要求、Claude 和自定义服务器路线，解释免费软件与付费模型、本地音频与云端上下文的区别，并检查安装行为、会议归档、权限确认及本地编译结果，给出循序渐进的桌面使用验收建议。"
descriptionEn: "Review Atticus for Mac: on-device speech, learned shortcuts, Claude and custom-server routes, installation behavior, privacy boundaries and local build checks."
wechatTitle: "Atticus：按住快捷键，让Mac干活"
wechatDigest: "拆解语音、快捷动作与模型分工，并核对免费、隐私和安装边界。"
pubDate: "2026-10-17"
updatedDate: "2026-10-17"
category: "Tech-News"
tags: ["Atticus", "macOS", "语音助手", "Claude Code", "开源"]
heroImage: "../../assets/images/atticus-mac-voice-assistant-banner.jpg"
---

Atticus 是一个住在 Mac 菜单栏里的语音助手：按住快捷键说话，松开后让它开应用、排窗口、找文件，或把复杂任务交给 Agent。它把本机语音识别、确定性快捷动作和模型推理接在一起，重点是减少日常操作的来回切换。

项目是 `SaarthurR/atticus-mac`，MIT 开源，当前要求 macOS 26+。本文固定源码 `0f4d8d79e3db4e9447a80deab847369423b295ad`，核对日期 2026-10-17。软件免费，但默认使用已有付费 Claude Pro/Max 计划，经 Claude Code 执行；当前源码也介绍 Devin CLI 和自定义模型服务器路线。不能把“没有 API Key”翻译成“模型使用永久免费”。

## 它和给聊天模型加个麦克风，有什么区别？

Atticus 先把输入分流。开应用、调整窗口、搜索和音乐等支持的简单指令，可以走确定性逻辑；复杂请求交给模型。已成功执行过的动作还可成为学习到的快捷方式，下次匹配后重放。这不是每轮都重新让大模型规划。

仓库介绍打开应用约 0.08 秒，以及一个多应用指令从 5.5 秒降至 0.4 秒，均为作者的具体示例。本文未复现延迟，也不把缓存命中速度写成完整语音到任务完成的统一响应时间。重放是否正确还取决于语义匹配、目标应用与当前状态。

入口默认是 Control+Option+Space，可配置按住说或再次按下提交。原生识别给出最终转写后，再放行 AI 工具和学到的快捷动作；部分内置即时命令在启用特定设置后可以边说边执行。它还提供 Esc 取消、语音播放打断和长录音复核，交互细节比单纯“语音转文字再发请求”更完整。

![小M把语音请求分到即时动作、学到的快捷方式和模型处理三条路径](../../assets/images/atticus-mac-voice-assistant-fig-01.png)

## 本地与云端，数据分别去哪里？

| 环节 | 资料描述 | 需要理解的边界 |
| --- | --- | --- |
| 语音识别 | Apple 设备端识别，原始语音留本机 | 不等于之后所有文字推理也留本机 |
| 简单指令与快捷方式 | 可在本机执行，跳过模型 | 要验收命中与实际动作 |
| Claude 默认路线 | Claude Code 使用现有付费计划 | 请求文字及任务所需上下文可能交给云端模型 |
| 自定义服务器 | 文档支持 Ollama、LM Studio、DeepSeek 等接法 | 本地还是远程由端点和实际工具决定 |
| 会议归档 | 本地保存转写、摘要等；不保存音频 | 默认 AI 会后摘要会把转写交给模型，可关闭 |

另外，README 写明每日匿名使用计数，可在设置里关闭；“帮助改进”故障反馈另行选择，默认未同意。不要把“音频不出 Mac”泛化为绝对没有网络通信。对于会议或客户资料，先确认转写保存、摘要模型和反馈开关。

当前设置支持模型选择、较难任务升级，以及后台 Agent。能用自定义服务不等于任意小模型都具备可靠的桌面操作能力；还需验证工具协议、上下文、模型行为及服务端兼容。

![小M区分本机语音、云端推理和可选本地模型的数据路径](../../assets/images/atticus-mac-voice-assistant-fig-02.png)

## 真正控制 Mac，靠的是哪些部件？

Swift 负责快捷键、语音、悬浮层与原生交互；Python 部分负责快速指令、提示词和工具逻辑；HTML/JavaScript 提供部分界面。辅助功能接口支持点击、滚动、输入、菜单与窗口操作，录屏权限则影响读取屏幕和预览等能力。

作者称 Safe mode 默认开启，通过 Claude Code sandbox 约束写入，并在删除、发送、购买、修改文件等风险操作前要求确认，另有命令拦截与 ask log。这些是项目设计，不是本文做过渗透或完整权限验证的安全认证。接自定义模型和其他 CLI 时，尤其要重新检查同样的批准流程是否有效。

本地“记住我”主要包括规则、个人事实、纠错与快捷动作等状态，能在设置里查看和调整。把一次纠错保存成规则很实用，但规则越积越多，也需要删除过时内容，避免把旧偏好套到新任务。

## 怎样安装和验收更稳妥？

先确认 macOS 26+、Apple Command Line Tools，以及要使用的 Claude Code、Devin 或自定义服务器。对希望审阅安装过程的用户，建议先拉仓库、读 `install.sh` 和 `build.sh`，再决定执行；不要只因为宣传是“一行命令”就忽略安装行为。

```bash
git clone https://github.com/SaarthurR/atticus-mac.git
cd atticus-mac
# 阅读 install.sh、build.sh 后，再按官方指引安装。
```

`build.sh` 不只是编译：还会写入用户 Applications、处理本地签名、配置登录启动并启动应用。本文为审阅而只编译到临时目录，没有运行安装脚本。第一次实际使用先试开计算器、移动测试窗口，再测搜索临时文件；复杂任务逐步增加权限和批准点。

验收指标应分开记录：按键到最终转写、最终转写到首个反馈、任务完成耗时、快捷方式命中、错误动作、取消是否生效。会议场景再看中文、口音、噪声与长会话状态，不能只拿作者的应用启动时间下结论。

本地验证：固定源码在 M4/macOS 26 上完成原生编译与 `--selftest`，得到 `native selftest ok`；限定的配置、个人资料、重放和遥测单元测试共 26 项通过。首次临时输出名导致 Swift 模块名不匹配，指定 `-module-name Atticus` 后解决，未修改源码。宽泛上游测试集合包含额外原生交互用例，我们中止该轮，不把它算作全套通过。没有进行真实语音、付费模型调用或日常桌面任务验收。

我的判断：它的价值在“哪些请求根本不需要模型”和原生操作入口；适合有 Mac、已有模型使用路径、愿意逐项验收的用户。它和通用电脑操作研究栈的区别，可对照：https://blog.mushroom.cv/blog/opengcua-generalist-computer-use-stack/

![小M从临时编译、简单动作逐步走到需要确认的复杂任务](../../assets/images/atticus-mac-voice-assistant-fig-03.png)

## 常见问题

### 不买 Claude 订阅可以用吗？

当前文档还提供 Devin CLI 和经 Claude Code 连接自定义服务器的路线。各路线的账户、模型和成本条件不同，不能保证全部免费。

### 这是纯离线助手吗？

设备端语音识别与本地快捷动作可以本地完成。默认 Claude 路线及 AI 会议摘要涉及模型服务；完整离线能力需单独配置和验证。

### 能在旧版 macOS 上安装吗？

当前项目要求 macOS 26+，原因包括新的 Apple 设备端语音能力，不能推断 macOS 14/15 同样支持。

## 一手资料

- 仓库：https://github.com/SaarthurR/atticus-mac
- 固定版本：https://github.com/SaarthurR/atticus-mac/tree/0f4d8d79e3db4e9447a80deab847369423b295ad
- 官网：https://saarthurr.github.io/atticus-mac/
- 安装行为：https://github.com/SaarthurR/atticus-mac/blob/0f4d8d79e3db4e9447a80deab847369423b295ad/build.sh

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Atticus is a Mac menu-bar voice assistant that opens apps, arranges windows, searches files and delegates harder work to an agent. It combines on-device speech recognition, deterministic shortcuts and model reasoning to reduce everyday interaction overhead.

The project is SaarthurR/atticus-mac, under MIT, currently requiring macOS 26+. This October 17, 2026 review pins `0f4d8d79e3db4e9447a80deab847369423b295ad`. The app is free; its default Claude Code route uses an existing paid Claude Pro/Max plan. Current documentation also describes Devin CLI and custom-server routes. No API key does not mean unlimited free inference.

## What goes beyond adding a microphone to chat?

Supported simple commands can bypass the model. Successful actions may become learned shortcuts that replay after a later match. Complex requests still use a model. These are different execution paths with different latency and failure modes.

The author’s examples include a 0.08-second app launch and one multi-app action falling from 5.5 to 0.4 seconds. We did not reproduce those figures, and they are not a uniform voice-to-task response time.

Control+Option+Space starts the interaction, with hold or toggle behavior. Final native transcripts gate AI tools and learned shortcuts; selected built-in commands can act during speech when explicitly enabled. Cancellation, spoken-output interruption and long-recording review make this more than a transcription box.

![XiaoM routes speech to instant actions, learned shortcuts or model reasoning](../../assets/images/atticus-mac-voice-assistant-fig-01.png)

## Which data stays local?

| Stage | Documented behavior | Boundary |
| --- | --- | --- |
| Speech recognition | Apple on-device recognition | Local audio does not make later text reasoning local |
| Instant actions and shortcuts | Can skip the model | Matching and resulting actions need validation |
| Default Claude route | Existing plan through Claude Code | Task text and necessary context may reach a cloud model |
| Custom server | Ollama, LM Studio, DeepSeek and other documented configurations | Locality depends on the endpoint and tools |
| Meeting archive | Transcripts and related records stored locally; no saved audio | Default AI recap sends transcript to the model; it can be disabled |

The README also documents a daily anonymous usage count, which can be disabled, and a separate opt-in failure-feedback feature. “Audio stays on the Mac” should not be generalized into “no network traffic.” Review recording, summary and feedback settings before handling sensitive meetings.

Model selection and background-agent features do not establish that every small local model can operate the desktop reliably. Validate endpoint compatibility, context and tool behavior.

![XiaoM distinguishes local speech, cloud reasoning and optional local inference](../../assets/images/atticus-mac-voice-assistant-fig-02.png)

## How does it operate the Mac?

Swift handles hotkeys, speech and native interaction; Python handles command routing, prompts and tools; HTML/JavaScript provide portions of the interface. Accessibility enables native application operations, while Screen Recording affects screen reading and previews.

The author describes Safe mode as enabled by default, using Claude Code’s sandbox and approval prompts for consequential actions, alongside blocked commands and an ask log. These are design claims, not a security certification from our review. Alternate CLIs and custom model configurations need their own approval-flow checks.

Memory includes rules, profile facts, corrections and learned actions. Editable memory is useful, but stale rules still need maintenance.

## How should installation and acceptance work?

Confirm macOS 26+, command-line tools and your chosen inference route. Inspect install.sh and build.sh before installation:

```bash
git clone https://github.com/SaarthurR/atticus-mac.git
cd atticus-mac
# Review install.sh and build.sh, then follow upstream installation.
```

The build script also installs into user Applications, handles local signing, configures login startup and starts the app. Our review compiled into a temporary directory instead of running that installer.

Start real acceptance with a disposable window and temporary files. Measure transcript finalization, first feedback, completed-task time, shortcut correctness, wrong actions and cancellation separately. Meeting acceptance should include language, accent, noise and long-session behavior.

Local verification compiled the unchanged source on M4/macOS 26 and passed the native selftest. An initial temporary output name produced a Swift module-name mismatch; adding `-module-name Atticus` resolved it. All 26 focused configuration/profile/replay/telemetry tests passed. We interrupted the broad upstream suite, which includes additional native interaction cases, and do not claim a full-suite pass. We tested no real speech session, paid model request or everyday desktop task.

Our assessment: the useful distinction is deciding which requests need no model, combined with a native interaction surface. Compare the research-stack approach here: https://blog.mushroom.cv/blog/opengcua-generalist-computer-use-stack/

![XiaoM moves from isolated compilation to simple actions and confirmed tasks](../../assets/images/atticus-mac-voice-assistant-fig-03.png)

## FAQ

### Must I buy Claude?

The current docs also describe Devin and custom-server routes through Claude Code. Each has its own account, model and cost requirements.

### Is this fully offline?

Native speech and simple actions can be local. Default Claude reasoning and AI meeting recaps use a model service. Full offline operation needs separate configuration and validation.

### Does it support older macOS versions?

The current requirement is macOS 26+, including Apple’s newer on-device speech functionality.

## Primary sources

- Code: https://github.com/SaarthurR/atticus-mac
- Pinned source: https://github.com/SaarthurR/atticus-mac/tree/0f4d8d79e3db4e9447a80deab847369423b295ad
- Website: https://saarthurr.github.io/atticus-mac/
- Installation behavior: https://github.com/SaarthurR/atticus-mac/blob/0f4d8d79e3db4e9447a80deab847369423b295ad/build.sh

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
