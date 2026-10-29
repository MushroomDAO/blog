import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createEngine} from '@relaycast/engine';
import {createNodeRuntime} from '@relaycast/engine/adapters/node';
const runtime=createNodeRuntime({dbPath:':memory:',baseUrl:'http://127.0.0.1',fileDir:'/tmp/agent-relay-smoke/files'});
const app=createEngine(runtime.deps), checks=[];
async function req(path,method='GET',body,token){
 const r=await app.request('http://127.0.0.1'+path,{method,headers:{'content-type':'application/json',...(token?{authorization:'Bearer '+token}:{})},...(body?{body:JSON.stringify(body)}:{})});
 const j=await r.json(); return {status:r.status,json:j};
}
try{
 const w=await req('/v1/workspaces','POST',{name:'isolated-demo'}); assert.equal(w.status,201);const key=w.json.data.api_key;assert.ok(key);checks.push('workspace created');
 const a=await req('/v1/agents','POST',{name:'alice'},key),b=await req('/v1/agents','POST',{name:'bob'},key);
 assert.equal(a.status,201);assert.equal(b.status,201);checks.push('two synthetic agents registered');
 const denied=await req('/v1/inbox');assert.equal(denied.status,401);checks.push('unauthenticated inbox refused with 401');
 const sent=await req('/v1/dm','POST',{to:'bob',text:'demo decision: use integer cents'},a.json.data.token);assert.equal(sent.status,201);
 console.log('SEND',JSON.stringify(sent.json));checks.push('DM accepted');
 const inbox=await req('/v1/inbox','GET',undefined,b.json.data.token);assert.equal(inbox.status,200);assert.ok(JSON.stringify(inbox.json).includes('demo decision: use integer cents'));checks.push('recipient inbox contains exact message');
 const empty=await req('/v1/inbox','GET',undefined,a.json.data.token);assert.equal(empty.status,200);checks.push('sender inbox accessible with its own token');
 const invalid=await req('/v1/dm','POST',{to:'bob',text:''},a.json.data.token);assert.equal(invalid.status,400);checks.push('empty DM refused with 400');
 console.log(JSON.stringify({engine:'12.2.1',node:process.version,checks,scope:'In-process Hono HTTP request handlers with real SQLite; no TCP/WebSocket, model sessions, cloud, external providers or performance test.'},null,2));
}finally{runtime.close();}
