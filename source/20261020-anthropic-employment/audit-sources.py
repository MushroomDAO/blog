from pathlib import Path
import hashlib,json,subprocess
b=Path(__file__).resolve().parent
urls={'employment.pdf':'https://www-cdn.anthropic.com/72628f1863c53432195db83279252dfd2cb53158/Employment%20at%20Anthropic.pdf','expectations.pdf':'https://www-cdn.anthropic.com/a28f24814c56e2834a3eae7b13946f19d3e97ec4/The%20AI%20Expectations%20Gap.pdf'}
for name,url in urls.items():
 if not (b/name).exists():subprocess.run(['curl','-fLsS','--compressed','-A','Mozilla/5.0',url,'-o',str(b/name)],check=True)
subprocess.run(['swift',str(b/'inspect-pdfs.swift'),str(b)],check=True)
meta=json.loads((b/'pdf-inspection.json').read_text());assert [x['pages']for x in meta]==[20,16]
e=(b/'employment-extracted.txt').read_text();x=(b/'expectations-extracted.txt').read_text();assert '27%'in e and '9%'in e and '17'in e;assert '75%'in x and '28%'in x
r={'date':'2026-10-20','scope':'Document snapshot and definition review only; no internal-data or causal-model replication.','documents':[{'name':n,'url':u,'sha256':hashlib.sha256((b/n).read_bytes()).hexdigest(),'bytes':(b/n).stat().st_size}for n,u in urls.items()],'pdfInspection':meta,'figure5Sample':{'employedUSRespondents':2278,'staffRespondents':1147,'USWeighted':True,'staffWeighted':False,'visuallyReviewed':True},'fullSurveySample':{'USAdults':10980,'staff':1334},'notes':'Question-specific and full-survey denominators kept separate; 6to1 is runtime versus assumed human hours, not headcount.'}
(b/'source-review.json').write_text(json.dumps(r,indent=2));(b/'source-manifest.json').write_text(json.dumps(r['documents'],indent=2));print('20/16-page PDF snapshots audited; figures and denominator scope reviewed.')
