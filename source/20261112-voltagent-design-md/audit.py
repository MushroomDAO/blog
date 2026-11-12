from pathlib import Path
import json,subprocess,datetime
repo=Path('/tmp/voltagent-design-research-20261112');docs=sorted((repo/'design-md').glob('*/DESIGN.md'));previews=list((repo/'design-md').glob('*/preview*.html'));s=(repo/'design-md/linear.app/DESIGN.md').read_text()
def lum(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];a=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in a];return sum(x*w for x,w in zip(a,[.2126,.7152,.0722]))
def contrast(a,b):
 x,y=sorted([lum(a),lum(b)]);return(y+.05)/(x+.05)
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'designDocuments':len(docs),'previewHtmlFiles':len(previews),'linear':{'bytes':len(s.encode()),'alpha':'version: alpha' in s,'knownGaps':'## Known Gaps' in s,'primaryOnWhiteContrast':contrast('#5e6ad2','#ffffff'),'mutedOnCanvasContrast':contrast('#62666d','#010102')},'scope':'Static checkout inventory and arithmetic on documented sRGB tokens, not site fidelity, rendering quality, accessibility conformance or model generation performance.'}
Path(__file__).with_name('audit-results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
