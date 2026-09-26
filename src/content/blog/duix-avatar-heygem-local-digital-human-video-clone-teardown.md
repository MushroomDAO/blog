---
title: "Duix-Avatar（前 HeyGem）：本地离线数字人视频生成深度拆解"
description: "duixcom/Duix-Avatar，15.6K 星，三个 Docker 服务打包 FunASR+Fish-Speech+视频引擎，RTX 4070 必须，70GB 镜像，自定义许可证 1000 MAU 付费门槛，「10 秒克隆」官方文档无依据，本地效果自承比云端差一档。"
pubDate: 2026-09-26
heroImage: "../../assets/images/duix-avatar-heygem-local-digital-human-video-clone-teardown-banner.jpg"
category: "Tech-Experiment"
tags: ["数字人", "视频生成", "本地推理", "Docker", "开源拆解"]
lang: "zh-CN"
wechatTitle: "Duix-Avatar：本地数字人克隆拆解"
wechatDigest: "自定义许可1000 MAU付费门槛；RTX 4070必须；70GB镜像；本地效果自认比云端差"
---

> **开源仅供学习**：本文所涉项目均来自公开仓库，分析仅供技术研究。如需商业使用，请仔细阅读对应许可证条款。

---

## 项目背景

**duixcom/Duix-Avatar**（GitHub：github.com/duixcom/Duix-Avatar）——之前叫做 **HeyGem**，在 v1.0.5（2025 年 8 月）正式改名。由新加坡公司 Duix 出品，定位是「本地全离线数字人视频生成工作台」：上传一段真人视频，克隆外貌和声音，再输入文字脚本，离线生成口播视频。

截至拆解时：**15,585 stars，2,652 forks**，开放问题 422 个。仓库最后一次 push：**2026-04-21**，近 5 个月无代码更新。

---

## 核心功能三件套

Duix-Avatar 的架构由三个 Docker 服务组成：

| 服务镜像 | 来源 | 功能 |
|---------|------|------|
| `guiji2025/fun-asr` | 阿里 FunASR | 语音识别（ASR） |
| `guiji2025/fish-speech-ziming` | Fish-Speech | 语音合成（TTS） |
| `guiji2025/duix.avatar` | 自研（C 语言） | 视频合成引擎 |

三步流程：**外貌克隆** → **声音克隆** → **唇形同步视频生成**，全部通过本地 REST API 串联（训练接口 `/v1/train`，视频合成 `127.0.0.1:8383/easy/submit`）。

---

## 硬件门槛

这是第一个拦路虎。官方明确要求：

- **GPU**：NVIDIA RTX 4070（**必须是 NVIDIA，无 AMD/Apple Silicon 支持**）
- **内存**：32GB RAM
- **存储**：130GB+（C 盘 100GB+，数据盘 30GB+）
- Docker 镜像下载量：约 **70GB**，安装耗时约 30 分钟

更棘手的是，**RTX 5070 / 5090（Blackwell 架构）不受支持**。Issue #624 显示新卡 CUDA kernel 直接报错，Issue #601/#617 也有类似反映，目前官方无回应。如果你刚换了最新一代 NVIDIA 卡，大概率跑不起来。

---

## 「10 秒克隆」说法核查

用户流传最广的描述是「上传 10 秒视频即可克隆」。我在官方 README、文档站（docs.duix.com）和所有 Release Notes 里**找不到任何对应的具体数字**。

README 对训练时长没有量化描述。这个说法可能来自第三方评测视频或早期营销内容，**在官方一手资料中暂无实证**，引用时请注明存疑。

---

## 「本地离线」的真实含义

关于「全离线」——**视频生成本身确实全离线**，所有推理在本地 Docker 容器内跑，官方承诺无需联网。

但 README 里有一句非常关键的自白：

> 本地版：「Usable effect」（**可用效果**）
> 云 API 版：「Stunning and higher definition effect」（**惊艳高清效果**）

这是官方原文的刻意措辞，相当于亲口承认本地效果比云端差一档。Duix 的商业模式是：开源版作引流，核心变现靠 duix.com 云 API 付费套餐。

