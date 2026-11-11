---
title: "Fable5.2做浏览器FPS：程序化资产、73轮迭代与缓存账单"
titleEn: "Fable 5.2 FPS Repro: Procedural Assets and Cost Audit"
description: "fable52-fps-repro公开四类浏览器游戏生成实验、五个HTML成品、提示词与缓存成本汇总。本文实际运行网页，检查Apple M4渲染、离线音频与调试辅助游戏状态，重算五行账单，说明73轮迭代和单文件背后的CDN依赖，并核对模型版本要求、订阅计费差异与脚本覆盖数据的细节，帮助读者先试玩再决定是否付费复现。"
descriptionEn: "Audit Fable 5.2 browser FPS artifacts, procedural assets and cached costs, with local Chrome checks, audio validation and practical reproduction limitations."
wechatTitle: "Fable5.2游戏复现：成品与成本核查"
wechatDigest: "实跑五个网页、核对缓存账单，拆解一句话做游戏背后的多轮工程闭环。"
pubDate: "2026-11-11"
updatedDate: "2026-11-11"
category: "Tech-News"
tags: ["Fable 5.2", "AI编程", "Three.js", "Web Audio", "提示词缓存"]
heroImage: "../../assets/images/fable52-fps-repro-procedural-game-cost-audit-banner.jpg"
lastPublishedAt: "2026-11-11T12:12:05Z"
---

fable52-fps-repro 用可试玩的网页、提示词和成本汇总，展示 AI 如何迭代出浏览器射击游戏。

项目由 `wquguru` 发布，采用 MIT 许可。仓库固定提交为 `a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961`，包含音效、材质、建模、完整 FPS 四类实验；音效多一组缓存对照，因此共有五个网页成品。

Mycelium Protocol 实际运行了五个页面，检查三维渲染、离线音频和部分游戏状态，并重算了五行账单。它适合研究“AI 编程怎样完成一个可见、可测的小作品”，其中的成品、生成过程和成本证据要分别看。

## “一句话做游戏”，实际上发生了什么？

作者说项目受 Saltline 展示启发，自己生成的完整游戏名为 SUBLEVEL 07，仓库不包含 Saltline 源码。前三项实验拆开研究音效、材质和模型，第四项再将它们组合进一个小关卡。

所谓“一句话”，指人给一次主要创作需求。实际输入还附有单文件与 CDN 等环境要求，以及允许浏览器截图、检查渲染器、离线测音频的系统指令。随后 Claude Code 多轮读文件、写代码、运行检查并修改。

作者记录完整 FPS 用了73轮、2,446秒，约40.8分钟。由此可见，它不是一次 API 返回就完成了游戏，而是一次需求驱动的长任务循环。累计661万输入 token 也不是一个661万上下文窗口，里面包含多轮重复读取与缓存读取。

![小M拿着一次需求卡，在写代码、浏览器检查和修改之间循环推进](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-01.png)

## 四类实验分别能学到什么？

| 实验 | 核心内容 | 阅读重点 |
|---|---|---|
| 01 音效 | Web Audio 合成枪声、换弹、脚步、雨雷和配乐 | 声音如何由振荡器、噪声和包络构造 |
| 02 材质 | 潮湿混凝土、锈蚀集装箱、金属和木托盘 | 数学噪声、着色器与 Canvas 纹理 |
| 03 模型 | 岸桥、货船、步枪和码头场景 | 几何体如何拼接成可识别物体 |
| 04 FPS | 地下变电站、三波无人机、开火换弹与结算 | 场景、音效和状态机怎样联动 |

这里的“纯代码生成资产”，主要是把规则写进浏览器程序：纹理在运行时计算或绘制，模型由几何体组成，音效由 Web Audio 合成。试玩时不会为每一帧调用大模型，也不需要在本机运行 Fable。

完整游戏 HTML 为130,777字节，约131KB。这个大小不包含从 CDN 加载的 Three.js 及其模块，也不等于整个游戏的网络传输量或运行内存。

我们观察到材质、建模和 FPS 页面从 `cdn.jsdelivr.net` 请求 JavaScript；两个音效台在本次加载中没有外部请求。因此，“单文件成品”与“完全离线、零依赖”要分开理解。

