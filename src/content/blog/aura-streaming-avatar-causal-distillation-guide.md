---
title: "AURA流式数字人：实时生成的前提与开放边界"
titleEn: "AURA Streaming Avatars: Speed, Causality and Release Limits"
description: "AURA 把肖像与语音变成分块输出的数字人视频，通过因果注意力、滚动缓存和两阶段蒸馏减少生成等待。本文核对 Kyutai 论文、推理源码与模型卡，区分 H100 上的论文吞吐、公开代码速度和首帧延迟，检查部分数据发布及非商业许可，并运行百轮缓存张量验证，解释从研究模型接入实时对话产品还需要补齐哪些工程环节。"
descriptionEn: "Explore Kyutai AURA's streaming avatars, causal cache and distillation, with H100 timing limits, partial data release and 100 synthetic cache checks on CPU."
wechatTitle: "AURA流式数字人：实时的条件"
wechatDigest: "核对数字人生成的分块机制、H100速度、公开代码差异与非商业许可，并验证滚动缓存逻辑。"
pubDate: "2026-11-21"
updatedDate: "2026-11-21"
category: "Tech-News"
tags: ["AURA", "Kyutai", "数字人", "流式生成", "模型蒸馏"]
heroImage: "../../assets/images/aura-streaming-avatar-causal-distillation-guide-banner.jpg"
---

AURA 把一张肖像和语音转成逐块输出的说话视频，重点是让数字人跟上持续到来的语音，而不是先等完整长视频生成结束。

这里指 Kyutai 的《AURA: AUdio-dRiven streaming Avatar》，arXiv:2611.26540，2026 年 11 月 19 日提交；它与同名的持续视频理解项目不同。Mycelium Protocol 核对了论文、官方模型卡，以及推理仓库提交 `c06aa7dc8b850405273345089da521454ffd607e`。代码与权重已公开，但带有非商业限制，不能按 MIT 或 Apache-2.0 项目理解。

论文：https://arxiv.org/abs/2611.26540

代码：https://github.com/kyutai-labs/aura

## 流式数字人到底省掉了什么等待？

传统双向视频扩散模型通常要看到较长的一段音频，并经过多轮去噪后生成整段画面。对语音助手而言，等音频攒够、再等视频算完，会让说话的人像明显落后于声音。

AURA 用分块因果生成替代跨长段的双向生成：每个块需要自己的音频，能读取已生成的历史，不依赖后面多个块的未来声音。每块只做四步去噪，再输出视频供后续播放。

这里的因果是块与块之间的，块内部仍可双向注意，并不等于每个音频采样一到就能出一帧。代码默认一个块有四个潜帧，对应通常 16 个视频帧，第一块为 13 帧。按 1.3B 的 16 fps 播放率计算，后续块约是一秒视频；5B 的 25 fps 对应约 0.64 秒。采集、编码和缓冲仍然影响响应。

![小M逐块接收语音积木并生成视频片段，同时保留身份锚点](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-01.png)

## 20.7 fps 与 9.7 fps，哪个才算实时？

官方给出的数字要分成论文优化管线与公开参考代码两组：

| 模型 | 输出与播放目标 | 论文优化管线，单张 H100 | README 的公开代码，开启 compile |
|---|---|---|---|
| AURA-1.3B | 官方称 576p，16 fps | 20.7 fps | 约 16 fps |
| AURA-5B | 官方称 720p，25 fps | 9.7 fps | 约 8 fps |

小模型在这组设备与设置下达到播放速度；大模型虽然更快于自己的教师，吞吐仍不足以持续跟上 25 fps 播放。它不能被笼统称为“720p 实时数字人”。

分辨率也不是固定视频模板。当前 1.3B 配置按肖像比例选择 `(576,576)` 或 `(512,768)` 的高宽桶；论文部分表注称它为 480p，正文与模型卡简称 576p。部署时应看实际高宽，而不是把“576p”自动翻译成固定 16:9 输出。

论文计时使用固定十秒英语音频，在单张 H100 上比较，Total 吞吐排除了加载与预热。1.3B 的约 23 倍和 5B 的约 17 倍，分别相对各自双向教师计算，不是相对任意数字人系统，也不是首帧延迟提升倍数。

本次没有复现这些 GPU 数字，更没有据此推算消费卡、Mac 或手机的表现。

## 为什么缓存不必随视频一直增长？

AURA 保留第一块作为稳定锚点，再保留最近的局部上下文，其余旧块会被移出缓存。这样，时间越长不必保存越多历史 K/V；同一块的不同去噪步骤也覆盖同一缓存位置，而不是每个步骤维护一整份历史。

