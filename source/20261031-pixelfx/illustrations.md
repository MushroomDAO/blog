# pixelfx 正文配图交付记录

- 日期：2026-10-31。
- 正文来源：`src/content/blog/pixelfx-pixel-effects-guide.md`（已阅读，未修改）。
- 使用技能：`mycelium-mushroom-illustrations`；生成方式为内置 `image_gen`，每张独立调用，共3张。
- 原始工具输出保留于 `/Users/jason/.codex/generated_images/` 下，未覆盖、未修改。
- 三张均为纯白背景16:9正文概念插画，无封面、无模拟UI；红盖白点、浅色菌柄的小M参与核心动作。
- 最终格式：1120×630，8-bit indexed PNG；MEDIANCUT量化48色、关闭抖动；合并相同RGB的调色板索引并移除PNG调色板填充项。三张均实际使用48色，无重复调色板项，各小于90,000字节；未使用960×540降级。
- 后处理仅做白底合成、缩放、近白背景归一、48色量化及无损PNG压缩；未重绘或添加内容。
- 图03的棋盘格仅用于示意PNG素材的透明区域；交付插画本身使用不透明纯白背景。
- 已目视检查三张最终PNG：中文标签可读，画面含对应主题，非banner或界面截图。
- 仅新增三张指定成图和本记录；未修改文章或其他项目文件，未查看或计算banner哈希，未部署、未提交。
- 本记录在最终图像验证完成后写入；写入后不再修改最终图像。

| 图 | 尺寸 | 字节数 | 使用颜色 | 重复调色板项 |
|---|---|---:|---:|---:|
| 01 | 1120×630 | 44965 | 48 | 0 |
| 02 | 1120×630 | 48891 | 48 | 0 |
| 03 | 1120×630 | 38983 | 48 | 0 |

## 01 · 代码驱动像素特效并复用

图注：小M把JavaScript代码送入手摇装置，驱动像素火焰和刀光，再把同类效果整理成可复用素材。概念示意。

- 原始文件：`/Users/jason/.codex/generated_images/01a190b2-9f30-7d43-b1c9-c50c3db9ab32/exec-760bd16b-0317-438d-876f-4a361e599877.png`
- 原始文件字节数：1292812
- 原始SHA256：`6f5beb7f551ee32ea05fb6822003a9e26b7ae95577a580262c0d0025a94c2101`
- 最终文件（仓库相对路径）：`src/assets/images/pixelfx-pixel-effects-guide-fig-01.png`
- 最终文件（绝对路径）：`/Users/jason/Dev/mycelium/blog/src/assets/images/pixelfx-pixel-effects-guide-fig-01.png`
- 最终SHA256：`023225c4858883fd4e56a27f63c1ec085385dbaae71826613f3af3a3b463e92a`

完整生成提示词：

```text
Use case: illustration-story.
Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, never a banner. Pure #FFFFFF white background. Thin slightly wobbly BLACK hand-drawn pen line art, restrained flat RED/ORANGE/BLUE accents, NO gradients, NO shadows, NO paper texture, NO noise. At least 40% empty white space, airy composition, all content well inside generous margins. Mature deadpan absurd product sketch, not cute or childish, not commercial vector art or PPT. No title, no top-left heading, no watermark, no mock UI, no browser window, no monitor, no app panels. This is a conceptual illustration, not a real product screenshot.
Recurring protagonist XiaoM 小M is a small serious MUSHROOM creature: rounded RED dome cap with 3-5 WHITE polka dots and thin black outline, CREAM stem body, small BLACK dot eyes on stem, thin stick arms and legs, blank focused expression, NO smile. Never solid-black mushroom. XiaoM must physically perform the central action; removing XiaoM should break the visual metaphor. Flat restrained colors so this art survives 48-color palette quantization. Chinese labels must be short, large enough to read at 1120x630, hand-lettered but accurate. Only specified labels; no incidental text.
Theme 01: Code drives pixel fire and sword slash, producing reusable effects. This explains pixelfx as editable JavaScript drawing pixels, not an AI image generation model.
Composition: In one loose horizontal hand-drawn scene, XiaoM operates a small absurd hand-cranked music-box-like device by feeding an unfurled paper code ribbon into it. The ribbon only has a few visible curly braces and tiny colored code-like strokes, not a screen. XiaoM's arm actually turns the crank. From the device rise TWO small clear pixel-art shapes: a stepped orange/red flame and a curved blue pixel sword-slash, drawn with crisp little square pixels amid pen line art. A short orange motion path carries small repeatable copies of these same two effects onto a tidy fan of three reusable loose effect tiles to the right. The code roll, XiaoM cranking, and fire/slash tiles should read as one simple action. Keep objects sparse, no conveyor belt, no elaborate plumbing, no formal box-and-arrow diagram.
ONLY exact labels: “代码” by the code ribbon in black; “像素特效” near the flame/slash in orange; “反复用” by the reusable tiles in blue. No other words. Avoid numerical claims and logos.
```

