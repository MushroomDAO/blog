from pathlib import Path
import tempfile,json,os,subprocess,shutil,sys
repo=Path('/tmp/skill2env-allspark-20261112');tasks=repo/'Skill2Env/tasks';rows=[]
for p in sorted(tasks.iterdir()):
 if not p.is_dir():continue
 j=json.loads((p/'tests/eval_spec.json').read_text());items=j['rubric'];rows.append({'task':p.name,'rubricItems':len(items),'weightSum':sum(x['weight']for x in items),'judgeRequired':any(x['method']=='llm_judge'for x in items),'requiredArtifactsPresent':all((p/x).exists()for x in ['instruction.md','task.toml','environment/Dockerfile','environment/workspace/_skill_ref/SKILL.md','tests/run_verifier.py','tests/verify.py'])})
with tempfile.TemporaryDirectory(prefix='skill2env-contract-')as d:
 tmp=Path(d);task=tasks/'context-slimming';shutil.copytree(task/'environment/workspace',tmp/'workspace');env=os.environ.copy()
 for k in ['JUDGE_BASE_URL','JUDGE_MODEL','JUDGE_API_KEY']:env.pop(k,None)
 env['VERIFIER_LOG_DIR']=str(tmp/'logs');p=subprocess.run([sys.executable,str(task/'tests/run_verifier.py')],cwd=tmp/'workspace',env=env,capture_output=True,text=True,timeout=30);negative={'exitCode':p.returncode,'stderr':p.stderr.strip(),'error':json.loads((tmp/'logs/error.json').read_text()),'rewardFileExists':(tmp/'logs/reward.txt').exists()};assert p.returncode==1 and not negative['rewardFileExists'] and 'JUDGE_BASE_URL'in p.stderr
r={'sourceRevision':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'tasks':rows,'totals':{'tasks':len(rows),'hybrid':sum(x['judgeRequired']for x in rows),'deterministic':sum(not x['judgeRequired']for x in rows)},'missingJudgeSmoke':negative,'scope':'Actual released verifier entry point on copied initial workspace with judge configuration intentionally absent. No solver, judge API, Docker environment, task generation, training or benchmark executed.'};Path(__file__).with_name('audit-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items()if k!='tasks'},ensure_ascii=False))
