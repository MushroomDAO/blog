# Zero-to-CAD research and publication

Primary model ADSKAILab/Zero-To-CAD-Qwen3-VL-2B revision8cf9260904aa6eb29f0826e3585f25b7df61ff89; paper2604.24479v1. Sources model-card.md,dataset-card.md,model-config.json and research-verification.json.

Local check: create a Python3.12 environment, install cadquery==2.6.1, then run replay-official-sample.py. It replays the manually reviewed official test-row0 ground-truth code, checks valid single-solid geometry, exports STEP/STL and checks STEP roundtrip volume. It compares the official reference STEP but does not run the2Bmodel or reproduce published benchmarks. test-row.json is a captured HF rows API response, source hash/UUID and capture metadata recorded. Full weights were not downloaded.

Use check-content.py and verify-live.py for publication checks; check-search.py verifies public retrieval. New official-gallery cover and three explanatory XiaoM figures. Raw botKB material reused; precise dedup proved no prior article/M2record, despite broad PT-5.2 falsepositives. Publishedlist API48001unavailable; draftbox was checked before a new draft. Currentdraft verification saved separately.
