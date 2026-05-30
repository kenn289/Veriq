output "release_name" {
  value = helm_release.minio.name
}

output "namespace" {
  value = helm_release.minio.namespace
}
