---
title: "PageSift：Rust 爬虫如何服务 AI，性能数字又该怎样读？"
titleEn: "PageSift: A Rust Crawler for AI, Beyond the Headlines"
description: "PageSift 是面向 AI 数据流水线的 Rust 爬虫与内容提取工具，提供 Markdown、SDK 和兼容接口。本文找到官方仓库，拆解有界队列、选择性渲染与部署路径，区分任务吞吐、成功网页和有效文档，并在 Mac 上验证 Python 包的离线转换和公开页面抓取，说明版本、参数、许可证与真实运行边界。"
descriptionEn: "PageSift offers Rust crawling and content extraction for AI. We audit benchmark denominators, SDK versions and deployment, with a Python smoke test on a Mac."
wechatTitle: "PageSift：Rust爬虫的数字怎么读"
wechatDigest: "找到官方仓库并在Mac跑通，拆解任务吞吐、有效文档和SDK版本差异。"
pubDate: "2026-10-26"
updatedDate: "2026-10-26"
category: "Tech-News"
tags: ["PageSift", "Rust", "爬虫", "数据提取", "RAG", "开源工具"]
heroImage: "../../assets/images/pagesift-rust-crawler-banner.jpg"
lastPublishedAt: "2026-10-26T00:50:05Z"
---

PageSift 是面向 AI 数据流水线的 Rust 爬虫与内容提取工具，可以把网页变成 Markdown 和结构化结果。它值得关注的是采集、清洗与资源控制如何衔接；选型时则需要把“处理了多少任务”与“拿到了多少有效文档”分开。

按你给出的 “a crawler” 描述，对应仓库是 **YOLOW92/pagesift**。另有 `joeychilson/pagesift` 同名 Go 项目，其说明明确不做爬虫，本文不把二者混在一起。

官方仓库：https://github.com/YOLOW92/pagesift

资料截止 2026-10-26，固定提交 `e6dca8e476bf69ef8d6e7d238874a136966b4cd5`。仓库 README 标注 0.70.0，本文实际运行的 Python 发布包为 0.20.0。Mycelium Protocol 完成了 Mac 上的基础功能验证，没有复现大规模吞吐、内存峰值或浏览器渲染性能。

## PageSift 解决数据链路的哪一段？

它处在“取得页面”和“交给模型”之间：请求内容、提取主体、生成 Markdown，并按需返回链接、图片地址和元数据。仓库还提供多页采集、文档处理和供 Agent 接入的服务接口。

这一步经常决定后面的模型是否在读正确材料。如果把导航、广告、页脚和空壳都送进知识库，检索效果差未必是向量模型的问题。

PageSift 不负责替使用者证明网页内容真实，也不会因为输出了 Markdown，就自动得到适合入库的资料。仍要记录原始 URL、时间、状态、提取结果与失败原因。

![小M把杂乱网页中的正文筛出来，将导航等周边材料分开](../../assets/images/pagesift-rust-crawler-fig-01.png)

## 为什么强调有界队列和选择性渲染？

一个站点可能不断发现新链接，慢页面又可能长期占住工作槽。如果发现速度持续快于处理速度，采集队列、浏览器和待保存结果会一起推高内存。

官方采用有界 frontier、背压和按主机控制并发等设计，目标是让资源压力反过来限制任务进入。0.70 的发布说明进一步描述了 NUMA 本地执行、HTTP 数据通路和读取 cgroup 内存上限的容量控制。

这些是架构目标与上游说明，不等于任何页面规模下都不会耗尽资源。特别是主进程 RSS、浏览器进程、容器内存和输出保留量，必须分别核对。

动态页面也不应全部按静态 HTML 处理。仓库描述了选择性渲染路线：先判断是否需要 JavaScript，再进入浏览器路径。这能减少不必要的开销，但仍依赖对应环境，并不保证延迟注入、登录后交互或所有 SPA 都能完整抓到。

0.70 发布说明：https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/docs/releases/0.70.0.md

## “百万页每秒”是在测什么？

官方 0.70 的饱和测试报告了 192 vCPU 上约 947,611 次每秒、2 亿任务、211.1 秒、峰值 RSS 888.1MiB。这属于本地合成负载的饱和测试，不能当成从公网采集同等数量有效文章的速度。

对知识库更有意义的，是另一份 0.60 公网报告中的不同计数：

| 报告字段 | 官方记录 |
|---|---:|
| 总处理任务 | 100,000,000 |
| HTTP 200 成功捕获 | 314,170 |
| 有效富文本 Markdown | 199,422 |
| 总耗时 | 2,373.9 秒 |
| 主机 | 80 vCPU、157GiB 内存的云主机 |

按这些字段直接做算术，HTTP 200 约为每秒 132 次，有效 Markdown 约为每秒 84 份。有效 Markdown 占报告总任务约 0.199%，占 HTTP 200 约 63.48%。

