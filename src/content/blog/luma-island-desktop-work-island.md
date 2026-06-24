---
title: "光岛：一触即发的桌面工作岛，普通人和开发者都能用"
titleEn: "Luma Island: One Touch, Work Starts — A Desktop Work Island for Everyone"
description: "光岛（luma-island-builder）是一个 Codex Skill，引导你用对话生成一个桌面边缘的小工作台——打开常用链接、复制资料、记录待办、运行脚本，一键触达，无需任何启动成本。"
descriptionEn: "Luma Island (luma-island-builder) is a Codex Skill that guides you through building a small desktop edge launcher — open links, copy snippets, capture todos, run scripts — one touch, task starts. No prior dev experience required."
pubDate: "2026-06-24"
updatedDate: "2026-06-24"
category: "Tech-News"
tags: ["桌面工具", "Codex Skill", "效率工具", "Electron", "AI编程", "个人工作流"]
heroImage: "../../assets/images/luma-island-desktop-work-island-banner.jpg"
---

> **一句话结论（BLUF）**：光岛不是桌宠，不是漂亮概念图——它是一个真正能跑起来的桌面工作小岛，把你每天重复的高频动作塞进屏幕边缘的一个点击里。普通人可以通过对话引导在 30 分钟内建出第一版；开发者可以自定义 Electron 架构、模块类型和本地脚本，把它变成真正属于自己的效率层。

GitHub：https://github.com/fxyadela/luma-island-builder  
作者：fxyadela · MIT · TypeScript / Electron / Vite

---

## 一、你每天在哪些"小摩擦"上浪费时间？

打开项目要找文件夹，复制常用回复要翻聊天记录，查 AI 用量要切换好几个 Tab，记一个临时待办还要想用哪个 App——这些动作每次只要几秒钟，但叠加起来，一天能消耗你几十次注意力切换。

**光岛（Luma Island）** 的目标是把这些动作全部收进屏幕边缘的一个小工作台。点一下，任务开始。不找、不切、不等。

---

## 二、光岛是什么？和桌宠有什么区别？

光岛是一个**可运行的跨平台桌面工作台**，基于 Electron + Vite 构建，能在 macOS、Windows、Linux 上运行。

它**不是**：
- 桌面宠物皮肤（不是装饰品）
- 漂亮的概念截图（不是做完就扔的 mockup）
- 需要账号和云同步的 SaaS 工具

它**是**：
- 一个悬浮在桌面边缘的轻量工作台
- 每个模块对应一个真实动作：打开、复制、记录、运行
- 配置存本地，不依赖网络，不需要账号

---

## 三、普通人怎么用？30 分钟建出第一版

### 前置条件

你需要安装 **Codex**（OpenAI 的代码助手 CLI，需要有 OpenAI 账号）。

安装光岛 Skill：

```bash
# macOS / Linux
mkdir -p ~/.codex/skills
git clone https://github.com/fxyadela/luma-island-builder.git ~/.codex/skills/luma-island-builder

# Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills"
git clone https://github.com/fxyadela/luma-island-builder.git "$env:USERPROFILE\.codex\skills\luma-island-builder"
```

安装后重启 Codex。

### 和 Codex 对话，一步步建出你的光岛

在 Codex 里输入：

```
用 $luma-island-builder 帮我做一个光岛。第一版只要 3 个模块：打开项目、复制通用资料、记录待办。
```

Skill 会**主动引导你**，不需要你从空白页开始想：

**第 1 步——给你的光岛取名**

选一个预设：工作光岛、创作者光岛、AI 光岛、客户跟进光岛，或者自定义。

**第 2 步——选主要用途**

打开入口 / 复制资料 / 模板回复 / 待办记录 / 状态显示 / 运行脚本，选你最需要的。

**第 3 步——定模块数量**

推荐先做 3 个，把它们跑通最重要。5 个是标准 MVP，8 个适合功能更多的场景。

**第 4 步——选外观**

收起时的样式：太极额度 / 冰箱门 / 液态胶囊，或者上传图片 / 描述自定义。

**第 5 步——逐个配置每个模块**

比如：
- `快捷入口`：目标 URL 或本地文件夹路径
- `资料复制`：一段你常用的文字（联系方式、介绍词、固定格式）
- `待办记录`：存哪里（本地 JSON / 指定文件）

**第 6 步——构建并验证**

Codex 生成代码，本地跑起来，验证每个模块点击后真的有结果。

### 验收标准：第一版算完成的 6 个条件

1. 能看到光岛
2. 点击可以打开
3. 每个模块点击有真实结果
4. 收起时显示正常（没有 NaN 或空白）
5. 可以在界面里改配置，不用改代码
6. 知道用了哪些系统权限

---

## 四、开发者如何深度定制？

### 架构概览

光岛基于 **Electron + Vite**，三层结构：

