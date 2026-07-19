---
title: "Ratatui：Codex、grok-build、CodeWhale 都选了它——Rust 终端 UI 的事实标准，21k stars"
titleEn: "Ratatui: Why Codex, grok-build & CodeWhale All Chose It — The De Facto Rust Terminal UI Standard, 21k Stars"
description: "Ratatui 是 Rust 终端 UI 的事实标准。Codex 锁了定制 revision，grok-build 自建 inline+textarea，CodeWhale 跟进上游 0.30——三者实现不同，但渲染层的选择是一致的。sub-millisecond 即时渲染、约束式布局、15+ 内置 Widget、纯 Rust 零 C 依赖，生态已扩展到 WebAssembly / UEFI / 嵌入式设备。"
descriptionEn: "Ratatui is the de facto Rust TUI standard. Codex locked a custom revision, grok-build built inline+textarea from scratch, CodeWhale follows upstream 0.30 — three different implementations, one shared rendering layer. Sub-millisecond immediate-mode rendering, constraint-based layouts, 15+ built-in widgets, pure Rust zero C deps. Ecosystem now spans WebAssembly, UEFI, and embedded."
pubDate: "2026-07-19"
updatedDate: "2026-07-19"
category: "Tech-Experiment"
tags: ["Rust", "TUI", "终端UI", "Codex", "Claude Code", "AI Agent", "开源", "ratatui"]
heroImage: "../../assets/images/ratatui-rust-tui-terminal-ui-guide-banner.jpg"
---

