---
title: "brief2mp4：让AI做动画，也交出验收证据"
titleEn: "brief2mp4: Agent Motion Graphics With Delivery Checks"
description: "brief2mp4把动画制作拆成需求规格、工具路由、渲染、检查与修正，最终交付MP4及证据报告。本文核对MIT许可和0.4.0代码，运行60项原仓库测试及5个真实视频检查用例，解释HyperFrames、Three.js和ffmpeg的分工，以及为什么格式通过仍不代表字幕、构图、故事和客户需求已经通过验收。"
descriptionEn: "Explore brief2mp4's MIT agent skill, deterministic rendering and delivery checks, with 60 upstream tests and five video checks separating format from meaning."
wechatTitle: "brief2mp4：动画交付要有验收证据"
wechatDigest: "核对开源代码与真实视频检查，看看AI制作动画如何交付证据，以及自动验收的边界。"
pubDate: "2026-11-19"
updatedDate: "2026-11-19"
category: "Tech-News"
tags: ["brief2mp4", "Agent Skills", "Motion Graphics", "HyperFrames", "FFmpeg"]
heroImage: "../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-banner.jpg"
---

brief2mp4让编码智能体按文字需求制作动画，并提交逐项验收报告。它最值得借鉴的，是把“视频做出来了”变成“哪些要求已经有证据证明”。

项目由Varun Pratap Bhardwaj维护，仓库为qualixar/brief2mp4，采用MIT许可。本文核对的是0.4.0版、提交`a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6`，查阅日期为2026年11月19日。

## brief2mp4究竟开放了什么？

它开放了给编码智能体使用的Skill、制作参考、模板和脚本。智能体理解需求并写动画代码，现有渲染工具负责生成画面，ffmpeg负责整理为交付文件。仓库没有发布一个新的文生视频模型，也不提供自己的模型权重。

核心产物有三个：制作前的`SPEC.md`、最终的`final.mp4`，以及说明逐条要求是否满足、依据是什么的`REPORT.md`。Skill要求先列出画幅、帧率、时长、准确字幕、视觉风格、分镜时段和验收条件，再开始写代码。

例如，“做一个好看的产品动画”很难检验；“15秒、1920×1080、30fps，最后两秒完整显示指定文案，标题高度至少100像素”就能拆成文件测量与画面检查。需求越具体，智能体越容易发现自己遗漏了什么。

![小M把模糊的动画请求拆成可逐项核对的制作规格](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-01.png)

## 一段动画为什么要调用多种工具？

brief2mp4按每个分镜的需要选工具，同一视频可以组合多条路线。

| 画面需要 | 主要路线 | 工程目的 |
|---|---|---|
| 字幕、布局、图表和二维动效 | HyperFrames，使用HTML、CSS与GSAP | 精确控制文字与时间线 |
| 粒子、风格化三维和镜头移动 | Three.js嵌入HyperFrames | 用代码控制空间与运动 |
| CAD零件、物理落体和爆炸图 | 可选3D包 | 建模、材质、物理烘焙与镜头组织 |
| 写实产品和光照 | 外部Blender | 生成写实镜头后参与合成 |
| 编码、拼接、时长和音频整理 | ffmpeg | 统一交付格式 |

这里一个扎实的设计是：画面应当由时间`t`决定。渲染器可能把不同时间点分给多个浏览器工作进程，帧的计算顺序未必连续。如果动画依赖真实时钟或未设种子的随机数，同一帧重算时就可能变样。

项目因此要求基于时间定位画面，随机扰动可复现，物理模拟先烘焙为逐帧姿态，再按时间读取。手工风格可以每秒只改变8至12次造型，同时保留24或30fps的视频帧率。可复现的画面也让修改与前后比较更可靠。

0.4.0列出30种美术风格及31个演示，包括剪纸、黏土、像素、蓝图等。这些是制作规则和可运行示例；实际成片质量仍取决于需求、智能体、场景代码与素材。

## “检查通过”具体保证了什么？

原始`check_delivery.sh`会检查H.264、yuv420p、尺寸、帧率、时长、音轨与响度等。默认目标包括30fps、AAC、48kHz双声道、约−14 LUFS，时长容差约为一帧。没有声音也需要保留音轨，静音须由需求明确允许。

