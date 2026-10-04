---
title: "aigccat：文字到 Unity/Godot 的自托管 3D 游戏资产管线，工程拆解"
titleEn: "aigccat: Self-Hosted AI 3D Game Asset Pipeline from Text to Unity/Godot — Engineering Teardown"
description: "RainNameless/aigccat，Apache-2.0，35 stars，JavaScript。自托管 AI 3D 游戏资产管线，11 工具工作台：文字/图片输入 → AI 生成纹理 → Remesh 优化 → UV 展开 → AI 骨骼绑定（Blender 脚本）→ 101 套动画模板 → 导出 GLB → 直接对接 Unity/Godot。三态版本管理（latest/approved/published）、多账号池、MinIO 存储、Docker 一键部署、成本台账和预算熔断机制。AI 骨骼绑定通过 Blender 脚本桥接 OpenCode，在容器内执行。"
descriptionEn: "RainNameless/aigccat, Apache-2.0, 35 stars, JavaScript. Self-hosted AI 3D game asset pipeline with an 11-tool workbench: text/image → AI texture → remesh → UV unwrap → AI rigging (Blender scripts) → 101 animation templates → GLB export → Unity/Godot import. Three-state version control (latest/approved/published), multi-account pool, MinIO storage, Docker one-click deploy, cost ledger + budget circuit breaker. AI rigging bridges to OpenCode via Blender scripts running inside the container."
pubDate: 2026-10-04
heroImage: "../../assets/images/aigccat-3d-game-asset-pipeline-ai-unity-godot-banner.jpg"
category: "Tech-Experiment"
tags: ["3D建模", "游戏开发", "Unity", "Godot", "AI生图", "自托管", "开源工具"]
lang: "zh-CN"
wechatTitle: "aigccat：文字到Unity/Godot的3D资产管线"
wechatDigest: "Apache-2.0；自托管3D管线；文字/图→GLB→Unity/Godot；三态版本管理+成本熔断"
---

3D 游戏资产的生产链条很长：生成纹理 → 优化网格 → 展 UV → 绑骨架 → 套动画 → 导出兼容格式 → 对接引擎。每一步都有专门工具，但把它们串起来、还能追踪成本、管控质量，一般要手动协调。

aigccat 把这条流水线做成了一个自托管工作台，11 个工具工位，Docker 一键跑起来。

GitHub: https://github.com/RainNameless/aigccat | ⭐ 35 | Apache-2.0 | JavaScript

---

## 管线总览

```
文字 / 图片输入
    ↓
AI 生成纹理（调 AI 图像 API）
    ↓
Remesh 网格优化（减面 + 补洞）
    ↓
UV 自动展开
    ↓
AI 骨骼绑定（Blender 脚本 + OpenCode 桥接，容器内执行）
    ↓
101 套动画模板（Walk/Run/Jump/Attack 等标准动作）
    ↓
GLB 导出
    ↓
Unity / Godot 工程对接
```

整个流程不需要手动在 Blender 里操作，骨骼绑定和动画通过容器内的脚本自动跑。

---

## 11 个工作台工具

工作台把每一步独立成一个工具，可以单独跑也可以组成流水线：

1. **文本生成器**：自然语言描述 → 触发 AI 图像生成
2. **图片上传器**：本地图片 → 进入管线
3. **纹理生成**：调 AI 图像 API，生成目标对象的 PBR 纹理
4. **Remesh 优化**：网格减面、补洞、重拓扑
5. **UV 展开**：自动 UV 映射
6. **骨骼绑定**：Blender 脚本 + OpenCode，AI 确定关节位置
7. **动画绑定**：101 套预制动画模板匹配骨骼
8. **材质编辑器**：调整 PBR 材质参数
9. **预览渲染**：实时 3D 预览
10. **GLB 导出**：标准格式，Unity/Godot 直接导入
11. **成本台账**：每次操作记录 AI API 调用成本

---

## 三态版本管理

资产有三个状态，防止未经审核的内容直接进入生产：

| 状态 | 含义 |
|------|------|
| `latest` | 最新生成，未审核 |
| `approved` | 人工或自动审核通过 |
| `published` | 已发布到 Unity/Godot 工程 |

