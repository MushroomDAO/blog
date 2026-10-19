---
pretty_name: Pine Computer — SaaSBench Evaluation Results
language:
- en
license: cc-by-4.0
size_categories:
- n<1K
tags:
- benchmark
- evaluation
- computer-use
- saas-bench
- tabular
configs:
- config_name: results-2026-09-09
  default: true
  data_files:
  - split: test
    path: releases/2026-09-09/results.jsonl
- config_name: saas-bench-1.1-2026-09-18
  data_files:
  - split: test
    path: releases/2026-09-18-saas-bench-1.1/results.jsonl
---

# Pine Computer — SaaSBench Evaluation Results

**[Pine Computer](https://pinesandbox.io) · [Pine AI](https://pine.im)**

Task-level results and evidence hashes for Pine Computer on SaaS-Bench. Raw traces and screenshots remain private. Separate releases retain their own task versions, selection rules and benchmark suite; they are not pooled.

## Latest: SaaS-Bench 1.1 · September 18–19, 2026

**78.33% checks passed · 29/106 tasks fully resolved (27.36%) · 106/106 tasks with valid results.**

The checkpoint numerator is **1,077 / 1,375 checks**. This completed batch had **125 attempts**: 106 accepted outcomes and 19 invalid/superseded attempts. Sixteen healthcare tasks were rerun after environment/grader fixes; three other tasks had grading-error retries. Valid failures and eight timeouts remain in the results. This is not a first-attempt-only score. See the [methodology](releases/2026-09-18-saas-bench-1.1/methodology.md) for the full selection and comparison caveats.

| Domain | Tasks | Checks passed | Fully resolved |
| --- | ---: | ---: | ---: |
| Agriculture | 12 | 76.74% | 8/12 |
| Business | 15 | 84.26% | 3/15 |
| Healthcare | 16 | 68.98% | 1/16 |
| Media | 20 | 80.85% | 8/20 |
| Software | 31 | 75.85% | 8/31 |
| Teamwork | 12 | 86.78% | 1/12 |

[Results](releases/2026-09-18-saas-bench-1.1/results.jsonl) · [Summary](releases/2026-09-18-saas-bench-1.1/summary.json) · [Evidence hashes](releases/2026-09-18-saas-bench-1.1/evidence-index.jsonl) · [Methodology](releases/2026-09-18-saas-bench-1.1/methodology.md)

## Release history

| Evaluation (UTC) | Suite | Checkpoint | Fully resolved | Results |
| --- | --- | ---: | ---: | --- |
| September 18–19, 2026 | SaaS-Bench 1.1 · `d38803b44197` | 78.33% | 29/106 | [106 rows](releases/2026-09-18-saas-bench-1.1/results.jsonl) |
| September 9–10, 2026 | Original SaaS-Bench · `dc16a4421dd0` | 76.35% | 27/106 | [106 rows](releases/2026-09-09/results.jsonl) |

These are different suites and are **not a controlled before/after comparison**. Historical release data, methodology and hashes are preserved. The original default dataset configuration is also preserved for existing consumers.

## Load results

```python
from datasets import load_dataset

results = load_dataset(
    "pine-ai/pine-computer-saasbench-results",
    name="saas-bench-1.1-2026-09-18",
    split="test",
)
```

Use `name="results-2026-09-09"` for the original release. These are evaluation-result records, not the underlying source tasks or execution environments.

## Evidence and attribution

Each release's evidence index identifies complete private archives by SHA-256. Publisher checks verify file identity and archive completeness, not independent task success. No third-party outcome verification is claimed.

SaaS-Bench was introduced by [UniPat AI](https://github.com/UniPat-AI/SaaS-Bench). These are Pine Computer results from Pine's integration; upstream task definitions and verifier source are not redistributed here. See the [upstream task-data license](https://github.com/UniPat-AI/SaaS-Bench/blob/main/LICENSE-DATA).

Public results and original documentation are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see [LICENSE.md](LICENSE.md). Attribute Pine AI, Pine Computer — SaaSBench Evaluation Results, the specific release and this repository URL. This license does not grant rights to private raw evidence.
