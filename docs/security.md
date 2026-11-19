# Security and cost boundaries

- Original documents are private D1 BLOBs queried by session tenant and document ID. Public static assets contain only four supplied synthetic PDFs.
- Sessions use random opaque tokens hashed in D1, HttpOnly/SameSite=Strict cookies, Secure on HTTPS, and 24-hour expiry. Reset/logout revoke sessions. Mutation requests require exact same-origin Origin headers.
- Public demo uploads are disabled. Private accounts are administrator-provisioned. Role checks protect writes and reviews.
- Uploads validate type, PDF magic, size and page count. Unknown types, missing facts, invalid dates, conflicts and ungrounded passages require review. Document instructions are data, never application instructions.
- No model API is invoked. D1 rate counters limit login, comparisons, tenant creation, reset and reprocessing. A global daily demo cap bounds trial consumption. Deployment scripts do not activate paid plans.
- Infrastructure failures return generic client errors. Source text and credentials are not logged. Runtime files, local secrets and browser traces are Git-ignored.

Limitations: native-text extraction only, no signature authenticity verification, no identity federation or public registration. Review approval confirms a finding without altering its deterministic outcome. Operators manage private-account retention/access; D1 backups retain data according to provider retention.
