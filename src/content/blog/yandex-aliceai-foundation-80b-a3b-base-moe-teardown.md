---
title: "Yandex 开源 AliceAI-Foundation-80B-A3B 基座模型：Apache-2.0 属实，俄语强，中文分词比 Qwen 多耗 58%"
titleEn: "Yandex Open-Sources AliceAI-Foundation-80B-A3B Base: Apache-2.0 Confirmed, Strong in Russian, 58% More Tokens Than Qwen for Chinese"
description: "AliceAI-Foundation-80B-A3B-Base 是 Yandex 从零训练的 80B 总参、约 3B 激活的 MoE 基座模型，Apache-2.0（LICENSE 文件已核实），上下文 262,144。骨架几乎照搬 Qwen3-Next-80B-A3B，换成 Kimi Delta Attention、注意力残差和 sigmoid 路由；benchmark 全部自跑，20 行里 12 行是 Yandex 自建的俄语测试。本机实测它的分词器：同一批纯中文段落比 Qwen3-Next 多用 58% 的 token，GB2312 一级 3755 个常用字只有 726 个是单独 token。官方 bf16 权重约 162.6GB，社区 4-bit 约 45GB、混合 2/4-bit 约 28GiB，Mac 至少 48GB 起步，且要用第三方补丁代码。"
descriptionEn: "AliceAI-Foundation-80B-A3B-Base is Yandex's from-scratch MoE base model with 80B total and about 3B active parameters, Apache-2.0 (verified in the LICENSE file), 262,144-token context. Its skeleton closely follows Qwen3-Next-80B-A3B, swapping in Kimi Delta Attention, attention residuals and sigmoid routing; every benchmark is self-run, and 12 of 20 rows are Yandex-built Russian tests. We measured its tokenizer locally: on the same pure-Chinese paragraphs it needs 58% more tokens than Qwen3-Next, and only 726 of the 3,755 GB2312 level-1 characters are single tokens. Official bf16 weights are about 162.6GB; community 4-bit ports are about 45GB and a mixed 2/4-bit port about 28GiB, so a Mac needs 48GB or more, plus third-party patched code."
pubDate: "2026-09-24"
updatedDate: "2026-09-24"
category: "Research"
tags: ["AliceAI", "Yandex", "MoE", "Qwen3-Next", "Kimi Delta Attention", "开源大模型", "分词器", "Apple Silicon", "本地部署"]
heroImage: "../../assets/images/yandex-aliceai-foundation-80b-a3b-base-moe-teardown-banner.jpg"
author: "Mycelium Protocol"
wechatTitle: "Yandex开源80B基座模型：中文多耗58% token"
wechatDigest: "从零训练的80B-A3B基座，Apache-2.0，俄语强；中文多耗58%token，Mac需48GB起"
---

**BLUF**：AliceAI-Foundation-80B-A3B-Base 是俄罗斯 Yandex 在 HuggingFace 上开源的一个大语言模型基座：总参数 80B、每个 token 只激活约 3B 的混合专家（MoE）结构，上下文 262,144 token，许可证确实是 Apache-2.0（仓库里的 LICENSE 文件写着 Copyright 2026 YANDEX LLC）。它的层数、宽度、专家数、激活专家数和 Qwen3-Next-80B-A3B 一模一样，差别在线性注意力换成了 Kimi Delta Attention、残差换成了注意力残差、路由换成了 sigmoid。对中文读者有三点要先知道：一是它是 Base 不是对话模型，不能直接聊；二是它的分词器对中文不友好，我们本机实测同一批纯中文段落比 Qwen3-Next 多用 58% 的 token；三是官方 bf16 权重约 162.6GB，Mac 只能靠社区量化版，最低 48GB 内存，而且要运行第三方补丁代码。它真正强的是俄语，以及它是少见的 80B 级、从零训练、Apache-2.0 的「基座」权重，适合拿来做后训练研究。

> 📌 一手资料
> 模型页：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base
> 英文模型卡：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/README_en.md
> Yandex 新闻稿（2026-09-21）：https://ir.yandex/press-releases?year=2026&id=2026-09-21
> Yandex 技术文章（Habr，俄文）：https://habr.com/ru/companies/yandex/articles/1083300/
> vLLM 支持 PR：https://github.com/vllm-project/vllm/pull/57963

---

## 为什么要看这个模型？

最近几个月，80B 级、约 3B 激活的 MoE 已经成了「高端个人电脑能跑的最大一档」：权重大，但每个 token 算得少，只要内存装得下，速度可以接近小模型。Qwen3-Next-80B-A3B 是这一档的代表。

Yandex 这次发的东西有两个少见的地方：一是它是从零训练的，不是在别家权重上微调；二是它放出的是 Base（预训练基座），而 Qwen3-Next 在 HuggingFace 上只放了 Instruct 和 Thinking 两个后训练版本，没有放 Base。想自己做 SFT、RL 或领域继续预训练的人，一个 80B 级、Apache-2.0 的干净基座是稀缺资源。

但我们这边关心的问题更具体：中文能不能用？Mac 能不能跑？许可证和「trust_remote_code」有没有坑？下面逐个核实。

说明：本文数字来自 HuggingFace API、模型卡、仓库文件和 Yandex 官方文章，标注「据 XX」的是二手来源。我们没有下载权重，没有跑过模型本身；本机实测只做了分词器（tokenizer.model 只有 2.6MB）。本机是 16GB 的 Mac mini M4，装不下这个模型的任何版本。

## AliceAI-Foundation-80B-A3B 到底是什么？

HuggingFace API 和模型卡给出的基本事实（2026-09-24 抓取）：

