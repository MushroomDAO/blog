---
title: "AI 水印是怎么打进文字的，又是怎么被去掉的：watermarks-remover 三层解剖"
titleEn: "watermarks-remover-ai-provenance-c2pa-synthid-statistical-open-source"
description: "guillaumemeyer/watermarks-remover 开源了一套针对 Claude、Gemini SynthID、OpenAI 和开源模型的三层 AI 溯源标记清除方案：Layer A 消除不可见 Unicode 字符，Layer B 对统计采样水印做重写攻击，File 层剥离 PNG/JPEG/PDF/DOCX 等格式的 C2PA 和元数据。项目 2 天内获得 3000+ stars。文章从技术原理出发，拆解每种水印的工作机制和清除路径，以及这个话题背后的隐私与内容溯源之争。"
descriptionEn: "guillaumemeyer/watermarks-remover open-sources a three-layer system for stripping AI provenance marks from Claude, Gemini SynthID, OpenAI, and open-source models: Layer A removes invisible Unicode characters, Layer B attacks statistical sampling watermarks via rewriting, and the File layer strips C2PA and metadata from PNG/JPEG/PDF/DOCX and more. 3000+ stars in 2 days. This piece dissects how each watermark type works, how removal works, and the broader privacy vs. content provenance debate."
pubDate: "2026-08-13"
updatedDate: "2026-08-13"
category: "Tech-News"
tags: ["AI水印", "C2PA", "SynthID", "内容溯源", "隐私", "开源", "Python", "Mycelium"]
heroImage: "../../assets/images/watermarks-remover-ai-provenance-c2pa-synthid-statistical-open-source-banner.jpg"
author: "Mycelium Protocol"
---

*by Mycelium Protocol*

---

你用 Claude 写了一份方案文档，发给客户之前想知道：这份文字里有没有什么东西能被追踪回去？

这不是科幻问题。现代 AI 系统在输出的文字和图片里注入了可检测的信号，从不可见的 Unicode 字符，到统计层面的采样偏差，再到文件级别的 C2PA 溯源标准——每一层都有公开的技术规范，也都出现了对应的去除工具。

`guillaumemeyer/watermarks-remover` 是目前对这套体系覆盖最完整的开源项目，2 天内获得 3034 stars，300 forks。项目针对 Claude、Gemini/SynthID、OpenAI 和开源模型，分三层处理 AI 溯源标记。

GitHub：https://github.com/guillaumemeyer/watermarks-remover  
许可证：MIT  
最新版本：v0.3.2

---

## 三种水印，三种机制

### Layer A：Unicode 编辑类水印

最容易理解的一层：在文字里注入人眼不可见的 Unicode 字符。

常见的注入目标包括：
- **零宽空格（ZWSP）**：U+200B，插在单词之间
- **双向控制字符（bidi）**：改变渲染方向的控制符
- **标签字符（tag chars）**：U+E0000 区段的字符，在普通显示器上不可见
- **空格同形字**：看起来像空格但编码不同的字符

检测和清除都是确定性的，Python 标准库可以完成，不需要模型调用：

```bash
python3 skills/remove-ai-marks/scripts/inspect_text.py draft.md
python3 skills/remove-ai-marks/scripts/clean_text.py draft.md -o draft.cleaned.md --stats
```

`inspect_text.py` 会列出每个可疑字符的位置和 Unicode 码点；`clean_text.py` 执行去除并输出统计报告。这是整个项目里唯一可以「验证通过」的操作——你能看到被删了什么。

### Layer B：统计采样水印

这一层是 AI 水印研究的主战场，也是最难处理的。

背后的原理来自 Kirchenbauer 等人的论文（2023）和 Google 的 SynthID-Text（Nature 2024）。大语言模型生成文字时，每一步都在从一个概率分布里采样下一个 token。如果在这个采样过程中植入一个伪随机偏置——让某些 token 被稍微多选一点——那么在足够长的文字里，这个偏置的统计特征就能被检测到。

这个信号不在单个字符里，**分散在整个文本的 token 选择模式中**。改几个词、调整几个标点，几乎不能移动信号。

有效的攻击方式是**大规模改写**，也就是 Layer B 做的事：

```bash
# 默认只输出改写 prompt（不调用模型）
python3 scripts/rewrite_text.py draft.md --backend print-prompt --strength paraphrase

# 配合本地 Ollama（默认只允许 loopback，远程端点需要显式开启）
WATERMARKS_REWRITE_BACKEND=ollama \
WATERMARKS_REWRITE_MODEL=llama3.2 \
  python3 scripts/rewrite_text.py draft.md -o draft.rewritten.md
```

