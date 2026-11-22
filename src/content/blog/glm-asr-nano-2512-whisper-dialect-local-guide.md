---
title: "GLM-ASR-Nano-2512：识别轻声与粤语，先看清评测和部署边界"
titleEn: "GLM-ASR-Nano: Quiet Speech, Dialects and Local Inference"
description: "GLM-ASR-Nano-2512 面向普通话、英语与粤语转写，官方强调低音量鲁棒性。本文核对智谱模型卡、代码、权重元数据和五项基准，解释 1.5B 与 HF 2B 标签、约 4.52GB 权重及 4.10 平均错误率的口径，并用本地样本检查推理链路，区分耳语、降低增益、离线文件与实时字幕的实际需求。"
descriptionEn: "Audit GLM-ASR-Nano's quiet-speech claims, dialect support, parameter counts, benchmark averages and local inference limits before choosing it for transcription."
wechatTitle: "GLM-ASR-Nano：轻声转写的边界"
wechatDigest: "核对轻声与粤语识别、权重体积和评测口径，再判断是否适合本地转写。"
pubDate: "2026-11-22"
updatedDate: "2026-11-22"
category: "Tech-News"
tags: ["GLM-ASR", "语音识别", "本地AI", "粤语", "模型评测"]
heroImage: "../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-banner.jpg"
---

GLM-ASR-Nano-2512 是一个可在本地把录音转成文字的模型，值得拿轻声和粤语样本试用；选型时要同时看权重、评测口径和实际录音条件。它来自 Z.ai，代码仓库采用 Apache-2.0，模型卡标注 MIT。

这不是 2026 年 11 月刚发布的模型。Hugging Face 仓库创建时间是 2025 年 12 月 9 日，后续经历了格式迁移。本文按当前快照核对资料，不把旧型号写成新发布，也不把作者成绩当作我们的复测结果。

模型卡：https://huggingface.co/zai-org/GLM-ASR-Nano-2512

官方代码：https://github.com/zai-org/GLM-ASR

封面是本地生成的麦克风场景示意，不是官方实验照片；正文配图用于解释部署与验收方法。

## 1.5B、2B 和文件体积，究竟分别是什么？

官方介绍称它为 1.5B 模型，但当前模型仓库的 Safetensors 元数据显示，完整 BF16 文件存储 2,257,843,200 个张量元素；模型文件为 4,515,776,712 字节，约 4.52GB，或 4.21GiB。

我们读取实际下载文件的张量头，按形状重新求和得到同样的总数，文件 SHA-256 也与官方 LFS 元数据一致。其中文本模型主体约 1.472B，文件另存约 0.121B 的输出头矩阵。检查发现嵌入与输出矩阵内容相同，当前 Transformers 配置绑定这两处权重；实际加载模型去重后的参数计数为 2,136,470,528。因此，文件元素总数与运行时独立参数也需要分开；不能把介绍里的 1.5B 当作整个当前模型的精确计数。HF 页面显示的“2B params”是规模标签，不能翻译成“模型体积 2GB”。

配置也确实包含不同部分：32 层音频编码器、音频到文本的投影，以及 28 层文本解码器。用一个营销数字规划设备内存容易失误。下载文件、权重驻留、音频特征、生成缓存和运行库开销是不同账目，4.52GB 文件不能保证 4.52GB 内存就能完整运行。

这里的元数据核对比纠结名称更有用：部署前锁定权重 revision、检查精度和运行环境；量化版本另行验证准确率，不能把 BF16 的成绩直接贴到量化推理上。

![小M把参数数量、权重文件和运行内存放在三个不同容器里核对](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-01.png)

## 4.10 的成绩，能说明它全面超过 Whisper 吗？

不能。官方对比图给出了五项测试，中文与英文使用 CER/WER，数值越低越好。下面是从图中核对的原始数值，而非 Mycelium Protocol 重新跑出的模型成绩。

| 官方测试 | GLM-ASR-Nano | Whisper V3 |
| --- | ---: | ---: |
| Wenet Meeting | 6.73 | 18.39 |
| Aishell-1 | 1.81 | 4.72 |
| Libri Clean | 2.00 | 1.86 |
| Libri Other | 4.19 | 3.43 |
| Fleurs EN | 5.78 | 6.23 |
| 图中平均 | 4.10 | 6.93 |

五个 GLM 数值的简单算术平均为 4.102，四舍五入得到 4.10。这个计算能复核表格内部是否一致，却不代表按所有音频时长或字数加权的总体错误率。CER 和 WER 的单位也不同，跨集合平均适合观察这张表，不能直接当成某个业务的预计错误率。

