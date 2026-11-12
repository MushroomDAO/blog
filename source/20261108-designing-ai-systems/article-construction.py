# Historical construction script; final descriptions and WeChat title were adjusted before freezing. Do not rerun on published article.
from pathlib import Path
import json
s='designing-ai-systems-book-platform-code-review'
cn='''《Designing AI Systems》讲的是如何把模型调用背后的通用能力做成共享平台，让业务应用复用会话、知识、工具、评测和运行服务。已找到Manning官方链接的GitHub仓库：`designing-ai-systems/designing_ai_systems_repo`，适合结合书籍理解AI工程如何分层。

## 找到的是全书，还是配套代码？

直接入口：https://github.com/designing-ai-systems/designing_ai_systems_repo
出版社页面：https://www.manning.com/books/designing-ai-systems

Manning产品页的“Source code on Github”直接指向这个仓库，仓库也链接回同一本书，来源关系可以核实。完整书名为《Designing AI Systems: A guide to production-ready platforms》，作者是Suhas Suresha与Dewang Sultania；出版社介绍分别将两人与Adobe、Netflix的机器学习工程经历联系起来。

公开仓库主要包含Python平台代码、协议、示例、测试、容器配置与README，没有找到全书正文、PDF或EPUB。核验时也未找到明确的LICENSE文件或项目license声明，GitHub返回的license字段为空。因此本文称它为公开配套代码，不擅自标成MIT或Apache，更不把它介绍为整本书的免费开源版本。

出版社页面在本次核验时显示全部章节可读，同时保留MEAP和预计2026年11月出版的标记。阅读与购买入口应以出版社当前页面为准；仓库存在，不代表书籍文本采用了相同授权或可以任意转载。

## 这本书最值得学的架构是什么？

关键是把应用逻辑与可复用基础能力分开。一个应用可能处理内部知识问答，另一个负责多步任务，但它们通常都会遇到模型接入、会话状态、凭证、检索、质量评估和成本归因。共享平台的目标，是让这些能力有统一接口和运维方式。

![小M让多个业务应用复用模型、会话、知识和工具等平台服务](../../assets/images/SLUG-fig-01.png)

代码采用Python领域对象与gRPC边界分离的方式：业务调用者主要接触dataclass，服务端再完成协议消息转换。阅读时应跟踪一个请求如何穿过SDK、gateway、服务和存储，而不只记住文件夹数量。

| 能力 | 仓库入口 | 阅读重点 |
| --- | --- | --- |
| 模型与提示词 | `services/models/` | 供应商适配、模型发现、流式响应、提示词注册 |
| 会话与记忆 | `services/sessions/` | 用户与会话的区别、历史分页、记忆读写和持久化 |
| 企业知识 | `services/data/` | 解析、切块、embedding、向量与混合检索 |
| 工具与规则 | `services/tools/`、`services/guardrails/` | 凭证引用、调用限制、熔断与策略检查 |
| 观测与改进 | `services/observability/`、`services/experiments/` | trace、token和成本、离线评测、实验与人工标注 |
| 应用运行 | `services/workflow/`、`services/gateway/` | 同步、SSE、异步任务、工作流组合和部署 |

仓库的Compose配置组织九个平台服务与PostgreSQL，业务工作流则可以独立部署。这体现的是共享服务与每个应用执行单元的区别。对于小团队，也可以先保留模块接口、减少进程数量，再根据隔离、吞吐和团队分工拆分；这是本文的实施建议，不是要求所有项目一开始就运维整套微服务。

## 第9章助手到底有没有代码？

有。根README的状态表仍把AI Assistant写成planned，但`claw/README.md`明确介绍第9章参考应用，`claw/claw.py`也包含上下文组装、记忆、检索、工具分派、模型循环和观测评分。判断覆盖范围应结合实际目录，不能只看一个滞后的状态条目。

Claw很适合用来理解平台服务如何被业务应用组合。它先做输入检查，再组装提示词、用户记忆、检索资料和历史消息，进入有限轮次的模型循环，最后过滤输出、保存对话并记录评分。

但“看见某个工具返回成功”仍需要核对实现。当前Claw对日历和工单动作返回确定性的模拟结构，不会因此真的在企业日历建会或在工单系统开单；MCP工具走的是另一条平台分派路径。本文没有接入真实账户或验证这些外部集成。

## 本地检查发现了哪些值得注意的边界？

本次固定源码为`94dd7ecdd02de7c1289bb81765deeaaa23dffcee`，按`uv.lock`安装依赖后，在本地选跑87项上游测试：会话存储、凭证、规则存储、切块、工作流装饰器、熔断器69项，加上Claw的18项。全部通过。项目要求Python至少3.12，本次`uv`实际选择的是Python 3.14.7，不能把它说成已验证所有受支持版本。

另外运行了两项自建合成夹具，检查的都是实际服务对象，没有启动公开端点，也没有访问外部模型。

第一项检查默认Data Service的embedding。入口`services/data/main.py`直接构造`DataService()`；未注入embedding函数时，构造器使用占位实现。对两个不同问题调用实际生成器，都得到相同的1536维全零向量。这能帮助确认对象和管线接通，却不能证明检索获得了语义能力。部署时应把真实embedding服务接入，并验证索引与查询侧的模型、维度和实际召回质量。

第二项注册了一个标为`requires_confirmation=True`的工具，再直接调用`ExecuteTool`。底层HTTP使用`MockTransport`，结果是模拟端点仍被调用。这个结果只证明直接执行入口没有因为该元数据而自动要求审批凭证，不排除调用方另行检查。真实业务需要明确审批由谁发起、审批结果绑定什么参数，以及在哪个入口强制核验，不能把一个布尔字段当成完整审批机制。

![小M检查占位向量和确认标记，区分接口接通与真实能力](../../assets/images/SLUG-fig-02.png)

源码里的`_execute_sandboxed`主要负责HTTP或MCP分派，以及超时和响应大小限制；代码注释把CPU、内存等资源约束留给部署层。因此名称中的sandbox不能独立证明存在完整的操作系统隔离。动态注册解析器会加载代码，工作流服务还挂载Docker socket，这些控制接口需要明确的管理权限与信任范围。

以上是局部代码核对与合成测试，不是全平台安全审计。没有运行完整测试集、PostgreSQL集成、Docker或Kubernetes部署，没有调用付费模型、真实MCP服务器或企业工具，也没有做负载与RAG质量评测。

## 怎样把它当作学习项目使用？

先从第3、4章对应的模型与会话能力入手，理解一次模型调用如何携带上下文、生成响应并保存历史。默认内存存储适合开发，但进程重启后的长期记忆需要明确持久化后端，不能仅凭接口名称判断数据会一直存在。

第二步阅读第5、6章对应的数据、工具和规则实现。用受控小文档集合检查切块和检索，把工具指向自己控制的模拟端点，验证允许、拒绝、失败、超时与重试路径。先证明链路里的每个信号都是真实的，再接企业数据与凭证。

第三步读第7、8章的观测、实验和工作流，再用Claw看各模块如何合起来。对真实应用而言，HTTP返回200不够：还要观察答案是否有依据、动作有没有重复、成本是否可归因、失败能否恢复。观察指标和独立评测，应该与功能开发一起设计。

![小M把参考应用中的模拟动作替换为经过验证的真实集成，再进入运行验收](../../assets/images/SLUG-fig-03.png)

最小的源码学习入口如下。先检查当前版本和本地依赖，再选择测试；下面不包含任何账户配置或真实工具执行：

```bash
git clone https://github.com/designing-ai-systems/designing_ai_systems_repo.git
cd designing_ai_systems_repo
uv sync --frozen
uv run pytest tests/test_session_storage.py tests/test_credential_store.py -q
```

真实模型调用需要API凭证，工作流容器示例需要Docker，PostgreSQL与pgvector属于进一步的存储配置。README所谓“uv是唯一前置条件”，应理解为基础Python环境入口，不能替代这些场景各自的依赖。

## 常见问题

### 能从GitHub下载这本书的完整免费正文吗？

本次找到的是出版社认可的配套代码仓库，没有找到全书正文或电子书文件。书籍请使用Manning提供的阅读入口，公开代码与全书授权应分别确认。

### 它已经可以不改代码直接承接生产业务吗？

它提供了相当完整的参考结构，但当前默认与模拟路径仍需核对。持久化、真实embedding、审批执行和外部工具集成，都应该在自己的环境里完成验收。

### 适合谁读？

适合掌握Python和基本软件架构、准备从模型调用走向平台建设的开发者。想学习单个提示词或快速聊天页面的人，可以先选择其中一个模块，不必一次启动所有服务。

## 一手资料

配套GitHub：https://github.com/designing-ai-systems/designing_ai_systems_repo
Manning书籍页：https://www.manning.com/books/designing-ai-systems
Claw参考应用：https://github.com/designing-ai-systems/designing_ai_systems_repo/tree/main/claw
Data Service：https://github.com/designing-ai-systems/designing_ai_systems_repo/blob/main/services/data/service.py
Tool Service：https://github.com/designing-ai-systems/designing_ai_systems_repo/blob/main/services/tools/service.py

本文授权适用于原创评介与插图；书籍与外部代码的权利说明以各自来源为准。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。
'''
en='''Designing AI Systems explains how to turn the capabilities surrounding model calls into a shared platform: conversations, knowledge, tools, evaluation and operations. Manning directly links the public companion repository, `designing-ai-systems/designing_ai_systems_repo`, which is useful for studying how these responsibilities fit together.

## Is this the full book or companion code?

Repository: https://github.com/designing-ai-systems/designing_ai_systems_repo
Publisher: https://www.manning.com/books/designing-ai-systems

The publisher’s GitHub resource points to this repository, which links back to the same title. The book is Designing AI Systems: A guide to production-ready platforms, by Suhas Suresha and Dewang Sultania. Manning’s biographies associate their engineering experience with Adobe and Netflix respectively.

The repository contains Python services, protocols, examples, tests and deployment configuration. No full book text, PDF or EPUB was found. At the reviewed commit, no explicit LICENSE file or project license declaration was found either; GitHub’s license metadata is null. This review therefore describes public companion code, without assigning MIT or Apache licensing or claiming a freely open-sourced complete book.

The publisher page observed during this review shows all chapters available while retaining MEAP and estimated November 2026 publication labels. Use its current reading and purchase options. Public source availability does not establish identical reuse terms for the book’s prose.

## What architecture is worth learning?

The central separation is between application logic and reusable capabilities. An internal knowledge assistant and a multi-step task application often share needs for model access, state, credentials, retrieval, evaluation and cost attribution. A platform gives these common responsibilities consistent interfaces and operating practices.

![Little M connects multiple applications to shared platform capabilities](../../assets/images/SLUG-fig-01.png)

The implementation separates Python domain objects from gRPC messages. Application code primarily works with dataclasses; service boundaries translate protocol messages. Follow a request through the SDK, gateway, service and storage to understand the design, rather than memorizing a folder list.

| Capability | Repository entry | Questions to inspect |
| --- | --- | --- |
| Models and prompts | `services/models/` | Provider adapters, discovery, streaming and prompt registration |
| Conversations and memory | `services/sessions/` | User versus session scope, pagination and persistence |
| Enterprise knowledge | `services/data/` | Parsing, chunking, embeddings and hybrid retrieval |
| Tools and rules | `services/tools/`, `services/guardrails/` | Credentials, execution limits, circuit breaking and policy checks |
| Observation and improvement | `services/observability/`, `services/experiments/` | Traces, cost, offline evaluation, experiments and annotation |
| Application execution | `services/workflow/`, `services/gateway/` | Sync, SSE, asynchronous jobs, composition and deployment |

Compose organizes nine platform services plus PostgreSQL, while application workflows can be deployed separately. This illustrates shared services versus per-application execution units. A small team could preserve module boundaries while initially running fewer processes, splitting them as isolation, throughput and ownership require. That is an adoption suggestion, not a requirement that every project start with all these microservices.

## Is the chapter-nine assistant implemented?

Yes. The root README still labels AI Assistant as planned, but `claw/README.md` describes the chapter-nine reference application, and `claw/claw.py` includes context assembly, memory, retrieval, tool dispatch, a model loop and observation scoring. The directory is stronger evidence than a stale status row.

Claw shows how an application composes the platform. It validates input, assembles the prompt, user memory, retrieved documents and conversation history, runs a bounded model loop, then filters output, stores messages and records a score.

Successful-looking tool results require implementation checks. Calendar and ticket actions currently return deterministic mock structures; they do not establish that a real company calendar or ticketing system was updated. MCP tools use a separate platform dispatch path. No real accounts or external integrations were exercised in this review.

## What did local verification establish?

The reviewed commit is `94dd7ecdd02de7c1289bb81765deeaaa23dffcee`. After installing from `uv.lock`, 87 selected upstream tests passed: 69 across session storage, credentials, policy storage, chunking, workflow decorators and circuit breaking, plus 18 for Claw. The project requires Python 3.12 or newer; this local uv run selected Python 3.14.7. These results do not verify every supported interpreter.

Two additional synthetic fixtures exercised actual service objects without exposing a server or calling an external model.

The first inspected default Data Service embeddings. Its main entry point constructs `DataService()` without injecting an embedding function. The fallback produces placeholder vectors: two different synthetic queries returned identical, all-zero vectors of 1,536 dimensions. This can support wiring exercises but establishes no semantic retrieval capability. An adopter must connect real embeddings and check consistent models, dimensions and measured retrieval quality across indexing and querying.

The second registered a tool with `requires_confirmation=True` and called `ExecuteTool` directly. An HTTP MockTransport endpoint was still reached. This establishes that the metadata alone does not force an approval artifact at that direct entry point; a caller may separately enforce approval. A real application must specify who approves, which parameters approval covers, and where it is checked.

![Little M checks placeholder vectors and confirmation metadata against real execution requirements](../../assets/images/SLUG-fig-02.png)

The method named `_execute_sandboxed` primarily dispatches HTTP or MCP calls and enforces timeout and response-size limits. Its comments leave CPU and memory constraints to deployment. The name alone is not evidence of complete operating-system isolation. Dynamic parser registration loads source code, and workflow containers use a mounted Docker socket; these administrative surfaces need explicit trust and access boundaries.

This was a local review and synthetic verification, not a platform security audit. The full test suite, PostgreSQL integration, Docker and Kubernetes deployment were not run. No paid models, real MCP servers or enterprise tools were called, and no load or RAG-quality benchmark was measured.

## How should this be used as a learning project?

Begin with the model and session components associated with chapters three and four. Trace how a request obtains context, receives a response and saves history. Default in-memory storage supports development, but durable memory across process restarts needs a persistent backend. An interface name cannot establish retention behavior.

Next, inspect the chapter-five and chapter-six data, tool and policy components. Use a controlled document collection to evaluate chunking and retrieval. Point tools at a mock endpoint under your control and exercise allow, deny, failure, timeout and retry paths. Establish that each signal is meaningful before connecting company documents and credentials.

Then study observation, experimentation and workflows, and use Claw to see their composition. An HTTP 200 response is insufficient for a real application: answers need evidence, actions must avoid unintended repetition, costs need attribution and failures need recovery. Instrumentation and independent evaluation belong alongside feature development.

![Little M replaces simulated reference actions with verified integrations before deployment acceptance](../../assets/images/SLUG-fig-03.png)

A minimal source-study entry point is:

```bash
git clone https://github.com/designing-ai-systems/designing_ai_systems_repo.git
cd designing_ai_systems_repo
uv sync --frozen
uv run pytest tests/test_session_storage.py tests/test_credential_store.py -q
```

Check the current revision and dependency requirements first. This snippet does not configure accounts or execute real tools. Actual model calls require credentials, workflow-container examples require Docker, and PostgreSQL with pgvector is an additional storage setup. Treat uv as the entry to the Python environment, rather than a replacement for every scenario’s dependencies.

## FAQ

### Can the complete book be downloaded freely from this repository?

No complete book text or electronic-book files were found. The confirmed repository is the publisher-linked companion implementation. Use Manning’s reading options and confirm book and code terms separately.

### Can it take production traffic without adaptation?

It provides a substantial reference structure, but defaults and mock paths require inspection. Persistence, real embeddings, enforced approval and external integrations need acceptance checks in the target environment.

### Who should study it?

Python developers and architects moving from individual model calls to platform engineering. Readers wanting only a simple chat interface can start with one component rather than operating every service at once.

## Primary sources

Companion repository: https://github.com/designing-ai-systems/designing_ai_systems_repo
Manning title: https://www.manning.com/books/designing-ai-systems
Claw reference application: https://github.com/designing-ai-systems/designing_ai_systems_repo/tree/main/claw
Data Service: https://github.com/designing-ai-systems/designing_ai_systems_repo/blob/main/services/data/service.py
Tool Service: https://github.com/designing-ai-systems/designing_ai_systems_repo/blob/main/services/tools/service.py

This article’s license covers the original review and illustrations. The book and external code retain their own rights and terms.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
'''
desc='Designing AI Systems的Manning官方配套仓库把模型、会话、企业知识、工具、安全规则、观测与工作流做成共享平台。本文核对代码来源和授权信息，介绍Claw参考助手，运行87项上游测试与两项合成检查，说明占位向量、确认标记和模拟工具的实际边界，并给出从源码阅读到真实集成验收的学习路线，帮助开发者理解生产参考实现。'
enDesc='Explore Designing AI Systems’ official companion code, shared services, Claw assistant, 87 passing tests and two checks of embeddings and tool approval boundaries.'
f={'title':'Designing AI Systems：从模型调用走向共享AI平台','titleEn':'Designing AI Systems: Book and Companion Code Review','description':desc,'descriptionEn':enDesc,'wechatTitle':'AI平台怎么建？找到这本书的配套代码','wechatDigest':'核对官方仓库，实测87项测试与两项边界检查，分清参考实现和生产验收。','pubDate':'2026-11-08','updatedDate':'2026-11-08','category':'Tech-Experiment','tags':['AI工程','Manning','平台架构','Agent','Python'],'heroImage':'../../assets/images/'+s+'-banner.jpg'}
t='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in f.items())+'\n---\n\n'+cn.replace('SLUG',s)+'\n<!--EN-->\n\n'+en.replace('SLUG',s);Path('src/content/blog',s+'.md').write_text(t);print('descriptions',len(desc),len(enDesc))