- 参数：safetensors 元数据统计 81,286,433,408 个参数，全部 BF16（包含 1 层 MTP 多 token 预测头）
- 权重文件：49 个分片，合计约 162.6GB
- 结构：48 层，隐藏维度 2048，布局为 12 ×（3 × KDA 层 + 1 × 门控全注意力层），每层后接 MoE
- MoE：512 个专家，每个 token 路由 10 个，另加 1 个共享专家，专家中间维度 512
- 全注意力层：16 个 query 头、2 个 KV 头，头维度 256，只对 25% 的维度做旋转位置编码
- 上下文：262,144 token
- 词表：129,024，SentencePiece BPE，以 LlamaTokenizer 加载
- 许可证：Apache-2.0；另有一份 NOTICES 文件提醒使用者遵守出口管制法规；向仓库贡献代码要签 Yandex 的 CLA
- 热度：下载 2,678 次，311 个赞；仓库 9 月 12 日创建，9 月 18 日首次提交权重，9 月 21 日发新闻稿

训练数据量模型卡里只写了「关键设计用多轮 2T token 的从零训练来验证」，没写正式训练量。据 Yandex 在 Habr 发的技术文章，正式训练分四段：8K 上下文预训练 17.5T token，32K 扩展 50B，256K 扩展 240B，再用 128K 上下文做 280B 的推理数据训练，合计约 18T token；约 30% 是合成或半合成数据，5–10% 是推理轨迹和 Agent 交互数据，优化器用的是 Muon。我们读到的数据构成里重点是俄语和英语，没有提到中文。

一个小插曲：我们的采集系统把这个模型的许可证标成「未声明」，但仓库的 LICENSE 文件、模型卡 frontmatter、HF API 的 cardData 三处都是 apache-2.0，这里以一手文件为准。

## 它和 Qwen3-Next-80B-A3B 有什么不同？



把两份 config.json 并排放，相同的地方比不同的多：

| 项目 | AliceAI-Foundation-80B-A3B-Base | Qwen3-Next-80B-A3B |
|---|---|---|
| 总参数（safetensors 统计） | 81.29B | 81.32B |
| 层数 / 隐藏维度 | 48 / 2048 | 48 / 2048 |
| 专家 / 每 token 激活 | 512 / 10 + 1 共享 | 512 / 10 + 1 共享 |
| 线性:全注意力 | 3:1（36 层 KDA + 12 层门控注意力） | 3:1（36 层 Gated DeltaNet + 12 层门控注意力） |
| 全注意力头 | 16 Q / 2 KV，头维度 256 | 16 Q / 2 KV，头维度 256 |
| 线性注意力 | Kimi Delta Attention，32 个 QK 头 | Gated DeltaNet，16 个 QK 头 / 32 个 V 头 |
| 路由 | sigmoid + 偏置修正 | softmax 归一化 |
| 残差 | 分块注意力残差（每 4 层一块） | 常规残差 |
| 词表 | 129,024 | 151,936 |
| 训练量 | 约 18T（据 Habr） | 15T（Qwen 模型卡） |
| 上下文 | 262,144 | 262,144（可用 YaRN 扩到约 101 万） |
| HF 公开版本 | 只有 Base | 只有 Instruct / Thinking |
| 许可证 | Apache-2.0 | Apache-2.0 |

Yandex 自己不回避这一点。Yandex 工程师提交给 vLLM 的 PR 原话是：相比 Qwen3Next，AliceAI 用 Kimi Delta Attention 替换 Gated DeltaNet，用分块注意力残差替换标准残差，用带偏置修正的 sigmoid 路由替换 softmax 路由；代码层面也是「从现有 Qwen3Next 配置派生」。Habr 文章同样写明架构以 Qwen3-Next 为起点。

「从零训练」和「照搬架构」并不矛盾：架构是公开的设计图，权重才是训练出来的东西。词表大小不同、线性注意力的参数形状不同，至少说明它不可能是 Qwen3-Next 权重的简单微调。但权重到底怎么来的，外部无法验证，我们只能说「Yandex 声称从零训练，公开证据与此不矛盾」。

## benchmark 可信吗？



模型卡的第一张表有 20 行，全部是 Yandex「内部评测基础设施」跑的，所有对比模型都在 vLLM 里用 temperature 0 推理，没有第三方复现。我们把这 20 行分成两类：

- Yandex 自建或基于自家产品数据的测试，共 12 行：WikiWebFacts、HardMultiQA、CultCat、6 个 EduBench（题目来自用户向 Alice 提的问题）、2 个 ExpertFactsQA、EGE（俄罗斯高考题）。AliceAI 在其中 10 行拿第一，差距很大，比如 ExpertFactsQA Law 49.6 对 Qwen3.5-35B-A3B-Base 的 27.9。
- 公开的英文或通用测试，共 8 行：TriviaQA、MMLU-Pro、SuperGPQA、MATH-500、BigCodeBench、LiveCodeBench、FinQA 128k、LongMemEval 128k。AliceAI 明确领先的只有 MATH-500（91.1）；LiveCodeBench 50.5 对 50.4、FinQA 74.1 并列，基本打平；TriviaQA（79.0 对最高 89.8）、MMLU-Pro（66.8 对 69.9）、SuperGPQA、BigCodeBench、LongMemEval 都落后于 Nemotron-3-Super 或 DeepSeek-V4-Flash。另外 BigCodeBench 是 Yandex「改进了测试用例的自家实现」，不是原版。

第二张表是推理题：AIME 2026 pass@32 96.7、HMMT 2026 2 月 pass@32 96.9、LiveCodeBench pass@1 60.4。pass@32 的意思是「采 32 次，只要有一次对就算对」，对基座模型来说这是在测潜力上限，不代表你单次提问能拿到这个正确率。

还有一点：主要对手 Qwen3.5-35B-A3B-Base 的总参数只有它的 44%。总参数大一倍多、知识题赢，并不意外。更公平的对照本该是同尺寸的 Qwen3-Next-80B-A3B-Base，但阿里没有公开这个 Base，所以也没法比。

结论：俄语事实知识这块它大概率确实强（新闻稿说它在俄语测试上追平了 Yandex 自家闭源的 Alice AI LLM，后者总参数是它的 3 倍、激活参数是 7 倍），但这些测试本身是 Yandex 出的题。英文通用能力是同档中游。

