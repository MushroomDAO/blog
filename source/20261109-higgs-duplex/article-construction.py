from pathlib import Path
import json
s='higgs-realtime-duplex-open-weights-pricing-engineering'
cn='''Higgs Realtime Duplex 是李沐参与创立的 Boson AI 团队推出的全双工多模态模型。到 2026 年 11 月 9 日本次核查为止，没有找到官方公开的 Duplex 权重、蒸馏版或端侧精简版；官方公告仍把 Duplex API 列为即将开放、需要候补登记。

已经可以调用并公布价格的是 Higgs Realtime；可以下载的 Higgs TTS、STT 又是其他用途的模型。不能用旧产品的价格给 Duplex 报价，也不能把一个可下载的语音模块当成完整全双工模型的裁剪版。

这条素材还提到了 Mika 和 WorldForge。我们也核对了它们，但三个项目没有被官方资料证明属于同一套系统。本文先回答开源与收费，再拆解模型设计、可用代码和工程实现路径。

## 这是不是李沐开发的模型？

Boson AI 官方团队页将 Mu Li 列为联合创始人、CEO/CTO；Duplex 技术公告的贡献者名单也包含他。因此，称为“李沐所在团队的模型”有一手依据，称为“李沐一个人开发”则不准确。

官方公告发表于 11 月 5 日。它描述一个 45B 参数的 MoE 前台模型，在文字模型基础上继续训练约 2 万亿个文本、音频和视觉 token，并把对话、思考、工具调用和任务委派组织到同时进行的流里。

我们以这份技术文稿、官方价格表、开发文档、GitHub 与 Hugging Face 资源为主要依据。找到了所述李沐讲解视频的链接，但未成功获取视频正文或字幕，不声称完整观看了约 44 分钟的内容。

## 到底哪些开源，哪些只是可以调用？

| 资源 | 本次核查状态 | 能否当成 Duplex 精简版 |
|---|---|---|
| Higgs Realtime Duplex | 公告与演示公开，API 候补；官方 GitHub/HF 未找到对应权重 | 未发现官方 lite、蒸馏或量化权重 |
| Higgs Realtime API | 已有公开接入文档与报价 | 是现售实时语音服务，不应默认等同新 Duplex |
| Higgs TTS 3 4B | 可以下载权重，专门做语音生成 | 不是完整的听、看、说、调工具模型 |
| Higgs STT 模型 | 有公开权重，所查模型卡标注 Apache-2.0 | 做语音识别，不是 Duplex 裁剪版 |
| Higgs-Realtime-Tutorial | Apache-2.0 教学代码 | 是调用服务的客户端与示例，不是模型权重 |

本次获取的 Boson GitHub 组织清单有 16 个公开仓库，Hugging Face 模型清单有 12 项，未看到 Duplex checkpoint。这个结论有时间边界，只表示本次检查未找到，不能证明它未来不会发布。

还要注意权重许可：Higgs TTS 3 使用研究与非商业许可，许可证明确说明它不是开源许可证。产品嵌入、托管 API 等商业部署需要另行授权；创作者制作并发布包括变现内容的音频作品，则有带署名要求的 Creator Use Grant。不能只看到“可以下载”，就按 Apache-2.0 理解全部使用权。

旧 higgs-audio 代码仓库虽然是 Apache-2.0，也不能把这个代码许可覆盖到所有新模型权重。当前模型卡和对应 LICENSE 比旧 README 中的名称、预览免费标签更适合判断现状。

![小M分别核对Duplex、现售API和可下载语音模块](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-01.png)

## 如果不开源，现在如何收费？

先给最重要的边界：**目前核到的是现有 Higgs Realtime 的价格，不是 Duplex 的价格。** 官网价格页没有单列 Duplex 报价；它的最终价格和可用范围应以正式开放后的文档或商务回复为准。

本次官网快照的美元费率如下，税费另计。

| Higgs Realtime 项目 | 公布费率 |
|---|---:|
| 输入 token | 每百万 $0.75 |
| 缓存输入 token | 每百万 $0.25 |
| 输出 token | 每百万 $4.50 |
| 音频输入估算 | 每分钟 $0.0023 |
| 音频输出估算 | 每分钟 $0.014 |
| 启用转写时的输入 | 每分钟 $0.0025 |
| Memory Search 查询 | 每千次 $5 |

服务采用预充值、按使用量扣费。分钟数字是典型用量估算，实际按消耗的 token 计费，不应当成固定的通话包价。

只为理解数量级，如果输入音频按 60 分钟、输出按 20 分钟估算，两项相加约为 $0.418；若输入和输出都按 60 分钟，则约为 $0.978。这是依据官网估价做的算术，不是实测账单。历史上下文、缓存命中、转写、搜索、委派给其他模型等都会影响最终费用。

“有一张脸”还需要单独看。价格表给出的 Higgs Avatar 视频输出价为 640×480 或 480×640 每分钟 $0.07，640×640 每分钟 $0.09。不能直接认定实时会话、视频生成与未来 Duplex 都采用相同计费规则，更不能默认头像视频包含在语音输出的 $0.014 中。部署时还要核对相应会话报价、LiveKit 和后台工具费用。

## 它怎样同时听、看、说，还能后台做事？

### 160 毫秒是分块粒度，不是端到端延迟保证

官方把流按 160 毫秒划分。即使没有人说话，静音块也继续进入处理过程；模型可以在听到一部分话时开始推理，在输出语音的同时继续接收输入。

这是持续交互的设计，与仅在用户说完后依次跑 ASR、文本模型、TTS 的串行流程不同。旧 API 能被打断，也不自动说明它具有新 Duplex 的全部原生并行多模态能力。

从用户开口到听到第一段回复，仍包括采集、网络、排队、模型计算、音频解码和播放缓冲。工具或后台大模型还可能花数秒。不能把 160 毫秒写成所有请求的响应时间，更不能套用现售 Realtime 的约 700 毫秒宣传值当作 Duplex 实测。

### 前台模型自己思考，需要时才委派

45B MoE 前台模型不只是语音壳。按官方设计，它能够自己推理和调用工具；遇到难题时，再把共享上下文交给更大的后台模型，同时继续和人交谈。工具结果可以分段返回，前台不必每次等到整项任务结束才开口。

这要求工程里把“当前说到哪里”和“后台任务做到哪里”分开管理。用户打断一句话，不一定是在取消刚才的后台检索；停止播放语音，也不会回滚已经发出的邮件或订单。

### 用压缩的表示控制持续交互成本

官方描述每个输入块一个音频 token、输出两个音频 token；相机每六个块输入一帧，约为每 0.96 秒一帧。这里是模型接收视觉信息的节奏，不是宣称每秒处理几十张完整高清画面。

音视频流约占每分钟 2.6K token，加入思考、工具调用与结果后约为 2.6–5K。近期五分钟保留音视频窗口，较旧历史以文本保留，并逐步压缩中间推理与工具轨迹。这些是作者公开的预算口径，不是当前 API 可直接套用的计费公式，也不意味着所有原始画面永久无损保存。

声音和脸由不同解码器生成：音频使用因果 flow-matching 解码器；视频使用因果 DiT，并利用参考图与近期 latent 保持连续性。参考音频和图片用于控制音色与形象，但不能据此推导出手机可以本地运行整个 45B 系统。

![小M展示持续音视频流、前台推理、后台工具与解码器](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-02.png)

## 工程上，今天能先实现什么？

### 路线一：先接现售 Realtime，做出可靠语音 Agent

官方教学仓库是一个具体入口：
https://github.com/boson-ai/Higgs-Realtime-Tutorial

它依次介绍服务端签发短期凭证、浏览器 WebSocket、麦克风、打断、乱序转录和工具调用，还有 Pipecat 与 LiveKit 的学习分支。正式 API Key 留在服务端，浏览器只获得短期凭证；正式产品仍需自行补身份验证、额度限制和会话隔离。

对于自己定义的 function 工具，应用负责执行，再以 call_id 对应返回结果，最后请求模型继续。官网内置的 web_search 则由服务端执行。工具事件可能在不同事件中重复出现，不能看到一次就再执行一次；批量独立工具也需要避免每个结果各触发一遍回复，造成多段语音互相覆盖。

接入时不要只改域名。当前 Boson 文档列出了协议差异：主要使用 WebSocket；配置 session 后才收到 session.created；输出模态不能随意混合；部分字段会被忽略或拒绝。应以当前 Boson 文档核对具体字段，不能默认任何兼容客户端都无改动可用。

打断处理尤其重要。收到 speech_started 后，客户端应立即停止本地播放并清理队列，按实际已播放时长发送 conversation.item.truncate，避免模型把用户没听到的后半句话当成已传达。服务端仅知道自己发出了多少音频，不知道客户端实际播放了多少。

### 路线二：需要脸时，使用明确的 Avatar 链路

当前官方 Avatar 实时会话教程采用：用户加入 LiveKit 房间，业务 Agent 转发麦克风到 Higgs Realtime，再把回复音频交给 Avatar 参与者，由它发布同步的视频和音轨。

这个 Avatar 本身不负责听懂问题和决策。教程明确要求 LiveKit Cloud，自建 LiveKit 地址在该托管会话接口下不受支持；不能因为 LiveKit 软件可以自托管，就认为这一条 Boson 托管链路也能照搬到自建房间。

这可以搭出可交谈、可调工具、有脸的产品，但不是获得了 Duplex 权重，也不能据此声称已复现其原生全双工视觉能力。

### 路线三：坚持自托管，先拆分模块

可以采用可部署的 STT、文本/视觉模型、TTS、头像渲染器和独立任务执行层，先验证事件、延迟和权限，再逐个替换组件。Higgs STT 与 TTS 可作为候选模块，但需分别核对许可证和硬件需求。

这种组合能做出许多相似的产品行为，却不等于复制了同一个端到端模型。真正的挑战还包括自然插话、旁人讲话判断、噪声抑制、工具未返回时的回应、长上下文与音画同步，需要用真实场景评估。

Mycelium Protocol 建议把实现至少分成媒体收发、会话状态、后台任务、结果合并和播放五部分。对支付、发送消息等动作，许可与幂等控制应在工具执行边界完成；不能用模型一句“已取消”代替实际任务状态。

![小M分开管理语音打断、后台任务和结果回传](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-03.png)

## Mika 和 WorldForge 分别能补哪一层？

Mika 是独立的 Android Agent 项目，Apache-2.0。它不需要为微信等 App 单独接业务 API，但会使用 Android 的系统能力、无障碍及屏幕信息来操作界面。所谓“端侧 Agent”描述的是运行与控制位置，不是保证模型推理全部离线。

当前文档明确 Mika 不带模型，需要用户选择模型服务；配置云端模型时，对话或屏幕信息可能发往所选服务。本次源码快照有 24 份 App 知识和 18 份网站知识，不能把“25＋应用”当成固定版本的精确数量。它积累的是技能与知识记录，不是证明每完成一次任务就更新模型权重。我们没有连接真实安卓设备或验证具体 App 的任务成功率。

WorldForge（shengzing/worldforge）则是 MIT 的 Mac＋云端或本地 GPU 创作工作台。代码包含本地守护进程、SwiftUI 客户端、远端模型 worker、隧道与后期处理，主要围绕三维世界、图像和视频生成。它不是 Boson 的 Duplex 运行时，也不是通用全双工模型；README 中的 GPU 资源与性能数字，本次未做复测。

如果未来把它们接到语音 Agent 后面，可以把 Mika 的手机任务和 WorldForge 的创作作业包装成异步工具，返回 job_id、进度和最终产物。这里是我们提出的集成方向，三个项目目前没有被核实存在现成的官方互通插件。

## 我们实际验证了哪些代码？

固定官方 Higgs-Realtime-Tutorial 版本 87f1ae81434d8a65126503ceef36871e0b529f5c，运行了 31 项测试并通过 TypeScript 类型检查。测试覆盖重采样、工具处理和转录状态；教学搜索读取本地固定页面数据，不是联网搜索服务。

另外，我们写了一个仅用 Python 标准库的编排示例，五项本地检查通过：工具等待时仍能接收音频事件；打断清空旧播放并拒绝过期音频；语音打断不自动取消后台作业；同一进程内重复 call_id 复用一个作业；显式取消作业与停止说话分开。

这不是音频模型或网络服务。示例没有麦克风、真实语音、视频解码、API 调用和持久任务账本；进程内去重不等于跨重启的 exactly-once。31＋5 项检查也不证明 Duplex 的延迟、自然度、基准成绩或成本已复现。

编排示例与证据：
https://github.com/MushroomDAO/blog/tree/publish/higgs-realtime-duplex-open-weights-pricing-engineering/source/20261109-higgs-duplex

## 常见问题

### 现在能下载一个小版 Duplex 放手机上吗？

本次没有找到官方这样的权重。公开的 TTS/STT 模型是功能组件，不能当成完整 Duplex 的缩小版，也没有足够依据给出端侧显存或内存保证。

### 想现在做商业产品，最现实的起点是什么？

先用现售 Realtime 做语音与工具闭环，按需要增加 Avatar；同时确认实际调用费、身份验证、任务授权和故障恢复。不要把尚在候补的 Duplex 设成必须立即可用的依赖。

### 它已经在所有指标上超过其他模型了吗？

官方结果并非全部第一，例如 Full-Duplex-Bench v1.5 为 75.5，表内 GPT-Live-1 为 80.1。不同评测协议和配置仍需分别看；我们没有独立重跑这些成绩，也不会用单项高分替代实际交互验收。

## 一手资料

Duplex 技术公告：https://www.boson.ai/blog/higgs-realtime-duplex
团队：https://www.boson.ai/about/team
价格：https://www.boson.ai/pricing
文档索引：https://docs.boson.ai/llms.txt
接入差异：https://docs.boson.ai/models/higgs-realtime/migrate-an-existing-integration
打断：https://docs.boson.ai/models/higgs-realtime/guides/turn-detection-and-interruptions
工具：https://docs.boson.ai/models/higgs-realtime/guides/tool-calling
实时 Avatar：https://docs.boson.ai/models/higgs-avatar/realtime-sessions
教学代码：https://github.com/boson-ai/Higgs-Realtime-Tutorial
模型组织：https://huggingface.co/bosonai
TTS 3 权重与许可：https://huggingface.co/bosonai/higgs-tts-3-4b
STT 权重：https://huggingface.co/bosonai/higgs-audio-v3-stt
Mika：https://github.com/wangzan101/Mika
WorldForge：https://github.com/shengzing/worldforge

相关工程思路：https://blog.mushroom.cv/blog/anthropic-dreaming-dynamic-workflow-memory-review/
Agent 训练与评测边界：https://blog.mushroom.cv/blog/axion-agent-training-data-cost-review/
'''
en='''Higgs Realtime Duplex is a full-duplex multimodal model from Boson AI, the company co-founded by Mu Li. As of our November 9, 2026 review, we found no official Duplex weights, distilled checkpoint, or on-device lite release. Its launch post still describes the API as coming soon, with a waitlist.

The already priced Higgs Realtime API is a different offering. Downloadable Higgs TTS and STT checkpoints serve narrower purposes; they are not automatically smaller editions of Duplex.

The supplied material also names Mika and WorldForge. We checked them separately rather than assuming that all three form one system.

## Is this Mu Li’s model?

Boson’s team page lists Mu Li as co-founder and CEO/CTO, and the Duplex announcement credits him among its technical contributors. Calling it his team’s model is supported; calling it a solo project is not.

The November 5 announcement describes a 45B MoE front model continued-trained from a text model on approximately two trillion text, audio, and visual tokens. Conversation, reasoning, tool calls, and delegation run alongside one another.

Our evidence comes from official technical text, pricing, developer documentation, and public repositories/model cards. We located the referenced talk’s URL but could not retrieve its video body or subtitles; we do not claim to have watched the roughly 44-minute talk in full.

## Which resources are actually open or accessible?

| Resource | Verified status | A smaller Duplex? |
|---|---|---|
| Higgs Realtime Duplex | Public announcement/demos; API waitlist; no corresponding official weights found | No official lite, distilled, or quantized checkpoint found |
| Higgs Realtime API | Public integration docs and pricing | Existing realtime service, not automatically new Duplex |
| Higgs TTS 3 4B | Downloadable speech-generation weights | Not a complete listening/vision/tool-use model |
| Higgs STT | Public weights; reviewed card declares Apache-2.0 | Speech recognition component |
| Higgs-Realtime-Tutorial | Apache-2.0 teaching code | Client/application examples, not model weights |

We inspected 16 public Boson GitHub repositories and 12 Hugging Face model entries. No Duplex checkpoint appeared in these inventories. This is a dated search result, not a claim that no future release is possible.

Downloadability also differs from open-source licensing. Higgs TTS 3 uses a research/non-commercial license that explicitly says it is not an open-source license. Product integration and hosted commercial services require separate authorization. A Creator Use Grant permits attributed creative content, including monetized creator publications, under its conditions.

The older higgs-audio code repository’s Apache-2.0 license does not relicense every newer checkpoint. Consult current model cards and their LICENSE files rather than relying on older names or free-preview text in a README.

![Little M distinguishes Duplex access, existing APIs, and downloadable speech components](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-01.png)

## What does it cost today?

The following rates belong to existing Higgs Realtime, not Duplex. The public rate card does not list a separate Duplex price. Its eventual availability and pricing require an official launch update or commercial confirmation.

| Existing Higgs Realtime billing event | USD rate |
|---|---:|
| Input tokens | $0.75 / million |
| Cached input tokens | $0.25 / million |
| Output tokens | $4.50 / million |
| Estimated audio input | $0.0023 / minute |
| Estimated audio output | $0.014 / minute |
| Transcription input, when enabled | $0.0025 / minute |
| Memory Search | $5 / thousand queries |

Usage draws from prepaid credit. Minute rates are estimates for typical token usage, not a fixed call package; taxes are excluded.

For scale only, 60 input-audio minutes plus 20 output minutes gives approximately $0.418 using the published estimates. With 60 minutes on both sides, it becomes approximately $0.978. These are arithmetic examples, not measured bills. History, caching, transcription, search, delegated models, and other services affect actual spend.

Avatar pricing must be considered separately. The rate card lists video output at $0.07/min for 640×480 or 480×640 and $0.09/min for 640×640. Do not assume that realtime sessions, rendered video jobs, and future Duplex all share identical billing, or that avatar output is included in $0.014/min speech. Confirm the relevant session terms and add LiveKit and backend-tool costs.

## How does native Duplex work?

### Chunks are not an end-to-end latency guarantee

The published design divides streams into 160 ms chunks, including silence. The model can begin reasoning from partial speech and continue receiving input while producing output.

This differs from a strictly sequential ASR → text model → TTS pipeline. An existing service’s ability to handle interruptions also does not establish all of new Duplex’s native concurrent multimodal capabilities.

Perceived latency still includes capture, network, queuing, inference, decoding, and playback buffering. A tool or delegated model may take seconds. Neither a 160 ms chunk size nor the existing Realtime product’s approximately 700 ms marketing figure is our measured Duplex latency.

### The front model reasons before delegating

According to Boson, the 45B front model can reason and call tools itself. Difficult requests can go to a larger backend with shared context while the front model continues the conversation. Tools may return incremental results.

Applications therefore need separate states for speech and work. Interrupting a sentence need not cancel a lookup. Stopping playback cannot undo an already executed email or purchase.

### Compression controls continuous-stream cost

Boson describes one incoming audio token and two outgoing audio tokens per chunk, with one camera frame every six chunks, approximately every 0.96 seconds. This is the model’s visual-input cadence, not a claim to consume dozens of full-resolution camera frames every second.

Audio/visual streams use approximately 2.6K tokens/min; reasoning and tools bring the reported total to roughly 2.6–5K. The model normally retains a recent five-minute audio/visual window, older text history, and progressively compacted reasoning/tool traces. These are author-reported representation budgets, not a billing formula or lossless permanent retention of every image.

A causal flow-matching decoder renders voice, while a causal DiT renders the face using reference imagery and recent latents. Reference-controlled identity does not imply that the complete 45B system runs locally on a phone.

![Little M connects continuous media, front-model reasoning, background tools, and decoders](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-02.png)

## What can an engineering team build now?

### Start with the available voice API

The official teaching repository is a concrete starting point:
https://github.com/boson-ai/Higgs-Realtime-Tutorial

It covers server-minted short-lived credentials, browser WebSockets, microphone input, interruption handling, out-of-order transcripts, and tools, with Pipecat and LiveKit learning tracks. Keep the permanent API key server-side; production applications still need authentication, quotas, and session isolation.

Your application executes custom function tools, returns results against call_id, and requests a continuation. Built-in web_search executes server-side. Deduplicate repeated tool events and avoid starting a separate spoken continuation for every tool in one batch.

Migration requires more than changing a domain. Current Boson docs describe WebSocket transport, session configuration before session.created, output-modality restrictions, and ignored/rejected fields. Validate the current Boson protocol instead of assuming every compatible client works unchanged.

On speech_started, stop local playback, clear its queue, and send conversation.item.truncate using actual played audio time. The server knows when it sent audio, not exactly what the listener heard.

### Add a face through an explicit Avatar integration

The documented hosted path uses a LiveKit room: the business agent forwards microphone audio to Higgs Realtime and sends returned speech to an Avatar participant that publishes synchronized video and audio.

The avatar does not understand or decide independently. This hosted session route currently requires LiveKit Cloud and rejects self-hosted LiveKit URLs. The underlying transport software’s self-hostability does not imply support by every hosted integration.

This can produce a talking, tool-using avatar application. It does not provide Duplex weights or reproduce its native full-duplex visual model.

### For self-hosting, decompose the system

Combine deployable STT, a text/vision model, TTS, an avatar renderer, and a task layer. Check each component’s license and hardware requirements. Higgs speech releases are component candidates, not complete Duplex substitutes.

Similar product behaviors are possible, but native interruptions, side-conversation detection, noise, partial tool results, long context, and audiovisual synchronization still require real evaluation.

Mycelium Protocol recommends separating media transport, session state, background jobs, result merging, and playback. Enforce permissions and idempotency at tool execution boundaries. A model saying it cancelled something is not an authoritative task-state transition.

![Little M manages speech interruption, background jobs, and returned results separately](../../assets/images/higgs-realtime-duplex-open-weights-pricing-engineering-fig-03.png)

## Where do Mika and WorldForge fit?

Mika is an independent Apache-2.0 Android agent. Avoiding per-app business APIs does not mean avoiding Android system interfaces or model APIs. It uses system capabilities, accessibility, and screen information; on-device orchestration is not a guarantee of offline inference.

Its docs state that it ships without a model and uses the provider you configure. Cloud models can receive conversation or screen information. Our pinned checkout contains 24 app knowledge files and 18 site files; do not treat “25+ apps” as a precise invariant. Accumulated skills and knowledge do not prove online weight updates. We connected no Android device and verified no real-app task success rates.

shengzing/worldforge is a separate MIT Mac/GPU creative workbench with a local daemon, SwiftUI client, remote model workers, tunnels, and post-processing. It targets world, image, and video generation. It is not Boson’s runtime or a general full-duplex model. We did not reproduce its README’s hardware/performance claims.

A future integration could wrap Mika phone tasks and WorldForge creative jobs as asynchronous tools returning job IDs, progress, and artifacts. This is our proposal; we found no verified official plug-and-play integration among the three.

## What code did we actually verify?

At official tutorial revision 87f1ae81434d8a65126503ceef36871e0b529f5c, 31 tests and TypeScript checking passed. The tests cover resampling, tool handling, and transcript state. The tutorial search reads a small local fixture rather than the live web.

We also wrote a standard-library Python orchestration example with five passing checks: audio events remain processable during pending work; interruption flushes playback and rejects stale audio; speech interruption preserves background work; repeated call IDs reuse one in-process job; explicit job cancellation remains separate.

This example is neither an audio model nor a network service. It has no microphone, real audio/video generation, API calls, or durable job ledger. In-process deduplication is not cross-restart exactly-once execution. The 31 + 5 checks do not reproduce Duplex quality, latency, benchmark scores, or costs.

Example and evidence:
https://github.com/MushroomDAO/blog/tree/publish/higgs-realtime-duplex-open-weights-pricing-engineering/source/20261109-higgs-duplex

## FAQ

### Can I download a small Duplex for my phone?

No such official checkpoint was found in this review. Public TTS/STT components are not complete Duplex lite models, and no reliable on-device memory requirement can be given from the available information.

### What is a practical commercial starting point?

Build a voice/tool loop on available Realtime, add Avatar if needed, and establish actual billing, authentication, permissions, and recovery. Do not make a waitlisted API an immediately required dependency.

### Is it ahead on every benchmark?

No. Boson’s table reports Full-Duplex-Bench v1.5 of 75.5 versus 80.1 for GPT-Live-1. Configurations and protocols matter, and we did not rerun these scores. Single-metric results cannot replace application acceptance testing.

## Primary sources

Duplex: https://www.boson.ai/blog/higgs-realtime-duplex
Team: https://www.boson.ai/about/team
Pricing: https://www.boson.ai/pricing
Documentation index: https://docs.boson.ai/llms.txt
Protocol differences: https://docs.boson.ai/models/higgs-realtime/migrate-an-existing-integration
Interruptions: https://docs.boson.ai/models/higgs-realtime/guides/turn-detection-and-interruptions
Tools: https://docs.boson.ai/models/higgs-realtime/guides/tool-calling
Realtime Avatar: https://docs.boson.ai/models/higgs-avatar/realtime-sessions
Tutorial: https://github.com/boson-ai/Higgs-Realtime-Tutorial
Model organization: https://huggingface.co/bosonai
TTS 3: https://huggingface.co/bosonai/higgs-tts-3-4b
STT: https://huggingface.co/bosonai/higgs-audio-v3-stt
Mika: https://github.com/wangzan101/Mika
WorldForge: https://github.com/shengzing/worldforge

Related architecture: https://blog.mushroom.cv/blog/anthropic-dreaming-dynamic-workflow-memory-review/
Training/evaluation boundaries: https://blog.mushroom.cv/blog/axion-agent-training-data-cost-review/
'''
d='Higgs Realtime Duplex是李沐所在Boson AI团队的45B全双工模型。本文核对官方权重与候补API状态，区分现售Realtime费率、TTS和STT组件，解析160毫秒分块、后台工具、数字人和自托管路线，并介绍Mika、WorldForge的独立定位，给出经过本地检查的编排示例与工程接入边界。'
e='Investigate Higgs Realtime Duplex weights, API access and pricing, with implementation paths, speech components, Mika, WorldForge, and local code checks.'
while len(d)<150:d+='供开发团队参考。'
while len(e)<150:e+=' Read on.'
assert 150<=len(d)<=160,len(d)
assert 150<=len(e)<=160,len(e)
f={'title':'Higgs Realtime Duplex：开源、收费与工程实现核查','titleEn':'Higgs Realtime Duplex: Weights, Pricing, and Engineering','description':d,'descriptionEn':e,'wechatTitle':'Higgs全双工：开源了吗，怎么接入','wechatDigest':'核对Duplex候补、现售API费用和语音权重，拆解异步工具与数字人链路。','pubDate':'2026-11-09','updatedDate':'2026-11-09','category':'Tech-News','tags':['Higgs','全双工','语音Agent','Boson AI','Mika','WorldForge'],'heroImage':'../../assets/images/'+s+'-banner.jpg'}
fm='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in f.items())+'\n---\n\n'
a='\n---\n\n> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。\n'
b='\n---\n\n> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.\n'
Path('src/content/blog/'+s+'.md').write_text(fm+cn+a+'\n<!--EN-->\n\n'+en+b);print(len(d),len(e))
