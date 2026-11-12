# Minilytics body illustrations

Completed 2026-10-29 using `mycelium-mushroom-illustrations` and the built-in `image_gen` tool. Exactly three independent generation calls produced three separate illustrations; all three were accepted. No composite sheet or additional variant was generated.

| Final file | Anchor and XiaoM's action | Chinese labels | Dimensions | Colors | Bytes |
| --- | --- | --- | --- | --- | --- |
| [fig-01](../../src/assets/images/minilytics-cloudflare-revenue-attribution-fig-01.png) | Tagged visit linked to payment: XiaoM closes a binder ring through a tagged visit slip and payment receipt. | 来源标签 / 付款 | 1120×630 | 48 | 25,747 |
| [fig-02](../../src/assets/images/minilytics-cloudflare-revenue-attribution-fig-02.png) | Separate quotas: XiaoM scoops a data tile into the database container, with independent request and storage containers beside it. | 请求 / 数据库 / 存储 | 1120×630 | 48 | 20,609 |
| [fig-03](../../src/assets/images/minilytics-cloudflare-revenue-attribution-fig-03.png) | Verify one marketing-to-payment loop before expansion: XiaoM inspects the loop's join through a magnifying glass; an unused extension remains separate. | 推广 / 付款 / 先核验 | 1120×630 | 48 | 24,745 |

All three are intended for the requested anchors; none is an optional alternate.

## Originals and reproducibility

Unmodified generated PNGs remain in the tool archive listed below. Redundant source-directory raster copies were removed after generation:

The tool's original files also remain at `/Users/jason/.codex/generated_images/01a186ff-516b-73f1-ab80-a2569ce2af3a/`, respectively:

1. `exec-5b23e519-b243-489d-a896-9f26371cfe71.png`
2. `exec-d75790f7-8306-4624-a19a-8e4a8ba5fe31.png`
3. `exec-61a17b02-2a3b-4668-be57-7b8a8baf6da0.png`

Original dimensions are 1672×941. The delivery files are resized to exact 16:9 with no content cropped. The exact three generation prompts are saved in [prompts.json](illustrations-originals/prompts.json). The built-in tool was used, with no fallback CLI generation.

[prepare.py](illustrations-originals/prepare.py) reproduces the delivery files using Pillow: Lanczos resize, collapse near-white generation tones to pure white, median-cut quantization to 48 colors without dithering, merge duplicate palette indices, and optimized PNG compression. Each final file uses exactly 48 distinct RGB colors. The 960×540 fallback was unnecessary.

Run from the repository root:

```bash
/Users/jason/venvs/ml/bin/python source/20261029-minilytics-nsh/illustrations-originals/prepare.py
```

[manifest.json](illustrations-originals/manifest.json) records original and final SHA-256 hashes, dimensions, actual color counts, byte sizes and white-pixel percentages.

## Verification

- Inspected all three final PNGs after resizing and quantization.
- Each is a separate 16:9 image with a pure white background, sparse hand-drawn black outlines and restrained color accents.
- XiaoM has a red cap with white spots, a pale stem and black dot eyes, and actively performs the central action in each image.
- Labels are readable and limited to two, three and three short Chinese phrases respectively.
- No background grid, fence, slide framing, dense diagram or visible background texture. No title or explanatory paragraph is embedded in the images.
- Pure white pixels account for 93.94%, 95.21% and 94.02% of the final canvases; all corners are exact RGB 255,255,255.
- All three PNGs are 1120×630, palette mode, exactly 48 colors, and below 90,000 bytes.
- No article or banner write was performed by this task. No deploy, build, publication or commit command was run.

## Concurrent workspace observation

The banner's SHA-256 remained `0db63f0ec58821d12c9a61e16f466f655a4c3a60c2577c748cec48f1c5872644`.

The article changed during this task through another workspace operation: its initial SHA-256 was `e8afcdc1fa1258809890d8d747e77cc6e21df835762a9e3487587bee09282cb7`, while the value observed at final verification was `51143a83e03062834eb68c2892b2609463902f40f065f6184e4b0f8741b567ff`. A changed description was visible. This illustration task did not write to or revert the article, and does not claim the article remained unchanged.

Primary session note: description and related-article URL edits were intentional; figure anchors remained unchanged. Manual final art accepted.
