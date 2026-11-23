#!/usr/bin/env bash
set -eu
cd "${1:?pass the pinned AlphaSift checkout}"
test "$(git rev-parse HEAD)" = d38bf412532a085aa48862255e9538249a536061
uv run --python 3.12 --with pytest --with pandas --with pyyaml --with requests python -m pytest tests/test_evaluation_next_open.py tests/test_risk.py tests/test_mcp.py tests/test_scorer.py tests/test_ranker.py -q
