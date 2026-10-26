---
title: "Realtime-Venus：双9B全双工模型、异步Agent与部署核查"
titleEn: "Realtime-Venus: Full-Duplex Models and Async Agents"
description: "Realtime-Venus 把持续音视频交互与后台 Agent 执行分开。本文核对 inclusionAI 模型卡、仓库与 arXiv 2609.13814，解释两个9B模型、官方评测、CUDA部署、Mac使用边界及外部任务后端。"
descriptionEn: "A source audit of Realtime-Venus: two 9B full-duplex models, asynchronous agents, reported benchmarks, CUDA deployment, and practical limits for Mac users."
wechatTitle: "Realtime-Venus：边对话边执行任务"
wechatDigest: "核查双9B全双工模型、异步任务架构与部署要求，性能结果均为官方自报。"
pubDate: "2026-09-20"
updatedDate: "2026-10-26"
heroImage: "../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-banner.jpg"
category: "Tech-Experiment"
tags: ["Realtime-Venus", "full-duplex", "voice-ai", "agent", "CUDA", "open-source"]
lang: zh-CN
lastPublishedAt: "2026-10-26T01:13:46Z"
---

Realtime-Venus 让语音助手在持续听、看、说的同时，把耗时任务交给后台 Agent，结果再回到原对话。它的价值在于交互与执行的协调；本文的模型分数全部来自官方报告，不是 Mycelium Protocol 的性能实测。

项目由蚂蚁集团 Venus Team 与清华大学合作，代码和模型卡标注 Apache-2.0。2026 年 10 月 26 日，我们复核模型卡、仓库和论文 v3，更新这篇旧稿，修正此前的权重容量、硬件门槛与脚本路径说明，保留原始发布日期和链接。

一手来源：

- 模型权重与模型卡：https://huggingface.co/inclusionAI/Realtime-Venus
- 代码：https://github.com/inclusionAI/Realtime-Venus
- 论文：https://arxiv.org/abs/2609.13814v3
- 项目主页：https://realtime-venus.github.io/

## 双 Loop 到底解决什么问题？

设想你让语音助手整理会议材料，然后继续讨论议程。执行任务可能要几十秒，交互却不能一直等着：你可能补充要求、纠正名字，或者直接取消任务。

Realtime-Venus 将工作分成两个循环。前台模型管理连续感知、说话时机和语音生成；后台 Harness 接收委托，执行推理或工具任务，再将结果送回发起请求的会话。前台不必等待后台任务完成才继续处理输入。

这和“先语音识别、再问文字模型、最后合成语音”的串行流水线有所区别。全双工还需要判断重叠语音的意义：“嗯”通常不该让助手停下来，“等等，改成下午”则可能需要改变回复和任务意图。

![小M持续听看并把耗时任务交给后台，表示交互与执行两个循环](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-01.png)

**双循环不等于同时运行两个9B模型。** Omni 和 Audio 是可供选择的完整对话前端，Harness 才是后台任务管理层；后台的任务模型另行配置。

## Omni、Audio、Harness 分别开源了什么？

| 组件 | 作用 | 需要注意的边界 |
| --- | --- | --- |
| Realtime-Venus-Omni，9B | 音视频、图像与文本输入，原生语音输出，主动交互与长视频记忆 | 官方推理路径使用 CUDA |
| Realtime-Venus-Audio，9B | 音频与文本输入，语音理解和全双工对话 | 是分别训练的检查点；推理不用视觉编码器，不代表文件一定明显更小 |
| Realtime-Venus-Harness | 委托捕获、异步执行、结果回传与交付追踪 | 默认通用任务后端需要 Codex 登录与网络 |
| 浏览器 Demo 和推理示例 | 麦克风、摄像头、上传媒体、任务进度与产物下载 | Demo 文档标明仅一个活跃会话，不能据此声称支持生产级多租户并发 |

模型卡列出两者均基于 MiniCPM-o 4.5 / Omni-Flow，语言主干为 Qwen3-8B，音频编码器为 Whisper-Medium，Omni 使用 SigLIP2 视觉编码器。两者标称上下文长度均为 40,960 tokens，权重精度为 BF16。

原生语音还依赖参考音频和 Token2wav 资源。下载时只取 safetensors、漏掉模型代码或语音资产，不能保证官方示例正常运行。

长视频 Memory 的思路是归档、检索相关历史证据，再重组音视频上下文，无需为该模块额外训练。它不意味着把任意长原始视频完整塞进40,960-token窗口，也不保证历史细节永不丢失。

## 官方成绩该怎么看？

