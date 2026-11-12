"""Read-only resource inventory; never loads model weights or contacts a device."""
import json
from pathlib import Path
import subprocess
import sys
mika, worldforge = [Path(x).resolve() for x in sys.argv[1:3]]
p = mika / 'core/src/main/resources/knowledge'
def revision(root):
    return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
r = {'mika': {'revision': revision(mika), 'appKnowledgeFiles': len(list((p/'apps').glob('*/APP.md'))), 'siteKnowledgeFiles': len(list((p/'sites').glob('*/SITE.md'))), 'byoModelDocument': 'docs/models.md'}, 'worldforge': {'revision': revision(worldforge), 'sourcePathsExist': {n:(worldforge/n).exists() for n in ['forge.py','macos_app','remote/forge_server.py','forge_local/postproc.py']}}, 'scope':'File inventory only; no functional Android/GPU or model capability test.'}
assert all(r['worldforge']['sourcePathsExist'].values())
print(json.dumps(r, indent=2))