## 中文能力怎么样？分词器实测



模型卡的语言标签只有 ru 和 en。我们下载了 2.6MB 的 tokenizer.model，在本机用 sentencepiece 实测，对照组是 Qwen3-Next-80B-A3B 的 tokenizer.json。

测试一：从本站最近 40 篇文章里抽出 142 段纯中文段落（汉字占比 75% 以上），共 8,775 个字符：

- AliceAI：8,669 个 token，约每字符 0.99 个 token
- Qwen3-Next：5,493 个 token，约每字符 0.63 个 token
- AliceAI 多用 58%；其中 24.6% 的 token 是「字节回退」，也就是一个汉字被拆成 3 个 UTF-8 字节 token

测试二：词表覆盖。129,024 个词条里，含汉字的只有 1,629 个，单个汉字的词条 923 个。GB2312 一级字库（3,755 个最常用汉字）里，只有 726 个能作为单独 token，其余要靠字节回退。实际例子：「混合专家模型」里的「混」、「激活」的「激」、「部署」的「署」、「稠密」的「稠」都被拆成了 3 个字节 token。

测试三：同一句话的三种语言版本（意思相同，讲 MoE 推理成本）：

| 语言 | AliceAI token | Qwen3-Next token | 比值 |
|---|---|---|---|
| 中文（63 字符） | 70 | 41 | 1.71 |
| 英文（237 字符） | 48 | 45 | 1.07 |
| 俄文（261 字符） | 49 | 83 | 0.59 |

这张表很直观：俄语上 Qwen 要多花 69% 的 token，中文上 AliceAI 要多花 71%。分词器是为俄英设计的。

这对中文用户意味着三件事：同样 262K 的上下文窗口，能装的中文内容大约只有 Qwen 的六成多；生成同样长度的中文要多跑约 1.6 倍的解码步数；大量字节回退通常也说明训练数据里中文很少，模型的中文知识和表达质量大概率不如 Qwen 系。第三点是推断，我们没有跑模型验证。

## Base 模型对普通用户意味着什么？

Base 是只做过预训练的「续写器」：你给它一段开头，它接着往下写。它没有学过「用户问、助手答」的格式，也没有经过安全对齐。直接问「帮我写个脚本」，它可能接着编出第二个问题，或者自问自答停不下来。

模型卡明确说：仓库附带的 chat_template.jinja 是给微调准备训练数据用的，故意没有设成默认对话模板。这份模板里角色前缀是「user:」「assistant:」，推理过程包在 [COT_START] 和 [COT_END] 之间，工具说明的前缀是俄语「Тебе доступны следующие функции:」（你可以使用以下函数）。也就是说，它预训练时见过这种格式的推理和工具调用数据，但要当助手用，还得自己做 SFT。仓库附了一个 LoRA 微调示例，官方写明要 4 张 80GB 显卡、FSDP2。

社区量化作者给出的用法也印证了这一点：MLX 4-bit 版的作者写了一个 few-shot 前缀，还要靠外部规则检测「下一个问题开头」来截断输出，他明确说这「不是自然结束」。

所以对大多数人：想要能聊天、能写代码的本地助手，这个模型现在不适合你；等官方或社区出 Instruct 版本再说。新闻稿提到 Yandex 后续的推理模型会支撑 Alice AI 的 Agent 能力，但没有给 Instruct 版本的发布时间。

## trust_remote_code 有什么安全含义？

HF 标签里的 custom_code 表示 transformers 里没有这个架构，加载时要加 `trust_remote_code=True`，让 transformers 从仓库下载并执行 Python 代码。这个仓库的远程代码只有两个文件：

- configuration_alice_ai.py（109 行，4.9KB）
- modeling_alice_ai.py（876 行，35KB）

我们通读了导入语句：只引用 torch 和 transformers，没有网络请求、subprocess、eval 之类的调用。在 CUDA 上会额外导入 flash-linear-attention 的 KDA 内核；在其他设备上退回纯 PyTorch 实现，而这个实现是逐个 token 循环计算的，在 Mac 的 MPS 上会非常慢。

真正的风险不在今天这份代码，而在「以后」：不锁版本时，每次加载都会拉仓库最新代码。建议加 `revision="84105ba3dc09f9e8141e69b74761af9a4d848f48"`（2026-09-24 的 main 分支提交）锁定。

另外两处需要额外的信任：

- 官方 vLLM 用法是运行 Docker 镜像 `yamlbrand/alice-ai-vllm:latest`，不是 vLLM 官方镜像。Docker Hub 显示这个账号只有这一个镜像，9 月 18 日注册，846 次拉取，没有公开 Dockerfile。讨论区有用户问 Dockerfile，一位 Yandex 成员回复说镜像里是和 vLLM PR #57963 基本相同的分支。命令里还带着 `--pull=always`，意味着每次启动都会拉最新的 latest 标签。生产环境建议等 PR 合并，或者至少锁定镜像摘要。
- 社区的 GGUF 和 MLX 版本都要运行作者自带的 llama.cpp 补丁或 model.py，这些是个人作者的代码，和 Yandex 无关，运行前要自己审一遍。

## 能在哪些推理框架上跑？

截至 2026-09-24：

- Transformers：官方参考版本 5.16.1，需要 trust_remote_code；GPU 上还要 flash-linear-attention 0.5.0
- vLLM：原生支持的 PR #57963 由 Yandex 工程师在 9 月 21 日提交，状态是 open、标了 needs-rebase；PR 自述不支持流水线并行，MTP 只支持 1 层。现在只能用上面那个第三方 Docker 镜像
- SGLang：讨论区有人问，没有回答
- llama.cpp / Ollama / LM Studio：上游没有 alice_ai 架构。社区有两个 GGUF 仓库，但都声明需要补丁版运行时
- MLX：上游 mlx-lm 没有原生支持，社区有两个带自定义 model.py 的量化版

对比之下，Qwen3-Next 的 qwen3next 架构早已进入 llama.cpp 上游。这是同档模型里 AliceAI 目前最大的实用短板。

