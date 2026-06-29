---
title: "百度开源 Unlimited-OCR：一次扫完整本 PDF，票据单据智能化提速"
titleEn: "Baidu Open-Sources Unlimited-OCR: One-Shot Long PDF Parsing — Accelerating Business Document Digitization"
description: "百度开源 Unlimited-OCR（11K⭐，MIT），提出 Reference Sliding Window Attention（R-SWA）彻底解决长文档解析的 KV Cache 爆增问题：一次推理可扫完数十页 PDF，KV Cache 全程恒定不增长。支持 Transformers / vLLM / SGLang，对发票、合同、银行流水、报销单等商业票据的批量智能化处理具有决定性加速作用。"
descriptionEn: "Baidu open-sources Unlimited-OCR (11K⭐, MIT) with Reference Sliding Window Attention (R-SWA): parse dozens of PDF pages in a single forward pass with constant KV cache. Supports Transformers/vLLM/SGLang. A decisive accelerator for batch digitization of business invoices, contracts, bank statements, and expense receipts."
pubDate: "2026-06-28"
updatedDate: "2026-06-28"
category: "Tech-News"
tags: ["OCR", "文档解析", "百度", "PDF处理", "票据智能化", "开源", "vLLM", "SGLang", "FP技术"]
heroImage: "../../assets/images/unlimited-ocr-baidu-document-parsing-guide-banner.jpg"
---

> **一句话定位**：Unlimited-OCR 不是传统 OCR 的性能升级，而是范式切换——用 R-SWA 让 KV Cache 从随序列增长变成全程恒定，从此「整本 PDF 一次推理扫完」不是噱头，是实际可达的工程现实。

---

## 项目信息

GitHub：https://github.com/baidu/Unlimited-OCR （11,634 ⭐，MIT 开源）

论文：arXiv:2606.23050（2026-06-23）

HuggingFace：https://huggingface.co/baidu/Unlimited-OCR

ModelScope：https://modelscope.cn/models/PaddlePaddle/Unlimited-OCR

作者：百度 17 位工程师联署，Youyang Yin 主导

---

## OCR 的「长期困境」

过去几年，端到端 OCR 模型走出了一条清晰的技术路线：

```
传统分块 OCR（逐字符/逐行）
    ↓
神经网络 OCR（CNN+RNN 端到端）
    ↓
DeepSeek-OCR（LLM 作为解码器）
    ↓
DeepSeek-OCR-2
    ↓
Unlimited-OCR（本文主角）
```

用 LLM 做解码器带来了质量飞跃，因为语言模型的先验分布能理解上下文、纠正歧义字符。但随之而来了一个根本性的性能问题：

**KV Cache 随序列长度线性增长。**

你扫的文档越长，KV Cache 占的显存越多，生成速度越慢。扫一张图没问题，扫一份 100 页合同——要么显存爆了，要么你得把文档切成几十块分批处理，再把结果拼起来，精度和效率都受损。

百度的论文把这个问题说得很直白：

> *这与人类在长文本抄写任务中不会效率下降形成了鲜明对比。*

人类读 100 页文件，第 100 页的速度和第 1 页一样快。现有的 LLM-decoder OCR 做不到。

---

## 核心技术：R-SWA（参考滑动窗口注意力）

**Reference Sliding Window Attention** 是 Unlimited-OCR 的核心创新。一句话解释：

> **把解码器里所有注意力层替换为 R-SWA，使 KV Cache 在整个解码过程中保持恒定。**

### 传统 LLM 解码器的问题

```
传统 Self-Attention：
输出 Token 1 → KV Cache [k1, v1]
输出 Token 2 → KV Cache [k1, v1, k2, v2]
输出 Token N → KV Cache [k1, v1, ..., kN, vN]
          ↑
     随序列增长，显存爆炸
```

### R-SWA 的解法

R-SWA 的设计思路来自「模仿人类解析工作记忆」：人在抄写长文时，不会把前面所有内容全记住——而是维护一个固定大小的「工作记忆窗口」，参考当前视觉信息向前推进。

```
R-SWA：
解码窗口固定大小（sliding window）
+ 参考（Reference）机制锁定关键全局上下文
= KV Cache 全程恒定，不随序列长度增长
```

**效果**：结合 DeepSeek-OCR 编码器的高压缩率 + R-SWA 的恒定 KV Cache，**在标准 32K 最大长度下，一次 forward pass 可以转写数十页文档**。

### R-SWA 的通用性

