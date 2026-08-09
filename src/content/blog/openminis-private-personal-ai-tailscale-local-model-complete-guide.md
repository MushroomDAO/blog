---
title: "OpenMinis 实测 + 隐私架构完全指南：本地大模型 + Tailscale，个人数据永不出家门"
titleEn: "OpenMinis Hands-On and a Complete Privacy Architecture Guide: Local Models Plus Tailscale, Data Never Leaves Home"
description: "OpenMinis 是一个开源 iOS/Android AI Agent，能直接访问你的日历、健康、照片、提醒事项、HomeKit，内置 Alpine Linux 环境。但它默认接外部大模型——你的私人数据就这样发走了。本文分析 OpenMinis 架构，给出完整的隐私优先方案：本地大模型（Ollama/llama.cpp）+ Tailscale 组网，手机 Agent 调用家里电脑的模型，数据全程不出内网。"
descriptionEn: "OpenMinis is an open-source iOS/Android AI agent with native access to Calendar, HealthKit, Photos, Reminders, HomeKit, and a built-in Alpine Linux shell. But it defaults to cloud LLMs — sending your personal data out. This guide analyzes OpenMinis' architecture and delivers a complete privacy-first alternative: local LLM (Ollama/llama.cpp) + Tailscale mesh, with your phone agent calling your home machine's model. Your data never leaves your network."
pubDate: "2026-08-05"
updatedDate: "2026-08-05"
category: "Tech-News"
tags: ["个人AI助理", "OpenMinis", "隐私保护", "Tailscale", "本地大模型", "Ollama", "开源", "Mycelium"]
heroImage: "../../assets/images/openminis-private-personal-ai-tailscale-local-model-complete-guide-banner.jpg"
---

*by Mycelium Protocol*

---

你的手机里有一份完整的你：日历记录你去哪、和谁见面；健康 App 知道你几点睡、心率是多少；照片里有你的脸、你孩子的脸、你的地址；提醒事项记着你在想什么、在担心什么。

**OpenMinis** 把 AI Agent 直接接进了这些数据——它能读你的 HealthKit、写你的 Calendar、控制你的 HomeKit、执行你手机里的快捷指令，内置了一个完整的 Alpine Linux 环境。这是真正的个人 AI 助理，不是玩具。

问题在于：它默认接的是 Claude、GPT、Gemini。

你的健康数据、日程、照片，通过 API 密钥，完整地发给了 Anthropic / OpenAI / Google 的服务器。一旦你接了外部大模型，**那个模型就掌握了你整个人的全部数据**。

这篇文章的目标：把 OpenMinis 的能力保留，把数据风险清零。

完整方案：本地大模型（Ollama）+ Tailscale 组网 + OpenMinis 自定义 endpoint，手机上的 Agent 调用家里电脑的模型，数据全程不出内网。

---

## OpenMinis 是什么

