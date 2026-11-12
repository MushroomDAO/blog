"""Reproduce only the three requested HiRoute illustration assets."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN_DIR = Path('/Users/jason/.codex/generated_images/01a185d1-9489-7772-afb6-f707726c8b45')
GENERATED = [
    'exec-e2615e85-86b8-4015-b3c0-17919c662809.png',
    'exec-b211d35f-3b96-4d97-8665-cc06a53c15de.png',
    'exec-84f8a9ca-9d9c-42bb-a296-285d771cf807.png',
]
ANCHORS = [
    'New user task selects model; valid tool continuation retains selection.',
    'Same-category bounded candidate failover; exhaustion explicitly errors; primary never downgrades.',
    'Total cost includes execution, judgment, cache misses and rework.',
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


records = []
for index, (generated_name, anchor) in enumerate(zip(GENERATED, ANCHORS), 1):
    stem = f'fig-{index:02}'
    original = HERE / 'originals' / f'{stem}.png'
    if not original.exists():
        shutil.copy2(GEN_DIR / generated_name, original)
    output = ROOT / 'src/assets/images' / f'hiroute-local-model-routing-{stem}.png'
    command = [
        'magick', str(original), '-background', 'white', '-alpha', 'remove',
        '-alpha', 'off', '-resize', '1200x675!', '-white-threshold', '93%',
        '+dither', '-colors', '96', '-depth', '8', '-strip',
        '-define', 'png:compression-level=9', f'PNG8:{output}',
    ]
    subprocess.run(command, check=True)
    with Image.open(output) as img:
        assert img.size == (1200, 675), img.size
        assert img.mode == 'P', img.mode
        colors = len(img.getcolors())
        rgb = img.convert('RGB')
        assert all(rgb.getpixel(p) == (255, 255, 255) for p in [
            (0, 0), (1199, 0), (0, 674), (1199, 674),
        ])
        white_fraction = sum(n for n, color in rgb.getcolors(810001)
                             if color == (255, 255, 255)) / (1200 * 675)
    size = output.stat().st_size
    assert size < 90000, (output, size)
    record = {
        'figure': index, 'anchor': anchor,
        'tool': 'image_gen.imagegen (built-in)',
        'generation_mode': 'three separate standalone generations; one call per image',
        'generated_source_path': str(GEN_DIR / generated_name),
        'original': str(original.relative_to(ROOT)),
        'original_sha256': sha256(original),
        'prompt': str((HERE / 'prompts' / f'{stem}.txt').relative_to(ROOT)),
        'prompt_sha256': sha256(HERE / 'prompts' / f'{stem}.txt'),
        'output': str(output.relative_to(ROOT)),
        'output_sha256': sha256(output), 'bytes': size,
        'dimensions': [1200, 675], 'png_color_type': 3, 'bit_depth': 8,
        'palette_colors': colors, 'white_threshold': '93%', 'dither': False,
        'exact_white_pixel_fraction': round(white_fraction, 6),
        'compression_command': command,
        'visual_review': 'Chinese labels correct; XiaoM participates in core action; abundant white space; anchor preserved.',
    }
    records.append(record)
    print(json.dumps({k: record[k] for k in [
        'output', 'bytes', 'dimensions', 'palette_colors', 'exact_white_pixel_fraction'
    ]}))

manifest = {
    'created_at': datetime.now(timezone.utc).isoformat(),
    'skill': '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
    'article_read': 'src/content/blog/hiroute-local-model-routing.md',
    'reference_files': ['style-dna.md', 'mushroom-ip.md', 'composition-patterns.md',
                        'prompt-template.md', 'qa-checklist.md'],
    'postprocessing': 'User-authorized ImageMagick resize, white threshold, palette compression. No generative content edits.',
    'images': records,
}
(HERE / 'provenance.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
