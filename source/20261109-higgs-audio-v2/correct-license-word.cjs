const fs=require('fs'),path=require('path'),assert=require('assert');
const req=require('module').createRequire(path.resolve('pipeline/m2/index.js')),axios=req('axios'),{WeChatClient}=req('./wechat-api/client.js');
(async()=>{
const env=Object.fromEntries(fs.readFileSync('.env','utf8').split('\n').filter(x=>/^[A-Z_]+=/.test(x)).map(x=>{let i=x.indexOf('=');return[x.slice(0,i),x.slice(i+1).replace(/^["']|["']$/g,'')]}));
const c=new WeChatClient(env.WECHAT_APP_ID,env.WECHAT_APP_SECRET),token=await c.getAccessToken();
const slug='higgs-audio-v2-engineering-deployment-guide',base=path.resolve('pipeline/m2/output',slug),rec=JSON.parse(fs.readFileSync(base+'.json','utf8'));
const endpoint=name=>'https://api.weixin.qq.com/cgi-bin/draft/'+name+'?access_token='+token;
const{data}=await axios.post(endpoint('get'),{media_id:rec.mediaId});assert(!data.errcode);const a=data.news_item[0];
const old='若许可方及关联方',fixed='若使用方及其关联方';assert(a.content.split(old).length===2||a.content.includes(fixed));
if(a.content.includes(old)){
 const articles={};for(const k of ['title','author','digest','content','content_source_url','thumb_media_id','need_open_comment','only_fans_can_comment'])if(a[k]!==undefined)articles[k]=a[k];
 articles.content=a.content.replace(old,fixed);const r=await axios.post(endpoint('update'),{media_id:rec.mediaId,index:0,articles});assert(r.data.errcode===0,JSON.stringify(r.data));
}
const html=fs.readFileSync(base+'.html','utf8');assert(html.includes(old)||html.includes(fixed));fs.writeFileSync(base+'.html',html.replace(old,fixed));
rec.licenseTerminologyCorrectedAt=new Date().toISOString();fs.writeFileSync(base+'.json',JSON.stringify(rec,null,2)+'\n');
const report={mediaId:rec.mediaId,updatedInPlace:true,correction:'许可方 -> 使用方, licensee instead of licensor',checkedAt:new Date().toISOString()};fs.writeFileSync(path.join(__dirname,'wechat-in-place-correction.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e.message);process.exit(1)});