## 为什么小场景也能显得很有质感？

FPS 的画面由受控的小空间撑起来：工业构件、重复箱体、灯光、雾、粒子、枪口效果与后处理互相强化。源码包含泛光、环境遮蔽，以及通过镜像相机额外渲染地面的反射。

这种地面反射不是给场景中的每一个物体都计算通用光线追踪。代码还提供不同画质等级，并会在持续帧时间偏高时降低内部渲染比例。效果和负载都要在具体画质与设备条件下判断。

![小M把几何、纹理与声音三种规则装进同一个浏览器小场景](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-02.png)

它的经验是约束范围，而不是堆叠功能。一个狭窄关卡允许重复使用资产，围绕几种材质和灯光反复打磨。把它外推成开放世界、多人联机或成熟商业游戏，还缺地图工具、网络同步、内容生产与长期测试。

## 我们实际跑通了哪些检查？

本次使用 Chrome 157、960×540视口运行五个页面。三维页面报告 `ANGLE Metal Renderer: Apple M4`，没有使用 SwiftShader。五页均未出现未捕获的 JavaScript 异常，场景截图也做了人工检查。

通过 FPS 调试接口进行的功能检查确认：移动后位置变化，开火使弹匣从30降到29，换弹恢复到30并减少备用弹药。随后通过调试接口清除目标，观察到三波推进和胜利状态；通过伤害接口验证了死亡结算。

这里必须说明测试边界：清除目标使用了 `__dbg.kill`，并维持测试角色血量，不是靠正常瞄准打通13架无人机。我们验证的是状态转换，不能把它写成真实战斗通关或难度评测。仓库录屏脚本同样使用调试接口逐帧推进，并会抬高血量，观看动图时应知道这一点。

两个音效台各检查14类声音；5分钟版还运行混合场景检查，完整 FPS 运行20项离线音频检查。本次结果未发现削波；两个音效台的采样检查也未发现 NaN。离线测量不等于听感好，我们没有做人耳逐项试听。

我们没有测帧率、首帧耗时或显存，也没有复现模型生成过程。README 中 M2 Pro 约120fps 是作者对建模演示的报告，不能作为本次测试或所有页面的性能结论。

## $15.96 的账单，能核实到哪一步？

作者说明使用的是订阅额度，表中是按 API 价格折算的成本，并非实际额外支付这些美元。我们核对2026年11月11日 Anthropic 官方价格页，仓库采用的每百万 token 单价相符：

| 类别 | 美元/百万token |
|---|---:|
| 普通输入 | 8 |
| 5分钟缓存写入 | 10 |
| 1小时缓存写入 | 16 |
| 缓存读取 | 0.20 |
| 输出 | 40 |

使用公开 TSV 的各类 token 计数重算，五行四舍五入后的金额均与表格一致。其中完整 FPS 为：

- 6,606,366累计输入 token，含6,003,260缓存读取，命中率约90.9%。
- 192,947输出 token，折算成本15.96美元。
- 若同样数量的输入全部按普通输入计价，算术对照为60.57美元。

最后一项是固定已观察 token 数量的反事实估算，不是另跑一次无缓存实验所得账单。原始 `runs/*.json` 被 `.gitignore` 排除，没有随仓库发布；我们能核验聚合数字与公式，不能重放每次模型调用或验证真实账户扣款。

![小M把普通输入、缓存读写与输出分开称量，旁边放着折算账单](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-03.png)

缓存命中率分母是输入总量，输出另外计费。音效对照里，1小时组折算6.97美元，5分钟组为4.66美元；两次运行的未缓存输入和输出数量也不同，每组又只跑一次，不能据此宣布某种 TTL 总是更贵或更省。

另外，不同订阅套餐对 Fable 的额度和 usage credits 规则不同。应按自己账号与官方现行说明确认，不能把作者“订阅额度内”的经历理解成所有订阅都不产生额外费用。

## 怎样先试玩，再决定是否复现生成？

现成成品可直接打开作者的演示页：