## Mac 能不能跑？要多大内存？



我们没有下载权重，下面是按文件大小推算加社区作者自报的数据：

| 版本 | 权重大小 | 来源 | 适合的 Mac |
|---|---|---|---|
| 官方 bf16 | 约 162.6GB | yandex 官方 | 192GB 以上（如大内存 Mac Studio），且 Mac 上走纯 PyTorch 慢路径，不推荐 |
| 社区 GGUF Q8_0 | 约 84.7GB | AMAImedia | 128GB；需补丁版运行时 |
| 社区 GGUF Q4_K_M | 48.4GB（45.1GiB） | Yamada114514 | 64GB 勉强，96GB 以上舒服；需补丁版 llama.cpp |
| 社区 MLX 4-bit | 约 44.9GB | Yamada114514 | 64GB 勉强，96GB 以上舒服 |
| 社区 MLX 混合 2/4-bit | 28.29GiB | Hosstia | 48GB |
| 16GB / 24GB / 32GB Mac | — | — | 任何版本都装不下 |

KV 缓存压力很小，这是混合注意力的好处：48 层里只有 12 层全注意力，每层 2 个 KV 头、头维度 256，按 bf16 推算每个 token 只占约 24KB，128K 上下文约 3.2GB，满 262K 约 6.4GB；36 层 KDA 的循环状态是固定大小，约 75MB。所以内存主要花在权重上。

社区作者的自报数据（均为小样本冒烟测试，不是严格基准）：

- Q4_K_M GGUF 在 M5 Max 128GB 上解码约 64–65 token/s，峰值常驻内存 45.58GiB。作者还发现 Metal 的批量矩阵内核会降低激活精度，第一版预填充和逐 token 解码的 logits 差了 7.02%，补丁强制 FP32 激活后才逐位一致，代价是预填充变慢。
- MLX 4-bit 在同一台机器上解码中位数约 48 token/s；另一位作者说它在 48GB 机器上会严重换页。
- 混合 2/4-bit 版把占全部参数 96.9% 的专家层压到 2-bit，其余保持 4-bit。作者自测：统一 2-bit（23.26GiB）在 5 道简单问答里只答对 1 道，把「法国首都」答成俄语「закон」（法律）；混合版 5 道全对，在 M4 Pro 48GB 上能全速跑。注意这是 4-bit 再反量化再压成 2-bit 的「二次量化」，精度损失比从 bf16 直接量化更大，5 道题的测试也说明不了太多。

给 Mac 用户的具体建议：

- 16–32GB：跑不了，别下载。同档想本地跑，也只能找更小的模型。
- 48GB：可以试混合 2/4-bit 的 MLX 版，当作体验俄英续写的玩具，不要期待质量。
- 64GB：Q4 能装下，但系统和其他程序会挤，长上下文容易换页。
- 96GB 以上：Q4 比较从容。但如果你的目标是中文，同样的内存跑 Qwen3-Next-80B-A3B 的 Instruct 版更合适：有上游 llama.cpp 和 MLX 支持、有对话能力、中文分词效率高得多（同样的中文少用约 37% 的 token）。

## 和同类怎么选？

- 要中文、要能聊天、要本地好部署：Qwen3-Next-80B-A3B-Instruct / Thinking，或者更新的 Qwen3.5 系列。
- 要俄语内容、俄罗斯法律教育这类本地知识：AliceAI 是目前开放权重里自报成绩最好的选择之一，但测试是 Yandex 自己出的，要在自己的数据上验证。
- 要一个干净的 80B 级 Apache-2.0 基座做后训练研究：AliceAI 有独特价值，因为同档的 Qwen3-Next 没有公开 Base。它还附了 WikiWebFacts、HardMultiQA 两个俄语事实评测数据集和评测协议。
- 要一个能直接用的助手：都别选 Base 模型。

顺带一提，Yandex 在 9 月 10 日（比这个仓库早两天建仓）还开源了一个 AliceAI-T5-35B-A0.6B，我们这次没有核实它。

## 背景：Yandex、Alice AI 和 YandexGPT

Alice（俄语 Алиса）是 Yandex 的语音助手品牌。2023 年 5 月，Yandex 发布 YandexGPT 并接入 Alice；2025 年 10 月 28 日，Yandex 在「Alice, what's new?」发布会上推出 Alice AI，背后是新的模型家族 Alice AI LLM、Alice AI VLM 和 Alice AI Art（据 Yandex 官方新闻稿）。这次开源模型用的就是 Alice AI 这个品牌。

Yandex 的开源历史（据 HuggingFace 上 yandex 账号的模型列表和相关报道）：

- 2022 年 6 月：YaLM-100B，100B 稠密模型，Apache-2.0，约 300B token 训练
- 2025 年 2–3 月：YandexGPT-5-Lite-8B 的 pretrain 和 instruct 版本，用的是自定义的 YandexGPT-5-Lite-8B License，不是标准开源许可证
- 2026 年 9 月：AliceAI-T5-35B-A0.6B 和本文的 AliceAI-Foundation-80B-A3B-Base，本文这个是 Apache-2.0

从自定义许可证回到 Apache-2.0，对想商用的人是好消息。

## 常见问题

**Q：许可证真的是 Apache-2.0 吗？能商用吗？**
A：是。仓库 LICENSE 文件是标准 Apache-2.0 文本，版权方 YANDEX LLC；模型卡和 HF API 也都标 apache-2.0。可以商用，但附带的 NOTICES 要求遵守适用的出口管制法规，企业使用时要让法务看一下这一条。

**Q：它是不是 Qwen3-Next 换皮？**
A：架构骨架基本照搬 Qwen3-Next，Yandex 自己也这么说；但线性注意力、残差、路由三处换了，词表也不同，不可能是 Qwen 权重的简单微调。权重是否完全从零训练，外部无法验证。