另外，**实时对话功能**完全需要访问 duix.com 云服务，不能本地运行。

---

## 许可证陷阱：自定义「DUIX.COM Community License」

这是最需要警惕的部分。许可证名称叫「DUIX.COM Community License」，**不是任何 SPDX 标准开源许可证**（SPDX 字段标注的是 `NOASSERTION`）。核心条款：

1. **1,000 MAU 付费门槛**：产品月活达到 1,000 用户就必须申请商业授权，授权与否由 DUIX.COM 单方面决定
2. **强制品牌展示**：网站、界面、文档均须显示「Built with DUIX.COM」
3. **IP 诉讼终止条款**：对 DUIX.COM 提起任何知识产权诉讼，许可即刻终止
4. **永久营销权**：DUIX.COM 获得使用你的实现案例做推广宣传的永久免费权利

还有一个未解决的合规问题：仓库打包分发了 GPL-3.0 的 FFmpeg（含 x264/x265），却套自定义许可证，存在 GPL 合规冲突（Issue #596，**目前无官方回应**）。

---

## 与 Duix-Mobile 的区别

同一组织下还有 **duixcom/Duix-Mobile**（8,255 stars，C++ 语言），但两者定位完全不同：

| | Duix-Avatar | Duix-Mobile |
|--|---|---|
| 定位 | 视频生成工作台 | 实时交互 Avatar SDK |
| 延迟 | 离线批量生成 | <120ms 实时 |
| 平台 | Windows / Ubuntu | iOS/Android/车机/VR/IoT |
| 用途 | 输出视频文件 | 嵌入 App 运行时 |

如果目标是在手机 App 里跑实时数字人，Duix-Mobile 才是对的仓库。

---

## 支持语言

英语、日语、韩语、普通话、法语、德语、阿拉伯语、西班牙语（8 种）。

---

## 关键数字汇总

| 指标 | 数值 |
|------|------|
| Stars | 15,585 |
| Docker 镜像大小 | ~70GB |
| 最低 GPU | NVIDIA RTX 4070 |
| 最低内存 | 32GB RAM |
| 最低存储 | 130GB+ |
| 支持语言数 | 8 种 |
| 最后更新 | 2026-04-21 |
| MAU 商业授权门槛 | 1,000 用户 |

---

## 综合判断

Duix-Avatar 打包了成熟的开源组件（FunASR + Fish-Speech）加自研 C 视频引擎，**工程落地度够高**，本地离线也是真的。但四点硬伤明显：

1. **硬件门槛极高**：RTX 4070 + 32GB RAM，70GB 镜像，不是随手能跑的工具
2. **新显卡不支持**：Blackwell（RTX 50 系）目前全线坑，5 个月没有维护迹象
3. **许可证不是开源**：1,000 MAU 就触发商业授权条款，GPL 冲突未解决
4. **本地效果差一档**：官方自承，如果追求质量还是要付费用云端

适合人群：有闲置 NVIDIA GPU 工作站、想离线预研数字人技术的开发者。不适合：生产部署、移动端、或者对质量有严格要求的场景。

---

> 开源仅供学习，商业使用请仔细核查许可证条款。

---

<!--EN-->

## Duix-Avatar (formerly HeyGem): Local Offline Digital Human Video Cloning — Deep Teardown

> **Open source for learning only**: All projects discussed are from public repositories, analysis is for technical research purposes only.

---

### Project Background

**duixcom/Duix-Avatar** (GitHub: github.com/duixcom/Duix-Avatar) — formerly called **HeyGem**, officially renamed at v1.0.5 (August 2025). Built by Singapore-based company Duix, positioned as a "fully local offline digital human video generation workbench": upload a real video, clone appearance and voice, input a text script, and generate talking-head video offline.

At teardown time: **15,585 stars, 2,652 forks**, 422 open issues. Last push: **2026-04-21** — nearly 5 months without a code update.

---

### Core Three-Component Architecture

