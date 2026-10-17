from pathlib import Path
import json,collections,statistics,hashlib
p=Path(__file__).parent/'kinex-episodes.jsonl'; rows=[json.loads(l) for l in p.read_text().splitlines()];groups=collections.defaultdict(list)
for r in rows:groups[r['case']].append(r)
out={'datasetSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'episodes':len(rows),'groups':{}}
for k,rs in groups.items():out['groups'][k]={'n':len(rs),'success':sum(r['success'] for r in rs),'meanCostUSD':statistics.mean(r['costLow'] for r in rs),'environments':dict(collections.Counter(r['environment'] for r in rs))}
(Path(__file__).parent/'kinex-recomputed.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
