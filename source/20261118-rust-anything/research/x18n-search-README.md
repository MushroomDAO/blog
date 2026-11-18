# x18n search in Rust

x18n's sidebar search (`fuzzyScore` from `packages/core/src/fuzzy.ts` over every key, then
filter and sort) moved to Rust as a batch, with the keys kept on the Rust side.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/search.ts .   # fuzzyScore: ~25%, per key
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
# port fuzzyScore, then add FuzzyScoreIndex to src/port.rs
rust-anything gate .                                   # 2000/2000 recorded cases match
rust-anything build . && node --experimental-strip-types bench.ts ../x18n
```

- `src/port.rs`: `fuzzy_score`, the port, and `FuzzyScoreIndex`: keys lowercased once (UTF-16,
  plus bytes for ASCII keys), a mask of the code units in each key, each key's first position of
  every common character, and the last query's matches. Its `rank` narrows to those matches when
  the query grows, reads one-letter queries from the first positions, and orders scores with a
  counting sort. Unit tests check it against `fuzzy_score` over every key.
- `src/lib.rs` (generated): `FuzzyScoreBatch` with `run(query)` (every score, a `Float64Array`)
  and `rank(query, min)` (indexes of scores >= `min`, best first, a `Uint32Array`).
- `search.ts`: the workload `profile` ran: the TS search, 14 queries, three times each.
- `bench.ts`: checks the results are identical to the TS pipeline (and to TS with the same
  narrowing), then times all three.

On 4 cores: TS 10 ms per query, TS with the same narrowing 4-5 ms, Rust 0.45-0.56 ms: **18-22x
faster than TS**, 7-12x faster than narrowed TS. With wasm (one thread), 11.5x.
