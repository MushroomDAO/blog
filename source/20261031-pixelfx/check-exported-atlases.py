# Run after reproduce-checks.sh, from a pinned pixelfx checkout. Requires Pillow.
from pathlib import Path
from PIL import Image
import json, hashlib
reports=[]
for ident in ['ice/frost-nova','melee/sword-slash','fire/torch']:
    p=Path('records')/ident
    name=ident.split('/')[1]
    m=json.loads((p/(name+'.json')).read_text())
    image=Image.open(p/(name+'.png')).convert('RGBA')
    alpha=image.getchannel('A').getextrema()
    assert alpha[0]==0 and alpha[1]>0
    assert len(m['frames'])==m['meta']['pixelfx']['frames']
    assert list(image.size)==[m['meta']['size']['w'],m['meta']['size']['h']]
    reports.append({'id':ident,'frames':len(m['frames']),'size':image.size,'alpha':alpha,
                    'sha256':hashlib.sha256((p/(name+'.png')).read_bytes()).hexdigest()})
print(json.dumps(reports,indent=2))
