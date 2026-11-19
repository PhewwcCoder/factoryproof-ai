import type { Metadata } from 'next';
import '@fontsource-variable/manrope';
import '@fontsource-variable/dm-sans';
import './globals.css';
export const metadata: Metadata = {title: 'FactoryProof AI | Factory evidence, buyer by buyer', description: 'Reconcile factory documents against buyer-specific requirements with source-linked explanations and deterministic checks.', openGraph: {title: 'FactoryProof AI', description: 'One evidence vault. Every buyer’s conditions.', type: 'website'}};
export default function RootLayout({children}: {children: React.ReactNode}) { return <html lang="en" data-type="software"><head><meta name="page-type" content="software"/><meta name="site-kind" content="software"/></head><body><a className="skip-link" href="#main">Skip to content</a>{children}</body></html>; }
