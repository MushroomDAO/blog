# Aura AI Local AI 栏目建设计划

> Aura AI · 每周更新 · 帮助每个人找到最优本地 AI 方案
> 
> 分支：`local-AI` | 域名：auraai.mushroom.cv | 更新：2026-04-18

---

## 栏目定位

**核心问题：** 我手头的设备，能跑什么 AI，怎么搭，用哪些软件，解决什么场景的问题？

**目标用户：** 普通用户（傻瓜方案）+ 极客用户（DIY 方案）

**更新频率：** 每周一次，持续跟踪模型/硬件/协议变化

**地域覆盖：** 中国大陆 · 东南亚 · 海外华人社区

---

## 网站架构（auraai.mushroom.cv）

### 页面结构

```
auraai.mushroom.cv/
├── index.html              ← 首页：Aura AI 介绍 + 4个研究栏目入口
├── r01-hardware/
│   └── index.html          ← R01 硬件报告（含历史版本索引）
├── r02-models/
│   └── index.html          ← R02 模型报告（含历史版本索引）
├── r03-software/
│   └── index.html          ← R03 软件报告（含历史版本索引）
├── r04-best-practices/
│   └── index.html          ← R04 最佳实践（按主题分页）
└── assets/
    ├── style.css
    └── logo.png
```

### 首页布局（index.html）

```
┌─────────────────────────────────────────────────────┐
│  AURA AI · Local AI 周报                            │
│  副标题：让每个人平等拥有 AI                          │
│  [关于 Aura AI] [Mycelium Protocol] [宣言文章链接]   │
├────────────┬────────────┬────────────┬──────────────┤
│ R01 硬件   │ R02 模型   │ R03 软件   │ R04 最佳实践 │
│            │            │            │              │
│ 手机/PC/   │ STT/TTS/   │ 按岗位/    │ 中小组织     │
│ 社区/极客  │ OCR/图像/  │ 场景/极客  │ 人+AI 构建   │
│            │ 代码...    │ 级分类     │              │
│ [查看报告] │ [查看报告] │ [查看报告] │ [查看报告]   │
│            │            │            │              │
│ 更新: 4/17 │ 更新: 4/17 │ 即将发布   │ 即将发布     │
├────────────┴────────────┴────────────┴──────────────┤
│ 成本计算器（内嵌）：我的预算 ___ 能买什么？           │
└─────────────────────────────────────────────────────┘
```

### 技术选型

**选型：Python 自建 Markdown→HTML 构建脚本**

理由：
- 内容全部是 markdown，无需框架
- 构建脚本 100-150 行 Python，完全可控
- 无 Node/npm 依赖，维护成本最低
- Cloudflare Pages 只需 `git push` 触发静态构建
- 后续更新只需添加新 markdown 文件 → 重新 build

技术依赖：
```
python3 + markdown + jinja2 + pygments（代码高亮）
build.py → 读取 research/local-AI/reports/*.md → 生成 dist/
```

备选方案（若 Python 脚本不够用）：**Eleventy (11ty)** — markdown 原生，Cloudflare Pages 支持好

### 部署流程

```bash
# 本地预览
python3 build.py && python3 -m http.server 8080 --directory dist/

# 部署到 Cloudflare Pages
npx wrangler pages deploy dist/ --project-name=auraai --branch=main

# 域名配置
# Cloudflare Pages 控制台 → 自定义域名 → auraai.mushroom.cv
```

### 更新机制

每次更新研究报告时：
1. 在对应目录新建以日期命名的文件，如 `R01-hardware-china-market-20260424.md`
2. 原始报告文件保持最新版本
3. 各栏目 index 页自动生成历史版本链接列表

---

## 四大研究报告（Research Reports）

### R01 · 硬件方案 ✅ 已完成

**文件：** `reports/R01-hardware-china-market.md`

覆盖：手机/PC/社区端/极客端 × 中国市场价格 × GPU 出口管制 × 三年月成本

**待补充：**
- [ ] T1.6 东南亚市场硬件差异
- [ ] T1.1.x 手机端 App 深度对比

---

### R02 · 模型匹配 ✅ 已完成

**文件：** `reports/R02-models-by-domain.md`

覆盖：10 个 AI 域（STT/TTS/OCR/图像/VLM/视频/对话/代码/Embedding/记忆）× 硬件匹配矩阵

**待补充：**
- [ ] T2.4 量化版本质量损失对比（Q4/Q8/FP16）
- [ ] T2.5 每周更新追踪机制

---

### R03 · 软件与工具 🔄 待启动

**文件：** `reports/R03-software-by-role.md`

**核心问题：** 我是 XX 岗位/场景，应该用什么 AI 软件？

#### 分类维度

**维度A：按岗位角色**

