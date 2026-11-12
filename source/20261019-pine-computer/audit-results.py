"""Recompute published result records; does not execute tasks or verify private traces."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json
b=Path(__file__).resolve().parent
names={'results.jsonl':'hf-results.jsonl','summary.json':'hf-summary.json','methodology.md':'hf-methodology.md','evidence-index.jsonl':'hf-evidence-index.jsonl'}
manifest={line.split(None,1)[1].strip().lstrip('*'):line.split(None,1)[0] for line in (b/'hf-SHA256SUMS.txt').read_text().splitlines() if line.strip()}
verified={}
for remote,local in names.items():
 key='releases/2026-09-18-saas-bench-1.1/'+remote
 actual=hashlib.sha256((b/local).read_bytes()).hexdigest();assert actual==manifest[key],(key,actual);verified[key]=actual
rows=[json.loads(x) for x in (b/'hf-results.jsonl').read_text().splitlines() if x.strip()];summary=json.loads((b/'hf-summary.json').read_text());assert len(rows)==106 and len({x['task_id'] for x in rows})==106
assert all(x['valid'] and x['accepted'] and 0<=x['checks_passed']<=x['checks_total'] for x in rows)
passed=sum(x['checks_passed'] for x in rows);total=sum(x['checks_total'] for x in rows);resolved=sum(x['fully_resolved'] for x in rows)
assert all(x['fully_resolved']==(x['checks_passed']==x['checks_total']) for x in rows)
assert (passed,total,resolved)==(1077,1375,29)
assert summary['metrics']['checks_passed']==passed and summary['metrics']['checks_total']==total
attempts=Counter(x['attempt'] for x in rows);reasons=Counter(x['terminal_reason'] for x in rows);domains={}
for domain in sorted({x['domain'] for x in rows}):
 d=[x for x in rows if x['domain']==domain];domains[domain]={'tasks':len(d),'checks_passed':sum(x['checks_passed'] for x in d),'checks_total':sum(x['checks_total'] for x in d),'resolved':sum(x['fully_resolved'] for x in d)}
evidence=[json.loads(x) for x in (b/'hf-evidence-index.jsonl').read_text().splitlines() if x.strip()];assert len(evidence)==106
out={'dataset':'pine-ai/pine-computer-saasbench-results','revision':'bd9df2a8a140f30bf67e4c4409e9323b579d2577','publishedFilesSHA256Matched':verified,'acceptedRecords':len(rows),'uniqueTasks':106,'checksPassed':passed,'checksTotal':total,'checkpointPercent':passed/total*100,'resolvedTasks':resolved,'resolvedPercent':resolved/len(rows)*100,'acceptedAttemptNumbers':dict(attempts),'terminalReasons':dict(reasons),'meanWeightedScorePercent':sum(x['score'] for x in rows)/len(rows)*100,'domains':domains,'publicEvidenceIndexRecords':len(evidence),'privateRawEvidenceVerified':False,'tasksReexecuted':False,'hostedAPIInvoked':False,'costIndependentlyRecomputed':False}
(b/'result-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ['acceptedRecords','checkpointPercent','resolvedPercent','acceptedAttemptNumbers','terminalReasons','meanWeightedScorePercent']},indent=2))