它在这张表的两个中文集合上优于 Whisper V3，但在 Libri Clean 和 Libri Other 上落后。表中还有平均 3.67 的 FunAudio-ASR，因此“最低”必须附带作者划定的开源、规模和比较对象范围，不能扩写成所有 ASR 模型第一。

同一 HF 仓库另附 Open ASR Leaderboard 的评测记录，标注 2025 年 12 月 9 日，mean WER 为 7.03、RTFx 为 145.28。它和上面的五项混合平均不是同一测试口径，更不能把 145.28 倍实时率当作个人电脑上的承诺。

## 低音量、耳语和方言，是同一个问题吗？

官方明确写了针对 Whisper/Quiet Speech 的训练，也强调普通话、英语之外的粤语优化。当前公开对比图没有独立的耳语分组、录音声压、麦克风距离或粤语分组结果。因此，合理结论是“值得针对性测试”，而非“已经证明任何悄悄话都准确”。

把正常语音数字音量调低，只改变幅度；真正耳语还会改变发声和频谱。远场、空调噪声、混响与手机降噪又会引入不同失真。软件无法凭空补回麦克风没有采到的信息。

方言也不能只看模型支持列表。粤语夹英语、地名、人名和行业词会改变错误分布。对于会议纪要，漏掉一个“不”、金额或姓名的影响，可能比平均少几个字错误更大。

![小M分别检查轻声、增益降低和背景噪声的不同录音瓶，而没有把它们倒成同一种测试](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-02.png)

## 本地推理应该先验证哪一层？

官方提供 Transformers 和 SGLang 路径，后者可以暴露本地 OpenAI 风格接口。使用 API 协议不等于把音频发到商业云端：请求最终去哪里，取决于服务地址、进程和部署方式。

还要分清版本。仓库保留的 `inference.py` 是旧权重路径，README 将它放在 Transformers 4.51.3 的旧格式说明下；当前模型卡使用 `GlmAsrForConditionalGeneration` 与 `AutoProcessor`。不要把旧脚本和新权重随意拼接。README 也提示 2025 年 12 月 27 日前下载的旧权重需要更新。

当前 processor 配置为 16kHz、128 维音频特征，特征提取器有 30 秒窗口参数。这些配置不等于产品已经具备无限时长转写、词级时间戳、说话人分离或低延迟流式字幕。长会议仍需验证切段、边界重叠、文本拼接和失败恢复。

这次我们确实下载并加载了上述固定权重，在 Apple M4 / 16GB / macOS 26.6.2 上使用 PyTorch 2.14.0、Transformers 5.16.1、MPS 与 FP16 完成本地推理。音频由 ffmpeg 转为 16kHz 单声道数组，HF 离线模式开启，生成上限为 128 token；未测峰值内存，也没有把加载或生成时间包装成速度基准。

| 实际输入 | 本地输出与观察 |
| --- | --- |
| 官方中文样本，6 秒 | “我还能再搞一个，就算是非常小的声音，也能识别准确。” |
| 官方英文样本，10.6 秒 | 与 README 给出的句子一致，仅大小写与标点不同。 |
| 同一中文样本再降低 30dB | “我还能再搞一个，就算是非常小的声音，也能识别正确。” |
| 3 秒数字静音 | 空文本，生成终止 token。 |

结果不是“全部准确”：降音量后，末尾的“准确”变成了“正确”。语义近似仍属于逐字转写差异，不能忽略。数字静音这一次没有产生文字，也不足以保证所有静音和背景噪声都不幻听。

这四个输入验证了当前权重与本地推理链路能工作，并保留了一个衰减后的失败细节。没有录制新的真人耳语，没有测试粤语，没有重跑五项基准，也没有在相同设备上对比 Whisper。源代码、权重哈希、样本哈希、运行脚本与完整输出已留档，读者可以按相同版本复核。

## 给实际项目的建议是什么？

Mycelium Protocol 的建议是先做小型、配对的业务验收集：正常音量、真人轻声、正常语音降低增益、同一环境加噪声分别保留；普通话与粤语分开统计，并单列否定词、数字、专有名词和静音误报。

每一组用相同音频对比候选模型，记录输入采样率、切段策略、精度、设备、耗时、峰值内存和完整转写。不要只挑成功示例。几十条样本能发现明显不匹配，但不足以证明一般化优势；最终门槛应由任务容错和人工复核成本决定。

如果你要做本地语音输入，它是一个值得加入候选表的模型。如果你要做实时会议助手，ASR 只是其中一环，还需要 VAD、增量结果、时间信息、说话人处理与延迟控制。把转写模型放进完整流水线后再验收，才能知道它究竟解决了哪一段问题。

![小M先用小录音样本验收转写，再连接切段、复核和交付环节](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-03.png)

## 常见问题

### 可以完全本地运行吗？

