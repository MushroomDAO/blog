# DeepSeek Super-agent 工程指南：小M正文插图

日期：2026-10-31。依据 `src/content/blog/deepseek-superagent-engineering-guide.md`，使用 `mycelium-mushroom-illustrations` skill 与内置 `image_gen`，分别生成三张独立原图；未使用参考图片，也未生成拼图。

三张均为纯白背景、红帽白点与米白菌柄的小M参与核心动作、少量中文标签的手绘概念图。无品牌标志或产品 UI 截图。三张全部为交付图，没有可选或废弃图。

## 最终文件校验

| 图 | 尺寸 | 字节数 | PNG 调色板条目 | 实际使用颜色 | 重复调色板项 | 960×540 回退 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 01 | 1120×630 | 41792 | 48 | 48 | 0 | 否 |
| 02 | 1120×630 | 43516 | 48 | 48 | 0 | 否 |
| 03 | 1120×630 | 71302 | 48 | 48 | 0 | 否 |

处理：Pillow 12.3.0；原图转 RGB 后以 Lanczos 缩放到 1120×630。将三通道均 ≥247 的近白像素还原为精确 #FFFFFF，再用无抖动 median-cut 量化至 48 色。合并重复 RGB 调色板索引、重映射全部像素，并移除 PNG PLTE 的未使用补齐项，重算 CRC；PNG optimize、zlib 压缩级别 9。解码后检查尺寸、索引、白色背景、颜色数和 PLTE 唯一性。三张均低于 90,000 字节，无需回退。

视觉复核：最终 PNG 已逐张打开检查，中文可读，核心动作与正文对应；第三幅明确保留“待验证”。未修改正文或封面，未查看或计算封面哈希，未部署、未提交。原始生成文件保持原样。SHA256 分别针对下列原始 PNG 与最终 PNG 的文件字节。

## 01：事件分流与统一交付

图注：小M把持续来源事件分流到彼此独立的 Worker 工作台；各工作台的任务回报汇入同一个面向用户的交付口。概念示意，不代表完整生产自治。

- 原始路径：`/Users/jason/.codex/generated_images/01a192c4-38b5-7f60-bef1-f31d10ed0219/exec-687b5f00-971c-4e42-aba4-421da2d59f9f.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/deepseek-superagent-engineering-guide-fig-01.png`
- 原始 SHA256：`5ee0e6534233cc8ffdb36629c2ef2416f5bfa98694013908c3322fde71941e66`
- 最终 SHA256：`9bc33fd7c4be675d2c44ff79faafa2af365d7b88c020770e0a8f02d9042c6396`

