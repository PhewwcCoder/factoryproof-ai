'use client';
import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Workspace } from '@/lib/types';
const Context = createContext<{data: Workspace; refresh: () => Promise<void>}>({} as never);
export function WorkspaceProvider({initial, children}: {initial: Workspace; children: React.ReactNode}) {
  const [data, setData] = useState(initial);
  const refresh = useCallback(async () => setData(await api<Workspace>('/workspace')), []);
  const processing = data.documents.some(d => d.processing_status === 'processing');
  useEffect(() => {if (!processing) return; const timer = setInterval(() => {void refresh().catch(() => undefined);}, 1200); return () => clearInterval(timer);}, [processing, refresh]);
  return <Context.Provider value={{data, refresh}}>{children}</Context.Provider>;
}
export const useWorkspace = () => useContext(Context);
