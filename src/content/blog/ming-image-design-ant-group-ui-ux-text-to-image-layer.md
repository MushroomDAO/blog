---
title: "蚂蚁 Ming-Image-0.1-Design：设计稿直出、图层可拆的 6B 开源模型"
titleEn: "Ant Group Ming-Image-0.1-Design: Open 6B Model That Generates Full Designs and Decomposes Layers"
description: "inclusionAI/Ming-Image-0.1-Design，MIT，6B，两模型串联：Design 模型直接生成含排版的完整设计稿（UI/信息图/海报），Layer 模型把合并图拆解成独立可编辑的 RGBA 图层。HuggingFace 368 赞，Artificial Analysis UI/UX Design 排行榜第一，RGBA 透明输出，Figma 式结构提示词支持，80GB VRAM。"
descriptionEn: "inclusionAI/Ming-Image-0.1-Design, MIT, 6B, two-model pipeline: the Design model generates complete compositions with layout (UI/infographics/posters), the Layer model decomposes a flat image into independently editable RGBA layers. 368 HuggingFace likes, top of Artificial Analysis UI/UX Design leaderboard. RGBA transparent output, Figma-style structured prompts, 80GB VRAM required."
pubDate: 2026-10-03
heroImage: "../../assets/images/ming-image-design-ant-group-ui-ux-text-to-image-layer-banner.jpg"
category: "Tech-Experiment"
tags: ["AI设计", "蚂蚁集团", "文生图", "UI设计", "开源", "RGBA", "图层分解"]
lang: "zh-CN"
wechatTitle: "蚂蚁Ming-Image：UI设计稿直出的开源模型"
wechatDigest: "inclusionAI MIT；6B两模型：生成整套设计稿+分解可编辑图层；RGBA；UI/UX榜第一"
---

UI 设计师用 AI 生成图最头疼的问题：生成的是一张合并图，文字不能改、图层不能动、排版调一个元素要重新生全套。

蚂蚁集团旗下 inclusionAI 发布的 Ming-Image-0.1-Design 试图从两头解决这件事——一个模型生成含排版的完整设计稿，另一个模型把合并图拆回独立可编辑的图层。

GitHub: https://github.com/inclusionAI/Ming-Image | ⭐ 158 | MIT  
HuggingFace: inclusionAI/Ming-Image-0.1-Design | 368 赞

---

## 两个模型，一套流水线

**Ming-Image-0.1-Design（生成）**：文字 → 完整设计稿。生成 UI 界面、信息图、海报、文字密集的视觉作品。关键是：文字排版、层级关系、卡片布局一次生成，不是先出底图再叠文字。

**Ming-Image-0.1-Design-Layer（拆解）**：设计稿图片 → 独立 RGBA 图层。把一张合并好的设计图按图层计划拆开，每层单独输出带透明通道的 PNG，后续可以单独编辑或替换。

两个都是 6B 参数，都走 BF16 精度，都需要 80GB VRAM（A100 级别）跑完整推理。

---

## 先来看生成端

给一段描述就能出完整设计稿，标题副标题、卖点卡片、标签的层级主次都在生成结果里：

```bash
python infer.py \
  --model inclusionAI/Ming-Image-0.1-Design \
  --task text-to-image \
  --prompt "Landing page for a productivity app called Flow. Clean minimal design, white background. Top nav: wordmark Flow + links Product/Pricing/Docs. Hero: bold headline Focus without the noise, gray subheading, purple CTA button Start free. Three feature cards below with icons, rounded corners, soft shadows. Modern sans-serif." \
  --width 2048 --height 2048 \
  --output-dir outputs/flow
```

几点实际约束：

- **推荐分辨率：2048×2048**（1:1），其他比例用 2560×1440（16:9）、2432×1824（4:3）、1664×2496（2:3）
- **采样步数：12**，CFG 1.0
- **Figma 式结构提示词效果更好**：图层从后向前描述，每个元素给坐标、颜色、文字精确引用
- 提示词可以是纯自然语言，也可以是 JSON 文件（作者提供了四季小屋的示例 JSON）

