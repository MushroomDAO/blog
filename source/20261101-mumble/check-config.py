"""Static check of the article's compose sample; does not start containers."""
from pathlib import Path
import json,re,yaml,hashlib,datetime
root=Path(__file__).resolve().parents[2]
s=Path(__file__).resolve().parent
raw=(s/'compose.yaml').read_text();config=yaml.safe_load(raw);service=config['services']['mumble']
checks={
 'fixedOfficialImage':service['image']=='ghcr.io/mumble-voip/mumble-server:v1.5.939',
 'tcpAndUdp':set(service['ports'])=={'64738:64738/tcp','64738:64738/udp'},
 'persistentNamedVolume':service['volumes']==['mumble-data:/data'] and 'mumble-data'in config['volumes'],
 'distinctRequiredSecrets':service['environment']['MUMBLE_CONFIG_SERVER_PASSWORD'].startswith('${MUMBLE_JOIN_PASSWORD:?') and service['environment']['MUMBLE_SUPERUSER_PASSWORD'].startswith('${MUMBLE_ADMIN_PASSWORD:?'),
 'exampleLimit':service['environment']['MUMBLE_CONFIG_USERS']=='20',
 'adminNotPublished':not any('6502'in p for p in service['ports']),
 'articleMatchesBothLanguages':(root/'src/content/blog/mumble-phone-walkie-talkie-guide.md').read_text().count(raw.strip())==2,
}
manifest=json.loads((s/'image-manifest.json').read_text());checks['registryTagAndPlatforms']=manifest['image']==service['image'] and any(x.get('architecture')=='arm64'for x in manifest['platforms'])
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':all(checks.values()),'checks':checks,'composeSha256':hashlib.sha256(raw.encode()).hexdigest(),'runtimeStarted':False,'limits':['NoDocker/Podmanlocally;notdockercomposeconfigorstart','NoTCP/UDPconnectionattempt','Nophone/Bluetooth/lockscreen/audio/latencytest']}
(s/'config-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['passed']
