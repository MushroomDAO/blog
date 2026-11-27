#!/bin/sh
set -eu
repo=${1:?Pass pinned clone of ValueMoonLab/qora-voca-zh}
[ "$(git -C "$repo" rev-parse HEAD)" = 63390ae6cd376c2f725f164191ad902b12db163f ]
PYTHONPATH="$repo/src" python -m pytest "$repo/tests" -q
python source/20261127-qora-voca/smoke.py "$repo" "${2:-/tmp/qora-voca-reproduced}"
