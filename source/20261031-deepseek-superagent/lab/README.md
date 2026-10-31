# Super-agent offline engineering exercise / 离线工程练习

This is an educational integration test, **not a new agent framework, a production deployment, or a model benchmark**. It reuses the official prototype's real `Engine`, SQLite `Store`, `Effects` and health board. Assessment, execution and destination delivery are local deterministic doubles. It never runs a real coding agent, logs into a service, sends GitHub/Feishu messages or merges a PR.

## Reproduce / 复现

Use Node in the upstream declared range (`^22.19.0 || >=24.0.0`) and pnpm. Tested here on Node26.10.0 and pnpm11.7.0, AppleM4/16GB/macOS26.6.2. Download this ZIP outside the checkout, unzip it, then:

```bash
git clone https://github.com/deepseek-ai/dsh-superagent-prototype.git
cd dsh-superagent-prototype
git checkout 6337fc823ce20251c8de8085948165c81aaa701e
pnpm install --frozen-lockfile
# Replace /path/to/lab with the extracted directory.
cp /path/to/lab/mycelium-practice.spec.ts tests/mycelium-practice.spec.ts
pnpm typecheck
pnpm exec vitest run tests/mycelium-practice.spec.ts
```

Expected: **7 passed**. The full upstream baseline `pnpm check` passed59files/1197tests before this extra test file was added; the extra exercise and typecheck were run separately. Temporary SQLite directories are cleaned after each case.

## Seven cases / 七个场景

1. Reopen SQLite and replay one source ID: no duplicate event.
2. An unauthorized originating actor never reaches semantic assessment.
3. A queued assignment survives database reopen without another ticket.
4. A subscribed guest follow-up supplies context without a new assessment or wider mandate.
5. A ready worker report differs from the owned PR being merged.
6. Receipt and delivery effect roll back together.
7. A lost acknowledgement causes a retry with a stable key; a fake idempotent destination keeps one logical result.

Case7 deliberately distinguishes two attempts from one logical delivery. The fake destination supports idempotency; real destinations require their own guarantees or reconciliation. The upstream GitHub adapter embeds a `dsh-superagent:<message-id>` HTML marker and searches existing comments before posting. That is useful reconciliation, not a universal exactly-once transaction across databases and GitHub. Do not remove it when adapting the channel.

Database reopen is not a hard-killed process/power-loss experiment. No distributed failover, arbitrary external-tool idempotency, real model quality, OS sandbox or semantic watchdog is validated here. `stop()` is empty because no OS worker is launched in this fixture; production code must use a real cancellation adapter. Source text and policy are separate; the subscribed-context test does not prove a model resists prompt injection.

The official runtime remains in the upstream repository. Follow its SETUP.md only when intentionally deploying with dedicated credentials and an isolated execution environment; this exercise does not run that setup.

Source provenance: `tests/core-engine.spec.ts`, `src/core/engine.ts`, `src/app/store.ts`, `src/app/effects.ts`, `src/app/outbox.ts` at the pinned commit. Original prototype: MIT, Copyright(c)2026DeepSeek Harness Team. The added harness is MIT, Copyright(c)2026Mycelium Protocol. Retain both license files.