> **GitHub**：[ratatui/ratatui](https://github.com/ratatui/ratatui) · ⭐ 21,779  
> **官网**：[ratatui.rs](https://ratatui.rs/) · **文档**：[docs.rs/ratatui](https://docs.rs/ratatui)  
> **起源**：2023 年 fork 自 [tui-rs](https://crates.io/crates/tui)，由社区接管持续维护

---

## 一个有趣的现象

Codex（OpenAI 的 CLI 编程 Agent）锁了一个定制 revision；grok-build 自建了 inline 和 textarea 两套组件；CodeWhale 选择跟进上游 0.30。

三个独立项目，三种不同的 UI 实现策略——但渲染层的选择是同一个：**Ratatui**。

这不是巧合。当最顶级的 AI 编程工具在 Rust 里需要做终端 UI 时，它们不约而同地落在了同一个库上。这说明 Ratatui 解决了一个真实的、普遍的问题，而且解决得足够好，以至于没有人觉得值得另起炉灶。

---

## 为什么 AI Agent 的终端 UI 很难做

终端 UI 听起来简单——不就是打印字符嘛。但有几个约束让它很麻烦：

**更新粒度**：GUI 有脏标记，只重绘变化的区域。终端没有这套机制——你要么重绘整个屏幕（闪烁），要么自己算出哪些字符变了（复杂）。

**布局**：终端没有 CSS，没有自动换行，没有弹性盒子——一切都是字符坐标和手动计算宽度。

**状态管理**：像 Claude Code / Codex 这样的 AI 工具，UI 状态极其复杂：流式输出、工具调用展开/折叠、并发任务进度、token 计数……这些状态要实时反映在 UI 里。

Ratatui 的答案是：**即时模式渲染（Immediate Mode）**+ **差分缓冲区（Buffer Diff）**。

---

## 核心设计：即时模式 + 差分输出

与大多数 GUI 框架不同，Ratatui 采用的是**即时模式渲染**：每一帧都从头重绘，没有持久化的 Widget 对象，没有状态同步的负担。

```rust
loop {
    terminal.draw(|frame| {
        // 每帧完整重绘，状态变了直接体现
        if state.is_running {
            frame.render_widget(ProgressWidget::new(&state), layout);
        } else {
            frame.render_widget(ResultWidget::new(&state), layout);
        }
    })?;
}
```

但「每帧重绘」不等于「每帧全量刷新终端」。Ratatui 在内部维护两个 Buffer（当前帧和上一帧），每次 `draw()` 结束后做 diff，**只把变化的字符写入终端**。这就是 sub-millisecond 渲染的来源：写到终端的字节数极少，大部分情况下接近零。

这个设计对 AI Agent 工具特别合适：
- 流式输出只有新增的字符变化 → 只写新字符
- 工具调用展开 → 只有那一块区域变化
- 状态更新 → 精确定位变化位置刷新

---

## 15+ 内置 Widget

Ratatui 内置的组件覆盖了 CLI 工具的绝大多数场景：

| Widget | 用途 |
|---|---|
| `Block` | 带边框/标题的容器，最基础的布局单元 |
| `Paragraph` | 多行文本，支持 wrap、scroll、样式标注 |
| `List` | 可选中列表，带光标状态 |
| `Table` | 多列数据表格，支持行选中 |
| `Chart` | 折线图/散点图，多数据集 |
| `BarChart` | 柱状图，支持分组 |
| `Sparkline` | 单行迷你折线图（适合展示实时 token 速率）|
| `Gauge` / `LineGauge` | 进度条，块字符/线条两种样式 |
| `Scrollbar` | 独立滚动条组件 |
| `Tabs` | 标签页导航 |
| `Canvas` | 用绘图字符画任意图形 |
| `Calendar` | 月历 |
| `Clear` | 清除区域（用于弹窗覆盖） |

这些组件覆盖了从简单的帮助菜单到复杂的多面板 Agent 控制台的所有需求。

---

## 约束式布局：终端的 Flexbox

Ratatui 的布局系统用「约束」描述区域划分，而不是像素：

```rust
let chunks = Layout::default()
    .direction(Direction::Vertical)
    .constraints([
        Constraint::Length(3),      // header: 固定 3 行
        Constraint::Min(10),         // main: 至少 10 行，剩余空间全给它
        Constraint::Percentage(20),  // footer: 20% 高度
    ])
    .split(frame.area());
```

约束类型：
- `Length(n)` — 固定 n 个字符
- `Percentage(p)` — 父区域的 p%
- `Min(n)` / `Max(n)` — 最小/最大约束，剩余空间自动分配
- `Ratio(num, den)` — 精确比例
- `Fill(n)` — 按权重分配剩余空间（类似 flex: n）

终端窗口随时可以 resize，约束式布局让 UI 自动适配——这对 Codex/grok-build 这样在各种终端环境下运行的工具非常重要。

---

## 为什么 Codex / grok-build / CodeWhale 各自的选择不同，却都用 Ratatui

这三者在 UI 策略上走了不同的路：

**Codex（OpenAI）** 锁定了一个定制 revision。原因很可能是稳定性：Ratatui API 变动较多（每个 minor 版本都有 breaking changes），Codex 选择固定一个已验证的版本，在上面做定制改动，不随上游漂移。

**grok-build（xAI）** 自建了 inline 和 textarea 两套组件。这说明标准的 `Paragraph` 和 `List` 对他们的 AI 编程场景来说不够用——流式输出的 inline 展示、代码编辑的 textarea 交互，需要比内置 Widget 更精细的控制。他们用 Ratatui 的 `Widget` trait 和 `Buffer` API 直接构建了自己的组件，但底层渲染、布局、终端交互仍然交给 Ratatui。

**CodeWhale** 跟进上游 0.30，拥抱 Ratatui 的最新 API（包括 `WidgetRef`/`StatefulWidgetRef` trait 带来的引用渲染能力）。这是最「正统」的用法，也意味着他们能直接用到 Ratatui 生态里的第三方 Widget。

共同点：**没有人用 ncurses，没有人用原始 ANSI 转义，没有人重新造渲染引擎**。Ratatui 处理了所有底层脏活——终端能力检测、颜色支持判断、字节写入、resize 信号处理、Buffer diff。

---

## 生态：从终端到 WebAssembly、UEFI、嵌入式

Ratatui 有一个活跃的第三方生态，已经远超「终端库」的定位：

**多后端渲染**：
- `ratzilla` — Ratatui + WebAssembly，在浏览器里渲染 TUI
- `egui-ratatui` — 作为 egui Widget 运行，可部署到桌面/Web
- `ratatui-uefi` — 在 UEFI 固件环境里渲染
- `mousefood` / `dumo` — 嵌入式图形设备后端（支持汉字！）

**多语言绑定**：
- `pyratatui` / `ratatui-py` — Python（Maturin + PyO3）
- `ratatui-ts` — TypeScript
- `ratatui-go` — Go
- `Ratatui.cs` — C#
- `ratatui_ruby` — Ruby

**实用 Widget 扩展**：
- `ratatui-textarea` — 功能完整的多行编辑器 Widget
- `ratatui-image` — 图片渲染（sixels + unicode 半块字符）
- `tachyonfx` — 类 shader 的 UI 动效系统
- `ratatui-markdown` — Markdown 渲染 + Mermaid 图表 + 语法高亮

**AI Agent 工具**（这个分类本身就说明了问题）：
- `bosun` — tmux 原生的 AI 编程 Agent 会话管理器（支持 Claude Code、Codex）
- `claudectl` — 多 Claude Code 会话 mission control，带实时成本追踪
- `crmux` — tmux 里监控多个 Claude Code 会话的 TUI viewer
- `agx` — AI Agent 执行轨迹的步进调试器

这些工具的出现说明：Ratatui 已经是 AI Agent 终端工具生态里默认的 UI 层了。

---

## 快速上手

```toml
# Cargo.toml
[dependencies]
ratatui = "0.29"
crossterm = "0.28"
```

```rust
use color_eyre::Result;
use crossterm::event::{self, Event};
use ratatui::{DefaultTerminal, Frame, widgets::Paragraph};

fn main() -> Result<()> {
    color_eyre::install()?;
    let terminal = ratatui::init();
    run(terminal)?;
    ratatui::restore();
    Ok(())
}

fn run(mut terminal: DefaultTerminal) -> Result<()> {
    loop {
        terminal.draw(render)?;
        if matches!(event::read()?, Event::Key(_)) {
            break Ok(());
        }
    }
}

fn render(frame: &mut Frame) {
    frame.render_widget(
        Paragraph::new("Hello from Ratatui!"),
        frame.area()
    );
}
```

用模板起步更快：

```bash
cargo install --locked cargo-generate
cargo generate ratatui/templates
```

---

## 几个容易踩的坑

**API 不稳定**：Ratatui 的每个 minor 版本几乎都有 breaking changes（这也是 Codex 选择锁 revision 的原因）。升级前务必看 [BREAKING-CHANGES.md](https://github.com/ratatui/ratatui/blob/main/BREAKING-CHANGES.md)。

**事件循环要自己管**：Ratatui 只管渲染。键盘/鼠标输入要用 `crossterm`（或 `termion`/`termwiz`）自己处理，异步场景要配 `tokio`。

**no\_std 支持**：Ratatui 支持 `no_std`（嵌入式目标），但需要自定义后端实现；并非所有 Widget 在所有后端上都可用。

---

## 一句话总结

当 Codex、grok-build、CodeWhale 在 Rust 里需要做终端 UI 时，都选了 Ratatui——尽管他们在上层实现了完全不同的 Widget 策略。原因很简单：即时模式渲染 + Buffer diff 把底层的脏活全处理了，纯 Rust 零 C 依赖让它可以运行在终端、浏览器、固件、嵌入式设备上。21k stars，从 2023 年接手 tui-rs 至今，Ratatui 已经是 Rust TUI 生态的事实标准。

© 2026 Author: Mycelium Protocol

<!--EN-->

## Ratatui: The De Facto Rust TUI Standard for AI Agent Terminals

**GitHub**: [ratatui/ratatui](https://github.com/ratatui/ratatui) · ⭐ 21,779  
**Website**: [ratatui.rs](https://ratatui.rs/) · **Docs**: [docs.rs/ratatui](https://docs.rs/ratatui)

### The Pattern

Codex (OpenAI) locked a custom revision. grok-build (xAI) built inline and textarea widgets from scratch. CodeWhale tracks upstream 0.30.

Three AI coding tools. Three different UI implementation strategies. One shared rendering layer: **Ratatui**.

This convergence is the signal: Ratatui solves the terminal rendering problem well enough that nobody builds their own.

### Core Design: Immediate Mode + Buffer Diff

Ratatui uses **immediate mode rendering** — every frame redraws from scratch. No persistent widget objects, no state sync overhead.

But "redraw every frame" ≠ "flush every character to the terminal." Ratatui maintains two internal buffers (current frame vs. previous frame) and **diffs them on every draw call**, only writing changed characters to stdout. That's the source of sub-millisecond render times.

For AI agent tools specifically: streaming output adds only new characters → only new characters get written. Tool call expansion → only that region updates. Perfect fit.

### 15+ Built-in Widgets

`Block`, `Paragraph`, `List`, `Table`, `Chart`, `BarChart`, `Sparkline`, `Gauge`, `LineGauge`, `Scrollbar`, `Tabs`, `Canvas`, `Calendar`, `Clear` — everything from simple help menus to complex multi-panel agent dashboards.

### Constraint-Based Layout

```rust
let chunks = Layout::default()
    .direction(Direction::Vertical)
    .constraints([
        Constraint::Length(3),       // header: fixed 3 rows
        Constraint::Min(10),          // main: at least 10 rows, fills remaining
        Constraint::Percentage(20),   // footer: 20% height
    ])
    .split(frame.area());
```

`Length`, `Percentage`, `Min`, `Max`, `Ratio`, `Fill` — Flexbox for the terminal. Auto-adapts to resize events.

### Why Each Project Diverged

- **Codex**: locked a custom revision for API stability — Ratatui has breaking changes most minor versions.
- **grok-build**: built inline + textarea widgets from scratch using Ratatui's `Widget` trait and `Buffer` API directly. Standard widgets weren't granular enough for streaming code output.
- **CodeWhale**: follows upstream 0.30, uses new `WidgetRef`/`StatefulWidgetRef` traits for reference-based rendering. Gains full third-party widget ecosystem access.

All three: Ratatui handles terminal capability detection, color support, byte writes, resize signals, buffer diffing. None of them reinvent the rendering engine.

### Ecosystem Expansion

**Multi-backend rendering**: `ratzilla` (WebAssembly), `egui-ratatui` (desktop/web), `ratatui-uefi` (firmware), embedded graphics backends.

**Multi-language bindings**: Python (PyO3), TypeScript, Go, C#, Ruby.

**AI Agent tooling** (the category's existence is itself the signal): `bosun` (tmux AI agent session manager), `claudectl` (multi-Claude-Code dashboard), `crmux` (Claude Code tmux viewer), `agx` (AI agent execution debugger).

### Quick Start

```bash
cargo install --locked cargo-generate
cargo generate ratatui/templates
```

### Gotcha: API Stability

Breaking changes in nearly every minor version. Always read [BREAKING-CHANGES.md](https://github.com/ratatui/ratatui/blob/main/BREAKING-CHANGES.md) before upgrading. This is exactly why Codex pinned a specific revision.

### Summary

When the most prominent Rust-based AI coding tools needed a terminal UI layer, they all chose Ratatui — despite diverging in every other implementation decision. Immediate mode + buffer diff handles the hard parts. Pure Rust, zero C dependencies, runs everywhere: terminal, WebAssembly, UEFI, embedded. 21k stars, forked from tui-rs in 2023, now the unambiguous standard for Rust TUI development.

© 2026 Author: Mycelium Protocol
