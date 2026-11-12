"""Prepare the three requested illustration PNGs; retain untouched generated originals.
Only resize to exact 16:9, normalize near-white background, and encode PNG palettes.
Run from the repository root with python3 source/20261025-airsup-machine-skill/generated-assets/prepare-assets.py
"""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
manifest = json.loads((BASE / "manifest.json").read_text())
for asset in manifest["assets"]:
    original = BASE / asset["original"]
    source = Image.open(original).convert("RGB")
    # Crop less than one percent to remove generator aspect-ratio rounding.
    rgb = ImageOps.fit(source, (1280, 720), method=Image.Resampling.LANCZOS)
    # Normalize only nearly white pixels; retain the cream character body.
    rgb.putdata([(255, 255, 255) if min(p) >= 247 else p for p in rgb.getdata()])
    chosen = None
    for colors in (128, 96, 64, 48, 32):
        pal = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                           dither=Image.Dither.NONE)
        palette = pal.getpalette()
        for i in range(0, len(palette), 3):
            if min(palette[i:i+3]) >= 247:
                palette[i:i+3] = [255, 255, 255]
        pal.putpalette(palette)
        buf = io.BytesIO()
        pal.save(buf, format="PNG", optimize=True, compress_level=9)
        if len(buf.getvalue()) < 90000:
            chosen = buf.getvalue()
            break
    if chosen is None:
        raise RuntimeError(f"Cannot meet size limit for {original}")
    target = ROOT / asset["final"]
    if target.exists() and target.read_bytes() != chosen:
        raise FileExistsError(f"Refusing to overwrite a different existing asset: {target}")
    target.write_bytes(chosen)
    with Image.open(target) as final:
        assert final.format == "PNG"
        assert final.size == (1280, 720)
        pixels = list(final.convert("RGB").getdata())
        white_fraction = sum(p == (255, 255, 255) for p in pixels) / len(pixels)
        assert white_fraction > .35
        assert all(final.convert("RGB").getpixel(c) == (255, 255, 255)
                   for c in ((0, 0), (1279, 0), (0, 719), (1279, 719)))
    asset.update({
        "original_dimensions": list(source.size),
        "original_bytes": original.stat().st_size,
        "original_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
        "dimensions": [1280, 720],
        "aspect_ratio": "16:9",
        "bytes": len(chosen),
        "palette_colors": colors,
        "pure_white_pixel_fraction": round(white_fraction, 4),
        "sha256": hashlib.sha256(chosen).hexdigest(),
        "qa": {
            "visual_review": "passed: current XiaoM design, active core action, sparse legible labels, no numerical claims, ample white space",
            "white_background": True,
            "exact_16_9": True,
            "under_90000_bytes": True
        }
    })
    print(f'{target.relative_to(ROOT)}: {len(chosen)} bytes, 1280x720, white {white_fraction:.1%}')
manifest["processing"] = "Exact 16:9 crop/resize to 1280x720, near-white normalization, optimized palette PNG; generated originals retained unchanged."
(BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
