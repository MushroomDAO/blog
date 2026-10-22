const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'../..');
const axios=require('module').createRequire(path.join(root,'pipeline/m2/index.js'))('axios');
const {WeChatClient}=require(path.join(root,'pipeline/m2/wechat-api/client.js'));
async function main(){
 const env=Object.fromEntries(fs.readFileSync(path.join(root,'.env'),'utf8').split('\n').filter(x=>/^[A-Z_]+=/.test(x)).map(x=>{const i=x.indexOf('=');return[x.slice(0,i),x.slice(i+1).replace(/^["']|["']$/g,'')]}));
 const slug='layerfs-v1-recursive-agent-filesystem';
 const receipt=JSON.parse(fs.readFileSync(path.join(root,'pipeline/m2/output',slug+'.json')));
 const client=new WeChatClient(env.WECHAT_APP_ID,env.WECHAT_APP_SECRET);
 const token=await client.getAccessToken();
 const {data}=await axios.post('https://api.weixin.qq.com/cgi-bin/draft/get?access_token='+token,{media_id:receipt.mediaId});
 if(data.errcode)throw Error('draft/get '+data.errcode);
 const a=data.news_item?.[0];
 const report={mediaId:receipt.mediaId,errcode:0,title:a?.title,coverPresent:Boolean(a?.thumb_media_id),bodyImageCount:(a?.content.match(/<img\b/g)||[]).length,documentedScope:a?.content.includes('本机没有 Docker'),pinnedSourceInContent:a?.content.includes('2aaf2552ce21154928b9f9c83582e41a637f5910'),titleMatches:a?.title===receipt.title,authorMatches:a?.author===receipt.author,digestMatches:a?.digest===receipt.digest};
 fs.writeFileSync(path.join(__dirname,'draft-verification.json'),JSON.stringify(report,null,2));
 if(!report.coverPresent||report.bodyImageCount!==3||!report.documentedScope||!report.pinnedSourceInContent||!report.titleMatches||!report.authorMatches||!report.digestMatches)throw Error('Draft content mismatch');
 console.log(report);
}
main().catch(e=>{console.error(e.message);process.exit(1)});
