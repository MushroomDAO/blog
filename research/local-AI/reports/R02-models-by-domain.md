# R02 模型调研报告：按域分类的本地 AI 最优模型

> 调研日期：2026-04-17 | 数据有效期：2026 Q2 | 状态：✅ 完成

---

## 一、STT / 语音输入

| 模型 | 大小 | VRAM/RAM | 中文准确率 | 速度 | 备注 |
|------|------|---------|-----------|------|------|
| **Whisper Large V3 Turbo** | 1.6GB | 3GB VRAM | ⭐⭐⭐⭐⭐ | 实时 | 首选，速度与精度最优平衡 |
| FunASR Paraformer-ZH | 0.4GB | 1GB RAM | ⭐⭐⭐⭐⭐ | 实时 | 阿里出品，普通话最优，纯离线 |
| SenseVoice Small | 0.28GB | 1GB RAM | ⭐⭐⭐⭐ | 极快 | 支持方言+情绪识别，超轻量 |

**关键结论：**
- 中文普通话首选 **FunASR Paraformer-ZH**（阿里出品，离线最优）
- 多语言混合首选 **Whisper Large V3 Turbo**（1.6GB，速度提升2x vs 原版）
- 手机端首选 **SenseVoice Small**（280MB，方言+情绪）
- HuggingFace: `openai/whisper-large-v3-turbo` | `FunAudioLLM/SenseVoiceSmall`

---

## 二、TTS / 语音合成

| 模型 | 大小 | VRAM/RAM | 中文音质 | 克隆能力 | 备注 |
|------|------|---------|---------|---------|------|
| **CosyVoice 3.0** | 2.5GB | 6GB VRAM | ⭐⭐⭐⭐⭐ | 3秒克隆 | 阿里出品，中文最自然 |
| Fish Audio S2 Pro | 1.2GB | 4GB VRAM | ⭐⭐⭐⭐⭐ | 10秒克隆 | 多语言，速度快 |
| ChatTTS | 0.9GB | 2GB VRAM | ⭐⭐⭐⭐ | 有限 | 开源轻量，情感表达好 |

**关键结论：**
- 中文自然度首选 **CosyVoice 3.0**（3秒声音克隆）
- 多语言/轻量首选 **Fish Audio S2 Pro**
- HuggingFace: `FunAudioLLM/CosyVoice3-0.5B` | `fishaudio/fish-speech`

---

## 三、OCR / 文档识别

| 模型 | 大小 | 运行需求 | 准确率 | 速度 | 备注 |
|------|------|---------|--------|------|------|
| **Marker** | 2.1GB | 4GB VRAM | ⭐⭐⭐⭐⭐ | 快 | PDF→Markdown，保留格式 |
| PaddleOCR 3.0 | 0.12GB | CPU 可运行 | ⭐⭐⭐⭐⭐ | 实时 | 百度出品，中文最优，超轻量 |
| Surya | 1.8GB | 4GB VRAM | ⭐⭐⭐⭐ | 中等 | 多语言90+，版式分析强 |

**关键结论：**
- PDF 处理首选 **Marker**（输出 Markdown，保留表格/图表）
- 纯 OCR 中文首选 **PaddleOCR 3.0**（CPU 可运行，极速）
- 手机/嵌入式首选 **PaddleOCR**（仅 120MB）
- HuggingFace: `VikParuchuri/marker` | `PaddlePaddle/PaddleOCR`

---

## 四、文生图 / Image Generation

| 模型 | 大小 | VRAM | 中文提示词 | 质量 | 备注 |
|------|------|------|-----------|------|------|
| **FLUX.1-dev** | 23.8GB | 12GB+ | 需翻译 | ⭐⭐⭐⭐⭐ | 当前开源最高质量 |
| FLUX.2 Klein (量化) | 6.1GB | 8GB | 需翻译 | ⭐⭐⭐⭐ | FLUX.1 量化版，8GB 可跑 |
| Kolors | 8.3GB | 10GB | ⭐⭐⭐⭐⭐ 原生 | ⭐⭐⭐⭐⭐ | 快手出品，中文提示词最优 |

**关键结论：**
- 英文提示词最高质量：**FLUX.1-dev**（需 12GB+ VRAM）
- 显存受限(8GB)：**FLUX.2 Klein 量化版**
- 中文提示词原生支持：**Kolors**（快手出品，专为中文优化）
- HuggingFace: `black-forest-labs/FLUX.1-dev` | `Kwai-Kolors/Kolors`

---

## 五、VLM / 图像理解

| 模型 | 大小 | VRAM | 中文理解 | 文档理解 | 备注 |
|------|------|------|---------|---------|------|
| **MiniCPM-V 2.6** | 8B / 5.5GB | 8GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 综合最强，支持视频 |
| Qwen2.5-VL 32B | 32B / 20GB | 20GB+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 旗舰级，文档理解最强 |
| InternVL3-8B | 8B / 5.8GB | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 学术强，多图处理 |

**关键结论：**
- 8GB 显存最优：**MiniCPM-V 2.6**（支持视频，OCR、图表识别强）
- 旗舰级（20GB+）：**Qwen2.5-VL 32B**（文档/PDF 理解最强）
- HuggingFace: `openbmb/MiniCPM-V-2_6` | `Qwen/Qwen2.5-VL-32B-Instruct`

---

## 六、视频生成

