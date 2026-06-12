---
title: "一句话生成能上线的 Lottie 动效：这个开源 Skill 讲清了 AI 能解什么"
titleEn: "One Prompt, Production-Ready Lottie: The Open-Source Skill That Shows What AI Can Actually Solve"
description: "diffusionstudio/lottie 是一个让 Claude Code、Codex 等 AI Agent 一句话生成可直接上线 Lottie 动效的开源 Skill。本文读透 README 后写成：安装方法、工作流、高质量 prompt 策略、3大技术陷阱，以及——为什么 Lottie 恰好是 AI「能解」的创意领域。"
descriptionEn: "diffusionstudio/lottie is an open-source skill letting Claude Code or Codex generate production-ready Lottie animations from a single prompt. This guide covers setup, workflow, prompting strategies, 3 critical technical traps, and why Lottie JSON is exactly the kind of creative domain AI can actually solve."
pubDate: "2026-06-12"
updatedDate: "2026-06-12"
category: "Tech-Experiment"
tags: ["Lottie动画", "AI编程", "开源Skill", "Claude Code", "动效设计", "前端开发", "text-to-lottie"]
heroImage: "../../assets/images/text-to-lottie-banner.jpg"
---

> **BLUF**：`diffusionstudio/lottie` 是 GitHub 上一个开源 Skill 框架，让 Claude Code、Codex 等编码 Agent 能从文字描述直接生成可上线的 Lottie 矢量动效 JSON。2.4k ★，MIT 协议，一行命令装好，热重载预览。更值得读的，是它背后的问题：为什么偏偏是 Lottie，AI 才能真的「解」它？

---

## 先说结论：为什么偏偏是 Lottie？

这个问题比工具本身更值得想清楚。

**AI 能解一个创意领域，需要什么条件？**

1. **结果是结构化的**，不是像素图（AI 写字比画画稳）
2. **格式有明确规范**，词汇量有限（不是自由发挥，是填空）
3. **可以机械验证**，对不对一眼就知道（JSON 校验 + 帧截图）
4. **关注点可分离**：结构、时序、视觉属性各自独立，不是混在一起的泥

Lottie 恰好全部满足：

- 它是 **JSON**，不是二进制，AI 天然擅长写
- Lottie spec 的核心元素类型只有约 20-30 种，全部有文档
- 同一份 JSON 在任何平台（Web/iOS/Android/Flutter）渲染结果确定
- 帧可以 pin：`?frame=60&paused=1`，截图验证，完全可自动化

这就是为什么同样的 AI，写 Photoshop 动画大概率一塌糊涂，写 Lottie JSON 却能生成「可上线」的结果。**不是 AI 更懂动画，是 Lottie 给了 AI 一个它能够发挥的操场。**

---

## 这个 Skill 是什么

`diffusionstudio/lottie` 的定位是：**一个给编码 Agent 用的 Lottie 生成 harness（脚手架 + 运行环境）**。

它做了三件事：
1. 提供一个 **SKILL.md**，告诉 Claude Code / Codex 怎么写合法的 Lottie JSON（格式规范、禁忌、checklist）
2. 提供一个 **本地预览播放器**（Skia CanvasKit / Skottie，非浏览器原生 Canvas，精准还原 AE 导出效果）
3. **热重载**：Agent 把 JSON 写进 `public/lottie.json`，Dev Server 立刻刷新播放，所见即所得

换句话说：**Agent 是编剧，你是导演，这个框架是片场**。

---

## 安装：两种方式

### 方式一：作为 Skill 安装（推荐）

```bash
npx skills add diffusionstudio/lottie
```

适合已经在用 Claude Code 或其他支持 Skill 的 Agent 工具，装好后直接在对话里触发。

### 方式二：脚手架一个新项目

```bash
npx degit diffusionstudio/lottie my-animation
cd my-animation
npm install && npm run dev
```

这会克隆整个框架，包含 Skottie 播放器和 React + TypeScript 控制组件。适合想本地完整调试的开发者。

浏览器打开 `http://localhost:5173`，就能看到实时预览。

---

## 工作流：Agent 怎么工作

整个流程非常清晰：

```
你的文字描述
    ↓
Agent 读取 SKILL.md（知道 Lottie 规范）
    ↓
Agent 生成 public/lottie.json
    ↓
Dev Server 热重载
    ↓
浏览器实时看到动画
    ↓
不满意 → 继续描述调整
    ↓
满意 → 导出给 Web/iOS/Android/Flutter 直接用
```

验证某一帧的方法：

```
http://localhost:5173?frame=60&paused=1
```

这个 URL 参数可以 pin 到任意帧，截图验证，也可以写进自动化测试。

---

## 怎么写出好的 Prompt？四个策略

