# Speech AI frontiers — illustration QA

日期：2026-10-11。交付：恰好四张独立正文 PNG。状态：全部通过。

## 范围与来源

- 已读取文章全文（含中英文）、小M skill、五份参考 style-dna / mushroom-ip / composition-patterns / prompt-template / qa-checklist，以及内置 imagegen 工作流。
- 使用内置 image_gen.imagegen，四次独立调用、每次一张，无 montage、无外部 API、无失败重试。
- 四份原图均在本轮开始后生成且不在初始 generated_images 文件清单中，原样保留。
- 本轮写操作仅涉及指定四个 PNG 和本 QA；没有写正文或 banner，没有发布、提交或 KB 写入。
- 工作期间发现正文摘要与初始摘要不同，且有其他文件被暂存。本轮工具没有这些写入操作；视为工作区并发改动，不回滚、不声称正文前后不变。摘要对照见下文。

## 规格和处理

四张均为不透明白底 PNG，1200 × 675，严格 16:9，每张 <90,000 字节。

| 图 | 最终文件 | 字节 | 纯白像素比例 | 结论 |
| --- | --- | ---: | ---: | --- |
| 01 | `src/assets/images/ai-speech-six-frontiers-open-source-fig-01.png` | 88,126 | 88.92% | PASS |
| 02 | `src/assets/images/ai-speech-six-frontiers-open-source-fig-02.png` | 85,589 | 89.62% | PASS |
| 03 | `src/assets/images/ai-speech-six-frontiers-open-source-fig-03.png` | 74,054 | 90.80% | PASS |
| 04 | `src/assets/images/ai-speech-six-frontiers-open-source-fig-04.png` | 88,196 | 89.41% | PASS |

原图尺寸均为 1672 × 941。以 Pillow 按比例缩放并用白色微量补边到 1200 × 675，不拉伸、不裁掉内容。RGB 三通道均 ≥245 的近白背景归一为 #FFFFFF，保留米白菌柄和淡灰工具箱。采用无抖动调色板 PNG、压缩级别 9；01 为 192 色预算，02–04 为 256 色预算。原图不改写。纯白像素比例仅是像素统计，不等同于构图留白面积。

## 视觉验收

已查看四张生成原图，并用 view_image 分别打开四张压缩后最终文件。

### 01 — 收听与播放双机关

- 小M左手保持收听机关开放，右手拉红色播放停止杆；来话以蓝色语音石表达，输出端出现暂停符号。
- 次要小机关与“轮流”标注对照顺序回合，无分格、无复杂流程图。
- 中文准确：“边听边说”“插话即停”“轮流”。角色参与核心动作。PASS。

### 02 — 等待缓冲罐

- 小M握无数字秒表，检查等待罐；快转计算轮并不能释放音频罐中的等待石。
- 三罐代表停顿等待、排队、播放缓冲，表达计算快不等于端到端响应快。
- 中文准确：“等停顿”“排队”“待播放”“算得快 ≠ 回得快”。
- 没有 timing 数字、毫秒、实测延迟或伪造统计。PASS。

### 03 — 三件独立许可资产

- 代码册、权重块、音频数据线轴分别连接自己的独立许可牌；无共用许可标签。
- 小M拉起权重牌并用放大镜核对，角色参与核心动作。
- 中文准确：“代码”“权重”“数据”“分别核对”。没有具体许可或权限断言。PASS。

### 04 — 只改一个变量

- 小M调一个装置的橙色旋钮并在夹板记录；无数字刻度尺表达测量，不声称已取得结果。
- 右侧准确五个独立、淡灰、开盖、白色内腔空工具箱；三远两近，没有标签、数字、连线或内部机器。
- 中文准确：“只改一处”“测了再说”。一个受控项目与闲置工具形成对照。PASS。

### 共同检查

- 四张均为红色蘑菇帽、四个白点、米白菌柄、黑点眼、冷静表情、黑色手绘线条；小M主动操作。
- 四角均为 RGB (255,255,255)，最终背景无纹理、渐变、投影，留白充足。
- 标注分别为 3 / 4 / 4 / 2 处，少量红橙蓝，短且清楚；无左上角标题、PPT 架构网格或拥挤流程图。
- 四个隐喻独立且风格一致；未打开 examples 复制旧构图。
- 压缩后中文与细线仍可读，04 五个淡灰空工具箱仍清晰可辨。四张均为所要求的交付图，无可选弃图。

## 原图保留与哈希

### 01

