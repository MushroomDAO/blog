---
title: "ChatCut × Codex / Claude Code：用提示词剪视频的完整教程，五套原创模板"
titleEn: "ChatCut × Codex / Claude Code: Complete Video Editing Tutorial with 5 Original Prompt Templates"
description: "ChatCut 是一个支持 Codex 和 Claude Code 插件的 AI 视频编辑器。本文从安装到实战，提供五套针对知识干货、产品评测、播客转视频、多镜头混剪、直播切片五个场景的原创提示词模板，开箱即用。"
descriptionEn: "ChatCut is an AI video editor with Codex and Claude Code plugin support. This tutorial covers installation through production, with 5 original prompt templates for knowledge content, product reviews, podcast-to-video, multi-shot edits, and livestream highlights."
pubDate: "2026-07-24"
updatedDate: "2026-07-24"
category: "Tech-Experiment"
tags: ["AI视频", "ChatCut", "Codex", "Claude Code", "提示词", "视频剪辑", "内容创作", "教程"]
heroImage: "../../assets/images/chatcut-ai-video-editor-codex-claude-code-plugin-tutorial-banner.jpg"
---

> **工具**：[chatcut.io](https://chatcut.io) · 插件仓库：[ChatCut-Inc/agent-plugin](https://github.com/ChatCut-Inc/agent-plugin)
> **支持的 Agent**：Codex（ChatGPT 桌面版）· Claude Code（桌面版 / CLI）
> **本文提供**：安装流程 + 五套原创场景模板，可直接复制使用

---

## 一、ChatCut 是什么

ChatCut 是一个 AI 视频编辑器。你可以直接在浏览器里用它，也可以通过 Codex 或 Claude Code 的插件系统把它接入你的 AI 工具链，用自然语言提示词驱动整个剪辑流程。

核心能力：

| 能力 | 说明 |
|------|------|
| 文字剪辑 | 在转录稿里改字 = 在时间线上剪片段 |
| 运动图形 | 自然语言描述 → 自动生成章节卡/图表/强调效果 |
| AI 字幕 | 100+ 语言，20+ 样式，可自定义保存模板 |
| AI 图像生成 | 封面、参考图、缺失的 B-roll 场景 |
| AI 视频生成 | 生成补拍镜头，支持参考图保持风格一致 |
| AI 配乐 | 无版权，按视频精确时长生成 |

---

## 二、安装：Codex 还是 Claude Code？

两条路各有侧重。**Codex**（ChatGPT 桌面版）的安装流程在 [chatcut.io/chatgpt](https://chatcut.io/chatgpt)；**Claude Code** 的流程在 [chatcut.io/claude](https://chatcut.io/claude)。

### Codex 安装（ChatGPT 桌面版）

**重要前提**：必须在本地桌面应用里操作，网页版 ChatGPT 无法安装本地插件。

在 Codex 桌面应用里开一个新对话，粘贴：

```
Read chatcut.io/chatgpt to install the ChatCut plugin and set up a new task for me.
```

Codex 会自动执行以下步骤：

```bash
# 1. 添加插件市场
"<BUNDLED_CODEX>" plugin marketplace add https://github.com/ChatCut-Inc/agent-plugin.git --ref main

# 2. 安装插件
"<BUNDLED_CODEX>" plugin add chatcut@<MARKETPLACE>

# 3. 登录（会打开 ChatCut OAuth 授权页）
"<BUNDLED_CODEX>" mcp login chatcut
```

登录完成后，Codex 会验证 plugin 状态和 MCP 注册，并自动为你打开第一个编辑对话。

### Claude Code 安装（CLI 或桌面版）

在 Claude Code 里运行：

```
Read chatcut.io/claude to install and use the ChatCut plugin
```

插件注册的 MCP 端点是：
```
https://api.chatcut.io/api/external-mcp/mcp
```

---

## 三、插件能做什么（MCP 工具层）

插件通过 MCP 协议把以下能力暴露给 Agent：

- **导入媒体**：把本地文件或 URL 导入到 ChatCut 项目
- **修改时间线**：剪辑、重排、删除片段
- **创建运动图形**：章节标题卡、数据可视化、文字强调
- **生成资产**：图像、配音、背景音乐
- **转录音频**：生成逐字转录稿
- **添加字幕**：多语言，自定义样式
- **导出视频**：指定分辨率、帧率、格式
- **验证编辑**：让 Agent 确认当前时间线状态

---

## 四、五套原创提示词模板

以下五套模板针对不同创作场景设计，每套可直接复制到 Codex 或 Claude Code 里使用，按需修改括号内的具体参数。

---

### 模板一：知识干货型（教程/技术口播）

适用于：技术教学、产品讲解、知识分享类口播视频

```
我有一段 [主题] 的教程口播视频，时长约 [X] 分钟。
请按以下步骤处理：

1. 转录全部音频，识别以下结构：
   - 概念引入段落（开场）
   - 步骤讲解段落（正文）
   - 总结/行动号召段落（结尾）
   
2. 剪辑处理：
   - 移除所有填充词和停顿（"那个""就是""然后"等）
   - 每个知识点之间保留 0.3 秒自然间隔
   - 删除重复解释同一概念的片段，保留最清晰的一次

3. 按识别出的结构添加章节：
   - 每章节开头生成一个深色背景的标题卡（显示 2 秒）
   - 标题卡文字：章节序号 + 核心关键词（不超过 8 个字）

4. 关键数据或公式出现时，在画面下方三分之一处叠加白底深字的文本框（保持 3 秒）

5. 字幕：
   - 中文：每屏一句，语义完整，字号 [大/中/小]，[黑底白字/白字黑描边]
   - 不超过视频画面下部四分之一区域

6. 从视频第 10-30 秒内选一帧作为封面：要求讲者面对镜头、表情自然

7. 导出 1080p 30fps MP4
```

---

### 模板二：产品评测型（科技 / 开箱 / 对比）

适用于：手机、电脑、耳机、软件工具等评测视频

```
这是一段 [产品名称] 的评测视频，包含 [开箱/上手/对比/总结] 环节。

剪辑任务：

1. 识别以下固定段落并打标签：
   - 开箱展示段（近景手持镜头）
   - 功能演示段（操作特写）
   - 横向对比段（并排展示）
   - 优缺点总结段（口播）

2. 在每个功能点首次出现时，在左上角添加一个小标签（白底黑字圆角矩形）显示功能名称，持续到该功能演示结束

3. 所有数据（价格/规格/跑分）出现时：
   - 暂停字幕 1 秒
   - 在画面右侧生成一个数据卡片（背景色与视频主色调互补）
   - 数字放大至正常字幕的 1.5 倍

4. 优缺点总结段：
   - 优点条目前加 ✓ 图标（绿色）
   - 缺点条目前加 × 图标（红色）
   - 每条在屏幕上停留 2 秒

5. 添加中英双语字幕，样式选 [你偏好的样式]

6. 封面选帧：产品正面清晰可见、光线均匀的一帧

7. 片头 3 秒不添加任何字幕或图形叠加

8. 导出 1080p 30fps MP4
```

---

### 模板三：播客转视频型（音频对话 → 可看视频）

适用于：把播客录音、访谈录音剪成适合发布的视频

```
这是一段 [时长] 的播客/访谈录音，嘉宾是 [嘉宾名]，主题是 [主题]。
视频背景是 [静态图/动态波形/分屏人脸]。

请完成以下处理：

1. 完整转录，标注每位发言人（主持人/嘉宾）

2. 内容精剪：
   - 移除超过 5 秒的无效停顿
   - 识别 3-5 个"金句"片段（有独到观点、可单独传播的段落）
   - 保留金句完整语境（前后各加 10 秒）
   - 其余内容可适当压缩，但不能破坏逻辑链

3. 金句出现时：
   - 全屏显示引用卡（深色背景 + 引号 + 金句文字 + 发言人名字）
   - 持续 3 秒后渐出，恢复视频

4. 在顶部添加播客信息栏（第 0-5 秒）：
   - 节目名称、期数、主题关键词

5. 字幕按发言人区分颜色：
   - 主持人：[颜色1]
   - 嘉宾：[颜色2]
   - 每屏一句，不超过 20 字

6. 视频末尾 10 秒：
   - 生成"本期精华"总结卡（3-5 条要点，逐条出现）

7. 导出 1080p 30fps MP4，适合横屏和竖屏两个版本（如需竖版，以 9:16 裁切主画面）
```

---

### 模板四：多镜头混剪型（活动 / 旅行 / 产品发布会）

适用于：把多段素材混剪成完整叙事视频

```
我有以下素材文件：[列出文件名或描述]
主题：[活动名称/旅行目的地/产品名称]
目标时长：[X] 分钟

请按以下逻辑剪辑：

1. 分析每段素材的拍摄内容，自动分类：
   - 全景/环境镜头
   - 人物/主体近景
   - 细节特写
   - 运动镜头

2. 按叙事结构组织：
   - 开场（30 秒）：选最具视觉冲击力的环境镜头 + 细节特写交叉剪
   - 主体（70%）：按时间顺序或主题模块排列
   - 结尾（20 秒）：回归全景，情感收束

3. 节奏控制：
   - 动态镜头（运动/变化）：每个镜头 2-4 秒
   - 静态镜头（讲解/停顿）：每个镜头 4-8 秒
   - 转场：优先使用硬切，视觉差异大的镜头间可用 0.3 秒黑场过渡

4. 如果素材中有同期声，保留环境音（音量降到 20%），去除背景噪声

5. 配乐：生成一首 [情感基调：欢快/沉稳/史诗/温暖] 的纯器乐，时长精确匹配视频

6. 在关键场景切换时在右下角生成地点标签卡（若为旅行视频）或时间节点标签

7. 不需要字幕（纯视觉叙事），但若有采访同期声，为该片段加字幕

8. 导出 1080p 30fps MP4
```

---

### 模板五：直播精华切片型

适用于：从长直播录像中提取高光，制作切片或精华集锦

```
这是一段 [X] 小时的直播录像。
直播类型：[游戏/知识直播/带货/聊天]
切片目标：制作 [3-5] 分钟的精华集锦，或单独提取 [N] 个 1-3 分钟的高光切片

处理步骤：

1. 分析全程音频，标记以下事件时间点：
   - 观众互动高峰（弹幕密集/主播语调提高）
   - 主播明显兴奋或惊喜反应
   - 有独立完整叙事的片段（一个完整故事/知识点/操作演示）
   - 笑点或转折时刻

2. 从标记点中提取 [N] 个最优片段，每个：
   - 包含完整的开头和结尾（不能在句子中间截断）
   - 前后各保留 3 秒缓冲

3. 每个切片开头叠加：
   - 左上角：直播日期 + 来源标记（可配置显示或隐藏）
   - 右下角：切片序号

4. 优化处理：
   - 移除超过 3 秒的沉默段
   - 保留直播间背景音，人声使用降噪增强

5. 如果是知识类直播：
   - 为每个切片添加字幕
   - 在核心知识点出现时加底部文字强调条

6. 集锦版本（可选）：
   - 用 2 秒黑场 + 切片标题过渡连接所有片段
   - 片头加 5 秒的合集封面（自动选最精彩帧）

7. 导出 1080p 30fps MP4（或 9:16 竖版，适合短视频平台）
```

---

## 五、使用技巧

**关于参数替换**：所有 `[]` 内的内容都需要根据你的实际情况填写。括号里的描述越具体，AI 的剪辑决策就越准确。

**关于迭代**：ChatCut 的 Agent 会在执行完每个步骤后等待你的确认或修改指令。不需要一次把所有要求说完——先从核心步骤开始，满意后再追加细节。

**关于字幕样式**：ChatCut 内置了 20+ 字幕预设（TikTok Pop、Noir Glass、Signal Flux 等），安装插件后可以让 Agent 列出所有可用样式，再在模板里指定。

**关于导出格式**：除 MP4 外，ChatCut 也支持针对不同平台的比例裁切（16:9 横屏 / 9:16 竖屏 / 1:1 方形）。在导出指令里加上平台目标可以让 Agent 自动处理比例。

---

## 六、局限性和注意事项

- **必须用桌面版**：插件安装需要本地 Codex 或 Claude Code 桌面应用，网页版无法安装
- **需要 ChatCut 账号**：第一次使用需要完成 OAuth 授权
- **AI 决策需人工复核**：特别是"删除口误"这类判断，建议在字幕稿层面先预览再导出
- **生成类功能有配额**：AI 图像/视频/音乐生成根据 ChatCut 的计划有使用限额

---

*数据来源：chatcut.io + GitHub ChatCut-Inc/agent-plugin，2026-07-24。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Tool**: [chatcut.io](https://chatcut.io) · Plugin: [ChatCut-Inc/agent-plugin](https://github.com/ChatCut-Inc/agent-plugin)
> **Supported Agents**: Codex (ChatGPT desktop) · Claude Code (desktop / CLI)
> **This article provides**: Installation walkthrough + 5 original scene-specific prompt templates, ready to copy

---

## 1. What Is ChatCut

ChatCut is an AI video editor. You can use it directly in your browser, or connect it to your AI toolchain through the Codex or Claude Code plugin system and drive the entire editing process with natural language prompts.

Core capabilities:

| Capability | Description |
|------------|-------------|
| Text-based editing | Edit the transcript = edit the timeline |
| Motion graphics | Natural language → chapter cards, charts, emphasis effects |
| AI captions | 100+ languages, 20+ styles, saveable custom templates |
| AI image generation | Thumbnails, reference images, missing B-roll scenes |
| AI video generation | Generate supplementary shots; reference image keeps style consistent |
| AI music | Royalty-free, generated at the exact length of your video |

---

## 2. Installation: Codex or Claude Code?

Both paths work — choose based on which tool you're already using.

### Codex Installation (ChatGPT Desktop)

**Key prerequisite**: You must be in the local desktop app. The ChatGPT web app cannot install local plugins.

Open a new conversation in the Codex desktop app and paste:

```
Read chatcut.io/chatgpt to install the ChatCut plugin and set up a new task for me.
```

Codex will automatically execute:

```bash
# 1. Add plugin marketplace
"<BUNDLED_CODEX>" plugin marketplace add https://github.com/ChatCut-Inc/agent-plugin.git --ref main

# 2. Install plugin
"<BUNDLED_CODEX>" plugin add chatcut@<MARKETPLACE>

# 3. Log in (opens ChatCut OAuth page in browser)
"<BUNDLED_CODEX>" mcp login chatcut
```

After login, Codex verifies plugin status, confirms MCP registration, and opens your first editing conversation.

### Claude Code Installation (CLI or Desktop)

In Claude Code, run:

```
Read chatcut.io/claude to install and use the ChatCut plugin
```

The plugin registers the MCP endpoint at:
```
https://api.chatcut.io/api/external-mcp/mcp
```

---

## 3. What the Plugin Can Do (MCP Tool Layer)

The plugin exposes these capabilities to the agent over MCP:

- **Import media**: Bring local files or URLs into a ChatCut project
- **Modify timeline**: Cut, reorder, delete segments
- **Create motion graphics**: Chapter title cards, data visualizations, text emphasis
- **Generate assets**: Images, voiceover, background music
- **Transcribe audio**: Generate word-for-word transcripts
- **Add captions**: Multilingual, custom styles
- **Export video**: Specify resolution, frame rate, format
- **Verify edits**: Let the agent confirm current timeline state

---

## 4. Five Original Prompt Templates

The following five templates are designed for distinct creator scenarios. Each can be copied directly into Codex or Claude Code and customized — replace everything in `[]` with your specifics.

---

### Template 1: Knowledge & Tutorial (Educational Talking-Head)

For: Technical tutorials, concept explainers, how-to videos

```
I have a tutorial talking-head video on [topic], approximately [X] minutes long.
Please process it as follows:

1. Transcribe the full audio and identify these structural sections:
   - Concept introduction (opening)
   - Step-by-step explanation (body)
   - Summary / call-to-action (closing)

2. Editing:
   - Remove all filler words and dead air ("um," "uh," "you know," etc.)
   - Preserve 0.3-second natural pauses between knowledge points
   - If the same concept is explained twice, keep the clearest version and remove the other

3. Add chapter markers based on the detected structure:
   - Generate a dark-background title card at the start of each chapter (2 seconds)
   - Title card text: chapter number + core keyword (8 words max)

4. When a key statistic, formula, or data point appears, overlay a white-background
   dark-text box in the lower third (hold for 3 seconds)

5. Captions:
   - One complete sentence per screen
   - Font size: [large/medium/small], style: [black bg white text / white text black outline]
   - Stay within the bottom quarter of the video frame

6. Select a thumbnail frame from seconds 10–30: presenter facing camera, natural expression

7. Export 1080p 30fps MP4
```

---

### Template 2: Product Review (Tech / Unboxing / Comparison)

For: Phone, laptop, earphone, software tool reviews

```
This is a review video for [product name], covering [unboxing/hands-on/comparison/verdict].

Editing tasks:

1. Identify and label these fixed segments:
   - Unboxing / first look (close-up handheld shots)
   - Feature demonstrations (operational close-ups)
   - Side-by-side comparisons
   - Pros & cons summary (talking head)

2. When a feature is first demonstrated, add a small label badge in the upper left
   (white background, black text, rounded rectangle) showing the feature name.
   Keep it visible until that demonstration ends.

3. When any number appears (price, spec, benchmark score):
   - Pause captions for 1 second
   - Generate a data card on the right side of the frame (color complement to video's dominant tone)
   - Make the number 1.5× the normal caption size

4. For the pros & cons segment:
   - Prefix each pro with a ✓ icon (green)
   - Prefix each con with an × icon (red)
   - Hold each item on screen for 2 seconds

5. Add bilingual captions in [language 1] and [language 2]

6. Thumbnail frame: product front face clearly visible, even lighting

7. No caption or graphic overlay in the first 3 seconds

8. Export 1080p 30fps MP4
```

---

### Template 3: Podcast-to-Video (Audio Conversation → Watchable Video)

For: Converting podcast recordings or interview audio into publishable video

```
This is a [duration] podcast / interview recording.
Guest: [guest name]. Topic: [topic].
Video background: [static image / audio waveform animation / split-screen faces]

Please complete:

1. Full transcript with speaker labels (Host / Guest)

2. Content editing:
   - Remove silences longer than 5 seconds
   - Identify 3–5 "quotable" segments (distinct perspective, self-contained insight)
   - Keep 10 seconds of context before and after each quotable
   - Compress the rest to reduce length without breaking logical flow

3. When a quotable moment plays:
   - Display a full-screen quote card (dark background + quotation marks + text + speaker name)
   - Hold for 3 seconds, then fade back to video

4. Add a podcast info banner in the first 5 seconds:
   - Show name, episode number, topic keywords

5. Color-coded captions by speaker:
   - Host: [color 1]
   - Guest: [color 2]
   - One sentence per screen, 20 words max

6. Final 10 seconds: generate a "Key Takeaways" card
   - 3–5 bullet points, appearing one by one

7. Export 1080p 30fps MP4
   Optional: also export a 9:16 vertical crop (main frame centered) for short-form platforms
```

---

### Template 4: Multi-Shot Edit (Event / Travel / Product Launch)

For: Combining multiple footage clips into a cohesive narrative video

```
I have the following footage files: [list file names or descriptions]
Theme: [event name / destination / product]
Target length: [X] minutes

Please edit as follows:

1. Analyze each clip and categorize it:
   - Wide / establishing shot
   - Subject / person close-up
   - Detail / texture close-up
   - Motion shot (pan, tilt, walk)

2. Arrange by narrative structure:
   - Opening (30 sec): most visually striking establishing shot + detail close-up intercut
   - Body (70%): chronological or thematic grouping
   - Closing (20%): return to wide shot, emotional resolution

3. Rhythm control:
   - Dynamic shots (movement / change): 2–4 seconds each
   - Static shots (explanation / pause): 4–8 seconds each
   - Transitions: prefer hard cuts; use 0.3-second black frame between
     visually jarring cuts

4. If clips have natural ambient sound:
   - Keep environment audio at 20% volume
   - Apply noise reduction to the ambient track

5. Music: generate a [mood: upbeat / calm / epic / warm] instrumental track
   at the exact duration of the final video

6. On key location or scene changes, add a label card in the lower right corner
   (location name for travel videos, or time stamp for event videos)

7. No captions needed (visual storytelling), EXCEPT for any interview segments —
   caption those

8. Export 1080p 30fps MP4
```

---

### Template 5: Livestream Highlights (Clip Extraction)

For: Extracting highlights from long livestream recordings for short clips or compilations

```
I have a [X]-hour livestream recording.
Stream type: [gaming / knowledge / shopping / casual chat]
Goal: [3–5 minute highlight reel] OR [extract [N] individual 1–3 minute clips]

Steps:

1. Analyze the full audio and mark timestamp events:
   - Viewer interaction peaks (dense chat / elevated host energy)
   - Host expressing visible excitement or surprise
   - Segments with self-contained narrative (complete story / knowledge point / demo)
   - Punchlines or turning points

2. Extract the [N] best segments from marked timestamps. Each clip must:
   - Begin and end at complete sentence boundaries
   - Include 3-second buffer before and after the core moment

3. At the start of each clip, overlay:
   - Upper left: stream date + source tag (configurable show/hide)
   - Lower right: clip number

4. Clean-up:
   - Remove silences over 3 seconds
   - Keep stream background audio; apply voice enhancement + noise reduction

5. For knowledge streams:
   - Add captions for each clip
   - When a core insight appears, add a bottom emphasis bar with the key phrase

6. Compilation version (optional):
   - Connect all clips with a 2-second black frame + clip title card
   - Add a 5-second intro thumbnail card (auto-select best frame) at the start

7. Export 1080p 30fps MP4
   Optional: 9:16 vertical crop for short-form platform distribution
```

---

## 5. Usage Tips

**On parameter substitution**: Everything in `[]` needs to reflect your actual project. The more specific your descriptions, the more precise the agent's editing decisions.

**On iteration**: The ChatCut agent confirms each step before proceeding. You don't need to put all requirements in one prompt — start with the core editing tasks, approve the result, then add refinements like captions or graphics.

**On caption styles**: ChatCut includes 20+ preset caption styles (TikTok Pop, Noir Glass, Signal Flux, etc.). After installing the plugin, ask the agent to list all available styles, then reference one by name in your template.

**On export format**: Beyond MP4, ChatCut supports aspect ratio crops for different platforms (16:9 landscape / 9:16 portrait / 1:1 square). Adding a platform target to your export instruction lets the agent handle the crop automatically.

---

## 6. Limitations

- **Desktop app required**: Plugin installation needs the local Codex or Claude Code desktop app — the web version cannot install plugins
- **ChatCut account required**: OAuth authorization is needed on first use
- **Review AI decisions**: Especially for "remove filler words" — preview in the transcript view before exporting
- **Generation caps**: AI image / video / music generation has usage limits depending on your ChatCut plan

---

*Data sources: chatcut.io + GitHub ChatCut-Inc/agent-plugin, collected 2026-07-24.*

© 2026 Author: Mycelium Protocol