实际提交的生成提示词：

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article body illustration, not a composite sheet. Pure white #FFFFFF background, minimal slightly wobbly BLACK hand-drawn thin pen lines, sparse flat RED/ORANGE/BLUE accents, absolutely no shadows, gradients, paper texture or noise. Large calm margins, at least 40% empty white space, subject density only 40–60% of canvas. Serious absurd low-tech product sketch, no formal flowchart boxes, no PPT infographic, no commercial vector illustration, no children's cartoon, no cute mascot poster, no logos, no product UI, no screenshots. No top-left heading, no title.
XiaoM is the main actor: a small mushroom creature with flat RED rounded dome cap, 3–5 WHITE polka dots, thin black outline, cream/off-white stem body, two small BLACK dot eyes on pale stem, thin arms and legs, deadpan serious expression, never solid black, never shiny or 3D. Repeated XiaoM figures may enact separate roles. XiaoM must physically perform the core actions. Orange lines show forward event/action paths; blue lines show returning evidence/reports/receipts. Only small, crisp, legible short Chinese annotations as specified, no Latin letters or additional text. All elements comfortably inside the 16:9 frame. These are conceptual engineering sketches, NOT a claim of shipped production, full autonomy, completed deployment, or universal exactly-once guarantees.
Theme: ongoing source events routed to separate isolated Worker benches, reports returned to ONE user-facing delivery mouth.
Composition: one coherent playful workshop, viewed straight on in an open white field. At left a little source pipe keeps dropping three separated paper event slips; use a tiny trailing slip to imply ongoing events. A central XiaoM actively turns a small sorting paddle that diverts orange paths to TWO visibly separated small workbenches, one above the other, with plenty of space between them. One XiaoM at each bench handles its own paper task. Separate benches are not connected to each other. From both benches blue report sheets follow return paths into the same hollow speaking-mouth-shaped hatch on the RIGHT. A delivery XiaoM at this single mouth gathers the two report sheets and offers one bundle toward a simple black outline human profile at far right. The mouth is an abstract physical delivery opening, not a second agent platform. All worker reports go ONLY to that one mouth, no Worker directly addresses the human. Clearly distinguish orange incoming paths from blue report returns, keep only necessary short arrows. No computer screens.
Exact Chinese labels, each once and located adjacent to the relevant object: “持续事件” beside source pipe, “分流” beside sorting paddle, “独立工作台” between the separate benches, “任务回报” near blue returning sheets, “统一交付口” beside the one mouth, “用户” by human profile. Do not draw completion ticks or deployment symbols.
```

## 02：持久化、发送与回执核查

图注：小M先将状态与待发送动作共同持久化，再执行发送；回执不明确时先核对已有消息，再决定是否重试。此机制不构成跨系统全局 exactly-once 保证。

- 原始路径：`/Users/jason/.codex/generated_images/01a192c4-38b5-7f60-bef1-f31d10ed0219/exec-26fa08f5-83eb-4a5c-a059-c6292cf19a1e.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/deepseek-superagent-engineering-guide-fig-02.png`
- 原始 SHA256：`724338dda8c87fd3fffc325e0067a64de3d5b8c89b4c0f1ea23fc24967824a43`
- 最终 SHA256：`b8d9832e329789cd804b9a46c2c8fef29a53404f46e66aae59622e9cf15ae137`

实际提交的生成提示词：

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article body illustration, not a composite sheet. Pure white #FFFFFF background, minimal slightly wobbly BLACK hand-drawn thin pen lines, sparse flat RED/ORANGE/BLUE accents, absolutely no shadows, gradients, paper texture or noise. Large calm margins, at least 40% empty white space, subject density only 40–60% of canvas. Serious absurd low-tech product sketch, no formal flowchart boxes, no PPT infographic, no commercial vector illustration, no children's cartoon, no cute mascot poster, no logos, no product UI, no screenshots. No top-left heading, no title.
XiaoM is the main actor: a small mushroom creature with flat RED rounded dome cap, 3–5 WHITE polka dots, thin black outline, cream/off-white stem body, two small BLACK dot eyes on pale stem, thin arms and legs, deadpan serious expression, never solid black, never shiny or 3D. Repeated XiaoM figures may enact separate roles. XiaoM must physically perform the core actions. Orange lines show forward event/action paths; blue lines show returning evidence/reports/receipts. Only small, crisp, legible short Chinese annotations as specified, no Latin letters or additional text. All elements comfortably inside the 16:9 frame. These are conceptual engineering sketches, NOT a claim of shipped production, full autonomy, completed deployment, or universal exactly-once guarantees.
Theme: write durable state and intended action together BEFORE sending; inspect ambiguous delivery receipt BEFORE deciding whether to retry.
Composition: a sparse left-to-right paper-dispatch workshop with one coherent narrative. At left a XiaoM uses a pen to inscribe TWO adjacent spaces in ONE open bound durable ledger resting on a small solid storage drawer. The spaces are headed “状态” and “待发动作”; both are visibly stored together. A single orange arrow leaves the committed ledger and reaches a second XiaoM at center who pushes a paper message into a simple outbound mail slot marked “发送”. Further right the delivery reply is a small receipt with a blue QUESTION MARK, label “回执不明”. A third XiaoM holds a magnifying glass over this uncertain receipt and a previously sent message in an archive, actively comparing them. The path ends at inspection, not at an automatic resend loop: a small retry envelope waits behind a closed simple bar at far right. Label under the inspector “先核对，再决定重试”. Do not imply all sends fail; ambiguity is the branch being examined. No duplicate outgoing messages, no success badges, no infinite loops, no guaranteed exactly-once wording.
Only these SIX Chinese text labels: “状态”, “待发动作”, “落盘后”, “发送”, “回执不明”, “先核对，再决定重试”. “落盘后” sits on the arrow AFTER the ledger and BEFORE sending. Keep labels readable and compact. Orange forward action, blue uncertain receipt/inspection.
```

