import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {decideAction} from '/tmp/grok-alt-copilot/server/src/approvals/policy.ts';
const base={team:[],personal:[],customRulesEnabled:true,autoReview:false,askBeforeChanges:false};
const candidate={actorId:'owner',botId:'bot',toolRef:'mcp/gmail/create_label',effect:'write',scope:'gmail',args:{name:'Notes'}};
const rule=(behaviour,id=behaviour)=>({id,ownerUserId:'owner',botId:'*',toolRef:'mcp/gmail/*',effect:'*',scope:'*',behaviour,revokedAt:null,createdAt:new Date(0)});
const cases=[];
async function check(name,input,expected){const out=await decideAction({...base,candidate,...input});assert.equal(out.behaviour,expected,name);cases.push({name,behaviour:out.behaviour,source:out.source});}
await check('ordinary read without stricter policy',{candidate:{...candidate,effect:'read',toolRef:'mcp/drive/list_files'}},'allow');
await check('ask-before-changes write',{askBeforeChanges:true},'ask');
await check('personal ask beats overlapping allow',{personal:[rule('allow'),rule('ask')]},'ask');
const{ownerUserId,...team}=rule('ask');await check('team ask beats personal allow',{team:[{...team,createdBy:'admin'}],personal:[rule('allow')]},'ask');
await check('preapproved without reviewer asks',{personal:[rule('pre_approved')]},'ask');
await check('send-email safety without matching allow',{candidate:{...candidate,toolRef:'mcp/gmail/send_email',args:{to:'person@example.test',body:'fixture'}}},'ask');
const r={sourceCommit:'d3b3ae83fe9068127c389aa2e557e2fe8fc558ac',checks:cases,passed:cases.length,scope:'actual pure policy function, zod4.6.7, mock candidate/rules, no DB/model/browser/action execution; not the full upstream test suite or complete security proof'};
writeFileSync(new URL('./copilot-policy-probe.json',import.meta.url),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
