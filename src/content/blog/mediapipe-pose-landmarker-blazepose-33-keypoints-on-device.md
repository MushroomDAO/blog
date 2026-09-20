---
title: "MediaPipe Pose Landmarker：BlazePose 33 个关键点，跑在设备上"
titleEn: "MediaPipe Pose Landmarker: BlazePose 33 Keypoints, Runs On-Device"
description: "你搜到的 google.github.io/mediapipe/solutions/pose.html 是旧 API，已于 2023 年 3 月废弃。现行版本是 google-ai-edge/mediapipe v1.0.0（37K stars，Apache-2.0），走 Tasks API，支持 Python/JS/Android/iOS，推理全在设备端。本文把两代 API 对比清楚，给出今天能直接跑的代码。"
descriptionEn: "The google.github.io/mediapipe/solutions/pose.html URL you found is the old Legacy API, deprecated March 2023. The current version is google-ai-edge/mediapipe v1.0.0 (37K stars, Apache-2.0), using the Tasks API, supporting Python/JS/Android/iOS with fully on-device inference. This article clarifies both APIs and provides code you can run today."
pubDate: 2026-09-20
category: "Tech-Experiment"
tags: ["mediapipe", "pose-estimation", "computer-vision", "blazepose", "on-device-ml", "google"]
lang: zh-CN
heroImage: "../../assets/images/mediapipe-pose-landmarker-blazepose-33-keypoints-on-device-banner.jpg"
---

先说链接的问题。

`google.github.io/mediapipe/solutions/pose.html` 是 MediaPipe 的**旧版文档**，对应的是 Legacy API——`mediapipe.solutions.pose`。这套 API 已于 2023 年 3 月正式废弃，代码库继续开放、预编译包继续分发，但不再维护。

如果你现在新建项目，要用的是 **Tasks API**，入口是 `mediapipe.tasks.vision.PoseLandmarker`。

---

## 仓库现状

MediaPipe 主仓库已从 `google/mediapipe` 迁移到 **`google-ai-edge/mediapipe`**，旧地址会自动跳转。截至发稿，37,006 stars，Apache-2.0 协议，C++ 实现，最新版本 **v1.0.0**（2026-07-28 发布）。

```
github.com/google-ai-edge/mediapipe
```

---

## BlazePose 是什么

MediaPipe Pose 底层是 **BlazePose**，Google Research 在 2020 年发表的实时人体姿态估计模型，采用两阶段 Detector-Tracker 流水线：

1. **Detector**：在帧内定位人体 ROI（Region of Interest）。找到之后就锁定，后续帧只跑 Tracker，除非人体消失。
2. **Tracker**：在 ROI 内预测 33 个关键点坐标 + 可见度评分。

这个设计的好处是帧间开销低——Detector 只在首帧和重定位时跑，大多数帧只跑轻量 Tracker。

---

## 33 个关键点

输出固定 33 个关键点，覆盖从头顶到脚趾的全身主要关节：

| 编号 | 部位 | 编号 | 部位 |
|------|------|------|------|
| 0 | 鼻子 | 11–12 | 左/右肩 |
| 1–4 | 左眼内/外 + 右眼内/外 | 13–14 | 左/右肘 |
| 5–6 | 左/右耳 | 15–16 | 左/右腕 |
| 7–10 | 嘴角 + 耳廓 | 23–24 | 左/右髋 |
| 17–22 | 手指关键点（拇指/食指/小指尖）| 25–32 | 膝/踝/脚跟/趾尖 |

每个关键点返回：
- `x`, `y`：图像归一化坐标（0–1）
- `z`：相对于髋部中点的深度估计（相对值）
- `visibility`：该点是否可见的置信度（0–1）
- `presence`：该点是否在帧内的置信度（0–1）

Tasks API 还输出**世界坐标系**版本（单位：米，以髋部为原点），适合计算关节角度和骨骼长度。

---

## 三个模型变体

| 模型 | 文件名 | 精度 | 速度 | 适用场景 |
|------|--------|------|------|---------|
| Lite | `pose_landmarker_lite.task` | 较低 | 最快 | 资源受限设备、实时应用 |
| Full | `pose_landmarker_full.task` | 中等 | 适中 | 大多数场景的默认选择 |
| Heavy | `pose_landmarker_heavy.task` | 最高 | 最慢 | 精度优先、离线分析 |

所有模型均可从 Google Storage 下载，也可以通过 Python 包自动拉取。

---

## Tasks API：Python 用法

安装：

```bash
pip install mediapipe
```

**图片模式**（单张图片）：

```python
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_full.task"
)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False
)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    image = mp.Image.create_from_file("photo.jpg")
    result = landmarker.detect(image)

    for idx, pose_landmarks in enumerate(result.pose_landmarks):
        print(f"人物 {idx}：")
        for i, landmark in enumerate(pose_landmarks):
            print(f"  关键点 {i}: x={landmark.x:.3f}, y={landmark.y:.3f}, "
                  f"z={landmark.z:.3f}, vis={landmark.visibility:.3f}")
```

**实时流模式**（摄像头）：