读代码时有一个细节：`kv_window=2` 把当前块也算进去，所以预留的是锚点、前一个块和当前块的空间。论文说保留一个最近的历史块，与这个配置并不矛盾。

这种设计控制的是特定缓存的增长方式，不能解释为总显存占用很低。扩散模型、VAE、文本编码器、音频编码器与临时张量仍要占资源；参数名中的 1.3B 不是整条系统的全部内存账。

它也不保证无限时长的人物身份绝不漂移。论文的长时稳定性实验是 60 秒：1.3B 的部分样本出现漂移，平均 CSIM 从 0.83 降到 0.78；5B 约从 0.76 降到 0.69。缓存大小不增长与人物长期一致性，是两个要分别验证的性质。

## 两阶段蒸馏为什么要一起做？

第一阶段 ODE Teacher Forcing 使用教师去噪轨迹，让学生学习以更少步骤生成，同时适应分块滑动窗口的因果注意力。它解决了结构与采样步数的改变，但学生沿自己的生成路径运行时，仍可能遇到训练时没见过的中间状态。

第二阶段使用带 backward simulation 的分布匹配蒸馏 DMD，让学生在自身生成路径上接受分布层面的修正，减少这一偏差。论文说明没有加入需要真实视频的 GAN 损失。这里的“少步推理”来自额外训练，不能理解成给原始大模型改一个步数参数便能得到相同质量。

![小M先沿教师轨迹练习，再检查自己生成的轨迹，区分两阶段蒸馏](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-02.png)

论文记录了数十张 H100 的训练设置。普通工程师更容易借鉴的是因果约束、缓存管理和反馈验证；从零重复完整蒸馏，是另一种资源规模的项目。

## 公开了什么，又有哪些尚未完整放出？

官方提供两款学生权重、1.3B 教师、推理代码和数据入口。权重有 merged 与 LoRA-only 等形态，后者不能脱离底座、教师和阶段顺序直接当最终模型使用；推理还依赖 Wan 的 VAE、文本编码器，以及对应音频编码器。

更需要注意数据卡的当前状态：`kyutai/AURA-Dataset` 明确标为部分发布。已列出的是 1.3B 教师的 ODE 潜变量轨迹，训练集 30,000 条、验证集 200 条。论文中 TalkVerse/5B 的 3 万段视频及其完整配套数据仍标为后续发布；参考图片和提示词也不在这份数据里重分发，需要从对应 Hallo3 来源取得。

因此，不宜把摘要中的发布承诺直接写成“所有视频与训练材料已经完整到手”。本次仅核对数据卡与文件说明，没有下载约 TB 级轨迹集合。

| 对象 | 当前标注的许可 |
|---|---|
| 推理仓库代码 | Snap Inc. Non-Commercial License |
| AURA-1.3B 权重 | CC BY-NC 4.0 |
| AURA-5B 权重 | Snap Inc. Non-Commercial License |
| AURA 数据集 | CC BY-NC 4.0，并须检查来源条件 |

这是一组有使用条件的研究发布。组件许可也要分别核对，不能只看到 Wan 的 Apache-2.0 就推导整套系统可自由商用。

数据卡：https://huggingface.co/datasets/kyutai/AURA-Dataset

## 本机验证覆盖到了哪里？

我们直接导入原样的 `aura/kv_cache.py`，用 CPU float32 合成张量推进 100 个块，检查锚点保持、旧块移出、最近历史保留、当前槽覆盖、K/V 内容，以及底层存储指针和形状不增长；另检查配置上限后的 RoPE 位置保持有界。检查全部通过。

这是一项缓存组件检查，没有运行扩散网络、VAE、音频编码器或完整数字人生成。测试环境为 PyTorch 2.14，而项目声明的完整环境要求为 PyTorch 2.6 至 2.8；单个组件可导入不能证明整套环境兼容。本次没有下载模型权重，也没有测显存峰值、首帧延迟或吞吐。

## 接入语音 Agent，还缺哪一层？

参考代码 `Aura.generate(image, audio)` 接收文件路径，在视频循环之前先提取音频特征，再逐块 yield 视频。它展示的是分块输出接口；不能仅凭 Python 生成器就宣布麦克风输入、网络传输和浏览器播放都已端到端流式化。

官方在线演示把 AURA 与 Unmute 语音系统组合。工程团队仍需处理增量音频、播放时钟、积压与丢帧策略、插话时取消旧片段，以及错误后恢复。至少同时记录“输入音频何时到达、第一块何时可播、是否持续追上播放”三个时刻。

