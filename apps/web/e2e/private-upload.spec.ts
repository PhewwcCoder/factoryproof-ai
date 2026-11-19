import { test, expect } from '@playwright/test';
import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { request as httpRequest } from 'node:http';
test('private login, real PDF upload, extraction and source authorization',async({request,baseURL})=>{
 test.skip(!!process.env.BASE_URL,'Local provisioning only; never creates test users on production.');
 const password=randomUUID()+randomUUID(),email=`test-${randomUUID()}@example.invalid`;
 const provision=spawnSync(process.execPath,['scripts/provision-user.mjs',email,'Private upload test','administrator'],{env:{...process.env,FACTORYPROOF_PASSWORD:password},encoding:'utf8'});
 expect(provision.status,provision.stderr).toBe(0);
 const login=await request.post('/api/auth/login',{headers:{Origin:baseURL!},data:{email,password}});expect(login.status()).toBe(200);
 const bytes=readFileSync(resolve(import.meta.dirname,'../../../datasets/public-demo/evidence/01_fire_drill_log.pdf'));
 const upload=await request.post('/api/documents',{headers:{Origin:baseURL!},multipart:{file:{name:'private-fire.pdf',mimeType:'application/pdf',buffer:bytes}}});expect(upload.status()).toBe(202);const {id}=await upload.json();
 await expect.poll(async()=>{const data=await (await request.get('/api/workspace')).json();return data.documents.find((d:{id:string})=>d.id===id)?.processing_status;},{timeout:45000}).toBe('ready');
 const source=await request.get(`/api/documents/${id}/file`);expect(source.status()).toBe(200);expect(await source.body()).toEqual(bytes);
 const invalid=await request.post('/api/documents',{headers:{Origin:baseURL!},multipart:{file:{name:'fake.pdf',mimeType:'application/pdf',buffer:Buffer.from('not a PDF')}}});expect(invalid.status()).toBe(400);
 // Observe the rejection headers directly: the server may close an oversized
 // request before Playwright has finished streaming its multipart body.
 const status=await new Promise<number>((resolve,reject)=>{const req=httpRequest(new URL('/api/documents',baseURL),{method:'POST',headers:{Origin:baseURL!,'Content-Type':'application/octet-stream','Content-Length':1024*1024+20000}},res=>{resolve(res.statusCode!);res.resume();});req.on('error',reject);req.end(Buffer.alloc(1024*1024+20000));});expect(status).toBe(413);
 await request.post('/api/auth/logout',{headers:{Origin:baseURL!}});expect((await request.get(`/api/documents/${id}/file`)).status()).toBe(401);
});
