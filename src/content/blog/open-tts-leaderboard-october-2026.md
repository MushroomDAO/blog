---
title: "开源TTS十强：10月英语榜与中文对照"
titleEn: "Open TTS Top 10: October English and Chinese Rankings"
description: "核对Hugging Face Open TTS Leaderboard 的2026年10月9日官方快照，列英语非克隆和中文Top10，比较声音克隆SIM、H200批量吞吐、A100与CPU首音延迟，解释语言、测试集、推理引擎与许可差异。本文保存接口证据，不重跑模型，区分客观评测、主观听感及部署条件，供语音项目筛选候选。"
descriptionEn: "Review the October Open TTS Leaderboard: English and Chinese Top 10, voice cloning, A100 and CPU latency, plus reproducible sources and deployment caveats."
wechatTitle: "开源TTS十强：10月英语榜与中文对照"
wechatDigest: "核对官方10月快照，比较英语、中文、克隆与流式延迟，说明Top10的适用范围。"
pubDate: "2026-10-16"
updatedDate: "2026-10-16"
category: "Tech-News"
tags: ["TTS", "Hugging Face", "语音合成", "开源模型", "模型评测"]
heroImage: "../../assets/images/open-tts-leaderboard-october-2026-banner.jpg"
---

Open TTS Leaderboard 把开源语音合成模型放到同一套文本、识别器与硬件上比较，帮助开发者先筛出候选。我们核验了 2026 年 10 月 16 日可读取的官方结果：最新登记快照是 **10 月 9 日**，默认英语非克隆榜前三是 Kokoro-82M、Paradee-8M-v1.0、Supertonic 3；Fish S2 Pro 排第四。它衡量可理解性、吞吐与声音相似度，不等于“最好听”的总榜。

> 阅读范围：本文整理官方公开评测，实际调用在线 Space 的公开接口并检查其数据聚合代码；没有下载模型推理、重新跑语音测试或进行主观试听打分。你提供的 iPhoneMirror 链接含省略号，字面地址返回 404，与本篇榜单无关，未据此推断项目内容。

## 10 月版本更新了什么？

官方介绍发布于 9 月 30 日，而 Space 的版本选择器还保留更早的实验快照。我们固定选择 `09-10-2026`，没有用 `latest` 做不可追溯的引用。结果数据登记 revision 为 `dd84b35e719440b53c06a9cef8e178e2c6950731`。

10 月 9 日的变更包括新增 LiquidAI/LFM2.5-Audio-1.5B 与 Paradee-8M-v1.0、加入 audio.cpp 流式引擎、增加 A100 流式评测并暂停 H200 流式测试，以及调整 MOSS TTS 的提示词。这里的“暂停 H200”针对 Streaming，不是取消主榜 H200 批量评测。新模型、引擎和提示词都可能改变排名，因此不能直接照搬首发新闻里的前三名。

官方入口：https://huggingface.co/spaces/hf-audio/open_tts_leaderboard

版本与聚合代码：https://huggingface.co/spaces/hf-audio/open_tts_leaderboard/blob/27639f0ab3cc57aaa194770fe5dc9a0b5595fd52/leaderboard_data.py

## 先定规则，再看 Top 10

本篇主表采用官方默认设置：English、Seed-TTS 与 CV3-Eval、关闭 Voice cloning，按平均 WER 升序。英语是在两个测试集上分别算错词率，再对两个分数取平均；不是把所有句子拼起来重新算一次，也没有加权揉入速度、参数量或声音相似度。

只有覆盖所选语言和适用测试集的模型才有完整排名；缺测不能当作零错误。Seed-TTS 只有中英，CV3-Eval 覆盖九种语言；再勾更多语言，参评范围与平均分就会变。英文界面单语言中文表头仍可能写 Average WER，实际中文度量是 CER，下面按字符错误率标注。

![小M按语言、测试集和克隆模式选择同一把尺子](../../assets/images/open-tts-leaderboard-october-2026-fig-01.png)

## 英语非克隆 Top 10：小模型依然有竞争力

