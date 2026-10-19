"""Run only the upstream fixed-revision policy package, without deploying localDot."""
from pathlib import Path
import urllib.request, tempfile, subprocess, json, hashlib
rev='e5054494125d09c6db86aba322be5e46cb8618ca'
files=['keyd/go.mod','keyd/go.sum','keyd/internal/policy/policy.go','keyd/internal/policy/policy_test.go','keyd/internal/policy/policy_integrity_test.go']
with tempfile.TemporaryDirectory(prefix='localdot-policy-') as td:
 root=Path(td)
 for name in files:
  data=urllib.request.urlopen(f'https://raw.githubusercontent.com/Shadowhusky/localdot/{rev}/{name}',timeout=40).read();p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  print(json.dumps({'file':name,'sha256':hashlib.sha256(data).hexdigest()}),flush=True)
 subprocess.run(['go','test','-json','-count=1','./internal/policy'],cwd=root/'keyd',check=True)
