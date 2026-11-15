---
title: "Lemo Opuscar：99种风格的代码制片与2.0许可变化"
titleEn: "Lemo Opuscar: 99 Film Styles and the 2.0 License"
description: "Lemo Opuscar在线画廊已扩展至99种影片风格与15个分类，Agent可参考导演、风格和渲染工具用代码制作短片。本文更新2.0版本的模型适配、生图依赖、运行条件及混合许可，区分MIT代码、非商业文档授权与额外商业制片许可，保留此前最小渲染实测的范围，并说明配音联网、素材权利和可重建工程的验收边界。"
descriptionEn: "Explore Lemo Opuscar’s 99 film styles, 2.0 code and docs licenses, commercial filmmaking permissions, image-tool dependencies and limits of our render test."
wechatTitle: "Lemo Opuscar：99种风格与许可变化"
wechatDigest: "画廊增至99种风格，代码仍为MIT，文档许可与商业制片授权需要分开理解。"
pubDate: "2026-10-20"
updatedDate: "2026-11-15"
category: "Tech-News"
tags: ["Lemo Opuscar", "AI视频", "Agent Skill", "创意编程", "Canvas", "WebGL"]
heroImage: "../../assets/images/lemo-opuscar-code-video-skill-banner.jpg"
---

Lemo Opuscar 能让编码 Agent 把一个主题做成有画面、声音和剪辑的短片。它的核心是将导演方法、风格提示与渲染工具放进同一套工作流，让 Agent 写代码来制作影片。

官方仓库是 `lemomo-ai/lemo-opuscar`，作者为 Lemomo（`@lemomo_ai`）。截至2026年10月20日，本次 GitHub API 快照为3,783星；我们核对了51种正式风格，另有一个不计入数量的模板目录。素材里的“2800+”是较早的热度描述，不影响项目的实际用法。

## 2026年11月更新：99种风格，2.0的边界变了

11月15日核对官网与仓库，当前版本为2.0.0，画廊展示99种风格，按15个分类组织，涵盖剪辑纪实、绘画插画、线稿图解、游戏、屏幕界面、仪器实证与数据地图等。每种风格有独立页面，可以先看样片、剧照和用途，再把对应STYLE.md交给Agent。官网11月12日公告称本轮新增33种；旧文的51种是10月20日快照，不能把99减51都归到一次发布。

README现在说明，本次版本由Claude Fable 5.2审阅改进，Fable、Opus、Sonnet均可使用，建议高effort。这是作者的适配说明，我们没有逐个模型复测效果。其他Agent能读取技能，也不等于能做出同样质量的短片。

三个风格额外依赖用户提供的生图工具：Manga Panels、Text Flash Cuts、Comic History Cartoon。它们仍将画面组织为代码渲染，但需要先取得生成的角色等图像资产；没有可用生图账号或工具时，不能把这三种宣传为纯代码、零外部生成依赖。当前README要求Node20+、FFmpeg7+和Python3.11+或uv；不能直接沿用Ubuntu24.04自带的FFmpeg6.1。

2.0也更新了许可：代码仍为MIT，Markdown指南、技能说明和图像提示词改为CC BY-NC 4.0。作者另外明确允许创作者及参与同一影片的员工、承包方和客户，读取、复制、改编这些文档来制作自己的影片，包括商业影片，并随该片工程交付相关文档。把文档或改写版单独售卖，或放入另一个以商业获益为目的的产品、服务，则超出这项额外许可，需要另行授权。2.0以前发布的版本及其分支保留原有许可；新条款不能倒套到旧版上。

工程上，我建议把风格页当成选型入口，先做15–30秒代表性镜头，记录所用提交、模型、声音来源及实际依赖，再扩成整片。99个样片能帮助判断视觉语言，不能证明任意新故事都已跑通。以下导演、渲染接口和两秒测试保留10月20日固定版本的研究范围；本次仅复核新官网、文档和许可，没有重跑99种风格或完整制片流程。

在线画廊：https://lemomo-ai.github.io/lemo-opuscar/
当前固定版本：https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6
当前许可：https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/LICENSE

**这套工具的主要路线是 Canvas/WebGL 逐帧渲染，而非调用视频生成模型抽取镜头。** 它省掉了一部分视频模型依赖，但制作仍需要编码模型、浏览器、FFmpeg、声音工具和成片验收。

## 它把哪些制作工作交给Agent？

可以把它理解成一个小型制片流程：先确定影片要讲什么，再写处理方案与分镜，画面由网页程序绘制，声音按同一条时间线生成或组织，最后混音并封装为 MP4。