v0.3.1 的更新让 Layer B 的攻击策略更具体：默认 `--strength paraphrase` 现在执行**词选择 + 句法攻击**，包括子句顺序、连接词、过渡词、句子边界、功能词的系统性替换。新增 `--strength humanize`（零次提示消除 AI 典型用语）和 `--strength code`（重写注释、文档字符串、本地变量名，保留公开 API）。

`--candidates N` 参数生成 N 个候选改写，用 bigram Jaccard 距离选出词汇差异最大的，并加入长度漂移保护。

**诚实的说明**：改写有代价。统计水印的信号分散在用词里，有效去除意味着大量句子必须改写，而改写必然降低原文的措辞质量。项目 README 里对此有一段罕见的坦诚：

> 如果计划无论如何都要用一个更便宜的模型来改写，为什么最初要付费用高级模型？直接用更便宜的模型生成，结果相同甚至更好。

Layer B 适合的场景是：你确实需要高级模型的推理和初稿质量，同时需要满足隐私或合规要求，愿意接受一次改写降低文字的流畅度。

### File 层：C2PA 和文件元数据

C2PA（Coalition for Content Provenance and Authenticity）是一套由 Adobe、微软、索尼等公司联合制定的内容溯源标准，已经被 Google（Gemini 图片）、Meta 和其他平台采用。

C2PA manifest 可以嵌入文件里（hard-bound）或通过远程 Content Credentials 链接关联（soft binding）。前者可以被清除；后者在文件层面去除后，原始内容仍然在 C2PA 网络里有记录。

支持的格式：

| 格式 | 处理内容 |
|------|----------|
| PNG / JPEG | C2PA chunk / APP11 / AI XMP hints |
| SVG | `<metadata>`、XMP 块 |
| PDF | 字节/XMP，建议搭配 exiftool |
| DOCX | docProps / customXml |
| ODT | meta.xml 生成器信息 |
| HTML | meta 标签、JSON-LD、data-ai* 属性 |
| Markdown | YAML frontmatter 中的 AI 相关字段 |

```bash
python3 skills/remove-ai-marks/scripts/inspect_file.py photo.png
python3 skills/remove-ai-marks/scripts/clean_file.py photo.png -o photo.cleaned.png
```

---

## SynthID 像素水印：检测但不去除

Google 的 SynthID 对图片有两套方案：文字水印（统计采样，Layer B 覆盖）和像素域水印（不可见的频域修改，类似传统隐写术）。

像素域水印的去除超出了这个项目的范围——项目文档里明确说明了这一点。但 v0.3.0 集成了一个可选的本地 SynthID 评分器（基于外部项目 `aloshdenny/reverse-SynthID`），可以对图片进行置信度评分：

```bash
# 一键引导（无 Docker）
bash skills/remove-ai-marks/scripts/setup_synthid.sh

# 评分
REVERSE_SYNTHID_DIR=~/reverse-SynthID \
  ~/reverse-SynthID/.venv/bin/python \
  skills/remove-ai-marks/scripts/score_synthid.py shot.png
```

评分使用 v4 频谱码本（`artifacts/spectral_codebook_v4.npz`，约 220MB）。这是检测，不是去除。

---

## 覆盖矩阵

| 水印类型 | Claude | Gemini/SynthID | OpenAI | 开源 LLM |
|----------|--------|----------------|--------|----------|
| Unicode / 编辑类 | Layer A | Layer A | Layer A | Layer A |
| 统计采样类 | Layer B 尽力而为 | Layer B 尽力而为 | Layer B（如存在）| Layer B 尽力而为 |
| C2PA / 文件元数据 | 支持的格式 | 存在时支持 | 存在时支持 | 存在时支持 |
| 像素域水印 | 超出范围 | 仅可选评分，不去除 | 超出范围 | 超出范围 |

---

## 去不掉的残余风险

这是整个项目里最重要的声明：**这个工具无法认证「官方检测器会失败」**。

报告分两类：
- **可验证的**：Unicode 字符计数、元数据操作——这些有明确的输入和输出
- **尽力而为的**：Layer B 统计水印改写——改写可以降低信号强度，但没有公开的通用检测器可以验证结果

如果需要检查残余信号，项目建议：
- C2PA 用 `c2patool` 或 Content Credentials 官方验证工具
- SynthID 图片用 Google 的官方检测器（如果 Vertex AI 提供）或本地评分器
- 统计文字水印：目前无公开的通用检测器

---

## 安全加固（v0.3.2）

v0.3.2 是一个纯安全版本，修复了几个值得关注的问题：

