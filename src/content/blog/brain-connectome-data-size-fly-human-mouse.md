---
title: "脑子的数据量：从果蝇 20TB 到人脑 1.4PB，我们到底在测量什么"
description: "网上流传「1 毫克脑组织=20TB 信息量」的说法，其实混合了三项不同的连接组研究：果蝇中央脑（2020，20TB+ 原始扫描数据）、人脑颞叶皮层 1 立方毫米（2024，1.4PB）、小鼠视觉皮层 1 立方毫米（2025 MICrONS，1.6PB）。这些 PB 级数字是电镜扫描和三维重建产生的图像数据量，并不等于大脑真正的记忆容量——两者差了好几个数量级，也回答不了同一个问题。"
titleEn: "How Much Data Is a Brain? From a Fly's 20TB to a Human Cortex's 1.4PB"
descriptionEn: "A viral claim says '1mg of brain tissue holds 20TB of information' — but it actually conflates three separate connectome studies: the fly central brain (2020, 20TB+ raw imaging data), 1mm³ of human temporal cortex (2024, 1.4PB), and 1mm³ of mouse visual cortex (2025 MICrONS, 1.6PB). These petabyte figures measure electron-microscope scan and reconstruction data — not the brain's actual memory capacity, which is a wholly different question and a wholly different number."
pubDate: 2026-07-25
updatedDate: 2026-07-25
category: "Research"
tags: ["脑科学", "连接组", "Connectome", "神经科学", "数据量", "果蝇", "MICrONS", "人脑皮层"]
lang: "zh-CN"
heroImage: "../../assets/images/brain-connectome-data-size-fly-human-mouse-banner.jpg"
---

> **内容来源**：本文基于三篇公开发表的连接组研究整理分析——《A connectome and analysis of the adult Drosophila central brain》（*eLife*, 2020）、《A petavoxel fragment of human cerebral cortex reconstructed at nanoscale resolution》（*Science*, 2024，Google Research × 哈佛）、MICrONS 小鼠视觉皮层图谱（Allen Institute 等, 2025）。具体来源见文末参考资源。版权归原作者/机构所有，本文为二次观点整理与科普分析。

---

## 一个流传很广、但拼错了的说法

你可能刷到过这样一句话：**"1 毫克脑组织，储存了 20TB 的信息"**。

这句话很抓耳朵，但仔细一查会发现：它其实是**两三篇不同论文的数字被嫁接在了一起**。真实情况是三项独立研究，测的是三件不同的事：

| 研究对象 | 年份/期刊 | 取样范围 | 数据量 | 神经元/细胞数 | 突触数 |
|---|---|---|---|---|---|
| **果蝇中央脑**（成年果蝇） | 2020, *eLife* | 全脑中央区域 | **超过 20 TB**（原始扫描图像） | 约 2.5 万个 | 超过 2000 万个 |
| **人脑颞叶皮层** | 2024, *Science*（Google Research × 哈佛） | 1 立方毫米（≈1 毫克组织） | **1.4 PB**（约 1400 TB） | 约 5.7 万个细胞 | 约 1.5 亿个 |
| **小鼠视觉皮层**（MICrONS 项目） | 2025, Allen Institute 等 | 1 立方毫米 | **约 1.6 PB** | 超过 20 万个细胞 | 约 5.23 亿个，约 4 公里轴突 |

三行放在一起看，"1 毫克=20TB"这句话立刻站不住脚——**真正对应"1 毫克组织"量级的，其实是 1.4～1.6 PB，比 20TB 高了近两个数量级**。20TB 说的是果蝇整个中央脑（远不止 1 毫克）的扫描数据量。

这不是哪篇论文写错了，而是**流传过程中，不同研究的关键词被剪碎重组**——这本身就很值得聊一聊：科学传播里，"是什么"和"有多大"经常在转述中悄悄互换。

---

## 为什么同样是"脑组织"，数据量能差几百倍？

关键变量是**分辨率**和**取样范围**，两者是跷跷板关系。

- **果蝇研究（2020）**：目标是重建**整个中央脑**的连接图谱，覆盖范围大，但受限于当时的电镜技术和计算能力，分辨率和数据密度相对没有拉满。
- **人脑/鼠脑研究（2024-2025）**：只取了**针尖大小的 1 立方毫米**，但用了纳米级分辨率的电子显微镜，把每一个突触、每一根轴突的三维结构都完整重建出来。取样范围缩小了几十万倍，但单位体积的数据密度暴涨。

