# CoreSpeed TIE 小M正文配图交付记录

- 日期：2026-10-31
- 对应正文：`src/content/blog/corespeed-tie-mac-studio-guide.md`（仅读取）
- 使用技能：`mycelium-mushroom-illustrations`、`imagegen`
- 生成方式：内置 `image_gen.imagegen`，三次独立新图调用，每次一张；无参考图片、无拼图、无变体或重生成。
- 原始文件保留在现有 `/Users/jason/.codex/generated_images/` 下，未覆盖或移动；未在其他位置复制原始大图。
- 三张最终图已全部完成、打开检查并计算以下 SHA-256 后，才写本报告。报告写入后不再修改最终图。
- 本任务只新增三张正文配图和本报告；未修改正文，未查看或哈希 banner，未部署、未提交。

## 最终文件与检查

| 图 | 最终路径（仓库相对） | 尺寸 | 字节数 | 实际调色板颜色 | 中文标注数 |
|---|---|---|---:|---:|---:|
| 01 | `src/assets/images/corespeed-tie-mac-studio-guide-fig-01.png` | 1120×630 | 12937 | 17 | 2 |
| 02 | `src/assets/images/corespeed-tie-mac-studio-guide-fig-02.png` | 1120×630 | 27850 | 24 | 3 |
| 03 | `src/assets/images/corespeed-tie-mac-studio-guide-fig-03.png` | 1120×630 | 18361 | 20 | 3 |

处理：从各自原图以 Lanczos 缩放到 1120×630；Pillow MEDIANCUT 48 色量化、关闭抖动。量化后，RGB 各通道均 ≥245 且通道差 ≤8 的近白色调色板项统一为 #FFFFFF；合并相同 RGB 的索引，重映射像素，紧凑保存 P 模式 PNG（optimize=True、compress_level=9）。48 是量化阶段的颜色上限，合并后实际颜色如表；三个文件均无重复的已用调色板索引。全部低于 90,000 字节，未使用 960×540 备用尺寸。

目视检查：三张均为独立 16:9 稀疏白底手绘场景，红帽白点、浅色菌柄小M参与核心动作，分别只有 2、3、3 个短中文标注。没有 PPT 网格、背景纹理、商标、实际 UI 截图或安全保证。图02中的文件夹是普通开放文件夹，账户权限卡与审批拨杆独立摆放，没有围墙、护盾或操作系统沙箱暗示。图03以断开的插头示意退出检查，没有表示验收已经通过的成功徽章。

## fig-01

