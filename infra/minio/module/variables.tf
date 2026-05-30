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

variable "acme_enabled" {
  type    = bool
  default = false
}

variable "acme_email" {
  type    = string
  default = ""
}

variable "acme_server" {
  type    = string
  default = "https://acme-v02.api.letsencrypt.org/directory"
}

variable "acme_dns_provider" {
  type    = string
  default = ""
}

variable "acme_dns_secret" {
  type    = string
  default = ""
}

variable "acme_dns_secret_namespace" {
  type    = string
  default = ""
}

variable "acme_dns_zone" {
  type    = string
  default = ""
}

variable "cloudflare_api_token" {
  type    = string
  default = ""
  sensitive = true
}

variable "aws_access_key_id" {
  type    = string
  default = ""
  sensitive = true
}

variable "aws_secret_access_key" {
  type    = string
  default = ""
  sensitive = true
}

variable "storage_class" {
  type    = string
  default = ""
}