## 03：分阶段验证与证据采集

图注：建议先离线回放，再接入受控 Worker，随后核验交付；各阶段分别收集事件记录、测试与草稿、收据与产物。图中交付阶段标为“待验证”，不表示已经部署完成。

- 原始路径：`/Users/jason/.codex/generated_images/01a192c4-38b5-7f60-bef1-f31d10ed0219/exec-a9668227-0a6a-4c98-80a4-f2e4d819a1d4.png`
- 最终路径：`/Users/jason/Dev/mycelium/blog/src/assets/images/deepseek-superagent-engineering-guide-fig-03.png`
- 原始 SHA256：`23a90446247dc561f06845e4ccddcfbe4799496ee73b02d3b3c5e3fc154a2117`
- 最终 SHA256：`55157a04757c528f6405bd86d9812ac6c2fd8c6930d36af828afcbcc92d30e7a`

实际提交的生成提示词：

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article body illustration, not a composite sheet. Pure white #FFFFFF background, minimal slightly wobbly BLACK hand-drawn thin pen lines, sparse flat RED/ORANGE/BLUE accents, absolutely no shadows, gradients, paper texture or noise. Large calm margins, at least 40% empty white space, subject density only 40–60% of canvas. Serious absurd low-tech product sketch, no formal flowchart boxes, no PPT infographic, no commercial vector illustration, no children's cartoon, no cute mascot poster, no logos, no product UI, no screenshots. No top-left heading, no title.
XiaoM is the main actor: a small mushroom creature with flat RED rounded dome cap, 3–5 WHITE polka dots, thin black outline, cream/off-white stem body, two small BLACK dot eyes on pale stem, thin arms and legs, deadpan serious expression, never solid black, never shiny or 3D. Repeated XiaoM figures may enact separate roles. XiaoM must physically perform the core actions. Orange lines show forward event/action paths; blue lines show returning evidence/reports/receipts. Only small, crisp, legible short Chinese annotations as specified, no Latin letters or additional text. All elements comfortably inside the 16:9 frame. These are conceptual engineering sketches, NOT a claim of shipped production, full autonomy, completed deployment, or universal exactly-once guarantees.
Theme: a recommended staged validation path: OFFLINE REPLAY, then CONTROLLED WORKER, then VERIFIED DELIVERY; collect evidence at every stage. This is a plan with later-stage verification still pending, not completed deployment.
Composition: three loosely spaced low-tech trial stations left to right, with short orange directional arrows between them, NO enclosing panels, no podium, no rising chart. At the first, XiaoM turns a hand-crank paper reel replaying event cards into a little specimen tray; under it a paper evidence pocket contains event records. At the second, XiaoM works on a draft patch at a small bench inside a simple low waist-high rail with a visible closed latch; no computer screen. Under it a second paper evidence pocket holds test strips and a draft sheet. At the third, XiaoM carefully compares one outgoing delivery sheet to a returned receipt using a magnifying glass before a simple outlet; under it a third evidence pocket holds matched receipt/artifact sheets. THIRD STATION has a small red hand-lettered tag “待验证”, not a green tick. The evidence pockets must visibly belong to all THREE stations and not be empty decoration; XiaoM must handle the specimens at each stage. No celebration, no deployment rocket, no production server, no universal completion or all-green status.
Only SEVEN small legible Chinese labels: above stations “离线回放”, “受控执行”, “核验交付”; by their evidence pockets “事件记录”, “测试与草稿”, “收据与产物”; and small red “待验证” adjacent to the last station. Leave spacious white margins.
```