```python
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions
import cv2
import time

def result_callback(result, output_image, timestamp_ms):
    if result.pose_landmarks:
        # 处理每帧结果
        for pose_landmarks in result.pose_landmarks:
            pass  # 在这里画骨骼或做分析

base_options = BaseOptions(model_asset_path="pose_landmarker_full.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback,
    num_poses=1
)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, timestamp_ms)
```

`running_mode` 三个值：
- `IMAGE`：单张图片，同步
- `VIDEO`：视频文件，同步，需要传入时间戳
- `LIVE_STREAM`：摄像头实时，异步回调

---

## Tasks API：JavaScript / Web

CDN 或 npm 安装：

```bash
npm install @mediapipe/tasks-vision
```

```javascript
import { PoseLandmarker, FilesetResolver, DrawingUtils } from "@mediapipe/tasks-vision";

const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
);

const poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
        modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task",
        delegate: "GPU"  // 或 "CPU"
    },
    runningMode: "VIDEO",
    numPoses: 1
});

// 每帧调用
const result = poseLandmarker.detectForVideo(videoElement, performance.now());
const drawingUtils = new DrawingUtils(canvasCtx);
for (const landmark of result.landmarks) {
    drawingUtils.drawLandmarks(landmark);
    drawingUtils.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
}
```

推理完全在浏览器内运行，WebGL 或 WASM 后端，无需后端服务器。

---

## 旧 Legacy API 对应关系

如果你在老代码里看到这种写法：

```python
# Legacy API（已废弃，勿用于新项目）
import mediapipe as mp
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
results = pose.process(frame_rgb)
```

对应的 Tasks API 迁移：

| Legacy | Tasks API |
|--------|-----------|
| `mp.solutions.pose.Pose()` | `vision.PoseLandmarker.create_from_options(options)` |
| `results.pose_landmarks` | `result.pose_landmarks[0]`（第一个人） |
| `results.pose_world_landmarks` | `result.pose_world_landmarks[0]` |
| `mp.solutions.drawing_utils.draw_landmarks` | `DrawingUtils.drawLandmarks()` |

主要变化：Tasks API 明确支持**多人**（`num_poses` 参数），输出是 list；Legacy API 只支持单人。

---

## 应用场景

- **健身动作识别**：检测深蹲、俯卧撑等动作是否标准
- **体态分析**：实时检测驼背、头前倾等不良姿势
- **手语识别**：结合手部关键点（HandLandmarker）做手语翻译
- **舞蹈/动作捕捉**：低成本动捕方案，无需专用硬件
- **AR 试衣**：在虚拟换装应用中对齐服装到人体

---

## 几点限制

- **单目 z 轴不可靠**：深度估计是从单目图像推算的，z 值是相对值，不适合做精确3D重建。
- **遮挡处理有限**：部分遮挡的关键点仍会输出但 visibility 会变低，不会自动填补缺失。
- **Heavy 模型实时性差**：在端侧设备（手机、树莓派）上 Heavy 模型通常无法保证实时。
- **非 SMPL 格式**：输出的是稀疏 33 点关键点，不是 SMPL/SMPL-X 格式的完整参数化人体模型，不能直接导入 Blender 做绑定。
- **多人场景 Detector 负担增加**：`num_poses > 1` 时，每次都需要 Detector 全图扫描，帧率下降明显。

---

## 参考资料

Tasks API 文档：ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker  
GitHub：github.com/google-ai-edge/mediapipe  
代码示例：github.com/googlesamples/mediapipe（mediapipe-samples 仓库）

> 开源代码仅供学习研究，生产部署请注意 model 和 data 的隐私条款（MediaPipe Tasks 有设备端处理声明）。

---

**仓库**：github.com/google-ai-edge/mediapipe  
**版本**：v1.0.0 | **Stars**：37,006 | **License**：Apache-2.0

<!--EN-->

First, a note about the link.

`google.github.io/mediapipe/solutions/pose.html` is the **old documentation** for the Legacy API — `mediapipe.solutions.pose`. This API was officially deprecated in March 2023. The codebase remains open and prebuilt binaries continue to be distributed, but it's no longer maintained.

If you're building something new, you want the **Tasks API**: `mediapipe.tasks.vision.PoseLandmarker`.

---

## Repository status

The MediaPipe repository has migrated from `google/mediapipe` to **`google-ai-edge/mediapipe`** — the old URL redirects automatically. At time of writing: 37,006 stars, Apache-2.0 license, C++ implementation, latest release **v1.0.0** (published 2026-07-28).

```
github.com/google-ai-edge/mediapipe
```

---

## What BlazePose is

MediaPipe Pose uses **BlazePose**, a real-time body pose estimation model published by Google Research in 2020. It uses a two-stage Detector-Tracker pipeline:

1. **Detector**: locates the person's ROI (Region of Interest) within the frame. Once found, the ROI is locked for subsequent frames — the Detector only re-runs if the person disappears.
2. **Tracker**: predicts 33 keypoint coordinates and visibility scores within the ROI.

The design keeps per-frame cost low: the Detector runs only on the first frame and on re-localization; most frames only run the lightweight Tracker.

---

## 33 keypoints

