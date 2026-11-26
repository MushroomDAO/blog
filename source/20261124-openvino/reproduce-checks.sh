#!/usr/bin/env bash
set -eu
cd "${1:-/Users/jason/Dev/mycelium/blog}"
uv run --no-project --python 3.12 --with openvino==2026.4.1 --with onnx==1.23.2 --with numpy==2.5.5 python source/20261124-openvino/smoke.py
