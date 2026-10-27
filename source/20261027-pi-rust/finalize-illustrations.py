"""Rebuild the three PNG deliverables from their untouched image_gen originals."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GENERATED = Path('/Users/jason/.codex/generated_images/01a17c66-ee66-7d82-85b6-81426da3abbb')
ORIGINALS = [
    GENERATED / 'exec-59413cf8-67ab-4765-a041-255d659b6eea.png',
    GENERATED / 'exec-73000b5f-1c43-41bf-9ed0-edd924065082.png',
    GENERATED / 'exec-598665a4-a4b6-4c20-a49b-eeb039baf30e.png',
]
PURPOSES = [
    'One agent engine shared by terminal and embedded application; composable tools and model connector.',
    'Durable session checkpoints restore interrupted work; external tool side effects require a separate checklist, with no universal exactly-once claim.',
    'Native plugin and agent share a host and workspace; a thin remote terminal uses a secure tunnel. No sandbox shield.',
]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records = []
for number, original in enumerate(ORIGINALS, 1):
    destination = ROOT / f'src/assets/images/pi-rust-agent-runtime-fig-{number:02}.png'
    prompt = HERE / f'fig-{number:02}-prompt.txt'
    for colors in (64, 48, 32, 24, 16):
        subprocess.run([
            'magick', str(original), '-background', 'white', '-alpha', 'remove',
            '-alpha', 'off', '-resize', '1280x720', '-gravity', 'center',
            '-extent', '1280x720', '-channel', 'RGB', '-fx',
            'min(r,min(g,b))>.97 && max(r,max(g,b))-min(r,min(g,b))<.008 ? 1 : u',
            '+channel', '+dither',
            '-colors', str(colors), '-strip', '-define', 'png:compression-level=9',
            '-define', 'png:compression-filter=5', f'PNG8:{destination}',
        ], check=True)
        if destination.stat().st_size < 90000:
            break
    dimensions = subprocess.check_output([
        'magick', 'identify', '-format', '%w %h', str(destination)
    ], text=True).split()
    assert dimensions == ['1280', '720'], dimensions
    assert destination.stat().st_size < 90000
    records.append({
        'figure': number, 'purpose': PURPOSES[number - 1],
        'original_path': str(original), 'original_sha256': sha256(original),
        'prompt': str(prompt.relative_to(ROOT)), 'prompt_sha256': sha256(prompt),
        'final_path': str(destination.relative_to(ROOT)),
        'final_sha256': sha256(destination), 'bytes': destination.stat().st_size,
        'width': 1280, 'height': 720, 'palette_max_colors': colors,
    })

manifest = {
    'date': '2026-10-27', 'generator': 'built-in image_gen.imagegen',
    'model': 'Tool did not expose model identity.',
    'generation_calls': 3, 'separate_images': True, 'reference_images': [],
    'skill': '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
    'source_of_concepts': 'User-provided figure specifications; no external factual research added.',
    'processing': 'ImageMagick: fit and white-pad to 1280x720, whiten only nearly neutral highlights (all channels >97%, channel spread <0.8%) while retaining cream tint, non-dithered indexed PNG, metadata stripped. No semantic content editing.',
    'originals': 'Retained untouched at image_gen default paths.',
    'figures': records,
}
(HERE / 'illustrations-provenance.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
)
for record in records:
    print(f"{record['final_path']}: {record['width']}x{record['height']}, {record['bytes']} bytes")
