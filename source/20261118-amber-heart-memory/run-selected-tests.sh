#!/usr/bin/env bash
set -euo pipefail
repo_dir="${1:?usage: run-selected-tests.sh CHECKOUT PYTHON}"
python_bin="${2:-python3}"
cd "$repo_dir"
"$python_bin" -m unittest -v \
  memory_core.tests.test_config \
  memory_core.tests.test_fixed_models \
  memory_core.tests.test_import_formats \
  memory_core.tests.test_import_stream \
  memory_core.tests.test_recall.RecallUnitTests \
  memory_web.tests.test_deploy_runtime \
  memory_web.tests.test_role_timeouts \
  memory_web.tests.test_extraction_model \
  memory_web.tests.test_usage_receipt \
  memory_core.tests.test_archives.ArchivePolicyTests
