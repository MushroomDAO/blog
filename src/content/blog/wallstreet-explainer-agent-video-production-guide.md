---
title: "wallstreet-explainer：把证据与审片写进AI视频流程"
titleEn: "wallstreet-explainer: An Agent Video Production Guide"
description: "wallstreet-explainer 是面向 Claude Code 与 Codex 的财经科技解说视频技能，连接文案、新闻证据、配音时间线、浏览器渲染与 FFmpeg。本文核对 MIT 授权、八站审片流程及联网依赖，并检查自带起始工程，说明本地出片验证与完整自动生产之间的边界，给创作者从短片开始的可复核试用路线。"
descriptionEn: "Explore wallstreet-explainer: agent skills for scripts, news evidence, narration and browser video rendering, with local checks and clear production boundaries."
wechatTitle: "wallstreet-explainer：证据与审片"
wechatDigest: "把文案、新闻证据和渲染接成流程，先分清自动化与审片责任。"
pubDate: "2026-11-27"
updatedDate: "2026-11-27"
lastPublishedAt: "2026-11-27T07:34:51.108247+00:00"
category: "Tech-News"
tags: ["AI视频", "Agent Skills", "视频制作", "开源工具", "事实核查"]
heroImage: "../../assets/images/wallstreet-explainer-agent-video-production-guide-banner.jpg"
---

wallstreet-explainer 把文案、证据素材、配音时间线和动效剪辑接成一套 Agent 制作流程。它值得关注的不是“输入题目就保证成片”，而是把解说视频里常被省略的找证据、逐镜设计和审片步骤写成了可复用工具。

官方项目是 HeyChengC/wallstreet-explainer，代码和文档采用 MIT，样片里的第三方新闻截图、人物、商标和视频另算。我们核对了固定版本源码，并检查自带起始工程及独立的短片渲染夹具；这不是整条 AI 自动生产链路的实测。

仓库：https://github.com/HeyChengC/wallstreet-explainer
制作流程：https://github.com/HeyChengC/wallstreet-explainer/blob/main/SKILL.md
授权说明：https://github.com/HeyChengC/wallstreet-explainer/blob/main/LICENSE

## 给一个题目，它实际调动了什么？

它是一套给 Claude Code、Codex 等编程 Agent 阅读的 skill，加上 Python、JavaScript 和浏览器制作工具，不是新训练的视频生成模型。Agent 负责组织选题、文案和镜头代码，工具负责找片、截网页、对齐语音、画逐帧画面和混音。

风格目标很明确：用真实新闻与当事人画面承担证据，让大数字、柱状图和因果链解释关系。深蓝织物底、金色数字和 2.5D 运镜只是视觉词汇，每镜必须先回答“观众多懂了什么”，而不是先决定塞哪个转场。

仓库区分横屏 16:9 与竖屏 9:16，也区分提供口播视频和无人出镜两种模式。有人物视频时，图形围绕主持人组织；没有口播时，可以先用临时 TTS 做时间线。样片使用数字人，不代表这个仓库自己训练或包含了一个数字人模型。

![小M把选题拆成文案、证据、镜头表和渲染工具，Agent串联各个环节](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-01.png)

## “自动做完”和官方流程，有什么区别？

README 用“给它一个选题”概括入口，但 SKILL.md 明确列出 0 到 7 共八站：选题、文案、导演表、素材、配音时间线、开头、720p 全片、最终成片。其原文要求每站给用户看，不要一口气交成片。

这里的人工判断有具体对象：文案是否准确，导演表能否讲通，关键素材是否对题，三个不同钩子的粗剪选哪个，整片画面和配音是否合适。本文介绍这套设计，并不把这些上游审片要求套到我们的博客发布流程里。

它的产品价值更像“可重复执行的制作规程”：Agent 不必从零猜软件怎么接，创作者也不必只凭一句“帮我剪好”验收。自动化减少搬运和重复劳动，选题判断、事实核查、叙事和最终质量仍需要负责的人。

## 新闻截图，为什么不等于事实核查？

snap_news.mjs 通过 Playwright 打开网页、滚到指定段落、等字体加载，再记录标题、命中短语的位置并截图。命中坐标可用于后续画荧光笔，让观众知道一句数字从哪里来。

这能提升证据的可追溯性，却没有自动证明原文正确，也没有证明文案没有断章取义。截图可能来自过时报道，金额可能混淆累计与单年，图片也可能只是在装饰。制作时仍应保存来源、发布时间、原始口径与文案之间的对应关系。

