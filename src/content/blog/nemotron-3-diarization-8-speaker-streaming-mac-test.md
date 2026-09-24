---
title: "Nemotron 3 Diarization 实测：NVIDIA 1 亿参数说话人分离模型，最多 8 人、可商用，Mac 上要自己编译"
titleEn: "Nemotron 3 Diarization Tested: NVIDIA's 100M Speaker Diarization Model, Up to 8 Speakers, Commercial-Friendly, Self-Build on Mac"
description: "Nemotron 3 Diarization 是 NVIDIA 2026-09-23 发布的 1 亿参数说话人分离模型，最多 8 人、流式延迟可低至 0.32 秒、OpenMDW-1.1 许可可商用。模型卡自报 DIHARD III DER 从 19.09% 降到 12.73%。我们在 16GB M4 Mac mini 上实测：官方安装脚本装的 v0.1.0 运行时加载失败，需从源码编译；编译后 10 分钟音频 CPU 69 秒、Metal 22 秒跑完，真人双人样本说话人数和身份全对，但 macOS 合成语音全部失手。"
descriptionEn: "Nemotron 3 Diarization is a 100M-parameter speaker diarization model NVIDIA released on 2026-09-23: up to 8 speakers, streaming latency down to 0.32 s, and an OpenMDW-1.1 license that allows commercial use. The model card self-reports DIHARD III DER falling from 19.09% to 12.73%. On a 16GB M4 Mac mini, the runtime installed by the official script (v0.1.0) fails to load it and has to be built from source; once built, 10 minutes of audio took 69 s on CPU and 22 s on Metal, a real two-speaker sample got speaker count and identities right, but macOS synthetic voices defeated it completely."
pubDate: "2026-09-24"
updatedDate: "2026-09-24"
category: "Tech-Experiment"
tags: ["说话人分离", "Speaker Diarization", "NVIDIA", "Nemotron", "Sortformer", "会议转写", "Apple Silicon", "GGUF", "本地部署"]
heroImage: "../../assets/images/nemotron-3-diarization-8-speaker-streaming-mac-test-banner.jpg"
author: "Mycelium Protocol"
wechatTitle: "英伟达Nemotron说话人分离模型Mac实测"
wechatDigest: "NVIDIA开源1亿参数说话人分离模型，最多8人可商用；Mac要源码编译，真人样本零混淆，合成语音失手。"
---

> 📌 模型：nvidia/Nemotron-3-Diarization
> HuggingFace：https://huggingface.co/nvidia/Nemotron-3-Diarization
> 许可：OpenMDW-1.1（可商用）｜ 参数：1 亿（99,226,504）｜ 发布：2026-09-23 ｜ 下载 4,282 / 点赞 224（2026-09-24）

---

**BLUF**：Nemotron 3 Diarization 是一个只回答「谁在什么时候说话」的模型，不做转写。它是 NVIDIA Streaming Sortformer 路线的新一代：1 亿参数、最多同时跟踪 8 个说话人（上一代是 4 个）、同一个权重可以在 0.32 秒到 30.4 秒之间切换延迟，许可证换成了比上一代宽松的 OpenMDW-1.1，商用不设门槛。模型卡自报的 DER 相比上一代普遍下降三到六成，但全是 NVIDIA 自己跑的；第三方里只有 Baseten 发了对比，它在 AMI 上输给了 pyannote community-1。我们在一台 16GB 的 M4 Mac mini 上实测：**按模型卡的指引用官方安装脚本装运行时，装到的是 8 月的 v0.1.0 版本，加载这个模型直接报错**；从 NVIDIA/NeMo-Speech.cpp 当天的 main 分支编译之后才跑通，107MB 的 GGUF 处理 10 分钟音频，CPU 流式 69 秒、Metal 流式 22 秒、Metal 大块模式 3.1 秒。真人双人样本说话人数和身份全对（DER 13-15%，误差全部来自边界多标）。但用 macOS 自带语音合成的 5 人中文对话，从头到尾被判成 1 个人，上一代模型也一样。

## 它到底解决什么问题？

说话人分离（speaker diarization）的输出是一张时间表：0.5-12.6 秒是说话人 1，12.4-18.1 秒是说话人 2……它不知道说话人是谁，只给匿名编号；也不管说了什么，文字要交给 ASR。会议纪要、播客字幕、客服录音质检、多人语音 Agent，都需要先有这张表，才能把 ASR 的文字按人拆开。

这个领域开源方案里用得最多的是 pyannote（community-1 在 HuggingFace 上月下载 550 万次），NVIDIA 这边则是 Sortformer 系列。Nemotron 3 Diarization 是 Sortformer 系列改名并入 Nemotron 品牌后的第一个版本，上一代 diar_streaming_sortformer_4spk-v2.1 的模型卡已经加上了「新版本已发布」的提示。

## 架构：跟 Sortformer 4spk 比改了什么？



模型卡给出的结构很简单：

- 输入 16kHz 单声道音频，先转 10 毫秒一帧的 Mel 频谱，再把 8 帧拼成一帧，编码器以 80 毫秒一帧的速度工作；
- 编码器是 31 层 Transformer，带 RoPE 旋转位置编码；
- 顶上一层 Conv1D 把预测上采样回 10 毫秒分辨率；
- 输出是 `[T, 8]` 的矩阵，每一列是一个说话人在每一帧「正在说话」的概率。

「Sortformer」这个名字说的是它怎么解决说话人编号的排列问题：8 个输出通道按说话人**第一次出现的先后**排序，第一个开口的永远是通道 1。流式推理靠两个缓存：AOSC（按到达顺序排列的说话人缓存）记住前面出现过的每个人的声音特征，FIFO 队列提供最近几秒的上下文。这两样都是 Streaming Sortformer 论文（arXiv 2507.18446）里提出的，新模型沿用。

