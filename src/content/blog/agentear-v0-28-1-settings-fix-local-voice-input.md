---
title: "AgentEar v0.28.1 发布：只修设置窗口重叠，但免费本地语音输入的功能值得重新梳理"
titleEn: "AgentEar v0.28.1: A Settings Layout Fix, and a Fresh Look at the Free Local Voice Input"
description: "AgentEar v0.28.1（2026-10-27）只重排设置窗口下半区：窗口加宽到 620 点，标题与下拉框不再互相压住。本文梳理这款 Apache-2.0 免费、全本地的 macOS 语音输入的功能：右 Command 录音、SenseVoice 转写、Markdown 知识库、语音指令与对话，以及版本边界。"
descriptionEn: "AgentEar v0.28.1 (2026-10-27) only rearranges the lower half of the Settings window, widening it to 620 points so labels and popups stop overlapping. A walkthrough of this free, Apache-2.0, fully local macOS voice input: right-Command dictation, SenseVoice, Markdown knowledge base, voice commands and conversation, plus the limits."
wechatTitle: "AgentEar v0.28.1：免费本地语音输入"
wechatDigest: "v0.28.1只修设置窗口重叠；梳理这款本地语音输入的功能、免费边界与限制。"
pubDate: "2026-10-28"
updatedDate: "2026-10-28"
category: "Tech-News"
tags: ["AgentEar", "语音输入", "本地ASR", "SenseVoice", "macOS", "Apache-2.0", "开源"]
heroImage: "../../assets/images/agentear-v0-28-1-settings-fix-local-voice-input-banner.jpg"
lastPublishedAt: "2026-10-28T10:49:07Z"
---

> 📌 发布页：https://github.com/iDoris-ai/AgentEar/releases/tag/v0.28.1
> 📌 项目仓库：https://github.com/iDoris-ai/AgentEar

**一句话结论：v0.28.1 不改录音、转写、对话和语言设置，只把设置窗口的下半区重新排版，修掉英文标题压在下拉框上的问题。AgentEar 本身是 Apache-2.0 的全本地语音输入，免费，但仅支持 Apple Silicon Mac。**

之前我写过一篇 AgentEar 的预览版介绍（agentear-local-voice-input-preview），这篇不重复安装细节，只讲两件事：这个版本改了什么，以及这款语音输入现在有哪些功能。

## v0.28.1 到底改了什么？

问题出在 v0.28.0：英文 “Speech recognition” 和 “Keep Raw Audio” 的标题横跨整行，下拉框却从同一行中段开始画，文字压在 “SenseVoice (built-in, default)” 和 “30 days” 上；下面四个按钮各占一整行。

v0.28.1 的处理：

- 窗口宽度改为 **620 点**；
- 两个标题同排、各占一半，下拉框在下一行、各占半行；
- 四个按钮排成两行两列：编辑术语表 + 打开语音指令，打开数据目录 + 查看日志；
- Qwen3 下载行、SenseVoice 行、Agent24 行仍是整行，界面语言和识别语言两行没动。

**升级影响**：已保存的配置不变，下次打开设置就是新排法。

**验证范围要看清**：作者用调试构建对着空的临时数据目录打开了设置窗口，确认两列存在、英文按钮放得下；另有一个单元测试 `settings_columns_are_half_width_and_do_not_overlap` 钉住两列等宽且不交叉。但 **发布包里的签名 `.app` 没有点过**（打开它会改写开机启动项），中文和泰文界面也没有重新截图，作者的理由是它们本来就比重叠的英文标题短。

## 上一版 v0.28.0 给了什么？

v0.28.1 是它的补丁，所以顺带说一下：v0.28.0 在设置窗口顶部加了“界面语言”和“识别语言”两行。新安装默认英文界面；已保存界面语言的配置不会被改写。在界面语言里选 **ไทย** 会同时切换界面，并触发约 574 MB 的泰语识别模型下载，**下载和校验完成前，保存的识别语言仍是 Auto**，避免录音时调用还不存在的引擎。

## 这款免费语音输入有哪些功能？

AgentEar 的两条底线是**成本和隐私**：录音和转写都在本机完成，不经过第三方服务器。

1. **按键即录即转写**：按一下右 Command 开始，再按一下停止，文字进剪贴板；没有辅助功能权限时降级为 `Ctrl+Shift+R`。
2. **速度**：README 自报，一段 7.4 秒录音全程 7.8 秒（转写 0.26 秒），空闲常驻内存 13 MB。这是作者自测，我没有复现。
3. **默认引擎 SenseVoiceSmall**：中、英、粤、日、韩自动判断；泰语走另一套 whisper.cpp 引擎，按需下载。
4. **原始音频先落盘**，转写之前就保存，丢了无法重算。
5. **Markdown 知识库**：说“这是一个 idea”“记一个任务”，就生成带 YAML 头的 Markdown，Obsidian、Logseq 都能直接读；`agentear --search` 支持中文子串全文检索。
6. **可选理解层**：接本地 LLM 做技术术语纠错和七类标签识别，默认关闭，需自备约 7.8 GB 模型，常驻约 7.3 GB 内存。
7. **语音指令**：本地快路径加 LLM 兜底；动作只有内置、打开网址、HTTP POST 三种，**故意不执行 shell**，因为听错一个字就不该变成在你机器上跑命令。写 Notion、发邮件这类向外动作执行前一定二次确认。
8. **实时对话**：双击右 Command（500ms 内两下）进入对话模式，单击是输入法模式；中、英、泰三语链路已跑通，但**不是全双工**，自动打断（AEC/VAD）还没做。