源码会移除部分广告与浮层，文档要求遇到验证码拦截时不要硬截，可以用已核实文字自行排版，并避免冒用网站标志。使用者应实际检查截图，而不是把网页成功打开当成证据已经合格。

![小M核对来源、日期和数字口径，再把原文片段与解说句子逐一连接](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-02.png)

## 哪些步骤能本地跑，哪些仍要联网？

| 环节 | 源码与文档显示的依赖 |
| --- | --- |
| 选题、写稿、写镜头代码 | 由外部编程 Agent 及所用模型完成；软件 MIT 不代表模型额度免费 |
| 搜索和下载素材 | 网页、视频网站与 yt-dlp 等工具，需要网络和可访问来源 |
| 新闻截图 | Playwright 浏览器访问目标网页，输出截图和坐标 |
| 临时配音 | temp_voice.py 使用 edge-tts，属于联网语音服务，不是仓库内的离线 TTS 权重 |
| 逐字对齐 | 可选 faster-whisper，本地执行但需准备模型；源码有 CUDA 与 CPU 回退路径 |
| 抠像 | 可选 ONNX 模型与运行时，需先准备模型文件 |
| 画面与混音 | 浏览器逐帧截图，FFmpeg 编码和混音，可在素材准备好后本地执行 |

安装还需要 Node.js、Python、FFmpeg／ffprobe、Playwright Chromium，以及自行准备的字体。README 列出的字体包括 MiSans、阿里妈妈数黑体、Bebas Neue、Montserrat 和 Noto Sans SC；文件名要与 CSS 对上。

因此，“本地渲染”可以成立，“整条链路完全离线、没有服务依赖”不能直接成立。正式配音能否换成自己的音频，应结合逐字对齐与时间线重新验收；不要只替换音轨而保留旧时刻。

## 代码怎样把声音和镜头接起来？

文案按句保存稳定 id，镜头用类似 @b02:关键词 的标记定位，而不是到处写死秒数。没有配音时，timeline_stub.mjs 根据字符类别估算时长，并显式标记 stub；有正式音频后再生成真实对齐结果。

这解决的是改配音后画面时刻到处漂移的问题，但估计时间线不是语音对齐实测。尤其数字、英文、停顿和语气变化大时，最终仍应以实际音频为准。

render.mjs 要求页面暴露 ready Promise 与 seek(t)。渲染器按时间调用 seek，浏览器截图后交给 FFmpeg 编码。它仍是浏览器渲染路线，不是原生 GPU 游戏引擎，也不是扩散模型逐帧生成。

## 我们这次验证到了哪一步？

Mycelium Protocol 在固定提交 b79bc0573455cb5fe335e78f653012e658fa9758 上检查源码，使用 Node.js 26.10.0 与 FFmpeg 9.0.2，对仓库自带横屏起始工程做小范围验证，具体结果以本段及随文研究记录为准。

实际结果分三部分：

- 时间线：直接调用原始 stub 函数，8 项合成输入断言通过，覆盖估计标记、空音频引用、逐字符时刻、时长、缺字段拒绝、原声插段与片名区间；没有生成或识别声音。
- 自带横屏 starter：成功建立 14.78 秒的估计时间线，但 --check 因三个字体文件 404 而以错误退出。new_film.mjs 虽提示会退到系统字体，当前渲染初始化仍等待 document.fonts.load，实际没有完成这次回退。我们没有把这个结果记为模板验收通过。
- 独立最小渲染夹具：另写一个没有外部字体的确定性 Canvas 页面，保持上游 render.mjs 不变，真实截取 0、1、1.9 秒三帧并编码 2 秒、640×360、30fps、60 帧 H.264 无声 MP4；ffprobe 确认文件结构和帧数，随后完整解码通过。它证明这组环境下浏览器到编码器的局部链路可用，不证明 starter 已修好，也不代表真实新闻短片的质量。

这个范围刻意不包括调用编程模型写一条新片、联网搜索新闻、抓取受限网站、生成语音、数字人口播、抠像、逐字识别、混音或整片叙事质量。模板里示例数字、占位素材和估计时间线不能被当作可发布的财经报道，也不能拿短片渲染耗时外推生产速度。

检查功能也要读清返回值。源码的 --check 会报告镜头表提醒，说明“过了不等于好看”；截图与视频路径中的部分页面错误或空画面情况会先打印日志。自动流水线除了看退出码，还应读取日志、检查资源、逐镜看片，并用 ffprobe 验证最终文件。

