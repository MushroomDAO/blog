---
title: "PromptSoul：用自然语言给 Live2D 角色加动作，AI 不碰骨骼"
titleEn: "PromptSoul: Natural Language to Live2D Motion, AI Never Touches the Skeleton"
description: "promptwhisper/promptsoul 把聊天情绪到 Live2D 动作的链路完整打通：自然语言描述一个动作，AI 生成、严格校验、原子写入，只用模型已有参数，不碰网格骨骼绑定。TypeScript + Next.js，MIT 开源。"
descriptionEn: "promptwhisper/promptsoul closes the full loop from chat emotion to Live2D motion: describe a movement in natural language, AI generates it with strict validation and atomic write — using only the model's existing parameters, no mesh or rig modification. TypeScript + Next.js, MIT open-source."
pubDate: "2026-07-22"
updatedDate: "2026-07-22"
category: "Tech-Experiment"
tags: ["Live2D", "AI NPC", "动作生成", "Next.js", "TypeScript", "角色动画", "开源工具", "AI工具", "虚拟角色"]
heroImage: "../../assets/images/promptsoul-live2d-ai-motion-npc-banner.jpg"
---

> **仓库**：promptwhisper/promptsoul · TypeScript · MIT  
> **定位**：Local-first AI Live2D NPC，自然语言安全生成动作  
> **启动**：`npm ci && npm run setup:demo -- --accept-license && npm run dev`

---

## 一、问题：聊天和身体是割裂的

给 Live2D 角色接 AI 聊天，技术上不难——把消息发给 LLM，把回复显示出来，完成。

但有一个问题从来没被优雅地解决：**角色的身体不知道发生了什么。**

回复"好开心！"，角色面无表情。对话情绪在跳，Live2D 在原地站着。文字和身体是两个系统，互相不知道对方在做什么。

要修这个问题，又要面对第二个难题：**想新加一个动作，Live2D 参数是噩梦。**

参数 ID、曲线、物理绑定、基础姿势……研究半天，写出来的 JSON 可能让角色眼睛卡死或者整个扭曲。原有动作组被覆盖了，还不一定发现。

PromptSoul 把这两个问题一起解决了。

---

## 二、完整链路

```
用户消息
    ↓
Next.js 后端调用 AI Provider
    ↓
AI 返回：角色回复文字 + 情绪标签
    ↓
情绪标签 → 映射到 Live2D 动作
    ↓
角色说话 + 做动作（同步）
```

这是「聊天→情绪→动作」的基础链路，让角色的身体和对话内容同步。

第二层是「动作工坊」——用自然语言描述新动作，AI 生成，安全写入：

```
"先惊讶地睁大眼睛，轻轻后仰，再点头回到原位"
    ↓
AI 生成结构化 JSON（曲线、时序、参数值）
    ↓
严格校验（见下节）
    ↓
原子写入 PromptSoul 动作组
    ↓
模型重新加载 + 自动预览
```

---

## 三、安全设计：AI 不碰骨骼

这是 PromptSoul 最核心的设计决定，README 在最显眼的位置写着：

> AI 不会直接修改网格、骨骼或 Cubism 绑定。所有动作都只能使用模型已有参数，并且只能注册到项目自有的 `PromptSoul` 动作组。

具体约束：

**生成端**：AI 看到的是不透明控制编号、语义名称和标准化值——不是原始参数 ID，不是动作曲线，不是模型文件结构。原始数据不出后端。

**校验端**：严格拒绝：
- 任意代码（不执行 AI 生成的逻辑）
- 未知参数（只接受模型已有的）
- 物理输出参数（不干预物理引擎）
- `PartOpacity`（不做透明度操作）
- 越界值（参数范围由模型自身确定）
- 未回到基础姿势的曲线（动作结束时角色要回到初始状态）

**写入端**：原子写入，只更新 `PromptSoul` 组。模型原有的 `Action`、`Idle`、`Tap` 等动作组一个字节不动。

**无法实现时**：如果当前模型无法自然、安全地表达描述，接口返回「不可实现」，而不是强行写入不合适的参数。

---

## 四、快速上手

需要 Node.js 22+、npm、现代浏览器，不需要 Python。

```bash
npm ci

# 首次使用：阅读并接受 Live2D 条款后下载官方 Hiyori 样例
npm run setup:demo -- --accept-license

# 生成并验证内置动作
npm run motions:generate
npm run motions:validate

npm run dev
```

打开 `http://127.0.0.1:8765`。

**不配置 API Key 也能跑**：聊天使用确定性的本地演示回复，Live2D、已有动作和交互正常工作。动作工坊需要连接 AI Provider。

---

## 五、接入 AI Provider

