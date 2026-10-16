"""Recheck source/APK metadata without installing or executing Android code.
Usage: python3 inspect-release.py SOURCE_DIR APK_PATH
"""
import hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
source,apk=map(Path,sys.argv[1:3])
build=(source/'scripts/build.sh').read_text();profiles=json.loads((source/'app/src/main/assets/profiles.json').read_text())
subprocess.run(['bash','-n',str(source/'scripts/build.sh'),str(source/'scripts/build-verify.sh')],check=True)
subprocess.run(['node','--check',str(source/'app/src/main/assets/app.js')],check=True)
with zipfile.ZipFile(apk) as archive:
 assert archive.testzip() is None
 assets=json.loads(archive.read('assets/profiles.json'))
 script=archive.read('assets/app.js').decode()
 subprocess.run(['node','--check'],input=script,text=True,check=True)
 result={'sourceBuildVersion':re.search(r'^VN=(.+)$',build,re.M)[1],'sourceProfiles':list(profiles['profiles']),'apkJsVersion':re.search(r'APP_VER="([^"]+)"',script)[1],'apkProfiles':list(assets['profiles']),'apkBytes':apk.stat().st_size,'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'zipCrc':'passed','syntax':'bash and node passed','scope':'No Android/native execution or inference'}
print(json.dumps(result,indent=2))
