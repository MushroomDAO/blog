---
title: "cli-zoo：otter 一条命令拉起 tmux 工位，wren 两行实时显示 token 消耗"
titleEn: "cli-zoo: One Command to Spin Up Your AI Coding Workspace, Two Lines to Track Tokens"
description: "模型大家都在用同一批，差距在工位上。Spoon94 的 cli-zoo 收了两只小动物：otter 用一条命令把 Claude Code / tmux / yazi / nvim / lazygit 拼成整洁的开发会话，wren 在状态栏实时显示 token 用量、缓存命中率、上下文占用。"
descriptionEn: "Everyone's running the same models. The difference is the workstation. Spoon94's cli-zoo ships two tools: otter launches a full tmux dev session for AI coding agents in one command, and wren puts live token counts and cache hit rates right in your statusline."
pubDate: 2026-09-20
category: "Tech-Experiment"
tags: ["shell", "tmux", "developer-tools", "claude-code", "open-source", "workflow"]
lang: zh-CN
heroImage: "../../assets/images/cli-zoo-otter-wren-tmux-ai-coding-workflow-shell-tools-banner.jpg"
---

模型大家都在用同一批，差距在工位上。

GitHub 上有个叫 Spoon94 的用户（头像是只狗），最近维护了一个叫 **cli-zoo** 的仓库，攒了几只用于 AI 编程流的 Shell 小工具，每个工具以动物命名，一个目录一个脚本，symlink 安装到全局。目前收了两只：**otter** 和 **wren**。

仓库地址：github.com/Spoon94/cli-zoo，MIT 协议，Shell 写成。

---

## otter：一条命令拉起整个 AI 开发会话

你用 Claude Code、Opencode 或者 Qoder CLI 写代码，通常要手动打开 tmux，分个窗格给终端，再开文件管理器，再开 git 面板……每次都要重复这套操作。

otter 解决的就是这件事：

```bash
otter -c claude          # 启动或复用 session，默认布局
otter -c opencode        # 换成 Opencode
otter -ks my-session     # 杀掉指定 session
```

布局固定为三格：
- **左**：你选的 AI CLI 工具（`claude` / `qodercli` / `opencode`）
- **右上**：yazi 文件管理器
- **右下**：空白 shell（备用）

检测到 `nvim` 时额外开一个 window 给编辑器，检测到 `lazygit` 时再开一个 window 给 git 面板。软依赖缺失自动降级，不会因为没装 yazi 就崩。

`-c` 的白名单是 `ALLOWED_TOOLS`，当前接受 `claude`、`qodercli`、`opencode` 三个值。想加新的，改这个变量就行。

---

## wren：两行状态栏，实时看 token 和缓存

wren 是个安装器，把一条两行状态栏接进三个宿主：Claude Code（`cc`）、pi 和 Qoder CLI（`qc`）。

安装：

```bash
./cli-zoo-install.sh wren        # 先把 wren 安装到 /usr/local/bin
wren install cc                  # 装进 Claude Code
wren install all                 # 三个宿主一起装
```

装完 statusline 长这样（Claude Code 侧，Dracula 配色）：

```
~/Code/cli-zoo | main ↑0↓0 +4 ✱2 | wC:t1:p1 | cc
↑12K ↓3K | R1.2M CH57.14% CP2 | 8.40%/200K | claude-opus-5 · high · 1h5m
```

两行各显示什么：

**第一行**：当前目录（长路径自动折叠）+ git 分支/状态 + header 在哪个 tmux pane + 宿主徽标（`cc` / `pi` / `qc`）

**第二行**：
- `↑12K ↓3K`：本次会话累计发出/收到的 token
- `R1.2M`：缓存读取量
- `CH57.14%`：缓存命中率（cache hit rate）
- `CP2`：上下文压缩次数（context compression count）
- `8.40%/200K`：当前上下文占比
- `claude-opus-5 · high · 1h5m`：模型 + 思考档位 + 运行时长

Qoder CLI 侧同构，数据源不同：

```
~/Code/cli-zoo | feat/x ↑0↓0 | wW:t1:p2 | qc
↑4.5M ↓65K | R4.2M CH98.21% | 15.00%/1M | Qwen3.8-Max · xhigh · 16m
```

**两级安装设计值得注意**：`cli-zoo-install.sh` 装的是 symlink（跟随仓库，改脚本即时生效）；`wren install` 装到宿主的是**文件副本**（仓库删了、移了，状态栏照常工作）。所以卸载顺序有讲究：先 `wren uninstall` 拆宿主接线，再 `cli-zoo-uninstall.sh wren` 摘本体，别搞反。

pi 里装完后用 `/footer` 命令切换开关。

---

## 工程细节

**安装脚本**：
```bash
git clone https://github.com/Spoon94/cli-zoo.git
cd cli-zoo
./cli-zoo-install.sh otter       # 或 wren
# 默认写 /usr/local/bin，不想动就：
PREFIX=$HOME/bin ./cli-zoo-install.sh otter
```

**目录结构**：每只动物一个目录 `zoo-scripts/<name>/`，入口脚本直接可执行，安装器用 `ln -s` 软链到 `$PREFIX`（wren 因为是多文件工具，软链的是入口脚本 `zoo-scripts/wren/wren`）。

**测试**：`docs/testing.md` 有专门的测试用例说明，覆盖安装/卸载幂等性（目标不存在时直接 exit 0）。

---