权重和依赖下载完成后，Transformers 可以在本地读取模型与音频。离线与否还取决于应用是否调用远程音频地址、额外云服务，以及是否真正禁止联网；本地 API 只是接口形式。

### 低音量识别好，是否等于耳语一定准确？

不等于。低增益、真人耳语、远场和噪声是不同条件，官方训练声明不能代替针对你的麦克风、语言和环境做配对验证。

### 商用许可证怎么看？

当前 GitHub 代码仓库提供 Apache-2.0 LICENSE，HF 模型元数据标注 MIT，但当前快照没有独立的 LICENSE 文件。分发时分别保存代码许可和权重声明，不把代码许可证自动套到所有权重、音频和第三方组件。

延伸阅读：本地 ASR 选型还可以对照 Rumble-2-Flash 的测试范围：https://blog.mushroom.cv/blog/rumble-2-flash-small-asr-phone-call-benchmarks/

资料与核验版本：GitHub `a324aa59a30952c54e8097c85efea592b7fafd81`；HF `61ba4e0b3309b6656edea3e93e419f7bd5c61957`。官方基准图与 `.eval_results/open_asr_leaderboard.yaml` 分别对应不同口径，本文保留这一差异。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

GLM-ASR-Nano-2512 converts recorded speech into text locally and is worth evaluating for quiet Mandarin and Cantonese input. Z.ai publishes the code under Apache-2.0; the Hugging Face model metadata says MIT. Choosing it requires checking the weights, evaluation scope and recording conditions together.

This is not a newly released November 2026 model. The HF repository was created on December 9, 2025, and subsequently migrated its weight format. This article audits current artifacts and separates author-reported scores from our own checks.

Model: https://huggingface.co/zai-org/GLM-ASR-Nano-2512

Code: https://github.com/zai-org/GLM-ASR

The cover is a locally generated microphone illustration, not an official experiment photograph. Body illustrations explain deployment and evaluation concepts.

## What do 1.5B, 2B and the download size mean?

The introduction calls this a 1.5B model. However, current Safetensors metadata reports 2,257,843,200 stored BF16 tensor elements for the complete artifact. Its weight file is 4,515,776,712 bytes: approximately 4.52GB or 4.21GiB. We independently summed tensor shapes from the downloaded header and verified its SHA-256 against official LFS metadata. The language-model body contains approximately 1.472B elements and the file separately stores a 0.121B output-head matrix. After loading, the deduplicated runtime parameter count is 2,136,470,528. The stored embedding and output matrices are identical, and the current Transformers configuration ties them. Stored elements and unique runtime parameters therefore require separate accounting. The introduction’s 1.5B label is not an exact count of this complete current artifact. The Hub’s rounded “2B params” label is not a 2GB file-size claim.

The configuration contains a 32-layer audio encoder, an audio projection and a 28-layer text decoder. These components make it especially important to count the actual deployed artifact. Download size, resident weights, audio features, generation caches and runtime overhead are separate budgets. A 4.52GB file does not establish a 4.52GB RAM requirement.

Pin the revision and precision before estimating hardware. A quantized derivative needs its own accuracy check; BF16 benchmark numbers do not automatically carry over.

![Little M checks parameter counts, weight files and runtime memory in three separate containers](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-01.png)

## Does 4.10 establish a universal win over Whisper?

No. The author's comparison image mixes Chinese character error rates and English word error rates across five datasets. These are reported results, not a benchmark rerun by Mycelium Protocol.

| Author benchmark | GLM-ASR-Nano | Whisper V3 |
| --- | ---: | ---: |
| Wenet Meeting | 6.73 | 18.39 |
| Aishell-1 | 1.81 | 4.72 |
| Libri Clean | 2.00 | 1.86 |
| Libri Other | 4.19 | 3.43 |
| Fleurs EN | 5.78 | 6.23 |
| Reported average | 4.10 | 6.93 |

The five GLM values average to 4.102 and round to 4.10. This verifies arithmetic consistency, not a duration-weighted or reference-token-weighted error rate across all recordings. Mixing CER and WER also makes the mean unsuitable as a forecast for an arbitrary application.

GLM wins both Chinese datasets in this comparison and loses both Libri subsets. Another listed model, FunAudio-ASR, scores 3.67 overall. Any “lowest” claim therefore needs the author's restrictions on model size, openness and comparison set; it cannot mean the best ASR model in every setting.

The same HF repository includes a separate Open ASR Leaderboard record dated December 9, 2025: mean WER 7.03 and RTFx 145.28. Different suites can produce different averages without contradiction. Neither that throughput nor the five-row mean is a promise about a personal computer.

## Are quiet speech, whispering and dialects interchangeable tests?

The official description explicitly mentions training for Whisper/Quiet Speech and optimization for Cantonese alongside Mandarin and English. The public comparison image does not isolate whisper recordings, sound levels, microphone distances or Cantonese results. It supports a targeted evaluation, rather than a guarantee about every whispered recording.

