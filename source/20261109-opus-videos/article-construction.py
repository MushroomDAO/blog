from pathlib import Path
import json
s='awesome-opus-videos-code-animation-guide'
cn='''awesome-opus5-5-videos 是一份用来学习“让 AI 写代码做动画”的案例与提示词合集。它最值得看的不是某段视频有多炫，而是创作者如何描述画面、组织时间轴，并把浏览器里的动画变成能够交付的视频。

先纠正地址：仓库所有者是 yihui-dev，原始素材中的 yihiu-dev 拼写有误。2026 年 11 月 9 日本次 GitHub API 快照为 14,384 Star；最后推送时间为 10 月 13 日，README 的内容更新标记为 10 月 12 日。“约 14k Star”可以确认，近期持续更新则未得到这次快照的支持。

仓库：https://github.com/yihui-dev/awesome-opus5-5-videos
配套浏览页：https://skillry.dev/ai-videos/opus-5-5

## 这是视频生成模型，还是编程案例库？

项目收集的是作者标注为 Claude Opus 5.5 创作的视频、原帖和提示词。主要路径是模型生成 HTML、Canvas、SVG、Three.js 等绘图或交互代码，浏览器运行这些代码，再录制或逐帧渲染得到视频。

这里需要区分三个产物：提示词描述要求，动画源码执行要求，MP4 保存执行后的画面。**拿到提示词，不等于拿到原视频的源码和全部素材。** 有的作品需要图片、音乐、字体或额外脚本，单独复制一段文字可能复现不了原帖效果。

本次 checkout 的跟踪内容为 Markdown、一个 JSON 数据文件、LICENSE 和 .gitignore，没有随附动画的 HTML/JS 源码，也没有可直接启动的渲染应用。clone 仓库得到的是资料集，不能把它当成装完依赖就批量出片的软件。

封面采用仓库 README 的作品拼图，展示的是合集收录的视觉样例，不是我们重新生成或验证的作品。

## 703、418、100，分别在数什么？

我们对固定版本 92aee2f586ac0715cb3cbcb6384834f98a33383d 做了只读数据核对，结果如下。

| 项目 | 本次核对结果 | 如何理解 |
|---|---:|---|
| data/videos.json 条目 | 703 | 元数据记录数，不是独立成功复现次数 |
| prompts/ 下的文件 | 703 | 每条都有对应提示词文件 |
| has_remake 为真 | 418 | 标记有 Skillry 复刻链接，不等于原始源码开源 |
| prompt_partial 为真 | 207 | 可能只有部分提示词或原帖描述 |
| prompt_partial 为假 | 496 | 合集未标记为部分内容，完整性仍需结合上下文判断 |
| README 分类精选 | 100 | 58 动效、16 讲解、14 三维、12 游戏交互 |

全量 JSON 的四类分别为：动效 369、讲解 116、三维场景 117、游戏交互 101。它们不是 README 精选区的分类数量。阅读第三方镜像时，尤其要留意它展示的是哪次同步和哪一种统计口径。

285 条没有复刻标记的记录，其 skillry_url 为空；这与元数据的可选字段设计一致，不能一概判成链接损坏。所有 703 个 slug 唯一，文件对应齐全，外层文本块提取并统一换行后，JSON 与 Markdown 的提示词内容一致。

这些检查只证明当前资料结构能对上。它们不证明所有原帖仍能访问、所有视频确由指定模型完成，或全部提示词可以一次成功生成同样的画面。

![小M区分案例条目、部分提示词和外部复刻链接](../../assets/images/awesome-opus-videos-code-animation-guide-fig-01.png)

## 为什么“用代码做视频”值得学？

对于产品动效、流程讲解、数据可视化和简单交互，代码把大量视觉要求变成了可修改的参数：元素在哪里，何时出现，停多久，如何移动，什么时候结束。改一个数字，不必重新生成整段素材。

它也有明确边界。需要复杂摄影质感、真实人物表演或大量原创资产时，浏览器动画未必是合适的主要工具。交互游戏的录屏看起来像视频，也不代表游戏逻辑、联机和性能已经达到发布标准。

这份合集适合当“视觉需求词典”：观察别人怎样描述层级、节奏、镜头和约束，再把这些描述用到自己的作品中。热门作品经过筛选，没有失败尝试的分母，不能直接用来推断模型的平均成功率。

## 最有价值的提示词，实际上在约定什么？

以 twoclipping-402193 为例，提示词不只要求做一个漂亮的 UI 动画，还约定先确认输入、用节拍组织状态变化、先检查关键帧，再渲染整段。它把审美方向、技术结构和验收顺序放在一起。

fleyta88-443662 则描述了具体动画时长和错开出现的间隔，并要求逐帧检查、局部修正。0xkarmi-129839 的收录文本强调按帧编号绘图、编码以及循环接缝检查；这类内容也提醒我们：标在 Prompt 栏里的文字可能带有原帖叙述，需要先读懂再转成任务。

这些案例共同指向一个实用原则：不要只要求“高级、丝滑、有科技感”，还要说明什么出现、何时出现、输入是什么、用什么形式交付，以及怎样判定失败。

对于讲解视频，还应先核对事实、公式和单位。画面里的粒子运动像物理模拟，不代表计算结果就符合对应的物理方程；模型写出了演示，也不能替代科学验证。

## 怎样做出可以逐帧检查的动画？

一个好用的接口是 seek(t)：给它一个时间，页面就显示对应画面。比起让动画完全依赖真实时钟和层层累积的状态，这种设计更容易抽查中间帧、重渲染片段和定位文字重叠。

但有这个函数名还不够。随机粒子需要固定种子，物理模拟需要固定步长或缓存状态，字体与图片应加载完成后再绘制。否则，相同 t 仍可能产生不同结果。

假设作品为 12 秒、30 fps，正式编码通常取 360 帧，时间为 0、1/30……359/30 秒。为了检查循环接缝，可以额外渲染 t=12 与 t=0 比较，但不要未经考虑就把重复的终点帧也编进循环。

仓库中的相关提示词给出了这类思路，未提供统一实现。我们没有运行这些作者作品或验证逐像素确定性，因此这里是工程方法介绍，不是对合集全部作品的测试结论。

![小M用固定时间抽查关键帧，再将帧序列编码为视频](../../assets/images/awesome-opus-videos-code-animation-guide-fig-02.png)

## 从复制提示词到交付视频，可以怎样做？

Mycelium Protocol 建议先选一个范围小的作品，如十几秒的三卡片流程讲解。以下是我们整理的工作流，不是仓库自带的自动化管线。

1. 先读原帖和提示词标记，列出缺失输入：字体、图片、音频、比例和输出格式。没有完整素材时先明确替代方案。
2. 写分镜和时间表，确认文字、数据及每个画面的目的。先约束信息密度，再调整风格。
3. 要求 Agent 生成可运行页面，并说明动画入口、依赖和资源路径。先验证静态构图，再做转场。
4. 检查开头、结尾和每个转场中点，重点看文字溢出、遮挡、闪烁、空白画面及错误日志。通过后再渲染全片。
5. 编码并用正常速度完整观看。音轨同步、裁切和循环接缝要在最终文件中再查一遍，不能只看浏览器预览。

下面这段是本次撰写的练习任务，可按自己的信息改写；它不是从作者原帖复制的提示词，也未在本次调用模型生成视频。

```text
做一段12秒、1920×1080的三步骤流程动画。
只使用本地HTML、Canvas和系统字体，不加载外部素材。
先给出分镜与时间表，再输出源码；提供seek(t)入口。
每一步使用一张卡片，每张卡片只放一个标题和一行说明。
先检查0、3、6、9、12秒的静态帧，再处理转场细节。
说明如何运行、如何渲染360帧，以及哪些条件尚未验证。
```

如果已经得到编号为 0000.png 到 0359.png 的帧序列，可以使用下面的常见 FFmpeg 编码形式。它仅展示帧序列到视频的步骤，不负责生成画面，也没有自动加入音轨；本次没有实际执行这条导出命令。

```bash
ffmpeg -framerate 30 -i frames/%04d.png \
  -c:v libx264 -pix_fmt yuv420p output.mp4
```

同一张画面既要做横屏又要做竖屏时，应重新安排文字和主体位置，而不是默认居中裁掉两边。会动的网页与可分享的视频文件，是两次不同的验收。

![小M按分镜、页面、关键帧和最终视频逐步验收](../../assets/images/awesome-opus-videos-code-animation-guide-fig-03.png)

## MIT 是否意味着所有视频都能随便商用？

仓库声明 MIT，但 README 同时明确视频和提示词归各自创作者所有，并为每条提供原帖。仓库许可证不应被扩展解释为收录作品里的音乐、人物、品牌、字体和图片都已获得商业使用许可。

学习构图和编程方法，与直接搬运成片是不同的使用方式。发布自己的作品时，应分别确认输入素材和输出使用条件，保留必要署名。需要改动或移除条目时，README 提供了提 issue 的路径。

## 本次核验范围与常见问题

### 需要安装什么才能浏览仓库？

GitHub 就能直接读 Markdown 和 JSON。配套 Skillry 页面本次能够获取到 HTML，但我们没有在浏览器内逐一播放或操作全部复刻。生成和导出所需的软件取决于所选提示词，不存在仓库统一保证的一条安装命令。

### 换一个模型能用这些提示词吗？

可以把任务要求迁移给其他编程模型尝试，但工具、上下文和资源条件会影响结果。这里没有跨模型对照实验，不能保证画面一致或质量等价。

### 这 703 条能否当作模型评测集？

可以用它们寻找待测任务，但不能直接当成已验证的评测基准。应先清理部分提示词、固定输入资产和预算，定义可检查的指标，再保存全部尝试和失败结果。

本次只读审计覆盖条目、分类、slug、提示词文件对应、可选链接字段及文本一致性。最初的审计脚本误把可选复刻链接要求为必填，并用简单代码围栏解析截断了一个内嵌代码块的长提示词；核对数据结构后修正了审计器，上游内容未改。我们没有调用 Opus、重新生成视频、重建 Skillry 或验证原作者的完整制作过程。

## 原始资料与延伸阅读

仓库：https://github.com/yihui-dev/awesome-opus5-5-videos
数据：https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/data/videos.json
UI 动效案例：https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/twoclipping-402193.md
逐帧检查案例：https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/fleyta88-443662.md
配套浏览：https://skillry.dev/ai-videos/opus-5-5
FFmpeg 文档：https://ffmpeg.org/ffmpeg.html

相关项目：https://blog.mushroom.cv/blog/rea-video-nuphos-agent-workflow-review/
图像生成的部署边界：https://blog.mushroom.cv/blog/moss-image-openmoss-layout-generation-review/
'''
en='''awesome-opus5-5-videos is a collection for learning how to ask AI agents to write animation code. Its practical value lies in describing visual intent, organizing time, and turning a browser animation into a deliverable video.

The correct owner is yihui-dev; yihiu-dev in the supplied material is a typo. Our November 9, 2026 GitHub API snapshot records 14,384 stars, a last push on October 13, and a README content-update label of October 12. Approximately 14K stars is supported. Recent continuous updates are not established by this snapshot.

Repository: https://github.com/yihui-dev/awesome-opus5-5-videos
Companion gallery: https://skillry.dev/ai-videos/opus-5-5

## What does the repository actually provide?

The list attributes its collected videos and prompts to Claude Opus 5.5. The principal workflow is code generation: HTML, Canvas, SVG, Three.js, and related technologies produce graphics in a browser, which are then recorded or rendered into frames.

Prompts, animation source, and encoded video are separate artifacts. A prompt does not include every original asset or implementation detail. Some examples need music, images, fonts, or additional scripts.

The checked-out repository contains Markdown, one JSON data file, LICENSE, and .gitignore. It does not ship the animations’ HTML/JS source or a runnable rendering application. Cloning it downloads reference material rather than an installed batch-video generator.

Our cover adopts the README’s visual mosaic. These are collection previews, not works we regenerated or independently validated.

## What do 703, 418, and 100 count?

Our read-only audit pins revision 92aee2f586ac0715cb3cbcb6384834f98a33383d.

| Measure | Count | Meaning |
|---|---:|---|
| JSON records | 703 | Metadata entries, not independently reproduced outputs |
| Prompt Markdown files | 703 | A corresponding file for every entry |
| has_remake entries | 418 | Marked with a Skillry remake link, not necessarily open source |
| prompt_partial entries | 207 | Partial prompts or original-post descriptions |
| Entries not marked partial | 496 | A metadata label, not a guarantee of complete context |
| README featured examples | 100 | 58 motion, 16 explainers, 14 3D, 12 interactive |

The complete JSON categories contain 369 motion entries, 116 explainers, 117 3D scenes, and 101 interactive works. These differ from the README’s featured counts.

The 285 entries without a remake flag have empty skillry_url fields. Those are optional metadata, not automatically broken links. All 703 slugs are unique and have corresponding files. Prompt text matches between JSON and Markdown after newline normalization and extraction of the outer text block.

This establishes structural consistency, not universal link availability, model attribution, or one-shot reproducibility. Third-party mirrors can also represent different snapshots and counts.

![Little M separates collection entries, partial prompts, and external remake links](../../assets/images/awesome-opus-videos-code-animation-guide-fig-01.png)

## Why learn code-rendered video?

Product motion, process explainers, data visualization, and small interactive scenes often benefit from explicit parameters: positions, timing, duration, and movement. A local edit can adjust one part without regenerating every visual asset.

The approach has limits. Photographic scenes, human performance, and extensive asset production may require other tools. A recorded interactive demo is not proof that the underlying game’s logic, networking, or performance is production-ready.

Use the collection as a vocabulary for visual requirements. Its selected popular outputs lack the denominator of failed attempts and therefore cannot establish an average model success rate.

## What do the strongest prompts specify?

The twoclipping-402193 example asks for inputs before implementation, organizes UI changes against a beat structure, and inspects frames before full rendering. It combines art direction, technical structure, and acceptance order.

The fleyta88-443662 entry specifies timing and stagger intervals, followed by frame inspection and focused repairs. The 0xkarmi-129839 text discusses frame-indexed drawing, encoding, and loop-seam checks. Some text under Prompt includes narrative about the original post, so it still needs interpretation before becoming an executable task.

The common lesson is to replace vague requests for polished motion with observable requirements: what appears, when, which inputs are needed, how the result is delivered, and what counts as failure.

For scientific explainers, verify facts, formulas, and units first. Attractive particle motion is not evidence that an implementation solves the named physical equations.

## How can animation support frame-by-frame inspection?

A useful interface is seek(t): supply a time and display the corresponding scene. This makes intermediate frames, partial re-renders, and overlap debugging easier than relying entirely on wall-clock progression and accumulated state.

The interface alone does not guarantee determinism. Random systems need seeds; simulations need fixed steps or cached states; fonts and images must finish loading. Otherwise, the same t can still produce different pixels.

A 12-second video at 30 fps normally encodes 360 frames at times 0 through 359/30 seconds. An additional t=12 frame can be compared with t=0 to inspect a seamless loop. Do not automatically encode both identical endpoint frames into the loop.

The collection supplies relevant ideas, not a common implementation. We did not execute the creators’ animations or verify pixel-level determinism.

![Little M inspects fixed-time frames before encoding a frame sequence](../../assets/images/awesome-opus-videos-code-animation-guide-fig-02.png)

## How do you turn a reference into a deliverable?

Mycelium Protocol recommends starting with a small scope, such as a short three-card process explainer. This is our proposed workflow, not bundled repository automation:

1. Read the original post and partial-prompt flag. Inventory missing fonts, images, audio, aspect ratio, and export requirements. Decide on substitutes when necessary.
2. Write a storyboard and timing plan. Verify text, data, and each scene’s purpose before styling.
3. Ask the agent for a runnable page, animation entry point, dependency list, and resource paths. Validate static composition before transitions.
4. Inspect the beginning, end, and transition midpoints for overflow, occlusion, flashes, blank frames, and errors. Render the full sequence only after those checks.
5. Encode and watch the final file at normal speed. Check synchronization, cropping, and loop seams again; browser preview is a different acceptance step.

Our own practice brief asks for a 12-second, 1920×1080 three-step animation using local HTML, Canvas, and system fonts, without external assets. It requests a storyboard before source, a seek(t) interface, one heading and one explanatory line per card, and inspection at 0, 3, 6, 9, and 12 seconds. It also requests run instructions and a 360-frame export plan. We did not submit this brief to a model or generate its video.

Given an existing numbered sequence from 0000.png through 0359.png, a conventional encoding command is:

```bash
ffmpeg -framerate 30 -i frames/%04d.png \\
  -c:v libx264 -pix_fmt yuv420p output.mp4
```

This illustrates frame-to-video encoding only. It does not generate frames or add an audio track, and we did not run this export command during the review.

A vertical version should generally rearrange text and subjects rather than simply crop the horizontal composition. A moving webpage and a shareable video file need separate acceptance checks.

![Little M checks storyboard, browser page, keyframes, and final export in sequence](../../assets/images/awesome-opus-videos-code-animation-guide-fig-03.png)

## Does MIT cover every collected video?

The repository declares MIT, while its README explicitly credits videos and prompts to their creators and links original posts. Do not interpret the repository license as blanket commercial permission for every included song, person, brand, font, or image.

Learning a technique differs from republishing a finished work. Check input-asset and output-use conditions separately and retain required attribution. The README directs creators to open an issue for changes or removal.

## FAQ and verification scope

### Do I need to install an application to browse it?

GitHub displays the Markdown and JSON directly. We retrieved the companion gallery’s HTML, but did not play or interact with all remakes. Generation and export dependencies vary by prompt; there is no universally validated install-and-render command here.

### Can I try another coding model?

Yes, as an experiment. Tools, available context, and assets affect results. We conducted no cross-model comparison and cannot guarantee matching output or equivalent quality.

### Is this a ready-made model benchmark?

No. It can suggest tasks, but a benchmark needs cleaned inputs, resolved partial prompts, fixed assets and budgets, measurable criteria, and records of failures as well as successes.

Our audit covers counts, categories, slugs, file correspondence, optional URL fields, and prompt-text consistency. An initial auditor incorrectly required every remake URL and truncated one nested-fence prompt. We corrected the auditor to match the data structure without changing upstream content. We made no Opus calls, generated no videos, rebuilt no Skillry application, and did not validate the creators’ full production process.

## Primary sources and related reading

Repository: https://github.com/yihui-dev/awesome-opus5-5-videos
Data: https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/data/videos.json
UI motion example: https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/twoclipping-402193.md
Frame-checking example: https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/fleyta88-443662.md
Gallery: https://skillry.dev/ai-videos/opus-5-5
FFmpeg documentation: https://ffmpeg.org/ffmpeg.html

Related workflow: https://blog.mushroom.cv/blog/rea-video-nuphos-agent-workflow-review/
Image generation boundaries: https://blog.mushroom.cv/blog/moss-image-openmoss-layout-generation-review/
'''
d='awesome-opus5-5-videos收集用Claude Opus 5.5制作的代码动画案例。本文纠正仓库地址，核对703个条目、207条部分提示词与418个复刻标记，解释HTML、Canvas、SVG和Three.js出片方式，给出分镜、关键帧检查与导出流程，并区分源码、模型归因、更新时间和素材授权的边界。'
e='Review 703 Opus video entries, partial prompts, and remake links, with a practical workflow for code animation, frame inspection, export, and asset rights.'
while len(d)<150:d+='供创作者参考。'
while len(e)<150:e+=' Read on.'
assert 150<=len(d)<=160,len(d)
assert 150<=len(e)<=160,len(e)
f={'title':'Awesome Opus视频合集：从703个案例学代码动画','titleEn':'Awesome Opus Videos: A Guide to Code Animation','description':d,'descriptionEn':e,'wechatTitle':'Opus视频合集：703个案例怎么学','wechatDigest':'核对提示词与复刻数量，拆解代码动画从分镜、关键帧到视频导出的实践。','pubDate':'2026-11-09','updatedDate':'2026-11-09','category':'Tech-News','tags':['AI视频','Claude','代码动画','Canvas','Three.js','开源项目'],'heroImage':'../../assets/images/'+s+'-banner.jpg'}
fm='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in f.items())+'\n---\n\n'
a='\n---\n\n> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。\n'
b='\n---\n\n> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.\n'
Path('src/content/blog/'+s+'.md').write_text(fm+cn+a+'\n<!--EN-->\n\n'+en+b)
print(len(d),len(e))
