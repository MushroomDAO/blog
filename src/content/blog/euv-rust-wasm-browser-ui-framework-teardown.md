---
title: "euv：一个 Rust WASM UI 框架，但它不是你想的那种「革命」"
titleEn: "euv: A Rust WASM UI Framework — What It Really Does Under the Hood"
description: "euv-dev/euv，MIT，15 stars，Rust 100%，v0.28.9，1,285 次提交，2 位贡献者。一个在 wasm-bindgen/web-sys 之上封装的 Rust 浏览器 UI 框架，提供 html! 声明式宏、虚拟 DOM diffing、Signal/SignalCell 响应式状态系统、class!/vars! CSS 宏，以及 Canvas/WebGL/Audio/MediaStream 集成。本文还原它的实际技术机制：底层不是独立编译链，不与 Emscripten 有关，也不是「第一个」Rust 前端框架（Yew 已经跑了 7 年）。「cargo build --release 就这一行」的说法需要加上「以及配置好 wasm-pack 的环境」这个前提。642+ 测试通过，DOM 帮助函数名随机化是一个有意思的安全加固设计。"
descriptionEn: "euv-dev/euv, MIT, 15 stars, Rust 100%, v0.28.9, 1,285 commits, 2 contributors. A Rust browser UI framework layered on top of wasm-bindgen/web-sys, providing the html! declarative macro, virtual DOM diffing, Signal/SignalCell reactive state, class!/vars! CSS macros, and Canvas/WebGL/Audio/MediaStream integration. This teardown goes under the hood: it's not an independent compilation toolchain, has nothing to do with Emscripten, and is not the 'first' Rust frontend framework — Yew has been around for 7 years. The 'just cargo build --release' claim requires a properly configured wasm-pack environment. 642+ tests passing; randomized DOM helper function names are an interesting security hardening detail."
pubDate: 2026-10-05
heroImage: "../../assets/images/euv-rust-wasm-browser-ui-framework-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["Rust", "WASM", "前端框架", "wasm-bindgen", "浏览器", "开源工具"]
lang: "zh-CN"
wechatTitle: "euv：wasm-bindgen封装的Rust前端框架拆解"
wechatDigest: "MIT 15星；基于wasm-bindgen非独立编译链；html!宏+Signal响应式+CSS宏；Yew/Leptos早先五年"
---

有人说 euv 让 Rust 第一次成为浏览器里的一等公民，`cargo build --release` 一行搞定，再也不用碰 Emscripten。这个说法激动人心——也需要拆一下。

GitHub: https://github.com/euv-dev/euv | ⭐ 15 | MIT | Rust | v0.28.9

---

## 它实际上是什么

euv 是一个 Rust Web UI 框架，核心是在 **wasm-bindgen / web-sys / js-sys** 之上加了一层高级封装：

- `html!` 宏：声明式 UI，编译期转为虚拟 DOM 结构
- `Signal` / `SignalCell`：响应式状态，类似 SolidJS 的 Signal 模型
- `computed!` / `watch!`：派生状态和副作用
- `class!` / `vars!`：CSS-in-Rust 宏，支持伪类（`PseudoRule`）和媒体查询（`MediaRule`）
- `#[component]` 属性宏：定义组件
- `NodeRef`：响应式 DOM 引用句柄
- Canvas / WebGL / Audio / MediaStream API 封装

项目结构是 7 个 workspace crate：`core`、`macros`、`cli`、`ui`、`engine`、`example`、`docs`。

---

## 「不需要 Emscripten」是真的

这一点是准确的——但原因不是「欧拉，euv 做到了 Emscripten 做不到的事」。

**Emscripten 是 C/C++ → WASM 的编译器**，从来就不在 Rust 的工具链里。Rust 有自己的 WASM 后端（`wasm32-unknown-unknown` target），配合 `wasm-bindgen` 实现 JS 互操作。euv 用的就是这条标准路径。