**Q：中文能用吗？**
A：能分词、能往回解码，不会出现未知字符；但同样的纯中文内容要多用约 58% 的 token，常用汉字大多要拆成字节，训练数据说明里也没有提到中文。中文场景不推荐。

**Q：16GB 的 Mac 能跑吗？**
A：不能。最小的社区版也有 28.29GiB。

**Q：能用 Ollama 或 LM Studio 吗？**
A：截至 9 月 24 日不能。上游 llama.cpp 没有这个架构，社区 GGUF 需要作者提供的补丁版运行时。

## 一手源

- 模型页：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base
- HF API：https://huggingface.co/api/models/yandex/AliceAI-Foundation-80B-A3B-Base
- 英文模型卡：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/README_en.md
- config.json：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/config.json
- LICENSE：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/LICENSE
- 远程代码：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/modeling_alice_ai.py
- 讨论区：https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/discussions
- Yandex 新闻稿：https://ir.yandex/press-releases?year=2026&id=2026-09-21
- Yandex Habr 技术文章（俄文）：https://habr.com/ru/companies/yandex/articles/1083300/
- vLLM PR #57963：https://github.com/vllm-project/vllm/pull/57963
- Docker 镜像：https://hub.docker.com/r/yamlbrand/alice-ai-vllm
- Qwen3-Next-80B-A3B-Instruct：https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct
- 社区 GGUF Q4_K_M：https://huggingface.co/Yamada114514/AliceAI-Foundation-80B-A3B-Base-GGUF
- 社区 GGUF 全套：https://huggingface.co/AMAImedia/AliceAI-Foundation-80B-A3B-BF16-GGUF
- 社区 MLX 4-bit：https://huggingface.co/Yamada114514/AliceAI-Foundation-80B-A3B-Base-MLX-4bit
- 社区 MLX 混合 2/4-bit：https://huggingface.co/Hosstia/AliceAI-Foundation-80B-A3B-Base-MLX-2bit
- Alice AI 发布（2025-10-28）：https://yandex.com/company/news/2025-10-28-01
- YaLM-100B：https://github.com/yandex/YaLM-100B
- YandexGPT-5-Lite-8B-pretrain：https://huggingface.co/yandex/YandexGPT-5-Lite-8B-pretrain

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

**BLUF**: AliceAI-Foundation-80B-A3B-Base is a large language model base that Russia's Yandex open-sourced on HuggingFace: a mixture-of-experts (MoE) model with 80B total parameters and about 3B active per token, a 262,144-token context, and a license that really is Apache-2.0 (the repo's LICENSE file reads Copyright 2026 YANDEX LLC). Its depth, width, expert count and active-expert count are identical to Qwen3-Next-80B-A3B; the differences are Kimi Delta Attention in place of the linear attention, attention residuals in place of plain residuals, and sigmoid routing. Three things matter up front for Chinese readers: it is a Base model, not a chat model; its tokenizer is unfriendly to Chinese, and our local test shows 58% more tokens than Qwen3-Next on the same pure-Chinese paragraphs; and the official bf16 weights are about 162.6GB, so Macs depend on community quantizations, need at least 48GB, and must run third-party patched code. Its real strengths are Russian, and the fact that it is a rare 80B-class, from-scratch, Apache-2.0 base checkpoint that is useful for post-training research.

> 📌 Primary sources
> Model page: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base
> English model card: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/README_en.md
> Yandex press release (2026-09-21): https://ir.yandex/press-releases?year=2026&id=2026-09-21
> Yandex technical write-up (Habr, Russian): https://habr.com/ru/companies/yandex/articles/1083300/
> vLLM support PR: https://github.com/vllm-project/vllm/pull/57963

---

## Why Look at This Model?

Over the past few months, 80B-class MoE models with about 3B active parameters have become the largest tier that high-end personal machines can run: the weights are big, but each token needs little compute, so if memory fits, speed can approach that of a small model. Qwen3-Next-80B-A3B is the reference model in this tier.

Yandex's release is unusual in two ways. First, it was trained from scratch rather than fine-tuned from someone else's weights. Second, it is a Base (pretrained) checkpoint, whereas Qwen3-Next on HuggingFace ships only Instruct and Thinking post-trained variants and no Base. For anyone who wants to run their own SFT, RL or domain continued pretraining, a clean 80B-class Apache-2.0 base is scarce.

Our questions are more concrete, though: is Chinese usable? Can a Mac run it? Are there traps in the license or in `trust_remote_code`? We checked each in turn.

Note: numbers here come from the HuggingFace API, the model card, repo files and Yandex's own publications; anything marked "according to X" is secondary. We did not download the weights or run the model itself; our only local test was the tokenizer (tokenizer.model is just 2.6MB). This machine is a 16GB Mac mini M4, which cannot hold any version of the model.

## What Exactly Is AliceAI-Foundation-80B-A3B?

Basic facts from the HuggingFace API and model card (fetched 2026-09-24):

- Parameters: safetensors metadata counts 81,286,433,408 parameters, all BF16 (including one MTP multi-token-prediction layer)
- Weight files: 49 shards, about 162.6GB in total
- Structure: 48 layers, hidden size 2048, laid out as 12 × (3 × KDA layer + 1 × gated full-attention layer), each followed by MoE
- MoE: 512 experts, 10 routed per token plus 1 shared expert, expert intermediate size 512
- Full-attention layers: 16 query heads, 2 KV heads, head dimension 256, rotary embedding on 25% of dimensions
- Context: 262,144 tokens
- Vocabulary: 129,024, SentencePiece BPE, loaded as LlamaTokenizer
- License: Apache-2.0; a separate NOTICES file reminds users to comply with export-control laws; contributing code to the repo requires signing Yandex's CLA
- Traction: 2,678 downloads and 311 likes; repo created September 12, weights first committed September 18, press release September 21

