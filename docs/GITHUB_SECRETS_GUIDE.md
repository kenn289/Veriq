GitHub Secrets Guide for MinIO CI integration
=============================================

This repository's CI expects the following secrets to be added in GitHub (Repository Settings -> Secrets & variables -> Actions):

- `MINIO_ENDPOINT` — e.g. `http://minio.example.com:9000` (include scheme)
- `MINIO_ACCESS_KEY` — CI user access key
- `MINIO_SECRET_KEY` — CI user secret key
- `MINIO_BUCKET` — optional, default `veriq-artifacts`

To add a secret via CLI (gh CLI):

```bash
gh secret set MINIO_ENDPOINT --body "http://minio.example.com:9000"
gh secret set MINIO_ACCESS_KEY --body "ci-access-key"
gh secret set MINIO_SECRET_KEY --body "ci-secret"
gh secret set MINIO_BUCKET --body "veriq-artifacts"
```

CI usage
- The workflow `.github/workflows/llm-smoke-test.yml` will only run the MinIO upload step when these secrets are present. The upload step runs `backend/llm/ci_upload_adapter.py`.