```text
https://wquguru.github.io/fable52-fps-repro/
```

本地查看不需要模型账号：

```bash
git clone https://github.com/wquguru/fable52-fps-repro.git
cd fable52-fps-repro
python3 -m http.server 8080 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8080/demos/04-fps/`。桌面键鼠操作是主要交互方式；Three.js 演示需要能访问 CDN，断网复用需先将相关模块本地化。

如果要重新生成，才需要 Claude Code、对应模型权限，以及截图自检使用的 `agent-browser` 和 Chrome。当前官方帮助页要求 Fable5.2 使用 Claude Code 2.1.321及以上，README 中的2.1.242门槛偏低；作者实际记录的2.1.322满足要求。

下面是会消耗模型额度的可选命令示例，本次没有执行：

```bash
zsh scripts/run.sh 04-fps prompts/04-fps.md 1h 20 \
  prompts/builder_system_04.md
```

其中20传给 `--max-budget-usd`，具体预算行为仍以当前 CLI 与账号计费规则为准。准备复现时建议用独立工作目录，核对父目录及全局指令的影响；作者也记录过目录名和写作规范进入游戏生成上下文的情况。

## 两个脚本细节，避免误读复现结果

`metrics.py` 会从本地 `runs/*.json` 重新生成 `data/metrics.tsv`。我们在临时副本验证，干净克隆没有这些日志时运行它，会将原汇总表覆盖成只有表头。先保留发布数据，只有生成了自己的运行日志后再做汇总。

`run.sh` 会把模型进程退出码写进 `runs/wall.log`，但最后执行的是 `echo | tee`。我们在临时目录用假模型命令返回7，实际观察到外层脚本仍返回0，而日志记录7。仅看脚本返回0，不足以认定任务完成；还要检查日志、结果 JSON 和实际 HTML。

Mycelium Protocol 的判断是，这个项目最值得学的是可见反馈闭环：给任务限定范围，生成程序化资产，用浏览器与音频数据检查，再对照账单解释成本。公开作品能帮助别人审查效果，原始日志、重复实验和统一性能测试则是下一步证据。

相关技能工作流也可参考：https://blog.mushroom.cv/blog/jane-street-socratic-tutor-agent-skills-guide/ 。两类项目共同的启发是给结论配上可检查的证据，而不是只接受模型的完成汇报。

## 常见问题

### 这是Saltline的源码吗？

作者明确说明是受其启发的独立实验。完整游戏名为SUBLEVEL 07，仓库不包含Saltline代码。

### 试玩需要购买模型服务吗？

运行已发布的HTML不调用生成模型。重新生成才需要模型账号和额度，三维网页仍依赖浏览器与Three.js模块。

### 131KB是否表示完全离线？

不是。它是完整FPS的HTML大小；Three.js和后处理模块从CDN加载，网络依赖需要另行处理。

### 这次是否验证了正常战斗通关和120fps？

没有。我们检查了调试辅助状态转换、基本操作和离线音频，未做人类玩法通关或帧率基准测试。

## 一手资料

- 仓库：https://github.com/wquguru/fable52-fps-repro
- 固定源码：https://github.com/wquguru/fable52-fps-repro/tree/a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961
- 在线演示：https://wquguru.github.io/fable52-fps-repro/
- 作者账单：https://github.com/wquguru/fable52-fps-repro/blob/a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961/data/metrics.tsv
- 官方API价格：https://platform.claude.com/docs/en/about-claude/pricing
- Fable使用条件：https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- CLI参数：https://code.claude.com/docs/en/cli-reference

封面采用仓库提供的游戏截图，按MIT许可保留来源；正文插图为Mycelium Protocol原创。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

fable52-fps-repro publishes playable artifacts, prompts and cost summaries showing how an AI coding loop can produce a small browser shooter.

The MIT-licensed repository by `wquguru`, inspected at commit `a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961`, contains four experiment categories and five HTML artifacts, including an audio caching comparison.

Mycelium Protocol ran all five pages, checked rendering, offline audio and selected game behavior, and recomputed the five published cost rows. Artifacts, generation history and billing evidence deserve separate assessment.

