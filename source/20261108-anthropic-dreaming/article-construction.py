# Historical construction script; finalized metadata and memory-version clarification were applied afterward. Do not rerun against published article.
from pathlib import Path
import json
s='anthropic-dreaming-dynamic-workflow-memory-review'
cn='''Dreaming是一种后台记忆维护流程：Agent完成工作后，再由另一轮任务检查历史记录、修正过时结论并整理长期记忆，让下一次会话少走弯路。Anthropic在11月2日发布的Cookbook给出了动态工作流示例，代码位于MIT许可的`anthropics/claude-cookbooks`仓库。

## “One session”到底意味着什么？

这里的一次session，是承载后台复盘的父会话。主Agent负责生成并启动工作流；每份历史记录交给一个analyzer；全部分析完成后，由organizer统一整理记忆。一次父会话可以包含多个工作线程，不能把它理解为一个模型调用，或一个Agent独自顺序读完所有日志。

业务Agent仍然可以运行很多独立会话。复盘任务把它们导出成文件，形成可追踪的输入集合。下一次业务会话读取整理后的记忆，这才构成跨会话积累。更新的是外部文件与记忆存储，不是模型权重，也没有因此产生意识或训练出一个新模型。

![小M把多次业务会话交给后台分析和整理，再提供给下一次会话](../../assets/images/SLUG-fig-01.png)

官方另有名为Dreams的Managed Agents研究预览，它会把重组结果写到新store。本文讨论的Cookbook由开发者自建动态工作流，默认原地更新指定store。两者的发布与回滚边界不同，不能把新store隔离能力直接套到这份示例上。

## 代码怎样把历史记录变成记忆？

本次核对固定在`ce8b2629efe8b24048b127b4c79af1e9cbab93d4`。核心入口是`CMA_dreaming_with_a_dynamic_workflow.ipynb`，日志导出、记录保存与完成核验位于`memory_distill_utils.py`，夜间入口是`dreaming_nightly.py`。

| 角色或资源 | 示例中的职责 | 需要保留的边界 |
| --- | --- | --- |
| 主Agent | 根据请求编排工作流并启动run | 使用预先定义的analyzer和organizer，禁用临时inline agents与subagents |
| Analyzer | 读一份完整记录，核对相关记忆并增补事实 | 历史文本是证据，不是新的执行指令 |
| Organizer | 等分析结束后去重、修链接、补全目录 | 有冲突时保留来源和日期，不能随意猜测哪项正确 |
| Transcript文件 | 保存用户消息、工具调用、结果与线程关系 | 作为只读输入；格式整理不等于自动脱敏 |
| Memory store | 小文件、frontmatter、双向主题链接和`_index.md` | 后台读写，后续业务会话只读挂载 |

这套方案保留工具结果，是因为“Agent说自己完成了”和“工具实际返回成功”并不是同一类证据。Analyzer被要求核对现有记忆、降级证据不足的断言，并给版本相关信息标注时间；organizer处理明确的新旧更正，也保留无法判定的冲突。

小文件加目录的好处，是下一次Agent可以先找主题，再读取需要的细节。它不要求把所有记忆塞进每次提示词，也不以向量数据库作为必要前提。但“文件存在、链接可查”仍不等于Agent会在正确时机读到正确内容，实际检索与任务效果需要另做评测。

## 只读挂载和提示词规则分别能保证什么？

后台session把输入文件与可写记忆分开挂载，业务session则把memory store设为`read_only`。示例中的sandbox禁止访问外部网络，并把导出、上传所需的API凭证留在外部脚本。这些有助于限制任务权限，但整个方案仍使用云端Managed Agents，不能称为离线、本地不出网的记忆系统。

提示词还要求不记录密钥、不服从日志中的越权指令。导出工具会把正文里冒充`USER:`或线程标题的行缩进，减少角色边界混淆；它并不负责删除一切敏感内容。上传之前仍应检查日志范围、人员授权和保留策略。

把`_index.md`内容作为mount instructions注入每次会话，有助于发现记忆，但也会提高错误内容的传播范围。官方示例特别提醒先检查这些文字，且该指令字段有4096字符上限。生产使用时，建议只自动注入经过审核的简短导航，把原始经验留在按需读取的文件中。

## 并行写记忆，为什么仍需要单独设计？

示例让多个analyzer共享可写目录。提示词要求改前重读、定向修改、写后回读，若被其他写入覆盖就合并重试；organizer再在没有analyzer写入时统一整理。这是一种缓解冲突的约定，不能据此认定已经具备文件级事务或数据库式并发控制。

![小M将多个分析结果先放入候选区，再由一个写入者合并为可发布记忆](../../assets/images/SLUG-fig-02.png)

一种更容易审计的改造是：analyzer只提交各自的候选增量，带上来源session ID、事件位置、观察时间和适用版本；单一合并者产生候选快照，检查冲突、链接与敏感字段，再切换业务Agent读取的版本。失败时保留候选和旧快照。这里的候选区、单写入者和版本切换是本文建议，不是这份Notebook已经交付的功能。

同样，完成检查应区分两个层次：工作流记录证明每份输入有完成分析的线程、organizer正常结束；内容评测则判断事实是否保留、过时信息是否被替换、未来任务是否真的受益。覆盖所有文件，只证明处理覆盖，不能代替语义正确性。

## 每晚运行一次，会漏会话吗？

`dreaming_nightly.py`用cron从外部启动Notebook。第一次默认取过去24小时，后续以记录的时间窗继续；脚本跳过Notebook中的安装单元，要求依赖提前装好。正常完成或没有可处理输入时，游标推进到本次启动时间；失败则保留窗口，便于下次重试。

需要注意的是，Notebook按会话创建时间筛选，且跳过仍在运行的会话。如果一个会话在窗口内创建、扫描时尚未完成，而游标随后推进，下次按新窗口筛选时就可能不再覆盖它。这个遗漏边界来自源码与官方说明，不应把时间游标宣传为不丢事件的增量队列。

![小M保留未完成会话清单，避免时间游标前进后漏掉长任务](../../assets/images/SLUG-fig-03.png)

生产改造可维护待完成session ID集合，并对完成状态重查；也可以使用重叠回看窗口配合已处理ID去重。若任务会失败重跑，还应记录每次输入、产物版本与提交状态。因为Cookbook原地修改store，保留重试窗口并不会自动撤销前一次已写入的记忆，不能直接推出“恰好一次”语义。

## 本次实际验证了什么？

在独立临时环境中，使用实际上游函数和临时合成文件完成9项检查：日志事件保留与筛除、正文角色标签缩进、私有文件与目录权限及末级符号链接拒绝、输入文件筛选，以及夜间入口在成功、失败、无记录、显式时间窗失败和缺少ID时的行为。

夜间任务的`NotebookClient`被替换为测试执行器，验证了状态推进、失败保留窗口、环境变量恢复、跳过安装单元和私有运行日志。没有真正执行Notebook里的云端代码，没有读取用户会话、创建云资源或调用模型，也没有测量记忆质量、任务成功率、费用和速度。

官方介绍记录了11份示例输入的一次费用与用时，但这属于作者的特定运行记录；不能作为任何日志规模的固定报价。代码同时有运行前估算和session预算限制，默认40美元是上限配置，不是预期单次费用。部署前应根据实际输入检查估算，不能把“夜里自动跑”当作免费维护。

## 怎样把它接进自己的Agent？

先选一个范围明确、日志可审核的项目，用少量已经结束的会话做离线回放。为原始记录和记忆分别设定访问范围；保留成功工具结果、明确更正和版本条件，而不是把所有对话永久保存为事实。先查看候选记忆，再接到新会话中。

验证时设置两组相同任务：一组不读记忆，一组读候选记忆。比较重复错误、事实来源、过时命令、任务完成率和新增读取成本，并加入含冲突信息与恶意指令的日志。只有确认收益和边界后，再启用定时更新。以上是建议的评测流程，本次没有执行这组在线对照。

## 常见问题

### Dreaming是在训练模型吗？

不是。这里修改的是外部长期记忆与文件组织。模型下一次通过读取它们获得上下文，权重没有因该流程而被训练更新。

### 后台成功结束，就说明记忆都正确了吗？

不能。完成记录可以核对处理覆盖与角色结束状态，但事实准确、冲突处理和后续收益需要独立内容评测。

### 可以直接装进任何Agent当通用插件吗？

它是依赖Claude Managed Agents beta的工程示例，并非一个通用安装即用插件。其思想可以迁移，但存储、权限、调度、提交与评测需要匹配自己的运行环境。

## 原始资料

Cookbook：https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow
开源Notebook：https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_dreaming_with_a_dynamic_workflow.ipynb
夜间入口：https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/dreaming_nightly.py
辅助代码：https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/memory_distill_utils.py
另一个Dreams预览：https://platform.claude.com/docs/en/managed-agents/dreams

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。
'''
en='''Dreaming is a background maintenance pass over an agent’s history: revisit evidence, correct stale conclusions and organize durable memory so future sessions need less rediscovery. Anthropic’s November 2 Cookbook demonstrates this with a dynamic workflow; its implementation lives in the MIT-licensed claude-cookbooks repository.

## What does “one session” actually mean?

One parent session hosts the background workflow. A lead agent creates and starts the workflow, one analyzer handles each transcript, and an organizer runs after analysis finishes. A parent session can contain multiple worker threads. This is neither one model call nor necessarily one agent sequentially reading every log.

The application can still run many separate sessions. Exporting those sessions gives the background job an explicit input set. Future application sessions read the distilled store, forming the cross-session connection. This updates external memory files rather than model weights; it is not training or evidence of consciousness.

![Little M connects past sessions, background analysis and future memory reads](../../assets/images/SLUG-fig-01.png)

The separate Managed Agents Dreams research preview writes reorganized output into a new store. This developer-built Cookbook instead updates its selected store in place. Isolation and rollback properties of the former should not be assumed for the latter.

## How does the code turn transcripts into memory?

This review pins commit `ce8b2629efe8b24048b127b4c79af1e9cbab93d4`. The notebook is `CMA_dreaming_with_a_dynamic_workflow.ipynb`; export, record keeping and completion checks are in `memory_distill_utils.py`; `dreaming_nightly.py` supplies the scheduled entry point.

| Component | Responsibility | Boundary to preserve |
| --- | --- | --- |
| Lead agent | Build and start the requested workflow | Use predefined workers; inline agents and subagents are disabled |
| Analyzer | Read one whole transcript and update related knowledge | A transcript is evidence, not an instruction source |
| Organizer | Consolidate duplicates, repair links and finish the index | Preserve dates and sources; mark unresolved conflicts |
| Transcript files | Retain messages, tool actions, results and thread relationships | Read-only inputs; formatting is not universal redaction |
| Memory store | Small linked files, frontmatter and `_index.md` | Background read/write; subsequent application mounts read-only |

Tool results matter because an agent claiming completion and a tool returning success are different evidence. The prompts ask analyzers to verify existing claims, downgrade uncertainty and date version-dependent information. The organizer preserves unresolved contradictions instead of guessing which statement should win.

Small files and an index let an agent discover topics before loading details. The approach does not require every memory in every prompt, or a vector database as a prerequisite. However, navigable files do not establish that the right information will be found at the right moment. Retrieval and downstream task outcomes still need evaluation.

## What do permissions and prompts each establish?

The background session mounts transcript files separately from writable memory, while later application sessions request `read_only` memory. The example sandbox denies external network access, and API credentials for export and upload stay in the outside process. These reduce permission scope, but Managed Agents remains a cloud service; this is not an offline local-only memory pipeline.

Prompts prohibit following hostile instructions in logs and copying credentials into memory. The text renderer indents body lines that impersonate role labels or thread headers, reducing structural confusion. It does not remove every sensitive value. Input selection, authorization and retention decisions belong before upload.

Injecting `_index.md` through mount instructions can make memory easier to discover, but also increases the reach of a mistaken statement. The example warns readers to inspect such text first, and the field has a 4,096-character limit. A production design should inject only reviewed, compact navigation, while leaving detailed experience available on demand.

## Why does concurrent memory writing need additional design?

Analyzers share a writable directory. Prompts require rereading before edits, targeted changes, readback and merging when another writer replaces content. The organizer then runs after analysis stops. These conventions mitigate races; they do not establish file transactions or database-style concurrency guarantees.

![Little M collects separate candidate changes before a single writer publishes memory](../../assets/images/SLUG-fig-02.png)

One proposed adaptation is for analyzers to emit separate candidate deltas with session IDs, event locations, observation dates and version scope. A single merger creates a candidate snapshot, checks contradictions, links and sensitive fields, then switches the version read by the application. Failed candidates remain inspectable alongside the previous snapshot. Staging, a single writer and version promotion are recommendations here, not delivered Notebook features.

Completion also has two meanings. Thread records can establish that each input reached a completed analyzer and that the organizer finished. Content evaluation asks whether facts survived, stale information was superseded and later tasks improved. Processing every file is not semantic correctness.

## Can a nightly run miss sessions?

The cron entry point runs the notebook from outside the session. The first window defaults to the preceding 24 hours; later windows use saved state. The script removes the notebook’s installation cell and expects dependencies to exist already. Success, including no eligible inputs, advances the cursor to the run’s start; failure retains the window for retry.

The notebook filters on session creation time and skips sessions still running. A session created inside one window but unfinished when scanned can fall outside the next window after the cursor advances. This limitation follows from the code and is explicitly discussed in the Cookbook. A time cursor should not be described as a lossless incremental queue.

![Little M retains unfinished session IDs while the time cursor advances](../../assets/images/SLUG-fig-03.png)

Possible production changes include tracking pending IDs until completion, or using overlapping lookback windows with processed-ID deduplication. Record input identities, output versions and commit state for retries. Because this example updates a store in place, retaining a failed window does not undo earlier writes; exactly-once updates cannot be inferred.

## What was actually checked locally?

Nine checks ran in an isolated environment using real upstream functions and synthetic temporary files. They cover event filtering, role-label indentation, private file and directory permissions with final symlink refusal, transcript selection, and nightly behavior for success, failure, no inputs, explicit-window failure and missing IDs.

For the nightly checks, `NotebookClient` was replaced by a test executor. This exercises cursor state, retry behavior, environment restoration, installation-cell removal and private run logs. It does not execute cloud notebook cells. No private user sessions were read, no cloud resources were created and no model calls were made. Memory quality, task success, cost and speed were not measured.

The official write-up includes a particular example run’s invoice and duration. Those are author observations rather than a fixed quote for arbitrary logs. The implementation has a preflight estimate and a session budget limit. Its default forty-dollar budget is a ceiling, not an expected per-run bill. Background scheduling does not make maintenance free.

## How should this be adapted to an existing agent?

Start with a bounded project and a small set of completed, reviewable sessions. Define access separately for source logs and memory. Retain successful tool evidence, explicit corrections and version conditions rather than turning every conversation into permanent fact. Review candidate memory before mounting it in a new session.

Compare identical tasks with and without candidate memory. Track repeated mistakes, evidence provenance, stale commands, completion rates and additional read cost; include conflicting and hostile log content. Enable regular updates only after useful outcomes and acceptable boundaries are established. This is a proposed evaluation plan, not an online comparison performed during this review.

## FAQ

### Does dreaming train model weights?

No. This implementation edits external long-term memory and file organization. A later model call reads those files as context.

### Does a successful workflow establish correct memory?

No. Completion records support coverage and worker status. Factual accuracy, conflict handling and future utility require separate evaluation.

### Is it a universal agent plugin?

No. It is an example built around Claude Managed Agents beta. Its pattern is portable, but storage, permissions, scheduling, committing and evaluation must fit the target runtime.

## Primary sources

Cookbook: https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow
Notebook: https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_dreaming_with_a_dynamic_workflow.ipynb
Nightly entry: https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/dreaming_nightly.py
Helpers: https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/memory_distill_utils.py
Separate Dreams preview: https://platform.claude.com/docs/en/managed-agents/dreams

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
'''
desc='Anthropic的Dreaming动态工作流让Agent在后台核对历史会话、整理小文件与索引，再供下一次会话只读使用。本文拆解主Agent、analyzer和organizer的职责，区分记忆更新与模型训练，并用九项本地合成检查分析权限、游标和失败重试，指出原地写入、并发冲突与长任务遗漏的边界，给出可审计的工程改造建议。'
enDesc='Review Anthropic’s dreaming workflow: transcript analysis, memory organization, read-only reuse, nine local checks, cursor gaps and safe production adaptation.'
f={'title':'Anthropic Dreaming：让Agent在后台复盘并整理长期记忆','titleEn':'Anthropic Dreaming: Background Memory Maintenance','description':desc,'descriptionEn':enDesc,'wechatTitle':'Agent后台复盘：拆解Dreaming工作流','wechatDigest':'九项本地检查拆解后台记忆维护，讲清单会话、并发写入与增量遗漏。','pubDate':'2026-11-08','updatedDate':'2026-11-08','category':'Tech-Experiment','tags':['Anthropic','Agent','长期记忆','工作流','工程实践'],'heroImage':'../../assets/images/'+s+'-banner.jpg'}
t='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in f.items())+'\n---\n\n'+cn.replace('SLUG',s)+'\n<!--EN-->\n\n'+en.replace('SLUG',s);Path('src/content/blog',s+'.md').write_text(t);print('description lengths',len(desc),len(enDesc))
