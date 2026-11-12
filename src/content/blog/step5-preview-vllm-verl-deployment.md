---
title: "Step-5 Preview 部署指南：vLLM 专用镜像与 verl RL 边界"
titleEn: "Step-5 Preview: vLLM Serving and verl RL Guide"
description: "Step-5 Preview 已提供 vLLM 专用镜像与部署配方，FP8 示例采用四张 B300 或八张 H200。本文核对模型页、镜像与 verl 强化学习 PR，解释 TP、EP、DP、长上下文与 NVFP4 的配置差异，给出接口验收步骤，并区分可下载权重、定制推理环境与仍处于草稿阶段的 LoRA 强化学习实现。"
descriptionEn: "Deploy Step-5 Preview with its dedicated vLLM image, compare GPU layouts and NVFP4, and understand the draft verl LoRA RL recipe and its reported results."
wechatTitle: "Step-5 Preview：部署与RL进展"
wechatDigest: "核对专用镜像、服务器配置和草稿阶段的强化学习实现，附接口验收方法。"
pubDate: "2026-10-15"
updatedDate: "2026-10-15"
category: "Tech-News"
tags: ["Step-5 Preview", "vLLM", "verl", "MoE", "模型部署", "强化学习"]
heroImage: "../../assets/images/step5-preview-vllm-verl-deployment-banner.jpg"
---

Step-5 Preview 已有专用 vLLM 镜像和服务器部署配方；verl 的强化学习适配目前仍是待合并的草稿 PR。想用它提供 API，可以沿推理配方验证；想训练 LoRA，还需要另一套定制依赖与多节点环境。

你提供的链接被换行截断了，完整入口是：

- vLLM 配方：https://recipes.vllm.ai/stepfun-ai/Step-5-Preview
- Docker 标签：`vllm/vllm-openai:step-5-preview`
- verl 实现：https://github.com/verl-project/verl/pull/8246
- 官方 FP8 权重：https://huggingface.co/stepfun-ai/Step-5-Preview
- 官方 NVFP4 权重：https://huggingface.co/stepfun-ai/Step-5-Preview-NVFP4

本文以 2026 年 10 月 15 日抓取的官方模型卡、vLLM Recipes 源文件与 PR 为依据。专用镜像存在，不代表通用发行版已包含全部能力；PR 的实验结果也不等于框架已经正式支持。

## Step-5 Preview 是多大的模型？

官方模型卡描述为约 600B 总参数、每 token 激活约 27B 的稀疏 MoE；vLLM 配方按 checkpoint 张量形状计数标为约 604B。两者统计口径不同，部署时应看实际 checkpoint 与显存规划。

27B 激活参数主要描述计算路径，不能据此按一个 27B 稠密模型估算权重占用。未在某个 token 上激活的专家仍需被部署系统保存或分布到设备，长上下文还要另外容纳 KV cache。

![小M把专家权重块分配到四张加速卡，并为 KV cache 留出独立空间，提醒激活参数不等于全部权重](../../assets/images/step5-preview-vllm-verl-deployment-fig-01.png)

官方资料介绍混合稀疏／滑动窗口注意力与多 token 预测（MTP）。配方给出的上下文上限为 1,048,576 tokens，包含输入与输出；“支持 1M”不意味着可以同时开满上下文、并发和输出长度。

模型介绍还涉及图像和视频能力，但本文只提供文本服务与文本 RL 的验证路径；下面的 curl 请求不能作为多模态接入已经验收的证据。

## 应该选择哪种硬件与并行方式？

| 配方路径 | 官方示例硬件 | 配置重点 |
| --- | --- | --- |
| FP8 | 单节点 4×B300 | TP4、TEP4 或 DEP4 |
| FP8 | 单节点 8×H200 | 对应 TP8、TEP8 或 DEP8，去掉 Blackwell 的 MegaMoE 参数 |
| NVFP4 | 单节点 4×B300 | 切换专用 checkpoint，示例上下文改为 320000 |
| verl LoRA RL | 作者报告 4 节点×4 张 GB300 | FSDP2 训练、两组 TP8 vLLM rollout、专门的 Step5 支持 |