跟上一代的差别整理成表：

| | diar_streaming_sortformer_4spk-v2.1 | Nemotron-3-Diarization |
|---|---|---|
| 参数 | 117M | 100M |
| 编码器 | 17 层 FastConformer（NEST）+ 18 层 Transformer | 31 层 Transformer + RoPE（由 NEST 自监督权重初始化） |
| 最多说话人 | 4 | 8 |
| 输出分辨率 | 80ms | 默认 10ms，可设为 10ms 的任意倍数 |
| 说话人缓存 | 188 帧 | 264 帧 |
| 许可证 | NVIDIA Open Model License | OpenMDW-1.1 |

训练数据方面，模型卡列得很细：约 1 万小时真实对话（Fisher、AMI、ICSI、VoxConverse、AISHELL-4、DIHARD III 开发集、CALLHOME 第 1 部分、AliMeeting、NOTSOFAR1、DISPLACE 等，另有 David AI 授权的多人对话 1,000 小时和 YODAS-v2 伪标签 5,000 小时），加上 82,611 小时用 FastMSS 工具合成的 1-8 人混音。其中 David AI 这家数据商的授权数据占合成数据的大头（英文 36,458 小时 + 多语种 19,216 小时）。训练用了 8 个节点、每节点 8 张 A100 80GB，先离线训练再流式微调。

## 许可证：能不能商用？

采集侧显示「未声明」，实际模型卡 frontmatter 写的是 `license: openmdw-1.1`，正文也明确写了「This model is ready for commercial or non-commercial use」。

OpenMDW-1.1 是一个面向模型的宽松许可，要点：

- 可以不受限制地使用、修改、分发模型材料，**商用不设营收门槛**；
- 分发时要附上许可证全文和原有版权声明；
- 对模型输出不设任何限制；
- 如果你主动发起专利或版权诉讼、主张这些模型材料侵权，你的授权自动终止（被动防御除外）。

这比上一代的 NVIDIA Open Model License 更干净，不再有 NVIDIA 自己那套附加条款。配套运行时 NeMo-Speech.cpp 是 Apache-2.0。需要留意的只有一点：训练数据里有 David AI 的商业授权数据和 LDC 语料（Fisher、CALLHOME），NVIDIA 已经在模型发布这一层处理了这些权利，下游用户用权重本身不受影响，但你不能因此拿到这些语料。

## 模型卡的成绩单：进步有多大？哪些是自报的？



模型卡的对比对象只有自家上一代，所有数字都由 NVIDIA 用 NeMo 的 `e2e_diarize_speech.py` 跑出来。重叠语音计入 DER，除 CALLHOME 用 0.25 秒容差外其他都是 0 容差。挑几个代表性的（离线配置 30.4 秒 / 流式 1.04 秒）：

| 数据集 | 4spk-v2.1 离线 | Nemotron 3 离线 | Nemotron 3 流式 1.04s |
|---|---|---|---|
| DIHARD III 全集 | 19.09 | 12.73 | 13.18 |
| DIHARD III 5-9 人 | 40.21 | 27.58 | 28.65 |
| CALLHOME 第 2 部分 | 10.32 | 9.10 | 10.29 |
| AliMeeting 近场（中文） | 11.57 | 6.40 | 6.59 |
| AliMeeting 远场（中文） | 13.69 | 10.47 | 10.80 |
| AMI SDM 单通道远场 | 21.42 | 11.14 | 12.80 |
| NOTSOFAR1 单通道 | 30.49 | 11.00 | 12.77 |

几个值得注意的地方：

1. **最大的进步在人多的场景。** NOTSOFAR1 单通道从 30.49 降到 11.00，因为旧模型只有 4 个通道，第 5 个人一出现就必错；DIHARD III 5-9 人那一栏也说明了同样的问题。如果你的会议经常超过 4 个人，这是升级的主要理由。
2. 说话人数量不是处处更准。AMI 上旧模型的说话人计数准确率（SCA）是 93.75%，新模型离线降到 87.50%、流式降到 81.25%；NOTSOFAR1 单通道流式只有 55-61%。DER 大幅下降的同时，「一共几个人」反而偶尔会数错，做会议纪要时要留意多出或少掉的说话人编号。
3. 参考标注是 NVIDIA 选的。AMI、AliMeeting、NOTSOFAR1 用的是强制对齐生成的参考标注，而不是数据集原始的分段标注。模型卡自己专门用一个醒目的方框提醒：换一套标注就是另一套评测协议，数字不能直接比。这有道理（原始标注把句内停顿算成说话），但也意味着这些数字不能和 pyannote 等其他模型卡上的 AMI / AliMeeting 数字直接对照。
4. 中文数据集在训练集里。AliMeeting 和 AISHELL-4 的训练集都参与了训练；测试集是独立的，但分布非常接近。中文会议录音上的实际表现，大概率比 AliMeeting 测试集的数字差。

第三方数据目前有两个来源：

- NVIDIA 的 HuggingFace 博客称，在 VoiceArena 的 Diarization-Bench 上，它在 12 个系统、139 段英文对话里排第一，DER 14.72%，第二名 19.3%。这仍是 NVIDIA 转述的，并且只测了英文。
- Baseten（NVIDIA 的推理合作伙伴）发了自己的测试：0 容差、计入重叠，AISHELL-4 上「low」配置 DER 9.8%，上一代 v2.1 是 27.2%；在 NOTSOFAR、AMI、CALLHOME、AISHELL 上全面好于 Meta Muse Voice Transcribe，只在 AMI 上输给 pyannote community-1。Baseten 还称一张 RTX PRO 6000 能同时撑 500 多路一小时长的流，加上转写后是 190 路。

