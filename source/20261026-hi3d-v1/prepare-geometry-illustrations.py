"""Compress the three built-in image_gen outputs and record provenance."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent
RAW = Path('/Users/jason/.codex/generated_images/01a178f1-10ed-7eb3-a337-28bcc9eeea3e')
NAMES = [
    'exec-bdd1c99d-a810-4e65-98aa-87b0d0140410.png',
    'exec-742b880c-8df6-4f75-8d9e-7d27657bece8.png',
    'exec-50b11784-5641-4862-9780-1cbd25893296.png',
]
MEANINGS = [
    'Existing coarse mesh plus matching teapot reference image enter a refinement station; finer geometry exits.',
    'XiaoM climbs three mesh steps with increasing geometric subdivision, labeled 512, 1024, 1536 only.',
    'Manual workshop inspection of geometry, scale, topology and license before export; no automatic game-ready claim.',
]

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    targets = [ROOT / f'src/assets/images/hi3d-v1-geometry-refinement-fig-{i:02d}.png' for i in range(1, 4)]
    manifest_path = SOURCE / 'geometry-refinement-illustrations-provenance.json'
    prior = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'images': []}
    prior_hashes = {item['final_path']: item['final_sha256'] for item in prior['images']}
    for target in targets:
        if target.exists():
            assert prior_hashes.get(str(target.relative_to(ROOT))) == digest(target), 'Refusing to overwrite an externally changed illustration.'
    manifest = {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'generation_tool': 'image_gen.imagegen',
        'mode': 'built-in',
        'model': 'Not exposed by the built-in image generation tool',
        'generation_calls': 3,
        'separate_images': True,
        'reference_images_supplied': False,
        'skill': '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
        'postprocessing': 'ImageMagick: fit and center-pad to 1280x720; flood-fill connected near-white background (3.5% fuzz) from all four corners; no-dither palette compression; restore near-white palette entries (1% fuzz) to pure white, preserving cream stem fill. No semantic edits.',
        'visual_review': {
            'reviewer': 'Codex visual inspection of all three built-in outputs',
            'character': 'Red cap, white spots, cream stem, black dot eyes; actively participates in each scene.',
            'claims': 'Geometry refinement only; existing mesh and image inputs shown; no texture improvement or automatic game-ready claim.',
            'labels': 'Only image 2 has readable text: 512, 1024, 1536.',
        },
        'images': [],
    }
    with tempfile.TemporaryDirectory(prefix='hi3d-geometry-') as temp:
        for i, (raw_name, target, meaning) in enumerate(zip(NAMES, targets, MEANINGS), 1):
            raw = RAW / raw_name
            candidate = Path(temp) / target.name
            for colors in (96, 64, 48, 32):
                subprocess.run([
                    'magick', str(raw), '-background', 'white', '-alpha', 'remove',
                    '-resize', '1280x720', '-gravity', 'center', '-extent', '1280x720',
                    '-fuzz', '3.5%', '-fill', 'white', '-draw', 'color 0,0 floodfill color 1279,0 floodfill color 0,719 floodfill color 1279,719 floodfill',
                    '+dither', '-colors', str(colors), '-fuzz', '1%', '-fill', 'white', '-opaque', 'white', '-strip',
                    '-define', 'png:compression-level=9', f'PNG8:{candidate}',
                ], check=True)
                if candidate.stat().st_size < 90000:
                    break
            assert candidate.stat().st_size < 90000
            with Image.open(candidate) as image:
                assert image.format == 'PNG' and image.size == (1280, 720)
                rgb = image.convert('RGB')
                assert all(rgb.getpixel(p) == (255, 255, 255) for p in [(0, 0), (1279, 0), (0, 719), (1279, 719)])
            target.write_bytes(candidate.read_bytes())
            prompt = SOURCE / f'geometry-refinement-fig-{i:02d}-prompt.txt'
            record = {
                'figure': i,
                'meaning': meaning,
                'original_path': str(raw),
                'original_sha256': digest(raw),
                'original_bytes': raw.stat().st_size,
                'original_preserved': True,
                'prompt_path': str(prompt.relative_to(ROOT)),
                'prompt_sha256': digest(prompt),
                'final_path': str(target.relative_to(ROOT)),
                'final_sha256': digest(target),
                'bytes': target.stat().st_size,
                'width': 1280,
                'height': 720,
                'aspect_ratio': '16:9',
                'palette_colors_limit': colors,
                'background': '#FFFFFF',
            }
            manifest['images'].append(record)
            print(json.dumps(record))
    path = SOURCE / 'geometry-refinement-illustrations-provenance.json'
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
