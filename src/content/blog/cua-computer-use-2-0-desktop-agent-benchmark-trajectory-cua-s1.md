---
title: "Cua：Computer-Use 2.0 开源基础设施，桌面操控降格为工具调用"
titleEn: "Cua: Computer-Use 2.0 Open Infrastructure — Desktop Control as a Tool Call"
description: "MIT，24.7K stars，YC W25。五件套：跨平台桌面驱动、云桌面集群、本地 VM、确定性评测框架、CUA-S1 小模型。核心主张是把 GUI 操作降格为 Agent 的一个工具调用——不是独占前台的循环。CUA-S1-Forms 70 万参数 2.8MB，真实表单 100% 准确率。"
descriptionEn: "MIT, 24.7K stars, YC W25. Five pieces: cross-platform desktop driver, cloud desktop pools, local VM manager, deterministic benchmark with trajectory export, CUA-S1 small model series. Core claim: GUI interaction as a tool call for the primary agent — not a front-stage-grabbing loop. CUA-S1-Forms has 706K params / 2.8MB, 100% accuracy on real forms."
pubDate: 2026-09-20
heroImage: "../../assets/images/cua-computer-use-2-0-desktop-agent-benchmark-trajectory-cua-s1-banner.jpg"
category: "Tech-Experiment"
tags: ["computer-use", "desktop-agent", "benchmark", "trajectory", "local-ai", "open-source"]
lang: zh-CN
---