### 策略一：给模型具体资产，不要空想

```
❌ 给我一个心形弹跳动画

✅ 用这个 SVG 路径（[粘贴路径]）做一个心形，
   进场时从 scale 0 弹出到 scale 1.2 再回到 1.0，
   ease-in-out 时序，24fps，60帧，透明背景
```

有 SVG、截图、真实数据作为素材时，效果显著更好。

### 策略二：用动效设计语言说话

专业术语对 AI 是明确指令，不是装腔作势：

- `ease-in`（由慢到快）、`ease-out`（由快到慢）、`ease-in-out`（慢-快-慢）
- `overshoot`（弹性越界）、`anticipation`（预备动作）
- `follow-through`（追随惯性）、`staging`（主体聚焦）

这是迪士尼12条动画原则的语言，SKILL.md 里 Agent 认得。

### 策略三：像摄影师一样思考镜头

```
✅ 从俯视拉近到正面（推镜头），同时图标从模糊到清晰，
   整体 1.5 秒，前 0.3 秒停顿建立焦点
```

### 策略四：明确说出你要可控的属性

SKILL.md 要求每个动画都暴露背景色控制。你可以要求更多：

```
✅ 把主色、动画速度、图标大小都做成可以实时调整的 slot，
   这样设计师能在 dashboard 里直接调参数，不用重新生成
```

---

## 三个必须知道的技术陷阱

这是 README 最值得读的部分，也是最多人踩坑的地方。

### 陷阱一：Shape 必须包在 Group 里

Skottie（Lottie 的底层渲染器）要求：**所有形状基元（矩形、圆形、路径）必须被包在 `ty: "gr"` 的 Group 层里**，不能直接平铺在 `shapes` 数组里。

```json
// ❌ 错误：直接在 shapes 里放矩形 → 渲染空白
"shapes": [{ "ty": "rc", "s": {"a": 0, "k": [100, 100]} }]

// ✅ 正确：包进 Group 的 it 数组，末尾加 transform
"shapes": [{
  "ty": "gr",
  "it": [
    { "ty": "rc", "s": {"a": 0, "k": [100, 100]} },
    { "ty": "fl", "c": {"a": 0, "k": [1, 0.2, 0.2, 1]} },
    { "ty": "tr", ... }
  ]
}]
```

平铺写法不报错，但渲染一片空白。

### 陷阱二：颜色是 0-1 不是 0-255

```json
// ❌ 错误
"c": {"a": 0, "k": [255, 50, 50, 255]}

// ✅ 正确（归一化 RGBA）
"c": {"a": 0, "k": [1, 0.196, 0.196, 1]}
```

### 陷阱三：keyframe 的 s 值必须是数组

```json
// ❌ 错误
{"t": 0, "s": 100}

// ✅ 正确
{"t": 0, "s": [100]}
```

SKILL.md 里有完整的 Pre-Finalization Checklist，让 Agent 在输出前自检，通常能自动规避这三个坑。

---

## 交互式控制：让动画有「旋钮」

生产级动画通常需要设计师能调参，而不是每次改参数都重新生成。Lottie Slot 系统可以做到这一点：

在 JSON 顶层声明 slot：
```json
{
  "slots": {
    "primaryColor": {"p": {"a": 0, "k": [0.2, 0.6, 1, 1]}}
  }
}
```

在 layer 里引用：
```json
{"ty": "fl", "c": {"sid": "primaryColor"}}
```

配套 `public/controls.json` 定义 UI 标签和滑块范围，就能在 dashboard 里实时拖动调整，不需要重新运行 Agent。

---

## 产出可以用在哪

生成的 `lottie.json` 直接可用于：

| 平台 | 库 |
|---|---|
| Web | lottie-web / @lottiefiles/dotlottie-web |
| React | react-lottie / lottie-react |
| React Native | lottie-react-native + Skia |
| iOS Swift | lottie-ios |
| Android Kotlin | lottie-android |
| Flutter | lottie-flutter |

也可以导入 After Effects（通过 Bodymovin 插件）做进一步精修，再导出。

---

## 和 LottieFiles AI 有什么区别

| 维度 | diffusionstudio/lottie | LottieFiles AI |
|---|---|---|
| 部署方式 | 本地 / 私有 | 云端 SaaS |
| 控制粒度 | 完整 JSON 控制 | 生成后有限编辑 |
| 与 Agent 集成 | 原生 Skill（Claude/Codex） | 无 Agent 原生接口 |
| 成本 | 只花 LLM token | 订阅费用 |
| 开源 | MIT ✅ | ❌ |
| 适合场景 | 工程师 + 精细控制 | 设计师 + 快速出图 |

---

## 小结：AI 能解创意领域的条件

