import Link from 'next/link';
import { Check, FileText, GitCompareArrows, ScanLine, ShieldCheck } from 'lucide-react';
import { Brand, StatusBadge } from '@/components/ui';
import { DemoButton } from '@/components/demo-button';
export default function Home() { return <>
  <header className="public-nav"><div className="wrap"><Brand/><nav aria-label="Main navigation"><a href="#workflow">How it works</a><Link href="/docs">Documentation</Link><Link href="/login">Sign in</Link></nav><DemoButton className="button secondary"/></div></header>
  <main id="main"><section className="landing-hero" data-enter><div className="wrap">
    <div className="hero-heading"><div><span className="eyebrow"><span className="small-square"/>Built for factory compliance teams</span><h1>Factory evidence.<br/>Every buyer’s conditions.</h1></div><div className="hero-intro"><p>Upload your records once. See exactly where they support each buyer’s requirements, where they fall short, and why.</p><DemoButton/><span className="meta">No account needed / 2 fictional buyers / 4 real sample PDFs.</span></div></div>
    <div className="hero-app app-frame" data-moment="comparison" aria-label="Illustrative comparison of the synthetic fire drill record">
      <div className="hero-app-top"><span><GitCompareArrows size={17}/>Cross-buyer comparison</span><span className="meta">Demonstration / 26 Dec 2026</span></div>
      <div className="hero-app-body"><div className="hero-evidence"><div className="document-icon"><FileText size={28}/></div><span className="meta">One source document</span><h2>Fire drill record</h2><p>26 April 2026</p><div className="paper-lines"><i/><i/><i/></div><div className="source-stamp"><ShieldCheck size={15}/>Source passage preserved</div></div>
      <div className="hero-buyer"><span className="buyer-mark">A</span><span className="meta">Fictional buyer</span><h3>Demo Buyer A</h3><p>Evidence from the last <strong>6 months</strong></p><div className="window-bar"><span/></div><StatusBadge status="INSUFFICIENT"/><p className="hero-reason">The April record is outside the accepted date window.</p></div>
      <div className="hero-buyer"><span className="buyer-mark pale">B</span><span className="meta">Fictional buyer</span><h3>Demo Buyer B</h3><p>Evidence from the last <strong>12 months</strong></p><div className="window-bar long"><span/></div><StatusBadge status="SUPPORTED"/><p className="hero-reason">The same date meets this buyer’s window.</p></div></div>
      <div className="hero-app-bottom"><span><Check size={15}/>Same evidence</span><span><Check size={15}/>Different constraints</span><span><Check size={15}/>Traceable decisions</span><Link href="/docs#verification">Read the verification logic</Link></div>
    </div>
  </div></section>
  <section className="workflow-section" id="workflow"><div className="wrap"><div className="section-intro"><span className="eyebrow">From records to review</span><h2>A clear chain of evidence.</h2><p>A relevant document is only the beginning. Each finding follows the source through explicit checks to a human decision.</p></div><div className="workflow-grid">
    <article><FileText size={30}/><h3>Keep the original</h3><p>Store documents in a private vault. Preserve the page and passage behind each extracted fact.</p></article>
    <article><ScanLine size={30}/><h3>Check the conditions</h3><p>Test dates, signatures, scope and thresholds against each buyer’s structured checklist.</p></article>
    <article><ShieldCheck size={30}/><h3>Resolve the gaps</h3><p>Inspect the source, record your review, and prepare a buyer-specific evidence report.</p></article>
  </div><div className="responsibility"><div><h3>Evidence preparation, with human judgment.</h3><p>FactoryProof does not certify compliance. Uncertain facts remain visible, and final reports require reviewer approval.</p></div><Link href="/docs#limitations" className="button secondary">Read the limitations</Link></div></div></section>
  </main><footer className="public-footer wrap"><Brand/><p>Factory Brain / IndustrySphere AI</p><Link href="/docs">Technical documentation</Link></footer>
</>; }
