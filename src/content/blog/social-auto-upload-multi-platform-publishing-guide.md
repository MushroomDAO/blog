---
title: "把内容一次发到全平台：social-auto-upload 个人自动发布入门实测指南"
titleEn: "Publish Once, Post Everywhere: A Hands-On Beginner's Guide to social-auto-upload"
description: "social-auto-upload（12.7k★，Apache 思路开源）用本地浏览器自动化，把图文/视频一键发到抖音、小红书、B站、视频号、快手、YouTube，支持定时、无头运行、cookie 登录，无需逆向、无需常驻 Docker。本文是亲手安装实测后的入门指南：怎么装、怎么登录、怎么发，以及为什么它适合个人而非刷屏。"
descriptionEn: "social-auto-upload (12.7k★) uses local browser automation to publish image-text and video posts to Douyin, Xiaohongshu, Bilibili, WeChat Channels, Kuaishou and YouTube — with scheduling, headless mode, and cookie login, no reverse-engineering and no always-on Docker. A hands-on beginner's guide after installing and testing it myself: install, log in, publish, and why it fits individuals rather than spam."
pubDate: "2026-06-21"
updatedDate: "2026-06-21"
category: "Tech-News"
tags: ["自媒体", "自动发布", "social-auto-upload", "小红书", "多平台分发", "浏览器自动化", "开源工具"]
heroImage: "../../assets/images/social-auto-upload-multi-platform-publishing-guide-banner.jpg"
---

> **BLUF**：**social-auto-upload**（GitHub 12.7k★）是一个把内容**一次写、自动发到多个平台**的开源工具——抖音、小红书、B站、视频号、快手、YouTube 都能发，支持图文、视频、定时发布。它的关键选择是**本地浏览器自动化**（用 patchright 做反检测）+ **cookie/扫码登录**，**不逆向 API、不需要常驻 Docker**，一条命令单次执行。这篇是我**亲手用 uv 装好、在 Mac 上实测跑通**之后写的入门指南：怎么装、怎么登录、怎么发图文/视频，以及一个重要立场——它适合**个人把自己的内容发布自动化**，不是用来刷屏发广告。

---

## 一、它解决什么问题？

如果你既写公众号、又发小红书、还想同步到 B站/视频号，你就懂那种痛：**同一份内容，手动在五六个 App 里各发一遍**，改尺寸、传图、填标题标签、点发布……一条内容发完半小时没了。

social-auto-upload 把这件事自动化：**你把内容和图片准备好，一条命令，它替你在目标平台上"像人一样"操作完成发布。** 注意定位——它帮你省的是**重复的体力活**，不是让你变成发广告的机器人。用它发自己的原创内容、做个人自动化，合理且不滥用；用它多账号批量刷广告，那是另一回事，也容易被平台封。本文只讲前者。

---

## 二、它能做什么？（实测确认）

我装好后用 `sau --help` 看到的真实能力：

**支持平台**：`抖音`、`快手`、`小红书`、`B站`、`视频号（腾讯）`、`YouTube`（README 还提到百家号、TikTok）。

**每个平台的操作**（以小红书为例）：
- `login` — 扫码登录
- `check` — 检查 cookie 是否有效
- `upload-video` — 发视频
- `upload-note` — **发图文笔记**

**核心特性**：
- **图文 + 视频**都支持；
- **定时发布**（`--schedule`）；
- **无头模式**（`--headless`，后台静默跑）；
- **多账号**（`--account` 各自隔离 cookie）；
- 还自带 **Web 界面**（`sau_frontend`/`sau_backend`）和 **Claude Code skills**（`skills/` 目录里有 `xiaohongshu-upload` 等）。

---

## 三、为什么是"浏览器自动化"，而不是 API？

这点值得普通人理解，因为它决定了**会不会被封、好不好维护**：

- **逆向 API**（破解签名直接调接口）：快，但平台一改签名就崩，且封号风险高；
- **浏览器自动化**（本工具）：用真实浏览器**模拟人的点击上传**，平台几乎分不出和真人的区别，风险低、不依赖逆向。本工具还从 Playwright 迁移到 **patchright** 专门做反检测，进一步降低被识别概率。

代价只有一个：**cookie 会过期**，过段时间要重新扫码登录一次。对个人用户，这是完全可接受的小麻烦，换来的是稳定和安全。

---

## 四、入门 5 步（我实测跑通的命令）