| 环节 | 仓库提供的基础 | 仍需Agent或创作者决定的事情 |
|---|---|---|
| 导演 | `DIRECTOR.md` | 主题、叙事、镜头、节奏和表演 |
| 视觉风格 | `styles/<style>/STYLE.md` | 如何把自己的故事画成该风格 |
| 技术制作 | `TECHNIQUE.md`、`core/` | 场景代码、声音事件、资源加载 |
| 输出与复核 | 静帧、视频、字幕和混音工具 | 是否好看、准确、易读、声音自然 |

它不是一个只有“神级提示词”的列表。共享工具让画面、声音和输出遵守相对明确的接口，风格样片则提供可参照的视觉语言。不过，现成样片存在，不代表任意新主题都能自动达到同等质量。

![小M将主题交给导演与风格指南，再组织代码画面、声音和成片输出](../../assets/images/lemo-opuscar-code-video-skill-fig-01.png)

10月20日固定版本要求先写 `TREATMENT.md`，再参考样片技术，避免把原片只换名字重新交付。这一点比“直接抄作业”更值得学：可复用的是制作方法，故事和表达仍应重新设计。

## 从51种到99种风格，应该怎样选？

风格库覆盖水彩、油画厚涂、浮世绘、像素游戏、纸艺、低多边形、玻璃产品渲染等路线。选择时先看内容适合什么视觉结构，而不是只选一个漂亮名字。

例如，讲一个温暖的小故事可以先试水彩或纸艺；说明系统关系可以试信息图；介绍真实产品结构，可以查看拆解路线。10月16日新增的8种 Evidence Films 则围绕真实材料，包括卫星影像、激光扫描、档案、CAD和实测数据等。

Evidence Films 是一种以材料和证据驱动创作的方向，不是自动事实核查证明。数据来自哪里、坐标是否一致、单位有没有混淆，都需要实际检查。影片画得可信，不代表里面的数值就可信。

仓库还有展示影片 OPUSCAR 98，以及配套的98段风格资料。这是另一套作品与分析入口，不能把它直接当作主风格库“有98种可用模板”的统计。

10月19日加入的自定义风格流程也很实用：把修改后的风格保存在 `~/lemo-my-styles/`，与共享库分开，并先做15–30秒测试片。先检验一个短段落，再投入整片，是更容易控制返工成本的方式。

## 如何安装并开始第一部短片？

官方面向 Claude Code 的安装入口是：

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

这是使用说明，我们没有在本次研究中安装插件或让它自动接管当前工作区。首次使用时，Skill 会获取共享指南、工具和风格提示，默认库目录是 `~/lemo-opuscar`；新影片工程位于发起任务的目录下。

也可以克隆仓库，在仓库内工作。为便于复核，下面固定本次研究的提交：

```bash
git clone https://github.com/lemomo-ai/lemo-opuscar.git
cd lemo-opuscar
git checkout b5e8ef93930b6d828f352055a689320f138237b1
claude
```

这种方式的影片工程通常放在 `films/<name>/`。其他 Agent 可以读取该 Skill 的目录。10月固定版针对 Opus 5.5 调整，2.0的模型适配见前文更新，换模型不保证相同效果；“能读SKILL.md”与“能完成同样的影片”是两个验收项。

当前系统要求 Node 20+、FFmpeg 7+、Python 3.11+或 uv。官方主要在 Apple Silicon macOS 开发，Linux建议按文档配置，Windows使用WSL；3D和大量着色器的风格还要考虑GPU。插件之外还会下载浏览器、Python依赖，以及所需的语音模型或采样库。语音依赖文件特别注明Kokoro需要Python 3.11–3.13，建议用独立环境，别直接假设最新系统Python可用。

第一条需求可以写得具体一点：

```text
做一部30秒水彩风格短片，解释阳台番茄从开花到结果。
面向第一次种菜的人，16:9，中文旁白，最多四个镜头。
先给我看处理方案和分镜，再制作。
我没有自己的录音和音乐；先列出声音方案及联网需求。
成片之外，保留字幕、素材来源、源码和一键重建脚本。
```

主题、观众、时长、镜头上限和验收阶段一旦确定，Agent就少了很多猜测。需要先看分镜时，应明确说出来；官方默认允许用户选择是否经过这个暂停点。

## 为什么它能用代码稳定生成视频？