TP 是把张量计算分片；EP 分布专家；DP 是多组数据并行处理。TEP 组合 TP 与 EP；DEP 示例使用 TP=1、DP=4，再启用 EP。这些布局要整体选择，不能把几行启动参数随意叠加。

B300 上 TEP/DEP 使用 `deep_gemm_mega_moe`；纯 TP 配方不选择它，因为该后端需要专家并行。`--max-num-seqs` 按 DP rank 生效，所以 DEP4 的 64 与 TP4 的 64，不能直接当作同一全局并发预算。

NVFP4 checkpoint 含 NVFP4 和 BF16 层，由配置检测量化方式。官方配方把它的示例上下文设为 320000；不能只替换模型名，就承诺完整 1M 上下文能以同样并发运行。这里没有跨精度质量与速度实测，因而不作性能排名。

## 如何启动一个可检查的文本 API？

先准备 Linux NVIDIA GPU 主机、可用驱动与容器 GPU 支持，并确认指定卡型、互联和存储容量。以下按官方 4×B300 FP8 的 TP4 示例整理；本文没有实际启动该服务器。

```bash
docker pull vllm/vllm-openai:step-5-preview

docker run --rm -it \
  --gpus all --ipc=host --network=host \
  --volume "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  --entrypoint /bin/bash \
  vllm/vllm-openai:step-5-preview
```

进入容器后，确认权重访问权限，执行：

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
vllm serve stepfun-ai/Step-5-Preview \
  --host 127.0.0.1 --port 18000 --served-model-name step5 \
  --tensor-parallel-size 4 \
  --data-parallel-backend mp --distributed-executor-backend mp \
  --disable-custom-all-reduce \
  --max-model-len 1048576 --max-num-batched-tokens 16384 \
  --max-num-seqs 64 --gpu-memory-utilization 0.85 \
  --enable-prefix-caching --spec-method mtp --spec-tokens 3 \
  --reasoning-parser step5 \
  --enable-auto-tool-choice --tool-call-parser step5