## What does “one prompt” mean here?

The author describes Saltline as the inspiration, while the independently generated game is SUBLEVEL 07. This repository does not contain Saltline's source.

“One prompt” means one principal human creative request. The input also includes environment constraints and system instructions permitting browser screenshots, renderer inspection and offline audio checks. Claude Code then repeatedly reads, writes, tests and revises files.

The author reports 73 turns and 2,446 seconds, roughly 40.8 minutes, for the FPS. This is a long-running agent loop rather than one API response. Its 6.6 million cumulative input tokens include repeated and cached reads, not a 6.6-million-token context window.

![Little M carries one task request around a write, inspect and revise loop](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-01.png)

## What do the four experiments contain?

| Experiment | Content | Useful implementation topic |
|---|---|---|
| Audio | Synthesized shots, reloads, footsteps, weather and music | Oscillators, noise and envelopes |
| Materials | Wet concrete, rusted containers, metals and wood | Mathematical noise, shaders and Canvas textures |
| Models | Crane, ship, rifle and harbor | Composing recognizable objects from geometry |
| FPS | Substation, drone waves, combat and outcomes | Connecting assets to interaction and state |

Procedural assets are produced by browser code. Playing the finished artifact does not invoke a model for each frame or require local Fable inference.

The FPS HTML is 130,777 bytes, approximately 131KB. That excludes the Three.js modules fetched from a CDN and is not total download size or runtime memory. We observed external JavaScript requests to `cdn.jsdelivr.net` from the three 3D demos; the two audio pages made no external requests during this run.

## How does a small scene achieve its appearance?

A constrained industrial environment combines repeated structures, a few materials, lighting, fog, particles and postprocessing. The FPS uses bloom, ambient occlusion and an additional mirrored-camera render for floor reflections.

This floor-reflection technique is not general ray tracing for every object. Quality levels and automatic internal-resolution reduction also affect appearance and load. Evaluate the result under explicit device and quality settings.

![Little M assembles geometry, material rules and synthesized audio into a compact browser scene](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-02.png)

The practical lesson is scope control. Reusable assets and a tiny level make iteration tractable. Open-world content, multiplayer, production tooling and long-term testing remain separate engineering work.

## What did we actually check?

We ran Chrome 157 at 960×540. The 3D demos reported Apple M4 through ANGLE Metal, rather than SwiftShader. All five pages loaded without uncaught JavaScript exceptions, and screenshots received manual review.

Using the FPS debug hooks, checks confirmed movement, ammunition dropping from 30 to 29 on firing, and reloading to 30 while consuming reserve ammunition. Debug-assisted target removal advanced all three waves to victory; the damage hook reached the death outcome.

The scope matters: we used `__dbg.kill` and maintained the test character's health. This was state-transition validation, not an ordinary aiming-based completion of all 13 drones. The repository's recording script also drives debug steps and raises health, which affects how its demonstration footage should be interpreted.

Both audio stations exercised 14 sound types. We also ran the five-minute version's mixed scene and 20 offline audio cases in the FPS. No clipping was reported in these checks, and the audio-station sample checks reported no NaNs. We did not perform a human listening assessment.

We measured no FPS, first-frame latency or VRAM usage, and did not regenerate the artifacts. The README's approximately 120fps on M2 Pro is the author's report for the modeling demo, not our benchmark or a guarantee for every page.

## What can the $15.96 cost claim establish?

The author used subscription capacity and reports API-equivalent costs, not those amounts as additional cash charges. On November 11, 2026, the official pricing page matched the rates used by the repository:

| Category | USD per million tokens |
|---|---:|
| Ordinary input | 8 |
| Five-minute cache writes | 10 |
| One-hour cache writes | 16 |
| Cache reads | 0.20 |
| Output | 40 |

Recomputing all five aggregate rows reproduced their rounded amounts. The FPS row contains 6,606,366 cumulative input tokens, including 6,003,260 cache reads, for approximately 90.9% input cache hits. Its 192,947 output tokens contribute to a $15.96 equivalent total.

