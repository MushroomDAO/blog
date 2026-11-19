# Architecture

brief2mp4 is not a renderer. It is a loop that an agent runs, plus the scripts and references that make each step of the loop checkable. The renderers are open-source tools it routes to.

<p align="center"><img src="../assets/architecture.png" alt="How brief2mp4 works, from brief to checked MP4" width="100%"></p>

The image is generated from code: edit `docs/diagrams/architecture.html` and run `bash docs/diagrams/render.sh`.

## The loop

```mermaid
stateDiagram-v2
  [*] --> Spec: brief arrives
  Spec --> Build: SPEC.md written
  Build --> Measure: render.mp4 finished
  Measure --> Look: check_delivery.sh
  Look --> Walk: contact_sheet.sh stills viewed
  Walk --> Fix: a done-when line is not met
  Fix --> Build: worst miss first (max 3 rounds)
  Walk --> Deliver: every line met
  Deliver --> [*]: final.mp4 + REPORT.md
  Deliver --> Recheck: user sends "Check it against the brief"
  Recheck --> Walk: re-read the ORIGINAL brief
```

Three design choices make the loop work:

1. **The spec is a contract.** The agent turns every line of the brief into a checkable "done when" line before it writes any code: "at 9.5 s the words FINISH SOMETHING TODAY are fully on screen, nothing cut off". The self-check measures against that list, not against the agent's memory of what it meant to build.
2. **Machines measure, eyes look.** `check_delivery.sh` measures what a script can: duration to the frame, size, frame rate, codecs, loudness, true peak, silence. What it can't measure (spelling on screen, overlap, whether the hero moment is there) is checked by pulling stills at named times and viewing them. The report says which evidence came from where.
3. **Recheck against the brief, not the spec.** The follow-up "Check it against the brief" goes back to the user's words, because a spec can drift from the brief.

## Routing

Each beat in the beat sheet is routed on its own. One film often uses several routes.

```mermaid
flowchart TD
  Beat[A beat from the beat sheet] --> Q1{Mostly words,<br/>UI or 2D shapes?}
  Q1 -->|yes| HF[HyperFrames<br/>HTML + CSS + GSAP]
  Q1 -->|no| Q2{Needs physics, CAD parts,<br/>exploded view, real materials?}
  Q2 -->|yes| D{3D pack<br/>installed?}
  D -->|yes| P[3D pack: model, material,<br/>physics, hf]
  D -->|no| T
  Q2 -->|no| Q3{Must look photoreal?<br/>glass, metal, soft shadow}
  Q3 -->|yes| B[Blender, headless]
  Q3 -->|no| T[Three.js template<br/>inside HyperFrames]
  P --> HF
  T --> HF
  B -->|PNG frames or<br/>ProRes 4444 alpha| HF
  HF --> FF[ffmpeg: finish.sh]
```

HyperFrames is the spine. It is the one place where layers meet on a single timeline, so type always sits in HTML above 3D and stays sharp, exact and spell-checkable.

## Why every frame is a function of time

```mermaid
sequenceDiagram
  participant R as HyperFrames renderer
  participant W1 as Chrome worker 1
  participant W2 as Chrome worker 2
  participant S as Scene (time t to pixels)
  R->>W1: seek t = 4.20 s
  R->>W2: seek t = 0.80 s
  W1->>S: draw(4.20)
  W2->>S: draw(0.80)
  S-->>W1: frame 126
  S-->>W2: frame 24
  W1-->>R: PNG 126
  W2-->>R: PNG 24
  R->>R: encode frames in order
```

The renderer seeks frames out of order across parallel workers. A scene that reads the wall clock, uses unseeded randomness or fetches from the network at render time would draw a different frame for the same `t` in different workers, and the video would flicker or jump. So every visible value is computed from `t` alone. Physics is the hard case: the 3D pack runs the simulation once with Jolt at a fixed step, saves one pose per frame, and the page looks poses up by `t`. The bake is byte-identical across runs, and the tests check that.

## The 3D pack

```mermaid
flowchart LR
  subgraph Assets
    SP[spec.py<br/>Manifold, trimesh or CadQuery] -->|model| G[part GLBs]
    G -->|material| GM[GLBs with PBR presets]
    GM -->|optimize| GO[compressed GLBs]
  end
  subgraph Motion
    SC[scene.json<br/>bodies, gravity, fps] -->|physics: Jolt bake| TR[track.json<br/>one pose per frame]
  end
  GO --> SH[shot.json<br/>models, camera, lights, titles]
  TR --> SH
  SH -->|hf| PR[HyperFrames project<br/>three.js, GSAP, fonts, GLBs vendored]
  PR --> SN[snapshot at 3-5 times]
  SN --> RD[render] --> F[finish.sh]
  GM -->|blender| BL[photoreal frames / MP4]
  BL --> PR
```

Every subcommand prints one JSON object, so an agent reads results instead of parsing logs. The pack is optional and lives in its own folder (`~/.brief2mp4/3d`) with its own Python venv and `node_modules`, so it never touches the user's global Python or npm. `detect_3d.sh` lets the skill branch: with the pack it builds physics and exploded views; without it, it uses the Three.js template and says so in the report.

## Files and responsibilities

| Path | Responsibility |
|---|---|
| `plugin/skills/brief2mp4/SKILL.md` | The loop: spec, route, build, self-check, fix, deliver |
| `references/*.md` | What the agent needs per tool: HyperFrames, Three.js, Blender, ffmpeg, mixed pipelines, the wider ecosystem |
| `scripts/finish.sh` | Any render to a delivery MP4: exact length, H.264 and AAC, -14 LUFS, true peak at or below -1.5 dBTP |
| `scripts/check_delivery.sh` | PASS, WARN or FAIL against the delivery spec |
| `scripts/contact_sheet.sh` | Stills at named times, plus a grid |
| `scripts/doctor.sh`, `detect_3d.sh` | What is installed, and the fix for what is not |
| `templates/` | Starting points that already render: SPEC.md, a Three.js scene, a Blender turntable |
| `3d/` | The optional pack: `b2m3d` CLI, shot runtime, material presets, installers |
| `edit/` | The optional edit pack: verified installers for the ArtCraft editors' CLIs, pinned versions, one tested recipe per app |
| `SETUP.md` | Machine setup an agent follows, per OS |
| `tests/` | Determinism, generation, detection and render tests; CI on macOS, Windows and Ubuntu |

## Extending it

- **A new tool route:** add a reference file in `references/`, a row to the routing table in SKILL.md, and a template that already renders. The tool must pass the determinism test: render the same frame twice in separate runs and get identical PNGs.
- **A new check:** add it to `check_delivery.sh` if a script can measure it, otherwise to the "Look" step as a named question about a still.
- **A new 3D motion:** add a model key to the shot runtime in `3d/templates/shot-runtime.js`, computed from `t` alone, with a test in `tests/`.