以下取自论文 v3 的表2、表3、表4、表6和表8，均为作者报告。各测试定义不同，不能把表中数字直接平均成一个“综合能力分”。

| 测试 | 官方结果 | 可以支持的判断 |
| --- | --- | --- |
| StreamingBench | Omni 70.2，MiniCPM-o 4.5 为67.9 | 在该视频理解评测上有提升 |
| OVO-Bench | Omni 64.7，基座60.7 | 该设置下的流式理解改善 |
| ProactiveVideoQA，PAUC | Omni 46.2，基座47.5 | 并非每项主动交互测试都超过基座 |
| LVOmniBench，60–90分钟子集 | Omni加Memory后47.06%，不加为41.18% | 该子集提升5.88个百分点，不等于完整系统持续运行的可靠性 |
| MMAU / MMAU-Pro | Audio 78.0% / 63.2% | 音频理解具备竞争力，不能据此推导识别延迟 |
| Full-Duplex-Bench v1.5 | Audio在用户附和时继续说话的比例0.97；打断场景回应比例0.75 | 连续性与及时响应打断存在不同维度的权衡 |
| 自建Delegate Benchmark | Omni总体路由准确率75.93%，Audio 68.89% | 测量是否正确委托，不是工具任务端到端成功率 |

论文默认每秒采样一帧，常规视频评测最多128帧；全双工评测以一秒音频块处理输入，输出音频为24kHz。部分竞品分数来自其他论文，比较时还需关注评测来源。

一秒输入块不是“一秒首音延迟”的直接测量，70.2也不是70.2毫秒。本次没有复现端到端延迟、实时因子、峰值显存或并发容量，因此不提供未经验证的速度结论。

## 后台做完，不等于用户已经听到

Harness 在委托时绑定会话，并固定请求开始时可用的证据边界。任务执行期间，用户可以继续说话；返回的结果需要经过会话、时效和播放状态相关的检查，再由前台组织成用户能听到的回复。

这解决的是一个容易被忽略的工程问题：任务状态已经变成“完成”，但用户正在说话、断开了连接，或者结果只送到了内部队列，实际没有播出。若系统直接把这些情况都算作成功，就会出现“后台说完成了，用户却没听到”的失联。

![小M等到谈话空隙把结果交回原会话，区分后台完成与实际播报](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-02.png)

我们的判断是，这套交付状态设计比单独展示“可以调用工具”更值得复用。实际接入审批、文件写入或消息发送时，仍要测试取消后是否继续执行、旧任务是否被新指令取代，以及重复回包是否触发重复动作。

## 本地部署需要什么硬件？Mac能跑吗？

本次读取 Hugging Face 文件元数据并汇总：每个模型目录的 safetensors 合计 **18,743,802,932字节，约18.74GB（17.46GiB）**。完整 Omni 目录约20.08GB，Audio约19.99GB。这是下载文件大小，不是显存或系统内存实测；缓存、激活、语音模块和媒体处理还会占用资源。

| 使用方式 | 当前官方路径与建议 |
| --- | --- |
| 独立模型示例 | 文档要求 Python 3.10、CUDA、FFmpeg；完整下载所选模型 |
| 完整网页交互 Demo | Linux服务器、NVIDIA CUDA GPU及可用驱动；安装器创建Python 3.11/3.12环境 |
| 具体显卡最低门槛 | 本次核查的官方部署文档未给出通用最低显存表；应按模式、上下文、语音输出实际测量 |
| Apple Silicon Mac本地推理 | 官方示例使用CUDA，没有在本次资料中找到可直接照做的MPS/MLX部署路径 |
| Mac作为客户端 | 可以通过SSH转发访问远端GPU服务，在浏览器使用本机摄像头和麦克风 |

旧稿“两个9B合计约18GB”“必须A100”“64GB Mac可直接走MPS”等说法均已删除。Audio不使用视觉编码器，也不能据此直接给出更低的显存保证。

本次核查机器是16GB统一内存的M4 Mac。我们做了源码、文件元数据和文档审计，没有下载并运行这些模型；下列命令是核对后的官方部署路径，不冒充本机跑通记录。

![小M用Mac浏览器连接远端GPU服务器，说明客户端与推理服务的区别](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-03.png)

## 如何按当前官方路径开始？

先在满足条件的Linux GPU服务器准备源码。为便于核对，本文固定到本次读取的仓库提交：

```bash
git clone https://github.com/inclusionAI/Realtime-Venus.git
cd Realtime-Venus
git checkout e53ae8d5bde92b30364b26f2e4c13c9db7a8ffea
```

在准备好的Python环境下载所需模型。只做音视频交互先选`omni`；纯语音选`audio`，不要无意中下载两个：

