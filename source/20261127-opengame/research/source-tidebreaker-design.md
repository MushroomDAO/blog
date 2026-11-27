# Tidebreaker

## Experience formula

A storm-chasing speedboat sprint: read the approaching gate, carve the turn, leap a wave and carry the boost into the next checkpoint.

## Loop and rules

Auto-throttle through a pseudo-3D projected archipelago course. Steer to gates; brake for control. Space launches a short jump with a 1.5-second cooldown. Clearing a wave/reef while airborne grants 2.1 seconds of boost. Rocks remove 24 hull, unjumped swells remove 9; banks slow and damage the boat. Each successful gate adds 3 seconds; misses subtract 4.

## Ending and ramp

Start with 100 hull and 65 seconds. Finish the eighth gate with at least six passed to qualify. Zero hull/time loses. R and the end menu fully reset the run. Gate tolerance narrows and cruising speed rises after each success; repeated hazards demand earlier steering. The route is deterministic; visual spray is cosmetic.

## Art direction

Built-in image generation only; original art, no brands or external runtime dependencies. Cover: painterly 16:9 key art with the game title. Two in-game assets are loaded and rendered in the actual play scene. Flat-magenta sprites are keyed to real alpha with Pillow and edge colors decontaminated. Final assets are locally resized/compressed; generation originals are not shipped.

## Input and presentation

A / D or arrows steer · W accelerates · S brakes · Space jumps; Mouse: hold and steer · Touch: drag to steer or use buttons. P / Escape pauses; R restarts. Sound starts muted and can be enabled after a user gesture. Backgrounding clears inputs and pauses. Menus support native keyboard focus, responsive layouts and reduced motion.

## Verification — 2026-11-20

- `node templates/games/tidebreaker/verify-offline.cjs`: all three games, 115 assertions passed, including 300 simulated 60 Hz frames each, input, pause/resume/restart, game endings, upgrade effects, catalogue schema and asset closure. This harness uses a stub DOM and canvas, not Chrome.
- `GAME_TEST_WIDTH=390 GAME_TEST_HEIGHT=844 node templates/games/tidebreaker/verify-offline.cjs`: the same 115 assertions passed at portrait geometry.
- Lighthouse story enumerates all 2,187 choice sequences; 2,134 produce a valid complete/early-ending run under fuel restrictions. Four ending labels and rescue counts from zero through five are reachable. Prefixes ending early are counted once per enumerated sequence, not as unique paths.
- Pillow checks: 1280×720 cover; under-budget files; genuine 0–255 alpha on sprites; no opaque magenta key fringe.
- JavaScript compilation and `git diff --check` passed.
- Browser acceptance remains **unverified**: starting the required local HTTP server returned `listen EPERM: operation not permitted 127.0.0.1:41873`; the specified Chrome executable also failed to launch in this sandbox. No real browser screenshots or frame-rate measurements were produced.
- `node templates/games/tidebreaker/verify-browser.cjs` is prepared for a local session that permits loopback listeners and Chrome. It serves only the three new games, blocks external page requests, starts through actual UI controls, plays for at least five seconds, checks errors, pause/restart and portrait touch, then saves `<id>-title.jpg`, `<id>-play.jpg` and `<id>-mobile.jpg` into each game's `screenshots/` folder.
- The requested Desktop screenshot destination was not written because the task restricts writes to the new game folders. `screenshots/` is reserved, currently empty; no screenshot should be inferred from this document.
- The built-in generation tool automatically saved its original-image cache outside the checkout; its interface does not expose a save-location setting. Only compressed final assets are part of these game folders. No paid API or CLI internet request was used.