但脚本不能独立证明字幕拼写、画面遮挡、叙事节奏或产品卖点正确。Skill还要求抽取关键时间的画面、实际查看，并逐条对照需求；修正最严重的问题后重新渲染，最多三轮。再次检查时要回到用户原始文字，防止错误的规格被反复自证。

黑屏或长期静止也只产生警告：它们可能是有意留白或结尾停留。也就是说，最终的`PASS`允许存在需要解释的`WARN`，不能直接当成客户签收。

![小M用两种量具分别检查视频文件规格和画面语义](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-02.png)

## Mycelium Protocol实际验证了哪些部分？

我们在本机macOS运行原仓库的CLI检测与美术风格相关测试：**60项通过，2项因可选3D核心包未安装而跳过，1项浏览器慢速测试未选择执行**。这覆盖路由、参考资料一致性、部分命令行为及检测逻辑，不能等同于全部风格已经完成真实浏览器渲染。

随后使用ffmpeg生成合成素材，直接调用未修改的`finish.sh`与`check_delivery.sh`，完成5个检查用例：

| 用例 | 实际结果 |
|---|---|
| 320×180、24fps、1秒素材整理成640×360、30fps、2秒，允许静音 | 通过；整理脚本补齐了时长和音轨 |
| 同一成片要求3秒 | 失败，发现时长不符 |
| 同一静音成片没有允许静音 | 失败，发现静音不符 |
| 无音轨原始素材 | 失败，发现音轨等规格不符 |
| 3秒纯色空白画面，格式正确且允许静音 | 通过，但出现长时间静止警告 |

最后一个是刻意设置的语义反例：画面没有任何标题，却能通过文件交付检查。它证明测量脚本有明确边界，仍需把“指定文字在指定时刻出现”变成另一项有证据的检查。

本次没有运行编码智能体从需求到成片的完整创作流程，没有安装或验证3D包、编辑包及Blender，也没有复现作者提供的渲染速度。这里验证的是本机脚本行为，而非动画创作质量排名。

## 工程师如何借鉴这套设计？

先做一个短、确定、容易验收的用例。比如15秒产品功能介绍，限制三段文字、一个示意图和两处音效；把精确文案、出现时间、竖屏安全区、授权音乐及交付规格写在原始需求里。不要一开始就用长片判断整套系统是否可用。

把验收分成文件规格、内容覆盖和人工审美三个部分。文件规格由脚本测；文字与时间点可以加入字幕清单、关键帧和画面区域检查；品牌语气、事实准确性、视觉节奏则由编辑签字。报告应同时写明通过、失败与未核验，保留证据文件位置。

再让每个需求条目拥有固定编号，关联对应分镜、测试和截图。重新渲染后更新相关证据，避免旧截图证明新版本。若要批量用于客户交付，还应保存输入文件哈希、依赖版本和渲染设置，便于重现与追查。

![小M沿着原始需求逐格回查成片，而不是只相信绿色通过标记](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-03.png)

## 如何开始，成本与许可要注意什么？

README提供克隆后运行`install.sh`的路径，也支持插件安装。基础要求是Node.js 22+与ffmpeg，Windows脚本使用Git Bash；3D、CAD、Blender和编辑包按需要再装。本次只在临时目录研究和调用脚本，没有把新Skill装进用户的编码环境。

```bash
git clone https://github.com/qualixar/brief2mp4.git
cd brief2mp4
bash plugin/skills/brief2mp4/scripts/doctor.sh
```

免费的是MIT许可的项目代码。编码智能体的模型调用、渲染算力、存储以及外部素材可能另有成本。“本地渲染”也不能自动推导为离线：若编码智能体使用云端模型，需要按它的服务配置判断需求和代码是否会离开设备。

MIT许可也不覆盖所有依赖和输入资产。仓库说明HyperFrames、Three.js、GSAP、Blender、ffmpeg等保留各自许可；字体、音乐、商标和客户录屏也需要分别确认使用条件。项目的兼容性表及样片说明来自作者，本次检查没有证明所有系统和路线均可交付。

## FAQ

### brief2mp4能直接替代视频生成模型吗？

它适合让编码智能体调动工具制作可控的动效、图表与产品动画。需要模型生成的真实人物、复杂自然运动或拍摄素材时，仍要另外准备对应工具或资产。