作为参照，pyannote community-1 自己模型卡上的 DER 是 DIHARD 3 20.2%、AMI（IHM）17.0%、AliMeeting 第 1 通道 20.3%、CALLHOME 第 2 部分 26.7%。这些同样是自报，标注和容差也不同，只能看数量级。

## Mac 上能跑吗？我们实测的结果

模型卡的「Supported Hardware」只列了 NVIDIA 的 Ampere / Ada / Hopper / Blackwell GPU，操作系统只写 Linux。但同一张卡的第一个用法就是 NeMo-Speech.cpp，也就是 NVIDIA 官方的 C++ 本地推理运行时。它基于 ggml（llama.cpp 用的那套张量库），GGUF 就是给它准备的。发布页有 `macos-aarch64-metal` 的预编译包。这台机器是 16GB 内存的 M4 Mac mini。



### 第一个坑：官方安装的版本不认这个模型

NeMo-Speech.cpp 最新的正式版本是 2026-08-19 的 v0.1.0，比模型发布早一个多月。我们下载 v0.1.0 的 Mac Metal 包（13MB），配合模型仓库里的 `Nemotron-3-Diarization.q8_0.gguf`（107MB）运行：

```
$ nemo-speech diarize ex.wav --model ./Nemotron-3-Diarization.q8_0.gguf
nemo-speech diarize: sortformer: pre_ln transformer variant is not supported
```

v0.1.0 的 `model list` 里也只有 4spk-v2。对 Nemotron 3 Diarization 的支持是 2026-09-24（写稿当天）才合进 main 分支的两个提交（#50 加支持、#52 设为默认），还没有发版。README 说安装脚本「优先用已验证的原生发布包」，所以**按模型卡照做的人，今天装到的就是这个跑不起来的版本**。

### 源码编译：比预想的轻

编译要 CMake 3.26+、Ninja 和 SentencePiece 开发文件。为了不往系统里装东西，我们把 cmake / ninja 装进临时 Python 虚拟环境，SentencePiece v0.2.1 在临时目录里编成静态库，然后：

```bash
git clone --depth 1 https://github.com/NVIDIA/NeMo-Speech.cpp
cd NeMo-Speech.cpp
git submodule update --init ggml
scripts/configure.sh metal-diar -DCMAKE_PREFIX_PATH=/path/to/sentencepiece \
  -DNEMO_SPEECH_BUILD_MIC_CAPTURE=OFF
cmake --build --preset metal-diar
```

`metal-diar` 这个预设只编说话人分离，编译本身 10 秒左右（101 个目标）。如果你本来就用 Homebrew，`brew install cmake ninja sentencepiece abseil` 之后直接编就行。编出来的 `nemo-speech diarize` 多了 `v3-streaming` / `v3-offline` 两个预设，加载模型正常。

### 速度

把一段 97.6 秒的多人样本重复 6 遍，得到 585.6 秒（约 10 分钟）的音频，测墙钟时间（含加载模型）：

| 模式 | 耗时 | 约合实时倍数 |
|---|---|---|
| CPU，默认流式 | 69.1 秒 | 8.5× |
| CPU，`--preset v3-offline` | 6.6 秒 | 88× |
| Metal，默认流式 | 22.4 秒 | 26× |
| Metal，`--preset v3-offline` | 3.1 秒 | 189× |

有两点跟直觉不同。一是短文件上 Metal 反而更慢：97.6 秒音频 Metal 25 秒、CPU 12 秒，看起来有十几秒的固定启动开销，长文件 Metal 才占优。二是默认流式模式每次只喂一小块，适合实时场景；**处理已经录好的文件应该用 `v3-offline` 预设**，快 10 倍左右。注意 `--preset v3-offline` 只是把流式的块调大，不是全注意力；真正的全注意力模式 `--offline` 受位置编码表限制，只能处理约 6.6 分钟以内的音频。

### 准确度：真人样本对了，合成语音全错

我们用了三段手头有「标准答案」的音频，DER 用自己写的逐帧脚本计算（10 毫秒一帧、0 容差、计入重叠、自动找最优的说话人对应关系）：

| 测试音频 | Nemotron 3 | 上一代 4spk-v2 |
|---|---|---|
| pyannote 官方示例（真人英文，2 人，30 秒），默认流式 | 2 人全对，DER 15.11%（混淆 0，全部是误报） | 2 人，DER 14.33% |
| 同上，`v3-offline` | DER 13.18%（混淆 0） | — |
| macOS 自带语音合成的中文会议（5 个声音，11 轮，77.6 秒） | 只识别出 1 个人 | 也只有 1 个人 |
| macOS 自带语音合成的英文对话（5 个声音，6 轮） | 只识别出 2 个人 | 识别出 4 个人 |

真人样本上两代都没有认错人，误差全部来自说话段的起止比参考标注宽一点（参考标注切得很紧，0 容差下这部分都算误报），是正常水平。

合成语音的结果要谨慎解读。macOS 的这批中文声音（婷婷、Eddy、Grandpa、Shelley、Rocko）出自同一套合成引擎，人耳听来音色差异明显，但在说话人特征空间里显然挤在了一起。**这不说明它对真人中文不行**，只说明两件事：一，别用系统 TTS 生成的「假会议」来测试说话人分离，会得出错误结论；二，如果你要处理的是 AI 配音的播客、多角色 TTS 有声书，最好先拿自己的素材试。NVIDIA 模型卡里的演示视频用的是 NVIDIA 自家 TTS 的 8 个声音，说明它不是完全分不出合成声音，只是对声音之间的差异有要求。

中文真人会议我们没有找到能在 5GB 以内拿到的、带标注的小样本，所以中文效果只能引用上面 AliMeeting 的自报数字和 Baseten 的 AISHELL-4 数字。

### 那 NeMo Python 和 Transformers 呢？