```
主进程（main process）
├── 创建悬浮窗口（always-on-top, 无边框, 透明）
├── 暴露安全的 IPC 处理器
├── 打开 URL / 路径 / 应用
├── 写剪贴板
├── 读写本地 JSON 配置
└── 运行本地脚本（需用户确认）

预加载层（preload）
└── 暴露窄接口 islandApi，隔离渲染层与 Node.js

渲染层（renderer）
├── 收起态入口
├── 展开态模块面板
├── 各模块按钮
├── 配置视图
└── 状态与反馈

本地存储
├── modules.json
├── collapsed-display.json
├── variables.json
└── todos.json / stats.json
```

### 窗口配置关键参数

```javascript
new BrowserWindow({
  width: 96,
  height: 96,
  frame: false,
  transparent: true,
  resizable: false,
  alwaysOnTop: true,
  skipTaskbar: true,
  webPreferences: {
    preload: preloadPath,
    contextIsolation: true,
  },
})
```

### 8 种模块类型，按需组合

| 模块类型 | 用途 | 必填配置 |
|---|---|---|
| 快捷入口 | 打开网页、App、文件夹、项目 | 标题、URL/路径、图标 |
| 资料复制 | 复制常用文字 | 标题、文字内容 |
| 模板回复 | 填写变量生成回复 | 标题、模板、变量列表 |
| 待办记录 | 快速记录小任务 | 标题、存储目标 |
| 状态面板 | 显示配额/脚本结果/截止日期 | 标题、数据源、刷新规则 |
| 文件夹入口 | 快速打开本地工作区 | 标题、路径 |
| 本地脚本 | 运行本地命令 | 标题、命令、风险确认 |
| AI 提示词 | 复制或打开可复用 Prompt | 标题、Prompt 内容、目标 App |

### 自定义开发流程

**第一步：检查现有仓库**（如果你有已有的 Electron 项目）

检查 `package.json` 里的依赖和脚本、主进程入口、preload 桥接层、本地配置存储位置，找到窗口创建和收起/展开逻辑。

**第二步：调用 Skill 生成骨架**

```
用 $luma-island-builder 帮我在现有 Electron 项目里添加光岛功能。
现有入口文件是 src/main.ts，渲染层用 React + Vite。
先做 3 个模块：快捷入口 × 2、本地脚本 × 1。
```

**第三步：添加自定义模块**

在 `modules.json` 里增加新条目，格式参考：

```json
{
  "id": "my-custom-module",
  "type": "local-script",
  "title": "一键部署",
  "command": "bash ~/scripts/deploy.sh",
  "requireConfirm": true
}
```

**第四步：处理状态面板数据源**

如果你接了 Claude Code / Codex 用量显示，注意：
- 数据源返回空时，显示 `100%`，不要显示 `--` 或 `NaN`
- 数据源完全不可用时，用中性占位或引导用户配置

**第五步：验证**

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/luma-island-builder
```

预期输出：`Skill is valid!`

### 防踩坑清单

- 不要一上来就做插件市场，先让 3 个模块跑通
- 不要把所有模块全部展开显示，优先 3-6 个
- 示例数据只用占位符（`{{service_name}}`），不要写真实数据
- 先做手动触发动作，AI 自动化是之后的事
- 权限说明要直白，不要用"智能"或"自动"模糊表述

---

## 五、光岛解决了什么本质问题？

每天的工作流里，入口成本是真实存在但很少被计算的损耗。你不是在想"我要打开哪个 App"，你是在不停地扫描、找、切、等——每次几秒，但一天叠加起来是几十次注意力中断。

光岛把这层损耗压缩成一次点击。不是因为 AI 有多聪明，而是因为**它提前替你做了决策**：你已经配置好了，一触，就是你要的那个动作。

---

## FAQ

**Q：不会写代码也能用吗？**  
可以，Skill 的引导流程是对话式的，通过选项和问答生成代码。不需要手写一行，但需要安装 Codex CLI 和 Git。

**Q：和 Alfred / Raycast 有什么区别？**  
Alfred 和 Raycast 是全局搜索和命令台，功能更广但配置也更复杂。光岛是针对你特定工作场景定制的"私有工作台"，比搜索台更窄、更专、更快触达。

**Q：数据存在哪里？**  
全部本地 JSON 文件，没有云同步，没有账号，没有数据上传。

**Q：支持哪些平台？**  
macOS、Windows、Linux，基于 Electron 跨平台。

**Q：我能分享我的光岛给别人用吗？**  
可以。导出 `modules.json` 配置文件分享即可，对方按照自己的路径调整配置后即可复用。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: Luma Island is not a desktop pet or a concept mockup — it's a real, runnable desktop edge launcher that collapses your daily repeated actions into one click. Non-developers can build their first island in 30 minutes through guided conversation; developers can customize the Electron architecture, module types, and local scripts to make it a true personal efficiency layer.

GitHub: https://github.com/fxyadela/luma-island-builder  
Author: fxyadela · MIT · TypeScript / Electron / Vite

---

## What Micro-Frictions Are Eating Your Day?

Finding the right folder to open a project. Hunting for a template reply in your chat history. Switching between three tabs to check your AI quota. Opening a new note app just to capture a single todo. Each action takes a few seconds — but across a day, they add up to dozens of attention interruptions.

**Luma Island** collects all of these into a small, persistent launcher at the edge of your desktop. One touch. Task starts. No searching, no switching, no waiting.

---

## What Is Luma Island? How Is It Different From a Desktop Pet?

Luma Island is a **runnable cross-platform desktop work island**, built on Electron + Vite, running on macOS, Windows, and Linux.

It is **not**:
- A desktop pet skin (not decoration)
- A polished concept screenshot (not a mockup that never ships)
- A SaaS tool requiring accounts and cloud sync

It **is**:
- A lightweight floating panel at the edge of your desktop
- Each module maps to one real action: open, copy, capture, run
- Config is stored locally — no network dependency, no account needed

---

## For General Users: Build Your First Island in 30 Minutes

### Prerequisites

Install **Codex** (OpenAI's CLI code assistant — requires an OpenAI account), then install the Luma Island skill:

```bash
# macOS / Linux
mkdir -p ~/.codex/skills
git clone https://github.com/fxyadela/luma-island-builder.git ~/.codex/skills/luma-island-builder
```

Restart Codex after cloning.

### Tell Codex What You Want

```
Use $luma-island-builder to help me build a Luma Island.
First version: 3 modules only — open my project, copy my standard bio, capture todos.
```

The Skill guides you step by step — no blank page:

1. **Name your island** — pick from presets or go custom
2. **Choose the main job** — open entries, copy snippets, template replies, todos, status, scripts
3. **Choose module count** — start with 3, standard MVP is 5, larger builds go to 8
4. **Pick a collapsed style** — Taichi Quota, Fridge Door, Liquid Capsule, or describe your own
5. **Configure each module** — action target, storage method, permissions
6. **Build and verify** — Codex generates the code; run it and confirm each module produces a real result

### First-Version Acceptance Criteria

- Can see the island
- Can open it with one click
- Each module click produces a real result
- Collapsed display shows sane values (no NaN, no blank percentages)
- Can change config without touching source code
- Understand which permissions are in use

---

## For Developers: Deep Customization Guide

### Architecture at a Glance

```
main process
├── create always-on-top frameless transparent window
├── expose safe IPC handlers
├── open URLs, paths, and apps
├── write clipboard
├── read/write local JSON config
└── run confirmed local scripts

