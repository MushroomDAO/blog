#!/usr/bin/env bash
set -euo pipefail
checkout=${1:?Pass the pinned upstream checkout directory}
cd "$checkout"
outputs=/tmp/lr2021-adsb-native-tests
mkdir -p "$outputs"
cc -std=c11 -Imain tests/check_adsb.c main/adsb.c -lm -o "$outputs/check_adsb"
"$outputs/check_adsb"
cc -std=c11 -Imain tests/test_correction.c main/adsb.c -lm -o "$outputs/test_correction"
"$outputs/test_correction"
cc -std=c11 -Imain tests/check_wifi_policy.c -o "$outputs/check_wifi_policy"
"$outputs/check_wifi_policy"
cc -std=c11 -Imain -Itests/stubs tests/test_stream.c main/trail_cache.c -lm -o "$outputs/test_stream"
"$outputs/test_stream"
python3 tests/test_web_serialization.py cc
node tests/test_connection.cjs
