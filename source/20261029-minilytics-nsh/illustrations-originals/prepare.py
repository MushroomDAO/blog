"""Rebuild the three delivery PNGs from preserved imagegen originals."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / "src/assets/images"
SLUG = "minilytics-cloudflare-revenue-attribution"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


results = []
for index in range(1, 4):
    originals = ["exec-5b23e519-b243-489d-a896-9f26371cfe71.png", "exec-d75790f7-8306-4624-a19a-8e4a8ba5fe31.png", "exec-61a17b02-2a3b-4668-be57-7b8a8baf6da0.png"]
    original = Path("/Users/jason/.codex/generated_images/01a186ff-516b-73f1-ab80-a2569ce2af3a") / originals[index - 1]
    target = ASSETS / f"{SLUG}-fig-{index:02}.png"
    with Image.open(original) as source:
        for dimensions in [(1120, 630), (960, 540)]:
            resized = source.convert("RGB").resize(dimensions, Image.Resampling.LANCZOS)
            # Reserve the color budget for the drawing rather than near-white
            # generation noise. This also gives the final canvas a pure white base.
            red, green, blue = resized.split()
            minimum = ImageChops.darker(ImageChops.darker(red, green), blue)
            background = minimum.point(lambda value: 255 if value >= 245 else 0)
            resized.paste((255, 255, 255), (0, 0), background)
            final = resized.quantize(
                colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
            )
            # Collapse generated near-white background tones to exact white
            # in the quantized palette, without touching the original artwork.
            palette = final.getpalette()
            for start in range(0, len(palette), 3):
                if min(palette[start : start + 3]) >= 245:
                    palette[start : start + 3] = [255, 255, 255]
            # Equal white colors must also share an index; otherwise invisible
            # source noise survives in the indexed stream and inflates the PNG.
            canonical = {}
            remap = []
            for start in range(0, len(palette), 3):
                color = tuple(palette[start : start + 3])
                remap.append(canonical.setdefault(color, start // 3))
            remap.extend(range(len(remap), 256))
            final = final.point(remap)
            final.putpalette(palette)
            final.save(target, optimize=True, compress_level=9)
            if target.stat().st_size < 90000:
                break
        assert target.stat().st_size < 90000, target
        with Image.open(target) as check:
            colors = check.convert("RGB").getcolors(check.width * check.height)
            white_pixels = sum(n for n, color in colors if color == (255, 255, 255))
            assert check.width * 9 == check.height * 16
            assert len(colors) <= 48
            rgb = check.convert("RGB")
            assert all(rgb.getpixel(point) == (255, 255, 255) for point in [
                (0, 0), (check.width - 1, 0),
                (0, check.height - 1), (check.width - 1, check.height - 1)
            ])
            results.append({
                "image": index,
                "original": str(original.relative_to(ROOT)),
                "original_size": list(source.size),
                "original_sha256": sha256(original),
                "final": str(target.relative_to(ROOT)),
                "dimensions": list(check.size),
                "bytes": target.stat().st_size,
                "mode": check.mode,
                "quantize_colors": 48,
                "actual_colors": len(colors),
                "pure_white_percent": round(100 * white_pixels / (check.width * check.height), 2),
                "sha256": sha256(target),
            })

(HERE / "manifest.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