页面右上角「AI Provider」设置，填写 OpenAI 兼容的 API 地址、模型名和 Key。支持任意 OpenAI 兼容服务：Claude、DeepSeek、本地 Ollama 等。

长期运行用环境变量：

```bash
export NPC_API_KEY="你的 API Key"
export NPC_API_BASE="https://api.openai.com/v1"
export NPC_MODEL="你的模型名"
npm start
```

| 变量 | 默认值 |
|---|---|
| `NPC_API_KEY` | 未设置时读取 `OPENAI_API_KEY` |
| `NPC_API_BASE` | `https://api.openai.com/v1` |
| `NPC_MODEL` | `gpt-5.6-luna` |

**Key 安全边界**：
- 浏览器只提交一次，不写 `localStorage`、Cookie、配置文件、Git
- 后端只在当前进程内存保存，重启自动清除
- Provider 配置只接受本机回环地址上的同源请求

---

## 六、动作工坊：写描述，看动作

连接 AI Provider 并导入模型后，页面底部的「动作工坊」自动启用。

输入描述：

```
先惊讶地睁大眼睛，轻轻后仰，再点头回到原位
```

后端流程：

1. 从模型原有动作估计安全参数范围和基础姿势
2. 只向 Provider 提供语义信息（不发送原始参数 ID 和动作曲线）
3. 校验 AI 返回的结构化 JSON
4. 原子写入，只更新 `PromptSoul` 组
5. 重新加载模型，自动预览结果

**动作存储**：
- AI 定义保存在 `motion-defs/generated/<model>/`（git 忽略）
- 运行文件保存在 `models/`（git 忽略）
- 每个模型最多 24 个 AI 动作
- 相同描述会更新同一个动作（幂等）

---

## 七、更换 Live2D 模型

```bash
npm run setup:model -- /path/to/model-folder-or.zip
npm run analyze:model
```

分析结果告诉你这个模型有哪些参数、安全范围和基础姿势。**必须先读分析结果，再为这个模型创建 `motion-defs/<model-name>.ts`**——不同模型的参数含义和安全范围完全不同，不能照搬。

```bash
npm run motions:generate
npm run motions:validate
npm run verify:browser  # 需要 Chrome
npm run dev
```

---

## 八、项目结构

```
app/                    Next.js 页面与 Route Handlers
components/             React UI（含内存 Key 设置面板）
lib/server/             Provider、聊天、模型和动作安全逻辑
scripts/                Node/TypeScript CLI
tests-node/             node:test 自动化测试
motion-defs/<model>.ts  模型专属基础动作定义（需手写）
motion-defs/generated/  本地 AI 动作定义（git 忽略）
npc.config.json         角色、欢迎语、快捷问题和署名
model.config.json       当前模型配置（本地生成，git 忽略）
```

---

## 九、部署注意事项

PromptSoul 需要读写本机模型工作副本，所以：

- **必须用 Node 自托管**，不能部署到 Edge 或无持久磁盘的 Serverless 运行时
- **绑定 `127.0.0.1`**，不要直接暴露到公网
- 生产构建显式使用 Next 的 Webpack 构建器，保持动态模型文件追踪可预测

```bash
npm run build
npm start
```

---

## 十、设计判断

**问题本身是真实的。** Live2D 角色接 AI 聊天，最常见的做法是把两者简单拼在一起——聊天走 API，动作走预设循环，两边互不知道对方在做什么。结果就是角色在说悲伤的话时跳着开心的待机动画。

**安全约束是关键设计。** 如果 AI 能直接写入任意 Live2D 参数，稍微偏一点就能让角色眼睛卡死、物理错乱、或者覆盖掉精心调好的原有动作组。PromptSoul 的「只用已有参数 + 只写 PromptSoul 组 + 严格校验」是正确的工程决策——不是限制，是让这个工具实际可用的前提。

**幂等更新和上限设计。** 相同描述更新同一个动作（而不是累积堆叠），每个模型上限 24 个 AI 动作——这两个决定让生成结果可管理，不会随时间越来越乱。

**本地优先是正确的定位。** Live2D 模型文件、角色设定、动作定义都在本地，不上传给第三方（角色设定和聊天内容会发给你配置的 Provider，但模型文件本身不出本机）。对需要保护原创角色的创作者来说，这是必须的。

**局限**：目前只支持 Cubism 4，模型专属的 `motion-defs` 需要手写（无法自动迁移），部署受运行时限制，动作生成速度取决于 Provider 延迟。

---

## 十一、适合什么场景

**原创 Live2D 角色开发者**：想给自己的角色加情绪联动，但不想每加一个动作都去翻 Cubism 参数文档的，动作工坊直接用自然语言描述即可。