核心工具要求网页提供三个约定：资源就绪后设置 `window.READY`；用 `window.render(t)` 绘制指定时刻；用 `window.DUR` 描述总时长。渲染器启动无头浏览器，按帧率给出时间点，再把截图通过管道交给 FFmpeg 编码。

关键在于 `render(t)` 必须由时间决定画面。不能依赖浏览器今天跑得快不快，也不能靠上一帧累积状态；随机效果需要固定种子。这样同一时间点才能单独检查，多工作进程也才能渲染不同片段。

例如，30秒、24 FPS的影片有720帧；这只是帧数计算，不是生成速度承诺。增加分辨率、复杂着色器、字体、粒子或后处理，都可能改变总渲染时间。

![小M按时间点绘制确定性画面，浏览器逐帧捕获，再交给FFmpeg编码](../../assets/images/lemo-opuscar-code-video-skill-fig-02.png)

在已有影片网页之后，可以先看几个时间点，再渲染完整画面：

```bash
node core/render/still.mjs films/tomato-story 0 5 12 --size 1280x720
node core/render/video.mjs films/tomato-story \
  --fps 24 --workers 3 --size 1280x720
```

这些命令需要已经存在的 `index.html` 及上述接口，并不会仅凭目录名自动写好故事。静帧工具默认输出到 `stills/`，视频工具默认生成 `out/video.mp4`，后者还不是已经完成旁白和混音的最终交付片。

## 配音和音乐是否完全免费、完全离线？

开源许可与运行成本需要分开看。作者估计一部影片通常需要 Agent 工作30–60分钟，并消耗较多Token；这是作者的经验说明，不是本次测量，也没有给所有片长或复杂度设定统一价格。

| 成本或数据路径 | 当前默认路线 | 判断时要注意 |
|---|---|---|
| 编码Agent | 旧版主要针对Opus 5.5；2.0列出Fable/Opus/Sonnet | 模型订阅或API成本另算 |
| 英文旁白 | Kokoro，本地推理 | 首次仍需下载模型和依赖 |
| 中文旁白 | edge-tts，在线服务 | 文本需要发送到相应语音服务 |
| 音乐 | 编写乐谱、采样与合成 | 采样库下载、许可证及混音需核对 |
| 渲染 | Chrome与FFmpeg | 占用本机计算、存储与制作时间 |

仓库也允许使用用户自己的录音、音乐或指定声音。文档提到Kokoro有离线中文声音，但对自然度有自己的评价，不能把默认的在线中文方案宣传成离线无网络。

它提供逐句ASR回查、字幕时间、声音压缩与混音规范。回查能帮助发现漏读和错读，却不能证明情感自然、表演合适。当前TECHNIQUE仍把默认中文路径写为在线edge-tts，而README许可段建议自制影片使用Kokoro或有权使用的声音；两处表述应分别核对，不能据此承诺全程离线。中文短句还可能出现识别误差；文档允许人工听确认后指定预期识别文本，因此“检查通过”仍需要结合实际听感解释。

## 我们实际跑通了哪一小段？

10月20日在隔离的临时目录中，使用当时固定提交的渲染工具和自制的简单Canvas场景：白底上一个蓝色圆形随时间移动。我们检查了两个时间点的静帧、同一时间点重新渲染的结果，以及两秒、640×360、24 FPS的无声H.264视频。

这段检查用于验证网页时间接口、浏览器捕获和FFmpeg编码链路。我们没有调用Opus、安装完整Skill、生成51种风格样片，也没有验证旁白、音乐或完整导演流程；不能把它写成“已实测一键做出专业短片”。

检查结果和输出属性保存在研究记录中。它证明的是最小渲染基础可以独立运行，不证明新故事的审美质量，也不构成任何模型或硬件速度基准。

## 怎样验收，才算真正完成一部影片？

先验收处理方案：故事是否适合目标观众，每个镜头是否承担一个明确任务。再验收静帧与关键动作：主体有没有变形，字能否读完，镜头运动是否支持表达。最后全速播放带声音的最终文件，检查对白、音乐、字幕和剪辑是否一致。

![小M分阶段核对处理方案、画面与声音，最后交付影片和可重建工程](../../assets/images/lemo-opuscar-code-video-skill-fig-03.png)

官方交付清单不止一个MP4，还包括海报、需要时的SRT、`TREATMENT.md`、第三方素材`CREDITS`、源码和`build.sh`。这些文件能让你以后改一句旁白、调整画幅或替换一个镜头，而不必从一个不可编辑的最终视频重新开始。

