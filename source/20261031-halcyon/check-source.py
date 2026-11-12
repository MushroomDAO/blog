"""Run lightweight checks against a clone; no model dependencies or downloads."""
import ast, importlib.util, json, sys
from pathlib import Path
root = Path(sys.argv[1])
files = sorted(root.glob('*.py'))
for path in files:
    ast.parse(path.read_text())
def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
vocab, common = load('vocab'), load('common')
assert vocab.TOTAL_VOCAB_SIZE == 80640
assert vocab.IMAGE_TOKENS == 1024
assert vocab.IMAGE_TOKEN_RANGE == (16384, 80384)
assert common.default_cfg_scale('radicalnumerics/Halcyon-1.6B', 'baseline') == 5.0
assert common.default_cfg_scale('radicalnumerics/Halcyon-1.6B', 'main') == 5.2
print(json.dumps({'parsedFiles': [p.name for p in files], 'helperChecks': 5,
                  'totalComputeRatio': 3.68e23 / 1.34e21,
                  'inferenceRun': False}, indent=2))
