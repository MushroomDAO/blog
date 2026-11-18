from pathlib import Path
from PIL import Image
import io,shutil,json
root=Path('/Users/jason/Dev/mycelium/blog');sources=Path('/Users/jason/.codex/generated_images/01a1ed8b-81d9-7df1-b6c3-9ebc8dd8f3c6');names=['exec-85d49e9a-57e4-402c-a5ff-57333ff6a616.png','exec-8f4ddab9-4f49-41b9-bae3-6c68fc3721b7.png','exec-da026540-89dd-474b-86e8-920dbe399933.png'];dest=root/'assets/bifrost-ai-gateway-engineering-guide-illustrations';dest.mkdir(exist_ok=True,parents=True)
rows=[]
for i,n in enumerate(names,1):
 p=sources/n;shutil.copy2(p,dest/f'{i:02d}-original.png');im=Image.open(p).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
 px=list(im.getdata());im.putdata([(255,255,255) if min(c)>=250 else c for c in px])
 out=root/f'src/assets/images/bifrost-ai-gateway-engineering-guide-fig-{i:02d}.png'
 for colors in [128,96,80,64,48,32,16,8]:
  q=im.quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);b=io.BytesIO();q.save(b,format='PNG',optimize=True)
  if len(b.getvalue())<90000:out.write_bytes(b.getvalue());break
 else:raise ValueError('too large')
 rows.append({'file':out.name,'bytes':out.stat().st_size,'palette':colors,'dimensions':[1280,720],'dither':'none','nearWhiteThreshold':250})
(root/'source/20261118-bifrost/body-image-sizes.json').write_text(json.dumps(rows,indent=2));print(rows)
