import argparse,json,sys,math,subprocess
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify a pinned OpenHoopVision checkout before running synthetic scoring checks.')
parser.add_argument('--source-dir',type=Path,required=True)
parser.add_argument('--expected-commit',default='9c000659a7d34ded894db90161c27cc0b55bb745')
args=parser.parse_args()
source=args.source_dir.expanduser().resolve(strict=True)
commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
if commit!=args.expected_commit:
 parser.error('source commit does not match expected revision; no code imported')
if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():
 parser.error('source checkout is not clean; no code imported')
sys.path.insert(0,str(source))
from events.scoring import shot_point_value,apply_shot_events_to_scoreboard
from tracking.court import COURT_GEOMETRY,COURT_LENGTH_M,COURT_WIDTH_M
cases=[]
def check(name,actual,expected):
 cases.append({'name':name,'actual':actual,'expected':expected,'passed':actual==expected})
check('under basket is two points',shot_point_value([1.6,7.62]),2)
check('outside left arc is three points',shot_point_value([10,7.62]),3)
check('near arc boundary remains uncertain',shot_point_value([8.84,7.62]),None)
check('corner three',shot_point_value([1,0.3]),3)
check('missing court coordinates stay unknown',shot_point_value(None),None)
check('out-of-court coordinates stay unknown',shot_point_value([-1,7]),None)
check('nonfinite court coordinates stay unknown',shot_point_value([math.nan,7]),None)
s={'dark':0,'light':0};e={'result':'made','team':'dark','points':3};apply_shot_events_to_scoreboard(s,[e,e]);apply_shot_events_to_scoreboard(s,[e]);check('same made-shot object applied once',s,{'dark':3,'light':0})
s={'dark':0,'light':0};pending=[];e={'result':'made','player_id':7,'points':3};apply_shot_events_to_scoreboard(s,[e],pending_events=pending);check('unknown team keeps score pending',(s.copy(),len(pending)),({'dark':0,'light':0},1));apply_shot_events_to_scoreboard(s,[],pending_events=pending,team_observations=[{'id':7,'team_semantic':'light'}]);check('later team observation resolves pending score',(s,len(pending)),({'dark':0,'light':3},0))
s={'dark':0,'light':0};apply_shot_events_to_scoreboard(s,[{'result':'miss','team':'dark','points':3}]);check('miss adds no points',s,{'dark':0,'light':0})
r={'sourceCommit':commit,'scope':'synthetic court coordinates and event dictionaries, no detector/weights/real video inference','geometry':{'lengthM':COURT_LENGTH_M,'widthM':COURT_WIDTH_M,'threePointRadiusM':COURT_GEOMETRY['three_point_radius_m']},'passed':sum(x['passed'] for x in cases),'failed':sum(not x['passed'] for x in cases),'cases':cases};Path(__file__).resolve().with_name('smoke-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['failed']==0