> 环境要求：macOS/Linux/Windows，Python 3.10–3.12。推荐用 `uv`（自动帮你装对的 Python 版本）。

**第 1 步：拉代码 + 装依赖**
```bash
git clone https://github.com/dreammis/social-auto-upload
cd social-auto-upload
uv sync          # 没有 uv 就用 pip install -r requirements.txt
```

**第 2 步：生成配置文件**（这一步漏了会报 `No module named 'conf'`，我踩过）
```bash
cp conf.example.py conf.py
```

**第 3 步：扫码登录**（会弹出浏览器，用手机 App 扫码）
```bash
uv run sau xiaohongshu login --account me
```

**第 4 步：发一条图文笔记**
```bash
uv run sau xiaohongshu upload-note --account me \
  --images cover.png page2.png \
  --title "我的标题" \
  --note "正文内容" \
  --tags AI,效率工具
```

**第 5 步（可选）：定时发布 / 后台静默**
```bash
uv run sau xiaohongshu upload-note --account me \
  --images cover.png --title "标题" --note "正文" \
  --schedule "2026-06-22 20:00" --headless
```

发视频同理：`uv run sau xiaohongshu upload-video --account me --file v.mp4 --title "标题"`；换平台就把 `xiaohongshu` 换成 `douyin`/`bilibili`/`tencent`/`youtube`。

> ⚠️ **踩坑提醒**：直接敲 `sau` 会报 `command not found`——因为它装在虚拟环境里。**正确姿势是 `uv run sau ...`**（或先 `source .venv/bin/activate` 再用 `sau`，或建一个全局软链）。

---

## 五、中肯建议：适合谁、不适合谁

**适合**：
- 一个人运营多平台、想把**自己原创内容**的发布自动化的创作者；
- 需要**定时发布**（比如排好一周的内容）；
- 想把发布接进自己的脚本/AI 流水线（它有 CLI + Web UI + CC skill，接入方便）。

**不适合 / 别这么用**：
- 多账号批量刷广告、养号矩阵——这既违背平台规则，也容易封号，本工具虽支持多账号但不建议拿来滥用；
- 想"零维护全自动"——cookie 会过期，隔段时间得扫码续一次，需要你偶尔照看。

**一句话**：把它当成"**替你点鼠标的助手**"，而不是"**不用管的发帖机器人**"，定位就对了。

---

## 六、它和我们关心的"内容自动化"是什么关系？

对做数字公共物品、小团队、个人创作者来说，内容发布的**重复劳动**是真实的时间黑洞。这类本地优先、开源、个人可控的自动化工具，正是把时间还给创作者本身——你专注表达，脏活交给工具。这与"让普通人掌握自己的表达与分发能力"的理念一致：**自动化的是流程，不是真诚。**

---

## FAQ

**Q：会被平台封号吗？**
A：用浏览器自动化 + 反检测、单账号、正常频率发自己的原创内容，风险很低。真正高风险的是多账号批量刷广告——那是滥用，不在本文建议范围。

**Q：一定要会写代码吗？**
A：基本只要会复制粘贴命令行。它还提供 Web 界面，更怕命令行的人可以用界面操作。

**Q：`sau` 命令找不到怎么办？**
A：它在虚拟环境里，用 `uv run sau ...`，或激活 `.venv` 后再用，或为它建个全局软链。

**Q：cookie 多久过期？**
A：因平台而异，通常几天到两周。过期后 `sau <平台> login` 重新扫码即可，`check` 命令可先检测是否有效。

---

> 📌 项目地址（请直接复制访问）：
> GitHub —— https://github.com/dreammis/social-auto-upload

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: **social-auto-upload** (GitHub 12.7k★) lets you **write once and auto-post to many platforms** — Douyin, Xiaohongshu, Bilibili, WeChat Channels, Kuaishou, YouTube — for both image-text notes and videos, with scheduling. Its key design: **local browser automation** (with patchright for anti-detection) + **cookie/QR login**, **no reverse-engineered APIs and no always-on Docker**, run as a single CLI command. This is a beginner's guide written after I **installed and tested it myself on a Mac with uv**: how to install, log in, and publish — plus a clear stance: it's for **automating your own content publishing**, not for spamming ads.

---

## 1. The Problem It Solves

If you run a WeChat blog, post to Xiaohongshu, and also want to mirror to Bilibili/Channels, you know the pain: **manually re-posting the same content across five or six apps** — resizing, uploading images, filling in titles and tags, hitting publish. Half an hour gone per post.

