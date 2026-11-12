from pathlib import Path
import subprocess,json,plistlib,hashlib,platform
b=Path('source/20261019-agentear');dmg=b/'AgentEar-0.27.0-preview.20261015.1-macos26-arm64.dmg';app=Path('/Volumes/AgentEar Preview ARM64 macOS26/AgentEar.app')
info=plistlib.loads((app/'Contents/Info.plist').read_bytes());materials=json.loads((app/'Contents/Resources/CORE-MATERIALS.json').read_text());(b/'bundle-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2,default=str));(b/'core-materials.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2));(b/'bundle-NOTICE.txt').write_text((app/'Contents/Resources/NOTICE').read_text())
cmds={'file':['file',str(app/'Contents/MacOS/AgentEar')],'app_signature':['codesign','--verify','--deep','--strict','--verbose=1',str(app)],'signature_details':['codesign','-dv','--verbose=4',str(app)],'dmg_gatekeeper':['spctl','-a','-t','open','--context','context:primary-signature','-v',str(dmg)],'app_stapler':['xcrun','stapler','validate',str(app)],'dmg_stapler':['xcrun','stapler','validate',str(dmg)]}
r={'hostMacOS':platform.mac_ver()[0],'sha256':hashlib.sha256(dmg.read_bytes()).hexdigest(),'bytes':dmg.stat().st_size,'expectedSHA256':'f6c16a8966ba90081a514e093759878071399ed3524e1e502e65ab650547d270','tests':{},'executedApp':False,'microphoneAccessed':False,'modelsDownloaded':False}
for name,cmd in cmds.items():
 try:
  x=subprocess.run(cmd,text=True,capture_output=True,timeout=40);r['tests'][name]={'returncode':x.returncode,'stdout':x.stdout,'stderr':x.stderr}
 except Exception as e:r['tests'][name]={'error':str(e)}
assert r['sha256']==r['expectedSHA256'];(b/'package-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False,indent=2));subprocess.run(['hdiutil','detach',str(app.parent)],check=True)
