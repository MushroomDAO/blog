---
title: "MiniCPM 仓鼠桌宠 + pet-forge：本地 1B 模型，感知你的 IDE，可换角色"
titleEn: "MiniCPM Desk Pet + pet-forge: Local 1B Model That Watches Your IDE and Supports Custom Characters"
description: "OpenBMB/MiniCPM-Desk-Pet，AGPL-3.0，491 stars，仓鼠桌宠内置 MiniCPM5-1B-GGUF（~2GB），本地推理，感知 Cursor/Claude Code/Codex 的 coding agent 状态，任务完成时在气泡里汇报发生了什么。rullerzhou-afk/pet-forge，MIT，60 stars，Codex Skill 版制作套件，SVG 矢量路线 + APNG 视频路线，vtracer 追踪 + 色键抠图工具链，用来做自定义桌宠角色。"
descriptionEn: "OpenBMB/MiniCPM-Desk-Pet, AGPL-3.0, 491 stars — hamster desktop pet running MiniCPM5-1B-GGUF locally (~2GB), aware of Cursor/Claude Code/Codex coding-agent state, narrates what the AI just did in a speech bubble. rullerzhou-afk/pet-forge, MIT, 60 stars — a Codex Skill toolkit to build custom pets via SVG vector path or APNG video pipeline."
pubDate: 2026-10-03
heroImage: "../../assets/images/minicpm-desk-pet-pet-forge-local-ai-companion-banner.jpg"
category: "Tech-Experiment"
tags: ["桌宠", "MiniCPM", "本地推理", "AI Agent", "开源", "Codex Skill", "面壁智能"]
lang: "zh-CN"
wechatTitle: "MiniCPM仓鼠桌宠：1B本地AI伴你写代码"
wechatDigest: "AGPL-3.0，491星；1B本地推理感知IDE；pet-forge套件做自定义角色Skill，MIT"
---

你的 coding agent 在跑任务，你不知道它跑完没有、卡在哪了、做了什么——除非自己去看日志。

MiniCPM-Desk-Pet 换了一个思路：把一只本地运行的仓鼠放在桌面上，让它帮你盯着 coding agent。任务跑完，仓鼠在气泡里告诉你发生了什么；agent 卡住等待你确认，仓鼠摇铃提醒你。

GitHub: https://github.com/OpenBMB/MiniCPM-Desk-Pet | ⭐ 491 | AGPL-3.0  
GitHub: https://github.com/rullerzhou-afk/pet-forge | ⭐ 60 | MIT

---

## 两个仓库，一套体系

**MiniCPM-Desk-Pet**（OpenBMB / 面壁智能）：可以直接跑的桌宠应用，内置 MiniCPM5-1B 本地模型，装好就用。

**pet-forge**（rullerzhou-afk）：桌宠角色制作工具包，Codex Skill，用来自制 SVG 或 APNG 格式的自定义角色。它不含成品角色，是帮你做出角色的路线图 + 工具链。

两者的联系：MiniCPM-Desk-Pet 的桌宠 UI 基于同一作者的 `clawd-on-desk` 项目，pet-forge 则是把角色制作方法论系统化成可重用工具包。

---

## MiniCPM-Desk-Pet：装好即用

### 核心定位

不是桌面小玩意，是 coding agent 的「状态播报员」：

- **任务叙述**：coding agent（Cursor、Claude Code、Codex）完成一轮任务后，桌宠在气泡里用一句话说 AI 刚做了什么，不用自己翻 terminal
- **Idle 提醒**：agent 在等你确认输入时，桌宠播放铃声动画提醒——不用盯着屏幕等
- **自动识别**：启动时扫描本机安装了哪些 coding agent，一键连接

这几个功能是普通「本地 AI 聊天」应用没有的——它们只有在应用和 IDE 之间真正集成时才能工作。

### 本地推理

- **模型**：MiniCPM5-1B-GGUF，约 2GB
- **平台**：macOS Apple Silicon（M1/M2/M3/M4，主测平台）、Windows x64（有安装包）
- **内存**：日常聊天不需要大 GPU，苹果芯片统一内存跑

首次启动引导流程：环境检查 → 模型下载（支持 HuggingFace / ModelScope 两个源，自动选快的）→ 模型预热 → 进入使用

