#!/usr/bin/env bash
set -euo pipefail
# Use the reviewed repository clone, without modifying the blog workspace.
rsi_repo=${1:?Pass the RSI-Anything checkout path}
rsi_python=${2:?Pass a Python executable with numpy scipy playwright==1.55.0 installed}
rsi_output=${3:?Pass an empty output directory}
mkdir -p "$rsi_output"
[ "$(git -C "$rsi_repo" rev-parse HEAD)" = 2582a0f11495af595d41bab3babec57d2c3fb80e ]
PYTHONPATH="$rsi_repo/src" "$rsi_python" -m unittest discover -s "$rsi_repo/tests" -v > "$rsi_output/workflow-tests.log" 2>&1
"$rsi_python" -m unittest discover -s "$rsi_repo/tasks/reaction_optimization/tests" -v > "$rsi_output/reaction-tests.log" 2>&1
"$rsi_python" "$rsi_repo/tasks/reaction_optimization/scripts/verify_assets.py" > "$rsi_output/reaction-assets.json"
"$rsi_python" "$rsi_repo/tasks/reaction_optimization/infer.py" --observations "$rsi_repo/tasks/reaction_optimization/examples/observations.json" --output "$rsi_output/chemistry-smoke-recommendation.json"
RSI_GUI_ROOT="$rsi_output/browser-run" PYTHONPATH="$rsi_repo/tasks/gui/src" "$rsi_python" -c 'from rsi_anything_gui.smoke import smoke; import json; print(json.dumps(smoke(4),indent=2))' > "$rsi_output/browser-smoke.json"
