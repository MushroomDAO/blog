"""One-shot service reload, only after the current reply and all CLI work finish."""
from pathlib import Path
import datetime,json,sqlite3,subprocess,time,os
BASE=Path(__file__).resolve().parent
DB=Path('/Users/jason/.heinu1-bot/sessions.db')
JOB='43c77f86-7274-4f68-993a-60394ca5986c'
CTL='/Users/jason/Dev/tools/Heinu1/bot/ctl.sh'

def state(status,**extra):
 (BASE/'reload-status.json').write_text(json.dumps({'status':status,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra},ensure_ascii=False,indent=2)+'\n')

def idle():
 with sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True) as db:
  job=db.execute('SELECT status FROM workflow_jobs WHERE id=?',(JOB,)).fetchone()
  busy=db.execute("SELECT count(*) FROM workflow_jobs WHERE status IN ('running','pending')").fetchone()[0]
  outbox=db.execute("SELECT count(*) FROM reply_outbox WHERE status='pending'").fetchone()[0]
 if not job or job[0]!='complete' or busy or outbox:return False
 ps=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True)
 rows=[]
 for line in ps.splitlines():
  parts=line.strip().split(None,2)
  if len(parts)==3:rows.append((int(parts[0]),int(parts[1]),parts[2]))
 bot={pid for pid,_,cmd in rows if '/Heinu1/bot/src/main.ts' in cmd}
 descendants=set(bot)
 while True:
  nxt=descendants|{pid for pid,parent,_ in rows if parent in descendants}
  if nxt==descendants:break
  descendants=nxt
 # CLI execution anywhere is treated as busy; all bot child commands also block.
 if any(('codex exec' in cmd or '/codex exec' in cmd or 'claude -p' in cmd) for pid,_,cmd in rows if pid!=os.getpid()):return False
 if descendants-bot:return False
 return True

state('waiting-for-current-reply',newPollerStarted=False)
deadline=time.monotonic()+3600
while time.monotonic()<deadline:
 if idle():
  time.sleep(10)
  if idle():
   state('restarting-after-idle',newPollerStarted=False)
   result=subprocess.run(['bash',CTL,'restart'],capture_output=True,text=True,timeout=60)
   # ctl output contains only operational status; never copy bot logs or secrets.
   (BASE/'reload-command.log').write_text(result.stdout+'\n'+result.stderr)
   state('reloaded' if result.returncode==0 else 'reload-failed',exitCode=result.returncode)
   break
 time.sleep(5)
else:state('deferred-timeout',reason='No safe idle window; service not restarted.')
