---
title: "AOHP：让操作系统真正为 AI Agent 而生，清北港三校联合开源"
titleEn: "AOHP: The First Open-Source OS Built for AI Agents — From Tsinghua, PKU, and HKU"
description: "AOHP（Android Open Harness Project）是清华、北大、港大三校联合团队基于 AOSP 开发的开源 OS 级 Agent 基座（arXiv:2606.23449，Apache-2.0）。核心主张：把 Agent 提升为操作系统的第一类公民，而非让 Agent 在为人类设计的界面上笨拙操作。三大机制：个性化服务合成（用户定义的 App）、高效 Agent 接口（并行后台执行）、安全信息流（细粒度数据流追踪）。OpenClaw 基准：完成率 +21%，Token 消耗 -51%。"
descriptionEn: "AOHP (Android Open Harness Project, arXiv:2606.23449, Apache-2.0) is an OS-level agent harness built on AOSP by a joint team from Tsinghua, PKU, and HKU. Core thesis: treat agents as first-class OS actors, not screen-scraping guests on human-designed interfaces. Three mechanisms: personalized service composition (user-defined apps backed by agents), efficient agent interfaces (parallel background execution decoupled from display), and secure information flow (fine-grained taint tracking + sandboxed sensitive values). OpenClaw benchmark: +21.12% completion rate, -51.55% token cost."
pubDate: "2026-07-05"
updatedDate: "2026-07-05"
category: "Research"
tags: ["AOHP", "Agent OS", "Android", "AOSP", "清华北大港大", "开源", "移动Agent"]
heroImage: "../../assets/images/aohp-android-agent-os-guide-banner.jpg"
---

