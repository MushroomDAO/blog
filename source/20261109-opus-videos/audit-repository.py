from pathlib import Path
import json,collections,re,hashlib,sys
from urllib.parse import urlparse
root=Path(sys.argv[1]).resolve();rows=json.loads((root/'data/videos.json').read_text());files=list((root/'prompts').glob('*.md'));slugs=[r['slug']for r in rows];missing=[];empty=[];bad_urls=[];partial_codes=[];mismatch=[]
for r in rows:
 p=root/'prompts'/f"{r['slug']}.md"
 if not p.is_file():missing.append(r['slug']);continue
 t=p.read_text();blocks=[t.split('```text\n',1)[1].rsplit('\n```',1)[0]] if '```text\n' in t else []
 if not blocks or not blocks[0].strip():empty.append(r['slug'])
 if blocks and blocks[0].strip()!=r['prompt'].replace('\\n','\n').strip():mismatch.append(r['slug'])
 for k in ['post_url','author_url','poster_url','skillry_url']:

  if not r[k] and k=='skillry_url' and not r['has_remake']:continue
  u=urlparse(r[k])
  if u.scheme!='https' or not u.netloc:bad_urls.append([r['slug'],k])
 if r['prompt_partial']:partial_codes.append(r['slug'])
report={'revision':__import__('subprocess').check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'rows':len(rows),'promptFiles':len(files),'categories':dict(collections.Counter(r['category']for r in rows)),'hasRemake':sum(bool(r['has_remake'])for r in rows),'partialMarked':len(partial_codes),'notPartialMarked':sum(not r['prompt_partial']for r in rows),'uniqueSlugs':len(set(slugs)),'missingFiles':missing,'missingPromptBlocks':empty,'invalidHttpsMetadata':bad_urls,'promptJsonMarkdownMismatchesAfterNewlineNormalization':mismatch,'latestAdded':max(r['added']for r in rows),'suffixCounts':dict(collections.Counter(p.suffix or '(none)' for p in root.rglob('*')if p.is_file()and'.git'not in p.parts)),'techTagsOverlapping':dict(collections.Counter(t for r in rows for t in r['tech_tags'])),'dataSha256':hashlib.sha256((root/'data/videos.json').read_bytes()).hexdigest(),'scope':'Read-only metadata and prompt-file structure audit; not visual review, model attribution, link liveness, generation success, or rights verification.'}
print(json.dumps(report,ensure_ascii=False,indent=2));assert not(missing or empty or bad_urls);assert len(slugs)==len(set(slugs))
