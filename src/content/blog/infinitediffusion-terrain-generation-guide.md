---
title: "InfiniteDiffusion：一个人、一张消费级显卡、一篇 SIGGRAPH 2026 顶会论文"
titleEn: "InfiniteDiffusion: One Developer, One Consumer GPU, One SIGGRAPH 2026 Paper"
description: "Alexander Goslin 以独立研究者身份，用 RTX 3090 Ti 发表 SIGGRAPH 2026 论文 InfiniteDiffusion，将扩散模型改造为懒惰采样，实现无界、O(1) 随机访问、确定性的无限地形生成。本文整理复现路径与游戏/工程应用方向。"
descriptionEn: "Alexander Goslin, an independent researcher and Walmart software engineer, published InfiniteDiffusion at SIGGRAPH 2026 using a single RTX 3090 Ti. The algorithm reformulates diffusion sampling as lazy and unbounded generation with O(1) random access and seed-consistency. This is a full reproduction guide and engineering application breakdown."
pubDate: "2026-06-27"
updatedDate: "2026-06-27"
category: "Tech-News"
tags: ["扩散模型", "程序化生成", "游戏开发", "SIGGRAPH", "地形生成", "AI图形", "独立研究"]
heroImage: "../../assets/images/infinitediffusion-terrain-generation-guide-banner.jpg"
---

> **一句话结论（BLUF）**：InfiniteDiffusion 不是新模型，是一个**零训练的采样算法**——把扩散模型的固定画布改成像 Perlin 噪声一样"按需生成任意位置"，同种子确定性，O(1) 随机访问。游戏引擎可以直接当 Perlin 噪声的 AI 升级版来用。

---

## 先说这件事本身有多不寻常

SIGGRAPH 是计算机图形学的顶会，三十多年来能发论文的基本都是 MIT、斯坦福、英伟达研究院、迪士尼实验室这种量级的机构——动辄几十张 A100，或者一个博士团队砸几年时间。

今年（2026）有一篇论文打破了这个规律。

作者叫 **Alexander Goslin**，署名栏只有他一个人，没有第二作者，没有通讯作者，没有导师，单位写的是 **Independent Researcher**（独立研究者）。根据推文信息，他白天是沃尔玛刚入职的初级软件工程师，晚上回家搞研究。显卡是一张 **RTX 3090 Ti**——在 AI 圈已经算不上旗舰了。

他用这张卡做出了一篇 SIGGRAPH 2026 论文，叫 **InfiniteDiffusion**。

---

## 论文在解决什么问题？

过去四十年，游戏和电影里的虚拟地形是靠 **Perlin 噪声**这类程序化算法生成的。它们很快，可以无限扩展，但看起来永远不够真实——山不像山，河不像河。

而扩散模型生成的图像逼真度极高，但一直被困在**固定尺寸的画布**里，没法做无限世界。

他的解决方案是一个**训练免费的算法**：把扩散模型的采样过程改成"懒惰"模式——不一次性画整张图，而是像 Perlin 噪声一样，随时按需生成任意位置的像素。而且是确定性的，同一个种子永远生成同一块地形。随机访问 **O(1) 时间复杂度**。

三个关键属性：

| 属性 | 说明 |
|---|---|
| **无界延伸** | 世界没有边缘，生成到哪算到哪 |
| **种子一致性** | 同坐标同种子永远返回同结果 |
| **O(1) 随机访问** | 加载任意 chunk 不依赖周边已生成内容 |

---

## 原始资源

论文 arXiv：https://arxiv.org/abs/2512.08309

ACM DOI（SIGGRAPH 正式版）：https://doi.org/10.1145/3799902.3811080

GitHub 主仓库：https://github.com/xandergos/terrain-diffusion（618 ⭐）

项目网站：https://xandergos.github.io/terrain-diffusion/

相关库 infinite-tensor：https://github.com/xandergos/infinite-tensor

Minecraft Mod：https://github.com/xandergos/terrain-diffusion-mc

HuggingFace 模型集合：https://huggingface.co/collections/xandergos/terrain-diffusion

---

## 30 分钟复现路径

### Step 0：环境

- Python 3.10+
- NVIDIA GPU（推荐 RTX 3070+，作者用 RTX 3090 Ti）
- 磁盘：模型约 2-4 GB

