---
title: "OpenThai 2.0 OCR Markdown：从泰文文档到可追溯的结构化内容"
titleEn: "OpenThai OCR Markdown: Thai Documents into Structured Data"
description: "OpenThai 2.0 OCR Markdown 是面向泰英印刷文档的零点六三B开放权重模型，输出文本、HTML表格和版面坐标。本文找到官方权重与代码入口，核对 OpenMDW 许可、H100单页速度和不同评测口径，介绍 NVIDIA 服务端与苹果本地部署路径，并用后处理测试和合成样页验证工程接入边界。"
descriptionEn: "Find OpenThai OCR Markdown's official weights and code, examine H100 benchmark limits, and build Thai document workflows with layout, tables, and local checks."
wechatTitle: "OpenThai OCR：泰文表格怎样可靠入库"
wechatDigest: "0.63B模型可保留表格和版面，但一页1.6秒有硬件条件，识别结果仍需结构与业务校验。"
pubDate: "2026-11-12"
updatedDate: "2026-11-12"
category: "Tech-News"
tags: ["OpenThai", "泰文OCR", "文档解析", "开放权重", "本地部署"]
heroImage: "../../assets/images/openthai-ocr-markdown-thai-document-engineering-banner.jpg"
---

OpenThai 2.0 OCR Markdown 能把泰文和英文文档页转成保留表格与版面位置的结构化内容，适合扫描归档、知识库和文档处理流水线。

iApp Technology 于2026年11月12日介绍了这一模型。官方发布仓库在 Hugging Face：https://huggingface.co/iapp/OpenThai2.0-OCR-Markdown 。这里不仅有权重，也有推理、服务、后处理和测试代码；本次没有确认到另一个独立的 iApp GitHub 发布仓库，没必要为凑 GitHub 地址而指向无关项目。

## 它输出的为什么不只是文字？

普通 OCR 最容易丢掉的是关系：一个金额属于哪一行、哪一个合并表头覆盖了几列、多栏正文应该按什么顺序读。字符识别正确，结构仍可能错。

这个模型保留 NVIDIA Nemotron 3.5 Parse 的处理方式：按阅读顺序输出区块，包含类别和位置；正文用 Markdown，表格用支持 `rowspan`、`colspan` 的 HTML。模型卡列出的输入规格是将单页适配到1664×2048像素。

HTML表格不是装饰。跨行跨列无法可靠地塞进普通 Markdown 管道表格；如果入库时又把 HTML 拍平成文字，模型保留的关系就被下一环节丢掉了。工程上应同时保存原页、区块坐标、结构化表格和可读正文。

![小M把一张文档页分成文字、表格和坐标三份关联输出](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-01.png)

## 0.63B 模型由什么组成？

它是 Nemotron 3.5 Parse 的泰文微调版本，总参数630.8M：视觉编码器约439.0M，文本解码器约191.8M。发布的 float32 权重文件约2.52GB，官方服务采用 bfloat16。

这几个数字不能互换。参数量不等于下载体积，权重体积也不等于完整运行显存。模型卡所说“约8GB H100显存”对应官方服务配置和并发设置，不是所有8GB消费卡均已验证的保证。

## “1.6秒”和“95.2分”应该怎样理解？

以下均为发布方结果，本次没有复现 H100 或 Typhoon 的比较：

| 项目 | OpenThai | Typhoon OCR V2 2B | 应保留的条件 |
|---|---:|---:|---|
| th-docs-tables v1，65页 | 95.2 | 91.6 | 文本与表格联合评分；差值区间为 +1.2至+6.2 |
| ThaiOCRBench表格，193图 | 68.9 | 67.6 | TEDS；差异没有统计显著性 |
| 印刷文字，12组平均 | 90.3 | 89.6 | 字符准确率；差异没有统计显著性 |
| 新皇家公报，339页 | 98.7 | 94.6 | 对照PDF文字层；同类文档分布 |
| 单页中位耗时 | 1.6秒 | 15.8秒 | H100、12页串行；Typhoon使用eager模式 |

所以“约10倍”是这套环境中15.8除以1.6得到的相对值。官方明确说 Typhoon 在所用 vLLM 版本上需要 eager 模式，若可用 CUDA graphs 会更快；不能把它扩大成各种硬件、输入和并发下的固定差距。

皇家公报的339页来自训练结束后发布的新文件，这比只测旧文档更有说服力。但模型卡也说明：训练中已有早期公报，测试参考文字与训练标签使用相同工具产生。它测到了熟悉文档类型中的新文件表现，不等于验证了任意陌生版式。

