---
title: "Decision 3.0：让文字、图片和视频直接进入决策接口"
titleEn: "Decision 3.0: Multimodal Inputs, Typed Decisions"
description: "Decision 3.0 将文本、JSON、图片和视频接入 System One 决策接口，返回选项概率而不生成长回答。本文核对六个规格的官方模型卡与推理代码，区分请求与前向计算，更新 Jev 0.3.2 评测与 MI325X 延迟，并分析小模型的泛化边界、视频采样限制、服务吞吐和内存代价，给出业务验证的接入路径。"
descriptionEn: "Decision 3.0 scores typed questions about text, images and video. We audit its model sizes, updated Jev results, latency conditions and deployment tradeoffs."
wechatTitle: "Decision 3.0：多模态输入直接做判断"
wechatDigest: "六档模型返回选项概率，适合分类与路由，但一次请求并不等于一次前向。"
pubDate: "2026-10-14"
updatedDate: "2026-10-14"
category: "Tech-News"
tags: ["Decision 3.0", "vLLM Semantic Router", "System One", "多模态", "决策模型", "开源"]
heroImage: "../../assets/images/decision30-multimodal-system-one-banner.jpg"
---

Decision 3.0 是把文字、图片和视频转成选项概率的模型系列，适合业务分类与路由，省去生成长回答的步骤。

vLLM Semantic Router 团队的六档模型采用 Apache-2.0。我们按 2026 年 10 月 14 日官方模型卡与代码快照核对。模型合集已更新，早期素材中的 Jev 0.3.1 成绩和延迟，不能与当前表格混用。

ModelScope 合集：https://modelscope.cn/collections/vllm-sr/Decision-30
旗舰模型：https://huggingface.co/vllm-sr/d3
最小模型：https://huggingface.co/vllm-sr/d3-edge
项目仓库：https://github.com/vllm-project/semantic-router

## 不生成回答，具体怎样得到决策？

调用者提供 `state` 和一个或多个问题。问题可以要求单选 `choice`、是非判断 `noul`，或有序分级评分 `score`。图片和视频作为附加输入，同一请求里的问题都可以读取这些媒体。

当前代码把选项映射到单 token 答案码，读取提示末位置的隐藏表示，用一个 255 路读出层评分，再形成选项概率。它不运行普通聊天模型那种逐 token 回答循环，接口的 `output_tokens` 为 0。但输入文本和视觉内容仍要编码，也仍需计算前向传播。

![小M将文字、图片和视频证据分配为给定选项的概率，而不生成长回答](../../assets/images/decision30-multimodal-system-one-fig-01.png)

一次请求容纳多个问题，和一次前向解决全部问题，是两件事。官方 AutoModel 路径明确按问题分别前向；Engine 的 `batching` 配置可以合并执行来提高吞吐。多问题接口让业务编排更方便，不能据此宣称增加问题没有计算成本。

![小M拆开包含多个问题的请求信封，逐题驱动计算齿轮，增加问题仍耗算力](../../assets/images/decision30-multimodal-system-one-fig-02.png)

输出字段也有细节：单选返回选项及概率分布；`noul` 返回肯定答案的概率；`score` 返回各等级概率与等级索引的加权期望，可能是小数。代码里的 `confidence` 由归一化熵计算，不等于经过业务校准的“答对概率”。

## 六个规格怎样比较？

下面采用当前模型卡列出的实际参数，包含视觉编码器。不同页面的档位叫法或取整可能出现 0.8/0.9B、4/5B、8/9B；应按具体模型 ID 和权重版本识别。

| 模型 ID | 模型卡参数 | Jev 文本指数 0.3.2 | Jev 视觉指数 0.3.2 |
| --- | ---: | ---: | ---: |
| d3-edge | 0.59B | 20.2 | 31.7 |
| d3-lite | 0.85B | 32.3 | 42.1 |
| d3-nano | 2.21B | 38.9 | 54.7 |
| d3-mini | 4.54B | 52.6 | 63.2 |
| d3-flash | 8.39B | 55.8 | 66.9 |
| d3 | 26.09B | 66.3 | 71.3 |

这些是官方模型卡引用的榜单分数，不是本文独立复现，也不是所有业务的准确率。当前 d3 卡片中 Decision 2.0 同档的文本指数为 55.9；比较需固定指数版本、子集和模型配置。

