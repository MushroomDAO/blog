"""Run upstream process matching tests in an isolated temporary directory, not the app."""
import hashlib,json,subprocess,tempfile,urllib.request
from pathlib import Path
pin='109de1d1690f6e3658e58725bf510f06af40ebfe'
proof=json.loads(Path(__file__).with_name('module-verification.json').read_text())
url=f'https://raw.githubusercontent.com/RoversX/ThinkTerm/{pin}/mux/src/agent_status/proc_match.rs'
with tempfile.TemporaryDirectory(prefix='thinkterm-proc-check-') as d:
 p=Path(d);source=urllib.request.urlopen(url,timeout=30).read()
 assert hashlib.sha256(source).hexdigest()==proof['sha256']
 (p/'proc_match.rs').write_bytes(source)
 (p/'check.rs').write_text('#[path = "proc_match.rs"] mod proc_match;\n')
 subprocess.run(['rustc','--edition=2021','--test',str(p/'check.rs'),'-o',str(p/'check')],check=True)
 subprocess.run([str(p/'check')],check=True)
