# OpenGame architecture

OpenGame combines a visible game workspace, coding agents, reusable game source, media generation and verification. **Game Studio and the Agent operate on the same owned game files.** The product presents this as the Super Game Agent experience; the source keeps interface, agent execution, domain services and delivery as separate layers.

[Run from source](opengame-setup.md) · [Game workflow](../skills/openmotion-game/SKILL.md) · [Game tool contract](../shared/game-tools.ts)

## Product creation loop

![OpenGame creation stack](readme/opengame/diagrams/creation-stack.svg)

A reference describes the experience to create. A bundled template provides source that can be copied into an independent project. Community references supply a new brief; they do not silently import another creator's source or assets. The agent develops the core loop, builds or selects the art and audio, implements the files and records verification before delivery.

Game Studio exposes genre, style, setting, orientation and playable-ad choices. The Artifact Viewer shows the game and its code alongside the conversation, making iteration a cycle of describe, build, play and refine. The project remains editable after the first playable result.

## Runtime and boundaries

![Game Studio and agents share the local application and game workspace](readme/opengame/diagrams/runtime-architecture.svg)

| Layer | Responsibility | Maintained source |
| --- | --- | --- |
| Studio | Creation controls, discovery, project handoff and playable/source views | [GameStudio.tsx](../studio/src/motion/game/GameStudio.tsx), [ArtifactBrowserPane.tsx](../studio/src/super-agent/ArtifactBrowserPane.tsx) |
| Agent execution | Selected local client, conversation context, execution and tool access | [Agent runtimes](../gateway/agent-runtimes.ts), [Super Agent](../gateway/super-agent.ts), [29 client definitions](../shared/local-agents.ts) |
| HTTP and MCP entry points | Serve the interface and expose the shared domain operations | [server.ts](../server.ts), [mcp.ts](../mcp.ts), [game tool schemas](../shared/game-tools.ts) |
| Game domain | Creation, independent remixes, owned files, metadata, preview, validation and lifecycle | [GameProjects](../game-projects.ts), [game contract](../shared/game-contract.ts) |
| Media and assets | Model discovery, provider configuration, generation jobs and reusable asset versions | [Model catalog](../gateway/catalog.ts), [provider registry](../shared/provider-registry.ts), [asset library](../gateway/asset-library.ts) |
| Verification | Source checks, deterministic rule simulation, isolated browser input and captures | [Game service](../game-projects.ts), [browser runtime](../browser.ts), [game tests](../tests/game-projects.test.ts) |
| Delivery | Local catalog, hosted static snapshots and gameplay-to-video jobs | [Game service](../game-projects.ts), [web publishing](../gateway/web-publish.ts), [game flow](../skills/openmotion-game/references/game-flow.md) |

### Two ways to work with an agent

1. **Inside Game Studio:** select a local agent and submit the brief. The game handoff carries the game ID and instructions into the integrated Super Agent runtime. Agent operations update the same files shown in preview.
2. **Inside an external agent:** connect local stdio MCP and use the game workflow and tools. Point Studio and MCP at the same absolute `MOTION_DATA_DIR`; otherwise they see different workspaces.

Creating a draft with `openmotion_game_create` returns its identity and brief. That operation alone does not execute an agent, complete the game or publish it. The integrated handoff or external agent supplies the creation work.

The current source retains `openmotion_game_*` tool names and the `openmotion-game` Skill. OpenGame branding does not change those connection identifiers. The [12 game tools](../shared/game-tools.ts) cover creation, inspection, file changes, metadata, cover capture, validation, simulation, play-testing, trailer jobs, readiness and local publication.

## The project is the handoff

![Game plan, asset inventory, verification and source stay together](readme/opengame/diagrams/project-context.svg)