- **NeMo Speech（Python）**：模型卡的安装说明从 `apt-get` 开始，硬件表只有 NVIDIA GPU。NeMo 是 PyTorch 写的，理论上能在 Mac 的 CPU / MPS 上推理，但官方没有承诺，我们也没装（依赖很重）。训练和微调基本等于必须用 Linux + NVIDIA。
- **Transformers**：已经原生支持（`AutoModelForAudioFrameClassification`，模型类型 `nemotron3_diarization`），但要从源码安装 transformers 主分支。离线和流式两种用法模型卡都给了完整代码，Mac 上用 PyTorch 跑应该可行，我们没有验证。

对 Mac 用户，目前最省事的路线就是 NeMo-Speech.cpp：一个 13MB 的二进制加一个 107MB 的 GGUF，不需要 Python。

## 跟 pyannote community-1 怎么选？

| | Nemotron 3 Diarization | pyannote community-1 |
|---|---|---|
| 许可 | OpenMDW-1.1，无需登录 | CC-BY-4.0，需在 HF 同意分享联系方式 |
| 形态 | 单个端到端模型（100M） | 分割 + 嵌入 + 聚类的流水线 |
| 说话人上限 | 硬上限 8 | 没有硬上限，可指定人数 |
| 流式 | 原生支持，0.32-1.04 秒延迟 | 以离线为主 |
| Mac 本地 | C++ 运行时，现在要自己编译 | `pip install pyannote.audio`，默认 CPU |
| 生态 | 刚发布，与 NVIDIA ASR 深度绑定 | 生态最成熟，WhisperX 等工具默认用它 |
| 公开对比 | Baseten 测试中只在 AMI 上输给 community-1 | 自报数字，标注协议不同 |

简单的判断：**要实时、会议人数在 8 人以内、打算用 NVIDIA 的 ASR，选 Nemotron 3；要处理已录好的文件、人数不定、想用现成的 WhisperX 类工具链，pyannote 依然是更省心的默认选择。** 8 人这个上限是硬的，模型卡明说超过 8 人时「语音可能漏掉或被分到错误的通道」。

## Mac 上怎么搭「会议录音转写 + 分离」？



分离只给时间表，要得到「谁说了什么」，还需要一个带词级时间戳的 ASR，再按时间把词分给人。有三条路线：

**路线 A：NeMo-Speech.cpp 一条命令。** 用包含 ASR 的预设（例如 `metal-asr`，它同时编进说话人分离）编译之后：

```bash
ffmpeg -i meeting.m4a -ac 1 -ar 16000 -c:a pcm_s16le meeting.wav
nemo-speech transcribe meeting.wav --diarize --json
```

JSON 里每个词都带一个从 1 开始的 `speaker` 字段；main 分支已经把 Nemotron 3 设为 `--diarize` 的默认模型。默认 ASR 是 Nemotron 3.5 ASR Streaming 0.6B，许可同样是 OpenMDW-1.1。中文要注意：这个 ASR 支持 40 个语言区域，中文（zh-CN）在第二档「broad-coverage」，不在最高档的 19 个「transcription-ready」里；英文场景 NVIDIA 推荐专门的英文版模型。实时场景可以用 `transcribe --live --diarize`，但说话人标签在确认前可能会变。

**路线 B：Whisper / 其他 ASR + Nemotron 3 出 RTTM，自己对齐。** 中文要求高时更稳妥：

```bash
nemo-speech diarize meeting.wav --preset v3-offline --format rttm -o meeting.rttm
```

然后用任何能输出词级时间戳的中文 ASR（whisper.cpp、FunASR 等）转写，按每个词的中点落在哪个说话段里分配说话人。这种做法的已知缺陷，NVIDIA 在集成指南里也直说了：两个人同时说话时，切出来的那段音频里两个声音都在，普通 ASR 可能把两人的话混在一起。重叠不多的会议没问题。

**路线 C：NeMo Python 的多说话人流式 ASR。** 集成指南给的正式方案是 Nemotron 3 Diarization 配 multitalker-parakeet-streaming-0.6b-v1（只支持英文，专门处理重叠语音）或 Nemotron 3.5 ASR，每个说话人一路独立的 ASR 流。效果最好，但要 CUDA，Mac 用户可以忽略。

另外两个实用提醒：输出的说话人编号是按「谁先开口」排的匿名编号，每次会话独立，不是声纹识别，要显示人名得自己加注册或映射步骤；输入一律先转成 16kHz 单声道。

## 局限和需要留意的地方

- 8 人硬上限，超过就会漏或错；大型会议、多人圆桌不适用。
- 发布与运行时不同步：模型 09-23 发布，Mac 能用的运行时支持 09-24 才合进 main，还没有正式版本。
- 成绩单几乎全是自报，基线只有自家上一代；唯一有 pyannote 对比的是 NVIDIA 的合作伙伴 Baseten。
- 说话人计数在部分数据集上比上一代差（AMI SCA 93.75% → 81.25-87.50%）。
- 模型卡的偏见子卡里，「针对受保护群体的参与」和「缓解偏见的措施」两项都写着「None」。
- 中文真人会议效果我们没有实测，只有 AliMeeting / AISHELL-4 的数字，而这两个数据集的训练集都参与了训练。

## 常见问题

**Q：Nemotron 3 Diarization 能转写文字吗？**
不能。它只输出每个说话人在每 10 毫秒的说话概率，文字要配 ASR。

**Q：可以商用吗？**
可以。OpenMDW-1.1 允许商用、不设营收门槛、对输出不设限制；分发权重时附上许可证和版权声明即可。

**Q：最少多大内存能跑？**
q8_0 的 GGUF 只有 107MB，我们在 16GB 的 M4 上跑 10 分钟音频毫无压力。它对内存几乎没有要求，门槛在于现在要自己编译运行时。

