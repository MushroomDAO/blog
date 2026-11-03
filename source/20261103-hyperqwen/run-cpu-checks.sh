#!/usr/bin/env bash
# Run upstream CPU behavior checks without installing dependencies or loading weights.
set -euo pipefail
cd "${1:?usage: run-cpu-checks.sh /path/to/pinned/HyperQwen}"
python3 -m unittest discover -s bench -p test_quality_battery.py
python3 bench/test_prepare_state.py
python3 bench/test_conc_ladder_salt.py
bash bench/test_no_key_bind.sh
