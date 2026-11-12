---
title: "Rayline ARC 开源路由模型：成本数字、权重与部署边界"
titleEn: "Rayline ARC: Open Routing Weights and a Cost Audit"
description: "Rayline ARC 用小模型预测候选模型的任务成功率、Token 用量和思考深度，再结合价格与策略决定下一步路由。本文找到官方权重、vLLM 插件和 Raydock 仓库，核对混合部署的质量与成本口径，指出当前表格与标题数字的算术差异，并跑五项插件测试，解释权重开放、训练资料与完整自托管的边界与接入验证方法。"
descriptionEn: "Find ARC's official weights and code, audit hybrid benchmark arithmetic, and examine serving gaps, cache-aware routing, and five CPU tests with a vLLM stand-in."
wechatTitle: "Rayline ARC：开源路由与成本数字核查"
wechatDigest: "找到官方权重与仓库，核对混合部署指标、插件能力和完整自托管的距离。"
pubDate: "2026-11-12"
updatedDate: "2026-11-12"
category: "Tech-News"
tags: ["Rayline", "ARC", "模型路由", "开源模型", "成本优化"]
heroImage: "../../assets/images/rayline-arc-open-routing-model-cost-audit-banner.jpg"
---

Rayline ARC 是替 Agent 选择下一步模型与思考配置的小模型：先预测质量与用量，再按你的价格和偏好决定把任务交给谁。

官方权重已在 Hugging Face 发布，推理插件和接入网关也有公开仓库。但“开源模型”“完整服务可自托管”和“业务成本稳定降低九成”是三件分别需要核验的事。本次核对发现，公开插件尚未提供完整服务；当前模型卡中的六行质量数据，也不能按它注明的平均方式复算出标题的 97.5%。

## 原始权重和代码在哪里？

| 入口 | 实际提供什么 | 当前边界 |
|---|---|---|
| https://huggingface.co/rayline-ai/ARC-1.0 | 权重、配置、Tokenizer、问题头、策略预设、合成校验样例、发布记录 | 自定义架构；不是直接接普通文本生成接口就能用 |
| https://github.com/rayline-ai/vllm-arc | vLLM 编码器集成、Stage-1 预测头加载与评分 | WIP，尚不支持端到端服务和完整决策 API |
| https://github.com/rayline-ai/raydock | 本地网关、CLI、云端与本地模型的接入 | 不同模式的鉴权和路由方式不同 |

旧的 `rayline-ai/rayline` 地址现指向 Raydock。ARC 权重与上述代码采用 Apache-2.0；发布包同时保留上游 NOTICE，包括 Nemotron-PII 的 CC-BY-4.0 署名信息。模型卡明确说，整理后的训练语料和生产训练系统仍是专有的。因此，可以确认权重和相关代码开放，不能写成整套训练流程与数据完全公开。

“全球首个统一路由模型”属于发布方的定位，本次没有完成足以证明全球首创的系统性优先权核查。

## 为什么把预测和路由策略拆开？

ARC 的底座是 Qwen3.5-0.8B。模型卡描述的专用预测头读取冻结的前十二层；通用问题头使用完整二十四层，其中上十二层为决策问题微调。多个信号共享底座，而非每一种判断单独部署一个大模型。

它预测候选模型的成功概率，以及未缓存输入、缓存读取、缓存写入、输出等用量。价格由应用在运行时提供。在模型与服务配置不变的前提下，供应商改价不必重新训练这些预测器。

Sage 和 Swift 是同一模型的策略配置，主要区别是对成功价值的偏好：

```text
效用 = V × 预测成功概率 − 预计成本
Sage:  V = 4.5
Swift: V = 0.1
```

V 的含义是应用愿意为成功付出的价值；不是模型能力等级，也不是准确率。Prefer-local 则先看本地模型是否达到给定成功阈值，不满足再用后备策略。

![小M先读取成功率和用量预测，再用价格与策略选择模型](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-01.png)

