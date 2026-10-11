# Peekaboo source and local checks — 2026-10-11

Official repository: https://github.com/openclaw/Peekaboo
Documentation commit: 509f12ce7958f220b693608106a135a7ac163775
Latest release snapshot: v4.9.0, published 2026-10-07.
GitHub API snapshot: 5282 stars. Moving counters are not performance measures.

Files README-official.md, docs-*.md, LICENSE and assets-peekaboo.png are unmodified official material from the pinned MIT repository. Main documentation may include post-release work. cli-* files are local observations, not an end-to-end benchmark.

Environment: Apple Silicon, macOS26.6.2, Node26.10.0.
Version check succeeds. MCP help supports stdio, reserves HTTP/SSE.
Permission query succeeds but selected Bridge and local hosts lack Screen Recording, Accessibility and Event Synthesizing grants.
Agent dry-run uses --no-desktop-context, reports no model invocation, zero tool calls, background-only policy. No real UI capture or action, clipboard read or permission request was performed. No latency/success-rate claim.

Reproduce the read-only checks:
```sh
npx -y @steipete/peekaboo@4.9.0 --version
npx -y @steipete/peekaboo@4.9.0 mcp --help
npx -y @steipete/peekaboo@4.9.0 permissions status --all-sources --json
npx -y @steipete/peekaboo@4.9.0 agent "Inspect a disposable local test window without changing it" --dry-run --no-desktop-context --json
```
Permissions depend on the actual execution host. A successful diagnostic command does not grant desktop access.

Banner decision: official hero is mostly marketing text and therefore unsuitable under banner rules. Generated article-specific local FLUX2Klein4B seed81 Mac keyboard/trackpad observation scene; verified1200x630,85371bytes,no text/faces and visually inspected.
