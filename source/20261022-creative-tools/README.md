# Creative tools research and publication evidence

Task: e6d6d22c-7207-4fa9-86c8-17a1a5b901d0. Date: 2026-10-22.

Three new bilingual topics: Ondine, live-panel-skill, awesome-animation-datasets/Motion Viewer. Existing onetake-envmanage-source-check updated in place with the Clawd case, retaining slug and matched qualified cover/body figures. No duplicate onetake article or draft was created.

Source pins are in the four compact *-meta.json files. `verify-source.py` fetches primary files at those pins, checks specific statements and the 45 published quality entries/nine thresholds; it does not measure performance or recompute dataset metrics. Full upstream snapshots stay local.

Agent-reach was absent from skill roots and PATH. Jina Reader was attempted as the user allowed: GitHub requests returned 403, so raw pinned GitHub bodies/API were used; Jina returned the HF Space shell, while its direct static app returned HTTP200 and control HTML. No claim of playing every dataset. Downloaded research images remain under /Users/jason/.heinu1-bot/media/creative-tools-*.

## Actual local checks

`python source/20261022-creative-tools/fetch-renderer.py` fetches 14 pinned live-panel renderer files into /tmp/creative-live-panel. No skills are installed or global application settings changed.

- CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' python -m unittest discover -s /tmp/creative-live-panel/tests -v
- python /tmp/creative-live-panel/scripts/render.py --config /tmp/creative-live-panel/examples/minimal/config.json --out /tmp/creative-live-panel/smoke.mp4 --width 600 --height 750 --duration 2 --fps 12 --html-out /tmp/creative-live-panel/smoke.html
- python /tmp/creative-live-panel/scripts/check_frames.py --config /tmp/creative-live-panel/examples/minimal/config.json --out-dir /tmp/creative-live-panel/checked --repeat

Results: three original browser regressions pass; minimal config 124 sampled time points, zero problems; four replay comparisons zero visibly different pixels. ffprobe verifies a two-second H264 24-frame 600x750 clip plus AAC (silent, not speech). Root visually viewed the sample. This does not establish speed, every example or every theme/font.

Ondine is a source/benchmark-report review only. Keep mounting-only bytes separate from compiler and SVG payload, README210B versus report127B discrepancy explicit, and arithmetic means/geometric ratios/module lanes separate. No comparative layout or performance run was performed.

Motion quality JSON was inspected and counted, not recomputed. Catalogue MIT-code/CCBY-list rights do not override original datasets. Preview cropping/resampling and known red-flag false alarms are disclosed.

Original onetake Clawd case ships the film only, not composition/model/score/source sound. No itemized20yuanAPIcost evidence found. Existing old draft receipt returns40007, absent remote batchget, freepublish API48001; preserve archived ID as recorded rather than creating a possible duplicate.

## Publication checks

All three original FLUX concept covers and nine new XiaoM figures were visually reviewed, as were the reused onetake cover and three original body figures. Upstream imagery was considered but mostly diagrams/text-heavy banners, and was not used as a new cover. New figures1280x720<90000bytes; reused figures1600x900 remain qualified16:9 and<90000bytes. Covers1200x630<99000bytes.

`check-content.py` performs metadata, bilingual, FAQ, source and image checks. One canonical build/deploy contains the batch; remaining semantic updates and draft creation follow sequentially after public URL validation. `verify-live.py` checks all four pages and16images, and new article ordering; onetake retains original pubDate. `verify-draft.cjs` reads each new draft back from WeChat. Draft receipts do not prove old content is still a draft.
