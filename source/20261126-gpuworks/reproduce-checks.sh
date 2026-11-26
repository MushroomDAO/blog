#!/usr/bin/env bash
set -eu
cd "${1:?pass pinnedGPUWorks checkout}"
test "$(git rev-parse HEAD)" = 696a369621c3b74264013472eae6d6c4f3b92756
GPUWORKS_USAGE_REPORT=off go test -json ./pkg/estimate ./internal/proto ./internal/agent/dgpucache
