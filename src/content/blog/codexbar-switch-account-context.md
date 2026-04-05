---
title: "Codexbar 发布：不再为切账号丢失上下文而烦恼"
titleEn: "codexbar-switch-account-context"
description: "macOS 菜单栏工具解决多账号切换痛点：保留统一 ~/.codex 历史池，切换 provider 不丢 session，本地统计 token 用量。"
descriptionEn: "macOS menu bar tool solves multi-account switching: keep unified ~/.codex history, switch providers without losing context."
pubDate: "2026-04-04"
category: "Tech-News"
tags: ["codex", "openai", "macOS", "developer-tools", "mult-account"]
heroImage: "../../assets/blog-placeholder-3.jpg"
---

## 多账号切换的痛点

如果你经常在 OpenAI 官方账号、第三方中转站、不同兼容 provider 之间切换，一定遇到过这个问题：

**配置切过去了，上下文像是断了。**

历史 session 明明还在磁盘里，却因为切账号变得不连贯。反复手改配置文件很烦，恢复现场更麻烦。

## Codexbar 的核心思路

Codexbar 是一个 macOS 菜单栏工具，它解决的不是"再建一套 Codex"，而是一个更具体的问题：

> **切账号、切 provider 之后，共用同一个 ~/.codex 历史池。**

它的做法很简单：

- ❌ 不给每个账号单独建一套 CODEX_HOME
- ❌ 不拆你的 ~/.codex 会话池  
- ✅ 只把当前选中的 provider/account 同步到 config.toml 和 auth.json
- ✅ 切换只影响后续新会话，已有历史不会被"切没了"

## 为什么这很重要

很多"多账号切换"方案会给每个账号单独建一套 CODEX_HOME。这样做隔离很强，但代价明显：

- 历史被分散到多份目录
- 切换后"上下文没了"的感觉很糟
- 需要在不同环境之间来回找 session

Codexbar 选的是另一条路：**保留统一的历史池。**

~/.codex/sessions 和 ~/.codex/archived_sessions 这一整套共享历史池保持不变。当前激活的配置会同步到标准位置，切换只影响之后的新请求。

## 现在支持的功能

- 多 OpenAI OAuth 账号管理
- 多 OpenAI 兼容 provider 管理
- 同一 provider 下挂多组 API key
- 菜单栏快速切换
- **本地 usage / 成本统计**

成本统计来自对 ~/.codex/sessions 和 archived_sessions 的扫描，直接在菜单栏看到 token 用量和估算成本，不需要手动翻 session 文件。

## 适合谁用

如果你符合以下情况，Codexbar 会很有用：

- 同时使用 OpenAI 官方和第三方兼容 provider
- 同一 provider 下维护多组 API key
- 不想每次切换都手改 config.toml
- 希望保留统一的 ~/.codex 历史和 resume 体验

## 获取方式

GitHub 开源：https://github.com/lizhelang/codexbar

菜单栏工具，macOS 专用，下载即用。

---

📄 **原文链接**: https://github.com/lizhelang/codexbar