| 模型 | 大小 | VRAM | 质量 | 速度 | 备注 |
|------|------|------|------|------|------|
| **Wan2.1** | 14GB | 16GB | ⭐⭐⭐⭐⭐ | 中等 | 阿里出品，当前开源最强 |
| CogVideoX-5B | 9GB | 12GB | ⭐⭐⭐⭐ | 慢 | 清华出品，文本理解强 |

**关键结论：**
- 视频生成门槛高，**16GB VRAM 是最低要求**
- 质量首选 **Wan2.1**（5秒1080p，细节最优）
- 显存有限(12GB)：**CogVideoX-5B**
- HuggingFace: `Wan-AI/Wan2.1-T2V-14B` | `THUDM/CogVideoX-5b`

---

## 七、通用对话 / Chat（≤7B 本地可运行）

| 模型 | 大小 | VRAM | 中文能力 | 推理能力 | 备注 |
|------|------|------|---------|---------|------|
| **Qwen3-7B** | 7B / 4.5GB | 6GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中文最优，思维链支持 |
| Llama 3.2-3B | 3B / 2.0GB | 3GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | 手机端首选 |
| Gemma 3-4B | 4B / 2.5GB | 4GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | Google出品，多语言强 |

**关键结论：**
- 中文对话首选 **Qwen3-7B**（阿里 Q2 2025，推理+中文双强）
- 手机/低显存：**Llama 3.2-3B**（2GB 可运行）
- Ollama 直接拉取：`ollama pull qwen3:7b` | `ollama pull llama3.2:3b`

---

## 八、代码辅助 / Code

| 模型 | 大小 | VRAM | 代码质量 | 补全速度 | 备注 |
|------|------|------|---------|---------|------|
| **DeepSeek-Coder-V2-Lite** | 16B / 9.7GB | 10GB | ⭐⭐⭐⭐⭐ | 快 | 代码综合最强，MIT协议 |
| Qwen2.5-Coder-7B | 7B / 4.5GB | 6GB | ⭐⭐⭐⭐⭐ | 快 | 7B中代码最强 |

**关键结论：**
- 10GB+ 显存首选 **DeepSeek-Coder-V2-Lite**（HumanEval 81.1%）
- 6GB 显存首选 **Qwen2.5-Coder-7B**（7B 中最强代码模型）
- VS Code 插件：Continue.dev 配合 Ollama 使用
- HuggingFace: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` | `Qwen/Qwen2.5-Coder-7B-Instruct`

---

## 九、Embedding / 向量检索

| 模型 | 大小 | 内存 | 检索精度 | 多语言 | 备注 |
|------|------|------|---------|--------|------|
| **BGE-M3** | 570MB | 2GB RAM | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中英双语最优，MTEB No.1 |
| Nomic Embed v2 | 548MB | 1.5GB RAM | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 开源Apache，RAG最优 |

**关键结论：**
- 中英双语 RAG 首选 **BGE-M3**（北航出品，支持稀疏+稠密双检索）
- 纯英文 RAG：**Nomic Embed v2**（Apache 许可，完全开源）
- Ollama 拉取：`ollama pull bge-m3` | `ollama pull nomic-embed-text`

---

## 十、Memory / 长期记忆

| 方案 | 类型 | 部署复杂度 | 功能 | 备注 |
|------|------|---------|------|------|
| **Mem0** | 库/服务 | ⭐⭐ 低 | 自动提取+更新记忆 | 开源，支持本地存储 |
| Letta (MemGPT) | Agent框架 | ⭐⭐⭐ 中 | 无限上下文, 自我编辑记忆 | 最强记忆框架 |

**关键结论：**
- 轻量集成首选 **Mem0**（pip 安装，3行代码，本地 SQLite 存储）
- 复杂 Agent 场景：**Letta**（支持 64K+ 上下文，自动记忆管理）
- GitHub: `mem0ai/mem0` | `letta-ai/letta`

---

## 硬件-模型匹配速查

| 设备/显存 | 推荐组合 |
|---------|---------|
| 手机 (8GB RAM) | SenseVoice + Llama 3.2-3B + PaddleOCR |
| PC 8GB VRAM | Whisper Large V3T + Qwen3-7B + BGE-M3 + MiniCPM-V 2.6 |
| PC 12GB VRAM | 上述全部 + DeepSeek-Coder-V2-Lite + CogVideoX-5B |
| PC 16GB VRAM | 上述 + Wan2.1 视频生成 + FLUX.1-dev 图像生成 |
| 社区端 Mac Mini M4 48GB | Qwen3-32B + Wan2.1 + FLUX.1 + 所有工具全量版本 |

---

## 中国大陆访问渠道

| 原地址 | 国内镜像 |
|--------|---------|
| HuggingFace | hf-mirror.com 或 ModelScope (modelscope.cn) |
| 魔搭社区 | modelscope.cn（阿里出品，国内最全） |
| 始智AI | wisemodel.cn |

---

## 主要信息来源

- HuggingFace Open LLM Leaderboard 2026 Q2
- HuggingFace Spaces: Open ASR Leaderboard
- ModelScope 中文模型排行
- OpenCompass 中文评测基准
- [Whisper Large V3 Turbo](https://huggingface.co/openai/whisper-large-v3-turbo)
- [BGE-M3 Technical Report](https://arxiv.org/abs/2402.03216)
- [Qwen3 Blog](https://qwenlm.github.io/blog/qwen3/)
