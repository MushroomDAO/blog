from pathlib import Path
import json,shutil
slug='axion-agent-training-data-cost-review';out=Path('source/20261109-axion')
cn='''Axion 1.0 把训练 Agent 的重点放在可验证任务与完整解题轨迹上：先练推理，再练检索，最后用强化学习改进工具交互。它值得学习的，是如何制造有学习信号的数据，以及怎样把训练、工具和评测接成一条链。

但原始素材里的几个结论需要拆开看。约 1K GPU-hours 是项目主页的作者口径；论文的 122B 成绩、公开的 35B 社区复现权重，以及“商用级”可靠性，是三个不同层次的证据。本文核对论文 v2、仓库代码、数据卡和模型卡，并做了本地代码检查，没有重跑模型训练或榜单。

## Axion 1.0 是什么，开源到哪一步了？

这是字节跳动与杜克大学等机构研究者提出的 Agent 训练方案，代码仓库是 bytedance/axion1_0。核心流程为两阶段监督微调（SFT）加异步 GRPO 强化学习，不额外加入专门的 mid-training、DPO 或 on-policy distillation 阶段。

论文的两个主要模型分别基于 Qwen3.6-35B-A3B 和 Qwen3.5-122B-A10B。35B / 122B 是总参数规模，3B / 10B 是每次计算激活的参数规模。激活少不等于只需要存储激活部分的权重。

| 公开资源 | 核实到的内容 | 使用时的边界 |
|---|---|---|
| GitHub | 数据构造、过滤、SFT、RL、评测准备与打分代码 | 训练环境和分布式 GPU 路径尚不能视为完整实测复现 |
| 数据集 | 10,819 条 Stage I、7,544 条 Stage II、484 个 RL 任务 | SFT 是完整对话；RL 是任务和答案，不是另一批完成的轨迹 |
| 35B 权重 | 模型卡明确标注 community reproduction | 不是论文官方 122B checkpoint，也不能照搬其成绩 |

代码、数据集和公开模型卡均声明 Apache-2.0；上游数据库及第三方组件的具体条款仍需分别保留。论文在 arXiv 上的授权与代码授权也不同，“全部开源”不应被理解为所有来源都自动适用同一许可证。

## 高质量数据如何被“构造”出来？

### 第一阶段：让题目针对底座的能力变难

Stage I 从公开课程、竞赛及推理问题出发，先组合出新题，再用底座实际求解。如果模型已经能答对，就依据它的解法继续加难：增加依赖步骤、把常数改成参数、扩大参数范围，或者引入必须分情况讨论的条件。

例如，一道代入公式就能得到数字的题，可以改为先证明中间量，再求包含该量的表达式。目标是增加必要的推理，而不是把题干写得更长。改写之后必须重新确定答案，不能沿用旧答案。

论文用 GPT-5.5 独立求解三次，并检查答案一致性与推导；收集轨迹时允许 Python，禁用搜索和网页检索。它省掉了一些训练阶段，却仍然需要生成、验证和采样的教师成本。没有 OPD 阶段，并不意味着完全不用强模型生产训练数据。

### 第二阶段：先用程序确定答案，再让模型出题

Stage II 的方法更适合借鉴：程序先筛选数据库记录，唯一选定一个实体，再计算参考答案，最后由语言模型把条件转成自然语言。

比如，从满足条件的系外行星中挑出某个极值对象，再查质量和半径求密度。程序要检查实体唯一性、极值之间的间隔、字段完整性、单位和数值精度。跨库任务则保存每个中间实体的标识，用于后续验证。

求解时不把构造用的数据库表和答案直接交给 Agent，而是让它通过搜索、网页访问、学术检索和 Python 找回事实；再用闭卷探测剔除不检索也能答对的题。这能增强“必须找证据”的训练信号，但闭卷失败本身不是绝对无污染证明。

![小M把数据库条件、唯一实体和计算答案连接成可验证任务](../../assets/images/axion-agent-training-data-cost-review-fig-01.png)

**值得迁移的是答案先行的数据工程：先把正确性定义清楚，再生成语言表述和成功轨迹。** 如果题目本身歧义、数据过期或单位错误，更多采样只会放大问题。

## 只有一万多条数据，为什么不等于“小训练量”？

两阶段共 18,363 条 SFT 轨迹，但每条可以包含多轮推理、工具调用和返回结果，不能按普通短问答理解。仓库报告 Stage II 约 312M tokens，SFT 使用 128K 上下文、三轮训练和 BF16 全参数更新。

公开数据把完整轨迹放在 messages 中；question 和 response 是方便浏览的派生列。只拿最后一段 response 训练，会丢掉搜索、观察与后续决策的关系。数据卡还明确说明，工具响应被编码在 user 消息中，接入别的训练模板时需要保持角色和 loss mask 一致。

论文只监督 assistant 生成的推理、工具调用和答案；系统提示、用户内容与工具观察提供上下文，不承担监督损失。参考答案和验证目标用于检查，不能混进求解输入。

另一个复现细节是：公开 Stage I 有 10,819 条，但保存的 122B SFT 输入记录为 9,840 条，并要求经过真实 Swift 模板计算长度和过滤。两个数字不能直接互换；重建训练输入应核对格式、长度、过滤记录和哈希。

## 强化学习究竟增加了什么？

SFT 学的是成功示范，RL 让模型用自己的策略实际探索。Axion 用异步 GRPO，每题采样八条轨迹，并给可验证的中间进展部分奖励。

最终答案正确得 1 分。否则，奖励是 max(0, 0.3 × P − 0.1 × (1 − A))，P 是按依赖顺序验证的进展比例，A 表示是否提交有效最终答案。三步链条里只有第一步和第三步正确，进展仍只有三分之一，因为第二步未成立。

筛选 RL 任务时，先排除评测重叠和缺陷问题，再从同一 checkpoint 离线采四次，保留至少答对一次且奖励有方差的题。这四次用于选题，不是正式训练的八次 rollout。

基础设施仍有复杂度：rollout 与训练使用分离 GPU 池；TITO 保存实际 token ID，减少重新分词引入的不一致；R3 记录 MoE 路由并在训练时重放，减少推理与训练选择不同专家的偏差。上下文压缩把长轨迹划成 session，因此 token、策略版本、奖励与会话边界都需要准确记录。

“方案简单”描述的是训练阶段数量，不代表单机脚本就能完成全部工程。仓库也明确：原始最终 RL 环境没有完整恢复，部分部署参数需要用户填写，分布式 GPU 训练尚未重新验证。

## 约 1K GPU-hours 能证明什么？

项目主页写的是约 1K 的 122B training GPU-hours。论文第 5.1 节能够直接核算的 SFT 明细如下，均为作者报告，非我们的测量。

| 模型 | GPU 数 | Stage I | Stage II | 两阶段 SFT |
|---|---:|---:|---:|---:|
| 35B | 32 | 1 小时 02 分 | 1 小时 46 分 | 约 90 GPU-hours |
| 122B | 32 | 3 小时 32 分 | 3 小时 58 分 | 240 GPU-hours |

122B 的 32 × 7.5 小时 = 240 GPU-hours，这是设备占用时间的累加，不是租金，也不是单卡训练 240 小时的可替换方案。论文还报告 122B SFT 每卡峰值显存 113 GiB，35B 为 101 GiB，不能将其写成消费级显卡可轻松复现。

RL 配置另有 40 张 rollout GPU、16 张 trainer GPU，以及评判和摘要等辅助模型服务。论文没有给出足以独立核算全部 RL 开销的完整运行时长，仓库也要求补充优化步数。因此，我们保留主页的约 1K 说法，但不将它当作独立验证的完整成本账单。

数据生成、教师调用、检索、验证、失败实验、底座预训练及上线推理，也不能默认包含在这个数字里。“后训练成本较低”与“从零做出整个系统只花这么多”是不同判断。

![小M分别核对SFT明细、RL资源和未列明的成本边界](../../assets/images/axion-agent-training-data-cost-review-fig-02.png)

## HLE 超过 GPT-6，应该怎样读？

论文表 1 报告：限制访问 Hugging Face 等网站时，Axion-122B 的完整 HLE 为 59.0%，35B 为 52.2%；不施加这些访问限制，则分别为 64.8% 和 59.1%。工具访问条件足以改变结果，引用分数必须带上条件。

同表引述 GPT-6 Astra 为 57.2%、Claude Opus 5 为 63.6%、Claude Fable 5 为 63.8%。这些是作者汇总的比较，不是我们对商业 API 做的同条件测试。论文明确指出，外部报告可能使用不同工具与执行设置。因此可以说 59.0 高于表内的 57.2，不能据此宣称通用能力全面领先，或当前所有榜单只排在两个模型之后。

作者自己运行的评测通常做三次、BMB 做五次，报告最好的一次，而非均值或投票融合结果。没有方差、统一预算与统一工具协议时，不宜把小分差扩展为稳定优势。

论文的完整 HLE 59.0% 与阶段分析用的 HLE-130 74.6% 也不能混用：后者是 130 道纯文本子集。公开评测指南主要围绕 HLE-130 准备与打分，推理 harness 还需要外接。

分阶段结果更有工程价值：35B 的 HLE-130 从 47.7 → 59.2 → 66.2 → 70.0；但 FrontierScience Research 在 RL 后从 58.3 降为 56.7。训练并非所有指标一起上涨，这些顺序 checkpoint 对比也不是严格的组件移除消融实验。

公开 35B 社区复现卡另报完整 HLE 52.8%，与论文 35B 的 52.2% 分列。我们没有独立重跑这两个分数，更没有把 122B 的 59.0% 写到下载的 35B 权重身上。

## 开发团队怎样利用这套思路？

Mycelium Protocol 的建议是先复刻数据闭环，再考虑扩模型。以下是工程方案建议，不是作者新增实验或已经验证的收益。

1. 选一个可验证的业务任务，例如从固定版本产品目录中识别符合条件的型号并计算成本；记录数据版本、单位和唯一性规则。
2. 先写确定性答案生成器与独立校验器，再生成自然语言问题；将答案、构造表、验证目标与求解环境隔离。
3. 用实际底座做闭卷和带工具的基线，记录成功率、工具调用、耗时与 token；按实体和来源划分训练集与留出集，避免同一道题换措辞进入两边。
4. 收集完整成功轨迹，剔除错误工具格式、异常中断、泄漏答案和重复题；按部署时的模板做 assistant-only SFT，先用小模型验证管线。
5. 如果 SFT 后仍有可重复的探索瓶颈，再做 RL。冻结检索权限、题集、工具和预算，报告多次运行的均值、离散程度及成本，并保留回归指标。

商业落地还需要实际任务的权限、数据边界、失败恢复、可观测性与人工接管。“科学推理榜单表现强”不能自动等同于支付、发信或修改企业系统时的可靠性。

![小M把任务构造、轨迹训练和固定协议评测接成闭环](../../assets/images/axion-agent-training-data-cost-review-fig-03.png)

### 我们实际检查了什么？

本次固定仓库版本 66cab5555ca25d3a5460ca6a6eff07f3a6bcabbc，在独立 Python 3.12 环境中运行了四个测试文件的选定 CPU 检查，结果为 104 passed、2 deselected，另有 18 个通过的子检查。

覆盖轨迹转 SFT、阶段工具限制、参考答案评分、带依赖的进展奖励、HLE 输出以及 SFT 启动和导出配置。部分网络返回和训练对象使用测试替身；两项需要更完整 Torch/verl 栈的 reward-manager 检查未执行。初跑缺少依赖和 macOS 临时目录的路径别名导致失败，补齐轻量依赖、使用规范化临时目录后重跑通过，未改上游代码。

我们也核对了 Hugging Face 数据浏览接口的记录数和两条 Stage II 消息结构。这是小样本格式检查，未下载全量训练数据或权重，未验证全部答案正确性、实际 loss mask、GPU 显存、训练吞吐、HLE 成绩或线上可靠性。测试通过证明的是这部分代码行为，不是论文结果已复现。

## 常见问题

### 下载公开的 35B，就能拿到 122B 的能力吗？

不能。公开链接明确是 35B 社区复现 checkpoint，其模型卡单独列了复现成绩。参数规模、训练细节与评测条件都需要分别核对。

### 18K 数据意味着准备成本很低吗？

不必然。这里是长轨迹，包含生成、求解、验证、工具返回与过滤成本。样本数少并不等于 token 数少，更不等于教师和检索免费。

### 这是否证明复杂训练算法都没用了？

没有。它说明高质量构造数据加较少训练阶段是一条有竞争力的路线。既有底座、长上下文训练、异步采样和 MoE 一致性工程仍然发挥作用，也不能从一个项目推导出所有替代方案无效。

## 原始资料与延伸阅读

论文：https://arxiv.org/abs/2611.03233 （本文核对 v2）
PDF：https://arxiv.org/pdf/2611.03233
项目主页：https://axion1-0.github.io/
代码：https://github.com/bytedance/axion1_0
数据：https://huggingface.co/datasets/Axion1-0/axion-training-data
35B 社区复现：https://huggingface.co/Axion1-0/Axion-1.0-35B
训练部署边界：https://github.com/bytedance/axion1_0/blob/main/axion/training/rl/README.md

相关实践：https://blog.mushroom.cv/blog/agentic-rl-lab-grpo-vision-post-training-low-cost-geometry/
后训练学习：https://blog.mushroom.cv/blog/rlhf-book-chinese-post-training-learning-guide/
'''
en='''Axion 1.0 centers agent training on verifiable tasks and complete solution trajectories: reasoning SFT first, tool-dependent SFT second, and asynchronous GRPO last. Its most useful contribution is a concrete way to manufacture learning signals and connect data, training, tools, and evaluation.

Several claims need separate treatment. Approximately 1K GPU-hours is the project website’s claim; the paper’s 122B scores, the downloadable 35B community reproduction, and production reliability are different evidence categories. We reviewed paper v2, code, and Hugging Face cards and ran selected local checks. We did not reproduce training or benchmark scores.

## What is available, and which model can you download?

ByteDance and collaborators including Duke University propose two consecutive supervised fine-tuning stages followed by asynchronous GRPO, without dedicated mid-training, DPO, or on-policy distillation stages.

The paper’s main models start from Qwen3.6-35B-A3B and Qwen3.5-122B-A10B. Total parameters are 35B and 122B; active parameters are 3B and 10B. Sparse activation does not remove the storage requirement for the other experts.

The GitHub repository provides construction, filtering, SFT, RL, and evaluation preparation/grading code. The dataset card lists 10,819 Stage I conversations, 7,544 Stage II conversations, and 484 RL tasks. RL tasks contain prompts and reference information, rather than another set of completed SFT trajectories.

The linked 35B model is explicitly a community reproduction, not an official 122B checkpoint. Code, dataset, and model cards declare Apache-2.0; upstream data and component terms still need separate attention. The arXiv paper has its own license.

## How do they construct useful training tasks?

### Stage I: strengthen problems using base-model feedback

Public course, competition, and reasoning questions become seeds for new problems. The generator first composes an additional dependency. If the base model solves the validated result, its solution guides another transformation: composition, parameterization, range changes, or case analysis.

This aims to increase necessary reasoning rather than question length. Every rewrite needs a newly verified answer. The paper describes three independent GPT-5.5 solutions plus agreement and derivation checks. Trajectory collection allows Python but disables retrieval.

Removing an OPD training stage therefore does not mean removing strong teacher models from data production. Generation, independent solving, filtering, and tool use remain real work and potential costs.

### Stage II: determine the answer before verbalizing the question

Programs filter records, uniquely select an entity, and compute an answer. A language model then turns the constraints into a natural question. One example selects an exoplanet by specified properties and asks for density derived from its mass and radius.

Construction checks uniqueness, selection margins, missing fields, units, and precision. Cross-database tasks retain intermediate identifiers. During solving, construction tables and references are withheld; the agent must recover evidence through search, page visits, scholarly retrieval, and Python. Closed-book probes remove questions answerable without retrieval, although such filtering is not absolute proof against contamination.

![Little M connects database constraints, a unique entity, and a computed reference](../../assets/images/axion-agent-training-data-cost-review-fig-01.png)

The transferable principle is to define correctness before generating language and trajectories. Ambiguous tasks, stale records, and unit mistakes cannot be repaired simply by collecting more solutions.

## Why does 18K examples not mean a tiny workload?

The 18,363 SFT examples are long conversations, not ordinary short question–answer pairs. Stage II alone is reported at roughly 312M tokens. SFT uses 128K context, three epochs, and full-parameter BF16 updates.

Train from messages to preserve actions, observations, and subsequent decisions; question and response are browsing columns. The data card encodes tool observations as user messages, which matters when adapting templates and loss masks.

The paper supervises assistant reasoning, tool calls, and answers. System/user messages and observations provide context without supervised loss. References and intermediate targets must stay out of solving inputs.

One reproducibility detail deserves attention: the public Stage I split has 10,819 records, while saved 122B SFT input provenance describes 9,840 conversations. The training path requires length annotation and filtering with the actual Swift template. These counts are not interchangeable; reconstructing the run requires matching transformations and input hashes.

## What does RL add?

RL starts from Stage II and lets the policy interact with tools. Eight rollouts per prompt receive outcome and intermediate-progress rewards.

A correct final answer earns 1. Otherwise, reward is max(0, 0.3 × P − 0.1 × (1 − A)), where P measures prerequisite-ordered verified progress and A indicates a valid final submission. Passing steps one and three in a three-step chain earns only one-third progress when step two is missing.

Task selection first excludes held-out overlaps and defective questions, then samples four attempts from one checkpoint. A task must have at least one correct answer and nonzero reward variance. These four selection attempts are distinct from the eight training rollouts.

Engineering remains substantial. Separate GPU pools generate and train. TITO preserves actual token IDs rather than reconstructing them by decoding and re-tokenizing. R3 records and replays MoE expert choices. Context condensation splits long trajectories into sessions, requiring consistent token masks, rewards, and policy-version accounting.

A simple sequence of training stages is not a simple deployment. The release states that the complete historical final RL environment was not recovered, several deployment inputs remain user-supplied, and distributed GPU training has not been revalidated.

## What does approximately 1K GPU-hours cover?

The project website advertises approximately 1K training GPU-hours for 122B. Section 5.1 gives an independently calculable breakdown for SFT, reported by the authors rather than measured here:

| Model | GPUs | Stage I | Stage II | SFT GPU-hours |
|---|---:|---:|---:|---:|
| 35B | 32 | 1h 02m | 1h 46m | approximately 90 |
| 122B | 32 | 3h 32m | 3h 58m | 240 |

For 122B, 32 × 7.5 hours equals 240 GPU-hours. This is accumulated device time, not a dollar bill or proof that one GPU could run the workload for 240 hours. Reported peak SFT memory is 113 GiB per GPU for 122B and 101 GiB for 35B.

The RL setup additionally uses 40 rollout GPUs, 16 trainer GPUs, and auxiliary model services. The paper does not provide sufficient complete RL runtime information to independently reconstruct its total cost; the released launcher also requires an optimizer-update count.

We retain the website’s approximately 1K figure with attribution. It is not an independently verified end-to-end cost ledger. Data generation, teacher calls, retrieval, validation, failed experiments, base pretraining, and deployed inference cannot simply be assumed included.

![Little M separates documented SFT cost from RL resources and unspecified costs](../../assets/images/axion-agent-training-data-cost-review-fig-02.png)

## Does the HLE comparison establish superiority over GPT-6?

Paper Table 1 reports full HLE of 59.0% for 122B and 52.2% for 35B with access to sites such as Hugging Face restricted. Without those restrictions, results become 64.8% and 59.1%. Tool access materially changes the result.

The same table cites GPT-6 Astra at 57.2%, Claude Opus 5 at 63.6%, and Claude Fable 5 at 63.8%. This is the authors’ comparison, not our controlled commercial-API experiment. The paper explicitly warns that external reports can use different tools and execution settings. A higher number in this table is not proof of universally better capability or a current global ranking.

For evaluations performed in their harness, the authors generally run three times, or five for BMB, and report the best single run. This is neither a mean nor a vote across attempts. Small differences need a shared budget, protocol, and uncertainty estimates before supporting a claim of stable superiority.

The full-HLE score of 59.0% is also different from the 74.6% HLE-130 result used in stage comparisons. HLE-130 is a 130-question text-only subset. The public evaluation guide focuses on preparing and grading that subset; an external inference harness is still required.

Stage comparisons are particularly informative: 35B HLE-130 progresses 47.7 → 59.2 → 66.2 → 70.0, while FrontierScience Research declines from 58.3 to 56.7 after RL. These are sequential checkpoints, not component-removal ablations, and improvement is not universal.

The community 35B card separately reports full HLE of 52.8%, versus 52.2% for the paper’s 35B. Neither was independently reproduced here. The paper’s 122B score must not be assigned to the downloadable 35B model.

## How should an engineering team apply the idea?

Mycelium Protocol recommends reproducing the data loop before scaling the model. The following is our implementation proposal, not a newly measured result:

1. Choose a bounded business task with deterministic references, such as selecting a product from a versioned catalog and calculating cost. Record units, source versions, and uniqueness rules.
2. Build answer generation and independent validation before question verbalization. Isolate construction data, answers, and verification targets from solving inputs.
3. Measure the actual base model with and without tools. Record success, tool calls, latency, and tokens. Split by entities and sources to prevent paraphrased duplicates crossing into held-out evaluation.
4. Collect complete successful trajectories. Reject malformed calls, interrupted runs, answer leakage, and duplicates. Match deployment templates and assistant-only supervision, starting with a smaller model to validate the pipeline.
5. Add RL only when SFT leaves a repeatable exploration bottleneck. Freeze tools, retrieval permissions, tasks, and budgets; report repeated-run means, dispersion, costs, and regressions.

Production use also needs permissions, data boundaries, recovery, observability, and human takeover. Scientific benchmark performance alone does not establish reliable behavior when sending messages, paying bills, or modifying enterprise systems.

![Little M closes the loop from task construction through training to fixed-protocol evaluation](../../assets/images/axion-agent-training-data-cost-review-fig-03.png)

### What did we actually verify?

At repository revision 66cab5555ca25d3a5460ca6a6eff07f3a6bcabbc, selected CPU checks from four test files produced 104 passed, 2 deselected, and 18 passing subtests in an isolated Python 3.12 environment.

Coverage includes trajectory conversion, stage tool restrictions, reference scoring, prerequisite-ordered rewards, HLE output, and SFT launch/export configuration. Some network responses and training objects are test doubles. Two reward-manager checks requiring a fuller Torch/verl stack were excluded. Initial missing dependencies and macOS temporary-path aliases were resolved by installing lightweight dependencies and selecting a canonical temporary directory, without changing upstream code.

We also checked Hugging Face viewer counts and the message structure of two Stage II examples. This is a small format sample, not a complete data audit. We downloaded no model weights and did not validate GPU execution, actual loss masking, training throughput, peak memory, full benchmark scores, or production reliability.

## FAQ

### Is the released 35B checkpoint equivalent to the paper’s 122B?

No. It is explicitly a community reproduction with its own results. Model size, training details, and evaluation conditions must be tracked separately.

### Does 18K examples imply inexpensive data preparation?

Not necessarily. These are long trajectories involving generation, solving, verification, tools, and filtering. Few records can still represent substantial token and service costs.

### Does this make more elaborate training methods obsolete?

No. It establishes a competitive direction centered on constructed data and fewer training stages. Strong base models, long-context training, asynchronous generation, and MoE consistency still matter; one project does not invalidate alternative recipes.

## Primary sources and related reading

Paper: https://arxiv.org/abs/2611.03233 — reviewed version v2.
PDF: https://arxiv.org/pdf/2611.03233
Project: https://axion1-0.github.io/
Code: https://github.com/bytedance/axion1_0
Data: https://huggingface.co/datasets/Axion1-0/axion-training-data
Community 35B reproduction: https://huggingface.co/Axion1-0/Axion-1.0-35B
RL deployment boundaries: https://github.com/bytedance/axion1_0/blob/main/axion/training/rl/README.md

Related practice: https://blog.mushroom.cv/blog/agentic-rl-lab-grpo-vision-post-training-low-cost-geometry/
Post-training guide: https://blog.mushroom.cv/blog/rlhf-book-chinese-post-training-learning-guide/
'''
desc='Axion 1.0用可验证任务构造、两阶段SFT和异步GRPO训练科学推理与工具型Agent。本文核对论文、开源代码、数据与35B社区复现模型，拆解约1K GPU-hours的成本边界、HLE完整集和130题子集的差别，以及多次取最好成绩的评测条件，并给出数据闭环实践建议，区分作者报告、代码检查与尚未复现的能力。'
den='Review Axion 1.0 data construction, SFT and RL, separating reported HLE results, training cost, community weights, and our selected local CPU code checks.'
while len(desc)<150:desc+='供开发者参考。'
while len(den)<150:den+=' Read on.'
assert 150<=len(desc)<=160,(len(desc),desc)
assert 150<=len(den)<=160,(len(den),den)
f={'title':'Axion 1.0：数据构造、Agent训练与低成本叙事的边界','titleEn':'Axion 1.0: Agent Data, Training, and Cost Boundaries','description':desc,'descriptionEn':den,'wechatTitle':'Axion 1.0：Agent训练贵在哪里','wechatDigest':'拆解可验证数据、三阶段训练与HLE成绩，厘清1K GPU小时的成本口径。','pubDate':'2026-11-09','updatedDate':'2026-11-09','category':'Tech-News','tags':['Axion','Agent','SFT','GRPO','开源模型','数据构造'],'heroImage':'../../assets/images/'+slug+'-banner.jpg'}
fm='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in f.items())+'\n---\n\n'
cccn='\n---\n\n> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。\n'
ccen='\n---\n\n> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.\n'
Path('src/content/blog/'+slug+'.md').write_text(fm+cn+cccn+'\n<!--EN-->\n\n'+en+ccen)
print(len(desc),len(den))