## 几点局限

- **星数低（1 star）**：仓库新，2026-09-19 才更新，代码质量需要自己评估后再用于生产工作流。
- **otter 工具白名单写死在脚本里**：加新工具需改源码，没有配置文件抽象。
- **wren 不同步更新**：装到宿主是副本，作者改脚本后你要重跑 `wren install` 才会更新，不会自动拉新版。
- **只测了三个宿主**：cc / pi / qc 以外的 AI CLI 工具（如 Gemini CLI）目前没有官方支持。

---

## 同作者的另一个仓库

顺带看了一下，Spoon94 还有个 **skill-vault**（3 stars，MIT，Python）：给 Claude Code、Codex CLI、Copilot CLI、Gemini CLI、OpenCode 整理了一批社区 Agent Skill，每个 skill 是自包含的 `SKILL.md`，遵循 Agent Skills 规范。两个仓库放在一起，方向一致——把 AI 编程工作流的"工位层"标准化。

> 开源代码仅供学习参考，正式使用前请自行测试评估。

---

**仓库**：github.com/Spoon94/cli-zoo  
**License**：MIT | **语言**：Shell  
**工具**：otter（tmux 工位布局）、wren（AI CLI token 状态栏）

<!--EN-->

Everyone's running the same models. The difference is the workstation.

A GitHub user called Spoon94 (dog avatar) maintains **cli-zoo** — a small collection of shell tools for AI coding workflows, one tool per directory, symlink-installed globally. Each tool is named after an animal. Two so far: **otter** and **wren**.

Repository: github.com/Spoon94/cli-zoo — MIT license, Shell.

---

## otter: One command to spin up a full AI dev session

When you use Claude Code, Opencode, or Qoder CLI, you typically have to manually open tmux, split panes for the terminal, add a file manager, open a git panel... same routine every time.

otter solves this:

```bash
otter -c claude          # start or reuse session with default layout
otter -c opencode        # switch to Opencode instead
otter -ks my-session     # kill a named session
```

Fixed three-pane layout:
- **Left**: your chosen AI CLI tool (`claude` / `qodercli` / `opencode`)
- **Top-right**: yazi file manager
- **Bottom-right**: empty shell (spare)

Detects `nvim` → opens a dedicated window. Detects `lazygit` → opens another. Soft dependencies that aren't installed are gracefully skipped — missing yazi won't crash the launch.

`-c` accepts the `ALLOWED_TOOLS` whitelist: `claude`, `qodercli`, `opencode`. Add more by editing that variable.

---

## wren: Two-line statusline with live token and cache data

wren is an installer that attaches a two-line statusline to three hosts: Claude Code (`cc`), pi, and Qoder CLI (`qc`).

Install:

```bash
./cli-zoo-install.sh wren        # install wren to /usr/local/bin
wren install cc                  # wire it into Claude Code
wren install all                 # wire all three hosts at once
```

After install, the statusline looks like this (Claude Code side, Dracula palette):

```
~/Code/cli-zoo | main ↑0↓0 +4 ✱2 | wC:t1:p1 | cc
↑12K ↓3K | R1.2M CH57.14% CP2 | 8.40%/200K | claude-opus-5 · high · 1h5m
```

**Line 1**: current directory (auto-truncated for long paths) + git branch/status + which tmux pane holds the header + host badge (`cc` / `pi` / `qc`)

**Line 2**:
- `↑12K ↓3K`: cumulative tokens sent/received this session
- `R1.2M`: cache read volume
- `CH57.14%`: cache hit rate
- `CP2`: context compression count
- `8.40%/200K`: context occupancy
- `claude-opus-5 · high · 1h5m`: model + thinking tier + session duration

Qoder CLI side is structurally identical, different data source:

```
~/Code/cli-zoo | feat/x ↑0↓0 | wW:t1:p2 | qc
↑4.5M ↓65K | R4.2M CH98.21% | 15.00%/1M | Qwen3.8-Max · xhigh · 16m
```

**The two-level installation is intentional**: `cli-zoo-install.sh` creates a symlink (tracks the repo — edits take effect instantly); `wren install` copies files into each host (works even if the repo is deleted or moved). Uninstall order matters: run `wren uninstall` first to unwire the hosts, then `cli-zoo-uninstall.sh wren` to remove the binary. In pi, toggle the footer with `/footer`.

---

## Limitations

- **1 star, new repo**: updated 2026-09-19. Evaluate the code yourself before adopting it in a real workflow.
- **otter's tool whitelist is hardcoded**: no config file abstraction; adding new tools means editing the script.
- **wren installs file copies, not live links**: the author's upstream changes don't reach your hosts automatically — you have to re-run `wren install` to update.
- **Only three hosts supported**: cc / pi / qc. No official support yet for Gemini CLI or other AI CLIs.

---

## Same author, related repo

Spoon94 also has **skill-vault** (3 stars, MIT, Python): a curated collection of community Agent Skills for Claude Code, Codex CLI, Copilot CLI, Gemini CLI, and OpenCode — each skill a self-contained `SKILL.md` following the Agent Skills spec. Same direction as cli-zoo: standardizing the "workstation layer" of AI coding workflows.

> Open-source code is for learning and reference. Evaluate before use in production.

---

**Repository**: github.com/Spoon94/cli-zoo  
**License**: MIT | **Language**: Shell  
**Tools**: otter (tmux workspace layout), wren (AI CLI token statusline)
