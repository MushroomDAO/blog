from pathlib import Path
import subprocess,textwrap,re,json,sys
r=Path(sys.argv[1])if len(sys.argv)>1 else Path('/tmp/corespeed-tie-research/cs')
lines=(r/'.github/workflows/check.yml').read_text().splitlines();out=[];name='';i=0
while i<len(lines):
 m=re.match(r'      - name: (.*)',lines[i])
 if m:name=m[1]
 if lines[i]=='        run: |':
  i+=1;a=[]
  while i<len(lines)and(not lines[i].strip()or lines[i].startswith('          ')):
   a.append(lines[i]);i+=1
  script=textwrap.dedent('\n'.join(a));p=subprocess.run(['bash','-eu','-c',script],cwd=r,text=True,capture_output=True);out.append({'name':name,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});continue
 i+=1
assert out and all(x['exitCode']==0 for x in out),out
report={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'checks':out,'scope':'Only upstream run blocks for local JSON/manifests; no GitHub Actions checkout or thirdparty scanner action; no login,devicepairing,GUIpermissiongrant or remotecontrol'}
Path(__file__).with_name('plugin-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'commit':report['commit'],'passed':len(out),'names':[x['name']for x in out]},ensure_ascii=False))
