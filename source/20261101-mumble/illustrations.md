# Mumble 正文配图生成与核对报告

日期：2026-11-01。

已读取 `src/content/blog/mumble-phone-walkie-talkie-guide.md`，应用 `mycelium-mushroom-illustrations` 及其风格、角色、构图、提示词和 QA 参考；通过内置 `image_gen` 恰好调用 3 次，每次独立生成 1 张，共交付 3 张正文配图，无拼图、无额外候选。

## 交付文件

| 图 | 文件（仓库根目录相对路径） | 尺寸 | 字节数 | 调色板颜色数 | 纯白像素占比 |
|---|---|---|---:|---:|---:|
| 01 | `src/assets/images/mumble-phone-walkie-talkie-guide-fig-01.png` | 1120×630（16:9） | 21,624 B | 48 | 95.76% |
| 02 | `src/assets/images/mumble-phone-walkie-talkie-guide-fig-02.png` | 1120×630（16:9） | 33,648 B | 48 | 91.95% |
| 03 | `src/assets/images/mumble-phone-walkie-talkie-guide-fig-03.png` | 1120×630（16:9） | 41,040 B | 48 | 90.47% |

3 张均为 PNG，均严格小于 90,000 B；文件可重新解码，四角均为 RGB(255,255,255)。纯白像素占比是文件像素统计，不等于构图留白面积。

## 逐张画面核对

1. **共同服务器语音频道**：三部手机的橙色连接全部汇入同一个明确画出的服务器，小M正在接入第三根线。标注仅“服务器”“同一频道”；没有手机之间直接通信的路径。服务器面板上的小波纹标记随“同一频道”标注表示频道，整体不表达手机无线电。
2. **凭证分开与双通路**：小M一手一把不同钥匙，分别放进“成员”“管理员”两个独立盒子；手机与服务器间同时存在清晰的 TCP、UDP 两条连接。钥匙没有绑定成一串，也没有把不同角色钥匙错误对应到某一协议。标注仅“成员”“管理员”“TCP”“UDP”。
3. **服务器解包再封装**：左侧手机送入带锁封套；小M位于服务器中转台内部，一手取出可见波形，一手把波形装入新封套，随后带锁封套分别送到右侧两部手机。标注仅“服务器”“服务器可见”，表达客户端与服务器之间的传输加密不等于服务器不可见，不画成端到端密封直通。

三张均使用红色菌盖、白圆点、米白菌柄、黑点眼与细手脚的小M；小M分别执行接入、分开存放钥匙、拆包与重新封装的核心动作。背景归白，黑色手绘线稿与少量色彩，无左上角标题、复杂 PPT 架构、文章截图。三张均为指定占位的正式交付，无可选图。

## 压缩方式

使用 Pillow 12.3.0，无 NumPy。原图 1672×941；保留原文件，在工作区另存压缩成品。先归白中性高亮，再用 Lanczos 缩放到 1120×630，缩放后再次归白，最后 48 色 MEDIANCUT、无抖动、PNG optimize、compress_level=9。归白条件为 RGB 三通道最小值 ≥210 且最大最小差 ≤6，减少背景纹理，同时保留偏暖的米白菌柄。

关键处理步骤：

```python
def whiten(image):
    image.putdata([
        (255, 255, 255) if min(pixel) >= 210 and max(pixel) - min(pixel) <= 6
        else pixel for pixel in image.get_flattened_data()
    ])
    return image

image = whiten(source.convert("RGB"))
image = whiten(image.resize((1120, 630), Image.Resampling.LANCZOS))
image = image.quantize(colors=48, method=Image.Quantize.MEDIANCUT,
                       dither=Image.Dither.NONE)
image.save(destination, format="PNG", optimize=True, compress_level=9)
```

## 原图与校验值

内置工具原图保留在原始生成路径，没有删除或覆盖：

