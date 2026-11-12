from pathlib import Path
import json,hashlib,shutil,yaml
b=Path(__file__).resolve().parent
files=['analytics-README.md','analytics-LICENSE.md','analytics-extra-lib-license.ex','analytics-tracker-npm_package-LICENSE.md','community-edition-README.md','community-edition-LICENSE','community-edition-compose.yml']
# Enterprise source stays out of the published evidence bundle. Fetch pinned originals
# when reproducing the audit; preserve the upstream licensing boundaries.
import urllib.request
pins={k:json.loads((b/(k+'-metadata.json')).read_text())['pin'] for k in ['analytics','community-edition']}
paths={'analytics-README.md':('analytics','README.md'),'analytics-LICENSE.md':('analytics','LICENSE.md'),'analytics-extra-lib-license.ex':('analytics','extra/lib/license.ex'),'analytics-tracker-npm_package-LICENSE.md':('analytics','tracker/npm_package/LICENSE.md'),'community-edition-README.md':('community-edition','README.md'),'community-edition-LICENSE':('community-edition','LICENSE'),'community-edition-compose.yml':('community-edition','compose.yml')}
for name in files:
 if not (b/name).exists():
  repo,relative=paths[name]
  (b/name).write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/plausible/'+repo+'/'+pins[repo]+'/'+relative,timeout=30).read())
c=yaml.safe_load((b/'community-edition-compose.yml').read_text());services=c['services'];assert set(services)=={'plausible','plausible_db','plausible_events_db'}
assert services['plausible']['image']=='ghcr.io/plausible/community-edition:v3.2.1'
assert set(services['plausible']['depends_on'])=={'plausible_db','plausible_events_db'}
assert all(x['condition']=='service_healthy'for x in services['plausible']['depends_on'].values())
assert all(services[k]['volumes']for k in services) and c['volumes']
assert 'GNU AFFERO GENERAL PUBLIC LICENSE' in (b/'analytics-LICENSE.md').read_text()
assert 'MIT License' in (b/'community-edition-LICENSE').read_text()
assert 'MIT License' in (b/'analytics-tracker-npm_package-LICENSE.md').read_text()
assert 'No rights are granted' in (b/'analytics-extra-lib-license.ex').read_text()
r={'date':'2026-10-20','scope':'Pinned source and Compose structure review only. No runtime, throughput or business-income test.','dockerCLIAvailable':shutil.which('docker') is not None,'services':{k:{'image':v['image'],'persistentMounts':len(v.get('volumes',[])),'healthcheck':'healthcheck'in v,'publishedPorts':v.get('ports',[])} for k,v in services.items()},'applicationWaitsForBothHealthyDatabases':True,'licenseScopes':{'core':'AGPLv3-or-later','deploymentFiles':'MIT','trackerPackage':'MIT','enterpriseNotice':'Separate restricted-use notice, not blanket AGPL coverage'},'files':[{'path':f,'sha256':hashlib.sha256((b/f).read_bytes()).hexdigest()}for f in files]}
(b/'source-review.json').write_text(json.dumps(r,indent=2));print('Pinned files reviewed; 3 Compose services, persistent storage and healthy-database dependencies confirmed. Docker CLI available:',r['dockerCLIAvailable'])