另一个容易忽略的数字是68.9：在更一般的表格图集上，成绩远没有95.2那样整齐。官方还披露193张表格中，有21张输出不足原表80%的单元格。只看文字准确率，会漏掉这种结构性失败。

![小M把硬件、输入集、评分与并发条件贴在各自结果旁边](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-02.png)

## Linux 服务端如何接入？

以官方安装说明为起点，在独立环境下载发布物并安装它的 Python 包，再启动 vLLM。部署时应固定并记录模型 revision；本文研究快照为 `7a153712e5b50fac7e4a9d42ccf9ec41fb4202f0`。

```bash
hf download iapp/OpenThai2.0-OCR-Markdown \
  --revision 7a153712e5b50fac7e4a9d42ccf9ec41fb4202f0 \
  --local-dir OpenThai2.0-OCR-Markdown
pip install vllm==0.26.0
pip install -e ./OpenThai2.0-OCR-Markdown
vllm serve ./OpenThai2.0-OCR-Markdown \
  --served-model-name nemotron-parse --trust-remote-code
```

上面的安装路径按官方指南整理，本文没有在 NVIDIA 服务器上执行。`trust-remote-code` 会加载发布物代码，审阅并固定快照很有必要；不要在不明版本上直接开放生产服务。

客户端可用包内的解析器，而不是自己用正则拆模型输出：

```python
from nemotron_parse.inference import DocumentParser, GenerationError

with DocumentParser(base_url="http://localhost:8000/v1",
                    model="nemotron-parse") as parser:
    try:
        result = parser.parse("page.png", mode="single")
        markdown = result["markdown"]
    except GenerationError:
        # 将该页记为失败，进入复核队列，不能当作空白页成功入库
        raise
```

PDF需要先逐页渲染为图像；官方示例采用200 DPI。生产流水线还应给每页附上文件哈希、页码、模型版本和处理状态，让失败重跑不生成第二份互相冲突的记录。

## 苹果本地运行有哪些差别？

官方指南提供 Transformers 后端，Apple Silicon 使用 MPS 和 float32。它还明确采用贪心解码，并在提示前补换行，使提示 token 与服务端路径对应；这不是随意替换一条聊天提示就能保证等价。

官方在 M3 Max 的两个页面上分别测到约15.5秒和26.7秒。这些是少量样页数据，并非完整设备基准。相同权重经 Transformers 和 vLLM 执行，输出也可能稍有差别，不能直接继承服务端评测成绩。

## 我们实际验证了什么？

Mycelium Protocol 固定发布快照，先运行后处理、推理接口与批处理三组上游测试：86项通过。这些测试主要验证程序协议与转换逻辑，不是86页OCR准确率测试。

随后在 Apple M4、16GB内存、PyTorch 2.13.0、MPS float32 上加载实际权重，读取一页自行排版的泰英采购汇总表。使用官方指南的换行提示与贪心解码，8项关键检查通过：标题、英文标题、两条物品、总额、表格存在及跨行跨列结构。

这次首次单页解析约23秒，计时包含页面处理、生成和后处理，排除约3.6秒的模型加载；只有一次运行，没有构成可重复的速度基准，也未测PDF渲染或并发。样页规整、没有扫描噪声，不能据此估计真实文档字符准确率，更没有重跑官方 H100 比较。

人工查看原页与输出时，还看到部分泰文从单一码位写法变成视觉相近的分解序列。本文只报告上述关键检查，没有声称全文逐码位一致。做检索、去重或CER评分时，应明确 Unicode 与空白规范，并保留原始输出供复核。

## 数据工程师最值得借鉴什么？

第一是把文字监督和版面监督分开管理。官方训练说明中，文字来自精确标签，部分框与类别来自基础模型输出后再对齐；通过后处理回转检查，过滤不能还原为标签的目标。这比直接把另一个模型的整段回答当真值更可审计。

第二是针对重复输出单独建失败样本。发布方记录了先前微调的循环输出，并在循环片段上使用不似然损失。工程启发是保留失败轨迹、定位出问题的片段，而不是只往训练集里不断加“好例子”。这不意味着本文重跑了它的训练或已验证该方案普遍有效。

第三是让结构检查进入业务链路。表格至少检查行列、跨格和关键字段；财务与政务场景再核对金额、日期和数字体系。泰文数字偶尔被转成阿拉伯数字，竖排表头、短裁剪和针式打印也有已知薄弱点。原页与坐标能让人工复核直接跳到问题位置。