### 检查通过就可以自动发布吗？

不能只据文件检查决定。本文空白画面反例说明格式通过仍可能缺失核心内容，应补验需求覆盖、事实、视觉与授权，再进入发布流程。

### 最值得先移植哪一部分？

先移植“每条需求对应一份可查证据”的报告结构。即使用现有剪辑软件、Remotion或其他渲染器，这种做法也能减少遗漏，并帮助团队判断哪些问题尚未解决。

来源与复核入口：

GitHub与README：https://github.com/qualixar/brief2mp4

固定版本架构说明：https://github.com/qualixar/brief2mp4/blob/a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6/docs/architecture.md

固定版本交付检查：https://github.com/qualixar/brief2mp4/blob/a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6/plugin/skills/brief2mp4/scripts/check_delivery.sh

相关工程阅读：Clover的代码开放范围与验证边界，https://blog.mushroom.cv/blog/clover-diffusion-llm-sft-engineering-guide/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

brief2mp4 directs a coding agent to make motion graphics from a written brief and deliver evidence for each requirement. Its useful contribution is making completion claims inspectable through specifications, measurements and real frames.

Varun Pratap Bhardwaj maintains qualixar/brief2mp4 under MIT. This review examines version 0.4.0 at commit `a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6`, accessed on November 19, 2026.

## What does brief2mp4 release?

The repository contains an agent Skill, references, templates and scripts. A coding agent interprets the brief and writes scene code; existing renderers produce pictures, and ffmpeg prepares the delivery file. The release contains no new video-generation model or model weights.

Its main artifacts are `SPEC.md`, written before implementation; `final.mp4`; and `REPORT.md`, which records whether each requirement was met and what evidence supports that conclusion. The specification includes dimensions, frame rate, duration, exact text, visual direction, timed beats and acceptance conditions.

“Make an attractive launch video” leaves much to interpretation. “15 seconds, 1920×1080, 30fps, the exact closing message visible for the last two seconds, headline height at least 100 pixels” separates measurable requirements from editorial judgment.

![Little M converts a vague animation request into individually checkable production requirements](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-01.png)

## Why does one video use several tools?

Routing happens per beat, so one film can combine several approaches.

| Requirement | Route | Purpose |
|---|---|---|
| Text, layouts, charts and 2D motion | HyperFrames with HTML, CSS and GSAP | Precise typography and timing |
| Particles, stylized 3D and camera moves | Three.js inside HyperFrames | Code-driven spatial motion |
| CAD parts, physics and exploded views | Optional 3D pack | Geometry, materials and baked motion |
| Photoreal products and lighting | External Blender | Realistic shots for composition |
| Encoding, joins, duration and audio | ffmpeg | Consistent delivery format |

A strong architectural choice is to compute pictures from time `t`. Parallel browser workers can request frames out of order. Wall-clock animation and unseeded randomness can therefore produce different pictures when the same frame is rendered again.

The project calls for time-addressable scenes, reproducible variation and physics baked into frame-by-frame poses. Handmade looks can update drawings 8–12 times per second while the file remains at 24 or 30fps. Reproducibility makes revisions and comparisons more reliable.

Version 0.4.0 lists 30 art forms and 31 demos, including paper cut-out, claymation, pixel art and blueprint looks. These are recipes and examples. The final result still depends on the brief, agent, implementation and assets.

## What does a delivery PASS establish?

The original `check_delivery.sh` checks H.264, yuv420p, dimensions, frame rate, duration, audio presence and loudness. Defaults include 30fps, AAC, 48kHz stereo and approximately −14 LUFS. Duration tolerance is about one frame. Even an intentionally silent delivery needs an audio track and explicit permission for silence.

These checks do not establish spelling, lack of overlap, narrative timing or correct product claims. The Skill additionally requires stills from named moments, actual visual inspection and evidence for each acceptance condition. It asks the agent to fix the largest miss and repeat, up to three rounds. A recheck returns to the original brief, because a mistaken specification can otherwise validate itself.

Long black or frozen sections produce warnings: they may be intentional pauses or holds. A final `PASS` can therefore include unresolved `WARN` messages and requires interpretation.

![Little M uses separate instruments for file specifications and the meaning of the pictures](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-02.png)