这些派生值只是对作者报告重新计算，没有经过我们的独立复测；它们也不是每个网站上的成功率预测。报告列出的错误类别没有完整解释全部一亿任务，尚不足以据此重建每个任务的生命周期。

因此，同一场运行可以同时有很高的任务处理吞吐和低得多的有效文档产出。前者体现调度、失败处理等工作，后者更接近知识库实际得到的东西。评估成本时，要先决定自己需要哪一个分母。

![小M分别清点调度任务、HTTP成功页面和可用文档三个篮子](../../assets/images/pagesift-rust-crawler-fig-02.png)

公网报告：https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/docs/benchmarks/0.60_p4_wild_x_2_showdown.md

## 内容提取质量也不能只看一个总分

当前 README 包含多组提取、PDF、动态渲染、结构化数据等测试，也同时出现不同数据集和评分口径。ROUGE、F1、召回率与场景成功数回答的是不同问题，不能拼成一个统一总榜。

官方列出的动态渲染对比中，PageSift 为 3/7 个场景，Playwright 为 5/7。这个结果本身就提示：静态页面提取快，不代表交互页面覆盖最广。

实用的验收方式是拿自己的资料类型做小样本：正文有没有截断，表格是否保留，PDF 是否丢掉公式，页面是否只是登录或验证提示。同一个抓取请求返回 200，也可能完全没有用户要的内容。

## Mac 上实际跑通了什么？

我们使用 M4 Mac、macOS 26.6.2、Python 3.12.14，在隔离虚拟环境中安装 `pagesift==0.20.0`，没有给博客项目增加依赖。

第一个检查不访问网络：把带有导航、正文和脚本标记的 HTML 交给 `pagesift.convert`。输出保留了正文中的唯一标记和页面标题，没有包含脚本标记。

第二个检查访问一个公开博客页面。结果状态为 200，引擎为 `http`，提取出的 Markdown 包含预期内容，元数据是 Python 字典。这验证了基本提取路径，不是速度或内存基准。

本机验证过的写法是：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install 'pagesift==0.20.0'
```

```python
import pagesift

doc = pagesift.scrape(
    "https://example.com/",
    formats=["markdown"],
    timeout=25000,
)
print(doc.markdown)
print(doc.metadata.get("title"))

# 已经持有 HTML 时，不必再请求网络。
converted = pagesift.convert(
    "<article><h1>Example</h1><p>Article content.</p></article>",
    url="https://example.com/",
)
```

这里 `timeout` 的单位是毫秒。Python 0.20.0 中，`metadata` 已作为结果字典提供，不能把它作为 `formats` 值传入；实际调用会得到 `UnsupportedOption`。结果字典也不能照顶层 README 的另一处示例写成 `doc.metadata.title`。

这正是为什么要分别记录仓库版本和安装包版本。本文没有将 0.20.0 的本机验证扩展为 0.70.0 所有能力都已测试。

Python 包说明：https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/crates/pagesift-py/README.md

发布包：https://pypi.org/project/pagesift/0.20.0/

## 怎样接入已有 Agent 或采集系统？

Python SDK 适合先做单页或固定 URL 列表的采集。需要复用连接池、robots 缓存和主机限速状态时，官方建议复用一个 `Scraper`，而不是每页新建一个。

需要发现链接并持续遍历，或使用新采集核心时，优先核对对应版本的 Rust / CLI 文档。不能把 Python 包的某个入口存在与否，当成整个项目能力的结论。

已有服务链路可以评估自托管 API。官方 Docker 示例使用 3002 端口，并配置 API key：

```sh
docker run -d -p 127.0.0.1:3002:3002 \
  -v pagesift-data:/data \
  -e PAGESIFT_API_KEYS=replace-with-your-key \
  ghcr.io/yolow92/pagesift:0.70.0
