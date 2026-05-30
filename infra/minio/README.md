MinIO provisioning examples

This folder contains example snippets to provision MinIO in Kubernetes using Helm and Terraform.

- `helm-values.yaml` — example values for a 4-node MinIO distributed deployment with persistent storage.
- `terraform_minio.tf` — Helm + Terraform snippet showing how to install the MinIO chart (requires configured Kubernetes provider and `kubectl` access).

These are templates — customize resource sizes, storage class and secrets for production.
