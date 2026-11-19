from pathlib import Path
from PIL import Image
import io,shutil,json
root=Path(__file__).resolve().parents[2];slug='organizing-intelligence-ai-jobs-wages-coordination';backup=root/'assets/organizing-intelligence-ai-jobs-wages-coordination-illustrations';backup.mkdir(exist_ok=True,parents=True);rows=[]
for i in range(1,4):
 dest=root/f'src/assets/images/{slug}-fig-{i:02d}.png';raw=backup/f'fig-{i:02d}-original.png'
 if not raw.exists():shutil.copy2(dest,raw)
 im=Image.open(raw).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS);im.putdata([(255,255,255)if min(c)>=250 else c for c in im.getdata()])
 for colors in [128,96,80,64,48,32,16,8]:
  q=im.quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);buf=io.BytesIO();q.save(buf,format='PNG',optimize=True)
  if len(buf.getvalue())<90000:dest.write_bytes(buf.getvalue());break
 else:raise ValueError('cannot compress')
 rows.append({'file':dest.name,'bytes':dest.stat().st_size,'dimensions':[1280,720],'palette':colors,'dither':'none','nearWhiteThreshold':250})
Path(__file__).with_name('body-image-sizes.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