social-auto-upload automates this: **prepare your content and images once, run one command, and it performs the publish "like a human" on each target platform.** The point: it saves you the **repetitive manual labor**, it does not turn you into an ad bot. Using it to publish your own original content as personal automation is reasonable and not abuse; using it for multi-account ad spam is a different thing and gets you banned. This guide is only about the former.

## 2. What It Can Do (verified)

From `sau --help` after install:

**Platforms**: Douyin, Kuaishou, Xiaohongshu, Bilibili, WeChat Channels (Tencent), YouTube (README also mentions Baijiahao, TikTok).

**Per-platform actions** (Xiaohongshu example): `login` (QR), `check` (cookie validity), `upload-video`, **`upload-note`** (image-text).

**Features**: image-text + video; scheduled publishing (`--schedule`); headless mode (`--headless`); multi-account (`--account`, isolated cookies); plus a built-in **Web UI** (`sau_frontend`/`sau_backend`) and **Claude Code skills** (`skills/`).

## 3. Why Browser Automation, Not an API?

This decides **ban risk and maintainability**:

- **Reverse-engineered API**: fast, but breaks whenever the platform changes its signing, with higher ban risk.
- **Browser automation** (this tool): drives a real browser to **mimic human clicks and uploads**, nearly indistinguishable from a person — low risk, no reverse-engineering. It moved from Playwright to **patchright** specifically for anti-detection.

The only cost: **cookies expire**, so you re-scan a QR every so often. For an individual, that's an acceptable trade for stability and safety.

## 4. Five-Step Quick Start (commands I actually ran)

> Requirements: macOS/Linux/Windows, Python 3.10–3.12. Use `uv` (it fetches the right Python).

```bash
# 1. Clone + install
git clone https://github.com/dreammis/social-auto-upload
cd social-auto-upload
uv sync                      # or: pip install -r requirements.txt

# 2. Create config (skipping this gives "No module named 'conf'" — I hit it)
cp conf.example.py conf.py

# 3. Log in (opens a browser; scan the QR with the app)
uv run sau xiaohongshu login --account me

# 4. Publish an image-text note
uv run sau xiaohongshu upload-note --account me \
  --images cover.png page2.png --title "My title" --note "Body" --tags AI,tools

# 5. (optional) schedule + headless
uv run sau xiaohongshu upload-note --account me \
  --images cover.png --title "T" --note "B" \
  --schedule "2026-06-22 20:00" --headless
```

Video is analogous (`upload-video --file v.mp4`); switch platforms by replacing `xiaohongshu` with `douyin`/`bilibili`/`tencent`/`youtube`.

> ⚠️ **Gotcha**: typing `sau` directly gives `command not found` — it lives in the venv. Use **`uv run sau ...`** (or activate `.venv`, or make a global symlink).

## 5. Who It's For (and Not)

**Good fit**: solo creators automating publishing of **their own original content**; people who want **scheduled** posts; anyone wiring publishing into a script/AI pipeline (CLI + Web UI + CC skill make integration easy).

**Not for / don't do this**: multi-account ad spam / account-farming matrices — against platform rules and ban-prone; the tool supports multi-account but don't abuse it. Also not "zero-maintenance fully-auto" — cookies expire and need occasional re-login.

**In one line**: treat it as **"an assistant that clicks the mouse for you,"** not **"a fire-and-forget posting bot."**

## 6. Why This Matters for Content Automation

For digital-public-goods folks, small teams, and individual creators, the **repetitive labor** of publishing is a real time sink. Local-first, open-source, individually-controlled automation like this gives time back to the creator — you focus on expression, the tool does the grunt work. That aligns with putting expression and distribution power back in ordinary people's hands: **automate the process, not the sincerity.**

## FAQ

**Q: Will I get banned?** Single account, normal cadence, your own original content via anti-detection browser automation — low risk. The real risk is multi-account ad spam, which is abuse and out of scope here.

**Q: Do I need to code?** Basically just copy-paste commands; a Web UI exists for the CLI-averse.

**Q: `sau` not found?** It's in the venv — use `uv run sau ...`, activate `.venv`, or symlink it globally.

**Q: How long do cookies last?** Platform-dependent, usually days to two weeks. Re-scan with `sau <platform> login`; use `check` to test validity first.

---

> 📌 Project (copy to visit):
> GitHub — https://github.com/dreammis/social-auto-upload

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
