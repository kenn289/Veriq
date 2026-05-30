MinIO Production Playbook
=========================

This playbook contains recommended steps to run MinIO in production for storing adapter artifacts.

1) Deployment options
- Kubernetes (recommended): use the official Helm chart and provision PVs with sufficient capacity. Configure TLS and use NodePort/ingress as appropriate.
- Managed S3-compatible storage: if available, prefer a managed provider.

2) Security
- Use TLS for all endpoints.
- Create a dedicated service account / access key pair for CI (limited permissions scoped to the artifacts bucket).
- Enable server-side encryption and consider object-lock for critical artifacts.

3) Bucket & lifecycle
- Create bucket `veriq-artifacts`.
- Apply lifecycle policy (see `backend/llm/minio_lifecycle.xml`) to expire `adapters/` objects after your retention window.

4) High-availability & backups
- Run MinIO in distributed mode across multiple nodes for HA.
- Schedule periodic backups of metadata and underlying storage snapshots.

5) CI Integration
- Store MinIO credentials as encrypted GitHub Secrets (see docs/GITHUB_SECRETS_GUIDE.md).
- Configure CI to upload adapters to `adapters/<adapter-name>/...` and let lifecycle handle cleanup.

6) Monitoring & alerts
- Monitor disk usage, request rates, and error rates. Set alerts for low disk space.

7) Example: Create user and bucket with `mc` (admin machine):

```bash
# configure alias
mc alias set admin https://minio-admin.example.com MINIO_ROOT_USER MINIO_ROOT_PASSWORD --api S3v4

# create bucket
mc mb admin/veriq-artifacts

# create a limited user for CI
mc admin user add admin ci-user ci-password
mc admin policy set admin readwrite user=ci-user

# apply lifecycle
mc ilm import admin/veriq-artifacts backend/llm/minio_lifecycle.xml
```