```bash
python -m pip install 'huggingface_hub>=0.34' 'PyYAML>=6.0'
python download_models.py --model omni --local-dir .
```

独立Omni示例的依赖与入口如下。脚本自带样例输入，输出与参数说明应同时阅读对应目录README：

```bash
python -m pip install -r Realtime-Venus-Omni/requirements.txt
export REALTIME_VENUS_MODEL_PATH="$PWD/Realtime-Venus-Omni"
python frontend/Realtime-Venus-Omni/offline_chat.py
python frontend/Realtime-Venus-Omni/duplex_chat.py
```

如果选择Audio，按其指南安装仓库根目录`requirements.txt`，使用`frontend/Realtime-Venus-Audio/audio_offline_chat.py`或`audio_duplex_chat.py`，不要套用不存在的`frontend/audio_inference.py`。

完整网页Demo另走安装器：

```bash
bash install.sh
# 编辑根目录 config.json 和 harness/config.json 后再启动
bash start.sh --config config.json
```

根目录`config.json`设置前端模型路径、模式和网页端口；`harness/config.json`设置任务后端、工作目录与执行相关选项。Omni的模式值为`video`（也接受`omni`），路径指向完整`Realtime-Venus-Omni`目录；Audio选择`audio`和对应检查点。

组件文档`demos/README.md`提供了Audio切换说明，而根README仍保留“Demo仅集成Omni”的旧表述。首次复现建议先用Omni，再按组件文档与实际代码核对Audio模式，避免把两份文档差异当成已验证兼容性。

网页默认监听远端`127.0.0.1:8032`。在自己的Mac终端保持隧道开启：

```bash
ssh -N -L 8032:127.0.0.1:8032 user@server
```

随后访问`http://localhost:8032`，完成浏览器麦克风或摄像头授权。`user@server`需要换成自己的服务器登录信息；这里没有把模型搬到Mac本地执行。

## “本地模型”是否意味着整套系统离线？

独立模型可以从本地检查点加载；完整Demo的默认通用任务执行依赖Codex后端，需要联网和有效登录。当前文档还允许部分角色选择Gemini，例如路由、结果整理或多模态理解；选择这些角色会将相应文本或媒体发送给Google API。

因此，要分别确认前台模型、后台任务模型、工具访问和媒体证据的流向。开源前台不自动意味着后台免费、离线或数据不出域。需要完全本地的团队，必须实现并验证相应后端适配，不能把接口可扩展写成已经支持所有本地模型。

代码与权重的Apache-2.0许可也不等于“仅限研究”；论文页面另有文档许可。第三方服务、数据、参考音色和其他依赖应分别核对适用条款。

## 上线前应该验收什么？

建议先做三组小测试：助手说话时分别输入附和和纠正；后台任务执行中修改要求或取消；任务完成后打断、断线再恢复。分别记录识别到意图、后台完成、结果入会话、音频实际播放四个时间点。

这比只测文本生成速度更贴近产品可用性。不要把路由准确率替代任务成功率，也不要把一段演示视频当作长时间稳定运行证明。

相关工程阅读：Mycelium Protocol 的OpenShell运行时分析讨论工具执行与隔离，可与这里的交互层分工对照：https://blog.mushroom.cv/blog/nvidia-openshell-agent-runtime/

## 常见问题

### 需要两个9B模型同时运行吗？

不需要。Omni与Audio是不同输入场景的前端选择；异步任务由Harness管理，后台模型另外配置。下载`all`只意味着取得两个目录。

### 18.74GB是否意味着24GB显卡一定能流畅运行？

不能。18.74GB是单模型safetensors文件总量，未包含全部运行开销。显卡容量、上下文与实时目标必须一起测量，本次没有24GB显卡实测。

### 官方分数能否证明Agent任务可靠完成？

不能。论文的委托测试衡量路由决策，完整工具执行、取消恢复、权限控制和语音交付还需要独立验收。

### Mac用户现在最稳妥的体验方式是什么？

使用浏览器连接配置好的Linux NVIDIA服务。把PyTorch设备参数改成`mps`不构成官方支持，也没有在本文中验证。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Realtime-Venus lets a voice assistant keep listening, watching, and speaking while an asynchronous agent handles longer tasks. Its main contribution is coordination between interaction and execution. All model scores below are author-reported; Mycelium Protocol has not reproduced GPU performance.

The project comes from Ant Group's Venus Team and Tsinghua University. Its repository and model card specify Apache-2.0. This October 26, 2026 update corrects hardware, weight-size, and deployment statements in our original September 20 article, retaining the same URL and original publication date.