**RGBA 透明输出**：加一句固定短语就能让背景变透明，输出带 Alpha 通道的 PNG，方便直接叠到其他背景上。

---

## 图层拆解端

`Ming-Image-0.1-Design-Layer` 的用法：给一张合并的设计图，加一个图层规划描述，输出 N 层独立 RGBA 图层。

```bash
python infer.py \
  --model inclusionAI/Ming-Image-0.1-Design-Layer \
  --task layer-decompose \
  --input-image assets/layer_samples/card_making_input.png \
  --prompt assets/layer_samples/card_making_prompt.txt \
  --resolution 1024 \
  --output-dir outputs/layers
```

官方示例是六层名片拆解：背景层 + 主图层 + 文字层 + 装饰层 + 标签层 + 徽章层，每层各自可编辑。输出保持输入图的宽高比。

对 Crello 测试集的定量测试：更低的 RGB L1 误差 + 更高的 Alpha soft IoU。但这是自报数据，具体数字看官方 model card 的图表。

---

## UI/UX Design 排行榜

model card 里放了一张来自 Artificial Analysis 的 UI/UX Design 专项排行榜截图，Ming-Image-0.1-Design 排第一。

排行榜是第三方 Artificial Analysis 做的，不是自报——这是这套数据相对可信的地方。但专项排行榜覆盖范围有限，和通用文生图模型（Midjourney、FLUX.1-dev 等）的比较不在这个榜上，还没有跨类别的公允对比。

社区跟进速度很快：HuggingFace 上已经有 GGUF 量化版（realrebelai/Ming-Image_GGUFs）、ComfyUI 节点（Kijai/Ming-Image-ComfyUI）、INT4 版本、vLLM-Omni 部署配方。

---

## 配套 Skills

inclusionAI 同时发布了两个 Agent Skill：

- **Ling UI Design**：用生成的视觉参考 + 图层拆解，辅助 Agent 从提示词或截图构建并视觉验证 UI 代码
- **Image to Editable PPT**：让 Agent 把一张设计图还原成 PowerPoint，文字和简单形状转成原生可编辑元素

这两个 Skill 走的是蚂蚁自己的 Ling 生态（Ling-3.0-flash-VL / qwen3.8-27B 作为提示词增强 LLM），不依赖专有 API，可以自托管。

---

## 硬件门槛

正经跑完整推理需要 80GB VRAM（A100/H100）。这是两个 6B 模型各自的独立需求，不是加在一起。

能走的降级路：
- GGUF 量化版（社区发布，17 likes）可以降低内存要求，但官方没给具体的量化精度和性能曲线
- 1024×1024 而不是 2048×2048 能明显省 VRAM 和时间
- 只用其中一个模型（生成或拆解），不用两个都装

日常跑 16GB 显存的机器：目前没有官方支持方案，等社区的 GGUF 进一步优化。

---

## 对设计师意味着什么

以前用 AI 做设计图的典型流程：出底图 → 手动加文字 → 手动排版 → 甲方改一处重来。

Ming-Image-0.1-Design 的理论路径：写设计规格（Figma 式提示词）→ 直出含排版的设计稿 → 用 Layer 模型拆回图层 → 单独修改某一层。

这个流程在 80GB VRAM 条件下是可用的。没有大 GPU 的情况下，生成端还可以通过 API 服务（DeepInfra 有部署）跑，Layer 端目前没看到公开 API。

MIT 许可证，商业使用无限制。

---

> 本文所涉软件采用 MIT 开源许可证，商用无限制。开源仅供学习参考，任何使用应遵循原仓库使用条款。

---

<!--EN-->

## Ant Group Ming-Image-0.1-Design: Open 6B Model That Generates and Decomposes Designs

The most common frustration with AI-generated design images: you get a flat merged file. Text can't be edited, layers can't be moved, and adjusting one element means regenerating the whole thing.

