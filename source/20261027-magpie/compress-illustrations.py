#!/usr/bin/env python3
"""Compress the generated originals in supplied provenance manifests; ImageMagick required."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identify(path):
    return subprocess.check_output(['magick', 'identify', '-format', '%w %h', str(path)], text=True).split()


for filename in sys.argv[1:]:
    manifest_path = Path(filename)
    manifest = json.loads(manifest_path.read_text())
    for asset in manifest['assets']:
        original = Path(asset['original_file'])
        output = Path(asset['output_file'])
        # Only replace our own prior output when its recorded hash still matches.
        if output.exists() and asset.get('sha256') != sha256(output):
            raise SystemExit(f'Refusing to replace untracked or changed asset: {output}')
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.stem + '.compressing.png')
        for colors in [64, 48, 32, 24, 16]:
            command = ['magick', str(original), '-resize', '1536x864', '-background', 'white',
                       '-gravity', 'center', '-extent', '1536x864', '-channel', 'RGB',
                       '-white-threshold', '97%', '+channel',
                       '-dither', 'None', '-colors', str(colors), '-strip',
                       '-define', 'png:compression-level=9', 'PNG8:' + str(temporary)]
            subprocess.run(command, check=True)
            if temporary.stat().st_size < 90000:
                break
        else:
            raise SystemExit(f'Could not meet byte limit for {output}')
        assert identify(temporary) == ['1536', '864']
        assert temporary.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
        corners = subprocess.check_output(['magick', str(temporary), '-format',
            '%[pixel:p{0,0}]|%[pixel:p{1535,0}]|%[pixel:p{0,863}]|%[pixel:p{1535,863}]',
            'info:'], text=True)
        assert corners == 'srgb(255,255,255)|srgb(255,255,255)|srgb(255,255,255)|srgb(255,255,255)', corners
        temporary.replace(output)
        asset.update({'original_sha256': sha256(original),
                      'original_dimensions': list(map(int, identify(original))),
                      'sha256': sha256(output), 'bytes': output.stat().st_size,
                      'dimensions': [1536, 864], 'aspect_ratio': '16:9',
                      'palette_colors_limit': colors, 'compression_command': command,
                      'compression_note': 'Palette quantization and resize are lossy; original generated PNG retained. Near-white pixels normalized to white; metadata stripped from delivery PNG.',
                      'prompt_sha256': sha256(asset['prompt_file']),
                      'corner_pixels': corners, 'automated_checks': 'pass'})
        for edit in asset.get('generation_history', []):
            edit['sha256'] = sha256(edit['file'])
        print(f'{output}: {output.stat().st_size} bytes, 1536x864, palette <= {colors}', flush=True)
    manifest['prepared_at_utc'] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
