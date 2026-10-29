# Agent Relay 正文配图记录

- 日期：2026-10-29
- 对应正文：`src/content/blog/agent-relay-coding-agent-collaboration.md`
- 使用 skill：`/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md`
- 生成方式：内置 `image_gen`，三张分别调用，一次一张，共三张；不是 banner。
- 交付：三张独立 PNG，均为 **1120 × 630、精确 16:9**，纯白背景、黑色手绘、小M红帽白点、少量中文标注，无标题。
- 三张均是本次指定锚点的正式交付图，无可选图。
- 本任务没有编辑正文、生成封面、部署或提交。只新增配图、原图副本和本文档；工作区其他改动不属于本任务。

## 成品与用途

| 图 | 成品（相对于本文件） | 字节数 | 用途与表达边界 |
| --- | --- | ---: | --- |
| 01 | [fig-01.png](../../src/assets/images/agent-relay-coding-agent-collaboration-fig-01.png) | 57357 | 两台电脑的小M使用同一个工作空间消息槽传递消息，人类少做转述。未拼合的代码片和“合并仍需复核”明确表示：消息通信不保证自主合并正确。对应四类能力介绍后的消息协作锚点。 |
| 02 | [fig-02.png](../../src/assets/images/agent-relay-coding-agent-collaboration-fig-02.png) | 49996 | 小M从授权范围内的文件抽屉取出数据；锁住的抽屉表示范围限制，外部写回保留“适配器”与“写回检查”。文件入口不会消除提供商 API、鉴权、一致性及结果核验。对应 Relayfile 段落。 |
| 03 | [fig-03.png](../../src/assets/images/agent-relay-coding-agent-collaboration-fig-03.png) | 66650 | 小M携任务产物处于确定性测试与人工批准门之间，人类实际操作批准开关。外围另设带锁围栏作为真实权限边界；围栏外松散纸张“权限声明”及“声明≠强制”说明声明本身不执行限制。这是建议配置的流程，不声称安装后默认获得这些门禁。对应 Flows 段落。 |

## 原图保存

生成器原始文件保持原位；下列仓库内副本与原始文件逐字节一致，没有对原图做压缩或覆盖。

| 图 | 仓库内原图副本 | 原始尺寸 | 原始字节数 |
| --- | --- | --- | ---: |
| 01 | [agent-relay-fig-01-original.png](illustration-originals/agent-relay-fig-01-original.png) | 1672 × 940 | 1279507 |
| 02 | [agent-relay-fig-02-original.png](illustration-originals/agent-relay-fig-02-original.png) | 1672 × 941 | 1180820 |
| 03 | [agent-relay-fig-03-original.png](illustration-originals/agent-relay-fig-03-original.png) | 1672 × 941 | 1747889 |

生成器原始路径：

1. `/Users/jason/.codex/generated_images/01a186a5-e49a-7041-9b83-32957b9c9e42/exec-cd18dfb3-a642-499b-9e4f-77b92fcaa2e4.png`
2. `/Users/jason/.codex/generated_images/01a186a5-e49a-7041-9b83-32957b9c9e42/exec-b38783cb-1a81-4218-a8ee-42729663d527.png`
3. `/Users/jason/.codex/generated_images/01a186a5-e49a-7041-9b83-32957b9c9e42/exec-a5a58bfe-57c6-46c6-bad4-f84193766e0b.png`

原图副本 SHA-256：

```text
01 d17dbc62a0b9e3c772b8da5b84eb7396d77b7f1fb083b063f6316a14e79bb990
02 3d514e4bb4bc6c7e38a9d3834a2e3fd9ab7655e2410f6aa77b10e68f652bcda1
03 1dd275a6795509d3622e8ca7cd0a7366cad492926caaa1232d631e794d7c5c2a
```

## 压缩与检查

- 使用 Pillow 处理交付副本：将 RGB 三通道都不低于 235 的近白背景像素统一为纯白，Lanczos 缩放至 1120 × 630，再保存为优化索引 PNG（compress_level=9）。
- 图 01、02：64 色中位切分、无抖动；图 03：16 色固定调色板、无抖动及 4 位 PNG，以保留红帽、蓝色批注与橙色路径，避免自动调色导致主体颜色变暗。
- 图 03 的固定 RGB 调色板：`[(255,255,255),(0,0,0),(45,45,45),(90,90,90),(140,140,140),(185,185,185),(220,220,220),(235,45,40),(170,35,30),(255,130,55),(200,90,45),(20,70,170),(65,140,220),(195,220,245),(255,244,224),(165,110,70)]`。
- 重新打开全部成品，验证真实 PNG 格式、像素尺寸、精确 16:9、白色角点及每张严格小于 90000 字节。
- 人工视觉检查：三张均有红帽白点的小M参与核心动作；中文标注可读；无标题；消息、适配器检查、人工审批与独立权限边界的表意符合指定锚点。压缩过程中没有增添或删除语义元素。

