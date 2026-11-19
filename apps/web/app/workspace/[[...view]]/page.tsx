import { notFound } from 'next/navigation';
import { WorkspaceView } from '@/components/workspace-view';
export default async function Page({params}: {params: Promise<{view?: string[]}>}) {const {view} = await params; const screen=view?.[0] || 'overview'; if(!['overview','evidence','buyers','compare','reviews','reports'].includes(screen)) notFound();return <WorkspaceView screen={screen}/>;}
