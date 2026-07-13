---
title: "用 Gemini + React Three Fiber 造 3D 互动科学应用：完整拆解与上手指南"
titleEn: "Build 3D Interactive Science Apps with Gemini + React Three Fiber: Full Breakdown and Tutorial"
description: "Dilum Sanjaya 用 Gemini 3 Pro 做了 3D 昆虫机器人模拟器、3D 智能家居、AI 对话造物等一系列互动科学应用。本文完整拆解技术栈，手把手带你从零搭一个 AI 驱动的 3D 互动场景。"
descriptionEn: "Dilum Sanjaya built 3D insect robot simulators, smart home apps, and AI-driven 3D scene builders with Gemini 3 Pro. This guide fully breaks down the tech stack and walks you through building an AI-powered 3D interactive scene from scratch."
pubDate: "2026-07-13"
updatedDate: "2026-07-13"
category: "Tech-Experiment"
tags: ["Gemini", "React Three Fiber", "3D", "AI应用开发"]
heroImage: "../../assets/images/gemini-3d-interactive-science-apps-react-three-fiber-tutorial-banner.jpg"
---

> 本文基于 Dilum Sanjaya（[@dilums](https://github.com/dilums)）的三个开源仓库，结合 Gemini 3 Pro 的 AI 能力和 React Three Fiber 的 3D 渲染能力，完整拆解 AI 驱动 3D 科学互动应用的建造方式。

---

## 先看 Dilum 做了什么

Dilum Sanjaya 是一位斯里兰卡开发者，过去一年里陆续用 Gemini 3 Pro 做了一系列引人注目的互动科学应用：

| 项目 | 技术亮点 | 仓库 |
|------|---------|------|
| **AI 对话造 3D 世界** | 输入自然语言 → AI 生成 3D 场景 JSON → R3F 实时渲染 | [aisdk-threejs-starter](https://github.com/dilums/aisdk-threejs-starter) |
| **Gemini 智能家居 3D** | Gemini 3 Pro 直驱 Three.js，实时控制 3D 家居场景 | [gemini-3-smart-home-app](https://github.com/dilums/gemini-3-smart-home-app) |
| **六足昆虫机器人模拟器** | 六足昆虫运动学算法 + 3D 可视化 + 轨迹图表 | [hexapod-robot-simulator](https://github.com/dilums/hexapod-robot-simulator) |

这三个项目的共同核心是：**用 AI 作为大脑，用 React Three Fiber（R3F）作为眼睛，把自然语言指令变成 3D 里的物理世界。**

---

## 技术栈全景

### 前端渲染层

**Three.js + React Three Fiber** 是这套技术的骨架。

- **Three.js**：WebGL 封装库，可以在浏览器里渲染 3D 场景，无需 OpenGL 知识
- **React Three Fiber（R3F）**：把 Three.js 包装成 React 组件，用声明式写法写 3D 场景
- **@react-three/drei**：R3F 常用工具包，提供 OrbitControls（鼠标旋转拖拽）、Environment（光照贴图）等开箱即用组件

### AI 接入层

Dilum 的项目里用了两种 Gemini 接入方式：

**方式 A：通过 Vercel AI SDK（支持 OpenAI / Gemini 切换）**
```bash
npm install ai @ai-sdk/google @ai-sdk/react
```
适合 Next.js，提供流式响应和 `useChat` hook。

**方式 B：直接用 `@google/genai` 官方 SDK**
```bash
npm install @google/genai
```
适合 Vite/React SPA，直接在客户端调用 Gemini API。

### 完整 package.json 示例

```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@google/genai": "^1.30.0",
    "@react-three/fiber": "^9.4.0",
    "@react-three/drei": "^10.7.7",
    "three": "^0.181.2",
    "next": "^15.5.4"
  }
}
```

---

## 核心原理拆解：AI 怎么「造」3D 物体

这是整套技术最关键的设计，理解这一点，后面的代码就全通了。

### 思路：让 AI 说 JSON，前端听 JSON 渲染

直接让 AI 写 Three.js 代码然后执行是危险的（XSS/沙箱问题）。Dilum 的方案更聪明：

```
用户输入文字 → AI 输出结构化 JSON → React Three Fiber 渲染 JSON
```

**第一步：给 AI 一个 System Prompt，约定 JSON 格式**

```typescript
export const systemPrompt = `你是一个 3D 场景生成助手。
当用户描述想要的 3D 物体时：
1. 用自然语言回应
2. 用 [3D_OBJECT][/3D_OBJECT] 标签包裹 JSON 描述

JSON 格式：
{
  "type": "box" | "sphere" | "cylinder" | "cone",
  "position": [x, y, z],  // 数值范围 -5 到 5
  "color": "hex 颜色或 CSS 颜色名",
  "args": [...],           // Three.js 几何体构造参数
  "rotation": [x, y, z]   // 可选，弧度
}

几何体参数参考表：
- box: [width, height, depth]，默认 [1, 1, 1]
- sphere: [radius, widthSegments, heightSegments]，默认 [1, 32, 32]
- cylinder: [radiusTop, radiusBottom, height, segments]，默认 [1, 1, 2, 32]
- cone: [radius, height, segments]，默认 [1, 2, 32]

地面规则：y=0 是地面，所有物体必须在地面以上。
`;
```

**第二步：解析 AI 输出，提取 JSON**

```typescript
export function extractObjects(response: string) {
  const blocks = [];
  const re = /\[3D_OBJECT\]([\s\S]*?)\[\/3D_OBJECT\]/g;
  let match;
  while ((match = re.exec(response)) !== null) {
    try {
      const raw = JSON.parse(match[1].trim());
      blocks.push({ ...raw, id: crypto.randomUUID() });
    } catch (e) {
      continue;
    }
  }
  return blocks;
}
```

**第三步：React Three Fiber 渲染 JSON 里描述的几何体**

```typescript
function SceneObject({ type, position, color, args, rotation }: ObjectSpec) {
  const geometry = useMemo(() => {
    switch (type) {
      case "box":      return <boxGeometry args={args} />;
      case "sphere":   return <sphereGeometry args={args} />;
      case "cylinder": return <cylinderGeometry args={args} />;
      case "cone":     return <coneGeometry args={args} />;
      default:         return <boxGeometry args={[1,1,1]} />;
    }
  }, [type, args]);

  return (
    <mesh position={position} rotation={rotation}>
      {geometry}
      <meshStandardMaterial color={color} />
    </mesh>
  );
}
```

**这是核心魔法：AI 不需要写 Three.js 代码，它只需要说「放一个红色的盒子在位置 [1,0.5,0]」，JSON 解析器接管剩余的工作。**

---

## 完整搭建步骤

### 第一步：创建项目

```bash
npx create-next-app@latest my-3d-science-app --typescript --tailwind
cd my-3d-science-app
npm install @google/genai @react-three/fiber @react-three/drei three
npm install @ai-sdk/google ai @ai-sdk/react  # 如果用 AI SDK 方式
```

### 第二步：创建 3D 画布组件

```typescript
// components/Scene3D.tsx
"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, Grid } from "@react-three/drei";
import { Suspense } from "react";

interface SceneObject {
  id: string;
  type: "box" | "sphere" | "cylinder" | "cone";
  position: [number, number, number];
  color: string;
  args: number[];
  rotation?: [number, number, number];
}

function Object3D({ type, position, color, args, rotation }: SceneObject) {
  const pos = position || [0, 0.5, 0];
  const rot = rotation || [0, 0, 0];

  return (
    <mesh position={pos} rotation={rot}>
      {type === "box"      && <boxGeometry args={args} />}
      {type === "sphere"   && <sphereGeometry args={args} />}
      {type === "cylinder" && <cylinderGeometry args={args} />}
      {type === "cone"     && <coneGeometry args={args} />}
      <meshStandardMaterial color={color} roughness={0.4} metalness={0.1} />
    </mesh>
  );
}

export function Scene3D({ objects }: { objects: SceneObject[] }) {
  return (
    <Canvas camera={{ position: [0, 5, 10], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
      <Suspense fallback={null}>
        <Environment preset="city" />
        {objects.map((obj) => (
          <Object3D key={obj.id} {...obj} />
        ))}
        <Grid
          args={[20, 20]}
          cellSize={1}
          cellThickness={0.5}
          sectionSize={5}
          fadeDistance={25}
        />
      </Suspense>
      <OrbitControls makeDefault />
    </Canvas>
  );
}
```

### 第三步：接入 Gemini API（方式 A — 直接 SDK）

```typescript
// lib/gemini.ts
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.NEXT_PUBLIC_GEMINI_API_KEY! });

export async function ask3DScene(userMessage: string, history: any[]) {
  const response = await ai.models.generateContent({
    model: "gemini-3-pro",
    contents: [
      { role: "user", parts: [{ text: systemPrompt }] },
      ...history,
      { role: "user", parts: [{ text: userMessage }] },
    ],
  });
  return response.text ?? "";
}
```

### 第三步（方式 B）：通过 AI SDK + API Route（Next.js）

```typescript
// app/api/chat/route.ts
import { google } from "@ai-sdk/google";
import { streamText, convertToModelMessages } from "ai";
import { systemPrompt } from "@/prompts/system";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: google("gemini-2.0-flash"),        // 或 "gemini-3-pro"
    system: systemPrompt,
    messages: convertToModelMessages(messages),
  });
  return result.toUIMessageStreamResponse();
}
```

### 第四步：主页面，把 AI 对话和 3D 渲染连起来

```typescript
// app/page.tsx
"use client";
import { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { Scene3D } from "@/components/Scene3D";
import { extractObjects } from "@/lib/utils";

export default function Home() {
  const [sceneObjects, setSceneObjects] = useState<any[]>([]);

  const { messages, sendMessage, status } = useChat({
    api: "/api/chat",
    onFinish: (response) => {
      const text = response.message.parts
        .find((p) => p.type === "text")?.text ?? "";
      const newObjects = extractObjects(text);
      if (newObjects.length > 0) {
        setSceneObjects((prev) => [...prev, ...newObjects]);
      }
    },
  });

  return (
    <div className="h-screen flex">
      {/* 左侧：3D 场景 */}
      <div className="flex-1">
        <Scene3D objects={sceneObjects} />
      </div>

      {/* 右侧：对话面板 */}
      <div className="w-80 border-l flex flex-col p-4 gap-4">
        <h1 className="font-bold text-lg">AI 3D 造物助手</h1>
        <div className="flex-1 overflow-y-auto space-y-2">
          {messages.map((m) => (
            <div key={m.id}
              className={`p-2 rounded text-sm ${
                m.role === "user" ? "bg-blue-100 text-right" : "bg-gray-100"
              }`}
            >
              {m.parts.find(p => p.type === "text")?.text
                ?.replace(/\[3D_OBJECT\][\s\S]*?\[\/3D_OBJECT\]/g, "")
                .trim()}
            </div>
          ))}
        </div>
        <form onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          const msg = fd.get("msg") as string;
          if (msg.trim()) { sendMessage({ text: msg }); e.currentTarget.reset(); }
        }} className="flex gap-2">
          <input name="msg" className="flex-1 border rounded px-2 py-1 text-sm"
            placeholder="描述你想要的 3D 物体…"
            disabled={status === "submitted"} />
          <button type="submit" className="bg-blue-500 text-white px-3 rounded text-sm">
            发送
          </button>
        </form>
        {/* 快捷示例 */}
        <div className="flex flex-wrap gap-1">
          {["加一只蝴蝶", "造一棵树", "来只蜻蜓", "加几朵花"].map((s) => (
            <button key={s} onClick={() => sendMessage({ text: s })}
              className="text-xs border rounded px-2 py-1 hover:bg-gray-50">
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 六足昆虫机器人：更进一步的科学模拟

Dilum 的 `hexapod-robot-simulator` 展示了如何在 3D 中模拟真实的昆虫运动学。六足机器人（Hexapod）的 6 条腿运动完全复刻了蜘蛛、螳螂等昆虫的步态逻辑。

**核心算法：逆运动学（Inverse Kinematics）**

传统 3D 动画是正向运动学——告诉每个关节转多少角度。昆虫行走用的是逆运动学——你只需说「把这只脚放在坐标 (x,y,z)」，算法自动计算每个关节应该转多少。

```
足端目标位置 (x, y, z)
        ↓
逆运动学算法（三角函数 + 余弦定理）
        ↓
髋关节角度 + 膝关节角度 + 踝关节角度
        ↓
Three.js 旋转对应的 3D 骨骼
```

该项目基于 [mithi/hexapod](https://github.com/mithi/hexapod) 的纯 JavaScript 运动学库，用 Next.js + shadcn 重构了界面，用 Plotly.js 实时绘制足端轨迹。

**技术栈（昆虫模拟器）：**

```
Next.js 16 + React 19          → 框架
shadcn/ui + Tailwind v4        → UI
Zustand                        → 状态管理（昆虫姿态、步态参数）
Plotly.js                      → 足端轨迹 3D 图表
hexapod 运动学库               → 核心计算（从 mithi/hexapod 移植）
```

---

## 进阶方向：把 Gemini 和昆虫模拟器结合

想象这样一个应用：

```
用户输入："模拟一只蚂蚁爬过一块凸起的石头"
           ↓
Gemini 3 Pro：解析意图 → 输出步态参数 JSON
           ↓
hexapod 运动学引擎：计算关节角度
           ↓
React Three Fiber：实时渲染 6 条腿的运动轨迹
```

Gemini 3 Pro 的多模态能力意味着你还可以：
- 上传一张真实蚂蚁的照片 → AI 分析腿的结构 → 在 3D 里重建
- 描述一种昆虫步态 → AI 生成运动参数 → 实时演示

---

## 快速跑起来

```bash
# 1. 克隆 aisdk-threejs-starter（AI 造物基础版）
git clone https://github.com/dilums/aisdk-threejs-starter.git
cd aisdk-threejs-starter
npm install

# 2. 配置 API key（两选一）
echo "OPENAI_API_KEY=sk-..." > .env.local
# 或切换到 Gemini：把 api/chat/route.ts 里的 openai() 换成 google()

# 3. 启动
npm run dev
# → http://localhost:3000

# 克隆六足昆虫模拟器
git clone https://github.com/dilums/hexapod-robot-simulator.git
cd hexapod-robot-simulator
npm install
npm run dev
```

**把 OpenAI 换成 Gemini（修改 `app/api/chat/route.ts`）：**

```typescript
// 原来
import { openai } from "@ai-sdk/openai";
const result = streamText({ model: openai("gpt-4o"), ... });

// 换成 Gemini
import { google } from "@ai-sdk/google";
const result = streamText({ model: google("gemini-2.0-flash"), ... });
// 同时在 .env.local 里加: GOOGLE_GENERATIVE_AI_API_KEY=你的key
```

---

## 核心技术要点小结

| 想做什么 | 用哪个工具 |
|---------|---------|
| 3D 渲染场景 | React Three Fiber + Three.js |
| 鼠标旋转/拖拽 3D 场景 | `<OrbitControls>` from @react-three/drei |
| AI 生成结构化 3D 描述 | System Prompt 约定 JSON 格式 |
| 接入 Gemini | `@google/genai` 或 `@ai-sdk/google` |
| 流式 AI 响应 | Vercel AI SDK `useChat` + `streamText` |
| 昆虫步态模拟 | hexapod 逆运动学库 |
| 实时数据可视化 | Plotly.js 或 recharts |

三句话记住这套架构：

1. **Gemini 是嘴**：把自然语言翻译成结构化的 JSON 描述
2. **Three.js 是手**：把 JSON 变成浏览器里的 3D 物体
3. **React Three Fiber 是桥**：用 React 组件的方式粘合两者

---

## 参考资源

- [aisdk-threejs-starter](https://github.com/dilums/aisdk-threejs-starter) — AI 对话造 3D 场景起步模板
- [gemini-3-smart-home-app](https://github.com/dilums/gemini-3-smart-home-app) — Gemini 3 Pro 直驱 3D 智能家居
- [hexapod-robot-simulator](https://github.com/dilums/hexapod-robot-simulator) — 六足昆虫运动学模拟器
- [mithi/hexapod](https://github.com/mithi/hexapod) — 原版六足运动学算法库
- [React Three Fiber 文档](https://r3f.docs.pmnd.rs) — R3F 官方文档
- [Gemini API 文档](https://ai.google.dev/gemini-api/docs) — Google Gemini API

© 2026 Author: Mycelium Protocol

<!--EN-->

## Build 3D Interactive Science Apps with Gemini + React Three Fiber: Full Breakdown and Tutorial

> Based on three open-source projects by Dilum Sanjaya ([@dilums](https://github.com/dilums)), covering AI-driven 3D scene generation, Gemini 3 Pro integration, and hexapod insect robot simulation.

---

### What Dilum Built

| Project | Highlight | Repo |
|---------|-----------|------|
| **AI 3D Scene Builder** | Natural language → AI JSON → R3F renders | [aisdk-threejs-starter](https://github.com/dilums/aisdk-threejs-starter) |
| **Gemini Smart Home 3D** | Gemini 3 Pro drives Three.js in real-time | [gemini-3-smart-home-app](https://github.com/dilums/gemini-3-smart-home-app) |
| **Hexapod Robot Simulator** | 6-leg insect kinematics + 3D visualization | [hexapod-robot-simulator](https://github.com/dilums/hexapod-robot-simulator) |

The core idea across all three: **use an LLM as the brain, React Three Fiber as the eyes, and translate natural language into a physical 3D world.**

---

### The AI-to-3D Pipeline

The key design insight: don't let AI write Three.js code directly (XSS risk). Instead, constrain AI to output structured JSON and let the renderer handle the rest.

```
User text → AI (structured JSON in [3D_OBJECT] tags) → parser → React Three Fiber
```

**System prompt (the core):**
```typescript
export const systemPrompt = `You are a 3D scene assistant.
When a user describes an object, output a friendly response AND wrap a JSON spec in [3D_OBJECT][/3D_OBJECT] tags.

JSON format:
{
  "type": "box" | "sphere" | "cylinder" | "cone",
  "position": [x, y, z],   // -5 to 5
  "color": "hex or CSS name",
  "args": [...],            // Three.js geometry constructor args
  "rotation": [x, y, z]    // optional, radians
}

Ground rule: y=0 is the floor. No part of any object may go below y=0.`;
```

**Parser:**
```typescript
export function extractObjects(response: string) {
  const re = /\[3D_OBJECT\]([\s\S]*?)\[\/3D_OBJECT\]/g;
  const blocks = [];
  let match;
  while ((match = re.exec(response)) !== null) {
    try { blocks.push({ ...JSON.parse(match[1].trim()), id: crypto.randomUUID() }); }
    catch (e) { continue; }
  }
  return blocks;
}
```

**R3F renderer:**
```typescript
function Object3D({ type, position, color, args }: ObjectSpec) {
  return (
    <mesh position={position}>
      {type === "box"    && <boxGeometry args={args} />}
      {type === "sphere" && <sphereGeometry args={args} />}
      <meshStandardMaterial color={color} />
    </mesh>
  );
}
```

---

### Switching OpenAI → Gemini

The `aisdk-threejs-starter` defaults to OpenAI. To use Gemini:

```bash
npm install @ai-sdk/google
```

```typescript
// app/api/chat/route.ts — replace one import + one call
import { google } from "@ai-sdk/google";   // was: import { openai } from "@ai-sdk/openai"

const result = streamText({
  model: google("gemini-2.0-flash"),        // was: openai("gpt-4o")
  system: systemPrompt,
  messages,
});
```

`.env.local`:
```
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_key
```

For direct Gemini SDK (Vite/React, no server):
```typescript
import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_GEMINI_KEY });
const response = await ai.models.generateContent({
  model: "gemini-3-pro",
  contents: [{ role: "user", parts: [{ text: prompt }] }],
});
```

---

### Hexapod Insect: Inverse Kinematics in 3D

The hexapod simulator models real insect locomotion. Instead of animating joint angles directly (forward kinematics), it uses **inverse kinematics**: you specify where you want the foot to land, and the algorithm calculates the required joint angles.

```
Target foot position (x, y, z)
       ↓
IK solver (law of cosines + trigonometry)
       ↓
Hip angle + knee angle + ankle angle
       ↓
Three.js rotates the 3D bones
```

Built on the [mithi/hexapod](https://github.com/mithi/hexapod) JS kinematics library, rebuilt with Next.js 16, shadcn/ui, Zustand for state, and Plotly.js for foot trajectory charts.

---

### Quick Start

```bash
# AI 3D scene builder
git clone https://github.com/dilums/aisdk-threejs-starter.git
cd aisdk-threejs-starter && npm install
echo "OPENAI_API_KEY=sk-..." > .env.local  # or GOOGLE_GENERATIVE_AI_API_KEY=
npm run dev   # http://localhost:3000

# Hexapod insect simulator
git clone https://github.com/dilums/hexapod-robot-simulator.git
cd hexapod-robot-simulator && npm install
npm run dev
```

---

### Architecture Summary

| Goal | Tool |
|------|------|
| 3D rendering | React Three Fiber + Three.js |
| Mouse orbit/drag | `<OrbitControls>` (drei) |
| AI → structured 3D | System prompt + JSON schema |
| Gemini integration | `@google/genai` or `@ai-sdk/google` |
| Streaming AI | Vercel AI SDK `useChat` + `streamText` |
| Insect gait simulation | hexapod IK library |
| Data charts | Plotly.js or recharts |

Three sentences: **Gemini is the mouth** (translates language to JSON). **Three.js is the hands** (turns JSON into 3D). **React Three Fiber is the bridge** (connects both with React).

**References:**
- [aisdk-threejs-starter](https://github.com/dilums/aisdk-threejs-starter)
- [gemini-3-smart-home-app](https://github.com/dilums/gemini-3-smart-home-app)
- [hexapod-robot-simulator](https://github.com/dilums/hexapod-robot-simulator)
- [React Three Fiber docs](https://r3f.docs.pmnd.rs)
- [Gemini API docs](https://ai.google.dev/gemini-api/docs)

© 2026 Author: Mycelium Protocol