**Q：延迟最低能到多少？**
单个权重支持 0.32 / 0.64 / 1.04 / 30.4 秒四档推荐配置，理论最低 80 毫秒但官方不推荐。这里的延迟是「输入缓冲」，不含计算时间。

**Q：中文效果怎么样？**
自报 AliMeeting 近场 DER 6.40%、远场 10.47%；Baseten 测 AISHELL-4 为 9.8%。我们没有找到可用的中文真人测试样本，用系统合成语音测试时所有人都被判成了同一个人，这个测试方法本身不可靠。

**Q：和上一代 Sortformer 4spk 比要不要换？**
会议常有 5 人以上、或者在意许可证的，换；2-4 人电话录音场景，CALLHOME 上两代差距不大（离线 10.32 → 9.10），不急。

## 一手源

- 模型卡：https://huggingface.co/nvidia/Nemotron-3-Diarization
- ASR 集成指南：https://huggingface.co/nvidia/Nemotron-3-Diarization/blob/main/ASR_INTEGRATION_GUIDE.md
- 评测说明：https://huggingface.co/nvidia/Nemotron-3-Diarization/blob/main/diarization_evaluation.md
- NVIDIA 官方博客：https://huggingface.co/blog/nvidia/nemotron-diarization
- NeMo-Speech.cpp：https://github.com/NVIDIA/NeMo-Speech.cpp
- OpenMDW-1.1 许可证：https://openmdw.ai/license/1-1/
- 上一代模型：https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1
- Streaming Sortformer 论文：https://arxiv.org/abs/2507.18446
- Baseten 测试：https://www.baseten.co/blog/nvidia-nemotron-3-diarization/
- pyannote community-1：https://huggingface.co/pyannote/speaker-diarization-community-1
- Nemotron 3.5 ASR：https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Model: nvidia/Nemotron-3-Diarization
> HuggingFace: https://huggingface.co/nvidia/Nemotron-3-Diarization
> License: OpenMDW-1.1 (commercial use allowed) | Parameters: 100M (99,226,504) | Released: 2026-09-23 | 4,282 downloads / 224 likes (2026-09-24)

---

**BLUF**: Nemotron 3 Diarization answers only one question — who spoke when — and does no transcription. It is the next generation of NVIDIA's Streaming Sortformer line: 100M parameters, up to 8 speakers tracked at once (the previous generation handled 4), one checkpoint that switches between 0.32 s and 30.4 s latency, and a move to the more permissive OpenMDW-1.1 license with no commercial threshold. The DER numbers on the model card drop by 30-60% relative to the previous generation, but NVIDIA ran all of them itself; the only third-party comparison so far comes from Baseten, where it lost to pyannote community-1 on AMI. We tested it on a 16GB M4 Mac mini: **following the model card and installing the runtime with the official script gets you the August v0.1.0 release, which fails to load this model**. It only worked after building NVIDIA/NeMo-Speech.cpp from that day's main branch. With the 107MB GGUF, 10 minutes of audio took 69 s in CPU streaming mode, 22 s in Metal streaming mode, and 3.1 s with Metal and large chunks. On a real two-speaker sample it got the speaker count and every identity right (DER 13-15%, with all the error coming from generous segment boundaries). But a five-voice Chinese conversation made with macOS's built-in speech synthesis was labelled as a single speaker from start to finish, and the previous-generation model did the same.

## What Problem Does It Actually Solve?

Speaker diarization outputs a timetable: 0.5-12.6 s is speaker 1, 12.4-18.1 s is speaker 2, and so on. It doesn't know who the speakers are, only anonymous numbers, and it doesn't care what was said; the words come from ASR. Meeting minutes, podcast subtitles, call-center QA and multi-party voice agents all need this table before ASR text can be split by speaker.

The most widely used open-source option is pyannote (community-1 has 5.5 million monthly downloads on HuggingFace). NVIDIA's own line is Sortformer. Nemotron 3 Diarization is the first release since Sortformer was renamed and folded into the Nemotron brand; the model card for the previous diar_streaming_sortformer_4spk-v2.1 now carries a "new version released" note.

## Architecture: What Changed From Sortformer 4spk?



The model card describes a simple structure:

- 16kHz mono input becomes 10 ms Mel-spectrogram frames, which are stacked 8 at a time, so the encoder runs at 80 ms per frame;
- the encoder is a 31-layer Transformer with RoPE rotary position embeddings;
- a Conv1D layer on top upsamples predictions back to 10 ms resolution;
- the output is a `[T, 8]` matrix, each column one speaker's per-frame probability of speaking.

"Sortformer" refers to how it resolves speaker permutation: the 8 output channels are ordered by **when each speaker first appears**, so whoever speaks first is always channel 1. Streaming relies on two caches: the AOSC (Arrival-Order Speaker Cache) remembers the voice characteristics of everyone heard so far, and a FIFO queue supplies the last few seconds of context. Both come from the Streaming Sortformer paper (arXiv 2507.18446), and the new model keeps them.

The differences from the previous generation:

| | diar_streaming_sortformer_4spk-v2.1 | Nemotron-3-Diarization |
|---|---|---|
| Parameters | 117M | 100M |
| Encoder | 17-layer FastConformer (NEST) + 18-layer Transformer | 31-layer Transformer + RoPE (initialized from NEST SSL weights) |
| Max speakers | 4 | 8 |
| Output resolution | 80 ms | 10 ms default, any multiple of 10 ms |
| Speaker cache | 188 frames | 264 frames |
| License | NVIDIA Open Model License | OpenMDW-1.1 |

