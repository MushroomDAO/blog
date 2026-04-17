# R01 硬件调研报告：中国市场本地 AI 部署方案

> 调研日期：2026-04-17 | 数据有效期：2026 Q2 | 状态：✅ 完成

---

## 一、手机端（Mobile Tier）

### 主流芯片 AI 能力对比

| 芯片 | 代表机型 | NPU 算力 | 可运行模型 | 推荐 RAM |
|------|---------|---------|-----------|---------|
| Apple A17/A18 | iPhone 15 Pro / 16 | 16核神经引擎 | Qwen2.5 1.5B、Llama3.2 3B | 8GB→3B；12GB→7B |
| Snapdragon 8 Gen 3 | 小米14 Pro、一加12 | 50+ TOPS | Llama3.2 3B（~10 tok/s）、Qwen3 4B | 12GB 推荐 |
| Dimensity 9300 | vivo Pad3 Pro | 全大核架构 | Llama3.2 3B（安卓最强） | 12GB+ 推荐 |

**关键结论：**
- Q4_K_M 量化的 Llama3.2 3B 在 Snapdragon 8 Elite 上可达 ~10 tok/s，交互流畅
- Dimensity 9300 因全大核架构，性能优于同代 Snapdragon
- RAM 门槛：8GB→1.5B-3B；12GB→3B-7B；16GB+→7B全量

**推荐 App：**
- iOS：PocketPal、LLM Farm
- Android：WhisperInput、SpeechNote、MNN LLM

**中国市场价格：** ¥3,500–8,000（12GB+ 旗舰机型）

---

## 二、PC/笔记本端（Personal PC Tier）

### 平台对比

| 平台 | 芯片 | 可用显存 | 适合模型 | 参考价（RMB） |
|------|------|---------|---------|-------------|
| Apple Silicon M2 | M2 | 8/16/32GB 统一内存 | 7B（16GB）、14B（32GB） | ~¥12,000 |
| Apple Silicon M3 | M3 | 8/16/32GB 统一内存 | 14-22B（32GB） | ~¥14,000 |
| Apple Silicon M4 | M4 | 16/32/64GB 统一内存 | 22B-70B（64GB） | ~¥18,000+ |
| Intel Core Ultra | 155H | 32/64GB DDR5 + 48 TOPS NPU | 14B-22B | ¥12,000–15,000 |
| AMD Ryzen AI | AI 300 系 | 32/64GB DDR5 + 50 TOPS NPU | 14B-22B | ¥10,000–14,000 |

**Apple Silicon 统一内存注意：** 70-75% 可用于模型权重。32GB M3 实际可用 ~24GB 跑模型。

### 独立显卡（中国可购买清单）

| 显卡 | 显存 | 中国价格 | 状态 | 适合模型 |
|------|------|---------|------|---------|
| RTX 5090 D V2 | 24GB GDDR7 | ¥16,499 | ✅ 官方在售（限量） | 70B Q4 |
| RTX 4070 | 12GB | ~¥4,599 | ✅ 可购 | 13B Q4 |
| RTX 4060 Ti | 16GB | ~¥2,999 | ✅ 可购 | 13B Q4 |
| RTX 4090 | 24GB | 灰市溢价 | ⚠️ 禁止出口，灰市高价 | 70B Q4 |
| RTX 3090（二手） | 24GB | ~¥5,000 | ✅ 二手市场 | 70B Q4，性价比最高 |
| RTX 3060（二手） | 12GB | ~¥1,300–1,600 | ✅ 入门首选 | 13B Q4 |

**显存对应模型规模：**
- 8GB VRAM → 7B Q4（约 4-5GB）
- 12GB VRAM → 13B Q4（约 8-9GB）
- 16GB VRAM → 13B FP16 / 22B Q4
- 24GB VRAM → 34B Q4 / 70B Q2

**推荐工具：** MLX（Apple Silicon 专用，快 10-20%）/ Ollama（通用，更易用）

---

## 三、社区端（Community Server，2-20人小团队）

### 推荐方案