| 排名 | 模型／评测变体 | 英语 WER（%）↓ | H200 RTFx ↑ |
| --- | --- | --- | --- |
| 1 | hexgrad/Kokoro-82M | 1.46 | 71.15 |
| 2 | sahilmahendrakar/Paradee-8M-v1.0 | 1.47 | 5.85 |
| 3 | Supertone/supertonic-3 | 1.54 | 47.32 |
| 4 | fishaudio/s2-pro | 1.58 | 0.4 |
| 5 | k2-fsa/OmniVoice | 1.61 | 37.56 |
| 6 | kyutai/pocket-tts | 1.62 | 9.09 |
| 7 | FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL) | 1.68 | 5.88 |
| 8 | ResembleAI/chatterbox (ChatterboxTTS) | 1.7 | 2.07 |
| 9 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice | 1.71 | 13.32 |
| 10 | BreezeBlue/Breeze-TTS-2 | 1.72 | 3.32 |

以上是官方 10 月 9 日快照的显示值，保留两位小数；不是我们的模型实测。RTFx 越大代表生成吞吐越高，71.15 表示按该评测路径每秒计算产出约 71.15 秒音频。支持批量的后端通常用 batch 32，其余用 batch 1，因此这一列比较的是各评测配置的吞吐，不能直接推出单用户首音速度。表中也是跨测试集 RTFx 的算术平均，不是把两个测试集合并后用总音频时长除总计算时间。

这里有三个值得工程团队注意的变化。第一，Paradee 进入第二名，Kokoro 与它只差 0.01 个百分点；没有置信区间或显著性检验，不能据此宣布前者必然更可靠。第二，Qwen3-TTS CustomVoice 进入第九，Breeze TTS 2 第十，与个别演示里的听感判断并不矛盾，评价目标不同。第三，S2 Pro 在这条 H200 路径的 RTFx 为 0.40，低于实时生成要求；这不能外推成它在所有推理引擎、量化和硬件上都只能这么快。

参数量和许可证也不能盲抄榜单元数据。例如 CosyVoice3 行显示 0.11B、CC BY 4.0，而链接到的官方模型卡标注 0.5B、Apache 2.0；“(RL)”是评测变体标签。我们保留原始行名与分数，不把元数据冲突改写成新结论。部署前应定位到实际检查点和对应代码、权重许可，而不是只看榜单一个字段。

## 做中文项目：另看这张 Top 10

| 排名 | 模型／评测变体 | 中文 CER（%）↓ | H200 RTFx ↑ |
| --- | --- | --- | --- |
| 1 | k2-fsa/OmniVoice | 0.92 | 48.45 |
| 2 | tencent/AuK | 0.93 | 7.67 |
| 3 | FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL) | 0.99 | 2.76 |
| 4 | OpenMOSS-Team/MOSS-TTS | 1.02 | 25.37 |
| 5 | tencent/AuK-Flash | 1.03 | 44.34 |
| 6 | fishaudio/s2-pro | 1.09 | 0.4 |
| 7 | openbmb/VoxCPM2 | 1.11 | 1.77 |
| 8 | Qwen/Qwen3-Omni-30B-A3B-Instruct | 1.14 | 11.98 |
| 9 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice | 1.15 | 14.58 |
| 10 | BreezeBlue/Breeze-TTS-2 | 1.17 | 3.29 |

口径仍是两个测试集、非克隆模式，改为 Chinese，按 CER 升序。OmniVoice 的 0.92% 与 AuK 的 0.93% 同样只是这个快照的观测差距。Kokoro 英语领先，并不能自动推出它适合中文业务；表中缺席也不是零分或质量判死刑。

对于中文客服或短旁白，我会先把 AuK、AuK-Flash、CosyVoice3、Qwen3-TTS 放进候选，再按克隆需求、引擎、许可和目标机器缩小范围。这是由榜单推导的选型路径，不是本机验收结论。OmniVoice 在榜单标注非商业许可，Fish 与 Breeze 列为自定义许可；“能下载权重”和“可直接用于商业服务”需要分别核对。

## 克隆模式：WER 第一不等于最像原声

| WER 排名 | 模型／变体 | 英语 WER（%）↓ | SIM ↑ |
| --- | --- | --- | --- |
| 1 | bosonai/higgs-tts-3-4b | 1.59 | 64.69 |
| 2 | k2-fsa/OmniVoice | 1.69 | 71.98 |
| 3 | Qwen/Qwen3-TTS-12Hz-1.7B-Base | 1.81 | 69.33 |
| 4 | openbmb/VoxCPM2 | 1.82 | 70.87 |
| 5 | fishaudio/s2-pro | 1.82 | 62.03 |

