"""Copy original tool outputs, compress the three approved figures, and record provenance."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SLUG = "apex-35b-v1-local-research-model"
ARTICLE = ROOT / "src/content/blog" / f"{SLUG}.md"
ARTICLE_SHA256_WHEN_READ = "272d01ba13ba7ee95d39ad40623da8f163f754afd60a8f349fe1860c77ba1e6e"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

article_before = digest(ARTICLE)
banner = ROOT / "src/assets/images" / f"{SLUG}-banner.jpg"
banner_before = digest(banner) if banner.exists() else None
previous_path = BASE / "illustration-provenance.json"
previous = json.loads(previous_path.read_text()) if previous_path.exists() else {"figures": []}
previous_hashes = {row["final"]: row["final_sha256"] for row in previous["figures"]}
records = []
for row in json.loads((BASE / "generation-results.json").read_text()):
    number = row["figure"]
    source = Path(row["path"])
    original = BASE / f"fig-{number:02d}-original.png"
    if original.exists():
        assert digest(original) == digest(source)
    else:
        shutil.copy2(source, original)
    destination = ROOT / "src/assets/images" / f"{SLUG}-fig-{number:02d}.png"
    processed = BASE / f"fig-{number:02d}-png8.png"
    commands = []
    for colors in (256, 128, 96, 64):
        command = [
            "magick", str(original), "-background", "white", "-alpha", "remove",
            "-alpha", "off", "-resize", "1200x675!", "-channel", "RGB",
            "-white-threshold", "93%", "+channel",
            "-dither", "None", "-colors", str(colors), "-strip",
            "-define", "png:compression-level=9", f"PNG8:{processed}",
        ]
        subprocess.run(command, check=True)
        commands.append(command)
        if processed.stat().st_size < 90000:
            break
    assert processed.stat().st_size < 90000
    with Image.open(processed) as image:
        assert image.size == (1200, 675)
        assert image.mode == "P"
        rgb = image.convert("RGB")
        assert all(rgb.getpixel(point) == (255, 255, 255)
                   for point in ((0, 0), (1199, 0), (0, 674), (1199, 674)))
        white_pixels = sum(count for count, color in rgb.getcolors(1200 * 675)
                           if color == (255, 255, 255))
        dimensions = list(image.size)
    assert processed.read_bytes()[25] == 3, "PNG must use indexed palette"
    if destination.exists():
        current_hash = digest(destination)
        assert current_hash in (digest(processed), previous_hashes.get(str(destination.relative_to(ROOT)))), "Refuse to overwrite an unrelated asset"
    shutil.copy2(processed, destination)
    assert digest(destination) == digest(processed)
    records.append({
        "figure": number,
        "generation_tool": "image_gen.imagegen (built-in)",
        "generated_path": str(source),
        "original": str(original.relative_to(ROOT)),
        "original_sha256": digest(original),
        "final": str(destination.relative_to(ROOT)),
        "final_sha256": digest(destination),
        "bytes": destination.stat().st_size,
        "dimensions": dimensions,
        "format": "PNG8 indexed palette",
        "palette_color_limit": colors,
        "white_threshold": "93%",
        "white_threshold_channels": "RGB independently, preserving the cream stem's lower blue channel",
        "dither": "None",
        "pure_white_fraction": round(white_pixels / (1200 * 675), 6),
        "commands": commands,
        "visual_qa": "Checked the generated output: correct Chinese labels, red cap with white dots, cream stem, active XiaoM, sparse white scene; distinct feedback loops in fig-02; four memory components in fig-03.",
    })

article_after = digest(ARTICLE)
banner_after = digest(banner) if banner.exists() else None
provenance = {
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "article": str(ARTICLE.relative_to(ROOT)),
    "article_sha256_when_read": ARTICLE_SHA256_WHEN_READ,
    "article_sha256_before_processing": article_before,
    "article_sha256_after_processing": article_after,
    "banner_sha256_before_processing": banner_before,
    "banner_sha256_after_processing": banner_after,
    "concurrent_workspace_note": "Other workers may update articles and banners. This script never writes either; hashes record observed versions without reverting concurrent work.",
    "prompt_file": "illustration-prompts.json",
    "generation_receipts": "generation-results.json",
    "original_metadata": "Original generated PNG files copied byte-for-byte, preserving embedded provenance metadata. Compressed deliverables strip metadata; hashes link them here.",
    "scope": "Exactly three separate generated images. Only the task source directory and three specified figure destinations written. No article/banner edits, build, or publishing.",
    "figures": records,
}
(BASE / "illustration-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
print(json.dumps([{k: record[k] for k in ("figure", "final", "bytes", "dimensions", "pure_white_fraction")} for record in records], indent=2))
