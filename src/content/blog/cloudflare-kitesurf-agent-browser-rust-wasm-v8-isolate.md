---
title: "Cloudflare 把浏览器也 Serverless 了：Kitesurf 调研"
titleEn: "Cloudflare Made the Browser Serverless Too: A Look at Kitesurf"
description: "Cloudflare 开源了 Kitesurf，一个专为 AI Agent 构建的浏览器，完全跑在 Cloudflare Workers 上。没有 Chrome 进程，Rust+WASM 做引擎，页面 JS 直接跑在 V8 isolate 里。CPU 消耗比 Chromium 低 3-4x，内存低 5-7x。本文深度分析架构、性能数据、工程接入方式，以及这件事对 AI Agent 基础设施的意义。"
descriptionEn: "Cloudflare has released Kitesurf, an agent-first browser built entirely on Cloudflare Workers. No Chrome process — Rust+WebAssembly for the engine, page JavaScript running directly in V8 isolates. 3-4x less CPU and 5-7x less memory than Chromium. This article analyzes the architecture, performance data, engineering integration, and what this means for AI agent infrastructure."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["Cloudflare", "浏览器引擎", "AI Agent", "WebAssembly", "Rust", "Serverless", "Mycelium"]
heroImage: "../../assets/images/cloudflare-kitesurf-agent-browser-rust-wasm-v8-isolate-banner.jpg"
---

*by Mycelium Protocol*

---

浏览器是互联网的操作系统。过去几十年，这句话意味着：一个体量巨大的本地进程——Chromium、Firefox、Safari——把 HTML、CSS、JavaScript 解析成你看到的页面。

Cloudflare 刚刚发布了 **Kitesurf**，一个不跑本地进程的浏览器。

**它完全运行在 Cloudflare Workers 上**。没有 Chrome 进程，没有 Node.js，没有 Electron。Rust+WebAssembly 做引擎，页面 JavaScript 直接跑在 V8 isolate 里。

---

## 为什么要造这个

原因很直接：Chromium 是为人类设计的，不是为 AI Agent 设计的。

人类需要：标签页、主题、浏览器扩展、跨设备同步、流畅的 60fps 滚动、像素级的渲染精度。

**Agent 不需要这些**。Agent 关心的是：token 数量、context 窗口、可扩展性、成本。一个 HTML 解析略有偏差的页面对 Agent 来说完全可以接受，但它无法接受每个实例消耗 270 MiB 内存。

Cloudflare 的 Browser Run 产品（原 Browser Rendering）随着 AI 的爆发看到了巨大增长，但用 Chromium 给每个 Agent 分配独立实例的成本是结构性问题。Kitesurf 是这个问题的答案。

---

## 架构：四个 Worker，一个浏览器

Kitesurf 由四个核心组件构成，每个都是独立的 Worker：

```
[外部 CDP 客户端]
       ↓
   Engine Worker          ← 唯一对外暴露的组件，持有 session 状态
       ↓        ↓
 PageScript     PageRenderer
  (V8 isolate)  (光栅化渲染)
       ↓
 SandboxOutbound          ← 唯一能访问网络的组件
```

### Engine：唯一有状态的组件

Engine 是整个系统里唯一持有状态的地方，用 **SQLite-based Durable Objects** 存储 session 状态。它暴露 Chrome DevTools Protocol (CDP) WebSocket 和 HTTP REST 接口，这意味着：**你的 Puppeteer、Playwright、chrome-remote-interface 代码不需要改动，直接指向 Kitesurf 就能用**。

### PageScript：页面 JS 跑在 V8 isolate 里

这是整个架构最有意思的部分。

每次新页面加载或 out-of-process iframe（OOPIF），Kitesurf 用 **Dynamic Workers** 动态创建一个新的 PageScript isolate。这个 isolate 持有：
- 一个干净的 `globalThis`
- 完整的 DOM document 对象

