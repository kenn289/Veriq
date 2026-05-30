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
