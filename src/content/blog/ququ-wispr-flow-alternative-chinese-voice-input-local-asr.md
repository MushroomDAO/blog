---
title: "蛐蛐 QuQu：本地中文语音输入法深度拆解，Wispr Flow 开源替代"
description: "yan5xu/ququ，2.2K 星，Wispr Flow 的开源替代方案。FunASR Paraformer-large 本地 ASR + LLM 润色，F2 按住说话松开自动粘贴，Electron + React 19。核心两个坑：无许可证声明（法律默认保留所有权利），项目已 11 个月未更新。"
pubDate: 2026-09-27
heroImage: "../../assets/images/ququ-wispr-flow-alternative-chinese-voice-input-local-asr-banner.jpg"
category: "Tech-Experiment"
tags: ["语音输入", "ASR", "本地推理", "FunASR", "开源拆解", "桌面工具"]
lang: "zh-CN"
wechatTitle: "蛐蛐QuQu：本地中文语音输入法拆解"
wechatDigest: "Wispr Flow开源替代；FunASR本地ASR+LLM润色；无许可证声明法律存疑；11个月未更新"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 项目背景

**yan5xu/ququ**（GitHub：github.com/yan5xu/ququ）——2,295 stars，231 forks，2025 年 9 月 20 日创建。

项目自述定位是「下一代中文桌面语音工作流」，直接对标 **Wispr Flow**（月费 $12 的商业语音输入软件），提供全本地、零月费的替代方案。操作逻辑一样：按住 F2 说话，松开自动转写，粘贴到光标位置。

---

## 技术架构：两阶段流水线

```
麦克风音频
    ↓
FunASR Paraformer-large（本地 ASR）
    + FSMN-VAD（端点检测）
    + CT-Transformer（标点恢复）
    ↓
[原始转录文本]
    ↓
LLM 润色层（任意 OpenAI API 兼容服务）
    ↓
过滤口头禅 / 纠正错词 / 理解上下文
    ↓
粘贴到当前光标位置
```

**ASR 层**：阿里 ModelScope 的 FunASR Paraformer-large，配合 FSMN-VAD 做说话结束检测、CT-Transformer 恢复标点。音频全本地处理，不上传。

**LLM 润色层**：接任意 OpenAI API 兼容接口，内置通义千问、Kimi、智谱的优化配置。这层是可选的——如果你只要原始转录也可以跳过。

**技术栈**：Electron + React 19 + TypeScript + Tailwind CSS + Vite，持久化用 better-sqlite3。

---

## 安装要求

- macOS 10.15+ / Windows 10+ / Linux
- Node.js 18+
- Python 3.8+（提供 `uv` 快速安装路径，也支持传统 venv 或 production 内嵌包）

Python 环境不可省，因为 FunASR 是 Python 包。这意味着部署比单语言项目更复杂，uv 路径约 2-3 分钟能搞定，但 Windows 上报告更多兼容性问题。

---

## 实用特性

- 全局热键 F2 按住录音，松手即转写粘贴，全流程无需切换窗口
- 编程术语识别：能正确输出 camelCase、snake_case、API 名称等
- 国产模型优化：针对通义千问/Kimi/智谱的润色策略有专门配置
- 历史记录：better-sqlite3 本地存档，查得到之前说了什么
- 多语言：主打中文，英文也能跑（FunASR 对英文也有支持）

---

## 两个关键坑

### 1. 没有许可证文件

GitHub API 返回的许可证字段是 `NOASSERTION`——仓库里没有放标准的开源许可证文件（MIT、Apache、GPL 等）。

这在法律上意味着：**默认所有权利保留**。你可以阅读源代码，但从严格法律角度看，不能自由修改、分发或商用，除非作者单独授权。

项目 README 自述「开源免费」，但这与无许可证的法律事实之间存在矛盾。如果你打算基于它构建产品，建议先联系作者确认。

### 2. 项目已 11 个月未更新

最后一次代码提交：**2025-10-08**——距今约 11 个月。53 个 open issues 悬而未决。

这不一定意味着项目被废弃，但对于一个依赖 FunASR、Electron、React 等快速迭代生态的工具，一年不更新会带来依赖版本积压。

