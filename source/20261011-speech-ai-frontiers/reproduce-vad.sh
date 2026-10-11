#!/bin/bash
# macOS-only component probe; requires uv, ffmpeg and the built-in say command.
# This generates synthetic speech; it does not capture a microphone or clone a person.
set -euo pipefail
cd "$(dirname "$0")"
uv venv .vad-venv --python 3.12
uv pip install --python .vad-venv/bin/python numpy==2.5.4 onnxruntime==1.31.0
.vad-venv/bin/python - <<'PY'
from pathlib import Path
import urllib.request,hashlib
url='https://raw.githubusercontent.com/snakers4/silero-vad/1e261b036686cd0017d500ee96acd1c4ba572a9d/src/silero_vad/data/silero_vad.onnx'
b=urllib.request.urlopen(url,timeout=60).read()
assert hashlib.sha256(b).hexdigest()=='1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3'
Path('silero-vad.onnx').write_bytes(b)
PY
say -o fixture.aiff 'Please stop speaking. I would like to change the appointment to tomorrow morning. Can you hear me while you are talking?'
ffmpeg -v error -y -i fixture.aiff -ar 16000 -ac 1 -c:a pcm_s16le fixture.wav
.vad-venv/bin/python vad-smoke.py
