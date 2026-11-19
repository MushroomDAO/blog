from pathlib import Path
import subprocess,json,shutil,hashlib
p=Path(__file__).resolve().parent;root=p.parents[1];job=Path('/Users/jason/.heinu1-bot/jobs/4124913f-d640-4580-9065-ef75c531f32e/research');job.mkdir(parents=True,exist_ok=True);included=[];excluded=[]
for f in p.rglob('*'):
 if not f.is_file():continue
 if f.suffix=='.log':f.write_text(f.read_text().rstrip()+'\n')
 rel=str(f.relative_to(root))
 if f.parent.name=='research' and f.suffix in {'.pdf','.html','.txt','.png'}:
  shutil.copy2(f,job/f.name);excluded.append({'path':rel,'privateArchive':str(job/f.name),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 else:included.append(rel)
record=p/'research/archive-manifest.json';record.write_text(json.dumps({'fullPrimaryTextsAndPageRendersPrivate':excluded,'paperLicense':'CC BY4.0','articleIsOriginalAnalysisWithAttribution':True},indent=2));included.append(str(record.relative_to(root)))
subprocess.run(['git','add','-f','--']+sorted(set(included)),cwd=root,check=True);print(json.dumps({'stagedSourceFiles':len(set(included)),'privateFiles':len(excluded)}))