所以正确的表述是：**Rust → WASM 这件事本来就不需要 Emscripten**，euv 只是在这条已有的路径上做了更高级的封装。

---

## 「cargo build --release 就这一行」的实际情况

这个说法不完全准确。euv 的工具链依赖是：

```toml
# Cargo.toml 里的关键依赖
wasm-bindgen = "..."
wasm-bindgen-futures = "..."
web-sys = { features = [...] }  # 大量 feature flag
js-sys = "..."
```

要让 Rust 代码真正跑在浏览器里，你还需要：

```bash
# 先安装 wasm-pack（一次性操作）
cargo install wasm-pack

# 实际构建命令（euv 的 CLI 封装了这个）
wasm-pack build --target web

# 或者用 euv 的 cli crate 简化
cargo run -p euv-cli -- build
```

`cargo build --release` 生成的是本地二进制，不是浏览器可以加载的 `.wasm` + `.js` 绑定对。euv 的 CLI 封装了这个复杂度，这确实是一个有价值的开发体验改善——但「一行」是简化描述，不是字面准确。

---

## 「第一个用所有权检查写出来的 Rust 前端框架」是不对的

Rust WASM UI 框架这个赛道：

| 框架 | 发布年份 | Stars（约） | 备注 |
|------|---------|------------|------|
| **Yew** | 2018 | 30K+ | 最成熟，虚拟 DOM |
| **Seed** | 2019 | 3.5K | Elm 架构风格 |
| **Sycamore** | 2021 | 2.5K | 信号系统，无虚拟 DOM |
| **Leptos** | 2022 | 17K+ | 细粒度响应式，SSR 支持 |
| **Dioxus** | 2022 | 25K+ | 跨平台（Web/Desktop/Mobile） |
| **euv** | 2026 | 15 | 这篇文章的主角 |

euv 是这个赛道里最年轻的项目之一，不是先驱。它和 Leptos 的 Signal 模型最像，差别在于 euv 更侧重多媒体 API（WebGL/Canvas/Audio）和 CSS-in-Rust 宏。

---

## 值得注意的设计细节

**DOM 帮助函数名随机化**

euv 的 DOM 操作帮助函数名包含微秒级时间戳编码后缀，比如 `set_class_f7a3e2` 而不是直接 `set_class`。目的是防止恶意 payload 预先猜测函数名来占用注入点。这是一个偏安全的工程设计，在其他 UI 框架里少见。

**642+ 测试，1,285 次提交，2 人**

15 颗星的项目跑了 1,285 次提交，测试覆盖 642+，两位贡献者。说明它不是随便丢上来的玩具，有人在认真维护。但这也意味着生态系统、文档、社区支持都还在早期。

---

## 怎么上手

README 目前极简，没有正式的「快速开始」文档。参考 `example` crate：

```bash
git clone https://github.com/euv-dev/euv.git
cd euv

# 安装依赖
cargo install wasm-pack

# 运行示例
cd example && wasm-pack build --target web
# 然后用任意静态服务器打开 index.html
python3 -m http.server 8080
```

一个简单的组件看起来像：

```rust
use euv::prelude::*;

#[component]
fn Counter() -> impl View {
    let count = Signal::new(0i32);

    html! {
        <div class={class!("counter")}>
            <p>{ count }</p>
            <button on:click={move |_| *count.write() += 1}>"+1"</button>
        </div>
    }
}
```

CSS 宏：

```rust
class! {
    ".counter" {
        display: "flex";
        flex_direction: "column";
        gap: "8px";
    }
}
```

---

## 适合什么场景

**适合**：
- 想在 Rust 工程里写 WebGL/Canvas/Audio，又不想手写大量 wasm-bindgen 绑定
- 喜欢 CSS-in-Rust 宏而不是 `.css` 文件
- 项目不需要 SSR，纯客户端渲染

**不适合**：
- 需要 SSR / 服务端渲染：选 Leptos
- 需要跨平台（Desktop/Mobile）：选 Dioxus
- 需要成熟生态和大量文档：选 Yew

