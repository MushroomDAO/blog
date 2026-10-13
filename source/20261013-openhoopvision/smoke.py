import json,sys,math
from pathlib import Path
sys.path.insert(0,'/tmp/openhoopvision-20261013')
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
r={'sourceCommit':'9c000659a7d34ded894db90161c27cc0b55bb745','scope':'synthetic court coordinates and event dictionaries, no detector/weights/real video inference','geometry':{'lengthM':COURT_LENGTH_M,'widthM':COURT_WIDTH_M,'threePointRadiusM':COURT_GEOMETRY['three_point_radius_m']},'passed':sum(x['passed'] for x in cases),'failed':sum(not x['passed'] for x in cases),'cases':cases};Path('/Users/jason/Dev/mycelium/blog/source/20261013-openhoopvision/smoke-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['failed']==0
