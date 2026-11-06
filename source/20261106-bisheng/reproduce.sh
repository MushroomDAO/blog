#!/bin/sh
# Run against source commit62f5893912a171265769f004fe79a96cfb009fee in an isolated environment.
set -eu
python3 -m venv /tmp/bisheng-test-venv
/tmp/bisheng-test-venv/bin/pip install pytest httpx PyYAML
cd /tmp/bisheng-research/src/bisheng-cli
PYTHONPATH=. /tmp/bisheng-test-venv/bin/python -m pytest tests/test_ignore.py tests/test_project.py tests/test_secret_warnings.py -q
bash -n /tmp/bisheng-research/docker/install.sh /tmp/bisheng-research/docker/lib/install-env.sh