d3-edge 的体积优势有明显能力代价：新领域任务分数为 12.9，d3 对应为 60.5。它可以优先用于窄而稳定的分类问题；真正选型应拿自己的任务做测试，不能只看家族最大模型的成绩，就推断最小版本也能胜任。

官方内部 Perception Test 验证集包含 19,140 道三选一视频题，d3 报告 top-1 准确率 77.4%，d3-edge 为 46.6%，随机机会水平约 33.3%。这和 Jev 文本或视觉指数是不同评测，不能拼成统一的“多模态准确率”。

本篇固定的旗舰卡片版本为 `fc2d74bd48ec29ae42d4330a543913f7858e3f40`，edge 为 `fe71f8e1dad1d0198386de78345b13f25c319b36`；其余四个快照也已保存。

## 文字、图片、视频分别适合什么任务？

文字或 JSON 可以表达工单、业务状态和结构化字段，一次请求问“归哪个部门”“有没有凭证”“紧急程度是哪档”。JSON 在提示构造中会序列化为文本，不意味着模型会替业务执行字段校验或数据库查询。

图片可以补充商品、收据、截图等视觉证据。例如根据收据判断支付方式，再结合描述做工单分类。官方支持多张图，每张图最多约 1.6MP；实际业务还应验证小字、模糊图和长票据是否影响判断。

视频默认按 2fps 采样，最多取 32 帧，长视频的采样会覆盖整个时间范围，并非读取每一帧。每帧最多约 0.2MP。它适合对短片做方向、颜色、简单事件判断；快速动作、细小变化或稀疏事件可能在采样中丢失。

这类模型给的是判断，而不是整个业务流程。退货部门选中了，不代表退货已执行；视频判断得到“向右”，也不代表拥有物体连续轨迹或实时控制系统。

## 毫秒延迟的测试条件是什么？

当前模型卡的 AutoModel 测试使用单张 AMD Instinct MI325X，一次处理一个请求，预热后统计 p50。下面都是作者测量，不能直接当作 Mac、CPU 或生产系统的端到端延迟。

| 模型 | 文本，1 个问题 | 图片，1 个问题 | 10 秒视频，1 个问题 |
| --- | ---: | ---: | ---: |
| d3-edge | 6.6ms | 58.6ms | 274ms |
| d3 | 54.4ms | 290ms | 500ms |

官方测试说明约 330 token 的工单文本、1,456×1,092 图片和 1080p 视频，先预热 3 次，再做最多 20 次计时。读入视频的时长、分辨率、采样和问题数量都会改变工作量；素材中的旧延迟应与其旧版本一起引用。

![小M调节视频采样孔并标记 MI325X 单请求预热条件，限定延迟与准确率的解读范围](../../assets/images/decision30-multimodal-system-one-fig-03.png)

吞吐也不是上述延迟的倒数。edge 的 Engine `batching` 在并发负载下报告 861 请求/秒，但单个文本请求的 p50 是 9.9ms，比 AutoModel 的 6.6ms 更高。官方同时披露该配置在公共集改变了 0.151% 的决策，多发生在接近的选项之间。

服务化还有内存成本：同一份 edge 报告中 AutoModel 单请求峰值为 5.2GiB，Engine `exact` 为 15.9GiB，`batching` 为 19.9GiB。一个 0.6B 模型的权重小，并不保证带缓存和并发的服务也只占很少内存。

## 我们在 Mac 上实际跑了哪些输入？

Mycelium Protocol 在隔离环境使用官方 d3-edge 包，固定上述 revision，在 CPU 上加载 BF16 权重；模型包完整校验通过。环境使用 PyTorch 2.14.0、Transformers 5.17.0 和匹配的视觉依赖，采用 PyTorch 参考实现，没有启用 AMD 优化内核。

我们完成了 3 次真实模型调用，共 6 个问题，三个请求的 `output_tokens` 均为 0。另有 6 个轻量契约检查通过，涵盖选项映射、肯定概率、评分期望、采样上限和无效评分输入；这些检查使用合成概率，不是模型准确率测试。

