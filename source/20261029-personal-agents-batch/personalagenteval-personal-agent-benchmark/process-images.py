"""Preserve the three image_gen originals and reproduce the requested PNG8 assets."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SLUG = "personalagenteval-personal-agent-benchmark"
GENERATED = Path("/Users/jason/.codex/generated_images/01a185d1-9149-7d23-88a1-c4c0e7d2edb5")
SOURCES = [
    "exec-ddb5a11a-ec79-4a25-9785-0aa86ddaec63.png",
    "exec-671ef3fc-20db-4b51-baf3-1adc065c4f8f.png",
    "exec-f05c3b32-485b-43c6-94b7-79dbe635428d.png",
]
ANCHORS = [
    "Inspect personal history before reservation",
    "Distinguish total pool (265) from shared comparison tasks (152)",
    "Turn an observed failure into a repeatable regression test",
]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records = []
for number, (filename, anchor) in enumerate(zip(SOURCES, ANCHORS), 1):
    original = HERE / "originals" / f"fig-{number:02d}-original.png"
    original.parent.mkdir(exist_ok=True)
    if not original.exists():
        shutil.copy2(GENERATED / filename, original)
    target = ROOT / "src/assets/images" / f"{SLUG}-fig-{number:02d}.png"
    command = [
        "magick", str(original), "-background", "white", "-alpha", "remove",
        "-alpha", "off", "-resize", "1200x675!", "-white-threshold", "93%",
        "+dither", "-colors", "64", "-depth", "8", "-strip",
        "-define", "png:compression-level=9", "PNG8:" + str(target),
    ]
    subprocess.run(command, check=True)
    data = target.read_bytes()
    width, height, depth, color_type = struct.unpack(">IIBB", data[16:26])
    assert (width, height) == (1200, 675)
    assert depth == 8 and color_type == 3, "Must be indexed PNG8"
    assert len(data) < 90000, "Must be below 90000 bytes"
    records.append({
        "figure": number,
        "anchor": anchor,
        "tool": "image_gen.imagegen",
        "generation_mode": "one standalone generation call per figure; no reference images",
        "generated_source": str(GENERATED / filename),
        "preserved_original": str(original.relative_to(ROOT)),
        "original_sha256": sha256(original),
        "final": str(target.relative_to(ROOT)),
        "final_sha256": sha256(target),
        "bytes": len(data),
        "width": width,
        "height": height,
        "bit_depth": depth,
        "png_color_type": color_type,
        "white_threshold": "93%",
        "dither": False,
        "maximum_palette_colors": 64,
        "processing_command": command,
        "visual_review": "Chinese labels and anchor meaning checked; XiaoM performs the central action; abundant white space.",
    })
provenance = {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "article": "src/content/blog/" + SLUG + ".md",
    "prompts": "prompts.json",
    "generator": "Built-in image_gen.imagegen; underlying model not reported by tool",
    "compression_version": subprocess.check_output(["magick", "-version"], text=True).splitlines()[0],
    "scope": "Exactly three independent assets; no article/banner edits, build or publishing",
    "figures": records,
}
(HERE / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
for record in records:
    print(f'{record["final"]}: {record["width"]}x{record["height"]}, PNG8, {record["bytes"]} bytes')
