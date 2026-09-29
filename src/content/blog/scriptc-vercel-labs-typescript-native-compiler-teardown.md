---
title: "scriptc：Vercel 把 TypeScript 编译成原生二进制，5000 星，启动比 Node 快 35 倍"
description: "vercel-labs/scriptc，Apache 2.0，5000+ 星，2026 年 7 月开源。TypeScript 直接编译成无 JS 引擎的原生可执行文件，CLI 冷启动 1.78ms vs Node 61.78ms。三层架构：静态编译 → 嵌入 quickjs-ng（~620KB）动态降级 → 编译拒绝。核心红旗：npm 包兼容性差，真实项目百报错，计算性能反比 Node 慢 7.5 倍。"
pubDate: 2026-09-29
heroImage: "../../assets/images/scriptc-vercel-labs-typescript-native-compiler-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["TypeScript", "编译器", "原生二进制", "开源拆解", "Vercel", "性能"]
lang: "zh-CN"
wechatTitle: "scriptc：TypeScript编译成原生二进制的Vercel实验"
wechatDigest: "5K星Apache 2.0；启动1.78ms比Node快35倍；但计算慢7.5倍；npm兼容性是真实门槛"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。

---

## 定位：把 TypeScript 变成不依赖 JS 引擎的本地可执行文件

Go 程序员运行 `go build`，得到一个无外部依赖的二进制，直接部署。TypeScript 程序员历来做不到——总需要 Node、Bun 或某个 JS 运行时。

**vercel-labs/scriptc** 想改变这件事。

用法是：

```bash
scriptc build hello.ts        # 编译成本地可执行文件
./hello                       # 直接运行，无需 Node
```

输出物里没有 Node，没有 V8，也没有 Deno。如果一切正常，你得到一个几 MB 的原生 ELF/Mach-O/PE 二进制。

仓库：github.com/vercel-labs/scriptc  
**Stars：5,000+ | License：Apache 2.0 | 创建：2026-07-22 | 最新版：0.0.16**

---

## 架构：TypeScript → 类型化 IR → LLVM → 原生

编译流水线分四步：

```
TypeScript 源码
    ↓
tsc（原版 TypeScript 编译器）：解析 + 类型检查
    ↓
类型化 IR（Typed Intermediate Representation）
    ↓
后端选择：
  --backend llvm  →  LLVM IR → 汇编 → 目标文件 → 原生可执行文件（默认）
  --backend c     →  可读 C（含源行注释，永久参考后端）
  --output wasm   →  WebAssembly via WASI Preview 1
```

IR 是前后端唯一接口。LLVM 是默认代码生成器；C 后端始终可用，输出可读代码，每行对应原始 TypeScript 行号。

---

## 三层编译策略

每一段代码会被分到三个层级之一：

### 第一层：静态编译（默认）

类型可静态推断的 TypeScript 代码直接走 LLVM，编译成原生指令。这是性能最好的层。

### 第二层：动态降级（--dynamic 标志）

两类代码落入这层：
- **npm 包**（打包进来的 JS）
- **`any` 类型代码**（类型不可静态推断）

这类代码在内嵌的 **quickjs-ng** 引擎里运行，引擎大小约 **620KB**。每个从动态层传回静态层的值，都会在运行时做类型验证。

`--dynamic` 是必须显式启用的标志；不加它，npm 包会在编译时被拒绝。

### 第三层：编译拒绝

无法处理的构造在编译期报错，错误码格式是 `SC001` 之类的 `SC` 码，并附带改写提示，告诉你怎么把代码改成可编译的形式。

---

## 关键数字

| 指标 | scriptc 0.0.16 | Bun 1.3.12 | Node 24.18.0 |
|------|---------------|-----------|-------------|
| CLI 冷启动（中位数） | **1.78ms** | 21.29ms | 61.78ms |
| 空闲内存（无框架 HTTP server） | **1.9MiB** | 更高 | 更高 |
| 字节数组计算（中位数） | 比 Node 慢 **7.5×** | — | 基准 |

启动时间是 scriptc 真正领先的地方：比 Node 快 35 倍，比 Bun 快 12 倍。对 CLI 工具和冷启动频繁的 Serverless 场景，这个差距是真实的。

但计算性能是另一回事——字节数组基准测试里，scriptc 比 Node 慢 7.5 倍。这说明 LLVM 后端目前的优化工作还不到位，不是银弹。

---

## 四个需要正视的问题

### 1. npm 包兼容性极差

一位开发者测试了本地所有项目，每个项目都有数百个报错，绝大多数 npm 依赖被拒绝。

这是当前最大的实用门槛。如果你的代码依赖 npm 生态（express、axios、zod……），你基本上只能用 `--dynamic` 把它们塞进 quickjs-ng——然后就失去了「无 JS 引擎」的卖点。

### 2. 计算性能反而更慢

启动快不代表跑得快。字节数组基准测试显示，scriptc 比 Node 慢 7.5 倍，即使有人专门对代码做了 scriptc 针对性优化。LLVM 后端目前还没有真正发挥出静态编译的潜力。

### 3. 版本 0.0.16 = 极早期实验

主版本号 0.0.x 明确传达了实验状态。Vercel Labs 此前有一个类似项目 **zerolang**，开源后不久便停止维护。有开发者把这段历史作为 scriptc 能否持续维护的风险信号。

### 4. 动态层的隐性成本

用 `--dynamic` 可以绕开编译拒绝，但每个跨越边界的值都需要运行时类型验证，增加了开销。不是免费的后备通道。

---

## WebKit 工程师的批评

