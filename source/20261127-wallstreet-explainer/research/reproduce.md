# Local smoke reproduction

Check out b79bc0573455cb5fe335e78f653012e658fa9758 of the upstream repository in a disposable directory. Install the Playwright version recorded in package-lock.json using npm with lifecycle scripts disabled, then install the documented Chromium browser. Node 26.10.0, FFmpeg 9.0.2 were used on macOS ARM.

1. Run original scripts/new_film.mjs on an empty target. With no supplied fonts, original scripts/render.mjs --dir TARGET --check fails on font404; preserve this failure.
2. Run timeline-check.mjs after adjusting its import to your checkout's scripts/timeline_stub.mjs. Eight synthetic assertions, not ASR or TTS.
3. Use the saved render-fixture/index.html and timeline.json. Original scripts/render.mjs --dir FIXTURE --stills 0,1,1.9 --h 360, followed by --video --h 360 --workers 1. View frames.
4. ffprobe -v error -show_streams -show_format -of json FIXTURE/out/visual_360.mp4. Assert H264,640x360,30fps,60frames,2seconds and no audio stream. Decode all frames with ffmpeg -v error -i FILE -f null -.

The fixture is ours; its sizing was corrected after initial visual inspection. The renderer source was not edited. Final fixture output is archived. No production-speed comparison, full-film test, external service calls, fetched news footage, synthesized voice, ASR alignment or mixing is implied. Upstream fonts must be prepared for a real starter-based production.
