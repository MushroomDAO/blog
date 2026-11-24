#!/usr/bin/env bash
set -eu
cd "${1:?pass pinned repository checkout}"
test "$(git rev-parse HEAD)" = b33313ba0e507dcbf2ed117b86155c6afb25e99e
export PYTHONPATH=.:engine
for f in test_scope_import.py test_triage.py test_report_sections.py test_recon_domain_boundary.py test_secret_scan_skip_dirs.py; do
 python3 -m unittest discover -s tests -p "$f" -v
done
