#!/usr/bin/env python3
"""Rebuild the three article figures from preserved image_gen originals."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SLUG = "nx2apple-switch-apple-builder"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    results = []
    for number in range(1, 4):
        name = f"{SLUG}-fig-{number:02d}.png"
        original = HERE / "originals" / name
        target = ROOT / "src/assets/images" / name
        attempts = []
        for colors in (256, 128, 96, 64, 48, 32):
            command = [
                "magick", str(original), "-background", "white", "-alpha", "remove",
                "-alpha", "off", "-colorspace", "sRGB", "-resize", "1200x675!",
                "-white-threshold", "93%", "+dither", "-colors", str(colors),
                "-strip", "-define", "png:compression-level=9", "PNG8:" + str(target),
            ]
            subprocess.run(command, check=True)
            attempts.append({"palette_limit": colors, "bytes": target.stat().st_size})
            if target.stat().st_size < 90000:
                break
        data = target.read_bytes()
        width, height, depth, color_type = struct.unpack(">IIBB", data[16:26])
        assert (width, height, depth, color_type) == (1200, 675, 8, 3)
        assert len(data) < 90000, (name, len(data))
        metadata = subprocess.check_output([
            "magick", str(target), "-format", "%k colors", "info:"
        ], text=True)
        rgb = subprocess.check_output(["magick", str(target), "-depth", "8", "RGB:-"])
        white_fraction = sum(rgb[i:i+3] == b"\xff\xff\xff"
                             for i in range(0, len(rgb), 3)) / (width * height)
        assert white_fraction > 0.5
        results.append({
            "figure": number, "original": str(original.relative_to(ROOT)),
            "original_sha256": sha256(original),
            "output": str(target.relative_to(ROOT)), "output_sha256": sha256(target),
            "width": width, "height": height, "bit_depth": depth,
            "png_color_type": color_type, "bytes": len(data),
            "white_threshold": "93%", "dither": False,
            "palette_limit": colors, "attempts": attempts,
            "command": command, "inspection": metadata,
            "pure_white_pixel_fraction": white_fraction,
        })
    (HERE / "compression-report.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
