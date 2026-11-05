#!/usr/bin/env bash
# Reproduce the limited CPU/GGUF check; this does not run QSA inference.
set -euo pipefail
repo=${1:?Pass the inspected engine checkout}
build=${2:?Pass a separate temporary build directory}
cmake -S "$repo" -B "$build" -G Ninja \
  -DGGML_CUDA=OFF -DGGML_METAL=OFF -DGGML_ACCELERATE=OFF \
  -DLLAMA_BUILD_TESTS=ON -DLLAMA_BUILD_EXAMPLES=OFF \
  -DLLAMA_BUILD_SERVER=OFF -DLLAMA_CURL=OFF
cmake --build "$build" --target test-gguf -j4
"$build/bin/test-gguf"
