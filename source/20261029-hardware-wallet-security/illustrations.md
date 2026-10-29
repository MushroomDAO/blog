# 硬件钱包安全核查：小M正文配图

生成日期：2026-10-29。对应文章：`src/content/blog/hardware-wallet-security-2026-claim-audit.md`。

按发布流程选定的三个认知锚点交付 **3 张独立成品**，采用 `mycelium-mushroom-illustrations` 与内置 `image_gen.imagegen`；未使用 API/CLI 回退、本地绘制替代、品牌素材或外部参考图片。三张均为小M红帽白点、浅色菌柄、黑色手绘轮廓、纯白背景与稀疏中文批注。均为概念隐喻，不主张任何实际产品结构，也不作为产品攻击复现或安全证明。

本任务仅写入三张成品 PNG 和本说明；未编辑正文或 banner，未执行发布、部署、提交或暂存。任务进行期间，正文与 banner 的哈希确实发生了任务外的变化，未回滚或覆盖这些并行改动，不能将其表述为整个工作区未变化。

## 成品与图注

| 图 | 文件 | 尺寸 | 大小（bytes） | 实际颜色数 | 纯白像素占比 |
|---|---|---|---:|---:|---:|
| fig-01 | [PNG](../../src/assets/images/hardware-wallet-security-2026-claim-audit-fig-01.png) | 1120×630 | 23719 | 48 | 93.66% |
| fig-02 | [PNG](../../src/assets/images/hardware-wallet-security-2026-claim-audit-fig-02.png) | 1120×630 | 22857 | 48 | 93.89% |
| fig-03 | [PNG](../../src/assets/images/hardware-wallet-security-2026-claim-audit-fig-03.png) | 1120×630 | 19989 | 48 | 94.03% |

### fig-01：五处安全边界分别核查

- 建议锚点：七个品牌分别发生了什么？ / Keystone 段落后。
- 中文图注：小M分别核查芯片、整机、固件、购买渠道与客户资料五处安全边界；这些是独立概念符号，并非真实设备结构。
- English caption: XiaoM inspects five separate security boundaries: chip, whole device, firmware, distribution channel and customer data. The symbols are conceptual, not a product teardown.
- 画内文字：分别核查（1 处）。
- 视觉核查：可见芯片、完整封闭签名设备、固件卷页、渠道纸箱、客户资料卡与信封。卡与信封属于同一资料符号。小M持放大镜执行核查。
- 原始选定生成文件：`/Users/jason/.codex/generated_images/01a18743-beee-7ae2-99ca-6e3e77b27caf/exec-983ce084-3900-46f4-a5fe-7156e527df90.png`。
- 原始尺寸：1672×941；原始 SHA-256：`6ce04eb80b3f94c1a96d3ccf0342f110054fde71814d5d9373affee2a488dadd`。
- 最终文件 SHA-256：`12919be175f220dde57fef8d64c4595f3d124deb174337701e69ad016963307f`。

### fig-02：真芯片不等于整机安全

- 建议锚点：“后门”应该怎么判定？末尾。
- 中文图注：小M用放大镜检查整台无品牌签名设备：真芯片不等于整机安全。此图是安全边界的概念示意，不是攻击复现。
- English caption: XiaoM examines an entire unbranded signer. A genuine chip does not establish whole-device safety; this is a conceptual illustration, not an attack reconstruction.
- 画内文字：真芯片 / 整机安全 / 概念示意（3 处，另有 ≠ 符号）。
- 视觉核查：放大镜覆盖整台封闭设备，芯片是设备外的独立概念图标；没有内部部件、植入模块、线路或攻击者。
- 原始选定生成文件：`/Users/jason/.codex/generated_images/01a18743-beee-7ae2-99ca-6e3e77b27caf/exec-6b4c9301-736a-4fee-9eb9-5e1e1f2c33d9.png`。
- 原始尺寸：1672×941；原始 SHA-256：`22408468cc623bf1371fbba3d114fa105ed3fd3d31c00dc5a6055b79a9a758fa`。
- 最终文件 SHA-256：`a2785dc2daf6a09f9ecfee00bbd85250f70e030e6481b7d0cb3f188222c9eb37`。

### fig-03：固件升级不能修复旧种子

- 建议锚点：普通持有人应该如何行动？末尾。
- 中文图注：小M拿着已经暴露的旧钥匙，旁边的新设备虽已更新固件，旧种子仍有风险；钥匙与其虚线副本仅作暴露风险的隐喻。
- English caption: XiaoM holds an already exposed old key beside updated new hardware. A firmware update does not repair an exposed seed; the key and dashed duplicate are metaphors.
- 画内文字：已暴露 / 固件已更新 / 旧种子仍有风险（3 处）。
- 视觉核查：小M举起旧钥匙；红色虚线钥匙暗示暴露后可能已有副本。新设备与旧钥匙分开，没有声称恢复同一种子会使其安全，也无真实恢复词或操作步骤。
- 原始选定生成文件：`/Users/jason/.codex/generated_images/01a18743-beee-7ae2-99ca-6e3e77b27caf/exec-1a456543-95aa-4230-9be2-9f33d77a2500.png`。
- 原始尺寸：1672×941；原始 SHA-256：`3baebbaade7e289aed6ff9b877185f4fbb0b16c8bf952450b1fd37889b86f7b0`。
- 最终文件 SHA-256：`e1db7b10d341a177fea8af082a6c606b8ca3eec34d601ad9b6811ad24a189014`。

