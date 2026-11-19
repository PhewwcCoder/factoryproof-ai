# Cloudflare-first, free-only MVP

Next.js App Router runs through vinext on Workers; Hono routes share the same Worker. D1 stores tenants, sessions, versioned records, audit entries, rate counters and bounded original-document BLOBs. Queues handles PDF extraction. Hourly cleanup cascades deletion of expired demo tenants.

The final free-only instruction supersedes the earlier R2 preference. No R2 subscription or paid plan is activated. Private sources are limited to 1 MB, 100 pages, and 100 documents per tenant. Public trial creation is capped at 100/day globally; provider quotas fail rather than upgrade billing.

Pure domain rules: apps/web/server/domain.ts. Extraction: extraction.ts. Original storage: documents.ts. Persistence: store.ts. These boundaries permit future R2, PostgreSQL/pgvector, hosted models and Python workers without frontend changes. services/api retains the earlier Python reference implementation and is not deployed.

Pipeline: validated upload -> private original -> queued extraction -> actual page text -> source-cited facts -> type-filtered candidates -> deterministic checks of every candidate -> versioned findings -> review -> report. Type matching never establishes support. Unsupported extraction, ambiguous facts and conflicts require review.

The public demonstration uses four supplied PDFs and two fictional buyer checklists transcribed from the contact sheet. Assessment date: 2026-12-26. No evaluation CSV is imported by application code. Isolated sessions prevent visitor data mixing. Reset revokes the old session and creates a new tenant. Public uploads are disabled; private uploads require a provisioned account.