这张表仍按英语克隆 WER 排序，SIM 只是旁列。比如 Higgs 的 WER 第一，但 SIM 为 64.69；同一模式下 AuK 的 SIM 为 75.08、WER 为 2.07%，并不在这张 WER 前五里。不能把“WER 排名”直接叫“克隆质量排名”。SIM 数字按界面原尺度照录，绝不是“多少比例的人认为声音一样”。

识别器能听清，并不说明情绪、重音、节奏和长句停顿自然；说话人嵌入接近，也不说明听众偏好更高。当前默认英语 Top 10 未出现的模型，例如 Drama 3，不能因为未入此表就宣布被击败。请先核对是否有覆盖相同条件的实际结果。

![小M分别测量听清、像谁和表达感，不合成单一奖杯](../../assets/images/open-tts-leaderboard-october-2026-fig-02.png)

## 语音 Agent 更该看哪一列：A100 与 CPU 首音延迟

新版本 A100 流式页按 TTFA p95 排序，部分前列如下：

| p95 排名 | 模型／引擎 | TTFA p95（ms）↓ | p50（ms）↓ | RTFx ↑ |
| --- | --- | --- | --- | --- |
| 1 | Serveurperso/Qwen3-TTS-GGUF¹ | 25.1 | 20.9 | 5.83 |
| 2 | LiquidAI/LFM2.5-Audio-1.5B (audio.cpp)² | 28.7 | 26.6 | 8.76 |
| 3 | kyutai/pocket-tts (audio.cpp)³ | 33.5 | 29.2 | 11.07 |
| 4 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice (photon)⁴ | 34.3 | 33.1 | 9.36 |
| 5 | kyutai/pocket-tts | 44.0 | 41.0 | 6.49 |
| 6 | BreezeBlue/Breeze-TTS-2 | 46.5 | 44.1 | 2.49 |

上标是官方引擎注释，不是模型代际。第一行 GGUF 项注明 1.7B、`chunk_size=12`、BF16；不能看到 GGUF 就自动说它用了低比特量化。audio.cpp 与 Photon 是不同推理路径，同一个模型会出现多行，不能把这些行当成独立基础模型凑 Top 10。

引擎参考：audio.cpp https://github.com/0xShug0/audio.cpp ；Photon https://moondream.ai/blog/photon-can-now-speak 。

CPU 页只有八条有测量值的配置，我们列前四，不能为了“CPU 十强”补两个没有结果的名字：

| p95 排名 | 模型／引擎 | TTFA p95（ms）↓ | p50（ms）↓ | RTFx ↑ |
| --- | --- | --- | --- | --- |
| 1 | kyutai/pocket-tts | 164.9 | 125.9 | 3.19 |
| 2 | kyutai/pocket-tts (audio.cpp)¹ | 182.3 | 73.6 | 2.49 |
| 3 | LiquidAI/LFM2.5-Audio-1.5B (audio.cpp)² | 341.1 | 273.6 | 1.2 |
| 4 | sahilmahendrakar/Paradee-8M-v1.0 | 996.9 | 390.1 | 11.48 |

两条 Pocket TTS 很能说明问题：audio.cpp 的中位数更小，73.6ms 对 125.9ms；但 p95 更大，182.3ms 对 164.9ms，因此按尾延迟排序反而在后。只报道一个最快数字，会隐去长尾体验。

A100 与 CPU 流式测试使用 CV3-Eval 英语 500 条，前三条预热，剩余 497 条统计，batch 1、默认音色、非克隆。A100 是 80GB GPU，CPU 是 HF Jobs 的 8 vCPU / 32GB 配置；这些数值不是 RTX 5090、Mac 或你的业务服务器成绩。历史 H200 流式页仅抽 47 条、只报 p50，又与新页不同。非流式模型要等整段生成结束才能播，界面 TTFA 相应记到生成完成；它的首音不能和真正流式实现混为一谈。

![小M用两只沙漏区分一批音频吞吐与第一个声音的等待](../../assets/images/open-tts-leaderboard-october-2026-fig-03.png)

## 如何把榜单变成部署决策？

先确定语种、固定音色还是声音克隆，再决定批量生产还是实时对话。批量旁白关心可理解性和吞吐；对话关心首音的 p50、p95，以及生成能否持续快于播放。接着锁定模型检查点、推理引擎、硬件、batch、精度和文本长度，才能把线上数据与榜单配置对照。

