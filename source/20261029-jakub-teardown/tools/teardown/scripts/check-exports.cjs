#!/usr/bin/env node
const fs = require('node:fs'), os = require('node:os'), path = require('node:path'), {spawn} = require('node:child_process');
const {findChrome} = require('./commands.cjs');

const TIMEOUT = 60000;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function connect(profile) {
  const portFile = path.join(profile, 'DevToolsActivePort'), start = Date.now();
  while (!fs.existsSync(portFile) || !fs.readFileSync(portFile, 'utf8').includes('\n')) {
    if (Date.now() - start > TIMEOUT) throw Error('Chrome did not open a debugging port');
    await sleep(100);
  }
  const port = fs.readFileSync(portFile, 'utf8').split('\n')[0];
  const page = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page');
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.onopen = resolve;
    socket.onerror = reject;
  });
  let id = 0;
  const pending = new Map(), listeners = [];
  socket.onmessage = ({data}) => {
    const message = JSON.parse(data);
    if (message.id && pending.has(message.id)) {
      const {resolve, reject} = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(Error(message.error.message));
      else resolve(message.result);
    } else if (message.method) {
      listeners.forEach(listen => listen(message));
    }
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    pending.set(++id, {resolve, reject});
    socket.send(JSON.stringify({id, method, params}));
  });
  return {send, on: listen => listeners.push(listen), close: () => socket.close()};
}


(async()=>{
 const out=path.resolve('exports');fs.mkdirSync(out,{recursive:true});
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'teardown-export-'));
 const browser=spawn(findChrome(),['--headless=new','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--window-size=1400,900','--no-first-run','about:blank'],{stdio:'ignore'});
 let cdp;const errors=[],network=[];
 try{
 cdp=await connect(profile);cdp.on(({method,params})=>{if(method==='Runtime.exceptionThrown')errors.push(params.exceptionDetails.text);if(method==='Network.requestWillBeSent'&&!/^(file|data|blob|about):/.test(params.request.url))network.push(params.request.url)});
 for(const method of ['Runtime.enable','Network.enable','Page.enable'])await cdp.send(method);
 await cdp.send('Page.setDownloadBehavior',{behavior:'allow',downloadPath:out});
 const ev=async expression=>{const r=await cdp.send('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 const settle=async()=>{await sleep(400);for(let i=0;i<150;i++){if(await ev("document.getElementById('viewport')?.getAttribute('aria-busy')==='false'"))return;await sleep(200)}throw Error('Render timeout')};
 await cdp.send('Page.navigate',{url:'file://'+path.resolve('dist/index.html')});await settle();
 await ev(`(()=>{const t=document.getElementById('color-target');t.value='filter';t.dispatchEvent(new Event('change'));const h=document.getElementById('hue');h.value=280;h.dispatchEvent(new Event('input'));const a=document.getElementById('annotate');a.checked=true;a.dispatchEvent(new Event('change'))})()`);await settle();
 for(const view of ['assembled','exploded']){await ev(`document.querySelector('#view [data-view="${view}"]').click()`);await settle();}
 const results=[];
 for(const format of ['svg','png','pdf']){
 await ev(`document.querySelector('.export-choice[data-format="${format}"]').click()`);
 let files=[];for(let i=0;i<200;i++){files=fs.readdirSync(out).filter(f=>f.endsWith('.'+format));if(files.length)break;await sleep(100)}
 if(files.length!==1)throw Error('Missing '+format);results.push({format,file:files[0],bytes:fs.statSync(path.join(out,files[0])).size});
 }
 const shot=await cdp.send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'viewer.png'),Buffer.from(shot.data,'base64'));
 const svgFile=path.join(out,results.find(x=>x.format==='svg').file),svg=fs.readFileSync(svgFile,'utf8');
 const metadata=JSON.parse(svg.match(/<metadata[^>]*>([\s\S]*?)<\/metadata>/)[1].replaceAll('&quot;','"').replaceAll('&amp;','&'));
 if(metadata.colors.parts.filter!=='#594fd7'||!metadata.annotate)throw Error('Color/annotation not exported');
 if(errors.length||network.length)throw Error(JSON.stringify({errors,network}));
 const result={results,metadata,errors,network,scope:'Three conceptual plates; part hue, annotations, assembled/exploded, actual SVG/PNG/PDF downloads. No manufacturing validation.'};fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{cdp?.close();browser.kill();await sleep(200);fs.rmSync(profile,{recursive:true,force:true})}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
