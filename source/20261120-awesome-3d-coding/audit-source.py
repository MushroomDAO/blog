from pathlib import Path
import re,json,hashlib,urllib.request,datetime
p=Path(__file__).parent;r=p/'research';s=(r/'README.md').read_text();section='';rows={}
for line in s.splitlines():
 if line.startswith('## '):section=line
 if line.startswith('| **'):rows[section]=rows.get(section,0)+1
sources=[('3dcodebench','https://raw.githubusercontent.com/gaoypeng/3dcodebench/main/README.md'),('cadtestbench','https://raw.githubusercontent.com/dimitrismallis/CADTestBench/main/README.md'),('worldcoder','https://raw.githubusercontent.com/shuolucs/WorldCoder-Bench/main/README.md'),('3dcodeverse-dataset','https://huggingface.co/datasets/3dcodeverse/3dcodeverse-2m/raw/main/README.md')]
checks=[]
for name,url in sources:
 try:
  q=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mycelium-Research'}),timeout=35);data=q.read();(Path('/Users/jason/.heinu1-bot/jobs/2a394977-41d1-4814-b4d4-59dfdc13ec50/research')/(name+'-README.md')).write_bytes(data);checks.append({'source':url,'status':q.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 except Exception as e:checks.append({'source':url,'error':str(e)})
report={'revision':'69b232ad5697032f860157a8125ee7e5ba1cdc51','countUnit':'Markdown data rows beginning | **, grouped by H2, not unique papers or runnable projects','counts':rows,'totalRows':sum(rows.values()),'sourceChecks':checks,'benchmarkExecuted':False,'allLinksChecked':False,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};(p/'source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
