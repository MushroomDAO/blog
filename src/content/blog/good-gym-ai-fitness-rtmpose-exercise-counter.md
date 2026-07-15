---
title: "Good-GYM：用摄像头当教练，开源 AI 实时计数你的每一个动作"
titleEn: "Good-GYM: Open-Source AI Fitness Assistant That Counts Every Rep via Webcam"
description: "基于 RTMPose 的开源健身助手，标准摄像头实时识别人体姿态、自动计数、姿势反馈，支持深蹲/俯卧撑/引体向上等 11 种动作，配置文件就能添加新动作，附 iOS App。"
descriptionEn: "An open-source fitness assistant built on RTMPose that uses a standard webcam to detect body pose in real time, count exercise reps automatically, and provide training feedback — supports 11 exercises, adds new ones via JSON config, includes iOS App."
pubDate: "2026-07-15"
updatedDate: "2026-07-15"
category: "Tech-Experiment"
tags: ["AI", "健身", "RTMPose", "姿态识别", "开源", "计算机视觉", "PyQt5"]
heroImage: "../../assets/images/good-gym-ai-fitness-rtmpose-banner.jpg"
---

健身记录这件事，每个人都嫌麻烦。手动计数容易数乱，穿戴设备要花钱，教练陪练更贵。**Good-GYM** 给了另一条路：只用电脑自带摄像头，AI 实时检测姿态，全程自动帮你数。

## 仓库地址和基本情况