HTML 和 CSS 解析用的是 Rust 组件：
- **Blitz**（DioxusLabs）——模块化渲染引擎
- **Stylo**（来自 Firefox/Servo）——高性能 CSS 解析器

每个 `<script>` 标签和 `.wasm` 文件，**都在同一个 isolate 里直接运行**。这不是模拟执行，是真实的 V8。

**eval 的问题**：Workers 出于安全原因不支持 `eval()`。Kitesurf 的解法是引入 [Boa JS](https://boajs.dev/)——一个用 Rust 写的 ECMAScript 引擎，在 Workers 里跑来处理偶尔出现的 eval 调用。运行时套运行时，不优雅但能用，等 Workers 原生支持 eval 后会迁移掉。

### PageRenderer：Rust 光栅化出像素

PageRenderer 从 PageScript 拿到页面对象（场景树），用 **blitz-paint** 光栅化成像素缓冲区，再通过 **Parley** 做字体整形和文本布局，最后返回 JPEG/PNG/PDF。

关键设计：**PageRenderer 不持有任何页面状态**。Engine 通过 Worker RPC 调用 `renderFrame()`，拿到结果。如果 PageRenderer 卡住了，Engine 直接杀掉重启一个新的，成本极低。

### SandboxOutbound：唯一触网的组件

所有网络请求——图片、字体、CSS、JS、`fetch()` 调用——必须经过 SandboxOutbound，其他组件被 Dynamic Workers 强制禁止直接访问网络。这里负责：

- CORS 执行
- 注入浏览器标准 Headers
- 响应过滤
- 每个页面独立的 cookie jar

失败 policy 的请求返回 403，不泄露到其他 session。

---

## 四个设计原则

**1. 无状态优先**：能无状态的组件就无状态。失败时直接丢弃重建，不需要恢复任何中间态。唯一例外是 Engine，它必须存 session 状态。

**2. Rust when possible**：所有 Rust 代码直接编译到 WebAssembly（用 wasm-bindgen，不用 Emscripten）。Emscripten 需要大量模拟层，产物臃肿；原生 Rust→WASM 更小、更快、更可靠。

**3. 失败降级，不 crash**：任何失败都降级到空白帧或缺失元素，绝不让整个 session 死掉。这是给「野生网页」设计的，不是给可控环境。

**4. 用 AI 构建 AI 的基础设施**：Kitesurf 的大量开发工作由 AI Agent 完成，以 [Web Platform Tests (WPT)](https://github.com/web-platform-tests/wpt) 作为明确的成功标准。人类专注架构决策和代码审查，Agent 负责实现——这本身就是一个 meta 层面有意思的案例。

---

## 性能数据：CPU 和内存是 Chromium 的几分之一

在 14 个 URL 的语料库上，Browser Run 快速操作的中位数对比（Kitesurf vs Chromium 热实例）：

| 指标 | Kitesurf | Chromium（热池） | Kitesurf 相对 |
|------|---------|--------------|-------------|
| CPU：截图 | 380 ms | 1,173 ms | **少 3.1x CPU** |
| CPU：HTML 提取 | 229 ms | 877 ms | **少 3.8x CPU** |
| 内存：截图 | 57.8 MiB | 271.0 MiB | **少 4.7x 内存** |
| 内存：HTML 提取 | 39.4 MiB | 273.7 MiB | **少 7.0x 内存** |
| 挂钟时间：截图 | 1,148 ms | 637 ms | 慢 1.8x |
| 挂钟时间：HTML 提取 | 820 ms | 472 ms | 慢 1.7x |

Chromium 赢在速度——已经 JIT 热身过的引擎就是快。Kitesurf 赢在资源消耗——CPU 少用 3-4x，内存少用 5-7x。

对 AI Agent 而言，这个取舍是合理的：**钱是按资源计费的，不是按毫秒计费的**。内存降低 7 倍意味着同等预算下可以跑 7 倍的并发实例。

---

## WPT 覆盖率：215,000+ 测试通过，每周仍在增加

Kitesurf 目前通过了 215,000+ 个 WPT 测试，且覆盖率每周增加数百个。

关键覆盖方向：CSS、DOM、HTML、Selection、SVG、XHR——这些恰好是 Agent 最依赖的部分。

已验证可以正确渲染的网站：TodoMVC（Vanilla/React/Vue/Angular/Preact）、Wikipedia、Hacker News、Cloudflare 博客、Cloudflare Dashboard。

Doom 也跑通了。Cloudflare 官方认证的测试标准。

---

## 工程接入：`browser=kitesurf` 参数

接入极其简单。Browser Run 的所有接口已经支持，只需加参数。

**截图 Quick Action**：

```bash
curl -X POST 'https://api.cloudflare.com/client/v4/accounts/<accountId>/browser-run/screenshot?browser=kitesurf' \
  -H 'Authorization: Bearer <apiToken>' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}' \
  --output "screenshot.png"
```

**MCP 接入（给 AI Agent 用）**：

```json
{
  "mcp": {
    "kitesurf": {
      "type": "local",
      "command": [
        "npx", "-y", "chrome-devtools-mcp@latest",
        "--wsEndpoint=wss://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/browser-run/devtools/browser?browser=kitesurf",
        "--wsHeaders={\"Authorization\":\"Bearer <API_TOKEN>\"}"
      ],
      "enabled": true
    }
  }
}
```

**Puppeteer**（现有代码几乎不改）：

```javascript
import puppeteer from '@cloudflare/puppeteer';

export default {
  async fetch(request, env) {
    const browser = await puppeteer.launch(env.MYBROWSER, {
      browser: 'kitesurf'
    });
    const page = await browser.newPage();
    await page.goto('https://example.com');
    const screenshot = await page.screenshot();
    await browser.close();
    return new Response(screenshot, {
      headers: { 'content-type': 'image/png' }
    });
  }
};
```

**当前不支持的场景**：视频播放、WebGL、需要真实 TLS 指纹的 bot-challenge、需要持久状态的长会话——这些继续用 Chromium。

---

## 调研结论：这件事为什么重要

Kitesurf 不只是一个「更便宜的浏览器」。它是一种范式转移的证明：

**浏览器不再必须是一个单体应用**。

传统浏览器的每一个部分——网络、解析、JS 执行、渲染——都在一个进程里，资源共享，状态混杂。Kitesurf 把这些拆成独立的无状态函数，每个函数只能访问它严格需要的资源，失败了直接丢弃重建。

这和 Serverless 把服务器应用拆成函数是同一件事。

对 AI Agent 基础设施来说，这个方向意义深远：

1. **成本结构变了**：不是「租一个 Chromium 实例等着」，而是「用多少付多少的计算」，适合 AI 工作负载突发式的特性
2. **隔离是第一公民**：每个 session、每个页面都是全新的 isolate，Agent 扫描任意网站不会在 session 间泄露数据
3. **Puppeteer/Playwright API 兼容**：不需要重写现有工具链，一个参数就能切换
4. **开源即将发布**：Cloudflare 承诺开源，允许用户在自己的账户上部署 Kitesurf 实例

Kitesurf 现在还是 12 周大的 Beta，不适合所有场景。但它证明了「Agent 的浏览器」可以和「人类的浏览器」是完全不同的东西——更轻、更便宜、更安全隔离——而这个方向，值得认真对待。

---

原文：[blog.cloudflare.com/kitesurf](https://blog.cloudflare.com/kitesurf)  
Playground：[kitesurf.cloudflare.app](https://kitesurf.cloudflare.app)

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## Cloudflare Serverless'd the Browser: A Deep Dive into Kitesurf

*by Mycelium Protocol*

---

The browser is the operating system of the internet. For decades, that meant one thing: a massive local process — Chromium, Firefox, Safari — parsing HTML, CSS, and JavaScript into the pages you see.

Cloudflare just released **Kitesurf**, a browser that runs no local process at all.

**It runs entirely on Cloudflare Workers.** No Chrome process. No Node.js. No Electron. Rust+WebAssembly for the engine, page JavaScript running directly in V8 isolates.

---

### Why Build This

The reason is straightforward: Chromium was built for humans, not AI agents.

Humans need: tabs, themes, browser extensions, cross-device sync, smooth 60fps scrolling, pixel-perfect rendering.

**Agents need none of these.** Agents care about token count, context windows, scalability, cost. A page with slightly imperfect CSS parsing is completely fine for an agent. What isn't fine: 270 MiB of memory per instance.

Cloudflare's Browser Run product has seen explosive growth with the rise of AI, but the cost of giving every agent its own Chromium instance is a structural problem. Kitesurf is the answer.

---

### Architecture: Four Workers, One Browser

Kitesurf consists of four core components, each an independent Worker:

```
[External CDP client]
         ↓
   Engine Worker          ← Only public-facing component; holds session state
       ↓        ↓
 PageScript     PageRenderer
  (V8 isolate)  (rasterization)
       ↓
 SandboxOutbound          ← Only component that can touch the network
```

**Engine: The Only Stateful Component**

Engine is the only place in the system that holds state, using **SQLite-based Durable Objects** for session storage. It exposes Chrome DevTools Protocol (CDP) via WebSocket and HTTP REST — meaning **your existing Puppeteer, Playwright, and chrome-remote-interface code works without modification**. Point it at Kitesurf and it just works.

**PageScript: Page JS in a V8 Isolate**

This is the architecturally interesting part.

For every new page load or out-of-process iframe (OOPIF), Kitesurf uses **Dynamic Workers** to spin up a fresh PageScript isolate. This isolate holds a clean `globalThis` and a full DOM document object.

HTML and CSS parsing use Rust components:
- **Blitz** (DioxusLabs) — modular rendering engine
- **Stylo** (from Firefox/Servo) — high-performance CSS parser

Every `<script>` tag and `.wasm` file runs **directly in the same isolate**. Not simulated — real V8.

**The eval problem:** Workers don't support `eval()` for security reasons. Kitesurf's solution: [Boa JS](https://boajs.dev/), an ECMAScript engine written in Rust, running inside Workers to handle eval calls. A runtime inside a runtime — not optimal, but it works. Will migrate away once Workers natively supports eval.

**PageRenderer: Rust Rasterizes the Pixels**

PageRenderer takes the page object (scene) from PageScript, rasterizes it using **blitz-paint** + **Parley** (text shaping and layout), and returns JPEG/PNG/PDF to the Engine via Worker RPC.

Critical: **PageRenderer holds no page state.** Engine calls `renderFrame()` over RPC; if PageRenderer stalls, Engine kills it and relaunches a fresh one. Self-contained, retryable, throwaway.

**SandboxOutbound: The Only Network Component**

All network access — images, fonts, CSS, JS, `fetch()` calls — must go through SandboxOutbound. Dynamic Workers enforces this: other components physically cannot touch the network. SandboxOutbound enforces CORS, injects browser-shaped headers, filters responses, and keeps each page's cookies in their own jar. Policy failures get a 403.

---

### Four Design Principles

**1. Stateless by default:** Every component except Engine is stateless. Failure means discard and restart — nothing to reconstruct, zero recovery cost.

**2. Rust when possible:** All Rust compiled directly to WebAssembly via wasm-bindgen, not Emscripten. Native Rust→WASM avoids emulation layers: smaller, faster, more reliable.

**3. Degrade, never crash:** Any failure produces a blank frame or missing element, never a dead session. Designed for the hostile open web, not a controlled environment.

**4. AI building AI infrastructure:** Large portions of Kitesurf were developed by AI agents, using Web Platform Tests as clear success criteria. Humans focused on architecture and review; agents handled implementation. Meta-interesting on its own.

---

### Performance: 3-7x Less CPU and Memory Than Chromium

Median of five Browser Run quick-action runs across a 14-URL corpus (Kitesurf vs Chromium warm pool):

| Metric | Kitesurf | Chromium (warm pool) | Relative |
|--------|---------|---------------------|---------|
| CPU: screenshot | 380 ms | 1,173 ms | **3.1× less CPU** |
| CPU: HTML extraction | 229 ms | 877 ms | **3.8× less CPU** |
| Memory: screenshot | 57.8 MiB | 271.0 MiB | **4.7× less memory** |
| Memory: HTML extraction | 39.4 MiB | 273.7 MiB | **7.0× less memory** |
| Wall time: screenshot | 1,148 ms | 637 ms | 1.8× slower |
| Wall time: HTML extraction | 820 ms | 472 ms | 1.7× slower |

Chromium wins on speed — a JIT-warmed engine beats a cold software renderer. Kitesurf wins on resources — 3-4× less CPU, 5-7× less memory.

For AI agents, this trade-off is correct: **cloud billing runs on resource consumption, not wall-clock time.** 7× less memory means 7× more concurrent sessions on the same budget.

---

### WPT Coverage: 215,000+ Tests Passing

Kitesurf passes 215,000+ Web Platform Tests and adds hundreds more every week. Strong coverage in CSS, DOM, HTML, Selection, SVG, and XHR — exactly the parts agents rely on most.

Verified compatible sites: TodoMVC (Vanilla/React/Vue/Angular/Preact), Wikipedia, Hacker News, Cloudflare Blog, Cloudflare Dashboard.

Doom also runs. Official Cloudflare certification criteria, apparently.

---

### Engineering Integration: Just Add `browser=kitesurf`

**Screenshot Quick Action:**

```bash
curl -X POST 'https://api.cloudflare.com/client/v4/accounts/<accountId>/browser-run/screenshot?browser=kitesurf' \
  -H 'Authorization: Bearer <apiToken>' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}' \
  --output "screenshot.png"
```

**MCP for AI agents:**

```json
{
  "mcp": {
    "kitesurf": {
      "type": "local",
      "command": [
        "npx", "-y", "chrome-devtools-mcp@latest",
        "--wsEndpoint=wss://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/browser-run/devtools/browser?browser=kitesurf",
        "--wsHeaders={\"Authorization\":\"Bearer <API_TOKEN>\"}"
      ]
    }
  }
}
```

**Not yet supported:** video, WebGL, bot-challenge TLS fingerprinting, long authenticated sessions requiring persistent state. Use Chromium for those.

---

### What This Actually Means

Kitesurf isn't just a "cheaper browser." It's proof of a paradigm shift:

**The browser doesn't have to be a monolithic application.**

Traditional browsers pack every subsystem — networking, parsing, JS execution, rendering — into one process. Kitesurf decomposes them into independent stateless functions, each with access only to exactly the resources it needs, each disposable on failure.

This is the same move Serverless made with server applications.

For AI agent infrastructure, this matters on three levels:

1. **Cost structure changes:** Not "rent a warm Chromium instance and wait" but "pay for exactly the compute used," matching the bursty, unpredictable nature of AI workloads
2. **Isolation is first-class:** Every session, every page gets a fresh isolate. An agent scanning arbitrary sites cannot leak data between sessions by construction
3. **Puppeteer/Playwright compatible:** No toolchain rewrite needed — one parameter switches the underlying engine

Kitesurf is 12 weeks old and not suitable for every use case. But it demonstrates that the "browser for agents" can be a fundamentally different thing from the "browser for humans" — lighter, cheaper, better isolated — and that direction is worth watching carefully.

---

Source: [blog.cloudflare.com/kitesurf](https://blog.cloudflare.com/kitesurf)  
Playground: [kitesurf.cloudflare.app](https://kitesurf.cloudflare.app)

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