只有 `approved` 状态的资产才能推进到 `published`，避免 AI 生成质量不达标的内容混进正式资产库。版本历史保留，可以回滚到任意之前的 `approved` 状态。

---

## 多账号池与成本熔断

**多账号池**：可以配置多个 AI 服务账号（图像生成 API、OpenCode 账号等），工作台按策略轮换调用，避免单账号限速影响流水线。

**成本台账**：每次 AI API 调用记录消耗，按资产、按时间段统计。

**预算熔断**：设定单资产预算上限和每日总预算。超出时自动停止 AI 调用，不会无声地烧超预算。

```json
// 配置示例
{
  "budget": {
    "per_asset_limit": 2.00,
    "daily_limit": 50.00,
    "on_exceed": "pause"
  }
}
```

---

## AI 骨骼绑定：OpenCode 桥接

骨骼绑定是最难自动化的一步。aigccat 的做法：

1. 容器里装 Blender（headless 模式）
2. Python 脚本读取网格，提取顶点分布
3. 顶点信息发给 OpenCode（容器内），让 AI 分析关节位置
4. Blender 脚本根据 AI 返回的关节方案执行骨骼创建和权重绑定
5. 绑定结果写入文件，进入下一步动画匹配

这个设计把 AI 判断（关节在哪）和确定性执行（Blender 操作）分开——AI 只做决策，Blender 脚本保证操作可复现。

**局限**：复杂有机体（非标准人形、多足生物、软体结构）效果不稳定，人形角色最可靠。

---

## 存储与部署

**MinIO**：S3 兼容的本地对象存储，保存所有资产文件、版本历史和中间产物。不需要云存储账号，数据在本地。

**Docker 部署**：

```bash
git clone https://github.com/RainNameless/aigccat.git
cd aigccat
cp .env.example .env
# 填写 AI API keys、MinIO 配置
docker compose up -d
```

默认端口 3000，MinIO Console 9001。首次启动会拉 Blender 镜像，总大小约 8–12GB（含 Blender + Python 依赖）。

**系统要求**：16GB+ RAM 推荐（Blender headless 跑大网格时吃内存），8核+ CPU。GPU 可选（用于加速某些 AI 推理步骤）。

---

## Unity / Godot 对接

导出的 GLB 文件通过工作台的导出面板直接推到配置的工程目录，或者手动复制。GLB 是通用格式，两个引擎都原生支持。

Unity 端会自动识别骨骼层级和动画剪辑（前提是骨骼命名符合 Unity Humanoid 标准——aigccat 骨骼绑定默认用标准命名）。

Godot 4.x 对 GLB 的支持更原生，导入后动画自动识别为 AnimationPlayer 节点。

---

## 适合谁用

**适合**：
- 独立游戏开发者，需要快速生成大量 NPC / 道具资产
- 小型游戏工作室，想把 AI 生成流程标准化、可追溯
- 想在本地跑完整 3D AI 资产流水线、不想数据上云的团队

**不适合**：
- 需要高精度角色动画（AAA 游戏级别）——AI 骨骼绑定对复杂角色精度有限
- 没有服务器资源运行 Docker 的场景

**当前状态**：35 stars，早期项目，API 可能变化。骨骼绑定是最活跃开发的部分，非标准形体效果需要实测。

---

> Apache-2.0 开源，商业使用无限制。骨骼绑定效果因模型复杂度而异。开源仅供学习参考。

---

<!--EN-->

## aigccat: Self-Hosted AI 3D Game Asset Pipeline — Engineering Teardown

The 3D game asset production chain is long: generate textures → optimize mesh → UV unwrap → rig → animate → export → import into engine. Every step has dedicated tools, but wiring them together with cost tracking and quality gates usually requires manual coordination.

aigccat packages this pipeline into a self-hosted workbench — 11 tool stations, one Docker command to bring it up.

GitHub: https://github.com/RainNameless/aigccat | ⭐ 35 | Apache-2.0 | JavaScript

---

### Pipeline Overview