| 实际输入 | 模型返回 | 独立核对与边界 |
| --- | --- | --- |
| 损坏商品的英文工单，3 个问题 | `returns` 概率约 0.9985；有凭证概率约 0.9996 | 与输入文案一致，但紧急程度没有把 Today 排第一 |
| 官方收据图片，1 个问题 | `card` 概率约 0.9751 | 图片可见 Paid by card，判断与样例一致 |
| 官方 4 秒视频，2 个问题 | 向右概率约 0.7748；变色概率约 0.7617 | 样例源视频为 32 帧、8fps；首尾帧显示方块从左侧蓝色变为右侧绿色 |

工单明确提到今天换货，但 urgency 的等级期望仅为 0.754，最高概率在 Routine，Today 约为 20.4%。这提醒我们：接口跑通、部分样例判断合理，不等于所有业务判断都已经可靠。

这次没有测延迟、吞吐、Core ML 或 ANE，也没有运行完整 Jev 和 Perception Test。官方样例视频是 4 秒，不能拿它去复现性能表中的 10 秒视频请求。测试脚本、原始输出与采样检查已保存，可按相同输入重跑。

## 如何接入自己的分类流程？

官方 Python 路径需要模型包的自定义代码，并指定 Transformers 5.17.0 等依赖。先审阅代码，再固定 revision；不要按普通聊天模型加载后调用 `generate` 来期待相同决策接口。

```python
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "vllm-sr/d3-edge",
    revision="fe71f8e1dad1d0198386de78345b13f25c319b36",
    trust_remote_code=True,
)
result = model.system_one(
    state={"message": "商品损坏，客户请求换货", "receipt": True},
    questions={
        "route": {
            "type": "choice",
            "instructions": "应该交给哪个部门？",
            "criteria": {
                "returns": "退货、换货和损坏商品",
                "billing": "支付和发票",
                "technical": "安装与使用问题",
            },
        },
        "has_receipt": {"type": "noul", "instructions": "客户有凭证吗？"},
    },
)
print(result["answers"])
```

HTTP 服务使用 `/v1/systemone`。模型卡注明 Engine 与 Decision 3.0 目前属于开发通道；其中吞吐优化还可能新于已经发布的镜像。接入时应核对实际软件版本，而不只是复制模型名称。

Mac 用户已有官方 Core ML 转换和 FluidUse 演示路线，覆盖文字、截图及视频等场景。这是另一套部署实现，需要单独验证，不应拿 MI325X 的延迟替代本机测试。

官方 Apple Silicon 说明：https://vllm-semantic-router.netlify.app/blog/decision-3-0-on-apple-silicon/
相关开源实现：https://github.com/FluidInference/FluidUse

我们认为合适的起点是一个选项清晰、可人工验收的窄任务。保存真实样本，比较不同模型在相同问题和输入上的错误，再根据实测设计转人工或转大模型的规则。用明确的验收集选择模型，比追逐家族最大版本的榜单名次更可靠。

相关本地决策模型阅读：https://blog.mushroom.cv/blog/decision2-kai-06b-local-classification-gguf/

## 常见问题

### Decision 3.0 是否完全不计算 token？

不是。输入仍需分词和编码，选项也映射为答案码；它省去的是逐 token 生成长回答的过程。一次调用多个问题仍可能执行多个前向。

### 返回高概率就能自动执行业务吗？

不能仅凭高概率判断正确率。概率和熵置信度需要在自己的数据上验证，决策输出与退款、付款、设备控制等实际动作也应分别验收。

### 0.6B 的 edge 能替代 27B 版本吗？

要看任务。官方新领域与视觉成绩存在较大差距，edge 更适合经过验收的窄分类；需要泛化或复杂视觉理解时，应测试更大规格。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Decision 3.0 turns text, images and video into option probabilities for classification and routing, without generating long answers.

The six-model family from the vLLM Semantic Router team is Apache-2.0 licensed. We reviewed official cards and code snapshots on October 14, 2026. Current cards use Jev 0.3.2; earlier 0.3.1 scores and latency figures must keep their original context.

ModelScope collection: https://modelscope.cn/collections/vllm-sr/Decision-30
Flagship: https://huggingface.co/vllm-sr/d3
Smallest model: https://huggingface.co/vllm-sr/d3-edge
Repository: https://github.com/vllm-project/semantic-router

