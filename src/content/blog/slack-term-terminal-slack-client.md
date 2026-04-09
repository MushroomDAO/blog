---
title: 'Slack-Term：程序员专属的终端版 Slack 客户端'
titleEn: 'slack-term-terminal-slack-client'
description: 'slack-term 是一个专为程序员和终端爱好者设计的开源工具，允许直接在终端中使用 Slack，轻量快速，支持 Vim 快捷键操作。'
descriptionEn: 'slack-term is an open-source tool designed for programmers and terminal enthusiasts, allowing you to use Slack directly in the terminal with lightweight performance and Vim-like shortcuts.'
pubDate: '2026-04-08'
category: 'Tech-News'
tags: ['slack', 'terminal', 'cli', 'developer-tools', 'tui']
heroImage: '../../assets/images/cover-slack-term.jpg'
---

![slack-term 界面](../../assets/images/content-slack-term.jpg)

**slack-term** 是一个专为程序员和终端爱好者设计的开源工具，它允许你直接在终端（Terminal）中使用 Slack。简单来说，如果你不想在工作时频繁切换到沉重且占内存的 Slack 桌面客户端，或者你单纯追求极客范儿的"纯文本"办公体验，这个工具就是为你准备的。

## 主要特点

### 轻量化
基于 Go 语言编写，运行速度极快，占用资源极小。

### 快捷键驱动
支持类似 Vim 的快捷键操作，无需鼠标即可高效切换频道、回复消息。

### 多工作区支持
可以在不同的 Slack 团队/工作区之间快速切换。

### 高度可定制
你可以通过配置文件自定义主题颜色和布局。

## 核心功能速览

| 功能 | 说明 |
|------|------|
| 实时聊天 | 支持接收和发送消息，实时同步。 |
| 频道浏览 | 侧边栏列出所有公共频道、私有频道和 DMs（私聊）。 |
| 通知提醒 | 当有人 @ 你或发送私信时，终端会有视觉提示。 |
| 历史查询 | 向上滚动即可查看之前的对话记录。 |

## GitHub 地址

你可以在 GitHub 上找到该项目的源代码、安装指南和详细配置文档：

🔗 **https://github.com/erroneousboat/slack-term**

## 如何快速开始？

### 1. 安装
如果你配置了 Go 环境，可以直接使用 `go install`；或者在 Release 页面下载对应系统的二进制文件。

```bash
go install github.com/erroneousboat/slack-term@latest
```

### 2. 获取 Token
你需要创建一个 Slack App 并获取 Legacy Token（或者按项目文档说明配置 OAuth）。

### 3. 配置文件
在家目录下创建 `.slack-term` 配置文件，填入你的 Token。

```json
{
  "slack_token": "xoxp-your-token-here",
  "theme": {
    "background": "black",
    "border": "white"
  }
}
```

### 4. 启动
直接在终端输入 `slack-term` 即可进入聊天界面。

## 小提醒

由于 Slack 官方 API 的策略调整，某些高级功能（如线索回复 Thread）在终端工具中可能不如官方客户端那样直观。不过对于日常的摸鱼...啊不，技术交流，它绝对绰绰有余！

你是打算用它来减少内存占用，还是想在老板经过时看起来像是在埋头写代码？

---

📄 **Original**: https://github.com/jpbruinsslot/slack-term
