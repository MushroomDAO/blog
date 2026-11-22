#!/usr/bin/env bash
set -euo pipefail
# Requires Bun, Git and a network connection. No global installation or agent config edits.
work=$(mktemp -d "${TMPDIR:-/tmp}/plannotator-check.XXXXXX")
git clone --depth 1 https://github.com/backnotprop/plannotator.git "$work/upstream"
git -C "$work/upstream" fetch origin 7eece56c28d1f03da7c8c6a875d78af0592f6ed0
git -C "$work/upstream" checkout --detach 7eece56c28d1f03da7c8c6a875d78af0592f6ed0
mkdir -p "$work/slice/packages/core" "$work/slice/packages/shared"
for name in annotation-threads feedback-templates; do
  cp "$work/upstream/packages/core/$name.ts" "$work/upstream/packages/core/$name.test.ts" "$work/slice/packages/core/"
done
cp "$work/upstream/packages/shared/request-origin.ts" "$work/upstream/packages/shared/request-origin.test.ts" "$work/slice/packages/shared/"
cp "$(dirname "$0")/http-check.ts" "$work/slice/"
cd "$work/slice"
bun test packages/core/annotation-threads.test.ts packages/core/feedback-templates.test.ts packages/shared/request-origin.test.ts
bun http-check.ts
