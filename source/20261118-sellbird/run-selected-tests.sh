#!/usr/bin/env bash
set -euo pipefail
cd "${1:?isolated checkout}"
"${2:?venv python}" -m pytest tests/test_outbox_native.py tests/test_outbox_review.py tests/test_do_not_contact.py tests/test_send_window.py tests/test_outbox_claim.py tests/test_dashboard_auth.py -q