| 设备 | CPU | 内存 | AI 能力 | 推荐度 | 价格（RMB） |
|------|-----|------|---------|--------|------------|
| **Mac Mini M4** | M4 | 24/48GB 统一内存 | 70B 模型（48GB） | ⭐⭐⭐⭐⭐ | ¥4,999–7,499 |
| **Mac Mini M4 Pro** | M4 Pro | 24/48/64GB | 70B+ 流畅运行 | ⭐⭐⭐⭐⭐ | ¥7,499–8,000 |
| Intel NUC 14 Pro AI | Core Ultra 7 | 32/64GB DDR5 | 14B-22B | ⭐⭐⭐⭐ | ¥8,000–12,000 |
| Minisforum N5 Max | Strix Halo | 32/64GB | 22B-70B（含集显） | ⭐⭐⭐⭐ | ¥12,000–18,000 |
| DXP6800 Pro（NAS） | Intel i5-1235U | 8GB | 7B-13B（可加 eGPU） | ⭐⭐⭐ | ¥7,000 |

**⚠️ Mac Mini M4 库存警告（2026年4月）：**
中国 OpenClaw AI Agent 热潮导致 Mac Mini M4 严重缺货，官方价溢价 ¥500-600，等待周期 4-5 周。建议提前预订。

**三套推荐方案：**

**方案A（一体化首选）：** Mac Mini M4 Pro 48GB（¥7,500）
- 可运行 70B 模型，24/7 静音运行，无需额外散热
- 适合 5-15 人团队的私有 AI 服务

**方案B（存储+推理混合）：** DXP6800 Pro NAS（¥7,000）+ RTX 3090 eGPU（¥5,000）= ¥12,000
- 同时提供团队存储和 AI 推理能力
- Thunderbolt 4 扩展，可后期升级显卡

**方案C（Windows 生态）：** Intel NUC 14 Pro AI（¥10,000，32GB）
- 配合 Ollama + Open WebUI，团队成员浏览器直接访问
- NPU 加速 Whisper 等轻量模型

---

## 四、极客端（Geek Workstation）

### 高性能工作站方案

| 配置 | 显存/内存 | 最大模型 | 参考价（RMB） |
|------|---------|---------|-------------|
| Mac Studio M4 Max | 128GB 统一内存 | 70B 实时推理 | ¥18,000–25,000 |
| Mac Studio M3 Ultra | 256GB 统一内存 | 70B+、多模型并行 | ¥25,000–50,000 |
| 双路 RTX 5090D | 48GB（24+24）GDDR7 | 70B+、微调 | ¥35,000–50,000+ |

**出口管制现状（2026年4月）：**
- H100/H200/Blackwell：完全禁止 ❌
- RTX 4090：禁止出口，灰市高价 ⚠️
- RTX 5090D V2：官方暂停后已恢复（2025年12月），供应有限 ⚠️
- Apple Silicon（Mac Studio/Pro）：无限制 ✅ → **最安全的极客选择**

**推荐：** Mac Studio M3 Ultra 256GB（约 ¥50,000）是中国市场唯一不受出口管制限制、可运行超大模型的原生方案。

---

## 五、三年分摊月成本对比

| 方案 | 购买价格 | 月电费估算 | 三年月均成本 | 备注 |
|------|---------|---------|------------|------|
| 手机（已有） | ¥0 增量 | 可忽略 | ¥0 | 利用现有设备 |
| Mac Mini M4 24GB | ¥4,999 | ~¥30 | ¥169/月 | 24/7 运行 |
| Mac Mini M4 Pro 48GB | ¥7,499 | ~¥40 | ¥249/月 | 团队首选 |
| RTX 3090 二手 + PC | ¥5,000+¥8,000 | ~¥100 | ¥472/月 | 含电费 |
| Mac Studio M3 Ultra | ¥50,000 | ~¥80 | ¥1,469/月 | 极客级 |

---

## 六、东南亚市场差异（附录）

- 进口渠道畅通，价格比中国高 10-20%
- HuggingFace 直接访问，无需镜像
- Apple Silicon 同样可购，部分市场有免税区优势
- 泰国、越南、新加坡有本地化语言模型需求（待 R05 专项报告）

---

## 主要信息来源

- [Local LLMs Apple Silicon Mac 2026 Guide](https://www.sitepoint.com/local-llms-apple-silicon-mac-2026/)
- [China OpenClaw Mac mini shortage](https://cntechpost.com/2026/03/13/)
- [RTX 5090D V2 China Launch](https://www.tweaktown.com/news/106995/)
- [Running LLMs on Snapdragon 8 Elite](https://grapeup.com/blog/running-llms-on-device-with-qualcomm-snapdragon-8-elite/)
- [LLM VRAM Requirements Complete Guide](https://localllm.in/blog/ollama-vram-requirements-for-local-llms)
- [Best NAS for AI 2026](https://ownyourai.dev/hardware/best-nas-for-ai/)