我的判断是，AURA 最值得研究的地方，是把实时约束提前写进训练与缓存结构，而非只在推理端做加速补丁。对准备做产品的团队，先用明确的硬件和任务验证，再核对授权；论文吞吐与可上线服务之间，仍有系统集成工作。

![小M连接输入音频、首块视频与播放时钟，检查是否积压并取消旧片段](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-03.png)

## FAQ

### 可以只接云端接口，不下载模型吗？

官方演示可用于体验，但公开仓库是依赖 CUDA 和本地模型权重的推理代码，不只是云端 API 包装。体验在线演示不等于已完成自托管。

### 720p 的 5B 模型已经实时吗？

论文报告 9.7 fps，而其播放目标是 25 fps；公开参考代码更约为 8 fps。这个设置下未达到持续实时播放。

### 无限流式是否证明能稳定直播几小时？

没有。固定缓存支持持续推进，但身份、口型与运行稳定性需要另外验证，论文报告的长时定量实验为一分钟。

相关阅读：LongCat 音频驱动数字人的工程核对 https://blog.mushroom.cv/blog/longcat-video-avatar-16-engineering-guide/

资料：项目入口 https://kyutai.org/aura/ ；1.3B https://huggingface.co/kyutai/AURA-1.3B ；5B https://huggingface.co/kyutai/AURA-5B ；论文全文 https://arxiv.org/html/2611.26540v1

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

AURA turns a portrait and speech into talking-head video emitted chunk by chunk. Its goal is to keep an avatar moving with arriving speech rather than wait for an entire long video to finish.

This is Kyutai's “AURA: AUdio-dRiven streaming Avatar,” arXiv:2611.26540, submitted November 19, 2026, not the unrelated streaming-video understanding project of the same name. Mycelium Protocol inspected the paper, model cards and repository commit `c06aa7dc8b850405273345089da521454ffd607e`. Public code and weights carry non-commercial restrictions.

Paper: https://arxiv.org/abs/2611.26540

Code: https://github.com/kyutai-labs/aura

## What waiting does causal streaming remove?

Bidirectional video diffusion commonly processes substantial audio segments with many denoising steps. A voice assistant then waits both for sufficient input and for generation to complete.

AURA generates causally across chunks, using each chunk's own audio and previously generated context. It uses four denoising steps per chunk rather than requiring several future audio chunks. Attention within a chunk remains bidirectional, so this does not mean instantaneous frame generation from each incoming audio sample.

The reference code uses four latent frames per chunk, normally decoding to 16 video frames, with 13 in the first chunk. Subsequent chunks therefore represent roughly one second at the small model's 16 fps, or 0.64 seconds at the larger model's 25 fps. Capture, encoding and buffering still affect responsiveness.

![Little M produces successive video chunks from audio while retaining an identity anchor](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-01.png)

## Which model actually reaches real time?

| Model | Output and playback target | Optimized paper pipeline, one H100 | Public code with compile, per README |
|---|---|---|---|
| AURA-1.3B | Described as 576p, 16 fps | 20.7 fps | Approximately 16 fps |
| AURA-5B | Described as 720p, 25 fps | 9.7 fps | Approximately 8 fps |

The smaller model meets playback speed in this setup. The larger one is faster than its teacher but does not keep up with 25 fps playback. It should not be described as a demonstrated real-time 720p system.

Resolution also depends on aspect-ratio buckets. The current small-model configuration selects height–width pairs `(576,576)` or `(512,768)`. Some paper table captions use the label 480p, while its main text and cards say 576p. Inspect actual output dimensions rather than assuming a fixed 16:9 format.

Paper throughput uses a fixed ten-second English audio clip on one H100 and excludes loading and warm-up. Approximately 23× and 17× speedups refer to the respective bidirectional teachers, not arbitrary competing systems or time to first frame. We reproduced none of these GPU measurements and made no consumer-GPU or mobile extrapolation.

## Why can the cache stay bounded?

AURA retains the initial chunk as an anchor and recent local context, evicting older entries. Denoising steps overwrite the current chunk's slot instead of maintaining separate complete histories for every noise level.

In the code, `kv_window=2` includes the current chunk. Allocated space therefore holds the anchor, the previous chunk and the current chunk. This agrees with the paper's description of one recent historical chunk.

Bounded cache growth does not imply tiny total GPU memory. The diffusion model, VAE, text encoder, audio encoder and temporary tensors still require resources. The 1.3B label does not describe the complete system's footprint.

