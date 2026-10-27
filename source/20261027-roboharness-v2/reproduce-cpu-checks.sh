#!/bin/sh
# Usage: sh reproduce-cpu-checks.sh /absolute/path/to/pinned/RoboHarness /absolute/path/to/python
set -eu
cd "$1/harness/v2/R1_pro"
PYTHONPATH=. "$2" -m pytest .dev/tests/test_protocol.py .dev/tests/test_receipt.py .dev/tests/test_gpu_assignment.py -q
