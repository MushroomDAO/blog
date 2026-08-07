---
title: "UniFace：把人脸分析全套能力统一到一个 Python API"
titleEn: "yakhyo-uniface-python-face-analysis-unified-library"
description: "yakhyo 开源的 Python 人脸分析统一库，944 stars。单一 API 覆盖：检测（RetinaFace/SCRFD/YOLOv8-Face）、识别（ArcFace/AdaFace）、追踪（BYTETracker）、106/468 点关键点、语义分割、人像抠图（MODNet）、注视估计、头部姿态、属性分析（年龄/性别/情绪）、活体检测、质量评估，支持 Apple Silicon / CUDA / CPU，模型自动下载。"
descriptionEn: "yakhyo's open-source unified Python face analysis library, 944 stars. Single API covering: detection (RetinaFace/SCRFD/YOLOv8-Face), recognition (ArcFace/AdaFace), tracking (BYTETracker), 106/468-point landmarks, semantic segmentation, portrait matting (MODNet), gaze estimation, head pose, attributes (age/gender/emotion), anti-spoofing, and quality assessment. Supports Apple Silicon / CUDA / CPU with auto model downloads."
pubDate: "2026-08-07"
updatedDate: "2026-08-07"
category: "Tech-News"
tags: ["人脸分析", "Python", "计算机视觉", "ONNX Runtime", "人脸识别", "ArcFace", "Mycelium"]
heroImage: "../../assets/images/yakhyo-uniface-python-face-analysis-unified-library-banner.jpg"
---

*by Mycelium Protocol*

---

人脸分析任务在工程实践中长期面临一个碎片化问题：检测用一个库，识别用另一个，关键点还要第三个，各库之间的数据格式不兼容，版本冲突难以管理，部署时要集成多个不同的模型推理管道。

UniFace 把这些全部装进一个 Python 包，用统一 API 调用。

GitHub: https://github.com/yakhyo/uniface | ⭐ 944 | MIT License

---

## 覆盖的能力清单

| 功能 | 支持的模型/方法 |
|------|----------------|
| **人脸检测** | RetinaFace, SCRFD, CenterFace, YOLOv5-Face, YOLOv8-Face（5 点关键点）；BlazeFace/MediaPipe（6 点关键点） |
| **人脸识别** | AdaFace, ArcFace, EdgeFace, MobileFace, SphereFace — 人脸 embedding 提取 |
| **人脸追踪** | BYTETracker — 跨帧持久 ID，适用于视频流 |
| **面部关键点** | 106 点（2d106det）；98/68 点（PIPNet）；468/478 点密集 3D 网格（MediaPipe Face Mesh，478 版含虹膜） |
| **面部分割/解析** | BiSeNet 语义分割（19 类）；XSeg 面部掩膜 |
| **人像抠图** | MODNet — 无 trimap 透明度预测，可直出透明背景 PNG 或绿幕合成 |
| **注视估计** | MobileGaze — 实时眼球注视方向 |
| **头部姿态** | 6D 旋转表示，输出 pitch/yaw/roll |
| **属性分析** | FairFace（年龄/性别/种族）；情绪识别；眼睛开合/眼镜/口罩状态（FaceAttribNet） |
| **向量存储** | FAISS 向量库，支持多人身份快速检索 |
| **活体检测** | MiniFASNet — 防照片/视频欺诈 |
| **质量评估** | eDifFIQA — 单分质量评分（NIST FATE-Quality 2024 第一名，L 变体） |
| **人脸匿名化** | 5 种模糊方式，用于隐私保护 |
| **硬件加速** | ARM64（Apple Silicon M 系列）/ CUDA（NVIDIA）/ CPU |

---

## 安装

```bash
# CPU / Apple Silicon
pip install uniface[cpu]

# NVIDIA GPU
pip install uniface[gpu]
```

`onnxruntime` 和 `onnxruntime-gpu` 共享同一个 Python 命名空间，不能同时安装——这是 UniFace 用 extras 分开的原因，安装时选一个即可，不会产生冲突。

**从源码安装（最新版）：**