On training data, the model card only says key design decisions were validated through separate from-scratch runs of 2T tokens each; it does not state the full training volume. According to Yandex's Habr write-up, training ran in four stages: 17.5T tokens of pretraining at 8K context, a 50B extension at 32K, 240B at 256K, then 280B of reasoning data at 128K, about 18T in total. Roughly 30% was synthetic or semi-synthetic, 5–10% was reasoning traces and agent interactions, and the optimizer was Muon. The data breakdown we read emphasizes Russian and English and does not mention Chinese.

A side note: our collection system tagged this model's license as "not declared", but the LICENSE file, the model card frontmatter and the HF API cardData all say apache-2.0. The primary files win.

## How Does It Differ From Qwen3-Next-80B-A3B?



Put the two config.json files side by side and the similarities outnumber the differences:

| Item | AliceAI-Foundation-80B-A3B-Base | Qwen3-Next-80B-A3B |
|---|---|---|
| Total params (safetensors) | 81.29B | 81.32B |
| Layers / hidden size | 48 / 2048 | 48 / 2048 |
| Experts / active per token | 512 / 10 + 1 shared | 512 / 10 + 1 shared |
| Linear : full attention | 3:1 (36 KDA + 12 gated attention) | 3:1 (36 Gated DeltaNet + 12 gated attention) |
| Full-attention heads | 16 Q / 2 KV, head dim 256 | 16 Q / 2 KV, head dim 256 |
| Linear attention | Kimi Delta Attention, 32 QK heads | Gated DeltaNet, 16 QK / 32 V heads |
| Routing | sigmoid + bias correction | softmax, normalized |
| Residuals | block attention residuals (blocks of 4 layers) | standard |
| Vocabulary | 129,024 | 151,936 |
| Training tokens | ~18T (per Habr) | 15T (Qwen model card) |
| Context | 262,144 | 262,144 (extendable to ~1.01M with YaRN) |
| Public HF variants | Base only | Instruct / Thinking only |
| License | Apache-2.0 | Apache-2.0 |

Yandex does not hide this. The vLLM PR from a Yandex engineer says that, compared with Qwen3Next, AliceAI replaces Gated DeltaNet with Kimi Delta Attention, standard residuals with Block Attention Residuals, and softmax routing with sigmoid routing plus expert-score correction bias; in code, its config is "derived from the existing Qwen3Next configuration". The Habr write-up likewise says the architecture started from Qwen3-Next.

"Trained from scratch" and "borrowed architecture" are not in conflict: an architecture is a public blueprint, and weights are what training produces. The different vocabulary size and different linear-attention parameter shapes at least rule out a simple fine-tune of Qwen3-Next weights. But outsiders cannot verify how the weights were produced, so the fair statement is: Yandex says it trained from scratch, and the public evidence does not contradict that.

## Can the Benchmarks Be Trusted?



The model card's first table has 20 rows, all run on Yandex's "internal evaluation infrastructure", with every compared model served in vLLM at temperature 0, and no third-party replication. We split the 20 rows into two groups:

- Tests built by Yandex or from its own product data, 12 rows: WikiWebFacts, HardMultiQA, CultCat, six EduBench sets (built from questions users asked Alice), two ExpertFactsQA sets, and EGE (Russian national exam). AliceAI tops 10 of these, often by a lot, e.g. ExpertFactsQA Law 49.6 versus 27.9 for Qwen3.5-35B-A3B-Base.
- Public English or general benchmarks, 8 rows: TriviaQA, MMLU-Pro, SuperGPQA, MATH-500, BigCodeBench, LiveCodeBench, FinQA 128k, LongMemEval 128k. AliceAI clearly leads only on MATH-500 (91.1). LiveCodeBench 50.5 versus 50.4 and a tie on FinQA at 74.1 are effectively draws. It trails Nemotron-3-Super or DeepSeek-V4-Flash on TriviaQA (79.0 versus a best of 89.8), MMLU-Pro (66.8 versus 69.9), SuperGPQA, BigCodeBench and LongMemEval. BigCodeBench is also "our implementation with improved tests", not the original.

The second table covers reasoning: AIME 2026 pass@32 96.7, HMMT February 2026 pass@32 96.9, LiveCodeBench pass@1 60.4. Pass@32 means "sample 32 times and count it correct if any one is right". For a base model that measures a ceiling of potential, not the accuracy you get from a single prompt.

One more thing: the main rival, Qwen3.5-35B-A3B-Base, has only 44% as many total parameters. A model with more than twice the total parameters winning knowledge questions is not surprising. The fairer comparison would be a same-size Qwen3-Next-80B-A3B-Base, but Alibaba never published that Base, so it cannot be done.