### Step 1：最小演示——理解算法核心

仓库里有一个 `annotated_infinite_panorama.py`，**自包含、有详细注释**，用 Stable Diffusion v1.5 生成无限宽度全景图，不依赖仓库其他代码：

```bash
git clone https://github.com/xandergos/terrain-diffusion
cd terrain-diffusion

pip install torch diffusers transformers accelerate infinite-tensor pillow numpy

python annotated_infinite_panorama.py
# 输出 output.png（默认 2048px，但实际是无限画布的裁切）
```

文件顶部可调参数：

```python
PROMPT = "photorealistic mountain landscape at sunset"
CROP_PIXEL_WIDTH = 4096   # 任意改，不影响内存消耗
INTERMEDIATE_TIMESTEPS = 5
```

### Step 2：地形生成完整环境

```bash
pip install -r requirements.txt

# CUDA 版（强烈建议）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 3：交互探索世界

```bash
# 游戏级精度（30m/像素，7.7km 粗糙图）
python -m terrain_diffusion explore xandergos/terrain-diffusion-30m

# 现实级精度（90m/像素，23km 范围）
python -m terrain_diffusion explore xandergos/terrain-diffusion-90m
```

左侧点击粗糙地图任意位置 → 右侧实时生成高分辨率地形 + 温度图。

### Step 4：API 模式（对接外部程序）

```bash
python -m terrain_diffusion api xandergos/terrain-diffusion-30m
# 本地 REST API，返回海拔 + 气候 JSON
```

---

## 两个预训练模型怎么选？

| 模型 | 分辨率 | 范围 | 适合场景 |
|---|---|---|---|
| `terrain-diffusion-30m` | 30m/像素 | 7.7km 粗糙图 | 游戏可玩世界——细节丰富，第一/三人称探索 |
| `terrain-diffusion-90m` | 90m/像素 | 23km 范围 | 写实世界构建——大尺度连贯，战略级俯视 |

---

## 工程应用方向

### 方向 A：游戏地形（最直接）

**Minecraft Mod 已经存在**，装完即用，直接替换原版地形生成器：
https://github.com/xandergos/terrain-diffusion-mc

自制游戏接入示例（调用本地 API）：

```python
import requests

def get_chunk_heightmap(chunk_x, chunk_z, seed=42):
    resp = requests.get(
        "http://localhost:8000/elevation",
        params={"x": chunk_x * 16, "z": chunk_z * 16,
                "width": 16, "height": 16, "seed": seed}
    )
    return resp.json()["heightmap"]  # 16x16 高度数组
```

对游戏引擎友好的三点：
- **同 seed 同地形**：玩家重登，世界完全一致
- **O(1) 随机访问**：按需加载 chunk，不需要预生成
- **接口与 Perlin 噪声兼容**：几乎可以直接替换现有管线

### 方向 B：Azgaar 奇幻地图 → 3D 地形

```bash
# 1. Azgaar 网站生成地图，导出完整 JSON
# 2. 转换为地形条件数据
python -m terrain_diffusion azgaar-to-tiff "MyWorld.json" azgaar-output/ --scale 100

# 3. 生成高分辨率 GeoTIFF
python -m terrain_diffusion xandergos/terrain-diffusion-90m tiff-export azgaar-output/ world.tif \
  --snr 0.2,0.2,1.0,0.2,1.0

# 4. 导入 Blender / Unreal / Unity 作 Heightmap
```

适合 RPG 世界设计、DND 地图、小说世界观视觉化。

### 方向 C：飞行 / 驾驶仿真

论文实测：框架速度"超过第一宇宙速度的 9 倍"（约 72km/s 地表覆盖速度），消费级 GPU 实现交互帧率生成。

- 飞行模拟器：飞到哪，地形生成到哪，永远不会飞出地图
- 自动驾驶仿真：无限延伸的道路环境
- 无人机航拍仿真

### 方向 D：算法迁移——超越地形

InfiniteDiffusion 与任务无关，任何扩散模型都可以套：

| 领域 | 应用思路 |
|---|---|
| 无限纹理贴图 | SD 模型生成无缝无限材质（石头、草地、木板）|
| 无限城市布局 | ControlNet 布局条件 + 本算法 → 无限俯视城市图 |
| 无限环境音效 | AudioLDM + 本算法 → 无限流式环境音 |
| GIS / 遥感 | 基于真实 DEM 微调后生成高分辨率地形补全 |

---

## 自己训练（高级）

想要火星地形、外星地形、卡通风格地形：

```bash
# 1. 下载 ETOPO 数据（30 弧秒 GeoTIFF）
#    https://www.ncei.noaa.gov/products/etopo-global-relief-model