Three Docker services form the backbone:

| Service Image | Source | Function |
|--------|--------|---------|
| `guiji2025/fun-asr` | Alibaba FunASR | Speech recognition (ASR) |
| `guiji2025/fish-speech-ziming` | Fish-Speech | Text-to-speech (TTS) |
| `guiji2025/duix.avatar` | Proprietary (C language) | Video synthesis engine |

Three-step pipeline: **appearance cloning** → **voice cloning** → **lip-sync video generation**, chained via local REST APIs (training: `/v1/train`, video synthesis: `127.0.0.1:8383/easy/submit`).

---

### Hardware Requirements

The first barrier. Official requirements:

- **GPU**: NVIDIA RTX 4070 (**NVIDIA only — no AMD or Apple Silicon**)
- **RAM**: 32GB
- **Storage**: 130GB+ (100GB+ on C: drive, 30GB+ data drive)
- Docker image download: ~**70GB**, ~30 minutes to install

Worse: **RTX 5070 / 5090 (Blackwell architecture) are not supported**. Issue #624 shows new cards throw CUDA kernel errors immediately. Issues #601/#617 report the same. No official response as of this writing.

---

### "10-Second Clone" Claim Check

The widely circulated claim is "upload a 10-second video to clone." I found **no corresponding number anywhere in official README, docs.duix.com, or Release Notes**.

The README has no quantified training time. This figure likely originated from third-party review videos or early marketing content — **unverified in official first-party sources**.

---

### What "Local Offline" Actually Means

Video generation itself is genuinely fully offline — all inference runs in local Docker containers, no network required.

But the README contains a telling self-assessment:

> Local version: "Usable effect"
> Cloud API version: "Stunning and higher definition effect"

That's official copy explicitly acknowledging local quality is one tier below cloud. Duix's business model: open-source as lead generation, monetize via duix.com cloud API.

**Real-time conversation** requires duix.com cloud services — not runnable locally.

---

### License Trap: Custom "DUIX.COM Community License"

The license is named "DUIX.COM Community License" — **not any SPDX-standard open-source license** (SPDX field shows `NOASSERTION`). Key clauses:

1. **1,000 MAU commercial trigger**: Once your product reaches 1,000 monthly active users, you must apply for commercial licensing — DUIX.COM decides whether to grant it
2. **Mandatory branding**: Website, UI, and documentation must display "Built with DUIX.COM"
3. **IP litigation termination**: Any IP lawsuit against DUIX.COM immediately terminates your license
4. **Perpetual marketing rights**: DUIX.COM gets perpetual, royalty-free rights to use your implementation as a promotional case study

Unresolved compliance issue: the repo distributes GPL-3.0 FFmpeg (with x264/x265) under a custom license — a GPL compatibility conflict documented in Issue #596 with **no official response**.

---

### Key Metrics Summary

| Metric | Value |
|--------|-------|
| Stars | 15,585 |
| Docker image size | ~70GB |
| Minimum GPU | NVIDIA RTX 4070 |
| Minimum RAM | 32GB |
| Minimum storage | 130GB+ |
| Supported languages | 8 |
| Last push | 2026-04-21 |
| Commercial MAU threshold | 1,000 users |

---

### Verdict

Duix-Avatar packages mature open-source components (FunASR + Fish-Speech) with a proprietary C video engine — solid engineering execution, genuinely offline. But four hard problems:

1. **High hardware barrier**: RTX 4070 + 32GB RAM + 70GB image — not a casual tool
2. **New GPUs unsupported**: Blackwell (RTX 50 series) is broken, no maintenance activity for 5 months
3. **Non-open license**: 1,000 MAU triggers commercial licensing; GPL conflict unresolved
4. **Local quality is one tier below cloud**: Official admission — quality-conscious use cases still need to pay for cloud

Good fit: developers with idle NVIDIA GPU workstations wanting to experiment with local digital human technology. Not suitable: production deployment, mobile, or quality-critical use cases.

---

> Open source for learning only. Check license terms carefully before commercial use.