Bottom line: the Russian factual-knowledge strength is probably real (the press release says it matches Yandex's closed Alice AI LLM on Russian benchmarks, a model with 3x the total and 7x the active parameters), but Yandex wrote those tests. On general English ability it sits mid-pack in its class.

## How Good Is Its Chinese? A Tokenizer Test



The model card lists only ru and en. We downloaded the 2.6MB tokenizer.model and measured it locally with sentencepiece, using Qwen3-Next-80B-A3B's tokenizer.json as the baseline.

Test 1: 142 pure-Chinese paragraphs (over 75% Han characters) from our 40 most recent posts, 8,775 characters in total:

- AliceAI: 8,669 tokens, about 0.99 tokens per character
- Qwen3-Next: 5,493 tokens, about 0.63 tokens per character
- AliceAI needs 58% more; 24.6% of its tokens are byte fallbacks, i.e. one Chinese character split into three UTF-8 byte tokens

Test 2: vocabulary coverage. Of 129,024 entries, only 1,629 contain Han characters, and 923 are single characters. Of the 3,755 most common characters in GB2312 level 1, only 726 exist as single tokens; the rest fall back to bytes. Concretely, 混 in 混合专家模型 (mixture of experts), 激 in 激活 (activate), 署 in 部署 (deploy) and 稠 in 稠密 (dense) each become three byte tokens.

Test 3: one sentence in three languages (same meaning, about MoE inference cost):

| Language | AliceAI tokens | Qwen3-Next tokens | Ratio |
|---|---|---|---|
| Chinese (63 chars) | 70 | 41 | 1.71 |
| English (237 chars) | 48 | 45 | 1.07 |
| Russian (261 chars) | 49 | 83 | 0.59 |

The table says it plainly: on Russian, Qwen spends 69% more tokens; on Chinese, AliceAI spends 71% more. The tokenizer was designed for Russian and English.

For Chinese users that means three things: the same 262K window holds only about 60-odd percent as much Chinese text as Qwen's; generating the same amount of Chinese takes about 1.6x the decoding steps; and heavy byte fallback usually signals little Chinese in the training data, so its Chinese knowledge and writing are likely weaker than Qwen's. The third point is an inference; we did not run the model to check it.

## What Does a Base Model Mean for Ordinary Users?

A Base model has only been pretrained. It is a continuation engine: give it an opening and it keeps writing. It has not learned the "user asks, assistant answers" format and has no safety alignment. Ask it to "write me a script" and it may invent a second question, or keep answering itself without stopping.

The model card says the bundled chat_template.jinja is for preparing fine-tuning data and is deliberately not set as the default chat template. In that template, role prefixes are "user:" and "assistant:", reasoning is wrapped in [COT_START] and [COT_END], and the tool-list prefix is Russian: "Тебе доступны следующие функции:" ("You have access to the following functions:"). So the model saw reasoning and tool-call data in this format during pretraining, but to use it as an assistant you still need your own SFT. The repo includes a LoRA fine-tuning example that officially requires four 80GB GPUs and FSDP2.

Community quantizers confirm this. The author of the MLX 4-bit port wrote a few-shot prefix and relies on an external rule that detects "the start of the next question" to cut output, stating plainly that this is "not natural EOS".

So for most people: if you want a local assistant that can chat and write code, this model is not for you yet. Wait for an official or community Instruct version. The press release says Yandex's upcoming reasoning model will power Alice AI's agentic features, but gives no date for an Instruct release.

## What Are the Security Implications of trust_remote_code?

The custom_code tag means transformers has no built-in class for this architecture, so loading requires `trust_remote_code=True`, which lets transformers download and execute Python code from the repo. This repo's remote code is just two files:

- configuration_alice_ai.py (109 lines, 4.9KB)
- modeling_alice_ai.py (876 lines, 35KB)

We read the imports: only torch and transformers, with no network calls, subprocess or eval. On CUDA it also imports the KDA kernels from flash-linear-attention; on other devices it falls back to a pure-PyTorch implementation that loops token by token, which will be very slow on Mac MPS.

The real risk is not today's code but tomorrow's: without pinning, every load pulls the latest repo code. Pin it with `revision="84105ba3dc09f9e8141e69b74761af9a4d848f48"` (the main-branch commit as of 2026-09-24).

Two more places require extra trust:

- The official vLLM instructions run the Docker image `yamlbrand/alice-ai-vllm:latest`, not an official vLLM image. Docker Hub shows the account holds only this image, registered September 18, with 846 pulls and no public Dockerfile. When a user asked for the Dockerfile in the discussion tab, a Yandex member replied that the image contains roughly the same branch as vLLM PR #57963. The command also uses `--pull=always`, so every start pulls whatever `latest` is at that moment. For production, wait for the PR to merge, or at least pin the image digest.
- The community GGUF and MLX versions all require running the authors' own llama.cpp patch or model.py. That is individual authors' code, unrelated to Yandex; review it before running.

## Which Inference Frameworks Can Run It?

As of 2026-09-24:

- Transformers: reference version 5.16.1, needs trust_remote_code; GPU also needs flash-linear-attention 0.5.0
- vLLM: native-support PR #57963 was opened by a Yandex engineer on September 21 and is open with a needs-rebase label; by its own description it does not support pipeline parallelism and MTP is limited to one layer. For now the only path is the third-party Docker image above
- SGLang: someone asked in the discussion tab; no answer
- llama.cpp / Ollama / LM Studio: no alice_ai architecture upstream. Two community GGUF repos exist, both stating they need a patched runtime
- MLX: no native support in upstream mlx-lm; two community quantizations ship their own model.py

By contrast, Qwen3-Next's qwen3next architecture has long been in upstream llama.cpp. Within its class, this is AliceAI's biggest practical weakness today.

## Can a Mac Run It, and How Much Memory Does It Need?



We did not download weights. The table combines file-size arithmetic with community authors' self-reported numbers:

| Version | Weight size | Source | Suitable Mac |
|---|---|---|---|
| Official bf16 | ~162.6GB | yandex | 192GB+ (e.g. a high-memory Mac Studio), and on Mac it takes the slow pure-PyTorch path; not recommended |
| Community GGUF Q8_0 | ~84.7GB | AMAImedia | 128GB; needs a patched runtime |
| Community GGUF Q4_K_M | 48.4GB (45.1GiB) | Yamada114514 | 64GB is tight, 96GB+ comfortable; needs patched llama.cpp |
| Community MLX 4-bit | ~44.9GB | Yamada114514 | 64GB is tight, 96GB+ comfortable |
| Community MLX mixed 2/4-bit | 28.29GiB | Hosstia | 48GB |
| 16GB / 24GB / 32GB Macs | — | — | No version fits |

KV-cache pressure is small, a benefit of hybrid attention: only 12 of 48 layers use full attention, each with 2 KV heads at head dimension 256, which works out in bf16 to about 24KB per token, about 3.2GB at 128K context and about 6.4GB at the full 262K. The 36 KDA layers keep a fixed-size recurrent state of about 75MB. Memory goes mostly to weights.

Community authors' self-reported numbers (all small smoke tests, not rigorous benchmarks):

- The Q4_K_M GGUF decodes at about 64–65 tokens/s on an M5 Max 128GB, with peak resident memory of 45.58GiB. The author also found that Metal's batched matrix kernels reduce activation precision: the first port's logits differed by 7.02% between prefill and token-by-token decoding, and only after the patch forced FP32 activations did they match bit for bit, at the cost of slower prefill.
- The MLX 4-bit port has a median decode of about 48 tokens/s on the same machine; another author says it swaps heavily on 48GB machines.
- The mixed 2/4-bit port compresses the expert layers, which hold 96.9% of all parameters, to 2-bit and keeps everything else at 4-bit. The author's own test: uniform 2-bit (23.26GiB) got only 1 of 5 simple questions right, answering "capital of France" with the Russian word "закон" (law); the mixed version got 5 of 5 and runs at full speed on an M4 Pro 48GB. Note that it was quantized 4-bit, dequantized, then re-quantized to 2-bit, so precision loss is larger than quantizing directly from bf16, and a 5-question test proves little.

Concrete advice for Mac users:

- 16–32GB: it will not run; do not download it. For local use in this tier you need a smaller model.
- 48GB: try the mixed 2/4-bit MLX port as a toy for Russian and English continuation; do not expect quality.
- 64GB: Q4 fits, but the OS and other apps compete, and long contexts will swap.
- 96GB and up: Q4 is comfortable. But if your goal is Chinese, the same memory is better spent on Qwen3-Next-80B-A3B Instruct: upstream llama.cpp and MLX support, chat ability, and far more efficient Chinese tokenization (about 37% fewer tokens for the same Chinese text).

## How Should You Choose Among Similar Models?

- For Chinese, chat and easy local deployment: Qwen3-Next-80B-A3B-Instruct / Thinking, or the newer Qwen3.5 series.
- For Russian content and Russia-specific knowledge such as law and education: AliceAI is among the best self-reported open-weight options, but Yandex wrote the tests, so validate on your own data.
- For a clean 80B-class Apache-2.0 base for post-training research: AliceAI is uniquely useful because the same-class Qwen3-Next has no public Base. It also ships two Russian factual evaluation datasets, WikiWebFacts and HardMultiQA, with their evaluation protocols.
- For an assistant you can use right away: skip Base models altogether.

As an aside, Yandex also open-sourced AliceAI-T5-35B-A0.6B on September 10 (its repo was created two days before this one); we did not verify it for this piece.

## Background: Yandex, Alice AI and YandexGPT

Alice (Russian: Алиса) is Yandex's voice-assistant brand. In May 2023 Yandex released YandexGPT and connected it to Alice. On October 28, 2025, at its "Alice, what's new?" event, Yandex launched Alice AI, backed by a new model family of Alice AI LLM, Alice AI VLM and Alice AI Art (according to Yandex's own press release). This open model carries the Alice AI brand.

Yandex's open-source history (from the yandex account's HuggingFace model list and related coverage):

