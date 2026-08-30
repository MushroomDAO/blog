---
title: "ExcalidrawZ：4年，把 Excalidraw 做成真正的原生 App"
titleEn: "ExcalidrawZ: Four Years Turning Excalidraw into a Real Native App"
description: "chocoford/ExcalidrawZ ⭐1410，纯 SwiftUI 打造的 macOS/iPadOS/iOS Excalidraw 原生客户端，从1.0到2.4.3迭代4年：原生文件管理、iCloud 同步、文件历史、AI 绘图助手、MCP 服务器、LaTeX 公式、文件加密，App Store 已上架。"
descriptionEn: "chocoford/ExcalidrawZ ⭐1410 — a pure SwiftUI Excalidraw native client for macOS/iPadOS/iOS, 4 years from v1.0 to v2.4.3: native file management, iCloud sync, file history, AI drawing assistant, MCP server integration, LaTeX math tools, file encryption. Available on the App Store."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Tech-News"
tags: ["Excalidraw", "macOS", "iOS", "SwiftUI", "open source", "drawing", "MCP", "AI", "productivity", "Apple"]
heroImage: "../../assets/images/excalidrawz-native-excalidraw-macos-ios-swiftui-mcp-ai-banner.jpg"
author: "Mycelium Protocol"
---

## 一个工具能做4年，说明它在认真解决问题

