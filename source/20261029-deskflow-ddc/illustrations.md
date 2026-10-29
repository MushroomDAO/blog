# Deskflow DDC — illustration provenance and checks

Date: 2026-10-29. Exactly three separate illustrations generated in this turn with built-in `image_gen.imagegen` (one call per image; no collage, banner, reused asset or regeneration).

## Inputs and prompt set

Read the complete article `src/content/blog/deskflow-ddc-monitor-keyboard-sharing.md`; the requested `mycelium-mushroom-illustrations/SKILL.md` and all five references: `style-dna.md`, `mushroom-ip.md`, `composition-patterns.md`, `prompt-template.md`, `qa-checklist.md`. Also read the system imagegen skill. No example composition was copied.

Shared prompt constraints: standalone 16:9 article illustration, pure white background, sparse black hand-drawn lines, restrained red/orange/blue, generous white space; serious XiaoM with red cap/white spots, cream stem, black dot eyes, actively performing the core action; few words; no title, realistic app screenshot, PPT layout, watermark or numeric codes.

Prompt briefs:
- **01:** XiaoM operates monitor input selection and the keyboard. Two distinct solid video cables connect two computers directly to separate monitor inputs. A separate orange dashed computer-to-computer LAN route carries only keyboard/mouse symbols, never video or a connection to the monitor.
- **02:** XiaoM inspects the monitor's physical input selection and both cable plugs with a magnifier before using a pairing-key metaphor between the computers. Two continuous video cables retain identifiable endpoints. No connector-to-number mapping or numeric input codes.
- **03:** XiaoM reaches the physical display input button and uses the operable peer laptop's trackpad to select the ordinary in-app stop-sharing command. Hiding the first app window into its tray leaves the keyboard/mouse route active. No independent emergency-stop device or guaranteed recovery is depicted.

## Original generation files

Preserved, unmodified under:
`/Users/jason/.codex/generated_images/01a185ee-0ecb-7951-a41f-03994e7c5daa/`

| Figure | Original PNG |
|---|---|
| 01 | `exec-00c3ddea-8d9a-4426-9e48-1f004d12e543.png` |
| 02 | `exec-3e3610f2-79e8-48d6-a2f8-bfe8b3955e7c.png` |
| 03 | `exec-09c3680c-eaf0-4457-852e-a5d9727cb5de.png` |

Originals: 1672×941. Final PNGs were derived only from these current-turn outputs with ImageMagick: resize to 1200×675, center on a white 1280×720 canvas without cropping, nondithered 96-color palette, normalize near-white pixels to white (2% fuzz), strip metadata, PNG compression level 9. Original provenance files remain available because final optimization strips embedded metadata.

## Final assets and inspection

All files below are in `src/assets/images/`. Original generations and all three compressed finals were individually viewed. Framing, readable wording, XiaoM participation and connection semantics checked manually; PNG signature, dimensions, byte count and white border checked programmatically.

| Filename | Dimensions | Bytes (<90,000) | Exact-white pixels | Visible words / result |
|---|---|---:|---:|---|
| `deskflow-ddc-monitor-keyboard-sharing-fig-01.png` | 1280×720 | 77,349 | 73.63% | 视频线 (twice), LAN; cables and input-event route separate; no streamed-video implication |
| `deskflow-ddc-monitor-keyboard-sharing-fig-02.png` | 1280×720 | 80,432 | 83.11% | 先检查, 再配对; both cables traceable; selector has connector icons, no numeric codes |
| `deskflow-ddc-monitor-keyboard-sharing-fig-03.png` | 1280×720 | 65,269 | 87.47% | 切画面, 隐藏窗口, 仍在共享, 停止共享; hiding differs from stopping; physical button controls picture only |

All three have an entirely #FFFFFF outer border and complete, uncropped subjects. Figure 02's key is symbolic pairing, not a hardware adapter. Figure 03 omits video wiring to focus on recovery; its only dashed route carries keyboard/mouse events. Its stop command remains inside the peer's app, conditional on that computer/application responding. These are conceptual illustrations, not exact hardware-port or product-UI replicas. All three are final requested assets.

SHA-256:
- 01: `93380f8818ecc024456d169a349288e3d201f7260391f7f1edbf518301277a2d`
- 02: `1cec5fd80c81fcb6821a29630978959d30fa0296f90a6fdf6b81c8b0fba76089`
- 03: `3f393efefb7d5ae47ca67f47ff259fbb731dae0635c2ad2e769f3b47bb3233f1`

Scope: this turn wrote only the three requested PNGs and this report; it did not edit the article, deploy or commit. Existing unrelated workspace changes were preserved. The article checksum changed during generation (observed modification time 11:35:51); no command in this turn wrote it, and it was not reverted. Therefore whole-workspace article-immutability verification is not claimed.


Primary publisher note: the observed article edit during generation was the intentional lastPublishedAt publication stamp; the illustration worker did not write the article.