```
Text / image input
    ↓
AI texture generation (AI image API)
    ↓
Remesh optimization (decimation + hole filling)
    ↓
Automatic UV unwrap
    ↓
AI rigging (Blender scripts + OpenCode bridge, runs inside container)
    ↓
101 animation templates (Walk/Run/Jump/Attack + more)
    ↓
GLB export
    ↓
Unity / Godot import
```

No manual Blender operations required — rigging and animation run via scripts inside the container.

---

### 11 Workbench Tools

Each pipeline stage is a discrete tool that can run standalone or as part of the pipeline:

1. **Text generator**: natural language description → triggers AI image generation
2. **Image uploader**: local images → pipeline entry
3. **Texture generation**: AI image API, produces PBR textures for the target object
4. **Remesh optimizer**: decimation, hole filling, retopology
5. **UV unwrap**: automatic UV mapping
6. **Rigging**: Blender scripts + OpenCode — AI determines joint positions
7. **Animation binding**: 101 pre-built animation templates matched to the skeleton
8. **Material editor**: adjust PBR material parameters
9. **Preview renderer**: real-time 3D preview
10. **GLB export**: standard format, direct Unity/Godot import
11. **Cost ledger**: tracks AI API spend per operation

---

### Three-State Version Control

Assets flow through three states to keep unreviewed work out of production:

| State | Meaning |
|-------|---------|
| `latest` | Freshly generated, unreviewed |
| `approved` | Passed manual or automated review |
| `published` | Deployed to Unity/Godot project |

Only `approved` assets can advance to `published`. Version history is retained — rollback to any previous `approved` state is supported.

---

### Multi-Account Pool and Budget Circuit Breaker

**Multi-account pool**: configure multiple AI service accounts (image generation APIs, OpenCode accounts). The workbench rotates across them by policy to avoid single-account rate limits blocking the pipeline.

**Cost ledger**: records every AI API call, aggregated per asset and per time period.

**Budget circuit breaker**: set per-asset and daily budget caps. When exceeded, AI calls pause automatically — no silent overruns.

---

### AI Rigging: OpenCode Bridge

Rigging is the hardest step to automate. aigccat's approach:

1. Blender runs headless inside the container
2. Python scripts extract mesh vertex distributions
3. Vertex data is sent to OpenCode (also in-container) for joint position analysis
4. Blender scripts execute skeleton creation and weight binding from the AI's joint plan
5. The bound mesh advances to animation matching

The design separates AI judgment (where are the joints?) from deterministic execution (Blender operations) — AI decides, Blender scripts ensure reproducibility.

**Constraint**: complex organic meshes (non-standard humanoids, multi-limbed creatures, soft-body structures) produce inconsistent results. Standard humanoids work most reliably.

---

### Storage and Deployment

**MinIO**: S3-compatible local object storage for all assets, version history, and intermediates. No cloud storage account needed.

**Docker deployment:**

```bash
git clone https://github.com/RainNameless/aigccat.git
cd aigccat
cp .env.example .env
# fill in AI API keys, MinIO config
docker compose up -d
```

Default port 3000, MinIO Console at 9001. First launch pulls the Blender image — total ~8–12GB.

**System requirements**: 16GB+ RAM recommended (Blender headless on large meshes is memory-heavy), 8+ CPU cores. GPU optional.

---

### Unity / Godot Integration

Exported GLB files can be pushed directly to a configured project directory via the export panel, or copied manually. Both engines natively support GLB.

Unity auto-detects the skeleton hierarchy and animation clips when bone naming follows the Unity Humanoid standard — which aigccat's rigging uses by default.

Godot 4.x has more native GLB support; imported assets automatically expose animations as AnimationPlayer nodes.

---

### Who Should Use It

**Good fit**: indie game developers who need to produce many NPC/prop assets quickly; small studios wanting a standardized, auditable AI asset pipeline; teams that want the full 3D AI pipeline running locally without cloud data exposure.

**Not ideal**: AAA-quality character animation requirements (AI rigging accuracy has limits); environments without server resources to run Docker.

**Current state**: 35 stars, early-stage project. API may change. Rigging is the most actively developed part — test on your target mesh complexity before committing.

---

> Apache-2.0, no commercial restrictions. Rigging quality varies by mesh complexity. For technical reference only.
