"""Archive three generated originals and prepare the requested small PNGs.

Usage: python3 prepare-assets.py ORIGINAL_01 ORIGINAL_02 ORIGINAL_03
"""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import shutil
import sys
from PIL import Image, ImageOps, ImageChops, __version__ as pillow_version

archive = Path(__file__).resolve().parent
root = archive.parents[2]
assert len(sys.argv) == 4, 'Provide exactly three original image paths'
entries = []
anchors = [
    'Investigate existing code, make a small change, drive the application, save verified context',
    'One agent defines task boundaries, workers edit isolated worktrees, reunite for verification',
    'A passing build is one checkpoint; real user action and visible result demonstrate behavior',
]
for index, original_arg in enumerate(sys.argv[1:], 1):
    original = Path(original_arg).resolve()
    archived = archive / 'originals' / f'fig-{index:02d}.png'
    if archived.exists():
        assert archived.read_bytes() == original.read_bytes(), 'Refusing to replace another original'
    else:
        shutil.copy2(original, archived)
    source = Image.open(archived)
    source.load()
    source_rgb = Image.new('RGB', source.size, 'white')
    if 'A' in source.getbands():
        source_rgb.paste(source.convert('RGB'), mask=source.getchannel('A'))
    else:
        source_rgb.paste(source.convert('RGB'))
    # Generated near-white background pixels otherwise retain noisy palette indices.
    red, green, blue = source_rgb.split()
    lightest_background = ImageChops.darker(ImageChops.darker(red, green), blue)
    white_mask = lightest_background.point(lambda value: 255 if value >= 245 else 0)
    source_rgb.paste((255, 255, 255), mask=white_mask)
    target = root / 'src/assets/images' / f'pstack-engineering-workflow-fig-{index:02d}.png'
    assert not target.exists(), f'Refusing to replace existing asset: {target}'
    chosen = None
    for width in (1536, 1280, 1152, 1024, 960):
        height = width * 9 // 16
        canvas = ImageOps.pad(source_rgb, (width, height), method=Image.Resampling.LANCZOS, color='white')
        for colors in (128, 96, 64, 48, 32):
            reduced = canvas.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            palette = reduced.getpalette()
            # Keep the white background exactly white after palette compression.
            for offset in range(0, len(palette), 3):
                if min(palette[offset:offset + 3]) >= 248:
                    palette[offset:offset + 3] = [255, 255, 255]
            reduced.putpalette(palette)
            buffer = BytesIO()
            reduced.save(buffer, format='PNG', optimize=True, compress_level=9)
            if len(buffer.getvalue()) < 90000:
                chosen = (buffer.getvalue(), width, height, colors)
                break
        if chosen:
            break
    assert chosen is not None, 'Unable to meet the PNG byte limit'
    data, width, height, colors = chosen
    target.write_bytes(data)
    with Image.open(target) as final:
        final.load()
        assert final.format == 'PNG'
        assert final.width * 9 == final.height * 16
        rgb = final.convert('RGB')
        corners = [rgb.getpixel(point) for point in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))]
        assert all(pixel == (255, 255, 255) for pixel in corners), corners
        white_count = sum(count for count, pixel in rgb.getcolors(width * height) if pixel == (255, 255, 255))
    entry = {
        'figure': index,
        'anchor': anchors[index - 1],
        'prompt': str((archive / 'prompts' / f'fig-{index:02d}.txt').relative_to(root)),
        'generated_source': str(original),
        'archived_original': str(archived.relative_to(root)),
        'original_bytes': archived.stat().st_size,
        'original_sha256': sha256(archived.read_bytes()).hexdigest(),
        'original_dimensions': list(source.size),
        'final': str(target.relative_to(root)),
        'final_bytes': len(data),
        'final_sha256': sha256(data).hexdigest(),
        'final_dimensions': [width, height],
        'palette_colors': colors,
        'pure_white_fraction': round(white_count / (width * height), 4),
        'checks': {'png': True, 'exact_16_9': True, 'under_90000_bytes': True, 'white_corners': True},
    }
    entries.append(entry)
    print(json.dumps(entry, ensure_ascii=False))
manifest = {
    'article_slug': 'pstack-engineering-workflow',
    'created_at': datetime.now(timezone.utc).isoformat(),
    'generator': 'built-in image_gen.imagegen; one independent call per figure',
    'skill': '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
    'character': 'Current XiaoM: red cap, white spots, cream stem, black dot eyes, thin limbs, deadpan',
    'figure_count': len(entries),
    'processing': f'Pillow {pillow_version}; normalize near-white pixels (all RGB channels >=245) to white, fit without cropping, palette PNG with no dithering, near-white palette entries normalized to pure white',
    'figures': entries,
    'visual_review': 'Pending final visual review',
}
(archive / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
