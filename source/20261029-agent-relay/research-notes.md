# Agent Relay research and verification

Checked 2026-10-29. Canonical source: https://github.com/AgentWorkforce/relay

## Duplicate reconciliation

The bot query and fresh check split Agent Relay into the generic word relay, yielding Nostr, network relay and other unrelated topics. Exact primary URL matched no article, local receipt, remote draft or memory. Exact phrase in OpenConnector refers to an ordinary local agent relay, not AgentWorkforce. Only raw incoming KB material matches this project. Remote drafts queried successfully (6 entries); published API denied 48001. No prior receipt exists to suggest an already published Agent Relay article. A new canonical slug is justified.

## Pinned sources

- Relay 1503039856c5c8665601f814c17f751407f66497; 2026-10-29T00:07:55-07:00
- Relayfile ffeca124e8817328f3151516540234004f050ae8; 2026-10-27T00:28:05Z
- RelayHistory be827d1e84e6f57de9c0e9c2ac5224369644cf2e; 2026-10-28T04:58:16Z
- Flows 878e089e1e9f16f440d3fdbdf5220782010739c5; 2026-10-28T14:59:08Z
- Relaycast 711c9c7e62ed934533cfedab15bfbe61b08adc13; 2026-10-29T06:35:24Z

Secondary READMEs and authoring guide were retrieved from main during the same pass; snapshots accompany the recorded heads. URLs in article remain readable main links. Latest formal Relay release v14.0.0 published October 13; npm version 14.0.0 checked independently. Source and published package are not assumed equivalent.

YC official page confirms Fall 2026, founders Will Washburn and Khaliq Gant. It is not a YC-authored project. Website trust page last reviewed October14 states full Cloud is not packaged for self-hosting, approval is per-flow and enterprise security features remain pending. Flows per-step permissions are explicitly declaration-only; cwd is not sandbox. No E2EE or compliance certification asserted.

## Local proof

Temporary npm workspace /tmp/agent-relay-smoke. Node22.23.4 invoked through npm exec node@22. Published @relaycast/engine12.2.1, locked dependencies. npm blocked unreviewed better-sqlite3 install script by default; its normal prebuild/build script was run explicitly in that disposable dependency directory. No global project/runtime configuration changed.

smoke.mjs constructs the real Node runtime with in-memory SQLite, then calls Hono request handlers without opening network sockets. Seven assertions passed: create workspace, register Alice/Bob, unauthenticated inbox401, DM accepted201, recipient exact message, authenticated sender inbox200, empty DM400. Engine reports provider not delivery-ready and deferred live delivery, consistent with no actual clients. No live agent, cloud, cross-machine, WebSocket, external SaaS or performance check. Tokens never printed; raw result contains only disposable IDs/message. No private history indexed. Node runtime closed.

Reproduce in a disposable directory with Node22: npm install @relaycast/engine@12.2.1; if npm blocks native install scripts review and build better-sqlite3 there; copy smoke.mjs to that directory and run node smoke.mjs. Use the archived lock for dependency precision. Do not run the script from this source directory expecting unrelated blog dependencies to supply the engine.

## Imagery

Official README hero https://agentrelay.com/readme-banners/relay.png inspected, 1400x392 with logo/text on a mostly dark background. Rejected because it is largely text/dead space and a 1200x630 cover crop would cut the wordmark. Original topic-specific banner generated locally using banner-creator FLUX seed8107: three computers wired through a switch, no people. Not a product screenshot. Machine verification passed with 0 failures and 0 warnings (93749 bytes); manual inspection confirmed a topic-matched illustrative photograph, no readable text or people. Three separate XiaoM figures commissioned through publisher-authorized codex exec; see illustrations.md.

## Published CLI compatibility proof

Installed agent-relay14.0.0 under /tmp/agent-relay-cli using Node22, ignore-scripts and omit-optional. DO_NOT_TRACK and AGENT_RELAY_TELEMETRY_DISABLED were set, AGENT_RELAY_HOME pointed to temporary state. Real --help shows no init command; init --help prints generic root help. mcp --help confirms --sessions-only. No init or login performed, no real client config changed. Article therefore gives published install/help commands separately from the main-branch init workflow. Static package evidence independently confirms sessions flag and no init command registration.

## Final image and build check

Three final 1120x630 figures accepted manually. Figure3 compression was corrected to retain red cap and blue labels; final sizes57357/49996/66650 bytes. An earlier build preceded that final image review, so the final build was repeated after asset acceptance. Only the final build will be deployed. No article or asset changes are intended after that build.
