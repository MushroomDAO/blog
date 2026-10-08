---
title: "一张桌子，十个宇宙：Evan Jia 的 Blender 个人主页开源了"
titleEn: "One Desk, Ten Universes: Evan Jia's Blender Personal Website Goes Open Source"
description: "Evan Jia（贾岱林，AI PM × Agent Builder）开源了个人主页 EdwinjJ1/personal-website（MIT）。核心概念「一张桌子，十个宇宙」：一个 Blender 渲染的桌面场景，通过三步 Python 流水线生成十种视觉风格（水墨、网版印刷、漫画、交叉线、点阵……），WebGL 热区映射把桌上的物件直接变成导航入口。设计亮点：改文案、项目、照片不需要重新渲染，只改 site/js/content.js 和 JSON 文件；换桌上的物件只改一个 blender/layout.py，再跑 10 分钟渲染。整套静态输出，Cloudflare Pages 部署，外加一个 Cloudflare Worker 驱动 AI 聊天。灵感来自抖音 @硕哥，梦想哭了，用 Claude + Blender 5.x 实现。"
descriptionEn: "Evan Jia (AI PM × Agent Builder) open-sourced his personal website EdwinjJ1/personal-website (MIT). Core concept — 'One Desk, Ten Universes': a single Blender-rendered desk scene processed through a three-step Python pipeline to produce ten distinct visual art styles (ink wash, halftone, comic, hatching, dot matrix…), with WebGL hotspots mapping desk objects directly to navigation panels. Design insight: text content and project listings require no re-render — just edit site/js/content.js and JSON files. Changing desk objects requires editing one file (blender/layout.py) and a ~10-minute render. Fully static output, Cloudflare Pages deploy, Cloudflare Worker for AI chat. Inspired by Douyin creator @硕哥梦想哭了, built with Claude + Blender 5.x."
pubDate: 2026-10-08
heroImage: "../../assets/images/personal-website-blender-webgl-ten-universes-render-pipeline-banner.jpg"
category: "Tech-Experiment"
tags: ["前端工具", "开源工具", "Blender", "WebGL", "创意工具", "个人网站"]
lang: "zh-CN"
wechatTitle: "一张桌子十个宇宙：Blender个人主页开源"
wechatDigest: "MIT；Blender渲染+WebGL热区；10种视觉风格；换文案不重渲染；换桌面物体改layout.py"
---

个人主页里"桌上的东西"通常只是装饰。这个项目把它们变成了导航。

Evan Jia（贾岱林，AI PM × Agent Builder）开源了自己的个人主页：一个 Blender 渲染的桌面场景，点击桌上的每件物品，打开对应的项目、博客或经历介绍。整个场景同时存在于十种不同的视觉风格里，可以切换。

GitHub: https://github.com/EdwinjJ1/personal-website | ⭐ 22 | MIT | 演示：evanlin.site

灵感来自抖音创作者 **@硕哥，梦想哭了**，用 Claude + Blender 5.x 实现。

---

## 「一张桌子，十个宇宙」

同一张桌子，十种视觉宇宙：水墨风、网版印刷、漫画线稿、素描排线、点阵……每种风格都是完整的视觉世界，切换是瞬间的，内容完全一致。

这不是同一张图的颜色变体，而是通过**分层渲染和后处理合成**重新生成的：每种风格有自己的线条来源、光照映射、纸张纹理和调色方案。

---

## 技术管线：三步走

```
npm run textures  →  npm run render  →  npm run stylize
```

**第一步：生成纹理材质**

`pipeline/textures.py` 生成桌面上的印刷品：软木板上的便利贴、书封面、屏幕内容、杂志剪报。输出到 `blender/tex/`。

**第二步：Blender 多通道渲染**

Blender 5.x 渲染场景的**分离通道**，不是最终图像：

| 通道 | 用途 |
|------|------|
| Base color | 基础颜色信息 |
| Emission | 发光体（屏幕、灯） |
| Per-object ID | 每个物件的唯一标识 → 热区地图 |
| Normals | 法线信息 → 描边来源 |
| Depth | 景深 |
| 5 个分离光组 | 各方向光照独立输出 |

在 M1 Max 上完整 4K 渲染约 10 分钟；以 1600px 宽测试样式更快。

**第三步：风格合成**

`pipeline/stylize.py` 把这些通道合成为十种视觉风格：
- 用法线/深度通道提取边缘 → 水墨/线稿效果
- 用量化光照通道叠加 → 网版半调/排线阴影
- 每种风格有独立调色盘和纸张纹理叠层

同时，**Object ID 通道单独导出为热区地图**，WebGL 用它检测鼠标悬停和点击，把物件映射到对应页面模块。

最终输出：纯静态 HTML + WebGL，Cloudflare Pages 部署。

---

## 最聪明的设计：内容和渲染分离

**改文案、项目、照片不需要重渲染。**

```
site/js/content.js   ← 所有面板文字、AI 聊天端点
site/assets/data/    ← 项目列表、博客文章、友链、照片（JSON 文件）
```

修改这些文件是纯前端改动——不需要碰 Blender，不需要跑 Python，直接推送即可部署。

**换桌上的物件，只改一个 Python 文件。**