许可需要按版本和资产分开：10月固定版的代码与文档为MIT；当前2.0的代码MIT、文档CC BY-NC及额外商业制片许可见前文。演示影片、剧照等通常按CC BY 4.0署名“Lemo-Opuscar by Lemomo (LemoLab)”、链接仓库和许可并注明修改，但第三方素材、Clawd角色、产品界面和商标不自动获得授权。LICENSE还排除了六段演示旁白：五段来自Edge TTS，一段来自Doubao TTS，不能单独提取复用；这些影片整体分享的允许范围以原许可说明为准。新制作影片归创作者，输入录音、字体、采样等仍需有相应权利。

我们的判断是，它尤其适合程序化动画、信息解释、风格化短故事和有明确数据来源的视觉说明。要求真人细腻表演、复杂实拍质感或完全自由的摄影效果时，应先做测试镜头，再决定是否采用这条路线。“人人都能当导演”是愿景，能否把一个具体故事做好，仍取决于表达、素材与迭代。

也可以结合本站Hypit文章比较：不同项目将视频组织成可编程结构的方式不同，别把“有开源工作流”当成同一套镜头和素材能力。
https://blog.mushroom.cv/blog/hypit-ai-agent-video-workflow-svml-claude-code-codex/

## 常见问题

### 这是另一个文生视频模型吗？

主要不是。它是一套让编码Agent写画面程序、组织声音和输出文件的Skill与工具库，主要画面路径是Canvas/WebGL逐帧渲染。

### 可以把Opus换成便宜的本地模型吗？

可以研究适配。当前2.0列出Fable、Opus、Sonnet并建议high effort，旧版针对Opus 5.5调优；其他模型可能不能复现。先检验理解风格、完成代码、修复渲染和声音组织的能力，再讨论替换后的总成本。

### 开源是不是意味着一部影片零成本？

不是。代码许可、模型费用、语音服务、素材条件以及本机渲染成本彼此独立。应按自己的影片复杂度和服务配置计算，不能从MIT许可推导出零费用。

## 来源与复核范围

复核日期：2026年10月20日。源码固定为 `b5e8ef93930b6d828f352055a689320f138237b1`。本次只做了自制极简场景的渲染链路检查，没有进行完整Agent制片、语音质量或速度测试；封面为概念图。

- 官方仓库：https://github.com/lemomo-ai/lemo-opuscar
- 影片画廊：https://lemomo-ai.github.io/lemo-opuscar/
- 固定版本：https://github.com/lemomo-ai/lemo-opuscar/tree/b5e8ef93930b6d828f352055a689320f138237b1
- 导演方法：https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/DIRECTOR.md
- 技术路线：https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/TECHNIQUE.md
- 工具接口：https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/core/README.md
- 风格索引：https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/styles/README.md

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Lemo Opuscar helps a coding agent turn a topic into a short film with picture, sound and editing. It combines directing guidance, style instructions and production tools so the agent can build the film in code.

The official repository is `lemomo-ai/lemo-opuscar`, by Lemomo, `@lemomo_ai`. Our October 20, 2026 API snapshot recorded 3,783 stars. We counted 51 actual style directories, excluding an additional template directory.

Its principal picture pipeline uses Canvas/WebGL pages rendered frame by frame, rather than a video-generation model. Coding-model usage, browsers, FFmpeg, audio tools and editorial review remain part of production.

## November update: 99 styles and the 2.0 boundaries

Checked November 15, the current package is 2.0.0 and the gallery presents 99 styles across 15 categories, with individual pages for films, stills, uses and STYLE.md instructions. The November 12 notice reports 33 additions in that release. Our original 51-style count is an October 20 snapshot; the difference between 51 and 99 should not all be attributed to one release.

The README now says this release was audited with Claude Fable 5.2 and supports Fable, Opus and Sonnet with high effort. These are author statements, not our comparative model tests. Three styles—Manga Panels, Text Flash Cuts and Comic History Cartoon—require an image-generation tool and suitable account supplied by the user. Their code-rendered films can incorporate generated image assets; they cannot start without that dependency. Current requirements include Node20+, FFmpeg7+, and Python3.11+ or uv, so Ubuntu24.04’s stock FFmpeg6.1 is insufficient.

Licensing also changed. Code remains MIT, while Markdown guides, skill instructions and image prompts use CC BY-NC 4.0. An additional express permission lets you and those working on the same film, including staff, contractors and the client, read, copy and adapt the docs to make your own films, including commercial/client work, and deliver relevant docs with that film’s project. Selling the docs or incorporating them, including adapted parts, into another commercially operated product or service exceeds that extra permission and requires a separate license. Versions published before2.0.0 and forks from them retain their original terms.

