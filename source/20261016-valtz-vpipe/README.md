# Valtz research and limited local verification

Official tgo-app-dev/valtz pinned cc02e25140571a18fad103f9cd6cf0190c5e97c1. The supplied shorthand vpipe/valtz resolves through the official Vpipe project link. Related Vpipe history is background, not an existing Valtz article.

No-engine/no-GUI core build, original tests and CLI project roundtrip ran locally. See smoke-result.json, configure.log, tests.log and failure-rerun.log. 192 passed / 1 failed / 17 skipped out of 210. The i8_gemm settings failure was reproduced alone. No upstream modification or production-impact diagnosis, no AI generation or paid calls. Build runtime /tmp/valtz-build-20261016; clone /tmp/valtz-20261016; original fixture /tmp/valtz-smoke-20261016.

Reproduction (after cloning and initializing LMDB):

```sh
cmake -S /path/to/valtz -B /tmp/valtz-review-build -G Ninja -DVALTZ_WITH_VPIPE=OFF -DVALTZ_BUILD_APP=OFF
cmake --build /tmp/valtz-review-build -j4
/tmp/valtz-review-build/tests/valtz_test
/tmp/valtz-review-build/tests/valtz_test --filter upscalers_run_as_settings_have_them
```

Author preview image adopted as cover, with pinned source/crop in research-evidence.json. No generated-performance claim is based on this image. Original saved in requested general media archive. Full raw source remains in the pinned upstream repository, not duplicated here.
