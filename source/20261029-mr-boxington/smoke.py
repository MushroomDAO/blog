import os,json,subprocess,tempfile,shutil
from pathlib import Path
out=Path('/Users/jason/Dev/mycelium/blog/source/20261029-mr-boxington');base=Path(tempfile.mkdtemp(prefix='proof-',dir='/tmp/boxington-smoke'));a=base/'checkout-a';b=base/'checkout-b';(a/'src').mkdir(parents=True)
(a/'Cargo.toml').write_text('[package]\nname="cache_probe"\nversion="0.1.0"\nedition="2024"\n')
(a/'src/lib.rs').write_text('pub fn answer() -> u32 { 42 }\n');(a/'src/main.rs').write_text('fn main() { println!("{}", cache_probe::answer()); }\n')
env={**os.environ,'MBX_CACHE_DIR':str(base/'cache'),'MBX_DISPLAY':'plain','MBX_SUMMARY':'full','CARGO_INCREMENTAL':'0'}
mbx='/tmp/boxington-bin/mbx';rows=[]
def run(label,args,cwd=a):
 r=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True);(out/f'{label}.log').write_text(r.stdout+r.stderr);rows.append({'label':label,'args':args,'cwd':str(cwd),'exitCode':r.returncode});assert r.returncode==0,(label,r.returncode,(r.stdout+r.stderr)[-1500:]);return r.stdout+r.stderr
run('toolchain',['rustc','--version']);run('lockfile',['cargo','generate-lockfile','--offline']);shutil.copytree(a,b)
run('cold-build',[mbx,'build','--offline','--target-dir',str(base/'target-a')]);run('cross-checkout-build',[mbx,'build','--offline','--target-dir',str(base/'target-b')],b)
r=subprocess.run([str(base/'target-b/debug/cache_probe')],capture_output=True,text=True);assert r.returncode==0 and r.stdout.strip()=='42';rows.append({'label':'restored-program','output':r.stdout.strip(),'exitCode':r.returncode})
run('explain-restored',[mbx,'explain','--last'],b)
(b/'src/lib.rs').write_text('pub fn answer() -> u32 { 43 }\n');run('modified-build',[mbx,'build','--offline','--target-dir',str(base/'target-c')],b)
r=subprocess.run([str(base/'target-c/debug/cache_probe')],capture_output=True,text=True);assert r.returncode==0 and r.stdout.strip()=='43';rows.append({'label':'modified-program','output':r.stdout.strip(),'exitCode':r.returncode})
run('explain-modified',[mbx,'explain','--last'],b);run('cache-stats',[mbx,'cache','stats','--json'],b);run('gc-preview',[mbx,'gc','--dry-run'],b)
(out/'smoke-results.json').write_text(json.dumps({'root':str(base),'conditions':{'cargoIncrementalSetting':'CARGO_INCREMENTAL=0; mbx learned_incremental left at its default, observed private state after edit','targets':'three distinct fresh explicit dirs','globalSetup':'not run','cache':str(base/'cache'),'benchmark':'not a timing or performance comparison'},'steps':rows},indent=2)+'\n');print('completed',base)
