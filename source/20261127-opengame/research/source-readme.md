<p align="center"><img src="docs/readme/opengame-logo.svg" width="400" alt="OpenGame"></p>

<p align="center"><strong>The First Super Game Agent — Open-Source Full-Stack AI Game Studio</strong></p>

<p align="center">
  <img src="docs/readme/opengame-hero.webp" width="100%" alt="OpenGame — The First Super Game Agent. Remix, re-style, test, and publish playable 3D, anime, pixel, and 9:16 mini-games from 25 built-in playable templates across 22 local AI agents.">
</p>

<p align="center">
  <a href="package.json"><img src="docs/readme/badges/node.svg" alt="Node.js 22.18+"></a>
  <a href="LICENSE"><img src="docs/readme/badges/license.svg" alt="Apache 2.0 license"></a>
  <a href="https://github.com/nexu-io/open-design"><img src="docs/readme/badges/built-by-opendesign.svg" alt="Built by OpenDesign"></a>
</p>

<p align="center">
  <a href="https://go.open-design.ai/?utm_source=github&amp;utm_medium=referral&amp;utm_campaign=opengame&amp;utm_content=readme_en"><img src="docs/readme/badges/opendesign-go.svg" alt="OpenDesign Go model subscriptions" /></a>
  <a href="https://discord.com/invite/M7NnHS9gNa"><img src="docs/readme/badges/discord.svg" alt="Join the OpenGame Discord" /></a>
  <a href="https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=b6cs46dc-acb2-48ed-941d-c45642ead841"><img src="docs/readme/badges/feishu.svg" alt="Join the OpenGame Feishu group" /></a>
  <a href="https://x.com/OpenDesignHQ"><img src="docs/readme/badges/x-opendesignhq.svg" alt="OpenDesign on X (@OpenDesignHQ)" /></a>
  <a href="https://x.com/OpenDesignDevs"><img src="docs/readme/badges/x-opendesigndevs.svg" alt="OpenDesign Developers on X (@OpenDesignDevs)" /></a>
  <a href="https://www.youtube.com/channel/UChtshixMhvtgBWzoD9R_Qfg"><img src="docs/readme/badges/youtube.svg" alt="OpenDesign on YouTube" /></a>
</p>

<p align="center"><a href="#quick-start">Quick Start</a> · <a href="#agent-wall">Agents</a> · <a href="#showcase">Playable Templates</a> · <a href="#features">Why OpenGame</a> · <a href="#publish-monetize">Publish &amp; Monetize</a> · <a href="#technical-guide">Setup &amp; MCP</a> · <a href="#community">Community</a></p>

<div align="center">

**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

# Introducing OpenGame

OpenGame is **the first open-source Super Game Agent** — turning **DeepSeek (DSH)**, **Claude Code**, **Codex**, or any of your local coding agents into an AI Unreal Engine / Unity and full-stack game studio. Go from a single idea to **AAA-grade 3D worlds** or **monetization-ready viral mini-games** in one end-to-end pipeline.