```bash
git clone https://github.com/yakhyo/uniface.git
cd uniface && pip install -e ".[cpu]"   # 或 .[gpu]
```

**可选：FAISS 向量存储**

```bash
pip install faiss-cpu   # 或 faiss-gpu
```

**注意：** 情绪模型基于 TorchScript，需要额外安装 `torch`；YOLOv5/v8-Face 使用更快的 NMS 需要 `torchvision`。

**模型自动下载**：首次使用时自动从网络下载对应模型并做 SHA-256 校验，缓存到 `~/.uniface/models`。可通过 API 或环境变量修改缓存路径：

```python
from uniface.model_store import set_cache_dir
set_cache_dir('/data/models')
# 或
# export UNIFACE_CACHE_DIR=/data/models
```

---

## 代码示例

**单功能：人脸检测**

```python
import cv2
from uniface.detection import RetinaFace

detector = RetinaFace()
image = cv2.imread("photo.jpg")
faces = detector.detect(image)

for face in faces:
    print(f"置信度: {face.confidence:.2f}")
    print(f"边界框: {face.bbox}")
    print(f"关键点: {face.landmarks.shape}")
```

**全功能：FaceAnalyzer（零配置）**

```python
import cv2
from uniface import FaceAnalyzer

# 默认：SCRFD 检测 + ArcFace MobileNet 识别
analyzer = FaceAnalyzer()
image = cv2.imread("photo.jpg")
faces = analyzer.analyze(image)

for face in faces:
    print(face.bbox, face.embedding.shape)
```

**带属性分析：**

```python
from uniface import FaceAnalyzer, AgeGender

analyzer = FaceAnalyzer(predictors=[AgeGender()])
faces = analyzer.analyze(image)

for face in faces:
    print(f"{face.sex}, {face.age}岁")
```

**人像抠图 → 透明背景 PNG：**

```python
import cv2
import numpy as np
from uniface.matting import MODNet

matting = MODNet()
image = cv2.imread("portrait.jpg")
matte = matting.predict(image)  # (H, W) float32，值在 [0, 1]

rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = (matte * 255).astype(np.uint8)
cv2.imwrite("transparent.png", rgba)
```

---

## 设计原则

**统一数据结构**：所有模块返回的 `Face` 对象包含 `bbox`、`confidence`、`landmarks`、`embedding` 等字段，不同检测器的结果格式一致，切换模型不需要修改下游代码。

**ONNX Runtime 为推理后端**：不依赖 PyTorch/TensorFlow 做推理（情绪模型是例外），减少了依赖体积和版本冲突风险，同时天然支持多硬件后端。

**生产就绪**：CI 持续运行，PyPI 发布，有完整文档站（yakhyo.github.io/uniface），适合直接集成到业务管道。

---

## 适用场景

- **安防/监控**：多人追踪 + 活体检测 + 人脸识别
- **内容审核**：人脸质量过滤 + 匿名化处理
- **身份验证**：ArcFace embedding + FAISS 快速检索
- **AR/特效**：468 点密集 3D 关键点 + 头部姿态
- **人像处理**：MODNet 抠图 + 背景替换

---

*Mycelium Protocol — 追踪 AI 系统的底层演化*

---

> **关于 Mycelium**
>
> 菌丝协议。持续追踪 AI 工具、系统和实验的内容节点。

---

<!--EN-->

## UniFace: A Single Python API for the Full Face Analysis Stack

*by Mycelium Protocol*

---

Face analysis in production has a persistent fragmentation problem: one library for detection, another for recognition, a third for landmarks. Data formats between libraries don't align, version conflicts accumulate, and deployment requires integrating multiple model inference pipelines.

UniFace puts all of this into a single Python package with a unified API.

GitHub: https://github.com/yakhyo/uniface | ⭐ 944 | MIT License

---

### What's Covered

