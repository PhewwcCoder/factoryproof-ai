# FactoryProof AI

Build source-grounded cross-buyer evidence reconciliation, never compliance certification.
Next.js App Router with vinext lives in apps/web; Hono/TypeScript Workers API in apps/web/server.
Cloudflare Workers, D1, private R2, and Queues are the primary deployment platform.
services/api is a Python reference implementation, not the production backend.
Python modules use absolute services.api imports. Run commands from repository root.
Persist production application data through D1. Every query must enforce session tenant.
Never make retrieval scores or LLM assertions a final verification decision.
Every extracted fact needs an exact source passage and page; missing facts stay missing.
Demo records and fictional buyer rules must remain visibly labeled synthetic.
Design tokens and patterns: docs/design/DESIGN_SYSTEM.md. Taste is the primary design skill.
Video files and production references belong exclusively in video/. Preserve their separate Git history.
Never commit secrets, runtime databases, private uploads, caches, or generated video assets.
Checks: python -m pytest tests; python -m ruff check services tests; npm --prefix apps/web run lint; npm --prefix apps/web run build.
Use conventional commits, no force push. Only publish to the user's supplied GitHub remote.
See docs/deployment.md for hosting and credentials. Never claim an unverified deployment.
Document tested behavior and pending work separately. Keep evaluations reproducible at a fixed reference date.