## 来源与迭代

所有原始生成文件保持在现有 `~/.codex/generated_images/` 下原位，未复制原始大图到仓库、source 或临时目录。压缩成品从这些原始文件派生。

- fig-01 首次生成：`/Users/jason/.codex/generated_images/01a18743-beee-7ae2-99ca-6e3e77b27caf/exec-e8aba4d2-e6d9-473b-8598-85e46933243f.png`。首次版本物件填色较重且脚下有阴影，保留原始文件，但不交付为成品。
- fig-01 经一次内置 imagegen 编辑，去掉重填色及阴影，保留五处边界、核查动作与单条标注；成品使用上文记录的 `exec-983ce084-3900-46f4-a5fe-7156e527df90.png`。
- fig-02、fig-03 各独立生成一次，均未使用参考图片。三张不同主题分别调用生成工具，没有拼成九宫格或多面板图。
- 除 fig-01 对其自身初版的编辑外，没有任何产品照片、品牌资产或以往案例图片作为视觉输入。原始模型响应未披露具体模型版本，因此不推测模型名。

## 压缩与验证

使用 Pillow 12.3.0：RGB → LANCZOS 缩放至 1120×630 → FASTOCTREE 48 色量化（无抖动）→ 对亮度接近白色的中性调色板项归并为纯白 → 对重复 RGB 项合并索引，并重排为从 0 开始的连续、全部已使用索引 → PNG `optimize=True, compress_level=9`。近白归并条件为 `min(R,G,B) >= 242 and max(R,G,B)-min(R,G,B) <= 8`，清除生成背景的轻微近白噪点。未在代码里重绘物件、中文或角色。

曾比较 MEDIANCUT 量化，发现其使少量蓝色批注趋于灰色，最终改用 FASTOCTREE 保留蓝色；仓库只保留最终三张 PNG。实际最终调色板均为 48 个唯一 RGB 值、索引连续，无重复 RGB 项和未使用索引。

程序逐张验证：PNG/P 模式、1120×630、严格 16:9、48 色、全部索引被使用、四角均为 RGB(255,255,255)、体积严格小于 90,000 bytes。三张均通过，未触发 960×540 回退。压缩后逐张人工查看，核对五处边界、完整设备、旧钥匙隐喻、红帽白点、中文标注与无品牌要求；无网格、PPT、多面板、可见背景纹理、真实内部结构或产品攻击步骤。

## 实际提示词

以下为发送给内置 imagegen 的完整提示词。fig-01 末尾另列实际编辑提示词。

### fig-01 生成提示词

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body illustration, not a collage.
Pure #FFFFFF white background. Sparse thin black hand-drawn pen contours, slightly irregular confident lines, flat restrained color, abundant blank white space (at least 50%). No texture, paper grain, gray background, gradient, shading or shadows. No grid, panels, PPT, infographic cards, formal flowchart, architecture diagram, title, logo, watermark or photorealism. Not cute, not a mascot poster.
Central active character XiaoM (小M): small serious deadpan mushroom with red dome cap bearing 3–5 WHITE round spots, pale cream stem body, black dot eyes, black outline, tiny thin arms and legs, flat color.
Core action: XiaoM is an inspector, carefully aiming a large handheld magnifying glass toward FIVE separate abstract trust-boundary objects, loosely arranged at different heights in a single airy tabletop-like scene, never in equal boxes or a straight diagram row. The five objects are exactly: (1) one tiny generic integrated circuit icon; (2) a separate WHOLE closed unbranded hardware signer with a blank small screen and two small round buttons; (3) a small curled firmware sheet with only two simple brace marks; (4) one open plain shipping carton representing the purchase/distribution channel; (5) one customer contact card bearing only a simple person silhouette and two blank lines, next to a tiny envelope as a single grouped object. These objects are independent conceptual symbols, not components of a real product. XiaoM's inspecting gesture and magnifier tie the scene together. No physical wiring between the symbols, no nested device cutaway, no attacker, no exploit.
Use only ONE small handwritten Chinese annotation near XiaoM in muted red: “分别核查”. No other rendered text. Keep all five objects recognizable but extremely simple, with no detailed circuitry. Composition fits comfortably inside generous white margins. No claims about any actual hardware construction.
```

### fig-02 生成提示词

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body illustration.
Pure #FFFFFF white background, sparse slightly wobbly BLACK hand-drawn linework, large quiet whitespace (at least 50%), flat red cap and tiny red/blue annotation accents, no paper texture, no shading, shadows, gradients, gray wash, no grids, cards, panels, PPT or formal diagram. No title, brand, logo, watermark, realistic product copy, attack demonstration or exploded view.
XiaoM (小M) is the core actor: serious blank-faced small mushroom, RED dome cap with 3–5 WHITE circular spots, cream-white stem body outlined in black, small BLACK dot eyes, tiny thin arms/legs. Not cute, not a smiling mascot.
Scene: XiaoM leans back to hold a comically oversized magnifying glass that encompasses the ENTIRE closed generic unbranded hardware signing device standing nearby. Make the whole modest rectangular signer visible inside the glass: simple black outline, blank screen, two plain buttons; sealed exterior only, with no internals visible. The magnifier is examining the device as a WHOLE, no attack in progress.
Beside the scene, a very small detached generic chip SYMBOL with one tiny blue checkmark has the handwritten Chinese label “真芯片”. It is explicitly a separate conceptual symbol floating on the white page, NOT inside or wired to the signer. A simple hand-drawn red “≠” sits between the chip symbol and the whole-device inspection scene, followed by the short handwritten label “整机安全”. The drawing communicates that a genuine chip is only a bounded property and cannot certify the whole device. A tiny blue handwritten note below the central scene reads “概念示意”. These are the ONLY three short Chinese labels; no other words. No tampering circuitry, malicious module, antenna, cross-section or real-world product details. Airy editorial sketch, with XiaoM doing the inspection, not merely watching.
STRICT RENDERING: no cast shadow even beneath feet. No mouth, no smile on XiaoM. All objects must be white unfilled interiors with thin black outlines, except the flat red cap, cream stem and the tiny specified red/blue marks. No gray or black device fill. No colored glass, no gradients inside shapes. Background absolute pure white.
```