我的独立判断是：榜单最有价值的产物是一个可解释的候选集。英语固定音色可先看 Kokoro、Paradee、Supertonic；CPU 英语对话优先研究 Pocket TTS 及其引擎差异；中文场景单独筛 CER 与实际服务条件。不要把非克隆的 CustomVoice 结果套到 Base 克隆版，也不要用低 WER 代替专业术语、数字读法或表达控制的验收。

评测工程上，ASR 采用 Qwen3-ASR-1.7B，误差也包含识别器与文本归一化的影响。SIM 使用 Seed-TTS Eval 对应的 WavLM-large + ECAPA-TDNN 路径，不能与旧版另一种 WavLM 嵌入尺度混比较。脚本仓已公开，但结果 CSV 仓和部分测试集拷贝并非匿名可下载；代码公开并不等于全部原始数据可直接再分发。

## 常见问题

### 这是“10 月 16 日新一轮实测”吗？

不是。10 月 16 日是我们抓取并核验公开接口的日期；选择的固定官方结果版本是 10 月 9 日。本文没有重新运行任何 TTS 模型。我们保存了查询参数、接口返回、源代码 revision 与排名提取脚本，便于复查。

### WER 1.46% 是 98.54% 的句子全对吗？

不是。WER 是词级插入、删除和替换错误相对参考词数的比例，不是整句通过率，也不是人类满意度；它甚至可能超过 100%。中文 CER 对字符计算。

### 哪个模型综合最好听？

这套客观榜不能回答。它能帮助筛选是否读清楚、生成多快、是否保留说话人身份；听感、情绪和产品体验还需要另行证据。

## 官方来源与 Top 10 项目入口

官方介绍：https://huggingface.co/blog/open-tts-leaderboard

评测脚本：https://github.com/huggingface/open-tts-leaderboard

本次核验代码提交：`2b2cd31257d22e00af4af585a1f447351c0e713c`。Space 提交：`27639f0ab3cc57aaa194770fe5dc9a0b5595fd52`。结果登记 revision 如上；公开结果通过 Space 正常接口读取，没有访问私有仓库权限。

- hexgrad/Kokoro-82M：https://huggingface.co/hexgrad/Kokoro-82M ；代码：https://github.com/hexgrad/kokoro
- sahilmahendrakar/Paradee-8M-v1.0：https://huggingface.co/sahilmahendrakar/Paradee-8M-v1.0 ；代码：https://github.com/sahilmahendrakar/paradee
- Supertone/supertonic-3：https://huggingface.co/Supertone/supertonic-3 ；代码：https://github.com/supertone-oss-archive/supertonic
- fishaudio/s2-pro：https://huggingface.co/fishaudio/s2-pro ；代码：https://github.com/fishaudio/fish-speech
- k2-fsa/OmniVoice：https://huggingface.co/k2-fsa/OmniVoice ；代码：https://github.com/k2-fsa/OmniVoice
- kyutai/pocket-tts：https://huggingface.co/kyutai/pocket-tts ；代码：https://github.com/kyutai-labs/pocket-tts
- FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL)：https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 ；代码：https://github.com/QwenAudio/CosyVoice
- ResembleAI/chatterbox (ChatterboxTTS)：https://huggingface.co/ResembleAI/chatterbox ；代码：https://github.com/resemble-ai/chatterbox
- Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice：https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice ；代码：https://github.com/QwenLM/Qwen3-TTS
- BreezeBlue/Breeze-TTS-2：https://huggingface.co/BreezeBlue/Breeze-TTS-2 ；代码：https://github.com/breezeblue-ai/breeze-tts

Pocket TTS 模型页本次匿名请求返回 401，入口按官方榜单保留，代码仓可以公开读取；没有冒充读取到其受限模型卡。以上每个地址对应榜单行的模型或变体，许可字段以目标检查点为准。

延伸阅读：我们此前的三款本地 TTS 比较，讨论了主观演示、硬件和公开评测不能混用的问题。
https://blog.mushroom.cv/blog/drama3-breeze2-fish-s2-comparison/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

The Open TTS Leaderboard compares open speech synthesis models using common texts, a reference recognizer and documented hardware. We queried the official Space on October 16, 2026 and selected its latest registered snapshot, **October 9**. The default English, non-cloning leaders are Kokoro-82M, Paradee-8M-v1.0 and Supertonic 3; Fish S2 Pro is fourth. This is an intelligibility ranking, not a universal listening-preference chart.

