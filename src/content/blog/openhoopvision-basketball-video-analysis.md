---
title: "OpenHoopVision：把篮球录像变成轨迹和事件数据"
titleEn: "OpenHoopVision: Basketball Video to Tracks and Events"
description: "OpenHoopVision 面向业余和青少年篮球录像，将检测、跟踪、球员身份、球场映射和事件推断连接起来，输出标注视频与JSONL。本文核对官方源码与作者报告的投篮指标，完成11项合成计分检查，说明两分兜底、固定球场几何、Git LFS权重及CPU路径的使用边界，并给教练与开发者提供可复核的试用流程。"
descriptionEn: "Explore OpenHoopVision's basketball video pipeline, author-reported shot metrics, structured exports, and verified scoring, court geometry and setup limits."
wechatTitle: "OpenHoopVision：篮球录像变数据"
wechatDigest: "篮球录像可转成轨迹和事件记录，使用时需核对身份、投篮结果、球场位置与两分兜底标记。"
pubDate: "2026-10-13"
updatedDate: "2026-10-13"
category: "Tech-News"
tags: ["OpenHoopVision", "Computer Vision", "Basketball", "Video Analysis", "Tracking", "Open Source"]
heroImage: "../../assets/images/openhoopvision-basketball-video-analysis-banner.jpg"
---

OpenHoopVision 是把篮球录像转成标注视频和结构化比赛数据的项目，面向业余与青少年比赛，帮助教练和开发者进一步复盘。

它由 feifeifei85 维护。我们固定在 2026 年 10 月 13 日读取的提交 `9c000659a7d34ded894db90161c27cc0b55bb745`，项目版本为 0.1.0。作者给出了投篮检测评估，但本次没有复跑模型或真实比赛；我们核对实现，并完成了 11 项局部合成计分检查。

官方仓库：https://github.com/feifeifei85/OpenHoopVision

## 从一段录像，能得到什么？

流水线逐帧检测球员、球和篮筐等对象，关联姿态与局部轨迹，再通过外观 ReID、球衣号码 OCR 和队伍颜色线索维持身份。球场关键点用于位置映射，球的动作与控球变化用于事件推断。

| 阶段 | 输入与作用 | 输出要核对的内容 |
| --- | --- | --- |
| 检测与姿态 | 找球员、球、篮筐与关键点 | 漏检、遮挡和低分辨率影响 |
| 跟踪与身份 | 关联轨迹、外观与球衣号码 | 同一球员是否换了 ID |
| 队伍与球场 | 队伍颜色和球场坐标 | 队伍归属与几何是否可靠 |
| 事件推断 | 结合球轨迹和控球变化 | 投篮结果、传球接收者等 |
| 导出 | 标注视频和逐帧 JSONL | 保留时间、来源与不确定状态 |

当前 README 列出投篮、运球、传球、篮板、失误和抢断六类事件；助攻、盖帽和犯规尚不支持。自动精彩片段工具仍被列为后续探索，不能当成已经交付的功能。

视频适合直接查看。JSONL 更适合后续计算：每帧使用 `basketball_frame_v2` 结构，包含帧号、时间戳、球员、持球者、球与篮筐特征、原始检测和事件。首条记录还包含运行配置，事件使用帧区间及结果等字段。

这让复盘可以从“回看整场”转向“定位一个事件、查看附近帧、检查原始依据”。轨迹和事件是推断结果，后续分析应继续保留它们的来源，而不是只拿最终记分牌做统计。

![小M把篮球胶片送入观察装置，同时输出供人查看的标注帧和供程序使用的结构化事件卡片](../../assets/images/openhoopvision-basketball-video-analysis-fig-01.png)

## 作者的指标，证明了哪一部分？

作者 README 报告了三组结果：

| 任务 | 作者报告的指标 | 评估口径 |
| --- | --- | --- |
| RF-DETR 篮球对象检测 | mAP@0.5 84.9%；mAP@0.5:0.95 62.3% | 自行整理标注数据的验证划分 |
| YOLO26s 球场姿态 | mAP@0.5 96.8%；mAP@0.5:0.95 81.1% | 球场关键点任务 |
| 端到端投篮 | Precision 85.51%；Recall 83.10%；F1 84.29% | 7 段视频、71 次投篮 |

投篮事件按时间 IoU ≥ 0.5 一对一匹配，其中一份不完整标注使用了 ±0.5 秒开始时间容差。作者另报告队伍归属准确率为 79.66%，即 47/59；不同指标的分母与任务应分别读。

