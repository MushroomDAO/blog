// Attach the verified Blog URL to the existing draft; never creates another draft.
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),req=require('module').createRequire(path.join(root,'pipeline/m2/index.js')),axios=req('axios'),{WeChatClient}=req('./wechat-api/client.js');
(async()=>{
const env=Object.fromEntries(fs.readFileSync(path.join(root,'.env'),'utf8').split('\n').filter(x=>/^[A-Z_]+=/.test(x)).map(x=>{let i=x.indexOf('=');return[x.slice(0,i),x.slice(i+1).replace(/^["']|["']$/g,'')]}));
const slug='rayline-arc-open-routing-model-cost-audit',p=path.join(root,'pipeline/m2/output',slug+'.json'),rec=JSON.parse(fs.readFileSync(p));
const client=new WeChatClient(env.WECHAT_APP_ID,env.WECHAT_APP_SECRET),token=await client.getAccessToken(),endpoint='https://api.weixin.qq.com/cgi-bin/draft/';
const {data}=await axios.post(endpoint+'get?access_token='+token,{media_id:rec.mediaId},{timeout:45000});assert(!data.errcode,JSON.stringify({errcode:data.errcode}));const a=data.news_item[0];assert(a.title===rec.title&&a.author===rec.author);
const sourceUrl='https://blog.mushroom.cv/blog/'+slug+'/';
if(a.content_source_url!==sourceUrl){
 const article={};for(const k of ['title','author','digest','content','thumb_media_id','need_open_comment','only_fans_can_comment'])if(a[k]!==undefined)article[k]=a[k];article.content_source_url=sourceUrl;
 const update=await axios.post(endpoint+'update?access_token='+token,{media_id:rec.mediaId,index:0,articles:article},{timeout:45000});assert(!update.data.errcode,JSON.stringify(update.data));
}
rec.contentSourceUrl=sourceUrl;fs.writeFileSync(p,JSON.stringify(rec,null,2)+'\n');console.log('Existing draft source URL set; same media ID retained.');
})().catch(e=>{console.error(e.message);process.exit(1)});