The output is always 33 fixed keypoints covering major joints from head to toes:

| Index | Landmark | Index | Landmark |
|-------|----------|-------|----------|
| 0 | Nose | 11–12 | Left/right shoulder |
| 1–4 | Left/right eye inner/outer | 13–14 | Left/right elbow |
| 5–6 | Left/right ear | 15–16 | Left/right wrist |
| 7–10 | Mouth corners + ear tragion | 23–24 | Left/right hip |
| 17–22 | Fingertip keypoints | 25–32 | Knee/ankle/heel/toe tip |

Each keypoint returns:
- `x`, `y`: normalized image coordinates (0–1)
- `z`: depth relative to the hip midpoint (relative units)
- `visibility`: confidence that the point is visible (0–1)
- `presence`: confidence that the point is within the frame (0–1)

The Tasks API also outputs **world coordinates** (meters, origin at hip midpoint) — useful for computing joint angles and bone lengths.

---

## Three model variants

| Model | Filename | Accuracy | Speed | Use case |
|-------|----------|----------|-------|---------|
| Lite | `pose_landmarker_lite.task` | Lower | Fastest | Resource-constrained devices, real-time |
| Full | `pose_landmarker_full.task` | Medium | Moderate | Default for most scenarios |
| Heavy | `pose_landmarker_heavy.task` | Highest | Slowest | Accuracy-first, offline analysis |

All models can be downloaded from Google Storage or pulled automatically via the Python package.

---

## Tasks API: Python

Install:

```bash
pip install mediapipe
```

**Image mode** (single image):

```python
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(
    model_asset_path="pose_landmarker_full.task"
)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False
)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    image = mp.Image.create_from_file("photo.jpg")
    result = landmarker.detect(image)

    for idx, pose_landmarks in enumerate(result.pose_landmarks):
        print(f"Person {idx}:")
        for i, landmark in enumerate(pose_landmarks):
            print(f"  Keypoint {i}: x={landmark.x:.3f}, y={landmark.y:.3f}, "
                  f"z={landmark.z:.3f}, vis={landmark.visibility:.3f}")
```

**Live stream mode** (webcam):

```python
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions
import cv2, time

def result_callback(result, output_image, timestamp_ms):
    if result.pose_landmarks:
        for pose_landmarks in result.pose_landmarks:
            pass  # draw skeleton or run analysis here

base_options = BaseOptions(model_asset_path="pose_landmarker_full.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback,
    num_poses=1
)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        landmarker.detect_async(mp_image, int(time.time() * 1000))
```

Three `running_mode` values:
- `IMAGE`: single image, synchronous
- `VIDEO`: video file, synchronous, pass timestamp
- `LIVE_STREAM`: webcam, async callback

---

## Tasks API: JavaScript / Web

```bash
npm install @mediapipe/tasks-vision
```

```javascript
import { PoseLandmarker, FilesetResolver, DrawingUtils } from "@mediapipe/tasks-vision";

const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
);

const poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
        modelAssetPath: "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task",
        delegate: "GPU"
    },
    runningMode: "VIDEO",
    numPoses: 1
});

const result = poseLandmarker.detectForVideo(videoElement, performance.now());
const drawingUtils = new DrawingUtils(canvasCtx);
for (const landmark of result.landmarks) {
    drawingUtils.drawLandmarks(landmark);
    drawingUtils.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
}
```

Inference runs entirely in the browser — WebGL or WASM backend, no server needed.

---

## Legacy → Tasks API migration

If you see old code:

```python
# Legacy API (deprecated — don't use for new projects)
import mediapipe as mp
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
results = pose.process(frame_rgb)
```

Migration guide:

| Legacy | Tasks API |
|--------|-----------|
| `mp.solutions.pose.Pose()` | `vision.PoseLandmarker.create_from_options(options)` |
| `results.pose_landmarks` | `result.pose_landmarks[0]` (first person) |
| `results.pose_world_landmarks` | `result.pose_world_landmarks[0]` |
| `mp.solutions.drawing_utils.draw_landmarks` | `DrawingUtils.drawLandmarks()` |

Main difference: Tasks API explicitly supports **multiple people** (`num_poses` parameter); results are a list. Legacy API only supported one person.

---

## Key limitations

- **Monocular z-axis is unreliable**: depth is estimated from a single image — z values are relative, not suitable for accurate 3D reconstruction.
- **Limited occlusion handling**: partially occluded keypoints still output but with lower visibility scores — missing points aren't auto-filled.
- **Heavy model isn't real-time on edge devices**: phones and Raspberry Pi typically can't maintain real-time throughput with the Heavy model.
- **Not SMPL format**: the output is 33 sparse keypoints, not a parameterized body model like SMPL/SMPL-X — can't be directly imported into Blender for rigging.
- **Multi-person performance drops**: `num_poses > 1` requires a full-frame Detector scan every time, significantly reducing frame rate.

---

**Repository**: github.com/google-ai-edge/mediapipe  
**Version**: v1.0.0 | **Stars**: 37,006 | **License**: Apache-2.0  
**Docs**: ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker  
**Samples**: github.com/googlesamples/mediapipe