**原子写入**：所有 cleaner 现在先写临时文件再原子重命名，拒绝符号链接目标。这防止了在 `/tmp` 等目录里预置符号链接劫持写入的攻击。

**HTTP 客户端加固**：`rewrite_text.py` 拒绝所有重定向（防止 API Key 通过 Authorization 头流向未验证的主机），非 loopback 端点默认拒绝，只接受 `http(s)` 协议，`--api-key` 参数被移除（密钥只通过环境变量 `WATERMARKS_REWRITE_API_KEY` 传入）。

**资源上限**：默认最大输入从 1GB 降至 256MB，新增 64MB stdin 上限，DOCX/ODT zip 预算从 512MB 降至 128MB，对外部工具子进程设置 `RLIMIT_AS` / `RLIMIT_FSIZE`。

**供应链**：CI Actions 用 SHA 固定，新增 CodeQL 工作流，`pip-audit` 步骤，Docker 镜像改为非特权用户。

---

## 为什么这个话题值得关注

AI 水印和内容溯源是接下来几年会持续升温的议题。欧盟 AI 法案第 50 条、美国 SB 942 等法规都在推动 AI 生成内容的标记要求。C2PA 已经在 Gemini、部分 Adobe 产品和 Bing Image Creator 里落地。

这个项目的出现提示了几件事：

**水印不是万能的**。统计水印在理论上很优雅，但文字是可以改写的，而改写会破坏信号。学术文献里已经有「沙中水印——生成模型强水印的不可能性」这样的研究（Zhang et al., ICML 2024）直接质疑这类方案的可靠性。

**元数据去除是一把双刃剑**。EXIF 去除在摄影圈已经存在几十年，C2PA 清除是同一件事的新版本。隐私和溯源之间的张力不会因为标准更新而消失。

**工具的存在推动了更强的水印研究**。每次一个新的去除工具出现，都会刺激水印方案的改进——像素域水印、硬绑定 C2PA、软绑定都是这种军备竞赛的结果。

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## How AI Watermarks Get Into Text — and How They Get Removed: A Three-Layer Anatomy of watermarks-remover

*by Mycelium Protocol*

---

You wrote a proposal document with Claude and want to know before sending it to a client: is there anything in this text that could be traced back to its origin?

This isn't a science fiction question. Modern AI systems embed detectable signals in their text and image outputs — invisible Unicode characters, statistical biases in token sampling, and file-level C2PA provenance standards. Each layer has public technical specifications, and each has spawned removal tools.

`guillaumemeyer/watermarks-remover` is the most complete open-source project covering this system. It earned 3,034 stars and 300 forks in two days. It targets Claude, Gemini/SynthID, OpenAI, and open-source models across three removal layers.

GitHub: https://github.com/guillaumemeyer/watermarks-remover  
License: MIT  
Latest: v0.3.2

---

### Three Watermarks, Three Mechanisms

**Layer A: Unicode edit-based watermarks.** The most straightforward layer: invisible Unicode characters embedded in text. Common targets include zero-width spaces (U+200B), bidirectional control characters, tag characters (U+E0000 range, invisible on standard displays), and space homoglyphs that look like spaces but have different encodings.

Detection and removal are deterministic. Python stdlib is sufficient; no model calls required. `inspect_text.py` lists every suspicious character with its Unicode codepoint and position. `clean_text.py` removes them and outputs a statistics report. This is the only operation in the whole project that can claim "verified removal" — you can see exactly what was deleted.

**Layer B: Statistical sampling watermarks.** This is the main battleground of AI watermarking research, and the hardest layer to address.

The underlying mechanism comes from Kirchenbauer et al. (2023) and Google's SynthID-Text (Nature, 2024). When a language model generates text, it samples the next token from a probability distribution at each step. If a pseudo-random bias is planted in that sampling process — nudging certain tokens to be selected slightly more often — a detectable statistical signature accumulates across sufficiently long text.

The signal doesn't live in any individual character. **It's distributed across the pattern of token choices throughout the entire text.** Changing a few words or adjusting punctuation barely moves the signal.

The effective attack is **large-scale rewriting** — what Layer B does. v0.3.1 sharpened the attack strategy: the default `--strength paraphrase` now executes a **word-choice + syntax attack**, systematically replacing clause order, connectors, transition words, sentence boundaries, and function words. New modes include `--strength humanize` (zero-shot targeting of formulaic AI-style phrasing) and `--strength code` (rewrites comments, docstrings, and local identifier names while preserving public API names).

The `--candidates N` flag generates N rewrites and selects the most lexically diverged using bigram Jaccard distance, with a length-drift guard.