[Excalidraw](https://excalidraw.com/) 是公认最好用的手绘风白板工具——但它是个网页。文件散落在浏览器下载文件夹，没有版本历史，iPad 上笔迹体验凑合，离线？不存在的。

**ExcalidrawZ**（`chocoford/ExcalidrawZ`）从 2022 年底开始做这件事：用纯 SwiftUI 重新包装 Excalidraw 核心，把它做成一个真正的 Apple 原生 App。

2026年8月，版本 **2.4.3**，⭐ **1410**，App Store 上架，macOS + iPadOS + iOS 全平台覆盖。

---

## 原生文件管理：从「乱放」到「有序」

浏览器版 Excalidraw 的文件管理就是没有文件管理——你下载一个 `.excalidraw` 文件，它在下载文件夹里等你找。

ExcalidrawZ 把绘图文件当成真正的 App 文档来管理：

- **分组和自定义排序**：你的图，按你的方式组织
- **iCloud 同步**：macOS、iPadOS、iOS 之间自动同步，画一半拿起 iPad 接着画
- **直接打开本地文件**：`.excalidraw`、`.excalidraw.png`、`.excalidraw.svg` 都认
- **临时文件和本地文件夹**：外部文件直接在 App 里编辑，不需要导入

---

## 文件历史：再也不怕改坏

ExcalidrawZ 会自动为每个 App 管理的绘图记录历史检查点。改得太远了？随时回到早期版本查看或恢复。

这是原生 App 才能做的事——浏览器版的 Excalidraw，关了标签页，一切都消失了。

---

## Apple Pencil + 原生手势

iPad 用户的体验：

- **Apple Pencil** 完整支持，包括熟悉的撤销/重做手势
- 鼠标和触控板的**滚动缩放手势**在 iPad 和 iPhone 上都能用
- **自定义工具栏顺序**，数字快捷键跟着你的配置走
- **PDF 导入**，直接在 Excalidraw 里批注
- **Mermaid 图转换**：把 Mermaid 代码粘进来，自动变成可编辑的 Excalidraw 图形

---

## AI 绘图助手

ExcalidrawZ 2.x 加入了 AI 助手，直接理解 Excalidraw 画布：

- **读图/创图/改图**：告诉 AI 你想要什么，它在画布上操作
- **图片上下文**：把截图发给 AI，让它参考画面内容
- **提案预览**：AI 生成的内容先在预览里看，满意了再应用到真实画布
- **per-file AI 可见性控制**：你可以指定某个文件对 AI 不可见
- **多端适配**：iPhone 紧凑工具栏、iPad 浮动面板、macOS 侧边检查器，三端界面各自优化

---

## MCP 服务器：让 AI 客户端直接操控 Excalidraw

这是 2.x 加入的功能里最有意思的一个：ExcalidrawZ 可以把自己暴露为一个 **MCP 服务器**，让兼容的 AI 客户端（Claude、Cursor 等）直接连进来操控画布。

两种模式：

| 模式 | 能力 |
|---|---|
| **Basic** | 标准 `excalidraw-mcp` 绘图工作流 |
| **Optimized** | 当前文件编辑、文件导航、历史记录、画布检查、导出、Library 工作流、数学工具 |

本地 MCP 客户端通过 App 托管的 HTTP 端点连接。也就是说，你可以在 Claude Code 里说"帮我在 Excalidraw 里画一张系统架构图"，ExcalidrawZ 直接执行。

---

## 数学和图表工具

面向技术图和学习笔记的专项功能：

- **LaTeX 公式**：直接插入渲染好的数学公式，后续可在画布上二次编辑
- **函数图像**：配置坐标轴和样式，渲染函数曲线
- **数学模板**：可复用的公式模板库
- **AI 辅助公式生成**：描述你要的公式，AI 帮你写 LaTeX

---

## 文件加密和访问控制

对于敏感图纸，ExcalidrawZ 加了一套保护机制：

- **本地认证锁定**（Face ID / Touch ID / 密码）
- **加密存储**：锁定的文件及其历史检查点都加密
- **恢复密钥**：万一生物认证失败，备用访问路径
- **AI 可见性隔离**：加锁文件对 AI 不可见，AI 只能通过提案画布间接操作
- **加密备份**：独立的恢复路径

---

## 导出和分享

- PNG / SVG / PDF 导出
- `.excalidraw.png` 和 `.excalidraw.svg`：**保留可编辑性**——图片里内嵌原始绘图数据，发给别人他们也能在 Excalidraw 里继续编辑
- 剪贴板、文件、系统分享表单
- App 管理文件批量归档备份

---

## 安装

**App Store**（推荐）：直接搜 ExcalidrawZ 或访问 [App Store 链接](https://apps.apple.com/app/excalidrawz/id6636493997)

**非 App Store 版**（macOS）：
```bash
# 从 GitHub Releases 下载最新 .dmg
# 拖入 Applications，完成
```

**从源码构建**（开发者）：
```
ExcalidrawZ/Config/ 下新建 Overrides.xcconfig：
DEVELOPMENT_TEAM = <你的 Apple 开发者 Team ID>
ICLOUD_CONTAINER = <你的 iCloud 容器标识符>
```

Excalidraw 核心也单独开源：[chocoford/excalidraw (ExcalidrawZ-core 分支)](https://github.com/chocoford/excalidraw/tree/ExcalidrawZ-core)

---

## 4年的积累在哪里

从 2022 年底第一个版本，到 2026 年 v2.4.3：ExcalidrawZ 走过了一条"先做好基础、再叠加能力"的路线。

早期解决的是最基本的需求：文件管理、iCloud 同步、本地文件支持——这些是从"浏览器工具"变成"真正 App"的必要条件。

中期做的是 Apple 平台的体验打磨：Apple Pencil 支持、触控手势、工具栏自定义——这些是"用起来顺不顺"的核心。

近期加入的 AI 助手和 MCP 集成，是在稳固基础上加的新维度：让 ExcalidrawZ 不只是一个画图工具，而是一个可以被 AI 工作流直接操控的创作环境。

1410 个 Star，4 年，这个数字说明它在认真解决用户的真实问题。

---

**GitHub**: [chocoford/ExcalidrawZ](https://github.com/chocoford/ExcalidrawZ) ⭐1410  
**App Store**: [ExcalidrawZ](https://apps.apple.com/app/excalidrawz/id6636493997)  
**Discord**: [discord.gg/aCv6w4HxDg](https://discord.gg/aCv6w4HxDg)

<!--EN-->

## ExcalidrawZ: Four Years Turning Excalidraw into a Real Native App

[Excalidraw](https://excalidraw.com/) is arguably the best hand-drawn whiteboard tool available — but it's a web page. Files scatter across browser downloads, there's no version history, iPad pencil experience is mediocre, and offline use doesn't exist.

**ExcalidrawZ** (`chocoford/ExcalidrawZ`) started solving this in late 2022: wrapping the Excalidraw canvas in pure SwiftUI to build a genuine Apple-native app. August 2026 — version **2.4.3**, ⭐**1410**, on the App Store, covering macOS + iPadOS + iOS.

### Native File Management

The browser Excalidraw has no file management — you download a `.excalidraw` file and it sits in your Downloads folder. ExcalidrawZ treats drawings as real app documents:

- Organize with groups and custom sort order
- iCloud sync across macOS, iPadOS, and iOS — start drawing on your Mac, pick up your iPad
- Open `.excalidraw`, `.excalidraw.png`, and `.excalidraw.svg` directly from the filesystem
- Edit external local files in-place without importing

### File History

ExcalidrawZ automatically records checkpoints for every app-managed drawing. Went down a wrong path? Review earlier states and restore. Browser Excalidraw? Close the tab and everything is gone.

### Apple Pencil and Native Gestures

- Full **Apple Pencil** support on iPad, including the familiar undo/redo gestures
- Mouse and trackpad scroll/zoom gestures on iPad and iPhone
- **Customizable toolbar order** — number shortcuts follow your configuration
- **PDF import** — annotate PDFs directly on the canvas
- **Mermaid diagram conversion** — paste Mermaid code, get an editable Excalidraw diagram

### AI Drawing Assistant

ExcalidrawZ's built-in AI assistant understands the canvas:

- **Read / create / revise** drawings through conversation
- **Image context** — attach screenshots for the AI to reference visually
- **Proposal preview** — AI-generated content appears in a preview before touching your real canvas
- **Per-file AI visibility** — mark specific files off-limits to AI
- Three-platform UI: iPhone compact toolbar, iPad floating panel, macOS inspector

### MCP Server Integration

The most interesting 2.x addition: ExcalidrawZ can expose itself as an **MCP server**, letting any compatible AI client (Claude, Cursor, etc.) directly control the canvas.

| Mode | Capabilities |
|---|---|
| **Basic** | Standard `excalidraw-mcp` drawing workflow |
| **Optimized** | Current-file editing, file navigation, history, canvas inspection, export, library workflows, math tools |

Local MCP clients connect through an app-hosted HTTP endpoint. You can tell Claude Code "draw me a system architecture diagram in Excalidraw" and ExcalidrawZ executes it directly.

### Math and Diagram Tools

For technical drawings and study notes:

- **LaTeX formulas** — insert rendered math; edit later directly from the canvas
- **Function graphs** — configurable axes and styles
- **Math templates** — reusable formula library
- **AI-assisted formula generation** — describe the math, get the LaTeX

### File Encryption and Access Control

For sensitive drawings, ExcalidrawZ adds a protection layer:

- **Local authentication lock** (Face ID / Touch ID / passcode)
- **Encrypted storage** — locked files and their checkpoints are encrypted at rest
- **Recovery key** for fallback access
- **AI isolation** — locked files are invisible to AI; AI works through proposal canvases only
- **Encrypted backups** as an additional recovery path

### Export and Sharing

- PNG / SVG / PDF export
- `.excalidraw.png` and `.excalidraw.svg` with **preserved editability** — the original drawing data is embedded in the file; recipients can reopen it in any Excalidraw client
- Clipboard, files, system share sheet
- Batch archive of app-managed files for backup

### Install

**App Store** (recommended): search ExcalidrawZ or use the [App Store link](https://apps.apple.com/app/excalidrawz/id6636493997)

**Non–App Store (macOS)**: download the latest `.dmg` from [Releases](https://github.com/chocoford/ExcalidrawZ/releases) and drag to Applications.

### Four Years of Compounding

From the first version in late 2022 to v2.4.3 in 2026, ExcalidrawZ followed a clear progression: lay the foundation first (file management, iCloud sync, local file support — the prerequisites for being a real app rather than a browser wrapper), then build native platform quality (Apple Pencil, touch gestures, toolbar customization — what makes it feel right to use), then add new dimensions on a solid base (AI assistant, MCP server — making ExcalidrawZ not just a drawing tool but a creation environment that AI workflows can directly control).

1,410 stars. Four years. Numbers that say someone is genuinely solving real problems.

**GitHub**: [chocoford/ExcalidrawZ](https://github.com/chocoford/ExcalidrawZ) ⭐1410  
**App Store**: [ExcalidrawZ](https://apps.apple.com/app/excalidrawz/id6636493997)  
**Discord**: [discord.gg/aCv6w4HxDg](https://discord.gg/aCv6w4HxDg)