这套拆分适合多轮 Agent：复杂规划可以交给强模型，简单整理可以交给便宜模型。但路由并不意味着每轮都换模型。换供应商可能损失缓存、改变上下文可用长度和工具行为；省下的单次输出费用，可能被新的输入开销抵消。

## “97.5% 性能、十分之一成本”究竟指什么？

当前模型卡把这组结果归于六个基准上的混合 edge–cloud 配置：DeepSeek V4.1 Flash 在多台 NVIDIA DGX Spark 上本地服务，prefer-local 阈值为 0.85，后备策略 V=4.5。作者报告保留 Opus 5.5 的 97.5% 质量，推理成本为 7.1%，即降低 92.9%。

这是特定模型池、任务集、价格与部署下的作者结果，不是任意 Agent 都能拿到的固定折扣。产品首页还给出了不同模式的另一组数字，不能把云端路由与本地混合配置的数据拼成同一次实验。

“质量保留”也不是所有任务绝对成功率达到 97.5%。例如模型卡的混合配置表中，Tau3 Banking 从基线 42.8% 降至 35.3%，相差 7.5 个百分点。平均表现可能掩盖某一业务域的退步。

### 我们重算后发现了什么？

本次固定模型卡 revision 为 `9dd93e765b09440804908b2af302d3db9677fb39`，按其 prefer-local 表格计算：

| 基准 | Opus 成功率 | 混合路由成功率 | 路由成本 / 基线 |
|---|---:|---:|---:|
| DeepSWE | 69.9% | 72.3% | 1.1% |
| Terminal-Bench 2.1 | 90.7% | 90.5% | 75.7% |
| SWE-Atlas QA | 61.6% | 62.6% | 1.6% |
| Tau3 Banking | 42.8% | 35.3% | 17.3% |
| GPQA Diamond | 89.5% | 92.5% | 12.3% |
| MMMU-Pro Vision | 82.2% | 82.7% | 40.9% |

模型卡说，质量是各基准比值的平均。直接计算 `mean(路由成功率 / 基线成功率)` 得到约 98.55%，并非标题的 97.5%。目前没有取得可以消除该差异的底层汇总说明；可能涉及统计版本或其他未展示口径，但我们不能代作者补出解释。

六个成本比例的简单平均约为 24.82%，也不能用来否定或证明作者的 7.1%：模型卡注明成本是匹配任务支出的汇总比例，需要各组绝对支出和任务数量才能复算。文章资料中保留了六行输入、计算脚本和结果，这次验证是算术核查，没有重新跑六套基准。

![小M分别核算质量比平均与支出汇总，标出不能混用的两种口径](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-02.png)

同样，低推理支出不等于已经证明低总拥有成本或低能耗。硬件利用率、设备成本和实际耗电仍需另行计量；本文没有独立复现这些项目。

## 权重已开放，为什么仍不能直接完整自托管？

ARC 使用自定义 `ArcImagePolicyForPooling` 架构，普通 stock vLLM 无法直接加载完整能力。公开插件 README 给出特定 vLLM nightly 加 fork overlay 的安装路径，测试环境是 Linux、CUDA 13.0、Python 3.12。

插件已提供编码器注册和 Stage-1 头，但明确未包含完整决策/策略 API、Stage 2、面向调用方的问题头与内容信号接口。模型权重里存在某个预测头，不等于当前公开服务代码已经把它暴露成可调用 API。

因此，不应给读者一条看似简单的 `vllm serve`，再声称能得到完整 ARC。可用的托管接口与尚在完善的开源服务路径，要分别选择、分别评估。

Raydock 也有容易混淆的模式：`--local` 使用本地静态路由，不需要托管鉴权；`hybrid` 模式则连接 ARC 决策，即使生成任务交给本地模型，仍可能产生托管决策费用。接入前要看实际模式，不能仅从“本地网关”推断所有流量与费用都留在本地。

