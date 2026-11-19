# Architecture and implementation plan

FactoryProof separates interpretation, candidate retrieval, deterministic constraints and human review.

The browser uses Next.js App Router and a same-origin /api reverse proxy. FastAPI authorizes an opaque, hashed, expiring session before every tenant-scoped operation. SQLAlchemy supports local SQLite and deployed PostgreSQL. Private files live outside the web root; an optional S3-compatible adapter supports R2. The local deployment is self-contained and requires no model API key.

Pipeline: validated PDF/text upload -> persisted processing state -> page-aware native extraction -> grounded structured facts -> lexical and latent-semantic retrieval -> deterministic checks -> versioned findings -> reviewer decisions -> preparation report. Unknown or ambiguous facts produce review outcomes. Scanned PDFs require OCR and are visibly flagged rather than silently treated as empty evidence.

Build order: (1) rules, data and API; (2) end-to-end workflows; (3) shared visual system and screens; (4) evaluation, browser QA and deployment preparation. PostgreSQL migrations and container deployment must use the same domain logic as the local demo.

Reference date is 2026-11-01 for synthetic demonstrations. The fire drill is dated 2026-03-01. Buyers Northstar Apparel (6 months) and Loom & Field (12 months) are fictional. Human review records decisions without overwriting deterministic results.
