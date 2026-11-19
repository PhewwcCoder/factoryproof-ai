export interface Env {
 DB: D1Database; EXTRACTION: Queue<Job>; ASSETS: Fetcher;
}
export type Job={tenant:string;document:string};
export type Session={tenant_id:string;role:string;user_name:string;expires_at:number;demo:number;name:string};
export const uid=()=>crypto.randomUUID();
export const now=()=>new Date().toISOString();
export async function hash(value:string){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)))).map(v=>v.toString(16).padStart(2,'0')).join('');}
export async function list<T>(env:Env,tenant:string,kind:string):Promise<T[]> {
 const {results}=await env.DB.prepare('SELECT id,payload,created_at FROM records WHERE tenant_id=? AND kind=? ORDER BY created_at,id').bind(tenant,kind).all<{id:string;payload:string;created_at:string}>();
 return results.map(r=>({...JSON.parse(r.payload),id:r.id,created_at:r.created_at}));
}
export async function get<T>(env:Env,tenant:string,id:string,kind:string):Promise<T|null> {
 const row=await env.DB.prepare('SELECT payload,created_at FROM records WHERE tenant_id=? AND id=? AND kind=?').bind(tenant,id,kind).first<{payload:string;created_at:string}>();
 return row?{...JSON.parse(row.payload),id,created_at:row.created_at}:null;
}
export async function put(env:Env,tenant:string,id:string,kind:string,payload:unknown){
 await env.DB.prepare('INSERT INTO records(tenant_id,id,kind,payload) VALUES(?,?,?,?) ON CONFLICT(tenant_id,id) DO UPDATE SET payload=excluded.payload').bind(tenant,id,kind,JSON.stringify(payload)).run();
}
export async function audit(env:Env,tenant:string,action:string){await put(env,tenant,uid(),'audit',{action});}
export async function allowed(env:Env,key:string,limit:number,seconds:number){
 const epoch=Math.floor(Date.now()/1000),bucket=Math.floor(epoch/seconds);
 const row=await env.DB.prepare('INSERT INTO rate_limits(key,count,expires_at) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1 RETURNING count').bind(`${key}:${bucket}`,epoch+seconds*2).first<{count:number}>();return !!row&&row.count<=limit;
}
export async function session(env:Env,token:string|undefined){if(!token)return null;return env.DB.prepare('SELECT s.tenant_id,s.role,s.user_name,s.expires_at,t.demo,t.name FROM sessions s JOIN tenants t ON t.id=s.tenant_id WHERE s.token_hash=? AND s.expires_at>?').bind(await hash(token),Math.floor(Date.now()/1000)).first<Session>();}
export async function passwordHash(password:string,salt:string){const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(password),'PBKDF2',false,['deriveBits']);return Array.from(new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2',salt:new TextEncoder().encode(salt),iterations:100000,hash:'SHA-256'},key,256))).map(v=>v.toString(16).padStart(2,'0')).join('');}