Scope: we retrieved public benchmark outputs and inspected the aggregation code. We did not run TTS inference, repeat the benchmark or conduct listening tests. The supplied iPhoneMirror URL was truncated and returned 404 literally; it is unrelated to this review.

## Which October update is this?

The September 30 announcement describes the launch. The Space retains earlier experimental snapshots and now offers `09-10-2026`, pinned to results revision `dd84b35e719440b53c06a9cef8e178e2c6950731`. The update adds LFM2.5-Audio-1.5B and Paradee, audio.cpp streaming paths and A100 streaming evaluation, pauses H200 streaming, and changes the MOSS TTS prompt. Batch evaluation still uses H200. A release announcement and a later data snapshot are different records.

Official Space: https://huggingface.co/spaces/hf-audio/open_tts_leaderboard

Pinned aggregation source: https://huggingface.co/spaces/hf-audio/open_tts_leaderboard/blob/27639f0ab3cc57aaa194770fe5dc9a0b5595fd52/leaderboard_data.py

## Define the ranking before choosing a winner

The main table selects English, both Seed-TTS and CV3-Eval, and voice cloning off. Rank follows the ascending mean of the two dataset WERs, not a composite of speed, size and voice similarity. Models need complete coverage of the selected applicable datasets and languages to receive a headline rank. Missing measurements are not zero errors. Seed-TTS covers English and Chinese; CV3-Eval covers nine languages. Chinese is scored with CER, despite a generic Average WER heading in the single-language interface.

![Xiao M selects a shared ruler for language, datasets and cloning mode](../../assets/images/open-tts-leaderboard-october-2026-fig-01.png)

## English non-cloning Top 10

| Rank | Model / evaluated variant | English WER (%)↓ | H200 RTFx ↑ |
| --- | --- | --- | --- |
| 1 | hexgrad/Kokoro-82M | 1.46 | 71.15 |
| 2 | sahilmahendrakar/Paradee-8M-v1.0 | 1.47 | 5.85 |
| 3 | Supertone/supertonic-3 | 1.54 | 47.32 |
| 4 | fishaudio/s2-pro | 1.58 | 0.4 |
| 5 | k2-fsa/OmniVoice | 1.61 | 37.56 |
| 6 | kyutai/pocket-tts | 1.62 | 9.09 |
| 7 | FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL) | 1.68 | 5.88 |
| 8 | ResembleAI/chatterbox (ChatterboxTTS) | 1.7 | 2.07 |
| 9 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice | 1.71 | 13.32 |
| 10 | BreezeBlue/Breeze-TTS-2 | 1.72 | 3.32 |

These are the official displayed values, not our inference measurements. H200 RTFx measures generated audio seconds per compute second: 71.15 means roughly 71.15 seconds of audio output per second in that evaluation path. Batching backends generally use batch 32; others use batch 1. This compares throughput configurations, not identical single-request latency. Displayed RTFx is also averaged across datasets rather than recomputed from their combined audio and compute totals.

Kokoro leads Paradee by only 0.01 percentage points. Without confidence intervals or significance testing, the display gap cannot establish reliable superiority. Qwen3-TTS CustomVoice ranks ninth and Breeze tenth; that does not contradict a different listening preference. Fish S2 Pro's 0.40 RTFx is below real time in this measured path, but does not establish the performance of every engine, precision or deployment.

Metadata also needs checking. The CosyVoice3 row reports 0.11B and CC BY 4.0, whereas its linked official card identifies the 0.5B checkpoint and Apache 2.0. The RL suffix is an evaluation variant. We preserve the row label and score rather than treating inconsistent metadata as a verified parameter count or license conclusion.

## Chinese non-cloning Top 10

| Rank | Model / evaluated variant | Chinese CER (%)↓ | H200 RTFx ↑ |
| --- | --- | --- | --- |
| 1 | k2-fsa/OmniVoice | 0.92 | 48.45 |
| 2 | tencent/AuK | 0.93 | 7.67 |
| 3 | FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL) | 0.99 | 2.76 |
| 4 | OpenMOSS-Team/MOSS-TTS | 1.02 | 25.37 |
| 5 | tencent/AuK-Flash | 1.03 | 44.34 |
| 6 | fishaudio/s2-pro | 1.09 | 0.4 |
| 7 | openbmb/VoxCPM2 | 1.11 | 1.77 |
| 8 | Qwen/Qwen3-Omni-30B-A3B-Instruct | 1.14 | 11.98 |
| 9 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice | 1.15 | 14.58 |
| 10 | BreezeBlue/Breeze-TTS-2 | 1.17 | 3.29 |