The training data list is detailed: about 10,000 hours of real conversations (Fisher, AMI, ICSI, VoxConverse, AISHELL-4, the DIHARD III dev set, CALLHOME part 1, AliMeeting, NOTSOFAR1, DISPLACE and more, plus 1,000 hours of licensed multi-speaker data from David AI and a 5,000-hour pseudo-labelled YODAS-v2 subset), and 82,611 hours of 1-8 speaker mixtures simulated with FastMSS. David AI's licensed data makes up most of the simulated mix (36,458 hours English plus 19,216 hours multilingual). Training used 8 nodes of 8 A100 80GB GPUs: offline training first, then streaming fine-tuning.

## The License: Can You Use It Commercially?

Our collector showed "not declared", but the model card frontmatter says `license: openmdw-1.1`, and the body states plainly: "This model is ready for commercial or non-commercial use."

OpenMDW-1.1 is a permissive license for models. The key points:

- you may use, modify and distribute the model materials without restriction, **with no revenue threshold for commercial use**;
- distributions must include the license text and the original copyright notices;
- no restrictions of any kind on outputs;
- if you start or voluntarily join patent or copyright litigation claiming the materials infringe, your grant terminates (defensive responses excepted).

That is cleaner than the previous generation's NVIDIA Open Model License, with none of NVIDIA's extra terms. The companion runtime, NeMo-Speech.cpp, is Apache-2.0. One thing to keep in mind: the training data includes David AI's commercially licensed data and LDC corpora (Fisher, CALLHOME). NVIDIA has dealt with those rights at the model release level. Downstream users of the weights aren't affected, but this gives you no rights to the corpora themselves.

## The Model Card's Numbers: How Big Is the Improvement, and Which Numbers Are Self-Reported?



The model card compares only against NVIDIA's previous generation, and NVIDIA produced every number with NeMo's `e2e_diarize_speech.py`. Overlapping speech counts toward DER, and the collar is 0 everywhere except CALLHOME (0.25 s). A representative selection (offline 30.4 s / streaming 1.04 s):

| Dataset | 4spk-v2.1 offline | Nemotron 3 offline | Nemotron 3 streaming 1.04s |
|---|---|---|---|
| DIHARD III full | 19.09 | 12.73 | 13.18 |
| DIHARD III 5-9 speakers | 40.21 | 27.58 | 28.65 |
| CALLHOME part 2 | 10.32 | 9.10 | 10.29 |
| AliMeeting near (Mandarin) | 11.57 | 6.40 | 6.59 |
| AliMeeting far (Mandarin) | 13.69 | 10.47 | 10.80 |
| AMI SDM single far-field | 21.42 | 11.14 | 12.80 |
| NOTSOFAR1 single-channel | 30.49 | 11.00 | 12.77 |

What stands out:

1. **The biggest gains are in crowded recordings.** NOTSOFAR1 single-channel drops from 30.49 to 11.00 because the old model had only 4 channels, so the fifth speaker was always wrong. The DIHARD III 5-9 speaker column tells the same story. If your meetings often have more than 4 people, that is the main reason to upgrade.
2. Speaker counting isn't better everywhere. On AMI the old model's speaker counting accuracy (SCA) was 93.75%; the new one drops to 87.50% offline and 81.25% streaming, and NOTSOFAR1 single-channel streaming manages only 55-61%. DER falls sharply, yet the total headcount is occasionally wrong. For meeting minutes, look out for extra or missing speaker numbers.
3. NVIDIA chose the reference labels. For AMI, AliMeeting and NOTSOFAR1 it used labels produced by forced alignment rather than the datasets' original segment labels. The model card warns in a prominent box that a different label set is a different evaluation protocol and the numbers aren't directly comparable. That's reasonable, since the original labels count within-sentence pauses as speech. It also means these numbers can't be compared directly with the AMI / AliMeeting figures on pyannote's or anyone else's model card.
4. The Mandarin datasets are in the training set. Both AliMeeting and AISHELL-4 training splits were used. The test splits are separate, but the distribution is very close. Real Mandarin meeting recordings will probably score worse than the AliMeeting test numbers.

There are two third-party sources so far:

- NVIDIA's HuggingFace blog says it ranks first on VoiceArena's Diarization-Bench among 12 systems across 139 English conversations, with 14.72% DER against 19.3% for second place. This is still NVIDIA reporting it, and it covers English only.
- Baseten (an NVIDIA inference partner) published its own test with 0 collar and overlap included: on AISHELL-4 at the "low" profile, DER 9.8% against 27.2% for the previous v2.1. It beat Meta Muse Voice Transcribe on NOTSOFAR, AMI, CALLHOME and AISHELL, and lost to pyannote community-1 only on AMI. Baseten also says a single RTX PRO 6000 can sustain more than 500 concurrent hour-long streams, or 190 with transcription.

For reference, pyannote community-1's own model card lists DER of 20.2% on DIHARD 3, 17.0% on AMI (IHM), 20.3% on AliMeeting channel 1 and 26.7% on CALLHOME part 2. These are also self-reported, with different labels and collars, so only the order of magnitude is meaningful.

## Does It Run on a Mac? What We Measured

The model card's "Supported Hardware" lists only NVIDIA Ampere / Ada / Hopper / Blackwell GPUs and names Linux as the only OS. Yet the first usage example on the same card is NeMo-Speech.cpp, NVIDIA's official C++ local inference runtime. It is built on ggml, the tensor library behind llama.cpp, and the GGUF file exists for it. The releases page has a prebuilt `macos-aarch64-metal` package. Our test machine was an M4 Mac mini with 16GB of memory.



### Pitfall One: The Officially Installed Version Doesn't Recognize the Model

The latest release of NeMo-Speech.cpp is v0.1.0 from 2026-08-19, more than a month older than the model. We downloaded the v0.1.0 Mac Metal package (13MB) and ran it with the repo's `Nemotron-3-Diarization.q8_0.gguf` (107MB):