![小M检查权重、预测头、决策 API 和接入网关之间尚未接齐的部分](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-03.png)

## 我们实际运行了哪些测试？

Mycelium Protocol 固定了公开插件快照，在 CPU 环境运行其上游测试：五项通过。测试用 stand-in vLLM 验证插件架构注册、图像配置约束、加载时跳过预测头，以及每张图像执行一次 float32 视觉路径等行为。

这不是加载 ARC 权重后的推理测试，也没有验证 CUDA fork 的数值一致性、真实路由质量、托管接口或任何节费基准。本次没有安装系统代理证书、改动 Agent 的全局配置或调用付费生成服务。

工程上可以按三个阶段推进：先复核发布包、NOTICE 和插件能力；再用自己有标签的小任务集，对照固定强模型与路由策略；最后接入多轮任务，记录每个路由点的预测、实际成功、输入输出用量、缓存、失败重试与总费用。

应先固定模型池和任务集，再比较 Sage、Swift 与自定义 V。需要“本地优先”时，还要把机器吞吐、并发与利用率纳入同一统计。只看单次 token 单价，很容易优化了账面价格，却增加整段任务的成本。

## 常见问题

### ARC 是替代 Opus 的聊天模型吗？

它主要输出路由相关信号，替下一步选择模型和思考设置；最终文本仍由被选中的模型生成。

### 免费下载权重，是否等于能免费获得完整托管服务？

不是。托管决策、下游模型与本地设备各有成本，公开插件的完整服务能力也尚未齐备。

### 97.5% 和 7.1% 是否已被本文复现？

没有。本文重算了展示数据，发现质量平均与标题有差异；汇总成本还缺绝对支出和样本信息，不能仅凭六个百分比复算。

一手入口：权重与模型卡 https://huggingface.co/rayline-ai/ARC-1.0 ；推理插件 https://github.com/rayline-ai/vllm-arc ；网关 https://github.com/rayline-ai/raydock ；技术报告 https://static.rayline.ai/rayline/reports/arc/latest 。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Rayline ARC predicts which model and reasoning configuration should handle an agent's next step. Applications combine its success and usage predictions with their own prices and policies.

Official weights are available, together with a serving plugin and a gateway. These releases do not establish a complete self-hosted service or a guaranteed reduction in business spending. Our arithmetic audit also found that the current displayed quality table does not reproduce its headline aggregate.

## Where are the official releases?

- Weights and release artifacts: https://huggingface.co/rayline-ai/ARC-1.0
- Encoder integration and Stage-1 scoring: https://github.com/rayline-ai/vllm-arc
- Local/cloud agent gateway: https://github.com/rayline-ai/raydock

The older rayline repository redirects to Raydock. ARC and these code projects use Apache-2.0, with upstream notices including CC-BY-4.0 Nemotron-PII attribution. The model card states that the curated training corpus and production training system remain proprietary. We did not establish the worldwide priority implied by the promotional “first” claim.

## Why separate predictions from policy?

ARC is derived from Qwen3.5-0.8B. Specialized heads read the frozen lower twelve layers; the question head uses all twenty-four layers, with the upper twelve fine-tuned for decision questions.

The model predicts success and usage components, including uncached input, cache reads, cache writes, and output. Prices are application inputs. Changing rates does not require retraining those predictors while the model and serving configuration remain fixed.

Sage and Swift are configurations of the same router. They choose by utility, V times predicted success minus expected cost, with V=4.5 and V=0.1 respectively. Prefer-local first checks a local success threshold and then applies a fallback policy. V is a value preference, not an accuracy score.

![Little M combines success and usage predictions with prices and routing policy](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-01.png)

Switching models every turn is not the goal. A cheaper generator can lose its advantage through cache misses, context limitations, or different tool behavior. Evaluate whole tasks rather than isolated output-token prices.

## What does the cost headline actually measure?

