"""Copy image_gen originals and make the three requested bounded-size PNGs.

Only writes this directory and the three article illustration destinations.
Existing originals and outputs must match before this script can reuse them.
"""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import shutil
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SLUG = 'ra-jit-blaze-rust-live-builds'
GENERATED = Path('/Users/jason/.codex/generated_images/01a17351-1c94-70a0-bee9-f3eaf926c7ef')
SOURCES = [
    'exec-eb3010ee-c577-4902-b7ae-4a365dca6d23.png',
    'exec-c33f6657-82fb-4179-9cab-4e964a37dc2e.png',
    'exec-151f4f04-7837-4f44-8a14-da73674a327b.png',
]
TOPICS = [
    ('resident-compiler-function-swap', '小M在保持就绪的常驻编译工坊中，只替换房屋的一块函数砖。', ['常驻编译器', '工坊就绪', '只换一个函数']),
    ('separate-timing-boundaries', '小M操作三只独立秒表，分别测量冷启动、热构建和在线应用，不承诺具体速度。', ['冷启动', '热构建', '在线应用', '分开计时']),
    ('stored-data-shape-restart', '小M发现新形状无法装入已有数据占据的模具，选择重启；同形状的函数砖仍可替换。', ['函数可换', '已有数据', '形状变了', '重启']),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = {
    'article_slug': SLUG,
    'generated_on': '2026-10-25',
    'article_context': 'ra-jit renamed blaze on 2026-10-24 (context supplied by user)',
    'generator': 'image_gen.imagegen',
    'generation_calls': 3,
    'skill': '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
    'references_read': ['style-dna.md', 'mushroom-ip.md', 'composition-patterns.md', 'prompt-template.md', 'qa-checklist.md'],
    'compression': 'Near-white RGB pixels with all channels >= 246 become pure white; resize to exact 16:9 with Lanczos; palette quantization without dithering; optimized PNG. Originals unchanged.',
    'byte_limit_exclusive': 90000,
    'assets': [],
}

for i, (filename, (topic, alt, labels)) in enumerate(zip(SOURCES, TOPICS), 1):
    source = GENERATED / filename
    original = HERE / f'fig-{i:02d}-original.png'
    if original.exists():
        assert digest(original) == digest(source), f'Original already differs: {original}'
    else:
        shutil.copy2(source, original)
    with Image.open(original) as opened:
        original_dimensions = list(opened.size)
        rgb = opened.convert('RGB')
    red, green, blue = rgb.split()
    darkest = ImageChops.darker(ImageChops.darker(red, green), blue)
    background_mask = darkest.point(lambda value: 255 if value >= 246 else 0)
    rgb.paste((255, 255, 255), mask=background_mask)
    selected = None
    for width in (1600, 1440, 1280, 1152, 1024):
        height = width * 9 // 16
        resized = rgb.resize((width, height), Image.Resampling.LANCZOS)
        for colors in (128, 96, 64, 48):
            quantized = resized.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            buffer = BytesIO()
            quantized.save(buffer, format='PNG', optimize=True, compress_level=9)
            data = buffer.getvalue()
            if len(data) < 90000:
                selected = (data, width, height, colors)
                break
        if selected:
            break
    assert selected, 'No acceptable PNG size'
    data, width, height, colors = selected
    destination = ROOT / 'src/assets/images' / f'{SLUG}-fig-{i:02d}.png'
    if destination.exists():
        assert destination.read_bytes() == data, f'Refusing to replace differing asset: {destination}'
    else:
        destination.write_bytes(data)
    with Image.open(destination) as check:
        check.load()
        assert check.format == 'PNG'
        assert check.width * 9 == check.height * 16
        assert check.convert('RGB').getpixel((0, 0)) == (255, 255, 255)
    assert destination.stat().st_size < 90000
    entry = {
        'figure': i, 'topic': topic, 'alt_zh': alt, 'labels_zh': labels,
        'original': original.relative_to(ROOT).as_posix(),
        'original_tool_path': str(source), 'original_dimensions': original_dimensions,
        'original_bytes': original.stat().st_size, 'original_sha256': digest(original),
        'prompt': (HERE / f'fig-{i:02d}-prompt.txt').relative_to(ROOT).as_posix(),
        'final': destination.relative_to(ROOT).as_posix(),
        'width': width, 'height': height, 'palette_colors': colors,
        'bytes': destination.stat().st_size, 'sha256': digest(destination),
        'qa': {'original_visually_inspected': True, 'final_visually_inspected': False,
               'png_decodes': True, 'exact_16_9': True, 'under_90000_bytes': True,
               'white_background': True, 'no_numeric_speed_claims': True},
    }
    manifest['assets'].append(entry)
    print(json.dumps({'figure': i, 'path': entry['final'], 'dimensions': [width, height], 'bytes': entry['bytes'], 'colors': colors}))

(HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
