---
title: "黑奴一号（Heinu1）：用微信远程控制家里的 Claude Code，随时随地 AI 编程"
description: "Heinu1 是一个开源 macOS 机器人，把微信变成你的远程 AI 编程终端。发一条消息，家里的 Claude Code 就开始工作：合并文档、发布博客、git push——出门在外也能让 AI 代劳。TypeScript + SQLite + 微信 iLink 官方 API，零封号风险。"
titleEn: "Heinu1: Control Claude Code at Home via WeChat — AI Coding Anywhere, Anytime"
descriptionEn: "Heinu1 is an open-source macOS bot that turns WeChat into your remote AI coding terminal. Send one message, and Claude Code at home starts working: merge docs, publish blogs, git push — all while you're away. TypeScript + SQLite + WeChat's official iLink API, zero ban risk."
pubDate: 2026-06-12
category: "Tech-Experiment"
tags: ["Heinu1", "黑奴一号", "ClaudeCode", "微信Bot", "远程控制", "AI编程", "iLink", "TypeScript", "开源", "macOS"]
lang: "zh-CN"
heroImage: "../../assets/images/heinu1-wechat-claude-code-remote-bot.png"
---

## 场景：你在外面，活在家里等着

你在咖啡馆，突然想起昨天写了一半的功能。或者需要把一份文档合并发布。或者让 AI 帮你搜索一个问题、整理一份报告。

但你不在电脑旁边。

**黑奴一号（Heinu1）** 解决这个问题：用微信给家里的电脑发一条消息，Claude Code 自动执行，完成后回复给你。

---

## 项目信息