The reported hybrid setup uses DeepSeek V4.1 Flash across multiple NVIDIA DGX Spark systems, a prefer-local threshold of 0.85, and fallback V=4.5. The authors report 97.5% of Opus 5.5 quality at 7.1% of its inference cost. The product homepage also presents a different cloud-routing configuration; these figures should not be mixed.

Relative retained quality does not mean every task has 97.5% absolute success. The displayed hybrid table includes a Tau3 Banking reduction from 42.8% to 35.3%, a 7.5 percentage-point drop.

### What happened when we recalculated the table?

We pinned model-card revision 9dd93e765b09440804908b2af302d3db9677fb39. Its six baseline/routed pairs are 69.9/72.3, 90.7/90.5, 61.6/62.6, 42.8/35.3, 89.5/92.5, and 82.2/82.7 percent.

The card describes quality as the average of per-benchmark ratios. Applying that definition to these displayed values gives approximately 98.55%, rather than 97.5%. We do not have underlying aggregate records that reconcile the difference. A different version or undisclosed aggregation detail is possible, but we cannot invent that explanation.

The six displayed cost ratios are 1.1%, 75.7%, 1.6%, 17.3%, 12.3%, and 40.9%. Their simple mean is 24.82%, which neither proves nor disproves the reported 7.1% pooled spending ratio. Reconstructing the latter requires absolute spending and matched task counts. Our evidence bundle contains the inputs and arithmetic script; we did not rerun the benchmarks.

![Little M separates mean quality ratios from pooled spending calculations](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-02.png)

Lower reported inference spending is also not an independently measured ownership-cost or energy reduction. Utilization, hardware costs, and power consumption require their own accounting.

## Why are open weights not yet a complete self-hosted service?

ARC uses a custom ArcImagePolicyForPooling architecture. Stock vLLM does not load its complete functionality directly. The plugin documents a pinned nightly plus a fork overlay, tested on Linux with CUDA 13.0 and Python 3.12.

Its public implementation supplies encoder integration and Stage-1 scoring. End-to-end serving, Stage 2, the decision/policy API, and caller-facing question/content-signal interfaces are still missing. A head's presence in a weight file does not imply that an operational public API for it is included.

Raydock has distinct modes too. Local mode uses static on-device routing without hosted authentication. Hybrid mode connects to ARC decisions and can charge for hosted decisions even when generation runs locally. A local gateway does not imply a fully offline or unbilled pipeline.

![Little M checks the gaps between weights, heads, decision APIs, and the gateway](../../assets/images/rayline-arc-open-routing-model-cost-audit-fig-03.png)

## What did our tests verify?

Mycelium Protocol ran the plugin's upstream CPU tests at a pinned commit: five passed. The suite uses a stand-in for vLLM to check architecture registration, image-engine constraints, skipped head weights, and one float32 visual call per image.

This did not run ARC weights, establish CUDA-fork parity, measure real routing quality, or reproduce savings. We did not install proxy certificates, change global agent settings, or call paid generation providers.

A practical rollout should first validate artifacts and supported interfaces, then compare policies on a labeled task set with a fixed model pool, and finally record full multi-turn success, usage, cache behavior, retries, and total spending. Local-first deployment also needs utilization and concurrency measurements.

## FAQ

### Is ARC a chat-model replacement for Opus?

It primarily supplies routing signals. The selected downstream model still generates the response.

### Do downloadable weights make the hosted service free?

No. Hosted decisions, generators, and local hardware have separate costs, while the public serving plugin is still incomplete.

### Did this article reproduce the headline figures?

No. The displayed quality table produced a different macro ratio, and pooled cost reconstruction needs absolute spending records unavailable here.

Sources: https://huggingface.co/rayline-ai/ARC-1.0 ; https://github.com/rayline-ai/vllm-arc ; https://github.com/rayline-ai/raydock ; https://static.rayline.ai/rayline/reports/arc/latest .

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
