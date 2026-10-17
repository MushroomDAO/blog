#!/bin/bash
set -euo pipefail
: "${D2R_REPO:?Set D2R_REPO to pinned d2r-mobile-build checkout}"
: "${KINEX_REPO:?Set KINEX_REPO to pinned Kinex checkout}"
: "${REVIEW_PYTHON:?Set REVIEW_PYTHON to Python 3.12 with Kinex dependencies}"
(cd "$D2R_REPO" && "$REVIEW_PYTHON" -m unittest discover -s tests -v)
PYTHONPATH="$KINEX_REPO/packages/core/assets/python" "$REVIEW_PYTHON" -m unittest discover -s "$KINEX_REPO/packages/core/test" -p driver_contract.py -v
"$REVIEW_PYTHON" "$(dirname "$0")/recompute-kinex.py"
