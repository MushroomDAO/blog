const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),http=require('node:http'),{spawn}=require('node:child_process'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function session(flags,url,run){
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'webmcp-browser-')),p=spawn(chrome,['--headless=new','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--no-first-run','--window-size=1280,900',...flags,'about:blank'],{stdio:'ignore'});let ws;
 try{const portfile=path.join(profile,'DevToolsActivePort');for(let n=0;!fs.existsSync(portfile);n++){if(n>150)throw Error('Chrome timeout');await sleep(100)}
 const port=fs.readFileSync(portfile,'utf8').split('\n')[0],targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let id=0;const pending=new Map(),errors=[];
 ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const q=pending.get(m.id);if(q){pending.delete(m.id);m.error?q.reject(Error(m.error.message)):q.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url});for(let n=0;!(await evaluate('typeof window.demoReady!=="undefined"'));n++){if(n>150)throw Error('Page timeout');await sleep(100)}
 const available=await evaluate('window.demoReady'),probe=await evaluate('({secure:isSecureContext,documentAPI:!!document.modelContext,navigatorAPI:!!navigator.modelContext,methods:document.modelContext?Object.getOwnPropertyNames(Object.getPrototypeOf(document.modelContext)):[]})');
 const result=await run({evaluate,send,available,probe});assert.equal(errors.length,0,JSON.stringify(errors));return {flags,available,probe,errors,...result};
 }finally{ws?.close();p.kill();await sleep(300);fs.rmSync(profile,{recursive:true,force:true})}
}
(async()=>{const file=path.join(root,'public/demos/webmcp-readonly/index.html'),server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(fs.readFileSync(file));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{const url=process.env.WEBMCP_DEMO_URL || `http://127.0.0.1:${server.address().port}/`;const baseline=await session([],url,async({evaluate})=>{await evaluate('document.querySelector("#lookup-form button").click()');return {manual:await evaluate('document.querySelector("#result").textContent')}});
 const preview=await session(['--enable-features=WebMCP,WebMCPTesting','--enable-blink-features=WebMCP,WebMCPTesting'],url,async({evaluate,send,available})=>{
 if(!available.available||available.error)throw Error(JSON.stringify(available));
 await evaluate('document.querySelector("#lookup-form button").click()');const manual=JSON.parse(await evaluate('document.querySelector("#result").textContent'));assert.equal(manual.stock,8);
 const list=await evaluate('(async()=> (await document.modelContext.getTools()).map(t=>({name:t.name,inputSchema:t.inputSchema,annotations:t.annotations})))()');
 const lookup=await evaluate('(async()=> {const t=(await document.modelContext.getTools()).find(t=>t.name==="lookup_demo_stock"); return await document.modelContext.executeTool(t,{sku:"demo-b"});})()');assert.equal(JSON.parse(lookup).stock,3);
 const invalid=await evaluate('(async()=>{try{const t=(await document.modelContext.getTools()).find(t=>t.name==="lookup_demo_stock");await document.modelContext.executeTool(t,{sku:"unknown"});return {rejected:false}}catch(e){return {rejected:true,error:e.name}}})()');assert(invalid.rejected);
 const duplicate=await evaluate('(async()=>{try{await document.modelContext.registerTool(window.demo.tool);return {rejected:false}}catch(e){return {rejected:true,error:e.name}}})()');assert(duplicate.rejected);
 await evaluate('document.querySelector("#invoke").click()');await sleep(300);const screenshot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(__dirname,(process.env.WEBMCP_RESULT_PREFIX||'demo')+'-preview.png'),Buffer.from(screenshot.data,'base64'));
 await evaluate('window.demo.dispose()');await sleep(100);const after=await evaluate('(async()=> (await document.modelContext.getTools()).map(t=>t.name))()');assert(!after.includes('lookup_demo_stock'));
 await evaluate('window.demo.register()');const again=await evaluate('(async()=> (await document.modelContext.getTools()).map(t=>t.name))()');assert(again.includes('lookup_demo_stock'));
 return {manual,tools:list,lookup,invalid,duplicate,afterAbort:after,afterReregister:again};});
 const result={checkedAt:new Date().toISOString(),browser:require('node:child_process').execFileSync(chrome,['--version'],{encoding:'utf8'}).trim(),baseline,preview,scope:'Native read-only browser demo. No LLM, production business system, timing/cost benchmark, extension or daily browser profile change.'};fs.writeFileSync(path.join(__dirname,(process.env.WEBMCP_RESULT_PREFIX?process.env.WEBMCP_RESULT_PREFIX+'-':'')+'browser-verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{server.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
