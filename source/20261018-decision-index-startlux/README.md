# Decision Index / StartLux October update

Updates existing article rather than duplicating its slug. Generated2026-10-16 official0.3.2 snapshot captured2026-10-18. Evidence and reproduction: `python source/20261018-decision-index-startlux/recompute-board.py` uses the saved official `board-v03.json` and writes `board-recomputed.json`. Upstream kit pinned f5a6e4fd85fed05e77878dfc4966d0568bfb45ec: run tests/test_index03.py with pytest and kit on PYTHONPATH.15 passed. Neither command runs a model or private benchmark.

Article/source checks: check-content.py and verify-live.py. Existing cover retained, three new conceptual figures. Draft/get40007 and freepublish/batchget48001 leave old creation receipt as archived evidence only; no draft created or updated. Never treat archivedMediaId as a current draft ID.