这些是作者报告，不是我们的实测。球场关键点的 mAP、对象检测的 mAP 和事件 F1 也不是同一把尺，不能把最高的一个百分比概括成“整套系统准确率”。7 段视频还不能覆盖所有机位、遮挡和场地条件。

## 球进了，为什么还要检查两分兜底？

投篮模块可以保留 `made`、`miss` 或 `unknown`。对于进球，只有球场位置可靠时才按坐标判断两分或三分；否则会给两分，并标记 `points_source="two_point_fallback"`。

这个标记很有用，因为它让下游区分“由球场位置判断”与“缺少可靠位置时采用兜底”。但兜底值本身不会证明这次投篮是两分。自动汇总之前，应把这类事件加入复核列表。

我们还查看了 `tracking/court.py`：代码将路径称为 NBA court，固定长宽为 28.65 × 15.24 米，三分半径为 7.24 米。因此，项目面向青少年篮球的目标，不等于默认几何已适配任意学校或地方赛事场地。先核对球场标线和映射，再评价两分、三分分类，才有意义。

![小M将带有两分兜底标签和不确定标记的投篮卡放入人工复核托盘，旁边的球场尺提醒核对实际场地几何](../../assets/images/openhoopvision-basketball-video-analysis-fig-02.png)

几何与计分源码：https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/tracking/court.py

投篮结果源码：https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/events/shot.py

## 我们实际做了哪些本地检查？

Mycelium Protocol 直接调用固定版本的 `shot_point_value()` 与 `apply_shot_events_to_scoreboard()`，使用合成球场坐标和事件字典，完成 **11 项检查，11 项通过**。

检查覆盖篮下两分、弧外和底角三分、三分线附近保持不确定、缺失与非法坐标，以及未命中不加分。同一个已处理的进球事件对象重复传入不会重复累加；队伍未知时保留待处理事件，后续出现队伍信息可以继续记分。

这项“同一对象”检查不等于证明跨进程、重新导入记录时的全局幂等。我们也没有运行目标检测、ReID、球衣 OCR 或真实视频事件推断，不能据此声称复现了 84.29% F1、身份匹配质量或端到端处理速度。

一个值得保留的工程特点是，系统把状态与依据放在记录中。对教练而言，未知结果或兜底结果需要回看片段；对开发者而言，这些字段使问题更容易被定位。

计分源码：https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/events/scoring.py

## 安装前，最容易误会什么？

官方要求 Python 3.10+、FFmpeg，以及五组模型 checkpoint。程序按指定路径读取权重，不会自动把缺失权重下载好。

本次普通克隆后的五个权重文件都只有 132–134 字节，内容是 Git LFS 指针，不能作为模型文件加载。指针声明的实际文件体积合计约 290 MB；这不包括 Python、PyTorch 和其他依赖。要先按仓库文件配置取得实际权重，再运行分析。

![小M用放大镜检查小小的 Git LFS 指针信封，旁边是封好的实际权重箱；合成计分卡单独检查，真实比赛胶片仍未运行](../../assets/images/openhoopvision-basketball-video-analysis-fig-03.png)

```bash
python -m pip install -e .
python main.py --video your_game.mp4
```

命令是官方使用方式，本次没有执行整段比赛推理。作者建议用 NVIDIA GPU；源码在 CUDA 不可用时选择 CPU，所检查的分支没有自动切到 Apple MPS 的路径。因此，在 Apple Silicon 上安装成功，也不能直接推断会获得 Metal 加速。

`requirements.lock` 是作者验证的 CUDA 13.0 环境直接依赖版本，不能把它当成所有系统都能照搬的环境证明。标注视频需要 FFmpeg 输出 H.264，默认输出视频与 JSONL 位于运行目录的上一级，也应留意自己指定的输出位置。

README 声明原创代码和项目训练产物采用 Apache-2.0，同时明确第三方模型、代码与依赖各自遵循许可，包括 Ultralytics 的 AGPL-3.0。本次固定文件树未见独立 LICENSE 文件；对再分发与集成，不能只看一个 Apache-2.0 声明便跳过依赖和权重来源核对。

Ultralytics 许可说明：https://www.ultralytics.com/license

## 教练和开发者怎样试用更有效？

先选一段可合法使用、画面清楚、能看到球和篮筐的短录像，人工记下投篮、结果和队伍，再比较输出事件。保留漏检、误检、未知结果与兜底值，不要只挑最好看的标注画面。

接着分别检查：球员 ID 是否稳定，镜头切换是否破坏跟踪，球场位置是否符合实际标线，哪些分值来自兜底。最终展示给队伍的统计，应能追溯到具体帧区间。