## What did Mycelium Protocol actually test?

On macOS, the selected upstream CLI-detection and art-form tests produced **60 passes, two skips because the optional 3D core was absent, and one deselected slow browser test**. This exercises routing, reference consistency and selected command and detection behavior. It does not establish that all looks render correctly in a real browser.

We also generated synthetic clips with ffmpeg and called the unchanged `finish.sh` and `check_delivery.sh` in five cases:

| Case | Observed outcome |
|---|---|
| Convert a 320×180, 24fps, one-second source to 640×360, 30fps, two seconds, permitting silence | PASS; finishing adds duration and audio |
| Require three seconds from the same finished clip | FAIL on duration |
| Check the silent delivery without permitting silence | FAIL on silence |
| Check the original clip without audio | FAIL on audio and other delivery mismatches |
| A three-second blank teal picture with correct format and permitted silence | PASS with a frozen-picture warning |

The last case is a deliberate semantic negative control: the picture contains no headline, yet passes file delivery checks. A requirement such as “show this exact message at this time” needs its own evidence.

We did not run an agent through a complete brief-to-video creative workflow, install or verify the optional 3D or edit packs or Blender, or reproduce the author's rendering speeds. These are local script-behavior checks, not a ranking of creative quality.

## How can engineers reuse this design?

Start with a short, bounded brief: a 15-second feature introduction, three lines of text, one diagram and two sound accents. Specify exact copy, appearance times, vertical safe areas, licensed music and delivery settings in the original requirements. A long film is a poor first diagnostic.

Separate file specifications, content coverage and editorial judgment. Scripts measure file properties. Text lists, named frames and region checks can support content review. An editor signs off on factual accuracy, brand voice and pacing. The report should retain passes, failures and unverified items, together with evidence locations.

Give every requirement a stable identifier that links to its beat, test and screenshot. Refresh affected evidence after rendering so an old screenshot cannot certify a new revision. Customer-delivery pipelines should also retain input hashes, dependency versions and render settings for reproducibility.

![Little M checks the final film against the original brief instead of trusting a green PASS alone](../../assets/images/brief2mp4-agent-motion-graphics-verification-guide-fig-03.png)

## How do setup, costs and licensing work?

The README offers script and plugin installation routes. Basic requirements are Node.js 22+ and ffmpeg; Windows scripts use Git Bash. Add 3D, CAD, Blender and editing components when needed. This review used a temporary checkout and did not install a new Skill into the user's coding environment.

```bash
git clone https://github.com/qualixar/brief2mp4.git
cd brief2mp4
bash plugin/skills/brief2mp4/scripts/doctor.sh
```

The MIT project code is free. Coding-agent calls, rendering compute, storage and external assets may have costs. Local rendering does not imply offline operation: a cloud-backed coding agent may send prompts or code to its service, depending on configuration.

MIT also does not relicense dependencies or input assets. HyperFrames, Three.js, GSAP, Blender, ffmpeg and other components retain their own terms. Fonts, music, trademarks and customer recordings require separate consideration. Author compatibility statements and sample renders exceed the scope of our checks.

## FAQ

### Does this replace a video-generation model?

It helps a coding agent make controlled motion graphics, charts and product animations with existing tools. Realistic people, complex natural motion or filmed footage can require additional tools and assets.

### Can a PASS automatically authorize publication?

File checks alone cannot. The blank-picture control demonstrates that correct formatting can coexist with missing core content. Verify requirements, facts, visuals and usage rights before publication.

### What should a team adopt first?

Adopt the report structure that maps every requirement to inspectable evidence. It works with existing editors, Remotion or other renderers, helps catch omissions and exposes unresolved issues.

Sources:

Repository and README: https://github.com/qualixar/brief2mp4

Pinned architecture: https://github.com/qualixar/brief2mp4/blob/a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6/docs/architecture.md

Pinned delivery checker: https://github.com/qualixar/brief2mp4/blob/a392d1bfb8771f2bc5b5d55ce7aef2b2535d16a6/plugin/skills/brief2mp4/scripts/check_delivery.sh

Related engineering review, Clover's released-code and verification boundaries: https://blog.mushroom.cv/blog/clover-diffusion-llm-sft-engineering-guide/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