打个比方：果蝇研究像用普通像素拍下整座城市的航拍图；人脑/鼠脑研究像用电子显微镜给一粒沙子拍 CT——**范围小了，但精细到原子级别，数据反而爆炸式增长**。

MICrONS 项目的鼠脑数据里，光是神经纤维总长度就有约 **4 公里**——全部压缩进 1 立方毫米的组织里，密度可想而知。

---

## 这些 PB 数据到底是什么，不是什么

这是本文最想说清楚的一点：

**PB 级数据 ≠ 大脑的记忆容量/信息容量。**

它是什么：电子显微镜把组织切成几万张纳米级薄片，逐张拍照、再用算法把这些切片**三维重建**成神经元形状、突触位置、血管走向的数字模型。1.4PB 装的是：

- 原始灰度图像（体素数据，每个立方体像素点的亮度值）
- 分割后的神经元/突触/血管三维网格模型
- 每个结构的标注元数据（类型、连接关系等）

这本质上是一份**极其精细的三维扫描文件**，类似给一块组织做了一次分辨率高到离谱的 CT + 建模，而不是大脑本身"存储"的信息量。就像一张 8K 照片的文件比照片里那朵花实际包含的信息量大得多——**测量工具的精度，不等于被测量对象的信息含量**。

---

## 那大脑真正的"记忆容量"，数量级大概是多少？

这是个完全不同的问题，答案也完全不同。

2016 年，Salk 研究所团队（Bartol 等人）在 *eLife* 发表过一项研究，专门测算突触强度的可辨识状态数——他们发现单个突触大约能区分出 26 种不同的强度等级，对应约 **4.7 bit** 的信息量。以此推算，**整个人脑的信息存储容量大约是 1 petabyte 量级**（当时的新闻标题喜欢说"是此前估计的 10 倍"）。

有意思的地方来了：这个基于"信息论"估算出的人脑记忆容量（约 1PB），和 2024 年人脑连接组研究扫描 1 立方毫米组织产生的数据量（1.4PB）**数量级碰巧接近**——但这纯属巧合，两者算的是完全不同的东西：一个是"整个大脑理论上能编码多少信息"，一个是"给针尖大小的一块组织拍照建模要用多少存储空间"。

如果按同样的扫描精度把**整个人脑**（约 1.2 升）都做一遍连接组重建，数据量会是多少？按 1 立方毫米对应 1.4PB 粗略线性外推——答案是**天文数字级别**，这也是为什么"全脑连接组"至今仍是神经科学最大的工程挑战之一，而不是"存储不够"这么简单的问题（实际瓶颈还包括切片、成像、计算和标注的时间成本）。

---

## 换算一下，这些数字有多大

数字太抽象，换算成日常概念更好感受：

- **1.4 PB** ≈ 你需要大约 **35 万张** 4TB 硬盘，或者连续播放约 **160 年** 的 1080p 高清视频
- **20 TB** ≈ 5 块常见的 4TB 移动硬盘，普通人一两千块钱就能买到
- 按这个密度线性外推，**整个人脑**（约 120 万立方毫米）做同精度连接组重建，数据量会落在 **EB（艾字节，10^18 字节）甚至更高**的量级——相当于当前全球所有数据中心存储总量的相当一部分

这也是为什么"全脑连接组"项目目前都只能从**一立方毫米**起步：不是因为不想做整个大脑，而是数据量和计算成本会随取样体积近乎线性甚至更快地膨胀。

---

## 写在最后

"1 毫克脑组织=20TB"这类说法之所以传得快，是因为它把两个真实但不同的科学发现，用一个更聳动的数字缝在了一起。拆开看，事实反而更有意思：

- 果蝇全脑连接组扫描：20TB+（2020）
- 1 立方毫米人脑/鼠脑连接组扫描：1.4～1.6 PB（2024-2025）
- 人脑理论信息容量估算：约 1PB 量级（2016，另一套完全不同的方法论）

三个数字，三个问题，三种测量方式。它们共同说明的，是神经科学正在从"能不能看清一个神经元"，走向"能不能给一整块脑组织做完整的三维数字孪生"——这件事本身，比任何一个耸动的数字都更值得关注。

---

**参考资源**

