import Link from 'next/link';
import { Check, CircleHelp, FileQuestion, ShieldCheck, TriangleAlert } from 'lucide-react';
import type { Status } from '@/lib/types';
export function Brand() { return <Link href="/" className="brand" aria-label="FactoryProof home"><span className="brand-symbol"><ShieldCheck size={21} strokeWidth={1.7}/></span><span>FactoryProof<span className="brand-ai">AI</span></span></Link>; }
const names: Record<Status, string> = {SUPPORTED: 'Supported', INSUFFICIENT: 'Insufficient', MISSING: 'Missing', NEEDS_REVIEW: 'Needs review'};
const icons = {SUPPORTED: Check, INSUFFICIENT: TriangleAlert, MISSING: FileQuestion, NEEDS_REVIEW: CircleHelp};
export function StatusBadge({status}: {status: Status}) { const Icon = icons[status]; return <span className={`status status-${status.toLowerCase()}`}><Icon size={14} aria-hidden="true"/>{names[status]}</span>; }
export function Empty({title, children}: {title: string; children: React.ReactNode}) { return <div className="empty"><FileQuestion size={30}/><h2>{title}</h2><p>{children}</p></div>; }
