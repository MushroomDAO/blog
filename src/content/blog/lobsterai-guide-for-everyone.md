---
title: "LobsterAI 普通人使用指南：网易有道出品，桌面 AI Agent 一句话搞定办公"
titleEn: "LobsterAI for Everyone: NetEase Youdao's Desktop AI Agent — Real Work Done with One Prompt"
description: "LobsterAI 是网易有道开源的桌面 AI Agent（MIT，5500+ Star），支持 macOS 和 Windows，内置 28 个技能——建本地系统、做数据分析、生成 PPT/视频、浏览器自动化、股票研究，还能从微信/飞书/钉钉远程控制。本文是零基础普通人入门指南。"
descriptionEn: "LobsterAI is NetEase Youdao's open-source desktop AI Agent (MIT, 5500+ stars) for macOS and Windows. 28 built-in skills cover local system building, data analysis, PPT/video generation, browser automation, stock research, and remote control via WeChat/Feishu/DingTalk. This is a beginner's guide for non-technical users."
pubDate: "2026-07-11"
updatedDate: "2026-07-11"
category: "Tech-News"
tags: ["LobsterAI", "AI Agent", "网易有道", "桌面助手", "开源", "自动化", "Office", "微信控制", "普通人指南"]
heroImage: "../../assets/images/lobsterai-guide-banner.jpg"
---

GitHub：[netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) · ⭐ 5500+ · MIT · 网易有道出品

下载地址：[lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list)

---

## LobsterAI 是什么

LobsterAI 是网易有道开源的桌面 AI Agent，支持 macOS 和 Windows。

简单说就是：**你有一台电脑，给它装上 LobsterAI，然后用一句中文告诉它你要什么，它在你电脑上真实地执行操作，把结果交给你。**

不是聊天机器人，是真的帮你干活的 Agent——操作本地文件、执行终端命令、打开浏览器、生成文档/表格/PPT、发邮件、定时任务……

对普通用户最重要的三点：
1. **下载安装即用**，不用配环境
2. **中文说话**，不用学 prompt
3. **连接微信/飞书/钉钉**，手机上远程发命令，电脑自动执行

---

## 能做什么（28 个内置技能）

LobsterAI 内置了 28 个开箱即用的技能，分几大类：

### 办公文档
| 技能 | 你可以说的话 |
|------|------------|
| Word 文档（docx） | "把这份报告草稿整理成正式文档，加目录和格式" |
| Excel 表格（xlsx） | "用这个 CSV 数据生成季度销售对比分析表" |
| PPT 演示（pptx） | "调研 AI Agent 市场现状，做成 10 页汇报 PPT" |
| PDF 处理 | "提取这个合同 PDF 里所有的金额条款" |

### 数据分析 & 可视化
| 技能 | 示例 |
|------|------|
| 数据分析 + 可视化 | "用 product-growth.xlsx 做增长分析，画折线图，总结主要驱动因素" |
| 股票分析（stock-analyzer） | "分析贵州茅台近三个月走势，给出简要研判" |
| 股票公告（stock-announcements） | "看看今天有哪些重要公告" |

### 内容创作
| 技能 | 示例 |
|------|------|
| 文章写作（article-writer） | "写一篇 2000 字的深度分析，关于 AI 对教育的影响" |
| 内容规划（content-planner） | "给我的公众号规划一个月的选题日历" |
| 日报热点（daily-trending） | "今天科技圈有什么大事，给我做个摘要" |

### 网页 & 浏览器自动化
| 技能 | 示例 |
|------|------|
| 网页搜索（web-search） | "搜索最近关于 Transformer 架构的论文" |
| Playwright 浏览器 | "打开广告投放后台，截图今天的消耗和转化数据" |
| 前端开发 | "帮我写一个计算器网页，直接能在浏览器打开" |

### 生成 AI 内容
| 技能 | 示例 |
|------|------|
| 视频生成（Remotion/Seedance） | "把这篇文章做成 60 秒解说视频" |
| 图片生成（Seedream） | "生成一张极简主义风格的产品概念图" |
| 音乐搜索 | "找几首适合专注工作的纯音乐" |

### 生活工具
| 技能 | 示例 |
|------|------|
| 天气查询 | "北京明天天气怎么样，要不要带伞" |
| 邮件收发（IMAP/SMTP） | "帮我检查收件箱，把未读邮件分类汇总" |
| 有道云笔记 | "把今天的会议记录整理保存到有道云" |
| 电影搜索 | "推荐几部适合周末看的科幻电影" |

---

## 安装（3 步，5 分钟）

### 第一步：下载安装包

进入官网 [lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list)，选择你的系统：
- **macOS**：下载 `.dmg` 文件，拖到 Applications
- **Windows**：下载 `.exe` 安装包，双击安装