Ant Group's inclusionAI published Ming-Image-0.1-Design to attack this from both ends — one model that generates complete layouts with typography, and one that decomposes a flat image back into independently editable layers.

GitHub: https://github.com/inclusionAI/Ming-Image | ⭐ 158 | MIT  
HuggingFace: inclusionAI/Ming-Image-0.1-Design | 368 likes

---

### Two Models, One Pipeline

**Ming-Image-0.1-Design (generation)**: text → complete design composition. Generates UI interfaces, infographics, posters, and text-rich visuals — with typography, hierarchy, and card layouts in the output, not applied separately afterward.

**Ming-Image-0.1-Design-Layer (decomposition)**: design image → independent RGBA layers. Takes a flat design and splits it by a layer plan, outputting each layer as a transparent-background PNG that can be edited or replaced individually.

Both are 6B parameters, BF16 precision, and require 80GB VRAM (A100-class) for full-precision inference.

---

### Generation

Describe a design and get back a complete composition:

```bash
python infer.py \
  --model inclusionAI/Ming-Image-0.1-Design \
  --task text-to-image \
  --prompt "Landing page for Flow. White background. Top nav: Flow wordmark + Product/Pricing/Docs. Bold headline 'Focus without the noise', gray subhead, purple CTA 'Start free'. Three feature cards below with icons, rounded corners." \
  --width 2048 --height 2048 \
  --output-dir outputs/flow
```

Key constraints:
- Recommended: **2048×2048** (1:1) or **2560×1440** (16:9), **2432×1824** (4:3)
- **12 steps**, CFG 1.0
- **Figma-style structured prompts give better results**: describe layers back-to-front, include coordinates, color values, and exact quoted strings for text
- RGBA transparent output: add a specific prefix phrase to get alpha-channel PNG output

---

### Layer Decomposition

Provide a flat design image plus a layer plan description:

```bash
python infer.py \
  --model inclusionAI/Ming-Image-0.1-Design-Layer \
  --task layer-decompose \
  --input-image card.png \
  --prompt card_layers.txt \
  --resolution 1024 \
  --output-dir outputs/layers
```

The official example shows a six-layer business card decomposition: background, main image, text, decoration, tags, badge — each output as a separate RGBA PNG. Output preserves the input image's aspect ratio.

---

### Leaderboard Position

The model card includes a screenshot from Artificial Analysis' UI/UX Design leaderboard, placing Ming-Image-0.1-Design first. Artificial Analysis is a third-party evaluator, so this isn't self-reported in the usual sense — but the leaderboard covers a specialized design-focused scope and doesn't include direct comparisons against general image models (Midjourney, FLUX.1-dev, etc.).

Community adoption is moving: GGUF quantizations, ComfyUI nodes, INT4 versions, and vLLM-Omni deployment recipes are already available.

---

### Companion Agent Skills

Two skills ship alongside:

- **Ling UI Design**: uses Ming-Image to generate visual references and Layer to decompose them, helping an agent build and visually check UI code from a prompt or screenshot
- **Image to Editable PPT**: helps an agent reconstruct a design image as an editable PowerPoint file, with text and shapes as native elements

Both run in the Ling/Qwen ecosystem — self-hostable.

---

### Hardware Floor

80GB VRAM for full inference. Community GGUF quantizations (17 likes on HuggingFace) reduce this, but no official quantization guidance or performance curve is published yet. 1024×1024 resolution significantly reduces VRAM and time.

For generation only: DeepInfra has a hosted API endpoint.

---

### What Changes for Designers

The old flow: generate flat image → add text manually → lay out manually → client changes one thing → start over.

The Ming-Image path: write a Figma-style spec → get a complete composed design → decompose back to layers → edit individual layers independently.

That workflow is usable today with 80GB VRAM, or via hosted API for the generation step. The full loop without big hardware is waiting on community quantization work.

MIT license. Commercial use unrestricted.

---

> MIT open source, commercial use unrestricted. For technical reference only.
