from pathlib import Path
import json,dataclasses,math
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
import indra_ocr,onnx
from onnx import numpy_helper
out=Path('/tmp/indra-ocr-smoke-20261015');out.mkdir(exist_ok=True)
models=Path('/tmp/indra-ocr-models-20261015')
lines=['Invoice INV-2026-1015','Customer: Example Research Team','Description: CPU OCR smoke test','Quantity: 5','Unit price: USD 25.10','Total: USD 125.50','Payment due: 2026-10-31','Keep this document for internal verification.','Printed text only. No handwriting or complex tables.','Reference: SAMPLE-0007','Contact: sample@example.invalid','End of controlled test document.']
pdf=out/'controlled-invoice.pdf';c=canvas.Canvas(str(pdf),pagesize=(612,792));c.setFont('Helvetica',14)
for i,s in enumerate(lines):c.drawString(50,740-i*28,s)
c.save()
im=Image.new('RGB',(1000,600),'white');draw=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',44)
for i,s in enumerate(['文档识别测试','发票号码：20261015','合计金额：125.50元','这是清晰印刷体测试页面。']):draw.text((70,75+i*105),s,font=font,fill='black')
scan=out/'controlled-chinese.png';im.save(scan)
results=[]
for mode,file in [('auto',pdf),('ocr',pdf),('ocr',scan)]:
 conv=indra_ocr.load(path=models,threads=2,mode=mode,providers=['CPUExecutionProvider'])
 for i,page in conv.convert(file):
  row={'file':file.name,'mode':mode,'pageIndex':i,**dataclasses.asdict(page),'text':page.text}
  assert page.source!='error' and page.lines and page.blocks and page.markdown
  assert all(len(l.box)==4 and all(math.isfinite(float(v)) for v in l.box) and l.box[0]<=l.box[2] and l.box[1]<=l.box[3] for l in page.lines)
  assert all(len(b['bbox'])==4 and b.get('label') for b in page.blocks)
  if file==pdf:assert '125.50' in page.text and '2026' in page.text
  else:assert '20261015' in page.text and '125.50' in page.text and '文档' in page.text
  assert page.source==('text' if mode=='auto' else 'ocr')
  (out/f'{file.stem}-{mode}.json').write_text(json.dumps(row,ensure_ascii=False,indent=2));results.append({'file':file.name,'mode':mode,'source':page.source,'lines':len(page.lines),'blocks':len(page.blocks),'text':page.text,'boxesFiniteOrdered':True,'markdownPresent':bool(page.markdown)})
model_inventory=[]
for p in sorted(models.glob('*.onnx')):
 g=onnx.load(str(p));model_inventory.append({'file':p.name,'bytes':p.stat().st_size,'initializerElements':sum(numpy_helper.to_array(t).size for t in g.graph.initializer)})
r={'codeCommit':'3d773aeedc5d79d1d0a2a04007a9075cd71a59f4','modelRevision':'ed345c7f158eddbc7dee0c6a7269afb75a94f7e8','packageVersion':indra_ocr.__version__,'provider':'CPUExecutionProvider','threads':2,'hardware':'M4 16GB','cases':results,'models':model_inventory,'scope':'Two original controlled fixtures, English PDF auto and forcedOCR plus Chinese rasterOCR. No throughput/latency/ranking benchmark, no complex table/math/handwriting coverage.'}
Path('/Users/jason/Dev/mycelium/blog/source/20261015-indra-ocr/smoke-result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False,indent=2))