My engineering recommendation is to select a style using its page, then make a representative15–30second shot, recording the revision, model, voice source and dependencies before expanding the film. The gallery provides visual references; it does not establish reliable completion for every new story. The renderer interface and two-second test below retain their October20 pinned scope. This update checks the current public gallery, docs and license, without rerunning99styles or a full filmmaking workflow.

Gallery: https://lemomo-ai.github.io/lemo-opuscar/
Current pinned revision: https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6
Current license: https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/LICENSE

## What does the workflow organize?

`DIRECTOR.md` covers narrative, shots, performance, rhythm and review. `TECHNIQUE.md` explains implementation. Each `STYLE.md` provides a visual approach. Shared tools capture frames, generate or organize audio, mix and export the result.

The guides ask the agent to write a treatment before studying demo implementation. This encourages a new story rather than replacing names in the reference film. Reusable production methods are valuable; a strong reference does not guarantee an equally strong result for every topic.

![A directing guide and style library coordinate code-rendered picture, sound and final output](../../assets/images/lemo-opuscar-code-video-skill-fig-01.png)

## Which style should you choose?

The main library spans watercolor, impasto, ukiyo-e, pixel/game aesthetics, paper construction, low-poly scenes and product rendering. Choose according to the content's visual structure, not only the prettiest example.

Eight Evidence Films styles added on October 16 work with real material such as satellite images, laser scans, archives, CAD and measured data. This is a sourcing-oriented creative approach, not proof of automatic fact checking. Inputs, units, coordinates and claims still need verification.

OPUSCAR 98 and its 98 style analyses are a separate showcase. They should not be confused with the count of reusable styles in the main library. The October 19 custom-style workflow stores personal variants outside the library and makes a 15–30 second test film before committing to more production.

## How do you start?

The documented Claude Code installation is:

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

On first use, it obtains a shared library, normally at `~/lemo-opuscar`. Film projects live in the folder where the task begins. Alternatively, clone the repository, pin the reviewed commit and launch Claude there; projects then normally go under `films/<name>/`.

```bash
git clone https://github.com/lemomo-ai/lemo-opuscar.git
cd lemo-opuscar
git checkout b5e8ef93930b6d828f352055a689320f138237b1
claude
```

We did not install the plugin or invoke an agent filmmaking run in this research. Other agents can read the skill. The October version targeted Opus5.5; current2.0 model guidance is described above. Equivalent output from other models is not promised.

Current requirements include Node20+, FFmpeg7+ and Python3.11+ or uv. The project was developed on Apple Silicon macOS, with Linux guidance and WSL for Windows. Three-dimensional or shader-heavy styles need appropriate graphics resources. Browsers, Python packages, voices and instrument samples are additional downloads. The voice requirements specifically note Python 3.11–3.13 for Kokoro, so use a compatible isolated environment.

For a first request, specify a 30 second watercolor explanation of a balcony tomato plant, a beginner audience, four shots, Chinese narration and 16:9. Ask to approve the treatment and storyboard first, list audio/network requirements and preserve source, captions, credits and a rebuild script.

That brief makes creative decisions and acceptance points explicit. A request to see a storyboard matters because the documented workflow lets the user choose whether it pauses at that stage.

## Why does the renderer need a time-based contract?

A film page exposes `window.READY`, a deterministic `window.render(t)` and `window.DUR`. The renderer starts a headless browser, requests the correct time for every frame and pipes screenshots into FFmpeg.

The same time must produce the same picture independently of previous frames. Avoid unseeded randomness and wall-clock-driven animation. Independent time evaluation permits isolated frame inspection and rendering different segments in separate workers.

A30second film at 24 FPS contains 720 frames. That arithmetic is not a speed claim. Resolution, effects, fonts, particles and shading all influence the actual work.

![Time-indexed deterministic frames are captured by a browser and encoded with FFmpeg](../../assets/images/lemo-opuscar-code-video-skill-fig-02.png)

After an actual film page exists, inspect frames and then render picture:

```bash
node core/render/still.mjs films/tomato-story 0 5 12 --size 1280x720
node core/render/video.mjs films/tomato-story \
  --fps 24 --workers 3 --size 1280x720
```

These commands require an existing `index.html` implementing the page contract. They do not generate a story from a directory name. The default `out/video.mp4` is picture output, not automatically the completed narrated and mixed film.