Charging the same observed input volume entirely at ordinary input rates produces $60.57. This is a fixed-volume counterfactual, not a separately executed uncached run. Raw `runs/*.json` files are excluded and unpublished; the aggregates support arithmetic checks, not reconstruction of every model call or verification of actual account debits.

![Little M weighs ordinary input, cache operations and output separately before totaling an equivalent bill](../../assets/images/fable52-fps-repro-procedural-game-cost-audit-fig-03.png)

The hit-rate denominator is input volume; output is billed separately. The one-hour audio run costs $6.97 equivalent versus $4.66 for the five-minute run, but uncached input and output volumes also differ. One run per condition cannot establish that either TTL is consistently cheaper.

Subscription inclusion and usage-credit rules depend on the plan. Check the current official terms for your account rather than assuming the author's subscription experience means every subscription avoids extra charges.

## How can you try the result before regenerating it?

The author's gallery is available at:

```text
https://wquguru.github.io/fable52-fps-repro/
```

Local viewing does not require a model account:

```bash
git clone https://github.com/wquguru/fable52-fps-repro.git
cd fable52-fps-repro
python3 -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/demos/04-fps/`. Desktop keyboard and mouse are the primary controls. Offline use of the 3D demos requires localizing their CDN dependencies.

Regeneration additionally needs Claude Code, model access, and `agent-browser` with Chrome for browser self-inspection. The current official help page requires Claude Code 2.1.321 or newer for Fable5.2, exceeding the README's 2.1.242 minimum. The author's recorded 2.1.322 satisfies it.

The following optional example consumes model capacity; we did not run it:

```bash
zsh scripts/run.sh 04-fps prompts/04-fps.md 1h 20 \
  prompts/builder_system_04.md
```

The value 20 is passed to `--max-budget-usd`; interpret its behavior alongside current CLI and account billing rules. Use an independent working directory and inspect inherited instructions. The author documents earlier experiments incorporating their directory name and unrelated writing rules into generation context.

## Which script details affect reproducibility?

`metrics.py` rewrites `data/metrics.tsv` from local `runs/*.json`. In an isolated copy, running it without those logs replaced the published table with a header only. Preserve the original aggregates and summarize only after producing your own logs.

`run.sh` records the model subprocess exit status in `runs/wall.log`, but finishes with `echo | tee`. In an isolated directory, a fake model command exiting 7 produced wrapper status 0 while the log retained 7. A zero wrapper status alone does not establish completion; inspect the log, result JSON and produced HTML.

Our assessment is that the useful contribution is an inspectable feedback loop: constrain scope, generate procedural assets, check browser and audio outputs, and explain costs with explicit accounting. Raw logs, repeated runs and controlled performance tests would strengthen the evidence further.

Related workflow context: https://blog.mushroom.cv/blog/jane-street-socratic-tutor-agent-skills-guide/ . In both cases, evidence should accompany a completion claim.

## FAQ

### Is this Saltline's source code?

The author describes independent experiments inspired by Saltline. The complete game here is SUBLEVEL 07; Saltline source is not included.

### Does playing require a model subscription?

The shipped HTML does not call a generation model. Regenerating it requires access and capacity; the 3D artifacts still depend on browser and Three.js modules.

### Does 131KB mean fully offline?

It describes the FPS HTML alone. Three.js and postprocessing modules load from a CDN until those dependencies are localized.

### Did we verify normal combat completion and 120fps?

No. We checked debug-assisted transitions, basic interactions and offline audio, without an ordinary playthrough or frame-rate benchmark.

## Primary sources

- Repository: https://github.com/wquguru/fable52-fps-repro
- Inspected source: https://github.com/wquguru/fable52-fps-repro/tree/a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961
- Live demos: https://wquguru.github.io/fable52-fps-repro/
- Published metrics: https://github.com/wquguru/fable52-fps-repro/blob/a7e1df3ce32eb2bb05e23ae457fe5fe2bffab961/data/metrics.tsv
- Official API pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Fable access requirements: https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan
- CLI flags: https://code.claude.com/docs/en/cli-reference

The cover adopts the project's screenshot with MIT source attribution. Body illustrations are original Mycelium Protocol work.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
