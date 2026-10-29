# Evidence and assumptions

Purpose: demonstrate teardown's viewer and export controls, not a real device teardown.
Output: A3 landscape vector sheet; PNG download at 300dpi. Preview 1400x900.

| Feature group | Evidence class | Treatment |
|---|---|---|
| Three functional layers | Concept with no physical form | Each idea represented by one plate; source,filter,cover names are illustrative |
| Width70–110,depth60,thickness2,gap0.3 | Hidden/unspecified geometry | All invented for demonstration; not manufacturing dimensions |
| Assembled placements and explosion | Authored concept geometry | One model and inventory; explosion0 reconstructs assembled positions |
| Part colors and labels | Authored presentation | Three distinguishable line hues and tint fills; English labels for bundled Latin font |

The example does not reconstruct a commercial screen or claim materials, tolerances, or optical accuracy.

Rebuild:
- npm ci --ignore-scripts
- node tools/teardown/scripts/proof.cjs drawing.json proof/
- node tools/teardown/scripts/build-viewer.cjs drawing.json dist/index.html
- node tools/teardown/scripts/check-viewer.cjs dist/index.html check/

Actual export checks: node tools/teardown/scripts/check-exports.cjs (after building the viewer). SVG metadata retains labels and selected filter #594fd7; PNG 4961x3508 at ~300dpi. PDF download checked only. Hosted page renders all 3 parts; Cloudflare injects analytics, unlike standalone local HTML.