论文特别强调 R-SWA 不只是 OCR 专用机制——它是**通用的解析注意力**，同样适用于：
- ASR（语音识别的长音频解码）
- 翻译（长文档翻译）
- 任何需要长序列解码的任务

这意味着这个技术组件未来会在更广泛的场景里出现。

---

## 两种推理模式

Unlimited-OCR 支持两种配置，根据场景选择：

| 模式 | 参数 | 适用场景 |
|---|---|---|
| **gundam** | base_size=1024, image_size=640, crop_mode=True | 单张图片，高精度细节扫描 |
| **base** | base_size=1024, image_size=1024, crop_mode=False | 多页/PDF，长文档批量处理 |

- **gundam 模式**：适合单张高密度票据（如增值税发票、报关单），crop_mode 开启会对图像做自适应裁剪，提升小字符识别精度
- **base 模式**：适合多页 PDF（合同、银行流水、招股书），image_size=1024 保持完整页面布局

---

## 三种部署方式

### 方式一：Transformers（最易上手）

```python
from transformers import AutoModel, AutoTokenizer
import torch

model = AutoModel.from_pretrained(
    'baidu/Unlimited-OCR',
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
).eval().cuda()

tokenizer = AutoTokenizer.from_pretrained('baidu/Unlimited-OCR', trust_remote_code=True)

# 单张票据（gundam 模式，高精度）
model.infer(
    tokenizer,
    prompt='<image>document parsing.',
    image_file='invoice.jpg',
    output_path='./output/',
    base_size=1024, image_size=640, crop_mode=True,
    max_length=32768,
)

# 多页 PDF（base 模式）
import fitz, tempfile, os

def pdf_to_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)
    tmp = tempfile.mkdtemp()
    paths = []
    for i, page in enumerate(doc):
        p = os.path.join(tmp, f'page_{i+1:04d}.png')
        page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72)).save(p)
        paths.append(p)
    return paths

model.infer_multi(
    tokenizer,
    prompt='<image>Multi page parsing.',
    image_files=pdf_to_images('contract.pdf'),
    output_path='./output/',
    image_size=1024, max_length=32768,
)
```

### 方式二：vLLM（高并发生产部署）

```bash
# CUDA 13.0（默认）
docker pull vllm/vllm-openai:unlimited-ocr

# Hopper GPU（H100/H800，CUDA 12.9）
docker pull vllm/vllm-openai:unlimited-ocr-cu129
```

完整部署细节见官方 Recipe：https://recipes.vllm.ai/baidu/Unlimited-OCR

### 方式三：SGLang（已支持 R-SWA 缓存优化，推荐生产）

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl
uv pip install kernels==0.11.7 pymupdf==1.27.2.2

# 启动服务器
python -m sglang.launch_server \
    --model baidu/Unlimited-OCR \
    --attention-backend fa3 \
    --context-length 32768 \
    --enable-custom-logit-processor \
    --host 0.0.0.0 --port 10000
```

SGLang 专门针对 R-SWA 做了缓存优化，是三种方式里内存效率最高的。批量处理可开 `--concurrency 8`。

---

## 为什么这对商业票据处理是「决定性加速」

这里要说一件在技术圈以外容易被忽视的事。

### 当前商业票据数字化的真实痛点

国内企业每年处理的票据量是天文数字：增值税发票、银行回单、合同、报销凭证、海关单据、医疗单据……绝大多数仍然是**纸质或扫描 PDF**，需要人工录入或分块 OCR 提取。

分块 OCR 的核心问题：

```
一份 50 页合同 → 切成 50 份单页 → 分别识别 → 人工/脚本拼接 → 后处理对齐
                                                       ↑
                                              这里经常出错：
                                              · 跨页表格断行
                                              · 页码逻辑丢失
                                              · 条款编号错位
                                              · 多列布局混乱
```

**根本原因**：传统 OCR 是无状态的，每一页都是独立的输入，不知道上下文。

### Unlimited-OCR 如何解决这个问题

**一次推理，整本文档作为一个整体处理。**

```
50 页合同 → 转成图片序列 → 一次 infer_multi → 完整结构化输出
                                    ↑
                              R-SWA 维持恒定 KV Cache
                              解码器始终知道整个文档上下文
                              跨页内容自然连通
