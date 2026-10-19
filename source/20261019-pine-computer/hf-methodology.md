# SaaS-Bench 1.1 — September 18–19, 2026

Pine Computer's production benchmark finished at 2026-09-19 04:33:38 UTC. Suite identity: `d38803b44197`; each result carries its actual task-version digest. The immutable Computer image version is not recorded in batch metadata and is not inferred from the current deployment.

## Selection and reruns

There were 125 attempts across 106 selected tasks. This release contains all 106 accepted runs, one per task, including 77 unresolved tasks and eight timeouts. Acceptance requires completed cleanup and the production benchmark validity verdict. It is not conditioned on task success.

Nineteen attempts are excluded: 16 healthcare attempts were invalidated by the operator after environment/grader fixes, then rerun under updated task versions; three other attempts had grading errors and were replaced by valid retries. No accepted run uses a valid-by-operator override. Accepted attempts are 87 first attempts and 19 second attempts. This is a repaired, multi-attempt benchmark batch, not a first-attempt-only result or a frozen single-build comparison. Task-level scores are not manually corrected in this publication.

## Metrics and schema

- Checkpoint: 1,077 / 1,375 checks passed = **78.33%**. Each verifier check contributes equally.
- Fully resolved: 29 / 106 tasks = **27.36%**. Every check must pass.
- `score` is the verifier's weighted points ratio, alongside `points_earned` and `points_total`. Do not average these scores to reproduce checkpoint.
- `terminal_reason=completed` means the agent ended its run, not that it passed every check. There are 98 completed runs and eight timeouts.
- Result rows contain release/record/task/version identifiers, domain, attempt, weighted scores, check counts, resolution, grade status, terminal reason and accepted/valid flags. The `test` split is result data, not source task material.

## Evidence and limitations

Original full gzip-NDJSON traces are retained privately. Each public evidence-index row binds a stable result ID to the compressed archive's SHA-256 and byte length. All 106 archives passed compressed byte count, SHA-256, storage checksum, gzip CRC, NDJSON parsing, task/run/schema identity, event counts/order/bounds, complete final metadata, and screenshot-count checks. No screenshots were omitted from these archives.

Private raw traces, prompts, screenshots, grading detail, credentials and operational identifiers are not included in this public package. Hash matching proves archive identity, not independent task success. Recorded diagnostic reviews are not treated as independent verification or authority to change grades.

The older September 9 release measures the original SaaS-Bench suite; this release measures SaaS-Bench 1.1. Different tasks, versions, fixtures and rerun histories prevent an apples-to-apples performance claim. Historical release files remain unchanged.

SaaS-Bench attribution: [UniPat AI](https://github.com/UniPat-AI/SaaS-Bench). Public result data and this documentation retain this repository's [CC BY 4.0 license](../../LICENSE.md); that license does not grant rights to private evidence.
