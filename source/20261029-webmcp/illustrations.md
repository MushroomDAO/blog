# WebMCP 小M正文配图：来源与 QA

- 日期：2026-10-29；本轮使用内置 `image_gen`，逐张生成三幅独立图片；第 03 张另做一次构图修正，最终交付恰好三张。
- 正文：`src/content/blog/webmcp-chrome-browser-tools-api-guide.md`。阅读中英正文；原文 Git blob：`e98e5d49d6c6dbaea46a71ca6bde89db2f3cf5d3`。
- 已读参考：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md` 及其 `references/{style-dna,mushroom-ip,composition-patterns,prompt-template,qa-checklist}.md`；同时读取系统 `imagegen/SKILL.md`。未复刻示例图。
- 原始生成目录：`/Users/jason/.codex/generated_images/01a18691-2775-7892-a172-e2856ae0d396/`；原文件全部保留。模型版本未由工具暴露，不作推断。

| 图 | 最终文件（src/assets/images/ 下） | 尺寸 | 大小 | 采用的原始文件 |
|---|---|---|---|---|
| 01 | webmcp-chrome-browser-tools-api-guide-fig-01.png | 1536×864 | 71,943 B | exec-5d1f19fd-2780-43ef-875f-acc73727726c.png |
| 02 | webmcp-chrome-browser-tools-api-guide-fig-02.png | 1536×864 | 83,679 B | exec-9d5d3c92-7ac9-43b2-9996-26c728ef0319.png |
| 03 | webmcp-chrome-browser-tools-api-guide-fig-03.png | 1536×864 | 65,692 B | exec-86ca5c82-de19-4c07-9822-42143267c0b0.png |

## QA

- 01：小M实际操作由同一网站连接出来的能力面板；“网站声明 / 查库存 / 筛选 / 原入口可用”可读。原网页按钮及指针保留，没有截图历史对比或所有网站自动接入的暗示。
- 02：小M把工具卡挂在原表单旁；两组“商品 / 数量”空槽对应，“手动查询”按钮未按下。原表单无覆盖，未出现代码、自动提交或成功状态。
- 03：小M检查“仅订单A”的钥匙；“授权核验”与独立“确认”闸柄都在提交之前。工具卡与纸条分别注明“工具卡≠授权”“只读提示≠权限”，未充当锁或通行证。闸门关闭、包裹未移动。
- 构图：三幅各讲一个动作，红帽白点、米白身体、黑点眼；白底与充足留白，无标题、banner 或拼贴。03 首版闸门出框，修正后整体入框；“提交”两字可辨，栏杆位于字间。
- 文字：压缩后的三个实际文件均经 `view_image` 逐张目视检查；中文标签无明显错字，关键文字未出框。没有声称进行 OCR 或额外模型验证。
- 文件检查：PNG 解码成功；严格 16:9；每张小于 **90,000 字节**。Pillow LANCZOS 调整到 1536×864，MEDIANCUT 无抖动索引色压缩（128 / 96 / 128 色）；近白调色板项（RGB 各通道 ≥246）归白并合并重复颜色，PNG optimize / level 9。未绘制或改写图中内容。
- 范围：本任务仅写入指定三张 PNG 与本记录；未修改文章、demo、封面，未部署或提交。
- 并发状态：末次核验时正文 blob 已变为 `c2b1d53a6b8ad91e6c459be5311e64c129940797`，与开始读取时不同；本任务未写入正文，也未覆盖或还原该外部变化。图片规格及哈希验证独立通过。

## 最终文件 SHA-256

```text
01  9e260baca1aa82a458741dc22ea32f00cd0583900e25ee50e51112ecda9be170
02  6dffbe586a01f1e2138f40f22cd16dd7ffa776f76ac3a73610b18e17525299b0
03  706b943afed324fde2e1cc4e69155d4f4d659cd7e3ead71bf3874bc59f67b9c2
```

<details>
<summary>生成提示词（原文；用于复核与重做）</summary>

三张均使用以下公共提示词，加上各自场景：

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article illustration, exactly 1536x864 if possible. Not a banner, no collage or multiple panels.
Pure white (#FFFFFF) background; minimalist thin black hand-drawn slightly wobbly pen lines, sparse orange/blue/red Chinese handwritten annotations. Large calm whitespace, at least 40% blank, generous safe margins. Flat color only. No shadows, gradients, paper texture, dense diagram, PPT, commercial vector art, realistic screenshot, title or top-left heading.
XiaoM is the core worker: small mushroom with RED dome cap, 3–5 WHITE spots, CREAM stem body, black outline and BLACK dot eyes, thin arms/legs, blank serious deadpan expression. Not black-filled, not cute, no smile or costume. XiaoM must physically perform the conceptual action. Muted sparse blue notes, orange only for connections/flow, red for cap and warnings. All labels large and clearly readable, no other words or pseudo-text. Invent a simple absurd physical product-sketch scene rather than a formal flowchart.
```