- 🚀 **Build AAA-Grade 3D Games with Your Agent.** Drive full-stack 3D gameplay, art, music, and voice straight from **DeepSeek (DSH)**, **Claude**, **Codex**, or **Gemini** — from one prompt to playable 3D action, racing, and open-world games.
- 🎮 **One-Click Remix & Re-style Any Game.** Start from **25 built-in playable templates** (3D, voxel, anime, pixel & 9:16 hits) with full editable source — keep proven mechanics while swapping characters, worlds, and art styles in minutes.
- 💰 **Build Games That Earn: Create → Verify → Monetize.** Automated logic checks, balance simulation, headless playtesting, covers, and gameplay trailers — ship live web links, export single-file **9:16 Playable Ads**, and connect publishing paths for **WeChat Mini Games**, **TikTok**, and **Douyin**.
- 🔓 **Full-Stack Open Source (BYOA + BYOK).** Code, art, video, music, voice, SFX, and Three.js 3D are all open source — plug in your favorite [local agent](#agent-wall) and own API keys, or connect [OpenDesign Go](https://go.open-design.ai/?utm_source=github&utm_medium=referral&utm_campaign=opengame&utm_content=readme_en) (Black Friday lowest-ever discount, with free access to **DeepSeek V4.1 Flash**, **Seedream**, and more).

<a id="quick-start"></a> <a id="快速开始"></a>

## ⚡ Quick Start

### 1. Give one prompt to your local Agent

Paste this instruction into **DeepSeek TUI / Harness**, **Claude Code**, **Codex**, **WorkBuddy**, **Cursor**, **Gemini CLI**, or any of the [22 supported local agents](#agent-wall):

```text
Follow https://github.com/nexu-io/opengame/blob/main/docs/opengame-setup.md to connect OpenGame to this agent. For a new install, use a shallow clone (--depth 1) and skip LFS downloads. Open the Game Studio template gallery so I can choose a game. Fetch that game's assets when I play or remix it.
If you find a reproducible OpenGame bug, you're welcome to open a PR against nexu-io/opengame with the fix, steps to reproduce, and how you verified it.
```

### 2. Install the Main OpenGame Skill with Skills CLI

Install the main `opengame` entry Skill (which guides local setup and routes into `openmotion-game` + 18 game craft, 3C, animation, playable-ad, and QA reference handbooks) with the [Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add https://github.com/nexu-io/opengame/tree/skills --skill opengame
```

> Installing the Skill copies the OpenGame entry instructions into your agent (you can also install `--skill openmotion-game` directly). Complete the local Studio & MCP setup below so your agent can call the 12 `openmotion_game_*` tools and open Game Studio.

### 3. Run OpenGame Studio locally from source

Requires **Git**, **Git LFS**, **npm**, and **Node.js 22.18+** (CI pins Node.js 26.11.1). Browse the catalog immediately after startup. Playing or remixing a template downloads its assets on first use. Tidebreaker works offline.

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --single-branch --branch main https://github.com/nexu-io/opengame.git
cd opengame
git lfs install --local --skip-smudge
npm ci
npm run build:studio
npm start
```

<a id="agent-wall"></a>

**Works with 22 local agents (BYOA)** · [Choose your agent](#choose-agent)

<p align="center"><a href="#choose-agent"><picture><source media="(max-width: 600px)" srcset="docs/readme/agents/local-agents.mobile.png"><img src="docs/readme/agents/local-agents.png" width="100%" alt="WorkBuddy, Codex CLI, Claude Code, OpenCode, Hermes, Antigravity, Gemini CLI, Grok Build, Kimi CLI, Cursor Agent, Qwen Code, Qoder CLI, GitHub Copilot, Pi, Kiro CLI, Kilo, Mistral Vibe, DeepSeek TUI, Reasonix, Aider, Devin, Trae CLI"></picture></a></p>

<a id="showcase"></a>

## 🕹️ Playable Game Templates & Showcase

OpenGame ships with **25 ready-to-play games** right inside [`templates/games/`](templates/games/) — complete with playable HTML5 / Three.js source, artwork, controls, and localization. Play them locally in Game Studio, **Remix** any title with one click, or **Re-style** it into your own IP, theme, or brand.

### 3D, Voxel & Action Games (16:9)

<table width="100%">
<tr>
<td width="50%" valign="top">
<img src="templates/games/tidebreaker/cover.webp" width="100%" alt="Tidebreaker — 3D storm archipelago speedboat racing"><br>
<strong>Tidebreaker</strong> · <code>3D · Racing · Three.js</code><br>
Race a speedboat through a storm-lashed archipelago, jump wave crests, dodge reefs, and beat the tide across eight checkpoints.<br>
<a href="templates/games/tidebreaker/">Inspect source &amp; DESIGN.md →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/starlight-bastion/cover.webp" width="100%" alt="Starlight Bastion — Voxel space crystal wave shooter"><br>
<strong>Starlight Bastion</strong> · <code>Voxel · Shooter · Upgrades</code><br>
Defend a luminous crystal against five escalating waves of voxel invaders, choosing roguelite upgrades between waves.<br>
<a href="templates/games/starlight-bastion/">Inspect source &amp; DESIGN.md →</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<img src="templates/games/skyline-courier/cover.webp" width="100%" alt="Skyline Courier — 3D cyberpunk rooftop parkour platformer"><br>
<strong>Skyline Courier</strong> · <code>3D · Platformer · Cyberpunk</code><br>
Run, leap, and wall-kick across rain-soaked cyberpunk skyscrapers to deliver three final parcels in 90 seconds.<br>
<a href="templates/games/skyline-courier/">Inspect source &amp; DESIGN.md →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/neon-drift/cover.webp" width="100%" alt="Neon Drift — 3D synthwave night highway racer"><br>
<strong>Neon Drift</strong> · <code>3D · Racing · Cyberpunk</code><br>
Weave through rain-slick neon highway traffic, chain near-misses to recharge boost, and chase a new distance record.<br>
<a href="templates/games/neon-drift/">Inspect source →</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<img src="templates/games/comet-guard/cover.webp" width="100%" alt="Comet Guard — Orbital defense space shooter"><br>
<strong>Comet Guard</strong> · <code>Shooter · Space</code><br>
Pilot an orbital interceptor in a painted starfield, shatter molten comets, and defend the station through escalating waves.<br>
<a href="templates/games/comet-guard/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/harbor-skirmish/cover.webp" width="100%" alt="Harbor Skirmish — 3D first-person island shooter"><br>
<strong>Harbor Skirmish</strong> · <code>3D FPS · Grapple &amp; Slide</code><br>
A stylized 3D first-person shooter on a curved island with double-jump, slide, dash, and grappling-hook mobility.<br>
<a href="templates/games/harbor-skirmish/">Inspect source →</a>
</td>
</tr>
</table>

### Stylized, Narrative & Atmospheric Games (16:9)

<table width="100%">
<tr>
<td width="50%" valign="top">
<img src="templates/games/glyph-garden/cover.webp" width="100%" alt="Glyph Garden — Anime fantasy match-3 puzzle"><br>
<strong>Glyph Garden</strong> · <code>Anime · Puzzle · Fantasy</code><br>
Trade moonlit petals and trigger cascading combo blooms to reach 2,200 points in 24 moves.<br>
<a href="templates/games/glyph-garden/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/lantern-hop/cover.webp" width="100%" alt="Lantern Hop — Pixel fantasy rooftop platformer"><br>
<strong>Lantern Hop</strong> · <code>Pixel · Platformer · Fantasy</code><br>
Guide a scarf-wearing pixel fox across layered moonlit rooftops, double-jumping gaps and collecting glowing paper lanterns.<br>
<a href="templates/games/lantern-hop/">Inspect source →</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<img src="templates/games/lighthouse-log/cover.webp" width="100%" alt="Lighthouse Log — Anime stormy-night narrative survival"><br>
<strong>Lighthouse Log</strong> · <code>Anime · Visual novel · Survival</code><br>
Keep a coastal lighthouse burning through seven stormy nights, rationing fuel and making impossible radio choices.<br>
<a href="templates/games/lighthouse-log/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/last-light/cover.webp" width="100%" alt="Last Light — Torch-beam horror escape"><br>
<strong>Last Light</strong> · <code>Horror · Atmospheric</code><br>
Search an abandoned school for three keys before your torch dies while keeping the pursuing shade pinned in your beam.<br>
<a href="templates/games/last-light/">Inspect source →</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<img src="templates/games/night-train/cover.webp" width="100%" alt="Night Train Letters — Interactive branching story"><br>
<strong>Night Train Letters</strong> · <code>Visual novel · Branching Narrative</code><br>
Three unsent letters on a rain-soaked night train to the sea — an intimate branching narrative built in pure HTML.<br>
<a href="templates/games/night-train/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/stack-the-moon/cover.webp" width="100%" alt="Stack the Moon — One-tap moonlit tower stacker"><br>
<strong>Stack the Moon</strong> · <code>Casual · One-Tap Arcade</code><br>
Build a moonlit observatory above the clouds one timed stone at a time; chain perfect landings to widen your tower.<br>
<a href="templates/games/stack-the-moon/">Inspect source →</a>
</td>
</tr>
</table>

### Viral Portrait Mini-Games & Playable Ads (9:16)

Built for mobile thumbs, instant first-frame engagement, short high-retention loops, and **mini-game / playable-ad monetization**:

<table width="100%">
<tr>
<td width="50%" valign="top">
<img src="templates/games/gate-legion/cover.webp" width="100%" alt="Gate Legion — 9:16 arithmetic gate army runner"><br>
<strong>Gate Legion</strong> · <code>9:16 · Gate Runner</code><br>
Lead your squad through <code>+10</code> / <code>×2</code> arithmetic gates and clash with the final boss army.<br>
<a href="templates/games/gate-legion/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/pin-rescue/cover.webp" width="100%" alt="Pin Rescue — 9:16 pull-the-pin puzzle"><br>
<strong>Pin Rescue</strong> · <code>9:16 · Pull-the-Pin Puzzle</code><br>
Pull pins to mix water and lava into stone, clear hazards, and deliver gold across five stages.<br>
<a href="templates/games/pin-rescue/">Inspect source →</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<img src="templates/games/sky-runner/cover.webp" width="100%" alt="Sky Runner — 9:16 3D neon hoverboard runner"><br>
<strong>Sky Runner</strong> · <code>9:16 · 3D Lane Runner</code><br>
Swipe lanes, collect coins, dodge drones, and boost through an accelerating neon skyway.<br>
<a href="templates/games/sky-runner/">Inspect source →</a>
</td>
<td width="50%" valign="top">
<img src="templates/games/slime-swell/cover.webp" width="100%" alt="Slime Swell — 9:16 city-eating arcade arena"><br>
<strong>Slime Swell</strong> · <code>9:16 · Grow &amp; Devour .io</code><br>
Swallow street objects, grow bigger than buildings, and outrank three rival slimes in 60 seconds.<br>
<a href="templates/games/slime-swell/">Inspect source →</a>
</td>
</tr>
</table>

<details>
<summary><strong>Browse all 25 built-in playable game templates</strong></summary>

| Game | Genre | Style | Format | Summary | Source |
| --- | --- | --- | --- | --- | --- |
| **Castle Crush** | Casual | Anime | 9:16 Portrait | Slingshot physics siege across four timber-and-stone stages | [castle-crush](templates/games/castle-crush/) |
| **Comet Guard** | Shooter | Minimal | 16:9 Landscape | Orbital interceptor defending a starfield station from molten comets | [comet-guard](templates/games/comet-guard/) |
| **Drift Dash** | Racing | Voxel | 9:16 Portrait | One-thumb retro circuit drifting against three AI rivals | [drift-dash](templates/games/drift-dash/) |
| **Gate Legion** | Casual | Pixel | 9:16 Portrait | Viral arithmetic-gate squad multiplier & boss clash | [gate-legion](templates/games/gate-legion/) |
| **Glyph Garden** | Casual | Anime | 16:9 Landscape | Cascading fantasy match-3 bloom puzzle | [glyph-garden](templates/games/glyph-garden/) |
| **Harbor Skirmish** | Shooter | 3D | 16:9 Landscape | Stylized 3D FPS with double-jump, slide, dash, and grapple | [harbor-skirmish](templates/games/harbor-skirmish/) |
| **Jingyang Ridge** | Casual | Anime | 16:9 Landscape | Ink-wash martial arts boss duel — read tells, dodge lanes, punish | [jingyang-ridge](templates/games/jingyang-ridge/) |
| **Lane Turret** | Shooter | Pixel | 9:16 Portrait | Auto-turret wave defense with upgrade cards | [lane-turret](templates/games/lane-turret/) |
| **Lantern Hop** | Platformer | Pixel | 16:9 Landscape | Moonlit rooftop fox endless double-jump runner | [lantern-hop](templates/games/lantern-hop/) |
| **Last Light** | Horror | Minimal | 16:9 Landscape | Flashlight survival escape through an abandoned school | [last-light](templates/games/last-light/) |
| **Lighthouse Log** | Visual novel | Anime | 16:9 Landscape | Seven stormy nights of fuel rationing & branching radio choices | [lighthouse-log](templates/games/lighthouse-log/) |
| **Merge Bakery** | Casual | Anime | 9:16 Portrait | Bake, merge pastries, and clear timed customer orders | [merge-bakery](templates/games/merge-bakery/) |
| **Neon Drift** | Racing | 3D | 16:9 Landscape | Rain-slick synthwave highway traffic weaving & boost | [neon-drift](templates/games/neon-drift/) |
| **Night Train Letters** | Visual novel | Minimal | 16:9 Landscape | Intimate branching story of three unsent letters on a night train | [night-train](templates/games/night-train/) |
| **Periscope Depth** | Shooter | Minimal | 16:9 Landscape | Submarine patrol: torpedo carriers on periscope, dodge sonar depth charges | [periscope-depth](templates/games/periscope-depth/) |
| **Pin Rescue** | Casual | Minimal | 9:16 Portrait | Pull-the-pin lava, water, and gold physics puzzles | [pin-rescue](templates/games/pin-rescue/) |
| **Rooftop Roast** | Casual | Minimal | 16:9 Landscape | Brandable café promo drone game — edit one `SHOP` object to rebrand | [rooftop-roast](templates/games/rooftop-roast/) |
| **Sky Runner** | Racing | 3D | 9:16 Portrait | Cyberpunk 3D hoverboard lane runner with coins & boost | [sky-runner](templates/games/sky-runner/) |
| **Skyline Courier** | Platformer | 3D | 16:9 Landscape | 3D rooftop parkour & wall-kicks against a 90-second timer | [skyline-courier](templates/games/skyline-courier/) |
| **Slime Swell** | Casual | Minimal | 9:16 Portrait | City-devouring growth arena against three rival slimes | [slime-swell](templates/games/slime-swell/) |
| **Sort Stack** | Casual | Minimal | 9:16 Portrait | Five-stage ring-sorting logic puzzle with undo | [sort-stack](templates/games/sort-stack/) |
| **Stack the Moon** | Casual | Minimal | 16:9 Landscape | One-tap moonlit observatory tower stacker | [stack-the-moon](templates/games/stack-the-moon/) |
| **Starlight Bastion** | Shooter | Voxel | 16:9 Landscape | Five-wave crystal defense with roguelite upgrades | [starlight-bastion](templates/games/starlight-bastion/) |
| **Tidebreaker** | Racing | 3D | 16:9 Landscape | Storm archipelago 3D speedboat racing & wave jumps | [tidebreaker](templates/games/tidebreaker/) |
| **Tilt Temple** | Casual | 3D | 9:16 Portrait | 3D floating labyrinth — tilt, collect the key, reach the portal | [tilt-temple](templates/games/tilt-temple/) |

</details>

<a id="features"></a>

## ✨ Why OpenGame

### 1. One-Click Remix & Re-style — Powered by Game-as-Code

Building a polished game from a blank prompt is hard for any model. OpenGame solves this by separating **verified game engineering** from **theme, art direction, and content**:

- **Every game is clean, inspectable source**: `index.html`, deterministic `logic.js`, vendored Three.js for 3D titles, plus structured design docs (`design/plan.md`, `design/style.md`, `design/assets.csv`, `design/verification.md`).
- **Remix in one click**: Click **Remix** on any of the 25 templates in Game Studio (or ask your agent to remix it) to fork an owned, editable draft with full controls, tuning knobs, and automated test hooks already wired up.
- **Re-style into any universe**: Swap genre dressing, characters, palette, sprites, textures, and music without breaking physics or win/loss rules — ideal for fast iteration with affordable models like **DeepSeek**, or pushing AAA-grade 3D & shader ambition with **Claude Fable 5.2**, **Opus**, **Codex**, and **Gemini**.

**Try these prompts in your connected Agent:**

```text
# 1. One-click Remix & Re-style (great for DeepSeek / fast models)
Use openmotion-game to remix the "Lantern Hop" template into a cyberpunk rain-city cat runner. Keep the double-jump physics and endless scoring loop, replace the fox and lanterns with a neon cyber-cat and holo-batteries, generate new key art and synthwave BGM, then validate, playtest, and capture a fresh cover.
```

```text
# 2. Build a 9:16 Playable Ad ready for mobile campaigns
Use openmotion-game to create a portrait 9:16 playable ad (playableAd: true) for a medieval tower-defense mobile game: instant first-frame interaction with a hand tutorial, a 25-second escalating wave battle, and an end card with an App Store / Google Play CTA. Validate, simulate, playtest at 390x844, and bundle as a single-file HTML.
```

```text
# 3. Original 3D Game from Scratch (great for Claude Fable 5.2 / Opus / Codex / Gemini)
Use openmotion-game to create a 3D wuxia boss-duel game (style: "3d") set on a misty bamboo cliff at dusk. Include parry timing, dodge i-frames, stamina management, and two boss phases. Run 3-tier simulation, headless Chromium playtest, capture a 1280x720 cover, and record a gameplay trailer.
```

<a id="model-wall"></a>

### 2. Full-Stack Multimodal Game Creation (BYOK)

A real game needs more than code — it needs key art, character sprites, seamless 3D textures, music loops, voice lines, and crisp sound effects. OpenGame's **Model Gateway** wires multimodal generation directly into the game project while keeping your API keys local and separate from game source.

<p>
  <img src="docs/readme/opengame/models/gpt-image.svg" width="148" alt="GPT Image">
  <img src="docs/readme/opengame/models/seedream.svg" width="148" alt="Seedream">
  <img src="docs/readme/models/nano-banana.svg" width="148" alt="Nano Banana 2">
  <img src="docs/readme/models/flux.svg" width="148" alt="FLUX">
  <img src="docs/readme/models/codex.svg" width="148" alt="Codex Image"><br>
  <img src="docs/readme/models/seedance.svg" width="148" alt="Seedance">
  <img src="docs/readme/models/wan.svg" width="148" alt="Wan">
  <img src="docs/readme/models/suno.svg" width="148" alt="Suno">
  <img src="docs/readme/models/elevenlabs.svg" width="148" alt="ElevenLabs">
  <img src="docs/readme/opengame/models/byteplus.svg" width="148" alt="BytePlus Voice">
</p>

| Game Asset Layer | Recommended Models (when configured in Model Gateway) | Zero-Key / Built-in Fallback |
| --- | --- | --- |
| **🖼️ Key art, portraits, sprites & textures** | `GPT Image 2.6` (edits & transparent PNGs), `Seedream 5.5` / `5.0 Flash`, `Nano Banana 2`, `FLUX`, `Codex Image` | Crisp procedural Canvas/SVG sprites & procedural textures |
| **🎵 Background music (menu, stage, boss)** | `ElevenLabs Music v2` (`no vocals` loops), `Suno v4` | Procedural Web Audio synthesized soundtrack |
| **🎙️ Character voice & announcer lines** | `ElevenLabs v3` (English & multilingual), `BytePlus TTS 2` (Chinese), `Kokoro` | Styled dialogue captions & subtitle UI |
| **🎬 Intro cutscenes & motion clips** | `Wan 2.7`, `Seedance 2.5` (short I2V clips) | In-engine animated intro camera & title sequence |
| **🔊 Impact SFX (hits, jumps, coins, UI)** | Synthesized directly in game code via the Web Audio API | Same (zero latency, zero external files) |
| **🧊 3D scenes & models** | Vendored **Three.js** + bundled CC0 kits + reserved 3D gateway slot (auto-discovered when connected) | Procedural Three.js geometry, lighting & shaders |

> OpenGame charges no software subscription for the local open-source stack. Use your own provider keys in **Model Settings**, connect [OpenDesign Go](https://go.open-design.ai/?utm_source=github&utm_medium=referral&utm_campaign=opengame&utm_content=readme_en) for unified multi-model access, or build 100% code-generated zero-API-cost games. [Model catalog](gateway/catalog.ts) · [Provider setup](docs/model-gateway.md)

### 3. Automated Game QA, Balance Simulation & Auto-Trailers

Agents shouldn't just output code and hope it runs. OpenGame enforces an automated engineering verification loop before marking any game **ready**:

1. **Static & 50-Tick Logic Validation (`openmotion_game_validate`)** — Verifies `index.html`, allowed asset/CDN policies, required deterministic exports, and runs a 50-tick smoke test (`< 5 ms` per tick).
2. **3-Tier Deterministic Balance Simulation (`openmotion_game_simulate`)** — Executes bounded headless routes without a browser to verify that a skilled `reference` route reaches a real win milestone, a degraded weak route struggles, and an `idle` player loses cleanly (`< 2500` ticks).
3. **Headless Chromium Playtesting (`openmotion_game_playtest`)** — Drives real keyboard/mouse/touch controls across 1–4 clients, checking 3C responsiveness, `390×844` mobile layout integrity, media URL loads, and zero console/network errors.
4. **Game-Only Cover Capture (`openmotion_game_capture_cover`)** — Captures a clean `1280×720` PNG directly from the game canvas in isolated headless Chrome.
5. **Automated Gameplay Trailer (`openmotion_game_trailer`)** — Records three real 5-second headless gameplay clips at `1280×720`, composes an editable ~19-second title + highlights + Play Now trailer, and renders an MP4 ready for social launch.

<a id="publish-monetize"></a>

## 🚀 End-to-End Distribution & Monetization

Turn playable prototypes into real games people can play, share, and pay for.

| Stage | Available Today | Roadmap (In Progress) |
| --- | --- | --- |
| **Play & Local Catalog** | Publish straight to your local OpenGame Studio market (`openmotion_game_publish`) with play tracking, favorites, and 1-click Remix | **Top 100 Profitable Mini-Game Templates** curated by genre & revenue mechanics for instant remixing |
| **Instant Web Share** | One-click static bundle & live web share link via OpenDesign Cloud (`openmotion_assets_use action="web_publish"`), rewriting local media URLs and compressing assets automatically | Custom domain & embeddable game widget cards |
| **Mobile Playable Ads** | Built-in **9:16 Playable Ad mode** (`playableAd: true`): first-frame instant play, hand tutorial, rich short-level progression, looping BGM, and App Store / Google Play end-card CTA | Direct ad-network packaging presets (AppLovin, Unity Ads, Meta, TikTok) |
| **Mini-Game Platforms & Monetization** | Clean self-contained HTML5/JS project exports ready for manual platform wrapping, plus auto-recorded gameplay trailers for launch marketing | **L1–L4 Guided Platform Publishing** (packaging scripts, checklists & Skills) for **WeChat Mini Games (微信小游戏)**, **Douyin Mini Games (抖音小游戏)**, **TikTok**, **Xiaohongshu Mini-Tools**, and **itch.io / Poki / CrazyGames** |
| **AI Game Playground** | Local single-player & existing room-based playtesting | **Multi-Model Live Game Arena** — pit multiple frontier LLMs against each other inside live games in real time |

<a id="technical-guide"></a>

## 🛠️ Setup & MCP Tools

<a id="agent-setup"></a> <a id="choose-agent"></a>

### Connect Your Local Agent

Choose your agent to connect the local OpenGame MCP server and Skills:

<p>
  <a href="#deepseek-setup"><img src="docs/readme/agents/deepseek-badge.svg" width="144" height="34" alt="DeepSeek TUI / Harness" /></a>
  <a href="#claude-setup"><img src="docs/readme/agents/claude-code-badge.svg" width="144" height="34" alt="Claude Code" /></a>
  <a href="#codex-setup"><img src="docs/readme/agents/codex-badge.svg" width="144" height="34" alt="Codex CLI" /></a>
  <a href="#workbuddy-setup"><img src="docs/readme/agents/workbuddy-badge.svg" width="144" height="34" alt="WorkBuddy" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/opencode-badge.svg" width="144" height="34" alt="OpenCode" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/hermes-badge.svg" width="144" height="34" alt="Hermes" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/antigravity-badge.svg" width="144" height="34" alt="Antigravity" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/gemini-badge.svg" width="144" height="34" alt="Gemini CLI" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/grok-build-badge.svg" width="144" height="34" alt="Grok Build" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/kimi-badge.svg" width="144" height="34" alt="Kimi CLI" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/cursor-badge.svg" width="144" height="34" alt="Cursor Agent" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/qwen-badge.svg" width="144" height="34" alt="Qwen Code" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/qoder-badge.svg" width="144" height="34" alt="Qoder CLI" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/copilot-badge.svg" width="144" height="34" alt="GitHub Copilot" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/pi-badge.svg" width="144" height="34" alt="Pi" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/kiro-badge.svg" width="144" height="34" alt="Kiro CLI" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/kilo-badge.svg" width="144" height="34" alt="Kilo" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/vibe-badge.svg" width="144" height="34" alt="Mistral Vibe" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/reasonix-badge.svg" width="144" height="34" alt="Reasonix" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/aider-badge.svg" width="144" height="34" alt="Aider" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/devin-badge.svg" width="144" height="34" alt="Devin" /></a>
  <a href="#manual-mcp"><img src="docs/readme/agents/trae-badge.svg" width="144" height="34" alt="Trae CLI" /></a>
</p>

- <a id="deepseek-setup"></a>**DeepSeek TUI / Harness** · Install the `openmotion-game` skill and connect the local MCP tools via Cordis configuration, or run `node integrations/dsh/install.ts` from the checkout. [DeepSeek Harness guide](docs/agent-adapters.md#deepseek-harness)
- <a id="claude-setup"></a>**Claude Code** · Add the stdio MCP entry below, install the `openmotion-game` skill, and run `/mcp` to verify the tools are active.
- <a id="codex-setup"></a>**Codex CLI** · Run `bash scripts/install-motion.command` from the checkout to register the local plugin and MCP server automatically.
- <a id="workbuddy-setup"></a>**WorkBuddy** · Import the connector or paste the `mcp.json` configuration below. [WorkBuddy guide](docs/agent-adapters.md#workbuddy)

<a id="manual-mcp"></a>

#### Manual stdio MCP configuration (works in any MCP client)

```json
{
  "mcpServers": {
    "openmotion": {
      "command": "/absolute/path/to/node",
      "args": ["--experimental-strip-types", "/absolute/path/to/opengame/mcp.ts"],
      "env": {
        "MOTION_DATA_DIR": "/absolute/path/to/opengame-data"
      }
    }
  }
}
```

> Keep `MOTION_DATA_DIR` outside the git checkout so your games, generated assets, and provider keys stay cleanly separated from repository updates. See the [full setup guide](docs/opengame-setup.md) and [architecture reference](docs/opengame-architecture.md).

### 12 Dedicated Game MCP Tools

OpenGame exposes a complete game-engineering tool surface over local stdio MCP (using the shared `openmotion_game_*` namespace so existing hosts and adapters stay 100% compatible):

| MCP Tool | Purpose |
| --- | --- |
| `openmotion_game_create` | Create a new game draft (2D, 3D with vendored Three.js, or 9:16 `playableAd`) and return the complete agent brief |
| `openmotion_game_get` | Read a game card, lifecycle status, and full file inventory |
| `openmotion_game_read_file` | Read any source or design file inside a game project |
| `openmotion_game_write_files` | Batch-write cohesive game source and design files (up to 100 text files / 8 MiB per owned game) |
| `openmotion_game_update_meta` | Merge title, description, controls, cover path, and localized metadata (`zh-CN`, etc.) |
| `openmotion_game_validate` | Check `index.html`, CDN policy, deterministic logic exports, and run a 50-tick smoke test |
| `openmotion_game_simulate` | Run bounded 3-tier deterministic headless simulations (`reference` win / weak / `idle` loss) |
| `openmotion_game_playtest` | Launch isolated headless Chrome (1–4 clients) to test real input controls, `390×844` layout, and console cleanliness |
| `openmotion_game_capture_cover` | Capture a clean `1280×720` PNG directly from the game canvas into `assets/cover.png` |
| `openmotion_game_trailer` | Record real headless gameplay clips and render an editable ~19-second MP4 trailer |
| `openmotion_game_set_status` | Transition lifecycle status (`building`, `ready`, `failed`) |
| `openmotion_game_publish` | Revalidate and publish the game into the local Game Studio catalog |

Plus **`openmotion_media_use`** (discover & inspect configured BYOK multimodal models) and **`openmotion_assets_use`** (generate images/music/voice/video and run `action: "web_publish"` for one-click cloud share links). [Full MCP contract](docs/mcp-phase1-tools.md)

### Game Engineering Skill & 18 Reference Handbooks

Every connected agent can read [`skills/openmotion-game/SKILL.md`](skills/openmotion-game/SKILL.md) (or `openmotion://workflow/game/start` via MCP resources) along with 18 specialized engineering handbooks:

| Domain | Reference Guides |
| --- | --- |
| **Game Design & Structure** | [Brief Standard](skills/openmotion-game/references/game-brief.md) · [Genres & Core Loops](skills/openmotion-game/references/game-genres.md) · [Design System](skills/openmotion-game/references/game-design-system.md) · [Reference Lookup](skills/openmotion-game/references/game-lookup.md) |
| **3C, Controls & Game Feel** | [3C Modules](skills/openmotion-game/references/game-3c-modules.md) · [Game Feel & Craft](skills/openmotion-game/references/game-feel-craft.md) · [Production Flow](skills/openmotion-game/references/game-flow.md) |
| **Visuals, 2D/3D & Audio** | [Stylization](skills/openmotion-game/references/game-stylization.md) · [Textures](skills/openmotion-game/references/game-textures.md) · [2D Animation](skills/openmotion-game/references/game-2d-animation.md) · [3D Animation](skills/openmotion-game/references/game-3d-animation.md) · [Procedural Motion](skills/openmotion-game/references/game-procedural-animation.md) · [Audio & Web Audio](skills/openmotion-game/references/game-audio.md) |
| **Playable Ads & Quality Gates** | [Playable Ad Spec](skills/openmotion-game/references/game-playable-ad.md) · [Quality Gates](skills/openmotion-game/references/game-gates.md) · [Review Rubric](skills/openmotion-game/references/review-rubric.md) |

### Tech Stack & Source Map

| Layer | Technology | Entry Points |
| --- | --- | --- |
| **OpenGame Studio UI** | React 19, TypeScript 5.9, Vite 6, Tailwind CSS 4, Zustand | [GameStudio.tsx](studio/src/motion/game/GameStudio.tsx) · [gameCatalog.ts](studio/src/motion/game/gameCatalog.ts) |
| **Game Runtime & QA** | Node.js, native HTTP, Puppeteer Core / Chrome, deterministic simulator | [game-projects.ts](game-projects.ts) · [shared/game-contract.ts](shared/game-contract.ts) · [server.ts](server.ts) |
| **MCP & Agent Skills** | Local stdio MCP server, `opengame` entry Skill, `openmotion-game` workflow & 18 handbooks | [mcp.ts](mcp.ts) · [skills/opengame/SKILL.md](skills/opengame/SKILL.md) · [skills/openmotion-game/](skills/openmotion-game/) |
| **Multimodal Gateway** | BYOK model discovery, job polling, asset library & web publish | [gateway/service.ts](gateway/service.ts) · [gateway/catalog.ts](gateway/catalog.ts) · [docs/assets.md](docs/assets.md) |
| **Playable Templates** | 25 standalone HTML5 / Canvas / Three.js games with covers & metadata | [templates/games/](templates/games/) |
| **Trailer Pipeline** | Headless gameplay capture + HTML composition + FFmpeg MP4 export | [docs/usage.md](docs/usage.md) · [scripts/verify-export.ts](scripts/verify-export.ts) |

<a id="community"></a>

## 🤝 Build Games Together

Share a playable game template, a remixable mini-game genre kit, an art-style guide, a platform publishing script (WeChat / Douyin / TikTok / itch.io), or a Game Studio improvement.

| Contribution | What to include |
| --- | --- |
| **A playable game template** | Self-contained folder under `templates/games/<id>/` with `index.html`, `game.json`, `cover.webp`, and optional `DESIGN.md` |
| **A genre or playable-ad recipe** | Clear 3C rules, balance invariants, and reference verification notes |
| **Platform publishing adapters** | Packaging scripts, manifest generators, or submission checklists for mini-game & web portals |
| **Agent & model integrations** | Host setup adapters or BYOK multimodal provider support |

[Contribute](CONTRIBUTING.md) · [Repository Guidelines](AGENTS.md) · [Report an Issue](https://github.com/nexu-io/opengame/issues)

<a id="acknowledgements"></a>

## 🙏 Acknowledgements & Open-Source Attribution

OpenGame is built on and inspired by the open-source game, creative tooling, and AI agent community.

### Core Foundations & Major Inspirations

| Project | License | How OpenGame Builds On / References It |
| --- | --- | --- |
| **[Higgsfield AI Skills](https://github.com/higgsfield-ai/skills)** | MIT | Source of several ported and adapted game craft handbooks under [skills/openmotion-game/](skills/openmotion-game/) ([PROVENANCE.md](skills/openmotion-game/PROVENANCE.md) · [LICENSE-HIGGSFIELD](skills/openmotion-game/LICENSE-HIGGSFIELD)) |
| **[HeyGen Hyperframes](https://github.com/heygen-com/hyperframes)** | Apache-2.0 | Upstream Studio editor foundation ([studio/LICENSE](studio/LICENSE)) and automated gameplay trailer composition & MP4 rendering engine |
| **[DSH Game Studio](https://github.com/ZSeven-W/dsh-game-studio)** & **[dsh-games](https://github.com/finiking/dsh-games)** (by [@FiniYang](https://x.com/FiniYang)) | Open Source | Early open-source inspiration and reference for DeepSeek Harness (DSH) AI-native game creation workflows, automated playtesting, and playable game walls |
| **[OpenDesign](https://github.com/nexu-io/open-design)** & **[OpenMotion](https://github.com/nexu-io/openmotion)** | Apache-2.0 | Shared open-source design system, multimodal Model Gateway, workspace architecture, and MCP tool contracts |
| **[Three.js](https://github.com/mrdoob/three.js)** | MIT | Vendored offline 3D rendering engine and model/skeleton loaders powering 3D templates and agent-built 3D games ([LICENSE-three.txt](templates/game-kits/vendor/LICENSE-three.txt)) |
| **[KayKit Adventurers Character Pack](https://www.kaylousberg.com/)** (by Kay Lousberg) | CC0 | Bundled offline rigged 3D characters (Mage & Knight) under [templates/game-kits/characters/](templates/game-kits/characters/) ([LICENSE-KayKit.txt](templates/game-kits/characters/LICENSE-KayKit.txt)) |
| **[Cocos Creator / Cocos Engine](https://github.com/cocos/cocos-engine)** | MIT | Open-source game engine runtime powering offline-playable mini-game templates |
| **[Model Context Protocol (MCP) SDK](https://github.com/modelcontextprotocol/typescript-sdk)** & **[Vercel Skills CLI](https://github.com/vercel-labs/skills)** | MIT / Apache-2.0 | Standard protocol for connecting 22 local AI agents and lightweight Skill distribution |

We also thank the broader open-source ecosystem powering our stack: **Puppeteer & Chrome for Testing**, **FFmpeg**, **Dockview**, **CodeMirror 6**, **Lexical**, **React**, **Vite**, **Tailwind CSS**, **Zustand**, **Electron**, **GSAP**, **DiceBear** (Micah avatar style, CC BY 4.0, [attribution](studio/skill-cover-attribution.md)), and open-source fonts (**Albert Sans**, **IBM Plex Mono**, **Instrument Serif**, SIL OFL 1.1).

### Community Game Showcase Credits

Special thanks to the creators whose publicly shared AI browser games are featured as inspiration links in Game Studio (click any tile to visit the creator's original post):

<p>
  <a href="https://x.com/felixrieseberg/status/2119925633564463609" title="Saltline by @felixrieseberg"><img src="studio/src/motion/game/community/saltline.jpg" width="56" height="56" alt="Saltline (@felixrieseberg)" /></a>
  <a href="https://x.com/Saccc_c/status/2109962425512734739" title="The Little Prince: Star Journey by @Saccc_c"><img src="studio/src/motion/game/community/little-prince.jpg" width="56" height="56" alt="The Little Prince: Star Journey (@Saccc_c)" /></a>
  <a href="https://x.com/Rubzem/status/2104253584737230926" title="Sky Reach by @jonesiller"><img src="studio/src/motion/game/community/sky-reach.jpg" width="56" height="56" alt="Sky Reach (@jonesiller)" /></a>
  <a href="https://x.com/edwinarbus/status/2102463453176979794" title="Antikythera Dive by @edwinarbus"><img src="studio/src/motion/game/community/shipwreck.jpg" width="56" height="56" alt="Antikythera Dive (@edwinarbus)" /></a>
  <a href="https://x.com/bridgemindai/status/2102451997395866021" title="Turbo Kart Rally by @bridgemindai"><img src="studio/src/motion/game/community/turbo-kart.jpg" width="56" height="56" alt="Turbo Kart Rally (@bridgemindai)" /></a>
  <a href="https://x.com/BubuStd/status/2102991290568954264" title="Voxel Musou by @BubuStd"><img src="studio/src/motion/game/community/voxel-musou.jpg" width="56" height="56" alt="Voxel Musou (@BubuStd)" /></a>
  <a href="https://x.com/ebbyamir/status/2120284261089673376" title="Starry Nightrider by @ebbyamir"><img src="studio/src/motion/game/community/starry-nightrider.jpg" width="56" height="56" alt="Starry Nightrider (@ebbyamir)" /></a>
  <a href="https://x.com/ViktorKav/status/2122647483281015155" title="Uno com Escada by @ViktorKav"><img src="studio/src/motion/game/community/uno-com-escada.jpg" width="56" height="56" alt="Uno com Escada (@ViktorKav)" /></a>
  <a href="https://x.com/kevin_t_ngo/status/2119868968307695818" title="What the Water Keeps by @kevin_t_ngo"><img src="studio/src/motion/game/community/what-the-water-keeps.jpg" width="56" height="56" alt="What the Water Keeps (@kevin_t_ngo)" /></a>
  <a href="https://x.com/kevin_t_ngo/status/2120238844754923874" title="Evensong by @kevin_t_ngo"><img src="studio/src/motion/game/community/evensong.jpg" width="56" height="56" alt="Evensong (@kevin_t_ngo)" /></a>
  <a href="https://x.com/mattshumer_/status/2119877065701036047" title="Mirror Earth by @mattshumer_"><img src="studio/src/motion/game/community/mirror-earth.jpg" width="56" height="56" alt="Mirror Earth (@mattshumer_)" /></a>
  <a href="https://x.com/photonstorm/status/2120330010112434313" title="Tennis (Go Wild) by @photonstorm"><img src="studio/src/motion/game/community/tennis-go-wild.jpg" width="56" height="56" alt="Tennis (Go Wild) (@photonstorm)" /></a>
  <a href="https://x.com/op7418/status/2120694045299327187" title="Mist-Locked Mountain Gate by @op7418"><img src="studio/src/motion/game/community/mist-locked-mountain-gate.jpg" width="56" height="56" alt="Mist-Locked Mountain Gate (@op7418)" /></a>
  <a href="https://x.com/__morse/status/2122013410309153042" title="omw: Castle Valley by @__morse"><img src="studio/src/motion/game/community/omw-castle-valley.jpg" width="56" height="56" alt="omw: Castle Valley (@__morse)" /></a>
  <a href="https://x.com/loktar00/status/2120192761542615271" title="LANTERNFALL by @loktar00"><img src="studio/src/motion/game/community/lanternfall.jpg" width="56" height="56" alt="LANTERNFALL (@loktar00)" /></a>
  <a href="https://x.com/Andrew_Blumson/status/2120599812512833557" title="MAAD MAXXING by @Andrew_Blumson"><img src="studio/src/motion/game/community/maad-maxxing.jpg" width="56" height="56" alt="MAAD MAXXING (@Andrew_Blumson)" /></a>
  <a href="https://x.com/kevin_t_ngo/status/2119900487688622171" title="Gilt &amp; Gutter by @kevin_t_ngo"><img src="studio/src/motion/game/community/gilt-and-gutter.jpg" width="56" height="56" alt="Gilt &amp; Gutter (@kevin_t_ngo)" /></a>
  <a href="https://x.com/xikhar/status/2122682962647122403" title="Papertrails by @xikhar"><img src="studio/src/motion/game/community/papertrails.jpg" width="56" height="56" alt="Papertrails (@xikhar)" /></a>
  <a href="https://x.com/AravSrinivas/status/2122338465648103676" title="VICE '86 by @AravSrinivas"><img src="studio/src/motion/game/community/vice-86.jpg" width="56" height="56" alt="VICE '86 (@AravSrinivas)" /></a>
  <a href="https://x.com/FuSheng_0306/status/2121237878097207583" title="Starfall by @FuSheng_0306"><img src="studio/src/motion/game/community/starfall-moba.jpg" width="56" height="56" alt="Starfall (@FuSheng_0306)" /></a>
  <a href="https://x.com/aniketjart/status/2121793239175119279" title="Goku: Four-Star Road by @aniketjart"><img src="studio/src/motion/game/community/goku-four-star-road.jpg" width="56" height="56" alt="Goku: Four-Star Road (@aniketjart)" /></a>
  <a href="https://x.com/noclipepe/status/2119728047754547326" title="Rug Racers by @noclipepe"><img src="studio/src/motion/game/community/rug-racers.jpg" width="56" height="56" alt="Rug Racers (@noclipepe)" /></a>
  <a href="https://x.com/noclipepe/status/2119927838321328577" title="Dino Run: Locked In by @noclipepe"><img src="studio/src/motion/game/community/rambo-dino.jpg" width="56" height="56" alt="Dino Run: Locked In (@noclipepe)" /></a>
  <a href="https://x.com/AravSrinivas/status/2122713692324384793" title="HADAL by @AravSrinivas"><img src="studio/src/motion/game/community/hadal.jpg" width="56" height="56" alt="HADAL (@AravSrinivas)" /></a>
  <a href="https://x.com/emollick/status/2119876449494540554" title="I Would Have Gotten Away With It by @emollick"><img src="studio/src/motion/game/community/i-would-have-gotten-away.jpg" width="56" height="56" alt="I Would Have Gotten Away With It (@emollick)" /></a>
  <a href="https://x.com/petergyang/status/2119901658394358005" title="Turbo Tails by @petergyang"><img src="studio/src/motion/game/community/turbo-tails.jpg" width="56" height="56" alt="Turbo Tails (@petergyang)" /></a>
</p>

> **Notice:** Community games link directly to their creators' original pages and remain the sole property of their respective authors — no third-party source code is copied. If you are a creator and would like your work updated, credited differently, or removed, please [open an issue](https://github.com/nexu-io/opengame/issues) and we will address it promptly.

## Contributors

Thanks to everyone who has taken part — code, game templates, skills, docs, feedback, and issues.

<a href="https://github.com/nexu-io/opengame/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nexu-io/opengame&amp;max=500&amp;columns=20&amp;anon=1" alt="OpenGame contributors" />
</a>

## Star History

<a href="https://www.star-history.com/#nexu-io/opengame&amp;Date">
  <picture>
    <source srcset="https://raw.githubusercontent.com/nexu-io/opengame/readme-charts/star-history.svg" />
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=nexu-io%2Fopengame&amp;type=Date&amp;theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=nexu-io%2Fopengame&amp;type=Date" />
    <img alt="OpenGame Star History" src="https://api.star-history.com/svg?repos=nexu-io%2Fopengame&amp;type=Date" />
  </picture>
</a>