## 免费有哪些前提？

许可证是 Apache-2.0，Release 没有标价。真正的门槛是：

- **仅 Apple Silicon**，Intel 不支持（上游 FunASR 运行时在 macOS 只发 arm64）。
- 本版压缩包 **约 265 MB**（`AgentEar-0.28.1-macos-arm64.zip`），已内置 ASR 运行时；对话模式的 LLM 和 TTS 模型另需下载约 3.5 GB。
- 之前版本的 README 写明 app 用本地自签证书、未公证，首次打开可能被 Gatekeeper 拦下，要到“隐私与安全性”里点“仍要打开”；本版发布页没有提公证状态，我没有核验。
- 泰语夹英文技术词没有可信数据，会把 `review pull request` 音译成泰文。

## 要不要升级？

如果你用英文界面、被设置窗口的重叠字困扰，升级；如果你只用快捷键录音转写，这一版对你没有功能差别。仓库只有 1 个 star，属于个人早期项目，选型时把它当“能用的本地小工具”，别当成熟产品。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**Bottom line: v0.28.1 changes nothing about recording, transcription, conversation or language settings. It only re-lays out the lower half of the Settings window to fix English labels drawn on top of popups. AgentEar itself is Apache-2.0, fully local and free, but Apple Silicon only.**

I covered AgentEar's preview earlier (agentear-local-voice-input-preview), so this post skips installation details and covers two things: what this release changes, and what the tool can do today.

## What exactly changed in v0.28.1?

In v0.28.0 the English labels “Speech recognition” and “Keep Raw Audio” spanned the full row while the popups started midway, so the text sat on top of “SenseVoice (built-in, default)” and “30 days”. The four buttons below each took a full row.

Now:

- the window is **620 points** wide;
- the two captions share one row, each in its own half, with the popups on the next row at half width;
- the four buttons form two rows of two: Edit Term List + Open Voice Commands, Open Data Folder + View Log;
- the Qwen3 download rows, the SenseVoice row and the Agent24 row stay full width; the interface-language and recognition-language rows are unchanged.

**Upgrade impact**: saved config is untouched; the next time Settings opens it uses the new layout.

**Know the verification scope**: the author opened a debug build against an empty temporary data directory and confirmed the two columns and that English button titles fit, and a unit test (`settings_columns_are_half_width_and_do_not_overlap`) pins equal, non-crossing columns. But **the signed `.app` in the release was not clicked** (opening it would rewrite the login item), and Chinese and Thai labels were not re-shot, on the grounds that they were already shorter than the English labels that overlapped.

## What did v0.28.0 add?

Since v0.28.1 patches it: v0.28.0 added Interface Language and Recognition Language rows at the top of Settings. New installs open in English; configs that already saved an interface language keep it. Choosing **ไทย** switches the interface and starts the roughly 574 MB Thai model download, and **the saved recognition language stays Auto until the download and check finish**, so a recording never calls an engine that isn't there yet.

## What can this free voice input do?

AgentEar's two hard constraints are cost and privacy: recording and transcription stay on the machine.

1. **Hotkey dictation**: press right Command to start, again to stop, text goes to the clipboard; falls back to `Ctrl+Shift+R` without Accessibility permission.
2. **Speed**: self-reported in the README, a 7.4 s clip takes 7.8 s end to end (0.26 s transcription) with 13 MB idle memory. I did not reproduce this.
3. **SenseVoiceSmall by default**: Chinese, English, Cantonese, Japanese, Korean with auto-detection; Thai uses a separate whisper.cpp engine downloaded on demand.
4. **Raw audio is saved first**, before transcription, since it cannot be regenerated.
5. **Markdown knowledge base**: say “this is an idea” or “note a task” and it writes a Markdown file with YAML front matter that Obsidian or Logseq can read; `agentear --search` does Chinese substring full-text search.
6. **Optional understanding layer**: a local LLM corrects technical terms and tags utterances into seven types. Off by default; needs about 7.8 GB of model and about 7.3 GB resident memory.
7. **Voice commands**: a local fast path with an LLM fallback. Actions are limited to built-in, open-URL and HTTP POST, **deliberately no shell**, because one misheard word must not become a command on your machine. Outbound actions such as writing to Notion or sending email always ask for confirmation first.
8. **Live conversation**: double-tap right Command (two presses within 500 ms) for conversation mode; a single tap is dictation mode. Chinese, English and Thai work end to end, but it is **not full duplex** and automatic barge-in (AEC/VAD) is not done.

## What is the catch with "free"?

The license is Apache-2.0 and the release has no price. The real requirements:

- **Apple Silicon only**; Intel is unsupported because the upstream FunASR runtime ships only arm64 on macOS.
- The release zip is **about 265 MB** (`AgentEar-0.28.1-macos-arm64.zip`) and bundles the ASR runtime; conversation mode needs about 3.5 GB of LLM and TTS models downloaded separately.
- Earlier README text says the app uses a local self-signed certificate and is not notarized, so Gatekeeper may block the first launch (use “Open Anyway”); this release page does not mention notarization and I did not verify it.
- Thai mixed with English technical terms has no reliable data; `review pull request` was transliterated into Thai script.

## Should you upgrade?

If you use the English UI and the overlapping text bothered you, yes. If you only use the hotkey to dictate, this release makes no functional difference. The repo has 1 star and is an early personal project: treat it as a handy local tool, not a mature product.

Sources: https://github.com/iDoris-ai/AgentEar/releases/tag/v0.28.1 · https://github.com/iDoris-ai/AgentEar

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
