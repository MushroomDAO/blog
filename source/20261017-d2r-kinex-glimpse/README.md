# D2R build / Kinex / Glimpse — source and publication evidence

Task `01aab571-1dee-4913-ad9b-440e40fb50ae`, inspected 2026-10-17.

These are three unrelated topics. `topics.json` records final slugs and pinned primary sources. `source-dedup.txt` shows the original bot material is the only matching KB record, with no prior article/current draft/local creation receipt. The account cannot list published WeChat articles (`48001`), a documented visibility gap rather than proof of absence.

- D2R: `jiayx/d2r-mobile-build` at `e92853236714bbf96642faadd781dccf29da9c9c`, MIT workflow repository. Initial system Python is too old for `zip(strict=True)`; Python 3.12 passes all 35 upstream tests. No game resource download, app compilation, installation or gameplay test.
- Kinex: `stacx-lab/kinex` at `15207927c6669fe98f1213a3fd05148e0fe938d3`, Apache-2.0. Nine upstream `driver_contract.py` tests pass; no simulator, model or robot execution. The Hugging Face dataset at commit `cfd43319636672a7dfba9c7cd3a783f7307adee2` contains 396 public episodes; recomputed means include failures and represent estimated API-equivalent prices, not billing proof.
- Glimpse: Elorian launch dated 2026-10-16, API/chat research preview. No verified downloadable official weights found. A same-name benchmark is not this model. The developer game anecdote lacks original complete evidence; article reports this limit. Integration design is our proposal, without paid inference or game benchmarking.

To reproduce the episode arithmetic, download the exact source file beside `recompute-kinex.py`:

```bash
curl -fL https://huggingface.co/datasets/stacx-lab/kinex-benchmark-release/resolve/cfd43319636672a7dfba9c7cd3a783f7307adee2/episodes.jsonl -o source/20261017-d2r-kinex-glimpse/kinex-episodes.jsonl
python3 source/20261017-d2r-kinex-glimpse/recompute-kinex.py
```

Expected SHA256: `74eba953f23ddc5fb81de80f32774d80105a86bcf78562450aca5bfb1c97530c`.

`reproduce-source-checks.sh` accepts explicit external checkout/interpreter paths. It does not install an application or start robot services. Large downloaded HTML/raw data and full nested generation logs stay local; small results and reproduction scripts are versioned.

All covers and nine explanatory figures are conceptual. Machine banner gates and final visual review complement one another. Cropping the D2R and Glimpse concept covers removed generated keyboard/lens glyphs missed by OCR; this is not a gameplay screenshot. Publication receipts, public URL/asset checks and remote draft checks are saved separately from local creation credentials.

The corrected Glimpse timeline figure is a schematic with ordered and aligned source timestamps; the final compressed file uses48 colors. Root accepted the generated correction and ended further pixel-position refinement rather than waiting for more variants.
