# Example Terraform snippet to deploy MinIO using the Helm provider.
# This is a minimal example and requires a configured Kubernetes provider.

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

resource "helm_release" "minio" {
  name       = "minio"
  repository = "https://operator.min.io/"
  chart      = "minio"
  version    = "8.2.0"

  values = [file("${path.module}/helm-values.yaml")]
}

variable "kubeconfig_path" {
  type = string
  description = "Path to kubeconfig used to deploy the chart"
}