| 角色 | 核心诉求 | 代表软件 |
|------|---------|---------|
| **程序员/开发者** | 代码补全、调试、文档 | Continue.dev、Cursor、Copilot替代 |
| **设计师** | 图像生成、风格迁移、素材创作 | ComfyUI、InvokeAI、Krita AI |
| **内容创作者** | 视频字幕、剪辑辅助、文案生成 | Whisper Desktop、剪映AI插件 |
| **知识工作者** | 笔记整理、文档总结、知识库 | Obsidian+RAG、Onyx、PrivateGPT |
| **运营/市场** | 文案生成、图片处理、翻译 | Open WebUI、LM Studio、翻译工具 |
| **学生/研究者** | 论文阅读、知识问答、笔记 | AnythingLLM、Zotero AI、Perplexica |
| **普通用户（傻瓜）** | 语音输入、聊天助手、照片 | LM Studio、Jan、Enchanted（iOS） |

**维度B：按使用场景**

| 场景 | 痛点 | 推荐工具 |
|------|------|---------|
| **免费语音输入法** | 输入慢，隐私泄露 | WhisperInput、SpeechNote、PocketPal |
| **本地知识库** | 笔记分散无法搜索 | Obsidian+智谱、AnythingLLM |
| **私密文件处理** | 不敢上传公司文件 | Onyx、PrivateGPT、LlamaIndex |
| **本地图像生成** | 订阅费贵，隐私 | ComfyUI、AUTOMATIC1111/Forge |
| **离线翻译** | 无网络或涉密 | LibreTranslate、Argos Translate |
| **代码辅助** | IDE 插件费用高 | Continue.dev+Ollama、Twinny |
| **视频字幕/转录** | 剪辑软件订阅费贵 | Whisper Desktop、faster-whisper |

**维度C：按技术门槛**

| 层级 | 定义 | 代表工具 |
|------|------|---------|
| **傻瓜级** | 下载即用，无需配置 | LM Studio、Jan、Enchanted |
| **进阶级** | 需要简单配置 | Ollama+Open WebUI、AnythingLLM |
| **极客级** | 命令行+配置文件 | llama.cpp、vllm、ComfyUI |
| **开发者级** | API集成+自定义 | Ollama API、LlamaIndex、LangChain |

#### 研究任务

- [ ] **T3.1** 傻瓜级工具横评：LM Studio vs Jan vs GPT4All（安装、中文支持、速度）
- [ ] **T3.2** 程序员工具链：Continue.dev + Ollama + DeepSeek-Coder 全配置教程
- [ ] **T3.3** 设计师工具链：ComfyUI 本地安装 + FLUX.1 工作流 + Kolors 中文提示词
- [ ] **T3.4** 语音输入完整方案：iOS/Android/PC 三端对比测评
- [ ] **T3.5** 知识库工具横评：Onyx vs AnythingLLM vs Obsidian+RAG
- [ ] **T3.6** 开源免费优先原则：每个推荐工具注明授权和费用

#### T3.2 程序员工具链（L2 拆分）

- [ ] T3.2.1 Continue.dev + Ollama 配置（VS Code + Cursor）
- [ ] T3.2.2 Twinny vs Copilot替代品对比
- [ ] T3.2.3 Aider（命令行AI编程）配置教程
- [ ] T3.2.4 本地 Code Review Agent 搭建方案

#### T3.4 语音输入（L2 拆分）

- [ ] T3.4.1 iOS：PocketPal + Whisper 快捷指令方案
- [ ] T3.4.2 Android：WhisperInput / SpeechNote / MNN LLM
- [ ] T3.4.3 PC：Whisper Desktop / faster-whisper / whisper.cpp
- [ ] T3.4.4 中文准确率对比：普通话 / 粤语 / 闽南话

---

### R04 · 最佳实践 🔄 待启动

**文件：** `reports/R04-best-practices-smb-human-ai.md`（首篇）

**更新方式：** 按主题独立文件 + 日期版本，如：
```
R04-smb-human-ai-roles-20260418.md    ← 本期
R04-personal-ai-workflow-20260425.md  ← 下期
```

#### 首篇主题：中小组织 人+AI 角色构建

**核心问题：** 一个 5-50 人的组织，如何引入 AI，建立人+AI 协作机制？

**研究框架：**

```
1. 角色分析
   └── 中小组织通用角色清单（运营/设计/销售/客服/研发）
   └── 每个角色当前痛点 × AI 可替代程度评估

2. 技能路径（Skill）
   └── 每个角色需要学习哪些 AI 工具
   └── 学习路径：从傻瓜→进阶→极客的成长曲线
   └── 评估指标：能独立完成什么 AI 任务

3. Agent 构建
   └── 如何为每个角色定制专属 Agent
   └── 训练方式：提示词工程 / RAG / Fine-tune
   └── Agent 评估标准：输出质量 / 稳定性 / 成本

4. AI Native 评估标准
   └── 个人 AI Native 指标（5个维度）
   └── 组织 AI Native 指标（流程/决策/协作三层）
   └── 评估工具：自测问卷 + 评分模型
```

#### 研究任务