```

这在以下几类场景产生决定性差异：

#### 1. 增值税发票批量入账

企业财务每月处理几百张发票，现有方案逐张识别 + 逐张校验。Unlimited-OCR 可以把一批发票图片打包一次处理，同时利用上下文检测异常（比如同一供应商不同发票的税率不一致、金额超出合理区间等）。

#### 2. 多页合同要素提取

法务审核 50 页合同，需要提取：甲方、乙方、金额、期限、违约条款、附件清单……传统分块 OCR 会在跨页段落、表格续页处出错。一次长程推理可以完整理解合同结构。

#### 3. 银行流水结构化

银行流水 PDF 通常 20-200 页，每行都是一条交易记录。分块处理容易漏行或重复识别跨页边缘的行。infer_multi 一次处理保证每条记录完整捕获。

#### 4. 医疗单据报销

医保报销涉及病历摘要 + 费用清单 + 处方单多个文件，传统方案各自独立 OCR，再人工关联。统一长程解析可以在一次推理里同时处理所有文件并保持语义连贯。

#### 5. 海关报关单 + 箱单 + 发票三单合一

外贸场景的三单核对（报关单、箱单、商业发票）需要字段级对齐。一次联合解析可以输出统一的对齐结构，而不是三份独立 OCR 结果再做后处理比对。

### 量化影响估算

| 指标 | 传统分块 OCR | Unlimited-OCR |
|---|---|---|
| 50 页 PDF 处理方式 | 50 次推理 + 人工拼接 | 1 次 infer_multi |
| 跨页内容连贯性 | 依赖后处理脚本 | 模型内原生保持 |
| 跨页表格识别准确率 | 通常 70-85% | 接近单页精度 |
| 开发集成复杂度 | 高（分块 + 拼接逻辑）| 低（一次调用）|
| 显存随页数增长 | 线性（或需分批）| 恒定（R-SWA）|

---

## 商业应用落地路线图

对想把 Unlimited-OCR 接入企业系统的开发者，建议的落地路线：

### 阶段一：单机验证（1 周）

```bash
# 用 Transformers 快速验证效果
pip install transformers torch pymupdf
python -c "
from transformers import AutoModel, AutoTokenizer
import torch
model = AutoModel.from_pretrained('baidu/Unlimited-OCR', 
    trust_remote_code=True, torch_dtype=torch.bfloat16).eval().cuda()
# 跑你们自己的样本发票/合同
"
```

### 阶段二：服务化部署（1-2 周）

用 SGLang 或 vLLM 包装成 OpenAI 兼容的 REST API：

```bash
# SGLang 批量处理接口
python infer.py \
    --pdf ./invoices/batch_202606.pdf \
    --output_dir ./results/ \
    --concurrency 8 \
    --image_mode gundam   # 单张发票用 gundam
