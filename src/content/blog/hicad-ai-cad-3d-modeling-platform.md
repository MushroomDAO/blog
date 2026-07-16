---
title: "HiCAD：用自然语言建 3D 模型，直接导出 STL 去打印"
titleEn: "HiCAD: Describe in Natural Language, Get a 3D-Printable Parametric Model"
description: "开源 AI CAD 建模平台 HiCAD，输入一句话自动生成参数化 JSCAD 3D 模型，Three.js 实时预览，滑块调参数，一键导出 STL/OBJ 文件送进 3D 打印机。支持 DeepSeek / OpenAI / Qwen，Vue 3 + NestJS 全栈开源，GPL v3。"
descriptionEn: "HiCAD is an open-source AI CAD platform: type a description, get a parametric JSCAD 3D model with Three.js live preview, slider-adjustable parameters, and one-click STL/OBJ export for 3D printing. Supports DeepSeek / OpenAI / Qwen. Full-stack Vue 3 + NestJS, GPL v3."
pubDate: "2026-07-16"
updatedDate: "2026-07-16"
category: "Tech-Experiment"
tags: ["AI", "CAD", "3D建模", "3D打印", "开源", "Vue3", "NestJS", "JSCAD"]
heroImage: "../../assets/images/hicad-ai-cad-platform-banner.jpg"
---