- 原图：`/Users/jason/.codex/generated_images/01a12b7d-48ca-7182-bd93-54843d46182b/exec-1c72dbde-401c-42da-8d3f-bbc65e9bd0de.png`
- 原图尺寸：1672 × 941；1,343,118 字节。
- 原图 SHA-256：`7166d3924d8d592c4e3f4e5e9a0375129900ce4dd1a005417a0f334e1befe9fa`
- 最终图 SHA-256：`22aa06e41c29cd6f2c344ccfa518a2a873f13f8efdde16f7e6c80df948c4c972`

### 02

- 原图：`/Users/jason/.codex/generated_images/01a12b7d-48ca-7182-bd93-54843d46182b/exec-0b399452-e5e0-4306-bfd5-19a3ad51997a.png`
- 原图尺寸：1672 × 941；1,311,239 字节。
- 原图 SHA-256：`05e0a1862fc49df37b7087ad179b47d30776b5a09e6c45151916280f1c73f658`
- 最终图 SHA-256：`6a2bea22bc1a1e87d2fd57bc7496a90b84887b35c6d3a3bc4c27b96420f84d9a`

### 03

- 原图：`/Users/jason/.codex/generated_images/01a12b7d-48ca-7182-bd93-54843d46182b/exec-5befeb36-58b5-40a3-8db4-b80cd54833c6.png`
- 原图尺寸：1672 × 941；1,226,962 字节。
- 原图 SHA-256：`1f7e5cc96ff3d3bffe65ea9e509b0d792d349bc490ff2735b7d93a7415f86f35`
- 最终图 SHA-256：`032fb3ca86ed919e0c178617ad128c4c10dd376aa49a213e1cb62a58dfcc3fb9`

### 04

- 原图：`/Users/jason/.codex/generated_images/01a12b7d-48ca-7182-bd93-54843d46182b/exec-7bc28676-39fd-415d-bceb-8cf8954caf6b.png`
- 原图尺寸：1672 × 941；1,252,408 字节。
- 原图 SHA-256：`ccc2418dc1c0eade8f735aae31b0b72e4e271c45b30de9259765ae4f85991394`
- 最终图 SHA-256：`02fbf87be64c0b54a48ed0c1f51a724db8d27128ca5d397bd0d139c3098f8014`

## 正文与 banner 摘要对照

- 文件：`src/content/blog/ai-speech-six-frontiers-open-source.md`
  - 初始：`f868f2704a02963524bf2c03c6b2702d99a159e415e9771fa7a92123a5d5ea71`
  - QA 写入时：`ea9661c04cfdb0edef2a06157313814003b54d67f2c7c94dfc337058521c08f6`
  - 状态：检测到并发改动；本轮未写入该文件。
- 文件：`src/assets/images/ai-speech-six-frontiers-open-source-banner.jpg`
  - 初始：`026a0e52129b43e2608c6cf9f1a7f75fbe2fbc7c1ff4218eefe99d437c1b93c1`
  - QA 写入时：`026a0e52129b43e2608c6cf9f1a7f75fbe2fbc7c1ff4218eefe99d437c1b93c1`
  - 状态：摘要一致。

## 提示词存档

内置生成模式。各单图调用使用共同前缀 + 对应内容，以下保存实际提示词。

### 共同前缀

```text
Generate exactly ONE standalone 16:9 horizontal Chinese body illustration for a serious speech AI research article. Asset type: minimalist editorial hand-drawn illustration, not an infographic slide. Canvas 1536x864 or another exact 16:9 size. Pure opaque white #FFFFFF background from edge to edge. Black fine, slightly wobbly pen lines; no paper texture, no shadows, no gradients, no colored wash. A lot of untouched white space, at least 45%, with main scene using only middle 50-60% of canvas and generous margins. Small handwritten Chinese annotations in red/orange/blue. No heading anywhere, particularly none top-left; no frame or panel border, no montage, no PPT, no architecture grid, no complex flowchart, no commercial vector aesthetic, no childish mascot art.
Recurring protagonist 小M / Xiao-M: one deadpan mushroom worker with a red dome cap containing exactly four white round spots, black hand-drawn outline; cream stem body, two small black dot eyes, thin arms and legs, neutral serious face, no cute smile or sparkles, flat red fill. Xiao-M must actively perform the core action, cannot merely watch. Keep this same identity in each separate illustration. Every prop drawn simply in black, sparse orange/red/blue only when meaningful. Render only the requested few Chinese phrases, accurately. Invent the described fresh physical metaphor, not stock architecture diagrams. 
```

### 01