preload
└── expose narrow islandApi to renderer

renderer
├── collapsed island entry
├── expanded module panel
├── module action buttons
├── small settings view
└── status and feedback display

local storage
├── modules.json
├── collapsed-display.json
├── variables.json
└── todos.json / stats.json
```

### 8 Module Types — Mix and Match

| Type | Value | Required Config |
|---|---|---|
| Quick Entry | Open a URL, app, folder, or project | title, URL/path, icon |
| Copy Snippet | Copy reusable text | title, text content |
| Template Reply | Fill variables into a message template | title, template, variable list |
| Todo Capture | Record small tasks or notes | title, storage target |
| Status Panel | Show quota, script result, deadline | title, data source, refresh rule |
| Folder Entry | Open a local workspace | title, path |
| Local Script | Run a local command | title, command, risk confirmation |
| AI Prompt | Copy or open a reusable prompt | title, prompt, target app |

### Custom Module JSON

Add a new module to `modules.json`:

```json
{
  "id": "deploy-shortcut",
  "type": "local-script",
  "title": "One-click deploy",
  "command": "bash ~/scripts/deploy.sh",
  "requireConfirm": true
}
```

### Status Panel: Handle Missing Data Correctly

When a quota or status source returns no data:
- Show `100%` for an explicit no-usage state — never show `--`, `NaN`, or empty
- If the source is completely unavailable, use a neutral placeholder or guide the user to configure a data source

### Anti-Patterns to Avoid

- Don't build a plugin marketplace before 3 modules work
- Don't show all modules at once — prioritize 3–6 visible actions
- Use `{{placeholder}}` for example data, never real data in seed files
- Add AI automation only after the manual action works reliably
- Be explicit about permissions — never hide them behind words like "smart" or "automatic"

---

## What Problem Does Luma Island Actually Solve?

Entry cost is a real but rarely counted form of work friction. You're not thinking "which app do I open" — you're scanning, finding, switching, waiting, dozens of times a day, a few seconds each.

Luma Island compresses that layer into a single click — not because AI is clever, but because **you've already made the decision in advance**. You configured it once. After that, one touch is all it takes.

---

## FAQ

**Q: Can I use this without coding experience?**  
Yes. The Skill guides you through conversation and choices, generating the code for you. You need to install Codex CLI and Git, but no manual coding is required.

**Q: How is this different from Alfred or Raycast?**  
Alfred and Raycast are global search and command launchers — powerful but general. Luma Island is a narrowly-configured private launcher for your specific daily workflow. Narrower scope, faster access, less setup noise.

**Q: Where is my data stored?**  
Local JSON files only. No cloud sync, no account, no data uploads.

**Q: Which platforms are supported?**  
macOS, Windows, Linux — Electron covers all three.

**Q: Can I share my island config with someone else?**  
Yes. Share your `modules.json` file; they adjust paths and targets for their environment and it works.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