```
$ nemo-speech diarize ex.wav --model ./Nemotron-3-Diarization.q8_0.gguf
nemo-speech diarize: sortformer: pre_ln transformer variant is not supported
```

The v0.1.0 `model list` also shows only 4spk-v2. Nemotron 3 Diarization support landed on main in two commits on 2026-09-24, the day we wrote this (#50 adds support, #52 makes it the default), and hasn't been released yet. The README says the install script "prefers a verified native release", so **anyone following the model card today ends up with a version that can't run it**.

### Building From Source: Lighter Than Expected

The build needs CMake 3.26+, Ninja and the SentencePiece development files. To keep the system clean, we installed cmake and ninja into a throwaway Python virtualenv, built SentencePiece v0.2.1 as a static library in a temp directory, then:

```bash
git clone --depth 1 https://github.com/NVIDIA/NeMo-Speech.cpp
cd NeMo-Speech.cpp
git submodule update --init ggml
scripts/configure.sh metal-diar -DCMAKE_PREFIX_PATH=/path/to/sentencepiece \
  -DNEMO_SPEECH_BUILD_MIC_CAPTURE=OFF
cmake --build --preset metal-diar
```

The `metal-diar` preset builds only diarization, and the compile itself takes about 10 seconds (101 targets). If you already use Homebrew, run `brew install cmake ninja sentencepiece abseil` and build directly. The resulting `nemo-speech diarize` gains two presets, `v3-streaming` and `v3-offline`, and loads the model without trouble.

### Speed

We repeated a 97.6 s multi-speaker sample six times to get 585.6 s (about 10 minutes) of audio and measured wall-clock time, model loading included:

| Mode | Time | Approx. real-time factor |
|---|---|---|
| CPU, default streaming | 69.1 s | 8.5× |
| CPU, `--preset v3-offline` | 6.6 s | 88× |
| Metal, default streaming | 22.4 s | 26× |
| Metal, `--preset v3-offline` | 3.1 s | 189× |

Two results cut against intuition. First, Metal was slower on short files: 97.6 s of audio took 25 s on Metal and 12 s on CPU, which looks like a fixed startup cost of a dozen or so seconds, so Metal only wins on long files. Second, the default streaming mode feeds small chunks one at a time, which suits real-time use; **for recordings you already have, use the `v3-offline` preset**, which is roughly 10× faster. Note that `--preset v3-offline` only enlarges the streaming chunks and isn't full attention. The true full-attention mode, `--offline`, is limited by the positional table to about 6.6 minutes of audio.

### Accuracy: Right on Real Voices, Wrong on Synthetic Ones

We used three clips with known answers and computed DER with our own frame-level script (10 ms frames, 0 collar, overlap included, optimal speaker mapping):

| Test audio | Nemotron 3 | Previous 4spk-v2 |
|---|---|---|
| pyannote's official sample (real English, 2 speakers, 30 s), default streaming | both speakers right, DER 15.11% (0 confusion, all false alarm) | 2 speakers, DER 14.33% |
| same, `v3-offline` | DER 13.18% (0 confusion) | — |
| Mandarin meeting from macOS built-in TTS (5 voices, 11 turns, 77.6 s) | only 1 speaker detected | also only 1 speaker |
| English dialogue from macOS built-in TTS (5 voices, 6 turns) | only 2 speakers detected | 4 speakers detected |

On the real sample neither generation mixed up the speakers. All the error came from segments starting and ending a little wider than the tightly cut reference, which counts as false alarm at 0 collar. That's a normal result.

Read the synthetic-voice results carefully. The macOS Mandarin voices we used (Tingting, Eddy, Grandpa, Shelley, Rocko) all come from the same synthesis engine. They sound clearly different to a human ear, but they evidently crowd together in speaker-embedding space. **This doesn't show the model fails on real Mandarin speech.** It shows two things: first, don't test diarization with "fake meetings" made by system TTS, because you'll draw the wrong conclusion; second, if your material is AI-voiced podcasts or multi-character TTS audiobooks, try it on your own content first. The demo video on NVIDIA's model card uses 8 voices from NVIDIA's own TTS, so the model can tell some synthetic voices apart; it just needs enough difference between them.

We couldn't find a labelled real Mandarin meeting sample under 5GB, so for Mandarin we can only cite the self-reported AliMeeting numbers above and Baseten's AISHELL-4 figure.

### What About NeMo Python and Transformers?

- **NeMo Speech (Python)**: the model card's install instructions start with `apt-get`, and its hardware table lists only NVIDIA GPUs. NeMo is written in PyTorch, so Mac CPU / MPS inference should work in theory, but NVIDIA makes no promise and we didn't install it (the dependencies are heavy). Training and fine-tuning effectively require Linux plus NVIDIA.
- **Transformers**: supported natively (`AutoModelForAudioFrameClassification`, model type `nemotron3_diarization`), but you need to install transformers from the main branch. The model card gives complete code for both offline and streaming use. Running it on a Mac through PyTorch should work; we didn't verify it.

For Mac users, NeMo-Speech.cpp is the least effort right now: a 13MB binary plus a 107MB GGUF, no Python needed.

## How Do You Choose Between It and pyannote community-1?

| | Nemotron 3 Diarization | pyannote community-1 |
|---|---|---|
| License | OpenMDW-1.1, no login | CC-BY-4.0, must agree to share contact info on HF |
| Form | single end-to-end model (100M) | segmentation + embedding + clustering pipeline |
| Speaker limit | hard cap of 8 | no hard cap, speaker count can be specified |
| Streaming | native, 0.32-1.04 s latency | mainly offline |
| Local on Mac | C++ runtime, self-build for now | `pip install pyannote.audio`, CPU by default |
| Ecosystem | just released, tightly coupled to NVIDIA ASR | most mature, default in tools like WhisperX |
| Public comparison | in Baseten's test, lost to community-1 only on AMI | self-reported, different label protocol |

The short version: **for real-time use, meetings of 8 people or fewer, and plans to use NVIDIA's ASR, pick Nemotron 3. For recorded files, unpredictable headcounts, or an existing WhisperX-style toolchain, pyannote is still the easier default.** The 8-speaker cap is hard: the model card says that with more than 8 speakers "speech can be missed or assigned to the wrong channel".

## How Do You Set Up Meeting Transcription Plus Diarization on a Mac?



Diarization gives you only the timetable. To get "who said what" you also need an ASR with word-level timestamps, then assign each word to a speaker by time. There are three routes:

**Route A: one NeMo-Speech.cpp command.** After building with a preset that includes ASR (for example `metal-asr`, which also compiles diarization):

```bash
ffmpeg -i meeting.m4a -ac 1 -ar 16000 -c:a pcm_s16le meeting.wav
nemo-speech transcribe meeting.wav --diarize --json
```

Every word in the JSON carries a 1-based `speaker` field, and main already makes Nemotron 3 the default model for `--diarize`. The default ASR is Nemotron 3.5 ASR Streaming 0.6B, also under OpenMDW-1.1. A caution for Mandarin: the ASR covers 40 language-locales, and Mandarin (zh-CN) sits in the second "broad-coverage" tier, not among the top 19 "transcription-ready" locales. For English, NVIDIA recommends its dedicated English model. For live use there's `transcribe --live --diarize`, but speaker labels can change until they are confirmed.

**Route B: Whisper or another ASR, plus Nemotron 3 RTTM, aligned yourself.** This is the safer choice when Mandarin accuracy matters:

```bash
nemo-speech diarize meeting.wav --preset v3-offline --format rttm -o meeting.rttm
```

Then transcribe with any Mandarin ASR that outputs word timestamps (whisper.cpp, FunASR, etc.) and assign each word to whichever speaker segment contains its midpoint. NVIDIA's integration guide states the known weakness of this approach: when two people talk at once, the cut audio contains both voices, and a conventional ASR may merge their words. Meetings with little overlap are fine.

**Route C: multi-talker streaming ASR in NeMo Python.** The integration guide's official setup pairs Nemotron 3 Diarization with multitalker-parakeet-streaming-0.6b-v1 (English only, built for overlapping speech) or Nemotron 3.5 ASR, running a separate ASR stream per speaker. It gives the best results but needs CUDA, so Mac users can skip it.

Two more practical notes. Speaker numbers are anonymous, ordered by who speaks first, and independent per session. This is not voiceprint identification, so showing names needs your own enrollment or mapping step. And always convert input to 16kHz mono first.

## Limitations and Things to Watch

- 8-speaker hard cap: beyond that, speech is missed or misassigned, which rules out large meetings and big roundtables.
- Model and runtime out of sync: the model shipped on 09-23, but Mac-capable runtime support only reached main on 09-24 and hasn't been released yet.
- The numbers are almost all self-reported, with only NVIDIA's own previous model as the baseline. The one comparison that includes pyannote comes from NVIDIA partner Baseten.
- Speaker counting is worse than the previous generation on some datasets (AMI SCA 93.75% → 81.25-87.50%).
- In the model card's bias subcard, both "participation of protected groups" and "measures to mitigate bias" read "None".
- We didn't test real Mandarin meetings ourselves. There are only the AliMeeting / AISHELL-4 numbers, and both datasets' training splits were used in training.

## FAQ

**Q: Can Nemotron 3 Diarization transcribe text?**
No. It outputs each speaker's speaking probability every 10 ms. Text needs an ASR.

**Q: Can I use it commercially?**
Yes. OpenMDW-1.1 allows commercial use with no revenue threshold and no restrictions on outputs. Include the license and copyright notices when you redistribute the weights.

**Q: How much memory does it need?**
The q8_0 GGUF is only 107MB, and 10 minutes of audio ran easily on our 16GB M4. Memory is barely a concern. The barrier right now is building the runtime yourself.

**Q: How low can the latency go?**
One checkpoint supports four recommended settings: 0.32 / 0.64 / 1.04 / 30.4 s. The theoretical minimum is 80 ms, but NVIDIA doesn't recommend it. These figures are input-buffer latency and exclude compute time.

**Q: How good is it on Mandarin?**
Self-reported DER on AliMeeting is 6.40% near-field and 10.47% far-field, and Baseten measured 9.8% on AISHELL-4. We couldn't find a usable real Mandarin test sample. A test with system-synthesized voices labelled everyone as the same speaker, and that method isn't reliable anyway.

**Q: Should I switch from Sortformer 4spk?**
Yes if your meetings often have 5 or more people, or the license matters to you. For 2-4 person phone calls, the two generations are close on CALLHOME (offline 10.32 → 9.10), so there's no rush.

## Primary Sources

- Model card: https://huggingface.co/nvidia/Nemotron-3-Diarization
- ASR integration guide: https://huggingface.co/nvidia/Nemotron-3-Diarization/blob/main/ASR_INTEGRATION_GUIDE.md
- Evaluation notes: https://huggingface.co/nvidia/Nemotron-3-Diarization/blob/main/diarization_evaluation.md
- NVIDIA blog: https://huggingface.co/blog/nvidia/nemotron-diarization
- NeMo-Speech.cpp: https://github.com/NVIDIA/NeMo-Speech.cpp
- OpenMDW-1.1 license: https://openmdw.ai/license/1-1/
- Previous model: https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1
- Streaming Sortformer paper: https://arxiv.org/abs/2507.18446
- Baseten test: https://www.baseten.co/blog/nvidia-nemotron-3-diarization/
- pyannote community-1: https://huggingface.co/pyannote/speaker-diarization-community-1
- Nemotron 3.5 ASR: https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
