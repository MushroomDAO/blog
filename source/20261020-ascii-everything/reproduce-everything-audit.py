"""Verify the app count and selected declarations at a fixed public revision."""
import json,urllib.request
pin='0fc4d361c1653bd29dcf96ff7e71eb8d9bab47a1';repo='HeyPuter/everything'
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MyceliumResearch'}),timeout=45).read().decode()
base=f'https://raw.githubusercontent.com/{repo}/{pin}/';tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{pin}?recursive=1'));assert not tree.get('truncated');apps=[x['path']for x in tree['tree']if x['type']=='blob'and x['path'].startswith('src/')and x['path'].count('/')==2 and x['path'].endswith('/package.json')];assert len(apps)==51
assert 'MIT License'in get(base+'LICENSE')
assert json.loads(get(base+'src/spreadsheet/package.json'))['license']=='AGPL-3.0-only'
assert 'GNU AFFERO GENERAL PUBLIC LICENSE'in get(base+'src/spreadsheet/LICENSE')
html=get(base+'src/spreadsheet/index.html');assert 'https://js.puter.com/v2/'in html and 'https://plausible.io/'in html
print('PASS:51app packages;rootMIT;spreadsheetAGPLpackage+LICENSE;PuterSDK and Plausible. Source audit only, not app runtime.')
