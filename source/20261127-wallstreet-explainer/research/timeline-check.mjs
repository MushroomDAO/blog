import assert from 'node:assert/strict';
import fs from 'node:fs';
import {stub} from '/tmp/wallstreet-research-20261127/scripts/timeline_stub.mjs';
const a=stub({lines:[{id:'x',text:'测试。'}]});assert(a.stub);assert.equal(a.beats[0].wav,null);assert.equal(a.beats[0].chars.length,3);assert(a.duration>a.beats[0].end);
assert.throws(()=>stub({lines:[{id:'x'}]}));
assert.throws(()=>stub({lines:[{text:'测试'}]}));
const b=stub({lines:[{id:'x',text:'测试。',bite:{parts:[['source.mp4',1,2,'引用',0]]}}],title:{after:'x',len:1}});assert.equal(b.inserts[0].parts[0].dur,2);assert.equal(b.title.end-b.title.start,1);
console.log(JSON.stringify({checks:8,passed:8,scope:'actual pure timeline function; synthetic input; no voice or ASR',node:process.version},null,2));