## 实际生成提示词

以下为三次内置工具调用的完整提示词；每次 `transparent_background=false`。

### 图 01

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, 1536x864 or another exact 16:9 canvas. Pure flat white #FFFFFF background. Minimalist slightly wobbly BLACK hand-drawn pen line art, sparse flat red/orange/blue accents, generous uninterrupted white space (at least 40%), main scene around middle 50-60% of canvas. Clean absurd editorial product sketch, dry deadpan humor, not cute, not childish. No paper texture, no off-white background, gradients, shadows, dense architecture, formal flowchart, PPT, commercial illustration, decorative frames, logos, watermark. NO TITLE anywhere, especially top-left. Chinese labels must be few, short, legible and rendered exactly as specified. XiaoM is the active protagonist: classic mushroom, rounded RED cap with 3-5 WHITE spots, pale CREAM stem body, thin black hand-drawn outline, two tiny BLACK dot eyes, thin stick limbs, serious blank expression; never solid black, no kawaii or 3D. Red cap is character identity color; orange only for transmission/motion, blue for explanatory labels. Invent the described physical metaphor, not a conveyor belt, not a mascot standing beside a diagram. Theme: messages among coding agents on different computers within a shared workspace reduce human forwarding; messaging does NOT guarantee autonomous correct code merging.
Composition: A low-tech shared wooden pigeonhole/message trough stretches between two physically separate open laptops, one at the left and one at the right, clearly two separate machines. A small XiaoM at each laptop is actively sliding an envelope into / retrieving an envelope out of the SAME central trough, so the mushroom agents themselves do the communication. A single thin orange route travels through the trough, not through a person. Above the trough, the small blue attached label reads "同一工作空间". On each laptop screen only two tiny black code-like marks, no real UI or logos. A small human figure in black line art sits below-left with idle hands and a little empty forwarding basket; nearby tiny handwritten label "少转述". At the lower right, separate from the message trough, place two small incompatible puzzle-edged code slips with a gap still between them and a red handwritten note "合并仍需复核". These code slips have NOT been merged, and NO success checkmark appears on them. Keep this secondary note small but readable; it must not compete with the main message exchange. Only THREE labels total: "同一工作空间", "少转述", "合并仍需复核". Let the two serious mushroom actors perform the communication; no arrows through the human, no automatic merge machine, no claims of guaranteed correctness. Single integrated illustration, no panels or title.
```

### 图 02

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, 1536x864 or another exact 16:9 canvas. Pure flat white #FFFFFF background. Minimalist slightly wobbly BLACK hand-drawn pen line art, sparse flat red/orange/blue accents, generous uninterrupted white space (at least 40%), main scene around middle 50-60% of canvas. Clean absurd editorial product sketch, dry deadpan humor, not cute, not childish. No paper texture, no off-white background, gradients, shadows, dense architecture, formal flowchart, PPT, commercial illustration, decorative frames, logos, watermark. NO TITLE anywhere, especially top-left. Chinese labels must be few, short, legible and rendered exactly as specified. XiaoM is the active protagonist: classic mushroom, rounded RED cap with 3-5 WHITE spots, pale CREAM stem body, thin black hand-drawn outline, two tiny BLACK dot eyes, thin stick limbs, serious blank expression; never solid black, no kawaii or 3D. Red cap is character identity color; orange only for transmission/motion, blue for explanatory labels. Invent the described physical metaphor, not a conveyor belt, not a mascot standing beside a diagram. Theme: Relayfile presents authorized provider data as scoped file drawers; provider writes still require adapter and checks. Single sparse scene with a strange compact freestanding filing chest, not a software architecture diagram.
Composition: On left-middle a black-outline filing cabinet with only THREE drawers, each drawer's paper tab reads one short Chinese label: "工单", "代码", "文档". The top two drawers are slightly open with a few simple file sheets. The bottom drawer is shut with a small padlock to signify scope, NOT unlimited access. A thin blue dashed outline encloses ONLY this cabinet, attached small label "授权范围". XiaoM in the center is physically half-leaning into the top drawer, with one hand gripping its handle and the other carrying ONE revised sheet toward a plain mechanical fitting in the middle-right. The fitting has mismatched socket shapes on its two ends, visibly acting as an adapter, with the handwritten label "适配器" on its body. Beyond this fitting, a little spring-latched inspection flap on the same short writeback pipe is still CLOSED, with a red short tag "写回检查". The pipe terminates in a small unbranded remote provider box drawn in very simple black outline. ONE orange directional line follows the revised sheet through the adapter toward the closed check flap and STOPS THERE, never bypassing it or implying completed mutation. Keep provider box unlabelled to minimize words. No checkmarks, no autonomous permission claims, no direct unrestricted write arrow from the drawers to the provider. EXACTLY SIX small Chinese labels: "工单", "代码", "文档", "授权范围", "适配器", "写回检查". No Latin text or title. Sparse hand-drawn physical scene, at least 40% pure white.
```