```

这是按官方示例整理的部署方式，本文没有实际启动该容器。仓库还宣称兼容 Firecrawl v1/v2、Jina Reader 路线和 MCP；接入前仍要核对所用端点、参数、认证和返回结构，不能把“兼容”理解为所有 API 行为完全等价。

![小M只在处理台有空位时放入新任务，动态页面另走需要浏览器的通道](../../assets/images/pagesift-rust-crawler-fig-03.png)

## 登录页、反爬与许可证的边界

PageSift 的官方定位是遵守 robots.txt 与主机限速，并报告访问障碍。它不是验证码解决器、账号登录替身或付费内容解锁器。把一个返回登录页的 URL 转成 Markdown，不代表完成了正文抓取。

在一次独立的小红书来源核查中，公开抓取只返回了登录页。这样的结果只能记为来源不可用，不能算有效文章；本文没有测试 PageSift 抓取该笔记。

许可证方面，仓库提供 AGPL-3.0-only 与商业授权选项。官方商业说明区分内部使用、修改后对外提供服务及闭源分发等情况。采购或嵌入产品前，应按自己的交付方式阅读许可证和商业条款，而不是把“可自托管”直接理解为没有后续义务。

商业授权说明：https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/COMMERCIAL.md

## 选型时先做一个小验收

先拿十几到几十个真实目标页面，记录请求状态、正文完整性、有效文档率、每份有效文档的耗时与资源消耗。把浏览器页面与静态页面分开，把原始采集内容与后续 Agent 指令分开。

如果这些页面能稳定取得所需字段，再逐步扩大范围，观察并发、主机限速、队列、磁盘输出与失败恢复。PageSift 值得试的方向是把采集和提取做成可控的数据基础设施，真正的判断标准是最终留下来的资料是否可用。

## 常见问题

### 哪个 PageSift 是这里介绍的爬虫？

是 `YOLOW92/pagesift` 的 Rust 项目。同名的 `joeychilson/pagesift` 定位不同，不能混用安装方式与功能说明。

### Python 0.20.0 和仓库 0.70.0 是同一套已验证功能吗？

不是。本文只在发布的 Python 0.20.0 上做了离线转换和公开网页提取。Rust、CLI、服务和浏览器路径需要分别验证。

### 每秒处理很多任务，意味着拿到同样多有效文章吗？

不是。任务完成、HTTP 成功和有效提取是三种计数。需要根据业务目标选择分母，并保留失败和空壳页面的记录。

封面来自 PageSift 官方仓库的标志图形，相关品牌与图形权利归原作者，不属于本文文字的 CC 授权范围。

原文与后续更新：https://blog.mushroom.cv/blog/pagesift-rust-crawler/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

PageSift is a Rust crawler and content-extraction tool for AI data pipelines. It turns pages into Markdown and structured results, but evaluating it requires separating processed tasks from successful pages and useful documents.

The crawler matching the request is `YOLOW92/pagesift`. The similarly named `joeychilson/pagesift` is a different Go project whose documentation explicitly excludes crawling.

Repository: https://github.com/YOLOW92/pagesift

Research cutoff: October 26, 2026, pinned to `e6dca8e476bf69ef8d6e7d238874a136966b4cd5`. The repository README says 0.70.0; our local test used the published Python package 0.20.0. Mycelium Protocol did not independently reproduce large-scale throughput, peak memory or browser performance.

## Where does PageSift fit?

It works between retrieving a page and supplying content to a model: fetch content, identify the main body, produce Markdown and optionally return links, image URLs and metadata. The repository also offers multi-page collection, document handling and agent-facing interfaces.

This matters because navigation, advertising and empty shells can undermine retrieval before a model sees the material. Markdown output does not establish factual truth or readiness for indexing. Preserve the source URL, time, status, extraction result and failure reason.

![Xiao-M sifts article content from navigation and other surrounding page material](../../assets/images/pagesift-rust-crawler-fig-01.png)

## Why bounded queues and selective rendering?

Link discovery can outpace processing, while slow pages occupy worker capacity. Unbounded queues, browser instances and retained results can grow memory together.

The project describes a bounded frontier, backpressure and per-host concurrency control. Its 0.70 release adds NUMA-local execution, a specialized HTTP data path and capacity decisions informed by cgroup memory limits.

These are architecture descriptions and upstream claims, not guarantees against every resource failure. Process RSS, browsers, container usage and retained output require separate accounting.

Selective rendering aims to use a browser only when JavaScript is needed. It still needs an appropriate environment and does not establish full support for delayed content, authenticated interactions or every SPA.

Release details: https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/docs/releases/0.70.0.md

## What does nearly a million pages per second measure?

The official 0.70 saturation result reports 947,611 operations per second on 192 vCPUs, 200 million tasks, 211.1 seconds and 888.1MiB peak RSS. This is a local synthetic workload, not equivalent public-web article retrieval.

A separate 0.60 public-run report makes the denominator issue concrete:

| Report field | Author's figure |
|---|---:|
| Processed tasks | 100,000,000 |
| Successful HTTP 200 captures | 314,170 |
| Rich Markdown documents | 199,422 |
| Wall time | 2,373.9 seconds |
| Host | 80 vCPUs, 157GiB RAM |

Arithmetic on those reported fields gives approximately 132 HTTP 200 captures per second and 84 useful Markdown documents per second. Useful documents represent about 0.199% of reported tasks and 63.48% of HTTP 200 responses.

These are derived figures from the author's report, not our benchmark or a predicted success rate for another site. The listed error categories do not account for the entire task count, so they are insufficient to reconstruct every task's lifecycle.

High task-processing throughput and much lower useful-document output can therefore coexist. Choose the denominator that reflects the pipeline's actual purpose.

![Xiao-M counts scheduled tasks, successful responses and useful documents separately](../../assets/images/pagesift-rust-crawler-fig-02.png)

Public-run report: https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/docs/benchmarks/0.60_p4_wild_x_2_showdown.md

## How should extraction quality be assessed?

The README contains multiple datasets and scoring methods across text, PDF, rendering and structured extraction. ROUGE, F1, recall and successful scenarios cannot form one interchangeable leaderboard.

Its dynamic-rendering comparison reports 3/7 scenarios for PageSift and 5/7 for Playwright. Fast static extraction does not establish the broadest interactive coverage.

Test your own sources: truncated text, missing tables, lost PDF formulas and login shells are different failures. HTTP 200 alone does not establish retrieval of the requested content.

## What worked on our Mac?

We installed `pagesift==0.20.0` in an isolated Python 3.12.14 environment on an M4 Mac running macOS 26.6.2. No blog dependencies were changed.

Offline conversion retained a unique article marker and title while omitting a script marker. A public-page scrape then returned HTTP 200 through the `http` engine, with expected Markdown content and dictionary metadata. These are functional checks, not performance measurements.

The tested Python interface is:

```python
import pagesift