### fig-03 生成提示词

```text
Use case: illustration-story. Generate exactly ONE standalone 16:9 horizontal Chinese article body illustration.
Pure #FFFFFF white background, thin slightly irregular BLACK hand-drawn pen outlines, sparse flat color, at least 50% empty white space, restrained red/orange/blue handwritten accents. No texture, grain, gray background, shadows, gradients, grids, frames, panels, PPT, formal flowchart, logo, brand, title or watermark. Not cute, no glossy cartoon styling.
XiaoM (小M) is a small deadpan serious mushroom: flat RED dome cap with 3–5 WHITE round spots, pale cream stem body, BLACK dot eyes and black outline, tiny sticklike arms and legs.
Core scene: XiaoM is actively holding up a large OLD ordinary metal KEY by its ring, examining it with concern but a blank expression. This old key is a visual metaphor for an already exposed seed, not an actual crypto key format. It has a short red handwritten annotation “已暴露”. The key remains plainly unchanged; draw a faint small red duplicate key OUTLINE immediately behind it to suggest it could already have been copied, with no attacker present.
Beside XiaoM stands one NEW plain generic unbranded CLOSED hardware signer: simple rounded rectangle, blank small screen, two plain buttons, no internals. A single small blue upward update arrow near the device and the blue handwritten label “固件已更新” suggest updated firmware, without technical interface details. XiaoM keeps the old exposed key held apart from the new device: updating the device has not repaired the old seed. Near the held key, one small red handwritten note says “旧种子仍有风险”. These THREE annotations are the only text. Do not add a fresh safe key, replacement ritual, repair tool, reset instructions, transaction data, recovery words or real product structure. Keep a single quiet conceptual scene with the old key as the visual focus.
STRICT RENDERING: no cast shadow beneath feet. All objects must be white unfilled interiors with thin black outlines, except the flat red cap, cream stem and the tiny specified red/blue marks. No gray or black device fill. No colored glass, no gradients inside shapes. Background absolute pure white.
```

### fig-01 编辑提示词

编辑参考仅为上述 fig-01 首次生成文件。

```text
Edit the provided illustration, preserving the exact core composition, all FIVE conceptual objects, XiaoM's inspecting action, the red cap with white spots, and the SINGLE Chinese label “分别核查”. Change only the visual rendering to a much sparser pure-white editorial pen sketch. Remove the shadow beneath XiaoM completely. All objects — chip, whole closed signer, firmware scroll, open carton, customer contact card with envelope, magnifying glass — must have plain WHITE unfilled interiors with thin slightly irregular BLACK outlines. Remove dark gray device and chip fills, tan carton fill, colored blue glass, gradients, highlights, paper texture and ALL shading. Retain only flat RED XiaoM cap with 3–5 WHITE circular spots, flat pale cream stem with BLACK dot eyes, and the one RED handwritten Chinese annotation. Background must be absolute #FFFFFF pure white with no noise, grain, paper texture, gray wash or shadow anywhere. Keep the five symbols detached and conceptual, no internals, wiring, real product structure or logos. Preserve the ample whitespace and 16:9 aspect. No extra labels, no title, no grid or PPT layout. Do not turn the character into a cute smiling mascot.
```