### 图 03

```text
Use case: illustration-story. Generate ONE standalone 16:9 horizontal Chinese article BODY illustration, 1536x864 or another exact 16:9 canvas. Pure flat white #FFFFFF background. Minimalist slightly wobbly BLACK hand-drawn pen line art, sparse flat red/orange/blue accents, generous uninterrupted white space (at least 40%), main scene around middle 50-60% of canvas. Clean absurd editorial product sketch, dry deadpan humor, not cute, not childish. No paper texture, no off-white background, gradients, shadows, dense architecture, formal flowchart, PPT, commercial illustration, decorative frames, logos, watermark. NO TITLE anywhere, especially top-left. Chinese labels must be few, short, legible and rendered exactly as specified. XiaoM is the active protagonist: classic mushroom, rounded RED cap with 3-5 WHITE spots, pale CREAM stem body, thin black hand-drawn outline, two tiny BLACK dot eyes, thin stick limbs, serious blank expression; never solid black, no kawaii or 3D. Red cap is character identity color; orange only for transmission/motion, blue for explanatory labels. Invent the described physical metaphor, not a conveyor belt, not a mascot standing beside a diagram. Theme: a deliberately configured workflow uses deterministic tests AND explicit human approval; actual permission enforcement is an independent boundary. A permissions declaration alone is not enforcement. Do not imply these are automatically provided by installing Agent Relay.
Composition: One coherent low-tech physical miniature work yard on white, rendered as sparse black pen sketch with ample white space above and below. A serious XiaoM actively carries a folded code artifact through the yard from left toward right. Inside the yard stand TWO small different mechanical gates in sequence: first a little test-fixture arch labelled exactly "确定性测试", with a tiny visible terminal exit-code readout "0" and a short open bar; second a separate CLOSED swing barrier labelled "人工批准", whose release handle is visibly held by the hand of a plain human reviewer at the right. XiaoM has passed the test fixture but is WAITING before the closed human approval barrier, holding the artifact; no self-approval, no automatic merge or universal approval claim. Only one short thin orange travel mark on the ground between fixture and waiting XiaoM; do not draw arrows as a formal flowchart.
INDEPENDENT OF BOTH GATES: a sparse continuous waist-high black wire fence surrounds the entire small yard including these gates, visibly returns in perspective, with a proper padlock on its small outer side gate. Small blue tag attached to the FENCE reads "实际权限边界". This fence means enforced credentials/runtime/repository protection; it is not generated by the paper declaration, and the human approval handle cannot unlock this fence.
In foreground outside the fence, one loose curling paper slip rests freely on the ground, labelled "权限声明", with a short red handwritten annotation beside this loose slip "声明≠强制". It has NO lock, NO magical protective aura, NO connection creating or replacing the fence. Make the distinction visually unmistakable: declaration = unfastened loose paper, actual permission boundary = substantial separately locked fence. Keep all forms light and sparse, no elaborate factory. Exactly FIVE Chinese labels: "确定性测试", "人工批准", "实际权限边界", "权限声明", "声明≠强制", plus tiny numeral "0". NO heading or title. Main actor XiaoM has red cap white spots, pale body and black dot eyes, holding actual task output while waiting for a human; human is secondary but plainly operating approval gate.
```