---

## 与 Wispr Flow 的实际差距

| | 蛐蛐 QuQu | Wispr Flow |
|--|---|---|
| 价格 | 免费（自托管） | $12/月 |
| ASR 质量 | FunASR Paraformer | 未公开（商业模型） |
| 隐私 | 全本地 | 云端处理 |
| 安装难度 | Node.js + Python 双环境 | 一键安装 |
| 维护状态 | **11 个月未更新** | 持续更新 |
| 许可证 | **无声明** | 商业闭源 |
| Windows 支持 | 有，但 issue 较多 | 原生支持 |

核心权衡很清晰：用免费和隐私换来更复杂的安装、更差的维护保障和法律不确定性。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 2,295 |
| 最后更新 | 2025-10-08（约 11 个月前） |
| 许可证 | **无（NOASSERTION）** |
| 触发热键 | F2 |
| ASR 模型 | FunASR Paraformer-large |
| 支持平台 | macOS / Windows / Linux |
| 运行时依赖 | Node.js 18+ + Python 3.8+ |

---

## 综合判断

蛐蛐 QuQu 在技术路线上是正确的：FunASR 本地跑效果扎实，LLM 润色层解决了 ASR 原生输出的口语化问题，热键交互体验与 Wispr Flow 对齐。对隐私敏感、不想付月费的中文用户来说是值得尝试的选项。

但两个硬伤需要正视：**无许可证声明**（商业使用有法律风险）和 **11 个月无维护**（依赖积压、issue 无响应）。如果作者重新活跃或补充了许可证，值得重新评估。现状下建议用于个人学习，不建议用于生产。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## QuQu (蛐蛐): Local Chinese Voice Input Method — Deep Teardown

> **Open source for learning only**: All projects discussed are from public repositories.

---

### Project Background

**yan5xu/ququ** (github.com/yan5xu/ququ) — 2,295 stars, 231 forks, created September 20, 2025.

Positions itself as a "next-generation Chinese desktop voice workflow" and a direct open-source alternative to **Wispr Flow** ($12/month commercial software). Same interaction model: hold F2 to record, release to auto-transcribe and paste at cursor.

---

### Two-Stage Pipeline Architecture

**ASR layer**: Alibaba ModelScope's FunASR Paraformer-large, with FSMN-VAD for speech endpoint detection and CT-Transformer for punctuation restoration. Audio is fully local — nothing uploaded.

**LLM polish layer**: Any OpenAI API-compatible endpoint. Has optimized configs for Chinese models (Tongyi Qianwen, Kimi, Zhipu). This layer is optional.

**Stack**: Electron + React 19 + TypeScript + Tailwind CSS + Vite + better-sqlite3.

---

### Two Critical Issues

**1. No license file**

GitHub API returns `NOASSERTION` — no standard open-source license (MIT/Apache/GPL) in the repo. Legally, this defaults to all rights reserved. The README calls it "open source and free," but that contradicts the legal reality. Verify with the author before building on it.

**2. 11 months without updates**

Last commit: 2025-10-08. 53 open issues unaddressed. A tool depending on FunASR, Electron, and React will accumulate dependency drift without maintenance.

---

### QuQu vs. Wispr Flow

| | QuQu | Wispr Flow |
|--|---|---|
| Price | Free (self-hosted) | $12/month |
| Privacy | Fully local | Cloud processing |
| Install | Node.js + Python | One-click |
| Maintenance | **11 months stale** | Actively maintained |
| License | **None declared** | Commercial closed-source |

Core tradeoff: free + privacy vs. complex install + no maintenance guarantee + legal uncertainty.

---

### Verdict

Good technical approach — FunASR Paraformer is solid, the LLM polish layer solves ASR's spoken-word messiness, and the F2 hotkey interaction matches Wispr Flow. Worth trying for privacy-conscious Chinese users who don't want a monthly subscription.

But two hard blockers: **no license** (legal risk for commercial use) and **11 months without maintenance** (dependency drift, unresponded issues). Suitable for personal learning. Not recommended for production.

---

> Open source for learning only. Verify license terms before commercial use.
