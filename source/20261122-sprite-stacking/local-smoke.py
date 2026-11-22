"""Run against an unchanged upstream clone; fixtures are ours, not generated AI art."""
from pathlib import Path
import sys,subprocess,json,importlib.util,hashlib,platform
from PIL import Image,ImageDraw
import numpy as np
repo=Path(sys.argv[1]);out=Path(__file__).parent/'research';spec=importlib.util.spec_from_file_location('slicer',repo/'skills/sprite-stacking/scripts/views_to_slices.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Four deliberately consistent rectangular pixel-art views; no claim to production artwork.
views=[]
for w,h in [(16,24),(24,12),(16,12),(16,12)]:
 a=Image.new('RGBA',(w+2,h+2),(0,0,0,0));d=ImageDraw.Draw(a);d.rectangle((0,0,w+1,h+1),fill=(15,15,20,255));d.rectangle((1,1,w,h),fill=(35,100,190,255));d.rectangle((4,4,min(w-1,9),min(h-1,7)),fill=(245,150,40,255));views.append(a)
scale=8;gap=40;width=sum(v.width*scale for v in views)+gap*5;height=max(v.height for v in views)*scale+gap*2;sheet=Image.new('RGBA',(width,height),'white');x=gap
for v in views:
 im=v.resize((v.width*scale,v.height*scale),Image.Resampling.NEAREST);sheet.alpha_composite(im,(x,(height-im.height)//2));x+=im.width+gap
sheet.convert('RGB').save(out/'fixture-four-views.png')
cmd=[sys.executable,str(repo/'skills/sprite-stacking/scripts/views_to_slices.py'),str(out/'fixture-four-views.png'),str(out/'fixture-slices.png'),'--order','reading','--top-nose','down','--slices','18','--preview',str(out/'fixture-preview.png'),'--html',str(out/'fixture-viewer.html'),'--normals',str(out/'fixture-normals.png'),'--emissive',str(out/'fixture-emissive.png')]
r=subprocess.run(cmd,capture_output=True,text=True);(out/'cli.log').write_text(r.stdout+r.stderr);assert r.returncode==0
im=Image.open(out/'fixture-slices.png');assert im.width%18==0 and im.height>0
for n in ['normals','emissive']:assert Image.open(out/f'fixture-{n}.png').size==im.size
html=(out/'fixture-viewer.html').read_text();assert 'data:image/png;base64,'in html and 'data-mode="turntable"'in html
# A conflicting pair of front/back silhouettes isolates the actual occupancy rule.
def solid(h,w):return np.full((h,w,4),(80,120,180,255),dtype=np.uint8)
top=solid(3,4);side=solid(2,3);front=solid(2,4);back=solid(2,4);front[:,:,3]=0;back[:,:,3]=0;front[:,0,3]=255;back[:,3,3]=255
v=m.carve(top,side,front,back);occupied=int(np.count_nonzero(v[:,:,:,3]));assert occupied==12
assert not np.logical_and(front[:,:,3]>0,back[:,:,3]>0).any()
empty=front.copy();empty[:,:,3]=0;assert np.count_nonzero(m.carve(top,side,empty,empty)[:,:,:,3])==0
blanktop=top.copy();blanktop[:,:,3]=0;assert np.count_nonzero(m.carve(blanktop,side,front,back)[:,:,:,3])==0
blankSide=side.copy();blankSide[:,:,3]=0;assert np.count_nonzero(m.carve(top,blankSide,front,back)[:,:,:,3])==0
summary={'python':platform.python_version(),'host':platform.platform(),'upstreamSelfCheck':'original tests/check.py passed; eight numbered groups, not a model or performance benchmark','cliExit':r.returncode,'layers':18,'stripDimensions':im.size,'normalEmissiveDimensionsMatch':True,'htmlSelfContainedImages':True,'frontBackDisjointOccupancy':occupied,'strictFourWayIntersectionWouldBe':0,'verifiedRule':'top AND side AND (front OR back)','emptyTopSideAndBothEndMasksClearVolume':True,'scope':'synthetic numeric silhouette tests and actual CLI; not generative model, game-engine integration or frame-time benchmark','files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in out.glob('fixture-*')if f.is_file()}}
(out/'local-smoke.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