![小M分别检查镜头表、抽帧图和最终文件，把脚本通过与内容可发布分开验收](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-03.png)

## 适合谁，第一次怎么试？

它适合已经有一个事实清楚的科技／财经题目、愿意控制文案和视觉语言，又想把重复制作交给 Agent 的创作者。它不是随便填一个热点就可以无人负责地发布的内容工厂。

第一次先做 20 到 30 秒、无人出镜、只解释一个数字的片段。来源控制在少数一手材料，保留出处；先确认文案和镜头表，再做临时声音、关键帧和小样。等这段能稳定复现，再增加人物、图表与更复杂的剪辑。

代码与文档的 MIT 授权不覆盖样片第三方材料。实际发行时，仍需逐项确认采用素材的使用条件；仓库附带出处清单值得借鉴，但不能把别人的样片整包当作自己的授权素材库。

## 常见问题

### 它是独立的视频生成模型吗？

不是。wallstreet-explainer 是编程 Agent 的制作 skill 与脚本工具集，模型调用来自使用者选择的 Agent，画面主要通过代码、素材、浏览器与 FFmpeg 制作。

### 不给真人视频也能制作吗？

官方提供无人出镜路线，也有横竖屏模板。没有主持人视频时，可以用素材与图形组织解说；这不意味着无需写稿、找证据或审片。

### 可以完全离线、零成本使用吗？

准备好工程、字体和素材后，本地渲染可以独立执行。但默认临时 TTS 和网络素材采集需要联网，Agent 模型也可能收费，不能把开源脚本等同于全部服务免费。

相关阅读：https://blog.mushroom.cv/blog/raea-native-gpu-react-video-game-engine-guide/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

wallstreet-explainer connects scripts, evidence footage, narration timing and motion graphics into an agent-assisted production workflow. Its useful contribution is a repeatable process for making explainer videos, rather than a guarantee that one topic produces an accurate, finished film without review.

The project is HeyChengC/wallstreet-explainer. Its code and documentation use MIT, while third-party screenshots, footage, logos and people shown in examples are excluded. We reviewed a pinned revision and tested a small local rendering slice, not the complete AI production chain.

Repository: https://github.com/HeyChengC/wallstreet-explainer
Production workflow: https://github.com/HeyChengC/wallstreet-explainer/blob/main/SKILL.md
License: https://github.com/HeyChengC/wallstreet-explainer/blob/main/LICENSE

## What does the agent actually operate?

This is a skill for coding agents such as Claude Code and Codex, accompanied by Python and JavaScript tools. It is not a newly trained video model. The agent organizes the topic, script and shot code; tools retrieve material, capture pages, align audio, render frames and mix tracks.

The intended visual language uses original reporting and real footage as evidence, with large numbers, charts and causal diagrams explaining relationships. Blue fabric backgrounds and restrained 2.5D camera moves are a vocabulary, not a prescribed shot sequence. Each shot should first explain what the viewer learns.

There are landscape 16:9 and portrait 9:16 paths, with or without supplied presenter footage. A digital presenter appearing in an example does not mean the repository contains or trains a digital-human model.

![Little M connects topic, script, evidence, shot plan and rendering tools through an agent](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-01.png)

## Is the official workflow fully unattended?

No. The README summarizes the entry point as providing a topic, but SKILL.md lists eight stages numbered 0–7: topic, script, director plan, assets, narration and timeline, opening, full 720p preview, and final delivery. It explicitly asks for staged user review rather than delivering a finished film in one jump.

Those reviews have concrete artifacts: factual copy, a readable director table, representative source frames, alternative opening hooks and a full preview. We describe this upstream design; its approval stages are not additional approval requirements for publishing this blog article.

The benefit is a repeatable production procedure. Automation reduces file handling and repetitive editing. Editorial responsibility, factual accuracy and whether the finished piece explains anything remain separate judgments.

## Why is a news screenshot not a fact check?

snap_news.mjs opens a page in Playwright, scrolls to a requested passage, waits for fonts, captures the screen and records headings and keyword rectangles. Those coordinates support a later highlighter overlay that shows where a quoted number appears.

A successful screenshot does not establish that the reporting is current, that a number uses the right accounting period, or that the narration preserves its context. Keep the source URL, publication date, measurement definition and corresponding spoken sentence together.

The tool removes selected overlays and advertising elements. Its documentation advises against forcing a screenshot through a challenge page; verified text can instead be typeset without pretending it is an authentic screenshot of the blocked site. The resulting image still needs inspection.

