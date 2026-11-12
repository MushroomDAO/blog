const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),req=require('module').createRequire(root+'/pipeline/m2/index.js'),axios=req('axios'),{WeChatClient}=req('./wechat-api/client.js');
(async()=>{const c=new WeChatClient(process.env.WECHAT_APP_ID,process.env.WECHAT_APP_SECRET),token=await c.getAccessToken(),rec=JSON.parse(fs.readFileSync(root+'/pipeline/m2/output/nx2apple-switch-apple-builder.json'));
const{data:d}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/get?access_token='+token,{media_id:rec.mediaId});assert(!d.errcode&&d.news_item.length===1);const a=d.news_item[0];assert(a.title===rec.title);const u='https://blog.mushroom.cv/blog/nx2apple-switch-apple-builder/';
if(a.content_source_url===u){console.log('source already correct');return;}
const fields=['title','author','digest','content','thumb_media_id','need_open_comment','only_fans_can_comment'];const article=Object.fromEntries(fields.map(k=>[k,a[k]]));article.content_source_url=u;
const{data:r}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/update?access_token='+token,{media_id:rec.mediaId,index:0,articles:article});assert(r.errcode===0,JSON.stringify(r));console.log('Existing draft source link updated; no new draft created');})();