**AI 对话角色原型**：做 VTuber 工具、AI 伴侣、游戏 NPC 原型的，PromptSoul 提供了情绪→动作映射的完整参考实现。

**Live2D + AI 技术研究**：项目里的「安全参数生成」方法——让 AI 只看到语义层、后端做校验和物理隔离——是一个值得参考的工程模式。

---

*数据来源：GitHub promptwhisper/promptsoul README，2026-07-22 采集。*

© 2026 Author: Mycelium Protocol

<!--EN-->

> **Repository**: promptwhisper/promptsoul · TypeScript · MIT  
> **Positioning**: Local-first AI Live2D NPC, safe natural-language motion generation  
> **Quick start**: `npm ci && npm run setup:demo -- --accept-license && npm run dev`

---

## 1. The Problem: Chat and Body Are Disconnected

Connecting a Live2D character to AI chat is technically straightforward — send the message to an LLM, display the reply, done.

But one problem has never been elegantly solved: **the character's body has no idea what's happening.**

The character replies "I'm so happy!" with a blank expression. The emotional arc of the conversation fluctuates, but the Live2D model stands perfectly still. Text and body are two separate systems with no awareness of each other.

Fixing this problem then runs into a second obstacle: **adding a new motion means wrestling with Live2D parameters, which is a nightmare.**

Parameter IDs, curves, physics bindings, base poses — after hours of research, the JSON you write might freeze the character's eyes or distort the entire model. The original motion groups could be overwritten without you even noticing.

PromptSoul solves both problems at once.

---

## 2. The Full Pipeline

```
User message
    ↓
Next.js backend calls AI Provider
    ↓
AI returns: character reply text + emotion tag
    ↓
Emotion tag → mapped to Live2D motion
    ↓
Character speaks + moves (synchronized)
```

This is the foundational "chat → emotion → motion" pipeline, keeping the character's body in sync with the conversation.

The second layer is the "Motion Workshop" — describe a new motion in natural language, AI generates it, and it is safely written:

```
"Eyes wide with surprise, lean back slightly, then nod back to neutral"
    ↓
AI generates structured JSON (curves, timing, parameter values)
    ↓
Strict validation (see next section)
    ↓
Atomic write to the PromptSoul motion group
    ↓
Model reloads + auto-preview
```

---

## 3. Safety Design: AI Never Touches the Skeleton

This is PromptSoul's most fundamental design decision, stated prominently in the README:

> AI does not directly modify meshes, bones, or Cubism bindings. All motions may only use the model's existing parameters, and may only be registered in the project's own `PromptSoul` motion group.

Specific constraints:

**Generation side**: What the AI sees are opaque control identifiers, semantic names, and normalized values — not raw parameter IDs, not motion curves, not the model file structure. Raw data never leaves the backend.

