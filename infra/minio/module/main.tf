terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.8"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

resource "helm_release" "minio" {
  name       = var.release_name
  repository = "https://operator.min.io/"
  chart      = "minio"
  version    = var.chart_version

  values = [yamlencode({
    replicaCount = var.replica_count
    persistence = {
      enabled = true
      size    = var.persistence_size
    }
    resources = var.resources
    # expose service and ingress scaffolding
    service = {
      type = var.service_type
    }
    ingress = {
      enabled = var.ingress_enabled
    }
  })]
}
