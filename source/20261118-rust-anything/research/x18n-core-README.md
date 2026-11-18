# x18n core, ported with rust-anything

Every function of `packages/core` (x18n v0.1.2) that can move to Rust without changing its
public API, ported, verified and measured with rust-anything. Rust is bridged with wasm-bindgen,
the plan's choice: core must keep running in browsers. Nothing in the x18n repository was changed.

## Result

**Correctness: every port matches the TS original exactly**, on 6,925 recorded cases plus 4,600
shadow-mode calls with zero mismatches. **Performance: as called from JS, the Rust versions are
slower** for nearly every function: the bridge costs more than the work.

| Unit | Ported | Kept in TS | Gate | Cases | Speedup per function (above 1x is faster) |
| --- | ---: | ---: | --- | ---: | --- |
| `fuzzy.ts` ([`../fuzzy-rs`](../fuzzy-rs)) | 1 | 0 | pass | 2000 | fuzzyScore 0.23x (napi: 0.22x) |
| `keys.ts` | 4 | 3 | pass | 1216 | joinKey 0.06x, splitKey 0.03x, isKeyUnder 0.06x, replaceKeyPrefix 0.01x |
| `text.ts` | 4 | 1 | pass | 1112 | diffText 0.01x, applyTextEdits 1.12x, rangeContains 0.46x, hashText 0.82x |
| `message-tree.ts` | 5 | 2 | pass | 748 | isMessageLeaf 0.01x, isMessageTree 0.05x, pathId 0.10x, applyMessageOps 1.15x, buildTree 1.19x |
| `locale.ts` | 3 | 1 | pass | 916 | resolveFallbacks 0.10x, fallbackChain 0.60x, localeSpellingKey 0.23x |
| `schema.ts` | 1 | 1 + schemas | pass | 20 | isJsonObject 0.05x |
| `plugins.ts` | 1 | 2 | pass | 308 | extensionOf 0.26x |
| `contracts.ts` | 1 | 2 | pass | 307 | toWireRange 0.02x |
| `project/` (pure helpers) | 9 | 13 | pass | 1298 | 0.03x to 0.66x |
| **Total** | **29** | **26** | **9/9** | **7925** | |

The few results above 1x are functions whose recorded cases are mostly invalid input: there JS
pays for building exceptions. Large inputs show the same picture (`smoke/bench.mjs`):

| Input | TS | Rust (wasm) |
| --- | ---: | ---: |
| `hashText`, 1.4 MB | 2.0 ms | 2.8 ms |
| `diffText`, 1.4 MB | 5.2 ms | 11.1 ms |
| `suppressedRanges`, 1.9 MB, 20k markers | 3.8 ms | 42.5 ms |
| `joinKey`, 100k calls | 6.3 ms | 65.7 ms |

Where the `suppressedRanges` time goes: copying the 1.9 MB string into wasm memory alone takes
4.4 ms, more than the whole TS function; turning 20k result objects back into JS takes ~25 ms.
V8 runs these string operations on its native UTF-16 strings; a bridge has to copy them.

## What stays in TS, and why

Decided by `rust-anything bridge` from the types, or with `--keep` where types cannot tell:

- **The engine** (`createProject`, `createPlanner`, `createAnalyzer`, `resolveConfig`,
  `createRegistry`, hosts, `define*`): it calls JS plugins and hosts through callbacks; values
  of these types hold functions, which no bridge can carry.
- **Closures and iterators** (`keyMatcher`, `pathMatcher`, `createLineIndex`, `walkLeaves`,
  `sortTree`): they return functions or lazy iterators, or take callbacks.
- **RegExp** (`globToRegExp`): returns a JS RegExp, whose syntax differs from Rust's.
- **Class identity** (`isX18nError`, `toErrorInfo`): `instanceof` checks.
- **Engine data** (`parseLocaleInfo`): `Intl.PluralRules` and `Intl.DisplayNames` use the JS
  engine's CLDR data; a Rust copy would drift from what users see.
- **Library objects** (`validate`, valibot schemas; `envelope`): generic or library-shaped values.

## What the port had to get right

Every one of these was caught by `rust-anything diff` or the port's own tests, not by reading:

- `replaceKeyPrefix` and `diffText` can cut an emoji in half; JS keeps the half (a lone
  surrogate), a Rust `String` cannot. The ports return UTF-16 units where that can happen.
- `splitKey` returns `{ namespace: undefined }`, while message trees hold real `null` leaves.
- `sortReviews` sorts by UTF-16 code units (JS `<`), not by code points (Rust `Ord`).
- `serde_json::Map::remove` with `preserve_order` swaps keys; JS `delete` keeps the order
  (`shift_remove`).
- `valueText(1e21)` is `"1e+21"` in JS; `sourceHash` hashes `JSON.stringify` output byte for byte.
- JS objects put integer-like keys (`"2"`, `"10"`) first.

## Recommendation for x18n

Do not ship these ports into x18n: they are correct but slower. The data says Rust pays off for
x18n only when a whole hot path moves at once, so that one call does a lot of work: for example
scanning every source file and analyzing usages in Rust (the builtins scanners and formats plus
the core analysis), with files read on the Rust side and a coarse `analyzeProject()` boundary.
That is a rewrite of a layer, not a port of functions; it is x18n's maintainers' decision.

## Reproduce

```sh
# each unit: record the TS behavior, then gate (fmt, clippy, tests, build, API, behavior)
rust-anything record keys-rs --inputs keys-rs/inputs.jsonl
rust-anything gate keys-rs
rust-anything bench keys-rs

# x18n has no node_modules here: npm packages core imports come from a scratch folder
rust-anything record schema-rs --inputs schema-rs/inputs.jsonl --resolve-from <dir with valibot, nostics>

# shadow mode across all units
RUST_ANYTHING_MODE=shadow node --experimental-transform-types smoke/shadow-smoke.ts
```