- 图 01：`/Users/jason/.codex/generated_images/01a19489-59f4-7b31-a269-719f4ab07fba/exec-8290f09c-1046-456f-8e1e-e1e53f76e774.png`
  - 成品 SHA-256：`dbf95766e196c3cc1bc2e924930a0bd1cb64fdb0dde2927b89d1b037f33f02eb`
- 图 02：`/Users/jason/.codex/generated_images/01a19489-59f4-7b31-a269-719f4ab07fba/exec-c43d4d3a-9424-4033-a605-ac229322779d.png`
  - 成品 SHA-256：`ff01aabd48753d7da18397f9ee3b90950f86d6aa4bbb3490fbc08bb6b48377a3`
- 图 03：`/Users/jason/.codex/generated_images/01a19489-59f4-7b31-a269-719f4ab07fba/exec-a1c03e79-8034-464b-bf2a-01d7f5122975.png`
  - 成品 SHA-256：`741033883bde1a72d8b1e9d68e242f1c634fd60b39ab877e8dcf623597d4fc23`

## 文章与 banner 未修改

三个既有图路径在中英文正文各引用 1 次，文件名与占位完全一致；共 3 个唯一插图文件、6 次正文引用。未修改文章、未生成或修改 banner、未执行构建或发布。文章和既有 banner 的处理前后 SHA-256 一致：

- 文章：`ee5f9f22443e417da8b899e2f82942323c71839909c5005eac7b9c47ae771be6`
- 既有 banner：`897e12c61eb8ed8048d9a1fc782d6504c72cd1c0c3e9d33419d8ab5994c8c11a`

## 实际生成提示词

执行方式：内置 `image_gen`，每张新生成；`transparent_background=false`，不传参考图；未使用 CLI/API 降级路径。

### 图 01

```text
Generate exactly ONE standalone 16:9 landscape illustration for the body of a Chinese technical article, not a cover. Topic: phones communicate through one shared Mumble server voice channel, never direct phone radio.
Visual style: perfectly pure white #FFFFFF background, minimalist thin slightly wobbly BLACK hand-drawn pen outlines, sparse flat red/orange/blue accents, huge clean white margins (at least 40% blank space). No paper texture, grain, shading, shadows, gradients or background wash. NOT a PPT, formal architecture diagram, commercial vector illustration, childish cartoon or cute mascot poster. No title, no border, no UI screenshot.
Central action: Xiao-M is a serious deadpan mushroom switchboard operator physically plugging the LAST of three simple phone connection cords into the SAME small server cabinet. Two phone cords are already plugged into this cabinet. Three clearly recognizable smartphones occupy a loose shallow arc around this single central machine, all connected to it, no lines between phones. The small server has two simple horizontal rack slots and, on its front, ONE shared channel receptacle with a small speech/sound-wave mark. Xiao-M is central and visibly using both thin arms to seat the plug, so it is doing the networking rather than posing nearby. Connection cords are sparse orange hand-drawn lines representing network paths, NOT literal radio. No antennas, radio waves, towers, walkie-talkies, clouds, direct phone-to-phone links or giant flowchart arrows.
Character identity: ONE Xiao-M, rounded flat RED mushroom cap with exactly 4 WHITE circular spots, thin black outline, CREAM/off-white stem body, tiny BLACK dot eyes, thin arms and legs, blank serious expression, not smiling, not glossy, not solid black.
Use just two small legible handwritten annotations beside the shared machine, in blue/black Chinese: "服务器" and "同一频道". No other words. All meaningful objects well inside wide blank canvas edges. A clean absurd hand-drawn product sketch, sparse and immediately readable.
```

### 图 02