- **GitHub**：[yo-WASSUP/Good-GYM](https://github.com/yo-WASSUP/Good-GYM)（373 ⭐，MIT 协议）
- **iOS App**：[App Store - GoodGYM](https://apps.apple.com/cn/app/goodgym/id6761142874)
- **Windows**：GitHub Releases 提供免安装便携版

Python 写的，依赖 PyQt5 做界面，ONNX Runtime 跑推理，配置了中英双语。**2025 年 6 月的大版本更新放弃了 YOLO 系列，转用 RTMPose**（由 [rtmlib](https://github.com/Tau-J/rtmlib) 提供），模型更轻，CPU 上的速度反而更流畅——因为模型小，GPU 初始化开销有时反而比 CPU 慢，项目明确推荐默认用 CPU。

## 支持的 11 种动作

| 英文 Key | 中文名 | 英文名 |
|---|---|---|
| squat | 深蹲 | Squat |
| pushup | 俯卧撑 | Push-up |
| situp | 仰卧起坐 | Sit-up |
| bicep_curl | 弯举 | Bicep Curl |
| lateral_raise | 侧平举 | Lateral Raise |
| overhead_press | 推举 | Overhead Press |
| leg_raise | 抬腿 | Leg Raise |
| knee_raise | 抬膝 | Knee Raise |
| knee_press | 压膝 | Knee Press |
| crunch | 卷腹 | Crunch |
| pullup | 引体向上 | Pull-up |

## 核心原理：角度阈值 + COCO 17 关键点

RTMPose 输出 COCO 格式的 17 个身体关键点，编号如下（项目里直接用这些索引）：

```
0: 鼻子  1: 左眼  2: 右眼  3: 左耳  4: 右耳
5: 左肩  6: 右肩  7: 左肘  8: 右肘  9: 左腕  10: 右腕
11: 左髋 12: 右髋 13: 左膝 14: 右膝 15: 左踝  16: 右踝
```

每个动作的计数逻辑：取 3 个关键点算夹角（余弦定理），和预设的 `down_angle`（动作底部角度）、`up_angle`（动作顶部角度）比较，一上一下构成一次完整计数。

以深蹲为例，核心逻辑大致是：

```python
# 取左髋(11)、左膝(13)、左踝(15)算膝盖弯曲角度
angle = calc_angle(hip, knee, ankle)
if angle < down_angle:   # 蹲下
    stage = "down"
if angle > up_angle and stage == "down":  # 站起来
    count += 1
    stage = "up"
```

## 数据驱动：改 JSON 就能加新动作

**所有动作定义都在 `data/exercises.json`**，不需要动一行 Python 代码。一个条目的结构是：

```json
{
  "squat": {
    "name_zh": "深蹲",
    "name_en": "Squat",
    "joints": [11, 13, 15],
    "down_angle": 90,
    "up_angle": 160,
    "side": "left"
  }
}
```

- `joints`：3 个关键点索引，对应 COCO 编号
- `down_angle` / `up_angle`：触发计数的角度阈值
- `side`：用哪侧身体检测（有些动作两侧取均值）

想加一个新动作，查一下对应关节的 COCO 索引，测几组动作时的角度范围，填进去就完成了。

## 本地跑起来

```bash
git clone https://github.com/yo-WASSUP/Good-GYM.git
cd Good-GYM

# 推荐用虚拟环境
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

启动后会打开 PyQt5 界面，选动作、点开始、站到摄像头前面就行。界面实时画出骨架、显示当前角度和计数。

**CPU 还是 GPU？** 项目文档明确说：模型很小，CPU 推理已经够快，GPU 反而因为初始化开销更慢，建议默认用 CPU（即默认配置，无需修改）。

## 训练计划和历史记录

除了实时计数，Good-GYM 还有：

- **训练计划**：设定目标组数和次数，AI 自动追踪完成情况
- **历史记录**：保存每次训练数据，看长期进度
- **实时反馈**：姿势偏差时有提示（文字提示；语音交互在 roadmap 但还没上）

## iOS App

如果不想在电脑前练，官方已经有 iOS App——[App Store - GoodGYM](https://apps.apple.com/cn/app/goodgym/id6761142874)，直接手机摄像头运行，界面和桌面版一致，也是中英双语。

## 和商业产品相比

| 维度 | Good-GYM | Apple Watch + Fitness+ | 健身房人工教练 |
|---|---|---|---|
| 成本 | 免费/开源 | 设备 + 订阅费 | 按课收费 |
| 是否需要穿戴 | 不需要 | 需要手表 | 不需要 |
| 可定制动作 | 改 JSON 即可 | 不能 | 依赖教练 |
| 隐私 | 本地推理 | 上传云端 | 无数据问题 |
| 实时骨架可视化 | 有 | 无 | 无 |

## 已知限制和 Roadmap

当前版本的限制：

- 需要正面或侧面对摄像头，遮挡过多会影响关键点检测
- 没有错误姿势的主动纠正（只有提示，没有语音指导）
- 语音交互控制在计划中，还没发布

Roadmap 里提到的方向：动作纠正提示、语音控制、更多动作类型。

## 一句话总结

一个普通摄像头 + RTMPose，在本地实时统计你的动作次数，数据驱动架构让扩展新动作极为简单，MIT 协议完全开源。**想自己折腾健身数据记录的开发者，值得一看。**

© 2026 Author: Mycelium Protocol

<!--EN-->

## Good-GYM: Open-Source AI Fitness Assistant with Pose Detection

**GitHub**: [yo-WASSUP/Good-GYM](https://github.com/yo-WASSUP/Good-GYM) | 373 ⭐ | MIT

Good-GYM is an open-source AI fitness assistant that uses a standard webcam to detect body pose in real time and automatically count exercise reps — no wearable device required.

### Key Switch: RTMPose (Not YOLOv11)

A major June 2025 update dropped YOLO models entirely and migrated to **RTMPose** via [rtmlib](https://github.com/Tau-J/rtmlib). The lighter model performs better on CPU than the prior YOLO-based approach — the project explicitly recommends CPU over GPU because the model is small enough that GPU initialization overhead can actually make it slower.

### Supported Exercises (11)

Squat, Push-up, Sit-up, Bicep Curl, Lateral Raise, Overhead Press, Leg Raise, Knee Raise, Knee Press, Crunch, Pull-up.

### How Rep Counting Works

RTMPose outputs 17 COCO keypoints. For each exercise, three keypoints define a joint (e.g. hip-knee-ankle for squats). The angle at that joint is compared against `down_angle` and `up_angle` thresholds — one complete down→up cycle increments the counter.

### Adding New Exercises — No Code Required

All exercise definitions live in `data/exercises.json`. Each entry specifies:

```json
{
  "my_exercise": {
    "name_zh": "...",
    "name_en": "...",
    "joints": [idx1, idx2, idx3],
    "down_angle": 90,
    "up_angle": 160,
    "side": "left"
  }
}
```

Edit the JSON, restart the app. That's it.

### Quick Start

```bash
git clone https://github.com/yo-WASSUP/Good-GYM.git
cd Good-GYM
pip install -r requirements.txt
python run.py
```

iOS App available on the [App Store](https://apps.apple.com/cn/app/goodgym/id6761142874). Windows portable build on GitHub Releases.

### Bottom Line

A fully local, privacy-respecting, webcam-only exercise counter. The data-driven architecture makes it easy to add custom exercises. MIT licensed. Worth a look if you want to build on top of pose-based fitness tracking.

© 2026 Author: Mycelium Protocol
