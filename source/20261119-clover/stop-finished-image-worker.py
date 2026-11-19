"""Stop only this task's overlong packaging worker after its three images exist."""
import subprocess,re,os,signal,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];slug='clover-diffusion-llm-sft-engineering-guide'
assert all((root/f'src/assets/images/{slug}-fig-{i:02d}.png').exists()for i in range(1,4))
rows=[]
for line in subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines():
 parts=line.strip().split(None,2)
 if len(parts)==3:rows.append((int(parts[0]),int(parts[1]),parts[2]))
pattern=r'^(?:\S*/)?codex exec -C /Users/jason/Dev/mycelium/blog -s workspace-write Use \$mycelium-mushroom-illustrations\. Read src/content/blog/clover-diffusion-llm-sft-engineering-guide\.md\.'
targets=[pid for pid,ppid,cmd in rows if re.search(pattern,cmd)];assert len(targets)==1,targets
owned=set(targets)
while True:
 old=len(owned);owned.update(pid for pid,ppid,cmd in rows if ppid in owned)
 if len(owned)==old:break
for pid in sorted(owned,reverse=True):
 try:os.kill(pid,signal.SIGTERM)
 except ProcessLookupError:pass
report={'workerPids':targets,'terminatedOwnedProcesses':sorted(owned),'reason':'Three images generated/copied; worker repeated packaging despite primary compression instruction. Preserve originals and re-compress from preserved images after stopping writes.','generatedImages':3,'imageGenerationRepeated':False}
Path(__file__).with_name('illustration-worker-recovery.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
