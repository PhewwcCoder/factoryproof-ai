'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Brand } from '@/components/ui';
import { DemoButton } from '@/components/demo-button';
export default function Login() {
  const [error, setError] = useState(''), [busy, setBusy] = useState(false); const router = useRouter();
  return <main className="login-page" id="main"><Brand/><div className="login-panel"><span className="eyebrow">Your factory workspace</span><h1>Welcome back.</h1><p>Sign in with the account provided by your factory administrator.</p><form onSubmit={async e => {e.preventDefault();setBusy(true);setError('');const data=new FormData(e.currentTarget);try{await api('/auth/login',{method:'POST',body:JSON.stringify(Object.fromEntries(data))});router.push('/workspace');}catch(e){setError((e as Error).message);setBusy(false);}}}><label>Email address<input name="email" type="email" autoComplete="email" required/></label><label>Password<input name="password" type="password" autoComplete="current-password" required/></label>{error && <p className="error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy?'Signing in…':'Sign in'}</button></form><div className="login-demo"><p>Evaluating FactoryProof?</p><DemoButton className="button secondary"/><span className="meta">A private session with synthetic evidence. No account needed.</span></div></div></main>;
}
