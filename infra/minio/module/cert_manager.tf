// Cert-Manager scaffolding (requires cert-manager installed in cluster)
// This creates a ClusterIssuer (selfsigned) and a sample Certificate resource
// Customize for your chosen Issuer (ACME/Let's Encrypt or CA).

resource "kubernetes_manifest" "cert_manager_selfsigned" {
  count = var.acme_enabled ? 0 : 1
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "ClusterIssuer"
    "metadata" = {
      "name" = "minio-selfsigned-issuer"
    }
    "spec" = {
      "selfSigned" = {}
    }
  }
}

resource "kubernetes_manifest" "minio_certificate" {
  count = var.acme_enabled ? 0 : 1
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "Certificate"
    "metadata" = {
      "name"      = "minio-cert"
      "namespace" = var.namespace
    }
    "spec" = {
      "dnsNames" = ["minio.example.com"]
      "secretName" = "minio-tls"
      "issuerRef" = {
        "name" = "minio-selfsigned-issuer"
        "kind" = "ClusterIssuer"
      }
    }
  }
}

# Optional ACME/Let's Encrypt ClusterIssuer (created when acme_enabled = true)
resource "kubernetes_manifest" "cert_manager_acme_issuer" {
  count = var.acme_enabled ? 1 : 0
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "ClusterIssuer"
    "metadata" = {
      "name" = "minio-acme-issuer"
    }
    "spec" = {
      "acme" = {
        "email" = var.acme_email
        "server" = var.acme_server
        "privateKeySecretRef" = { "name" = "minio-acme-account-key" }
        # If an ACME DNS provider is provided, configure DNS-01 solver; otherwise default to HTTP-01
        "solvers" = (
          var.acme_dns_provider != "" ? [
            # Generic DNS-01 solver; provider specific config must be supplied via the referenced secret
            { "dns01" = { var.acme_dns_provider = { "secretName" = var.acme_dns_secret, "secretNamespace" = var.acme_dns_secret_namespace } } }
          ] : [
            { "http01" = { "ingress" = { "class" = "nginx" } } }
          ]
        )
      }
    }
  }
}

resource "kubernetes_manifest" "minio_certificate_acme" {
  count = var.acme_enabled ? 1 : 0
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "Certificate"
    "metadata" = {
      "name"      = "minio-cert"
      "namespace" = var.namespace
    }
    "spec" = {
      "dnsNames" = ["minio.example.com"]
      "secretName" = "minio-tls"
      "issuerRef" = {
        "name" = "minio-acme-issuer"
        "kind" = "ClusterIssuer"
      }
    }
  }
}

# Optionally create a Kubernetes secret for Cloudflare API token when user provided token and no secret name specified
resource "kubernetes_secret" "acme_cloudflare_secret" {
  count = var.acme_enabled && var.acme_dns_provider == "cloudflare" && var.acme_dns_secret == "" && var.cloudflare_api_token != "" ? 1 : 0

  metadata {
    name      = "cloudflare-api-token"
    namespace = var.acme_dns_secret_namespace != "" ? var.acme_dns_secret_namespace : var.namespace
  }

  string_data = {
    "api-token" = var.cloudflare_api_token
  }

  type = "Opaque"
}

# Optionally create a Kubernetes secret for AWS credentials (Route53) when user provided keys and no secret name specified
resource "kubernetes_secret" "acme_route53_secret" {
  count = var.acme_enabled && var.acme_dns_provider == "route53" && var.acme_dns_secret == "" && (var.aws_access_key_id != "" && var.aws_secret_access_key != "") ? 1 : 0

  metadata {
    name      = "route53-credentials"
    namespace = var.acme_dns_secret_namespace != "" ? var.acme_dns_secret_namespace : "cert-manager"
  }

  string_data = {
    "aws_access_key_id"     = var.aws_access_key_id
    "aws_secret_access_key" = var.aws_secret_access_key
  }

  type = "Opaque"
}