![小M把原页、版本和结构校验串进可重试的文档入库流水线](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-03.png)

## 许可、API与适用范围

权重及随附的 NVIDIA 代码文档按 OpenMDW-1.1 发布，tokenizer另有MIT许可。当前条文允许在遵守条件下使用和修改，分发时保留协议与适用声明；输出本身不受该协议额外限制。它不是一句“全仓MIT”，也不代表全部原始训练数据都随权重发布。

官方还有托管 Markdown API：`POST https://api.iapp.co.th/v3/store/ocr/document/markdown`。免费取得权重与使用商业API是两回事；API会把文件交给服务方处理，本地部署才是另一条数据路径。

完整手写页、场景文字和屏幕照片不是目标。若只要文字行而不需要表格结构，iApp另有 OCR Text 产品；它的体积、许可和速度不能混入本文这个 Markdown 模型的指标。

## 常见问题

### 能在普通电脑上复现一页1.6秒吗？

不能直接推断。这个数字来自 H100 上12页的串行测试；本地设备、后端、输入和解码设置都影响耗时。

### 是否找到了官方 GitHub 仓库？

本次确认的完整发布入口是 Hugging Face 模型仓库，内含代码和权重。没有确认另一个独立 iApp GitHub 仓库，不把无关地址当成来源。

### 输出表格能否直接用于财务计算？

应先校验结构和关键值。模型卡披露过丢单元格和数字混写，识别成功不等于业务数据已经可靠。

模型与代码：https://huggingface.co/iapp/OpenThai2.0-OCR-Markdown
官方发布：https://iapp.co.th/blog/openthai2p0-ocr-markdown-launch
运行指南：https://iapp.co.th/en/blog/openthai2p0-ocr-how-to-run
基础模型：https://huggingface.co/nvidia/Nemotron-3.5-Parse
许可：https://openmdw.ai/license/1-1/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

OpenThai 2.0 OCR Markdown converts Thai and English document pages into text, HTML tables, and positioned layout blocks. It is useful when a document pipeline must preserve relationships rather than extract words alone.

The official release is https://huggingface.co/iapp/OpenThai2.0-OCR-Markdown . iApp Technology introduced it on November 12, 2026. This Hugging Face repository includes inference, serving, postprocessing, tests, and weights; we did not establish a separate official iApp GitHub release repository.

## What does it preserve?

The Thai fine-tune retains NVIDIA Nemotron 3.5 Parse's reading order, block classes, and boxes. Pages are fitted to 1664×2048 pixels. Text becomes Markdown; tables use HTML with row and column spans.

Flattening those tables into plain text discards relationships again. Preserve the original page, geometry, table structure, and readable content together so a reviewer can trace a value back to its source.

![Little M links page text, tables, and coordinates](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-01.png)

## What does 0.63B mean for deployment?

The 630.8M parameters comprise a 439.0M vision encoder and a 191.8M text decoder. Published float32 weights occupy about 2.52 GB; the official server uses bfloat16.

Parameter count, download size, and runtime memory are different quantities. The approximately 8 GB H100 allocation in the model card describes a particular serving configuration, not validation on every 8 GB consumer GPU.

## How should the benchmarks be read?

These are publisher results, not our H100 or Typhoon reproduction:

| Evaluation | OpenThai | Typhoon OCR V2 2B | Qualification |
|---|---:|---:|---|
| th-docs-tables v1, 65 pages | 95.2 | 91.6 | Combined text/table score; difference interval +1.2 to +6.2 |
| ThaiOCRBench tables, 193 images | 68.9 | 67.6 | TEDS difference not significant |
| Printed text, 12 sets | 90.3 | 89.6 | Character-accuracy difference not significant |
| New Gazette pages, 339 | 98.7 | 94.6 | PDF text-layer reference; familiar document type |
| Median seconds per page | 1.6 | 15.8 | H100, 12 serial pages; Typhoon eager mode |

The approximately tenfold speed ratio belongs to this setup. The authors state that Typhoon requires eager mode on their vLLM version and would benefit from CUDA graphs if available. It is not a universal hardware or workload ratio.

The new Gazette documents postdate training, but earlier Gazette material was in training and the references share the training-label tool. This is new material from a familiar distribution rather than proof of arbitrary-layout generalization. The card also reports that 21 of 193 general table images retain fewer than 80% of their cells.

![Little M keeps hardware, dataset, scoring, and concurrency conditions beside each result](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-02.png)

## How do engineers connect it?

