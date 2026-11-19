import type { Env } from './store';
export const MAX_UPLOAD=1024*1024;
export async function saveOriginal(env:Env,tenant:string,id:string,content:ArrayBuffer){
 if(content.byteLength>MAX_UPLOAD)throw new Error('Free MVP upload limit is 1 MB.');
 await env.DB.prepare('INSERT INTO document_blobs(tenant_id,document_id,content) VALUES(?,?,?)').bind(tenant,id,content).run();
}
export async function readOriginal(env:Env,tenant:string,id:string):Promise<ArrayBuffer|null>{
 const data=await env.DB.prepare('SELECT content FROM document_blobs WHERE tenant_id=? AND document_id=?').bind(tenant,id).first<ArrayBuffer>('content');
 return data?new Uint8Array(data).buffer:null;
}