**Validation side**: Strict rejection of:
- Arbitrary code (no AI-generated logic is executed)
- Unknown parameters (only the model's existing ones are accepted)
- Physics output parameters (no interference with the physics engine)
- `PartOpacity` (no opacity manipulation)
- Out-of-range values (parameter bounds are determined by the model itself)
- Curves that do not return to the base pose (the character must return to its initial state when a motion ends)

**Write side**: Atomic write, updating only the `PromptSoul` group. The model's original `Action`, `Idle`, `Tap`, and other motion groups are not touched — not a single byte.

**When infeasible**: If the current model cannot express the description naturally and safely, the API returns "not achievable" rather than forcing inappropriate parameters.

---

## 4. Quick Start

Requires Node.js 22+, npm, and a modern browser. No Python needed.

```bash
npm ci

# First-time setup: read and accept the Live2D terms, then download the official Hiyori sample
npm run setup:demo -- --accept-license

# Generate and validate built-in motions
npm run motions:generate
npm run motions:validate

npm run dev
```

Open `http://127.0.0.1:8765`.

**Works without an API Key**: Chat uses deterministic local demo replies; Live2D, existing motions, and interactions all work normally. The Motion Workshop requires a connected AI Provider.

---

## 5. Connecting an AI Provider

Click "AI Provider" in the top-right corner of the page and enter an OpenAI-compatible API endpoint, model name, and key. Any OpenAI-compatible service is supported: Claude, DeepSeek, local Ollama, and more.

For long-running use, set environment variables:

```bash
export NPC_API_KEY="your API key"
export NPC_API_BASE="https://api.openai.com/v1"
export NPC_MODEL="your model name"
npm start
```

| Variable | Default |
|---|---|
| `NPC_API_KEY` | Falls back to `OPENAI_API_KEY` if unset |
| `NPC_API_BASE` | `https://api.openai.com/v1` |
| `NPC_MODEL` | `gpt-5.6-luna` |

**Key security boundary**:
- Submitted by the browser once only — never written to `localStorage`, cookies, config files, or git
- Backend holds it in current-process memory only; cleared on restart
- Provider configuration only accepts same-origin requests from the local loopback interface

---

## 6. Motion Workshop: Describe It, Watch It Move

Once an AI Provider is connected and a model is loaded, the "Motion Workshop" at the bottom of the page activates automatically.

Enter a description:

```
Eyes wide with surprise, lean back slightly, then nod back to neutral
```

Backend process:

1. Estimate safe parameter ranges and base pose from the model's existing motions
2. Send only semantic information to the Provider (raw parameter IDs and motion curves are not transmitted)
3. Validate the structured JSON returned by AI
4. Atomic write, updating only the `PromptSoul` group
5. Reload the model and auto-preview the result

**Motion storage**:
- AI definitions saved to `motion-defs/generated/<model>/` (git-ignored)
- Runtime files saved to `models/` (git-ignored)
- Maximum 24 AI-generated motions per model
- Identical descriptions update the same motion (idempotent)

---

## 7. Switching the Live2D Model

```bash
npm run setup:model -- /path/to/model-folder-or.zip
npm run analyze:model
```

The analysis output tells you which parameters the model has, their safe ranges, and its base pose. **You must read the analysis output before creating `motion-defs/<model-name>.ts` for this model** — parameter semantics and safe ranges differ entirely between models; you cannot copy one over from another.

```bash
npm run motions:generate
npm run motions:validate
npm run verify:browser  # requires Chrome
npm run dev
```

---

## 8. Project Structure

```
app/                    Next.js pages and Route Handlers
components/             React UI (includes in-memory Key settings panel)
lib/server/             Provider, chat, model, and motion safety logic
scripts/                Node/TypeScript CLI
tests-node/             node:test automated tests
motion-defs/<model>.ts  Model-specific base motion definitions (hand-written)
motion-defs/generated/  Local AI motion definitions (git-ignored)
npc.config.json         Character, welcome message, quick questions, and attribution
model.config.json       Current model configuration (generated locally, git-ignored)
```

---

## 9. Deployment Notes

PromptSoul requires read/write access to a local working copy of the model, so:

- **Must be self-hosted with Node** — cannot be deployed to Edge or Serverless runtimes without persistent disk
- **Bind to `127.0.0.1`** — do not expose directly to the public internet
- Production builds explicitly use Next.js's Webpack builder to keep dynamic model file tracking predictable

```bash
npm run build
npm start
```

---

## 10. Design Judgments

**The problem itself is real.** The most common approach to connecting a Live2D character with AI chat is to simply bolt the two together — chat goes through an API, motions run on a preset loop, and neither side knows what the other is doing. The result: the character plays a cheerful idle animation while delivering sad dialogue.

**Safety constraints are the key design.** If AI could write arbitrary Live2D parameters directly, even a slight deviation could freeze the character's eyes, corrupt physics, or overwrite a carefully tuned original motion group. PromptSoul's "only use existing parameters + only write to the PromptSoul group + strict validation" approach is the correct engineering decision — not a limitation, but the prerequisite that makes the tool actually usable.

**Idempotent updates and a hard cap.** Identical descriptions update the same motion (rather than accumulating stacks), and each model is capped at 24 AI-generated motions — these two decisions keep generated output manageable and prevent it from growing more chaotic over time.

**Local-first is the right positioning.** Live2D model files, character definitions, and motion definitions all stay local and are never uploaded to third parties (character settings and chat content are sent to your configured Provider, but the model files themselves never leave the machine). For creators who need to protect their original characters, this is essential.

**Limitations**: Currently only supports Cubism 4, model-specific `motion-defs` require hand-authoring (no auto-migration), deployment is constrained by runtime requirements, and motion generation speed depends on Provider latency.

---

## 11. Suitable Use Cases

**Original Live2D character developers**: If you want to add emotion-linked motions to your character but don't want to dig through Cubism parameter documentation every time, the Motion Workshop lets you describe motions in natural language directly.

**AI conversational character prototypes**: For those building VTuber tools, AI companions, or game NPC prototypes, PromptSoul provides a complete reference implementation of the emotion → motion mapping pipeline.

**Live2D + AI technical research**: The "safe parameter generation" approach used in this project — letting AI see only the semantic layer while the backend handles validation and physics isolation — is an engineering pattern worth referencing.

---

*Data source: GitHub promptwhisper/promptsoul README, collected 2026-07-22.*

© 2026 Author: Mycelium Protocol
