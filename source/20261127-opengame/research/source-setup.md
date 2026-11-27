# Run OpenGame from source

This guide installs the `nexu-io/opengame` checkout and connects its game tools to a local agent. Use the source checkout for the game workflow described in this repository.

## Prerequisites

- Git, Git LFS, npm and Node.js **26.11.1** (the CI version). `package.json` declares Node.js 22.18.0 or later.
- A local agent with stdio MCP support for AI-assisted creation. Browsing and playing bundled games does not require an agent connection.
- Chrome/Chromium for automated game screenshots and play-tests. Video trailers additionally require FFmpeg/ffprobe and the prepared export runtime.
- Media-provider credentials or an OpenDesign account only when using the corresponding generation or hosting services.

## Install the main OpenGame Skill

Install the main `opengame` Skill once through the official Skills CLI as the first setup step before cloning or configuring MCP (using the lightweight `skills` branch so Skills CLI skips cloning the full game template catalog while still attributing installs to `nexu-io/opengame`):

```sh
npx --yes skills@1.9.0 add https://github.com/nexu-io/opengame/tree/skills --skill opengame --global --agent AGENT --copy --yes
```

Use `codex` for Codex and `claude-code` for Claude Code. For DeepSeek Harness (DSH) or any host without a dedicated Skills CLI target, use `universal`. Select only the intended host; for custom or isolated profiles, omit `--global` and run inside that profile or project directory instead of the daily global profile.

Reuse an existing official installation and skip this step if `opengame` is already installed from `nexu-io/opengame` (for example, when setup started from the `opengame` Skill itself). Preserve unrelated Skills, foreign same-name entries, and the CLI's telemetry opt-outs (`DISABLE_TELEMETRY`, `DO_NOT_TRACK`). Setting `OPENMOTION_SKIP_PUBLIC_SKILL=1` skips this optional step. Do not reinstall merely to generate another install event.

A Skills CLI failure or timeout does not block Studio or MCP setup: report it briefly and continue below. Skills CLI installs instructions only; continue the local source installation and stdio MCP setup below in this same conversation.

## Install and build

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --single-branch --branch main https://github.com/nexu-io/opengame.git
cd opengame
git lfs install --local --skip-smudge
npm ci
npm run build:studio
```

The shallow clone includes game source, catalog metadata, covers and the complete Tidebreaker game. Other templates keep binary assets in Git LFS. Studio and MCP fetch the selected template's assets on demand and reuse them in this checkout. To prepare a template for offline use, run `git lfs pull --include="templates/games/<game-id>/**" --exclude=""` from the checkout. Optional videos have separate [storage instructions](repository-storage.md).

## Start a separate workspace

Keep project data outside the checkout. Use the same absolute data directory for Studio and MCP so the agent edits the games you see.

macOS / Linux:

```sh
MOTION_DATA_DIR="$HOME/.opengame/workspace" npm start
```

Windows PowerShell:

```powershell
$env:MOTION_DATA_DIR = Join-Path $env:USERPROFILE '.opengame\workspace'
npm start
```

Open the exact `previewUrl` returned by startup, then select **Game Studio**, or append `/game` to that origin. Do not assume a fixed port: the runtime may reuse a compatible service or select another free port.

Browse a template and play it. **Remix** creates an independent editable draft in the chosen workspace. In the integrated Studio, this action can immediately hand the task to the selected local Agent; ensure that the intended Agent and model are selected before starting. The service's draft-creation operation alone does not finish the game. An external-client handoff may instead provide instructions to continue in that client.

## Connect your local agent

Use your client's local stdio MCP configuration. The example below is the JSON format used by clients that support an `mcpServers` object; translate it into the native format for other clients. Replace all placeholder paths with absolute paths, including the Node executable returned by `command -v node` (macOS / Linux) or `(Get-Command node).Source` (PowerShell).

```json
{
  "mcpServers": {
    "opengame": {
      "command": "/absolute/path/to/node",
      "args": [
        "--experimental-strip-types",
        "/absolute/path/to/opengame/mcp.ts"
      ],
      "env": {
        "MOTION_DATA_DIR": "/absolute/path/to/.opengame/workspace"
      }
    }
  }
}
```

For Windows JSON, escape backslashes (`C:\\Users\\name\\...`) or use forward slashes. In this example, `opengame` is only the client-side connection label. The main entry Skill is **`opengame`** ([`skills/opengame/SKILL.md`](../skills/opengame/SKILL.md)), while the current public tool prefix remains **`openmotion_game_*`**, the specialist game workflow Skill remains **`openmotion-game`**, and the resource URI remains **`openmotion://workflow/game/start`**. Renaming those MCP identifiers would prevent discovery or calls from matching this implementation.

