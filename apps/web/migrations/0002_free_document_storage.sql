-- Free-only MVP: bounded private originals without an R2 billing subscription.
CREATE TABLE IF NOT EXISTS document_blobs (
 tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
 document_id TEXT NOT NULL, content BLOB NOT NULL CHECK(length(content)<=1048576),
 PRIMARY KEY(tenant_id,document_id)
);