# 2. 下载 WorldClim 气候数据（bio 30s）
#    https://www.worldclim.org/data/worldclim21.html

# 3. 放入 data/global/

# 4. 训练粗糙模型（最轻量，单卡可跑）
accelerate launch -m terrain_diffusion train \
  --config ./configs/diffusion_coarse/diffusion_coarse.cfg

# 5. 保存模型
python -m terrain_diffusion.training.save_model \
  -c checkpoints/diffusion_coarse/latest_checkpoint -s 0.05
```

**成本最低改法**：只重训粗糙模型（coarse model，体积很小），精细模型复用预训练权重即可。

---

## 与现有方案对比

| 方案 | 无限延伸 | 视觉逼真度 | 训练成本 | O(1) 随机访问 |
|---|:-:|:-:|:-:|:-:|
| Perlin Noise | ✅ | ❌ 低 | 无 | ✅ |
| 传统扩散模型 | ❌ 有界 | ✅ 极高 | 高 | ❌ |
| MultiDiffusion | 部分 | ✅ | 无 | ❌ 需全局图 |
| **InfiniteDiffusion** | ✅ | ✅ | **零** | ✅ |

---

## 引用

```bibtex
@inproceedings{goslin2026infinitediffusion,
  author    = {Goslin, Alexander},
  title     = {InfiniteDiffusion: Bridging Learned Fidelity and Procedural Utility for Open-World Terrain Generation},
  booktitle = {SIGGRAPH Conference Papers '26},
  year      = {2026},
  doi       = {10.1145/3799902.3811080}
}
```

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: InfiniteDiffusion is not a new model — it's a zero-training sampling algorithm that transforms fixed-canvas diffusion into Perlin-noise-style on-demand pixel generation, with seed-consistency and O(1) random access. For game engines, it's essentially a plug-in AI upgrade to Perlin noise.

---

## Why This Paper Is Unusual

SIGGRAPH is the top venue in computer graphics. For three decades, it has been dominated by MIT, Stanford, NVIDIA Research, and Disney Labs — teams with dozens of A100s or PhD groups working for years.

This year's conference included a paper that broke that pattern entirely.

The author is **Alexander Goslin**. The byline has only his name — no co-authors, no advisor, no institution except **Independent Researcher**. According to his posts, he works as a junior software engineer at Walmart by day and researches at night. His GPU is an **RTX 3090 Ti** — not flagship by AI standards anymore.

He published **InfiniteDiffusion** at SIGGRAPH 2026.

---

## What Problem Does It Solve?

For four decades, virtual terrain in games and films has used **Perlin noise** and similar procedural algorithms: fast, infinite, but fundamentally not photorealistic — mountains that don't look like mountains.

Diffusion models produce stunning visual fidelity, but they're confined to **fixed-size canvases**. You can't build an infinite world with them.

His solution is a **training-free algorithm**: reformulate diffusion sampling as lazy evaluation — instead of generating the whole image at once, compute individual pixels on demand, just like Perlin noise. Deterministic (same seed = same terrain everywhere). **O(1) random access time**.

Three key properties:

| Property | What it means |
|---|---|
| **Seamless infinite extent** | No world boundary — generate wherever you go |
| **Seed-consistency** | Same coordinates + same seed = same result, always |
| **O(1) random access** | Load any chunk without depending on neighbors |

---

## Source Links

Paper (arXiv): https://arxiv.org/abs/2512.08309

ACM DOI (SIGGRAPH official): https://doi.org/10.1145/3799902.3811080

GitHub: https://github.com/xandergos/terrain-diffusion (618 ⭐)

Project site: https://xandergos.github.io/terrain-diffusion/

infinite-tensor library: https://github.com/xandergos/infinite-tensor

Minecraft Mod: https://github.com/xandergos/terrain-diffusion-mc

HuggingFace models: https://huggingface.co/collections/xandergos/terrain-diffusion

---

## Reproduction in 30 Minutes

### Step 1: Minimal demo — understand the algorithm

The repo includes `annotated_infinite_panorama.py`: self-contained, heavily annotated, uses Stable Diffusion v1.5, no dependency on the rest of the codebase:

```bash
git clone https://github.com/xandergos/terrain-diffusion
cd terrain-diffusion
pip install torch diffusers transformers accelerate infinite-tensor pillow numpy
python annotated_infinite_panorama.py
# outputs output.png (2048px crop of an unbounded canvas)
```

Edit constants at the top to experiment: `PROMPT`, `CROP_PIXEL_WIDTH`, `INTERMEDIATE_TIMESTEPS`.

### Step 2: Full terrain environment

```bash
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 3: Interactive world explorer

```bash
python -m terrain_diffusion explore xandergos/terrain-diffusion-30m
```

Click anywhere on the coarse map (left panel) → high-resolution terrain + temperature map generates in real time (right panel).

### Step 4: REST API (for external integration)

```bash
python -m terrain_diffusion api xandergos/terrain-diffusion-30m
# Local REST API returning elevation + climate JSON
```

---

## Engineering Applications

### Game terrain (most direct)

A **Minecraft Fabric Mod already exists**: https://github.com/xandergos/terrain-diffusion-mc — install and it replaces Minecraft's world generator.

For custom engines via the local API:

```python
import requests

def get_chunk_heightmap(chunk_x, chunk_z, seed=42):
    resp = requests.get(
        "http://localhost:8000/elevation",
        params={"x": chunk_x * 16, "z": chunk_z * 16,
                "width": 16, "height": 16, "seed": seed}
    )
    return resp.json()["heightmap"]
```

Engine-friendly properties: same-seed determinism for player saves; O(1) chunk access with no pre-generation; near drop-in replacement for existing Perlin noise pipelines.

### Fantasy map → 3D terrain (Azgaar pipeline)

```bash
python -m terrain_diffusion azgaar-to-tiff "MyWorld.json" azgaar-output/ --scale 100
python -m terrain_diffusion xandergos/terrain-diffusion-90m tiff-export azgaar-output/ world.tif \
  --snr 0.2,0.2,1.0,0.2,1.0
# Import world.tif into Blender / Unreal / Unity as heightmap
```

### Flight and driving simulation

The paper reports terrain generation outpacing orbital velocity 9× on a consumer GPU — meaning realistic terrain streams faster than any vehicle can traverse it. Perfect for flight simulators, autonomous driving sims, and drone simulation.

### Beyond terrain — algorithm transfer

InfiniteDiffusion is task-agnostic. Any diffusion model works:

| Domain | Application |
|---|---|
| Seamless textures | SD-generated infinite tileable materials (rock, grass, wood) |
| Infinite city maps | ControlNet layout conditioning + the algorithm → unbounded aerial city views |
| Ambient audio | AudioLDM + this algorithm → infinite environmental sound streams |
| GIS / remote sensing | Fine-tune on real DEM data → high-resolution terrain completion |

---

## FAQ

**Q: Does it require training a new model?**  
No. InfiniteDiffusion is a training-free sampling algorithm. Drop any compatible diffusion model in and it works. Zero training cost.

**Q: Can it run on a laptop GPU?**  
Yes, though slower. The author used an RTX 3090 Ti for the benchmarks. Smaller GPUs will work; the `annotated_infinite_panorama.py` demo is the lightest entry point.

**Q: Is the terrain geographically realistic?**  
The hierarchical model stack couples real-world geography data (ETOPO elevation, WorldClim climate) at the coarse scale with diffusion fidelity at fine scale. For realistic Earth-like worlds, yes. For fantasy or alien worlds, retrain just the coarse model.

**Q: What's the difference between the 30m and 90m models?**  
`terrain-diffusion-30m` is finer and more controllable — best for playable game worlds. `terrain-diffusion-90m` is more expansive and coherent — best for large-scale worldbuilding where you're looking at the map rather than walking through it.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