---

## 局限

- **15 颗星**：生态极早期，社区小，遇到问题基本靠自己看源码
- **无 benchmark**：没有和 Yew/Leptos/Dioxus 的性能对比数据，不知道虚拟 DOM 实现的质量
- **文档贫乏**：README 极简，`docs` crate 存在但内容有限
- **2 位贡献者**：维护风险集中，如果核心开发者停止维护，项目可能停滞

---

> MIT 开源。15 颗星的早期项目，API 可能随版本变化。开源仅供学习参考。

---

<!--EN-->

## euv: What This Rust WASM UI Framework Actually Does

Someone called euv "Rust's first-ever first-class citizen in the browser, just `cargo build --release`." That framing is worth unpacking.

GitHub: https://github.com/euv-dev/euv | ⭐ 15 | MIT | Rust | v0.28.9

---

### What It Actually Is

euv is a Rust web UI framework layered **on top of wasm-bindgen / web-sys / js-sys** — not a standalone compilation toolchain. It adds:

- `html!` macro: declarative UI, compiles to virtual DOM at build time
- `Signal` / `SignalCell`: reactive state system (SolidJS-style)
- `computed!` / `watch!`: derived state and side effects
- `class!` / `vars!`: CSS-in-Rust macros with pseudo-class and media query support
- `#[component]` attribute macro for defining components
- `NodeRef`: reactive DOM reference handles
- Canvas / WebGL / Audio / MediaStream API wrappers

7 workspace crates: `core`, `macros`, `cli`, `ui`, `engine`, `example`, `docs`.

---

### "No Emscripten" Is Accurate — But Misleading

Emscripten is a C/C++ → WASM compiler. It was never part of the Rust toolchain. Rust has its own WASM backend (`wasm32-unknown-unknown`) with `wasm-bindgen` for JS interop. euv uses that standard path. Rust never needed Emscripten — euv just builds a developer-friendly layer on top of what already exists.

---

### "Just cargo build --release" — The Fine Print

You still need wasm-pack, and the actual compile step goes through it:

```bash
cargo install wasm-pack
wasm-pack build --target web
```

euv's CLI crate abstracts this, which is a genuine DX improvement — but it's not a single `cargo build`. Wasm output needs extra tooling that the standard `cargo build` pipeline doesn't handle.

---

### "First Rust Frontend Framework" Is Not Accurate

The Rust WASM UI framework space has been active for years:

| Framework | Year | Stars (approx) |
|-----------|------|---------------|
| **Yew** | 2018 | 30K+ |
| **Sycamore** | 2021 | 2.5K |
| **Leptos** | 2022 | 17K+ |
| **Dioxus** | 2022 | 25K+ |
| **euv** | 2026 | 15 |

euv most resembles Leptos in its Signal-based reactivity model. Its differentiators are deeper multimedia API integration (WebGL/Canvas/Audio) and CSS-in-Rust macros.

---

### Interesting Design Detail: Randomized DOM Helper Names

euv appends microsecond-timestamp-encoded suffixes to DOM operation helper function names (e.g., `set_class_f7a3e2` instead of `set_class`). This prevents malicious payloads from pre-occupying injection points by guessing function names — an unusual security hardening approach for a UI framework.

---

### Reality Check

- **15 stars**: very early ecosystem, minimal community support
- **No benchmarks**: no performance comparison against Yew/Leptos/Dioxus
- **Minimal docs**: README is sparse; `docs` crate exists but is thin
- **2 contributors**: concentrated maintenance risk
- **1,285 commits, 642+ tests**: actively developed and not a toy project

**Use if**: you want Rust WebGL/Canvas/Audio with less boilerplate, or you prefer CSS-in-Rust macros.  
**Don't use if**: you need SSR (→ Leptos), cross-platform (→ Dioxus), or a mature ecosystem (→ Yew).

---

> MIT. 15 stars, early-stage project. API may change across versions. For technical reference only.