- June 2022: YaLM-100B, a 100B dense model, Apache-2.0, trained on about 300B tokens
- February–March 2025: YandexGPT-5-Lite-8B pretrain and instruct, under a custom YandexGPT-5-Lite-8B License rather than a standard open-source license
- September 2026: AliceAI-T5-35B-A0.6B and the AliceAI-Foundation-80B-A3B-Base covered here, the latter under Apache-2.0

Moving from a custom license back to Apache-2.0 is good news for anyone who wants commercial use.

## FAQ

**Q: Is the license really Apache-2.0? Can I use it commercially?**
A: Yes. The repo's LICENSE file is the standard Apache-2.0 text with YANDEX LLC as copyright holder, and the model card and HF API both say apache-2.0. Commercial use is allowed, but the bundled NOTICES file asks users to comply with applicable export-control laws; companies should have legal review that clause.

**Q: Is it just a reskinned Qwen3-Next?**
A: The architecture skeleton largely follows Qwen3-Next, as Yandex itself says, but linear attention, residuals and routing were all swapped and the vocabulary differs, so it cannot be a simple fine-tune of Qwen weights. Whether the weights were fully trained from scratch cannot be verified from outside.

**Q: Is it usable for Chinese?**
A: It tokenizes and decodes Chinese losslessly with no unknown characters, but the same pure-Chinese text takes about 58% more tokens, most common characters are split into bytes, and the training-data description does not mention Chinese. Not recommended for Chinese.

**Q: Can a 16GB Mac run it?**
A: No. The smallest community version is 28.29GiB.

**Q: Does it work with Ollama or LM Studio?**
A: Not as of September 24. Upstream llama.cpp lacks the architecture, and community GGUFs require the authors' patched runtime.

## Primary Sources

- Model page: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base
- HF API: https://huggingface.co/api/models/yandex/AliceAI-Foundation-80B-A3B-Base
- English model card: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/README_en.md
- config.json: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/config.json
- LICENSE: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/LICENSE
- Remote code: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/blob/main/modeling_alice_ai.py
- Discussions: https://huggingface.co/yandex/AliceAI-Foundation-80B-A3B-Base/discussions
- Yandex press release: https://ir.yandex/press-releases?year=2026&id=2026-09-21
- Yandex Habr write-up (Russian): https://habr.com/ru/companies/yandex/articles/1083300/
- vLLM PR #57963: https://github.com/vllm-project/vllm/pull/57963
- Docker image: https://hub.docker.com/r/yamlbrand/alice-ai-vllm
- Qwen3-Next-80B-A3B-Instruct: https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct
- Community GGUF Q4_K_M: https://huggingface.co/Yamada114514/AliceAI-Foundation-80B-A3B-Base-GGUF
- Community GGUF full set: https://huggingface.co/AMAImedia/AliceAI-Foundation-80B-A3B-BF16-GGUF
- Community MLX 4-bit: https://huggingface.co/Yamada114514/AliceAI-Foundation-80B-A3B-Base-MLX-4bit
- Community MLX mixed 2/4-bit: https://huggingface.co/Hosstia/AliceAI-Foundation-80B-A3B-Base-MLX-2bit
- Alice AI launch (2025-10-28): https://yandex.com/company/news/2025-10-28-01
- YaLM-100B: https://github.com/yandex/YaLM-100B
- YandexGPT-5-Lite-8B-pretrain: https://huggingface.co/yandex/YandexGPT-5-Lite-8B-pretrain

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