```python
# blender/layout.py
# 每个物件：模型路径、位置、旋转、缩放、热区名
objects = [
    {"model": "book.blend", "pos": (0.3, 0.1, 0), "hot": "projects"},
    {"model": "globe.blend", "pos": (-0.2, 0.3, 0), "hot": "about"},
    ...
]
```

`hot` 值对应 `content.js` 里的 `HOTS` 和 `LABELS` 表——改完跑一次渲染，新物件就出现在页面上，对应的热区自动生效。测试套件会验证热区注册是否完整。

---

## 其他模块

**AI 聊天**：`workers/api/` 是一个 Cloudflare Worker，提供网站上的 AI 对话功能，`content.js` 里的 `CHAT.api` 字段指定接口地址。

**音乐播放列表**：`pipeline/sync_music.py` 同步音乐列表，通过 `PLAYLIST_ID` 配置。

**自动部署**：GitHub Actions 在推送 `main` 后自动部署到 GitHub Pages。

---

## 制作思路图

项目 README 附了一张 `002/preview/how-its-made.jpg`（制作思路），展示了从 Blender 多通道输出到风格合成再到 WebGL 热区的完整数据流。如果你要理解管线里每一步的数据格式和依赖关系，这张图是最快的入口。

---

## 适合谁 fork

这个仓库对以下情况有参考价值：

- 想把个人主页做得不一样、用 3D 场景取代标准布局的开发者
- 了解 Blender 渲染管线 + Python 合成流程的人（硬门槛：需要 Blender 5.x 和 `uv`）
- 对「内容与渲染分离」这个设计模式感兴趣的人

⚠️ 现实提示：照片、文字和本人形象保留作者版权，仅代码 MIT。1.7 GB 仓库包含原始照片，clone 要有心理准备。修改桌面物件需要有 Blender 环境。

---

> MIT 许可（仅代码）。EdwinjJ1/personal-website，Evan Jia 开发。灵感来自抖音 @硕哥，梦想哭了。开源仅供学习参考。

---

<!--EN-->

## One Desk, Ten Universes: Evan Jia's Blender Personal Website Goes Open Source

On most personal websites, desk objects are decoration. This one turns them into navigation.

Evan Jia (AI PM × Agent Builder) open-sourced his personal site: a Blender-rendered desk scene where clicking each object on the desk opens the corresponding project, blog post, or bio section. The same scene exists in ten distinct visual art styles that can be switched between instantly.

GitHub: https://github.com/EdwinjJ1/personal-website | ⭐ 22 | MIT | Demo: evanlin.site

Inspired by Douyin creator @硕哥梦想哭了, built with Claude + Blender 5.x.

---

### The Concept

Ten visual universes, one desk: ink wash, halftone print, comic line art, cross-hatching, dot matrix… Each style is a complete visual world. Switching is instant; content is identical.

These aren't color variants of the same image — they're generated through layered rendering and compositing, each style with its own line sources, lighting mappings, paper textures, and palette.

---

### Three-Step Pipeline

```
npm run textures  →  npm run render  →  npm run stylize
```

**Step 1: Generate textures**
`pipeline/textures.py` generates printed materials for the desk: corkboard sticky notes, book covers, screen content, magazine clippings. Output to `blender/tex/`.

**Step 2: Multi-pass Blender render**
Blender 5.x renders separate passes — not a final image:

| Pass | Used for |
|------|---------|
| Base color | Color info |
| Emission | Glowing surfaces (screens, lamps) |
| Per-object ID | Unique ID per object → hotspot map |
| Normals | Edge extraction for outlines |
| Depth | Depth of field |
| 5 light groups | Separate directional lighting |

Full 4K render: ~10 minutes on M1 Max. Testing at 1600px is faster.

**Step 3: Stylize**
`pipeline/stylize.py` composites the passes into ten art styles:
- Normals/depth → edge lines (ink/line art effects)
- Quantized lighting → halftone/hatching shading
- Per-style palette and paper texture layers

The Object ID pass is separately exported as the **hotspot map** that WebGL uses to detect hover and click, mapping desk objects to page modules.

Final output: pure static HTML + WebGL, deployed to Cloudflare Pages.

---

### The Clever Part: Content Separated from Rendering

**Changing text, projects, and photos requires no re-render.**

```
site/js/content.js   ← all panel copy, AI chat endpoint
site/assets/data/    ← projects, posts, links, photos (JSON)
```

These are front-end only — no Blender, no Python, just push to deploy.

**Changing desk objects requires editing one Python file.**

```python
# blender/layout.py
objects = [
    {"model": "book.blend", "pos": (0.3, 0.1, 0), "hot": "projects"},
    {"model": "globe.blend", "pos": (-0.2, 0.3, 0), "hot": "about"},
    ...
]
```

The `hot` value maps to `HOTS` and `LABELS` in `content.js`. Edit the file, run the render, new objects appear with working hotspots. Tests verify hotspot registration automatically.

---

### Who Should Fork This

Useful if: you want a non-standard personal website using a 3D scene for navigation; you're comfortable with Blender 5.x + Python (`uv`); you're interested in the content/render separation pattern.

⚠️ Hard requirements: Blender 5.x environment for any desk modifications. The 1.7 GB repo includes original photos. Photos, personal image, and text are author-copyright — only code is MIT.

---

> MIT license (code only). EdwinjJ1/personal-website by Evan Jia. Concept inspired by Douyin creator @硕哥梦想哭了. For technical reference only.
