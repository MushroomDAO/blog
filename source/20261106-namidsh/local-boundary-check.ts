import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, symlink, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@nami/cordis'
import Tools from '@nami/dsh-tools'
import * as fsTool from '@nami/dsh-tool-fs'
const base=await mkdtemp(join(tmpdir(),'nami-boundary-'))
try {
 const root=join(base,'workspace');await mkdir(root);await writeFile(join(base,'outside.txt'),'PUBLIC_TEST_FIXTURE_ONLY');await symlink(join(base,'outside.txt'),join(root,'link.txt'))
 const app=new Context();app.plugin(Tools);app.plugin(fsTool,{root});await new Promise(r=>setTimeout(r,30))
 const traversal=await app.tools.execute({name:'read_file',args:{path:'../outside.txt'}})
 const link=await app.tools.execute({name:'read_file',args:{path:'link.txt'}})
 assert(traversal.isError);assert.equal(link.content,'PUBLIC_TEST_FIXTURE_ONLY')
 console.log(JSON.stringify({parentTraversalBlocked:true,symlinkOutsideReadable:true,fixtureOnly:true,interpretation:'lexical root restriction is not a sandbox'}))
} finally {await rm(base,{recursive:true,force:true})}
