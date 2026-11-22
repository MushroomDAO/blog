#!/bin/sh
set -eu
# Run inside the upstream clone pinned in research/source-pins.json.
test "$(git rev-parse HEAD)" = "6b1713518eb75f8495415662870f682357372d09"
python3 -m unittest discover -s mac/tests -v