我们的判断是，它提供了一个值得继续扩展的录像数据接口：视频给人看，逐帧记录给程序用。实际试用的重点应是发现本队录像的失败模式，并建立复核流程，逐步把可用的分析接上去。

如果更关心视频资产与编辑工作流，可继续阅读本站 Seal 分析：https://blog.mushroom.cv/blog/seal-ai-video-workbench/

## 常见问题

### 是实时比赛分析吗？

当前 README 描述的是对录制视频逐帧离线分析。没有本次实测的实时帧率，不能宣称实时部署已经验证。

### 标注视频上的比分就是确定的比赛比分吗？

不一定。事件结果、队伍归属和球场位置都可能不可靠，进球还可能使用两分兜底；应检查来源标记并回看相关片段。

### Mac 会自动使用 MPS 吗？

所检查的 runner 根据 CUDA 是否可用选择 CUDA 或 CPU，没有自动 MPS 分支。本文没有做完整 Mac 推理速度测试。

### 本次验证覆盖模型精度吗？

没有。11 项合成检查覆盖计分函数的局部逻辑，作者的真实视频指标单独列出，未独立复现。

## 一手来源

- 官方仓库与说明：https://github.com/feifeifei85/OpenHoopVision
- 固定源码：https://github.com/feifeifei85/OpenHoopVision/tree/9c000659a7d34ded894db90161c27cc0b55bb745
- 中文说明：https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/README_zh.md
- 运行设备选择：https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/pipeline/video_analysis.py

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

OpenHoopVision turns recorded basketball footage into annotated video and structured game data, targeting amateur and youth games for further review by coaches and developers.

Maintained by feifeifei85, the source we inspected on October 13, 2026 is pinned to `9c000659a7d34ded894db90161c27cc0b55bb745`, package version 0.1.0. The author reports shot-detection metrics. We did not rerun the models or real-game evaluation; our local verification consisted of 11 synthetic scoring checks and source inspection.

Official repository: https://github.com/feifeifei85/OpenHoopVision

## What comes out of a recorded game?

The pipeline detects players, the ball and rim, associates pose and local tracks, then uses appearance ReID, jersey OCR and team-color evidence to maintain identity. Court keypoints support mapping; ball actions and possession changes support event inference.

| Stage | Role | What requires review |
| --- | --- | --- |
| Detection and pose | Find objects and keypoints | Occlusion, missed detections, low resolution |
| Tracking and identity | Associate tracks, appearance and jersey numbers | Whether a player changes identity |
| Teams and court | Team labels and court coordinates | Attribution and geometric reliability |
| Events | Infer actions and possession changes | Shot outcomes and other event fields |
| Export | Annotated video and frame JSONL | Timing, evidence and uncertainty |

The README lists shots, dribbles, passes, rebounds, turnovers and steals. Assists, blocks and fouls are unsupported. Automatic highlights remain a future exploration, not a shipped feature.

Each JSONL frame uses `basketball_frame_v2`, with frame number, timestamp, players, holder, ball/rim features, raw detections and events. The first record includes run configuration. Events carry frame intervals and event-specific fields.

This supports locating a candidate event, inspecting nearby frames and checking the underlying evidence. Derived tracks and events should retain that provenance in downstream statistics.

![Xiao-M feeds basketball film into an observation device that produces an annotated frame for people and structured event cards for programs](../../assets/images/openhoopvision-basketball-video-analysis-fig-01.png)

## What do the reported metrics establish?

| Task | Author-reported result | Evaluation scope |
| --- | --- | --- |
| RF-DETR basketball detection | mAP@0.5 84.9%; mAP@0.5:0.95 62.3% | In-house validation split |
| YOLO26s court pose | mAP@0.5 96.8%; mAP@0.5:0.95 81.1% | Court keypoint task |
| End-to-end shots | Precision 85.51%; recall 83.10%; F1 84.29% | 71 shots across seven videos |

Shot events are matched one-to-one at temporal IoU ≥ 0.5, with a ±0.5-second onset tolerance for one incomplete annotation. Team attribution is reported separately as 79.66%, or 47/59. Different denominators and tasks should remain separate.

These are the author's results, not our measurements. Detection mAP, pose mAP and event F1 cannot be collapsed into one overall system accuracy. Seven videos also cannot cover every camera, court and occlusion condition.

## Why inspect the two-point fallback?

Shots can retain `made`, `miss` or `unknown`. For made shots, reliable court coordinates determine two versus three points. Otherwise, the system assigns two and records `points_source="two_point_fallback"`.

The flag distinguishes geometric classification from a default. It does not establish that the basket was actually worth two points. Downstream summaries should queue those events for review.

