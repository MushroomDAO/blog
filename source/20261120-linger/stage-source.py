from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent;root=p.parents[1];files=[]
for f in p.rglob('*'):
 if not f.is_file():continue
 if f.suffix=='.log':f.write_text(f.read_text().rstrip()+'\n')
 files.append(str(f.relative_to(root)))
subprocess.run(['git','add','-f','--']+files,cwd=root,check=True)
print(json.dumps({'stagedSourceFiles':len(files),'scope':'only source/20261120-linger; upstreampubliclicensedexcerptrecords, no modelweights'}))
