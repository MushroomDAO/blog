# Vitalik paranoid AI privacy research — 2026-10-22

Task: c5e63f39-e4a3-4689-94f6-b29d0541af1b

Article: https://blog.mushroom.cv/blog/vitalik-paranoid-ai-zkapi-tor/

Original October 16 post includes its demonstration video: https://x.com/VitalikButerin/status/2111046730959433793
Direct X retrieval returned403. Public embedded post checked; its actual shortlink https://t.co/MepCFCrLv1 resolved to https://github.com/vbuterin/zkapi/tree/feat/client-concession-local . No separate original vlog identified.

Pinned source: 0fb263b0da04986cfe5c63b12340c1581018ae9b. Client MIT license only; no blanket license claim. source-review.json hashes13 relevant source documents; verify-source.py checks those hashes, placeholder deployments and privacy statements.

Reproduce the local checks from that exact source checkout:

```sh
cd /tmp/vitalik-zkapi-research/zkapi-clientd
go test -json ./internal/relay ./internal/rewriter ./internal/cover
```

Actual local toolchain go1.27.1 darwin/arm64. 3packages passed;32test/subtest pass events,6skips,0failures. Local SOCKS/TLS/mock fixtures, not live Tor, model generation, paid inference, wallet transactions, gas savings or anonymity evaluation. These counts do not denote independent security properties. Upstream16case editor qualitative evaluation is described with attribution, not rerun.

Distinct layers: authorization unlinkability, network isolation identities, task wording, bounded cover GETs and agent sandbox. None proves content secrecy from inference. User-text rewriting does not comprehensively sanitize tool/system messages or attachments. Rewriter connection is direct; use truly local model if original text must stay local. Mainnet gas roadmap not confirmed shipped. Branch itself marks undeployed concession manifests and absent production proving keys; old clientd-v0.1.6 packages lack these privacy features. Go guide1.26 versus actualgo.mod1.25 discrepancy recorded.

No suitable official nonportrait/text-light hero. Generated FLUX164 banner rootviewed:88973B1200x630; natural dark desk edge accounts for framing warning, not artificialpadding. Earlier163discarded tinydeviceengraving. Three current red-cap XiaoM figures rootreviewed:32645/48856/42831B1280x720.

Prewriting dedup exactsource absent; zkAPI match was raw user KB material only. PublishedlistAPI48001, remote draftbox1, local receipts and MemPalace searched; no prior article or draftreceipt found. Reused raw material. One new WeChat draft created only after Blog deploy; remote read and fulltail/metadata/cover/bodyimages checked. No mass-send.

Verification and final receipts are separate JSON files. Full upstream repository, private environment, wallet state, raw user KB matches and nested image-generation logs are not tracked here.
