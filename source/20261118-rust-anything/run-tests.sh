#!/usr/bin/env bash
set -euo pipefail
cd "${1:?isolated checkout required}"
cargo test --locked --lib
cargo test --locked --test app python_cli_records_and_replays -- --exact --nocapture
# Full loop test retains an unresolved Ruby build failure on system Ruby 2.6.10.
cargo test --locked --test loop -- --nocapture
