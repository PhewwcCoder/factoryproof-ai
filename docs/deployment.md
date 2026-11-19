# Cloudflare Workers Free deployment

The user's final free-only constraint overrides the earlier R2 preference. No R2 subscription, paid Workers upgrade, or paid model calls are configured. `apps/web/wrangler.jsonc` declares D1, Queues, static assets and hourly cleanup.

Resources: D1 `factoryproof-mvp` (`bcc3c340-534e-4fb8-9958-93ddf3c615a7`), Queue `factoryproof-extraction`, Worker `factoryproof-ai`.

```sh
cd apps/web
npm ci
npx wrangler whoami
npm run db:remote
npm run build
npm run deploy
```

For another account, sign in using `wrangler login`, create a D1 database and queue, and update the database ID. Do not modify unrelated resources. Local migrations and preview both use `.wrangler/state`; the start script sets this explicitly.

The demo requires no application secrets. CI deployment needs `CLOUDFLARE_ACCOUNT_ID` and a scoped `CLOUDFLARE_API_TOKEN` in GitHub secrets. The supplied CI validates source and builds; it does not automatically deploy. Never commit credentials.

Private accounts: from `apps/web`, set `FACTORYPROOF_PASSWORD` locally and run `node scripts/provision-user.mjs email tenant-name role`. This provisions locally by default; append `--remote` for production. The password is salted/hashed, never printed, and temporary SQL is removed.

After deployment, set `BASE_URL` to the emitted HTTPS URL and run `npm run test:e2e`. This tests the real unauthenticated browser journey, every golden outcome, PDFs, downloads, tenant isolation, CSRF denial and reset. CLI upload success alone is not deployment verification.

Private D1 originals are limited to 1 MB, below D1's 2 MB row limit. The app caps new demo tenants at 100/day, expires them after 24 hours, and cleans hourly. Free platform quotas must cause an error rather than trigger a paid upgrade. Do not activate billing to work around quotas without a new user instruction.

References: [vinext Workers](https://vinext.dev/docs/deploying/cloudflare), [D1 limits](https://developers.cloudflare.com/d1/platform/limits/), [Queues free allowance](https://developers.cloudflare.com/queues/platform/pricing/), [R2 activation](https://developers.cloudflare.com/r2/get-started/).
