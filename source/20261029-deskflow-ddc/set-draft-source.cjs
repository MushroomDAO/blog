const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),req=require('module').createRequire(root+'/pipeline/m2/index.js'),axios=req('axios'),{WeChatClient}=req('./wechat-api/client.js');
(async()=>{
 const slug='deskflow-ddc-monitor-keyboard-sharing',url='https://blog.mushroom.cv/blog/'+slug+'/',recPath=root+'/pipeline/m2/output/'+slug+'.json',rec=JSON.parse(fs.readFileSync(recPath));
 const env=Object.fromEntries(fs.readFileSync(root+'/.env','utf8').split('\n').filter(x=>/^[A-Z_]+=/.test(x)).map(x=>{let i=x.indexOf('=');return[x.slice(0,i),x.slice(i+1).replace(/^["']|["']$/g,'')]}));
 const c=new WeChatClient(env.WECHAT_APP_ID,env.WECHAT_APP_SECRET),token=await c.getAccessToken();
 const{data:d}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/get?access_token='+token,{media_id:rec.mediaId});assert(!d.errcode,JSON.stringify(d));assert(d.news_item.length===1);const a=d.news_item[0];assert(a.title===rec.title&&a.author===rec.author&&a.digest===rec.digest);
 if(a.content_source_url!==url){const article={};for(const k of ['title','author','digest','content','thumb_media_id','need_open_comment','only_fans_can_comment'])article[k]=a[k];article.content_source_url=url;
 const{data:r}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/update?access_token='+token,{media_id:rec.mediaId,index:0,articles:article});assert(r.errcode===0,JSON.stringify(r));}
 rec.blogUrl=url;rec.contentSourceUrl=url;fs.writeFileSync(recPath,JSON.stringify(rec,null,2)+'\n');console.log(JSON.stringify({mediaId:rec.mediaId,sourceUrl:url,action:'same draft/update; no new draft'}));
})().catch(e=>{console.error(e.message);process.exitCode=1});