## How does it make decisions without generating answers?

Callers supply `state` and typed questions: `choice`, yes/no `noul`, or ordered `score`. Attached images and videos are available to every question in that request.

The current code maps options to single-token answer codes, reads the final prompt position's hidden representation, and scores a 255-way readout. The interface reports `output_tokens: 0`, but input tokenization, visual encoding and forward computation still happen.

![Xiao-M distributes text, image and video evidence into probabilities over supplied options without generating a long answer](../../assets/images/decision30-multimodal-system-one-fig-01.png)

Multiple questions per request do not imply one forward pass for the entire request. The official AutoModel path evaluates each question separately; Engine's `batching` profile can combine work to improve throughput. The API simplifies orchestration rather than making extra questions free.

![Xiao-M opens one request envelope and cranks separate computation gears for each question; additional questions still require compute](../../assets/images/decision30-multimodal-system-one-fig-02.png)

Choice answers include a selected option and distribution. `noul` returns the affirmative probability. `score` reports level probabilities and the expected level index, which can be fractional. `confidence` is based on normalized entropy, not a calibrated probability that the decision is correct.

## How do the six sizes compare?

These parameter counts are stated in current cards and include the vision encoder. Rounded size labels differ across pages; identify the actual checkpoint by model ID and revision.

| Model | Card parameter count | Jev text index 0.3.2 | Jev vision index 0.3.2 |
| --- | ---: | ---: | ---: |
| d3-edge | 0.59B | 20.2 | 31.7 |
| d3-lite | 0.85B | 32.3 | 42.1 |
| d3-nano | 2.21B | 38.9 | 54.7 |
| d3-mini | 4.54B | 52.6 | 63.2 |
| d3-flash | 8.39B | 55.8 | 66.9 |
| d3 | 26.09B | 66.3 | 71.3 |

These are leaderboard figures quoted by the official cards, not our reproduction or universal business accuracy. The current d3 card lists same-size Decision 2.0 at 55.9 on the text index. Comparisons need a fixed index version, subset and model configuration.

The small model has a clear capability tradeoff: edge scores 12.9 on new-domain tasks versus d3's 60.5. Start with narrow, stable categories and evaluate your own examples. Flagship results cannot establish what the smallest model will handle.

The internal Perception Test validation evaluation contains 19,140 three-option video questions. Reported top-1 accuracy is 77.4% for d3 and 46.6% for edge, against 33.3% chance. That measure differs from the text and vision indexes.

Pinned flagship revision: `fc2d74bd48ec29ae42d4330a543913f7858e3f40`; edge: `fe71f8e1dad1d0198386de78345b13f25c319b36`. The other four snapshots are also recorded.

## What tasks fit each input modality?

Text or JSON can describe tickets and structured state, with questions about department, receipt availability and urgency. JSON is serialized into prompt text; the model does not thereby execute schema validation or database queries for the business.

Images add evidence from products, receipts or screenshots. Multiple images are accepted, each up to roughly 1.6MP. Small print, blur and long documents still need validation on representative inputs.

Videos default to 2fps with at most 32 frames spread across the full duration, each up to about 0.2MP. Short-clip direction, color and simple event questions fit the interface. Fast actions, tiny changes and rare events can disappear between sampled frames.

A decision is not a completed workflow. Selecting the returns department does not execute a return; answering “right” does not supply continuous object tracking or a control system.

## What do the millisecond latency numbers measure?

Current AutoModel figures use one AMD Instinct MI325X, one request at a time, after warm-up. They are author measurements rather than our CPU, Mac or production end-to-end timings.

| Model | Text, one question | Image, one question | Ten-second video, one question |
| --- | ---: | ---: | ---: |
| d3-edge | 6.6ms | 58.6ms | 274ms |
| d3 | 54.4ms | 290ms | 500ms |

The documented workloads include about 330 text tokens, a 1,456×1,092 image and a 1080p clip. Three warm-up calls precede up to 20 timed calls. Input size, sampling and question count change the work; retain the version when quoting earlier timings.

![Xiao-M adjusts video sampling and tags MI325X single-request warm-up conditions to bound interpretations of latency and accuracy](../../assets/images/decision30-multimodal-system-one-fig-03.png)

