"""Re-run upstream pure-Java helpers; requires an existing JDK and MotoNav checkout."""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True,type=Path);p.add_argument('--jdk',required=True,type=Path);a=p.parse_args()
with tempfile.TemporaryDirectory(prefix='motonav-classes-') as tmp:
 for name in ['CruiseIdleTimer','MapStylePolicy','WeatherArea']:
  subprocess.run([str(a.jdk/'bin/javac'),'-encoding','UTF-8','-d',tmp,str(a.repo/'android/app/src/main/java/com/example/motonav'/f'{name}.java'),str(a.repo/'android/tests'/f'{name}Test.java')],check=True)
  subprocess.run([str(a.jdk/'bin/java'),'-cp',tmp,'com.example.motonav.'+name+'Test'],check=True)
