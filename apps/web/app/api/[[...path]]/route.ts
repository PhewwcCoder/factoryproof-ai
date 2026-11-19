import { env } from 'cloudflare:workers';
import { api } from '@/server/api';
import type { Env } from '@/server/store';
const handler=(request:Request)=>api.fetch(request,env as unknown as Env);
export const GET=handler;
export const POST=handler;
export const PUT=handler;
export const DELETE=handler;