Throughput is a different measurement. Edge's Engine `batching` profile reports 861 requests/s under load, but its single-text-request p50 is 9.9ms versus AutoModel's 6.6ms. The card also reports 0.151% changed decisions on the public suite, largely near ties.

Service memory differs from weight size: the edge report lists 5.2GiB peak for single-request AutoModel, 15.9GiB for Engine `exact`, and 19.9GiB for `batching`. A small checkpoint does not guarantee a small concurrent service.

## What did we actually run on a Mac?

Mycelium Protocol loaded the pinned official d3-edge package with BF16 weights on CPU in an isolated environment. Full package verification passed. The environment used PyTorch 2.14.0, Transformers 5.17.0 and matching visual dependencies, with PyTorch reference operations rather than AMD kernels.

Three actual model calls answered six questions, and all three reported zero output tokens. Six additional contract checks passed for option mapping, affirmative probability, expected score, video sampling bounds and invalid score input. Those checks use synthetic distributions, not model-accuracy measurements.

| Actual input | Returned result | Inspection and limitation |
| --- | --- | --- |
| English damaged-delivery ticket, three questions | returns probability about 0.9985; receipt probability about 0.9996 | Consistent with the input, but urgency did not rank Today first |
| Official receipt image, one question | card probability about 0.9751 | The visible receipt says Paid by card |
| Official four-second video, two questions | right probability about 0.7748; color-change probability about 0.7617 | The source contains 32 frames at 8fps; inspected first/last frames show a blue square on the left and a green square on the right |

Although the ticket requested replacement today, urgency's expected level was only 0.754. Routine had the highest probability and Today received about 20.4%. Successful execution and plausible sample decisions do not establish business reliability.

We measured neither latency nor throughput, and ran no Core ML, ANE or full Jev/Perception benchmark. The official example clip is four seconds, distinct from the performance table's ten-second workload. Scripts, raw results and inspection records are retained for rerunning these inputs.

## How should developers integrate it?

The Python route uses custom package code and dependencies including Transformers 5.17.0. Review that code and pin its revision. Loading a plain chat backbone and calling `generate` is not the same decision API.

```python
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "vllm-sr/d3-edge",
    revision="fe71f8e1dad1d0198386de78345b13f25c319b36",
    trust_remote_code=True,
)
result = model.system_one(
    state={"message": "Damaged delivery, replacement requested", "receipt": True},
    questions={
        "route": {
            "type": "choice",
            "instructions": "Which department should handle this?",
            "criteria": {
                "returns": "Refunds, replacements and damage",
                "billing": "Payments and invoices",
                "technical": "Setup and use",
            },
        },
        "has_receipt": {"type": "noul", "instructions": "Is a receipt available?"},
    },
)
print(result["answers"])
```

The HTTP route is `/v1/systemone`. The cards place Engine and Decision 3.0 in the development channel; benchmarked serving optimizations may be newer than published images. Verify the actual software build as well as the model ID.

Mac users have an official Core ML conversion and FluidUse demonstration path for text, screenshots and video. That is a separate implementation and needs separate validation; MI325X timings cannot stand in for local measurements.

Official Apple Silicon article: https://vllm-semantic-router.netlify.app/blog/decision-3-0-on-apple-silicon/
Implementation: https://github.com/FluidInference/FluidUse

Our recommendation is to start with one clearly defined, manually verifiable decision task. Save real examples, compare errors under identical inputs and questions, and use measured results to define escalation to a person or larger model. That is more useful than selecting a size solely from the flagship's rank.

Related local decision-model reading: https://blog.mushroom.cv/blog/decision2-kai-06b-local-classification-gguf/

## FAQ

### Does Decision 3.0 avoid all token computation?

No. Inputs are tokenized and encoded, and options map to answer codes. It removes long autoregressive answers. Multiple questions can still require multiple forwards.

### Does a high probability justify executing a business action?

Not by itself. Validate probabilities and entropy-derived confidence on your own data, and assess the decision separately from executing payments, refunds or device operations.

### Can edge replace the 27B model?

It depends on the task. Reported new-domain and visual results differ substantially. Edge suits validated narrow categories; broader or harder visual workloads need comparison with larger sizes.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
