#!/bin/sh
# Run from source/20261122-raea/research after extracting the pinned official Mac archive.
# RAEA names its bin/raea executable. No installer, skill changes, server or cloud key required.
set -eu
: "${RAEA:?Set RAEA to the extracted bin/raea executable}"
export RAEA_OFFLINE=1 RAEA_ENV_FILE=/dev/null RAEA_AUDIO_AUTOSETUP=0
mkdir -p smoke-output
"$RAEA" render hello.tsx -o smoke-output/hello.mp4
ffprobe -v error -count_frames -show_entries stream=width,height,nb_read_frames,r_frame_rate -of json smoke-output/hello.mp4
"$RAEA" check hello.tsx --quick -o smoke-output/good.json
set +e
"$RAEA" check bad.tsx --quick -o smoke-output/bad.json
bad_exit=$?
set -e
[ "$bad_exit" -eq 1 ]
"$RAEA" play input.tsx --offscreen --seconds 2 --size 640x480 --input-script keys.json --snapshot 1 smoke-output/play.png --json smoke-output/play.json
"$RAEA" render input.tsx --input render-keys.json --frame 30 -o smoke-output/input30.png
# The original sparse keys.json caused render to throw. The original unmodified archive
# also refused export-game because bin/raea-game was absent. Those failures are archived.