- 最终绝对路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/corespeed-tie-mac-studio-guide-fig-01.png`
- 原始生成文件：`/Users/jason/.codex/generated_images/01a19084-a41c-70c2-90e4-59036411242f/exec-7651ad20-6021-40a9-b2bd-252c5db46562.png`
- 原图尺寸：1672×941
- 最终图 SHA-256：`1fb773ca5fecc77958bf53eff55d0b871b9dda27332c8e07cc64a09c1128662b`
- 原图 SHA-256：`e0b617756dd6a838624a839e9ca4541e2ddae38152d5b81b2eb5a2c522f250a1`
- 中文标注：`远程代理`、`本地工具`
- 建议位置：中文“哪些能力可以交给 Agent？”相关能力说明后；英文 What can agents reach? 后。
- 中文图注：小M搭接远程 Agent 与本地 Mac 工具工作站，示意连接层复用现有电脑的能力。
- English caption: XiaoM bridges a remote agent to tools on an existing local Mac workstation; a conceptual illustration.
- 纯白像素比例：95.6261%（按最终图 #FFFFFF 像素统计）。

### 完整生成提示词

```text
Use case: illustration-story.
Generate ONE standalone independent 16:9 horizontal Chinese article body illustration, not a collage or a slide.
Pure solid white (#FFFFFF) background, sparse black hand-drawn pen linework with a gently uneven human stroke, flat small color accents, enormous negative space (at least 55% white). Keep the scene compact within the central horizontal band with generous margins. No texture, paper grain, shadows, gradients, grid, PPT, formal diagram, panel borders, glossy commercial vector style or actual UI screenshots.
XiaoM is the core worker: a deadpan little mushroom with a rounded flat RED cap bearing 3–5 WHITE round spots, pale cream stem body, black outline, tiny black dot eyes, thin arms and legs. Serious blank expression, no smile, no shiny eyes, no costume, not a cute mascot. XiaoM actively performs the core action. Black pen lines dominate; orange for a connection or movement, very small blue/red handwritten annotations.
No logos, Apple mark, brand names, English text, title, watermark, badges, shields, locks, walls, cages, security guarantees, or implication of OS isolation. Draw only the Chinese labels explicitly listed below, each once; at most THREE short Chinese labels in the entire image. No other text, numbers, glyph strings, or tiny writing. Handwritten Chinese must be clearly legible.

Theme: a remote agent can use enabled tools on an existing local Mac workstation.
Composition: At the left a small floating paper card with a simple abstract agent face made of two dots and one short line; label it “远程代理” in small blue handwriting. At the right a generic local Mac-style workbench: a small plain low rectangular desktop computer next to a generic monitor and a simple keyboard, completely unbranded. On the monitor use just two abstract tool pictograms: a spanner and a document, no UI, no text. Label the workbench “本地工具” in small black handwriting. In the middle XiaoM straddles the gap and physically fits an orange connector bridge between the card and the workbench, holding its loose connector in one hand and bracing with a thin leg. The mushroom's bridging labor is what makes the connection intelligible. One small orange connection only, no cloud, internet globe, pipelines, extra tools or decorative arrows. The local machine is not drawn as a sandbox. Scene uses around 40% of canvas area. Labels verbatim, exactly two: “远程代理”, “本地工具”.
```

## fig-02

- 最终绝对路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/corespeed-tie-mac-studio-guide-fig-02.png`
- 原始生成文件：`/Users/jason/.codex/generated_images/01a19084-a41c-70c2-90e4-59036411242f/exec-4b64ca06-5a24-4638-864a-8ca493da9b5a.png`
- 原图尺寸：1672×941
- 最终图 SHA-256：`25a0f435a7bff7c524b024d4a08c449b23686f2418294da5cb1e12d9f3307f7b`
- 原图 SHA-256：`ef7bca4dcddaf9e2566194e13145845cd0c3adec0450517f660bec82a4d56e9b`
- 中文标注：`工作目录`、`账户权限`、`审批开关`
- 建议位置：工作目录和审批，是否构成完整隔离？ / Are directories and approvals complete isolation? 后。
- 中文图注：小M区分工作目录、账户权限与审批开关：目录范围、账户可达资源和审批配置是不同控制，工作文件夹不构成操作系统级沙箱。
- English caption: XiaoM distinguishes the working folder, account privileges and approval switch; a folder does not provide OS-level isolation.
- 纯白像素比例：88.2792%（按最终图 #FFFFFF 像素统计）。

### 完整生成提示词

```text
Use case: illustration-story.
Generate ONE standalone independent 16:9 horizontal Chinese article body illustration, not a collage or a slide.
Pure solid white (#FFFFFF) background, sparse black hand-drawn pen linework with a gently uneven human stroke, flat small color accents, enormous negative space (at least 55% white). Keep the scene compact within the central horizontal band with generous margins. No texture, paper grain, shadows, gradients, grid, PPT, formal diagram, panel borders, glossy commercial vector style or actual UI screenshots.
XiaoM is the core worker: a deadpan little mushroom with a rounded flat RED cap bearing 3–5 WHITE round spots, pale cream stem body, black outline, tiny black dot eyes, thin arms and legs. Serious blank expression, no smile, no shiny eyes, no costume, not a cute mascot. XiaoM actively performs the core action. Black pen lines dominate; orange for a connection or movement, very small blue/red handwritten annotations.
No logos, Apple mark, brand names, English text, title, watermark, badges, shields, locks, walls, cages, security guarantees, or implication of OS isolation. Draw only the Chinese labels explicitly listed below, each once; at most THREE short Chinese labels in the entire image. No other text, numbers, glyph strings, or tiny writing. Handwritten Chinese must be clearly legible.

Theme: a working folder, the user's account privileges, and an approval switch are different controls. A folder is NOT an operating system sandbox.
Composition: One deadpan XiaoM is actively sorting three different tangible objects on a loose open work surface, not a grid, not a flowchart. One hand touches a small ordinary OPEN file folder labelled “工作目录”; the other lifts a much larger loose account-permission credential card with a plain single-person silhouette labelled “账户权限”; a foot carefully nudges a SEPARATE small physical toggle on its own tiny base labelled “审批开关”. The folder is simply an open stationery folder holding one blank sheet, not a container enclosing XiaoM, the credential, the switch, or the computer. The account credential visibly remains independent of the folder, and is larger to suggest broader account reach. The toggle has no ON/OFF text and makes no approval or security promise; it is visibly a configurable control rather than a success badge. Stagger the three objects naturally near XiaoM, with generous white space, no enclosing boundary, no keys or padlocks, no shields, no nested rectangles, no checkmarks, no folder-to-permission arrows. Draw ONLY these three exact Chinese handwritten labels, one beside each relevant object: “工作目录”, “账户权限”, “审批开关”.
```

## fig-03

- 最终绝对路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/corespeed-tie-mac-studio-guide-fig-03.png`
- 原始生成文件：`/Users/jason/.codex/generated_images/01a19084-a41c-70c2-90e4-59036411242f/exec-d27d7816-887f-44e3-a804-2e70e368b5a7.png`
- 原图尺寸：1672×941
- 最终图 SHA-256：`97bd174ad5aa05011e979cc42040082cb078119b2a5e7d61d4dc0123fd309bb8`
- 原图 SHA-256：`6eeda41179bba97cf6124482badaf32eef3cc837896eb23800e7d0f86e8a7d0e`
- 中文标注：`读取`、`受控写入`、`退出检查`
- 建议位置：怎样做一次范围明确的试用？ / How should a first trial work? 后。
- 中文图注：小M沿读取、受控写入和退出检查验收连接；这是一条建议的检查路径，不表示远程流程已实测通过。
- English caption: XiaoM follows read, controlled-write and exit checks; a proposed acceptance sequence rather than a completed remote test.
- 纯白像素比例：95.0064%（按最终图 #FFFFFF 像素统计）。

### 完整生成提示词

```text
Use case: illustration-story.
Generate ONE standalone independent 16:9 horizontal Chinese article body illustration, not a collage or a slide.
Pure solid white (#FFFFFF) background, sparse black hand-drawn pen linework with a gently uneven human stroke, flat small color accents, enormous negative space (at least 55% white). Keep the scene compact within the central horizontal band with generous margins. No texture, paper grain, shadows, gradients, grid, PPT, formal diagram, panel borders, glossy commercial vector style or actual UI screenshots.
XiaoM is the core worker: a deadpan little mushroom with a rounded flat RED cap bearing 3–5 WHITE round spots, pale cream stem body, black outline, tiny black dot eyes, thin arms and legs. Serious blank expression, no smile, no shiny eyes, no costume, not a cute mascot. XiaoM actively performs the core action. Black pen lines dominate; orange for a connection or movement, very small blue/red handwritten annotations.
No logos, Apple mark, brand names, English text, title, watermark, badges, shields, locks, walls, cages, security guarantees, or implication of OS isolation. Draw only the Chinese labels explicitly listed below, each once; at most THREE short Chinese labels in the entire image. No other text, numbers, glyph strings, or tiny writing. Handwritten Chinese must be clearly legible.

Theme: suggested acceptance checks: read first, make a controlled temporary write, then verify exit/disconnection.
Composition: One thin orange meandering walking path, low in the central band, passes three small grounded objects at irregular natural spacing without panels or formal nodes. At the left, an open blank document and a small magnifying lens labelled “读取”. In the middle, a single blank disposable sheet resting under a pencil held by a small physical stop lever, suggesting deliberate controlled writing; label “受控写入”. At the right, a physically disconnected simple cable plug with clearly visible open air between plug and socket, labelled “退出检查”. XiaoM is actively walking the path, body leaning toward the last disconnected plug and one hand inspecting the separated connector, while a few small black footprints behind imply the sequence from the read object past the controlled-write object. One XiaoM only, no duplicate characters. No success checkmarks, no security badges, no claim the checks already passed, no UI or log screenshots. Leave top half mostly untouched white; the three labels sit close to objects, never as headings. Exactly THREE short labels verbatim: “读取”, “受控写入”, “退出检查”.
```
