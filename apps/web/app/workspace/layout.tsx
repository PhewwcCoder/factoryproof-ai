import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { WorkspaceProvider } from '@/components/workspace-context';
import { WorkspaceShell } from '@/components/workspace-shell';
import { env } from 'cloudflare:workers';
import { api } from '@/server/api';
import type { Workspace } from '@/lib/types';
import type { Env } from '@/server/store';
export default async function WorkspaceLayout({children}: {children: React.ReactNode}) {
  const jar = await cookies();
  if (!jar.get('fp_session')) redirect('/login');
  const response = await api.fetch(new Request('https://internal/api/workspace', {headers:{Cookie:jar.toString()}}), env as unknown as Env);
  if (response.status === 401) redirect('/login');
  if (!response.ok) throw new Error('The workspace API is unavailable.');
  const initial = await response.json() as Workspace;
  return <WorkspaceProvider initial={initial}><WorkspaceShell>{children}</WorkspaceShell></WorkspaceProvider>;
}