## 02 · 看帧图、改代码、看动作

图注：小M查看contact sheet中的序列帧、修改代码，并通过连续动作预览复查，形成反复迭代的视觉检查闭环。概念示意。

- 原始文件：`/Users/jason/.codex/generated_images/01a190b2-9f30-7d43-b1c9-c50c3db9ab32/exec-42f1c161-228d-49c6-a0b7-c51d74d9cb25.png`
- 原始文件字节数：1328957
- 原始SHA256：`36bbb03b7028f8d194a02b6b4e2258e61d5ee3c0f882de3fad71fe86e19132cb`
- 最终文件（仓库相对路径）：`src/assets/images/pixelfx-pixel-effects-guide-fig-02.png`
- 最终文件（绝对路径）：`/Users/jason/Dev/mycelium/blog/src/assets/images/pixelfx-pixel-effects-guide-fig-02.png`
- 最终SHA256：`d71eedd939ace5a438638ca06853fb1fc9c50a4cd541c2726cfab206d0005ba1`

完整生成提示词：

```text
Use case: illustration-story.
Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, never a banner. Pure #FFFFFF white background. Thin slightly wobbly BLACK hand-drawn pen line art, restrained flat RED/ORANGE/BLUE accents, NO gradients, NO shadows, NO paper texture, NO noise. At least 40% empty white space, airy composition, all content well inside generous margins. Mature deadpan absurd product sketch, not cute or childish, not commercial vector art or PPT. No title, no top-left heading, no watermark, no mock UI, no browser window, no monitor, no app panels. This is a conceptual illustration, not a real product screenshot.
Recurring protagonist XiaoM 小M is a small serious MUSHROOM creature: rounded RED dome cap with 3-5 WHITE polka dots and thin black outline, CREAM stem body, small BLACK dot eyes on stem, thin stick arms and legs, blank focused expression, NO smile. Never solid-black mushroom. XiaoM must physically perform the central action; removing XiaoM should break the visual metaphor. Flat restrained colors so this art survives 48-color palette quantization. Chinese labels must be short, large enough to read at 1120x630, hand-lettered but accurate. Only specified labels; no incidental text.
Theme 02: Inspect a contact sheet, edit code, then review actual motion and repeat; static frames and continuous playback provide different evidence.
Composition: A single loose circular workbench ritual, not three framed panels. At left is a tilted loose CONTACT SHEET paper bearing a sparse 2-by-3 grid of SIX small pixel flame frames, each flame at a different animation phase, no UI. Center-bottom XiaoM bends over a paper code ribbon and physically changes a curly-brace code line with an oversized pencil, while its other hand tilts a small magnifying glass toward the contact sheet. At right, a simple open hand-powered flipbook, held up by XiaoM's thin other arm if needed, has a few fanning pages and an emerging pixel slash with two minimal motion echoes, indicating continuous motion rather than static frame inspection. Use just THREE thin, sweeping orange arrow segments forming an open loop: contact sheet to code edit, code edit to flipbook motion, motion back to sheet. XiaoM is the active editor at the heart of this cycle, not an observer. Keep a large white hole and generous outer whitespace, sparse contact sheet, no screens.
ONLY exact labels: “看帧图” beside contact sheet in black; “改代码” beside the pencil in orange; “看动作” beside flipbook in blue. No title, no extra text.
```

