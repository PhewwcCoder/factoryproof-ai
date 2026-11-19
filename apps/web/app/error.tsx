'use client';
export default function ErrorPage({reset}: {reset:()=>void}) {return <main id="main" className="content"><h1>The workspace couldn’t load.</h1><p>Check that the API service is running, then try again.</p><button className="button primary" onClick={reset}>Try again</button></main>;}
