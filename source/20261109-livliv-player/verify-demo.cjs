const fs=require('fs'),path=require('path'),assert=require('assert');
const req=require('module').createRequire('/tmp/livliv-player-research/package.json');const{chromium}=req('playwright-core');
(async()=>{const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});try{
const context=await browser.newContext({permissions:[],viewport:{width:1100,height:800}}),page=await context.newPage(),requests=[],errors=[];
page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8766/example/demo.html?model=../characters/k01/');await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('Sena'),{timeout:30000});
const before=await page.evaluate(()=>({status:document.querySelector('#status').textContent,playing:window.player.playing,expressions:window.player.expressions}));
const actions=await page.evaluate(()=>{const p=window.player;const id=p.expressions[0]?.id??p.expressions[0];const accepted=id?p.setExpression(id):false;p.act('nod');p.params.mouthOpen=.6;return{expression:id,accepted,mouthOpen:p.params.mouthOpen,snapshot:p.snapshot().startsWith('data:image/png')}});
await page.screenshot({path:process.argv[2]||'/tmp/livliv-demo-screenshot.png'});
const remote=requests.filter(u=>/^https?:/.test(u)&&!u.startsWith('http://127.0.0.1:8766/'));assert(before.playing&&actions.snapshot&&actions.mouthOpen===.6&&errors.length===0&&remote.length===0);
await page.evaluate(()=>window.player.dispose());const out={browser:'headless Chromium with SwiftShader',...before,actions,externalRequests:remote,pageErrors:errors,requests:requests.length,realCamera:false,realMicrophone:false,scope:'one actual demo page, local character, parameter/expression/action path and PNG snapshot; no performance or sensor benchmark'};fs.writeFileSync(path.join(__dirname,'demo-verification.json'),JSON.stringify(out,null,2));console.log(JSON.stringify(out));
}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