![Little M connects verified source dates and measurement definitions to each narrated claim](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-02.png)

## Which components run locally?

| Component | Dependency and boundary |
| --- | --- |
| Planning and shot code | An external coding agent and its chosen model; MIT software does not include model credits |
| Footage retrieval | Network sources and tools such as yt-dlp |
| News captures | Playwright visiting the actual source page |
| Temporary narration | edge-tts, an online speech service rather than bundled offline weights |
| Word alignment | Optional local faster-whisper with downloaded models; source includes CUDA and CPU paths |
| Matting | Optional ONNX models and runtime, prepared separately |
| Rendering and mixing | Local browser frame capture and FFmpeg once inputs are available |

Installation also needs Node.js, Python, FFmpeg/ffprobe, Playwright Chromium and separately prepared fonts. The README lists MiSans, Alimama ShuHeiTi (阿里妈妈数黑体), Bebas Neue, Montserrat and Noto Sans SC. Follow the exact CSS filenames rather than assuming a system substitute is equivalent.

Local rendering therefore does not establish a completely offline workflow. Replacing temporary speech with an existing recording also requires correct timing and a new alignment check; swapping the audio alone can leave an obsolete timeline.

## How are narration and shots connected?

Script sentences have stable identifiers. Shot cues use markers such as @b02:keyword instead of embedding arbitrary seconds throughout the code. Before speech is available, timeline_stub.mjs estimates duration from character classes and explicitly marks the timeline as a stub. That is planning data, not measured speech alignment.

render.mjs expects a ready Promise and seek(t) on the page. It seeks each frame, captures it in a browser and passes frames to FFmpeg. This is a browser rendering pipeline, not a native GPU game engine or a diffusion-based video model.

## What did our local check cover?

Mycelium Protocol reviewed revision b79bc0573455cb5fe335e78f653012e658fa9758 and used Node.js 26.10.0 with FFmpeg 9.0.2 to exercise a small portion of the bundled landscape starter project.

The actual results were separated:

- Timeline: eight assertions against the original stub function passed using synthetic inputs. They cover the stub marker, absent audio reference, per-character cues, duration, required-field rejection, an inserted source clip and a title interval. No speech was generated or recognized.
- Bundled landscape starter: project creation produced a 14.78-second estimated timeline, but --check failed because three font files returned 404. Although new_film.mjs suggests system fallback, initialization awaits document.fonts.load and this run did not fall back successfully. This is a failed starter check, not a passed template acceptance.
- Independent minimal fixture: we wrote a deterministic Canvas page without external fonts and left upstream render.mjs unchanged. It captured three frames at 0, 1 and 1.9 seconds, then encoded a silent two-second, 640×360, 30fps, 60-frame H.264 MP4. ffprobe confirmed the stream and frame count, and complete decoding succeeded. This validates the browser-to-encoder slice only; it neither repairs the starter nor demonstrates editorial quality.

We did not ask a coding model to produce a new film, retrieve live news, test restricted websites, synthesize narration, run a digital presenter, matte people, recognize or align speech, mix audio, or assess a complete narrative. Starter figures, placeholder assets and estimated timings are not publishable financial reporting. This test is not a throughput benchmark.

The check path prints shot-table warnings and explicitly says that passing does not mean the result looks good. Some screenshot/video paths also log page errors or blank-image findings. A production wrapper should inspect logs and resources as well as exit status, review frames, and validate the final container with ffprobe.

![Little M checks shot reports, sampled frames and the final file separately before delivery](../../assets/images/wallstreet-explainer-agent-video-production-guide-fig-03.png)

## Who should try it first?

The project suits creators with a well-defined, verifiable technology or finance question who want control over copy and visual language while delegating repetitive production tasks. Start with a 20–30 second presenter-free segment explaining one number from a few primary sources.

Keep citations, review the script and director table, then test temporary timing, representative frames and a short preview. Add presenters and complex graphics only after that small loop is reproducible. The MIT license on scripts does not clear third-party sample media for reuse.

## FAQ

### Is this a standalone generative video model?

No. It is an agent skill and production toolkit using coding agents, source assets, a browser and FFmpeg.

### Can it work without presenter footage?

The project documents presenter-free landscape and portrait workflows. They still require a script, evidence selection and visual review.

### Is the entire workflow offline and free?

Prepared local rendering can run independently, but default temporary TTS and web sourcing require network access. The chosen coding model may also charge for usage.

Related reading: https://blog.mushroom.cv/blog/raea-native-gpu-react-video-game-engine-guide/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