Use an isolated environment and pin the release revision. Our research snapshot is `7a153712e5b50fac7e4a9d42ccf9ec41fb4202f0`. The official Linux guide uses vLLM 0.26.0 and the package bundled with the model:

```bash
hf download iapp/OpenThai2.0-OCR-Markdown \
  --revision 7a153712e5b50fac7e4a9d42ccf9ec41fb4202f0 \
  --local-dir OpenThai2.0-OCR-Markdown
pip install vllm==0.26.0
pip install -e ./OpenThai2.0-OCR-Markdown
vllm serve ./OpenThai2.0-OCR-Markdown \
  --served-model-name nemotron-parse --trust-remote-code
```

These are documented deployment steps, not commands we ran on an NVIDIA server. Review remote code and keep its revision fixed. Use `DocumentParser` with box/class mode and `mode="single"`; catch `GenerationError` as a failed page instead of accepting an empty successful result.

Render PDFs page by page; the official example uses 200 DPI. Keep a file hash, page number, model revision, settings, and status so retries are traceable and do not create contradictory duplicate records.

## What changes on a Mac?

The official Transformers path uses MPS and float32, greedy decoding, and a leading newline matching the server's prompt tokenization. The authors report 15.5 and 26.7 seconds for two M3 Max pages, not a broad device benchmark. Backend differences can also change output, so identical weights do not automatically inherit the vLLM accuracy results.

## What did we verify?

Mycelium Protocol ran the pinned upstream postprocessing, inference-interface, and batch suites: 86 tests passed. These test program behavior, not OCR accuracy on 86 pages.

We then loaded the real weights on an Apple M4 with 16 GB memory, PyTorch 2.13.0, MPS, and float32, following the official greedy/newline prompt path. A self-authored Thai/English purchase page passed eight key checks: titles, two items, total, table presence, and row/column spans.

Its first single-page parse took about 23 seconds, including page processing, generation, and postprocessing, but excluding approximately 3.6 seconds of model loading. One run is not a repeatable speed benchmark; PDF rendering, concurrency, real scans, CER, H100, and Typhoon were not evaluated.

Some Thai output used visually similar decomposed Unicode sequences. Passing the key checks does not establish codepoint-identical transcription. Define Unicode and whitespace policies for search, deduplication, and CER while retaining raw output for review.

## What should data engineers borrow?

Separate exact text supervision from layout supervision and verify that postprocessing can reconstruct the target. The publisher obtains some layout labels from the base model, aligns them with exact text, and filters incompatible targets. That is more auditable than treating an entire generated answer as ground truth.

Keep failure traces as well as successful examples. The training recipe includes earlier repetition spans with an unlikelihood objective. We did not reproduce training or establish that this intervention transfers universally.

Validate table shape and business fields after recognition. Missing cells, rotated headers, mixed Thai/Arabic digits, short crops, and dot-matrix printing require targeted checks. Original-page geometry makes review practical.

![Little M connects originals, versions, checks, and retryable document ingestion](../../assets/images/openthai-ocr-markdown-thai-document-engineering-fig-03.png)

## License and scope

Weights and accompanying NVIDIA source/documentation use OpenMDW-1.1; the tokenizer has separate MIT terms. The current agreement permits use and modification subject to its conditions and retention of notices on redistribution. It places no additional restrictions on generated outputs. This is not a claim that the whole release is MIT or that all raw training data is included.

A hosted endpoint also exists: `POST https://api.iapp.co.th/v3/store/ocr/document/markdown`. Free weight downloads do not imply free hosted inference. Sending a document to that service and processing it locally are distinct data paths.

Full handwritten pages, scene text, and screen photos are outside the target. iApp's separate OCR Text product should not be confused with the Markdown model's size, license, or speed.

## FAQ

### Does 1.6 seconds apply to an ordinary laptop?

No. It is a median from twelve serial pages on an H100; device, backend, input, and decoding settings matter.

### Is there a verified official GitHub release?

The verified release is on Hugging Face and contains source and weights. We did not establish a separate official iApp GitHub repository.

### Can extracted financial tables be trusted immediately?

Validate structure and critical values first. The model card documents missing cells and digit substitutions.

Model and code: https://huggingface.co/iapp/OpenThai2.0-OCR-Markdown
Launch: https://iapp.co.th/blog/openthai2p0-ocr-markdown-launch
Run guide: https://iapp.co.th/en/blog/openthai2p0-ocr-how-to-run
Base model: https://huggingface.co/nvidia/Nemotron-3.5-Parse
License: https://openmdw.ai/license/1-1/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
