#!/usr/bin/env bash
set -euo pipefail
# Run within a disposable LGUI checkout; Node>=24 and Chrome/Edge required.
[ "$(git rev-parse HEAD)" = '6b448511409861bdea68c5958e09b220a8d8ccfa' ]
node plugin/tools/lgui.mjs doctor --json
npm run check
node scripts/sync-examples.mjs
node --test --test-concurrency=1 --test-timeout=120000 'tests/unit/**/*.test.mjs' 'tests/check/**/*.test.mjs' tests/e2e/inventory.test.mjs
cd examples/inventory
node ../../plugin/tools/lgui.mjs check --json
node ../../plugin/tools/lgui.mjs test --json
node ../../plugin/tools/lgui.mjs verify --view BagView --json
