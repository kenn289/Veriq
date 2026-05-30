MinIO lifecycle policy (server-side)
===================================

This file shows how to configure a server-side lifecycle policy in MinIO to automatically remove old adapter artifacts (recommended over client-side deletions).

Apply using the MinIO Client (`mc`):

1. Install `mc`:

   - macOS / Linux: follow https://min.io/docs/minio/linux/reference/minio-mc.html

2. Export credentials and alias (example):

```bash
export MINIO_ENDPOINT=http://minio.local:9000
export MINIO_ACCESS_KEY=veriq
export MINIO_SECRET_KEY=veriqsecret
export BUCKET=veriq-artifacts
```

3. Apply lifecycle configuration:

```bash
# set alias (one-time)
mc alias set minio $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY --api S3v4

# import the included lifecycle XML which expires objects under adapters/ after 30 days
mc ilm import minio/$BUCKET backend/llm/minio_lifecycle.xml
```

Alternatively, use the MinIO Console (web UI) -> Buckets -> Lifecycle to paste the XML.

Notes
- The provided XML targets key prefix `adapters/` and expires objects after 30 days. Adjust `Days` as needed.
- Server-side lifecycle is preferred because it avoids relying on CI clients to delete objects and is more robust.
