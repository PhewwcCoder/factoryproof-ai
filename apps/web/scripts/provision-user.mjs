import { webcrypto, randomUUID } from 'node:crypto';
import { mkdtempSync, writeFileSync, rmSync, rmdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
const [email,name,role='administrator']=process.argv.slice(2),password=process.env.FACTORYPROOF_PASSWORD;
if(!email||!name||!password||password.length<12||!['administrator','compliance_officer','reviewer','viewer'].includes(role))throw new Error('Provide email, tenant name, role and FACTORYPROOF_PASSWORD (minimum 12 characters).');
const salt=randomUUID(),tenant='private-'+randomUUID(),encoder=new TextEncoder();
const key=await webcrypto.subtle.importKey('raw',encoder.encode(password),'PBKDF2',false,['deriveBits']);
const hash=Buffer.from(await webcrypto.subtle.deriveBits({name:'PBKDF2',salt:encoder.encode(salt),iterations:100000,hash:'SHA-256'},key,256)).toString('hex');
const q=s=>"'"+s.replaceAll("'","''")+"'";
const folder=mkdtempSync(join(tmpdir(),'factoryproof-provision-')),file=join(folder,'user.sql');
try{writeFileSync(file,`INSERT INTO tenants(id,name,demo) VALUES(${q(tenant)},${q(name)},0);\nINSERT INTO users(email,tenant_id,password_hash,salt,role) VALUES(${q(email.toLowerCase())},${q(tenant)},${q(hash)},${q(salt)},${q(role)});`);const r=spawnSync(process.execPath,['node_modules/wrangler/bin/wrangler.js','d1','execute','factoryproof-mvp',process.argv.includes('--remote')?'--remote':'--local','--file',file],{stdio:'inherit'});if(r.status)process.exitCode=r.status;}finally{rmSync(file);rmdirSync(folder);}