doc = pagesift.scrape(
    "https://example.com/",
    formats=["markdown"],
    timeout=25000,
)
print(doc.markdown)
print(doc.metadata.get("title"))
```

The timeout is in milliseconds. In Python 0.20.0, `metadata` is a result dictionary, not an accepted `formats` value. Passing it there raises `UnsupportedOption`; attribute-style `doc.metadata.title` is also inappropriate. Parts of the top-level README therefore need to be checked against the installed SDK version.

We did not extend this smoke test into a claim that all 0.70 repository features work locally.

Python documentation: https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/crates/pagesift-py/README.md

Published package: https://pypi.org/project/pagesift/0.20.0/

## How can it join an existing pipeline?

The Python SDK is a reasonable starting point for individual pages or known URL lists. Its documentation recommends reusing a `Scraper` to retain connection pools, robots caching and rate-limit state.

For link discovery and newer collection cores, check the corresponding Rust and CLI version. SDK packaging is not a reliable proxy for every repository capability.

For self-hosted service integration, the repository provides this Docker route, here bound to loopback:

```sh
docker run -d -p 127.0.0.1:3002:3002 \
  -v pagesift-data:/data \
  -e PAGESIFT_API_KEYS=replace-with-your-key \
  ghcr.io/yolow92/pagesift:0.70.0
```

We did not run that container. The project advertises Firecrawl v1/v2, Jina Reader and MCP interfaces; validate the exact endpoints, options, authentication and responses you depend on rather than assuming complete API equivalence.

![Xiao-M admits work only when capacity is free and sends dynamic pages to an optional browser](../../assets/images/pagesift-rust-crawler-fig-03.png)

## What are the access and licensing boundaries?

PageSift describes a policy of respecting robots.txt and host limits and reporting access barriers. It is not a substitute for account login, CAPTCHA handling or paid-content access. Converting a login page does not retrieve the underlying article.

A separate public-source check of a Xiaohongshu note returned only a login page. That establishes an unavailable source rather than a useful article. We did not test PageSift on that note.

The project offers AGPL-3.0-only and commercial licensing. Its commercial guide distinguishes internal use, modified public services and proprietary distribution. Review the actual license and your delivery arrangement before embedding it; self-hosting alone does not settle every obligation.

Commercial guide: https://github.com/YOLOW92/pagesift/blob/e6dca8e476bf69ef8d6e7d238874a136966b4cd5/COMMERCIAL.md

## What should a pilot measure?

Use a small set of real target pages. Record status, content completeness, useful-document rate and resource cost per useful document. Separate browser and static workloads, and keep captured content distinct from instructions an agent may execute.

Expand only after required fields are reliably extracted. Observe queue size, host limits, output storage and failure recovery. PageSift is worth evaluating as controllable collection infrastructure; useful retained material is the practical outcome.

## FAQ

### Which same-name repository is the crawler?

This article concerns the Rust project `YOLOW92/pagesift`. Do not mix its installation commands and feature claims with the different Go project `joeychilson/pagesift`.

### Does the Python smoke test validate all repository 0.70 features?

No. It covers published Python 0.20.0 conversion and a public static-page scrape. Rust, CLI, service and browser paths need their own checks.

### Are processed tasks equivalent to useful retrieved articles?

No. Task completion, HTTP success and useful extraction are distinct counts. Retain failures and empty shells, and choose a denominator aligned with your goal.

The cover uses PageSift's official repository logo. Branding and source-art rights remain with their owners and are excluded from the article's text license.

Canonical article: https://blog.mushroom.cv/blog/pagesift-rust-crawler/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