Primary sources:

- Model card and weights: https://huggingface.co/inclusionAI/Realtime-Venus
- Source code: https://github.com/inclusionAI/Realtime-Venus
- Technical report v3: https://arxiv.org/abs/2609.13814v3
- Project page: https://realtime-venus.github.io/

## What does the dual-loop architecture solve?

A spoken request to prepare meeting materials may take much longer to execute than an ordinary conversational response. Meanwhile, the user may add requirements, correct a name, or cancel.

The interaction loop handles continuous perception, conversational control, and native speech. The capability loop delegates work through Harness and returns its result to the originating conversation. A long task need not block incoming conversational input.

Full duplex also requires interpreting overlapping speech. An acknowledgment should not necessarily stop the assistant, whereas a correction may require a changed response. This is more than attaching a tool call to a serial speech-recognition, text-generation, and speech-synthesis pipeline.

![Continuous interaction with a separate background task loop](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-01.png)

Two loops do not require loading both 9B checkpoints. Omni and Audio are alternative conversational frontends. Harness manages background work, whose model is configured separately.

## What is actually released?

| Component | Purpose | Boundary |
| --- | --- | --- |
| Omni, 9B | Streaming audiovisual interaction, proactive responses, speech, and video memory | Official inference examples use CUDA |
| Audio, 9B | Audio/text understanding and full-duplex spoken interaction | Separately trained; unused vision at inference does not guarantee much smaller files |
| Harness | Asynchronous delegation, execution, return, and delivery tracking | Default general-task backend needs Codex authentication and network access |
| Browser Demo and scripts | Microphone, camera, media uploads, task progress, and artifacts | Demo documentation specifies one active conversation |

The model card lists MiniCPM-o 4.5 / Omni-Flow, a Qwen3-8B language backbone, and a Whisper-Medium audio encoder. Omni additionally uses SigLIP2. Both checkpoints specify BF16 weights and a 40,960-token context.

Speech generation also needs the reference audio and Token2wav assets. Download complete checkpoint directories, including model code, rather than safetensors alone. Training-free video memory archives and retrieves relevant historical evidence; it does not retain unlimited raw video in the context window or guarantee perfect recall.

## What do the reported scores establish?

The following are from report v3, not independent measurements. Metrics have different definitions and should not be averaged into a single capability score.

| Evaluation | Reported result | Interpretation |
| --- | --- | --- |
| StreamingBench | Omni 70.2; MiniCPM-o 4.5 67.9 | Better video understanding in this setting |
| OVO-Bench | Omni 64.7; base model 60.7 | Improvement on this streaming evaluation |
| ProactiveVideoQA, PAUC | Omni 46.2; base model 47.5 | Not an improvement on every proactive metric |
| LVOmniBench, 60–90-minute subset | Omni 41.18% without memory, 47.06% with memory | A 5.88-percentage-point gain on this subset |
| MMAU / MMAU-Pro | Audio 78.0% / 63.2% | Competitive audio understanding, not a latency measurement |
| Full-Duplex-Bench v1.5 | Audio backchannel continuation 0.97; interruption response 0.75 | Continuity and interruption handling are distinct trade-offs |
| In-house Delegate Benchmark | Overall routing: Omni 75.93%, Audio 68.89% | Delegation decisions, not end-to-end tool success |

The evaluation description uses one video frame per second, a maximum of 128 frames for ordinary video evaluation, and one-second input audio chunks for duplex evaluation. Speech output is 24kHz. Some competitor figures come from other reports.

A one-second input chunk is not a measured one-second time to first audio. We did not reproduce latency, real-time factor, peak VRAM, or concurrency.

## Why distinguish task completion from spoken delivery?

Harness binds requests to their original sessions and preserves the evidence boundary available when a delegation begins. Returned results undergo eligibility and playback-related handling before the frontend presents them.

A completed task may still have an unheard result: the user could be speaking, disconnected, or waiting while the reply sits in an internal queue. Treating execution completion and actual playback as separate events makes this failure visible.

![A finished task is returned to the original conversation when delivery is appropriate](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-02.png)

Our engineering assessment is that this delivery model is more reusable than a simple tool-calling demonstration. Applications still need to test cancellation, superseded requests, stale results, and duplicate external actions.

## What hardware is needed? Can a Mac run it?

We summed the Hugging Face file metadata: each checkpoint has 18,743,802,932 bytes of safetensors, approximately 18.74GB or 17.46GiB. The complete Omni directory is approximately 20.08GB; Audio is 19.99GB. These are file sizes, not measured runtime memory. Cache, activations, speech assets, and media processing require additional resources.

