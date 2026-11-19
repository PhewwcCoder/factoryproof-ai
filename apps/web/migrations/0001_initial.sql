CREATE TABLE IF NOT EXISTS tenants (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, demo INTEGER NOT NULL DEFAULT 0, expires_at INTEGER
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
 role TEXT NOT NULL, user_name TEXT NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
 email TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id),
 password_hash TEXT NOT NULL, salt TEXT NOT NULL, role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS records (
 id TEXT NOT NULL, tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
 kind TEXT NOT NULL, payload TEXT NOT NULL CHECK(json_valid(payload)),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
 PRIMARY KEY(tenant_id,id)
);
CREATE INDEX records_by_tenant_kind ON records(tenant_id,kind,created_at);
CREATE INDEX sessions_expiry ON sessions(expires_at);
CREATE TABLE IF NOT EXISTS rate_limits (key TEXT PRIMARY KEY, count INTEGER NOT NULL, expires_at INTEGER NOT NULL);