```

这保留模型卡的计算参数，监听地址改为本机以便先验收。将服务提供给其他机器时，应按自己的认证与网络方案配置入口。显存不足先降低 `--max-model-len` 或并发，不能把示例参数当作适用于所有负载的最佳值。

```bash
curl -fsS http://127.0.0.1:18000/v1/models
curl -N http://127.0.0.1:18000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  --data '{"model":"step5","messages":[{"role":"user","content":"Hello!"}],"max_tokens":4096,"stream":true}'
```

注意端口和模型名：这里显式设置 `18000` 与 `step5`，因此请求也要对应。Recipes 通用请求示例则使用 `8000` 和完整仓库名；混用两套示例会产生连接或模型名错误。

验收应依次覆盖短文本、流式结束、reasoning 字段解析、一个无副作用的工具调用，再逐步增加输入长度与并发。启用了 parser 只是配置成立；工具名、参数 JSON 和客户端实际调用仍需端到端验证。MTP 的三个候选 token 也不等于三倍吞吐，收益取决于接受率和硬件负载。

建议保存模型 revision、容器 digest、驱动版本、启动命令与首个成功请求。本文核对 Docker Hub 标签时取得摘要 `sha256:8bc189bb3f57183bcaf4f01405b29d4d92d782a182b384aac79b4b2885fb1fda`；标签可以更新，复现时应重新核对并固定摘要。

![小M匹配 step-5-preview 容器镜像、18000 启动端口与 step5 请求模型，核对成功回执后再继续](../../assets/images/step5-preview-vllm-verl-deployment-fig-02.png)

## verl #8246 已经能直接安装使用了吗？

截至核验时，PR 为 **open、Draft、未合并**，head 为 `136e22c7d02683d90c48a8ff76d1292de43ff394`。作者说明，上游通用 vLLM 当时尚不能服务 Step5；rollout 需要独立提交中的模型支持、融合注意力与 sparse-indexer 的 LoRA 服务，以及避免 sleep/wake 主机内存持续增长的备份处理。

因此，推理镜像能运行，不足以证明它同时满足此 PR 的训练依赖。不要只 `pip install verl` 后就执行脚本，也不要把草稿分支描述成已发布版本。

适配路径是文本模型上的 FP8 checkpoint、FSDP2、GRPO 与 LoRA。训练器从权重构建所需精度的投影，训练和同步 adapter；R3 记录 rollout 的专家路由，并在训练侧重放，以减少两侧路径不一致。它不是对全部 600B 参数进行全量训练，也没有在该实验中验证视觉 RL。

入口脚本为 `examples/grpo_trainer/run_step5_preview_dapo_lora_fsdp.sh`。需要 Ray 集群、各节点可访问的模型、DAPO-Math-17K 与 AIME-2024 的 Parquet 文件，以及匹配的 vLLM 和 Python 依赖。作者配置 LoRA rank 32、alpha 64、学习率 1e-5、4096-token 响应预算。

固定源码：https://github.com/aoshen02/verl/tree/136e22c7d02683d90c48a8ff76d1292de43ff394

## 怎样读懂作者报告的 RL 提升？

作者报告在 16 张 GB300 上运行 194 步，并经历两次从 LoRA checkpoint 恢复；AIME-2024 mean@8 从 step 0 的 0.375 到 step 190 的 0.658。这里的限定条件是 **4096-token 预算下的正确率**。

起点只有 40% 的答案在预算内完成，step 190 提升至 75%；已经完成的答案正确率则由约 94% 变为约 88%，且完成题目集合变大、难度构成变化。两组条件准确率不是同一子集，不能直接推断模型退化；整体分数提升也不能直接概括为一般数学能力同比增长。

更准确的理解是，这次训练让更多答案在指定预算内完成并被判对。作者称平均每训练步约 13 分钟、一次 AIME 验证约 4 分钟；这些是该集群与配置的报告，不能用于估算单卡成本。

![小M对齐两把相同的 4096-token 预算尺，对比之前较多未完成解答与之后较多完成解答，RL 实验旁标有草稿旗帜](../../assets/images/step5-preview-vllm-verl-deployment-fig-03.png)

PR 还报告 131 项测试通过、5 项跳过，但同时说明测试未随 PR 提交。本文没有独立取得并重跑那套测试。示例脚本的数据洗牌方式也与参考实验不同，复现前需要按脚本注释准备相同数据顺序。

## 常见问题与本文核验范围

### 是 Apache 2.0 模型吗？

不是。官方权重使用自定义 StepFun Model License 1.0，HF 标记为 `other`。框架许可不能代替模型许可；商业部署应阅读对应版本全文与适用条件。

许可：https://huggingface.co/stepfun-ai/Step-5-Preview/blob/main/LICENSE.txt

### 有 Apple Silicon 或普通单卡配方吗？

本文核对的官方 Recipes 路径是大型 NVIDIA 服务器配置，不是 Mac 部署指南。27B 激活参数不意味着只需装下 27B 权重。

### 本文做了哪些验证？

我们抓取全文，对照 Recipes YAML、模型卡、模型配置、Docker Hub tag 元数据与 PR API，并静态检查启动参数及脚本。没有下载数百 B 权重、启动 GPU 容器、运行推理或复现 RL；硬件与成绩均标明来源。

可结合这篇文章理解预算受限的决策系统，但不能把不同任务指标相互排名：https://blog.mushroom.cv/blog/decision30-multimodal-system-one/

源版本：Recipes `2f6a61c1d2d7f25e4224d3e0b8dd5c1478e7b556`；FP8 模型 `364b3b03fed2477aa0953fe855a2c4c8c48ee3cc`。原材料中的组织首页已补全为具体配方与 PR，避免读者落到不相关页面。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Step-5 Preview has a dedicated vLLM container and server recipes. Its verl reinforcement-learning integration remains an unmerged draft PR. Serving an API and training LoRA therefore require separate dependency checks.

The normalized source URLs are:

- Recipe: https://recipes.vllm.ai/stepfun-ai/Step-5-Preview
- Image: `vllm/vllm-openai:step-5-preview`
- RL PR: https://github.com/verl-project/verl/pull/8246
- FP8: https://huggingface.co/stepfun-ai/Step-5-Preview
- NVFP4: https://huggingface.co/stepfun-ai/Step-5-Preview-NVFP4

This review cross-checks official sources captured on October 15, 2026. An available dedicated image does not establish feature parity with a generic release, and PR experiments do not establish merged framework support.

## How large is Step-5 Preview?

The official model card describes roughly 600B total parameters and 27B active parameters per token. Recipes labels it approximately 604B based on checkpoint tensor shapes. The active count describes computation, while the deployment still has to store or distribute the experts and allocate KV cache.

![Xiao-M distributes expert weight blocks across four accelerator cards while reserving separate KV-cache space, showing that active parameters do not represent all stored weights](../../assets/images/step5-preview-vllm-verl-deployment-fig-01.png)

The model uses hybrid sparse/sliding-window attention and MTP. The recipe specifies 1,048,576 context tokens including input and output. Full context, maximum concurrency and maximum output cannot be assumed to fit together.

Official material also discusses image and video capabilities. The examples here validate a text-serving path and discuss text RL; a successful text request does not validate multimodal integration.

## Which hardware and parallel layout should you choose?

| Path | Official example | Key details |
| --- | --- | --- |
| FP8 | 4×B300 in one node | TP4, TEP4 or DEP4 |
| FP8 | 8×H200 in one node | TP8, TEP8 or DEP8; omit Blackwell MegaMoE settings |
| NVFP4 | 4×B300 in one node | Separate checkpoint; example context320000 |
| verl LoRA RL | Author reports 4 nodes×4 GB300 | FSDP2 trainer, two TP8 rollout engines and custom Step5 support |

TP shards tensor computation; EP distributes experts; DP supplies data-parallel ranks. TEP combines TP and EP. DEP4 uses TP1, DP4 and expert parallelism. These are alternative layouts, not a set of independent switches to combine arbitrarily.

Blackwell TEP/DEP uses `deep_gemm_mega_moe`. Pure TP leaves backend selection to the default because MegaMoE requires expert parallelism. Sequence limits apply per DP rank, which changes the interpretation of concurrency across layouts.

The NVFP4 checkpoint contains NVFP4 and BF16 layers. Its recipe uses a 320000-token context. Switching checkpoints alone does not prove that full 1M context and identical concurrency will fit. We provide no cross-precision performance or quality ranking.

## How can you bring up a checkable text API?

Prepare a Linux NVIDIA server with a working driver, container GPU support and the appropriate GPU layout. The following follows the official FP8 TP4 B300 example; we did not execute it on a GPU server.

```bash
docker pull vllm/vllm-openai:step-5-preview
docker run --rm -it \
  --gpus all --ipc=host --network=host \
  --volume "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  --entrypoint /bin/bash \
  vllm/vllm-openai:step-5-preview
