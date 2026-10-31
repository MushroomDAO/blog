#!/usr/bin/env bash
set -euo pipefail
# Run inside a disposable checkout of the pinned repository; PNG tools need only Node >=18.
git rev-parse HEAD
node tools/check.mjs
node tools/render.mjs ice/frost-nova melee/sword-slash fire/torch --sheet
node --input-type=module - <<'JS'
import {allIds,loadEffect} from './tools/lib/fxlib.mjs';
import {PAL} from './src/core/index.js';
const ids=allIds();const categories={};let pure=0,simulated=0;
for(const id of ids){const c=id.split('/')[0];categories[c]=(categories[c]??0)+1;const f=await loadEffect(id);if(f.mod.create)simulated++;else pure++;}
console.log(JSON.stringify({effects:ids.length,categories,palettes:Object.keys(PAL),pure,simulated},null,2));
JS