回到开头的问题。

`diffusionstudio/lottie` 之所以能用，不是因为 AI「懂动画」，而是因为：

- Lottie JSON 是**有限词汇的结构化语言**
- Agent 读了 SKILL.md 就知道**规则是什么**
- 热重载播放器让**验证成本极低**（看一眼就知道对不对）
- Slot 系统让**人工精调成本也低**（不用重新生成）

这个组合，让一个原本"感性"的创意产出——矢量动效——变成了一个 AI 可以可靠生成的工程产物。

**这个模式值得借鉴**：如果你也在某个领域想引入 AI 生成，先问自己：我能把这个领域的输出，变成 Lottie JSON 这样——结构化、规范有限、可机械验证——的格式吗？能的话，AI 就能解它。

---

> 相关资源（请手动访问）：
> GitHub 主仓库：https://github.com/diffusionstudio/lottie
> LottieFiles 官方 AI 工具：https://lottiefiles.com/ai
> OmniLottie（CVPR 2026 多模态生成）：https://github.com/OpenVGLab/OmniLottie
> LottieFiles motion-design-skill：https://github.com/lottiefiles/motion-design-skill

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> **BLUF**: `diffusionstudio/lottie` is an open-source skill harness letting Claude Code or Codex generate production-ready Lottie animation JSON from a single prompt. 2.4k ★, MIT, one-line install, hot-reload preview. More interesting: it illustrates exactly *why* Lottie is a creative domain AI can actually solve.

---

## Why Lottie — Not Figma, Not After Effects?

AI can reliably solve a creative domain when:

1. **Output is structured**, not pixels
2. **Format has a finite vocabulary** (fill-in-the-blanks, not free improvisation)
3. **Results are mechanically verifiable** (JSON validation + frame screenshot)
4. **Concerns are separable**: structure, timing, visual properties are independent

Lottie checks every box. It's JSON. The spec has ~20-30 core element types, all documented. The same JSON renders identically on any platform. You can pin any frame with `?frame=60&paused=1` and screenshot it. AI doesn't "understand" animation — it just turns out Lottie is a language it can write reliably.

---

## What the Skill Does

`diffusionstudio/lottie` provides:
1. A **SKILL.md** that tells the agent how to write valid Lottie JSON (rules, forbidden patterns, pre-finalization checklist)
2. A **local preview player** built on Skia CanvasKit / Skottie — the same renderer used by Telegram and dozens of apps
3. **Hot reload**: agent writes `public/lottie.json`, browser refreshes instantly

Agent is the scriptwriter. You're the director. This repo is the film set.

---

## Install

```bash
# As a skill (works with Claude Code, Codex, etc.)
npx skills add diffusionstudio/lottie

# Or scaffold a fresh project
npx degit diffusionstudio/lottie my-animation
cd my-animation && npm install && npm run dev
```

---

## 4 Prompting Strategies

**1. Ground with real assets** — paste the SVG path, not "a heart shape"

**2. Speak motion design language** — ease-in/out, overshoot, anticipation, follow-through. These aren't fancy words; they're precise instructions the agent understands.

**3. Think cinematically** — "pull back from close-up to wide, 1.5 seconds, 0.3s hold at start"

**4. Declare what should be a slot** — "make primary color, speed, and icon size adjustable in the dashboard so the designer can tweak without re-running the agent"

---

## 3 Technical Traps

**Trap 1: Shapes must be wrapped in a Group**
Flat shape arrays render blank in Skottie. Every shape primitive needs to live inside a `"ty": "gr"` group with a trailing `"ty": "tr"` transform.

**Trap 2: Colors are 0–1 RGBA, not 0–255**
`[1, 0.196, 0.196, 1]` = opaque red. Passing `[255, 50, 50, 255]` silently produces wrong output.

**Trap 3: Keyframe `s` values must be arrays**
`{"t": 0, "s": 100}` is wrong. `{"t": 0, "s": [100]}` is correct.

The SKILL.md includes a pre-finalization checklist the agent runs before output — catches most of these automatically.

---

## Output Targets

Generated `lottie.json` runs on Web (lottie-web), React, React Native + Skia, iOS Swift, Android Kotlin, and Flutter. Also importable into After Effects for manual refinement.

---

## The Pattern Worth Borrowing

The reason this works is a design pattern, not a magic AI capability:

Structured format + finite vocabulary + cheap mechanical verification + low human adjustment cost = a creative domain AI can reliably solve.

If you're introducing AI generation into any domain, ask yourself: can I make the output look like Lottie JSON — structured, bounded, verifiable? If yes, AI can solve it.

---

> GitHub: https://github.com/diffusionstudio/lottie
> MIT license. One-line install. Try it on your next icon animation.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
