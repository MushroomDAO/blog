"""Exercise unmodified Sherlock against synthetic loopback HTTP responses only."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import json
from sherlock_project.sherlock import sherlock
from sherlock_project.notify import QueryNotify

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_HEAD(self): self.respond(False)
    def do_GET(self): self.respond(True)
    def respond(self,body):
        key=self.path.split('/')[1]
        status,text={'ok':(200,'profile'), 'missing':(404,'absent'), 'soft404':(200,'user absent'), 'genericlogin':(200,'please log in'), 'redirect':(302,''), 'waf':(403,'<span id="challenge-error-text">'), 'blocked':(403,'access denied'), 'limited':(429,'rate limited')}[key]
        self.send_response(status)
        if status==302:self.send_header('Location','/genericlogin/demo')
        self.end_headers()
        if body:self.wfile.write(text.encode())
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
def spec(endpoint,mode,**kwargs):return {'urlMain':base,'url':base+'/'+endpoint+'/{}','errorType':mode,**kwargs}
sites={
 'status_ok':spec('ok','status_code'),
 'status_404':spec('missing','status_code'),
 'message_soft404':spec('soft404','message',errorMsg='user absent'),
 'unrecognized_login':spec('genericlogin','message',errorMsg='user absent'),
 'redirect_302':spec('redirect','response_url'),
 'known_waf':spec('waf','message',errorMsg='user absent'),
 'generic_403':spec('blocked','status_code'),
 'generic_429':spec('limited','status_code'),
 'illegal_username':spec('ok','status_code',regexCheck=r'^digits[0-9]+$'),
}
expected={'status_ok':'Claimed','status_404':'Available','message_soft404':'Available','unrecognized_login':'Claimed','redirect_302':'Available','known_waf':'WAF','generic_403':'Available','generic_429':'Available','illegal_username':'Illegal'}
try:
 result=sherlock('demo',sites,QueryNotify(),timeout=3)
 actual={k:str(v['status'].status) for k,v in result.items()}
 assert actual==expected,(actual,expected)
 out={'scope':'Synthetic loopback fixtures; no real social account enumeration; not a performance or accuracy benchmark','checks':len(expected),'results':actual,'false_positive_demonstration':'Generic login page without configured error text becomes Claimed','false_negative_demonstration':'Unrecognized HTTP 403 or 429 status_code fixture becomes Available; this does not prove absence'}
 Path(__file__).with_name('local-http-audit-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
finally:server.shutdown();server.server_close()