**[OpenMinis](https://github.com/OpenMinis/OpenMinis)**（GPLv3，iOS/Android/macOS/visionOS）是目前功能最完整的开源移动端 AI Agent。

麦克斯托瑞（MacStories）创始人 Federico Viticci 的评价：

> "the most impressive indie app I've seen in a while"

知乎评价："在很大程度上实现甚至局部超越了 Apple Intelligence"。

### 核心能力矩阵

| 能力层 | 具体功能 |
|--------|---------|
| **设备集成** | HealthKit、Calendar、Reminders、Contacts、HomeKit、Bluetooth、Location、Photos、Speech、Clipboard |
| **计算环境** | 内置 Alpine Linux（iOS 上基于 iSH ARM64 fork，Android 基于 PRoot）|
| **浏览器自动化** | 打开网页、填表、截图、提取内容 |
| **Skills 系统** | SKILL.md 格式，可导入自定义技能 |
| **持久化 Memory** | 跨会话记忆 |
| **Workspaces** | 多上下文工作区，`minis://workspace/` 寻址 |
| **MCP 支持** | 通过环境变量连接自托管 MCP 服务 |

### 它能做哪些真实任务

这些是社区真实在用的工作流，不是 Demo：

- **拍一张饭的照片 → 自动记营养到 Apple Health**（AI 识别菜品、估算热量、写入 HealthKit）
- **设闹钟时自动拉 X 时间线摘要 → TTS 合成 → 用 AI 音频叫醒你**（Shortcuts 触发 Minis）
- **把 Telegram 群消息 → 提取 bug 和待办 → 去重 → 写入 Apple Reminders**
- **把分享进来的链接/消息 → 自动创建带地点和时间的日历事件**
- **Obsidian vault 挂载 → 在 Linux 环境里研究、写 Markdown、存回 vault**

这就是「AI 真的接管了手机」的样子——不是和 AI 聊天，而是 AI 帮你操作手机上的 App。

### 它怎么工作（架构简述）

```
用户请求
   ↓
Agent Loop（对话 + 工具调用规划）
   ↓
工具层:
   ├── 设备工具（HealthKit / Calendar / Reminders / HomeKit…）
   ├── Alpine Linux Shell（安装包、执行脚本、处理文件）
   ├── 浏览器自动化
   └── MCP Clients（连外部服务）
   ↓
LLM 推理（你配置的 Provider）
   ↓
结果 + 行动
```

**关键一步**：「LLM 推理」这一层，用的是你填入的 API Key 对应的外部服务。你的工具调用结果——包含你的健康数据、日历内容——作为 context 发给了那个服务。

---

## 隐私悖论：越好用，泄露越多

这是接入外部大模型的 AI 助理无法回避的结构性问题。

当 OpenMinis 帮你分析睡眠数据时，它要把 HealthKit 的 Sleep Analysis 数据作为 context 发给 Claude/GPT。当它帮你整理日历时，你未来三个月的行程发出去了。当它分析一张照片时，照片内容（至少是描述）发出去了。

这不是 OpenMinis 的问题，这是「把个人数据喂给外部 LLM」这个模式本身的问题。

| 场景 | 发出去的数据 |
|------|------------|
| 分析睡眠 | 你的起床时间、入睡时间、心率变化 |
| 日历摘要 | 所有日程、地点、参与者 |
| 照片分析 | 照片内容描述、可能的 EXIF 元数据 |
| 健康趋势 | 运动、血压、月经周期、用药记录 |
| 家庭联系人 | 家人姓名、手机号、关系 |

你把这些数据给任何一家公司，他们就拥有了比你自己更完整的你的画像。

---

## 完整隐私方案：本地模型 + Tailscale

解法很清晰：**把「LLM 推理」这一层替换成你控制的本地模型**，而且不依赖手机算力，通过 Tailscale 把家里的电脑变成你的私有 AI 后端。

```
手机（OpenMinis）
   │
   │  Tailscale 加密隧道（零公网暴露）
   │
   ↓
家里的电脑（Ollama / llama.cpp）
   │
   ├── 模型在本地跑推理
   ├── 数据永远不出内网
   └── 你完全控制模型和日志
```

### 为什么是 Tailscale？

Tailscale 基于 WireGuard，在你的设备之间建立点对点加密隧道：

- **零端口暴露**：你的 Ollama 服务不需要公网 IP 或端口转发
- **穿透 NAT**：手机 4G/5G 网络下也能连回家里（NAT traversal）
- **设备认证**：只有你 Tailscale 账号里的设备能互访
- **流量加密**：WireGuard 级别的端到端加密
- **免费套餐够用**：100 台设备，足够个人使用

### 架构图（详细）

```
┌─────────────────────────────────┐
│  iPhone / iPad                  │
│  OpenMinis                      │
│  ┌─────────────────────────┐    │
│  │ Agent Loop              │    │
│  │  ├─ HealthKit Tool      │    │
│  │  ├─ Calendar Tool       │    │
│  │  ├─ Reminders Tool      │    │
│  │  ├─ HomeKit Tool        │    │
│  │  └─ Linux Shell         │    │
│  └───────────┬─────────────┘    │
└──────────────│──────────────────┘
               │ HTTPS
               │ (OpenAI-compatible API)
               │
    ─── Tailscale VPN ────────────
               │ WireGuard 加密
               │
┌──────────────│──────────────────┐
│  家里的 Mac / Linux 服务器       │
│                                 │
│  Ollama（本地模型服务）          │
│  http://100.x.x.x:11434        │
│                                 │
│  已加载的模型：                  │
│  ├─ qwen3:32b（中文强，推荐）   │
│  ├─ llama3.3:70b（英文强）      │
│  └─ qwen3:8b（轻量备用）        │
└─────────────────────────────────┘
```

---

## 第一步：在电脑上装 Ollama

### macOS（Apple Silicon 推荐）

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型（选一个适合你显存的）
ollama pull qwen3:32b      # 32B，需要 ~20GB 内存，中文最强
ollama pull llama3.3:70b   # 70B，需要 ~45GB 内存，英文最强
ollama pull qwen3:8b       # 8B，需要 ~5GB 内存，M1/M2 基础款可用

# 验证运行
ollama run qwen3:8b "你好，这是测试"
```

### Linux（NVIDIA GPU）

```bash
curl -fsSL https://ollama.com/install.sh | sh

# 如果有 GPU，Ollama 自动检测并使用
ollama pull qwen3:32b

# 让 Ollama 监听所有接口（Tailscale 需要）
# 编辑 /etc/systemd/system/ollama.service
# 在 [Service] 下添加：
# Environment="OLLAMA_HOST=0.0.0.0:11434"
systemctl restart ollama
```

### 模型选型参考

| 模型 | 参数 | 内存需求 | 中文能力 | 适合硬件 |
|------|------|---------|---------|---------|
| qwen3:8b | 8B | ~5 GB | 优秀 | M1/M2 8GB+ |
| qwen3:14b | 14B | ~9 GB | 优秀 | M2 16GB+ |
| qwen3:32b | 32B | ~20 GB | 极强 | M2 Ultra 32GB+ |
| llama3.3:70b | 70B | ~45 GB | 良好 | M3 Ultra 192GB |
| gemma3:27b | 27B | ~17 GB | 良好 | M3 Max 48GB+ |

**日历/健康类任务不需要最强模型**：日程整理、健康分析、备忘录处理，qwen3:14b 已经够用。70B 主要在需要复杂推理（写代码、深度分析）时才有明显优势。

---

## 第二步：配置 Tailscale

### 安装（电脑端）

```bash
# macOS
brew install tailscale
# 或下载 App：https://tailscale.com/download

# Linux
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### 安装（手机端）

- iOS：App Store 搜索 Tailscale
- Android：Google Play 搜索 Tailscale

两端用同一个账号登录，Tailscale 自动建立隧道。

### 获取你电脑的 Tailscale IP

```bash
tailscale ip -4
# 输出类似：100.64.x.x
```

### 验证连通性（在手机 Tailscale App 里）

```
ping 100.64.x.x
```

或者在手机浏览器访问 `http://100.64.x.x:11434/api/tags`，能看到已下载的模型列表就通了。

---

## 第三步：在 OpenMinis 配置本地模型

OpenMinis 支持任何 OpenAI 兼容 API。Ollama 原生提供这个接口。

### 配置路径

1. 打开 OpenMinis → **Settings → AI Providers**
2. 选择 **Custom / OpenAI-Compatible**
3. 填入：

```
Base URL: http://100.64.x.x:11434/v1
API Key:  ollama   （任意字符串，Ollama 不验证 key）
Model:    qwen3:32b  （或你下载的模型名）
```

4. 保存，发一条测试消息确认连通

**就这样。** 从这一刻起，所有推理在你家里的机器上跑，OpenMinis 读取的健康数据、日历内容、照片描述，全程只在你的设备和你的电脑之间流动。

---

## 第四步：给 OpenMinis 配专属 Skills

Skills 是 OpenMinis 的能力扩展系统。一个 SKILL.md 文件告诉 Agent 在什么场景做什么。

### 隐私优先的健康分析 Skill（示例）

```markdown
---
name: health-privacy-analysis
description: >
  分析 Apple Health 数据（睡眠、运动、心率、步数）。
  触发词：健康报告、睡眠分析、运动数据、心率趋势。
  所有数据只在本地处理，不调用任何外部 API。
---

## 工作流

1. 用 HealthKit 工具读取指定时间范围的数据
2. 在本地 Linux Shell 里用 Python 处理和可视化数据
3. 用自然语言给出洞察和建议
4. 生成的报告存到本地文件，不上传

## 隐私声明

本 Skill 不调用任何需要网络的工具。所有数据处理在设备本地完成。
```

### 推荐配合的社区 Skills

| Skill | 来源 | 功能 |
|-------|------|------|
| `health-sleep-analysis` | MinisSkills | 睡眠数据深度分析 |
| `github-trending` | MinisSkills | GitHub 趋势报告（从本地 Linux 抓取） |
| `qbt-hub` | MinisSkills | 控制家里的 qBittorrent |
| 自定义日历周报 | 自建 | 每周日程汇总 + 下周规划 |

Skills 仓库：[OpenMinis/MinisSkills](https://github.com/OpenMinis/MinisSkills)

---

## 进阶：MCP 连接本地服务

OpenMinis 支持 MCP（Model Context Protocol），可以通过 Tailscale 把家里跑的 MCP 服务暴露给手机 Agent。

### 在 OpenMinis 配置 MCP

**Settings → Environment Variables** 添加：

```
OLLAMA_MCP_URL=http://100.64.x.x:3000
```

然后在 Skills 里通过 MCP 客户端调用本地服务，比如：

- **本地 Obsidian vault**（通过 obsidian-mcp）
- **本地文件系统**（通过 filesystem-mcp）
- **本地 SQLite 数据库**（存你的自定义记录）
- **本地 Home Assistant**（智能家居控制）

这样你不仅是「用本地模型」，而且是「把整套智能家居和本地数据库接入了 Agent」。

---

## 硬件推荐清单

### 入门级（日常任务够用）

| 设备 | 统一内存 | 可跑模型 | 月均耗电 |
|------|---------|---------|---------|
| Mac Mini M4 | 16 GB | qwen3:8b | 约 ¥8 |
| Mac Mini M4 Pro | 24 GB | qwen3:14b | 约 ¥10 |

**为什么推荐 Mac Mini**：静音、功耗低（推理时约 25–40W）、7×24 小时开机也不心疼电费，Apple Silicon 的统一内存架构跑 LLM 远比同内存量的独显快。

### 主力级（复杂推理 + 多用户）

| 设备 | 统一内存 | 可跑模型 | 适用场景 |
|------|---------|---------|---------|
| Mac Studio M4 Max | 48 GB | qwen3:32b | 家庭/小团队 |
| Mac Studio M4 Ultra | 96 GB | llama3.3:70b | 需要旗舰推理能力 |

### Linux 服务器方案（有 NVIDIA GPU 的话）

```
RTX 4090（24GB）→ 可跑 qwen3:32b（4-bit 量化）
RTX 4090 × 2   → 可跑 70B 级别模型（4-bit）
```

---

## 隐私架构的四条原则

这个方案之所以能成立，有四条底线：

**1. 模型权重在你的机器上**

Ollama 把模型文件下载到 `~/.ollama/models/`。推理在你的 CPU/GPU/NPU 上跑，不联网，不发遥测。

**2. 数据不离开内网**

Tailscale 建立的是点对点加密隧道。手机发出的 API 请求，经过 WireGuard 加密后直接到你的电脑，不经过 Tailscale 的服务器（Tailscale 只做 NAT 穿透的 relay，实际通信是 P2P）。

**3. API Key 不存在**

你的「API Key」是 `ollama`——这个字符串没有任何价值，Ollama 不做认证。没有密钥泄露的风险。

**4. 你控制日志**

外部 AI 服务有使用日志，可能用于训练。你的 Ollama 服务，日志在你的机器上，想删就删，想关就关。

---

## 性能预期和局限

诚实地说，本地模型 vs 外部 API 不是平等替换。

| 维度 | Ollama（本地） | Claude / GPT（外部 API） |
|------|--------------|------------------------|
| 推理速度 | Mac Mini M4：约 20–40 tok/s | 约 80–150 tok/s |
| 能力上限 | qwen3:32b / llama3.3:70b | Claude Opus 5 / GPT-5 |
| 复杂推理 | 良好 | 优秀 |
| 中文能力 | qwen3 系列优秀 | 优秀 |
| 隐私 | 完全私有 | 数据发出去了 |
| 成本 | 一次性硬件 | 按 token 计费 |

**在哪些场景下本地模型完全够用**：
- 日历整理、周报生成
- 健康数据分析
- 备忘录/提醒事项处理
- 照片分类和描述
- 智能家居控制
- 本地文件处理和搜索

**在哪些场景下外部模型有明显优势**：
- 需要最新信息（本地模型有知识截止日期）
- 极复杂的代码生成和调试
- 需要超长上下文（>32K tokens）
- 多模态高质量图像理解

**折中方案**：日常隐私敏感任务用本地模型，偶尔需要顶级推理时，在 OpenMinis 里切换到外部 API——但在发送之前，把 context 里的敏感信息手动清除。

---

## 快速启动 Checklist

```
□ 电脑安装 Ollama 并下载模型
  ollama pull qwen3:14b

□ 让 Ollama 监听所有接口
  OLLAMA_HOST=0.0.0.0:11434 ollama serve

□ 电脑安装 Tailscale 并登录
  记下 Tailscale IP（100.x.x.x）

□ 手机安装 Tailscale，同账号登录
  验证：浏览器访问 http://100.x.x.x:11434/api/tags

□ 安装 OpenMinis（App Store 或 TestFlight）

□ OpenMinis → Settings → AI Providers → Custom
  Base URL: http://100.x.x.x:11434/v1
  API Key:  ollama
  Model:    qwen3:14b

□ 授权 OpenMinis 访问 HealthKit / Calendar / Reminders
  （首次使用会弹出系统权限请求）

□ 发一条测试："分析我今天的步数目标完成情况"

□ 确认数据没有离开内网（Ollama 终端日志里能看到请求）
```

---

## 关于 OpenMinis 本身的现状

OpenMinis 在 2026 年 7 月已宣布完全开源（GPLv3）。几个关键数据点：

- App Store 已上架（iOS 16+ / macOS 13+ / visionOS 1.0+）
- Android APK 在 GitHub Releases 发布（预览版）
- TestFlight Beta 持续迭代
- 技术架构：iOS 端 Swift/SwiftUI，Android 端 Kotlin/Compose
- Linux 沙箱：iOS 用 iSH ARM64 fork，Android 用 PRoot
- Skill 格式与 Claude Code、Codex 的 Skills 格式兼容

仓库：[github.com/OpenMinis/OpenMinis](https://github.com/OpenMinis/OpenMinis)

---

## 结语：数据主权是真实问题

「把个人数据发给外部 AI」这件事，在 2026 年还没有被足够严肃地对待。

你给一个外部 AI 服务接入健康数据，本质上是在让一家商业公司的服务器永久持有你的生理信息。你不知道这些数据被存了多久、用于什么目的、在什么条件下会被访问。服务条款里通常有一句话说「我们可能用你的数据改善服务」。

本文描述的方案不是偏执——它是在技术上可行、成本在 Mac Mini 层级可接受的现实选择。你用自己的电脑跑推理，通过 Tailscale 加密隧道连回来，OpenMinis 的 Agent 能力全部保留，只是不再把你的日历和心率发给硅谷的服务器。

**数据在哪里，控制权就在哪里。**

---

**资源链接**

- OpenMinis 仓库：[github.com/OpenMinis/OpenMinis](https://github.com/OpenMinis/OpenMinis)
- MinisSkills（社区技能）：[github.com/OpenMinis/MinisSkills](https://github.com/OpenMinis/MinisSkills)
- AwesomeMinis（社区用例）：[github.com/OpenMinis/AwesomeMinis](https://github.com/OpenMinis/AwesomeMinis)
- Ollama 官网：[ollama.com](https://ollama.com)
- Tailscale 官网：[tailscale.com](https://tailscale.com)
- OpenMinis App Store：[apps.apple.com/app/id6759188481](https://apps.apple.com/app/id6759188481)
- TestFlight Beta：[testflight.apple.com/join/3BdkA5c3](https://testflight.apple.com/join/3BdkA5c3)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## OpenMinis + Local LLM + Tailscale: A Complete Guide to a Truly Private Personal AI

*by Mycelium Protocol*

Your phone holds a complete portrait of you. Your calendar records where you go and who you meet. Health tracks when you sleep and what your heart rate does. Photos contain your face, your children's faces, your home address. Reminders capture what you're thinking about and worried about.

**OpenMinis** plugs an AI agent directly into all of that — it can read your HealthKit, write to your Calendar, control HomeKit, execute Shortcuts, and it runs a full Alpine Linux environment on-device. This is a real personal AI assistant, not a toy.

The catch: it defaults to Claude, GPT, and Gemini.

Your health data, your schedule, your photos — sent via API key to Anthropic's, OpenAI's, or Google's servers. Connect an external LLM and that company holds your complete life data.

This guide keeps OpenMinis' capabilities intact while eliminating the privacy risk: local LLM (Ollama) + Tailscale mesh networking + custom endpoint in OpenMinis. Your phone agent calls your home machine's model. Your data never leaves your network.

---

### What OpenMinis Does

**[OpenMinis](https://github.com/OpenMinis/OpenMinis)** (GPLv3, iOS/Android/macOS/visionOS) is the most feature-complete open-source mobile AI agent available.

MacStories' Federico Viticci: *"the most impressive indie app I've seen in a while."*

**What it can actually access:**

| Layer | Capabilities |
|-------|-------------|
| Device integration | HealthKit, Calendar, Reminders, Contacts, HomeKit, Bluetooth, Location, Photos, Speech, Clipboard |
| Compute | Full Alpine Linux on-device (iSH ARM64 fork on iOS, PRoot on Android) |
| Browser | Navigate, fill forms, screenshot, extract content |
| Skills | SKILL.md format — import or write custom workflows |
| MCP | Connect self-hosted MCP servers via environment variables |

**What people actually use it for:**

- Photograph a meal → estimate macros → write to Apple Health automatically
- Morning alarm → pull X timeline → summarize → synthesize TTS → play as wake-up audio
- Telegram group messages → extract bugs and action items → deduplicate → file into Apple Reminders
- Share a link or message → automatically create a calendar event with time and location
- Mount an Obsidian vault in the Linux sandbox → research and write Markdown → save back

That's not "chatting with AI." That's the AI operating your phone.

---

### The Privacy Paradox

When OpenMinis analyzes your sleep data, it sends your HealthKit Sleep Analysis as context to Claude/GPT. When it summarizes your calendar, your next three months of appointments go with it. When it analyzes a photo, the image content is transmitted.

| Scenario | Data sent to external servers |
|----------|------------------------------|
| Sleep analysis | Wake time, sleep time, heart rate variability |
| Calendar summary | All appointments, locations, attendees |
| Photo analysis | Image content, possible EXIF metadata |
| Health trends | Exercise, blood pressure, medication records |
| Contacts | Family members' names, phone numbers, relationships |

One API connection and a commercial company's servers permanently hold your physiological and behavioral profile.

---

### The Complete Privacy Architecture

Replace the LLM inference layer with a model you control, accessed through Tailscale's encrypted tunnel:

```
iPhone (OpenMinis)
    │
    │  Tailscale encrypted tunnel (WireGuard, P2P)
    │
    ↓
Home Mac / Linux server (Ollama)
    │
    ├── Model runs locally (qwen3:32b / llama3.3:70b)
    ├── Data never leaves your network
    └── You control the model and logs
```

**Why Tailscale:**
- Zero port exposure — Ollama never needs a public IP
- NAT traversal — works on mobile 4G/5G anywhere in the world
- Device authentication — only your Tailscale account's devices can connect
- WireGuard encryption — end-to-end
- Free tier covers 100 devices (personal use)

---

### Setup: Step by Step

**Step 1 — Install Ollama on your machine:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:14b   # good for most personal assistant tasks
```

Make Ollama listen on all interfaces:
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Step 2 — Install Tailscale on both devices:**

```bash
# macOS
brew install tailscale

# Linux
curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up
```

Install the Tailscale app on your phone, log in with the same account. Get your machine's Tailscale IP: `tailscale ip -4` (will be 100.x.x.x).

**Step 3 — Configure OpenMinis:**

Settings → AI Providers → Custom / OpenAI-Compatible:
```
Base URL:  http://100.64.x.x:11434/v1
API Key:   ollama
Model:     qwen3:14b
```

Done. Every inference now runs on your home machine.

---

### Model Selection

| Model | RAM needed | Chinese | Use case |
|-------|-----------|---------|---------|
| qwen3:8b | ~5 GB | Excellent | M1/M2 base |
| qwen3:14b | ~9 GB | Excellent | M2 16GB+ |
| qwen3:32b | ~20 GB | Outstanding | M2 Ultra 32GB+ |
| llama3.3:70b | ~45 GB | Good | M3 Ultra |

Calendar, health analysis, and reminders management work well with qwen3:14b. The 70B models mainly help with complex reasoning, code generation, and deep analysis.

---

### Hardware Recommendations

**Entry level** (daily personal assistant tasks):
- Mac Mini M4 (16 GB) → qwen3:8b, ~20–40 tok/s, ~25W idle
- Mac Mini M4 Pro (24 GB) → qwen3:14b

**Main setup** (comfortable headroom for complex tasks):
- Mac Studio M4 Max (48 GB) → qwen3:32b
- Mac Studio M4 Ultra (96 GB) → llama3.3:70b

Mac Mini is the recommendation for most people: silent, low power (~25–40W under inference load), runs 24/7 without significant electricity cost, and Apple Silicon's unified memory architecture handles LLM inference far better than discrete GPU configurations of similar VRAM.

---

### The Four Privacy Guarantees

**1. Model weights live on your machine** — Ollama stores models in `~/.ollama/models/`. Inference runs on your CPU/GPU/NPU with no network calls.

**2. Data stays on your network** — Tailscale builds a peer-to-peer WireGuard tunnel. API requests from your phone travel encrypted directly to your machine, not through Tailscale's servers (Tailscale only brokers the NAT traversal; actual traffic is P2P).

**3. No real API key** — Your "API key" is the string `ollama`. It has no value; Ollama doesn't authenticate requests. No credential leak risk.

**4. You own the logs** — External AI services log your usage and may use it for training. Your Ollama instance: logs are on your machine, deletable, configurable, or simply off.

---

### Honest Limitations

Local models are not a drop-in replacement for frontier cloud APIs:

| Dimension | Ollama (local) | Claude/GPT (API) |
|-----------|---------------|-----------------|
| Speed | Mac Mini M4: ~20–40 tok/s | ~80–150 tok/s |
| Capability ceiling | qwen3:32b / llama3.3:70b | Claude Opus 5 / GPT-5 |
| Complex reasoning | Good | Excellent |
| Privacy | Fully private | Data sent out |
| Cost | One-time hardware | Per-token billing |

**Where local is fully adequate**: calendar management, health data analysis, reminders processing, photo description, smart home control, local file search.

**Where cloud has clear advantages**: tasks requiring current web knowledge, extremely long context (>32K tokens), top-tier code generation.

Practical middle ground: use local for all privacy-sensitive daily tasks; when you genuinely need frontier-level reasoning, switch to an external API in OpenMinis — but manually strip sensitive context before sending.

---

### Data Sovereignty Is a Real Issue

In 2026, connecting personal health data to an external AI service means a commercial company's servers permanently hold your physiological profile. Terms of service typically include a line about using your data to "improve services."

The architecture described here isn't paranoid — it's a realistic choice that's technically feasible and economically accessible at the Mac Mini price point. You run inference on your own hardware, encrypted tunnel connects your phone, OpenMinis' full agent capabilities are preserved. You just stopped sending your calendar and heart rate to servers in Silicon Valley.

**Where your data lives is where your control is.**

---

**Resources**

- OpenMinis repo: [github.com/OpenMinis/OpenMinis](https://github.com/OpenMinis/OpenMinis)
- MinisSkills: [github.com/OpenMinis/MinisSkills](https://github.com/OpenMinis/MinisSkills)
- AwesomeMinis: [github.com/OpenMinis/AwesomeMinis](https://github.com/OpenMinis/AwesomeMinis)
- Ollama: [ollama.com](https://ollama.com)
- Tailscale: [tailscale.com](https://tailscale.com)
- App Store: [apps.apple.com/app/id6759188481](https://apps.apple.com/app/id6759188481)
- TestFlight Beta: [testflight.apple.com/join/3BdkA5c3](https://testflight.apple.com/join/3BdkA5c3)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
