"""Stage only this task's records; retain the full licensed paper privately."""
from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent;root=p.parents[1];included=[];excluded=[]
for f in p.rglob('*'):
 if not f.is_file():continue
 rel=str(f.relative_to(root))
 if f.name.startswith('report') and f.suffix in {'.pdf','.html','.txt','.png'}:excluded.append(rel)
 else:included.append(rel)
record=p/'public-stage-scope.json';record.write_text(json.dumps({'excludedFullPaperAndRenders':excluded,'privateArchive':'bot job e87ef8e5-8623-49a7-9a94-00ad3a756676/research','articleUsesOriginalIllustrations':True},indent=2));included.append(str(record.relative_to(root)))
subprocess.run(['git','add','-f','--']+sorted(set(included)),cwd=root,check=True)
print(json.dumps({'stagedSourceFiles':len(set(included)),'excludedFullPaperFiles':len(excluded)}))