Digitally attenuating normal speech changes amplitude. Actual whispering also changes how speech is produced and its spectrum. Distance, room reverberation, background noise and device noise reduction introduce further differences. A model cannot recover information that the microphone never captured.

Dialect evaluation also needs realistic vocabulary. Cantonese mixed with English, names and domain terms can behave differently from a support-list label. Missing a negation or an amount can matter more than a modest improvement in aggregate error rate.

![Little M keeps actual quiet speech, reduced gain and noisy recordings in separate test containers](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-02.png)

## Which layer should a local deployment verify first?

The repository documents Transformers and SGLang. A local SGLang endpoint can expose an OpenAI-style API without sending audio to a commercial cloud. The protocol name says nothing about the destination; inspect the configured address and deployment.

Match the code path to the checkpoint. The retained `inference.py` belongs to the older Transformers 4.51.3 weight format, while the current card uses `GlmAsrForConditionalGeneration` and `AutoProcessor`. The README explicitly asks users who downloaded weights before December 27, 2025, to update them. Mixing old scripts with current checkpoints is an avoidable source of failures.

The processor specifies 16kHz audio and 128 feature bins, with a 30-second feature-extractor window parameter. These settings do not establish unlimited recording support, word timestamps, diarization or incremental live captions. Long meetings still require tested segmentation, overlap, joining and recovery behavior.

We downloaded and loaded the pinned weights on an Apple M4 with 16GB memory, running macOS 26.6.2, PyTorch 2.14.0 and Transformers 5.16.1. Actual inference used MPS and FP16. ffmpeg supplied 16kHz mono arrays, HF offline mode was enabled, and generation was capped at 128 tokens. We did not measure peak memory or report a speed benchmark.

| Actual input | Observed output |
| --- | --- |
| Official Chinese clip, 6 seconds | 我还能再搞一个，就算是非常小的声音，也能识别准确。 |
| Official English clip, 10.6 seconds | The README sentence, with capitalization and punctuation differences only. |
| Same Chinese clip attenuated by 30dB | 我还能再搞一个，就算是非常小的声音，也能识别正确。 |
| Three seconds of digital silence | Empty text and an end token. |

The attenuated sample changed the final Chinese word from “准确” to “正确”. Similar meaning does not make it an exact transcription. The silence case produced no text once; it does not guarantee absence of hallucinations on silence or background noise generally.

These four inputs establish a working local inference path and expose one attenuation-related transcription difference. They are not a Cantonese evaluation, a newly recorded whisper test, a rerun of the five benchmarks or a paired Whisper comparison. We preserved code, weight and sample hashes, the runner and complete outputs for reproduction.

## How should a team evaluate it for a real application?

Mycelium Protocol recommends a small paired acceptance set with separate groups for normal speech, actual quiet speech, attenuated normal speech and added noise. Keep Mandarin and Cantonese results separate. Track numbers, negations, proper names and silence false positives explicitly.

Use identical recordings for competing models and record sampling rate, segmentation, precision, device, latency, peak memory and complete output. Keep failures. A few dozen examples can reveal an obvious mismatch but cannot establish broad superiority; acceptance thresholds should follow task risk and human correction costs.

For local dictation, GLM-ASR-Nano is a reasonable candidate to investigate. For a live meeting assistant, it supplies only one component. VAD, incremental output, timestamps, speaker handling and latency control still need their own implementation and evaluation.

![Little M validates a small recording set before connecting segmentation, human review and delivery](../../assets/images/glm-asr-nano-2512-whisper-dialect-local-guide-fig-03.png)

## FAQ

### Can it run entirely locally?

Transformers can read local weights and recordings after dependencies are available. Actual offline behavior also depends on remote audio URLs, additional services and network settings. A local API is simply an interface, not evidence that every application component stays offline.

### Does low-volume robustness guarantee whisper recognition?

No. Attenuation, actual whispering, far-field speech and noise require separate tests. An author training statement cannot replace paired recordings from the intended microphones, language and environment.

### Which license applies?

The GitHub code includes an Apache-2.0 LICENSE. HF model metadata says MIT, but the audited snapshot does not contain a separate LICENSE file. Preserve the code license and model declaration separately and check audio and dependency terms independently when redistributing.

Related evaluation context: https://blog.mushroom.cv/blog/rumble-2-flash-small-asr-phone-call-benchmarks/

Audited revisions: GitHub `a324aa59a30952c54e8097c85efea592b7fafd81`; HF `61ba4e0b3309b6656edea3e93e419f7bd5c61957`. The official comparison image and `.eval_results/open_asr_leaderboard.yaml` use different evaluation scopes.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