## 03 · 实时JS与透明PNG／JSON接入游戏

图注：小M连接两条游戏接入路径：JavaScript实时绘制，以及透明PNG精灵图配JSON帧数据后导入使用。概念示意，不代表已完成游戏引擎集成测试。

- 原始文件：`/Users/jason/.codex/generated_images/01a190b2-9f30-7d43-b1c9-c50c3db9ab32/exec-9fb4cab7-8e57-4d2e-a9c2-57f0d11fcb85.png`
- 原始文件字节数：1208742
- 原始SHA256：`106c6fe2b51794110bb3516f30ef9be73db2bb93e172ba9a125b66443b3ed21c`
- 最终文件（仓库相对路径）：`src/assets/images/pixelfx-pixel-effects-guide-fig-03.png`
- 最终文件（绝对路径）：`/Users/jason/Dev/mycelium/blog/src/assets/images/pixelfx-pixel-effects-guide-fig-03.png`
- 最终SHA256：`15eff9396c27de973d4cd6e24661a3fe8892f782318c0c68878fbd3616cf0233`

完整生成提示词：

```text
Use case: illustration-story.
Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, never a banner. Pure #FFFFFF white background. Thin slightly wobbly BLACK hand-drawn pen line art, restrained flat RED/ORANGE/BLUE accents, NO gradients, NO shadows, NO paper texture, NO noise. At least 40% empty white space, airy composition, all content well inside generous margins. Mature deadpan absurd product sketch, not cute or childish, not commercial vector art or PPT. No title, no top-left heading, no watermark, no mock UI, no browser window, no monitor, no app panels. This is a conceptual illustration, not a real product screenshot.
Recurring protagonist XiaoM 小M is a small serious MUSHROOM creature: rounded RED dome cap with 3-5 WHITE polka dots and thin black outline, CREAM stem body, small BLACK dot eyes on stem, thin stick arms and legs, blank focused expression, NO smile. Never solid-black mushroom. XiaoM must physically perform the central action; removing XiaoM should break the visual metaphor. Flat restrained colors so this art survives 48-color palette quantization. Chinese labels must be short, large enough to read at 1120x630, hand-lettered but accurate. Only specified labels; no incidental text.
Theme 03: Two ways into game workflows: live JS computation versus exported transparent PNG atlas + JSON metadata. This is a conceptual choice, not proof of tested game engine integration.
Composition: XiaoM straddles two loose gently diverging paths like an absurd practical stage technician, actively plugging two DIFFERENT artifacts into two small open game-scene stage dioramas at the right. Upper path: XiaoM pulls a flexible paper code ribbon marked “JS”, which directly feeds a little floating pixel flame above a simple unframed game ground line, suggesting live drawing. Lower path: XiaoM physically slots a transparent film sheet containing a sparse 2-by-3 atlas of pixel sword-slash frames together with a small curly-brace metadata tag marked “JSON” into a small hand-cut frame holder beside a second bare game ground line. The film sheet is depicted in thin black outline; faint pale-gray transparency checker marks ONLY inside its six cells, never on the white background. Attach a small “PNG” mark to the film. Two small orange directional curves only; no giant fork diagram, no cards/dashboard, no branded engine logos, no UI chrome. The two game scenes use only a tiny neutral stick game character, ground line and effect, NOT mushrooms as targets.
ONLY text allowed: upper label “实时画” in blue and token “JS”; lower label “导出用” in orange and tokens “PNG” and “JSON”; tiny label “透明” by the film edge in black. All labels legible. No engine names or compatibility badges. Keep >=40% pure white negative space.
```