> **GitHub**：[MrXujiang/HiCAD](https://github.com/MrXujiang/HiCAD) · 170 ⭐ · GPL v3  
> **在线体验**：https://hicad.mvtable.com

---

## 它解决的问题

CAD 软件一直有一道很高的入门门槛：学 Fusion 360、SolidWorks 或 OpenSCAD 需要几十到几百小时的练习，才能把脑子里的形状变成模型文件。

HiCAD 把这道门槛压低到**一句话**：输入「一个内径 20mm、外径 40mm、高 30mm 的空心圆柱体」，AI 自动生成对应的 JSCAD 参数化代码，Three.js 在浏览器里实时渲染出来，不满意就用滑块调参数，满意了导出 STL 送进 3D 打印机。

整个流程不需要安装任何 CAD 软件，只需要一个浏览器。

---

## 核心功能一览

| 功能 | 说明 |
|------|------|
| 🤖 **AI 智能建模** | 自然语言 → JSCAD 参数化 3D 代码，DeepSeek/GPT-4o/Qwen 可选 |
| 🎯 **双阶段精准建模** | 复杂模型（机械臂、坦克等）：意图分析 → 确定性代码生成，零定位误差 |
| 👁️ **实时 3D 预览** | WebWorker 驱动无卡顿渲染，Three.js 支持 360° 旋转缩放 |
| ✏️ **Monaco 代码编辑器** | VS Code 同款编辑器内核，语法高亮 + 智能补全 |
| 🎛️ **参数化控制面板** | 滑块实时调整尺寸参数，拖动即可看到模型变化 |
| 📦 **STL / OBJ 导出** | 一键导出，直接兼容 Cura、PrusaSlicer 等切片软件 |
| 🏪 **模板市场** | 浏览和发布社区共享的参数化模板 |
| 🔗 **无需登录的分享链接** | 生成链接，他人无需账号即可在线预览你的模型 |
| 🔄 **多 AI 适配器** | `.env` 一行切换 DeepSeek · OpenAI · Qwen |

---

## 双阶段建模：处理复杂模型的关键设计

对于简单几何体（圆柱、方块、螺丝），AI 直接输出 JSCAD 代码即可。但遇到有关节的机械臂、有履带的坦克这类复杂模型，单次 AI 输出的代码往往会出现定位误差。

HiCAD 的双阶段方案：

```
用户输入「一只六轴机械臂，底座直径 80mm」
        │
        ▼ 第一阶段：意图分析
   AI 解析：
   - 关节数量、相对位置关系
   - 各部件的尺寸约束
   - 运动范围需求
        │
        ▼ 第二阶段：确定性代码生成
   backend/src/modules/ai/jscad-codegen.ts
   基于分析结果，用模板 + 参数确定性生成 JSCAD 代码
        │
        ▼ 输出：零定位误差的 3D 模型
```

这个设计的本质是**把 AI 的「理解」和「生成」分开**：第一阶段依赖 AI 的语义理解能力，第二阶段用确定性算法保证输出的精确性。

---

## 技术架构

HiCAD 是一个 Monorepo，分三层：

```
hicad/
├── frontend/          # Vue 3 + Vite + Three.js + Monaco Editor
├── backend/           # NestJS + TypeScript + lowdb + SSE
└── shared/            # 前后端共享 TypeScript 类型定义
```

### 前端技术选择

| 库 | 用途 |
|---|---|
| Vue 3 (Composition API) | UI 框架 |
| Three.js | WebGL 3D 渲染，WebWorker 驱动零卡顿 |
| Monaco Editor | VS Code 同款代码编辑器内核 |
| Pinia | 状态管理（编辑器状态、AI 会话、用户信息） |
| Tailwind CSS | 原子化样式 |

### 后端技术选择

| 库 | 用途 |
|---|---|
| NestJS 10 | 企业级 Node.js 框架，模块化架构 |
| SSE（Server-Sent Events） | AI 流式输出实时推送到浏览器 |
| lowdb | 轻量级 JSON 文件数据库，零配置，适合独立部署 |
| Passport JWT | 无状态身份认证 |
| bcrypt | 密码安全哈希 |

后端的 AI 适配器层设计值得关注：

```
backend/src/modules/ai/
├── adapters/
│   ├── deepseek.adapter.ts   # DeepSeek V3
│   ├── openai.adapter.ts     # GPT-4o
│   └── qwen.adapter.ts       # Qwen-Max
├── design-prompt.ts          # 机械臂意图分析 Prompt
├── tank-prompt.ts            # 坦克意图分析 Prompt
├── jscad-codegen.ts          # 确定性代码生成器
└── prompt-builder.ts         # 通用建模 Prompt 构建
```

切换 AI 提供商只需修改 `.env` 里的 `AI_ADAPTER` 字段，不动任何代码。

---

## 5 分钟本地跑起来

前置要求：Node.js ≥ 18、pnpm ≥ 9

```bash
# 1. 克隆
git clone https://github.com/MrXujiang/HiCAD.git
cd HiCAD

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，至少填一个 AI API Key：
# AI_ADAPTER=deepseek
# DEEPSEEK_API_KEY=sk-xxx

# 3. 安装依赖并启动
pnpm install && pnpm start
```

访问 http://localhost:3000，前端页面和 API 服务都在这个端口下（前端静态文件由 NestJS 托管）。

**激活码**：首次注册需要激活码，关注微信公众号「趣谈AI」，回复「HiCAD」免费获取。

---

## 生产部署（PM2 + Nginx）

```bash
# 构建
pnpm build

# PM2 启动后端
pm2 start ecosystem.config.json
pm2 save && pm2 startup
```

Nginx 配置的关键是 SSE 流式响应需要关闭 buffering：

```nginx
location /api {
    proxy_pass http://localhost:3000;
    proxy_buffering off;      # SSE 必须关闭缓冲
    proxy_cache off;
    proxy_read_timeout 300s;  # AI 响应可能较慢
}
```

---

## 当前路线图

- [x] AI 自然语言 → JSCAD 3D 模型
- [x] 双阶段精准建模（机械臂 / 坦克）
- [x] Monaco 编辑器 + 实时预览 + 参数化面板
- [x] 模板市场 + STL/OBJ 导出
- [ ] Docker 一键部署
- [ ] 更多 AI 模型类型（人形机器人、建筑结构）
- [ ] 协同编辑
- [ ] 模型版本历史

---

## 适合谁用

- **创客 / 3D 打印爱好者**：有想法但不会 CAD，直接自然语言描述然后打印出来
- **工程师快速原型**：不需要精密工程图纸时，快速生成参考模型
- **教育场景**：通过参数化建模直观学习几何和空间关系
- **开发者二次开发**：GPL v3 开源，AI 适配器层已抽象好，替换成自己的模型只需实现对应接口

---

## 一句话总结

HiCAD 做的事情很直接：**用 AI 把「会说话」和「会 CAD」之间的门槛彻底打掉**。技术选型务实（Vue 3 + NestJS + Three.js + lowdb），没有过度工程化，本地能跑，生产能部署，代码结构清晰。对于想快速把想法变成可打印实体的人，值得一试。

© 2026 Author: Mycelium Protocol

<!--EN-->

## HiCAD: Describe in Natural Language, Get a 3D-Printable Parametric Model

**GitHub**: [MrXujiang/HiCAD](https://github.com/MrXujiang/HiCAD) · 170 ⭐ · GPL v3  
**Live demo**: https://hicad.mvtable.com

### What It Does

HiCAD is an open-source AI CAD platform that turns natural language descriptions into parametric 3D models you can print. You type something like "a hollow cylinder with inner diameter 20mm, outer diameter 40mm, height 30mm" — the AI generates JSCAD parametric code, Three.js renders it live in the browser, and you adjust dimensions via sliders. When satisfied, export STL or OBJ and load it directly into your slicer.

No CAD software to install. Just a browser.

### Key Features

- **AI Modeling**: Natural language → JSCAD parametric 3D code (DeepSeek/OpenAI/Qwen selectable via `.env`)
- **Two-phase modeling**: For complex models (robotic arms, tanks): intent analysis first, then deterministic code generation — eliminates positioning errors
- **Live 3D Preview**: Three.js with WebWorker — no jank even during generation
- **Monaco Editor**: VS Code's editor engine for manual JSCAD editing
- **Parametric sliders**: Drag to adjust dimensions, watch the model update instantly
- **STL / OBJ export**: Compatible with Cura, PrusaSlicer, and other slicers
- **Template marketplace**: Community parametric templates
- **Shareable links**: Preview without an account

### Architecture

Monorepo with three layers: `frontend/` (Vue 3 + Vite + Three.js + Monaco), `backend/` (NestJS + SSE for streaming + lowdb), and `shared/` TypeScript types.

The AI adapter layer is cleanly abstracted — switching AI providers is a single `.env` change:

```env
AI_ADAPTER=deepseek   # or: openai | qwen
DEEPSEEK_API_KEY=sk-xxx
```

### Quick Start

```bash
git clone https://github.com/MrXujiang/HiCAD.git
cd HiCAD
cp .env.example .env   # fill in your API key
pnpm install && pnpm start
# Open http://localhost:3000
```

### The Two-Phase Design Insight

For complex articulated models, single-pass AI generation produces positioning errors. HiCAD splits the work: AI handles semantic understanding (what joints exist, what constraints apply), then a deterministic code generator produces the JSCAD output from those structured parameters — eliminating the error-prone step of asking AI to also handle geometric precision.

This separation of "understanding" from "generating" is the core architectural idea worth borrowing in any AI-generation pipeline.

### Bottom Line

HiCAD removes the barrier between "being able to describe a shape" and "being able to model it." Practical tech stack, clean architecture, self-hostable. GPL v3 open-source.

© 2026 Author: Mycelium Protocol
