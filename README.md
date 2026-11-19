# FactoryProof AI

Source-grounded cross-buyer evidence reconciliation. One record can support one buyer while failing another buyer's date or sign-off conditions.

**Synthetic Demonstration — Not an Official Compliance Assessment**

## Run locally

Requires Node 24. From `apps/web`:

```sh
npm ci
npm run db:local
npm run build
npm start
```

Open http://127.0.0.1:3000 and choose **Try with Sample Documents**. Local Workers, D1 and Queues need no model key or billing activation. `npm run dev` starts Vite.

## Product

- Isolated public trial with four actual synthetic PDFs and two fictional buyer checklists.
- Evidence vault, extracted source passages and original PDF previews.
- Queued native PDF extraction, deterministic cross-buyer constraints and explicit uncertainty.
- Buyer rule editing/versioning, human reviews, downloadable draft/reviewed reports.
- Private account login, tenant-authorized PDF/text uploads capped at 1 MB.
- Reset, expiring sessions, scheduled cleanup, rate limits and public `/docs`.

Fixed assessment date: **2026-12-26**. The April 26 fire drill fails Buyer A's six-month condition and supports Buyer B's twelve-month condition.

## Free-only architecture

Workers + vinext + Hono + D1 + Queues. Private originals use bounded D1 BLOBs. R2 is omitted because its activation allows overage billing. No paid Workers upgrade or hosted LLM call is enabled. See [deployment](docs/deployment.md) and [security](docs/security.md).

```sh
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run test:e2e
```

Tests extract real PDFs and compare all ten outcomes with an independent evaluation CSV. The original ZIP, buyer JSON and expected_results.csv were absent from the supplied folder; included rules/evaluation are explicitly labeled contact-sheet transcriptions. See [provenance](datasets/public-demo/README.md).

Scanned PDF OCR, arbitrary narrative interpretation, hosted LLM extraction and vector retrieval are future work. Current parsing recognizes sample forms and labeled fields; unresolved facts require review. Sign-off text is not signature authenticity verification.

Video production files and references are in [`video/`](video/README.md), preserving their separate Git history and existing changes.
