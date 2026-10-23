# Historical failure audit — 2026-10-23

Maintenance only. No article, deployment, banner or WeChat draft created.

- `history-audit.json`: 71 unique old article URLs, all HTTP 200; all local M2 receipt IDs match original records. Initial queue snapshot is before reconciliation.
- `wechat-audit.json`: only two current remote drafts. Published-list API 48001 prevents proving whether other 69 old receipts were published; preserve them as recorded/unverified.
- `reconciliation.json`: one false-failed homepage task closed after live homepage verification and private database backup. Queue afterward: 74 complete, this audit running, zero failed.
- `routing-before.log`, `bot-tests.log`, `typecheck.log`: regression reproduced then fixed in Heinu1 commit cf1caf3; 24 tests and typecheck pass.
- `reload-when-idle.py`: one-shot reload waits for current completed job, drained reply outbox, no running/pending jobs and no active CLI; checks idle twice. Status lives in `reload-status.json`. No second poller is manually started.
- `compatibility-publication-proof.json`: an existing Splash article receipt is reused only because this in-flight task's old bot plan still demands a publication receipt. This is not a new publication. New requests use the corrected classification after reload.

The raw sessions.db backup stays private outside Git. No old receipt IDs or published article bodies were rewritten. No semantic index update is needed because no content changed.