| Feature | Models / Methods |
|---------|-----------------|
| **Face Detection** | RetinaFace, SCRFD, CenterFace, YOLOv5-Face, YOLOv8-Face (5-point landmarks); BlazeFace/MediaPipe (6-point) |
| **Face Recognition** | AdaFace, ArcFace, EdgeFace, MobileFace, SphereFace — face embedding extraction |
| **Face Tracking** | BYTETracker — persistent IDs across video frames |
| **Facial Landmarks** | 106-point (2d106det); 98/68-point (PIPNet); 468/478-point dense 3D mesh (MediaPipe Face Mesh, 478 adds irises) |
| **Face Parsing/Segmentation** | BiSeNet semantic segmentation (19 classes); XSeg face masking |
| **Portrait Matting** | MODNet — trimap-free alpha matte, transparent PNG or green screen output |
| **Gaze Estimation** | MobileGaze — real-time gaze direction |
| **Head Pose** | 6D rotation representation, outputs pitch/yaw/roll |
| **Attribute Analysis** | FairFace (age/gender/race); emotion; eye openness/glasses/mask state (FaceAttribNet) |
| **Vector Store** | FAISS-backed, fast multi-identity search |
| **Anti-Spoofing** | MiniFASNet — photo/video spoof detection |
| **Quality Assessment** | eDifFIQA — single-score quality (NIST FATE-Quality 2024 #1, L variant) |
| **Anonymization** | 5 blur methods for privacy protection |
| **Hardware** | ARM64 (Apple Silicon M-series) / CUDA (NVIDIA) / CPU |

---

### Installation

```bash
# CPU / Apple Silicon
pip install uniface[cpu]

# NVIDIA GPU
pip install uniface[gpu]
```

`onnxruntime` and `onnxruntime-gpu` share the same Python namespace and can't coexist — that's why UniFace uses extras to separate them. Pick one, no conflict.

**From source:**

```bash
git clone https://github.com/yakhyo/uniface.git
cd uniface && pip install -e ".[cpu]"   # or .[gpu]
```

**Models auto-download** on first use, verified by SHA-256, cached to `~/.uniface/models`. Override:

```python
from uniface.model_store import set_cache_dir
set_cache_dir('/data/models')
```

---

### Code Examples

**Detection only:**

```python
import cv2
from uniface.detection import RetinaFace

detector = RetinaFace()
image = cv2.imread("photo.jpg")
faces = detector.detect(image)

for face in faces:
    print(f"Confidence: {face.confidence:.2f}, BBox: {face.bbox}")
```

**Full analysis (zero config):**

```python
from uniface import FaceAnalyzer

# Default: SCRFD detection + ArcFace MobileNet recognition
analyzer = FaceAnalyzer()
faces = analyzer.analyze(cv2.imread("photo.jpg"))
```

**With attribute predictors:**

```python
from uniface import FaceAnalyzer, AgeGender

analyzer = FaceAnalyzer(predictors=[AgeGender()])
faces = analyzer.analyze(image)
for face in faces:
    print(f"{face.sex}, {face.age}y")
```

**Portrait matting → transparent PNG:**

```python
from uniface.matting import MODNet
import numpy as np

matting = MODNet()
matte = matting.predict(image)   # float32 (H, W), values in [0, 1]

rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
rgba[:, :, 3] = (matte * 255).astype(np.uint8)
cv2.imwrite("transparent.png", rgba)
```

---

### Design Principles

**Unified data structures**: all modules return `Face` objects with consistent fields (`bbox`, `confidence`, `landmarks`, `embedding`). Switching detectors doesn't require changes to downstream code.

**ONNX Runtime as inference backend**: no PyTorch/TensorFlow dependency for inference (emotion model is the exception), reducing package size and version conflict risk while natively supporting multiple hardware targets.

**Production-ready**: continuous CI, PyPI releases, complete documentation site (yakhyo.github.io/uniface).

---

### Use Cases

- **Security/surveillance**: multi-person tracking + liveness detection + face recognition
- **Content moderation**: quality filtering + anonymization
- **Identity verification**: ArcFace embeddings + FAISS fast retrieval
- **AR/effects**: 468-point dense 3D landmarks + head pose
- **Portrait processing**: MODNet matting + background replacement

---

*Mycelium Protocol — tracking the deep evolution of AI systems*

© 2026 Mycelium Protocol. All rights reserved.