Filip Pizlo（苹果 JSC / WebKit JavaScript 引擎核心贡献者）在讨论中质疑了 scriptc 的性能方法论：用 LLVM 编译 TypeScript 未必比精良 JIT 更快，因为 JIT 可以内联、特化、根据实际运行数据优化——而 AOT 编译缺少这些信息。这不是说 scriptc 的路错了，但性能上的期望需要校准。

---

## 什么情况下值得试

现阶段适合的场景：

- **CLI 工具**：冷启动延迟是主要体验瓶颈，且不重度依赖 npm 包
- **Serverless 函数**：冷启动计费，且逻辑够简单（不需要 npm 包）
- **分发单文件工具**：不想让用户装 Node，代码库干净纯 TypeScript

不适合的场景：目前依赖任何非 stdlib npm 包的项目。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 5,000+ |
| License | Apache 2.0 |
| 创建 | 2026-07-22 |
| 当前版本 | 0.0.16 |
| 后端 | LLVM IR（默认）、C（参考）、WASM via WASI Preview 1 |
| 嵌入引擎 | quickjs-ng ~620KB（动态层） |
| CLI 启动 vs Node | 35× 快（1.78ms vs 61.78ms） |
| 计算 vs Node | 7.5× 慢（字节数组基准）|

---

## 综合判断

scriptc 是一个方向正确但还没成熟的研究项目。TypeScript 开发者渴望「一条命令出二进制」的体验，这个需求是真实的，Vercel 有能力把它做成。

启动时间的领先是货真价实的，对 CLI 工具有实际意义。但当前版本对 npm 生态几乎不兼容、计算性能不如 Node，意味着在 99% 的真实项目上还无法直接用。

对比 Bun 的策略——先兼容 Node 生态、再优化性能——scriptc 选择了先做「正确的架构」，再慢慢扩展兼容范围。这个赌注可能成功，也可能像 zerolang 一样半途而废。v0.0.16 阶段，把它当作「值得关注的实验」比「可以依赖的工具」更合适。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## scriptc: Vercel Compiles TypeScript to Native Binaries, 5K Stars, 35× Faster Startup Than Node

> **Open source for learning only**: All projects discussed are from public repositories.

---

### What It Does: TypeScript → Native Binary, No JS Engine

Go developers run `go build` and get a dependency-free binary. TypeScript developers have historically needed Node, Bun, or some JS runtime. **vercel-labs/scriptc** changes that:

```bash
scriptc build hello.ts   # compile to native executable
./hello                  # run directly, no Node required
```

No Node, no V8, no Deno in the output binary.

Repo: github.com/vercel-labs/scriptc  
**5,000+ stars | Apache 2.0 | Created 2026-07-22 | v0.0.16**

---

### Architecture: TypeScript → Typed IR → LLVM → Native

```
TypeScript → tsc (parsing + type checking) → Typed IR
  → LLVM (default): native executable
  → C backend (--backend c): readable, source-annotated C (permanent reference)
  → WASM (--output wasm): WASI Preview 1
```

---

### Three-Tier Compilation

Every construct lands in one of three tiers:

**Tier 1 — Static (default)**: Statically typed TypeScript compiles to native LLVM instructions. Best performance tier.

**Tier 2 — Dynamic (--dynamic flag)**: npm packages (bundled JS) and `any`-typed code run inside an embedded **quickjs-ng engine (~620KB)**. Values crossing back into static code are validated at runtime.

**Tier 3 — Rejected**: Unsupported constructs fail at compile time with an `SC`-prefixed error code and a rewrite hint.

---

### Key Numbers

| Metric | scriptc 0.0.16 | Bun 1.3.12 | Node 24.18.0 |
|--------|---------------|-----------|-------------|
| CLI cold start (median) | **1.78ms** | 21.29ms | 61.78ms |
| Idle memory (bare HTTP server) | **1.9MiB** | higher | higher |
| Byte-array compute | **7.5× slower** than Node | — | baseline |

Startup is scriptc's real win: 35× faster than Node, 12× faster than Bun. Compute throughput is currently 7.5× *slower* than Node.

---

### Four Problems

**1. npm compatibility is the real wall.** One developer tested all their local projects and got hundreds of errors on each — most npm dependencies rejected. `--dynamic` works around it but sacrifices the "no JS engine" benefit.

**2. Compute is slower than Node.** 7.5× slower in the byte-array benchmark, even with scriptc-specific optimizations applied. LLVM hasn't delivered on its promise yet.

**3. v0.0.16 = early experiment.** Vercel's previous similar project (zerolang) went dormant shortly after release. Longevity risk is real and publicly noted.

**4. Dynamic tier overhead.** Every value crossing the static/dynamic boundary is runtime-validated. Not a free fallback.

---

### The Filip Pizlo Critique

Filip Pizlo (Apple JSC / WebKit JS engine core contributor) questioned the performance approach: a mature JIT can inline, specialize, and optimize based on observed runtime data in ways that AOT compilation cannot. Expectations need calibrating accordingly.

---

### When It's Worth Trying

**Good fit today**: CLI tools where cold-start latency matters and you have minimal npm dependencies; serverless functions with simple logic and no npm packages.

**Not ready for**: Any project relying on the npm ecosystem.

---

### Verdict

scriptc's direction is correct: TypeScript developers want `go build` semantics. The cold-start advantage is real and meaningful for CLI tooling. But at v0.0.16, npm incompatibility and below-Node compute performance make it unusable for most real projects.

The strategic bet is "correct architecture first, compatibility later" — the opposite of Bun's "compatibility first, speed second" approach. That bet may pay off, or follow zerolang into dormancy. Treat it as a research project to watch, not infrastructure to build on.

---

> Open source for learning only. Verify license terms before commercial use.
