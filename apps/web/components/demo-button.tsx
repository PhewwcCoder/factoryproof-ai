'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
export function DemoButton({className = 'button primary', children = 'Try with Sample Documents'}: {className?: string; children?: React.ReactNode}) {
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const router = useRouter();
  async function open() { setBusy(true); setError(''); try {await api('/auth/demo', {method: 'POST'}); router.push('/workspace/evidence');} catch(e) {setError((e as Error).message); setBusy(false);} }
  return <div className="demo-action"><button className={className} onClick={open} disabled={busy}>{busy ? 'Preparing workspace…' : children}</button>{error && <p className="error" role="alert">{error}</p>}</div>;
}
