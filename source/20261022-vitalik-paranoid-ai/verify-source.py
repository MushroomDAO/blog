from pathlib import Path
import subprocess,json,hashlib
b=Path(__file__).resolve().parent
r=Path('/tmp/vitalik-zkapi-research');pin='0fb263b0da04986cfe5c63b12340c1581018ae9b'
assert subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip()==pin
meta=json.loads((b/'source-review.json').read_text())
for x in meta['files']:assert hashlib.sha256((r/x['path']).read_bytes()).hexdigest()==x['sha256']
checks={'clientMIT':(r/'zkapi-clientd/LICENSE').read_text().startswith('MIT License'),'mainnetUndeployed':'"not_deployed"'in(r/'sdk/assets/config/mainnet.json').read_text(),'sepoliaUndeployed':'"not_deployed"'in(r/'sdk/assets/config/sepolia.json').read_text(),'oldPackageNotPrivacy':'do **not** contain'in(r/'zkapi-clientd/README.md').read_text(),'rewriterDirect':'outside Tor/Wisp'in(r/'zkapi-clientd/docs/REWRITER.md').read_text(),'attachmentsNotAnonymized':'**not anonymized**'in(r/'zkapi-clientd/docs/REWRITER.md').read_text(),'noProvenTrafficProtection':'not proven traffic-analysis protection'in(r/'zkapi-clientd/docs/COVER_TRAFFIC.md').read_text(),'goMod1_25':'go 1.25.0'in(r/'zkapi-clientd/go.mod').read_text(),'guide1_26':'Go 1.26'in(r/'zkapi-clientd/docs/DEVELOPMENT.md').read_text()}
assert all(checks.values()),checks
(b/'source-verification.json').write_text(json.dumps({'commit':pin,'hashesVerified':len(meta['files']),'checks':checks},indent=2));print('Pinned source and deployment/privacy/license boundaries verified')