## What costs money, and what goes online?

The author estimates 30–60 minutes of agent work and substantial token use for a film. That is an author estimate, not our measurement or a price guarantee.

The default English voice path uses local Kokoro inference after model download. Chinese narration normally uses online edge-tts. User recordings or specified audio can replace defaults; the documentation also mentions offline Chinese Kokoro voices, with quality qualifications. The current TECHNIQUE still documents online edge-tts for Chinese, while the README license section recommends Kokoro or an authorized voice for your own films. Reconcile the selected voice path explicitly; do not promise an entirely offline workflow.

Music uses written scores, sampled instruments and synthesis. Sample downloads and licensing still matter. Chrome/FFmpeg consume local compute and storage. Coding-model subscription or API costs remain separate from the repository's open-source license.

ASR checks help detect missed or misread speech. They do not establish emotional performance or naturalness. The Chinese workflow allows manual listening and an expected-ASR override for recognition errors, another reason to interpret a passed automated check carefully.

## What did we actually check?

On October20, in an isolated temporary directory, we used the pinned renderer files and an original minimal Canvas scene: a blue circle moves across a white background. We checked two still timestamps, a repeated render of the same timestamp, and a silent two-second 640×360 video at 24 FPS.

This checks the page contract, browser capture and FFmpeg encoding. We did not call Opus, install the full skill, reproduce the style collection or test narration, music and the complete directing process. It is not a model or hardware performance benchmark.

The output properties and check records are preserved with the research. A small functioning render path establishes a useful implementation foundation, not the aesthetic quality of a newly generated story.

## What counts as a finished delivery?

Review the treatment, then stills and key actions, then the final film at normal speed with sound. Verify text readability, narration, music, captions and transitions together.

![Review story, picture and sound before delivering the film together with its rebuildable source](../../assets/images/lemo-opuscar-code-video-skill-fig-03.png)

The documented deliverables include MP4, poster, SRT where relevant, treatment, third-party `CREDITS`, source and a one-command `build.sh`. An editable project is more useful for future revisions than a lone flattened video.

The October pinned code and docs were MIT-licensed. Current2.0 code is MIT; its docs use CC BY-NC plus the additional filmmaking permission described above. Demo films and stills generally use CC BY4.0 with “Lemo-Opuscar by Lemomo (LemoLab)” credit, repository and license links, and change disclosure. Third-party materials, Clawd, product interfaces and trademarks are excluded from blanket permission. Six demo narration tracks—five Edge TTS, one Doubao TTS—are excluded and must not be extracted or reused separately; whole-film sharing follows the specific LICENSE wording. Newly made films belong to their creators, while recordings, fonts, samples and other inputs retain their own terms.

Our assessment is that the approach is particularly suitable for procedural animation, visual explanations, stylized stories and sourced-data films. Test a representative shot before choosing it for demanding live-action appearance or subtle human performance. The workflow reduces production friction; a clear story, suitable assets and iteration still determine the result.

Compare the related Hypit article for another approach to programmable video structures:
https://blog.mushroom.cv/blog/hypit-ai-agent-video-workflow-svml-claude-code-codex/

## FAQ

### Is this another text-to-video model?

Its principal route is a skill/toolkit that guides a coding agent to implement scenes, audio and exports. Picture is mainly generated through frame-by-frame Canvas/WebGL rendering.

### Can a cheaper local model replace Opus?

It can be investigated. Current2.0 docs list Fable, Opus and Sonnet at high effort, while warning about other models; the old pinned version targeted Opus5.5. Check style interpretation, implementation, rendering repair and audio organization before comparing total costs.

### Does open source make each film free?

No. Code licensing, coding-model usage, speech services, asset conditions and rendering resources are separate. Estimate them for the actual brief and configuration.

## Sources and scope

Reviewed October 20, 2026 at commit `b5e8ef93930b6d828f352055a689320f138237b1`. We checked a minimal original scene through the renderer, not a complete agent filmmaking run, voice-quality evaluation or speed test. The cover is conceptual.

- Repository: https://github.com/lemomo-ai/lemo-opuscar
- Gallery: https://lemomo-ai.github.io/lemo-opuscar/
- Directing: https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/DIRECTOR.md
- Technique: https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/TECHNIQUE.md
- Tool contract: https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/core/README.md
- Style index: https://github.com/lemomo-ai/lemo-opuscar/blob/b5e8ef93930b6d828f352055a689320f138237b1/styles/README.md

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
