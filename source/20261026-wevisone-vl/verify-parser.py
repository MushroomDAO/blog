"""Run the two pinned upstream parser tests without importing model dependencies."""
from pathlib import Path
import ast
import importlib.util
import json

root = Path(__file__).parent
spec = importlib.util.spec_from_file_location('reviewed_parser', root / 'upstream-parser.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
names = ['test_parser_scales_bins_and_drops_degenerate_boxes', 'test_parser_reads_points_and_truncated_answers']
nodes = [n for n in ast.parse((root / 'upstream-test-evaluation.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name in names]
assert len(nodes) == len(names)
namespace = {'parse_prediction': parser.parse_prediction}
exec(compile(ast.Module(body=nodes, type_ignores=[]), 'upstream-parser-tests', 'exec'), namespace)
for name in names:
    namespace[name]()
assert parser.parse_prediction('None', 1280, 720) == {}
print(json.dumps({'upstreamTestsPassed': names, 'NoneToEmptyPassed': True, 'scope': 'synthetic parser inputs; no model inference or GPU benchmark'}))