### 01

```text
Scene: A single website browser-window object is like a small workshop counter. Its normal front has three simple anonymous buttons and an accessible mouse pointer; this normal UI entrance stays OPEN and connected, never crossed out. XiaoM stands centrally, actively using a hanging capability panel supplied by this ONE website, finger on a named capability row. A thin orange cord visibly connects panel back to the same site. Panel has two named rows for clear business capabilities, contrasting the anonymous buttons without depicting a failed former era. Panel is deliberately installed by this site, not magically available everywhere. Use only these exact Chinese labels: “网站声明” beside the panel's attachment, “查库存” and “筛选” on its two rows, “原入口可用” beneath the unobstructed normal web UI. No screenshots, camera icons, before/after arrows, universality claims, checkmarks of guaranteed success, or suggestion that old automation only used pixels.
```

### 02

```text
Scene: A normal human-facing paper-like browser form stands upright, two clearly usable empty input fields and one unpressed manual button. Beside it XiaoM is physically adding a separate hanging tool card to a small peg on the form's outside edge; card must not overlay, replace, block or detach the form. Two simple parameter slots on the card correspond naturally to the form's two fields, joined by two short thin orange connections. XiaoM is attaching the card, NOT pressing the submit button. The human mouse pointer stays next to the original manual button; no submission or success is shown. Use only these exact Chinese labels: “原表单”, “商品”, “数量”, “手动查询” on the form; “工具卡”, “商品”, “数量” on the card. No programming code, attribute names, braces, HTML, auto-submit claim, magic conversion, or labels suggesting a tool call has executed.
```

### 03

```text
Scene: XiaoM actively checks a small physical KEY with a narrowly scoped blue tag before a consequential business action. The key is separate from a plain tool card resting nearby. XiaoM holds the scoped key up to a small access-check keyhole on a CLOSED gate; this keyhole visibly comes before a separate red confirmation latch on the same gate. Beyond the closed gate is a modest sealed parcel representing the consequential action, still unmoved. A cursor/hand must explicitly operate the confirmation latch in the future; no autonomous crossing, no final success check. The ordinary rectangular tool card has NO key teeth, NO permission badge, NO keyhole fit. Its read-only note is visibly just a paper hint, never a lock, shield or barrier. Use only these exact Chinese labels: “仅订单A” on the KEY tag; “授权核验” beside the keyhole; “确认” on the red latch; “提交” on the parcel beyond; “工具卡≠授权” on the plain card; “只读提示≠权限” as a small blue paper note by the card. Clear scoped authorization and explicit confirmation remain required. No impression that a tool description grants permission or that read-only annotations enforce it.
```

03 初版：`exec-685c24ee-7dc8-4504-a386-495cb61fa26f.png`（同一原始目录）。以下编辑以此为唯一参考图，改善构图后采用上表的最终版本：

```text
Edit this third illustration only; it remains ONE standalone 16:9 white hand-drawn XiaoM article illustration. Correct framing and legibility: recompose the SAME scene smaller and centered with at least 8% white margin on ALL sides; show the ENTIRE closed gate including its top and right boundary, no cut objects. Keep gate modest in height. Place the sealed parcel just beyond the gate with its “提交” label fully readable, NOT overlapped by any gate bars. Preserve all six labels verbatim and readable: “仅订单A”, “授权核验”, “确认”, “提交”, “工具卡≠授权”, “只读提示≠权限”. Preserve XiaoM actively checking the SCOPED KEY at the separate authorization keyhole BEFORE the still-unoperated confirmation latch. Gate remains CLOSED, parcel unmoved, no claim of completed submission. Tool card and read-only note remain separate pieces of paper, not security controls. Preserve red cap/white spots, cream body, deadpan expression and sparse thin black hand-drawn look. Make canvas background truly pure flat WHITE with flat fills, no shading or texture. No added objects, code, titles, borders, panels or collage. Main content should occupy at most 60% of canvas area; lots of clean whitespace.
```

</details>
