---
title: "Anthropic MHS：AI 正式接管物理世界——开源硬件的下一个机会在哪里"
titleEn: "Anthropic MHS: AI Takes Over the Physical World — Where Open Hardware Fits In"
description: "Anthropic 发布模型硬件标准（MHS）研究预览，统一 AI Agent 操控实体设备的接口层，已接入 Genentech/CMU/QuEra/LeRobot/树莓派。分析开源硬件接入 MHS 的工程路径与优先项目。"
descriptionEn: "Anthropic's Model Hardware Standard (MHS) research preview unifies how AI agents operate physical devices. Analysis of MHS architecture, early results from Genentech/CMU/QuEra, and engineering guidance for open hardware teams wanting to build MHS-compatible projects."
pubDate: 2026-08-30
updatedDate: 2026-08-30
category: "Research"
tags: ["Anthropic", "MHS", "robotics", "open hardware", "AI agent", "Claude", "lab automation", "physical AI"]
heroImage: "../../assets/images/anthropic-mhs-model-hardware-standard-ai-agents-physical-devices-open-hardware-banner.jpg"
author: "Mycelium Protocol"
---

## 这件事比"AI 写代码"重要得多

2026 年 8 月 27 日，Anthropic 发布了**模型硬件标准（MHS，Model Hardware Standard）**的研究预览第一阶段。

这不是一个新模型，也不是一个新 API。它是一套**让 AI Agent 安全、标准化地操控物理设备的通用接口规范**。机械臂、显微镜、液体处理器、3D 打印机、激光器、量子计算机——任何有可编程接口的设备，都可以通过 MHS 被 AI Agent 发现、理解、操控。

如果说 MCP（Model Context Protocol）解决的是"AI 怎么连软件工具"，MHS 解决的是"AI 怎么连物理世界"。

> MHS 将实验室/工厂的集成时间从数周缩短到数小时，甚至几分钟。

---

## MHS 的工作原理：一套"物理世界的 MCP"

### 核心架构：标准化驱动层

MHS 的本质是一个**标准化驱动程序（Driver）**，它在 AI Agent 和物理设备之间架起一座桥：

```
AI Agent（Claude / 任意模型）
       ↓ MCP / CLI / Code Files
   MHS Driver（标准化层）
       ↓ 设备原生接口
 物理设备（显微镜/机械臂/液体处理器...）
```

**三层设计**：

1. **原语层（Primitives）**：所有设备只需理解两种操作——`read`（如"读取当前温度"）和 `write`（如"设置目标温度 37°C"）。极简，但足够。

2. **设备发现层（Discoverability）**：每个设备以标准格式注册，可以跨网络被 Agent 自动发现，不需要人工写"翻译器"。

3. **语义标注层（Natural Language Tags）**：驱动中嵌入自然语言标注，描述设备的物理特性（重量、安全限制、操作范围……），这些信息原来只存在于纸质手册里。Agent 首次使用一台从没见过的设备时，通过这些标注自动理解如何安全操控它。

**三种控制机制**：
- **MCP**：与 Claude 直接对话控制设备
- **CLI**：命令行调用，适合脚本集成
- **Code Files（API）**：把多步操作打包成代码文件，让设备自主执行长流程，无需 Agent 在每步之间推理（激光对准、连续采样等）

**模型无关**：MHS 通过标准协议（MCP）暴露接口，任何 Agent 框架都可以接入，不绑定 Claude。

---

## 早期实验结果：已经很惊人

### Genentech：蛋白质浓度测定自动化

协调液体处理器、机械臂、酶标仪三台设备，完成 BCA 蛋白质浓度测定实验。Claude 自主优化液体流速参数——水 ≈ 140 µL/s，粘性 BSA 蛋白溶液 ≈ 10 µL/s——并能在遇到液体处理错误时自主恢复，无需人工介入。**以前需要自动化专家手写每组参数，现在 Claude 自己跑闭环优化**。

### 卡内基梅隆大学：串行稀释实验速度提升 3×

CMU 用 MHS 协调液体处理器、酶标仪、机械臂和监控摄像头——跨三台有根本不兼容接口的计算机——把剂量响应曲线实验速度提升到原来的约 3 倍。

### QuEra Computing：量子计算机激光稳定

