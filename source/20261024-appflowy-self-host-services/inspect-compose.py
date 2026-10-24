"""Inspect the public Compose manifest without interpolation or service startup."""
from pathlib import Path
import yaml,json,sys
p=Path(sys.argv[1]);d=yaml.safe_load(p.read_text())
print(json.dumps({'scope':'YAML parse only; no Docker installation, image pull, deployment or restore','services':[{'name':n,'image':v.get('image'),'ports':v.get('ports',[]),'profiles':v.get('profiles',[])}for n,v in d['services'].items()]},indent=2))
