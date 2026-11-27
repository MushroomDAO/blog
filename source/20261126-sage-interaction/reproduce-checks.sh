#!/bin/sh
set -eu
repo=${1:?Pass the path to a clone of InternLM/Sage-Interaction}
expected=d3bc2703e0e7f4ec357fc3c73153dd9e9332f9d3
actual=$(git -C "$repo" rev-parse HEAD)
[ "$actual" = "$expected" ] || { echo "Wrong source revision" >&2; exit 1; }
python3 source/20261126-sage-interaction/check-protocol.py "$repo"
