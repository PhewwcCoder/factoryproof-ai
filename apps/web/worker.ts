import handler from 'vinext/server/fetch-handler';
import { consume, cleanup } from './server/jobs';
import type { Env, Job } from './server/store';
const worker = {
 fetch: handler.fetch,
 queue: (batch:MessageBatch<Job>,env:Env)=>consume(batch,env),
 scheduled: (_event:ScheduledController,env:Env,ctx:ExecutionContext)=>ctx.waitUntil(cleanup(env)),
};
export default worker;