> 也可以从 [GitHub Releases](https://github.com/netease-youdao/LobsterAI/releases) 下载最新版。

### 第二步：配置 AI 模型

第一次启动 LobsterAI 需要配置一个 AI 模型（大脑）：

**推荐新手选 OpenAI 或 DeepSeek：**
- OpenAI GPT-4o：去 [platform.openai.com](https://platform.openai.com) 获取 API Key，按用量收费
- DeepSeek：去 [platform.deepseek.com](https://platform.deepseek.com) 获取 API Key，价格比 OpenAI 便宜很多
- 国内用户也可以选阿里云百炼（Qwen）、月之暗面（Moonshot）等

在设置页填入 API Key，选好默认模型，完成。

### 第三步：开始对话

打开主界面，直接中文输入你的需求，按 Enter 发送。

---

## 5 个真实使用场景

### 场景 1：从 Excel 数据生成分析报告

你有一份销售数据表，想要可视化 + 分析报告：

```
把 /桌面/Q2销售数据.xlsx 做成可视化分析，
找出销售增长最快的产品和地区，
生成一份带图表的分析报告文档
```

LobsterAI 会：读取 Excel → 执行数据分析 → 生成折线图/柱状图 → 写一份 Word 报告，保存到桌面。

---

### 场景 2：一句话生成 PPT

```
调研 2026 年 AI Agent 行业现状，
整理主要玩家、技术趋势和商业化路径，
做成 12 页的投资人汇报 PPT，专业配色
```

Agent 会先搜索资料，然后组织内容，最后调用 PPTX 技能生成可编辑的 PowerPoint 文件。

---

### 场景 3：建一个本地小系统

```
我现在用 Excel 管进销存，很麻烦。
帮我做一个本地库存管理系统：
可以录入进货、出货、查看库存余量和利润，
能在浏览器里打开
```

LobsterAI 会写前端 HTML/CSS/JS + 本地数据存储逻辑，生成一个可以直接用浏览器打开的小系统，不需要安装任何服务器。

---

### 场景 4：定时任务自动化

```
每天早上 9 点，帮我搜集昨天的 AI 行业新闻，
整理成 10 条重要动态，用微信发给我
```

在「定时任务」页面创建：设置时间（每天 09:00） → 写触发提示词 → 绑定微信通知渠道 → 保存。

之后每天早上自动执行，结果发到你微信。

---

### 场景 5：用手机远程控制电脑

这是 LobsterAI 很有意思的功能：**IM 远程控制**。

绑定微信/企微/飞书/钉钉后，你出门在外，可以用手机发消息控制家里的电脑：

```
（从微信发给 LobsterAI）
帮我查一下公司今天的服务器 CPU 使用情况，
如果超过 80% 就截图发给我
```

电脑上的 Agent 收到指令 → 执行 → 把结果发回你的手机。

---

## 多 Agent 工作流：让不同专家分工协作

LobsterAI 支持创建多个 Agent，每个 Agent 有独立的角色、模型和工作目录：

比如你可以建：
- **数据分析师**：绑定 DeepSeek，专门处理数据文件
- **内容写作助手**：绑定 GPT-4o，专门写文章
- **投资研究员**：绑定 Claude，专门做股票和行业分析
- **自动化机器人**：绑定便宜的小模型，专门跑定时任务

不同任务分配给不同 Agent，既能控制成本，又能让每个 Agent 专注自己擅长的事。

---

## Expert Kits：场景化能力包

除了独立技能，LobsterAI 还提供 Expert Kits（专家套件），把常见工作流打包好：

- **数据分析套件**：Excel + 可视化 + 报告一体
- **内容创作套件**：选题 → 写作 → 排版全链路
- **投资研究套件**：股票 + 公告 + 技术分析组合

安装一个 Kit，相关技能自动配置好，不用逐一开启。

---

## 使用技巧

**1. 说清楚文件路径**

```
❌ 分析我的销售数据
✅ 分析 /桌面/2026年Q2销售.xlsx，重点看华东地区
```

**2. 说清楚你要的格式**

```
❌ 生成报告
✅ 生成一份 Word 文档，包含：执行摘要（300字）+ 数据图表 + 结论建议
```

**3. 大任务分步给**

复杂任务可以先让它做规划再执行：

```
第一步：先帮我把需求梳理一下，列出执行步骤，我确认后再开始
```

**4. 安全敏感操作会请求确认**

文件操作、终端命令、网络访问等敏感操作，LobsterAI 都会先暂停让你确认，不会未经同意就执行。这是设计上的安全机制，不是 bug。

---

## 数据和隐私

LobsterAI 的数据存储在本地：
- 会话记录：存在本机 `lobsterai.sqlite`（Electron userData 目录）
- 工作空间记忆：本地文件（`MEMORY.md` / `USER.md` 等）
- API 密钥：本地配置文件，不上传

你的对话内容会发给你配置的 AI 模型提供商（如 OpenAI），和 LobsterAI 本身无关。如果有隐私需求，可以配置本地 Ollama 模型完全离线运行。

---

## 和其他工具对比

| | LobsterAI | ChatGPT | Cursor/Claude |
|--|-----------|---------|---------------|
| 本地文件操作 | ✅ 直接读写 | ❌ | ✅ |
| 浏览器自动化 | ✅ Playwright | ❌ | ❌ |
| 微信/飞书远程控制 | ✅ | ❌ | ❌ |
| 定时任务 | ✅ | ❌ | ❌ |
| PPT/Word 生成 | ✅ 可编辑文件 | ❌ 只输出文字 | ❌ |
| 本地数据隐私 | ✅ | ❌ | 部分 |
| 开源免费 | ✅ MIT | ❌ | ❌ |

LobsterAI 最大的差异在于**真实执行**——它不只是回答你，是在你的电脑上做事。

---

## 一句话总结

LobsterAI 是目前开源桌面 AI Agent 里功能最完整的产品之一，网易有道出品，MIT 开源，不需要技术背景就能上手。

如果你有一台电脑，有些重复性的工作想自动化，或者想让 AI 帮你真正干活而不只是聊天——值得装一下试试。

---

- 官网下载：[lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list)
- GitHub：[netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) ⭐ 5500+
- 社区微信群：见官网二维码

© 2026 Author: Mycelium Protocol

<!--EN-->

## LobsterAI for Everyone: NetEase Youdao's Desktop AI Agent

GitHub: [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) · ⭐ 5500+ · MIT · by NetEase Youdao

Download: [lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list)

---

### What Is LobsterAI

LobsterAI is an open-source desktop AI Agent for macOS and Windows, built by NetEase Youdao. The core idea: tell it what you need in plain language, and it actually does the work on your real computer — reading and writing local files, running terminal commands, operating a browser, generating documents, sending emails, running scheduled jobs.

It's not a chatbot. It's an agent that executes.

Three things that matter most for non-technical users:
1. **Download and run** — no environment setup needed
2. **Plain language** — no prompting skills required
3. **WeChat/Feishu/DingTalk integration** — send commands from your phone, desktop executes

---

### 28 Built-in Skills

**Office documents**: Word/Excel/PowerPoint/PDF generation and processing

**Data analysis**: spreadsheet analysis, visual dashboards, stock research (analyzer, announcements, explorer)

**Content creation**: article writing, content planning, daily news digest

**Web & browser automation**: web search, Playwright browser automation, frontend development

**AI generation**: Remotion/Seedance video generation, Seedream image generation

**Utilities**: weather, IMAP/SMTP email, Youdao Notes, film/music search

---

### Install in 3 Steps

1. **Download**: Go to [lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list) → macOS `.dmg` or Windows `.exe`

2. **Configure AI model**: Open Settings → enter an API key. Recommended for beginners: DeepSeek (affordable) or OpenAI GPT-4o. Any OpenAI-compatible provider works.

3. **Start chatting**: Type your request in Chinese or English, hit Enter.

---

### Real Scenarios

**Excel → Analysis report**: "Analyze /Desktop/Q2_Sales.xlsx, find the fastest-growing products and regions, generate a Word report with charts." → LobsterAI reads the file, runs analysis, generates charts, writes a formatted Word document.

**One-prompt PPT**: "Research the 2026 AI Agent market. Make a 12-page investor deck covering major players, tech trends, and commercialization paths." → Searches web → organizes content → generates editable PowerPoint.

**Build a local system**: "I manage inventory in Excel. Build me a local inventory system I can open in my browser." → Generates HTML/CSS/JS app with local data storage, no server needed.

**Scheduled automation**: "Every weekday at 9 AM, collect yesterday's AI industry news and send me a digest via WeChat." → Set up in the Scheduled Tasks page, runs automatically every morning.

**Phone-to-desktop remote control**: After binding WeChat/Feishu/DingTalk, send commands from your phone and get results back — useful when you're away from your desk.

---

### Multi-Agent Workflows

Create multiple specialized agents, each with their own model, role, working directory, and IM bindings:

- Data Analyst → DeepSeek (cost-effective for data tasks)
- Content Writer → GPT-4o
- Investment Researcher → Claude
- Automation Bot → small cheap model for scheduled jobs

Different tasks go to different agents. Better results, controlled costs.

---

### Privacy and Data

All session data lives locally in `lobsterai.sqlite`. Workspace memory is local files (`MEMORY.md`, `USER.md`, etc.). API keys stay in local config — not uploaded. Your conversations go to whatever AI provider you configured (e.g., OpenAI), not to LobsterAI itself. For full offline operation, configure a local Ollama model.

Sensitive actions (file writes, terminal commands, network access) require explicit approval before execution — this is a safety feature, not a bug.

---

- Download: [lobsterai.youdao.com](https://lobsterai.youdao.com/#/download-list)
- GitHub: [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) ⭐ 5500+

© 2026 Author: Mycelium Protocol
