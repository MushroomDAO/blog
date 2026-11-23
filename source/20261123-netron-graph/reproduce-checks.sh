#!/bin/sh
set -eu
test "$(git -C "$1" rev-parse HEAD)" = "7a60f26aaabcc8f723de4ad3e5e6134eb92fa5f9"
python3 "$(dirname "$0")/local-checks.py" "$1"