```

Inside the container, ensure checkpoint access, then run:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
vllm serve stepfun-ai/Step-5-Preview \
  --host 127.0.0.1 --port 18000 --served-model-name step5 \
  --tensor-parallel-size 4 \
  --data-parallel-backend mp --distributed-executor-backend mp \
  --disable-custom-all-reduce \
  --max-model-len 1048576 --max-num-batched-tokens 16384 \
  --max-num-seqs 64 --gpu-memory-utilization 0.85 \
  --enable-prefix-caching --spec-method mtp --spec-tokens 3 \
  --reasoning-parser step5 \
  --enable-auto-tool-choice --tool-call-parser step5
```

The compute arguments follow the model card; we change the bind address to loopback for initial acceptance. Configure an authenticated network entry point when serving other machines. Reduce context or concurrency when memory is insufficient.

```bash
curl -fsS http://127.0.0.1:18000/v1/models
curl -N http://127.0.0.1:18000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  --data '{"model":"step5","messages":[{"role":"user","content":"Hello!"}],"max_tokens":4096,"stream":true}'
```

Use the matching port and model alias. The generic Recipes request instead uses port 8000 and the full checkpoint name; mixing conventions creates avoidable failures.

Check short text, stream completion, reasoning parsing and a harmless tool call before increasing length and load. Parser flags do not prove client integration. Three speculative MTP tokens do not guarantee triple throughput: acceptance rate and hardware utilization matter.