```text
Scene: a strange two-hand acoustic workbench with Xiao-M in the center. To the left, a wide listening funnel stays open, receiving a small incoming blue speech pebble with two little wave marks; Xiao-M's left hand holds the listening mechanism's valve open. To the right, a tiny crank-driven playback bellows with a loudspeaker mouth is mid-speech, three light sound strokes leaving its mouth. Xiao-M's right hand is decisively pulling its RED physical stop lever as the incoming speech pebble enters the listening funnel. This depicts simultaneous active listening and speaking, with interrupt cancellation of old playback. The listening funnel remains open while playback stops. Few orange motion strokes around the lever, an orange pause mark near outgoing sound is enough; no spaghetti connections. Near the main workbench write “边听边说” in blue and beside the red brake write “插话即停” in red. A very small subordinate physical doodle in the bottom-right quiet area: a single reversible mouth-ear funnel with a shutter switching position, visually showing listening then speaking rather than both at once, label only “轮流” in black. This is a simple secondary contrast inside ONE cohesive illustration, not separate comic panels or a montage. No other text, no numbers, no redundant characters.
```

### 02

```text
Scene: Xiao-M has climbed between three transparent audio-buffer jars on an otherwise empty surface, pressing a plain analog stopwatch to one jar to measure its waiting sound-pebbles while inspecting the other jars. Jars are unevenly spaced like physical laboratory containers, not diagram nodes. Each jar contains two or three small blue sound-pebbles held above its closed bottom hatch, visibly waiting to be released. The three jar labels, accurately hand written in small blue, are “等停顿”, “排队”, “待播放”. Xiao-M actively tests the waiting jar with the stopwatch in one hand, another hand lightly probes its latch. The stopwatch has only a needle and a few unnumbered tick marks, no digits. Near the jars a SMALL crank computation wheel spins very fast with sparse orange motion strokes; this is visibly fast while the sound remains in the jars. A compact red handwritten caution near Xiao-M reads exactly “算得快 ≠ 回得快”. Keep labels attached to their objects, not a title. One coherent sparse hand-drawn scene, ample clean white. No pipeline arrows, no elaborate wiring, no timing figures, no statistics, no milliseconds, no clocks with numbers. The core point is waiting along the audio path can dominate despite fast computation.
```

### 03

```text
Scene: Xiao-M is kneeling in a sparse improvised specimen inspection area, holding a large black-line magnifying glass DIRECTLY over a separate paper license tag. There are exactly THREE visibly different independent physical artifacts, unevenly placed rather than gridded: on the left a small folded source-code booklet with a tiny black curly-brace doodle and its OWN hanging license tag reading “代码”; near the middle a small stacked weight slab/parameter brick with its OWN attached license tag reading “权重”; on the right a little audio-data spool with its OWN attached license tag reading “数据”. These three objects never share a wrapping, stamp or common tag. Each tag tied only to its own artifact with a short string, not to the others. Xiao-M's hand pulls the middle tag forward and the magnifier scrutinizes that specific tag, visually doing the checking rather than passively standing nearby. On each tag a few simple illegible-rule strokes suggest separate terms, but render no fake license names or pseudo-writing. One short red handwritten note near the lens reads “分别核对”. Tags in black with a tiny blue corner mark or tiny red line, not solid colored cards. Lots of white whitespace, no heading, no flowchart arrows, no tick stamps, no universal “开源” label, no license claims, no logos, no large information panels. Communicate three separately licensed artifacts, not one universal open-source permission.
```

### 04

```text
Scene: Xiao-M sits seriously at ONE small measured experiment mechanism, a quirky hand-cranked acoustic test jig on a short table. A single blue sound-pebble is clamped in the jig. Xiao-M actively adjusts its sole ORANGE screw/knob with one hand while the other hand records observations on a plain small clipboard with only three tally strokes, no numbers, no graph, no data claims. Beside the jig is a simple unnumbered measuring scale so measurement is physically visible. This ONE rig is in strong black hand-drawn lines. A short blue note attached near the sole adjustable knob reads “只改一处”; a short red note beside the clipboard reads “测了再说”.
Off to the right, away from the active bench, exactly FIVE small EMPTY OPEN toolboxes sit idle, faint light-gray black-pencil outlines, white interiors clearly showing no machines inside. Group loosely as three further-back and two nearer, not a formal grid, not stack obscuring the count. All five boxes must be independently visible, with no labels, no numerals, no names, no tools, no cables connecting them. Keep their contrast very low; they are background possibilities, not active systems. No other boxes. Keep this uncluttered and quiet: one protagonist, one controlled measured rig, five faint abandoned empty toolboxes. The image explains concentrating on a single reproducible controlled project instead of training six systems at once. No six-panel layout, no busy count labels, no arrow network, no headings, no extra text.
```
