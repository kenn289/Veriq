// RBAC, ServiceAccount and PVC scaffolding for MinIO module
resource "kubernetes_service_account" "minio_sa" {
  metadata {
    name      = "minio-ci-sa"
    namespace = var.namespace
  }
}

resource "kubernetes_role" "minio_role" {
  metadata {
    name      = "minio-ci-role"
    namespace = var.namespace
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/log", "services", "endpoints", "persistentvolumeclaims"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding" "minio_rb" {
  metadata {
    name      = "minio-ci-rb"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.minio_role.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.minio_sa.metadata[0].name
    namespace = var.namespace
  }
}

resource "kubernetes_persistent_volume_claim" "minio_pvc" {
  metadata {
    name      = "minio-pvc"
    namespace = var.namespace
  }

  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.persistence_size
      }
    }
    storage_class_name = var.storage_class
  }
}
