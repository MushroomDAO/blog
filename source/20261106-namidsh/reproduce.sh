#!/bin/sh
# Run in isolated clones; no API key required. Pin commits from research-review.json.
set -eu
npm ci --ignore-scripts
npm test
npm run check
node tests/compat.ts > mini.txt
# npm reference is @deepseek-ai/cordis@4.1.0 installed in a separate prefix.
# npm install --prefix /tmp/namidsh-real --ignore-scripts @deepseek-ai/cordis@4.1.0 esbuild
CORDIS=/tmp/namidsh-real/node_modules/@deepseek-ai/cordis/lib/index.js node tests/compat.ts > real.txt
diff -u mini.txt real.txt
# Expected comparison difference: RAN LS versus RAN UNDEFINED, not an identical trace.

# Vendored reference is a separate DSH checkout at fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159.
# Make @deepseek-ai/cosmokit resolvable using the isolated prefix node_modules.
# /tmp/namidsh-real/node_modules/.bin/esbuild /tmp/namidsh-upstream/vendor/cordis/src/index.ts --bundle --platform=node --format=esm --packages=external --outfile=/tmp/namidsh-upstream/vendor/cordis/lib/index.js
# CORDIS=/tmp/namidsh-upstream/vendor/cordis/lib/index.js node tests/compat.ts > vendored.txt
# diff -u mini.txt vendored.txt
