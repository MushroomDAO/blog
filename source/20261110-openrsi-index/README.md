# OpenRSI Index — review and publication evidence

Job: 22c882a4-7a52-42f8-84d1-f80407d85c3c
Slug: openrsi-index-research-agent-benchmark-guide

source-inventory.json pins the repository revision and reviewed primary documents. source-audit.json records real task compiler output, manifest count and Qwen JSONL byte/hash checks; audit-source.py reruns that read-only audit against a supplied checkout.

Targeted upstream tests, in an isolated Python 3.12 environment:

```bash
uv pip install --python /path/to/venv/bin/python -e /path/to/OpenRSI-Index/RSI-Harness pytest pytest-asyncio
cd /path/to/OpenRSI-Index/RSI-Harness
/path/to/venv/bin/python -m pytest tests/runtime/test_reward.py tests/task/test_digest.py tests/task/test_compiler.py tests/runtime/test_submissions.py -q
```

183 tests passed. No complete suite, Docker deployment, firewall change, paid model call, GPU training or scientific score reproduction. CLI help was inspected; article GPU command is an unexecuted reader example.

The Qwen public wrapper is data-only. Marin is a sanitized non-Harbor historical environment. GPIC logged continuation and packaged legacy runtime differ; its screening protocols are not a matched cross-agent benchmark. The article preserves those boundaries.

Private raw upstream pages and logs are stored in the job folder. Public evidence here includes our own audit, test output and channel readback, without republishing raw contacts or transcripts.