Refresh MCP in the selected client. Ask the agent to discover its tools, read the game workflow resource and inspect the draft you selected. A saved configuration is not proof of an active connection; verify that `openmotion_game_get` can read that draft's exact ID in the intended workspace.

Both the [entry Skill](../skills/opengame/SKILL.md) and the [game workflow Skill](../skills/openmotion-game/SKILL.md) are also available directly in the checkout. Installing Skill instructions does not install the application or connect MCP. A cloud-only client cannot reach a local stdio process through this configuration.

## Create and remix

Start from a template's **Remix** action or ask your connected agent to create a single-player game. Supply the target device, core action and visual direction. The agent should read the existing project before editing, implement the game, validate it and play-test the controls.

```text
Use the game workflow to create a portrait puzzle with five short levels.
The player sorts colored rings between poles. Add undo, a restart button
and clear touch controls. Use procedural graphics for this first version.
Validate and play-test it, then give me its local play link.
```

The game service exposes creation, reading, file edits, metadata, validation, simulation, play-testing, cover capture, status, local publication and gameplay trailers. See the current [tool schemas](../shared/game-tools.ts) for exact names and inputs.

## Staying up to date

When running from a clean Git checkout on `main`, creation and generation calls across OpenGame and OpenMotion (`openmotion_game_create`, `openmotion_create_project`, `openmotion_design_project` with `action: "create"`, `openmotion_capability_run` without `dryRun`, and `openmotion_assets_use` / `openmotion_media_use` with `action: "generate"`) share a single 24-hour check window in `MOTION_DATA_DIR/.update-check.json` and silently apply newer `origin/main` commits before running. Dependencies and Studio assets are rebuilt only when their input fingerprints change, local copies of installed Skills are refreshed, an idle local backend is restarted cleanly on macOS, Linux and Windows (if active work or an unmanaged backend defers restart, `restartDeferred: true` is returned so the updated backend takes effect on the next restart), and any build failure rolls back automatically to the previous commit.

- **Manual update anytime:** run `npm run update` (or `node --experimental-strip-types scripts/update.ts --apply`) from the checkout root. Use `--check` to inspect status without applying changes.
- **Disable automatic checks:** set `OPENMOTION_AUTO_UPDATE=0` in the MCP server's `env` block. Local edits or non-`main` branches are never overwritten automatically.

## Generation and sharing

Configure only the providers you intend to use. Available models are discovered from the connected environment; paid image, music or voice generation uses the selected provider or account balance. See the [media workflow](../skills/openmotion-media/SKILL.md).

- **Local publication:** `openmotion_game_publish` lists the game in this workspace's catalog. Game tools return an absolute link to this OpenGame instance. A localhost URL is only reachable on the machine running it.
- **Public sharing:** the separate `openmotion_assets_use` operation with `action: "web_publish"` and `targetKind: "game"` publishes a static snapshot through an authenticated OpenDesign account and hosting workspace. Follow the [game sharing guide](../skills/openmotion-game/references/game-flow.md). Check the returned status and final URL; later local edits do not automatically update a published snapshot.
- **Multiplayer:** new creation is single-player. Existing local room-based projects keep their local server requirement; static hosting does not deploy that server.
- **Trailers:** gameplay capture and video export have additional Chrome/FFmpeg/runtime prerequisites. Automated captures do not establish sound quality, real-device performance or human gameplay acceptance.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| The agent cannot find the game | Match `MOTION_DATA_DIR` between Studio and the MCP process; use the selected draft's ID. |
| MCP has no game tools | Verify the source path points to this checkout's `mcp.ts`, then refresh discovery in the client. |
| A template cannot be edited | Use **Remix** to create an owned draft first. |
| Play works but automated capture fails | Check Chrome/Chromium availability and loopback access; ordinary play and server-side capture have different requirements. |
| A shared link still shows the previous version | Publish a new static snapshot through the sharing flow. |

If you or your agent reproduce a bug in setup, template downloads or Studio, we welcome a fix via pull request against `main` in [nexu-io/opengame](https://github.com/nexu-io/opengame). Include the steps to reproduce and how you verified the fix. See the [contribution guide](../CONTRIBUTING.md).

[Back to OpenGame](../README.md)
