---
title: "Codexbar: Stop Losing Context When Switching Accounts"
titleEn: "codexbar-macOS-menu-bar-tool"
description: "macOS menu bar tool solves multi-account switching pain: keep unified ~/.codex history pool, switch provider without losing sessions, local token usage stats."
descriptionEn: "Codexbar is a macOS menu bar tool that preserves your ~/.codex session history when switching between OpenAI accounts and providers."
pubDate: "2026-04-04"
category: "Tech-News"
tags: ["codex", "openai", "macOS", "developer-tools", "cli"]
heroImage: "../../assets/blog-placeholder-3.jpg"
---

## The Multi-Account Switching Pain

If you frequently switch between OpenAI official accounts, third-party proxies, and different compatible providers, you've definitely encountered this:

**Config switched, but context feels broken.**

Historical sessions are still on disk, but become disjointed after switching accounts. Manually editing config files is annoying, and restoring context is even more painful.

## Codexbar's Core Idea

Codexbar is a macOS menu bar tool. It doesn't try to "rebuild another Codex"—it solves a more specific problem:

> **After switching accounts/providers, share the same ~/.codex history pool.**

Its approach is simple:

- ❌ No separate CODEX_HOME for each account
- ❌ Don't split your ~/.codex session pool
- ✅ Only sync current provider/account to config.toml and auth.json
- ✅ Switching only affects new sessions, existing history stays intact

## Why This Matters

Many "multi-account switching" solutions create separate CODEX_HOME for each account. Strong isolation, but obvious costs:

- History scattered across multiple directories
- That "context is gone" feeling after switching
- Constantly searching for sessions across environments

Codexbar takes another path: **keep a unified history pool.**

~/.codex/sessions and ~/.codex/archived_sessions remain shared. Current config syncs to standard locations, switching only affects future requests.

## Current Features

- Multiple OpenAI OAuth account management
- Multiple OpenAI-compatible provider management
- Multiple API keys per provider
- Quick switching from menu bar
- **Local usage / cost statistics**

Cost stats come from scanning ~/.codex/sessions and archived_sessions. See token usage and estimated costs directly in the menu bar—no manual session file digging.

## Who It's For

Codexbar is useful if you:

- Use both OpenAI official and third-party compatible providers
- Maintain multiple API keys per provider
- Don't want to manually edit config.toml every time
- Want unified ~/.codex history and resume experience

## Get It

Open source on GitHub: https://github.com/lizhelang/codexbar

Menu bar tool, macOS only, download and use.

---

📄 **Original**: https://github.com/lizhelang/codexbar
