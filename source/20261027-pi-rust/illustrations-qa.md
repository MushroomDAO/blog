# pi-rust XiaoM illustration delivery

Generated using the built-in image_gen tool, with exactly three separate generation calls. Prompts are saved as `fig-01-prompt.txt` through `fig-03-prompt.txt`. Original generated files are retained unchanged at the paths in `illustrations-provenance.json`; final PNGs are in `src/assets/images/`.

Visual review of all three illustrations:

- White horizontal canvas, black hand-drawn outlines, red cap with white spots, pale cream stem, active XiaoM, orange connections and limited blue accents.
- No written labels or titles. Only a terminal chevron/cursor and pictograms are used.
- Figure 1: one visible engine serves the terminal and application, with detachable tool modules and a model connector.
- Figure 2: saved checkpoint cards and resumed work are visually separate from the external-action checklist and parcel. Empty checklist boxes make no claim of universally completed or exactly-once side effects.
- Figure 3: native plugin, host and workspace share one physical base. The padlock is on the communication tunnel. No sandbox shield or plugin isolation enclosure appears.

Finalization uses ImageMagick only for framing, white-background cleanup and PNG palette compression. No article, banner, publishing, git operation or subagent work was performed for this request. The pre-existing `smoke-local-gateway.py` file is unrelated and was left untouched.

Exact final dimensions, byte counts and SHA-256 hashes are in `illustrations-provenance.json`. `finalize-illustrations.py` reproduces the deliverables from the originals. No temporary image candidates are written into the project.
