"""Compile a tiny crate with Relax, check tests and borrow rejection, then patch a live function."""
from pathlib import Path
import subprocess,tempfile,json,os,select,time,re
out=Path(__file__).parent;exe=Path('/tmp/makepad-relax-20261114/target/release/relax');env={**os.environ,'RELAX_OFFLINE':'1'};reports={}
with tempfile.TemporaryDirectory(prefix='relax-smoke-')as d:
 root=Path(d);p=root/'relax_smoke';(p/'src').mkdir(parents=True);(p/'Cargo.toml').write_text('[package]\nname="relax_smoke"\nversion="0.1.0"\nedition="2021"\n[workspace]\n');code='''fn value() -> u32 { 1 }
fn main() { for i in 0..32 { println!("state={} value={}", i, value()); std::thread::sleep(std::time::Duration::from_millis(250)); } }
#[test] fn addition() { assert_eq!(2 + 3, 5); }
#[test] fn vec_sum() { let v = vec![1u32, 2, 3]; assert_eq!(v.iter().sum::<u32>(), 6); }
''';(p/'src/main.rs').write_text(code);(out/'smoke-fixture.rs').write_text(code)
 def run(args,name):
  r=subprocess.run([str(exe),*args],cwd=p,env=env,capture_output=True,text=True,timeout=150);(out/(name+'.log')).write_text(r.stdout+r.stderr);return r
 good=run(['check','relax_smoke'],'check-valid');assert good.returncode==0,(good.returncode,good.stderr[-1000:]);reports['validCheck']=True
 tests=run(['test','relax_smoke'],'jit-tests');assert tests.returncode==0,tests.stderr[-1000:];reports['jitTests']=True
 # A real borrow error, never executed.
 (p/'src/main.rs').write_text('fn main() { let mut v = vec![1]; let r = &v; v.push(2); println!("{:?}", r); }\n');bad=run(['check','relax_smoke'],'check-borrow-error');assert bad.returncode!=0 and ('borrow'in bad.stderr.lower()or'E0502'in bad.stderr),'Expected borrow rejection';reports['borrowErrorRejected']=True
 (p/'src/main.rs').write_text(code)
 process=subprocess.Popen([str(exe),'run','--quiet','--check-first','relax_smoke'],cwd=p,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1);lines=[];changed=False;deadline=time.monotonic()+150
 try:
  while time.monotonic()<deadline:
   ready,_,_=select.select([process.stdout],[],[],1)
   if not ready:
    if process.poll()is not None:break
    continue
   line=process.stdout.readline()
   if not line and process.poll()is not None:break
   lines.append(line)
   if 'state=2 value=1'in line and not changed:
    (p/'src/main.rs').write_text(code.replace('fn value() -> u32 { 1 }','fn value() -> u32 { 2 }'));changed=True
   if 'value=2'in line:reports['hotPatchStateRetained']=True
  if process.poll()is None:process.terminate()
  process.wait(timeout=10)
 finally:
  if process.poll()is None:process.kill();process.wait()
 (out/'hot-patch.log').write_text(''.join(lines));reports['hotPatchAttempted']=changed;reports['processExitCode']=process.returncode;states=[(int(a),int(b))for a,b in re.findall(r'state=(\d+) value=(\d+)', ''.join(lines))];new=[a for a,b in states if b==2];reports['hotPatchStateRetained']=bool(new)and new[0]>2 and all(states[i][0]<states[i+1][0]for i in range(len(states)-1));reports['states']=states
 reports['scope']='Apple M4, standalone Rust fixture, offline, no performance ratios, no game/Makepad UI/devhub run';(out/'smoke-results.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports))
