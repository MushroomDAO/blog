#!/bin/sh
set -eu
# Pass a pinned upstream clone; use Python with Pillow and NumPy.
test "$(git -C "$1" rev-parse HEAD)" = "6fecdfd0d6e5a0595f979550e05f4b1fcde550fe"
python3 "$1/tests/check.py"
python3 "$(dirname "$0")/local-smoke.py" "$1"
