import { extract } from './extraction';
import { get, put, type Env, type Job } from './store';
import type { Evidence } from '../lib/types';
import { readOriginal } from './documents';
export async function processDocument(env:Env,job:Job){
 const doc=await get<Evidence>(env,job.tenant,job.document,'document');if(!doc)return;
 const content=await readOriginal(env,job.tenant,job.document);if(!content)return;
 try{const result=await extract(new Uint8Array(content),doc.name);await put(env,job.tenant,doc.id,'document',{...doc,...result});}
 catch(error){await put(env,job.tenant,doc.id,'document',{...doc,facts:{},citations:{},pages:[],processing_status:'error',message:error instanceof Error?error.message:'Document extraction failed.'});}
}
export async function consume(batch:MessageBatch<Job>,env:Env){for(const message of batch.messages){try{await processDocument(env,message.body);message.ack();}catch{message.retry({delaySeconds:30});}}}
export async function cleanup(env:Env){
 const expired=await env.DB.prepare('SELECT id FROM tenants WHERE demo=1 AND expires_at<? LIMIT 50').bind(Math.floor(Date.now()/1000)).all<{id:string}>();
 for(const tenant of expired.results)await env.DB.prepare('DELETE FROM tenants WHERE id=?').bind(tenant.id).run();
 await env.DB.batch([env.DB.prepare('DELETE FROM sessions WHERE expires_at<?').bind(Math.floor(Date.now()/1000)),env.DB.prepare('DELETE FROM rate_limits WHERE expires_at<?').bind(Math.floor(Date.now()/1000))]);
}