```

### 阶段三：对接业务系统

输出结果是结构化文本（Markdown 或自定义格式），对接到：
- 财务系统（发票入账）
- ERP（合同要素录入）
- 报销平台（单据校验）
- 档案管理（文件分类归档）

---

## 与同类方案对比

| 方案 | 长文档能力 | KV Cache | 开源 | 许可证 |
|---|---|---|---|---|
| Unlimited-OCR | ✅ 数十页一次推理 | 恒定（R-SWA）| ✅ | MIT |
| DeepSeek-OCR-2 | 部分 | 线性增长 | ✅ | 自定义 |
| GOT-OCR | 有限 | 线性增长 | ✅ | Apache 2.0 |
| 商业 OCR API | 通常分页 | N/A（云端）| ❌ | 按量计费 |
| Tesseract | 无 LLM 上下文 | N/A | ✅ | Apache 2.0 |

Unlimited-OCR 目前是开源社区里**唯一**做到恒定 KV Cache 长程解析的端到端 OCR 模型。

---

## 技术演进视角：OCR 正在成为 AI 基础设施

把这次发布放在更长的时间线上看：

```
2020 前：OCR = 规则 + 传统CV，处理结构化表单
2022-2023：LLM 接入 OCR 解码器，开始理解非结构化文档
2024-2025：DeepSeek-OCR 系列，端到端质量大幅提升
2026：Unlimited-OCR，长程恒定推理，打通「任意长度文档」的处理瓶颈
```

**下一步会发生什么？**

当 OCR 能可靠处理任意长度的文档，它就不再只是「识别文字的工具」，而是**文档理解的基础设施层**：

- 财务自动化：发票入账、报销审核、账期管理全面无人工干预
- 法律科技：合同审查、条款提取、风险标注自动化
- 金融合规：反洗钱的交易记录核查、贷款文件审核
- 政务数字化：档案电子化、政务文件标准化处理

OCR 精度和长程能力的每一次突破，都直接转化为这些场景里「人工录入/审核时间」的缩减。Unlimited-OCR 这次突破不是渐进式优化，是**从「分块处理能用」到「整体理解可靠」的跃迁**。

---

## 快速开始

**1. HuggingFace Demo（无需 GPU，直接试用）**

https://huggingface.co/spaces/baidu/Unlimited-OCR

**2. 本地部署**

```bash
pip install transformers torch torchvision pymupdf einops addict easydict
python -c "
import torch
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained('baidu/Unlimited-OCR', trust_remote_code=True, torch_dtype=torch.bfloat16).eval().cuda()
tokenizer = AutoTokenizer.from_pretrained('baidu/Unlimited-OCR', trust_remote_code=True)
model.infer(tokenizer, prompt='<image>document parsing.', image_file='test.jpg', output_path='./out/', base_size=1024, image_size=640, crop_mode=True, max_length=32768, save_results=True)
"
```

**3. 资源汇总**

| 资源 | 地址 |
|---|---|
| GitHub | https://github.com/baidu/Unlimited-OCR |
| arXiv 论文 | https://arxiv.org/abs/2606.23050 |
| HuggingFace 模型 | https://huggingface.co/baidu/Unlimited-OCR |
| HuggingFace Demo | https://huggingface.co/spaces/baidu/Unlimited-OCR |
| ModelScope | https://modelscope.cn/models/PaddlePaddle/Unlimited-OCR |
| vLLM Recipe | https://recipes.vllm.ai/baidu/Unlimited-OCR |

---

## 总结

Unlimited-OCR 做对了一件关键的事：**把「长文档解析」的性能瓶颈从工程优化题变成了架构设计题**，用 R-SWA 从根本上解决了 KV Cache 随序列增长的问题。

对做文档处理、票据智能化、合规自动化的团队来说，这是今年最值得跑一遍 Demo 的模型。MIT 开源，代码和权重全部公开，HuggingFace 有在线 Demo，上手没有门槛。

欢迎试完来评论区分享测试结果——特别是长 PDF 和多页发票的效果，很想知道真实场景的表现。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接。

<!--EN-->

> **In one line**: Baidu open-sources Unlimited-OCR — R-SWA keeps KV cache constant regardless of sequence length, enabling one-shot parsing of entire multi-page PDFs. This is a decisive accelerator for business document digitization: invoices, contracts, bank statements, and expense receipts processed as complete documents instead of disconnected page chunks.

---

## What Is R-SWA?

**Reference Sliding Window Attention** replaces all attention layers in the decoder:
- Standard self-attention: KV cache grows linearly with sequence length → memory explosion for long docs
- R-SWA: KV cache stays **constant** throughout decoding, regardless of document length
- Result: dozens of pages parsed in **one single forward pass** at 32K max length

This is how Unlimited-OCR emulates human parsing working memory — we don't get slower at page 100 than page 1.

---

## Two Inference Modes

| Mode | Config | Use Case |
|---|---|---|
| **gundam** | image_size=640, crop_mode=True | Single images (invoices, receipts — high detail) |
| **base** | image_size=1024, crop_mode=False | Multi-page PDFs (contracts, bank statements) |

---

## Three Deployment Options

1. **Transformers** — easiest local setup (Python 3.12 + CUDA 12.9)
2. **vLLM** — Docker images ready, production concurrency
3. **SGLang** — R-SWA cache optimization already implemented, highest memory efficiency

---

## Why This Matters for Business Documents

The core problem with page-by-page OCR for business documents:
- Cross-page tables break — rows split across pages → reconstruction errors
- Multi-column layouts scramble — OCR doesn't know the page is 2 columns
- Context lost — item descriptions on page 1 referenced by totals on page 5 → no linkage

Unlimited-OCR parses the entire document as a unit. Cross-page tables, clause references, and running totals all stay connected because the decoder has global context.

**High-impact use cases:**
- **VAT invoice batches** — process 100 invoices, model can flag inconsistent tax rates across the batch
- **Contract extraction** — 50-page agreement parsed in one call; cross-page clauses stay linked
- **Bank statement reconciliation** — 200-page transaction history, zero missed rows at page boundaries
- **Customs + packing list + invoice triple-check** — joint parsing produces aligned fields without post-processing joins

---

## Try It Now

**No GPU? Online demo**: https://huggingface.co/spaces/baidu/Unlimited-OCR

```bash
pip install transformers torch pymupdf einops
```

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to share and adapt with attribution.
