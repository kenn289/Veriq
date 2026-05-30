Terraform MinIO module

This folder contains a minimal Terraform module scaffold that installs the MinIO Helm chart.

Usage (example):

```hcl
module "minio" {
  source = "./infra/minio/module"
  kubeconfig_path = var.kubeconfig_path
  replica_count = 4
  persistence_size = "200Gi"
}
```

Customize the `values` in `main.tf` as needed for your environment.

TLS / cert-manager
------------------

This module includes optional cert-manager scaffolding.

- To use a self-signed `ClusterIssuer` (default), do nothing; the module will create a self-signed issuer and a `Certificate` for `minio.example.com`.
- To enable ACME (Let's Encrypt) HTTP-01 issuance, set `acme_enabled = true` and provide `acme_email`. Example:

```hcl
module "minio" {
  source = "./infra/minio/module"
  kubeconfig_path = var.kubeconfig_path
  acme_enabled = true
  acme_email = "ops@example.com"
}
```

Notes:
- The ACME issuer scaffold uses an HTTP-01 solver with an ingress class of `nginx`. For production DNS-01 challenge support, replace the `solvers` block with your DNS provider configuration and provide any required secrets.
- You must provision DNS records for `minio.example.com` and ensure ingress exposes the challenge endpoint.
- The `minio-production` GitHub Environment is expected by the deploy workflow for protected `terraform apply` steps; configure environment reviewers in the repository settings.

DNS-01 (recommended for production)
-----------------------------------

To use DNS-01 challenges (recommended for production), set `acme_enabled = true` and configure `acme_dns_provider` plus a secret containing provider credentials. The module's `terraform.tfvars.example` shows a Cloudflare example. The module will create an ACME `ClusterIssuer` using DNS-01 when `acme_dns_provider` is non-empty.

Provider-specific notes:
- Cloudflare: create an API token with DNS edit permissions and store it in a Kubernetes secret (name matches `acme_dns_secret`).
- Route53: prefer IAM roles or store AWS credentials in a secret referenced by `acme_dns_secret`.

Automatic secret creation
-------------------------

If you prefer Terraform to create the provider secret for you, set the credentials variables in your `terraform.tfvars` (e.g. `cloudflare_api_token` or `aws_access_key_id`/`aws_secret_access_key`) and leave `acme_dns_secret` empty. The module will create the appropriate Kubernetes `Secret` in the target namespace with a sensible default name (`cloudflare-api-token` or `route53-credentials`). For production, consider managing secrets via a dedicated secret management workflow.

See `terraform.tfvars.example` in this folder for a starting point.
