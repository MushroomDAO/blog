"""Re-export the three original NSH illustrations; never touch article or banner."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = ROOT / "src/assets/images"
SLUG = "nsh-native-shell-cross-platform-ui"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def export(original, size):
    with Image.open(original) as source:
        resized = source.convert("RGB").resize(size, Image.Resampling.LANCZOS)
        # Normalize the generated near-white background before palette selection.
        resized.putdata([
            (255, 255, 255) if min(rgb) >= 245 and max(rgb) - min(rgb) <= 8 else rgb
            for rgb in resized.get_flattened_data()
        ])
        indexed = resized.quantize(
            colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
        )
    # Collapse near-white palette shades to exact white, removing background noise.
    palette = indexed.getpalette()
    for offset in range(0, len(palette), 3):
        rgb = palette[offset:offset + 3]
        if min(rgb) >= 245 and max(rgb) - min(rgb) <= 8:
            palette[offset:offset + 3] = [255, 255, 255]
    indexed.putpalette(palette)
    output = BytesIO()
    indexed.save(output, format="PNG", optimize=True, compress_level=9)
    return output.getvalue()


manifest = []
for number in range(1, 4):
    originals = ['exec-e757e12f-0dcb-445a-80de-6dec8877303c.png', 'exec-663d39d6-7d07-49ed-9356-bebd9cb45ffe.png', 'exec-d616c458-f61d-489d-8c01-c7b55702606f.png']
    original = Path('/Users/jason/.codex/generated_images/01a18702-0cd1-70b3-9340-62d15c218355/') / originals[number - 1]
    destination = ASSETS / f"{SLUG}-fig-{number:02d}.png"
    for size in [(1120, 630), (960, 540)]:
        encoded = export(original, size)
        if len(encoded) < 90000:
            break
    else:
        raise ValueError(f"Cannot meet size limit: {destination}")
    destination.write_bytes(encoded)
    with Image.open(destination) as final:
        rgb = final.convert("RGB")
        colors = len(rgb.getcolors(maxcolors=256))
        corners = [rgb.getpixel(point) for point in (
            (0, 0), (size[0] - 1, 0), (0, size[1] - 1),
            (size[0] - 1, size[1] - 1)
        )]
        assert final.format == "PNG" and final.mode == "P"
        assert size[0] * 9 == size[1] * 16
        assert colors <= 48
        assert all(pixel == (255, 255, 255) for pixel in corners)
        whites = sum(count for count, color in rgb.getcolors(256)
                     if color == (255, 255, 255))
    manifest.append({
        "figure": number,
        "original": str(original),
        "original_sha256": digest(original),
        "final": str(destination.relative_to(ROOT)),
        "final_sha256": digest(destination),
        "width": size[0], "height": size[1], "bytes": len(encoded),
        "quantization_colors": 48, "distinct_rgb_colors": colors,
        "white_corners": True, "exact_white_fraction": whites / (size[0] * size[1]),
    })
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