> **GitHub**: [aohp-os/aohp](https://github.com/aohp-os/aohp) · **arXiv**: [2606.23449](https://arxiv.org/abs/2606.23449) · **Apache-2.0** · 清华大学 · 北京大学 · 香港大学

---

## 一个被忽视的根本矛盾

当前 AI Agent 的主流用法是这样的：拿一个为人类设计的 GUI，让 Agent 通过截图 + 模拟点击来操作它。

这条路能走，但代价巨大：
- Agent 需要反复截图解析界面，每一步都要询问 LLM "下一步点哪里"
- 所有操作必须在前台逐步串行执行，不能并行
- 应用之间的数据被沙箱隔离，Agent 要跨 App 提取信息就要绕很多圈
- 敏感数据（密码、支付信息）在 Agent 操作过程中以明文流经整个系统

**清华、北大、港大的研究团队把这个矛盾看得很透彻**：问题不是 Agent 不够聪明，而是**操作系统从来没有为 Agent 而设计**。

他们的答案是 **AOHP（Android Open Harness Project）**——基于 AOSP（Android 开源项目）构建的 OS 级 Agent 基座，把整个操作系统架构调整为以 Agent 为中心。

---

## 传统 Android vs AOHP：一张对比图说明白

[![传统 Android 与 AOHP 架构对比](https://github.com/aohp-os/aohp/raw/main/images/comparison.png)](https://github.com/aohp-os/aohp/blob/main/images/comparison.png)

| 维度 | 传统 Android | AOHP |
|---|---|---|
| **交互模型** | 用户直接操作开发者定义的 App 界面 | Agent 作为 OS 第一类公民，在用户意图下行动 |
| **交互入口** | 固定的 App GUI，由开发者决定 | 由 Agent 生成的个性化服务入口 |
| **执行模式** | 单线程前台执行，绑定屏幕 | 并行后台执行，与屏幕解耦 |
| **系统记忆** | 数据碎片化，锁在各 App 内部 | OS 统一管理跨 App 记忆，支持任务个性化 |
| **安全与隐私** | 粗粒度 App 权限，数据流不透明 | 细粒度信息流追踪，敏感数据沙箱化 |

---

## 三大核心机制

### 1. 个性化服务合成：用户定义 App，而非开发者定义 App

这是 AOHP 最激进的设计决策。

传统操作系统里，App 的界面和功能由开发者决定。你想查一下某个联系人最近的航班，你得打开航空公司 App → 登录 → 查询 → 然后再打开通讯录 → 找到联系人 → 发消息。整个流程由多个 App 的界面边界切分。

AOHP 的做法：你说"给王总发一条消息，附上他今晚抵达的航班号"。OS 的 Agent 层直接调用系统 API、后台 CLI 和必要的 GUI，把整个流程合成为一个"用户定义的 App"——这个 App 不是安装包，而是为这次需求即时生成的服务单元，前端 UI 也是 Agent 生成的。

**这意味着 App 的边界从"开发者的产品规划"变成了"用户的实际需求"。**

### 2. 高效 Agent 接口：并行后台执行，与屏幕解耦

传统 Android 上运行 Agent 有一个隐性约束：所有交互都必须在前台屏幕上串行发生。

AOHP 重新设计了 Agent 的执行模型：

- **后台并行执行**：多个 Agent 任务可以同时在后台运行，不占用屏幕
- **API 优先**：Agent 优先通过系统 API 和 CLI 完成任务，只在必要时才回退到 GUI 操作
- **原生内存接口**：OS 直接提供跨 App 的任务记忆 API，Agent 不需要自己维护上下文状态

结果体现在基准测试里：相同任务，AOHP 上的 Agent 比在传统 Android 上少发 48% 的 LLM 请求，少用 52% 的 Token，执行时间减少 44%。

### 3. 安全信息流：细粒度数据追踪，敏感值沙箱化

让 Agent 访问系统级权限是一把双刃剑——Agent 能力越强，安全边界就越重要。

AOHP 引入了**信息流追踪（Information Flow Tracking）**机制：

- 敏感数据（密码、支付信息、位置）在系统层被打上"污点标记"（taint）
- 任何涉及敏感数据的操作，Agent 在界面上看到的是引用指针（vault reference），而不是明文
- 需要用户同意的高风险操作（转账、支付确认）会自动触发用户确认弹窗
- 敏感事件被裁剪处理，保留污点元数据但不泄露原始内容

五项安全检查全部通过，包括"不支持的访问直接失败关闭"（fail-closed）——这比"允许通过但留日志"的设计更保守。

---

## 系统架构

[![AOHP 系统架构](https://github.com/aohp-os/aohp/raw/main/images/overview.png)](https://github.com/aohp-os/aohp/blob/main/images/overview.png)

AOHP 在 AOSP 的系统层和框架层引入 Agent 基础设施，但**保留了完整的 Android 软件生态和硬件生态**。这是一个关键决策：不是重写操作系统，而是在现有 Android 基础上做最小必要的架构扩展。

这意味着：
- 现有的 Android App 仍然可以运行
- 成熟的 Android 驱动和硬件支持可以直接复用
- 开发者只需要学习新的 Agent API，不需要从零适配

---

## 基准测试结果

评估采用 [OpenClaw](https://github.com/openclaw/openclaw) 基准，30 个覆盖真实移动场景的任务，包括 GUI 操作、非 GUI 操作、事件捕获、多源检索、记忆管理和混合工作流。

### 完成率

| 设置 | 完成率 | 完全完成 | 部分完成 |
|---|---|---|---|
| OpenClaw on 传统 Android | 54.44% | 13 / 30 | 7 / 30 |
| OpenClaw on AOHP | **75.56%** | **20 / 30** | 5 / 30 |
| 提升 | **+21.12%** | **+7 tasks** | — |

### 执行成本（11 个双方都完全完成的任务）

| 设置 | Tool Calls | 执行时长 | Token 消耗 | LLM 请求数 |
|---|---|---|---|---|
| 传统 Android | 233 | 33.94 分钟 | 7.10M | 273 |
| AOHP | **129** | **18.93 分钟** | **3.44M** | **143** |
| 降低幅度 | **-44.64%** | **-44.21%** | **-51.55%** | **-47.62%** |

这组数字传递的信息很明确：**相同能力的 Agent 模型，在为 Agent 设计的 OS 上，效率接近翻倍**。

---

## 独特定位：与其他 Agent 操作系统框架的区别

目前市面上有不少 Agent 框架（AutoGPT、LangChain、各类 Computer Use 实现），但 AOHP 的定位与它们根本不同：

| 对比维度 | 现有 Agent 框架 | AOHP |
|---|---|---|
| **层级** | 应用层（在 OS 之上运行） | OS 层（修改 AOSP 内核/框架层） |
| **执行模型** | 串行前台，截图-点击循环 | 并行后台，API 优先 |
| **内存管理** | 框架自己维护上下文 | OS 原生提供跨 App 记忆 |
| **安全边界** | 依赖 App 权限模型 | OS 级信息流追踪 |
| **生态兼容性** | 需要 App 开放 API | 直接复用完整 Android 生态 |

简单说：现有框架是在现有 OS 上**绑手脚地跑**，AOHP 是为 Agent 专门**重建了运动场**。

---

## 它能为 Agent 开发提供什么？

如果你在做移动端 AI Agent，AOHP 提供的不是另一个 Python 库，而是**整个运行时环境的升级**：

**对 Agent 开发者：**
- 直接调用系统 API 和 CLI，不再依赖截图解析 GUI
- 原生的跨 App 记忆 API，不需要自己实现上下文管理
- 后台并行执行支持，Agent 任务不再相互阻塞

**对研究者：**
- 一个可复现的开源 AOSP fork，可以直接在 Cuttlefish 模拟器上跑
- 开放的 OpenClaw 基准，统一的 Agent 能力评估框架
- 安全研究的可控测试环境（信息流追踪可以直接研究）

**对产品方向：**
- "用户定义的 App"这个概念，直接预示了下一代移动操作系统的交互范式——用户不再浏览 App Store，而是描述需求，OS 即时生成服务

---

## 快速上手

AOHP 以可运行的 AOSP fork 形式发布，在 Cuttlefish 虚拟机上可以直接运行：

```bash
# 克隆开发框架
git clone git@github.com:aohp-os/aohp.git
cd aohp

# 初始化 AOSP + AOHP manifests（Android 16 QPR2）
cd AOSP && repo init -b android16-qpr2-release
cd .repo && git clone git@github.com:aohp-os/local_manifests.git && cd ..
repo sync -j4

# 编译
bash scripts/build.sh

# 启动 Cuttlefish 模拟器
source AOSP/build/envsetup.sh
lunch aosp_cf_x86_64_phone_aohp-trunk_staging-userdebug
sudo -E bash -c 'ulimit -n 65536; '"$ANDROID_HOST_OUT"'/bin/launch_cvd --report_anonymous_usage_stats=n' &
```

模拟器在 `https://localhost:8443/` 打开。完整的开发指南（网络配置、多实例、贡献流程）在 [Development Guide](https://github.com/aohp-os/aohp/blob/main/docs/DEVELOPMENT.md)。

> **注意**：AOHP 目前是**早期研究原型**，还不适合生产环境或安全敏感工作负载。

---

## 写在最后

AOHP 最重要的贡献不是某个性能数字，而是它提出了一个**系统性的问题重构**：

我们花了那么多精力让 Agent 学会模仿人类操作手机，但从来没有问过——**如果手机操作系统从一开始就是为 Agent 设计的，应该长什么样？**

这篇论文和这个开源项目给出了第一个可运行的答案。

---

> **GitHub**: [aohp-os/aohp](https://github.com/aohp-os/aohp) · **arXiv**: [2606.23449](https://arxiv.org/abs/2606.23449) · **Apache-2.0**  
> **作者**：Shanhui Zhao, Jiacheng Liu et al. · 清华大学 / 北京大学 / 香港大学

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: AOHP (Android Open Harness Project, arXiv:2606.23449, Apache-2.0) is an OS-level agent harness built on AOSP by a joint team from Tsinghua, PKU, and HKU. Core insight: the reason AI agents on mobile are slow, expensive, and unsafe is that the OS was never designed for agents. AOHP treats agents as first-class OS actors, introducing three mechanisms: personalized service composition (user-defined apps backed by agents), efficient agent interfaces (parallel background execution, API-first, OS-native cross-app memory), and secure information flow (fine-grained taint tracking, vault references for sensitive values). OpenClaw benchmark on 30 real-world tasks: +21.12% completion rate, −51.55% token cost, −44.21% execution time, −47.62% LLM requests — on the same agent model.

---

## What Problem It Solves

Current agent frameworks run at the application layer: they screenshot the screen, parse it with an LLM, simulate a tap, repeat. This loop works but it's expensive (every step needs an LLM call), serial (can't parallelize across apps), and unsafe (sensitive data flows in plaintext through the agent pipeline). AOHP solves these at the OS layer rather than patching around them at the framework layer.

## Three Core Mechanisms

**Personalized service composition**: Instead of developer-defined app interfaces, AOHP enables user-defined apps — generated on the fly from the user's expressed need, backed by agents orchestrating APIs, CLIs, and GUI as needed.

**Efficient agent interfaces**: Background parallel execution decoupled from the screen display. API-first execution model (falls back to GUI only when necessary). OS-native cross-app memory API (agents don't maintain their own context).

**Secure information flow**: Sensitive values (passwords, payment info) are replaced with vault references in the agent's view. High-risk operations require user consent. Unsupported access fails closed, not open. All five security policy cases enforced in evaluation.

## Why It Matters for Agent Developers

AOHP isn't another Python library — it's an upgrade to the entire runtime environment. Agents can call system APIs and CLIs directly instead of screen-scraping. Cross-app memory is OS-native. Background parallel execution is built in. The same agent model, half the tokens and half the time.

## Getting Started

AOSP fork that runs on Cuttlefish (virtual machine). `repo sync` + `bash scripts/build.sh` + `launch_cvd`. Emulator at `https://localhost:8443/`. Full guide at [DEVELOPMENT.md](https://github.com/aohp-os/aohp/blob/main/docs/DEVELOPMENT.md).

Early-stage research prototype. Not production-ready. Feedback and contributions welcome.

**Links**: [GitHub](https://github.com/aohp-os/aohp) · [arXiv:2606.23449](https://arxiv.org/abs/2606.23449)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