- [ ] **T4.1** 中小组织通用角色 AI 使用调研（运营/设计/销售/客服/研发）
- [ ] **T4.2** 运营角色人+AI 完整配置方案（首选深度研究对象）
- [ ] **T4.3** Agent 构建教程：从提示词→RAG→Fine-tune 三步走
- [ ] **T4.4** AI Native 评估标准设计（个人5维度 + 组织3层）
- [ ] **T4.5** 组织变革路径：Skill→Agent→Native 三阶段实施手册

#### T4.2 运营角色深度研究（L2 拆分）

- [ ] T4.2.1 运营日常工作流梳理（内容/数据/用户/活动4类）
- [ ] T4.2.2 各工作流 AI 工具配置（选型+安装+配置）
- [ ] T4.2.3 运营 Agent 定制：品牌声音、行业知识库、数据模板
- [ ] T4.2.4 实测：1人运营+AI vs 3人运营的工作量对比

---

## 网站建设任务清单

### W1. 构建脚本（Python）

- [ ] **W1.1** 设计 HTML 模板（index、报告页、历史版本页）
- [ ] **W1.2** 编写 `build.py`：读取 markdown → 渲染 HTML → 输出 dist/
- [ ] **W1.3** 设计 CSS 样式（极简、中英双语、移动端适配）
- [ ] **W1.4** 首页成本计算器（纯 JS，无后端）
- [ ] **W1.5** 历史版本索引自动生成（按日期文件名排序）

### W2. Cloudflare Pages 配置

- [ ] **W2.1** 创建 Cloudflare Pages 项目（`auraai`）
- [ ] **W2.2** 连接 GitHub 仓库，配置构建命令：`python3 build.py`
- [ ] **W2.3** 配置自定义域名：`auraai.mushroom.cv`
- [ ] **W2.4** 配置 DNS：CNAME → Cloudflare Pages 域名

### W3. 内容填充

- [ ] **W3.1** 首页 Aura AI 介绍文案（引用宣言文章摘要）
- [ ] **W3.2** R01 发布（已有数据，直接上线）
- [ ] **W3.3** R02 发布（已有数据，直接上线）
- [ ] **W3.4** R03 研究完成后发布
- [ ] **W3.5** R04 首篇研究完成后发布

---

## 执行优先级矩阵（更新版）

| 任务 | 优先级 | 预计工时 | 状态 |
|------|--------|---------|------|
| **W1 构建脚本 + 模板** | P0 | 4h | 待开始 |
| **W2 Cloudflare Pages 配置** | P0 | 1h | 待开始 |
| **W3.1-3.3 上线 R01+R02** | P0 | 2h | 待开始 |
| **T3 R03 软件报告** | P1 | 6h | 待开始 |
| **T4.1-4.2 R04 最佳实践首篇** | P1 | 8h | 待开始 |
| T3.2 程序员工具链教程 | P1 | 4h | 待开始 |
| T3.4 语音输入三端方案 | P1 | 3h | 待开始 |
| T2.4 量化版本对比 | P2 | 2h | 待开始 |
| T1.6 东南亚硬件差异 | P2 | 2h | 待开始 |
| T4.4 AI Native 评估标准 | P2 | 4h | 待开始 |
| T5.1 中国镜像替代方案 | P2 | 2h | 待开始 |

---

## 文件目录结构

```
research/local-AI/
├── plan.md                              ← 本文件（持续更新）
├── reports/
│   ├── R01-hardware-china-market.md     ✅ 完成
│   ├── R02-models-by-domain.md          ✅ 完成
│   ├── R03-software-by-role.md          🔄 待启动
│   └── R04-smb-human-ai-roles.md        🔄 待启动
└── website/                             ← 静态网站源文件
    ├── build.py                         ← 构建脚本
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   └── report.html
    ├── assets/
    │   ├── style.css
    │   └── logo.svg
    └── dist/                            ← 构建输出（部署到 CF Pages）
```

---

## D1-D5 研究任务（原有，继续推进）

### D1. 硬件（R01 基础，继续深化）

- [x] T1.1-T1.5 中国市场四端硬件调研 → R01 已完成
- [ ] T1.6 东南亚市场硬件差异

### D2. 模型（R02 基础，继续深化）

- [x] T2.1 HuggingFace Top 模型调研 → R02 已完成
- [ ] T2.2 中文特化模型专项（Qwen3/DeepSeek/Yi）
- [ ] T2.4 量化版本质量损失对比

### D3. 场景（合并入 R03/R04）

- 场景研究成果将体现在 R03 软件报告的"按场景"维度
- 最佳实践案例将体现在 R04

### D4. 工具（合并入 R03）

- 工具调研成果将体现在 R03 软件报告

### D5. 地域差异

- [ ] T5.1 中国 HuggingFace 镜像替代（ModelScope/hf-mirror/魔搭）
- [ ] T5.2 国产模型生态调研

---

*计划持续更新 · 执行顺序以优先级矩阵为准 · 调研结果存入 reports/ 目录*