装好后，普通聊天不出本机，不调用任何远程服务。

### 用法

```bash
# macOS 安装（官方 DMG）
xattr -cr /Applications/MiniCPM\ Desk\ Pet.app  # 如果系统提示阻止

# 快捷键
Cmd+Shift+M   # 开/关聊天气泡
Cmd+Shift+T   # 切换 thinking 模式
Esc           # 输入时关闭气泡
```

**换角色（Persona 适配器）**：Settings → MiniCPM，默认内置猫娘（neko）风格适配器，用的是 neko30k 数据集微调。可以导入自定义角色适配器。

### 已知约束

- macOS Apple Silicon 是主测平台，Windows 支持但测试深度不同
- 响应速度取决于芯片代数、内存压力和选用模型
- coding agent 感知依赖各工具的集成接口，不同版本行为可能不同
- 首次启动需要网络（除非本地已有 .gguf 文件）

---

## pet-forge：自制桌宠角色的 Codex Skill

如果你想换一个不是仓鼠的角色，或者自己搭一套桌宠，pet-forge 给出了完整路线。

### 两条路线

**SVG 路线**（推荐精确动画）：

```
参考 PNG → 去背景 → vtracer 矢量化 → 结构化 SVG → CSS 动画
```

优点：文件小、精确 CSS 循环、每个关键帧可改、无生成 API 费用。
适合：线条清晰的矢量风格角色。

**APNG 路线**（推荐视觉丰富）：

```
提示词 → AI 参考图 → 首尾帧锚定视频生成 → 色键抠图 → .apng
```

优点：视觉风格更丰富、快速出草稿。
代价：依赖图像/视频生成 API（豆包/Seedance 或自有 API），重跑频率高。

**混合路线**：APNG 承载自然运动（角色动作），SVG 承载精确效果（特效、粒子、文字）。

### 实际工具链

**SVG 路线的 png2svg 工具**：

```powershell
# 去背景
py -3 -m rembg i character.png character-clean.png

# vtracer 矢量化
py -3 routes\svg\tools\png2svg\png2svg.py character-clean.png character.svg --preset apple-precise
```

vtracer 适合色块清晰的图形，对复杂渐变、毛发、噪点边缘效果差——这类情况走 APNG 路线或手工重建关键 SVG 结构。

README 里有一个对比案例：同一张梨形角色 PNG，工具路线（vtracer）输出 13 条匿名 path、约 21KB，GPT-5.5 Pro 直接生成 SVG 输出 15 条带语义 id 的 path、约 12KB，结构更干净、可直接绑定动画。模型直接写 SVG 这个路线值得认真对待。

**APNG 路线的色键抠图工具**：

```powershell
py chroma_key.py output/idle/video.mp4 output/idle/result.apng --plays 0 --key-color "#00B140"
```

角色含大面积绿色时换用品红色键（`#FF00FF`），在视频生成阶段一并指定背景颜色。

### 作为 Codex Skill 使用

pet-forge 根目录有 `SKILL.md`——可以直接作为 Codex Skill 加载，让 Codex 用仓库里的路线文档、模板和工具链一步步帮你做角色。

Skill 覆盖：路线选择 → 透明 PNG 转 SVG → APNG 提示词准备 → 片段组装 → SVG 效果叠加 → 运行时接入。

如果要从头做一个角色，pet-forge 推荐先做**角色拓扑盘点**：这个角色有没有完整的头+身体+四肢？有没有嘴巴和表情？有没有手脚？——不同拓扑对应不同的 SVG 约定和动画合同，不要默认每个桌宠都有同样的结构。

---

## 两者怎么配合用

最直接的用法：

1. 用 **pet-forge** + Codex 制作一个自定义 SVG/APNG 角色
2. 导入到 **MiniCPM-Desk-Pet** 作为自定义 persona 适配器
3. 桌宠跑 MiniCPM5-1B 本地推理，感知你的 Cursor/Claude Code，用你自己的角色形象播报任务进度

对设计师来说，整条链路不依赖云端服务（除了 APNG 路线的视频生成步骤）。

---

## 许可证说明