Save the model revision, image digest, driver, command and successful request. Docker Hub returned `sha256:8bc189bb3f57183bcaf4f01405b29d4d92d782a182b384aac79b4b2885fb1fda` for the tag during this review. Tags can move; verify and pin a digest for reproduction.

![Xiao-M matches the step-5-preview container image, startup port 18000 and request model step5, then checks a successful receipt before advancing](../../assets/images/step5-preview-vllm-verl-deployment-fig-02.png)

## Is verl #8246 ready in a normal release?

At verification, the PR was open, draft and unmerged, at head `136e22c7d02683d90c48a8ff76d1292de43ff394`. Its author says generic upstream vLLM did not yet serve Step5 and describes separately upstreamed support for the model, LoRA on fused attention/indexer projections, and host backups that avoid repeated sleep/wake memory growth.

A working serving image alone does not prove these training dependencies are present. Installing a generic verl release is insufficient evidence that the example will run.

The path uses a verl-native text model, FSDP2, GRPO and LoRA over an FP8 checkpoint. It trains and synchronizes adapters. R3 records expert routing during rollout and replays it during training. This is neither full-parameter 600B training nor demonstrated visual RL.

The entry point is `examples/grpo_trainer/run_step5_preview_dapo_lora_fsdp.sh`. It needs a Ray cluster, model access on every node, DAPO-Math-17K/AIME-2024 Parquet files and matching dependencies. The example uses rank 32, alpha 64, a 1e-5 learning rate and 4096-token responses.

Pinned source: https://github.com/aoshen02/verl/tree/136e22c7d02683d90c48a8ff76d1292de43ff394

## What do the reported RL results establish?

The author reports 194 steps on 16 GB300 GPUs, with two resumptions from LoRA checkpoints. AIME-2024 mean@8 rises from 0.375 at step 0 to 0.658 at step 190, under a 4096-token response budget.

Only 40% of initial answers finished within budget, rising to 75%. Accuracy among finished answers changes from roughly 94% to 88%, over a larger and differently composed set. Those conditional scores do not isolate regression; the overall improvement also should not be presented as a general reasoning gain of the same proportion.

The supported interpretation is that more answers finish and score correctly within the specified budget. The reported roughly 13 minutes per step and 4 minutes per validation are specific to that cluster. They are not single-GPU cost estimates.

![Xiao-M aligns two identical 4096-token budget rulers, comparing more unfinished solutions earlier with more completed solutions later, beside an RL experiment flag marked draft in Chinese](../../assets/images/step5-preview-vllm-verl-deployment-fig-03.png)

The author reports 131 tests passing and 5 skipped, while explicitly noting those tests are not included in the PR. We did not obtain and rerun them. The shipped example also shuffles data differently from the reference run; follow its comments before claiming reproduction.

## FAQ and verification scope

### Is the model Apache 2.0?

No. The official weights use StepFun Model License 1.0; Hugging Face marks it as `other`. Framework licenses do not replace the checkpoint license. Read the versioned terms for the intended deployment.

License: https://huggingface.co/stepfun-ai/Step-5-Preview/blob/main/LICENSE.txt

### Is there a Mac or ordinary single-GPU recipe here?

The verified source describes large NVIDIA server deployments. The 27B active parameter count does not mean only 27B parameters need storage.

### What did we actually verify?

We fetched full source text and cross-checked Recipes YAML, the model card/configuration, Docker Hub metadata and the PR API, with static command/script checks. We did not download the full weights, start a GPU container, run inference or reproduce RL.

Related reading on budget-constrained decisions, not a comparable benchmark: https://blog.mushroom.cv/blog/decision30-multimodal-system-one/

Source pins: Recipes `2f6a61c1d2d7f25e4224d3e0b8dd5c1478e7b556`; FP8 model `364b3b03fed2477aa0953fe855a2c4c8c48ee3cc`.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
