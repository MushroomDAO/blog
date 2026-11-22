#!/usr/bin/env bash
set -euo pipefail
# Requires Git, Python3, Node22+, Chrome, ffmpeg and ffprobe. Runs upstream tests in a temporary checkout.
check_script="$(cd "$(dirname "$0")" && pwd)/verify-determinism.py"
work=$(mktemp -d "${TMPDIR:-/tmp}/cinecode-check.XXXXXX")
git clone --depth 1 https://github.com/sarpstar/cinecode.git "$work/upstream"
git -C "$work/upstream" fetch origin c8a3e7552699360a2b0142c9620882af2069eedb
git -C "$work/upstream" checkout --detach c8a3e7552699360a2b0142c9620882af2069eedb
export CINECODE_SPARKS="$work/sparks.json"
cd "$work/upstream"
python3 -m unittest discover -s tests -v
cd tests
CINECODE_BROWSER_TESTS=1 python3 -m unittest -v test_capture.Browser.test_resume_and_fresh test_capture.Browser.test_changed_image_with_preserved_date_and_size test_capture.Browser.test_a_page_that_throws_while_loading_fails_fast_with_its_error test_capture.Browser.test_multi_worker_video_contains_every_frame

python3 "$check_script" "$work/upstream"
