const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');const req=require('module').createRequire(path.join(root,'pipeline/m2/index.js'));const axios=req('axios');const{WeChatClient}=req('./wechat-api/client.js');
(async()=>{
const env=Object.fromEntries(fs.readFileSync(path.join(root,'.env'),'utf8').split('\n').filter(x=>/^[A-Z_]+=/.test(x)).map(x=>{const i=x.indexOf('=');return[x.slice(0,i),x.slice(i+1).replace(/^["']|["']$/g,'')]}));const c=new WeChatClient(env.WECHAT_APP_ID,env.WECHAT_APP_SECRET);const token=await c.getAccessToken();const reports=[];
for(const slug of ['roboharness-v2-workspace']){
 const rec=JSON.parse(fs.readFileSync(path.join(root,'pipeline/m2/output',slug+'.json'),'utf8'));const local=fs.readFileSync(path.join(root,'pipeline/m2/output',slug+'.html'),'utf8');
 const{data}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/get?access_token='+token,{media_id:rec.mediaId});assert(!data.errcode,JSON.stringify({errcode:data.errcode}));const a=data.news_item[0];
 // WeChat escapes apostrophes in CSS as &#39;. Decode equivalent numeric entities before comparing the full HTML.
 const normalized=x=>x.replace(/&#(?:x([0-9a-f]+)|([0-9]+));/gi,(_,hex,dec)=>String.fromCodePoint(parseInt(hex||dec,hex?16:10))).replace(/\s+/g,' ').trim();const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
 const canonical=JSON.parse(require('child_process').execFileSync('python3',[path.join(__dirname,'wechat-content-canonical.py')],{input:JSON.stringify({local,remote:a.content}),encoding:'utf8'}));
 const coverLog=fs.readFileSync('/tmp/'+slug+'-m2.log','utf8');const coverId=coverLog.match(/Cover uploaded: media_id=(\S+)/)?.[1];
 const report={slug,mediaId:rec.mediaId,titleMatches:a.title===rec.title,authorMatches:a.author===rec.author,digestMatches:a.digest===rec.digest,htmlExact:normalized(a.content)===normalized(local),...canonical,platformRewrites:['external anchor wrappers removed','numeric entity escaping','img src converted to data-src and CDN resolution 0 to640'],canonicalInBody:a.content.includes('https://blog.mushroom.cv/blog/'+slug+'/'),copyrightPresent:a.content.includes('Mycelium Protocol'),coverMatches:a.thumb_media_id===coverId,needOpenComment:a.need_open_comment,onlyFansComment:a.only_fans_can_comment,contentSourceUrl:a.content_source_url||'',localContentHash:hash(normalized(local)),remoteContentHash:hash(normalized(a.content))};
 assert(report.titleMatches&&report.authorMatches&&report.digestMatches&&(report.fullTextMatches&&report.imageIdentitiesMatch&&report.imageCount===3)&&report.canonicalInBody&&report.copyrightPresent&&report.coverMatches,JSON.stringify(report));assert(report.needOpenComment===1&&report.onlyFansComment===0,JSON.stringify(report));reports.push(report);
}
const out={checkedAt:new Date().toISOString(),drafts:reports};fs.writeFileSync(path.join(__dirname,'wechat-verification.json'),JSON.stringify(out,null,2));console.log(JSON.stringify(out));
})().catch(e=>{console.error(e.message);process.exit(1)});