**The honest caveat**: rewriting has costs. The statistical watermark signal is distributed across word choices, so effective removal requires rewriting a large fraction of sentences — and every rewrite replaces the original word choices with the rewriting model's, flattening tone, voice, and precision. The README puts it plainly:

> If the plan is to rewrite the text with a cheaper model anyway, why pay for a premium model in the first place? Generating directly with the cheaper model is simpler, cheaper, and produces the same — or better — end result.

Layer B makes sense when you specifically need the premium model's reasoning and drafting quality, and are willing to accept a rewrite pass to satisfy a privacy or compliance requirement — not as a cheap route to mark-free text.

**File layer: C2PA and file metadata.** C2PA (Coalition for Content Provenance and Authenticity) is a provenance standard jointly developed by Adobe, Microsoft, Sony, and others, now adopted by Google (Gemini images), Meta, and other platforms. A C2PA manifest can be embedded in a file (hard-bound) or linked via a remote Content Credentials reference (soft binding). The former can be stripped; after stripping the latter, the original content still has a record in the C2PA network.

Supported formats span PNG/JPEG (C2PA chunks, AI XMP hints), SVG (`<metadata>`, XMP), PDF (byte/XMP, exiftool preferred), DOCX (docProps, customXml), ODT (meta.xml), HTML (meta tags, JSON-LD, data-ai* attributes), and Markdown (AI keys in YAML frontmatter).

---

### SynthID Pixel Watermarks: Detection Only

Google's SynthID has two modes for images: text watermarking (statistical sampling, covered by Layer B) and pixel-domain watermarking (imperceptible frequency-domain modifications, similar to traditional steganography). Pixel-domain removal is explicitly out of scope.

v0.3.0 integrated an optional local SynthID scorer (from external project `aloshdenny/reverse-SynthID`) that reports a confidence score on an image — detection, not removal. V4 scoring uses a spectral codebook (~220 MB from the upstream checkout). The scorer is not bundled; it loads at runtime from your local checkout, staying under the upstream project's non-commercial Research License.

---

### What Residual Risk Remains

The most important statement in the project: **this tool cannot certify that vendor detectors will fail.**

Reports fall into two categories: verifiable (Unicode character counts, metadata actions — these have clear inputs and outputs) and best-effort (Layer B statistical watermark rewriting — rewriting degrades the signal but there is no public universal detector to verify the result).

For those who want to check residual signals themselves, the project points to `c2patool` or the Content Credentials official verify tool for C2PA, Google's official SynthID detector (where offered via Vertex AI) or the local scorer for pixel marks, and notes that no public universal detector currently exists for statistical text watermarks.

---

### Security Hardening in v0.3.2

v0.3.2 is a pure security release. Notable fixes: atomic writes via temp-file + atomic rename, refusing symlinked destinations (closes a symlink-placement attack where a pre-placed link in `/tmp` could redirect output to an arbitrary path); HTTP client hardening that refuses all redirects (preventing API key leakage via Authorization header to unvalidated hosts), denies non-loopback endpoints by default, and removes `--api-key` entirely (keys only via `WATERMARKS_REWRITE_API_KEY` env var); resource caps (max input 256 MiB, 64 MiB stdin, 128 MiB for DOCX/ODT zips, `RLIMIT_AS`/`RLIMIT_FSIZE` on external subprocess calls); CI actions SHA-pinned, CodeQL workflow added, `pip-audit` step, Docker image runs unprivileged.

---

### Why This Topic Matters

AI watermarking and content provenance are issues that will keep heating up. The EU AI Act Article 50 and US SB 942 both push toward mandatory labeling of AI-generated content. C2PA is already live in Gemini, parts of Adobe's product line, and Bing Image Creator.

This project's appearance signals a few things:

**Watermarks aren't infallible.** Statistical watermarks are elegant in theory, but text can be rewritten, and rewriting disrupts the signal. Academic literature already includes "Watermarks in the Sand: Impossibility of Strong Watermarking for Generative Models" (Zhang et al., ICML 2024), which directly challenges the reliability of such schemes.

**Metadata removal is a familiar tension.** EXIF stripping has existed in photography for decades. C2PA removal is the same operation with updated specifications. The tension between privacy and provenance doesn't disappear because the standard is newer.

**Tools like this drive stronger watermarking research.** Every new removal tool stimulates improvements in watermarking — pixel-domain marks, hard-bound C2PA, soft binding are all products of this arms race.

The underlying question this project surfaces is real: **who owns the provenance record of text you generate?** The answer affects journalists, legal professionals, researchers, anyone who pays for AI assistance and doesn't want that assistance to be permanently visible in what they produce.

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