Owned games are stored under the selected workspace's `games/<game-id>/` directory. Source installations and the full distribution ZIP include `templates/games/`. The default npm package ships each template's metadata and cover, the starter kits, and a playable offline Tidebreaker. On first play or Remix of another template, the local game service downloads its version-pinned ZIP from `releases.open-design.ai/open-game/games/objects/`, verifies its length, SHA-256 and archive entries, and installs it atomically under the workspace's `game-template-cache/<hash>/`. A completed download works offline across restarts. Remix creates a separate owned copy. New npm releases pin a new index; old installations continue to use their original game versions.

```text
MOTION_DATA_DIR/
└── games/
    └── <game-id>/
        ├── game.json                # identity, metadata and lifecycle
        ├── index.html               # playable entry
        ├── *.js / *.css             # game-specific source organization
        ├── assets/                  # project files and captured evidence
        └── design/
            ├── plan.md              # experience, art direction and acceptance
            ├── assets.csv           # sources, licenses and approved costs
            └── verification.md      # checks, results and remaining gaps
```

The exact source layout is chosen by the game. Projects implementing deterministic simulation provide `logic.js` with the expected rule interface. The design documents are workflow context supplied to the agent, not an automatic long-term memory or retrieval service.

The game service serializes mutations within its service instance, restricts writes to workspace-owned files and keeps template metadata separate. Editing a ready or published game returns it to `building`. A `ready` flag by itself is not proof that a check passed.

## Media supply

The Model Gateway separates model discovery from execution. Built-in presets provide initial choices; configured provider catalogs can supply additional models. Image, video, music, speech and sound-effect results enter the asset workflow and can be referenced by game files.

Provider setup belongs to the runtime environment. Project documents record the assets selected and their provenance. Asset discovery, a submitted generation job and a completed usable asset are separate states. See [Model Gateway](model-gateway.md), [asset library](assets.md) and [provider settings](provider-settings.md).

## Verification and delivery

| Stage | Input | Evidence or result |
| --- | --- | --- |
| Validate | Current entry files, local references and supported source contracts | Diagnostics for missing or unsupported resources |
| Simulate | A supported deterministic rule implementation and reference/idle routes | Rule outcomes and bounded state snapshots |
| Play-test | Current game files and keyboard/mouse scripts | Browser errors, failed requests, state assertions and screenshots |
| Capture | Running game and a bounded input sequence | A real game cover |
| Local publication | An owned game that passes the publication check | A playable entry in the local catalog |
| Web sharing | Game files, referenced assets and configured hosting | A static snapshot at the returned URL |
| Trailer | A ready/published game and the prepared video runtime | Gameplay clips, an editable Motion project and verified MP4 |

Browser automation here is performed by the application's isolated headless browser. It is separate from the user's browser session. Human evaluation still determines whether the controls feel good, the game is enjoyable and the release is ready.

Web sharing creates a snapshot. Later source edits do not update that snapshot automatically. Gameplay trailers are separate editable video projects; they do not replace the game source. The local `openmotion_game_publish` operation registers a game in the local catalog. Product distribution to TikTok, WeChat and Douyin uses the corresponding platform release integration rather than changing that MCP operation's meaning.

## Stack and extension points

The source uses Node.js and TypeScript for application services; React, Vite, Tailwind CSS and Zustand for Studio; browser HTML/CSS/JavaScript for playable games; and Chrome plus FFmpeg/ffprobe for capture and video delivery. Dependency pins are in [package.json](../package.json), [package-lock.json](../package-lock.json) and the [runtime lock](../scripts/runtime-lock.json).

- **Game creators:** add a focused, runnable template with clear controls, cover art, asset credits and play-test evidence.
- **Frontend contributors:** improve creation, preview, code inspection and handoff through the shared design system.
- **Agent contributors:** improve client adapters, game tools, workflow instructions and reproducible verification.
- **Model contributors:** add or improve provider adapters using the existing model and asset job lifecycle.
- **Delivery contributors:** improve bundle handling, snapshot reliability or gameplay trailer capture, with reproducible checks.

Use the [contribution guide](../CONTRIBUTING.md). This document describes the game boundary; the retained [shared product architecture](product/architecture.md) covers the wider runtime and video/design modules.
