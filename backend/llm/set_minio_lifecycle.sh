#!/usr/bin/env bash
set -euo pipefail
# Apply lifecycle policy to a MinIO bucket using the mc (MinIO Client) tool.
# Requires: mc installed and accessible in PATH, and MINIO_ENDPOINT/MINIO_ACCESS_KEY/MINIO_SECRET_KEY env vars.

MC_ALIAS=${MC_ALIAS:-minio}
BUCKET=${BUCKET:-veriq-artifacts}
LIFECYCLE_FILE="$(dirname "$0")/minio_lifecycle.xml"

if ! command -v mc >/dev/null 2>&1; then
  echo "mc (MinIO Client) not found in PATH. Install from https://min.io/docs/minio/linux/reference/minio-mc.html"
  exit 1
fi

if [ -z "${MINIO_ENDPOINT:-}" ] || [ -z "${MINIO_ACCESS_KEY:-}" ] || [ -z "${MINIO_SECRET_KEY:-}" ]; then
  echo "Please set MINIO_ENDPOINT, MINIO_ACCESS_KEY and MINIO_SECRET_KEY environment variables."
  exit 1
fi

echo "Setting mc alias $MC_ALIAS -> $MINIO_ENDPOINT"
mc alias set "$MC_ALIAS" "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4 || true

echo "Importing lifecycle config to $MC_ALIAS/$BUCKET from $LIFECYCLE_FILE"
mc ilm import "$MC_ALIAS/$BUCKET" "$LIFECYCLE_FILE"

echo "Lifecycle policy applied."