- **MiniCPM-Desk-Pet**：AGPL-3.0，修改后的版本也必须以相同许可证开放。商业使用需要注意 AGPL 的网络服务条款。
- **pet-forge**：MIT，商业使用无限制。
- **MiniCPM5-1B 模型权重**：单独受 OpenBMB MiniCPM 模型许可证约束，不是 AGPL。

---

> AGPL-3.0 开源，商业使用前请核实条款。pet-forge 工具包 MIT 许可，无限制。开源仅供学习参考。

---

<!--EN-->

## MiniCPM Desk Pet + pet-forge: Local 1B Model That Watches Your IDE

Your coding agent is running a task. You don't know if it finished, where it got stuck, or what it actually did — unless you open the terminal and read the logs.

MiniCPM-Desk-Pet takes a different approach: put a locally-running hamster on your desktop, let it watch the coding agent for you. When a task finishes, the hamster narrates what happened in a speech bubble. When the agent is waiting for your input, it rings a bell.

GitHub: https://github.com/OpenBMB/MiniCPM-Desk-Pet | ⭐ 491 | AGPL-3.0  
GitHub: https://github.com/rullerzhou-afk/pet-forge | ⭐ 60 | MIT

---

### Two Repos, One System

**MiniCPM-Desk-Pet** (OpenBMB): a desktop pet application that ships and runs MiniCPM5-1B locally. Download, install, use.

**pet-forge** (rullerzhou-afk): a character creation toolkit packaged as a Codex Skill. Routes, templates, and tools for building SVG or APNG desktop pet characters. It's a framework, not a finished character pack.

The connection: MiniCPM-Desk-Pet's pet UI is based on the same author's `clawd-on-desk` project. pet-forge systematizes the character-building methodology into a reusable toolkit.

---

### MiniCPM-Desk-Pet: Core Features

**Task narration**: after a Cursor/Claude Code/Codex session ends, the pet summarizes what the AI just did in a speech bubble.

**Idle alerts**: when a coding agent is waiting for your input, the pet plays a bell animation and sound.

**Auto-detect agents**: on startup, the app scans for installed coding tools and prompts you to connect them in one click.

**Local inference**: MiniCPM5-1B-GGUF, ~2GB. macOS Apple Silicon is the primary tested platform. Everyday chat runs entirely on-device.

**Persona adapters**: switch or import character adapters from Settings → MiniCPM. Bundled: a neko-style adapter fine-tuned on neko30k.

---

### pet-forge: Custom Character Toolkit

Two routes for building pet characters:

**SVG route** (for precise animation): `PNG → remove background → vtracer vectorization → structured SVG → CSS animation`. Small files, exact loops, every keyframe editable, no API costs.

**APNG route** (for richer visuals): `prompt → AI reference image → anchor-frame video generation → chroma-key compositing → .apng`. More visual expressiveness, but requires an image/video generation API and frequent retakes.

**Hybrid**: APNG carries natural motion, SVG carries precise effects (particles, glows, typography).

A demo in the README compares the same pear-shaped character processed two ways: vtracer gave 13 anonymous paths, ~21KB, minimal semantic structure. GPT-5.5 Pro writing SVG directly gave 15 semantically-named paths, ~12KB, grouped by body region, immediately animatable. Model-written SVG is worth taking seriously.

**Codex Skill**: pet-forge has a `SKILL.md` at the repo root — load it as a Codex Skill and let Codex walk through the character-building workflow using the repo's routes, templates, and tools.

---

### How They Work Together

1. Use **pet-forge** + Codex to build a custom SVG/APNG character
2. Import it into **MiniCPM-Desk-Pet** as a persona adapter
3. The pet runs MiniCPM5-1B locally, monitors your coding agent, and narrates progress in your own character's appearance

The full pipeline is cloud-free (except for the APNG video generation step).

---

### License Notes

- **MiniCPM-Desk-Pet**: AGPL-3.0. Modified versions must be released under the same license. Check the network service clause for commercial use.
- **pet-forge**: MIT. No restrictions.
- **MiniCPM5-1B weights**: governed by OpenBMB's separate model license, not AGPL.

---

> AGPL-3.0 open source — verify terms before commercial use. pet-forge is MIT, no restrictions. For technical reference only.