This switches the language while retaining both datasets and non-cloning mode. OmniVoice leads at 0.92%, followed by AuK at 0.93%. English leadership does not imply Chinese leadership; absence from this selection is not a zero score. For Chinese deployments, AuK, AuK-Flash, CosyVoice3 and Qwen3-TTS form useful initial candidates, subject to the target checkpoint, engine, license and machine. This is our selection analysis, not local acceptance testing. The leaderboard marks OmniVoice non-commercial and Fish and Breeze custom-licensed; downloadable weights alone do not establish commercial permission.

## Voice cloning changes both the candidates and the question

| WER rank | Model / variant | English WER (%)↓ | SIM ↑ |
| --- | --- | --- | --- |
| 1 | bosonai/higgs-tts-3-4b | 1.59 | 64.69 |
| 2 | k2-fsa/OmniVoice | 1.69 | 71.98 |
| 3 | Qwen/Qwen3-TTS-12Hz-1.7B-Base | 1.81 | 69.33 |
| 4 | openbmb/VoxCPM2 | 1.82 | 70.87 |
| 5 | fishaudio/s2-pro | 1.82 | 62.03 |

This table is sorted by English cloning WER, not SIM. Higgs leads WER at 1.59 with SIM 64.69. AuK scores SIM 75.08 with WER 2.07 and falls outside this WER top five. SIM values retain the interface scale; they are not percentages of listeners convinced by a cloned voice. Recognizable words and similar speaker embeddings do not directly establish natural timing, emotion or preference. A model absent from this selection, including Drama 3, has not thereby lost a controlled comparison.

![Xiao M measures intelligibility, speaker identity and expression separately](../../assets/images/open-tts-leaderboard-october-2026-fig-02.png)

## Streaming: inspect A100 and CPU first-audio latency

Leading A100 configurations, sorted by p95 TTFA:

| p95 rank | Model / engine | TTFA p95 (ms)↓ | p50 (ms)↓ | RTFx ↑ |
| --- | --- | --- | --- | --- |
| 1 | Serveurperso/Qwen3-TTS-GGUF¹ | 25.1 | 20.9 | 5.83 |
| 2 | LiquidAI/LFM2.5-Audio-1.5B (audio.cpp)² | 28.7 | 26.6 | 8.76 |
| 3 | kyutai/pocket-tts (audio.cpp)³ | 33.5 | 29.2 | 11.07 |
| 4 | Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice (photon)⁴ | 34.3 | 33.1 | 9.36 |
| 5 | kyutai/pocket-tts | 44.0 | 41.0 | 6.49 |
| 6 | BreezeBlue/Breeze-TTS-2 | 46.5 | 44.1 | 2.49 |

Superscripts identify official engine notes. The GGUF row specifies the 1.7B model, chunk_size 12 and BF16; GGUF does not automatically imply low-bit quantization. audio.cpp and Photon are runtime paths. Multiple rows for a model are not separate foundation models.

Engine references: audio.cpp https://github.com/0xShug0/audio.cpp ; Photon https://moondream.ai/blog/photon-can-now-speak .

The CPU page has eight measured configurations, not ten. Its first four are:

| p95 rank | Model / engine | TTFA p95 (ms)↓ | p50 (ms)↓ | RTFx ↑ |
| --- | --- | --- | --- | --- |
| 1 | kyutai/pocket-tts | 164.9 | 125.9 | 3.19 |
| 2 | kyutai/pocket-tts (audio.cpp)¹ | 182.3 | 73.6 | 2.49 |
| 3 | LiquidAI/LFM2.5-Audio-1.5B (audio.cpp)² | 341.1 | 273.6 | 1.2 |
| 4 | sahilmahendrakar/Paradee-8M-v1.0 | 996.9 | 390.1 | 11.48 |

Pocket TTS illustrates the median-versus-tail distinction: audio.cpp has the lower p50, 73.6ms versus 125.9ms, but the higher p95, 182.3ms versus 164.9ms. Reporting only the median hides that tradeoff.