```text
Generate exactly ONE standalone 16:9 landscape Chinese technical article body illustration, not a cover. Topic: keep ordinary member credentials separate from administrator credentials and make BOTH TCP and UDP network paths available to the same server.
Pure white #FFFFFF background, fine slightly irregular BLACK hand-drawn ink outlines, very sparse flat RED, ORANGE, BLUE accents. At least 40% empty white space. No grain, paper texture, gradients, shadows, shading or color wash. No title, frame, PPT boxes, formal architecture diagram, commercial vector illustration, cute mascot poster, complex UI or decorative symbols.
Make ONE compact hand-drawn scene: a small server cabinet on the right, a single recognizable phone on the left, TWO clearly separate gently curving connection paths between phone and server, one blue and one orange, each visibly connected at BOTH ends. Label the blue path exactly "TCP" and the orange path exactly "UDP", small legible handwriting, no port numbers needed. In front of the cabinet, Xiao-M is actively placing two visibly DIFFERENT keys into TWO small SEPARATE open storage boxes, one key in each hand, with each key just above its own box opening. The boxes do NOT touch and keys are not on a common key ring. One ordinary simple small key and one larger distinct administrative key. Give these boxes just the short legible handwritten Chinese labels "成员" and "管理员". The keys represent credentials, NOT keys that open the two protocol routes: do not connect either key or box to a particular network path. Both paths belong to the same phone-server connection. Keep the cabinet, paths and key storage as one quiet physical vignette, no additional panels or modules.
Xiao-M must perform the key-separation action at the center: ONE mushroom with rounded flat RED cap, exactly 4 WHITE circular spots, CREAM/off-white stem with black sketch outline, tiny BLACK dot eyes, skinny arms and legs, blank deadpan serious expression. No smiles, large eyes, solid black body, 3D rendering or realistic mushroom.
Exactly four tiny labels total: "成员", "管理员", "TCP", "UDP". No other text, no banners. Sparse and slightly absurd but immediately understandable.
```

### 图 03

```text
Generate exactly ONE standalone 16:9 landscape illustration for a Chinese technical article body, not a banner. Core claim: Mumble transport encryption ends at the server; the server decrypts incoming voice packets and encrypts them again for recipient phones. It is NOT encryption that hides the content from the server.
Minimalist fine slightly wobbly BLACK hand-drawn pen lines on absolutely pure white #FFFFFF, sparse flat RED cap, ORANGE paths, BLUE envelopes. At least 40% white negative space. No texture, paper grain, shading, gradients, shadows, background wash, commercial vector look, childish cute art, PPT, flowchart boxes, UI or title.
One simple absurd physical scene: a server cabinet becomes a small OPEN-FRONT relay workbench, clearly labeled with only the small handwritten Chinese word "服务器". Xiao-M works INSIDE this server workbench. A single phone at left sends a closed blue envelope bearing a tiny padlock icon along one thin orange path into the workbench. At Xiao-M's left hand there is an OPEN envelope with its flap visibly lifted and the voice payload taken OUT: a loose clearly visible black audio waveform strip above the workbench. With the other hand Xiao-M is putting a matching audio waveform strip INTO a DIFFERENT outbound blue envelope at the right end of the same workbench, closing/resealing it for delivery. Two sealed outbound envelopes bearing tiny padlock icons continue along two short thin orange paths to TWO recipient smartphones at right. Keep the decryption/re-encryption action central and obvious: sealed on the network, OPEN AND READABLE within the server, then sealed again for recipients. The waveform should be plainly visible outside its envelope at server, no opaque safe, no locked box enclosing the server, no end-to-end tunnel, no message bypassing server. Do not imply someone permanently stores or records it. No recording symbols, headphones, spies or extra people.
ONE Xiao-M performs BOTH unpacking and repacking as the main worker: flat rounded RED mushroom cap with exactly 4 WHITE circular spots, pale CREAM stem body with black hand-drawn outline, tiny BLACK dot eyes, skinny arms and legs, calm blank serious expression, not cute or smiling, not solid black. Just one additional short red handwritten annotation under the open workbench: "服务器可见". Total only two short labels, no English, no paragraphs. No multi-panel comic. All objects inside generous clean white edges.
```