[Cua](https://github.com/trycua/cua) 是 YC W25 孵化的跨平台桌面 Agent 基础设施，MIT 协议，当前 24,700+ stars。它把一个完整的从训练到评估的闭环——桌面驱动、云桌面集群、本地 VM、评测框架、专用小模型——打包进一套开源工具链。

**仓库**：github.com/trycua/cua | **License**：MIT | **Stars**：24.7K

---

## Computer-Use 2.0 是什么

Cua 用这个词区分两代 Agent 的操作模式：

| | CU 1.0 | CU 2.0 |
|--|--------|--------|
| 工作方式 | 截图 → 理解 → 执行 GUI | GUI 仅是主 Agent 的一个工具调用 |
| 焦点 | 霸占屏幕前台 | 不抢焦点，后台操控 |
| 能力边界 | 单一 GUI 循环 | 代码/API/GUI 在同一任务自由切换 |
| 可观测性 | 低（截图流） | 高（无障碍树 + 轨迹数据） |

核心论点：**桌面操控不应是 Agent 的整个循环，而应是它众多工具调用中的一种。** Agent 可以先读日志、改代码、调 REST API，只有在"GUI 是最佳接口"时才去操控屏幕。

---

## 五件套组件

### 1. Cua Driver（桌面驱动）

跨平台，macOS / Windows / Linux（X11、Sway、GNOME）。特点：

- **不抢焦点**：后台操控原生 App，用户可以同时用电脑
- **双感知流**：无障碍树（Accessibility Tree）+ 截图，Agent 选择用哪个
- **接口**：MCP / CLI / Python SDK / TypeScript SDK
- 已接入：Claude Code、Codex、Hermes、Qwen Code、Factory Droid、Clicky

```python
from cua import Driver

async with Driver() as driver:
    await driver.open_app("Finder")
    await driver.click("Desktop")
    screenshot = await driver.screenshot()
```

### 2. Cua Fleets（云桌面集群）

run.cua.ai，隔离 Sandbox 池，预热消除冷启动延迟。支持 Linux 容器、macOS VM、Windows VM、Android（QEMU）。**注意**：claim 结束后 Pool 保留计费容量，需主动清理。

### 3. Lume（本地 VM 管理器）

仅限 Apple Silicon，用 Apple Virtualization.Framework 跑本地虚拟机，声称 CPU 速度达宿主机 97%。

```bash
/bin/bash -c "$(curl -fsSL https://cua.ai/lume/install.sh)"
lume create --os macos --size 50gb  # macOS 镜像约 50GB
```

**限制**：macOS VM 绑死 Apple Silicon。Linux/Windows/Android 在支持 QEMU 的任何宿主机可跑。

### 4. Cua Bench（评测框架）

确定性三段式：setup → agent execution → evaluation。兼容 OSWorld、ScreenSpot、Windows Arena，支持导出轨迹数据供训练。

**KiCad 专项评测**（25 道专家级 PCB 任务）揭示了真实能力上限：

| 模型 | 完成数/25 |
|------|-----------|
| GPT-5.5 | 6（最佳） |
| Gemini 3.5 Flash | 5（全解）+ 3（部分） |
| 其余 5 个前沿模型 | 0（空白画布任务全部失败） |

**OSWorld 全行业当前仍在 30~50%**——Cua 提供的是 infra，不是 intelligence。

### 5. CUA-S1-Forms（专用小模型）

第一个 System 1 模型，面向表单填写决策场景。

| 参数量 | 体积 | 架构 |
|--------|------|------|
| 706,048（约 70 万） | **2.8 MB** | 字节级嵌入 + 2 层 Transformer Encoder（宽 128，4 头） |

工作方式：不生成文本，单次前向传播对候选动作（FILL / CHECK / CLICK / SKIP）打分并返回概率分布。每个选项作为 query 对 context token 做 attention（AttentionHead 机制）。

**实测性能**：

| 测试集 | CUA-S1-Forms | Jev API |
|--------|--------------|---------|
| 合成测试集 | 99.95% | — |
| 真实表单（3 份 / 196 决策） | **100%** | 83.6% |

**模型限制**：
- 只从文档解析器已提取的实体中选取，无法生成新值
- 合成数据训练为主，真实验证样本少（196 个决策）
- 字节级 encoder，中文不友好
- 仅首发表单场景，其他 GUI 交互尚无对应 S1 模型

---

## 安装

```bash
# Driver（macOS/Linux）
/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"

# Python SDK
pip install cua

# TypeScript SDK
npm install @trycua/cua

# Bench（Python 3.12+ 和 uv）
uv tool install 'cua-bench[browser]'
```

**许可证注意**：可选依赖 `ultralytics` 为 AGPL-3.0，商用前需确认是否引入。

---

## 怎么看这件事

Cua 的价值主要在基础设施层，不是模型层。它把"截图 + 点击"的简单循环拆解成可组合的工具链——驱动、沙盒、评测、轨迹导出——让上层 Agent 系统可以把桌面操控当普通工具调用而非核心循环。

CUA-S1-Forms 的 70 万参数 / 2.8 MB 是它在模型侧的一次表态：对于特定场景的快速决策，不需要大模型。但 196 个真实决策的验证规模很小，距离足够的置信度还有距离。

KiCad 测试数字更能说明现状：最强模型 25 题只过 6 道，OSWorld 全行业卡在 30~50%。这不是在否定 Cua，而是在说整个 Computer-Use 领域的 intelligence 仍然是短板——Cua 让这个短板变得可测量、可观测，这是它真实的贡献。

> 开源代码与模型仅供学习研究，商用前注意 AGPL-3.0 依赖污染风险。

---

<!--EN-->

## Cua: Computer-Use 2.0 Open Infrastructure

[Cua](https://github.com/trycua/cua) (YC W25) is a cross-platform desktop agent infrastructure stack — MIT licensed, 24,700+ stars. It ships five pieces as a single open-source toolkit: a desktop driver, cloud desktop pools, a local VM manager, a deterministic benchmark framework, and a series of tiny specialized decision models (CUA-S1).

**Repo**: github.com/trycua/cua | **License**: MIT | **Stars**: 24.7K

---

### Computer-Use 2.0: The Concept

| | CU 1.0 | CU 2.0 |
|--|--------|--------|
| Execution model | Screenshot → understand → execute GUI | GUI is one tool call among many |
| Focus | Front-stage, cursor-grabbing | Background, non-disruptive |
| Capability | Single GUI loop | Code / API / GUI within the same task |
| Observability | Low (screenshot stream) | High (accessibility tree + trajectory data) |

The core claim: **desktop control should be a tool the primary agent reaches for — not the entire loop**. An agent should be free to read logs, edit code, or call an API, and only drop down to GUI interaction when the screen is the best interface.

---

### Five Components

**Cua Driver** — cross-platform (macOS / Windows / Linux X11/Sway/GNOME). Runs in background without grabbing focus. Exposes both an accessibility tree and screenshots. Integrates via MCP / CLI / Python SDK / TypeScript SDK. Already wired into Claude Code, Codex, Hermes, Qwen Code.

**Cua Fleets** — cloud desktop sandbox pool (run.cua.ai). Pre-warmed to eliminate cold starts. Supports Linux containers, macOS VMs, Windows VMs, Android (QEMU). Note: pool capacity keeps billing after a claim ends — requires manual cleanup.

**Lume** — local VM manager for Apple Silicon only, using Apple Virtualization.Framework. Claims 97% native CPU speed. macOS images are ~50 GB.

**Cua Bench** — deterministic three-stage framework (setup → execution → evaluation). Compatible with OSWorld, ScreenSpot, Windows Arena. Exports trajectory data for training.

**CUA-S1-Forms** — first System 1 model (706K params, 2.8 MB). Single forward pass scores candidate actions (FILL / CHECK / CLICK / SKIP) against extracted entities. No text generation.

---

### Honest Benchmark Numbers

KiCad benchmark (25 expert-level PCB tasks, Cua Bench-driven):

| Model | Completed / 25 |
|-------|----------------|
| GPT-5.5 | 6 (best) |
| Gemini 3.5 Flash | 5 full + 3 partial |
| 5 other frontier models | 0 (all failed on blank-canvas tasks) |

OSWorld: industry-wide still 30–50%. Cua provides infrastructure, not intelligence.

CUA-S1-Forms accuracy:
- Synthetic test set: 99.95%
- Real forms (3 forms / 196 decisions): **100%** vs Jev API's 83.6%
- Validation sample size is small — 196 decisions is not a large production dataset.

---

### Limitations

1. **macOS VM locked to Apple Silicon.** Linux/Windows/Android run on any QEMU host.
2. **macOS images ~50 GB** — not a quick install.
3. **Linux Driver still pre-release.**
4. **CUA-S1-Forms can only pick from already-extracted entities** — cannot generate new values.
5. **Byte-level encoder is not Chinese-friendly.**
6. **Optional `ultralytics` dependency is AGPL-3.0** — commercial use requires careful review.
7. **Fast-moving codebase** (1,300+ stars/week) — pin versions.

---

### Bottom Line

Cua's value is primarily in infrastructure: it decomposes the "screenshot-and-click" loop into composable, observable primitives. The trajectory export and deterministic benchmarking are the most immediately useful pieces for anyone building or evaluating desktop agents. CUA-S1-Forms at 2.8 MB is a credible proof-of-concept that specialized models can handle narrow GUI decisions efficiently — but 196 real-world validation decisions is a thin sample. The KiCad numbers are the most honest signal in the whole package: the intelligence problem in computer-use is wide open, and Cua is making it measurable.

> Open-source code and models for research and learning only. Check AGPL-3.0 transitive dependency exposure before commercial use.
