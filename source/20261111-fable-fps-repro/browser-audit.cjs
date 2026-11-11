const fs=require('fs'),http=require('http'),path=require('path'),assert=require('assert');
const {chromium}=require('/tmp/fable-fps-browser/node_modules/playwright');
const root=process.argv[2]||'/tmp/fable-fps-research',out=__dirname;
(async()=>{
 const server=http.createServer((req,res)=>{let p=path.join(root,decodeURIComponent(req.url.split('?')[0]));if(fs.existsSync(p)&&fs.statSync(p).isDirectory())p=path.join(p,'index.html');if(!p.startsWith(root)||!fs.existsSync(p)){res.writeHead(404);res.end();return}res.setHeader('Content-Type',p.endsWith('.html')?'text/html':p.endsWith('.js')?'application/javascript':'application/octet-stream');res.end(fs.readFileSync(p));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 let browser;const results=[];
 try{
  browser=await chromium.launch({channel:'chrome',headless:true});const ctx=await browser.newContext({viewport:{width:960,height:540},deviceScaleFactor:1,ignoreHTTPSErrors:true});
  for(const name of ['01-audio','01-audio-1h','02-materials','03-models','04-fps']){
   const page=await ctx.newPage();const errors=[],requests=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({url:r.url(),type:r.resourceType()}));
   await page.goto(`http://127.0.0.1:${server.address().port}/demos/${name}/?manual=1&q=2&pr=1&still=1`,{waitUntil:'networkidle',timeout:60000});
   const r={name,title:await page.title(),errors,externalRequests:requests.filter(x=>!x.url.startsWith('http://127.0.0.1'))};
   if(name==='01-audio'){
    await page.waitForFunction(()=>!!window.SFX);r.audio=await page.evaluate(()=>SFX.selftest());r.mix=await page.evaluate(()=>SFX.mixtest());r.soundCount=Object.keys(r.audio).length;
   }else if(name==='01-audio-1h'){
    await page.waitForFunction(()=>!!window.__selfTest);r.audio=await page.evaluate(()=>__selfTest());r.soundCount=Object.keys(r.audio).length;r.selftestError=await page.evaluate(()=>window.__err);
   }else if(name==='02-materials'){
    await page.waitForFunction(()=>window.__ready,{timeout:60000});r.renderer=await page.evaluate(()=>window.__gpu);r.buttons=await page.locator('#bar button').count();await page.locator('#bar button').nth(2).click();
   }else if(name==='03-models'){
    await page.waitForFunction(()=>!!window.__viewer,{timeout:60000});r.viewer=await page.evaluate(()=>{const v=__viewer,g=v.renderer.getContext(),d=g.getExtension('WEBGL_debug_renderer_info');return{renderer:d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):'unknown',models:Object.keys(v.MODELS)}});
   }else{
    await page.waitForFunction(()=>!!window.__dbg?.step,{timeout:60000});r.renderer=await page.evaluate(()=>__dbg.gpu);r.softwareRenderer=await page.evaluate(()=>__dbg.soft);
    r.functional=await page.evaluate(()=>{const d=__dbg;d.start();d.step(1/60,1);const a=d.st();d.set({keys:{KeyW:true}});d.step(1/60,60);d.set({keys:{KeyW:false}});const moved=d.st();d.fire();const fired=d.st();d.reload();d.step(1/60,180);const reloaded=d.st();const waves=new Set();for(let n=0;n<160&&d.st().state==='playing';n++){d.set({hp:100});for(let i=d.drones().length-1;i>=0;i--)d.kill(i);d.step(.05,20);waves.add(d.st().wave);}return{start:a,moved,fired,reloaded,debugCleared:d.st(),waves:[...waves]}});
    assert.notDeepStrictEqual(r.functional.start.pos,r.functional.moved.pos);assert(r.functional.fired.ammo<r.functional.moved.ammo);assert(r.functional.reloaded.ammo===30);assert(r.functional.debugCleared.state==='win');
    await page.screenshot({path:'/tmp/fable-fps-debug-win.png'});await page.evaluate(()=>{__dbg.start();__dbg.hurt(1000)});await page.waitForFunction(()=>__dbg.st().state==='over');r.death=await page.evaluate(()=>__dbg.st());r.audio=await page.evaluate(()=>__dbg.audioTest());r.audioCases=Object.keys(r.audio).length;
   }
   r.errors=[...errors];await page.screenshot({path:`/tmp/fable-fps-${name}.png`});assert(errors.length===0,JSON.stringify(errors));results.push(r);fs.writeFileSync(path.join(out,'browser-audit-results.json'),JSON.stringify({scope:'Existing shipped artifacts only; debug-assisted functional checks, offline audio; no generation, FPS benchmark or human listening',browserVersion:browser.version(),viewport:[960,540],results},null,2));await page.close();
  }
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r))}
 console.log(JSON.stringify(results.map(r=>({name:r.name,pageErrors:r.errors.length,renderer:r.renderer||r.viewer?.renderer,soundCount:r.soundCount,audioCases:r.audioCases}))))
})().catch(e=>{console.error(e.stack);process.exit(1)});
