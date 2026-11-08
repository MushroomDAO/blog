from pathlib import Path
import ast,json,hashlib,sys,subprocess
root=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ai-infra-learning-research');out=Path(__file__).parent
modules=[]
for p in sorted((root/'lessons').glob('mod-*')):
 labs=list((p/'labs').glob('lab-*.md'));ex=[q for q in (p/'exercises').iterdir() if q.is_dir()and q.name.startswith('exercise-')and(q/'README.md').exists()]if(p/'exercises').exists()else[]
 flat=list((p/'exercises').glob('exercise-*.md'));modules.append({'module':p.name,'labs':len(labs),'exerciseDirectories':len(ex),'flatExerciseFiles':len(flat)})
projects=[];syntax=[]
for p in sorted((root/'projects').glob('project-*')):
 tests=[]
 for f in sorted((p/'tests').glob('test_*.py')):
  tree=ast.parse(f.read_text());funcs=[]
  for n in ast.walk(tree):
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name.startswith('test_'):
    body=[x for x in n.body if not(isinstance(x,ast.Expr)and isinstance(x.value,ast.Constant)and isinstance(x.value.value,str))]
    empty=all(isinstance(x,ast.Pass)or(isinstance(x,ast.Expr)and isinstance(x.value,ast.Constant)and x.value.value is Ellipsis)for x in body)
    funcs.append({'name':n.name,'docstringAndPassOnly':empty})
  tests.append({'file':str(f.relative_to(root)),'functions':funcs})
 projects.append({'project':p.name,'tests':tests})
for f in root.rglob('*.py'):
 if '.git' in f.parts:continue
 try:ast.parse(f.read_text());syntax.append({'path':str(f.relative_to(root)),'parses':True})
 except(SyntaxError,UnicodeError)as e:syntax.append({'path':str(f.relative_to(root)),'parses':False,'error':str(e)})
r={'repository':'https://github.com/ai-infra-curriculum/ai-infra-engineer-learning','commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'modules':modules,'labFiles':sum(x['labs']for x in modules),'exerciseEntries':sum(x['exerciseDirectories']+x['flatExerciseFiles']for x in modules),'projects':projects,'projectMakefiles':[str(q.relative_to(root))for q in root.glob('projects/project-*/Makefile')],'parserPythonVersion':sys.version,'pythonSyntax':syntax,'scope':'File inventory and Python AST inspection only; presence is not completeness or runtime correctness. Docstring/pass-only detection is structural, not a complete test-quality analysis.'}
(out/'repository-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'commit':r['commit'],'modules':modules,'totalLabs':r['labFiles'],'exerciseEntries':r['exerciseEntries'],'projectTestFunctions':[{'project':p['project'],'functions':sum(len(t['functions'])for t in p['tests']),'empty':sum(f['docstringAndPassOnly']for t in p['tests']for f in t['functions'])}for p in projects],'pythonFiles':len(syntax),'syntaxErrors':sum(not x['parses']for x in syntax)},indent=2))
