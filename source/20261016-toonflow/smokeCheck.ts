import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const root='/tmp/toonflow-20261016',data='/tmp/toonflowSmokeData';
process.env.NODE_ENV='production';process.env.TOONFLOW_DATA_DIR=data;
await mkdir(resolve(data,'workspaces/checkProject'),{recursive:true});
const {createApp}=await import('/tmp/toonflow-20261016/apps/server/src/app.ts');
const app=await createApp({webRoot:resolve(root,'build/web'),dataDirectory:data,toolsRoot:resolve(root,'build/tools'),nodesRoot:resolve(root,'build/nodes'),extRoot:resolve(root,'build/ext'),providersRoot:resolve(root,'build/providers'),skillsRoot:resolve(root,'build/skills')});
const server=app.listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));
const address=server.address();if(!address||typeof address==='string')throw Error('No TCP address');const base='http://127.0.0.1:'+address.port;
const checks=[];
async function request(path,init={}){const res=await fetch(base+path,init);const text=await res.text();checks.push({path,status:res.status,body:text.slice(0,600)});if(res.status!==200)throw Error(path+' '+res.status+' '+text);return text;}
try{
 const html=await request('/');if(!html.includes('<html'))throw Error('Not HTML');
 const list=JSON.parse(await request('/api/workspaces/list'));if(!JSON.stringify(list).includes('checkProject'))throw Error('Missing workspace');
 const q=new URLSearchParams({directory:resolve(data,'workspaces/checkProject'),path:'shotNotes.txt'});
 const expected='Original fixture only: review reference images before generating video.\n';
 await request('/api/workspaces/files/write?'+q,{method:'PUT',headers:{'content-type':'application/octet-stream'},body:expected});
 const actual=await request('/api/workspaces/files/read?'+q);if(actual!==expected)throw Error('Round trip mismatch');
 await writeFile('/Users/jason/Dev/mycelium/blog/source/20261016-toonflow/local-smoke.json',JSON.stringify({runtime:Bun.version,sourcePin:'d2e94aca7b59659ff6b4ca15f03cf134ec7f0e1d',bind:'127.0.0.1 ephemeral',checks,roundTripEqual:true,modelsCalled:false,scope:'source createApp and built web/plugins; no production entry/MCP runtime initialization, GUI interaction or generation'},null,2));
 console.log('PASS: built HTML, workspace list, original text PUT/GET match; no model calls');
}catch(error){console.error(error);process.exitCode=1;}finally{server.close();process.exit(process.exitCode??0);}
