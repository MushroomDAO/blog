"""Check literal regexes from the pinned plugin, not the complete safeagents policy."""
from pathlib import Path
import ast,re,hashlib,json,urllib.request
url='https://huggingface.co/harness-hub/qwen-safeagents-plugin/resolve/d39145c491b854d104272bd4bac501be7f01deea/atif_harbor.py'
src=urllib.request.urlopen(url,timeout=30).read();assert hashlib.sha256(src).hexdigest()=='33cd9c2a87d53d882a0881aaae620acb758c98f31127e2a4e8dedb24b9dcf108'
tree=ast.parse(src);names={'SOLUTION_PATH','HIDDEN_PATH','EXIT_ZERO','FORCED_SUCCESS'};nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in names for x in n.targets)];ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'pinned-regex-constants','exec'),ns)
cases=[('own deliverable','SOLUTION_PATH','/solution/solve.py',True),('nested repository path','SOLUTION_PATH','/app/solution/solve.py',False),('hidden tests','HIDDEN_PATH','/tests/test_outputs.py',True),('hidden rewards','HIDDEN_PATH','/logs/verifier/reward.txt',True),('ordinary project tests','HIDDEN_PATH','/app/tests/test.py',False),('debugging hook','FORCED_SUCCESS','sys.excepthook = print',False),('forced success hook','FORCED_SUCCESS','sys.excepthook = lambda *args: sys.exit(0)',True),('nonzero debug exit','FORCED_SUCCESS','sys.excepthook = lambda *args: sys.exit(99)',False)]
for name,key,text,expected in cases:assert bool(re.search(ns[key],text))==expected,name
print(json.dumps({'passed':len(cases),'scope':'regex constants only, no detector composition or real tool execution'}))