- [A connectome and analysis of the adult Drosophila central brain — eLife, 2020](https://elifesciences.org/articles/57443)
- [Ten years of neuroscience at Google yields maps of human brain — Google Research](https://research.google/blog/ten-years-of-neuroscience-at-google-yields-maps-of-human-brain/)
- [谷歌震撼发布纳米级人脑图谱！AI加持人类大脑研究 — BAAI Hub](https://hub.baai.ac.cn/view/37013)
- [Scientists complete largest wiring diagram and functional map of the brain to date — Allen Institute](https://alleninstitute.org/news/scientists-complete-largest-wiring-diagram-and-functional-map-of-the-brain-to-date)
- [他们竟花10年死磕这1立方毫米的组织… — 腾讯新闻](https://news.qq.com/rain/a/20250519A09AD600)

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权。

<!--EN-->

> **TL;DR**: A viral claim — "1mg of brain tissue stores 20TB of information" — turns out to be a mashup of three separate connectome studies. The fly central brain connectome (eLife, 2020) produced 20TB+ of raw electron-microscopy imaging data covering the whole central brain. A 1mm³ fragment of human temporal cortex (Science, 2024, Google Research × Harvard) — roughly 1mg of tissue — produced 1.4PB of data at nanoscale resolution. A 1mm³ fragment of mouse visual cortex (MICrONS, 2025) produced ~1.6PB. The "1mg = 20TB" claim conflates the fly's whole-brain-but-lower-resolution scan with the mammalian studies' tiny-but-nanoscale-resolution scans — the actual 1mg-equivalent number is 1.4-1.6PB, nearly two orders of magnitude higher. More importantly: **none of these petabyte figures measure the brain's actual memory capacity.** They measure the size of the 3D reconstruction file — voxel imagery, segmented neuron/synapse meshes, and metadata — produced by scanning tissue at nanoscale resolution. A 2016 Salk Institute study (Bartol et al., eLife) estimated the brain's actual information-theoretic storage capacity at roughly 1 petabyte, based on ~4.7 bits of distinguishable strength per synapse — a figure that happens to land near the same order of magnitude as the 2024 human cortex scan data, purely by coincidence, since the two numbers answer entirely different questions.

## How Much Data Is a Brain, Really?

| Study | Year/Journal | Sample | Data Size | Cells | Synapses |
|---|---|---|---|---|---|
| Fly central brain | 2020, *eLife* | Whole central brain | **20TB+** (raw scan) | ~25,000 neurons | 20M+ |
| Human temporal cortex | 2024, *Science* | 1mm³ (~1mg) | **1.4PB** | ~57,000 cells | ~150M |
| Mouse visual cortex (MICrONS) | 2025, Allen Institute | 1mm³ | **~1.6PB** | 200,000+ cells | ~523M, ~4km of axon |

**The resolution/coverage tradeoff**: the fly study covered an entire brain region at earlier-generation resolution; the human and mouse studies covered a pinhead-sized volume at nanoscale resolution, reconstructing every synapse and axon in 3D — smaller volume, exponentially denser data.

**What the petabytes actually are**: thousands of nanoscale EM slice images, stitched into 3D voxel data, then segmented into neuron/synapse/blood-vessel meshes with metadata. It's a hyper-precise 3D scan file — not the brain's storage capacity, the same way an 8K photo's file size isn't the amount of information contained in the flower it depicts.

**What the brain's real capacity might be**: ~1 petabyte, per the 2016 Salk Institute synaptic-strength study — a completely different methodology (information theory on synapse states) that coincidentally lands near the same order of magnitude as the 2024 scan data, for unrelated reasons.

**In everyday terms**: 1.4PB ≈ ~350,000 4TB hard drives, or ~160 years of continuous 1080p video. Extrapolating the same resolution to a full human brain (~1.2 liters) would land somewhere in the exabyte range — which is why "whole-brain connectomes" still start at 1mm³, not because storage doesn't exist, but because the cost scales close to linearly (or worse) with sampled volume.

**Sources**: [Drosophila connectome (eLife, 2020)](https://elifesciences.org/articles/57443) · [Google Research blog](https://research.google/blog/ten-years-of-neuroscience-at-google-yields-maps-of-human-brain/) · [Allen Institute / MICrONS](https://alleninstitute.org/news/scientists-complete-largest-wiring-diagram-and-functional-map-of-the-brain-to-date)

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
