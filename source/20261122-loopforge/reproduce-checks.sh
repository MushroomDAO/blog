#!/bin/sh
# In a clean clone pinned to eb2e368f14d004e6a22ee25940f5a03c0b5d9f38.
# No installer, credentials or server startup. Dependencies may download on first Go run.
set -eu
go test ./internal/engine -run 'Test.*(Graph|Gate|Retry|Rerun|Dependency|Ready)' -count=1 -json
node --test e2e/unit/flow-designer.test.mjs
