from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent;work=Path('/tmp/brief2mp4-smoke-20261119');work.mkdir(exist_ok=True)
scripts=Path('/tmp/brief2mp4-20261119/plugin/skills/brief2mp4/scripts')
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=120);return r
def command(args):
 r=run(args);assert r.returncode==0,r.stderr;return r
command(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=24','-t','1','-c:v','libx264','-pix_fmt','yuv420p',str(work/'rough.mp4')])
command(['bash',str(scripts/'finish.sh'),'--in',str(work/'rough.mp4'),'--out',str(work/'final.mp4'),'--seconds','2','--size','640x360','--fps','30'])
command(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=teal:size=640x360:rate=30','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','3','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(work/'blank.mp4')])
cases=[('finished-file',work/'final.mp4','2',True,0),('wrong-duration',work/'final.mp4','3',True,1),('silent-without-permission',work/'final.mp4','2',False,1),('missing-audio',work/'rough.mp4','1',True,1),('blank-semantic-negative-control',work/'blank.mp4','3',True,0)]
results=[]
for name,f,seconds,silent,expected in cases:
 args=['bash',str(scripts/'check_delivery.sh'),str(f),'--seconds',seconds,'--size','640x360','--fps','30']+(['--silent-ok']if silent else[])
 r=run(args);(p/(name+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==expected,(name,r.stdout,r.stderr)
 results.append({'case':name,'returncode':r.returncode,'expected':expected,'output':r.stdout})
probe=json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(work/'final.mp4')]).stdout)
out={'scope':'Original unmodified finish/check scripts; generated synthetic clips, no coding-agent video creation or 3D/Blender render. Blank teal contains none of a hypothetical required headline yet delivery passes with frozen warning; demonstrates format vs semantic boundary.','cases':results,'probe':probe,'scriptHashes':{n:hashlib.sha256((scripts/n).read_bytes()).hexdigest()for n in ['finish.sh','check_delivery.sh']}}
(p/'smoke-results.json').write_text(json.dumps(out,indent=2));print(json.dumps({'passed':len(results),'cases':[x['case']for x in results]}))