In `tracking/court.py`, the source names its paths NBA court and fixes dimensions at 28.65 × 15.24 meters, with a 7.24-meter three-point radius. A youth-basketball audience does not establish that this geometry fits every school or local competition. Verify the markings and mapping before assessing point classification.

![Xiao-M places an uncertain shot card with a two-point fallback tag in a manual review tray beside a ruler for checking actual court geometry](../../assets/images/openhoopvision-basketball-video-analysis-fig-02.png)

Court geometry: https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/tracking/court.py

Shot outcomes: https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/events/shot.py

## What did we verify locally?

Mycelium Protocol called the pinned `shot_point_value()` and `apply_shot_events_to_scoreboard()` with synthetic coordinates and event dictionaries. **All 11 checks passed.**

They cover two-point and three-point positions, uncertainty near the arc, missing/invalid coordinates and misses adding no score. Reusing the same processed made-shot object does not add points twice. An event with an unknown team stays pending and can be applied after later team evidence.

The same-object check is not proof of global idempotency across processes or reimported records. We did not run detection, ReID, OCR or real-video event inference, and did not reproduce F1, identity quality or end-to-end throughput.

Retaining state and evidence in records is useful: coaches can revisit uncertain clips, while developers can locate which stage produced a questionable result.

Scoring source: https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/events/scoring.py

## What should be checked before installation?

The documented requirements are Python 3.10+, FFmpeg and five checkpoint files. The program reads configured paths rather than automatically downloading missing models.

Our ordinary checkout contained only 132–134-byte Git LFS pointers for all five weights. They are not loadable checkpoints. Their declared actual sizes total roughly 290 MB, excluding Python, PyTorch and other dependencies. Obtain the real artifacts before analysis.

![Xiao-M inspects a tiny Git LFS pointer envelope beside a sealed box of actual weights, while synthetic scoring cards are checked separately from untouched game footage](../../assets/images/openhoopvision-basketball-video-analysis-fig-03.png)

```bash
python -m pip install -e .
python main.py --video your_game.mp4
```

These are the documented commands, not a full-game run we performed. The author recommends NVIDIA GPU processing. The inspected runner selects CPU when CUDA is unavailable; it does not automatically select Apple MPS. Installation success on Apple Silicon is therefore not evidence of Metal acceleration.

`requirements.lock` pins direct dependencies for the author's validated CUDA 13.0 environment, not every platform. H.264 output requires FFmpeg. Default video and JSONL outputs are one directory above the working project; inspect or explicitly set output paths.

The README declares original code and project-trained artifacts Apache-2.0, while third-party models, code and dependencies retain their own licenses, including Ultralytics AGPL-3.0. The pinned tree has no standalone LICENSE file. Integration and redistribution need the actual dependency and artifact provenance, not a blanket Apache-2.0 assumption.

Ultralytics licensing information: https://www.ultralytics.com/license

## How can coaches and developers evaluate it?

Use a short, legally usable clip with a visible ball and rim. Label shots, outcomes and teams manually, then compare events. Retain misses, false positives, unknowns and fallbacks rather than selecting only attractive annotated frames.

Check identity stability, camera-cut effects, court alignment and point-source flags separately. Statistics shown to a team should trace back to frame intervals.

Our assessment is that the project provides a useful interface for extending recorded-game analysis: video for people, frame records for programs. The practical next step is identifying failure modes in the team's own footage and establishing a review workflow.

For a related video workspace, see our Seal analysis: https://blog.mushroom.cv/blog/seal-ai-video-workbench/

## FAQ

### Is this validated real-time analysis?

The README describes offline processing of recorded video. We did not measure a real-time frame rate.

### Is the rendered score definitive?

No. Event results, team attribution and court mapping can be unreliable, and made shots can receive a two-point fallback. Inspect source flags and the relevant frames.

### Will Mac automatically use MPS?

The inspected runner selects CUDA or CPU, with no automatic MPS branch. We did not benchmark full Mac inference.

### Did our checks validate model accuracy?

No. The 11 checks cover local scoring logic. Author-reported real-video metrics are listed separately and were not independently reproduced.

## Primary sources

- Official repository: https://github.com/feifeifei85/OpenHoopVision
- Pinned source: https://github.com/feifeifei85/OpenHoopVision/tree/9c000659a7d34ded894db90161c27cc0b55bb745
- Chinese README: https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/README_zh.md
- Device selection: https://github.com/feifeifei85/OpenHoopVision/blob/9c000659a7d34ded894db90161c27cc0b55bb745/pipeline/video_analysis.py

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