QuEra 把 MHS 引入量子计算机的激光系统。AI Agent 开发了一个控制器，在无人干预的情况下将激光"锁频"（原子量子计算中激光必须维持的超精确频率）的恢复成功率达到 **99.3%**。

### 华盛顿大学 Baker 实验室

用 MHS 构建了远程仪器监控仪表盘、AI 监督的 qPCR（在正确时刻自动停止），以及机械臂与液体处理器的无碰撞板件交接。

---

## 现状：研究预览阶段，即将开源

**重要信息**：MHS 目前处于**受邀研究预览**阶段，尚未开源。官方网站 [modelhardwarestandard.com](https://www.modelhardwarestandard.com/) 开放申请，主要面向科研机构和先进制造商。

**已加入的合作方**（包括设备厂商和软件平台）：

| 合作方 | 内容 |
|---|---|
| **HuggingFace LeRobot** ⭐27,051 | 机器人 AI 库，**已在 LeRobot 中添加 MHS 支持** |
| **Raspberry Pi** | 多款产品加入 MHS 集成，Camera MHS Driver 已测试成功 |
| **AWS Strands Robots** | 连接 AI Agent 与物理设备的库，将通过 MHS 提供支持 |
| Doosan Robotics | 工业机械臂，测试 MHS 质量检测与多机协调 |
| Tecan | 液体处理平台 Fluent |
| Universal Robots | 协作机器人平台 |
| Danaher | 智能仪器与自主实验室 |

**开源时间表**：Anthropic 表示将在研究预览结束后开源 MHS，并同步发布安全评估报告和部署指南。

---

## 对开源硬件的意义：工程分析

用户的问题是：**如果做开源硬件，能否基于 MHS 做出有价值的项目？**

答案是**可以，而且时机很好**。原因和工程路径如下。

### 为什么现在是时机

1. **LeRobot + MHS 已经是开源的入口**：HuggingFace 的 LeRobot（⭐27,051）已经在添加 MHS 支持。这意味着开源机器人硬件项目可以直接在这个生态里落地。

2. **树莓派是第一个被点名的开源硬件平台**：Raspberry Pi 不是选项，是已经在做的事——Camera MHS Driver 已经测试成功。这验证了廉价单板计算机类硬件完全适合 MHS 驱动开发。

3. **MHS 准备开源**：提前参与研究预览、开发驱动、积累社区，比开源后再入场有先发优势。

4. **标准规范本身极简**：`read`/`write` + 自然语言标注。实现一个新设备的 MHS 驱动，工程量远低于传统 ROS 节点或定制 SDK。

---

### 适合开源硬件的 MHS 项目类型

**前提条件**：设备必须有**可编程接口**（串口、USB HID、GPIO、以太网均可）。只要能用代码发送指令、读取数据，就能做 MHS 驱动。

#### 项目优先级评估

**★★★ 高优先级——入门快、影响大**

**1. 树莓派多传感器站（Environmental Sensor Hub）**

```
硬件：Raspberry Pi 5 + 温度/pH/DO/光照传感器阵列
MHS Driver：read_temperature / read_pH / set_pump_speed
用途：水质监测、植物培养、环境科研
工程量：1-2 周
```
树莓派已在 MHS 名单上，社区基础最强。多传感器融合是科研实验室最常见的痛点，MHS 让 Agent 能够自动解读多维数据并调节参数。

**2. SO-ARM100 低成本机械臂 + LeRobot + MHS**

```
硬件：SO-ARM100（约 $100，开源设计）或 Koch v1.1
MHS Driver：move_joint / get_joint_angle / set_gripper
用途：LeRobot 数据采集、桌面物体操作、实验室样品处理
工程量：2-3 周
```
LeRobot 已添加 MHS 支持，SO-ARM100 是 LeRobot 官方支持的廉价开源机械臂。这是当前生态里最直接的切入点。

**3. OpenFlexure 显微镜 + MHS Driver**

```
硬件：OpenFlexure Microscope（3D 打印，约 $50-200）
MHS Driver：set_focus / set_illumination / capture_image / move_stage
用途：微生物学、材料检测、教育科研
工程量：2-4 周
```
OpenFlexure 是最成熟的开源科研显微镜，有完整的 Python API，做 MHS 驱动只需一个薄适配层。MBF Bioscience 正在给 ScanImage（商业激光扫描显微镜软件）做 MHS 驱动，验证了显微镜这个方向。

**★★ 中优先级——技术难度略高**

**4. 低成本液体处理器（Syringe Pump Array）**

```
硬件：步进电机 + 注射器（Poseidon 开源设计，约 $100-300）
MHS Driver：aspirate(volume) / dispense(volume) / set_flow_rate
用途：化学实验、药物稀释、PCR 准备
工程量：3-5 周
```
Genentech 案例直接证明液体处理是 MHS 的核心场景。Poseidon 是 MIT 媒体实验室开源的注射泵设计，已有完整 CAD 和固件。

**5. 开源光谱仪（DIY Spectrometer）**

```
硬件：线性 CCD + USB 接口（Public Lab / SpectralWorkbench 系列）
MHS Driver：capture_spectrum / set_integration_time / calibrate
用途：水质检测、化学分析、环境监测
工程量：2-4 周
```

---

### MHS 驱动开发：工程指南

一个 MHS 驱动的最小结构大致如下（具体 schema 待官方开源后确认，以下为基于公开信息的工程推断）：

```python
# MHS Driver 伪结构（基于公开信息推断）
class MyDeviceDriver:
    # 设备元数据（自然语言标注）
    metadata = {
        "name": "OpenFlexure Microscope v6",
        "description": "3D-printed open-source microscope with motorized stage",
        "weight_kg": 0.8,
        "safety_limits": {
            "max_illumination_mW": 50,
            "stage_travel_mm": {"x": 24, "y": 24, "z": 8}
        },
        "capabilities": ["brightfield imaging", "focus control", "XYZ positioning"],
        "programming_interface": "USB-serial via Python API"
    }
    
    # MHS 原语：read
    def read(self, parameter: str) -> dict:
        if parameter == "focus_position":
            return {"value": self.scope.get_position()["z"], "unit": "steps"}
        if parameter == "image":
            return {"data": self.scope.capture()}
    
    # MHS 原语：write
    def write(self, parameter: str, value) -> dict:
        if parameter == "focus_position":
            self.scope.move({"z": value})
            return {"status": "ok"}
        if parameter == "illumination":
            assert value <= self.metadata["safety_limits"]["max_illumination_mW"]
            self.scope.set_illumination(value)
```

**关键工程点**：

1. **安全限制必须硬编码**，不能依赖 Agent 自己判断。电流上限、行程边界、温度阈值——这些放在驱动里，不是在 prompt 里。

2. **自然语言标注越详细越好**。Agent 首次使用设备时，这些标注是它唯一的"使用手册"。重量、材质约束、操作时序、常见故障模式——都写进去。

3. **状态反馈要实时**。Agent 需要观察结果来决定下一步（QuEra 激光对准、Genentech 流速优化都是闭环的）。驱动要能流式返回设备状态。

4. **把长流程打包成 Code Files**。不要让 Agent 在每个微步骤之间都推理。把"完成一次对焦"这种有固定步骤的操作封装成代码文件，Agent 调用一次就够了。

---

### 一个可以立刻开始的最小项目

如果现在就想动手，最低门槛的切入点：

```bash
# 1. 申请 MHS 研究预览（可以同时开始下面的工作）
# https://www.modelhardwarestandard.com/

# 2. 在 LeRobot 生态里开始
git clone https://github.com/huggingface/lerobot
# 关注 LeRobot 的 MHS 支持 PR/branch

# 3. 用树莓派做一个最简 MHS-ready 传感器驱动
# - 任意 USB/GPIO 传感器
# - 实现 read(parameter) / write(parameter, value) 两个方法
# - 写好自然语言 metadata
# - 通过 MCP 暴露给 Claude

# 4. 测试闭环：让 Claude 通过 MCP 读取传感器，
#    根据读数调节某个执行器（风扇、泵、加热器）
```

这个最小项目能验证整个 MHS 闭环，不需要等 MHS 正式开源。

---

## 局限与风险

**AI 空间推理的现实局限**：Genentech 案例明确指出——Claude 不理解气泡的物理成因（液体起泡导致检测失败），只会重试而不是物理修复。**AI 在物理直觉方面仍需要人类专家监督**，尤其是首次部署时。

**商业授权在发布时确定**：MHS 尚未开源，具体 License 未知。LeRobot（Apache 2.0）是已知安全的开源层。

**公共 DERP 中继类比**：MHS 的公共 DERP 服务（如果有）在正式开源前属于研究性基础设施，生产部署应该自建。

---

## 总结

MHS 是 Anthropic 在"让 AI 更有用"这个方向上最实质性的一步——它不是让 AI 更聪明，而是给 AI 配上了手和眼睛。对开源硬件社区来说，这是一个比"又一个 AI 框架"重要得多的信号：**物理设备即将成为 AI Agent 的原生公民**。

最值得关注的切入点：SO-ARM100 + LeRobot（最低成本机器人）、OpenFlexure + MHS Driver（开源显微镜）、树莓派多传感器站（最低门槛验证）。与其等 MHS 正式开源，不如现在就基于 LeRobot 生态开始，用 MCP 搭建 MHS-ready 的设备驱动原型。

**官方公告**: [anthropic.com/news/model-hardware-standard-research-preview](https://www.anthropic.com/news/model-hardware-standard-research-preview)  
**申请研究预览**: [modelhardwarestandard.com](https://www.modelhardwarestandard.com/)  
**LeRobot（已添加 MHS 支持）**: [github.com/huggingface/lerobot](https://github.com/huggingface/lerobot) ⭐27,051

<!--EN-->

## Anthropic MHS: AI Takes Over the Physical World — Engineering Guide for Open Hardware

On August 27, 2026, Anthropic launched the research preview of the **Model Hardware Standard (MHS)** — a shared specification for AI agents to safely operate physical devices including robotic arms, microscopes, liquid handlers, 3D printers, and lasers.

If MCP (Model Context Protocol) solved "how AI connects to software tools," MHS solves "how AI connects to the physical world." Any device with a programmable interface can be discovered, understood, and operated by an AI agent through MHS.

> MHS reduces device integration time from weeks to hours or minutes.

### How MHS Works

MHS introduces a standardized driver layer between AI agents and physical hardware:

```
AI Agent (Claude / any model)
       ↓ MCP / CLI / Code Files
   MHS Driver (standardization layer)
       ↓ device-native interface
Physical Device (microscope/robot arm/liquid handler...)
```

**Three-layer design**:

1. **Primitives**: Every device only needs to understand two operations — `read` (e.g., "get temperature") and `write` (e.g., "set temperature 37°C"). Minimal, but sufficient.

2. **Device discoverability**: Each device registers in a standard format and can be auto-discovered by agents across a network — no bespoke translator programs.

3. **Natural language tags**: Drivers embed natural language descriptions of physical characteristics (weight, safety limits, operating ranges). Information previously buried in paper manuals is now machine-readable. An agent encountering an unfamiliar device reads these tags to understand how to operate it safely.

**Three control mechanisms**: MCP (for direct Claude interaction), CLI (for scripting), and Code Files (packaged multi-step sequences the device executes autonomously without per-step agent reasoning).

**Model-agnostic**: MHS exposes its interface via standard protocols like MCP; any agent framework can access it.

### Early Results

**Genentech**: BCA protein assay automation across liquid handler + robotic arm + plate reader. Claude autonomously optimized liquid flow rates in a closed loop (water ≈ 140 µL/s, viscous BSA ≈ 10 µL/s) and recovered from hardware errors without intervention — work that previously required an automation specialist writing custom code for each parameter set.

**Carnegie Mellon**: Dose-response experiments ~3× faster, coordinating four devices across three computers with fundamentally incompatible interfaces.

**QuEra Computing**: AI agent recovers quantum laser "lock" (the ultra-precise frequency neutral-atom quantum computers require) **99.3% of the time** without human intervention.

**University of Washington Baker lab**: Remote instrument dashboard, AI-supervised qPCR that halts at the right amplification moment, and collision-free plate handoffs between robotic arm and liquid handler.

### Current Status: Research Preview, Soon Open Source

MHS is currently in **invited research preview** — not yet open source. Apply at [modelhardwarestandard.com](https://www.modelhardwarestandard.com/).

**Notable open-source adopters already committed**:
- **HuggingFace LeRobot** ⭐27,051 — adding MHS support (Apache 2.0)
- **Raspberry Pi** — MHS integration across products, Camera MHS Driver already tested
- AWS Strands Robots, Doosan Robotics, Tecan, Universal Robots (hardware vendors)

### Engineering Guidance for Open Hardware Teams

**Can open hardware teams build MHS-compatible projects now?** Yes, and the timing is good.

**Why now**: LeRobot already has MHS support coming (the highest-starred open robotics library). Raspberry Pi is already named as an MHS platform. The standard itself is minimally complex — `read`/`write` primitives + natural language tags. Building an MHS driver for a new device is far less work than writing a custom ROS node.

**Priority projects by feasibility**:

**★★★ High priority — fast to build, high impact**

1. **Raspberry Pi multi-sensor station** (temp/pH/dissolved oxygen): Hardware cost under $100, largest community base, directly validates the MHS environment monitoring use case. 1-2 weeks of engineering.

2. **SO-ARM100 + LeRobot + MHS**: SO-ARM100 is an open-source ~$100 robot arm officially supported by LeRobot. With LeRobot adding MHS support, this is the most direct on-ramp. 2-3 weeks.

3. **OpenFlexure microscope + MHS driver**: 3D-printed open-source microscope ($50-200), complete Python API already exists. An MHS driver is a thin adapter layer. MBF Bioscience building a commercial microscope MHS driver validates the direction. 2-4 weeks.

**★★ Medium priority**

4. **Open-source syringe pump array** (Poseidon design): The Genentech case directly proves liquid handling is a core MHS use case. MIT's open-source Poseidon pump has CAD and firmware. 3-5 weeks.

5. **DIY USB spectrometer**: USB-interfaced CCD spectrometer, water quality / chemical analysis use case.

**Minimum viable MHS driver structure**:

```python
class MyDeviceDriver:
    metadata = {
        "name": "OpenFlexure Microscope v6",
        "description": "3D-printed open-source microscope",
        "weight_kg": 0.8,
        "safety_limits": {"max_illumination_mW": 50},
        "capabilities": ["brightfield imaging", "focus control", "XYZ positioning"]
    }
    
    def read(self, parameter: str) -> dict:
        if parameter == "focus_position":
            return {"value": self.scope.get_position()["z"], "unit": "steps"}
    
    def write(self, parameter: str, value) -> dict:
        if parameter == "illumination":
            assert value <= self.metadata["safety_limits"]["max_illumination_mW"]
            self.scope.set_illumination(value)
            return {"status": "ok"}
```

**Key engineering rules**:

1. **Hard-code safety limits in the driver** — never rely on the agent to enforce current/temperature/force limits
2. **Make natural language metadata as rich as possible** — it is the device's only "manual" for a first-time agent
3. **Stream real-time state** — closed-loop AI control (like QuEra's laser alignment, Genentech's flow rate optimization) requires continuous feedback
4. **Package long procedures as Code Files** — don't force per-step agent reasoning; wrap deterministic sequences so the device runs autonomously

**The minimum viable experiment you can start today**:

```bash
# Clone LeRobot (MHS support in progress)
git clone https://github.com/huggingface/lerobot

# Or: build an MHS-ready Raspberry Pi sensor driver
# Implement read(parameter) / write(parameter, value)
# Write rich natural language metadata
# Expose via MCP to Claude
# Test closed loop: Claude reads sensor, adjusts actuator (fan/pump/heater)
```

### Caveats

- **AI spatial/physical reasoning has real limits**: Genentech found Claude didn't understand bubble physics (it kept retrying instead of physically correcting). Expert human oversight is still required, especially on first deployment
- **MHS license TBD**: Not yet open source; LeRobot (Apache 2.0) is the safe open-source layer to build on now
- **Research preview infrastructure**: Treat public MHS relays/services as experimental; production deployments should self-host

### Summary

MHS is Anthropic's most consequential step toward useful AI — not making the model smarter, but giving it hands and eyes. Physical devices are becoming first-class AI agent citizens.

Best open hardware entry points: SO-ARM100 + LeRobot (lowest-cost robot), OpenFlexure + MHS driver (open microscope), Raspberry Pi sensor station (lowest friction validation). Rather than waiting for MHS to open-source, start building MHS-ready device drivers via LeRobot's ecosystem and MCP today.

**Official announcement**: [anthropic.com/news/model-hardware-standard-research-preview](https://www.anthropic.com/news/model-hardware-standard-research-preview)  
**Apply for preview**: [modelhardwarestandard.com](https://www.modelhardwarestandard.com/)  
**LeRobot (MHS support added)**: [github.com/huggingface/lerobot](https://github.com/huggingface/lerobot) ⭐27,051
