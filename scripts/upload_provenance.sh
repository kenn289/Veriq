#!/usr/bin/env bash
set -euo pipefail

# Usage: upload_provenance.sh <image> <tag>
IMAGE=${1:-}
TAG=${2:-}
if [ -z "$IMAGE" ] || [ -z "$TAG" ]; then
  echo "Usage: $0 <image> <tag>" >&2
  exit 2
fi

MINIO_ENDPOINT=${MINIO_ENDPOINT:-}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-}
MINIO_BUCKET=${MINIO_BUCKET:-}
AWS_S3_BUCKET=${AWS_S3_BUCKET:-}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-}

echo "Installing mc and cosign if not present"
command -v mc >/dev/null 2>&1 || {
  curl -fsSL -o /tmp/mc https://dl.min.io/client/mc/release/linux-amd64/mc
  chmod +x /tmp/mc
  sudo mv /tmp/mc /usr/local/bin/mc
}

command -v cosign >/dev/null 2>&1 || {
  COSIGN_VERSION=$(curl -s https://api.github.com/repos/sigstore/cosign/releases/latest | jq -r .tag_name)
  curl -fsSL -o /tmp/cosign https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-linux-amd64
  chmod +x /tmp/cosign
  sudo mv /tmp/cosign /usr/local/bin/cosign
}

FULL_IMAGE="${IMAGE}:${TAG}"
echo "Verifying image: $FULL_IMAGE"
cosign verify --output-signature web.sig "$FULL_IMAGE" || true

image_id=$(docker image inspect --format='{{.Id}}' "$FULL_IMAGE") || image_id=""
git_sha=$(git rev-parse --short HEAD || echo "")
timestamp=$(date --iso-8601=seconds)

jq -n --arg image "$FULL_IMAGE" --arg image_id "$image_id" --arg git_sha "$git_sha" --arg ts "$timestamp" '{image: $image, image_id: $image_id, git_sha: $git_sha, timestamp: $ts}' > provenance.json
mc alias set myminio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4 || true
mc mb --ignore-existing myminio/${MINIO_BUCKET} || true
if [ -n "$MINIO_ENDPOINT" ] && [ -n "$MINIO_ACCESS_KEY" ] && [ -n "$MINIO_SECRET_KEY" ] && [ -n "$MINIO_BUCKET" ]; then
  mc cp web.sig myminio/${MINIO_BUCKET}/signatures/${TAG}/web.sig || true
  mc cp provenance.json myminio/${MINIO_BUCKET}/signatures/${TAG}/provenance.json || true
  echo "Verifying upload with mc stat"
  mc stat myminio/${MINIO_BUCKET}/signatures/${TAG}/provenance.json
elif [ -n "$AWS_S3_BUCKET" ] && [ -n "$AWS_DEFAULT_REGION" ]; then
  echo "Uploading to AWS S3"
  command -v aws >/dev/null 2>&1 || { echo "aws CLI required for S3 upload"; exit 4; }
  aws s3 cp web.sig s3://${AWS_S3_BUCKET}/signatures/${TAG}/web.sig || true
  aws s3 cp provenance.json s3://${AWS_S3_BUCKET}/signatures/${TAG}/provenance.json || true
  echo "Verifying upload with aws s3api head-object"
  aws s3api head-object --bucket ${AWS_S3_BUCKET} --key signatures/${TAG}/provenance.json
else
  echo "No MINIO or AWS S3 credentials provided; skipping upload"
fi

echo "Uploaded signatures and provenance for ${FULL_IMAGE} to ${MINIO_ENDPOINT}/${MINIO_BUCKET}/signatures/${TAG}/"