Nor does bounded storage prove indefinite identity stability. The paper's long-form quantitative test lasts 60 seconds. Some small-model samples drift, with mean CSIM falling from 0.83 to 0.78; the larger model falls approximately from 0.76 to 0.69. Duration-independent cache size and persistent visual identity require separate checks.

## Why use two distillation stages?

ODE Teacher Forcing first aligns a student with teacher denoising trajectories while introducing fewer steps and block-causal sliding-window attention. However, inference exposes the student to intermediate states created by its own generation process.

Distribution Matching Distillation with backward simulation then corrects this mismatch using student-generated states. The paper does not add a GAN loss requiring real videos. Few-step inference follows additional training; reducing a teacher's step-count setting alone does not establish equivalent quality.

![Little M first follows teacher trajectories and then checks trajectories created by the student](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-02.png)

The reported training setup uses tens of H100 GPUs. Most application engineers can more readily borrow the causal constraints and cache design than reproduce the full training pipeline.

## What is publicly available?

The release includes two student checkpoints, the small teacher, inference code and a dataset entry. Merged weights and LoRA-only checkpoints serve different purposes. The latter require the appropriate base and preceding stages. Inference also needs the Wan VAE and text encoder plus the corresponding audio encoder.

The dataset card explicitly marks a partial release. It currently describes the 1.3B teacher's ODE latent trajectories: 30,000 training samples and 200 validation samples. The 30K TalkVerse/5B clips and complete associated material described in the paper are marked as forthcoming. Reference images and prompts are not redistributed there and require the appropriate Hallo3 source.

We checked metadata and descriptions, not the roughly terabyte-scale trajectory collection. The paper's release statement should not be rewritten as confirmation that every video and training component is already available.

| Component | Stated license |
|---|---|
| Repository code | Snap Inc. Non-Commercial License |
| AURA-1.3B weights | CC BY-NC 4.0 |
| AURA-5B weights | Snap Inc. Non-Commercial License |
| Dataset | CC BY-NC 4.0, with source terms to inspect |

The presence of Apache-2.0 Wan components does not replace the other components' terms.

Dataset: https://huggingface.co/datasets/kyutai/AURA-Dataset

## What did the local check establish?

We imported the unmodified upstream `aura/kv_cache.py` and advanced synthetic CPU float32 tensors through 100 blocks. Checks covered anchor retention, eviction, recent history, current-slot replacement, K/V values, unchanged storage pointers and shapes, and bounded RoPE indices after a configured cap. All checks passed.

This did not run diffusion, VAE decoding, audio encoding or complete avatar generation. The test used PyTorch 2.14, outside the project's declared 2.6–2.8 range; a component check does not prove full-runtime compatibility. We downloaded no model weights and measured no peak GPU memory, first-frame latency or throughput.

## What remains between the model and a voice agent?

The reference `Aura.generate(image, audio)` accepts file paths and extracts audio features before entering the video loop, then yields video chunks. That is a chunked output interface, not proof of live microphone input, transport and browser playback working together.

The online demo combines AURA with Unmute. A product still needs incremental audio handling, playback clocks, backlog policies, cancellation of stale video after interruptions, and recovery. Record when audio arrives, when the first chunk is playable and whether generation keeps pace thereafter.

The transferable idea is to put streaming constraints into training and cache structure rather than rely solely on inference-time acceleration. Deployment requires hardware-specific validation, appropriate authorization and further system integration.

![Little M coordinates incoming audio, the first video chunk and the playback clock](../../assets/images/aura-streaming-avatar-causal-distillation-guide-fig-03.png)

## FAQ

### Is the repository only a cloud API wrapper?

No. It supplies local inference code requiring CUDA and model weights. Trying the hosted demo does not establish a working self-hosted deployment.

### Is the 720p model already real time?

The reported 9.7 fps is below its 25 fps playback target; reference-code throughput is approximately 8 fps. That setup does not demonstrate sustained real-time playback.

### Does streaming indefinitely guarantee hours of stable operation?

No. Bounded storage supports continued generation, while identity, synchronization and operational stability need further evaluation. The reported long-form quantitative test spans one minute.

Related engineering context: https://blog.mushroom.cv/blog/longcat-video-avatar-16-engineering-guide/

Sources: https://kyutai.org/aura/ ; https://huggingface.co/kyutai/AURA-1.3B ; https://huggingface.co/kyutai/AURA-5B ; full paper https://arxiv.org/html/2611.26540v1

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