| Deployment | Current documented path |
| --- | --- |
| Standalone examples | Python 3.10, CUDA, FFmpeg, and a complete selected checkpoint |
| Browser stack | Linux NVIDIA CUDA server; installer creates an isolated Python 3.11/3.12 environment |
| Minimum GPU capacity | The reviewed deployment guides provide no universal minimum-VRAM table; measure the selected mode and context |
| Apple Silicon inference | No ready-to-follow MPS/MLX deployment path was found in the reviewed official material |
| Mac client | A browser and SSH tunnel can connect local microphone/camera input to the remote GPU server |

Earlier claims that both 9B models total 18GB, that an A100 is mandatory, or that a 64GB Mac can simply use MPS have been removed. Not using vision at inference is insufficient evidence for a particular memory reduction.

Our audit machine is a 16GB M4 Mac. This review checked sources and metadata; it did not run the models. The commands below are documentation-checked deployment instructions, not a successful local inference test.

![A Mac browser connects to a remote NVIDIA inference server](../../assets/images/realtime-venus-fulldup-interactive-dual-loop-local-deploy-fig-03.png)

## How do you start with the official path?

On a suitable Linux GPU server, check out the reviewed source revision:

```bash
git clone https://github.com/inclusionAI/Realtime-Venus.git
cd Realtime-Venus
git checkout e53ae8d5bde92b30364b26f2e4c13c9db7a8ffea
python -m pip install 'huggingface_hub>=0.34' 'PyYAML>=6.0'
python download_models.py --model omni --local-dir .
```

Select `audio` for Audio only. The downloader defaults to `all` when the option is omitted, so make the choice explicit. Keep custom model code and speech assets.

For standalone Omni, in the appropriate Python environment:

```bash
python -m pip install -r Realtime-Venus-Omni/requirements.txt
export REALTIME_VENUS_MODEL_PATH="$PWD/Realtime-Venus-Omni"
python frontend/Realtime-Venus-Omni/offline_chat.py
python frontend/Realtime-Venus-Omni/duplex_chat.py
```

Audio's guide uses the root `requirements.txt` and its `audio_offline_chat.py` / `audio_duplex_chat.py` scripts under `frontend/Realtime-Venus-Audio/`. Read each guide for bundled sample inputs, outputs, and parameters.

For the full browser Demo, use the separate installer flow:

```bash
bash install.sh
# Configure config.json and harness/config.json before starting.
bash start.sh --config config.json
```

The root file selects frontend type, complete checkpoint path, and web port. The Harness file configures background tasks and workspace. Omni uses type `video` or `omni`; Audio uses `audio` with its separate checkpoint.

There is a documentation mismatch: `demos/README.md` describes Audio mode, while the root README retains an older Omni-only statement. Start with Omni, then check the component documentation and code before relying on Audio integration.

From the Mac, keep this tunnel open and replace the SSH destination:

```bash
ssh -N -L 8032:127.0.0.1:8032 user@server
```

Open `http://localhost:8032` and authorize microphone/camera access. The model still runs on the server.

## Does a local frontend make the complete system offline?

No. Standalone inference can load local checkpoints, but the default Demo general-task worker uses a networked Codex backend. Current documentation also allows Gemini for selected roles such as routing, result preparation, and multimodal understanding. Selecting those roles sends the corresponding text or media to Google's API.

Audit frontend inference, background inference, tool access, and evidence handling separately. Interface extensibility is not proof that every local backend is already supported. Apache-2.0 does not impose a research-only restriction; the paper and third-party services, data, voices, and dependencies have their own applicable terms.

Before deployment, test acknowledgments versus corrections, changing or canceling a running task, and interrupted or disconnected result delivery. Record intent detection, task completion, result insertion, and actual audio playback independently. Routing accuracy cannot replace task success or permission testing.

Related Mycelium Protocol engineering analysis: https://blog.mushroom.cv/blog/nvidia-openshell-agent-runtime/

## Frequently asked questions

### Must both checkpoints run together?

No. Omni and Audio are alternative frontends. Harness manages asynchronous tasks with a separately configured backend.

### Does an 18.74GB checkpoint guarantee smooth operation on a 24GB GPU?

No. The figure measures safetensors file size, excluding runtime overhead. This review includes no 24GB GPU experiment.

### Do the official scores establish reliable agent execution?

No. Delegation routing, external execution, cancellation, permissions, and spoken delivery require separate validation.

### What is the practical Mac access path?

Use a browser connected to a configured Linux NVIDIA server. Changing a PyTorch device string to `mps` is neither an official support statement nor a validated deployment in this review.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
