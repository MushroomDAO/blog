# Adapter card: first-training

- Template: `prompt-only@1.0`
- Started from: `e9e7ac4f4e31be57e29221b4d3ba56c4b04f9aa8`
- Evolver: `learner`
- Task: task-info
- Training: 1 epoch(s), 2 step(s)
- Spending: rollouts $0.0000, Evolver $0.0000; 0.00 h

## Settings that affect what can be trusted

- sandbox: {"enabled": false, "enforce": "required", "network": "none", "allow": [], "read": [], "packages": [], "env": [], "audit": null, "profiles": {}}
- evolver_access: {"environment": [], "tools": [], "send_material_out": false}
- validation data given to the Evolver: False

Warnings raised at start:
- sandbox.enabled is false: what the Evolver starts runs unconfined; it can read anything on this machine, including the test split, and reach the network.

## What was learned

current adapter

See the final step's report: `step_0002/output/report.md` in the run records.

## Evaluation

| Adapter | Tasks | Repeats | Mean score | Solved at least once | Cost (USD) |
|---|---|---|---|---|---|
| final | 2 | 1 | 1.000 | 1.000 | 0.0000 |

Where it has not been tested: any task, model or pipeline other than the one above.
