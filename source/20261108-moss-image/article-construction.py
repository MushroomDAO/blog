from pathlib import Path
import json
s='moss-image-openmoss-layout-generation-review'
cn='''MOSS-Image 是 OpenMOSS 的开源图像生成模型家族，重点是把中英文字和复杂版式一起画进图片。它既接受自然语言提示词，也能用 JSON 指定文字、物体及其位置，适合研究海报、信息图和其他需要组织内容的视觉任务。

官方仓库是 `OpenMOSS/MOSS-Image`，已发布 Base 与 SFT 两套权重。模型卡标注 Apache-2.0，仓库的独立推理代码也采用 Apache-2.0；使用第三方转换、组件或社区模型时仍应查看各自说明。本次固定仓库提交 `6be4453024c5acae9dcd0a191e26ee524e743310`，核对权重配置，并完成不下载完整权重的本地辅助验证。

封面采用官方 README 展示的上海全景样例，经裁剪制作，用于说明项目的公开成果，不是本次运行 MOSS-Image 得到的图片。

## Base、SFT和社区版本，应该怎样区分？

| 入口 | 角色 | 使用时关注什么 |
|---|---|---|
| MOSS-Image-Base | 基础文生图模型 | 采样参数、提示词和后续适配 |
| MOSS-Image-SFT | 在 Base 上用筛选数据监督微调 | 与 Base 相同的架构和推理管线，比较具体任务表现 |
| Comfy-Org/MOSS-Image | ComfyUI 格式的模型组件与工作流 | 加载器、组件文件放置及原生支持版本 |
| 社区 LoRA、蒸馏、量化或编辑分支 | 各自修改、适配或扩展 | 来源、基础模型、参数和兼容性需要分别核对 |

SFT 不是“少步版”的同义词，Base/SFT 的区别也不等于是否支持 Layout。两者都支持自然语言、标签序列和布局输入。官方示例中 SFT 的文字分组和白板组织更清楚，但示例不能替代对自己任务的对照测试。

对初次使用者，先在固定提示词、尺寸、种子和采样参数下比较 Base 与 SFT，更容易理解差异。先不要把多个社区加速、去条纹、精度转换 LoRA 一起叠加，否则很难定位效果变化来自哪一层。

## 5B背后是一条怎样的生成链路？

“5B”指图像生成的 DiT 骨干，不能直接用作整套系统的参数量或内存估算。本次读取的 SFT 配置确认了 42 层图像 Transformer、Qwen3.5 系列文本编码器，以及 `AutoencoderKLFlux2`；项目文档将文本编码器描述为 Qwen3.5-9B。

简化的链路是：文本编码器理解提示词 → DiT 在潜空间逐步生成 → VAE 解码成像素。布局规划或提示词增强还可以发生在前面。不同阶段的权重、激活和中间结果都会影响资源占用。

项目的标准推荐包括 Flow-matching Euler、50 步、CFG 3、Shift 5，以及负分支跳过第 22 层的设置。用户指南还建议手动输入的宽高使用正的 16 倍数；不要把任意尺寸字符串都当成有效输入。

这组参数是起点，不是跨平台画质一致性保证。换调度器、精度、工作流或社区适配器后，应保留参数记录再比较。文档提到的长提示词上限为 4096 tokens，不能把文本编码器配置中的更大上下文能力，直接当成图像管线实际接受的长度。

![小M依次调度文本编码器、图像DiT和VAE，说明完整生成链路与分阶段资源占用](../../assets/images/SLUG-fig-01.png)

## Layout的价值是什么？

单纯说“把标题放在上面，主体放在下面”，会给模型留下大量解释空间。Layout 让用户直接写出需要画出的文字、元素说明和边界框，适合让内容组织成为生成输入的一部分。

这仍然是条件生成：模型需要按布局画出图片，框并不自动变成排版软件的确定性约束。输出也不是自动附带可编辑字体图层的 SVG 或 PSD。最终海报的错别字、标点、溢出和视觉层级仍要检查。

项目提供的 Prompt Enhancer skill 可以协助 Agent 扩写内容或规划布局。其中的 `compile_prompt.py` 做格式校验和坐标转换，不会调用图像生成服务；运行编译器成功，不代表已经生成图片。

### 两种坐标格式为什么容易混淆？

| 格式 | 原点 | 坐标顺序 | 画布尺寸 |
|---|---|---|---|
| 可编辑布局草稿 | 左上角 | `xyxy`：x1、y1、x2、y2 | 包含 width、height |
| 送给模型的提示 JSON | 画布中心 | `yxyx`：y1、x1、y2、x2 | 编译结果不包含宽高，生成时另行设置 |

这些是绝对像素坐标，不是归一化的 0–1 坐标。以 1024×1024 画布为例，草稿标题框 `[128,96,896,224]`，转换后是 `[-416,-384,-288,384]`：先调整顺序，再按相应轴减去画布中心。

本次实际编译的两元素草稿如下，可以保存为 `draft.json`：

```json
{
  "width": 1024,
  "height": 1024,
  "bbox_coord_space": "abs",
  "bbox_format": "xyxy",
  "summary": {
    "canvas": "single",
    "caption": "A clean poster with a short Chinese title and a blue mountain below."
  },
  "items": [
    {"label":"text","caption":"Large blue title.","text":"看见山川","bbox":[128,96,896,224]},
    {"label":"object","caption":"A blue mountain.","bbox":[128,320,896,928]}
  ]
}
```

从项目根目录运行：

```bash
python3 skills/moss-image-prompt-enhancer/scripts/compile_prompt.py draft.json --output prompt.txt
```

编译结果的标题框与上文一致，物体框为 `[-192,-384,416,384]`，并带有 `bbox_coord_space: "abs_centralized"` 与 `bbox_format: "yxyx"`。实际生成时仍应选择 1024×1024；只修改画布尺寸，不会替你等比例重算原来的元素框。

![小M把左上角xyxy草稿转换为中心原点yxyx，携带相同画布尺寸进入生成](../../assets/images/SLUG-fig-02.png)

## 论文中的文字成绩应该怎样理解？

技术报告提出 LongLongTextBench（LLTB）和 RealLayoutArena（RLA），分别观察长文本渲染与版式丰富的生成任务。作者报告 LLTB 平均文字覆盖率约 96.3%；这不是本次复测结果。

这个覆盖指标使用 OCR 识别后的英文词或中文字符多重集合召回，按语言与长度组汇总。论文明确说明，它不检查顺序，也不直接惩罚多出的 OCR 单元，标点也不在对应匹配白名单中。因此，96.3% 不能翻译成“整页逐字逐句正确率96.3%”。

RLA 的整套系统比较包含提示词增强，另有共享增强提示词的生成器比较。评价“模型骨干”和评价“规划器加生成器”是不同问题，不能抽取不同设置里的排名，拼成统一的全面领先结论。

实际验收可保留三项：逐字核对指定文字，检查元素是否落在预期区域，再请人评估层级和阅读顺序。对于日期、价格、公式等信息，即使图像视觉效果很好，也应单独核对。

## 如何选择ComfyUI或Python入口？

ComfyUI 用户可以先走原生支持路径：选用包含 MOSS-Image 支持的版本，安装对应依赖，并使用 Comfy-Org 提供的组件和原生工作流。扩散模型、文本编码器和 VAE 分别放到对应目录，CLIP Loader 类型使用 `moss_image`。

仓库内的 HF 目录加载插件是另一条路径，适合读取本地 Diffusers 模型目录或继续使用旧插件工作流。切换原生路线时应换成对应工作流，不能只替换一个加载节点；文档特别说明，两条路线的时间步倍率和采样节点不能机械混用。

Python 用户应注意，仓库提供 UI、内存管理等运行代码，独立模型管线还会从 Hugging Face 模型包加载自定义实现。复现时同时记录仓库提交和模型 revision；只固定 GitHub 提交，不足以固定所有执行代码与权重。

本次读取的 SFT 模型 revision 为 `f972bd4b4b9e3852133cc5da954d87bc32cd8fb9`。这个记录用于定位所查配置，不表示已下载或运行该版本的完整模型。

## 显存与Mac部署有哪些实际边界？

先区分 GPU 常驻、组件卸载、逐层卸载和低内存模式。把权重转移到 CPU 或按需从磁盘读取，会改变显存压力，也会增加传输、加载和等待，不能只比较一个显存数字。

项目 README 记录过低内存路径生成一张 1024×1024、50 步图片的峰值：PyTorch GPU 已分配约 3.65 GiB、已保留约 3.85 GiB，任务系统 RAM 含文件缓存约 14 GiB。这些是项目给出的特定运行记录，不是所有硬件、尺寸和配置的最低要求，也不是本次测量。

Mac 文档另列出实验性的 PyTorch MPS 路线，公开的真权重验证针对 M1 Max、32GB 统一内存及 SFT。它分阶段加载约 17GB 文本编码器和约 10GB DiT，并对 MPS 不支持的 FP64 时间步运算做 CPU 处理；不是把 CUDA 示例的设备字符串改为 `mps` 就完成全部适配。

文档建议为一套模型、环境和下载文件预留约 40GB 磁盘，记录的出图调用为数分钟级。其他芯片、较小内存、Base 模型及不同版本仍应分别验证。社区训练器所称“6GB LoRA训练”也不能直接变成官方完整推理链路的显存需求。

## 本次在本机验证到了哪一层？

Mycelium Protocol 执行了两组上游检查：布局编译器 8 项测试，以及 MPS 运行辅助逻辑的 11 项回归检查，共 19 项通过。检查覆盖草稿校验与坐标编译、加载阶段顺序、提示缓存、时间步 CPU 运算、上游源码变动时明确失败及相关 UI 构造等路径。

MPS 回归大量使用替身对象和模拟加载器，不能据此宣称真实权重已经在本机完成生成。另实际运行了上面的布局编译示例，核对两组边界框与输出字段；全程没有下载完整模型权重，也没有评测画质、OCR准确率、出图速度或峰值内存。

测试环境为 Python 3.12.15、PyTorch 2.15.0、Diffusers 0.41.0、Transformers 5.20.1、Accelerate 1.15.0 和 Gradio 6.30.0。它与文档的真权重验证环境不完全相同，保留版本记录是为了避免把辅助逻辑通过说成整套环境等价。

![小M把布局编译与运行辅助检查放在已验证区，真实出图、OCR和峰值内存留待验证](../../assets/images/SLUG-fig-03.png)

## 值得怎样开始使用？

先选一个可核对的任务：一句短标题、两三个明确元素、固定画布。记录原始草稿、编译后的提示词、模型版本、参数和种子；生成后保留原图，再做文字与布局验收。

等这一轮能够复现，再逐步增加文本长度、布局密度和风格约束。修改时尽量一次只动一类变量，例如仅换 Base/SFT、仅变步数或仅调整布局，避免把提示词、模型、精度和社区插件同时更换。

MOSS-Image 的吸引力在于把内容组织引入开源图像生成流程。它可以成为设计探索和视觉工作流的一部分；走向可靠交付，还需要把结构化输入、实际生成和结果校对接成闭环。

## 常见问题

### MOSS-Image就是一个5B模型文件吗？

不是。5B描述图像DiT骨干，实际管线还使用文本编码器和VAE。下载体积、系统内存和显存还受精度、卸载、尺寸与运行环境影响。

### Prompt Enhancer skill会自己生成图片吗？

其编译脚本不会调用生成服务。它把内容或布局草稿整理成模型提示词，之后仍需使用MOSS-Image管线或相应工作流出图。

### 本次已经证明中文海报不会出错了吗？

没有。19项辅助检查和坐标编译示例不能替代真实出图、OCR与人工校对。论文覆盖率也不是逐字顺序、标点和整页排版的完全正确率。

## 来源与进一步阅读

官方仓库：https://github.com/OpenMOSS/MOSS-Image

Base权重：https://huggingface.co/OpenMOSS-Team/MOSS-Image-Base

SFT权重：https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT

中文指南：https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE_ZH.md

ComfyUI与格式转换模型：https://huggingface.co/Comfy-Org/MOSS-Image

Mac实验路线：https://github.com/OpenMOSS/MOSS-Image/blob/main/docs/macos.md

技术报告及指标定义：https://arxiv.org/html/2610.23374v1

相关阅读，AI基础设施中的部署与验收：https://blog.mushroom.cv/blog/ai-infrastructure-engineer-learning-path-review/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。
'''
en='''MOSS-Image is OpenMOSS's open image-generation family, emphasizing bilingual text rendering and layout-rich images. It accepts natural-language prompts and JSON specifications for text, objects and their positions, making it interesting for posters, infographics and other content-heavy visual tasks.

The official repository is `OpenMOSS/MOSS-Image`, with Base and SFT checkpoints. Model cards identify Apache-2.0, and the standalone pipeline code is Apache-2.0; check separate components and community derivatives on their own terms. This review pins repository commit `6be4453024c5acae9dcd0a191e26ee524e743310`, reads model configurations and performs bounded helper checks without downloading full weights.

The cover is cropped from the official README's Shanghai panorama example. It illustrates a published project result, not an image generated by this review.

## Base, SFT and community derivatives

| Entry | Role | What to check |
|---|---|---|
| MOSS-Image-Base | Base text-to-image model | Sampling, prompts and adaptation |
| MOSS-Image-SFT | Curated-data supervised fine-tuning | Same architecture/pipeline, task-specific comparison |
| Comfy-Org/MOSS-Image | ComfyUI components and workflows | Loaders, file placement and native support |
| Community adapters, distillations, quantizations or editing branches | Independent changes/extensions | Provenance, base model, settings and compatibility |

SFT does not mean a few-step distillation. Both official checkpoints support prose, tag sequences and Layout. The project's comparison example shows clearer grouping after SFT, but examples do not replace tests on a particular task.

For an initial comparison, keep prompt, dimensions, seed and sampling settings fixed. Avoid adding several community speed, precision and banding adapters at once; it becomes difficult to attribute a change.

## What sits around the five-billion-parameter backbone?

The5B figure describes the image DiT, not the whole pipeline's parameter count or memory footprint. The inspected SFT configuration has42 transformer layers, a Qwen3.5-family text encoder and `AutoencoderKLFlux2`. Project documentation identifies the text encoder as Qwen3.5-9B.

The simplified chain is text encoding → iterative latent generation by the DiT → VAE decoding. Prompt planning can occur beforehand. Weights, activations and intermediate results at each stage affect resource requirements.

Recommended defaults include flow-matching Euler,50 steps, CFG3, shift5 and negative-branch skipping at layer22. Positive dimensions must be multiples of16. These settings are a starting point, not a cross-platform image-equivalence guarantee. The documented prompt cap is4096 tokens; a larger context length in the underlying text model's config does not establish a larger pipeline input limit.

![LittleM coordinates text encoding, image DiT sampling and VAE decoding as separate resource stages](../../assets/images/SLUG-fig-01.png)

## What does Layout add?

Layout makes literal text, element descriptions and bounding boxes part of the input. It can reduce ambiguity in instructions such as placing a title above an illustration. It remains generative conditioning rather than a deterministic typesetting constraint. Output is a raster image, not automatically an editable SVG or layered PSD.

The Prompt Enhancer skill can help an agent expand content or plan positions. Its `compile_prompt.py` validates and converts a draft; it does not call an image service. A successfully compiled prompt is not a successfully generated image.

### Why are the coordinate conventions easy to confuse?

| Format | Origin | Order | Dimensions |
|---|---|---|---|
| Editable draft | Top-left | `xyxy` | Contains width/height |
| Model-facing prompt | Canvas center | `yxyx` | Generation dimensions are supplied separately |

These are absolute pixels. On a1024×1024 canvas, draft title box `[128,96,896,224]` becomes `[-416,-384,-288,384]` after coordinate reordering and centering.

The following two-element draft was compiled during this review:

```json
{
  "width": 1024,
  "height": 1024,
  "bbox_coord_space": "abs",
  "bbox_format": "xyxy",
  "summary": {
    "canvas": "single",
    "caption": "A clean poster with a short Chinese title and a blue mountain below."
  },
  "items": [
    {"label":"text","caption":"Large blue title.","text":"看见山川","bbox":[128,96,896,224]},
    {"label":"object","caption":"A blue mountain.","bbox":[128,320,896,928]}
  ]
}
```

From the repository root:

```bash
python3 skills/moss-image-prompt-enhancer/scripts/compile_prompt.py draft.json --output prompt.txt
```

The second box becomes `[-192,-384,416,384]`. The output declares `abs_centralized` and `yxyx`, omitting width/height. Use1024×1024 when generating. Changing canvas dimensions alone does not rescale the draft's boxes.

![LittleM converts top-left xyxy into centered yxyx and keeps the intended generation size](../../assets/images/SLUG-fig-02.png)

## How should the reported text score be read?

The report introduces LLTB for long-text rendering and RLA for layout-rich generation. Its approximately96.3% LLTB coverage is author-reported, not reproduced here. Coverage uses OCR word/character multiset recall; it does not check order or directly penalize extra OCR units, and the matching whitelist excludes punctuation. It is not exact-string accuracy.

RLA also distinguishes complete prompt-enhancement systems from generators sharing enhanced prompts. Rankings from those different setups cannot be combined into one universal superiority claim.

For a real deliverable, check literal text, element placement and human-readable hierarchy separately. Dates, prices and formulas deserve explicit review even when the image looks polished.

## ComfyUI or Python?

ComfyUI users can choose a version containing native MOSS-Image support, install its matching dependencies, and use Comfy-Org's native components/workflow. Diffusion model, text encoder and VAE go into their respective directories; the CLIP Loader type is `moss_image`.

The repository's local-HF-directory plugin is a separate path for Diffusers directories and existing plugin workflows. When switching paths, import the matching workflow rather than replacing one loader. The documentation specifically distinguishes timestep multipliers and sampling nodes.

Python loading can execute a custom pipeline supplied in the Hugging Face model bundle, while the Git repository supplies runtime/UI components. Record both the Git commit and model revision. A repository pin alone does not fix all weights and executing code.

The inspected SFT model revision was `f972bd4b4b9e3852133cc5da954d87bc32cd8fb9`. This identifies the checked configuration, not a completed full-weight inference run.

## Memory and Apple silicon limits

GPU-resident, component, sequential and low-memory modes make different tradeoffs. Moving weights through CPU RAM or disk can lower GPU usage while adding transfers and loading time.

For one1024×1024,50-step image, the project records approximately3.65GiB allocated and3.85GiB reserved GPU memory, plus14GiB task RAM including file cache on its low-memory path. These are particular recorded peaks, not universal minimum requirements or measurements from this review.

The experimental MPS route separately documents SFT validation on an M1 Max with32GB unified memory. It stages an approximately17GB text encoder and10GB DiT and handles an MPS-unsupported FP64 timestep operation on CPU. A simple CUDA-to-MPS device-string edit does not reproduce that adaptation.

The guide suggests roughly40GB disk space for a model bundle, environment and download files, with recorded generation calls taking minutes. Other chips, smaller memory configurations, Base and different dependencies need separate validation. A community trainer's6GB adapter-training example is not an inference-memory requirement for the complete official pipeline.

## What was tested locally?

Mycelium Protocol ran eight upstream layout-compiler tests and eleven MPS-runtime helper regression checks:19 passed. They cover draft validation/conversion, staged loading, prompt caching, CPU timestep arithmetic, explicit failure on upstream source changes and related UI construction.

The MPS tests extensively use fake objects and mocked loaders; they do not establish real-weight image generation. The two-element draft above was also compiled and its output boxes/fields checked. No full model weights were downloaded, and no image-quality, OCR, generation-speed or peak-memory benchmark was run.

The helper environment used Python3.12.15, PyTorch2.15.0, Diffusers0.41.0, Transformers5.20.1, Accelerate1.15.0 and Gradio6.30.0. It is not identical to the documented real-weight validation environment. Keeping those distinctions prevents helper success from becoming a claim of full-stack equivalence.

![LittleM separates verified compiler/runtime helpers from image, OCR and memory checks still pending](../../assets/images/SLUG-fig-03.png)

## A useful first workflow

Start with one short title, a few elements and a fixed canvas. Save the editable draft, compiled prompt, checkpoint revision, sampling settings and seed. Retain the original generated image, then check text and placement.

Increase text length, layout density and style constraints gradually. Change one category of variable at a time, such as checkpoint, step count or layout, before introducing more community components.

MOSS-Image's useful contribution is bringing content organization into an open image-generation workflow. Reliable delivery still requires connecting structured input, actual generation and output review.

## FAQ

### Is MOSS-Image a single5B file?

No. The figure describes the image backbone. Text encoding and VAE decoding also require resources, and precision/offloading/dimensions affect total needs.

### Does the Prompt Enhancer skill generate images?

Its compiler does not call an image API. It prepares prompt/layout input for MOSS-Image or a compatible workflow to generate later.

### Were error-free Chinese posters demonstrated here?

No. Nineteen helper checks and coordinate compilation do not replace real generation, OCR and manual review. Reported coverage is not full-page exactness.

## Sources and further reading

Official repository: https://github.com/OpenMOSS/MOSS-Image

Base weights: https://huggingface.co/OpenMOSS-Team/MOSS-Image-Base

SFT weights: https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT

User guide: https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md

ComfyUI models: https://huggingface.co/Comfy-Org/MOSS-Image

Experimental Mac route: https://github.com/OpenMOSS/MOSS-Image/blob/main/docs/macos.md

Technical report and metric definitions: https://arxiv.org/html/2610.23374v1

Related infrastructure review: https://blog.mushroom.cv/blog/ai-infrastructure-engineer-learning-path-review/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
'''
meta={'title':'MOSS-Image：OpenMOSS的文字生图、布局控制与部署边界','titleEn':'MOSS-Image: OpenMOSS Layout Generation and Deployment','description':'MOSS-Image是OpenMOSS开源图像模型，提供Base与SFT权重，支持中英文字和JSON布局。本文核对5B骨干、文本编码器与VAE，解释两种坐标格式、提示词增强、ComfyUI及Mac路线，通过19项辅助检查和实际布局编译，区分官方画质报告、内存记录与本次未测能力，帮助建立从结构化输入到结果校对的流程。','descriptionEn':'Review MOSS-Image Base and SFT, layout coordinates, ComfyUI and Mac deployment, with 19 helper checks and clear limits on text scores, memory and image quality.','wechatTitle':'MOSS-Image：文字生图与布局控制','wechatDigest':'找到OpenMOSS官方模型，拆解布局坐标、完整资源需求与本地辅助验证。','pubDate':'2026-11-08','updatedDate':'2026-11-08','category':'Tech-Experiment','tags':['MOSS-Image','OpenMOSS','图像生成','布局控制','ComfyUI','本地部署'],'heroImage':f'../../assets/images/{s}-banner.jpg'}
text='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in meta.items())+'\n---\n\n'+cn.replace('SLUG',s)+'\n<!--EN-->\n\n'+en.replace('SLUG',s)
# English spacing only; do not alter numeric JSON or identifiers.
for a,b in [('The5B','The 5B'),('has42','has 42'),('Euler,50','Euler, 50'),('CFG3','CFG 3'),('shift5','shift 5'),('layer22','layer 22'),('of16','of 16'),('is4096','is 4096'),('a1024','a 1024'),('Use1024','Use 1024'),('approximately96.3','approximately 96.3'),('one1024','one 1024'),('×1024,50','×1024, 50'),('approximately3.65GiB','approximately 3.65 GiB'),('and3.85GiB','and 3.85 GiB'),('plus14GiB','plus 14 GiB'),('with32GB','with 32 GB'),('approximately17GB','approximately 17 GB'),('and10GB','and 10 GB'),('roughly40GB','roughly 40 GB'),("trainer's6GB","trainer's 6 GB"),('checks:19','checks: 19'),('Python3.12','Python 3.12'),('PyTorch2.15','PyTorch 2.15'),('Diffusers0.41','Diffusers 0.41'),('Transformers5.20','Transformers 5.20'),('Accelerate1.15','Accelerate 1.15'),('Gradio6.30','Gradio 6.30'),('single5B','single 5B')]:text=text.replace(a,b)
Path('src/content/blog',s+'.md').write_text(text);print({k:len(meta[k])for k in ['titleEn','description','descriptionEn','wechatTitle','wechatDigest']})