- **GitHub**：[jhfnetboy/Heinu1](https://github.com/jhfnetboy/Heinu1)
- **许可证**：Apache 2.0（开源）
- **技术栈**：TypeScript（81%）+ JavaScript + Shell
- **依赖**：Node.js 18+、Claude Code、微信 v2026.3.20+

---

## 它是怎么工作的

架构很直接，分四层：

```
你的手机微信
    ↓ 发消息
微信 iLink Bot API（官方 HTTP 长轮询）
    ↓ 接收
本地 daemon（Node.js）
    ↓ 解析命令，spawn 进程
Claude Code CLI（带 --resume 保持上下文）
    ↓ 执行任务
结果回传微信
```

**关键设计：spawn-per-message 模型**

每条消息单独 spawn 一个 `claude` 进程，用 `--resume <session-id>` 恢复上下文——不是一个长连接的持久进程，而是"每次对话用上次的记忆重新启动"。好处：崩溃了自动恢复，不影响其他会话。

**零封号风险**：用的是微信官方 iLink Bot API（HTTP 长轮询，35 秒服务器 hold），不是 hook 或逆向协议。

会话历史存在 SQLite，工作区配置存在 `~/.heinu1-bot/`。

---

## 安装：5 分钟搞定

**前提**：macOS + Node.js 18+ + Claude Code 已安装

```bash
git clone https://github.com/jhfnetboy/Heinu1.git
cd Heinu1/bot
bash setup.sh
```

**配置工作区**（可以有多个项目）：

```bash
npm run ws -- add blog ~/Dev/mycelium/blog "博客项目"
npm run ws -- add main ~/Dev/myproject "主项目"
npm run ws -- default blog   # 设置默认工作区
```

**启动**：

```bash
npm start
```

终端会显示二维码，用微信扫码添加 ClawBot 为好友。之后每次开机自动启动（launchd 服务）。

---

## 微信里能做什么

### 发任务

```
你：把 dev-log.md 合并成一篇博客，发布到 /blog，git push
Bot：⚡ 收到，开始执行
[Claude 自动读文件、写内容、执行 git push]
Bot：✅ 完成：文章已保存，已推送到远端
```

### 切换工作区

```
/ws           → 列出所有工作区
/ws blog      → 切换到博客项目（工作目录 + 上下文同步切换）
/ws main      → 切换到主项目
```

### 管理会话

```
/new          → 开启全新对话（清除上下文）
/sessions     → 查看历史会话列表
/resume 2     → 恢复第 2 个会话继续工作
```

---

## 三种权限模式

| 模式 | 行为 | 适合场景 |
|------|------|---------|
| **bypassPermissions**（默认） | 全自动，不询问，直接执行 | 家用/可信环境，最流畅 |
| **acceptEdits** | 文件修改自动批准，Bash 命令需确认 | 想控制执行风险 |
| **default** | 每步操作都询问 | 谨慎模式（远程操作时消息来回会很多） |

家用机推荐 `bypassPermissions`——你已经信任这台电脑，不需要反复确认。

---

## 真实使用场景

**场景 1：出门前没来得及发文章**
```
在地铁上：
"帮我把今天写的草稿整理成正式博客，发布到 blog，git push"
十分钟后收到完成通知
```

**场景 2：在会议室突然需要数据**
```
"搜一下最近关于 TEE 安全的研究，整理成 markdown 发给我"
Claude 搜索 + 整理，把结果回传微信
```

**场景 3：多项目并行管理**
```
早上切换到 blog 工作区，让 AI 整理昨天的记录
下午 /ws main 切换，继续主项目的功能开发
```

**场景 4：出差期间的代码审查**
```
"看一下 PR #42，有没有明显的问题，简单说一下"
Claude 拉取 PR，分析后回复摘要
```

---

## 与直接用手机版 Claude 的区别

| 对比维度 | Heinu1 | 手机版 Claude |
|---------|--------|--------------|
| 能访问本地文件 | ✅ | ❌ |
| 能执行 git 命令 | ✅ | ❌ |
| 能跑测试/构建 | ✅ | ❌ |
| 会话跨消息保持 | ✅（--resume） | 受限 |
| 多工作区切换 | ✅ | ❌ |
| 微信原生交互 | ✅ | ❌（要开另一个 App） |

核心差异：Heinu1 是你**家里的机器**在工作，Claude 能访问你的全部本地环境。手机版 Claude 只能在对话框里聊天，没有本地执行能力。

---

## 适合谁用

**最适合：**
- 重度使用 Claude Code 的开发者，经常需要远程触发任务
- 有家用 Mac 一直开机的人
- 想用微信作为"随身 AI 终端"的人
- 需要管理多个项目、频繁切换上下文的人

**前提条件：**
- 家里/办公室有一台常开的 macOS 机器
- 已经在用 Claude Code
- 有微信账号（用于 iLink Bot）

---

## 资源

| 资源 | 链接 |
|------|------|
| GitHub | [jhfnetboy/Heinu1](https://github.com/jhfnetboy/Heinu1) |
| 许可证 | Apache 2.0 |
| 依赖 | Node.js 18+、Claude Code、微信 v2026.3.20+ |

---

*Heinu1 由 [jhfnetboy](https://github.com/jhfnetboy) 构建，Apache 2.0 开源。*

<!--EN-->

## Heinu1: Remote-Control Claude Code via WeChat

**Heinu1** ([jhfnetboy/Heinu1](https://github.com/jhfnetboy/Heinu1)) is an open-source macOS bot that turns WeChat into a remote terminal for Claude Code. Send a message from anywhere — Claude Code on your home machine executes the task and reports back.

### Architecture

```
WeChat (your phone)
  ↓
WeChat iLink Bot API (official HTTP long-polling, no ban risk)
  ↓
Local Node.js daemon
  ↓
Claude Code CLI (--resume <session-id> for context continuity)
  ↓
Results back to WeChat
```

**Spawn-per-message model**: each message spawns a fresh `claude` process with `--resume` for context. Crash-safe, session-isolated.

### Install (5 min)

```bash
git clone https://github.com/jhfnetboy/Heinu1.git
cd Heinu1/bot && bash setup.sh
npm run ws -- add blog ~/Dev/mycelium/blog "Blog"
npm start   # shows QR code to add ClawBot on WeChat
```

Auto-starts on subsequent boots via launchd.

### Usage

```
"Merge dev-log.md into a blog post, publish, git push"
→ Bot: ⚡ received, executing
→ [Claude reads files, writes, pushes]
→ Bot: ✅ done, pushed to remote

/ws main     → switch workspace
/new         → fresh conversation
/resume 2    → continue session #2
```

### Permission Modes

| Mode | Behavior |
|------|----------|
| `bypassPermissions` (default) | Fully automated, no prompts |
| `acceptEdits` | File changes auto-approved, Bash requires confirm |
| `default` | Every operation prompts |

### Key Differentiator vs Mobile Claude

Heinu1 runs Claude Code with full access to your local files, git, terminal, and build tools. Mobile Claude is a conversation only.

**GitHub**: [jhfnetboy/Heinu1](https://github.com/jhfnetboy/Heinu1) · Apache 2.0
