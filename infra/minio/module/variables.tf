variable "kubeconfig_path" {
  type = string
}

variable "release_name" {
  type    = string
  default = "minio"
}

variable "chart_version" {
  type    = string
  default = "8.2.0"
}

variable "replica_count" {
  type    = number
  default = 4
}

variable "persistence_size" {
  type    = string
  default = "200Gi"
}

variable "resources" {
  type = any
  default = {
    requests = { cpu = "2000m", memory = "8Gi" }
    limits   = { cpu = "4000m", memory = "16Gi" }
  }
}

variable "namespace" {
  type    = string
  default = "minio"
}

variable "service_type" {
  type    = string
  default = "ClusterIP"
}

variable "ingress_enabled" {
  type    = bool
  default = false
}

variable "storage_class" {
  type    = string
  default = ""
}
