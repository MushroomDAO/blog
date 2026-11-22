"""Run the pinned project's capture verifier on its original PAGE fixture; pass checkout path."""
import ast, subprocess, sys, tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve()
tree=ast.parse((repo/'tests/test_capture.py').read_text())
page=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAGE' for t in n.targets))
with tempfile.TemporaryDirectory(prefix='cinecode-determinism-') as tmp:
    root=Path(tmp);(root/'lib').mkdir();(root/'assets').mkdir()
    (root/'index.html').write_text(page)
    (root/'lib/theme.mjs').write_text('export const tint="#ff0000";\n')
    (root/'assets/image.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#00ff00"/></svg>')
    subprocess.run(['node',str(repo/'scripts/capture.mjs'),'--url',str(root/'index.html'),'--verify'],check=True)