A100 and CPU use the English CV3-Eval split: 500 examples, three warm-ups and 497 measured requests, batch 1 and default voices without cloning. Hardware is an 80GB A100 or HF Jobs CPU with 8 vCPU and 32GB RAM. These are not Mac or RTX 5090 results. The paused historical H200 streaming run subsampled 47 examples and reports only p50. For non-streaming models, first playable audio arrives only after full generation, so their TTFA is measured to completion.

![Xiao M separates total audio throughput from waiting for the first sound](../../assets/images/open-tts-leaderboard-october-2026-fig-03.png)

## Turn the benchmark into an engineering shortlist

Choose language and cloning mode, then distinguish offline production from live conversation. Batch narration prioritizes intelligibility and throughput; interactive agents need p50 and p95 first-audio latency plus sustained generation faster than playback. Record checkpoint, engine, precision, hardware, batch and text length before comparing deployment results.

Our reading is that Kokoro, Paradee and Supertonic deserve initial consideration for English fixed voices; Pocket TTS deserves investigation for CPU English conversation; Chinese requires its own CER shortlist. CustomVoice results cannot stand in for a Base voice-cloning checkpoint. Low WER does not certify terminology, number reading or expressive control.

Qwen3-ASR-1.7B and text normalization contribute to measured WER. SIM uses the Seed-TTS Eval WavLM-large plus ECAPA-TDNN path; legacy embeddings on another scale are deliberately excluded by the code. Evaluation scripts are now public, although the result CSV repository and some dataset copies are private. Public code does not make every underlying data artifact freely redistributable.

## Frequently asked questions

### Did we run an October 16 model evaluation?

No. October 16 is our retrieval date. October 9 is the selected official result snapshot. We saved request parameters, public responses and pinned sources; no model inference or listening test was performed.

### Does 1.46% WER mean 98.54% of sentences were perfect?

No. WER counts word insertions, deletions and substitutions relative to reference word count. It is not sentence accuracy or listener satisfaction and can exceed 100%. CER applies the calculation to characters.

### Which model sounds best overall?

This objective leaderboard cannot determine that. It narrows candidates by intelligibility, speed and speaker preservation; listening preference needs separate evidence.

## Official sources and model/code entry points

Announcement: https://huggingface.co/blog/open-tts-leaderboard

Evaluation code: https://github.com/huggingface/open-tts-leaderboard

Code commit: `2b2cd31257d22e00af4af585a1f447351c0e713c`. Space commit: `27639f0ab3cc57aaa194770fe5dc9a0b5595fd52`. The public Space served the selected private-dataset revision through its normal interface; we did not access private repository credentials.

- hexgrad/Kokoro-82M：https://huggingface.co/hexgrad/Kokoro-82M ；代码：https://github.com/hexgrad/kokoro
- sahilmahendrakar/Paradee-8M-v1.0：https://huggingface.co/sahilmahendrakar/Paradee-8M-v1.0 ；代码：https://github.com/sahilmahendrakar/paradee
- Supertone/supertonic-3：https://huggingface.co/Supertone/supertonic-3 ；代码：https://github.com/supertone-oss-archive/supertonic
- fishaudio/s2-pro：https://huggingface.co/fishaudio/s2-pro ；代码：https://github.com/fishaudio/fish-speech
- k2-fsa/OmniVoice：https://huggingface.co/k2-fsa/OmniVoice ；代码：https://github.com/k2-fsa/OmniVoice
- kyutai/pocket-tts：https://huggingface.co/kyutai/pocket-tts ；代码：https://github.com/kyutai-labs/pocket-tts
- FunAudioLLM/Fun-CosyVoice3-0.5B-2512 (RL)：https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 ；代码：https://github.com/QwenAudio/CosyVoice
- ResembleAI/chatterbox (ChatterboxTTS)：https://huggingface.co/ResembleAI/chatterbox ；代码：https://github.com/resemble-ai/chatterbox
- Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice：https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice ；代码：https://github.com/QwenLM/Qwen3-TTS
- BreezeBlue/Breeze-TTS-2：https://huggingface.co/BreezeBlue/Breeze-TTS-2 ；代码：https://github.com/breezeblue-ai/breeze-tts

The Pocket TTS model-page request returned HTTP 401 anonymously. We retain the official entry point and public code link without claiming to have read its gated card. License and implementation checks should target the actual evaluated checkpoint or variant.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
